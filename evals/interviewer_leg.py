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
import time
import uuid
from pathlib import Path

import requests

from evals import interviewer_marks as marks
from harness import interviewer_fake as fake
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

#: What waits for keel-web 069's page objects (`harness/interviewer_screens.py`): L1's carousel, W1's frame 2, Sent's
#: persona line (S1 / S2), Send more's format row (S3), the change popup, the role card's *Try it yourself*, the dry
#: run's page and the stranger's stage, sheet and field through the speech seam.
WEB_069_FOLLOW_UP = (
    "keel-web 069 (the AI interviewer's screens): page objects for L1, W1 frame 2, S1 / S2 / S3, the change popup, Try "
    "it yourself and the respondent's player through window.__keelSpeech -- each held to the wire this leg holds.")


class _Wire:
    """The founder's calls on keel-cloud's routes, each kept for the record (IM2 sweeps the interviewer bodies)."""

    def __init__(self, j, record: dict):
        self.j = j
        self.record = record

    def __call__(self, method: str, suffix: str, body: dict | None = None, *, ok=(200, 201, 204)) -> tuple[int, dict]:
        path = suffix if suffix.startswith("/v2/") else self.j.project(suffix)
        status, payload = self.j.call(method, path, body, ok=ok)
        self.record["responses"].append({"method": method, "path": path, "status": status, "body": payload})
        if "/interviewer" in path and isinstance(payload, dict) and status < 300:
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


# --------------------------------------------------------------------------------------------- the legs

def leg_interviewer(j) -> dict:
    """S-006 (05-paidly, B2B), after the contacts leg: the whole of spec 044 FR-002 (see the module docstring)."""
    return _leg(j, short=False)


def leg_interviewer_short(j) -> dict:
    """S-005 (01-countly, B2C): the short form (spec 044 judgement call 3) -- the recording's one charge, READY, the
    spoken order and the solution passage on the one role, and one AI-interviewer link served with Range."""
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
            _while_recording(j, wire, record)
        _ready(j, wire, record, FIRST_FACE, "the first recording")
        _the_recording(j, wire, record)
        if not short:
            _dry_run(j, wire, record)
        _ai_link(j, wire, record, answer=not short)
        if not short:
            _choice_link(j, wire, record)
            _change_face(j, wire, record)
            _low_balance(j, wire, record, founder_id, run)
            _retry(j, wire, record)
        record["ledger"] = stack_ledger.rows(j.stack, founder_id, since=since)
        with j.recorder.step("interviewer: the ledger since Keel's door -- the stand-in grant, the recording's one "
                             "HOLD / SPEND pair, the change's, the stand-in low balance, and no other row",
                             party="stack", kind="assert") as h:
            others = [x for x in record["ledger"] if x.get("action") not in fake.ACTIONS
                      and not (x.get("idempotency_key") or "").startswith(stack_ledger.key_prefix(SPEC))]
            h.record_assert({"other rows": []}, {"rows": [(x["kind"], x.get("action"), x["credits"])
                                                          for x in record["ledger"]], "others": others})
            assert not others, others
    finally:
        _restore(j, wire, founder_id, run)
    if short:
        # the short form answers no AI link, so the pilot's count has no subject: what was served is kept apart
        record["pilot_served"] = record.pop("pilot", {}).get("served")
    require = ["IM1", "IM3", "IM4", "IM5", "IM7"] if short else [m for m, _, _ in marks.MARKS if m in _owed(record)]
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
    """runs/DRIFT.md #85: contract 16 says the batch refuses an own-AI account's AI_INTERVIEWER / CHOICE links 422
    INTERVIEWER_NEEDS_CREDITS, as the single link and the commercial link do; keel-cloud's batch (`ContactsService.
    makeLinks`) never asks the door and answers 409 INTERVIEWER_NOT_READY. Stepped round, not failed: what is held is
    that nothing is made; the code is held straight the moment it is the contract's."""
    with j.recorder.step("interviewer: DRIFT #85 -- on their own AI the founder's AI-interviewer link in a BATCH is "
                         "refused 409 INTERVIEWER_NOT_READY where contract 16 says 422 INTERVIEWER_NEEDS_CREDITS; "
                         "nothing is made either way", party="founder", kind="assert") as h:
        before = len((wire("GET", "/invitations")[1]).get("invitations") or [])
        status, body = wire("POST", "/invitations/batch", {
            "expectedRevision": j.revision(), "respondentType": vs.LINK_PRIMARY, "format": "AI_INTERVIEWER",
            "people": [{"personName": AI_PERSON}]}, ok=(409, 422))
        after = len((wire("GET", "/invitations")[1]).get("invitations") or [])
        fired = (status, body.get("code")) == (409, fake.NOT_READY)
        record["own_ai"]["batch"] = {"status": status, "body": body, "drift_85": fired}
        h.record_assert({"status": 422, "code": fake.NEEDS_CREDITS, "made": 0},
                        {"status": status, "code": body.get("code"), "made": after - before, "DRIFT #85": fired})
        assert before == after, (before, after)
        assert fired or (status, body.get("code")) == (422, fake.NEEDS_CREDITS), body


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
        status, view = wire("POST", "/interviewer/face", {"face": FIRST_FACE})
        record["first"] = {"status": status, "view": view, "balance_before": balance_before,
                           "balance_after": wire.credits(), "at": stack_ledger.now(j.stack)}
        h.record_assert({"status": 200, "face": FIRST_FACE, "recording": "RECORDING or READY",
                         "balance": balance_before - fake.CREDITS}, record["first"])
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
        assert stored.get("schema_version") == 22, stored.get("schema_version")
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
        after = _counts(j, wire, record)
        clips = len([c for c in (player.get("clips") or {}).values() if c]) + sum(
            1 + (1 if v.get("more") else 0) for v in (player.get("items") or {}).values())
        record["dry_run"] = {"tryRun": served.get("tryRun"), "clips": clips, "before": before, "after": after,
                             "writes": [], "founder_clip": founder_clip, "opening_url": opening.get("url"),
                             "mark": player.get("mark")}
        h.record_assert({"tryRun": True, "mark": fake.MARK, "url": f"/v2/projects/{j.project_id}/interviewer/clips/",
                         "clip": 206, "before == after": True}, record["dry_run"])
        assert served.get("tryRun") is True and player.get("mark") == fake.MARK, served.get("tryRun")
        assert (opening.get("url") or "").startswith(f"/v2/projects/{j.project_id}/interviewer/clips/"), opening
        assert founder_clip["status"] == 206, founder_clip
        assert before == after, (before, after)


def _make_link(j, wire: _Wire, fmt: str, person: str) -> dict:
    _, batch = wire("POST", "/invitations/batch", {"expectedRevision": j.revision(),
                                                   "respondentType": vs.LINK_PRIMARY, "format": fmt,
                                                   "people": [{"personName": person}]})
    link = (batch.get("links") or [{}])[0]
    return {"format": batch.get("format"), "url": link.get("url"), "invitationId": link.get("invitationId"),
            "token": _token(link.get("url") or "")}


def _ai_link(j, wire: _Wire, record: dict, *, answer: bool) -> None:
    """Decision 5 and FR-H: an AI-interviewer link's interview carries the player -- every clip on the link's own route,
    206 to a Range, 404 for a clip that is not this link's -- and its answers go back with `heard` / `how`."""
    with j.recorder.step("interviewer (FR-H): an AI-interviewer link is made once READY; the stranger's interview "
                         "carries `interviewer` (the face, the mark, every clip in order) and `formats` "
                         "[AI_INTERVIEWER]; its clips answer 206 to a Range, 200 whole, 404 for another role's clip",
                         party="participant", kind="assert") as h:
        made = _make_link(j, wire, "AI_INTERVIEWER", AI_PERSON)
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
        _answer_ai_on_the_wire(j, wire, record, made, interview)


def _person_for_the_link(j):
    """The first corpus person on the primary link -- composed, never generated (spec 043 call 133's rule)."""
    return next(p for p in j.people if p.link == vs.LINK_PRIMARY)


def _with_heard(body: dict, interview: dict) -> dict:
    """The corpus person's body as the AI page sends it: `format` AI_INTERVIEWER and `heard` / `how` on every answer --
    the first with options said aloud (its options' words), a cost total typed, the rest tapped (heard: the tapped
    option's words)."""
    labels = {}
    for part in interview.get("parts") or []:
        for item in part.get("items") or []:
            labels[item.get("itemId")] = {o.get("optionId"): o.get("label") for o in item.get("options") or []}
    out = dict(body, format="AI_INTERVIEWER")
    answers = []
    said = False
    for a in body.get("answers") or []:
        words = " and ".join(labels.get(a.get("itemId"), {}).get(o, "") for o in a.get("optionIds") or []).strip()
        if a.get("costTotal"):
            how, heard = "TYPED", str((a.get("costTotal") or {}).get("value"))
        elif not said and words:
            how, heard, said = "SPOKEN", words, True
        else:
            how, heard = "TAPPED", words or str(a.get("scale") or a.get("number") or a.get("chip") or "")
        answers.append({**a, "heard": heard, "how": how})
    out["answers"] = answers
    return out


def _answer_ai_on_the_wire(j, wire: _Wire, record: dict, made: dict, interview: dict) -> None:
    """Until keel-web 069's player is driven through the speech seam: the body its page sends, on the wire."""
    with j.recorder.step("interviewer (FR-H): the AI link answered -- `format` AI_INTERVIEWER and `heard` / `how` on "
                         "every answer; then the pilot ask's Yes, the same write a text link's is, counted in the "
                         "overview's pilot", party="participant", kind="assert") as h:
        person = _person_for_the_link(j)
        items = {i.get("dimension"): i for part in interview.get("parts") or [] for i in part.get("items") or []}
        recall = ((items.get("commercial.existing_sacrifice") or {}).get("costTotal") or {}).get("recallPeriod")
        body = _with_heard(person.response(made["token"], recall), interview)
        pilot_before = (j.get(j.project("/standings")) or {}).get("pilot") or {}
        posted = _participant(j, "POST", made["token"], "/interview/response", body)
        pilot = _participant(j, "POST", made["token"], "/interview/pilot", {"pilotOptIn": True})
        _, register = wire("GET", "/invitations")
        row = next((r for r in register.get("invitations") or [] if r.get("invitationId") == made["invitationId"]),
                   {})
        pilot_after = (j.get(j.project("/standings")) or {}).get("pilot") or {}
        record["ai_answers"] = {"body": body, "status": posted.status_code, "register_row": row, "by": "wire"}
        record["pilot"] = {**record.get("pilot", {}), "answered": "YES" if pilot.status_code == 204 else None,
                           "before": pilot_before.get("optedIn"), "after": pilot_after.get("optedIn"),
                           "status": pilot.status_code}
        h.record_assert({"response": 201, "pilot": 204, "formatUsed": "AI_INTERVIEWER", "status": "ANSWERED",
                         "optedIn": (pilot_before.get("optedIn") or 0) + 1},
                        {"response": posted.status_code, "pilot": pilot.status_code, "row": row,
                         "optedIn": pilot_after.get("optedIn")})
        assert posted.status_code in (200, 201), _json_of(posted)
        assert pilot.status_code == 204, pilot.text
        assert row.get("formatUsed") == "AI_INTERVIEWER" and row.get("status") == "ANSWERED", row


def _choice_link(j, wire: _Wire, record: dict) -> None:
    with j.recorder.step("interviewer (FR-H): a Let-them-choose link's interview offers both -- `formats` [TEXT, "
                         "AI_INTERVIEWER] with the player -- and an answer in writing posts `format` TEXT, which the "
                         "register reads as `formatUsed` TEXT", party="participant", kind="assert") as h:
        made = _make_link(j, wire, "CHOICE", CHOICE_PERSON)
        interview = _json_of(_participant(j, "GET", made["token"], "/interview"))
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
                            "register_row": row}
        h.record_assert({"format": "CHOICE", "formats": ["TEXT", "AI_INTERVIEWER"], "player": True,
                         "formatUsed": "TEXT"}, record["choice"])
        assert made["format"] == "CHOICE" and interview.get("formats") == ["TEXT", "AI_INTERVIEWER"], record["choice"]
        assert interview.get("interviewer") and posted.status_code in (200, 201), record["choice"]
        assert row.get("format") == "CHOICE" and row.get("formatUsed") == "TEXT", row


def _change_face(j, wire: _Wire, record: dict) -> None:
    with j.recorder.step(f"interviewer (decision 3): *Change who asks · 400 AI credits* -- "
                         f"{fake.FACE_NAMES[CHANGED_FACE]} -- charges 400 once, the line goes back to RECORDING and "
                         "then READY on the new face; the old clips serve until then and are gone after",
                         party="founder", kind="assert") as h:
        old = (record.get("recording") or {}).get("clips") or []
        old_ai = record["ai_link"]["made"]["token"]
        before = wire.credits()
        status, view = wire("POST", "/interviewer/face", {"face": CHANGED_FACE})
        ready = _ready(j, wire, record, CHANGED_FACE, "the change of face")
        after = wire.credits()
        stored = (stack_ledger.recording(j.stack, j.project_id).get("recording") or {})
        gone = _stranger_clip(j, f"/v2/i/{old_ai}/interview/clips/{old[0]['id']}", "bytes=0-99") if old else {}
        record["change"] = {"face": CHANGED_FACE, "face_before": FIRST_FACE,
                            "face_after": (view.get("face") or {}).get("code"), "status": status,
                            "balance_before": before, "balance_after": after,
                            "trail": [view.get("status")] + ready["trail"],
                            "ready_face": stored.get("face"), "old_clip_after_ready": gone.get("status")}
        h.record_assert({"face": CHANGED_FACE, "charged": fake.CREDITS, "trail": "RECORDING ... READY",
                         "old clip": 404}, record["change"])
        assert status == 200 and record["change"]["face_after"] == CHANGED_FACE, view
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
        status, body = wire("POST", "/interviewer/face", {"face": FIRST_FACE}, ok=(422,))
        _, view = wire("GET", "/interviewer")
        record["low_balance"] = {"status": status, "body": body, "balance": LOW_BALANCE,
                                 "balance_after": wire.credits(), "ledger_rows_added": _rows(j, record) - rows_before,
                                 "face_before": CHANGED_FACE, "face_after": (view.get("face") or {}).get("code")}
        want = fake.INSUFFICIENT_REMEDY.format(required=fake.CREDITS, available=LOW_BALANCE)
        h.record_assert({"status": 422, "code": fake.INSUFFICIENT, "required": fake.CREDITS, "available": LOW_BALANCE,
                         "remedy": want}, record["low_balance"])
        assert body.get("code") == fake.INSUFFICIENT and body.get("required") == fake.CREDITS, body
        assert body.get("available") == LOW_BALANCE and body.get("remedy") == want, body
        assert record["low_balance"]["ledger_rows_added"] == 0 and view.get("status") == "READY", record["low_balance"]


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
