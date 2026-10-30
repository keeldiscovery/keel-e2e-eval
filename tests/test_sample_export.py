"""Spec 060: the sample export (`evals/sample_export.py`) -- stackless, over a recorded fixture of S-006's reads.

`tests/fixtures/sample/s006-reads.json` is what the founder session received from the finished 05-paidly project at
its twenty answers on the local stack (`runs/<id>-s006-paidly/sample-reads.json`, the run of `make sample` that
spec 060's tasks.md names), unedited but for one seeded link and one seeded address (`_seeded`) -- the wire carries
neither on these routes today, and FR-2 must still hold if a later contract adds one.

Acceptance 1: the withholding test (FR-2: a grep of the whole output against the founder, emails and tokens; since spec
061 the entry's twenty people's names must be there, as served) and a shape test (every file FR-1 names is written). Then the gate (FR-3) green on the fixture and red on each seeded fault
with its reason named and nothing written, the manifest (FR-4), and FR-5's two invariants.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

from evals import sample_export as se
from harness import vectors_script as vs
from harness.steps import Recorder
from instructions import marks as instruction_marks
from stack.config import load_config
from stack.stub_oidc.identity import FOUNDER_A

REPO = Path(__file__).resolve().parent.parent
FIXTURE = REPO / "tests" / "fixtures" / "sample" / "s006-reads.json"
KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
PROJECT = "00000000-0000-0000-0000-000000000060"
TOKEN = "seededToken0060abcdef"
SEEDED_EMAIL = "seeded.person@example.com"
#: Spec 061: 05-paidly's twenty scripted people, as the spec names them -- the translators, then the agencies.
TWENTY = ("Nadia Petrova", "Omar Farouk", "Petra Novak", "Quentin Roux", "Rosa Alvarez", "Sven Larsen",
          "Talia Ben-David", "Umar Siddiqui", "Vera Kowalski", "Wen Zhang", "Xavier Dubois", "Yara Haddad",
          "Kate Alder", "Mo Birch", "Sara Cedar", "Tariq Dune", "Uma Elm", "Viktor Fern", "Wanda Gorse", "Yusuf Hazel")


@pytest.fixture(scope="module")
def entry():
    try:
        return vs.entry_for(KEEL_CLOUD, "05-paidly")[1]
    except Exception as missing:  # noqa: BLE001 - no keel-cloud beside the checkout
        pytest.skip(f"the corpus is not readable here: {missing}")


def _seeded() -> dict:
    reads = json.loads(FIXTURE.read_text(encoding="utf-8"))
    first = se.invitation_ids(reads["invitations"])[0]
    reads[f"invitations/{first}"]["url"] = f"http://localhost:5183/i/{TOKEN}"
    reads["invitations"]["invitations"][0]["email"] = SEEDED_EMAIL
    return reads


@pytest.fixture()
def reads() -> dict:
    return _seeded()


def _journey(tmp_path: Path, reads: dict, entry) -> SimpleNamespace:
    base = f"/v2/projects/{PROJECT}/"

    def get(path: str):
        assert path.startswith(base), path
        return copy.deepcopy(reads[path[len(base):]])

    return SimpleNamespace(recorder=Recorder(tmp_path / "run"), get=get, project_id=PROJECT, entry=entry,
                           people=vs.person_inputs(entry), founder_identity=FOUNDER_A,
                           tokens={"someone": TOKEN}, stack=SimpleNamespace(keel_cloud=KEEL_CLOUD))


def _people(entry) -> list[str]:
    return [p.person for p in vs.person_inputs(entry)]


def _output(out: Path) -> str:
    return "".join(p.read_text(encoding="utf-8") for p in sorted(out.rglob("*.json")))


# ------------------------------------------------------------------------------------------------ FR-1 shape

def test_the_fixture_is_s006s_twenty_answers(reads, entry):
    assert (reads["standings"].get("people") or {}).get("answered") == 20
    assert len(se.invitation_ids(reads["invitations"])) == 20
    assert se.batch_ids(reads["readings"]), "the fixture lists no reading batch"
    assert set(se.expected_keys(reads)) == set(reads)


def test_every_file_fr1_names_is_written(tmp_path, reads, entry):
    out = tmp_path / "sample"
    result = se.export_sample(_journey(tmp_path, reads, entry), out, run_dir=tmp_path)
    want = [f"{k}.json" for k in se.expected_keys(reads)]
    assert sorted(result["manifest"]["files"]) == sorted(want)
    for name in ("overview", "plan", "standings", "roles", "people", "readings", "invitations"):
        assert (out / f"{name}.json").is_file(), name
    for batch in se.batch_ids(reads["readings"]):
        assert (out / "readings" / f"{batch}.json").is_file(), batch
    for invitation in se.invitation_ids(reads["invitations"]):
        assert (out / "invitations" / f"{invitation}.json").is_file(), invitation
    on_disk = sorted(str(p.relative_to(out)) for p in out.rglob("*.json"))
    assert on_disk == sorted([*want, se.MANIFEST])
    # the reads as received go to the run bundle, never beside the snapshot
    assert (tmp_path / "sample-reads.json").is_file()
    assert result["size"] == sum(p.stat().st_size for p in out.rglob("*.json"))


def test_paths_mirror_the_founder_api_with_the_id_removed(reads):
    seen = []
    se.capture(lambda path: seen.append(path) or copy.deepcopy(reads[path.split(f"{PROJECT}/", 1)[1]]), PROJECT)
    assert seen == [f"/v2/projects/{PROJECT}/{k}" for k in se.expected_keys(reads)]


def test_the_manifest(tmp_path, reads, entry):
    out = tmp_path / "sample"
    se.export_sample(_journey(tmp_path, reads, entry), out)
    manifest = json.loads((out / se.MANIFEST).read_text(encoding="utf-8"))
    assert list(manifest) == ["entry", "corpus", "exportedAt", "cloud", "files"]
    assert manifest["entry"] == "05-paidly" and manifest["corpus"] == entry.revision
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", manifest["exportedAt"])
    assert manifest["cloud"] is None or re.fullmatch(r"[0-9a-f]{40}", manifest["cloud"])
    assert manifest["files"][:7] == [f"{k}.json" for k in se.TOP_READS]


def test_a_rerun_removes_what_the_last_manifest_listed_and_nothing_else(tmp_path, reads, entry):
    out = tmp_path / "sample"
    out.mkdir()
    (out / "keep.txt").write_text("not ours", encoding="utf-8")
    (out / "readings").mkdir()
    (out / "readings" / "old-batch.json").write_text("{}", encoding="utf-8")
    (out / se.MANIFEST).write_text(json.dumps({"files": ["readings/old-batch.json", "../escape.json"]}),
                                   encoding="utf-8")
    (tmp_path / "escape.json").write_text("{}", encoding="utf-8")
    se.export_sample(_journey(tmp_path, reads, entry), out)
    assert not (out / "readings" / "old-batch.json").exists()
    assert (out / "keep.txt").is_file() and (tmp_path / "escape.json").is_file()


# --------------------------------------------------------------------------------------------- FR-2 withheld

def test_names_kept_and_no_email_founder_or_token_survives(tmp_path, reads, entry):
    """FR-2's acceptance (spec 061 FR-2): every one of the entry's twenty names IS in the whole output, and no email,
    founder word or token is."""
    out = tmp_path / "sample"
    result = se.export_sample(_journey(tmp_path, reads, entry), out)
    written = _output(out)
    raw = json.dumps(reads, ensure_ascii=False)
    people = _people(entry)
    assert sorted(people) == sorted(TWENTY), "the entry's people are not the twenty spec 061 names"
    assert TOKEN in raw and SEEDED_EMAIL in raw
    for name in TWENTY:
        assert re.search(rf"(?<!\w){re.escape(name)}(?!\w)", written), name
    assert not re.search(r"Person \d+", written)
    assert result["people"] == 20
    for word in (FOUNDER_A.name, FOUNDER_A.email, TOKEN, SEEDED_EMAIL):
        assert word not in written, word
    assert not re.search(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", written)
    assert '"email"' not in written
    assert not re.search(r"/i/[A-Za-z0-9_\-]{8,}", written)
    assert se.WITHHELD in written


def test_people_json_keeps_every_name_in_its_order(reads, entry):
    done = se.withhold(reads)
    on_people = [row["personName"] for role in reads["people"]["roles"] for row in role["invitations"]]
    assert sorted(on_people) == sorted(TWENTY)
    kept = [row["personName"] for role in done.reads["people"]["roles"] for row in role["invitations"]]
    assert kept == on_people
    # stable: the same reads give the same output
    assert se.withhold(reads).reads == done.reads


def test_one_person_is_one_name_in_every_file(reads, entry):
    done = se.withhold(reads)
    for invitation in se.invitation_ids(reads["invitations"]):
        original = reads[f"invitations/{invitation}"]["personName"]
        assert done.reads[f"invitations/{invitation}"]["personName"] == original
    pilot = done.reads["standings"].get("pilotPeople") or []
    assert [row["name"] for row in pilot] == [row["name"] for row in reads["standings"].get("pilotPeople") or []]
    for row in pilot:
        assert row["name"] in TWENTY, row["name"]


def test_withholding_leaves_everything_else_as_served(reads, entry):
    done = se.withhold(reads)
    assert done.reads["standings"]["vectors"][0]["vector"] == reads["standings"]["vectors"][0]["vector"]
    assert done.reads["standings"]["facts"]["decision"] == reads["standings"]["facts"]["decision"]
    assert done.reads["standings"]["priceMedian"] == reads["standings"]["priceMedian"]
    assert done.reads["standings"]["pilot"] == reads["standings"]["pilot"]
    assert done.reads["overview"] == reads["overview"]


def test_names_untouched_and_the_founder_dropped():
    reads = {"people": {"roles": [{"invitations": [{"personName": "Uma Elm"}]}]},
             "x": {"story": "Uma Elmore met Uma Elm; Eval Founder said so.", "owner": "Eval Founder",
                   "contact": "eval-founder@keel-e2e-eval.test", "token": "abc"}}
    done = se.withhold(reads, founder_name="Eval Founder", founder_email="eval-founder@keel-e2e-eval.test")
    assert done.reads["x"]["story"] == "Uma Elmore met Uma Elm;  said so."
    assert done.reads["people"] == reads["people"]
    assert "owner" not in done.reads["x"] and "contact" not in done.reads["x"]
    assert done.reads["x"]["token"] == se.WITHHELD


def test_survivors_finds_each_kind_and_never_a_name():
    left = se.survivors('{"a": "Kate Alder", "b": "x@y.io", "c": "tok123456789", "d": "Eval Founder"}',
                        founder_name="Eval Founder", founder_email="e@f.test", tokens=["tok123456789"])
    assert set(left) == {"emails", "tokens", "founder"}
    assert se.names_kept('{"a": "Kate Alder", "b": "Uma Elmore"}', ["Kate Alder", "Uma Elm"]) == ["Kate Alder"]


# ----------------------------------------------------------------------------------------------- FR-3 gate

def test_the_gate_passes_on_s006s_reads(reads, entry):
    reasons, measured = se.gate(reads, entry.expected)
    assert reasons == []
    assert measured["card"]["decision"] == se.DECISION_LABEL
    assert measured["verdicts"] == {"PROBLEM": "HOLDING_UP", "SOLUTION": "HOLDING_UP", "COMMERCIAL": "NOT_HOLDING_UP"}
    assert measured["card"]["pilot"]["finished"] == 20 and measured["card"]["price"]["edgeSaid"]


def test_the_spec_floor_of_ten_is_reported_not_gated(reads, entry):
    """Judgement call 1: 05-paidly's commercial stage is its eight decision-makers, so FR-3's n >= 10 is measured
    and named, and the gate holds each dimension to the entry's own n."""
    _, measured = se.gate(reads, entry.expected)
    want_under = sorted(k for k, v in entry.expected["standings"].items() if v["n"] < se.SPEC_MIN_N)
    assert measured[f"under {se.SPEC_MIN_N}"] == want_under
    assert "commercial.price" in want_under


def _fault(reads: dict, what: str) -> dict:
    bad = copy.deepcopy(reads)
    standings = bad["standings"]
    if what == "label":
        standings["facts"]["decision"]["label"] = "NOT_YET"
    elif what == "pilot":
        standings["pilot"] = None
    elif what == "price":
        standings["priceMedian"] = None
    elif what == "n":
        standings["vectors"][2]["dimensions"][0]["n"] = 7
    elif what == "verdict":
        standings["vectors"][2]["verdict"] = "HOLDING_UP"
    elif what == "not asked":
        standings["vectors"][0]["dimensions"][1]["status"] = "NOT_ASKED_YET"
    return bad


@pytest.mark.parametrize("what, said", [
    ("label", "decision label"), ("pilot", "pilot count"), ("price", "price line"), ("n", "the corpus expects 8"),
    ("verdict", "COMMERCIAL reads"), ("not asked", "was not asked"),
])
def test_the_gate_refuses_by_name_and_writes_nothing(tmp_path, reads, entry, what, said):
    bad = _fault(reads, what)
    reasons, _ = se.gate(bad, entry.expected)
    assert reasons and any(said in r for r in reasons), reasons
    out = tmp_path / "sample"
    with pytest.raises(se.SampleRefused) as refused:
        se.export_sample(_journey(tmp_path, bad, entry), out)
    assert any(said in r for r in refused.value.reasons)
    assert not out.exists() or not any(out.rglob("*"))


def test_a_refusal_fails_the_run_after_the_journey(tmp_path, reads, entry):
    pending = se.Pending(out_dir=tmp_path / "sample", run_dir=tmp_path)
    pending.take(_journey(tmp_path, _fault(reads, "label"), entry))
    assert json.loads((tmp_path / "sample.json").read_text())["refused"]
    with pytest.raises(pytest.fail.Exception, match="decision label"):
        pending.settle()
    with pytest.raises(pytest.fail.Exception, match="never ran"):
        se.Pending(out_dir=tmp_path / "other").settle()


# ------------------------------------------------------------------------------------------- FR-4 / FR-5

def test_only_the_variable_turns_it_on():
    assert se.wanted({}) is None and se.wanted({se.EXPORT_VAR: "  "}) is None
    assert se.wanted({se.EXPORT_VAR: "/tmp/sample"}) == Path("/tmp/sample")
    assert se.pending(env={}) is None
    assert se.pending(env={se.EXPORT_VAR: "/tmp/sample"}).out_dir == Path("/tmp/sample")


def test_make_sample_and_make_eval():
    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    target = makefile.split("\nsample: venv\n", 1)[1].split("\n\n", 1)[0]
    assert "KEEL_SAMPLE_EXPORT" in target and '"public" / "sample"' in target and "-k s006" in target
    eval_target = makefile.split("\neval: venv\n", 1)[1].split("\n\n", 1)[0]
    assert "KEEL_SAMPLE_EXPORT" not in eval_target


def test_s006_takes_the_export_only_when_asked():
    source = (REPO / "evals" / "test_s006_paidly.py").read_text(encoding="utf-8")
    assert "sample_export.pending(run_dir)" in source and "if sample is not None:" in source
    # the export is taken before the contacts leg (twenty answers), and settled after the journey
    assert source.index("sample.take(j)") < source.index("contacts_leg.leg_contacts(j)")
    assert source.index("corpus_scenario.run(") < source.index("sample.settle()")


def test_marks_version_is_22():
    """Spec 078 moved MARKS_VERSION 20 -> 21 (the `read` mark kind, reported, never gating); spec 093 21 -> 22 (`L1`,
    `L5`); the export moved nothing."""
    assert instruction_marks.MARKS_VERSION == 22
