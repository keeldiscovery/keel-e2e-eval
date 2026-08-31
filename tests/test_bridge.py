"""Stackless unit tests for harness/bridge.py (design §12 item 1) -- `BridgeLoop` driven against a
scripted fake `AgentRelay` (no live stack), proving the mechanical/reasoning boundary keel-skill's
own SKILL.md teaches (M15: "the relay's poll is the host's own mechanical loop, never something
your reasoning drives... wakes your reasoning only once a founder turn has actually arrived") and
the lease-refusal contract (stop, never contend).
"""

from __future__ import annotations

import pytest

from harness.bridge import BridgeLoop, BridgeReply, LeaseRefused
from harness.relay import RelayError, RelayTurn


class _ScriptedAgentRelay:
    """A minimal `AgentRelay` double: `polls` is consumed one `(turns, error)` pair per `poll()`
    call; `posted` records every `post_turns` call verbatim."""

    def __init__(self, polls: list[tuple[list[RelayTurn], Exception | None]]):
        self._polls = list(polls)
        self.posted: list[list[dict]] = []

    def poll(self, cursor: int):
        turns, error = self._polls.pop(0)
        if error is not None:
            raise error
        new_cursor = max([t.seq for t in turns], default=cursor)
        return turns, new_cursor

    def post_turns(self, turns: list[dict]):
        self.posted.append(turns)
        return []


def _turn(seq: int, text: str, author: str = "founder") -> RelayTurn:
    return RelayTurn(seq=seq, author=author, kind="message", text=text, payload=None, at=None)


def test_reasoning_wakes_once_per_founder_turn_never_on_an_empty_poll():
    relay = _ScriptedAgentRelay([([], None), ([_turn(1, "hello")], None), ([], None)])
    calls: list[str] = []

    def reasoning(text: str) -> BridgeReply:
        calls.append(text)
        return BridgeReply(text=f"reply to {text}")

    loop = BridgeLoop(relay, reasoning)
    loop.step()  # empty poll -- no reasoning call, no model tokens spent (design §8's hard rule)
    assert calls == []
    loop.step()  # exactly one founder turn -- exactly one reasoning call
    assert calls == ["hello"]
    assert relay.posted == [[{"kind": "message", "text": "reply to hello"}]]
    loop.step()  # empty again -- no further reasoning call
    assert calls == ["hello"]


def test_a_non_founder_turn_in_the_same_poll_is_never_reacted_to():
    relay = _ScriptedAgentRelay([([_turn(1, "echo", author="agent"), _turn(2, "hi", author="founder")], None)])
    calls: list[str] = []
    loop = BridgeLoop(relay, lambda text: calls.append(text) or BridgeReply(text="ok"))
    loop.step()
    assert calls == ["hi"]


def test_one_founder_turn_can_get_multiple_reply_turns():
    relay = _ScriptedAgentRelay([([_turn(1, "hi")], None)])
    loop = BridgeLoop(relay, lambda text: [BridgeReply(text="a"), BridgeReply.playback("b", {"x": 1})])
    loop.step()
    assert relay.posted == [[{"kind": "message", "text": "a"},
                              {"kind": "playback", "text": "b", "payload": {"x": 1}}]]


def test_lease_refusal_on_poll_stops_and_never_retries():
    err = RelayError(422, {"rule": "relay-lease", "problem": "held",
                            "remedy": "wait, or stop the other connected agent"})
    relay = _ScriptedAgentRelay([([], err)])
    loop = BridgeLoop(relay, lambda text: BridgeReply(text="x"))
    with pytest.raises(LeaseRefused) as exc:
        loop.step()
    assert "wait" in str(exc.value)
    assert loop.stopped is True and loop.stop_reason == exc.value.remedy


def test_lease_refusal_on_post_also_stops_and_never_retries():
    err = RelayError(422, {"rule": "relay-lease", "problem": "held", "remedy": "wait it out"})

    class _RefusesOnPost(_ScriptedAgentRelay):
        def post_turns(self, turns):
            raise err

    relay = _RefusesOnPost([([_turn(1, "hi")], None)])
    loop = BridgeLoop(relay, lambda text: BridgeReply(text="x"))
    with pytest.raises(LeaseRefused):
        loop.step()
    assert loop.stopped is True


def test_non_lease_relay_error_propagates_unchanged():
    err = RelayError(422, {"rule": "relay-turn-too-long", "problem": "too long", "remedy": "shorten it"})
    relay = _ScriptedAgentRelay([([], err)])
    loop = BridgeLoop(relay, lambda text: BridgeReply(text="x"))
    with pytest.raises(RelayError) as exc:
        loop.step()
    assert exc.value.rule == "relay-turn-too-long"
    assert loop.stopped is False


def test_run_until_stops_the_instant_the_predicate_is_satisfied():
    relay = _ScriptedAgentRelay([([], None), ([_turn(1, "go")], None), ([], None)])
    seen: list[str] = []
    loop = BridgeLoop(relay, lambda text: seen.append(text) or BridgeReply(text="ok"))
    loop.run_until(lambda: bool(seen))
    assert seen == ["go"]


def test_run_until_raises_timeout_if_the_predicate_never_becomes_true():
    relay = _ScriptedAgentRelay([([], None)] * 5)
    loop = BridgeLoop(relay, lambda text: BridgeReply(text="x"))
    with pytest.raises(TimeoutError):
        loop.run_until(lambda: False, max_steps=3)
