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


# ------------------------------------------- US2: calibration (062; calls 30-32, marks §2.1-§2.3)

import copy                                                                  # noqa: E402


@pytest.fixture()
def registry():
    return fx.registry()


def _calibrate(entry, registry, vector="PROBLEM", mutate=None, judge=None):
    result = fx.calibration_result(registry, vector)
    if mutate:
        mutate(result)
    return score_mod.score_calibration(fx.calibration_case(entry, vector), entry, registry,
                                       result, judge=judge)


def _q(result, key):
    return next(q for q in result["questions"] if q["key"] == key)


@pytest.mark.parametrize("vector, count", [("PROBLEM", 9), ("SOLUTION", 9), ("COMMERCIAL", 7)])
def test_a_good_answer_covers_its_slice_and_meets_every_rule(entry, registry, vector, count):
    score = _calibrate(entry, registry, vector)
    assert (score.coverage_hit, score.coverage_of, score.coverage_passed) == (count, count, True)
    assert (score.validity_hit, score.validity_of) == (count, count), score.faults
    assert score.faults == []
    if vector == "PROBLEM":
        assert (score.leak_clean, score.leak_of) == (9, 9)
    else:
        assert score.leak_of == 0, "sweep A runs on the PROBLEM vector only"


@pytest.mark.parametrize("name, mutate, words", [
    ("doubled", lambda r: r["questions"].append(copy.deepcopy(r["questions"][1])), "doubled"),
    ("missing", lambda r: r["questions"].pop(2), "missing problem.severity"),
    ("foreign", lambda r: r["questions"].append({"key": "problem.vibes", "question": "?"}),
     "outside the slice problem.vibes"),
    ("out of order", lambda r: r["questions"].insert(0, r["questions"].pop(3)), "out of order"),
])
def test_coverage_is_absolute_and_any_slip_fails_the_case(entry, registry, name, mutate, words):
    score = _calibrate(entry, registry, mutate=mutate)
    assert score.coverage_passed is False and score.coverage_hit == 0, name
    assert any(words in f["evidence"] for f in score.faults if f["check"] == "dimension_coverage")


def _severity_options(r):
    return _q(r, "problem.severity")["options"]


@pytest.mark.parametrize("name, mutate, words", [
    ("count", lambda r: _severity_options(r).pop(), "4 options; the registry fixes 5"),
    ("order", lambda r: _severity_options(r).insert(0, _severity_options(r).pop(2)),
     "out of registry order"),
    ("foreign code", lambda r: _severity_options(r)[0].__setitem__("normalized", "awful"),
     "not the registry's"),
    ("repeated", lambda r: _q(r, "problem.consequence")["options"].append(
        copy.deepcopy(_q(r, "problem.consequence")["options"][0])), "repeated"),
    ("too few written", lambda r: _q(r, "problem.consequence")["options"].__delitem__(
        slice(1, 3)), "the rule asks 4-6"),
    ("not a slug", lambda r: _q(r, "problem.consequence")["options"][0].__setitem__(
        "normalized", "Lost Sleep"), "not slugs"),
    ("empty phrase", lambda r: _severity_options(r)[1].__setitem__("belief_phrase", " "),
     "no belief_phrase"),
    ("phrase is label", lambda r: _severity_options(r)[1].__setitem__(
        "belief_phrase", "OPTION 2 for this"), "its belief_phrase is its label"),
    ("not sure", lambda r: _severity_options(r)[4].__setitem__("label", "I'm not sure"),
     "not-sure option"),
    ("template", lambda r: _q(r, "problem.severity").__setitem__("belief_template", "x"),
     "{value} exactly once"),
    ("options on numeric", lambda r: _q(r, "problem.frequency").__setitem__(
        "options", [{"label": "1", "normalized": "one", "belief_phrase": "one"}]),
     "options on a numeric control"),
    ("numeric spec", lambda r: _q(r, "problem.duration").__setitem__(
        "normalized", {"axis_max": 120}), "numeric spec axis_max"),
    ("no seven nights", lambda r: _q(r, "problem.prevalence").__setitem__(
        "question", "How many had this recently?"), "7-night window"),
    ("fifths with a hole", lambda r: _q(r, "problem.prevalence")["options"][2].__setitem__(
        "normalized", "p_50_60"), "not the registry's"),
])
def test_option_validity_fails_on_each_registry_rule_made_to_fail_once(entry, registry, name,
                                                                       mutate, words):
    score = _calibrate(entry, registry, mutate=mutate)
    validity = [f for f in score.faults if f["check"] == "option_validity"]
    assert len(validity) == 1, (name, score.faults)
    assert words in validity[0]["evidence"], (name, validity[0]["evidence"])
    assert score.validity_hit == score.validity_of - 1


def test_the_fixed_codes_a_model_written_rule_names_must_be_there(registry):
    dimension = registry.by_key("commercial.existing_sacrifice")
    good = fx.calibration_question(dimension)
    assert score_mod.calibration_checks(good, dimension) == []
    good["options"] = [o for o in good["options"] if o["normalized"] != "none"]
    assert any("['none']" in f for f in score_mod.calibration_checks(good, dimension))


def test_the_commitment_ladder_is_the_rungs_for_the_projects_type(registry):
    dimension = registry.by_key("commercial.commitment")
    b2c = fx.calibration_question(dimension)
    assert [o["normalized"] for o in b2c["options"]] == ["setup", "install", "mic",
                                                          "next_episode", "contact_me"]
    assert score_mod.calibration_checks(b2c, dimension) == []
    assert any("the ladder is" in f for f in score_mod.calibration_checks(b2c, dimension,
                                                                         b2b=True))


def test_a_failed_case_covers_nothing_and_writes_nothing(entry, registry):
    score = score_mod.score_calibration(fx.calibration_case(entry, "PROBLEM"), entry, registry,
                                        None, failed="schema-invalid")
    assert (score.coverage_hit, score.coverage_of, score.validity_of) == (0, 9, 0)
    assert score.failed == "schema-invalid"


def test_totals_roll_calibration_into_the_three_marks(entry, registry):
    good = _calibrate(entry, registry)
    bad = _calibrate(entry, registry, mutate=lambda r: r["questions"].pop(2))
    totals = score_mod.totals([good, bad])
    assert totals["calibration_cases"] == 2
    assert totals["calibration_coverage"] == {"hit": 9, "of": 18}
    assert totals["dimension_coverage"] == 0.5
    assert totals["calibration_validity"] == {"hit": 17, "of": 17}
    assert totals["option_validity"] == 1.0
    assert totals["no_leak"] == 1.0
