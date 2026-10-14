"""Corpus revision 10, the real seven files, through the one reader (spec 040 FR-002, T004, judgement call 78;
revision 9's by spec 038, first written for revision 3 by spec 029 T047).

**One reader, one hash, one place** (spec 010's rule; judgement call 49): the files are read through
`instructions.corpus.load` exactly as a run reads them -- keel-cloud's canon, and nowhere else. Nothing here is a copy
of the corpus. What is held is the shape every entry must have at revision 10 and the facts keel-cloud 087 pins
(`GoldenCorpusTest` on r10, `check_corpus_r10.py`): the calibrated set per persona, the plan per link, the 11 vector
verdicts and 21 standings 087's table moved, the two re-windowed entries (D13), every entry's occasion, every founder
list against the registry's `saves`, every pick's shape, the founder cost and the derived Ability to pay, the price
ladder, the recall periods, and the B2B entries' decision-makers.

When `stack.toml`'s keel-cloud is not at revision 10 every test here skips **by name**, with the reason -- never a
fixture copy, which would be a second frozen corpus in all but name.
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
        fx.canon_entry(f"{name}.yaml")                 # skips, by name, when canon is not r10
    return corpus_mod.load(keel_cloud, registry=fx.registry())


def test_the_seven_entries_are_all_at_revision_ten(corpus):
    assert [e.id for e in corpus.entries] == list(ENTRIES)
    for entry in corpus.entries:
        assert entry.revision == 10, entry.id
    assert Path(corpus.directory) == fx.canon_dir()


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_every_entry_calibrates_its_personas_set_and_plans_per_link(corpus, entry_id):
    """Calls 47, 59: twelve keys on a B2C persona, thirteen on a B2B one; PRIMARY asks 4 / 3 / 4 on B2C, and part 3
    of a B2B study is the COMMERCIAL_B2B link's six -- four on Mulch Run, whose founder left Price out, and so
    Ability to pay. D3: a vector's deciding dimension is any of its own."""
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
        assert verdict["deciding"] in [d.key for d in registry.calibrated_slice(vector, b2b)], (entry_id, vector)
    for key, row in entry.founder_calibration.items():
        assert row.get("belief_sentence"), f"{entry_id} {key}: the belief sentence"
    assert entry.interpretations.get("problem"), f"{entry_id}: the problem sentence"
    assert entry.respondent_questions["problem.importance"]["own_item"] == \
        entry.tested("problem.importance")["code"], "the own item is the founder's item 0"
    assert entry.vocabulary(), "no_leak needs a list to sweep with"


#: keel-cloud 087's *Vector verdicts (11 moved)*, and the ten that did not.
VERDICTS = {
    "01-countly": {"PROBLEM": ("PEOPLE_DISAGREE", "problem.current_solution_satisfaction"),
                   "SOLUTION": ("HOLDING_UP", "solution.compatibility"),
                   "COMMERCIAL": ("TOO_FEW_TO_CALL", "commercial.existing_sacrifice")},
    "02-compliancelog": {"PROBLEM": ("HOLDING_UP", "problem.prevalence"),
                         "SOLUTION": ("PEOPLE_DISAGREE", "solution.relative_advantage"),
                         "COMMERCIAL": ("NOT_HOLDING_UP", "commercial.price")},
    "03-lullaby": {"PROBLEM": ("NOT_HOLDING_UP", "problem.current_solution_satisfaction"),
                   "SOLUTION": ("PEOPLE_DISAGREE", "solution.adoption_friction"),
                   "COMMERCIAL": ("PEOPLE_DISAGREE", "commercial.existing_sacrifice")},
    "04-linerly": {"PROBLEM": ("PEOPLE_DISAGREE", "problem.importance"),
                   "SOLUTION": ("NOT_HOLDING_UP", "solution.relative_advantage"),
                   "COMMERCIAL": ("HOLDING_UP", "commercial.existing_sacrifice")},
    "05-paidly": {"PROBLEM": ("HOLDING_UP", "problem.prevalence"),
                  "SOLUTION": ("HOLDING_UP", "solution.compatibility"),
                  "COMMERCIAL": ("NOT_HOLDING_UP", "commercial.existing_sacrifice")},
    "06-repeatline": {"PROBLEM": ("HOLDING_UP", "problem.prevalence"),
                      "SOLUTION": ("NOT_HOLDING_UP", "solution.relative_advantage"),
                      "COMMERCIAL": ("PEOPLE_DISAGREE", "commercial.commitment")},
    "07-mulchrun": {"PROBLEM": ("NOT_HOLDING_UP", "problem.prevalence"),
                    "SOLUTION": ("HOLDING_UP", "solution.compatibility"),
                    "COMMERCIAL": ("PEOPLE_DISAGREE", "commercial.purchase_friction")},
}

MOVED = [("01-countly", "PROBLEM"), ("01-countly", "SOLUTION"), ("02-compliancelog", "PROBLEM"),
         ("02-compliancelog", "COMMERCIAL"), ("03-lullaby", "SOLUTION"), ("03-lullaby", "COMMERCIAL"),
         ("04-linerly", "PROBLEM"), ("06-repeatline", "PROBLEM"), ("06-repeatline", "COMMERCIAL"),
         ("07-mulchrun", "SOLUTION"), ("07-mulchrun", "COMMERCIAL")]


def test_the_vector_verdicts_are_the_ones_golden_corpus_test_pins(corpus):
    verdicts = {e.id: {v: (row["verdict"], row["deciding"]) for v, row in e.expected["vector_verdicts"].items()}
                for e in corpus.entries}
    assert verdicts == VERDICTS
    assert len(MOVED) == 11 and len(set(MOVED)) == 11


#: keel-cloud 087's *Standings (21 moved)*: (status, drift) at revision 10.
MOVED_STANDINGS = {
    ("01-countly", "problem.importance"): ("HOLDING_UP", "stronger"),
    ("01-countly", "problem.current_solution_satisfaction"): ("PEOPLE_DISAGREE", "both"),
    ("01-countly", "solution.compatibility"): ("HOLDING_UP", "none"),
    ("02-compliancelog", "problem.importance"): ("HOLDING_UP", "none"),
    ("02-compliancelog", "commercial.buyer_payer_alignment"): ("PEOPLE_DISAGREE", "both"),
    ("02-compliancelog", "commercial.commitment"): ("HOLDING_UP", "none"),
    ("03-lullaby", "problem.importance"): ("PEOPLE_DISAGREE", "both"),
    ("03-lullaby", "solution.compatibility"): ("HOLDING_UP", "none"),
    ("03-lullaby", "commercial.commitment"): ("HOLDING_UP", "none"),
    ("04-linerly", "problem.importance"): ("PEOPLE_DISAGREE", "both"),
    ("04-linerly", "problem.current_solution_satisfaction"): ("PEOPLE_DISAGREE", "both"),
    ("05-paidly", "commercial.buyer_payer_alignment"): ("PEOPLE_DISAGREE", "both"),
    ("05-paidly", "commercial.purchase_friction"): ("PEOPLE_DISAGREE", "both"),
    ("05-paidly", "commercial.commitment"): ("HOLDING_UP", "none"),
    ("06-repeatline", "problem.importance"): ("HOLDING_UP", "none"),
    ("06-repeatline", "commercial.purchase_friction"): ("HOLDING_UP", "none"),
    ("06-repeatline", "commercial.commitment"): ("PEOPLE_DISAGREE", "both"),
    ("07-mulchrun", "problem.importance"): ("PEOPLE_DISAGREE", "both"),
    ("07-mulchrun", "problem.current_solution_satisfaction"): ("PEOPLE_DISAGREE", "both"),
    ("07-mulchrun", "solution.compatibility"): ("HOLDING_UP", "none"),
    ("07-mulchrun", "commercial.purchase_friction"): ("PEOPLE_DISAGREE", "both"),
}


def test_the_twenty_one_moved_standings_are_087s(corpus):
    assert len(MOVED_STANDINGS) == 21
    for (entry_id, key), want in MOVED_STANDINGS.items():
        row = corpus.by_id(entry_id).expected["standings"][key]
        assert (row["status"], row.get("drift")) == want, (entry_id, key)


def test_the_status_totals_across_the_seven(corpus):
    """The six status words only, over 4 x 12 + 3 x 13 rows; `above` / `below` are gone with `choice_majority`."""
    totals = {}
    for entry in corpus.entries:
        for row in entry.expected["standings"].values():
            assert row["status"] in corpus_mod.STATUSES
            assert row.get("drift") in corpus_mod.DRIFTS + (None,)
            totals[row["status"]] = totals.get(row["status"], 0) + 1
    assert totals == {"HOLDING_UP": 58, "NOT_HOLDING_UP": 7, "PEOPLE_DISAGREE": 18,
                      "TOO_FEW_TO_CALL": 2, "LEFT_OUT": 2}
    assert sum(totals.values()) == 4 * 12 + 3 * 13


WINDOWS = {"01-countly": (4, "WEEKS", "delivery"), "02-compliancelog": (3, "MONTHS", "compliance report"),
           "03-lullaby": (7, "NIGHTS", "night"), "04-linerly": (12, "MONTHS", "ride"),
           "05-paidly": (3, "MONTHS", "invoice"), "06-repeatline": (7, "DAYS", "shift on the phones"),
           "07-mulchrun": (2, "WEEKS", "yard run")}


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_every_window_counts_at_least_two_and_every_entry_records_its_occasion(corpus, entry_id):
    """D13 (rule W): no one-unit window -- 01-countly's {1, MONTHS} became {4, WEEKS}, 06-repeatline's {1, SHIFTS}
    {7, DAYS} (087 judgement call 9) -- and every entry records `context.occasion`; Frequency's picks stay on the
    founder's own axis."""
    entry = corpus.by_id(entry_id)
    count, unit, occasion = WINDOWS[entry_id]
    assert (entry.window().count, entry.window().unit) == (count, unit)
    assert entry.window().count >= registry_mod.WINDOW_MIN_COUNT
    assert entry.occasion() == occasion
    if entry_id == "01-countly":
        assert entry.founder_calibration["problem.frequency"]["answer"] == \
            {"lower": 1, "upper": 3, "unit": "weeks out of 4"}
        assert entry.person("Tom Okafor").picks["problem.frequency"] == 4, "clamped from 5 (087)"
    if entry_id == "06-repeatline":
        assert entry.founder_calibration["problem.frequency"]["answer"] == \
            {"lower": 4, "upper": 5, "unit": "days out of 7"}


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_every_founder_list_obeys_the_registrys_saves(corpus, entry_id):
    """087 FR-007 (rule L): each list within its `saves` -- counts, words, the picked index where the registry
    picks, the phrase, the faces, Buyer and payer's fixed `Nobody else` -- and no `labels` / `belief_phrase` on the
    seven reshaped dimensions."""
    entry = corpus.by_id(entry_id)
    registry = fx.registry()
    for dimension in registry.calibrated(entry.b2b()):
        if not dimension.founder_list or entry.unsure(dimension.key):
            continue
        saves = dimension.saves
        saved = entry.founder_list(dimension.key)
        assert saves["min_items"] <= len(saved["items"]) <= saves["max_items"], (entry_id, dimension.key)
        for item in saved["items"]:
            assert registry_mod.words(item["label"]) <= saves["max_words"], (entry_id, item)
            assert bool(item.get("asked")) is bool(saves.get("asked")), (entry_id, item)
        assert (saved["picked"] is not None) is bool(saves["picked"]), (entry_id, dimension.key)
        assert bool(saved["phrase"]) is bool(saves.get("phrase")), (entry_id, dimension.key)
        if saves.get("fixed_first"):
            assert saved["items"][0] == {"code": "nobody_else", "label": "Nobody else"}
        calibration = entry.founder_calibration[dimension.key]
        assert "labels" not in calibration
        if dimension.key in corpus_mod.RESHAPED:
            assert "belief_phrase" not in calibration, (entry_id, dimension.key)


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_every_row_is_the_registrys_and_every_pick_its_rows(corpus, entry_id):
    """Rules R and A: a row's control and one escape the registry's, a fixed-answer row the registry's codes; a
    pick a code of its row, Importance two distinct codes, an escape exactly the row's -- never on Commitment --
    and no guessed flag (D8)."""
    entry = corpus.by_id(entry_id)
    registry = fx.registry()
    for key, row in entry.respondent_questions.items():
        dimension = registry.by_key(key)
        assert row["control"] == dimension.respondent_control, (entry_id, key)
        assert row.get("escape") == (dimension.escape or {}).get("code"), (entry_id, key)
        if dimension.fixed_answers:
            assert row["codes"] == dimension.fixed_answer_codes, (entry_id, key)
    for person in entry.people():
        for key, pick in person.picks.items():
            row = entry.respondent_questions[key]
            assert not (isinstance(pick, dict) and "rough" in pick), (entry_id, person.person, key)
            if isinstance(pick, dict) and "chip" in pick:
                assert pick["chip"] == row.get("escape") and key != "commercial.commitment"
            elif row["control"] == "pick_two":
                assert len(pick) == 2 and len(set(pick)) == 2 and set(pick) <= set(row["codes"])
            elif row["control"] in ("fixed_four", "fixed_three", "single_choice_5", "price_ladder"):
                assert pick in row["codes"], (entry_id, person.person, key, pick)


PRICES = {"01-countly": (30, 50, "month"), "02-compliancelog": (250, 350, "month"),
          "03-lullaby": (5, 12, "month"), "04-linerly": (30, 45, "year"),
          "05-paidly": (60, 100, "month"), "06-repeatline": (120, 180, "month"),
          "07-mulchrun": None}


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_every_founder_price_is_on_the_ladder_and_its_row_is_the_ladders(corpus, entry_id):
    """Calls 51, 60: each entry's own price, in its market's currency, over the cost's period; Mulch Run's
    per-yard price is on no period, so Price is left out there and is never planned."""
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
    assert entry.respondent_questions["commercial.price"]["codes"] == corpus_mod.price_ladder_codes(price["low"])
    assert "commercial.price" in entry.plan()[3]


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_existing_sacrifice_is_one_total_over_a_recall_period(corpus, entry_id):
    """Calls 51, 60, 68: the plan row is `cost_total` with no codes and no units, every pick one total --
    `{mode, value, currency, period}`, `{nothing: true, ...}` or the escape -- with the recall period it was asked
    over, and the standing no option counts."""
    entry = corpus.by_id(entry_id)
    row = entry.respondent_questions["commercial.existing_sacrifice"]
    assert row["control"] == registry_mod.COST_TOTAL_CONTROL and row["escape"] == "cant_recall"
    assert "codes" not in row and "units" not in row
    assert "optionCounts" not in entry.expected["standings"]["commercial.existing_sacrifice"]
    for person in entry.people():
        pick = person.picks.get("commercial.existing_sacrifice")
        if pick is None or "chip" in pick:
            continue
        assert set(pick) <= {"mode", "value", "nothing", "currency", "period"}, (entry_id, person.person)
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
    """Call 60: the cost on the five periods (HOURS at a rate on Repeatline only), the B2B entries' `hourly_rate`,
    Ability to pay recomputed from the cost and the price -- Mulch Run's left out with its price."""
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
    assert ("commercial.ability_to_pay" in entry.plan()[3]) is entry.b2b()


@pytest.mark.parametrize("entry_id, time_only", [("01-countly", 4), ("02-compliancelog", 7)])
def test_the_b2c_people_who_gave_only_time_are_reported_apart(corpus, entry_id, time_only):
    """Call 65: Countly's four managers and ComplianceLog's seven lose only time -- the standing records the
    count and the median hours a month, and counts them in no money reading."""
    standing = corpus.by_id(entry_id).expected["standings"]["commercial.existing_sacrifice"]
    assert standing["time_only"] == time_only and standing["time_only_hours"] > 0
    assert standing["status"] == "TOO_FEW_TO_CALL"


def test_lullabys_standings_are_087s(corpus):
    """03-lullaby at revision 10: Importance splits (3 of 8 put the own item in their two), Compatibility and
    Commitment hold on the fixed answers, Current solution fails below the line."""
    lullaby = corpus.by_id("03-lullaby")
    standings = lullaby.expected["standings"]
    expected = {
        "problem.prevalence": ("HOLDING_UP", "stronger"), "problem.frequency": ("HOLDING_UP", "none"),
        "problem.importance": ("PEOPLE_DISAGREE", "both"),
        "problem.current_solution_satisfaction": ("NOT_HOLDING_UP", "short"),
        "solution.compatibility": ("HOLDING_UP", "none"),
        "solution.relative_advantage": ("HOLDING_UP", "none"),
        "solution.adoption_friction": ("PEOPLE_DISAGREE", "both"),
        "commercial.existing_sacrifice": ("PEOPLE_DISAGREE", "both"),
        "commercial.price": ("PEOPLE_DISAGREE", "both"),
        "commercial.ability_to_pay": ("HOLDING_UP", "none"),
        "commercial.buyer_payer_alignment": ("HOLDING_UP", "none"),
        "commercial.commitment": ("HOLDING_UP", "none"),
    }
    assert {k: (v["status"], v.get("drift")) for k, v in standings.items()} == expected
    assert (standings["problem.prevalence"]["yes"], standings["problem.prevalence"]["n"]) == (10, 12)
    assert standings["problem.importance"]["own_item_picks"] == 3


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
def test_a_b2b_entrys_decision_makers_answer_commercial_only_on_their_own_link(corpus, entry_id, deciders):
    """FR-010, decision 26, keel-cloud 075: the decision-maker answers part 3 on COMMERCIAL_B2B, story-less and
    ANCHORED by rule; the primary people answer no commercial item at all."""
    entry = corpus.by_id(entry_id)
    assert entry.role(entry.decision_maker_role())["roleType"] == "BUYER"
    assert len(entry.deciders()) == deciders
    assert all(p.recency is None and p.picks and all(k.startswith("commercial.") for k in p.picks)
               for p in entry.deciders())
    assert not any(k.startswith("commercial.") for p in entry.gate_yes() for k in p.picks)
    assert all(p.story is None and p.chip is None and p.anchoring == "ANCHORED" for p in entry.deciders())
    assert set(registry_mod.B2B_ONLY) <= set(entry.plan()[3])


def test_the_corpus_wide_interpret_denominator_is_counted_not_estimated(corpus):
    """106 people, less every gate-No, every chipped story and every decision-maker (who is never read) -- r10
    moved no person."""
    assert sum(len(e.people()) for e in corpus.entries) == 106
    assert sum(len(e.readable()) for e in corpus.entries) == 65


def test_the_fixture_fallback_is_gone():
    """Call 49: no `tests/fixtures/corpus-r3/`, and no `FIXTURE_DIR` to fall back to."""
    assert not (Path(__file__).parent / "fixtures" / "corpus-r3").exists()
    assert not hasattr(corpus_mod, "FIXTURE_DIR")


@pytest.mark.parametrize("revision, rubric", [(9, "MARKS_VERSION 17"), (8, "MARKS_VERSION 15"),
                                              (6, "MARKS_VERSION 12"), (3, "MARKS_VERSION 9")])
def test_a_corpus_directory_holding_an_older_file_refuses_by_name(tmp_path, revision, rubric):
    """Calls 49, 78: one older file in keel-cloud's corpus refuses the whole load, naming the entry and the rubric
    that read its revision -- never a fallback."""
    keel_cloud = tmp_path / "keel-cloud"
    canon = corpus_mod.corpus_dir(keel_cloud)
    canon.mkdir(parents=True)
    raw = fx.raw_entry()
    fx.write_entry(canon, raw, "09-fixture.yaml")
    fx.write_entry(canon, dict(raw, id="08-old", revision=revision), "08-old.yaml")
    with pytest.raises(corpus_mod.CorpusError) as refusal:
        corpus_mod.load(keel_cloud, registry=fx.registry())
    assert str(refusal.value).startswith(f"08-old: revision is {revision}")
    assert rubric in str(refusal.value)


def test_a_missing_corpus_directory_refuses_by_name(tmp_path):
    with pytest.raises(corpus_mod.CorpusError) as refusal:
        corpus_mod.load(tmp_path / "keel-cloud", registry=fx.registry())
    assert "no corpus at" in str(refusal.value)


def test_the_corpus_reads_the_same_through_the_exported_registry(corpus):
    """The cloud's own registry resource binds the seven as the slice does."""
    path = Path(load_config(validate=False).keel_cloud) / "src" / "main" / "resources" / "keel" / \
        "dimension-registry.json"
    if not path.is_file():
        pytest.skip(f"no exported registry at {path}")
    exported = registry_mod.load(path)
    for entry in corpus.entries:
        corpus_mod.load_file(entry.path, registry=exported)
    assert yaml.safe_load(Path(corpus.entries[0].path).read_text())["revision"] == 10


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_every_entry_records_the_two_golden_names(corpus, entry_id):
    """Call 55, amended: the idea's short name in at most five plain words, the offer's in at most six -- keel-cloud
    088's frames carry both (Relative advantage, Price)."""
    from instructions import context as context_mod                         # noqa: PLC0415
    entry = corpus.by_id(entry_id)
    short, offer = context_mod.short_name_of(entry), context_mod.offer_name_of(entry)
    assert short and len(short.split()) <= 5, (entry_id, short)
    assert offer and len(offer.split()) <= 6, (entry_id, offer)
    if entry_id == "03-lullaby":
        assert (short, offer) == ("a suggested reason for crying", "something that helps at night")


def test_every_relative_advantage_is_benefit_first(corpus):
    """Call 76 kept, call 78: the founder's benefits are a one-item list (`{items: [{code, label}]}`), the plan row is
    the code-written item with its one escape, a pick is `{answer, advantages}`."""
    key = "solution.relative_advantage"
    for entry in corpus.entries:
        assert len(entry.founder_list(key)["items"]) == 1, entry.id
        assert entry.respondent_questions[key] == {"part": 2, "control": "benefit_with_advantages",
                                                   "codes": ["positive", "neutral", "negative"],
                                                   "escape": "cant_tell"}, entry.id
