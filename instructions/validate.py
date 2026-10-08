"""The aggregate's own verdict on every model answer (spec 009 FR-012; spec 029 FR-024).

**The rules are never re-implemented here.** The v9 templates' rule ids (`X1`..`X3`, `P1`..`P3`,
`M1`..`M3`, `C1`..`C7`, `R1`..`R8`, `I1`, `B1`..`B5` -- screen-shapes §4) live in keel-cloud, and
the only honest way to ask whether the aggregate would have taken a result is to hand it to the
aggregate. So this module collects a whole run's answers into one batch and shells
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
import re
import subprocess
from pathlib import Path

from .contract import ContractUnavailable

#: Where keel-cloud keeps the validator this module shells, so that *whether it takes a screen* can
#: be asked rather than assumed (025 FR-019, spec 029 FR-024). Reading a sibling to learn a fact
#: about it is what this package already does for the contract, the instructions and the routing
#: table; what it never does is keep a copy.
_TOOL = (Path("src") / "test" / "java" / "com" / "keeldiscovery" / "cloud" / "tooling"
         / "ScreenContractTool.java")

#: The seven model screens a v9 batch carries, and the marker in the validator's source that says
#: it takes each -- the **constant reference**, `InferenceScreen.<SCREEN>`, the way `QUESTIONS` was
#: read at v8: a screen named in that file's prose is a screen assumed. `COMPARE` is never batched
#: (there is no answer to validate).
_SHAPE_MARKERS = {
    "CONTEXT_INTERPRET": "InferenceScreen.CONTEXT_INTERPRET",
    "PROBLEM_INTERPRET": "InferenceScreen.PROBLEM_INTERPRET",
    "SOLUTION_MECHANISM": "InferenceScreen.SOLUTION_MECHANISM",
    "CALIBRATION_QUESTIONS": "InferenceScreen.CALIBRATION_QUESTIONS",
    "RESPONDENT_QUESTIONS": "InferenceScreen.RESPONDENT_QUESTIONS",
    "INTERPRET": "InferenceScreen.INTERPRET",
    "BRIEF": "InferenceScreen.BRIEF",
}


def _prerequisite(screen: str) -> str:
    own = (" `dimension_coverage`, `option_validity` and `no_leak` are this repository's code and "
           "are measured either way." if screen in ("CALIBRATION_QUESTIONS",
                                                    "RESPONDENT_QUESTIONS") else "")
    return (f"keel-cloud's `screenContracts validate` does not take the {screen} case kind "
            f"(no `{_SHAPE_MARKERS[screen]}` in {_TOOL.name}). **Prerequisite for keel-cloud**: "
            f"spec 058's `ScreenContractTool` {screen} case (keel-e2e-eval spec 029 FR-024, "
            f"contracts/screen-shapes.md §6). Until it lands, `rule_refusal_rate` and "
            f"`shape_refusals` are UNMEASURED for every {screen} answer -- not zero, and not met."
            + own)


_PREREQUISITE = {screen: _prerequisite(screen) for screen in _SHAPE_MARKERS}


def shapes_taken(keel_cloud: Path) -> dict:
    """Which of the seven screens keel-cloud's validator takes, read off the validator itself.

    `{screen: True|False}`, and every screen `False` when the file cannot be read at all -- an
    unreadable sibling is a prerequisite that has not landed, not a capability to assume.
    """
    try:
        source = (Path(keel_cloud) / _TOOL).read_text(encoding="utf-8")
    except OSError:
        return {screen: False for screen in _SHAPE_MARKERS}
    return {screen: bool(_taken_by(screen).search(source)) for screen in _SHAPE_MARKERS}


def _taken_by(screen: str):
    """The constant reference **or** an enum `switch` label naming `screen` -- 058's validator
    dispatches the vector screens as `case CONTEXT_INTERPRET -> ...` inside `switch (screen)`,
    where Java forbids the qualified name, so reading only `InferenceScreen.X` left three screens
    it does take unmeasured (run 20261008T001657Z). Prose still never counts: a label needs
    `case` before it and `->`/`:`/`,` after it."""
    name = re.escape(screen)
    return re.compile(rf"InferenceScreen\.{name}\b|\bcase\s+(?:[A-Z_]+\s*,\s*)*{name}\s*(?:->|:|,)")


def shapes_needed(batch: dict) -> set:
    """The screens this batch actually carries, so a run is never failed for a kind it never
    reached for."""
    return {case.get("screen") for case in batch.get("cases") or []
            if case.get("screen") in _SHAPE_MARKERS}


def unmet_by_screen(keel_cloud: Path, batch: dict) -> dict:
    """`{screen: sentence}` for each screen this batch carries that the validator does not take.

    **Never softened to a warning and never scored as a refusal** (FR-024, 025 FR-019): the caller
    leaves the aggregate's two marks unmeasured for that kind, by name, and an unmeasured mark is
    not a met mark (judgement call 13).
    """
    taken = shapes_taken(keel_cloud)
    return {screen: _PREREQUISITE[screen] for screen in sorted(shapes_needed(batch))
            if not taken.get(screen)}


def unmet_prerequisites(keel_cloud: Path, batch: dict) -> list:
    """`unmet_by_screen`'s sentences, as a list."""
    return list(unmet_by_screen(keel_cloud, batch).values())


def without_screens(batch: dict, screens) -> dict:
    """The batch less the cases of `screens` -- a kind the validator does not take is not sent to
    be refused for the wrong reason; it is reported unmeasured instead."""
    return {"cases": [c for c in batch.get("cases") or [] if c.get("screen") not in screens]}


def build_batch(cases_and_results) -> dict:
    """One batch from every case that produced a result the aggregate can be asked about, in
    `contracts/screen-shapes.md` §6's shape -- **one entry kind per screen**, each carrying the
    state its `ScreenResultApplier` reads: the vector and the registry slice's keys on a
    calibration case; the part, the link, the plan and the founder's option sets **and values** on
    a respondent case (`R3` is checked against values the model was never shown, so the validator
    needs the state the screen would really have arrived into -- 025 D12/D18); the invitation and
    the story on an `INTERPRET` case; the context and the seed on the interpretations; the
    standings on `BRIEF`. A `COMPARE` row is never batched.
    """
    cases = []
    for item in cases_and_results:
        case, result = item[0], item[1]
        if result is None or case.kind == "COMPARE":
            continue
        context = case.payload.get("context") or {}
        seed = (case.payload.get("input") or {}).get("content") or None
        # A redraw (call 41) is judged against the state its case's first draft arrived into, and
        # is told apart by its id: `<case_id>#redraw`.
        case_id = item[2] if len(item) > 2 and item[2] else case.case_id
        entry = {"case_id": case_id, "screen": case.screen}
        if case.kind == "CONTEXT":
            entry.update(market=context.get("market"), context_fields=context.get("context_fields"))
        elif case.kind == "FRAME":
            entry.update(market=context.get("market"), context=context.get("context"))
            if case.screen == "SOLUTION_MECHANISM":
                entry["problem_statement"] = (context.get("problem") or {}).get("statement") \
                    or context.get("problem_statement")
            entry["seed"] = seed
        elif case.kind == "CALIBRATION":
            # Every key the job's prompt context carried (context with its window, market, the
            # dimensions...), the same dict the runner built -- keel-cloud 058 (4ea3062) rebuilds
            # the case from the entry's own corridor and falls back to Lullaby's for what it lacks.
            entry.update(dict(context))
            entry.update(market=context.get("market"), vector=case.meta.get("vector"),
                         context=context.get("context"),
                         registry_slice=list(case.meta.get("registry_slice") or []))
        elif case.kind == "RESPONDENT":
            # The same: context (and so the recall window R8 reads), market, items, founder_options
            # and -- on parts 2 and 3 of the primary link -- the mechanism, as the job was handed
            # them; then the validator-only state the model was never shown.
            entry.update(dict(context))
            entry.update(market=context.get("market"), part=case.meta.get("part"),
                         link=case.meta.get("link"), plan=list(case.meta.get("plan") or []),
                         founder_options=context.get("founder_options"),
                         founder_values=case.meta.get("founder_values"))
        elif case.kind == "READING":
            entry.update(invitation_id=context.get("invitation_id"), story=context.get("story"))
        elif case.kind == "BRIEF":
            entry.update(market=context.get("market"), standings=context.get("vectors"))
        entry.update(case_id=case_id, screen=case.screen)     # never a context key's
        entry["result"] = result
        cases.append(entry)
    return {"cases": cases}


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


#: The id suffix a redraw's verdict carries in a batch and its report (judgement call 41).
REDRAW_SUFFIX = "#redraw"


def redraw_id(case_id: str) -> str:
    return f"{case_id}{REDRAW_SUFFIX}"


def is_redraw(case_id) -> bool:
    return str(case_id or "").endswith(REDRAW_SUFFIX)


def verdict(keel_cloud: Path, case, result, directory: Path, *, redraw: bool = False,
            timeout_s: float = 900.0) -> dict:
    """The aggregate's report entry for **one** answer, asked during the run (call 41) so that a
    rule refusal can be redrawn the way the cloud redraws it. One JVM start an answer, and the
    batch and report kept under `directory` as evidence. Raises `ContractUnavailable` as `run`
    does."""
    case_id = redraw_id(case.case_id) if redraw else case.case_id
    slug = "".join(c if c.isalnum() or c in "-_" else "-" for c in case_id).strip("-")
    batch = build_batch([(case, result, case_id)])
    report = run(keel_cloud, batch, Path(directory) / f"{slug}.batch.json",
                 Path(directory) / f"{slug}.report.json", timeout_s=timeout_s)
    for entry in report:
        if entry.get("case_id") == case_id:
            return entry
    raise ContractUnavailable(f"keel-cloud's validator returned no verdict for {case_id}")


def fold_in(report: list) -> dict:
    """The report, counted the way the marks read it.

    `refusals_by_rule` counts **rule refusals only** — a shape refusal never reached the aggregate,
    and a case refusal is the eval's own. `by_case` lets the report quote the aggregate's own words
    beside the diff that produced them.

    **Call 41.** An entry whose id ends `#redraw` is a redraw's verdict: a refusal of it is
    *counted* (a second rule refusal in `refusals_by_rule`, a shape refusal in `shape_refusals`)
    but it never joins the denominator -- `shown`, the first drafts the aggregate judged (accepted
    plus rule-refused, as since v6) -- and an accepted redraw is not a second acceptance.
    """
    by_case, rules = {}, {}
    accepted = shape = case_fault = shown_refused = 0
    redraws = redraws_accepted = second_refusals = 0
    for entry in report:
        by_case[entry.get("case_id")] = entry
        second = is_redraw(entry.get("case_id"))
        if second:
            redraws += 1
        if entry.get("accepted"):
            if second:
                redraws_accepted += 1
            else:
                accepted += 1
            continue
        refusal = entry.get("refusal") or {}
        kind = refusal.get("kind")
        if second and kind in ("rule", "shape"):
            second_refusals += 1
        if kind == "rule":
            rule = refusal.get("rule") or "unnamed"
            rules[rule] = rules.get(rule, 0) + 1
            if not second:
                shown_refused += 1
        elif kind == "shape":
            shape += 1
        else:
            case_fault += 1
    return {"accepted": accepted, "refusals_by_rule": rules, "shape_refusals": shape,
            "case_faults": case_fault, "shown": accepted + shown_refused,
            "redraws": redraws, "redraws_accepted": redraws_accepted,
            "second_refusals": second_refusals, "by_case": by_case}
