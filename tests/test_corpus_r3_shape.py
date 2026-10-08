"""Corpus revision 3, the real seven files, through the one reader (spec 029 FR-006 to FR-012,
SC-005; T047).

**One reader, one hash** (spec 010's rule): the files are read through `instructions.corpus.load`
exactly as a run reads them -- keel-cloud's corpus once it carries revision 3, and this branch's
recorded revision (`tests/fixtures/corpus-r3/`) while it does not (the loader's docstring). Nothing
here is a copy of either. What is held is the shape every entry must have, and the facts the spec
names entry by entry: Lullaby's statuses, drifts, totals and verdicts (FR-007); Hugo and Leo at the
gate and Jonas's chip (FR-011, FR-017); Countly's asked dimension left out (FR-009); the B2B entry
(FR-010); and the seven digests: canon's once it holds r3, the fixtures' while it holds r2,
byte-identical either way.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml

from instructions import corpus as corpus_mod
from stack.config import load_config
from tests import v9_fixtures as fx

ENTRIES = ("01-countly", "02-compliancelog", "03-lullaby", "04-linerly", "05-paidly",
           "06-repeatline", "07-mulchrun")


@pytest.fixture(scope="module")
def corpus():
    return corpus_mod.load(load_config(validate=False).keel_cloud, registry=fx.registry())


def test_the_seven_entries_are_all_at_revision_three(corpus):
    assert [e.id for e in corpus.entries] == list(ENTRIES)
    for entry in corpus.entries:
        assert entry.revision == 3, entry.id


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_every_entry_has_the_r3_shape_and_the_plans_asks(corpus, entry_id):
    entry = corpus.by_id(entry_id)
    registry = fx.registry()
    assert set(entry.founder_calibration) == set(registry.keys())
    assert sum(len(keys) for keys in entry.plan().values()) <= 23
    assert set(entry.expected["standings"]) == set(registry.keys())
    assert set(entry.expected["vector_verdicts"]) == {"PROBLEM", "SOLUTION", "COMMERCIAL"}
    for key, row in entry.founder_calibration.items():
        assert row.get("belief_sentence"), f"{entry_id} {key}: O-2's belief sentence"
    assert entry.interpretations.get("problem"), f"{entry_id}: O-3's problem sentence"
    assert entry.respondent_questions["problem.importance"].get("own_item"), "D3's own item"
    assert entry.vocabulary(), "no_leak needs a list to sweep with"


def test_lullaby_reproduces_the_registrys_worked_example(corpus):
    """FR-007, A-6: the registry's `lullaby` objects, under the signed rules."""
    lullaby = corpus.by_id("03-lullaby")
    standings = lullaby.expected["standings"]
    expected = {
        "problem.prevalence": ("HOLDING_UP", "above"), "problem.duration": ("NOT_HOLDING_UP", "below"),
        "problem.severity": ("PEOPLE_DISAGREE", "below"),
        "problem.current_solution_satisfaction": ("NOT_HOLDING_UP", "above"),
        "problem.importance": ("HOLDING_UP", "none"), "problem.urgency": ("LEFT_OUT", None),
        "commercial.retention_potential": ("LEFT_OUT", None),
        "solution.effectiveness_threshold": ("BAR_SET", "above"),
        "commercial.wtp_hypothesis": ("NOT_TESTED_BY_DESIGN", "none"),
    }
    for key, (status, drift) in expected.items():
        assert (standings[key]["status"], standings[key].get("drift")) == (status, drift), key
    assert (standings["problem.prevalence"]["yes"], standings["problem.prevalence"]["n"]) == (10, 12)
    assert (standings["problem.duration"]["median"], standings["problem.duration"]["n"]) == (11, 7)
    assert standings["problem.importance"]["share"] == 0.38
    totals = {}
    for row in standings.values():
        totals[row["status"]] = totals.get(row["status"], 0) + 1
    assert totals == {"HOLDING_UP": 12, "NOT_HOLDING_UP": 6, "PEOPLE_DISAGREE": 3, "BAR_SET": 1,
                      "NOT_TESTED_BY_DESIGN": 1, "LEFT_OUT": 2}
    assert lullaby.expected["vector_verdicts"] == {
        "PROBLEM": {"verdict": "NOT_HOLDING_UP", "deciding": "problem.duration"},
        "SOLUTION": {"verdict": "NOT_HOLDING_UP", "deciding": "solution.compatibility"},
        "COMMERCIAL": {"verdict": "NOT_HOLDING_UP", "deciding": "commercial.commitment"}}
    assert all(row.get("n", 0) <= 10 for key, row in standings.items()
               if key.startswith("commercial.")), "decision 14: n <= 10 on part 3"


def test_lullabys_twelve_people_two_at_the_gate_and_one_chip(corpus):
    lullaby = corpus.by_id("03-lullaby")
    assert len(lullaby.people()) == 12 and len(lullaby.readable()) == 9
    for name in ("Hugo Laurent", "Leo Martins"):
        person = lullaby.person(name)
        assert (person.recency, person.story, person.picks) == ("no", None, {}), name
    jonas = lullaby.person("Jonas Weber")
    assert (jonas.chip, jonas.anchoring) == ("cant_recall", "GUESSED")
    assert "Jonas Weber" not in [p.person for p in lullaby.readable()]


def test_countly_leaves_out_an_asked_dimension(corpus):
    """FR-009, decision 16: `dimension_coverage`'s `unsure` subtraction is exercised, not only
    `asked_in_v1`'s."""
    countly = corpus.by_id("01-countly")
    assert countly.unsure("problem.severity")
    assert countly.expected["standings"]["problem.severity"]["status"] == "LEFT_OUT"
    assert len(countly.plan()[1]) == 7


def test_paidly_is_b2b_with_its_decision_makers_on_their_own_link(corpus):
    """FR-010, A-5: the agency decides; its people answer Part 3 on the COMMERCIAL_B2B link."""
    paidly = corpus.by_id("05-paidly")
    assert paidly.persona["decision_maker"] == {"role": "agency"}
    assert paidly.role("agency")["roleType"] == "BUYER"
    deciders = paidly.deciders()
    assert len(deciders) == 8
    assert all(p.recency is None and all(k.startswith("commercial.") for k in p.picks)
               for p in deciders)
    assert len(paidly.plan()[3]) == 6, "the B2B link is Part 3's plan"


def test_the_corpus_wide_interpret_denominator_is_counted_not_estimated(corpus):
    """O-4: 106 people, less every gate-No, every chipped story and every decision-maker (who is
    never read) -- the number marks.py's v9 header records."""
    assert sum(len(e.people()) for e in corpus.entries) == 106
    assert sum(len(e.readable()) for e in corpus.entries) == 65


def _fixture_digests() -> dict:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(corpus_mod.FIXTURE_DIR).glob("*.yaml"))}


def _digests(corpus) -> dict:
    return {Path(path).name: digest for path, digest in corpus.hashes.items()}


def test_a_revision_three_canon_is_read_and_its_digests_are_the_fixtures(tmp_path):
    """keel-cloud's corpus at r3 (the files moved byte for byte): the loader reads canon, and the
    seven digests are the recorded revision's."""
    keel_cloud = tmp_path / "keel-cloud"
    canon = corpus_mod.corpus_dir(keel_cloud)
    canon.mkdir(parents=True)
    for path in Path(corpus_mod.FIXTURE_DIR).glob("*.yaml"):
        (canon / path.name).write_bytes(path.read_bytes())
    assert corpus_mod.source_dir(keel_cloud) == canon
    loaded = corpus_mod.load(keel_cloud, registry=fx.registry())
    assert loaded.directory == canon
    assert _digests(loaded) == _fixture_digests() and len(loaded.hashes) == 7


def test_a_revision_two_canon_falls_back_to_the_fixtures(tmp_path):
    """keel-cloud's corpus still at r2: the loader reads `tests/fixtures/corpus-r3/`, and no
    digest it reports is one of the r2 files'."""
    keel_cloud = tmp_path / "keel-cloud"
    canon = corpus_mod.corpus_dir(keel_cloud)
    canon.mkdir(parents=True)
    for path in Path(corpus_mod.FIXTURE_DIR).glob("*.yaml"):
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        fx.write_entry(canon, dict(raw, revision=2), path.name)
    assert corpus_mod.source_dir(keel_cloud) == corpus_mod.FIXTURE_DIR
    loaded = corpus_mod.load(keel_cloud, registry=fx.registry())
    assert Path(loaded.directory) == Path(corpus_mod.FIXTURE_DIR)
    assert _digests(loaded) == _fixture_digests()
    old = {hashlib.sha256(p.read_bytes()).hexdigest() for p in canon.glob("*.yaml")}
    assert not set(loaded.hashes.values()) & old


#: keel-cloud 058's worktree, whose canon took revision 3 in 44dab90.
KEEL_CLOUD_058 = Path("/Users/athulrajeev/Documents/projects/keel-cloud/.claude/worktrees/"
                      "058-vector-corridor")


def test_keel_cloud_058s_canon_is_the_recorded_revision_byte_for_byte():
    canon = corpus_mod.corpus_dir(KEEL_CLOUD_058)
    if not canon.is_dir():
        pytest.skip(f"keel-cloud 058's worktree corpus is absent at {canon}")
    theirs = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(canon.glob("*.yaml"))}
    assert theirs == _fixture_digests(), "canon r3 and tests/fixtures/corpus-r3 must not drift"


def test_the_recorded_revision_carries_its_move_instruction():
    readme = (Path(corpus_mod.FIXTURE_DIR) / "README.md").read_text(encoding="utf-8")
    assert "moved, byte for byte" in readme
    assert "canon/designs/measured-beliefs/corpus/" in readme


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


def test_lullabys_labels_are_the_registrys_worked_example_verbatim(corpus):
    """`lullaby.founder_options[*].label` of the verbatim registry draft (`contracts/`), which
    keel-cloud 058's `dimension-registry.json` carries unchanged -- with 058's own C6 rewording
    (`VectorFixtures.patchedOptions`: *better* -> *more*, *faster* -> *sooner*, *helps* -> *is
    useful*), because those are the labels 058's Lullaby project holds and its contract tool
    compares a batch's `founder_options` against."""
    import yaml                                                             # noqa: PLC0415
    draft = Path(__file__).resolve().parent.parent / "specs" / "029-marks-v9-vectors" / \
        "contracts" / "dimension-registry.yaml"
    lullaby = corpus.by_id("03-lullaby")
    for dimension in yaml.safe_load(draft.read_text(encoding="utf-8"))["dimensions"]:
        if (dimension["founder"].get("normalized") or {}).get("codes") != "model_written":
            continue
        want = [o["label"].replace("better", "more").replace("faster", "sooner")
                .replace("helps", "is useful") for o in dimension["lullaby"]["founder_options"]]
        assert list(lullaby.founder_labels(dimension["key"]).values()) == want, dimension["key"]
