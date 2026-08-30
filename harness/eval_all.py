"""`python -m harness.eval_all` -- the Makefile's `eval-all` entrypoint (T013, FR-005): runs the
full scenario set (s001 included) via one `pytest evals` invocation -- one stack session, since
`evals/conftest.py`'s `stack` fixture is session-scoped and attaches to whatever `make up` already
started rather than re-booting per test -- then writes `runs/INDEX-<stamp>.html` naming every run
bundle this invocation produced (slug, verdict, score, category bars, a link to its own
report.html).

Deliberately a thin wrapper, not a reimplementation of `make eval`'s own pytest invocation: this
runs the exact same `pytest evals -q` a developer would run by hand, so `make eval-all`'s bundles
are ordinary run bundles, nothing INDEX-specific baked into how they're produced.
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from harness.evidence import RUNS_DIR, generate_index
from stack.config import REPO_ROOT


def _run_dirs_since(cutoff: datetime) -> list[Path]:
    """Every `runs/<slug>/` directory with a `verdict.json` newer than `cutoff`, one per scenario
    slug (the latest, if a slug somehow produced more than one bundle in this invocation) -- sorted
    by scenario slug for a stable, readable index."""
    by_slug: dict[str, Path] = {}
    if not RUNS_DIR.is_dir():
        return []
    for candidate in RUNS_DIR.iterdir():
        verdict_path = candidate / "verdict.json"
        if not candidate.is_dir() or not verdict_path.is_file():
            continue
        try:
            mtime = datetime.fromtimestamp(verdict_path.stat().st_mtime, tz=timezone.utc)
        except OSError:
            continue
        if mtime < cutoff:
            continue
        try:
            import json
            verdict = json.loads(verdict_path.read_text())
        except (OSError, ValueError):
            continue
        slug = verdict.get("scenario") or candidate.name
        existing = by_slug.get(slug)
        if existing is None or candidate.name > existing.name:
            by_slug[slug] = candidate
    return [by_slug[slug] for slug in sorted(by_slug)]


def main() -> int:
    started = datetime.now(timezone.utc)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "evals", "-q"],
        cwd=str(REPO_ROOT),
    )

    run_dirs = _run_dirs_since(started)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = RUNS_DIR / f"INDEX-{stamp}.html"
    generate_index(run_dirs, out_path)
    print(f"\neval-all: {len(run_dirs)} run bundle(s) -- wrote {out_path}")

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
