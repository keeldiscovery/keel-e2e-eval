"""Spec 141: the harness mirrors keel-cloud's cycle 14 round (219-228; keel-cloud-docs master `0844a180`, each spec's
tasks.md *Owed: keel-e2e-eval*). No stack, no model, no paid call; the cloud's sources are read from the checkout
`stack.toml` names, skipped without it. The cases are the cloud's own tests' (named beside each).

- FR-4 Commitment (221): the Yes at eleven, the step whole; an act-first smaller step said -ing and kept; data acts.
- FR-5 Prevalence (224): E8 reads the head verb and the verdict words; 06-repeatline's scripted clause off *by hand*.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from harness import vectors_script as vs
from instructions import spoken as spoken_mod
from instructions import step_cost as step_cost_mod
from instructions import wording as wording_mod
from instructions.registry import RecallWindow
from stack.config import load_config

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
VECTORS = "src/main/java/com/keeldiscovery/cloud/domain/vectors/"
APPLICATION = "src/main/java/com/keeldiscovery/cloud/application/"
INSTRUCTIONS = "src/main/resources/keel/inference-instructions/"
SEVEN_DAYS = RecallWindow(7, "DAYS")
#: keel-cloud `VectorFixtures` (Lullaby).
EVENT_PAST = "had to work out why their baby was crying"
WENT_WRONG = "did not know why the baby cried"


def _cloud(rel: str) -> str:
    path = KEEL_CLOUD / rel
    if not path.is_file():
        pytest.skip(f"no keel-cloud checkout at {KEEL_CLOUD} ({rel})")
    return path.read_text(encoding="utf-8")


# ----------------------------------------------------------------------------------------------- FR-4: keel-cloud 221

def test_the_yes_is_the_step_whole_at_eleven():
    """221 FR-1 (`SpokenForm.STEP_OPTION_MAX_WORDS`, `ItemFrames.firstYes` / `stepCut`; CommitmentWholeStepTest):
    Codyco's *at one hotel* and Expanse's *for two weeks* stay; a step past nine is cut and the cut named."""
    spoken = _cloud(VECTORS + "SpokenForm.java")
    frames = _cloud(VECTORS + "ItemFrames.java")
    assert "STEP_OPTION_MAX_WORDS = 11;" in spoken and spoken_mod.STEP_OPTION_MAX_WORDS == 11
    assert "STEP_MAX_WORDS = SpokenForm.STEP_OPTION_MAX_WORDS - 2;" in frames and spoken_mod.STEP_MAX_WORDS == 9
    assert spoken_mod.first_yes("pay €3,000 for a money-back pilot at one hotel") == \
        "Yes, I'd pay €3,000 for a money-back pilot at one hotel"
    assert spoken_mod.first_yes("let Expanse measure cluster waste free for two weeks") == \
        "Yes, I'd let Expanse measure cluster waste free for two weeks"
    assert spoken_mod.step_cut("let Expanse measure cluster waste free for two weeks") is None


def test_an_act_first_smaller_step_is_kept_and_said_as_its_act():
    """221 FR-2 (`ItemFrames.restatesTheStep` / `act` / `smallerSaid` / `theStep`): AirCaps' *try a pair of caption
    glasses* names another act than *order*, so it is served, *trying ...*; the vocabularies are the cloud's."""
    frames = _cloud(VECTORS + "ItemFrames.java")
    for word in spoken_mod.SMALLER_ACT_VERBS:
        assert f'"{word}"' in frames.split("ACT_VERBS = ", 1)[1].split(";", 1)[0], word
    for word in spoken_mod.SIZE_OR_COST:
        assert f'"{word}"' in frames.split("SIZE_OR_COST = ", 1)[1].split(";", 1)[0], word
    assert not spoken_mod.restates_the_step("order the caption glasses with free returns",
                                            "try a pair of caption glasses")
    assert spoken_mod.second_yes("try a pair of caption glasses") == \
        "Probably, after trying a pair of caption glasses first"
    assert vs.the_step("try a pair of caption glasses") == "trying a pair of caption glasses"
    assert vs.the_step("a free trial") == "the free trial"
    assert spoken_mod.restates_the_step("pay for one month after the trial", "a free trial")


def test_data_acts_are_the_clouds_and_cost_data():
    """221 FR-3 (`StepCost.DATA_ACTS`): installing, uploading, handing over, letting it read or measure -- free or not;
    *allow it to use the microphone* is none of them."""
    source = _cloud(VECTORS + "StepCost.java")
    body = source.split("DATA_ACTS = Pattern.compile(", 1)[1].split(");", 1)[0]
    java = "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', body)).replace("\\\\", "\\")
    assert step_cost_mod.DATA_ACTS.pattern == java
    for step, word in (("let Expanse measure cluster waste free for two weeks", "measure"),
                       ("install the app", "install"), ("hand the call logs over", "over"),
                       ("upload last month's invoices", "upload"), ("allow it to read the calendar", "read")):
        assert step_cost_mod.of(step) == step_cost_mod.Cost(step_cost_mod.DATA, word), step
    assert step_cost_mod.of("allow it to use the microphone at night") is None


# ----------------------------------------------------------------------------------------------- FR-5: keel-cloud 224

PALUS = "kept raise cash in the bank's default treasury product"
FRESCO = "sorted site photos by hand for the log"
AIRCAPS = "nodded along without understanding what was said"
EXPANSE = "had a job fail partway through its run"
CODYCO = "let a booking call ring out unanswered"


def test_the_lists_are_the_clouds():
    """224 (`WindowFrame.STATE_VERBS`, `VERDICT_WORDS`, the instruction's gate rule quoting the list word for word)."""
    frame = _cloud(VECTORS + "WindowFrame.java")
    states = frame.split("STATE_VERBS = List.of(", 1)[1].split(");", 1)[0]
    assert tuple(re.findall(r'"([^"]+)"', states)) == wording_mod.STATE_VERBS
    verdicts = frame.split("VERDICT_WORDS = List.of(", 1)[1].split(");", 1)[0]
    assert tuple(re.findall(r'"([^"]+)"', verdicts)) == wording_mod.VERDICT_WORDS
    rule = re.search(r"\*\*The verb says the act, never a verdict on it\*\*[^:]*: none of (.*?)\.\n",
                     _cloud(INSTRUCTIONS + "respondent-questions.md"), re.DOTALL)
    assert tuple(re.findall(r"\*([^*]+)\*", re.sub(r"\s+", " ", rule.group(1)))) == wording_mod.VERDICT_WORDS


@pytest.mark.parametrize("event,head", [
    (PALUS, "kept"), ("held the delivery at the dock for a day", "held"), ("had cash in a fund that paid little", "had"),
    ("sat in the trailer with the day's photos", "sat"), ("remained on hold with the bank", "remained"),
    ("keeps the notes on a phone", "keeps"), ("their cash sat in a treasury product", "sat"),
    ("had the cash sit in a fund", "sit"), ("had kept the notes on a phone", "kept")])
def test_a_head_verb_of_state_is_refused(event, head):
    """224 FR-1 (PrevalenceEventIsAMomentTest `aHeadVerbOfStateIsRefused`)."""
    assert wording_mod.packed_fault(event, "a call rang out unanswered", SEVEN_DAYS) == (
        f"E8: event '{event}' is a standing state ('{head}'); write the moment inside the window where it showed -- "
        "what they did, or what happened to the thing, on a given day")


def test_the_unit_is_the_windows_and_have_is_read_whole():
    """224 FR-1 (`wentWrongAllowsTheVerbAndHaveIsReadWhole`)."""
    assert wording_mod.packed_fault(PALUS, None, RecallWindow(5, "WORKING_DAYS")).endswith("on a given working day")
    assert wording_mod.packed_fault(PALUS, None).endswith("on a given day")
    assert wording_mod.packed_fault("kept a guest on hold past ten minutes",
                                    "kept a guest on hold past ten minutes", SEVEN_DAYS) is None
    assert wording_mod.packed_fault("kept a guest on hold past ten minutes", "a guest waited on hold", SEVEN_DAYS)
    assert wording_mod.packed_fault("held a delivery at the dock overnight",
                                    "a delivery is held at the dock overnight", SEVEN_DAYS) is None
    assert wording_mod.packed_fault("had cash in a fund that paid little", "had to move cash", SEVEN_DAYS)
    for moment in (EVENT_PAST, EXPANSE, "had a job run out of memory", "had a booking call ring out without being "
                   "answered", "had lost the site notes before the log", "had the payroll go out with an error",
                   "a booking call rang out unanswered"):
        assert wording_mod.packed_fault(moment, WENT_WRONG, SEVEN_DAYS) is None, moment


def test_each_verdict_word_is_refused():
    """224 FR-2 (`eachVerdictWordIsRefused`)."""
    carrying = {"idle": "watched the truck idle at the gate", "sitting": "found the parcel sitting at the gate",
                "still": "still waited for the delivery at noon", "stay": "stayed late in the trailer on the log",
                "have to": "lost the notes they had to file", "fail to": "failed to file the log",
                "waste": "wasted an hour on the phone", "struggle": "struggled to follow a conversation",
                "by hand": FRESCO, "manually": "typed the notes in manually",
                "could have": "could have saved the notes", "would have": "would have missed the call",
                "more than it could": "asked for more than it could give", "better": "found a better supplier"}
    assert tuple(carrying) == wording_mod.VERDICT_WORDS
    for word, event in carrying.items():
        fault = wording_mod.packed_fault(event, event, SEVEN_DAYS)
        assert fault and fault.startswith(f"E8: event '{event}' ") and f"'{word}" in fault, (word, fault)
    assert wording_mod.packed_fault(FRESCO, "had to sort photos", SEVEN_DAYS) == (
        f"E8: event '{FRESCO}' carries 'by hand', a verdict on the act -- the way it was done or what might have been "
        "-- not the act; write the act alone, from went_wrong, as a person saw it on a given day")
    assert wording_mod.packed_fault("still had photos to log", "still had photos to log") is None
    assert wording_mod.packed_fault("still had photos to log", "photos waited")
    assert wording_mod.packed_fault(EVENT_PAST, WENT_WRONG) is None
    assert wording_mod.packed_fault("still had to put the photos into the log",
                                    "still had to put the photos into the log") is None
    assert wording_mod.packed_fault("lost the notes they have to file", "lost the notes")


def test_cycle_fourteens_clauses_and_the_scripted_seven():
    """224 FR-5 (`theCycleFourteenClauses`); its owed list: 06-repeatline's scripted clause is reworded off *by hand*
    (the harness's fixture, the corpus untouched) and every scripted Prevalence passes E8."""
    for moment in (AIRCAPS, EXPANSE, CODYCO, EVENT_PAST, "typed up the log after the walk", "took a call from a guest",
                   "waited at the supply yard for mulch"):
        assert wording_mod.packed_fault(moment, moment, SEVEN_DAYS) is None, moment
        assert wording_mod.packed_fault(moment, WENT_WRONG, SEVEN_DAYS) is None, moment
    assert "('kept')" in wording_mod.packed_fault(PALUS, "the bank paid little on raise cash", SEVEN_DAYS)
    assert "carries 'by hand'" in wording_mod.packed_fault(FRESCO, "sorted site photos for the log", SEVEN_DAYS)
    assert vs.PROBLEM_CLAUSES["06-repeatline"] == ("had to type a refill request in", "have to type a refill request in")
    for entry_id, (event, _) in vs.PROBLEM_CLAUSES.items():
        assert wording_mod.packed_fault(event, vs.ACT_THAT_HURTS[entry_id][1]) is None, entry_id
