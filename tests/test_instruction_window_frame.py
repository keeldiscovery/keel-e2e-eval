"""The window frame and Price, as the ruler reads them at `MARKS_VERSION` 11 (spec 031 US3; T010;
judgement calls 52-56).

keel-cloud 072 writes the four windowed questions from fixed frames around one model-written clause,
and 073 makes Price code's and the model's money a refusal. `instructions/wording.py` mirrors the
Java line for line (`WindowFrame.fault`, `Wording.money` / `tickAll` / `carries`); these tests hold
the mirror to the Java's own worked cases -- the payroll and Lullaby clauses of
`window-frame-design.md` §3.1, keel-cloud 072's D-4 and D-6 -- and the scorers to calls 52-56. Each
rule fails once for its own reason and passes once, and the reported wording counts never reach
`marks.judge`.
"""

from __future__ import annotations

import pytest

from instructions import marks as marks_mod
from instructions import score as score_mod
from instructions import validate as validate_mod
from instructions import wording as wording_mod
from instructions.registry import RecallWindow
from tests import v9_fixtures as fx

SEVEN_NIGHTS = RecallWindow(7, "NIGHTS")
THIRTY_DAYS = RecallWindow(30, "DAYS")
LAST_SHIFT = RecallWindow(1, "SHIFTS")


# ---------------------------------------------------------------- E1-E3 (`WindowFrame.fault`)

@pytest.mark.parametrize("event, window", [
    ("had to work out why their baby was crying", SEVEN_NIGHTS),
    ("ran a payroll with an error in it, such as a typo in hours or a missing employee",
     THIRTY_DAYS),
    ("Had to work out why their baby was crying.", SEVEN_NIGHTS),     # a capital, a full stop
    ("have to work out why your baby was crying", SEVEN_NIGHTS),      # the gate's base form
])
def test_the_designs_own_clauses_pass_e1_to_e3(event, window):
    assert wording_mod.event_fault(event, window) is None


@pytest.mark.parametrize("event, window, rule, words", [
    ("", SEVEN_NIGHTS, "E2", "empty"),
    ("had 3 bad nights", SEVEN_NIGHTS, "E1", "'3' is a number"),
    ("woke up one more time", SEVEN_NIGHTS, "E1", "'one' is a number"),
    ("had a payroll error last month", THIRTY_DAYS, "E1", "'last' is a time word"),
    ("had a bad shift with the rota", LAST_SHIFT, "E1", "'shift' is a time word"),
    ("had a bad night, did they?", SEVEN_NIGHTS, "E1", "time word"),
    ("had to guess why the baby cried?", SEVEN_NIGHTS, "E2", "is a question"),
    ("had to guess. Then they rocked the baby", SEVEN_NIGHTS, "E2", "more than one sentence"),
    (" ".join(["word"] * 26), SEVEN_NIGHTS, "E2", "26 words; at most 25"),
    ("did you have to guess why the baby cried", SEVEN_NIGHTS, "E3", "'did you'"),
    ("in the dark, had to guess", SEVEN_NIGHTS, "E3", "'in'"),
    ("how many parents had to guess", SEVEN_NIGHTS, "E3", "'how many'"),
])
def test_each_of_e1_to_e3_refuses_for_its_own_reason(event, window, rule, words):
    fault = wording_mod.event_fault(event, window)
    assert fault is not None and fault.startswith(rule + ":"), fault
    assert words in fault, fault


def test_the_clause_is_trimmed_as_the_frame_holds_it():
    assert wording_mod.clause("  Had to   guess.. ") == "had to guess"
    assert wording_mod.clause("NHS staff were short") == "NHS staff were short", "an acronym"


# ----------------------------------------------------- W7 / W9 / W3 / W8 (`Wording`, mirrored)

@pytest.mark.parametrize("text, hit", [
    ("Which of these? Tick all that apply.", "Tick all"),
    ("Tick every one you believe applies.", "Tick every"),
    ("Select all that apply", "Select all"),
    ("Pick all you would take.", "Pick all"),
    ("Would they check every payroll?", None),                       # 072 D-6: a real question
])
def test_w7_is_the_tick_all_hint_and_nothing_else(text, hit):
    assert wording_mod.tick_all(text) == hit


@pytest.mark.parametrize("text, hit", [
    ("Would they pay £5 a month?", "£"), ("About $40?", "$"), ("In GBP or not", "GBP"),
    ("They spent 40 pounds sterling", "40 pounds sterling"), ("Was it 12 dollars?", "12 dollars"),
    ("a eur trip", None), ("They lost 3 hours", None), ("Paid help at night", None),
])
def test_w9_is_money_in_any_model_text(text, hit):
    assert wording_mod.money(text) == hit


@pytest.mark.parametrize("text, name, carried", [
    ("When would a parent look at a suggested reason for crying?",
     "a suggested reason for crying", True),
    ("Would the Suggested-Reason for Crying help?", "a suggested reason for crying", True),
    ("Would the list of flagged employees help?", "a list of flagged employees", True),
    ("Would a suggestion help?", "a suggested reason for crying", False),
    ("Anything at all", None, True),                                 # a card with no name
])
def test_verbatim_is_case_punctuation_and_a_leading_article_free(text, name, carried):
    """keel-cloud 072 D-4."""
    assert wording_mod.carries(text, name) is carried


# ---------------------------------------------------------- calls 52-55 on the two scorers

@pytest.fixture()
def registry():
    return fx.registry()


def test_frequency_owes_no_text_on_a_framed_window_and_its_question_on_a_one_unit_window(registry):
    """Call 52 (072 D-7): a text written anyway on a framed window is ignored, never a fault."""
    frequency = registry.by_key("problem.frequency")
    bare = {"key": frequency.key, "respondent_note": "x"}
    assert score_mod.calibration_checks(bare, frequency, window=SEVEN_NIGHTS) == []
    written = dict(bare, question="On how many nights did it happen? Tick all that apply.")
    assert score_mod.calibration_checks(written, frequency, window=SEVEN_NIGHTS) == [], \
        "a text on a framed window is not read"
    assert score_mod.calibration_checks(bare, frequency, window=LAST_SHIFT) == \
        ["no question written"]


def test_price_owes_its_key_alone_on_both_screens(registry):
    """Call 53: options on the founder's Price are C2; the respondent's Price item is code's whole."""
    price = registry.by_key("commercial.price")
    assert score_mod.calibration_checks({"key": price.key, "respondent_note": "x"}, price) == []
    with_options = {"key": price.key, "options": [{"label": "Under £2", "belief_phrase": "x"}]}
    assert score_mod.calibration_checks(with_options, price)[0].startswith("C2:")
    anything = {"key": price.key, "question": "Pay £5? Tick all that apply.", "options": ["£5"]}
    assert score_mod.respondent_checks(anything, price, {"control": "price_ladder"}) == []
    assert not score_mod.is_swept(price) and not score_mod.is_swept(
        registry.by_key("problem.frequency"), SEVEN_NIGHTS)
    assert score_mod.is_swept(registry.by_key("problem.frequency"), LAST_SHIFT)


def test_the_gate_owes_its_event_and_is_held_to_e1_to_e3(registry):
    gate = registry.by_key("problem.prevalence")
    row = {"control": "gate_yes_no"}
    assert score_mod.respondent_checks({"key": gate.key, "event": "lose your keys",
                                        "options": None}, gate, row) == []
    assert score_mod.respondent_checks({"key": gate.key, "question": "In the last 7 nights, did "
                                        "you lose your keys?"}, gate, row)[0].startswith("E2:")
    assert score_mod.respondent_checks({"key": gate.key, "event": "lose your keys last night"},
                                       gate, row)[0].startswith("E1:")
    assert any(f.startswith("W9:") for f in score_mod.respondent_checks(
        {"key": gate.key, "event": "lose a £5 key"}, gate, row))


def test_u1_holds_every_kind_of_cost_to_its_unit_on_both_screens(registry):
    sacrifice = registry.by_key("commercial.existing_sacrifice")
    question = fx.calibration_question(sacrifice)
    assert score_mod.calibration_checks(question, sacrifice) == []
    none = next(o for o in question["options"] if o["normalized"] == "none")
    assert "unit" not in none, "the fixed none has none"
    question["options"][1]["unit"] = "days"
    assert score_mod.calibration_checks(question, sacrifice) == [
        "U1: 'Option 2 for this' is a kind of cost and needs its unit -- money, hours or count -- "
        "and has 'days'"]
    entry = fx.entry()
    row = entry.respondent_questions[sacrifice.key]
    item = {"key": sacrifice.key, "question": "What did it cost you?",
            "options": ["spare_keys", "locksmith", "Taxis", "Bus fares"],
            "units": [None, None, "money", "hours"]}
    assert score_mod.respondent_checks(item, sacrifice, row) == [], \
        "founder kinds keep the calibration's unit; only distractors owe one"
    item["units"] = [None, None, "money"]
    assert score_mod.respondent_checks(item, sacrifice, row) == [
        "U1: 'Bus fares' is a kind of cost and needs its unit in units[3] -- money, hours or "
        "count -- and has None"]


def test_w3_and_w8_hold_only_to_a_name_the_corpus_records(registry):
    """Call 55: with no name nothing is held; with one, the SOLUTION and COMMERCIAL questions
    (Existing sacrifice aside) carry it verbatim."""
    compatibility = registry.by_key("solution.compatibility")
    question = {"key": compatibility.key, "question": "When would a parent look at it?",
                "options": fx.calibration_question(compatibility)["options"]}
    assert score_mod.calibration_checks(question, compatibility) == []
    assert score_mod.calibration_checks(question, compatibility,
                                        short_name="a suggested reason for crying") == [
        "W3: the question does not name the idea by its short name, 'a suggested reason for "
        "crying', verbatim"]
    commitment = registry.by_key("commercial.commitment")
    asked = dict(fx.calibration_question(commitment),
                 question="Which steps would they take to try something that helps at night?")
    assert score_mod.calibration_checks(asked, commitment,
                                        offer_name="something that helps at night") == []
    sacrifice = registry.by_key("commercial.existing_sacrifice")
    assert score_mod.calibration_checks(fx.calibration_question(sacrifice), sacrifice,
                                        offer_name="something that helps at night") == [], \
        "072 D-2: Existing sacrifice names no offer"
    item = {"key": commitment.key, "question": "Which would you do now?", "options": ["A"]}
    faults = score_mod.respondent_checks(item, commitment, {"control": "multi_choice_ladder"},
                                         part=3, offer_name="something that helps at night")
    assert any(f.startswith("W8:") for f in faults), faults


def test_w7_and_w9_are_option_validity_faults_on_the_respondent_screen(registry):
    scale = registry.by_key("problem.current_solution_satisfaction")
    row = {"control": "single_choice_5", "codes": list(scale.fixed_codes)}
    item = {"key": scale.key, "question": "How well did it work? Tick all that apply.",
            "options": [f"Choice {i}" for i in range(5)]}
    assert any(f.startswith("W7:") for f in score_mod.respondent_checks(item, scale, row))
    item = dict(item, question="How well did it work?", options=["£1"] + item["options"][1:])
    assert any(f.startswith("W9:") for f in score_mod.respondent_checks(item, scale, row))


# ---------------------------------------------------------------- call 56: reported, never marked

def test_the_wording_rules_are_counted_per_question():
    long_one = ("When a payroll has been run and needs checking before employees are paid, at what "
                "point do you think a payroll practitioner would look at a list of employees?")
    counted = wording_mod.reported(long_one, founder=True)
    assert counted["words"] == 29 and counted["w1"] and counted["w2"] and counted["w6"]
    assert counted["s1"], "a clause in front of a long one-sentence question"
    shorthand = "After a payroll run, when would a practitioner look at a list of flagged employees?"
    counted = wording_mod.reported(shorthand, founder=True)     # §3.7 says 14; the words are 15
    assert counted["words"] == 15
    assert not counted["w1"] and not counted["s1"] and not counted["w2"] and not counted["w6"]
    scene = ("A payroll has been run and needs checking before payday. At what point would a "
             "payroll practitioner look at a list of employees flagged as unusual?")
    counted = wording_mod.reported(scene, founder=True)
    assert (counted["words"], counted["w1"], counted["s1"]) == (26, True, False), \
        "§3.6's own S1 example is one word over W1's 25 with a scene -- reported, never a fault"
    assert "w2" not in wording_mod.reported("Do you think so?", founder=False), \
        "W2 and W6 are the founder's side only"
    assert wording_mod.long_options(["Straight after the run",
                                     "Only with a special exception or extra sign-off from above"]) == 1


def test_the_wording_counts_reach_the_totals_and_never_the_judge(registry):
    entry = fx.entry()
    result = fx.calibration_result(registry, "SOLUTION")
    result["questions"][0]["question"] = ("When the keys are gone and the train is due, do you "
                                          "think a commuter who cycles would look at it first?")
    score = score_mod.score_calibration(fx.calibration_case(entry, "SOLUTION"), entry, registry,
                                        result)
    totals = score_mod.totals([score])
    wording = totals["wording"]["calibration"]
    assert wording["questions"] == 3 and wording["w2"] == 1 and wording["s1"] == 1
    assert totals["option_validity"] == 1.0, "a reported rule is never a fault"
    judged = marks_mod.judge(totals, marks_mod.load())
    assert "wording" not in judged and "wording" not in marks_mod.DEFAULTS


# ------------------------------------------------- call 55: the validator holds what the job had

def test_the_validators_batch_carries_the_mechanism_and_offer_the_job_was_handed(tmp_path):
    """keel-cloud's validator stands Lullaby's fixture in for a missing mechanism, and that fixture
    carries a short name the corpus does not: the batch hands it the entry's own, name and all."""
    from instructions import prompts as prompts_mod                         # noqa: PLC0415
    entry = fx.entry()
    cases = prompts_mod.build_cases(entry, fx.exported(tmp_path), fx.instructions(),
                                    fx.FakeRuntime, n_runs=1)
    solution = next(c for c in cases if c.case_id.endswith("CALIBRATION_SOLUTION/run1"))
    problem = next(c for c in cases if c.case_id.endswith("CALIBRATION_PROBLEM/run1"))
    batch = validate_mod.build_batch([(solution, {"questions": []}),
                                      (problem, {"questions": []})])
    sent, plain = batch["cases"]
    assert sent["mechanism"]["mechanism"] == entry.solution_mechanism["mechanism"]
    assert sent["mechanism"]["short_name"] is None and sent["offer_name"] is None
    assert "mechanism" not in plain, "the PROBLEM job is handed no mechanism, nor its validator"
    assert len(solution.meta["swept"]) == 3, "every SOLUTION key has model text (swept on PROBLEM only)"
    assert problem.meta["swept"] == [
        "problem.prevalence", "problem.importance", "problem.current_solution_satisfaction"]
