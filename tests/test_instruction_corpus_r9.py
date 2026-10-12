"""Corpus revision 9's additions, through the one reader (spec 035 T002, FR-006; `MARKS_VERSION` 17, call 80).

Revision 9 (keel-cloud 083) moves no entry -- they are revision 8's byte for byte -- and adds `chat/*.yaml` and
`verdicts/six-scenarios.yaml`. The reader hashes both on the way in, takes `check_corpus_r9.py`'s rule V at load and
rule C against the registry the export carries, and refuses a directory without them by name as v16's.
The tests that read keel-cloud's canon skip, by name, when the configured checkout is not at revision 9."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from instructions import corpus as corpus_mod
from instructions import registry as registry_mod
from stack.config import load_config
from tests import v9_fixtures as fx

REGISTRY_JSON = Path("src") / "main" / "resources" / "keel" / "dimension-registry.json"


def canon():
    keel_cloud = load_config(validate=False).keel_cloud
    fx.canon_entry("03-lullaby.yaml")                                  # skips, by name, below revision 9
    return keel_cloud


def real_registry(keel_cloud):
    path = Path(keel_cloud) / REGISTRY_JSON
    registry = registry_mod.load(path, check=False)
    if not any(d.chat for d in registry.dimensions):
        pytest.skip("keel-cloud's registry carries no chat blocks (version < 3)")
    return registry


def test_the_corpus_is_revision_nine_over_revision_eights_entries():
    assert corpus_mod.REVISION == 9 and corpus_mod.ENTRY_REVISION == 8


def test_the_real_additions_are_read_hashed_and_checked_against_the_registry():
    keel_cloud = canon()
    corpus = corpus_mod.load(keel_cloud)
    assert [i.id for i in corpus.chat] == ["dark-chocolate", "lullaby", "payroll", "superior-chocolate",
                                           "voice-notes", "writing-checker"]
    assert sum(len(i.cases) for i in corpus.chat) == 41
    assert len(corpus.scenarios) == 7
    hashed = {Path(p).name for p in corpus.hashes}
    assert "six-scenarios.yaml" in hashed and "payroll.yaml" in hashed and "03-lullaby.yaml" in hashed
    corpus.bind(real_registry(keel_cloud))                              # rule C, against the export's registry
    corpus.verify_unchanged()


def test_the_cases_carry_the_corpus_labels_the_marks_read():
    corpus = corpus_mod.load(canon())
    payroll = corpus.idea("payroll")
    current = next(c for c in payroll.cases if c.dimension == "problem.current_solution_satisfaction")
    assert current.follow_up is True and current.measure == "TIME" and current.respondent == "band_ladder"
    assert sum(1 for i in corpus.chat for c in i.cases if c.leaves_out) == 3
    assert sum(1 for i in corpus.chat for c in i.cases if c.follow_up) == 5


def write_dir(tmp_path):
    keel_cloud = tmp_path / "keel-cloud"
    directory = corpus_mod.corpus_dir(keel_cloud)
    directory.mkdir(parents=True)
    fx.write_entry(directory, fx.raw_entry(), "02-new.yaml")
    return keel_cloud, directory


def test_a_directory_without_the_additions_is_revision_eights_whole_and_refused_by_name(tmp_path):
    keel_cloud, _directory = write_dir(tmp_path)
    with pytest.raises(corpus_mod.CorpusError) as refusal:
        corpus_mod.load(keel_cloud)
    said = str(refusal.value)
    assert "MARKS_VERSION 16's corpus (revision 8)" in said and "chat/*.yaml" in said
    assert "six-scenarios.yaml" in said and "corpus revision 9" in said


def test_the_additions_load_beside_the_entries_and_are_hashed(tmp_path):
    keel_cloud, directory = write_dir(tmp_path)
    fx.write_additions(directory)
    corpus = corpus_mod.load(keel_cloud)
    assert [e.id for e in corpus.entries] == ["09-fixture"] and len(corpus.chat) == 1
    assert {Path(p).name for p in corpus.hashes} >= {"fixture.yaml", "six-scenarios.yaml", "02-new.yaml"}
    (directory / "chat" / "fixture.yaml").write_text("id: x\ncases: []\n")
    with pytest.raises(corpus_mod.CorpusError, match="changed while the run was in flight"):
        corpus.verify_unchanged()


def test_an_entry_at_another_revision_is_still_refused_before_the_additions_are_looked_for(tmp_path):
    keel_cloud, directory = write_dir(tmp_path)
    fx.write_entry(directory, dict(fx.raw_entry(), id="08-old", revision=7), "08-old.yaml")
    with pytest.raises(corpus_mod.CorpusError) as refusal:
        corpus_mod.load(keel_cloud)
    assert "revision is 7" in str(refusal.value) and "MARKS_VERSION 13's and 14's" in str(refusal.value)


@pytest.mark.parametrize("mutate, words", [
    (lambda d: d["cases"][0].__setitem__("follow_up", "no"), "follow_up is not a boolean"),
    (lambda d: d["cases"][0].pop("measure"), "`measure` is a non-empty string"),
    (lambda d: d.__setitem__("cases", []), "a list of `cases`"),
    (lambda d: d.pop("id"), "an `id`"),
])
def test_a_malformed_chat_file_is_refused_by_name(tmp_path, mutate, words):
    keel_cloud, directory = write_dir(tmp_path)
    fx.write_additions(directory)
    path = directory / "chat" / "fixture.yaml"
    raw = yaml.safe_load(path.read_text())
    mutate(raw)
    path.write_text(yaml.safe_dump(raw))
    with pytest.raises(corpus_mod.CorpusError) as refusal:
        corpus_mod.load(keel_cloud)
    assert words in str(refusal.value)


def test_six_scenarios_must_be_seven_each_with_its_rows_and_the_three_vectors(tmp_path):
    keel_cloud, directory = write_dir(tmp_path)
    fx.write_additions(directory)
    path = directory / "verdicts" / "six-scenarios.yaml"
    raw = yaml.safe_load(path.read_text())
    raw["scenarios"].pop()
    path.write_text(yaml.safe_dump(raw))
    with pytest.raises(corpus_mod.CorpusError, match="6 scenarios, not seven"):
        corpus_mod.load(keel_cloud)
    raw = yaml.safe_load(fx_scenarios())
    raw["scenarios"][0]["expect"]["problem.frequency"]["status"] = "WIBBLE"
    path.write_text(yaml.safe_dump(raw))
    with pytest.raises(corpus_mod.CorpusError, match="WIBBLE"):
        corpus_mod.load(keel_cloud)
    raw = yaml.safe_load(fx_scenarios())
    raw["scenarios"][0]["verdicts"].pop("COMMERCIAL")
    path.write_text(yaml.safe_dump(raw))
    with pytest.raises(corpus_mod.CorpusError, match="not the three vectors"):
        corpus_mod.load(keel_cloud)


def fx_scenarios() -> str:
    scenario = {"expect": {"problem.frequency": {"status": "HOLDING_UP"}},
                "verdicts": {"PROBLEM": "HOLDING_UP", "SOLUTION": "HOLDING_UP", "COMMERCIAL": "HOLDING_UP"},
                "decision": "BUILD"}
    return yaml.safe_dump({"scenarios": [dict(scenario, id=f"s{i}") for i in range(7)]})


REGISTRY = {"dimensions": [
    {"key": "problem.frequency", "vector": "PROBLEM", "order": 1, "name": "Frequency", "weight": "SUPPORTING",
     "chat": {"measures": ["COUNT"], "leave_out_allowed": True,
              "respondent": {"frames": {"COUNT": "segmented_0_to_7"}}}},
    {"key": "solution.adoption_friction", "vector": "SOLUTION", "order": 2, "name": "Adoption friction",
     "weight": "DEAL_BREAKER",
     "chat": {"measures": ["EFFORT"], "leave_out_allowed": False,
              "respondent": {"frames": {"EFFORT": "effort_yes_no", "HABIT": "how_often"}}}},
    {"key": "problem.prevalence", "vector": "PROBLEM", "order": 0, "name": "Prevalence", "weight": "DEAL_BREAKER"}]}


def registry():
    return registry_mod.from_document(REGISTRY, check=False)


def idea(**over):
    case = dict(idea="x", dimension="problem.frequency", founder="f", follow_up=False, measure="COUNT",
                family=None, respondent="segmented_0_to_7")
    case.update(over)
    return [corpus_mod.ChatIdea("x", "X", False, (corpus_mod.ChatCase(**case),))]


@pytest.mark.parametrize("over, words", [
    ({}, None),
    ({"dimension": "problem.prevalence"}, "no chat block"),
    ({"dimension": "problem.nope"}, "no such registry dimension"),
    ({"measure": "TIME"}, "not in ['COUNT']"),
    ({"respondent": "band_ladder"}, "is not the frame segmented_0_to_7"),
    ({"respondent": "leave_out"}, None),
    ({"dimension": "solution.adoption_friction", "measure": "EFFORT", "respondent": "leave_out"},
     "leave_out is not allowed"),
    ({"dimension": "solution.adoption_friction", "measure": "EFFORT", "family": "HABIT",
      "respondent": "how_often"}, None),
    ({"dimension": "solution.adoption_friction", "measure": "EFFORT", "family": "HABIT",
      "respondent": "effort_yes_no"}, "is not the frame how_often"),
])
def test_rule_c_against_the_registry(over, words):
    if words is None:
        corpus_mod.check_chat(idea(**over), registry())
        return
    with pytest.raises(corpus_mod.CorpusError, match=words.replace("[", r"\[").replace("]", r"\]")):
        corpus_mod.check_chat(idea(**over), registry())


def test_the_registry_reader_carries_the_chat_block():
    assert registry().by_key("problem.frequency").chat["measures"] == ["COUNT"]
    assert registry().by_key("problem.prevalence").chat == {}
    assert json.dumps(registry().by_key("solution.adoption_friction").chat)
