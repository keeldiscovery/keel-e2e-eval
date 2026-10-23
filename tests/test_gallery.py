"""Spec 063: the example gallery export (`evals/gallery.py`) -- stackless, over a trimmed copy of one back-test run.

`tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/` is the run of record for 08-fresco (spec 062's
`runs/20261022T164045Z-backtest-08-fresco`), cut down to what the export reads: `backtest.json`'s `spec`, `run`,
`passed`, `failed_step`, `entry`, `stack` and `respondents`; `inputs.json`'s `founder`; `export/` with the seven top
reads, one batch and one invitation (its manifest listing those nine); and `transcript.jsonl`'s follow-up steps (every
200, one 204), each cut to `name`, `request` and the response's `person` and `link`. `expected-interview-fresco.json`
pins FR-3a's interview.json on it.

FR-4 as the amendment of record (2026-10-23) leaves it: the attribution check (it replaces the rename and its
survivors grep) -- `inspiredBy`, `publicDescription` with URL and date, `simulated`, the fixed disclaimer and the
assumptions, alike in the index row and the manifest, each refusing when missing; the index shape; the file set per
slug, interview.json included and its shape pinned; provenance kept out of every byte under OUT (FR-3, 2026-10-22).
060/061's tests (`test_sample_export.py`) are untouched.
"""

from __future__ import annotations

import dataclasses
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
PINNED = FIXTURES / "expected-interview-fresco.json"
AT = "2026-10-22T20:00:00Z"
FRESCO_DISCLAIMER = ("A simulated study inspired by Fresco (Y Combinator Fall 2024). The founder's answers, the twenty "
                     "participants and everything they said are fictional, written from Fresco's public material to "
                     "show what Keel does. Not customer research about Fresco; not affiliated with Fresco or Y "
                     "Combinator.")


@pytest.fixture(scope="module")
def names():
    return g.load_names()


@pytest.fixture()
def exported(tmp_path, names):
    out = tmp_path / "sample"
    result = g.export([RUN], out, names=names, exported_at=AT, provenance_dir=tmp_path / "runs" / "gallery")
    return out, result


def _with(names, entry, **changes):
    return [dataclasses.replace(n, **changes) if n.entry == entry else n for n in names]


# ------------------------------------------------------------------------------------------ the map (2026-10-23)

def test_the_map_is_the_amendments(names):
    assert [(n.entry, n.slug, n.name, n.replaces, n.inspired_by["batch"]) for n in names] == [
        ("08-fresco", "fresco", "Fresco", (), "Fall 2024"),
        ("09-karsa", "karsa", "Karsa", (), "Winter 2025"),
        ("10-palus", "palus-finance", "Palus Finance", (), "Winter 2026"),
        ("11-issen", "issen", "Issen", (), "Fall 2024"),
        ("12-transload", "transload", "Transload", (), "Spring 2026"),
        ("13-aircaps", "aircaps", "AirCaps", (), "Fall 2025"),
    ]
    for n in names:
        assert n.inspired_by == {"name": n.name, "batch": n.inspired_by["batch"],
                                 "ycUrl": f"https://www.ycombinator.com/companies/{n.slug}"}
        # launch-era (1d42c51): the Launch YC post's own title, its URL and its date
        assert n.public_description["url"].startswith("https://www.ycombinator.com/launches/")
        assert n.public_description["date"] < "2026-10-22" and n.public_description["text"].strip() and not n.axes
        if n.status_today:                                              # today's one-liner, where it differs
            assert n.status_today["url"] == n.inspired_by["ycUrl"] and n.status_today["date"] == "2026-10-22"
            assert n.status_today["text"] != n.public_description["text"]
    assert [n.slug for n in names if not n.status_today] == ["aircaps"]
    assert names[0].public_description == {
        "text": "Fresco: The scribe for construction",
        "url": "https://www.ycombinator.com/launches/M73-fresco-the-scribe-for-construction", "date": "2024-10-23"}


def test_a_malformed_map_is_refused_by_name(tmp_path):
    bad = tmp_path / "names.toml"
    bad.write_text('[[gallery]]\nentry = "08-fresco"\nslug = "Fres Co"\nname = "Fresco"\nreplaces = ["Fresco"]\n'
                   '[[gallery]]\nentry = "08-fresco"\nslug = "fresco"\nname = "Fresco"\nreplaces = []\n'
                   'axes = {mood = "calm"}\n', encoding="utf-8")
    with pytest.raises(g.GalleryRefused) as refused:
        g.load_names(bad)
    said = " ".join(refused.value.reasons)
    assert "slug 'Fres Co'" in said and "replaces must be []" in said and "['mood']" in said
    assert "entry repeated" in said and "name repeated" in said


def test_the_disclaimer_is_the_fixed_sentence(names):
    assert names[0].disclaimer() == FRESCO_DISCLAIMER
    palus = next(n for n in names if n.entry == "10-palus")
    assert palus.disclaimer().startswith("A simulated study inspired by Palus Finance (Y Combinator Winter 2026).")
    assert "written from Palus Finance's public material" in palus.disclaimer()


# ---------------------------------------------------------------------------------- the attribution check

def test_the_attribution_in_the_index_and_the_manifest(exported):
    out, _ = exported
    row = json.loads((out / g.INDEX).read_text(encoding="utf-8"))["examples"][0]
    manifest = json.loads((out / "fresco" / se.MANIFEST).read_text(encoding="utf-8"))
    want = {"inspiredBy": {"name": "Fresco", "batch": "Fall 2024", "ycUrl": "https://www.ycombinator.com/companies/fresco"},
            "publicDescription": {"text": "Fresco: The scribe for construction",
                                  "url": "https://www.ycombinator.com/launches/M73-fresco-the-scribe-for-construction",
                                  "date": "2024-10-23"},
            "statusToday": {"text": "AI copilot for construction estimators",
                            "url": "https://www.ycombinator.com/companies/fresco", "date": "2026-10-22"},
            "simulated": True, "disclaimer": FRESCO_DISCLAIMER}
    for block in (row, manifest):
        assert {k: block[k] for k in want} == want
        assert block["assumptions"][0] == ("Nearly all of these construction superintendents had this at least once "
                                           "in the last 5 working days.")
        assert block["assumptions"][-1] == "Most are open to start a paid pilot on one site now."
        assert len(block["assumptions"]) == 13 and all(isinstance(a, str) for a in block["assumptions"])
    standings = json.loads((RUN / "export" / "standings.json").read_text(encoding="utf-8"))
    beliefs = [d["belief"] for v in standings["vectors"] for d in v["dimensions"] if d.get("belief")]
    assert row["assumptions"] == beliefs                              # as the run served them


@pytest.mark.parametrize("change, said", [
    ({"inspired_by": {}}, "inspiredBy needs name, batch and ycUrl"),
    ({"inspired_by": {"name": "Fresco", "batch": "Fall 2024", "ycUrl": "https://fresco-ai.com/"}},
     "is not a YC company page"),
    ({"public_description": {"text": "AI copilot for construction estimators", "url": "", "date": "2026-10-22"}},
     "publicDescription needs text, url and date"),
    ({"public_description": {"text": "x", "url": "https://www.ycombinator.com/companies/fresco", "date": "October"}},
     "publicDescription url"),
    ({"public_description": {}}, "publicDescription needs text, url and date"),
    ({"status_today": {"text": "AI copilot for construction estimators", "url": "", "date": "2026-10-22"}},
     "statusToday needs text, url and date"),
    ({"status_today": {"text": "x", "url": "https://www.ycombinator.com/companies/fresco", "date": "today"}},
     "statusToday url"),
])
def test_a_slug_missing_its_attribution_is_refused_and_nothing_is_written(tmp_path, names, change, said):
    out = tmp_path / "sample"
    with pytest.raises(g.GalleryRefused) as refused:
        g.export([RUN], out, names=_with(names, "08-fresco", **change), exported_at=AT,
                 provenance_dir=tmp_path / "prov")
    assert any(said in r for r in refused.value.reasons), refused.value.reasons
    assert all(r.startswith("fresco: ") for r in refused.value.reasons)
    assert not out.exists() and not (tmp_path / "prov").exists()


def test_the_clusters_are_the_diversity_researchs(names):
    assert [(n.slug, n.cluster["id"], n.cluster["label"]) for n in names] == [
        ("fresco", 4, "Construction and real estate"),
        ("karsa", 27, "Payments, banking, lending, stablecoins"),
        ("palus-finance", 27, "Payments, banking, lending, stablecoins"),
        ("issen", 29, "Education and tutoring"),
        ("transload", 16, "Supply chain, logistics, freight"),
        ("aircaps", 6, "Consumer video, media and creators")]


def test_keywords_are_derived_when_the_map_writes_none(names):
    run = g.read_run(RUN)
    words = g.keywords(run, dataclasses.replace(names[0], keywords=()), occasion="day")
    assert g.KEYWORDS_MIN <= len(words) <= g.KEYWORDS_MAX and words[:2] == ["construction superintendent", "day"]
    assert all(w == w.lower() and w.strip() for w in words) and not any("fresco" in w for w in words)
    assert not set(words[2:]) & g._STOP                  # the actor and the occasion are taken as served
    for n in names:                                       # the map's lists: 5 to 12, lower case, no company name
        assert g.KEYWORDS_MIN <= len(n.keywords) <= g.KEYWORDS_MAX
        assert all(k == k.lower() and n.name.lower() not in k for k in n.keywords)


@pytest.mark.parametrize("change, said", [
    ({"cluster": {}}, "cluster needs an integer id and a label"),
    ({"cluster": {"id": "4", "label": "Construction and real estate"}}, "cluster needs an integer id"),
    ({"keywords": ("site", "photos", "logs", "trailer")}, "4 keywords, not 5 to 12"),
    ({"keywords": (" ", "photos", "logs", "trailer", "dispute")}, "not plain lower-case"),
    ({"keywords": ("fresco app", "photos", "logs", "trailer", "dispute")}, "a keyword names the company"),
])
def test_a_slug_without_its_cluster_or_keywords_is_refused(tmp_path, names, change, said):
    with pytest.raises(g.GalleryRefused) as refused:
        g.export([RUN], tmp_path / "sample", names=_with(names, "08-fresco", **change), exported_at=AT,
                 provenance_dir=tmp_path / "prov")
    assert any(said in r for r in refused.value.reasons), refused.value.reasons
    assert not (tmp_path / "sample").exists()


def test_status_today_is_optional(tmp_path, names):
    out = tmp_path / "sample"
    g.export([RUN], out, names=_with(names, "08-fresco", status_today={}), exported_at=AT,
             provenance_dir=tmp_path / "prov")
    row = json.loads((out / g.INDEX).read_text(encoding="utf-8"))["examples"][0]
    manifest = json.loads((out / "fresco" / se.MANIFEST).read_text(encoding="utf-8"))
    assert "statusToday" not in row and "statusToday" not in manifest and row["publicDescription"]["text"]


def test_a_missing_disclaimer_simulated_or_assumptions_is_refused(names):
    run = g.read_run(RUN)
    s = g.prepare(names[0], run, exported_at=AT)
    assert g.attribution_reasons(s) == []
    for key, value, said in (("disclaimer", None, "the disclaimer is missing"),
                             ("disclaimer", "A simulated study.", "not the fixed sentence"),
                             ("simulated", False, "simulated is not true"),
                             ("assumptions", [], "no assumptions")):
        broken = dataclasses.replace(s, row={**s.row, key: value})
        reasons = g.attribution_reasons(broken)
        assert any(said in r for r in reasons) and any("differently" in r for r in reasons), reasons


def test_a_run_without_twenty_people_is_refused(tmp_path, names):
    run = tmp_path / RUN.name
    shutil.copytree(RUN, run)
    path = run / "export" / "invitations.json"
    register = json.loads(path.read_text(encoding="utf-8"))
    register["invitations"] = register["invitations"][:19]
    path.write_text(json.dumps(register), encoding="utf-8")
    with pytest.raises(g.GalleryRefused, match="invited 19 people; the disclaimer says twenty"):
        g.export([run], tmp_path / "sample", names=names, exported_at=AT, provenance_dir=tmp_path / "prov")


def test_the_060_withholding_still_refuses(tmp_path, names):
    run = tmp_path / RUN.name
    shutil.copytree(RUN, run)
    people = run / "export" / "people.json"
    payload = json.loads(people.read_text(encoding="utf-8"))
    payload["Backtest Founder"] = 1                                     # the founder, where withholding can't reach
    people.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(g.GalleryRefused) as refused:
        g.export([run], tmp_path / "sample", names=names, exported_at=AT, provenance_dir=tmp_path / "prov")
    assert any("survive the withholding" in r for r in refused.value.reasons)


def test_nothing_is_renamed(exported):
    out, _ = exported
    run = g.read_run(RUN)
    for key, payload in run.reads.items():
        assert json.loads((out / "fresco" / f"{key}.json").read_text(encoding="utf-8")) == payload
    assert "Fresco" in (out / "fresco" / "overview.json").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------------------------- FR-1 the index

def test_the_index_shape(exported):
    out, result = exported
    written = json.loads((out / g.INDEX).read_text(encoding="utf-8"))
    assert written == {"generatedAt": AT, "count": 1, "examples": result["index"]}      # a35af52's envelope
    row = written["examples"][0]
    assert list(row) == ["slug", "name", "inspiredBy", "publicDescription", "statusToday", "simulated", "disclaimer",
                         "oneLine",
                         "problem", "assumptions", "decision", "howSure", "pilot", "price", "b2b", "cloud", "web",
                         "axes", "cluster", "keywords", "interview"]
    assert row["slug"] == "fresco" and row["name"] == "Fresco" and row["b2b"] is True
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
    assert row["cluster"] == {"id": 4, "label": "Construction and real estate"}
    assert row["keywords"] == ["construction superintendent", "site walks", "daily logs", "photos", "punch lists",
                               "documents", "trailer", "liability", "dispute", "general contractors"]
    roles = json.loads((out / "fresco" / "roles.json").read_text(encoding="utf-8"))["roles"]
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
    on_disk = sorted(str(p.relative_to(out / "fresco")) for p in (out / "fresco").rglob("*") if p.is_file())
    assert on_disk == sorted([*listed, "interview.json", se.MANIFEST])
    assert sorted(p.name for p in out.iterdir()) == ["fresco", "index.json"]
    assert result["slugs"]["fresco"]["written"] == [*listed, "interview.json"]


def test_the_manifest_shape(exported):
    out, _ = exported
    manifest = json.loads((out / "fresco" / se.MANIFEST).read_text(encoding="utf-8"))
    assert list(manifest) == ["cloud", "web", "exportedAt", "inspiredBy", "publicDescription", "statusToday",
                              "simulated", "disclaimer", "assumptions"]
    assert (manifest["cloud"], manifest["web"], manifest["exportedAt"]) == ("b2cf168", "9f3845a", AT)


def test_the_provenance_is_written_once_outside_out(exported, tmp_path):
    out, result = exported
    path = tmp_path / "runs" / "gallery" / f"provenance-{AT}.json"
    assert result["provenance"] == str(path) and out not in path.parents
    assert json.loads(path.read_text(encoding="utf-8")) == [{
        "slug": "fresco", "entry": "08-fresco", "run": RUN.name, "cloud": "b2cf168", "web": "9f3845a",
        "renamed": {"from": [], "to": "Fresco"}}]
    assert (REPO / ".gitignore").read_text(encoding="utf-8").splitlines().count("runs/") == 1


def test_no_byte_under_out_carries_provenance(exported, names):
    out, _ = exported
    everything = b"".join(p.read_bytes() for p in sorted(out.rglob("*")) if p.is_file()).decode("utf-8").lower()
    for needle in ("08-fresco", RUN.name.lower(), "backtest", "/users/", "renamed"):
        assert needle not in everything, needle
    assert g.provenance_under(out, ["08-fresco", RUN.name, "-backtest-"]) == []


def test_provenance_already_under_out_refuses_and_nothing_is_written(tmp_path, names):
    out = tmp_path / "sample"
    out.mkdir()
    (out / "notes.txt").write_text("made from 08-fresco", encoding="utf-8")
    with pytest.raises(g.GalleryRefused) as refused:
        g.export([RUN], out, names=names, exported_at=AT, provenance_dir=tmp_path / "prov")
    assert refused.value.reasons == ["already under OUT: notes.txt: ['08-fresco']"]
    assert sorted(p.name for p in out.iterdir()) == ["notes.txt"] and not (tmp_path / "prov").exists()
    with pytest.raises(g.GalleryRefused, match="is under OUT"):
        g.export([RUN], out, names=names, exported_at=AT, provenance_dir=out / "gallery")


def test_the_interview_is_pinned_on_one_run(exported):
    out, _ = exported
    written = json.loads((out / "fresco" / "interview.json").read_text(encoding="utf-8"))
    assert written == json.loads(PINNED.read_text(encoding="utf-8"))
    primary, decider = written["links"]
    assert list(primary) == ["role", "label", "kind", "occasion", "idea", "gate", "storyPrompt", "storyHint", "parts",
                             "reveal", "followUp"]
    assert (primary["kind"], decider["kind"]) == ("FULL", "COMMERCIAL_LINK")
    assert primary["gate"]["chips"] == [{"code": "CANT_RECALL", "label": "I can't recall one particular day"}]
    assert primary["reveal"]["what"] == "Imagine Fresco." and decider["idea"]["what"] == "Imagine Fresco."
    item = primary["parts"][1]["items"][1]
    assert list(item)[:9] == ["dimension", "kicker", "question", "control", "hint", "options", "advantages", "escape",
                              "shown"]
    assert item["question"] == "On your last day, would Fresco have made things better, or not?"
    assert item["kicker"] == "Part 2 of 2 · An idea to consider · 2 of 3"
    assert decider["followUp"]["asked"][0] == {"dimension": "commercial.commitment",
                                               "question": "What would you start with instead?"}


def test_the_interview_withholds_ids_tokens_and_media(exported):
    out, _ = exported
    text = (out / "fresco" / "interview.json").read_text(encoding="utf-8")
    keys = set(g._keys(json.loads(text)))
    assert not keys & g._DROPPED
    assert "withheld" not in text and "/i/" not in text and "@" not in text
    assert not any(w in text.lower() for w in (".mp4", ".webm", "clip", "face", "recording"))


def test_a_rerun_replaces_the_slug_and_keeps_the_root_files(tmp_path, names):
    out = tmp_path / "sample"
    out.mkdir()
    (out / "standings.json").write_text("{}", encoding="utf-8")     # `make sample`'s root files stay (FR-1)
    g.export([RUN], out, names=names, exported_at=AT, provenance_dir=tmp_path / "prov")
    stale = out / "fresco" / "readings" / "gone.json"
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
    assert "fresco" in said and "08-fresco" not in said and (tmp_path / "out" / "index.json").is_file()
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
