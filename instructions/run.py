"""`python -m instructions.run` -- the whole eval, and the dry run that costs nothing.

    --dry-run        print every prompt this run would send, and the case count and estimate;
                     call nothing, spend nothing
    --baseline       name the bundle `-instructions-baseline`, and say in the report that a red
                     result is the expected one
    -k SUBSTRING     only cases whose case id contains it (`-k 01-countly`, `-k reading`)
    -n N             runs per case (default 3)
    --marks FILE     an alternative marks file

**Read a prompt before spending anything.** The dry run exists for exactly that: an assumption
prompt and a reading prompt, in full, with `TASK`, `CONTRACT`, the `SOURCE MATERIAL` heading and
the nonce-fenced block. If the context keys look wrong, the fault is in `instructions/context.py`
or in keel-cloud's exporter, and it is far cheaper to find now than after a hundred calls.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from stack.config import REPO_ROOT, load_config

from . import contract as contract_mod
from . import corpus as corpus_mod
from . import instruction as instruction_mod
from . import judge as judge_mod
from . import marks as marks_mod
from . import prompts as prompts_mod
from . import report as report_mod
from . import runner as runner_mod
from . import score as score_mod
from . import validate as validate_mod

# Rough, and honest about being rough: the founder's own account pays, and the point of printing a
# number before the first call is that nobody is surprised by the size of the bill, not that the
# number is right to the cent.
COST_PER_CASE_ESTIMATE_USD = 0.06

SCREENS = list(contract_mod.SCREENS_ASSUMPTIONS.values()) + [contract_mod.SCREEN_READING]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="instructions.run", description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--baseline", action="store_true")
    parser.add_argument("-k", dest="filter", default=None)
    parser.add_argument("-n", dest="n_runs", type=int, default=3)
    parser.add_argument("--marks", default=None)
    parser.add_argument("--no-judge", action="store_true",
                        help="score with the structural matcher alone (MARKS_VERSION 1's rule)")
    args = parser.parse_args(argv)

    config = load_config()
    try:
        facts = runner_mod.preflight(config, dry_run=args.dry_run)
    except runner_mod.NotReady as reason:
        print(f"instruction eval cannot start: {reason}", file=sys.stderr)
        return 2

    corpus = corpus_mod.load(config.keel_cloud)
    executor_module, validator_module = prompts_mod.load_runtime(config.keel_runtime)

    if args.dry_run:
        return _dry_run(config, corpus, executor_module, args)

    with runner_mod.RunLock(REPO_ROOT / "runs"):
        return _real_run(config, corpus, executor_module, validator_module, facts, args)


# --------------------------------------------------------------------------------------- helpers

def _instructions_for(config, screens=SCREENS) -> dict:
    return {screen: instruction_mod.read(config.keel_cloud, screen) for screen in screens}


def _all_cases(corpus, exported, instructions, executor_module, args) -> list:
    cases = []
    for entry in corpus.entries:
        cases.extend(prompts_mod.build_cases(entry, exported, instructions, executor_module,
                                             n_runs=args.n_runs))
    if args.filter:
        needle = args.filter.lower()
        cases = [c for c in cases
                 if needle in c.case_id.lower()
                 or (needle == "reading" and c.kind == "READING")
                 or (needle == "assumptions" and c.kind == "ASSUMPTIONS")]
    return cases


def _dry_run(config, corpus, executor_module, args) -> int:
    """Everything a real run does, up to the point where it would cost money."""
    into = Path(REPO_ROOT) / "runs" / ".contracts-dry"
    exported = contract_mod.export(config.keel_cloud, into)
    instructions = _instructions_for(config)
    cases = _all_cases(corpus, exported, instructions, executor_module, args)

    print(f"contract exported from keel-cloud {exported.manifest.get('keel_cloud_commit')}"
          f"{' (dirty)' if exported.manifest.get('keel_cloud_dirty') else ''}")
    for screen in SCREENS:
        print(f"  {screen:<24} keys: {exported.keys_for(screen)}")
    print()

    shown = {"ASSUMPTIONS": False, "READING": False}
    for case in cases:
        if shown[case.kind]:
            continue
        shown[case.kind] = True
        print("=" * 100)
        print(f"{case.case_id}   ({case.screen})")
        print("=" * 100)
        print(case.prompt)
        print()

    assumptions = sum(1 for c in cases if c.kind == "ASSUMPTIONS")
    reading = sum(1 for c in cases if c.kind == "READING")
    print("-" * 100)
    print(f"{len(cases)} cases: {assumptions} assumption, {reading} reading, "
          f"N={args.n_runs} runs per case")
    print(f"rough estimate at ${COST_PER_CASE_ESTIMATE_USD:.2f} a case: "
          f"${len(cases) * COST_PER_CASE_ESTIMATE_USD:.2f} of the founder's own money")
    print("nothing was called and nothing was spent")
    return 0


def _real_run(config, corpus, executor_module, validator_module, facts, args) -> int:
    started = time.monotonic()
    run_dir = report_mod.start_bundle(config, baseline=args.baseline)
    print(f"run bundle: {run_dir}")

    exported = contract_mod.export(config.keel_cloud, run_dir / "contracts")
    report_mod.write_corpus_hashes(run_dir, corpus, when="before")
    instructions = _instructions_for(config)
    cases = _all_cases(corpus, exported, instructions, executor_module, args)
    marks = marks_mod.load(args.marks)

    # `ClaudeCodeExecutor` puts its per-job dirs at `<home>/jobs/<job_id>`, so the home is the run
    # directory itself and the bundle's `jobs/` is exactly what the run-bundle contract describes.
    # The wall clock is production's own default (keel-runtime `DEFAULT_JOB_TIMEOUT_SECONDS`) and
    # is deliberately not overridden: an eval more patient than production would report an
    # instruction as working that a founder watches fail.
    executor = executor_module.ClaudeCodeExecutor(home=run_dir)
    judge = judge_mod.NoJudge() if args.no_judge else judge_mod.Judge()
    people = {(e.id, p.person): p for e in corpus.entries for p in e.people()}

    reading_scores, assumption_scores, prompts, errored = [], [], [], 0
    schema_invalid = 0
    produced_sets = []
    total_cost = 0.0
    reported_model = None

    for index, case in enumerate(cases, start=1):
        answer = runner_mod.ask(executor_module, validator_module, executor, case)
        total_cost += answer.total_cost_usd or 0.0
        reported_model = reported_model or _model_of(answer.envelope)
        entry = corpus.by_id(case.entry_id)

        if answer.errored:
            errored += 1
        if answer.never_fit or (answer.outcome is not None and not answer.schema_valid) \
                or (answer.outcome is None and answer.schema_error and not answer.errored):
            schema_invalid += 1

        failed = answer.error or (answer.schema_error if not answer.schema_valid else None)
        if case.kind == "READING":
            score = score_mod.score_reading(case, entry, people[(case.entry_id, case.subject)],
                                            answer.result, failed=failed)
            reading_scores.append(score)
            diff = {"case_id": case.case_id, "kind": case.kind, "failed": failed,
                    "per_anchor": score.per_anchor, "missing_ids": score.missing_ids,
                    "extra_ids": score.extra_ids}
        else:
            questions = answer.questions if answer.outcome == "NEEDS_INPUT" else None
            score = score_mod.score_assumptions(case, entry, answer.result, failed=failed,
                                                needs_input_questions=questions, judge=judge)
            assumption_scores.append(score)
            if answer.schema_valid and answer.outcome == "COMPLETED" and answer.result:
                produced_sets.append((case, answer.result))
            diff = _assumption_diff(case, entry, answer, score)

        report_mod.write_case(run_dir, case, answer, diff)
        prompts.append({"case_id": case.case_id, "screen": case.screen, "prompt": case.prompt})
        status = ("ERROR" if answer.errored else
                  "never fit its shape" if answer.never_fit else
                  answer.outcome or "no-outcome") + ("" if answer.schema_valid else " (invalid)")
        print(f"[{index}/{len(cases)}] {case.case_id:<44} {status}")

    corpus.verify_unchanged()
    report_mod.write_corpus_hashes(run_dir, corpus, when="after (unchanged)")

    # The aggregate's own verdict on the whole run, in one JVM start (FR-012).
    aggregate = {"accepted": 0, "refusals_by_rule": {}, "shape_refusals": 0, "case_faults": 0,
                 "by_case": {}}
    refusals_measured = False
    if produced_sets:
        try:
            report = validate_mod.run(config.keel_cloud,
                                      validate_mod.build_batch(produced_sets),
                                      run_dir / "batch.json", run_dir / "validation.json")
            aggregate = validate_mod.fold_in(report)
            refusals_measured = True
        except Exception as exc:                  # noqa: BLE001 - unmeasured, never mis-measured
            print(f"the aggregate could not be asked: {exc}", file=sys.stderr)
            (run_dir / "validation.json").write_text(
                json.dumps({"unavailable": str(exc)}, indent=2), encoding="utf-8")

    totals = score_mod.totals(reading_scores, assumption_scores, errored=errored,
                              schema_invalid=schema_invalid,
                              refusals_by_rule=aggregate["refusals_by_rule"],
                              shape_refusals=aggregate["shape_refusals"],
                              refusals_measured=refusals_measured,
                              judge_calls=judge.call_count)
    scorecard = {
        "marks_version": marks_mod.MARKS_VERSION,
        "marks": marks,
        "model": {"claude_version": facts.get("claude_version"),
                  "reported_model": reported_model,
                  "job_timeout_seconds": executor.timeout_seconds,
                  "job_max_turns": executor.max_turns,
                  "job_budget_usd": executor.budget_usd,
                  "judge": "off" if args.no_judge else "on"},
        "n_runs": args.n_runs,
        "aggregate": {k: v for k, v in aggregate.items() if k != "by_case"},
        "judge_calls": judge.calls,
        "contract_manifest": exported.manifest,
        "reading": [_reading_json(s) for s in reading_scores],
        "assumptions": [_assumption_json(s) for s in assumption_scores],
        "totals": totals,
        "spread": {
            "recall": score_mod.spread(assumption_scores, lambda s: s.golden_belief_recall),
            "anchoring": score_mod.spread(reading_scores, lambda s: s.anchoring_accuracy),
        },
        "prompts": prompts,
    }
    report_mod.write_scorecard(run_dir, scorecard)

    judged = marks_mod.judge(totals, marks)
    verdict = {
        "scenario": "instructions",
        "baseline": bool(args.baseline),
        "passed": bool(judged["passed"]) and errored == 0,
        "errored": errored,
        "marks": judged,
        "marks_version": marks_mod.MARKS_VERSION,
        "model": scorecard["model"],
        "n_runs": args.n_runs,
        "cases": len(cases),
        "duration_s": round(time.monotonic() - started, 3),
        "total_cost_usd": round(total_cost, 4),
    }
    report_mod.write_verdict(run_dir, verdict)
    versions = json.loads((run_dir / "versions.json").read_text(encoding="utf-8"))
    path = report_mod.render_report(run_dir, verdict=verdict, scorecard=scorecard,
                                    versions=versions)
    # The one artefact with no number in it (FR-019). Keyed by entry+stage, taking the first run of
    # each case: the register is read once per instruction, not once per repetition.
    produced_by_case = {}
    for case, result in produced_sets:
        produced_by_case.setdefault(f"{case.entry_id}/{case.subject}", result)
    register = report_mod.render_register(
        run_dir, entries_by_market=report_mod.register_blocks(corpus, produced_by_case))

    print()
    print(f"verdict: {'PASSED' if verdict['passed'] else 'FAILED'}   "
          f"anchoring {_fmt(totals['anchoring_accuracy'])} · "
          f"recall {_fmt(totals['golden_belief_recall'])} · "
          f"refusals {sum(totals['refusals_by_rule'].values()) if refusals_measured else 'not measured'} · "
          f"schema-invalid {totals['schema_invalid']} · errored {errored}")
    print(f"report: {path}")
    print(f"register (unscored, for a person who knows the market): {register}")
    print(f"cost: ${total_cost:.2f}")
    return 0 if verdict["passed"] else 1


def _fmt(value) -> str:
    return "—" if value is None else f"{value * 100:.1f}%"


def _model_of(envelope) -> str | None:
    if not isinstance(envelope, dict):
        return None
    for key in ("model", "modelUsage", "model_usage"):
        value = envelope.get(key)
        if isinstance(value, str):
            return value
        if isinstance(value, dict) and value:
            return ", ".join(sorted(value))
    return None


def _assumption_diff(case, entry, answer, score) -> dict:
    goldens = entry.beliefs_for(case.subject)
    produced = (answer.result or {}).get("assumptions") if isinstance(answer.result, dict) else []
    produced = produced if isinstance(produced, list) else []
    alignment = score.alignment
    return {
        "case_id": case.case_id,
        "kind": case.kind,
        "failed": score.failed,
        "needs_input": score.needs_input,
        "existing_roles": case.existing_roles,
        "golden": [{"id": g.id, **{k: v for k, v in _golden_row(g).items()}} for g in goldens],
        "produced": produced,
        "matched": [] if alignment is None else [
            {"golden_id": p.golden_id, "produced_index": p.produced_index, "score": p.score,
             "by": p.by, "fields": p.fields} for p in alignment.matched],
        "missing": [] if alignment is None else alignment.missing,
        "extra": [] if alignment is None else alignment.extra,
        "ambiguous": [] if alignment is None else alignment.ambiguous,
    }


def _golden_row(belief) -> dict:
    return {"heading": belief.heading, "statement": belief.statement, "risk": belief.risk,
            "mark": belief.mark, "founderPhrase": belief.founder_phrase,
            "expectation": belief.expectation, "selection": belief.selection}


def _reading_json(score) -> dict:
    return {"case_id": score.case_id, "entry_id": score.entry_id, "subject": score.subject,
            "run_index": score.run_index, "given": score.given, "answered": score.answered,
            "agreed": score.agreed, "anchoring_accuracy": score.anchoring_accuracy,
            "confusion": score.confusion, "per_anchor": score.per_anchor,
            "missing_ids": score.missing_ids, "extra_ids": score.extra_ids,
            "failed": score.failed}


def _assumption_json(score) -> dict:
    return {"case_id": score.case_id, "entry_id": score.entry_id, "subject": score.subject,
            "run_index": score.run_index, "golden_total": score.golden_total,
            "matched": score.matched, "golden_belief_recall": score.golden_belief_recall,
            "exact_match": score.exact_match(), "extra_beliefs": score.extra_beliefs,
            "needs_input": score.needs_input,
            "needs_input_questions": score.needs_input_questions,
            "phrase_band": score.phrase_band, "judged": score.judged,
            "judged_candidacy": score.judged_candidacy,
            "existing_roles": score.existing_roles, "failed": score.failed,
            "missing": [] if score.alignment is None else score.alignment.missing}


if __name__ == "__main__":
    raise SystemExit(main())
