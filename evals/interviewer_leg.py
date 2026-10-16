"""The AI interviewer leg (spec 044; keel-cloud 094 at contract 16, `InferenceCharge` 9; keel-web 069): after S-006's
contacts leg the founder's project gets its interviewer -- Tito, recorded once by the stack's fake renderer -- and the
leg walks everything 094 and 069 say about it: the recording's one charge, the persona line through RECORDING to READY,
the links that wait for it (`INTERVIEWER_NOT_READY`) and the text link that never does, the spoken order of every
role's clips, the solution passage's three facts, the founder's word never spoken, *Try it yourself* writing nothing,
an AI-interviewer link's clips served with HTTP Range and answered with `heard` / `how`, a Let-them-choose link
answered in writing, the change of face for 400 credits, its refusal at a low balance, and the pilot ask -- the last
line of every role, its Yes counted where a text link's is. S-005 walks the short form: the recording, READY, one AI
link served.

**The founder's door is a stand-in** (judgement call 148): the journey's founder is on their own AI (the scripted
runtime built the project), and an account on its own AI records nothing -- `POST lock` writes no recording and its
receipt carries no `interviewer` (contract 16), `GET interviewer` and every AI link answer `INTERVIEWER_NEEDS_CREDITS`.
A Keel's-AI founder's lock on this stack would hand its RESPONDENT_QUESTIONS job to Keel's own Anthropic account, which
has no key here, so no lock on Keel's door ever reaches READY. So the leg asserts the own-AI refusals first, stands the
founder on Keel's door with a fresh grant (spec 043's stand-in, keyed `e2e-eval:044:`), and records the interviewer the
one way contract 16 gives a locked project with none -- `POST interviewer/face`, *"on a project locked before spec 094
(NOT_RECORDED) this is the first recording, gated and charged at the same price"* -- then puts the founder back on
their own door in a `finally`. On the remote profile only the own-AI refusals run.

**The scripts are on no route**: `ClipRef` carries an id, a URL and a length, so the spoken order, the solution passage
and the founder's word are read from the recording keel-cloud stored (`stack/ledger.recording`, a plain `SELECT` of
three paths of the project's document).

Every rule is scored by `evals/interviewer_marks.py` over the record this leg builds (`interviewer.json` and
`interviewer-marks.json` in the run bundle); the leg fails when an owed mark is unmet. No model runs, no vendor is
called and no money is spent anywhere here.
"""

from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path

import requests

from evals import interviewer_marks as marks
from harness import interviewer_fake as fake
from harness import interviewer_screens as ivs
from harness import interviews_screens as iv
from harness import vectors_script as vs
from stack import ledger as stack_ledger

SPEC = "044"
FIRST_FACE = "TITO"
CHANGED_FACE = "JUDY"
#: The balance the change is refused at (stand-in 2): under one change (400), over nothing else the leg needs.
LOW_BALANCE = 100
AI_PERSON = "Someone the founder knows, by voice"
CHOICE_PERSON = "Someone the founder knows, who picks"
TEXT_PERSON = "Someone the founder knows, in writing"
#: The founder's word the leg writes after the lock (call 149: no corpus founder writes one; `PUT word` is legal after
#: the lock) -- so the rule that it is never spoken has a word to hold. Composed here, never generated.
FOUNDERS_WORD = ("I started this because I spent years watching good people lose whole evenings to it, and I would "
                 "like to hear how it goes for you before I build anything.")

#: keel-web 069's page objects (`harness/interviewer_screens.py`), built in spec 044 once 069 merged at `d23895f`.
WEB_069_FOLLOW_UP = (
    "keel-web 069 (the AI interviewer's screens), DONE in spec 044: L1, W1 frame 2 (replayed), S1 / S2 / S3, the "
    "persona line's popup, Try it yourself and the respondent's stage and sheet through window.__keelSpeech -- each "
    "held to the wire this leg holds.")
READ_REASON = marks.READ_REASON
#: Spec 044 judgement call 3, widened (call 155): the B2C short form -- the recording, READY, its clips, one AI link
#: served with Range and answered on the stranger's own screen (the consumer link carries the cost total, so the field
#: is typed there), the pilot, the reading on arrival.
SHORT_FORM = ["IM1", "IM3", "IM4", "IM5", "IM6", "IM7", "IM9", "IM13"]


class _Wire:
    """The founder's calls on keel-cloud's routes, each kept for the record (IM2 sweeps the interviewer bodies)."""

    def __init__(self, j, record: dict):
        self.j = j
        self.record = record

    def __call__(self, method: str, suffix: str, body: dict | None = None, *, ok=(200, 201, 204)) -> tuple[int, dict]:
        path = suffix if suffix.startswith("/v2/") else self.j.project(suffix)
        status, payload = self.j.call(method, path, body, ok=ok)
        self.record["responses"].append({"method": method, "path": path, "status": status, "body": payload})
        # the founder's interviewer views (the persona line, the faces, a face change, a retry) -- not Try it
        # yourself's `Interview`, whose cost and price questions are the respondent's, not the recording's
        if re.search(r"/interviewer(/faces|/face|/retry)?$", path) and isinstance(payload, dict) and status < 300:
            self.record.setdefault("wire_views", []).append(payload)
        return status, payload if isinstance(payload, dict) else {}

    def me(self) -> dict:
        return self.j.get("/v2/me") or {}

    def credits(self) -> int | None:
        return self.me().get("creditsAvailable")

    def clip(self, url: str, range_: str | None = None) -> dict:
        """One clip on the founder's own route (the session's cookies), with or without a Range."""
        headers = {"Range": range_} if range_ else {}
        response = self.j.context.request.fetch(f"{self.j.cloud_base}{url}", method="GET", headers=headers,
                                                timeout=20_000)
        return _clip_facts(response.status, response.headers, len(response.body()) if response.status < 400 else 0)


def _clip_facts(status: int, headers, length: int) -> dict:
    h = {k.lower(): v for k, v in dict(headers).items()}
    return {"status": status, "content_range": h.get("content-range"), "accept_ranges": h.get("accept-ranges"),
            "content_type": h.get("content-type"), "cache_control": h.get("cache-control"), "length": length}


def _participant(j, method: str, token: str, suffix: str, body: dict | None = None, *,
                 headers: dict | None = None) -> requests.Response:
    """The stranger's side: no session at all, the token the credential."""
    return requests.request(method, f"{j.cloud_base}/v2/i/{token}{suffix}", json=body, headers=headers or {},
                            timeout=20)


def _stranger_clip(j, url: str, range_: str | None = None) -> dict:
    response = requests.get(f"{j.cloud_base}{url}", headers={"Range": range_} if range_ else {}, timeout=20)
    return _clip_facts(response.status_code, response.headers, len(response.content) if response.ok else 0)


def _json_of(response: requests.Response) -> dict:
    try:
        body = response.json()
    except ValueError:
        return {}
    return body if isinstance(body, dict) else {}


def _token(url: str) -> str:
    return url.rstrip("/").rsplit("/", 1)[-1]


def _rows(j, record: dict) -> int:
    return len(stack_ledger.rows(j.stack, record["founder_id"]))


def _persona(j) -> ivs.Persona:
    return ivs.Persona(j.page, j.recorder, j.web_base, patience=j.patience)


def _labels(j) -> dict[str, str]:
    """Each kind's card label on Sent, by link (`InvitationRow.kinds[]` / the register's kinds)."""
    register = j.get(j.project("/invitations")) or {}
    return {k.get("respondentType"): k.get("label") for k in register.get("kinds") or []}


# --------------------------------------------------------------------------------------------- the legs

def leg_interviewer(j) -> dict:
    """S-006 (05-paidly, B2B), after the contacts leg: the whole of spec 044 FR-002 (see the module docstring)."""
    return _leg(j, short=False)


def leg_interviewer_short(j) -> dict:
    """S-005 (01-countly, B2C): the short form (spec 044 judgement call 3, widened by call 155) -- the recording's one
    charge, READY, the spoken order and the solution passage on the one role, and one AI-interviewer link served with
    Range and answered on the stranger's own screen (the consumer link asks the cost total, typed into its field)."""
    return _leg(j, short=True)


def _leg(j, *, short: bool) -> dict:
    record: dict = {"entry": j.entry.id, "project_id": j.project_id, "short": short, "responses": [],
                    "wire_views": []}
    wire = _Wire(j, record)
    _own_ai(j, wire, record)
    if j.stack is None or j.stack.is_remote:
        with j.recorder.step("interviewer: the rest of the leg needs the local stack's database (the stand-in door, "
                             "the ledger and the stored recording) and is skipped on the remote profile",
                             party="stack", kind="note") as h:
            h.record_wire({"profile": getattr(j.stack, "profile", None)},
                          {"skipped": "Keel's door, the recording, the links, the change, the refusal"})
        return record
    account = stack_ledger.founder_account(j.stack, j.founder_identity.sub)
    record["founder_id"] = founder_id = account["id"]
    run = f"{j.project_id}:{int(time.time())}"
    since = stack_ledger.now(j.stack)
    try:
        _keels_door(j, wire, founder_id, run)
        _founders_word(j, wire, record)
        _first_recording(j, wire, record)
        if not short:
            _screens_recording(j, wire, record)
            _while_recording(j, wire, record)
        _ready(j, wire, record, FIRST_FACE, "the first recording")
        if not short:
            _screens_ready(j, wire, record)
        _the_recording(j, wire, record)
        if not short:
            _dry_run(j, wire, record)
        _ai_link(j, wire, record, answer=True)
        if not short:
            _choice_link(j, wire, record)
            _change_face(j, wire, record)
            _low_balance(j, wire, record, founder_id, run)
            _retry(j, wire, record)
        record["ledger"] = stack_ledger.rows(j.stack, founder_id, since=since)
        with j.recorder.step("interviewer: the ledger since Keel's door -- the stand-in grant, the recording's one "
                             "HOLD / SPEND pair, the change's, the stand-in low balance, the readings on arrival "
                             "(keel-cloud 095), and no other row",
                             party="stack", kind="assert") as h:
            reading_jobs = {x.get("inference_job_id") for x in record["ledger"]
                            if x.get("kind") == "HOLD" and x.get("action") in ("INTERPRET", "BRIEF")
                            and READ_REASON.match(x.get("reason") or "")}
            others = [x for x in record["ledger"] if x.get("action") not in fake.ACTIONS
                      and not (x.get("idempotency_key") or "").startswith(stack_ledger.key_prefix(SPEC))
                      and not (x.get("inference_job_id") and x.get("inference_job_id") in reading_jobs)]
            h.record_assert({"other rows": []}, {"rows": [(x["kind"], x.get("action"), x["credits"])
                                                          for x in record["ledger"]], "others": others})
            assert not others, others
    finally:
        _restore(j, wire, founder_id, run)
        if record.get("arrivals"):
            _read_what_is_left(j, wire, record)
    require = SHORT_FORM if short else [m for m, _, _ in marks.MARKS if m in _owed(record)]
    _score(j, record, require=require)
    return record


def _owed(record: dict) -> set[str]:
    """Every mark whose subject this record carries -- the screen marks join when 069's page objects draw them, and
    IM12 when the stack can seed the fake's fail-once (DRIFT #86)."""
    return {m for m, key, _ in marks.MARKS if key in record}


# ------------------------------------------------------------------------------------------- the steps

def _own_ai(j, wire: _Wire, record: dict) -> None:
    with j.recorder.step("interviewer (094 FR-F): on their own AI the founder's project has no recording -- the lock's "
                         "receipt carried no interviewer, GET interviewer and an AI-interviewer link are refused "
                         "INTERVIEWER_NEEDS_CREDITS, and nothing is made", party="founder", kind="assert") as h:
        me = wire.me()
        status, body = wire("GET", "/interviewer", ok=(422,))
        roles = _role_ids(j)
        before = len((wire("GET", "/invitations")[1]).get("invitations") or [])
        single, single_body = wire("POST", "/invitations", {
            "expectedRevision": j.revision(), "roleId": roles[vs.LINK_PRIMARY], "personName": AI_PERSON,
            "about": "the AI interviewer on an account on its own AI", "format": "AI_INTERVIEWER"}, ok=(422,))
        after = len((wire("GET", "/invitations")[1]).get("invitations") or [])
        record["own_ai"] = {"aiPath": me.get("aiPath"), "receipt": j.receipt, "status": status, "body": body,
                            "link": {"status": single, "body": single_body}, "register": [before, after]}
        h.record_assert({"aiPath": "OWN", "receipt.interviewer": None, "status": 422, "code": fake.NEEDS_CREDITS,
                         "link": fake.NEEDS_CREDITS, "made": 0}, record["own_ai"])
        assert me.get("aiPath") == "OWN" and "interviewer" not in (j.receipt or {}), record["own_ai"]
        assert body.get("code") == fake.NEEDS_CREDITS == single_body.get("code") and before == after, record["own_ai"]
    _drift_85(j, wire, record)


def _drift_85(j, wire: _Wire, record: dict) -> None:
    """runs/DRIFT.md #85, RESOLVED by keel-cloud 097 (call 21): on their own AI the founder's AI_INTERVIEWER link in a
    batch is refused 422 INTERVIEWER_NEEDS_CREDITS -- the door is asked first, as on the single-link routes -- and
    nothing is made (spec 046 FR-003; spec 044 stepped round its 409 INTERVIEWER_NOT_READY)."""
    with j.recorder.step("interviewer (keel-cloud 097, DRIFT #85 closed): on their own AI the founder's AI-interviewer "
                         "link in a BATCH is refused 422 INTERVIEWER_NEEDS_CREDITS, and nothing is made",
                         party="founder", kind="assert") as h:
        before = len((wire("GET", "/invitations")[1]).get("invitations") or [])
        status, body = wire("POST", "/invitations/batch", {
            "expectedRevision": j.revision(), "respondentType": vs.LINK_PRIMARY, "format": "AI_INTERVIEWER",
            "people": [{"personName": AI_PERSON}]}, ok=(409, 422))
        after = len((wire("GET", "/invitations")[1]).get("invitations") or [])
        record["own_ai"]["batch"] = {"status": status, "body": body}
        h.record_assert({"status": 422, "code": fake.NEEDS_CREDITS, "made": 0},
                        {"status": status, "code": body.get("code"), "made": after - before})
        assert before == after, (before, after)
        assert (status, body.get("code")) == (422, fake.NEEDS_CREDITS), body


def _keels_door(j, wire: _Wire, founder_id: str, run: str) -> None:
    with j.recorder.step("interviewer: STAND-IN (call 148) -- the founder on Keel's door with a fresh grant of 1,500 "
                         "(spec 043's stand-in, keyed e2e-eval:044:); a lock on Keel's door never reaches READY on a "
                         "stack with no Keel's-AI key", party="stack", kind="protocol") as h:
        added = stack_ledger.stand_in_keels_door(j.stack, founder_id, run, spec=SPEC)
        me = wire.me()
        h.record_wire({"stand-in": "ai_path KEEL + GRANT", "credits added": added},
                      {"aiPath": me.get("aiPath"), "creditsAvailable": me.get("creditsAvailable")})
        assert me.get("aiPath") == "KEEL" and me.get("creditsAvailable") == stack_ledger.GRANT_CREDITS, me


def _restore(j, wire: _Wire, founder_id: str, run: str) -> None:
    with j.recorder.step("interviewer: STAND-IN reversed -- the founder back on their own door with nothing to spend, "
                         "as every later journey on this founder expects", party="stack", kind="protocol") as h:
        taken = stack_ledger.restore_own_door(j.stack, founder_id, run, spec=SPEC)
        me = wire.me()
        h.record_wire({"closing row": taken}, {"aiPath": me.get("aiPath"),
                                               "creditsAvailable": me.get("creditsAvailable")})
        assert me.get("aiPath") == "OWN" and me.get("creditsAvailable") is None, me


def _founders_word(j, wire: _Wire, record: dict) -> None:
    with j.recorder.step("interviewer (call 149): the founder writes a word after the lock -- `PUT word`, legal after "
                         "the lock, the incentive and the pilot kept as stored -- so the word never spoken has a "
                         "subject; it is on the done screen as text", party="founder", kind="assert") as h:
        stored = (stack_ledger.recording(j.stack, j.project_id).get("word") or {})
        body = {"expectedRevision": j.revision(), "pitch": FOUNDERS_WORD, "incentive": stored.get("incentive")}
        if stored.get("pilotEnabled") is not None:
            body["pilotEnabled"] = stored.get("pilotEnabled")
        status, saved = wire("PUT", "/word", body)
        after = stack_ledger.recording(j.stack, j.project_id)
        record["word_written"] = {"status": status, "before": stored, "after": after.get("word")}
        h.record_assert({"pitch": FOUNDERS_WORD, "incentive": stored.get("incentive")}, record["word_written"])
        assert after.get("pitch") == FOUNDERS_WORD, record["word_written"]
        assert (after.get("word") or {}).get("incentive") == stored.get("incentive"), record["word_written"]


def _first_recording(j, wire: _Wire, record: dict) -> None:
    with j.recorder.step("interviewer (contract 16): on Keel's door the project locked with no recording reads "
                         "NOT_RECORDED; the five faces, Judy preselected, the change price 400; a face not on the list "
                         "is refused FACE_UNKNOWN and charges nothing", party="founder", kind="assert") as h:
        _, view = wire("GET", "/interviewer")
        _, faces = wire("GET", "/interviewer/faces")
        rows_before, balance_before = _rows(j, record), wire.credits()
        unknown, unknown_body = wire("POST", "/interviewer/face", {"face": "BOB"}, ok=(422,))
        record["faces"] = {"view": view, "faces": faces, "unknown": {"status": unknown, "body": unknown_body,
                                                                     "ledger_rows_added": _rows(j, record) - rows_before,
                                                                     "balance_after": wire.credits()}}
        h.record_assert({"status": "NOT_RECORDED", "face": None, "faces": list(fake.FACES),
                         "preselected": fake.PRESELECTED, "changePrice": fake.CHANGE_PRICE,
                         "unknown": fake.FACE_UNKNOWN}, record["faces"])
        assert view.get("status") == "NOT_RECORDED" and view.get("face") is None, view
        assert [f.get("code") for f in faces.get("faces") or []] == list(fake.FACES), faces
        assert [f.get("name") for f in faces.get("faces") or []] == [fake.FACE_NAMES[f] for f in fake.FACES], faces
        assert all(f.get("previewUrl") == fake.preview_path(f.get("code")) for f in faces.get("faces") or []), faces
        assert faces.get("preselected") == fake.PRESELECTED and faces.get("changePrice") == fake.CHANGE_PRICE, faces
        assert unknown_body.get("code") == fake.FACE_UNKNOWN, unknown_body
        assert record["faces"]["unknown"]["ledger_rows_added"] == 0 and wire.credits() == balance_before

    with j.recorder.step(f"interviewer: the founder picks {fake.FACE_NAMES[FIRST_FACE]} -- the first recording "
                         "starts RECORDING at once (0 of N until the clips are composed), one charge, nothing shown",
                         party="founder", kind="assert") as h:
        balance_before = wire.credits()
        persona = _persona(j)
        persona.sent(j.project_id)
        before = persona.wait_state("NOT_RECORDED")
        pressed = persona.record(FIRST_FACE)
        status, view = pressed["status"], pressed["body"]
        record["first"] = {"status": status, "view": view, "balance_before": balance_before,
                           "balance_after": wire.credits(), "at": stack_ledger.now(j.stack), "line": before,
                           "popup": pressed["popup"], "sent": pressed["sent"]}
        record["wire_views"].append(view)
        h.record_assert({"status": 200, "face": FIRST_FACE, "recording": "RECORDING or READY",
                         "balance": balance_before - fake.CREDITS,
                         "line": {"state": "NOT_RECORDED", "text": ivs.PERSONA_NOT_RECORDED,
                                  "action": ivs.pick_who_asks(fake.CREDITS)},
                         "popup": {"title": ivs.RECORD_FACE_TITLE, "faces": list(fake.FACES),
                                   "confirm": f"Record {fake.FACE_NAMES[FIRST_FACE]}"},
                         "sent": {"face": FIRST_FACE}}, record["first"])
        assert before.get("state") == "NOT_RECORDED" and ivs.PERSONA_NOT_RECORDED in before.get("text", ""), before
        assert before.get("action") == ivs.pick_who_asks(fake.CREDITS), before
        assert pressed["popup"]["title"] == ivs.RECORD_FACE_TITLE, pressed["popup"]
        assert pressed["popup"]["faces"] == list(fake.FACES), pressed["popup"]
        assert pressed["popup"]["confirm"] == f"Record {fake.FACE_NAMES[FIRST_FACE]}", pressed["popup"]
        assert pressed["sent"] == {"face": FIRST_FACE} and status == 200, pressed
        assert (view.get("face") or {}).get("code") == FIRST_FACE, view
        assert view.get("status") in ("RECORDING", "READY"), view
        assert record["first"]["balance_after"] == balance_before - fake.CREDITS, record["first"]


def _while_recording(j, wire: _Wire, record: dict) -> None:
    """Decision 7: while recording, text links work at once; AI-interviewer and Let-them-choose links wait, and so does
    Try it yourself; a change of face waits for this recording to finish."""
    with j.recorder.step("interviewer (decision 7): while RECORDING the AI interviewer and Let them choose are refused "
                         "409 INTERVIEWER_NOT_READY on the batch and the single link, Try it yourself too, a change of "
                         "face 409 INTERVIEWER_FAILED -- and a text link is made at once", party="founder",
                         kind="assert") as h:
        _, view = wire("GET", "/interviewer")
        if view.get("status") != "RECORDING":
            h.record_wire({"note": "the fake finished before the first read"}, view)
            record["while_recording"] = {"skipped": view.get("status")}
            return
        roles = _role_ids(j)
        refusals = {}
        for fmt in ("AI_INTERVIEWER", "CHOICE"):
            status, body = wire("POST", "/invitations/batch", {
                "expectedRevision": j.revision(), "respondentType": vs.LINK_PRIMARY, "format": fmt,
                "people": [{"personName": AI_PERSON}]}, ok=(409, 201))
            refusals[fmt] = {"status": status, "code": body.get("code")}
        if vs.is_b2b(j.entry):
            status, body = wire("POST", "/commercial-link", {"expectedRevision": j.revision(),
                                                             "personName": AI_PERSON, "format": "AI_INTERVIEWER"},
                                ok=(409, 201))
            refusals["commercial-link"] = {"status": status, "code": body.get("code")}
        tried, tried_body = wire("GET", f"/interviewer/try/{roles[vs.LINK_PRIMARY]}", ok=(409, 200))
        changed, changed_body = wire("POST", "/interviewer/face", {"face": CHANGED_FACE}, ok=(409, 200))
        text, text_body = wire("POST", "/invitations/batch", {
            "expectedRevision": j.revision(), "respondentType": vs.LINK_PRIMARY, "format": "TEXT",
            "people": [{"personName": TEXT_PERSON}]})
        _, after = wire("GET", "/interviewer")
        record["while_recording"] = {"view": view, "refusals": refusals,
                                     "try": {"status": tried, "code": tried_body.get("code")},
                                     "change": {"status": changed, "code": changed_body.get("code")},
                                     "text": {"status": text, "format": text_body.get("format"),
                                              "links": len(text_body.get("links") or [])},
                                     "still": after.get("status")}
        h.record_assert({"refusals": {k: {"status": 409, "code": fake.NOT_READY} for k in refusals},
                         "try": {"status": 409, "code": fake.NOT_READY},
                         "change": {"status": 409, "code": fake.IN_FLIGHT}, "text": {"status": 201, "links": 1},
                         "progress": "k of N"}, record["while_recording"])
        if after.get("status") != "RECORDING":
            return                                       # READY landed mid-step; what was refused was refused in time
        assert all(r == {"status": 409, "code": fake.NOT_READY} for r in refusals.values()), refusals
        assert (tried, tried_body.get("code")) == (409, fake.NOT_READY), tried_body
        assert (changed, changed_body.get("code")) == (409, fake.IN_FLIGHT), changed_body
        assert text == 201 and text_body.get("format") == "TEXT" and len(text_body.get("links") or []) == 1, text_body
        progress = view.get("progress") or {}
        assert 0 <= int(progress.get("done", -1)) <= int(progress.get("total", -1)), view


def _screens_recording(j, wire: _Wire, record: dict) -> None:
    """S1 (keel-web 069 FR-004 / FR-005 / FR-006): while the clips record, Sent's persona line names the face, says it
    is recording with a bar and *k of N clips done*; each card's *Try it yourself* is greyed *recording*; the primary
    reads *Send text-only links*; Send more greys the AI interviewer and Let them choose *recording*. No price."""
    persona = _persona(j)
    with j.recorder.step("interviewer (S1): while RECORDING the persona line names Tito, recording, a bar and k of N "
                         "clips; Try it yourself greyed *recording*; *Send text-only links*; Send more greys the AI "
                         "interviewer and Let them choose *recording*", party="founder", kind="assert") as h:
        line = persona.wait_state("RECORDING")
        cards = persona.cards()
        labels = _labels(j)
        formats = persona.formats_now(labels[vs.LINK_PRIMARY])
        record.setdefault("screens", {})["S1"] = line["text"]
        record["screens_drawn"] = {"S1": {"line": line, "cards": cards, "formats": formats}}
        name = fake.FACE_NAMES[FIRST_FACE]
        h.record_assert({"line": f"{ivs.persona_asks(name)} {ivs.PERSONA_RECORDING}", "try": ivs.TRY_IT_YOURSELF_RECORDING,
                         "primary": ivs.SEND_TEXT_ONLY_LINKS, "greyed": iv.FORMAT_RECORDING,
                         "hint": ivs.SEND_FORMAT_RECORDING}, record["screens_drawn"]["S1"])
        if line.get("state") != "RECORDING":
            return                                         # READY landed while the screen was read
        assert ivs.persona_asks(name) in line["text"] and ivs.PERSONA_RECORDING in line["text"], line
        assert line.get("bar") is not None, line
        assert all(c["try"] and not c["try"]["enabled"] and c["try"]["text"] == ivs.TRY_IT_YOURSELF_RECORDING
                   for c in cards), cards
        assert all(c["primary"] == ivs.SEND_TEXT_ONLY_LINKS for c in cards), cards
        rows = formats["rows"]
        assert rows.get(iv.TEXT_ONLY, {}).get("disabled") is False, rows
        assert all(r["disabled"] and r["word"] == iv.FORMAT_RECORDING for n, r in rows.items() if n != iv.TEXT_ONLY), rows


def _screens_ready(j, wire: _Wire, record: dict) -> None:
    """S2, S3, W1 and L1 once READY: the line *Recorded today at hh:mm.* with the one priced action, *Try it yourself*
    lit and *Send links*; Send more offers *AI interviewer · Tito*; W1 replayed names Tito in frame 2; L1 revisited
    draws the carousel with Tito checked. None of them shows a price but the one action (IM2)."""
    persona = _persona(j)
    name = fake.FACE_NAMES[FIRST_FACE]
    with j.recorder.step("interviewer (S2 / S3): READY in place -- *Recorded today at hh:mm.* and *Change who asks · "
                         "400 AI credits*; Try it yourself lit, *Send links*; Send more offers *AI interviewer · Tito* "
                         "and says it is already recorded", party="founder", kind="assert") as h:
        persona.sent(j.project_id)
        line = persona.wait_state("READY")
        cards = persona.cards()
        formats = persona.formats_now(_labels(j)[vs.LINK_PRIMARY])
        record["screens"]["S2"] = line["text"]
        record["screens"]["S3"] = formats["text"]
        record["screens_drawn"]["S2"] = {"line": line, "cards": cards}
        record["screens_drawn"]["S3"] = formats
        h.record_assert({"line": "Recorded today at", "action": ivs.change_who_asks(fake.CREDITS),
                         "try": ivs.TRY_IT_YOURSELF, "primary": ivs.SEND_LINKS,
                         "formats": [iv.ai_format_name(name), iv.TEXT_ONLY, iv.CHOICE_NAME],
                         "hint": ivs.SEND_FORMAT_RECORDED}, {"S2": record["screens_drawn"]["S2"], "S3": formats})
        assert "Recorded today at" in line["text"] and line.get("action") == ivs.change_who_asks(fake.CREDITS), line
        assert all(c["try"] and c["try"]["enabled"] and c["try"]["text"] == ivs.TRY_IT_YOURSELF for c in cards), cards
        assert all(c["primary"] == ivs.SEND_LINKS for c in cards), cards
        assert list(formats["rows"]) == [iv.ai_format_name(name), iv.TEXT_ONLY, iv.CHOICE_NAME], formats["rows"]
        assert not any(r["disabled"] for r in formats["rows"].values()), formats["rows"]
        assert formats["hint"] == ivs.SEND_FORMAT_RECORDED, formats
    with j.recorder.step("interviewer (W1, FR-003): *How it works* replays the walkthrough's four frames, frame 2 "
                         "*Tito asks your questions*", party="founder", kind="assert") as h:
        drawn = persona.walkthrough_again()
        record["screens_drawn"]["W1"] = drawn
        h.record_assert({"frames": 4, "frame 2": ivs.walkthrough_asks_title(name)}, drawn)
        assert len(drawn["texts"]) == 4 and ivs.walkthrough_asks_title(name) in drawn["texts"][1], drawn
    with j.recorder.step("interviewer (L1, FR-002): the lock's last screen revisited on Keel's door -- *Who asks the "
                         "questions*, the five faces, one checked -- and no price on it", party="founder",
                         kind="assert") as h:
        l1 = persona.l1_again(j.project_id)
        record["screens"]["L1"] = l1["text"]
        record["screens_drawn"]["L1"] = l1
        h.record_assert({"faces": list(fake.FACES), "checked": 1, "price words": []},
                        {**l1, "price words": marks.PRICE_WORD.findall(l1["text"])})
        assert l1["faces"] == list(fake.FACES) and len(l1["checked"]) == 1, l1
        assert not marks.PRICE_WORD.search(l1["text"]), l1["text"]
    with j.recorder.step("interviewer: DRIFT #87 -- L1 revisited after the lock checks Judy, the preselected face, "
                         "while Tito asks every question (stepped round: the face asking is held on the persona line "
                         "and the wire)", party="founder", kind="note") as h:
        h.record_wire({"recorded": FIRST_FACE}, {"checked on L1": l1["checked"],
                                                 "DRIFT #87": l1["checked"] != [FIRST_FACE]})
        record["screens_drawn"]["L1"]["drift_87"] = l1["checked"] != [FIRST_FACE]
    persona.sent(j.project_id)


def _ready(j, wire: _Wire, record: dict, face: str, what: str) -> dict:
    """The fake completes: the persona line's read reaches READY within spec 044's 30 s (judgement call 2)."""
    with j.recorder.step(f"interviewer: {what} reaches READY within {fake.READY_WITHIN_S} s on the fake renderer "
                         f"({fake.FAKE_DELAY_S} s a clip, polled every {fake.POLL_S} s) -- every clip done, readyAt "
                         f"stamped, {fake.FACE_NAMES[face]} asks", party="stack", kind="assert") as h:
        started = time.monotonic()
        trail: list[str] = []
        view: dict = {}
        while time.monotonic() - started < fake.READY_WITHIN_S * j.patience:
            view = j.get(j.project("/interviewer")) or {}
            if not trail or trail[-1] != view.get("status"):
                trail.append(view.get("status"))
            if view.get("status") in ("READY", "FAILED"):
                break
            time.sleep(1)
        took = round(time.monotonic() - started, 1)
        record.setdefault("ready", []).append({"what": what, "face": face, "trail": trail, "view": view,
                                               "seconds": took})
        record["wire_views"].append(view)
        progress = view.get("progress") or {}
        h.record_assert({"status": "READY", "face": face, "done": "total", "within_s": fake.READY_WITHIN_S},
                        {"trail": trail, "view": view, "seconds": took})
        assert view.get("status") == "READY", (trail, view)
        assert (view.get("face") or {}).get("code") == face and view.get("readyAt"), view
        assert progress.get("total") and progress.get("done") == progress.get("total"), view
        assert view.get("failure") is None and view.get("changePrice") == fake.CHANGE_PRICE, view
        return {"trail": trail, "view": view}


def _role_ids(j) -> dict[str, str]:
    persona = j.get(j.project("/persona")) or {}
    out = {}
    for t in persona.get("respondentTypes") or []:
        out[vs.LINK_B2B if t.get("commercialLink") else vs.LINK_PRIMARY] = t.get("roleId")
    return out


def _served_parts(interview: dict) -> list[dict]:
    """The parts a role's link serves and their items in order -- the gate first in part 1 (094 `PassageComposer`)."""
    parts = []
    for part in interview.get("parts") or []:
        items = [i.get("dimension") for i in part.get("items") or []]
        if int(part.get("part")) == 1 and interview.get("gate"):
            items = [interview["gate"].get("dimension")] + items
        parts.append({"part": int(part.get("part")), "items": items})
    return parts


def _the_recording(j, wire: _Wire, record: dict) -> None:
    """What keel-cloud stored, held to what each role's link serves (the dry run's Interview is a link's, 094 FR-G)."""
    with j.recorder.step("interviewer (094 FR-B): every role's clips in the spoken order, as its link is served; the "
                         "solution passage reads the idea's three lines; the founder's word is spoken nowhere; the "
                         "pilot ask last; each clip the fake's one-second file at 0.1 s a word", party="stack",
                         kind="assert") as h:
        stored = stack_ledger.recording(j.stack, j.project_id)
        rec = stored.get("recording") or {}
        record["recording"] = rec
        record["schema_version"] = stored.get("schema_version")
        _, idea = wire("GET", "/idea")
        record["idea"] = {"name": idea.get("shortName") or idea.get("what"), "what": idea.get("what"),
                          "how": idea.get("how"), "belief": idea.get("belief")}
        record["word"] = stored.get("pitch") or ""
        roles = {}
        tries = {}
        for link, role_id in _role_ids(j).items():
            _, served = wire("GET", f"/interviewer/try/{role_id}")
            tries[link] = served
            roles[link] = {"kind": served.get("kind"), "parts": _served_parts(served), "roleId": role_id}
        record["roles"] = roles
        record["tries"] = {k: {"tryRun": v.get("tryRun"), "formats": v.get("formats"),
                               "clips": sorted(((v.get("interviewer") or {}).get("clips") or {}).keys())}
                           for k, v in tries.items()}
        record["pilot"] = {"served": {f"try {k}": bool(((v.get("interviewer") or {}).get("clips") or {}).get("pilot"))
                                      for k, v in tries.items()}}
        clip_bytes = fake.fake_clip_bytes(j.stack.keel_cloud)
        off = [c for c in rec.get("clips") or [] if c.get("status") != "DONE"
               or (clip_bytes is not None and c.get("bytes") != clip_bytes)
               or c.get("durationSeconds") != fake.fake_seconds(c.get("script"))]
        h.record_assert({"face": FIRST_FACE, "status": "READY", "roles": sorted(roles), "off the fake": []},
                        {"face": rec.get("face"), "status": rec.get("status"), "roles": roles,
                         "clips": [(c.get("role"), c.get("kind"), c.get("itemId")) for c in rec.get("clips") or []],
                         "off the fake": off, "schema_version": stored.get("schema_version")})
        assert rec.get("face") == FIRST_FACE and rec.get("status") == "READY", rec.get("status")
        assert int(stored.get("schema_version") or 0) >= 22, stored.get("schema_version")   # 23 since keel-cloud 096
        assert not off, off


def _counts(j, wire: _Wire, record: dict) -> dict:
    invitations = (wire("GET", "/invitations")[1]).get("invitations") or []
    standings = j.get(j.project("/standings")) or {}
    return {"invitations": len(invitations), "answered": sum(1 for i in invitations if i.get("status") == "ANSWERED"),
            "pilot": (standings.get("pilot") or {}).get("optedIn"), "ledger": _rows(j, record)}


def _dry_run(j, wire: _Wire, record: dict) -> None:
    """Decision 6: Try it yourself, per role -- the same Interview with clips, on the founder's route; stores nothing."""
    with j.recorder.step("interviewer (decision 6): Try it yourself serves each role's whole interview with its clips "
                         "and `tryRun`, its clips on the founder's own route (206 to a Range), and writes nothing -- "
                         "no invitation, no response, no pilot, no ledger row", party="founder", kind="assert") as h:
        before = _counts(j, wire, record)
        roles = _role_ids(j)
        _, served = wire("GET", f"/interviewer/try/{roles[vs.LINK_PRIMARY]}")
        player = served.get("interviewer") or {}
        opening = (player.get("clips") or {}).get("opening") or {}
        founder_clip = wire.clip(opening.get("url") or "", "bytes=0-99")
        drawn = _dry_run_on_screen(j)
        after = _counts(j, wire, record)
        clips = len([c for c in (player.get("clips") or {}).values() if c]) + sum(
            1 + (1 if v.get("more") else 0) for v in (player.get("items") or {}).values())
        record["dry_run"] = {"tryRun": served.get("tryRun"), "clips": clips, "before": before, "after": after,
                             "writes": drawn["writes"], "founder_clip": founder_clip, "opening_url": opening.get("url"),
                             "mark": player.get("mark"), "screen": drawn}
        h.record_assert({"tryRun": True, "mark": fake.MARK, "url": f"/v2/projects/{j.project_id}/interviewer/clips/",
                         "clip": 206, "before == after": True}, record["dry_run"])
        assert served.get("tryRun") is True and player.get("mark") == fake.MARK, served.get("tryRun")
        assert (opening.get("url") or "").startswith(f"/v2/projects/{j.project_id}/interviewer/clips/"), opening
        assert founder_clip["status"] == 206, founder_clip
        assert before == after, (before, after)
        assert drawn["mark"] == ivs.MARK_TRY and drawn["done"]["tryRun"], drawn
        assert ivs.TRY_NOTHING_STORED in drawn["done"]["text"] and not drawn["writes"], drawn
        assert drawn["first"]["question"] and drawn["videos"] == 1, drawn


def _dry_run_on_screen(j) -> dict:
    """keel-web 069 FR-007 on the founder's own page: *Try it yourself* on the specialists' card, *Start talking* (the
    opening plays on the one `<video>`), the first question answered aloud through the seam, End -- the dry run stops
    there -- *Nothing was stored.*, and the page wrote nothing."""
    j.context.add_init_script(ivs.SPEECH_SEAM)
    persona = _persona(j)
    persona.sent(j.project_id)
    persona.try_it(j.project_id, _labels(j)[vs.LINK_PRIMARY])
    # the button navigates inside the app; the seam's init script runs on a document's load, so the dry run's own
    # route is loaded once more (same URL) before anything is said
    j.page.reload(wait_until="load")
    player = ivs.Player(j.page, j.recorder, party="founder", patience=j.patience)
    try:
        with player.step("founder tries the interview: Start talking, one answer aloud, End") as h:
            try:
                j.page.get_by_test_id("start-talking").wait_for(state="visible", timeout=30_000)
                player.requests.clear()
                player.start()
                player.wait_phase("listening")
                stage = player.stage()
                first = player.sheet()
                player.say("yes", True)
                player.answer()
                where = player.stage()["where"]
                player.end()                                   # the dry run stops at End (069 FR-007)
                done = player.done()
            except Exception:
                h.add_screenshot(player.screenshot("try-stuck"))
                h.record_wire({"stuck": True}, player.where_it_stood())
                raise
            h.add_screenshot(player.screenshot("try-done"))
            writes = [r for r in player.requests if r["method"] != "GET"]
            return {"mark": stage["mark"], "first": first, "pilot_where": where, "done": done, "writes": writes,
                    "videos": stage["videos"]}
    finally:
        j.page.remove_listener("request", player._keep)


def _send_link(j, fmt: str, person: str) -> dict:
    """A link made on Sent's *Send more* (keel-web 069 S3): the format picked, *Someone I know*, the name, *Make their
    link* -- the batch keel-web received and the link it drew."""
    persona = _persona(j)
    primary = next(t for t in (j.get(j.project("/persona")) or {}).get("respondentTypes") or []
                   if not t.get("commercialLink"))
    sent = iv.Interviews(j.page, j.recorder, j.web_base, patience=j.patience)
    about = f"{primary.get('label')}, asked about one real time."
    persona.sent(j.project_id)
    made = sent.send_someone(j.project_id, _labels(j)[vs.LINK_PRIMARY], person, about, fmt=fmt)
    if made["status"] == 409 and (made["batch"] or {}).get("rule") == "concurrency":
        with j.recorder.step("interviewer: DRIFT #88 -- Send more sent the revision Sent read when it opened; an "
                             "answer read on arrival (keel-cloud 095) moved the project since, and the link was "
                             "refused 409 with the server's own words in the popup; Sent is opened again and the "
                             "link made once more", party="founder", kind="note") as h:
            h.record_wire({"sent": made.get("sent")}, {"status": made["status"], "body": made["batch"],
                                                       "drawn": made.get("drawn")})
        j.page.goto(f"{j.web_base}/p/{j.project_id}/interviews/sent", wait_until="load")
        persona.sent(j.project_id)
        made = sent.send_someone(j.project_id, _labels(j)[vs.LINK_PRIMARY], person, about, fmt=fmt)
    batch = made["batch"] or {}
    link = (batch.get("links") or [{}])[0]
    assert made["status"] == 201 and made["url"] == link.get("url"), made
    return {"format": batch.get("format"), "url": link.get("url"), "invitationId": link.get("invitationId"),
            "token": _token(link.get("url") or ""), "formats": made["formats"], "by": "keel-web"}


def _ai_link(j, wire: _Wire, record: dict, *, answer: bool) -> None:
    """Decision 5 and FR-H: an AI-interviewer link's interview carries the player -- every clip on the link's own route,
    206 to a Range, 404 for a clip that is not this link's -- and its answers go back with `heard` / `how`."""
    with j.recorder.step("interviewer (FR-H): an AI-interviewer link is made once READY; the stranger's interview "
                         "carries `interviewer` (the face, the mark, every clip in order) and `formats` "
                         "[AI_INTERVIEWER]; its clips answer 206 to a Range, 200 whole, 404 for another role's clip",
                         party="participant", kind="assert") as h:
        made = _send_link(j, "AI_INTERVIEWER", AI_PERSON)
        response = _participant(j, "GET", made["token"], "/interview")
        interview = _json_of(response)
        player = interview.get("interviewer") or {}
        clips = player.get("clips") or {}
        opening = clips.get("opening") or {}
        part = _stranger_clip(j, opening.get("url") or "", "bytes=0-99")
        whole = _stranger_clip(j, opening.get("url") or "")
        own = {c.get("clipId") for c in clips.values() if c} | {
            r.get("clipId") for v in (player.get("items") or {}).values() for r in (v.get("clip"), v.get("more")) if r}
        others = [c for c in (record.get("recording") or {}).get("clips") or []
                  if c.get("role") != vs.LINK_PRIMARY and c.get("id") not in own]
        foreign_id = others[0]["id"] if others else str(uuid.uuid4())
        foreign = _stranger_clip(j, f"/v2/i/{made['token']}/interview/clips/{foreign_id}", "bytes=0-99")
        record["ai_link"] = {"made": made, "status": response.status_code, "formats": interview.get("formats"),
                             "face": player.get("face"), "mark": player.get("mark"), "clips": sorted(clips),
                             "items": len(player.get("items") or {}), "own clips": len(own)}
        record["range"] = {"part": part, "whole": whole,
                           "foreign": {**foreign, "what": "another role's clip" if others else "an unknown id"}}
        record["pilot"] = {**record.get("pilot", {}),
                           "served": {**(record.get("pilot") or {}).get("served", {}), "ai link": bool(clips.get("pilot"))}}
        h.record_assert({"format": "AI_INTERVIEWER", "formats": ["AI_INTERVIEWER"], "face": FIRST_FACE,
                         "mark": fake.MARK, "range": {"part": 206, "whole": 200, "foreign": 404}},
                        {"link": record["ai_link"], "range": record["range"]})
        assert made["format"] == "AI_INTERVIEWER" and response.status_code == 200, record["ai_link"]
        assert interview.get("formats") == ["AI_INTERVIEWER"], interview.get("formats")
        assert (player.get("face") or {}).get("code") == FIRST_FACE and player.get("mark") == fake.MARK, player
        assert all((c.get("url") or "").startswith(f"/v2/i/{made['token']}/interview/clips/")
                   for c in clips.values() if c), clips
        assert part["status"] == 206 and whole["status"] == 200 and foreign["status"] == 404, record["range"]
    j.tokens["interviewer:ai"] = made["token"]
    if answer:
        _answer_ai_on_screen(j, wire, record, made, interview)


def _person_for_the_link(j):
    """The **last** corpus person keel-cloud reads (a gate yes with a story) -- composed, never generated (spec 043
    call 133's rule). The last, because the two answers this leg makes are read on arrival on Keel's door, which has no
    key on this stack, so they stay unread; the leg reads them on the founder's own door before it ends (call 152),
    and the scripted executor repeats its last INTERPRET entry once its readings are spent -- this person's own."""
    names = {p.person for p in vs.readable_people(j.entry)}
    return [p for p in j.people if p.person in names][-1]


ORDINALS = ["the first one", "the second one", "the third one", "the fourth one", "the fifth one", "the sixth one"]
NUMBER_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]


def _closed(answer: dict) -> dict:
    """An answer's closed fields, order taken out -- what the person answered, not how."""
    a = {k: v for k, v in answer.items() if k not in ("heard", "how", "itemId")}
    for key in ("optionIds", "advantageIds"):
        if key in a:
            a[key] = sorted(a[key])
    if a.get("costTotal") and a["costTotal"].get("value") is not None:
        a["costTotal"] = {**a["costTotal"], "value": round(float(a["costTotal"]["value"]), 4)}
    return a


def _drive_ai(player, interview: dict, expected: dict) -> list[dict]:
    """The stranger answers every question the way the corpus person did, as a person would on the stage: the gate
    said aloud, the story typed, one ordinal, one miss ("31" -- out of every range here -- then the number in words,
    after the didn't-catch clip), a pick-two tapped, "all of them" for the advantages when they are all the person's,
    the rest said by their options' own words (or a cost total typed into the field), the escape tapped; then the pilot
    ask -- *Last question* -- Yes, *Finish*. Returns what each sheet drew and what was done on it."""
    gate = interview.get("gate") or {}
    items = {i.get("question"): i for part in interview.get("parts") or [] for i in part.get("items") or []}
    by_prompt = {i.get("advantagesPrompt"): i for i in items.values() if i.get("advantagesPrompt")}
    by_id = {a["itemId"]: a for a in expected.get("answers") or []}
    walked: list[dict] = []
    used = {"ordinal": False, "miss": False}
    for _ in range(40):
        player.wait_phase("listening", timeout_s=40)
        stage, sheet = player.stage(), player.sheet()
        entry = {"where": stage["where"], "question": sheet["question"], "options": [o["label"] for o in sheet["options"]],
                 "mark": stage["mark"], "did": []}
        walked.append(entry)
        q = sheet["question"]
        if stage["where"] == ivs.LAST_QUESTION:
            player.tap("Yes")
            entry["did"].append("tap Yes")
            player.next()
            return walked
        if gate and q == gate.get("question"):
            player.say("yes, I did", True)
            player.answer()
            entry["did"].append("said yes, I did")
            player.next()
            continue
        after_gate = len(walked) > 1 and walked[-2]["question"] == gate.get("question")
        if gate and after_gate and q not in items and q not in by_prompt:      # the story, after Yes
            if expected.get("anchorChip"):
                player.tap_chip()
                entry["did"].append("tap the story's chip")
            else:
                player.type_instead(expected.get("story") or "")
                player.answer()
                entry["did"].append("typed the story")
            player.next()
            continue
        if q in by_prompt:                                          # the advantages, after "better"
            item = by_prompt[q]
            want = by_id[item["itemId"]].get("advantageIds") or []
            labels = {a["id"]: a["label"] for a in item.get("advantages") or []}
            if want and sorted(want) == sorted(labels):
                player.say("all of them", True)
                player.answer()
                entry["did"].append("said all of them")
            else:
                for a in want:
                    player.tap(labels[a])
                    entry["did"].append(f"tap {labels[a]}")
            player.next()
            continue
        item = items.get(q)
        assert item, {"an unknown question on the sheet": q, "served": sorted(items)}
        ans = by_id.get(item["itemId"]) or {}
        options = {o["optionId"]: o["label"] for o in item.get("options") or []}
        control = item.get("control")
        if ans.get("chip"):
            player.tap_chip()
            entry["did"].append("tap the escape")
        elif control == "pick_two":
            for o in ans.get("optionIds") or []:
                player.tap(options[o])
                entry["did"].append(f"tap {options[o]}")
        elif ans.get("scale") is not None or ans.get("number") is not None:
            value = ans.get("scale") if ans.get("scale") is not None else ans.get("number")
            if not used["miss"]:
                player.say("31", True)
                player.answer()
                player.wait_phase("listening", timeout_s=20)        # the didn't-catch clip, then the window again
                entry["missed"] = player.sheet()["preview"] or player.sheet()["status"]
                entry["did"].append("said 31 (a miss)")
                used["miss"] = True
            words = NUMBER_WORDS[int(value)] if str(value).isdigit() and int(value) < len(NUMBER_WORDS) else str(value)
            player.say(words, True)
            player.answer()
            entry["did"].append(f"said {words}")
        elif ans.get("costTotal"):
            cost = ans["costTotal"]
            player.unit("HOURS" if cost.get("mode") == "HOURS" else "AMOUNT")
            player.fill_field(str(cost.get("value")))
            player.answer()
            entry["did"].append(f"typed {cost.get('value')} into the field")
            entry["typed"] = {"itemId": item["itemId"], "value": str(cost.get("value"))}
        else:
            labels = [options[o] for o in ans.get("optionIds") or []]
            assert len(labels) == 1, {"item": item["dimension"], "answer": ans}
            index = [o["label"] for o in sheet["options"]].index(labels[0])
            if not used["ordinal"] and index < len(ORDINALS):
                said = ORDINALS[index]
                used["ordinal"] = True
            else:
                said = labels[0]
            player.say(said, True)
            player.answer()
            entry["did"].append(f"said {said}")
        player.next()
    raise AssertionError({"the interview never reached its pilot ask": walked[-3:]})


def _answer_ai_on_screen(j, wire: _Wire, record: dict, made: dict, interview: dict) -> None:
    """keel-web 069 FR-008 on the stranger's own page, through the speech seam (`vite --mode test`): the intro (who
    asks, an AI, Start talking), then every question as `_drive_ai` answers it; the one `POST response` keel-web sends
    -- `format` AI_INTERVIEWER, `heard` / `how` on every answer, the person's own closed answers -- then the pilot
    ask's Yes, the same write a text link's is, counted in the overview's pilot."""
    person = _person_for_the_link(j)
    items = {i.get("dimension"): i for part in interview.get("parts") or [] for i in part.get("items") or []}
    recall = ((items.get("commercial.existing_sacrifice") or {}).get("costTotal") or {}).get("recallPeriod")
    expected = person.response(made["token"], recall)
    pilot_before = (j.get(j.project("/standings")) or {}).get("pilot") or {}
    stranger = j.browser.new_context()
    stranger.add_init_script(ivs.SPEECH_SEAM)
    seen: dict = {}

    def keep(response) -> None:
        if response.request.method == "POST" and response.url.endswith(("/interview/response", "/interview/pilot")):
            seen.setdefault(response.url.rsplit("/", 1)[-1], []).append(
                {"status": response.status, "body": response.request.post_data_json})
    try:
        page = stranger.new_page()
        page.on("response", keep)
        player = ivs.Player(page, j.recorder, patience=j.patience)
        with player.step("the stranger answers the AI interviewer: the intro, Start talking, every question by voice, "
                         "tap or typing, the pilot ask, Finish") as h:
            try:
                intro = player.open(made["url"])
                player.start()
                walked = _drive_ai(player, interview, expected)
                done = player.done()
            except Exception:
                h.add_screenshot(player.screenshot("ai-stuck"))
                h.record_wire({"stuck": True}, player.where_it_stood())
                raise
            h.add_screenshot(player.screenshot("ai-done"))
    finally:
        stranger.close()
    with j.recorder.step("interviewer (FR-008 / FR-H): keel-web sent ONE response -- `format` AI_INTERVIEWER, `heard` / "
                         "`how` on every answer, exactly the person's own answers -- and after the pilot ask (*Last "
                         "question*, never skipped) one pilot write, counted in the overview's pilot", party="participant",
                         kind="assert") as h:
        responses, pilots = seen.get("response") or [], seen.get("pilot") or []
        body = (responses[0] if responses else {}).get("body") or {}
        _, register = wire("GET", "/invitations")
        row = next((r for r in register.get("invitations") or [] if r.get("invitationId") == made["invitationId"]),
                   {})
        pilot_after = (j.get(j.project("/standings")) or {}).get("pilot") or {}
        sent = {a["itemId"]: _closed(a) for a in body.get("answers") or []}
        want = {a["itemId"]: _closed(a) for a in expected.get("answers") or []}
        top = {k: body.get(k) for k in ("recency", "story", "anchorChip") if k in expected}
        by_item = {a.get("itemId"): a for a in body.get("answers") or []}
        typed = [{"itemId": w["typed"]["itemId"], "typed": w["typed"]["value"],
                  "how": (by_item.get(w["typed"]["itemId"]) or {}).get("how"),
                  "heard": (by_item.get(w["typed"]["itemId"]) or {}).get("heard")} for w in walked if w.get("typed")]
        if typed:
            # Spec 046 FM6 (keel-web 070, DRIFT #89 closed): a value typed into the field carries `heard`.
            record["typed_fields"] = j.feedback["typed_fields"] = typed
        record["ai_answers"] = {"body": body, "status": (responses[0] if responses else {}).get("status"),
                                "register_row": row, "by": "keel-web", "walked": walked, "intro": intro,
                                "done": done, "expected": expected}
        record["pilot"] = {**record.get("pilot", {}), "answered": "YES" if pilots and pilots[0]["status"] == 204 else None,
                           "before": pilot_before.get("optedIn"), "after": pilot_after.get("optedIn"),
                           "status": pilots[0]["status"] if pilots else None,
                           "asked": [w["where"] for w in walked][-1:]}
        h.record_assert({"responses": 1, "format": "AI_INTERVIEWER", "answers": want,
                         "top": {k: expected[k] for k in top}, "pilot": 204, "formatUsed": "AI_INTERVIEWER",
                         "intro": {"intro": "AI_INTERVIEWER", "heading": f"{fake.FACE_NAMES[FIRST_FACE]} will ask you"}},
                        {"responses": len(responses), "format": body.get("format"), "answers": sent, "top": top,
                         "pilots": pilots, "row": row, "intro": intro, "walked": walked})
        assert intro["intro"] == "AI_INTERVIEWER" and intro["buttons"] == ["start-talking"], intro
        assert intro["heading"].startswith(f"{fake.FACE_NAMES[FIRST_FACE]} will ask you"), intro
        assert len(responses) == 1 and responses[0]["status"] in (200, 201), responses
        assert body.get("format") == "AI_INTERVIEWER", body
        assert sent == want, {"sent": sent, "want": want}
        assert top == {k: expected[k] for k in top}, (top, expected)
        assert len(pilots) == 1 and pilots[0]["status"] == 204, pilots
        assert row.get("formatUsed") == "AI_INTERVIEWER" and row.get("status") == "ANSWERED", row
        assert all(w["mark"] == ivs.MARK for w in walked), [w["mark"] for w in walked]
    _read_on_arrival(j, wire, record, made["invitationId"], "the AI link's")


def _read_on_arrival(j, wire: _Wire, record: dict, invitation_id: str, whose: str) -> None:
    """keel-cloud 095 FR-A / FR-E, on Keel's door: an answer with words is read on arrival -- the founder presses
    nothing -- and its INTERPRET HOLD says why (`read-on-arrival:<invitationId>`); since keel-cloud 096 no batch writes
    the brief. On this stack Keel's own AI has no key, so each job fails at once and is refunded; the batch still ends.
    Nothing here starts a reading."""
    with j.recorder.step(f"interviewer (keel-cloud 095): {whose} answer is read on arrival -- no POST readings; the "
                         "newest batch ends; its INTERPRET HOLD carries read-on-arrival:<invitationId>, and no batch "
                         "writes the brief (096; Keel's AI has no key on this stack: each job refunded)", party="stack",
                         kind="assert") as h:
        deadline = time.monotonic() + 60 * j.patience
        batch: dict = {}
        while time.monotonic() < deadline:
            batches = j.get(j.project("/readings")) or []
            batch = batches[0] if isinstance(batches, list) and batches else {}
            if invitation_id in (batch.get("invitationIds") or []) and batch.get("status") not in ("RUNNING",
                                                                                                    "PENDING"):
                break
            time.sleep(1)
        rows = stack_ledger.rows(j.stack, record["founder_id"])
        mine = [x for x in rows if (x.get("reason") or "") == f"read-on-arrival:{invitation_id}"]
        record.setdefault("arrivals", []).append({"invitationId": invitation_id, "batch": batch,
                                                  "holds": [x for x in mine if x.get("kind") == "HOLD"]})
        h.record_assert({"batch": "ends with this answer in it", "HOLD reason": f"read-on-arrival:{invitation_id}"},
                        {"batch": batch, "rows": [(x["kind"], x.get("action"), x["credits"], x.get("reason"))
                                                  for x in rows if x.get("action") in ("INTERPRET", "BRIEF")]})
        assert invitation_id in (batch.get("invitationIds") or []), batch
        assert batch.get("status") not in ("RUNNING", "PENDING"), batch
        assert [x for x in mine if x.get("kind") == "HOLD" and x.get("action") == "INTERPRET"], mine


def _read_what_is_left(j, wire: _Wire, record: dict) -> None:
    """Call 152: the answers read on arrival failed on Keel's keyless door and wait unread; keel-cloud 095 FR-D reads
    every unread answer of the founder's projects when an agent next connects -- S-007's runtime, on S-007's script,
    which would spend S-007's readings on them (found once: S-007's standings moved by one person). So, back on their
    own door with this journey's runtime still connected, the founder asks for the reading on the wire, and the leg
    leaves nothing unread."""
    with j.recorder.step("interviewer (call 152): back on their own door, the founder's session reads what Keel's "
                         "keyless door left unread, so the next agent to connect finds nothing of this project's to "
                         "read", party="founder", kind="assert") as h:
        status, started = wire("POST", "/readings", {}, ok=(201, 409))
        deadline = time.monotonic() + 60 * j.patience
        batch = started if isinstance(started, dict) else {}
        while status == 201 and time.monotonic() < deadline:
            batches = j.get(j.project("/readings")) or []
            batch = batches[0] if isinstance(batches, list) and batches else {}
            if batch.get("status") not in ("RUNNING", "PENDING"):
                break
            time.sleep(1)
        again, nothing = wire("POST", "/readings", {}, ok=(201, 409))
        record["left_unread"] = {"status": status, "batch": batch, "after": {"status": again, "body": nothing}}
        h.record_assert({"batch": "DONE", "failed": [], "after": "409 NOTHING_TO_READ"}, record["left_unread"])
        assert status == 201 and batch.get("status") == "DONE" and not batch.get("failed"), record["left_unread"]
        # a reading's refusal names itself in `rule` (`ReadingRefusal`), not `code`
        assert again == 409 and (nothing.get("code") or nothing.get("rule")) == "NOTHING_TO_READ", record["left_unread"]
    with j.recorder.step("interviewer (keel-cloud 096, spec 045): the readings wrote no brief; the founder comes back "
                         "(GET overview on the session the agent is bound to) and one BRIEF is started and ends on "
                         "this journey's own runtime (spec 045 call 172)", party="founder", kind="assert") as h:
        briefs = lambda: [i for i in (j.get(f"/v2/inference-interactions?project_id={j.project_id}") or [])  # noqa: E731
                          if i.get("screen") == "BRIEF"]
        before = briefs()
        j.get(j.project("/overview"))
        deadline = time.monotonic() + 60 * j.patience
        after = briefs()
        ended = {"APPLIED", "RESULT_INVALID", "DOMAIN_REFUSED", "JOB_FAILED", "APPLY_ERROR", "ABANDONED"}
        seen = {x.get("interaction_id") for x in before}
        while time.monotonic() < deadline and not [b for b in after
                                                   if b.get("interaction_id") not in seen and b.get("status") in ended]:
            time.sleep(1)
            after = briefs()
        new = [b.get("status") for b in after if b.get("interaction_id") not in seen]
        record["brief_on_return"] = {"before": [b.get("status") for b in before], "new": new}
        h.record_assert({"new BRIEF": "one that ends (a lost race's retries aside)"}, record["brief_on_return"])
        assert 1 <= len(new) <= 3 and new.count("STATE_CONFLICT") == len(new) - 1, new


def _choice_intro_on_screen(j, url: str) -> dict:
    """A Let-them-choose link's intro on the stranger's own page (P0c): both offered. Read only -- the answer in
    writing goes on the wire (call 154: the text player behind *Answer in writing* is the text link's, walked on every
    journey already)."""
    stranger = j.browser.new_context()
    try:
        page = stranger.new_page()
        player = ivs.Player(page, j.recorder, patience=j.patience)
        with player.step("the stranger opens a Let-them-choose link: Talk to Tito, or Answer in writing") as h:
            drawn = player.open(url)
            h.add_screenshot(player.screenshot("choice-intro"))
            return drawn
    finally:
        stranger.close()


def _choice_link(j, wire: _Wire, record: dict) -> None:
    with j.recorder.step("interviewer (FR-H): a Let-them-choose link's interview offers both -- `formats` [TEXT, "
                         "AI_INTERVIEWER] with the player -- and an answer in writing posts `format` TEXT, which the "
                         "register reads as `formatUsed` TEXT", party="participant", kind="assert") as h:
        made = _send_link(j, "CHOICE", CHOICE_PERSON)
        interview = _json_of(_participant(j, "GET", made["token"], "/interview"))
        intro = _choice_intro_on_screen(j, made["url"])
        person = _person_for_the_link(j)
        items = {i.get("dimension"): i for part in interview.get("parts") or [] for i in part.get("items") or []}
        recall = ((items.get("commercial.existing_sacrifice") or {}).get("costTotal") or {}).get("recallPeriod")
        body = dict(person.response(made["token"], recall), format="TEXT")
        posted = _participant(j, "POST", made["token"], "/interview/response", body)
        _, register = wire("GET", "/invitations")
        row = next((r for r in register.get("invitations") or [] if r.get("invitationId") == made["invitationId"]),
                   {})
        record["choice"] = {"made": made, "formats": interview.get("formats"),
                            "player": bool(interview.get("interviewer")), "response": posted.status_code,
                            "register_row": row, "intro": intro}
        h.record_assert({"format": "CHOICE", "formats": ["TEXT", "AI_INTERVIEWER"], "player": True,
                         "formatUsed": "TEXT"}, record["choice"])
        assert made["format"] == "CHOICE" and interview.get("formats") == ["TEXT", "AI_INTERVIEWER"], record["choice"]
        assert interview.get("interviewer") and posted.status_code in (200, 201), record["choice"]
        assert row.get("format") == "CHOICE" and row.get("formatUsed") == "TEXT", row
        assert intro["intro"] == "CHOICE" and intro["buttons"] == ["choice-talk", "choice-write"], intro
    _read_on_arrival(j, wire, record, made["invitationId"], "the Let-them-choose link's")


def _change_face(j, wire: _Wire, record: dict) -> None:
    with j.recorder.step(f"interviewer (decision 3): *Change who asks · 400 AI credits* -- "
                         f"{fake.FACE_NAMES[CHANGED_FACE]} -- charges 400 once, the line goes back to RECORDING and "
                         "then READY on the new face; the old clips serve until then and are gone after",
                         party="founder", kind="assert") as h:
        old = (record.get("recording") or {}).get("clips") or []
        old_ai = record["ai_link"]["made"]["token"]
        before = wire.credits()
        persona = _persona(j)
        persona.sent(j.project_id)
        pressed = persona.record(CHANGED_FACE)
        status, view = pressed["status"], pressed["body"]
        record["wire_views"].append(view)
        drawn_after = persona.line()
        ready = _ready(j, wire, record, CHANGED_FACE, "the change of face")
        after = wire.credits()
        stored = (stack_ledger.recording(j.stack, j.project_id).get("recording") or {})
        gone = _stranger_clip(j, f"/v2/i/{old_ai}/interview/clips/{old[0]['id']}", "bytes=0-99") if old else {}
        record["change"] = {"face": CHANGED_FACE, "face_before": FIRST_FACE,
                            "face_after": (view.get("face") or {}).get("code"), "status": status,
                            "balance_before": before, "balance_after": after,
                            "trail": [view.get("status")] + ready["trail"],
                            "ready_face": stored.get("face"), "old_clip_after_ready": gone.get("status"),
                            "popup": pressed["popup"], "line_after_press": drawn_after}
        h.record_assert({"face": CHANGED_FACE, "charged": fake.CREDITS, "trail": "RECORDING ... READY",
                         "old clip": 404}, record["change"])
        assert status == 200 and record["change"]["face_after"] == CHANGED_FACE, view
        assert pressed["popup"]["title"] == ivs.CHANGE_FACE_TITLE, pressed["popup"]
        assert pressed["popup"]["confirm"] == f"Record {fake.FACE_NAMES[CHANGED_FACE]}", pressed["popup"]
        assert before - after == fake.CREDITS, record["change"]
        assert stored.get("face") == CHANGED_FACE and stored.get("status") == "READY", stored.get("status")
        assert not old or gone.get("status") == 404, gone
    record["recording_after_change"] = {"face": stored.get("face"), "clips": len(stored.get("clips") or [])}


def _low_balance(j, wire: _Wire, record: dict, founder_id: str, run: str) -> None:
    with j.recorder.step(f"interviewer: STAND-IN -- the balance lowered to {LOW_BALANCE}, under one change of face",
                         party="stack", kind="protocol") as h:
        delta = stack_ledger.stand_in_balance(j.stack, founder_id, run, to=LOW_BALANCE, spec=SPEC)
        h.record_wire({"row": delta}, {"creditsAvailable": wire.credits()})
        assert wire.credits() == LOW_BALANCE
    with j.recorder.step(f"interviewer (decision 3): at {LOW_BALANCE} credits a change of face is REFUSED 422 "
                         "INSUFFICIENT_CREDITS_FOR_INTERVIEWER with required / available and keel-cloud's sentence; "
                         "nothing is charged and Judy still asks", party="founder", kind="assert") as h:
        rows_before = _rows(j, record)
        persona = _persona(j)
        persona.sent(j.project_id)
        persona.wait_state("READY")
        pressed = persona.record(FIRST_FACE)
        status, body = pressed["status"], pressed["body"]
        _, view = wire("GET", "/interviewer")
        record["low_balance"] = {"status": status, "body": body, "balance": LOW_BALANCE,
                                 "balance_after": wire.credits(), "ledger_rows_added": _rows(j, record) - rows_before,
                                 "face_before": CHANGED_FACE, "face_after": (view.get("face") or {}).get("code"),
                                 "popup": pressed.get("popup_text"), "refusal_drawn": pressed.get("refusal")}
        want = fake.INSUFFICIENT_REMEDY.format(required=fake.CREDITS, available=LOW_BALANCE)
        h.record_assert({"status": 422, "code": fake.INSUFFICIENT, "required": fake.CREDITS, "available": LOW_BALANCE,
                         "remedy": want}, record["low_balance"])
        assert body.get("code") == fake.INSUFFICIENT and body.get("required") == fake.CREDITS, body
        assert body.get("available") == LOW_BALANCE and body.get("remedy") == want, body
        assert record["low_balance"]["ledger_rows_added"] == 0 and view.get("status") == "READY", record["low_balance"]
        # the popup draws the server's words, its balance sentence left off (keel-web 069 `withoutBalance`)
        assert want.split(" You have")[0] in (pressed.get("popup_text") or ""), pressed


def _retry(j, wire: _Wire, record: dict) -> None:
    """Step 9: a clip the fake fails once is retried by the recorder, READY still arrives, and the retry is free. The
    fake's seams (`FakeInterviewerRenders.failOnce` / `failScripts`) are reachable from a test's own Spring context and
    from nothing the stack sets (DRIFT #86), so the retry is read off the recording where it happened and is otherwise
    unmeasured, never passed."""
    stored = (stack_ledger.recording(j.stack, j.project_id).get("recording") or {})
    retried = [c for c in stored.get("clips") or [] if int(c.get("attempts") or 0) >= 2]
    with j.recorder.step("interviewer (FR-E): a clip retried by the recorder on its own -- read off the stored "
                         "recording; the fake's fail-once seam is not reachable from the stack (DRIFT #86)",
                         party="stack", kind="note") as h:
        h.record_wire({"seam": "FakeInterviewerRenders.failOnce / failScripts"},
                      {"retried": [(c.get("kind"), c.get("attempts"), c.get("status")) for c in retried]})
    if retried:
        record["retry"] = {"clip": retried[0], "status": stored.get("status"), "ledger_rows_added": 0}


def _score(j, record: dict, *, require: list[str]) -> None:
    """The interviewer marks over the record, written into the bundle; the leg fails on any owed mark unmet."""
    card = marks.scorecard(record)
    run_dir = Path(j.recorder.run_dir)
    (run_dir / "interviewer.json").write_text(json.dumps(record, indent=2, default=str) + "\n", encoding="utf-8")
    (run_dir / "interviewer-marks.json").write_text(json.dumps(card, indent=2, default=str) + "\n", encoding="utf-8")
    with j.recorder.step(f"interviewer marks v{marks.INTERVIEWER_MARKS_VERSION}: {card['met']} of {card['measured']} "
                         f"met ({', '.join(require)} owed)", party="stack", kind="assert") as h:
        owed = {c["mark"]: c for c in card["checks"] if c["mark"] in require}
        h.record_assert({m: True for m in require}, {m: {"ok": c["ok"], "detail": c["detail"]}
                                                     for m, c in owed.items()})
        unmet = [m for m, c in owed.items() if not (c["measured"] and c["ok"])]
        assert not unmet, {m: owed[m] for m in unmet}
