"""keel-web via the eval-owned vite config (contracts/stack-contract.md): `npx vite --config
stack/vite.eval.config.ts` run from the keel-web checkout so vite resolves its own plugins from
keel-web's node_modules.
"""

from __future__ import annotations

import os

import requests

from stack.config import REPO_ROOT, StackConfig
from stack import processes
from stack.processes import is_port_open, is_running, killpg_by_name, require_port_free, spawn

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
    """Idempotent, and safe on a half-up stack (see stack.postgres.up's docstring).

    Spec 140 FR-4: the health gate on keel-web restarts web once before it raises -- on a 500 or a timeout after the
    spawn (`processes.wait_or_restart`), and on a web of this profile's own that is up but no longer answers 200 (the
    cycle-14 Vite that degraded mid-cycle): stopped and spawned again, said in the walk log, then gated."""
    if is_up(config):
        return
    name = _process_name(config)
    if is_port_open(config.web_port) and is_running(name):
        print(f"[up] ({config.profile}) keel-web: up on {config.web_port} but not answering 200 -- restarting it once "
              "(spec 140)", flush=True)
        killpg_by_name(name)
        _spawn(config, name)
        processes.wait_for_http(f"http://localhost:{config.web_port}/", config.web_boot_timeout, ok_statuses={200})
        return
    require_port_free(config.web_port, "keel-web")
    _spawn(config, name)

    def restart() -> None:
        killpg_by_name(name)
        _spawn(config, name)

    processes.wait_or_restart(f"http://localhost:{config.web_port}/", config.web_boot_timeout, restart=restart,
                              say=lambda line: print(f"[up] ({config.profile}) {line}", flush=True),
                              ok_statuses={200}, label="keel-web")


def _spawn(config: StackConfig, name: str) -> None:
    env = dict(os.environ)
    env["EVAL_WEB_PORT"] = str(config.web_port)
    env["EVAL_CLOUD_PORT"] = str(config.cloud_port)
    vite_config = REPO_ROOT / "stack" / "vite.eval.config.ts"
    log_path = REPO_ROOT / "runs" / ".stack" / f"{name}.log"
    spawn(
        name,
        ["npx", "vite", "--config", str(vite_config)],
        cwd=config.keel_web,
        env=env,
        log_path=log_path,
    )
