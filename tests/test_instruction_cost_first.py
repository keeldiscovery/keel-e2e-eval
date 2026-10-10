"""Cost first, held by code (spec 032 US3; judgement calls 59-65; keel-cloud 074) -- and, since spec 033 (call
67; keel-cloud 077), the buyer's cost as one total.

The two money questions are code's -- Existing sacrifice asks *What does it cost ... today?* of the founder and
*{Last month}, what did it cost ...?* of the buyer, Price *What price do you have in mind ...?* -- so the model
owes each its key (and, in calibration, a note) and nothing else, and Ability to pay (derived) is not in the
calibration job at all. `W10` and `U1` retired with the kinds. Stackless and modelless: the hand-sized
fixtures, never keel-cloud.
"""

from __future__ import annotations

import pytest

from instructions import context as context_mod
from instructions import registry as registry_mod
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


def _q(result, key):
    return next(q for q in result["questions"] if q["key"] == key)


# ------------------------------------------------- the calibration side: the key and the note, no kinds

def test_existing_sacrifice_owes_its_key_and_nothing_else(registry):
    """Call 67: no options, no unit, no question, no belief phrase -- the entry is the key and the note."""
    sacrifice = registry.by_key(SACRIFICE)
    question = fx.calibration_question(sacrifice)
    assert set(question) == {"key", "respondent_note"}
    assert score_mod.calibration_checks(question, sacrifice) == []
    assert score_mod.model_text(question, sacrifice, founder=True) is None


def test_a_question_the_model_wrote_anyway_is_not_read(registry):
    """Never a fault, never held to W7 / W9: keel-cloud sets it aside (`withQuestion(null)`)."""
    sacrifice = registry.by_key(SACRIFICE)
    question = dict(fx.calibration_question(sacrifice),
                    question="What does it cost? Tick all that apply. About £5?")
    assert score_mod.calibration_checks(question, sacrifice) == []


@pytest.mark.parametrize("options", [
    [{"label": "Spare keys", "unit": "money"}],
    [{"label": f"Kind {i}", "belief_phrase": "x"} for i in range(5)],
])
def test_any_option_on_existing_sacrifice_is_c2_as_on_price(registry, options):
    """Call 67 (keel-cloud 077, contract 8: `unit` is gone): options are refused with C2, like Price's."""
    sacrifice = registry.by_key(SACRIFICE)
    question = dict(fx.calibration_question(sacrifice), options=options)
    faults = score_mod.calibration_checks(question, sacrifice)
    assert len(faults) == 1 and faults[0].startswith(f"C2: {len(options)} options on Existing sacrifice")


def test_money_in_the_event_is_still_w9_on_existing_sacrifice(registry):
    sacrifice = registry.by_key(SACRIFICE)
    question = dict(fx.calibration_question(sacrifice), event="spent £5 on a spare")
    assert any(f.startswith("W9:") for f in score_mod.calibration_checks(question, sacrifice))


def test_ability_to_pay_is_not_in_the_job_and_the_denominator_is_the_answered_set(entry, registry):
    good = _calibrate(entry, registry, "COMMERCIAL")
    assert (good.coverage_of, good.coverage_hit, good.validity_of) == (4, 4, 4)
    assert [q["key"] for q in fx.calibration_result(registry, "COMMERCIAL")["questions"]] == [
        SACRIFICE, "commercial.price", "commercial.buyer_payer_alignment", "commercial.commitment"]

    def include_ability(result):
        ability = registry.by_key(ABILITY)
        result["questions"].insert(2, {"key": ABILITY, "question": "How would they pay?"})
        assert ability.derived
    bad = _calibrate(entry, registry, "COMMERCIAL", include_ability)
    assert bad.coverage_passed is False
    assert any("outside the slice commercial.ability_to_pay" in f["evidence"] for f in bad.faults)


def test_the_b2b_job_is_five_answered_and_still_has_purchase_friction():
    b2b = fx.entry(fx.ENTRY_B2B)
    registry = fx.registry()
    score = _calibrate(b2b, registry, "COMMERCIAL")
    assert (score.coverage_of, score.coverage_hit, score.validity_hit) == (5, 5, 5)
    assert "commercial.purchase_friction" in [d.key for d in registry.answered_slice("COMMERCIAL", True)]


def test_neither_side_sweeps_existing_sacrifice(registry):
    """Call 67: the founder's side was never read (v12) and the respondent's is code's now, so nothing the
    model wrote is swept, as with Price."""
    sacrifice = registry.by_key(SACRIFICE)
    assert not score_mod.is_swept(sacrifice, founder=True)
    assert not score_mod.is_swept(sacrifice)
    assert not score_mod.is_swept(registry.by_key("commercial.price"))


# ------------------------------------------------------ the respondent side: the key alone, W10 and U1 retired

@pytest.mark.parametrize("period, words", [
    ("day", "last week"), ("week", "last week"), ("month", "last month"),
    ("quarter", "the last three months"), ("year", "the last three months"),
    (None, "the last three months")])
def test_the_recall_words_follow_the_founders_cost_period(period, words):
    """`Period.recallWords`: a day is asked over a week, a year over three months, no estimate over three months."""
    assert wording_mod.recall_words(period) == words


def test_the_respondent_item_is_the_key_alone_and_w10_and_u1_are_retired(entry, registry):
    """Call 67: whatever question, options or units a model writes for the total is not read -- no W10 on the
    recall words, no U1 on a unit, no options to count."""
    sacrifice = registry.by_key(SACRIFICE)
    row = entry.respondent_questions[SACRIFICE]
    assert row["control"] == "cost_total" and sacrifice.respondent_code_written
    assert score_mod.respondent_checks({"key": SACRIFICE}, sacrifice, row, part=3) == []
    written = {"key": SACRIFICE, "question": "What did the keys cost you in the last three months?",
               "options": ["Taxis", "Bus fares"], "units": [None, "days"]}
    assert score_mod.respondent_checks(written, sacrifice, row, part=3) == []
    assert not hasattr(wording_mod, "recall_fault") and not hasattr(score_mod, "UNITS")


def test_the_context_names_the_recall_words_the_job_is_handed_filled(entry, registry):
    """Call 62: `{cost_period}` is filled on every respondent item with the founder's recall words."""
    assert context_mod.cost_recall_of(entry) == "last month"
    built = context_mod.build_respondent(entry, 3, entry.plan(registry), registry)
    sacrifice = next(i for i in built["items"] if i["key"] == SACRIFICE)
    assert "{cost_period}" not in str(sacrifice)
    registry_text = registry.by_key(SACRIFICE).respondent["guidance"]
    assert "{cost_period}" in registry_text, "the registry keeps the placeholder; the job never sees it"
    assert "last month" in sacrifice["respondent"]["guidance"]
    calibration = context_mod.build_calibration(entry, "COMMERCIAL", registry)
    assert "{cost_period}" in str(calibration["dimensions"][0]), \
        "keel-cloud fills the placeholder on respondent items only; the calibration copy keeps it"


# ------------------------------------------------------ Ability to pay's respondent item and sweep B

def test_ability_to_pays_four_rungs_are_the_fixed_respondent_codes_on_the_b2b_link():
    b2b = fx.entry(fx.ENTRY_B2B)
    registry = fx.registry()
    ability = registry.by_key(ABILITY)
    row = b2b.respondent_questions[ABILITY]
    item = {"key": ABILITY, "question": "Where did the money come from?",
            "options": ["From an existing line", "A new line, signed off", "From other spend", "None"]}
    assert score_mod.respondent_checks(item, ability, row, part=3) == []
    five = dict(item, options=item["options"] + ["Free"])
    assert any("5 options; the plan has 4" in f for f in score_mod.respondent_checks(
        five, ability, row, part=3))
    assert ABILITY in b2b.plan()[3] and ABILITY not in fx.entry().plan()[3]


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
        case = fx.respondent_case(entry, part)
        score = score_mod.score_respondent(case, entry, registry, entry.plan(), result)
        assert score.coverage_passed and score.faults == [], (part, score.faults)
