"""The run bundle, and the one file a person reads (spec 009 FR-015/FR-016/FR-020/FR-021).

The bundle, not the number, is the product of a run -- this repo's oldest rule, applied here
unchanged. Every number in `report.html` traces to a prompt and an envelope on disk, and anything
that cannot honestly be a number is rendered rather than left out.

`report.html` is one self-contained file with no network resources, and it always carries three
things that are easy to forget and expensive to forget: **the model this run was judged under**
(the marks are comparable only within a model -- keel-runtime sends no `--model` and this repo does
not add one), **the `MARKS_VERSION`** that judged it, and **the stated blind spots** -- the register
is not scored and no metric represents it; whether an option list leads is not scored either;
wording is free.
"""

from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

from harness.evidence import new_run_dir, write_versions

from . import brief as brief_mod
from . import marks as marks_mod


# Which host answered is part of a bundle's *name*, not only of its contents (spec 014 FR-005).
# Two hosts' runs are different measurements that must never be averaged, and the cheapest place
# to say so is the one string that appears in every `ls`, every README line and every citation.
# `claude` keeps the bare name it has always had, so every existing run of record still reads as
# what it is rather than being retroactively renamed.
HOST_SUFFIXES = {"claude": "", "copilot": "-copilot", "codex": "-codex"}


def start_bundle(config, *, baseline: bool, host: str = "claude") -> Path:
    slug = "instructions-baseline" if baseline else "instructions"
    slug += HOST_SUFFIXES.get(host, f"-{host}")
    run_dir = new_run_dir(slug)
    write_versions(run_dir, config)
    return run_dir


def write_manifest(run_dir: Path, manifest: dict) -> None:
    """`manifest.json`: host, CLI, model and rubric, written **before the first call** and again
    after the last (spec 014 FR-005). A run that died at case one still names what it was."""
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str),
                                           encoding="utf-8")


def write_corpus_hashes(run_dir: Path, corpus, *, when: str = "before") -> None:
    lines = [f"{digest}  {path}" for path, digest in sorted(corpus.hashes.items())]
    path = run_dir / "corpus.sha256"
    header = f"# {when} the run\n"
    path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")


def copy_contracts(run_dir: Path, exported) -> None:
    target = run_dir / "contracts"
    if Path(exported.directory).resolve() != target.resolve():
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(exported.directory, target)


def case_dir(run_dir: Path, case) -> Path:
    path = run_dir / "cases" / case.bundle_path
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_case(run_dir: Path, case, answer, diff: dict, *, host: str = "claude") -> None:
    """`prompt.txt`, `envelope.json`, `diff.json` -- the three files a finding is quoted from.

    `prompt.txt` is what **this host** was sent, byte for byte: on Copilot that includes the
    `SYSTEM` and `RESPONSE` sections the CLI has no flag for, which Claude receives as flags
    (design §5.4, C-8). `instructions/prompts.py` renders each with keel-runtime's own renderer,
    so neither bundle ever carries the other host's prompt.
    """
    directory = case_dir(run_dir, case)
    (directory / "prompt.txt").write_text(case.prompt, encoding="utf-8")
    redraw = getattr(answer, "redraw", None)
    if redraw is not None and getattr(answer, "redraw_prompt", ""):
        (directory / "prompt-redraw.txt").write_text(answer.redraw_prompt, encoding="utf-8")
    (directory / "envelope.json").write_text(json.dumps({
        "case_id": case.case_id,
        "host": host,
        "screen": case.screen,
        "outcome": answer.outcome,
        "schema_valid": answer.schema_valid,
        "schema_error": answer.schema_error,
        "recovery_pass": answer.recovery_pass,
        "num_turns": answer.num_turns,
        "total_cost_usd": answer.total_cost_usd,
        "premium_requests": answer.premium_requests,
        "reported_model": answer.reported_model,
        # The wire's own pin for this case (`instructions/models.py`), `None` on the CLI default.
        "model_requested": getattr(case, "model", None),
        # Both halves of it (keel-cloud table v6): `None` on every reading by construction, because
        # `reading` routes to the `light` tier whose row carries no effort.
        "effort_requested": getattr(case, "effort", None),
        "duration_s": round(answer.duration_s, 3),
        "error": answer.error,
        "result": answer.result,
        "questions": answer.questions,
        "envelope": answer.envelope,
        # Judgement call 41: the first draft, the answer a founder would see (`null` when the
        # aggregate refused both drafts, or judged this one only at the end of the run), which
        # of them the structural marks read, every refusal, and the repair turn itself.
        **_drafts(answer),
    }, indent=2, default=str), encoding="utf-8")
    (directory / "diff.json").write_text(json.dumps(diff, indent=2, default=str),
                                         encoding="utf-8")


def _drafts(answer) -> dict:
    view = getattr(answer, "view", None)
    if view is None:
        return {}
    accepted = answer.accepted
    redraw = answer.redraw
    return {
        "answer": {"raw": answer.view(), "accepted": accepted.view() if accepted else None,
                   "scored": "accepted" if accepted is not None else "raw"},
        "refusals": answer.refusals,
        "redraw": None if redraw is None else {
            "repair": ((answer.redraw_payload or {}).get("context") or {}).get("repair"),
            "request_payload": answer.redraw_payload,
            "outcome": redraw.outcome, "result": redraw.result, "questions": redraw.questions,
            "schema_valid": redraw.schema_valid,
            "schema_error": redraw.schema_error, "error": redraw.error,
            "num_turns": redraw.num_turns, "total_cost_usd": redraw.total_cost_usd,
            "premium_requests": redraw.premium_requests, "tokens": redraw.tokens,
            "reported_model": redraw.reported_model, "duration_s": round(redraw.duration_s, 3),
            "envelope": redraw.envelope},
    }


def write_scorecard(run_dir: Path, scorecard: dict) -> None:
    (run_dir / "scorecard.json").write_text(json.dumps(scorecard, indent=2, default=str),
                                            encoding="utf-8")


def write_verdict(run_dir: Path, verdict: dict) -> None:
    (run_dir / "verdict.json").write_text(json.dumps(verdict, indent=2, default=str),
                                          encoding="utf-8")


# ------------------------------------------------------------------------------------ report.html

_CSS = """
body{font:14px/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;margin:0;
 background:#faf9f7;color:#1c1a17}
main{max-width:1100px;margin:0 auto;padding:24px}
h1{font-size:24px;margin:0 0 4px}h2{font-size:18px;margin:32px 0 8px;border-bottom:1px solid #ddd8d0;
 padding-bottom:4px}h3{font-size:15px;margin:20px 0 6px}
.banner{padding:12px 16px;border-radius:6px;margin:12px 0;font-weight:600}
.banner.fail{background:#f8e2e0;color:#7a2018}.banner.pass{background:#e2f0e2;color:#1c5220}
.banner.note{background:#f3ecdc;color:#5c4813;font-weight:400}
table{border-collapse:collapse;width:100%;margin:8px 0;font-size:13px}
th,td{border:1px solid #e3ded6;padding:5px 8px;text-align:left;vertical-align:top}
th{background:#f1ede6;font-weight:600}
code,pre{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px}
pre{background:#f1ede6;padding:10px;overflow-x:auto;white-space:pre-wrap;word-break:break-word}
details{margin:6px 0}summary{cursor:pointer;font-weight:600}
.small{font-size:12px;color:#6b6459}
"""


#: The report's own classes -- kept off `register.html`, which carries no mark of any kind.
_REPORT_CSS = """
.mark.met{color:#1c5220;font-weight:600}.mark.missed{color:#a3271b;font-weight:600}
.tick{color:#1c5220}.cross{color:#a3271b}.na{color:#8a8378}
"""


def _esc(value) -> str:
    return html.escape("" if value is None else str(value))


def _pct(value) -> str:
    return "—" if value is None else f"{value * 100:.1f}%"


def _spend(verdict: dict) -> str:
    """What this run cost, **in the unit its host reports** (spec 014 FR-007, design C-7).

    Claude Code reports dollars; Copilot reports premium requests and no dollars at all. A
    `$0.00` on a Copilot report would be a lie in the shape of a number, so the two are never
    converted into one another and a run that reported neither says so.
    """
    premium = verdict.get("total_premium_requests")
    if premium is not None:
        return f"{premium:g} premium requests (this host reports no dollars)"
    tokens = verdict.get("total_tokens")
    if tokens:
        return (f"{tokens.get('input_tokens', 0)} input + {tokens.get('output_tokens', 0)} output "
                "tokens (this host reports tokens against a plan, no dollars)")
    dollars = verdict.get("total_cost_usd")
    if dollars is not None:
        return f"${dollars:.2f}"
    return "cost not reported"


# The host's own name for itself, for a page a person reads (spec 014 FR-006).
HOST_NAMES = {"claude": "Claude Code", "copilot": "GitHub Copilot", "codex": "Codex"}


def host_name(host) -> str:
    return HOST_NAMES.get(host, str(host or "unknown host"))


def _mark_row(name: str, result: dict, fmt=_pct) -> str:
    """One mark: its value, its bar, and whether it was met -- or *not measured*, which is a row
    that failed and says why it failed (judgement call 13), never a blank."""
    measured = result.get("measured", result.get("value") is not None)
    cls = "met" if result["met"] else "missed"
    word = "met" if result["met"] else ("NOT measured" if not measured else "NOT met")
    value = fmt(result["value"]) if measured else "not measured"
    return (f"<tr><td>{_esc(name)}</td><td>{value}</td>"
            f"<td>{_esc(result['mark'])}</td><td class='mark {cls}'>{word}</td></tr>")


def _count(value) -> str:
    return "—" if value is None else str(value)


#: The eight rows of the v11 mark table, in `marks.ROWS` order: (row, label, formatter).
MARK_ROWS = (
    ("dimension_coverage", "dimension coverage (one question a dimension, both screens)", _pct),
    ("option_validity", "option validity (every registry rule, every question)", _pct),
    ("no_leak", "no leak (mechanism words and founder values, swept)", _pct),
    ("anchoring_accuracy", "anchoring accuracy (one judgement a readable person)", _pct),
    ("compare_correctness", "compare correctness (keel-cloud's engine, status + drift)", _pct),
    ("refusals", "rule refusals, as a rate of answers judged", _pct),
    ("shape_refusals", "shape refusals", _count),
    ("brief_paragraphs", "BRIEF paragraphs (all four marks)", _pct),
)


def render_report(run_dir: Path, *, verdict: dict, scorecard: dict, versions: dict,
                  host: str = "claude", filename: str = "report.html") -> Path:
    t = scorecard["totals"]
    judged = verdict["marks"]
    baseline = verdict.get("baseline")
    named_host = host_name(host)

    parts = [f"<!doctype html><meta charset='utf-8'><title>Instruction eval on {_esc(named_host)}"
             f" — {_esc(run_dir.name)}</title><style>{_CSS}{_REPORT_CSS}</style><main>"]
    parts.append(f"<h1>The instruction eval on {_esc(named_host)}</h1>"
                 f"<p class='small'>{_esc(run_dir.name)}</p>")
    parts.append(
        f"<div class='banner note'><b>This run was answered by {_esc(named_host)}</b> "
        f"(<code>{_esc((scorecard.get('model') or {}).get('cli_version') or 'version unknown')}"
        "</code>). keel-cloud <code>canon/designs/keel-skill-design.md</code> §5.5: <b>two runs "
        "under different hosts are different measurements and must never be averaged.</b> Read "
        "this page against the same host's own previous run, never against the other's.</div>")
    if verdict.get("dry_run"):
        parts.append("<div class='banner note'><b>A dry run.</b> Nothing was called and nothing "
                     "was spent: <code>compare_correctness</code> is measured, because keel-cloud's "
                     "engine needs no model, and every model-scored mark is <em>not measured</em> "
                     "-- so this verdict is <code>passed: false</code> by construction (judgement "
                     "calls 13 and 34).</div>")
    if baseline:
        parts.append("<div class='banner note'><b>This is the baseline.</b> A red result is the "
                     "expected one.</div>")

    cls = "pass" if judged.get("passed") else "fail"
    word = "PASSED" if judged.get("passed") else "FAILED"
    parts.append(f"<div class='banner {cls}'>{word}</div>")

    parts.append("<table><tr><th>Mark</th><th>This run</th><th>Required</th><th></th></tr>")
    for name, label, fmt in MARK_ROWS:
        result = judged.get(name) or {"value": None, "mark": "—", "met": False,
                                      "measured": False}
        parts.append(_mark_row(label, result, fmt))
    parts.append("</table>")
    unmet = verdict.get("unmet_prerequisites") or scorecard.get("unmet_prerequisites") or []
    if unmet:
        parts.append("<h3>Prerequisites not met, by name</h3><ul>"
                     + "".join(f"<li>{_esc(reason)}</li>" for reason in unmet) + "</ul>")

    model = scorecard.get("model") or {}
    per_class = model.get("models_used")
    per_class_effort = model.get("efforts_used") or {}
    if per_class:
        def _leg(job_class, name):
            if not name:
                return f"{_esc(job_class)} <b>the CLI's default</b>"
            effort = per_class_effort.get(job_class)
            at = (f" at <code>{_esc(effort)}</code>" if effort
                  else " at <b>the CLI's own effort</b>")
            return f"{_esc(job_class)} <code>{_esc(name)}</code>{at}"

        pinned = (", pinned per job class through the job's own <code>model</code> and "
                  "<code>effort</code> keys: "
                  + " · ".join(_leg(job_class, name) for job_class, name in per_class.items())
                  + (f" (table: <code>{_esc(model.get('models_source'))}</code>)"
                     if model.get("models_source") else ""))
    elif model.get("pinned_model"):
        pinned = f", pinned with <code>--model {_esc(model.get('pinned_model'))}</code>"
    else:
        pinned = (", <b>nothing pinned</b> — so what answered is whatever this CLI's router "
                  "chose on the day (design §5.4, C-5)")
    parts.append(
        f"<p><b>Judged under:</b> {_esc(named_host)}, "
        f"<code>{_esc(model.get('cli_version') or 'unknown CLI version')}</code>"
        + (f", model <code>{_esc(model.get('reported_model'))}</code>"
           if model.get("reported_model") else ", and <b>the CLI reported no model</b>")
        + pinned
        + ". <b>These marks are comparable only within this host and this model.</b> "
          f"The tie-breaking judge is <code>{_esc(model.get('judge_host') or 'off')}</code> on "
          "both hosts, deliberately, so the scoring is one constant across a comparison.</p>")
    parts.append(f"<p class='small'>MARKS_VERSION {marks_mod.MARKS_VERSION} · N = "
                 f"{_esc(verdict.get('n_runs'))} · {_esc(verdict.get('cases'))} cases · "
                 f"{_esc(verdict.get('errored'))} errored · "
                 f"{_spend(verdict)} · "
                 f"{verdict.get('duration_s', 0):.0f}s · registry "
                 f"{_esc(scorecard.get('registry_version'))}</p>")
    caps = (f"max turns {_esc(model.get('job_max_turns'))}"
            if model.get("job_max_turns") is not None
            else "<b>no turn cap</b> — this CLI has no flag for one")
    caps += (f" · budget ${_esc(model.get('job_budget_usd'))}"
             if model.get("job_budget_usd") is not None
             else " · <b>no dollar cap</b> — this CLI has none, and none is invented (C-7)")
    if model.get("max_ai_credits") is not None:
        caps += f" · max AI credits {_esc(model.get('max_ai_credits'))}"
    parts.append(f"<p class='small'>Executor caps, production's own and not overridden here: "
                 f"wall clock <b>{_esc(model.get('job_timeout_seconds'))}s</b> · "
                 f"{caps}. Judge: <b>{_esc(model.get('judge') or 'on')}</b>, "
                 f"{_esc(t.get('judge_calls', 0))} calls; it decided "
                 f"{_esc(t.get('leak_judged', 0))} of the {_esc(t.get('leak_hit_items', 0))} "
                 f"items with a <code>no_leak</code> hit ({_esc(t.get('leak_hits', 0))} word hits) "
                 f"— <b>{_pct(t.get('judged_fraction'))}</b>. Every other item was decided by "
                 "code.</p>")
    parts.append(wording_html(t.get("wording")))

    parts.append("<h2>Sibling commits</h2><table><tr><th>Repo</th><th>Commit</th><th>Dirty</th></tr>")
    for name, info in versions.items():
        parts.append(f"<tr><td>{_esc(name)}</td><td><code>{_esc((info.get('commit') or '')[:12])}"
                     f"</code></td><td>{'yes' if info.get('dirty') else 'no'}</td></tr>")
    parts.append("</table>")
    manifest = scorecard.get("contract_manifest") or {}
    parts.append(f"<p class='small'>Contract exported from keel-cloud "
                 f"<code>{_esc(manifest.get('keel_cloud_commit'))}</code>"
                 f"{' (dirty)' if manifest.get('keel_cloud_dirty') else ''} at "
                 f"{_esc(manifest.get('generated_at'))}.</p>")

    parts.append("<h2>What this run does not tell you</h2><div class='banner note'>"
                 "<b>The register is not scored, and no metric on this page represents it.</b> "
                 "Whether a question sounds like that market is design §3.8's <em>cannot be "
                 "checked by code</em>; a person who knows the market reads "
                 "<a href='register.html'>register.html</a>, and that reading is recorded with "
                 "the run.<br><b>The three interpretation screens are rendered, never scored</b> "
                 "(judgement call 28): their leaks are the aggregate's rule refusals and count in "
                 "the rate only.<br><b>Wording is free.</b> <code>option_validity</code> checks the "
                 "mapping onto the registry, never the invention (call 31); whether an option list "
                 "leads is still not scored.</div>")

    # --------------------------------------------------------------------------- compare
    parts.append("<h2>COMPARE — keel-cloud's engine against the corpus</h2>")
    if t.get("compare_measured"):
        parts.append(f"<p><b>{_esc(t['compare_agreed'])} of {_esc(t['compare_checks'])}</b> "
                     "status + drift checks agreed (every calibrated dimension -- 10 on a B2C entry, 12 on "
                     "a B2B one -- and 3 vectors an entry) · "
                     f"{_esc(t.get('compare_reported_diffs', 0))} counts differ (reported, never "
                     "marked — call 3).</p>")
    else:
        parts.append("<p><b>Not measured.</b> "
                     + "; ".join(_esc(f"{u['entry']}: {u['reason']}")
                                 for u in t.get("compare_unmeasured") or [])
                     + "</p>")
    rows = [(case, m) for case in scorecard.get("compare") or [] for m in case["mismatches"]]
    if rows:
        parts.append("<table><tr><th>Entry</th><th>Row</th><th>Corpus</th><th>Engine</th></tr>")
        for case, m in rows:
            parts.append(f"<tr><td>{_esc(case['entry_id'])}</td><td>{_esc(m['key'])}</td>"
                         f"<td><code>{_esc(json.dumps(m['expected']))}</code></td>"
                         f"<td><code>{_esc(json.dumps(m['produced']))}</code></td></tr>")
        parts.append("</table>")

    # ----------------------------------------------------------- the two question screens
    for title, prefix in (("CALIBRATION_QUESTIONS", "calibration"),
                          ("RESPONDENT_QUESTIONS", "respondent")):
        if not t.get(f"{prefix}_cases"):
            continue
        cov, val, leak = (t[f"{prefix}_coverage"], t[f"{prefix}_validity"], t[f"{prefix}_leak"])
        parts.append(f"<h2>{title}</h2><p>{t[f'{prefix}_cases']} cases · coverage "
                     f"{cov['hit']} of {cov['of']} · validity {val['hit']} of {val['of']} · "
                     f"leak {leak['clean']} clean of {leak['of']} swept</p>")
        faults = [(case, f) for case in scorecard.get(prefix) or []
                  for f in case.get("faults") or []]
        if faults:
            parts.append("<table><tr><th>Case</th><th>Dimension</th><th>Rule</th>"
                         "<th>Evidence</th></tr>")
            for case, f in faults:
                parts.append(f"<tr><td>{_esc(case['case_id'])}</td><td>{_esc(f.get('key'))}</td>"
                             f"<td>{_esc(f.get('check'))}</td><td>{_esc(f.get('evidence'))}</td>"
                             "</tr>")
            parts.append("</table>")

    # --------------------------------------------------------------------------- the reading
    if t.get("people_given"):
        parts.append("<h2>INTERPRET — one judgement a readable person</h2>")
        parts.append(f"<p>accuracy <b>{_pct(t['anchoring_accuracy'])}</b> over "
                     f"{t['people_answered']} answered of {t['people_given']} read · "
                     f"<b>GUESSED precision</b> {_pct(t['guessed_precision'])} · "
                     f"<b>GUESSED recall</b> {_pct(t['guessed_recall'])} · "
                     f"{t['reading_missing_ids']} never answered · "
                     f"{t['reading_extra_ids']} ids invented · "
                     f"{t.get('chipped_skipped', 0)} chipped stories GUESSED by code, never read"
                     "</p>")
        c = t["confusion"]
        parts.append("<table><tr><th></th><th>called ANCHORED</th><th>called GUESSED</th></tr>"
                     f"<tr><th>was ANCHORED</th><td>{c['aa']}</td><td>{c['ag']}</td></tr>"
                     f"<tr><th>was GUESSED</th><td>{c['ga']}</td><td>{c['gg']}</td></tr></table>")

    parts.append("<h3>Three ways of being wrong, three lines</h3><table>"
                 "<tr><th>Line</th><th>Count</th><th>What it means</th></tr>"
                 f"<tr><td>schema-invalid</td><td>{t['schema_invalid']}</td>"
                 "<td>keel-runtime's own validator refused it; keel-cloud never saw it</td></tr>"
                 f"<tr><td>shape refusals</td><td>{t['shape_refusals']}</td>"
                 "<td>it fit no contract the aggregate could read</td></tr>"
                 f"<tr><td>rule refusals</td><td>"
                 f"{sum(t['refusals_by_rule'].values()) if t.get('refusals_measured') else 'not measured'}</td>"
                 f"<td>the aggregate read it and refused it: "
                 f"{_esc(json.dumps(t['refusals_by_rule']))}</td></tr></table>")
    parts.append(_redraws_html(t, scorecard.get("redraws") or []))

    # ---------------------------------------------------------------------------------- brief
    if t.get("brief_measured"):
        parts.append("<h2>What this says (the BRIEF screen)</h2>")
        parts.append(f"<p><b>{_pct(t['brief_paragraphs'])}</b> of {t['brief_cases']} paragraphs "
                     f"met all {len(brief_mod.MARK_NAMES)} marks · "
                     f"{t['brief_needs_input']} asked a question on a screen "
                     "with nobody to ask.</p>")
        parts.append("<div class='banner note'><b>The context this subject sends is not, in one "
                     "field, the context production sends.</b> keel-cloud renders the deciding "
                     "line's number with <code>Measure.say</code>; this repo keeps no copy of that "
                     "arithmetic, so the middle answer goes over in the founder's own unit "
                     "(judgement call 19). And the paragraph is rendered whole on "
                     "<a href='register.html'>register.html</a>, unscored.</div>")
        by_mark = t.get("brief_by_mark") or {}
        parts.append("<table><tr><th>Mark</th><th>Met</th></tr>")
        for name in brief_mod.MARK_NAMES:
            row = by_mark.get(name) or {}
            parts.append(f"<tr><td><code>{_esc(name)}</code></td>"
                         f"<td>{row.get('met', 0)} / {row.get('of', 0)}</td></tr>")
        parts.append("</table>")
        misses = [c for c in (scorecard.get("brief") or []) if not c["met"]]
        if misses:
            parts.append(f"<h3>What the misses were ({len(misses)})</h3><table>"
                         "<tr><th>Case</th><th>Mark</th><th>Finding</th></tr>")
            for case in misses:
                for name, met in case["marks"].items():
                    if met is True:
                        continue
                    parts.append(f"<tr><td>{_esc(case['case_id'])}</td>"
                                 f"<td><code>{_esc(name)}</code></td>"
                                 f"<td>{_esc(case['findings'].get(name))}</td></tr>")
            parts.append("</table>")

    # ---------------------------------------------------------------------------------- spread
    parts.append("<h2>The spread</h2><p class='small'>Each of the N runs on its own. A case that "
                 "passes twice and fails once is an unstable instruction, not a 67 %.</p>")
    for title, block in sorted((scorecard.get("spread") or {}).items()):
        if not block:
            continue
        parts.append(f"<h3>{_esc(title)}</h3><table><tr><th>Case</th><th>Runs</th><th>min</th>"
                     "<th>max</th></tr>")
        for key, row in sorted(block.items()):
            runs = ", ".join(_pct(v) for v in row["runs"])
            parts.append(f"<tr><td>{_esc(key)}</td><td>{runs}</td><td>{_pct(row['min'])}</td>"
                         f"<td>{_pct(row['max'])}</td></tr>")
        parts.append("</table>")

    parts.append("<h2>The prompts</h2>")
    for entry in scorecard.get("prompts") or []:
        parts.append(f"<details><summary>{_esc(entry['case_id'])} — {_esc(entry['screen'])}"
                     "</summary><pre>" + _esc(entry["prompt"]) + "</pre></details>")

    parts.append("<h2><a href='register.html'>register.html</a></h2><p>Every produced question, "
                 "interpretation and paragraph, grouped by market and entry, with <b>no score, no "
                 "tick and no cross</b>. <b>Nothing on that page contributes to the verdict "
                 "above.</b></p>")
    parts.append("</main>")
    path = run_dir / filename
    path.write_text("".join(parts), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------------- register.html

_REGISTER_CSS = """
.market{background:#eee9df;padding:10px 14px;border-radius:6px;margin:26px 0 10px}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:10px 0}
.pair>div{border:1px solid #e3ded6;border-radius:6px;padding:10px;background:#fff}
.side{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:#8a8378;margin-bottom:4px}
ul{margin:4px 0 0 18px;padding:0}
"""


def wording_html(wording) -> str:
    """Call 56: the wording rules the subject only instructs, counted per screen -- reported, never
    a mark, and said so on the page."""
    if not wording:
        return ""
    rows = []
    for screen in ("calibration", "respondent"):
        w = wording.get(screen) or {}
        if not w.get("questions"):
            continue
        founder = (f" · W2 <i>do you think</i> {_esc(w.get('w2', 0))} · W6 second person "
                   f"{_esc(w.get('w6', 0))}" if screen == "calibration" else "")
        rows.append(f"{_esc(screen)}: {_esc(w.get('questions'))} questions with model text, "
                    f"{_esc(w.get('words'))} words · W1 over length {_esc(w.get('w1', 0))} · "
                    f"S1 clause first {_esc(w.get('s1', 0))}{founder} · W5 options over 8 words "
                    f"{_esc(w.get('w5', 0))} of {_esc(w.get('options', 0))}")
    if not rows:
        return ""
    return ("<p class='small'>Wording, <b>reported and never marked</b> (judgement call 56; "
            "<code>window-frame-design.md</code> §3.6-§3.8): " + "; ".join(rows) + ".</p>")


def _redraws_html(t: dict, redraws: list) -> str:
    """Judgement call 41, on the page: what the structural marks were scored on, and every redraw
    as raw -> accepted, beside the rule that refused the first draft."""
    scored_on = t.get("scored_on") or "accepted"
    out = ["<h3>Raw &rarr; accepted (judgement call 41)</h3>"]
    if scored_on != "accepted":
        out.append(f"<div class='banner note'><b>Scored on the raw answer.</b> {_esc(scored_on)}."
                   " <code>option_validity</code>, <code>dimension_coverage</code> and "
                   "<code>no_leak</code> read each first draft as it came back.</div>")
        return "".join(out)
    out.append(f"<p>The structural marks read the <b>accepted</b> answer -- the one a founder "
               f"sees after the runtime's rule refusal and one redraw; "
               f"<code>rule_refusal_rate</code> counts every refusal. "
               f"{t.get('redraws', 0)} redrawn · {t.get('redraws_accepted', 0)} accepted on the "
               f"redraw · {t.get('second_refusals', 0)} refused again (scored on the raw).</p>")
    if not redraws:
        return "".join(out)
    out.append("<table><tr><th>Case</th><th>First draft</th><th>Redraw</th></tr>")
    for row in redraws:
        first = row.get("first_refusal") or {}
        second = row.get("second_refusal") or {}
        after = ("accepted" if row.get("accepted") else
                 f"refused again ({second.get('rule') or second.get('kind') or 'no answer'})")
        out.append(f"<tr><td>{_esc(row.get('case_id'))}</td>"
                   f"<td>refused {_esc(first.get('rule'))}: {_esc(first.get('message'))}</td>"
                   f"<td>{_esc(after)}</td></tr>")
    out.append("</table>")
    return "".join(out)


def render_register(run_dir: Path, *, entries_by_market: dict,
                    paragraphs: dict | None = None,
                    host: str = "claude", cli_version: str | None = None,
                    model: str | None = None,
                    filename: str = "register.html") -> Path:
    """The one artefact in this bundle with no number in it (spec 009 FR-019; spec 029 FR-022).

    Per entry, grouped by market (screen-shapes §7): the three interpretations, verbatim, each
    marked *accepted* or *refused (rule id)* by the aggregate -- the only words this page adds; the
    calibration questions in registry order beside the registry's own founder question where it
    has one, the founder's chosen phrase and the belief sentence the corpus records; the respondent items
    beside the plan row, the B2B link on its own; and the brief
    paragraph beside the standings table. A judgement here would look like evidence and would be
    similarity to one hand-written example (judgement call 10); the person who knows the market
    reads it instead.
    """
    named_host = host_name(host)
    parts = [f"<!doctype html><meta charset='utf-8'><title>Register on {_esc(named_host)} — "
             f"{_esc(run_dir.name)}</title><style>" + _CSS + _REGISTER_CSS + "</style><main>"]
    parts.append(f"<h1>Register — {_esc(named_host)}</h1>"
                 f"<p class='small'>{_esc(run_dir.name)} · every word on this page was written "
                 f"by {_esc(named_host)}"
                 + (f", <code>{_esc(cli_version)}</code>" if cli_version else "")
                 + (f", model <code>{_esc(model)}</code>" if model
                    else ", model not reported by the CLI")
                 + "</p>")
    parts.append("<div class='banner note'><b>Nothing on this page is scored, and nothing on it "
                 "contributes to the run's verdict.</b> It exists so a person who knows the market "
                 "can read what a founder and a stranger there would actually have been asked — "
                 "whether the words are the ones people use, whether the units are the ones they "
                 "answer in, and whether an option list quietly leads. Design §3.8 says this "
                 "cannot be checked by code; a person reads it and the reading is recorded with "
                 "the run.</div>")
    for market_key, entries in (entries_by_market or {}).items():
        parts.append(f"<div class='market'><b>{_esc(market_key)}</b></div>")
        for entry_id, block in entries.items():
            parts.append(f"<h2>{_esc(entry_id)}</h2><p class='small'>{_esc(block.get('title'))}"
                         "</p>")
            parts.append(_redrawn_html(block.get("redraws") or []))
            parts.append(_interpretations_html(block.get("interpretations") or []))
            parts.append(_calibration_html(block.get("calibration") or []))
            parts.append(_respondent_html(block.get("respondent") or [],
                                          block.get("b2b") or []))
    for market_key, entries in (paragraphs or {}).items():
        parts.append(f"<div class='market'><b>{_esc(market_key)}</b> — what this says</div>")
        for entry_id, block in entries.items():
            verdicts = " · ".join(f"{v} {verdict}"
                                  for v, verdict in (block.get("verdicts") or {}).items())
            parts.append(f"<h3>{_esc(entry_id)}</h3>"
                         f"<p class='small'>{_esc(block.get('title'))} — {_esc(verdicts)}</p>")
            if block.get("paragraph"):
                parts.append("<div class='pair'><div><div class='side'>the model's own "
                             "paragraph</div><p>" + _esc(block["paragraph"]) + "</p></div>"
                             "<div><div class='side'>this entry's standings, for reference "
                             "only</div>" + _standings_html(block.get("standings") or {},
                                                            block.get("vector_verdicts") or {})
                             + "</div></div>")
            else:
                parts.append("<p class='small'>no paragraph was produced for this entry</p>")
    parts.append("</main>")
    path = run_dir / filename
    path.write_text("".join(parts), encoding="utf-8")
    return path


def _redrawn_html(rows: list) -> str:
    """Raw -> accepted (call 41): the first draft the aggregate refused, the rule's own words, and
    whether the redraw below it was taken. Words only, no score."""
    if not rows:
        return ""
    out = ["<h3>Redrawn after a rule refusal</h3>"]
    for row in rows:
        first = row.get("first_refusal") or {}
        after = ("the redraw was accepted, and it is what this page shows" if row.get("accepted")
                 else "the redraw was refused too, so this page shows the first draft")
        out.append(f"<p><b>{_esc(row.get('case_id'))}</b> — refused "
                   f"{_esc(first.get('rule'))}: {_esc(first.get('message'))}; {_esc(after)}.</p>"
                   "<div class='pair'><div><div class='side'>raw (the first draft)</div><pre>"
                   f"{_esc(json.dumps(row.get('raw'), indent=2, ensure_ascii=False))}</pre></div>"
                   "<div><div class='side'>redrawn</div><pre>"
                   f"{_esc(json.dumps(row.get('redrawn'), indent=2, ensure_ascii=False))}</pre>"
                   "</div></div>")
    return "".join(out)


def _interpretations_html(rows: list) -> str:
    if not rows:
        return ""
    out = ["<h3>The three interpretations</h3>"]
    for row in rows:
        verdict = row.get("aggregate") or "not shown to the aggregate"
        out.append(f"<p><b>{_esc(row.get('screen'))}</b> — {_esc(verdict)}</p>"
                   f"<pre>{_esc(json.dumps(row.get('result'), indent=2, ensure_ascii=False))}"
                   "</pre>")
    return "".join(out)


def _calibration_html(rows: list) -> str:
    if not rows:
        return ""
    out = ["<h3>Calibration questions, in registry order</h3>"]
    for row in rows:
        out.append("<div class='pair'><div><div class='side'>written by the model · "
                   f"{_esc(row.get('key'))}</div><p>{_esc(row.get('question') or '— not written')}"
                   "</p>")
        if row.get("event"):
            out.append(f"<p class='small'>event (code frames it): {_esc(row.get('event'))}</p>")
        options = row.get("options") or []
        if options:
            out.append("<ul>" + "".join(
                f"<li>{_esc(o.get('label'))} <span class='small'>({_esc(o.get('normalized'))}; "
                f"{_esc(o.get('belief_phrase'))})</span></li>" for o in options) + "</ul>")
        out.append("</div><div><div class='side'>the registry's own question, and the founder's "
                   "answer</div>"
                   f"<p>{_esc(row.get('founder_question') or '— the registry has none')}</p>"
                   f"<p class='small'>chosen: {_esc(row.get('belief_phrase') or 'not sure')}</p>"
                   f"<p class='small'>belief: {_esc(row.get('belief_sentence'))}</p></div></div>")
    return "".join(out)


def _respondent_html(parts_rows: list, b2b_rows: list) -> str:
    if not parts_rows and not b2b_rows:
        return ""
    out = ["<h3>Respondent items, beside the plan</h3>"]

    def items(rows):
        for row in rows:
            out.append(f"<p><b>{_esc(row.get('key'))}</b> · part {_esc(row.get('part'))} · "
                       f"{_esc(row.get('control'))} · {_esc(', '.join(row.get('codes') or []))}"
                       f"</p><p>{_esc(row.get('question') or '— not written')}</p>")
            options = row.get("options") or []
            if options:
                out.append("<ul>" + "".join(
                    f"<li>{_esc(o.get('label') if isinstance(o, dict) else o)}</li>"
                    for o in options) + "</ul>")

    items([r for r in parts_rows if r.get("part") == 1])
    items([r for r in parts_rows if r.get("part") != 1])
    if b2b_rows:
        out.append("<h3>The decision-maker's link (COMMERCIAL_B2B)</h3>")
        items(b2b_rows)
    return "".join(out)


def _standings_html(standings: dict, verdicts: dict) -> str:
    if not standings:
        return "<p class='small'>this entry records no standings</p>"
    rows = []
    for vector, verdict in verdicts.items():
        rows.append(f"<tr><th colspan='5'>{_esc(vector)} — {_esc(verdict.get('verdict'))}, "
                    f"deciding {_esc(verdict.get('deciding'))}</th></tr>")
        for key, v in standings.items():
            if not key.startswith(vector.lower() + "."):
                continue
            counts = v.get("optionCounts") or v.get("median") or v.get("proportion")
            rows.append(f"<tr><td>{_esc(key)}</td><td>{_esc(v.get('status'))}</td>"
                        f"<td>{_esc(v.get('drift'))}</td><td>{_esc(v.get('n'))}</td>"
                        f"<td>{_esc(counts)}</td></tr>")
    return ("<table><tr><th>dimension</th><th>status</th><th>drift</th><th>n</th>"
            f"<th>median / counts</th></tr>{''.join(rows)}</table>")


def _market_key(entry) -> str:
    market = entry.market or {}
    key = " · ".join(str(part) for part in
                     (market.get("country"), market.get("region"), market.get("language")) if part)
    return key or "no market named"


def paragraph_blocks(corpus, brief_scores: list) -> dict:
    """Every BRIEF paragraph, grouped by market beside its entry's own standings (judgement call
    17). The **first** run of each case: the register is read once per instruction."""
    first = {}
    for score in brief_scores or []:
        first.setdefault(score.entry_id, score)
    grouped = {}
    for entry in corpus.entries:
        score = first.get(entry.id)
        if score is None:
            continue
        verdicts = (entry.expected or {}).get("vector_verdicts") or {}
        grouped.setdefault(_market_key(entry), {})[entry.id] = {
            "title": entry.title,
            "paragraph": score.paragraph,
            "verdicts": {v: (verdicts.get(v) or {}).get("verdict") for v in verdicts},
            "vector_verdicts": verdicts,
            "standings": (entry.expected or {}).get("standings") or {},
        }
    return grouped


def register_blocks(corpus, produced: dict, registry=None, aggregate: dict | None = None,
                    *, redraws=()) -> dict:
    """Groups every produced answer by market and entry, beside what the corpus and the registry
    say (screen-shapes §7). `produced` is `{entry_id: {case kind and subject: result}}` -- the
    first run of each case -- as `run.py` collects it; `aggregate` is `fold_in`'s `by_case`, so an
    interpretation can be marked accepted or refused by rule id and nothing else.

    **No score, no tick, no cross** (judgement call 10).
    """
    aggregate = aggregate or {}
    grouped = {}
    for entry in corpus.entries:
        mine = produced.get(entry.id)
        if not mine:
            continue
        reg = registry if registry is not None else entry.registry
        shown_ids = {case_id for case_id, _result in mine.values()}
        block = {"title": entry.title, "interpretations": [], "calibration": [],
                 "respondent": [], "b2b": [],
                 "redraws": [r for r in redraws or () if r.get("case_id") in shown_ids]}
        for screen in ("CONTEXT_INTERPRET", "PROBLEM_INTERPRET", "SOLUTION_MECHANISM"):
            if screen not in mine:
                continue
            case_id, result = mine[screen]
            verdict = aggregate.get(case_id)
            if verdict is None:
                said = None
            elif verdict.get("accepted"):
                said = "accepted"
            else:
                refusal = verdict.get("refusal") or {}
                said = f"refused ({refusal.get('rule') or refusal.get('kind')})"
                again = aggregate.get(f"{case_id}#redraw")
                if again is not None:
                    second = again.get("refusal") or {}
                    said += (", redrawn: accepted" if again.get("accepted") else
                             f", redrawn: refused ({second.get('rule') or second.get('kind')})")
            block["interpretations"].append({"screen": screen, "result": result,
                                             "aggregate": said})
        produced_questions = {}
        for vector in ("PROBLEM", "SOLUTION", "COMMERCIAL"):
            _case_id, result = mine.get(f"CALIBRATION_{vector}", (None, None))
            for q in (result or {}).get("questions") or []:
                if isinstance(q, dict) and q.get("key"):
                    produced_questions.setdefault(q["key"], q)
        if reg is not None and any(k.startswith("CALIBRATION_") for k in mine):
            for d in reg.calibrated(entry.b2b()):                    # call 47
                q = produced_questions.get(d.key) or {}
                calibration = entry.founder_calibration.get(d.key) or {}
                block["calibration"].append({
                    "key": d.key, "question": q.get("question"), "event": q.get("event"),
                    "options": q.get("options"),
                    "founder_question": (d.lullaby or {}).get("founder_question")
                    if entry.id == "03-lullaby" else None,
                    "belief_phrase": calibration.get("belief_phrase"),
                    "belief_sentence": calibration.get("belief_sentence")})
        for label in ("PART1", "PART2", "PART3", "B2B"):
            _case_id, result = mine.get(f"RESPONDENT_{label}", (None, None))
            if not isinstance(result, dict):
                continue
            part = {"PART1": 1, "PART2": 2, "PART3": 3, "B2B": 3}[label]
            rows = []
            for item in result.get("items") or []:
                if not isinstance(item, dict):
                    continue
                plan_row = (entry.respondent_questions or {}).get(item.get("key")) or {}
                rows.append({"key": item.get("key"), "part": part,
                             "control": plan_row.get("control"), "codes": plan_row.get("codes"),
                             "question": item.get("question") or (
                                 f"(code frames the event) {item['event']}"
                                 if item.get("event") else None),
                             "options": item.get("options")})
            if label == "B2B":
                block["b2b"] = rows
            else:
                block["respondent"].extend(rows)
        grouped.setdefault(_market_key(entry), {})[entry.id] = block
    return grouped
