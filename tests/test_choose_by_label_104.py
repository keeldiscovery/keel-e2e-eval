"""Spec 104 -- Choose picks the founder's own row, found by its label.

The corpus's `pickedIndex` indexes the entry's TYPED items (`list.items`); on a live journey (`strict=False`, the
back-test and S-012) Keel's list writer may draft rows of its own beside the founder's, so Choose finds the founder's
row on the drafted list by its label (FR-1), for every `vs.PICKED` dimension (FR-2), names the rows Keel added in one
finding per dimension (FR-3), and refuses by name where the label is not drafted -- never row 0. The golden walk
(`strict=True`) keeps its behaviour: the typed label and the typed index.
"""
from __future__ import annotations

import inspect
import json
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from evals import corpus_scenario
from harness import vectors_script as vs

#: From `runs/20261030T183150Z-backtest-21-codyco` (the fixture's `source` says which lines).
CODYCO = json.loads((Path(__file__).parent / "fixtures" / "runs" / "21-codyco-choose-104" / "solution.json")
                    .read_text(encoding="utf-8"))


@dataclass
class _J:
    strict: bool = False
    findings: list = field(default_factory=list)


def _answer(key: str, labels: list[str], picked: int) -> vs.CalibrationAnswer:
    return vs.CalibrationAnswer(dimension=key, text="; ".join(labels), body={
        "dimension": key, "list": {"items": [{"label": label} for label in labels], "pickedIndex": picked}})


def _question(key: str, labels: list[str]) -> dict:
    return {"dimension": key, "draft": {"items": [{"label": label} for label in labels]}}


def _old_live_pick(question: dict, answer: vs.CalibrationAnswer) -> tuple[str, int]:
    """`_choose_label`'s live branch before spec 104: the entry's index applied to the drafted list, or its last."""
    rows = (question.get("draft") or {}).get("items") or []
    index = (answer.listed or {}).get("pickedIndex") or 0
    held = min(index, max(0, len(rows) - 1))
    return rows[held].get("label"), held


TYPED = ["Let an AI answer guests in the hotel's voice", "Set which calls the AI hands to the desk"]
PREPENDED = ["Forward unanswered calls to Codyco", "Connect Codyco to the hotel's PMS", *TYPED]


@pytest.mark.parametrize("key", sorted(vs.PICKED))
def test_a_drafted_list_with_two_prepended_rows_picks_the_founders_label(key):
    """FR-1 / FR-2: Keel's two rows ahead of the founder's; `pickedIndex` 0 is the founder's first typed item, found
    at row 2 -- not Keel's row 0 (what the walk picked before)."""
    answer = _answer(key, TYPED, 0)
    question = _question(key, PREPENDED)
    assert _old_live_pick(question, answer) == ("Forward unanswered calls to Codyco", 0)
    assert corpus_scenario._choose_label(_J(), question, answer) == (TYPED[0], 2)
    assert corpus_scenario._choose_label(_J(), question, _answer(key, TYPED, 1)) == (TYPED[1], 3)


@pytest.mark.parametrize("key", sorted(vs.PICKED))
def test_a_list_in_the_founders_order_picks_the_same_row_as_before(key):
    """FR-1: where Keel drafted the founder's own list, the label finds the row the index found."""
    labels = ["Nobody else", "The hotel's owner", "The finance director"]
    for picked in range(len(labels)):
        answer, question = _answer(key, labels, picked), _question(key, labels)
        assert corpus_scenario._choose_label(_J(), question, answer) == _old_live_pick(question, answer) \
            == (labels[picked], picked)


@pytest.mark.parametrize("key", sorted(vs.PICKED))
def test_a_label_not_drafted_refuses_by_name_never_row_0(key):
    """FR-1: the picked label not on the drafted list stops the walk, naming the dimension, the label, what Keel
    drafted and what the founder typed; an empty draft refuses the same way."""
    answer = _answer(key, TYPED, 0)
    with pytest.raises(vs.VectorsScriptError) as refused:
        corpus_scenario._choose_label(_J(), _question(key, ["Forward unanswered calls to Codyco", TYPED[1]]), answer)
    said = str(refused.value)
    assert key in said and repr(TYPED[0]) in said and "not on the drafted list" in said and "spec 104" in said
    assert "Forward unanswered calls to Codyco" in said
    with pytest.raises(vs.VectorsScriptError, match="not on the drafted list"):
        corpus_scenario._choose_label(_J(), {"dimension": key}, answer)


def test_the_golden_walk_keeps_the_typed_label_and_index():
    """Strict is unchanged: the scripted list is the entry's own, so the typed label and its index -- the drafted
    rows are not read, and nothing refuses."""
    answer = _answer("solution.adoption_friction", TYPED, 1)
    question = _question("solution.adoption_friction", ["anything else"])
    assert corpus_scenario._choose_label(_J(strict=True), question, answer) == (TYPED[1], 1)


def test_the_rows_keel_added_are_named_in_one_finding():
    """FR-3: one finding per dimension listing the drafted rows the entry did not type, in the drafted order; none
    where Keel drafted only the founder's."""
    key = "solution.adoption_friction"
    answer = _answer(key, TYPED, 0)
    assert corpus_scenario.keel_added(_question(key, PREPENDED), answer) == PREPENDED[:2]
    j = _J()
    corpus_scenario._name_keel_added(j, key, _question(key, PREPENDED), answer)
    corpus_scenario._name_keel_added(j, key, _question(key, TYPED), answer)
    what = "Adoption friction: Keel added: 'Forward unanswered calls to Codyco', 'Connect Codyco to the hotel's PMS'"
    assert j.findings == [{
        "what": what,
        "served": {"dimension": key, "drafted": PREPENDED, "typed": TYPED, "added": PREPENDED[:2]}}]


def test_the_leg_names_the_added_rows_off_the_golden_walk_and_refuses_inside_a_step():
    """FR-1 / FR-3 wired into `leg_calibrate`: on every PICKED dimension, the finding off strict, then the pick; a
    refusal recorded in its own step and re-raised."""
    source = inspect.getsource(corpus_scenario.leg_calibrate)
    picked = source[source.index("if key in vs.PICKED:"):source.index("j.corridor.list_choose(question, label)")]
    assert "if not j.strict:\n                _name_keel_added(j, key, question, answer)" in picked
    assert "except vs.VectorsScriptError:" in picked and "(spec 104 FR-1)" in picked and "raise\n" in picked


def _codyco(key: str) -> tuple[dict, vs.CalibrationAnswer]:
    case = CODYCO["dimensions"][key]
    return ({"dimension": key, "draft": {"items": case["drafted"]}},
            vs.CalibrationAnswer(dimension=key, body=case["typed"], text=case["text"]))


def test_21_codyco_adoption_friction_picks_the_ai_voice_not_keels_forwarding():
    """The re-walk of 2026-10-30: the entry types two efforts, `pickedIndex` 0 the AI voice; Keel prepends the
    forwarding and the PMS rows. The walk picked *Forward unanswered calls to Codyco* (the bundle's Choose step); by
    label it picks the founder's, row 2, and names Keel's two rows."""
    key = "solution.adoption_friction"
    question, answer = _codyco(key)
    case = CODYCO["dimensions"][key]
    assert _old_live_pick(question, answer) == (case["picked_on_screen"], 0)
    assert corpus_scenario._choose_label(_J(), question, answer) == ("Let an AI answer guests in the hotel's voice", 2)
    j = _J()
    corpus_scenario._name_keel_added(j, key, question, answer)
    assert [f["what"] for f in j.findings] == [
        "Adoption friction: Keel added: 'Forward unanswered calls to Codyco', 'Connect Codyco to the hotel's PMS'"]


def test_21_codyco_compatibility_was_reworded_so_the_walk_picks_it_and_names_the_drift():
    """Not foreseen by spec 104, from the same bundle: Keel's compatibility draft moved the founder's tense (*could be
    forwarded* -> *can be forwarded*, *took* -> *takes*, *were* -> *are*), so the drafted list does not keep the
    founder's labels word for word here. Spec 104 stopped the walk by name; spec 108 FR-1 picks the one row the tense
    fold finds and writes the DRIFT finding instead (`tests/test_reworded_row_108.py`). FR-3 still names all three
    rows as Keel's, by exact label. (The earlier re-walk `runs/20261030T161100Z-backtest-21-codyco` drafted them word
    for word.)"""
    key = "solution.compatibility"
    question, answer = _codyco(key)
    j = _J()
    assert corpus_scenario._choose_label(j, question, answer) == (
        "Unanswered calls can be forwarded to another number", 0)
    assert [f["what"] for f in j.findings] == [
        "DRIFT: Keel reworded the founder's row 'Unanswered calls could be forwarded to another number' as "
        "'Unanswered calls can be forwarded to another number' (spec 081)"]
    drafted = [row["label"] for row in CODYCO["dimensions"][key]["drafted"]]
    assert corpus_scenario.keel_added(question, answer) == drafted
