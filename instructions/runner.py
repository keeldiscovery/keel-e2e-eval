"""Calling the model, and refusing to start when it cannot be called (spec 009 FR-006/7/8).

The pre-flight is in the shape of S-004's own `_claude_ready()`, and for the same reason: a run
that cannot reach the model has measured nothing, and a harness that reported that as a bad
instruction would be lying about keel-cloud. So every prerequisite -- **this host's** CLI on PATH
and logged in, the keel-cloud checkout and its exporter, the corpus, keel-runtime's importable
executor -- is checked before a penny is spent, and a failure prints the reason and stops.

The call itself is keel-runtime's own executor, imported and never copied. That is the whole
point: the closed, tool-less, session-less argv, the nonce-fenced prompt, the envelope built from
the response contract and the one recovery pass are the runtime's own behaviour, and an eval that
reproduced them would eventually measure a prompt production does not send.

**Two hosts** (spec 014; keel-cloud `canon/designs/keel-skill-design.md` §5). `host` decides which
CLI is required and probed here, and nothing else in this module. The binary's name is read out of
keel-runtime's `EXECUTOR_BINARIES` rather than written down again, so `claude-code`'s permanent
alias and any future name are the runtime's to define.

**The Copilot probe costs a premium request, and is taken anyway.** One call against a hundred and
thirty-one is the cheapest insurance in a metered run, and FR-006/7/8's rule does not soften for a
host that bills differently. It is decided **by the JSONL, never by the exit code** (design §5.4,
C-3): 1.0.83 was measured exiting 0 on a run whose task had failed, and exiting 1 with no JSONL at
all on a bogus token.
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


def preflight(config, *, dry_run: bool = False, host: str = "claude",
              executor_module=None) -> dict:
    """Everything that must be true before the first call. Returns what it learned."""
    facts = {"host": host}

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

    if executor_module is None:
        from . import prompts as prompts_mod      # noqa: PLC0415 - avoids a circular import
        executor_module, _ = prompts_mod.load_runtime(keel_runtime)

    binary = binary_for(executor_module, host)
    facts["cli"] = binary

    if dry_run:
        facts["cli_version"] = None
        return facts

    if shutil.which(binary) is None:
        raise NotReady(
            f"no `{binary}` on PATH -- this eval calls a real model through the {host} CLI, "
            "exactly as a founder's own runtime would")
    facts["cli_version"] = _cli_version(binary)
    if host == "copilot":
        reason = _copilot_ready(binary, executor_module)
    elif host == "codex":
        reason = _codex_ready(binary, executor_module)
    else:
        reason = _claude_ready(binary)
    if reason:
        raise NotReady(reason)
    return facts


def binary_for(executor_module, host: str) -> str:
    """Which CLI this host needs, **from keel-runtime's own table** (spec 014 FR-002).

    `EXECUTOR_BINARIES` is `keel_runtime.config`'s, re-read here rather than written down again:
    one place decides that `claude-code` means `claude`, and it is not this one. A host the
    runtime has no binary for is a refusal naming the ones it has -- never a guess, and never
    `host` itself used as a command.
    """
    resolve = getattr(executor_module, "canonical_executor_name", None)
    canonical = resolve(host) if callable(resolve) else host
    try:
        from keel_runtime.config import EXECUTOR_BINARIES  # noqa: PLC0415 - late by design
    except ImportError as exc:                    # pragma: no cover - load_runtime ran first
        raise NotReady(f"keel-runtime's config is not importable: {exc}") from exc
    try:
        return EXECUTOR_BINARIES[canonical]
    except KeyError:
        known = ", ".join(sorted(EXECUTOR_BINARIES))
        raise NotReady(
            f"keel-runtime knows no CLI for host {host!r}; it knows: {known}") from None


def _cli_version(binary: str) -> str | None:
    try:
        done = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=30)
        return done.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def _claude_ready(binary: str = "claude") -> str | None:
    """A reason to stop, or `None`. The probe costs well under a cent (S-004's own shape)."""
    try:
        done = subprocess.run(
            [binary, "-p", "--tools", "", "--max-turns", "1", "--output-format", "json",
             "--no-session-persistence", "Reply with the single word ok."],
            capture_output=True, text=True, timeout=120)
        body = json.loads(done.stdout.strip().splitlines()[-1]) if done.stdout.strip() else {}
    except Exception as exc:                      # noqa: BLE001 - any failure is a reason to stop
        return f"`{binary} -p` did not answer: {exc}"
    if body.get("is_error"):
        return f"`{binary}` is not usable here: {body.get('result')!r}"
    return None


def _copilot_ready(binary: str, executor_module) -> str | None:
    """A reason to stop, or `None`. One premium request, in the executor's own closed shape.

    **The exit code is not consulted** (C-3). What is: whether any `session.error` appeared, and
    whether an authentication marker appeared in it or on stderr -- keel-runtime's own
    `COPILOT_AUTH_MARKERS`, since the string that means "not logged in" is a measurement of a CLI
    and belongs where it was measured, not in a second copy here.
    """
    excluded = getattr(executor_module, "COPILOT_EXCLUDED_TOOLS", ()) or ()
    argv = [binary, "-p", "Reply with the single word ok."]
    argv += [f"--excluded-tools={tool}" for tool in excluded]
    argv += ["--disable-builtin-mcps", "--no-custom-instructions", "--no-ask-user", "--no-remote",
             "--no-remote-export", "--no-auto-update", "--no-color",
             "--output-format", "json", "--log-level", "none"]
    try:
        done = subprocess.run(argv, capture_output=True, text=True, timeout=180)
    except Exception as exc:                      # noqa: BLE001 - any failure is a reason to stop
        return f"`{binary} -p` did not answer: {exc}"

    events = _jsonl(done.stdout)
    errors = [_event_text(e) for e in events if e.get("type") == "session.error"]
    stderr = (done.stderr or "").strip()
    markers = [m.lower() for m in getattr(executor_module, "COPILOT_AUTH_MARKERS", ()) or ()]
    for text in [stderr] + errors:
        if text and any(marker in text.lower() for marker in markers):
            return (f"`{binary}` is not logged in here: {text.splitlines()[0]} -- log in with "
                    f"`{binary}` (or set COPILOT_GITHUB_TOKEN) before spending a run")
    if errors:
        return f"`{binary}` answered with a session error: {'; '.join(errors)}"
    if not events:
        return (f"`{binary} -p` produced no JSONL at all "
                f"(exit {done.returncode}): {stderr or 'no stderr'}")
    return None


def _codex_ready(binary: str, executor_module) -> str | None:
    """A reason to stop, or `None`. One short call in the executor's own closed shape
    (keel-runtime spec 008): `codex exec -` with the runtime's `CODEX_EXEC_FLAGS` and every
    `CODEX_DISABLED_FEATURES` flag, the prompt on stdin. The exit code is not consulted; the
    `error`/`turn.failed` events and stderr are, against keel-runtime's own `CODEX_AUTH_MARKERS`,
    for the reason `_copilot_ready` gives."""
    flags = list(getattr(executor_module, "CODEX_EXEC_FLAGS", ()) or ())
    disabled = getattr(executor_module, "CODEX_DISABLED_FEATURES", ()) or ()
    argv = [binary, "exec", "-"] + flags
    for feature in disabled:
        argv += ["--disable", feature]
    try:
        done = subprocess.run(argv, input="Reply with the single word ok.",
                              capture_output=True, text=True, timeout=180)
    except Exception as exc:                      # noqa: BLE001 - any failure is a reason to stop
        return f"`{binary} exec` did not answer: {exc}"

    events = _jsonl(done.stdout)
    errors = []
    for event in events:
        if event.get("type") == "error":
            errors.append(str(event.get("message") or event))
        elif event.get("type") == "turn.failed":
            errors.append(str((event.get("error") or {}).get("message") or event))
    stderr = (done.stderr or "").strip()
    markers = [m.lower() for m in getattr(executor_module, "CODEX_AUTH_MARKERS", ()) or ()]
    for text in [stderr] + errors:
        if text and any(marker in text.lower() for marker in markers):
            return (f"`{binary}` is not logged in here: {text.splitlines()[0]} -- run "
                    f"`{binary} login` before spending a run")
    if errors:
        return f"`{binary}` answered with an error: {'; '.join(errors)}"
    if not events:
        return (f"`{binary} exec` produced no JSONL at all "
                f"(exit {done.returncode}): {stderr or 'no stderr'}")
    return None


def _jsonl(stdout: str) -> list:
    """Every JSON object on its own line. Not `_parse_stream_events`: that one is the executor's,
    and this probe is the referee's own, with nothing riding on it but a yes or a no."""
    events = []
    for line in (stdout or "").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            parsed = json.loads(line)
        except ValueError:
            continue
        if isinstance(parsed, dict):
            events.append(parsed)
    return events


def _event_text(event: dict) -> str:
    data = event.get("data") or {}
    for key in ("message", "error", "reason"):
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
    return json.dumps(data)


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
    # spec 014 / design §5.4 C-7: Copilot reports premium requests and no dollars, and the
    # runtime never invents a figure it was not given. So does this eval: one of these two is
    # `None` on every run, and neither is filled in from the other.
    premium_requests: float | None = None
    # keel-runtime spec 008: Codex reports tokens against a plan -- `usage` from the CLI's own
    # `turn.completed` -- and no dollars and no premium requests. Same rule: never converted.
    tokens: dict | None = None
    reported_model: str | None = None
    duration_s: float = 0.0
    error: str | None = None          # ExecutorUnavailable/Timeout: not a score
    never_fit: bool = False           # the model failed the contract, which IS a score

    @property
    def errored(self) -> bool:
        return self.error is not None and not self.never_fit


def _model_kwarg(executor_module, executor, request_payload: dict) -> dict:
    """The model the job names for this executor's host, resolved by keel-runtime's own rule.

    In production `keel_runtime.poller` reads `request_payload["model"][<host_key>]` into
    `InferenceRequest.model` before an executor sees the job (spec 009); this eval calls the
    executor directly and so must do the poller's one step itself -- through the poller's own
    function, never a second copy of the rule. A runtime older than 0.5.0 has neither the field
    nor the function, and gets nothing (its pin is on the executor, `models.apply_fallback`)."""
    import importlib  # noqa: PLC0415 - late, beside the late executor import
    try:
        poller = importlib.import_module(executor_module.__name__.rsplit(".", 1)[0] + ".poller")
        resolve = poller._model_for
    except (ImportError, AttributeError):
        return {}
    if "model" not in getattr(executor_module.InferenceRequest, "__dataclass_fields__", {}):
        return {}
    return {"model": resolve(executor, request_payload)}


def ask(executor_module, validator_module, executor, case) -> Answer:
    """One case, one call. An executor failure is recorded as an error, never as a bad answer."""
    request = executor_module.InferenceRequest(
        job_id=_job_id(case), interaction_id=_job_id(case), turn_number=1,
        request_payload=case.payload, **_model_kwarg(executor_module, executor, case.payload))
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
        answer.premium_requests = answer.envelope.get("premium_requests")
        answer.tokens = answer.envelope.get("tokens")
        answer.reported_model = reported_model(answer.envelope, executor)
        return answer
    except executor_module.InvalidResponse as exc:
        # The envelope came back but carried no usable structured output: the model failed to
        # answer the contract at all, which is a measurement, not an executor failure.
        answer.schema_error = str(exc)
        answer.duration_s = time.monotonic() - started
        answer.envelope = executor.last_envelope or {}
        answer.premium_requests = answer.envelope.get("premium_requests")
        answer.tokens = answer.envelope.get("tokens")
        answer.reported_model = reported_model(answer.envelope, executor)
        return answer

    answer.duration_s = time.monotonic() - started
    answer.envelope = executor.last_envelope or {}
    answer.recovery_pass = bool(answer.envelope.get("recovery_pass"))
    answer.num_turns = answer.envelope.get("num_turns")
    answer.total_cost_usd = answer.envelope.get("total_cost_usd")
    answer.premium_requests = answer.envelope.get("premium_requests")
    answer.tokens = answer.envelope.get("tokens")
    answer.reported_model = reported_model(answer.envelope, executor)

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


# ------------------------------------------------------------------------------- which model


def reported_model(envelope, executor=None) -> str | None:
    """The model the CLI says answered -- **whatever it says**, never a slug this repo assumed.

    Claude Code puts it in the envelope, as a string or as a `modelUsage` map of every model the
    call touched. Copilot puts it nowhere in `last_envelope` at all (`runs/DRIFT.md` #53): the
    router announces its choice in a `session.auto_mode_resolved` event, and `last_events` is the
    only place the run keeps it. That is one field read off a host's own stream, not a second copy
    of any behaviour -- and the design requires a measured run to name the model it measured
    (§5.4, C-5), so a run that could not name one records `None` and says so on the page rather
    than leaving the question open.
    """
    from_envelope = _model_of_envelope(envelope)
    if from_envelope:
        return from_envelope
    return _model_of_events(getattr(executor, "last_events", None))


def _model_of_envelope(envelope) -> str | None:
    if not isinstance(envelope, dict):
        return None
    for key in ("model", "modelUsage", "model_usage"):
        value = envelope.get(key)
        if isinstance(value, str) and value:
            return value
        if isinstance(value, dict) and value:
            return ", ".join(sorted(value))
    return None


# Where a Copilot run names its model, measured 2026-09-09 against CLI 1.0.83 and against the
# design's own reading of it (§5.4: *"`session.auto_mode_resolved.chosenModel`"*). Two places,
# because the router only announces a choice when it made one: a pinned `--model` run may emit no
# `auto_mode_resolved` at all, and then the usage checkpoint's per-model breakdown is the only
# record. Both are read; neither is guessed at.
_MODEL_EVENT_KEYS = ("chosenModel", "resolvedModel", "model")


def _model_of_events(events) -> str | None:
    """Every distinct model this run's own events name, in the order they first appeared."""
    seen = []

    def remember(value):
        if isinstance(value, str) and value and value not in seen:
            seen.append(value)

    for event in events or []:
        if not isinstance(event, dict):
            continue
        data = event.get("data") if isinstance(event.get("data"), dict) else {}
        if "auto_mode_resolved" in str(event.get("type") or ""):
            for key in _MODEL_EVENT_KEYS:
                remember(data.get(key))
        if event.get("type") == "session.usage_checkpoint":
            for entry in data.get("promptCacheBreakState") or []:
                if isinstance(entry, dict):
                    for name in (entry.get("models") or {}):
                        remember(name)
    return ", ".join(seen) or None
