"""Run bundle plumbing (data-model.md, contracts/evidence-contract.md): run_dir creation,
versions.json, verdict.json, failure captures, and the report.html generator -- which reads
transcript.jsonl alone, so `make report RUN=<dir>` can rebuild it from a crashed run too.
"""

from __future__ import annotations

import base64
import html
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from stack.config import REPO_ROOT

RUNS_DIR = REPO_ROOT / "runs"

# The four repos versions.json pins (design §2/§7): this repo plus the three siblings it drives.
REPO_LABELS = ["keel-e2e-eval", "keel-cloud", "keel-web", "keel-skill"]


def new_run_dir(scenario_slug: str) -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = RUNS_DIR / f"{ts}-{scenario_slug}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


# ------------------------------------------------------------------------------- versions.json

def _git_info(path: Path) -> dict:
    try:
        commit = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "-C", str(path), "status", "--porcelain"],
            capture_output=True, text=True, timeout=10,
        ).stdout
        dirty = bool(status.strip())
        return {"path": str(path), "commit": commit or None, "dirty": dirty}
    except (OSError, subprocess.SubprocessError) as exc:
        return {"path": str(path), "commit": None, "dirty": None, "error": str(exc)}


def write_versions(run_dir: Path, config) -> None:
    repos = {
        "keel-e2e-eval": _git_info(REPO_ROOT),
        "keel-cloud": _git_info(config.keel_cloud),
        "keel-web": _git_info(config.keel_web),
        "keel-skill": _git_info(config.keel_skill),
    }
    (run_dir / "versions.json").write_text(json.dumps(repos, indent=2))


# -------------------------------------------------------------------------------- verdict.json

def write_verdict(run_dir: Path, scenario: str, passed: bool, failed_step: str | None,
                   duration_s: float) -> None:
    verdict = {
        "scenario": scenario,
        "passed": passed,
        "failed_step": failed_step,
        "duration_s": round(duration_s, 3),
    }
    (run_dir / "verdict.json").write_text(json.dumps(verdict, indent=2))


# ------------------------------------------------------------------------------ failure capture

def write_failure_capture(run_dir: Path, *, page_html: str | None, console_lines: list[str]) -> None:
    failure_dir = run_dir / "failure"
    failure_dir.mkdir(parents=True, exist_ok=True)
    if page_html is not None:
        (failure_dir / "page.html").write_text(page_html)
    (failure_dir / "console.log").write_text("\n".join(console_lines))


# ---------------------------------------------------------------------------------- report.html

def _read_transcript(run_dir: Path) -> list[dict]:
    """Reads transcript.jsonl and sorts by `seq`. A step that opens another step inside its own
    body (e.g. a browser step that logs a DRIFT note mid-navigation) finishes and appends the
    inner record before the outer one -- `seq` is assigned when a step is entered, not when it's
    appended, so file order and seq order can differ for nested steps even though every seq is
    still unique. Sorting here is what makes the report read top-to-bottom in the order steps
    actually started.
    """
    path = run_dir / "transcript.jsonl"
    if not path.exists():
        return []
    entries = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    entries.sort(key=lambda e: e.get("seq", 0))
    return entries


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


PARTY_COLOR = {
    "agent": "#6d5bd0",
    "founder": "#1a7f5a",
    "participant": "#b3691b",
    "stack": "#555",
}

KIND_LABEL = {
    "protocol": "wire",
    "browser": "browser",
    "assert": "assert",
    "note": "note",
}


def _badge(text: str, color: str) -> str:
    return (f'<span style="display:inline-block;padding:1px 8px;border-radius:10px;'
            f'font-size:11px;font-weight:600;color:#fff;background:{color}">{html.escape(text)}</span>')


def _json_block(label: str, value) -> str:
    if value is None:
        return ""
    body = html.escape(json.dumps(value, indent=2, default=str))
    return (f"<details><summary>{html.escape(label)}</summary>"
            f"<pre style=\"white-space:pre-wrap;background:#f6f6f6;padding:8px;"
            f"border-radius:6px;overflow-x:auto\">{body}</pre></details>")


def _thumbnails(run_dir: Path, screenshots: list[str]) -> str:
    parts = []
    for name in screenshots:
        img_path = run_dir / "screenshots" / name
        if not img_path.exists():
            parts.append(f"<span>(missing: {html.escape(name)})</span>")
            continue
        b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
        href = f"screenshots/{name}"
        parts.append(
            f'<a href="{html.escape(href)}" target="_blank" style="display:inline-block;margin:4px">'
            f'<img src="data:image/png;base64,{b64}" alt="{html.escape(name)}" '
            f'style="width:220px;border:1px solid #ccc;border-radius:4px;display:block" />'
            f'<div style="font-size:11px;color:#666;text-align:center">{html.escape(name)}</div></a>'
        )
    return "".join(parts)


def _versions_table(versions: dict | None) -> str:
    if not versions:
        return "<p><em>No versions.json (harness crashed before it could be written).</em></p>"
    rows = []
    for label in REPO_LABELS:
        info = versions.get(label, {})
        commit = (info.get("commit") or "?")[:12]
        dirty = " (dirty)" if info.get("dirty") else ""
        rows.append(f"<tr><td>{html.escape(label)}</td><td><code>{html.escape(commit)}{dirty}</code></td></tr>")
    return "<table>" + "".join(rows) + "</table>"


def generate_report(run_dir: Path) -> Path:
    """Rebuilds report.html from transcript.jsonl alone (plus versions.json/verdict.json when
    present) -- re-runnable via `make report RUN=<dir>`, and safe to call on a crashed run: a
    missing verdict.json renders as "harness crashed" rather than raising.
    """
    entries = _read_transcript(run_dir)
    versions = _read_json(run_dir / "versions.json")
    verdict = _read_json(run_dir / "verdict.json")

    scenario = verdict.get("scenario") if verdict else run_dir.name
    passed = verdict.get("passed") if verdict else None
    failed_step = verdict.get("failed_step") if verdict else None
    duration_s = verdict.get("duration_s") if verdict else None

    if verdict is None:
        verdict_html = _badge("HARNESS CRASHED (no verdict.json)", "#b3261e")
    elif passed:
        verdict_html = _badge("PASSED", "#1a7f5a")
    else:
        verdict_html = _badge("FAILED", "#b3261e")

    failing_anchor = ""
    if failed_step:
        failing_anchor = f'<a href="#failed-step">Jump to failing step: {html.escape(failed_step)}</a>'

    rows_html = []
    for entry in entries:
        seq = entry.get("seq")
        name = entry.get("name", "")
        party = entry.get("party", "stack")
        kind = entry.get("kind", "note")
        ok = entry.get("ok", True)
        duration = entry.get("duration_s", 0.0)
        error = entry.get("error")
        screenshots = entry.get("screenshots") or []
        anchor_id = f' id="failed-step"' if (failed_step and name == failed_step and not ok) else ""
        status_badge = _badge("ok", "#1a7f5a") if ok else _badge("FAILED", "#b3261e")
        party_badge = _badge(party, PARTY_COLOR.get(party, "#555"))

        body_parts = []
        if kind == "assert":
            body_parts.append(_json_block("expected", entry.get("request")))
            body_parts.append(_json_block("actual", entry.get("response")))
        elif kind == "protocol":
            body_parts.append(_json_block("request", entry.get("request")))
            body_parts.append(_json_block("response", entry.get("response")))
        if screenshots:
            body_parts.append(_thumbnails(run_dir, screenshots))
        if error:
            body_parts.append(f'<p style="color:#b3261e">{html.escape(error)}</p>')
        if not ok and name == failed_step:
            failure_dir = run_dir / "failure"
            links = []
            if (failure_dir / "page.html").exists():
                links.append('<a href="failure/page.html" target="_blank">page HTML at failure</a>')
            if (failure_dir / "console.log").exists():
                links.append('<a href="failure/console.log" target="_blank">browser console at failure</a>')
            if links:
                body_parts.append("<p>" + " &middot; ".join(links) + "</p>")

        rows_html.append(f"""
        <div{anchor_id} style="border:1px solid #ddd;border-radius:8px;padding:10px 14px;margin:10px 0">
          <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
            <span style="color:#999;font-variant-numeric:tabular-nums">#{seq}</span>
            {party_badge}
            <span style="font-size:11px;color:#888;text-transform:uppercase">{html.escape(KIND_LABEL.get(kind, kind))}</span>
            <b>{html.escape(name)}</b>
            {status_badge}
            <span style="margin-left:auto;color:#999;font-size:12px">{duration:.2f}s</span>
          </div>
          {''.join(body_parts)}
        </div>
        """)

    started_at = entries[0]["ts"] if entries else None
    html_doc = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{html.escape(str(scenario))} - eval report</title>
<style>
body {{ font-family: -apple-system, Helvetica, Arial, sans-serif; max-width: 900px; margin: 24px auto; padding: 0 16px; color:#222; }}
table {{ border-collapse: collapse; }}
td {{ padding: 2px 10px 2px 0; }}
details summary {{ cursor: pointer; font-size: 12px; color: #555; }}
</style></head>
<body>
<h1>{html.escape(str(scenario))}</h1>
<p>{verdict_html} &nbsp; started: {html.escape(str(started_at))} &nbsp; duration: {duration_s if duration_s is not None else '?'}s</p>
<p>{failing_anchor}</p>
<h3>Repo versions</h3>
{_versions_table(versions)}
<h3>Steps</h3>
{''.join(rows_html) if rows_html else '<p><em>No transcript entries.</em></p>'}
</body></html>
"""
    out_path = run_dir / "report.html"
    out_path.write_text(html_doc)
    return out_path


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[0] != "--rebuild":
        print("usage: python -m harness.evidence --rebuild <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(argv[1]).resolve()
    if not run_dir.is_dir():
        print(f"no such run directory: {run_dir}", file=sys.stderr)
        return 1
    out = generate_report(run_dir)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
