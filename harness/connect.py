"""Runs keel-connect-skill's own script to start the runtime (spec 005-connect-stack FR-007,
edge cases): the harness never shells `python3 -m keel_runtime` itself -- the connect skill is
one of the four applications this repo referees, so starting the runtime through anything else
would leave it un-refereed. `keel_connect_check.py`'s own stable contract
(`keel-connect-skill/specs/001-keel-connect-check/contracts/skill-script-output.md`) is the only
thing this module depends on; everything about the script's *internals* may change without this
module changing too.

US2 step 1: the browser then opens whatever `verification_uri` this hands back -- a keel-web URL,
because `stack/cloud.py` points `KEEL_V2_CONNECT_VERIFICATION_URI` at keel-web's own `/connect`.

**Spec 012: the runtime the script starts is the one that travelled inside the skill.** Two lines
changed and both are the point (design §3.2, §13 step 9):

- `--runtime-path` is **not passed any more**. The skill resolves `<skill root>/keel_runtime/`
  itself -- rule 2 of its own resolution order, the rule a founder is on.
- `KEEL_RUNTIME_PATH` is **scrubbed from the environment** (`stack.runtime.scrubbed_env`), along
  with `KEEL_HOME` and `KEEL_BASE_URL`. Dropping the flag alone would not have been enough: this
  repo is worked on from shells that export `KEEL_RUNTIME_PATH` (keel-connect-playground's own
  walk-through environment does), and an inherited one would silently put the *checkout* back --
  a green run that never touched the runtime it claims to referee. The stack names the home and
  the base URL on the command line instead, so what the run says it did is what it did (T-1).

**Spec 011: the way out is the same discipline as the way in.** `stop_runtime_via_skill` shells
keel-connect-skill's *other* script, `scripts/keel_disconnect.py`, and never
`python3 -m keel_runtime disconnect` (keel-cloud `canon/designs/keel-disconnect-design.md` §8.4).
It is deliberately separate from `stop_runtime`, which is `make down`'s door and keeps the
fallback a teardown needs; see its own docstring for the one-sentence difference.

The seven outcomes of that script's contract are all recognised here, `python_too_old` included:
a referee that read an unknown outcome as "unrecognized" would report the wrong thing about the
one machine state -- an interpreter below the floor -- the skill exists to explain.
"""

from __future__ import annotations

import json
import subprocess
import sys

from stack.config import StackConfig
from stack.runtime import home_dir
from stack import runtime as stack_runtime

DEFAULT_WAIT_SECONDS = 15


class RuntimeUnavailable(RuntimeError):
    """The script reported `runtime_unavailable` or `internal_error` -- no usable keel-runtime
    could be found or launched at all."""


class PythonTooOld(RuntimeError):
    """The script reported `python_too_old` -- the interpreter running it is below keel-runtime's
    3.9 floor (design §3.3/§4). Nothing was resolved and nothing was run. Its own exception,
    because "the referee's interpreter is too old" is a fact about this machine, not a runtime
    that could not be found."""


class AuthorizationPendingTimeout(RuntimeError):
    """The script reported `authorization_pending_timeout` (spec 005 edge cases: this is a
    recorded stack failure, not merely "try again" -- a healthy connect skill script, against a
    healthy keel-runtime, reports a launch signal well within its own default wait window)."""


def _run_connect_check_script(config: StackConfig, recorder, *, step_name: str,
                               wait_seconds: float, executor: str = "scripted",
                               env_extra: dict[str, str] | None = None,
                               script_path=None) -> dict:
    """The one place `keel_connect_check.py` is ever shelled out from -- `start_runtime_via_skill`
    (the first connect) and `reconnect` (spec 006-agent-optional US1 step 7) are two differently-
    named callers of the exact same invocation; the script itself has no notion of "first" vs
    "again" connect, only whatever `stack.runtime.status` finds when it starts."""
    # `script_path` names another tree's copy of the script (S-013 runs an *older* bundle's);
    # the default is this stack's own skill checkout.
    script_path = script_path or config.connect_check_script_path
    cloud_base_url = config.cloud_base_url
    # The home is this stack's own (isolation, `stack/runtime.py`'s docstring) and it names its
    # Keel in a `config.json`, so the `status` call the script makes -- which is never given a
    # `--base-url` by its own contract -- still resolves this profile's address and answers with
    # an `environment` naming it.
    stack_runtime.ensure_home_names_keel(config)
    cmd = [
        sys.executable, str(script_path),
        "--base-url", cloud_base_url,
        "--executor", executor,
        "--credential-backend", "file",
        "--no-browser",
        "--home", str(home_dir(config)),
        "--wait-seconds", str(wait_seconds),
    ]

    with recorder.step(step_name, party="stack", kind="protocol") as h:
        try:
            # The skill script launches `keel connect` with the environment it inherits, so
            # `env_extra` reaches the runtime (spec 008-stranger FR-001: the canary's own marker).
            # Scrubbed first (spec 012 FR-004): no `KEEL_RUNTIME_PATH` reaches the script, so the
            # runtime it resolves can only be the one bundled inside it.
            env = stack_runtime.scrubbed_env(env_extra)
            completed = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", timeout=wait_seconds + 30, env=env)
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

        if outcome == "python_too_old":
            h.fail(f"python_too_old: {body.get('message')}")
            raise PythonTooOld(
                f"the interpreter running keel_connect_check.py is Python "
                f"{body.get('found')}, below the {body.get('required')} floor: "
                f"{body.get('message')}")

        if outcome in ("runtime_unavailable", "internal_error"):
            h.fail(f"{outcome}: {body.get('message')}")
            raise RuntimeUnavailable(f"{outcome}: {body.get('message')}")

        if outcome == "authorization_pending_timeout":
            h.fail(f"authorization_pending_timeout: {body.get('message')}")
            raise AuthorizationPendingTimeout(body.get("message", "authorization_pending_timeout"))

        # keel-connect-skill spec 005 (upgrade in place): `upgraded` carries the relaunch's own
        # outcome in `then`, and a relaunch that timed out is the same failure a first launch
        # would be; `upgrade_waiting` is a legitimate answer the scenario asserts on.
        if outcome == "upgraded" and body.get("then") == "authorization_pending_timeout":
            h.fail(f"upgraded, then authorization_pending_timeout: {body.get('message')}")
            raise AuthorizationPendingTimeout(body.get("message", "authorization_pending_timeout"))
        if outcome not in ("authorization_started", "connected", "already_connected",
                           "upgraded", "upgrade_waiting"):
            h.fail(f"unrecognized outcome from keel_connect_check.py: {outcome!r}")
            raise RuntimeUnavailable(f"unrecognized outcome from keel_connect_check.py: {outcome!r}")

        return body


def start_runtime_via_skill(config: StackConfig, recorder, *,
                             wait_seconds: float = DEFAULT_WAIT_SECONDS,
                             executor: str = "scripted",
                             env_extra: dict[str, str] | None = None,
                             script_path=None) -> dict:
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
        config, recorder, step_name=f"keel-connect-skill: start the runtime ({executor} executor)",
        wait_seconds=wait_seconds, executor=executor, env_extra=env_extra, script_path=script_path)


def stop_runtime(config: StackConfig, recorder, *, timeout_s: float = 15) -> dict:
    """Spec 006-agent-optional (FR-002, US1 step 1) as amended by spec 012 (FR-003): stops a
    runtime this session started the same way `make down`/`stack/lifecycle.teardown` does -- by
    **asking it to disconnect** and reading the outcome that proves it went.

    `stack.runtime.disconnect` runs keel-connect-skill's own `scripts/keel_disconnect.py` when
    that script exists, and the bundled runtime's `disconnect` command when it does not; either
    way this is the door a founder uses, not a SIGTERM aimed at a pid out of a heartbeat file.
    The proof is in the answer: `stopped`/`disconnected` is emitted only after the pid was
    observed **not alive** (keel-runtime's disconnect contract, guarantee 4), and `not_running` is
    the idempotent second call -- so the "wait for status to catch up" loop this function used to
    need is gone. It is still confirmed against `status` afterwards, because the outcome and the
    heartbeat disagreeing would itself be a finding.

    Returns the disconnect outcome dict (S-008 asserts on it). Raises `RuntimeError` only for
    `did_not_stop`/`timeout` -- the one outcome the contract says a caller must treat as a
    failure -- or for a `status` that still reads running after a stop was claimed.
    """
    with recorder.step("the runtime is asked to disconnect (as `make down` does)",
                        party="stack", kind="protocol") as h:
        before = stack_runtime.status(config)
        outcome = stack_runtime.disconnect(config, timeout=timeout_s + 45)
        after = stack_runtime.status(config)
        h.record_wire({"home": str(home_dir(config))},
                       {"before": before, "disconnect": outcome, "after": after})

        name = outcome.get("outcome")
        if name in stack_runtime.DID_NOT_STOP_OUTCOMES:
            h.fail(f"the runtime did not stop: {outcome}")
            raise RuntimeError(f"the runtime did not stop: {outcome}")
        if name not in stack_runtime.STOPPED_OUTCOMES:
            h.fail(f"unrecognized disconnect outcome: {outcome}")
            raise RuntimeError(f"unrecognized disconnect outcome: {outcome}")
        if after.get("running", False):
            h.fail(f"disconnect answered {name!r} but status still reads running: {after}")
            raise RuntimeError(f"disconnect answered {name!r} but status still reads running: {after}")
        return outcome


def stop_runtime_via_skill(config: StackConfig, recorder, *,
                            timeout_s: float = 60) -> dict:
    """Spec `011-keel-disconnect`: the founder's own way **out**, through the same discipline the
    way in already obeys.

    `harness/connect.py`'s opening rule is that this harness never shells `python3 -m keel_runtime`
    itself, because keel-connect-skill is one of the four applications under referee. The
    disconnect obeys the identical rule and the design says so in as many words (keel-cloud
    `canon/designs/keel-disconnect-design.md` §8.4): *"a new `harness/connect.py::
    stop_runtime_via_skill` shelling `scripts/keel_disconnect.py`, never `python3 -m keel_runtime
    disconnect`."*

    So this is **not** `stop_runtime` with a different name. `stop_runtime` is `make down`'s door:
    it prefers the script, falls through to the bundled runtime's own command when a sibling has
    not landed one yet, and accepts either vocabulary, because a teardown that cannot tear down is
    worse than a teardown that took the lower layer. This one has no fallback: it fails, loudly,
    if keel-connect-skill has no `scripts/keel_disconnect.py`, because the whole point of S-001's
    tail is to referee **that script's** contract -- `disconnected`, in the founder's vocabulary,
    is a word only it says.

    Returns the parsed outcome dict verbatim (the caller asserts on it, as S-001's tail does).
    Raises `RuntimeError` for `did_not_stop`/`timeout` -- the one outcome the contract says a
    caller must treat as a failure -- and `DisconnectScriptMissing` when the script is not there.
    """
    with recorder.step("keel-connect-skill: the founder says \"keel disconnect\"",
                        party="stack", kind="protocol") as h:
        before = stack_runtime.status(config)
        outcome = stack_runtime.disconnect_via_skill_script(config, timeout=timeout_s)
        if outcome is None:
            script = config.disconnect_script_path
            h.record_wire({"script": str(script)}, {"error": "no parseable outcome"})
            h.fail(f"keel-connect-skill's own way out did not answer: {script}")
            raise stack_runtime.DisconnectScriptMissing(
                f"S-001's tail referees keel-connect-skill's `keel_disconnect.py` and that script "
                f"either is not at {script} or did not print one line of JSON carrying an "
                f"`outcome`. This tail deliberately has no fallback to `python3 -m keel_runtime "
                f"disconnect` (design §8.4).")
        after = stack_runtime.status(config)
        h.record_wire({"home": str(home_dir(config)), "via": outcome.get("via")},
                       {"before": before, "disconnect": outcome, "after": after})

        name = outcome.get("outcome")
        if name in stack_runtime.DID_NOT_STOP_OUTCOMES:
            h.fail(f"the runtime did not stop: {outcome}")
            raise RuntimeError(f"the runtime did not stop: {outcome}")
        if after.get("running", False):
            h.fail(f"disconnect answered {name!r} but status still reads running: {after}")
            raise RuntimeError(
                f"disconnect answered {name!r} but status still reads running: {after}")
        return outcome


def reconnect(config: StackConfig, recorder, *,
              wait_seconds: float = DEFAULT_WAIT_SECONDS,
              executor: str = "scripted",
              env_extra: dict[str, str] | None = None) -> dict:
    """Spec 006-agent-optional (FR-002, US1 step 7): reruns keel-connect-skill's own script fresh,
    exactly as the first connect does. Edge cases: "reconnecting mints a new device authorization
    -- the old one is spent" -- the runtime process this session previously started was stopped by
    `stop_runtime` above, and the keel session it was bound to was closed by logging out, so this
    is expected to come back `authorization_started` with a brand-new `verification_uri`/user
    code, not a resume of the old one.
    """
    return _run_connect_check_script(
        config, recorder, step_name=f"keel-connect-skill: reconnect the runtime ({executor} executor)",
        wait_seconds=wait_seconds, executor=executor, env_extra=env_extra)
