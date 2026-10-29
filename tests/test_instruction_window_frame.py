"""The window frame, as the ruler reads it at `MARKS_VERSION` 18 (spec 031 US3; spec 040; judgement calls 52-55,
78, 83, 85).

keel-cloud 072 writes the windowed questions from fixed frames around one model-written clause; since 087 (D13) a
window counts at least two units, so every project frames Frequency and there is no one-unit branch; since 088 the
respondent job writes the gate's clause and nothing else, and `E4` holds the gate and the Frequency question it frames
to 20 words each. `instructions/wording.py` mirrors the Java (`WindowFrame.fault`, `gate`, `frequencyRespondent`,
`Wording.money`); these tests hold the mirror to the design's own clauses and the scorers to calls 83 and 85. Each
rule fails once for its own reason and passes once.
"""

from __future__ import annotations

import pytest

from instructions import score as score_mod
from instructions import validate as validate_mod
from instructions import wording as wording_mod
from instructions.registry import RecallWindow
from tests import v9_fixtures as fx

SEVEN_NIGHTS = RecallWindow(7, "NIGHTS")
THIRTY_DAYS = RecallWindow(30, "DAYS")
FOUR_WEEKS = RecallWindow(4, "WEEKS")


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
    ("had a bad shift with the rota", SEVEN_NIGHTS, "E1", "'shift' is a time word"),
    ("had a bad week with the rota", FOUR_WEEKS, "E1", "'week' is a time word"),
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


# --------------------------------------------------------------------------- W9 (`Wording.money`)

@pytest.mark.parametrize("text, hit", [
    ("Would they pay £5 a month?", "£"), ("About $40?", "$"), ("In GBP or not", "GBP"),
    ("They spent 40 pounds sterling", "40 pounds sterling"), ("Was it 12 dollars?", "12 dollars"),
    ("a eur trip", None), ("They lost 3 hours", None), ("Paid help at night", None),
])
def test_w9_is_money_in_any_model_text(text, hit):
    assert wording_mod.money(text) == hit




def test_the_retired_wording_mirrors_are_gone():
    """Call 83: W7's `tick_all`, W3 / W8's `carries` and call 56's reported counts read model question text, and the
    model writes none since keel-cloud 087 / 088."""
    for name in ("tick_all", "carries", "normal", "reported", "long_options"):
        assert not hasattr(wording_mod, name), name


# ------------------------------------------------------------- E4 (keel-cloud 088, the gate framed)

def test_the_gate_and_frequency_are_framed_around_the_clause():
    assert wording_mod.gate(SEVEN_NIGHTS, "Had to guess why the baby cried.") == \
        "In the last 7 nights, did you had to guess why the baby cried?"
    assert wording_mod.gate(FOUR_WEEKS, "lose your keys") == "In the last 4 weeks, did you lose your keys?"
    # spec 089 FR-5 (keel-cloud 160 FR-2): served window first; E4 measures the frame it was set against
    assert wording_mod.frequency_respondent(FOUR_WEEKS, "lose your keys") == \
        "In the last 4 weeks, on how many weeks did you lose your keys?"
    assert wording_mod.frequency_respondent(FOUR_WEEKS, "") == "In the last 4 weeks, on how many weeks did that happen?", \
        "no clause: did that happen, window first (keel-cloud 2026-10-12, 160)"
    assert wording_mod.frequency_measured(FOUR_WEEKS, "lose your keys") == \
        "On how many of those 4 weeks did you lose your keys?"
    assert wording_mod.frequency_measured(FOUR_WEEKS, "") == "On how many of those 4 weeks did that happen?"


def test_e4_holds_each_framed_question_to_twenty_words():
    assert wording_mod.framed_fault("lose your keys on the way out", SEVEN_NIGHTS) is None
    # 11 words of clause: Frequency frames it into 20 -- the longest still within 20.
    eleven = "search the whole flat for your keys before leaving for work"
    assert wording_mod.framed_fault(eleven, SEVEN_NIGHTS) is None
    fault = wording_mod.framed_fault(eleven + " again", SEVEN_NIGHTS)
    assert fault is not None and fault.startswith("E4:") and "21 words" in fault, fault
    assert "On how many of those 7 nights" in fault, "the longer of the two is named (as E4 measures it, keel-cloud 160)"


# ---------------------------------------------------------- calls 83, 85 on the two scorers

@pytest.fixture()
def registry():
    return fx.registry()


def test_frequency_owes_its_key_and_note_alone(registry):
    """Call 85 (keel-cloud 087): Frequency's question is code's on every window (D13); a text written anyway is not
    read, and options are C2."""
    frequency = registry.by_key("problem.frequency")
    bare = {"key": frequency.key, "respondent_note": "x"}
    assert score_mod.calibration_checks(bare, frequency, window=SEVEN_NIGHTS) == []
    written = dict(bare, question="On how many nights did it happen? Tick all that apply.")
    assert score_mod.calibration_checks(written, frequency, window=SEVEN_NIGHTS) == [], "a text is not read"
    with_options = dict(bare, options=[{"label": "Most nights", "belief_phrase": "most"}])
    assert score_mod.calibration_checks(with_options, frequency)[0].startswith("C2:")
    assert not score_mod.is_swept(frequency) and not score_mod.is_swept(frequency, founder=False)


def test_the_gate_owes_its_event_and_is_held_to_e1_to_e4(registry):
    gate = registry.by_key("problem.prevalence")
    assert score_mod.respondent_checks({"key": gate.key, "event": "lose your keys"}, gate) == []
    assert score_mod.respondent_checks({"key": gate.key, "question": "In the last 7 nights, did "
                                        "you lose your keys?"}, gate)[0].startswith("E2:")
    assert score_mod.respondent_checks({"key": gate.key, "event": "lose your keys last night"},
                                       gate)[0].startswith("E1:")
    long = "have to search the whole flat for your keys before leaving for work again"
    assert score_mod.respondent_checks({"key": gate.key, "event": long}, gate,
                                       window=SEVEN_NIGHTS)[0].startswith("E4:")
    assert any(f.startswith("W9:") for f in score_mod.respondent_checks(
        {"key": gate.key, "event": "lose a £5 key"}, gate))


def test_every_other_respondent_item_is_codes_whole(registry):
    """Call 83 (keel-cloud 088 FR-002): an item's key is all the model owes; a question or options written anyway are
    not read and are never a fault."""
    for key in ("problem.frequency", "problem.importance", "commercial.price", "commercial.commitment"):
        anything = {"key": key, "question": "Pay £5? Tick all that apply.", "options": ["£5"], "event": "x"}
        assert score_mod.respondent_checks(anything, registry.by_key(key)) == [], key


def test_the_prevalence_calibration_entry_owes_its_event_and_five_fifths(registry):
    """Call 85: E1-E3 on the clause, the five fifths each a label and a belief phrase (C2-C4), W9."""
    gate = registry.by_key("problem.prevalence")
    good = fx.calibration_question(gate)
    assert score_mod.calibration_checks(good, gate) == []
    assert score_mod.calibration_checks(dict(good, event=None), gate)[0].startswith("E2:")
    assert score_mod.calibration_checks(dict(good, event="lost their keys last week"), gate)[0].startswith("E1:")
    assert score_mod.calibration_checks(dict(good, options=good["options"][:4]), gate)[0].startswith("C2:")
    phrase = [dict(o) for o in good["options"]]
    phrase[0]["belief_phrase"] = ""
    assert any(f.startswith("C4:") for f in score_mod.calibration_checks(dict(good, options=phrase), gate))
    sure = [dict(o) for o in good["options"]]
    sure[1]["label"] = "Not sure"
    assert any(f.startswith("C3:") for f in score_mod.calibration_checks(dict(good, options=sure), gate))
    money = [dict(o) for o in good["options"]]
    money[2]["label"] = "About £5 worth"
    assert any(f.startswith("W9:") for f in score_mod.calibration_checks(dict(good, options=money), gate))


# ------------------------------------------------- call 55: the validator holds what the job had

def test_the_validators_batch_carries_the_mechanism_and_offer_the_job_was_handed(tmp_path):
    """keel-cloud's validator stands Lullaby's fixture in for a missing mechanism: the batch hands it the entry's
    own, short name and all; the PROBLEM job and its validator are handed none."""
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
    assert sent["mechanism"]["short_name"] == "a tag that beeps back"
    assert sent["offer_name"] == "a fix for lost keys"
    assert "mechanism" not in plain, "the PROBLEM job is handed no mechanism, nor its validator"
    assert solution.meta["swept"] == ["solution.compatibility", "solution.relative_advantage",
                                      "solution.adoption_friction"], "the lists' words (swept on PROBLEM only)"
    assert problem.meta["swept"] == [
        "problem.prevalence", "problem.importance", "problem.current_solution_satisfaction"]
