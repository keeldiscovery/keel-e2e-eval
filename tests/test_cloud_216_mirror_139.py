"""Spec 139 FR-1 / FR-2: the harness mirrors keel-cloud 216 (the writer names the hurt; keel-cloud-docs `40ae6754`,
its tasks.md *Owed: keel-e2e-eval*). No stack, no model, no paid call; the cloud's sources are read from the checkout
`stack.toml` names, skipped without it.

- FR-1 the cards at 216's digest (`2f1a63cc...`), byte for byte the cloud's vendored copy.
- FR-2 the Frequency frame *On how many of {window} did you {event}?* (the founder's *... did a typical {actor} ...?*),
  the cap 9 / 8 unchanged and measured on 174's frame; `E9` (the no-sayer), `L37b` (the own row is the hurt, on
  `went_wrong`'s verb) and `K12` (the condition is the assurance) mirrored on the cloud's own cases
  (`TheWriterNamesTheHurtTest`) and read by name in the lock notes; the cost belief's subject the paying unit
  (`CommercialChain.payingUnit`); the scripted writer's Prevalence carries `no_sayer`, its conditions pass K12.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from evals import backtest as bt
from harness import vectors_script as vs
from instructions import chain as chain_mod
from instructions import corpus as corpus_mod
from instructions import wording as wording_mod
from instructions import writers_rules as writers_mod
from instructions.registry import RecallWindow
from quality import cards
from stack.config import load_config

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
VECTORS = "src/main/java/com/keeldiscovery/cloud/domain/vectors/"
APPLICATION = "src/main/java/com/keeldiscovery/cloud/application/"
INSTRUCTIONS = "src/main/resources/keel/inference-instructions/"
CARDS_SHA256_216 = "2f1a63ccc481175ff45a540a199c0930c77f4640a64ea0c798f5c2a3c0fdd2c4"
THREE_MONTHS = RecallWindow(3, "MONTHS")
FIVE_WORKING_DAYS = RecallWindow(5, "WORKING_DAYS")
#: keel-cloud `VectorFixtures` (Lullaby, 216).
ROUTINE = "settle the baby"
WENT_WRONG = "did not know why the baby cried"
NO_SAYER = "a parent who knew at once what the cry meant"


def _cloud(rel: str) -> str:
    path = KEEL_CLOUD / rel
    if not path.is_file():
        pytest.skip(f"no {rel} at {KEEL_CLOUD}")
    return path.read_text(encoding="utf-8")


# ------------------------------------------------------------------------------------------------ FR-1 the cards

def test_the_cards_are_the_vendored_copy_at_216s_digest():
    """Spec 139 FR-1, re-pinned by spec 141 FR-1: the cards at 216's digest, or at the cycle 14 round's after it (216's
    lines below stand in both)."""
    from tests.test_cloud_219_228_mirror_141 import CARDS_SHA256_141   # noqa: PLC0415
    ours = cards.CARDS_PATH.read_bytes()
    review = _cloud(APPLICATION + "RespondentReview.java")
    sha = re.search(r'CARDS_SHA256 = "([0-9a-f]{64})"', review).group(1)
    assert sha in (CARDS_SHA256_216, CARDS_SHA256_141)
    assert hashlib.sha256(ours).hexdigest() == sha
    assert (KEEL_CLOUD / "src/main/resources/keel/dimension-cards.md").read_bytes() == ours
    text = " ".join(ours.decode("utf-8").split())
    assert "*On how many of {window} did you {event}?*" in text and "*On how many of {window} did a typical" in text
    assert "`E9`" in text and "`L37b`" in text and "`K12`" in text
    assert "*In {window}, on how many {unit} did you {event}?*" not in text


# ------------------------------------------------------------------------------------ FR-2 the Frequency frame

@pytest.mark.parametrize("window, cap", [(RecallWindow(7, "NIGHTS"), 9), (RecallWindow(7, "DAYS"), 9),
                                         (RecallWindow(4, "WEEKS"), 9), (THREE_MONTHS, 9), (FIVE_WORKING_DAYS, 8)])
def test_the_frame_says_the_unit_once_and_the_cap_is_212s(window, cap):
    """216 FR-3 (`TheWriterNamesTheHurtTest`, `WindowFrame.windowFirst`, `eventMaxWords`): served *On how many of
    {window} did you ...?*, a word shorter than 174's; the cap measured on 174's frame, so a clause at it is 19 served."""
    at_cap = " ".join(["act"] * cap)
    assert wording_mod.event_max_words(window) == cap
    assert wording_mod.frequency_respondent(window, "lose your keys") == \
        f"On how many of {window.words()} did you lose your keys?"
    assert len(wording_mod.frequency_respondent(window, at_cap).split()) == 19
    assert len(wording_mod.frequency_respondent_before216(window, at_cap).split()) == 20
    vs_window = vs.Window(window.count, window.unit)
    assert vs.frequency_served(vs_window, "lose your keys") == wording_mod.frequency_respondent(window, "lose your keys")
    assert vs.frequency_served(vs_window, None) == f"On how many of {window.words()} did that happen?"
    assert vs.frequency_served_before216(vs_window, "lose your keys") == \
        wording_mod.frequency_respondent_before216(window, "lose your keys")


def test_a_stored_item_in_174s_opening_reads_as_stored():
    """216 FR-3 (`theStoredOpeningIsRead`)."""
    stored = wording_mod.frequency_respondent_before216(THREE_MONTHS, "move raise cash into the bank's fund")
    assert stored == "In the last 3 months, in how many months did you move raise cash into the bank's fund?"
    assert wording_mod.frequency_respondent_before216(FIVE_WORKING_DAYS, "type up the log") == \
        "In the last 5 working days, on how many days did you type up the log?"
    held = vs.frequency_held_before216(vs.Window(5, "WORKING_DAYS"),
                                       "type up the daily log in the trailer after the site walks were done")
    assert len(held.split()) <= vs.STEM_MAX_WORDS
    assert wording_mod.frequency_respondent(FIVE_WORKING_DAYS, "type up the daily log after the walk").count(" ") + 1 \
        == 19


def test_the_frames_are_window_frames():
    text = _cloud(VECTORS + "WindowFrame.java")
    assert 'return "On how many of " + RecallWindow.orDefault(window).words() + " ";' in text
    assert 'return "In " + w.words() + ", " + countedIn(w) + " how many " + shortUnit(w) + " ";' in text
    assert "windowFirstBefore216(window) + \"did you\"" in text, "the cap measured on 174's frame"
    rules = _cloud(APPLICATION + "RespondentQuestionsRules.java")
    assert "WindowFrame.frequencyRespondentBefore216(window," in rules, "E4 measures 174's frame"


# ------------------------------------------------------------------------------------------------ FR-2 E9

@pytest.mark.parametrize("no_sayer, routine, went_wrong, circumstance, people, starts", [
    # 216's cycle-13 shapes (`e9RefusesTheShapes`)
    ("a super who wrote the log on site", "write up the daily log", "typed up the day's photos and notes into the log",
     "the day's site walks are done", ("superintendent", "construction superintendents"),
     "E9: no_sayer 'a super who wrote the log on site' differs from the rest by the routine"),
    ("a researcher who submitted with values known to fit", "submit a job to the cluster",
     "set its memory, GPUs and run time", "a job is ready to submit", ("researcher", "researchers and ML engineers"),
     "E9:"),
    ("an agent who answered every call that shift", "answer booking calls on a shift",
     "took a booking call on their shift", "a booking call comes in", ("reservation agent", "reservation agents"),
     "E9:"),
    ("a researcher who never uses the shared cluster", "submit a job to the cluster",
     "had a job killed for running out of memory", "a job is ready to submit to the shared cluster",
     ("researcher", "researchers"), "E9: no_sayer 'a researcher who never uses the shared cluster' says 'never' before"),
    ("someone who is not a super", "write the daily log", "typed up the daily log in the trailer after the walk",
     "the day's site walks are done", ("super", "supers"), "E9:"),
    ("a super whose job doesn't keep a daily log", "write the daily log",
     "typed up the daily log in the trailer after the walk", "the daily log is due after the walk", ("super", "supers"),
     "E9:"),
    (" ", "write the daily log", "typed it up", None, (), "E9: write no_sayer beside event"),
])
def test_e9_refuses_the_shapes(no_sayer, routine, went_wrong, circumstance, people, starts):
    fault = wording_mod.no_sayer_fault(no_sayer, routine, went_wrong, circumstance, *people)
    assert fault and fault.startswith(starts), fault
    assert "the thing that failed, was lost, came back wrong, sat idle or had to be done twice" in fault


@pytest.mark.parametrize("no_sayer, routine, went_wrong, circumstance, people", [
    ("a super whose log was done on site before the walk ended", "write the daily log",
     "typed up the daily log in the trailer after the walk", "the day's site walks are done",
     ("superintendent", "construction superintendents")),
    ("a researcher whose job ran within what it asked for", "submit a job to the cluster",
     "had a job killed for running out of memory", "a job is ready to submit", ("researcher", "researchers and ML engineers")),
    ("an agent whose shift had every booking call picked up", "answer booking calls on a shift",
     "had a booking call ring out unanswered", "a booking call comes in", ("reservation agent", "reservation agents")),
    (NO_SAYER, ROUTINE, WENT_WRONG, "the baby cries in the night", ("parent", "parents of babies under six months")),
])
def test_e9_passes_the_good_examples(no_sayer, routine, went_wrong, circumstance, people):
    assert wording_mod.no_sayer_fault(no_sayer, routine, went_wrong, circumstance, *people) is None


def test_e9s_words_are_the_clouds():
    text = re.sub(r'"\s*\+\s*"', "", _cloud(VECTORS + "WindowFrame.java"))
    assert f'NO_SAYER_TEST = "{wording_mod.NO_SAYER_TEST}"' in text
    roots = re.sub(r'"\s*\+\s*"', "", _cloud(VECTORS + "WritersRules.java"))
    found = re.search(r"ING_NOUNS = Set\.of\(([^)]*)\)", roots).group(1)
    assert set(re.findall(r'"([^"]+)"', found)) == set(writers_mod.ING_NOUNS)


# ------------------------------------------------------------------------------------------------ FR-2 L37b

@pytest.mark.parametrize("row, routine, went_wrong, fault", [
    ("Guessing memory, GPUs and run time", "submit a job to the cluster", "had a job killed for running out of memory",
     "L37b: the own row 'Guessing memory, GPUs and run time' is not the hurt Prevalence tests"),
    ("Choosing where the raise cash sits", "keep raise cash in the bank",
     "moved raise cash into the bank's default treasury product", "L37b:"),
    ("Following and joining the conversation", "talk with hearing people at work",
     "lost the thread of a fast group conversation", "L37b:"),
    ("Writing up the daily log", "write the daily log", "typed up the daily log in the trailer after the walk",
     "its verb is the routine's"),
    ("Typing up the log after the walk", "write the daily log", "typed up the daily log in the trailer after the walk",
     None),
    ("Having a job killed for memory", "submit a job to the cluster", "had a job killed for running out of memory", None),
    ("Knowing what the cry means", ROUTINE, WENT_WRONG, None),
    ("Guessing memory, GPUs and run time", None, None, None),
])
def test_l37b_the_own_row_is_the_hurt(row, routine, went_wrong, fault):
    """216 FR-2 (`l37bReadsTheHeadVerb`)."""
    said = writers_mod.own_row_hurt_fault(row, routine, went_wrong)
    if fault is None:
        assert said is None, said
    else:
        assert said and fault in said and "went_wrong said as the difficulty" in said, said


#: Spec 139 FR-2 (plan.md, judgement call 3; 137's call 9): the corpus's recorded own rows the scripted writer drafts,
#: read against the scripted `went_wrong` -- the golden seven's own (`vs.ACT_THAT_HURTS`), a back-test entry's
#: *had a time when {circumstance}* (revision 25 records no `went_wrong`) -- that break L37b: findings for a corpus
#: revision that records the hurt, never failures. Lullaby's own row passes on 216's `went_wrong`.
L37B_FINDINGS = {"01-countly", "02-compliancelog", "04-linerly", "06-repeatline", "07-mulchrun", "10-palus", "11-issen",
                 "15-voltair", "16-pairio", "17-expanse", "20-lemma", "23-taiga", "24-probo", "30-realroots",
                 "34-wideframe", "35-candle"}


@pytest.fixture(scope="module")
def entries() -> list:
    if not corpus_mod.corpus_dir(KEEL_CLOUD).is_dir() or not corpus_mod.backtest_dir(KEEL_CLOUD).is_dir():
        pytest.skip(f"no corpus at {KEEL_CLOUD}")
    return [*vs.load(KEEL_CLOUD).entries, *vs.load(KEEL_CLOUD, backtest=True).entries]


def test_the_corpus_own_rows_that_break_l37b_are_findings(entries):
    found = set()
    for entry in entries:
        routine, went_wrong = vs.act_that_hurts(entry)
        own = ((entry.founder_list("problem.importance") or {}).get("items") or [{}])[0].get("label")
        if writers_mod.own_row_hurt_fault(own, routine, went_wrong):
            found.add(entry.id)
    assert found == L37B_FINDINGS


# ------------------------------------------------------------------------------------- FR-2 the scripted writer

def test_every_scripted_prevalence_carries_a_no_sayer_that_passes_e9(entries):
    """216's owed list (*the scripted runtime / fakes: Prevalence results carry `no_sayer`*): the golden seven's own
    (`vs.NO_SAYERS`, Lullaby's the cloud's `VectorFixtures.NO_SAYER`), every other entry `vs.NO_SAYER_ANY`."""
    assert vs.NO_SAYERS["03-lullaby"] == NO_SAYER and vs.act_that_hurts(
        next(e for e in entries if e.id == "03-lullaby")) == (ROUTINE, WENT_WRONG)
    for entry in entries:
        q = next(q for q in vs.calibration_result(entry, "PROBLEM")["questions"] if q["key"] == "problem.prevalence")
        assert q["no_sayer"] == vs.NO_SAYERS.get(entry.id, vs.NO_SAYER_ANY), entry.id
        ctx = vs._ctx(entry)
        assert wording_mod.no_sayer_fault(q["no_sayer"], q["routine"], q["went_wrong"], ctx.get("circumstance"),
                                          *(p for p in (ctx.get("actor"), ctx.get("actor_plural")) if p)) is None, \
            entry.id


def test_every_scripted_condition_is_an_assurance(entries):
    """216 FR-5 (K12): no scripted or recorded Adoption friction condition names a danger word un-negated."""
    for entry in entries:
        for item in (entry.founder_list("solution.adoption_friction") or {}).get("items") or []:
            condition = vs.adoption_condition(item)
            assert vs.assurance_fault(condition) is None, (entry.id, condition)


# ------------------------------------------------------------------------------------------------ FR-2 K12

@pytest.mark.parametrize("danger", ["they risk my job failing", "missed calls need your own judgement",
                                    "my calls could go down", "it could break my schedule"])
def test_k12_refuses_the_danger(danger):
    fault = vs.assurance_fault(danger)
    assert fault and fault.startswith("K12:") and "what Keel has to do or promise, not what they fear" in fault


@pytest.mark.parametrize("assurance", ["it hands me the hard calls", "failed jobs fall back to my numbers",
                                       "it didn't wake the baby", "it doesn't break my schedule",
                                       "my staff's pay details stayed private"])
def test_k12_passes_the_assurance(assurance):
    assert vs.assurance_fault(assurance) is None


def test_k12s_words_are_the_clouds():
    text = re.sub(r'"\s*\+\s*"', "", _cloud(APPLICATION + "AskedRules.java"))
    risk = re.search(r'RISK = Pattern\.compile\("([^"]+)"', text).group(1)
    for word in ("risks?", "fails?", "failing", "lose", "breaks?", "wrong", "miss", "crash", "down", "needs? my",
                 "needs? your", "judgement", "judgment"):
        assert word in risk and word in vs.RISK.pattern, word


# ------------------------------------------------------------------------------------- FR-2 the paying unit

def test_the_paying_unit():
    """216 FR-4 (`thePayingUnit`)."""
    fresco = ("construction superintendents at US general contractors", "have jobs that run on Procore or ACC",
              "construction superintendents")
    palus = ("finance leads at venture-backed startups in the US within two years of a raise, banking with Mercury, "
             "Brex or similar", "work at a startup that banks with Mercury, Brex or similar", "finance leads")
    codyco = ("reservation agents at hotel groups in Germany that run a central reservations office or call center",
              None, "reservation agents")
    assert chain_mod.paying_unit(*fresco, True) == "US general contractors"
    assert chain_mod.paying_unit(*palus, True) == "venture-backed startups"
    assert chain_mod.paying_unit(*codyco, True) == "hotel groups"
    assert chain_mod.paying_unit("finance leads", "work at a startup that banks with Mercury", "finance leads",
                                 True) == "startups"
    assert chain_mod.paying_unit("researchers and ML engineers", None, "researchers and ML engineers", True) is None
    assert chain_mod.paying_unit("researchers and ML engineers", None, "researchers and ML engineers", False) == \
        "researchers and ML engineers"
    assert chain_mod.organisation("nurses who work at night") is None


def test_the_cost_belief_names_the_paying_unit():
    """216 FR-4 (`theBeliefNamesThePayingUnit`): money the paying unit's, its *per {unit}* kept; 213's word where none is
    named; a share lost on B2B the paying unit's; the hours path unchanged."""
    money = {"mode": "MONEY", "low": 800, "high": 1000, "period": "month", "currency": "USD", "base": "the daily log",
             "unit": "site"}
    assert chain_mod.cost_belief(money, "site walk", "operations lead", "Contractor operations leads", True,
                                 paying="US general contractors") == \
        "US general contractors already spend about $800 to $1,000 per site a month on the daily log."
    assert chain_mod.cost_belief(money, "site walk", "head of infrastructure", "Heads of infrastructure", True,
                                 paying=None).startswith("Heads of infrastructure already spend about $800 to $1,000")
    share = {"mode": "RATE", "low": 5, "high": 5, "period": "month", "currency": "USD", "measure": "%",
             "base": "the reservation calls"}
    assert chain_mod.cost_belief(share, "x", "revenue director", "Hotel group revenue directors", True,
                                 paying="hotel groups", actor_plural="reservation agents") == \
        "Hotel groups already lose about 5% of the reservation calls a month."
    hours = {"mode": "HOURS", "low": 30, "high": 60, "period": "month", "currency": "USD", "measure": "hours",
             "base": "the daily log", "unit": "site", "rate": 60}
    assert chain_mod.cost_belief(hours, "site walk", "operations lead", "Contractor operations leads", True,
                                 actor="construction superintendent", actor_plural="construction superintendents",
                                 paying="US general contractors") == \
        "Construction superintendents already spend 30 to 60 hours per site a month on the daily log."


def test_a_recorded_sentence_reads_with_the_paying_unit():
    """216 FR-4 (`VectorCorpusFixture.spec216Payer`): the record's decider word gives way where it opens the sentence or
    follows *costs*; no organisation named, the record as it stands."""
    assert corpus_mod.spec216_payer("Hotel group revenue directors already lose about 5% of the calls a month.",
                                    "hotel groups", "hotel group revenue directors") == \
        "Hotel groups already lose about 5% of the calls a month."
    assert corpus_mod.spec216_payer("The problem already costs contractor operations leads {value}.",
                                    "US general contractors", "Contractor operations leads") == \
        "The problem already costs US general contractors {value}."
    assert corpus_mod.spec216_payer("Heads of infrastructure already spend x.", None, "Heads of infrastructure") == \
        "Heads of infrastructure already spend x."


def test_the_paying_unit_is_the_clouds():
    text = re.sub(r'"\s*\+\s*"', "", _cloud(VECTORS + "CommercialChain.java"))
    assert "public static String payingUnit(ContextSlots slots, boolean b2b)" in text
    qualifier = re.search(r"QUALIFIER = java\.util\.Set\.of\(([^;]*)\);", text).group(1)
    assert set(re.findall(r'"([^"]+)"', qualifier)) == set(chain_mod.ORG_QUALIFIER)
    no_org = re.search(r"NO_ORG = java\.util\.Set\.of\(([^;]*)\);", text).group(1)
    assert set(re.findall(r'"([^"]+)"', no_org)) == set(chain_mod.NO_ORG)


# ------------------------------------------------------------------------------------------------ the lock notes

def test_the_lock_notes_read_e9_l37b_and_k12_by_name():
    rows = [{"screen": "CALIBRATION_QUESTIONS", "detail": "breach questions[0].no_sayer: E9: write no_sayer beside "
                                                          "event -- the test"},
            {"screen": "CALIBRATION_QUESTIONS", "founderNote": "L37b: the own row 'Guessing memory' is not the hurt"},
            {"screen": "ASKED", "turns": [{"content": "K12: 'Only if they risk my job' names the danger"}]},
            {"screen": "CALIBRATION_QUESTIONS", "detail": "L37: the own row 'x' is the job said again"}]
    assert [n["rule"] for n in bt.lock_notes(None, rows)] == ["E9", "L37b", "K12", "L37"]
    assert "keel-cloud 216 FR-1" in bt.LOCK_NOTES["E9"] and "keel-cloud 206 FR-1" in bt.LOCK_NOTES["E9"]
    assert "keel-cloud 216 FR-2" in bt.LOCK_NOTES["L37b"] and "keel-cloud 216 FR-5" in bt.LOCK_NOTES["K12"]


# ------------------------------------------------------------------------------------------ the instruction files

def test_the_instructions_say_what_the_mirrors_hold():
    lists = _cloud(INSTRUCTIONS + "founder-lists.md")
    assert "**`no_sayer`**" in lists and '"no_sayer": "a parent who knew at once what the cry meant"' in lists
    assert '"went_wrong": "did not know why the baby cried"' in lists
    asked = _cloud(INSTRUCTIONS + "respondent-questions.md")
    assert "*On how many of {window} did you {event}?*" in asked
    assert "**The problem, never the circumstance**" in asked and "**Every condition the founder gave, kept**" in asked
    assert "**The condition is the assurance**" in _cloud(INSTRUCTIONS + "asked.md")
    assert "*On how many of {window}" in _cloud(INSTRUCTIONS + "respondent-review.md")


# ------------------------------------------------------------------------------- FR-4b the So line (keel-cloud 218)

def _whether(belief: str) -> str:
    """keel-cloud 218 (`BeliefSentence.whetherClause`, its tasks.md *Owed to keel-e2e-eval*): the So line's clause is
    *Whether* + the entry's Compatibility belief lower-cased, its stop dropped (the fourteen's beliefs read *Most ...*)."""
    text = belief.strip().rstrip(".")
    return "Whether " + text[:1].lower() + text[1:]


def test_no_pin_quotes_the_so_line_and_the_rule_reads_the_belief():
    """FR-4b: no eval pin quotes Compatibility's So line (218 grepped; *Whether could ...* was the defect); any that does
    carries the belief's subject -- 218's three examples, read off revision 25's beliefs."""
    if not corpus_mod.backtest_dir(KEEL_CLOUD).is_dir():
        pytest.skip(f"no back-test corpus at {KEEL_CLOUD}")
    entries = {e.id: e for e in vs.load(KEEL_CLOUD, backtest=True).entries}
    said = {e: _whether(entries[e].founder_calibration["solution.compatibility"]["belief_sentence"])
            for e in corpus_mod.GALLERY}
    assert said["08-fresco"] == ("Whether most construction superintendents on commercial jobs could talk into their "
                                 "phone over the noise on site")
    assert said["21-codyco"] == "Whether most reservation agents at hotel groups could forward unanswered calls to " \
                                "another number"
    assert said["13-aircaps"] == "Whether most deaf and hard-of-hearing adults could read captions while watching faces"
    assert all(s.startswith("Whether most ") for s in said.values())
    repo = Path(__file__).resolve().parents[1]
    for folder in ("harness", "evals", "instructions", "tests"):
        for path in (repo / folder).rglob("*.py"):
            if path.resolve() != Path(__file__).resolve():
                assert "Whether could" not in path.read_text(encoding="utf-8"), path
