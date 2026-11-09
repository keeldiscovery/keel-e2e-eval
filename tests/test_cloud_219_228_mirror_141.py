"""Spec 141: the harness mirrors keel-cloud's cycle 14 round (219-228; keel-cloud-docs master `0844a180`, each spec's
tasks.md *Owed: keel-e2e-eval*). No stack, no model, no paid call; the cloud's sources are read from the checkout
`stack.toml` names, skipped without it. The cases are the cloud's own tests' (named beside each).

- FR-4 Commitment (221): the Yes at eleven, the step whole; an act-first smaller step said -ing and kept; data acts.
- FR-5 Prevalence (224): E8 reads the head verb and the verdict words; 06-repeatline's scripted clause off *by hand*.
- FR-2 Relative advantage (219): *Think of {hard_case}.* first; the belief on `hard_case_theirs`; the scripted clause.
- FR-3 Price (220): the question and the belief name the idea; the walk holds the served question.
- FR-6 Current solution (226, 228): `line` or `lineAfter`; the walk leaves the line; W-rung read by name.
- FR-7 Existing sacrifice (222, 227): the loss clause framed where code reads none; a count is a count, the typed unit.
- FR-8 Compatibility and Importance (225, 223): the row's kind (L-kind); the own row from the clause (`OwnRow.fromClause`).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from harness import vectors_script as vs
from instructions import chain as chain_mod
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
#: FR-1: the cards' digest at the round -- keel-cloud `RespondentReview.CARDS_SHA256` at keel-cloud-docs `8b281774`
#: (219-229 merged), moved by eval spec 142 to keel-cloud-docs `1bbe210e` (231 and 230 merged: the Prevalence card
#: amended), then by eval spec 143 to keel-cloud-docs `ac81bf6f` (232 merged: Importance §2 and Current solution §2 --
#: the review may change a row, Put back; was `06fcd867...`), then by eval spec 144 to keel-cloud-docs `9e4b7fda` (233
#: merged: Compatibility §2 -- the review may change a condition, a settled row put aside; was `2f4f0bf8...`), then by
#: eval spec 145 to keel-cloud-docs `74a04fb5` (235 merged: Current solution §2 *The notes* -- the five rewritten as one
#: scale -- and Importance §2 *The notes under the rows* -- a part, a cause or a means put aside; was `98b7379b...`), then
#: by eval spec 147 to keel-cloud-docs `76620269` (236 and 237 merged: Compatibility §2 -- every row read, Keel's
#: included, the suggestion moves; Relative advantage §2, §5, §6 -- the benefits read back, the hard case rewritten, the
#: job in the tail; was `3041f69c...`), then by eval spec 148 to keel-cloud-docs `155eaca9` (238, 239, 240 and 241
#: merged: Prevalence §2 -- the act that hurts read against the segment; Existing sacrifice §2, §6 -- the item names the
#: thing they see go; Ability to pay §2, §5, §6 -- the labels fit every organisation; the steps between 238's
#: `d764f34f...` and 239's `94f9edc6...`; was `42fa94dd...`); the one constant the 213, 216, 232 and 233 pins read for
#: the current copy (re-pinned here when a later spec moves the cards again).
CARDS_SHA256_141 = "78bd11674018b1e2644b2de99256e1fe3c2c781e0f6fca7cefab68fe98e86307"
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
        "what they did, or what happened to the thing, on a given day" + wording_mod.left_standing("day"))


def test_the_unit_is_the_windows_and_have_is_read_whole():
    """224 FR-1 (`wentWrongAllowsTheVerbAndHaveIsReadWhole`)."""
    # spec 142 FR-2 (keel-cloud 231 FR-2): the moment's tail says the unit too
    working = wording_mod.packed_fault(PALUS, None, RecallWindow(5, "WORKING_DAYS"))
    assert "on a given working day;" in working and working.endswith(wording_mod.left_standing("working day"))
    bare = wording_mod.packed_fault(PALUS, None)
    assert "on a given day;" in bare and bare.endswith(wording_mod.left_standing("day"))
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
                  "Think of the last daily log when you lost site notes before writing it. Would it have helped you "
                  "keep an accurate record of the day's work on site better, or not?",
                  "For most, with it, their last daily log where they lost site notes would have given them hours back "
                  "at the end of the day and action items to the crew the same day."),
    "10-palus": ("cash decision", "over the last 3 months, when the company decides where cash from a raise sits until "
                 "it is needed", "Palus", "a treasury account that holds your long-term reserve",
                 "keep the money from a raise safe and earning until the company sends it",
                 "the last time your bank cut the yield on your raise cash",
                 "the last time their bank cut the yield on their raise cash",
                 ["Higher yield on cash not needed for months", "No treasury hire to manage it"],
                 "Think of the most recent time your bank cut the yield on your raise cash. Would Palus, a treasury "
                 "account, have helped you keep the money from a raise safe and earning better, or not?",
                 "For most, with it, the last time their bank cut the yield on their raise cash would have given them "
                 "higher yield on cash not needed for months and no treasury hire to manage it."),
    "13-aircaps": ("conversation", "the last time you tried to follow and join a face-to-face conversation", "AirCaps",
                   "an app", "follow and join a face-to-face conversation",
                   "the last time you lost track of a conversation with hearing people",
                   "the last time they lost track of a conversation with hearing people",
                   ["More of the talk followed without asking for repeats"],
                   "Think of the most recent time you lost track of a conversation with hearing people. Would AirCaps, "
                   "an app, have helped you follow and join a face-to-face conversation better, or not?",
                   "For most, with it, the last time they lost track of a conversation with hearing people would have "
                   "given them more of the talk followed without asking for repeats."),
    "17-expanse": ("job", None, "Expanse", "software on every node that predicts each job's resource needs",
                   "get each job to run to the end without wasting the cluster", "the last job that ran out of memory",
                   "their last job that ran out of memory",
                   ["A job that runs to the end first time", "A shorter wait in the queue"],
                   "Think of the last job that ran out of memory. Would Expanse, software on every node, have helped "
                   "you get each job to run to the end better, or not?",
                   "For most, with it, their last job that ran out of memory would have given them a job that runs to "
                   "the end first time and a shorter wait in the queue."),
    "21-codyco": ("booking call", "the last time booking calls came in on your shift", "Codyco",
                  "an AI reservation agent that answers missed calls", "turn every guest who calls into a booking",
                  "the last time a booking call rang out unanswered", "the last time a booking call rang out unanswered",
                  ["Missed calls turned into bookings", "Callers answered when the desk is busy"],
                  "Think of the most recent time a booking call rang out unanswered. Would Codyco, an AI reservation "
                  "agent, have helped you turn every guest who calls into a booking better, or not?",
                  "For most, with it, the last time a booking call rang out unanswered would have given them missed "
                  "calls turned into bookings and callers answered when the desk is busy."),
}


@pytest.mark.parametrize("entry_id", sorted(HARD_FIVE))
def test_the_five_items_and_beliefs_on_the_hard_case(entry_id):
    """219 FR-4 / FR-5 (`RelativeAdvantageHardCaseTest.theFiveItemsAsServedAndAsReadNow` / `...Beliefs...`): *Think of
    {hard_case}.* first; the belief on `hard_case_theirs`, every benefit kept. Eval spec 147 FR-1 (keel-cloud 237 FR-3):
    the items as keel-cloud now serves them -- the question after the hard case names the job (*have helped you {job}
    better, or not?*), the cap ladder giving way to the what's head, or to *it* (Fresco's ten-word job)."""
    occasion, stem, name, what, job, hard, theirs, benefits, item, belief = HARD_FIVE[entry_id]
    assert spoken_mod.advantage_stem(occasion, name, what, job, stem, hard) == item
    anchor = spoken_mod.hard_case_anchor(hard)
    assert item.startswith(anchor + " Would ") and item.endswith(spoken_mod.helped_tail(job))
    assert spoken_mod.DONE_BETTER not in item
    assert item[len(anchor) + 1:] == spoken_mod.advantage_question(name, what, job)
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


# ------------------------------------------------------------------------------------------ FR-6: keel-cloud 226, 228

def test_the_line_is_read_from_line_or_line_after():
    """226 FR-3 (contract 61, `VectorDtos.SavedListDto.lineAfter`: the index of the rung the line follows, `line` - 1):
    the walk reads `line` where served, else `lineAfter` + 1; the two disagreeing is named."""
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    dtos = _cloud("src/main/java/com/keeldiscovery/cloud/protocol/founder/VectorDtos.java")
    # eval spec 143 (keel-cloud 232 FR-3, contract 62): the record gains `putAside` and `changed` after `lineAfter`
    assert "Integer line,\n            DurationDto duration, Integer lineAfter, List<PutAsideDto> putAside, ChangedDto " \
           "changed)" in dtos
    assert "({@code line} - 1)" in dtos
    assert cs.served_line({"line": 2, "lineAfter": 1}) == 2
    assert cs.served_line({"lineAfter": 2}) == 3
    assert cs.served_line({"line": 1}) == 1 and cs.served_line({}) is None and cs.served_line(None) is None
    assert cs.line_after_faults({"line": 2, "lineAfter": 1}) == []
    assert cs.line_after_faults({"line": 2}) == [] and cs.line_after_faults({"lineAfter": 3}) == []
    assert cs.line_after_faults({"line": 2, "lineAfter": 2}) == [{"line": 2, "lineAfter": 2, "want lineAfter": 1}]


def test_the_walk_leaves_the_line_where_it_is_drawn(golden):
    """226 FR-3 (its owed list): the walk sends no `lineAfter` (absent: the draft's line stands), so the brief's bar
    names the saved line's rung as before (`brief_facts.current_solution_bar` stands); the golden Countly and Linerly
    ladders take W-rung's one repair turn, read by name and never counted (`backtest.LOCK_NOTES`)."""
    from evals import backtest as bt                                    # noqa: PLC0415
    from instructions import brief_facts as bf                          # noqa: PLC0415
    key = "problem.current_solution_satisfaction"
    for entry in golden.values():
        saved = vs.saved_list(entry, key)
        assert "lineAfter" not in saved, entry.id
    assert bf.current_solution_bar("Got it right after one wrong guess") == \
        "holds if at least 2 in 3 land below 'Got it right after one wrong guess'"
    assert "keel-cloud 226" in bt.LOCK_NOTES["W-rung"]
    measure = _cloud(VECTORS + "MeasureRung.java")
    assert 'Optional.of("W-rung: ' in measure
    found = bt.lock_notes(None, [{"screen": "CALIBRATION_QUESTIONS",
                                  "detail": "breach result.questions[1].list.items[2].label: W-rung: 'Counted twice' "
                                            "leaves the founder's measure"}])
    assert [n["rule"] for n in found] == ["W-rung"]


def test_the_two_boxes_stand_as_spec_140_read_them():
    """228 (contract 60): the draft's `answer` and `how` -- read since spec 140 FR-4b (`vectors_screens.sent_how`,
    `corpus_scenario.answer_boxes_faults`); nothing more owed here."""
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    from harness import vectors_screens as vs_screens                   # noqa: PLC0415
    assert callable(vs_screens.sent_how) and callable(cs.answer_boxes_faults)


# ------------------------------------------------------------------------------------------ FR-7: keel-cloud 222, 227

#: keel-cloud `SacrificeItemNamesTheLossTest.CLAUSES`: the clause a writer following the rule would write.
LOSS_CLAUSES = {"21-codyco": "rang out unanswered", "13-aircaps": "did you stop following the thread of",
                "10-palus": "went unearned at the bank", "17-expanse": "went unused by any job",
                "08-fresco": "went into the daily log"}
#: `theFiveEntries`: (wanted, as cycle 14 served it, with the clause).
LOSS_ITEMS = {
    "21-codyco": (True, "Last month, about what percent of the reservation calls did you go without in booking calls "
                        "that rang out unanswered?",
                  "Last month, about what percent of the reservation calls rang out unanswered?"),
    "13-aircaps": (True, "Last month, about how many conversations fell through?",
                   "Last month, about how many conversations did you stop following the thread of?"),
    "10-palus": (True, "Last year, about what percent of the long-term reserve did you go without?",
                 "Last year, about what percent of the long-term reserve went unearned at the bank?"),
    "17-expanse": (False, "Last month, about what percent of the reserved GPU hours sat idle?", None),
    "08-fresco": (False, "Last month, about how many hours per site did your team spend on the daily log?", None),
}


@pytest.mark.parametrize("entry_id", sorted(LOSS_ITEMS))
def test_the_sacrifice_item_names_the_loss(entry_id):
    """222 FR-1 / FR-4 (`SacrificeItemNamesTheLossTest.theFiveEntries`): the writer is wanted on the three gaps alone;
    the clause in the frame there; the two code reads word for word as before with the field present."""
    entry = _gallery(entry_id)
    team, cost, job = vs.is_b2b(entry), entry.cost(), entry.context.get("job")
    wanted, before, now = LOSS_ITEMS[entry_id]
    assert vs.loss_clause_wanted(team, entry.occasion(), cost) is wanted
    assert vs.cost_question(team, entry.occasion(), job, cost) == before
    assert vs.cost_question(team, entry.occasion(), job, cost, LOSS_CLAUSES[entry_id]) == (now or before)


def test_the_loss_clause_frames_and_the_scripted_part_one():
    """222 (`LossClause.said`, `lossClauseFrames`, the part-1 result's optional `loss_clause`): a clause opening on the
    thing is cut to its verb phrase, one on the person turned to a question's order; the scripted part 1 carries none
    today (`LOSS_CLAUSES` empty: no golden line falls to a neutral verb), so no item moves."""
    applier = _cloud(VECTORS + "LossClause.java")
    assert 'FIELD = "loss_clause";' in applier
    assert vs.loss_clause_said("booking calls that rang out unanswered", "the reservation calls", None) == \
        "rang out unanswered"
    assert vs.loss_clause_said("you stopped following the thread of", None, "conversations") == \
        "did you stop following the thread of"
    assert vs.loss_clause_said("you were cut off.", None, "calls") == "were you cut off"
    assert vs.loss_clause_frames("Last month", "rang out", "the calls", None) == [
        "Last month, about what percent of the calls rang out?", "Last month, what percent of the calls rang out?"]
    assert vs.loss_clause_question("Last month", "lost the thread", None, "conversations") is None, "never lose"
    assert vs.LOSS_CLAUSES == {}
    assert vs.scripted_loss_clause(_gallery("13-aircaps")) is None


#: keel-cloud `SacrificeHeadingNamesThePayerTest`'s costs (revision 25) and the sentences 227 stores.
COSTS_227 = {
    "10-palus": ({"mode": "RATE", "low": 2, "high": 2, "measure": "%", "base": "the long-term reserve", "unit": "company",
                  "period": "year", "currency": "USD",
                  "lossPhrase": "Yield they gave up by leaving the reserve at the bank"},
                 dict(b2b=True, paying="venture-backed startups", actor="startup founder",
                      actor_plural="startup founders"),
                 "about 2% of the long-term reserve per company a year",
                 "About 2% of the long-term reserve per company a year: yield they gave up by leaving the reserve at "
                 "the bank."),
    "13-aircaps": ({"mode": "RATE", "low": 12, "high": 12, "measure": "conversations",
                    "base": "the conversations they are in", "unit": "person", "period": "month", "currency": "USD",
                    "lossPhrase": "Conversations they lost the thread of"},
                   dict(b2b=False, paying=None, actor="deaf or hard-of-hearing adult",
                        actor_plural="deaf and hard-of-hearing adults"),
                   "about 12 conversations per person a month",
                   "Deaf and hard-of-hearing adults already lose about 12 conversations per person a month: "
                   "conversations they lost the thread of."),
    "17-expanse": ({"mode": "RATE", "low": 30, "high": 59, "measure": "%", "base": "the reserved GPU hours",
                    "unit": "cluster", "period": "month", "currency": "USD",
                    "lossPhrase": "Reserved GPU hours that sit idle"},
                   dict(b2b=True, paying=None, actor="researcher", actor_plural="researchers and ML engineers"),
                   "about 30% to 59% of the reserved GPU hours per cluster a month",
                   "About 30% to 59% of the reserved GPU hours per cluster a month: reserved GPU hours that sit idle."),
    "21-codyco": ({"mode": "RATE", "low": 5, "high": 5, "measure": "%", "base": "the reservation calls", "unit": "hotel",
                   "period": "month", "currency": "EUR", "lossPhrase": "Booking calls that rang out unanswered"},
                  dict(b2b=True, paying="hotel groups", actor="reservation agent", actor_plural="reservation agents"),
                  "about 5% of the reservation calls per hotel a month",
                  "About 5% of the reservation calls per hotel a month: booking calls that rang out unanswered."),
}


@pytest.mark.parametrize("entry_id", sorted(COSTS_227))
def test_a_count_is_a_count_and_the_unit_is_the_founders(entry_id):
    """227 FR-2 / FR-3 (`SacrificeHeadingNamesThePayerTest.theFiveEntries`): the stored sentence and the phrase -- a
    count *about 12 conversations per person a month* (no *of {base}*, never a %), the typed unit kept beside a percent
    of a named base."""
    cost, who, said, belief = COSTS_227[entry_id]
    assert chain_mod.cost_said(cost, None, "operator") == said
    assert chain_mod.cost_belief(cost, None, "operator", "the deciders", **who) == belief


def test_the_unit_is_typed_or_none_and_the_recorded_words_read_by_227s_rule():
    """227 FR-3 (`theUnitIsTheFounders`) and `VectorCorpusFixture.spec227Cost`: no unit typed, no *per*, never the role
    word; revision 25's words read as 227 writes them until a revision records them."""
    no_unit = {**COSTS_227["21-codyco"][0], "unit": None}
    assert chain_mod.cost_said(no_unit, None, "director") == "about 5% of the reservation calls a month"
    assert chain_mod.cost_belief(no_unit, None, "director", "x", True, paying="hotel groups") == \
        "About 5% of the reservation calls a month: booking calls that rang out unanswered."
    count_no_unit = {**COSTS_227["13-aircaps"][0], "unit": None}
    assert chain_mod.cost_said(count_no_unit, None, "wearer") == "about 12 conversations a month"
    clusters = {**COSTS_227["17-expanse"][0], "base": "the cluster's GPU hours"}
    assert chain_mod.cost_said(clusters, None, "operator") == "about 30% to 59% of the cluster's GPU hours a month"
    aircaps, who = COSTS_227["13-aircaps"][0], COSTS_227["13-aircaps"][1]
    assert corpus_mod.spec227_cost("about 12 conversations of the conversations they are in per person a month",
                                   aircaps, None, who["actor"], who["actor_plural"], False, True) == \
        "about 12 conversations per person a month"
    assert corpus_mod.spec227_cost("About 12 of the conversations they are in per person a month: conversations they "
                                   "lost the thread of.", aircaps, None, who["actor"], who["actor_plural"], False,
                                   False) == COSTS_227["13-aircaps"][3]
    expanse = COSTS_227["17-expanse"][0]
    assert corpus_mod.spec227_cost("About 30% to 59% of the reserved GPU hours a month: reserved GPU hours that sit "
                                   "idle.", expanse, None, "researcher", "researchers", True, False) == \
        COSTS_227["17-expanse"][3]
    fixture = _cloud("src/test/java/com/keeldiscovery/cloud/corpus/VectorCorpusFixture.java")
    assert "public static String spec227Cost(String recorded, CalibrationAnswer.Cost cost," in fixture


# ------------------------------------------------------------------------------------------ FR-8: keel-cloud 225, 223

def test_compatibility_rows_say_their_kind(golden):
    """225 FR-1 (`ScreenResultApplier.rowKinds` / `heldKind`, `SavedList.KINDS`, L-kind): the scripted writer writes
    `kind` beside `settled_by`, the word test's own reading, so no L-kind repair turn is spent and today's frame stands;
    a row with none, an allower written other than permission, a could-row written fact without its why are faults."""
    from instructions import score as score_mod                         # noqa: PLC0415
    saved = _cloud(VECTORS + "SavedList.java")
    assert re.search(r'KINDS = (?:java\.util\.)?List\.of\("ability", "fact", "permission"\)', saved) and \
        spoken_mod.KINDS == ("ability", "fact", "permission")
    for entry in golden.values():
        rows = vs.drafted_list(entry, "solution.compatibility")["items"]
        assert rows and all(r["kind"] == spoken_mod.held_kind(r) for r in rows), entry.id
        assert score_mod.kind_faults(rows) == [], entry.id
    assert score_mod.kind_faults([{"label": "They had a phone to hand"}])[0].startswith("L-kind: write kind on")
    allowed = {"label": "Their manager allowed them to install apps", "kind": "ability"}
    assert "so it is a permission, not ability" in score_mod.kind_faults([allowed])[0]
    could = {"label": "could forward unanswered calls to another number", "kind": "fact"}
    assert "opens on 'could'" in score_mod.kind_faults([could])[0]
    assert score_mod.kind_faults([{**could, "kind_why": "the hotel's phone system is set up by IT"}]) == []
    assert spoken_mod.kind_of("permission", "could you have forwarded calls", "could forward calls") == "PERMISSION"
    assert spoken_mod.kind_of(None, "did you have your phone to hand", "They had a phone to hand") == "FACT"


#: keel-cloud 223's owed list (the golden seven) and its tasks.md table (cycle 14's five): code's own row from the clause.
OWN_ROWS_223 = {
    "01-countly": "Recounting stock by hand after a mismatched delivery",
    "02-compliancelog": "Pulling training completions into a spreadsheet by hand",
    "03-lullaby": "Knowing why the baby cried",
    "04-linerly": "Losing time to a puncture riding",
    "05-paidly": "Waiting beyond agreed terms to be paid",
    "06-repeatline": "Typing a refill request in by hand",
    "07-mulchrun": "Waiting at the supply yard for mulch",
}
CLAUSE_ROWS_223 = {
    "lost site notes before writing the daily log": "Losing site notes before writing the daily log",
    "had their bank cut the yield on their raise cash": "Having their bank cut the yield",
    "lost track of a face-to-face conversation with hearing people":
        "Losing track of a face-to-face conversation with hearing people",
    "had a job run out of memory": "Having a job run out of memory",
    "had a booking call ring out unanswered": "Having a booking call ring out unanswered",
}


def test_the_own_row_is_codes_from_the_clause(golden):
    """223 FR-1 (`OwnRow.fromClause`, `ScreenResultApplier.codesOwnRow`): every scripted PROBLEM run serves code's own row
    from `went_wrong` in place of the registry's -- the Check draws it and the belief names it (the walk's strict read);
    cycle 14's five as 223's table pins them; *had to* and a negation read past, a subject pronoun dropped, the cut."""
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    from instructions import writers_rules as writers_mod               # noqa: PLC0415
    _cloud(VECTORS + "OwnRow.java")
    for entry_id, row in OWN_ROWS_223.items():
        entry = golden[entry_id]
        assert writers_mod.own_row_from_clause(vs.ACT_THAT_HURTS[entry_id][1]) == row
        # spec 141 FR-8 (keel-cloud 229): the writer's act takes the place where it holds -- 223's row is the fallback
        own = vs.code_own_row(entry)
        assert own == (vs.own_row_act(entry) or row)
        assert cs._corpus_list(entry, "problem.importance")["items"][0] == own
    for clause, row in CLAUSE_ROWS_223.items():
        assert writers_mod.own_row_from_clause(clause) == row, clause
    assert writers_mod.own_row_from_clause("they had to sort the photos by hand") == "Sorting the photos by hand"
    assert writers_mod.own_row_from_clause("") is None and writers_mod.own_row_from_clause("photos") is None
    import dataclasses                                                  # noqa: PLC0415
    assert vs.code_own_row(dataclasses.replace(golden["01-countly"], scope="SOLUTION")) is None
    linerly = golden["04-linerly"]
    belief = cs.importance_belief_on_code_own_row(linerly, corpus_mod.engine_belief(linerly, "problem.importance"))
    assert belief.endswith("Fixing a puncture on the way to work is one of the two they would most like made easier.")
    lullaby = golden["03-lullaby"]               # 229: the act the card names is the registry's row, so nothing moves
    assert cs.importance_belief_on_code_own_row(lullaby, corpus_mod.engine_belief(lullaby, "problem.importance")) == \
        corpus_mod.engine_belief(lullaby, "problem.importance")


def test_the_founders_own_row_note(golden):
    """223 FR-2 (`OwnRow.NOTE`, `OwnRow.note`): the note under a saved own row the founder reworded into the job or the
    circumstance said again; none on Keel's row saved unchanged (the scripted Save) or on a row that names the hurt."""
    from instructions import writers_rules as writers_mod               # noqa: PLC0415
    assert f'NOTE = "{writers_mod.OWN_ROW_NOTE[:60]}' in _cloud(VECTORS + "OwnRow.java").replace('"\n            + "', "")
    job, circumstance = "settle the baby", "the baby cries in the night"
    keels = "Knowing why the baby cried"
    assert writers_mod.own_row_note(keels, keels, job, circumstance) is None
    assert writers_mod.own_row_note("knowing why the baby cried.", keels, job, circumstance) is None
    assert writers_mod.own_row_note("Settling the baby", keels, job, circumstance, "parents") == writers_mod.OWN_ROW_NOTE


# ----------------------------------------------------------------------------------------------- FR-1: the digest

def test_the_reader_digest_is_the_clouds_vendored_cards():
    """FR-1: `quality/readers/dimensions.md` is keel-cloud's `src/main/resources/keel/dimension-cards.md` byte for byte,
    its sha256 the cloud's `CARDS_SHA256` -- the round's digest (`CARDS_SHA256_141`)."""
    import hashlib                                                      # noqa: PLC0415
    from quality import cards                                           # noqa: PLC0415
    review = _cloud(APPLICATION + "RespondentReview.java")
    sha = re.search(r'CARDS_SHA256 = "([0-9a-f]{64})"', review).group(1)
    ours = cards.CARDS_PATH.read_bytes()
    assert (KEEL_CLOUD / "src/main/resources/keel/dimension-cards.md").read_bytes() == ours
    assert hashlib.sha256(ours).hexdigest() == sha == CARDS_SHA256_141
    text = " ".join(ours.decode("utf-8").split())
    assert "Think of {hard_case}." in text and "hard_case_theirs" in text             # 219
    assert "keel-cloud 222" in text                                                    # 222


#: keel-cloud 229's owed list: the golden seven's acts (A1, A2, A4 checked by the cloud's builder by hand; A3 here).
OWN_ROW_ACTS_229 = {
    "01-countly": "Recounting stock by hand after a mismatched delivery",
    "02-compliancelog": "Pulling training completions into a spreadsheet by hand",
    "03-lullaby": "Knowing what the cry means",
    "04-linerly": "Fixing a puncture on the way to work",
    "05-paidly": "Chasing payment on an approved invoice past its terms",
    "06-repeatline": "Typing a refill request in by hand",
    "07-mulchrun": "Getting mulch loaded at the supply yard",
}
#: `ImportanceOwnRowAsAnActTest.ACTS` over `RelativeAdvantageHardCaseTest.FIVE` (went_wrong, hard_case, job, stem,
#: occasion, people, name).
ACTS_229 = {
    "Fresco": ("Keeping site notes until the daily log is written", HARD_FIVE["08-fresco"], "construction "
               "superintendent", "construction superintendents", "lost site notes before writing the daily log"),
    "Palus": ("Moving raise cash when the bank cuts its yield", HARD_FIVE["10-palus"], "finance lead", "finance leads",
              "had their bank cut the yield on their raise cash"),
    "AirCaps": ("Following a fast or noisy conversation with hearing people", HARD_FIVE["13-aircaps"],
                "deaf or hard-of-hearing adult", "deaf or hard-of-hearing adults",
                "lost track of a face-to-face conversation with hearing people"),
    "Expanse": ("Sizing a job's memory so it never runs out", HARD_FIVE["17-expanse"], "researcher",
                "researchers and ML engineers", "had a job run out of memory"),
    "Codyco": ("Picking up booking calls before they ring out", HARD_FIVE["21-codyco"], "reservation agent",
               "reservation agents", "had a booking call ring out unanswered"),
}


def _act_fault(name: str, act: str):
    from instructions import writers_rules as writers_mod               # noqa: PLC0415
    _, five, actor, actors, went_wrong = ACTS_229[name]
    occasion, stem, idea, _what, job, hard = five[:6]
    return writers_mod.own_row_act_fault(act, went_wrong, hard, job, stem, occasion, [actor, actors], [idea], "")


def test_the_own_row_is_the_writers_act_held_by_a1_to_a4(golden):
    """229 FR-2 (`ImportanceOwnRowAsAnActTest.theFiveActsPass` and its refusals; `OwnRowAct.fault`, `OwnRow.outcomeVerb`):
    the five cycle-14 acts pass, 223's rows for the same clauses are refused A2; each test refuses its own case; the
    golden seven's acts (229's owed list) hold A1-A4 on each entry's own words, so the scripted Importance question
    carries them as `own_row` and the walk expects them."""
    from instructions import writers_rules as writers_mod               # noqa: PLC0415
    source = KEEL_CLOUD / VECTORS / "OwnRowAct.java"                   # on keel-cloud master once 229 merges
    assert not source.is_file() or 'FIELD = "own_row";' in source.read_text(encoding="utf-8")
    assert writers_mod.OWN_ROW_FIELD == "own_row"
    for name, (act, *_rest) in ACTS_229.items():
        assert _act_fault(name, act) is None, name
        before = writers_mod.own_row_from_clause(ACTS_229[name][4])
        assert _act_fault(name, before).startswith("A2: "), (name, before)
    assert writers_mod.own_row_outcome_verb("lost site notes before writing the daily log") == "lose"
    assert writers_mod.own_row_outcome_verb("had to sort photos") is None
    assert _act_fault("Fresco", "Sorting the day's photos by hand for the log").startswith(
        "A1: own_row 'Sorting the day's photos by hand for the log' shares no word")
    assert _act_fault("Expanse", "Sizing a job so it neither fails nor wastes GPUs").startswith("A1: ")
    assert _act_fault("Fresco", "Site notes kept until the daily log is written").startswith(
        "A2: own_row 'Site notes kept until the daily log is written' opens on")
    assert _act_fault("Fresco", "Losing site notes before the log is written").startswith(
        "A2: own_row 'Losing site notes before the log is written' heads on")
    assert "heads on 'having'" in _act_fault("Expanse", "Having a job's memory run out")
    assert _act_fault("Fresco", "Keeping an accurate record of site work").startswith(
        "A3: own_row 'Keeping an accurate record of site work' is the job or the")
    assert "is 11 words; at most 9" in _act_fault("Fresco", "Keeping every site note safe until the daily log is written")
    assert "the idea's name ('Fresco')" in _act_fault("Fresco", "Keeping site notes in Fresco for the log")
    assert "'3', a number the founder did not write" in _act_fault("Fresco", "Keeping 3 site notes until the log is written")
    assert writers_mod.own_row_act_fault(" ", WENT_WRONG, None, None, None, None) is None
    assert writers_mod.own_row_act_clean(" picking up booking calls before they ring out. ") == \
        "Picking up booking calls before they ring out"
    assert vs.OWN_ROW_ACTS == OWN_ROW_ACTS_229
    for entry_id, act in OWN_ROW_ACTS_229.items():
        entry = golden[entry_id]
        assert vs.own_row_act_fault(entry, act) is None, entry_id
        assert vs.calibration_question(entry, "problem.importance")["own_row"] == act
        assert vs.calibration_question(entry, "problem.importance", first=True)["own_row"] == act
        assert vs.code_own_row(entry) == act
    import dataclasses                                                  # noqa: PLC0415
    assert "own_row" not in vs.calibration_question(dataclasses.replace(golden["01-countly"], scope="SOLUTION"),
                                                   "problem.importance")
