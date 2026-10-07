"""Every number a run reports (spec 009 FR-011/FR-013; spec 029 data-model §6, marks-v9 §2).

Three rules run through all of it, unchanged since `MARKS_VERSION` 1.

**Nothing is averaged before it is reported.** Each of the N runs is scored on its own and the
report carries the spread; a case that passes twice and fails once is an unstable instruction, not
a 67 %.

**`GUESSED` precision and recall are never optional** (call 5). Most stories in this corpus are
anchored, so a reader that answered `ANCHORED` to everything scores high on accuracy and has recall
zero on the one judgement the instrument exists to make.

**Three ways of being wrong stay three lines** (call 6): schema-invalid, shape refusal, rule
refusal -- three different instruction fixes, never summed.

At `MARKS_VERSION` 9 the subjects moved (call 28). `score_assumptions`, `score_reading` and the
alignment they rode on retired with `align.py` (call 29). What scores now:

- `score_compare` -- keel-cloud's engine against `expected` (call 34; `instructions/compare.py`);
- `score_calibration` / `score_respondent` -- `dimension_coverage`, `option_validity` and `no_leak`
  by code against the registry (calls 30-32; spec 029 US2/US3);
- `score_interpret` -- one anchoring judgement a readable person (call 33; US3);
- `brief.score_brief` -- five per-case marks, all or nothing (call 35).

`totals` rolls each over **its own** denominator and never another's.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import brief as brief_mod


# ------------------------------------------------------------------------------------ compare

@dataclass
class CompareCaseScore:
    case_id: str
    entry_id: str
    subject: str = "COMPARE"
    checks: int = 0
    agreed: int = 0
    mismatches: list = field(default_factory=list)
    reported_diffs: list = field(default_factory=list)
    measured: bool = False
    reason: str | None = None

    @property
    def compare_correctness(self):
        return (self.agreed / self.checks) if (self.measured and self.checks) else None


def score_compare(case, entry, compare_score) -> CompareCaseScore:
    """One entry's `COMPARE` row: the diff `compare.py` made, carried onto the case. An engine that
    could not be asked is `measured: false` with its reason, and stays that way (call 13)."""
    return CompareCaseScore(case_id=case.case_id, entry_id=entry.id,
                            checks=compare_score.checks, agreed=compare_score.agreed,
                            mismatches=list(compare_score.mismatches),
                            reported_diffs=list(compare_score.reported_diffs),
                            measured=compare_score.measured, reason=compare_score.reason)


# ------------------------------------------------------------------------------------- totals

def _fraction(hit, of):
    return (hit / of) if of else None


def _sum(scores, name) -> int:
    return sum(int(getattr(s, name, 0) or 0) for s in scores)


def _question_screen(scores) -> dict:
    """Coverage, validity and leak over one question screen's cases (calibration or respondent)."""
    return {
        "cases": len(scores),
        "coverage": {"hit": _sum(scores, "coverage_hit"), "of": _sum(scores, "coverage_of")},
        "validity": {"hit": _sum(scores, "validity_hit"), "of": _sum(scores, "validity_of")},
        "leak": {"clean": _sum(scores, "leak_clean"), "of": _sum(scores, "leak_of")},
    }


def totals(calibration_scores=(), respondent_scores=(), interpret_scores=(), compare_scores=(),
           *, brief_scores=(), errored: int = 0, refusals_by_rule: dict | None = None,
           shape_refusals: int = 0, schema_invalid: int = 0, refusals_measured: bool = False,
           refusals_shown: int = 0, judge_calls: int = 0, leak_hits: int | None = None,
           leak_judged: int | None = None, refusals_unmeasured_kinds=()) -> dict:
    """The run's own numbers (data-model §6), each summed over its own denominator."""
    calibration = _question_screen(calibration_scores)
    respondent = _question_screen(respondent_scores)
    both = list(calibration_scores) + list(respondent_scores)

    coverage_of = calibration["coverage"]["of"] + respondent["coverage"]["of"]
    validity_of = calibration["validity"]["of"] + respondent["validity"]["of"]
    leak_of = calibration["leak"]["of"] + respondent["leak"]["of"]
    hits = _sum(both, "leak_hits") if leak_hits is None else leak_hits
    judged = _sum(both, "leak_judged") if leak_judged is None else leak_judged

    # INTERPRET: one judgement a readable person (call 33). The chipped are outside every count.
    answered = _sum(interpret_scores, "answered")
    agreed = _sum(interpret_scores, "agreed")
    confusion = {"aa": 0, "ag": 0, "ga": 0, "gg": 0}
    for s in interpret_scores:
        for key, value in (getattr(s, "confusion", None) or {}).items():
            confusion[key] = confusion.get(key, 0) + value
    called_guessed = confusion["ag"] + confusion["gg"]
    was_guessed = confusion["ga"] + confusion["gg"]
    interpret_shape = _sum(interpret_scores, "shape_fault")

    compare_measured = bool(compare_scores) and all(s.measured for s in compare_scores)
    checks = sum(s.checks for s in compare_scores if s.measured)
    compare_agreed = sum(s.agreed for s in compare_scores if s.measured)

    brief = brief_mod.totals(list(brief_scores or []))

    return {
        **brief,
        "calibration_cases": calibration["cases"],
        "calibration_coverage": calibration["coverage"],
        "calibration_validity": calibration["validity"],
        "calibration_leak": calibration["leak"],
        "respondent_cases": respondent["cases"],
        "respondent_coverage": respondent["coverage"],
        "respondent_validity": respondent["validity"],
        "respondent_leak": respondent["leak"],
        "dimension_coverage": _fraction(calibration["coverage"]["hit"]
                                        + respondent["coverage"]["hit"], coverage_of),
        "option_validity": _fraction(calibration["validity"]["hit"]
                                     + respondent["validity"]["hit"], validity_of),
        "no_leak": _fraction(calibration["leak"]["clean"] + respondent["leak"]["clean"], leak_of),
        "leak_hits": hits,
        "leak_judged": judged,
        "judged_fraction": (judged / hits) if hits else 0.0,
        "judge_calls": judge_calls,
        "anchoring_accuracy": _fraction(agreed, answered),
        "guessed_precision": _fraction(confusion["gg"], called_guessed),
        "guessed_recall": _fraction(confusion["gg"], was_guessed),
        "confusion": confusion,
        "people_given": _sum(interpret_scores, "given"),
        "people_answered": answered,
        "reading_missing_ids": sum(len(getattr(s, "missing_ids", []) or [])
                                   for s in interpret_scores),
        "reading_extra_ids": sum(len(getattr(s, "extra_ids", []) or []) for s in interpret_scores),
        "chipped_skipped": 0,
        "compare_checks": checks,
        "compare_agreed": compare_agreed,
        "compare_correctness": _fraction(compare_agreed, checks) if compare_measured else None,
        "compare_measured": compare_measured,
        "compare_reported_diffs": sum(len(s.reported_diffs) for s in compare_scores),
        "compare_unmeasured": [{"entry": s.entry_id, "reason": s.reason}
                               for s in compare_scores if not s.measured],
        "refusals_by_rule": dict(refusals_by_rule or {}),
        # v6 (call 22): how many answers the aggregate judged -- the rate's denominator.
        "refusals_shown": int(refusals_shown or 0),
        "refusals_measured": refusals_measured,
        "refusals_unmeasured_kinds": list(refusals_unmeasured_kinds or ()),
        # A produced reading whose `anchoring` is neither word is a shape refusal (spec 029 Edge
        # Cases), counted against the absolute zero beside the aggregate's own.
        "shape_refusals": int(shape_refusals or 0) + interpret_shape,
        "schema_invalid": schema_invalid,
        "errored": errored,
    }


def spread(scores: list, metric) -> dict:
    """Per case (entry + subject), the min and max of `metric` across the N runs.

    The point of reporting it: an average of a metric that was 1.0 once and 0.0 twice describes no
    run that happened.
    """
    buckets = {}
    for s in scores:
        value = metric(s)
        buckets.setdefault(f"{s.entry_id}/{s.subject}", []).append(value)
    out = {}
    for key, values in buckets.items():
        real = [v for v in values if v is not None]
        out[key] = {
            "runs": values,
            "min": min(real) if real else None,
            "max": max(real) if real else None,
        }
    return out
