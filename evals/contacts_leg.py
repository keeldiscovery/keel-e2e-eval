"""The contacts leg (spec 043, keel-cloud 093 at contract 15; keel-web 068's Interviews section since the second
commit): after S-006's journey the founder finds the decision-makers through Keel's Contacts -- **on keel-web's own
screens** -- Keel's base query on its tab, *Start from it*, *Size it* (free), the chips removed down to the market,
*Show the first 25* (150 credits), the page of names and *Save 3 picked* (12 each), C3, *Go to Sent → Send more* (Text;
the AI interviewer greyed, *not recorded* since keel-web 069), the batch's links and .csv; one found person answers on
the stranger's own screens; *Make a new link* on Sent; *Find 25 more*; a second dataset that finds nobody new; the two credit refusals in the *Not enough
credits* popup at a low balance; and nothing ever emailed. S-005 holds the B2C half: `NOT_B2B` and its card.

**Every screen is held to the wire it was handed**: each press returns the response keel-web received (the page
objects in `harness/interviews_screens.py`), the founder's session re-reads the dataset, the register and the ledger,
and keel-cloud's own fake contact source (`keel.v2.contacts.source = fake`, the stack's default) is restated by
`harness/contacts_fake.py`. Four things stay on the wire because no screen can say them (judgement call 139): the
AI interviewer's refusal (keel-web greys it and never sends it), a relink of an answered link (Sent offers none), a
dataset in another country (C2's places narrow within the market's own country, #50), and the empty page of a search
sized 0 (C2 turns *Show the first 25* off).

**The founder's door is a stand-in** (judgement calls 129-131, `stack/ledger.py`): the journey's founder is on their
own AI (the scripted runtime built the project), contacts need credits, and on a stack with no Keel's-AI key nothing
else can build a locked B2B project for a Keel's-AI founder. So the leg asserts the own-AI refusal first, stands the
founder on Keel's door with a fresh grant of 2,000, does the work, lowers the balance once for the two refusals, and
puts the founder back on their own door in a `finally`. On the remote profile (the staging twin, no database) only the
own-AI refusal runs, and the rest is skipped by name.

Every rule is scored by `evals/contacts_marks.py` over the record this leg builds (`contacts.json` and
`contacts-marks.json` in the run bundle); the leg fails when any mark is unmet. No model runs anywhere here.
"""

from __future__ import annotations

import dataclasses
import json
import re
import time
from pathlib import Path

import requests
import yaml

from evals import contacts_marks as marks
from evals import corpus_scenario
from harness import contacts_fake as fake
from harness import interviews_screens as iv
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from stack import cloud as stack_cloud
from stack import ledger as stack_ledger
from stack.config import REPO_ROOT

KIND = vs.LINK_B2B
#: The founder's first three picks get their emails and their links; the first answers, the second gets a new link.
PICKS = 3
#: The balance the refusals are seen at (stand-in 2): under a page (150) and under the one name waiting (12) -- 20
#: until spec 053, when the market was GB: its 27 left two names after the first page, their emails 24.
LOW_BALANCE = 10
#: Spec 053 (D20): the base query's place is the project's market (keel-cloud `BaseQuery.marketFor`), every corpus
#: entry's is the US since revision 12, so the market's own dataset is the US's; the other country is the fake's other,
#: GB (it has no third; judgement call 5). The counts are `fake.size` on each country wherever the code can read them.
DATASET_NAME = "Everyone in the US"
SECOND_NAME = "Everyone in the US, again"
ELSEWHERE_COUNTRY = "GB"
ELSEWHERE_NAME = "Practitioners in the UK"

#: What waited for keel-web 068's page objects (built in spec 043's second commit, `harness/interviews_screens.py`).
WEB_068_FOLLOW_UP = (
    "keel-web 068 (the Interviews section), DONE in spec 043's second commit: page objects for the Contacts tabs, the "
    "dataset page, the Send more popup and the Sent register, each held to the wire this leg already held.")


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


class _Captured:
    """Every contacts / register body keel-web itself received while the leg ran (CM7 sweeps their keys too)."""

    def __init__(self, page, record: dict):
        self.page = page
        self.record = record

    def __enter__(self):
        self.page.on("response", self._keep)
        return self

    def __exit__(self, *exc) -> None:
        self.page.remove_listener("response", self._keep)

    def _keep(self, response) -> None:
        url = response.url
        if "/v2/projects/" not in url or not ("/contacts/" in url or "/invitations" in url):
            return
        try:
            body = response.json()
        except Exception:  # noqa: BLE001 - a 204 or a page
            return
        self.record["responses"].append({"method": response.request.method, "path": url, "status": response.status,
                                         "body": body, "by": "keel-web"})


def _downloads(page):
    """A press that downloads a file, read back as text (the batch's own .csv, verbatim)."""
    def press(click) -> str:
        with page.expect_download(timeout=20_000) as got:
            click()
        return Path(got.value.path()).read_text(encoding="utf-8")
    return press


# ---------------------------------------------------------------------------------------------- B2C

def leg_contacts_not_b2b(j) -> dict:
    """S-005 (01-countly, B2C): Contacts are refused NOT_B2B -- before any other gate, so an own-AI founder meets it
    too (keel-cloud 093 call 8's order: ownership, NOT_B2B, NOT_LOCKED, CONTACTS_NEED_CREDITS) -- and keel-web 068
    draws *Finding consumers is coming* (D10)."""
    record: dict = {"entry": j.entry.id, "project_id": j.project_id, "responses": []}
    wire = _Wire(j, record)
    contacts = iv.Contacts(j.page, j.recorder, j.web_base, patience=j.patience)
    with j.recorder.step("contacts (keel-cloud 093, D10): a consumer study's Contacts are refused NOT_B2B; keel-web "
                         "draws *Finding consumers is coming*", party="founder", kind="assert") as h:
        drawn = contacts.open(j.project_id)
        status, body = wire("GET", "/contacts/datasets", ok=(422,))
        created, created_body = wire("POST", "/contacts/datasets", {"respondentType": vs.LINK_PRIMARY}, ok=(422,))
        record["not_b2b"] = {"status": status, "body": body, "create": {"status": created, "body": created_body},
                             "drawn": drawn}
        h.record_assert({"status": 422, "code": "NOT_B2B", "card": iv.CONTACTS_B2C_TITLE}, record["not_b2b"])
        assert body.get("code") == "NOT_B2B" and created_body.get("code") == "NOT_B2B", record["not_b2b"]
        assert drawn.get("card") == iv.CONTACTS_B2C_TITLE, drawn
    _score(j, record, require=["CM14"])
    return record


# ---------------------------------------------------------------------------------------------- B2B

def leg_contacts(j) -> dict:
    """S-006 (05-paidly, B2B), after the brief. See the module docstring for the order."""
    record: dict = {"entry": j.entry.id, "project_id": j.project_id, "responses": [], "sizes": [], "pages": [],
                    "purchases": [], "saved": []}
    wire = _Wire(j, record)
    contacts = iv.Contacts(j.page, j.recorder, j.web_base, patience=j.patience)

    with j.recorder.step("contacts (keel-cloud 093, D9): on their own AI the founder's Contacts are refused "
                         "CONTACTS_NEED_CREDITS; keel-web draws its one line", party="founder", kind="assert") as h:
        me = wire.me()
        status, body = wire("GET", "/contacts/datasets", ok=(422,))
        drawn = contacts.open(j.project_id)
        record["own_ai_refusal"] = {"status": status, "body": body, "aiPath": me.get("aiPath"), "drawn": drawn}
        h.record_assert({"aiPath": "OWN", "status": 422, "code": "CONTACTS_NEED_CREDITS",
                         "line": iv.CONTACTS_NEED_CREDITS_LINE}, record["own_ai_refusal"])
        assert me.get("aiPath") == "OWN" and body.get("code") == "CONTACTS_NEED_CREDITS", record["own_ai_refusal"]
        assert drawn.get("line") == iv.CONTACTS_NEED_CREDITS_LINE, drawn

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
        with _Captured(j.page, record):
            _the_work(j, wire, contacts, record, everyone, founder_id, run)
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
    with j.recorder.step("contacts: STAND-IN (call 129) -- the founder on Keel's door with a fresh grant of 2,000; on a "
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


def _rows(j, record: dict) -> int:
    return len(stack_ledger.rows(j.stack, record["founder_id"]))


def _sized(j, wire: _Wire, record: dict, everyone, press, query: dict, fetched: set, label: str) -> dict:
    """A *Size it* the founder pressed: the size keel-web received, held to the fake's count, free."""
    before, rows_before = wire.credits(), _rows(j, record)
    out = press()
    entry = {"dataset": label, "wire": (out["summary"] or {}).get("sizedWithEmail"),
             "fake": fake.size(everyone, query, fetched), "balance_before": before, "balance_after": wire.credits(),
             "ledger_rows_added": _rows(j, record) - rows_before, "drawn": out.get("drawn")}
    record["sizes"].append(entry)
    return {**out, "entry": entry}


def _paged(j, wire: _Wire, record: dict, everyone, press, query: dict, fetched: set, after: str | None,
           label: str) -> dict:
    """A page of names the founder asked for: the receipt keel-web received, the names it drew, the fake's own."""
    before = wire.credits()
    out = press()
    receipt = out["body"] or {}
    rows = receipt.get("page") or []
    ids = [r["sourceId"] for r in rows]
    record["pages"].append({"dataset": label, "ids": ids, "rows": rows, "drawn": (out["drawn"] or {}).get("names"),
                            "fake_ids": [p.source_id for p in fake.page(everyone, query, fetched, after=after)]})
    record["purchases"].append({"action": "CONTACT_PAGE", "charged": receipt.get("creditsCharged"),
                                "available": receipt.get("creditsAvailable"), "balance_before": before,
                                "me_after": wire.credits(), "units": len(rows)})
    fetched.update(ids)
    return out


def _dataset_id(url: str) -> str:
    match = re.search(r"/interviews/contacts/([0-9a-f-]{36})", url)
    assert match, url
    return match.group(1)


def _the_work(j, wire: _Wire, contacts, record: dict, everyone, founder_id: str, run: str) -> None:
    fetched: set[str] = set()
    sent = iv.Interviews(j.page, j.recorder, j.web_base, patience=j.patience)

    # ---- C1: the tabs and Keel's base query
    with j.recorder.step("contacts (C1): one tab per kind of people -- the translators and the agency project managers "
                         "-- each with Keel's base query, sized free to the fake's own count; the prices from the "
                         "server's table", party="founder", kind="assert") as h:
        _, overview = wire("GET", "/contacts/datasets")
        kinds = {k["respondentType"]: k for k in overview.get("kinds") or []}
        deciders = kinds.get(KIND) or {}
        base = (deciders.get("base") or {}).get("query") or {}
        drawn = contacts.open(j.project_id)
        tab = contacts.tab(deciders.get("label") or "")
        # Spec 046 FM3 (keel-cloud 097 F5): the base query carries no industry, on any kind's tab.
        j.feedback["base_query"] = {k: (v.get("base") or {}).get("query") for k, v in kinds.items()}
        record["overview"] = {"kinds": list(kinds), "prices": overview.get("prices"), "base": base,
                              "base_sized": (deciders.get("base") or {}).get("sizedWithEmail"),
                              "base_fake": fake.size(everyone, base) if base else None, "drawn": drawn, "tab": tab}
        h.record_assert({"kinds": [vs.LINK_PRIMARY, KIND], "prices": {"page": 150, "email": 12, "pageSize": 25},
                         "base sized": record["overview"]["base_fake"],
                         "tabs": [f"{kinds[k]['label']} · 0" for k in kinds]}, record["overview"])
        assert list(kinds) == [vs.LINK_PRIMARY, KIND], list(kinds)
        assert overview.get("prices") == {"page": fake.PAGE_CREDITS, "email": fake.EMAIL_CREDITS,
                                          "pageSize": fake.PAGE_SIZE}, overview.get("prices")
        assert base.get("levels") and set(base["levels"]) == {"MANAGER", "DIRECTOR"}, base
        assert [{k: v for k, v in p.items() if k != "label"} for p in base.get("places") or []] == \
            [{"kind": "COUNTRY", "code": j.entry.market["country"]}], base
        assert record["overview"]["base_sized"] == record["overview"]["base_fake"], record["overview"]
        assert drawn.get("tabs") == [f"{kinds[k]['label']} · 0" for k in kinds], drawn
        assert tab["datasets"] == [] and tab["base"]["sized"].startswith("Sized free"), tab
        assert f"about {record['overview']['base_fake']} with a work email" in tab["base"]["sized"], tab

    with j.recorder.step("contacts (C2): *Start from it* draws Keel's base query as chips; *Size it* makes the dataset "
                         "(BASE) and sizes it free to the fake's count", party="founder", kind="assert") as h:
        chips = contacts.start_from_base()
        out = _sized(j, wire, record, everyone, contacts.size_it, base, fetched, "base")
        dataset_id = _dataset_id(out["url"])
        _, view = wire("GET", f"/contacts/datasets/{dataset_id}")
        dataset = view.get("dataset") or {}
        h.record_assert({"chips": {"titles": base["titles"], "levels": len(base["levels"]),
                                   "sizes": len(base["companySizes"])}, "basedOn": "BASE", "sized": out["entry"]["fake"]},
                        {"chips": chips, "dataset": dataset, "sized": out["entry"]})
        assert chips.get("Who · job titles") == base["titles"], chips
        assert len(chips.get("Level") or []) == len(base["levels"]), chips
        assert len(chips.get("Companies") or []) == len(base.get("categories") or []) + len(base["companySizes"]), chips
        assert dataset.get("basedOn") == "BASE" and dataset.get("respondentType") == KIND, dataset
        assert {k: dataset["query"].get(k) or [] for k in ("titles", "levels", "categories", "companySizes")} == \
            {k: base.get(k) or [] for k in ("titles", "levels", "categories", "companySizes")}, (dataset["query"], base)
        assert out["entry"]["wire"] == out["entry"]["fake"], out["entry"]

    country = j.entry.market["country"]
    market_query = {"places": [{"kind": "COUNTRY", "code": country}]}
    in_market = [p for p in everyone if p.country == country]
    with_email = fake.size(everyone, market_query)                     # 26 on the US since spec 053 (27 on GB)
    left_after_page = with_email - fake.PAGE_SIZE                      # 1 (2 on GB)
    with j.recorder.step(f"contacts (C2, call 132): the founder removes every chip but the market, names it "
                         f"{DATASET_NAME!r} -- the fake's payroll people match no Paidly title -- and sizes it again: "
                         f"{with_email} with a work email ({len(in_market)} in the {country}, "
                         f"{sum(1 for p in in_market if not p.email)} with none, never counted)", party="founder",
                         kind="assert") as h:
        chips = contacts.remove_all_but_places()
        contacts.name(DATASET_NAME)
        query = {"places": [{k: v for k, v in place.items() if k != "label"} for place in base["places"]]}
        out = _sized(j, wire, record, everyone, lambda: contacts.size_it(again=True), query, fetched, DATASET_NAME)
        _, view = wire("GET", f"/contacts/datasets/{dataset_id}")
        dataset = view.get("dataset") or {}
        h.record_assert({"chips": {"Where": 1}, "name": DATASET_NAME, "sizedWithEmail": with_email,
                         "drawn": f"About {with_email}"},
                        {"chips": chips, "dataset": dataset, "sized": out["entry"]})
        assert query == market_query, (query, market_query)
        assert [k for k, v in chips.items() if v] == ["Where"], chips
        assert dataset.get("name") == DATASET_NAME and dataset.get("sizedWithEmail") == with_email, dataset
        assert dataset["query"]["titles"] == [] and dataset["query"]["levels"] == [], dataset["query"]
        assert out["entry"]["wire"] == with_email == out["entry"]["fake"], out["entry"]
        assert (out["entry"]["drawn"] or "").startswith(f"About {with_email} people with a work email"), out["entry"]
        # the fixture's own facts (keel-cloud 092 FR-D, `fake-contacts.json`): 29 in the US, 3 with no work email
        assert country == "US" and len(in_market) == 29 and with_email == 26, (country, len(in_market), with_email)
        assert 0 < left_after_page < fake.PAGE_SIZE, left_after_page
    record["dataset_name"] = DATASET_NAME

    with j.recorder.step("contacts (Show 25): a page of 25 names is 150 credits, the fake's own first 25, drawn with a "
                         "box each and no email on any row; the balance and /v2/me drop by 150", party="founder",
                         kind="assert") as h:
        out = _paged(j, wire, record, everyone, contacts.show_first, query, fetched, None, DATASET_NAME)
        receipt, first = out["body"], record["pages"][-1]
        names = [r["fullName"] for r in first["rows"]]
        # spec 048: the grant is 2,000 since spec 047 (keel-cloud 098); this line still read 1,500 - 150
        h.record_assert({"rows": 25, "charged": 150, "available": stack_ledger.GRANT_CREDITS - 150,
                         "ids": first["fake_ids"], "drawn": names},
                        {"rows": len(first["ids"]), "charged": receipt.get("creditsCharged"),
                         "available": receipt.get("creditsAvailable"), "ids": first["ids"], "drawn": out["drawn"]})
        assert out["status"] == 200 and len(first["ids"]) == 25 and receipt.get("creditsCharged") == 150, receipt
        assert receipt.get("creditsAvailable") == stack_ledger.GRANT_CREDITS - 150 == wire.credits(), receipt
        assert (receipt.get("dataset") or {}).get("moreToFetch") is True, receipt.get("dataset")
        assert out["drawn"]["names"] == names, out["drawn"]
        _, resized = wire("POST", f"/contacts/datasets/{dataset_id}/size", {})
        assert resized.get("sizedWithEmail") == left_after_page, resized

    with j.recorder.step(f"contacts (Save): the founder ticks {PICKS} and saves them -- *Save {PICKS} picked and get "
                         f"their emails · {PICKS * 12} credits* -- the fake's own addresses, email only; C3 draws each "
                         "*Saved · no link yet*", party="founder", kind="assert") as h:
        picks = names[:PICKS]
        before = wire.credits()
        out = contacts.save_picked(picks, tools=True)
        saved = out["body"] or {}
        record["purchases"].append({"action": "CONTACT_EMAIL", "charged": saved.get("creditsCharged"),
                                    "available": saved.get("creditsAvailable"), "balance_before": before,
                                    "me_after": wire.credits(), "units": saved.get("savedCount")})
        by_name = {p.full_name: p for p in everyone}
        for person in (saved.get("dataset") or {}).get("people") or []:
            truth = by_name.get(person["fullName"])
            record["saved"].append({**{k: person.get(k) for k in ("foundPersonId", "fullName", "email", "emailStatus",
                                                                 "verified", "status")},
                                    "fake_email": truth.email if truth else None,
                                    "fake_status": truth.email_status if truth else None})
        c3 = out["drawn"]
        h.record_assert({"button": f"Save {PICKS} picked and get their emails · {PICKS * 12} credits",
                         "savedCount": PICKS, "charged": PICKS * 12, "status": iv.FOUND_STATUS["FOUND"]},
                        {"button": out["button"], "saved": record["saved"], "c3": c3})
        assert out["button"] == f"Save {PICKS} picked and get their emails · {PICKS * 12} credits", out["button"]
        assert saved.get("savedCount") == PICKS and saved.get("creditsCharged") == PICKS * fake.EMAIL_CREDITS, saved
        assert len(record["saved"]) == PICKS and {s["status"] for s in record["saved"]} == {"FOUND"}, record["saved"]
        drawn_names = sorted(n for n in picks if any(r.get("Name", "").startswith(n) for r in c3["rows"]))
        assert drawn_names == sorted(picks) and len(c3["rows"]) == PICKS, c3
        assert all(iv.FOUND_STATUS["FOUND"] in r.get("Status", "") for r in c3["rows"]), c3
        assert all(any(s["email"] in r.get("Email", "") for r in c3["rows"]) for s in record["saved"]), c3
    with j.recorder.step("contacts (keel-web 070 F3 / F4): on the page of names *Select all* ticks the page's 25 and the "
                         f"button counts them -- *Save 25 picked ... · {25 * fake.EMAIL_CREDITS} credits* -- and *Clear* "
                         "unticks them (Save off, 0); one page, so no pager; the dataset page draws no *Copy as a new "
                         "dataset*", party="founder", kind="assert") as h:
        tools = out["tools"] or {}
        n = tools.get("rows")
        want = {"labels": {"select_all": iv.NAMES_SELECT_ALL, "clear": iv.NAMES_CLEAR},
                "all": f"Save {n} picked and get their emails · {n * fake.EMAIL_CREDITS} credits",
                "cleared": f"Save 0 picked and get their emails · 0 credits", "copy_as_new": 0}
        h.record_assert(want, {**tools, "c3 copy_as_new": c3.get("copy_as_new")})
        assert n == iv.NAMES_PER_PAGE and tools["pager"] is False, tools
        assert tools["labels"] == want["labels"], tools
        assert tools["before"] == {"select_all": True, "clear": False}, tools
        assert tools["all"]["ticked"] == n and tools["all"]["button"] == want["all"], tools
        assert tools["all"]["tools"] == {"select_all": False, "clear": True}, tools
        assert tools["cleared"]["ticked"] == 0 and tools["cleared"]["button"] == want["cleared"], tools
        assert tools["cleared"]["save_enabled"] is False, tools
        assert c3.get("copy_as_new") == 0, c3
    found = [s["foundPersonId"] for s in record["saved"]]
    name_of = {s["foundPersonId"]: s["fullName"] for s in record["saved"]}

    # ---- links: Go to Sent -> Send more
    with j.recorder.step("contacts (S3, call 134; contract 16 since spec 044): the AI interviewer is refused 409 "
                         "INTERVIEWER_NOT_READY -- this project has no recording yet -- on the batch and on the single "
                         "commercial link, and nothing is made", party="founder", kind="assert") as h:
        before = len((wire("GET", "/invitations")[1]).get("invitations") or [])
        status, body = wire("POST", "/invitations/batch", {"expectedRevision": j.revision(), "respondentType": KIND,
                                                           "format": "AI_INTERVIEWER",
                                                           "people": [{"foundPersonId": found[0]}]}, ok=(409,))
        single, single_body = wire("POST", "/commercial-link", {"expectedRevision": j.revision(),
                                                                "personName": "Someone the founder knows",
                                                                "format": "AI_INTERVIEWER"}, ok=(409,))
        after = len((wire("GET", "/invitations")[1]).get("invitations") or [])
        record["format_refusal"] = {"status": status, "body": body, "register_before": before,
                                    "register_after": after,
                                    "commercial_link": {"status": single, "body": single_body}}
        h.record_assert({"status": 409, "code": "INTERVIEWER_NOT_READY", "commercial-link": "INTERVIEWER_NOT_READY"},
                        record["format_refusal"])
        assert body.get("code") == "INTERVIEWER_NOT_READY" == single_body.get("code") and before == after, \
            record["format_refusal"]

    with j.recorder.step(f"contacts (S1-S3a): *Go to Sent → Send more* opens the decision-makers' popup with the dataset "
                         f"chosen -- Text only checked, the AI interviewer and Let them choose *not recorded* -- the "
                         f"founder picks the {PICKS}, *Make {PICKS} links*: one batch as Text, each link handed back once "
                         "with the saved email, the batch's own .csv downloaded; Keel sends nothing; each LINK_MADE",
                         party="founder", kind="assert") as h:
        contacts.go_to_send_more()
        made = sent.send_from_dataset([name_of[f] for f in found], downloads=_downloads(j.page))
        batch = made["batch"] or {}
        links = batch.get("links") or []
        record["batch"] = {"format": batch.get("format"), "links": links, "csv": batch.get("csv"),
                           "downloaded": made["csv"], "ui": {k: made[k] for k in ("formats", "who", "dataset",
                                                                                  "rows", "table")}}
        _, view = wire("GET", f"/contacts/datasets/{dataset_id}")
        statuses = {fp: p.get("status") for fp, p in _people_by_id(view).items() if fp in found}
        h.record_assert({"links": PICKS, "format": "TEXT", "statuses": "LINK_MADE", "csv lines": PICKS + 1,
                         "dataset": DATASET_NAME, "downloaded": "the batch's csv, verbatim"},
                        {"batch": record["batch"], "statuses": statuses})
        assert made["status"] == 201 and batch.get("format") == "TEXT" and len(links) == PICKS, batch
        text = made["formats"][iv.TEXT_ONLY]
        assert text["checked"] and not text["disabled"], made["formats"]
        # keel-web 069: on Keel's door with no recording yet the other two are greyed *not recorded*
        assert all(f["disabled"] and f["word"] == iv.FORMAT_NOT_RECORDED
                   for name, f in made["formats"].items() if name != iv.TEXT_ONLY), made["formats"]
        assert made["who"].get("true") == iv.WHO_DATASET and made["dataset"] == DATASET_NAME, made
        assert sorted(link.get("foundPersonId") for link in links) == sorted(found), links
        assert {link.get("email") for link in links} == {s["email"] for s in record["saved"]}, links
        assert made["csv"] == batch.get("csv") and len((batch.get("csv") or "").splitlines()) == PICKS + 1, made["csv"]
        assert len(made["table"]) == PICKS, made["table"]
        assert set(statuses.values()) == {"LINK_MADE"}, statuses
    link_of = {link["foundPersonId"]: link for link in links}

    # ---- one found person answers, through the stranger's own screens
    answered, relinked_person = found[0], found[1]
    answered_link, other_link = link_of[answered], link_of[relinked_person]
    token = _token(answered_link["url"])
    decider = next(p for p in j.people if p.link == KIND)
    trail = [record["saved"][0]["status"]]

    def status_of(fp: str) -> str | None:
        return _people_by_id(wire("GET", f"/contacts/datasets/{dataset_id}")[1]).get(fp, {}).get("status")

    trail.append(status_of(answered))
    stranger = j.browser.new_context()
    try:
        page = stranger.new_page()
        screens = vs_screens.Interview(page, j.recorder)
        with j.recorder.step(f"contacts: {answered_link['personName']} opens their link -- a decision-maker's interview, "
                             "part 3 alone -- and reads OPENED", party="participant", kind="assert") as h:
            got, interview = _participant(j, "GET", token, "/interview")
            screens.open(answered_link["url"])
            deadline = time.monotonic() + 20
            while status_of(answered) != "OPENED" and time.monotonic() < deadline:
                time.sleep(0.5)
            trail.append(status_of(answered))
            h.record_assert({"interview": 200, "kind": "COMMERCIAL_LINK", "status": "OPENED"},
                            {"interview": got, "kind": interview.get("kind"), "status": trail[-1]})
            assert got == 200 and interview.get("kind") == "COMMERCIAL_LINK", got

        with j.recorder.step(f"contacts: {answered_link['personName']} answers on their own screens (the corpus "
                             f"decision-maker {decider.person}'s picks, call 133) and reads ANSWERED",
                             party="participant", kind="assert") as h:
            items = {i.get("dimension"): i for part in interview.get("parts") or [] for i in part.get("items") or []}
            recall = ((items.get("commercial.existing_sacrifice") or {}).get("costTotal") or {}).get("recallPeriod")
            expected = decider.response(token, recall)
            by_item = {a["itemId"]: a for a in expected.get("answers") or []}
            walked = screens.walk(dataclasses.replace(decider, person=answered_link["personName"]), interview,
                                  by_item)
            deadline = time.monotonic() + 20
            while status_of(answered) != "ANSWERED" and time.monotonic() < deadline:
                time.sleep(0.5)
            trail.append(status_of(answered))
            record["status_trail"] = trail
            h.record_assert({"sent": expected, "trail": marks.STATUS_ORDER}, {"sent": walked["body"], "trail": trail})
            assert corpus_scenario._normal_body(walked["body"] or {}) == corpus_scenario._normal_body(expected), \
                (walked["body"], expected)
    finally:
        stranger.close()

    with j.recorder.step("contacts (T1): the Sent register -- newest link first; the answered person's row reads Text, "
                         f"from the {DATASET_NAME!r} dataset, Answered, with no *Make a new link*; no email field on any "
                         "row; the decision-makers' kind row counts them", party="founder", kind="assert") as h:
        sent.land(j.project_id)
        drawn = sent.register()
        _, register = wire("GET", "/invitations")
        rows = register.get("invitations") or []
        row = next((r for r in rows if r.get("invitationId") == answered_link["invitationId"]), {})
        kind_row = next((k for k in register.get("kinds") or [] if k.get("respondentType") == KIND), {})
        record["register"] = {"invitations": rows, "kinds": register.get("kinds"), "drawn": drawn}
        record["register_row"] = row
        record["answered_found_person"] = answered
        corpus_deciders = sum(1 for p in j.people if p.link == KIND)
        offers = sent.status_cell_offers(answered_link["personName"])
        drawn_row = next((r for r in drawn if r.get("Who") == answered_link["personName"]), {})
        h.record_assert({"top": sorted(link["personName"] for link in links), "row": "Text · dataset · Answered",
                         "kind": {"linksMade": corpus_deciders + PICKS, "answered": corpus_deciders + 1}},
                        {"top": [r.get("Who") for r in drawn[:PICKS]], "row": drawn_row, "offers": offers,
                         "kind": kind_row})
        assert {r.get("invitationId") for r in rows[:PICKS]} == {link["invitationId"] for link in links}, rows[:PICKS]
        assert [r.get("Who") for r in drawn] == [r.get("personName") for r in rows], drawn
        assert drawn_row.get("Format") == "Text" and "dataset" in (drawn_row.get("Kind · from") or ""), drawn_row
        assert (drawn_row.get("Status") or "").startswith(iv.REGISTER_STATUS["ANSWERED"]), drawn_row
        assert iv.MAKE_A_NEW_LINK not in offers, offers
        assert kind_row.get("linksMade") == corpus_deciders + PICKS, kind_row
        assert kind_row.get("answered") == corpus_deciders + 1, kind_row

    with j.recorder.step(f"contacts (D7): *Make a new link* for {other_link['personName']} on Sent -- the old link "
                         "answers 404, the new one opens, the same invitation; an answered link is refused "
                         "ALREADY_ANSWERED", party="founder", kind="assert") as h:
        old = _token(other_link["url"])
        first_made = next((r.get("linkMadeAt") for r in record["register"]["invitations"]
                           if r.get("invitationId") == other_link["invitationId"]), None)
        made = sent.make_new_link(other_link["personName"])
        relinked = made["relinked"] or {}
        new = _token(made["url"])
        old_status, _ = _participant(j, "GET", old, "/interview")
        new_status, _ = _participant(j, "GET", new, "/interview")
        refused, refusal = wire("POST", f"/invitations/{answered_link['invitationId']}/relink",
                                {"expectedRevision": j.revision()}, ok=(422,))
        _, register = wire("GET", "/invitations")
        moved = next((r for r in register.get("invitations") or []
                      if r.get("invitationId") == other_link["invitationId"]), {})
        person = _people_by_id(wire("GET", f"/contacts/datasets/{dataset_id}")[1]).get(relinked_person, {})
        record["relink"] = {"old_url": other_link["url"], "new_url": made["url"], "old_status": old_status,
                            "new_status": new_status, "drawn_is_served": made["url"] == relinked.get("url"),
                            "same_invitation": relinked.get("invitationId") == other_link["invitationId"],
                            "first_linkMadeAt": first_made, "register_linkMadeAt": moved.get("linkMadeAt"),
                            "relinked_at": relinked.get("linkMadeAt"),
                            "found_person_linkMadeAt": person.get("linkMadeAt"),
                            "answered_refusal": {"status": refused, "body": refusal}}
        h.record_assert({"old": 404, "new": 200, "answered": "ALREADY_ANSWERED"}, record["relink"])
        assert made["status"] == 201 and made["url"] == relinked.get("url"), made
        assert old_status == 404 and new_status == 200, record["relink"]
        assert moved.get("linkMadeAt") == relinked.get("linkMadeAt") != first_made, record["relink"]
    _link_times(j, record["relink"], other_link["personName"])

    # ---- nobody twice
    with j.recorder.step(f"contacts (Find 25 more): on C3 the second page is the {left_after_page} left -- "
                         f"{left_after_page * fake.NAME_CREDITS} credits, {fake.NAME_CREDITS} a name -- and repeats "
                         "nobody", party="founder", kind="assert") as h:
        contacts.open_dataset(j.project_id, dataset_id)
        out = _paged(j, wire, record, everyone, contacts.find_more, query, fetched, first["ids"][-1], DATASET_NAME)
        receipt, second = out["body"], record["pages"][-1]
        h.record_assert({"rows": left_after_page, "charged": left_after_page * fake.NAME_CREDITS, "repeats": []},
                        {"rows": len(second["ids"]), "charged": receipt.get("creditsCharged"),
                         "repeats": sorted(set(second["ids"]) & set(first["ids"])), "drawn": out["drawn"]})
        assert out["status"] == 200 and len(second["ids"]) == left_after_page, receipt
        assert receipt.get("creditsCharged") == left_after_page * fake.NAME_CREDITS, receipt
        assert not set(second["ids"]) & set(first["ids"]), second["ids"]
        assert out["drawn"]["names"] == [r["fullName"] for r in second["rows"]], out["drawn"]

    with j.recorder.step(f"contacts (E11): a second dataset on the same search, {SECOND_NAME!r}, made from the base "
                         f"query's chips with the same ones removed, sizes to 0 -- every one of the {with_email} was fetched on "
                         "this project -- C2 offers no page, and the empty page asked for on the wire charges nothing", party="founder", kind="assert") as h:
        contacts.open(j.project_id)
        contacts.tab(deciders.get("label") or "")
        contacts.start_from_base()
        contacts.remove_all_but_places()
        contacts.name(SECOND_NAME)
        sized = _sized(j, wire, record, everyone, contacts.size_it, query, fetched, SECOND_NAME)
        second_id = _dataset_id(sized["url"])
        offered = contacts.show_first_enabled()                # 068: *Show the first 25* is off at a size of 0
        rows_before, before = _rows(j, record), wire.credits()
        _, empty = wire("POST", f"/contacts/datasets/{second_id}/fetch", {})     # call 139: on the wire, as no screen can
        record["second_dataset"] = {"size": sized["entry"]["wire"], "fake": fake.size(everyone, query, fetched),
                                    "page": empty.get("page"), "charged": empty.get("creditsCharged"),
                                    "balance": [before, wire.credits()], "show_first_offered": offered,
                                    "drawn": sized["entry"]["drawn"],
                                    "ledger_rows_added": _rows(j, record) - rows_before}
        h.record_assert({"size": 0, "page": [], "charged": 0, "show_first_offered": False}, record["second_dataset"])
        assert sized["entry"]["wire"] == 0 and empty.get("page") == [], record["second_dataset"]
        assert empty.get("creditsCharged") == 0 and offered is False, record["second_dataset"]
        assert second_id != dataset_id

    # ---- the two refusals at a low balance
    elsewhere = {"places": [{"kind": "COUNTRY", "code": ELSEWHERE_COUNTRY}]}
    elsewhere_size = fake.size(everyone, elsewhere)                     # 27 on GB (26 on the US until spec 053)
    with j.recorder.step(f"contacts: another kind's dataset in another country, {ELSEWHERE_NAME!r} -- "
                         f"{elsewhere_size} with a work email, none fetched yet (on the wire: the chips narrow within "
                         "the market's own country, #50)", party="founder", kind="assert") as h:
        assert ELSEWHERE_COUNTRY != country and elsewhere_size == 27, (country, elsewhere_size)
        _, created = wire("POST", "/contacts/datasets", {"respondentType": vs.LINK_PRIMARY, "name": ELSEWHERE_NAME,
                                                         "query": elsewhere})
        elsewhere_id = (created.get("dataset") or {}).get("datasetId")
        other = _sized(j, wire, record, everyone,
                       lambda: {"summary": wire("POST", f"/contacts/datasets/{elsewhere_id}/size", {})[1]},
                       elsewhere, fetched, ELSEWHERE_NAME)["entry"]["wire"]
        h.record_assert(elsewhere_size, other)
        assert other == elsewhere_size, other

    with j.recorder.step(f"contacts: STAND-IN (call 130) -- the balance lowered to {LOW_BALANCE}; the fake's 53 people "
                         "cannot spend a grant of 2,000 below 1,046", party="stack", kind="protocol") as h:
        delta = stack_ledger.stand_in_balance(j.stack, founder_id, run, to=LOW_BALANCE)
        h.record_wire({"row": delta}, {"creditsAvailable": wire.credits()})
        assert wire.credits() == LOW_BALANCE

    with j.recorder.step(f"contacts (D5): at {LOW_BALANCE} credits *Show the first 25* and *Save "
                         f"{left_after_page} picked* are REFUSED "
                         "422 with required / available -- the *Not enough credits* popup draws the two numbers, one "
                         "Close, no buy path -- and nothing is fetched, revealed, stored or charged", party="founder",
                         kind="assert") as h:
        refusals = {}
        waiting = [r["fullName"] for r in second["rows"]]          # the first dataset's second page, still unsaved
        for name, open_it, press, required in (
                ("names", lambda: contacts.open_dataset(j.project_id, elsewhere_id, "?view=edit"),
                 contacts.show_first, fake.PAGE_CREDITS),
                ("emails", lambda: contacts.open_dataset(j.project_id, dataset_id, "?view=names"),
                 lambda: contacts.save_picked(waiting), len(waiting) * fake.EMAIL_CREDITS)):
            rows_before = _rows(j, record)
            view_before = wire("GET", f"/contacts/datasets/{dataset_id}")[1]
            open_it()
            out = press()
            view_after = wire("GET", f"/contacts/datasets/{dataset_id}")[1]
            other_after = wire("POST", f"/contacts/datasets/{elsewhere_id}/size", {})[1].get("sizedWithEmail")
            refusals[name] = {"status": out["status"], "body": out["body"], "required": required,
                              "available": LOW_BALANCE, "balance_after": wire.credits(), "drawn": out["drawn"],
                              "ledger_rows_added": _rows(j, record) - rows_before,
                              "unchanged": (len(view_before.get("people") or []) == len(view_after.get("people") or [])
                                            and [r["sourceId"] for r in view_before.get("page") or []]
                                            == [r["sourceId"] for r in view_after.get("page") or []]
                                            and other_after == elsewhere_size)}
        record["credit_refusals"] = refusals
        h.record_assert({"names": {"code": "INSUFFICIENT_CREDITS_FOR_NAMES", "required": 150, "available": LOW_BALANCE,
                                   "drawn": marks.NAMES_REMEDY.format(required=150, available=LOW_BALANCE)},
                         "emails": {"code": "INSUFFICIENT_CREDITS_FOR_EMAILS",
                                    "required": left_after_page * fake.EMAIL_CREDITS, "available": LOW_BALANCE,
                                    "drawn": marks.EMAILS_REMEDY.format(required=left_after_page * fake.EMAIL_CREDITS,
                                                                        available=LOW_BALANCE)}},
                        refusals)
        for name, code, template in (("names", "INSUFFICIENT_CREDITS_FOR_NAMES", marks.NAMES_REMEDY),
                                     ("emails", "INSUFFICIENT_CREDITS_FOR_EMAILS", marks.EMAILS_REMEDY)):
            x = refusals[name]
            assert x["body"].get("code") == code, x
            assert x["drawn"]["sentence"] == template.format(required=x["required"], available=LOW_BALANCE), x
            assert x["drawn"]["buttons"] == ["Close"], x


def _link_times(j, relink: dict, who: str) -> None:
    """keel-cloud 093 call 16, held straight since DRIFT #83 closed (keel-cloud-docs `a4f2c95`): after *Make a new
    link* the register's *Link made* is the new link's time, and the found person's row keeps the first link's."""
    with j.recorder.step(f"contacts (call 16, DRIFT #83 closed): {who}'s found-person row keeps the first link's time; "
                         "the register's Link made moved to the new link's", party="founder", kind="assert") as h:
        h.record_assert({"found person": relink.get("first_linkMadeAt"), "register": relink.get("relinked_at")},
                        {"found person": relink.get("found_person_linkMadeAt"),
                         "register": relink.get("register_linkMadeAt")})
        assert relink.get("found_person_linkMadeAt") == relink.get("first_linkMadeAt"), relink
        assert relink.get("register_linkMadeAt") == relink.get("relinked_at") != relink.get("first_linkMadeAt"), relink


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
