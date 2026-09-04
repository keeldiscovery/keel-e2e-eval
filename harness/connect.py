"""Runs keel-connect-skill's own script to start the runtime (spec 005-connect-stack FR-007,
edge cases): the harness never shells `python3 -m keel_runtime` itself -- the connect skill is
one of the four applications this repo referees, so starting the runtime through anything else
would leave it un-refereed. `keel_connect_check.py`'s own stable contract
(`keel-connect-skill/specs/001-keel-connect-check/contracts/skill-script-output.md`) is the only
thing this module depends on; everything about the script's *internals* may change without this
module changing too.

US2 step 1: the browser then opens whatever `verification_uri` this hands back -- a keel-web URL,
because `stack/cloud.py` points `KEEL_V2_CONNECT_VERIFICATION_URI` at keel-web's own `/connect`.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time

from stack.config import StackConfig
from stack.runtime import home_dir
from stack import runtime as stack_runtime

DEFAULT_WAIT_SECONDS = 15


class RuntimeUnavailable(RuntimeError):
    """The script reported `runtime_unavailable` or `internal_error` -- no usable keel-runtime
    could be found or launched at all."""


class AuthorizationPendingTimeout(RuntimeError):
    """The script reported `authorization_pending_timeout` (spec 005 edge cases: this is a
    recorded stack failure, not merely "try again" -- a healthy connect skill script, against a
    healthy keel-runtime, reports a launch signal well within its own default wait window)."""


def _run_connect_check_script(config: StackConfig, recorder, *, step_name: str,
                               wait_seconds: float) -> dict:
    """The one place `keel_connect_check.py` is ever shelled out from -- `start_runtime_via_skill`
    (the first connect) and `reconnect` (spec 006-agent-optional US1 step 7) are two differently-
    named callers of the exact same invocation; the script itself has no notion of "first" vs
    "again" connect, only whatever `stack.runtime.status` finds when it starts."""
    script_path = config.connect_check_script_path
    cloud_base_url = f"http://localhost:{config.cloud_port}"
    cmd = [
        sys.executable, str(script_path),
        "--runtime-path", str(config.keel_runtime),
        "--base-url", cloud_base_url,
        "--executor", "scripted",
        "--credential-backend", "file",
        "--no-browser",
        "--home", str(home_dir(config)),
        "--wait-seconds", str(wait_seconds),
    ]

    with recorder.step(step_name, party="stack", kind="protocol") as h:
        try:
            completed = subprocess.run(cmd, capture_output=True, text=True, timeout=wait_seconds + 30)
        except (OSError, subprocess.TimeoutExpired) as exc:
            h.record_wire({"cmd": cmd}, {"error": str(exc)})
            h.fail(f"could not run keel_connect_check.py: {exc}")
            raise RuntimeUnavailable(str(exc)) from exc

        stdout = completed.stdout.strip()
        try:
            body = json.loads(stdout.splitlines()[-1]) if stdout else {}
        except (json.JSONDecodeError, IndexError) as exc:
            h.record_wire({"cmd": cmd}, {"stdout": completed.stdout, "stderr": completed.stderr})
            h.fail(f"keel_connect_check.py did not print one line of JSON: {exc}")
            raise RuntimeUnavailable(
                f"keel_connect_check.py produced no parseable JSON (stderr: {completed.stderr!r})"
            ) from exc

        h.record_wire({"cmd": cmd}, body)
        outcome = body.get("outcome")

        if outcome in ("runtime_unavailable", "internal_error"):
            h.fail(f"{outcome}: {body.get('message')}")
            raise RuntimeUnavailable(f"{outcome}: {body.get('message')}")

        if outcome == "authorization_pending_timeout":
            h.fail(f"authorization_pending_timeout: {body.get('message')}")
            raise AuthorizationPendingTimeout(body.get("message", "authorization_pending_timeout"))

        if outcome not in ("authorization_started", "connected", "already_connected"):
            h.fail(f"unrecognized outcome from keel_connect_check.py: {outcome!r}")
            raise RuntimeUnavailable(f"unrecognized outcome from keel_connect_check.py: {outcome!r}")

        return body


def start_runtime_via_skill(config: StackConfig, recorder, *,
                             wait_seconds: float = DEFAULT_WAIT_SECONDS) -> dict:
    """Runs `keel_connect_check.py` exactly as spec US2 step 1 shows, parses its one line of JSON,
    and records the call as one step (`party="stack"`, since starting the runtime is stack
    plumbing, not a founder- or agent-observed moment -- the smoke's own interaction scopes begin
    once the browser reacts to what this returns).

    Returns the parsed JSON body verbatim (contract's `outcome` plus whatever fields that outcome
    carries) on `authorization_started`/`connected`/`already_connected`; raises
    `RuntimeUnavailable` for `runtime_unavailable`/`internal_error`, and
    `AuthorizationPendingTimeout` for `authorization_pending_timeout` (both after recording the
    step as failed, so the transcript shows exactly what the script said).
    """
    return _run_connect_check_script(
        config, recorder, step_name="keel-connect-skill: start the runtime", wait_seconds=wait_seconds)


def stop_runtime(config: StackConfig, recorder, *, timeout_s: float = 15) -> None:
    """Spec 006-agent-optional (FR-002, US1 step 1): stops a runtime this session started, the
    same way `make down`/`stack/lifecycle.teardown` does -- `stack.runtime.kill`'s own SIGTERM by
    heartbeat pid, never `python3 -m keel_runtime` shelled directly (this stack never launches the
    runtime itself; it only ever stops one it -- or a prior session -- already launched through
    the connect skill).

    Waits for `stack.runtime.status` to read not-running before returning: a fire-and-forget
    SIGTERM racing the scenario's very next assertion (that a fresh login has nothing to bind) is
    exactly the kind of flake this repo's other waits are written to avoid. Idempotent, like
    `runtime.kill` itself -- a no-op, recorded as such, if the runtime was already stopped.
    """
    with recorder.step("the runtime is stopped (heartbeat pid, as `make down` does)",
                        party="stack", kind="protocol") as h:
        before = stack_runtime.status(config)
        h.record_wire(None, {"before": before})
        stack_runtime.kill(config)
        deadline = time.monotonic() + timeout_s
        after = stack_runtime.status(config)
        while after.get("running", False) and time.monotonic() < deadline:
            time.sleep(0.2)
            after = stack_runtime.status(config)
        h.record_wire(None, {"after": after})
        if after.get("running", False):
            h.fail(f"runtime still reports running {timeout_s}s after SIGTERM: {after}")
            raise RuntimeError(f"runtime did not stop within {timeout_s}s: {after}")


def reconnect(config: StackConfig, recorder, *,
              wait_seconds: float = DEFAULT_WAIT_SECONDS) -> dict:
    """Spec 006-agent-optional (FR-002, US1 step 7): reruns keel-connect-skill's own script fresh,
    exactly as the first connect does. Edge cases: "reconnecting mints a new device authorization
    -- the old one is spent" -- the runtime process this session previously started was stopped by
    `stop_runtime` above, and the keel session it was bound to was closed by logging out, so this
    is expected to come back `authorization_started` with a brand-new `verification_uri`/user
    code, not a resume of the old one.
    """
    return _run_connect_check_script(
        config, recorder, step_name="keel-connect-skill: reconnect the runtime", wait_seconds=wait_seconds)
