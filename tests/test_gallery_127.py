"""Spec 127 -- the gallery admits an entry on its mean (the acceptance gate loosened).

The founder, 2026-11-01: *"If it's above 84%, we can accept it ... let it be the entry mean rather than a single
project."* `quality/cycle.toml [gallery] entry_mean_pct = 84.0`; with `--scores` an entry is an example when its three
studies each have a score file and the mean of their three `score_pct` is at or above the line (FR-1); a flagged screen
no longer refuses, a missing score file still does; the provenance carries each study's `score_pct`, the mean and the
flagged screens, and `promote` says the summary line (FR-2); spec 106 FR-3's cycle gate stands (FR-3).

The score files here are real ones' shape: cycle 7's `17-expanse` SOLUTION file (`quality/scores/`, read only) with its
header rewritten and its overall `score_pct` set; cycle 7's own five entries are read on their committed files.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evals import gallery as g
from quality import cycle, rubric
from tests.test_gallery_106 import AT, LATER, study_run

REPO = Path(__file__).resolve().parent.parent
SCORES = REPO / "quality" / "scores"
CYCLE7 = REPO / "quality" / "cycles" / "20261102-7021fd5.md"
REAL = SCORES / "17-expanse" / "20261102-SOLUTION-r3-7021fd5-v16-claude-opus-5-5.json"
STAMPS = {"problem": "T10", "solution": "T11", "money": "T12"}


@pytest.fixture(autouse=True)
def _no_decisions(monkeypatch, tmp_path):
    monkeypatch.setattr(cycle, "DECISIONS", tmp_path / "no-decisions.toml")


def real_score(scores: Path, run: Path, pct: float, *, zero: tuple[int, str] | None = None,
               scored_at: str = "2026-11-02T02:10:07+00:00") -> Path:
    """A score file of `run` in the real file's shape (cycle 7's Expanse solution file), its overall `score_pct` set to
    `pct`; `zero` = (the screen's `n`, a criterion) gives that screen a 0 -- a flagged screen."""
    obj = json.loads(REAL.read_text(encoding="utf-8"))
    record = json.loads((run / "backtest.json").read_text(encoding="utf-8"))
    obj.update(entry=record["entry"]["id"], scope=record["scope"], bundle=run.name, scored_at=scored_at)
    if zero:
        screen = next(s for s in obj["screens"] if s["n"] == zero[0] and s["audience"] == "founder")
        screen[zero[1]] = 0
        flags = sum(1 for s in obj["screens"] if rubric.flagged(s))
        obj["summary"]["overall"]["flagged"] = obj["summary"]["founder"]["flagged"] = flags
    obj["summary"]["overall"]["score_pct"] = pct
    path = scores / obj["entry"] / f"{run.name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")
    rubric.load_file(path)                                         # the readers' own check passes it
    return path


def entry_runs(root: Path, entry: str, pcts, scores: Path, *, day: str = "20261102", unscored=(), zero=None):
    """One entry's three studies (problem, solution, money), each scored at its `pcts` but `unscored` studies; `zero` =
    (study, the screen's `n`, a criterion) flags that screen of that study."""
    runs = []
    for study, pct in zip(g.STUDIES, pcts):
        run = study_run(root, entry, study, f"{day}{STAMPS[study]}{entry[:2]}000Z")
        if study not in unscored:
            real_score(scores, run, pct, zero=zero[1:] if zero and zero[0] == study else None)
        runs.append(run)
    return runs


def real_screen(n: int) -> dict:
    return next(s for s in json.loads(REAL.read_text(encoding="utf-8"))["screens"] if s["n"] == n)


# ------------------------------------------------------------------------------------------- FR-1 the line

def test_the_line_is_committed_in_cycle_toml_and_read_by_both_commands():
    assert cycle.load_config()["gallery"]["entry_mean_pct"] == 84.0
    assert g.entry_mean_line() == 84.0
    text = (REPO / "quality" / "cycle.toml").read_text(encoding="utf-8").split("[gallery]", 1)[1]
    assert "entry_mean_pct = 84.0" in text and "If it's above 84%" in text, "committed with its why"
    assert cycle.load_config()["bar_pct"] == rubric.BAR_PCT == 90.0, "FR-3: the bar is untouched"


@pytest.mark.parametrize("line", ["", "entry_mean_pct = \"high\"", "entry_mean_pct = 120.0", "entry_mean_pct = true"])
def test_a_line_absent_or_not_a_percentage_is_refused_by_name(tmp_path, line):
    text = (REPO / "quality" / "cycle.toml").read_text(encoding="utf-8").replace("entry_mean_pct = 84.0", line)
    path = tmp_path / "cycle.toml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(cycle.Refused, match=r"\[gallery\] entry_mean_pct is .*\(spec 127 FR-1"):
        cycle.load_config(path)
    with pytest.raises(g.GalleryRefused, match=r"entry_mean_pct is .* not a percentage"):
        g.entry_mean_line(path)


@pytest.mark.parametrize("pcts, admitted, shown", [
    ((84.0, 84.0, 84.0), True, "84.0"),                 # at the line
    ((83.0, 84.0, 85.0), True, "84.0"),                 # at the line, on the mean (no study need reach it)
    ((81.7, 83.6, 90.7), True, "85.3"),                 # above
    ((81.7, 83.6, 86.5), False, "83.9"),                # below (cycle 7's Fresco)
    ((83.9, 84.0, 84.0), False, "83.97"),               # below by a hair: never shown as 84.0
])
def test_an_entry_is_admitted_on_its_mean_at_or_above_the_line(tmp_path, pcts, admitted, shown):
    scores = tmp_path / "scores"
    runs = entry_runs(tmp_path / "runs", "10-palus", pcts, scores)
    passing, refused, by_entry = g.entry_gate(runs, scores, line=84.0)
    info = by_entry["10-palus"]
    assert info["accepted"] is admitted and passing == (runs if admitted else [])
    assert {s: v["score_pct"] for s, v in info["studies"].items()} == dict(zip(g.STUDIES, pcts))
    assert g.mean_text(info["mean"], 84.0) == shown
    if admitted:
        assert refused == []
    else:
        figures = ", ".join(f"{s} {p}" for s, p in zip(g.STUDIES, pcts))
        assert refused == [f"10-palus {shown} < 84.0 -- the mean of its three studies' score_pct ({figures}) is under "
                           "the entry's line (spec 127 FR-1); the gallery keeps what it holds for it"]


def test_the_mean_is_exact_and_shown_to_one_decimal():
    assert g.mean_text(86.9, 84.0) == "86.9" and g.mean_text(83.2666, 84.0) == "83.3"
    assert g.mean_text(83.97, 84.0) == "83.97" and g.mean_text(83.999, 84.0) == "83.999"
    assert g.mean_text(84.0, 84.0) == "84.0"


def test_a_flagged_screen_no_longer_refuses_and_travels_in_the_provenance(tmp_path):
    scores, said = tmp_path / "scores", []
    runs = entry_runs(tmp_path / "runs", "17-expanse", (87.2, 87.5, 86.0), scores, zero=("money", 5, "r2"))
    result = g.promote(runs, tmp_path / "sample", scores_dir=scores, cycle="20261102-7021fd5",
                       provenance_dir=tmp_path / "prov", exported_at=AT, say=said.append)
    assert not any(line.startswith("refused") for line in said)
    assert said[-1] == "1 entry accepted on a mean of at least 84.0, 0 refused"
    assert [r["slug"] for r in result["index"]] == ["expanse"]
    row = json.loads(Path(result["provenance"]).read_text(encoding="utf-8"))["examples"][0]
    assert row["flagged"] == [{"study": "money", "screen": real_screen(5)["screen"], "criterion": "r2", "n": 5,
                               "audience": "founder"}]


@pytest.mark.parametrize("criterion", ["r1", "r3", "r5"])
def test_each_zero_is_one_flag_by_study_screen_and_criterion(tmp_path, criterion):
    scores = tmp_path / "scores"
    runs = entry_runs(tmp_path / "runs", "17-expanse", (87.2, 87.5, 86.0), scores, zero=("solution", 1, criterion))
    passing, refused, by_entry = g.entry_gate(runs, scores, line=84.0)
    assert refused == [] and passing == runs and by_entry["17-expanse"]["accepted"] is True
    assert by_entry["17-expanse"]["flagged"] == [{"study": "solution", "screen": real_screen(1)["screen"],
                                                  "criterion": criterion, "n": 1, "audience": "founder"}]


def test_a_missing_score_file_still_refuses_the_study_and_its_entry(tmp_path):
    scores, said = tmp_path / "scores", []
    runs = entry_runs(tmp_path / "runs", "17-expanse", (99.0, 99.0, 99.0), scores, unscored=("money",))
    with pytest.raises(g.NothingToBuild):
        g.promote(runs, tmp_path / "sample", scores_dir=scores, provenance_dir=tmp_path / "prov", exported_at=AT,
                  say=said.append)
    assert said[0] == (f"refused {runs[2].name} (17-expanse · COMMERCIAL): no score file at rubric version "
                       f"{rubric.RUBRIC_VERSION} under {scores} -- a bundle the readers have not passed is not an "
                       "example")
    assert any(line.startswith("refused 17-expanse: no money study (COMMERCIAL)") for line in said)
    assert said[-1] == ("0 entries accepted on a mean of at least 84.0, 1 refused "
                        "(17-expanse no mean (money not scored))")
    assert not (tmp_path / "sample").exists() and not (tmp_path / "prov").exists()


# ------------------------------------------------------------------------------- FR-2 provenance and summary

def test_the_provenance_records_each_studys_score_the_mean_the_flags_and_the_line(tmp_path):
    scores = tmp_path / "scores"
    runs = (entry_runs(tmp_path / "runs", "08-fresco", (81.7, 83.6, 86.5), scores)
            + entry_runs(tmp_path / "runs", "17-expanse", (87.2, 87.5, 86.0), scores, zero=("problem", 2, "r4")))
    result = g.promote(runs, tmp_path / "sample", scores_dir=scores, cycle="20261102-7021fd5",
                       provenance_dir=tmp_path / "prov", exported_at=AT, say=lambda _: None)
    data = json.loads(Path(result["provenance"]).read_text(encoding="utf-8"))
    assert data["accepted"] == {"cycle": "20261102-7021fd5", "score_pct": data["accepted"]["score_pct"],
                                "rubric_version": rubric.RUBRIC_VERSION, "entry_mean_pct": 84.0}
    (row,) = data["examples"]
    assert row["entry"] == "17-expanse" and row["slug"] == "expanse"
    assert {s: v["score_pct"] for s, v in row["studies"].items()} == {"problem": 87.2, "solution": 87.5, "money": 86.0}
    assert row["mean"] == 86.9
    assert row["flagged"] == [{"study": "problem", "screen": real_screen(2)["screen"], "criterion": "r4", "n": 2,
                               "audience": "founder"}]
    assert set(row["flagged"][0]) == {"study", "screen", "criterion", "n", "audience"}
    # nothing of it under OUT: no entry id, no run name (the export's own check, read here once more)
    under = b"".join(p.read_bytes() for p in (tmp_path / "sample").rglob("*") if p.is_file()).decode().lower()
    assert "17-expanse" not in under and all(r.name.lower() not in under for r in runs)


def test_the_summary_line_names_the_refused_with_their_means(tmp_path):
    scores, said = tmp_path / "scores", []
    runs = (entry_runs(tmp_path / "runs", "10-palus", (80.8, 83.9, 84.2), scores)
            + entry_runs(tmp_path / "runs", "17-expanse", (87.2, 87.5, 86.0), scores)
            + entry_runs(tmp_path / "runs", "21-codyco", (90.0, 90.0, 90.0), scores, unscored=("solution",)))
    g.promote(runs, tmp_path / "sample", scores_dir=scores, provenance_dir=tmp_path / "prov", exported_at=AT,
              say=said.append)
    assert "refused 10-palus 83.0 < 84.0 -- the mean of its three studies' score_pct (problem 80.8, solution 83.9, " \
           "money 84.2) is under the entry's line (spec 127 FR-1); the gallery keeps what it holds for it" in said
    assert said[-1] == ("1 entry accepted on a mean of at least 84.0, 2 refused (10-palus 83.0, "
                        "21-codyco no mean (solution not scored))")
    two = g.entry_summary({"a": {"mean": 85.0, "missing": []}, "b": {"mean": 90.0, "missing": []}}, ["a", "b"], 84.0)
    assert two == "2 entries accepted on a mean of at least 84.0, 0 refused"


def test_a_refused_entry_keeps_its_older_example_and_a_slug_with_none_stays_absent(tmp_path):
    scores, out = tmp_path / "scores", tmp_path / "sample"
    (out / "palus-finance").mkdir(parents=True)
    (out / "palus-finance" / "standings.json").write_text('{"old": true}')
    old = {"slug": "palus-finance", "name": "Palus", "b2b": True, "decision": "OLD", "title": "Palus, as it was"}
    (out / "index.json").write_text(json.dumps({"examples": [old, {"slug": "karsa", "b2b": True}]}))
    runs = (entry_runs(tmp_path / "runs", "10-palus", (80.8, 83.9, 84.2), scores)
            + entry_runs(tmp_path / "runs", "13-aircaps", (83.0, 85.5, 81.3), scores)
            + entry_runs(tmp_path / "runs", "17-expanse", (87.2, 87.5, 86.0), scores))
    result = g.promote(runs, out, scores_dir=scores, cycle="20261102-7021fd5", provenance_dir=tmp_path / "prov",
                       exported_at=LATER, say=lambda _: None)
    index = json.loads((out / "index.json").read_text(encoding="utf-8"))["examples"]
    assert [r["slug"] for r in index] == ["palus-finance", "karsa", "expanse"], \
        "FR-5: every older row in its place (karsa, not in the cycle, too), the new slug appended"
    assert index[0] == old and index[1] == {"slug": "karsa", "b2b": True}, "the older examples stay as they were"
    assert (out / "palus-finance" / "standings.json").read_text() == '{"old": true}'
    assert not (out / "aircaps").exists(), "a refused slug with no example stays absent"
    assert result["kept"] == ["palus-finance", "karsa"] and list(result["slugs"]) == ["expanse"]
    data = json.loads(Path(result["provenance"]).read_text(encoding="utf-8"))
    assert data["kept"] == ["palus-finance", "karsa"] and [r["slug"] for r in data["examples"]] == ["expanse"]


def test_a_cycle_of_two_entries_leaves_twelve_existing_rows_untouched(tmp_path):
    """FR-5 (the founder's rule, 2026-11-01: the gallery grows by new entries only; a certified entry is never re-walked
    just to stay in): a gallery of fourteen, a cycle walking two of them -- one refreshed in place, one refused: the
    twelve others' rows and folders are byte for byte as they were, in their order (a new slug appends:
    `test_a_refused_entry_keeps_its_older_example_and_a_slug_with_none_stays_absent`)."""
    scores, out = tmp_path / "scores", tmp_path / "sample"
    names = g.load_names()
    gallery = names[:14]
    rows = [{"slug": n.slug, "name": n.name, "b2b": i % 2 == 0, "decision": "OLD", "title": f"{n.name}, certified"}
            for i, n in enumerate(gallery)]
    for n in gallery:
        (out / n.slug / "problem").mkdir(parents=True)
        (out / n.slug / "problem" / "standings.json").write_text(json.dumps({"slug": n.slug}))
    (out / "index.json").write_text(json.dumps({"generatedAt": AT, "count": len(rows), "examples": rows}))
    walked = {"08-fresco": (90.0, 90.0, 90.0), "10-palus": (80.8, 83.9, 84.2)}
    assert {n.entry for n in gallery} >= {"08-fresco", "10-palus"} and len(gallery) == 14
    others = [n.slug for n in gallery if n.entry not in walked]
    assert len(others) == 12
    before = {p: p.read_bytes() for s in others for p in (out / s).rglob("*") if p.is_file()}
    runs = [r for entry, pcts in walked.items() for r in entry_runs(tmp_path / "runs", entry, pcts, scores)]
    result = g.promote(runs, out, scores_dir=scores, cycle="20261102-7021fd5", provenance_dir=tmp_path / "prov",
                       exported_at=LATER, say=lambda _: None)
    index = json.loads((out / "index.json").read_text(encoding="utf-8"))["examples"]
    assert [r["slug"] for r in index] == [n.slug for n in gallery], "every row in its place"
    for i, n in enumerate(gallery):
        if n.slug != "fresco":
            assert index[i] == rows[i], n.slug                 # the twelve, and refused palus, untouched
    assert index[0]["slug"] == "fresco" and index[0]["decision"] != "OLD" and index[0]["title"] == "Fresco, certified"
    assert {p: p.read_bytes() for s in others for p in (out / s).rglob("*") if p.is_file()} == before
    assert list(result["slugs"]) == ["fresco"] and len(result["kept"]) == 13


# ------------------------------------------------------------------------------------------- FR-3 the cycle gate

def test_the_cycle_gate_stands_over_entries_above_the_line(tmp_path):
    scores, out, prov = tmp_path / "scores", tmp_path / "sample", tmp_path / "prov"
    g.promote(entry_runs(tmp_path / "a", "17-expanse", (95.0, 95.0, 95.0), scores), out, scores_dir=scores,
              cycle="c1", score_pct=95.0, provenance_dir=prov, exported_at=AT, say=lambda _: None)
    before = {p: p.read_bytes() for p in out.rglob("*") if p.is_file()}
    with pytest.raises(g.GalleryRefused) as refused:
        g.promote(entry_runs(tmp_path / "b", "17-expanse", (90.0, 90.0, 90.0), scores, day="20261109"), out,
                  scores_dir=scores, cycle="c2", score_pct=90.0, provenance_dir=prov, exported_at=LATER,
                  say=lambda _: None)
    assert "below the gallery's last accepted 95.0%" in refused.value.reasons[0]
    assert {p: p.read_bytes() for p in out.rglob("*") if p.is_file()} == before


def test_accept_hands_the_committed_line_to_the_gallery():
    source = (REPO / "quality" / "cycle.py").read_text(encoding="utf-8")
    body = source.split("\ndef accept(argv=None) -> int:\n", 1)[1].split("\ndef _snapshot_slugs", 1)[0]
    assert 'entry_mean_pct=cfg["gallery"]["entry_mean_pct"]' in body
    assert body.index("gallery.gate(") < body.index("table.cut_baseline(")
    assert "ENTRY_MEAN" in (REPO / "Makefile").read_text(encoding="utf-8").split("\ngallery: venv\n", 1)[1] \
        .split("\n\n", 1)[0]


# ------------------------------------------------------------------------------- cycle 7, on its own score files

def test_cycle_7_admits_expanse_alone_on_its_committed_score_files(tmp_path):
    """The acceptance's expectation on cycle 7's five entries (`quality/cycles/20261102-7021fd5.md`, the score files
    under `quality/scores/`, read only): Expanse 86.9 accepted; Fresco 83.9, AirCaps 83.3, Palus 83.0, Codyco 83.9
    refused. The bundles are stand-ins named as the record names them (the gate reads their entry, scope and name)."""
    record = cycle.load_record(CYCLE7)
    runs = []
    for s in record["studies"]:
        stamp = s["bundle"].split("-backtest-", 1)[0]
        study = g.SCOPE_STUDY[s["scope"]]
        run = study_run(tmp_path / "runs", s["entry"], study, stamp)
        assert run.name == s["bundle"]
        runs.append(run)
    passing, refused, by_entry = g.entry_gate(runs, SCORES, line=84.0)
    assert {e: g.mean_text(i["mean"], 84.0) for e, i in by_entry.items()} == {
        "08-fresco": "83.9", "10-palus": "83.0", "13-aircaps": "83.3", "17-expanse": "86.9", "21-codyco": "83.9"}
    assert [e for e, i in by_entry.items() if i["accepted"]] == ["17-expanse"]
    assert [p.name for p in passing] == [s["bundle"] for s in record["studies"] if s["entry"] == "17-expanse"]
    assert [r.split(" -- ")[0] for r in refused] == ["08-fresco 83.9 < 84.0", "10-palus 83.0 < 84.0",
                                                     "13-aircaps 83.3 < 84.0", "21-codyco 83.9 < 84.0"]
    assert g.entry_summary(by_entry, ["17-expanse"], 84.0) == (
        "1 entry accepted on a mean of at least 84.0, 4 refused (08-fresco 83.9, 10-palus 83.0, 13-aircaps 83.3, "
        "21-codyco 83.9)")
    # the flags travel: Expanse's solution study has none, its problem and money studies two each
    assert {f["study"] for f in by_entry["17-expanse"]["flagged"]} == {"problem", "money"}
