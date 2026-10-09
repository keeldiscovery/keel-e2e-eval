"""`instructions/corpus.py` at revision 4: the loader on a hand-sized entry (spec 029 FR-006, data-model
§2-§3; T012; at revision 4 by spec 030 T006, judgement calls 47 and 49).

Everything the scorers read off an entry -- the plan, the vocabulary and its inflection ledger, who
is readable -- is checked here on `tests/fixtures/corpus/09-fixture-r4.yaml`, a person can count it
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


def test_the_plan_is_four_three_two(entry):
    plan = entry.plan()
    assert {part: len(keys) for part, keys in plan.items()} == {1: 4, 2: 3, 3: 2}
    assert plan[1][0] == "problem.prevalence", "the gate is Part 1's first item"
    assert "commercial.buyer_payer_alignment" not in plan[3], "left out by the founder"
    assert "commercial.ability_to_pay" not in plan[3], "b2b_only, and this entry is B2C"


def test_the_plan_without_a_registry_is_the_files_own_golden_plan():
    unbound = corpus_mod.load_file(fx.ENTRY)
    assert {p: len(k) for p, k in unbound.plan().items()} == {1: 4, 2: 3, 3: 2}


def test_a_b2b_entry_calibrates_twelve_and_routes_part_three_to_the_decision_maker():
    """Call 47 and decision 26: the b2b_only pair calibrated and asked, on COMMERCIAL_B2B."""
    b2b = fx.entry(fx.ENTRY_B2B)
    assert len(b2b.calibrated_keys()) == 12 and len(fx.entry().calibrated_keys()) == 10
    assert b2b.link_of(3) == "COMMERCIAL_B2B" and b2b.link_of(1) == "PRIMARY"
    assert b2b.plan()[3] == ["commercial.existing_sacrifice", "commercial.ability_to_pay",
                             "commercial.purchase_friction", "commercial.commitment"]


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
                   "revision 4 only -- revision 3 is MARKS_VERSION 9's corpus"),
    "labels one short": (
        lambda r: r["founder_calibration"]["commercial.existing_sacrifice"].__setitem__(
            "labels", ["Spares"]),
        "founder_calibration[commercial.existing_sacrifice].labels must be one label per founder "
        "option"),
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
        "commercial.ability_to_pay", {"answer": "easily", "belief_sentence": "x"}),
        "names commercial.ability_to_pay, which a B2C entry does not calibrate (b2b_only; "
        "judgement call 47)"),
    "a b2b_only pick on a B2C entry": (lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
        "commercial.purchase_friction", ["forgetting"]),
        "Ann Abbott picks commercial.purchase_friction, which a B2C entry does not calibrate"),
    "a standing short": (lambda r: r["expected"]["standings"].pop("problem.importance"),
                         "expected.standings is not exactly the 10 calibrated keys"),
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
            "story": "Last month we bought a fleet tag.", "chip": None, "anchoring": "ANCHORED",
            "picks": {"commercial.ability_to_pay": "easily"}, **over}


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
    ("primary", fx.ENTRY, {}, "decision-maker is the same person"),
])
def test_a_decision_maker_out_of_place_is_refused(tmp_path, path, raw_entry, mutation, words):
    raw = fx.raw_entry(raw_entry)
    raw["answers"].append(_decider(**mutation))
    with pytest.raises(corpus_mod.CorpusError) as refusal:
        corpus_mod.load_file(fx.write_entry(tmp_path, raw))
    assert words in str(refusal.value)
