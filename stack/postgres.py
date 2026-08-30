"""Postgres via docker compose (contracts/stack-contract.md): fixed port 55432, pg_isready gate."""

from __future__ import annotations

import subprocess

from stack.config import REPO_ROOT, StackConfig
from stack.processes import HealthGateTimeout, require_port_free
import time


def up(config: StackConfig) -> None:
    """Idempotent, and safe on a half-up stack: if postgres is already answering on its port
    (e.g. only keel-web died and `boot` is recovering the rest), this is a no-op rather than a
    `require_port_free` failure against our own already-healthy container.
    """
    if is_up(config):
        return
    require_port_free(config.postgres_port, "postgres")
    subprocess.run(
        ["docker", "compose", "up", "-d", "postgres"],
        cwd=str(REPO_ROOT), check=True,
    )
    _wait_ready(timeout_s=60)


def _wait_ready(timeout_s: float) -> None:
    deadline = time.monotonic() + timeout_s
    last: subprocess.CompletedProcess | None = None
    while time.monotonic() < deadline:
        last = subprocess.run(
            ["docker", "compose", "exec", "-T", "postgres", "pg_isready", "-U", "keel", "-d", "keel_cloud"],
            cwd=str(REPO_ROOT), capture_output=True, text=True,
        )
        if last.returncode == 0:
            return
        time.sleep(1)
    detail = last.stdout + last.stderr if last else "docker compose never ran"
    raise HealthGateTimeout(f"postgres never became ready within {timeout_s:.0f}s: {detail}")


def down() -> None:
    """Idempotent: safe to call when postgres was never brought up."""
    subprocess.run(
        ["docker", "compose", "down", "-v"],
        cwd=str(REPO_ROOT), check=False,
    )


def is_up(config: StackConfig) -> bool:
    result = subprocess.run(
        ["docker", "compose", "exec", "-T", "postgres", "pg_isready", "-U", "keel", "-d", "keel_cloud"],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    return result.returncode == 0
