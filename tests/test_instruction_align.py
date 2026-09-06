"""`instructions/align.py`: the fixed point, and the hard case (spec 009 FR-018, SC-002).

**The fixed point is the whole test.** Align every corpus entry's golden beliefs against
themselves: recall must be 100 %, every scored field must agree, every pair must be a belief with
itself, and no pair may need a judge. A matcher that cannot recognise the golden set as itself
cannot be trusted to score a model's — every number this eval reports would be an artefact of the
matcher rather than a fact about the instruction.

It runs against the real frozen corpus in the keel-cloud checkout, on purpose. A fixture would
prove the matcher consistent with a fixture; this proves it consistent with the thing the eval
actually scores.
"""

from __future__ import annotations

import pytest

from instructions import align as align_mod
from instructions import corpus as corpus_mod
from stack.config import load_config


@pytest.fixture(scope="module")
def corpus():
    config = load_config(validate=False)
    try:
        return corpus_mod.load(config.keel_cloud)
    except corpus_mod.CorpusError as reason:
        pytest.skip(str(reason))


def test_every_corpus_entry_aligned_against_itself_is_a_perfect_score(corpus):
    for entry in corpus.entries:
        for stage in corpus_mod.STAGES:
            goldens = entry.beliefs_for(stage)
            if not goldens:
                continue
            produced = [align_mod.as_wire(b) for b in goldens]

            alignment = align_mod.align(goldens, produced)

            where = f"{entry.id}/{stage}"
            assert len(alignment.matched) == len(goldens), f"{where}: recall is not 100 %"
            assert alignment.missing == [], f"{where}: {alignment.missing} unreached"
            assert alignment.extra == [], f"{where}: {alignment.extra} unexplained"
            assert alignment.ambiguous == [], f"{where}: needed a judge for {alignment.ambiguous}"
            assert alignment.judged == 0, f"{where}: a model decided part of the identity"
            for pair in alignment.matched:
                assert pair.golden_id == goldens[pair.produced_index].id, \
                    f"{where}: {pair.golden_id} matched somebody else's belief"
                for field, value in pair.fields.items():
                    assert value is not False, f"{where}/{pair.golden_id}: {field} disagreed"


def test_two_beliefs_on_one_shared_selection_pair_the_right_way_round_reversed(corpus):
    """01-countly's P4a/P4b: one multi-select, identical option lists, two expected options.

    Presented in the produced set's reverse order, because position must never decide a pair --
    the two are structurally indistinguishable apart from the option each expects, which is
    exactly the discrimination `expected_or_band` exists to make.
    """
    entry = corpus.by_id("01-countly")
    if entry is None:
        pytest.skip("01-countly is not in this corpus")
    shared = [b for b in entry.beliefs if b.id in {"P4a", "P4b"}]
    if len(shared) != 2:
        pytest.skip("01-countly no longer carries P4a/P4b")
    assert shared[0].selection == shared[1].selection, "the premise of this test"
    assert shared[0].expectation.get("options") == shared[1].expectation.get("options")

    alignment = align_mod.align(shared, [align_mod.as_wire(b) for b in reversed(shared)])

    pairs = {p.golden_id: p.produced_index for p in alignment.matched}
    assert pairs == {"P4a": 1, "P4b": 0}
    assert alignment.ambiguous == []
    assert all(p.fields["expected_or_band"] for p in alignment.matched)


def test_a_band_that_is_close_but_not_equal_is_a_miss_not_a_pass(corpus):
    """The §8.3 phrase table is a fixture, not a judgement: close did not apply the table."""
    entry = corpus.by_id("01-countly")
    if entry is None:
        pytest.skip("01-countly is not in this corpus")
    golden = next(b for b in entry.beliefs
                  if b.expectation.get("type") == "INTERVAL" and b.expectation.get("upper"))
    produced = align_mod.as_wire(golden)
    produced["expectation"] = dict(produced["expectation"])
    upper = dict(produced["expectation"]["upper"])
    upper["value"] = upper["value"] + 1
    produced["expectation"]["upper"] = upper

    alignment = align_mod.align([golden], [produced])

    assert len(alignment.matched) == 1, "a near band is still the same belief"
    assert alignment.matched[0].fields["expected_or_band"] is False, "but the band is a miss"


def test_a_choice_pair_scores_kind_and_unit_as_not_applicable():
    """Judgement call 2: a Choice has no measure, and counting its absence as agreement would
    flatter every Choice belief in the corpus."""
    golden = {"type": "CHOICE", "options": ["yes", "no"], "expected": "yes", "risk": "LOAD_BEARING",
              "mark": "DIRECT", "founder_phrase": None, "heading": "h", "kind": None, "unit": None}

    fields = align_mod.compare(golden, dict(golden))

    assert fields["kind"] is None and fields["unit"] is None
    assert fields["type"] is True and fields["expected_or_band"] is True


def test_founder_phrase_absent_on_both_sides_agrees_and_present_on_one_side_misses():
    """Judgement call 8, and the reason it exists: a CHOICE came from no phrase at all."""
    base = {"type": "CHOICE", "options": ["yes", "no"], "expected": "yes", "risk": "SUPPORTING",
            "mark": "DIRECT", "heading": "h", "kind": None, "unit": None}

    assert align_mod.compare({**base, "founder_phrase": None},
                             {**base, "founder_phrase": None})["founder_phrase"] is True
    assert align_mod.compare({**base, "founder_phrase": "about a week"},
                             {**base, "founder_phrase": None})["founder_phrase"] is False
    assert align_mod.compare({**base, "founder_phrase": "About A Week"},
                             {**base, "founder_phrase": "about a week "})["founder_phrase"] is True
