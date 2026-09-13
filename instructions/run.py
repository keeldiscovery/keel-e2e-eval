"""`python -m instructions.run` -- the whole eval, and the dry run that costs nothing.

    --dry-run        print every prompt this run would send, and the case count and estimate;
                     call nothing, spend nothing
    --host HOST      which host answers: `claude` (the default, and every published mark),
                     `copilot` or `codex`. It decides the CLI the pre-flight requires, the executor
                     keel-runtime constructs, and the prompt that host is sent -- and nothing
                     else. **Two hosts' runs are different measurements and are never averaged.**
    --baseline       name the bundle `-instructions-baseline`, and say in the report that a red
                     result is the expected one
    -k SUBSTRING     only cases whose case id contains it (`-k 01-countly`, `-k reading`)
    -n N             runs per case (default 3)
    --marks FILE     an alternative marks file
    --models FILE    a model-routing table (keel-cloud `model-routing-design.md` §4) pinning each
                     job class -- assumptions, reading, brief -- through the job's own `model`
                     key, exactly as the cloud sends it; `exported` means the table keel-cloud's
                     own exporter wrote beside the contracts. Never beside `KEEL_<HOST>_MODEL`.

**Read a prompt before spending anything.** The dry run exists for exactly that: an assumption
prompt and a reading prompt, in full, with `TASK`, `CONTRACT`, the `SOURCE MATERIAL` heading and
the nonce-fenced block. If the context keys look wrong, the fault is in `instructions/context.py`
or in keel-cloud's exporter, and it is far cheaper to find now than after a hundred calls.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from stack.config import REPO_ROOT, load_config

from . import brief as brief_mod
from . import contract as contract_mod
from . import corpus as corpus_mod
from . import instruction as instruction_mod
from . import judge as judge_mod
from . import marks as marks_mod
from . import models as models_mod
from . import prompts as prompts_mod
from . import report as report_mod
from . import runner as runner_mod
from . import score as score_mod
from . import validate as validate_mod

# Rough, and honest about being rough: the founder's own account pays, and the point of printing a
# number before the first call is that nobody is surprised by the size of the bill, not that the
# number is right to the cent.
COST_PER_CASE_ESTIMATE_USD = 0.06

SCREENS = (list(contract_mod.SCREENS_ASSUMPTIONS.values())
           + [contract_mod.SCREEN_READING, contract_mod.SCREEN_BRIEF])


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="instructions.run", description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--baseline", action="store_true")
    # spec 014 FR-001. `choices` rather than a free string: an unknown host is refused by
    # argparse, before a prerequisite is checked and before anything is spent.
    parser.add_argument("--host", default="claude", choices=("claude", "copilot", "codex"),
                        help="which host answers (default: claude)")
    parser.add_argument("-k", dest="filter", default=None)
    parser.add_argument("-n", dest="n_runs", type=int, default=3)
    parser.add_argument("--marks", default=None)
    parser.add_argument("--models", default=None,
                        help="a model-routing table pinning each job class through the job's "
                             "`model` key, or `exported` for keel-cloud's own")
    parser.add_argument("--no-judge", action="store_true",
                        help="score with the structural matcher alone (MARKS_VERSION 1's rule)")
    args = parser.parse_args(argv)

    # A table given as a file is read before anything else is asked for, so a typo in it is the
    # first thing said and not the last; `exported` has to wait for the exporter. Both refuse
    # beside a legacy `KEEL_<HOST>_MODEL`: a run pins one way (design §6).
    if args.models is not None and args.models != "exported":
        try:
            models_mod.select(args.models, host=args.host, environ=os.environ)
        except models_mod.ModelsUnavailable as reason:
            print(f"instruction eval cannot start: {reason}", file=sys.stderr)
            return 2

    config = load_config()
    # keel-runtime is imported *before* the pre-flight now, because the pre-flight asks it which
    # CLI this host needs (`EXECUTOR_BINARIES`) rather than writing the name down again. The
    # import costs nothing and spends nothing.
    try:
        executor_module, validator_module = prompts_mod.load_runtime(config.keel_runtime)
    except prompts_mod.RuntimeUnavailable as reason:
        print(f"instruction eval cannot start: {reason}", file=sys.stderr)
        return 2
    try:
        facts = runner_mod.preflight(config, dry_run=args.dry_run, host=args.host,
                                     executor_module=executor_module)
    except runner_mod.NotReady as reason:
        print(f"instruction eval cannot start: {reason}", file=sys.stderr)
        return 2

    corpus = corpus_mod.load(config.keel_cloud)

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
                                             n_runs=args.n_runs, host=args.host))
    if args.filter:
        needle = args.filter.lower()
        cases = [c for c in cases
                 if needle in c.case_id.lower()
                 or (needle == "reading" and c.kind == "READING")
                 or (needle == "assumptions" and c.kind == "ASSUMPTIONS")
                 or (needle == "brief" and c.kind == "BRIEF")]
    return cases


def _dry_run(config, corpus, executor_module, args) -> int:
    """Everything a real run does, up to the point where it would cost money."""
    into = Path(REPO_ROOT) / "runs" / ".contracts-dry"
    exported = contract_mod.export(config.keel_cloud, into)
    instructions = _instructions_for(config)
    cases = _all_cases(corpus, exported, instructions, executor_module, args)
    try:
        table = models_mod.select(args.models, host=args.host, exported=exported,
                                  environ=os.environ)
    except models_mod.ModelsUnavailable as reason:
        print(f"instruction eval cannot start: {reason}", file=sys.stderr)
        return 2
    models_mod.stamp(cases, table, args.host)

    print(f"host: {args.host} -- every prompt below is the one this host's executor sends")
    print(f"models pinned through the job's `model` key: {models_mod.describe(table, args.host)}"
          + (f" (from {table.source})" if table else ""))
    print(f"contract exported from keel-cloud {exported.manifest.get('keel_cloud_commit')}"
          f"{' (dirty)' if exported.manifest.get('keel_cloud_dirty') else ''}")
    for screen in SCREENS:
        print(f"  {screen:<24} keys: {exported.keys_for(screen)}")
    print()

    shown = {"ASSUMPTIONS": False, "READING": False, "BRIEF": False}
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
    brief = sum(1 for c in cases if c.kind == "BRIEF")
    print("-" * 100)
    print(f"{len(cases)} cases: {assumptions} assumption, {reading} reading, {brief} brief, "
          f"N={args.n_runs} runs per case")
    print(f"rough estimate at ${COST_PER_CASE_ESTIMATE_USD:.2f} a case: "
          f"${len(cases) * COST_PER_CASE_ESTIMATE_USD:.2f} of the founder's own money")
    print("nothing was called and nothing was spent")
    return 0


def _real_run(config, corpus, executor_module, validator_module, facts, args) -> int:
    started = time.monotonic()
    run_dir = report_mod.start_bundle(config, baseline=args.baseline, host=args.host)
    print(f"run bundle: {run_dir}")
    print(f"host: {args.host} ({facts.get('cli')} {facts.get('cli_version') or 'version unknown'})")

    exported = contract_mod.export(config.keel_cloud, run_dir / "contracts")
    report_mod.write_corpus_hashes(run_dir, corpus, when="before")
    instructions = _instructions_for(config)
    cases = _all_cases(corpus, exported, instructions, executor_module, args)
    marks = marks_mod.load(args.marks)

    # The model-routing table (keel-cloud model-routing-design.md §7 step 2): each case is pinned
    # through the wire's own sixth key, `model: {<host>: <model>}`, stamped after the prompt was
    # rendered so it is never in the prompt. `pinned_model` below stays the single-model pin of
    # the runs of record so far; the two are exclusive and `select` refuses both at once.
    try:
        table = models_mod.select(args.models, host=args.host, exported=exported,
                                  environ=os.environ)
    except models_mod.ModelsUnavailable as reason:
        print(f"instruction eval cannot start: {reason}", file=sys.stderr)
        return 2
    models_mod.stamp(cases, table, args.host)
    # keel-runtime 0.5.0 reads the key; anything older reads a constructor pin, so on an older
    # runtime the per-case value is put where that runtime looks (`apply_fallback`), one case at a
    # time. Asked of the runtime module itself, never assumed.
    routing_runtime = models_mod.reads_the_job_key(sys.modules.get("keel_runtime"))
    if table is not None:
        print(f"models pinned through the job's `model` key: "
              f"{models_mod.describe(table, args.host)} (from {table.source}; "
              f"keel-runtime {'reads the key' if routing_runtime else 'is older than 0.5.0, so each case is pinned on the executor instead'})")

    # Both executors put their per-job dirs at `<home>/jobs/<job_id>`, so the home is the run
    # directory itself and the bundle's `jobs/` is exactly what the run-bundle contract describes.
    # The wall clock is production's own default (keel-runtime `DEFAULT_JOB_TIMEOUT_SECONDS`) and
    # is deliberately not overridden: an eval more patient than production would report an
    # instruction as working that a founder watches fail.
    #
    # **Through `get_executor`, never by naming a class** (spec 014 FR-003). It is the same
    # function `keel_runtime.cli` calls for `--executor`, so which class a host means, what
    # `claude-code` aliases to, and which caps each constructor is given are keel-runtime's to
    # decide -- and a second table here would be the sixth version of `runs/DRIFT.md`
    # #33/#36/#41/#44/#45: the referee holding its own copy of something it does not own.
    # Each host's pin is its own variable, the same names keel-runtime reads (spec 005 C-5 for
    # Copilot; spec 008 for Codex, whose unpinned run answers with the account's default model).
    pinned_model = (os.environ.get("KEEL_CODEX_MODEL") if args.host == "codex"
                    else os.environ.get("KEEL_COPILOT_MODEL")) or None
    if routing_runtime and pinned_model:
        # keel-runtime 0.5.0 reads no such variable (spec 009): honouring it here would be the
        # referee pinning what production cannot, and ignoring it would be an unpinned run
        # wearing a pin's name. Either is a lie; refuse before the first call.
        print(f"keel-runtime {'.'.join(map(str, models_mod.runtime_version(executor_module)))} "
              f"ignores KEEL_<HOST>_MODEL; pin with MODELS=<file> (the job's `model` key) instead",
              file=sys.stderr)
        return 2
    executor = executor_module.get_executor(
        args.host, home=run_dir,
        **models_mod.executor_kwargs(args.host, pinned_model, routing_runtime))
    judge = judge_mod.NoJudge() if args.no_judge else judge_mod.Judge()
    people = {(e.id, p.person): p for e in corpus.entries for p in e.people()}

    reading_scores, assumption_scores, brief_scores = [], [], []
    prompts, errored = [], 0
    schema_invalid = 0
    produced_sets = []
    total_cost = 0.0
    total_premium = 0.0
    premium_seen = False
    total_tokens = {"input_tokens": 0, "output_tokens": 0}
    tokens_seen = False
    reported_model = None

    # Written before the first call, so a run that dies at case one still says what it was.
    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    report_mod.write_manifest(run_dir, _manifest(args, facts, executor, pinned_model,
                                                 None, started_at, table=table))

    for index, case in enumerate(cases, start=1):
        models_mod.apply_fallback(executor, case, table, routing_runtime=routing_runtime)
        answer = runner_mod.ask(executor_module, validator_module, executor, case)
        total_cost += answer.total_cost_usd or 0.0
        if answer.premium_requests is not None:
            premium_seen = True
            total_premium += answer.premium_requests
        if answer.tokens:
            tokens_seen = True
            for key in total_tokens:
                total_tokens[key] += int(answer.tokens.get(key) or 0)
        reported_model = reported_model or answer.reported_model
        entry = corpus.by_id(case.entry_id)

        if answer.errored:
            errored += 1
        if answer.never_fit or (answer.outcome is not None and not answer.schema_valid) \
                or (answer.outcome is None and answer.schema_error and not answer.errored):
            schema_invalid += 1

        failed = answer.error or (answer.schema_error if not answer.schema_valid else None)
        if case.kind == "BRIEF":
            questions = answer.questions if answer.outcome == "NEEDS_INPUT" else None
            score = brief_mod.score_brief(case, entry, answer.result, outcome=answer.outcome,
                                          failed=failed, needs_input_questions=questions)
            brief_scores.append(score)
            diff = {"case_id": case.case_id, "kind": case.kind, "failed": failed,
                    "needs_input": score.needs_input, "paragraph": score.paragraph,
                    "length": score.length, "marks": score.marks, "findings": score.findings,
                    "deciding_lines": {
                        c.get("stage"): brief_mod.deciding_line(c)
                        for c in (case.payload.get("context") or {}).get("claims") or []}}
        elif case.kind == "READING":
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

        report_mod.write_case(run_dir, case, answer, diff, host=args.host)
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
                              refusals_shown=aggregate["accepted"]
                              + sum(aggregate["refusals_by_rule"].values()),
                              judge_calls=judge.call_count,
                              brief_scores=brief_scores)
    scorecard = {
        "marks_version": marks_mod.MARKS_VERSION,
        "marks": marks,
        "model": _model_block(args, facts, executor, pinned_model, reported_model, table=table),
        "n_runs": args.n_runs,
        "aggregate": {k: v for k, v in aggregate.items() if k != "by_case"},
        "judge_calls": judge.calls,
        "contract_manifest": exported.manifest,
        "reading": [_reading_json(s) for s in reading_scores],
        "assumptions": [_assumption_json(s) for s in assumption_scores],
        "brief": [_brief_json(s) for s in brief_scores],
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
        # spec 014 FR-005: which host, on the one file a gate is read off.
        "host": args.host,
        "cli": facts.get("cli"),
        "cli_version": facts.get("cli_version"),
        "passed": bool(judged["passed"]) and errored == 0,
        "errored": errored,
        "marks": judged,
        "marks_version": marks_mod.MARKS_VERSION,
        "model": scorecard["model"],
        # keel-cloud model-routing-design.md §7: the per-class pins this run measured, `None`
        # where the host answered on its CLI's default; `null` for a single-model run.
        "models_used": table.models_used(args.host) if table else None,
        "n_runs": args.n_runs,
        "cases": len(cases),
        "duration_s": round(time.monotonic() - started, 3),
        # C-7: one of these two, never both, and never one filled in from the other. Copilot
        # reports premium requests and no dollars; a `$0.00` on a Copilot report would be a lie
        # in the shape of a number.
        "total_cost_usd": round(total_cost, 4) if not (premium_seen or tokens_seen) else None,
        "total_premium_requests": round(total_premium, 4) if premium_seen else None,
        # keel-runtime spec 008: Codex's unit. Input and output, summed over the run, never priced.
        "total_tokens": dict(total_tokens) if tokens_seen else None,
    }
    report_mod.write_verdict(run_dir, verdict)
    report_mod.write_manifest(run_dir, _manifest(args, facts, executor, pinned_model,
                                                 reported_model, started_at, table=table))
    versions = json.loads((run_dir / "versions.json").read_text(encoding="utf-8"))
    path = report_mod.render_report(run_dir, verdict=verdict, scorecard=scorecard,
                                    versions=versions, host=args.host)
    # The one artefact with no number in it (FR-019). Keyed by entry+stage, taking the first run of
    # each case: the register is read once per instruction, not once per repetition.
    produced_by_case = {}
    for case, result in produced_sets:
        produced_by_case.setdefault(f"{case.entry_id}/{case.subject}", result)
    register = report_mod.render_register(
        run_dir, entries_by_market=report_mod.register_blocks(corpus, produced_by_case),
        paragraphs=report_mod.paragraph_blocks(corpus, brief_scores),
        host=args.host, cli_version=facts.get("cli_version"), model=reported_model)

    print()
    print(f"verdict: {'PASSED' if verdict['passed'] else 'FAILED'}   "
          f"anchoring {_fmt(totals['anchoring_accuracy'])} · "
          f"recall {_fmt(totals['golden_belief_recall'])} · "
          f"refusals {sum(totals['refusals_by_rule'].values()) if refusals_measured else 'not measured'}"
          f"{' of ' + str(totals['refusals_shown']) + ' judged' if refusals_measured else ''} · "
          f"brief {_fmt(totals['brief_paragraphs']) if totals['brief_measured'] else 'not measured'} · "
          f"schema-invalid {totals['schema_invalid']} · errored {errored}")
    print(f"report: {path}")
    print(f"register (unscored, for a person who knows the market): {register}")
    if premium_seen:
        print(f"cost: {total_premium:g} premium requests "
              f"(this host reports no dollars, and none are invented)")
    elif tokens_seen:
        print(f"cost: {total_tokens['input_tokens']} input + {total_tokens['output_tokens']} output "
              f"tokens (this host reports tokens against a plan; no dollars are invented)")
    else:
        print(f"cost: ${total_cost:.2f}")
    print(f"host: {args.host} · cli {facts.get('cli_version')} · "
          f"model {reported_model or 'not reported'} · pinned "
          + (f"per class {models_mod.describe(table, args.host)}" if table
             else (pinned_model or 'nothing')))
    return 0 if verdict["passed"] else 1


def _fmt(value) -> str:
    return "—" if value is None else f"{value * 100:.1f}%"


def _model_block(args, facts, executor, pinned_model, reported_model, table=None) -> dict:
    """Everything a mark is only comparable within (spec 014 FR-005).

    `job_max_turns` and `job_budget_usd` are read with `getattr`, and that is not defensiveness:
    `CopilotExecutor` **has neither**, because the CLI has no flag for either and keel-runtime
    refuses to pretend otherwise (C-7). `None` here means "this host has no such cap", which is a
    fact about the host and is exactly what the report should say.
    """
    return {
        "host": args.host,
        "cli": facts.get("cli"),
        "cli_version": facts.get("cli_version"),
        "pinned_model": pinned_model,
        "reported_model": reported_model,
        # The per-class pins (model-routing-design.md §7), carried here so a rescore and the
        # report keep them; `None` for a single-model run.
        "models_used": table.models_used(args.host) if table else None,
        "models_source": table.source if table else None,
        "job_timeout_seconds": getattr(executor, "timeout_seconds", None),
        "job_max_turns": getattr(executor, "max_turns", None),
        "job_budget_usd": getattr(executor, "budget_usd", None),
        "max_ai_credits": getattr(executor, "max_ai_credits", None),
        "judge": "off" if args.no_judge else "on",
        # The tie-breaker is the referee's, not the subject's, and it stays on `claude` on both
        # hosts so the *scoring* is one constant across the comparison. Written down rather than
        # assumed (spec 014's fifth clarification).
        "judge_host": "off" if args.no_judge else "claude",
    }


def _manifest(args, facts, executor, pinned_model, reported_model, started_at,
              table=None) -> dict:
    """`manifest.json`: what this run was, in the one file that is written before the first call.

    A bundle whose run died at case one still names its host, its CLI and its rubric -- which is
    the difference between a failed run somebody can read and a directory somebody has to guess
    about.
    """
    return {
        "scenario": "instructions",
        "baseline": bool(args.baseline),
        "host": args.host,
        "cli": {"binary": facts.get("cli"), "version": facts.get("cli_version")},
        "model": {"pinned": pinned_model, "reported": reported_model,
                  "per_class": table.models_used(args.host) if table else None,
                  "table": table.source if table else None},
        "marks_version": marks_mod.MARKS_VERSION,
        "n_runs": args.n_runs,
        "filter": args.filter,
        "judge": "off" if args.no_judge else "on",
        "caps": {"job_timeout_seconds": getattr(executor, "timeout_seconds", None),
                 "job_max_turns": getattr(executor, "max_turns", None),
                 "job_budget_usd": getattr(executor, "budget_usd", None),
                 "max_ai_credits": getattr(executor, "max_ai_credits", None)},
        "started_at": started_at,
    }


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


def _brief_json(score) -> dict:
    return {"case_id": score.case_id, "entry_id": score.entry_id, "run_index": score.run_index,
            "paragraph": score.paragraph, "length": score.length, "marks": score.marks,
            "findings": score.findings, "phrasing": score.phrasing,
            "met": score.met, "failed": score.failed,
            "needs_input": score.needs_input,
            "needs_input_questions": score.needs_input_questions}


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
