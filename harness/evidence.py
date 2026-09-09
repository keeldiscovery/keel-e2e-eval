"""Run bundle plumbing (data-model.md, contracts/evidence-contract.md): run_dir creation,
versions.json, verdict.json, failure captures, and the report.html generator -- which reads
transcript.jsonl alone, so `make report RUN=<dir>` can rebuild it from a crashed run too.

002-eval-scoring (T009/T014/T016): `generate_report` now also re-runs scoring every time it's
called (scorecard-contract.md: "make report RUN=<dir> re-runs scoring + rendering from the
bundle alone") -- reading `facts.json` and `transcript.jsonl`, writing a fresh `scorecard.json`,
and re-stamping verdict.json's `score`/`policy_version`, without touching transcript.jsonl or
screenshots (SC-004). A scoring-layer crash is caught here so it degrades to "no scorecard"
rather than taking report generation down with it -- scorecard.json's absence is itself the
signal contract calls for.
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

from harness import rubric, scoring
from harness.interactions import Interaction, derive_interactions
from stack.config import REPO_ROOT

RUNS_DIR = REPO_ROOT / "runs"

# The five repos versions.json pins (spec 005 FR-012): this repo plus the four siblings it drives.
REPO_LABELS = ["keel-e2e-eval", "keel-cloud", "keel-web", "keel-runtime", "keel-connect-skill"]


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
    """The four siblings a run ran against, **plus the runtime that actually ran** (spec 012).

    `keel-runtime` names the *checkout*, which since spec 012 is only read from (caps,
    `build_prompt`) and no longer run. What runs is the copy that travelled inside the skill, and
    it is gitignored there -- so its commit cannot come from `git`, and `RUNTIME_VERSION` beside
    the skill is the record of which keel-runtime commit `make runtime` copied. A run that could
    not name the runtime it ran would be a run nobody can reproduce.
    """
    from stack import runtime as stack_runtime  # noqa: PLC0415 -- avoids a circular import

    repos = {
        "keel-e2e-eval": _git_info(REPO_ROOT),
        "keel-cloud": _git_info(config.keel_cloud),
        "keel-web": _git_info(config.keel_web),
        "keel-runtime": _git_info(config.keel_runtime),
        "keel-connect-skill": _git_info(config.keel_connect_skill),
        "keel-runtime (bundled, the one that runs)": {
            "path": str(stack_runtime.bundled_runtime_dir(config)),
            "runtime_version": stack_runtime.bundled_runtime_version(config),
            "present": stack_runtime.bundled_runtime_present(config),
        },
    }
    (run_dir / "versions.json").write_text(json.dumps(repos, indent=2))


# -------------------------------------------------------------------------------- verdict.json

def write_verdict(run_dir: Path, scenario: str, passed: bool, failed_step: str | None,
                   duration_s: float, *, score: float | None = None,
                   policy_version: int | None = None) -> None:
    verdict = {
        "scenario": scenario,
        "passed": passed,
        "failed_step": failed_step,
        "duration_s": round(duration_s, 3),
        # 002-eval-scoring, data-model.md's "verdict.json additions". None until scoring has run
        # at least once for this bundle (e.g. the very first write, before the finally block's
        # scoring step) -- distinct from "scoring crashed", which scorecard.json's absence signals.
        "score": score,
        "policy_version": policy_version,
    }
    (run_dir / "verdict.json").write_text(json.dumps(verdict, indent=2))


def finalize_run(run_dir: Path, *, slug: str, facts: dict | None = None, passed: bool,
                  failed_step: str | None, duration_s: float) -> dict | None:
    """The finally-block sequence a scored eval calls exactly once (T009): persist the fact
    registry, write verdict.json, and regenerate report.html (which itself runs scoring -- see
    this module's docstring). Called from inside the caller's own `finally`, so an interrupted
    run still gets a scored, reported bundle rather than losing its evidence.

    Takes `slug` + `facts` directly (spec 005-connect-stack FR-006/FR-013) rather than a
    `Scenario` object -- `evals/scenario.py`'s payload-builder abstraction is retired along with
    the agent-protocol harness it served; `evals/payroll_exceptions.py` is a plain fixture
    module, not a Scenario subclass.
    """
    try:
        scoring.write_facts(run_dir, facts or {})
    except Exception as exc:  # noqa: BLE001 - persisting facts must never mask the scenario's outcome
        (run_dir / "scoring_error.txt").write_text(f"could not write facts.json: {type(exc).__name__}: {exc}")
    write_verdict(run_dir, scenario=slug, passed=passed, failed_step=failed_step,
                  duration_s=duration_s)
    generate_report(run_dir)
    return _read_json(run_dir / "scorecard.json")


def write_generated(run_dir: Path, *, script: dict | None = None, inputs: dict | None = None) -> None:
    """spec 010 FR-006: the script this run generated from the corpus, and what the founder and
    each person typed, into the bundle beside the transcript.

    **Nothing generated is committed** (spec judgement call 1): a checked-in script could go stale
    against a corpus that moved and a run could be green anyway, which is the one thing freezing
    the corpus exists to prevent. Written here instead, so `runs/<id>/` shows the corpus, the
    screen and the wire side by side and a reader can check every value by eye (SC-009).
    """
    if script is not None:
        (run_dir / "script.json").write_text(
            json.dumps(script, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if inputs is not None:
        (run_dir / "inputs.json").write_text(
            json.dumps(inputs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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
    # The second founder on a two-founder instance (S-010). A report about two people telling them
    # apart at a glance is the whole reason this row exists; unknown parties still fall back to
    # grey, so nothing depends on it being here.
    "founder-b": "#0f6f8c",
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


def _generated_section(run_dir: Path) -> str:
    """spec 010 FR-006: `script.json` and `inputs.json` rendered beside the transcript, so the
    bundle shows the corpus, the screen and the wire without rerunning anything. Absent for every
    scenario that generates neither (S-002, S-003), which is why this returns "" rather than an
    empty heading."""
    script = _read_json(run_dir / "script.json")
    inputs = _read_json(run_dir / "inputs.json")
    if script is None and inputs is None:
        return ""
    provenance = ""
    if script:
        provenance = (f'<p style="font-size:12px;color:#666">corpus entry '
                      f'<b>{html.escape(str(script.get("_entry_id", "?")))}</b> &middot; sha256 '
                      f'{html.escape(str(script.get("_entry_sha256", "?"))[:16])}… &middot; '
                      f'{html.escape(str(script.get("_source", "")))}</p>')
    return ("<h3>Generated from the corpus</h3>" + provenance
            + _json_block("script.json (what keel-runtime answered from)", script)
            + _json_block("inputs.json (what the founder and each person typed)", inputs))


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


# --------------------------------------------------------------------------------- scoring (002)

def _score_and_stamp(run_dir: Path, verdict: dict | None) -> dict | None:
    """Runs harness.scoring over this bundle (transcript.jsonl + facts.json), writes
    scorecard.json, and re-stamps verdict.json's score/policy_version -- the "re-runs scoring"
    half of `make report RUN=<dir>` (scorecard-contract.md). Returns the scorecard dict, or None
    if there's no verdict (nothing ran yet) or scoring itself crashed.
    """
    if verdict is None:
        return None
    scenario_slug = verdict.get("scenario") or run_dir.name
    complete = bool(verdict.get("passed"))
    try:
        facts = scoring.read_facts(run_dir)
        scorecard = scoring.score_bundle(run_dir, scenario=scenario_slug, complete=complete, facts=facts)
    except Exception as exc:  # noqa: BLE001 - a scoring bug must degrade to "no scorecard", not crash the report
        (run_dir / "scoring_error.txt").write_text(f"{type(exc).__name__}: {exc}")
        return None
    write_verdict(run_dir, scenario=scenario_slug, passed=verdict.get("passed", False),
                  failed_step=verdict.get("failed_step"), duration_s=verdict.get("duration_s") or 0.0,
                  score=scorecard["run_score"], policy_version=scorecard["policy_version"])
    return scorecard


_CATEGORY_ORDER = ["FIDELITY", "GUIDANCE", "ORIENTATION", "CLARITY"]


def _score_color(score: float | None) -> str:
    if score is None:
        return "#999"
    if score >= 4.5:
        return "#1a7f5a"
    if score >= 3.5:
        return "#6b8f1a"
    if score >= 2.5:
        return "#b3691b"
    return "#b3261e"


def _score_header(scorecard: dict | None) -> str:
    if scorecard is None:
        return "<p><em>No scorecard.json (scoring hasn't run, or crashed -- see scoring_error.txt if present).</em></p>"
    run_score = scorecard.get("run_score")
    categories = scorecard.get("categories") or {}
    # 003-eval-set T003/T013 (design §6.1): a category no interaction in this run could ever carry
    # (S-007's no-browser scorecard) is "not applicable", not "no data" -- distinguishable in the
    # header so a reviewer doesn't mistake a by-design absence for a gap.
    not_applicable = set(scorecard.get("not_applicable_categories") or [])
    bars = []
    for attribute in _CATEGORY_ORDER:
        score = categories.get(attribute)
        pct = (score / 5 * 100) if score is not None else 0
        if score is not None:
            label = f"{score:g}/5"
        else:
            label = "not applicable" if attribute in not_applicable else "no data"
        color = _score_color(score)
        bars.append(f"""
        <div style="margin:6px 0">
          <div style="display:flex;justify-content:space-between;font-size:12px;color:#444">
            <span>{attribute.title()}</span><span>{label}</span>
          </div>
          <div style="background:#eee;border-radius:4px;height:8px">
            <div style="width:{pct:.0f}%;background:{color};height:8px;border-radius:4px"></div>
          </div>
        </div>""")
    gated_badge = _badge("GATED -- incomplete run, capped", "#b3261e") if scorecard.get("gated") else ""
    # Three states, not two (spec 012): a score; **not scored**, when every one of the four
    # attributes is not applicable to this scenario (S-008 referees a contract, not a screen);
    # and `?/5`, which means scoring itself has not answered yet.
    if run_score is not None:
        run_score_label = f"{run_score:g}/5"
    elif len(not_applicable) == len(_CATEGORY_ORDER):
        run_score_label = "not scored"
    else:
        run_score_label = "?/5"
    return f"""
    <div style="border:2px solid #333;border-radius:10px;padding:16px 20px;margin:16px 0 24px">
      <div style="display:flex;align-items:baseline;gap:16px;flex-wrap:wrap">
        <span style="font-size:44px;font-weight:700;color:{_score_color(run_score)}">{run_score_label}</span>
        <span style="color:#666;font-size:13px">policy v{scorecard.get('policy_version')}</span>
        {gated_badge}
      </div>
      {''.join(bars)}
    </div>"""


def _attribute_chip(attribute: str, score: float) -> str:
    color = _score_color(score)
    return (f'<span style="display:inline-block;padding:1px 8px;border-radius:10px;font-size:11px;'
            f'font-weight:600;color:#fff;background:{color}">{html.escape(attribute[:3].title())} {score:g}</span>')


def _conversation_card(conversation: dict | None) -> str:
    """The agent surface's stand-in for "a screenshot of each interaction" (design §2/§7 pass
    5): instruction purpose+content, requirements, the founder's (summarized) reply, and the
    outcome -- prose, not the raw JSON (which stays available in the interaction's own raw-step
    JSON blocks below, per scorecard-contract.md)."""
    if not conversation:
        return ""
    parts = []
    instruction = conversation.get("instruction")
    if instruction and (instruction.get("purpose") or instruction.get("content")):
        if instruction.get("purpose"):
            parts.append(f"<p><b>Purpose:</b> {html.escape(instruction['purpose'])}</p>")
        if instruction.get("content"):
            parts.append(f"<p><b>Instruction:</b> {html.escape(instruction['content'])}</p>")
    requirements = conversation.get("requirements")
    if requirements:
        items = "".join(f"<li>{html.escape(r)}</li>" for r in requirements)
        parts.append(f"<p><b>Requirements:</b></p><ul style='margin-top:2px'>{items}</ul>")
    if conversation.get("reply_summary"):
        parts.append(f"<p><b>Founder's reply:</b> {html.escape(conversation['reply_summary'])}</p>")
    if conversation.get("outcome"):
        parts.append(f"<p><b>Outcome:</b> {html.escape(str(conversation['outcome']))}</p>")
    if not parts:
        return ""
    return (f'<div style="background:#f3f3fb;border-radius:6px;padding:8px 14px;margin:8px 0">'
            f'{"".join(parts)}</div>')


def _interaction_card(entry: dict, interaction: Interaction | None, run_dir: Path) -> str:
    """One card per interaction (scorecard-contract.md): title, type/party badges, attribute
    chips, screenshots or a conversation card, and failed/waived checks inline (passed ones
    collapsed) -- the review surface design §7 pass 5 asks for.
    """
    attributes = entry.get("attributes") or {}
    chips = "".join(_attribute_chip(a, s) for a, s in attributes.items())
    party = interaction.party if interaction else "stack"
    party_badge = _badge(party, PARTY_COLOR.get(party, "#555"))
    type_badge = _badge(entry.get("type", "?"), "#444")

    body_parts = []
    if interaction and interaction.conversation:
        body_parts.append(_conversation_card(interaction.conversation))
    if interaction and interaction.screenshots:
        body_parts.append(_thumbnails(run_dir, interaction.screenshots))

    checks = entry.get("checks") or []
    notable = [c for c in checks if not c.get("pass") or c.get("waived")]
    passed_clean = [c for c in checks if c.get("pass") and not c.get("waived")]
    if notable:
        rows = []
        for check in notable:
            waived = check.get("waived")
            status, color = ("WAIVED", "#b3691b") if waived else ("FAILED", "#b3261e")
            reference = f" ({html.escape(waived['reference'])})" if waived else ""
            rows.append(f'<li>{_badge(status, color)} <b>{html.escape(check["check_id"])}</b> '
                        f'&mdash; {html.escape(check.get("detail", ""))}{reference}</li>')
        body_parts.append(f'<ul style="padding-left:18px;margin:6px 0">{"".join(rows)}</ul>')
    if passed_clean:
        body_parts.append(_json_block(
            f"{len(passed_clean)} passed check(s)",
            {c["check_id"]: c.get("detail") for c in passed_clean},
        ))

    step_links = ""
    if interaction and interaction.step_seqs:
        anchors = " &middot; ".join(f'<a href="#step-{seq}">#{seq}</a>' for seq in interaction.step_seqs)
        step_links = f'<p style="font-size:11px;color:#888">raw steps: {anchors}</p>'

    return f"""
    <div style="border:1px solid #ccd;border-radius:8px;padding:10px 14px;margin:10px 0;background:#fafaff">
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        {party_badge}{type_badge}
        <b>{html.escape(entry.get('title', entry.get('id', '')))}</b>
        {chips}
      </div>
      {''.join(body_parts)}
      {step_links}
    </div>"""


def _scorecard_matrix(scorecard: dict | None) -> str:
    if not scorecard or not scorecard.get("interactions"):
        return ""
    header_cells = "".join(f"<th>{a.title()}</th>" for a in _CATEGORY_ORDER)
    rows = []
    for entry in scorecard["interactions"]:
        attributes = entry.get("attributes") or {}
        cells = "".join(f"<td>{attributes[a]:g}</td>" if a in attributes else "<td>&mdash;</td>"
                         for a in _CATEGORY_ORDER)
        rows.append(f"<tr><td>{html.escape(entry.get('title', entry.get('id', '')))}</td>{cells}</tr>")
    return f"""
    <h3>Scorecard matrix</h3>
    <table style="border-collapse:collapse;width:100%">
      <tr><th style="text-align:left">Interaction</th>{header_cells}</tr>
      {''.join(rows)}
    </table>"""


def generate_report(run_dir: Path) -> Path:
    """Rebuilds report.html from transcript.jsonl alone (plus versions.json/verdict.json when
    present) -- re-runnable via `make report RUN=<dir>`, and safe to call on a crashed run: a
    missing verdict.json renders as "harness crashed" rather than raising.

    002-eval-scoring: also re-runs scoring (`_score_and_stamp`) every call, and adds the score
    header, per-interaction cards, and the scorecard matrix (scorecard-contract.md).
    """
    entries = _read_transcript(run_dir)
    versions = _read_json(run_dir / "versions.json")
    verdict = _read_json(run_dir / "verdict.json")
    scorecard = _score_and_stamp(run_dir, verdict)
    if scorecard is not None:
        # _score_and_stamp re-wrote verdict.json's score/policy_version -- re-read so the header
        # below reflects them too.
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

    facts = scoring.read_facts(run_dir)
    interactions, _results = rubric.evaluate(derive_interactions(entries), facts)
    interactions_by_id = {ix.id: ix for ix in interactions}

    interaction_cards_html = ""
    if scorecard is not None:
        interaction_cards_html = "".join(
            _interaction_card(entry, interactions_by_id.get(entry["id"]), run_dir)
            for entry in scorecard.get("interactions", [])
        )

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
          <a id="step-{seq}"></a>
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
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ padding: 4px 10px 4px 0; border-bottom: 1px solid #eee; text-align: left; }}
details summary {{ cursor: pointer; font-size: 12px; color: #555; }}
</style></head>
<body>
<h1>{html.escape(str(scenario))}</h1>
<p>{verdict_html} &nbsp; started: {html.escape(str(started_at))} &nbsp; duration: {duration_s if duration_s is not None else '?'}s</p>
<p>{failing_anchor}</p>
{_score_header(scorecard)}
<h3>Repo versions</h3>
{_versions_table(versions)}
{_generated_section(run_dir)}
<h3>Interactions</h3>
{interaction_cards_html if interaction_cards_html else '<p><em>No scored interactions (no scorecard.json).</em></p>'}
{_scorecard_matrix(scorecard)}
<h3>Steps</h3>
{''.join(rows_html) if rows_html else '<p><em>No transcript entries.</em></p>'}
</body></html>
"""
    out_path = run_dir / "report.html"
    out_path.write_text(html_doc)
    return out_path


def _verdict_badge_html(passed: bool | None) -> str:
    if passed is None:
        return _badge("HARNESS CRASHED", "#b3261e")
    return _badge("PASSED", "#1a7f5a") if passed else _badge("FAILED", "#b3261e")


def _index_category_bars(categories: dict, not_applicable: list) -> str:
    parts = []
    for attribute in _CATEGORY_ORDER:
        score = categories.get(attribute)
        if attribute in (not_applicable or []):
            label, pct, color = "N/A", 0, "#ccc"
        elif score is None:
            label, pct, color = "—", 0, "#eee"
        else:
            label, pct, color = f"{score:g}", score / 5 * 100, _score_color(score)
        parts.append(f"""
        <div style="display:flex;align-items:center;gap:6px;font-size:11px;color:#555;margin:2px 0">
          <span style="width:26px">{attribute[:3].title()}</span>
          <span style="background:#eee;border-radius:3px;height:6px;width:60px;display:inline-block;overflow:hidden">
            <span style="display:block;height:6px;width:{pct:.0f}%;background:{color}"></span>
          </span>
          <span style="width:24px">{html.escape(label)}</span>
        </div>""")
    return "".join(parts)


def generate_index(run_dirs: list[Path], out_path: Path) -> Path:
    """T013 (design §3, FR-005): one page listing a batch of run bundles -- slug, verdict, score,
    per-category bars (N/A rendered distinctly from a real 0, per `not_applicable_categories`,
    T003), and a link to each bundle's own `report.html`. Reads only `verdict.json`/
    `scorecard.json` from each bundle -- never re-runs scoring itself (that stays
    `generate_report`'s/`make report`'s job; `eval_all.py` calls both, in that order, for the
    bundles it just produced).
    """
    rows = []
    total_score = 0.0
    total_weight = 0
    for run_dir in run_dirs:
        verdict = _read_json(run_dir / "verdict.json") or {}
        scorecard = _read_json(run_dir / "scorecard.json")
        slug = verdict.get("scenario") or run_dir.name
        score = verdict.get("score")
        categories = (scorecard or {}).get("categories") or {}
        not_applicable = (scorecard or {}).get("not_applicable_categories") or []
        report_href = f"{run_dir.name}/report.html"
        if score is not None:
            total_score += score
            total_weight += 1
        rows.append(f"""
        <tr>
          <td>{html.escape(slug)}</td>
          <td>{_verdict_badge_html(verdict.get("passed"))}</td>
          <td style="font-weight:700;font-size:18px;color:{_score_color(score)}">
            {f"{score:g}/5" if score is not None else "?/5"}</td>
          <td>{_index_category_bars(categories, not_applicable)}</td>
          <td><a href="{html.escape(report_href)}" target="_blank">report.html</a></td>
          <td style="color:#888;font-size:12px">{html.escape(run_dir.name)}</td>
        </tr>""")

    average = f"{total_score / total_weight:.1f}/5" if total_weight else "?/5"
    generated_at = datetime.now(timezone.utc).isoformat()
    html_doc = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>keel-e2e-eval -- run index</title>
<style>
body {{ font-family: -apple-system, Helvetica, Arial, sans-serif; max-width: 1000px; margin: 24px auto; padding: 0 16px; color:#222; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ padding: 8px 10px; border-bottom: 1px solid #eee; text-align: left; vertical-align: top; }}
</style></head>
<body>
<h1>Eval set -- run index</h1>
<p>generated {html.escape(generated_at)} &nbsp; {len(run_dirs)} run(s) &nbsp;
   average score across scored runs: <b>{average}</b></p>
<table>
  <tr><th>Scenario</th><th>Verdict</th><th>Score</th><th>Categories</th><th>Report</th><th>Run</th></tr>
  {''.join(rows) if rows else '<tr><td colspan="6"><em>No runs.</em></td></tr>'}
</table>
</body></html>
"""
    out_path.write_text(html_doc)
    return out_path


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[0] == "--rebuild":
        run_dir = Path(argv[1]).resolve()
        if not run_dir.is_dir():
            print(f"no such run directory: {run_dir}", file=sys.stderr)
            return 1
        out = generate_report(run_dir)
        print(f"wrote {out}")
        return 0
    if len(argv) >= 2 and argv[0] == "--index":
        out_path = Path(argv[1]).resolve()
        run_dirs = [Path(p).resolve() for p in argv[2:]]
        out = generate_index(run_dirs, out_path)
        print(f"wrote {out}")
        return 0
    print("usage: python -m harness.evidence --rebuild <run_dir>", file=sys.stderr)
    print("       python -m harness.evidence --index <out.html> <run_dir> [<run_dir> ...]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
