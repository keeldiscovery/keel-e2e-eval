"""The instruction bytes a job actually carries (spec 009 FR-003).

`InferenceInstructionRegistry.get(screen)` returns the resource's text `.strip()`ed, and that is
exactly what `InferenceJobService.buildRequestPayload` puts at `request_payload["instruction"]`.
So this module reads the same file and strips it the same way, and does nothing else -- no
templating, no substitution, no trimming of its own. If the prose is wrong, the eval must be
measuring the wrong prose for the right reason.
"""

from __future__ import annotations

from pathlib import Path

# `InferenceScreen.resourceName()`'s own mapping, screen constant to file stem.
STEMS = {
    "PROBLEM_FRAME": "problem-frame",
    "PROBLEM_ASSUMPTIONS": "problem-assumptions",
    "SOLUTION_FRAME": "solution-frame",
    "SOLUTION_ASSUMPTIONS": "solution-assumptions",
    "SOLUTION_REFRAME": "solution-reframe",
    "COMMERCIAL_FRAME": "commercial-frame",
    "COMMERCIAL_ASSUMPTIONS": "commercial-assumptions",
    "COMMERCIAL_REFRAME": "commercial-reframe",
    "INTERPRET": "interpret",
    "QUESTIONS": "questions",
    # MARKS_VERSION 9 (spec 029 W4): the five new templates, keel-cloud 059-063. The stems above
    # stay -- keel-cloud keeps those files while today's product still ships -- but no v9 case reads
    # them.
    "CONTEXT_INTERPRET": "context-interpret",
    "PROBLEM_INTERPRET": "problem-interpret",
    "SOLUTION_MECHANISM": "solution-mechanism",
    # keel-cloud 087: the screen keeps its name, its instruction is `founder-lists.md`; 088: `asked.md`.
    "CALIBRATION_QUESTIONS": "founder-lists",
    "RESPONDENT_QUESTIONS": "respondent-questions",
    "ASKED": "asked",
}


class InstructionUnavailable(RuntimeError):
    """The instruction resource is not where keel-cloud keeps it."""


def path_for(keel_cloud: Path, screen: str) -> Path:
    try:
        stem = STEMS[screen]
    except KeyError:
        raise InstructionUnavailable(f"no instruction stem known for screen {screen}") from None
    return Path(keel_cloud) / "src" / "main" / "resources" / "keel" / "inference-instructions" \
        / f"{stem}.md"


def read(keel_cloud: Path, screen: str) -> str:
    path = path_for(keel_cloud, screen)
    if not path.is_file():
        raise InstructionUnavailable(f"no instruction at {path}")
    return path.read_text(encoding="utf-8").strip()
