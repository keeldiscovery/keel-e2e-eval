"""The FounderAgent driver (T010): a deterministic v2 loop over /v2/agent/** -- get_next, branch
on kind, get_context for granted handles only, submit with the token -- consulting only the
scenario's payload builders. No LLM anywhere.

**Judgement call -- the real choreography vs. the plan's**: plan.md's S-001 script describes
frame -> roles -> assumptions -> REVIEW -> approve, repeated for all three stages, and only then
one INVITE/participant/INTERPRET round. Reading `NextRecommendation.compute` (keel-cloud) shows
this is not what the server actually does:

1. `get_next`'s very first loop frames *every* stage as a draft, one FRAME per call, before it
   ever consults `currentFocus()` -- so PROBLEM, SOLUTION and COMMERCIAL all get their first
   words before anything else happens.
2. `currentFocus()` then always returns the *earliest* stage (PROBLEM first) that still has any
   unmet need. Once PROBLEM is framed+approved with an open, uninvited load-bearing assumption,
   `needs(PROBLEM)` is `INVITE` -- and that is a "present need", so `currentFocus()` picks PROBLEM
   again, `INVITE`-handoff and all, *before SOLUTION or COMMERCIAL ever get roles or assumptions*.

So the real per-stage cycle is: frame (all three, up front) -> roles (once, project-wide, at
PROBLEM's first REVIEW cycle) -> assumptions(stage) -> REVIEW(stage) -> approve -> INVITE(stage)
-> participant answers -> WAITING resolves -> INTERPRET(stage) -- and that whole
assumptions..interpret cycle repeats three times, once per stage, interleaved rather than
batched. `evals/test_s001_smoke.py` drives this real sequence, not the plan's batched one, and
this docstring is the record of that correction (see the delivery report's finding A1).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

import requests

from harness.steps import Recorder


class ProtocolError(RuntimeError):
    """A submit_action/get_context/get_next call was refused: the flat {rule, problem, remedy}
    triple every v2 refusal carries (AgentDtos.ErrorBody), plus the HTTP status."""

    def __init__(self, status: int, body: Any):
        self.status = status
        self.body = body
        self.rule = body.get("rule") if isinstance(body, dict) else None
        self.problem = body.get("problem") if isinstance(body, dict) else None
        self.remedy = body.get("remedy") if isinstance(body, dict) else None
        super().__init__(f"HTTP {status} rule={self.rule}: {self.problem}")


class PayloadBuilder(Protocol):
    """What a Scenario must provide the driver -- consulted, never generated (FR-003)."""

    def build_payload(self, action: str, detail: dict, context: dict[str, Any]) -> dict:
        ...


def _safe_json(response: requests.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return response.text


class FounderAgentDriver:
    """Drives the agent's half of a discovery: create, frame, roles, assumptions, interpret,
    proceed-to-brief. REVIEW/INVITE/WAITING handoffs are returned to the caller untouched --
    FR-004 forbids this driver from shortcutting a handoff on the wire; a real party (the founder
    browser, or the participant) has to act.
    """

    def __init__(self, base_url: str, recorder: Recorder, scenario: PayloadBuilder,
                 session: requests.Session | None = None):
        self.base_url = base_url.rstrip("/")
        self.recorder = recorder
        self.scenario = scenario
        self.session = session or requests.Session()
        self.project_id: str | None = None

    # ------------------------------------------------------------------------------- SKILL.md

    def load_skill(self, skill_md_path: Path) -> str:
        """Loads SKILL.md from the keel-skill checkout, per design §3 ("loads SKILL.md and runs
        the loop"). Treated as **opaque documentation, surfaced in the report** -- never parsed
        for wire behavior: keel-skill's SKILL.md is being rewritten to v2 by a parallel effort,
        so depending on its literal text here would make this driver's behavior a moving target.
        Everything this driver actually does on the wire comes from the scenario's deterministic
        payload builders (FR-003); this step exists so a reviewer can see, in the transcript,
        exactly which SKILL.md text this run was driven alongside.
        """
        with self.recorder.step(f"load SKILL.md from {skill_md_path}", party="agent",
                                 kind="note") as h:
            if not skill_md_path.exists():
                h.fail(f"no SKILL.md at {skill_md_path}")
                raise FileNotFoundError(
                    f"keel-skill checkout has no SKILL.md at {skill_md_path}")
            text = skill_md_path.read_text()
            first_line = text.splitlines()[0] if text else ""
            h.record_wire({"path": str(skill_md_path)},
                           {"bytes": len(text), "first_line": first_line})
        return text

    # --------------------------------------------------------------------------- wire primitives

    def _post(self, path: str, body: Any, step_name: str) -> Any:
        with self.recorder.step(step_name, party="agent", kind="protocol") as h:
            response = self.session.post(f"{self.base_url}{path}", json=body, timeout=15)
            parsed = _safe_json(response)
            h.record_wire({"path": path, "body": body}, {"status": response.status_code, "body": parsed})
            if response.status_code >= 400:
                h.fail(f"HTTP {response.status_code}: {parsed}")
                raise ProtocolError(response.status_code, parsed)
        return parsed

    def get_next(self) -> dict:
        if self.project_id is None:
            return self._post("/v2/agent/next", None, "get_next (before any project)")
        return self._post(f"/v2/agent/projects/{self.project_id}/next", None,
                           f"get_next (project {self.project_id})")

    def get_context(self, token: str, handle: str) -> Any:
        return self._post("/v2/agent/context", {"token": token, "handle": handle},
                           f"get_context({handle})")

    def check_mcp_reachable(self) -> None:
        """One /mcp reachability touch even though this driver speaks HTTP (design §3)."""
        with self.recorder.step("check /mcp is reachable", party="agent", kind="protocol") as h:
            response = self.session.post(f"{self.base_url}/mcp", json={}, timeout=10)
            h.record_wire({"path": "/mcp"}, {"status": response.status_code})
            if response.status_code == 404:
                h.fail("/mcp answered 404 -- the MCP endpoint is not mounted")
                raise RuntimeError("/mcp is not mounted")

    # ------------------------------------------------------------------------------ submit + retry

    def _submit(self, token: str, payload: dict, label: str) -> dict:
        return self._post("/v2/agent/submit", {"token": token, "payload": payload}, f"submit {label}")

    def submit_with_recovery(self, token: str, payload: dict, action: str, label: str) -> dict:
        """Refusal recovery per {rule, problem, remedy} (T010):

        - `token`/`concurrency` -- the token (or the revision it names) is stale. Nothing was
          written, so the fix is mechanical: call get_next again for a fresh token bound to the
          project's current revision, and resubmit the *same* semantic payload (the "facts
          store" -- this driver is deterministic, so re-deriving that payload from the scenario
          again is exactly reusing the facts already decided, not generating a new answer).
        - `schema` -- the payload's shape was wrong. The remedy is to correct and resubmit
          *against the same token* (a schema violation never touches the aggregate, so the token
          is still good). `Scenario.fix_schema`, if provided, gets one chance to correct it;
          otherwise this re-raises, because a schema violation from a deterministic builder is a
          driver bug, not a runtime condition to paper over.
        """
        try:
            result = self._submit(token, payload, label)
        except ProtocolError as err:
            if err.rule in ("token", "concurrency"):
                fresh = self.get_next()
                if fresh.get("kind") != "action" or fresh.get("action") != action:
                    raise RuntimeError(
                        f"expected a fresh '{action}' token after a {err.rule} refusal, got {fresh}"
                    ) from err
                result = self._submit(fresh["token"], payload, f"{label} [retried after {err.rule}]")
            elif err.rule == "schema" and hasattr(self.scenario, "fix_schema"):
                fixed = self.scenario.fix_schema(action, payload, err.problem)  # type: ignore[attr-defined]
                result = self._submit(token, fixed, f"{label} [schema-corrected]")
            else:
                raise
        self.project_id = result["projectId"]
        return result

    # ------------------------------------------------------------------------------------- loop

    def advance_one(self) -> dict:
        """One get_next, and -- only if it recommends an action -- the context reads and submit
        needed to run it. Returns the raw NextResponse either way, so the caller can branch on
        `kind` (a handoff is returned untouched, for a real party to execute).
        """
        response = self.get_next()
        if response.get("kind") != "action":
            return response

        action = response["action"]
        token = response["token"]
        detail = response.get("detail") or {}
        context: dict[str, Any] = {}
        for handle in response.get("context") or []:
            context[handle] = self.get_context(token, handle)

        payload = self.scenario.build_payload(action, detail, context)
        self.submit_with_recovery(token, payload, action, action)
        return response

    def advance_until_handoff(self) -> dict | None:
        """Runs agent actions until a handoff is recommended, or PROCEED_TO_BRIEF is submitted
        (the natural end of this driver's role -- get_next is illegal once the project is
        terminal, so this stops rather than calling it again).
        """
        while True:
            response = self.advance_one()
            if response.get("kind") == "handoff":
                return response
            if response.get("action") == "PROCEED_TO_BRIEF":
                return None
