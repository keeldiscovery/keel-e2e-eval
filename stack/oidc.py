"""The stub OIDC issuer's lifecycle, and the two founders it will sign in as (keel-cloud
`canon/designs/google-sign-in-design.md` §10.1-§10.3).

**Why a fourth service.** keel-cloud is about to stop having a password (that design's §12 step 5;
keel-cloud spec `032-google-sign-in`). What replaces it is Sign in with Google -- Authorization
Code + PKCE, an ID token verified against the issuer's JWKS -- and the referee cannot own a Google
account. §3.6 is the whole test story: **the issuer is configuration**. `KEEL_OIDC_ISSUER` defaults
to `https://accounts.google.com` and production sets nothing; this stack sets it to a local stub
and keel-cloud walks the one login path it has, all of it, with no flag, no bypass header, no
seeded cookie and no password anywhere (§10.8).

**This module lands first, on purpose** (§12 step 4): before keel-cloud's own change, so that
change has something to point at, and provable on its own -- `make up` brings a fourth service up,
its discovery document and JWKS answer, and `/authorize` -> `/token` hands back an ID token that
verifies. Everything downstream of that (the picker in `harness/browser.py`, S-010, S-011,
`stack/auth.py` losing its password) is the **second half** of spec 015 and waits on keel-cloud
032. The four `KEEL_*` variables in `stack/cloud.py:build_env` are wired now and are harmless:
today's keel-cloud reads none of them.

Follows the house shape exactly (`cloud.py`, `web.py`): a `NAME`, a profile-suffixed
`_process_name`, `is_up`, `up` -- `require_port_free` -> `ensure_key` -> `spawn` ->
`wait_for_http`. The stub is stateless, so `stack/processes.py:teardown_all_processes` killing its
process group is nearly the whole teardown; the one thing it leaves on disk is this boot's signing
key, and `clear_key` (called from `stack.lifecycle.teardown`) takes that with it, so nothing of the
stub survives a run.
"""

from __future__ import annotations

import os
import sys

import requests

from stack.config import REPO_ROOT, StackConfig
from stack.processes import is_port_open, require_port_free, spawn, wait_for_http
from stack.stub_oidc import identity
from stack.stub_oidc.identity import Identity  # noqa: F401 - re-exported here
from stack.stub_oidc.keys import generate_pem

NAME = "oidc"
BOOT_TIMEOUT_S = 30

#: The client and the two founders. **The same objects**, re-exported from the stub package's own
#: `identity.py` so `oidc.CLIENT_ID`, `oidc.FOUNDER_A`, `oidc.FOUNDER_B` and
#: `oidc.STUB_IDENTITIES` still name what they always named -- `stack/auth.py` builds
#: `FOUNDER_ONE`/`FOUNDER_TWO` from them and the tests assert against them here.
#:
#: They moved down one level for spec 018 (e2e-matrix-design.md §3): the same server runs as a
#: container on the staging twin, and this module cannot go with it -- it imports `requests`,
#: `stack.config` and `stack.processes`, none of which a stub issuer needs. The data belongs to
#: the package that serves it; this module is the local profiles' lifecycle around it.
CLIENT_ID = identity.CLIENT_ID
CLIENT_SECRET = identity.CLIENT_SECRET
FOUNDER_A = identity.FOUNDER_A
FOUNDER_B = identity.FOUNDER_B
STUB_IDENTITIES = identity.STUB_IDENTITIES


def _process_name(config: StackConfig) -> str:
    """See `stack/cloud.py`'s own -- same split-stacks reasoning: two profiles never share a pid
    file, so an eval `make down` can never kill a playground stub."""
    return NAME if config.profile == "eval" else f"{NAME}-{config.profile}"


def issuer_url(config: StackConfig) -> str:
    """What `KEEL_OIDC_ISSUER` will name, and what the discovery document calls itself.

    Spec 017: on the two local profiles this is `http://localhost:<this profile's oidc port>`,
    unchanged; on the `remote` profile it is `KEEL_REMOTE_OIDC_URL` (default `<web>/oidc`, which
    is where Caddy proxies the stub on the staging twin), because there is no local port to name
    and the issuer is a thing that already exists."""
    return config.oidc_base_url


def discovery_url(config: StackConfig) -> str:
    return f"{issuer_url(config)}/.well-known/openid-configuration"


def jwks_url(config: StackConfig) -> str:
    return f"{issuer_url(config)}/jwks"


def key_path(config: StackConfig):
    """`runs/.stack/oidc-key.pem` (profile-suffixed), beside the pid files -- stack machinery,
    not a run's evidence. It is generated at `make up` and is worth nothing: it signs tokens for
    an issuer that only exists because a local environment variable names it."""
    return REPO_ROOT / "runs" / ".stack" / f"{_process_name(config)}-key.pem"


def ensure_key(config: StackConfig):
    """A **fresh** signing key for this boot. `openssl genrsa` once, at `make up`; the arithmetic
    afterwards is pure Python (`stack/stub_oidc/keys.py` says why).

    Regenerated rather than reused so a key never outlives the run that made it -- the same
    posture `runtime.reset` takes to the runtime home, and the reason it is safe to say this
    harness holds no long-lived secret-shaped file. `clear_key` below is the other half."""
    return generate_pem(key_path(config))


def clear_key(config: StackConfig) -> None:
    """Called from `stack.lifecycle.teardown` (§10.3: the stub is stateless, so nothing of it
    survives a run). Idempotent, and only ever this profile's own key."""
    key_path(config).unlink(missing_ok=True)


def cloud_env(config: StackConfig) -> dict[str, str]:
    """The four variables `stack/cloud.py` passes keel-cloud (§10.3). Both profiles get them and
    only the ports differ, exactly as the two base URLs already do. **No
    `KEEL_GOOGLE_ALLOWED_DOMAIN`**: the open posture is what the scenarios exercise and the closed
    one is a keel-cloud unit test, not a stack variant."""
    return {
        "KEEL_OIDC_ISSUER": issuer_url(config),
        "KEEL_GOOGLE_CLIENT_ID": CLIENT_ID,
        "KEEL_GOOGLE_CLIENT_SECRET": CLIENT_SECRET,
        "KEEL_GOOGLE_REDIRECT_URI":
            f"{config.cloud_base_url}/v2/auth/google/callback",
    }


def is_up(config: StackConfig) -> bool:
    """Answers only for *this* profile's stub: the discovery document has to name this profile's
    own origin, so a playground stub answering on the eval port would read as down, not as up."""
    if not is_port_open(config.oidc_port):
        return False
    try:
        response = requests.get(discovery_url(config), timeout=3)
    except requests.exceptions.RequestException:
        return False
    if response.status_code != 200:
        return False
    try:
        return response.json().get("issuer") == issuer_url(config)
    except ValueError:
        return False


def up(config: StackConfig) -> None:
    """Idempotent, and safe on a half-up stack (see `stack.postgres.up`'s docstring)."""
    if is_up(config):
        return
    require_port_free(config.oidc_port, "stub OIDC issuer")
    ensure_key(config)
    name = _process_name(config)
    log_path = REPO_ROOT / "runs" / ".stack" / f"{name}.log"
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["PYTHONUNBUFFERED"] = "1"
    spawn(
        name,
        [sys.executable, "-m", "stack.stub_oidc",
         "--port", str(config.oidc_port),
         "--key", str(key_path(config)),
         "--issuer", issuer_url(config)],
        cwd=REPO_ROOT,
        env=env,
        log_path=log_path,
    )
    wait_for_http(discovery_url(config), BOOT_TIMEOUT_S, ok_statuses={200})
