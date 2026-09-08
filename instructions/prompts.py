"""The prompt, built by keel-runtime rather than written here (spec 009 FR-004).

`request_payload` is `InferenceJobService.buildRequestPayload`'s shape, including the
empty-content sentinel an auto screen carries -- `InferenceOrchestrator.start` passes `""` for a
screen with nothing founder-typed, and that empty string is what reaches the prompt's
`founder_text:` line. The rendering itself is `keel_runtime.executor.build_prompt`, imported and
never copied: the nonce fence, the `SOURCE MATERIAL` heading and the `TASK`/`CONTRACT` ordering
are the runtime's to define, and a copy of them here would be a second prompt to keep in step.
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path


class RuntimeUnavailable(RuntimeError):
    """keel-runtime could not be imported -- a reason to stop, never a score."""


def load_runtime(keel_runtime: Path):
    """Imports `keel_runtime` from the sibling checkout named in `stack.toml`.

    Put on `sys.path` rather than vendored, for the same reason the contract is exported rather
    than copied: this repo floats at sibling HEAD, and a prompt built from a stale copy of the
    runtime would be a prompt production never sends.
    """
    keel_runtime = Path(keel_runtime).resolve()
    package = keel_runtime / "keel_runtime" / "__init__.py"
    if not package.is_file():
        raise RuntimeUnavailable(
            f"no keel_runtime package at {keel_runtime} -- this eval imports keel-runtime's own "
            "build_prompt and executor, and copies neither")
    if str(keel_runtime) not in sys.path:
        sys.path.insert(0, str(keel_runtime))
    if importlib.util.find_spec("keel_runtime") is None:
        raise RuntimeUnavailable(f"{keel_runtime} is not importable as `keel_runtime`")
    import keel_runtime.executor as executor          # noqa: PLC0415 - deliberate late import
    import keel_runtime.response_validator as validator  # noqa: PLC0415
    return executor, validator


@dataclass
class Case:
    """One prompt this run would send, and everything needed to explain it afterwards."""

    case_id: str
    kind: str                 # ASSUMPTIONS | READING | BRIEF
    entry_id: str
    screen: str
    subject: str              # the stage, or the person
    run_index: int
    payload: dict
    prompt: str = ""
    existing_roles: list = field(default_factory=list)

    @property
    def bundle_path(self) -> str:
        return f"{self.entry_id}/{_slug(self.subject)}/run{self.run_index}"


def _slug(text: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "-" for c in text).strip("-")


def payload_for(instruction: str, context: dict, response_contract: dict) -> dict:
    """`InferenceJobService.buildRequestPayload`'s four keys, in its order."""
    return {
        "instruction": instruction,
        "context": context,
        "interaction_history": [],
        "input": {"content": ""},
        "response_contract": response_contract,
    }


def render(executor_module, payload: dict, *, job_id: str = "eval") -> str:
    """keel-runtime's own `build_prompt`. The nonce is fresh on every call, by design."""
    request = executor_module.InferenceRequest(
        job_id=job_id, interaction_id=job_id, turn_number=1, request_payload=payload)
    return executor_module.build_prompt(request)


def build_cases(entry, exported, instructions_by_screen, executor_module, *, n_runs: int = 3,
                stages=("PROBLEM", "SOLUTION", "COMMERCIAL")) -> list:
    """Every case one corpus entry produces: three assumption screens and one reading per person.

    `n_runs` repeats each case, because a case that passes twice and fails once is an unstable
    instruction rather than a two-thirds one -- `score.py` reports the spread and averages nothing
    before it reports it.
    """
    from . import context as context_mod          # noqa: PLC0415 - avoids a circular import
    from .contract import (SCREEN_BRIEF, SCREEN_READING,        # noqa: PLC0415
                            SCREENS_ASSUMPTIONS)

    cases = []
    for stage in stages:
        screen = SCREENS_ASSUMPTIONS[stage]
        keys = exported.keys_for(screen)
        contract = exported.for_screen(screen)
        roles = context_mod.roles_for(entry, stage)
        context = context_mod.build_assumptions(entry, stage, keys)
        payload = payload_for(instructions_by_screen[screen], context, contract)
        for run_index in range(1, n_runs + 1):
            case = Case(
                case_id=f"{entry.id}/{stage}/run{run_index}",
                kind="ASSUMPTIONS", entry_id=entry.id, screen=screen, subject=stage,
                run_index=run_index, payload=payload, existing_roles=roles)
            case.prompt = render(executor_module, payload, job_id=_slug(case.case_id))
            cases.append(case)

    keys = exported.keys_for(SCREEN_READING)
    contract = exported.for_screen(SCREEN_READING)
    for person in entry.people():
        context = context_mod.build_reading(entry, person, keys)
        if not context.get("anchors"):
            # Nobody wrote anything: production would never have started a reading at all.
            continue
        payload = payload_for(instructions_by_screen[SCREEN_READING], context, contract)
        for run_index in range(1, n_runs + 1):
            case = Case(
                case_id=f"{entry.id}/{person.person}/run{run_index}",
                kind="READING", entry_id=entry.id, screen=SCREEN_READING,
                subject=person.person, run_index=run_index, payload=payload)
            case.prompt = render(executor_module, payload, job_id=_slug(case.case_id))
            cases.append(case)

    # The BRIEF screen: one case an entry, because there is one paragraph a project. It is built
    # last for the same reason production writes it last -- it is what a founder reads once every
    # stage has been approved and every answer read.
    keys = exported.keys_for(SCREEN_BRIEF)
    contract = exported.for_screen(SCREEN_BRIEF)
    context = context_mod.build_brief(entry, keys)
    payload = payload_for(instructions_by_screen[SCREEN_BRIEF], context, contract)
    for run_index in range(1, n_runs + 1):
        case = Case(
            case_id=f"{entry.id}/BRIEF/run{run_index}",
            kind="BRIEF", entry_id=entry.id, screen=SCREEN_BRIEF, subject="BRIEF",
            run_index=run_index, payload=payload)
        case.prompt = render(executor_module, payload, job_id=_slug(case.case_id))
        cases.append(case)
    return cases
