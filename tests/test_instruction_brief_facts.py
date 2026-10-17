"""`instructions/brief_facts.py`: this repository's reading of an entry's `BriefFacts`, and its DRY compare against
keel-cloud's own (spec 040 FR-006; keel-cloud 089 FR-001-FR-006; judgement calls 82, 84; spec 052: keel-cloud 103's
two card lines and 104's price median, call 119).

The reading is pinned on the hand-sized fixtures (stackless), and on keel-cloud's canon corpus at revision 11 it
must agree with `BriefFactsCorpusTest`'s `build/brief-facts/<entry>.json` on every card, the pilot and the price
median -- 101 checks on the seven entries, the insight half of `statusWords` the only thing reported.
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


def test_lower_keeps_an_acronym_and_could_phrase_reads_103_fr_9():
    """keel-cloud 103 FR-9 (`BriefFacts.couldPhrase`): every subject is kept after "said"; no "said yes:"."""
    assert bf.lower("The HR director") == "the HR director"
    assert bf.lower("HR director") == "HR director"
    assert bf.could_phrase("They could connect a tool") == "could connect a tool"
    assert bf.could_phrase("Could connect a tool") == "could connect a tool"
    assert bf.could_phrase("Their phone was within reach") == "said their phone was within reach"
    assert bf.could_phrase("The agency could approve it on a platform") == \
        "said the agency could approve it on a platform"
    assert bf.could_phrase("") == bf.COULD_PHRASE_BLANK == "said yes, easily or with some steps"


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
    """keel-cloud 103 FR-9 (design §3, overturning 089 call 7): the card counts the supporters -- quick or not needed
    -- so it falls when the bet fails like every other card."""
    card = next(c for c in bf.cards_for(b2b, fx.registry()) if c["key"] == "commercial.purchase_friction")
    standing = b2b.expected["standings"]["commercial.purchase_friction"]
    supporters = bf._option_count(standing, "yes_quick") + bf._option_count(standing, "not_needed")
    assert (supporters, standing["n"]) == (3, 5)
    assert card["number"] == "3 of 5"
    assert card["line"] == "did not need the office manager's sign-off, or it was quick"


# ------------------------------------------------------------------------- the price median (spec 052 FR-1)

def test_the_price_median_on_a_hand_worked_table_three_edges_and_the_exact_half():
    """keel-cloud 104 FR-1 (design §3, D11): the highest edge at least half of n chose at or above. Three edges --
    £10, £20, £50 a month -- chosen at or above by 9, 6 and 3 of 12: £20 is the median at exactly half (6 * 2 == 12)."""
    rows = [{"edge": 10, "edgeSaid": "£10 a month", "chose": 9}, {"edge": 20, "edgeSaid": "£20 a month", "chose": 6},
            {"edge": 50, "edgeSaid": "£50 a month", "chose": 3}]
    assert bf.price_median(rows, 12) == {"edgeSaid": "£20 a month", "chose": 6, "n": 12}
    # one more answer and six is under half: the floor falls to £10
    assert bf.price_median(rows, 13) == {"edgeSaid": "£10 a month", "chose": 9, "n": 13}
    # the highest qualifying edge, not the first: every row reaching half reads the top one
    assert bf.price_median([dict(r, chose=12) for r in rows], 12)["edgeSaid"] == "£50 a month"
    # nobody counted, no table, or no edge reaching half: no median
    assert bf.price_median(rows, 0) is None and bf.price_median(None, 12) is None
    assert bf.price_median([dict(r, chose=1) for r in rows], 12) is None


def test_the_price_table_counts_each_pick_at_or_above_each_edge():
    """`BriefFacts.priceTable`'s chose column over the founder's ladder (a low of £20: bands 10-20, 20-50, 50-100,
    over 100): *under* floors at 0, *would not pay* has no floor and counts in n only."""
    bands = ["under_10", "band_10_20", "band_20_50", "band_20_50", "band_50_100", "over_100", "would_not_pay"]
    rows = bf.price_table(20, bands, currency="GBP", period="month")
    assert [(r["edgeSaid"], r["chose"]) for r in rows] == [("£10 a month", 5), ("£20 a month", 4),
                                                           ("£50 a month", 2), ("£100 a month", 1)]
    assert bf.price_median(rows, len(bands)) == {"edgeSaid": "£20 a month", "chose": 4, "n": 7}
    assert bf.price_table(0.5, bands) is None, "a low off the ladder has no table"


def test_the_entrys_price_median_reads_its_own_price_standing(entry, b2b):
    """The fixture's Price counts: 1 + 4 + 1 + 2 would not pay over n 8 -- £2 a month or more, 5 of 8; the B2B one's
    decision-makers 3 + 1 + 1 over n 5 -- £2, 4 of 5. A left-out Price, or one nobody counted answered, has none."""
    assert bf.price_median_for(entry) == {"edgeSaid": "£2 a month", "chose": 5, "n": 8}
    assert bf.price_median_for(b2b) == {"edgeSaid": "£2 a month", "chose": 4, "n": 5}
    left = copy.deepcopy(entry.expected)
    left["standings"]["commercial.price"] = {"status": "LEFT_OUT"}
    assert bf.price_median_for(dataclasses.replace(entry, expected=left)) is None
    nobody = copy.deepcopy(entry.expected)
    nobody["standings"]["commercial.price"] = {"status": "NOT_ASKED_YET", "n": 0}
    assert bf.price_median_for(dataclasses.replace(entry, expected=nobody)) is None


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


def test_facts_for_is_briefs_shape_without_what_104_deleted(entry):
    """keel-cloud 104: no `sharpest`, `targets` or `keys`; `commercial.priceMedian` beside broke and notAsked."""
    facts = bf.facts_for(entry, fx.registry())
    assert list(facts) == ["header", "decision", "vectors", "money", "pilot", "cards", "problem", "solution",
                           "commercial"]
    assert facts["money"]["currencySymbol"] == "£" and facts["money"]["periodWords"] == "a month"
    assert facts["commercial"]["priceMedian"] == bf.price_median_for(entry)
    assert not hasattr(bf, "targets_for") and not hasattr(bf, "beliefs_for") and not hasattr(bf, "stories_for")


# ------------------------------------------------------------------------------------- the compare

def test_the_compare_agrees_with_its_own_reading_and_reports_insights(entry):
    registry = fx.registry()
    cloud = bf.facts_for(entry, registry)
    cloud["cards"][2]["statusWords"] += " · it's the difficulty they'd most like made easier"
    score = bf.compare(entry, registry, cloud)
    assert (score.agreed, score.checks) == (14, 14) and score.correctness == 1.0
    assert [d["field"] for d in score.reported_diffs] == ["statusWords (insight)"]


def test_a_card_that_differs_is_a_mismatch_and_the_pilot_too(entry):
    registry = fx.registry()
    cloud = bf.facts_for(entry, registry)
    cloud["cards"][0]["number"] = "9 of 12"
    cloud["pilot"]["optedIn"] += 1
    score = bf.compare(entry, registry, cloud)
    assert score.checks == 14 and score.agreed == 12
    assert {m["key"] for m in score.mismatches} == {"problem.prevalence", "pilot"}


@pytest.mark.parametrize("fault", [
    lambda m: m.update(chose=m["chose"] + 1),                 # a count off by one
    lambda m: m.update(edgeSaid="£5 a month"),                # the next edge up: the half rule read as "more than"
    lambda m: m.clear() or None,                              # an empty object where the median is
])
def test_a_price_median_that_differs_is_a_mismatch(entry, fault):
    """Seeded faults on the price median: each is one mismatch, keyed `priceMedian`."""
    registry = fx.registry()
    cloud = bf.facts_for(entry, registry)
    fault(cloud["commercial"]["priceMedian"])
    score = bf.compare(entry, registry, cloud)
    assert [m["key"] for m in score.mismatches] == ["priceMedian"] and score.agreed == score.checks - 1


def test_a_price_median_keel_cloud_leaves_null_is_a_mismatch_when_the_entry_has_one(entry):
    registry = fx.registry()
    cloud = bf.facts_for(entry, registry)
    cloud["commercial"]["priceMedian"] = None
    assert [m["key"] for m in bf.compare(entry, registry, cloud).mismatches] == ["priceMedian"]


def test_no_facts_from_keel_cloud_is_unmeasured_never_zero(entry):
    score = bf.compare(entry, fx.registry(), None)
    assert score.measured is False and score.correctness is None and "no brief facts" in score.reason
    assert bf.unmeasured("x", "why").correctness is None


def cloud_facts_at_104():
    """keel-cloud's `build/brief-facts/` read whole -- or a skip naming why: absent, or written before keel-cloud 104
    (no `commercial.priceMedian` key), which a fresh `BriefFactsCorpusTest` run rewrites."""
    keel_cloud = load_config(validate=False).keel_cloud
    if not (keel_cloud / cloud_mod.FACTS_DIR).is_dir():
        pytest.skip("keel-cloud's build/brief-facts/ is absent -- run its BriefFactsCorpusTest "
                    "(`./gradlew test --tests '*BriefFactsCorpusTest'`) to compare")
    fx.canon_entry("01-countly.yaml")
    registry = fx.registry()
    corpus = corpus_mod.load(keel_cloud).bind(registry)
    cloud = cloud_mod.read(keel_cloud, corpus=corpus, registry=registry)
    if any("priceMedian" not in ((f or {}).get("commercial") or {}) for f in cloud.facts.values()):
        pytest.skip("keel-cloud's build/brief-facts/ predates keel-cloud 104 (no commercial.priceMedian) -- rerun "
                    "its BriefFactsCorpusTest to compare")
    return registry, corpus, cloud


def test_keel_clouds_facts_agree_on_every_card_pilot_and_price_median_of_corpus_r11():
    """The DRY compare (spec 040 SC; spec 052): keel-cloud 104's facts for the seven r11 entries against this reading
    -- 87 cards, 7 pilots, 7 price medians (101 of 101 at keel-cloud-docs 9a033fe)."""
    registry, corpus, cloud = cloud_facts_at_104()
    scores = [bf.compare(e, registry, cloud.facts.get(e.id)) for e in corpus.entries]
    assert sum(s.checks for s in scores) == 101
    assert sum(s.agreed for s in scores) == 101, [m for s in scores for m in s.mismatches]
    assert {d["field"] for s in scores for d in s.reported_diffs} <= {"statusWords (insight)"}
