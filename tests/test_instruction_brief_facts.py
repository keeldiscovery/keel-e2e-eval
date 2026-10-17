"""`instructions/brief_facts.py`: this repository's reading of an entry's `BriefFacts`, and its DRY compare against
keel-cloud's own (spec 040 FR-006; keel-cloud 089 FR-001-FR-006; judgement calls 82, 84).

The reading is pinned on the hand-sized fixtures (stackless), and on keel-cloud's canon corpus at revision 10 it
must agree with `BriefFactsCorpusTest`'s `build/brief-facts/<entry>.json` on every card and the pilot -- 94 checks on
the seven entries, the insight half of `statusWords` the only thing reported.
"""

from __future__ import annotations

import copy
import dataclasses

import pytest

from instructions import brief_facts as bf
from instructions import cloud_corpus as cloud_mod
from instructions import corpus as corpus_mod
from stack.config import load_config
from tests import v9_fixtures as fx


@pytest.fixture(scope="module")
def entry():
    return fx.entry()


@pytest.fixture(scope="module")
def b2b():
    return fx.entry(fx.ENTRY_B2B)


def test_lower_keeps_an_acronym_and_could_phrase_reads_103():
    assert bf.lower("The HR director") == "the HR director"
    assert bf.lower("HR director") == "HR director"
    assert bf.could_phrase("They could connect a tool") == "could connect a tool"
    assert bf.could_phrase("Could connect a tool") == "could connect a tool"
    # keel-cloud 103 (FR-9): every other subject reads "said ...", no "yes:"
    assert bf.could_phrase("Their phone was within reach") == "said their phone was within reach"
    assert bf.could_phrase("The agency could approve it") == "said the agency could approve it"
    assert bf.could_phrase("") == "said yes, easily or with some steps"


def test_one_card_a_calibrated_dimension_in_registry_order(entry, b2b):
    registry = fx.registry()
    cards = bf.cards_for(entry, registry)
    assert [c["key"] for c in cards] == registry.calibrated_keys(False)
    assert len(bf.cards_for(b2b, registry)) == 13
    by_key = {c["key"]: c for c in cards}
    assert by_key["problem.prevalence"]["number"] == "10 of 12"
    assert by_key["problem.prevalence"]["line"] == "had it in the last 7 nights"
    assert by_key["problem.frequency"]["number"] == "2.5 nights out of 7"
    assert by_key["problem.importance"]["line"] == "put it in their top two"
    assert by_key["solution.compatibility"]["line"] == "said they had a phone to hand"
    assert by_key["solution.relative_advantage"]["line"] == "said it would have made their last morning better"
    assert by_key["solution.adoption_friction"]["line"] == "would clip a tag to the key ring"
    assert by_key["commercial.existing_sacrifice"]["line"] == "a month, what it costs them today"
    assert by_key["commercial.commitment"]["line"] == "open to install the app"
    left = by_key["commercial.buyer_payer_alignment"]
    assert left["status"] == "LEFT_OUT" and "number" not in left and left["line"] == bf.LEFT_OUT_LINE
    assert all(c["statusWords"] == bf.VERDICT_WORDS[c["status"]] for c in cards)


def test_purchase_friction_counts_the_supporters(b2b):
    """keel-cloud 103 (FR-9, design §3): the card counts the supporters -- quick or not needed -- not "needed"."""
    card = next(c for c in bf.cards_for(b2b, fx.registry()) if c["key"] == "commercial.purchase_friction")
    standing = b2b.expected["standings"]["commercial.purchase_friction"]
    supporters = bf._option_count(standing, "yes_quick") + bf._option_count(standing, "not_needed")
    assert card["number"] == f"{supporters} of {standing['n']}"
    assert card["line"] == "did not need the office manager's sign-off, or it was quick"


def test_the_pilot_counts_every_finished_interview_on_either_link(entry, b2b):
    pilot = bf.pilot_for(entry)
    assert pilot["finished"] == 12 and pilot["optedIn"] == sum(p.pilot_opt_in for p in entry.people())
    assert pilot["percent"] == round(pilot["optedIn"] * 100 / 12)
    assert [p["link"] for p in pilot["perLink"]] == ["PRIMARY"]
    two = bf.pilot_for(b2b)
    assert [p["words"] for p in two["perLink"]] == ["people who have it", "decision-makers"]
    assert two["finished"] == 17


def _with_verdicts(entry, **verdicts):
    expected = copy.deepcopy(entry.expected)
    for vector, word in verdicts.items():
        expected["vector_verdicts"][vector]["verdict"] = word
    return dataclasses.replace(entry, expected=expected)


@pytest.mark.parametrize("verdicts, label, split, not_tested", [
    ({}, "BUILD_BUT_CHANGE", False, []),
    ({"COMMERCIAL": "HOLDING_UP"}, "BUILD", False, []),
    ({"PROBLEM": "PEOPLE_DISAGREE"}, "NOT_YET", True, []),
    ({"PROBLEM": "NOT_HOLDING_UP"}, "NOT_YET", False, []),
    ({"PROBLEM": "NOT_TESTED"}, "KEEP_INTERVIEWING", False, ["PROBLEM"]),
    ({"COMMERCIAL": "NOT_TESTED"}, "KEEP_INTERVIEWING", False, ["COMMERCIAL"]),
])
def test_the_decision_reads_every_dimension(entry, verdicts, label, split, not_tested):
    """§4.2 as 082 amended it, over all thirteen (D3, 089 FR-006): no deal-breaker filter."""
    shaped = _with_verdicts(entry, **verdicts)
    decision = bf.decision(shaped, fx.registry())
    assert (decision["label"], decision["split"], decision["notTested"]) == (label, split, not_tested)
    assert decision["reason"].startswith("Smallest group: ")


def test_what_broke_is_the_deciding_dimension_of_a_called_failure(entry):
    cards = bf.cards_for(entry, fx.registry())
    broke = bf.broke_of(entry, cards, "COMMERCIAL")
    assert broke["key"] == entry.expected["vector_verdicts"]["COMMERCIAL"]["deciding"]
    assert broke["number"] == next(c for c in cards if c["key"] == broke["key"])["number"]
    assert bf.broke_of(entry, cards, "PROBLEM") is None, "a holding stage broke on nothing"


def test_not_asked_names_left_out_derived_and_b2b_only(entry, b2b):
    keys = [n["key"] for n in bf.not_asked(entry, fx.registry(), "COMMERCIAL")]
    assert keys == ["commercial.ability_to_pay", "commercial.buyer_payer_alignment",
                    "commercial.purchase_friction"]
    assert [n["key"] for n in bf.not_asked(b2b, fx.registry(), "COMMERCIAL")] == \
        ["commercial.buyer_payer_alignment"]


def test_facts_for_is_briefs_shape(entry):
    facts = bf.facts_for(entry, fx.registry())
    assert list(facts) == ["header", "decision", "vectors", "money", "pilot", "cards", "problem", "solution",
                           "commercial", "targets", "keys"]
    assert facts["money"]["currencySymbol"] == "£" and facts["money"]["periodWords"] == "a month"
    assert facts["keys"] == fx.registry().calibrated_keys(False)
    assert all({"key", "name", "status", "n", "notTested"} <= set(t) for t in facts["targets"])


def test_beliefs_carry_no_weight_and_the_lists_their_tested_item(entry):
    beliefs = bf.beliefs_for(entry, fx.registry())
    assert all("weight" not in b for b in beliefs)
    by_key = {b["key"]: b for b in beliefs}
    assert by_key["solution.compatibility"]["founder_phrase"] == "They had a phone to hand"
    assert by_key["problem.prevalence"]["founder_phrase"] == "Most"


# ------------------------------------------------------------------------------------- the compare

def test_the_compare_agrees_with_its_own_reading_and_reports_insights(entry):
    registry = fx.registry()
    cloud = bf.facts_for(entry, registry)
    cloud["cards"][2]["statusWords"] += " · it's the difficulty they'd most like made easier"
    score = bf.compare(entry, registry, cloud)
    assert (score.agreed, score.checks) == (13, 13) and score.correctness == 1.0
    assert [d["field"] for d in score.reported_diffs] == ["statusWords (insight)"]


def test_a_card_that_differs_is_a_mismatch_and_the_pilot_too(entry):
    registry = fx.registry()
    cloud = bf.facts_for(entry, registry)
    cloud["cards"][0]["number"] = "9 of 12"
    cloud["pilot"]["optedIn"] += 1
    score = bf.compare(entry, registry, cloud)
    assert score.checks == 13 and score.agreed == 11
    assert {m["key"] for m in score.mismatches} == {"problem.prevalence", "pilot"}


def test_no_facts_from_keel_cloud_is_unmeasured_never_zero(entry):
    score = bf.compare(entry, fx.registry(), None)
    assert score.measured is False and score.correctness is None and "no brief facts" in score.reason
    assert bf.unmeasured("x", "why").correctness is None


def test_keel_clouds_facts_agree_on_every_card_and_pilot_of_corpus_r10():
    """The DRY compare (spec 040 SC): keel-cloud 089's facts for the seven r10 entries against this reading."""
    keel_cloud = load_config(validate=False).keel_cloud
    if not (keel_cloud / cloud_mod.FACTS_DIR).is_dir():
        pytest.skip("keel-cloud's build/brief-facts/ is absent -- run its BriefFactsCorpusTest "
                    "(`./gradlew test --tests '*BriefFactsCorpusTest'`) to compare")
    fx.canon_entry("01-countly.yaml")
    registry = fx.registry()
    corpus = corpus_mod.load(keel_cloud).bind(registry)
    cloud = cloud_mod.read(keel_cloud, corpus=corpus, registry=registry)
    scores = [bf.compare(e, registry, cloud.facts.get(e.id)) for e in corpus.entries]
    assert sum(s.checks for s in scores) == 94
    assert sum(s.agreed for s in scores) == 94, [m for s in scores for m in s.mismatches]
    assert {d["field"] for s in scores for d in s.reported_diffs} <= {"statusWords (insight)"}
