"""Corpus revision 4, the real seven files, through the one reader (spec 030 FR-002, US2; T006;
first written for revision 3 by spec 029 T047).

**One reader, one hash, one place** (spec 010's rule; judgement call 49): the files are read
through `instructions.corpus.load` exactly as a run reads them -- keel-cloud's canon, and nowhere
else; the fixture fallback of 2026-10-07 is gone with its directory. Nothing here is a copy of the
corpus. What is held is the shape every entry must have and the facts keel-cloud 071 pins
(`GoldenCorpusTest`): the calibrated set per persona (ten keys on 01-04, twelve on 05-07), the plan
per link, the status totals across the seven, Lullaby's standings and verdicts, the gate-No and
chipped people, and the B2B entries' decision-makers on `commercial.*` only.

When `stack.toml`'s keel-cloud is not at revision 4 every test here skips **by name**, with the
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
        fx.canon_entry(f"{name}.yaml")                 # skips, by name, when canon is not r4
    return corpus_mod.load(keel_cloud, registry=fx.registry())


def test_the_seven_entries_are_all_at_revision_four(corpus):
    assert [e.id for e in corpus.entries] == list(ENTRIES)
    for entry in corpus.entries:
        assert entry.revision == 4, entry.id
    assert Path(corpus.directory) == fx.canon_dir()


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_every_entry_calibrates_its_personas_set_and_plans_per_link(corpus, entry_id):
    """Call 47: ten keys on a B2C persona, twelve on a B2B one; PRIMARY asks 4 / 3 / 3 on B2C,
    and part 3 of a B2B study is the COMMERCIAL_B2B link's five (decision 26)."""
    entry = corpus.by_id(entry_id)
    registry = fx.registry()
    b2b = entry_id in B2B
    assert entry.b2b() is b2b
    calibrated = registry.calibrated_keys(b2b)
    assert len(calibrated) == (12 if b2b else 10)
    assert set(entry.founder_calibration) == set(calibrated) == set(entry.calibrated_keys())
    assert set(entry.expected["standings"]) == set(calibrated)
    assert {part: len(keys) for part, keys in entry.plan().items()} == \
        ({1: 4, 2: 3, 3: 5} if b2b else {1: 4, 2: 3, 3: 3})
    assert entry.link_of(3) == (registry_mod.LINK_B2B if b2b else registry_mod.LINK_PRIMARY)
    assert set(entry.expected["vector_verdicts"]) == {"PROBLEM", "SOLUTION", "COMMERCIAL"}
    for vector, verdict in entry.expected["vector_verdicts"].items():
        assert verdict["deciding"] in registry_mod.DEAL_BREAKERS[vector], (entry_id, vector)
    for key, row in entry.founder_calibration.items():
        assert row.get("belief_sentence"), f"{entry_id} {key}: the belief sentence"
    assert entry.interpretations.get("problem"), f"{entry_id}: the problem sentence"
    assert entry.respondent_questions["problem.importance"].get("own_item"), "D3's own item"
    assert entry.vocabulary(), "no_leak needs a list to sweep with"


def test_the_status_totals_across_the_seven_are_keel_cloud_071s(corpus):
    """The six status words only; the totals 071's recomputed corpus carries."""
    totals = {}
    for entry in corpus.entries:
        for row in entry.expected["standings"].values():
            assert row["status"] in corpus_mod.STATUSES
            totals[row["status"]] = totals.get(row["status"], 0) + 1
    assert totals == {"HOLDING_UP": 53, "NOT_HOLDING_UP": 11, "PEOPLE_DISAGREE": 12}
    assert sum(totals.values()) == 4 * 10 + 3 * 12


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
    """The registry's `checks.lullaby_statuses`: 6 / 3 / 1, Prevalence holding with its drift."""
    lullaby = corpus.by_id("03-lullaby")
    standings = lullaby.expected["standings"]
    expected = {
        "problem.prevalence": ("HOLDING_UP", "above"), "problem.frequency": ("HOLDING_UP", "none"),
        "problem.importance": ("HOLDING_UP", "none"),
        "problem.current_solution_satisfaction": ("NOT_HOLDING_UP", "above"),
        "solution.compatibility": ("NOT_HOLDING_UP", "above"),
        "solution.adoption_friction": ("PEOPLE_DISAGREE", "below"),
        "commercial.commitment": ("NOT_HOLDING_UP", "none"),
    }
    for key, (status, drift) in expected.items():
        assert (standings[key]["status"], standings[key].get("drift")) == (status, drift), key
    assert (standings["problem.prevalence"]["yes"], standings["problem.prevalence"]["n"]) == (10, 12)
    assert standings["problem.importance"]["share"] == 0.38
    totals = {}
    for row in standings.values():
        totals[row["status"]] = totals.get(row["status"], 0) + 1
    assert totals == {"HOLDING_UP": 6, "NOT_HOLDING_UP": 3, "PEOPLE_DISAGREE": 1}
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
    """FR-010, decision 26: the decision-maker answers part 3 on COMMERCIAL_B2B, the b2b_only
    pair included; the primary people answer no commercial item at all."""
    entry = corpus.by_id(entry_id)
    assert entry.role(entry.decision_maker_role())["roleType"] == "BUYER"
    assert len(entry.deciders()) == deciders
    assert all(p.recency is None and p.picks and all(k.startswith("commercial.") for k in p.picks)
               for p in entry.deciders())
    assert not any(k.startswith("commercial.") for p in entry.gate_yes() for k in p.picks)
    assert set(registry_mod.B2B_ONLY) <= set(entry.plan()[3])


def test_the_corpus_wide_interpret_denominator_is_counted_not_estimated(corpus):
    """106 people, less every gate-No, every chipped story and every decision-maker (who is never
    read) -- the number marks.py's v10 header records."""
    assert sum(len(e.people()) for e in corpus.entries) == 106
    assert sum(len(e.readable()) for e in corpus.entries) == 65


def test_the_fixture_fallback_is_gone():
    """Call 49: no `tests/fixtures/corpus-r3/`, and no `FIXTURE_DIR` to fall back to."""
    assert not (Path(__file__).parent / "fixtures" / "corpus-r3").exists()
    assert not hasattr(corpus_mod, "FIXTURE_DIR")


def test_a_corpus_directory_holding_a_revision_three_file_refuses_by_name(tmp_path):
    """Call 49: one r3 file in keel-cloud's corpus refuses the whole load, naming the entry and
    revision 3 as v9's -- never a fallback."""
    keel_cloud = tmp_path / "keel-cloud"
    canon = corpus_mod.corpus_dir(keel_cloud)
    canon.mkdir(parents=True)
    raw = fx.raw_entry()
    fx.write_entry(canon, raw, "09-fixture-r4.yaml")
    fx.write_entry(canon, dict(raw, id="08-old", revision=3), "08-old.yaml")
    with pytest.raises(corpus_mod.CorpusError) as refusal:
        corpus_mod.load(keel_cloud, registry=fx.registry())
    assert str(refusal.value).startswith("08-old: revision is 3")
    assert "MARKS_VERSION 9" in str(refusal.value)


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
                if dimension.fixed_codes is not None or dimension.founder_numeric:
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
    assert yaml.safe_load(Path(corpus.entries[0].path).read_text())["revision"] == 4
