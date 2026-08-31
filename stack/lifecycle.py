"""Whole-stack up/down/status, shared by the Makefile's CLI entrypoint and evals/conftest.py's
attach-or-boot fixture (contracts/stack-contract.md).
"""

from __future__ import annotations

import time

from stack import auth, cloud, postgres, web
from stack.config import StackConfig, load_config
from stack.processes import teardown_all_processes


def quick_gates_pass(config: StackConfig) -> bool:
    """A fast, non-blocking check: is the whole stack already up and answering? Used so `make
    eval` against an already-up stack attaches instead of re-booting (design pass 5, edge case).
    `boot` below handles the partial case (e.g. only keel-web died) by checking -- and only
    (re)starting -- each piece independently, rather than requiring all-or-nothing here.
    """
    return postgres.is_up(config) and cloud.is_up(config) and web.is_up(config)


def boot(config: StackConfig) -> None:
    """Brings the whole stack up, printing each gate as it passes (FR-001, SC-001)."""
    print(f"[up] ({config.profile}) postgres: booting on {config.postgres_port} ...")
    postgres.up(config)
    print(f"[up] ({config.profile}) postgres: ready on {config.postgres_port}")

    print(f"[up] ({config.profile}) keel-cloud: booting on {config.cloud_port} "
          f"(budget {config.cloud_boot_timeout}s) ...")
    cloud.up(config)
    print(f"[up] ({config.profile}) keel-cloud: ready on {config.cloud_port}")
    print("[up] keel-cloud: /mcp is reachable")

    print(f"[up] ({config.profile}) keel-web: booting on {config.web_port} "
          f"(budget {config.web_boot_timeout}s) ...")
    web.up(config)
    print(f"[up] ({config.profile}) keel-web: ready on {config.web_port}")

    print("[up] all gates passed")


def teardown(config: StackConfig | None = None) -> None:
    """killpg the recorded process groups, wait, then `docker compose down -v` (contract order).
    Idempotent and safe when only part of the stack came up.

    Split-stacks (relay-design.md §12.5): every step below is scoped to `config.profile` --
    `teardown_all_processes(config.profile)` only ever kills that profile's own pid files, and
    `postgres.down(config)` only ever addresses that profile's own Compose project. The eval
    profile's own founder credentials (`stack/auth.py`) are cleared only when tearing down the
    eval profile itself -- a playground teardown has never touched, and must never touch, the
    eval account's stored credentials.
    """
    config = config or load_config()
    print(f"[down] ({config.profile}) stopping keel-web and keel-cloud ...")
    teardown_all_processes(config.profile)
    time.sleep(0.5)
    print(f"[down] ({config.profile}) stopping postgres ...")
    postgres.down(config)
    if config.profile == "eval":
        # postgres.down() drops the eval project's volume (-v) -- the founder account
        # stack/auth.py stored credentials for no longer exists once this returns
        # (founder-experience round 2).
        auth.clear_stored()
    print(f"[down] ({config.profile}) done")
