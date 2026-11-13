"""Spec 154 FR-4 (the keel-cloud 248 half) and FR-5 -- **a call, without a Meet, and the card headless** (keel-cloud 248
*A call with me: plan, sign in, start*; keel-web 189 *Calls with me*, 188 *the copilot card*).

The founder plans a call on Sent's **Calls with me** tab (`plan-call` -> the one screen: the kind row on two kinds, *Their
name*, *Plan the call* -> `POST calls {roleId, name}` 201, the Done screen), the row reads PLANNED with *unverified* (no
identity yet) and *Start the call*; the Start sheet's three steps are read and pressed as the harness can (the Meet is a
tick, the copilot is opened by the harness in the founder's own context, the link is read off the row's `signInUrl`);
the person opens their link in their own context -- the CALL arrival card (`call-arrival`: the notice, *Continue with
Google*, no Begin, nothing of the questionnaire) -- and signs in on the stub issuer exactly as a group link's stranger
does (start -> the picker, by `login_hint`'s identity -> the callback -> `call-signed-in`); the row then reads GOOGLE,
Google's name, and *You wrote {typed}* where the typed word is not in Google's name (one call typed as a nickname, one as
the person's own first name); the card's title mark flips to Google.

**The card, headless (FR-5)**: the copilot route (`/p/{id}/calls/{callId}`) is opened in the founder's context with
`navigator.mediaDevices` and `documentPictureInPicture` faked by an init script -- two silent `AudioContext` tracks
(the microphone and the tab share), a device list of two microphones, a `documentPictureInPicture` object so the browser
check passes (headless Chromium has no Document PiP: the Float step is asserted drawn and never pressed, the card never
floating). The mic dropdown lists two and remembers the one picked across a reload (`localStorage` `keel-copilot-mic`);
Start posts `start` (ON_CALL on the wire, the row's status); the script is walked by the card's own buttons -- the
intro, the gate's Yes (the STORY stretch, stopped), six filings with one undo (Z on the newest, filed again), the
follow-up stretch where a filing is in `against`, the reveal, the pilot; the two closing stretches (OWN_QUESTIONS,
THEIR_QUESTIONS) opened and stopped; End -> the upload hits `POST calls/{id}/record` as one multipart with three parts
named `founder`, `them` and `keys` (the request is kept off the wire by the harness). **Since keel-cloud 249** (the second pass): the
upload answers 200 with the row, the digest files it (ENDED, then ANSWERED on the poll) -- the card's own record on the
first call (silent tracks, heard as the stack's one word); on the second call, never signed in, the fake record built
off the script (`evals/call_record`) is uploaded on the wire and the digest is read whole: the detail (format CALL,
identity NONE, six TAPPED answers with their seconds, `heard` on item 1 naming option 3, the story and the follow-up as
the fake transcriber heard them, two notes with both voices), the timeline, Hear the call's tracks with Range, NO
INTERVIEW ledger row (keel-cloud 250), and the n line's `unverified` 0 after the first call and 1 after the second.

Nothing paid: the fake executor answers the FIRST_PERSON job on this stack (keel-cloud 248 FR-7b) and the fake
transcriber the stretches (249). Every step records what it read; the leg asserts on the wire and the screen.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any

import requests

from evals import call_record
from harness import interview_charge as charge
from harness import interviewer_fake as fake
from harness import interviews_screens as iv
from harness.browser import _BrowserStep, chooser_button_selector
from stack import auth as stack_auth
from stack import cloud_log

SPEC = "154"

# ----------------------------------------------------------------------------------------- keel-web 189: Calls with me

CALLS = "[data-testid='calls']"
CALL_ROWS = "[data-testid='call-row']"
CALL_START = "[data-testid='call-start']"
CALL_SEE_ANSWERS = "[data-testid='call-see-answers']"
CALL_STATUS = "[data-testid='call-status']"
CALL_NAME = "[data-testid='call-name']"
CALL_ROLE_LINE = "[data-testid='call-role-line']"
YOU_WROTE = "[data-testid='you-wrote']"
CALLS_SEARCH = "[data-testid='calls-search']"
PLAN_CALL_POPUP = "[data-testid='plan-call-popup']"
PLAN_CALL_TITLE = "[data-testid='plan-call-title']"
PLAN_CALL_KIND = "[data-testid='plan-call-kind']"
PLAN_CALL_NAME = "[data-testid='plan-call-name']"
PLAN_CALL_LINE = "[data-testid='plan-call-line']"
PLAN_CALL_PRESS = "[data-testid='plan-call-press']"
PLAN_CALL_DONE = "[data-testid='plan-call-done']"
PLAN_CALL_DONE_BOX = "[data-testid='plan-call-done-box']"
START_CALL_SHEET = "[data-testid='start-call-sheet']"
START_CALL_TITLE = "[data-testid='start-call-title']"
START_CALL_DONE = "[data-testid='start-call-done']"
#: keel-web 189's words (`translate.ts`).
CALL_STATUS_WORDS = {"PLANNED": "Call planned", "ON_CALL": "On the call", "ENDED": "Call ended · Keel is writing it up",
                     "ANSWERED": "Answered · counted", "SCREENED_OUT": "Screened out · kept"}
MARK_VERIFIED = "verified · Google"
MARK_UNVERIFIED = "unverified · typed by you"
PLAN_CALL_KICKER = "Calls with me · plan a call"
PLAN_CALL_TITLE_WORDS = "Who are you calling?"
PLAN_CALL_KIND_LABEL = "Who are they?"
PLAN_CALL_LINE_WORDS = ("On a video call, in Chrome. Keel shows you what to say and keeps the answers; the call is recorded "
                        "for you both. One person per call. Nothing more to pay.")
PLAN_CALL_PRESS_WORDS = "Plan the call"
START_CALL_KICKER = "Calls with me · start the call"
START_CALL_STEPS = ("Open the Google Meet in Chrome", "Open the copilot", "Send them their sign-in link")
CALL_START_WORDS = "Start the call"
#: keel-web 189 / keel-cloud 248: the person's card.
CALL_ARRIVAL = "[data-testid='call-arrival']"
CALL_NOTICE = "[data-testid='call-notice']"
CALL_SIGNED_IN = "[data-testid='call-signed-in']"
ARRIVAL_GOOGLE = "[data-testid='arrival-google']"
CALL_NOTICE_WORDS = ("This call is recorded and kept with your name. {first} may quote your words in their report, and "
                     "there's no way to take it back once it's done.")
CALL_SIGNED_IN_WORDS = "You're signed in. Back to the call."
#: keel-cloud 248: the stub's identity the person signs in as (the eval's registry, per run).
PERSON_NAME = "Renata Castillo-Vega"
#: The founder's typed words: a nickname (not in Google's name -> *You wrote*) and the person's own first name.
TYPED_NICKNAME = "Reni"
#: keel-cloud 248's and 249's log lines (ids only).
LOG_PLANNED, LOG_SIGNED_IN, LOG_STARTED = "call_planned", "call_signed_in", "call_started"
LOG_ENDED, LOG_DIGESTED, LOG_COUNTED = "call_ended", "call_digested", "call_counted"
#: keel-cloud 249: the digest's thread polls every 10 s; a call is ANSWERED within this.
DIGEST_WITHIN_S = 90

# ------------------------------------------------------------------------------------------- keel-web 188: the card

COPILOT_PAGE = "[data-testid='copilot-page']"
COPILOT_CARD = "[data-testid='copilot-card']"
BROWSER_LINE = "[data-testid='browser-line']"
FLOATING = "[data-testid='floating']"
MIC_STORAGE_KEY = "keel-copilot-mic"
RECORD_PARTS = ("founder", "them", "keys")
#: keel-web 188 FR-2: the browser line's words where the check fails (never drawn under the fakes).
COPILOT_BROWSER_LINE = ("Keel's copilot runs in Chrome on a laptop. Open this page in Chrome, and join the Meet from a "
                        "Chrome tab.")
#: The fake sources (FR-5): `getUserMedia` / `getDisplayMedia` answer a silent `AudioContext` stream (one audio track
#: each -- the tab share also carries a video track the page drops), `enumerateDevices` two microphones by label, and
#: `documentPictureInPicture` is an object whose `requestWindow` refuses (never called: the Float step is not pressed).
FAKE_MEDIA = r"""
(() => {
  const mics = [
    { deviceId: 'mic-one', kind: 'audioinput', label: 'Fake microphone one', groupId: 'g1' },
    { deviceId: 'mic-two', kind: 'audioinput', label: 'Fake microphone two', groupId: 'g2' },
    { deviceId: 'spk-one', kind: 'audiooutput', label: 'Fake speaker', groupId: 'g1' },
  ];
  const silent = (withVideo) => {
    const Ctx = window.AudioContext || window.webkitAudioContext;
    const ctx = new Ctx();
    const dest = ctx.createMediaStreamDestination();
    const gain = ctx.createGain();
    gain.gain.value = 0;
    gain.connect(dest);
    const stream = dest.stream;
    if (withVideo) {
      const canvas = document.createElement('canvas');
      canvas.width = 16; canvas.height = 16;
      const video = canvas.captureStream ? canvas.captureStream(5) : null;
      if (video) for (const t of video.getVideoTracks()) stream.addTrack(t);
    }
    return stream;
  };
  const calls = { getUserMedia: [], getDisplayMedia: [], enumerate: 0 };
  const devices = {
    getUserMedia: async (constraints) => {
      calls.getUserMedia.push(constraints);
      const stream = silent(false);
      const track = stream.getAudioTracks()[0];
      const wanted = constraints && constraints.audio && constraints.audio.deviceId && constraints.audio.deviceId.exact;
      track.getSettings = () => ({ deviceId: wanted || 'mic-one' });
      return stream;
    },
    getDisplayMedia: async (constraints) => { calls.getDisplayMedia.push(constraints); return silent(true); },
    enumerateDevices: async () => { calls.enumerate += 1; return mics.map((m) => ({ ...m, toJSON() { return m; } })); },
    addEventListener() {}, removeEventListener() {},
  };
  try { Object.defineProperty(navigator, 'mediaDevices', { value: devices, configurable: true }); } catch (e) {}
  window.__keelFakeMedia = calls;
  if (!window.documentPictureInPicture) {
    window.documentPictureInPicture = { requestWindow: () => Promise.reject(new DOMException('headless', 'NotSupportedError')),
                                        window: null, addEventListener() {}, removeEventListener() {} };
  }
})();
"""


def _words(locator) -> str:
    return " ".join((locator.first.text_content() or "").split()) if locator.count() else ""


def _json(response) -> dict:
    try:
        body = response.json()
    except Exception:  # noqa: BLE001 - an empty or non-JSON body
        return {"status": response.status}
    return body if isinstance(body, dict) else {"status": response.status, "body": body}


def _step(j, name: str, *, party: str = "founder", kind: str = "assert"):
    return j.recorder.step(name, party=party, kind=kind)


def _labels(j) -> dict[str, str]:
    register = j.get(j.project("/invitations")) or {}
    return {k.get("respondentType"): (k.get("label"), k.get("roleId")) for k in register.get("kinds") or []}


def _row_of(sent_page, call_id: str):
    return sent_page.locator(f"{CALL_ROWS}[data-call='{call_id}']").first


def _read_row(row) -> dict:
    return {"call": row.get_attribute("data-call"), "status": row.get_attribute("data-status"),
            "name": _words(row.locator(CALL_NAME)), "role_line": _words(row.locator(CALL_ROLE_LINE)),
            # keel-web 189 draws the separator inside the span (*You wrote {typed} ·*): read without it
            "you_wrote": re.sub(r"\s*·$", "", _words(row.locator(YOU_WROTE))) or None,
            "status_words": _words(row.locator(CALL_STATUS)),
            "start": _words(row.locator(CALL_START)) or None,
            "see_answers": _words(row.locator(CALL_SEE_ANSWERS)) or None}


# ------------------------------------------------------------------------------------------------ the founder's side

def plan_a_call(j, sent: iv.Interviews, kind: str, typed: str, *, expect_kind_row: bool) -> dict:
    """Spec 154 FR-4 (keel-web 189 FR-2, keel-cloud 248 FR-1): *Plan a call* on the Calls tab -> the one screen -> the
    kind pressed where the project has two -> the name -> *Plan the call* -> 201 CallRow; the Done screen; Done."""
    labels = _labels(j)
    label, role_id = labels[kind]
    b = _BrowserStep(j.recorder, j.page, "founder")
    with b.step(f"founder plans a call with {typed!r} ({label}) from Sent's Calls with me tab") as h:
        sent.land(j.project_id)
        tabs = sent.open_tab("calls")
        panel = (tabs.get("panel") or {})
        j.page.locator(iv.PLAN_CALL_BUTTON).first.click()
        popup = j.page.locator(PLAN_CALL_POPUP).first
        popup.wait_for(state="visible", timeout=10_000)
        drawn = {"tab": tabs.get("calls"), "panel": panel, "kicker": _words(popup.locator(".pop__kicker")),
                 "title": _words(popup.locator(PLAN_CALL_TITLE)), "line": _words(popup.locator(PLAN_CALL_LINE)),
                 "kind_row": popup.locator(PLAN_CALL_KIND).count() > 0,
                 "press_disabled_before": popup.locator(PLAN_CALL_PRESS).first.is_disabled()}
        if drawn["kind_row"]:
            drawn["kind_label"] = _words(popup.locator(f"{PLAN_CALL_KIND} label"))
            radio = popup.locator(f"[data-testid='plan-call-kind-{role_id}']").first
            if radio.get_attribute("aria-checked") != "true":
                radio.click()
            drawn["kinds"] = [{"id": r.get_attribute("data-testid"), "text": _words(r),
                               "checked": r.get_attribute("aria-checked") == "true"}
                              for r in popup.locator(f"{PLAN_CALL_KIND} [role=radio]").all()]
        popup.locator(PLAN_CALL_NAME).fill(typed)
        drawn["press"] = _words(popup.locator(PLAN_CALL_PRESS))
        offset = cloud_log.offset(j.stack)
        with j.page.expect_response(lambda r: r.request.method == "POST" and r.url.split("?")[0].endswith("/calls"),
                                    timeout=30_000) as planned:
            popup.locator(PLAN_CALL_PRESS).first.click()
        response = planned.value
        row = _json(response)
        out = {"status": response.status, "sent": response.request.post_data_json, "row": row, "drawn": drawn,
               "log": cloud_log.wait_lines(j.stack, LOG_PLANNED, project_id=j.project_id, since_offset=offset)}
        if response.status < 400:
            popup.locator(PLAN_CALL_DONE).wait_for(state="visible", timeout=10_000)
            out["done"] = {"title": _words(popup.locator(PLAN_CALL_DONE)), "box": _words(popup.locator(PLAN_CALL_DONE_BOX))}
            h.add_screenshot(b.screenshot(f"call-planned-{typed.split()[0].lower()}"))
            popup.get_by_role("button", name=iv.SEND_DONE, exact=True).click()
            popup.wait_for(state="hidden", timeout=10_000)
        else:
            out["refusal"] = _words(popup)
            h.add_screenshot(b.screenshot("call-plan-refused"))
        h.record_wire(out["sent"], {"status": out["status"], "row": row})
    first = typed.split()[0]
    with _step(j, f"keel-web 189 FR-2 / keel-cloud 248 FR-1: Plan a call is one screen -- the kicker, *Who are you "
                  f"calling?*, {'the kind row (two kinds)' if expect_kind_row else 'no kind row (one kind)'}, the one "
                  "line, *Plan the call* -> POST calls {roleId, name} 201: PLANNED, identity NONE, the typed word kept, "
                  "a signInUrl and the copilotPath; the Done screen; the call planned: line") as h:
        want = {"status": 201, "sent": {"roleId": role_id, "name": typed}, "kicker": PLAN_CALL_KICKER,
                "title": PLAN_CALL_TITLE_WORDS, "line": PLAN_CALL_LINE_WORDS, "kind_row": expect_kind_row,
                "press": PLAN_CALL_PRESS_WORDS, "row": {"status": "PLANNED", "identity": "NONE", "typedName": typed,
                                                        "personName": typed, "nameDiffers": False, "roleId": role_id},
                "done": {"title": f"{first}'s call is planned"}, "tab": "Calls with me · n"}
        h.record_assert(want, out)
        assert out["status"] == 201 and out["sent"] == want["sent"], out
        assert (drawn["kicker"], drawn["title"], drawn["line"], drawn["press"]) == (
            PLAN_CALL_KICKER, PLAN_CALL_TITLE_WORDS, PLAN_CALL_LINE_WORDS, PLAN_CALL_PRESS_WORDS), drawn
        assert drawn["kind_row"] is expect_kind_row and drawn["press_disabled_before"] is True, drawn
        if expect_kind_row:
            assert drawn.get("kind_label") == PLAN_CALL_KIND_LABEL, drawn
            assert any(k["checked"] and k["id"] == f"plan-call-kind-{role_id}" for k in drawn["kinds"]), drawn
        for key, value in want["row"].items():
            assert row.get(key) == value, (key, row)
        assert row.get("signInUrl") and row.get("copilotPath") == f"/p/{j.project_id}/calls/{row.get('callId')}", row
        assert row.get("signedInAt") is None and row.get("startedAt") is None and row.get("endedAt") is None, row
        assert out["done"]["title"] == f"{first}'s call is planned" and "Start the call" in out["done"]["box"], out["done"]
        assert (tabs.get("calls") or {}).get("selected") is True, tabs
        assert panel.get("id") == "sent-panel-calls" and panel.get("lead") == iv.SENT_LEAD["calls"], panel
        if out["log"] is not None:
            assert any(x.get("call") == row.get("callId") and x.get("role") == role_id for x in out["log"]), out["log"]
    return out


def read_the_row(j, sent: iv.Interviews, call_id: str, *, want_status: str, want_name: str, want_you_wrote: str | None,
                 what: str) -> dict:
    """The call's row on the Calls tab as drawn against `GET calls/{id}`: the status word, the name, the mark on the
    role line (*verified · Google* / *unverified · typed by you*), *You wrote {typed}* where the names differ, and the
    row's action (*Start the call* until a record)."""
    sent.land(j.project_id)
    sent.open_tab("calls")
    j.page.locator(f"{CALL_ROWS}[data-call='{call_id}']").first.wait_for(state="visible", timeout=20_000)
    drawn = _read_row(_row_of(j.page, call_id))
    wire = j.get(j.project(f"/calls/{call_id}")) or {}
    with _step(j, f"{what}: the row reads *{CALL_STATUS_WORDS[want_status]}*, the name {want_name!r}"
                  + (f", *You wrote {want_you_wrote}*" if want_you_wrote else "") + " -- as GET calls/{id} serves it "
                  "(keel-web 189 FR-1, FR-5; keel-cloud 248 FR-2, FR-4)") as h:
        mark = MARK_VERIFIED if wire.get("identity") == "GOOGLE" else MARK_UNVERIFIED
        want = {"status": want_status, "status_words": CALL_STATUS_WORDS[want_status], "name": want_name,
                "you_wrote": f"You wrote {want_you_wrote}" if want_you_wrote else None, "mark": mark,
                "start": CALL_START_WORDS}
        h.record_assert(want, {"drawn": drawn, "wire": {k: wire.get(k) for k in
                                                        ("status", "identity", "personName", "typedName", "nameDiffers")}})
        assert drawn["status"] == want_status == wire.get("status"), (drawn, wire)
        assert drawn["status_words"].startswith(CALL_STATUS_WORDS[want_status]), drawn
        assert drawn["name"] == want_name == wire.get("personName"), (drawn, wire)
        assert (drawn["you_wrote"] or None) == want["you_wrote"], drawn
        assert wire.get("nameDiffers") is bool(want_you_wrote), wire
        if want_status in ("ANSWERED", "SCREENED_OUT"):
            assert drawn["see_answers"] and drawn["start"] is None, drawn
        else:
            assert drawn["start"] == CALL_START_WORDS and drawn["see_answers"] is None, drawn
    return {"drawn": drawn, "wire": wire}


def start_sheet(j, sent: iv.Interviews, call: dict) -> dict:
    """Spec 154 FR-4 (keel-web 189 FR-3): *Start the call* on the row -> the sheet's three steps in order -- the Meet
    ticked (a local tick), the copilot opened by the harness itself (step 2 would `window.open`; the card is walked in
    the founder's own context), the link pressed (the clipboard, or the drawn link where it refuses) -- then Done."""
    call_id = call["callId"]
    b = _BrowserStep(j.recorder, j.page, "founder")
    with b.step(f"founder opens Start the call for {call.get('personName')!r} and walks its steps") as h:
        sent.land(j.project_id)
        sent.open_tab("calls")
        _row_of(j.page, call_id).locator(CALL_START).first.click()
        sheet = j.page.locator(START_CALL_SHEET).first
        sheet.wait_for(state="visible", timeout=10_000)
        steps = []
        for i in range(1, 4):
            li = sheet.locator(f"[data-testid='start-call-step-{i}']").first
            steps.append({"title": _words(li.locator(".sc-step__title")), "press": _words(li.locator(f"[data-testid='start-call-press-{i}']")),
                          "done_before": li.get_attribute("data-done")})
        drawn = {"kicker": _words(sheet.locator(".pop__kicker")), "title": _words(sheet.locator(START_CALL_TITLE)),
                 "steps": steps}
        sheet.locator("[data-testid='start-call-press-1']").first.click()
        # step 2 opens a new tab (window.open); the harness opens the card itself in this context (FR-5), so it is
        # read and left unpressed here
        sheet.locator("[data-testid='start-call-press-3']").first.click()
        j.page.wait_for_timeout(300)
        fallback = sheet.locator("[data-testid='start-call-link-fallback']")
        after = [sheet.locator(f"[data-testid='start-call-step-{i}']").first.get_attribute("data-done") for i in range(1, 4)]
        drawn["after"] = after
        drawn["link_shown"] = _words(fallback.locator(".sc-step__link")) if fallback.count() else None
        drawn["copied_words"] = _words(sheet.locator("[data-testid='start-call-press-3']"))
        h.add_screenshot(b.screenshot("start-call-sheet"))
        sheet.locator(START_CALL_DONE).first.click()
        sheet.wait_for(state="hidden", timeout=10_000)
        h.record_wire({"call": call_id}, drawn)
    first = (call.get("personName") or "").split()[0]
    with _step(j, "keel-web 189 FR-3: the Start sheet -- the kicker, *Start the call with {first}*, the three steps in "
                  "order, steps 1 and 3 green once pressed, step 2 (the copilot's tab) left to the harness; the link "
                  "copied or drawn for the founder's own copy") as h:
        h.record_assert({"kicker": START_CALL_KICKER, "title": f"Start the call with {first}", "steps": list(START_CALL_STEPS),
                         "after": ["true", "false", "true"], "link": call.get("signInUrl")}, drawn)
        assert drawn["kicker"] == START_CALL_KICKER and drawn["title"] == f"Start the call with {first}", drawn
        assert [s["title"] for s in steps] == list(START_CALL_STEPS), steps
        assert all(s["done_before"] == "false" for s in steps), steps
        assert after == ["true", "false", "true"], after
        assert drawn["link_shown"] in (None, call.get("signInUrl")), drawn
    return drawn


# ------------------------------------------------------------------------------------------------- the person's side

def sign_the_person_in(j, browser, call: dict, person, *, what: str) -> dict:
    """Spec 154 FR-4 (keel-cloud 248 FR-3 / FR-4, keel-web 189 FR-4): the person opens their own link in their own
    context -- the CALL arrival card (the founder's first name, the notice, *Continue with Google*, no Begin, nothing of
    the questionnaire) -- and signs in on the stub issuer as a group link's stranger does; the next read is
    CALL_SIGNED_IN; the wire's row reads GOOGLE and Google's name."""
    token = stack_auth.token_of(call["signInUrl"])
    served_before = requests.get(f"{j.cloud_base}/v2/i/{token}/interview", timeout=20)
    card_wire = _json(served_before)
    context = browser.new_context()
    try:
        page = context.new_page()
        b = _BrowserStep(j.recorder, page, "participant")
        with b.step(f"{what}: {person.name} opens their call link and signs in with Google on the stub issuer") as h:
            page.goto(call["signInUrl"], wait_until="load")
            page.locator(CALL_ARRIVAL).first.wait_for(state="visible", timeout=30_000)
            arrival = page.locator(CALL_ARRIVAL).first
            drawn = {"state": arrival.get_attribute("data-state"), "heading": _words(page.locator("[data-testid='arrival-heading']")),
                     "notice": _words(page.locator(CALL_NOTICE)), "google": _words(page.locator(ARRIVAL_GOOGLE)),
                     "google_href": page.locator(ARRIVAL_GOOGLE).first.get_attribute("href") if page.locator(ARRIVAL_GOOGLE).count() else None,
                     "begin": page.get_by_role("button", name="Begin", exact=True).count(),
                     "text": _words(arrival)}
            h.add_screenshot(b.screenshot("call-arrival"))
            offset = cloud_log.offset(j.stack)
            page.locator(ARRIVAL_GOOGLE).first.click()
            page.get_by_role("heading", name="Choose an account").wait_for(state="visible", timeout=20_000)
            page.locator(chooser_button_selector(person.id)).first.click()
            page.locator(CALL_SIGNED_IN).first.wait_for(state="visible", timeout=30_000)
            signed = {"state": page.locator(CALL_ARRIVAL).first.get_attribute("data-state"),
                      "line": _words(page.locator(CALL_SIGNED_IN)), "url": page.url,
                      "google_left": page.locator(ARRIVAL_GOOGLE).count()}
            h.add_screenshot(b.screenshot("call-signed-in"))
            served_after = _json(requests.get(f"{j.cloud_base}/v2/i/{token}/interview", timeout=20))
            log = cloud_log.wait_lines(j.stack, LOG_SIGNED_IN, project_id=j.project_id, since_offset=offset)
            h.record_wire({"token": "the call's", "person": person.id}, {"card": drawn, "signed": signed})
    finally:
        context.close()
    wire = j.get(j.project(f"/calls/{call['callId']}")) or {}
    founder_first = (card_wire.get("founderFirstName") or "")
    with _step(j, f"{what}: the CALL token serves CALL_ARRIVAL -- the notice, Continue with Google, no Begin, nothing of "
                  "the questionnaire -- and the card draws it; the callback writes the identity: CALL_SIGNED_IN, the row "
                  "GOOGLE with Google's name (keel-cloud 248 FR-3 / FR-4; keel-web 189 FR-4)", party="participant") as h:
        want = {"served": {"state": "CALL_ARRIVAL", "kind": "CALL_ARRIVAL", "parts": None, "gate": None},
                "card": {"state": "arrival", "notice": CALL_NOTICE_WORDS.format(first=founder_first), "begin": 0,
                         "google": "Continue with Google", "google_href": f"/v2/i/{token}/auth/google/start"},
                "signed": {"state": "signed-in", "line": CALL_SIGNED_IN_WORDS, "google_left": 0},
                "after": {"state": "CALL_SIGNED_IN"},
                "wire": {"identity": "GOOGLE", "personName": person.name, "nameDiffers": call["typedName"] not in person.name}}
        got = {"served": {k: card_wire.get(k) for k in ("state", "kind", "parts", "gate", "consentText")},
               "card": drawn, "signed": signed, "after": {"state": served_after.get("state")},
               "wire": {k: wire.get(k) for k in ("identity", "personName", "typedName", "nameDiffers", "signedInAt")},
               "log": log}
        h.record_assert(want, got)
        assert card_wire.get("state") == "CALL_ARRIVAL" == card_wire.get("kind"), card_wire
        assert "parts" not in card_wire and "gate" not in card_wire and "consentText" not in card_wire, card_wire
        assert drawn["state"] == "arrival" and drawn["begin"] == 0, drawn
        assert drawn["notice"] == CALL_NOTICE_WORDS.format(first=founder_first), drawn
        assert drawn["google_href"] == f"/v2/i/{token}/auth/google/start", drawn
        assert signed["state"] == "signed-in" and signed["line"] == CALL_SIGNED_IN_WORDS and signed["google_left"] == 0, signed
        assert served_after.get("state") == "CALL_SIGNED_IN" and "signInUrl" not in served_after, served_after
        assert wire.get("identity") == "GOOGLE" and wire.get("personName") == person.name, wire
        assert wire.get("nameDiffers") is (call["typedName"] not in person.name) and wire.get("signedInAt"), wire
        if log is not None:
            assert any(x.get("call") == call["callId"] for x in log), log
    return {"card": drawn, "signed": signed, "wire": wire}


# ---------------------------------------------------------------------------------------------- the card, headless

class Card:
    """keel-web 188's copilot card, driven by its own buttons (never the keys, so what the walk pressed is what a founder
    presses) in a founder context with the fake sources. Machinery: asserts nothing."""

    def __init__(self, page, recorder, base: str, *, patience: float = 1.0):
        self.page = page
        self.base = base.rstrip("/")
        self.patience = patience
        self._b = _BrowserStep(recorder, page, "founder")

    def open(self, copilot_path: str) -> dict:
        self.page.goto(f"{self.base}{copilot_path}", wait_until="load")
        self.page.locator(f"{COPILOT_CARD}, {BROWSER_LINE}").first.wait_for(state="visible",
                                                                           timeout=30_000 * self.patience)
        return self.read()

    def phase(self) -> str | None:
        card = self.page.locator(COPILOT_CARD)
        return card.first.get_attribute("data-phase") if card.count() else None

    def read(self) -> dict:
        t = lambda sel: _words(self.page.locator(sel))  # noqa: E731
        select = self.page.locator("[data-testid='which-mic']")
        return {"phase": self.phase(), "browser_line": t(BROWSER_LINE) or None, "floating": self.page.locator(FLOATING).count(),
                "title": t("[data-testid='card-title']"), "mark": t("[data-testid='mark']"),
                "mark_identity": (self.page.locator("[data-testid='mark']").first.get_attribute("data-identity")
                                  if self.page.locator("[data-testid='mark']").count() else None),
                "who": t("[data-testid='who']"), "read": t("[data-testid='read']"),
                "filed": t("[data-testid='filed-words']") or None,
                "mics": [o.get_attribute("value") for o in select.locator("option").all()] if select.count() else [],
                "mic_value": select.first.input_value() if select.count() else None,
                "start_disabled": self.page.locator("[data-testid='start']").first.is_disabled()
                if self.page.locator("[data-testid='start']").count() else None,
                "float_drawn": self.page.locator("[data-testid='float']").count(),
                "float_disabled": self.page.locator("[data-testid='float']").first.is_disabled()
                if self.page.locator("[data-testid='float']").count() else None,
                "options": [_words(o) for o in self.page.locator("[data-testid^='opt-']").all()],
                "failure": t("[data-testid='failure']") or None,
                "progress": [i.get_attribute("data-mark") for i in self.page.locator("ul.cpl-prog i").all()]}

    def press(self, testid: str, *, wait_phase: tuple | None = None, timeout_s: float = 20) -> None:
        self.page.locator(f"[data-testid='{testid}']").first.click()
        if wait_phase:
            self.wait_phase(*wait_phase, timeout_s=timeout_s)

    def wait_phase(self, *phases: str, timeout_s: float = 20) -> str:
        selector = ", ".join(f"{COPILOT_CARD}[data-phase='{p}']" for p in phases)
        self.page.locator(selector).first.wait_for(state="attached", timeout=timeout_s * 1000 * self.patience)
        return self.phase() or ""

    def wait_read(self, text_changed_from: str, *, timeout_s: float = 10) -> str:
        try:
            self.page.wait_for_function("(was) => { const el = document.querySelector('[data-testid=read]'); "
                                        "return el && el.textContent.replace(/\\s+/g, ' ').trim() !== was; }",
                                        arg=text_changed_from, timeout=timeout_s * 1000)
        except Exception:  # noqa: BLE001 - the same words twice (two items alike) is the caller's to read
            pass
        return _words(self.page.locator("[data-testid='read']"))

    def pick_mic(self, device_id: str) -> None:
        self.page.locator("[data-testid='which-mic']").first.select_option(value=device_id)
        self.page.wait_for_function("(id) => document.querySelector('[data-testid=which-mic]')?.value === id",
                                    arg=device_id, timeout=10_000)

    def remembered_mic(self) -> str | None:
        return self.page.evaluate("(k) => { try { return localStorage.getItem(k); } catch (e) { return null; } }",
                                  MIC_STORAGE_KEY)

    def screenshot(self, name: str):
        return self._b.screenshot(name)


def _script_passages(j, call_id: str) -> dict:
    return j.get(j.project(f"/calls/{call_id}/script")) or {}


def walk_the_card(j, browser, call: dict, *, record: dict) -> dict:
    """Spec 154 FR-5: the card headless -- the fake sources, the browser check, the mic picked by name and remembered
    across a reload, Start (ON_CALL), six filings with one undo, the stretches, End, the upload's three parts."""
    call_id = call["callId"]
    uploads: list[dict] = []

    def keep(request) -> None:
        if request.method == "POST" and request.url.split("?")[0].endswith(f"/calls/{call_id}/record"):
            body = request.post_data_buffer or b""
            names = re.findall(rb'name="([^"]+)"', body)
            files = re.findall(rb'filename="([^"]+)"', body)
            uploads.append({"url": request.url, "bytes": len(body),
                            "parts": [n.decode("utf-8", "replace") for n in names],
                            "files": [f.decode("utf-8", "replace") for f in files],
                            "content_type": request.headers.get("content-type", "")})
    # the founder's own context (their session as keel-cloud's login left it -- never a cookie set by hand), a new page
    # with the fake sources installed before any script of the page runs
    page = j.context.new_page()
    try:
        page.add_init_script(FAKE_MEDIA)
        page.on("request", keep)
        responses: list = []
        page.on("response", lambda r: responses.append({"url": r.url, "status": r.status})
                if r.request.method == "POST" and r.url.split("?")[0].endswith(f"/calls/{call_id}/record") else None)
        card = Card(page, j.recorder, j.web_base, patience=j.patience)
        with card._b.step("founder opens the copilot card headless: the fake microphone and tab, the browser check, the "
                          "mic picked by name and remembered, Start, the filings, End, the upload") as h:
            before = card.open(call["copilotPath"])
            h.add_screenshot(card.screenshot("card-before"))
            # the two sources
            card.press("mic")
            page.wait_for_function("() => document.querySelectorAll('[data-testid=which-mic] option').length >= 2", timeout=15_000)
            after_mic = card.read()
            card.pick_mic("mic-two")
            card.press("share")
            page.wait_for_function("() => !document.querySelector('[data-testid=start]').disabled", timeout=15_000)
            sources = card.read()
            remembered = card.remembered_mic()
            # the remembered mic across a reload: the dropdown reopens on the one picked
            page.reload(wait_until="load")
            page.locator(COPILOT_CARD).first.wait_for(state="visible", timeout=30_000)
            card.press("mic")
            page.wait_for_function("() => document.querySelector('[data-testid=which-mic]')?.value === 'mic-two'", timeout=15_000)
            reopened = card.read()
            card.press("share")
            page.wait_for_function("() => !document.querySelector('[data-testid=start]').disabled", timeout=15_000)
            h.add_screenshot(card.screenshot("card-sources"))
            # Start: the intro
            with page.expect_response(lambda r: r.request.method == "POST" and r.url.split("?")[0].endswith(f"/calls/{call_id}/start"),
                                      timeout=30_000) as started:
                card.press("start", wait_phase=("reading",))
            start_status = started.value.status
            on_call = _json(started.value)
            filings = _walk_filings(card, page)
            h.add_screenshot(card.screenshot("card-filed"))
            # the closing stretches and End
            closing = _walk_closing(card, page)
            # End -> the upload: keel-cloud 249 answers 200 with the row (ENDED), the digest files it (ANSWERED)
            offset = cloud_log.offset(j.stack)
            card.press("end")
            try:
                card.wait_phase("done", "failed", timeout_s=60)
            except Exception:  # noqa: BLE001 - recorded: the phase the card stood in
                pass
            page.wait_for_timeout(500)
            ended = card.read()
            statuses = wait_digested(j, call_id)
            h.add_screenshot(card.screenshot("card-ended"))
            h.record_wire({"copilotPath": call["copilotPath"]},
                          {"before": before, "after_mic": after_mic, "sources": sources, "remembered": remembered,
                           "reopened": reopened, "start": {"status": start_status, "row": on_call},
                           "filings": filings, "closing": closing, "ended": ended, "uploads": uploads,
                           "upload_responses": responses})
    finally:
        page.close()
    wire = j.get(j.project(f"/calls/{call_id}")) or {}
    out = {"before": before, "after_mic": after_mic, "sources": sources, "remembered": remembered, "reopened": reopened,
           "start": {"status": start_status, "row": on_call}, "filings": filings, "closing": closing, "ended": ended,
           "uploads": uploads, "upload_responses": responses, "statuses": statuses,
           "wire_after": {k: wire.get(k) for k in ("status", "startedAt", "endedAt")},
           "log": {"ended": cloud_log.wait_lines(j.stack, LOG_ENDED, project_id=j.project_id, since_offset=offset),
                   "digested": cloud_log.wait_lines(j.stack, LOG_DIGESTED, project_id=j.project_id, since_offset=offset),
                   "counted": cloud_log.wait_lines(j.stack, LOG_COUNTED, project_id=j.project_id, since_offset=offset)}}
    record["card"] = out
    with _step(j, "spec 154 FR-5 (keel-web 188): the browser check passes on the fakes (no browser line), the mic "
                  "dropdown lists two and keeps the one picked across a reload, Start posts start (ON_CALL) and reads "
                  "the intro, six filings with one undo, the STORY / FOLLOW_UP / OWN_QUESTIONS / THEIR_QUESTIONS "
                  "stretches, End uploads one multipart with three parts founder / them / keys; Float drawn, never "
                  "pressed, never floating") as h:
        want = {"browser_line": None, "mics": ["mic-one", "mic-two"], "picked": "mic-two", "remembered": "mic-two",
                "reopened_on": "mic-two", "start": {"status": 200, "status_after": "ON_CALL"},
                "filings": {"filed": 6, "undo": 1}, "closing": {"stretches": ["OWN_QUESTIONS", "THEIR_QUESTIONS"]},
                "upload": {"parts": list(RECORD_PARTS), "files": ["founder.wav", "them.wav", "keys.json"], "status": 200},
                "float": {"drawn": 1, "floating": 0}, "phase": "done", "statuses": ["ENDED", "ANSWERED"],
                "log": "call ended, call digested, call counted (local)"}
        h.record_assert(want, out)
        assert before["browser_line"] is None and before["phase"] == "before", before
        assert sorted(after_mic["mics"]) == ["mic-one", "mic-two"], after_mic
        assert sources["mic_value"] == "mic-two" and remembered == "mic-two", (sources, remembered)
        assert reopened["mic_value"] == "mic-two", reopened
        assert sources["start_disabled"] is False, sources
        assert start_status == 200 and on_call.get("status") == "ON_CALL" and on_call.get("startedAt"), on_call
        assert filings["filed"] >= 6 and filings["undo"] == 1, filings
        assert [s["kind"] for s in closing["stretches"]] == ["OWN_QUESTIONS", "THEIR_QUESTIONS"], closing
        assert uploads and uploads[0]["parts"] == list(RECORD_PARTS), uploads
        assert uploads[0]["files"] == ["founder.wav", "them.wav", "keys.json"], uploads
        assert "multipart/form-data" in uploads[0]["content_type"], uploads
        # FR-5: no Document PiP in headless -- the Float step drawn (the check passes on the fake), never pressed, the
        # card never floating; asserted so, never failed
        assert ended["floating"] == 0 and before["float_drawn"] == 1, (before, ended)
        # keel-cloud 249 (FR-1, FR-2): the upload answers 200 with the row, the card reads done, the row flips to
        # ENDED and then ANSWERED on the poll (the digest's thread; the silent tracks are heard as the stack's one word)
        assert responses and responses[-1]["status"] == 200, responses
        assert ended["phase"] == "done" and ended["failure"] is None, ended
        assert statuses["seen"][:1] in (["ENDED"], ["ANSWERED"]) and statuses["final"] == "ANSWERED", statuses
        assert wire.get("status") == "ANSWERED" and wire.get("endedAt"), wire
        for name in ("ended", "digested", "counted"):
            if out["log"][name] is not None:
                assert any(x.get("call") == call_id for x in out["log"][name]), (name, out["log"][name])
    return out


def _walk_filings(card: Card, page) -> dict:
    """The script by the card's buttons: the intro's →, the gate's Yes (STORY stretch stopped), each item's first
    option (a number item typed 3 and filed; a two-step ladder's first band then its first option), the follow-up
    stretch stopped where it opens, the reveal's →, the pilot's Yes; one undo (Z) on the second filing, filed again."""
    filed = 0
    undo = 0
    seen: list[dict] = []
    guard = 0
    undone_once = False
    while guard < 60:
        guard += 1
        phase = card.phase()
        read = card.read()
        seen.append({"phase": phase, "read": read["read"][:80], "options": read["options"][:7], "filed": read["filed"]})
        if phase in ("own", "theirs", "end", "sending", "done", "failed"):
            break
        if phase == "story":
            card.press("stop")
            continue
        if phase == "follow-up":
            card.press("stop")
            continue
        if phase == "screened":
            card.press("back-to-screener")
            continue
        if phase == "second-step":
            card.press("opt-1")
            filed += 1
            continue
        if phase != "reading":
            page.wait_for_timeout(200)
            continue
        options = page.locator("[data-testid^='opt-']:not([data-testid='opt-0'])")
        typed = page.locator("[data-testid='typed']")
        nxt = page.locator("[data-testid='next']")
        if typed.count():
            page.keyboard.type("3")
            card.press("file-number")
            filed += 1
        elif options.count():
            if filed == 2 and not undone_once:
                # one undo: Z takes the newest filing back and shows that question again; it is filed once more
                page.keyboard.press("z")
                undo += 1
                undone_once = True
                page.wait_for_timeout(200)
                continue
            card.press("opt-1")
            filed += 1
        elif nxt.count():
            card.press("next")
        else:
            page.keyboard.press("ArrowRight")
        page.wait_for_timeout(150)
    return {"filed": filed, "undo": undo, "steps": seen, "phase": card.phase()}


def _walk_closing(card: Card, page) -> dict:
    """The two closing stretches opened and stopped (OWN_QUESTIONS, THEIR_QUESTIONS), to End."""
    stretches = []
    for kind in ("OWN_QUESTIONS", "THEIR_QUESTIONS"):
        phase = card.phase()
        if phase not in ("own", "theirs"):
            break
        card.press("stretch")
        page.wait_for_timeout(700)
        stretches.append({"kind": kind, "phase": phase})
        card.press("stop")
        page.wait_for_timeout(200)
    try:
        card.wait_phase("end", timeout_s=10)
    except Exception:  # noqa: BLE001 - the phase is recorded
        pass
    return {"stretches": stretches, "phase": card.phase()}


# --------------------------------------------------------------------------------- keel-cloud 249: the record and the digest

def wait_digested(j, call_id: str, *, timeout_s: float = DIGEST_WITHIN_S) -> dict:
    """The row's statuses from the upload on, polled every second: ENDED, then ANSWERED (or SCREENED_OUT) once the
    digest filed it."""
    seen: list[str] = []
    started = time.monotonic()
    row: dict = {}
    while time.monotonic() - started < timeout_s * j.patience:
        row = j.get(j.project(f"/calls/{call_id}")) or {}
        status = row.get("status")
        if status and (not seen or seen[-1] != status):
            seen.append(status)
        if status in ("ANSWERED", "SCREENED_OUT"):
            break
        time.sleep(1)
    return {"seen": seen, "final": row.get("status"), "row": row, "seconds": round(time.monotonic() - started, 1)}


def upload_fixture_record(j, call: dict, record: dict) -> dict:
    """Spec 154 FR-4 (keel-cloud 249 FR-1): the fake call record built off the call's script (`evals/call_record`) and
    uploaded as the three parts `founder` / `them` / `keys` -- 200 with the row ENDED, the digest to ANSWERED."""
    call_id = call["callId"]
    script = j.get(j.project(f"/calls/{call_id}/script")) or {}
    built = call_record.write_record(j.recorder.run_dir, script)
    with _step(j, f"the fake call record for {call.get('personName')!r}: two 16 kHz mono WAVs (the founder's with a tone "
                  "at every filing, the person's with the words the fake transcriber hears at each window) and the key "
                  "log off the script -- six items filed, one undone and filed again, the STORY / FOLLOW_UP / "
                  "OWN_QUESTIONS / THEIR_QUESTIONS stretches -- uploaded as founder / them / keys: 200, the row ENDED, "
                  "then ANSWERED (keel-cloud 249 FR-1, FR-2)", party="founder") as h:
        offset = cloud_log.offset(j.stack)
        response = j.context.request.post(
            f"{j.cloud_base}{j.project(f'/calls/{call_id}/record')}",
            multipart={"founder": {"name": "founder.wav", "mimeType": "audio/wav", "buffer": built["founder"]},
                       "them": {"name": "them.wav", "mimeType": "audio/wav", "buffer": built["them"]},
                       "keys": {"name": "keys.json", "mimeType": "application/json",
                                "buffer": json.dumps(built["log"]).encode("utf-8")}},
            timeout=60_000)
        body = _json(response)
        statuses = wait_digested(j, call_id)
        out = {"status": response.status, "row": {k: body.get(k) for k in ("status", "endedAt", "identity")},
               "statuses": statuses, "plan": built["plan"], "log": built["log"],
               "lines": {"ended": cloud_log.wait_lines(j.stack, LOG_ENDED, project_id=j.project_id, since_offset=offset),
                         "digested": cloud_log.wait_lines(j.stack, LOG_DIGESTED, project_id=j.project_id, since_offset=offset)}}
        record["fixture"] = out
        h.record_assert({"status": 200, "row": {"status": "ENDED"}, "statuses": ["ENDED", "ANSWERED"],
                         "parts": list(RECORD_PARTS)}, out)
        assert response.status == 200 and body.get("status") == "ENDED" and body.get("endedAt"), (response.status, body)
        assert statuses["final"] == "ANSWERED", statuses
        assert statuses["seen"][:1] == ["ENDED"] or statuses["seen"] == ["ANSWERED"], statuses
        if out["lines"]["digested"] is not None:
            assert any(x.get("call") == call_id for x in out["lines"]["digested"]), out["lines"]
    return out


def the_digest(j, call: dict, record: dict, *, founder_id: str | None, since: str | None) -> None:
    """Spec 154 FR-4 (keel-cloud 249 FR-2, FR-5): what the digest filed for the fixture call -- the detail (format CALL,
    identity NONE, the six filed answers TAPPED with their seconds, `heard` on item 1 naming option 3, the story the
    fake transcriber heard, one follow-up, two notes with both voices), the timeline (the filings, the four stretch
    kinds, `heard`), Hear the call's two tracks with Range, and NO INTERVIEW ledger row (keel-cloud 250 overrides the
    30)."""
    call_id = call["callId"]
    plan = record["fixture"]["plan"]
    detail = j.get(j.project(f"/invitations/{call_id}")) or {}
    timeline = j.get(j.project(f"/calls/{call_id}/timeline")) or {}
    answers = detail.get("answers") or {}
    items = answers.get("items") or []
    by_item = {i.get("itemId"): i for i in items}
    heard_item = plan["heard_item"]
    notes = detail.get("notes") or []
    follow_ups = answers.get("followUps") or []
    with _step(j, "keel-cloud 249 FR-2 / FR-5: the detail of the fixture call -- format CALL, identity NONE, six answers "
                  "TAPPED each with its second, item 1 *heard* as option 3's label, the story as the fake heard it, one "
                  "follow-up with its words, two notes (own questions, their questions) with both voices") as h:
        got = {"format": detail.get("format"), "callId": detail.get("callId"), "identity": detail.get("identity"),
               "status": detail.get("status"), "answers": len(items),
               "hows": sorted({i.get("how") for i in items}), "ats": sum(1 for i in items if isinstance(i.get("at"), (int, float))),
               "heard": {k: v.get("heard") for k, v in by_item.items() if v.get("heard")},
               "story": answers.get("story"), "anchoring": answers.get("anchoring"),
               "followUps": [{k: f.get(k) for k in ("dimension", "text", "how")} for f in follow_ups],
               "notes": [{k: n.get(k) for k in ("kind", "from", "to", "founder", "them")} for n in notes]}
        record["detail"] = got
        want = {"format": "CALL", "callId": call_id, "identity": "NONE", "status": "ANSWERED", "answers": 6,
                "hows": ["TAPPED"], "heard": {heard_item: plan["heard_option_label"]}, "story": call_record.STORY,
                "followUps": [{"text": call_record.FOLLOW_UP, "how": "RECORDED"}] if plan["follow_up_item"] else [],
                "notes": [{"kind": "OWN_QUESTIONS", "founder": call_record.OWN_FOUNDER, "them": call_record.OWN_THEM},
                          {"kind": "THEIR_QUESTIONS", "founder": call_record.THEIR_FOUNDER, "them": call_record.THEIR_THEM}]}
        h.record_assert(want, got)
        assert got["format"] == "CALL" and got["callId"] == call_id and got["identity"] == "NONE", got
        assert got["status"] == "ANSWERED", got
        assert len(items) >= 6 and got["hows"] == ["TAPPED"] and got["ats"] == len(items), got
        assert got["heard"] == {heard_item: plan["heard_option_label"]}, got["heard"]
        assert got["story"] == call_record.STORY, got["story"]
        if plan["follow_up_item"]:
            assert len(follow_ups) == 1 and follow_ups[0].get("text") == call_record.FOLLOW_UP, follow_ups
        assert [n.get("kind") for n in notes] == ["OWN_QUESTIONS", "THEIR_QUESTIONS"], notes
        assert (notes[0].get("founder"), notes[0].get("them")) == (call_record.OWN_FOUNDER, call_record.OWN_THEM), notes
        assert (notes[1].get("founder"), notes[1].get("them")) == (call_record.THEIR_FOUNDER, call_record.THEIR_THEM), notes
    with _step(j, "keel-cloud 249 FR-5: the timeline -- the filings kept after the undo in time order, the stretches as the "
                  "key log had them (STORY, FOLLOW_UP, OWN_QUESTIONS, THEIR_QUESTIONS), the notes' windows, `heard` on "
                  "item 1") as h:
        kinds = [s.get("kind") for s in timeline.get("stretches") or []]
        got = {"duration": timeline.get("duration"), "filings": len(timeline.get("filings") or []),
               "ats_sorted": [f.get("at") for f in timeline.get("filings") or []] == sorted(f.get("at") for f in timeline.get("filings") or []),
               "kinds": kinds, "notes": len(timeline.get("notes") or []),
               "heard": [(x.get("itemId"), x.get("label")) for x in timeline.get("heard") or []]}
        record["timeline"] = got
        surviving = len(record["fixture"]["log"]["filings"]) - len(record["fixture"]["log"]["undos"])
        h.record_assert({"filings": surviving, "ats_sorted": True,
                         "kinds": ["STORY", "FOLLOW_UP", "OWN_QUESTIONS", "THEIR_QUESTIONS"] if plan["follow_up_item"] else ["STORY", "OWN_QUESTIONS", "THEIR_QUESTIONS"],
                         "notes": 2, "heard": [(heard_item, plan["heard_option_label"])]}, got)
        assert got["filings"] == surviving and got["ats_sorted"], got
        assert kinds == (["STORY", "FOLLOW_UP", "OWN_QUESTIONS", "THEIR_QUESTIONS"] if plan["follow_up_item"]
                         else ["STORY", "OWN_QUESTIONS", "THEIR_QUESTIONS"]), kinds
        assert got["notes"] == 2 and got["heard"] == [(heard_item, plan["heard_option_label"])], got
        assert isinstance(got["duration"], (int, float)) and got["duration"] >= call_record.TIMES["end"], got
    with _step(j, "keel-cloud 249 FR-5: Hear the call -- each track answers 206 to a Range and 200 whole with "
                  "Accept-Ranges; another track word is the bare 404", party="founder") as h:
        base = f"{j.cloud_base}{j.project(f'/calls/{call_id}/audio')}"
        part = j.context.request.get(f"{base}/them", headers={"Range": "bytes=0-99"}, timeout=20_000)
        whole = j.context.request.get(f"{base}/founder", timeout=20_000)
        other = j.context.request.get(f"{base}/meet", timeout=20_000)
        got = {"part": {"status": part.status, "length": len(part.body()), "content_range": part.headers.get("content-range")},
               "whole": {"status": whole.status, "accept_ranges": whole.headers.get("accept-ranges"),
                         "length": len(whole.body()), "type": whole.headers.get("content-type")},
               "other": other.status}
        record["audio"] = got
        h.record_assert({"part": {"status": 206, "length": 100}, "whole": {"status": 200, "accept_ranges": "bytes",
                                                                           "length": len(record["fixture"]["log"]) and 44 + call_record.DURATION_S * call_record.BYTES_PER_SECOND},
                         "other": 404}, got)
        assert got["part"]["status"] == 206 and got["part"]["length"] == 100, got
        assert got["whole"]["status"] == 200 and got["whole"]["accept_ranges"] == "bytes", got
        assert got["whole"]["length"] == 44 + call_record.DURATION_S * call_record.BYTES_PER_SECOND, got
        assert got["other"] == 404, got
    if founder_id and since and j.stack is not None and not j.stack.is_remote:
        from stack import ledger as stack_ledger                           # noqa: PLC0415
        rows = stack_ledger.rows(j.stack, founder_id, since=since)
        with _step(j, "keel-cloud 250 over 249: a filed call writes NO INTERVIEW row and nothing that moves the balance",
                   party="stack") as h:
            interview = [x for x in rows if x.get("action") == charge.INTERVIEW]
            moved = [x for x in rows if charge.moves_balance(x) and x.get("kind") not in ("GRANT", "PURCHASE")
                     and x.get("action") not in (charge.PROJECT, fake.RECORDING)]
            record["ledger"] = {"interview": interview, "moved": moved, "rows": len(rows)}
            h.record_assert({"INTERVIEW rows": 0, "moved by a call": 0}, record["ledger"])
            assert not interview and not moved, record["ledger"]


def people_counts(j) -> dict:
    """`StandingsView.people` -- `answered` and spec 249's `unverified` (the CALL records whose person never signed in)."""
    people = (j.get(j.project("/standings")) or {}).get("people") or {}
    return {k: people.get(k) for k in ("invited", "answered", "unverified")}


# ------------------------------------------------------------------------------------------------------- the leg

def first_person_line(belief: str) -> str:
    """The first-person belief as keel-cloud's `first-person.md` asks for it -- *I believe it would* then the same claims
    in the same words (FR-7 F4): the card's belief with its leading *It would* / *it would* said by the speaker."""
    said = " ".join(str(belief or "").split()).rstrip(".")
    lead = re.match(r"^(?:[Ii]t|[Tt]his|[Tt]hat)\s+would\s+", said)
    rest = said[lead.end():] if lead else (said[:1].lower() + said[1:])
    return f"I believe it would {rest}." if lead else f"I believe {rest}."


def stand_in_first_person(j, record: dict) -> None:
    """Spec 154 FR-4 / FR-5 (keel-cloud 248 FR-7, FR-10): the first Plan a call starts the FIRST_PERSON job, which runs
    on Keel's AI alone; the local stack has Keel's AI off on either door, so keel-cloud logs *first-person owed: ...
    not written reason=...* and the script holds `firstPersonPending` -- the card draws only its writing line (keel-web
    188). The line is held logged, then written as the job would write it (`stack_ledger.stand_in_first_person`), so the
    card can be walked. Nothing on the remote profile (the twin runs Keel's AI)."""
    if j.stack is None or j.stack.is_remote:
        return
    from stack import ledger as stack_ledger                               # noqa: PLC0415
    with _step(j, "keel-cloud 248 FR-10: the first Plan a call left the first-person line owed on this stack (Keel's AI "
                  "is off here on either door) -- STAND-IN: the line written as the FIRST_PERSON job would, so the card "
                  "draws (keel-web 188)", party="stack", kind="protocol") as h:
        owed = cloud_log.wait_lines(j.stack, "first_person_owed", project_id=j.project_id) or []
        idea = stack_ledger.idea_lines(j.stack, j.project_id)
        line = first_person_line(idea.get("belief") or "")
        stored = idea.get("beliefFirstPerson") or stack_ledger.stand_in_first_person(j.stack, j.project_id, line)
        script = j.get(j.project(f"/calls/{record['calls'][0]['callId']}/script")) or {}
        record["first_person"] = {"owed": [o.get("reason") for o in owed], "belief": idea.get("belief"),
                                  "stored": stored, "pending_after": script.get("firstPersonPending")}
        h.record_assert({"owed": "logged with its reason", "stored": line, "pending_after": False},
                        record["first_person"])
        assert owed and all(o.get("reason") for o in owed), record["first_person"]
        assert stored and script.get("firstPersonPending") is False, record["first_person"]


def leg_calls(j, browser, *, kind: str | None = None) -> dict:
    """Spec 154 FR-4 (248's half) + FR-5, after the interviewer leg on S-005: two calls planned (a nickname, then the
    person's own first name), the first signed in by the person (GOOGLE, *You wrote*), its card walked headless to the
    upload; the second left PLANNED and unverified. Returns the record (`calls.json` in the bundle)."""
    from harness import vectors_script as vs                             # noqa: PLC0415
    record: dict = {"project_id": j.project_id, "calls": []}
    labels = _labels(j)
    kind = kind or vs.LINK_PRIMARY
    two_kinds = len(labels) > 1
    sent = iv.Interviews(j.page, j.recorder, j.web_base, patience=j.patience, guide=j.guide)
    stamp = f"{int(time.time())}"
    person = stack_auth.register_stranger(j.stack, f"caller-{stamp}", PERSON_NAME) if j.stack is not None else None
    # the Calls tab before any call
    sent.land(j.project_id)
    tabs = sent.open_tab("calls")
    with _step(j, "keel-web 187 FR-1 / 189 FR-1: Sent's third tab -- *Calls with me · 0*, its lead, Plan a call enabled "
                  "on the locked project, *No calls planned.*") as h:
        panel = tabs.get("panel") or {}
        h.record_assert({"calls": iv.sent_tab_calls(0), "lead": iv.SENT_LEAD["calls"], "button": iv.SEND_PLAN_CALL,
                         "enabled": True, "empty": "No calls planned."}, tabs)
        assert (tabs.get("calls") or {}).get("text") == iv.sent_tab_calls(0), tabs
        assert panel.get("lead") == iv.SENT_LEAD["calls"] and (panel.get("button") or {}).get("text") == iv.SEND_PLAN_CALL, panel
        assert (panel.get("button") or {}).get("disabled") is False, panel
        assert panel.get("empty") == "No calls planned.", panel
    first = plan_a_call(j, sent, kind, TYPED_NICKNAME, expect_kind_row=two_kinds)
    call = first["row"]
    record["calls"].append(call)
    read_the_row(j, sent, call["callId"], want_status="PLANNED", want_name=TYPED_NICKNAME, want_you_wrote=None,
                 what="the first call, planned")
    start_sheet(j, sent, call)
    if person is not None:
        record["person"] = {"id": person.id, "name": person.name}
        signed = sign_the_person_in(j, browser, call, person, what="the first call")
        record["signed_in"] = signed
        read_the_row(j, sent, call["callId"], want_status="PLANNED", want_name=person.name,
                     want_you_wrote=TYPED_NICKNAME, what="the first call, signed in")
        from stack import ledger as stack_ledger                           # noqa: PLC0415
        founder_id = stack_ledger.founder_account(j.stack, j.founder_identity.sub)["id"] if j.stack is not None and not j.stack.is_remote else None
        since = stack_ledger.now(j.stack) if founder_id else None
        stand_in_first_person(j, record)
        walk_the_card(j, browser, call, record=record)
        read_the_row(j, sent, call["callId"], want_status=record["card"]["wire_after"]["status"], want_name=person.name,
                     want_you_wrote=TYPED_NICKNAME, what="the first call, after the card")
        with _step(j, "keel-cloud 249 FR-4: the n line after the first call -- its person signed in, so `unverified` 0 and "
                      "the call inside `answered`", party="stack") as h:
            counts = people_counts(j)
            record["people_after_first"] = counts
            h.record_assert({"unverified": 0, "answered": ">= 1"}, counts)
            assert counts.get("unverified") == 0 and (counts.get("answered") or 0) >= 1, counts
        second = plan_a_call(j, sent, kind, person.given_name, expect_kind_row=two_kinds)
        record["calls"].append(second["row"])
        read_the_row(j, sent, second["row"]["callId"], want_status="PLANNED", want_name=person.given_name,
                     want_you_wrote=None, what="the second call, planned and unverified")
        # the second call is never signed in: the fake record is uploaded on the wire, as the card would, and digested
        j.call("POST", j.project(f"/calls/{second['row']['callId']}/start"), None, ok=(200,))
        upload_fixture_record(j, second["row"], record)
        the_digest(j, second["row"], record, founder_id=founder_id, since=since)
        read_the_row(j, sent, second["row"]["callId"], want_status="ANSWERED", want_name=person.given_name,
                     want_you_wrote=None, what="the second call, filed and unverified")
        with _step(j, "keel-cloud 249 FR-4: the n line after the second call -- its person never signed in, so "
                      "`unverified` 1, the call inside `answered` (the default count)", party="stack") as h:
            counts = people_counts(j)
            record["people_after_second"] = counts
            h.record_assert({"unverified": 1, "answered": ">= 2"}, counts)
            assert counts.get("unverified") == 1 and (counts.get("answered") or 0) >= 2, counts
    with _step(j, "spec 154 FR-4: the Calls register after -- every call planned, newest first; the search box from six "
                  "rows is the table's own (keel-web 189 FR-1: drawn from six, as the links' is)", kind="assert") as h:
        wire = j.get(j.project("/calls")) or {}
        rows = [r.get("callId") for r in wire.get("calls") or []]
        sent.land(j.project_id)
        sent.open_tab("calls")
        drawn = [r.get_attribute("data-call") for r in j.page.locator(CALL_ROWS).all()]
        search = j.page.locator(CALLS_SEARCH).count()
        record["register"] = {"wire": rows, "drawn": drawn, "search": search}
        h.record_assert({"rows": len(record["calls"]), "search": "from six rows" if len(rows) >= 6 else "not yet"},
                        record["register"])
        assert set(drawn) == set(rows) == {c["callId"] for c in record["calls"]}, record["register"]
        assert (search > 0) == (len(rows) >= iv.LINKS_SEARCH_FROM), record["register"]
    from pathlib import Path                                               # noqa: PLC0415
    (Path(j.recorder.run_dir) / "calls.json").write_text(json.dumps(record, indent=2, default=str) + "\n", encoding="utf-8")
    return record
