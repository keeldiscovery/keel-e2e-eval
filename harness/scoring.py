"""Roll-ups (T005, data-model.md's "Scoring math"): check results -> interaction attribute
scores -> category scores -> one run score, plus the 2/5 completion gate. Also owns the
transcript-to-scorecard pipeline (`score_bundle`) and the `facts.json` side-file that lets a
bundle re-score itself without the original Scenario object (see module docstring below on why
that file exists).

Everything here is a pure function of what's already on disk (transcript.jsonl, facts.json) --
no wire calls, no wall-clock dependence in the scores themselves (`generated_at` is a timestamp,
not a scoring input) -- so `make report RUN=<dir>` can call `score_bundle` again under a bumped
policy and get a legitimately re-derived scorecard (SC-004).
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from evals import policy
from evals.facts import Fact
from harness import rubric
from harness.interactions import Interaction, derive_interactions


def round_half(value: float) -> float:
    """Rounds to the nearest 0.5, per contract's half-point scale."""
    return round(value * 2) / 2


# ------------------------------------------------------------------------------------- roll-ups

def score_interaction_attribute(checks: list[rubric.CheckResult], attribute: str) -> tuple[float | None, float]:
    """`5 x sum(weight of passed-or-waived) / sum(weight)`, rounded to halves -- or (None, 0.0)
    when this interaction carries no checks for `attribute` at all (it doesn't "carry" that
    attribute, per data-model.md's category definition)."""
    relevant = [c for c in checks if c.attribute == attribute]
    total_weight = sum(c.weight for c in relevant)
    if total_weight <= 0:
        return None, 0.0
    # `passed` is already True for a waived check (rubric.py sets it that way) -- "waived counts
    # as pass but is flagged" (data-model.md).
    passed_weight = sum(c.weight for c in relevant if c.passed)
    return round_half(5 * passed_weight / total_weight), total_weight


def score_categories(results_by_interaction: dict[str, list[rubric.CheckResult]]) -> dict[str, float]:
    """Category score = weighted mean, across every interaction that carries that attribute, of
    the interaction's own attribute score -- weighted by that interaction's total check weight
    for the attribute, so a heavier-checked interaction (e.g. a weight-2 FID hop) counts more."""
    sums = {attribute: 0.0 for attribute in policy.CATEGORY_WEIGHTS}
    weights = {attribute: 0.0 for attribute in policy.CATEGORY_WEIGHTS}
    for checks in results_by_interaction.values():
        for attribute in policy.CATEGORY_WEIGHTS:
            score, weight = score_interaction_attribute(checks, attribute)
            if score is None:
                continue
            sums[attribute] += score * weight
            weights[attribute] += weight
    return {
        attribute: round_half(sums[attribute] / weights[attribute])
        for attribute in policy.CATEGORY_WEIGHTS if weights[attribute] > 0
    }


def compute_run_score(categories: dict[str, float], *, complete: bool) -> float | None:
    """Run score = weighted mean of the four categories (policy weights; a category absent from
    this run -- e.g. no participant-page ever happened -- is left out of both the numerator and
    the weight total, rather than scored as a 0, since it carries no evidence either way).
    `complete=False` caps the result at policy.COMPLETION_GATE_SCORE (design's "a beautiful
    half-run can't outscore an ugly complete one").

    **`None` when no category applies at all** (spec 012). The rule above already says an absent
    category carries no evidence either way; a run where *every* category is absent used to score
    `0.0` regardless, which says "as bad as a run can be" about a run that measured nothing of the
    kind these four attributes measure. S-008 is the scenario that made it visible -- it referees
    a contract between the skill and the runtime, and never puts a founder in front of a screen
    the policy has a check for. `None` reads as *not scored*, and the report says so in words.

    This is not a policy change and `POLICY_VERSION` does not move: no check, weight or waiver in
    `evals/policy.py` is touched, and every run with at least one applicable category scores
    exactly what it scored before -- the pre-9 runs of record re-score unchanged.
    """
    present = {a: w for a, w in policy.CATEGORY_WEIGHTS.items() if a in categories}
    total_weight = sum(present.values())
    if not total_weight:
        return None
    raw = sum(categories[a] * w for a, w in present.items()) / total_weight
    if not complete:
        raw = min(raw, policy.COMPLETION_GATE_SCORE)
    return round_half(raw)


def _check_to_dict(check: rubric.CheckResult) -> dict[str, Any]:
    # "pass" (data-model.md's literal field name) can't be a Python attribute (reserved word),
    # hence CheckResult.passed internally -- renamed back to "pass" only at the JSON boundary.
    return {
        "check_id": check.check_id,
        "attribute": check.attribute,
        "weight": check.weight,
        "pass": check.passed,
        "waived": check.waived,
        "detail": check.detail,
        "evidence": check.evidence,
    }


def not_applicable_categories(categories: dict[str, float]) -> list[str]:
    """003-eval-set T003 (design §6.1): categories no interaction in this run carries at all --
    S-007's no-browser scorecard is the motivating case (no ui-visit/participant-page interaction
    ever exists, so ORIENTATION's U-checks and FIDELITY's UI-hop checks never fire). `categories`
    (`score_categories`' output) already excludes these from both the numerator and the weight
    total in `compute_run_score` -- that math was already honest -- this just names them
    explicitly in the scorecard, so a reviewer sees "not applicable" rather than wondering whether
    an absent category was scored zero and dropped, or simply forgotten.
    """
    return sorted(a for a in policy.CATEGORY_WEIGHTS if a not in categories)


def build_scorecard(interactions: list[Interaction], results_by_interaction: dict[str, list[rubric.CheckResult]],
                     *, scenario: str, complete: bool) -> dict[str, Any]:
    categories = score_categories(results_by_interaction)
    interaction_entries = []
    for ix in interactions:
        checks = results_by_interaction.get(ix.id, [])
        attributes = {}
        for attribute in policy.CATEGORY_WEIGHTS:
            score, _weight = score_interaction_attribute(checks, attribute)
            if score is not None:
                attributes[attribute] = score
        interaction_entries.append({
            "id": ix.id, "type": ix.type, "title": ix.title,
            "attributes": attributes,
            "checks": [_check_to_dict(c) for c in checks],
        })
    return {
        "policy_version": policy.POLICY_VERSION,
        "scenario": scenario,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "interactions": interaction_entries,
        "categories": categories,
        "not_applicable_categories": not_applicable_categories(categories),
        "run_score": compute_run_score(categories, complete=complete),
        "gated": not complete,
        "complete": complete,
    }


# --------------------------------------------------------------------------------- facts.json

def write_facts(run_dir: Path, facts: dict[str, Fact]) -> None:
    """Persists the scenario's fact registry into the bundle (`facts.json`), so `make report
    RUN=<dir>` can re-run FIDELITY checks without the original Scenario object -- scoring stays a
    pure function of the bundle (spec edge case), not of whatever Python object happened to be
    live in the process that ran the eval.
    """
    raw = {fact_id: asdict(fact) for fact_id, fact in facts.items()}
    (run_dir / "facts.json").write_text(json.dumps(raw, indent=2))


def read_facts(run_dir: Path) -> dict[str, Fact]:
    path = run_dir / "facts.json"
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}
    facts: dict[str, Fact] = {}
    for fact_id, fields in raw.items():
        try:
            facts[fact_id] = Fact(
                text=fields.get("text", ""), kind=fields.get("kind", ""),
                hops=list(fields.get("hops") or []), absent_hops=list(fields.get("absent_hops") or []),
            )
        except (TypeError, AttributeError):
            continue
    return facts


# -------------------------------------------------------------------------------- the pipeline

def _read_transcript_entries(run_dir: Path) -> list[dict]:
    """Same ordering contract as harness.evidence._read_transcript (sorted by `seq`, malformed
    lines skipped) -- duplicated in miniature rather than imported, so this module and
    harness.evidence don't need to import each other."""
    path = run_dir / "transcript.jsonl"
    if not path.exists():
        return []
    entries = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    entries.sort(key=lambda e: e.get("seq", 0))
    return entries


def score_bundle(run_dir: Path, *, scenario: str, complete: bool,
                  facts: dict[str, Fact] | None = None) -> dict[str, Any]:
    """Reads transcript.jsonl (+ facts.json when `facts` isn't passed explicitly), evaluates the
    policy, writes scorecard.json, and returns it. This is what both the live eval (conftest.py,
    with `facts` fresh from the scenario) and `make report RUN=<dir>` (evidence.py, with `facts`
    re-read from facts.json) call -- the only difference is where `facts` comes from.
    """
    if facts is None:
        facts = read_facts(run_dir)
    entries = _read_transcript_entries(run_dir)
    interactions = derive_interactions(entries)
    interactions, results = rubric.evaluate(interactions, facts)
    scorecard = build_scorecard(interactions, results, scenario=scenario, complete=complete)
    (run_dir / "scorecard.json").write_text(json.dumps(scorecard, indent=2, default=str))
    return scorecard
