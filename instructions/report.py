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


def start_bundle(config, *, baseline: bool) -> Path:
    slug = "instructions-baseline" if baseline else "instructions"
    run_dir = new_run_dir(slug)
    write_versions(run_dir, config)
    return run_dir


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


def write_case(run_dir: Path, case, answer, diff: dict) -> None:
    """`prompt.txt`, `envelope.json`, `diff.json` -- the three files a finding is quoted from."""
    directory = case_dir(run_dir, case)
    (directory / "prompt.txt").write_text(case.prompt, encoding="utf-8")
    (directory / "envelope.json").write_text(json.dumps({
        "case_id": case.case_id,
        "screen": case.screen,
        "outcome": answer.outcome,
        "schema_valid": answer.schema_valid,
        "schema_error": answer.schema_error,
        "recovery_pass": answer.recovery_pass,
        "num_turns": answer.num_turns,
        "total_cost_usd": answer.total_cost_usd,
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


def _mark_row(name: str, result: dict, fmt=_pct) -> str:
    cls = "met" if result["met"] else "missed"
    word = "met" if result["met"] else "NOT met"
    return (f"<tr><td>{_esc(name)}</td><td>{fmt(result['value'])}</td>"
            f"<td>{result['mark']}</td><td class='mark {cls}'>{word}</td></tr>")


def render_report(run_dir: Path, *, verdict: dict, scorecard: dict, versions: dict) -> Path:
    t = scorecard["totals"]
    judged = verdict["marks"]
    baseline = verdict.get("baseline")

    parts = ["<!doctype html><meta charset='utf-8'><title>Instruction eval — "
             f"{_esc(run_dir.name)}</title><style>{_CSS}</style><main>"]
    parts.append(f"<h1>The instruction eval</h1><p class='small'>{_esc(run_dir.name)}</p>")

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
    parts.append(_mark_row("refusals (rule)", judged["refusals"],
                           fmt=lambda v: "not measured" if v is None else str(v)))
    parts.append("</table>")

    model = scorecard.get("model") or {}
    parts.append(
        "<p><b>Judged under:</b> "
        f"<code>{_esc(model.get('claude_version') or 'unknown claude CLI')}</code>"
        + (f", model <code>{_esc(model.get('reported_model'))}</code>"
           if model.get("reported_model") else "")
        + ". keel-runtime sends no <code>--model</code> and this repo does not add one, so "
          "<b>these marks are comparable only within this model</b>.</p>")
    parts.append(f"<p class='small'>MARKS_VERSION {marks_mod.MARKS_VERSION} · N = "
                 f"{_esc(verdict.get('n_runs'))} · {_esc(verdict.get('cases'))} cases · "
                 f"{_esc(verdict.get('errored'))} errored · "
                 f"${verdict.get('total_cost_usd') or 0:.2f} · "
                 f"{verdict.get('duration_s', 0):.0f}s</p>")
    parts.append(f"<p class='small'>Executor caps, production's own and not overridden here: "
                 f"wall clock <b>{_esc(model.get('job_timeout_seconds'))}s</b> · max turns "
                 f"{_esc(model.get('job_max_turns'))} · budget "
                 f"${_esc(model.get('job_budget_usd'))}. An eval more patient than production "
                 f"would report an instruction as working that a founder watches fail. "
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

def render_register(run_dir: Path, *, entries_by_market: dict) -> Path:
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
    parts = ["<!doctype html><meta charset='utf-8'><title>Register — "
             f"{_esc(run_dir.name)}</title><style>" + _CSS + """
.market{background:#eee9df;padding:10px 14px;border-radius:6px;margin:26px 0 10px}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:10px 0}
.pair>div{border:1px solid #e3ded6;border-radius:6px;padding:10px;background:#fff}
.side{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:#8a8378;margin-bottom:4px}
ul{margin:4px 0 0 18px;padding:0}
</style><main>"]
    parts.append(f"<h1>Register</h1><p class='small'>{_esc(run_dir.name)}</p>")
    parts.append("<div class='banner note'><b>Nothing on this page is scored, and nothing on it "
                 "contributes to the run's verdict.</b> It exists so a person who knows the market "
                 "can read what a stranger there would actually have been asked — whether the "
                 "words are the ones people use, whether the units are the ones they answer in, "
                 "and whether an option list quietly leads to the answer the founder hopes for. "
                 "Design §3.8 says this cannot be checked by code; §10 step 4 says a person reads "
                 "it and the reading is recorded with the run. That reading is the only thing that "
                 "closes SC-012, and no metric here pretends to stand in for it.</div>")

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
    path = run_dir / "register.html"
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
