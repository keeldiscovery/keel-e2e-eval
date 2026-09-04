"""The runtime home directory keel-connect-skill's script and keel-runtime share (spec 005
FR-003): `runs/.stack/keel-home/`, wiped at `make up` so a credential or heartbeat from a prior
run never makes the landing read "Agent connected" before the smoke itself has connected (spec
005 edge cases). `make up` ends with the runtime **not yet running** -- the smoke starts it,
through the connect skill's script, because starting it is part of the journey (US1).

The runtime is a child the stack owns but never launches directly (edge cases: only
keel-connect-skill's script may start `keel connect`, since the skill is itself one of the four
applications under referee) -- `kill()` reads the heartbeat file's own `pid` (keel-runtime spec
021's `status` contract, read here via `python3 -m keel_runtime status`) so `make down` can reap a
runtime the smoke left running, exactly the way `keel-runtime status` itself would report it.
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
from pathlib import Path

from stack.config import REPO_ROOT, StackConfig


def home_dir(config: StackConfig) -> Path:
    """`runs/.stack/keel-home` for the default (eval) profile, unchanged; `runs/.stack/keel-
    home-<profile>` for any other (split-stacks, relay-design.md §12.5) -- two profiles running
    concurrently (e.g. two referee sessions sharing this checkout, one on each profile) must
    never share a runtime home, or one's `keel connect` heartbeat/credential reads as the
    other's."""
    name = "keel-home" if config.profile == "eval" else f"keel-home-{config.profile}"
    return REPO_ROOT / "runs" / ".stack" / name


def reset(config: StackConfig) -> None:
    """Wiped, then recreated empty, at every `make up` (spec 005 edge case: no credential or
    heartbeat from a prior run survives into a new stack session)."""
    home = home_dir(config)
    if home.exists():
        shutil.rmtree(home)
    home.mkdir(parents=True, exist_ok=True)


def status(config: StackConfig) -> dict:
    """Shells `python3 -m keel_runtime status --home <home>` uninstalled from the keel-runtime
    checkout -- the same invocation shape keel-runtime's own README documents (and the one
    `keel_connect_check.py` uses via `--runtime-path`). Never raises: any subprocess or parse
    failure reads the same as "not running", since a `status` this stack cannot even shell out to
    is definitely not a runtime this stack can call connected.
    """
    try:
        result = subprocess.run(
            ["python3", "-m", "keel_runtime", "status", "--home", str(home_dir(config))],
            cwd=str(config.keel_runtime),
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {"running": False}
    if result.returncode != 0 or not result.stdout.strip():
        return {"running": False}
    try:
        return json.loads(result.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        return {"running": False}


def is_gate_clear(config: StackConfig) -> bool:
    """The `runtime-home` gate itself (US1 independent test / acceptance scenario 1): the
    directory exists and is empty of a heartbeat -- i.e. `status` reads not-running."""
    home = home_dir(config)
    return home.is_dir() and not status(config).get("running", False)


def kill(config: StackConfig) -> None:
    """Idempotent: a no-op if the runtime was never started this session, or has already exited
    on its own. SIGTERM (not killpg) is enough -- `keel connect` is a single Python process with
    no children of its own for the scripted executor, and SIGTERM is exactly the signal
    keel-runtime's own shutdown handler (spec 021 FR-003) is written to expect, so the heartbeat
    file is removed the same clean way Ctrl+C would remove it.
    """
    pid = status(config).get("pid")
    if not pid:
        return
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
