"""The aggregate's own verdict on every produced belief set (spec 009 FR-012, T023/T024).

**The invariants are never re-implemented here.** `E1`..`E5`, `Q1`, `Q2`, `Q4`, `Q5` and `M1` live
in keel-cloud's `Project.introduceAssumptions` and its value objects, and the only honest way to
ask whether the aggregate would have taken a result is to hand it to the aggregate. So this module
collects a whole run's produced sets into one batch in keel-cloud spec 029's batch shape and shells
`./gradlew -q screenContracts --args="validate <batch> <report>"` **once** — one JVM start for the
run, not one per case, and a report on disk so the bundle keeps it as evidence.

Three ways of being wrong stay three lines (judgement call 6), because they call for three
different fixes:

- `schema_valid: false` — keel-runtime's own validator refused it; keel-cloud never saw it, and the
  instruction's envelope section is what is wrong.
- `kind: "shape"` — it reached the applier and did not fit the contract; the field named in `path`
  is what is wrong.
- `kind: "rule"` — it fit the contract and the aggregate refused the answer, by id; the
  instruction's *rules* are what is wrong, and the id says which sentence is missing.

A fourth, `kind: "case"`, is the eval's own fault by construction — a batch case whose state was
illegal before the result was even applied — and is never counted against a model.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .contract import ContractUnavailable

# The stage a screen decomposes, for the batch's own `screen` field.
_STAGE_SCREEN = {"PROBLEM": "PROBLEM_ASSUMPTIONS", "SOLUTION": "SOLUTION_ASSUMPTIONS",
                 "COMMERCIAL": "COMMERCIAL_ASSUMPTIONS"}


def build_batch(cases_and_results) -> dict:
    """One batch from every assumption case that produced a result.

    `roles` is the state the screen would have arrived into — the roles earlier stages introduced,
    exactly what the case's own context carried — so a `{reuse: label}` resolves the way it would
    in production rather than failing for a reason the model is not responsible for.
    """
    cases = []
    for case, result in cases_and_results:
        if result is None:
            continue
        cases.append({
            "case_id": case.case_id,
            "screen": _STAGE_SCREEN.get(case.subject, case.screen),
            "market": case.payload.get("context", {}).get("market"),
            "roles": [{"label": r.get("label"), "roleType": r.get("roleType"),
                       "about": r.get("about"), "market": r.get("market")}
                      for r in (case.existing_roles or [])],
            "statement": _statement_of(case),
            "result": result,
        })
    return {"cases": cases}


def _statement_of(case) -> str | None:
    context = case.payload.get("context") or {}
    for key in ("problem_statement", "solution_statement", "commercial_statement"):
        if context.get(key):
            return context[key]
    return None


def run(keel_cloud: Path, batch: dict, batch_path: Path, report_path: Path,
        *, timeout_s: float = 900.0) -> list:
    """Writes the batch, calls keel-cloud's validator once, reads the report back."""
    batch_path.parent.mkdir(parents=True, exist_ok=True)
    batch_path.write_text(json.dumps(batch, indent=2), encoding="utf-8")
    if not batch["cases"]:
        report_path.write_text("[]\n", encoding="utf-8")
        return []

    gradlew = Path(keel_cloud) / "gradlew"
    argv = [str(gradlew), "-q", "screenContracts",
            f"--args=validate {batch_path.resolve()} {report_path.resolve()}"]
    try:
        done = subprocess.run(argv, cwd=str(keel_cloud), capture_output=True, text=True,
                              timeout=timeout_s)
    except (OSError, subprocess.SubprocessError) as exc:
        raise ContractUnavailable(f"could not run keel-cloud's validator: {exc}") from exc
    if done.returncode != 0:
        raise ContractUnavailable(
            "keel-cloud's `screenContracts validate` failed -- this eval asks the aggregate what "
            "it refuses rather than re-stating its rules.\n"
            + (done.stderr.strip() or done.stdout.strip())[-4000:])
    return json.loads(report_path.read_text(encoding="utf-8"))


def fold_in(report: list) -> dict:
    """The report, counted the way the marks read it.

    `refusals_by_rule` counts **rule refusals only** — a shape refusal never reached the aggregate,
    and a case refusal is the eval's own. `by_case` lets the report quote the aggregate's own words
    beside the diff that produced them.
    """
    by_case, rules = {}, {}
    accepted = shape = case_fault = 0
    for entry in report:
        by_case[entry.get("case_id")] = entry
        if entry.get("accepted"):
            accepted += 1
            continue
        refusal = entry.get("refusal") or {}
        kind = refusal.get("kind")
        if kind == "rule":
            rule = refusal.get("rule") or "unnamed"
            rules[rule] = rules.get(rule, 0) + 1
        elif kind == "shape":
            shape += 1
        else:
            case_fault += 1
    return {"accepted": accepted, "refusals_by_rule": rules, "shape_refusals": shape,
            "case_faults": case_fault, "by_case": by_case}
