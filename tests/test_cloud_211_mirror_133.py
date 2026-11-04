"""Spec 133 -- the harness mirrors keel-cloud 211 and keel-web 171 (their tasks.md, *Owed elsewhere*: keel-e2e-eval). No
stack, no model, no paid call; the cloud's and the web's sources are read from the checkouts `stack.toml` names
(keel-cloud-docs master `e485abeb`, keel-web master `2523777e`), skipped without them.

- FR-1 `L33` and `L34` by name (`backtest.LOCK_NOTES`, `instructions/score.py`), `X8` refusing one dropped founder word
  (`qualifiers.x8`), each on cycle 10's cases as keel-cloud's `CycleTenCodeDefectsTest` reads them.
- FR-2 the scripted writer: priced Commitment steps carry Keel's free smaller step with its reason; Buyer and payer rows
  are roles the Answer typed; the context result keeps every founder word of WHAT and WHEN.
- FR-3 the pins: the Commitment Answer question, the untimed Purchase friction belief, Prevalence's whole segment, the
  *who answers* label, Relative advantage's every benefit, the typist fixture's *Four*.
- FR-4 the Commitment card's good example carries its free smaller step; nothing else in the cards moved, and the cloud's
  vendored copy is owed.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

from evals import backtest as bt
from harness import qualifiers as q
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from instructions import friction as friction_mod
from instructions import registry as registry_mod
from instructions import score as score_mod
from instructions import step_cost as step_cost_mod
from quality import cards
from stack.config import load_config

CONFIG = load_config(validate=False)
KEEL_CLOUD = Path(CONFIG.keel_cloud)
REPO = Path(__file__).resolve().parents[1]
VECTORS = "src/main/java/com/keeldiscovery/cloud/domain/vectors/"
APPLICATION = "src/main/java/com/keeldiscovery/cloud/application/"
FOUNDER = "src/main/java/com/keeldiscovery/cloud/protocol/founder/"
TESTS = "src/test/java/com/keeldiscovery/cloud/"
BP = registry_mod.BUYER_KEY
COMMITMENT = registry_mod.COMMITMENT_KEY
CODYCO_DECIDER = "hotel group revenue director"
#: keel-cloud 211's `CycleTenCodeDefectsTest.onlyTypedRolesAreRows`: the people every list may name besides the Answer.
CODYCO_NAMED = (CODYCO_DECIDER, "director", "reservation agent", "reservation agents")


def _cloud(rel: str) -> str:
    path = KEEL_CLOUD / rel
    if not path.is_file():
        pytest.skip(f"no {rel} at {KEEL_CLOUD}")
    return path.read_text(encoding="utf-8")


def _joined(java: str) -> str:
    """A Java source with its string concatenations joined (`"a " + "b"` -> `"a b"`)."""
    return re.sub(r'"\s*\+\s*"', "", java)


@pytest.fixture(scope="module")
def entries() -> list:
    from instructions import corpus as c                               # noqa: PLC0415
    if not c.corpus_dir(KEEL_CLOUD).is_dir() or not c.backtest_dir(KEEL_CLOUD).is_dir():
        pytest.skip(f"no corpus at {KEEL_CLOUD}")
    return [*vs.load(KEEL_CLOUD).entries, *vs.load(KEEL_CLOUD, backtest=True).entries]


def _dimension(key: str):
    """A list dimension as `score.list_faults` reads it (the registry's controls and saves for the two read here)."""
    if key == BP:
        return SimpleNamespace(key=key, founder_control="role_list", part=3,
                               saves={"min_items": 1, "max_items": 3, "max_words": 4, "fixed_first": {"code":
                                                                                                     "nobody_else"}})
    return SimpleNamespace(key=key, founder_control="one_step", part=3,
                           saves={"min_items": 1, "max_items": 2, "max_words": 9})


def _roles(*labels: str) -> list[dict]:
    return [{"code": "nobody_else", "label": "Nobody else"}] + [{"code": f"role_{i + 1}", "label": label}
                                                                 for i, label in enumerate(labels)]


# ------------------------------------------------------------------------------------- FR-1: L33, L34, X8 by name

def test_l33_l34_and_x8_are_lock_notes_by_name():
    for rule in ("L33", "L34", "X8"):
        assert rule in bt.LOCK_NOTES and "keel-cloud 211" in bt.LOCK_NOTES[rule], rule
    rows = [{"screen": "CALIBRATION_QUESTIONS", "detail": "breach result.questions[0].list.items[2].label: L33: 'The "
             "finance director' is a role the founder did not type in this Answer (\"The hotel's owner\"); a row is ..."},
            {"screen": "CALIBRATION_QUESTIONS", "founderNote": "L34: 'pay for a money-back pilot at one hotel' costs the "
             "person money ('pay'); a step that costs money, data or a signature takes a second item"},
            {"screen": "CONTEXT_INTERPRET", "turns": [{"content": "X8: the circumstance drops the founder's own words "
                                                                  "['bokoing'] (they wrote \"...\")"}]}]
    found = bt.lock_notes(None, rows)
    assert [n["rule"] for n in found] == ["L33", "L34", "X8"]
    assert all(n["means"] == bt.LOCK_NOTES[n["rule"]] for n in found)


def test_the_cloud_names_l33_l34_and_x8_as_the_harness_restates_them():
    applier = _joined(_cloud(APPLICATION + "ScreenResultApplier.java"))
    assert '"L33: \'"' in applier and "' is a role the founder did not type in this Answer (\\\"" in applier
    assert '"L34: \'" + step + "\' costs the person "' in applier
    assert "costs the person \" + its.kind()" in applier or '"person " + its.kind()' in applier
    # X8 holds a founder word at zero (was `dropped.size() > most`), a preposition aside
    assert applier.count("if (!dropped.isEmpty() || added.size() > most) {") == 2
    assert "dropped.size() > most ||" not in applier
    prepositions = re.search(r"PREPOSITIONS = java\.util\.Set\.of\(([^)]*)\)", applier).group(1)
    assert set(re.findall(r'"([a-z]+)"', prepositions)) == set(q.PREPOSITIONS)
    # L34 runs after L15 and L27, on Commitment alone
    assert applier.index("L34 --") > applier.index("L27") and applier.index("L34 --") > applier.index("L15")


def test_step_cost_is_the_clouds_vocabulary():
    """`instructions.step_cost` restates `StepCost`'s three closed vocabularies word for word."""
    java = _joined(_cloud(VECTORS + "StepCost.java"))
    for name, pattern in (("MONEY_WORDS", step_cost_mod.MONEY_WORDS), ("SIGNATURE_WORDS", step_cost_mod.SIGNATURE_WORDS),
                          ("DATA_WORDS", step_cost_mod.DATA_WORDS)):
        theirs = re.search(name + r' = Pattern\.compile\("(.*?)"\);', java).group(1)
        theirs = theirs.replace("\\\\", "\\").replace("(?i)", "")
        ours = pattern.pattern.replace("(?i)", "")
        if name == "DATA_WORDS":
            # Java's one variable-length look-behind is five fixed-length ones in Python
            theirs = theirs.replace("(?<!sample |demo |test |example |dummy )", "")
            ours = re.sub(r"\(\?<!\w+ \)", "", ours)
        assert ours == theirs, name
    assert 'MONEY = "money"' in java and 'DATA = "data"' in java and 'SIGNATURE = "a signature"' in java


def test_step_cost_reads_the_steps_words():
    """keel-cloud 211 `stepCostReadsTheStepsWords`, case for case."""
    assert step_cost_mod.of("pay €3,000 for a money-back pilot at one hotel").kind == step_cost_mod.MONEY
    assert step_cost_mod.of("start a paid pilot on one site").word == "paid"
    assert step_cost_mod.of("order a pair with free returns").word == "order"
    assert step_cost_mod.of("let us run a trial on their cluster data").kind == step_cost_mod.DATA
    assert step_cost_mod.of("sign a letter of intent for the agent").kind == step_cost_mod.SIGNATURE
    for free in ("allow it to use the microphone at night", "a free trial at one hotel", "a demo on sample data",
                 "a look at a working unit", "a short call about the agent", "sign up for the free plan"):
        assert step_cost_mod.of(free) is None, free
    # spec 137 FR-2 (keel-cloud 213 FR-8, `CycleTenCodeDefectsTest` re-pinned likewise): moved money is money --
    # *in order to* is still no order
    assert step_cost_mod.of("move idle cash in order to see the rate") == step_cost_mod.Cost(step_cost_mod.MONEY, "move")


def test_l34_a_priced_step_takes_a_free_one():
    """keel-cloud 211 `aPricedStepTakesAFreeOne`: alone, refused by name; with a free smaller step, none; a smaller
    step that costs something itself, refused; a step that costs nothing, none -- and `score.list_faults` names it."""
    answer = "pay for a money-back pilot at one hotel"
    assert step_cost_mod.l34([answer]).startswith("L34: 'pay for a money-back pilot at one hotel' costs the person "
                                                 "money ('pay')")
    assert step_cost_mod.l34([answer, "A free test call on the overflow line"]) is None
    assert step_cost_mod.l34([answer, "A paid workshop first"]).startswith(
        "L34: 'A paid workshop first' costs the person money ('paid') itself")
    assert step_cost_mod.l34(["allow it to use the microphone at night"]) is None
    alone = score_mod.list_faults({"key": COMMITMENT, "list": {"items": [{"label": answer}]}}, _dimension(COMMITMENT))
    assert [f for f in alone if f.startswith("L34: ")]
    free = {"key": COMMITMENT, "list": {"items": [{"label": answer}, {"label": "A free test call on the overflow line",
                                                                    "reason": "the pilot costs money"}]}}
    assert not [f for f in score_mod.list_faults(free, _dimension(COMMITMENT)) if f.startswith("L34")]


def test_l33_only_typed_roles_are_rows():
    """keel-cloud 211 `onlyTypedRolesAreRows`: Codyco's finance director refused where the Answer typed the owner alone,
    both kept where it typed both, the decider and the agent passing; Palus's board, typed."""
    drafted = _roles("The hotel's owner", "The finance director")
    fault = score_mod.untyped_role(drafted, "The hotel's owner", CODYCO_NAMED)
    assert fault.startswith("L33: 'The finance director' is a role the founder did not type in this Answer "
                            "(\"The hotel's owner\")")
    assert score_mod.untyped_role(drafted, "The hotel's owner; The finance director", CODYCO_NAMED) is None
    assert score_mod.untyped_role(_roles("Hotel group revenue director", "Reservation agent"), "The hotel's owner",
                                  CODYCO_NAMED) is None
    assert score_mod.untyped_role(_roles("The board"), "The board", ("founder",)) is None
    # on the draft, where the Answer is typed (a redraft); never on the seed-time job, which has none
    question = {"key": BP, "list": {"items": [{"label": r["label"]} for r in drafted[1:]]}}
    faults = score_mod.list_faults(question, _dimension(BP), answers={BP: "The hotel's owner"}, named=CODYCO_NAMED)
    assert [f for f in faults if f.startswith("L33: 'The finance director'")]
    assert not [f for f in score_mod.list_faults(question, _dimension(BP)) if f.startswith("L33")]


def test_x8_every_founder_word_lands():
    """keel-cloud 211 `everyFounderWordLands`: the five entries' cycle-10 read-backs, each refused naming the word it
    dropped, and their whole versions passing."""
    codyco_when = ("bokoing calls come in on every shift, after hours, at peak and on holidays, and not every one gets "
                   "answeed")
    codyco_what = "turn everry guest who calls into a booking"
    faults = q.x8(codyco_what, codyco_when, "turn every guest who calls into a booking",
                  "calls come in on every shift, after hours, at peak and on holidays, and not every one gets answered")
    assert any(f.startswith("X8: the circumstance drops the founder's own words") and "'bokoing'" in f for f in faults)
    assert q.x8(codyco_what, codyco_when, "turn every guest who calls into a booking",
                "booking calls come in on every shift, after hours, at peak and on holidays, and not every one gets "
                "answered") == []
    palus = ("keep the money from a raise safe and earning until the company sends it",
             "the company decides where cash from a raise sits until it is needded")
    assert any("'raise'" in f for f in q.x8(*palus, palus[0], "they decide where cash sits until it is needed"))
    assert q.x8(*palus, palus[0], "the company decides where cash from a raise sits until it is needed") == []
    fresco = ("keep an accurate rcord of the day's work on site",
              "the day's site walks are done and the photoss and notes still have to go into the dailyy log")
    fresco_job = "keep an accurate record of the day's work on site"
    assert any("'site'" in f for f in q.x8(*fresco, fresco_job, "the walks are done and the photos and notes still "
                                                                "have to go into the daily log"))
    assert q.x8(*fresco, fresco_job, "the day's site walks are done and the photos and notes still have to go into "
                                     "the daily log") == []
    expanse_when = "a job is ready to sbmit and its memory, GPUs and run time have to be guessed frst"
    expanse_what = "get each job to run to the end without wasting the clusterr"
    submit = "a job is ready to submit and its memory, GPUs and run time have to be guessed first"
    assert any(f.startswith("X8: the job drops the founder's own words") and "'run'" in f
               for f in q.x8(expanse_what, expanse_when, "get each one to the end without wasting the cluster", submit))
    assert q.x8(expanse_what, expanse_when, "get each job to run to the end without wasting the cluster", submit) == []
    aircaps = ("follow and join a face-to-face covnersation",
               "a conversation with hearingg people is too fast or too noisy to follow")
    lost = q.x8(*aircaps, "follow and join a face-to-face conversation", "the talk is too fast or too noisy for them")
    assert any("'conversation'" in f and "'follow'" in f for f in lost)
    assert q.x8(*aircaps, "follow and join a face-to-face conversation",
                "a conversation with hearing people is too fast or too noisy to follow") == []
    # Lullaby's own *during* -> *in*: a preposition the clause swaps is no word lost
    assert q.x8(None, "the baby cries during the night", None, "the baby cries in the night") == []


# --------------------------------------------------------------------------------- FR-2: the scripted writer's rows

#: The back-test entries whose Commitment step costs the person money, data or a signature (`StepCost`), alone on the
#: corpus list -- each drafted and saved with Keel's free smaller step.
#: Spec 137 FR-2 (keel-cloud 213 FR-8, `StepCost.moved`): Palus' *move a small part of the reserve* is moved money --
#: a priced step, so it owes Keel's free smaller step (L34).
PRICED = {"08-fresco": "paid", "09-karsa": "buy", "10-palus": "move", "11-issen": "pay", "13-aircaps": "order",
          "15-voltair": "pay", "21-codyco": "€", "23-taiga": "access", "25-bidflow": "paying", "30-realroots": "buy",
          "32-frizzle": "pay", "34-wideframe": "pay"}


def test_every_scripted_commitment_draft_passes_l34_and_l7(entries):
    """FR-2 (keel-cloud 211 FR-6): every scripted Commitment draft -- seed-time and redraft -- holds `L34`; Keel's free
    smaller step is added exactly where the step costs something and the list is the step alone, with its `reason`
    (`L7`), and kept (since 211 `L19` drops Keel's only where the step costs nothing); the golden lists are untouched."""
    priced = {}
    for entry in entries:
        if not entry.founder_list(COMMITMENT) or entry.unsure(COMMITMENT):
            continue
        for draft in (vs.drafted_list(entry, COMMITMENT), vs.first_draft(entry, COMMITMENT)):
            labels = [i["label"] for i in draft["items"]]
            assert step_cost_mod.l34(labels) is None, (entry.id, labels)
            assert not [f for f in score_mod.list_faults({"key": COMMITMENT, "list": draft}, _dimension(COMMITMENT))
                        if f.startswith("L34")], entry.id
        keels = vs.keels_smaller_step(entry)
        if keels:
            draft = vs.drafted_list(entry, COMMITMENT)
            assert draft["items"][1] == keels and keels["label"] == vs.KEELS_SMALLER_STEP
            assert keels["reason"].strip() and step_cost_mod.of(keels["label"]) is None
            assert len(keels["reason"]) <= 200
            priced[entry.id] = step_cost_mod.of(draft["items"][0]["label"]).word
    assert {k: v[:1] if v.startswith("€") else v for k, v in priced.items()} == PRICED
    assert not [e.id for e in entries if not e.backtest and vs.keels_smaller_step(e)], "no golden step is priced"


def test_the_founder_saves_and_strangers_are_served_keels_free_step(entries):
    """FR-2: the founder saves both rows (`saved_list`, the cloud's positional codes `step`, `smaller_step`), and the
    soft yes is served on Keel's step (`smaller_step`): *Probably, after a look at how it works first*."""
    from instructions import spoken as spoken_mod                      # noqa: PLC0415
    by_id = {e.id: e for e in entries}
    codyco = by_id["21-codyco"]
    saved = vs.saved_list(codyco, COMMITMENT)
    assert saved["items"] == [{"code": "step", "label": "pay €3,000 for a money-back pilot at one hotel"},
                              {"code": "smaller_step", "label": vs.KEELS_SMALLER_STEP}]
    assert vs.smaller_step(codyco) == vs.KEELS_SMALLER_STEP
    assert spoken_mod.second_yes(vs.smaller_step(codyco)) == "Probably, after a look at how it works first"
    # a step that costs nothing keeps its list as typed: no smaller step, *Probably yes*
    countly = by_id["01-countly"]
    assert vs.keels_smaller_step(countly) is None and vs.smaller_step(countly) is None
    assert [i["code"] for i in vs.saved_list(countly, COMMITMENT)["items"]] == ["step"]
    # a golden list with the founder's own smaller step is the corpus's, coded as the cloud codes it
    compliancelog = by_id["02-compliancelog"]
    assert vs.keels_smaller_step(compliancelog) is None
    assert [i["code"] for i in vs.saved_list(compliancelog, COMMITMENT)["items"]] == ["step", "smaller_step"]
    assert vs.wire_code(COMMITMENT, 0) == "step" and vs.wire_code(COMMITMENT, 1) == "smaller_step"
    assert '"step" : "smaller_step"' in _cloud(VECTORS + "SavedList.java").replace("index == 0 ? ", "") \
        or 'ONE_STEP -> index == 0 ? "step" : "smaller_step";' in _cloud(VECTORS + "SavedList.java")


def test_every_scripted_buyer_and_payer_row_is_a_role_the_answer_typed(entries):
    """FR-2 (keel-cloud 211 FR-2, `L33`): every row of every scripted Buyer and payer redraft is a role the walker's
    Answer types (`answer_text`) -- none from the founder's material, another answer or the trade -- read with no named
    people at all, so the row is the Answer's own."""
    checked = 0
    for entry in entries:
        if not entry.founder_list(BP) or entry.unsure(BP):
            continue
        draft = vs.drafted_list(entry, BP)
        answer = vs.answer_text(entry, BP)
        assert score_mod.untyped_role(draft["items"], answer, ()) is None, (entry.id, answer, draft["items"])
        assert not [f for f in score_mod.list_faults({"key": BP, "list": draft}, _dimension(BP), answers={BP: answer})
                    if f.startswith("L33")], entry.id
        checked += bool(draft["items"])
    assert checked >= 20


def test_the_scripted_context_result_keeps_every_founder_word(entries):
    """FR-2 (keel-cloud 211 FR-5, `X8`): the scripted CONTEXT_INTERPRET result's job and circumstance keep every founder
    word of WHAT and WHEN as the walker types them (`build_context_interpret`'s `what` / `when`)."""
    from instructions import context as context_mod                    # noqa: PLC0415
    for entry in entries:
        typed = context_mod.build_context_interpret(entry)["context_fields"]
        result = vs.context_result(entry)
        assert q.x8(typed["what"], typed["when"], result["job"], result["circumstance"]) == [], entry.id


# ------------------------------------------------------------------------------------------------- FR-3: the pins

def test_the_commitment_answer_question_is_the_clouds():
    prompts = _joined(_cloud(VECTORS + "AnswerPrompts.java"))
    assert vs_screens.COMMITMENT_ANSWER_QUESTION == ("What's the first real step you'd want them to take, and what "
                                                     "would it cost them?")
    assert f'COMMERCIAL_COMMITMENT -> "{vs_screens.COMMITMENT_ANSWER_QUESTION}"' in prompts
    assert f'-> "{vs_screens.COMMITMENT_ANSWER_QUESTION_205}"' not in prompts


def test_the_untimed_purchase_friction_belief_is_the_clouds():
    """keel-cloud 211 FR-1 (`codycosBeliefWaitsForTheFoundersTime`): the Check screen's save (no pick, no time) owes the
    time and reads the untimed form; *not sure* (a pick, no time) the undated; a typed time the template."""
    java = _joined(_cloud(VECTORS + "PurchaseFriction.java"))
    assert f'UNTIMED_BELIEF =\n            "{friction_mod.UNTIMED_BELIEF}";' in java \
        or f'"{friction_mod.UNTIMED_BELIEF}"' in java
    assert "return list != null && list.pickedIndex() == null && !dated(list);" in java
    step = "A data protection review of guest calls"
    checked = {"items": [{"label": step}], "pickedIndex": None}
    assert friction_mod.time_owed(checked)
    assert friction_mod.belief("hotel group revenue directors", step, None, owed=True) == (
        "Most hotel group revenue directors would get through a data protection review of guest calls within the time "
        "you'll set, or not need it.")
    unsure = {**checked, "pickedIndex": 0}
    assert not friction_mod.time_owed(unsure)
    assert friction_mod.belief("hotel group revenue directors", step, None) == (
        "Most hotel group revenue directors would get through a data protection review of guest calls, or not need it.")
    assert friction_mod.belief("hotel group revenue directors", step, friction_mod.Duration(4, "WEEKS"), owed=True) == (
        "Most hotel group revenue directors would get through a data protection review of guest calls within about 4 "
        "weeks, or not need it.")
    assert not re.search(r"\d", friction_mod.UNTIMED_BELIEF)


def test_prevalence_names_the_whole_segment():
    """keel-cloud 211 FR-3 (`prevalenceNamesTheWholeSegment`, and the re-pinned Lullaby question)."""
    java = _cloud(VECTORS + "WindowFrame.java")
    assert 'return people.contains(", ") ? people + "," : people;' in java
    five = vs.Window(5, "WORKING_DAYS")
    fresco = vs.prevalence_people("construction superintendents at US general contractors",
                                  "have jobs that run on Procore or ACC", "construction superintendents")
    assert vs.founder_prevalence_question(five, fresco, "typed up the daily log after their site walks") == (
        "In the last 5 working days, how many out of 10 construction superintendents at US general contractors, who "
        "have jobs that run on Procore or ACC, typed up the daily log after their site walks?")
    seven = vs.Window(7, "DAYS")
    aircaps = vs.prevalence_people("deaf and hard-of-hearing adults in the US", "talk with hearing people every week",
                                   "deaf and hard-of-hearing adults")
    assert vs.founder_prevalence_question(seven, aircaps, "lost track of a conversation with hearing people") == (
        "In the last 7 days, how many out of 10 deaf and hard-of-hearing adults in the US, who talk with hearing "
        "people every week, lost track of a conversation with hearing people?")
    codyco = vs.prevalence_people("reservation agents at hotel groups in Germany that run a central reservations "
                                  "office or call center", "work at a hotel group in Germany that runs a central "
                                  "reservations office or call center", "reservation agents")
    assert vs.founder_prevalence_question(seven, codyco, "had a booking call ring out unanswered") == (
        "In the last 7 days, how many out of 10 reservation agents at hotel groups in Germany that run a central "
        "reservations office or call center had a booking call ring out unanswered?")
    lullaby = vs.founder_prevalence_question(vs.Window(7, "NIGHTS"), vs.prevalence_people(
        "parents of babies under six months in the US", None, "parents"), "had to work out why their baby was crying")
    assert lullaby == ("In the last 7 nights, how many out of 10 parents of babies under six months in the US had to "
                       "work out why their baby was crying?")
    assert lullaby.replace("In the last 7 nights, how many out of 10 parents of ", "") in _joined(
        _cloud(TESTS + "application/ScreenResultApplierVectorsTest.java"))
    assert vs.prevalence_people(None, None, "parents") == "parents"


def test_the_who_answers_label_is_the_whole_role():
    """keel-cloud 211 FR-8 (`theDecidersOptionIsTheWholeRole`, `CycleTenServedLinesTest`): never the last word."""
    java = _joined(_cloud(VECTORS + "PersonaModel.java"))
    assert 'whole + ", with " + BeliefSentence.joined(others) + " agreeing"' in java
    assert vs.who_answers("Hotel group revenue director", "director") == "Hotel group revenue director"
    assert vs.who_answers("Hotel group revenue director", "director", ["The hotel's owner"]) == (
        "Hotel group revenue director, with the hotel's owner agreeing")
    assert vs.who_answers("Hotel group revenue director", "director", ["The hotel's owner", "The finance director"]) \
        == "Hotel group revenue director, with the hotel's owner and the finance director agreeing"
    assert vs.who_answers(None, "nursery manager") == "Nursery manager"
    assert vs.who_answers("Hotel group revenue director", "director") != "Director"
    served = _cloud(TESTS + "protocol/founder/CycleTenServedLinesTest.java")
    assert '.isEqualTo("Hotel group revenue director, with the hotel\'s owner agreeing")' in served


def test_relative_advantage_serves_every_benefit_kept():
    """keel-cloud 211 FR-4 (`CycleTenServedLinesTest.theWholeBeliefBesideTheList`): the *Keel will test* line's
    `{value}` -- every benefit still kept, joined with *and*, the saved list's over the draft's."""
    assert "static String everyBenefitServed(" in _cloud(FOUNDER + "VectorsController.java")
    draft = ["Hours back at the end of the day", "Action items to the crew the same day"]
    assert corpus_mod.every_benefit_served(None, draft) == (
        "hours back at the end of the day and action items to the crew the same day")
    assert corpus_mod.every_benefit_served(["Missed booking calls turned into bookings"], draft) == (
        "missed booking calls turned into bookings")
    assert corpus_mod.every_benefit_served(None, None) is None
    assert corpus_mod.every_benefit(["A.", "B", "C"]) == "a, b and c"


def test_the_typist_fixture_counts_four():
    """keel-web 171 FR-1 (done on master 6b7a8bd): the context intro on 1 of 2 says *Four*."""
    fixture = json.loads((REPO / "tests/fixtures/typist/backtest-21-codyco-PROBLEM.json").read_text(encoding="utf-8"))
    intros = re.findall(r'"intro": "([^"]*)"', json.dumps(fixture))
    assert any(i.startswith("Four short answers, a phrase each.") for i in intros)
    assert not any(i.startswith("Five short answers") for i in intros)


# ---------------------------------------------------------------------------- FR-4: the Commitment card's example

def test_the_commitment_cards_good_example_carries_its_free_smaller_step():
    body = cards.card("commercial.commitment")
    five = " ".join(cards.section(body, 5).split())
    good = five.split("**Bad (R7 0)**")[0]
    assert "start a paid pilot on one site" in good and "a look at how it works" in good
    assert "Probably, after a look at how it works first" in good and "Probably yes" not in good
    assert "no smaller step on the list" not in good


def test_nothing_else_in_the_cards_moved_and_the_clouds_copy_is_owed():
    """FR-4: the eval's cards and keel-cloud's vendored copy (`keel/dimension-cards.md`, at `CARDS_SHA256`) carry the
    Commitment card's good example alike. Spec 136 FR-1 (keel-cloud 212): the one-clause lines under Prevalence and
    Frequency are in both. Spec 137 FR-1 (keel-cloud 213 FR-11b): the cloud's copy now carries spec 135's corpus
    writer's law at its head and 212's cap as its code holds it (*at most 9 words, 8 on a working-days window*), so
    the two files are byte for byte one at `e3cdea00...`; and (keel-cloud 214 FR-2) at `0ab29614...`, Relative
    advantage's stranger line the hard case."""
    vendored = KEEL_CLOUD / "src/main/resources/keel/dimension-cards.md"
    if not vendored.is_file():
        pytest.skip(f"no vendored cards at {KEEL_CLOUD}")
    theirs = vendored.read_text(encoding="utf-8")
    ours = cards.CARDS_PATH.read_text(encoding="utf-8")
    review = _cloud(APPLICATION + "RespondentReview.java")
    sha = re.search(r'CARDS_SHA256 = "([0-9a-f]{64})"', review).group(1)
    assert hashlib.sha256(theirs.encode("utf-8")).hexdigest() == sha
    good = re.compile(r"- \*\*Good \(R7 2\)\*\* -- Fresco: step \*start a paid pilot on one site\*.*?last two\.\n", re.S)
    assert len(good.findall(ours)) == 1
    # spec 135 FR-3: the pointer to the corpus writer's constitution at the head (above the first card marker, so
    # never handed to a reader or the review turn); keel-cloud 213 FR-11b vendored it
    law = re.compile(r"\n\*\*The corpus writer's law\*\* \(spec 135 FR-3.*?so they can\.\n", re.S)
    assert len(law.findall(ours)) == 1 and len(law.findall(theirs)) == 1
    assert theirs == ours
    assert hashlib.sha256(ours.encode("utf-8")).hexdigest() == sha
    for key in cards_keys(ours):
        assert cards.card(key, theirs) == cards.card(key, ours), key


def cards_keys(text: str) -> list[str]:
    return re.findall(r"<!-- card:([a-z_.]+):begin -->", text)


def test_no_corpus_revision_moved():
    """keel-cloud 211 moved no corpus revision and no contract: the reader still reads revision 23."""
    assert corpus_mod.REVISION == 23
