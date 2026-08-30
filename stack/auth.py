"""Founder auth bootstrap (founder-experience round 2): keel-cloud now enforces real auth end to
end -- founder web routes need a session, `/v2/agent/**` and `/mcp` need `X-Keel-Agent-Key` -- so
something has to establish the one founder account before any scenario can drive a discovery.

`ensure_founder_account` is the "recipes/conftest step" the round-2 design asks for: idempotent
against `GET /v2/setup` (an already-set-up instance is left alone), called from
`evals/conftest.py`'s `stack` fixture so it runs once per attach-or-boot, whichever a scenario
session actually does.

**Judgement call -- where credentials live.** `runs/.stack/founder.json`, alongside the pid files
`stack/processes.py` already keeps there: this is stack machinery (how to reach the one account
this harness itself created), not a scored run's evidence, so it does not belong under a run
bundle's own directory. The agent key is mint-once and never retrievable again (keel-cloud's own
design), so it must be captured and stored the moment `POST /v2/setup` succeeds or every later
scenario has no way to authenticate the agent surface at all.

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
(`make down && make up`) when they don't work -- there is no way to recover a lost agent key short
of that, since keel-cloud never stores or re-reveals the raw value.
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
    agent_key: str


def _read_stored() -> FounderCredentials | None:
    if not CREDENTIALS_PATH.exists():
        return None
    try:
        raw = json.loads(CREDENTIALS_PATH.read_text())
        return FounderCredentials(name=raw["name"], email=raw["email"],
                                   password=raw["password"], agent_key=raw["agentKey"])
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def _write_stored(creds: FounderCredentials) -> None:
    CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_PATH.write_text(json.dumps({
        "name": creds.name, "email": creds.email, "password": creds.password,
        "agentKey": creds.agent_key,
    }, indent=2))


def clear_stored() -> None:
    """Called from `stack.lifecycle.teardown()` -- see this module's docstring on why a
    `founder.json` must never outlive the postgres volume it describes."""
    CREDENTIALS_PATH.unlink(missing_ok=True)


def account_exists(config: StackConfig) -> bool:
    """A direct, side-effect-free `GET /v2/setup` read (task item 5's S-008 auth moments):
    `evals/conftest.py`'s `founder_credentials` fixture calls this *before* provisioning, so a
    scenario can observe the genuinely virgin instance (`accountExists: false`) the one time in a
    stack's lifetime it is ever true -- `ensure_founder_account` itself would otherwise consume
    that moment as a side effect of provisioning."""
    base = f"http://localhost:{config.cloud_port}"
    response = requests.get(f"{base}/v2/setup", timeout=10)
    response.raise_for_status()
    return bool(response.json().get("accountExists", False))


def ensure_founder_account(config: StackConfig) -> FounderCredentials:
    """`GET /v2/setup` -> `accountExists`. `False`: `POST /v2/setup` once, store the result (the
    only moment the raw agent key ever exists outside keel-cloud's own response). `True`: reuse
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
        creds = FounderCredentials(name=body["name"], email=body["email"],
                                    password=FOUNDER_PASSWORD, agent_key=body["agentKey"])
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
        "account). There is no way to recover a lost agent key -- run `make down` (drops the "
        "postgres volume) and `make up` again to start from a fresh account."
    )
