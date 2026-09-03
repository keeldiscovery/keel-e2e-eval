"""Founder auth bootstrap (spec 005 FR-005, keel-cloud spec 023): keel-cloud's founder web routes
need a session; there is no agent key any more (`keel connect`'s device flow replaces it) -- so
something still has to establish the one founder account before the browser can log in and the
smoke can drive a discovery.

`ensure_founder_account` is the "recipes/conftest step" round-2's design asked for and spec 005
keeps: idempotent against `GET /v2/setup` (an already-set-up instance is left alone), called from
`evals/conftest.py`'s `stack` fixture so it runs once per attach-or-boot, whichever a scenario
session actually does.

**Judgement call -- where credentials live.** `runs/.stack/founder.json`, alongside the pid files
`stack/processes.py` already keeps there: this is stack machinery (how to reach the one account
this harness itself created), not a scored run's evidence, so it does not belong under a run
bundle's own directory. Spec 023 FR-005 mints no agent key any more, so there is nothing
mint-once to capture -- only the email/password this harness itself chose, stored so a later
attach (not a fresh boot) can log back in.

**Why `teardown()` must delete this file.** `stack.postgres.down()` is `docker compose down -v` --
every `make down` drops the postgres volume, so the account `founder.json` describes stops
existing the moment teardown runs. A stale file surviving past that point would describe
credentials for an account that is gone; `clear_stored()` (called from `stack.lifecycle.teardown`)
keeps the file's presence in sync with the account's actual lifetime.

**The self-healing case: attaching to a stack this process didn't boot.** `GET /v2/setup` reporting
`accountExists: true` says nothing about *which* password is behind it -- a stored `founder.json`
might describe a different setup entirely (e.g. someone re-ran `docker compose up` by hand outside
this harness's own teardown). `ensure_founder_account` verifies the stored credentials with a real
`POST /v2/login` round-trip rather than trusting the file blind, and raises with a clear remedy
(`make down && make up`) when they don't work.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import requests

from stack.config import REPO_ROOT, StackConfig

CREDENTIALS_PATH = REPO_ROOT / "runs" / ".stack" / "founder.json"

FOUNDER_NAME = "Eval Founder"
FOUNDER_EMAIL = "eval-founder@keel-e2e-eval.test"
FOUNDER_PASSWORD = "eval-founder-password-1"  # noqa: S105 - a fixed, throwaway harness fixture, never a real secret


@dataclass(frozen=True)
class FounderCredentials:
    name: str
    email: str
    password: str


@dataclass(frozen=True)
class KeelSession:
    """The keel session `POST /v2/setup`/`POST /v2/login` opens server-side (keel-cloud spec 023
    FR-002) -- `boundAgentSessionId` is null until a runtime connects through `keel connect`."""

    keel_session_id: str
    bound_agent_session_id: str | None


def _read_stored() -> FounderCredentials | None:
    if not CREDENTIALS_PATH.exists():
        return None
    try:
        raw = json.loads(CREDENTIALS_PATH.read_text())
        return FounderCredentials(name=raw["name"], email=raw["email"], password=raw["password"])
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def _write_stored(creds: FounderCredentials) -> None:
    CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_PATH.write_text(json.dumps({
        "name": creds.name, "email": creds.email, "password": creds.password,
    }, indent=2))


def clear_stored() -> None:
    """Called from `stack.lifecycle.teardown()` -- see this module's docstring on why a
    `founder.json` must never outlive the postgres volume it describes."""
    CREDENTIALS_PATH.unlink(missing_ok=True)


def account_exists(config: StackConfig) -> bool:
    """A direct, side-effect-free `GET /v2/setup` read: `evals/conftest.py`'s
    `founder_credentials` fixture calls this *before* provisioning, so a scenario can observe the
    genuinely virgin instance (`accountExists: false`) the one time in a stack's lifetime it is
    ever true -- `ensure_founder_account` itself would otherwise consume that moment as a side
    effect of provisioning."""
    base = f"http://localhost:{config.cloud_port}"
    response = requests.get(f"{base}/v2/setup", timeout=10)
    response.raise_for_status()
    return bool(response.json().get("accountExists", False))


def ensure_founder_account(config: StackConfig) -> FounderCredentials:
    """`GET /v2/setup` -> `accountExists`. `False`: `POST /v2/setup` once, store nothing but
    email/password (spec 023 FR-005: no agent key is minted or returned any more). `True`: reuse
    `runs/.stack/founder.json`, verified live via `POST /v2/login` rather than trusted blind.
    """
    base = f"http://localhost:{config.cloud_port}"
    status = requests.get(f"{base}/v2/setup", timeout=10)
    status.raise_for_status()
    if not status.json().get("accountExists"):
        response = requests.post(f"{base}/v2/setup", json={
            "name": FOUNDER_NAME, "email": FOUNDER_EMAIL, "password": FOUNDER_PASSWORD,
        }, timeout=10)
        if response.status_code >= 400:
            raise RuntimeError(f"POST /v2/setup failed: {response.status_code} {response.text}")
        body = response.json()
        creds = FounderCredentials(name=body["name"], email=body["email"], password=FOUNDER_PASSWORD)
        _write_stored(creds)
        return creds

    stored = _read_stored()
    if stored is not None:
        login = requests.post(f"{base}/v2/login", json={
            "email": stored.email, "password": stored.password,
        }, timeout=10)
        if login.status_code < 400:
            return stored

    raise RuntimeError(
        "keel-cloud reports a founder account already exists, but this harness has no working "
        f"credentials for it ({CREDENTIALS_PATH} is missing, stale, or describes a different "
        "account). Run `make down` (drops the postgres volume) and `make up` again to start from "
        "a fresh account."
    )


def login_and_keel_session(config: StackConfig, credentials: FounderCredentials) -> tuple[requests.Session, KeelSession]:
    """`POST /v2/login` on a fresh `requests.Session` (spec 005 FR-013's wire-level assertions
    against `GET .../overview` and `GET .../standing` -- these need their own founder-session
    cookie, entirely separate from the browser's own; the project they read belongs to the one
    founder account regardless of which session reads it). Returns the session (its cookie jar
    now carries the founder session) and the keel session login opened, for assertions that want
    `keelSessionId`/`boundAgentSessionId` directly (US2 acceptance scenario 1's "runtime connects
    within 30s" check reads `boundAgentSessionId` becoming non-null, not just the screen).
    """
    base = f"http://localhost:{config.cloud_port}"
    session = requests.Session()
    response = session.post(f"{base}/v2/login", json={
        "email": credentials.email, "password": credentials.password,
    }, timeout=10)
    if response.status_code >= 400:
        raise RuntimeError(f"POST /v2/login failed: {response.status_code} {response.text}")
    body = response.json()
    return session, KeelSession(
        keel_session_id=body["keelSessionId"], bound_agent_session_id=body.get("boundAgentSessionId"),
    )
