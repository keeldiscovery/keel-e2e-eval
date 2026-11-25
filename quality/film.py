"""The film walk (spec 163 FR-2, FR-5; spec 165): `make film-walk ENTRIES=<ids|holdout|default> WHY="<...>"
[DOOR=keel|fake] [DRY=1] [PEOPLE=<n>] [TYPOS=0]`.

**One project an entry** (spec 165, closing 163's judgement call 1): the film's own project is the study the people
answer -- no second, typed project is made. For each entry, in order --

1. `make film-leg ENTRY=<id> DOOR=<door> OUT=<walk> PEOPLE=<people> TYPOS=<0|1>` (`evals/run_film.py`): a PROBLEM
   project, the seven beats told (the entry's words on Keel's door, typed with typos on `TYPOS=1`; the fake script's on
   the fakes), the boxes' yes, the build, **the film captured before any stranger sees it** into `<walk>/film/<entry>/`
   (fourteen frames, the story, the pictures, the setting and the prompts, the ledger's rows); then on the same project
   the lock (the window, the calibration, the credits, the ready page's lock, the questions READY -- a step that does
   not hold fails the leg by name), its link sent to the entry's first `people` (`quality/cycle.toml`'s seven) of the
   role the PROBLEM scope sends, each answering **the film's link** (the opening, the screener, the film, *Did this
   happen to you?*, the experience, Frequency's five, Importance over the role's tasks, the whys where owed) with their
   recorded answers mapped onto the four questions, then the founder's page read after the answers; the bundle
   `make read-screens` reads is the leg's evidence folder (`backtest.json`, `kind: "film"`), named in `film.json`.
2. On Keel's door only (PAID): `make read-screens RUN=<that folder>` -- the strangers' screens of the film's link (§A,
   R6) and the founder's page after the seven answers (§B), as the cycles read them.

The walk's bundle `runs/<stamp>-film-walk/` carries the films (`film/<entry>/`) and in `walk.json` each entry's one
project (`project_id`), its screens bundle and its score file; `make read-films RUN=<walk>` reads the films, `make
read-film-table RUN=<walk>` tables the three scores an entry, all of that one project. `walk.json` is rewritten after
every step (the work protected).

**Free on the fakes** (`DOOR=fake`, FR-4's local walk): step 1 whole on the stack as it stands (or booted), keel-cloud's
fakes answering (`FakeStoryReadings`, `FakePictures`, the fake transcriber and readers) -- the film, the lock, the
people on the film's link and the founder's page; step 2 is paid and is not run -- the walk says so.

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
    """Spec 165: per entry the film leg -- the film, then the same project's lock, people and founder's page -- and on
    Keel's door `make read-screens` on that leg's screens bundle; no back-test (no second, typed project)."""
    make = ["make", "-C", str(REPO), "--no-print-directory"]
    steps = []
    for entry in entries:
        sends = ([f"PEOPLE={int(people)}"] if people else []) + [f"TYPOS={1 if typos else 0}"]
        steps.append({"entry": entry, "what": "film", "log": str(walk / "logs" / f"{entry}.film.log"),
                      "argv": [*make, "film-leg", f"ENTRY={entry}", f"DOOR={door}", f"OUT={walk}", *sends]})
        if door == "keel":
            steps.append({"entry": entry, "what": "read", "log": str(walk / "logs" / f"{entry}.read.log"),
                          "argv": [*make, "read-screens", "RUN=<bundle>"]})
    return steps


def film_record(walk: Path, entry: str) -> dict:
    """The film leg's own record (`film/<entry>/film.json`), or `{}` where the leg wrote none."""
    path = Path(walk) / "film" / entry / "film.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def project_row(film: dict) -> dict:
    """Spec 165 FR-2: what `walk.json` names of the entry's one project -- the project, the screens bundle read-screens
    reads, the people sent and answered, the lock's refusal where it did not hold."""
    strangers = film.get("strangers") or {}
    row = {"project_id": film.get("project_id"), "screens_bundle": film.get("screens_bundle"),
           "people": strangers.get("people"), "answered": strangers.get("answered")}
    if film.get("refused"):
        row["refused"] = film["refused"]
    return {k: v for k, v in row.items() if v is not None}


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
            print("  (DOOR=fake: the film, the lock, the people on the film's link and the founder's page, free; "
                  "read-screens is paid and is not run)")
        print(f"then: make read-films RUN={walk_dir}  and  make read-film-table RUN={walk_dir}")
        return 0
    walk_dir.mkdir(parents=True, exist_ok=True)
    record = {"spec": "163+165", "why": args.why, "door": args.door, "started": stamp, "people": people,
              "typos": args.typos != "off", "keel-cloud": cyc.git_sha(cloud, short=8),
              "keel-web": cyc.git_sha(web, short=8), "entries": []}

    def save():
        (walk_dir / WALK_RECORD).write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    by_entry: dict[str, dict] = {}
    for step in steps:
        row = by_entry.setdefault(step["entry"], {"entry": step["entry"], "film": f"film/{step['entry']}"})
        if row not in record["entries"]:
            record["entries"].append(row)
        argv = [a.replace("<bundle>", row.get("screens_bundle") or "") for a in step["argv"]]
        if step["what"] == "read" and not row.get("screens_bundle"):
            row["read"] = "not run: the film leg wrote no screens bundle (the film's project never had its people)"
            save()
            continue
        print(f"{step['entry']}: {step['what']} ...", flush=True)
        code = _run(argv, step["log"], runner)
        row[f"{step['what']}_exit"] = code
        if step["what"] == "read":
            row["score_file"] = score_file_of(Path(step["log"]))
        if step["what"] == "film":
            film = film_record(walk_dir, step["entry"])
            row["captured"] = bool(film)
            row.update(project_row(film))
            if row.get("screens_bundle"):
                row["screens"] = Path(row["screens_bundle"]).name
        save()
        print(f"{step['entry']}: {step['what']} exit {code} (log {step['log']})", flush=True)
    record["ended"] = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if args.door == "fake":
        record["note"] = ("DOOR=fake: the film, the lock, the people on the film's link and the founder's page walked "
                          "free; read-screens is paid and was not run")
    save()
    print(f"walk bundle: {walk_dir}")
    for r in record["entries"]:
        print(f"  {r['entry']}: the film's project {r.get('project_id')}, {r.get('answered')} of {r.get('people')} "
              f"answered on its link, screens bundle {r.get('screens_bundle')}"
              + (f" -- REFUSED: {r['refused']}" if r.get("refused") else ""))
    print(f"next: make read-films RUN={walk_dir}  then  make read-film-table RUN={walk_dir}")
    return 0 if all(r.get("captured") and r.get("screens_bundle") and r.get("film_exit") == 0
                    for r in record["entries"]) else 1


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] != "walk":
        print("usage: python -m quality.film walk --entries ... --why ... [--door keel|fake] [--dry-run]", file=sys.stderr)
        return 2
    return walk(argv[1:])


if __name__ == "__main__":
    sys.exit(main())
