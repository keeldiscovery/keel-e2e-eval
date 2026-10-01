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
        # One merged occasion serving two stages -- the shape every corpus entry's first anchor has
        # carried since the 2026-09-30 revision (`MARKS_VERSION` 8, judgement call 25).
        questionnaire={"anchors": [
            {"id": "A1", "stages": ["PROBLEM", "SOLUTION"],
             "prompt": "Think of the last delivery.",
             "taps": ["hasn't happened"], "selections": []}]},
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
    # `MARKS_VERSION` 8, judgement call 24 (keel-cloud spec 049): **no `stage`**. It used to travel
    # beside `anchor_id`, first, because decision 18 (DRIFT #37) made the pair the only thing that
    # told two occasions apart. One questionnaire a project makes `Q7` project-wide and a merged
    # occasion serves two stages' beliefs, so a `stage` here would name nothing -- and this is the
    # four keys `interpret.md` has described its context as all along (design §5.2's drift).
    assert list(built["anchors"][0]) == ["anchor_id", "prompt", "text", "tap"]
    assert all("stage" not in anchor for anchor in built["anchors"])


def test_the_tap_table_covers_every_tap_the_frozen_corpus_writes():
    for english in ("hasn't happened", "can't recall", "rather not say"):
        assert context_mod.tap_enum(english) in {"HASNT_HAPPENED", "CANT_RECALL", "RATHER_NOT_SAY"}


# ----------------------------------------------- spec 025 T014: `earlier_lines` (keel-cloud 049)

EARLIER_KEYS = ["stage", "line", "heading", "statement", "measure", "band", "role", "risk"]


def test_earlier_lines_is_empty_for_the_problem_stage(entry):
    """`[]`, and the key is then never written at all -- exactly as `putEarlierLines` returns
    without writing it. The problem screen is where a project's first line is invented."""
    assert context_mod.earlier_lines(entry, "PROBLEM") == []


def test_earlier_lines_carries_design_6A4s_eight_keys_and_no_more(entry):
    lines = context_mod.earlier_lines(entry, "SOLUTION")

    assert len(lines) == 1
    assert list(lines[0]) == EARLIER_KEYS, "the eight keys, in the builder's own order"
    assert lines[0]["stage"] == "PROBLEM"
    assert lines[0]["line"] == 1
    assert lines[0]["role"] == "Restaurant managers", "the role's label, not its id"
    assert "mark" not in lines[0], "a later stage makes its own DIRECT/PROXY judgement"
    assert "founderPhrase" not in lines[0] and "founder_phrase" not in lines[0], \
        "the founder's words are about that stage's claim, not this one's"
    assert "selection" not in lines[0] and "id" not in lines[0], "nothing on the wire names an id"


def test_the_line_number_is_one_based_within_each_stage(entry):
    """`{stage, line}`, not a flat index: the list is grouped by stage in the context, and a reader
    of a failed job should see at a glance which stage was being joined."""
    lines = context_mod.earlier_lines(entry, "COMMERCIAL")

    assert [(l["stage"], l["line"]) for l in lines] == [("PROBLEM", 1), ("SOLUTION", 1)]


def test_a_choice_line_carries_a_null_measure_and_its_options(entry):
    line = context_mod.earlier_lines(entry, "SOLUTION")[0]
    assert line["measure"] is None, "present and null -- a Choice has no measure"
    assert line["band"] == {"options": ["yes", "no"], "expected": "yes"}


def test_an_interval_line_carries_its_measure_and_its_bands_own_flags():
    """The flags are carried, not dropped: `BucketBuilder` builds a different scale for an exclusive
    bound than for an inclusive one, so a later stage deciding whether its number is the same number
    has to be shown the same band."""
    interval = {"type": "INTERVAL",
                "measure": {"kind": "DURATION", "unit": "minutes", "per": "wake-up"},
                "lower": {"value": 20, "inclusive": True, "exact": False},
                "upper": {"value": 45, "inclusive": False, "exact": False}}
    entry = Entry(id="09-fixture", title="t", market={},
                  statements={"PROBLEM": "p", "SOLUTION": "s"},
                  roles=[{"id": "parent", "label": "New parents"}],
                  beliefs=[_belief("P1", "PROBLEM", "parent", expectation=interval)],
                  questionnaire={"anchors": []}, answers=[], expected={}, path=None,
                  sha256="0" * 64)

    line = context_mod.earlier_lines(entry, "SOLUTION")[0]

    assert line["measure"] == {"kind": "DURATION", "unit": "minutes", "per": "wake-up"}
    assert line["band"] == {"lower": {"value": 20, "inclusive": True, "exact": False},
                            "upper": {"value": 45, "inclusive": False, "exact": False}}
