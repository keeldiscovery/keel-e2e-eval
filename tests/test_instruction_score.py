"""`instructions/score.py` at `MARKS_VERSION` 10 (spec 029 data-model §6; T025, T029, T035, T039,
T040, T042, T043; spec 030 T009-T010, calls 46-47).

Fixtures a person can check by hand: the hand-sized registry slice of twelve and
`09-fixture-r5.yaml` (B2C: eleven calibrated keys, one left out). Every mark has its green half and its
red half here, and every total is summed over its own denominator and never another's -- each
denominator read off the registry and the entry (`_slice`, `_plan`), never typed.
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

def _checks(entry) -> int:
    return len(entry.calibrated_keys()) + len(entry.expected["vector_verdicts"])


def test_score_compare_carries_the_diff_onto_the_case(entry):
    score = _compare(entry)
    assert (score.agreed, score.checks, score.measured) == (_checks(entry), _checks(entry), True)
    assert score.compare_correctness == 1.0


def test_compare_correctness_is_measured_only_when_every_row_was(entry):
    good = _compare(entry)
    bad = score_mod.score_compare(_compare_case(entry), entry,
                                  compare_mod.unmeasured(entry.id, "no engine (keel-cloud 058)"))
    totals = score_mod.totals(compare_scores=[good])
    assert totals["compare_measured"] and totals["compare_correctness"] == 1.0
    assert totals["compare_checks"] == _checks(entry) == 14
    mixed = score_mod.totals(compare_scores=[good, bad])
    assert mixed["compare_measured"] is False and mixed["compare_correctness"] is None
    assert mixed["compare_unmeasured"] == [{"entry": "09-fixture",
                                           "reason": "no engine (keel-cloud 058)"}]
    judged = marks_mod.judge(mixed, marks_mod.load())
    assert judged["compare_correctness"]["measured"] is False


def test_a_disagreeing_engine_is_measured_and_not_met(entry):
    totals = score_mod.totals(compare_scores=[_compare(entry, "disagree")])
    assert totals["compare_agreed"] == _checks(entry) - 2
    assert totals["compare_reported_diffs"] == 1
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


def _slice(entry, registry, vector) -> int:
    """Call 47: the vector's calibrated slice for the entry's persona -- read, never typed."""
    return len(registry.calibrated_slice(vector, entry.b2b()))


@pytest.mark.parametrize("vector, count", [("PROBLEM", 4), ("SOLUTION", 3), ("COMMERCIAL", 4)])
def test_a_good_answer_covers_its_slice_and_meets_every_rule(entry, registry, vector, count):
    assert _slice(entry, registry, vector) == count, "B2C: the b2b_only pair is not calibrated"
    score = _calibrate(entry, registry, vector)
    assert (score.coverage_hit, score.coverage_of, score.coverage_passed) == (count, count, True)
    assert (score.validity_hit, score.validity_of) == (count, count), score.faults
    assert score.faults == []
    if vector == "PROBLEM":
        # Calls 52, 53: Frequency over the framed 7 nights has no model text to sweep.
        assert (score.leak_clean, score.leak_of) == (count - 1, count - 1)
    else:
        assert score.leak_of == 0, "sweep A runs on the PROBLEM vector only"


@pytest.mark.parametrize("name, mutate, words", [
    ("doubled", lambda r: r["questions"].append(copy.deepcopy(r["questions"][1])), "doubled"),
    ("missing", lambda r: r["questions"].pop(2), "missing problem.importance"),
    ("foreign", lambda r: r["questions"].append({"key": "problem.vibes", "question": "?"}),
     "outside the slice problem.vibes"),
    ("out of order", lambda r: r["questions"].insert(0, r["questions"].pop(3)), "out of order"),
])
def test_coverage_is_absolute_and_any_slip_fails_the_case(entry, registry, name, mutate, words):
    score = _calibrate(entry, registry, mutate=mutate)
    assert score.coverage_passed is False and score.coverage_hit == 0, name
    assert any(words in f["evidence"] for f in score.faults if f["check"] == "dimension_coverage")


#: The fixed five-point scale of v10's PROBLEM vector (it was Severity's at v9).
SCALE = "problem.current_solution_satisfaction"
#: The one model-written set a B2C entry calibrates (it was Consequence's, on PROBLEM, at v9).
SET = "commercial.existing_sacrifice"


def _scale_options(r):
    return _q(r, SCALE)["options"]


def _set_options(r):
    return _q(r, SET)["options"]


@pytest.mark.parametrize("name, vector, mutate, words", [
    ("count", "PROBLEM", lambda r: _scale_options(r).pop(), "4 options; the registry fixes 5"),
    ("order", "PROBLEM", lambda r: _scale_options(r).insert(0, _scale_options(r).pop(2)),
     "out of registry order"),
    ("foreign code", "PROBLEM", lambda r: _scale_options(r)[0].__setitem__("normalized", "awful"),
     "not the registry's"),
    ("repeated", "COMMERCIAL", lambda r: _set_options(r).append(
        copy.deepcopy(_set_options(r)[0])), "repeated"),
    ("too few written", "COMMERCIAL", lambda r: _set_options(r).__delitem__(slice(1, 3)),
     "the rule asks 4-6"),
    ("not a slug", "COMMERCIAL", lambda r: _set_options(r)[0].__setitem__(
        "normalized", "Lost Sleep"), "not slugs"),
    ("empty phrase", "PROBLEM", lambda r: _scale_options(r)[1].__setitem__("belief_phrase", " "),
     "no belief_phrase"),
    ("phrase too long", "PROBLEM", lambda r: _scale_options(r)[1].__setitem__(
        "belief_phrase", "x" * 121), "121 characters, longer than 120"),
    ("phrase not sure", "PROBLEM", lambda r: _scale_options(r)[1].__setitem__(
        "belief_phrase", "not sure how bad it is"), "belief_phrase carries a not-sure word"),
    ("not sure", "PROBLEM", lambda r: _scale_options(r)[4].__setitem__("label", "I'm not sure"),
     "not-sure option"),
    ("template", "PROBLEM", lambda r: _q(r, SCALE).__setitem__("belief_template", "x"),
     "{value} exactly once"),
    ("options on numeric", "PROBLEM", lambda r: _q(r, "problem.frequency").__setitem__(
        "options", [{"label": "1", "normalized": "one", "belief_phrase": "one"}]),
     "options on a numeric control"),
    ("numeric spec", "PROBLEM", lambda r: _q(r, "problem.frequency").__setitem__(
        "normalized", {"axis_max": 120}), "numeric spec axis_max"),
    ("no event", "PROBLEM", lambda r: _q(r, "problem.prevalence").pop("event"),
     "E2: Prevalence carries `event`"),
    ("a time word in the event", "PROBLEM", lambda r: _q(r, "problem.prevalence").__setitem__(
        "event", "lost their keys last week"), "E1: 'last' is a time word"),
    ("tick all", "SOLUTION", lambda r: _q(r, "solution.compatibility").__setitem__(
        "question", "When would it fit? Tick all that apply."), "W7: 'Tick all'"),
    ("money", "COMMERCIAL", lambda r: _q(r, "commercial.commitment").__setitem__(
        "question", "Would they pay £3 to try it?"), "W9: '£'"),
    ("options on Price", "COMMERCIAL", lambda r: _q(r, "commercial.price").__setitem__(
        "options", [{"label": "Under £2", "belief_phrase": "under two"}]), "C2:"),
    ("a kind with no unit", "COMMERCIAL", lambda r: _set_options(r)[0].pop("unit"),
     "U1: 'Option 1 for this' is a kind of cost"),
    ("fifths with a hole", "PROBLEM", lambda r: _q(r, "problem.prevalence")["options"][2]
     .__setitem__("normalized", "p_50_60"), "not the registry's"),
])
def test_option_validity_fails_on_each_registry_rule_made_to_fail_once(entry, registry, name,
                                                                       vector, mutate, words):
    score = _calibrate(entry, registry, vector, mutate=mutate)
    validity = [f for f in score.faults if f["check"] == "option_validity"]
    assert len(validity) == 1, (name, score.faults)
    assert words in validity[0]["evidence"], (name, validity[0]["evidence"])
    assert score.validity_hit == score.validity_of - 1



def test_a_belief_phrase_equal_to_its_label_is_accepted(entry, registry):
    # Call 37 (founder decision 32, 2026-10-08): C4 no longer refuses a phrase that repeats its
    # label, case-folded -- keel-cloud 062 accepts it, so the eval does too.
    def same(r):
        for option in _scale_options(r):
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
    assert (score.coverage_hit, score.coverage_of, score.validity_of) == \
        (0, _slice(entry, registry, "PROBLEM"), 0)
    assert score.failed == "schema-invalid"


def test_totals_roll_calibration_into_the_three_marks(entry, registry):
    good = _calibrate(entry, registry)
    bad = _calibrate(entry, registry, mutate=lambda r: r["questions"].pop(2))
    totals = score_mod.totals([good, bad])
    assert totals["calibration_cases"] == 2
    count = _slice(entry, registry, "PROBLEM")
    assert totals["calibration_coverage"] == {"hit": count, "of": 2 * count}
    assert totals["dimension_coverage"] == 0.5
    assert totals["calibration_validity"] == {"hit": 2 * count - 1, "of": 2 * count - 1}
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


@pytest.mark.parametrize("part, count, sweeps", [(1, 4, 6), (2, 3, 3), (3, 3, 2)])
def test_coverage_per_part_is_the_plan_exactly_once_each(entry, registry, part, count, sweeps):
    """Calls 52, 53: Frequency over the framed 7 nights and Price owe no text, so neither is
    swept -- part 1 sweeps three items twice, part 3 two of its three once."""
    assert len(entry.plan()[part]) == count, "the plan, read: 4 / 3 / 4 less the one left out"
    score = _respond(entry, registry, part)
    assert (score.coverage_hit, score.coverage_of) == (count, count)
    assert (score.validity_hit, score.validity_of) == (count, count), score.faults
    assert (score.leak_clean, score.leak_of) == (sweeps, sweeps), \
        "sweep A on Part 1's items, sweep B on every item"


def test_a_label_only_answer_is_held_to_the_count(entry, registry):
    score = _respond(entry, registry, 1, label_only=True)
    assert score.validity_hit == score.validity_of == len(entry.plan()[1]), score.faults


def _options(result, key):
    return _item(result, key)["options"]


@pytest.mark.parametrize("name, part, mutate, words", [
    ("control", 1, lambda r: _item(r, SCALE).__setitem__("control", "single_choice"),
     "control 'single_choice'"),
    ("founder label missing", 3, lambda r: _options(r, SET).pop(0),
     "missing founder label(s) ['spare_keys']"),
    ("one distractor", 3, lambda r: _options(r, SET).pop(),
     "1 distractor(s); a set takes 2 to 3"),
    ("something else written", 3, lambda r: _options(r, SET).append("Something else"),
     "code appends it"),
    ("fixed scale grew", 1, lambda r: _options(r, SCALE).append(
        {"label": "Off the scale", "code": "off_scale"}), "nothing added"),
    ("chips", 1, lambda r: _item(r, SCALE).__setitem__("chips", []), "chips []"),
    ("anchor", 1, lambda r: _item(r, SCALE).__setitem__("anchor", "last_purchase"),
     "anchor 'last_purchase'"),
    ("importance too short", 1, lambda r: _item(r, "problem.importance").__setitem__(
        "options", ["One", "Two", "Three"]), "3 difficulties; Importance takes 4 to 6"),
    ("not sure", 1, lambda r: _options(r, SCALE)[0].__setitem__("label", "Not sure."),
     "not-sure option"),
    ("options on a number", 1, lambda r: _item(r, "problem.frequency").__setitem__(
        "options", ["5", "10"]), "options on a segmented_0_to_7 control"),
    ("options on the gate", 1, lambda r: _item(r, "problem.prevalence").__setitem__(
        "options", ["Yes", "No"]), "options on a gate_yes_no control"),
])
def test_validity_fails_on_each_respondent_rule_made_to_fail_once(entry, registry, name, part,
                                                                  mutate, words):
    score = _respond(entry, registry, part, mutate)
    validity = [f for f in score.faults if f["check"] == "option_validity"]
    assert len(validity) == 1, (name, score.faults)
    assert words in validity[0]["evidence"], (name, validity[0]["evidence"])


# Call 38: code appends, never the model -- the scorer judges the plan's codes less the appended.

def _row(entry, key):
    return entry.respondent_questions[key]


def test_a_fixed_code_control_owes_exactly_one_label_per_founder_code(entry, registry):
    dimension = registry.by_key("solution.relative_advantage")
    row = _row(entry, dimension.key)
    want = [c for c in row["codes"] if c not in ("nothing_would_change", "something_else")]
    item = {"key": dimension.key, "question": "That night?",
            "options": [f"Label {i}" for i in range(len(want))]}
    assert score_mod.respondent_checks(item, dimension, row) == []
    plus_escape = dict(item, options=item["options"] + ["Nothing would have changed"])
    assert any(f"{len(want) + 1} options; the plan has {len(want)}" in f
               for f in score_mod.respondent_checks(plus_escape, dimension, row))
    short = dict(item, options=item["options"][:-1])
    assert score_mod.respondent_checks(short, dimension, row)


@pytest.mark.parametrize("distractors, ok", [(1, False), (2, True), (3, True), (4, False)])
def test_a_set_takes_every_founder_label_and_two_to_three_distractors(entry, registry,
                                                                      distractors, ok):
    from instructions.registry import RESPONDENT_ESCAPES                     # noqa: PLC0415
    dimension = registry.by_key(SET)
    row = _row(entry, dimension.key)
    founder = [c for c in row["codes"] if c not in RESPONDENT_ESCAPES]
    labels = [c.upper() for c in founder] + [f"Distractor {i}" for i in range(distractors)]
    faults = score_mod.respondent_checks({"key": dimension.key, "question": "After?",
                                          "options": labels, "units": ["money"] * len(labels)},
                                         dimension, row)
    assert (faults == []) is ok, faults
    if not ok:
        assert f"{distractors} distractor(s)" in faults[0]


def test_a_set_missing_a_founder_label_fails(entry, registry):
    from instructions.registry import RESPONDENT_ESCAPES                     # noqa: PLC0415
    dimension = registry.by_key(SET)
    row = _row(entry, dimension.key)
    founder = [c for c in row["codes"] if c not in RESPONDENT_ESCAPES]
    labels = founder[1:] + ["Distractor a", "Distractor b"]
    faults = score_mod.respondent_checks({"key": dimension.key, "question": "After?",
                                          "options": labels}, dimension, row)
    assert any(f"missing founder label(s) [{founder[0]!r}]" in f for f in faults), faults


def _canon(name="03-lullaby.yaml"):
    """One of keel-cloud's r4 entries (skipped by name when the canon is not at r4)."""
    from instructions import corpus as corpus_mod                       # noqa: PLC0415
    return corpus_mod.load_file(fx.canon_entry(name), registry=fx.registry())


def _lullaby():
    return _canon()


def test_a_set_is_judged_against_the_founders_labels_not_the_codes(registry):
    lullaby = _lullaby()
    key = "commercial.existing_sacrifice"
    dimension, row = registry.by_key(key), lullaby.respondent_questions[key]
    labels = lullaby.founder_labels(key)
    shown = [label for code, label in labels.items() if code != "nothing"]
    good = {"key": key, "question": "That last thing?",
            "options": [s.upper() + "!" for s in shown] + ["Distractor a", "Distractor b"],
            "units": ["money"] * (len(shown) + 2)}
    assert score_mod.respondent_checks(good, dimension, row, founder_labels=labels) == [], \
        "058's R2 comparison, and the founder's own 'None of these' left to code"
    codes = dict(good, options=[c for c in labels if c != "nothing"] + ["Distractor a"])
    faults = score_mod.respondent_checks(codes, dimension, row, founder_labels=labels)
    assert any("missing founder label(s)" in f for f in faults), faults


def test_the_founders_escape_is_told_by_its_label_whatever_production_slugged_it(registry):
    """Production slugs *None of these* as `none_of_these_<...>`, never the bare `none`: the
    escape row 058 appends is recognised by its LABEL, not a fixed slug."""
    lullaby = _lullaby()
    key = "commercial.existing_sacrifice"
    dimension, row = registry.by_key(key), lullaby.respondent_questions[key]
    labels = {("none_of_these_they_cope" if code == "nothing" else code): label
              for code, label in lullaby.founder_labels(key).items()}
    assert any(score_mod.is_escape_label(label) for label in labels.values())
    shown = [label for label in labels.values() if not score_mod.is_escape_label(label)]
    item = {"key": key, "question": "That last thing?",
            "options": shown[1:] + shown[:1] + ["Distractor a", "Distractor b"]}
    faults = score_mod.respondent_checks(item, dimension, row, founder_labels=labels)
    assert not [f for f in faults if "missing founder label" in f], faults


@pytest.mark.parametrize("label", ["None of these", "None of these; they cope with what they have",
                                   "Nothing", "Nothing yet", "I wouldn't have reached for it at all",
                                   "Something else"])
def test_every_escape_058_appends_is_known_by_its_label(label):
    assert score_mod.is_escape_label(label)
    assert not score_mod.is_escape_label("Nothing on the shelf matched")


def test_a_scale_step_that_begins_with_something_else_is_not_an_escape(registry):
    """Call 44: an escape row the model wrote is told by its WHOLE normalised label, never a
    prefix -- certificate run 3 (`runs/20261008T194906Z-instructions`, 06-repeatline Part 3)
    was faulted on Ability to pay's own scale step (then code `barely`; since r5 the rungs are
    renamed, `taken_from_other_spend` the nearest)."""
    key = "commercial.ability_to_pay"
    dimension, row = registry.by_key(key), _canon("06-repeatline.yaml").respondent_questions[key]
    labels = ["Out of a budget line we already had", "A new line someone signed off",
              "Taken from other spend", "Something else was cut or given up to cover it"]
    item = {"key": key, "question": "Where did the money come from?",
            "options": [{"label": label, "code": code} for label, code in
                        zip(labels, ["existing_line", "new_line_signed_off",
                                     "taken_from_other_spend", "no_budget"])]}
    assert not score_mod.is_escape_label(labels[-1])
    assert score_mod.respondent_checks(item, dimension, row) == []


@pytest.mark.parametrize("label", ["Something else", "something else.", "None of these",
                                   "Nothing yet", "Nothing"])
def test_a_bare_escape_written_on_a_set_is_still_a_fault(entry, registry, label):
    score = _respond(entry, registry, 3, mutate=lambda r: _options(r, SET).append(label))
    assert any("written by the model; code appends it" in f["evidence"] for f in score.faults), \
        score.faults


def test_sweep_a_runs_on_part_one_and_sweep_b_on_every_part(entry, registry):
    leak_a = _respond(entry, registry, 1, lambda r: _item(r, SCALE).__setitem__(
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


def test_a_part_one_mechanism_stem_only_in_an_option_label_is_judged_not_faulted(entry, registry):
    """Call 43: *phone*, *wheel*, *caught* -- a stem offered as an answer goes to the judge."""
    def mutate(r):
        item = next(i for i in r["items"] if i.get("options"))
        _set_option(r, item["key"], 0, "The beep went off")
    judge = fx.FakeJudge(answer=False)
    score = _respond(entry, registry, 1, mutate, judge=judge)
    assert len(judge.calls) == 1
    assert not [f for f in score.faults if f.get("sweep") == "A"]


def test_sweep_b_catches_a_founder_number_the_registry_did_not_fix(entry, registry):
    """At v10 Frequency is the one numeric dimension and its axis (0-7) is the registry's, so a
    founder number outside it is the only one sweep B can catch."""
    dimension = registry.by_key("problem.frequency")
    founder = {"answer": {"lower": 9, "upper": 12, "unit": "days out of 14"}}
    swept = score_mod.sweep_b(["Was it more like 12 days?"], dimension, founder)
    assert swept["fault"] and "12" in swept["evidence"]
    assert not score_mod.sweep_b(["Was it more like 4 nights?"], dimension,
                                 {"answer": {"lower": 2, "upper": 4}})["fault"], \
        "4 is on the registry's own axis"
    window = _respond(entry, registry, 1, lambda r: _item(r, "problem.frequency").__setitem__(
        "question", "On how many of the last 7 nights?"))
    assert not [f for f in window.faults if f["check"] == "no_leak"], \
        "the founder said up to 4 of 7; the 7 is the registry's window"


def _set_option(result, key, index, label):
    option = _item(result, key)["options"][index]
    if isinstance(option, dict):
        option["label"] = label
    else:
        _item(result, key)["options"][index] = label


def test_sweep_b_passes_the_founders_label_in_an_option(entry, registry):
    """Call 40: a fixed-code control shows every rung, the founder's own among them."""
    score = _respond(entry, registry, 2, lambda r: _set_option(
        r, "solution.adoption_friction", 1, "A single whistle"))
    assert not [f for f in score.faults if f["check"] == "no_leak"]


def test_sweep_b_faults_the_founders_label_in_the_stem(entry, registry):
    score = _respond(entry, registry, 2, lambda r: _item(r, "solution.adoption_friction")
                     .__setitem__("question", "Would a single whistle have been too much?"))
    faults = [f for f in score.faults if f["check"] == "no_leak"]
    assert [f["sweep"] for f in faults] == ["B"] and "a single whistle" in faults[0]["evidence"]


def test_sweep_b_faults_the_founders_phrase_in_a_part_one_stem(entry, registry):
    stem = _respond(entry, registry, 1, lambda r: _item(r, SCALE).__setitem__(
        "question", "Would you say the way you handle it is hit and miss?"))
    assert any("is hit and miss" in f["evidence"]
               for f in stem.faults if f.get("sweep") == "B"), stem.faults


def test_sweep_b_never_reads_the_reveal(entry, registry):
    """Call 44b: the reveal is R6's (claim words) and names the mechanism's moment."""
    score = _respond(entry, registry, 2, lambda r: r["reveal"].__setitem__(
        "body", "One idea: a single whistle starts it."))
    assert not [f for f in score.faults if f.get("sweep") == "B"]


def test_a_mechanism_stem_the_registry_itself_words_for_the_dimension_is_no_leak(entry, registry):
    """Call 44a: wording the registry gives the dimension can never be a leak."""
    dimension = registry.by_key(SCALE)
    assert score_mod.text_mod.stem("beep") not in score_mod.registry_stems(registry, dimension)
    faulted = _respond(entry, registry, 1, lambda r: _item(r, SCALE).__setitem__(
        "question", "How bad was it before the beep?"))
    assert [f for f in faulted.faults if f.get("sweep") == "A"]
    dimension.respondent["guidance"] = dimension.respondent.get("guidance", "") + " Until the beep."
    assert score_mod.text_mod.stem("beep") in score_mod.registry_stems(registry, dimension)
    clean = _respond(entry, registry, 1, lambda r: _item(r, SCALE).__setitem__(
        "question", "How bad was it before the beep?"))
    assert not [f for f in clean.faults if f.get("sweep") == "A"], clean.faults


def test_the_registrys_lullaby_example_is_not_registry_wording(registry):
    dimension = registry.by_key(SCALE)
    dimension.lullaby["founder_question"] = "Does the whistle help?"
    assert score_mod.text_mod.stem("whistle") not in score_mod.registry_stems(registry, dimension)


@pytest.mark.parametrize("label, faulted", [
    ("I'm not sure", True), ("Not sure", True), ("Don't know", True), ("I don't know", True),
    ("Unsure", True), ("Prefer not to say", True), ("Not sure it would fit", False),
    ("When working for a new agency they do not know yet", False)])
def test_a_not_sure_option_is_the_whole_label_never_a_substring(entry, registry, label, faulted):
    """Call 44: the whole normalised label against the list (keel-cloud 058's C3 likewise)."""
    score = _respond(entry, registry, 1, lambda r: _options(r, SCALE)[0]
                     .__setitem__("label", label))
    hits = [f for f in score.faults if "not-sure option" in f.get("evidence", "")]
    assert bool(hits) is faulted


def test_the_b2b_link_scores_the_commercial_part_whole_less_the_left_out(registry):
    """Calls 47, 50: COMMERCIAL_B2B asks the commercial six (the b2b_only pair and Price included),
    less the founder's unsure Buyer/payer -- five, read off the plan."""
    b2b = fx.entry(fx.ENTRY_B2B)
    count = len(registry.plan_keys(3, b2b.founder_calibration, "COMMERCIAL_B2B", True))
    assert count == 5 and b2b.plan()[3] == registry.plan_keys(3, b2b.founder_calibration,
                                                              "COMMERCIAL_B2B", True)
    score = _respond(b2b, registry, 3, link="COMMERCIAL_B2B")
    assert (score.coverage_hit, score.coverage_of) == (count, count)
    assert score.validity_hit == count, score.faults
    assert score.link == "COMMERCIAL_B2B" and score.subject == "B2B"


def test_totals_roll_both_question_screens_into_the_same_three_marks(entry, registry):
    totals = score_mod.totals([_calibrate(entry, registry)], [_respond(entry, registry, 1),
                                                              _respond(entry, registry, 2)])
    plan = entry.plan()
    asked = len(plan[1]) + len(plan[2])
    assert totals["respondent_coverage"] == {"hit": asked, "of": asked} == {"hit": 7, "of": 7}
    assert totals["dimension_coverage"] == 1.0
    # Calls 52, 53: Frequency (framed on 7 nights) is swept on neither screen.
    assert totals["calibration_leak"]["of"] + totals["respondent_leak"]["of"] == \
        (len(registry.calibrated_slice("PROBLEM", False)) - 1) + 2 * (len(plan[1]) - 1) \
        + len(plan[2])


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
    return _corpus_mod.load_file(fx.canon_entry("03-lullaby.yaml"), registry=fx.registry())


@pytest.mark.parametrize("vector, count", [("PROBLEM", 4), ("SOLUTION", 3), ("COMMERCIAL", 4)])
def test_the_golden_062_accepts_scores_clean_with_no_code_on_any_option(lullaby, registry, vector,
                                                                         count):
    result = _golden(vector)
    assert not any("normalized" in o for q in result["questions"] for o in q.get("options") or [])
    score = score_mod.score_calibration(fx.calibration_case(lullaby, vector), lullaby, registry,
                                        result, judge=fx.FakeJudge())
    assert score.faults == [], score.faults
    assert (score.coverage_hit, score.validity_hit, score.validity_of) == (count, count, count)
    if vector == "PROBLEM":
        assert (score.leak_clean, score.leak_of) == (count - 1, count - 1)   # Frequency is code's


def test_a_fixed_code_question_one_option_short_fails_by_position(lullaby, registry):
    result = _golden("PROBLEM")
    next(q for q in result["questions"] if q["key"] == SCALE)["options"].pop()
    score = score_mod.score_calibration(fx.calibration_case(lullaby, "PROBLEM"), lullaby,
                                        registry, result, judge=fx.FakeJudge())
    assert [f["key"] for f in score.faults] == [SCALE]
    assert "joined by position" in score.faults[0]["evidence"]


def test_a_stated_code_is_only_a_cross_check_against_its_position(registry):
    dimension = registry.by_key(SCALE)
    question = fx.calibration_question(dimension)
    assert score_mod.calibration_checks(question, dimension) == []
    question["options"][0]["normalized"] = "hit_and_miss"
    assert any("by position it is 'works_well'" in f
               for f in score_mod.calibration_checks(question, dimension))


def test_a_label_only_respondent_answer_takes_the_plans_codes_by_position(entry, registry):
    score = _respond(entry, registry, 1, label_only=True)
    assert score.validity_hit == score.validity_of == len(entry.plan()[1])
    short = _respond(entry, registry, 3, lambda r: _options(r, SET).pop(0), label_only=True)
    assert [f["key"] for f in short.faults if f["check"] == "option_validity"] == [SET]
