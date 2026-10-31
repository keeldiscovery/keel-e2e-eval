"""Spec 107 (keel-cloud 175, `FoundersOwnWordsTest`): the harness's J1 and M5 mirrors exempt every word or phrase found
whole, case aside, in the founder's own texts -- the context's typed fields, the problem seed, the solution seed, the
audience words -- exactly as keel-cloud's `Vocabulary.typedIn` / `VectorCorridor.founderTexts()` now do. Stackless."""

from __future__ import annotations

import pytest

from evals import corpus_scenario as cs
from evals import scope_marks as sm
from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from tests.test_after_131 import FRAME, PALUS_HOW, _backtest, _golden_entries, _refusal_body, keels_words


def _paidly():
    [paidly] = [e for e in _golden_entries() if e.id == "05-paidly"]
    return paidly


# ------------------------------------------------------------------------------- the match and the texts

def test_typed_in_is_whole_word_case_aside_and_a_hyphen_joins():
    """`Vocabulary.typedIn` (175 T001): *api* is not typed in *rapid*, *rate* not in *floating-rate*, *floating-rate* not
    in *floating rate*; *PMS* is *pms*; a phrase is matched whole. No stemming: *API* typed is not *APIs*."""
    assert corpus_mod.typed_in("pms", ["writes it into the PMS (OPERA Cloud)"])
    assert corpus_mod.typed_in("mortgage bonds", ["government-backed Mortgage Bonds, held at a custodian"])
    assert corpus_mod.typed_in("floating-rate", ["short-duration, floating-rate bonds"])
    assert not corpus_mod.typed_in("api", ["a rapid answer"])
    assert not corpus_mod.typed_in("rate", ["short-duration, floating-rate bonds"])
    assert not corpus_mod.typed_in("floating-rate", ["a floating rate"])
    assert not corpus_mod.typed_in("apis", ["it reads the API"])
    assert not corpus_mod.typed_in("api", [])
    assert not corpus_mod.typed_in("", ["api"])


def test_the_founders_texts_are_the_typed_fields_the_seeds_and_the_audience_words():
    """`VectorCorridor.founderTexts()`: the four fields keel-web's context form takes, the two seeds as the walk types
    them (whitespace folded), the audience words -- never Keel's interpretations, never the untyped occasion."""
    palus = _backtest("10-palus")
    texts = corpus_mod.founder_texts(palus, ["custodian"])
    founder = vs.founder_inputs(palus)
    assert list(texts) == [*founder.context_fields.values(), founder.problem_seed, founder.solution_seed, "custodian"]
    assert (palus.interpretations or {}).get("problem") not in texts
    assert palus.context["occasion"] not in texts

    class Bare:
        id = "99-none"
    assert corpus_mod.founder_texts(Bare()) == ()


# ------------------------------------------------------------------------------- FR-1: J1

def test_paidly_says_platform_and_so_does_its_own_seed():
    """The named case: 05-paidly's scripted how says *platform*, and so does its solution seed (*A platform that pays
    the translator ...*), so GET idea notes none and the strict J1 check expects none."""
    paidly = _paidly()
    assert vs.jargon(vs.idea_lines(paidly)["how"]) == ["platform"]
    assert vs.founder_inputs(paidly).solution_seed.startswith("A platform that pays the translator")
    assert vs.expected_j1(paidly) == []


def test_j1_still_notes_a_word_keel_brought_in():
    """Where *platform* is Keel's (a Paidly seed without it), the note is owed as before; the founder's audience words
    exempt it the old way."""
    keels = keels_words(_paidly(), "platform")
    assert vs.expected_j1(keels) == ["platform"]
    assert vs.expected_j1(keels, ["Platform"]) == []


def test_no_golden_card_owes_a_j1_note():
    """Every golden card's J1 words are typed in its own seeds, so every strict walk expects no note."""
    assert {e.id: vs.expected_j1(e) for e in _golden_entries()} == {e.id: [] for e in _golden_entries()}


# ------------------------------------------------------------------------------- FR-2: M5

def test_palus_card_in_its_own_words_is_no_m5_fault():
    """`palusCardInItsOwnWordsHasNoM5BreachAndNoJ1Note`, mirrored: *short-duration, floating-rate, government-backed
    mortgage bonds* are the seed's own; without the founder's texts the lists still trip them (175 FR-3)."""
    palus = _backtest("10-palus")
    lines = {"how": PALUS_HOW, "belief": FRAME + "earn more on the cash you will not touch."}
    assert corpus_mod.m5_faults(lines, founder_texts=corpus_mod.founder_texts(palus)) == []
    assert [f["word"] for f in corpus_mod.m5_faults(lines)] == ["short-duration", "floating-rate", "mortgage bonds"]


def test_a_card_that_adds_an_api_is_faulted_on_the_api_alone():
    """`aCardThatIntroducesAnApiIsBreachedAndTheRepairNamesOnlyTheApi`, mirrored: one trade-word fault, on *API*."""
    palus = _backtest("10-palus")
    how = PALUS_HOW + " It reads your bank balance through an API."
    faults = corpus_mod.m5_faults({"how": how}, founder_texts=corpus_mod.founder_texts(palus))
    assert faults == [{"line": "how", "word": "API", "fault": "trade word"}]
    assert corpus_mod.m5_faults({"how": how}, audience_words=["API"],
                                founder_texts=corpus_mod.founder_texts(palus)) == []


def test_the_spoken_form_rules_still_read_the_line_alone():
    """175 T003: names in parentheses and a design-note belief are about how a line is heard, not whose word it is --
    Codyco's seed types *(OPERA Cloud, Sihot, Apaleo)* and the parenthesis is still a fault; its *PMS* is not."""
    codyco = _backtest("21-codyco")
    how = "Codyco writes the confirmed booking into the PMS (OPERA Cloud, Sihot, Apaleo)."
    faults = corpus_mod.m5_faults({"how": how, "belief": FRAME + "need no change to the front desk."},
                                  founder_texts=corpus_mod.founder_texts(codyco))
    assert [f["fault"] for f in faults] == ["names in parentheses", "design note"]


@pytest.mark.parametrize("entry_id, words", [
    ("10-palus", ["short-duration", "floating-rate", "mortgage bonds", "money market"]),
    ("11-issen", ["spaced-repetition", "curriculum"]),
    ("12-transload", ["workflow", "3d box"]),
    ("14-code-four", ["check words"]),
    ("21-codyco", ["pms"]),
    ("16-pairio", []),
])
def test_the_back_test_seeds_type_the_words_the_rows_named(entry_id, words):
    """keel-cloud 175's list of the eval pins to move: the M5 words each entry's own texts type (16-pairio's *CMMS* /
    *ERP* are not in its seed)."""
    typed = corpus_mod.founder_texts(_backtest(entry_id))
    assert [w for w in corpus_mod.M5_WORDS if corpus_mod.typed_in(w, typed)] == words


@pytest.mark.parametrize("entry_id, fires", [
    ("10-palus", ["mortgage-backed bonds"]),
    ("11-issen", []),
    ("12-transload", []),
    ("14-code-four", ["check word"]),
    ("21-codyco", []),
    ("16-pairio", ["connected to SAP, Maximo or SharePoint", "to SAP, Maximo or SharePoint",
                   "SAP, Maximo or SharePoint", "CMMS", "ERP"]),
])
def test_lock_plain_words_rows_fire_only_on_keels_words(entry_id, fires):
    """FR-2: the rows stay; on the entry's own texts a row fires only where no M5 word it carries is typed. Palus's
    *mortgage-backed* and Code Four's singular *check word* are not the seeds' (no stemming); Pairio's list rows carry no
    M5 word (the list of names is a spoken-form rule and stays M5's) and its *CMMS* / *ERP* are Keel's."""
    typed = corpus_mod.founder_texts(_backtest(entry_id))
    assert [p for p, _ in corpus_mod.LOCK_PLAIN_WORDS[entry_id] if corpus_mod._row_fires(p, typed)] == fires


def test_plain_line_leaves_the_founders_words_and_moves_keels():
    """Palus's own card is no edit at all; a refusal on Keel's *API* moves the API and keeps the bond words; Keel's
    *mortgage-backed bonds* takes Palus's own row; Codyco's typed *PMS* stays."""
    palus = _backtest("10-palus")
    assert corpus_mod.plain_line(palus, "how", PALUS_HOW, "short-duration") is None
    after = corpus_mod.plain_line(palus, "how", PALUS_HOW + " It reads your bank balance through an API.", "API")
    assert after == PALUS_HOW + " It reads your bank balance through a connection."
    assert corpus_mod.plain_line(palus, "how", "It holds mortgage-backed bonds for you.", "mortgage-backed") == \
        "It holds government-backed bonds for you."
    codyco = _backtest("21-codyco")
    assert corpus_mod.plain_line(codyco, "how", "Codyco writes the booking into the PMS.", "PMS") is None
    assert corpus_mod.plain_line(codyco, "how", "Codyco writes the booking into the PMS (OPERA Cloud, Sihot, Apaleo).",
                                 "OPERA Cloud") == "Codyco writes the booking into the PMS."


def test_the_lock_is_answered_on_keels_word_alone():
    """`theLockStillRefusesAnApiTheFounderNeverTyped`, walked: Palus's card refused on *API*, the how edited once, the
    founder's bond words kept, the second lock 200."""
    palus = _backtest("10-palus")
    lines = {"how": PALUS_HOW + " It reads your bank balance through an API.", "belief": FRAME + "earn more."}
    edits, answers = [], [{"status": 200, "receipt": {"version": 1}}]

    def edit(e):
        edits.append(e)
        lines.update(e)
        return {"typed": e}
    out = cs.answer_refused_lock(cs.lock_refusal(422, _refusal_body("how", "API")), entry=palus,
                                 read_lines=lambda: dict(lines), edit=edit, relock=lambda: answers.pop(0))
    assert out["status"] == 200 and out["passes"] == 1
    assert edits == [{"how": PALUS_HOW + " It reads your bank balance through a connection."}]
    assert corpus_mod.m5_faults(lines, founder_texts=corpus_mod.founder_texts(palus)) == []


# ------------------------------------------------------------------------------- FR-2: the problem's sentence

def test_the_problem_sentence_keeps_a_word_the_seed_carries():
    """`theProblemSentenceKeepsAWordThePalusProblemSeedCarries`, mirrored on `sentence_faults`: *money market fund*
    is Palus's own; *sweep account* is not, and is still a fault."""
    typed = corpus_mod.founder_texts(_backtest("10-palus"))
    said = "Startups leave idle cash in a money market fund that pays them too little."
    assert sm.sentence_faults(said) == ["M5 word 'money market'"]
    assert sm.sentence_faults(said, typed) == []
    swept = "Startups leave idle cash in a sweep account that pays them too little."
    assert sm.sentence_faults(swept, typed) == ["M5 word 'sweep account'"]
