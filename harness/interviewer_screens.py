"""keel-web 069's AI interviewer, as page objects (spec 044 T003; keel-web master `d23895f`).

Machinery, not judgement: every class here acts and reads, and asserts nothing -- `evals/interviewer_leg.py` judges.
The words are copied from keel-web `src/lib/translate.ts` at `d23895f`; the selectors are the ones 069's tasks.md names
for this repository (*Selectors (for keel-e2e-eval 044)*).

* `Persona`   -- Sent's persona line (`[data-testid=persona-line]`, `data-state`), its progress bar, *Change who asks* /
                 *Record the interviewer* and the popup (`[data-testid=change-face-popup]`, the carousel,
                 `[data-testid=change-face-confirm]`), the role cards' *Try it yourself*, Send more's format row read
                 and cancelled, W1 replayed through *How it works*, L1 revisited.
* `Player`    -- the AI interviewer's page for a stranger or the founder's dry run: the intros, the stage (`data-phase`,
                 the one `<video>`, the pills, End, the ship mark), the sheet (options, field, escape, preview, heard,
                 *That's my answer*, *Next question* / *Finish*, *Type instead*) and the end screens.
* `SPEECH_SEAM` -- the init script that stands in for the browser's recogniser through the test build's own seam
                 (`window.__keelSpeech`, present only under `vite --mode test`, which the stack serves): keel-web's own
                 `tests/fixtures/interviewer/fakeSpeech.ts`, restated in JavaScript. `__say(text, final)` is the
                 stranger speaking. No microphone is opened.

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
THATS_MY_ANSWER = "That’s my answer"
FINISH = "Finish"
NEXT_QUESTION = "Next question"


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
#: the app does; the app reads the seam only in a test-mode build).
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
  window.__keelSpeech = { Recognition: FakeRecognition, recorder: null };
  const last = () => (window.__speech || [])[(window.__speech || []).length - 1];
  window.__say = (text, final) => {
    const r = last();
    if (!r) return false;
    r.results.push({ isFinal: !!final, 0: { transcript: text }, length: 1 });
    if (r.onresult) r.onresult({ resultIndex: r.results.length - 1, results: r.results });
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
        return {"intro": intro.get_attribute("data-intro"), "heading": _words(intro.locator("h1").first),
                "text": _words(intro),
                "buttons": [t for t in ("start-talking", "choice-talk", "choice-write")
                            if self.page.get_by_test_id(t).count()]}

    def start(self, testid: str = "start-talking") -> None:
        """The intro's button -- pressed again while the page is still the intro: a press that lands before the app
        has hydrated is lost (seen once on S-006: the intro drawn, the stage never left it)."""
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
        return bool(self.page.evaluate("([t, f]) => window.__say(t, f)", [text, final]))

    def answer(self) -> None:
        """*That's my answer*."""
        button = self.page.get_by_test_id("ai-answer")
        button.wait_for(state="visible", timeout=10_000)
        self.page.locator('[data-testid=ai-answer]:not([disabled])').wait_for(timeout=10_000)
        button.click()

    def next(self) -> None:
        """*Next question* / *Finish*, once the answer is held."""
        self.page.get_by_test_id("ai-next").wait_for(state="visible", timeout=10_000)
        self.page.get_by_test_id("ai-next").click()

    def tap(self, label: str) -> None:
        self.page.get_by_test_id("ai-sheet").locator("[data-testid=ai-options] .opt", has_text=re.compile(
            rf"^\s*{re.escape(label)}\s*$")).first.click()

    def tap_chip(self) -> None:
        self.page.get_by_test_id("ai-sheet").locator(".iv-chips .chip").first.click()

    def type_instead(self, text: str) -> None:
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
