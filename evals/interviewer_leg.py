"""The AI interviewer leg (spec 044; keel-cloud 094 at contract 16, `InferenceCharge` 9; keel-web 069): after S-006's
contacts leg the founder's project gets its interviewer -- Chukwu since spec 058 (Tito before), recorded once by the
stack's fake renderer -- and the leg walks everything 094 and 069 say about it: the recording's one charge, the persona
line through RECORDING to READY, the links that wait for it (`INTERVIEWER_NOT_READY`) and the text link that never
does, the spoken order of every role's clips, the solution passage's three facts, the founder's word never spoken, *Try it yourself* writing nothing,
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

**Since spec 048 (keel-cloud 099 + keel-web 072, contract 18; 19 since 051) the stranger's walk is the answer path**: the intro's
*Test your mic* ("hello" -> *Heard: hello*), no *That's my answer* anywhere, every spoken answer read by the cloud's
classifier -- the stack's FakeClassifier, left real behind the page (judgement call 1) -- a confident read **held** and
gone on by itself, a correction and one word two labels carry asked *Is that right?*, a word of protest in a hold, Back
from the next question with the answer changed by a tap; before the link is answered the classifier guard sends the
152 spoken-answer cases carried onto its own items (`harness/classifier_guard.py`), Try it yourself asks its own
founder's route, and S-006 answers one more AI link from the recorded path on the wire (silence, the fake transcriber,
`how` RECORDED).

**Since spec 049 (keel-cloud 100 + keel-web 073) the page hears them out**: nothing is lit or filled while they speak,
and an utterance is read after a 1.5 s quiet gap, every final of the window joined. The guard's copy carries 100's 18
`readaloud` cases (170 in all); one question is answered the way people do -- its first words read aloud as a final,
then the option's own words as a final within a second -- and the leg holds one read of both, nothing lit between
(IM19); the first pick-two is answered by taps that wait for *Save and next* (IM20); the pilot's spoken yes is held
and goes on with no *Finish*; and the recorded link's pilot ask is written down through `transcribe` as the page
does it (DRIFT #91).

**Since spec 050 (keel-cloud 101 + 102, keel-web 074 + 075)**: every role's opening says whose idea it is and the
route, and the problem and idea passages close on *Take a moment* and the count (a plain assertion on the stored
scripts); on S-006 a recording seeded in the old words re-renders them at no charge on the first read (FR-5); the walk
lets the 2 s beat after each of those passages pass and holds what it drew (IM21) and the 4 s gap (no length
encoded); the story ends by the pause on S-005 and by its *Save and next* on S-006 (IM22); a yes to *Is that right?* is
held (IM15); *Microphone off* after the thanks (and on the dry run's End); and the recorded link's pilot yes is written
down now that keel-cloud 102 serves `transcribe` until the opt-in (DRIFT #91 resolved).

**Since spec 051 (keel-cloud 103, contract 19 on the interview side; keel-web 076)**: after the last item's hold the
page asks the cloud's follow-up route; the leg holds the rung and the words to the harness's own walk (`LADDER`,
`first_rung`), walks two windows by way of Back -- S-005's browser path by the pause then by *Save and next*, S-006's
recorded path (the recogniser refusing, the seam's recorder) 4 s after the last sound, then left silent to the cap and
skipped -- checks Try it yourself's twin route and the recorded link's follow-up on the wire, every role's FOLLOW_UP
clips and their free backfill (stand-in 5), and the consent line (IM23-IM27).

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
from harness import classifier_guard as guard
from harness import interviewer_fake as fake
from harness import interviewer_screens as ivs
from harness import interviews_screens as iv
from harness import vectors_script as vs
from stack import ledger as stack_ledger

SPEC = "044"
#: What the stack's fake transcriber hears for any recording over the silence floor (`stack/cloud.py`
#: KEEL_INTERVIEWER_FAKE_TRANSCRIPT; keel-cloud 099 FakeTranscriber's `otherwise`).
FAKE_TRANSCRIPT = "yes"
#: Spec 058 (keel-cloud 110): the four photo avatars -- the first recording is the last card (Tito's place), the change
#: goes to LIVIA (where JUDY was), the preselected face, which is therefore a change and not the default.
FIRST_FACE = "CHUKWU"
CHANGED_FACE = "LIVIA"
#: Spec 058 FR-2 / FR-3: how long a tapped hello (4.6-5.4 s) is waited for to end -- on the remote profile the 90 s
#: navigation timeout, as the welcome's mp4 is (a clip over the wire may take its time to load).
HEAR_WAIT_S = 20
HEAR_WAIT_REMOTE_S = 90
#: The balance the change is refused at (stand-in 2): under one change (400), over nothing else the leg needs.
LOW_BALANCE = 100
AI_PERSON = "Someone the founder knows, by voice"
CHOICE_PERSON = "Someone the founder knows, who picks"
#: Spec 048 (keel-cloud 099 FR-4 / FR-7): an AI link answered from the recorded path, on the wire.
RECORDED_PERSON = "Someone the founder knows, whose browser records"
#: keel-cloud 099 judgement call 1: under 12 KiB of audio/webm is silence -- never transcribed, never classified. One
#: byte under, and one well over (what the stack's fake transcriber hears for it is `FAKE_TRANSCRIPT`).
SILENT_WEBM = b"\x1a\x45\xdf\xa3" + b"\x00" * (12 * 1024 - 5)
SOUNDED_WEBM = b"\x1a\x45\xdf\xa3" + b"\x01" * (16 * 1024)
TEXT_PERSON = "Someone the founder knows, in writing"
#: The founder's word the leg writes after the lock (call 149: no corpus founder writes one; `PUT word` is legal after
#: the lock) -- so the rule that it is never spoken has a word to hold. Composed here, never generated.
FOUNDERS_WORD = ("I started this because I spent years watching good people lose whole evenings to it, and I would "
                 "like to hear how it goes for you before I build anything.")

#: keel-web 069's page objects (`harness/interviewer_screens.py`), built in spec 044 once 069 merged at `d23895f`.
WEB_069_FOLLOW_UP = (
    "keel-web 069 (the AI interviewer's screens), DONE in spec 044: L1, W1 frame 2 (replayed until keel-web 088), S1 / "
    "S2 / S3, the "
    "persona line's popup, Try it yourself and the respondent's stage and sheet through window.__keelSpeech -- each "
    "held to the wire this leg holds.")
READ_REASON = marks.READ_REASON
#: Spec 044 judgement call 3, widened (call 155): the B2C short form -- the recording, READY, its clips, one AI link
#: served with Range and answered on the stranger's own screen (the consumer link carries the cost total, so the field
#: is typed there), the pilot, the reading on arrival.
#: Spec 048: the stranger's walk is the answer path on S-005 too -- the mic test, the holds, "Is that right?" and the
#: way back are owed there as on S-006; RECORDED (IM18) is the full leg's alone.
#: Spec 049: IM19 (hears them out) and IM20 (taps wait for Save) are owed on the short form too.
#: Spec 050: IM21 (a beat after the passages) and IM22 (the story's Save -- S-005 ends it by the pause, S-006 by Save)
#: are owed on the short form too.
#: Spec 051: IM23 (asked on the first rung), IM24 (skipped honoured) and IM26 (speak or type) on the short form too;
#: IM25's recorded window and IM27's backfill are the full leg's.
#: Spec 058: IM28 (tap to hear) on the short form too -- it records from the same popup; IM29's Let-them-choose link is
#: the full leg's.
#: Spec 059: IM30 (the band's *Hear <name>*) on both -- each leg records, and Sent's band follows.
SHORT_FORM = ["IM1", "IM3", "IM4", "IM5", "IM6", "IM7", "IM9", "IM13", "IM14", "IM15", "IM16", "IM17", "IM19",
              "IM20", "IM21", "IM22", "IM23", "IM24", "IM26", "IM28", "IM30"]
#: Spec 059 FR-2: keel-web 088 removed *How it works* from Sent, so W1's replay -- the reading that held frame 2 to the
#: recorded face -- has no control to press. The first-visit walkthrough is unchanged and stays `leg_invite`'s.
W1_REPLAY_RETIRED = ("keel-web 088 FR-1 removed *How it works* from Sent (the page's pill *How this page works* "
                     "replaced it), so the walkthrough is not replayed and W1's frame-2 reading on a replay retires "
                     "(spec 059 FR-2); the first visit's W1 stays leg_invite's")


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


def _hear_wait(j) -> float:
    return HEAR_WAIT_REMOTE_S if getattr(j.stack, "is_remote", False) else HEAR_WAIT_S


def _hello(record: dict, face: str) -> str | None:
    """The face's `helloUrl` as `GET interviewer/faces` served it (contract 23)."""
    faces = ((record.get("faces") or {}).get("faces") or {}).get("faces") or []
    return next((f.get("helloUrl") for f in faces if f.get("code") == face), None)


def _persona(j) -> ivs.Persona:
    return ivs.Persona(j.page, j.recorder, j.web_base, patience=j.patience, guide=j.guide)


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
        if j.stack is not None:
            _score(j, record, require=[], note=REMOTE_MARKS)
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
        _hear_the_band(j, record)
        if not short:
            _screens_ready(j, wire, record)
        _the_recording(j, wire, record)
        if not short:
            _backfill(j, wire, record)
            _dry_run(j, wire, record)
        _ai_link(j, wire, record, answer=True)
        if not short:
            _choice_link(j, wire, record)
            _recorded_link(j, wire, record)
            _change_face(j, wire, record)
            _low_balance(j, wire, record, founder_id, run)
            _retry(j, wire, record)
        record["ledger"] = stack_ledger.rows(j.stack, founder_id, since=since)
        with j.recorder.step("interviewer: the ledger since Keel's door -- the stand-in grant, the recording's one "
                             "HOLD / SPEND pair, the change's, the stand-in low balance, the readings on arrival "
                             "(keel-cloud 095), and no other row",
                             party="stack", kind="assert") as h:
            reading_jobs = {x.get("inference_job_id") for x in record["ledger"]
                            if x.get("kind") == "HOLD" and x.get("action") in marks.READ_ACTIONS
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
    _follow_up_record(j, record)
    # spec 048: the answer path's five are owed on the full leg whatever the record carries -- a walk that never went
    # back is a walk that failed to, not a mark left unmeasured (spec 051: and the follow-up's five)
    answer_path = ["IM14", "IM15", "IM16", "IM17", "IM18", "IM19", "IM20", "IM21", "IM22", "IM23", "IM24", "IM25",
                   "IM26", "IM27", "IM28", "IM29", "IM30"]
    require = SHORT_FORM if short else [m for m, _, _ in marks.MARKS if m in _owed(record) or m in answer_path]
    _score(j, record, require=require)
    return record


def _follow_up_record(j, record: dict) -> None:
    """Spec 051: the follow-up's record for IM23-IM26 -- every text walk's (the corpus leg's, `j.follow_ups`), the AI
    link's and Try it yourself's twin; the AI link's windows; the story's boxes (`j.speak`)."""
    if record.get("follow_up_ai") is None:
        return
    record["follow_up"] = {"text": list((getattr(j, "follow_ups", None) or {}).values()),
                           "ai": record["follow_up_ai"], "try": (record.get("dry_run") or {}).get("follow_up")}
    record["follow_up_windows"] = {"windows": ((record["follow_up_ai"].get("walk") or {}).get("windows") or []),
                                   "full": not record.get("short"), "page_cap_ms": _page_cap(j)}
    if getattr(j, "speak", None):
        record["speak"] = dict(j.speak)


def _page_cap(j) -> int | None:
    """keel-web's own two minutes (`answerPath.ts` `FOLLOW_UP_RECORD_CAP_MS`), read off the checkout the stack serves:
    the seam shortened the silent window, so the real cap is held here (and on the wire, `maxSeconds` 120)."""
    path = Path(j.stack.keel_web) / "src" / "lib" / "answerPath.ts"
    m = re.search(r"FOLLOW_UP_RECORD_CAP_MS\s*=\s*([\d_]+)", path.read_text(encoding="utf-8")) if path.is_file() \
        else None
    return int(m.group(1).replace("_", "")) if m else None


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
    with j.recorder.step("interviewer: STAND-IN (call 148) -- the founder on Keel's door with a fresh grant of 2,000 "
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
                         "NOT_RECORDED; the four faces with their stills and hellos, Livia preselected, the change price 400; "
                         "a face not on the list, and a retired one (Judy), is refused FACE_UNKNOWN and charges "
                         "nothing", party="founder", kind="assert") as h:
        _, view = wire("GET", "/interviewer")
        _, faces = wire("GET", "/interviewer/faces")
        rows_before, balance_before = _rows(j, record), wire.credits()
        unknown, unknown_body = wire("POST", "/interviewer/face", {"face": "BOB"}, ok=(422,))
        # spec 058 FR-1: a code keel-cloud 110 retired is a face not on the list
        retired, retired_body = wire("POST", "/interviewer/face", {"face": fake.RETIRED[0]}, ok=(422,))
        record["faces"] = {"view": view, "faces": faces, "unknown": {"status": unknown, "body": unknown_body,
                                                                     "ledger_rows_added": _rows(j, record) - rows_before,
                                                                     "balance_after": wire.credits()},
                           "retired": {"face": fake.RETIRED[0], "status": retired, "code": retired_body.get("code")}}
        h.record_assert({"status": "NOT_RECORDED", "face": None, "faces": list(fake.FACES),
                         "preselected": fake.PRESELECTED, "changePrice": fake.CHANGE_PRICE,
                         "unknown": fake.FACE_UNKNOWN,
                         "retired": {"face": fake.RETIRED[0], "status": 422, "code": fake.FACE_UNKNOWN},
                         "helloUrl": [fake.hello_path(f) for f in fake.FACES]}, record["faces"])
        assert view.get("status") == "NOT_RECORDED" and view.get("face") is None, view
        assert [f.get("code") for f in faces.get("faces") or []] == list(fake.FACES), faces
        assert [f.get("name") for f in faces.get("faces") or []] == [fake.FACE_NAMES[f] for f in fake.FACES], faces
        assert all(f.get("previewUrl") == fake.preview_path(f.get("code")) for f in faces.get("faces") or []), faces
        assert all(f.get("helloUrl") == fake.hello_path(f.get("code")) for f in faces.get("faces") or []), faces
        assert faces.get("preselected") == fake.PRESELECTED and faces.get("changePrice") == fake.CHANGE_PRICE, faces
        assert unknown_body.get("code") == fake.FACE_UNKNOWN == retired_body.get("code"), (unknown_body, retired_body)
        assert record["faces"]["unknown"]["ledger_rows_added"] == 0 and wire.credits() == balance_before

    with j.recorder.step(f"interviewer: the founder picks {fake.FACE_NAMES[FIRST_FACE]} -- the first recording "
                         "starts RECORDING at once (0 of N until the clips are composed), one charge, nothing shown",
                         party="founder", kind="assert") as h:
        balance_before = wire.credits()
        persona = _persona(j)
        persona.sent(j.project_id)
        before = persona.wait_state("NOT_RECORDED")
        pressed = persona.record(FIRST_FACE, hear_s=_hear_wait(j))
        status, view = pressed["status"], pressed["body"]
        # spec 058 FR-2 (IM28): the tap that picked the face played her hello in the card
        record["hear_face"] = {**(pressed.get("hear") or {}), "hello": _hello(record, FIRST_FACE),
                               "sent": pressed["sent"]}
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
    with j.recorder.step(f"interviewer (S1): while RECORDING the persona line names {fake.FACE_NAMES[FIRST_FACE]}, "
                         "recording, a bar and k of N clips; Try it yourself greyed *recording*; *Send text-only "
                         "links*; Send more greys the AI interviewer and Let them choose *recording*", party="founder",
                         kind="assert") as h:
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
    lit and *Send links*; Send more offers *AI interviewer · {face}*; W1 replayed names the face in frame 2; L1 revisited
    draws the carousel with the first face checked. None of them shows a price but the one action (IM2)."""
    persona = _persona(j)
    name = fake.FACE_NAMES[FIRST_FACE]
    with j.recorder.step("interviewer (S2 / S3): READY in place -- *Recorded today at hh:mm.* and *Change who asks · "
                         f"400 AI credits*; Try it yourself lit, *Send links*; Send more offers *AI interviewer · {name}* "
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
    with j.recorder.step("interviewer (W1, spec 059 FR-2): the replay reading retires -- keel-web 088 removed *How it "
                         "works* from Sent, and no control of that name is left on the page", party="founder",
                         kind="assert") as h:
        drawn = {"retired": W1_REPLAY_RETIRED, "how_it_works": persona.how_it_works()}
        record["screens_drawn"]["W1"] = drawn
        h.record_assert({"how_it_works": 0}, drawn)
        assert drawn["how_it_works"] == 0, drawn
    with j.recorder.step("interviewer (L1, FR-002): the lock's last screen revisited on Keel's door -- *Who asks the "
                         "questions*, the four faces, one checked -- and no price on it", party="founder",
                         kind="assert") as h:
        l1 = persona.l1_again(j.project_id)
        record["screens"]["L1"] = l1["text"]
        record["screens_drawn"]["L1"] = l1
        h.record_assert({"faces": list(fake.FACES), "checked": 1, "price words": []},
                        {**l1, "price words": marks.PRICE_WORD.findall(l1["text"])})
        assert l1["faces"] == list(fake.FACES) and len(l1["checked"]) == 1, l1
        assert not marks.PRICE_WORD.search(l1["text"]), l1["text"]
    with j.recorder.step("interviewer (keel-web 070, DRIFT #87 closed): L1 revisited after the lock checks the face "
                         f"that was recorded -- {fake.FACE_NAMES[FIRST_FACE]} -- not the preselected "
                         f"{fake.FACE_NAMES[fake.PRESELECTED]}", party="founder", kind="assert") as h:
        h.record_assert({"checked": [FIRST_FACE]}, {"checked on L1": l1["checked"]})
        assert l1["checked"] == [FIRST_FACE], l1["checked"]
    persona.sent(j.project_id)


def _hear_the_band(j, record: dict) -> None:
    """IM30 (keel-web 088 FR-2): on Sent, once the first recording is READY, the who-asks band's *Hear <name> · 5 s*
    plays her hello in the band's circle to its end and the still returns (the wait 20 s locally, the 90 s navigation
    timeout on the remote profile); on the guide journey Sent's order and counts are read again with the band drawn
    (G15, G17)."""
    from evals import corpus_scenario                         # noqa: PLC0415 - corpus_scenario reads this leg's record
    persona = _persona(j)
    with j.recorder.step(f"interviewer (IM30, keel-web 088 FR-2): the who-asks band's Hear "
                         f"{fake.FACE_NAMES[FIRST_FACE]} · 5 s plays her hello in the band and the still returns",
                         party="founder", kind="assert") as h:
        persona.sent(j.project_id)
        persona.wait_state("READY")
        heard = persona.hear_band(wait_s=_hear_wait(j))
        view = j.get(j.project("/interviewer")) or {}
        record["hear_band"] = {**heard, "face": FIRST_FACE, "hello": (view.get("face") or {}).get("helloUrl"),
                               "retired": FIRST_FACE in fake.RETIRED}
        h.record_assert({"words": f"{ivs.HEAR_PREFIX}{fake.FACE_NAMES[FIRST_FACE]} · 5 s", "ended": True,
                         "hello": fake.hello_path(FIRST_FACE), "still back": True}, record["hear_band"])
    corpus_scenario.sent_reading(j, "after the first recording")


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
    record["tries_served"] = tries
    _framing_lines(j, record, tries)
    _follow_up_clips(j, record, tries)


def _follow_up_clips(j, record: dict, tries: dict) -> None:
    """Spec 051 (keel-cloud 103 FR-6), IM27's record and a plain assertion: every role's set holds one FOLLOW_UP clip
    per rung its link walks (the served `followUps[]`: five on a B2B practitioner's link, three on the decision-maker's,
    every rung a B2C link serves), each saying *One last thing.* and the registry's spoken wording, DONE -- and the
    served `clips.followUp` names exactly those rungs."""
    sets = fake.role_sets(record["recording"])
    roles = {}
    for link, served in tries.items():
        want = [f.get("dimension") for f in served.get("followUps") or []]
        spoken_words = {f.get("dimension"): f.get("spoken") for f in served.get("followUps") or []}
        clips = [{"itemId": c.get("itemId"), "script": c.get("script"), "status": c.get("status")}
                 for c in sets.get(link) or [] if c.get("kind") == "FOLLOW_UP"]
        roles[link] = {"want": want, "spoken": spoken_words, "clips": clips,
                       "served": sorted(((served.get("interviewer") or {}).get("clips") or {}).get("followUp") or {})}
    record["follow_up_clips"] = {"roles": roles, "full": not record.get("short")}
    with j.recorder.step("interviewer (keel-cloud 103 FR-6): every role holds one FOLLOW_UP clip per rung its link "
                         "walks -- One last thing. and the rung's spoken wording, DONE -- and serves them by rung",
                         party="stack", kind="assert") as h:
        h.record_assert({link: {"rungs": r["want"], "script": "One last thing. {spoken}"} for link, r in roles.items()},
                        roles)
        for link, r in roles.items():
            # keel-cloud 118: a rung may carry a second *#also* clip (its deciding line's other half); it rides beside
            # the rung's own clip, on a rung the link walks, DONE -- and is not a rung of its own.
            rung_clips = [c for c in r["clips"] if "#also" not in (c["itemId"] or "")]
            also = [c for c in r["clips"] if "#also" in (c["itemId"] or "")]
            assert r["want"] and [c["itemId"] for c in rung_clips] == r["want"], (link, r)
            assert all(c["script"] == fake.follow_up_script(fake.rung(c["itemId"])[3]) and c["status"] == "DONE"
                       for c in rung_clips), (link, r["clips"])
            assert all(c["itemId"].split("#")[0] in r["want"] and c["status"] == "DONE"
                       and c["script"].startswith("One last thing.") for c in also), (link, also)
            assert all(r["spoken"][d] == fake.rung(d)[3] for d in r["want"]), (link, r["spoken"])
            assert r["served"] == sorted(r["want"]), (link, r["served"])


def _framing_words(served: dict, role: dict) -> dict[str, dict]:
    """Spec 050 FR-1 (keel-cloud 101): what each passage of a role must say, from the interview its link serves -- the
    opening whole; the problem passage whole (`{topic} That's the problem. ...`, part 1's items with the gate); the
    idea passage's opening and close (the reveal's three lines between are IM4's), its count part 2's items on the full
    link and every served item on the decision-maker's."""
    commercial = served.get("kind") == "COMMERCIAL_LINK"
    counts = {int(part["part"]): len(part["items"]) for part in role["parts"]}
    out = {"OPENING": {"whole": fake.opening(served.get("founderFirstName"), commercial)}}
    if 1 in counts:
        out["PROBLEM"] = {"whole": fake.problem_passage(served.get("topic") or "", counts[1])}
    if 2 in counts or commercial:
        n = sum(counts.values()) if commercial else counts[2]
        out["SOLUTION"] = {"starts": fake.SOLUTION_OPENING, "ends": fake.solution_close(n)}
    return out


def _says(script: str, want: dict) -> bool:
    script = script or ""
    return (script == want["whole"]) if "whole" in want else (
        script.startswith(want["starts"]) and script.endswith(want["ends"]))


def _framing_lines(j, record: dict, tries: dict) -> None:
    """Spec 050 FR-1, a plain assertion on what keel-cloud stored: every role's opening, problem and idea passages say
    101's framing lines (`harness/interviewer_fake.py`, copied from `PassageComposer`)."""
    with j.recorder.step("interviewer (keel-cloud 101): every role's opening says whose idea it is and the route, the "
                         "problem and the idea passages close on Take a moment and the count", party="stack",
                         kind="assert") as h:
        sets = fake.role_sets(record["recording"])
        out = {}
        for link, served in tries.items():
            want = _framing_words(served, record["roles"][link])
            have = {c.get("kind"): c.get("script") for c in sets.get(link) or [] if c.get("kind") in want}
            out[link] = {kind: {"want": w, "said": have.get(kind), "ok": _says(have.get(kind), w)}
                         for kind, w in want.items()}
        record["framing"] = out
        h.record_assert({link: {k: "101's words" for k in v} for link, v in out.items()}, out)
        bad = {link: [k for k, v in kinds.items() if not v["ok"]] for link, kinds in out.items()}
        assert out and not any(bad.values()), {link: {k: out[link][k] for k in ks} for link, ks in bad.items() if ks}


def _backfill(j, wire: _Wire, record: dict) -> None:
    """Spec 050 FR-5 (keel-cloud 101 FR-2): a recording in the words from before 101 re-renders its opening, problem
    and idea passages at no charge on the first read, the old clips serving until the new are stored. The stack cannot
    record in old words any more, so it is seeded -- STAND-IN 4, the stored scripts of those clips put back to the old
    words (`stack.ledger.stand_in_old_words`) -- and the first read is the founder's Try it yourself (`GET interviewer/
    try/{roleId}`, 101 judgement call 4: the same `backfill` a stranger's link read runs). Then: one new clip per role
    and kind, stored with today's words, the old ids gone from the set and from what the next read serves, the
    recording READY throughout, and no ledger row.

    Spec 051 FR-8 (keel-cloud 103 FR-6), on the same read: the recording is also made one from before 103 -- STAND-IN 5,
    its FOLLOW_UP clips taken out (`stack.ledger.stand_in_no_follow_ups`) -- so the first read serves `clips.followUp`
    `{}` and queues one line per rung per role at no charge; then each rung's clip is stored again, DONE, in the same
    words (*One last thing.* and the registry's spoken wording), and served."""
    rec = record["recording"]
    today = {c["id"]: c for c in rec.get("clips") or [] if c.get("kind") in ("OPENING", "PROBLEM", "SOLUTION")}
    old = {cid: fake.before_101(c["kind"], c["script"]) for cid, c in today.items()}
    follow = {(c["role"], c["itemId"]): c for c in rec.get("clips") or [] if c.get("kind") == "FOLLOW_UP"}
    with j.recorder.step("interviewer: STAND-IN -- the stored recording's opening, problem and idea passages put back "
                         "to the words from before keel-cloud 101, and its follow-up clips taken out (a recording "
                         "from before keel-cloud 103)", party="stack", kind="protocol") as h:
        seeded = stack_ledger.stand_in_old_words(j.stack, j.project_id, old)
        removed = stack_ledger.stand_in_no_follow_ups(j.stack, j.project_id)
        h.record_wire({"clips": {cid: (today[cid]["role"], today[cid]["kind"]) for cid in old},
                       "follow-ups": sorted(f"{r}:{d}" for r, d in follow)},
                      {"seeded": seeded, "old words": old, "follow-ups taken out": removed})
        assert seeded == len(old) and old, (seeded, old)
        assert removed == len(follow) and follow, (removed, sorted(follow))
    with j.recorder.step("interviewer (keel-cloud 101 FR-2, 103 FR-6): the first read re-renders the passages in "
                         "today's words and stores each rung's follow-up again, at no charge -- one new clip per role "
                         "and kind, the old clips gone once the new are stored, READY throughout, no ledger row",
                         party="founder", kind="assert") as h:
        rows_before = _rows(j, record)
        roles = _role_ids(j)
        served_before = {link: wire("GET", f"/interviewer/try/{rid}")[1] for link, rid in roles.items()}
        statuses, swapped, followed, waited = [], {}, {}, 0.0
        while waited <= 90 * j.patience:
            stored = stack_ledger.recording(j.stack, j.project_id).get("recording") or {}
            statuses.append(stored.get("status"))
            clips = stored.get("clips") or []
            swapped = {}
            for cid, c in today.items():
                same = [x for x in clips if x.get("role") == c["role"] and x.get("kind") == c["kind"]]
                swapped[cid] = {"role": c["role"], "kind": c["kind"], "now": [(x.get("id"), x.get("status"))
                                                                              for x in same],
                                "ok": len(same) == 1 and same[0].get("id") != cid and same[0].get("status") == "DONE"
                                and same[0].get("script") == c["script"]}
            followed = {}
            for (role, dim), c in follow.items():
                same = [x for x in clips if x.get("role") == role and x.get("kind") == "FOLLOW_UP"
                        and x.get("itemId") == dim]
                followed[f"{role}:{dim}"] = {"now": [(x.get("id"), x.get("status")) for x in same],
                                             "ok": len(same) == 1 and same[0].get("id") != c["id"]
                                             and same[0].get("status") == "DONE"
                                             and same[0].get("script") == c["script"]}
            if all(v["ok"] for v in swapped.values()) and all(v["ok"] for v in followed.values()):
                break
            time.sleep(2)
            waited += 2
        served_after = {link: wire("GET", f"/interviewer/try/{rid}")[1] for link, rid in roles.items()}
        refs = {link: {slot: (((v.get("interviewer") or {}).get("clips") or {}).get(slot) or {}).get("clipId")
                       for slot in ("opening", "problem", "solution")} for link, v in served_after.items()}
        refs_before = {link: {slot: (((v.get("interviewer") or {}).get("clips") or {}).get(slot) or {}).get("clipId")
                              for slot in ("opening", "problem", "solution")} for link, v in served_before.items()}
        still_old = sorted({cid for link in refs.values() for cid in link.values() if cid in today})
        fu_before = {link: sorted((((v.get("interviewer") or {}).get("clips") or {}).get("followUp") or {}))
                     for link, v in served_before.items()}
        fu_after = {link: sorted((((v.get("interviewer") or {}).get("clips") or {}).get("followUp") or {}))
                    for link, v in served_after.items()}
        fu_want = {link: sorted(d for r, d in follow if r == link) for link in roles}
        record["backfill"] = {"seeded": len(old), "swapped": swapped, "statuses": sorted(set(statuses)),
                              "waited_s": waited, "served_before": refs_before, "served_after": refs,
                              "ledger_rows_added": _rows(j, record) - rows_before,
                              "follow_ups": {"taken_out": removed, "stored": followed, "served_before": fu_before,
                                             "served_after": fu_after, "want": fu_want}}
        h.record_assert({"swapped": {cid: True for cid in today}, "statuses": ["READY"], "served old ids": [],
                         "ledger rows added": 0, "follow-ups": {"served before": {k: [] for k in fu_want},
                                                                "stored": {k: True for k in followed},
                                                                "served after": fu_want}},
                        {**record["backfill"], "served old ids": still_old})
        assert all(v["ok"] for v in swapped.values()), swapped
        assert all(v["ok"] for v in followed.values()), followed
        assert set(statuses) == {"READY"}, statuses
        assert not still_old, refs
        assert all(v == [] for v in fu_before.values()), fu_before
        assert fu_after == fu_want, (fu_after, fu_want)
        assert record["backfill"]["ledger_rows_added"] == 0, record["backfill"]
    if record.get("follow_up_clips") is not None:
        record["follow_up_clips"]["backfill"] = {**record["backfill"]["follow_ups"],
                                                 "statuses": record["backfill"]["statuses"],
                                                 "ledger_rows_added": record["backfill"]["ledger_rows_added"]}


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
        clips = len(_all_clips(player.get("clips") or {})) + sum(
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
        stores = [w for w in drawn["writes"] if w not in drawn["reads"]]
        assert ivs.TRY_NOTHING_STORED in drawn["done"]["text"] and not stores, drawn
        assert drawn["first"]["question"] and drawn["videos"] == 1, drawn
        # keel-web 072 on the dry run: the mic tested, the answer read by the founder's own classify route and held
        assert drawn["mic"]["after"]["mic_heard"] == ivs.mic_heard("hello"), drawn["mic"]
        assert ivs.HELD in drawn["hold"]["status"] and drawn["hold"]["went_on"], drawn["hold"]
        # keel-web 075 FR-4: End's screen says the microphone is off, and nothing listens
        assert drawn["mic_off"]["shown"] and drawn["mic_off"]["text"] == ivs.MIC_OFF, drawn["mic_off"]
        assert drawn["mic_off"]["listening"] is False, drawn["mic_off"]
        assert any(r["url"].endswith(f"/v2/projects/{j.project_id}/interviewer/classify") for r in drawn["reads"]), \
            drawn["reads"]
    _dry_run_guard(j, wire, record, served)


def _dry_run_guard(j, wire: _Wire, record: dict, served: dict) -> None:
    """Spec 048 FR-6 / FR-3 on the founder's side: the same cases through the dry run's own classify route
    (`POST /v2/projects/{projectId}/interviewer/classify`, keel-cloud 099 T011) on Try it yourself's items -- the same
    validators, the founder's own routing (the fake for an eval founder), nothing stored; and an item the dry run does
    not serve is 422 ITEM_NOT_ON_FORM."""
    with j.recorder.step("classifier guard (spec 048 FR-6): the cases through Try it yourself's own classify route -- "
                         "no confident wrong answer, the corrections right, nothing stored; an item not on its form "
                         "422 ITEM_NOT_ON_FORM", party="founder", kind="assert") as h:
        items = guard.served_items(served)

        def post(body: dict) -> tuple[int, dict]:
            status, got = j.call("POST", j.project("/interviewer/classify"), body, ok=(200, 409, 422))
            return status, got if isinstance(got, dict) else {}

        before = _counts(j, wire, record)
        report = guard.run(post, items)
        refused, refusal = j.call("POST", j.project("/interviewer/classify"),
                                  {"itemId": "not-an-item-of-this-form", "heard": "yes"}, ok=(422,))
        after = _counts(j, wire, record)
        summary = report.summary()
        record["dry_run_guard"] = {**report.to_json(), "foreign": {"status": refused, "body": refusal},
                                   "before": before, "after": after}
        h.record_assert({"wrong": 0, "refused": 0, "foreign": 422, "before == after": True},
                        {k: v for k, v in summary.items()} | {"foreign": {"status": refused, "body": refusal},
                                                              "before": before, "after": after})
        assert not report.refused and not report.wrong, summary
        assert all(v == "right" for v in report.corrections.values()), report.corrections
        assert (refusal.get("code") if isinstance(refusal, dict) else None) == "ITEM_NOT_ON_FORM", refusal
        assert before == after, (before, after)


def _dry_run_on_screen(j) -> dict:
    """keel-web 069 FR-007 and 072 on the founder's own page: *Try it yourself* on the specialists' card, *Test your
    mic* ("hello"), *Start the interview* (the opening plays on the one `<video>`), the first question answered aloud
    through the seam and **held** -- the walkthrough's frame of the hold photographed -- then End: *Nothing was
    stored.*, and the page posted nothing but the answer path's reads (the founder's own `interviewer/classify`, which
    store nothing; keel-cloud 099 T011)."""
    j.context.add_init_script(ivs.SPEECH_SEAM)
    j.context.add_init_script(ivs.FLOW_TIMELINE)
    persona = _persona(j)
    persona.sent(j.project_id)
    persona.try_it(j.project_id, _labels(j)[vs.LINK_PRIMARY])
    # the button navigates inside the app; the seam's init script runs on a document's load, so the dry run's own
    # route is loaded once more (same URL) before anything is said
    j.page.reload(wait_until="load")
    player = ivs.Player(j.page, j.recorder, party="founder", patience=j.patience)
    try:
        with player.step("founder tries the interview: Test your mic, Start the interview, one answer aloud and held, "
                         "End") as h:
            try:
                j.page.get_by_test_id("ai-intro").wait_for(state="visible", timeout=30_000)
                player.requests.clear()
                mic = player.mic_test("hello")
                player.start()
                player.wait_phase("listening")
                stage = player.stage()
                first = player.sheet()
                player.wait_ear()
                player.say("yes", True)
                player.wait_status(ivs.HELD)
                h.add_screenshot(player.screenshot("try-hold"))     # the walkthrough's frame: the hold
                hold = player.hold()
                where = player.stage()["where"]
                player.end()                                   # the dry run stops at End (069 FR-007)
                done = player.done()
                mic_off = player.mic_off()                     # keel-web 075 FR-4: the dry run's done screen too
            except Exception:
                h.add_screenshot(player.screenshot("try-stuck"))
                h.record_wire({"stuck": True}, player.where_it_stood())
                raise
            h.add_screenshot(player.screenshot("try-done"))
            posts = [r for r in player.requests if r["method"] != "GET"]
            return {"mark": stage["mark"], "first": first, "pilot_where": where, "done": done, "writes": posts,
                    "videos": stage["videos"], "mic": mic, "hold": hold, "mic_off": mic_off,
                    "reads": [r for r in posts if marks.READS.search(r["url"].split("?")[0])]}
    finally:
        j.page.remove_listener("request", player._keep)


def _send_link(j, fmt: str, person: str) -> dict:
    """A link made on Sent's *Send more* (keel-web 069 S3): the format picked, *Someone I know*, the name, *Make their
    link* -- the batch keel-web received and the link it drew."""
    persona = _persona(j)
    primary = next(t for t in (j.get(j.project("/persona")) or {}).get("respondentTypes") or []
                   if not t.get("commercialLink"))
    sent = iv.Interviews(j.page, j.recorder, j.web_base, patience=j.patience, guide=j.guide)
    about = f"{primary.get('label')}, asked about one real time."
    persona.sent(j.project_id)
    made = sent.send_someone(j.project_id, _labels(j)[vs.LINK_PRIMARY], person, about, fmt=fmt)
    if made.get("retried"):
        # runs/DRIFT.md #88, RESOLVED by keel-web 070: a link refused 409 concurrency (an answer read on arrival moved the
        # project behind Sent) is read again and sent once more, silently -- the popup never shows the server's words.
        with j.recorder.step("interviewer (keel-web 070, DRIFT #88 closed): Send more's link was refused 409 "
                             "concurrency behind an arrival reading and keel-web sent it once more on the new "
                             "revision, silently -- made, and no server sentence drawn", party="founder") as h:
            first = made["retried"][0]
            h.record_assert({"retry": 201, "drawn": "no 'expected at revision'"},
                            {"first": first, "status": made["status"], "drawn": made.get("drawn")})
            assert made["status"] == 201, made
            assert "expected at revision" not in (made.get("drawn") or ""), made.get("drawn")
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
        own = {c.get("clipId") for c in _all_clips(clips)} | {
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
                   for c in _all_clips(clips)), clips
        assert part["status"] == 206 and whole["status"] == 200 and foreign["status"] == 404, record["range"]
    j.tokens["interviewer:ai"] = made["token"]
    record["served_interview"] = interview
    _classifier_guard(j, wire, record, made, interview)
    if not record.get("short"):
        _dry_run_follow_up(j, wire, record, interview, made["token"])
    if answer:
        _answer_ai_on_screen(j, wire, record, made, interview)


def _on_the_try(answers: list[dict], link: dict, tried: dict) -> list[dict]:
    """A link's answers carried onto Try it yourself's own ids (the dry run's interview is the same questions under
    the founder's ids): each item by its dimension, each option by its label."""
    link_items = {i["itemId"]: i for part in link.get("parts") or [] for i in part.get("items") or []}
    try_items = {i.get("dimension"): i for part in tried.get("parts") or [] for i in part.get("items") or []}
    out = []
    for a in answers:
        item = link_items.get(a.get("itemId")) or {}
        mine = try_items.get(item.get("dimension")) or {}
        if not mine:
            continue
        by_label = {o["label"]: o["optionId"] for o in mine.get("options") or []}
        adv_label = {x["label"]: x["id"] for x in mine.get("advantages") or []}
        labels = {o["optionId"]: o["label"] for o in item.get("options") or []}
        adv = {x["id"]: x["label"] for x in item.get("advantages") or []}
        moved = {**a, "itemId": mine.get("itemId")}
        if "optionIds" in a:
            moved["optionIds"] = [by_label[labels[o]] for o in a["optionIds"]]
        if "advantageIds" in a:
            moved["advantageIds"] = [adv_label[adv[o]] for o in a["advantageIds"]]
        out.append(moved)
    return out


def _dry_run_follow_up(j, wire: _Wire, record: dict, interview: dict, token: str) -> None:
    """Spec 051 FR-6 (keel-cloud 103's founder twin, `POST /v2/projects/{projectId}/interviewer/follow-up`): Try it
    yourself's follow-up, on the wire -- the AI link's person's answers carried onto the dry run's own ids are asked the
    harness's rung with the harness's text, and the rung's clip on the founder's own clip route (206 to a Range); a
    person owed nothing is 204; nothing is stored (no invitation, response, pilot or ledger row). The dry run's screen
    is walked to its first question and End (spec 050), not to its follow-up (judgement call 7)."""
    # read again: the backfill (stand-in 5) stored the follow-up clips anew since the recording was first read
    _, tried = wire("GET", f"/interviewer/try/{_role_ids(j)[vs.LINK_PRIMARY]}")
    person, owed, _ = _ai_person(j, interview, token)
    clear = next(p for p in j.people if p.link == vs.LINK_PRIMARY and p.recency
                 and vs.follow_up_question(j.entry, p.picks, p.link, interview, token) is None)
    with j.recorder.step("interviewer (keel-cloud 103): Try it yourself's follow-up on the founder's twin route -- the "
                         f"harness's rung ({owed['dimension']}) and text with the rung's clip on the founder's route, "
                         "204 for a person owed nothing, nothing stored", party="founder", kind="assert") as h:
        before = _counts(j, wire, record)
        asked, got = j.call("POST", j.project("/interviewer/follow-up"),
                            {"answers": _on_the_try(person.response(token)["answers"], interview, tried)}, ok=(200,))
        none, nothing = j.call("POST", j.project("/interviewer/follow-up"),
                               {"answers": _on_the_try(clear.response(token)["answers"], interview, tried)},
                               ok=(204, 200))
        clip = (got or {}).get("clip") or {}
        fetched = wire.clip(clip.get("url") or "", "bytes=0-99") if clip.get("url") else {}
        after = _counts(j, wire, record)
        want_clip = ((((tried.get("interviewer") or {}).get("clips") or {}).get("followUp") or {})
                     .get(owed["dimension"]) or {}).get("clipId")
        out = {"owed": owed, "status": asked, "body": got, "clear": {"person": clear.person, "status": none},
               "clip": fetched, "want_clip": want_clip, "before": before, "after": after}
        record["dry_run"] = {**record.get("dry_run", {}), "follow_up": out}
        h.record_assert({"status": 200, "dimension": owed["dimension"], "text": owed["text"], "clip": 206,
                         "clear": 204, "before == after": True}, out)
        assert got.get("dimension") == owed["dimension"] and got.get("text") == owed["text"], got
        assert clip.get("clipId") == want_clip and (clip.get("url") or "").startswith(
            f"/v2/projects/{j.project_id}/interviewer/clips/"), (clip, want_clip)
        assert fetched.get("status") == 206, fetched
        assert none == 204, (none, nothing)
        assert before == after, (before, after)


def _classifier_guard(j, wire: _Wire, record: dict, made: dict, interview: dict) -> None:
    """Spec 048 FR-3: the spoken-answer cases (`harness/classifier_cases.py`; 170 since spec 049, keel-cloud 100's
    `readaloud` group among them, held to the same bar and counted on its own) carried onto this AI link's own items
    and sent to the stranger's `POST /v2/i/{token}/interview/classify` -- keel-cloud 099's FakeClassifier, which every
    eval founder gets and the stack runs for everyone (no key) -- before the link is answered: no confident wrong
    answer, the corrections asked come back right, nothing refused, and nothing stored (the link still unanswered)."""
    with j.recorder.step("classifier guard (spec 048 FR-3): the spoken-answer cases carried onto this AI link's items "
                         "and sent to POST /v2/i/{token}/interview/classify -- keel-cloud 099's FakeClassifier: no "
                         "confident wrong answer, every correction asked right, nothing refused, nothing stored",
                         party="participant", kind="assert") as h:
        served = guard.served_items(interview)

        def post(body: dict) -> tuple[int, dict]:
            response = _participant(j, "POST", made["token"], "/interview/classify", body)
            return response.status_code, _json_of(response)

        report = guard.run(post, served)
        _, register = wire("GET", "/invitations")
        row = next((r for r in register.get("invitations") or [] if r.get("invitationId") == made["invitationId"]),
                   {})
        record["classifier_guard"] = {**report.to_json(), "served": [s.shape for s in served],
                                      "link_after": row.get("status")}
        summary = report.summary()
        h.record_assert({"wrong": 0, "refused": 0, "corrections": "right where asked", "link": "not ANSWERED"},
                        {k: v for k, v in summary.items() if k not in ("wrong cases", "refused cases")}
                        | {"wrong cases": summary["wrong cases"], "refused cases": summary["refused cases"],
                           "link": row.get("status")})
        assert not report.refused, summary["refused cases"]
        assert not report.wrong, summary["wrong cases"]
        assert all(v == "right" for v in report.corrections.values()), report.corrections
        assert summary["asked"] >= len([c for c in guard.all_cases() if c.item == "gate"]), summary
        assert summary["groups"].get("readaloud", {}).get("asked"), summary["groups"]
        assert not summary["groups"]["readaloud"]["wrong"], summary["groups"]["readaloud"]
        assert row.get("status") != "ANSWERED", row


def _person_for_the_link(j):
    """The **last** corpus person keel-cloud reads (a gate yes with a story) -- composed, never generated (spec 043
    call 133's rule). The last, because the two answers this leg makes are read on arrival on Keel's door, which has no
    key on this stack, so they stay unread; the leg reads them on the founder's own door before it ends (call 152),
    and the scripted executor repeats its last INTERPRET entry once its readings are spent -- this person's own."""
    names = {p.person for p in vs.readable_people(j.entry)}
    return [p for p in j.people if p.person in names][-1]


ORDINALS = ["first", "second", "third", "fourth", "fifth", "sixth"]
NUMBER_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
#: A cost total said aloud is said in the served currency's word (keel-cloud's FakeClassifier reads these).
CURRENCY_WORDS = {"USD": "dollars", "GBP": "pounds", "EUR": "euros"}


def _closed(answer: dict) -> dict:
    """An answer's closed fields, order taken out -- what the person answered, not how."""
    a = {k: v for k, v in answer.items() if k not in ("heard", "how", "itemId")}
    for key in ("optionIds", "advantageIds"):
        if key in a:
            a[key] = sorted(a[key])
    if a.get("costTotal") and a["costTotal"].get("value") is not None:
        a["costTotal"] = {**a["costTotal"], "value": round(float(a["costTotal"]["value"]), 4)}
    return a


def _shared_word(label: str, labels: list[str]) -> str | None:
    """One word of `label` that another label also carries (keel-cloud FakeClassifier's "one word in two labels" --
    "payroll" on the check's payroll item): said alone it is read unsure, never guessed."""
    for word in guard._sig(label):
        if sum(1 for other in labels if any(guard.same(word, w) for w in guard._sig(other))) >= 2:
            return word
    return None


def _status_or_on(player, question: str, *, timeout_s: float = 20) -> str | None:
    """After an answer: the held or the unsure status, or None when the sheet went on to another question first."""
    deadline = time.monotonic() + timeout_s * player.patience
    while time.monotonic() < deadline:
        status = player.status()
        if ivs.HELD in status or ivs.IS_THAT_RIGHT in status:
            return status
        if player.page.get_by_test_id("ai-done").count() or player.question() != question:
            return None
        time.sleep(0.05)
    raise AssertionError({"status never read": (ivs.HELD, ivs.IS_THAT_RIGHT), "it read": player.status(),
                          "phase": player.phase(), "question": question})


def _clearest(indexes: list[int], labels: list[str]) -> int:
    """Of `indexes`, the option whose words no other label holds and which holds no other label ("Yes" sits inside
    "Yes, if it was clearly worth it"): said whole, it is read with confidence. The first, when none is."""
    norm = [guard._norm(label) for label in labels]
    for i in indexes:
        if not any(j != i and (f" {norm[i]} " in f" {norm[j]} " or f" {norm[j]} " in f" {norm[i]} ")
                   for j in range(len(norm))):
            return i
    return indexes[0]


def _wait_next(player, question: str, *, timeout_s: float = 30) -> None:
    """The sheet on another question than `question` (or the end screen)."""
    deadline = time.monotonic() + timeout_s * player.patience
    while time.monotonic() < deadline:
        if player.page.get_by_test_id("ai-done").count() or (player.question() and player.question() != question):
            return
        time.sleep(0.1)
    raise AssertionError({"the sheet stayed on": question, "status": player.status(), "phase": player.phase()})


def _presses_between(player, start: float, end: float) -> list[dict]:
    return [e for e in player.timeline() if e.get("kind") == "press" and start <= (e.get("t") or 0) <= end]


def _now(player) -> float:
    return float(player.page.evaluate("() => performance.now()"))


def _question_words(question: str) -> str:
    """The question read aloud as a recogniser writes it down (no punctuation): up to its question mark, its closing
    "or not" left off -- "On your last delivery would an alert on mismatched deliveries have made things better" --
    which on the relative-advantage ask holds an option's own words (keel-web 072 lit that row as they arrived)."""
    head = re.split(r"[?]", question or "", maxsplit=1)[0]
    words = re.findall(r"[\w'’]+", head)
    if words[-2:] and [w.lower() for w in words[-2:]] == ["or", "not"]:
        words = words[:-2]
    return " ".join(words)


def _read_aloud_item(interview: dict, expected: dict) -> str | None:
    """Spec 049 judgement call 1: the question that carries the read-aloud step -- the "better" one (Relative
    advantage, `benefit_with_advantages`: its labels share words) where the person picks one of its options, else the
    first one-of question whose labels share a word, else the first one-of question."""
    answers = {a["itemId"]: a for a in expected.get("answers") or []}
    items = [i for part in interview.get("parts") or [] for i in part.get("items") or []]

    def one_of(i: dict) -> bool:
        a = answers.get(i.get("itemId")) or {}
        return (i.get("control") not in ("pick_two", "cost_total", "segmented_0_to_7", "number_with_unit")
                and len(a.get("optionIds") or []) == 1 and not a.get("chip"))

    labels = lambda i: [o["label"] for o in i.get("options") or []]  # noqa: E731
    for rule in (lambda i: i.get("control") == "benefit_with_advantages",
                 lambda i: any(_shared_word(label, labels(i)) for label in labels(i)),
                 lambda i: True):
        for i in items:
            if one_of(i) and rule(i):
                return i.get("itemId")
    return None


class _Walk:
    """What the stranger did on the stage, kept for the record: each sheet, the holds, the "Is that right?" turns,
    the way back, and how each item was answered (`how` the response must then carry)."""

    def __init__(self, player, interview: dict, expected: dict, *, story_by: str = "wait",
                 follow_up: dict | None = None):
        self.player = player
        self.gate = interview.get("gate") or {}
        self.items = {i.get("question"): i for part in interview.get("parts") or [] for i in part.get("items") or []}
        self.by_prompt = {i.get("advantagesPrompt"): i for i in self.items.values() if i.get("advantagesPrompt")}
        self.order = [i.get("itemId") for part in interview.get("parts") or [] for i in part.get("items") or []]
        self.by_id = {a["itemId"]: a for a in expected.get("answers") or []}
        self.expected = expected
        self.walked: list[dict] = []
        self.holds: list[dict] = []
        self.confirms: list[dict] = []
        self.back: dict | None = None
        self.veto: dict | None = None
        self.how: dict[str, str] = {}
        self.used = {"miss": False, "medium": False, "correction": False, "back": False, "veto": False,
                     "taps": False, "aloud": False}
        self._back_from: dict | None = None
        #: Spec 049: the read-aloud step (IM19), the pick-two by taps (IM20), the pilot's hold (IM14).
        self.aloud_item = _read_aloud_item(interview, expected)
        self.hear_out: dict | None = None
        self.taps: dict | None = None
        self.pilot_hold: dict | None = None
        #: Spec 050 FR-3 (keel-web 074 FR-2): the story ended by the pause (`wait`, S-005) or by its Save (`save`,
        #: S-006), and what it drew (IM22).
        self.story_by = story_by
        self.story_seen: dict | None = None
        #: Spec 051 FR-6 / FR-7: the one follow-up -- `{"line", "by": "browser" | "recorded"}` -- and what it drew.
        self.follow_up_plan = follow_up or {}
        self.follow_up_seen: dict | None = None
        self.recorded = False
        clips = (interview.get("interviewer") or {}).get("clips") or {}
        self.didnt_catch = (clips.get("didntCatch") or {}).get("clipId")
        self.pilot_clip = (clips.get("pilot") or {}).get("clipId")

    # ---- one spoken answer, held
    def held(self, entry: dict, said: str, *, item: dict | None = None, meant: str | None = None,
             labels: list[str] | None = None, keep_turn: bool = True) -> dict | None:
        """`said`, read with confidence and held. Where the read comes back unsure instead (keel-web 072 asks "Is that
        right?" for one word two labels hold, as "Yes" is in "Yes, if it was clearly worth it"), the turn is
        answered -- "yes" when the lit pick is the one meant, else the one meant by its place -- and kept as an "Is that
        right?" turn."""
        p = self.player
        start = _now(p)
        made = p.ear()["count"]
        p.wait_ear()
        question = p.question()
        p.say(said, True)
        now = _status_or_on(p, question)
        if now is None:
            # straight on, no hold: after a veto the same pick said again is taken as it stands (keel-web 072 call 5)
            entry["did"].append(f"said {said!r}, taken straight on")
            return None
        if ivs.IS_THAT_RIGHT in now and item is not None and meant is not None:
            turn = p.confirming()
            turn.update({"said": said, "meant": [meant], "item": item.get("dimension"), "unasked": True})
            p.wait_ear(newer_than=made)
            index = (labels or []).index(meant) if meant in (labels or []) else None
            answer_with = "yes" if turn["lit"] == [meant] or index is None else f"the {ORDINALS[index]} one"
            again = _now(p)
            p.say(answer_with, True)
            turn["answered"] = answer_with
            hold = _held_or_on(p, turn["question"])
            if hold is not None:
                hold.update({"said": answer_with, "presses": _presses_between(p, again, _now(p))})
                self.holds.append(hold)
            turn["held"] = _held_facts(hold)                # keel-web 074: the answer to it is held too
            _wait_next(p, turn["question"])
            turn.update({"went_on": True, "sent_item": item.get("itemId")})
            if keep_turn:                               # the Back move's first answer is changed later: not kept
                self.confirms.append(turn)
            entry["did"].append(f"said {said!r}: Is that right? -> {answer_with!r}")
            return None
        hold = p.hold()
        hold["said"] = said
        hold["presses"] = _presses_between(p, start, _now(p))
        self.holds.append(hold)
        entry["did"].append(f"said {said!r}, held")
        return hold

    def confirm(self, entry: dict, item: dict, said: str, answer_with: str | None, meant: str,
                labels: list[str]) -> bool:
        """`said`, meant to be read unsure: "Is that right?" -> `answer_with` said (None: the Yes chip tapped). The
        tier is the cloud's and the page's to decide, so a read that comes back sure instead is settled where it lands
        (held on the one meant, or "no" in the hold and the one meant by its place) and False is returned -- the move
        is tried again on a later question."""
        p = self.player
        made = p.ear()["count"]
        p.wait_ear()
        question = p.question()
        p.say(said, True)
        now = _status_or_on(p, question)
        if now is None or ivs.HELD in now:
            self._settle_held(entry, question, said, meant, labels)
            return False
        turn = p.confirming(timeout_s=1)
        turn.update({"said": said, "meant": [meant], "item": item.get("dimension")})
        # the "Is that right?" clip plays, then the window opens again on the same question
        p.wait_ear(newer_than=made)
        if answer_with is None:
            p.yes(by="tap")
            turn["answered"] = "tap Yes, that's it"
        else:
            p.say(answer_with, True)
            turn["answered"] = answer_with
        # keel-web 074 holds a yes like a confident answer: the hold's presses are counted from after the answer
        start = _now(p)
        # agreed: straight on, no hold; named again: re-read, and held when it is sure
        hold = _held_or_on(p, turn["question"])
        if hold is not None:
            hold.update({"said": answer_with, "presses": _presses_between(p, start, _now(p))})
            self.holds.append(hold)
        turn["held after"] = hold is not None
        turn["held"] = _held_facts(hold)
        _wait_next(p, turn["question"])
        turn["went_on"] = True
        turn["sent_item"] = item.get("itemId")
        self.confirms.append(turn)
        entry["did"].append(f"said {said!r}: Is that right? -> {turn['answered']!r}")
        return True

    def _settle_held(self, entry: dict, question: str, said: str, meant: str, labels: list[str]) -> None:
        """A read that was sure where an unsure one was meant: held on the one meant, it runs out; held on another,
        "no" in the hold and the one meant by its place."""
        p = self.player
        if p.question() != question:
            entry["did"].append(f"said {said!r}, taken straight on")
            return
        lit = [o["label"] for o in p.sheet()["options"] if o["checked"]]
        if lit == [meant]:
            hold = p.hold()
            hold.update({"said": said, "presses": []})
            self.holds.append(hold)
            entry["did"].append(f"said {said!r}, held (sure)")
        else:
            p.veto()
            p.wait_ear()
            p.say(f"the {ORDINALS[labels.index(meant)]} one", True)
            _held_or_on(p, question)
            entry["did"].append(f"said {said!r}, held on {lit}: 'no', then its place")
        _wait_next(p, question)

    # ---- the walk
    def run(self) -> list[dict]:
        p = self.player
        for _ in range(60):
            p.wait_phase("listening", "held", "confirming", timeout_s=40)
            p.wait_phase("listening", timeout_s=40)
            stage, sheet = p.stage(), p.sheet()
            entry = {"where": stage["where"], "question": sheet["question"],
                     "options": [o["label"] for o in sheet["options"]], "mark": stage["mark"], "did": [],
                     "back": _words_of(p, "ai-back")}
            self.walked.append(entry)
            q = sheet["question"]
            if self._back_from and q == self._back_from["next"]:
                self.go_back(entry)
                continue
            if stage["where"] == ivs.LAST_QUESTION:
                self.pilot(entry)
                return self.walked
            if stage["where"] == ivs.FOLLOW_UP_KICKER:
                self.follow_up(entry)
                continue
            condition = (self.gate or {}).get("condition") or {}
            if condition and q == condition.get("question"):
                # keel-cloud 120 (FR-2): the segment chip, asked before the gate question; the golden people are
                # inside the segment, so the answer is the first code the study lets in (YES / NO)
                self.held(entry, "yes" if (condition.get("inCodes") or ["YES"])[0] == "YES" else "no")
                continue
            if self.gate and q == self.gate.get("question"):
                self.held(entry, "yes" if self.expected.get("recency", True) is not False else "no")
                self.how[self.gate.get("itemId")] = "SPOKEN"
                continue
            after_gate = len(self.walked) > 1 and self.walked[-2]["question"] == self.gate.get("question")
            if self.gate and after_gate and q not in self.items and q not in self.by_prompt:
                self.story(entry)
                continue
            if q in self.by_prompt:
                self.advantages(entry, self.by_prompt[q])
                continue
            item = self.items.get(q)
            assert item, {"an unknown question on the sheet": q, "served": sorted(self.items)}
            self.answer(entry, item, sheet)
        raise AssertionError({"the interview never reached its pilot ask": self.walked[-3:]})

    def story(self, entry: dict) -> None:
        """The gate's story. keel-web 072: spoken -- never classified, the transcript is the answer. keel-web 074 FR-2
        (spec 050 FR-3): its window says *Take your time. Pause for a few seconds when you're done, or tap Save.*; *Save
        and next* (`ai-save`) is absent until a final is heard; then the story ends by the pause (`story_by` "wait":
        the gap runs, nothing pressed) or by Save (it is read at once) -- held either way, then on (IM22)."""
        p = self.player
        if self.expected.get("anchorChip"):
            p.tap_chip()
            entry["did"].append("tap the story's chip")
            _wait_next(p, entry["question"])
            return
        story = self.expected.get("story") or ""
        p.wait_ear()
        try:
            status_before = p.wait_status(ivs.STORY, timeout_s=5)
        except AssertionError:
            status_before = p.status()
        save_before = p.save_state()
        reads0 = len(p.classified)
        said_at = _now(p)
        p.say(story, True)
        waited = 0
        while waited < 3_000 * p.patience and not p.save_state()["shown"]:
            p.page.wait_for_timeout(50)
            waited += 50
        save_after = p.save_state()
        pressed_at = None
        if self.story_by == "save" and save_after["shown"]:
            pressed_at = _now(p)
            p.page.get_by_test_id("ai-save").click()
        hold = p.hold(timeout_s=20)
        _wait_next(p, entry["question"])
        events = p.timeline()
        held_at = next((e["t"] for e in events if e.get("kind") == "phase" and e.get("value") == "held"
                        and (e.get("t") or 0) >= said_at), None)
        self.story_seen = {
            "by": self.story_by, "question": entry["question"], "said": story, "status_before": status_before,
            "save_before": save_before, "save_after_final": save_after, "pressed": pressed_at is not None,
            "held": hold, "held_phase_seen": held_at is not None,
            "final_to_held_ms": round(held_at - said_at) if held_at is not None else None,
            "press_to_held_ms": round(held_at - pressed_at) if held_at is not None and pressed_at is not None else None,
            "presses": _presses_between(p, said_at, _now(p)), "classified": len(p.classified) - reads0,
            "next": p.question()}
        entry["did"].append("said the story, then " + ("Save and next" if pressed_at is not None else "the pause"))

    def advantages(self, entry: dict, item: dict) -> None:
        want = self.by_id[item["itemId"]].get("advantageIds") or []
        labels = {a["id"]: a["label"] for a in item.get("advantages") or []}
        said = "all of them" if want and sorted(want) == sorted(labels) else " and ".join(labels[a] for a in want)
        self.held(entry, said)
        _wait_next(self.player, entry["question"])

    def pilot(self, entry: dict) -> None:
        """The pilot ask -- *Last question*, never skipped: "yes" said, and (keel-web 073 FR-7) held like any confident
        answer -- the ring on Yes, *Finish* on the sheet -- and on by itself to the thanks: nothing pressed."""
        p = self.player
        start = _now(p)
        if self.recorded:
            # spec 051: the recogniser refused on the follow-up, so the page records every window since (keel-web
            # `listenFailed`); the pilot ask's "yes" is written down by the stack's fake transcriber
            box = ivs.SpeakBox(p.page)
            _wait_recording_since(p, _played_at(p, self.pilot_clip))
            box.speak()
            box.quiet()
        else:
            p.wait_ear()
            p.say("yes", True)
        hold = p.hold(timeout_s=30)
        done = p.done(timeout_s=20)
        hold.update({"said": "yes", "presses": _presses_between(p, start, _now(p)), "pilot": True,
                     "done": bool(done.get("text"))})
        self.holds.append(hold)
        self.pilot_hold = hold
        entry["did"].append("said yes: held, then the thanks with nothing pressed")

    # ---- spec 051: the one follow-up
    def follow_up(self, entry: dict) -> None:
        """Spec 051 FR-6 / FR-7 (keel-web 076 FR-9, keel-cloud 103 design §5.3): after the last item's hold the page
        asks the cloud's route; with a rung it plays the rung's FOLLOW_UP clip, the sheet says *One last thing* and the
        cloud's filled text, and the window is the story's -- never classified. Two windows, by way of *Back* from the
        first (076: Back from the follow-up lands on the last item; on again, the route is asked again):

        * **browser** (S-005): the first window said and ended by the pause, Back in its hold, the last item tapped
          again, the second said and ended by *Save and next* -- the response's `followUp` SPOKEN with the words;
        * **recorded** (S-006): the recogniser refuses on the first window (`not-allowed`, Chrome on iPhone), so the
          page records it -- a sound, then quiet: it ends 4 s after the last sound and is written down with
          `maxSeconds` 120; Back in its hold, the last item tapped again, the second window left silent: it runs to the
          cap (shortened through the seam, judgement call 2) and the question is skipped -- `skipped: true`, no
          didn't-catch, the pilot ask next."""
        p = self.player
        plan = self.follow_up_plan
        line = plan.get("line") or ""
        by = plan.get("by") or "browser"
        x = self.follow_up_seen = {"by": by, "windows": [], "line": line}
        last = self.order[-1]
        last_item = next(i for i in self.items.values() if i.get("itemId") == last)
        options = {o["optionId"]: o["label"] for o in last_item.get("options") or []}
        meant = [options[o] for o in (self.by_id.get(last) or {}).get("optionIds") or []]
        assert len(meant) == 1 and last_item.get("control") not in ("pick_two", "benefit_with_advantages"), \
            {"the last item is answered again by one tap": last_item.get("dimension"), "meant": meant}
        # the first window
        first = self._follow_up_window(entry, "first")
        if by == "recorded":
            first.update(self._recorded_take(first))
        else:
            first.update(self._browser_take(line, "wait"))
        x["windows"].append(first)
        # Back in its hold: the last item again, tapped again -- and the follow-up asked once more
        p.page.get_by_test_id("ai-back").click()
        _wait_question(p, last_item.get("question"))
        x["back"] = {"to": p.question(), "lit": p.checked(), "step": _step_of(p)}
        p.tap(meant[0])
        self.how[last] = "TAPPED"
        x["back"]["tapped"] = meant[0]
        deadline = time.monotonic() + 40 * p.patience
        while time.monotonic() < deadline and not (_step_of(p) == "followUp" and p.phase() == "listening"):
            p.page.wait_for_timeout(100)
        second = self._follow_up_window(entry, "second")
        if by == "recorded":
            second.update(self._silent_window(second))
        else:
            second.update(self._browser_take(line, "save"))
        x["windows"].append(second)
        entry["did"].append(f"the follow-up: {first.get('ended')}, Back and on, then {second.get('ended')}")

    def _follow_up_window(self, entry: dict, which: str) -> dict:
        """What one follow-up window drew as it opened: the sheet's step and where, the kicker, the question, the
        status, *Skip this one*, *Save and next* (none before words), Back -- and the clip that played into it."""
        p = self.player
        p.wait_phase("listening", timeout_s=40)
        sheet = p.sheet()
        events = p.timeline()
        plays = [e for e in events if e.get("kind") == "play"]
        return {"which": which, "opened_at": _now(p), "step": _step_of(p), "where": p.stage()["where"],
                "kicker": sheet["kicker"], "question": sheet["question"], "status": sheet["status"],
                "skip": _words_of(p, "ai-skip"), "save_before": p.save_state(), "back": _words_of(p, "ai-back"),
                "clip": plays[-1].get("clip") if plays else None, "classified_before": len(p.classified),
                "banner": sheet.get("banner")}

    def _browser_take(self, line: str, by: str) -> dict:
        """The browser path's window: the line said as one final, then the pause ("wait": nothing pressed, held after
        the gap) or *Save and next* at once ("save")."""
        p = self.player
        p.wait_ear()
        said_at = _now(p)
        p.say(line, True, look=False)
        waited = 0
        while waited < 3_000 * p.patience and not p.save_state()["shown"]:
            p.page.wait_for_timeout(50)
            waited += 50
        save_after = p.save_state()
        pressed_at = None
        if by == "save" and save_after["shown"]:
            pressed_at = _now(p)
            p.page.get_by_test_id("ai-save").click()
        status = p.wait_status(ivs.HELD, timeout_s=20)
        held_at = next((e["t"] for e in p.timeline() if e.get("kind") == "phase" and e.get("value") == "held"
                        and (e.get("t") or 0) >= said_at), None)
        sheet = p.sheet()
        out = {"path": "browser", "ended": by, "said": line, "save_after_final": save_after,
               "pressed": pressed_at is not None, "held_status": status, "heard": sheet["heard"],
               "final_to_held_ms": round(held_at - said_at) if held_at is not None else None,
               "press_to_held_ms": round(held_at - pressed_at) if held_at is not None and pressed_at else None,
               "presses": _presses_between(p, said_at, _now(p)), "classified": len(p.classified)}
        if by == "save":
            hold = p.hold(timeout_s=20)
            out["went_on"] = hold.get("went_on")
            _wait_where(p, ivs.LAST_QUESTION)
            out["next"] = p.stage()["where"]
        return out

    def _recorded_take(self, opened: dict) -> dict:
        """The recorded path's window (spec 051 FR-7): the recogniser refuses (`not-allowed`), the page records the
        window; a sound for a moment, then quiet -- the recording stops 4 s after the last sound and is written down
        (`transcribe`, `maxSeconds` 120); the transcript is held."""
        p = self.player
        box = ivs.SpeakBox(p.page)
        p.wait_ear()
        before = len(_record_stamps(p)["starts"])
        p.page.evaluate("() => window.__speechError('not-allowed')")
        self.recorded = True
        started = _wait_recording(p, before)
        sound_at = box.speak()
        quiet_at = box.quiet()
        status = p.wait_status(ivs.HELD, timeout_s=30)
        stamps = _record_stamps(p)
        stops = [t for t in stamps["stops"] if t >= quiet_at]
        sheet = p.sheet()
        return {"path": "recorded", "ended": "quiet", "recording_started": started, "sound_at": sound_at,
                "quiet_at": quiet_at, "stopped_at": stops[0] if stops else None,
                "quiet_to_stop_ms": round(stops[0] - quiet_at) if stops else None, "held_status": status,
                "heard": sheet["heard"], "banner": sheet.get("banner"), "classified": len(p.classified),
                "classified_before": opened.get("classified_before")}

    def _silent_window(self, opened: dict) -> dict:
        """The recorded path's silent window (spec 051 FR-7, IM24): nothing said; the recording runs to the cap
        (`followUpCapMs` through the seam) and the question is skipped -- no didn't-catch, the pilot ask next."""
        p = self.player
        started = _wait_recording_since(p, _played_at(p, opened.get("clip")))
        _wait_where(p, ivs.LAST_QUESTION, timeout_s=ivs.FOLLOW_UP_SEAM_CAP_MS / 1000 + 30)
        stamps = _record_stamps(p)
        cancels = [t for t in stamps["cancels"] if t >= started]
        catches = [e for e in p.timeline() if e.get("kind") == "play" and e.get("clip") == self.didnt_catch
                   and (e.get("t") or 0) >= started]
        return {"path": "recorded", "ended": "cap", "recording_started": started,
                "cancelled_at": cancels[0] if cancels else None,
                "ran_ms": round(cancels[0] - started) if cancels else None, "cap_ms": ivs.FOLLOW_UP_SEAM_CAP_MS,
                "didnt_catch_played": len(catches), "next": p.stage()["where"]}

    def read_aloud(self, entry: dict, item: dict, meant: str, labels: list[str]) -> None:
        """Spec 049 FR-2: the way people answer -- the question's first words read aloud as a final, then within a
        second the option's own words as a final. keel-web 073 lights nothing in the quiet gap after the first and reads
        the two as one utterance: one `classify` carrying both. The read is then settled where it lands (held on the
        one meant; held on another -> "no" and its place; "Is that right?" -> "yes" or its place), so the response
        still carries the person's own answer."""
        p = self.player
        p.wait_ear()
        question = p.question()
        first = _question_words(question)
        reads0 = len(p.classified)
        made = p.ear()["count"]
        start = _now(p)
        p.say(first, True)
        seen = p.hearing[-1] if p.hearing and p.hearing[-1]["said"] == first else None
        # the gap's own recogniser (the page restarts it after the first final's end): the answer goes to it
        waited = 0
        while waited < 1_000 and not (p.ear()["live"] and p.ear()["count"] > made):
            p.page.wait_for_timeout(50)
            waited += 50
        in_gap = [c["body"] for c in p.classified[reads0:] if (c["body"] or {}).get("itemId") == item["itemId"]]
        between = _now(p) - start
        p.say(meant, True, look=False)
        now = _status_or_on(p, question)
        reads = [c["body"] for c in p.classified[reads0:] if (c["body"] or {}).get("itemId") == item["itemId"]]
        lit = p.checked()
        self.hear_out = {"question": question, "item": item["itemId"], "dimension": item.get("dimension"),
                         "first": first, "second": meant, "between_ms": round(between), "after_first": seen,
                         "reads_in_gap": len(in_gap), "reads": [r.get("heard") for r in reads],
                         "landed": now, "lit": lit, "meant": meant}
        if now is None:
            entry["did"].append(f"read aloud {first!r}, then said {meant!r}: taken straight on")
        elif ivs.IS_THAT_RIGHT in now:
            turn = p.confirming()
            turn.update({"said": f"{first} {meant}", "meant": [meant], "item": item.get("dimension"), "aloud": True})
            p.wait_ear()
            answer_with = "yes" if turn["lit"] == [meant] else f"the {ORDINALS[labels.index(meant)]} one"
            p.say(answer_with, True)
            turn["answered"] = answer_with
            hold = _held_or_on(p, turn["question"])
            if hold is not None:
                hold.update({"said": answer_with, "presses": []})
                self.holds.append(hold)
            turn["held"] = _held_facts(hold)
            _wait_next(p, turn["question"])
            turn.update({"went_on": True, "sent_item": item.get("itemId")})
            self.confirms.append(turn)
            self.hear_out["settled"] = f"Is that right? -> {answer_with}"
            entry["did"].append(f"read aloud {first!r}, then said {meant!r}: Is that right? -> {answer_with!r}")
        else:
            self._settle_held(entry, question, f"{first} {meant}", meant, labels)
            self.hear_out["settled"] = "held" if lit == [meant] else f"held on {lit}: 'no', then its place"
            entry["did"].append(f"read aloud {first!r}, then said {meant!r}")
            return
        _wait_next(p, question)

    def tap_pick_two(self, entry: dict, item: dict, want: list[str], labels: list[str]) -> None:
        """Spec 049 FR-5 (keel-web 073 FR-6): a pick-two by taps. One tick: *Save and next* drawn and off, nothing goes
        on by itself for 1.5 s, no ring; a second: on; a third row tapped: ignored; Save: *Got it.*, the next question,
        `how` TAPPED."""
        p = self.player
        p.wait_ear()
        question = p.question()
        before = p.save_state()
        p.tap(want[0])
        p.page.wait_for_timeout(ivs.TAP_WAIT_MS)
        one = {**p.save_state(), "question_same": p.question() == question}
        p.tap(want[1])
        two = p.save_state()
        third = next((label for label in labels if label not in want), None)
        if third is not None:
            p.tap(third)
            p.page.wait_for_timeout(300)
        three = p.save_state()
        start = _now(p)
        p.page.get_by_test_id("ai-save").click()
        _wait_next(p, question)
        after = [st for st in p.statuses() if (st.get("t") or 0) >= start and st.get("question") == question]
        self.taps = {"question": question, "item": item["itemId"], "want": want, "before": before, "one": one,
                     "two": two, "third": {"tapped": third, **three}, "statuses_after_save": [st.get("status")
                                                                                         for st in after],
                     "next": p.question()}
        self.how[item["itemId"]] = "TAPPED"
        entry["did"].append(f"tapped {want[0]!r} (Save off), {want[1]!r} (Save on), Save and next")

    def go_back(self, entry: dict) -> None:
        """FR-6: from the next question, *Back* -- the previous question reopens with the (wrong) answer said there lit;
        the person's own is tapped, and the interview goes forward again."""
        p = self.player
        back = self._back_from
        self._back_from = None
        went = p.back(by="tap")
        p.tap(back["meant"])
        _wait_next(p, back["question"])
        self.back = {"from": back["next"], "question": back["question"], "button": went["button"], "to": went["to"],
                     "lit_on_return": went["lit"], "said_first": back["said"], "changed_to": back["meant"],
                     "forward": p.question(), "item": back["itemId"]}
        self.how[back["itemId"]] = "TAPPED"
        entry["did"].append(f"Back to {back['question']!r}, tapped {back['meant']!r}, forward again")

    def answer(self, entry: dict, item: dict, sheet: dict) -> None:
        p = self.player
        ans = self.by_id.get(item["itemId"]) or {}
        options = {o["optionId"]: o["label"] for o in item.get("options") or []}
        control = item.get("control")
        labels_shown = [o["label"] for o in sheet["options"]]
        if ans.get("chip"):
            p.tap_chip()
            entry["did"].append("tap the escape")
            self.how[item["itemId"]] = "TAPPED"
            _wait_next(p, entry["question"])
            return
        if control == "pick_two" and not self.used["taps"] and len(ans.get("optionIds") or []) == 2:
            # keel-web 073 FR-6: the first pick-two by taps -- a tick only ticks; *Save and next* finishes it (IM20)
            self.used["taps"] = True
            self.tap_pick_two(entry, item, [options[o] for o in ans["optionIds"]], labels_shown)
            return
        if control == "pick_two":
            self.held(entry, " and ".join(options[o] for o in ans.get("optionIds") or []))
            self.how[item["itemId"]] = "SPOKEN"
            _wait_next(p, entry["question"])
            return
        if ans.get("scale") is not None or ans.get("number") is not None:
            value = ans.get("scale") if ans.get("scale") is not None else ans.get("number")
            if not self.used["miss"]:
                p.wait_ear()
                p.say("31", True)                       # out of every range here: the didn't-catch clip
                # keel-web 073: read after the quiet gap -- wait for the miss itself, then the window opened again
                entry["missed"] = p.wait_missed()
                p.wait_ear(timeout_s=20)
                entry["did"].append("said 31 (a miss)")
                self.used["miss"] = True
            words = NUMBER_WORDS[int(value)] if str(value).isdigit() and int(value) < len(NUMBER_WORDS) else str(value)
            self.held(entry, f"about {words}")
            self.how[item["itemId"]] = "SPOKEN"
            _wait_next(p, entry["question"])
            return
        if ans.get("costTotal"):
            cost = ans["costTotal"]
            value = float(cost.get("value") or 0)
            currency = (item.get("costTotal") or {}).get("currency")
            word = "hours" if cost.get("mode") == "HOURS" else CURRENCY_WORDS.get(currency or "")
            if value.is_integer() and word:
                self.held(entry, f"{int(value)} {word}")
                self.how[item["itemId"]] = "SPOKEN"
            else:
                p.unit("HOURS" if cost.get("mode") == "HOURS" else "AMOUNT")
                p.fill_field(str(cost.get("value")))
                p.save()                                # typed words keep *Save and next*
                entry["did"].append(f"typed {cost.get('value')} into the field")
                entry["typed"] = {"itemId": item["itemId"], "value": str(cost.get("value"))}
                self.how[item["itemId"]] = "TYPED"
            _wait_next(p, entry["question"])
            return
        labels = [options[o] for o in ans.get("optionIds") or []]
        assert len(labels) == 1, {"item": item["dimension"], "answer": ans}
        meant = labels[0]
        index = labels_shown.index(meant)
        others = [i for i in range(len(labels_shown)) if i != index and i < len(ORDINALS)]
        last_item = self.order and item["itemId"] == self.order[-1]
        # keel-web 072 call 7: Back lands on a step's main ask and asks its follow-ups again -- the way back and the
        # veto are tried on a plain one-of question, never on benefit_with_advantages (its advantages follow)
        plain = control != "benefit_with_advantages"
        self.how[item["itemId"]] = "SPOKEN"
        if not self.used["aloud"] and self.aloud_item == item["itemId"]:
            # keel-web 073 / keel-cloud 100: the question's first words read aloud, then the answer (IM19)
            self.used["aloud"] = True
            self.read_aloud(entry, item, meant, labels_shown)
            return
        if not self.used["correction"] and len(labels_shown) >= 3 and index < len(ORDINALS) and others:
            # "the first one, wait, actually the third": the last correction wins, and a correction is read unsure
            # (keel-cloud 099 judgement call 8) -- "Is that right?" with the right one lit, then "yes"
            said = f"the {ORDINALS[others[0]]} one, wait, actually the {ORDINALS[index]}"
            self.used["correction"] = self.confirm(entry, item, said, "yes", meant, labels_shown)
            return
        if not self.used["back"] and others and not last_item and plain:
            # answered with another option's own words, held; Back from the next question changes it by a tap
            self.used["back"] = True
            wrong = labels_shown[_clearest(others, labels_shown)]
            self.held(entry, wrong, item=item, meant=wrong, labels=labels_shown, keep_turn=False)
            _wait_next(p, entry["question"])
            self._back_from = {"question": entry["question"], "next": p.question(), "meant": meant, "said": wrong,
                               "itemId": item["itemId"]}
            return
        shared = _shared_word(meant, labels_shown)
        if not self.used["medium"] and shared and index < len(ORDINALS):
            # one word two labels carry ("payroll"): "Is that right?" -> the person names theirs by its place
            self.used["medium"] = self.confirm(entry, item, shared, f"the {ORDINALS[index]} one", meant, labels_shown)
            return
        if not self.used["veto"] and plain:
            # a word of protest in the hold reopens the question; the option said again is held and goes on
            self.used["veto"] = True
            p.wait_ear()
            p.say(meant, True)
            if ivs.IS_THAT_RIGHT in p.wait_status(ivs.HELD, ivs.IS_THAT_RIGHT):
                # unsure, not held: no hold to protest in -- named by its place instead, and the veto tried later
                self.used["veto"] = False
                p.wait_ear()
                p.say(f"the {ORDINALS[index]} one", True)
                _held_or_on(p, entry["question"])
                _wait_next(p, entry["question"])
                entry["did"].append(f"said {meant!r}: unsure, then its place")
                return
            self.veto = p.veto()
            entry["did"].append(f"said {meant!r}, then 'no' in the hold")
            self.held(entry, meant, item=item, meant=meant, labels=labels_shown)
            _wait_next(p, entry["question"])
            return
        self.held(entry, meant, item=item, meant=meant, labels=labels_shown)   # the option's own words
        _wait_next(p, entry["question"])


def _step_of(player) -> str | None:
    """keel-web 076: the sheet's step (`ai-sheet[data-step]`: gate | item | followUp | pilot)."""
    sheet = player.page.get_by_test_id("ai-sheet")
    return sheet.first.get_attribute("data-step") if sheet.count() else None


def _wait_question(player, question: str | None, *, timeout_s: float = 20) -> None:
    deadline = time.monotonic() + timeout_s * player.patience
    while time.monotonic() < deadline and player.question() != question:
        time.sleep(0.05)
    assert player.question() == question, {"Back landed on": player.question(), "want": question}


def _wait_where(player, where: str, *, timeout_s: float = 30) -> None:
    deadline = time.monotonic() + timeout_s * player.patience
    while time.monotonic() < deadline and player.stage()["where"] != where:
        time.sleep(0.1)
    assert player.stage()["where"] == where, {"the stage never reached": where, "it reads": player.stage()}


def _record_stamps(player) -> dict:
    """The seam recorder's stamps (`harness/interviewer_screens.recorder_seam`)."""
    return player.page.evaluate("""() => ({ starts: (window.__recordStarts || []).slice(),
        stops: (window.__recordStops || []).slice(), cancels: (window.__recordCancels || []).slice() })""")


def _played_at(player, clip_id: str | None) -> float:
    """When `clip_id` last began to play on the stage (the timeline's `play`), or 0."""
    plays = [e.get("t") or 0 for e in player.timeline() if e.get("kind") == "play" and clip_id
             and e.get("clip") == clip_id]
    return plays[-1] if plays else 0.0


def _wait_recording_since(player, since: float, *, timeout_s: float = 20) -> float:
    """The first recording begun at or after `since` (a clip's play): when."""
    deadline = time.monotonic() + timeout_s * player.patience
    while time.monotonic() < deadline:
        starts = [t for t in _record_stamps(player)["starts"] if t >= since]
        if starts:
            return starts[0]
        time.sleep(0.05)
    raise AssertionError({"no recording began after": since, "stamps": _record_stamps(player),
                          "status": player.status()})


def _wait_recording(player, before: int, *, timeout_s: float = 20) -> float:
    """A recording begun after the `before`-th: when (`performance.now()`)."""
    deadline = time.monotonic() + timeout_s * player.patience
    while time.monotonic() < deadline:
        starts = _record_stamps(player)["starts"]
        if len(starts) > before:
            return starts[-1]
        time.sleep(0.05)
    raise AssertionError({"no recording began": _record_stamps(player), "status": player.status()})


def _held_or_on(player, question: str, *, timeout_s: float = 20) -> dict | None:
    """After an answer to "Is that right?": the question went on at once (agreed -- None), or the read was held."""
    deadline = time.monotonic() + timeout_s * player.patience
    while time.monotonic() < deadline:
        if player.page.get_by_test_id("ai-done").count() or player.question() != question:
            return None
        if ivs.HELD in player.status():
            return player.hold()
        time.sleep(0.1)
    raise AssertionError({"after Is that right? the sheet stayed": question, "status": player.status()})


def _held_facts(hold: dict | None) -> dict | None:
    """Spec 050 FR-4 (keel-web 074 FR-3): what the hold after an answer to *Is that right?* drew -- `data-phase` held,
    the ring, the lit row's `data-unsure` ("false" once agreed), the status."""
    if hold is None:
        return None
    return {k: hold.get(k) for k in ("phase", "ring", "unsure", "status", "lit", "went_on")}


def _words_of(player, testid: str) -> str | None:
    loc = player.page.get_by_test_id(testid)
    return " ".join((loc.first.text_content() or "").split()) if loc.count() else None


def _slot_clips(clips: dict) -> dict[str, dict]:
    """A player's one-clip slots (`opening`, `pilot`, ...) -- not `followUp`, which since keel-cloud 103 is a map of
    one clip per rung."""
    return {slot: c for slot, c in (clips or {}).items() if c and slot != "followUp"}


def _all_clips(clips: dict) -> list[dict]:
    """Every clip a player's `clips` carries: the slots and each rung's follow-up."""
    return list(_slot_clips(clips).values()) + list(((clips or {}).get("followUp") or {}).values())


def _clip_kinds(interview: dict) -> dict[str, str]:
    """A served interview's clip ids by what they say: the slots' names upper-cased (`opening` -> OPENING), an item's
    clip ITEM, its follow-up ITEM_MORE."""
    player = interview.get("interviewer") or {}
    kinds = {c.get("clipId"): re.sub(r"(?<!^)(?=[A-Z])", "_", slot).upper()
             for slot, c in _slot_clips(player.get("clips") or {}).items()}
    for clip in ((player.get("clips") or {}).get("followUp") or {}).values():
        kinds[clip.get("clipId")] = "FOLLOW_UP"                     # spec 051: one a rung, keyed by dimension
    for item in (player.get("items") or {}).values():
        if item.get("clip"):
            kinds[item["clip"].get("clipId")] = "ITEM"
        if item.get("more"):
            kinds[item["more"].get("clipId")] = "ITEM_MORE"
    return kinds


def _beats_seen(interview: dict, beats: list[dict], starts: dict) -> dict:
    """Spec 050 FR-2 (keel-web 075 FR-1), IM21's record: every beat the stage took, after which clip, how long, what it
    drew, and how many recognisers or recordings were started inside it; and the passages it is owed after (the served
    PROBLEM and SOLUTION clips, in the spoken order)."""
    kinds = _clip_kinds(interview)
    clips = (interview.get("interviewer") or {}).get("clips") or {}
    out = []
    for b in beats:
        t0, t1 = b.get("t0"), b.get("t1")
        inside = (lambda ts: sum(1 for t in ts or [] if t0 is not None and t >= t0 and (t1 is None or t <= t1)))
        out.append({**b, "after_kind": kinds.get(b.get("after")),
                    "ms": round(t1 - t0) if t0 is not None and t1 is not None else None,
                    "starts_in": inside(starts.get("speech")), "recordings_in": inside(starts.get("record"))})
    return {"beats": out, "expected": [k.upper() for k in ("problem", "solution") if clips.get(k)],
            "beat_ms": ivs.BEAT_MS}


def _mic_off_after_thanks(j, interview: dict, mic_off: dict, starts: dict, events: list[dict], whose: str) -> None:
    """Spec 050 FR-7 (keel-web 075 FR-4), a plain assertion once a link: after the thanks the done screen says
    *Microphone off* (`ai-mic-off`, `role=status`), the seam's recogniser no longer listens, and no recogniser was
    started after the thanks clip began."""
    thanks = (((interview.get("interviewer") or {}).get("clips") or {}).get("thanks") or {}).get("clipId")
    played = [e.get("t") for e in events if e.get("kind") == "play" and thanks and e.get("clip") == thanks]
    since = played[-1] if played else None
    after = [t for t in starts.get("speech") or [] if since is not None and t > since]
    with j.recorder.step(f"interviewer (keel-web 075 FR-4): after {whose} thanks the done screen says Microphone off "
                         "and nothing listens any more", party="participant", kind="assert") as h:
        h.record_assert({"ai-mic-off": ivs.MIC_OFF, "role": "status", "listening": False,
                         "recognisers started after the thanks": 0},
                        {**mic_off, "thanks played at": since, "recognisers started after the thanks": len(after)})
        assert mic_off["shown"] and mic_off["text"] == ivs.MIC_OFF and mic_off["role"] == "status", mic_off
        assert mic_off["listening"] is False, mic_off
        assert since is not None and not after, {"thanks": since, "started after": after}


def _answer_ai_on_screen(j, wire: _Wire, record: dict, made: dict, interview: dict) -> None:
    """keel-web 069 FR-008 and 072's answer path on the stranger's own page, through the speech seam (`vite --mode
    test`) with the classifier left real (the stack's FakeClassifier): the intro, *Test your mic* ("hello" -> *Heard:
    hello*), *Start the interview*, then every question as `_Walk` answers it -- no *That's my answer* anywhere, a
    confident read held and gone on by itself, "Is that right?" for a correction and for one word two labels carry,
    Back once, a word of protest once -- the pilot ask "yes" and *Finish*; then the one `POST response` keel-web sends:
    `format` AI_INTERVIEWER, `how` and `heard` on every answer as it was given, exactly the person's own answers (the
    changed one included), and the pilot's Yes counted."""
    person, owed, line = _ai_person(j, interview, made["token"])
    items = {i.get("dimension"): i for part in interview.get("parts") or [] for i in part.get("items") or []}
    recall = ((items.get("commercial.existing_sacrifice") or {}).get("costTotal") or {}).get("recallPeriod")
    expected = person.response(made["token"], recall)
    pilot_before = (j.get(j.project("/standings")) or {}).get("pilot") or {}
    stranger = j.browser.new_context()
    stranger.add_init_script(ivs.SPEECH_SEAM)
    by = "browser" if record.get("short") else "recorded"
    if by == "recorded":
        # spec 051 FR-7: the recorder the page falls back to, and the follow-up's cap shortened (judgement call 2)
        stranger.add_init_script(ivs.recorder_seam(follow_up_cap_ms=ivs.FOLLOW_UP_SEAM_CAP_MS))
    stranger.add_init_script(ivs.FLOW_TIMELINE)
    seen: dict = {}
    replies: list = []

    def keep(response) -> None:
        if response.request.method == "POST" and response.url.endswith(("/interview/response", "/interview/pilot",
                                                                        "/interview/classify")):
            seen.setdefault(response.url.rsplit("/", 1)[-1], []).append(
                {"status": response.status, "body": response.request.post_data_json})
        if response.request.method == "POST" and response.url.endswith(("/interview/follow-up",
                                                                        "/interview/transcribe")):
            replies.append(response)                     # read once the walk is over (never inside the handler)
    try:
        page = stranger.new_page()
        page.on("response", keep)
        player = ivs.Player(page, j.recorder, patience=j.patience)
        with player.step("the stranger answers the AI interviewer: the intro, Test your mic, Start the interview, every "
                         "question by voice (held, Is that right?, Back once, one read aloud first), a pick-two by taps "
                         "and Save, the pilot ask held and on by itself") as h:
            try:
                intro = player.open(made["url"])
                mic = player.mic_test("hello")
                h.add_screenshot(player.screenshot("ai-mic-tested"))
                player.start()
                walk = _Walk(player, interview, expected, story_by="wait" if record.get("short") else "save",
                             follow_up={"line": line, "by": by})
                walked = walk.run()
                done = player.done()
                asked = _replies(replies)
                mic_off = player.mic_off()
                h.add_screenshot(player.screenshot("ai-mic-off"))
                beats, starts = player.beats(), player.starts()
                events, statuses = player.timeline(), player.statuses()
                saw = player.saw_thats_my_answer()
                record["ai_flow"] = j.feedback["ai_flow"] = {
                    "events": events, "next_presses": sum(1 for e in events if e.get("kind") == "next"
                                                          and e.get("value") != ivs.FINISH),
                    "finish_presses": sum(1 for e in events if e.get("kind") == "next" and e.get("value") == ivs.FINISH)}
            except Exception:
                h.add_screenshot(player.screenshot("ai-stuck"))
                h.record_wire({"stuck": True}, player.where_it_stood())
                raise
            h.add_screenshot(player.screenshot("ai-done"))
    finally:
        stranger.close()
    record["mic_test"] = {**mic, "intro": intro}
    _consent_on_the_intro(j, interview, intro, "the AI link's")
    record["follow_up_ai"] = {"owed": owed, "line": line, "by": by, "asked": asked, "walk": walk.follow_up_seen,
                              "clips": ((interview.get("interviewer") or {}).get("clips") or {}).get("followUp"),
                              "followUps": interview.get("followUps")}
    record["beat"] = _beats_seen(interview, beats, starts)
    if walk.story_seen:
        record["story"] = walk.story_seen
    _mic_off_after_thanks(j, interview, mic_off, starts, events, "the AI link's")
    record["hold"] = {"holds": walk.holds, "veto": walk.veto, "statuses": statuses, "saw_thats_my_answer": saw,
                      "pilot": walk.pilot_hold, "finish_presses": record["ai_flow"]["finish_presses"]
                      + sum(1 for e in events if e.get("kind") == "press" and e.get("testid") == "ai-finish")}
    with j.recorder.step("interviewer (FR-008 / FR-H; keel-web 072): keel-web sent ONE response -- `format` "
                         "AI_INTERVIEWER, `how` and `heard` on every answer as it was given, exactly the person's own "
                         "answers (the one changed through Back included) -- the classifier asked for every spoken "
                         "closed answer, That's my answer never drawn, and after the pilot ask (*Last question*, never "
                         "skipped) one pilot write, counted in the overview's pilot", party="participant",
                         kind="assert") as h:
        responses, pilots = seen.get("response") or [], seen.get("pilot") or []
        classified = seen.get("classify") or []
        body = (responses[0] if responses else {}).get("body") or {}
        _, register = wire("GET", "/invitations")
        row = next((r for r in register.get("invitations") or [] if r.get("invitationId") == made["invitationId"]),
                   {})
        pilot_after = (j.get(j.project("/standings")) or {}).get("pilot") or {}
        sent = {a["itemId"]: _closed(a) for a in body.get("answers") or []}
        want = {a["itemId"]: _closed(a) for a in expected.get("answers") or []}
        top = {k: body.get(k) for k in ("recency", "story", "anchorChip") if k in expected}
        by_item = {a.get("itemId"): a for a in body.get("answers") or []}
        hows = {k: (by_item.get(k) or {}).get("how") for k in walk.how if k in by_item}
        typed = [{"itemId": w["typed"]["itemId"], "typed": w["typed"]["value"],
                  "how": (by_item.get(w["typed"]["itemId"]) or {}).get("how"),
                  "heard": (by_item.get(w["typed"]["itemId"]) or {}).get("heard")} for w in walked if w.get("typed")]
        if typed:
            # Spec 046 FM6 (keel-web 070, DRIFT #89 closed): a value typed into the field carries `heard`.
            record["typed_fields"] = j.feedback["typed_fields"] = typed
        for turn in walk.confirms:
            a = by_item.get(turn["sent_item"]) or {}
            options = {o["optionId"]: o["label"] for o in (next((i for i in items.values()
                                                                  if i.get("itemId") == turn["sent_item"]), {})
                                                            .get("options") or [])}
            turn["sent"] = [options.get(o) for o in a.get("optionIds") or []]
        if walk.back:
            a = by_item.get(walk.back["item"]) or {}
            options = {o["optionId"]: o["label"] for o in (next((i for i in items.values()
                                                                  if i.get("itemId") == walk.back["item"]), {})
                                                            .get("options") or [])}
            record["back"] = {**walk.back, "sent": [options.get(o) for o in a.get("optionIds") or []],
                              "sent_how": a.get("how")}
        record["confirm"] = {"turns": walk.confirms}

        def sent_labels(item_id: str) -> list[str | None]:
            a = by_item.get(item_id) or {}
            options = {o["optionId"]: o["label"] for o in (next((i for i in items.values()
                                                                  if i.get("itemId") == item_id), {})
                                                            .get("options") or [])}
            return [options.get(o) for o in a.get("optionIds") or []]

        # spec 049: the read-aloud step (IM19) and the pick-two by taps (IM20), held to what the response carried
        record["hear_out"] = {**(walk.hear_out or {"never": "no question carried the read-aloud step"}),
                              "hearing": player.hearing}
        if walk.hear_out:
            record["hear_out"]["sent"] = sent_labels(walk.hear_out["item"])
        if walk.taps:
            record["taps"] = {**walk.taps, "sent": sent_labels(walk.taps["item"]),
                              "sent_how": (by_item.get(walk.taps["item"]) or {}).get("how")}
        if record.get("story"):
            record["story"]["sent"] = body.get("story")                 # IM22: the response carries the story
        record["follow_up_ai"]["sent"] = body.get("followUp")
        record["ai_answers"] = {"body": body, "status": (responses[0] if responses else {}).get("status"),
                                "register_row": row, "by": "keel-web", "walked": walked, "intro": intro,
                                "done": done, "expected": expected, "how": {"want": walk.how, "sent": hows},
                                "classified": len(classified)}
        record["pilot"] = {**record.get("pilot", {}), "answered": "YES" if pilots and pilots[0]["status"] == 204 else None,
                           "before": pilot_before.get("optedIn"), "after": pilot_after.get("optedIn"),
                           "status": pilots[0]["status"] if pilots else None,
                           "asked": [w["where"] for w in walked][-1:]}
        spoken = [k for k, v in walk.how.items() if v == "SPOKEN" and k != (interview.get("gate") or {}).get("itemId")]
        h.record_assert({"responses": 1, "format": "AI_INTERVIEWER", "answers": want, "how": walk.how,
                         "top": {k: expected[k] for k in top}, "pilot": 204, "formatUsed": "AI_INTERVIEWER",
                         "That's my answer": "never in the DOM", "classify": f">= {len(spoken)} calls, all 200",
                         "intro": {"intro": "AI_INTERVIEWER", "heading": f"{fake.FACE_NAMES[FIRST_FACE]} will ask you"}},
                        {"responses": len(responses), "format": body.get("format"), "answers": sent, "how": hows,
                         "top": top, "pilots": pilots, "row": row, "intro": intro, "walked": walked,
                         "saw That's my answer": saw, "classify": [c["status"] for c in classified],
                         "statuses": [s.get("status") for s in statuses]})
        assert intro["intro"] == "AI_INTERVIEWER" and intro["buttons"] == ["start-talking"], intro
        assert intro["heading"].startswith(f"{fake.FACE_NAMES[FIRST_FACE]} will ask you"), intro
        assert len(responses) == 1 and responses[0]["status"] in (200, 201), responses
        assert body.get("format") == "AI_INTERVIEWER", body
        assert sent == want, {"sent": sent, "want": want}
        assert top == {k: expected[k] for k in top}, (top, expected)
        assert hows == {k: v for k, v in walk.how.items() if k in by_item}, {"sent": hows, "want": walk.how}
        assert all((by_item.get(k) or {}).get("heard") for k, v in walk.how.items()
                   if v == "SPOKEN" and k in by_item), {k: (by_item.get(k) or {}).get("heard") for k in walk.how}
        assert saw is False, "That's my answer (ai-answer) was drawn"
        assert len(classified) >= len(spoken) and all(c["status"] == 200 for c in classified), classified
        assert len(pilots) == 1 and pilots[0]["status"] == 204, pilots
        assert row.get("formatUsed") == "AI_INTERVIEWER" and row.get("status") == "ANSWERED", row
        assert all(w["mark"] == ivs.MARK for w in walked), [w["mark"] for w in walked]
    _follow_up_on_the_ai_link(j, record)
    _read_on_arrival(j, wire, record, made["invitationId"], "the AI link's")


def _ai_person(j, interview: dict, token: str):
    """Spec 051: the person who answers the AI link (`_person_for_the_link`, the last read) and the follow-up the
    harness's own walk owes them on it. Where their own picks owe none (01-countly's last reader holds up on every
    rung), their Commitment is answered *Yes, after trying it first* instead -- a support in `Compare`, so no standing
    moves, and the ladder's last rung against (design §2: it is asked too) -- so the short form has a follow-up to
    walk (judgement call 6). Returns (person, the owed question, the line they say)."""
    person = _person_for_the_link(j)
    owed = vs.follow_up_question(j.entry, person.picks, vs.LINK_PRIMARY, interview, token)
    if owed is None:
        # keel-cloud 118 (FR-1): the conditional yes is served only where the founder's list carries a smaller step
        # (01-countly's does not, so *Yes, after ... first* is not on the sheet); the other conditional yes, Adoption
        # friction's *Yes, if it was clearly worth it*, is a support as well (`Compare.supportingCodes`) and owes its
        # #also follow-up -- so no standing moves either way
        if vs.smaller_step(j.entry) is not None:
            person = vs.with_pick(person, "commercial.commitment", ["yes_after_trying"])
        else:
            person = vs.with_pick(person, "solution.adoption_friction", ["yes_if_worth_it"])
        owed = vs.follow_up_question(j.entry, person.picks, vs.LINK_PRIMARY, interview, token)
    assert owed is not None, {"no follow-up owed on the AI link": person.person}
    line = person.follow_up or vs.FOLLOW_UP_LINES[owed["dimension"]][0]
    return person, owed, line


def _replies(responses: list) -> list[dict]:
    """The follow-up route's and `transcribe`'s answers the page received, in order: what was sent and what came."""
    out = []
    for response in responses:
        try:
            got = response.json() if response.status == 200 else {}
        except Exception:  # noqa: BLE001 - a 204
            got = {}
        out.append({"route": response.url.rsplit("/", 1)[-1], "status": response.status,
                    "sent": response.request.post_data_json, "body": got})
    return out


def _consent_on_the_intro(j, interview: dict, intro: dict, whose: str) -> None:
    """Spec 051 FR-9, a plain assertion on the AI intro: the served consent line (keel-cloud 103, D17) is drawn, and
    the old door line is gone."""
    from evals.corpus_scenario import CONSENT_GONE, CONSENT_TEXT        # noqa: PLC0415 - the one copy of the line

    with j.recorder.step(f"interviewer (keel-cloud 103 FR-8, D17): {whose} intro says the name travels with the words "
                         "and may be quoted; Nothing here asks for your name is gone", party="participant",
                         kind="assert") as h:
        text = " ".join((intro.get("text") or "").split())
        h.record_assert({"served": CONSENT_TEXT, "drawn": True, "gone": CONSENT_GONE},
                        {"served": interview.get("consentText"), "intro": text})
        assert interview.get("consentText") == CONSENT_TEXT, interview.get("consentText")
        assert CONSENT_TEXT in text and CONSENT_GONE not in text, text


def _follow_up_on_the_ai_link(j, record: dict) -> None:
    """Spec 051 FR-6 / FR-7 (keel-web 076 FR-9, keel-cloud 103): what the AI link's follow-up did, held -- the route
    asked twice (once a pass of the last item) and both times on the harness's rung with the harness's text, the
    rung's FOLLOW_UP clip played into both windows (`clips.followUp[dimension]`, the route's own `clip`), the sheet's
    step `followUp` with *One last thing*, the story's status, *Skip this one*, no *Save and next* before words, nothing
    classified; the browser path's first window ended by the pause and its second by Save (the response SPOKEN with
    the words), or the recorded path's first window 4 s after the last sound (`transcribe` `maxSeconds` 120) and its
    second, silent, at the cap -- skipped, no didn't-catch, the pilot ask next."""
    x = record["follow_up_ai"]
    owed = x["owed"]
    clips = x.get("clips") or {}
    # keel-cloud 118: a conditional yes owes the rung's *#also* stem, served under its own clip key
    clip_key = owed["dimension"] + ("#also" if owed.get("also") else "")
    # the served `clips.followUp` map is keyed by dimension alone (no #also entry -- a wire gap noted in tasks.md), so
    # the #also clip is looked up in the stored recording by its item id; the route still serves it
    stored = {c.get("itemId"): c.get("clipId") or c.get("id")
              for c in ((record.get("recording") or {}).get("clips") or []) if isinstance(c, dict)}
    want_clip = (clips.get(clip_key) or {}).get("clipId") or stored.get(clip_key) \
        or (clips.get(owed["dimension"]) or {}).get("clipId")
    routes = [a for a in x.get("asked") or [] if a["route"] == "follow-up"]
    windows = (x.get("walk") or {}).get("windows") or []
    with j.recorder.step(f"interviewer (keel-cloud 103, keel-web 076): the AI link's follow-up on {owed['dimension']} "
                         f"-- the {x['by']} path, two windows by way of Back", party="participant", kind="assert") as h:
        if x["by"] == "browser":
            want_sent = {"dimension": owed["dimension"], "text": x["line"], "how": "SPOKEN", "skipped": False}
        else:
            want_sent = {"dimension": owed["dimension"], "skipped": True}
        h.record_assert({"routes": [{"status": 200, "dimension": owed["dimension"], "text": owed["text"]}] * 2,
                         "clip": want_clip, "windows": ["wait", "save"] if x["by"] == "browser" else ["quiet", "cap"],
                         "sent": want_sent}, x)
        assert len(routes) == 2 and all(r["status"] == 200 for r in routes), routes
        for r in routes:
            assert r["body"].get("dimension") == owed["dimension"] and r["body"].get("spoken") == owed["spoken"], r
            assert r["body"].get("text") == owed["text"], {"route": r["body"].get("text"), "harness": owed["text"]}
            assert (r["body"].get("clip") or {}).get("clipId") == want_clip, (r["body"].get("clip"), want_clip)
        assert len(windows) == 2, windows
        for w in windows:
            assert w["step"] == "followUp" and w["where"] == ivs.FOLLOW_UP_KICKER, w
            assert w["kicker"] == ivs.FOLLOW_UP_KICKER and w["question"] == owed["text"], w
            assert w["status"] == ivs.STORY and w["skip"] == ivs.FOLLOW_UP_SKIP, w
            assert w["save_before"]["shown"] is False and w["clip"] == want_clip, w
            assert w.get("classified", w["classified_before"]) == w["classified_before"], w     # never classified
        if x["by"] == "browser":
            first, second = windows
            assert first["ended"] == "wait" and not first["presses"] and not first["pressed"], first
            assert second["ended"] == "save" and second["pressed"] and second["went_on"], second
            assert second["final_to_held_ms"] is not None and second["final_to_held_ms"] < marks.GAP_FREE_MS, second
        else:
            first, second = windows
            transcribed = [a for a in x.get("asked") or [] if a["route"] == "transcribe"
                           and (a["sent"] or {}).get("itemId") == routes[0]["body"].get("itemId")]
            first["transcribed"] = transcribed
            assert len(transcribed) == 1 and transcribed[0]["status"] == 200, transcribed
            assert transcribed[0]["sent"].get("maxSeconds") == 120, transcribed[0]["sent"]
            assert first["quiet_to_stop_ms"] is not None and abs(first["quiet_to_stop_ms"] - ivs.SILENCE_FREE_MS) <= 500, \
                first
            assert FAKE_TRANSCRIPT in (first["heard"] or "").lower(), first
            assert second["ran_ms"] is not None and second["ran_ms"] >= 0.95 * second["cap_ms"], second
            assert second["didnt_catch_played"] == 0 and second["next"] == ivs.LAST_QUESTION, second
        assert x.get("sent") == want_sent, {"sent": x.get("sent"), "want": want_sent}


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
                                                  for x in rows if x.get("action") in marks.READ_ACTIONS]})
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
    with j.recorder.step("interviewer (keel-cloud 104, spec 052; was 096's brief): the readings wrote no themes; the "
                         "founder comes back (GET overview on the session the agent is bound to) and every THEMES job "
                         "started -- at most one a failing dimension -- ends on this journey's own runtime",
                         party="founder", kind="assert") as h:
        briefs = lambda: [i for i in (j.get(f"/v2/inference-interactions?project_id={j.project_id}") or [])  # noqa: E731
                          if i.get("screen") == "THEMES"]
        before = briefs()
        j.get(j.project("/overview"))
        deadline = time.monotonic() + 60 * j.patience
        after = briefs()
        ended = {"APPLIED", "RESULT_INVALID", "DOMAIN_REFUSED", "JOB_FAILED", "APPLY_ERROR", "ABANDONED"}
        seen = {x.get("interaction_id") for x in before}
        quiet = time.monotonic() + 10 * j.patience          # none due: no THEMES appears, and none is waited for
        while time.monotonic() < deadline:
            fresh = [b for b in after if b.get("interaction_id") not in seen]
            if (fresh and all(b.get("status") in ended for b in fresh)) or (not fresh and time.monotonic() > quiet):
                break
            time.sleep(1)
            after = briefs()
        new = [b.get("status") for b in after if b.get("interaction_id") not in seen]
        record["themes_on_return"] = {"before": [b.get("status") for b in before], "new": new}
        h.record_assert({"new THEMES": "each one that ends (a lost race's retries aside); none when no failing "
                                       "dimension's answers moved"}, record["themes_on_return"])
        assert all(s in ended or s == "STATE_CONFLICT" for s in new), new


def _choice_intro_on_screen(j, url: str) -> dict:
    """A Let-them-choose link's intro on the stranger's own page (P0c): both offered. Read only -- the answer in
    writing goes on the wire (call 154: the text player behind *Answer in writing* is the text link's, walked on every
    journey already)."""
    stranger = j.browser.new_context()
    try:
        page = stranger.new_page()
        player = ivs.Player(page, j.recorder, patience=j.patience)
        with player.step(f"the stranger opens a Let-them-choose link: Talk to {fake.FACE_NAMES[FIRST_FACE]}, or "
                         "Answer in writing -- and taps *Hear* (keel-web 087 FR-3)") as h:
            drawn = player.open(url)
            h.add_screenshot(player.screenshot("choice-intro"))
            drawn["hear"] = player.hear(wait_s=_hear_wait(j))
            h.add_screenshot(player.screenshot("choice-intro-heard"))
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
        owed = vs.follow_up_question(j.entry, person.picks, vs.LINK_PRIMARY, interview, made["token"])
        stored = stack_ledger.stored_follow_ups(j.stack, j.project_id).get(made["invitationId"])
        # spec 058 FR-3 (IM29): *Hear <name>* on this intro played her hello, the choice buttons enabled throughout
        record["hear_intro"] = {**(intro.pop("hear", None) or {}), "face": FIRST_FACE,
                                "hello": _hello(record, FIRST_FACE)}
        record["choice"] = {"made": made, "formats": interview.get("formats"),
                            "player": bool(interview.get("interviewer")), "response": posted.status_code,
                            "register_row": row, "intro": intro,
                            "follow_up": {"owed": owed, "sent": None, "stored": stored}}
        h.record_assert({"format": "CHOICE", "formats": ["TEXT", "AI_INTERVIEWER"], "player": True,
                         "formatUsed": "TEXT"}, record["choice"])
        assert made["format"] == "CHOICE" and interview.get("formats") == ["TEXT", "AI_INTERVIEWER"], record["choice"]
        assert interview.get("interviewer") and posted.status_code in (200, 201), record["choice"]
        assert row.get("format") == "CHOICE" and row.get("formatUsed") == "TEXT", row
        assert intro["intro"] == "CHOICE" and intro["buttons"] == ["choice-talk", "choice-write"], intro
        # keel-cloud 103: a response that owes a follow-up and sends none is stored skipped
        assert owed and stored == {"dimension": owed["dimension"], "text": None, "how": None, "skipped": True}, stored
    _read_on_arrival(j, wire, record, made["invitationId"], "the Let-them-choose link's")


def _recorded_link(j, wire: _Wire, record: dict) -> None:
    """keel-cloud 099 FR-4 / FR-7 (contract 18) on the wire: an AI link answered from the recorded path -- the page
    keel-web draws where a browser cannot listen sends each window's recording to `POST /v2/i/{token}/interview/answer`.
    A recording under the silence floor comes back `heard` "", unclear, reason silence (nothing transcribed); one over it
    is written down by the stack's fake transcriber and read by its fake classifier, `how` RECORDED; and the one
    response, its spoken answers `how` RECORDED with what was heard, is accepted and stored as answered."""
    import base64                                                             # noqa: PLC0415

    with j.recorder.step("interviewer (keel-cloud 099 FR-4 / FR-7): an AI link answered from the recorded path -- "
                         "silence under the floor is read as silence and never transcribed, a recording over it is "
                         "transcribed (the fake) and classified, and a response with how RECORDED is accepted",
                         party="participant", kind="assert") as h:
        # the revision off GET persona, not GET overview: on Keel's keyless door a read of the overview would start the
        # stale brief (keel-cloud 096 FR-D), fail it, and leave this staleness "tried" -- no brief on the return later
        revision = int((j.get(j.project("/persona")) or {}).get("revision") or 0)
        status, made = wire("POST", "/invitations/batch", {
            "expectedRevision": revision, "respondentType": vs.LINK_PRIMARY, "format": "AI_INTERVIEWER",
            "people": [{"personName": RECORDED_PERSON}]})
        link = (made.get("links") or [{}])[0]
        token = _token(link.get("url") or "")
        interview = _json_of(_participant(j, "GET", token, "/interview"))
        gate = interview.get("gate") or {}

        def answer(audio: bytes) -> dict:
            response = _participant(j, "POST", token, "/interview/answer", {
                "itemId": gate.get("itemId"), "audio": base64.b64encode(audio).decode("ascii"),
                "mimeType": "audio/webm", "language": j.entry.market["language"]})
            return {"status": response.status_code, **_json_of(response)}

        silence, sounded = answer(SILENT_WEBM), answer(SOUNDED_WEBM)
        person = _person_for_the_link(j)
        items = {i.get("dimension"): i for part in interview.get("parts") or [] for i in part.get("items") or []}
        recall = ((items.get("commercial.existing_sacrifice") or {}).get("costTotal") or {}).get("recallPeriod")
        body = dict(person.response(token, recall), format="AI_INTERVIEWER")
        body["answers"] = [{**a, "how": "RECORDED", "heard": _heard_for(a, interview)} for a in body["answers"]]
        follow_up = _recorded_follow_up(j, token, interview, person, body)
        posted = _participant(j, "POST", token, "/interview/response", body)
        _, register = wire("GET", "/invitations")
        row = next((r for r in register.get("invitations") or [] if r.get("invitationId") == link.get("invitationId")),
                   {})
        stored = stack_ledger.stored_follow_ups(j.stack, j.project_id).get(link.get("invitationId"))
        follow_up["stored"] = stored
        record["recorded"] = {"made": {"status": status, "invitationId": link.get("invitationId")},
                              "silence": silence, "sounded": sounded, "status": posted.status_code,
                              "response": _json_of(posted), "body": body, "register_row": row,
                              "follow_up": follow_up}
        h.record_assert({"silence": {"status": 200, "heard": "", "unclear": True, "reason": "silence"},
                         "sounded": {"status": 200, "heard": FAKE_TRANSCRIPT}, "response": "201",
                         "register": {"status": "ANSWERED", "formatUsed": "AI_INTERVIEWER"}},
                        {k: v for k, v in record["recorded"].items() if k != "body"})
        assert status == 201 and token, made
        assert silence["status"] == 200 and silence.get("heard") == "" and silence.get("unclear") is True, silence
        assert silence.get("reason") == "silence", silence
        assert sounded["status"] == 200 and sounded.get("heard") == FAKE_TRANSCRIPT, sounded
        assert sounded.get("picks") == ["Yes"] and sounded.get("confidence") == "high", sounded
        assert posted.status_code in (200, 201), record["recorded"]["response"]
        assert row.get("status") == "ANSWERED" and row.get("formatUsed") == "AI_INTERVIEWER", row
        # spec 051 (keel-cloud 103): the follow-up, recorded and written down in its two-minute window, then stored
        want = {"dimension": follow_up["owed"]["dimension"], "text": FAKE_TRANSCRIPT, "how": "RECORDED",
                "skipped": False}
        assert follow_up["route"]["status"] == 200 and follow_up["route"]["body"].get("dimension") == want[
            "dimension"], follow_up["route"]
        assert follow_up["route"]["body"].get("text") == follow_up["owed"]["text"], follow_up["route"]
        assert follow_up["over"]["status"] == 422 and follow_up["heard"]["status"] == 200, follow_up
        assert follow_up["heard"].get("text") == FAKE_TRANSCRIPT, follow_up["heard"]
        assert follow_up["wrong"]["status"] == 422 and follow_up["wrong"]["body"].get("code") == "SHAPE_MISMATCH", \
            follow_up["wrong"]
        assert body.get("followUp") == want and stored == want, {"sent": body.get("followUp"), "stored": stored}
    _recorded_pilot(j, record, token, interview, link.get("invitationId"))
    _read_on_arrival(j, wire, record, link.get("invitationId"), "the recorded link's")


def _recorded_follow_up(j, token: str, interview: dict, person, body: dict) -> dict:
    """Spec 051 FR-6 on the wire, the recorded link's follow-up in the page's order (keel-web 076 FR-9): the answers to
    `POST .../interview/follow-up` (the harness's rung and text), the window's recording to `transcribe` against the
    follow-up's own id -- refused 422 at `maxSeconds` 90 (60 or 120 only), written down at 120 (the stack's fake hears
    "yes") -- a response naming another rung refused 422 SHAPE_MISMATCH (the cloud walks the ladder too), and the
    words put on `body` as `followUp` RECORDED."""
    import base64                                                             # noqa: PLC0415

    owed = vs.follow_up_question(j.entry, person.picks, vs.LINK_PRIMARY, interview, token)
    assert owed is not None, {"the recorded link's person is owed no follow-up": person.person}
    route = _participant(j, "POST", token, "/interview/follow-up", {"answers": body["answers"]})
    asked = _json_of(route)

    def transcribe(seconds: int) -> dict:
        got = _participant(j, "POST", token, "/interview/transcribe", {
            "itemId": asked.get("itemId"), "audio": base64.b64encode(SOUNDED_WEBM).decode("ascii"),
            "mimeType": "audio/webm", "language": j.entry.market["language"], "maxSeconds": seconds})
        return {"status": got.status_code, **_json_of(got)}

    over, heard = transcribe(90), transcribe(120)
    other = next(r for r in fake.walks(vs.LINK_PRIMARY, vs.is_b2b(j.entry)) if r != owed["dimension"])
    wrong = _participant(j, "POST", token, "/interview/response", {
        **body, "followUp": {"dimension": other, "text": heard.get("text") or "x", "how": "RECORDED"}})
    body["followUp"] = {"dimension": asked.get("dimension"), "text": heard.get("text"), "how": "RECORDED",
                        "skipped": False}
    return {"owed": owed, "route": {"status": route.status_code, "body": asked}, "over": over, "heard": heard,
            "wrong": {"status": wrong.status_code, "body": _json_of(wrong), "dimension": other}}


def _recorded_pilot(j, record: dict, token: str, interview: dict, invitation_id: str | None = None) -> None:
    """Spec 049 FR-6 (keel-web 073 FR-7(b)) on the wire, in the page's own order: the answers go first (`toPilot` sends
    the response, then asks the pilot), then the pilot ask's recording is written down through `POST .../transcribe`
    against the first question's item (no `expected`, 073 D-02) and read on the page; a "yes" is held and goes on, and
    the page posts `POST .../pilot {pilotOptIn: true}`. The stack's fake transcriber hears "yes" for any recording over
    the floor, so the opt-in must be written. **DRIFT #91, RESOLVED by keel-cloud 102** (spec 050 FR-6): `transcribe` is
    served on an answered AI link while its pilot opt-in is not yet recorded (the item word `pilot`, yes / no
    expected), so the step REQUIRES transcribe 200 "yes", then `POST pilot` 204, the stored opt-in true
    (`stack.ledger.pilot_opt_in`), and the window closed after it (a second transcribe 409)."""
    import base64                                                             # noqa: PLC0415

    gate = interview.get("gate") or {}
    first = gate.get("itemId") or next((i.get("itemId") for part in interview.get("parts") or []
                                        for i in part.get("items") or []), None)
    # No `GET standings` here: on Keel's keyless door it starts the stale brief (keel-cloud 096 FR-D) right after this
    # link's answer made it stale, fails it, and leaves the staleness "tried" -- no brief on the founder's return (the
    # sibling of 048 call 14). The opt-in's count is IM6's, on the AI link, over the same route.
    with j.recorder.step("interviewer (keel-web 073 FR-7(b), DRIFT #91): the recorded link's pilot ask, after its "
                         "answers went -- the recording written down through transcribe against the first question's "
                         "item, the fake's \"yes\" read on the page, and the pilot's opt-in written",
                         party="participant", kind="assert") as h:
        written = _participant(j, "POST", token, "/interview/transcribe", {
            "itemId": first, "audio": base64.b64encode(SOUNDED_WEBM).decode("ascii"), "mimeType": "audio/webm",
            "language": j.entry.market["language"]})
        got = {"status": written.status_code, **_json_of(written)}
        out: dict = {"itemId": first, "transcribe": got, "drift": "#91 resolved (keel-cloud 102)"}
        record["recorded"]["pilot"] = out
        opted_before = stack_ledger.pilot_opt_in(j.stack, j.project_id, invitation_id) if invitation_id else None
        heard = (got.get("text") or "").strip().lower()
        pilot = _participant(j, "POST", token, "/interview/pilot", {"pilotOptIn": True}) \
            if written.status_code == 200 and heard == FAKE_TRANSCRIPT else None
        out["pilot"] = pilot.status_code if pilot is not None else None
        out["opted_in"] = {"before": opted_before,
                           "after": stack_ledger.pilot_opt_in(j.stack, j.project_id, invitation_id)
                           if invitation_id else None}
        again = _participant(j, "POST", token, "/interview/transcribe", {
            "itemId": first, "audio": base64.b64encode(SOUNDED_WEBM).decode("ascii"), "mimeType": "audio/webm",
            "language": j.entry.market["language"]})
        out["transcribe_after_pilot"] = again.status_code
        h.record_assert({"transcribe": {"status": 200, "text": FAKE_TRANSCRIPT}, "pilot": 204,
                         "opted_in": {"before": False, "after": True}, "transcribe_after_pilot": 409}, out)
        assert written.status_code == 200 and heard == FAKE_TRANSCRIPT, got
        assert out["pilot"] == 204, out
        assert out["opted_in"] == {"before": False, "after": True}, out["opted_in"]
        assert again.status_code == 409, out


def _heard_for(answer: dict, interview: dict) -> str:
    """What a recorded answer was heard as: the option's own words, the value, or the escape's (composed here)."""
    for part in interview.get("parts") or []:
        for item in part.get("items") or []:
            if item.get("itemId") != answer.get("itemId"):
                continue
            labels = {o["optionId"]: o["label"] for o in item.get("options") or []}
            labels.update({a["id"]: a["label"] for a in item.get("advantages") or []})
            if answer.get("chip"):
                return (item.get("escape") or {}).get("label") or "I can't say"
            if answer.get("costTotal"):
                return str(answer["costTotal"].get("value"))
            if answer.get("scale") is not None:
                return str(answer["scale"])
            words = [labels.get(o, "") for o in (answer.get("optionIds") or []) + (answer.get("advantageIds") or [])]
            return " and ".join(w for w in words if w) or "yes"
    return "yes"


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
                         f"nothing is charged and {fake.FACE_NAMES[CHANGED_FACE]} still asks", party="founder",
                         kind="assert") as h:
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


#: The scorecard's one line on the remote profile (amendment 2026-10-17 to spec 051): nothing is owed there.
REMOTE_MARKS = ("none owed on the remote profile: the AI walk (IM14-IM25), Try it yourself and the clips need the local "
                "database and keel-web's test build (window.__keelSpeech), which staging does not serve, and the text "
                "links' stories are typed there, so IM26 (speak or type) is unmeasured")


def _score(j, record: dict, *, require: list[str], note: str | None = None) -> None:
    """The interviewer marks over the record, written into the bundle; the leg fails on any owed mark unmet. `note`
    says, in one line on the card and the step, why nothing is owed (the remote profile)."""
    card = marks.scorecard(record)
    card["owed"] = list(require)
    if note:
        card["note"] = note
    run_dir = Path(j.recorder.run_dir)
    (run_dir / "interviewer.json").write_text(json.dumps(record, indent=2, default=str) + "\n", encoding="utf-8")
    (run_dir / "interviewer-marks.json").write_text(json.dumps(card, indent=2, default=str) + "\n", encoding="utf-8")
    owing = f"{', '.join(require)} owed" if require else (note or "none owed")
    with j.recorder.step(f"interviewer marks v{marks.INTERVIEWER_MARKS_VERSION}: {card['met']} of {card['measured']} "
                         f"met ({owing})", party="stack", kind="assert") as h:
        owed = {c["mark"]: c for c in card["checks"] if c["mark"] in require}
        h.record_assert({m: True for m in require}, {m: {"ok": c["ok"], "detail": c["detail"]}
                                                     for m, c in owed.items()})
        unmet = [m for m, c in owed.items() if not (c["measured"] and c["ok"])]
        assert not unmet, {m: owed[m] for m in unmet}
