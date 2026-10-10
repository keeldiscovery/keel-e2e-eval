"""Cost first, held by code (spec 032 US3; judgement calls 59-65; keel-cloud 074).

The two money questions are code's -- Existing sacrifice asks *What does it cost ... today?* and Price
*What price do you have in mind ...?* -- so the model owes the first its kinds of cost (with units) and
nothing else, the second its key, and Ability to pay (derived) is not in the calibration job at all.
`W10` holds the part-3 Existing sacrifice question to the recall words of the founder's cost period.
Stackless and modelless: the hand-sized fixtures, never keel-cloud.
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


# ------------------------------------------------- the calibration side: kinds with units, no text

def test_existing_sacrifice_owes_its_kinds_and_nothing_else(registry):
    """Call 61: 4 options with units and no question, no belief phrase, is valid."""
    sacrifice = registry.by_key(SACRIFICE)
    question = fx.calibration_question(sacrifice)
    assert "question" not in question and all("belief_phrase" not in o for o in question["options"])
    assert score_mod.calibration_checks(question, sacrifice) == []
    assert score_mod.model_text(question, sacrifice, founder=True) is None
    assert score_mod.model_text({"question": "x"}, sacrifice) == "x", "the respondent's is read (W10)"


def test_a_question_the_model_wrote_anyway_is_not_read(registry):
    """Never a fault, never held to W7 / W9: keel-cloud sets it aside (`withQuestion(null)`)."""
    sacrifice = registry.by_key(SACRIFICE)
    question = dict(fx.calibration_question(sacrifice),
                    question="What does it cost? Tick all that apply. About £5?")
    assert score_mod.calibration_checks(question, sacrifice) == []


@pytest.mark.parametrize("mutate, words", [
    (lambda q: q["options"][0].pop("unit"), "U1: 'Spare keys' is a kind of cost"),
    (lambda q: q["options"][0].__setitem__("unit", "days"), "has 'days'"),
    (lambda q: q["options"][0].__setitem__("label", "I'm not sure"), "not-sure option"),
    (lambda q: q["options"][0].__setitem__("label", "Spare keys at £5"), "W9: '£'"),
    (lambda q: q.__setitem__("options", q["options"][:2]), "2 options; the rule asks 4-6"),
])
def test_the_kinds_are_held_to_units_labels_and_count(registry, mutate, words):
    sacrifice = registry.by_key(SACRIFICE)
    question = fx.calibration_question(sacrifice)
    mutate(question)
    faults = score_mod.calibration_checks(question, sacrifice)
    assert any(words in f for f in faults), faults


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


def test_the_founder_side_sweep_never_reads_existing_sacrifice(registry):
    sacrifice = registry.by_key(SACRIFICE)
    assert not score_mod.is_swept(sacrifice, founder=True)
    assert score_mod.is_swept(sacrifice), "the respondent's question is read, so swept by B"
    assert not score_mod.is_swept(registry.by_key("commercial.price"))


# ------------------------------------------------------------------------ W10 on the respondent side

@pytest.mark.parametrize("period, words", [
    ("day", "last week"), ("week", "last week"), ("month", "last month"),
    ("quarter", "the last three months"), ("year", "the last three months"),
    (None, "the last three months")])
def test_the_recall_words_follow_the_founders_cost_period(period, words):
    """`Period.recallWords`: a day is asked over a week, a year over three months, no estimate over three months."""
    assert wording_mod.recall_words(period) == words


def _item(question):
    return {"key": SACRIFICE, "question": question,
            "options": ["spare_keys", "locksmith", "Taxis", "Bus fares"],
            "units": [None, None, "money", "hours"]}


def test_w10_holds_the_part_three_question_to_the_recall_words(entry, registry):
    sacrifice = registry.by_key(SACRIFICE)
    row = entry.respondent_questions[SACRIFICE]
    assert entry.cost()["period"] == "month"
    good = _item("What did the keys cost you last month?")
    assert score_mod.respondent_checks(good, sacrifice, row, part=3, cost_period="month") == []
    bad = _item("What did the keys cost you in the last three months?")
    faults = score_mod.respondent_checks(bad, sacrifice, row, part=3, cost_period="month")
    assert len(faults) == 1 and faults[0].startswith("W10: the Existing sacrifice question asks over "
                                                      "'last month'")
    no_estimate = score_mod.respondent_checks(good, sacrifice, row, part=3, cost_period=None)
    assert no_estimate and no_estimate[0].startswith("W10:") and "the last three months" in no_estimate[0]


def test_w10_reads_the_words_as_carries_does_and_on_either_link(entry, registry):
    """A leading article, case and punctuation are free (`Wording.carries`); part 1 and 2 are not part 3."""
    sacrifice = registry.by_key(SACRIFICE)
    row = entry.respondent_questions[SACRIFICE]
    item = _item("Over THE last three months, what did the keys cost you?")
    assert score_mod.respondent_checks(item, sacrifice, row, part=3, cost_period="quarter") == []
    assert score_mod.respondent_checks(_item("Keys?"), sacrifice, row, part=3, cost_period="year")
    other = registry.by_key("commercial.commitment")
    commitment = {"key": other.key, "question": "What would you do?",
                  "options": [f"Choice {i}" for i in range(5)]}
    assert not any(f.startswith("W10") for f in score_mod.respondent_checks(
        commitment, other, entry.respondent_questions.get(other.key) or {}, part=3, cost_period="week"))


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
