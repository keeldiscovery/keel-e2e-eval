"""Corpus revision 7, the real seven files, through the one reader (spec 033 FR-002, T004; revision 6's by spec 032;
revision 5's by spec 031, revision 4's by spec 030, first written for revision 3 by spec 029 T047).

**One reader, one hash, one place** (spec 010's rule; judgement call 49): the files are read
through `instructions.corpus.load` exactly as a run reads them -- keel-cloud's canon, and nowhere
else; the fixture fallback of 2026-10-07 is gone with its directory. Nothing here is a copy of the
corpus. What is held is the shape every entry must have and the facts keel-cloud 077 pins
(`GoldenCorpusTest` on r7): the calibrated set per persona (twelve keys on 01-04, thirteen on
05-07), the plan per link, the status totals across the seven, every founder cost on the five
periods with the price on the cost's, Ability to pay recomputed, every Existing sacrifice pick with
its recall period, Lullaby's standings and verdicts, the gate-No and chipped people, and the B2B
entries' decision-makers story-less, ANCHORED and on `commercial.*` only.

When `stack.toml`'s keel-cloud is not at revision 7 every test here skips **by name**, with the
reason -- never a fixture copy, which would be a second frozen corpus in all but name.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from instructions import corpus as corpus_mod
from instructions import registry as registry_mod
from stack.config import load_config
from tests import v9_fixtures as fx

ENTRIES = ("01-countly", "02-compliancelog", "03-lullaby", "04-linerly", "05-paidly",
           "06-repeatline", "07-mulchrun")
B2B = ("05-paidly", "06-repeatline", "07-mulchrun")


@pytest.fixture(scope="module")
def corpus():
    keel_cloud = load_config(validate=False).keel_cloud
    for name in ENTRIES:
        fx.canon_entry(f"{name}.yaml")                 # skips, by name, when canon is not r7
    return corpus_mod.load(keel_cloud, registry=fx.registry())


def test_the_seven_entries_are_all_at_revision_seven(corpus):
    assert [e.id for e in corpus.entries] == list(ENTRIES)
    for entry in corpus.entries:
        assert entry.revision == 7, entry.id
    assert Path(corpus.directory) == fx.canon_dir()


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_every_entry_calibrates_its_personas_set_and_plans_per_link(corpus, entry_id):
    """Calls 47, 59: twelve keys on a B2C persona (Ability to pay derived, calibrated), thirteen on a B2B
    one; PRIMARY asks 4 / 3 / 4 on B2C, and part 3 of a B2B study is the COMMERCIAL_B2B link's six
    (decision 26) -- four on Mulch Run, whose founder left Price out, and so Ability to pay."""
    entry = corpus.by_id(entry_id)
    registry = fx.registry()
    b2b = entry_id in B2B
    assert entry.b2b() is b2b
    calibrated = registry.calibrated_keys(b2b)
    assert len(calibrated) == (13 if b2b else 12)
    assert set(entry.founder_calibration) == set(calibrated) == set(entry.calibrated_keys())
    assert set(entry.expected["standings"]) == set(calibrated)
    part3 = (4 if entry_id == "07-mulchrun" else 6) if b2b else 4
    assert {part: len(keys) for part, keys in entry.plan().items()} == {1: 4, 2: 3, 3: part3}
    assert entry.link_of(3) == (registry_mod.LINK_B2B if b2b else registry_mod.LINK_PRIMARY)
    assert set(entry.expected["vector_verdicts"]) == {"PROBLEM", "SOLUTION", "COMMERCIAL"}
    for vector, verdict in entry.expected["vector_verdicts"].items():
        assert verdict["deciding"] in registry_mod.DEAL_BREAKERS[vector], (entry_id, vector)
    for key, row in entry.founder_calibration.items():
        assert row.get("belief_sentence"), f"{entry_id} {key}: the belief sentence"
    assert entry.interpretations.get("problem"), f"{entry_id}: the problem sentence"
    assert entry.respondent_questions["problem.importance"].get("own_item"), "D3's own item"
    assert entry.vocabulary(), "no_leak needs a list to sweep with"


def test_the_status_totals_across_the_seven_are_keel_cloud_074s(corpus):
    """The six status words only, over 4 x 12 + 3 x 13 rows: the cost-first readings moved Existing sacrifice
    (two too few to call) and added Ability to pay to the four consumer entries."""
    totals = {}
    for entry in corpus.entries:
        for row in entry.expected["standings"].values():
            assert row["status"] in corpus_mod.STATUSES
            totals[row["status"]] = totals.get(row["status"], 0) + 1
    assert totals == {"HOLDING_UP": 54, "NOT_HOLDING_UP": 14, "PEOPLE_DISAGREE": 15,
                      "TOO_FEW_TO_CALL": 2, "LEFT_OUT": 2}
    assert sum(totals.values()) == 4 * 12 + 3 * 13


PRICES = {"01-countly": (30, 50, "month"), "02-compliancelog": (250, 350, "month"),
          "03-lullaby": (5, 12, "month"), "04-linerly": (30, 45, "year"),
          "05-paidly": (60, 100, "month"), "06-repeatline": (120, 180, "month"),
          "07-mulchrun": None}


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_every_founder_price_is_on_the_ladder_and_its_row_is_the_ladders(corpus, entry_id):
    """Calls 51, 60 (keel-cloud 073 D-10, 074 D-10): each entry's own price, in its market's currency,
    over the cost's period; Mulch Run's per-yard price is on no period, so Price is left out there and
    is never planned."""
    entry = corpus.by_id(entry_id)
    price = entry.price()
    if PRICES[entry_id] is None:
        assert price is None and entry.unsure("commercial.price")
        assert "commercial.price" not in entry.plan()[3]
        assert entry.expected["standings"]["commercial.price"]["status"] == "LEFT_OUT"
        return
    assert (price["low"], price["high"], price["period"]) == PRICES[entry_id]
    assert price["currency"] == corpus_mod.MARKET_CURRENCY[entry.market["country"]]
    assert price["period"] == entry.cost()["period"], "the price takes the cost's period"
    assert entry.respondent_questions["commercial.price"]["codes"] == \
        corpus_mod.price_ladder_codes(price["low"])
    assert "commercial.price" in entry.plan()[3]


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_existing_sacrifice_is_one_total_over_a_recall_period(corpus, entry_id):
    """Calls 51, 60, 68: the plan row is `cost_total` with no codes and no units, the founder entry no kinds,
    every pick one total -- `{mode, value, currency, period}`, `{nothing: true, ...}` or a chip -- with the
    recall period it was asked over, and the standing no option counts."""
    entry = corpus.by_id(entry_id)
    row = entry.respondent_questions["commercial.existing_sacrifice"]
    assert row["control"] == registry_mod.COST_TOTAL_CONTROL
    assert "codes" not in row and "units" not in row
    founder = entry.founder_calibration["commercial.existing_sacrifice"]
    assert "labels" not in founder and "units" not in founder
    assert "optionCounts" not in entry.expected["standings"]["commercial.existing_sacrifice"]
    for person in entry.people():
        pick = person.picks.get("commercial.existing_sacrifice")
        if pick is None:
            continue
        assert set(pick) <= {"mode", "value", "nothing", "currency", "period", "rough"}, (entry_id, person.person)
        assert pick.get("nothing") is True or pick["mode"] in ("AMOUNT", "HOURS"), (entry_id, person.person)
        assert pick["period"] in corpus_mod.RECALL_PERIODS, (entry_id, person.person)


COSTS = {"01-countly": ("AMOUNT", 20, 60, "month"), "02-compliancelog": ("AMOUNT", 300, 900, "month"),
         "03-lullaby": ("AMOUNT", 10, 30, "month"), "04-linerly": ("AMOUNT", 30, 60, "year"),
         "05-paidly": ("AMOUNT", 100, 300, "month"), "06-repeatline": ("HOURS", 40, 80, "month"),
         "07-mulchrun": ("AMOUNT", 100, 200, "month")}
ABILITY = {"01-countly": (50, 250, "some_from_spend"), "02-compliancelog": (28, 117, "some_from_spend"),
           "03-lullaby": (17, 120, "some_from_spend"), "04-linerly": (50, 150, "some_from_spend"),
           "05-paidly": (20, 100, "mostly_from_spend"), "06-repeatline": (8, 23, "small_share"),
           "07-mulchrun": None}


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_every_founder_cost_is_an_estimate_and_ability_to_pay_is_derived_from_it(corpus, entry_id):
    """Call 60 (keel-cloud 074 D-10, D-13): the cost on the five periods (HOURS at a rate on Repeatline only),
    the B2B entries' `hourly_rate`, Ability to pay recomputed from the cost and the price -- Mulch Run's left
    out with its price."""
    entry = corpus.by_id(entry_id)
    cost = entry.cost()
    mode, low, high, period = COSTS[entry_id]
    assert (cost["mode"], cost["low"], cost["high"], cost["period"]) == (mode, low, high, period)
    assert ("rate" in cost) is (mode == "HOURS")
    assert (entry.hourly_rate() is not None) is entry.b2b()
    ability = entry.founder_calibration["commercial.ability_to_pay"]
    if ABILITY[entry_id] is None:
        assert ability.get("unsure") is True
        assert entry.expected["standings"]["commercial.ability_to_pay"]["status"] == "LEFT_OUT"
        assert "commercial.ability_to_pay" not in entry.plan()[3]
        return
    low_r, high_r, band = ABILITY[entry_id]
    assert ability["answer"] == {"ratio_low": low_r, "ratio_high": high_r, "band": band}
    assert corpus_mod.derive_ability(cost, entry.price()) == ability["answer"]
    assert (("commercial.ability_to_pay" in entry.plan()[3])) is entry.b2b()


@pytest.mark.parametrize("entry_id, time_only", [("01-countly", 4), ("02-compliancelog", 7)])
def test_the_b2c_people_who_gave_only_time_are_reported_apart(corpus, entry_id, time_only):
    """Call 65 (keel-cloud 074 D-12): Countly's four managers and ComplianceLog's seven lose only time -- the
    standing records the count and the median hours a month, and counts them in no money reading."""
    standing = corpus.by_id(entry_id).expected["standings"]["commercial.existing_sacrifice"]
    assert standing["time_only"] == time_only and standing["time_only_hours"] > 0
    assert standing["status"] == "TOO_FEW_TO_CALL"


def test_the_vector_verdicts_are_the_ones_golden_corpus_test_pins(corpus):
    verdicts = {e.id: {v: (row["verdict"], row["deciding"])
                       for v, row in e.expected["vector_verdicts"].items()}
                for e in corpus.entries}
    assert verdicts["02-compliancelog"]["PROBLEM"] == ("NOT_HOLDING_UP", "problem.importance")
    assert verdicts["04-linerly"]["PROBLEM"] == ("NOT_HOLDING_UP", "problem.importance")
    assert verdicts["06-repeatline"]["PROBLEM"] == ("NOT_HOLDING_UP", "problem.importance")
    assert verdicts["03-lullaby"]["PROBLEM"] == ("NOT_HOLDING_UP",
                                                 "problem.current_solution_satisfaction")
    assert verdicts["05-paidly"]["PROBLEM"] == ("HOLDING_UP", "problem.prevalence")
    assert verdicts["05-paidly"]["SOLUTION"] == ("HOLDING_UP", "solution.compatibility")


def test_lullaby_reproduces_the_registrys_worked_example(corpus):
    """The registry's `checks.lullaby_statuses`: 6 / 3 / 3 (Existing sacrifice and Price are the splits,
    Ability to pay holds), Prevalence holding with its drift."""
    lullaby = corpus.by_id("03-lullaby")
    standings = lullaby.expected["standings"]
    expected = {
        "problem.prevalence": ("HOLDING_UP", "above"), "problem.frequency": ("HOLDING_UP", "none"),
        "problem.importance": ("HOLDING_UP", "none"),
        "problem.current_solution_satisfaction": ("NOT_HOLDING_UP", "above"),
        "solution.compatibility": ("NOT_HOLDING_UP", "above"),
        "solution.adoption_friction": ("PEOPLE_DISAGREE", "below"),
        "commercial.commitment": ("NOT_HOLDING_UP", "none"),
        "commercial.price": ("PEOPLE_DISAGREE", "below"),
        "commercial.existing_sacrifice": ("PEOPLE_DISAGREE", "below"),
        "commercial.ability_to_pay": ("HOLDING_UP", "none"),
    }
    for key, (status, drift) in expected.items():
        assert (standings[key]["status"], standings[key].get("drift")) == (status, drift), key
    assert (standings["problem.prevalence"]["yes"], standings["problem.prevalence"]["n"]) == (10, 12)
    assert standings["problem.importance"]["share"] == 0.38
    totals = {}
    for row in standings.values():
        totals[row["status"]] = totals.get(row["status"], 0) + 1
    assert totals == {"HOLDING_UP": 6, "NOT_HOLDING_UP": 3, "PEOPLE_DISAGREE": 3}
    assert lullaby.expected["vector_verdicts"] == {
        "PROBLEM": {"verdict": "NOT_HOLDING_UP",
                    "deciding": "problem.current_solution_satisfaction"},
        "SOLUTION": {"verdict": "NOT_HOLDING_UP", "deciding": "solution.compatibility"},
        "COMMERCIAL": {"verdict": "NOT_HOLDING_UP", "deciding": "commercial.commitment"}}


def test_lullabys_twelve_people_two_at_the_gate_and_one_chip(corpus):
    lullaby = corpus.by_id("03-lullaby")
    assert len(lullaby.people()) == 12 and len(lullaby.readable()) == 9
    for name in ("Hugo Laurent", "Leo Martins"):
        person = lullaby.person(name)
        assert (person.recency, person.story, person.picks) == ("no", None, {}), name
    jonas = lullaby.person("Jonas Weber")
    assert (jonas.chip, jonas.anchoring) == ("cant_recall", "GUESSED")
    assert "Jonas Weber" not in [p.person for p in lullaby.readable()]


@pytest.mark.parametrize("entry_id, deciders", [("05-paidly", 8), ("06-repeatline", 7),
                                                ("07-mulchrun", 7)])
def test_a_b2b_entrys_decision_makers_answer_commercial_only_on_their_own_link(
        corpus, entry_id, deciders):
    """FR-010, decision 26, keel-cloud 075: the decision-maker answers part 3 on COMMERCIAL_B2B, story-less
    and ANCHORED by rule; the primary people answer no commercial item at all."""
    entry = corpus.by_id(entry_id)
    assert entry.role(entry.decision_maker_role())["roleType"] == "BUYER"
    assert len(entry.deciders()) == deciders
    assert all(p.recency is None and p.picks and all(k.startswith("commercial.") for k in p.picks)
               for p in entry.deciders())
    assert not any(k.startswith("commercial.") for p in entry.gate_yes() for k in p.picks)
    assert all(p.story is None and p.chip is None and p.anchoring == "ANCHORED"
               for p in entry.deciders())
    assert set(registry_mod.B2B_ONLY) <= set(entry.plan()[3])


def test_the_corpus_wide_interpret_denominator_is_counted_not_estimated(corpus):
    """106 people, less every gate-No, every chipped story and every decision-maker (who is never
    read) -- the number marks.py's v11 header records (r6 moved no person)."""
    assert sum(len(e.people()) for e in corpus.entries) == 106
    assert sum(len(e.readable()) for e in corpus.entries) == 65


def test_the_fixture_fallback_is_gone():
    """Call 49: no `tests/fixtures/corpus-r3/`, and no `FIXTURE_DIR` to fall back to."""
    assert not (Path(__file__).parent / "fixtures" / "corpus-r3").exists()
    assert not hasattr(corpus_mod, "FIXTURE_DIR")


@pytest.mark.parametrize("revision, rubric", [(6, "MARKS_VERSION 12"), (5, "MARKS_VERSION 11"),
                                              (4, "MARKS_VERSION 10"), (3, "MARKS_VERSION 9")])
def test_a_corpus_directory_holding_an_older_file_refuses_by_name(tmp_path, revision, rubric):
    """Calls 49, 51, 60, 68: one r6 (or r5, r4, r3) file in keel-cloud's corpus refuses the whole load, naming the
    entry and the rubric that read its revision -- never a fallback."""
    keel_cloud = tmp_path / "keel-cloud"
    canon = corpus_mod.corpus_dir(keel_cloud)
    canon.mkdir(parents=True)
    raw = fx.raw_entry()
    fx.write_entry(canon, raw, "09-fixture-r7.yaml")
    fx.write_entry(canon, dict(raw, id="08-old", revision=revision), "08-old.yaml")
    with pytest.raises(corpus_mod.CorpusError) as refusal:
        corpus_mod.load(keel_cloud, registry=fx.registry())
    assert str(refusal.value).startswith(f"08-old: revision is {revision}")
    assert rubric in str(refusal.value)


def test_a_missing_corpus_directory_refuses_by_name(tmp_path):
    with pytest.raises(corpus_mod.CorpusError) as refusal:
        corpus_mod.load(tmp_path / "keel-cloud", registry=fx.registry())
    assert "no corpus at" in str(refusal.value)


def test_every_model_written_set_carries_the_labels_the_founder_saw(corpus):
    """keel-cloud 058 (afe36fd): production sends the founder's LABELS as `founder_options`, and
    its contract tool refuses a batch that sends codes. One label per founder option, in order."""
    registry = fx.registry()
    for entry in corpus.entries:
        for part in (1, 2, 3):
            for key in entry.plan(registry)[part]:
                dimension = registry.by_key(key)
                if dimension.fixed_codes is not None or dimension.founder_numeric \
                        or dimension.founder_price or dimension.founder_cost \
                        or dimension.derived:   # Ability to pay: fixed rungs; call 67: no kinds of cost
                    continue
                labels = entry.founder_labels(key)
                assert labels and list(labels) == entry.founder_option_codes(key), (entry.id, key)


def test_the_corpus_reads_the_same_through_the_exported_registry(corpus):
    """The export's own registry (`dimension-registry.json`) binds the seven as the slice does."""
    path = Path(load_config(validate=False).keel_cloud) / "src" / "main" / "resources" / "keel" / \
        "dimension-registry.json"
    if not path.is_file():
        pytest.skip(f"no exported registry at {path}")
    exported = registry_mod.load(path)
    for entry in corpus.entries:
        corpus_mod.load_file(entry.path, registry=exported)
    assert yaml.safe_load(Path(corpus.entries[0].path).read_text())["revision"] == 7


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_every_entry_records_the_two_golden_names(corpus, entry_id):
    """Call 55, amended (keel-cloud 073 `ed581f8`, kept in r6): W3 / W8 hold to the corpus's own names -- the
    idea's in at most five plain words, the offer's in at most six -- on every entry."""
    from instructions import context as context_mod                         # noqa: PLC0415
    entry = corpus.by_id(entry_id)
    short, offer = context_mod.short_name_of(entry), context_mod.offer_name_of(entry)
    assert short and len(short.split()) <= 5, (entry_id, short)
    assert offer and len(offer.split()) <= 6, (entry_id, offer)
    if entry_id == "03-lullaby":
        assert (short, offer) == ("a suggested reason for crying", "something that helps at night")
