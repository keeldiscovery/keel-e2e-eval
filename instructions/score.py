"""Every number a run reports (spec 009 FR-011/FR-013, contracts/metrics-contract.md).

Three rules run through all of it.

**Nothing is averaged before it is reported.** Each of the N runs is scored on its own and the
report carries the spread; a case that passes twice and fails once is an unstable instruction, not
a 67 %.

**`GUESSED` precision and recall are never optional.** Most anchors in this corpus are anchored, so
a reader that answered `ANCHORED` to everything scores high on accuracy and has recall zero on the
one judgement the instrument exists to make. Accuracy alone would call that reader good.

**Three ways of being wrong stay three lines.** A schema-invalid answer (keel-runtime's own
validator refused it), a shape refusal (it fit no contract the aggregate could read) and a rule
refusal (the aggregate read it and refused it, by id) call for three different instruction fixes,
so they are never summed.

One reading of the metrics contract worth stating: it defines `answered` as the anchors given for
which the model returned a word and `anchoring_accuracy` as `agree / answered`, and separately says
an omitted or invented anchor id is "counted against `answered`". This module uses the formula as
written and reports `given`, `answered`, `missing_ids` and `extra_ids` beside it, so a model that
quietly skipped the hard anchors is visible rather than flattered by a smaller denominator.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import align as align_mod
from . import brief as brief_mod

FIELDS = align_mod.FIELDS


# ---------------------------------------------------------------------------------------- reading

@dataclass
class ReadingScore:
    case_id: str
    entry_id: str
    subject: str
    run_index: int
    given: int = 0
    answered: int = 0
    agreed: int = 0
    confusion: dict = field(default_factory=lambda: {"aa": 0, "ag": 0, "ga": 0, "gg": 0})
    per_anchor: list = field(default_factory=list)
    missing_ids: list = field(default_factory=list)
    extra_ids: list = field(default_factory=list)
    failed: str | None = None       # a reason the case produced nothing at all

    @property
    def anchoring_accuracy(self):
        return (self.agreed / self.answered) if self.answered else None


def score_reading(case, entry, person, result, *, failed: str | None = None) -> ReadingScore:
    """One reading case: the model's word per anchor against the corpus's own.

    Matched by **`(stage, anchorId)`, never the bare id** (measured-beliefs decision 18, DRIFT
    #37): an anchor id is unique only within one stage's own questionnaire, so the pair is what the
    context handed the model (`context.anchors_for`) and what the contract now requires back. A
    produced anchoring with no `stage` -- or the wrong one -- is not a match; it refuses the same
    way an omitted or invented id already did, rather than resolving it by guessing.
    """
    score = ReadingScore(case_id=case.case_id, entry_id=entry.id, subject=case.subject,
                         run_index=case.run_index, failed=failed)
    given = {}
    for anchor_id, answer in person.written():
        stage = (entry.anchor(anchor_id) or {}).get("stage")
        given[(stage, anchor_id)] = answer.get("anchoring")
    score.given = len(given)
    if failed or not isinstance(result, dict):
        score.missing_ids = sorted(anchor_id for _, anchor_id in given)
        return score

    produced = {}
    raw = result.get("anchorings")
    if isinstance(raw, list):
        for item in raw:
            if (isinstance(item, dict) and isinstance(item.get("anchorId"), str)
                    and isinstance(item.get("stage"), str)):
                produced[(item["stage"], item["anchorId"])] = item.get("anchoring")

    for (stage, anchor_id), golden in given.items():
        answer = produced.get((stage, anchor_id))
        if answer not in ("ANCHORED", "GUESSED"):
            score.missing_ids.append(anchor_id)
            score.per_anchor.append({"anchor_id": anchor_id, "golden": golden,
                                     "produced": answer, "agree": False})
            continue
        score.answered += 1
        agree = (answer == golden)
        score.agreed += int(agree)
        key = ("g" if golden == "GUESSED" else "a") + ("g" if answer == "GUESSED" else "a")
        score.confusion[key] = score.confusion.get(key, 0) + 1
        score.per_anchor.append({"anchor_id": anchor_id, "golden": golden,
                                 "produced": answer, "agree": agree})

    score.extra_ids = sorted(anchor_id for _, anchor_id in (set(produced) - set(given)))
    return score


# ------------------------------------------------------------------------------------ assumptions

@dataclass
class AssumptionScore:
    case_id: str
    entry_id: str
    subject: str            # the stage
    run_index: int
    golden_total: int = 0
    matched: int = 0
    extra_beliefs: int = 0
    judged: int = 0
    judged_candidacy: int = 0
    needs_input: bool = False
    needs_input_questions: list = field(default_factory=list)
    failed: str | None = None
    field_hits: dict = field(default_factory=dict)      # field -> [agreed, applicable]
    phrase_band: dict = field(default_factory=lambda: {
        "phrase_band": 0, "phrase_only": 0, "band_only": 0, "neither": 0})
    alignment: object = None
    existing_roles: list = field(default_factory=list)

    @property
    def golden_belief_recall(self):
        return (self.matched / self.golden_total) if self.golden_total else None

    def exact_match(self) -> dict:
        return {name: (hits / total if total else None)
                for name, (hits, total) in self.field_hits.items()}


def score_assumptions(case, entry, result, *, failed: str | None = None,
                      needs_input_questions=None, judge=None) -> AssumptionScore:
    """One assumption case, aligned and counted.

    A `NEEDS_INPUT`, a schema-invalid answer and an executor failure all land here as a case that
    found no goldens: an assumption screen's only legitimate ask is a missing statement (design
    decision 14) and this harness always supplies one, so an ask is a failed case counted in the
    recall denominator -- not excluded, and not softened.
    """
    goldens = entry.beliefs_for(case.subject)
    score = AssumptionScore(case_id=case.case_id, entry_id=entry.id, subject=case.subject,
                            run_index=case.run_index, golden_total=len(goldens), failed=failed,
                            existing_roles=[r.get("label") for r in case.existing_roles])
    score.field_hits = {name: [0, 0] for name in FIELDS}
    if needs_input_questions is not None:
        score.needs_input = True
        score.needs_input_questions = needs_input_questions
        return score
    if failed or not isinstance(result, dict):
        return score

    produced = result.get("assumptions")
    produced = produced if isinstance(produced, list) else []
    alignment = align_mod.align(goldens, produced, judge)
    score.alignment = alignment
    score.matched = len(alignment.matched)
    score.extra_beliefs = len(alignment.extra)
    score.judged = alignment.judged
    score.judged_candidacy = alignment.judged_candidacy

    for pair in alignment.matched:
        for name in FIELDS:
            value = pair.fields.get(name)
            if value is None:
                continue                      # n/a: a Choice pair has no measure to compare
            score.field_hits[name][1] += 1
            score.field_hits[name][0] += int(bool(value))
        phrase = bool(pair.fields.get("founder_phrase"))
        band = bool(pair.fields.get("expected_or_band"))
        key = ("phrase_band" if phrase and band else
               "phrase_only" if phrase else
               "band_only" if band else "neither")
        score.phrase_band[key] += 1
    return score


# ----------------------------------------------------------------------------------------- totals

def totals(reading_scores: list, assumption_scores: list, *, errored: int = 0,
           refusals_by_rule: dict | None = None, shape_refusals: int = 0,
           schema_invalid: int = 0, refusals_measured: bool = False,
           refusals_shown: int = 0,
           judge_calls: int = 0, brief_scores: list | None = None) -> dict:
    """The run's own numbers, each summed over its own denominator and never over another's."""
    given = sum(s.given for s in reading_scores)
    answered = sum(s.answered for s in reading_scores)
    agreed = sum(s.agreed for s in reading_scores)
    confusion = {"aa": 0, "ag": 0, "ga": 0, "gg": 0}
    for s in reading_scores:
        for key, value in s.confusion.items():
            confusion[key] = confusion.get(key, 0) + value

    called_guessed = confusion["ag"] + confusion["gg"]
    was_guessed = confusion["ga"] + confusion["gg"]

    golden_total = sum(s.golden_total for s in assumption_scores)
    matched = sum(s.matched for s in assumption_scores)

    field_hits = {name: [0, 0] for name in FIELDS}
    phrase_band = {"phrase_band": 0, "phrase_only": 0, "band_only": 0, "neither": 0}
    for s in assumption_scores:
        for name, (hits, total) in s.field_hits.items():
            field_hits[name][0] += hits
            field_hits[name][1] += total
        for key, value in s.phrase_band.items():
            phrase_band[key] += value

    # MARKS_VERSION 4: the BRIEF subject's own numbers, folded in beside the other two and never
    # summed with them -- three subjects, three denominators (`instructions/brief.py`).
    brief = brief_mod.totals(brief_scores or [])

    return {
        **brief,
        "anchoring_accuracy": (agreed / answered) if answered else None,
        "guessed_precision": (confusion["gg"] / called_guessed) if called_guessed else None,
        "guessed_recall": (confusion["gg"] / was_guessed) if was_guessed else None,
        "confusion": confusion,
        "anchors_given": given,
        "anchors_answered": answered,
        "reading_missing_ids": sum(len(s.missing_ids) for s in reading_scores),
        "reading_extra_ids": sum(len(s.extra_ids) for s in reading_scores),
        "golden_belief_recall": (matched / golden_total) if golden_total else None,
        "golden_beliefs": golden_total,
        "matched_beliefs": matched,
        "exact_match": {name: (hits / total if total else None)
                        for name, (hits, total) in field_hits.items()},
        "exact_match_counts": {name: {"agreed": hits, "applicable": total}
                               for name, (hits, total) in field_hits.items()},
        "phrase_band": phrase_band,
        "extra_beliefs": sum(s.extra_beliefs for s in assumption_scores),
        "needs_input_cases": sum(1 for s in assumption_scores if s.needs_input),
        "judged_fraction": (sum(s.judged for s in assumption_scores) / matched) if matched else 0.0,
        "judged_pairs": sum(s.judged for s in assumption_scores),
        "judged_candidacy_pairs": sum(s.judged_candidacy for s in assumption_scores),
        "judged_any_fraction": ((sum(s.judged + s.judged_candidacy for s in assumption_scores)
                                 / matched) if matched else 0.0),
        "judge_calls": judge_calls,
        "refusals_by_rule": dict(refusals_by_rule or {}),
        # v6: how many answers the aggregate judged (accepted + refused) -- the rate's denominator.
        "refusals_shown": int(refusals_shown or 0),
        "refusals_measured": refusals_measured,
        "shape_refusals": shape_refusals,
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
