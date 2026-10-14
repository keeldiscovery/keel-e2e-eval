"""Cost first, held by code (spec 032 US3; judgement calls 59-67; keel-cloud 074 / 077) -- at `MARKS_VERSION` 18
(spec 040, calls 83, 85).

The two money questions are code's -- Existing sacrifice asks *What does it cost ... today?* of the founder and
*{Last month}, what did it cost ...?* of the buyer, Price *What price do you have in mind ...?* -- so the founder-lists
job owes each its key (and a note) and nothing else, and Ability to pay (derived) is not in that job at all. Since
keel-cloud 088 every respondent item but the gate is code's whole, the cost total and Ability to pay's four budget
sources among them. Stackless and modelless: the hand-sized fixtures, never keel-cloud.
"""

from __future__ import annotations

import pytest

from instructions import context as context_mod
from instructions import score as score_mod
from instructions import wording as wording_mod
from tests import v9_fixtures as fx

SACRIFICE = "commercial.existing_sacrifice"
ABILITY = "commercial.ability_to_pay"


@pytest.fixture()
def registry():
    return fx.registry()


@pytest.fixture()
def entry():
    return fx.entry()


def _calibrate(entry, registry, vector, mutate=None):
    result = fx.calibration_result(registry, vector, b2b=entry.b2b())
    if mutate:
        mutate(result)
    return score_mod.score_calibration(fx.calibration_case(entry, vector), entry, registry, result)


# ------------------------------------------------- the calibration side: the key and the note, no kinds

@pytest.mark.parametrize("key", [SACRIFICE, "commercial.price"])
def test_the_money_entries_owe_their_key_and_nothing_else(registry, key):
    """Calls 53, 67: no options, no unit, no question -- the entry is the key and the note."""
    dimension = registry.by_key(key)
    question = fx.calibration_question(dimension)
    assert set(question) == {"key", "respondent_note"}
    assert score_mod.calibration_checks(question, dimension) == []


def test_a_question_the_model_wrote_anyway_is_not_read(registry):
    """Never a fault: keel-cloud sets it aside (`withQuestion(null)`)."""
    sacrifice = registry.by_key(SACRIFICE)
    question = dict(fx.calibration_question(sacrifice), question="What does it cost? Tick all that apply.")
    assert score_mod.calibration_checks(question, sacrifice) == []


@pytest.mark.parametrize("options", [
    [{"label": "Spare keys", "unit": "money"}],
    [{"label": f"Kind {i}", "belief_phrase": "x"} for i in range(5)],
])
def test_any_option_on_existing_sacrifice_is_c2_as_on_price(registry, options):
    """Call 67 (keel-cloud 077): options are refused with C2, like Price's."""
    sacrifice = registry.by_key(SACRIFICE)
    question = dict(fx.calibration_question(sacrifice), options=options)
    faults = score_mod.calibration_checks(question, sacrifice)
    assert len(faults) == 1 and faults[0].startswith(f"C2: {len(options)} options on Existing sacrifice")


def test_money_in_the_event_is_still_w9_on_existing_sacrifice(registry):
    """`ScreenResultApplier.refuseMoney` reads every entry's event and options."""
    sacrifice = registry.by_key(SACRIFICE)
    question = dict(fx.calibration_question(sacrifice), event="spent £5 on a spare")
    assert any(f.startswith("W9:") for f in score_mod.calibration_checks(question, sacrifice))


def test_a_list_on_a_money_entry_is_l1(registry):
    """Call 85: a draft is written only for the seven list dimensions."""
    price = registry.by_key("commercial.price")
    question = dict(fx.calibration_question(price), list={"items": [{"label": "About five pounds"}]})
    assert score_mod.calibration_checks(question, price)[0].startswith("L1:")


def test_ability_to_pay_is_not_in_the_job_and_the_denominator_is_the_answered_set(entry, registry):
    good = _calibrate(entry, registry, "COMMERCIAL")
    assert (good.coverage_of, good.coverage_hit, good.validity_of) == (4, 4, 4)
    assert [q["key"] for q in fx.calibration_result(registry, "COMMERCIAL")["questions"]] == [
        SACRIFICE, "commercial.price", "commercial.buyer_payer_alignment", "commercial.commitment"]

    def include_ability(result):
        assert registry.by_key(ABILITY).derived
        result["questions"].insert(2, {"key": ABILITY, "respondent_note": "x"})
    bad = _calibrate(entry, registry, "COMMERCIAL", include_ability)
    assert bad.coverage_passed is False
    assert any("outside the slice commercial.ability_to_pay" in f["evidence"] for f in bad.faults)


def test_the_b2b_job_is_five_answered_and_still_has_purchase_friction():
    b2b = fx.entry(fx.ENTRY_B2B)
    registry = fx.registry()
    score = _calibrate(b2b, registry, "COMMERCIAL")
    assert (score.coverage_of, score.coverage_hit, score.validity_hit) == (5, 5, 5)
    assert "commercial.purchase_friction" in [d.key for d in registry.answered_slice("COMMERCIAL", True)]


def test_neither_side_sweeps_the_money_entries(registry):
    """Call 83: code writes every word of them, so nothing the model wrote is swept."""
    for key in (SACRIFICE, "commercial.price", ABILITY):
        dimension = registry.by_key(key)
        assert not score_mod.is_swept(dimension) and not score_mod.is_swept(dimension, founder=False)


# ------------------------------------------------------ the respondent side: the key alone

@pytest.mark.parametrize("period, words", [
    ("day", "last week"), ("week", "last week"), ("month", "last month"),
    ("quarter", "the last three months"), ("year", "the last three months"),
    (None, "the last three months")])
def test_the_recall_words_follow_the_founders_cost_period(period, words):
    """`Period.recallWords`: a day is asked over a week, a year over three months, no estimate over three months."""
    assert wording_mod.recall_words(period) == words


@pytest.mark.parametrize("key", [SACRIFICE, ABILITY, "commercial.price"])
def test_the_respondent_item_is_the_key_alone(registry, key):
    """Calls 67, 83: whatever question, options or units a model writes for a code-written item is not read."""
    dimension = registry.by_key(key)
    written = {"key": key, "question": "What did the keys cost you in the last three months?",
               "options": ["Taxis", "Bus fares"], "units": [None, "days"]}
    assert score_mod.respondent_checks(written, dimension) == []
    assert not hasattr(wording_mod, "recall_fault") and not hasattr(score_mod, "UNITS")


def test_the_context_names_the_recall_words_the_job_is_handed_filled(entry, registry):
    """Call 62: `{cost_period}` is filled on every respondent item with the founder's recall words."""
    assert context_mod.cost_recall_of(entry) == "last month"
    built = context_mod.build_respondent(entry, 3, entry.plan(registry), registry)
    sacrifice = next(i for i in built["items"] if i["key"] == SACRIFICE)
    assert "{cost_period}" not in str(sacrifice)
    registry_text = registry.by_key(SACRIFICE).respondent["b2b"]["guidance"]
    assert "{cost_period}" in registry_text, "the registry keeps the placeholder; the job never sees it"


def test_ability_to_pays_four_sources_are_the_registrys_fixed_answers(registry):
    """keel-cloud 088 FR-001: Ability to pay's budget sources are `respondent.fixed_answers` on its single_choice,
    asked on the decision-maker's link only."""
    ability = registry.by_key(ABILITY)
    assert ability.fixed_answer_codes == ["existing_line", "new_line_signed_off", "taken_from_other_spend",
                                          "no_budget"]
    assert ability.escape["code"] == "cant_recall_one" and ability.b2b_link_only
    assert ABILITY in fx.entry(fx.ENTRY_B2B).plan()[3] and ABILITY not in fx.entry().plan()[3]


def test_sweep_b_reads_the_cost_estimates_low_and_high(entry, registry):
    """`RespondentQuestionsRules.numbers`: the founder's cost low and high are a belief, never shown."""
    sacrifice = registry.by_key(SACRIFICE)
    founder = entry.founder_calibration[SACRIFICE]
    assert score_mod.sweep_b(["What did it cost last month?"], sacrifice, founder)["fault"] is False
    hit = score_mod.sweep_b(["Did it cost 20 last month?"], sacrifice, founder)
    assert hit["fault"] and "the founder's number 20" in hit["evidence"]


def test_a_good_respondent_plan_scores_clean_end_to_end(entry, registry):
    for part in (1, 2, 3):
        result = fx.respondent_result(entry, part)
        score = score_mod.score_respondent(fx.respondent_case(entry, part), entry, registry, entry.plan(), result)
        assert score.coverage_passed and score.faults == [], (part, score.faults)
