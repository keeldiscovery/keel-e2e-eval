"""The quality cycle (spec 079): one kick-off, a comparison, an adviser, a rerun, an acceptance that becomes the homepage.

`quality/CYCLE.md` is the runbook; this module is its commands, and `quality/cycle.toml` is everything they read.

- **`walk`** -- `make quality-walk ENTRIES=<ids|default> [SCOPES=] [DOOR=keel|host] [BUILD=<cloud7>] [PEOPLE=<n>]
  [DRY=1] WHY=...` (paid, FR-2 / FR-5): per entry and per scope, `make backtest ENTRY= SCOPE= DOOR= PEOPLE=` (spec 106
  FR-2: `cycle.toml`'s `people`, seven a study on the person's own link) on the local stack, then `make
  read-screens RUN=<the new bundle>`, then `make read-table BASELINE=1 CYCLE=<record>`; it writes the cycle record
  `quality/cycles/<yyyymmdd>-<cloud7>.md` (the why in the founder's words, the studies, the bundles, the score files, the
  head, the cost and the time, the comparison with the baseline and with the previous cycle). Refused without ENTRIES,
  without WHY, with a dirty keel-cloud checkout, on DOOR=keel without the key in the shell, without the `claude` CLI
  (the readers' door, and the host door's), on an unknown entry or scope, or when BUILD= is not the checkout's sha.
  `DRY=1` prints the plan and runs nothing.
- **`advise`** -- `make quality-advise CYCLE=<record> [DRY=1]` (paid, FR-4): one bounded call per weak row of the
  cycle, `quality/readers/adviser.md` filled with the row, its failing screens, its fix location and **the current
  text at that location** read from the keel-cloud checkout; the proposals go to `quality/cycles/<record>-advice.md`,
  **never applied**. A weak row the founder has already decided (`quality/decisions.toml`, spec 087) is snoozed:
  listed under *Decided before* with the decision's word and why, not sent; the adviser is told what he declined.
- **`accept`** -- `make quality-accept CYCLE=<record>` (free, FR-6): `quality/BASELINE.md` rewritten from that cycle's
  score files (the old one kept under `quality/baselines/<date>.md`), then the gallery built from that cycle's bundles
  behind the readers' gate (`evals/gallery.py --scores`), what changed in the snapshot, and the sentence the keel-web
  refresh spec starts from.
- **`due`** -- `make quality-due` (free, FR-7): whether a cycle is due, and why; it runs nothing else.

No key is ever read, named or passed: the presence of `KEEL_ANTHROPIC_API_KEY` is checked for DOOR=keel (as `make
backtest` checks it) and its value never touched. Nothing here runs from `make eval`, `make unit`, the matrix or a
checker (FR-9).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path

from quality import decisions as dec
from quality import readers, rubric, table

REPO = Path(__file__).resolve().parent.parent
QUALITY = REPO / "quality"
CYCLE_TOML = QUALITY / "cycle.toml"
CYCLES_DIR = QUALITY / "cycles"
ADVISER_PROMPT = QUALITY / "readers" / "adviser.md"
#: Spec 087: the founder's decisions -- a weak row one of them covers is snoozed, not advised again.
DECISIONS = QUALITY / "decisions.toml"
RUNS_DIR = REPO / "runs"
SCORES_REL = "quality/scores"

DOORS = ("keel", "host")
#: Spec 071 FR-4: the scopes a back-test walks under.
SCOPES = ("PROBLEM", "SOLUTION", "SOLUTION_COMMERCIAL", "COMMERCIAL", "ALL")
#: The design's §5 ladder.
RUNGS = ("words", "effort", "split")
KEY_NAME = "KEEL_ANTHROPIC_API_KEY"

REGISTRY_REL = Path("src/main/resources/keel/dimension-registry.json")
INSTRUCTIONS_REL = Path("src/main/resources/keel/inference-instructions")
BACKTEST_REL = Path("canon/designs/measured-beliefs/backtest")
#: What a cycle is due on (FR-7): keel-cloud paths whose change moves the words or the models.
DUE_PATHS = ("src/main/resources/keel/dimension-registry.json", "src/main/resources/keel/inference-instructions",
             "src/main/resources/keel/model-routing.json")

_DATA = "<!-- cycle:data -->"
_ADVICE_DATA = "<!-- advice:data -->"

LADDER = ("| rung | change | when |\n|---|---|---|\n"
          "| words | fix the words (the registry row, or the instruction file) | a weak row with a clear *instead* |\n"
          "| effort | the job class's effort raised (e.g. `calibration` medium -> high), measured by the readers on the "
          "same entries | the words did not fix it |\n"
          "| split | split the one call per dimension and route the weak dimension higher (a contract change) | one "
          "dimension still weak at high effort |")


class Refused(RuntimeError):
    """A reason a cycle command will not run, printed as one sentence (exit 2)."""


# ------------------------------------------------------------------------------------------------ the settings

def load_config(path: Path | None = None, *, readers_toml: Path | None = None) -> dict:
    """`quality/cycle.toml`, checked: the scopes known, the door a door, and the bar, the weak rule and the reader held
    equal to their second homes (`quality/rubric.py`, `quality/readers.toml`) -- refused, naming both, when not."""
    path = Path(path or CYCLE_TOML)
    if not path.is_file():
        raise Refused(f"no cycle settings at {path} (spec 079 FR-8)")
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    cyc, bar, weak = raw.get("cycle") or {}, raw.get("bar") or {}, raw.get("weak") or {}
    cfg = {
        "entries": list(cyc.get("entries") or []), "scopes": list(cyc.get("scopes") or []),
        "door": str(cyc.get("door") or "keel"), "people": cyc.get("people"), "bar_pct": float(bar.get("bar_pct", -1)),
        "weak": {"zero_entries": int(weak.get("zero_entries", -1)), "mean_under": float(weak.get("mean_under", -1))},
        "reader": dict(raw.get("reader") or {}), "adviser": dict(raw.get("adviser") or {}),
        "gallery": dict(raw.get("gallery") or {}), "cadence": dict(raw.get("cadence") or {}),
    }
    cfg["adviser"].setdefault("timeout_s", 300)
    cfg["adviser"].setdefault("max_quote_chars", 16000)
    cfg["adviser"]["sections"] = dict((raw.get("adviser") or {}).get("sections") or {})
    unknown = [s for s in cfg["scopes"] if s not in SCOPES]
    if unknown or not cfg["scopes"]:
        raise Refused(f"{path.name}: scopes {cfg['scopes']} -- each one of {', '.join(SCOPES)}")
    if cfg["door"] not in DOORS:
        raise Refused(f"{path.name}: door {cfg['door']!r} is not one of {DOORS}")
    if cfg["people"] is not None and (isinstance(cfg["people"], bool) or not isinstance(cfg["people"], int)
                                      or cfg["people"] < 1):
        raise Refused(f"{path.name}: people {cfg['people']!r} is not a number of people -- a whole number from 1, the "
                      "people each study sends on the person's own link (spec 106 FR-2)")
    for key in ("model", "effort"):
        if not cfg["adviser"].get(key):
            raise Refused(f"{path.name} has no adviser.{key} (spec 079 FR-4)")
    if cfg["bar_pct"] != rubric.BAR_PCT:
        raise Refused(f"{path.name} says the bar is {cfg['bar_pct']}% and quality/rubric.py BAR_PCT {rubric.BAR_PCT}% "
                      "-- they are held equal; change both in one commit")
    if (cfg["weak"]["zero_entries"], cfg["weak"]["mean_under"]) != (rubric.WEAK_ZERO_ENTRIES, rubric.WEAK_MEAN):
        raise Refused(f"{path.name}'s weak rule {cfg['weak']} is not quality/rubric.py's (WEAK_ZERO_ENTRIES "
                      f"{rubric.WEAK_ZERO_ENTRIES}, WEAK_MEAN {rubric.WEAK_MEAN}) -- a change to the weak rule is a "
                      "RUBRIC_VERSION bump (RUBRIC.md, *Versions*), made in both files at once")
    pinned = readers.load_reader_config(readers_toml)
    for key in ("model", "effort"):
        if str(cfg["reader"].get(key)) != str(pinned.get(key)):
            raise Refused(f"{path.name} names the reader's {key} {cfg['reader'].get(key)!r} and quality/readers.toml "
                          f"{pinned.get(key)!r} -- two files must never name two readers")
    g = cfg["gallery"]
    g.setdefault("refuse_flagged", True)
    g.setdefault("refuse_under_bar", True)
    g.setdefault("scope_order", ["SOLUTION", "PROBLEM", "COMMERCIAL", "SOLUTION_COMMERCIAL", "ALL"])
    cfg["cadence"].setdefault("days", 7)
    return cfg


def load_decisions(path: Path | str | None = None) -> list[dict]:
    """`quality/decisions.toml` (spec 087 FR-1), every entry checked -- refused by name when it is not that shape;
    no file is no decision."""
    path = Path(path or DECISIONS)
    try:
        return dec.load(path)
    except dec.DecisionsError as reason:
        raise Refused(f"the decisions file {_rel(path)} is not the shape spec 087 FR-1 reads: {reason}") from reason


# ------------------------------------------------------------------------------------------------ the checkouts

def checkouts() -> tuple[Path, Path]:
    """keel-cloud and keel-web as stack.toml names them (read only)."""
    from stack.config import load_config as stack_config               # noqa: PLC0415
    cfg = stack_config(validate=False)
    return Path(cfg.keel_cloud), Path(cfg.keel_web)


def _git(path: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True, timeout=60)
    if done.returncode != 0:
        raise Refused(f"git {' '.join(args)} failed in {path}: {done.stderr.strip()[:200]}")
    return done.stdout


def git_sha(path: Path, *, short: int = 7) -> str:
    return _git(path, "rev-parse", f"--short={short}", "HEAD").strip()


def git_branch(path: Path) -> str:
    try:
        return _git(path, "rev-parse", "--abbrev-ref", "HEAD").strip()
    except Refused:
        return "?"


def git_dirty(path: Path) -> list[str]:
    """What makes a checkout not name what was measured: any tracked change, or an untracked file under `src/` (where
    the registry, the instructions and the code live). Untracked design notes under `canon/` do not move a build."""
    lines = []
    for line in _git(path, "status", "--porcelain").splitlines():
        if not line.strip():
            continue
        if line.startswith("??") and not line[3:].startswith("src/"):
            continue
        lines.append(line)
    return lines


# ------------------------------------------------------------------------------------------------ the walk

@dataclass
class Study:
    """One (entry, scope) of a cycle: its walk, its bundle, its score file."""

    entry: str
    scope: str
    bundle: str | None = None
    bundle_path: str | None = None
    passed: bool | None = None
    failed_step: str | None = None
    score_file: str | None = None
    score_pct: float | None = None
    flagged_pct: float | None = None
    walk_usd: float | None = None
    walk_s: float | None = None
    read_usd: float | None = None
    read_s: float | None = None
    error: str | None = None
    # spec 082 FR-3: the shas this study was walked on (the bundle's `stack`), beside the pins of the kick-off
    cloud_sha: str | None = None
    web_sha: str | None = None

    @property
    def key(self) -> str:
        return f"{self.entry} · {self.scope}"


def resolve_entries(raw: str | None, cfg: dict) -> list[str]:
    raw = (raw or "").strip()
    if not raw:
        raise Refused("make quality-walk refuses: no ENTRIES -- name the entries to walk, `ENTRIES=21-codyco,08-fresco`, "
                      f"or `ENTRIES=default` for quality/cycle.toml's {', '.join(cfg['entries']) or '(none named)'}")
    if raw == "default":
        if not cfg["entries"]:
            raise Refused("make quality-walk refuses: ENTRIES=default and quality/cycle.toml names no entry")
        return list(cfg["entries"])
    return [e.strip() for e in raw.split(",") if e.strip()]


def resolve_scopes(raw: str | None, cfg: dict) -> list[str]:
    scopes = [s.strip().upper() for s in (raw or "").split(",") if s.strip()] or list(cfg["scopes"])
    unknown = [s for s in scopes if s not in SCOPES]
    if unknown:
        raise Refused(f"make quality-walk refuses: SCOPES {unknown} -- each one of {', '.join(SCOPES)} (spec 071 FR-4)")
    return scopes


def resolve_people(raw: str | int | None, cfg: dict) -> int | None:
    """Spec 106 FR-2: `PEOPLE=` (a whole number from 1), else quality/cycle.toml's `people` (seven); None sends every
    person each study's scope sends."""
    raw = str(raw if raw is not None else "").strip()
    if not raw:
        return cfg.get("people")
    if not raw.isdigit() or int(raw) < 1:
        raise Refused(f"make quality-walk refuses: PEOPLE={raw!r} is not a number of people -- a whole number from 1, "
                      "the people each study sends on the person's own link (spec 106 FR-2)")
    return int(raw)


def preflight(*, entries: list[str], scopes: list[str], door: str, why: str | None, build: str | None, dry: bool,
              cloud: Path, env: dict | None = None, which=shutil.which) -> tuple[list[str], list[str]]:
    """Every refusal and every warning, before anything runs: `(refusals, warnings)`. On a dry run the refusals that
    only matter to a paid run (no WHY, no key, no CLI, a dirty checkout) are warnings -- the plan is still printed."""
    env = os.environ if env is None else env
    hard, soft = [], []
    if door not in DOORS:
        hard.append(f"DOOR={door} is not a door -- `DOOR=keel` (Keel's AI, spec 062) or `DOOR=host` (the founder's own "
                    "Claude Code, spec 066)")
    known = {p.name[:-len(".yaml")] for p in (cloud / BACKTEST_REL).glob("*.yaml")} if (cloud / BACKTEST_REL).is_dir() \
        else None
    if known is not None:
        unknown = [e for e in entries if e not in known]
        if unknown:
            hard.append(f"no back-test entry {unknown} in keel-cloud {BACKTEST_REL}")
    if build:
        sha = git_sha(cloud, short=max(7, len(build)))
        if not sha.startswith(build):
            hard.append(f"BUILD={build} but the keel-cloud checkout is at {sha} -- check the build out first, or name "
                        "the sha it is at")
    paid = []
    if not (why or "").strip():
        paid.append("no WHY -- every cycle says why it is spent, in the founder's words (`WHY=\"the registry's "
                    "Frequency row moved\"`), and the record carries it (spec 079 FR-7)")
    dirty = git_dirty(cloud)
    if dirty:
        paid.append(f"the keel-cloud checkout {cloud} is dirty ({len(dirty)} path(s), first {dirty[0].strip()!r}) -- a "
                    "sha must name what was measured; commit or stash first")
    if door == "keel" and not env.get(KEY_NAME):
        paid.append(f"{KEY_NAME} is not set in this shell -- DOOR=keel answers every job on Keel's AI (spec 062 FR-2); "
                    "or walk DOOR=host on the founder's own Claude Code")
    if not which("claude"):
        paid.append("the `claude` CLI is not on PATH -- the readers run through it (spec 078)"
                    + (", and DOOR=host answers every job through it (spec 066)" if door == "host" else ""))
    (soft if dry else hard).extend(paid)
    return hard, soft


def plan_steps(entries: list[str], scopes: list[str], door: str, work: Path, people: int | None = None) -> list[dict]:
    """The walk as commands, in order: per entry per scope a `make down`, a `make backtest` and a `make read-screens`,
    then one `make read-table`. `<bundle>` is filled after its back-test, from the run folder it wrote. Spec 106 FR-2:
    `people` (cycle.toml's seven, or `PEOPLE=`) rides on every back-test as `PEOPLE=`."""
    make = ["make", "-C", str(REPO), "--no-print-directory"]
    sends = [f"PEOPLE={int(people)}"] if people else []
    steps = []
    for entry in entries:
        for scope in scopes:
            tag = f"{entry}-{scope}"
            steps += [
                {"study": (entry, scope), "what": "down", "argv": [*make, "down"]},
                {"study": (entry, scope), "what": "backtest", "log": str(work / f"{tag}.backtest.log"),
                 "argv": [*make, "backtest", f"ENTRY={entry}", f"SCOPE={scope}", f"DOOR={door}", *sends]},
                {"study": (entry, scope), "what": "read", "log": str(work / f"{tag}.read.log"),
                 "out": str(work / f"read-{tag}"),
                 "argv": [*make, "read-screens", "RUN=<bundle>", f"OUT={work / f'read-{tag}'}"]},
            ]
    steps.append({"study": None, "what": "table",
                  "argv": [*make, "read-table", "BASELINE=1", "CYCLE=<record>"]})
    return steps


def _usd(record: dict) -> float | None:
    cost = record.get("cost") or {}
    for value in ((cost.get("cli") or {}).get("usd"), cost.get("usd")):
        if isinstance(value, (int, float)):
            return round(float(value), 4)
    return None


def _run(argv: list[str], log: str | None, runner=subprocess.run) -> int:
    if log:
        Path(log).parent.mkdir(parents=True, exist_ok=True)
        with open(log, "w", encoding="utf-8") as handle:
            return runner(argv, stdout=handle, stderr=subprocess.STDOUT).returncode
    return runner(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode


def walk_one(entry: str, scope: str, steps: list[dict], *, door: str, runner=subprocess.run, sleep=time.sleep,
             runs_dir: Path | None = None) -> Study:
    """One study, walked and read. A host-door walk stopped by the plan's limit is rerun after it, at most three times
    (scripts/backtest-host.sh's rule)."""
    from evals import backtest as bt                                   # noqa: PLC0415

    study = Study(entry, scope)
    down, back, read = steps
    for attempt in range(4):
        _run(down["argv"], None, runner)
        started = time.monotonic()
        _run(back["argv"], back["log"], runner)
        study.walk_s = round(time.monotonic() - started, 1)
        log_text = Path(back["log"]).read_text(encoding="utf-8", errors="replace") if Path(back["log"]).is_file() else ""
        run_dir = bt.run_dir_in(log_text) or bt.latest_run_dir(entry, Path(back["log"]), runs_dir)
        row = bt.summary(run_dir, entry)
        if door == "host" and row.get("limit_stop") is not None and attempt < 3:
            wait = max(60.0, bt.resume_epoch(row["limit_stop"] or None) - time.time())
            print(f"  {entry} · {scope}: stopped by the plan's limit -- waiting {int(wait)} s, then rerun {attempt + 1} of 3")
            sleep(wait)
            continue
        break
    if run_dir is None or not (Path(run_dir) / bt.RECORD).is_file():
        study.error = f"the back-test wrote no bundle (see {back['log']})"
        return study
    record = json.loads((Path(run_dir) / bt.RECORD).read_text(encoding="utf-8"))
    study.bundle, study.bundle_path = Path(run_dir).name, str(Path(run_dir).resolve())
    study.passed, study.failed_step = bool(record.get("passed")), record.get("failed_step")
    study.walk_usd = _usd(record)
    stack = record.get("stack") or {}
    study.cloud_sha, study.web_sha = _sha7(stack.get("keel-cloud")), _sha7(stack.get("keel-web"))
    walked_scope = record.get("scope") or "ALL"
    if walked_scope != scope:
        study.error = f"the bundle says scope {walked_scope}, the walk asked {scope}"
        return study
    if not record.get("founder_screens"):
        study.error = f"the bundle carries no founder screen (failed at {study.failed_step!r}): nothing to read"
        return study
    argv = [a.replace("RUN=<bundle>", f"RUN={run_dir}") for a in read["argv"]]
    started = time.monotonic()
    code = _run(argv, read["log"], runner)
    study.read_s = round(time.monotonic() - started, 1)
    pointer = Path(read["out"]) / "score-path.txt"
    if code != 0 or not pointer.is_file():
        study.error = f"make read-screens exited {code} (see {read['log']})"
        return study
    path = Path(pointer.read_text(encoding="utf-8").strip())
    obj = rubric.load_file(path)
    study.score_file = _rel(path)
    study.read_usd = obj.get("cost_usd")
    overall = obj["summary"]["overall"]
    study.score_pct, study.flagged_pct = overall.get("score_pct"), overall.get("flagged_pct")
    return study


def _sha7(sha) -> str | None:
    return (str(sha).strip()[:7] or None) if sha else None


def _rel(path: Path | str) -> str:
    path = Path(path).resolve()
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def _abs(path: str | Path, root: Path | None = None) -> Path:
    path = Path(path)
    return path if path.is_absolute() else Path(root or REPO) / path


# ------------------------------------------------------------------------------------------------ the record

def record_name(day: str, cloud7: str, cycles_dir: Path) -> str:
    """`<yyyymmdd>-<cloud7>`, with `-2`, `-3` ... when a cycle of that day and build is already recorded."""
    name, bump = f"{day}-{cloud7}", 2
    while (Path(cycles_dir) / f"{name}.md").exists():
        name, bump = f"{day}-{cloud7}-{bump}", bump + 1
    return name


def load_files(paths: list[str], root: Path | None = None) -> list[dict]:
    files = []
    for rel in paths:
        path = _abs(rel, root)
        if not path.is_file():
            raise Refused(f"the cycle names the score file {rel}, which is not on disk")
        obj = rubric.load_file(path)
        if obj.get("partial"):
            raise Refused(f"{rel} is a partial run: never a score of record")
        obj["_path"] = str(path)
        files.append(obj)
    return files


_RECORD_NAME = re.compile(r"^\d{8}-[0-9a-f]{7,}(-\d+)?\.md$")


def record_files(cycles_dir: Path) -> list[Path]:
    """Every cycle record under `cycles_dir`, oldest first (`<yyyymmdd>-<cloud7>[-n].md`; never an advice file)."""
    return sorted(p for p in Path(cycles_dir).glob("*.md") if _RECORD_NAME.match(p.name))


def previous_record(cycles_dir: Path, before: str) -> Path | None:
    """The latest cycle record named before `before` (records sort by name: the date, then the build)."""
    found = [p for p in record_files(cycles_dir) if p.stem < before and _DATA in p.read_text(encoding="utf-8")]
    return found[-1] if found else None


def _head_of(files: list[dict]) -> dict | None:
    current, _ = table.split_by_version(files)
    latest = table.latest_per_entry(current)
    if not latest:
        return None
    top = table.head(latest)
    s = top["summary"]
    return {"score_pct": top["score_pct"], "flagged_pct": s["overall"]["flagged_pct"], "screens": s["overall"]["screens"],
            "founder": {"score_pct": s["founder"]["score_pct"], "flagged_pct": s["founder"]["flagged_pct"]},
            "respondent": {"score_pct": s["respondent"]["score_pct"], "flagged_pct": s["respondent"]["flagged_pct"]},
            "by_scope": {k: {"score_pct": v["score_pct"], "flagged_pct": v["flagged_pct"]}
                         for k, v in top["by_scope"].items()},
            "meets_bar": top["meets_bar"]}


_SCORE_SHA = re.compile(r"-r\d+-([0-9a-f]{7,})-v")


def study_shas(study: dict, root: Path | None = None) -> dict:
    """Spec 082 FR-3: the keel-cloud and keel-web shas one study was walked on -- its own (recorded since 082), else its
    score file's header (the bundle's `stack`, as the reader copied it), else the cloud sha in the score file's name."""
    cloud, web = _sha7(study.get("cloud_sha")), _sha7(study.get("web_sha"))
    rel = study.get("score_file")
    if rel and (cloud is None or web is None):
        try:
            header = json.loads(_abs(rel, root).read_text(encoding="utf-8"))
            cloud, web = cloud or _sha7(header.get("cloud_sha")), web or _sha7(header.get("web_sha"))
        except (OSError, ValueError):
            pass
        named = _SCORE_SHA.search(Path(rel).name)
        cloud = cloud or (named.group(1)[:7] if named else None)
    return {"keel-cloud": cloud, "keel-web": web}


def _stop_step(study: dict) -> str:
    """The step a walk stopped at, by its name (the step's words before its first colon); a stop outside any step
    (an error the journey raised between steps) and a walk that wrote no bundle said as such."""
    if not study.get("bundle"):
        return study.get("error") or "no bundle written"
    step = study.get("failed_step")
    if not step:
        return "no step named (stopped outside a step)"
    return step.split(":", 1)[0].strip()


def walks_of(record: dict, root: Path | None = None) -> dict:
    """Spec 082 FR-3: how many walks reached their end and which stopped (study -- the step), and every move of the
    keel-cloud or keel-web sha from the kick-off's pin, in the order the studies were walked -- named, never refused."""
    studies = record.get("studies") or []
    stopped = [{"study": f"{s['entry']} · {s['scope']}", "step": _stop_step(s)} for s in studies if not s.get("passed")]
    pins = {"keel-cloud": _sha7(record.get("cloud_sha")), "keel-web": _sha7(record.get("web_sha"))}
    moved = []
    for repo, pin in pins.items():
        at = pin
        for s in studies:
            sha = study_shas(s, root)[repo]
            if sha and at and sha != at:
                moved.append({"repo": repo, "from": at, "to": sha, "study": f"{s['entry']} · {s['scope']}"})
            at = sha or at
    return {"walks": len(studies), "ended": len(studies) - len(stopped), "stopped": stopped, "pins": pins,
            "moved": moved}


def compose(studies: list[Study], *, name: str, why: str, door: str, cloud_sha: str, web_sha: str, started: str,
            ended: str, seconds: float, cfg: dict, baseline_path: Path, cycles_dir: Path, root: Path | None = None,
            cloud_branch: str | None = None, web_dirty: bool = False, scores_dir: str = SCORES_REL,
            entries_arg: str | None = None, decisions: list[dict] | None = None,
            people: int | None = None) -> tuple[str, dict]:
    """The cycle record (FR-2): markdown for the founder, and the same facts as a data block the other commands read.
    Spec 087 FR-2: a weak row a decision covers is listed under *Decided before* (`decided_before`), not to advise.
    Spec 106 FR-2: `people`, the number each study sent on the person's own link, where the walk named one."""
    if decisions is None:
        decisions = load_decisions()
    scored = [s for s in studies if s.score_file]
    files = load_files([s.score_file for s in scored], root)
    current, _ = table.split_by_version(files)
    latest = table.latest_per_entry(current)
    head = _head_of(files)
    rows = table.rows(latest) if latest else []
    weak = [table.row_key(r) for r in rows if r["weak"]]
    _, snoozed = dec.split([r for r in rows if r["weak"]], decisions, name, table.row_key)
    routing = sorted({str(f.get("routing_version")) for f in files}) or ["?"]

    baseline = against_baseline = None
    if Path(baseline_path).is_file():
        try:
            base = table.read_baseline(Path(baseline_path))
            baseline = {"cut": base.get("cut"), "score_pct": base.get("score_pct"),
                        "flagged_pct": base.get("flagged_pct"), "studies": base.get("studies")}
            if latest:
                comp = table.compare(base, latest)
                against_baseline = {"verdict": comp["verdict"], "why": comp["why"],
                                    "moved": [m["row"] for m in table.moved_rows(comp, rows)]}
        except (table.TableRefused, rubric.RubricError) as reason:
            against_baseline = {"verdict": "not compared", "why": str(reason), "moved": []}

    previous = None
    prev_path = previous_record(cycles_dir, name)
    if prev_path is not None:
        prev = load_record(prev_path)
        previous = {"record": prev_path.stem, "score_pct": (prev.get("head") or {}).get("score_pct"),
                    "flagged_pct": (prev.get("head") or {}).get("flagged_pct"), "studies": {}}
        now_by = {s.key: s.score_pct for s in scored}
        for s in prev.get("studies") or []:
            key = f"{s['entry']} · {s['scope']}"
            if key in now_by and s.get("score_pct") is not None and now_by[key] is not None:
                previous["studies"][key] = {"then": s["score_pct"], "now": now_by[key],
                                            "delta": round(now_by[key] - s["score_pct"], 1)}
        try:
            prev_files = load_files([s["score_file"] for s in prev.get("studies") or [] if s.get("score_file")], root)
            prev_latest = table.latest_per_entry(table.split_by_version(prev_files)[0])
            if prev_latest and latest:
                comp = table.compare(table.baseline_data(prev_latest, cut=prev_path.stem), latest)
                previous.update(verdict=comp["verdict"], why=comp["why"])
        except (Refused, table.TableRefused, rubric.RubricError) as reason:
            previous.update(verdict="not compared", why=str(reason))

    walk_usd = round(sum(s.walk_usd or 0 for s in studies), 4)
    read_usd = round(sum(s.read_usd or 0 for s in studies), 4)
    data = {
        "record": name, "spec": "079", "why": why, "started": started, "ended": ended, "seconds": seconds,
        "door": door, "entries": sorted({s.entry for s in studies}), "scopes": list(dict.fromkeys(s.scope for s in studies)),
        "entries_arg": entries_arg,
        "cloud_sha": cloud_sha, "cloud_branch": cloud_branch, "web_sha": web_sha, "web_dirty": web_dirty,
        "routing_versions": routing, "rubric_version": rubric.RUBRIC_VERSION,
        "reader": {k: cfg["reader"].get(k) for k in ("model", "effort")},
        "adviser": {k: cfg["adviser"].get(k) for k in ("model", "effort")},
        "bar_pct": cfg["bar_pct"], "weak_rule": cfg["weak"], "scores_dir": scores_dir,
        "studies": [asdict(s) for s in studies], "walks": None, "head": head, "weak_rows": weak,
        "baseline": baseline, "against_baseline": against_baseline, "previous": previous,
        "cost": {"walk_usd": walk_usd, "read_usd": read_usd, "total_usd": round(walk_usd + read_usd, 4)},
    }
    data["walks"] = walks_of(data, root)
    if people:                                      # spec 106: absent on a walk that capped nobody, as a 079 record reads
        data["people"] = int(people)
    if snoozed:                                     # spec 087: absent when nothing is decided, as a 079 record reads
        data["decided_before"] = snoozed
    return render_record(data), data


def _pct(value) -> str:
    return "–" if value is None else f"{value:.1f}%"


def render_record(d: dict) -> str:
    head, base, bar = d.get("head") or {}, d.get("baseline"), d["bar_pct"]
    rel = f"quality/cycles/{d['record']}.md"
    entries = ",".join(d["entries"])
    scopes = ",".join(d["scopes"])
    lines = [f"# Quality cycle {d['record']}", "",
             f"**Why this cycle** (the founder's words): {d['why'] or '(a dry run: no why)'}", "",
             f"Spec 079. Walked {d['started']} -> {d['ended']} ({round((d['seconds'] or 0) / 60, 1)} min) through "
             f"DOOR={d['door']} on keel-cloud `{d['cloud_sha']}` ({d.get('cloud_branch') or '?'}) and keel-web "
             f"`{d['web_sha']}`{' (dirty)' if d.get('web_dirty') else ''}; routing v{', v'.join(d['routing_versions'])}; "
             f"RUBRIC_VERSION {d['rubric_version']}; reader {d['reader']['model']} ({d['reader']['effort']}); the bar "
             f"{bar:.0f}%; weak = a 0 in {d['weak_rule']['zero_entries']} entries or a mean under "
             f"{d['weak_rule']['mean_under']} (quality/cycle.toml)"
             + (f"; {d['people']} people a study on the person's own link (spec 106)" if d.get("people") else "")
             + ".", "",
             "## The head", "",
             f"- **This cycle**: score_pct **{_pct(head.get('score_pct'))}**, flagged {_pct(head.get('flagged_pct'))} of "
             f"{head.get('screens', 0)} screens (founder {_pct((head.get('founder') or {}).get('score_pct'))}, respondent "
             f"{_pct((head.get('respondent') or {}).get('score_pct'))}"
             + "".join(f"; {k} {_pct(v['score_pct'])}" for k, v in (head.get("by_scope") or {}).items()) + ")",
             *table.walks_lines(d.get("walks")),
             (f"- **The baseline** (cut {base['cut']}): score_pct {_pct(base.get('score_pct'))}, flagged "
              f"{_pct(base.get('flagged_pct'))}" if base else "- **The baseline**: none cut yet"),
             f"- **The bar**: {bar:.0f}% -- this cycle "
             f"{'meets it' if head.get('score_pct') is not None and head['score_pct'] >= bar else 'is BELOW it'}", ""]
    ab = d.get("against_baseline")
    lines += ["## Against the baseline", ""]
    if ab:
        lines += [f"**Verdict: {ab['verdict'].upper()}** -- {ab['why']}.", ""]
        lines += ([f"Moved since the baseline ({len(ab['moved'])}; their *instead* lines in TABLE.md): "
                   + "; ".join(ab["moved"])] if ab["moved"] else ["No row moved since the baseline."]) + [""]
    else:
        lines += ["No baseline is cut yet: this cycle is compared with nothing. `make quality-accept` cuts one from a "
                  "cycle, on the founder's word.", ""]
    prev = d.get("previous")
    lines += ["## Against the previous cycle", ""]
    if prev:
        lines += [f"Previous: `quality/cycles/{prev['record']}.md`, score_pct {_pct(prev.get('score_pct'))} -> "
                  f"{_pct(head.get('score_pct'))}. **Verdict: {str(prev.get('verdict', 'not compared')).upper()}** -- "
                  f"{prev.get('why', '')}.", ""]
        if prev["studies"]:
            lines += ["| study | then | now | delta |", "|---|---|---|---|"]
            lines += [f"| {k} | {_pct(v['then'])} | {_pct(v['now'])} | {v['delta']:+.1f} |"
                      for k, v in prev["studies"].items()]
            lines.append("")
    else:
        lines += ["No earlier cycle record.", ""]
    lines += ["## The studies", "",
              "| study | bundle | walk | score file | score_pct | flagged | walk $ | read $ | minutes |",
              "|---|---|---|---|---|---|---|---|---|"]
    for s in d["studies"]:
        walk = ("passed" if s.get("passed") else f"failed at {s.get('failed_step')!r}") if s.get("bundle") else "--"
        if s.get("error"):
            walk += f"; {s['error']}"
        minutes = round(((s.get("walk_s") or 0) + (s.get("read_s") or 0)) / 60, 1)
        lines.append(" | ".join(["| " + f"{s['entry']} · {s['scope']}", f"`{s.get('bundle') or '--'}`", walk,
                                 f"`{s['score_file']}`" if s.get("score_file") else "--", _pct(s.get("score_pct")),
                                 _pct(s.get("flagged_pct")), f"{s['walk_usd']}" if s.get("walk_usd") is not None else "--",
                                 f"{s['read_usd']}" if s.get("read_usd") is not None else "--", f"{minutes} |"]))
    snoozed = d.get("decided_before") or []
    decided = {s["row"] for s in snoozed}
    to_advise = [k for k in d["weak_rows"] if k not in decided]
    if snoozed:
        lines += ["", f"## Weak rows ({len(d['weak_rows'])}: {len(to_advise)} to advise, {len(snoozed)} decided before) "
                      "-- their fix locations and *instead* lines are in TABLE.md", ""]
        lines += [f"- {k}" for k in to_advise] or ["- none to advise: every weak row was decided before (below)"]
        lines += ["", f"## Decided before ({len(snoozed)}) -- snoozed by `quality/decisions.toml` (spec 087), not sent "
                      "to the adviser", ""]
        lines += [dec.line(s) for s in snoozed]
    else:
        lines += ["", f"## Weak rows ({len(d['weak_rows'])}) -- their fix locations and *instead* lines are in TABLE.md",
                  ""]
        lines += [f"- {k}" for k in d["weak_rows"]] or ["- none"]
    advise_count = (f"one call per weak row not decided before: {len(to_advise)}" if snoozed
                    else f"one call per weak row: {len(d['weak_rows'])}")
    c = d["cost"]
    lines += ["", "## Cost and time", "",
              f"Walks ${c['walk_usd']} (Keel's AI, or the CLI's list-price equivalent on the founder's plan), readers "
              f"${c['read_usd']} (the founder's plan), ${c['total_usd']} in all; {round((d['seconds'] or 0) / 60, 1)} "
              "minutes.", "",
              "## What the founder decides now (quality/CYCLE.md)", "",
              f"1. **Advise** (paid, {advise_count}): `make quality-advise CYCLE={rel}`",
              f"2. **Rerun** after a keel-cloud change is merged: `make quality-walk ENTRIES={entries} SCOPES={scopes} "
              f"DOOR={d['door']}" + (f" PEOPLE={d['people']}" if d.get("people") else "")
              + " WHY=\"<why, in his words>\"`",
              f"3. **Accept** (free, on his word): `make quality-accept CYCLE={rel}`", "",
              _DATA, "```json", json.dumps(d, indent=1, ensure_ascii=False), "```", ""]
    return "\n".join(lines)


def load_record(path: str | Path) -> dict:
    """A cycle record's data block -- refused by name when there is no such record or it carries none."""
    if not path:
        raise Refused("no CYCLE -- name a cycle record, `CYCLE=quality/cycles/<yyyymmdd>-<cloud7>.md` (the latest is "
                      f"{_latest_name()})")
    p = Path(path)
    if not p.is_file():
        for candidate in (REPO / p, CYCLES_DIR / p, CYCLES_DIR / f"{p.name}.md"):
            if candidate.is_file():
                p = candidate
                break
        else:
            raise Refused(f"no cycle record {path} -- the records are quality/cycles/<yyyymmdd>-<cloud7>.md (the latest "
                          f"is {_latest_name()})")
    text = p.read_text(encoding="utf-8")
    match = re.search(re.escape(_DATA) + r"\s*```json\s*(.*?)```", text, re.S)
    if not match:
        raise Refused(f"{p} is not a cycle record: it carries no `{_DATA}` block")
    data = json.loads(match.group(1))
    data["_path"] = str(p)
    return data


def _latest_name() -> str:
    found = record_files(CYCLES_DIR)
    return f"quality/cycles/{found[-1].name}" if found else "none yet"


def table_head(record: dict, *, baseline_path: Path | None = None) -> dict:
    """What `make read-table CYCLE=` puts at the top of TABLE.md (FR-3): this cycle, the baseline, the bar."""
    base = None
    path = Path(baseline_path or table.BASELINE_PATH)
    if path.is_file():
        try:
            b = table.read_baseline(path)
            base = {"cut": b.get("cut"), "score_pct": b.get("score_pct"), "flagged_pct": b.get("flagged_pct")}
        except (table.TableRefused, rubric.RubricError):
            base = None
    head = record.get("head") or {}
    return {"record": f"quality/cycles/{record['record']}.md", "cloud_sha": record.get("cloud_sha"),
            "studies": sum(1 for s in record.get("studies") or [] if s.get("score_file")),
            # spec 082 FR-3: a record from before 082 carries no `walks`; its studies and score files say the same
            "walks": record.get("walks") or walks_of(record),
            "this": {"score_pct": head.get("score_pct"), "flagged_pct": head.get("flagged_pct")},
            "baseline": base, "bar_pct": record.get("bar_pct") or rubric.BAR_PCT}


def walk(argv=None, *, runner=subprocess.run, env=None, which=shutil.which) -> int:
    p = argparse.ArgumentParser(prog="make quality-walk", description="Spec 079 FR-2: the kick-off.")
    p.add_argument("--entries", default="")
    p.add_argument("--scopes", default="")
    p.add_argument("--door", default="")
    p.add_argument("--build", default="")
    p.add_argument("--why", default="")
    p.add_argument("--people", default="", help="spec 106 FR-2: people a study (default quality/cycle.toml's)")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--cycles-dir", default=str(CYCLES_DIR))
    p.add_argument("--decisions", default="", help=argparse.SUPPRESS)
    a = p.parse_args(argv)
    try:
        cfg = load_config()
        decisions = load_decisions(a.decisions or None)       # spec 087: refused before any paid step, not after
        entries = resolve_entries(a.entries, cfg)
        scopes = resolve_scopes(a.scopes, cfg)
        door = (a.door or cfg["door"]).strip().lower()
        people = resolve_people(a.people, cfg)
        cloud, web = checkouts()
        hard, soft = preflight(entries=entries, scopes=scopes, door=door, why=a.why, build=a.build or None,
                               dry=a.dry_run, cloud=cloud, env=env, which=which)
        if hard:
            raise Refused("make quality-walk refuses: " + "; ".join(hard))
    except Refused as reason:
        print(str(reason), file=sys.stderr)
        return 2
    cloud7, web7 = git_sha(cloud), git_sha(web)
    now = dt.datetime.now(dt.timezone.utc)
    cycles_dir = Path(a.cycles_dir)
    name = record_name(now.strftime("%Y%m%d"), cloud7, cycles_dir)
    work = RUNS_DIR / "quality-walk" / f"{now.strftime('%Y%m%dT%H%M%SZ')}-{name}"
    steps = plan_steps(entries, scopes, door, work, people)
    record_path = cycles_dir / f"{name}.md"
    if a.dry_run:
        print(f"quality-walk DRY RUN -- nothing runs, nothing is written. WHY: {a.why or '(none: a paid walk needs one)'}")
        print(f"keel-cloud {cloud} at {cloud7} ({git_branch(cloud)}); keel-web {web} at {web7}; DOOR={door}")
        print(f"studies: {len(entries) * len(scopes)} ({', '.join(entries)} x {', '.join(scopes)}); reader "
              f"{cfg['reader']['model']} ({cfg['reader']['effort']}); the bar {cfg['bar_pct']:.0f}%; "
              + (f"{people} people a study on the person's own link, the decision-makers whole (spec 106)" if people
                 else "every person each study's scope sends"))
        for warning in soft:
            print(f"  a paid walk would refuse: {warning}")
        for i, step in enumerate(steps, 1):
            argv = [x.replace("CYCLE=<record>", f"CYCLE={_rel(record_path)}").replace(f"{REPO}/", "")
                    for x in step["argv"]]
            print(f"  {i:>3}. {' '.join(argv[4:]) if argv[:1] == ['make'] else ' '.join(argv)}"
                  + (f"   > {_rel(step['log'])}" if step.get("log") else ""))
        print(f"decisions: {len(decisions)} in quality/decisions.toml (spec 087) -- a weak row one covers is listed "
              "under Decided before, not advised")
        print(f"then the record: {_rel(record_path)} (and TABLE.md's head); commit both with the score files")
        return 0
    print(f"quality-walk: {len(entries) * len(scopes)} studies on keel-cloud {cloud7}, keel-web {web7}, DOOR={door}"
          + (f", {people} people a study" if people else "") + f"; logs under {work}")
    started, t0 = now.isoformat(timespec="seconds"), time.monotonic()
    studies = []
    by_study: dict = {}
    for step in steps:
        if step["study"]:
            by_study.setdefault(step["study"], []).append(step)
    for (entry, scope), three in by_study.items():
        print(f"  {entry} · {scope}: walking")
        study = walk_one(entry, scope, three, door=door, runner=runner)
        if study.cloud_sha is None or study.web_sha is None:      # spec 082 FR-3: no bundle stack -- the checkouts now
            try:
                study.cloud_sha, study.web_sha = study.cloud_sha or git_sha(cloud), study.web_sha or git_sha(web)
            except Refused:
                pass
        for repo, pin, sha in (("keel-cloud", cloud7, study.cloud_sha), ("keel-web", web7, study.web_sha)):
            if sha and sha != pin:
                print(f"  {entry} · {scope}: walked on {repo} {sha}, not the kick-off's {pin} -- recorded, not refused")
        print(f"  {entry} · {scope}: " + (f"score_pct {study.score_pct}, flagged {study.flagged_pct}% "
                                         f"({study.score_file})" if study.score_file else f"NOT SCORED -- {study.error}"))
        studies.append(study)
    ended = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    text, data = compose(studies, name=name, why=a.why.strip(), door=door, cloud_sha=cloud7, web_sha=web7,
                         started=started, ended=ended, seconds=round(time.monotonic() - t0, 1), cfg=cfg,
                         baseline_path=table.BASELINE_PATH, cycles_dir=cycles_dir, cloud_branch=git_branch(cloud),
                         web_dirty=bool(git_dirty(web)), entries_arg=a.entries, decisions=decisions, people=people)
    cycles_dir.mkdir(parents=True, exist_ok=True)
    record_path.write_text(text, encoding="utf-8")
    table_argv = [x.replace("CYCLE=<record>", f"CYCLE={record_path}") for x in steps[-1]["argv"]]
    if not table.BASELINE_PATH.is_file():
        table_argv = [x for x in table_argv if x != "BASELINE=1"]           # the first cycle: nothing to compare with
    if _run(table_argv, str(work / "read-table.log"), runner) != 0 and "BASELINE=1" in table_argv:
        _run([x for x in table_argv if x != "BASELINE=1"], str(work / "read-table.log"), runner)   # a baseline refused
    head = data.get("head") or {}
    print(f"cycle record: {_rel(record_path)} -- score_pct {head.get('score_pct')}% against the bar of "
          f"{cfg['bar_pct']:.0f}%, {len(data['weak_rows'])} weak row(s)"
          + (f" ({len(data['decided_before'])} decided before)" if data.get("decided_before") else "")
          + (f", {data['against_baseline']['verdict'].upper()} than the baseline" if data.get("against_baseline") else ""))
    print(f"commit: git add quality/scores quality/TABLE.md {_rel(record_path)}")
    return 0 if all(s.score_file for s in studies) else 1


# ------------------------------------------------------------------------------------------------ the adviser

def adviser_template(path: Path | None = None) -> str:
    text = Path(path or ADVISER_PROMPT).read_text(encoding="utf-8")
    begin, end = "<!-- advise:begin -->", "<!-- advise:end -->"
    if text.count(begin) != 1 or text.count(end) != 1:
        raise Refused(f"{ADVISER_PROMPT.name} must carry one `advise:begin` and one `advise:end` marker")
    return text.split(begin, 1)[1].split(end, 1)[0].strip() + "\n"


def _criteria_lines(row: dict) -> str:
    anchors = {c["id"]: c for c in (rubric.g_criteria() if row["kind"] == "insights" else rubric.criteria())}
    out = []
    for c in row["weak_on"]:
        a = anchors.get(c, {})
        zeros, mean = row["zero_entries"].get(c) or [], row["means"].get(c)
        reason = (f"a 0 in {len(zeros)} entries ({', '.join(zeros)})" if len(zeros) >= rubric.WEAK_ZERO_ENTRIES
                  else f"mean {mean} under {rubric.WEAK_MEAN}")
        out.append(f"- {c.upper()} {a.get('question', '')} -- 2: {a.get('2', '')} / 1: {a.get('1', '')} / 0: "
                   f"{a.get('0', '')}. Weak by {reason}.")
    return "\n".join(out)


def failing_screens(row: dict, files: list[dict], *, limit: int = 12) -> list[str]:
    """The screens of this row that scored under 2 on a criterion the row is weak on, with whys and instead lines."""
    out = []
    for f in files:
        if table.scope_of(f) != row["scope"]:
            continue
        if row["kind"] == "insights":
            for r in f.get("insights") or []:
                if (r.get("dimension") or "-") != row["dimension"]:
                    continue
                low = [c for c in row["weak_on"] if r.get(c, 2) < 2]
                if low:
                    out.append(f"- {f['entry']} · follow-up line {r.get('line')!r} (link {r.get('link')}): "
                               + "; ".join(f"{c.upper()} {r[c]} -- {r['whys'].get(c, '')}" for c in low))
            continue
        for s in f["screens"]:
            if (s.get("dimension") or "-", s["audience"], s["kind"]) != (row["dimension"], row["audience"], row["kind"]):
                continue
            low = [c for c in row["weak_on"] if s.get(c) is not None and s[c] < 2]
            if low:
                whys = "; ".join(f"{c.upper()} {s[c]} -- {s.get('why' + c[1:], '')}" for c in low)
                out.append(f"- {f['entry']} · `{s['screen']}`" + (f" (link {s['link']})" if s.get("link") else "")
                           + f": {whys}" + (f". Instead: {s['instead']}" if s.get("instead") else ""))
    return out[:limit] or ["- (no screen under 2 on the weak criteria: the row is weak by its mean)"]


def _section(text: str, heading: str) -> str | None:
    match = re.search(rf"^(#{{2,4}})\s+{re.escape(heading)}\s*$", text, re.M)
    if not match:
        return None
    level = len(match.group(1))
    rest = text[match.end():]
    stop = re.search(rf"^#{{2,{level}}}\s", rest, re.M)
    return (match.group(0) + rest[:stop.start() if stop else len(rest)]).strip()


def current_text(row: dict, *, cloud: Path, cfg: dict, sha: str | None = None) -> dict:
    """The current text at the row's fix location, read from the keel-cloud checkout (FR-4): `{where, text}`."""
    category, place = row["fix"]["category"], row["fix"]["place"]
    cap = int(cfg["adviser"]["max_quote_chars"])
    at = f" (keel-cloud at `{sha}`)" if sha else ""
    dimension = None if row["dimension"] == "-" else row["dimension"]
    if category == "registry row" and dimension:
        path = cloud / REGISTRY_REL
        registry = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        dims = {d.get("key"): d for d in registry.get("dimensions") or []}
        if dimension not in dims:
            return {"where": f"{REGISTRY_REL}{at}", "text": f"(no registry row named {dimension})"}
        if row["audience"] == "founder":
            block = "founder"
        elif row["kind"] == "follow_up":
            block = "follow_up"
        else:
            block = "respondent"
        body = {block: dims[dimension].get(block)}
        if block == "follow_up" and dims[dimension].get("no_follow_up"):
            body["no_follow_up"] = dims[dimension]["no_follow_up"]
        return {"where": f"`{REGISTRY_REL}`, dimension `{dimension}`, its `{block}` block{at}",
                "text": json.dumps(body, indent=1, ensure_ascii=False)[:cap]}
    if category == "shared file":
        named = re.findall(r"([a-z][a-z0-9-]*\.md)", place)
        if named:
            path = cloud / INSTRUCTIONS_REL / named[0]
            if not path.is_file():
                return {"where": f"`{INSTRUCTIONS_REL / named[0]}`{at}", "text": "(the file is not in the checkout)"}
            text = path.read_text(encoding="utf-8")
            heading = (cfg["adviser"].get("sections") or {}).get(row["kind"])
            part = _section(text, heading) if heading else None
            where = f"`{INSTRUCTIONS_REL / named[0]}`" + (f", section *{heading}*" if part else ", the whole file") + at
            return {"where": where, "text": (part or text)[:cap]}
    return {"where": place, "text": f"(no model writes these words: {place}. Propose the words; a code change in "
                                    "keel-cloud or keel-web carries them.)"}


def adviser_prompt(row: dict, files: list[dict], *, cloud: Path, cfg: dict, sha: str | None = None,
                   template: str | None = None, declined: list[dict] | None = None) -> str:
    """The adviser's prompt for one weak row; `declined` (spec 087 FR-3) the decisions the founder has said no to on
    it, their whys in full."""
    current = current_text(row, cloud=cloud, cfg=cfg, sha=sha)
    means = ", ".join(f"{c.upper()} {v}" for c, v in row["means"].items())
    values = {
        "row": (f"{table.row_key(row)} -- {row['screens']} screen(s) over {', '.join(row['entries'])}; means {means}; "
                f"weak on {', '.join(c.upper() for c in row['weak_on'])}"),
        "criteria": _criteria_lines(row),
        "screens": "\n".join(failing_screens(row, files)),
        "location": f"{row['fix']['category']}: {row['fix']['place']}" + "".join(
            f"\n{also}" for also in row["fix"].get("also") or []),
        "current": f"{current['where']}:\n\n{current['text']}",
        "ladder": LADDER,
        "declined": dec.prompt_lines(declined or []),
    }
    return readers.fill(template or adviser_template(), values)


def parse_advice(raw: str, *, declined_ids: tuple | list = ()) -> dict:
    """The adviser's answer. `reopens` (spec 087 FR-3) is the ids of the declined decisions the edit goes against:
    required as a list when the prompt quoted any, else optional (an answer of 079's shape reads as reopening none)."""
    body = rubric.extract_json(raw)
    rung = str(body.get("rung") or "").strip().lower()
    if rung not in RUNGS:
        raise rubric.RubricError(f"rung must be one of {RUNGS}; got {body.get('rung')!r}")
    why = str(body.get("why") or "").strip()
    if not why:
        raise rubric.RubricError("no why")
    aware = body.get("persona_aware")
    if not isinstance(aware, bool):
        raise rubric.RubricError(f"persona_aware must be true or false (spec 081 FR-6); got {aware!r}")
    reopens = body.get("reopens")
    if reopens is None and not declined_ids:
        reopens = []
    if not isinstance(reopens, list) or not all(isinstance(i, str) for i in reopens):
        raise rubric.RubricError(f"reopens must be a list of decision ids (spec 087 FR-3); got {reopens!r}")
    return {"new_text": str(body.get("new_text") or "").strip(), "why": why, "rung": rung, "persona_aware": aware,
            "reopens": [i.strip() for i in reopens if i.strip()]}


#: Spec 081 FR-6 (design §5a): a proposal that adds a condition on an industry, a role, a country or a product -- *if
#: the people are mariners, say nautical miles* -- is a special case, refused whatever the adviser's own flag says.
#: The words a condition opens with, then who or what it is on.
_SUBJECT = (r"(?:\{\w*(?:actor|segment|market|country|role|industry|trade|product)\w*\}"
            r"|\b(?:\w*(?:actor|segment|market|country|role|industry|trade|product)\w*|people|person|respondents?|"
            r"strangers?|founders?|users?|customers?|buyers?|workers?|sector)\b)")
_CONDITION = re.compile(
    r"\b(?:if|when|whenever|where|unless|in\s+case)\s+(?:the\s+|a\s+|an\s+|your\s+|their\s+)?" + _SUBJECT +
    r"\s+(?:is|are|work|works|sells?|makes?|runs?|names?|says?|includes?|mentions?|equals?|==?|in|from|at)\b",
    re.I)


def special_case(proposal: dict) -> str | None:
    """Why a proposal is refused as a special case (spec 081 FR-6), or None: the adviser marked it not persona-aware,
    or its text adds a condition on who the people are, their trade, their country or the product."""
    if proposal.get("persona_aware") is not True:
        return "the adviser marked it persona_aware false: a special case, not the persona handed to the writer"
    found = _CONDITION.search(proposal.get("new_text") or "")
    if found:
        return (f"its text adds a condition on who the people are ({found.group(0)!r}): a special case -- the fix is "
                "the writer handed the persona, for every trade at once (design §5a)")
    return None


def reopened(proposal: dict, declined: list[dict]) -> str | None:
    """Why a proposal is refused as reopening what the founder declined (spec 087 FR-3), or None: the adviser named a
    declined decision its edit goes against -- refused as 081 FR-6 refuses a special case, naming the decision."""
    ids = proposal.get("reopens") or []
    if not ids:
        return None
    why = {d["id"]: d["why"].strip() for d in declined}
    named = "; ".join(f"{i} ({why[i]})" if i in why else i for i in ids)
    return f"it reopens what the founder has already declined: {named}"


def cycle_files(record: dict, root: Path | None = None) -> list[dict]:
    files = load_files([s["score_file"] for s in record.get("studies") or [] if s.get("score_file")], root)
    if not files:
        raise Refused(f"the cycle {record['record']} has no score file: nothing was read")
    _, aside = table.split_by_version(files)
    if aside:
        raise Refused(f"the cycle {record['record']} was read at rubric version "
                      f"{sorted({f['rubric_version'] for f in aside})}, the rubric is at {rubric.RUBRIC_VERSION} -- "
                      "two rubric versions are never mixed; walk a new cycle")
    return files


def weak_rows(files: list[dict]) -> list[dict]:
    return [r for r in table.rows(table.latest_per_entry(files)) if r["weak"]]


def render_advice(record: dict, proposals: list[dict], *, adviser: dict, quoted_at: str, cost: float, calls: int,
                  seconds: float, calls_dir: str, decided_before: list[dict] | None = None) -> str:
    stem = record["record"]
    moved = "" if quoted_at == record.get("cloud_sha") else (
        f" -- **the checkout has moved since the cycle measured `{record.get('cloud_sha')}`**: the quotes are today's")
    lines = [f"# Advice on cycle {stem}", "",
             f"Spec 079 FR-4. {len(proposals)} weak row(s) of `quality/cycles/{stem}.md`, one call each, adviser "
             f"{adviser['model']} ({adviser['effort']}) through the claude CLI; the current text quoted from keel-cloud "
             f"`{quoted_at}`{moved}. ${cost} in {calls} call(s), {seconds} s; every prompt and answer under "
             f"`{calls_dir}`."
             + (f" {len(decided_before)} more decided before, listed at the end (spec 087): not advised."
                if decided_before else ""), "",
             "**Nothing here is applied.** The founder says which proposals to take; a taken proposal becomes a "
             "keel-cloud spec (the registry row or the instruction file, with the spoken-form acceptance line where a "
             "respondent wording moves), built, gated and merged like any other, and then the cycle is walked again "
             "(quality/CYCLE.md step 4).", ""]
    for i, p in enumerate(proposals, 1):
        lines += [f"## {i}. {p['row']} -- weak on {', '.join(c.upper() for c in p['weak_on'])}", "",
                  f"Fix location: **{p['fix']['category']}** -- {p['fix']['place']}. Quoted: {p['where']}.", ""]
        for also in p["fix"].get("also") or []:
            lines += [f"Fix for {also}.", ""]
        if p.get("error"):
            lines += [f"**No proposal**: {p['error']}", ""]
        elif p.get("refused"):
            if p.get("refused_by") == "spec 087 FR-3":
                lines += [f"**Refused -- not a proposal** (spec 087 FR-3): {p['refused']}. The model's first idea "
                          "reopened a decision the founder has already made and it was not taken; the row stays open "
                          "for a proposal that keeps to it.", ""]
            else:
                lines += [f"**Refused -- not a proposal** (spec 081 FR-6): {p['refused']}. The model's first idea was "
                          "a special case and it was not taken; the row stays open for a persona-aware proposal.", ""]
            lines += ["<details><summary>The refused text</summary>", "", "```text",
                      p.get("new_text") or "(empty)", "```", "", f"Its why: {p.get('why', '')}", "", "</details>", ""]
        else:
            lines += [f"Rung: **{p['rung']}**", "", f"Why: {p['why']}", "", "The proposed text:", "", "```text",
                      p["new_text"] or "(no change of words: see the rung)", "```", ""]
        lines += ["<details><summary>The current text</summary>", "", "```text", p["current"], "```", "", "</details>",
                  "", "Taken: _(the founder's word)_", ""]
    body = {"cycle": stem, "quoted_at": quoted_at, "adviser": adviser, "proposals": proposals}
    if decided_before:
        lines += [f"## Decided before ({len(decided_before)}) -- not advised: `quality/decisions.toml` (spec 087)", "",
                  "The founder decided these rows before; each stays snoozed while its decision holds (a taken one "
                  "until its spec is merged, then the row competes again).", ""]
        lines += [dec.line(s) for s in decided_before] + [""]
        body["decided_before"] = decided_before
    lines += [_ADVICE_DATA, "```json", json.dumps(body, indent=1, ensure_ascii=False), "```", ""]
    return "\n".join(lines)


def advise(argv=None, *, runner=subprocess.run) -> int:
    p = argparse.ArgumentParser(prog="make quality-advise", description="Spec 079 FR-4: the adviser.")
    p.add_argument("--cycle", default="")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--cloud", default="", help=argparse.SUPPRESS)
    p.add_argument("--out", default="", help="the advice file (default quality/cycles/<record>-advice.md)")
    p.add_argument("--decisions", default="", help=argparse.SUPPRESS)
    a = p.parse_args(argv)
    try:
        cfg = load_config()
        decisions = load_decisions(a.decisions or None)
        record = load_record(a.cycle)
        files = cycle_files(record)
        cloud = Path(a.cloud) if a.cloud else checkouts()[0]
        try:
            sha = git_sha(cloud)
        except Refused:
            sha = None
        weak = weak_rows(files)
        rows, snoozed = dec.split(weak, decisions, record["record"], table.row_key)      # spec 087 FR-2
        declined = [dec.declined_for(r, decisions, record["record"]) for r in rows]     # spec 087 FR-3
        template = adviser_template()
        prompts = [(r, adviser_prompt(r, files, cloud=cloud, cfg=cfg, sha=sha, template=template, declined=no))
                   for r, no in zip(rows, declined)]
    except (Refused, rubric.RubricError) as reason:
        print(f"make quality-advise refuses: {reason}", file=sys.stderr)
        return 2
    stem = record["record"]
    if not weak:
        print(f"cycle {stem}: no weak row -- nothing to advise, no call made")
        return 0

    def decided_lines():
        if snoozed:
            print(f"## Decided before ({len(snoozed)}) -- quality/decisions.toml (spec 087): snoozed, not sent")
            for s in snoozed:
                print(dec.line(s))
    if not rows:
        decided_lines()
        print(f"cycle {stem}: {len(weak)} weak row(s), every one decided before (quality/decisions.toml, spec 087) -- "
              "nothing to advise, no call made" + (", nothing written" if a.dry_run else ""))
        return 0
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if a.dry_run:
        for i, (row, prompt) in enumerate(prompts, 1):
            print("=" * 100)
            print(f"[{i}/{len(prompts)}] {table.row_key(row)}")
            print("=" * 100)
            print(prompt)
        decided_lines()
        print(f"dry run: {len(prompts)} adviser prompt(s) for cycle {stem}; no call made, nothing written"
              + (f"; {len(snoozed)} weak row(s) decided before, not sent" if snoozed else ""))
        return 0
    run_dir = RUNS_DIR / f"{stamp}-advise-{stem}"
    run_dir.mkdir(parents=True, exist_ok=True)  # the CLI runs with this as its cwd: the probe died on a missing dir (2026-10-28, the first live run)
    reader = readers.Reader({"model": cfg["adviser"]["model"], "effort": cfg["adviser"]["effort"],
                             "timeout_s": cfg["adviser"]["timeout_s"]}, run_dir, runner=runner)
    if not reader.available():
        print("make quality-advise refuses: the `claude` binary is not on PATH -- the adviser runs through the claude "
              "CLI as the readers do (spec 079 FR-4)", file=sys.stderr)
        return 2
    said = reader.ask("probe", readers.PROBE_PROMPT)
    if said["error"] or not (said["answer"] or "").strip():
        print(f"make quality-advise refuses: `claude -p` could not answer a one-word probe ({said['error'] or 'empty'})",
              file=sys.stderr)
        return 2
    started = time.monotonic()
    proposals = []
    for i, ((row, prompt), no) in enumerate(zip(prompts, declined), 1):
        current = current_text(row, cloud=cloud, cfg=cfg, sha=sha)
        entry = {"row": table.row_key(row), "weak_on": row["weak_on"], "fix": row["fix"], "where": current["where"],
                 "current": current["text"]}
        said = reader.ask(f"advise-{i:02d}", prompt)
        try:
            if said["error"]:
                raise rubric.RubricError(said["error"])
            entry.update(parse_advice(said["answer"], declined_ids=[d["id"] for d in no]))
            refused = special_case(entry)
            if refused:
                entry["refused"] = refused
            elif reopened(entry, no):
                entry.update(refused=reopened(entry, no), refused_by="spec 087 FR-3")
        except rubric.RubricError as reason:
            entry["error"] = f"the answer could not be read ({reason})"
        proposals.append(entry)
        said_of = (("REFUSED: reopens a decision" if entry.get("refused_by") else "REFUSED: a special case")
                   if entry.get("refused") else entry.get("rung") or "unread")
        print(f"  {entry['row']:<72} {said_of}")
    out = Path(a.out) if a.out else Path(record["_path"]).with_name(f"{stem}-advice.md")
    cost = round(sum(c["cost_usd"] for c in reader.calls if not c["cached"]), 4)
    out.write_text(render_advice(record, proposals, adviser={k: cfg["adviser"][k] for k in ("model", "effort")},
                                 quoted_at=sha or "?", cost=cost, calls=len(reader.calls),
                                 seconds=round(time.monotonic() - started, 1), calls_dir=_rel(run_dir / "calls"),
                                 decided_before=snoozed),
                   encoding="utf-8")
    refused = sum(1 for p in proposals if p.get("refused"))
    print(f"advice: {_rel(out)} ({len(proposals)} proposal(s), ${cost}"
          + (f"; {refused} refused (a special case, or a decision reopened), recorded by row" if refused else "")
          + (f"; {len(snoozed)} decided before, listed at the end" if snoozed else "")
          + "); nothing applied -- commit it, and the founder says which to take")
    return 0


# ------------------------------------------------------------------------------------------------ the acceptance

def bundle_dir(study: dict, runs_dir: Path) -> Path | None:
    for candidate in (study.get("bundle_path"), str(Path(runs_dir) / str(study.get("bundle")))):
        if candidate and Path(candidate).is_dir():
            return Path(candidate)
    return None


def accept(argv=None) -> int:
    from evals import gallery                                            # noqa: PLC0415

    p = argparse.ArgumentParser(prog="make quality-accept", description="Spec 079 FR-6: the acceptance.")
    p.add_argument("--cycle", default="")
    p.add_argument("--out", default="", help="the gallery snapshot (default keel-web's public/sample)")
    p.add_argument("--runs-dir", default=str(RUNS_DIR), help="where the cycle's bundles are, by name")
    p.add_argument("--quality-out", default=str(QUALITY), help="where BASELINE.md and baselines/ are written")
    p.add_argument("--provenance-dir", default=str(gallery.PROVENANCE_DIR))
    p.add_argument("--today", default="", help=argparse.SUPPRESS)
    a = p.parse_args(argv)
    try:
        cfg = load_config()
        record = load_record(a.cycle)
        files = cycle_files(record)
        out = Path(a.out) if a.out else checkouts()[1] / "public" / "sample"
    except (Refused, rubric.RubricError) as reason:
        print(f"make quality-accept refuses: {reason}", file=sys.stderr)
        return 2
    stem = record["record"]
    quality_out = Path(a.quality_out)
    baseline_path = quality_out / "BASELINE.md"
    today = a.today or dt.date.today().isoformat()
    had = baseline_path.is_file()
    quality_out.mkdir(parents=True, exist_ok=True)
    try:
        table.cut_baseline(files, None, path=baseline_path, archive_dir=quality_out / "baselines", today=today)
    except table.TableRefused as reason:
        print(f"make quality-accept refuses: {reason}", file=sys.stderr)
        return 2
    head = record.get("head") or {}
    print(f"baseline: {baseline_path} cut {today} from cycle {stem} (score_pct {head.get('score_pct')}%)"
          + (f"; the old one kept under {quality_out / 'baselines'}/" if had else "; the first baseline"))

    # the gallery, from this cycle's bundles, behind the readers' gate
    names = gallery.load_names()
    named = {n.entry: n for n in names}
    runs, set_aside = [], []
    for s in record.get("studies") or []:
        if not s.get("bundle"):
            set_aside.append(f"{s['entry']} · {s['scope']}: no bundle ({s.get('error') or 'the walk wrote none'})")
            continue
        d = bundle_dir(s, Path(a.runs_dir))
        if d is None:
            set_aside.append(f"{s['bundle']} ({s['entry']} · {s['scope']}): the bundle folder is not on this machine "
                             f"(looked in {a.runs_dir})")
        elif s["entry"] not in named:
            set_aside.append(f"{s['bundle']} ({s['entry']} · {s['scope']}): {s['entry']} has no row in "
                             "instructions/gallery_names.toml -- add its attribution first")
        else:
            runs.append(d)
    g = cfg["gallery"]
    scores_dir = _abs(record.get("scores_dir") or SCORES_REL)
    passing, refused = gallery.score_gate(runs, scores_dir, bar_pct=cfg["bar_pct"], refuse_flagged=g["refuse_flagged"],
                                          refuse_under_bar=g["refuse_under_bar"])
    for line in set_aside:
        print(f"gallery: set aside {line}")
    for line in refused:
        print(f"gallery: refused {line}")
    if not passing:
        print("gallery: no bundle of this cycle passes the readers' gate -- the gallery is left as it is")
        return 0
    picked, notes = gallery.one_per_entry(passing, list(g["scope_order"]))
    for note in notes:
        print(f"gallery: {note}")
    before = _snapshot_slugs(out)
    covers = {slug: (out / slug / "cover.jpg").read_bytes() for slug in before if (out / slug / "cover.jpg").is_file()}
    print(f"gallery: as `make gallery RUNS={','.join(str(r) for r in picked)} SCORES={_rel(scores_dir)} "
          f"SCOPE_ORDER={','.join(g['scope_order'])} OUT={out}`")
    try:
        result = gallery.export(picked, out, names=names, provenance_dir=Path(a.provenance_dir))
    except gallery.GalleryRefused as refusal:
        print(f"gallery: {refusal}", file=sys.stderr)
        print("the baseline is cut; the gallery is left as it is -- fix the refusal above and run `make quality-accept` "
              "again (it re-cuts the same baseline)")
        return 1
    after = [row["slug"] for row in result["index"]]
    for slug, data in covers.items():                                  # 063 replaces a slug's folder whole: the cover
        if slug in after and not (out / slug / "cover.jpg").is_file():  # (keel-web spec 103) is the snapshot's, kept
            (out / slug / "cover.jpg").write_bytes(data)
    refreshed = [s for s in after if s in before]
    added = [s for s in after if s not in before]
    no_cover = [s for s in after if not (out / s / "cover.jpg").is_file()]
    for row in result["index"]:
        print(f"gallery: {row['slug']:<14} {row.get('scope', 'ALL'):<11} (cloud {row.get('cloud')}, web {row.get('web')})")
    print(f"snapshot {out}: refreshed {', '.join(refreshed) or 'none'}; added {', '.join(added) or 'none'}; "
          f"missing a cover.jpg {', '.join(no_cover) or 'none'}; still missing a gallery_names.toml row: "
          + (", ".join(sorted({line.split(':')[0] for line in set_aside if 'gallery_names' in line})) or "none"))
    print(f"provenance: {result['provenance']} (outside the snapshot, not committed)")
    sentence = (f"keel-web spec: refresh the example gallery from keel-e2e-eval quality cycle {stem} (accepted {today}; "
                f"score_pct {head.get('score_pct')}% at RUBRIC_VERSION {rubric.RUBRIC_VERSION} against the bar of "
                f"{cfg['bar_pct']:.0f}%, keel-cloud {record.get('cloud_sha')}) -- commit public/sample as `make "
                f"quality-accept` wrote it ({len(refreshed)} slug(s) refreshed: {', '.join(refreshed) or 'none'}; "
                f"{len(added)} added: {', '.join(added) or 'none'}"
                + (f"; a 1200x800 cover.jpg still to add for {', '.join(no_cover)}" if no_cover else "")
                + "), re-pin the example frames (light, dark, phone) and the example pages' copy pins, light gate; "
                  "deploy on the founder's word.")
    print("")
    print(sentence)
    print("")
    print(f"commit here: git add {_rel(baseline_path)}" + (f" {_rel(quality_out / 'baselines')}" if had else ""))
    return 0


def _snapshot_slugs(out: Path) -> list[str]:
    index = Path(out) / gallery_index_name()
    if not index.is_file():
        return []
    try:
        return [row["slug"] for row in json.loads(index.read_text(encoding="utf-8")).get("examples") or []]
    except (ValueError, KeyError, TypeError):
        return []


def gallery_index_name() -> str:
    from evals import gallery                                            # noqa: PLC0415
    return gallery.INDEX


# ------------------------------------------------------------------------------------------------ the cadence

def due(argv=None) -> int:
    """FR-7: is a cycle due? A registry, instruction or routing change merged in keel-cloud since the last record's
    build, or `cadence.days` since it. It says so; it runs nothing."""
    p = argparse.ArgumentParser(prog="make quality-due")
    p.add_argument("--cycles-dir", default=str(CYCLES_DIR))
    a = p.parse_args(argv)
    try:
        cfg = load_config()
        cloud, _ = checkouts()
        head = git_sha(cloud)
    except Refused as reason:
        print(str(reason), file=sys.stderr)
        return 2
    found = record_files(Path(a.cycles_dir))
    if not found:
        print(f"due: no cycle record yet -- the first cycle is due (keel-cloud at {head}); the founder kicks it off")
        return 0
    last = load_record(found[-1])
    reasons = []
    try:
        changed = _git(cloud, "log", "--oneline", f"{last['cloud_sha']}..HEAD", "--", *DUE_PATHS).splitlines()
    except Refused:
        changed = []
        reasons.append(f"the last record's build {last['cloud_sha']} is not in the checkout's history")
    if changed:
        reasons.append(f"{len(changed)} keel-cloud commit(s) touching the registry, an instruction or the routing since "
                       f"{last['cloud_sha']} (first: {changed[-1]})")
    ended = dt.datetime.fromisoformat(last["ended"]) if last.get("ended") else None
    if ended:
        days = (dt.datetime.now(dt.timezone.utc) - ended).days
        if days >= int(cfg["cadence"]["days"]):
            reasons.append(f"{days} days since the last record (the cadence is {cfg['cadence']['days']})")
    print(f"due: the last cycle is {found[-1].name} (keel-cloud {last['cloud_sha']}; now {head}) -- "
          + ("A CYCLE IS DUE: " + "; ".join(reasons) if reasons else "not due")
          + ". Nothing runs by itself: the founder kicks off.")
    return 0


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    commands = {"walk": walk, "advise": advise, "accept": accept, "due": due}
    if not argv or argv[0] not in commands:
        print(f"usage: python -m quality.cycle {{{'|'.join(commands)}}} ...", file=sys.stderr)
        return 2
    return commands[argv[0]](argv[1:])


if __name__ == "__main__":
    sys.exit(main())
