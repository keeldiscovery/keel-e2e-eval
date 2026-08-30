"""003-eval-set T001: policy v2 fixtures. Proves the recalibration (evals/policy.py judgement
call 3; specs/eval-scoring-design.md §3's dated amendment; runs/DRIFT.md #4's re-adjudication) by
construction:

- a raw enum/field-name leak in an agent-cycle's `instruction`/`requirements` no longer fails
  anything (those texts are agent-facing, not swept any more);
- the same leak in a handoff's `display` still fails both `CLA-A1` and the new handoff `GUI-A2` --
  the one protocol text a founder actually receives stays checked at full strength.
"""

from __future__ import annotations

from evals import policy
from harness import scoring
from harness.steps import Recorder


def _checks_for(scorecard: dict, check_id: str) -> list[dict]:
    return [c for entry in scorecard["interactions"] for c in entry["checks"] if c["check_id"] == check_id]


def _score(tmp_path):
    return scoring.score_bundle(tmp_path, scenario="policy-v2-fixture", complete=True)


def test_policy_version_is_2():
    assert policy.POLICY_VERSION == 2


# --------------------------------------- agent-cycle: no longer vocabulary-swept (US1 scenario 1)

def test_seeded_enum_in_instruction_and_requirements_no_longer_fails_anything(tmp_path):
    """A raw `Verdict` enum and a raw field name (`askedOf`), seeded into an agent-cycle's
    `instruction.content` and `requirements` -- exactly what tripped policy v1's CLA-A1/GUI-A2
    twenty times over on S-001 -- must not fail CLA-A1 or GUI-A2 under v2, because neither check
    applies to an agent-cycle interaction any more."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("agent-cycle"):
        with recorder.step("get_next (project p1)", party="agent", kind="protocol") as h:
            h.record_wire({}, {"status": 200, "body": {
                "kind": "action", "action": "INTRODUCE_ASSUMPTIONS", "token": "t",
                "instruction": {
                    "purpose": "introduce assumptions",
                    "content": "a load-bearing belief is CONTRADICTED when the majority of people "
                               "who spoke described the opposite",
                },
                "requirements": ["askedOf naming a role whose type is compatible with the stage"],
                "context": [], "detail": {"stage": "PROBLEM"},
            }})

    scorecard = _score(tmp_path)
    cla = _checks_for(scorecard, "CLA-A1")
    gui_a2 = _checks_for(scorecard, "GUI-A2")
    assert cla == [], "CLA-A1 must not be emitted for an agent-cycle interaction under policy v2"
    assert gui_a2 == [], "GUI-A2 must not be emitted for an agent-cycle interaction under policy v2"
    # GUI-A1 (presence/sentence-shape) and ORI-A1 (non-empty instruction) are untouched.
    gui_a1 = _checks_for(scorecard, "GUI-A1")
    assert len(gui_a1) == 1 and gui_a1[0]["pass"] is True
    ori_a1 = _checks_for(scorecard, "ORI-A1")
    assert len(ori_a1) == 1 and ori_a1[0]["pass"] is True


# ------------------------------------------ handoff display: still swept (US1 scenario 2)

def test_seeded_enum_in_handoff_display_still_fails_cla_a1_and_gui_a2(tmp_path):
    """The one protocol text a founder actually receives -- a handoff's `display` -- stays swept
    at full strength: a raw enum there fails both CLA-A1 (unchanged from v1) and GUI-A2 (new
    under v2)."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("agent-handoff"):
        with recorder.step("get_next (project p1)", party="agent", kind="protocol") as h:
            h.record_wire({}, {"status": 200, "body": {
                "kind": "handoff", "reason": "REVIEW",
                "display": "The problem card's verdict is CONTRADICTED -- read the contradictions "
                           "handle before deciding what to do.",
                "detail": {"stage": "PROBLEM"},
            }})

    scorecard = _score(tmp_path)
    cla = _checks_for(scorecard, "CLA-A1")
    gui_a2 = _checks_for(scorecard, "GUI-A2")
    assert len(cla) == 1 and cla[0]["pass"] is False
    assert "CONTRADICTED" in cla[0]["detail"]
    assert len(gui_a2) == 1 and gui_a2[0]["pass"] is False
    assert "CONTRADICTED" in gui_a2[0]["detail"]


def test_clean_handoff_display_passes_cla_a1_and_gui_a2(tmp_path):
    """Control for the above: a founder-phrased display with no leaks passes both."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("agent-handoff"):
        with recorder.step("get_next (project p1)", party="agent", kind="protocol") as h:
            h.record_wire({}, {"status": 200, "body": {
                "kind": "handoff", "reason": "REVIEW",
                "display": "The problem card is waiting for your approval -- read the questions "
                           "before anyone is asked.",
                "detail": {"stage": "PROBLEM"},
            }})

    scorecard = _score(tmp_path)
    cla = _checks_for(scorecard, "CLA-A1")
    gui_a2 = _checks_for(scorecard, "GUI-A2")
    assert len(cla) == 1 and cla[0]["pass"] is True
    assert len(gui_a2) == 1 and gui_a2[0]["pass"] is True
