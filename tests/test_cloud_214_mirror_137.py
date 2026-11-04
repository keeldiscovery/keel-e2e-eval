"""Spec 137 FR-2 (214's half) -- the harness mirrors keel-cloud 214 (the writers keep the rules the cards state: five
code checks).

`instructions/writers_rules.py` restates `WritersRules` (L37 Importance's own row, X14 the occasion, L38 / L39 the
rungs, L40 Purchase friction's suggested step) with `OccasionStem.whenClause`; `instructions/spoken.py` the hard case
(`ScaleFour.hardCase`) ahead of 198's at-stake anchor; `instructions/wording.money_all` (FR-5's W9 that never reads the
founder's own money); `instructions/score.writers_faults` faults a draft that breaks each (and L15 on a Commitment step
that drops a typed number). The cases are `TheWritersKeepTheCardsRulesTest`'s, word for word. The scripted drafts carry
the corpus's own words: those that break a rule are pinned as findings for the next corpus revision (214's *Owed*),
never a failure; Keel's own additions (the free smaller step) obey every rule.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from evals import backtest as bt
from harness import vectors_script as vs
from instructions import score as score_mod
from instructions import spoken as spoken_mod
from instructions import wording as wording_mod
from instructions import writers_rules as w
from stack.config import load_config

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
VECTORS = "src/main/java/com/keeldiscovery/cloud/domain/vectors/"

PALUS_JOB = "keep the money from a raise safe and earning until the company spends it"
PALUS_CIRCUMSTANCE = "the company decides where cash from a raise sits until it is needed"
EXPANSE_JOB = "get each job to run to the end without wasting the cluster"
EXPANSE_CIRCUMSTANCE = "a job is ready to submit and its memory, GPUs and run time have to be guessed first"
CODYCO_JOB = "turn every guest who calls into a booking"
CODYCO_CIRCUMSTANCE = ("booking calls come in on every shift, after hours, at peak and on holidays, and not every one "
                       "gets answered")
AIRCAPS_CIRCUMSTANCE = "a conversation with hearing people is too fast or too noisy to follow"
FRESCO_CIRCUMSTANCE = "the day's site walks are done and the photos and notes still have to go into the daily log"


def _cloud(path: str) -> str:
    target = KEEL_CLOUD / path
    if not target.is_file():
        pytest.skip(f"no {path} at {KEEL_CLOUD}")
    return target.read_text(encoding="utf-8")


def _set_of(source: str, name: str) -> set[str]:
    body = re.search(rf"{name} = (?:java\.util\.)?Set\.of\((.*?)\);", source, re.S).group(1)
    return set(re.findall(r'"([^"]+)"', body))


# ------------------------------------------------------------------------------------------- the vocabularies

def test_the_word_lists_are_the_clouds():
    rules = _cloud(VECTORS + "WritersRules.java")
    assert _set_of(rules, "SMALL") == w.SMALL
    assert _set_of(rules, "DECISIONS") == w.DECISIONS and _set_of(rules, "CALLS") == w.CALLS
    assert _set_of(rules, "TIMES") == w.TIMES and _set_of(rules, "PLURAL_VERBS") == w.PLURAL_VERBS
    assert _set_of(rules, "STATE_VERBS") == w.STATE_VERBS and _set_of(rules, "SUBJECTS") == w.SUBJECTS
    assert "(contracts?|terms|agreements?|\"\n            + \"purchase orders?|order forms?|invoices?)" in rules
    assert "(products?|product's)" in rules
    scale = _cloud(VECTORS + "ScaleFour.java")
    assert "static String hardCase(String occasion, String stem)" in scale


# ------------------------------------------------------------------------------------------- FR-1 L37

def test_the_own_row_is_never_the_job():
    assert w.own_row_fault("Keeping raise cash safe and earning", PALUS_JOB, PALUS_CIRCUMSTANCE, "finance lead",
                           "finance leads") is None
    assert w.own_row_fault("Guessing memory, GPUs and run time", EXPANSE_JOB, EXPANSE_CIRCUMSTANCE, "researcher",
                           "researchers").startswith("L37: the own row 'Guessing memory, GPUs and run time' is the job "
                                                     "or the circumstance said again")
    assert w.own_row_fault("Turning every caller into a booking", CODYCO_JOB, CODYCO_CIRCUMSTANCE, "reservation agent",
                           "reservation agents")
    assert w.own_row_fault("Logging the day's photos and notes", "keep an accurate record of the day's work on site",
                           FRESCO_CIRCUMSTANCE, "construction superintendent", "construction superintendents")
    assert w.own_row_fault("Following a fast, noisy conversation", "follow and join a face-to-face conversation",
                           AIRCAPS_CIRCUMSTANCE, "deaf or hard-of-hearing adult", "deaf or hard-of-hearing adults")
    assert w.own_row_fault("Booking calls that ring out unanswered", CODYCO_JOB, CODYCO_CIRCUMSTANCE,
                           "reservation agent", "reservation agents") is None
    assert w.own_row_fault("Sizing a job before you know its needs", EXPANSE_JOB, EXPANSE_CIRCUMSTANCE, "researcher",
                           "researchers") is None
    assert w.root("caller") == w.root("calls") and w.root("guessed") == w.root("guessing")
    assert w.root("logging") == w.root("log") and w.root("Keeping") == w.root("keep")


# ------------------------------------------------------------------------------------------- FR-2 X14

def test_the_occasion_is_the_hard_case():
    stem = "over the last 3 months, when your company decided where cash from a raise would sit"
    assert w.occasion_fault("cash decision", stem, PALUS_CIRCUMSTANCE, False).startswith(
        "X14: occasion 'cash decision' is a decision")
    assert w.occasion_fault("call", "the last time a booking call rang out unanswered", CODYCO_CIRCUMSTANCE,
                            False).startswith("X14: occasion 'call' alone reads as a judgement call")
    assert w.occasion_fault("booking call", "the last time a booking call rang out unanswered", CODYCO_CIRCUMSTANCE,
                            False) is None
    assert w.occasion_fault("time", "the last time a conversation with hearing people was too fast to follow",
                            AIRCAPS_CIRCUMSTANCE, False).startswith(
        "X14: occasion 'time' alone, where the circumstance names a moment ('conversation')")
    assert "('site walks')" in w.occasion_fault("time", "the last time the day's site walks were done",
                                                FRESCO_CIRCUMSTANCE, False)
    assert w.occasion_fault("time", "the last time your baby cried in the night", "the baby cries during the night",
                            False) is None
    assert w.occasion_fault("time", stem, PALUS_CIRCUMSTANCE, False) is None
    assert w.occasion_fault("conversation", "the last time you went out with friends", AIRCAPS_CIRCUMSTANCE,
                            False).startswith("X14: the stem 'the last time you went out with friends' names no word "
                                              "of the circumstance")
    assert w.occasion_fault("cash decision", stem, PALUS_CIRCUMSTANCE, True) is None


def test_relative_advantage_asks_the_hard_case():
    codyco = spoken_mod.advantage_stem("booking call", "Codyco",
                                       "an AI reservation agent that answers the calls nobody picks up", CODYCO_JOB,
                                       "the last time a booking call rang out unanswered")
    assert codyco.startswith("Think of the most recent time a booking call rang out unanswered. Would Codyco, ")
    assert codyco.endswith(spoken_mod.DONE_BETTER)
    assert spoken_mod.advantage_stem(
        "conversation", "AirCaps", "captioning glasses", "follow and join a face-to-face conversation",
        "the last time a conversation with hearing people was too fast or too noisy to follow") == (
        "Think of the most recent time a conversation with hearing people was too fast or too noisy to follow. Would "
        "AirCaps, captioning glasses, have done that better for you, or not?")
    assert spoken_mod.advantage_stem("time", "Palus", "a treasury account", PALUS_JOB,
                                     "over the last 3 months, when your company decided where cash from a raise would "
                                     "sit").startswith("Think of the most recent time your company decided where cash "
                                                       "from a raise would sit. Would Palus, a treasury account,")
    assert spoken_mod.advantage_stem("daily log", "Fresco", "a voice log for site walks",
                                     "keep an accurate record of the day's work on site",
                                     "the last time the day's site walks were done").startswith(
        "Think of the last daily log when the day's site walks were done. Would Fresco")
    # no stem: 198's at-stake anchor, as before
    assert spoken_mod.advantage_stem("night", "Lullaby", "a phone app that listens to crying",
                                     "work out what the baby needs and settle the baby").startswith(
        "Think of the last night when you had to work out what the baby needs and settle the baby. Would Lullaby")
    assert w.when_clause("over the last 3 months, when your company decided") == "your company decided"
    assert w.when_clause("the last time you tried to get dollars") == "you tried to get dollars"
    assert w.when_clause("Yesterday") is None


# ------------------------------------------------------------------------------------------- FR-3 L38, L39

def test_a_rung_never_joins_two_states():
    assert w.joined_fault("The cash lost value or was out of reach").startswith(
        "L38: 'The cash lost value or was out of reach' joins two outcomes with 'or'")
    for joined in ("I caught parts and nodded along", "I missed most of it and stayed quiet",
                   "Lost the thread and mostly nodded along"):
        assert w.joined_fault(joined), joined
    assert w.joined_fault("Waited and still came up short") is None
    for one in ("It worked after a try or two", "It worked straight away", "It took a lot of guessing",
                "Finished at home or the next morning", "Every booking call was answered",
                "The photos and notes were logged", "The cash stayed safe but earned less than hoped"):
        assert w.joined_fault(one) is None, one
    assert w.same_words("The cash stayed safe and earned", "Earned, and the cash stayed safe")
    assert not w.same_words("Every booking call was answered", "Nearly every booking call was answered")
    rows = ["It worked straight away", "It worked after a try or two", "Booking calls rang out",
            "Booking calls ringing out", "It didn't work at all"]
    assert w.rung_faults(rows, [True] * 5) == [
        "L39: 'Booking calls ringing out' says what 'Booking calls rang out' says, in the same words; each rung is one "
        "distinct outcome on the one scale -- write another, worse or better"]
    assert w.typed_in_answer("The cash lost value or was out of reach",
                             "your way of settling the baby; The cash lost value or was out of reach")


# ------------------------------------------------------------------------------------------- FR-4 L40

def test_the_suggested_step_is_the_buyers_brake():
    assert w.founders_side_fault("A review of the contract terms", ["Fresco"]).startswith(
        "L40: Keel's suggested step 'A review of the contract terms' is a formality of the founder's own paper "
        "('contract')")
    assert "checks the founder's product" in w.founders_side_fault("A check of the product's data handling",
                                                                     ["Fresco"])
    assert "names the idea ('Fresco')" in w.founders_side_fault("A security review of Fresco", ["Fresco"])
    for brake in ("A data protection review of guest calls", "A works council review", "A security review",
                  "Diligence on a new provider", "A vendor risk assessment by IT"):
        assert w.founders_side_fault(brake, ["Fresco"]) is None, brake


# ------------------------------------------------------------------------------------------- FR-5 the step's terms

def test_the_founders_money_is_theirs_and_the_step_keeps_its_numbers():
    assert wording_mod.money_all("pay €3,000 for a pilot, then EUR 1,000 a month in eur") == ["€", "EUR"]
    importance = type("D", (), {"key": "commercial.commitment"})
    items = [{"label": "pay for a money-back pilot at one hotel"}]
    faults = score_mod.writers_faults(importance.key, items, "pay €3,000 for a money-back pilot at one hotel", None)
    assert faults == ["L15: the founder's step says '3,000' (\"pay €3,000 for a money-back pilot at one hotel\"); the "
                      "step keeps every number the founder typed, as typed"]
    assert score_mod.writers_faults(importance.key, [{"label": "pay €3,000 for a money-back pilot"}],
                                    "pay €3,000 for a money-back pilot at one hotel", None) == []


def test_the_eval_faults_a_draft_that_breaks_each():
    ctx = {"job": EXPANSE_JOB, "circumstance": EXPANSE_CIRCUMSTANCE, "actor": "researcher",
           "actor_plural": "researchers"}
    own = score_mod.writers_faults("problem.importance", [{"label": "Guessing memory, GPUs and run time"}], None, ctx)
    assert own and own[0].startswith("L37: ")
    typed = score_mod.writers_faults("problem.importance", [{"label": "Guessing memory, GPUs and run time"}],
                                     "Guessing memory, GPUs and run time; queue waits", ctx)
    assert typed == [], "a row typed in the Answer is the founder's"
    rungs = score_mod.writers_faults("problem.current_solution_satisfaction",
                                     [{"label": "It worked straight away"},
                                      {"label": "The cash lost value or was out of reach"}], None, None)
    assert rungs[0].startswith("L38: ")
    friction = score_mod.writers_faults("commercial.purchase_friction",
                                        [{"label": "A security review"},
                                         {"label": "A review of the contract terms", "suggested": True}], None, None,
                                        ["Fresco"])
    assert friction[0].startswith("L40: ")


def test_the_lock_notes_read_214s_rules_by_name():
    rows = [{"screen": "CALIBRATION_QUESTIONS", "detail": "breach x: L37: the own row 'a' is the job"},
            {"screen": "CONTEXT_INTERPRET", "detail": "breach result.occasion: X14: occasion 'cash decision' is a"}]
    assert [(n["rule"], n["screen"]) for n in bt.lock_notes(None, rows)] == [("L37", "CALIBRATION_QUESTIONS"),
                                                                             ("X14", "CONTEXT_INTERPRET")]


# ------------------------------------------------------------------------------------------- the scripted drafts

#: The corpus's own words that break a 214 rule, as the scripted writer drafts them (214's *Owed*: a corpus revision
#: rewords them) -- findings, never failures; the rule named.
FINDINGS = {"05-paidly": ["L37"], "07-mulchrun": ["L37"], "08-fresco": ["L37"], "09-karsa": ["L37"],
            "10-palus": ["X14"], "17-expanse": ["L38"], "22-andy-ai": ["L37"], "23-taiga": ["L38"],
            "25-bidflow": ["L37"], "27-blacksmith": ["L38"], "28-relvy-ai": ["L38"], "32-frizzle": ["L38"],
            "33-cardboard": ["L37"]}


@pytest.fixture(scope="module")
def entries() -> list:
    from instructions import corpus as c                               # noqa: PLC0415
    if not c.corpus_dir(KEEL_CLOUD).is_dir() or not c.backtest_dir(KEEL_CLOUD).is_dir():
        pytest.skip(f"no corpus at {KEEL_CLOUD}")
    return [*vs.load(KEEL_CLOUD).entries, *vs.load(KEEL_CLOUD, backtest=True).entries]


def _answer(entry, key: str, vector: str):
    return next((a.text for a in vs.calibration_answers(entry, vector) if a.dimension == key), None)


def test_the_scripted_drafts_break_214s_rules_only_in_the_corpus_words(entries):
    found = {}
    for entry in entries:
        ctx = vs._ctx(entry)
        rules = []
        if w.occasion_fault(vs.occasion(entry), None, ctx.get("circumstance"), False):
            rules.append("X14")
        for key, vector in (("problem.importance", "PROBLEM"), ("problem.current_solution_satisfaction", "PROBLEM"),
                            ("commercial.purchase_friction", "COMMERCIAL"), ("commercial.commitment", "COMMERCIAL")):
            if not entry.founder_list(key) or entry.unsure(key):
                continue
            items = vs.drafted_list(entry, key)["items"]
            names = [n for n in (getattr(entry, "idea_name", None),) if n]
            rules += [f.split(":")[0] for f in score_mod.writers_faults(key, items, _answer(entry, key, vector), ctx,
                                                                        names)]
        keels = vs.keels_smaller_step(entry)
        if keels:
            assert not score_mod.writers_faults("commercial.commitment", [keels], None, ctx), entry.id
        if rules:
            found[entry.id] = rules
    assert found == FINDINGS
