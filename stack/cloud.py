"""keel-cloud via `./gradlew bootRun` (contracts/stack-contract.md): the load-bearing base-URL and
connect-verification-URI overrides, --no-daemon so the whole JVM lives inside our own recorded
process group (design pass 5 -- a bare gradle daemon would survive `make down`'s killpg untouched).

spec 005 FR-002: the MCP/relay overrides (`SPRING_AI_MCP_SERVER_PROTOCOL`,
`KEEL_V2_RELAY_PRESENCE_THRESHOLD`, `KEEL_V2_RELAY_POLL_WINDOW`) and the `/mcp` reachability gate
are removed with them -- the connect stack talks to keel-cloud over `/v2/*` and keel-runtime's own
long-poll; nothing here speaks MCP or the relay any more (runs/DRIFT.md's 2026-09-03 retirement
note).
"""

from __future__ import annotations

import os

import requests

from stack.config import REPO_ROOT, StackConfig
from stack.processes import is_port_open, require_port_free, spawn, wait_for_http

NAME = "cloud"


def _process_name(config: StackConfig) -> str:
    """Split-stacks (relay-design.md §12.5): profile-suffixed pid/log names so a playground
    boot's own process never shares a pid file with the eval profile's -- see
    stack/processes.py's `teardown_all_processes` docstring for why that matters."""
    return NAME if config.profile == "eval" else f"{NAME}-{config.profile}"


def build_env(config: StackConfig) -> dict[str, str]:
    env = dict(os.environ)
    java_home = env.get("JAVA_HOME") or "/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"
    env.update({
        "JAVA_HOME": java_home,
        "KEEL_DB_URL": f"jdbc:postgresql://localhost:{config.postgres_port}/keel_cloud",
        "KEEL_DB_USERNAME": "keel",
        "KEEL_DB_PASSWORD": "keel",
        "KEEL_SERVER_PORT": str(config.cloud_port),
        # Load-bearing (design §2): the shipped defaults point at localhost:3000/{projects,i},
        # a URL keel-web does not serve -- it serves /p and /i.
        "KEEL_V2_FOUNDER_BASE_URL": f"http://localhost:{config.web_port}/p",
        "KEEL_V2_PARTICIPANT_BASE_URL": f"http://localhost:{config.web_port}/i",
        "KEEL_V2_FOUNDER_DISPLAY_NAME": "Eval Founder",
        # spec 005 FR-002: the URL the runtime's device-authorization response hands back
        # (`verification_uri`) must be a keel-web URL the browser can open -- keel-cloud's own
        # default falls back to KEEL_V2_FOUNDER_BASE_URL + "/connect" already, but this is set
        # explicitly so the gate (US1 acceptance scenario 3) never depends on that fallback.
        "KEEL_V2_CONNECT_VERIFICATION_URI": f"http://localhost:{config.web_port}/connect",
    })
    return env


def is_up(config: StackConfig) -> bool:
    if not is_port_open(config.cloud_port):
        return False
    try:
        response = requests.get(f"http://localhost:{config.cloud_port}/v2/setup", timeout=3)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def up(config: StackConfig) -> None:
    """Idempotent, and safe on a half-up stack (see stack.postgres.up's docstring)."""
    if is_up(config):
        return
    require_port_free(config.cloud_port, "keel-cloud")
    env = build_env(config)
    name = _process_name(config)
    log_path = REPO_ROOT / "runs" / ".stack" / f"{name}.log"
    spawn(
        name,
        ["./gradlew", "bootRun", "--no-daemon", "--console=plain"],
        cwd=config.keel_cloud,
        env=env,
        log_path=log_path,
    )
    wait_for_http(
        f"http://localhost:{config.cloud_port}/v2/setup",
        config.cloud_boot_timeout,
        ok_statuses={200},
    )
