"""S-013 -- upgrade in place (keel-connect-skill spec `005-upgrade-in-place`, keel-runtime spec
`007-launcher-version`; design of record keel-cloud `canon/designs/upgrade-in-place-design.md`).

The founder's rule, 2026-09-11: *"whenever a user types keel connect the old runtime should be
killed and the new one should start"* -- with the guard the same hour settled: only when the
bundle is newer and the runtime is idle, never a downgrade, and say so. This scenario proves the
three branches a machine can observe, against the real cloud, the real runtime and the skill's own
script, with no model in the loop (`make eval`, deterministic, free):

1. **An older bundle connects.** A copy of the skill's own tree with `VERSION` rewritten to
   `1.0.0` starts the runtime; the device is approved in a real browser; `keel status` reads
   `launcher_version: "1.0.0"`, which is what keel-runtime 0.2.0 records of whoever launched it.
2. **The newer bundle replaces it.** The checkout's own `keel_connect_check.py` (VERSION 2.0.0 or
   later) answers `upgraded`, `then: connected` -- the older runtime stopped through its own
   `disconnect`, the new one reconnected on the saved credential with no second approval -- and
   `status` now names the checkout's version with a different pid.
3. **Nothing happens twice, and nothing goes backwards.** The newer bundle again: `already_connected`
   with `launcher_version` the checkout's. The older bundle again: `already_connected` too, the pid
   unchanged -- an older project's "keel connect" never downgrades the runtime a newer one started
   (Spec Kit installs the tree per project, which is why this branch exists).

**What this scenario cannot prove, and says so instead of skipping quietly** (C-11): the busy
branch -- `upgrade_waiting` when the older runtime is working on a job. It needs a job in flight at
the moment the check runs, which the scripted executor answers in milliseconds; the branch is held
by keel-connect-skill's own tests against a runtime that reports `busy: true`
(`test_an_older_busy_runtime_is_left_to_finish`). Recorded in the bundle, not silently passed.

Journey coverage: §1.0 (arrival -- the runtime connected, replaced, still connected). The ledger
in keel-cloud `canon/CANON.md` names S-001 for §1.0 and is not amended by this scenario.
"""
from __future__ import annotations

import shutil
import tempfile
import time
from pathlib import Path

from harness.browser import Auth, Connect, Landing
from harness.connect import start_runtime_via_skill, stop_runtime
from harness.evidence import finalize_run
from harness.steps import Recorder
from stack import runtime as stack_runtime

OLDER_VERSION = "1.0.0"


def _older_bundle(skill_root: Path, destination: Path) -> Path:
    """A copy of the skill as an older release would have shipped it -- `SKILL.md`, `scripts/`,
    `keel_runtime/`, `RUNTIME_VERSION` -- with `VERSION` rewritten to `1.0.0`. The same runtime
    bytes as the checkout's: what is being tested is the *skill's* version, which is what ships
    and what updates (design §4, U3), not the runtime's own number."""
    tree = destination / "keel-connect-older"
    tree.mkdir(parents=True)
    for top in ("SKILL.md", "RUNTIME_VERSION"):
        if (skill_root / top).is_file():
            shutil.copy2(skill_root / top, tree / top)
    shutil.copytree(skill_root / "scripts", tree / "scripts",
                    ignore=shutil.ignore_patterns("__pycache__", "*.py[co]"))
    shutil.copytree(skill_root / "keel_runtime", tree / "keel_runtime",
                    ignore=shutil.ignore_patterns("__pycache__", "*.py[co]"))
    (tree / "VERSION").write_text(OLDER_VERSION + "\n", encoding="utf-8")
    return tree


def _checkout_version(skill_root: Path) -> str:
    return (skill_root / "VERSION").read_text(encoding="utf-8").strip()


def test_s013_upgrade_in_place(stack, founder_one, browser, run_dir):
    recorder = Recorder(run_dir)
    web_base = f"http://localhost:{stack.web_port}"
    cloud_base = f"http://localhost:{stack.cloud_port}"
    started = time.monotonic()
    passed = False
    context = browser.new_context()
    workspace = Path(tempfile.mkdtemp(prefix="s013-"))
    newer_version = _checkout_version(stack.keel_connect_skill)

    def _get(path: str) -> dict:
        return context.request.get(f"{cloud_base}{path}", timeout=15_000).json()

    try:
        with recorder.step("the runtime home is put back the way `make up` leaves it",
                            party="stack", kind="protocol") as h:
            before = stack_runtime.status(stack)
            left_over = stack_runtime.disconnect(stack) if before.get("running") else None
            stack_runtime.reset(stack)
            h.record_wire({"home": str(stack_runtime.home_dir(stack))},
                           {"before": before, "disconnected": left_over,
                            "after": stack_runtime.status(stack)})

        with recorder.step(f"an older bundle is made: the checkout's tree at VERSION {OLDER_VERSION}",
                            party="stack", kind="assert") as h:
            older = _older_bundle(stack.keel_connect_skill, workspace)
            h.record_assert({"older": OLDER_VERSION, "checkout": ">= 2.0.0"},
                             {"older": (older / "VERSION").read_text().strip(),
                              "checkout": newer_version})
            assert tuple(int(x) for x in newer_version.split(".")) > (1, 0, 0), (
                f"the checkout's VERSION is {newer_version}; this scenario needs it newer than "
                f"{OLDER_VERSION} (keel-connect-skill spec 005 made it 2.0.0)")

        # ------------------------------------------------------------ 1. the older bundle connects
        page = context.new_page()
        Auth(page, recorder, web_base).sign_in(founder_one)
        Landing(page, recorder, web_base).visit()

        result = start_runtime_via_skill(stack, recorder,
                                         script_path=older / "scripts" / "keel_connect_check.py")
        with recorder.step("§1.0: the older bundle's runtime asks for this device to be approved",
                            party="stack", kind="assert") as h:
            h.record_assert({"outcome": "authorization_started"}, {"outcome": result.get("outcome")})
            assert result["outcome"] == "authorization_started", result
        connect = Connect(page, recorder)
        connect.open(result["verification_uri"])
        connect.approve()
        connect.wait_for_connected(timeout_s=30)

        with recorder.step("`keel status` names the launcher that started it: the older bundle",
                            party="stack", kind="assert") as h:
            status = stack_runtime.status(stack)
            h.record_assert({"running": True, "connected": True,
                             "launcher_version": OLDER_VERSION, "busy": False},
                            {k: status.get(k) for k in ("running", "connected", "launcher_version", "busy")})
            assert status.get("running") and status.get("connected"), status
            assert status.get("launcher_version") == OLDER_VERSION, status
            assert status.get("busy") is False, status
            older_pid = status["pid"]
            older_session = status["agent_session_id"]

        # ------------------------------------------------------- 2. the newer bundle replaces it
        upgraded = start_runtime_via_skill(stack, recorder)
        with recorder.step("§1.0: the newer bundle's \"keel connect\" replaces the older runtime "
                            "and says so", party="stack", kind="assert") as h:
            h.record_assert({"outcome": "upgraded", "then": "connected",
                             "previous_version": OLDER_VERSION, "bundle_version": newer_version},
                            {k: upgraded.get(k) for k in ("outcome", "then", "previous_version", "bundle_version")})
            assert upgraded["outcome"] == "upgraded", upgraded
            assert upgraded["then"] == "connected", (
                "the relaunch must reconnect on the saved credential -- no second approval: "
                f"{upgraded}")
            assert upgraded["previous_version"] == OLDER_VERSION, upgraded
            assert upgraded["bundle_version"] == newer_version, upgraded
            assert upgraded["pid"] != older_pid, "the new runtime must be a new process"

        with recorder.step("`keel status` now names the newer launcher, on a new process, still "
                            "connected", party="stack", kind="assert") as h:
            status = stack_runtime.status(stack)
            h.record_assert({"launcher_version": newer_version, "connected": True,
                             "pid changed": True},
                            {"launcher_version": status.get("launcher_version"),
                             "connected": status.get("connected"),
                             "pid changed": status.get("pid") != older_pid})
            assert status.get("launcher_version") == newer_version, status
            assert status.get("connected") is True, status
            assert status.get("pid") != older_pid, status
            newer_pid = status["pid"]

        with recorder.step("§1.0 wire: the cloud sees a fresh agent session, connected",
                            party="stack", kind="assert") as h:
            deadline = time.monotonic() + 30
            me = _get("/v2/me")
            while time.monotonic() < deadline and not (me.get("agent") or {}).get("connected"):
                time.sleep(1)
                me = _get("/v2/me")
            agent = me.get("agent") or {}
            h.record_wire("GET /v2/me", agent)
            assert agent.get("connected"), f"the cloud does not see the new runtime: {agent}"
            new_session = agent.get("agentSessionId") or agent.get("agent_session_id")
            assert new_session and new_session != older_session, (
                f"the goodbye and the new session are one upgrade: {older_session} -> {new_session}")

        # ---------------------------------------------- 3. nothing twice, nothing backwards
        again = start_runtime_via_skill(stack, recorder)
        with recorder.step("the newer bundle again: already connected, and it says which version",
                            party="stack", kind="assert") as h:
            h.record_assert({"outcome": "already_connected", "launcher_version": newer_version},
                            {k: again.get(k) for k in ("outcome", "launcher_version")})
            assert again["outcome"] == "already_connected", again
            assert again.get("launcher_version") == newer_version, again

        kept = start_runtime_via_skill(stack, recorder,
                                       script_path=older / "scripts" / "keel_connect_check.py")
        with recorder.step("the older bundle again: the newer runtime is kept -- never a downgrade",
                            party="stack", kind="assert") as h:
            status = stack_runtime.status(stack)
            h.record_assert({"outcome": "already_connected", "launcher_version": newer_version,
                             "pid": newer_pid},
                            {"outcome": kept.get("outcome"),
                             "launcher_version": kept.get("launcher_version"),
                             "pid": status.get("pid")})
            assert kept["outcome"] == "already_connected", kept
            assert kept.get("launcher_version") == newer_version, kept
            assert status.get("pid") == newer_pid, "an older bundle must not touch a newer runtime"

        with recorder.step("the busy branch is held by the skill's own tests, not observed here",
                            party="stack", kind="protocol") as h:
            h.record_wire(None, {
                "upgrade_waiting skipped because": (
                    "it needs a job in flight at the moment the check runs, and the scripted "
                    "executor answers in milliseconds; keel-connect-skill's "
                    "test_an_older_busy_runtime_is_left_to_finish holds it against a runtime "
                    "reporting busy: true (design C-11: recorded, never silently passed)")})

        stopped = stop_runtime(stack, recorder)
        with recorder.step("the way out still works after an upgrade", party="stack", kind="assert") as h:
            h.record_assert({"running": False}, {"running": stack_runtime.status(stack).get("running")})
            assert stack_runtime.status(stack).get("running") is False, stopped

        passed = True
    finally:
        context.close()
        shutil.rmtree(workspace, ignore_errors=True)
        duration = time.monotonic() - started
        finalize_run(run_dir, slug="s013-upgrade-in-place", facts={}, passed=passed,
                     failed_step=recorder.failed_step, duration_s=duration)
        print(f"\nrun bundle: {run_dir}")
