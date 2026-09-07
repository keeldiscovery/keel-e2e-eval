"""`instructions/context.py`: every key the exporter names, in its order (spec 009 FR-018).

Stackless and modelless. What is being guarded is that the context this eval builds is the context
production builds -- because everything downstream is only meaningful if the prompt was the right
prompt, and a context key quietly missing would make a bad instruction look worse than it is.
"""

from __future__ import annotations

import pytest

from instructions import context as context_mod
from instructions.corpus import Entry, GoldenBelief, Person


def _belief(bid, stage, asked_of, **kw):
    return GoldenBelief(id=bid, stage=stage, heading=kw.get("heading", "h"),
                        statement=kw.get("statement", "s"),
                        founder_phrase=kw.get("founder_phrase"), risk="LOAD_BEARING",
                        asked_of=asked_of, mark="DIRECT",
                        expectation=kw.get("expectation", {"type": "CHOICE",
                                                           "options": ["yes", "no"],
                                                           "expected": "yes"}),
                        selection=kw.get("selection", "S1"), group=None)


@pytest.fixture()
def entry():
    return Entry(
        id="09-fixture", title="A fixture",
        market={"country": "GB", "region": None, "language": "en-GB"},
        statements={"PROBLEM": "The problem.", "SOLUTION": "The solution.",
                    "COMMERCIAL": "The commercial claim."},
        roles=[{"id": "manager", "label": "Restaurant managers", "roleType": "PRACTITIONER",
                "about": "runs the kitchen"},
               {"id": "buyer", "label": "Owner-managers", "roleType": "BUYER",
                "about": "signs for the tools", "market": {"country": "US", "region": "TX",
                                                           "language": "en-US"}}],
        beliefs=[_belief("P1", "PROBLEM", "manager"),
                 _belief("S1", "SOLUTION", "manager"),
                 _belief("C1", "COMMERCIAL", "buyer")],
        questionnaire={"anchors": [
            {"id": "A1", "stage": "PROBLEM", "prompt": "Think of the last delivery.",
             "taps": ["hasn't happened"], "selections": []},
            {"id": "A2", "stage": "SOLUTION", "prompt": "Think of that same delivery.",
             "taps": [], "selections": []}]},
        answers=[], expected={}, path=None, sha256="0" * 64)


ASSUMPTION_KEYS = ["problem_statement", "existing_roles", "market"]


def test_every_key_is_present_and_in_the_exporters_own_order(entry):
    built = context_mod.build_assumptions(entry, "PROBLEM", ASSUMPTION_KEYS)

    assert list(built) == ASSUMPTION_KEYS
    assert built["problem_statement"] == "The problem."
    assert built["market"] == {"country": "GB", "region": None, "language": "en-GB"}


def test_the_corpus_writes_its_statements_in_lower_case_and_they_are_still_found(entry):
    """Found by the dry-run gate, before a penny was spent: the corpus keys its statements
    `problem`/`solution`/`commercial` while the aggregate's own StageType is upper case. A
    `problem_statement` of `null` is the one value that makes an assumption screen legitimately
    ask (design decision 14) -- so the whole run would have measured the harness, not the prose."""
    lower = Entry(**{**entry.__dict__,
                     "statements": {"problem": "The problem.", "solution": "The solution.",
                                    "commercial": "The commercial claim."}})
    upper = Entry(**{**entry.__dict__,
                     "statements": {"PROBLEM": "The problem.", "SOLUTION": "The solution.",
                                    "COMMERCIAL": "The commercial claim."}})

    for source in (lower, upper):
        built = context_mod.build_assumptions(source, "PROBLEM", ASSUMPTION_KEYS)
        assert built["problem_statement"] == "The problem."


def test_a_key_this_harness_has_no_value_for_is_null_rather_than_absent(entry):
    # ScreenContextBuilder always writes every key for its screen, including the ones whose value
    # is absent -- so a key keel-cloud adds tomorrow appears in the prompt as itself, not missing.
    built = context_mod.build_assumptions(entry, "PROBLEM", ASSUMPTION_KEYS + ["something_new"])

    assert "something_new" in built
    assert built["something_new"] is None
    assert list(built)[-1] == "something_new"


def test_existing_roles_are_derived_from_earlier_stages_askedOf(entry):
    # research.md R5a: a corpus lists its roles flat, and the askedOf edge is the only evidence in
    # the file of which stage needed which role.
    assert context_mod.roles_for(entry, "PROBLEM") == []
    assert [r["id"] for r in context_mod.roles_for(entry, "SOLUTION")] == ["manager"]
    assert [r["id"] for r in context_mod.roles_for(entry, "COMMERCIAL")] == ["manager"]


def test_a_roles_own_market_rides_along_and_a_role_without_one_carries_no_key(entry):
    entry.beliefs.append(_belief("S2", "SOLUTION", "buyer"))
    roles = context_mod.roles_for(entry, "COMMERCIAL")

    by_id = {r["id"]: r for r in roles}
    assert "market" not in by_id["manager"]
    assert by_id["buyer"]["market"] == {"country": "US", "region": "TX", "language": "en-US"}


def test_a_blank_anchor_is_never_offered_and_a_tap_is_mapped_to_its_enum(entry):
    person = Person(person="Priya", picks={}, anchors={
        "A1": {"text": "Tuesday two weeks ago, the veg order.", "anchoring": "ANCHORED"},
        "A2": {"text": "   ", "anchoring": "GUESSED"},
        "A3": {"text": "Never had one.", "tap": "hasn't happened", "anchoring": "ANCHORED"}})

    built = context_mod.build_reading(entry, person, ["invitation_id", "anchors"])

    assert list(built) == ["invitation_id", "anchors"]
    assert built["invitation_id"] == "09-fixture/Priya"
    ids = [a["anchor_id"] for a in built["anchors"]]
    assert ids == ["A1", "A3"], "a blank anchor is not offered at all"
    assert built["anchors"][0]["prompt"] == "Think of the last delivery."
    assert built["anchors"][0]["tap"] is None
    assert built["anchors"][1]["tap"] == "HASNT_HAPPENED"
    # decision 18 / DRIFT #37: stage travels beside anchor_id, first -- A1 is on the entry's own
    # questionnaire (PROBLEM); A3 is not on it at all, so its stage is None rather than invented.
    assert list(built["anchors"][0]) == ["stage", "anchor_id", "prompt", "text", "tap"]
    assert built["anchors"][0]["stage"] == "PROBLEM"
    assert built["anchors"][1]["stage"] is None


def test_the_tap_table_covers_every_tap_the_frozen_corpus_writes():
    for english in ("hasn't happened", "can't recall", "rather not say"):
        assert context_mod.tap_enum(english) in {"HASNT_HAPPENED", "CANT_RECALL", "RATHER_NOT_SAY"}
