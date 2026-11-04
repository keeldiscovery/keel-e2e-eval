"""Spec 138 -- Compatibility's suggested row is the founder's own.

Cycle 13 (`quality/cycles/20261104-e3e22a8.md`): 10-palus' SOLUTION walk stopped at Compatibility -- the picked
condition *could wait one to two business days for their cash* was drafted capitalised and marked `suggested` (keel-cloud
121: the one founder condition most likely to be missing, with its why), and spec 112's `_founders_rows` dropped every
`suggested` row as Keel's. Since 138 the drop holds on Adoption friction (keel-cloud 171: Keel's one-time step) and
Purchase friction (Keel's suggested step) alone (FR-1); `keel_added` no longer names a row the founder typed once folded
(FR-2); the pick lands on Compatibility's suggested row (FR-3). FR-4: the cycle 13 shape on Compatibility and on
Adoption friction, and `keel_added`.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from evals import corpus_scenario
from harness import vectors_script as vs

COMPATIBILITY = corpus_scenario.COMPATIBILITY_KEY
ADOPTION = corpus_scenario.ADOPTION_KEY
PURCHASE = corpus_scenario.PURCHASE_FRICTION_KEY

#: 10-palus SOLUTION, cycle 13: the entry's three typed conditions (only the first two fit the 25-word Answer box),
#: `pickedIndex` 1.
TYPED = ["could keep their current bank while the reserve sat elsewhere",
         "could wait one to two business days for their cash",
         "had a cash policy that allowed bonds beyond Treasuries"]
#: Keel's draft: the first two, capitalised, the second marked `suggested` with a why (keel-cloud 121).
DRAFTED = [{"label": "Could keep their current bank while the reserve sat elsewhere"},
           {"label": "Could wait one to two business days for their cash", "suggested": True,
            "suggestedWhy": "Most treasury teams expect same-day access to their cash."}]
LABELS = [row["label"] for row in DRAFTED]


@dataclass
class _J:
    strict: bool = False
    findings: list = field(default_factory=list)


def _answer(key: str, labels: list[str], picked: int) -> vs.CalibrationAnswer:
    return vs.CalibrationAnswer(dimension=key, text="; ".join(labels), body={
        "dimension": key, "list": {"items": [{"label": label} for label in labels], "pickedIndex": picked}})


def _question(key: str, rows: list[dict]) -> dict:
    return {"dimension": key, "draft": {"items": rows}}


def _drift(typed: str, drafted: str) -> str:
    return f"DRIFT: Keel reworded the founder's row '{typed}' as '{drafted}' (spec 081)"


# ----------------------------------------------------------------------------- FR-1 / FR-3: the cycle 13 shape

def test_palus_compatibility_picks_the_suggested_founder_row_with_the_drift_finding():
    """FR-1 / FR-3 / FR-4: the typed pick lands on *Could wait ...*, row 1, the one Keel marked `suggested` -- with
    spec 081's DRIFT finding (the capital letter), as 21-codyco's *could forward ...* was found in cycle 13. No stop."""
    question, answer = _question(COMPATIBILITY, DRAFTED), _answer(COMPATIBILITY, TYPED, 1)
    assert corpus_scenario._founders_rows(question) == LABELS
    j = _J()
    assert corpus_scenario._choose_label(j, question, answer) == (LABELS[1], 1)
    assert j.findings == [{"what": _drift(TYPED[1], LABELS[1]),
                           "served": {"dimension": COMPATIBILITY, "typed": TYPED[1], "drafted": LABELS[1],
                                      "rows": LABELS}}]
    # the other typed row lands on its own capitalised row the same way
    assert corpus_scenario._choose_label(_J(), question, _answer(COMPATIBILITY, TYPED, 0)) == (LABELS[0], 0)


def test_palus_shape_on_adoption_friction_still_stops():
    """FR-4: the same rows on Adoption friction, the suggested row Keel's own step (keel-cloud 171): it is no
    founder's row, the typed pick is near none of the founder's, and the stop of spec 104 stands, unchanged."""
    question, answer = _question(ADOPTION, DRAFTED), _answer(ADOPTION, TYPED, 1)
    assert corpus_scenario._founders_rows(question) == LABELS[:1]
    j = _J()
    with pytest.raises(vs.VectorsScriptError) as refused:
        corpus_scenario._choose_label(j, question, answer)
    said = str(refused.value)
    assert f"{TYPED[1]!r} is not on the drafted list (spec 104 FR-1)" in said
    assert f"Keel left out {TYPED[1:]!r} (spec 108 FR-2)" in said
    assert [f["what"] for f in j.findings] == [
        "Adoption friction: Keel left out: " + ", ".join(f"'{label}'" for label in TYPED[1:])]
    # 112's finding is untouched: Keel's marked step, with its why
    assert corpus_scenario.keel_added(question, answer) == [LABELS[1]]
    assert corpus_scenario.keel_suggested(question) == [{"label": LABELS[1], "why": DRAFTED[1]["suggestedWhy"]}]


def test_purchase_friction_keeps_112s_rule():
    """FR-1 / FR-3: on Purchase friction the suggested step is Keel's -- never a founder's row, never near a typed one,
    named as *Keel added* even where it reads like a typed row once folded; typed word for word, it is the pick."""
    question = _question(PURCHASE, DRAFTED)
    assert corpus_scenario._founders_rows(question) == LABELS[:1]
    with pytest.raises(vs.VectorsScriptError, match="not on the drafted list"):
        corpus_scenario._choose_label(_J(), question, _answer(PURCHASE, TYPED, 1))
    assert corpus_scenario.keel_added(question, _answer(PURCHASE, TYPED, 0)) == [LABELS[1]]
    assert corpus_scenario._choose_label(_J(), question, _answer(PURCHASE, LABELS, 1)) == (LABELS[1], 1)
    assert corpus_scenario.keel_added(question, _answer(PURCHASE, LABELS, 1)) == []


def test_a_typed_label_on_two_rows_picks_the_first_on_compatibility_the_founders_on_adoption():
    """FR-3: on Compatibility the `flagged` skip is off -- the first row equal to the typed label is the pick; on
    Adoption friction a typed label found on both is the founder's unmarked row, as spec 112 says."""
    rows = [{"label": TYPED[0], "suggested": True, "suggestedWhy": "x"}, {"label": TYPED[0]}]
    assert corpus_scenario._choose_label(_J(), _question(COMPATIBILITY, rows),
                                         _answer(COMPATIBILITY, TYPED, 0)) == (TYPED[0], 0)
    assert corpus_scenario._choose_label(_J(), _question(ADOPTION, rows), _answer(ADOPTION, TYPED, 0)) == (TYPED[0], 1)
    assert corpus_scenario._choose_label(_J(), _question(PURCHASE, rows), _answer(PURCHASE, TYPED, 0)) == (TYPED[0], 1)


def test_the_golden_walk_is_unchanged():
    j = _J(strict=True)
    assert corpus_scenario._choose_label(j, _question(COMPATIBILITY, DRAFTED), _answer(COMPATIBILITY, TYPED, 1)) == (
        TYPED[1], 1)
    assert j.findings == []


# ----------------------------------------------------------------------------- FR-2: Keel added, folded

def test_keel_added_names_no_capitalised_typed_row():
    """FR-2 / FR-4: cycle 13's *Compatibility: Keel added: 'Could keep ...', 'Could wait ...'* on rows the founder typed
    word for word (Keel's capital letter alone) was a false finding -- it goes; a row the founder never typed is still
    Keel's."""
    answer = _answer(COMPATIBILITY, TYPED, 1)
    assert corpus_scenario.keel_added(_question(COMPATIBILITY, DRAFTED), answer) == []
    j = _J()
    corpus_scenario._name_keel_added(j, COMPATIBILITY, _question(COMPATIBILITY, DRAFTED), answer)
    assert j.findings == []
    new = "Could move the reserve without a board vote"
    question = _question(COMPATIBILITY, [*DRAFTED, {"label": new}])
    assert corpus_scenario.keel_added(question, answer) == [new]
    j = _J()
    corpus_scenario._name_keel_added(j, COMPATIBILITY, question, answer)
    assert [f["what"] for f in j.findings] == [f"Compatibility: Keel added: '{new}'"]


def test_a_near_row_is_the_drift_not_keel_added():
    """FR-2: a row near a typed label but not equal once folded (spec 108's tiers 2 and 3) is the founder's reworded --
    the DRIFT finding of 108 on the pick, never *Keel added*."""
    typed = ["Unanswered calls could be forwarded to another number"]
    reworded = "Unanswered calls could be forwarded to another number at night"
    question = _question(COMPATIBILITY, [{"label": reworded}, {"label": "Keel's own row"}])
    answer = _answer(COMPATIBILITY, typed, 0)
    assert corpus_scenario.keel_added(question, answer) == ["Keel's own row"]
    j = _J()
    assert corpus_scenario._choose_label(j, question, answer) == (reworded, 0)
    assert [f["what"] for f in j.findings] == [_drift(typed[0], reworded)]


@pytest.mark.parametrize("key", sorted(set(vs.PICKED) - {ADOPTION, PURCHASE}))
def test_every_founders_dimension_reads_the_flag_as_the_founders(key):
    """FR-1: on every dimension but Adoption friction and Purchase friction, every drafted row is the founder's."""
    question = _question(key, DRAFTED)
    assert corpus_scenario._founders_rows(question) == LABELS
    assert corpus_scenario.keel_added(question, _answer(key, TYPED, 1)) == []
