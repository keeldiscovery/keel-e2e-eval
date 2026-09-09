"""S-008, the runtime that travelled inside the skill (spec 012-bundled-runtime).

The design of record is keel-cloud `canon/designs/keel-skill-design.md`: the runtime is 2,070
lines of dependency-free Python, so **the skill carries it** (§3.1), resolves it checkout →
bundled → `PATH` (§3.2), and every one of the seven outcomes names *which Keel* it is talking
about (§6.3, §7). Acceptance row **A-7** is this module's whole job: *the runtime that runs is the
one that travelled*.

Nothing here is new product behaviour to look at on a screen. It is the one scenario that proves
the referee is refereeing the thing a founder actually gets — every other scenario in this repo
started `keel connect` with `--runtime-path <checkout>`, which is the one path a founder is never
on. So S-008 walks the founder's own path end to end, and asserts the four things that path
turns on:

1. **The skill resolves the bundled runtime with no `KEEL_RUNTIME_PATH` anywhere** (T-1). Proved
   twice: positively, by connecting; and negatively, by running the same script against a copy of
   the skill tree with its `keel_runtime/` removed and an empty `PATH`, which must answer
   `runtime_unavailable` rather than reach some other runtime.
2. **`status` answers the four keys spec `004-shipped-runtime` added** — `executor`,
   `executor_on_path`, `environment` — with `base_url` now always present.
3. **The device flow is unchanged by any of it**: `authorization_started` with a code and a URL,
   approved in a real browser at keel-web's own `/connect`, `/v2/me` reading the agent connected;
   and a second call answering `already_connected` because `status` is always checked first.
4. **There is a door out.** `disconnect` — through keel-connect-skill's own `keel_disconnect.py`
   when it exists, the bundled runtime's own command when it does not — answers `disconnected`
   with a pid it observed leave, and a second call answers `not_running`.

Journey coverage: §1.0 (arrival — the runtime is connected, and disconnected again). The ledger
in keel-cloud `canon/CANON.md` names S-001 for §1.0 and is not amended by this scenario; S-008
proves *how the runtime got there*, which is a fact about the four applications rather than a
moment in the founder's journey.

**What this scenario cannot prove tonight, and says so instead of skipping quietly** (C-11):

- `python_too_old` needs an interpreter below 3.9 and this machine has none (the oldest is
  Apple's `/usr/bin/python3` 3.9.6 — the floor itself). The floor is asserted instead: the whole
  script runs under it and answers a contract outcome rather than a `SyntaxError`, which is the
  half of the version gate this machine *can* observe. The skip is recorded in the bundle.

**And one thing it could not prove until tonight, and now does** (`runs/DRIFT.md` #47, RESOLVED).
When this scenario was written, the runtime bundled inside the skill was `0.1.0+a05f9bc`, four
commits behind keel-runtime's `master`: `_say_goodbye` was a seam with no call in it, because
`CloudClient` had no `end_agent_session`. `/v2/me` therefore went on naming this run's own agent
session as connected for the whole probe window, and the scenario recorded `"path observed":
"staleness"` rather than adapting around it. keel-connect-skill has since re-run `make runtime`
(`4eb0548`, bundling `0.1.0+638c0dc`), so the goodbye now travels with the skill and the fast path
is what a founder gets. **The probe is an assertion now**: the path must be `goodbye`, inside a
window an eighth of keel-cloud's 90-second `presence-threshold`, and a run that falls back to
staleness is red. The other half is asserted either way — **local truth first** (invariant G3):
`keel status` reads not-running the moment `disconnect` answered, whatever the network did.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from harness.browser import Auth, Connect, Landing
from harness.connect import start_runtime_via_skill, stop_runtime
from harness.evidence import finalize_run
from harness.steps import Recorder
from stack import runtime as stack_runtime

#: Every python3 worth trying as "the oldest interpreter on this machine". The floor is 3.9
#: (design §4.1, because Apple's command-line tools ship 3.9.6), so an entry below it is what
#: would let this scenario observe `python_too_old` for real.
CANDIDATE_INTERPRETERS = (
    "/usr/bin/python3.8", "python3.8", "/usr/bin/python3.7", "python3.7",
    "/usr/bin/python3", "python3.9", "/opt/homebrew/bin/python3.9",
)

def _agent_session_of(me: dict) -> str | None:
    """The agent session `/v2/me` names, from `AgentPresence` (keel-cloud
    `canon/openapi-v2.yaml`): `agentSessionId`, camelCase like the rest of the founder tag — the
    connect tag's own `AgentConnectionResponse` spells the same idea `agent_session_id`, so both
    are read and neither is guessed at."""
    agent = me.get("agent") or {}
    value = agent.get("agentSessionId") or agent.get("agent_session_id")
    return value if agent.get("connected") else None


#: How long the goodbye gets to arrive before this scenario concludes it did not (keel-cloud's
#: own `presence-threshold` is 90 s, so anything inside this window is the goodbye and nothing
#: else). Deliberately short: waiting out staleness would make a scenario nobody runs.
GOODBYE_WINDOW_SECONDS = 12.0


def _interpreter_version(path: str) -> tuple[int, int] | None:
    """`(major, minor)` for an interpreter that exists and answers, else `None`."""
    resolved = path if os.path.isabs(path) else (shutil.which(path) or "")
    if not resolved or not os.path.isfile(resolved):
        return None
    try:
        out = subprocess.run(
            [resolved, "-c", "import sys; print('%d %d' % sys.version_info[:2])"],
            capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    try:
        major, minor = out.stdout.split()
        return int(major), int(minor)
    except ValueError:
        return None


def _oldest_interpreter() -> tuple[str, tuple[int, int]] | None:
    found: list[tuple[tuple[int, int], str]] = []
    for candidate in CANDIDATE_INTERPRETERS:
        resolved = candidate if os.path.isabs(candidate) else shutil.which(candidate)
        if not resolved:
            continue
        version = _interpreter_version(resolved)
        if version:
            found.append((version, resolved))
    if not found:
        return None
    version, path = min(found)
    return path, version


def _skill_tree_without_its_runtime(skill_root: Path, destination: Path) -> Path:
    """A copy of the skill — `SKILL.md` and `scripts/` — with **no `keel_runtime/`**, which is
    what a skill copied wrong looks like (design §3.2: `runtime_unavailable`'s message says the
    directory is incomplete, and names neither an install nor the development override)."""
    tree = destination / "keel-connect"
    (tree / "scripts").mkdir(parents=True, exist_ok=True)
    for script in (skill_root / "scripts").glob("*.py"):
        shutil.copy2(script, tree / "scripts" / script.name)
    for top in ("SKILL.md", "RUNTIME_VERSION"):
        if (skill_root / top).is_file():
            shutil.copy2(skill_root / top, tree / top)
    return tree


def _run_check_script(script: Path, *, interpreter: str, empty_path: Path,
                      extra_args: tuple[str, ...] = ()) -> dict:
    """One line of JSON out of `keel_connect_check.py`, run with **an empty `PATH`** and none of
    the three ambient KEEL variables. With no `keel` reachable and no checkout named, rules 1 and
    3 of the resolution order are both impossible — so whatever answers came from rule 2, the
    runtime bundled inside the skill, or from nowhere at all."""
    env = stack_runtime.scrubbed_env({"PATH": str(empty_path)})
    completed = subprocess.run(
        [interpreter, str(script), *extra_args],
        capture_output=True, text=True, timeout=90, env=env)
    stdout = completed.stdout.strip()
    assert stdout, (
        f"keel_connect_check.py printed nothing on stdout (rc={completed.returncode}, "
        f"stderr={completed.stderr!r})")
    lines = stdout.splitlines()
    assert len(lines) == 1, (
        f"the contract is exactly one line of JSON on stdout, always; got {len(lines)}: {lines!r}")
    body = json.loads(lines[0])
    body["_exit_code"] = completed.returncode
    return body


def test_s008_bundled_runtime(stack, founder_credentials, browser, run_dir):
    recorder = Recorder(run_dir)
    web_base = f"http://localhost:{stack.web_port}"
    cloud_base = f"http://localhost:{stack.cloud_port}"
    expected_environment = f"localhost:{stack.cloud_port}"
    started = time.monotonic()
    passed = False
    context = browser.new_context()
    workspace = Path(tempfile.mkdtemp(prefix="s008-"))

    def _get(path: str) -> dict:
        return context.request.get(f"{cloud_base}{path}", timeout=15_000).json()

    try:
        # -------------------------------------------- 0. the state `make up` leaves behind
        with recorder.step("the runtime home is put back the way `make up` leaves it",
                            party="stack", kind="protocol") as h:
            # This scenario owns the runtime's own lifecycle, so it starts from the lifecycle's
            # own starting point: nothing running, and a home with no credential in it. It is the
            # last scenario in the set (alphabetically, and `make eval-all` runs pytest over
            # `evals/`), so no other scenario is relying on a runtime it stops here -- and a
            # credential left by an earlier scenario would turn this run's `authorization_started`
            # into a `connected`, which is a different journey and a weaker proof.
            before = stack_runtime.status(stack)
            left_over = stack_runtime.disconnect(stack) if before.get("running") else None
            stack_runtime.reset(stack)
            h.record_wire({"home": str(stack_runtime.home_dir(stack))},
                           {"before": before, "disconnected": left_over,
                            "after": stack_runtime.status(stack)})

        # ------------------------------------------------------------------ 1. what is on disk
        with recorder.step("the runtime travelled inside the skill, and no KEEL_RUNTIME_PATH "
                            "reaches it", party="stack", kind="assert") as h:
            bundled = stack_runtime.bundled_runtime_dir(stack)
            present = stack_runtime.bundled_runtime_present(stack)
            child_env = stack_runtime.scrubbed_env()
            h.record_assert(
                {"bundled runtime present": True, "KEEL_RUNTIME_PATH in the child env": False},
                {"bundled runtime present": present,
                 "KEEL_RUNTIME_PATH in the child env": "KEEL_RUNTIME_PATH" in child_env,
                 "path": str(bundled),
                 "RUNTIME_VERSION": stack_runtime.bundled_runtime_version(stack)})
            assert present, (
                f"no bundled runtime at {bundled} -- `make -C {stack.keel_connect_skill} runtime`")
            assert "KEEL_RUNTIME_PATH" not in child_env, (
                "T-1: no KEEL_RUNTIME_PATH may reach the skill's script, or the runtime under "
                "referee is the checkout and not the one a founder gets")

        # ------------------------------------------------- 2. the four keys `status` now carries
        with recorder.step("`keel status` names the executor, the home and which Keel this is",
                            party="stack", kind="assert") as h:
            before = stack_runtime.status(stack)
            h.record_wire({"cmd": "keel status --home <this profile's home>"}, before)
            h.record_assert(
                {"running": False, "environment": expected_environment,
                 "base_url": stack.cloud_base_url, "executor present": True,
                 "executor_on_path present": True},
                {"running": before.get("running"), "environment": before.get("environment"),
                 "base_url": before.get("base_url"), "executor present": "executor" in before,
                 "executor_on_path present": "executor_on_path" in before})
            assert before.get("running") is False, (
                f"`make up` ends with the runtime not yet running; got {before}")
            for key in ("home", "base_url", "environment", "executor", "executor_on_path"):
                assert key in before, (
                    f"keel-runtime spec 004 FR-009 puts {key!r} on both `status` shapes; got "
                    f"{sorted(before)}")
            assert before["environment"] == expected_environment, (
                f"the isolated home must still name its Keel (spec 012 FR-004); got "
                f"{before['environment']!r}")
            assert before["base_url"] == stack.cloud_base_url, before
            assert Path(before["home"]) == stack_runtime.home_dir(stack), before

        # ------------------------------- 3. a stripped skill answers `runtime_unavailable` (A-7)
        with recorder.step("a skill copied without its runtime says so, and reaches no other one",
                            party="stack", kind="assert") as h:
            empty_path = workspace / "empty-path"
            empty_path.mkdir(parents=True, exist_ok=True)
            stripped = _skill_tree_without_its_runtime(stack.keel_connect_skill, workspace)
            body = _run_check_script(stripped / "scripts" / "keel_connect_check.py",
                                     interpreter=sys.executable, empty_path=empty_path)
            h.record_wire({"skill tree": str(stripped), "PATH": str(empty_path)}, body)
            h.record_assert({"outcome": "runtime_unavailable", "environment": None, "exit": 0},
                             {"outcome": body.get("outcome"), "environment": body.get("environment"),
                              "exit": body["_exit_code"]})
            assert body["outcome"] == "runtime_unavailable", (
                f"a skill tree with no keel_runtime/ and an empty PATH must reach no runtime at "
                f"all; got {body}")
            assert body["environment"] is None, (
                "`environment` is null exactly when no runtime answered (contract guarantee 4)")
            assert body["_exit_code"] == 0, "only `internal_error` exits non-zero"
            for forbidden in ("KEEL_RUNTIME_PATH", "--runtime-path", "pip install"):
                assert forbidden not in body["message"], (
                    f"X-4: no founder-facing message names {forbidden!r}; got {body['message']!r}")

        # ---------------------------------------------------- 4. the floor, and the gate above it
        with recorder.step("the whole script runs on the oldest interpreter this machine has",
                            party="stack", kind="assert") as h:
            oldest = _oldest_interpreter()
            assert oldest, "no python3 at all on this machine -- nothing to measure the floor with"
            interpreter, version = oldest
            body = _run_check_script(stripped / "scripts" / "keel_connect_check.py",
                                     interpreter=interpreter, empty_path=empty_path)
            below_floor = version < (3, 9)
            expected = "python_too_old" if below_floor else "runtime_unavailable"
            skipped = None if below_floor else (
                "python_too_old was NOT observed: the oldest interpreter on this machine is "
                f"{version[0]}.{version[1]}, at or above the 3.9 floor. Recorded, never silently "
                "passed (design §10 C-11). What is observed instead is the floor itself: the "
                "whole script parses and answers a contract outcome under it.")
            h.record_wire({"interpreter": interpreter,
                            "version": f"{version[0]}.{version[1]}",
                            "python_too_old skipped because": skipped}, body)
            h.record_assert({"outcome": expected}, {"outcome": body.get("outcome")})
            assert body["outcome"] == expected, (
                f"under {interpreter} ({version[0]}.{version[1]}) the script answered {body}")

        # ------------------------------------------------------------- 5. the founder's own walk
        page = context.new_page()
        Auth(page, recorder, web_base).log_in(email=founder_credentials.email,
                                               password=founder_credentials.password)
        landing = Landing(page, recorder, web_base)
        arrival = landing.visit()
        with recorder.step("§1.0: the founder arrives, and the landing says where the agent is",
                            party="founder", kind="protocol") as h:
            # **Recorded, not asserted.** "The landing reads *No agent connected*" is S-001's
            # assertion and it is only true of a stack nobody has connected to yet: keel-cloud
            # keeps an agent session connected until its 90-second `presence-threshold` expires,
            # so a scenario that ran after another one would fail on the previous run's session
            # rather than on anything of its own. What this scenario proves about connecting is
            # proved by the device flow below, which only a credential-free home can reach.
            h.record_wire(None, {"agent_connected": arrival["agent_connected"]})

        result = start_runtime_via_skill(stack, recorder)
        with recorder.step("§1.0: the bundled runtime asks for this device to be approved",
                            party="stack", kind="assert") as h:
            h.record_assert({"outcome": "authorization_started",
                              "environment": expected_environment},
                             {"outcome": result.get("outcome"),
                              "environment": result.get("environment")})
            assert result["outcome"] == "authorization_started", (
                f"expected a freshly-reset home to need device approval, got {result}")
            assert result["environment"] == expected_environment, (
                f"every shape names which Keel this is; got {result.get('environment')!r}")
            for key in ("user_code", "verification_uri", "pid", "log_file"):
                assert key in result, f"the `authorization_started` shape carries {key!r}: {result}"

        connect = Connect(page, recorder)
        frame = connect.open(result["verification_uri"])
        with recorder.step("§1.0: the verification URI opens the device-decision frame",
                            party="founder", kind="assert") as h:
            h.record_assert("B", frame)
            assert frame == "B", f"expected the device-decision frame B, got {frame!r}"
        connect.approve()
        connect.wait_for_connected(timeout_s=30)

        with recorder.step("the runtime this run started is the one that connected",
                            party="stack", kind="assert") as h:
            # **Local truth first, here too.** The device was approved; the runtime redeems the
            # code on its own poll interval and writes its heartbeat when it has. Waiting on
            # `keel status` -- against a home this scenario wiped at step 0 -- is the only wait
            # that cannot be satisfied by somebody else's runtime.
            deadline = time.monotonic() + 30
            live = stack_runtime.status(stack)
            while not live.get("running", False) and time.monotonic() < deadline:
                page.wait_for_timeout(500)
                live = stack_runtime.status(stack)
            h.record_wire(None, live)
            h.record_assert({"running": True}, {"running": live.get("running")})
            assert live.get("running"), (
                f"the approved runtime never wrote a heartbeat to the home this run owns: {live}")
            session_id = live.get("agent_session_id")
            assert session_id, f"a connected runtime names its agent session: {live}"

        with recorder.step("§1.0 wire: GET /v2/me names *this* agent session as connected",
                            party="stack", kind="assert") as h:
            # `agent.connected` alone is not enough and this scenario found out why: keel-cloud
            # computes it from `last_seen_at` against a 90-second presence threshold, so a session
            # an earlier scenario left behind still reads connected for a minute and a half after
            # its runtime is gone. `agent_session_id` is on the same response and is the answer to
            # *whose* runtime -- so it is what is asserted (`AgentConnectionResponse`).
            deadline = time.monotonic() + 30
            me = _get("/v2/me")
            def _is_ours(body: dict) -> bool:
                return _agent_session_of(body) == session_id
            while not _is_ours(me) and time.monotonic() < deadline:
                page.wait_for_timeout(1_000)
                me = _get("/v2/me")
            h.record_wire(None, me)
            h.record_assert({"connected": True, "agent_session_id": session_id},
                             {"connected": (me.get("agent") or {}).get("connected"),
                              "agent_session_id": _agent_session_of(me)})
            assert _is_ours(me), f"/v2/me never named this run's own agent session: {me}"

        # ------------------------------------------------- 6. saying it twice starts nothing twice
        again = start_runtime_via_skill(stack, recorder)
        with recorder.step("saying it again reads the running runtime instead of starting a "
                            "second one", party="stack", kind="assert") as h:
            h.record_assert({"outcome": "already_connected",
                              "environment": expected_environment, "base_url dropped": True},
                             {"outcome": again.get("outcome"),
                              "environment": again.get("environment"),
                              "base_url dropped": "base_url" not in again})
            assert again["outcome"] == "already_connected", (
                f"`status` is always checked first, so a running runtime is never restarted; got "
                f"{again}")
            assert again["environment"] == expected_environment, again
            for key in ("agent_session_id", "last_heartbeat_at"):
                assert key in again, f"the `already_connected` shape carries {key!r}: {again}"
            assert "base_url" not in again, (
                "this shape lost `base_url` and gained `environment` -- one key for which Keel, "
                f"never two (design §7); got {again}")

        running = stack_runtime.status(stack)
        with recorder.step("`keel status` reads the connected runtime, and still names the Keel",
                            party="stack", kind="assert") as h:
            h.record_wire(None, running)
            h.record_assert({"running": True, "environment": expected_environment},
                             {"running": running.get("running"),
                              "environment": running.get("environment")})
            assert running.get("running") is True, running
            assert running.get("environment") == expected_environment, running
            assert running.get("agent_session_id") == again["agent_session_id"], (
                f"the two contracts must describe one runtime: status {running}, skill {again}")

        # ---------------------------------------------------------------- 7. and the door out
        stopped = stop_runtime(stack, recorder)
        with recorder.step("the runtime is gone, and the outcome is a proof rather than a signal",
                            party="stack", kind="assert") as h:
            h.record_wire(None, stopped)
            h.record_assert({"outcome": "disconnected|stopped", "pid observed gone": True},
                             {"outcome": stopped.get("outcome"),
                              "pid observed gone": "pid" in stopped})
            assert stopped["outcome"] in ("disconnected", "stopped"), (
                f"a running runtime disconnects with a proof it went; got {stopped}")
            assert "pid" in stopped, stopped
            assert stopped.get("environment") == expected_environment, stopped

        stopped_again = stop_runtime(stack, recorder)
        with recorder.step("and asking twice is `not_running`, not an error",
                            party="stack", kind="assert") as h:
            h.record_wire(None, stopped_again)
            h.record_assert({"outcome": "not_running"}, {"outcome": stopped_again.get("outcome")})
            assert stopped_again["outcome"] == "not_running", (
                f"disconnect is idempotent by its own contract; got {stopped_again}")

        # ------------------------------------------- 8. what keel-cloud knows, and how fast
        with recorder.step("keel-cloud is told the agent is going, and does not wait out the "
                            "staleness window", party="stack", kind="assert") as h:
            local = stack_runtime.status(stack)
            deadline = time.monotonic() + GOODBYE_WINDOW_SECONDS

            def _ours_still_connected() -> tuple[dict, bool]:
                body = _get("/v2/me")
                return body, _agent_session_of(body) == session_id

            me, still = _ours_still_connected()
            while still and time.monotonic() < deadline:
                page.wait_for_timeout(1_000)
                me, still = _ours_still_connected()
            path = "goodbye" if not still else "staleness"
            h.record_wire({"window_s": GOODBYE_WINDOW_SECONDS},
                           {"path observed": path, "local status": local, "/v2/me": me,
                            "bundled runtime":
                                stack_runtime.bundled_runtime_version(stack)})
            h.record_assert({"local truth first: keel status not running": True,
                              "path observed": "goodbye"},
                             {"local truth first: keel status not running":
                                  not local.get("running", False),
                              "path observed": path})
            # **Local truth first, always** -- keel-runtime's `_say_goodbye` docstring, invariant
            # G3. Whichever path keel-cloud is on, the founder's own machine already reads
            # not-running, and that is the assertion this scenario is entitled to make today.
            assert not local.get("running", False), (
                f"the heartbeat must be gone the moment disconnect answered; got {local}")
            # And the goodbye itself (spec 011). This was `runs/DRIFT.md` #47 — observed as
            # `staleness` while the bundled copy was `0.1.0+a05f9bc`, recorded rather than
            # adapted around — and it is an assertion now that keel-connect-skill bundles a
            # runtime carrying `CloudClient.end_agent_session`. The window is an eighth of
            # keel-cloud's own presence threshold, so nothing but a goodbye can make it pass.
            assert path == "goodbye", (
                f"this run's own agent session {session_id} is still connected "
                f"{GOODBYE_WINDOW_SECONDS}s after the runtime left, so keel-cloud was never told "
                f"— it is waiting out the 90-second staleness window instead. The bundled runtime "
                f"is {stack_runtime.bundled_runtime_version(stack)!r}: {me}")

        passed = True
    finally:
        context.close()
        shutil.rmtree(workspace, ignore_errors=True)
        duration = time.monotonic() - started
        finalize_run(run_dir, slug="s008-bundled-runtime", facts={}, passed=passed,
                     failed_step=recorder.failed_step, duration_s=duration)
        print(f"\nrun bundle: {run_dir}")
