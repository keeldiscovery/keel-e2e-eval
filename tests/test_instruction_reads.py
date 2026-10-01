"""A belief that reads an earlier belief's measurement (spec 025 FR-011, US5, T013).

`MARKS_VERSION` 8, judgement call 27. This eval scores the model's **raw** answer -- `runner.py`
stores `response["result"]` and applies it to nothing, and keel-cloud's validator is shelled for a
verdict and hands no resolved `Assumption` back. So a belief carrying `reads: {stage, line}` and no
expectation arrives at `produced_view` with `type: None`, `structural_candidate` refuses it on its
first line, and `golden_belief_recall` falls by one line per reference on an instruction change that
was supposed to move it by nothing.

`align.resolve_reads` is the correction: the referent's whole expectation, copied out of the
`earlier_lines` **this eval itself numbered and sent**, before alignment. The test that matters is
the equivalence one -- a referencing belief must align exactly as the same belief written longhand
does, on all eight fields -- because that is what makes judgement call 26 true rather than hopeful.
"""

from __future__ import annotations

import copy

from instructions import align as align_mod

#: One entry of `context.earlier_lines`: design §6A.4's eight keys, no more and no fewer.
INTERVAL_LINE = {
    "stage": "PROBLEM", "line": 3,
    "heading": "Settling takes most of an hour",
    "statement": "A parent woken at night spends 20 to 45 minutes settling the baby.",
    "measure": {"kind": "DURATION", "unit": "minutes", "per": None},
    "band": {"lower": {"value": 20, "inclusive": True, "exact": False},
             "upper": {"value": 45, "inclusive": True, "exact": False}},
    "role": "Parent of a baby under one",
    "risk": "LOAD_BEARING",
}

CHOICE_LINE = {
    "stage": "PROBLEM", "line": 1,
    "heading": "They try more than one thing",
    "statement": "The parent tried more than one thing before the baby settled.",
    "measure": None,
    "band": {"options": ["yes", "no"], "expected": "yes"},
    "role": "Parent of a baby under one",
    "risk": "SUPPORTING",
}

LONGHAND_INTERVAL = {
    "type": "INTERVAL", "measure": {"kind": "DURATION", "unit": "minutes", "per": None},
    "lower": {"value": 20, "inclusive": True, "exact": False},
    "upper": {"value": 45, "inclusive": True, "exact": False},
}


def _referencing(**overrides) -> dict:
    belief = {"heading": "They will pay to get that back",
              "statement": "A parent who spends that long settling will pay to shorten it.",
              "risk": "LOAD_BEARING", "mark": "PROXY",
              "founderPhrase": "they'd pay to get that hour back",
              "reads": {"stage": "PROBLEM", "line": 3}}
    belief.update(overrides)
    return belief


# ------------------------------------------------------------------------------- it does resolve

def test_a_reference_is_given_the_referents_whole_expectation():
    beliefs, unresolved = align_mod.resolve_reads([_referencing()], [INTERVAL_LINE])

    assert unresolved == 0
    assert beliefs[0]["expectation"] == LONGHAND_INTERVAL


def test_a_choice_reference_copies_the_options_and_the_expected_option():
    belief = _referencing(reads={"stage": "PROBLEM", "line": 1})

    beliefs, unresolved = align_mod.resolve_reads([belief], [CHOICE_LINE])

    assert unresolved == 0
    assert beliefs[0]["expectation"] == {
        "type": "CHOICE", "options": ["yes", "no"], "expected": "yes"}


def test_only_the_expectation_is_copied_and_the_input_is_not_mutated():
    """`risk`, `mark`, `founderPhrase`, `heading` and `statement` stay the belief's own -- they are
    its claim about its own stage, and the referent's would put one stage's words round another's
    claim."""
    original = _referencing()
    before = copy.deepcopy(original)

    beliefs, _ = align_mod.resolve_reads([original], [INTERVAL_LINE])

    assert original == before, "resolve_reads copies; it never writes through"
    resolved = beliefs[0]
    assert resolved["heading"] == "They will pay to get that back"
    assert resolved["risk"] == "LOAD_BEARING"
    assert resolved["mark"] == "PROXY"
    assert resolved["founderPhrase"] == "they'd pay to get that hour back"
    assert resolved["statement"] == original["statement"]


def test_a_belief_that_reads_nothing_is_passed_through_untouched():
    plain = {"heading": "h", "statement": "s", "expectation": LONGHAND_INTERVAL}
    beliefs, unresolved = align_mod.resolve_reads([plain], [INTERVAL_LINE])
    assert (beliefs, unresolved) == ([plain], 0)


# ------------------------------------------------------- the equivalence that makes call 26 true

class _Golden:
    """The corpus side of a pair, in `corpus.GoldenBelief`'s shape and no more of it than
    `align.golden_view` reads."""

    def __init__(self):
        self.id = "S4"
        self.expectation = LONGHAND_INTERVAL
        self.risk = "LOAD_BEARING"
        self.mark = "PROXY"
        self.founder_phrase = "they'd pay to get that hour back"
        self.heading = "They will pay to get that back"
        self.statement = "A parent who spends that long settling will pay to shorten it."


def test_a_reference_aligns_exactly_as_the_same_belief_written_longhand_does():
    """SC-005, and the whole point of judgement call 27: with the expectation copied in first,
    `align.FIELDS` does not change and neither does the recall denominator."""
    golden = _Golden()
    longhand = _referencing(expectation=LONGHAND_INTERVAL)
    longhand.pop("reads")

    referencing, unresolved = align_mod.resolve_reads([_referencing()], [INTERVAL_LINE])

    from_reference = align_mod.align([golden], referencing)
    from_longhand = align_mod.align([golden], [longhand])

    assert unresolved == 0
    assert len(from_reference.matched) == len(from_longhand.matched) == 1
    assert from_reference.matched[0].fields == from_longhand.matched[0].fields
    assert all(from_reference.matched[0].fields[name] is True for name in align_mod.FIELDS)
    assert from_reference.matched[0].score == from_longhand.matched[0].score


def test_an_unresolved_reference_does_not_match_at_all():
    """Production gives a derivation failure one repair turn; this eval has never had one, so an
    unresolvable reference is counted and left to fail -- never retried, never excused."""
    beliefs, unresolved = align_mod.resolve_reads(
        [_referencing(reads={"stage": "PROBLEM", "line": 99})], [INTERVAL_LINE])

    assert unresolved == 1
    assert align_mod.align([_Golden()], beliefs).matched == []


# ----------------------------------------------------------------- the four it refuses to resolve

def test_an_ordinal_out_of_range_is_unresolved():
    _, unresolved = align_mod.resolve_reads(
        [_referencing(reads={"stage": "PROBLEM", "line": 9})], [INTERVAL_LINE])
    assert unresolved == 1


def test_a_stage_that_is_not_an_earlier_one_is_unresolved():
    _, unresolved = align_mod.resolve_reads(
        [_referencing(reads={"stage": "COMMERCIAL", "line": 3})], [INTERVAL_LINE])
    assert unresolved == 1


def test_a_belief_carrying_both_a_reads_and_an_expectation_keeps_its_own_and_is_counted():
    """Design §6A.5: *"Both, or neither, is a shape refusal."* The belief keeps what it wrote --
    this module never overwrites an expectation -- and the shape is counted anyway, because a shape
    the contract refuses is not a reference that worked."""
    own = {"type": "CHOICE", "options": ["yes", "no"], "expected": "no"}

    beliefs, unresolved = align_mod.resolve_reads(
        [_referencing(expectation=own)], [INTERVAL_LINE])

    assert unresolved == 1
    assert beliefs[0]["expectation"] == own


def test_a_chain_is_refused_outright():
    """Design §6A.5 step 4: **the referent must own its expectation.** A line that itself reads
    another is one indirection too many -- the second belief could have named the first."""
    chained = dict(INTERVAL_LINE, reads={"stage": "PROBLEM", "line": 1})

    _beliefs, unresolved = align_mod.resolve_reads([_referencing()], [chained])

    assert unresolved == 1


def test_a_line_with_no_band_at_all_is_not_a_referent():
    """The other half of *owns its expectation*: there is nothing to copy, so there is no reference
    -- counted, and never quietly resolved to an empty expectation that would align with nothing."""
    bandless = {k: v for k, v in INTERVAL_LINE.items() if k != "band"}

    _beliefs, unresolved = align_mod.resolve_reads([_referencing()], [bandless])

    assert unresolved == 1


def test_two_beliefs_reading_one_line_are_two_references_and_both_resolve():
    """Judgement call 26: *two lines reading one control are two lines in the recall denominator;
    the control they share is one.* That is not a chain and is not an error."""
    both = [_referencing(), _referencing(heading="and so will the agency")]

    beliefs, unresolved = align_mod.resolve_reads(both, [INTERVAL_LINE])

    assert unresolved == 0
    assert [b["expectation"] for b in beliefs] == [LONGHAND_INTERVAL, LONGHAND_INTERVAL]


def test_align_fields_did_not_change():
    """FR-011's last clause, and judgement call 26's: the eight fields still decide a pair. What
    changed is that a referencing belief now arrives at them whole."""
    assert align_mod.FIELDS == ("type", "kind", "unit", "per", "expected_or_band",
                                "risk", "mark", "founder_phrase")
