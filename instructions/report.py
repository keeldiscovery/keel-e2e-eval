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
        "duration_s": round(answer.duration_s, 3),
        "error": answer.error,
        "result": answer.result,
        "questions": answer.questions,
        "envelope": answer.envelope,
    }, indent=2, default=str), encoding="utf-8")
    (directory / "diff.json").write_text(json.dumps(diff, indent=2, default=str),
                                         encoding="utf-8")


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
.mark.met{color:#1c5220;font-weight:600}.mark.missed{color:#a3271b;font-weight:600}
.tick{color:#1c5220}.cross{color:#a3271b}.na{color:#8a8378}
code,pre{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px}
pre{background:#f1ede6;padding:10px;overflow-x:auto;white-space:pre-wrap;word-break:break-word}
details{margin:6px 0}summary{cursor:pointer;font-weight:600}
.small{font-size:12px;color:#6b6459}
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


def _mark_row(name: str, result: dict, fmt=_pct) -> str:
    cls = "met" if result["met"] else "missed"
    word = "met" if result["met"] else "NOT met"
    return (f"<tr><td>{_esc(name)}</td><td>{fmt(result['value'])}</td>"
            f"<td>{result['mark']}</td><td class='mark {cls}'>{word}</td></tr>")


# The host's own name for itself, for a page a person reads (spec 014 FR-006).
HOST_NAMES = {"claude": "Claude Code", "copilot": "GitHub Copilot", "codex": "Codex"}


def host_name(host) -> str:
    return HOST_NAMES.get(host, str(host or "unknown host"))


def render_report(run_dir: Path, *, verdict: dict, scorecard: dict, versions: dict,
                  host: str = "claude") -> Path:
    t = scorecard["totals"]
    judged = verdict["marks"]
    baseline = verdict.get("baseline")
    named_host = host_name(host)

    parts = [f"<!doctype html><meta charset='utf-8'><title>Instruction eval on {_esc(named_host)}"
             f" — {_esc(run_dir.name)}</title><style>{_CSS}</style><main>"]
    parts.append(f"<h1>The instruction eval on {_esc(named_host)}</h1>"
                 f"<p class='small'>{_esc(run_dir.name)}</p>")
    parts.append(
        f"<div class='banner note'><b>This run was answered by {_esc(named_host)}</b> "
        f"(<code>{_esc((scorecard.get('model') or {}).get('cli_version') or 'version unknown')}"
        "</code>). keel-cloud <code>canon/designs/keel-skill-design.md</code> §5.5: <b>two runs "
        "under different hosts are different measurements and must never be averaged.</b> Read "
        "this page against the same host's own previous run, never against the other's.</div>")

    if baseline:
        parts.append("<div class='banner note'><b>This is the baseline.</b> It measures "
                     "keel-cloud's instructions <em>before</em> spec 029 rewrote them. A red "
                     "result is the expected one: today's assumption screens emit "
                     "<code>question: {ask, disconfirming}</code> and today's reading screen emits "
                     "<code>claimType</code> and <code>stance</code>, and neither fits the "
                     "contract spec 028 shipped. A <em>green</em> baseline would mean this harness "
                     "was measuring something other than the instruction.</div>")

    cls = "pass" if judged.get("passed") else "fail"
    word = "PASSED" if judged.get("passed") else "FAILED"
    parts.append(f"<div class='banner {cls}'>{word}</div>")

    parts.append("<table><tr><th>Mark</th><th>This run</th><th>Required</th><th></th></tr>")
    parts.append(_mark_row("anchoring accuracy", judged["anchoring_accuracy"]))
    parts.append(_mark_row("golden-belief recall", judged["golden_belief_recall"]))
    parts.append(_mark_row("shape refusals", judged.get("shape_refusals", {"value": None, "mark": 0, "met": False}),
                           lambda v: "—" if v is None else str(v)))
    parts.append(_mark_row("refusals (rule), as a rate of answers judged", judged["refusals"],
                           fmt=lambda v: "not measured" if v is None else str(v)))
    parts.append(_mark_row("BRIEF paragraphs (all four marks)", judged["brief_paragraphs"],
                           fmt=lambda v: "not measured" if v is None else _pct(v)))
    parts.append("</table>")

    model = scorecard.get("model") or {}
    per_class = model.get("models_used")
    if per_class:
        # keel-cloud model-routing-design.md §7: the pins went through the job's own `model`
        # key, one per class -- the run the cloud's table actually claims.
        pinned = (", pinned per job class through the job's own <code>model</code> key: "
                  + " · ".join(f"{_esc(job_class)} <code>{_esc(name)}</code>" if name
                               else f"{_esc(job_class)} <b>the CLI's default</b>"
                               for job_class, name in per_class.items())
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
                 f"{verdict.get('duration_s', 0):.0f}s</p>")
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
                 f"{caps}. An eval more patient than production would "
                 f"report an instruction as working that a founder watches fail. "
                 f"Judge: <b>{_esc(model.get('judge') or 'on')}</b>, "
                 f"{_esc(t.get('judge_calls', 0))} calls; it broke "
                 f"{_esc(t.get('judged_pairs', 0))} ties and let "
                 f"{_esc(t.get('judged_candidacy_pairs', 0))} pairs exist that the structure "
                 f"rejected — <b>{_pct(t.get('judged_any_fraction'))}</b> of matched pairs "
                 f"involved a model's opinion. Discount the recall by exactly that much.</p>")

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
                 "Whether an anchor sounds like a supply yard in Texas or a builder's merchant in "
                 "London is design §3.8's <em>cannot be checked by code</em>; §10 step 4 says what "
                 "is done instead — a person who knows the market reads the produced anchors and "
                 "option lists, and that reading is recorded with the run.<br>"
                 "<b>Whether an option list leads is not scored either.</b> It is design §4's most "
                 "expensive authoring mistake and there is no golden data for it.<br>"
                 "<b>Wording is free.</b> Headings and statements contribute a tie-break to "
                 "alignment and nothing to any score.<br>"
                 "<b>No longer on this list:</b> the §8.3 phrase mapping. keel-cloud spec 029 put "
                 "<code>founderPhrase</code> on the wire, so the phrase is scored beside the band."
                 "</div>")

    # ------------------------------------------------------------------------------- the reading
    parts.append("<h2>The reading</h2>")
    parts.append(f"<p>accuracy <b>{_pct(t['anchoring_accuracy'])}</b> over "
                 f"{t['anchors_answered']} answered of {t['anchors_given']} given · "
                 f"<b>GUESSED precision</b> {_pct(t['guessed_precision'])} · "
                 f"<b>GUESSED recall</b> {_pct(t['guessed_recall'])} · "
                 f"{t['reading_missing_ids']} anchors never answered · "
                 f"{t['reading_extra_ids']} anchor ids invented</p>")
    parts.append("<p class='small'>Read recall first. Most anchors in this corpus are anchored, so "
                 "a reader that answered ANCHORED to everything scores high on accuracy and has "
                 "failed at the one judgement it exists to make.</p>")
    c = t["confusion"]
    parts.append("<table><tr><th></th><th>called ANCHORED</th><th>called GUESSED</th></tr>"
                 f"<tr><th>was ANCHORED</th><td>{c['aa']}</td><td>{c['ag']}</td></tr>"
                 f"<tr><th>was GUESSED</th><td>{c['ga']}</td><td>{c['gg']}</td></tr></table>")

    disagreements = [row for case in scorecard["reading"] for row in case["per_anchor"]
                     if not row["agree"]]
    parts.append(f"<h3>Disagreements ({len(disagreements)})</h3>")
    if disagreements:
        parts.append("<table><tr><th>Case</th><th>Anchor</th><th>Golden</th><th>Model</th></tr>")
        for case in scorecard["reading"]:
            for row in case["per_anchor"]:
                if row["agree"]:
                    continue
                parts.append(f"<tr><td>{_esc(case['case_id'])}</td><td>{_esc(row['anchor_id'])}</td>"
                             f"<td>{_esc(row['golden'])}</td>"
                             f"<td>{_esc(row['produced'] or '— never answered')}</td></tr>")
        parts.append("</table>")

    failed_reading = [case for case in scorecard["reading"] if case.get("failed")]
    if failed_reading:
        parts.append(f"<h3>Reading cases that produced nothing ({len(failed_reading)})</h3><table>"
                     "<tr><th>Case</th><th>Why</th></tr>")
        for case in failed_reading:
            parts.append(f"<tr><td>{_esc(case['case_id'])}</td>"
                         f"<td><code>{_esc(case['failed'])}</code></td></tr>")
        parts.append("</table>")

    # --------------------------------------------------------------------------- the assumptions
    parts.append("<h2>The assumptions</h2>")
    parts.append(f"<p>golden-belief recall <b>{_pct(t['golden_belief_recall'])}</b> "
                 f"({t['matched_beliefs']} of {t['golden_beliefs']}) · "
                 f"{t['extra_beliefs']} extra beliefs · "
                 f"{t['needs_input_cases']} NEEDS_INPUT cases · "
                 f"{_pct(t['judged_fraction'])} of matches decided by a model</p>")
    parts.append("<table><tr><th>Field</th><th>Exact match</th><th>Agreed / applicable</th></tr>")
    for name, rate in t["exact_match"].items():
        counts = t["exact_match_counts"][name]
        parts.append(f"<tr><td><code>{_esc(name)}</code></td><td>{_pct(rate)}</td>"
                     f"<td>{counts['agreed']} / {counts['applicable']}</td></tr>")
    parts.append("</table>")

    pb = t["phrase_band"]
    parts.append("<h3>The phrase beside the band</h3><table>"
                 "<tr><th>Phrase</th><th>Band</th><th>Pairs</th><th>What it means</th></tr>"
                 f"<tr><td>agrees</td><td>agrees</td><td>{pb['phrase_band']}</td>"
                 "<td>read the founder and applied the §8.3 table</td></tr>"
                 f"<tr><td>agrees</td><td>differs</td><td>{pb['phrase_only']}</td>"
                 "<td>read the founder, got the arithmetic wrong</td></tr>"
                 f"<tr><td>differs</td><td>agrees</td><td>{pb['band_only']}</td>"
                 "<td>right band from a phrase the founder never used — unstable</td></tr>"
                 f"<tr><td>differs</td><td>differs</td><td>{pb['neither']}</td>"
                 "<td>did not read the founder's size at all</td></tr></table>")

    parts.append("<h3>Three ways of being wrong, three lines</h3><table>"
                 "<tr><th>Line</th><th>Count</th><th>What it means</th></tr>"
                 f"<tr><td>schema-invalid</td><td>{t['schema_invalid']}</td>"
                 "<td>keel-runtime's own validator refused it, or the CLI's own "
                 "<code>--json-schema</code> was never satisfied in six turns; keel-cloud never "
                 "saw it</td></tr>"
                 f"<tr><td>shape refusals</td><td>{t['shape_refusals']}</td>"
                 "<td>it fit no contract the aggregate could read</td></tr>"
                 f"<tr><td>rule refusals</td><td>"
                 f"{sum(t['refusals_by_rule'].values()) if t.get('refusals_measured') else 'not measured'}</td>"
                 f"<td>the aggregate read it and refused it: "
                 f"{_esc(json.dumps(t['refusals_by_rule']))}</td></tr></table>")

    parts.append("<h3>Per case</h3><table><tr><th>Case</th><th>Recall</th><th>Matched</th>"
                 "<th>Missing</th><th>Extra</th><th>Outcome</th><th>existing_roles supplied</th></tr>")
    for case in scorecard["assumptions"]:
        outcome = ("NEEDS_INPUT" if case["needs_input"] else
                   case.get("failed") or "COMPLETED")
        parts.append(
            f"<tr><td>{_esc(case['case_id'])}</td><td>{_pct(case['golden_belief_recall'])}</td>"
            f"<td>{case['matched']} / {case['golden_total']}</td>"
            f"<td>{_esc(', '.join(case['missing']) or '—')}</td>"
            f"<td>{case['extra_beliefs']}</td><td><code>{_esc(outcome)}</code></td>"
            f"<td class='small'>{_esc(', '.join(case['existing_roles']) or '—')}</td></tr>")
    parts.append("</table>")

    needs_input = [c for c in scorecard["assumptions"] if c["needs_input"]]
    if needs_input:
        parts.append(f"<h3>NEEDS_INPUT outcomes ({len(needs_input)})</h3>"
                     "<p class='small'>An assumption screen's only legitimate ask is a missing "
                     "statement (design decision 14), and this harness always supplies one. Each "
                     "of these is a failed case, shown so the failure can be read rather than only "
                     "counted.</p><table><tr><th>Case</th><th>What it asked</th></tr>")
        for case in needs_input:
            asked = "; ".join(str(q.get("question")) for q in (case["needs_input_questions"] or [])
                              if isinstance(q, dict))
            parts.append(f"<tr><td>{_esc(case['case_id'])}</td><td>{_esc(asked)}</td></tr>")
        parts.append("</table>")

    # ---------------------------------------------------------------------------------- brief
    if t.get("brief_measured"):
        parts.append("<h2>What this says (the BRIEF screen)</h2>")
        parts.append(f"<p><b>{_pct(t['brief_paragraphs'])}</b> of {t['brief_cases']} paragraphs "
                     f"met all four marks · {t['brief_needs_input']} asked a question on a screen "
                     "with nobody to ask.</p>")
        parts.append("<div class='banner note'><b>The context this subject sends is not, in one "
                     "field, the context production sends.</b> keel-cloud renders "
                     "<code>median_reads</code> with <code>Measure.say</code>, which rounds and "
                     "re-units (<em>45 minutes</em>, <em>£7.50</em>); this repo does not own that "
                     "arithmetic and refuses to keep a copy of it, so the middle answer is handed "
                     "over in the corpus's own unit (<em>0.75 hours</em>) and the mark checks "
                     "<code>brief.md</code>'s own rule against that string -- <em>you quote it "
                     "exactly, never convert</em>. <code>claims[].drift</code>, "
                     "<code>below</code> and <code>above</code> are written and left "
                     "<code>null</code> for the same reason: the corpus does not carry them and "
                     "<code>Project.driftOfStage</code> is keel-cloud's.<br>"
                     "<b>And the paragraph is rendered as well as marked.</b> Almost everything "
                     "about a good paragraph is wording, which design §3.8 says cannot be checked "
                     "by code -- so every paragraph is on <a href='register.html'>register.html</a> "
                     "beside its entry's own standings, unscored, for a person to read.</div>")
        by_mark = t.get("brief_by_mark") or {}
        parts.append("<table><tr><th>Mark</th><th>Met</th><th>What it checks</th></tr>")
        for name, what in (
                ("shape", "one paragraph, no heading, bullet, stage label or link, ≤ 1200"),
                ("coverage", "each claim's verdict named in the design's words; the deciding "
                             "line's number quoted; no invented <em>N of M</em>"),
                ("register", "second person, and no money the context never carried"),
                ("source_material", "no id, field name or enum name; never NEEDS_INPUT")):
            row = by_mark.get(name) or {}
            parts.append(f"<tr><td><code>{_esc(name)}</code></td>"
                         f"<td>{row.get('met', 0)} / {row.get('of', 0)}</td><td>{what}</td></tr>")
        parts.append("</table>")

        parts.append("<h3>Per case</h3><table><tr><th>Case</th><th>Length</th><th>shape</th>"
                     "<th>coverage</th><th>register</th><th>source</th></tr>")
        for case in scorecard.get("brief") or []:
            cells = "".join(
                f"<td class='{'tick' if case['marks'].get(n) is True else 'cross'}'>"
                f"{'✓' if case['marks'].get(n) is True else '✗'}</td>"
                for n in ("shape", "coverage", "register", "source_material"))
            parts.append(f"<tr><td>{_esc(case['case_id'])}</td><td>{case['length']}</td>{cells}</tr>")
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
    for title, block in (("golden-belief recall", scorecard["spread"]["recall"]),
                         ("anchoring accuracy", scorecard["spread"]["anchoring"])):
        if not block:
            continue
        parts.append(f"<h3>{title}</h3><table><tr><th>Case</th><th>Runs</th><th>min</th>"
                     "<th>max</th></tr>")
        for key, row in sorted(block.items()):
            runs = ", ".join(_pct(v) for v in row["runs"])
            parts.append(f"<tr><td>{_esc(key)}</td><td>{runs}</td><td>{_pct(row['min'])}</td>"
                         f"<td>{_pct(row['max'])}</td></tr>")
        parts.append("</table>")

    # --------------------------------------------------------------------------------- prompts
    parts.append("<h2>The prompts</h2>")
    for entry in scorecard.get("prompts") or []:
        parts.append(f"<details><summary>{_esc(entry['case_id'])} — {_esc(entry['screen'])}"
                     "</summary><pre>" + _esc(entry["prompt"]) + "</pre></details>")

    parts.append("<h2><a href='register.html'>register.html</a></h2><p>Every produced anchor "
                 "prompt and option list, grouped by market, with <b>no score, no tick and no "
                 "cross</b> — it exists so a person who knows that market can read what a stranger "
                 "there would have been asked, and their reading is recorded with this run "
                 "(SC-012). <b>Nothing on that page contributes to the verdict above.</b></p>")

    parts.append("</main>")
    path = run_dir / "report.html"
    path.write_text("".join(parts), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------------- register.html

def render_register(run_dir: Path, *, entries_by_market: dict,
                    paragraphs: dict | None = None,
                    host: str = "claude", cli_version: str | None = None,
                    model: str | None = None,
                    filename: str = "register.html") -> Path:
    """The one artefact in this bundle with no number in it (spec 009 FR-019, T027).

    Whether an anchor sounds like a supply yard in Texas or a builder's merchant in London is
    design §3.8's *cannot be checked by code*, and §10 step 4 says what is done instead: a person
    who knows the market reads the produced anchors and option lists, and **that reading is
    recorded with the run**. So this page renders them, grouped by market, with the corpus's own
    anchor for the same stage beside each for reference — and no score, no tick, no cross.

    A metric here would look like evidence and would in fact be similarity to one hand-written
    example (judgement call 10). Whether an option list *leads* — design §4's most expensive
    authoring mistake, the one that collapses a dropdown's recall to 1 % — is the other thing this
    page exists for and the other thing nothing scores.
    """
    named_host = host_name(host)
    parts = [f"<!doctype html><meta charset='utf-8'><title>Register on {_esc(named_host)} — "
             f"{_esc(run_dir.name)}</title><style>" + _CSS + """
.market{background:#eee9df;padding:10px 14px;border-radius:6px;margin:26px 0 10px}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:10px 0}
.pair>div{border:1px solid #e3ded6;border-radius:6px;padding:10px;background:#fff}
.side{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:#8a8378;margin-bottom:4px}
ul{margin:4px 0 0 18px;padding:0}
</style><main>"""]
    # FR-006: the page a person reads with their own judgement must say **whose words these
    # are** before they read a single one. Register is exactly the thing that differs between two
    # models, and a reader comparing Copilot's prose to a memory of Claude's without being told
    # would be the most expensive quiet mistake this bundle could make.
    parts.append(f"<h1>Register — {_esc(named_host)}</h1>"
                 f"<p class='small'>{_esc(run_dir.name)} · every word on this page was written "
                 f"by {_esc(named_host)}"
                 + (f", <code>{_esc(cli_version)}</code>" if cli_version else "")
                 + (f", model <code>{_esc(model)}</code>" if model
                    else ", model not reported by the CLI")
                 + "</p>")
    parts.append("<div class='banner note'><b>Nothing on this page is scored, and nothing on it "
                 "contributes to the run's verdict.</b> It exists so a person who knows the market "
                 "can read what a stranger there would actually have been asked — whether the "
                 "words are the ones people use, whether the units are the ones they answer in, "
                 "and whether an option list quietly leads to the answer the founder hopes for. "
                 "Design §3.8 says this cannot be checked by code; §10 step 4 says a person reads "
                 "it and the reading is recorded with the run. That reading is the only thing that "
                 "closes SC-012, and no metric here pretends to stand in for it.</div>")

    if paragraphs:
        parts.append("<h2>What this says — the paragraphs, whole</h2>")
        parts.append("<div class='banner note'><b>One paragraph per entry, exactly as the model "
                     "wrote it, with that entry's own three verdicts beside it.</b> The four "
                     "marks on the report cover only what <code>brief.md</code> states as a rule; "
                     "whether this reads like someone who has read all three cards, in the "
                     "register of that market, is design §3.8's <em>cannot be checked by code</em> "
                     "— and a mark that narrow can be wrong about a paragraph that is right. "
                     "<b>Nothing here is scored.</b></div>")
        for market_key, entries in paragraphs.items():
            parts.append(f"<div class='market'><b>{_esc(market_key)}</b></div>")
            for entry_id, block in entries.items():
                verdicts = " · ".join(f"{stage} {verdict}"
                                      for stage, verdict in (block.get("stages") or {}).items())
                parts.append(f"<h3>{_esc(entry_id)}</h3>"
                             f"<p class='small'>{_esc(block.get('title'))} — {_esc(verdicts)}</p>")
                if block.get("paragraph"):
                    parts.append("<div class='pair'><div><div class='side'>the model's own "
                                 "paragraph</div><p>" + _esc(block["paragraph"]) + "</p>"
                                 + _phrasing_html(block.get("phrasing") or []) + "</div>"
                                 "<div><div class='side'>this entry's standings, for reference "
                                 "only</div>" + _standings_html(block.get("standings") or {})
                                 + "</div></div>")
                else:
                    parts.append("<p class='small'>no paragraph was produced for this entry</p>")

    for market_key, entries in entries_by_market.items():
        parts.append(f"<div class='market'><b>{_esc(market_key)}</b></div>")
        for entry_id, stages in entries.items():
            for stage, block in stages.items():
                parts.append(f"<h3>{_esc(entry_id)} · {_esc(stage)}</h3>")
                parts.append("<div class='pair'>")
                parts.append("<div><div class='side'>produced by the model</div>"
                             + _anchors_html(block.get("produced") or []) + "</div>")
                parts.append("<div><div class='side'>the corpus's own, for reference only</div>"
                             + _anchors_html(block.get("golden") or []) + "</div>")
                parts.append("</div>")
    parts.append("</main>")
    path = run_dir / filename
    path.write_text("".join(parts), encoding="utf-8")
    return path


def _anchors_html(anchors: list) -> str:
    if not anchors:
        return "<p class='small'>nothing produced for this stage</p>"
    out = []
    for anchor in anchors:
        out.append(f"<p><b>{_esc(anchor.get('id'))}</b> — {_esc(anchor.get('prompt'))}</p>")
        for selection in anchor.get("selections") or []:
            control = selection.get("control")
            out.append(f"<p class='small'>{_esc(selection.get('id'))} · {_esc(control)} — "
                       f"{_esc(selection.get('prompt'))}</p>")
            options = selection.get("options") or []
            if options:
                out.append("<ul>" + "".join(f"<li>{_esc(o)}</li>" for o in options) + "</ul>")
            escape = selection.get("escape") or []
            if escape:
                out.append("<p class='small'>escape: "
                           + _esc(", ".join(str(e) for e in escape)) + "</p>")
    return "".join(out)


def _phrasing_html(phrasing: list) -> str:
    """Judgement call 20: **observed, never marked.** `brief.md` licenses the paraphrase by
    example -- *"Write them into ordinary sentences: 'the problem is real'"* -- so whether the
    design's own verdict phrase literally appears is something a person reads off the paragraph
    above, not something a number stands in for. No tick, no cross; the word *carries* or *says it
    another way*, and the sentence is right there to judge."""
    if not phrasing:
        return ""
    rows = []
    for row in phrasing:
        if row.get("verdict") is None:
            rows.append(f"<li>{_esc(row.get('stage'))} — unapproved, no status to name</li>")
            continue
        how = ("carries the design's own phrase" if row.get("present")
               else "says it another way — read the sentence above")
        rows.append(f"<li>{_esc(row.get('stage'))} is {_esc(row.get('verdict'))} "
                    f"(<em>{_esc(row.get('phrase'))}</em>): {how}</li>")
    return ("<div class='side'>the four verdict words, observed and not scored</div><ul>"
            + "".join(rows) + "</ul>")


def _standings_html(standings: dict) -> str:
    if not standings:
        return "<p class='small'>this entry records no standings</p>"
    rows = "".join(
        f"<tr><td>{_esc(k)}</td><td>{_esc(v.get('verdict'))}</td><td>{_esc(v.get('drift'))}</td>"
        f"<td>{_esc(v.get('inside'))}/{_esc((v.get('inside') or 0) + (v.get('outside') or 0))}</td>"
        f"<td>{_esc(v.get('median', '—'))}</td></tr>" for k, v in standings.items())
    return ("<table><tr><th>line</th><th>verdict</th><th>drift</th><th>inside</th>"
            f"<th>median</th></tr>{rows}</table>")


def paragraph_blocks(corpus, brief_scores: list) -> dict:
    """Every BRIEF paragraph, grouped by market beside its entry's own standings (judgement call
    17). Keyed by entry and taking the **first** run of each case, exactly as the anchors are:
    the register is read once per instruction, not once per repetition."""
    first = {}
    for score in brief_scores or []:
        first.setdefault(score.entry_id, score)
    grouped = {}
    for entry in corpus.entries:
        score = first.get(entry.id)
        if score is None:
            continue
        market = entry.market or {}
        key = " · ".join(str(part) for part in
                         (market.get("country"), market.get("region"), market.get("language"))
                         if part)
        grouped.setdefault(key or "no market named", {})[entry.id] = {
            "title": entry.title,
            "paragraph": score.paragraph,
            "phrasing": score.phrasing,
            "stages": (entry.expected or {}).get("stages") or {},
            "standings": (entry.expected or {}).get("standings") or {},
        }
    return grouped


def register_blocks(corpus, produced_by_case: dict) -> dict:
    """Groups every produced questionnaire by market, entry and stage, beside the corpus's own."""
    grouped = {}
    for entry in corpus.entries:
        market = entry.market or {}
        key = " · ".join(str(part) for part in
                         (market.get("country"), market.get("region"), market.get("language"))
                         if part)
        for stage in ("PROBLEM", "SOLUTION", "COMMERCIAL"):
            produced = produced_by_case.get(f"{entry.id}/{stage}")
            if produced is None:
                continue
            grouped.setdefault(key or "no market named", {}) \
                   .setdefault(entry.id, {})[stage] = {
                       "produced": (produced.get("questionnaire") or {}).get("anchors") or [],
                       "golden": entry.anchors_for(stage),
                   }
    return grouped
