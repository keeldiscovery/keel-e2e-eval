"""Re-score a finished run from its own bundle, under today's marks (spec 009, run-bundle
contract's "re-reading" promise).

    python -m instructions.rescore runs/<id> [--no-judge]

The bundle already holds everything a score is made of: the produced result in every
`cases/**/envelope.json`, the corpus that judged it, and the contract it was judged against. So a
rubric change does not mean spending the money again — `scorecard.json` is rewritten as
`scorecard-v<MARKS_VERSION>.json` **beside** the original rather than over it, because two
scorecards under two rubrics are the evidence that the rubric changed, and one of them overwritten
is not.

The one thing it cannot recover is a call that never happened: a run taken before
`instructions/validate.py` existed has no aggregate verdict, and re-scoring says so rather than
inventing a zero.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from stack.config import load_config

from . import brief as brief_mod
from . import context as context_mod
from . import contract as contract_mod
from . import corpus as corpus_mod
from . import judge as judge_mod
from . import marks as marks_mod
from . import prompts as prompts_mod
from . import report as report_mod
from . import score as score_mod


def _cases(run_dir: Path):
    for envelope_path in sorted(run_dir.glob("cases/*/*/*/envelope.json")):
        yield json.loads(envelope_path.read_text(encoding="utf-8")), envelope_path.parent


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="instructions.rescore", description=__doc__)
    parser.add_argument("run_dir")
    parser.add_argument("--no-judge", action="store_true")
    args = parser.parse_args(argv)

    run_dir = Path(args.run_dir)
    original = json.loads((run_dir / "scorecard.json").read_text(encoding="utf-8"))
    config = load_config()
    corpus = corpus_mod.load(config.keel_cloud)
    judge = judge_mod.NoJudge() if args.no_judge else judge_mod.Judge()

    people = {(e.id, p.person): p for e in corpus.entries for p in e.people()}
    reading_scores, assumption_scores, brief_scores = [], [], []
    # MARKS_VERSION 4: a BRIEF case is marked against the context it was sent, and the bundle
    # keeps the prompt rather than the object. The context is a pure function of the frozen entry
    # and the exported key list the bundle also keeps, so it is rebuilt from both -- the same way
    # `score_assumptions` re-derives its goldens from the corpus rather than from the scorecard.
    try:
        brief_keys = contract_mod.read(run_dir / "contracts").keys_for(contract_mod.SCREEN_BRIEF)
    except Exception:                             # noqa: BLE001 - a bundle taken before BRIEF
        brief_keys = None                         # existed has no BRIEF case to score either

    for envelope, directory in _cases(run_dir):
        case_id = envelope["case_id"]
        entry_id, subject, run_part = case_id.split("/")
        entry = corpus.by_id(entry_id)
        kind = ("BRIEF" if envelope["screen"] == contract_mod.SCREEN_BRIEF
                else "ASSUMPTIONS" if envelope["screen"].endswith("ASSUMPTIONS") else "READING")
        case = prompts_mod.Case(case_id=case_id, kind=kind, entry_id=entry_id,
                                screen=envelope["screen"], subject=subject,
                                run_index=int(run_part.replace("run", "")), payload={})
        old = _old_case(original, case_id)
        case.existing_roles = [{"label": label} for label in (old or {}).get("existing_roles", [])]
        failed = envelope.get("error") or (
            envelope.get("schema_error") if not envelope.get("schema_valid") else None)

        if kind == "BRIEF":
            if brief_keys is None:
                continue
            case.payload = {"context": context_mod.build_brief(entry, brief_keys)}
            questions = envelope.get("questions") if envelope.get("outcome") == "NEEDS_INPUT" \
                else None
            brief_scores.append(brief_mod.score_brief(
                case, entry, envelope.get("result"), outcome=envelope.get("outcome"),
                failed=failed, needs_input_questions=questions))
        elif kind == "READING":
            reading_scores.append(score_mod.score_reading(
                case, entry, people[(entry_id, subject)], envelope.get("result"), failed=failed))
        else:
            questions = envelope.get("questions") if envelope.get("outcome") == "NEEDS_INPUT" \
                else None
            score = score_mod.score_assumptions(case, entry, envelope.get("result"), failed=failed,
                                                needs_input_questions=questions, judge=judge)
            assumption_scores.append(score)
            (directory / f"diff-v{marks_mod.MARKS_VERSION}.json").write_text(
                json.dumps({"case_id": case_id, "matched": [
                    {"golden_id": p.golden_id, "produced_index": p.produced_index, "by": p.by,
                     "fields": p.fields} for p in (score.alignment.matched if score.alignment
                                                   else [])],
                    "missing": score.alignment.missing if score.alignment else [],
                    "extra": score.alignment.extra if score.alignment else []},
                    indent=2), encoding="utf-8")

    errored = sum(1 for e, _d in _cases(run_dir) if e.get("error") and
                  "never fit its shape" not in str(e.get("error")))
    validation = run_dir / "validation.json"
    measured = validation.is_file() and "unavailable" not in validation.read_text(encoding="utf-8")

    totals = score_mod.totals(reading_scores, assumption_scores, errored=errored,
                              refusals_measured=measured, judge_calls=judge.call_count,
                              brief_scores=brief_scores)
    marks = marks_mod.load()
    judged = marks_mod.judge(totals, marks)

    scorecard = {
        "marks_version": marks_mod.MARKS_VERSION,
        "rescored_from": original.get("marks_version"),
        "marks": marks,
        "model": original.get("model"),
        "n_runs": original.get("n_runs"),
        "contract_manifest": original.get("contract_manifest"),
        "reading": [_reading_json(s) for s in reading_scores],
        "assumptions": [_assumption_json(s) for s in assumption_scores],
        "brief": [_brief_json(s) for s in brief_scores],
        "totals": totals,
        "judge_calls": judge.calls,
        "spread": {
            "recall": score_mod.spread(assumption_scores, lambda s: s.golden_belief_recall),
            "anchoring": score_mod.spread(reading_scores, lambda s: s.anchoring_accuracy),
        },
        "prompts": original.get("prompts", []),
    }
    out = run_dir / f"scorecard-v{marks_mod.MARKS_VERSION}.json"
    out.write_text(json.dumps(scorecard, indent=2, default=str), encoding="utf-8")

    # The register is the one page a rubric change can genuinely alter without a new call: what a
    # newer rubric moved *out* of the marks has to be readable somewhere, and this is where it
    # goes (judgement calls 17 and 20). Written beside the original, never over it, for the same
    # reason the scorecard is.
    if brief_scores:
        report_mod.render_register(
            run_dir, entries_by_market={},
            paragraphs=report_mod.paragraph_blocks(corpus, brief_scores),
            filename=f"register-v{marks_mod.MARKS_VERSION}.html")

    print(f"re-scored {run_dir.name} under MARKS_VERSION {marks_mod.MARKS_VERSION} "
          f"(was {original.get('marks_version')})")
    print(f"  recall     {_fmt(totals['golden_belief_recall'])}  "
          f"(was {_fmt(original['totals']['golden_belief_recall'])})")
    print(f"  anchoring  {_fmt(totals['anchoring_accuracy'])}  "
          f"(was {_fmt(original['totals']['anchoring_accuracy'])})")
    print(f"  brief      {_fmt(totals['brief_paragraphs'])}  "
          f"(was {_fmt((original.get('totals') or {}).get('brief_paragraphs'))})")
    print(f"  refusals   {'measured' if measured else 'NOT measured'}  "
          f"-> mark met: {judged['refusals']['met']}")
    print(f"  judge      {judge.call_count} calls, deciding "
          f"{_fmt(totals['judged_fraction'])} of matched pairs")
    print(f"  passed     {judged['passed']}")
    print(f"  written    {out}")
    if brief_scores:
        print(f"  register   {run_dir / f'register-v{marks_mod.MARKS_VERSION}.html'}")
    return 0


def _fmt(value) -> str:
    return "—" if value is None else f"{value * 100:.1f}%"


def _old_case(original: dict, case_id: str):
    for entry in original.get("assumptions", []):
        if entry.get("case_id") == case_id:
            return entry
    return None


def _reading_json(s) -> dict:
    return {"case_id": s.case_id, "entry_id": s.entry_id, "subject": s.subject,
            "run_index": s.run_index, "given": s.given, "answered": s.answered,
            "agreed": s.agreed, "anchoring_accuracy": s.anchoring_accuracy,
            "confusion": s.confusion, "per_anchor": s.per_anchor,
            "missing_ids": s.missing_ids, "extra_ids": s.extra_ids, "failed": s.failed}


def _brief_json(s) -> dict:
    return {"case_id": s.case_id, "entry_id": s.entry_id, "run_index": s.run_index,
            "paragraph": s.paragraph, "length": s.length, "marks": s.marks,
            "findings": s.findings, "phrasing": s.phrasing, "met": s.met, "failed": s.failed,
            "needs_input": s.needs_input}


def _assumption_json(s) -> dict:
    return {"case_id": s.case_id, "entry_id": s.entry_id, "subject": s.subject,
            "run_index": s.run_index, "golden_total": s.golden_total, "matched": s.matched,
            "golden_belief_recall": s.golden_belief_recall, "exact_match": s.exact_match(),
            "extra_beliefs": s.extra_beliefs, "needs_input": s.needs_input,
            "needs_input_questions": s.needs_input_questions, "phrase_band": s.phrase_band,
            "judged": s.judged, "judged_candidacy": s.judged_candidacy,
            "existing_roles": s.existing_roles, "failed": s.failed,
            "missing": [] if s.alignment is None else s.alignment.missing}


if __name__ == "__main__":
    raise SystemExit(main())
