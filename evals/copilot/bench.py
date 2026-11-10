"""Spec 151 FR-7: `make copilot-bench` -- the copilot call bench, one round at one level.

  KEEL_OPENAI_API_KEY=... KEEL_ANTHROPIC_API_KEY=... python -m evals.copilot.bench --round 1 --level text
      [--stacks 1,2,3] [--questionnaire <fixture>] [--limit n] [--sample 20] [--resume runs/<stamp>-copilot-bench-...]
  python -m evals.copilot.bench --round 1 --level text --dry          (no key, nothing spent)

Writes `runs/<stamp>-copilot-bench-r<round>-<level>/`: `plan.json`, `writer.jsonl` (every script's record: kept or
dropped, its faults, its tries, its cost), `scripts.jsonl`, `sample.md`, `audio/<script>/` (`founder.wav`, `them.wav`,
`turns.json`; LEVEL=audio), `transcripts.jsonl` (what each stack heard), `events.jsonl`, the sheets (`report.py`),
`page/`, `register-row.md`, and a row a stack on `runs/copilot-bench-register.md`.

**PAID** (the writer, the voices, the three stacks): refused without both keys in the shell, which go into the request
headers alone; never in `make eval`, `make unit`, the matrix or a schedule; on the founder's word per round. `--sample`
stops after `scripts.jsonl` and `sample.md`, before any audio or stack call, so the reviewer reads first; `--resume`
continues from the scripts written. `--dry` writes three scripts of the round with the fake writer, renders nothing,
runs Stacks 1 and 2 at the text level through fake clients answering the canned events (Stack 3, which has no text
level, scores the canned events directly), scores them, and spends nothing; it appends no register row.
Exit: DRY 0 once everything is written; a paid run 0 when at least one stack's certificate is PASS, else 1.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from evals.copilot import plan as plans
from evals.copilot import questionnaire as qmod
from evals.copilot import render as rmod
from evals.copilot import report, score, writer
from evals.copilot.clients import HttpClients, keys_from
from evals.copilot.fakes import FakeClients
from evals.copilot.stacks import STACKS, canned_events, parse_stacks

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = REPO_ROOT / "runs"
DRY_SCRIPTS = 3
SAMPLE_DEFAULT = 20


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _append(path: Path, rows: list[dict]):
    with path.open("a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def parse_args(argv):
    ap = argparse.ArgumentParser(prog="make copilot-bench", description=__doc__.split("\n\n")[0])
    ap.add_argument("--round", type=int, required=True, choices=[1, 2, 3, 4])
    ap.add_argument("--level", required=True, choices=["text", "audio"])
    ap.add_argument("--stacks", default=None, help="comma list of 1, 2, 3 (default all the level allows)")
    ap.add_argument("--questionnaire", default=None, help="a fixture (default the committed 08-fresco one)")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--sample", type=int, default=0, help="write this many scripts to sample.md and stop")
    ap.add_argument("--resume", default=None)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--snrs", default=None, help="noise beds on R3's respondent track (e.g. 10), audio only")
    ap.add_argument("--noise-share", type=float, default=None)
    ap.add_argument("--voices", default=None, help="founder:them")
    ap.add_argument("--runs-dir", default=None, help=argparse.SUPPRESS)
    return ap.parse_args(argv)


def run(argv: list[str] | None = None, *, env=None) -> int:
    a = parse_args(argv)
    keys = None if a.dry else keys_from(env)
    q = qmod.load(a.questionnaire)
    qname = Path(q["path"]).stem
    stacks = parse_stacks(a.stacks)
    if a.level == "text":
        dropped = [n for n in stacks if "text" not in STACKS[n].levels]
        stacks = [n for n in stacks if "text" in STACKS[n].levels or a.dry]
        if dropped and not a.dry:
            print(f"copilot-bench: stack {', '.join(map(str, dropped))} has no text level; not run")
    runs_dir = Path(a.runs_dir) if a.runs_dir else RUNS_DIR
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(a.resume) if a.resume else runs_dir / f"{stamp}-copilot-bench-r{a.round}-{a.level}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "audio").mkdir(exist_ok=True)                               # empty at the text level and on DRY
    stamp = out.name.split("-copilot-bench")[0]

    # the plan and the scripts
    entries = plans.build(a.round, q, seed=a.seed)
    full = len(entries)
    if a.dry:
        step = max(1, len(entries) // DRY_SCRIPTS)                     # three spread across the round's plan
        entries = entries[::step][:DRY_SCRIPTS]
    elif a.limit:
        entries = entries[:a.limit]
    (out / "plan.json").write_text(json.dumps({"spec": "151", "round": a.round, "level": a.level,
                                               "questionnaire": q["path"], "seed": plans.seed_for(a.round, a.seed),
                                               "entries": len(entries), "of": full, "dry": a.dry,
                                               "coverage": plans.coverage(entries)}, indent=1), encoding="utf-8")
    records = _jsonl(out / "writer.jsonl")
    done = {r["id"] for r in records}
    todo = [e for e in entries if e["id"] not in done]
    w = writer.FakeWriter(q, qname) if a.dry else writer.ModelWriter(HttpClients(keys, timeout=600), q, qname)
    if todo:
        print(f"copilot-bench: writing {len(todo)} scripts ({len(done)} written) -> {out}", flush=True)
        with cf.ThreadPoolExecutor(1 if a.dry else a.workers) as ex:
            for rec in ex.map(w.write, todo):
                _append(out / "writer.jsonl", [{k: v for k, v in rec.items() if k != "script"}])
                if rec["kept"]:
                    _append(out / "scripts.jsonl", [rec["script"]])
                records.append(rec)
    scripts = sorted(_jsonl(out / "scripts.jsonl"), key=lambda s: s["id"])
    scripts = [s for s in scripts if s["id"] in {e["id"] for e in entries}]
    kept = len(scripts)
    dropped_n = sum(1 for r in records if not r.get("kept"))
    (out / "sample.md").write_text(writer.sample_markdown(scripts, a.sample or SAMPLE_DEFAULT), encoding="utf-8")
    print(f"copilot-bench: {kept} scripts kept, {dropped_n} dropped; sample -> {out / 'sample.md'}", flush=True)
    if a.sample and not a.dry:
        print("copilot-bench: SAMPLE stops here -- read sample.md, then RESUME=" + str(out))
        return 0

    # the audio
    clocks, tts_seconds, noisy = {}, 0.0, {}
    if a.level == "audio" and not a.dry:
        noisy = rmod.noise_plan(scripts, round_=a.round, snrs=a.snrs, share=a.noise_share)
        from evals.noise.pipeline import samples_root                         # noqa: PLC0415
        for s in scripts:
            d = out / "audio" / s["id"]
            got = rmod.load_clocks(d)
            if got is None:
                r = rmod.render(s, d, keys["openai"], pair=rmod.voices(a.voices), noise=noisy.get(s["id"]),
                                beds_root=samples_root())
                got, tts_seconds = r["clocks"], tts_seconds + r["tts_seconds"]
            clocks[s["id"]] = got

    # the stacks
    events: dict = {}
    for n in stacks:
        stack = STACKS[n]()
        evs = {}
        for s in scripts:
            if a.dry and "text" not in stack.levels:
                evs[s["id"]] = canned_events(s)
                continue
            clients = FakeClients(s) if a.dry else HttpClients(keys)
            level = "text" if a.dry else a.level
            evs[s["id"]] = stack.run(s, q, clients, level=level, audio_dir=out / "audio" / s["id"],
                                     clocks=clocks.get(s["id"]))
        events[n] = evs
        _append(out / "events.jsonl", [dict(e, stack=n, script=sid) for sid, es in evs.items() for e in es])
        _append(out / "transcripts.jsonl", [{"stack": n, "script": sid, "turn": e["turn"], "heard": e.get("heard")}
                                            for sid, es in evs.items() for e in es])

    # the sheets
    sheets = [score.sheet(scripts, events[n], q, round_=a.round, level=a.level, stack=STACKS[n].name, number=n,
                          noisy=set(noisy)) for n in stacks]
    header = {"stamp": stamp, "spec": "151", "round": a.round, "level": a.level, "questionnaire": q["path"],
              "scripts_kept": kept, "scripts_dropped": dropped_n, "dry": a.dry,
              "run_cost": score.run_costs(records, tts_seconds), "noise": noisy}
    lines = report.write(out, sheets, scripts, events, header=header, audio=a.level == "audio" and not a.dry,
                         register=not a.dry)
    for line in lines:
        print(line)
    print(f"copilot-bench: sheet -> {out / 'sheet.md'}")
    if a.dry:
        return 0
    return 0 if any(sh["certificate"]["verdict"] == "PASS" for sh in sheets) else 1


if __name__ == "__main__":
    sys.exit(run())
