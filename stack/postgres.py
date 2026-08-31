"""Postgres via docker compose (contracts/stack-contract.md): fixed port 55432, pg_isready gate.

Split-stacks (relay-design.md §12.5, the account-collision incident): the playground profile runs
under its own Compose *project* (`-p keel-eval-playground`), targeting the `postgres-playground`
service -- a separate container and a real named volume, declared in the same docker-compose.yml
but isolated by project name, which is Compose's own isolation boundary (not the file). The eval
profile's own commands are byte-identical to before (no `-p` flag, service name `postgres`), so an
eval `make down` (always `docker compose down -v` with no `-p`) only ever addresses the default
eval project and can never see, let alone drop, the playground's container or volume.
"""

from __future__ import annotations

import subprocess
import time

from stack.config import REPO_ROOT, StackConfig
from stack.processes import HealthGateTimeout, require_port_free

PLAYGROUND_PROJECT = "keel-eval-playground"


def _service_name(config: StackConfig) -> str:
    return "postgres" if config.profile == "eval" else "postgres-playground"


def _compose_args(config: StackConfig) -> list[str]:
    """The `-p <project>` prefix that puts the playground profile in its own Compose project --
    omitted entirely for the eval profile, so its commands are exactly what they always were."""
    if config.profile == "eval":
        return ["docker", "compose"]
    return ["docker", "compose", "-p", PLAYGROUND_PROJECT]


def up(config: StackConfig) -> None:
    """Idempotent, and safe on a half-up stack: if postgres is already answering on its port
    (e.g. only keel-web died and `boot` is recovering the rest), this is a no-op rather than a
    `require_port_free` failure against our own already-healthy container.
    """
    if is_up(config):
        return
    require_port_free(config.postgres_port, "postgres")
    subprocess.run(
        [*_compose_args(config), "up", "-d", _service_name(config)],
        cwd=str(REPO_ROOT), check=True,
    )
    _wait_ready(config, timeout_s=60)


def _wait_ready(config: StackConfig, timeout_s: float) -> None:
    deadline = time.monotonic() + timeout_s
    last: subprocess.CompletedProcess | None = None
    while time.monotonic() < deadline:
        last = subprocess.run(
            [*_compose_args(config), "exec", "-T", _service_name(config),
             "pg_isready", "-U", "keel", "-d", "keel_cloud"],
            cwd=str(REPO_ROOT), capture_output=True, text=True,
        )
        if last.returncode == 0:
            return
        time.sleep(1)
    detail = last.stdout + last.stderr if last else "docker compose never ran"
    raise HealthGateTimeout(f"postgres never became ready within {timeout_s:.0f}s: {detail}")


def down(config: StackConfig) -> None:
    """Idempotent: safe to call when postgres was never brought up. `-v` here only ever drops
    volumes inside `config`'s own Compose project (the eval profile's default project, or the
    playground profile's own `keel-eval-playground` project) -- never the other one's."""
    subprocess.run(
        [*_compose_args(config), "down", "-v"],
        cwd=str(REPO_ROOT), check=False,
    )


def is_up(config: StackConfig) -> bool:
    result = subprocess.run(
        [*_compose_args(config), "exec", "-T", _service_name(config),
         "pg_isready", "-U", "keel", "-d", "keel_cloud"],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    return result.returncode == 0
