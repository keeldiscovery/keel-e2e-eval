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
    ("phrase too long", lambda r: _severity_options(r)[1].__setitem__(
        "belief_phrase", "x" * 121), "121 characters, longer than 120"),
    ("phrase not sure", lambda r: _severity_options(r)[1].__setitem__(
        "belief_phrase", "not sure how bad it is"), "belief_phrase carries a not-sure word"),
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



def test_a_belief_phrase_equal_to_its_label_is_accepted(entry, registry):
    # Call 37 (founder decision 32, 2026-10-08): C4 no longer refuses a phrase that repeats its
    # label, case-folded -- keel-cloud 062 accepts it, so the eval does too.
    def same(r):
        for option in _severity_options(r):
            option["belief_phrase"] = str(option["label"]).upper()
    score = _calibrate(entry, registry, mutate=same)
    assert not [f for f in score.faults if f["check"] == "option_validity"], score.faults
    assert score.validity_hit == score.validity_of

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


# --------------------------------------------- US3: respondent (063; calls 30-32, marks §2.2-§2.3)

def _respond(entry, registry, part, mutate=None, *, link="PRIMARY", judge=None, label_only=False):
    result = fx.respondent_result(entry, part, link=link, label_only=label_only)
    if mutate:
        mutate(result)
    return score_mod.score_respondent(fx.respondent_case(entry, part, link=link), entry,
                                      registry, entry.plan(), result, judge=judge)


def _item(result, key):
    return next(i for i in result["items"] if i["key"] == key)


@pytest.mark.parametrize("part, count, sweeps", [(1, 8, 16), (2, 9, 9), (3, 6, 6)])
def test_coverage_per_part_is_the_plan_exactly_once_each(entry, registry, part, count, sweeps):
    score = _respond(entry, registry, part)
    assert (score.coverage_hit, score.coverage_of) == (count, count)
    assert (score.validity_hit, score.validity_of) == (count, count), score.faults
    assert (score.leak_clean, score.leak_of) == (sweeps, sweeps), \
        "sweep A on Part 1's items, sweep B on every item"


def test_a_label_only_answer_is_held_to_the_count(entry, registry):
    score = _respond(entry, registry, 1, label_only=True)
    assert score.validity_hit == score.validity_of == 8, score.faults


def _options(result, key):
    return _item(result, key)["options"]


@pytest.mark.parametrize("name, mutate, words", [
    ("control", lambda r: _item(r, "problem.severity").__setitem__("control", "single_choice"),
     "control 'single_choice'"),
    ("founder code missing", lambda r: _options(r, "problem.consequence").pop(0),
     "missing code(s) ['late']"),
    ("a distractor missing", lambda r: _options(r, "problem.consequence").pop(2),
     "missing code(s) ['missed_train']"),
    ("something else not last", lambda r: _options(r, "problem.consequence").insert(
        0, _options(r, "problem.consequence").pop()), "not last"),
    ("fixed scale grew", lambda r: _options(r, "problem.severity").append(
        {"label": "Off the scale", "code": "off_scale"}), "nothing added"),
    ("chips", lambda r: _item(r, "problem.severity").__setitem__("chips", []), "chips []"),
    ("anchor", lambda r: _item(r, "problem.severity").__setitem__("anchor", "last_purchase"),
     "anchor 'last_purchase'"),
    ("own item first", lambda r: _options(r, "problem.importance").insert(
        0, _options(r, "problem.importance").pop(1)), "own item (finding_keys) is first"),
    ("not sure", lambda r: _options(r, "problem.severity")[0].__setitem__(
        "label", "Not sure, really"), "not-sure option"),
    ("options on a number", lambda r: _item(r, "problem.duration").__setitem__(
        "options", ["5", "10"]), "options on a number_with_unit control"),
])
def test_validity_fails_on_each_respondent_rule_made_to_fail_once(entry, registry, name, mutate,
                                                                  words):
    score = _respond(entry, registry, 1, mutate)
    validity = [f for f in score.faults if f["check"] == "option_validity"]
    assert len(validity) == 1, (name, score.faults)
    assert words in validity[0]["evidence"], (name, validity[0]["evidence"])


def test_a_founder_number_among_band_edges_is_a_fault_and_a_registry_edge_is_not(entry, registry):
    good = _respond(entry, registry, 2)
    assert not [f for f in good.faults if f["key"] == "solution.effectiveness_threshold"]
    founder = {"value": 7, "unit": "minutes"}
    dimension = registry.by_key("solution.effectiveness_threshold")
    row = entry.respondent_questions["solution.effectiveness_threshold"]
    item = {"key": dimension.key, "question": "How much sooner?",
            "options": ["Under 7", "7 to 10", "10 to 20", "20 or more", "Nothing would"]}
    assert any("band edge" in f for f in score_mod.respondent_checks(item, dimension, row, founder))
    founder["value"] = 5
    assert score_mod.respondent_checks(dict(item, options=["Under 5", "5 to 10", "10 to 20",
                                                           "20 or more", "Nothing would"]),
                                       dimension, row, founder) == [], \
        "5 is the registry's own edge, never the founder's to have leaked"


def test_sweep_a_runs_on_part_one_and_sweep_b_on_every_part(entry, registry):
    leak_a = _respond(entry, registry, 1, lambda r: _item(r, "problem.severity").__setitem__(
        "question", "How bad was it before the beep?"))
    assert [f["sweep"] for f in leak_a.faults if f["check"] == "no_leak"] == ["A"]
    part2 = _respond(entry, registry, 2, lambda r: _item(r, "solution.compatibility").__setitem__(
        "question", "When would the beep have helped?"))
    assert not [f for f in part2.faults if f["check"] == "no_leak"], \
        "after the reveal the mechanism may be named"
    leak_b = _respond(entry, registry, 2, lambda r: _item(r, "solution.relative_advantage")
                      .__setitem__("question", "Would a shorter search have mattered?"))
    faults = [f for f in leak_b.faults if f["check"] == "no_leak"]
    assert [f["sweep"] for f in faults] == ["B"] and "a shorter search" in faults[0]["evidence"]


def test_sweep_b_catches_a_founder_number_the_registry_did_not_fix(entry, registry):
    score = _respond(entry, registry, 1, lambda r: _item(r, "problem.duration").__setitem__(
        "question", "Was it more like 15 minutes?"))
    assert any("15" in f["evidence"] for f in score.faults if f.get("sweep") == "B")
    window = _respond(entry, registry, 1, lambda r: _item(r, "problem.frequency").__setitem__(
        "question", "On how many of the last 7 nights?"))
    assert not [f for f in window.faults if f["check"] == "no_leak"], \
        "the founder said up to 4 of 7; the 7 is the registry's window"


def test_the_b2b_link_scores_the_six_part_three_items(registry):
    b2b = fx.entry(fx.ENTRY_B2B)
    score = _respond(b2b, registry, 3, link="COMMERCIAL_B2B")
    assert (score.coverage_hit, score.coverage_of) == (6, 6)
    assert score.validity_hit == 6, score.faults
    assert score.link == "COMMERCIAL_B2B" and score.subject == "B2B"


def test_totals_roll_both_question_screens_into_the_same_three_marks(entry, registry):
    totals = score_mod.totals([_calibrate(entry, registry)], [_respond(entry, registry, 1),
                                                              _respond(entry, registry, 2)])
    assert totals["respondent_coverage"] == {"hit": 17, "of": 17}
    assert totals["dimension_coverage"] == 1.0
    assert totals["calibration_leak"]["of"] + totals["respondent_leak"]["of"] == 9 + 16 + 9


# -------------------------------------------------------------- US3: INTERPRET (064; call 33)

def _read(entry, name, result):
    person = entry.person(name)
    return score_mod.score_interpret(fx.interpret_case(entry, name), entry, person, result)


def _answer(entry, name, word, **extra):
    return {"invitationId": f"{entry.id}/{name}", "anchoring": word, **extra}


def test_one_judgement_a_readable_person_keyed_on_the_person(entry):
    readable = [p.person for p in entry.readable()]
    scores = [_read(entry, n, _answer(entry, n, entry.person(n).anchoring)) for n in readable]
    totals = score_mod.totals(interpret_scores=scores)
    assert totals["people_given"] == 9 and totals["people_answered"] == 9
    assert totals["anchoring_accuracy"] == 1.0
    assert totals["confusion"] == {"aa": 8, "ag": 0, "ga": 0, "gg": 1}
    assert totals["guessed_precision"] == 1.0 and totals["guessed_recall"] == 1.0


def test_a_reader_that_answers_anchored_to_everyone_has_guessed_recall_zero(entry):
    scores = [_read(entry, p.person, _answer(entry, p.person, "ANCHORED"))
              for p in entry.readable()]
    totals = score_mod.totals(interpret_scores=scores)
    assert totals["anchoring_accuracy"] == 8 / 9
    assert totals["guessed_recall"] == 0.0 and totals["guessed_precision"] is None


def test_the_chipped_person_is_never_in_any_count(entry):
    assert "Jo Judd" not in [p.person for p in entry.readable()]
    scores = [_read(entry, p.person, _answer(entry, p.person, p.anchoring))
              for p in entry.readable()]
    assert all(s.subject != "Jo Judd" for s in scores)


def test_a_stage_or_anchor_id_is_neither_read_nor_refused(entry):
    score = _read(entry, "Ann Abbott", _answer(entry, "Ann Abbott", "ANCHORED",
                                                stage="PROBLEM", anchorId="A1"))
    assert score.answered == 1 and score.agreed == 1 and score.shape_fault == 0


def test_a_word_outside_the_two_is_a_shape_refusal_counted_against_the_zero(entry):
    score = _read(entry, "Ann Abbott", _answer(entry, "Ann Abbott", "PROBABLY"))
    assert score.shape_fault == 1 and score.answered == 0
    assert score.missing_ids == ["Ann Abbott"]
    assert score_mod.totals(interpret_scores=[score], shape_refusals=0)["shape_refusals"] == 1


def test_another_persons_invitation_is_an_extra_id_and_this_person_missing(entry):
    score = _read(entry, "Ann Abbott", {"invitationId": "09-fixture/Someone Else",
                                        "anchoring": "ANCHORED"})
    assert score.extra_ids == ["09-fixture/Someone Else"] and score.missing_ids == ["Ann Abbott"]
    assert score.answered == 0


def test_a_read_in_keel_clouds_v8_interpret_shape_is_read_until_064_narrows_it(entry):
    score = _read(entry, "Ann Abbott", {"invitationId": "09-fixture/Ann Abbott",
                                        "anchorings": [{"anchorId": "story",
                                                        "anchoring": "ANCHORED"}]})
    assert score.answered == 1 and score.agreed == 1


# ------------------------------------- keel-cloud 062: options carry no code, joined by position

import json as _json                                                         # noqa: E402

from instructions import corpus as _corpus_mod                               # noqa: E402

GOLDEN = fx.FIXTURES / "calibration"


def _golden(vector):
    return _json.loads((GOLDEN / f"03-lullaby.{vector}.result.json").read_text(encoding="utf-8"))


@pytest.fixture()
def lullaby():
    return _corpus_mod.load_file(fx.CORPUS_R3 / "03-lullaby.yaml", registry=fx.registry())


@pytest.mark.parametrize("vector, count", [("PROBLEM", 9), ("SOLUTION", 9), ("COMMERCIAL", 7)])
def test_the_golden_062_accepts_scores_clean_with_no_code_on_any_option(lullaby, registry, vector,
                                                                         count):
    result = _golden(vector)
    assert not any("normalized" in o for q in result["questions"] for o in q.get("options") or [])
    score = score_mod.score_calibration(fx.calibration_case(lullaby, vector), lullaby, registry,
                                        result, judge=fx.FakeJudge())
    assert score.faults == [], score.faults
    assert (score.coverage_hit, score.validity_hit, score.validity_of) == (count, count, count)
    if vector == "PROBLEM":
        assert (score.leak_clean, score.leak_of) == (9, 9)


def test_a_fixed_code_question_one_option_short_fails_by_position(lullaby, registry):
    result = _golden("PROBLEM")
    next(q for q in result["questions"] if q["key"] == "problem.severity")["options"].pop()
    score = score_mod.score_calibration(fx.calibration_case(lullaby, "PROBLEM"), lullaby,
                                        registry, result, judge=fx.FakeJudge())
    assert [f["key"] for f in score.faults] == ["problem.severity"]
    assert "joined by position" in score.faults[0]["evidence"]


def test_a_stated_code_is_only_a_cross_check_against_its_position(registry):
    dimension = registry.by_key("problem.severity")
    question = fx.calibration_question(dimension)
    assert score_mod.calibration_checks(question, dimension) == []
    question["options"][0]["normalized"] = "very"
    assert any("by position it is 'barely'" in f
               for f in score_mod.calibration_checks(question, dimension))


def test_a_label_only_respondent_answer_takes_the_plans_codes_by_position(entry, registry):
    score = _respond(entry, registry, 1, label_only=True)
    assert score.validity_hit == score.validity_of == 8
    short = _respond(entry, registry, 1, lambda r: _options(r, "problem.consequence").pop(0),
                     label_only=True)
    assert [f["key"] for f in short.faults if f["check"] == "option_validity"] == \
        ["problem.consequence"]
