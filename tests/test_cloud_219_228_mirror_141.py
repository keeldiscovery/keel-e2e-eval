"""Spec 141: the harness mirrors keel-cloud's cycle 14 round (219-228; keel-cloud-docs master `0844a180`, each spec's
tasks.md *Owed: keel-e2e-eval*). No stack, no model, no paid call; the cloud's sources are read from the checkout
`stack.toml` names, skipped without it. The cases are the cloud's own tests' (named beside each).

- FR-4 Commitment (221): the Yes at eleven, the step whole; an act-first smaller step said -ing and kept; data acts.
- FR-5 Prevalence (224): E8 reads the head verb and the verdict words; 06-repeatline's scripted clause off *by hand*.
- FR-2 Relative advantage (219): *Think of {hard_case}.* first; the belief on `hard_case_theirs`; the scripted clause.
- FR-3 Price (220): the question and the belief name the idea; the walk holds the served question.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from instructions import spoken as spoken_mod
from instructions import step_cost as step_cost_mod
from instructions import wording as wording_mod
from instructions.registry import RecallWindow
from stack.config import load_config
from tests import v9_fixtures as fx

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
VECTORS = "src/main/java/com/keeldiscovery/cloud/domain/vectors/"
APPLICATION = "src/main/java/com/keeldiscovery/cloud/application/"
INSTRUCTIONS = "src/main/resources/keel/inference-instructions/"
SEVEN_DAYS = RecallWindow(7, "DAYS")
#: keel-cloud `VectorFixtures` (Lullaby).
EVENT_PAST = "had to work out why their baby was crying"
WENT_WRONG = "did not know why the baby cried"


@pytest.fixture(scope="module")
def golden():
    """The golden seven as the corpus records them (skipped by name off the checkout)."""
    return {e: corpus_mod.load_file(fx.canon_entry(f"{e}.yaml"), registry=fx.registry())
            for e in ("01-countly", "02-compliancelog", "03-lullaby", "04-linerly", "05-paidly", "06-repeatline",
                      "07-mulchrun")}


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


# ----------------------------------------------------------------------------------------------- FR-2: keel-cloud 219

#: keel-cloud `RelativeAdvantageHardCaseTest`'s five cycle-14 entries: (occasion, stem, name, what, job, hard_case,
#: hard_case_theirs, benefits, the item now, the belief now).
HARD_FIVE = {
    "08-fresco": ("daily log", "the last time the site walks were done and photos and notes still had to go into the "
                  "daily log", "Fresco", "an AI scribe that turns your site-walk videos into notes",
                  "keep an accurate record of the day's work on site",
                  "the last daily log when you lost site notes before writing it",
                  "their last daily log where they lost site notes",
                  ["Hours back at the end of the day", "Action items to the crew the same day"],
                  "Think of the last daily log when you lost site notes before writing it. Would Fresco, an AI scribe "
                  "that turns your site-walk videos into notes, have done that better for you, or not?",
                  "For most, with it, their last daily log where they lost site notes would have given them hours back "
                  "at the end of the day and action items to the crew the same day."),
    "10-palus": ("cash decision", "over the last 3 months, when the company decides where cash from a raise sits until "
                 "it is needed", "Palus", "a treasury account that holds your long-term reserve",
                 "keep the money from a raise safe and earning until the company sends it",
                 "the last time your bank cut the yield on your raise cash",
                 "the last time their bank cut the yield on their raise cash",
                 ["Higher yield on cash not needed for months", "No treasury hire to manage it"],
                 "Think of the most recent time your bank cut the yield on your raise cash. Would Palus, a treasury "
                 "account that holds your long-term reserve, have done that better for you, or not?",
                 "For most, with it, the last time their bank cut the yield on their raise cash would have given them "
                 "higher yield on cash not needed for months and no treasury hire to manage it."),
    "13-aircaps": ("conversation", "the last time you tried to follow and join a face-to-face conversation", "AirCaps",
                   "an app", "follow and join a face-to-face conversation",
                   "the last time you lost track of a conversation with hearing people",
                   "the last time they lost track of a conversation with hearing people",
                   ["More of the talk followed without asking for repeats"],
                   "Think of the most recent time you lost track of a conversation with hearing people. Would AirCaps, "
                   "an app, have done that better for you, or not?",
                   "For most, with it, the last time they lost track of a conversation with hearing people would have "
                   "given them more of the talk followed without asking for repeats."),
    "17-expanse": ("job", None, "Expanse", "software on every node that predicts each job's resource needs",
                   "get each job to run to the end without wasting the cluster", "the last job that ran out of memory",
                   "their last job that ran out of memory",
                   ["A job that runs to the end first time", "A shorter wait in the queue"],
                   "Think of the last job that ran out of memory. Would Expanse, software on every node that predicts "
                   "each job's resource needs, have done that better for you, or not?",
                   "For most, with it, their last job that ran out of memory would have given them a job that runs to "
                   "the end first time and a shorter wait in the queue."),
    "21-codyco": ("booking call", "the last time booking calls came in on your shift", "Codyco",
                  "an AI reservation agent that answers missed calls", "turn every guest who calls into a booking",
                  "the last time a booking call rang out unanswered", "the last time a booking call rang out unanswered",
                  ["Missed calls turned into bookings", "Callers answered when the desk is busy"],
                  "Think of the most recent time a booking call rang out unanswered. Would Codyco, an AI reservation "
                  "agent that answers missed calls, have done that better for you, or not?",
                  "For most, with it, the last time a booking call rang out unanswered would have given them missed "
                  "calls turned into bookings and callers answered when the desk is busy."),
}


@pytest.mark.parametrize("entry_id", sorted(HARD_FIVE))
def test_the_five_items_and_beliefs_on_the_hard_case(entry_id):
    """219 FR-4 / FR-5 (`RelativeAdvantageHardCaseTest.theFiveItemsAsServedAndAsReadNow` / `...Beliefs...`): *Think of
    {hard_case}.* first, the question unchanged after it; the belief on `hard_case_theirs`, every benefit kept."""
    occasion, stem, name, what, job, hard, theirs, benefits, item, belief = HARD_FIVE[entry_id]
    assert spoken_mod.advantage_stem(occasion, name, what, job, stem, hard) == item
    anchor = spoken_mod.hard_case_anchor(hard)
    assert item.startswith(anchor + " Would " + name + ", ")
    assert item[len(anchor) + 1:] == spoken_mod.advantage_stem(occasion, name, what, job, stem).split(". ", 1)[1]
    assert corpus_mod.advantage_belief_219(benefits, occasion, theirs) == belief
    assert corpus_mod.advantage_belief(benefits, occasion, theirs) == belief


def test_the_hard_case_frames_are_the_clouds():
    """219 (`HardCase.ITEM_LEAD`, `TEMPLATE_OCCASION`, `belief`, `said`)."""
    source = _cloud(VECTORS + "HardCase.java")
    assert f'ITEM_LEAD = "{spoken_mod.HARD_CASE_LEAD}";' in source
    assert f'TEMPLATE_OCCASION = "{corpus_mod.HARD_CASE_TEMPLATE_OCCASION}";' in source
    template = "For most, with it, their last {occasion} would have given them {value}."
    assert corpus_mod.ADVANTAGE_BELIEF_TEMPLATE_199 == template
    assert corpus_mod.hard_case_belief(template, "their last job that ran out of memory.") == \
        "For most, with it, their last job that ran out of memory would have given them {value}."
    assert corpus_mod.hard_case_belief(template, None) == template
    assert spoken_mod.hard_case_said("The last time a call dropped.") == "the most recent time a call dropped"
    # Lullaby's (keel-cloud `VectorFixtures.HARD_CASE`), and none: today's anchor
    assert spoken_mod.hard_case_anchor("the last night when you did not know why your baby cried") == \
        "Think of the last night when you did not know why your baby cried."
    assert spoken_mod.advantage_stem("night", "Lullaby", "a phone app", "work out what the baby needs", None, None) == \
        spoken_mod.advantage_stem("night", "Lullaby", "a phone app", "work out what the baby needs")


def test_the_scripted_writers_carry_the_clause_where_the_cloud_reads_it(golden):
    """219 FR-1 / FR-2 (its owed list): the scripted Prevalence carries the hard cases only where an entry holds them
    (none today: no pin moves); the scripted problem card carries the six clause fields in a study without the problem's
    questions, and the gate the card's clause asks is the writer's (`event_base`), so no E10 note."""
    import dataclasses                                                  # noqa: PLC0415
    countly = golden["01-countly"]
    assert vs.HARD_CASES == {} and vs.hard_cases(countly) == {}
    prevalence = vs.calibration_question(countly, "problem.prevalence")
    assert "hard_case" not in prevalence and "hard_case_theirs" not in prevalence
    assert set(vs.problem_result(countly)) == {"statement", "offer_name"}
    solution = dataclasses.replace(countly, scope="SOLUTION")
    card = vs.problem_result(solution)
    assert card["event"] == vs.event_past(countly) == vs.PROBLEM_CLAUSES["01-countly"][0]
    assert (card["routine"], card["went_wrong"]) == vs.ACT_THAT_HURTS["01-countly"]
    assert card["no_sayer"] == vs.NO_SAYERS["01-countly"]
    assert vs.event_base(solution) == vs.PROBLEM_CLAUSES["01-countly"][1]
    assert wording_mod.packed_fault(card["event"], card["went_wrong"]) is None
    assert set(vs.problem_result(dataclasses.replace(countly, scope="COMMERCIAL"))) == {"statement", "offer_name"}


# ----------------------------------------------------------------------------------------------- FR-3: keel-cloud 220

#: keel-cloud `PriceNamesTheIdeaTest`'s cycle-14 beliefs (four of five word for word; AirCaps' people are the cloud
#: fixture's *Deaf or hard-of-hearing adults*, the corpus records *Deaf and ...*).
PRICE_BELIEFS = {
    "08-fresco": "Contractor operations leads would think Fresco worth $800 to $1,000 per site a month.",
    "10-palus": "Startup founders would think a fee of 0.25% of the long-term reserve a year fair for Palus.",
    "17-expanse": "Cluster operators would think Expanse worth $10,000 to $20,000 per cluster a month.",
    "21-codyco": "Hotel group revenue directors would think Codyco worth €3,000 up front, then €1,000 to €1,500 per "
                 "hotel a month.",
}


def _gallery(entry_id: str):
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / f"{entry_id}.yaml"
    if not path.is_file():
        pytest.skip(f"no gallery entry {path}")
    return corpus_mod.load_file(path, registry=fx.registry(), backtest=True)


def test_the_price_question_names_the_idea():
    """220 FR-1 (`CostEstimate.priceQuestion` / `priceSubject`): the idea by its name, else the offer, else *a fix for
    this*; the walk holds the served question to it (`corpus_scenario.price_question_faults`)."""
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    source = _cloud(VECTORS + "CostEstimate.java")
    assert '"What price do you have in mind for " + (subject == null ? "a fix for this" : subject) + "?"' in source
    assert vs.price_question("Fresco", "something for the end-of-day documents") == \
        "What price do you have in mind for Fresco?"
    assert vs.price_question(None, "something for the end-of-day documents") == \
        "What price do you have in mind for something for the end-of-day documents?"
    assert vs.price_question(" ", None) == "What price do you have in mind for a fix for this?"
    view = {"questions": [{"dimension": "commercial.price", "question": "What price do you have in mind for Fresco?"}]}
    assert cs.price_question_faults(view, "Fresco", "something") == []
    assert cs.price_question_faults(view, None, "something") == [
        {"price question": "What price do you have in mind for Fresco?",
         "want": "What price do you have in mind for something?"}]
    assert cs.price_question_faults({"questions": []}, "Fresco", None) == []


@pytest.mark.parametrize("entry_id", ["08-fresco", "10-palus", "13-aircaps", "17-expanse", "21-codyco"])
def test_the_walked_price_question_and_belief_name_the_idea(entry_id):
    """220 FR-1 / FR-2 (spec 141 FR-3): on a study that holds a name, the Price question the walk owes and the belief
    the engine writes over the walker's price (`price_belief_owed`) both name the idea."""
    entry = _gallery(entry_id)
    assert entry.idea_name
    assert vs.price_question(entry.idea_name, (entry.interpretations or {}).get("offer_name")) == \
        f"What price do you have in mind for {entry.idea_name}?"
    belief = vs.price_belief_owed(entry)
    assert entry.idea_name in belief and " it worth " not in belief and "fair for it." not in belief
    if entry_id in PRICE_BELIEFS:
        assert belief == PRICE_BELIEFS[entry_id]
