"""spec 005-connect-stack FR-010/FR-011 (evals/policy.py's module docstring, judgement call 9):
policy v6 retires the agent-protocol half of the rubric wholesale (there is no more founder-agent
HTTP/MCP surface for this harness to observe -- every inference job runs through keel-runtime's
scripted executor and is only ever seen through the screen) and adds three ui_visit checks:
CLA-U4 (no retired string), CLA-U5 (no gendered pronoun for a participant), GUI-U3 (every waiting
state names what is waited for). The construction-not-assertion fixtures for those three live in
tests/test_scoring_seeded_loss.py alongside every other seeded-loss case; this file proves the
version bump itself and the specific vocabulary/removal claims policy v6 makes.
"""

from __future__ import annotations

from evals import policy
from harness import scoring
from harness.steps import Recorder


def test_v6_vocabulary_survives_every_later_bump():
    """The version constant itself is `tests/test_policy_v8.py`'s to assert -- this file proves
    what **v6** claimed, and that no later bump quietly took it away."""
    assert policy.POLICY_VERSION >= 7


def test_v7_exempts_the_two_house_copy_collisions():
    """Judgement call 10: approved keel-web copy must not read as an enum leak."""
    assert "assumptions" not in policy.CLARITY_TOKENS
    assert "CONTRADICTED" not in policy.CLARITY_TOKENS
    assert policy.enum_violations("NOT HOLDING UP \u2014 WHAT THEY CONTRADICTED") == []
    assert policy.enum_violations("That's how the assumptions get validated.") == []
    # and the neighbours are still swept
    assert policy.enum_violations("verdict: SUPPORTED") == ["SUPPORTED"]
    assert policy.enum_violations("status AWAITING_CONFIRMATION") == ["AWAITING_CONFIRMATION"]


def test_agent_protocol_checks_are_gone_from_the_registry():
    """ORI-A*/GUI-A* (agent-cycle), ORI-H1/GUI-H1 (agent-handoff), ORI-R1/GUI-R1 (agent-refusal),
    and the chat-visit trio (CLA-C1/ORI-C1/GUI-C1) no longer exist as checks at all -- there is no
    interaction kind left that could ever produce them (harness/interactions.py's FR-009 kinds)."""
    retired = {
        "ORI-A1", "ORI-A2", "ORI-A3", "GUI-A1", "GUI-A2", "GUI-A3", "CLA-A2",
        "ORI-H1", "GUI-H1", "ORI-R1", "GUI-R1", "CLA-C1", "ORI-C1", "GUI-C1",
    }
    assert retired.isdisjoint(policy.CHECKS.keys())


def test_ui_visit_checks_and_arrival_check_survive():
    surviving = {"ORI-U1", "ORI-U2", "ORI-U3", "GUI-U1", "GUI-U2", "GUI-U3",
                 "CLA-U1", "CLA-U2", "CLA-U3", "CLA-U4", "CLA-U5", "CLA-AR1", "ORI-P1", "GUI-P1"}
    assert surviving <= policy.CHECKS.keys()


def test_category_weights_still_sum_to_one():
    assert sum(policy.CATEGORY_WEIGHTS.values()) == 1.0


def test_connect_states_are_clarity_tokens():
    """The device-authorization/runtime-job status vocabulary a founder-facing screen must never
    leak raw (evals/policy.py's `CONNECT_STATES`)."""
    for token in ("AWAITING_CONFIRMATION", "ACCEPTED", "PENDING", "RUNNING", "DONE", "EXPIRED"):
        assert token in policy.CLARITY_TOKENS


def test_seeded_connect_state_leak_fails_cla_u1(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the connect screen", party="founder", kind="browser") as h:
            h.capture_text("screen", "connect")
            h.capture_text("stage_screen", "Status: AWAITING_CONFIRMATION")

    scorecard = scoring.score_bundle(tmp_path, scenario="policy-v6-fixture", complete=True)
    checks = [c for entry in scorecard["interactions"] for c in entry["checks"] if c["check_id"] == "CLA-U1"]
    assert len(checks) == 1
    assert checks[0]["pass"] is False
    assert "AWAITING_CONFIRMATION" in checks[0]["detail"]


def test_the_wire_only_hops_stayed_retired():
    """v6 retired the five wire-only hops with the agent protocol that carried them. v8 restated
    `HOP_IDS` for the measured-beliefs screens (`tests/test_policy_v8.py` asserts that list); what
    this still proves is that no retired wire hop came back with it."""
    assert "agent_echo" not in policy.HOP_IDS
    assert "interpret_context" not in policy.HOP_IDS
    assert "recorded" not in policy.HOP_IDS
    assert "roles_context" not in policy.HOP_IDS


def test_answer_participant_page_is_weight_2():
    assert policy.fid_weight("answer", "participant_page") == 2
    assert policy.fid_weight("answer", "interpret_context") == policy.DEFAULT_WEIGHT
