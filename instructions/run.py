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
                     asked, respondent, reading, compare. A needle matching nothing says so
                     and spends nothing. Spec 105: a needle that names a keel-cloud back-test
                     entry (`-k 08-fresco/PROBLEM_INTERPRET`) or a planted probe
                     (`-k 169-banking-gaming`) screens it beside the golden corpus
                     (`instructions/screen_entries.py`); a kind word and the full eval do not.
    -n N             runs per model case (default 3)
    --marks FILE     an alternative marks file
    --models FILE    a model-routing table pinning each job class -- context, frame, calibration,
                     asked, respondent, reading -- through the job's own `model` key, exactly as
                     the cloud sends it; `exported` means the table keel-cloud's own exporter
                     wrote beside the contracts. Never beside `KEEL_<HOST>_MODEL`.

**Read a prompt before spending anything.** The dry run exists for exactly that. It does more: the
four deterministic marks cost nothing, so the dry run measures them for real and writes them into a
bundle -- `compare_correctness` (keel-cloud's engine, call 34), since `MARKS_VERSION` 18
`spoken_form` and `brief_facts` (keel-cloud's corpus tests' composed wording and facts, calls 79 and
82), and since 20 `report_overview` (the Overview those facts draw, call 117) -- and every model-scored mark beside
them is *not measured*, so the dry verdict is
`passed: false` by construction and says why.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from stack.config import REPO_ROOT, load_config

from . import brief_facts as brief_facts_mod
from . import cloud_corpus as cloud_mod
from . import compare as compare_mod
from . import contract as contract_mod
from . import corpus as corpus_mod
from . import instruction as instruction_mod
from . import judge as judge_mod
from . import marks as marks_mod
from . import models as models_mod
from . import overview as overview_mod
from . import prompts as prompts_mod
from . import report as report_mod
from . import runner as runner_mod
from . import screen_entries as screen_mod
from . import score as score_mod
from . import spoken as spoken_mod
from . import validate as validate_mod

# Rough, and honest about being rough: the founder's own account pays, and the point of printing a
# number before the first call is that nobody is surprised by the size of the bill.
COST_PER_CASE_ESTIMATE_USD = 0.04

#: The eight model screens (spec 029 FR-016; spec 040). `COMPARE` is not one: it is never sent.
SCREENS = contract_mod.MODEL_SCREENS

#: `-k` kind words (research R6): each selects by `Case.kind` exactly. `interpret` is deliberately
#: not one -- it would be ambiguous between the three interpretation screens and the reads; the
#: slash form `03-lullaby/INTERPRET` selects the reads.
KIND_WORDS = {"context": "CONTEXT", "frame": "FRAME", "calibration": "CALIBRATION",
              "asked": "ASKED", "respondent": "RESPONDENT", "reading": "READING", "compare": "COMPARE"}


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


def _all_cases(corpus, exported, instructions, executor_module, args, extras=None) -> list:
    """The golden corpus's cases, the needle applied -- and, spec 105 FR-3, the cases of the back-test entries and
    probes the needle names (`extras`, `screen_entries.load`), after them."""
    cases = []
    for entry in corpus.entries:
        cases.extend(prompts_mod.build_cases(entry, exported, instructions, executor_module,
                                             n_runs=args.n_runs, host=args.host))
    selected = select(cases, args.filter)
    if extras:
        selected += screen_mod.build_cases(extras, exported, instructions, executor_module, needle=args.filter,
                                           n_runs=args.n_runs, host=args.host)
    return selected


def _golden(cases) -> list:
    """The cases drawn from the golden corpus -- what the deterministic marks are read over (spec 105 FR-3: a
    back-test entry or a probe has no golden expectations, and no corpus-test facts)."""
    return [c for c in cases if not screen_mod.is_extra(c)]


def _screen_entries_line(extras) -> str:
    backtest = ", ".join(e.id for e in extras.backtest) or "none"
    probes = ", ".join(p.id for p in extras.probes) or "none"
    return f"screened beside the golden corpus (spec 105): back-test entries {backtest} · probes {probes}"


def _cloud(config, corpus, registry, run_dir):
    """keel-cloud's composed wording and facts (calls 79, 82, 84), asked once and kept in the bundle -- or
    `None` with the reason printed, when keel-cloud's corpus tests cannot be run (both marks then unmeasured)."""
    try:
        cloud = cloud_mod.produce(config.keel_cloud, corpus=corpus, registry=registry)
        cloud_mod.copy_into(run_dir, config.keel_cloud)
        return cloud, None
    except cloud_mod.CloudCorpusUnavailable as reason:
        print(f"[cloud-corpus] NOT read -- {str(reason).splitlines()[0]}")
        return None, str(reason)


def deterministic(corpus, registry, cases, cloud, reason=None):
    """`spoken_form`, `brief_facts` and `report_overview` over the entries the selected cases are drawn from (zero
    spend)."""
    entries = {c.entry_id for c in cases}
    if cloud is None:
        why = reason or cloud_mod.PREREQUISITE
        return (spoken_mod.unmeasured(why),
                [brief_facts_mod.unmeasured(e, why) for e in sorted(entries)],
                [overview_mod.unmeasured(e, why) for e in sorted(entries)])
    spoken = spoken_mod.score(cloud, corpus, entry_ids=entries)
    facts = [brief_facts_mod.compare(e, registry, cloud.facts.get(e.id)) for e in corpus.entries
             if e.id in entries]
    overview = [overview_mod.compare(e, registry, cloud.facts.get(e.id)) for e in corpus.entries
                if e.id in entries]
    print(f"[spoken] {spoken.clean} of {spoken.units} composed items and faces keep the guidelines"
          f" · {len(spoken.known)} known corpus items named apart (call 81)")
    for fault in spoken.faults:
        print(f"[spoken]   {fault['entry']} {fault['key']} {fault['unit']}: {fault['evidence']}")
    for score in facts:
        line = (f"{score.agreed} of {score.checks} agreed · {len(score.reported_diffs)} reported"
                if score.measured else f"NOT measured -- {score.reason}")
        print(f"[facts]  {score.entry_id:<44} {line}")
    for score in overview:
        line = (f"{score.agreed} of {score.checks} agreed" if score.measured else f"NOT measured -- {score.reason}")
        print(f"[overview] {score.entry_id:<42} {line}")
    return spoken, facts, overview


def _compare(config, corpus, cases, run_dir) -> list:
    """Every selected `COMPARE` row, shelled to keel-cloud's engine at build time -- the dry path
    and the real path are one code path (research R7). Both files stay in the bundle."""
    scores = []
    for case in cases:
        if case.kind != "COMPARE":
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
    """The export, the registry bound to the corpus, keel-cloud's corpus files, the cases selected -- or a
    refusal by name. Spec 105 FR-3: the back-test entries and probes the needle names, read beside the corpus
    (empty for the full eval and a kind word), their cases after the golden ones."""
    exported = contract_mod.export(config.keel_cloud, contracts_dir)
    corpus.bind(exported.registry)
    extras = screen_mod.load(config.keel_cloud, args.filter, golden_ids=[e.id for e in corpus.entries])
    cloud, reason = _cloud(config, corpus, exported.registry, Path(contracts_dir).parent)
    instructions = _instructions_for(config)
    cases = _all_cases(corpus, exported, instructions, executor_module, args, extras=extras)
    return exported, instructions, cases, cloud, reason, extras


def _counts(cases) -> dict:
    out = {kind: 0 for kind in prompts_mod.KINDS}
    for case in cases:
        out[case.kind] = out.get(case.kind, 0) + 1
    return out


def denominators(cases) -> dict:
    """Spec 030 US3, call 47: what each structural mark is counted over, per entry and per N --
    read off the cases the registry and the entries built (`registry_slice`, `plan`, the items an
    `ASKED` case is handed), never typed. A dry run has no answer to score, so `dimension_coverage`,
    `option_validity` and `no_leak` stay unmeasured there (call 13); what it can show, and does, is
    the denominator each would have. Coverage counts one a dimension (calibration), one a planned
    item (respondent) and one an index handed (asked); validity one a dimension, the gate alone
    (call 83) and one a face; `sweep_a` is the PROBLEM job's written entries and the gate's clause,
    `sweep_b` the gate's clause (the case's `swept`)."""
    out = {}
    for case in cases:
        if case.run_index != 1 or case.kind not in ("CALIBRATION", "RESPONDENT", "ASKED"):
            continue
        row = out.setdefault(case.entry_id, {"calibration": 0, "respondent": {}, "asked": 0,
                                             "validity": 0, "sweep_a": 0, "sweep_b": 0})
        swept = len(case.meta.get("swept") or [])
        if case.kind == "CALIBRATION":
            row["calibration"] += len(case.meta.get("registry_slice") or [])
            row["validity"] += len(case.meta.get("registry_slice") or [])
            if case.meta.get("vector") == "PROBLEM":
                row["sweep_a"] += swept
            continue
        if case.kind == "ASKED":
            row["asked"] += len(case.meta.get("items") or [])
            row["validity"] += len(case.meta.get("items") or [])
            continue
        plan = list(case.meta.get("plan") or [])
        link = case.meta.get("link") or corpus_mod.LINK_PRIMARY
        row["respondent"][link] = row["respondent"].get(link, 0) + len(plan)
        row["validity"] += sum(1 for k in plan if k == "problem.prevalence")
        row["sweep_a"] += swept
        row["sweep_b"] += swept
    return out


def _denominator_line(rows: dict) -> str:
    calibration = sum(r["calibration"] for r in rows.values())
    respondent = sum(sum(r["respondent"].values()) for r in rows.values())
    asked = sum(r["asked"] for r in rows.values())
    validity = sum(r["validity"] for r in rows.values())
    sweeps = sum(r["sweep_a"] + r["sweep_b"] for r in rows.values())
    return (f"denominators read off the registry, per N: dimension_coverage {calibration} "
            f"calibration + {respondent} respondent + {asked} asked · option_validity {validity} · "
            f"no_leak {sweeps} sweeps")


def _dry_run(config, corpus, executor_module, facts, args) -> int:
    """Everything a real run does, up to the point where it would cost money -- and `COMPARE`,
    which costs nothing, done for real."""
    run_dir = report_mod.start_bundle(config, baseline=args.baseline, host=args.host)
    try:
        exported, instructions, cases, cloud, cloud_reason, extras = _prepare(
            config, corpus, executor_module, args, run_dir / "contracts")
    except (contract_mod.ContractUnavailable, corpus_mod.CorpusError) as reason:
        print(f"instruction eval cannot start: {reason}", file=sys.stderr)
        return 2
    if not cases:
        print(f"no case matches -k {args.filter!r}; nothing was built and nothing was spent")
        return 2
    if extras:
        print(_screen_entries_line(extras))
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
    spoken, facts_scores, overview_scores = deterministic(corpus, exported.registry, _golden(cases), cloud,
                                                          cloud_reason)
    marks = marks_mod.load(args.marks)
    totals = score_mod.totals(compare_scores=compare_scores, spoken_score=spoken,
                              facts_scores=facts_scores, overview_scores=overview_scores)
    scorecard = {
        "marks_version": marks_mod.MARKS_VERSION, "marks": marks, "dry_run": True,
        "model": {"host": args.host, "cli": facts.get("cli"), "cli_version": None},
        "n_runs": args.n_runs, "registry_version": exported.registry.version,
        "contract_manifest": exported.manifest,
        "compare": [_compare_json(s) for s in compare_scores],
        "spoken": _spoken_json(spoken),
        "brief_facts": [_facts_json(s) for s in facts_scores],
        "report_overview": [_overview_json(s) for s in overview_scores],
        "totals": totals, "spread": {}, "prompts": [],
        "denominators": denominators(cases),
        # MARKS_VERSION 21 (call 121): the readers' scores, reported from committed score files, never gating.
        "read": marks_mod.read_rows(e.id for e in corpus.entries),
        # Spec 105 FR-3: what the screen read beside the golden corpus, the probes apart from the entries.
        "screen_entries": extras.record(),
    }
    report_mod.write_scorecard(run_dir, scorecard)
    judged = marks_mod.judge(totals, marks)
    counts = _counts(cases)
    verdict = {"scenario": "instructions", "dry_run": True, "host": args.host,
               "passed": False, "marks": judged, "marks_version": marks_mod.MARKS_VERSION,
               "unmet_prerequisites": [u["reason"] for u in totals["compare_unmeasured"]]
               + ([totals["spoken_unmeasured"]] if totals.get("spoken_unmeasured") else []),
               "why_not_passed": "a dry run calls no model: every model-scored mark is "
                                 "unmeasured, and an unmeasured mark is not met (call 13)",
               "cases": len(model_cases), "compare_rows": counts["COMPARE"],
               "n_runs": args.n_runs, "total_cost_usd": 0.0}
    report_mod.write_verdict(run_dir, verdict)

    print("-" * 100)
    print(f"{len(model_cases)} cases: {counts['CONTEXT'] + counts['FRAME']} interpretation, "
          f"{counts['CALIBRATION']} calibration, {counts['ASKED']} asked, {counts['RESPONDENT']} respondent, "
          f"{counts['READING']} interpret, N={args.n_runs} runs per case "
          f"-- plus {counts['COMPARE']} COMPARE row(s), which are never a call")
    compare_line = (f"{totals['compare_agreed']} of {totals['compare_checks']}"
                    if totals["compare_measured"] else "NOT measured")
    spoken_line = (f"{totals['spoken_clean']} of {totals['spoken_units']} ({totals['spoken_known']} known apart)"
                   if totals["spoken_measured"] else "NOT measured")
    facts_line = (f"{totals['brief_facts_agreed']} of {totals['brief_facts_checks']}"
                  if totals["brief_facts_measured"] else "NOT measured")
    overview_line = (f"{totals['report_overview_agreed']} of {totals['report_overview_checks']}"
                     if totals["report_overview_measured"] else "NOT measured")
    print(f"compare_correctness: {compare_line} · spoken_form: {spoken_line} · brief_facts: {facts_line} · "
          f"report_overview: {overview_line} · every model mark unmeasured · passed: false")
    for entry_id, row in scorecard["denominators"].items():
        links = " + ".join(f"{n} {link}" for link, n in row["respondent"].items())
        print(f"  {entry_id:<20} calibration {row['calibration']} · asked {row['asked']} · respondent {links} · "
              f"validity {row['validity']} · no_leak sweep A {row['sweep_a']} + sweep B {row['sweep_b']}")
    print(_denominator_line(scorecard["denominators"]))
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
        exported, instructions, cases, cloud, cloud_reason, extras = _prepare(
            config, corpus, executor_module, args, run_dir / "contracts")
    except (contract_mod.ContractUnavailable, corpus_mod.CorpusError) as reason:
        print(f"instruction eval cannot start: {reason}", file=sys.stderr)
        return 2
    if not cases:
        print(f"no case matches -k {args.filter!r}; nothing was built and nothing was spent")
        return 2
    if extras:
        print(_screen_entries_line(extras))
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
    # before the first paid call rather than after the last. The two v18 deterministic marks likewise.
    compare_scores = _compare(config, corpus, cases, run_dir)
    spoken, facts_scores, overview_scores = deterministic(corpus, exported.registry, _golden(cases), cloud,
                                                          cloud_reason)

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
        entry = corpus.by_id(case.entry_id)
        for draft in (answer, answer.redraw):
            if draft is not None:
                _count_draft(state, draft)
        scored = answer.scored
        failed = scored.error or (scored.schema_error if not scored.schema_valid else None)
        diff = _score(case, entry, scored, failed, state, judge)
        _score_probe(case, answer, diff, state)
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
    extras.verify_unchanged()
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
        batch = validate_mod.without_screens(batch, unmet_by_screen)
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
                              compare_scores, asked_scores=state.asked,
                              spoken_score=spoken, facts_scores=facts_scores, overview_scores=overview_scores,
                              errored=state.errored, schema_invalid=state.schema_invalid,
                              refusals_by_rule=aggregate["refusals_by_rule"],
                              shape_refusals=aggregate["shape_refusals"],
                              refusals_measured=refusals_measured,
                              refusals_shown=aggregate.get("shown", 0),
                              judge_calls=judge.call_count,
                              refusals_unmeasured_kinds=unmeasured_kinds)
    totals.update(redraw_totals(aggregate, scored_on="accepted"))
    totals["chipped_skipped"] = _chipped(corpus, cases)
    unmet += [u["reason"] for u in totals["compare_unmeasured"]]
    unmet += [totals["spoken_unmeasured"]] if totals.get("spoken_unmeasured") else []
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
        "spoken": _spoken_json(spoken),
        "brief_facts": [_facts_json(s) for s in facts_scores],
        "report_overview": [_overview_json(s) for s in overview_scores],
        "calibration": [_question_json(s) for s in state.calibration],
        "asked": [_question_json(s) for s in state.asked],
        "respondent": [_question_json(s) for s in state.respondent],
        "interpret": [_interpret_json(s) for s in state.interpret],
        "totals": totals,
        "redraws": state.redraws,
        "spread": _spreads(state),
        "prompts": state.prompts,
        # MARKS_VERSION 21 (call 121): the readers' scores, reported from committed score files, never gating.
        "read": marks_mod.read_rows(e.id for e in corpus.entries),
        # Spec 105 FR-3: what the screen read beside the golden corpus, and each probe case's mark, apart from the
        # entries' marks -- a probe is no entry and its mark moves no row of the marks file.
        "screen_entries": extras.record(),
        "probes": state.probes,
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
        self.calibration, self.respondent, self.interpret = [], [], []
        self.asked = []
        self.shown_to_aggregate = []
        # Call 41: the answers judged during the run, their report entries (the first draft's
        # under its case id, a redraw's under `<case_id>#redraw`), and one row a redraw.
        self.judged = set()
        self.verdict_entries = []
        self.redraws = []
        self.produced = {}               # entry -> {screen-or-subject: (case_id, result)}
        self.probes = []                 # spec 105 FR-3: one probe mark a probe case
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
    if case.kind == "ASKED":
        return f"ASKED_{case.subject}"
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
    elif case.kind == "ASKED":
        score = score_mod.score_asked(case, entry, entry.registry, result, failed=failed)
        state.asked.append(score)
        diff.update(faults=score.faults, coverage_passed=score.coverage_passed)
        diff["line"] = (f"  coverage {score.coverage_hit}/{score.coverage_of} · validity "
                        f"{score.validity_hit}/{score.validity_of}")
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
    return diff


def _score_probe(case, answer, diff, state) -> dict | None:
    """Spec 105 FR-3: a probe case's mark, read off its FIRST turn (`answer`, never a redraw): NEEDS_INPUT with one
    question naming the planted term and offering two readings, else a fault. Written into the case's `diff.json`
    (`source`, `probe`, `failed`, the console `line`) and kept on `state.probes`; `None` on every other case (a
    back-test case's diff only says where it came from)."""
    source = (case.meta or {}).get("source")
    if source:
        diff["source"] = source
    plant = screen_mod.plant_of(case)
    if plant is None:
        return None
    mark = screen_mod.probe_mark(case.entry_id, plant, outcome=answer.outcome, questions=answer.questions,
                                 result=answer.result)
    mark = {"case_id": case.case_id, "run_index": case.run_index, **mark}
    diff["probe"] = mark
    diff["failed"] = diff.get("failed") or (None if mark["held"] else "probe: " + "; ".join(mark["faults"]))
    diff["line"] = screen_mod.probe_line(mark)
    state.probes.append(mark)
    return mark


def _chipped(corpus, cases) -> int:
    """The chipped stories of every entry this run built a case for: `GUESSED` by code, never read
    (call 33 amended) -- printed so the reader sees the denominator it was left out of."""
    entries = {c.entry_id for c in cases if c.kind == "READING"}
    return sum(1 for e in corpus.entries if e.id in entries
               for p in e.gate_yes() if p.chip is not None)


def _spreads(state) -> dict:
    questions = state.calibration + state.asked + state.respondent
    return {
        "coverage": score_mod.spread(questions, lambda s: s.coverage),
        "validity": score_mod.spread(questions, lambda s: s.validity),
        "leak": score_mod.spread(state.calibration + state.respondent, lambda s: s.leak),
        "anchoring": score_mod.spread(state.interpret, lambda s: s.anchoring_accuracy),
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


def _spoken_json(score) -> dict:
    return {"measured": score.measured, "reason": score.reason, "units": score.units, "clean": score.clean,
            "spoken_form": score.spoken_form, "faults": score.faults, "known": score.known,
            "missing_known": [list(k) for k in score.missing_known], "by_entry": score.by_entry}


def _facts_json(score) -> dict:
    return {"entry_id": score.entry_id, "checks": score.checks, "agreed": score.agreed,
            "brief_facts": score.correctness, "mismatches": score.mismatches,
            "reported_diffs": score.reported_diffs, "measured": score.measured, "reason": score.reason}


def _question_json(score) -> dict:
    return {k: v for k, v in vars(score).items() if not k.startswith("_")}


def _interpret_json(score) -> dict:
    return {k: v for k, v in vars(score).items() if not k.startswith("_")}


def _overview_json(score) -> dict:
    return {"entry_id": score.entry_id, "checks": score.checks, "agreed": score.agreed,
            "report_overview": score.correctness, "mismatches": score.mismatches,
            "measured": score.measured, "reason": score.reason}


if __name__ == "__main__":
    raise SystemExit(main())
