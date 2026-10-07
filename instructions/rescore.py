"""Re-score a finished run from its own bundle, under today's marks (spec 009, run-bundle
contract's "re-reading" promise; spec 029 FR-004, research R11).

    python -m instructions.rescore runs/<id> [--no-judge]

The bundle already holds everything a score is made of: the produced result in every
`cases/**/envelope.json`, the contract and the registry it was judged against (`contracts/`,
including `dimension-registry.json`), and the engine's input (`compare/*.in.json`). So a rubric
change within a version's subjects does not mean spending the money again --
`scorecard-v<MARKS_VERSION>.json` is written **beside** the original, never over it.

**Across the v8 → v9 bump it means nothing, and it refuses** (judgement call 28; FR-004). A v8
bundle holds answers to screens v9 does not have -- three assumption screens and a questionnaire --
scored against a corpus revision 3 no longer carries. `marks_version` is read **first**, before the
corpus is loaded, so such a bundle is refused in one line, by name, with the reason, and no file of
it is touched.

For a v9 bundle the cases are rebuilt with the same builders and the same exported key lists the
run used, every envelope is scored again by the run's own `_score`, and `COMPARE` is re-run from
the bundle's own engine input (it spends nothing).
"""

from __future__ import annotations

import argparse
import json
import sys
import types
from pathlib import Path

from stack.config import load_config

from . import compare as compare_mod
from . import contract as contract_mod
from . import corpus as corpus_mod
from . import judge as judge_mod
from . import marks as marks_mod
from . import prompts as prompts_mod
from . import report as report_mod
from . import run as run_mod
from . import score as score_mod
from . import validate as validate_mod

#: The one sentence a pre-v9 bundle is refused with (FR-004, SC-004).
CROSSED_THE_BUMP = "answered on screens v9 does not have, against corpus r2"


class _SilentRuntime:
    """Enough of keel-runtime's executor to rebuild a case without rendering a prompt: the bundle
    keeps every prompt it actually sent in `cases/**/prompt.txt`."""

    @staticmethod
    def InferenceRequest(**kw):                        # noqa: N802 - mirrors the real dataclass
        return types.SimpleNamespace(**kw)

    @staticmethod
    def build_prompt(request):
        return ""


def _envelopes(run_dir: Path):
    for path in sorted(run_dir.glob("cases/**/envelope.json")):
        yield json.loads(path.read_text(encoding="utf-8")), path.parent


def refusal(run_dir: Path, original: dict) -> str | None:
    """The reason this bundle cannot be re-scored at `MARKS_VERSION`, or `None` when it can."""
    version = original.get("marks_version")
    if not isinstance(version, int) or version < 9:
        return (f"{run_dir.name} was scored at marks_version {version}: {CROSSED_THE_BUMP}. "
                "Not re-scored (spec 029 FR-004; judgement call 28) -- a v8 number is a "
                "measurement of a product v9 does not judge, and the only v9 number is a v9 run.")
    return None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="instructions.rescore", description=__doc__)
    parser.add_argument("run_dir")
    parser.add_argument("--no-judge", action="store_true")
    args = parser.parse_args(argv)

    run_dir = Path(args.run_dir)
    original = json.loads((run_dir / "scorecard.json").read_text(encoding="utf-8"))
    reason = refusal(run_dir, original)
    if reason:
        print(reason, file=sys.stderr)
        return 2

    host = _host_of(run_dir, original)
    config = load_config()
    exported = contract_mod.read(run_dir / "contracts")
    corpus = corpus_mod.load(config.keel_cloud).bind(exported.registry)
    judge = judge_mod.NoJudge() if args.no_judge else judge_mod.Judge()

    cases = {}
    for entry in corpus.entries:
        instructions = {screen: "" for screen in run_mod.SCREENS}
        for case in prompts_mod.build_cases(entry, exported, instructions, _SilentRuntime,
                                            n_runs=max(int(original.get("n_runs") or 1), 1)):
            cases[case.case_id] = case

    state = run_mod._RunState()
    for envelope, _directory in _envelopes(run_dir):
        case = cases.get(envelope.get("case_id"))
        if case is None:
            continue
        answer = types.SimpleNamespace(
            outcome=envelope.get("outcome"), schema_valid=bool(envelope.get("schema_valid")),
            schema_error=envelope.get("schema_error"), error=envelope.get("error"),
            result=envelope.get("result"), questions=envelope.get("questions"),
            errored=bool(envelope.get("error")))
        failed = answer.error or (answer.schema_error if not answer.schema_valid else None)
        if answer.errored and "never fit its shape" not in str(answer.error):
            state.errored += 1
        run_mod._score(case, corpus.by_id(case.entry_id), answer, failed, state, judge)

    compare_scores = []
    for in_path in sorted((run_dir / "compare").glob("*.in.json")):
        entry_input = json.loads(in_path.read_text(encoding="utf-8"))
        entry = corpus.by_id(entry_input.get("entry"))
        if entry is None:
            continue
        case = cases.get(f"{entry.id}/COMPARE")
        try:
            produced = compare_mod.run(config.keel_cloud, entry_input, in_path,
                                       in_path.with_name(f"{entry.id}.rescore.out.json"))
            raw = compare_mod.diff(entry.expected, produced, entry=entry)
        except compare_mod.EngineUnavailable as why:
            raw = compare_mod.unmeasured(entry.id, str(why))
        compare_scores.append(score_mod.score_compare(case, entry, raw))

    validation = run_dir / "validation.json"
    measured = validation.is_file() and "unavailable" not in validation.read_text(encoding="utf-8")
    aggregate = {"accepted": 0, "refusals_by_rule": {}, "shape_refusals": 0}
    if measured:
        try:
            aggregate = validate_mod.fold_in(json.loads(validation.read_text(encoding="utf-8")))
        except Exception as exc:                  # noqa: BLE001 - unmeasured, never mis-measured
            print(f"validation.json could not be folded in: {exc}", file=sys.stderr)
            measured = False
    measured = measured and not original.get("unmet_prerequisites")

    totals = score_mod.totals(state.calibration, state.respondent, state.interpret,
                              compare_scores, brief_scores=state.brief, errored=state.errored,
                              refusals_by_rule=aggregate["refusals_by_rule"],
                              shape_refusals=aggregate["shape_refusals"],
                              refusals_measured=measured,
                              refusals_shown=aggregate["accepted"]
                              + sum(aggregate["refusals_by_rule"].values()),
                              judge_calls=judge.call_count)
    marks = marks_mod.load()
    judged = marks_mod.judge(totals, marks)
    scorecard = {
        "marks_version": marks_mod.MARKS_VERSION,
        "rescored_from": original.get("marks_version"),
        "marks": marks,
        "model": original.get("model"),
        "n_runs": original.get("n_runs"),
        "registry_version": exported.registry.version,
        "contract_manifest": original.get("contract_manifest"),
        "compare": [run_mod._compare_json(s) for s in compare_scores],
        "calibration": [run_mod._question_json(s) for s in state.calibration],
        "respondent": [run_mod._question_json(s) for s in state.respondent],
        "interpret": [run_mod._interpret_json(s) for s in state.interpret],
        "brief": [run_mod._brief_json(s) for s in state.brief],
        "totals": totals,
        "judge_calls": judge.calls,
        "spread": run_mod._spreads(state),
        "prompts": original.get("prompts", []),
    }
    out = run_dir / f"scorecard-v{marks_mod.MARKS_VERSION}.json"
    out.write_text(json.dumps(scorecard, indent=2, default=str), encoding="utf-8")
    if state.brief:
        report_mod.render_register(
            run_dir, entries_by_market={},
            paragraphs=report_mod.paragraph_blocks(corpus, state.brief), host=host,
            cli_version=(original.get("model") or {}).get("cli_version"),
            model=(original.get("model") or {}).get("reported_model"),
            filename=f"register-v{marks_mod.MARKS_VERSION}.html")

    print(f"re-scored {run_dir.name} ({host}) under MARKS_VERSION {marks_mod.MARKS_VERSION} "
          f"(was {original.get('marks_version')})")
    for name in marks_mod.ROWS:
        print(f"  {name:<20} {run_mod._fmt_row(judged[name])}")
    print(f"  passed     {judged['passed']}")
    print(f"  written    {out}")
    return 0


def _host_of(run_dir: Path, original: dict) -> str:
    """The host this bundle was answered by: its `manifest.json`, else its scorecard's model
    block, else `claude` -- which is what every bundle taken before spec 014 was."""
    manifest_path = run_dir / "manifest.json"
    if manifest_path.is_file():
        try:
            host = json.loads(manifest_path.read_text(encoding="utf-8")).get("host")
        except ValueError:
            host = None
        if host:
            return host
    return (original.get("model") or {}).get("host") or "claude"


if __name__ == "__main__":
    raise SystemExit(main())
