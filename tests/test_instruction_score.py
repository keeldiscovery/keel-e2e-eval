"""`instructions/score.py` at `MARKS_VERSION` 18 (spec 029 data-model §6; spec 030 calls 46-47; spec 040, judgement
calls 77-85).

Fixtures a person can check by hand: the hand-sized registry slice (registry 4) and `09-fixture.yaml` (B2C: twelve
calibrated keys, Buyer and payer left out) with its B2B twin. Since keel-cloud 087 / 088 the model writes no question:
the founder-lists job writes Prevalence's clause and fifths and every list dimension's draft (call 85), the respondent
job the gate's clause (call 83), the `ASKED` job a face a list item (call 84). Every mark has its green half and its
red half here, and every total is summed over its own denominator and never another's -- each denominator read off
the registry and the entry (`_slice`, the plan, the items handed), never typed.
"""

from __future__ import annotations

import copy
import json

import pytest

from instructions import compare as compare_mod
from instructions import corpus as corpus_mod
from instructions import marks as marks_mod
from instructions import prompts as prompts_mod
from instructions import spoken as spoken_mod
from instructions import brief_facts as brief_facts_mod
from instructions import score as score_mod
from tests import v9_fixtures as fx


@pytest.fixture()
def entry():
    return fx.entry()


@pytest.fixture()
def b2b_entry():
    """The B2B twin: Purchase friction calibrated and its two steps listed; part 3 the decision-maker's link."""
    return fx.entry(fx.ENTRY_B2B)


@pytest.fixture()
def registry():
    return fx.registry()


def _compare_case(entry):
    return prompts_mod.Case(case_id=f"{entry.id}/COMPARE", kind="COMPARE", entry_id=entry.id,
                            screen="COMPARE", subject="COMPARE", run_index=0, payload={})


def _compare(entry, name="agree"):
    produced = json.loads((fx.COMPARE / f"09-fixture.{name}.out.json").read_text())
    return score_mod.score_compare(_compare_case(entry), entry,
                                   compare_mod.diff(entry.expected, produced, entry=entry))


def _checks(entry) -> int:
    """All thirteen decide (call 77): one check a calibrated dimension and one a vector."""
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
    assert totals["compare_checks"] == _checks(entry) == 15
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

def test_totals_carries_every_v20_key_and_nothing_retired():
    totals = score_mod.totals()
    for key in ("calibration_cases", "calibration_coverage", "calibration_validity",
                "calibration_leak", "respondent_cases", "respondent_coverage",
                "respondent_validity", "respondent_leak", "asked_cases", "asked_coverage", "asked_validity",
                "dimension_coverage", "option_validity",
                "no_leak", "leak_hits", "leak_judged", "judged_fraction", "judge_calls",
                "anchoring_accuracy", "guessed_precision", "guessed_recall", "confusion",
                "people_given", "people_answered", "reading_missing_ids", "reading_extra_ids",
                "chipped_skipped", "compare_checks", "compare_agreed", "compare_correctness",
                "compare_measured", "compare_reported_diffs", "spoken_form", "spoken_measured",
                "spoken_units", "spoken_clean", "spoken_known", "spoken_unmeasured", "brief_facts",
                "brief_facts_checks", "brief_facts_agreed", "brief_facts_measured", "brief_facts_reported_diffs",
                "brief_facts_unmeasured", "report_overview", "report_overview_checks", "report_overview_agreed",
                "report_overview_measured", "report_overview_unmeasured", "refusals_by_rule",
                "refusals_measured", "refusals_shown", "shape_refusals", "schema_invalid",
                "errored"):
        assert key in totals, key
    for retired in ("golden_belief_recall", "exact_match", "phrase_band", "anchors_given",
                    "unresolved_reads", "brief_paragraphs", "wording", "brief_cases", "brief_answers",
                    "brief_measured", "brief_by_mark", "brief_needs_input"):
        assert retired not in totals, retired


def test_an_empty_run_measures_nothing_and_says_none_rather_than_zero():
    totals = score_mod.totals()
    for name in ("dimension_coverage", "option_validity", "no_leak", "anchoring_accuracy",
                 "compare_correctness", "spoken_form", "brief_facts", "report_overview"):
        assert totals[name] is None, name


def test_the_spread_reports_each_run_and_averages_nothing():
    from types import SimpleNamespace
    scores = [SimpleNamespace(entry_id="e", subject="PROBLEM", value=v) for v in (1.0, 0.0, 1.0)]
    spread = score_mod.spread(scores, lambda s: s.value)
    assert spread == {"e/PROBLEM": {"runs": [1.0, 0.0, 1.0], "min": 0.0, "max": 1.0}}


def test_the_retired_scorers_are_gone():
    """Calls 29, 83: the assumption scorers, and the model-written option and wording checks."""
    for name in ("score_assumptions", "score_reading", "AssumptionScore", "FIELDS", "model_text",
                 "WORDING_KEYS", "wording_totals", "is_escape_label", "ESCAPE_LABELS", "_ladder_codes",
                 "_named_faults", "_question_texts"):
        assert not hasattr(score_mod, name), name


def test_report_overview_reaches_the_totals_measured_or_not(entry):
    """Call 117: `report_overview` is measured at zero spend; an unmeasured one says why."""
    from instructions import overview as overview_mod                    # noqa: PLC0415
    unmeasured = score_mod.totals(overview_scores=[overview_mod.unmeasured(entry.id, "no facts")])
    assert unmeasured["report_overview"] is None
    assert unmeasured["report_overview_unmeasured"] == [{"entry": entry.id, "reason": "no facts"}]
    score = overview_mod.compare(entry, fx_registry(), None)
    assert score.measured is False and "no brief facts" in score.reason
    agreed = overview_mod.FactsCompare(entry.id)
    agreed.checks, agreed.agreed = 7, 6
    measured = score_mod.totals(overview_scores=[agreed])
    assert (measured["report_overview"], measured["report_overview_checks"]) == (6 / 7, 7)
    assert marks_mod.judge(measured, marks_mod.load())["report_overview"]["met"] is False


def fx_registry():
    from tests import v9_fixtures as fx                                     # noqa: PLC0415
    return fx.registry()


def test_the_two_deterministic_marks_reach_the_totals_measured_or_not(entry, registry):
    """Calls 79, 82: `spoken_form` and `brief_facts` are measured at zero spend, and an unmeasured one says why."""
    unmeasured = score_mod.totals(spoken_score=spoken_mod.unmeasured("no gradlew"),
                                  facts_scores=[brief_facts_mod.unmeasured(entry.id, "no facts")])
    assert unmeasured["spoken_form"] is None and unmeasured["spoken_unmeasured"] == "no gradlew"
    assert unmeasured["brief_facts"] is None
    assert unmeasured["brief_facts_unmeasured"] == [{"entry": entry.id, "reason": "no facts"}]
    judged = marks_mod.judge(unmeasured, marks_mod.load())
    assert judged["spoken_form"]["measured"] is False and judged["brief_facts"]["measured"] is False
    spoken = spoken_mod.SpokenScore(units=4, clean=3, measured=True)
    facts = brief_facts_mod.FactsCompare(entry.id)
    facts.checks, facts.agreed = 14, 14
    measured = score_mod.totals(spoken_score=spoken, facts_scores=[facts])
    assert (measured["spoken_form"], measured["spoken_units"], measured["spoken_clean"]) == (0.75, 4, 3)
    assert (measured["brief_facts"], measured["brief_facts_checks"]) == (1.0, 14)
    judged = marks_mod.judge(measured, marks_mod.load())
    assert judged["spoken_form"]["met"] is False and judged["brief_facts"]["met"] is True


# --------------------------------------------- calibration: the founder-lists job (calls 30-32, 85)

def _calibrate(entry, registry, vector="PROBLEM", mutate=None, judge=None):
    result = fx.calibration_result(registry, vector, b2b=entry.b2b())
    if mutate:
        mutate(result)
    return score_mod.score_calibration(fx.calibration_case(entry, vector), entry, registry,
                                       result, judge=judge)


def _q(result, key):
    return next(q for q in result["questions"] if q["key"] == key)


def _items(result, key):
    return _q(result, key)["list"]["items"]


def _slice(entry, registry, vector) -> int:
    """Calls 47, 61: the vector's answered slice for the entry's persona -- read, never typed."""
    return len(registry.answered_slice(vector, entry.b2b()))


@pytest.mark.parametrize("vector, count", [("PROBLEM", 4), ("SOLUTION", 3), ("COMMERCIAL", 4)])
def test_a_good_answer_covers_its_slice_and_meets_every_rule(entry, registry, vector, count):
    assert _slice(entry, registry, vector) == count, "B2C: Purchase friction is not calibrated, Ability to pay is derived"
    score = _calibrate(entry, registry, vector)
    assert (score.coverage_hit, score.coverage_of, score.coverage_passed) == (count, count, True)
    assert (score.validity_hit, score.validity_of) == (count, count), score.faults
    assert score.faults == []
    if vector == "PROBLEM":
        # Frequency writes nothing a reader is shown: Prevalence and the two lists are swept.
        assert (score.leak_clean, score.leak_of) == (count - 1, count - 1)
    else:
        assert score.leak_of == 0, "sweep A runs on the PROBLEM vector only"


@pytest.mark.parametrize("name, mutate, words", [
    ("doubled", lambda r: r["questions"].append(copy.deepcopy(r["questions"][1])), "doubled"),
    ("missing", lambda r: r["questions"].pop(2), "missing problem.importance"),
    ("foreign", lambda r: r["questions"].append({"key": "problem.vibes", "respondent_note": "?"}),
     "outside the slice problem.vibes"),
    ("out of order", lambda r: r["questions"].insert(0, r["questions"].pop(3)), "out of order"),
])
def test_coverage_is_absolute_and_any_slip_fails_the_case(entry, registry, name, mutate, words):
    score = _calibrate(entry, registry, mutate=mutate)
    assert score.coverage_passed is False and score.coverage_hit == 0, name
    assert any(words in f["evidence"] for f in score.faults if f["check"] == "dimension_coverage")


IMPORTANCE = "problem.importance"
CURRENT = "problem.current_solution_satisfaction"
COMPAT = "solution.compatibility"
ADOPTION = "solution.adoption_friction"
GATE = "problem.prevalence"


def _set(key, index, field, value):
    return lambda r: _items(r, key)[index].__setitem__(field, value)


@pytest.mark.parametrize("name, vector, mutate, words", [
    # L1: the count, the phrase, the list itself
    ("importance four", "PROBLEM", lambda r: _items(r, IMPORTANCE).pop(), "L1: problem.importance takes exactly 5"),
    ("no phrase", "PROBLEM", lambda r: _q(r, CURRENT)["list"].__setitem__("phrase", " "),
     "L1: Current solution carries the phrase today's way is asked by"),    # spec 093 FR-3: 161's words
    ("a phrase in Keel's words", "PROBLEM", lambda r: _q(r, CURRENT)["list"].__setitem__(
        "phrase", "your way of finding them"), "L1: 'your way of finding them' opens on 'your way of'"),
    ("no list", "SOLUTION", lambda r: _q(r, COMPAT).pop("list"), "write its draft list"),
    ("options on a list", "SOLUTION", lambda r: _q(r, ADOPTION).__setitem__(
        "options", [{"label": "Clip it", "belief_phrase": "clip"}]), "never options"),
    ("five conditions", "SOLUTION", lambda r: _items(r, COMPAT).extend(
        copy.deepcopy(_items(r, COMPAT)[:1]) * 3), "takes 2 to 4 items"),
    ("three steps", "COMMERCIAL", lambda r: _items(r, "commercial.commitment").extend(
        [{"label": "pay for it"}, {"label": "sign for it"}]), "takes 1 to 2 items"),
    ("three roles", "COMMERCIAL", lambda r: _items(r, "commercial.buyer_payer_alignment").extend(
        [{"label": "The owner"}, {"label": "Finance"}]), "takes 0 to 2 items besides Nobody else"),
    # L2: words an item (roles four)
    ("a long rival", "PROBLEM", _set(IMPORTANCE, 2, "label", "Riding in the wet weather on the way into work today"),
     "L2: item 3 is 1 to 9 words"),
    ("a long role", "COMMERCIAL", _set("commercial.buyer_payer_alignment", 0, "label",
                                       "The manager of the whole office"), "L2: item 1 is 1 to 4 words"),
    # L3: no number the founder did not write
    ("an invented number", "SOLUTION", _set(COMPAT, 1, "label", "Their 3 keys were on one ring"),
     "L3: '3' in item 2 is a number the founder did not write"),
    # L4 and the K rules on a drafted face (call 85)
    ("no face", "SOLUTION", _set(ADOPTION, 0, "asked", ""), "L4: item 1 carries the stranger's clause"),
    ("a question mark", "SOLUTION", _set(COMPAT, 0, "asked", "did you have your phone to hand?"), "L4:"),
    ("not to the stranger", "SOLUTION", _set(COMPAT, 0, "asked", "did the phone sit within reach"), "K3:"),
    ("framed too long", "SOLUTION", _set(ADOPTION, 0, "asked",
                                         "you'd clip a small tag to your key ring once and then whistle for "
                                         "it every morning before work"), "K2: framed"),
    # L5: one suggested item, on Purchase friction and Compatibility only (spec 093 FR-3: keel-cloud 121 FR-3; the
    # harness said Purchase friction only) -- never on Adoption friction
    ("a suggested effort", "SOLUTION", _set(ADOPTION, 0, "suggested", True), "L5: item 1"),
    ("two suggested conditions", "SOLUTION", lambda r: [_items(r, COMPAT)[i].__setitem__("suggested", True)
                                                        for i in (0, 1)], "L5: item 2"),
    # C3 and W9 on a list
    ("a not-sure rival", "PROBLEM", _set(IMPORTANCE, 4, "label", "Not sure"), "C3:"),
    ("money in an outcome", "PROBLEM", _set(CURRENT, 1, "label", "Lost five pounds on a taxi, £5"), "W9:"),
    # Prevalence: the clause and the five fifths (E1-E3, C2-C4)
    ("no event", "PROBLEM", lambda r: _q(r, GATE).pop("event"), "E2: Prevalence carries `event`"),
    ("a time word in the event", "PROBLEM", lambda r: _q(r, GATE).__setitem__(
        "event", "lost their keys last week"), "E1: 'last' is a time word"),
    ("four fifths", "PROBLEM", lambda r: _q(r, GATE)["options"].pop(), "C2: 4 options; the registry fixes 5"),
    ("empty phrase", "PROBLEM", lambda r: _q(r, GATE)["options"][1].__setitem__("belief_phrase", " "),
     "no belief_phrase"),
    ("phrase too long", "PROBLEM", lambda r: _q(r, GATE)["options"][1].__setitem__("belief_phrase", "x" * 121),
     "121 characters, longer than 120"),
    ("phrase not sure", "PROBLEM", lambda r: _q(r, GATE)["options"][1].__setitem__(
        "belief_phrase", "not sure how many"), "belief_phrase carries a not-sure word"),
    ("a not-sure fifth", "PROBLEM", lambda r: _q(r, GATE)["options"][4].__setitem__("label", "I'm not sure"),
     "not-sure option"),
    # the code-written entries owe their key alone
    ("options on Frequency", "PROBLEM", lambda r: _q(r, "problem.frequency").__setitem__(
        "options", [{"label": "1", "belief_phrase": "one"}]), "C2: 1 options on Frequency"),
    ("a list on Frequency", "PROBLEM", lambda r: _q(r, "problem.frequency").__setitem__(
        "list", {"items": [{"label": "Most nights"}]}), "L1: problem.frequency is no list"),
    ("options on Price", "COMMERCIAL", lambda r: _q(r, "commercial.price").__setitem__(
        "options", [{"label": "Under two pounds", "belief_phrase": "under two"}]), "C2:"),
])
def test_option_validity_fails_on_each_rule_made_to_fail_once(entry, b2b_entry, registry, name, vector, mutate,
                                                               words):
    entry = b2b_entry if vector == "COMMERCIAL" else entry
    score = _calibrate(entry, registry, vector, mutate=mutate)
    validity = [f for f in score.faults if f["check"] == "option_validity"]
    assert len(validity) == 1, (name, score.faults)
    assert words in validity[0]["evidence"], (name, validity[0]["evidence"])
    assert score.validity_hit == score.validity_of - 1


def test_one_suggested_step_is_allowed_on_purchase_friction_and_a_second_is_not(b2b_entry, registry):
    """L5: the good B2B draft already tags one step suggested."""
    assert _calibrate(b2b_entry, registry, "COMMERCIAL").faults == []
    score = _calibrate(b2b_entry, registry, "COMMERCIAL",
                       _set("commercial.purchase_friction", 0, "suggested", True))
    assert any("L5: item 2" in f["evidence"] for f in score.faults)


def test_one_suggested_condition_is_allowed_on_compatibility(entry, registry):
    """Spec 093 FR-3 (keel-cloud 121 FR-3, the cloud's L5): the condition most likely to be missing is marked on
    Compatibility -- the founder-lists screen of 2026-10-29 faulted the Lullaby listening item for it."""
    assert _calibrate(entry, registry, "SOLUTION", _set(COMPAT, 0, "suggested", True)).faults == []


def test_a_drafted_face_is_held_to_its_own_labels_digits(entry, registry):
    """Call 85, K4: a face may carry a number only where its label does."""
    def numbered(r):
        item = _items(r, ADOPTION)[0]
        item["label"], item["asked"] = "Clip 7 tags to the key ring", "you'd clip 7 tags to your key ring, once"
    assert _calibrate(entry, registry, "SOLUTION", numbered).faults == [], "7 is the window's, so L3 allows it too"


def test_a_belief_phrase_equal_to_its_label_is_accepted(entry, registry):
    # Call 37 (founder decision 32, 2026-10-08): C4 does not refuse a phrase that repeats its label, case-folded.
    def same(r):
        for option in _q(r, GATE)["options"]:
            option["belief_phrase"] = str(option["label"]).upper()
    score = _calibrate(entry, registry, mutate=same)
    assert not [f for f in score.faults if f["check"] == "option_validity"], score.faults


def test_a_question_written_on_a_list_is_not_read(entry, registry):
    """keel-cloud 087: a list dimension's question is code's Answer prompt; one written anyway is never a fault."""
    score = _calibrate(entry, registry, "SOLUTION",
                       lambda r: _q(r, COMPAT).__setitem__("question", "Tick all that apply. £5?"))
    assert score.faults == []


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


@pytest.fixture()
def lullaby():
    return corpus_mod.load_file(fx.canon_entry("03-lullaby.yaml"), registry=fx.registry())


def _drafted_from(entry, registry, vector) -> dict:
    """The corpus's own founder answers, as the founder-lists job would have drafted them."""
    questions = []
    for d in registry.answered_slice(vector, entry.b2b()):
        if d.key == GATE:
            questions.append(fx.calibration_question(d) | {"event": "had to work out why their baby was crying"})
        elif d.founder_list:
            saved = entry.founder_list(d.key) or {}
            items = [{k: i[k] for k in ("label", "asked") if k in i} for i in saved.get("items") or []
                     if i.get("code") != "nobody_else"]
            # spec 093 FR-3 (keel-cloud 161): the job drafts the act bare -- the stored *your way of ...* read bare
            phrase = score_mod._YOUR_WAY_OF.sub("", saved.get("phrase") or "").strip()
            draft = {"items": items} | ({"phrase": phrase} if phrase else {})
            questions.append({"key": d.key, "list": draft, "respondent_note": "x"})
        else:
            questions.append({"key": d.key, "respondent_note": "x"})
    return {"vector": vector, "questions": questions}


@pytest.mark.parametrize("vector", ["PROBLEM", "SOLUTION", "COMMERCIAL"])
def test_the_corpus_lists_as_a_draft_score_clean(lullaby, registry, vector):
    """Calls 85, 112: Lullaby's own lists meet every L rule and, at revision 11, every face the K rules too -- *was the
    room quiet enough for your phone to hear the cry* says *your* (keel-cloud 091, DRIFT #77 closed)."""
    score = score_mod.score_calibration(fx.calibration_case(lullaby, vector), lullaby, registry,
                                        _drafted_from(lullaby, registry, vector), judge=fx.FakeJudge())
    assert score.faults == [], score.faults
    assert spoken_mod.KNOWN == ()


# --------------------------------------------- respondent: the gate's clause (calls 30-32, 83)

def _respond(entry, registry, part, mutate=None, *, link="PRIMARY", judge=None):
    result = fx.respondent_result(entry, part, link=link)
    if mutate:
        mutate(result)
    return score_mod.score_respondent(fx.respondent_case(entry, part, link=link), entry,
                                      registry, entry.plan(), result, judge=judge)


def _item(result, key):
    return next(i for i in result["items"] if i["key"] == key)


@pytest.mark.parametrize("part, count, gate, sweeps", [(1, 4, 1, 2), (2, 3, 0, 0), (3, 3, 0, 0)])
def test_coverage_per_part_is_the_plan_and_validity_the_gate_alone(entry, registry, part, count, gate, sweeps):
    """Call 83: coverage is one `{key}` a planned item; validity and both sweeps read the gate's clause only."""
    assert len(entry.plan()[part]) == count, "the plan, read: 4 / 3 / 4 less the one left out"
    score = _respond(entry, registry, part)
    assert (score.coverage_hit, score.coverage_of) == (count, count)
    assert (score.validity_hit, score.validity_of) == (gate, gate), score.faults
    assert (score.leak_clean, score.leak_of) == (sweeps, sweeps)


@pytest.mark.parametrize("name, mutate, words", [
    ("doubled", lambda r: r["items"].append({"key": "problem.frequency"}), "doubled"),
    ("missing", lambda r: r["items"].pop(1), "missing problem.frequency"),
    ("foreign", lambda r: r["items"].append({"key": "commercial.price"}), "outside the slice commercial.price"),
    ("out of order", lambda r: r["items"].insert(0, r["items"].pop(3)), "out of order"),
])
def test_respondent_coverage_is_absolute(entry, registry, name, mutate, words):
    score = _respond(entry, registry, 1, mutate)
    assert score.coverage_passed is False, name
    assert any(words in f["evidence"] for f in score.faults if f["check"] == "dimension_coverage")


@pytest.mark.parametrize("event, rule", [
    (None, "E2"), ("lose your keys last night", "E1"), ("lose 3 keys", "E1"),
    ("did you lose your keys", "E3"),
    ("have to search the whole flat for your keys before you can leave for work", "E4"),
    ("lose a spare that cost GBP", "W9")])
def test_the_gate_clause_fails_each_rule_once(entry, registry, event, rule):
    def mutate(r):
        gate = _item(r, GATE)
        if event is None:
            gate.pop("event")
        else:
            gate["event"] = event
    score = _respond(entry, registry, 1, mutate)
    validity = [f for f in score.faults if f["check"] == "option_validity"]
    assert len(validity) == 1 and validity[0]["evidence"].startswith(rule + ":"), score.faults
    assert (score.validity_hit, score.validity_of) == (0, 1)


def test_anything_written_on_another_item_is_not_read(entry, registry):
    """keel-cloud 088 FR-002: a `question` or `options` on any item but the gate is not read, never a fault."""
    def written(r):
        for item in r["items"]:
            if item["key"] != GATE:
                item.update(question="Tick all that apply. £5?", options=["A distractor"], event="x")
    for part in (1, 2, 3):
        assert _respond(entry, registry, part, written).faults == [], part


def test_the_b2b_link_covers_the_commercial_part_whole_less_the_left_out(b2b_entry, registry):
    plan = b2b_entry.plan()[3]
    assert plan == ["commercial.existing_sacrifice", "commercial.price", "commercial.ability_to_pay",
                    "commercial.purchase_friction", "commercial.commitment"]
    score = _respond(b2b_entry, registry, 3, link="COMMERCIAL_B2B")
    assert (score.coverage_hit, score.coverage_of, score.validity_of, score.leak_of) == (5, 5, 0, 0)


def test_totals_roll_every_screen_into_the_same_three_marks(entry, registry):
    calibration = _calibrate(entry, registry)
    respondent = [_respond(entry, registry, p) for p in (1, 2, 3)]
    asked = score_mod.score_asked(fx.asked_case(entry), entry, registry, fx.asked_result(entry))
    totals = score_mod.totals([calibration], respondent, asked_scores=[asked])
    plan = entry.plan()
    assert totals["dimension_coverage"] == 1.0 and totals["option_validity"] == 1.0
    assert totals["calibration_coverage"]["of"] + totals["respondent_coverage"]["of"] \
        + totals["asked_coverage"]["of"] == 4 + sum(len(v) for v in plan.values()) + 2
    assert totals["respondent_validity"]["of"] == 1 and totals["asked_validity"]["of"] == 2
    assert totals["calibration_leak"]["of"] + totals["respondent_leak"]["of"] == 3 + 2


# ---------------------------------------------------------------- ASKED: the faces (calls 84, 85)

def _ask(entry, registry, mutate=None, key=COMPAT):
    result = fx.asked_result(entry, key)
    if mutate:
        mutate(result)
    return score_mod.score_asked(fx.asked_case(entry, key), entry, registry, result)


@pytest.mark.parametrize("key, count", [(COMPAT, 2), (ADOPTION, 1)])
def test_the_corpus_faces_cover_every_index_and_keep_every_k_rule(entry, registry, key, count):
    score = _ask(entry, registry, key=key)
    assert (score.coverage_hit, score.coverage_of, score.validity_hit, score.validity_of) == \
        (count, count, count, count), score.faults


@pytest.mark.parametrize("name, mutate, words", [
    ("a foreign index", lambda r: r["items"].append({"index": 7, "asked": "did you"}), "K1: [7] are not indices"),
    ("phrased twice", lambda r: r["items"].append(dict(r["items"][0])), "K1: [0] phrased twice"),
    ("one missing", lambda r: r["items"].pop(), "K1: [1] not phrased"),
])
def test_k1_is_every_index_handed_once_and_no_other(entry, registry, name, mutate, words):
    score = _ask(entry, registry, mutate)
    assert score.coverage_passed is False and score.coverage_hit == 0, name
    assert any(words in f["evidence"] for f in score.faults if f["check"] == "dimension_coverage"), score.faults


@pytest.mark.parametrize("asked, rule", [
    ("did the phone sit within reach", "K3"), ("did you have your 2 phones to hand", "K4"),
    ("did you have your phone to hand?", "K6"), ("", "K2"),
    (" ".join(["you"] * 21), "K2")])
def test_each_k_rule_fails_once_for_its_own_reason(entry, registry, asked, rule):
    score = _ask(entry, registry, lambda r: r["items"][0].__setitem__("asked", asked))
    validity = [f for f in score.faults if f["check"] == "option_validity"]
    assert len(validity) == 1 and validity[0]["evidence"].startswith(rule + ":"), score.faults
    assert validity[0]["key"] == f"{COMPAT}[0]"
    assert (score.validity_hit, score.validity_of) == (1, 2)


def test_an_adoption_face_framed_past_twenty_words_is_k2(entry, registry):
    long = "you'd clip a small tag to your key ring once and then whistle for it every morning"
    score = _ask(entry, registry, lambda r: r["items"][0].__setitem__("asked", long), key=ADOPTION)
    assert any("K2: framed" in f["evidence"] for f in score.faults)


def test_a_failed_asked_case_covers_nothing(entry, registry):
    score = score_mod.score_asked(fx.asked_case(entry), entry, registry, None, failed="schema-invalid")
    assert (score.coverage_hit, score.coverage_of, score.validity_of) == (0, 2, 0)


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
