"""Spec 043: the contacts marks (`evals/contacts_marks.py`) over a record shaped like the leg's -- each met on a good
record and each failed by a fault seeded into it, so no mark is a pass that cannot fail; the fake restated
(`harness/contacts_fake.py`) against keel-cloud's own fixture; the stand-ins (`stack/ledger.py`) refused on the remote
profile and never spliced into SQL; the leg's shape (no phone anywhere, the stand-ins reversed in a `finally`)."""

from __future__ import annotations

import copy
import inspect
import uuid

import pytest

from evals import contacts_leg, contacts_marks as marks
from harness import contacts_fake as fake
from stack import ledger
from stack.config import load_config

PROJECT = str(uuid.uuid4())


def _pair(action: str, credits: int, *, version: int = 8) -> list[dict]:
    op = str(uuid.uuid4())
    unit, cost = ((fake.NAME_CREDITS, fake.NAME_COST_MICRO_USD) if action == "CONTACT_PAGE"
                  else (fake.EMAIL_CREDITS, fake.EMAIL_COST_MICRO_USD))
    return [{"kind": "HOLD", "credits": -credits, "action": action, "price_version": version, "project_id": PROJECT,
             "inference_job_id": None, "price_credits": None, "actual_cost_micro_usd": None,
             "idempotency_key": f"contacts:{op}:hold"},
            {"kind": "SPEND", "credits": 0, "action": action, "price_version": None, "project_id": PROJECT,
             "inference_job_id": None, "price_credits": credits, "actual_cost_micro_usd": credits // unit * cost,
             "idempotency_key": f"contacts:{op}:spend"}]


def good() -> dict:
    """A record as S-006's leg writes one: three picks, one answered, one relinked, the two refusals at 20."""
    first = [f"p{i:02d}" for i in range(25)]
    second = ["p25", "p26"]
    links = [{"invitationId": f"i{i}", "personName": f"Person {i}", "foundPersonId": f"f{i}", "email": f"{i}@x.example",
              "emailStatus": "VALID", "url": f"http://localhost:5173/i/t{i}"} for i in range(3)]
    register = [{"invitationId": f"i{2 - i}", "personName": "x", "roleLabel": "r", "invitedAt": "t",
                 "status": "ANSWERED" if i == 2 else "SENT", "respondentType": "COMMERCIAL_B2B", "format": "TEXT",
                 "source": "DATASET", "linkMadeAt": f"2026-10-15T04:00:0{3 - i}.5Z", "foundPersonId": f"f{2 - i}",
                 "datasetName": "Everyone in the UK", "answeredAt": "2026-10-15T04:01:00Z" if i == 2 else None}
                for i in range(3)]
    return {
        "entry": "05-paidly", "project_id": PROJECT,
        "responses": [{"method": "POST", "path": "/fetch", "status": 200, "body": {"page": [{"sourceId": "p00",
                                                                                            "fullName": "A"}]}}],
        "own_ai_refusal": {"status": 422, "body": {"code": "CONTACTS_NEED_CREDITS"}},
        "sizes": [{"dataset": "base", "wire": 0, "fake": 0, "balance_before": 1500, "balance_after": 1500,
                   "ledger_rows_added": 0},
                  {"dataset": "uk", "wire": 27, "fake": 27, "balance_before": 1500, "balance_after": 1500,
                   "ledger_rows_added": 0}],
        "pages": [{"dataset": "uk", "ids": first, "fake_ids": list(first), "rows": [{"sourceId": i} for i in first]},
                  {"dataset": "uk", "ids": second, "fake_ids": list(second), "rows": [{"sourceId": i} for i in second]}],
        "purchases": [{"action": "CONTACT_PAGE", "charged": 150, "available": 1350, "balance_before": 1500,
                       "me_after": 1350, "units": 25},
                      {"action": "CONTACT_EMAIL", "charged": 36, "available": 1314, "balance_before": 1350,
                       "me_after": 1314, "units": 3},
                      {"action": "CONTACT_PAGE", "charged": 12, "available": 1302, "balance_before": 1314,
                       "me_after": 1302, "units": 2}],
        "saved": [{"foundPersonId": f"f{i}", "fullName": f"Person {i}", "email": f"{i}@x.example",
                   "emailStatus": "VALID", "verified": True, "status": "FOUND", "fake_email": f"{i}@x.example",
                   "fake_status": "VALID"} for i in range(3)],
        "ledger": [{"kind": "GRANT", "credits": 1500, "action": None, "price_version": None,
                    "idempotency_key": "e2e-eval:043:x:door"},
                   *_pair("CONTACT_PAGE", 150), *_pair("CONTACT_EMAIL", 36), *_pair("CONTACT_PAGE", 12),
                   {"kind": "PURCHASE", "credits": -1282, "action": None, "price_version": None,
                    "idempotency_key": "e2e-eval:043:x:low-balance"}],
        "format_refusal": {"status": 422, "body": {"code": "FORMAT_NOT_AVAILABLE",
                                                    "problem": "The AI interviewer is not available yet"},
                           "register_before": 20, "register_after": 20,
                           "commercial_link": {"status": 422, "body": {"code": "FORMAT_NOT_AVAILABLE"}}},
        "batch": {"format": "TEXT", "links": links,
                  "csv": "name,email,email_status,link\n" + "\n".join(f"P,{i}@x.example,verified,u" for i in range(3))},
        "status_trail": ["FOUND", "LINK_MADE", "OPENED", "ANSWERED"],
        "register": {"invitations": register, "kinds": []},
        "register_row": register[2], "answered_found_person": "f0", "dataset_name": "Everyone in the UK",
        "relink": {"old_url": "http://x/i/t1", "new_url": "http://x/i/n1", "old_status": 404, "new_status": 200,
                   "same_invitation": True, "answered_refusal": {"status": 422, "body": {"code": "ALREADY_ANSWERED"}}},
        "second_dataset": {"size": 0, "fake": 0, "page": [], "charged": 0, "ledger_rows_added": 0},
        "credit_refusals": {
            "names": {"status": 422, "required": 150, "available": 20, "balance_after": 20, "ledger_rows_added": 0,
                      "unchanged": True,
                      "body": {"rule": "credits", "code": "INSUFFICIENT_CREDITS_FOR_NAMES", "required": 150,
                               "available": 20, "remedy": "A page of 25 names is 150 credits. You have 20."}},
            "emails": {"status": 422, "required": 24, "available": 20, "balance_after": 20, "ledger_rows_added": 0,
                       "unchanged": True,
                       "body": {"rule": "credits", "code": "INSUFFICIENT_CREDITS_FOR_EMAILS", "required": 24,
                                "available": 20,
                                "remedy": "Their verified emails are 24 credits, 12 each. You have 20."}}},
        "stack": {"services": ["postgres", "postgres-playground"], "mail_env": [], "mail_config": []},
        "source": {"port_methods": ["size", "fetch", "revealEmails", "suggestTitles", "suggestCategories",
                                    "suggestPlaces", "checkRevealBatch"], "contact_types": [["email"]],
                   "found_contact_fields": ["sourceId", "fullName", "jobTitle", "companyName", "companyWebsite",
                                            "city", "countryCode", "linkedinUrl"]},
    }


def _by_mark(record: dict) -> dict:
    return {c.mark: c for c in marks.score(record)}


def test_a_good_record_meets_every_b2b_mark_and_leaves_the_b2c_one_unmeasured():
    checks = _by_mark(good())
    assert {m for m, c in checks.items() if c.measured and c.ok} == {f"CM{i}" for i in range(1, 14)}, {
        m: c.detail for m, c in checks.items() if not c.ok}
    assert not checks["CM14"].measured and not checks["CM14"].ok
    card = marks.scorecard(good())
    assert (card["measured"], card["met"], card["unmeasured"]) == (13, 13, ["CM14"])
    assert card["version"] == marks.CONTACTS_MARKS_VERSION == 1


def test_the_b2c_record_measures_not_b2b_alone():
    checks = _by_mark({"not_b2b": {"status": 422, "body": {"code": "NOT_B2B"}}})
    assert [m for m, c in checks.items() if c.measured] == ["CM14"] and checks["CM14"].ok
    assert not _by_mark({"not_b2b": {"status": 404, "body": {}}})["CM14"].ok


def _seed(path: list, value) -> dict:
    record = copy.deepcopy(good())
    target = record
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value(target[path[-1]]) if callable(value) else value
    return record


SEEDED = [
    ("CM1", ["sizes", 1, "wire"], 30),                                       # sized off the fake
    ("CM1", ["sizes", 0, "balance_after"], 1490),                            # sizing charged
    ("CM2", ["ledger"], lambda rows: [r for r in rows if not r["idempotency_key"].endswith(":spend")][:2] + rows[3:]),
    ("CM2", ["ledger", 1, "price_version"], 7),                              # the charge table's old version
    ("CM2", ["ledger", 2, "actual_cost_micro_usd"], 1),                      # a cost off the Starter rate
    ("CM2", ["purchases", 1, "charged"], 48),                                # a receipt with no pair
    ("CM3", ["ledger", 3, "price_version"], 7),
    ("CM4", ["purchases", 0, "me_after"], 1500),                             # /v2/me disagrees
    ("CM5", ["pages", 1, "ids"], ["p24", "p25"]),                            # a repeat
    ("CM5", ["pages", 0, "fake_ids"], ["q"]),                                # not the fake's page
    ("CM6", ["second_dataset", "size"], 27),                                 # fetched people counted again
    ("CM6", ["second_dataset", "charged"], 6),
    ("CM7", ["responses"], [{"body": {"page": [{"sourceId": "a", "phone": "+44"}]}}]),
    ("CM7", ["responses"], [{"body": {"people": [{"mobileNumber": "x"}]}}]),
    ("CM7", ["pages", 0, "rows"], [{"sourceId": "p00", "email": "a@b.example"}]),
    ("CM7", ["saved", 0, "email"], "someone@else.example"),
    ("CM7", ["batch", "csv"], "name,email,phone,link\n"),
    ("CM7", ["source", "contact_types"], [["email", "phone"]]),               # the adapter asks for a phone
    ("CM7", ["source", "port_methods"], ["revealEmails", "revealPhones"]),
    ("CM7", ["source", "found_contact_fields"], ["fullName", "phoneNumber"]),
    ("CM8", ["register", "invitations", 0, "emailedAt"], "2026-10-15T04:00:00Z"),
    ("CM8", ["stack", "services"], ["postgres", "mailhog"]),
    ("CM8", ["stack", "mail_env"], ["KEEL_SMTP_HOST"]),
    ("CM8", ["stack", "mail_config"], ["application.yml: spring.mail.host: x"]),
    ("CM9", ["status_trail"], ["FOUND", "LINK_MADE", "ANSWERED"]),
    ("CM9", ["register_row", "datasetName"], None),
    ("CM9", ["register", "invitations"], lambda rows: rows[::-1]),          # oldest first
    ("CM10", ["relink", "old_status"], 200),                                 # the old link still opens
    ("CM10", ["relink", "answered_refusal"], {"status": 201, "body": {}}),
    ("CM11", ["credit_refusals", "names", "status"], 409),                   # the older gates' status
    ("CM11", ["credit_refusals", "emails", "ledger_rows_added"], 2),         # charged on a refusal
    ("CM11", ["credit_refusals", "names", "body", "remedy"], "Not enough credits."),
    ("CM12", ["format_refusal", "register_after"], 21),                      # a link was made anyway
    ("CM12", ["format_refusal", "commercial_link", "status"], 201),
    ("CM13", ["own_ai_refusal", "body", "code"], "NOT_B2B"),
]


@pytest.mark.parametrize("mark,path,value", SEEDED, ids=[f"{m}-{'.'.join(map(str, p))}" for m, p, _ in SEEDED])
def test_each_mark_fails_on_its_seeded_fault(mark, path, value):
    checks = _by_mark(_seed(path, value))
    assert checks[mark].measured and not checks[mark].ok, checks[mark].detail


def test_a_record_missing_a_key_is_unmeasured_not_passed():
    record = good()
    del record["relink"]
    assert not _by_mark(record)["CM10"].measured


def test_the_mail_pattern_does_not_mistake_an_email_field_for_a_mail_sender():
    assert not marks.MAIL_KEY.search("KEEL_FOUNDER_EMAIL")
    assert not marks.MAIL_KEY.search("KEEL_OIDC_EMAIL_CLAIM")
    for hit in ("KEEL_SMTP_HOST", "SPRING_MAIL_HOST", "mail", "postmark", "KEEL_SES_REGION", "mailhog"):
        assert marks.MAIL_KEY.search(hit), hit


# ------------------------------------------------------------------------------------------ the fake, restated

@pytest.fixture(scope="module")
def everyone():
    try:
        return fake.people(load_config(validate=False).keel_cloud)
    except fake.FakeUnavailable as missing:
        pytest.skip(str(missing))


def test_the_fake_holds_59_people_53_with_a_work_email(everyone):
    assert len(everyone) == 59 and sum(1 for p in everyone if p.email) == 53
    assert sum(1 for p in everyone if p.country == "GB") == 30
    assert all(p.email.endswith(".example") for p in everyone if p.email)


def test_the_uk_sizes_to_27_and_pages_in_fixture_order(everyone):
    uk = {"places": [{"kind": "COUNTRY", "code": "GB"}]}
    assert fake.size(everyone, uk) == 27
    first = fake.page(everyone, uk)
    assert len(first) == 25 and [p.source_id for p in first] == [p.source_id for p in fake.matching(everyone, uk)][:25]
    fetched = {p.source_id for p in first}
    second = fake.page(everyone, uk, fetched, after=first[-1].source_id)
    assert len(second) == 2 and not fetched & {p.source_id for p in second}
    assert fake.size(everyone, uk, fetched | {p.source_id for p in second}) == 0
    assert fake.size(everyone, {"places": [{"kind": "COUNTRY", "code": "US"}]}) == 26
    statuses = sorted(p.email_status for p in fake.matching(everyone, uk))
    assert statuses.count("VALID") == 24 and statuses.count("CATCH_ALL") == 2 and statuses.count("INVALID") == 1


def test_a_title_matches_on_every_word_and_a_place_on_its_kind(everyone):
    uk = [{"kind": "COUNTRY", "code": "GB"}]
    payroll = fake.size(everyone, {"titles": ["payroll manager"], "places": uk})
    assert payroll == sum(1 for p in everyone if p.country == "GB" and p.email and p.job_title
                          and {"payroll", "manager"} <= set(p.job_title.lower().split()))
    assert fake.size(everyone, {"titles": ["agency project manager"], "places": uk}) == 0
    region = fake.size(everyone, {"places": [{"kind": "REGION", "code": "GB-SCT"}]})
    assert region == sum(1 for p in everyone if p.region == "GB-SCT" and p.email)
    assert fake.size(everyone, {"places": []}) == 0                       # Q3: a search says where


# ------------------------------------------------------------------------------------------ the stand-ins

class _Remote:
    is_remote = True


@pytest.mark.parametrize("call", [lambda c: ledger.founder_account(c, "sub"),
                                  lambda c: ledger.stand_in_keels_door(c, str(uuid.uuid4()), "r"),
                                  lambda c: ledger.stand_in_balance(c, str(uuid.uuid4()), "r", to=20),
                                  lambda c: ledger.restore_own_door(c, str(uuid.uuid4()), "r")])
def test_the_ledger_is_never_reached_on_the_remote_profile(call):
    with pytest.raises(ledger.LedgerUnavailable, match="remote"):
        call(_Remote())


def test_no_value_is_spliced_into_the_ledgers_sql():
    import ast                                                            # noqa: PLC0415
    source = inspect.getsource(ledger)
    tree = ast.parse(source)
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "id", "") in ("_psql", "_json")]
    assert len(calls) >= 8
    for call in calls:
        sql = call.args[1]
        literal = isinstance(sql, ast.Constant) or (
            isinstance(sql, ast.BinOp) and all(isinstance(x, ast.Constant) for x in (sql.left, sql.right)))
        wrapped = isinstance(sql, ast.JoinedStr) and [v.value.id for v in sql.values
                                                     if isinstance(v, ast.FormattedValue)] == ["select"]
        assert literal or wrapped, ast.unparse(sql)
    assert source.count("UPDATE founder_account") == 2                    # the door, and its reversal
    with pytest.raises(ledger.LedgerUnavailable):
        ledger.rows(type("Local", (), {"is_remote": False})(), "1; DROP TABLE credit_ledger")


def test_keel_clouds_code_cannot_ask_a_source_for_a_phone():
    facts = contacts_leg.source_facts(load_config(validate=False).keel_cloud)
    if not facts["port_methods"]:
        pytest.skip("keel-cloud predates spec 092's ContactSource")
    assert "revealEmails" in facts["port_methods"] and facts["contact_types"] == [["email"]], facts
    assert "linkedinUrl" in facts["found_contact_fields"], facts
    assert not [x for x in facts["port_methods"] + facts["found_contact_fields"] if marks.PHONE_KEY.search(x)]


def test_the_leg_reverses_the_door_in_a_finally_and_never_asks_for_a_phone():
    body = inspect.getsource(contacts_leg.leg_contacts)
    assert "finally:" in body and "_restore(" in body.split("finally:")[1]
    import ast                                                            # noqa: PLC0415
    calls = [n for n in ast.walk(ast.parse(inspect.getsource(contacts_leg)))
             if isinstance(n, ast.Call) and getattr(n.func, "id", "") in ("wire", "_participant")]
    assert len(calls) > 20
    assert not [ast.unparse(c) for c in calls if "phone" in ast.unparse(c).lower()]
    assert "068" in contacts_leg.WEB_068_FOLLOW_UP and "Send more" in contacts_leg.WEB_068_FOLLOW_UP
