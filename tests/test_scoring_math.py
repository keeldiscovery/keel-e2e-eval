"""T015: scoring math (halves, category weights, the completion gate), an interrupted-run
fixture gated at 2/5 (SC-003), and re-score idempotence -- a bumped policy stamp updates without
mutating transcript.jsonl or screenshots (SC-004)."""

from __future__ import annotations

from evals import policy
from evals.scenario import Fact
from harness import rubric, scoring
from harness.evidence import _read_transcript, generate_report
from harness.interactions import Interaction
from harness.steps import Recorder


def _cr(check_id, attribute, weight, passed, **evidence):
    return rubric.CheckResult(check_id=check_id, attribute=attribute, weight=weight,
                               passed=passed, detail="fixture", evidence=evidence)


# -------------------------------------------------------------------------------- round_half

def test_round_half_rounds_to_the_nearest_half_point():
    assert scoring.round_half(4.24) == 4.0
    assert scoring.round_half(4.26) == 4.5
    assert scoring.round_half(4.75) == 5.0
    assert scoring.round_half(0.24) == 0.0


# ------------------------------------------------------------------ interaction attribute score

def test_interaction_attribute_score_is_weighted_and_halved():
    checks = [
        _cr("A", "ORIENTATION", 1, True),
        _cr("B", "ORIENTATION", 1, False),
        _cr("C", "ORIENTATION", 2, True),
    ]
    # passed weight = 1 + 2 = 3, total weight = 4 -> 5 * 3/4 = 3.75 -> rounds to 4.0 (nearest half)
    score, weight = scoring.score_interaction_attribute(checks, "ORIENTATION")
    assert score == 4.0
    assert weight == 4


def test_interaction_attribute_score_is_none_when_the_attribute_is_not_carried():
    checks = [_cr("A", "CLARITY", 1, True)]
    score, weight = scoring.score_interaction_attribute(checks, "ORIENTATION")
    assert score is None
    assert weight == 0.0


def test_waived_check_counts_as_pass_in_the_attribute_score():
    checks = [_cr("A", "FIDELITY", 1, True, )]
    checks[0].waived = {"reason": "r", "reference": "ref"}
    score, _weight = scoring.score_interaction_attribute(checks, "FIDELITY")
    assert score == 5.0


# --------------------------------------------------------------------------------- categories

def test_category_score_weights_by_each_interactions_total_check_weight():
    results = {
        "I1": [_cr("A", "FIDELITY", 1, True)],           # 5.0, weight 1
        "I2": [_cr("B", "FIDELITY", 2, False)],           # 0.0, weight 2
    }
    categories = scoring.score_categories(results)
    # (5.0*1 + 0.0*2) / 3 = 1.666.. -> rounds to 1.5
    assert categories["FIDELITY"] == 1.5


def test_category_absent_when_no_interaction_carries_it():
    results = {"I1": [_cr("A", "FIDELITY", 1, True)]}
    categories = scoring.score_categories(results)
    assert "GUIDANCE" not in categories
    assert categories["FIDELITY"] == 5.0


# --------------------------------------------------------------------------------- run score

def test_run_score_is_the_category_weighted_mean_when_complete():
    categories = {"FIDELITY": 5.0, "GUIDANCE": 5.0, "ORIENTATION": 5.0, "CLARITY": 5.0}
    assert scoring.compute_run_score(categories, complete=True) == 5.0

    categories_mixed = {"FIDELITY": 0.0, "GUIDANCE": 5.0, "ORIENTATION": 5.0, "CLARITY": 5.0}
    # 0*0.4 + 5*0.25 + 5*0.2 + 5*0.15 = 3.0
    assert scoring.compute_run_score(categories_mixed, complete=True) == 3.0


def test_run_score_excludes_categories_with_no_data_rather_than_scoring_them_zero():
    # Only FIDELITY has data -- the run score should equal FIDELITY's score, not be dragged down
    # by treating the other three (weight 0.6 combined) as zero.
    categories = {"FIDELITY": 4.0}
    assert scoring.compute_run_score(categories, complete=True) == 4.0


def test_incomplete_run_is_capped_at_the_completion_gate():
    categories = {"FIDELITY": 5.0, "GUIDANCE": 5.0, "ORIENTATION": 5.0, "CLARITY": 5.0}
    assert scoring.compute_run_score(categories, complete=False) == policy.COMPLETION_GATE_SCORE


def test_incomplete_run_below_the_gate_is_not_raised_to_it():
    categories = {"FIDELITY": 1.0, "GUIDANCE": 1.0, "ORIENTATION": 1.0, "CLARITY": 1.0}
    assert scoring.compute_run_score(categories, complete=False) == 1.0


# ------------------------------------------------------------------------ interrupted run (SC-003)

def test_interrupted_run_scores_what_it_saw_gated_at_two(tmp_path):
    """A run that never finished the workflow (an exception mid-scenario) still gets a scored
    bundle -- category scores describe what was observed, but complete=False caps the run score."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui-visit"):
        with recorder.step("founder opens the problem stage card", party="founder", kind="browser") as h:
            h.capture_text("screen", "stage")
            h.capture_text("stage", "PROBLEM")
            h.capture_text("identity", "p1")
            h.capture_text("stage_identity", "THE PROBLEM")
            h.capture_text("stage_screen", "THE PROBLEM\nEverything looks great here.")
    # Simulate the harness dying mid-scenario: no PROCEED_TO_BRIEF, no brief screen -- just what
    # was captured before the crash.
    scorecard = scoring.score_bundle(tmp_path, scenario="interrupted", complete=False)
    assert scorecard["complete"] is False
    assert scorecard["gated"] is True
    assert scorecard["run_score"] <= policy.COMPLETION_GATE_SCORE
    # The categories that WERE observed are still reported, not blanked out by the gate.
    assert scorecard["categories"]  # at least ORIENTATION/CLARITY from the one ui-visit


# --------------------------------------------------------------------------- re-score (SC-004)

def test_rescoring_is_idempotent_and_never_mutates_transcript_or_screenshots(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui-visit"):
        with recorder.step("founder opens the problem stage card", party="founder", kind="browser") as h:
            h.capture_text("screen", "stage")
            h.capture_text("stage", "PROBLEM")
            h.capture_text("stage_screen", "THE PROBLEM\nPayroll managers lose hours.")
            shot = recorder.next_screenshot_name("stage")
            recorder.screenshot_path(shot).write_bytes(b"\x89PNG\r\n\x1a\nfake")
            h.add_screenshot(shot)

    facts = {"problem_statement": Fact(text="Payroll managers lose hours.", kind="statement",
                                        hops=["stage_screen"])}
    scoring.write_facts(tmp_path, facts)

    from harness.evidence import write_verdict
    write_verdict(tmp_path, scenario="s001-smoke", passed=True, failed_step=None, duration_s=1.0)

    transcript_before = (tmp_path / "transcript.jsonl").read_text()
    screenshot_before = (tmp_path / "screenshots" / shot).read_bytes()

    first_report = generate_report(tmp_path).read_text()
    second_report = generate_report(tmp_path).read_text()

    assert (tmp_path / "transcript.jsonl").read_text() == transcript_before
    assert (tmp_path / "screenshots" / shot).read_bytes() == screenshot_before
    assert first_report == second_report

    import json
    verdict = json.loads((tmp_path / "verdict.json").read_text())
    assert verdict["policy_version"] == policy.POLICY_VERSION
    assert verdict["score"] is not None
