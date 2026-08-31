"""The relay wire client (design §12 item 1; keel-cloud commit 6f1c175, spec 016 + design §14):
`FounderRelay` speaks the session-gated founder endpoints (`/v2/projects/{id}/relay[...]`),
`AgentRelay` speaks the key-gated, long-polling agent endpoint (`/v2/agent/relay`) -- both riding
whatever `requests.Session` the caller already holds (a `FounderAgentDriver`'s session already
carries the agent key header and, once `log_in` runs, the founder session cookie too -- the same
one session this module's two classes are handed).

**Wire contract, confirmed live against keel-cloud's own source and acceptance tests (not
assumed)**: the lease travels as an ordinary query parameter, `lease`, on both the agent's GET and
POST -- never a header -- and is minted/returned in the JSON body field `leaseToken`. A refused
lease is a `422` with the flat `{rule, problem, remedy}` triple every v2 refusal carries
(`rule == "relay-lease"`), the same shape `harness.driver.ProtocolError` already models -- reused
here as `RelayError` rather than a second, near-identical exception type.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from harness.steps import Recorder


class RelayError(RuntimeError):
    """A founder or agent relay call was refused -- the flat {rule, problem, remedy} triple."""

    def __init__(self, status: int, body: Any):
        self.status = status
        self.body = body
        self.rule = body.get("rule") if isinstance(body, dict) else None
        self.problem = body.get("problem") if isinstance(body, dict) else None
        self.remedy = body.get("remedy") if isinstance(body, dict) else None
        super().__init__(f"HTTP {status} rule={self.rule}: {self.problem}")


def _safe_json(response: requests.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return response.text


@dataclass
class RelayTurn:
    seq: int
    author: str  # "founder" | "agent"
    kind: str  # "message" | "playback"
    text: str
    payload: Any
    at: str | None


def _turn_from_dto(d: dict) -> RelayTurn:
    return RelayTurn(seq=d["seq"], author=d["author"], kind=d["kind"], text=d.get("text") or "",
                      payload=d.get("payload"), at=d.get("at"))


class FounderRelay:
    """The founder half: session-gated (cookie auth) -- post, read-since-cursor, presence."""

    def __init__(self, base_url: str, session: requests.Session, project_id: str, recorder: Recorder):
        self.base_url = base_url.rstrip("/")
        self.session = session
        self.project_id = project_id
        self.recorder = recorder

    def post_turn(self, text: str) -> RelayTurn:
        path = f"/v2/projects/{self.project_id}/relay"
        with self.recorder.step(f"founder posts a relay turn: {text[:60]!r}", party="founder",
                                 kind="protocol") as h:
            h.capture_text("founder_turn", text)
            response = self.session.post(f"{self.base_url}{path}", json={"text": text}, timeout=15)
            parsed = _safe_json(response)
            h.record_wire({"path": path, "body": {"text": text}},
                           {"status": response.status_code, "body": parsed})
            if response.status_code >= 400:
                h.fail(f"HTTP {response.status_code}: {parsed}")
                raise RelayError(response.status_code, parsed)
        return _turn_from_dto(parsed)

    def read_turns(self, cursor: int = 0) -> list[RelayTurn]:
        path = f"/v2/projects/{self.project_id}/relay"
        with self.recorder.step(f"founder reads relay turns since cursor {cursor}", party="founder",
                                 kind="protocol") as h:
            response = self.session.get(f"{self.base_url}{path}", params={"cursor": cursor}, timeout=15)
            parsed = _safe_json(response)
            h.record_wire({"path": path, "params": {"cursor": cursor}},
                           {"status": response.status_code, "body": parsed})
            if response.status_code >= 400:
                h.fail(f"HTTP {response.status_code}: {parsed}")
                raise RelayError(response.status_code, parsed)
        return [_turn_from_dto(t) for t in (parsed.get("turns") or [])]

    def presence(self) -> dict:
        """`{connected, lastPollAt?}` -- `lastPollAt` is an absent key (never `null`) before any
        agent has ever polled this project."""
        path = f"/v2/projects/{self.project_id}/relay/presence"
        with self.recorder.step("founder reads relay presence", party="founder", kind="protocol") as h:
            response = self.session.get(f"{self.base_url}{path}", timeout=15)
            parsed = _safe_json(response)
            h.record_wire({"path": path}, {"status": response.status_code, "body": parsed})
            if response.status_code >= 400:
                h.fail(f"HTTP {response.status_code}: {parsed}")
                raise RelayError(response.status_code, parsed)
        return parsed


class AgentRelay:
    """The agent half: key-gated (the session's own `X-Keel-Agent-Key` header, set once by
    whoever constructed this session -- see `harness.driver.FounderAgentDriver.__init__`), long-
    poll + post, with the lease's own query-param/body-field discipline (module docstring).
    Mechanical: `poll`/`post_turns` spend no model tokens themselves -- `harness.bridge.BridgeLoop`
    is the one thing that decides when to wake a reasoning callable, per design §8's "the poll is
    mechanical -- a hard rule".
    """

    def __init__(self, base_url: str, session: requests.Session, project_id: str, recorder: Recorder,
                 *, poll_window_s: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.session = session
        self.project_id = project_id
        self.recorder = recorder
        self.poll_window_s = poll_window_s
        self.lease: str | None = None
        # Convenience for a caller that drives this relay directly rather than through
        # `harness.bridge.BridgeLoop` (which tracks its own cursor): `poll()` defaults to this and
        # always advances it, so `agent_relay.poll()` alone is a legal, stateful long-poll cycle.
        self.cursor: int = 0

    def _params(self, **extra: Any) -> dict[str, Any]:
        params = {"projectId": self.project_id, **extra}
        if self.lease:
            params["lease"] = self.lease
        return params

    def poll(self, cursor: int | None = None) -> tuple[list[RelayTurn], int]:
        """One long-poll call (parks up to keel-cloud's own `poll-window`, default 25s -- this
        client's own `poll_window_s` request timeout must stay comfortably above that). A clean,
        empty 200 (nothing new before the window elapsed) is not an error -- returns `([], cursor)`
        unchanged, ready for the caller to re-poll immediately, exactly like a real host's
        mechanical loop would (design §8). `cursor` defaults to `self.cursor` (updated after every
        call) for a caller driving this relay directly; `harness.bridge.BridgeLoop` tracks its own
        cursor and always passes it explicitly."""
        if cursor is None:
            cursor = self.cursor
        with self.recorder.step(f"agent long-polls the relay (cursor {cursor})", party="agent",
                                 kind="protocol") as h:
            response = self.session.get(f"{self.base_url}/v2/agent/relay",
                                         params=self._params(cursor=cursor), timeout=self.poll_window_s + 5)
            parsed = _safe_json(response)
            h.record_wire({"path": "/v2/agent/relay", "params": self._params(cursor=cursor)},
                           {"status": response.status_code, "body": parsed})
            if response.status_code >= 400:
                h.fail(f"HTTP {response.status_code}: {parsed}")
                raise RelayError(response.status_code, parsed)
            self.lease = parsed.get("leaseToken") or self.lease
        turns = [_turn_from_dto(t) for t in (parsed.get("turns") or [])]
        new_cursor = max([t.seq for t in turns], default=cursor)
        self.cursor = new_cursor
        return turns, new_cursor

    def post_turns(self, turns: list[dict]) -> list[RelayTurn]:
        """`turns`: `[{"kind": "message"|"playback", "text": ..., "payload": ... (playback only)}]`
        -- a `message` turn carrying a `payload` is refused by the domain (`RelayTurn`'s own
        compact constructor), so this never sets `payload` on a message turn."""
        with self.recorder.step(f"agent posts {len(turns)} relay turn(s)", party="agent",
                                 kind="protocol") as h:
            for t in turns:
                h.capture_text("agent_turn", t.get("text") or "")
            response = self.session.post(f"{self.base_url}/v2/agent/relay",
                                          params=self._params(), json={"turns": turns}, timeout=15)
            parsed = _safe_json(response)
            h.record_wire({"path": "/v2/agent/relay", "params": self._params(), "body": {"turns": turns}},
                           {"status": response.status_code, "body": parsed})
            if response.status_code >= 400:
                h.fail(f"HTTP {response.status_code}: {parsed}")
                raise RelayError(response.status_code, parsed)
            self.lease = parsed.get("leaseToken") or self.lease
        return [_turn_from_dto(t) for t in (parsed.get("turns") or [])]
