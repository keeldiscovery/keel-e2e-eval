"""Spec 157 FR-3: `make e2e-157` -- the lot, once, on the current profile (`evals/three_views.py`); since spec 158 the
founder's legs walk the conversation (keel-web 245 on keel-cloud 263) and the report names the beats.

Not a `test_*.py`: `make eval` never collects it (the scenario set is unchanged); the make target names this file.
Every leg runs whatever the one before it did (a leg whose project is missing is skipped by name), and the report is
written in a `finally`: `runs/157/<cloud sha>-<web sha>/report.md`, the bundle beside it. The test fails unless every
leg is green -- a leg written to an unbuilt screen (keel-web 243) is *written, not run*, which is not green.
"""

from __future__ import annotations

import time

from evals import three_views as tv
from evals import three_views_report as report
from evals import three_views_strangers as strangers
from harness.evidence import RUNS_DIR, _git_info, write_versions
from harness.steps import Recorder
from stack import cloud_log
from stack.config import REPO_ROOT


def _sha(info: dict, n: int) -> str:
    return str((info or {}).get("commit") or "unknown")[:n]


def test_e2e_157_three_views(stack, browser):
    cloud = _git_info(stack.keel_cloud)
    web = _git_info(stack.keel_web)
    folder = RUNS_DIR / "157" / f"{_sha(cloud, 8)}-{_sha(web, 8)}"
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    bundle = folder / stamp
    bundle.mkdir(parents=True, exist_ok=False)
    write_versions(bundle, stack)
    recorder = Recorder(bundle)
    run = tv.Run(stack, browser, recorder, bundle)
    log_from = cloud_log.offset(stack) if not run.remote else 0
    started = time.monotonic()
    try:
        run.open()
        tv.timed(run, "FR-1a", lambda leg: tv.fr1_a(run, leg))
        tv.timed(run, "FR-1b", lambda leg: tv.fr1_b(run, leg))
        tv.timed(run, "FR-1d", lambda leg: tv.fr1_d(run, leg))
        tv.timed(run, "FR-1c", lambda leg: tv.fr1_c(run, leg))
        strangers.walk_all(run)
    finally:
        try:
            run.close()
        finally:
            text = None
            path = cloud_log.path_of(stack)
            if not run.remote and path is not None and path.exists():
                with path.open("rb") as fh:
                    fh.seek(log_from)
                    text = fh.read().decode("utf-8", errors="replace")
            scan = report.log_scan(text)
            meta = {"cloud": _sha(cloud, 8), "web": _sha(web, 8), "eval": _sha(_git_info(REPO_ROOT), 7),
                    "profile": getattr(stack, "profile", "?"), "started": stamp,
                    "seconds": round(time.monotonic() - started), "bundle": str(bundle.relative_to(REPO_ROOT))}
            legs = list(run.legs.values())
            written = report.write_report(folder / "report.md", legs, meta, scan, run.beats, run.fits, run.turns)
            (bundle / "report.md").write_text(written.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"\nreport: {written}\nbundle: {bundle}")
    assert scan.get("clean") is not False, report.scan_line(scan)
    missed = [f"{leg.id}: {leg.status} {leg.why}" for leg in run.legs.values() if leg.status != "green"]
    assert not missed, "\n".join(missed)
