"""The `remote` profile: three URLs that already answer, and the two things a cell does to the
registry in front of them (spec 017; keel-cloud `canon/designs/e2e-matrix-design.md` §5.3, §6.4).

**What this module is not.** It is not a fifth service, not a deploy, and not a second lifecycle.
`stack/cloud.py`, `stack/web.py`, `stack/postgres.py` and `stack/oidc.py` each start a process;
this one starts nothing at all. `make up PROFILE=remote` *asks three questions* and `make down
PROFILE=remote` does nothing, because a referee that could tear down the thing it is refereeing is
a referee with a footgun -- and on staging that thing is a box other cells are mid-run against.

**The invariant this file is written to keep** (§11's "the referee is not modified to accommodate
a deployment"): every line here is reached only when `config.profile == "remote"`. The eval and
playground profiles do not import a different code path, they run the same one, and the same
`stack/auth.py`, `harness/browser.py` and scenario steps serve all three. What differs is a base
URL and, when a gate stands in front of the issuer, a basic-auth pair on exactly two requests.

**The registry half** (§4.3, §6.4). On staging each cell signs in as *its own* founder, registered
just before the run and labelled with the verdict just after, so the founder's morning is a picker
that reads as the log they asked for. `register_cell_identity` is the before and
`label_cell_identity` is the after; `identity_to_sign_in_as` is what a scenario calls to get one
on remote and the built-in *Eval Founder* everywhere else, which is how a scenario stays one
scenario.
"""

from __future__ import annotations

import os
import re
import secrets
import time
from typing import Mapping

import requests

from stack.auth import FOUNDER_ONE, StubFounder
from stack.config import REMOTE_CELL_VAR, StackConfig

#: How long any one of these calls may take. Generous by local standards because the other end is
#: a `t4g.micro` behind Caddy on the public internet, and mean by staging standards because a
#: referee that hangs is worse than one that fails.
TIMEOUT_S = 20


class RemoteNotAnswering(RuntimeError):
    """One of the three URLs the remote profile names did not answer as it must. Raised by
    `make up PROFILE=remote` before any scenario runs, so a cell fails at the gate with the URL
    in the message rather than four screens later with a blank page."""


class RegistryRefused(RuntimeError):
    """The stub's registry refused a registration or a label (409, 403, 404 ...). Carries the
    status and the body, because both are the whole of the diagnosis."""

    def __init__(self, status: int, body: str, what: str):
        super().__init__(f"{what} -- the issuer answered {status}: {body[:300]}")
        self.status = status
        self.body = body


# ------------------------------------------------------------------------------- the three gates

def gate_auth(config: StackConfig) -> tuple[str, str] | None:
    """The basic-auth pair for the **issuer's origin only** (§4.2). keel-cloud's own routes and
    keel-web's pages are not behind the gate -- only `/oidc/authorize` is -- so nothing else in
    this harness ever sends it."""
    return config.gate_credential


def checks(config: StackConfig) -> list[tuple[str, bool, str]]:
    """The three questions `make up PROFILE=remote` asks, as `(what, ok, detail)`:

    1. **keel-web answers 200** at `/` -- the landing page a stranger gets (§9 S6).
    2. **keel-cloud answers 401** at `/v2/me` -- the same readiness gate `stack/cloud.py` uses,
       and the one that proves the JVM is listening, Flyway has run and the security chain is
       wired (google-sign-in-design.md §10.3).
    3. **the issuer's discovery document answers 200** -- and names itself, which is how a
       mis-set `KEEL_REMOTE_OIDC_URL` is caught here instead of at the first sign-in.

    Never a gate credential on any of them: all three are open on staging by design, and asking
    them anonymously is also asking whether a stranger sees what §9 says they see.
    """
    results = []
    for what, url, expected in (
        ("keel-web", f"{config.web_base_url}/", (200,)),
        ("keel-cloud", f"{config.cloud_base_url}/v2/me", (401,)),
        ("issuer", f"{config.oidc_base_url}/.well-known/openid-configuration", (200,)),
    ):
        try:
            response = requests.get(url, timeout=TIMEOUT_S, allow_redirects=False)
        except requests.exceptions.RequestException as exc:
            results.append((what, False, f"{url} -- {type(exc).__name__}: {exc}"))
            continue
        ok = response.status_code in expected
        detail = f"{url} -- {response.status_code}, expected {expected[0]}"
        if ok and what == "issuer":
            try:
                named = response.json().get("issuer")
            except ValueError:
                named = None
            if named != config.oidc_base_url:
                ok = False
                detail = (f"{url} -- 200, but the document calls itself {named!r} and this "
                          f"profile names {config.oidc_base_url!r}")
        results.append((what, ok, detail))
    return results


def is_up(config: StackConfig) -> bool:
    return all(ok for _, ok, _ in checks(config))


def require_answering(config: StackConfig) -> None:
    """What `boot` does for this profile: ask, print, and refuse to go on if any answer is
    wrong."""
    results = checks(config)
    for what, ok, detail in results:
        print(f"[up] (remote) {what}: {'ok' if ok else 'FAILED'} -- {detail}")
    bad = [detail for _, ok, detail in results if not ok]
    if bad:
        raise RemoteNotAnswering(
            "the remote profile names URLs that did not answer as they must:\n  "
            + "\n  ".join(bad))


# ---------------------------------------------------------------------------------- the registry

def cell_name(env: Mapping[str, str] | None = None) -> str:
    """The cell this run is, from `KEEL_REMOTE_CELL` (`ubuntu-copilot-py3.13`), or `local` when
    a founder is running it from their own Mac."""
    env = os.environ if env is None else env
    return (env.get(REMOTE_CELL_VAR) or "local").strip() or "local"


def _slug(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", text).strip("-").lower() or "cell"


def new_identity_id(env: Mapping[str, str] | None = None, *, stamp: str | None = None) -> str:
    """`<cell>-<stamp>-<four random>`. The random tail is not security, it is **re-runs**: two
    runs of the same cell in one minute must be two founders, or the second would inherit the
    first's project and prove nothing (§8: cells never delete)."""
    stamp = stamp or time.strftime("%Y%m%dT%H%M%S", time.gmtime())
    return f"{_slug(cell_name(env))}-{stamp}-{secrets.token_hex(2)}"


def register_cell_identity(config: StackConfig, label: str, *, name: str | None = None,
                           id: str | None = None, email: str | None = None) -> StubFounder:
    """`POST /identities` -- this cell's own founder, before it signs in (§4.3, §5.3 step 4).

    `label` is the long form the picker shows under the button and the verdict is patched into;
    `name` is the short form keel-web greets the founder by and a participant page carries, and it
    defaults to the cell and the day. The `sub` is **derived by the issuer** (`cell-<id>`) and
    never sent: a caller that could choose its own `sub` could choose another cell's, and the
    `sub` is the whole of keel-cloud's identity.

    Returns a `StubFounder`, so the call site reads `sign_in(page, config, register_cell_identity
    (config, label))` and every scenario step after it is the step it already was.
    """
    identity_id = id or new_identity_id()
    name = name or f"Eval {time.strftime('%m%d', time.gmtime())} {cell_name()}"
    email = email or f"{identity_id}@keel-e2e-eval.test"
    response = requests.post(
        f"{config.oidc_base_url}/identities",
        json={"id": identity_id, "name": name, "email": email, "label": label},
        auth=gate_auth(config), timeout=TIMEOUT_S,
    )
    if response.status_code != 201:
        raise RegistryRefused(response.status_code, response.text,
                              f"registering identity {identity_id!r}")
    body = response.json()
    return StubFounder(id=body["id"], sub=body["sub"], email=body["email"], name=body["name"])


def label_cell_identity(config: StackConfig, identity_id: str, label: str) -> dict:
    """`PATCH /identities/<id>` -- the verdict, written beside the founder the cell signed in as
    (§6.4, the second of the three places a verdict is recorded). Label only: a run can never
    rename, re-address or re-`sub` the founder it just was."""
    response = requests.patch(
        f"{config.oidc_base_url}/identities/{identity_id}",
        json={"label": label}, auth=gate_auth(config), timeout=TIMEOUT_S,
    )
    if response.status_code != 200:
        raise RegistryRefused(response.status_code, response.text,
                              f"labelling identity {identity_id!r}")
    return response.json()


def registered_identities(config: StackConfig) -> list[dict]:
    """`GET /identities` -- newest first, what the picker renders. Here for a founder poking at
    staging from a REPL and for the tests; no scenario needs it."""
    response = requests.get(f"{config.oidc_base_url}/identities", auth=gate_auth(config),
                            timeout=TIMEOUT_S)
    if response.status_code != 200:
        raise RegistryRefused(response.status_code, response.text, "reading the registry")
    return response.json().get("identities", [])


def identity_to_sign_in_as(config: StackConfig, label: str,
                           fallback: StubFounder = FOUNDER_ONE, *,
                           name: str | None = None) -> StubFounder:
    """**The one call a scenario makes.** On the remote profile: register this cell's own founder
    and return it. Anywhere else: the built-in *Eval Founder*, with no I/O at all -- so the eval
    and playground profiles behave exactly as they did, which is the invariant this whole spec is
    written around."""
    if not config.is_remote:
        return fallback
    return register_cell_identity(config, label, name=name)
