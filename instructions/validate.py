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

# The stage a screen decomposes, for the batch's own `screen` field. `QUESTIONS` gains nothing here
# on purpose: it names no stage, and `case.screen` is already `QUESTIONS`.
_STAGE_SCREEN = {"PROBLEM": "PROBLEM_ASSUMPTIONS", "SOLUTION": "SOLUTION_ASSUMPTIONS",
                 "COMMERCIAL": "COMMERCIAL_ASSUMPTIONS"}

#: Where keel-cloud keeps the validator this module shells, so that *whether it takes a shape* can
#: be asked rather than assumed (FR-019). Reading a sibling to learn a fact about it is what this
#: package already does for the contract (`contract.export`), the instructions (`instruction.read`)
#: and the routing table (`models.from_keel_cloud`); what it never does is keep a copy.
_TOOL = (Path("src") / "test" / "java" / "com" / "keeldiscovery" / "cloud" / "tooling"
         / "ScreenContractTool.java")

#: The three shapes this eval needs the validator to take, and the marker in its source that says
#: it does. `earlier_beliefs` is the batch key that would let `ScreenResultApplier` resolve a
#: `reads: {stage, line}`; `QUESTIONS` is the screen whose case seeds a project with settled lines;
#: `measurements` is the batch key that makes those settled lines **the ones the model was shown**,
#: so a `reads` index means the same belief on both sides. The marker is the *read* and not the
#: word: `measurements` appears in that file's prose already, and a shape read off a comment is a
#: shape assumed.
_SHAPE_MARKERS = {"earlier_beliefs": "earlier_beliefs", "questions": "InferenceScreen.QUESTIONS",
                  "measurements": 'get("measurements")'}


def shapes_taken(keel_cloud: Path) -> dict:
    """Which of `_SHAPE_MARKERS` keel-cloud's validator takes, read off the validator itself.

    `{shape: True|False}`, and every shape `False` when the file cannot be read at all -- an
    unreadable sibling is a prerequisite that has not landed, not a capability to assume.
    """
    try:
        source = (Path(keel_cloud) / _TOOL).read_text(encoding="utf-8")
    except OSError:
        return {shape: False for shape in _SHAPE_MARKERS}
    return {shape: marker in source for shape, marker in _SHAPE_MARKERS.items()}


def shapes_needed(batch: dict) -> set:
    """Which shapes *this* batch actually needs, so a run is never failed for a capability nothing
    in it reached for. A `QUESTIONS` case needs the `questions` shape; an assumptions case whose
    result carries a `reads` needs `earlier_beliefs`, and one that does not needs nothing."""
    needed = set()
    for case in batch.get("cases") or []:
        if case.get("screen") == "QUESTIONS":
            needed.add("questions")
            if case.get("measurements"):
                needed.add("measurements")
            continue
        produced = (case.get("result") or {}).get("assumptions")
        if isinstance(produced, list) and any(
                isinstance(b, dict) and b.get("reads") is not None for b in produced):
            needed.add("earlier_beliefs")
    return needed


def unmet_prerequisites(keel_cloud: Path, batch: dict) -> list:
    """One sentence per shape this batch needs and keel-cloud's validator does not take.

    **Never softened to a warning and never scored as a refusal** (FR-019). The caller reports the
    marks that depended on it as *unmeasured*, and an unmeasured mark is not a met mark (judgement
    call 13). A green run that never showed the aggregate a questionnaire, or that showed it a
    reference it had nothing to resolve against, is the one way this rubric could flatter itself.
    """
    taken = shapes_taken(keel_cloud)
    reasons = []
    for shape in sorted(shapes_needed(batch)):
        if taken.get(shape):
            continue
        reasons.append(_PREREQUISITE[shape])
    return reasons


_PREREQUISITE = {
    "earlier_beliefs": (
        "keel-cloud's `screenContracts validate` does not read the batch's `earlier_beliefs`: "
        "`ScreenContractTool.projectFor` frames this screen's stage and approves no earlier one, "
        "so `ScreenResultApplier.resolveReads` has an empty `earlierLinesOf` and refuses every "
        "reference the model wrote. **Prerequisite for keel-cloud**: `projectFor` must introduce "
        "and approve the batch's `earlier_beliefs`, per stage, in the order the case's own "
        "`earlier_lines` numbered them (keel-e2e-eval spec 025 FR-018/FR-019). Until it does, "
        "`rule_refusal_rate` and `shape_refusals` are UNMEASURED on any run whose answers carry a "
        "`reads` -- they are not zero, and they are not met."),
    "questions": (
        "keel-cloud's `screenContracts validate` does not know the `QUESTIONS` screen, so `Q5`, "
        "`Q6`, `Q7` and `Q8` are unreachable and `rule_refusal_rate` has not been measured on the "
        "screen this rubric bumped for. **Prerequisite for keel-cloud**: spec 048 FR-015 and spec "
        "049's `ScreenContractTool` QUESTIONS case."),
    "measurements": (
        "keel-cloud's `screenContracts validate` does not read the `QUESTIONS` batch case's "
        "`measurements`: `ScreenContractTool.projectFor` seeds that case with a canned project of "
        "three settled beliefs, so a `reads` index the model wrote against the array it was "
        "actually shown is refused for naming a measurement the seeded project does not have. "
        "**Prerequisite for keel-cloud**: `projectFor` must seed the `QUESTIONS` project from the "
        "batch's own `measurements`, in the given index order, so `measurements[i]` on the seeded "
        "project is the i-th entry the model saw (keel-e2e-eval spec 025 FR-018/FR-019). Until it "
        "does, `rule_refusal_rate` and `shape_refusals` are UNMEASURED on any run that showed a "
        "questionnaire call more measurements than the canned project carries -- they are not "
        "zero, and they are not met."),
}


def build_batch(cases_and_results) -> dict:
    """One batch from every case that produced a result the aggregate can be asked about.

    `roles` is the state the screen would have arrived into — the roles earlier stages introduced,
    exactly what the case's own context carried — so a `{reuse: label}` resolves the way it would
    in production rather than failing for a reason the model is not responsible for.

    **`earlier_beliefs`** (spec 025 FR-018) is the same idea one design later. Under keel-cloud
    spec 049 a belief may carry `reads: {stage, line}`, and `ScreenResultApplier` resolves it
    against the project's own approved earlier stages. A batch case that carried nothing to resolve
    against would have every reference refused as a derivation failure — and `shape_refusals` is
    marked at an absolute zero, so the run would fail for a fault **this eval created**. So the
    earlier stages' approved beliefs travel with the case, per stage, **in the order
    `context.earlier_lines` numbered them**, which is the order the ordinal counts in.

    **And a `QUESTIONS` case is a case** — which is why it carries **`measurements`** (spec 025
    FR-018, Discovered D18). Its result is applied through `writeQuestionnaire`, the only way `Q5`,
    `Q6`, `Q7` and `Q8` are reachable at all and counted by rule id; and its only cross-reference,
    `reads`, is a 0-based index into the `measurements` array the model was shown. A case that
    carried no measurements left the validator to seed a canned project of its own, and every index
    past the end of *that* project came back a shape refusal — a fault **this eval created**, on a
    mark set at an absolute zero. So the settled beliefs travel with the case, **in
    `context.measurements`' own order**, which is the order the index counts in.
    """
    cases = []
    for case, result in cases_and_results:
        if result is None:
            continue
        context = case.payload.get("context") or {}
        entry = {
            "case_id": case.case_id,
            "screen": _STAGE_SCREEN.get(case.subject, case.screen),
            "market": context.get("market"),
            "roles": [{"label": r.get("label"), "roleType": r.get("roleType"),
                       "about": r.get("about"), "market": r.get("market")}
                      for r in (case.existing_roles or [])],
            "statement": _statement_of(case),
            "result": result,
        }
        if case.kind == "QUESTIONS":
            entry["measurements"] = _measurements(context)
        else:
            entry["earlier_beliefs"] = _earlier_beliefs(context)
        cases.append(entry)
    return {"cases": cases}


def _measurements(context: dict) -> list:
    """The settled beliefs **the model was given**, in `measurements`' own order and numbering.

    The same objects the context carried, not a second derivation of them -- `_earlier_beliefs`'
    rule one screen along, and for the harder version of the same reason. A `QUESTIONS` answer's
    only cross-reference is `reads`, a 0-based index into this array; a validator seeded with a
    *different* array resolves index 3 to a belief the model never saw, or to nothing at all, and
    counts the model's own arithmetic as a shape refusal. One place decides the index, and it is
    `instructions/context.measurements_for`.
    """
    measurements = context.get("measurements")
    return list(measurements) if isinstance(measurements, list) else []


def _earlier_beliefs(context: dict) -> list:
    """The earlier stages' approved beliefs, in `earlier_lines`' own order and numbering.

    The same objects the context carried, not a second derivation of them: one place decides the
    ordinal, and a `{stage, line}` that meant one belief in the prompt and another in the validator
    is the failure the whole reference design exists to make impossible.
    """
    lines = context.get("earlier_lines")
    return list(lines) if isinstance(lines, list) else []


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
