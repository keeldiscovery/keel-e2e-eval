"""Spec 108 -- a reworded founder row is picked by its nearest label and named as a drift, not a stop.

Spec 104 picks the founder's row on Choose by its exact label and stops by name where none is drafted. On a live
journey (`strict=False`) Keel's list writer sometimes rewords the founder's label against spec 081's word-for-word
rule; where no row equals the typed label, the one nearest row is picked and one DRIFT finding names the rewording
(FR-1); no near row, or more than one, stops as 104 does, and a typed row not drafted at all is named in a finding
beside 104's *Keel added* (FR-2). The three cases of 2026-10-30 are fixtures (FR-4).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from evals import corpus_scenario
from harness import vectors_script as vs

FIXTURES = Path(__file__).parent / "fixtures" / "runs"
#: `runs/20261030T183150Z-backtest-21-codyco` (spec 104's fixture), `...T150723Z-backtest-13-aircaps`,
#: `...T173645Z-backtest-08-fresco` -- each file's `source` says which lines.
CODYCO = json.loads((FIXTURES / "21-codyco-choose-104" / "solution.json").read_text(encoding="utf-8"))
AIRCAPS = json.loads((FIXTURES / "13-aircaps-choose-108" / "solution.json").read_text(encoding="utf-8"))
FRESCO = json.loads((FIXTURES / "08-fresco-choose-108" / "commercial.json").read_text(encoding="utf-8"))


@dataclass
class _J:
    strict: bool = False
    findings: list = field(default_factory=list)


def _case(fixture: dict, key: str) -> tuple[dict, vs.CalibrationAnswer]:
    case = fixture["dimensions"][key]
    return ({"dimension": key, "draft": {"items": case["drafted"]}},
            vs.CalibrationAnswer(dimension=key, body=case["typed"], text=case["text"]))


def _answer(key: str, labels: list[str], picked: int) -> vs.CalibrationAnswer:
    return vs.CalibrationAnswer(dimension=key, text="; ".join(labels), body={
        "dimension": key, "list": {"items": [{"label": label} for label in labels], "pickedIndex": picked}})


def _question(key: str, labels: list[str]) -> dict:
    return {"dimension": key, "draft": {"items": [{"label": label} for label in labels]}}


def _drift(typed: str, drafted: str) -> str:
    return f"DRIFT: Keel reworded the founder's row '{typed}' as '{drafted}' (spec 081)"


# ----------------------------------------------------------------------------- the fold

@pytest.mark.parametrize(("typed", "drafted"), [
    ("Unanswered calls could be forwarded to another number", "Unanswered calls can be forwarded to another number"),
    ("They would charge the glasses", "They will charge the glasses."),
    ("Pairing the glasses", "pair the glasses"),
    ("Charged the glasses every day", "Charge the glasses, every day"),
    ("The hotel's owner", "the hotels owner"),
])
def test_the_same_words_once_folded(typed, drafted):
    """FR-1: case, punctuation, *-s / -ed / -ing* and *could / can / would / will* fold to the same words."""
    assert corpus_scenario._folded_words(typed) == corpus_scenario._folded_words(drafted)


@pytest.mark.parametrize(("typed", "drafted"), [
    ("The PMS took bookings from outside systems", "The PMS takes bookings from outside systems"),
    ("Calls are not forwarded", "Calls are forwarded"),
    ("Calls can't be forwarded to the desk", "Calls can be forwarded to the desk"),
])
def test_what_does_not_fold(typed, drafted):
    """No irregular past (*took* / *takes*); a negation is a word, never folded away."""
    assert corpus_scenario._folded_words(typed) != corpus_scenario._folded_words(drafted)
    assert corpus_scenario.nearest_rows(typed, [drafted], [typed]) == []


# ----------------------------------------------------------------------------- FR-1 / FR-4: the three cases

def test_21_codyco_the_tense_fold_picks_the_row_and_writes_the_drift_line():
    """`183150Z`: *could be forwarded* drafted *can be forwarded*; the fold finds the one row, row 0, and the finding
    names both labels. The walk goes on to adoption friction."""
    key = "solution.compatibility"
    question, answer = _case(CODYCO, key)
    j = _J()
    drafted = "Unanswered calls can be forwarded to another number"
    assert corpus_scenario._choose_label(j, question, answer) == (drafted, 0)
    assert drafted == CODYCO["dimensions"][key]["picked_on_screen"]
    assert j.findings == [{
        "what": _drift("Unanswered calls could be forwarded to another number", drafted),
        "served": {"dimension": key, "typed": "Unanswered calls could be forwarded to another number",
                   "drafted": drafted, "rows": [r["label"] for r in CODYCO["dimensions"][key]["drafted"]]}}]


def test_13_aircaps_the_rewording_picks_by_content_words():
    """`150723Z`: *Wear the glasses, paired to the phone* drafted *Pair the glasses to their phone* (and Keel split
    *Wear the glasses in conversations* out of it). No row has the same words; the one whose content words are all
    the typed label's (3 of its 4) is picked -- the row the walk picked on screen that day."""
    key = "solution.adoption_friction"
    question, answer = _case(AIRCAPS, key)
    j = _J()
    drafted = "Pair the glasses to their phone"
    assert corpus_scenario._choose_label(j, question, answer) == (drafted, 0)
    assert drafted == AIRCAPS["dimensions"][key]["picked_on_screen"]
    assert [f["what"] for f in j.findings] == [_drift("Wear the glasses, paired to the phone", drafted)]


def test_13_aircaps_compatibility_kept_the_label_so_no_finding():
    """The same walk's compatibility draft kept the founder's labels word for word: picked by label, no finding."""
    question, answer = _case(AIRCAPS, "solution.compatibility")
    j = _J()
    assert corpus_scenario._choose_label(j, question, answer) == ("Their phone was with them and online", 0)
    assert j.findings == []


def test_08_fresco_the_missing_row_stops_and_names_what_was_left_out():
    """`173645Z`: *A trial on one live job* was not drafted at all (Keel drafted *A budget approval* in its place).
    FR-2: the stop of 104, by name, and one finding naming the typed row the draft left out, beside 104's
    *Keel added*."""
    key = "commercial.purchase_friction"
    question, answer = _case(FRESCO, key)
    j = _J()
    corpus_scenario._name_keel_added(j, key, question, answer)
    with pytest.raises(vs.VectorsScriptError) as refused:
        corpus_scenario._choose_label(j, question, answer)
    said = str(refused.value)
    assert "'A trial on one live job' is not on the drafted list (spec 104 FR-1)" in said
    assert "Keel left out ['A trial on one live job'] (spec 108 FR-2)" in said
    assert [f["what"] for f in j.findings] == ["Purchase friction: Keel added: 'A budget approval'",
                                               "Purchase friction: Keel left out: 'A trial on one live job'"]
    assert j.findings[1]["served"]["left out"] == ["A trial on one live job"]
    assert corpus_scenario.keel_left_out(question, answer) == ["A trial on one live job"]


def test_08_fresco_buyer_payer_kept_the_label_so_no_finding():
    question, answer = _case(FRESCO, "commercial.buyer_payer_alignment")
    j = _J()
    assert corpus_scenario._choose_label(j, question, answer) == ("The CFO", 1)
    assert j.findings == []


# ----------------------------------------------------------------------------- FR-1: two near rows, the guards

@pytest.mark.parametrize("key", sorted(vs.PICKED))
def test_two_near_rows_stop_by_name(key):
    """FR-1: more than one row as near (here both carry every content word) stops as 104 does, naming them; no
    DRIFT line is written."""
    typed = ["Charge the glasses", "Set which calls go to the desk"]
    rows = ["Charge the glasses every day", "Charge the glasses at night", typed[1]]
    j = _J()
    with pytest.raises(vs.VectorsScriptError) as refused:
        corpus_scenario._choose_label(j, _question(key, rows), _answer(key, typed, 0))
    said = str(refused.value)
    assert key in said and "'Charge the glasses' is not on the drafted list (spec 104 FR-1)" in said
    assert "2 rows are as near (['Charge the glasses every day', 'Charge the glasses at night'], spec 108 FR-1)" \
        in said
    assert j.findings == []


def test_the_nearest_tier_wins_over_a_looser_one():
    """A row with the same words once folded is nearer than one that only carries every content word."""
    rows = ["Unanswered calls forwarded to another number today", "Unanswered calls can be forwarded to another number"]
    typed = ["Unanswered calls could be forwarded to another number"]
    assert corpus_scenario.nearest_rows(typed[0], rows, typed) == [rows[1]]


def test_another_typed_row_is_never_the_rewording():
    """A drafted row that is another of the founder's typed labels, word for word, is the founder's own row, not a
    rewording of the picked one."""
    typed = ["Charge the glasses", "Charge the glasses every day"]
    j = _J()
    with pytest.raises(vs.VectorsScriptError, match="Keel left out \\['Charge the glasses'\\]"):
        corpus_scenario._choose_label(j, _question("solution.adoption_friction", [typed[1]]),
                                      _answer("solution.adoption_friction", typed, 0))


def test_a_one_word_row_is_not_near_a_long_label():
    """The subset tier asks for at least half the typed label's content words."""
    typed = ["Wear the caption glasses with every hearing person"]
    assert corpus_scenario.nearest_rows(typed[0], ["Glasses"], typed) == []


def test_the_golden_walk_is_unchanged():
    """Strict reads no drafted row: the typed label and index, and no finding."""
    j = _J(strict=True)
    question, answer = _case(AIRCAPS, "solution.adoption_friction")
    assert corpus_scenario._choose_label(j, question, answer) == ("Wear the glasses, paired to the phone", 0)
    assert j.findings == []
