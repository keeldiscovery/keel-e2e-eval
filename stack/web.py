"""keel-web via the eval-owned vite config (contracts/stack-contract.md): `npx vite --config
stack/vite.eval.config.ts` run from the keel-web checkout so vite resolves its own plugins from
keel-web's node_modules.
"""

from __future__ import annotations

import os

import requests

from stack.config import REPO_ROOT, StackConfig
from stack.processes import is_port_open, require_port_free, spawn, wait_for_http

NAME = "web"


def _process_name(config: StackConfig) -> str:
    """See stack/cloud.py's `_process_name` -- same split-stacks reasoning."""
    return NAME if config.profile == "eval" else f"{NAME}-{config.profile}"


def is_up(config: StackConfig) -> bool:
    if not is_port_open(config.web_port):
        return False
    try:
        return requests.get(f"http://localhost:{config.web_port}/", timeout=3).status_code == 200
    except requests.exceptions.RequestException:
        return False


def up(config: StackConfig) -> None:
    """Idempotent, and safe on a half-up stack (see stack.postgres.up's docstring)."""
    if is_up(config):
        return
    require_port_free(config.web_port, "keel-web")
    env = dict(os.environ)
    env["EVAL_WEB_PORT"] = str(config.web_port)
    env["EVAL_CLOUD_PORT"] = str(config.cloud_port)
    vite_config = REPO_ROOT / "stack" / "vite.eval.config.ts"
    name = _process_name(config)
    log_path = REPO_ROOT / "runs" / ".stack" / f"{name}.log"
    spawn(
        name,
        ["npx", "vite", "--config", str(vite_config)],
        cwd=config.keel_web,
        env=env,
        log_path=log_path,
    )
    wait_for_http(
        f"http://localhost:{config.web_port}/",
        config.web_boot_timeout,
        ok_statuses={200},
    )
