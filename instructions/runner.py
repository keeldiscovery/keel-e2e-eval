"""Calling the model, and refusing to start when it cannot be called (spec 009 FR-006/7/8).

The pre-flight is in the shape of S-004's own `_claude_ready()`, and for the same reason: a run
that cannot reach the model has measured nothing, and a harness that reported that as a bad
instruction would be lying about keel-cloud. So every prerequisite -- `claude` on PATH and logged
in, the keel-cloud checkout and its exporter, the corpus, keel-runtime's importable executor -- is
checked before a penny is spent, and a failure prints the reason and stops.

The call itself is `keel_runtime.executor.ClaudeCodeExecutor`, imported and never copied. That is
the whole point: the closed, tool-less, session-less argv, the nonce-fenced prompt, the
`--json-schema` envelope built from the response contract and the one recovery pass are the
runtime's own behaviour, and an eval that reproduced them would eventually measure a prompt
production does not send.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path


class NotReady(RuntimeError):
    """A prerequisite is missing. Printed with its reason; never scored."""


LOCK_NAME = ".instruction-eval.lock"

# `ClaudeCodeExecutor`'s own words when `--json-schema` was never satisfied in max_turns.
NEVER_FIT_MARKER = "the answer never fit its shape"


def preflight(config, *, dry_run: bool = False) -> dict:
    """Everything that must be true before the first call. Returns what it learned."""
    facts = {}

    keel_cloud = Path(config.keel_cloud)
    if not (keel_cloud / "gradlew").is_file():
        raise NotReady(f"no keel-cloud checkout at {keel_cloud} (stack.toml [paths].keel_cloud)")
    corpus_dir = keel_cloud / "canon" / "designs" / "measured-beliefs" / "corpus"
    if not corpus_dir.is_dir() or not any(corpus_dir.glob("*.yaml")):
        raise NotReady(f"no frozen corpus at {corpus_dir} -- keel-cloud spec 028 must be on this "
                       "checkout's branch")

    keel_runtime = Path(config.keel_runtime)
    if not (keel_runtime / "keel_runtime" / "executor.py").is_file():
        raise NotReady(f"no keel-runtime checkout at {keel_runtime} -- this eval imports its "
                       "build_prompt and ClaudeCodeExecutor")

    if dry_run:
        facts["claude_version"] = None
        return facts

    if shutil.which("claude") is None:
        raise NotReady("no `claude` on PATH -- this eval calls a real model through the Claude "
                       "Code CLI, exactly as a founder's own runtime would")
    facts["claude_version"] = _claude_version()
    reason = _claude_ready()
    if reason:
        raise NotReady(reason)
    return facts


def _claude_version() -> str | None:
    try:
        done = subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=30)
        return done.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def _claude_ready() -> str | None:
    """A reason to stop, or `None`. The probe costs well under a cent (S-004's own shape)."""
    try:
        done = subprocess.run(
            ["claude", "-p", "--tools", "", "--max-turns", "1", "--output-format", "json",
             "--no-session-persistence", "Reply with the single word ok."],
            capture_output=True, text=True, timeout=120)
        body = json.loads(done.stdout.strip().splitlines()[-1]) if done.stdout.strip() else {}
    except Exception as exc:                      # noqa: BLE001 - any failure is a reason to stop
        return f"`claude -p` did not answer: {exc}"
    if body.get("is_error"):
        return f"`claude` is not usable here: {body.get('result')!r}"
    return None


class RunLock:
    """One instruction eval at a time.

    Two runs would share the `claude` CLI's own rate limit and the founder's own account, and
    neither's cost figure would mean anything. The lock is a file in `runs/`, released on exit.
    """

    def __init__(self, runs_dir: Path):
        self.path = Path(runs_dir) / LOCK_NAME

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise NotReady(
                f"another instruction eval holds {self.path} (started "
                f"{self.path.read_text(errors='replace').strip()}). Wait for it, or delete the "
                "lock if it is stale -- two runs would share one account's rate limit and "
                "neither's cost would mean anything.") from None
        os.write(fd, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()).encode())
        os.close(fd)
        return self

    def __exit__(self, *exc):
        self.path.unlink(missing_ok=True)
        return False


@dataclass
class Answer:
    """One model call, and everything needed to explain it afterwards."""

    case_id: str
    outcome: str | None = None
    result: dict | None = None
    questions: list | None = None
    schema_valid: bool = False
    schema_error: str | None = None
    envelope: dict = field(default_factory=dict)
    recovery_pass: bool = False
    num_turns: int | None = None
    total_cost_usd: float | None = None
    duration_s: float = 0.0
    error: str | None = None          # ExecutorUnavailable/Timeout: not a score
    never_fit: bool = False           # the model failed the contract, which IS a score

    @property
    def errored(self) -> bool:
        return self.error is not None and not self.never_fit


def ask(executor_module, validator_module, executor, case) -> Answer:
    """One case, one call. An executor failure is recorded as an error, never as a bad answer."""
    request = executor_module.InferenceRequest(
        job_id=_job_id(case), interaction_id=_job_id(case), turn_number=1,
        request_payload=case.payload)
    started = time.monotonic()
    answer = Answer(case_id=case.case_id)
    # `ClaudeCodeExecutor` sets `last_envelope` only after a call that got that far, so a timeout
    # would leave the *previous* case's envelope standing and this bundle would file it under the
    # wrong case id. Every number in a report must trace to an envelope that belongs to it, so the
    # slate is cleared first: a timed-out case carries no envelope rather than someone else's.
    executor.last_envelope = None
    try:
        response = executor.execute(request)
    except (executor_module.ExecutorUnavailable, executor_module.ExecutorTimeout,
            executor_module.ExecutorAuthFailure) as exc:
        answer.error = f"{type(exc).__name__}: {exc}"
        # `ClaudeCodeExecutor` raises ExecutorUnavailable for two very different things, and this
        # eval must not report them as one. "The answer never fit its shape" is `error_max_turns`
        # after a schema refusal: the model was reached, was told the contract, and could not
        # satisfy it in six turns -- which is a *measurement of the instruction*, and precisely the
        # finding a baseline against pre-029 prose exists to record. A missing binary or a dead CLI
        # is a harness failure and measures nothing. Only the second sets `errored`.
        answer.never_fit = NEVER_FIT_MARKER in str(exc)
        if answer.never_fit:
            answer.schema_error = str(exc)
        answer.duration_s = time.monotonic() - started
        answer.envelope = executor.last_envelope or {}
        return answer
    except executor_module.InvalidResponse as exc:
        # The envelope came back but carried no usable structured output: the model failed to
        # answer the contract at all, which is a measurement, not an executor failure.
        answer.schema_error = str(exc)
        answer.duration_s = time.monotonic() - started
        answer.envelope = executor.last_envelope or {}
        return answer

    answer.duration_s = time.monotonic() - started
    answer.envelope = executor.last_envelope or {}
    answer.recovery_pass = bool(answer.envelope.get("recovery_pass"))
    answer.num_turns = answer.envelope.get("num_turns")
    answer.total_cost_usd = answer.envelope.get("total_cost_usd")

    contract = case.payload.get("response_contract") or {}
    try:
        validator_module.validate_response(response, contract)
        answer.schema_valid = True
    except validator_module.InvalidResponse as exc:
        answer.schema_error = str(exc)

    answer.outcome = response.get("outcome") if isinstance(response, dict) else None
    if isinstance(response, dict):
        answer.result = response.get("result")
        answer.questions = response.get("questions")
    return answer


def _job_id(case) -> str:
    return "".join(c if c.isalnum() else "-" for c in case.case_id).strip("-")
