"""`python -m instructions.run` -- the whole eval, and the dry run that costs nothing.

    --dry-run        print every screen's context keys and one prompt per kind, run keel-cloud's
                     engine for every selected COMPARE row, and write a scorecard and a verdict;
                     call no model, spend nothing
    --host HOST      which host answers: `claude` (the default, and every published mark),
                     `copilot` or `codex`. It decides the CLI the pre-flight requires, the executor
                     keel-runtime constructs, and the prompt that host is sent -- and nothing
                     else. **Two hosts' runs are different measurements and are never averaged.**
    --baseline       name the bundle `-instructions-baseline`, and say in the report that a red
                     result is the expected one
    -k NEEDLE        only cases whose case id contains it, case-insensitively (`-k 03-lullaby`,
                     `-k 03-lullaby/INTERPRET`), or one kind word: context, frame, calibration,
                     respondent, reading, compare, brief. A needle matching nothing says so and
                     spends nothing.
    -n N             runs per model case (default 3)
    --marks FILE     an alternative marks file
    --models FILE    a model-routing table pinning each job class -- context, frame, calibration,
                     respondent, reading, brief -- through the job's own `model` key, exactly as
                     the cloud sends it; `exported` means the table keel-cloud's own exporter
                     wrote beside the contracts. Never beside `KEEL_<HOST>_MODEL`.

**Read a prompt before spending anything.** The dry run exists for exactly that. At
`MARKS_VERSION` 9 it does one more thing: `COMPARE` is keel-cloud's engine, not a model, so the dry
run measures `compare_correctness` for real and writes it into a bundle (judgement call 34) -- and
every model-scored mark beside it is *not measured*, so the dry verdict is `passed: false` by
construction and says why.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import types
from pathlib import Path

from stack.config import REPO_ROOT, load_config

from . import brief as brief_mod
from . import chat as chat_mod
from . import compare as compare_mod
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
# number before the first call is that nobody is surprised by the size of the bill.
COST_PER_CASE_ESTIMATE_USD = 0.04

#: The nine model screens (spec 029 FR-016; the chat pair at v17). `COMPARE` is not one: it is never sent.
SCREENS = contract_mod.MODEL_SCREENS

#: `-k` kind words (research R6): each selects by `Case.kind` exactly. `interpret` is deliberately
#: not one -- it would be ambiguous between the three interpretation screens and the reads; the
#: slash form `03-lullaby/INTERPRET` selects the reads.
KIND_WORDS = {"context": "CONTEXT", "frame": "FRAME", "calibration": "CALIBRATION",
              "respondent": "RESPONDENT", "reading": "READING", "compare": "COMPARE",
              "brief": "BRIEF", "chat": "CHAT", "feedback": "FEEDBACK"}


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
    parser.add_argument("--why", default=None,
                        help="why this run is paid for: instruction:<file>, prompt:<file>, "
                             "contract:<file> (a screen), new-model:<host>:<model> or "
                             "marks:<version> (the full run); refused without one unless "
                             "--dry-run (design §7.1)")
    parser.add_argument("--models", default=None,
                        help="a model-routing table pinning each job class through the job's "
                             "`model` key, or `exported` for keel-cloud's own")
    parser.add_argument("--no-judge", action="store_true",
                        help="ask no judge: a no_leak inflection tie goes undecided and is "
                             "counted clean, and leak_judged says how many")
    args = parser.parse_args(argv)
    from . import why as why_mod  # noqa: PLC0415
    try:
        args.why_record = why_mod.check(args.why, screen=bool(args.filter), dry_run=args.dry_run)
    except why_mod.NoReason as refusal:
        print(refusal, file=sys.stderr)
        return 2

    # A table given as a file is read before anything else is asked for, so a typo in it is the
    # first thing said and not the last; `exported` has to wait for the exporter.
    if args.models is not None and args.models != "exported":
        try:
            models_mod.select(args.models, host=args.host, environ=os.environ)
        except models_mod.ModelsUnavailable as reason:
            print(f"instruction eval cannot start: {reason}", file=sys.stderr)
            return 2

    config = load_config()
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

    try:
        corpus = corpus_mod.load(config.keel_cloud)
    except corpus_mod.CorpusError as reason:
        print(f"instruction eval cannot start: {reason}", file=sys.stderr)
        return 2

    if args.dry_run:
        return _dry_run(config, corpus, executor_module, facts, args)

    with runner_mod.RunLock(REPO_ROOT / "runs"):
        return _real_run(config, corpus, executor_module, validator_module, facts, args)


# --------------------------------------------------------------------------------------- helpers

def _instructions_for(config, screens=SCREENS) -> dict:
    """Every template keel-cloud has for the seven screens; `None` for one it does not have yet
    (keel-cloud 059-065, the Waits). A selected case whose template is missing is refused by name
    after the needle is applied (`_missing_instructions`), so `-k compare` runs before any
    template exists."""
    out = {}
    for screen in screens:
        try:
            out[screen] = instruction_mod.read(config.keel_cloud, screen)
        except instruction_mod.InstructionUnavailable:
            out[screen] = None
    return out


def _missing_instructions(config, cases, instructions) -> list:
    return sorted({f"{c.screen}: no instruction at {instruction_mod.path_for(config.keel_cloud, c.screen)}"
                   for c in cases if c.kind != "COMPARE" and instructions.get(c.screen) is None})


def select(cases: list, needle: str | None) -> list:
    """`-k` (research R6): a kind word selects that kind exactly; anything else is a
    case-insensitive substring of the case id."""
    if not needle:
        return list(cases)
    word = needle.strip().lower()
    if word in KIND_WORDS:
        return [c for c in cases if c.kind == KIND_WORDS[word]]
    return [c for c in cases if word in c.case_id.lower()]


def _all_cases(corpus, exported, instructions, executor_module, args) -> list:
    cases = []
    for entry in corpus.entries:
        cases.extend(prompts_mod.build_cases(entry, exported, instructions, executor_module,
                                             n_runs=args.n_runs, host=args.host))
    # Corpus revision 9 (MARKS_VERSION 17): the calibration chat's cases, then the six-scenario verdicts' row.
    # (`load` always carries them; a corpus built by hand without them builds neither.)
    if corpus.chat:
        cases.extend(prompts_mod.build_chat_cases(corpus, exported, instructions, executor_module,
                                                  n_runs=args.n_runs, host=args.host))
    if corpus.scenarios:
        cases.append(prompts_mod.six_scenarios_case())
    return select(cases, args.filter)


def _compare(config, corpus, cases, run_dir) -> list:
    """Every selected `COMPARE` row, shelled to keel-cloud's engine at build time -- the dry path
    and the real path are one code path (research R7). Both files stay in the bundle."""
    scores = []
    for case in cases:
        if case.kind != "COMPARE":
            continue
        if case.entry_id == compare_mod.SIX_ID:
            try:
                raw = compare_mod.six_scenarios(config.keel_cloud, corpus.scenarios)
            except compare_mod.EngineUnavailable as reason:
                raw = compare_mod.unmeasured(compare_mod.SIX_ID, str(reason))
            scores.append(score_mod.score_compare(case, types.SimpleNamespace(id=compare_mod.SIX_ID), raw))
            line = (f"{raw.agreed} of {raw.checks} agreed · {len(raw.mismatches)} scenarios differ"
                    if raw.measured else f"NOT measured -- {str(raw.reason).splitlines()[0]}")
            print(f"[compare] {case.case_id:<44} {line}")
            continue
        entry = corpus.by_id(case.entry_id)
        compare_dir = Path(run_dir) / "compare"
        try:
            produced = compare_mod.run(config.keel_cloud, case.compare_input,
                                       compare_dir / f"{entry.id}.in.json",
                                       compare_dir / f"{entry.id}.out.json")
            raw = compare_mod.diff(entry.expected, produced, entry=entry)
        except compare_mod.EngineUnavailable as reason:
            raw = compare_mod.unmeasured(entry.id, str(reason))
        scores.append(score_mod.score_compare(case, entry, raw))
        line = (f"{raw.agreed} of {raw.checks} agreed · {len(raw.reported_diffs)} counts differ"
                if raw.measured else f"NOT measured -- {str(raw.reason).splitlines()[0]}")
        print(f"[compare] {case.case_id:<44} {line}")
    return scores


def _prepare(config, corpus, executor_module, args, contracts_dir):
    """The export, the registry bound to the corpus, the cases selected -- or a refusal by name."""
    exported = contract_mod.export(config.keel_cloud, contracts_dir)
    corpus.bind(exported.registry)
    instructions = _instructions_for(config)
    cases = _all_cases(corpus, exported, instructions, executor_module, args)
    return exported, instructions, cases


def _counts(cases) -> dict:
    out = {kind: 0 for kind in prompts_mod.KINDS}
    for case in cases:
        out[case.kind] = out.get(case.kind, 0) + 1
    return out


def denominators(cases) -> dict:
    """Spec 030 US3, call 47: what each structural mark is counted over, per entry and per N --
    read off the cases the registry and the entries built (`registry_slice`, `plan`), never typed.
    A dry run has no answer to score, so `dimension_coverage`, `option_validity` and `no_leak` stay
    unmeasured there (call 13); what it can show, and does, is the denominator each would have.
    Calibration and respondent count one a dimension (coverage and validity alike, Price
    included); `sweep_a` is the PROBLEM calibration questions and the PRIMARY Part 1 items,
    `sweep_b` every respondent item -- each only where the model wrote text a reader is shown
    (calls 52, 53: never Price, never Frequency over a framed window; the case's `swept`). And the
    names W3 / W8 are held to (call 55): the corpus's, else none."""
    out = {}
    for case in cases:
        if case.run_index != 1 or case.kind not in ("CALIBRATION", "RESPONDENT"):
            continue
        row = out.setdefault(case.entry_id, {"calibration": 0, "respondent": {}, "sweep_a": 0,
                                             "sweep_b": 0, "short_name": None,
                                             "offer_name": None})
        row["short_name"] = case.meta.get("short_name")
        row["offer_name"] = case.meta.get("offer_name")
        swept = len(case.meta.get("swept") or [])
        if case.kind == "CALIBRATION":
            row["calibration"] += len(case.meta.get("registry_slice") or [])
            if case.meta.get("vector") == "PROBLEM":
                row["sweep_a"] += swept
            continue
        count = len(case.meta.get("plan") or [])
        link = case.meta.get("link") or corpus_mod.LINK_PRIMARY
        row["respondent"][link] = row["respondent"].get(link, 0) + count
        row["sweep_b"] += swept
        if case.meta.get("part") == 1 and link == corpus_mod.LINK_PRIMARY:
            row["sweep_a"] += swept
    return out


def chat_denominators(cases) -> dict:
    """What each chat mark is counted over per N, read off the cases and the corpus's own labels (never typed):
    the chat cases (`follow_up_budget`, `preview_rules`, `no_founder_leak`), those the corpus measures rather than
    leaves out (`one_measurable` reads a proposal on all of them, and `leave_out` on the rest), those expecting one
    follow-up (a case where the model asks has no proposal to read in this one-call chat), the Importance cases
    (`importance_list`) and the feedback cases (`feedback_obeys`)."""
    chat = [c for c in cases if c.kind == "CHAT" and c.run_index == 1]
    feedback = [c for c in cases if c.kind == "FEEDBACK" and c.run_index == 1]
    labels = [c.meta["chat_case"] for c in chat]
    return {"chat": len(chat), "ideas": len({c.entry_id for c in chat}),
            "leave_out": sum(1 for x in labels if x.leaves_out),
            "follow_up_expected": sum(1 for x in labels if x.follow_up),
            "importance": sum(1 for x in labels if x.dimension == chat_mod.IMPORTANCE),
            "feedback": len(feedback),
            "feedback_refusals": sum(1 for c in feedback
                                     if c.meta["feedback"]["expect"]["outcome"] == "refuse")}


def _chat_denominator_line(row: dict) -> str:
    return (f"calibration chat, per N: {row['chat']} chat cases over {row['ideas']} ideas "
            f"({row['follow_up_expected']} expecting one follow-up, {row['leave_out']} to leave out, "
            f"{row['importance']} Importance) · {row['feedback']} feedback cases "
            f"({row['feedback_refusals']} to refuse)")


def _denominator_line(rows: dict) -> str:
    calibration = sum(r["calibration"] for r in rows.values())
    respondent = sum(sum(r["respondent"].values()) for r in rows.values())
    sweeps = sum(r["sweep_a"] + r["sweep_b"] for r in rows.values())
    return (f"denominators read off the registry, per N: dimension_coverage {calibration} "
            f"calibration + {respondent} respondent · no_leak {sweeps} sweeps")


def _dry_run(config, corpus, executor_module, facts, args) -> int:
    """Everything a real run does, up to the point where it would cost money -- and `COMPARE`,
    which costs nothing, done for real."""
    run_dir = report_mod.start_bundle(config, baseline=args.baseline, host=args.host)
    try:
        exported, instructions, cases = _prepare(config, corpus, executor_module, args,
                                                 run_dir / "contracts")
    except (contract_mod.ContractUnavailable, corpus_mod.CorpusError) as reason:
        print(f"instruction eval cannot start: {reason}", file=sys.stderr)
        return 2
    if not cases:
        print(f"no case matches -k {args.filter!r}; nothing was built and nothing was spent")
        return 2
    missing = _missing_instructions(config, cases, instructions)
    if missing:
        print("instruction eval cannot start: keel-cloud has no template yet for a selected "
              "screen (keel-cloud 059-065, the Waits):\n  " + "\n  ".join(missing),
              file=sys.stderr)
        return 2
    try:
        table = models_mod.select(args.models, host=args.host, exported=exported,
                                  environ=os.environ)
    except models_mod.ModelsUnavailable as reason:
        print(f"instruction eval cannot start: {reason}", file=sys.stderr)
        return 2
    model_cases = [c for c in cases if c.kind != "COMPARE"]
    models_mod.stamp(model_cases, table, args.host)

    print(f"host: {args.host} -- every prompt below is the one this host's executor sends")
    print(f"models pinned through the job's `model` key: {models_mod.describe(table, args.host)}"
          + (f" (from {table.source})" if table else ""))
    print(f"contract exported from keel-cloud {exported.manifest.get('keel_cloud_commit')}"
          f"{' (dirty)' if exported.manifest.get('keel_cloud_dirty') else ''}; registry version "
          f"{exported.registry.version}")
    for screen in SCREENS:
        try:
            print(f"  {screen:<24} keys: {exported.keys_for(screen)}")
        except contract_mod.ContractUnavailable as reason:
            print(f"  {screen:<24} {reason}")
    print()

    shown = set()
    for case in model_cases:
        if case.kind in shown:
            continue
        shown.add(case.kind)
        print("=" * 100)
        print(f"{case.case_id}   ({case.screen})")
        print("=" * 100)
        print(case.prompt)
        print()

    compare_scores = _compare(config, corpus, cases, run_dir)
    marks = marks_mod.load(args.marks)
    totals = score_mod.totals(compare_scores=compare_scores)
    scorecard = {
        "marks_version": marks_mod.MARKS_VERSION, "marks": marks, "dry_run": True,
        "model": {"host": args.host, "cli": facts.get("cli"), "cli_version": None},
        "n_runs": args.n_runs, "registry_version": exported.registry.version,
        "contract_manifest": exported.manifest,
        "compare": [_compare_json(s) for s in compare_scores],
        "totals": totals, "spread": {}, "prompts": [],
        "denominators": denominators(cases),
        "chat_denominators": chat_denominators(cases),
    }
    report_mod.write_scorecard(run_dir, scorecard)
    judged = marks_mod.judge(totals, marks)
    counts = _counts(cases)
    verdict = {"scenario": "instructions", "dry_run": True, "host": args.host,
               "passed": False, "marks": judged, "marks_version": marks_mod.MARKS_VERSION,
               "unmet_prerequisites": [u["reason"] for u in totals["compare_unmeasured"]],
               "why_not_passed": "a dry run calls no model: every model-scored mark is "
                                 "unmeasured, and an unmeasured mark is not met (call 13)",
               "cases": len(model_cases), "compare_rows": counts["COMPARE"],
               "n_runs": args.n_runs, "total_cost_usd": 0.0}
    report_mod.write_verdict(run_dir, verdict)

    print("-" * 100)
    print(f"{len(model_cases)} cases: {counts['CONTEXT'] + counts['FRAME']} interpretation, "
          f"{counts['CALIBRATION']} calibration, {counts['RESPONDENT']} respondent, "
          f"{counts['READING']} interpret, {counts['BRIEF']} brief, {counts['CHAT']} chat, "
          f"{counts['FEEDBACK']} feedback, N={args.n_runs} runs per case "
          f"-- plus {counts['COMPARE']} COMPARE row(s), which are never a call")
    compare_line = (f"{totals['compare_agreed']} of {totals['compare_checks']}"
                    if totals["compare_measured"] else "NOT measured")
    print(f"compare_correctness: {compare_line} · every model mark unmeasured · passed: false")
    for entry_id, row in scorecard["denominators"].items():
        links = " + ".join(f"{n} {link}" for link, n in row["respondent"].items())
        names = (f"W3 held to {row.get('short_name')!r}" if row.get("short_name")
                 else "W3 held to no name") + " · " + (
            f"W8 held to {row.get('offer_name')!r}" if row.get("offer_name")
            else "W8 held to no name")
        print(f"  {entry_id:<20} calibration {row['calibration']} · respondent {links} · "
              f"no_leak sweep A {row['sweep_a']} + sweep B {row['sweep_b']} · {names}")
    print(_denominator_line(scorecard["denominators"]))
    print(_chat_denominator_line(scorecard["chat_denominators"]))
    print(f"rough estimate at ${COST_PER_CASE_ESTIMATE_USD:.2f} a case: "
          f"${len(model_cases) * COST_PER_CASE_ESTIMATE_USD:.2f} of the founder's own money")
    print(f"bundle: {run_dir}")
    print("nothing was called and nothing was spent")
    return 0


def _real_run(config, corpus, executor_module, validator_module, facts, args) -> int:
    started = time.monotonic()
    run_dir = report_mod.start_bundle(config, baseline=args.baseline, host=args.host)
    print(f"run bundle: {run_dir}")
    print(f"host: {args.host} ({facts.get('cli')} {facts.get('cli_version') or 'version unknown'})")

    try:
        exported, instructions, cases = _prepare(config, corpus, executor_module, args,
                                                 run_dir / "contracts")
    except (contract_mod.ContractUnavailable, corpus_mod.CorpusError) as reason:
        print(f"instruction eval cannot start: {reason}", file=sys.stderr)
        return 2
    if not cases:
        print(f"no case matches -k {args.filter!r}; nothing was built and nothing was spent")
        return 2
    missing = _missing_instructions(config, cases, instructions)
    if missing:
        print("instruction eval cannot start: keel-cloud has no template yet for a selected "
              "screen:\n  " + "\n  ".join(missing), file=sys.stderr)
        return 2
    report_mod.write_corpus_hashes(run_dir, corpus, when="before")
    marks = marks_mod.load(args.marks)
    model_cases = [c for c in cases if c.kind != "COMPARE"]

    try:
        table = models_mod.select(args.models, host=args.host, exported=exported,
                                  environ=os.environ)
    except models_mod.ModelsUnavailable as reason:
        print(f"instruction eval cannot start: {reason}", file=sys.stderr)
        return 2
    models_mod.stamp(model_cases, table, args.host)
    routing_runtime = models_mod.reads_the_job_key(sys.modules.get("keel_runtime"))
    if table is not None:
        print(f"models pinned through the job's `model` key: "
              f"{models_mod.describe(table, args.host)} (from {table.source}; "
              f"keel-runtime {'reads the key' if routing_runtime else 'is older than 0.5.0, so each case is pinned on the executor instead'})")

    pinned_model = (os.environ.get("KEEL_CODEX_MODEL") if args.host == "codex"
                    else os.environ.get("KEEL_COPILOT_MODEL")) or None
    if routing_runtime and pinned_model:
        print(f"keel-runtime {'.'.join(map(str, models_mod.runtime_version(executor_module)))} "
              f"ignores KEEL_<HOST>_MODEL; pin with MODELS=<file> (the job's `model` key) instead",
              file=sys.stderr)
        return 2
    # **Through `get_executor`, never by naming a class** (spec 014 FR-003): which class a host
    # means is keel-runtime's to decide, and a second table here would be DRIFT #33's sixth copy.
    executor = executor_module.get_executor(
        args.host, home=run_dir,
        **models_mod.executor_kwargs(args.host, pinned_model, routing_runtime))
    judge = judge_mod.NoJudge() if args.no_judge else judge_mod.Judge()

    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    report_mod.write_manifest(run_dir, _manifest(args, facts, executor, pinned_model, None,
                                                 started_at, table=table, exported=exported,
                                                 corpus=corpus))

    # COMPARE first: it spends nothing, and a run whose engine cannot be asked should say so
    # before the first paid call rather than after the last.
    compare_scores = _compare(config, corpus, cases, run_dir)

    state = _RunState()
    # Judgement call 41: the five screens keel-cloud redraws are judged as they are answered, so a
    # rule refusal gets the one repair turn the cloud would queue; the rest wait for the batch.
    verdicts = _Verdicts(config.keel_cloud, run_dir / "verdicts",
                         validate_mod.shapes_taken(config.keel_cloud))
    for index, case in enumerate(model_cases, start=1):
        models_mod.apply_fallback(executor, case, table, routing_runtime=routing_runtime)
        answer = runner_mod.ask_with_redraw(
            executor_module, validator_module, executor, case, verdicts,
            render=lambda payload, case=case: prompts_mod.render(
                executor_module, payload, job_id=prompts_mod._slug(case.case_id) + "-turn2",
                host=args.host))
        entry = corpus.by_id(case.entry_id)          # None on a chat case: it belongs to no entry
        for draft in (answer, answer.redraw):
            if draft is not None:
                _count_draft(state, draft)
        scored = answer.scored
        failed = scored.error or (scored.schema_error if not scored.schema_valid else None)
        failed = failed or refused_twice(case, answer.redraw is not None,
                                         answer.accepted is not None, answer.refusals)
        diff = _score(case, entry, scored, failed, state, judge)
        state.record_verdicts(case, answer)
        report_mod.write_case(run_dir, case, answer, diff, host=args.host)
        state.prompts.append({"case_id": case.case_id, "screen": case.screen,
                              "prompt": case.prompt})
        status = ("ERROR" if answer.errored else
                  "never fit its shape" if answer.never_fit else
                  answer.outcome or "no-outcome") + ("" if answer.schema_valid else " (invalid)")
        if answer.redraw is not None:
            first_rule = (answer.refusals[0] if answer.refusals else {}).get("rule")
            status += (f" -> refused {first_rule}, redrawn: "
                       + ("accepted" if answer.accepted is answer.redraw else "refused again"))
        print(f"[{index}/{len(model_cases)}] {case.case_id:<44} {status}{diff.get('line', '')}")

    corpus.verify_unchanged()
    report_mod.write_corpus_hashes(run_dir, corpus, when="after (unchanged)")

    # The aggregate's own verdict on every model answer, in one JVM start (FR-024). A kind the
    # validator does not take leaves the rate unmeasured, by name, for that kind (025 FR-019).
    aggregate = {"accepted": 0, "refusals_by_rule": {}, "shape_refusals": 0, "case_faults": 0,
                 "by_case": {}}
    refusals_measured = False
    unmet, unmeasured_kinds = [], []
    if state.shown_to_aggregate:
        # The answers already judged during the run (call 41) are not asked twice.
        batch = validate_mod.build_batch([(c, r) for c, r in state.shown_to_aggregate
                                          if c.case_id not in state.judged])
        unmet_by_screen = validate_mod.unmet_by_screen(config.keel_cloud, batch)
        unmet = list(unmet_by_screen.values())
        unmeasured_kinds = sorted(unmet_by_screen)
        # The chat pair's rules are restated by `instructions/chat.py` while the validator does not take them.
        own_rules = validate_mod.own_rules_untaken(config.keel_cloud, batch)
        batch = validate_mod.without_screens(batch, list(unmet_by_screen) + own_rules)
        try:
            report = validate_mod.run(config.keel_cloud, batch,
                                      run_dir / "batch.json", run_dir / "validation.json")
            combined = state.verdict_entries + list(report)
            (run_dir / "validation.json").write_text(json.dumps(combined, indent=2),
                                                     encoding="utf-8")
            aggregate = validate_mod.fold_in(combined)
            refusals_measured = not unmet and verdicts.down is None
        except Exception as exc:                  # noqa: BLE001 - unmeasured, never mis-measured
            print(f"the aggregate could not be asked: {exc}", file=sys.stderr)
            (run_dir / "validation.json").write_text(
                json.dumps({"unavailable": str(exc)}, indent=2), encoding="utf-8")
        if verdicts.down is not None:
            print(f"the aggregate could not be asked during the run, so nothing after that was "
                  f"redrawn and the rate is unmeasured: {verdicts.down}", file=sys.stderr)
        for reason in unmet:
            print(f"the aggregate was asked a shape it does not take: {reason}", file=sys.stderr)

    totals = score_mod.totals(state.calibration, state.respondent, state.interpret,
                              compare_scores, brief_scores=state.brief, errored=state.errored,
                              chat_scores=state.chat, schema_invalid=state.schema_invalid,
                              refusals_by_rule=aggregate["refusals_by_rule"],
                              shape_refusals=aggregate["shape_refusals"],
                              refusals_measured=refusals_measured,
                              refusals_shown=aggregate.get("shown", 0),
                              judge_calls=judge.call_count,
                              refusals_unmeasured_kinds=unmeasured_kinds)
    totals.update(redraw_totals(aggregate, scored_on="accepted"))
    totals["chipped_skipped"] = _chipped(corpus, cases)
    unmet += [u["reason"] for u in totals["compare_unmeasured"]]
    scorecard = {
        "marks_version": marks_mod.MARKS_VERSION,
        "marks": marks,
        "model": _model_block(args, facts, executor, pinned_model, state.reported_model,
                              table=table),
        "n_runs": args.n_runs,
        "registry_version": exported.registry.version,
        "aggregate": {k: v for k, v in aggregate.items() if k != "by_case"},
        "unmet_prerequisites": unmet,
        "judge_calls": judge.calls,
        "contract_manifest": exported.manifest,
        "compare": [_compare_json(s) for s in compare_scores],
        "calibration": [_question_json(s) for s in state.calibration],
        "respondent": [_question_json(s) for s in state.respondent],
        "interpret": [_interpret_json(s) for s in state.interpret],
        "brief": [_brief_json(s) for s in state.brief],
        "chat": [_chat_json(s) for s in state.chat],
        "chat_denominators": chat_denominators(cases),
        "totals": totals,
        "redraws": state.redraws,
        "spread": _spreads(state),
        "prompts": state.prompts,
    }
    report_mod.write_scorecard(run_dir, scorecard)

    judged = marks_mod.judge(totals, marks)
    verdict = {
        "scenario": "instructions",
        "baseline": bool(args.baseline),
        "host": args.host,
        "cli": facts.get("cli"),
        "cli_version": facts.get("cli_version"),
        "passed": bool(judged["passed"]) and state.errored == 0,
        "errored": state.errored,
        "marks": judged,
        "marks_version": marks_mod.MARKS_VERSION,
        "unmet_prerequisites": unmet,
        "model": scorecard["model"],
        "models_used": table.models_used(args.host) if table else None,
        "efforts_used": table.efforts_used(args.host) if table else None,
        "n_runs": args.n_runs,
        "cases": len(model_cases),
        "compare_rows": sum(1 for c in cases if c.kind == "COMPARE"),
        "duration_s": round(time.monotonic() - started, 3),
        # C-7: one of these, never more than one, and never one filled in from another.
        "total_cost_usd": (round(state.total_cost, 4)
                           if not (state.premium_seen or state.tokens_seen) else None),
        "total_premium_requests": round(state.total_premium, 4) if state.premium_seen else None,
        "total_tokens": dict(state.total_tokens) if state.tokens_seen else None,
    }
    report_mod.write_verdict(run_dir, verdict)
    report_mod.write_manifest(run_dir, _manifest(args, facts, executor, pinned_model,
                                                 state.reported_model, started_at, table=table,
                                                 exported=exported, corpus=corpus))
    versions = json.loads((run_dir / "versions.json").read_text(encoding="utf-8"))
    path = report_mod.render_report(run_dir, verdict=verdict, scorecard=scorecard,
                                    versions=versions, host=args.host)
    register = report_mod.render_register(
        run_dir,
        entries_by_market=report_mod.register_blocks(corpus, state.produced,
                                                     exported.registry, aggregate["by_case"],
                                                     redraws=state.redraws),
        paragraphs=report_mod.paragraph_blocks(corpus, state.brief),
        host=args.host, cli_version=facts.get("cli_version"), model=state.reported_model)

    print()
    print(f"verdict: {'PASSED' if verdict['passed'] else 'FAILED'}   "
          + " · ".join(f"{name} {_fmt_row(judged[name])}" for name in marks_mod.ROWS)
          + f" · schema-invalid {totals['schema_invalid']} · errored {state.errored}")
    print(f"report: {path}")
    print(f"register (unscored, for a person who knows the market): {register}")
    if state.premium_seen:
        print(f"cost: {state.total_premium:g} premium requests "
              f"(this host reports no dollars, and none are invented)")
    elif state.tokens_seen:
        print(f"cost: {state.total_tokens['input_tokens']} input + "
              f"{state.total_tokens['output_tokens']} output tokens (this host reports tokens "
              "against a plan; no dollars are invented)")
    else:
        print(f"cost: ${state.total_cost:.2f}")
    return 0 if verdict["passed"] else 1


#: What `totals` says about the redraws (call 41), and what the structural marks were scored on.
SCORED_ON_ACCEPTED = "accepted"
SCORED_ON_RAW = ("raw -- this bundle records no redraw (it predates judgement call 41), so every "
                 "structural mark is scored on the first draft")


def refused_twice(case, redrawn: bool, accepted: bool, refusals) -> str | None:
    """Decision 46: a `BRIEF` the aggregate refused, redrew and refused again shows the founder no
    paragraph -- the raw one is scored, and as a fault (every mark missed), never as a paragraph.
    `None` on every other screen (their structural marks read the raw answer's own faults) and on
    a brief that was accepted or never redrawn."""
    if case.screen != "BRIEF" or not redrawn or accepted:
        return None
    rules = [r.get("rule") or r.get("kind") for r in refusals or []]
    return f"refused twice by the aggregate ({' then '.join(str(r) for r in rules)}); no paragraph"


def redraw_totals(aggregate: dict, *, scored_on: str) -> dict:
    return {"redraws": int(aggregate.get("redraws") or 0),
            "redraws_accepted": int(aggregate.get("redraws_accepted") or 0),
            "second_refusals": int(aggregate.get("second_refusals") or 0),
            "scored_on": scored_on}


class _Verdicts:
    """The aggregate asked one answer at a time, during the run (call 41). `None` -- judge it at
    the end, redraw nothing -- for a screen the validator does not take, and for every answer
    after the validator could not be asked once (`down` says why, and the rate goes unmeasured)."""

    def __init__(self, keel_cloud, directory, taken: dict):
        self.keel_cloud, self.directory, self.taken = keel_cloud, directory, taken
        self.down = None

    def __call__(self, case, result, *, redraw: bool = False):
        if self.down is not None or not self.taken.get(case.screen):
            return None
        try:
            return validate_mod.verdict(self.keel_cloud, case, result, self.directory,
                                        redraw=redraw)
        except Exception as exc:                  # noqa: BLE001 - unmeasured, never mis-measured
            self.down = str(exc)
            return None


def _count_draft(state, answer) -> None:
    """One host call's spend and its two failure lines -- the first draft's and, since call 41,
    the redraw's too: a repair turn that errors or misses the envelope is counted like any call."""
    state.spend(answer)
    if answer.errored:
        state.errored += 1
    if answer.never_fit or (answer.outcome is not None and not answer.schema_valid) \
            or (answer.outcome is None and answer.schema_error and not answer.errored):
        state.schema_invalid += 1


class _RunState:
    """Everything one run accumulates, in one place."""

    def __init__(self):
        self.calibration, self.respondent, self.interpret, self.brief = [], [], [], []
        self.chat = []                   # MARKS_VERSION 17: the calibration chat's scores
        self.shown_to_aggregate = []
        # Call 41: the answers judged during the run, their report entries (the first draft's
        # under its case id, a redraw's under `<case_id>#redraw`), and one row a redraw.
        self.judged = set()
        self.verdict_entries = []
        self.redraws = []
        self.produced = {}               # entry -> {screen-or-subject: (case_id, result)}
        self.prompts = []
        self.errored = self.schema_invalid = 0
        self.total_cost = self.total_premium = 0.0
        self.premium_seen = self.tokens_seen = False
        self.total_tokens = {"input_tokens": 0, "output_tokens": 0}
        self.reported_model = None

    def record_verdicts(self, case, answer) -> None:
        real = [v for v in answer.verdicts if isinstance(v, dict) and v.get("case_id")]
        if not real:
            return
        self.judged.add(case.case_id)
        self.verdict_entries.extend(real)
        if answer.redraw is not None:
            self.redraws.append(redraw_row(case, answer))

    def spend(self, answer) -> None:
        self.total_cost += answer.total_cost_usd or 0.0
        if answer.premium_requests is not None:
            self.premium_seen = True
            self.total_premium += answer.premium_requests
        if answer.tokens:
            self.tokens_seen = True
            for key in self.total_tokens:
                self.total_tokens[key] += int(answer.tokens.get(key) or 0)
        self.reported_model = self.reported_model or answer.reported_model


def redraw_row(case, answer) -> dict:
    """One redraw, as the scorecard, the report and the register show it: raw -> accepted."""
    refusals = answer.refusals
    first = next((r for r in refusals if r.get("draft") == 1), {})
    second = next((r for r in refusals if r.get("draft") == 2), None)
    return {"case_id": case.case_id, "screen": case.screen, "run_index": case.run_index,
            "first_refusal": first, "repair": ((answer.redraw_payload or {}).get("context")
                                               or {}).get("repair"),
            "accepted": answer.accepted is answer.redraw, "second_refusal": second,
            "raw": answer.result, "redrawn": answer.redraw.result if answer.redraw else None}


def _produced_key(case) -> str:
    if case.kind == "CALIBRATION":
        return f"CALIBRATION_{case.subject}"
    if case.kind == "RESPONDENT":
        return f"RESPONDENT_{case.subject}"
    if case.kind == "READING":
        return f"INTERPRET/{case.subject}"
    return case.screen


def _score(case, entry, answer, failed, state, judge) -> dict:
    """One answered case: kept for the aggregate and the register, and scored where its kind has
    a scorer. Returns the case's `diff.json`, with a `line` the console prints beside it."""
    result = answer.result if (answer.schema_valid and answer.outcome == "COMPLETED") else None
    if result is not None:
        state.shown_to_aggregate.append((case, result))
        if case.run_index == 1:
            state.produced.setdefault(case.entry_id, {})[_produced_key(case)] = (case.case_id,
                                                                              result)
    diff = {"case_id": case.case_id, "kind": case.kind, "failed": failed,
            "outcome": answer.outcome, "result": answer.result}
    if answer.outcome == "NEEDS_INPUT":
        diff["needs_input"] = answer.questions
        # No case kind at v9 may legitimately ask: every screen is handed the corpus's own
        # inputs, so an ask is a failed case, counted, never softened (decision 14's reading).
        failed = failed or "NEEDS_INPUT on a screen this eval always supplies"
    if case.kind == "CALIBRATION":
        score = score_mod.score_calibration(case, entry, entry.registry, result, judge=judge,
                                            failed=failed)
        state.calibration.append(score)
        diff.update(faults=score.faults, coverage_passed=score.coverage_passed)
        diff["line"] = (f"  coverage {score.coverage_hit}/{score.coverage_of} · validity "
                        f"{score.validity_hit}/{score.validity_of} · leak {score.leak_clean}/"
                        f"{score.leak_of} (judged {score.leak_judged})")
    elif case.kind == "RESPONDENT":
        score = score_mod.score_respondent(case, entry, entry.registry, entry.plan(), result,
                                           judge=judge, failed=failed)
        state.respondent.append(score)
        diff.update(faults=score.faults, coverage_passed=score.coverage_passed)
        diff["line"] = (f"  coverage {score.coverage_hit}/{score.coverage_of} · validity "
                        f"{score.validity_hit}/{score.validity_of} · leak {score.leak_clean}/"
                        f"{score.leak_of} (judged {score.leak_judged})")
    elif case.kind == "READING":
        score = score_mod.score_interpret(case, entry, entry.person(case.subject), result,
                                          failed=failed)
        state.interpret.append(score)
        diff.update(golden=score.golden, produced=score.produced,
                    missing_ids=score.missing_ids, extra_ids=score.extra_ids)
        diff["line"] = (f"  {score.produced or 'no word'} (corpus {score.golden})")
    elif case.kind == "CHAT":
        score = chat_mod.score_chat(case.meta["chat_case"], case.meta["chat_block"],
                                    case.meta["idea_words"], answer.outcome, result,
                                    questions=len(answer.questions or []), failed=failed)
        state.chat.append(score)
        diff.update(faults=score.faults, marks=score.marks)
        diff["line"] = "  " + " · ".join(f"{name} {'yes' if verdict else 'no'}"
                                         for name, verdict in score.marks.items() if verdict is not None)
    elif case.kind == "FEEDBACK":
        score = chat_mod.score_feedback(case.meta["feedback"], answer.outcome, result, failed=failed)
        state.chat.append(score)
        diff.update(faults=score.faults, marks=score.marks)
        diff["line"] = f"  feedback_obeys {'yes' if score.marks['feedback_obeys'] else 'no'}"
    elif case.kind == "BRIEF":
        questions = answer.questions if answer.outcome == "NEEDS_INPUT" else None
        score = brief_mod.score_brief(case, entry, answer.result, outcome=answer.outcome,
                                      failed=None if questions is not None else failed,
                                      needs_input_questions=questions,
                                      registry=entry.registry)
        state.brief.append(score)
        diff.update(paragraph=score.paragraph, length=score.length, marks=score.marks,
                    findings=score.findings)
        diff["line"] = "  " + " · ".join(f"{name} {'yes' if score.marks.get(name) else 'no'}"
                                         for name in brief_mod.MARK_NAMES)
    return diff


def _chipped(corpus, cases) -> int:
    """The chipped stories of every entry this run built a case for: `GUESSED` by code, never read
    (call 33 amended) -- printed so the reader sees the denominator it was left out of."""
    entries = {c.entry_id for c in cases if c.kind == "READING"}
    return sum(1 for e in corpus.entries if e.id in entries
               for p in e.gate_yes() if p.chip is not None)


def _spreads(state) -> dict:
    return {
        "coverage": score_mod.spread(state.calibration + state.respondent,
                                     lambda s: s.coverage),
        "validity": score_mod.spread(state.calibration + state.respondent,
                                     lambda s: s.validity),
        "leak": score_mod.spread(state.calibration + state.respondent, lambda s: s.leak),
        "anchoring": score_mod.spread(state.interpret, lambda s: s.anchoring_accuracy),
        "brief": score_mod.spread(state.brief, lambda s: 1.0 if s.met else 0.0),
    }


def _fmt_row(row) -> str:
    if not row.get("measured"):
        return "not measured"
    value = row["value"]
    return str(value) if isinstance(value, int) else f"{value * 100:.1f}%"


def _fmt(value) -> str:
    return "—" if value is None else f"{value * 100:.1f}%"


def _model_block(args, facts, executor, pinned_model, reported_model, table=None) -> dict:
    """Everything a mark is only comparable within (spec 014 FR-005).

    `job_max_turns` and `job_budget_usd` are read with `getattr`, and that is not defensiveness:
    `CopilotExecutor` **has neither** (C-7). `None` here means "this host has no such cap".
    """
    return {
        "host": args.host,
        "cli": facts.get("cli"),
        "cli_version": facts.get("cli_version"),
        "pinned_model": pinned_model,
        "reported_model": reported_model,
        "models_used": table.models_used(args.host) if table else None,
        "efforts_used": table.efforts_used(args.host) if table else None,
        "models_source": table.source if table else None,
        "job_timeout_seconds": getattr(executor, "timeout_seconds", None),
        "job_max_turns": getattr(executor, "max_turns", None),
        "job_budget_usd": getattr(executor, "budget_usd", None),
        "max_ai_credits": getattr(executor, "max_ai_credits", None),
        "judge": "off" if args.no_judge else "on",
        "judge_host": "off" if args.no_judge else "claude",
    }


def _manifest(args, facts, executor, pinned_model, reported_model, started_at,
              table=None, exported=None, corpus=None) -> dict:
    """`manifest.json`: what this run was, in the one file that is written before the first call."""
    return {
        "scenario": "instructions",
        "why": getattr(args, "why_record", None),
        "baseline": bool(args.baseline),
        "host": args.host,
        "cli": {"binary": facts.get("cli"), "version": facts.get("cli_version")},
        "model": {"pinned": pinned_model, "reported": reported_model,
                  "per_class": table.models_used(args.host) if table else None,
                  "table": table.source if table else None},
        "effort": {"per_class": table.efforts_used(args.host) if table else None,
                   "how": ("the job's own `effort` key, keel-cloud model-routing-design.md §5"
                           if table and table.efforts else
                           "not pinned -- every CLI answered at its own default")},
        "marks_version": marks_mod.MARKS_VERSION,
        "registry_version": getattr(getattr(exported, "registry", None), "version", None),
        "corpus_digests": ({Path(p).name: d for p, d in sorted(corpus.hashes.items())}
                           if corpus is not None else None),
        "n_runs": args.n_runs,
        "filter": args.filter,
        "judge": "off" if args.no_judge else "on",
        "caps": {"job_timeout_seconds": getattr(executor, "timeout_seconds", None),
                 "job_max_turns": getattr(executor, "max_turns", None),
                 "job_budget_usd": getattr(executor, "budget_usd", None),
                 "max_ai_credits": getattr(executor, "max_ai_credits", None)},
        "started_at": started_at,
    }


def _compare_json(score) -> dict:
    return {"case_id": score.case_id, "entry_id": score.entry_id, "checks": score.checks,
            "agreed": score.agreed, "compare_correctness": score.compare_correctness,
            "mismatches": score.mismatches, "reported_diffs": score.reported_diffs,
            "measured": score.measured, "reason": score.reason}


def _question_json(score) -> dict:
    return {k: v for k, v in vars(score).items() if not k.startswith("_")}


def _interpret_json(score) -> dict:
    return {k: v for k, v in vars(score).items() if not k.startswith("_")}


def _chat_json(score) -> dict:
    return {"case_id": score.case_id, "kind": score.kind, "marks": score.marks,
            "faults": [list(f) for f in score.faults]}


def _brief_json(score) -> dict:
    return {"case_id": score.case_id, "entry_id": score.entry_id, "run_index": score.run_index,
            "reading": score.reading, "paragraph": score.paragraph, "length": score.length,
            "marks": score.marks,
            "findings": score.findings, "phrasing": score.phrasing,
            "met": score.met, "failed": score.failed,
            "needs_input": score.needs_input,
            "needs_input_questions": score.needs_input_questions}


if __name__ == "__main__":
    raise SystemExit(main())
