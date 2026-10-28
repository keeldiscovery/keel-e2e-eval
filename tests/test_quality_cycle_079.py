"""The quality cycle (spec 079): the settings, the kick-off's plan and refusals, the cycle record, TABLE.md's head, the
adviser's prompt, the acceptance and the gallery's readers' gate -- with no model, no stack, no network and no key.

The fixtures (`tests/fixtures/quality/cycle/`):

- `scores/` -- four score files over two entries: 08-fresco PROBLEM of 25 October (every screen 2: the earlier cycle and
  the baseline), and of 1 November 08-fresco PROBLEM (the stranger's Importance item turns weak on R2 -- a flagged
  screen, 88.2% under the bar; 86.7% before spec 081 gave every respondent screen an R6 of 2), 08-fresco SOLUTION and
  09-karsa COMMERCIAL (100%); all at rubric version 2;
- `BASELINE.md` -- cut from the 25 October file; `cycles/20261025-0000aaa.md` and `cycles/20261101-abcdef1.md` -- two
  records `compose` wrote, the second naming a fourth study (08-fresco COMMERCIAL) walked and never read;
- `keel-cloud/` -- a registry with two rows, `respondent-questions.md` with named sections, three entry ids.

The bundles `quality-accept` builds the gallery from are 063's fixture run (`tests/fixtures/gallery/`), copied per study
by `build_runs`, which the gate's `make quality-accept` on the fixture cycle uses as well.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from evals import backtest as bt
from evals import gallery
from quality import cycle, readers, rubric, table

REPO = Path(__file__).resolve().parent.parent
FX = Path(__file__).parent / "fixtures" / "quality" / "cycle"
SCORES_REL = "tests/fixtures/quality/cycle/scores"
SCORES = FX / "scores"
RECORD = FX / "cycles" / "20261101-abcdef1.md"
EARLIER = FX / "cycles" / "20261025-0000aaa.md"
BASELINE = FX / "BASELINE.md"
CLOUD = FX / "keel-cloud"
FRESCO_RUN = REPO / "tests" / "fixtures" / "gallery" / "20261022T164045Z-backtest-08-fresco"
WEAK_ROW = "PROBLEM · respondent · problem.importance · item"


def _score(entry: str, day: str, scope: str, sha: str = "abcdef1") -> str:
    return f"{SCORES_REL}/{entry}/{day}-{scope}-r2-{sha}-v13-claude-opus-5-5.json"


def studies_of_the_fixture() -> list[cycle.Study]:
    S = cycle.Study
    return [S("08-fresco", "PROBLEM", "20261101T100000Z-backtest-08-fresco", None, True, None,
              _score("08-fresco", "20261101", "PROBLEM"), 88.2, 33.3, 0.55, 410.0, 0.4, 120.0),
            S("08-fresco", "SOLUTION", "20261101T110000Z-backtest-08-fresco", None, True, None,
              _score("08-fresco", "20261101", "SOLUTION"), 100.0, 0.0, 0.61, 430.0, 0.4, 120.0),
            S("09-karsa", "COMMERCIAL", "20261101T120000Z-backtest-09-karsa", None, True, None,
              _score("09-karsa", "20261101", "COMMERCIAL"), 100.0, 0.0, 0.33, 300.0, 0.3, 90.0),
            S("08-fresco", "COMMERCIAL", "20261101T130000Z-backtest-08-fresco", None, True, None, None, None, None,
              0.35, 320.0, None, 30.0, "make read-screens exited 2 (see the read log)")]


def compose_the_fixture(cycles_dir: Path = FX / "cycles", baseline: Path = BASELINE) -> tuple[str, dict]:
    return cycle.compose(studies_of_the_fixture(), name="20261101-abcdef1",
                         why="the registry's Importance row moved (keel-cloud 150)", door="host", cloud_sha="abcdef1",
                         web_sha="1234567", started="2026-11-01T10:00:00+00:00", ended="2026-11-01T11:00:00+00:00",
                         seconds=3600.0, cfg=cycle.load_config(), baseline_path=baseline, cycles_dir=cycles_dir,
                         cloud_branch="master", scores_dir=SCORES_REL, entries_arg="08-fresco,09-karsa")


def build_runs(dest: str | Path) -> Path:
    """The fixture cycle's four bundles, each a copy of 063's fixture run with its name, entry and scope rewritten --
    `python -c "from tests.test_quality_cycle_079 import build_runs; build_runs('<dir>')"` for a rehearsal."""
    dest = Path(dest)
    for name, entry, scope in (("20261101T100000Z-backtest-08-fresco", "08-fresco", "PROBLEM"),
                               ("20261101T110000Z-backtest-08-fresco", "08-fresco", "SOLUTION"),
                               ("20261101T120000Z-backtest-09-karsa", "09-karsa", "COMMERCIAL"),
                               ("20261101T130000Z-backtest-08-fresco", "08-fresco", "COMMERCIAL")):
        run = dest / name
        if run.exists():
            shutil.rmtree(run)
        shutil.copytree(FRESCO_RUN, run)
        record = json.loads((run / bt.RECORD).read_text(encoding="utf-8"))
        record.update(run=name, scope=scope)
        record["entry"] = {**record["entry"], "id": entry, "path": f"backtest/{entry}.yaml"}
        (run / bt.RECORD).write_text(json.dumps(record), encoding="utf-8")
    return dest


def git_checkout(path: Path, files: dict[str, str]) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    for rel, text in files.items():
        (path / rel).parent.mkdir(parents=True, exist_ok=True)
        (path / rel).write_text(text, encoding="utf-8")
    quiet = {"capture_output": True, "check": True}
    subprocess.run(["git", "-C", str(path), "init", "-q"], **quiet)
    subprocess.run(["git", "-C", str(path), "add", "-A"], **quiet)
    subprocess.run(["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "c"], **quiet)
    return path


@pytest.fixture
def cloud(tmp_path):
    return git_checkout(tmp_path / "cloud", {"canon/designs/measured-beliefs/backtest/21-codyco.yaml": "id: 21-codyco\n",
                                             "canon/designs/measured-beliefs/backtest/08-fresco.yaml": "id: 08\n",
                                             "src/main/resources/keel/dimension-registry.json": "{}\n"})


def _pre(cloud, **kw):
    args = {"entries": ["21-codyco"], "scopes": ["PROBLEM"], "door": "keel", "why": "the founder's words",
            "build": None, "dry": False, "cloud": cloud, "env": {cycle.KEY_NAME: "set"},
            "which": lambda name: "/usr/bin/claude"}
    args.update(kw)
    return cycle.preflight(**args)


# ------------------------------------------------------------------------------------------- FR-8 the settings

def test_the_settings_are_a_committed_file_held_to_the_rubric_and_the_readers():
    cfg = cycle.load_config()
    assert cfg["scopes"] == ["PROBLEM", "SOLUTION", "COMMERCIAL"]
    assert cfg["bar_pct"] == rubric.BAR_PCT == 90.0
    assert cfg["weak"] == {"zero_entries": rubric.WEAK_ZERO_ENTRIES, "mean_under": rubric.WEAK_MEAN}
    assert {k: cfg["reader"][k] for k in ("model", "effort")} == \
        {k: readers.load_reader_config()[k] for k in ("model", "effort")}
    assert cfg["adviser"]["model"] == "claude-opus-5-5" and cfg["door"] == "keel"
    assert len(cfg["entries"]) == 5 and all(re.fullmatch(r"\d\d-[a-z0-9-]+", e) for e in cfg["entries"])
    assert cfg["gallery"]["refuse_flagged"] and cfg["gallery"]["refuse_under_bar"]
    assert cfg["gallery"]["scope_order"][0] == "SOLUTION" and cfg["cadence"]["days"] == 7
    assert "quality/cycle.toml" in (REPO / "quality" / "CYCLE.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("change, said", [
    (("bar_pct = 90.0", "bar_pct = 85.0"), "held equal"),
    (("zero_entries = 2", "zero_entries = 3"), "RUBRIC_VERSION bump"),
    (('effort = "medium"\n\n[adviser]', 'effort = "high"\n\n[adviser]'), "two files must never name two readers"),
    (('scopes = ["PROBLEM", "SOLUTION", "COMMERCIAL"]', 'scopes = ["MONEY"]'), "scopes"),
])
def test_settings_that_disagree_with_their_second_home_are_refused_by_name(tmp_path, change, said):
    text = cycle.CYCLE_TOML.read_text(encoding="utf-8")
    assert change[0] in text
    path = tmp_path / "cycle.toml"
    path.write_text(text.replace(change[0], change[1], 1), encoding="utf-8")
    with pytest.raises(cycle.Refused, match=said):
        cycle.load_config(path)


# ------------------------------------------------------------------------------------- FR-2 the kick-off

def test_no_entries_is_refused_and_default_is_the_files(capsys):
    assert cycle.walk(["--why", "w"]) == 2
    assert "make quality-walk refuses: no ENTRIES" in capsys.readouterr().err
    cfg = cycle.load_config()
    assert cycle.resolve_entries("default", cfg) == cfg["entries"]
    assert cycle.resolve_entries(" 21-codyco, 08-fresco ", cfg) == ["21-codyco", "08-fresco"]
    assert cycle.resolve_scopes("", cfg) == ["PROBLEM", "SOLUTION", "COMMERCIAL"]
    with pytest.raises(cycle.Refused, match="SCOPES"):
        cycle.resolve_scopes("problem,MONEY", cfg)


def test_a_clean_checkout_with_the_key_and_the_cli_passes(cloud):
    assert _pre(cloud) == ([], [])
    assert _pre(cloud, door="host", env={}) == ([], []), "the host door asks for no key"


def test_a_dirty_keel_cloud_checkout_is_refused_and_an_untracked_design_note_is_not(cloud):
    (cloud / "canon" / "designs" / "note.md").write_text("draft\n", encoding="utf-8")
    assert _pre(cloud) == ([], []), "an untracked note under canon/ moves no build"
    (cloud / "src" / "new.txt").write_text("x\n", encoding="utf-8")
    hard, _ = _pre(cloud)
    assert len(hard) == 1 and "is dirty" in hard[0] and "a sha must name what was measured" in hard[0]
    (cloud / "src" / "new.txt").unlink()
    (cloud / "src/main/resources/keel/dimension-registry.json").write_text('{"moved": 1}\n', encoding="utf-8")
    assert "is dirty" in _pre(cloud)[0][0]


def test_door_keel_without_the_key_is_refused_and_the_key_is_never_read(cloud):
    hard, _ = _pre(cloud, env={})
    assert len(hard) == 1 and "KEEL_ANTHROPIC_API_KEY is not set" in hard[0]
    source = (REPO / "quality" / "cycle.py").read_text(encoding="utf-8")
    assert 'KEY_NAME = "KEEL_ANTHROPIC_API_KEY"' in source and source.count('"KEEL_ANTHROPIC_API_KEY"') == 1
    assert re.findall(r"env\.get\(KEY_NAME\)", source) and "environ[KEY_NAME]" not in source


def test_door_host_without_the_claude_cli_is_refused(cloud):
    hard, _ = _pre(cloud, door="host", env={}, which=lambda name: None)
    assert len(hard) == 1 and "the `claude` CLI is not on PATH" in hard[0] and "DOOR=host answers" in hard[0]
    hard, _ = _pre(cloud, which=lambda name: None)
    assert "the readers run through it" in hard[0], "DOOR=keel still reads through the CLI"


def test_no_why_an_unknown_entry_a_door_and_a_build_are_refused(cloud):
    assert "no WHY" in _pre(cloud, why="  ")[0][0]
    assert "no back-test entry ['99-nobody']" in _pre(cloud, entries=["99-nobody"])[0][0]
    assert "is not a door" in _pre(cloud, door="side")[0][0]
    hard, _ = _pre(cloud, build="fffffff")
    assert "BUILD=fffffff but the keel-cloud checkout is at" in hard[0]
    sha = subprocess.run(["git", "-C", str(cloud), "rev-parse", "--short=7", "HEAD"], capture_output=True,
                         text=True).stdout.strip()
    assert _pre(cloud, build=sha) == ([], [])


def test_a_dry_run_turns_the_paid_refusals_into_warnings(cloud):
    (cloud / "src" / "new.txt").write_text("x\n", encoding="utf-8")
    hard, soft = _pre(cloud, dry=True, why="", env={}, which=lambda name: None)
    assert hard == [] and len(soft) == 4
    assert _pre(cloud, dry=True, entries=["99-nobody"])[0], "an unknown entry is refused even dry"


def test_the_plan_is_per_entry_per_scope_then_one_table(tmp_path):
    steps = cycle.plan_steps(["21-codyco", "08-fresco"], ["PROBLEM", "COMMERCIAL"], "host", tmp_path)
    assert [s["what"] for s in steps] == ["down", "backtest", "read"] * 4 + ["table"]
    back = [s["argv"][4:] for s in steps if s["what"] == "backtest"]
    assert back[0] == ["backtest", "ENTRY=21-codyco", "SCOPE=PROBLEM", "DOOR=host"]
    assert back[3] == ["backtest", "ENTRY=08-fresco", "SCOPE=COMMERCIAL", "DOOR=host"]
    read = steps[2]["argv"][4:]
    assert read[0] == "read-screens" and read[1] == "RUN=<bundle>" and read[2].startswith("OUT=")
    assert steps[-1]["argv"][4:] == ["read-table", "BASELINE=1", "CYCLE=<record>"]


def test_the_dry_walk_prints_the_plan_and_runs_nothing(monkeypatch, tmp_path, capsys):
    web = git_checkout(tmp_path / "web", {"package.json": "{}\n"})
    cloud = git_checkout(tmp_path / "cloud2", {"canon/designs/measured-beliefs/backtest/21-codyco.yaml": "id\n"})
    monkeypatch.setattr(cycle, "checkouts", lambda: (cloud, web))

    def never(*a, **k):
        raise AssertionError("a dry run runs nothing")
    code = cycle.walk(["--entries", "21-codyco", "--scopes", "PROBLEM", "--why", "dry", "--dry-run",
                       "--cycles-dir", str(tmp_path / "cycles")], runner=never, env={}, which=lambda n: None)
    out = capsys.readouterr().out
    assert code == 0 and "DRY RUN -- nothing runs" in out and "WHY: dry" in out
    assert "backtest ENTRY=21-codyco SCOPE=PROBLEM DOOR=keel" in out and "read-screens RUN=<bundle>" in out
    assert "read-table BASELINE=1 CYCLE=" in out and "a paid walk would refuse: KEEL_ANTHROPIC_API_KEY" in out
    assert not (tmp_path / "cycles").exists(), "no record is written"


def test_one_study_is_walked_then_read_and_its_score_file_recorded(monkeypatch, tmp_path):
    runs = tmp_path / "runs"
    score = REPO / _score("08-fresco", "20261101", "SOLUTION")
    seen = []

    def fake(argv, stdout=None, stderr=None):
        seen.append(argv[4:])
        if argv[4] == "backtest":
            run = runs / "20261101T110000Z-backtest-08-fresco"
            run.mkdir(parents=True)
            (run / bt.RECORD).write_text(json.dumps({"run": run.name, "passed": True, "scope": "SOLUTION",
                                                     "founder_screens": [{}], "cost": {"cli": {"usd": 0.61}}}))
            stdout.write(f"run bundle: {run}\n")
        if argv[4] == "read-screens":
            out = Path(argv[6].split("=", 1)[1])
            out.mkdir(parents=True)
            (out / "score-path.txt").write_text(f"{score}\n")
        return SimpleNamespace(returncode=0)

    steps = [s for s in cycle.plan_steps(["08-fresco"], ["SOLUTION"], "host", tmp_path / "work") if s["study"]]
    study = cycle.walk_one("08-fresco", "SOLUTION", steps, door="host", runner=fake, runs_dir=runs)
    assert [s[0] for s in seen] == ["down", "backtest", "read-screens"]
    assert seen[2][1] == f"RUN={runs / '20261101T110000Z-backtest-08-fresco'}"
    assert study.passed and study.bundle == "20261101T110000Z-backtest-08-fresco" and study.walk_usd == 0.61
    assert study.score_file == _score("08-fresco", "20261101", "SOLUTION") and study.score_pct == 100.0
    assert study.read_usd == 0.4 and study.error is None


def test_a_walk_runs_every_study_then_the_table_and_writes_the_record(monkeypatch, tmp_path, capsys):
    web = git_checkout(tmp_path / "web", {"package.json": "{}\n"})
    cloud = git_checkout(tmp_path / "cloud3", {"canon/designs/measured-beliefs/backtest/08-fresco.yaml": "id\n"})
    monkeypatch.setattr(cycle, "checkouts", lambda: (cloud, web))
    monkeypatch.setattr(cycle, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(table, "BASELINE_PATH", BASELINE)
    runs, seen = tmp_path / "bundles", []
    scores = {"PROBLEM": REPO / _score("08-fresco", "20261101", "PROBLEM"),
              "SOLUTION": REPO / _score("08-fresco", "20261101", "SOLUTION")}

    def fake(argv, stdout=None, stderr=None):
        seen.append(argv[4:])
        args = dict(a.split("=", 1) for a in argv[5:] if "=" in a)
        if argv[4] == "backtest":
            run = runs / f"2026110{len(seen)}T100000Z-backtest-08-fresco"
            run.mkdir(parents=True)
            (run / bt.RECORD).write_text(json.dumps({"run": run.name, "passed": True, "scope": args["SCOPE"],
                                                     "founder_screens": [{}], "cost": {"usd": 0.5}}))
            stdout.write(f"run bundle: {run}\n")
        if argv[4] == "read-screens":
            Path(args["OUT"]).mkdir(parents=True)
            scope = "PROBLEM" if "PROBLEM" in args["OUT"] else "SOLUTION"
            (Path(args["OUT"]) / "score-path.txt").write_text(f"{scores[scope]}\n")
        return SimpleNamespace(returncode=0)

    code = cycle.walk(["--entries", "08-fresco", "--scopes", "PROBLEM,SOLUTION", "--door", "host", "--why",
                       "a week since the last cycle", "--cycles-dir", str(tmp_path / "cycles")],
                      runner=fake, env={}, which=lambda n: "/usr/bin/claude")
    assert code == 0
    assert [s[0] for s in seen] == ["down", "backtest", "read-screens"] * 2 + ["read-table"]
    assert seen[-1][1:3] == ["BASELINE=1", f"CYCLE={tmp_path / 'cycles' / seen[-1][2].rsplit('/', 1)[1]}"]
    record = cycle.load_record(next((tmp_path / "cycles").glob("*.md")))
    assert record["why"] == "a week since the last cycle" and record["door"] == "host"
    assert [s["scope"] for s in record["studies"]] == ["PROBLEM", "SOLUTION"]
    assert record["head"]["score_pct"] == 94.1 and record["against_baseline"]["verdict"] == "worse"
    assert record["cost"]["walk_usd"] == 1.0 and "cycle record: quality/cycles/" not in capsys.readouterr().err


# --------------------------------------------------------------------------------------- the cycle record

def test_the_record_is_composed_from_the_score_files_the_baseline_and_the_previous_cycle():
    text, data = compose_the_fixture()
    assert text == RECORD.read_text(encoding="utf-8"), "the committed fixture record is what compose writes"
    assert text.startswith("# Quality cycle 20261101-abcdef1\n\n**Why this cycle** (the founder's words): the "
                           "registry's Importance row moved (keel-cloud 150)")
    assert data["head"]["score_pct"] == 95.6 and data["head"]["flagged_pct"] == 12.5
    assert data["head"]["by_scope"]["PROBLEM"]["score_pct"] == 88.2
    assert data["baseline"]["cut"] == "2026-10-25" and data["baseline"]["score_pct"] == 100.0
    assert data["against_baseline"]["verdict"] == "worse" and data["against_baseline"]["moved"] == [WEAK_ROW]
    assert data["previous"]["record"] == "20261025-0000aaa" and data["previous"]["verdict"] == "worse"
    assert data["previous"]["studies"] == {"08-fresco · PROBLEM": {"then": 100.0, "now": 88.2, "delta": -11.8}}
    assert data["weak_rows"] == [WEAK_ROW] and data["bar_pct"] == 90.0 and data["rubric_version"] == 2
    assert data["cost"] == {"walk_usd": 1.84, "read_usd": 1.1, "total_usd": 2.94}
    assert "make read-screens exited 2" in text and "make quality-advise CYCLE=quality/cycles/20261101-abcdef1.md" in text
    assert "make quality-accept CYCLE=quality/cycles/20261101-abcdef1.md" in text
    assert cycle.load_record(RECORD)["head"] == data["head"], "the data block round-trips"


def test_the_first_cycle_has_no_baseline_and_no_previous(tmp_path):
    text, data = compose_the_fixture(cycles_dir=tmp_path, baseline=tmp_path / "BASELINE.md")
    assert data["baseline"] is None and data["previous"] is None and data["against_baseline"] is None
    assert "No baseline is cut yet" in text and "No earlier cycle record." in text


def test_records_are_named_by_day_and_build_and_never_overwritten(tmp_path):
    assert cycle.record_name("20261101", "abcdef1", tmp_path) == "20261101-abcdef1"
    (tmp_path / "20261101-abcdef1.md").write_text("x")
    assert cycle.record_name("20261101", "abcdef1", tmp_path) == "20261101-abcdef1-2"
    assert cycle.previous_record(FX / "cycles", "20261101-abcdef1") == EARLIER
    assert cycle.previous_record(FX / "cycles", "20261025-0000aaa") is None


def test_an_unknown_cycle_is_refused(tmp_path):
    with pytest.raises(cycle.Refused, match="no CYCLE"):
        cycle.load_record("")
    with pytest.raises(cycle.Refused, match="no cycle record quality/cycles/19990101-nope.md"):
        cycle.load_record("quality/cycles/19990101-nope.md")
    (tmp_path / "x.md").write_text("# not a record\n")
    with pytest.raises(cycle.Refused, match="carries no"):
        cycle.load_record(tmp_path / "x.md")


# --------------------------------------------------------------------------------- FR-3 TABLE.md's head

def test_the_table_head_is_this_cycle_the_baseline_and_the_bar_then_the_rows_that_moved(tmp_path):
    out = tmp_path / "TABLE.md"
    shutil.copytree(SCORES, tmp_path / "scores")
    shutil.rmtree(tmp_path / "scores" / "08-fresco")
    (tmp_path / "scores" / "08-fresco").mkdir()
    shutil.copy(REPO / _score("08-fresco", "20261101", "PROBLEM"), tmp_path / "scores" / "08-fresco")
    shutil.copy(REPO / _score("08-fresco", "20261101", "SOLUTION"), tmp_path / "scores" / "08-fresco")
    assert table.main(["--scores-dir", str(tmp_path / "scores"), "--out", str(out), "--baseline",
                       "--baseline-file", str(BASELINE), "--cycle", str(RECORD)]) == 0
    text = out.read_text(encoding="utf-8")
    head = [line for line in text.splitlines() if line.startswith("- **")][:3]
    assert head[0].startswith("- **This cycle** (`quality/cycles/20261101-abcdef1.md`, cloud abcdef1, 3 studies): "
                              "score_pct **95.6%**, flagged 12.5%")
    assert head[1] == "- **The baseline** (cut 2026-10-25): score_pct 100.0%, flagged 0.0%"
    assert head[2] == "- **The bar**: 90% -- this cycle meets it"
    assert text.index("**This cycle**") < text.index("## The rows")
    moved = text.split("## Moved since the baseline", 1)[1]
    assert f"### {WEAK_ROW} -- turned WEAK (R2 -2.00, R3 -1.00, R4 -1.00)" in moved
    assert "When the crew is short on site, which of these comes first for you?" in moved
    assert "## The weak rows, with their *instead* lines" in text and "registry row" in text


def test_without_a_cycle_the_table_is_078s(tmp_path):
    out = tmp_path / "TABLE.md"
    assert table.main(["--scores-dir", str(SCORES), "--out", str(out)]) == 0
    assert "**This cycle**" not in out.read_text(encoding="utf-8")


# ------------------------------------------------------------------------------------------ FR-4 the adviser

def _weak(kind_filter=None):
    files = cycle.cycle_files(cycle.load_record(RECORD))
    return files, cycle.weak_rows(files)


def test_the_adviser_prompt_quotes_the_weak_row_its_screens_and_the_current_registry_row():
    files, rows = _weak()
    assert [table.row_key(r) for r in rows] == [WEAK_ROW]
    prompt = cycle.adviser_prompt(rows[0], files, cloud=CLOUD, cfg=cycle.load_config(), sha="abcdef1")
    assert "{{" not in prompt and "propose ONE edit" in prompt
    assert f"{WEAK_ROW} -- 1 screen(s) over 08-fresco" in prompt and "weak on R2, R3, R4" in prompt
    assert "- R2 **Plain to this person.**" in prompt
    assert "0: confusing, double-barrelled, or words of another trade. Weak by mean 0.0 under 1.5" in prompt
    assert "R2 -- the registry row, or the instruction gains the trade's words" in prompt, "spec 081 FR-5"
    assert "08-fresco · `item-problem.importance` (link PRIMARY): R2 0 -- item-problem.importance: why 2" in prompt
    assert "Instead: When the crew is short on site, which of these comes first for you?" in prompt
    assert "registry row: problem.importance's respondent wording" in prompt
    assert ("`src/main/resources/keel/dimension-registry.json`, dimension `problem.importance`, its `respondent` "
            "block (keel-cloud at `abcdef1`)") in prompt
    assert "FIXTURE-RESPONDENT-GUIDANCE" in prompt and "What came first?" not in prompt, "the respondent block only"
    assert "| words | fix the words" in prompt and '"rung": "words" | "effort" | "split"' in prompt
    assert "## The fix is persona awareness, never a special case" in prompt and '"persona_aware": true | false' in prompt


def test_the_current_text_follows_the_fix_location():
    cfg = cycle.load_config()

    def row(audience, kind, dimension, category, place):
        return {"audience": audience, "kind": kind, "dimension": dimension, "fix": {"category": category, "place": place}}
    founder = cycle.current_text(row("founder", "q", "problem.importance", *table.fix_location("founder", "q",
                                                                                                 "problem.importance")),
                                 cloud=CLOUD, cfg=cfg)
    assert "its `founder` block" in founder["where"] and "the {actor} has to get done" in founder["text"]
    follow = cycle.current_text(row("respondent", "follow_up", "problem.importance",
                                    *table.fix_location("respondent", "follow_up", "problem.importance")),
                                cloud=CLOUD, cfg=cfg)
    assert "`follow_up` block" in follow["where"] and "What came first?" in follow["text"]
    gate = cycle.current_text(row("respondent", "gate", "problem.prevalence",
                                  *table.fix_location("respondent", "gate", "problem.prevalence")), cloud=CLOUD, cfg=cfg)
    assert "respondent-questions.md`, section *The gate*" in gate["where"]
    assert "FIXTURE-GATE-SECTION" in gate["text"] and "FIXTURE-CONDITION-SECTION" not in gate["text"]
    screener = cycle.current_text(row("respondent", "screener", "-", *table.fix_location("respondent", "screener", None)),
                                  cloud=CLOUD, cfg=cfg)
    assert "FIXTURE-CONDITION-SECTION" in screener["text"] and "FIXTURE-GATE-SECTION" not in screener["text"]
    page = cycle.current_text(row("founder", "ready", "-", *table.fix_location("founder", "ready", None)),
                              cloud=CLOUD, cfg=cfg)
    assert page["text"].startswith("(no model writes these words")
    missing = cycle.current_text(row("respondent", "item", "problem.nothing", "registry row", "x"), cloud=CLOUD, cfg=cfg)
    assert missing["text"] == "(no registry row named problem.nothing)"


class FakeAdviser:
    def __init__(self, answer):
        self.answer, self.seen = answer, []

    def __call__(self, argv, *, input, capture_output, text, timeout, env, cwd):    # noqa: A002
        self.seen.append(argv)
        result = "ready" if "Reply with the one word" in input else self.answer
        body = {"type": "result", "is_error": False, "result": result, "total_cost_usd": 0.05}
        return SimpleNamespace(stdout=json.dumps(body) + "\n", stderr="", returncode=0)


def _advise(monkeypatch, tmp_path, answer, *extra):
    fake = FakeAdviser(answer)
    monkeypatch.setattr(readers.Reader, "available", lambda self: True)
    monkeypatch.setattr(cycle, "RUNS_DIR", tmp_path / "runs")
    out = tmp_path / "advice.md"
    code = cycle.advise(["--cycle", str(RECORD), "--cloud", str(CLOUD), "--out", str(out), *extra], runner=fake)
    return code, out, fake


def test_the_dry_adviser_prints_the_prompt_and_calls_nothing(monkeypatch, tmp_path, capsys):
    code, out, fake = _advise(monkeypatch, tmp_path, "{}", "--dry-run")
    said = capsys.readouterr().out
    assert code == 0 and fake.seen == [] and not out.exists() and not (tmp_path / "runs").exists()
    assert f"[1/1] {WEAK_ROW}" in said and "FIXTURE-RESPONDENT-GUIDANCE" in said
    assert "dry run: 1 adviser prompt(s) for cycle 20261101-abcdef1; no call made, nothing written" in said


def test_the_adviser_writes_its_proposals_and_applies_nothing(monkeypatch, tmp_path):
    answer = json.dumps({"new_text": "On that day, which two of these would you most like made easier?",
                         "why": "One. Two. Three.", "rung": "words", "persona_aware": True})
    before = (CLOUD / cycle.REGISTRY_REL).read_bytes()
    code, out, fake = _advise(monkeypatch, tmp_path, answer)
    assert code == 0 and len(fake.seen) == 2, "the probe, then one call for the one weak row"
    assert fake.seen[1][-4:] == ["--model", "claude-opus-5-5", "--effort", "medium"]
    assert fake.seen[1][:len(readers.JUDGE_ARGV)] == readers.JUDGE_ARGV
    text = out.read_text(encoding="utf-8")
    assert text.startswith("# Advice on cycle 20261101-abcdef1") and "**Nothing here is applied.**" in text
    assert f"## 1. {WEAK_ROW} -- weak on R2, R3, R4" in text and "Rung: **words**" in text
    assert "On that day, which two of these would you most like made easier?" in text and "Taken: _(the founder" in text
    assert (CLOUD / cycle.REGISTRY_REL).read_bytes() == before, "never applied"
    assert sorted(p.name for p in (tmp_path / "runs").rglob("*.prompt.txt"))[0] == "001-probe.prompt.txt"


def test_an_unreadable_proposal_is_named_not_invented(monkeypatch, tmp_path):
    code, out, _ = _advise(monkeypatch, tmp_path, json.dumps({"new_text": "x", "why": "y", "rung": "louder"}))
    assert code == 0 and "**No proposal**: the answer could not be read (rung must be one of" in out.read_text()


def test_the_adviser_refuses_without_the_claude_cli(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(readers.Reader, "available", lambda self: False)
    assert cycle.advise(["--cycle", str(RECORD), "--cloud", str(CLOUD), "--out", str(tmp_path / "a.md")]) == 2
    assert "the `claude` binary is not on PATH" in capsys.readouterr().err and not (tmp_path / "a.md").exists()


def test_the_adviser_refuses_an_unknown_cycle_and_has_nothing_to_say_without_a_weak_row(tmp_path, capsys):
    assert cycle.advise(["--cycle", "quality/cycles/19990101-nope.md", "--dry-run"]) == 2
    assert "no cycle record" in capsys.readouterr().err
    text, _ = compose_the_fixture(cycles_dir=tmp_path, baseline=tmp_path / "none.md")
    data = json.loads(text.split("```json", 1)[1].split("```", 1)[0])
    data["studies"] = [s for s in data["studies"] if s["scope"] != "PROBLEM"]
    record = tmp_path / "20261102-abcdef1.md"
    record.write_text(cycle.render_record(data), encoding="utf-8")
    assert cycle.advise(["--cycle", str(record), "--cloud", str(CLOUD), "--dry-run"]) == 0
    assert "no weak row -- nothing to advise, no call made" in capsys.readouterr().out


# -------------------------------------------------------------------------------------- FR-6 the acceptance

def _accept(tmp_path, *extra):
    runs = build_runs(tmp_path / "runs")
    out, quality_out = tmp_path / "sample", tmp_path / "quality"
    code = cycle.accept(["--cycle", str(RECORD), "--runs-dir", str(runs), "--out", str(out), "--quality-out",
                         str(quality_out), "--provenance-dir", str(tmp_path / "prov"), "--today", "2026-11-02", *extra])
    return code, out, quality_out


def test_accept_cuts_the_baseline_refuses_the_failing_bundles_by_name_and_builds_the_rest(tmp_path, capsys):
    (tmp_path / "quality").mkdir()
    shutil.copy(BASELINE, tmp_path / "quality" / "BASELINE.md")
    (tmp_path / "sample" / "fresco").mkdir(parents=True)
    (tmp_path / "sample" / "fresco" / "cover.jpg").write_bytes(b"JPEG")
    (tmp_path / "sample" / "index.json").write_text(json.dumps({"examples": [{"slug": "fresco"}]}))
    code, out, quality_out = _accept(tmp_path)
    said = capsys.readouterr().out
    assert code == 0
    # the baseline: rewritten from the cycle's score files, the old one kept
    data = table.read_baseline(quality_out / "BASELINE.md")
    assert data["cut"] == "2026-11-02" and sorted(data["studies"]) == ["08-fresco · PROBLEM", "08-fresco · SOLUTION",
                                                                       "09-karsa · COMMERCIAL"]
    assert (quality_out / "baselines" / "2026-10-25.md").read_text() == BASELINE.read_text()
    # the readers' gate: refused by name, with the reason
    assert ("gallery: refused 20261101T100000Z-backtest-08-fresco (08-fresco · PROBLEM): "
            "20261101-PROBLEM-r2-abcdef1-v13-claude-opus-5-5.json has 1 flagged screen(s) and score_pct 88.2% under "
            "the bar of 90%") in said
    assert ("gallery: refused 20261101T130000Z-backtest-08-fresco (08-fresco · COMMERCIAL): no score file at rubric "
            "version 2") in said
    # built from the rest: one example per entry, the solution study for fresco
    index = json.loads((out / gallery.INDEX).read_text(encoding="utf-8"))
    assert sorted((r["slug"], r["scope"]) for r in index["examples"]) == [("fresco", "SOLUTION"), ("karsa", "COMMERCIAL")]
    assert (out / "fresco" / "cover.jpg").read_bytes() == b"JPEG", "the snapshot's cover is kept"
    assert "refreshed fresco; added karsa; missing a cover.jpg karsa" in said
    assert "keel-web spec: refresh the example gallery from keel-e2e-eval quality cycle 20261101-abcdef1" in said
    assert "re-pin the example frames (light, dark, phone)" in said


def test_accept_with_nothing_passing_cuts_the_baseline_and_leaves_the_gallery(tmp_path, capsys, monkeypatch):
    cfg = {**cycle.load_config(), "bar_pct": 101.0}
    monkeypatch.setattr(cycle, "load_config", lambda *a, **k: cfg)
    code, out, quality_out = _accept(tmp_path)
    said = capsys.readouterr().out
    assert code == 0 and (quality_out / "BASELINE.md").is_file() and not out.exists()
    assert "no bundle of this cycle passes the readers' gate -- the gallery is left as it is" in said


def test_accept_refuses_without_a_cycle_or_an_unknown_one(capsys, tmp_path):
    assert cycle.accept(["--out", str(tmp_path / "s")]) == 2
    assert "make quality-accept refuses: no CYCLE" in capsys.readouterr().err
    assert cycle.accept(["--cycle", "nope", "--out", str(tmp_path / "s")]) == 2
    assert "no cycle record nope" in capsys.readouterr().err
    assert not (tmp_path / "s").exists()


def test_the_gallery_gate_by_itself(tmp_path):
    runs = build_runs(tmp_path / "runs")
    every = sorted(runs.iterdir())
    passing, refused = gallery.score_gate(every, SCORES)
    assert [p.name for p in passing] == ["20261101T110000Z-backtest-08-fresco", "20261101T120000Z-backtest-09-karsa"]
    assert len(refused) == 2
    passing, refused = gallery.score_gate(every, SCORES, refuse_flagged=False, bar_pct=80.0)
    assert len(passing) == 3, "the PROBLEM study passes once neither rule refuses it"
    # a score file at another rubric version is set aside by name, never read as passing
    other = tmp_path / "scores" / "09-karsa"
    other.mkdir(parents=True)
    obj = json.loads((REPO / _score("09-karsa", "20261101", "COMMERCIAL")).read_text())
    obj["rubric_version"] = 3
    (other / "x-r3.json").write_text(json.dumps(obj))
    _, refused = gallery.score_gate([runs / "20261101T120000Z-backtest-09-karsa"], tmp_path / "scores")
    assert "set aside at another rubric version: x-r3.json" in refused[0]


def test_make_gallery_with_scores_and_a_scope_order(tmp_path, capsys):
    runs = build_runs(tmp_path / "runs")
    names = ",".join(str(p) for p in sorted(runs.iterdir()))
    base = ["--runs", names, "--out", str(tmp_path / "out"), "--provenance-dir", str(tmp_path / "prov"),
            "--scores", str(SCORES)]
    assert gallery.main(base) == 0
    said = capsys.readouterr().out
    assert said.count("gallery: refused ") == 2 and "gallery: 2 slugs" in said
    lenient = base + ["--keep-flagged", "--bar", "80"]
    assert gallery.main(lenient) == 1, "fresco passes twice without a scope order: given twice"
    assert "08-fresco given twice" in capsys.readouterr().err
    assert gallery.main(lenient + ["--scope-order", "SOLUTION,PROBLEM,COMMERCIAL"]) == 0
    said = capsys.readouterr().out
    assert said.count("gallery: refused ") == 1, "only the bundle with no score file"
    assert ("gallery: 08-fresco: the SOLUTION study (20261101T110000Z-backtest-08-fresco) is the example; also "
            "passing: PROBLEM (20261101T100000Z-backtest-08-fresco)") in said
    assert gallery.main(["--runs", names, "--out", str(tmp_path / "o2"), "--provenance-dir", str(tmp_path / "p"),
                         "--scores", str(tmp_path / "empty")]) == 1
    assert "every run was refused by the readers' gate" in capsys.readouterr().err


# ---------------------------------------------------------------------------------- FR-1 / FR-7 / FR-9

def test_the_runbook_is_a_file_read_first_with_six_steps():
    text = (REPO / "quality" / "CYCLE.md").read_text(encoding="utf-8")
    first = text.splitlines()[0]
    assert "kick off the instruction set" in first and "this file and nothing else" in first
    steps = re.findall(r"^## Step (\d)\b", text, re.M)
    assert steps == ["1", "2", "3", "4", "5", "6"]
    for command in ("make quality-walk", "make quality-advise", "make quality-accept", "make quality-due",
                    "make read-table"):
        assert command in text, command
    for question in ("current score", "what changed", "what is proposed", "on the homepage"):
        assert question in text.lower(), question
    agents = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    assert "**The quality cycle**" in agents and "quality/CYCLE.md" in agents


def test_no_gate_names_the_cycle_and_the_targets_refuse_without_a_cycle():
    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    for name in ("eval: venv", "eval-live: venv", "unit: venv", "sample: venv", "instruction-eval: venv"):
        body = makefile.split(f"\n{name}\n", 1)[1].split("\n\n", 1)[0]
        assert "quality-" not in body and "quality.cycle" not in body, name
    for path in (REPO / "matrix").rglob("*"):
        if path.is_file() and path.suffix in (".py", ".toml", ".yml", ".yaml"):
            assert "quality-walk" not in path.read_text(encoding="utf-8"), path
    assert not list((REPO / "quality").rglob("test_*.py"))
    for target in ("quality-advise", "quality-accept"):
        body = makefile.split(f"\n{target}: venv\n", 1)[1].split("\n\n", 1)[0]
        assert f"make {target} refuses: no CYCLE" in body
    walk = makefile.split("\nquality-walk: venv\n", 1)[1].split("\n\n", 1)[0]
    assert "--dry-run" in walk and "--why" in walk and "KEY" not in walk
    assert "--cycle" in makefile.split("\nread-table: venv\n", 1)[1].split("\n\n", 1)[0]
    assert "--scores" in makefile.split("\ngallery: venv\n", 1)[1].split("\n\n", 1)[0]


def test_the_cycle_records_are_committed():
    ignore = (REPO / ".gitignore").read_text(encoding="utf-8")
    assert "quality" not in ignore and (REPO / "quality" / "cycles" / "README.md").is_file()
