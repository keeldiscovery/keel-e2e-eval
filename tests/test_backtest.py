"""Spec 062: the back-test runner, stackless (Acceptance 1).

The one test FR-1 asks for -- **every file in keel-cloud's back-test directory loads in back-test mode**, so a broken
entry is caught here and not after a paid run starts -- passes trivially while the directory is empty, and refuses the
broken fixture (`tests/fixtures/backtest/99-broken.yaml`) with the sentence a golden author gets. Around it: FR-1's
three differences and nothing else (`expected` absent, `idea_name`, `sources`), `vs.entry_for(..., backtest=True)`,
`IDEA_NAMES` falling back to the entry's own name, FR-2's refusal sentence and founder, FR-3's ungated export, FR-4's
transcript rendering, and FR-5's walls (no `make eval`, no matrix, no mark).
"""

from __future__ import annotations

import fnmatch
import json
from pathlib import Path

import pytest
import yaml

from evals import backtest as bt
from evals import sample_export as se
from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from instructions import marks as instruction_marks
from stack.config import load_config
from tests import v9_fixtures as fx

REPO = Path(__file__).resolve().parent.parent
BROKEN = REPO / "tests" / "fixtures" / "backtest" / "99-broken.yaml"
KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
IDEA = "Whistle key tag"


def _good_raw() -> dict:
    """10-fixture-b2b as a back-test entry: `expected` removed, the founder's idea name added."""
    raw = fx.raw_entry(fx.ENTRY_B2B)
    raw.pop("expected", None)
    raw["id"] = "98-good"
    raw["idea_name"] = IDEA
    raw["sources"] = "98-good.sources.md"
    return raw


def _write(tmp_path: Path, raw: dict, name: str = "98-good.yaml") -> Path:
    return fx.write_entry(tmp_path, raw, name=name)


def _refusal(path: Path, *, backtest: bool = True) -> str:
    with pytest.raises(corpus_mod.CorpusError) as refused:
        corpus_mod.load_file(path, registry=fx.registry(), backtest=backtest)
    return str(refused.value)


# ------------------------------------------------------------------------------------- FR-1: the directory

def test_every_backtest_entry_loads_in_backtest_mode():
    """FR-1's test: every `*.yaml` in `<keel_cloud>/canon/designs/measured-beliefs/backtest/`, through the back-test
    loader bound to the registry, and through the harness readers a run calls first -- trivially green when empty."""
    directory = corpus_mod.backtest_dir(KEEL_CLOUD)
    refused = {}
    for path in sorted(directory.glob("*.yaml")) if directory.is_dir() else []:
        try:
            entry = corpus_mod.load_file(path, registry=fx.registry(), backtest=True)
            vs.founder_inputs(entry)
            vs.person_inputs(entry)
        except (corpus_mod.CorpusError, vs.VectorsScriptError) as refusal:
            refused[path.name] = str(refusal)
    assert not refused, json.dumps(refused, indent=2)


def test_the_broken_fixture_is_refused_with_the_golden_sentence(tmp_path):
    said = _refusal(BROKEN)
    assert "99-broken: context.occasion is 'the cold wet winter morning'" in said, said
    # the same file with the occasion mended loads, so the occasion is the one fault
    raw = yaml.safe_load(BROKEN.read_text(encoding="utf-8"))
    raw["context"]["occasion"] = "morning"
    entry = corpus_mod.load_file(_write(tmp_path, raw, "99-broken.yaml"), registry=fx.registry(), backtest=True)
    assert entry.id == "99-broken" and entry.idea_name == IDEA


def test_a_good_entry_loads_with_no_expected_and_its_idea_name(tmp_path):
    entry = corpus_mod.load_file(_write(tmp_path, _good_raw()), registry=fx.registry(), backtest=True)
    assert entry.expected == {} and entry.idea_name == IDEA and entry.backtest is True
    raw = _good_raw()
    raw["expected"] = {}
    assert corpus_mod.load_file(_write(tmp_path, raw), registry=fx.registry(), backtest=True).expected == {}
    # IDEA_NAMES falls back to the entry's own name (FR-1); a golden entry is unchanged
    assert vs.founder_idea_name(entry) == IDEA and vs.founder_inputs(entry).idea_name == IDEA
    assert vs.idea_name(entry) == "whistle key tag"
    golden = fx.entry(fx.ENTRY_B2B)
    assert golden.idea_name is None and golden.backtest is False
    assert vs.founder_idea_name(golden) == vs.short_name(golden)


def test_a_person_s_own_follow_up_replaces_the_pooled_line_and_golden_entries_keep_the_pool(tmp_path):
    """062 follow-up (2026-10-22): `follow_up:` on a person is their own answer to the one follow-up the interview owes
    them; a person owed none keeps None, a person without the key keeps the harness's pooled line; golden unchanged."""
    raw = _good_raw()
    owed_before = {p.person: p.follow_up for p in vs.person_inputs(
        corpus_mod.load_file(_write(tmp_path, raw), registry=fx.registry(), backtest=True)) if p.follow_up}
    assert owed_before, "the fixture owes at least one follow-up"
    first, *rest = sorted(owed_before)
    for person in raw["answers"]:
        if person["person"] == first:
            person["follow_up"] = "Mine, in my own words."
    entry = corpus_mod.load_file(_write(tmp_path, raw), registry=fx.registry(), backtest=True)
    after = {p.person: p.follow_up for p in vs.person_inputs(entry)}
    assert after[first] == "Mine, in my own words."
    assert all(after[name] == owed_before[name] for name in rest)
    not_owed = [p.person for p in vs.person_inputs(entry) if not p.follow_up]
    if not_owed:
        for person in raw["answers"]:
            if person["person"] == not_owed[0]:
                person["follow_up"] = "Never asked, never typed."
        entry = corpus_mod.load_file(_write(tmp_path, raw), registry=fx.registry(), backtest=True)
        assert {p.person: p.follow_up for p in vs.person_inputs(entry)}[not_owed[0]] is None
    golden = fx.entry(fx.ENTRY_B2B)
    assert all(p.follow_up is None for p in golden.people())


def test_a_backtest_entry_carries_no_golden_expectations(tmp_path):
    raw = _good_raw()
    raw["expected"] = fx.raw_entry(fx.ENTRY_B2B)["expected"]
    said = _refusal(_write(tmp_path, raw))
    assert "98-good: carries `expected`; a back-test entry has no golden expectations" in said, said


@pytest.mark.parametrize("name, said", [
    (None, "idea_name is None"), ("", "idea_name is ''"),
    ("A whistle tag for every key ring", "is 7 words; the founder's name for the idea is at most 5"),
])
def test_a_backtest_entry_names_its_idea_in_at_most_five_words(tmp_path, name, said):
    raw = _good_raw()
    if name is None:
        raw.pop("idea_name")
    else:
        raw["idea_name"] = name
    assert said in _refusal(_write(tmp_path, raw))


@pytest.mark.parametrize("key", corpus_mod.BACKTEST_KEYS)
def test_a_golden_entry_never_carries_a_backtest_key(tmp_path, key):
    raw = fx.raw_entry(fx.ENTRY_B2B)
    raw[key] = _good_raw()[key]
    assert f"carries `{key}`, a back-test key (spec 062)" in _refusal(_write(tmp_path, raw), backtest=False)


def test_entry_for_reads_the_backtest_directory_and_the_golden_load_never_does(tmp_path):
    keel_cloud = tmp_path / "keel-cloud"
    directory = corpus_mod.backtest_dir(keel_cloud)
    directory.mkdir(parents=True)
    assert vs.load(keel_cloud, backtest=True).entries == []          # empty: an empty corpus, never a refusal
    _write(directory, _good_raw())
    (directory / "98-good.sources.md").write_text("ignored by the loader\n", encoding="utf-8")
    (directory / "README.md").write_text("ignored too\n", encoding="utf-8")
    corpus, entry = vs.entry_for(keel_cloud, "98-good", backtest=True)
    assert entry.id == "98-good" and Path(corpus.directory) == directory and len(corpus.entries) == 1
    with pytest.raises(vs.VectorsScriptError, match="no back-test entry '05-paidly'"):
        vs.entry_for(keel_cloud, "05-paidly", backtest=True)
    with pytest.raises(corpus_mod.CorpusError, match="no corpus at"):
        vs.entry_for(keel_cloud, "98-good")                          # the golden reader never looks there
    assert corpus_mod.backtest_dir(KEEL_CLOUD).parent == corpus_mod.corpus_dir(KEEL_CLOUD).parent


# ------------------------------------------------------------------------------------- FR-2: door and key

def test_the_key_refusal_is_one_sentence_and_reads_presence_only():
    said = bt.refusal({})
    assert said and bt.KEY_VAR in said and said.count(". ") == 0
    assert bt.refusal({bt.KEY_VAR: "  "}) == said
    assert bt.refusal({bt.KEY_VAR: "sk-not-a-key"}) is None
    assert bt.entry_refusal({}) and bt.entry_refusal({bt.ENTRY_VAR: "08-x"}) is None
    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    assert said in makefile, "the Makefile's refusal and the runner's are the same sentence"


def test_the_backtest_founder_is_outside_fake_for():
    assert not bt.in_fake_for(bt.IDENTITY_EMAIL, bt.FAKE_FOR_DEFAULT)
    assert bt.in_fake_for("eval-founder@keel-e2e-eval.test", bt.FAKE_FOR_DEFAULT)
    assert bt.in_fake_for(bt.IDENTITY_EMAIL, "keel-e2e-eval.test, Backtest@Keel-Backtest.test")
    assert bt.IDENTITY_NAME == "Backtest Founder" and bt.IDENTITY_EMAIL == "backtest@keel-backtest.test"
    assert bt.fake_for({}) == bt.FAKE_FOR_DEFAULT and bt.fake_for({bt.FAKE_FOR_VAR: ""}) == ""


def test_watched_people_are_one_a_link_who_see_every_screen():
    people = vs.person_inputs(fx.entry(fx.ENTRY_B2B))
    watched = bt.watched_people(people)
    assert set(watched) == {p.link for p in people}
    first = next(p for p in people if p.person == watched["PRIMARY"])
    assert first.recency and first.story and not first.anchor_chip
    assert watched["COMMERCIAL_B2B"] == next(p.person for p in people if p.link == "COMMERCIAL_B2B")


# ------------------------------------------------------------------------------------- FR-3: the ungated export

def test_the_export_runs_ungated_on_a_backtest(tmp_path):
    from tests import test_sample_export as t                      # the 060 fixture and its journey
    try:
        entry = vs.entry_for(KEEL_CLOUD, "05-paidly")[1]
    except Exception as missing:  # noqa: BLE001
        pytest.skip(f"the corpus is not readable here: {missing}")
    bad = t._fault(t._seeded(), "label")
    with pytest.raises(se.SampleRefused):
        se.export_sample(t._journey(tmp_path / "a", bad, entry), tmp_path / "a" / "out")
    result = se.export_sample(t._journey(tmp_path / "b", bad, entry), tmp_path / "b" / "out", gated=False)
    assert result["card"]["decision"] != se.DECISION_LABEL and (tmp_path / "b" / "out" / se.MANIFEST).is_file()
    assert result["people"] == 20


# ------------------------------------------------------------------------------------- FR-4: the transcript

def test_the_markdown_has_the_five_sections_and_asserts_nothing():
    record = {"run": "20261022T000000Z-backtest-00-x", "passed": True, "wall_s": 12.0,
              "entry": {"id": "00-x", "title": "X", "idea_name": IDEA},
              "brief": bt.brief(json.loads((REPO / "tests" / "fixtures" / "sample" / "s006-reads.json")
                                          .read_text(encoding="utf-8"))["standings"]),
              "founder_screens": [{"n": 1, "screen": "name", "file": "screens/founder-01-name.png",
                                   "question": "What should we call this project?", "answer": "X"}],
              "respondents": {"PRIMARY": {"person": "A", "served": {"kind": "FULL", "parts": [
                  {"part": 1, "items": [{"question": "Q?", "dimension": "problem.importance", "control": "pick_two",
                                         "options": ["a", "b"], "escape": "Not sure"}]}]},
                                          "screens": ["screens/respondent-primary-01-intro.png"]}},
              "readings": [{"person": "A", "link": "PRIMARY", "file anchoring": "ANCHORED",
                            "model anchoring": "GUESSED", "same": False}],
              "cost": {"usd": 1.23, "micro_usd": 1230000, "jobs": 3, "models": ["m"], "by_class": {}},
              "screenshots": {"founder": 1, "respondent": {"PRIMARY": 1}}, "legs": [{"leg": "leg_x", "seconds": 1.0}]}
    md = bt.markdown(record)
    for heading in ("## 1. Founder screens", "## 2. Respondent questions", "## 3. The brief", "## 4. Readings",
                    "## 5. Cost and time"):
        assert heading in md
    assert "**BUILD_BUT_CHANGE**" in md and "Proof that it saves time every month" in md
    assert "| A | PRIMARY |" in md and "screens/founder-01-name.png" in md
    assert bt.brief({})["decision"]["label"] is None


# ------------------------------------------------------------------------------------- FR-5: nothing else moves

def test_no_directory_run_collects_the_backtest():
    runner = REPO / "evals" / "run_backtest.py"
    assert runner.is_file()
    assert not any(fnmatch.fnmatch(runner.name, pattern) for pattern in ("test_*.py", "*_test.py"))
    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    target = makefile.split("\nbacktest:\n", 1)[1].split("\n\n", 1)[0]
    assert "evals/run_backtest.py" in target and "KEEL_BACKTEST_ENTRY=$(ENTRY)" in target
    for name in ("eval: venv", "eval-live: venv", "unit: venv", "sample: venv"):
        body = makefile.split(f"\n{name}\n", 1)[1].split("\n\n", 1)[0]
        assert "backtest" not in body, name


def test_the_matrix_never_names_the_backtest():
    for path in (REPO / "matrix").rglob("*"):
        if path.is_file() and path.suffix in (".py", ".toml", ".yml", ".yaml"):
            assert "backtest" not in path.read_text(encoding="utf-8").lower(), path


def test_the_paid_command_is_documented_and_marks_version_stays_20():
    agents = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    assert "make backtest" in agents and "spec 062" in agents
    assert instruction_marks.MARKS_VERSION == 20
