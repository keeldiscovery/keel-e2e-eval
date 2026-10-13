"""`instructions/corpus.py` at revision 7: the loader on a hand-sized entry (spec 029 FR-006, data-model
§2-§3; T012; at revision 4 by spec 030 T006, judgement calls 47 and 49; at revision 5 by spec 031
T006, judgement calls 50 and 51; at revision 6 by spec 032 T005, judgement calls 59 and 60; at revision 7 by spec 033 T004, call 68; at revision 9 by spec 038 T002, call 76).

Everything the scorers read off an entry -- the plan, the vocabulary and its inflection ledger, who
is readable -- is checked here on `tests/fixtures/corpus/09-fixture-r7.yaml`, a person can count it
by hand: 12 people, Kit and Lu answer No at the gate, Jo chips, Ivy's story is vague, eight are
anchored; one founder answer is unsure. And every refusal of data-model §2 is made to happen once,
from a one-line change to that file, naming the entry and the key.
"""

from __future__ import annotations

import pytest

from instructions import corpus as corpus_mod
from tests import v9_fixtures as fx


@pytest.fixture()
def entry():
    return fx.entry()


def test_the_plan_is_four_three_three(entry):
    plan = entry.plan()
    assert {part: len(keys) for part, keys in plan.items()} == {1: 4, 2: 3, 3: 3}
    assert plan[3] == ["commercial.existing_sacrifice", "commercial.price", "commercial.commitment"]
    assert plan[1][0] == "problem.prevalence", "the gate is Part 1's first item"
    assert "commercial.buyer_payer_alignment" not in plan[3], "left out by the founder"
    assert "commercial.ability_to_pay" not in plan[3], "b2b_link_only, and this entry is B2C"


def test_the_plan_without_a_registry_is_the_files_own_golden_plan():
    unbound = corpus_mod.load_file(fx.ENTRY)
    assert {p: len(k) for p, k in unbound.plan().items()} == {1: 4, 2: 3, 3: 3}


def test_a_b2b_entry_calibrates_thirteen_and_routes_part_three_to_the_decision_maker():
    """Calls 47, 59 and decision 26: Purchase friction calibrated and asked, and Ability to pay asked,
    on COMMERCIAL_B2B -- Price too, asked of whoever pays; a B2C entry calibrates twelve."""
    b2b = fx.entry(fx.ENTRY_B2B)
    assert len(b2b.calibrated_keys()) == 13 and len(fx.entry().calibrated_keys()) == 12
    assert b2b.link_of(3) == "COMMERCIAL_B2B" and b2b.link_of(1) == "PRIMARY"
    assert b2b.plan()[3] == ["commercial.existing_sacrifice", "commercial.price",
                             "commercial.ability_to_pay", "commercial.purchase_friction",
                             "commercial.commitment"]


def test_the_price_the_units_and_the_ladder_are_read(entry):
    """Call 51: the founder's range, its period and currency; the row the
    ladder's five bands around a low of 3 (the 2-5 band in the middle) plus would_not_pay."""
    assert entry.price() == {"low": 3, "high": 5, "period": "month", "currency": "GBP"}
    assert not hasattr(entry, "units"), "call 68: there are no kinds of cost to count in a unit"
    assert corpus_mod.price_ladder_codes(3) == entry.respondent_questions["commercial.price"]["codes"]
    assert corpus_mod.price_ladder_codes(500) == [
        "under_250", "band_250_500", "band_500_1000", "band_1000_2500", "over_2500", "would_not_pay"]
    assert corpus_mod.price_ladder_codes(1)[:2] == ["under_1", "band_1_2"], "clamped at the foot"
    assert corpus_mod.price_ladder_codes(9999)[-2:] == ["over_10000", "would_not_pay"], \
        "clamped at the head"
    with pytest.raises(ValueError):
        corpus_mod.price_ladder_codes(10000)


def test_the_vocabulary_is_the_mechanisms_stems_and_none_of_the_problems(entry):
    vocabulary = entry.vocabulary()
    assert {"tag", "beep", "whistl", "loud"} <= vocabulary
    for problem_word in ("key", "morn", "door", "commuter", "cycl", "lost"):
        assert problem_word not in vocabulary
    assert entry.mechanism_phrases() == [("key", "ring")]


def test_the_inflection_ledger_carries_the_one_planted_collision(entry):
    ledger = entry.inflection_ledger()
    assert ledger == {"listen": {"mechanism": ["listens"], "problem": ["listened"]}}
    assert "listen" not in entry.vocabulary(), "a tie is the judge's, never a plain fault"


def test_the_one_liner_is_the_golden_mechanisms_four_fields(entry):
    line = entry.mechanism_one_liner()
    for part in ("the commuter", "when the keys are not where they were left",
                 "whistles once", "a beep from the tag"):
        assert part in line


def test_who_is_read_who_passed_the_gate_and_who_answered_at_all(entry):
    assert len(entry.people()) == 12
    assert len(entry.gate_yes()) == 10
    readable = [p.person for p in entry.readable()]
    assert len(readable) == 9
    assert "Jo Judd" not in readable, "a chipped story is GUESSED by code, never read"
    assert "Kit Kerr" not in readable and "Lu Lam" not in readable
    assert "Ivy Ives" in readable, "a vague story without a chip is read -- and is GUESSED"


def test_b2b_is_the_decision_maker_being_a_role(entry):
    assert entry.b2b() is False
    b2b = fx.entry(fx.ENTRY_B2B)
    assert b2b.b2b() is True and b2b.decision_maker_role() == "buyer"


def test_the_hash_and_verify_unchanged_are_unchanged(tmp_path):
    path = fx.write_entry(tmp_path, fx.raw_entry())
    corpus = corpus_mod.Corpus(entries=[corpus_mod.load_file(path)], directory=tmp_path,
                               hashes={str(path): corpus_mod._sha256(path)})
    corpus.verify_unchanged()
    path.write_text(path.read_text() + "\n# moved\n")
    with pytest.raises(corpus_mod.CorpusError, match="changed while the run was in flight"):
        corpus.verify_unchanged()


def _person(raw, name):
    return next(p for p in raw["answers"] if p["person"] == name)


MUTATIONS = {
    "revision 2": (lambda r: r.__setitem__("revision", 2), "revision is 2"),
    "no revision": (lambda r: r.pop("revision"), "revision is absent"),
    "beliefs": (lambda r: r.__setitem__("beliefs", []), "`beliefs`"),
    "questionnaire": (lambda r: r.__setitem__("questionnaire", {}), "`questionnaire`"),
    "buckets": (lambda r: r["expected"].__setitem__("buckets", {}), "`expected.buckets`"),
    "stages": (lambda r: r["expected"].__setitem__("stages", {}), "`expected.stages`"),
    "anchors": (lambda r: _person(r, "Ann Abbott").__setitem__("anchors", {}), "`anchors`"),
    "revision 3": (lambda r: r.__setitem__("revision", 3), "revision is 3; this eval reads "
                   "revision 9 only -- revision 3 is MARKS_VERSION 9's corpus"),
    "revision 4": (lambda r: r.__setitem__("revision", 4), "revision is 4; this eval reads "
                   "revision 9 only -- revision 4 is MARKS_VERSION 10's corpus"),
    "revision 5": (lambda r: r.__setitem__("revision", 5), "revision is 5; this eval reads "
                   "revision 9 only -- revision 5 is MARKS_VERSION 11's corpus"),
    "revision 7": (lambda r: r.__setitem__("revision", 7), "revision is 7; this eval reads "
                   "revision 9 only -- revision 7 is MARKS_VERSION 13's and 14's corpus"),
    "revision 8": (lambda r: r.__setitem__("revision", 8), "revision is 8; this eval reads "
                   "revision 9 only -- revision 8 is MARKS_VERSION 15's and 16's corpus, before benefit first"),
    "an advantage answer that is not a list": (
        lambda r: r["founder_calibration"]["solution.relative_advantage"].__setitem__(
            "answer", "shorter_time"), "revision 9 ticks one to 4 distinct advantages, as a list"),
    "five advantages ticked": (
        lambda r: r["founder_calibration"]["solution.relative_advantage"].__setitem__(
            "answer", ["fewer_attempts", "shorter_time", "less_worry", "less_help_needed", "easier_recovery"]),
        "revision 9 ticks one to 4 distinct advantages, as a list"),
    "the old single-choice plan row": (
        lambda r: r["respondent_questions"]["solution.relative_advantage"].__setitem__(
            "control", "single_choice"), "revision 9 asks benefit_with_advantages over"),
    "a benefit pick that is a bare code": (
        lambda r: _person(r, "Ann Abbott")["picks"].__setitem__("solution.relative_advantage", "shorter_time"),
        "Ann Abbott's solution.relative_advantage pick is 'shorter_time'; revision 9 answers"),
    "positive without an advantage": (
        lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
            "solution.relative_advantage", {"answer": "positive"}), "exactly under positive"),
    "an advantage the founder did not tick": (
        lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
            "solution.relative_advantage", {"answer": "positive", "advantages": ["less_worry"]}),
        "exactly under positive"),
    "advantages under neutral": (
        lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
            "solution.relative_advantage", {"answer": "neutral", "advantages": ["shorter_time"]}),
        "exactly under positive"),
    "a price off the ladder": (
        lambda r: r["founder_calibration"]["commercial.price"]["answer"].__setitem__("low", 10000),
        "founder_calibration[commercial.price] is 10000 to 5: off the ladder"),
    "revision 6": (lambda r: r.__setitem__("revision", 6), "revision is 6; this eval reads "
                   "revision 9 only -- revision 6 is MARKS_VERSION 12's corpus"),
    "a price on a period outside the five": (
        lambda r: r["founder_calibration"]["commercial.price"]["answer"].__setitem__(
            "period", "one_off"), "founder_calibration[commercial.price].period is 'one_off'"),
    "a price on another period than the cost's": (
        lambda r: r["founder_calibration"]["commercial.price"]["answer"].__setitem__(
            "period", "week"), "it is the cost estimate's, 'month' (since revision 6)"),
    "a cost that is a tick list": (
        lambda r: r["founder_calibration"]["commercial.existing_sacrifice"].__setitem__(
            "answer", ["spare_keys"]), "a cost estimate is {mode: AMOUNT | HOURS"),
    "hours on a B2C entry": (
        lambda r: r["founder_calibration"]["commercial.existing_sacrifice"]["answer"].update(
            mode="HOURS", rate=20), "is HOURS on a B2C entry"),
    "a cost low of nothing": (
        lambda r: r["founder_calibration"]["commercial.existing_sacrifice"]["answer"].__setitem__(
            "low", 0), "a cost low is above 0"),
    "a cost on a period outside the five": (
        lambda r: r["founder_calibration"]["commercial.existing_sacrifice"]["answer"].__setitem__(
            "period", "one_off"), "founder_calibration[commercial.existing_sacrifice].period is 'one_off'"),
    "a cost in another currency": (
        lambda r: r["founder_calibration"]["commercial.existing_sacrifice"]["answer"].__setitem__(
            "currency", "USD"), "founder_calibration[commercial.existing_sacrifice].currency is 'USD'"),
    "a cost sentence that is not the engine's": (
        lambda r: r["founder_calibration"]["commercial.existing_sacrifice"].__setitem__(
            "belief_sentence", "They spend a lot."), "the engine's is 'The problem already costs the payer about"),
    "an ability that is not derived": (
        lambda r: r["founder_calibration"]["commercial.ability_to_pay"]["answer"].__setitem__(
            "band", "new_money"), "derived from the cost and the price it is"),
    "an ability answered over a cost left out": (
        lambda r: r["founder_calibration"]["commercial.existing_sacrifice"].update(
            {"unsure": True}) or r["founder_calibration"]["commercial.existing_sacrifice"].pop("answer"),
        "the cost or the price is left out, so it is too"),
    "ability to pay missing": (lambda r: r["founder_calibration"].pop("commercial.ability_to_pay"),
                               "founder_calibration lacks commercial.ability_to_pay"),
    "a pick with no recall period": (
        lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
            "commercial.existing_sacrifice",
            {"mode": "AMOUNT", "value": 3, "currency": "GBP"}),
        "records period None; revision 7 records the recall period"),
    "a price in another currency": (
        lambda r: r["founder_calibration"]["commercial.price"]["answer"].__setitem__(
            "currency", "USD"), "the market (GB) prices in GBP, never another"),
    "a price row that is not the ladder": (
        lambda r: r["respondent_questions"]["commercial.price"].__setitem__(
            "codes", ["under_5", "band_5_10", "band_10_20", "band_20_50", "over_50",
                      "would_not_pay"]),
        "respondent_questions[commercial.price].codes are"),
    "a kinds list on the founder's entry": (
        lambda r: r["founder_calibration"]["commercial.existing_sacrifice"].__setitem__(
            "labels", ["Spares"]), "carries `labels`; revision 7 has no kinds of cost"),
    "units on the founder's entry": (
        lambda r: r["founder_calibration"]["commercial.existing_sacrifice"].__setitem__(
            "units", {"spare_keys": "money"}), "carries `units`; revision 7 has no kinds of cost"),
    "the old control": (
        lambda r: r["respondent_questions"]["commercial.existing_sacrifice"].__setitem__(
            "control", "branch_pick_amounts"), "revision 7 asks cost_total, with no codes and no units"),
    "codes on the plan row": (
        lambda r: r["respondent_questions"]["commercial.existing_sacrifice"].__setitem__(
            "codes", ["spare_keys", "none"]), "revision 7 asks cost_total, with no codes and no units"),
    "an r6 pick": (
        lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
            "commercial.existing_sacrifice",
            {"currency": "GBP", "period": "quarter",
             "amounts": [{"kind": "spare_keys", "value": 3, "unit": "money"}]}),
        "revision 7 answers {mode: AMOUNT | HOURS, value, currency, period}"),
    "an r4 pick": (
        lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
            "commercial.existing_sacrifice", {"bought": "spare_keys", "cost": {"value": 4}}),
        "revision 7 answers {mode: AMOUNT | HOURS, value, currency, period}"),
    "a negative total": (
        lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
            "commercial.existing_sacrifice",
            {"mode": "HOURS", "value": -2, "currency": "GBP", "period": "month"}),
        "revision 7 answers {mode: AMOUNT | HOURS, value, currency, period}"),
    "option counts on the standing": (
        lambda r: r["expected"]["standings"]["commercial.existing_sacrifice"].__setitem__(
            "optionCounts", "spare_keys=2"), "records optionCounts; revision 7 has no kinds to count"),
    "a price pick off the row": (
        lambda r: _person(r, "Ann Abbott")["picks"].__setitem__("commercial.price", "band_20_50"),
        "Ann Abbott's commercial.price pick 'band_20_50' is not one of the ladder's"),
    "neither answer nor unsure": (
        lambda r: r["founder_calibration"].__setitem__("problem.importance",
                                                       {"belief_phrase": "x"}),
        "founder_calibration[problem.importance]"),
    "gate-No with a story": (lambda r: _person(r, "Kit Kerr").__setitem__("story", "Tuesday."),
                             "Kit Kerr answered No at the gate and carries `story`"),
    "gate-No with picks": (lambda r: _person(r, "Lu Lam").__setitem__(
        "picks", {"problem.frequency": 2}), "Lu Lam answered No at the gate and carries picks"),
    "chip anchored": (lambda r: _person(r, "Jo Judd").__setitem__("anchoring", "ANCHORED"),
                      "Jo Judd carries the chip cant_recall and is ANCHORED"),
    "unknown role": (lambda r: r.__setitem__("persona", {"decision_maker": {"role": "cfo"}}),
                     "names the role 'cfo'"),
    "status outside Status": (
        lambda r: r["expected"]["standings"]["problem.importance"].__setitem__("status", "MIXED"),
        "expected.standings[problem.importance].status is 'MIXED'"),
    "a retired status": (
        lambda r: r["expected"]["standings"]["solution.compatibility"].__setitem__(
            "status", "BAR_SET"),
        "expected.standings[solution.compatibility].status is 'BAR_SET', outside Status"),
    "deciding not a deal-breaker": (
        lambda r: r["expected"]["vector_verdicts"]["PROBLEM"].__setitem__(
            "deciding", "problem.frequency"),
        "deciding is 'problem.frequency', not a DEAL_BREAKER of PROBLEM"),
}

KEY_MUTATIONS = {
    "a founder key short": (lambda r: r["founder_calibration"].pop("problem.importance"),
                            "missing problem.importance"),
    "a founder key foreign": (lambda r: r["founder_calibration"].__setitem__(
        "problem.vibes", {"unsure": True}), "names problem.vibes, which is not a registry key"),
    "a b2b_only key on a B2C entry": (lambda r: r["founder_calibration"].__setitem__(
        "commercial.purchase_friction", {"answer": ["forgetting"], "belief_sentence": "x"}),
        "names commercial.purchase_friction, which a B2C entry does not calibrate (b2b_only; "
        "judgement call 47)"),
    "a b2b_only pick on a B2C entry": (lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
        "commercial.purchase_friction", ["forgetting"]),
        "Ann Abbott picks commercial.purchase_friction, which a B2C entry does not calibrate"),
    "a standing short": (lambda r: r["expected"]["standings"].pop("problem.importance"),
                         "expected.standings is not exactly the 12 calibrated keys"),
    "a founder code not the registry's": (lambda r: r["founder_calibration"]["problem.importance"].__setitem__(
        "answer", "the_top"), "answers 'the_top', which is not one of the registry's codes"),
    "a pick foreign": (lambda r: _person(r, "Ann Abbott")["picks"].__setitem__("problem.vibes", 1),
                       "Ann Abbott picks problem.vibes"),
    "a plan key foreign": (lambda r: r["respondent_questions"].__setitem__(
        "problem.vibes", {"part": 1}), "respondent_questions carries problem.vibes"),
    "a standing foreign": (lambda r: r["expected"]["standings"].__setitem__(
        "problem.vibes", {"status": "LEFT_OUT"}), "expected.standings carries problem.vibes"),
    "the plan disagrees": (lambda r: r["respondent_questions"].pop("problem.importance"),
                           "respondent_questions part 1"),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_every_refusal_names_the_entry_and_the_key(tmp_path, name):
    mutate, words = MUTATIONS[name]
    raw = fx.raw_entry()
    mutate(raw)
    with pytest.raises(corpus_mod.CorpusError) as refusal:
        corpus_mod.load_file(fx.write_entry(tmp_path, raw))
    assert str(refusal.value).startswith("09-fixture: "), refusal.value
    assert words in str(refusal.value)


@pytest.mark.parametrize("name", sorted(KEY_MUTATIONS))
def test_every_registry_refusal_names_the_entry_and_the_key(tmp_path, name):
    mutate, words = KEY_MUTATIONS[name]
    raw = fx.raw_entry()
    mutate(raw)
    path = fx.write_entry(tmp_path, raw)
    corpus_mod.load_file(path)                      # the shape alone is fine...
    with pytest.raises(corpus_mod.CorpusError) as refusal:
        corpus_mod.load_file(path, registry=fx.registry())   # ...the registry is not
    assert str(refusal.value).startswith("09-fixture: ")
    assert words in str(refusal.value)


def test_the_loader_reads_keel_clouds_canon_and_nowhere_else(tmp_path):
    """Call 49: the configured directory is the only source -- an older file there refuses by
    name, never a fallback to a fixture directory."""
    keel_cloud = tmp_path / "keel-cloud"
    directory = corpus_mod.corpus_dir(keel_cloud)
    directory.mkdir(parents=True)
    raw = fx.raw_entry()
    fx.write_entry(directory, raw, "02-new.yaml")
    assert corpus_mod.source_dir(keel_cloud) == directory
    assert [e.id for e in corpus_mod.load(keel_cloud).entries] == ["09-fixture"]
    fx.write_entry(directory, dict(raw, revision=3), "01-old.yaml")
    with pytest.raises(corpus_mod.CorpusError, match="revision is 3"):
        corpus_mod.load(keel_cloud)


# ---------------------------------------------- FR-010: the decision-maker's link on a B2B entry

def _decider(**over):
    return {"person": "Bea Buyer", "link": "COMMERCIAL_B2B", "recency": None,
            "story": None, "chip": None, "anchoring": "ANCHORED",
            "picks": {"commercial.ability_to_pay": "existing_line"}, **over}


def test_a_decision_maker_answers_part_three_on_their_own_link(tmp_path):
    raw = fx.raw_entry(fx.ENTRY_B2B)
    raw["answers"].append(_decider())
    entry = corpus_mod.load_file(fx.write_entry(tmp_path, raw), registry=fx.registry())
    assert [p.person for p in entry.deciders()] == ["Bea Buyer"]
    assert "Bea Buyer" not in [p.person for p in entry.readable()], "a decider is never read"
    assert len(entry.gate_yes()) == 10, "and is never asked the gate"


@pytest.mark.parametrize("path, raw_entry, mutation, words", [
    ("b2b", fx.ENTRY_B2B, {"recency": "yes"}, "is never asked the gate"),
    ("b2b", fx.ENTRY_B2B, {"picks": {"problem.frequency": 2}}, "the link is Part 3 only"),
    ("b2b", fx.ENTRY_B2B, {"story": "Last month we bought a fleet tag."}, "no story screen"),
    ("b2b", fx.ENTRY_B2B, {"anchoring": "GUESSED"}, "ANCHORED by rule"),
    ("primary", fx.ENTRY, {}, "decision-maker is the same person"),
])
def test_a_decision_maker_out_of_place_is_refused(tmp_path, path, raw_entry, mutation, words):
    raw = fx.raw_entry(raw_entry)
    raw["answers"].append(_decider(**mutation))
    with pytest.raises(corpus_mod.CorpusError) as refusal:
        corpus_mod.load_file(fx.write_entry(tmp_path, raw))
    assert words in str(refusal.value)
