"""The contacts leg (spec 043, keel-cloud 093 at contract 15): **on the wire**, after S-006's journey, the founder finds
the decision-makers through Keel's Contacts -- datasets per kind of people, sizing (free), a page of 25 names (150
credits), their verified emails (12 each), links in one batch -- and one found person answers through their link; then
Make a new link, the two credit refusals at a low balance, a second page and a second dataset that leave out everyone
already fetched, the AI interviewer refused, and nothing ever emailed. S-005 holds the B2C half: `NOT_B2B`.

**No page objects yet** (keel-web 068, the Interviews section, is being built in parallel): every step is the founder's
own session on keel-cloud's routes, the stranger's link on the participant routes, and keel-cloud's own fake contact
source (`keel.v2.contacts.source = fake`, the stack's default) restated by `harness/contacts_fake.py`. What waits for
068 is named in `WEB_068_FOLLOW_UP` below and in spec 043's follow-ups.

**The founder's door is a stand-in** (judgement calls 129-131, `stack/ledger.py`): the journey's founder is on their
own AI (the scripted runtime built the project), contacts need credits, and on a stack with no Keel's-AI key nothing
else can build a locked B2B project for a Keel's-AI founder. So the leg asserts the own-AI refusal first, stands the
founder on Keel's door with a fresh grant of 1,500, does the work, lowers the balance once for the two refusals, and
puts the founder back on their own door in a `finally`. On the remote profile (the staging twin, no database) only the
own-AI refusal runs, and the rest is skipped by name.

Every rule is scored by `evals/contacts_marks.py` over the record this leg builds (`contacts.json` and
`contacts-marks.json` in the run bundle); the leg fails when any mark is unmet. No model runs anywhere here.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import requests
import yaml

from evals import contacts_marks as marks
from harness import contacts_fake as fake
from harness import vectors_script as vs
from stack import cloud as stack_cloud
from stack import ledger as stack_ledger
from stack.config import REPO_ROOT

KIND = vs.LINK_B2B
#: The founder's first three picks get their emails and their links; the first answers, the second gets a new link.
PICKS = 3
#: The balance the refusals are seen at (stand-in 2): under a page (150) and under the two names waiting (24).
LOW_BALANCE = 20
DATASET_NAME = "Everyone in the UK"
SECOND_NAME = "Everyone in the UK, again"
ELSEWHERE_NAME = "Practitioners in the US"

#: What waits for keel-web 068's page objects (the Interviews section); see spec 043's follow-ups.
WEB_068_FOLLOW_UP = (
    "keel-web 068 (the Interviews section): page objects for the Contacts tabs (one per kind of people, Keel's base "
    "query's chips and its free size), the dataset page (Show 25 / Find 25 more, the picks, Save and get their emails, "
    "the statuses), the Send more popup (a kind, Text only, AI interviewer and Let them choose shown not available, "
    "the batch's links and .csv) and the Sent register (newest first, format / source / dataset / Link made, Make a "
    "new link) -- each held to the wire this leg already holds.")


def _mail_config(keel_cloud: Path) -> list[str]:
    """Lines of keel-cloud's configuration or build that would send mail (none: Keel never sends)."""
    hits = []
    for rel in ("src/main/resources/application.yml", "build.gradle", "build.gradle.kts"):
        path = Path(keel_cloud) / rel
        if path.is_file():
            hits += [f"{rel}: {line.strip()}" for line in path.read_text(encoding="utf-8").splitlines()
                     if re.search(r"^\s*(mail|smtp)\s*:|spring[.-]mail|smtp|starter-mail|javax\.mail|jakarta\.mail",
                                  line, re.I)]
    return hits


def stack_facts(config) -> dict:
    """What the stack is made of, read for *nothing is emailed*: its Compose services, the environment keel-cloud is
    started with, keel-cloud's own configuration and build."""
    compose = yaml.safe_load((REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")) or {}
    env = stack_cloud.build_env(config)
    ours = {k for k in env if k.startswith(("KEEL_", "SPRING_", "JAVA_"))}
    return {"services": sorted((compose.get("services") or {}).keys()),
            "mail_env": sorted(k for k in ours if marks.MAIL_KEY.search(k)),
            "mail_config": _mail_config(config.keel_cloud)}


#: keel-cloud's contact port, its one vendor adapter and the found contact, read as source (spec 092 FR-B / FR-C).
PORT = "src/main/java/com/keeldiscovery/cloud/application/contacts/ContactSource.java"
ADAPTER = "src/main/java/com/keeldiscovery/cloud/infrastructure/explorium/ExploriumContactSource.java"
FOUND = "src/main/java/com/keeldiscovery/cloud/domain/contacts/FoundContact.java"


def source_facts(keel_cloud: Path) -> dict:
    """What keel-cloud's code can ask a source for (call 137): the port's methods, every `contact_types` the adapter
    sends, and the found contact's fields. The fake's own call counters live in keel-cloud's process and are served
    nowhere, so "no phone was ever requested" is held here, on the ledger's email-only rate and on every wire body."""
    def text(rel: str) -> str:
        path = Path(keel_cloud) / rel
        return path.read_text(encoding="utf-8") if path.is_file() else ""
    port = re.findall(r"^\s+[A-Za-z<>, ]+? ([a-z][A-Za-z]*)\(", text(PORT), re.M)
    adapter = [line.strip() for line in text(ADAPTER).splitlines() if "contact_types" in line and "putArray" in line]
    found = re.search(r"record FoundContact\(([^)]*)\)", text(FOUND), re.S)
    return {"port_methods": port, "contact_types": [re.findall(r'\.add\("([^"]+)"\)', line) for line in adapter],
            "found_contact_fields": [f.split()[-1] for f in (found.group(1) if found else "").split(",") if f.strip()]}


class _Wire:
    """The founder's calls, each kept for the record (CM7 sweeps every body's keys)."""

    def __init__(self, j, record: dict):
        self.j = j
        self.record = record

    def __call__(self, method: str, suffix: str, body: dict | None = None, *, ok=(200, 201, 204)) -> tuple[int, dict]:
        path = suffix if suffix.startswith("/v2/") else self.j.project(suffix)
        status, payload = self.j.call(method, path, body, ok=ok)
        self.record["responses"].append({"method": method, "path": path, "status": status, "body": payload})
        return status, payload if isinstance(payload, dict) else {}

    def me(self) -> dict:
        return self.j.get("/v2/me") or {}

    def credits(self) -> int | None:
        return self.me().get("creditsAvailable")


def _participant(j, method: str, token: str, suffix: str, body: dict | None = None) -> tuple[int, dict]:
    """The stranger's side: no session at all."""
    url = f"{j.cloud_base}/v2/i/{token}{suffix}"
    response = requests.request(method, url, json=body, timeout=20)
    try:
        payload = response.json()
    except ValueError:
        payload = {}
    return response.status_code, payload if isinstance(payload, dict) else {}


def _token(url: str) -> str:
    return url.rstrip("/").rsplit("/", 1)[-1]


def _people_by_id(view: dict) -> dict:
    return {p["foundPersonId"]: p for p in view.get("people") or []}


# ---------------------------------------------------------------------------------------------- B2C

def leg_contacts_not_b2b(j) -> dict:
    """S-005 (01-countly, B2C): Contacts are refused NOT_B2B -- before any other gate, so an own-AI founder meets it
    too (keel-cloud 093 call 8's order: ownership, NOT_B2B, NOT_LOCKED, CONTACTS_NEED_CREDITS)."""
    record: dict = {"entry": j.entry.id, "project_id": j.project_id, "responses": []}
    wire = _Wire(j, record)
    with j.recorder.step("contacts (keel-cloud 093, D10): a consumer study's Contacts are refused NOT_B2B -- the web "
                         "shows *Finding consumers is coming*", party="founder", kind="assert") as h:
        status, body = wire("GET", "/contacts/datasets", ok=(422,))
        created, created_body = wire("POST", "/contacts/datasets", {"respondentType": vs.LINK_PRIMARY}, ok=(422,))
        record["not_b2b"] = {"status": status, "body": body, "create": {"status": created, "body": created_body}}
        h.record_assert({"status": 422, "code": "NOT_B2B"}, record["not_b2b"])
        assert body.get("code") == "NOT_B2B" and created_body.get("code") == "NOT_B2B", record["not_b2b"]
    _score(j, record, require=["CM14"])
    return record


# ---------------------------------------------------------------------------------------------- B2B

def leg_contacts(j) -> dict:
    """S-006 (05-paidly, B2B), after the brief. See the module docstring for the order."""
    record: dict = {"entry": j.entry.id, "project_id": j.project_id, "responses": [], "sizes": [], "pages": [],
                    "purchases": [], "saved": []}
    wire = _Wire(j, record)

    with j.recorder.step("contacts (keel-cloud 093, D9): on their own AI the founder's Contacts are refused "
                         "CONTACTS_NEED_CREDITS -- contacts are bought with credits", party="founder",
                         kind="assert") as h:
        me = wire.me()
        status, body = wire("GET", "/contacts/datasets", ok=(422,))
        record["own_ai_refusal"] = {"status": status, "body": body, "aiPath": me.get("aiPath")}
        h.record_assert({"aiPath": "OWN", "status": 422, "code": "CONTACTS_NEED_CREDITS"}, record["own_ai_refusal"])
        assert me.get("aiPath") == "OWN" and body.get("code") == "CONTACTS_NEED_CREDITS", record["own_ai_refusal"]

    if j.stack is None or j.stack.is_remote:
        with j.recorder.step("contacts: the rest of the leg needs the local stack's database (the stand-in door and "
                             "the ledger) and is skipped on the remote profile", party="stack", kind="note") as h:
            h.record_wire({"profile": getattr(j.stack, "profile", None)}, {"skipped": "Keel's door, the purchases, "
                          "the links, the refusals"})
        _score(j, record, require=["CM13"])
        return record

    everyone = fake.people(j.stack.keel_cloud)
    account = stack_ledger.founder_account(j.stack, j.founder_identity.sub)
    founder_id = account["id"]
    run = f"{j.project_id}:{int(time.time())}"
    record["founder_id"] = founder_id
    since = stack_ledger.now(j.stack)
    try:
        _keels_door(j, wire, record, founder_id, run)
        _the_work(j, wire, record, everyone, founder_id, run)
        record["ledger"] = stack_ledger.rows(j.stack, founder_id, since=since)
        with j.recorder.step("contacts: the ledger since Keel's door -- the stand-in grant, one HOLD / SPEND pair a "
                             "purchase, the stand-in low balance, and no other row", party="stack", kind="assert") as h:
            kinds = [(x["kind"], x.get("action"), x["credits"]) for x in record["ledger"]]
            h.record_assert({"pairs": sorted((p["action"], p["charged"]) for p in record["purchases"]
                                             if p["charged"])}, kinds)
            others = [x for x in record["ledger"] if x.get("action") not in ("CONTACT_PAGE", "CONTACT_EMAIL")
                      and not (x.get("idempotency_key") or "").startswith(stack_ledger.KEY_PREFIX)]
            assert not others, others
        record["stack"] = stack_facts(j.stack)
        record["source"] = source_facts(j.stack.keel_cloud)
    finally:
        _restore(j, wire, founder_id, run)
    _score(j, record, require=[m for m, _, _ in marks.MARKS if m != "CM14"])
    return record


def _keels_door(j, wire: _Wire, record: dict, founder_id: str, run: str) -> None:
    with j.recorder.step("contacts: STAND-IN (call 129) -- the founder on Keel's door with a fresh grant of 1,500; on a "
                         "stack with no Keel's-AI key nothing else can build a locked B2B project for a Keel's-AI "
                         "founder", party="stack", kind="protocol") as h:
        added = stack_ledger.stand_in_keels_door(j.stack, founder_id, run)
        me = wire.me()
        h.record_wire({"stand-in": "ai_path KEEL + GRANT", "credits added": added},
                      {"aiPath": me.get("aiPath"), "creditsAvailable": me.get("creditsAvailable")})
        assert me.get("aiPath") == "KEEL" and me.get("creditsAvailable") == stack_ledger.GRANT_CREDITS, me


def _restore(j, wire: _Wire, founder_id: str, run: str) -> None:
    with j.recorder.step("contacts: STAND-IN reversed (call 131) -- the founder back on their own door with nothing "
                         "to spend, as every later journey on this founder expects", party="stack",
                         kind="protocol") as h:
        taken = stack_ledger.restore_own_door(j.stack, founder_id, run)
        me = wire.me()
        h.record_wire({"closing row": taken}, {"aiPath": me.get("aiPath"),
                                               "creditsAvailable": me.get("creditsAvailable")})
        assert me.get("aiPath") == "OWN" and me.get("creditsAvailable") is None, me


def _size(j, wire: _Wire, record: dict, everyone, dataset_id: str, query: dict, fetched: set, label: str) -> int:
    before = wire.credits()
    rows_before = len(stack_ledger.rows(j.stack, record["founder_id"]))
    _, summary = wire("POST", f"/contacts/datasets/{dataset_id}/size", {})
    after = wire.credits()
    entry = {"dataset": label, "wire": summary.get("sizedWithEmail"), "fake": fake.size(everyone, query, fetched),
             "balance_before": before, "balance_after": after,
             "ledger_rows_added": len(stack_ledger.rows(j.stack, record["founder_id"])) - rows_before}
    record["sizes"].append(entry)
    return entry["wire"]


def _fetch(j, wire: _Wire, record: dict, everyone, dataset_id: str, query: dict, fetched: set,
           after: str | None, label: str) -> dict:
    before = wire.credits()
    _, receipt = wire("POST", f"/contacts/datasets/{dataset_id}/fetch", {})
    rows = receipt.get("page") or []
    ids = [r["sourceId"] for r in rows]
    page = {"dataset": label, "ids": ids, "rows": rows,
            "fake_ids": [p.source_id for p in fake.page(everyone, query, fetched, after=after)]}
    record["pages"].append(page)
    record["purchases"].append({"action": "CONTACT_PAGE", "charged": receipt.get("creditsCharged"),
                                "available": receipt.get("creditsAvailable"), "balance_before": before,
                                "me_after": wire.credits(), "units": len(rows)})
    fetched.update(ids)
    return receipt


def _the_work(j, wire: _Wire, record: dict, everyone, founder_id: str, run: str) -> None:
    fetched: set[str] = set()

    # ---- the tabs and Keel's base query
    with j.recorder.step("contacts (C1): one tab per kind of people -- the translators and the agency project managers "
                         "-- each with Keel's base query, sized free to the fake's own count; the prices from the "
                         "server's table", party="founder", kind="assert") as h:
        _, overview = wire("GET", "/contacts/datasets")
        kinds = {k["respondentType"]: k for k in overview.get("kinds") or []}
        deciders = kinds.get(KIND) or {}
        base = (deciders.get("base") or {}).get("query") or {}
        record["overview"] = {"kinds": list(kinds), "prices": overview.get("prices"), "base": base,
                              "base_sized": (deciders.get("base") or {}).get("sizedWithEmail"),
                              "base_fake": fake.size(everyone, base) if base else None}
        h.record_assert({"kinds": [vs.LINK_PRIMARY, KIND], "prices": {"page": 150, "email": 12, "pageSize": 25},
                         "base sized": record["overview"]["base_fake"]}, record["overview"])
        assert list(kinds) == [vs.LINK_PRIMARY, KIND], list(kinds)
        assert overview.get("prices") == {"page": fake.PAGE_CREDITS, "email": fake.EMAIL_CREDITS,
                                          "pageSize": fake.PAGE_SIZE}, overview.get("prices")
        assert base.get("levels") and set(base["levels"]) == {"MANAGER", "DIRECTOR"}, base
        assert [{k: v for k, v in p.items() if k != "label"} for p in base.get("places") or []] == \
            [{"kind": "COUNTRY", "code": j.entry.market["country"]}], base
        assert record["overview"]["base_sized"] == record["overview"]["base_fake"], record["overview"]

    with j.recorder.step("contacts (C2): a dataset for the decision-makers from Keel's base query -- unsized, nothing "
                         "spent -- and sized free to the fake's count", party="founder", kind="assert") as h:
        _, created = wire("POST", "/contacts/datasets", {"respondentType": KIND, "basedOn": "BASE"})
        dataset = created.get("dataset") or {}
        dataset_id = dataset.get("datasetId")
        sized = _size(j, wire, record, everyone, dataset_id, base, fetched, "base")
        h.record_assert({"basedOn": "BASE", "query": base, "sizedWithEmail": None, "sized": record["sizes"][-1]["fake"]},
                        {"dataset": dataset, "sized": sized})
        assert dataset.get("basedOn") == "BASE" and dataset.get("respondentType") == KIND, dataset
        assert {k: dataset["query"][k] for k in ("titles", "levels", "categories", "companySizes")} == \
            {k: base[k] for k in ("titles", "levels", "categories", "companySizes")}, (dataset["query"], base)
        assert dataset.get("sizedWithEmail") is None, dataset

    with j.recorder.step(f"contacts (C2, call 132): the founder removes every chip but the market -- {DATASET_NAME!r}; "
                         "the fake's payroll people match no Paidly title -- and sizes it: 27 with a work email (30 in "
                         "the UK, 3 with none, never counted)", party="founder", kind="assert") as h:
        query = {"places": [{k: v for k, v in place.items() if k != "label"} for place in base["places"]]}
        _, edited = wire("PATCH", f"/contacts/datasets/{dataset_id}", {"name": DATASET_NAME, "query": query})
        dataset = edited.get("dataset") or {}
        sized = _size(j, wire, record, everyone, dataset_id, query, fetched, DATASET_NAME)
        uk = [p for p in everyone if p.country == "GB"]
        h.record_assert({"name": DATASET_NAME, "sizedWithEmail": 27, "fake": record["sizes"][-1]["fake"],
                         "in the UK": 30, "with no email": 3},
                        {"dataset": dataset, "sized": sized, "uk": len(uk), "no email": sum(1 for p in uk if not p.email)})
        assert dataset.get("name") == DATASET_NAME and dataset.get("sizedWithEmail") is None, dataset
        assert sized == 27 == record["sizes"][-1]["fake"], record["sizes"][-1]
        assert len(uk) == 30 and sum(1 for p in uk if not p.email) == 3, len(uk)
    record["dataset_name"] = DATASET_NAME

    with j.recorder.step("contacts (Show 25): a page of 25 names is 150 credits, the fake's own first 25, no email on "
                         "any row; the balance and /v2/me drop by 150", party="founder", kind="assert") as h:
        receipt = _fetch(j, wire, record, everyone, dataset_id, query, fetched, None, DATASET_NAME)
        first = record["pages"][-1]
        h.record_assert({"rows": 25, "charged": 150, "available": 1350, "ids": first["fake_ids"]},
                        {"rows": len(first["ids"]), "charged": receipt.get("creditsCharged"),
                         "available": receipt.get("creditsAvailable"), "ids": first["ids"],
                         "moreToFetch": (receipt.get("dataset") or {}).get("moreToFetch")})
        assert len(first["ids"]) == 25 and receipt.get("creditsCharged") == 150, receipt
        assert receipt.get("creditsAvailable") == 1350 == wire.credits(), receipt
        assert (receipt.get("dataset") or {}).get("moreToFetch") is True, receipt.get("dataset")
        resized = _size(j, wire, record, everyone, dataset_id, query, fetched, f"{DATASET_NAME} after a page")
        assert resized == 2, resized

    with j.recorder.step(f"contacts (Save): the founder saves {PICKS} picks and gets their verified emails at 12 each "
                         "-- the fake's own addresses, email only; each FOUND", party="founder", kind="assert") as h:
        picks = first["ids"][:PICKS]
        before = wire.credits()
        _, saved = wire("POST", f"/contacts/datasets/{dataset_id}/save", {"sourceIds": picks})
        record["purchases"].append({"action": "CONTACT_EMAIL", "charged": saved.get("creditsCharged"),
                                    "available": saved.get("creditsAvailable"), "balance_before": before,
                                    "me_after": wire.credits(), "units": saved.get("savedCount")})
        people = (saved.get("dataset") or {}).get("people") or []
        by_source = fake.by_id(everyone)
        names = {p.full_name: p for p in (by_source[i] for i in picks)}
        for person in people:
            truth = names.get(person["fullName"])
            record["saved"].append({**{k: person.get(k) for k in ("foundPersonId", "fullName", "email", "emailStatus",
                                                                 "verified", "status")},
                                    "fake_email": truth.email if truth else None,
                                    "fake_status": truth.email_status if truth else None})
        h.record_assert({"savedCount": PICKS, "charged": PICKS * 12, "status": "FOUND"},
                        {"saved": record["saved"], "charged": saved.get("creditsCharged")})
        assert saved.get("savedCount") == PICKS and saved.get("creditsCharged") == PICKS * fake.EMAIL_CREDITS, saved
        assert len(record["saved"]) == PICKS and {s["status"] for s in record["saved"]} == {"FOUND"}, record["saved"]
        found = [s["foundPersonId"] for s in record["saved"]]

    # ---- links
    with j.recorder.step("contacts (S3, call 134): the AI interviewer is refused FORMAT_NOT_AVAILABLE -- *not "
                         "available yet* -- on the batch and on the single commercial link, and nothing is made",
                         party="founder", kind="assert") as h:
        before = len((wire("GET", "/invitations")[1]).get("invitations") or [])
        status, body = wire("POST", "/invitations/batch", {"expectedRevision": j.revision(), "respondentType": KIND,
                                                           "format": "AI_INTERVIEWER",
                                                           "people": [{"foundPersonId": found[0]}]}, ok=(422,))
        single, single_body = wire("POST", "/commercial-link", {"expectedRevision": j.revision(),
                                                                "personName": "Someone the founder knows",
                                                                "format": "AI_INTERVIEWER"}, ok=(422,))
        after = len((wire("GET", "/invitations")[1]).get("invitations") or [])
        record["format_refusal"] = {"status": status, "body": body, "register_before": before,
                                    "register_after": after,
                                    "commercial_link": {"status": single, "body": single_body}}
        h.record_assert({"status": 422, "code": "FORMAT_NOT_AVAILABLE", "commercial-link": "FORMAT_NOT_AVAILABLE"},
                        record["format_refusal"])
        assert body.get("code") == "FORMAT_NOT_AVAILABLE" == single_body.get("code") and before == after, \
            record["format_refusal"]

    with j.recorder.step(f"contacts (S3a): links for the {PICKS} found people in one batch, as Text -- each handed "
                         "back once with their saved email, and a .csv; Keel sends nothing; each LINK_MADE",
                         party="founder", kind="assert") as h:
        _, batch = wire("POST", "/invitations/batch", {"expectedRevision": j.revision(), "respondentType": KIND,
                                                       "format": "TEXT",
                                                       "people": [{"foundPersonId": f} for f in found]})
        links = batch.get("links") or []
        record["batch"] = {"format": batch.get("format"), "links": links, "csv": batch.get("csv")}
        _, view = wire("GET", f"/contacts/datasets/{dataset_id}")
        statuses = {fp: p.get("status") for fp, p in _people_by_id(view).items() if fp in found}
        h.record_assert({"links": PICKS, "format": "TEXT", "statuses": "LINK_MADE", "csv lines": PICKS + 1},
                        {"batch": record["batch"], "statuses": statuses})
        assert batch.get("format") == "TEXT" and len(links) == PICKS, batch
        assert [link.get("foundPersonId") for link in links] == found, links
        assert [link.get("email") for link in links] == [s["email"] for s in record["saved"]], links
        assert len((batch.get("csv") or "").splitlines()) == PICKS + 1, batch.get("csv")
        assert set(statuses.values()) == {"LINK_MADE"}, statuses

    # ---- one found person answers
    answered, relinked_person = found[0], found[1]
    answered_link, other_link = links[0], links[1]
    token = _token(answered_link["url"])
    decider = next(p for p in j.people if p.link == KIND)
    trail = [record["saved"][0]["status"]]

    def status_of(fp: str) -> str | None:
        return _people_by_id(wire("GET", f"/contacts/datasets/{dataset_id}")[1]).get(fp, {}).get("status")

    trail.append(status_of(answered))
    with j.recorder.step(f"contacts: {answered_link['personName']} opens their link -- a decision-maker's interview, "
                         "part 3 alone -- and reads OPENED", party="participant", kind="assert") as h:
        got, interview = _participant(j, "GET", token, "/interview")
        opened, _ = _participant(j, "POST", token, "/opened")
        trail.append(status_of(answered))
        h.record_assert({"interview": 200, "kind": "COMMERCIAL_LINK", "opened": 204, "status": "OPENED"},
                        {"interview": got, "kind": interview.get("kind"), "opened": opened, "status": trail[-1]})
        assert got == 200 and interview.get("kind") == "COMMERCIAL_LINK" and opened == 204, (got, opened)

    with j.recorder.step(f"contacts: {answered_link['personName']} answers through the link (the corpus "
                         f"decision-maker {decider.person}'s picks, call 133) and reads ANSWERED", party="participant",
                         kind="assert") as h:
        items = {i.get("dimension"): i for part in interview.get("parts") or [] for i in part.get("items") or []}
        recall = ((items.get("commercial.existing_sacrifice") or {}).get("costTotal") or {}).get("recallPeriod")
        sent, reply = _participant(j, "POST", token, "/interview/response", decider.response(token, recall))
        trail.append(status_of(answered))
        record["status_trail"] = trail
        h.record_assert({"response": [200, 201, 204], "trail": marks.STATUS_ORDER}, {"response": sent, "trail": trail,
                                                                                    "reply": reply})
        assert sent in (200, 201, 204), (sent, reply)

    with j.recorder.step("contacts (T1): the Sent register -- newest link first; the answered person's row reads Text, "
                         f"from {DATASET_NAME!r}, when the link was made and when they answered; no email field on any "
                         "row; the decision-makers' kind row counts them", party="founder", kind="assert") as h:
        _, register = wire("GET", "/invitations")
        rows = register.get("invitations") or []
        row = next((r for r in rows if r.get("invitationId") == answered_link["invitationId"]), {})
        kind_row = next((k for k in register.get("kinds") or [] if k.get("respondentType") == KIND), {})
        record["register"] = {"invitations": rows, "kinds": register.get("kinds")}
        record["register_row"] = row
        record["answered_found_person"] = answered
        corpus_deciders = sum(1 for p in j.people if p.link == KIND)
        h.record_assert({"top": [link["invitationId"] for link in links][::-1], "row": "TEXT · DATASET",
                         "kind": {"linksMade": corpus_deciders + PICKS, "answered": corpus_deciders + 1}},
                        {"top": [r.get("invitationId") for r in rows[:PICKS]], "row": row, "kind": kind_row})
        assert {r.get("invitationId") for r in rows[:PICKS]} == {link["invitationId"] for link in links}, rows[:PICKS]
        assert kind_row.get("linksMade") == corpus_deciders + PICKS, kind_row
        assert kind_row.get("answered") == corpus_deciders + 1, kind_row

    with j.recorder.step(f"contacts (D7): Make a new link for {other_link['personName']} -- the old link answers 404, "
                         "the new one opens, the same invitation; an answered link is refused ALREADY_ANSWERED",
                         party="founder", kind="assert") as h:
        old = _token(other_link["url"])
        first_made = next((r.get("linkMadeAt") for r in record["register"]["invitations"]
                           if r.get("invitationId") == other_link["invitationId"]), None)
        _, relinked = wire("POST", f"/invitations/{other_link['invitationId']}/relink",
                           {"expectedRevision": j.revision()})
        new = _token(relinked.get("url") or "")
        old_status, _ = _participant(j, "GET", old, "/interview")
        new_status, _ = _participant(j, "GET", new, "/interview")
        refused, refusal = wire("POST", f"/invitations/{answered_link['invitationId']}/relink",
                                {"expectedRevision": j.revision()}, ok=(422,))
        _, register = wire("GET", "/invitations")
        moved = next((r for r in register.get("invitations") or []
                      if r.get("invitationId") == other_link["invitationId"]), {})
        person = _people_by_id(wire("GET", f"/contacts/datasets/{dataset_id}")[1]).get(relinked_person, {})
        record["relink"] = {"old_url": other_link["url"], "new_url": relinked.get("url"), "old_status": old_status,
                            "new_status": new_status,
                            "same_invitation": relinked.get("invitationId") == other_link["invitationId"],
                            "first_linkMadeAt": first_made, "register_linkMadeAt": moved.get("linkMadeAt"),
                            "relinked_at": relinked.get("linkMadeAt"),
                            "found_person_linkMadeAt": person.get("linkMadeAt"),
                            "answered_refusal": {"status": refused, "body": refusal}}
        h.record_assert({"old": 404, "new": 200, "answered": "ALREADY_ANSWERED"}, record["relink"])
        assert old_status == 404 and new_status == 200, record["relink"]
        assert moved.get("linkMadeAt") == relinked.get("linkMadeAt") != first_made, record["relink"]
    _drift_83(j, record["relink"], other_link["personName"])

    # ---- nobody twice
    with j.recorder.step("contacts (Find 25 more): the second page is the two left -- 12 credits, 6 a name -- and "
                         "repeats nobody", party="founder", kind="assert") as h:
        receipt = _fetch(j, wire, record, everyone, dataset_id, query, fetched, first["ids"][-1], DATASET_NAME)
        second = record["pages"][-1]
        h.record_assert({"rows": 2, "charged": 12, "repeats": []},
                        {"rows": len(second["ids"]), "charged": receipt.get("creditsCharged"),
                         "repeats": sorted(set(second["ids"]) & set(first["ids"]))})
        assert len(second["ids"]) == 2 and receipt.get("creditsCharged") == 2 * fake.NAME_CREDITS, receipt
        assert not set(second["ids"]) & set(first["ids"]), second["ids"]

    with j.recorder.step(f"contacts (E11): a second dataset on the same search, {SECOND_NAME!r}, sizes to 0 -- every "
                         "one of the 27 was fetched on this project -- and its empty page charges nothing",
                         party="founder", kind="assert") as h:
        _, created = wire("POST", "/contacts/datasets", {"respondentType": KIND, "name": SECOND_NAME, "query": query})
        second_id = (created.get("dataset") or {}).get("datasetId")
        sized = _size(j, wire, record, everyone, second_id, query, fetched, SECOND_NAME)
        rows_before = len(stack_ledger.rows(j.stack, founder_id))
        before = wire.credits()
        _, empty = wire("POST", f"/contacts/datasets/{second_id}/fetch", {})
        record["second_dataset"] = {"size": sized, "fake": fake.size(everyone, query, fetched),
                                    "page": empty.get("page"), "charged": empty.get("creditsCharged"),
                                    "balance": [before, wire.credits()],
                                    "ledger_rows_added": len(stack_ledger.rows(j.stack, founder_id)) - rows_before}
        h.record_assert({"size": 0, "page": [], "charged": 0}, record["second_dataset"])
        assert sized == 0 and empty.get("page") == [] and empty.get("creditsCharged") == 0, record["second_dataset"]

    # ---- the two refusals at a low balance
    with j.recorder.step(f"contacts: another kind's dataset in another country, {ELSEWHERE_NAME!r} -- 26 with a work "
                         "email, none fetched yet", party="founder", kind="assert") as h:
        elsewhere = {"places": [{"kind": "COUNTRY", "code": "US"}]}
        _, created = wire("POST", "/contacts/datasets", {"respondentType": vs.LINK_PRIMARY, "name": ELSEWHERE_NAME,
                                                         "query": elsewhere})
        elsewhere_id = (created.get("dataset") or {}).get("datasetId")
        us = _size(j, wire, record, everyone, elsewhere_id, elsewhere, fetched, ELSEWHERE_NAME)
        h.record_assert(26, us)
        assert us == 26, us

    with j.recorder.step(f"contacts: STAND-IN (call 130) -- the balance lowered to {LOW_BALANCE}; the fake's 53 people "
                         "cannot spend a grant of 1,500 below 546", party="stack", kind="protocol") as h:
        delta = stack_ledger.stand_in_balance(j.stack, founder_id, run, to=LOW_BALANCE)
        h.record_wire({"row": delta}, {"creditsAvailable": wire.credits()})
        assert wire.credits() == LOW_BALANCE

    with j.recorder.step(f"contacts (D5): at {LOW_BALANCE} credits a page of names and the two waiting names' emails "
                         "are REFUSED 422 with required / available -- nothing fetched, revealed, stored or charged",
                         party="founder", kind="assert") as h:
        refusals = {}
        waiting = second["ids"]                                  # the first dataset's second page, still unsaved
        for name, method, suffix, body, required in (
                ("names", "POST", f"/contacts/datasets/{elsewhere_id}/fetch", {}, fake.PAGE_CREDITS),
                ("emails", "POST", f"/contacts/datasets/{dataset_id}/save", {"sourceIds": waiting},
                 len(waiting) * fake.EMAIL_CREDITS)):
            rows_before = len(stack_ledger.rows(j.stack, founder_id))
            view_before = wire("GET", f"/contacts/datasets/{dataset_id}")[1]
            status, refusal = wire(method, suffix, body, ok=(422,))
            view_after = wire("GET", f"/contacts/datasets/{dataset_id}")[1]
            us_after = wire("POST", f"/contacts/datasets/{elsewhere_id}/size", {})[1].get("sizedWithEmail")
            refusals[name] = {"status": status, "body": refusal, "required": required, "available": LOW_BALANCE,
                              "balance_after": wire.credits(),
                              "ledger_rows_added": len(stack_ledger.rows(j.stack, founder_id)) - rows_before,
                              "unchanged": (len(view_before.get("people") or []) == len(view_after.get("people") or [])
                                            and [r["sourceId"] for r in view_before.get("page") or []]
                                            == [r["sourceId"] for r in view_after.get("page") or []]
                                            and us_after == 26)}
        record["credit_refusals"] = refusals
        h.record_assert({"names": {"code": "INSUFFICIENT_CREDITS_FOR_NAMES", "required": 150, "available": LOW_BALANCE},
                         "emails": {"code": "INSUFFICIENT_CREDITS_FOR_EMAILS", "required": 24,
                                    "available": LOW_BALANCE}}, refusals)
        for name, code in (("names", "INSUFFICIENT_CREDITS_FOR_NAMES"), ("emails", "INSUFFICIENT_CREDITS_FOR_EMAILS")):
            assert refusals[name]["body"].get("code") == code, refusals[name]


def _drift_83(j, relink: dict, who: str) -> None:
    """DRIFT #83, stepped round (call 136): keel-cloud 093 call 16 says the found person's `linkMadeAt` keeps the first
    link's time while the register's *Link made* moves; the wire's `FoundPersonRow.linkMadeAt` reads the invitation's
    (`ContactsController.personRow`), so it moves too, and the first time is served nowhere. Named while it fires; held
    to call 16 the moment it does not."""
    served, first = relink.get("found_person_linkMadeAt"), relink.get("first_linkMadeAt")
    if served == relink.get("relinked_at") != first:
        with j.recorder.step(f"DRIFT #83 -- {who}'s found-person row reads the new link's time ({served}), not the first "
                             f"link's ({first}) that keel-cloud 093 call 16 says it keeps; the register's Link made "
                             "moved, as it should", party="stack", kind="note") as h:
            h.record_wire({"call 16": "the found person's linkMadeAt keeps the first link's time"}, relink)
        return
    with j.recorder.step(f"contacts (call 16): {who}'s found-person row keeps the first link's time", party="stack",
                         kind="assert") as h:
        h.record_assert(first, served)
        assert served == first, relink


def _score(j, record: dict, *, require: list[str]) -> None:
    """The contacts marks over the record, written into the bundle; the leg fails on any required mark unmet."""
    card = marks.scorecard(record)
    run_dir = j.recorder.run_dir
    (Path(run_dir) / "contacts.json").write_text(json.dumps(record, indent=2, default=str) + "\n", encoding="utf-8")
    (Path(run_dir) / "contacts-marks.json").write_text(json.dumps(card, indent=2, default=str) + "\n",
                                                       encoding="utf-8")
    with j.recorder.step(f"contacts marks v{marks.CONTACTS_MARKS_VERSION}: {card['met']} of {card['measured']} met "
                         f"({', '.join(require)} owed)", party="stack", kind="assert") as h:
        owed = {c["mark"]: c for c in card["checks"] if c["mark"] in require}
        h.record_assert({m: True for m in require}, {m: {"ok": c["ok"], "detail": c["detail"]}
                                                     for m, c in owed.items()})
        unmet = [m for m, c in owed.items() if not (c["measured"] and c["ok"])]
        assert not unmet, {m: owed[m] for m in unmet}
