"""The film walk (spec 163 FR-2, FR-5): `make film-walk ENTRIES=<ids|holdout|default> WHY="<...>" [DOOR=keel|fake]
[DRY=1] [PEOPLE=<n>] [TYPOS=0]`.

**PAID on Keel's door** (the default, `DOOR=keel`; the founder's word): for each entry, in order --

1. `make film-leg ENTRY=<id> DOOR=keel OUT=<walk>` (`evals/run_film.py`): its own stack booted from this shell with the
   keys and `KEEL_PICTURES=openai`, a PROBLEM project, the seven beats told in the entry's words, the boxes' yes, the
   build with the real pictures, and **the film captured before any stranger sees it** into `<walk>/film/<entry>/`
   (fourteen frames, the story, the pictures, the setting and the prompts, the ledger's rows); the stack down after.
2. `make backtest ENTRY=<id> SCOPE=PROBLEM DOOR=keel PEOPLE=<people> TYPOS=1` -- **the scenario-maker unchanged**, as
   `make quality-walk` runs it: the entry typed as the founder, the people answering on the person's own link, the
   founder's page after the answers (spec 109); its bundle named in the walk's record.
3. `make read-screens RUN=<that bundle>` -- every respondent screen (§A, R6) and the founder's page after the answers
   (§B), as the cycles read them.

The walk's bundle `runs/<stamp>-film-walk/` carries the three: the films (`film/<entry>/`), and in `walk.json` each
entry's back-test bundle and its score file; `make read-films RUN=<walk>` reads the films, `make read-film-table
RUN=<walk>` tables the three scores an entry. `walk.json` is rewritten after every step (the work protected).

**Free on the fakes** (`DOOR=fake`, FR-7's local walk): step 1 alone on the stack as it stands (or booted), keel-cloud's
fakes answering (`FakeStoryReadings`, `FakePictures`); steps 2 and 3 are paid and are not run -- the walk says so.

It refuses (one sentence, exit 2, nothing run) without ENTRIES; on `ENTRIES=holdout` while `quality/cycle.toml`
`[film] holdout` is empty (the integrator writes the founder's nine first); without WHY on a paid walk; on DOOR=keel
without `KEEL_ANTHROPIC_API_KEY`, `KEEL_OPENAI_API_KEY` or `KEEL_PICTURES=openai` in the shell, without the `claude`
CLI (the readers), or with a stack already answering (each step brings its own); on an entry keel-cloud has no
back-test file for. `DRY=1` prints the plan and runs nothing.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from quality import cycle as cyc
from quality import film_table as ft

REPO = Path(__file__).resolve().parent.parent
RUNS_DIR = REPO / "runs"
DOORS = ("keel", "fake")
PAID_KEYS = ("KEEL_ANTHROPIC_API_KEY", "KEEL_OPENAI_API_KEY")
WALK_RECORD = "walk.json"


class Refused(RuntimeError):
    """A reason the walk does not start, printed as one sentence (exit 2)."""


def resolve_entries(raw: str | None, cfg: dict, film: dict) -> list[str]:
    raw = (raw or "").strip()
    if not raw:
        raise Refused("make film-walk refuses: no ENTRIES -- `ENTRIES=08-fresco`, `ENTRIES=holdout` (the nine of "
                      "quality/cycle.toml [film] holdout) or `ENTRIES=default` (the five of [cycle] entries)")
    if raw == "holdout":
        if not film["holdout"]:
            raise Refused("make film-walk refuses: ENTRIES=holdout and quality/cycle.toml [film] holdout is empty -- the "
                          "integrator writes the founder's nine there before the paid run (spec 163 FR-5)")
        return list(film["holdout"])
    if raw == "default":
        return list(cfg["entries"])
    return [e.strip() for e in raw.split(",") if e.strip()]


def preflight(entries: list[str], *, door: str, why: str | None, dry: bool, cloud: Path, env: dict | None = None,
              which=shutil.which, stack_up=None) -> tuple[list[str], list[str]]:
    """`(refusals, warnings)` before anything runs; on a dry run the paid-only refusals are warnings."""
    env = os.environ if env is None else env
    hard, soft = [], []
    if door not in DOORS:
        hard.append(f"DOOR={door} -- `keel` (paid: Keel's AI and the real pictures) or `fake` (the free local walk)")
    known_dir = cloud / cyc.BACKTEST_REL
    if known_dir.is_dir():
        unknown = [e for e in entries if not (known_dir / f"{e}.yaml").is_file()]
        if unknown:
            hard.append(f"no back-test entry {unknown} in keel-cloud {cyc.BACKTEST_REL}")
    paid = []
    if door == "keel":
        if not (why or "").strip():
            paid.append("no WHY -- a paid walk says why it is spent, in the founder's words")
        missing = [k for k in PAID_KEYS if not (env.get(k) or "").strip()]
        if missing:
            paid.append(f"{', '.join(missing)} not set in this shell -- the walk reads on Keel's AI and draws the real "
                        "pictures (never logged or echoed)")
        if (env.get("KEEL_PICTURES") or "").strip().lower() != "openai":
            paid.append("KEEL_PICTURES is not `openai` -- keel-cloud 273 draws the real pictures only on its `openai` "
                        "port (export KEEL_PICTURES=openai)")
        if not which("claude"):
            paid.append("the `claude` CLI is not on PATH -- `make read-screens` reads through it")
        if stack_up and stack_up():
            paid.append("a stack already answers on the eval ports -- `make down` first: each step brings its own stack "
                        "booted from this shell")
    elif (env.get("KEEL_PICTURES") or "").strip().lower() == "openai":
        hard.append("DOOR=fake with KEEL_PICTURES=openai -- the free walk never draws a paid picture")
    (soft if dry else hard).extend(paid)
    return hard, soft


def plan_steps(entries: list[str], *, door: str, walk: Path, people: int | None, typos: bool) -> list[dict]:
    make = ["make", "-C", str(REPO), "--no-print-directory"]
    steps = []
    for entry in entries:
        steps.append({"entry": entry, "what": "film", "log": str(walk / "logs" / f"{entry}.film.log"),
                      "argv": [*make, "film-leg", f"ENTRY={entry}", f"DOOR={door}", f"OUT={walk}"]})
        if door == "keel":
            sends = ([f"PEOPLE={int(people)}"] if people else []) + (["TYPOS=1"] if typos else [])
            steps.append({"entry": entry, "what": "backtest", "log": str(walk / "logs" / f"{entry}.backtest.log"),
                          "argv": [*make, "backtest", f"ENTRY={entry}", "SCOPE=PROBLEM", "DOOR=keel", *sends]})
            steps.append({"entry": entry, "what": "read", "log": str(walk / "logs" / f"{entry}.read.log"),
                          "argv": [*make, "read-screens", "RUN=<bundle>"]})
    return steps


def newest_bundle(entry: str, since: float, runs_dir: Path | None = None) -> Path | None:
    found = [p for p in Path(runs_dir or RUNS_DIR).glob(f"*-backtest-{entry}") if p.stat().st_mtime >= since - 1]
    return max(found, key=lambda p: p.stat().st_mtime) if found else None


def score_file_of(log: Path) -> str | None:
    try:
        for line in Path(log).read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("score file: "):
                return line.split(": ", 1)[1].strip()
    except OSError:
        return None
    return None


def _run(argv: list[str], log: str, runner=subprocess.run) -> int:
    Path(log).parent.mkdir(parents=True, exist_ok=True)
    with open(log, "w", encoding="utf-8") as handle:
        return runner(argv, stdout=handle, stderr=subprocess.STDOUT).returncode


def walk(argv=None, *, runner=subprocess.run, env=None, which=shutil.which, stack_up=None) -> int:
    parser = argparse.ArgumentParser(prog="quality.film walk")
    parser.add_argument("--entries", default="")
    parser.add_argument("--why", default="")
    parser.add_argument("--door", default="keel")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--people", default=None)
    parser.add_argument("--typos", default="on")
    parser.add_argument("--out", default=None)
    args = parser.parse_args(argv)
    env = os.environ if env is None else env
    try:
        cfg = cyc.load_config()
        film = ft.load_film_config()
        entries = resolve_entries(args.entries, cfg, film)
        people = cyc.resolve_people(args.people, cfg)
        cloud, web = cyc.checkouts()
        if stack_up is None:
            def stack_up():
                from stack.config import load_config                      # noqa: PLC0415
                from stack.lifecycle import quick_gates_pass              # noqa: PLC0415
                return quick_gates_pass(load_config(profile="eval"))
        hard, soft = preflight(entries, door=args.door, why=args.why, dry=args.dry_run, cloud=cloud, env=env,
                               which=which, stack_up=stack_up)
    except (Refused, cyc.Refused, ft.Refused) as reason:
        print(str(reason), file=sys.stderr)
        return 2
    if hard:
        print("make film-walk refuses: " + hard[0] + (f" (and {len(hard) - 1} more)" if len(hard) > 1 else ""),
              file=sys.stderr)
        return 2
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    walk_dir = Path(args.out) if args.out else RUNS_DIR / f"{stamp}-film-walk"
    steps = plan_steps(entries, door=args.door, walk=walk_dir, people=people, typos=args.typos != "off")
    if args.dry_run:
        for w in soft:
            print(f"warning (a paid walk refuses this): {w}")
        print(f"the film walk: {len(entries)} entr{'y' if len(entries) == 1 else 'ies'} on DOOR={args.door}, into "
              f"{walk_dir}")
        for s in steps:
            print("  " + " ".join(s["argv"]))
        if args.door == "fake":
            print("  (DOOR=fake: the back-test and read-screens are paid and are not run; the film alone)")
        print(f"then: make read-films RUN={walk_dir}  and  make read-film-table RUN={walk_dir}")
        return 0
    walk_dir.mkdir(parents=True, exist_ok=True)
    record = {"spec": "163", "why": args.why, "door": args.door, "started": stamp, "people": people,
              "typos": args.typos != "off", "keel-cloud": cyc.git_sha(cloud, short=8),
              "keel-web": cyc.git_sha(web, short=8), "entries": []}

    def save():
        (walk_dir / WALK_RECORD).write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    by_entry: dict[str, dict] = {}
    for step in steps:
        row = by_entry.setdefault(step["entry"], {"entry": step["entry"], "film": f"film/{step['entry']}"})
        if row not in record["entries"]:
            record["entries"].append(row)
        started = time.time()
        argv = [a.replace("<bundle>", row.get("backtest_path") or "") for a in step["argv"]]
        if step["what"] == "read" and not row.get("backtest_path"):
            row["read"] = "not run: the back-test wrote no bundle"
            save()
            continue
        print(f"{step['entry']}: {step['what']} ...", flush=True)
        code = _run(argv, step["log"], runner)
        row[f"{step['what']}_exit"] = code
        if step["what"] == "backtest":
            bundle = newest_bundle(step["entry"], started)
            row["backtest"] = bundle.name if bundle else None
            row["backtest_path"] = str(bundle) if bundle else None
        if step["what"] == "read":
            row["score_file"] = score_file_of(Path(step["log"]))
        if step["what"] == "film":
            row["captured"] = (walk_dir / "film" / step["entry"] / "film.json").is_file()
        save()
        print(f"{step['entry']}: {step['what']} exit {code} (log {step['log']})", flush=True)
    record["ended"] = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if args.door == "fake":
        record["note"] = "DOOR=fake: the film alone (the back-test and read-screens are paid and were not run)"
    save()
    print(f"walk bundle: {walk_dir}")
    print(f"next: make read-films RUN={walk_dir}  then  make read-film-table RUN={walk_dir}")
    return 0 if all(r.get("captured") for r in record["entries"]) else 1


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] != "walk":
        print("usage: python -m quality.film walk --entries ... --why ... [--door keel|fake] [--dry-run]", file=sys.stderr)
        return 2
    return walk(argv[1:])


if __name__ == "__main__":
    sys.exit(main())
