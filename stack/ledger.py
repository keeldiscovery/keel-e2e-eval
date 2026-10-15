"""keel-cloud's credit ledger, read off the local stack's Postgres -- and the **three stand-ins** spec 043's contacts leg
writes, each named, each reversed by the leg itself (judgement calls 129-131).

**Why the referee reads the database at all.** keel-cloud spec 093 settles every purchase of names or emails as a
`HOLD` and its `SPEND`, written together with no job, the `HOLD` carrying `price_version` 8 (`CreditLedgerEntry.
passThrough`). No route serves a ledger row: `/v2/me.creditsAvailable` is the sum and nothing more. So the pair, its
keys, its `price_version` and its Starter-rate cost are only observable in `credit_ledger` itself, and reading it is
the only way to hold them. Reads are plain `SELECT`s; nothing here reads a project document.

**Why it writes three rows' worth, and only on the local profiles.** Contacts are refused to an own-AI account
(`CONTACTS_NEED_CREDITS`, D9) and open only on a locked B2B project; on the local stack a Keel's-AI account cannot
walk the corridor to its lock at all, because its jobs run on Keel's own Anthropic account and the stack sets no key
(keel-cloud `application.yml`'s `keels-ai.api-key`: empty means every Keel's-AI job fails and is refunded). The
product has no route from one state to the other either ("There is no route that switches an account",
`MeResponse.aiPath`). So the leg takes the project the scripted runtime just built and stands its founder on Keel's
door with a fresh grant -- `stand_in_keels_door` -- lowers the balance once to see the two refusals --
`stand_in_balance` -- and puts the founder back on their own door with nothing to spend -- `restore_own_door` -- in a
`finally`. Every row written carries `reason` `e2e-eval spec 043: ...` and an `idempotency_key` under `e2e-eval:043:`,
so a reader of the table can tell the referee's rows from the product's. Nothing else in this repository writes to
the database, and the remote profile (the staging twin) refuses all three by name.

Through `docker compose exec` on the profile's own service, exactly as `stack/postgres.py` checks readiness; SQL goes
in on stdin with `psql -v` variables, so no value is ever spliced into a statement.
"""

from __future__ import annotations

import json
import re
import subprocess
import uuid

from stack import postgres
from stack.config import REPO_ROOT, StackConfig

#: What every stand-in row says it is.
REASON = "e2e-eval spec 043: {what} (a stand-in; keel-cloud has no route to this state on a stack with no Keel's-AI key)"
KEY_PREFIX = "e2e-eval:043:"
#: keel-cloud `CreditPolicy.GRANT_CREDITS`: what a Google sign-up is granted (`CreditLedgerEntry.grant`).
GRANT_CREDITS = 1500

_UUID = re.compile(r"^[0-9a-fA-F-]{36}$")


class LedgerUnavailable(RuntimeError):
    """The profile has no database this harness can reach (the remote profile), or `psql` failed."""


def _psql(config: StackConfig, sql: str, **variables: str) -> str:
    if config.is_remote:
        raise LedgerUnavailable("the remote profile's database is the staging twin's; the referee never reaches it")
    args = [*postgres._compose_args(config), "exec", "-T", postgres._service_name(config),
            "psql", "-U", "keel", "-d", "keel_cloud", "-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1"]
    for name, value in variables.items():
        args += ["-v", f"{name}={value}"]
    done = subprocess.run(args, input=sql, cwd=str(REPO_ROOT), capture_output=True, encoding="utf-8",
                          errors="replace")
    if done.returncode != 0:
        raise LedgerUnavailable(f"psql exited {done.returncode}: {(done.stderr or done.stdout).strip()}")
    return done.stdout.strip()


def _json(config: StackConfig, select: str, **variables: str):
    out = _psql(config, f"SELECT COALESCE(json_agg(t), '[]'::json) FROM ({select}) t;\n", **variables)
    return json.loads(out or "[]")


# ---------------------------------------------------------------------------------------------- reads

def founder_account(config: StackConfig, sub: str) -> dict:
    """The founder's account row by the stub identity's `sub` (keel-cloud keys an account on it, §3.4)."""
    rows = _json(config, "SELECT id, email, ai_path, walkthrough_seen_at FROM founder_account "
                         "WHERE google_subject = :'sub'", sub=sub)
    if len(rows) != 1:
        raise LedgerUnavailable(f"expected one founder_account for sub {sub!r}, found {len(rows)}")
    return rows[0]


def rows(config: StackConfig, founder_id: str, *, since: str | None = None) -> list[dict]:
    """The founder's ledger rows, oldest first, optionally only those written at or after `since` (ISO time)."""
    _require_uuid(founder_id)
    return _json(config, "SELECT id, project_id, inference_job_id, kind, credits, price_credits, "
                         "actual_cost_micro_usd, action, price_version, reason, idempotency_key, created_at "
                         "FROM credit_ledger WHERE founder_account_id = :'founder' "
                         "AND created_at >= COALESCE(NULLIF(:'since', '')::timestamptz, '-infinity') "
                         "ORDER BY created_at, idempotency_key",
                 founder=founder_id, since=since or "")


def balance(config: StackConfig, founder_id: str) -> int:
    _require_uuid(founder_id)
    out = _psql(config, "SELECT COALESCE(SUM(credits), 0) FROM credit_ledger WHERE founder_account_id = :'founder';\n",
                founder=founder_id)
    return int(out)


def now(config: StackConfig) -> str:
    """The database's own clock, so `since` is compared on one clock with `created_at`."""
    return _psql(config, "SELECT to_json(now())#>>'{}';\n")


# ------------------------------------------------------------------------------------- the stand-ins

def stand_in_keels_door(config: StackConfig, founder_id: str, run: str) -> int:
    """Stand-in 1 (call 129): the account on Keel's door with a fresh grant of 1,500 -- the two facts a Google sign-up
    writes (`ai_path` KEEL, `CreditLedgerEntry.grant`), the grant topping up whatever balance the account holds to
    exactly 1,500. Returns the credits added."""
    _require_uuid(founder_id)
    added = GRANT_CREDITS - balance(config, founder_id)
    _psql(config, "BEGIN;\n"
                  "UPDATE founder_account SET ai_path = 'KEEL' WHERE id = :'founder';\n"
                  "INSERT INTO credit_ledger (id, founder_account_id, kind, credits, reason, idempotency_key, created_at)"
                  " VALUES (:'row', :'founder', 'GRANT', :'credits', :'reason', :'key', now());\n"
                  "COMMIT;\n",
          founder=founder_id, row=str(uuid.uuid4()), credits=str(added),
          reason=REASON.format(what="the account on Keel's door with a fresh grant of 1,500"),
          key=f"{KEY_PREFIX}{run}:door")
    return added


def stand_in_balance(config: StackConfig, founder_id: str, run: str, *, to: int) -> int:
    """Stand-in 2 (call 130): the balance lowered to `to` with one row, as keel-cloud's own `ContactsJourneyTest.
    balance` does (a `PURCHASE` row of the difference) -- the eval cannot spend the fake's 53 people down past 954
    credits of a 1,500 grant. Returns the row's credits."""
    _require_uuid(founder_id)
    delta = int(to) - balance(config, founder_id)
    _psql(config, "INSERT INTO credit_ledger (id, founder_account_id, kind, credits, reason, idempotency_key, created_at)"
                  " VALUES (:'row', :'founder', 'PURCHASE', :'credits', :'reason', :'key', now());\n",
          founder=founder_id, row=str(uuid.uuid4()), credits=str(delta),
          reason=REASON.format(what=f"the balance lowered to {int(to)} to see the two credit refusals"),
          key=f"{KEY_PREFIX}{run}:low-balance")
    return delta


def restore_own_door(config: StackConfig, founder_id: str, run: str) -> int:
    """Stand-in 3 (call 131): the account back on its own door with a zero balance, so the next journey on the same
    founder (S-007 after S-006, or a second run on an un-dropped database) meets the account it always met: `ai_path`
    OWN and nothing to spend (an OWN account's `creditsAvailable` is null whatever the ledger holds). Returns the
    credits the closing row took."""
    _require_uuid(founder_id)
    delta = -balance(config, founder_id)
    _psql(config, "BEGIN;\n"
                  "INSERT INTO credit_ledger (id, founder_account_id, kind, credits, reason, idempotency_key, created_at)"
                  " VALUES (:'row', :'founder', 'PURCHASE', :'credits', :'reason', :'key', now());\n"
                  "UPDATE founder_account SET ai_path = 'OWN' WHERE id = :'founder';\n"
                  "COMMIT;\n",
          founder=founder_id, row=str(uuid.uuid4()), credits=str(delta),
          reason=REASON.format(what="the account back on its own door with nothing to spend"),
          key=f"{KEY_PREFIX}{run}:restore")
    return delta


def _require_uuid(value: str) -> None:
    if not _UUID.match(str(value or "")):
        raise LedgerUnavailable(f"not an account id: {value!r}")
