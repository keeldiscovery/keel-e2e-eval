"""keel-web 069's AI interviewer, as page objects (spec 044 T003; keel-web master `d23895f`), and keel-web 072's answer
path (spec 048 T003, contract 18: no *That's my answer*, the three tiers, the hold, Back, Test your mic).

Machinery, not judgement: every class here acts and reads, and asserts nothing -- `evals/interviewer_leg.py` judges.
The words are copied from keel-web `src/lib/translate.ts`; the selectors are the ones 069's tasks.md names for this
repository (*Selectors (for keel-e2e-eval 044)*) and 072's spec names (`ai-yes`, `ai-back`, `ai-mic-test`,
`ai-mic-heard`, `start-talking`).

* `Persona`   -- Sent's persona line (`[data-testid=persona-line]`, `data-state`), its progress bar, *Change who asks* /
                 *Record the interviewer* and the popup (`[data-testid=change-face-popup]`, the carousel,
                 `[data-testid=change-face-confirm]`), the role cards' *Try it yourself*, Send more's format row read
                 and cancelled, W1 replayed through *How it works*, L1 revisited.
* `Player`    -- the AI interviewer's page for a stranger or the founder's dry run: the intros (072: *Test your mic*),
                 the stage (`data-phase`, the one `<video>`, the pills, End, the ship mark), the sheet (options, field,
                 escape, preview, heard, status, Back, *Yes, that's it*, *Save and next* for typed words, *Finish* on
                 the pilot, *Type instead*) and the end screens. 072: an utterance ends on a final result (the seam's
                 recogniser then ends, as Chrome's does); the cloud's classifier decides (`classify`); a confident read
                 is **held** two seconds and the interview goes on by itself (`hold`), a word of protest reopens it
                 (`veto`), an unsure one asks "Is that right?" (`yes`), and *Back* reopens the last question (`back`).
* `SPEECH_SEAM` -- the init script that stands in for the browser's recogniser and microphone through the test build's
                 own seam (`window.__keelSpeech`, present only under `vite --mode test`, which the stack serves): keel-web's
                 own `tests/fixtures/interviewer/fakeSpeech.ts`, restated in JavaScript. `__say(text, final)` is the
                 stranger speaking; a final is followed by the recogniser's end. No microphone is opened. **No `classify`
                 is put on the seam** (spec 048 judgement call 1): the page calls the real route, and the stack's
                 keel-cloud answers it with its `FakeClassifier` -- what staging runs for eval founders too.

Every write a press makes returns the response keel-web received, so the leg holds the wire the page was handed.
"""

from __future__ import annotations

import re

from playwright.sync_api import Page

from harness.browser import _BrowserStep, _safe_text

# ---- keel-web d23895f `translate.ts`
PERSONA_RECORDING = "Recording now, usually ready in about five minutes. You can leave this page."
PERSONA_NOT_RECORDED = "No interviewer recorded yet."
TRY_IT_YOURSELF = "Try it yourself"
TRY_IT_YOURSELF_RECORDING = "Try it yourself · recording"
TRY_NOTHING_STORED = "Nothing was stored."
SEND_TEXT_ONLY_LINKS = "Send text-only links"
SEND_LINKS = "Send links"
SEND_FORMAT_RECORDED = "The interviewer is already recorded for this project."
SEND_FORMAT_RECORDING = "The interviewer is still recording; Text only is ready now."
CHANGE_FACE_TITLE = "Change who asks"
RECORD_FACE_TITLE = "Record the interviewer"
HOW_IT_WORKS = "How it works"
WALKTHROUGH_GOT_IT = "Got it"
MARK = "Keel · AI interviewer"
MARK_TRY = "Keel · AI interviewer · try run"
LAST_QUESTION = "Last question"
#: keel-web 070's press after an answer, gone with keel-web 072 FR-5: never in the DOM again.
THATS_MY_ANSWER = "That’s my answer"
FINISH = "Finish"
#: keel-web 070 F1 / 072 FR-5: typed words keep an explicit press.
SAVE_AND_NEXT = "Save and next"
# ---- keel-web 072 `translate.ts` (spec 072 FR-7, FR-9)
START_THE_INTERVIEW = "Start the interview"
MIC_TEST = "Test your mic"
SAY_HELLO = "Say hello"
MIC_FALLBACK = "You can tap or type your answers instead"
INTRO_TRANSCRIBED = ("Where your browser can't listen, Keel's transcription provider writes your answer down and keeps "
                     "nothing.")
GOT_THAT = "Got that…"
WRITING_DOWN = "Writing it down…"
HELD = "Got it. Moving on… say no to change"
IS_THAT_RIGHT = "Is that right? Say yes, or tell me the right one"
YES_THATS_IT = "Yes, that’s it"
#: The words a stranger says for each move (design §3-§4).
VETO = "no"
SAY_YES = "yes"
GO_BACK = "go back"


def mic_heard(text: str) -> str:
    return f"Heard: {text}"


def back_to(question: int) -> str:
    return f"‹ Back to question {question}"

#: Spec 046 FM5: the stage's timeline, kept by the page itself from before the app runs -- every `data-phase` the stage
#: takes (`performance.now()`), every `play` of a clip on the stage's `<video>`, and every press of `ai-next` with the
#: words it carried. `window.__keelFlow()` hands it back. Spec 048 (keel-web 072): every change of the sheet's status
#: words (`ai-status`) in order, `window.__keelPhases()`; every press of a button on the sheet with its words; and
#: whether *That's my answer* (`ai-answer`) was ever in the DOM, `window.__keelSawAnswer()`.
FLOW_TIMELINE = r"""
(() => {
  const events = [];
  const statuses = [];
  let phase = null;
  let status = null;
  let sawAnswer = false;
  const read = () => {
    const stage = document.querySelector('[data-testid=ai-stage]');
    const now = stage ? stage.getAttribute('data-phase') : null;
    if (now !== phase) { phase = now; events.push({ t: performance.now(), kind: 'phase', value: now }); }
    const line = document.querySelector('[data-testid=ai-status]');
    const words = line ? (line.textContent || '').trim() : null;
    if (words && words !== status) {
      status = words;
      const q = document.querySelector('[data-testid=ai-sheet] .iv-q');
      statuses.push({ t: performance.now(), status: words, question: q ? (q.textContent || '').trim() : null });
    }
    if (!sawAnswer && document.querySelector('[data-testid=ai-answer]')) sawAnswer = true;
  };
  new MutationObserver(read).observe(document, { subtree: true, childList: true, attributes: true,
                                                 characterData: true });
  document.addEventListener('play', (e) => {
    const v = e.target;
    if (v && v.tagName === 'VIDEO') events.push({ t: performance.now(), kind: 'play', clip: v.getAttribute('data-clip') });
  }, true);
  document.addEventListener('click', (e) => {
    const b = e.target && e.target.closest ? e.target.closest('[data-testid=ai-next]') : null;
    if (b) events.push({ t: performance.now(), kind: 'next', value: (b.textContent || '').trim() });
    const any = e.target && e.target.closest ? e.target.closest('[data-testid=ai-sheet] button, [data-testid=ai-sheet] .opt') : null;
    if (any) events.push({ t: performance.now(), kind: 'press', testid: any.getAttribute('data-testid'),
                           value: (any.textContent || '').trim() });
  }, true);
  window.__keelFlow = () => events.slice();
  window.__keelPhases = () => statuses.slice();
  window.__keelSawAnswer = () => sawAnswer;
})();
"""


def persona_asks(face: str) -> str:
    return f"{face} asks your questions."


def persona_progress(done: int, total: int) -> str:
    return f"{done} of {total} clips done"


def change_who_asks(credits: int) -> str:
    return f"Change who asks · {credits:,} AI credits"


def pick_who_asks(credits: int) -> str:
    return f"Record the interviewer · {credits:,} AI credits"


def walkthrough_asks_title(face: str) -> str:
    return f"{face} asks your questions"


def ai_intro_heading(face: str, questions: int) -> str:
    return f"{face} will ask you {questions} questions."


#: keel-web `tests/fixtures/interviewer/fakeSpeech.ts` `installFakeSpeech`, in JavaScript (an init script runs before
#: the app does; the app reads the seam only in a test-mode build). Spec 048 (keel-web 072): a final result is followed
#: by the recogniser's end, so a final said is an utterance ended and the page reads it; `mic` is a microphone that is
#: always granted with a steady level, so *Test your mic* is driven by `__say("hello", true)`. Unlike keel-web's own
#: fixture it puts **no `classify`** on the seam: the route is left real (judgement call 1).
SPEECH_SEAM = r"""
(() => {
  class FakeRecognition {
    constructor() {
      this.continuous = false; this.interimResults = false; this.lang = ""; this.maxAlternatives = 1;
      this.onstart = null; this.onresult = null; this.onerror = null; this.onend = null;
      this.results = []; this.started = false; this.stopped = false;
      (window.__speech = window.__speech || []).push(this);
    }
    start() { this.started = true; }
    stop() { this.stopped = true; }
    abort() {}
  }
  window.__keelSpeech = {
    Recognition: FakeRecognition, recorder: null,
    mic: { acquire: async () => true, level: () => 0.12, release: () => undefined },
  };
  const last = () => (window.__speech || [])[(window.__speech || []).length - 1];
  window.__say = (text, final) => {
    const r = last();
    if (!r) return false;
    r.results.push({ isFinal: !!final, 0: { transcript: text }, length: 1 });
    if (r.onresult) r.onresult({ resultIndex: r.results.length - 1, results: r.results });
    if (final) setTimeout(() => { if (r.onend) r.onend({}); }, 0);
    return true;
  };
  window.__speechError = (error) => { const r = last(); if (r && r.onerror) r.onerror({ error }); };
  window.__speechEnd = () => { const r = last(); if (r && r.onend) r.onend({}); };
  window.__recognisers = () => (window.__speech || []).length;
})();
"""


def _json(response) -> dict:
    try:
        body = response.json()
    except Exception:  # noqa: BLE001 - an empty or non-JSON body
        return {"status": response.status}
    return body if isinstance(body, dict) else {"status": response.status, "body": body}


def _words(locator) -> str:
    return " ".join((locator.text_content() or "").split()) if locator.count() else ""


# --------------------------------------------------------------------------------------------- the founder

class Persona:
    def __init__(self, page: Page, recorder, base_url: str, *, patience: float = 1.0):
        self.page = page
        self.base = base_url.rstrip("/")
        self.patience = patience
        self._b = _BrowserStep(recorder, page, "founder")

    def sent(self, project_id: str) -> None:
        if not self.page.url.split("?")[0].endswith(f"/p/{project_id}/interviews/sent"):
            self.page.goto(f"{self.base}/p/{project_id}/interviews/sent", wait_until="load")
        self.page.locator(".sent__kinds").wait_for(state="visible", timeout=60_000 * self.patience)

    def line(self) -> dict:
        """The persona line as drawn: its state, words, bar and action."""
        line = self.page.get_by_test_id("persona-line")
        if not line.count():
            return {"state": None, "text": ""}
        bar = line.locator("[role=progressbar]")
        action = line.get_by_test_id("change-who-asks")
        return {"state": line.get_attribute("data-state"), "text": _words(line),
                "bar": ({"now": bar.get_attribute("aria-valuenow"), "max": bar.get_attribute("aria-valuemax")}
                        if bar.count() else None),
                "action": _words(action) or None,
                "try_again": line.get_by_test_id("persona-try-again").count() > 0}

    def wait_state(self, state: str, *, timeout_s: float = 45) -> dict:
        """The line in place reaching `state` (keel-web polls `GET interviewer` every 10 s while RECORDING)."""
        self.page.locator(f'[data-testid=persona-line][data-state="{state}"]').wait_for(
            state="visible", timeout=timeout_s * 1000 * self.patience)
        return self.line()

    def cards(self) -> list[dict]:
        """Each kind's card: its label, *Try it yourself* (enabled or not, its words) and the primary's words."""
        out = []
        for card in self.page.locator(".sent__kinds .role").all():
            tryit = card.get_by_test_id("try-it-yourself")
            out.append({"label": _words(card.locator(".role__label").first),
                        "try": {"text": _words(tryit), "enabled": tryit.is_enabled()} if tryit.count() else None,
                        "primary": _words(card.locator(".btn.primary").first)})
        return out

    def record(self, face: str, *, expect_status: int | None = None) -> dict:
        """*Change who asks* / *Record the interviewer* -> the popup -> the face -> *Record {Face}*: what the popup drew,
        the POST keel-web sent and what it received; on a refusal the popup's words (it stays open; Cancel closes)."""
        with self._b.step(f"founder picks {face.title()} in the persona line's popup") as h:
            self.page.get_by_test_id("change-who-asks").click()
            popup = self.page.get_by_test_id("change-face-popup")
            popup.wait_for(state="visible", timeout=10_000)
            drawn = {"title": _words(popup.locator("h2").first), "lead": _words(popup.locator(".ccard__sub").first),
                     "faces": [b.get_attribute("data-face") for b in popup.locator('button[role="radio"]').all()]}
            popup.locator(f'[data-face="{face}"]').click()
            confirm = popup.get_by_test_id("change-face-confirm")
            drawn["confirm"] = _words(confirm)
            with self.page.expect_response(lambda r: r.request.method == "POST"
                                           and r.url.endswith("/interviewer/face"), timeout=30_000) as posted:
                confirm.click()
            out = {"popup": drawn, "sent": posted.value.request.post_data_json, "status": posted.value.status,
                   "body": _json(posted.value)}
            if posted.value.status >= 400:
                popup.locator(".remedy, [role=alert], .banner").first.wait_for(state="visible", timeout=10_000)
                out["refusal"] = _words(popup.locator(".remedy, [role=alert], .banner").first)
                out["popup_text"] = _words(popup)
                h.add_screenshot(self._b.screenshot("change-face-refused"))
                popup.get_by_role("button", name="Cancel", exact=True).click()
            else:
                popup.wait_for(state="hidden", timeout=10_000)
            h.add_screenshot(self._b.screenshot(f"persona-{face.lower()}"))
            return out

    def formats_now(self, kind_label: str) -> dict:
        """S3: *Send more*'s format row on a kind's card, read and cancelled (nothing is made)."""
        card = self.page.locator(".sent__kinds .role",
                                 has=self.page.locator(".role__label", has_text=re.compile(
                                     rf"^{re.escape(kind_label)}$"))).first
        card.locator(".btn.primary").click()
        dialog = self.page.get_by_role("dialog")
        dialog.locator("[role=radiogroup] [role=radio]").first.wait_for(state="visible", timeout=10_000)
        rows = {}
        for radio in dialog.locator("[role=radiogroup] [role=radio]").all():
            word = radio.locator(".fmt__na")
            rows[_words(radio.locator(".fmt__name").first)] = {
                "disabled": radio.is_disabled(), "checked": radio.get_attribute("aria-checked") == "true",
                "word": _words(word) if word.count() else None}
        out = {"rows": rows, "hint": _words(dialog.locator(".hint").first), "text": _words(dialog)}
        dialog.get_by_role("button", name="Cancel", exact=True).first.click()
        dialog.wait_for(state="hidden", timeout=10_000)
        return out

    def walkthrough_again(self) -> dict:
        """*How it works* on Sent's header plays W1 again: its frames' titles (frame 2 is who asks), then *Got it*."""
        with self._b.step("founder replays How it works: W1's four frames") as h:
            self.page.get_by_role("button", name=HOW_IT_WORKS, exact=True).click()
            strip = self.page.locator(".wtstrip")
            strip.wait_for(state="visible", timeout=10_000)
            frames = [_words(f.locator("b, h3, strong").first) or _words(f) for f in strip.locator(".wtframe").all()]
            drawn = {"frames": frames, "texts": [_words(f) for f in strip.locator(".wtframe").all()],
                     "intro": _words(self.page.locator(".corridor__intro").first)}
            h.add_screenshot(self._b.screenshot("walkthrough-again"))
            self.page.get_by_role("button", name=WALKTHROUGH_GOT_IT, exact=True).click()
            self.page.locator(".sent__kinds").wait_for(state="visible", timeout=30_000)
            return drawn

    def l1_again(self, project_id: str) -> dict:
        """L1 revisited on a locked project (the carousel, disabled; no button): its whole text, for the no-price rule."""
        self.page.goto(f"{self.base}/p/{project_id}/define/ready/interviewer", wait_until="load")
        main = self.page.locator(".corridor.before").first
        main.wait_for(state="visible", timeout=30_000)
        self.page.get_by_test_id("face-carousel").wait_for(state="visible", timeout=20_000)
        carousel = self.page.get_by_test_id("face-carousel")
        return {"text": _words(main), "faces": [b.get_attribute("data-face")
                                                for b in carousel.locator('button[role="radio"]').all()],
                "checked": [b.get_attribute("data-face") for b in
                            carousel.locator('button[role="radio"][aria-checked="true"]').all()]}

    def try_it(self, project_id: str, role_label: str) -> None:
        """*Try it yourself* on the kind's card: the dry run's route."""
        card = self.page.locator(".sent__kinds .role",
                                 has=self.page.locator(".role__label", has_text=re.compile(
                                     rf"^{re.escape(role_label)}$"))).first
        card.get_by_test_id("try-it-yourself").click()
        self.page.wait_for_url(re.compile(rf"/p/{project_id}/interviews/try/"), timeout=20_000)


# --------------------------------------------------------------------------------------------- the player

class Player:
    """The AI interviewer's page, for a stranger (a link) or the founder (Try it yourself): driven through the speech
    seam, a tap, a typed field or *Type instead*, the way a person would."""

    def __init__(self, page: Page, recorder, *, party: str = "participant", patience: float = 1.0):
        self.page = page
        self.patience = patience
        self._b = _BrowserStep(recorder, page, party)
        self.requests: list[dict] = []
        page.on("request", self._keep)

    def _keep(self, request) -> None:
        if "/v2/" in request.url and request.method != "GET":
            self.requests.append({"method": request.method, "url": request.url})

    # ---- arriving
    def open(self, url: str) -> dict:
        self.page.goto(url, wait_until="load")
        intro = self.page.get_by_test_id("ai-intro")
        intro.wait_for(state="visible", timeout=30_000)
        return self.intro()

    def intro(self) -> dict:
        intro = self.page.get_by_test_id("ai-intro")
        start = self.page.get_by_test_id("start-talking")
        heard = self.page.get_by_test_id("ai-mic-heard")
        return {"intro": intro.get_attribute("data-intro"), "heading": _words(intro.locator("h1").first),
                "text": _words(intro),
                "buttons": [t for t in ("start-talking", "choice-talk", "choice-write")
                            if self.page.get_by_test_id(t).count()],
                "mic_test": self.page.get_by_test_id("ai-mic-test").count() > 0,
                "mic_heard": _words(heard) or None,
                "start_enabled": start.is_enabled() if start.count() else None}

    def mic_test(self, heard: str = "hello", *, timeout_s: float = 15) -> dict:
        """keel-web 072 FR-7: *Test your mic* -> the seam's microphone (always granted) -> *Say hello* -> `heard` said
        -> *Heard: hello* with its tick, and *Start the interview* enabled. What the intro drew before and after."""
        before = self.intro()
        made = self.ear()["count"]
        self.page.get_by_test_id("ai-mic-test").click()
        deadline = timeout_s * 1000 * self.patience
        # the one-shot recogniser is made by the press, after the microphone is granted: speak once it listens
        self.wait_ear(newer_than=made, timeout_s=timeout_s)
        said = self.say(heard, True)
        line = self.page.get_by_test_id("ai-mic-heard")
        line.wait_for(state="visible", timeout=deadline)
        self.page.locator("[data-testid=start-talking]:not([disabled])").wait_for(timeout=deadline)
        return {"before": before, "said": said, "after": self.intro()}

    def start(self, testid: str = "start-talking") -> None:
        """The intro's button -- pressed again while the page is still the intro: a press that lands before the app
        has hydrated is lost (seen once on S-006: the intro drawn, the stage never left it). Since keel-web 072 it is
        enabled by *Test your mic* (or its fallback), so the leg tests the mic first."""
        button = self.page.get_by_test_id(testid)
        for _ in range(5):
            button.click()
            try:
                self.page.get_by_test_id("ai-intro").wait_for(state="detached", timeout=3_000)
                return
            except Exception:  # noqa: BLE001 - still the intro: press again
                if not button.count():
                    return
        raise AssertionError(f"the intro never left on {testid}")

    # ---- the stage
    def phase(self) -> str | None:
        stage = self.page.get_by_test_id("ai-stage")
        return stage.get_attribute("data-phase") if stage.count() else None

    def wait_phase(self, *phases: str, timeout_s: float = 30) -> str:
        sel = ", ".join(f'[data-testid=ai-stage][data-phase="{p}"]' for p in phases)
        self.page.locator(sel).first.wait_for(state="attached", timeout=timeout_s * 1000 * self.patience)
        return self.phase() or ""

    def stage(self) -> dict:
        video = self.page.locator("video.aiv-stage__video")
        return {"phase": self.phase(), "where": _words(self.page.get_by_test_id("ai-where")),
                "state": _words(self.page.get_by_test_id("ai-state")),
                "mark": _words(self.page.get_by_test_id("ship-mark")),
                "videos": video.count(), "clip": video.first.get_attribute("data-clip") if video.count() else None}

    # ---- the sheet
    def sheet(self) -> dict:
        sheet = self.page.get_by_test_id("ai-sheet")
        options = sheet.locator("[data-testid=ai-options] .opt")
        field = sheet.get_by_test_id("ai-field")
        return {"question": _words(sheet.locator(".iv-q").first), "kicker": _words(sheet.locator(".iv-kicker").first),
                "options": [{"label": _words(o), "checked": o.get_attribute("aria-checked") == "true",
                             "role": o.get_attribute("role")} for o in options.all()],
                "field": field.input_value() if field.count() else None,
                "chip": _words(sheet.locator(".iv-chips .chip").first) or None,
                "preview": _words(sheet.get_by_test_id("ai-preview")),
                "heard": _words(sheet.get_by_test_id("ai-heard")),
                "status": _words(sheet.get_by_test_id("ai-status")),
                "banner": _words(sheet.get_by_test_id("ai-banner")) or None}

    def say(self, text: str, final: bool = True) -> bool:
        """The stranger speaks into the newest recogniser. A final ends the utterance (the seam's recogniser then ends,
        keel-web 072 FR-3), and the page sends what it heard to `classify`; nothing is pressed after it."""
        return bool(self.page.evaluate("([t, f]) => window.__say(t, f)", [text, final]))

    def ear(self) -> dict:
        """The seam's recognisers: how many the page has made, and whether the newest is listening (started, not
        stopped)."""
        return self.page.evaluate("""() => { const s = window.__speech || []; const r = s[s.length - 1];
            return { count: s.length, live: !!(r && r.started && !r.stopped) }; }""")

    def wait_ear(self, *, newer_than: int | None = None, timeout_s: float = 20) -> dict:
        """A recogniser listening -- one made after `newer_than` recognisers when given (a window opened again after
        a clip)."""
        deadline = timeout_s * 1000 * self.patience
        waited = 0.0
        while waited <= deadline:
            ear = self.ear()
            if ear["live"] and (newer_than is None or ear["count"] > newer_than):
                return ear
            self.page.wait_for_timeout(100)
            waited += 100
        raise AssertionError({"no recogniser listening": self.ear(), "newer than": newer_than,
                              "phase": self.phase(), "status": self.status()})

    def status(self) -> str:
        return _words(self.page.get_by_test_id("ai-status"))

    def question(self) -> str:
        return _words(self.page.get_by_test_id("ai-sheet").locator(".iv-q").first)

    def wait_status(self, *words: str, timeout_s: float = 20) -> str:
        """The sheet's status line reading one of `words` (keel-web 072 FR-9)."""
        deadline = timeout_s * 1000 * self.patience
        waited = 0.0
        while waited <= deadline:
            now = self.status()
            if any(w in now for w in words):
                return now
            self.page.wait_for_timeout(100)
            waited += 100
        raise AssertionError({"status never read": words, "it read": self.status(), "phase": self.phase()})

    def hold(self, *, timeout_s: float = 20) -> dict:
        """A confident read held (keel-web 072 FR-4): the status reads *Got it. Moving on… say no to change* with the
        pick lit, and -- nothing said, nothing tapped -- the question goes on by itself. What the hold drew, and the
        question that came after it."""
        before = self.question()
        status = self.wait_status(HELD, timeout_s=timeout_s)
        sheet = self.sheet()
        rings = self.page.locator("[data-testid=ai-sheet] .aiv__ring").count()
        deadline = timeout_s * 1000 * self.patience
        waited = 0.0
        while waited <= deadline and self.question() == before and HELD in self.status():
            self.page.wait_for_timeout(100)
            waited += 100
        return {"question": before, "status": status, "lit": [o["label"] for o in sheet["options"] if o["checked"]],
                "heard": sheet["heard"], "ring": rings > 0, "next": self.question(),
                "went_on": self.question() != before or HELD not in self.status()}

    def veto(self, word: str = VETO, *, final: bool = False) -> dict:
        """A word of protest in the hold (FR-4): the hold ends and the question reopens, the pick still lit. Said as an
        interim by default -- keel-web 072 hears a veto in an interim or a final, and keeps the same recogniser for the
        question (its call 5), so what is said next is the new answer, not "no" read on its own."""
        before = self.question()
        self.wait_status(HELD)
        self.wait_ear()                                 # the hold's window listening
        self.say(word, final)
        waited = 0
        while waited < 5_000 * self.patience and HELD in self.status():
            self.page.wait_for_timeout(100)
            waited += 100
        reopened = self.question() == before and HELD not in self.status()
        return {"question": before, "said": word, "reopened": reopened, "status": self.status(),
                "lit": [o["label"] for o in self.sheet()["options"] if o["checked"]]}

    def confirming(self, *, timeout_s: float = 20) -> dict:
        """An unsure read (FR-2): *Is that right? Say yes, or tell me the right one*, the pick lit, the Yes chip."""
        status = self.wait_status(IS_THAT_RIGHT, timeout_s=timeout_s)
        sheet = self.sheet()
        unsure = [_words(o) for o in self.page.locator('[data-testid=ai-sheet] .opt[data-unsure="true"]').all()]
        yes = self.page.get_by_test_id("ai-yes")
        return {"question": self.question(), "status": status,
                "lit": [o["label"] for o in sheet["options"] if o["checked"]], "unsure": unsure,
                "yes": _words(yes) if yes.count() else None}

    def yes(self, *, by: str = "say") -> None:
        """Agreeing to "Is that right?": *Yes, that's it* tapped, or "yes" said -- straight on, no hold."""
        if by == "tap":
            self.page.get_by_test_id("ai-yes").click()
        else:
            self.say(SAY_YES, True)

    def back(self, *, by: str = "tap") -> dict:
        """The way back (FR-6): *‹ Back to question n* tapped, or "go back" said, from the next question -- the previous
        question reopens with its answer lit, no clip replayed."""
        before = self.question()
        button = self.page.get_by_test_id("ai-back")
        drawn = _words(button) if button.count() else None
        if by == "say":
            self.say(GO_BACK, True)
        else:
            button.click()
        deadline = 10_000 * self.patience
        waited = 0.0
        while waited <= deadline and self.question() == before:
            self.page.wait_for_timeout(100)
            waited += 100
        sheet = self.sheet()
        return {"from": before, "button": drawn, "by": by, "to": self.question(),
                "lit": [o["label"] for o in sheet["options"] if o["checked"]], "field": sheet["field"]}

    def timeline(self) -> list[dict]:
        """`FLOW_TIMELINE`'s events, or none where the init script was not installed."""
        try:
            return list(self.page.evaluate("() => window.__keelFlow ? window.__keelFlow() : []") or [])
        except Exception:  # noqa: BLE001 - a page that has gone
            return []

    def statuses(self) -> list[dict]:
        """`FLOW_TIMELINE`'s status words, in order (`window.__keelPhases`)."""
        try:
            return list(self.page.evaluate("() => window.__keelPhases ? window.__keelPhases() : []") or [])
        except Exception:  # noqa: BLE001
            return []

    def saw_thats_my_answer(self) -> bool | None:
        try:
            return self.page.evaluate("() => window.__keelSawAnswer ? window.__keelSawAnswer() : null")
        except Exception:  # noqa: BLE001
            return None

    def save(self) -> None:
        """*Save and next* -- typed words keep their explicit press (072 FR-5)."""
        self.page.get_by_test_id("ai-sheet").get_by_role("button", name=SAVE_AND_NEXT, exact=True).click()

    def finish(self) -> None:
        """*Finish* on the pilot ask (072 FR-2: the pilot keeps it)."""
        button = self.page.get_by_test_id("ai-sheet").get_by_role("button", name=FINISH, exact=True)
        button.wait_for(state="visible", timeout=10_000 * self.patience)
        button.click()

    def tap(self, label: str) -> None:
        self.page.get_by_test_id("ai-sheet").locator("[data-testid=ai-options] .opt", has_text=re.compile(
            rf"^\s*{re.escape(label)}\s*$")).first.click()

    def tap_chip(self) -> None:
        self.page.get_by_test_id("ai-sheet").locator(".iv-chips .chip").first.click()

    def type_instead(self, text: str) -> None:
        """*Type instead*, the words typed; *Save and next* (`save`) sends them on."""
        self.page.get_by_test_id("ai-type").click()
        self.page.get_by_test_id("ai-typed").fill(text)

    def fill_field(self, value: str) -> None:
        self.page.get_by_test_id("ai-field").fill(value)

    def unit(self, mode: str) -> None:
        """The amount-or-hours toggle: *Hours*, or *Amount* (its label carries the currency)."""
        name = re.compile(r"^Hours$") if mode == "HOURS" else re.compile(r"^Amount")
        self.page.get_by_test_id("ai-sheet").get_by_role("radiogroup", name="Hours or amount").get_by_role(
            "radio", name=name).click()

    def end(self) -> None:
        self.page.get_by_test_id("ai-end").click()

    def done(self, *, timeout_s: float = 20) -> dict:
        done = self.page.get_by_test_id("ai-done")
        done.first.wait_for(state="visible", timeout=timeout_s * 1000)
        return {"text": _words(done.first), "tryRun": done.first.get_attribute("data-try-run") == "true"}

    def where_it_stood(self) -> dict:
        """What the page drew when a wait gave up: the stage, the sheet, the intro or the end, and the requests."""
        out: dict = {"url": self.page.url}
        try:
            out["stage"] = self.stage()
            if self.page.get_by_test_id("ai-sheet").count():
                out["sheet"] = self.sheet()
            out["body"] = " ".join((self.page.locator("body").text_content() or "").split())[:1500]
        except Exception as broken:  # noqa: BLE001 - a diagnostic never hides the failure it explains
            out["unreadable"] = repr(broken)
        out["requests"] = self.requests[-10:]
        return out

    def screenshot(self, name: str):
        return self._b.screenshot(name)

    def step(self, name: str):
        return self._b.step(name)
