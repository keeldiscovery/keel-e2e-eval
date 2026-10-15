"""The contacts marks (spec 043): keel-cloud spec 093's rules, held over one contacts leg's record -- deterministic,
zero spend, the way spec 040 / 042 wrote `spoken_form` and `brief_facts` (one check a rule, all of them owed, nothing
named apart).

They are a **journey** ruler, not the instruction eval's: `instructions/marks.py`'s `MARKS_VERSION` measures
keel-cloud's inference prose, and Contacts has none (no model turn anywhere in spec 093), so these carry their own
version and leave `MARKS_VERSION` at 19 (judgement call 135). The leg (`evals/contacts_leg.py`) builds the record from
what the wire answered, what `credit_ledger` holds and what the stack is made of; `score` reads only the record, so a
unit test can seed a bad one and watch the mark fail (`tests/test_contacts_marks.py`).

A mark whose subject the record does not carry is **unmeasured** -- reported, never passed -- so S-005's B2C record
(the `NOT_B2B` refusal alone) measures one mark and S-006's measures every one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from harness import contacts_fake as fake
from harness import interviewer_fake as fake_interviewer

#: Bumped whenever a mark is born, retired, or reads its record differently.
CONTACTS_MARKS_VERSION = 2
#: v2 (spec 044, contract 16): CM12 reads the AI interviewer's refusal as 409 INTERVIEWER_NOT_READY; CM2 / CM3 hold
#: `price_version` 9.

#: Every key the wire might name a phone by; none may appear anywhere in a contacts response (E6).
PHONE_KEY = re.compile(r"phone|mobile|\btel\b|telephone", re.I)
#: The register's rows carry no email field (people-workflow §5: "No email field anywhere; Keel never sends").
EMAIL_KEY = re.compile(r"email", re.I)
#: A stack variable or a config key that would send mail.
MAIL_KEY = re.compile(r"smtp|(^|[_.\-])mail|sendgrid|postmark|(^|[_.\-])ses([_.\-]|$)", re.I)

CSV_HEADER = "name,email,email_status,link"
STATUS_ORDER = ["FOUND", "LINK_MADE", "OPENED", "ANSWERED"]
NAMES_REMEDY = "A page of 25 names is {required} credits. You have {available}."
EMAILS_REMEDY = "Their verified emails are {required} credits, 12 each. You have {available}."


@dataclass(frozen=True)
class Check:
    mark: str
    rule: str
    measured: bool
    ok: bool
    detail: Any = None


def _instant(text: str | None) -> datetime:
    """An ISO instant as the wire writes it (`...Z`, any number of fraction digits), for ordering."""
    if not text:
        return datetime.min.replace(tzinfo=timezone.utc)
    m = re.match(r"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(?:\.(\d+))?", text)
    if not m:
        return datetime.min.replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(m.group(1)).replace(tzinfo=timezone.utc) + timedelta(
        microseconds=int((m.group(2) or "0").ljust(6, "0")[:6]))


def _keys(value: Any) -> list[str]:
    """Every key anywhere in a JSON value."""
    out: list[str] = []
    if isinstance(value, dict):
        for k, v in value.items():
            out.append(str(k))
            out += _keys(v)
    elif isinstance(value, list):
        for v in value:
            out += _keys(v)
    return out


# ------------------------------------------------------------------------------------------------ the marks

def sizing_is_free_and_the_fakes(r: dict) -> tuple[bool, Any]:
    """CM1: every sizing answers the fake's own count, leaving out everyone fetched, and moves neither the balance nor
    the ledger (E4 / E5)."""
    sizes = r["sizes"]
    bad = [s for s in sizes if s["wire"] != s["fake"] or s["balance_before"] != s["balance_after"]
           or s["ledger_rows_added"] != 0]
    return bool(sizes) and not bad, {"sizes": len(sizes), "bad": bad}


def every_purchase_a_pair(r: dict) -> tuple[bool, Any]:
    """CM2: every page and every reveal that charged credits is one HOLD of -n (price_version 9, no job, this project)
    and its SPEND of 0 carrying the price n and the Starter-rate cost, under one `contacts:<op>:` key; a receipt that
    charged nothing wrote nothing."""
    rows = [x for x in r["ledger"] if x.get("action") in ("CONTACT_PAGE", "CONTACT_EMAIL")]
    ops: dict[str, dict] = {}
    for x in rows:
        key = x.get("idempotency_key") or ""
        m = re.fullmatch(r"contacts:([0-9a-f-]{36}):(hold|spend)", key)
        if not m:
            return False, {"unkeyed": x}
        ops.setdefault(m.group(1), {})[m.group(2)] = x
    pairs = []
    faults = []
    for op, pair in ops.items():
        hold, spend = pair.get("hold"), pair.get("spend")
        if not hold or not spend:
            faults.append({"op": op, "half": pair})
            continue
        n = -int(hold["credits"])
        unit, cost = ((fake.NAME_CREDITS, fake.NAME_COST_MICRO_USD) if hold["action"] == "CONTACT_PAGE"
                      else (fake.EMAIL_CREDITS, fake.EMAIL_COST_MICRO_USD))
        ok = (hold["kind"] == "HOLD" and spend["kind"] == "SPEND" and hold["action"] == spend["action"]
              and n > 0 and n % unit == 0 and hold.get("price_version") == fake.PRICE_VERSION
              and hold.get("inference_job_id") is None and spend.get("inference_job_id") is None
              and hold.get("project_id") == r["project_id"] == spend.get("project_id")
              and int(spend["credits"]) == 0 and spend.get("price_credits") == n
              and spend.get("actual_cost_micro_usd") == (n // unit) * cost
              and spend.get("price_version") is None)
        if not ok:
            faults.append({"op": op, "hold": hold, "spend": spend})
        pairs.append((hold["action"], n))
    charged = sorted((p["action"], p["charged"]) for p in r["purchases"] if p["charged"] > 0)
    return not faults and sorted(pairs) == charged, {"pairs": sorted(pairs), "receipts": charged, "faults": faults}


def every_hold_at_the_charge_version(r: dict) -> tuple[bool, Any]:
    """CM3: every HOLD written on the founder's ledger while the leg ran carries `price_version` 9 (charge v9 since
    keel-cloud 094; 8 at spec 043)."""
    holds = [x for x in r["ledger"] if x.get("kind") == "HOLD"]
    bad = [x for x in holds if x.get("price_version") != fake.PRICE_VERSION]
    return bool(holds) and not bad, {"holds": len(holds), "bad": bad}


def balance_follows_receipts(r: dict) -> tuple[bool, Any]:
    """CM4: each receipt's `creditsAvailable` is the balance before it less what it charged, and `/v2/me` agrees."""
    bad = [p for p in r["purchases"]
           if p["available"] != p["balance_before"] - p["charged"] or p["me_after"] != p["available"]]
    return bool(r["purchases"]) and not bad, {"bad": bad}


def nobody_fetched_twice(r: dict) -> tuple[bool, Any]:
    """CM5: no prospect id is ever on two pages -- by the cursor within a dataset or across datasets -- and each page is
    the fake's own next page (E11)."""
    seen: list[str] = [i for p in r["pages"] for i in p["ids"]]
    off = [p for p in r["pages"] if p["ids"] != p["fake_ids"]]
    return len(seen) == len(set(seen)) and len(r["pages"]) >= 2 and not off, {
        "ids": len(seen), "distinct": len(set(seen)), "off": off}


def excluded_on_sizing(r: dict) -> tuple[bool, Any]:
    """CM6: a second dataset on the same search sizes to the fake's count less every id fetched on the project, and its
    empty page charges nothing."""
    second = r["second_dataset"]
    return (second["size"] == second["fake"] and second["page"] == [] and second["charged"] == 0
            and second["ledger_rows_added"] == 0), second


def emails_only_never_a_phone(r: dict) -> tuple[bool, Any]:
    """CM7: no contacts response names a phone anywhere; a page row has no email; a saved person has the fake's own
    address and status; the .csv is name, email, status, link; each reveal is priced at the email-only rate; and
    keel-cloud's code cannot ask for a phone (the port has no such method, the found contact no such field, and every
    `contact_types` the adapter sends is `["email"]`)."""
    phones = sorted({k for resp in r["responses"] for k in _keys(resp.get("body")) if PHONE_KEY.search(k)})
    page_emails = [row for p in r["pages"] for row in p["rows"] if "email" in row]
    saved_off = [s for s in r["saved"] if s["email"] != s["fake_email"] or s["emailStatus"] != s["fake_status"]
                 or s["verified"] != (s["fake_status"] == "VALID")]
    header = (r["batch"]["csv"] or "").splitlines()[0] if r["batch"].get("csv") else ""
    reveal_costs = [x for x in r["ledger"] if x.get("action") == "CONTACT_EMAIL" and x.get("kind") == "SPEND"
                    and x.get("actual_cost_micro_usd") != (x.get("price_credits") or 0) // fake.EMAIL_CREDITS
                    * fake.EMAIL_COST_MICRO_USD]
    source = r["source"]
    asks = [m for m in source["port_methods"] if PHONE_KEY.search(m)]
    asks += [f for f in source["found_contact_fields"] if PHONE_KEY.search(f)]
    types = source["contact_types"]
    ok = not phones and not page_emails and bool(r["saved"]) and not saved_off and header == CSV_HEADER \
        and not reveal_costs and not asks and bool(types) and all(t == ["email"] for t in types) \
        and "revealEmails" in source["port_methods"]
    return ok, {"phone keys": phones, "page rows with email": len(page_emails), "saved off": saved_off,
                "csv header": header, "reveals off the email rate": reveal_costs, "phone in the code": asks,
                "contact_types": types}


def nothing_emailed(r: dict) -> tuple[bool, Any]:
    """CM8: Keel sends nothing -- the register's rows carry no email field, every link comes back to the founder, and
    the stack has no mail service, no mail variable and no mail configuration."""
    reg = [k for row in r["register"]["invitations"] for k in row if EMAIL_KEY.search(k)]
    stack = r["stack"]
    mail_services = [s for s in stack["services"] if MAIL_KEY.search(s)]
    handed = all((link.get("url") or "").startswith("http") for link in r["batch"]["links"])
    ok = not reg and not mail_services and not stack["mail_env"] and not stack["mail_config"] and handed \
        and bool(r["batch"]["links"])
    return ok, {"register email keys": reg, "services": stack["services"], "mail env": stack["mail_env"],
                "mail config": stack["mail_config"], "links handed back": handed}


def status_follows_the_link(r: dict) -> tuple[bool, Any]:
    """CM9: the answered person's status reads FOUND -> LINK_MADE -> OPENED -> ANSWERED, and the register's row for
    them carries the link's facts (TEXT, DATASET, the dataset's name, when the link was made, who it was made for,
    when they answered), newest link first."""
    seen = r["status_trail"]
    row = r["register_row"]
    times = [_instant(x.get("linkMadeAt")) for x in r["register"]["invitations"]]
    ok = (seen == STATUS_ORDER and row.get("format") == "TEXT" and row.get("source") == "DATASET"
          and row.get("datasetName") == r["dataset_name"] and bool(row.get("linkMadeAt"))
          and row.get("foundPersonId") == r["answered_found_person"] and row.get("status") == "ANSWERED"
          and bool(row.get("answeredAt")) and row.get("respondentType") == "COMMERCIAL_B2B"
          and times == sorted(times, reverse=True))
    return ok, {"trail": seen, "row": row, "newest first": times == sorted(times, reverse=True),
                "rows": len(times)}


def a_new_link_retires_the_old(r: dict) -> tuple[bool, Any]:
    """CM10: Make a new link -- the old link answers 404, the new one opens, the invitation is the same one, the
    register's Link made moves while the found person keeps the first link's time (093 call 16; DRIFT #83 closed by
    keel-cloud-docs a4f2c95); an answered link is refused ALREADY_ANSWERED."""
    x = r["relink"]
    times = ("found_person_linkMadeAt" not in x
             or (x["found_person_linkMadeAt"] == x.get("first_linkMadeAt")
                 and x.get("register_linkMadeAt") == x.get("relinked_at") != x.get("first_linkMadeAt")))
    ok = (times and x["old_status"] == 404 and x["new_status"] == 200 and x["same_invitation"]
          and x["new_url"] != x["old_url"]
          and x["answered_refusal"].get("status") == 422
          and (x["answered_refusal"].get("body") or {}).get("code") == "ALREADY_ANSWERED")
    return ok, x


def refused_without_the_credits(r: dict) -> tuple[bool, Any]:
    """CM11: at a low balance a page and a reveal are refused 422 with `required` / `available` and keel-cloud's own
    remedy, and nothing is fetched, revealed, stored or charged."""
    out = {}
    ok = True
    for name, code, template in (("names", "INSUFFICIENT_CREDITS_FOR_NAMES", NAMES_REMEDY),
                                 ("emails", "INSUFFICIENT_CREDITS_FOR_EMAILS", EMAILS_REMEDY)):
        x = r["credit_refusals"][name]
        body = x.get("body") or {}
        want = template.format(required=x["required"], available=x["available"])
        this = (x["status"] == 422 and body.get("code") == code and body.get("rule") == "credits"
                and body.get("required") == x["required"] and body.get("available") == x["available"]
                and body.get("remedy") == want and x["ledger_rows_added"] == 0
                and x["balance_after"] == x["available"] and x["unchanged"])
        ok = ok and this
        out[name] = {"ok": this, "want remedy": want, **x}
    return ok, out


def format_not_available(r: dict) -> tuple[bool, Any]:
    """CM12: an AI interviewer link on a project with no recording is refused 409 INTERVIEWER_NOT_READY on the batch
    and on the single commercial link, and nothing is made (contract 16: FORMAT_NOT_AVAILABLE is no longer answered;
    until spec 044 it was 422 FORMAT_NOT_AVAILABLE, "not available yet")."""
    x = r["format_refusal"]
    body = x.get("body") or {}
    single = x.get("commercial_link") or {}
    ok = (x["status"] == 409 and body.get("code") == fake_interviewer.NOT_READY
          and x["register_before"] == x["register_after"]
          and single.get("status") == 409 and (single.get("body") or {}).get("code") == fake_interviewer.NOT_READY)
    return ok, x


def own_ai_needs_credits(r: dict) -> tuple[bool, Any]:
    """CM13: an own-AI founder's Contacts are refused 422 CONTACTS_NEED_CREDITS (D9)."""
    x = r["own_ai_refusal"]
    return x["status"] == 422 and (x.get("body") or {}).get("code") == "CONTACTS_NEED_CREDITS", x


def consumers_not_b2b(r: dict) -> tuple[bool, Any]:
    """CM14: a consumer study's Contacts are refused 422 NOT_B2B (D10) -- whichever door the founder is on."""
    x = r["not_b2b"]
    return x["status"] == 422 and (x.get("body") or {}).get("code") == "NOT_B2B", x


#: (mark id, the record key it reads, the rule). Order is the leg's.
MARKS: list[tuple[str, str, Callable[[dict], tuple[bool, Any]]]] = [
    ("CM1", "sizes", sizing_is_free_and_the_fakes),
    ("CM2", "ledger", every_purchase_a_pair),
    ("CM3", "ledger", every_hold_at_the_charge_version),
    ("CM4", "purchases", balance_follows_receipts),
    ("CM5", "pages", nobody_fetched_twice),
    ("CM6", "second_dataset", excluded_on_sizing),
    ("CM7", "saved", emails_only_never_a_phone),
    ("CM8", "stack", nothing_emailed),
    ("CM9", "status_trail", status_follows_the_link),
    ("CM10", "relink", a_new_link_retires_the_old),
    ("CM11", "credit_refusals", refused_without_the_credits),
    ("CM12", "format_refusal", format_not_available),
    ("CM13", "own_ai_refusal", own_ai_needs_credits),
    ("CM14", "not_b2b", consumers_not_b2b),
]


def score(record: dict) -> list[Check]:
    checks = []
    for mark, key, rule in MARKS:
        doc = (rule.__doc__ or "").strip().split("\n")[0]
        if key not in record:
            checks.append(Check(mark, doc, measured=False, ok=False))
            continue
        try:
            ok, detail = rule(record)
        except (KeyError, TypeError, IndexError, ValueError) as broken:
            ok, detail = False, {"record could not be read": repr(broken)}
        checks.append(Check(mark, doc, measured=True, ok=bool(ok), detail=detail))
    return checks


def scorecard(record: dict) -> dict:
    checks = score(record)
    measured = [c for c in checks if c.measured]
    return {"version": CONTACTS_MARKS_VERSION,
            "measured": len(measured), "met": sum(c.ok for c in measured),
            "unmeasured": [c.mark for c in checks if not c.measured],
            "checks": [{"mark": c.mark, "rule": c.rule, "measured": c.measured, "ok": c.ok, "detail": c.detail}
                       for c in checks]}
