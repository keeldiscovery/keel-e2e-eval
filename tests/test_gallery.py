"""Spec 063: the example gallery export (`evals/gallery.py`) -- stackless, over a trimmed copy of one back-test run.

`tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/` is the run of record for 08-fresco (spec 062's
`runs/20261022T164045Z-backtest-08-fresco`), cut down to what the export reads: `backtest.json`'s `spec`, `run`,
`passed`, `failed_step`, `entry`, `stack` and `respondents`; `inputs.json`'s `founder`; `export/` with the seven top
reads, one batch and one invitation (its manifest listing those nine); and `transcript.jsonl`'s follow-up steps (every
200, one 204), each cut to `name`, `request` and the response's `person` and `link`. `expected-interview-daylog.json`
pins FR-3a's interview.json on it.

FR-4: the rename over a fixture with the six names in mixed positions, a survivor refusing; the index shape; the file
set per slug, interview.json included and its shape pinned. 060/061's tests (`test_sample_export.py`) are untouched.
FR-3 as amended 2026-10-22: no entry id, run name or `renamed.from` under OUT; the provenance file outside it; every
byte under OUT grepped, any case, no exclusions.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from evals import backtest as bt
from evals import gallery as g
from evals import sample_export as se

REPO = Path(__file__).resolve().parent.parent
FIXTURES = REPO / "tests" / "fixtures" / "gallery"
RUN = FIXTURES / "20261022T164045Z-backtest-08-fresco"
PINNED = FIXTURES / "expected-interview-daylog.json"
OLD = ("Fresco", "Karsa", "Palus Finance", "Palus", "Issen", "Transload", "AirCaps")
AT = "2026-10-22T20:00:00Z"


@pytest.fixture(scope="module")
def names():
    return g.load_names()


@pytest.fixture(scope="module")
def renamer(names):
    return g.Renamer(names)


@pytest.fixture()
def exported(tmp_path, names):
    out = tmp_path / "sample"
    result = g.export([RUN], out, names=names, exported_at=AT, provenance_dir=tmp_path / "runs" / "gallery")
    return out, result


# ------------------------------------------------------------------------------------------------ FR-2 the map

def test_the_map_is_the_spec(names):
    assert [(n.entry, n.slug, n.name, n.replaces) for n in names] == [
        ("08-fresco", "daylog", "Daylog", ("Fresco",)),
        ("09-karsa", "dollarsafe", "Dollarsafe", ("Karsa",)),
        ("10-palus", "idlewell", "Idlewell", ("Palus Finance", "Palus")),
        ("11-issen", "talkleap", "Talkleap", ("Issen",)),
        ("12-transload", "dockmeasure", "Dockmeasure", ("Transload",)),
        ("13-aircaps", "captionglass", "Captionglass", ("AirCaps",)),
    ]
    assert all(not n.axes for n in names)          # all seven axes are derived today (judgement call 6)


def test_a_malformed_map_is_refused_by_name(tmp_path):
    bad = tmp_path / "names.toml"
    bad.write_text('[[gallery]]\nentry = "08-fresco"\nslug = "Day Log"\nname = "Daylog"\nreplaces = []\n'
                   '[[gallery]]\nentry = "08-fresco"\nslug = "daylog"\nname = "Daylog"\nreplaces = ["Fresco"]\n'
                   'axes = {mood = "calm"}\n', encoding="utf-8")
    with pytest.raises(g.GalleryRefused) as refused:
        g.load_names(bad)
    said = " ".join(refused.value.reasons)
    assert "slug 'Day Log'" in said and "replaces must be" in said and "['mood']" in said
    assert "entry repeated" in said and "name repeated" in said


MIXED = {
    "name": "Fresco",
    "statements": ["Fresco turns a site walk into notes.", "With Karsa, savers hold dollars; Karsa's fee is low.",
                   "Ask Palus Finance (or just Palus) where the reserve sits.", "Practise with Issen.",
                   "Transload: measure every shipment.", "The AirCaps glasses, paired.",
                   "a lowercase fresco, karsa, issen, transload and aircaps", "\"AirCaps\"-style quotes and FRESCO caps"],
    "nested": [{"reveal": {"what": "Imagine Transload.", "how": "Issen listens; AirCaps captions."}}],
    "kept": ["Frescoes", "Palusian", "Issenberg", "Transloading", "AirCapsule", 7, None, True],
}


def test_the_rename_over_the_six_names_in_mixed_positions(renamer):
    out = renamer.value(MIXED)
    assert out["name"] == "Daylog"
    assert out["statements"] == [
        "Daylog turns a site walk into notes.", "With Dollarsafe, savers hold dollars; Dollarsafe's fee is low.",
        "Ask Idlewell (or just Idlewell) where the reserve sits.", "Practise with Talkleap.",
        "Dockmeasure: measure every shipment.", "The Captionglass glasses, paired.",
        "a lowercase daylog, dollarsafe, talkleap, dockmeasure and captionglass",
        "\"Captionglass\"-style quotes and Daylog caps"]
    assert out["nested"] == [{"reveal": {"what": "Imagine Dockmeasure.", "how": "Talkleap listens; Captionglass captions."}}]
    assert out["kept"] == MIXED["kept"]               # whole words only; nothing else touched
    assert renamer.survivors(json.dumps(out)) == []
    assert "Idlewell Finance" not in json.dumps(out)  # the longer string first


def test_the_survivors_grep_finds_every_old_name_in_any_case(renamer):
    assert renamer.survivors(json.dumps(MIXED)) == sorted(OLD)
    assert renamer.survivors("an AIRCAPS key") == ["AirCaps"]
    assert renamer.survivors("Frescoes and Palusian") == []


def test_a_survivor_refuses_the_export_and_nothing_is_written(tmp_path, names):
    run = tmp_path / RUN.name
    shutil.copytree(RUN, run)
    overview = run / "export" / "overview.json"
    payload = json.loads(overview.read_text(encoding="utf-8"))
    payload["Fresco notes"] = "a key the rename never touches"       # keys are not text fields
    overview.write_text(json.dumps(payload), encoding="utf-8")
    out = tmp_path / "sample"
    with pytest.raises(g.GalleryRefused) as refused:
        g.export([run], out, names=names, exported_at=AT, provenance_dir=tmp_path / "prov")
    assert refused.value.reasons == ["daylog: ['Fresco'] survive the rename"]
    assert not out.exists() and not (tmp_path / "prov").exists()


def test_the_060_withholding_still_refuses(tmp_path, names):
    run = tmp_path / RUN.name
    shutil.copytree(RUN, run)
    people = run / "export" / "people.json"
    payload = json.loads(people.read_text(encoding="utf-8"))
    payload["Backtest Founder"] = 1                                     # the founder, where withholding can't reach
    people.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(g.GalleryRefused) as refused:
        g.export([run], tmp_path / "sample", names=names, exported_at=AT, provenance_dir=tmp_path / "prov")
    assert "survive the withholding" in refused.value.reasons[0]


def test_nothing_but_the_names_changes(exported, renamer):
    out, _ = exported
    run = g.read_run(RUN)
    changed = 0
    for key, payload in run.reads.items():
        written = json.loads((out / "daylog" / f"{key}.json").read_text(encoding="utf-8"))
        assert written == renamer.value(payload)
        changed += written != payload
    assert changed >= 3                                  # overview's name, plan's questions, standings' insights
    assert "Daylog" in (out / "daylog" / "overview.json").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------------------------- FR-1 the index

def test_the_index_shape(exported):
    out, result = exported
    index = json.loads((out / g.INDEX).read_text(encoding="utf-8"))
    assert index == result["index"] and len(index) == 1
    row = index[0]
    assert list(row) == ["slug", "name", "oneLine", "problem", "decision", "howSure", "pilot", "price", "b2b",
                         "cloud", "web", "axes", "interview"]
    assert row["slug"] == "daylog" and row["name"] == "Daylog" and row["b2b"] is True
    assert row["oneLine"] == "The scribe for construction superintendents"
    assert row["problem"].startswith("Construction superintendents spend up to 3 hours a day on documents")
    assert row["problem"].endswith("a dispute with the owner.") and "based on" not in row["problem"]
    assert (row["decision"], row["howSure"]) == ("NOT_YET", "MEDIUM")
    assert row["pilot"] == {"optedIn": 6, "finished": 20, "percent": 30}
    assert row["price"] == {"edgeSaid": "$250 a month", "chose": 6, "n": 8}
    assert (row["cloud"], row["web"]) == ("b2cf168", "9f3845a")
    assert list(row["axes"]) == list(g.AXES)
    assert row["axes"] == {"whoHasIt": "construction superintendent", "whoPays": "contractor",
                           "rhythm": "every working day", "costMode": "time", "priceShape": "monthly",
                           "firstStep": "start a paid pilot on one site", "kind": "business"}
    assert row["interview"] == {"links": [{"role": "PRIMARY", "label": "Construction superintendents", "items": 7},
                                          {"role": "COMMERCIAL_B2B", "label": "Contractor", "items": 6}]}
    roles = json.loads((out / "daylog" / "roles.json").read_text(encoding="utf-8"))["roles"]
    assert [l["items"] for l in row["interview"]["links"]] == [r["questionCount"] for r in roles]


def test_the_gallery_alternates_b2b_and_b2c():
    rows = [{"slug": s, "b2b": b} for s, b in
            [("a", True), ("b", True), ("c", False), ("d", True), ("e", False), ("f", False), ("g", False)]]
    assert [r["slug"] for r in g.gallery_order(rows)] == ["a", "c", "b", "e", "d", "f", "g"]


def test_axes_on_a_consumer_entry_and_the_maps_word_wins():
    run = g.read_run(RUN)
    run.record = {**run.record, "entry": {**run.record["entry"], "b2b": False}}
    run.founder = {**run.founder, "decider": {"kind": "SAME_PERSON"}, "window": {"count": 3, "unit": "MONTHS"}}
    words = g.axes(run, {"rhythm": "a few times a year"})
    assert (words["whoPays"], words["kind"], words["rhythm"]) == ("themselves", "consumer", "a few times a year")


def test_one_sentence_and_one_line():
    assert g.one_sentence("A thing breaks. It costs money; based on our talks.") == "A thing breaks."
    assert g.one_sentence("People lose 20% a year; based on the founder's family.") == "People lose 20% a year."
    assert g.one_line("Fresco — the scribe for builders") == "The scribe for builders"
    assert g.one_line("Plain") == "Plain"


# -------------------------------------------------------------------------------- FR-1/3/3a the file set per slug

def test_the_file_set_per_slug(exported):
    out, result = exported
    listed = json.loads((RUN / "export" / se.MANIFEST).read_text(encoding="utf-8"))["files"]
    on_disk = sorted(str(p.relative_to(out / "daylog")) for p in (out / "daylog").rglob("*") if p.is_file())
    assert on_disk == sorted([*listed, "interview.json", se.MANIFEST])
    assert sorted(p.name for p in out.iterdir()) == ["daylog", "index.json"]
    assert result["slugs"]["daylog"]["written"] == [*listed, "interview.json"]


def test_the_manifest_carries_only_the_shas_and_the_time(exported):
    out, _ = exported
    manifest = json.loads((out / "daylog" / se.MANIFEST).read_text(encoding="utf-8"))
    assert manifest == {"cloud": "b2cf168", "web": "9f3845a", "exportedAt": AT}


def test_the_provenance_is_written_once_outside_out(exported, tmp_path):
    out, result = exported
    path = tmp_path / "runs" / "gallery" / f"provenance-{AT}.json"
    assert result["provenance"] == str(path) and out not in path.parents
    assert json.loads(path.read_text(encoding="utf-8")) == [{
        "slug": "daylog", "entry": "08-fresco", "run": RUN.name, "cloud": "b2cf168", "web": "9f3845a",
        "renamed": {"from": ["Fresco"], "to": "Daylog"}}]
    assert (REPO / ".gitignore").read_text(encoding="utf-8").splitlines().count("runs/") == 1


def test_every_byte_under_out_is_free_of_every_old_name(exported, renamer):
    out, _ = exported
    everything = b"".join(p.read_bytes() for p in sorted(out.rglob("*")) if p.is_file()).decode("utf-8").lower()
    assert [w for w in OLD if w.lower() in everything] == []           # substring, any case: stricter than the grep
    assert g.survivors_under(out, renamer) == []
    assert "08-fresco" not in everything and "backtest" not in everything


def test_an_old_name_already_under_out_refuses_and_nothing_is_written(tmp_path, names):
    out = tmp_path / "sample"
    out.mkdir()
    (out / "notes.txt").write_text("left over from Karsa", encoding="utf-8")
    with pytest.raises(g.GalleryRefused) as refused:
        g.export([RUN], out, names=names, exported_at=AT, provenance_dir=tmp_path / "prov")
    assert refused.value.reasons == ["already under OUT: notes.txt: ['Karsa']"]
    assert sorted(p.name for p in out.iterdir()) == ["notes.txt"] and not (tmp_path / "prov").exists()
    with pytest.raises(g.GalleryRefused, match="is under OUT"):
        g.export([RUN], out, names=names, exported_at=AT, provenance_dir=out / "gallery")


def test_the_interview_is_pinned_on_one_run(exported):
    out, _ = exported
    written = json.loads((out / "daylog" / "interview.json").read_text(encoding="utf-8"))
    assert written == json.loads(PINNED.read_text(encoding="utf-8"))
    primary, decider = written["links"]
    assert list(primary) == ["role", "label", "kind", "occasion", "idea", "gate", "storyPrompt", "storyHint", "parts",
                             "reveal", "followUp"]
    assert (primary["kind"], decider["kind"]) == ("FULL", "COMMERCIAL_LINK")
    assert primary["gate"]["chips"] == [{"code": "CANT_RECALL", "label": "I can't recall one particular day"}]
    assert primary["reveal"]["what"] == "Imagine Daylog." and decider["idea"]["what"] == "Imagine Daylog."
    item = primary["parts"][1]["items"][1]
    assert list(item)[:9] == ["dimension", "kicker", "question", "control", "hint", "options", "advantages", "escape",
                              "shown"]
    assert item["question"] == "On your last day, would Daylog have made things better, or not?"
    assert item["kicker"] == "Part 2 of 2 · An idea to consider · 2 of 3"
    assert decider["followUp"]["asked"][0] == {"dimension": "commercial.commitment",
                                               "question": "What would you start with instead?"}


def test_the_interview_withholds_ids_tokens_and_media(exported):
    out, _ = exported
    text = (out / "daylog" / "interview.json").read_text(encoding="utf-8")
    keys = set(g._keys(json.loads(text)))
    assert not keys & g._DROPPED
    assert "withheld" not in text and "/i/" not in text and "@" not in text
    assert not any(w in text.lower() for w in (".mp4", ".webm", "clip", "face", "recording"))
    assert g.Renamer(g.load_names()).survivors(text) == []


def test_a_rerun_replaces_the_slug_and_keeps_the_root_files(tmp_path, names):
    out = tmp_path / "sample"
    out.mkdir()
    (out / "standings.json").write_text("{}", encoding="utf-8")     # `make sample`'s root files stay (FR-1)
    g.export([RUN], out, names=names, exported_at=AT, provenance_dir=tmp_path / "prov")
    stale = out / "daylog" / "readings" / "gone.json"
    stale.write_text("{}", encoding="utf-8")
    g.export([RUN], out, names=names, exported_at=AT, provenance_dir=tmp_path / "prov")
    assert not stale.exists() and (out / "standings.json").read_text(encoding="utf-8") == "{}"


# ------------------------------------------------------------------------------------------------- the runs

def _fake_run(root: Path, name: str, passed: bool = True) -> Path:
    d = root / name
    (d / "export").mkdir(parents=True)
    (d / bt.RECORD).write_text(json.dumps({"passed": passed}), encoding="utf-8")
    (d / "export" / se.MANIFEST).write_text("{}", encoding="utf-8")
    return d


def test_the_default_is_the_newest_finished_run_per_entry(tmp_path, names):
    for n in names:
        _fake_run(tmp_path, f"20261022T100000Z-backtest-{n.entry}")
    newest = _fake_run(tmp_path, "20261022T120000Z-backtest-08-fresco")
    _fake_run(tmp_path, "20261022T130000Z-backtest-08-fresco", passed=False)
    picked = g.newest_runs(names, tmp_path)
    assert picked[0] == newest and len(picked) == 6
    shutil.rmtree(tmp_path / "20261022T100000Z-backtest-13-aircaps")
    with pytest.raises(g.GalleryRefused, match="no finished back-test run of 13-aircaps"):
        g.newest_runs(names, tmp_path)


def test_an_unknown_entry_or_a_twice_given_one_is_refused(tmp_path, names):
    with pytest.raises(g.GalleryRefused, match="given twice"):
        g.export([RUN, RUN], tmp_path / "out", names=names, provenance_dir=tmp_path / "prov")
    with pytest.raises(g.GalleryRefused, match="is not in gallery_names.toml"):
        g.export([RUN], tmp_path / "out", names=[n for n in names if n.entry != "08-fresco"],
                 provenance_dir=tmp_path / "prov")
    assert not (tmp_path / "out").exists()


def test_the_command_line(tmp_path, capsys):
    assert g.main(["--out", str(tmp_path / "out"), "--runs", str(RUN), "--provenance-dir", str(tmp_path / "p")]) == 0
    said = capsys.readouterr().out
    assert "daylog" in said and "fresco" not in said.lower() and (tmp_path / "out" / "index.json").is_file()
    assert len(list((tmp_path / "p").glob("provenance-*.json"))) == 1
    assert g.main(["--out", str(tmp_path / "out2"), "--runs-dir", str(tmp_path)]) == 1
    assert "no finished back-test run" in capsys.readouterr().err


def test_served_items_keeps_the_item_kicker_and_spec_115s_extras():
    served = bt.served_items({"parts": [{"part": 3, "items": [{
        "itemId": "x", "dimension": "commercial.price", "control": "price_ladder", "question": "Worth?",
        "kicker": "The buying decision · 2 of 6", "options": [{"optionId": "o1", "label": "Under $250"}],
        "escape": {"code": "CANT_SAY", "label": "I can't say"}, "whatYouGet": "a, b and c",
        "plan": {"question": "And after that?", "options": [{"optionId": "p1", "label": "$10"}]}}]}]})
    item = served["parts"][0]["items"][0]
    assert item["kicker"] == "The buying decision · 2 of 6" and item["whatYouGet"] == "a, b and c"
    assert item["plan"] == {"question": "And after that?", "options": ["$10"]} and "itemId" not in item


# ---------------------------------------------------------------------------------------------- the Makefile

def test_make_gallery_and_make_sample():
    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    target = makefile.split("\ngallery: venv\n", 1)[1].split("\n\n", 1)[0]
    assert "-m evals.gallery" in target and '"public" / "sample"' in target
    assert "$(OUT)" in target and "$(RUNS)" in target and "$(RUNS_DIR)" in target
    sample = makefile.split("\nsample: venv\n", 1)[1].split("\n\n", 1)[0]
    assert "-k s006" in sample and "gallery" not in sample           # the single-run export is unchanged
    assert "gallery" in makefile.split(".PHONY:", 1)[1].split("\n\n", 1)[0]
