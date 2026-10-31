"""Spec 112's addendum (2026-10-30) -- keel-cloud 172's pins: Current solution's escape fits the act.

keel-cloud 172 (`ItemFrames.escapeFor`, `CommercialChain.side`): the list writer calls `handed_off`; where it is false
the item is served *I can't recall* (`cant_recall`, counted apart, said *Or say you can't recall.*), where it is true or
the list carries no call (every list before 172) *Someone else did it* (`someone_else_checks`). The call is stored on
the server and never reaches a wire, so the mirror (`instructions/spoken.py` `item_escape` / `served_escape`) reads it
off the SERVED item's escape; the walk sends the code served (`vectors_script.served_escape_picks`: keel-cloud refuses
the other, *not this question's way out*). The pins of lists with no call stand: `tests/test_follow_up_ladder.py`'s
*Current solution: an escape is apart* row and `tests/fixtures/corpus/10-fixture-b2b.yaml`'s `someone_else_checks`.

No browser, no stack."""
from __future__ import annotations

import dataclasses
import inspect
import types
from pathlib import Path

import pytest

from evals import corpus_scenario as cs
from harness import vectors_script as vs
from instructions import cloud_corpus as cloud_mod
from instructions import registry as registry_mod
from instructions import spoken as spoken_mod
from tests import v9_fixtures as fx

KEY = "problem.current_solution_satisfaction"
CANT = {"code": "CANT_RECALL", "label": "I can't recall"}
SOMEONE = {"code": "SOMEONE_ELSE_CHECKS", "label": "Someone else did it that night"}


def _registry():
    """The fixture registry with Current solution's row as the registry of record has it since keel-cloud 123."""
    document = fx.registry_document()
    for dimension in document["dimensions"]:
        if dimension["key"] == KEY:
            dimension["respondent"]["escape"] = {"code": "someone_else_checks", "label": "Someone else did it",
                                                 "counts": "apart"}
    return registry_mod.from_document(document, source="spec 112 addendum fixture", check=False)


REG = _registry()


# ------------------------------------------------------------------------------- the call, off the served item

@pytest.mark.parametrize("served, want", [
    (None, None), ({}, None), ({"escape": None}, None), ("", None),
    (CANT, False), ({"escape": CANT}, False), ("cant_recall", False), ("CANT_RECALL", False), ("I can't recall", False),
    ({"label": "I can't  recall"}, False),
    (SOMEONE, True), ({"escape": SOMEONE}, True), ("someone_else_checks", True), ("Someone else did it", True),
])
def test_handed_off_of_the_served_item(served, want):
    assert spoken_mod.handed_off_of(served) is want


@pytest.mark.parametrize("served, want", [
    (None, "Someone else did it"),                                    # a list with no call: the registry's row
    ({"escape": CANT}, "I can't recall"),                             # handed_off false
    (CANT, "I can't recall"),
    ({"escape": SOMEONE}, "Someone else did it"),                     # handed_off true: the row (123's occasion apart)
])
def test_current_solutions_escape_is_the_served_items(served, want):
    assert spoken_mod.item_escape(REG, KEY, None, served) == want
    assert spoken_mod.served_escape(REG, KEY, None, served) == want
    assert spoken_mod.said(spoken_mod.served_escape(REG, KEY, None, served)) == spoken_mod.said(want)


def test_the_spoken_line_of_cant_recall_is_the_second_person():
    assert spoken_mod.said(spoken_mod.CANT_RECALL_ESCAPE) == spoken_mod.said("you can't recall")


def test_no_other_dimension_reads_the_served_item():
    """keel-cloud 172 FR-4: the resolver moves Current solution's escape alone."""
    for dimension in REG.dimensions:
        if dimension.key == KEY:
            continue
        assert spoken_mod.served_escape(REG, dimension.key, None, CANT) == spoken_mod.served_escape(REG, dimension.key)
        assert spoken_mod.item_escape(REG, dimension.key, None, CANT) == spoken_mod.item_escape(REG, dimension.key)


# ------------------------------------------------------------------------------------- S6 on the composed record

CURRENT = dict(entry="09-fixture", key=KEY, part=1, question="How did finding them go?", stem="How did finding them go?",
               options=("Found them straight away", "Found them after a quick look", "It took a full search",
                        "Found them only after being late", "Never found them that morning"),
               anchor=None, count_line="I'll read five options.",
               options_line="Found them straight away; found them after a quick look; it took a full search; found "
                            "them only after being late; or never found them that morning.", transform="none")


def _item(escape, line):
    return cloud_mod.ComposedItem(**CURRENT, escape=escape, escape_line=line)


def test_s6_holds_either_served_escape_and_its_own_spoken_line():
    assert spoken_mod.item_faults(_item("Someone else did it", "Or say someone else did it."), REG) == []
    assert spoken_mod.item_faults(_item("I can't recall", "Or say you can't recall."), REG) == []
    # the line says the other way out than the label served
    assert [f.split(":")[0] for f in spoken_mod.item_faults(_item("I can't recall", "Or say someone else did it."),
                                                            REG)] == ["S6"]
    assert [f.split(":")[0] for f in spoken_mod.item_faults(_item("Someone else did it", "Or say you can't recall."),
                                                            REG)] == ["S6"]
    # an escape that is neither is still the registry's fault
    assert "S6" in [f.split(":")[0] for f in spoken_mod.item_faults(_item("I can't tell", "Or say you can't tell."),
                                                                    REG)]


# ----------------------------------------------------------------------------------------- the walk: the code served

def _person(chip="SOMEONE_ELSE_CHECKS", **over):
    picks = [vs.Pick(dimension=KEY, chip=chip), vs.Pick(dimension="problem.importance", codes=["rival_1", "rival_2"])]
    return vs.PersonInputs(person="Ana Ruiz", link=vs.LINK_PRIMARY, recency=True, story="x", anchor_chip=None,
                           picks=picks, pilot_opt_in=False, anchoring="ANCHORED", **over)


def test_the_walk_sends_cant_recall_where_it_is_served():
    person, notes = vs.served_escape_picks(_person(), {KEY: {"escape": CANT}})
    assert [p.chip for p in person.picks] == ["CANT_RECALL", None]
    assert person.picks[1] == _person().picks[1]                                  # Importance untouched
    assert notes == ["Ana Ruiz: Current solution's escape is served as \"I can't recall\" (keel-cloud 172: the list "
                     "writer judged the act one that cannot be handed off); the file's someone_else_checks is sent as "
                     "cant_recall, the code served (spec 112's addendum)"]
    assert person.response("tok")["answers"][0] == {"itemId": vs.item_id("tok", KEY), "chip": "CANT_RECALL"}


def test_the_walk_sends_someone_else_where_that_is_served():
    person, notes = vs.served_escape_picks(_person("CANT_RECALL"), {KEY: {"escape": {"code": "someone_else_checks",
                                                                                     "label": "Someone else did it"}}})
    assert person.picks[0].chip == "SOMEONE_ELSE_CHECKS" and "that can be handed off" in notes[0]


@pytest.mark.parametrize("person, items", [
    (_person(), {KEY: {"escape": SOMEONE}}),                       # the code served is the file's: a list with no call
    (_person(), {}),                                               # nothing served (the item not on the link)
    (_person(), {KEY: {"escape": None}}),
    (_person("NONE_OF_THESE"), {KEY: {"escape": CANT}}),           # no Current solution escape in the file
    (dataclasses.replace(_person(), picks=[vs.Pick(dimension=KEY, codes=["outcome_1"])]), {KEY: {"escape": CANT}}),
])
def test_the_walk_leaves_the_person_where_nothing_moves(person, items):
    assert vs.served_escape_picks(person, items) == (person, [])


def test_answer_one_re_expresses_before_the_items_are_held():
    source = inspect.getsource(cs._answer_one)
    assert "vs.served_escape_picks(person, items)" in source
    assert source.index("served_escape_picks") < source.index("interview carries every item this person")


# ------------------------------------------------------------------------- the pins of lists with no call stand

def test_the_lists_with_no_call_keep_someone_else():
    fixture = Path(__file__).parent / "fixtures" / "corpus" / "10-fixture-b2b.yaml"
    text = fixture.read_text(encoding="utf-8")
    assert "escape: someone_else_checks" in text and "chip: someone_else_checks" in text
    assert "handed_off" not in text                                                # no call: the registry's escape
    ladder = (Path(__file__).parent / "test_follow_up_ladder.py").read_text(encoding="utf-8")
    assert 'chip="SOMEONE_ELSE_CHECKS"' in ladder
    assert spoken_mod.served_escape(REG, KEY) == spoken_mod.registry_escape(REG, KEY) == "Someone else did it"
    assert {"someone_else_checks", "cant_recall"} <= vs.ESCAPES


def test_the_consumer_budget_and_off_chain_escapes_are_unmoved():
    entry = types.SimpleNamespace(chain=lambda: False, b2b=lambda: False)
    assert spoken_mod.item_escape(REG, "commercial.ability_to_pay", entry, CANT) == spoken_mod.CONSUMER_BUDGET_ESCAPE
