"""`instructions/score.py` at `MARKS_VERSION` 9 (spec 029 data-model §6; T025, T029, T035, T039,
T040, T042, T043).

Fixtures a person can check by hand: the hand-sized registry slice and `09-fixture-r3.yaml`. Every
mark has its green half and its red half here, and every total is summed over its own
denominator and never another's.
"""

from __future__ import annotations

import json

import pytest

from instructions import compare as compare_mod
from instructions import marks as marks_mod
from instructions import prompts as prompts_mod
from instructions import score as score_mod
from tests import v9_fixtures as fx


@pytest.fixture()
def entry():
    return fx.entry()


def _compare_case(entry):
    return prompts_mod.Case(case_id=f"{entry.id}/COMPARE", kind="COMPARE", entry_id=entry.id,
                            screen="COMPARE", subject="COMPARE", run_index=0, payload={})


def _compare(entry, name="agree"):
    produced = json.loads((fx.COMPARE / f"09-fixture.{name}.out.json").read_text())
    return score_mod.score_compare(_compare_case(entry), entry,
                                   compare_mod.diff(entry.expected, produced, entry=entry))


# ------------------------------------------------------------------------------------ compare

def test_score_compare_carries_the_diff_onto_the_case(entry):
    score = _compare(entry)
    assert (score.agreed, score.checks, score.measured) == (28, 28, True)
    assert score.compare_correctness == 1.0


def test_compare_correctness_is_measured_only_when_every_row_was(entry):
    good = _compare(entry)
    bad = score_mod.score_compare(_compare_case(entry), entry,
                                  compare_mod.unmeasured(entry.id, "no engine (keel-cloud 058)"))
    totals = score_mod.totals(compare_scores=[good])
    assert totals["compare_measured"] and totals["compare_correctness"] == 1.0
    assert totals["compare_checks"] == 28
    mixed = score_mod.totals(compare_scores=[good, bad])
    assert mixed["compare_measured"] is False and mixed["compare_correctness"] is None
    assert mixed["compare_unmeasured"] == [{"entry": "09-fixture",
                                           "reason": "no engine (keel-cloud 058)"}]
    judged = marks_mod.judge(mixed, marks_mod.load())
    assert judged["compare_correctness"]["measured"] is False


def test_a_disagreeing_engine_is_measured_and_not_met(entry):
    totals = score_mod.totals(compare_scores=[_compare(entry, "disagree")])
    assert totals["compare_agreed"] == 26 and totals["compare_reported_diffs"] == 1
    assert marks_mod.judge(totals, marks_mod.load())["compare_correctness"]["met"] is False


def test_a_run_with_no_compare_row_has_compare_unmeasured():
    assert score_mod.totals()["compare_measured"] is False


# ------------------------------------------------------------------------------------- totals

def test_totals_carries_every_v9_key_and_nothing_retired():
    totals = score_mod.totals()
    for key in ("calibration_cases", "calibration_coverage", "calibration_validity",
                "calibration_leak", "respondent_cases", "respondent_coverage",
                "respondent_validity", "respondent_leak", "dimension_coverage", "option_validity",
                "no_leak", "leak_hits", "leak_judged", "judged_fraction", "judge_calls",
                "anchoring_accuracy", "guessed_precision", "guessed_recall", "confusion",
                "people_given", "people_answered", "reading_missing_ids", "reading_extra_ids",
                "chipped_skipped", "compare_checks", "compare_agreed", "compare_correctness",
                "compare_measured", "compare_reported_diffs", "refusals_by_rule",
                "refusals_measured", "refusals_shown", "shape_refusals", "schema_invalid",
                "errored", "brief_cases", "brief_paragraphs", "brief_measured", "brief_by_mark"):
        assert key in totals, key
    for retired in ("golden_belief_recall", "exact_match", "phrase_band", "anchors_given",
                    "unresolved_reads"):
        assert retired not in totals, retired


def test_an_empty_run_measures_nothing_and_says_none_rather_than_zero():
    totals = score_mod.totals()
    for name in ("dimension_coverage", "option_validity", "no_leak", "anchoring_accuracy",
                 "compare_correctness", "brief_paragraphs"):
        assert totals[name] is None, name


def test_the_spread_reports_each_run_and_averages_nothing():
    from types import SimpleNamespace
    scores = [SimpleNamespace(entry_id="e", subject="PROBLEM", value=v) for v in (1.0, 0.0, 1.0)]
    spread = score_mod.spread(scores, lambda s: s.value)
    assert spread == {"e/PROBLEM": {"runs": [1.0, 0.0, 1.0], "min": 0.0, "max": 1.0}}


def test_the_retired_scorers_are_gone():
    for name in ("score_assumptions", "score_reading", "AssumptionScore", "FIELDS"):
        assert not hasattr(score_mod, name), name
