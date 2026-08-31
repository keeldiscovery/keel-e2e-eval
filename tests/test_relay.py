"""Stackless unit tests for harness/relay.py (design §12 item 1) -- a stubbed HTTP transport, no
live stack: proves the wire discipline this feature's own research pinned down live against
keel-cloud's source and acceptance tests -- the lease travels as an ordinary query parameter
(never a header), an empty long-poll is a clean, turn-less result (never an error), and a refusal
maps to `RelayError`'s own `{rule, problem, remedy}` triple.
"""

from __future__ import annotations

import pytest

from harness.relay import AgentRelay, FounderRelay, RelayError
from harness.steps import Recorder


class _FakeResponse:
    def __init__(self, status: int, body):
        self.status_code = status
        self._body = body

    def json(self):
        return self._body


class _FakeSession:
    """Records every call and hands it to `respond` -- a per-test callable, so each test picks
    exactly the wire behavior it wants to prove without a real HTTP layer."""

    def __init__(self, respond):
        self.calls: list[tuple] = []
        self._respond = respond

    def post(self, url, json=None, params=None, timeout=None):
        self.calls.append(("POST", url, json, params))
        return self._respond("POST", url, json, params)

    def get(self, url, params=None, timeout=None):
        self.calls.append(("GET", url, None, params))
        return self._respond("GET", url, None, params)


# --------------------------------------------------------------------------------- founder side

def test_founder_relay_posts_and_returns_the_turn(tmp_path):
    def respond(method, url, body, params):
        assert method == "POST" and url.endswith("/v2/projects/p1/relay")
        return _FakeResponse(201, {"seq": 1, "author": "founder", "kind": "message",
                                    "text": body["text"], "payload": None, "at": "2026-08-31T00:00:00Z"})
    session = _FakeSession(respond)
    relay = FounderRelay("http://localhost:18080", session, "p1", Recorder(tmp_path))
    turn = relay.post_turn("hello")
    assert turn.seq == 1 and turn.author == "founder" and turn.text == "hello"


def test_founder_relay_read_turns_sends_cursor_as_a_query_param(tmp_path):
    seen = {}

    def respond(method, url, body, params):
        seen["params"] = params
        return _FakeResponse(200, {"turns": []})
    session = _FakeSession(respond)
    relay = FounderRelay("http://localhost:18080", session, "p1", Recorder(tmp_path))
    relay.read_turns(cursor=7)
    assert seen["params"] == {"cursor": 7}


def test_founder_relay_presence_reads_connected_and_last_poll_at(tmp_path):
    def respond(method, url, body, params):
        assert url.endswith("/relay/presence")
        return _FakeResponse(200, {"connected": True, "lastPollAt": "2026-08-31T00:00:05Z"})
    session = _FakeSession(respond)
    relay = FounderRelay("http://localhost:18080", session, "p1", Recorder(tmp_path))
    presence = relay.presence()
    assert presence == {"connected": True, "lastPollAt": "2026-08-31T00:00:05Z"}


def test_founder_relay_refusal_raises_relay_error_with_the_rule_triple(tmp_path):
    def respond(method, url, body, params):
        return _FakeResponse(422, {"rule": "relay-turn-too-long",
                                    "problem": "this turn is 4001 characters, over the 4000-character limit",
                                    "remedy": "shorten the turn to 4000 characters or fewer and post it again"})
    session = _FakeSession(respond)
    relay = FounderRelay("http://localhost:18080", session, "p1", Recorder(tmp_path))
    with pytest.raises(RelayError) as exc:
        relay.post_turn("x" * 5000)
    assert exc.value.rule == "relay-turn-too-long"
    assert "shorten" in exc.value.remedy


# ------------------------------------------------------------------------------------ agent side

def test_agent_relay_lease_is_a_query_param_never_a_header(tmp_path):
    seen = []

    def respond(method, url, body, params):
        seen.append(dict(params or {}))
        return _FakeResponse(200, {"leaseToken": "abc123", "turns": []})
    session = _FakeSession(respond)
    relay = AgentRelay("http://localhost:18080", session, "p1", Recorder(tmp_path), poll_window_s=1)
    relay.poll(cursor=0)
    assert "lease" not in seen[0]  # first contact -- nothing to present yet
    assert relay.lease == "abc123"
    relay.poll(cursor=0)
    assert seen[1]["lease"] == "abc123"  # minted token re-presented on the next call


def test_agent_relay_empty_poll_is_clean_not_an_error(tmp_path):
    def respond(method, url, body, params):
        return _FakeResponse(200, {"leaseToken": "t1", "turns": []})
    session = _FakeSession(respond)
    relay = AgentRelay("http://localhost:18080", session, "p1", Recorder(tmp_path), poll_window_s=1)
    turns, cursor = relay.poll(cursor=5)
    assert turns == [] and cursor == 5


def test_agent_relay_poll_advances_cursor_to_the_highest_seq_seen(tmp_path):
    def respond(method, url, body, params):
        return _FakeResponse(200, {"leaseToken": "t1", "turns": [
            {"seq": 3, "author": "founder", "kind": "message", "text": "a", "payload": None, "at": None},
            {"seq": 5, "author": "founder", "kind": "message", "text": "b", "payload": None, "at": None},
        ]})
    session = _FakeSession(respond)
    relay = AgentRelay("http://localhost:18080", session, "p1", Recorder(tmp_path), poll_window_s=1)
    turns, cursor = relay.poll(cursor=0)
    assert cursor == 5 and [t.text for t in turns] == ["a", "b"]


def test_agent_relay_post_turns_carries_kind_text_and_payload(tmp_path):
    seen = {}

    def respond(method, url, body, params):
        seen["body"] = body
        return _FakeResponse(200, {"leaseToken": "t1", "turns": []})
    session = _FakeSession(respond)
    relay = AgentRelay("http://localhost:18080", session, "p1", Recorder(tmp_path), poll_window_s=1)
    relay.post_turns([{"kind": "playback", "text": "done", "payload": {"roles": []}}])
    assert seen["body"] == {"turns": [{"kind": "playback", "text": "done", "payload": {"roles": []}}]}


def test_agent_relay_lease_refusal_raises_relay_error_naming_the_remedy(tmp_path):
    def respond(method, url, body, params):
        return _FakeResponse(422, {"rule": "relay-lease",
                                    "problem": "another agent session already holds this project's relay lease",
                                    "remedy": "wait for the lease to expire, or stop the other connected agent"})
    session = _FakeSession(respond)
    relay = AgentRelay("http://localhost:18080", session, "p1", Recorder(tmp_path), poll_window_s=1)
    with pytest.raises(RelayError) as exc:
        relay.poll(cursor=0)
    assert exc.value.rule == "relay-lease"
    assert "wait" in exc.value.remedy
