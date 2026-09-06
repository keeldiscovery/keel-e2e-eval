"""The rubric this eval judges by, versioned (spec 009 FR-014).

`MARKS_VERSION` is to this eval what `POLICY_VERSION` is to `evals/policy.py`, and deliberately a
separate constant: an instruction-eval rubric change must never look like a scenario-scoring one.
**Bump it for any change to a mark, a metric definition, an alignment rule, the field list, or a
judgement call below** -- scores under different versions describe different rubrics and are not
comparable.

Judgement calls, append-only across every version, struck nowhere, because the rubric's history is
part of what a number means:

1.  **v1**: exact-match is over matched pairs only, so recall and exactness are not
    double-counted.
2.  **v1**: `measure.kind`/`measure.unit` are `n/a` for a Choice pair and excluded from the rate
    rather than counted as agreeing.
3.  **v1**: extra beliefs are counted and not marked. Over-generation is a finding first.
4.  **v1**: band equality is exact, because the phrase table is a fixture, not a judgement.
5.  **v1**: `GUESSED` precision and recall are mandatory beside accuracy, never optional.
6.  **v1**: a shape refusal, a schema-invalid answer and a rule refusal are three different lines.
7.  **v1**: the spread is reported; nothing is averaged before it is reported.
8.  **v1**: `founderPhrase` is a scored exact-match field, and absent-on-both-sides agrees, because
    a `CHOICE` has no phrase and requiring one would penalise every Choice belief.
9.  **v1**: a `NEEDS_INPUT` from an assumption screen whose statement was present is a failed case
    counted in the recall denominator, per design decision 14 -- not excluded, and not softened.
10. **v1**: the register is rendered and never scored. A metric here would look like evidence and
    be similarity to one hand-written example; the design requires a person, so the run records
    what the person said.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

MARKS_VERSION = 1

DEFAULT_MARKS_PATH = Path(__file__).parent / "marks.toml"

DEFAULTS = {
    "anchoring_accuracy": 0.90,
    "golden_belief_recall": 0.80,
    "refusals": 0,
}


def load(path: Path | str | None = None) -> dict:
    path = Path(path) if path else DEFAULT_MARKS_PATH
    if not path.is_file():
        raise FileNotFoundError(f"no marks file at {path}")
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    marks = dict(DEFAULTS)
    marks.update(raw.get("marks") or {})
    return marks


def judge(totals: dict, marks: dict) -> dict:
    """Each mark against its number. A run passes only if all three are met.

    A `None` is a failure, not a pass: a mark with no measurement behind it has not been met, and
    saying otherwise would let an empty run look green.
    """
    accuracy = totals.get("anchoring_accuracy")
    recall = totals.get("golden_belief_recall")
    refusals = sum((totals.get("refusals_by_rule") or {}).values())
    results = {
        "anchoring_accuracy": {
            "value": accuracy, "mark": marks["anchoring_accuracy"],
            "met": accuracy is not None and accuracy >= marks["anchoring_accuracy"]},
        "golden_belief_recall": {
            "value": recall, "mark": marks["golden_belief_recall"],
            "met": recall is not None and recall >= marks["golden_belief_recall"]},
        "refusals": {
            "value": refusals, "mark": marks["refusals"],
            "met": refusals <= marks["refusals"]},
    }
    results["passed"] = all(r["met"] for r in results.values() if isinstance(r, dict))
    return results
