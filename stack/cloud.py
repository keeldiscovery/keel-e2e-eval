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

from stack import oidc
from stack.config import REPO_ROOT, StackConfig
from stack.processes import is_port_open, require_port_free, spawn, wait_for_http

NAME = "cloud"

# **Why the readiness gate asks `/v2/me` and expects a 401** (google-sign-in-design.md §10.3).
# It used to poll `GET /v2/setup` for a `200`, and keel-cloud spec 032 deletes that route with the
# password. `/v2/me` answering `401` proves the same three things -- the JVM is listening, Flyway
# has run, and the security chain is wired -- and adds no route to the product for the harness's
# benefit. `GET /v2/auth/google/start` would also answer, but it writes a `login_attempt` row on
# every boot poll, which is a silly way to learn a port is open.
READY_PATH = "/v2/me"
READY_STATUS = 401


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
        # **`KEEL_V2_FOUNDER_BASE_URL` is an ORIGIN, and carries no path.** It used to be
        # `.../p`, matching the deleted `keel.v2.founder-base-url` *property* that had a project
        # path baked onto it for `OpenWebUrls`'s screen links. That property is gone (keel-cloud's
        # 030 follow-on) and the env var that outlived it is now the origin three things derive
        # from: `/connect` (the device verification URI), `/v2/auth/google/callback` (the redirect
        # URI) and -- since keel-cloud spec 032 -- **`/login`, where every refused sign-in lands,
        # and the destination a successful one is sent to** (`AuthError.location`,
        # `GoogleCallbackController`, `application.yml`'s own default of `http://localhost:5173`).
        # Left at `.../p` this stack would send a signed-in founder to `/p/` and a refused one to
        # `/p/login?auth_error=...`, both of which keel-web resolves as a project id (its router's
        # `/p/:projectId/*`) rather than as a screen. Found reading spec 032 before `make up`,
        # and asserted in `tests/test_config.py`.
        "KEEL_V2_FOUNDER_BASE_URL": f"http://localhost:{config.web_port}",
        # The participant base URL is *not* an origin: `participant-base-url` is used verbatim to
        # mint invitation links, and keel-web serves the stranger's page at `/i/:token`.
        "KEEL_V2_PARTICIPANT_BASE_URL": f"http://localhost:{config.web_port}/i",
        # KEEL_V2_FOUNDER_DISPLAY_NAME deleted: keel-cloud no longer reads that property -- the
        # participant page and the founder-side read name the founder from the *owning* account's
        # own name (application/FounderNames), which since keel-cloud spec 032 is whichever
        # founder signed in with Google and created the project. Nothing here configures a name.
        # spec 005 FR-002: the URL the runtime's device-authorization response hands back
        # (`verification_uri`) must be a keel-web URL the browser can open -- keel-cloud's own
        # default falls back to KEEL_V2_FOUNDER_BASE_URL + "/connect" already, but this is set
        # explicitly so the gate (US1 acceptance scenario 3) never depends on that fallback.
        "KEEL_V2_CONNECT_VERIFICATION_URI": f"http://localhost:{config.web_port}/connect",
    })
    # Sign in with Google, pointed at this profile's stub issuer (keel-cloud
    # `canon/designs/google-sign-in-design.md` 10.3). Wired now, ahead of keel-cloud spec 032,
    # and **harmless until then**: today's keel-cloud reads none of these four, and an unknown
    # environment variable is not a boot failure. The one thing that differs between production
    # and this harness is `KEEL_OIDC_ISSUER` naming a different URL -- there is no flag, no
    # bypass header and no test-only login anywhere (10.8).
    env.update(oidc.cloud_env(config))
    return env


def is_up(config: StackConfig) -> bool:
    if not is_port_open(config.cloud_port):
        return False
    try:
        response = requests.get(f"http://localhost:{config.cloud_port}{READY_PATH}", timeout=3)
        return response.status_code == READY_STATUS
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
        f"http://localhost:{config.cloud_port}{READY_PATH}",
        config.cloud_boot_timeout,
        ok_statuses={READY_STATUS},
    )
