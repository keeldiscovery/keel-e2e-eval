"""keel-cloud via `./gradlew bootRun` (contracts/stack-contract.md): the two load-bearing base-URL
overrides, --no-daemon so the whole JVM lives inside our own recorded process group (design pass
5 -- a bare gradle daemon would survive `make down`'s killpg untouched), and the /mcp reachability
check.

keel-cloud's `SecurityConfig` permits `spring.ai.mcp.server.streamable-http.mcp-endpoint`
(default `/mcp`) as the live MCP transport. That was originally false against `spring-ai-bom
2.0.1` (its default is the SSE transport at `/sse`), which this stack gate caught on first boot
(runs/DRIFT.md #3): `/sse` answered 403 while `/mcp` answered a bare 404. keel-cloud now ships
`spring.ai.mcp.server.protocol: STREAMABLE` in its own application.yml (pinned there by
SecurityConfigTest), so this module injects nothing MCP-related and the gate observes the
shipped configuration -- exactly what it exists to test.
"""

from __future__ import annotations

import os

import requests

from stack.config import REPO_ROOT, StackConfig
from stack.processes import is_port_open, require_port_free, spawn, wait_for_http

NAME = "cloud"


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
    })
    return env


def is_up(config: StackConfig) -> bool:
    if not is_port_open(config.cloud_port):
        return False
    try:
        requests.get(f"http://localhost:{config.cloud_port}/", timeout=3)
        return True
    except requests.exceptions.RequestException:
        return False


def up(config: StackConfig) -> None:
    """Idempotent, and safe on a half-up stack (see stack.postgres.up's docstring)."""
    if is_up(config):
        check_mcp_reachable(config)
        return
    require_port_free(config.cloud_port, "keel-cloud")
    env = build_env(config)
    log_path = REPO_ROOT / "runs" / ".stack" / "cloud.log"
    spawn(
        NAME,
        ["./gradlew", "bootRun", "--no-daemon", "--console=plain"],
        cwd=config.keel_cloud,
        env=env,
        log_path=log_path,
    )
    wait_for_http(f"http://localhost:{config.cloud_port}/", config.cloud_boot_timeout)
    check_mcp_reachable(config)


def check_mcp_reachable(config: StackConfig) -> None:
    """One check per stack boot (contracts/stack-contract.md): POST /mcp must not be
    connection-refused or 404, even though the driver itself speaks HTTP, not MCP.

    Founder-experience round 2: /mcp now also sits behind the agent-key gate
    (`AgentKeyAuthorizationManager`), but this check runs from `cloud.up()`, before any founder
    account exists to mint a key from (`evals/conftest.py`'s founder_credentials fixture runs
    later, once the whole stack is up) -- so it stays keyless and unchanged: a 401 here still means
    "mounted, and now also gated", which is exactly as reachable as this check ever promised. The
    scenario-time reachability touches (`harness/driver.py`'s `check_mcp_reachable`,
    `harness/mcp_client.py`'s `McpClient`) run after the founder account exists and do carry the
    key, exercising the gate for real.
    """
    url = f"http://localhost:{config.cloud_port}/mcp"
    try:
        response = requests.post(url, json={}, timeout=5)
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(f"/mcp is not reachable at {url}: {exc}") from exc
    if response.status_code == 404:
        raise RuntimeError(f"/mcp at {url} answered 404 -- the MCP endpoint is not mounted")
