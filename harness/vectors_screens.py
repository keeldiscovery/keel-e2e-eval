"""keel-web's vector-corridor screens, as page objects (spec 039; spec 041: keel-web 063 and 064).

Machinery, not judgement: every class here acts and reads, and asserts nothing -- the scenario
(`evals/corpus_scenario.py`) judges what they read. The labels a page object **presses** are spelled
once, below, copied from keel-web `src/lib/translate.ts`; a copy change in keel-web shows up as a
named mismatch rather than as a fifteen-second wait on nothing (the rule DRIFT #71 taught).

Four groups, in the journey's order:

* `Corridor`   -- the founder's five steps under `/p/{id}/define/...` (keel-web 063: one dimension a
                  screen): the context, the two seeds and their cards, Prevalence / Frequency / the cost /
                  the price on one screen each, every list dimension's *Answer* -> *Check and save* ->
                  *Choose*, S2 (the idea's three lines, checked), the persona, and step 5 (the word, the
                  pilot, *Lock and write the questions*). Each screen reads its frame: the kicker, the
                  stage counter (*Problem · 3 of 4*) and its dots, and the side nav's lock.
* `PeopleLinks` -- the People page's two send popups: the specialist's three steps and, on a B2B
                  study, the decision-maker's commercial link.
* `Interview`  -- the stranger's `/i/{token}` pager (keel-web 064): intro, the decision-maker's idea
                  screen, the gate, every item as served (kicker, stem, options, one escape last), the
                  reveal, done.
* `GuideWelcome` -- keel-web 080's welcome sheet over a new project's first screen (spec 054): the face, the live
                  caption, the snippet, Skip (the one control), *Play the welcome again*, and the test build's seam;
                  `GuideWire` keeps what the page sent and received about it (the `guide-seen` POSTs, the overviews).
* `Answers`    -- the board (`/p/{id}`), the stage pages (`/p/{id}/s/{VECTOR}`) with one row's
                  per-person list, the overview's pilot tile, and keel-web 065's brief: page one
                  (`/p/{id}/brief`, and the download's `/p/{id}/print`) and page two
                  (`/p/{id}/brief/breakdown`).
"""

from __future__ import annotations

import re
import time
from typing import Any, Callable

from playwright.sync_api import Page

from harness import interviewer_screens as ivs
from harness.browser import _SCREEN_TEXT_JS, _BrowserStep, _safe_all_texts, _safe_text, _screen_text
from harness.steps import Recorder

# ------------------------------------------------------------------- keel-web's own words (pressed)

CONTEXT_SAVE = "Save and continue"
CONTEXT_YES = "Yes, that's it"
SEED_SEND = "Send"
CARD_YES_PROBLEM = "Yes, that's the problem"
CARD_LOOKS_RIGHT = "Looks right"
#: Until keel-web 070 F8: the mechanism card's *Someone else would use it* link and its *Who would use it instead?* box.
SOMEONE_ELSE_USES = ("Someone else would use it", "Who would use it instead?")
KICKER_INTERPRETATION = "Here's what Keel understood"
KICKER_MECHANISM = "Here's the mechanism Keel understood"
KICKER_CONTEXT = "Keel understands"
CONTINUE = "Continue"
SAVE = "Save"
#: `STAGE_EXIT_LABEL`: a stage's last screen names where it goes next (design §4: P6, S10, C11).
STAGE_EXIT = {"PROBLEM": "Save and continue to the solution",
              "SOLUTION": "Continue to paying",
              "COMMERCIAL": "Save and continue to Before people see it"}
UNSURE_CHIP = "I'm not sure"
PRICE_NONE_CHIP = "No price yet"
LEAVE_OUT_CHIP = "Leave this out of the study"
LIST_DRAFTING = "Keel is writing this from your answer."
COST_MODE_GROUP = "Measured as"
COST_MODE_WORD = {"AMOUNT": "Fixed amount", "HOURS": "Hours"}
PERSONA_QUESTION = "Who makes the buying decision?"
PERSONA_SAME = "The same person would decide to pay"
PERSONA_SOMEONE_ELSE = "Someone else would decide"
PERSONA_ROLE = "If someone else, what role would that person typically have?"
BEFORE_CONTINUE = "Continue"
BEFORE_LOCK = "Lock and write the questions"           # until keel-web 069
#: keel-web 069 `translate.ts`: L1, the third screen of step 5.
L1_TITLE = "Who asks the questions"
BEFORE_LOCK_RECORD = "Lock and record the interviewer"
BEFORE_LOCK_APPROVE = "Lock and approve"
BEFORE_INTERVIEWER_OWN = "The AI interviewer needs Keel's credits; links go out as text."
NAV_LOCK_LINE = "Opens once you start recruiting"
NAV_LOCKED_LABEL = "Project sections, locked until recruiting starts"
SEND_THE_QUESTIONS = "Send the questions"
SEND_NAME = "Their name"
SEND_NEXT = re.compile(r"Next — see what they.ll be asked")
MAKE_THEIR_LINK = "Make their link"

IV_BEGIN = "Begin"
IV_CONTINUE = "Continue"
IV_NEXT = "Next"
IV_SEND = "Send my answers"
IV_YES = "Yes"
IV_NO = "No"
IV_COST_MODE_GROUP = "Measured as"
IV_COST_MODE_WORD = {"AMOUNT": "Amount", "HOURS": "Hours"}
IV_PICK_TWO = "Pick two."
IV_TWO_PICKED = "2 of 2 picked. Untick one to change."


def gate_chip_word(occasion: str | None) -> str:
    """keel-web `gateChipWord`: the gate story's one chip (contract 13: CANT_RECALL alone)."""
    return f"I can't recall one particular {(occasion or '').strip() or 'time'}"


def _wait_url(page: Page, pattern: str, *, timeout_s: float = 30) -> None:
    page.wait_for_url(re.compile(pattern), timeout=timeout_s * 1000)


def _button(page, name, *, exact: bool = True):
    return page.get_by_role("button", name=name, exact=exact) if isinstance(name, str) else \
        page.get_by_role("button", name=name)


def _first_text(scope, selector: str) -> str:
    """The first match's text, or "" at once when nothing matches -- never Playwright's thirty-second
    wait for an element a screen variant does not draw (the decider banner on a B2C page)."""
    try:
        found = scope.locator(selector)
        return found.first.inner_text() if found.count() else ""
    except Exception:  # noqa: BLE001 - a read, never load-bearing
        return ""


def _text(page: Page) -> str:
    """The rendered words of the page's working region: `main` where keel-web draws one, the body
    otherwise (the founder's shell has no `<main>`)."""
    return _screen_text(page, "main") or _screen_text(page, "body")


def _number(value) -> str:
    value = float(value)
    return str(int(value)) if value.is_integer() else str(value)


def _tc(locator) -> str:
    """The first match's DOM words (`text_content`, not the CSS's capitals), "" at once when nothing matches."""
    try:
        return " ".join((locator.first.text_content() or "").split()) if locator.count() else ""
    except Exception:  # noqa: BLE001 - a read
        return ""


def _words(locator) -> str:
    """The first match's DOM words with a space between every text node (`_SCREEN_TEXT_JS`), so two elements' words
    never run together ("Low." + "Smallest" reads "Low. Smallest", not "Low.Smallest"): what a token is cut from."""
    try:
        return (locator.first.evaluate(_SCREEN_TEXT_JS) or "") if locator.count() else ""
    except Exception:  # noqa: BLE001 - a read
        return ""


def _value(locator) -> str:
    try:
        return locator.input_value()
    except Exception:  # noqa: BLE001 - a read
        return ""


def _json_body(response) -> dict:
    try:
        body = response.json()
    except Exception:  # noqa: BLE001 - an empty or non-JSON body
        return {}
    return body if isinstance(body, dict) else {"body": body}


# ------------------------------------------------------------------- keel-web 080's guide (spec 054)
#
# The six test ids, the seam's name and the files, spelled once (keel-web `specs/080-guide-welcome/spec.md` FR-6,
# FR-1, FR-2.7). The page objects press and read by these and never by words (054 judgement call 2).

GUIDE_WELCOME = "[data-testid='guide-welcome']"
GUIDE_FACE = "[data-testid='guide-face']"
GUIDE_CAPTION = "[data-testid='guide-caption']"
GUIDE_SNIPPET = "[data-testid='guide-snippet']"
GUIDE_SKIP = "[data-testid='guide-skip']"
GUIDE_REPLAY = "[data-testid='guide-replay']"
#: `window.__keelGuide {seek(seconds), cuesFired[]}` -- keel-web's test build only (`import.meta.env.MODE === "test"`).
GUIDE_SEAM = "__keelGuide"
#: The welcome's files, keel-web's own `public/guide/` (design D29).
WELCOME_CUES_PATH = "/guide/welcome.cues.json"
WELCOME_CAPTIONS = "welcome.vtt"
#: keel-web 080 judgement call 2: *Play the welcome again* lives at the foot of the Feedback panel; the panel's trigger
#: is `FeedbackTab`'s one button (`.fb-tab`, `aria-haspopup="dialog"`), the right-edge tab above 720 px.
FEEDBACK_TRIGGER = "button.fb-tab[aria-haspopup='dialog']"
#: The project's first screen has drawn: the shell's main column holds something.
PROJECT_SCREEN = ".shell--project .shell__main > *"
GUIDE_SEEN_PATH = re.compile(r"/v2/projects/[^/?#]+/guide-seen(?:[?#]|$)")
OVERVIEW_PATH = re.compile(r"/v2/projects/([^/?#]+)/overview(?:[?#]|$)")
#: A founder write: anything but a read under one project (the create, `POST /v2/projects`, has no id segment).
PROJECT_WRITE = re.compile(r"/v2/projects/[^/?#]+(?:/[^?#]*)?(?:[?#]|$)")
#: After a press that should post nothing, how long a `guide-seen` request is waited for before "none" is read.
GUIDE_SETTLE_MS = 750

#: One read of the sheet's face, in one round trip: the `<video>`'s state, its captions track, and `currentTime` again
#: 600 ms later (054 judgement call 1: whether the clock moves is recorded, and required only where it decodes).
_FACE_JS = r"""async (sel) => {
  const v = document.querySelector(sel);
  if (!v) return null;
  const track = v.querySelector('track');
  const tt = v.textTracks && v.textTracks.length ? v.textTracks[0] : null;
  const first = {paused: v.paused, muted: v.muted, autoplay: v.autoplay, readyState: v.readyState,
                 currentTime: v.currentTime, error: v.error ? v.error.code : null,
                 duration: Number.isFinite(v.duration) ? v.duration : null, src: v.currentSrc || v.src || ''};
  await new Promise((r) => setTimeout(r, 600));
  return {...first, currentTimeLater: v.currentTime, pausedLater: v.paused, readyStateLater: v.readyState,
          errorLater: v.error ? v.error.code : null,
          track: track ? {src: track.src, kind: track.kind, mode: tt ? tt.mode : null} : null};
}"""

#: Skip's box against the viewport, and what `elementFromPoint` finds at its centre.
_SKIP_JS = r"""(sel) => {
  const s = document.querySelector(sel);
  const vw = window.innerWidth, vh = window.innerHeight;
  if (!s) return {present: false, visible: false, enabled: false, in_view: false, hit: false,
                  viewport: {width: vw, height: vh}};
  const r = s.getBoundingClientRect();
  const cs = getComputedStyle(s);
  const visible = r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none'
                  && parseFloat(cs.opacity || '1') > 0;
  const at = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
  return {present: true, visible, enabled: !s.disabled && s.getAttribute('aria-disabled') !== 'true',
          in_view: r.top >= 0 && r.left >= 0 && r.bottom <= vh && r.right <= vw,
          hit: !!at && (at === s || s.contains(at)), focused: document.activeElement === s,
          words: (s.innerText || '').replace(/\s+/g, ' ').trim(),
          box: {x: r.left, y: r.top, width: r.width, height: r.height}, viewport: {width: vw, height: vh},
          scroll: {x: window.scrollX, y: window.scrollY}};
}"""

#: Every control inside the sheet, with its words and its accessible label.
_CONTROLS_JS = r"""(sel) => {
  const root = document.querySelector(sel);
  if (!root) return [];
  const all = root.querySelectorAll('button, a, input, select, textarea, label, [role=button], [role=link], '
                                    + '[role=checkbox], [role=switch], [tabindex]:not([tabindex="-1"])');
  return Array.from(all).map((el) => ({
    tag: el.tagName.toLowerCase(), testid: el.getAttribute('data-testid'), role: el.getAttribute('role'),
    words: (el.innerText || '').replace(/\s+/g, ' ').trim(), label: el.getAttribute('aria-label'),
    visible: !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length)}));
}"""


def _guide_of(response) -> dict | None:
    """The `Overview.guide` a response carried, `None` when it carried none (a cloud before contract 20)."""
    body = _json_body(response)
    guide = body.get("guide")
    return guide if isinstance(guide, dict) else None


def _request_row(request) -> dict:
    """A request as the record keeps it: method, path, body, and the status it was answered (read after the event)."""
    try:
        body = request.post_data_json
    except Exception:  # noqa: BLE001 - a body that is not JSON
        body = request.post_data
    try:
        response = request.response()
        status = response.status if response is not None else None
    except Exception:  # noqa: BLE001 - a request that failed has no response
        status = None
    return {"method": request.method, "path": request.url.split("?")[0], "body": body, "status": status}


class GuideWire:
    """What the founder's page sent and received about the guide while attached (spec 054): every `guide-seen`
    request, every overview it read (its `guide` and `revision`), and every founder write under the project -- kept as
    Playwright objects in the order they came and read after, never inside the handler (a body read there waits on the
    handler itself). Machinery: it asserts nothing."""

    def __init__(self, page: Page):
        self.page = page
        self.events: list[tuple[str, Any]] = []
        self._on = False

    def attach(self) -> "GuideWire":
        if not self._on:
            self.page.on("request", self._request)
            self.page.on("response", self._response)
            self._on = True
        return self

    def detach(self) -> None:
        if self._on:
            self.page.remove_listener("request", self._request)
            self.page.remove_listener("response", self._response)
            self._on = False

    def _request(self, request) -> None:
        if request.method == "POST" and GUIDE_SEEN_PATH.search(request.url):
            self.events.append(("guide", request))

    def _response(self, response) -> None:
        url, method = response.url, response.request.method
        if method == "GET" and OVERVIEW_PATH.search(url):
            self.events.append(("overview", response))
        elif method in ("PUT", "POST", "PATCH", "DELETE") and PROJECT_WRITE.search(url) \
                and not GUIDE_SEEN_PATH.search(url):
            self.events.append(("write", response))

    def guide_posts(self) -> list[dict]:
        return [_request_row(r) for kind, r in self.events if kind == "guide"]

    def overviews(self) -> list[dict]:
        """Each overview the page received, in order: its `guide` (or None) and `revision`."""
        out = []
        for kind, response in self.events:
            if kind == "overview":
                body = _json_body(response)
                out.append({"guide": _guide_of(response), "revision": body.get("revision"),
                            "status": response.status})
        return out

    def received(self) -> dict | None:
        """The `guide` of the first overview the page received, or None."""
        seen = self.overviews()
        return seen[0]["guide"] if seen else None

    def writes_after_guide(self) -> list[dict]:
        """The founder writes the page made after its first `guide-seen` request, in order."""
        out, after = [], False
        for kind, obj in self.events:
            if kind == "guide":
                after = True
            elif kind == "write" and after:
                out.append({"method": obj.request.method, "path": obj.url.split("?")[0], "status": obj.status})
        return out

    def wait_overview(self, timeout_s: float) -> bool:
        """Waits for the page's first overview response (an event, never a bare sleep); True when one came."""
        if any(kind == "overview" for kind, _ in self.events):
            return True
        try:
            self.page.wait_for_event("response", predicate=lambda r: r.request.method == "GET"
                                     and bool(OVERVIEW_PATH.search(r.url)), timeout=timeout_s * 1000)
        except Exception:  # noqa: BLE001 - none came: the caller reads that
            pass
        return any(kind == "overview" for kind, _ in self.events)


class GuideWelcome:
    """keel-web 080's welcome sheet (spec 054 FR-1): the face, the caption, the snippet, Skip, *Play the welcome again*
    and the test build's seam. Acts and reads; asserts nothing (this module's rule) -- `evals/corpus_scenario.
    leg_welcome` judges what it reads, `evals/guide_marks.py` scores it."""

    def __init__(self, page: Page, recorder: Recorder, base_url: str = ""):
        self.page = page
        self.base = (base_url or "").rstrip("/")
        self._b = _BrowserStep(recorder, page, "founder")
        self.recorder = recorder

    # --------------------------------------------------------------------------------------------- reads

    def present(self, timeout_s: float = 10) -> bool:
        """True once the sheet is visible, False if it never was within `timeout_s`."""
        try:
            self.page.locator(GUIDE_WELCOME).first.wait_for(state="visible", timeout=timeout_s * 1000)
            return True
        except Exception:  # noqa: BLE001 - absence is a reading, not a crash
            return False

    def count(self) -> int:
        return self.page.locator(GUIDE_WELCOME).count()

    def absent(self, after: Callable[[], Any] | None = None, *, timeout_s: float = 15,
               grace_s: float = 5) -> dict:
        """The sheet's count, read only once the page has received the overview that carries `guide` and drawn the
        project's first screen (never a bare sleep). `after` opens the page (a `goto`); the overview is listened for
        from before it. When the overview the page received does not say `welcomeSeen: true` the page could still open
        the sheet (its chunk is lazy), so the sheet is waited for up to `grace_s` before the count is read."""
        responses: list = []

        def keep(response) -> None:
            if response.request.method == "GET" and OVERVIEW_PATH.search(response.url):
                responses.append(response)

        self.page.on("response", keep)
        try:
            if after is not None:
                after()
            if not responses:
                try:
                    self.page.wait_for_event("response", predicate=lambda r: r.request.method == "GET"
                                             and bool(OVERVIEW_PATH.search(r.url)), timeout=timeout_s * 1000)
                except Exception:  # noqa: BLE001 - recorded as no overview
                    pass
            try:
                self.page.locator(PROJECT_SCREEN).first.wait_for(state="visible", timeout=timeout_s * 1000)
                screen = True
            except Exception:  # noqa: BLE001 - recorded
                screen = False
            guide = _guide_of(responses[0]) if responses else None
            if not (guide or {}).get("welcomeSeen") is True:
                try:
                    self.page.locator(GUIDE_WELCOME).first.wait_for(state="attached", timeout=grace_s * 1000)
                except Exception:  # noqa: BLE001 - the expected outcome
                    pass
            count = self.count()
        finally:
            self.page.remove_listener("response", keep)
        return {"count": count, "received": guide, "screen": screen, "overviews": len(responses),
                "url": self.page.url}

    def face(self) -> dict | None:
        """`guide-face`: paused, muted, autoplay, readyState, currentTime and again 600 ms later, the media error's code,
        the duration, and the captions track's src, kind and mode -- one round trip."""
        try:
            return self.page.evaluate(_FACE_JS, GUIDE_FACE)
        except Exception:  # noqa: BLE001 - a read
            return None

    def clock(self) -> float | None:
        """The face's `currentTime` alone (a cheap read, for "before any cue")."""
        try:
            return self.page.evaluate("(sel) => { const v = document.querySelector(sel); "
                                      "return v ? v.currentTime : null; }", GUIDE_FACE)
        except Exception:  # noqa: BLE001 - a read
            return None

    def wait_cue(self, cue_id: str, *, timeout_s: float = 2.0) -> str | None:
        """Waits (a condition, bounded) for the snippet to draw `cue_id` after a seek, then reads `data-cue`."""
        try:
            self.page.locator(f"{GUIDE_SNIPPET}[data-cue='{cue_id}']").first.wait_for(state="attached",
                                                                                     timeout=timeout_s * 1000)
        except Exception:  # noqa: BLE001 - read whatever is drawn
            pass
        return self.cue()

    def caption(self) -> str:
        """The live caption line as drawn (`guide-caption`)."""
        return _tc(self.page.locator(GUIDE_CAPTION))

    def caption_visible(self) -> bool:
        try:
            found = self.page.locator(GUIDE_CAPTION)
            return bool(found.count()) and found.first.is_visible()
        except Exception:  # noqa: BLE001 - a read
            return False

    def cue(self) -> str | None:
        """The snippet's `data-cue`, or None while no cue has fired."""
        try:
            found = self.page.locator(GUIDE_SNIPPET)
            return found.first.get_attribute("data-cue") if found.count() else None
        except Exception:  # noqa: BLE001 - a read
            return None

    def controls(self) -> list[dict]:
        """Every button, link, field and label inside the sheet, with its words and its `aria-label`."""
        try:
            return self.page.evaluate(_CONTROLS_JS, GUIDE_WELCOME) or []
        except Exception:  # noqa: BLE001 - a read
            return []

    def skip_in_view(self) -> dict:
        """Skip's box inside the viewport, and `elementFromPoint` at its centre is Skip (or inside it)."""
        try:
            return self.page.evaluate(_SKIP_JS, GUIDE_SKIP)
        except Exception:  # noqa: BLE001 - a read
            return {"present": False, "visible": False, "enabled": False, "in_view": False, "hit": False}

    def served_cues(self) -> list[dict]:
        """`{web_base}/guide/welcome.cues.json`, as the site serves it."""
        response = self.page.context.request.get(f"{self.base}{WELCOME_CUES_PATH}", timeout=10_000)
        body = response.json() if response.ok else []
        return body if isinstance(body, list) else []

    # ------------------------------------------------------------------------------------------ the seam

    def seam(self) -> bool:
        """True where keel-web's test build put `window.__keelGuide` (absent from a production build)."""
        try:
            return bool(self.page.evaluate("(n) => !!window[n]", GUIDE_SEAM))
        except Exception:  # noqa: BLE001 - a read
            return False

    def seek(self, seconds: float) -> bool:
        """`__keelGuide.seek(seconds)`; False where there is no seam."""
        return bool(self.page.evaluate("([n, s]) => window[n] ? (window[n].seek(s), true) : false",
                                       [GUIDE_SEAM, seconds]))

    def cues_fired(self) -> list[str] | None:
        """`__keelGuide.cuesFired`, or None where there is no seam."""
        try:
            return self.page.evaluate("(n) => window[n] ? Array.from(window[n].cuesFired) : null", GUIDE_SEAM)
        except Exception:  # noqa: BLE001 - a read
            return None

    def hold_face(self) -> bool:
        """Pauses the face so the page's own clock cannot run past a seam walk (the seam drives the cues either way)."""
        try:
            return bool(self.page.evaluate("(sel) => { const v = document.querySelector(sel); "
                                           "if (!v) return false; v.pause(); return true; }", GUIDE_FACE))
        except Exception:  # noqa: BLE001 - a face that would not pause is recorded as False
            return False

    # ------------------------------------------------------------------------------------------- actions

    def _close(self, press: Callable[[], None]) -> dict:
        """Presses, waits for the sheet to go, and returns the `guide-seen` requests the press caused (method, body,
        status) and how long the sheet took to go (None when it never went)."""
        seen: list = []

        def keep(request) -> None:
            if request.method == "POST" and GUIDE_SEEN_PATH.search(request.url):
                seen.append(request)

        self.page.on("request", keep)
        try:
            started = time.monotonic()
            press()
            try:
                self.page.locator(GUIDE_WELCOME).first.wait_for(state="detached", timeout=5_000)
                gone_ms = round((time.monotonic() - started) * 1000)
            except Exception:  # noqa: BLE001 - recorded as never gone
                gone_ms = None
            if not seen:
                try:
                    self.page.wait_for_event("request", predicate=lambda r: r.method == "POST"
                                             and bool(GUIDE_SEEN_PATH.search(r.url)), timeout=GUIDE_SETTLE_MS)
                except Exception:  # noqa: BLE001 - none went out: the reading
                    pass
        finally:
            self.page.remove_listener("request", keep)
        return {"gone_ms": gone_ms, "requests": [_request_row(r) for r in seen]}

    def _press_skip(self) -> None:
        self.page.locator(GUIDE_SKIP).first.click()

    def skip(self) -> dict:
        """Presses Skip; returns `{door, gone_ms, requests}`."""
        with self._b.step("founder presses Skip on the guide's welcome") as h:
            out = {"door": "skip", **self._close(self._press_skip)}
            h.add_screenshot(self._b.screenshot("guide-skipped"))
        return out

    def escape(self) -> dict:
        """Presses Escape (keel-web 080 FR-2.6: Escape is Skip); returns `{door, gone_ms, requests}`."""
        with self._b.step("founder presses Escape on the guide's welcome") as h:
            out = {"door": "escape", **self._close(lambda: self.page.keyboard.press("Escape"))}
            h.add_screenshot(self._b.screenshot("guide-escaped"))
        return out

    def end(self, seconds: float) -> dict:
        """Seeks to the video's end through the seam (local only); the sheet closes by itself. `{door: end, ...}`."""
        with self._b.step(f"the welcome plays to its end ({seconds:.1f} s, through the seam)") as h:
            out = {"door": "end", **self._close(lambda: self.seek(seconds))}
            h.add_screenshot(self._b.screenshot("guide-ended"))
        return out

    def replay(self) -> dict:
        """*Play the welcome again*: `guide-replay` if it is visible, else the Feedback panel's trigger first (080
        judgement call 2), then `guide-replay`. Returns `{found, via, opened, requests}` -- the `guide-seen` requests the
        press and the opening caused."""
        with self._b.step("founder presses Play the welcome again") as h:
            target = self.page.locator(GUIDE_REPLAY).first
            via = "guide-replay"
            if not (self.page.locator(GUIDE_REPLAY).count() and target.is_visible()):
                trigger = self.page.locator(FEEDBACK_TRIGGER)
                if not trigger.count():
                    return {"found": False, "via": None, "opened": False, "requests": []}
                trigger.first.click()
                via = "the Feedback panel"
                try:
                    target.wait_for(state="visible", timeout=5_000)
                except Exception:  # noqa: BLE001 - not there: the reading
                    return {"found": False, "via": via, "opened": False, "requests": []}
            seen: list = []

            def keep(request) -> None:
                if request.method == "POST" and GUIDE_SEEN_PATH.search(request.url):
                    seen.append(request)

            self.page.on("request", keep)
            try:
                target.click()
                opened = self.present(timeout_s=10)
            finally:
                self.page.remove_listener("request", keep)
            h.add_screenshot(self._b.screenshot("guide-replayed"))
        return {"found": True, "via": via, "opened": opened, "requests": [_request_row(r) for r in seen]}

    def pass_by(self, wire: GuideWire, *, timeout_s: float = 5.0) -> dict:
        """Spec 054 FR-6, for every journey that does not judge the welcome: decided from the overview the page received
        (no wait when it says `welcomeSeen: true` or carries no `guide`), else the sheet waited for up to `timeout_s`
        and, if it comes, Skip pressed -- in one `note` step. Absence is not a failure."""
        deadline = time.monotonic() + timeout_s
        received = wire.received() if wire.wait_overview(timeout_s) else None
        overviews = wire.overviews()
        if overviews and (received is None or received.get("welcomeSeen") is True):
            return {"shown": False, "received": received}
        if not self.present(timeout_s=max(0.1, deadline - time.monotonic())):
            return {"shown": False, "received": received}
        with self.recorder.step("the guide's welcome opened over the project's first screen; this journey does not "
                                "judge it and passes it by with Skip (spec 054 FR-6)",
                                party="founder", kind="note") as h:
            out = {"shown": True, "received": received, **self._close(self._press_skip)}
            h.request = {"received": received}
            h.response = out
        return out


# --------------------------------------------------------------------------------------- Corridor

class Corridor:
    """The founder's corridor screens. One instance per founder page.

    `patience` scales the waits that wait on a **model** -- a card landing, questions or a list being
    written -- and nothing else: 1 on the scripted journeys, where the scripted executor answers in
    well under a second, more on S-012, where a host's model writes each one."""

    def __init__(self, page: Page, recorder: Recorder, base_url: str, *, patience: float = 1.0):
        self.page = page
        self.base = base_url.rstrip("/")
        self.patience = patience
        self._b = _BrowserStep(recorder, page, "founder")
        self.conflicts = []
        self.saves = []

    # ------------------------------------------------------------------------ every screen's frame

    def frame(self) -> dict:
        """What frames the screen on display (keel-web 063 FR-003, FR-009): the kicker, *Problem · k of n*
        and its dots (how many, which one is now), the side nav's lock, and (spec 054 FR-2 e) how many welcome
        sheets cover it -- 0 on every frame after the welcome was seen."""
        dots = self.page.locator(".calib__progress .calib__dots i")
        classes = [dots.nth(i).get_attribute("class") or "" for i in range(dots.count())]
        nav = self.page.locator(f"nav[aria-label='{NAV_LOCKED_LABEL}']")
        return {"kicker": _first_text(self.page, ".corridor__kicker"),
                "progress": _first_text(self.page, ".calib__progress > span"),
                "dots": len(classes),
                "now": next((i + 1 for i, c in enumerate(classes) if "now" in c.split()), None),
                "done": sum(1 for c in classes if "done" in c.split()),
                "nav_locked": nav.count() > 0 and NAV_LOCK_LINE in _first_text(self.page, ".side-nav__lockline"),
                "nav_links": self.page.locator("nav.side-nav a").count(),
                "welcome": self.page.locator(GUIDE_WELCOME).count()}

    def _primary(self):
        return self.page.locator(".ccard__foot button.btn.primary").first

    #: Every write a corridor screen's primary refused 409 CONCURRENCY and pressed again (runs/DRIFT.md #80).
    conflicts: list

    def _press_primary(self, expected_label: str | None = None) -> str:
        """Presses the card's primary and waits for the next address; returns the label it carried.

        runs/DRIFT.md #80: a write the page posts at a revision the server has moved past is answered 409
        CONCURRENCY and the screen says nothing -- the founder presses again once the page's 3-second poll
        has the new revision. So does this, once, and keeps the refusal in `conflicts` for the leg to name."""
        primary = self._primary()
        primary.wait_for(state="visible", timeout=20_000)
        label = _safe_text(lambda: primary.inner_text()).strip()
        if expected_label is not None and label != expected_label:
            raise AssertionError(f"the primary reads {label!r}, not {expected_label!r}")
        before = self.page.url
        refused: list = []

        def on_response(response) -> None:
            if response.status == 409 and response.request.method in ("PUT", "POST") \
                    and "/v2/projects/" in response.url:
                refused.append({"url": response.url, "method": response.request.method})

        self.page.on("response", on_response)
        try:
            self.page.wait_for_function("(b) => !b.disabled", arg=primary.element_handle(), timeout=30_000)
            primary.click()
            try:
                self.page.wait_for_function("(u) => window.location.href !== u", arg=before, timeout=10_000)
            except Exception:  # noqa: BLE001 - only a refused write earns the second press
                if not refused:
                    raise
                self.page.wait_for_timeout(4_000)
                self.page.wait_for_function("(b) => !b.disabled", arg=self._primary().element_handle(),
                                            timeout=30_000)
                self._primary().click()
                self.page.wait_for_function("(u) => window.location.href !== u", arg=before, timeout=30_000)
                self.conflicts.append({"screen": before, "refused": refused, "label": label})
        finally:
            self.page.remove_listener("response", on_response)
        return label

    # ------------------------------------------------------------------------ step 1: context

    def context(self, project_id: str, fields: dict, window: dict) -> str:
        """Types the four fields and the window, saves, and waits for the *Keel understands* card.
        Returns the card's sentence as drawn."""
        with self._b.step("founder fills the context step: who, what, when, which people, and the "
                          f"recall window ({window['count']} {window['unit']})") as h:
            self.page.goto(f"{self.base}/p/{project_id}/define/context", wait_until="load")
            self.page.locator("#context-actor").wait_for(state="visible", timeout=20_000)
            for key in ("actor", "job", "circumstance", "segment"):
                self.page.locator(f"#context-{key}").fill(fields[key])
            self.page.locator("input.cwindow__count").fill(str(window["count"]))
            self.page.locator("select.cwindow__unit").select_option(window["unit"])
            h.add_screenshot(self._b.screenshot("context-filled"))
            saved = self._save_context()
            self.saves.append(saved)
            if isinstance(saved.get("status"), int) and saved["status"] >= 400:
                # A refused Save never brings the card (and the screen has no second press): the leg reads
                # `saves` and names what refused it rather than a minute's timeout (spec 054 FR-2 d).
                h.capture_text("stage_screen", _screen_text(self.page, ".ccard"))
                return ""
            self.page.locator(".understands").first.wait_for(state="visible",
                                                             timeout=60_000 * self.patience)
            h.capture_text("stage_screen", _screen_text(self.page, ".ccard"))
            h.add_screenshot(self._b.screenshot("context-card"))
            return _first_text(self.page, ".understands__big")

    #: Every context Save's answer as the page received it (`PUT /v2/projects/{id}/context`): method, path, status.
    saves: list

    def _save_context(self) -> dict:
        try:
            with self.page.expect_response(lambda r: r.request.method == "PUT"
                                           and r.url.split("?")[0].endswith("/context"), timeout=20_000) as got:
                _button(self.page, CONTEXT_SAVE).click()
            response = got.value
            return {"method": "PUT", "path": response.url.split("?")[0], "status": response.status,
                    "body": _json_body(response) if response.status >= 400 else None}
        except Exception as missing:  # noqa: BLE001 - recorded: no Save reached the wire
            return {"method": "PUT", "path": None, "status": None, "error": repr(missing)}

    def context_window_line(self) -> str:
        return _first_text(self.page, ".understands__window")

    def confirm_context(self) -> None:
        with self._b.step("founder confirms: Yes, that's it") as h:
            _button(self.page, CONTEXT_YES).click()
            _wait_url(self.page, r"/define/problem/seed")
            h.add_screenshot(self._b.screenshot("context-confirmed"))

    # --------------------------------------------------------------------- steps 2-3: the seeds

    def seed(self, project_id: str, vector: str, text: str) -> dict:
        """Types the seed into the chat and waits for the card. Returns what the card draws."""
        slug = vector.lower()
        kicker = KICKER_INTERPRETATION if vector == "PROBLEM" else KICKER_MECHANISM
        with self._b.step(f"founder types the {slug} seed and sends it") as h:
            if f"/define/{slug}/seed" not in self.page.url:
                self.page.goto(f"{self.base}/p/{project_id}/define/{slug}/seed", wait_until="load")
            box = self.page.get_by_role("textbox", name=SEED_SEND)
            box.wait_for(state="visible", timeout=20_000)
            box.fill(text)
            _button(self.page, SEED_SEND).click()
            self.page.get_by_text(kicker).first.wait_for(state="visible",
                                                         timeout=60_000 * self.patience)
            h.add_screenshot(self._b.screenshot(f"{slug}-card"))
            claim = _first_text(self.page, ".understood__claim")
            rows = {}
            for row in self.page.locator(".mrow").all():
                label = _first_text(row, ".mrow__label")
                rows[label] = _safe_text(lambda: row.inner_text())
            h.capture_text("stage_screen", _text(self.page))
            return {"claim": claim, "rows": rows, "text": _text(self.page)}

    def confirm_seed(self, vector: str) -> None:
        """The card confirmed: the problem's opens Prevalence; the solution's is the idea's Answer (keel-web
        063 call 1), so it opens S2, the idea's Check screen."""
        slug = vector.lower()
        name = CARD_YES_PROBLEM if vector == "PROBLEM" else CARD_LOOKS_RIGHT
        nxt = r"/define/problem/q/1" if vector == "PROBLEM" else r"/define/solution/idea"
        with self._b.step(f"founder confirms the {slug} card: {name}") as h:
            _button(self.page, name).click()
            _wait_url(self.page, nxt)
            h.add_screenshot(self._b.screenshot(f"{slug}-confirmed"))

    def idea_check(self, name: str | None = None) -> dict:
        """S2 (keel-web 063 FR-007; 070 F7): the idea's three lines, read as drawn, and saved -- Save is the approval --
        and on to the solution's first question. Since keel-cloud 097 the what line is never Keel's draft: it is empty
        with its placeholder (*Name it in up to five words*) and Save off until the founder types a name, which is
        `name`. Returns the lines as drawn (before any edit), the what box's own state, the name typed and the frame."""
        title = ("founder names the idea on S2 and saves it (Save approves)" if name else
                 "founder checks the idea's three lines and saves them (S2: Save approves)")
        with self._b.step(title) as h:
            _wait_url(self.page, r"/define/solution/idea")
            self.page.locator("#idea-what").wait_for(state="visible", timeout=20_000)
            reloaded = False
            try:
                self.page.wait_for_function("() => (document.querySelector('#idea-how')?.value || '') !== ''",
                                            timeout=5_000)
            except Exception:  # noqa: BLE001 - runs/DRIFT.md #78: the stale plan's empty lines
                h.add_screenshot(self._b.screenshot("idea-check-empty"))
                self.page.reload(wait_until="load")
                self.page.locator("#idea-what").wait_for(state="visible", timeout=20_000)
                self.page.wait_for_function(
                    "() => (document.querySelector('#idea-how')?.value || '') !== ''", timeout=20_000)
                reloaded = True
            lines = {line: _value(self.page.locator(f"#idea-{line}")) for line in ("what", "how", "belief")}
            what = self.page.locator("#idea-what")
            unnamed = {"value": lines["what"], "placeholder": what.get_attribute("placeholder") or "",
                       "save_enabled": self._primary().is_enabled()}
            frame = self.frame()
            counter = {"drawn": self._name_counter()}
            h.capture_text("stage_screen", _text(self.page))
            h.add_screenshot(self._b.screenshot("idea-check"))
            if name:
                # keel-web 066 (D14): the counter is live and Save is off over five words -- typed once one word past
                # five, read, then the name itself.
                over = f"{name} {' '.join(['for', 'every', 'single', 'day', 'and', 'night'][:6 - len(name.split())])}"
                what.fill(over)
                counter["over"] = {"typed": over, **self._name_counter()}
                h.add_screenshot(self._b.screenshot("idea-named-over-five"))
                what.fill(name)
                counter["named"] = self._name_counter()
                h.add_screenshot(self._b.screenshot("idea-named"))
            label = self._press_primary(SAVE)
            _wait_url(self.page, r"/define/solution/q/\d+$")
            return {"lines": lines, "unnamed": unnamed, "typed": name, "frame": frame, "primary": label,
                    "reloaded": reloaded, "counter": counter}

    def _name_counter(self) -> dict:
        """keel-web 066's S2 counter under *What it is* (`[data-testid=idea-name-words]`, *n / 5 words*), whether it
        reads over, and whether Save is enabled."""
        wc = self.page.locator("[data-testid=idea-name-words]")
        return {"text": _tc(wc) if wc.count() else None,
                "over": wc.count() > 0 and "calib__wc--over" in (wc.first.get_attribute("class") or ""),
                "save_enabled": self._primary().is_enabled()}

    # -------------------------------------------------- calibration: one screen per single question

    def wait_questions(self, *, timeout_s: float = 60) -> None:
        self.page.locator("h1.calib__q").first.wait_for(
            state="visible", timeout=timeout_s * 1000 * self.patience)

    def single(self, question: dict, answer: dict) -> dict:
        """Answers one single screen -- Prevalence, Frequency, the cost, the price -- for `question` (a
        `CalibrationQuestion` read off the wire) with `answer` (the wire's `CalibrationAnswer`), then the
        primary. Returns what the screen showed just before it: the frame, the belief line, the primary."""
        name = question.get("dimension")
        with self._b.step(f"founder answers {name}") as h:
            self.page.locator("h1.calib__q").first.wait_for(state="visible", timeout=30_000)
            control = question.get("control")
            labels = {o.get("normalized"): o.get("label") for o in question.get("options") or []}
            if answer.get("unsure"):
                chip = PRICE_NONE_CHIP if control == "price_range" else UNSURE_CHIP
                self.page.locator("button.calib__chip", has_text=chip).first.click()
            elif control == "single_choice":
                group = self.page.get_by_role("radiogroup", name=question.get("name"), exact=True)
                group.get_by_role("radio", name=labels[answer["codes"][0]], exact=True).click()
            elif control == "numeric_interval":
                interval = answer["interval"]
                nums = self.page.locator("input.calib__num")
                nums.nth(0).fill(_number(interval["low"]))
                nums.nth(1).fill(_number(interval["high"]))
                unit = self.page.locator("select.calib__unit")
                if unit.count() and unit.first.locator(f"option[value='{interval['unit']}']").count():
                    unit.first.select_option(interval["unit"])
            elif control == "cost_estimate":
                cost = answer["cost"]
                modes = self.page.get_by_role("radiogroup", name=COST_MODE_GROUP, exact=True)
                if modes.count():
                    modes.get_by_role("radio", name=COST_MODE_WORD[cost["mode"]], exact=True).click()
                nums = self.page.locator("input.calib__num")
                nums.nth(0).fill(_number(cost["low"]))
                nums.nth(1).fill(_number(cost["high"]))
                self.page.locator("select.calib__unit").first.select_option(cost["period"])
            elif control == "price_range":
                price = answer["price"]
                nums = self.page.locator("input.calib__num")
                nums.nth(0).fill(_number(price["low"]))
                nums.nth(1).fill(_number(price["high"]))
            else:
                raise AssertionError(f"no single screen for the calibration control {control!r} ({name})")
            seen = {"screen": "single", "frame": self.frame(), "question": _first_text(self.page, "h1.calib__q"),
                    "belief": _first_text(self.page, ".calib__belief-text")}
            h.capture_text("stage_screen", _text(self.page))
            h.add_screenshot(self._b.screenshot(f"calibration-{name}"))
            seen["primary"] = self._press_primary()
            return seen

    # ------------------------------------------- calibration: a list's Answer, Check and save, Choose

    def list_answer(self, question: dict, text: str | None) -> dict:
        """A list dimension's *Answer* (keel-web 063 FR-004): the founder's words typed and Continue --
        which posts `calibration/{vector}/draft` and opens Check -- or, `text` None, *Leave this out of the
        study* and on past this question. Returns the frame and the prompt drawn."""
        name = question.get("dimension")
        with self._b.step(f"founder answers {name} in their own words" if text else
                          f"founder leaves {name} out of the study") as h:
            self.page.locator("textarea.calib__answerbox").first.wait_for(state="visible", timeout=30_000)
            seen = {"screen": "answer", "frame": self.frame(), "question": _first_text(self.page, "h1.calib__q"),
                    "hint": _first_text(self.page, ".calib__hint"),
                    "derived": _first_text(self.page, ".calib__derived")}
            if text:
                self.page.locator("textarea.calib__answerbox").first.fill(text)
                seen["counter"] = _first_text(self.page, ".calib__wc")
            else:
                self.page.locator("button.calib__chip", has_text=LEAVE_OUT_CHIP).first.click()
            h.capture_text("stage_screen", _text(self.page))
            h.add_screenshot(self._b.screenshot(f"answer-{name}"))
            seen["primary"] = self._press_primary(CONTINUE)
            if text:
                _wait_url(self.page, r"/check")
            return seen

    def _list_rows(self) -> dict:
        rows = []
        for li in self.page.locator(".listcheck ul.listrows li.listrow").all():
            locked = li.locator(".listrow__ed--lock")
            if locked.count():
                rows.append({"text": _first_text(li, ".listrow__ed--lock"), "tag": _first_text(li, ".listrow__tag"),
                             "locked": True})
            else:
                rows.append({"text": _value(li.locator("textarea.listrow__ed").first),
                             "tag": _first_text(li, ".listrow__tag"), "locked": False,
                             "counter": _first_text(li, ".listrow__wc"), "warn": _first_text(li, ".listrow__warn")})
        field = self.page.locator(".listcheck .listcheck__field textarea.listrow__ed")
        return {"rows": rows, "field": _value(field.first) if field.count() else None,
                "line": _first_text(self.page, ".listcheck__line"),
                "note": _first_text(self.page, ".listcheck__note"),
                "title": _first_text(self.page, ".listcheck__title")}

    def _keel_test(self) -> dict:
        return {"belief": _first_text(self.page, ".keeltest__t"), "bar": _first_text(self.page, ".keeltest__b"),
                "shown": self.page.locator(".keeltest").count() > 0}

    def importance_rows(self, add: list[str], *, one_more: bool) -> dict:
        """keel-web 070 F9 / 071 on Importance's Check screen: the counter (*yours + n*) and the one-more ask as drawn,
        then the founder's own further difficulties typed in, each into a line *+ Write a difficulty they'd recognise*
        opens. With `one_more` the list is own + 1: *Save* is disabled (keel-web 071; the server's ONE_MORE_NEEDED is
        the backstop) and the harness records that it is, presses nothing, and reads it enabled once three stand.
        Returns what each stage drew."""
        name = "problem.importance"
        counter = lambda: _first_text(self.page, "[data-testid=importance-counter]")  # noqa: E731
        ask = lambda: _first_text(self.page, "[data-testid=importance-one-more]")  # noqa: E731
        rows = self.page.locator(".listcheck ul.listrows li.listrow textarea.listrow__ed")
        out: dict = {"counter": counter(), "ask": ask(), "save_enabled": self._primary().is_enabled(), "added": []}
        with self._b.step(f"founder names {len(add)} more difficult{'y' if len(add) == 1 else 'ies'} on Importance's "
                          "Check screen" + (" while Save waits for three" if one_more else "")) as h:
            h.add_screenshot(self._b.screenshot(f"check-{name}-as-drafted"))
            if one_more:
                # keel-web 071: nothing to press -- Save is off below three; a click on a disabled button sends nothing
                out["save_disabled_below_three"] = not self._primary().is_enabled()
                h.add_screenshot(self._b.screenshot(f"check-{name}-one-more"))
            for label in add:
                before = rows.count()
                self.page.locator(".listcheck__add").first.click()
                self.page.wait_for_function("(n) => document.querySelectorAll("
                                            "'.listcheck ul.listrows li.listrow textarea.listrow__ed').length > n",
                                            arg=before, timeout=10_000)
                rows.nth(rows.count() - 1).fill(label)
                out["added"].append(label)
            out["counter_after"] = counter()
            out["ask_after"] = ask()
            out["save_enabled_after"] = self._primary().is_enabled()
            h.add_screenshot(self._b.screenshot(f"check-{name}-named"))
        return out

    def list_check(self, question: dict, *, timeout_s: float = 60, add: list[str] | None = None,
                   one_more: bool = False) -> dict:
        """*Check and save* (FR-005): waits out *Keel is writing this from your answer.*, reads the drafted
        list as drawn -- every row, the locked ones (*yours*, *context*, *who decides*), the phrase or the
        step, the *Keel will test* box -- and saves it untouched with the primary (*Save*, or the stage's
        exit where the list does not pick). Returns what it read."""
        name = question.get("dimension")
        with self._b.step(f"founder checks Keel's list for {name} and saves it") as h:
            _wait_url(self.page, r"/check")
            self.page.locator(".listcheck").first.wait_for(state="visible",
                                                           timeout=timeout_s * 1000 * self.patience)
            drafting = self.page.locator(".calib__drafting")
            if drafting.count():
                drafting.first.wait_for(state="detached", timeout=timeout_s * 1000 * self.patience)
            seen = {"screen": "check", "frame": self.frame(), **self._list_rows(), "test": self._keel_test()}
            h.capture_text("stage_screen", _text(self.page))
            h.add_screenshot(self._b.screenshot(f"check-{name}"))
        if add is not None:
            seen["importance"] = self.importance_rows(add, one_more=one_more)
            seen["after"] = self._list_rows()
            seen["test_after"] = self._keel_test()
        with self._b.step(f"founder saves {name}") as h:
            seen["primary"] = self._press_primary()
            h.add_screenshot(self._b.screenshot(f"check-{name}-saved"))
            return seen

    def list_choose(self, question: dict, label: str) -> dict:
        """*Choose* (FR-006): none pre-picked; the radio named `label` picked; the *Keel will test* box
        read with the pick; the primary (*Continue*, or the stage's exit). Returns what it read."""
        name = question.get("dimension")
        with self._b.step(f"founder picks the one item strangers are asked about: {label!r} ({name})") as h:
            _wait_url(self.page, r"/choose")
            group = self.page.locator(".listcheck [role=radiogroup]").first
            group.wait_for(state="visible", timeout=20_000)
            radios = group.get_by_role("radio")
            before = [radios.nth(i).get_attribute("aria-checked") for i in range(radios.count())]
            options = [_safe_text(lambda r=radios.nth(i): r.inner_text()).strip() for i in range(radios.count())]
            empty = self._keel_test()
            group.get_by_role("radio", name=label, exact=True).click()
            seen = {"screen": "choose", "frame": self.frame(), "options": options,
                    "picked_before": [i for i, c in enumerate(before) if c == "true"],
                    "test_before": empty, "test": self._keel_test(),
                    "prompt": _first_text(self.page, ".listcheck__title")}
            h.capture_text("stage_screen", _text(self.page))
            h.add_screenshot(self._b.screenshot(f"choose-{name}"))
            seen["primary"] = self._press_primary()
            return seen

    # --------------------------------------------------------------------------------- persona

    def persona(self, decider: dict) -> dict:
        with self._b.step(f"founder says who decides to pay: {decider.get('kind')}") as h:
            _wait_url(self.page, r"/define/persona")
            group = self.page.get_by_role("radiogroup", name=PERSONA_QUESTION, exact=True)
            group.wait_for(state="visible", timeout=20_000)
            if decider["kind"] == "SAME_PERSON":
                group.get_by_role("radio", name=PERSONA_SAME, exact=True).click()
            else:
                group.get_by_role("radio", name=PERSONA_SOMEONE_ELSE, exact=True).click()
                self.page.get_by_label(PERSONA_ROLE, exact=True).fill(decider["role"])
            _button(self.page, CONTINUE).click()
            self.page.get_by_text(KICKER_CONTEXT).first.wait_for(state="visible", timeout=20_000)
            text = _text(self.page)
            h.add_screenshot(self._b.screenshot("persona-set"))
            _button(self.page, CONTINUE).click()
            _wait_url(self.page, r"/define/commercial/q/1")
            return {"text": text}

    # ------------------------------------------------------------------- step 5: before people

    def word_pilot_and_lock(self, face: str | None = None) -> dict:
        """Step 5 (keel-web 063 FR-007; keel-web 069 FR-002 since spec 044): *A word from you* (1 of 3), *The pilot*
        (2 of 3), then L1 *Who asks the questions* (3 of 3) -- the carousel of five faces on Keel's door (`face`
        tapped when given), one line on an account on its own AI -- and *Lock and record the interviewer* / *Lock and
        approve*. Returns the counters, what L1 drew and the lock's receipt as keel-web received it (`LockReceipt`)."""
        with self._b.step("founder passes the word and the pilot, picks who asks, then locks") as h:
            _wait_url(self.page, r"/define/ready")
            counter = self.page.get_by_test_id("before-counter")
            counter.wait_for(state="visible", timeout=20_000)
            # The DOM's words, not the CSS's capitals (`text-transform`).
            first = counter.text_content() or ""
            _button(self.page, BEFORE_CONTINUE).click()
            _wait_url(self.page, r"/define/ready/pilot")
            self.page.locator("[data-testid=before-counter]", has_text=re.compile(r"^2 of")).wait_for(timeout=10_000)
            second = counter.text_content() or ""
            h.add_screenshot(self._b.screenshot("pilot"))
            counters = [first.strip(), second.strip()]
            l1: dict = {}
            if self.page.get_by_test_id("lock-and-record").count() == 0:          # keel-web 069: a third screen
                _button(self.page, BEFORE_CONTINUE).click()
                _wait_url(self.page, r"/define/ready/interviewer")
                self.page.locator("[data-testid=before-counter]", has_text="3 of 3").wait_for(timeout=10_000)
                counters.append((counter.text_content() or "").strip())
                l1 = self.l1(face)
            with self.page.expect_response(lambda r: r.request.method == "POST" and r.url.endswith("/lock"),
                                           timeout=30_000) as locked:
                self.page.get_by_test_id("lock-and-record").click()
            try:
                receipt = locked.value.json()
            except Exception:  # noqa: BLE001 - a refused lock's body is the leg's to report
                receipt = {"status": locked.value.status, "text": _safe_text(lambda: locked.value.text())}
            l1["sent"] = locked.value.request.post_data_json
            _wait_url(self.page, r"/interviews/sent|/people", timeout_s=60)       # keel-web 068: Sent
            h.add_screenshot(self._b.screenshot("locked-people"))
            return {"counters": counters, "receipt": receipt, "l1": l1}

    def l1(self, face: str | None = None) -> dict:
        """L1 as drawn (keel-web 069 FR-002): the title, the lead or the own-AI line, the carousel's faces and which is
        checked, the button's words and the main column's whole text (for the no-price rule). `face` is tapped."""
        main = self.page.locator(".corridor.before").first
        main.wait_for(state="visible", timeout=20_000)
        carousel = self.page.get_by_test_id("face-carousel")
        faces = []
        if carousel.count():
            if face:
                carousel.locator(f'[data-face="{face}"]').click()
                carousel.locator(f'[data-face="{face}"][aria-checked="true"]').wait_for(timeout=5_000)
            faces = [{"face": b.get_attribute("data-face"), "checked": b.get_attribute("aria-checked") == "true",
                      "text": " ".join((b.text_content() or "").split())}
                     for b in carousel.locator('button[role="radio"]').all()]
        button = self.page.get_by_test_id("lock-and-record")
        return {"title": _safe_text(lambda: main.locator("h1").first.inner_text()),
                "sub": _safe_text(lambda: main.locator(".ccard__sub").first.inner_text()),
                "faces": faces, "carousel": carousel.count() > 0,
                "button": _safe_text(lambda: button.inner_text()) if button.count() else None,
                "text": " ".join((main.text_content() or "").split())}


# ------------------------------------------------------------------------------------ PeopleLinks

class PeopleLinks:
    """The People page after lock: one link per person, through keel-web's own two popups."""

    def __init__(self, page: Page, recorder: Recorder, base_url: str, *, patience: float = 1.0):
        self.page = page
        self.base = base_url.rstrip("/")
        self.patience = patience
        self._b = _BrowserStep(recorder, page, "founder")

    def open(self, project_id: str) -> None:
        """The People page's *Kinds of people* side, where the role cards are. Once anyone has been
        asked the page opens on *Who's been asked*, so the toggle is pressed when the cards are not
        there."""
        if not self.page.url.endswith(f"/p/{project_id}/people"):
            self.page.goto(f"{self.base}/p/{project_id}/people", wait_until="load")
        self.page.locator(".role, table.ppl").first.wait_for(state="visible",
                                                            timeout=60_000 * self.patience)
        if self.page.locator(".role").count() == 0:
            self.page.locator(".toggle button", has_text=re.compile("kinds", re.I)).click()
        self.page.locator(".role").first.wait_for(state="visible", timeout=20_000)

    def role_labels(self) -> list[str]:
        return _safe_all_texts(self.page, ".role .role__label")

    def specialist_link(self, project_id: str, role_label: str, person: str, about: str) -> str:
        with self._b.step(f"founder sends the questions to {person}") as h:
            self.open(project_id)
            card = self.page.locator(".role", has=self.page.locator(".role__label", has_text=role_label)).first
            card.get_by_role("button", name=SEND_THE_QUESTIONS, exact=True).click()
            dialog = self.page.get_by_role("dialog")
            dialog.get_by_label(SEND_NAME, exact=True).fill(person)
            about_box = dialog.locator("#send-about")
            if about_box.count():
                about_box.fill(about)
            dialog.get_by_role("button", name=SEND_NEXT).click()
            first = person.split()[0]
            dialog.get_by_role("button", name=f"Generate {first}'s link").click()
            box = dialog.locator(".linkbox").first
            box.wait_for(state="visible", timeout=20_000)
            url = _link_of(box)
            h.add_screenshot(self._b.screenshot(f"link-{first}"))
            dialog.get_by_role("button", name="Done", exact=True).click()
            dialog.wait_for(state="hidden", timeout=10_000)
            return url

    def commercial_link(self, project_id: str, role_label: str, person: str) -> str:
        with self._b.step(f"founder makes the decision-maker's link for {person}") as h:
            # runs/DRIFT.md #75: the commercial popup posts the revision of the page's last
            # `GET /overview` poll (every 4 s while an invitation is out), so a link made within a
            # poll of the previous one is refused CONCURRENCY. The page is reloaded first, the way a
            # founder who comes back to it has it.
            self.open(project_id)
            self.page.reload(wait_until="load")
            self.open(project_id)
            card = self.page.locator(".role", has=self.page.locator(".role__label", has_text=role_label)).first
            card.get_by_role("button", name=SEND_THE_QUESTIONS, exact=True).click()
            dialog = self.page.get_by_role("dialog")
            dialog.get_by_label(SEND_NAME, exact=True).fill(person)
            dialog.get_by_role("button", name=MAKE_THEIR_LINK, exact=True).click()
            box = dialog.locator(".linkbox").first
            box.wait_for(state="visible", timeout=20_000)
            url = _link_of(box)
            h.add_screenshot(self._b.screenshot(f"commercial-link-{person.split()[0]}"))
            dialog.get_by_role("button", name="Close", exact=True).click()
            dialog.wait_for(state="hidden", timeout=10_000)
            return url


def _link_of(box) -> str:
    text = _safe_text(lambda: box.inner_text())
    match = re.search(r"https?://\S+", text)
    if match:
        return match.group(0)
    for attr in ("value", "href"):
        found = box.locator(f"[{attr}]").first
        if found.count():
            return found.get_attribute(attr) or ""
    return text.strip()


# --------------------------------------------------------------------------------------- Interview

class Interview:
    """The stranger's `/i/{token}` (keel-web 064): one screen at a time, every word as served. `walk`
    takes the interview as the wire served it (to read the labels of the option ids a pick names) and
    the person's answers; it records what each screen drew (`screens`) for the scenario to judge."""

    def __init__(self, page: Page, recorder: Recorder):
        self.page = page
        self._b = _BrowserStep(recorder, page, "participant")
        self.seen: list[str] = []
        self.screens: list[dict] = []

    def _keep(self) -> None:
        text = _screen_text(self.page, "div.iv-page") or _screen_text(self.page, "body")
        if text and (not self.seen or self.seen[-1] != text):
            self.seen.append(text)

    def _main(self):
        return self.page.locator("main").first

    def open(self, url: str) -> None:
        with self._b.step("the stranger opens their link") as h:
            self.page.goto(url, wait_until="load")
            _button(self.page, IV_BEGIN).wait_for(state="visible", timeout=20_000)
            self._keep()
            h.add_screenshot(self._b.screenshot("interview-intro"))

    def walk(self, person, interview: dict, wire_answers: dict, *, follow_up: str | None = None,
             speak: str | None = None) -> dict:
        """Begin, the decision-maker's idea screen, the gate, every item and the reveal, *Send my
        answers*; returns the body the page POSTed, the done screen's heading and what every screen drew.
        `wire_answers` is `{itemId: ItemAnswer}` -- what this person answers, already re-expressed as the
        wire takes it.

        Spec 051 (keel-web 076, keel-cloud 103): *Send my answers* first posts the answers to `POST .../interview/
        follow-up` (never after a gate No); a 200 opens the one follow-up (*One last thing*), where `follow_up` is
        typed and *Continue* pressed -- `None` presses *Skip this one* -- and then the response goes; a 204 sends it at
        once. `speak` drives the story's box (`SpeakOrTypeBox`, through `text_seam`): "quiet" or "done" -- the story
        typed, then *Speak*, a sound, and the take ended by the 4 s quiet or by *Done* (T1 -> T4); "refused" -- *Speak*
        on a refused microphone (T6), then typed. What the route answered, the screen drew and the box did is kept."""
        page = self.page
        self.route: dict = {}
        self.follow_up_seen: dict | None = None
        self.speak_seen: dict | None = None
        self._transcribe_responses: list = []
        page.on("response", self._keep_transcribe)
        with self._b.step(f"{person.person} answers the interview, screen by screen") as h:
            self.consent = {"heading": _first_text(page, "section.iv-consent h2"),
                            "text": _first_text(page, "section.iv-consent p")}
            # Spec 044 call 150: wait for the answer's own response, not the request leaving the browser -- the last
            # decision-maker's done screen is not a heading of its own, so the walk returned while the POST was in
            # flight and the standings read the project before it landed (S-006, n 7 of 8, once).
            with page.expect_response(lambda r: r.request.method == "POST"
                                      and r.url.endswith("/interview/response"),
                                      timeout=120_000) as answered:
                _button(page, IV_BEGIN).click()
                if interview.get("kind") == "COMMERCIAL_LINK" and interview.get("idea"):
                    self._idea()
                gate = interview.get("gate")
                if gate:
                    self._gate(person, gate, interview.get("occasion"), speak=speak)
                if gate is None or person.recency:
                    self._items(interview, wire_answers)
                    self._follow_up(follow_up)
            body = answered.value.request.post_data_json
            status = answered.value.status
            page.get_by_role("heading", level=1).first.wait_for(state="visible", timeout=20_000)
            self._keep()
            heading = _safe_text(lambda: page.get_by_role("heading", level=1).first.inner_text())
            h.add_screenshot(self._b.screenshot(f"interview-done-{person.person.split()[0]}"))
            page.remove_listener("response", self._keep_transcribe)
            return {"body": body, "status": status, "done": heading, "seen": list(self.seen),
                    "screens": list(self.screens), "follow_up_route": self.route, "follow_up": self.follow_up_seen,
                    "speak": self.speak_seen, "transcribed": self._transcribed(), "consent": self.consent}

    def _keep_transcribe(self, response) -> None:
        """Every `transcribe` the page sent (the box's recorded take): kept as the response, read after the walk (a
        body read inside an event handler would wait on the handler itself)."""
        if response.request.method == "POST" and response.url.split("?")[0].endswith("/interview/transcribe"):
            self._transcribe_responses.append(response)

    def _transcribed(self) -> list[dict]:
        out = []
        for response in self._transcribe_responses:
            body = response.request.post_data_json or {}
            got = _json_body(response)
            out.append({"itemId": body.get("itemId"), "maxSeconds": body.get("maxSeconds"),
                        "mimeType": body.get("mimeType"), "language": body.get("language"),
                        "status": response.status, "text": got.get("text")})
        return out

    def _follow_up(self, line: str | None) -> None:
        """Spec 051 FR-4 (keel-web 076 FR-3): the route's answer to the last item's *Send my answers* -- 200 opens *One
        last thing* (the kicker, the cloud's question as `h1.iv-q`, the note, the box, *Continue* off while empty, *Skip
        this one*), where `line` is typed and *Continue* pressed, or (no line) *Skip this one*; 204 sends at once."""
        page = self.page
        route = self.route
        if route.get("status") != 200:
            return
        screen = page.get_by_test_id("iv-follow-up")
        screen.wait_for(state="visible", timeout=20_000)
        self._keep()
        box = ivs.SpeakBox(page, "[data-testid=iv-follow-up]")
        cont = _button(page, IV_CONTINUE)
        drawn = {"kicker": _first_text(screen, ".iv-kicker"), "question": _first_text(screen, "h1.iv-q"),
                 "note": _first_text(screen, ".iv-note"), "box": box.read(),
                 "continue_enabled_empty": cont.is_enabled(),
                 "skip": _tc(screen.get_by_test_id("iv-follow-up-skip")),
                 "textarea_label": screen.locator("textarea").first.get_attribute("aria-label")}
        self.screens.append({"screen": "follow_up", **{k: drawn[k] for k in ("kicker", "question", "note")}})
        if line:
            screen.locator("textarea").first.fill(line)
            drawn["continue_enabled_typed"] = cont.is_enabled()
            drawn["did"] = "typed"
            drawn["typed"] = line
            cont.click()
        else:
            drawn["did"] = "skipped"
            screen.get_by_test_id("iv-follow-up-skip").click()
        self.follow_up_seen = drawn

    def opt_in_to_pilot(self, interview: dict) -> None:
        label = ((interview.get("done") or {}).get("pilot") or {}).get("label")
        if not label:
            return
        # Wait for the pilot's 204, not just the request leaving the browser (spec 043 call 147): the tick is a
        # project write, and on staging the founder's next move (the #84 reading) raced it -- the reading captured
        # the revision before the tick and failed STATE_CONFLICT. Locally the tick always landed first.
        with self.page.expect_response(lambda r: r.request.method == "POST" and r.url.endswith("/interview/pilot"),
                                       timeout=20_000) as ticked:
            self.page.get_by_role("checkbox", name=label, exact=True).click()
        assert ticked.value.status == 204, f"the pilot tick answered {ticked.value.status}"

    def _idea(self) -> None:
        """D9 (keel-web 064 FR-007): the decision-maker's link opens with the idea's three lines."""
        page = self.page
        _button(page, IV_CONTINUE).wait_for(state="visible", timeout=20_000)
        self._keep()
        self.screens.append({"screen": "idea", "kicker": _first_text(page, ".iv-kicker"),
                             "card": _first_text(page, ".iv-card"),
                             "question": _first_text(page, "h1.iv-q")})
        _button(page, IV_CONTINUE).click()

    def _gate(self, person, gate: dict, occasion: str | None, *, speak: str | None = None) -> None:
        page = self.page
        group = page.get_by_role("radiogroup", name=gate["question"], exact=True)
        group.wait_for(state="visible", timeout=20_000)
        self._keep()
        group.get_by_role("radio", name=IV_YES if person.recency else IV_NO, exact=True).click()
        chips = []
        if person.recency:
            chips = _safe_all_texts(page, ".iv-story .iv-chips button")
            if person.anchor_chip:
                _button(page, gate_chip_word(occasion)).click()
            elif person.story and speak:
                self._speak_story(person.story, speak)
            elif person.story:
                page.locator("textarea").first.fill(person.story)
        self.screens.append({"screen": "gate", "kicker": _first_text(page, ".iv-kicker"),
                             "question": _first_text(page, "h1.iv-q"), "chips": chips})
        _button(page, IV_CONTINUE).click()

    def _speak_story(self, story: str, how: str) -> None:
        """Spec 051 FR-5 (keel-web 076 FR-6..FR-8, design §6): the story's box, T1 -> T4 through the seam's recorder --
        idle (nothing asked of the microphone yet), the story typed, *Speak* tapped (the microphone asked for now), the
        listening card (the waveform, the clock, Cancel, Done; Continue off), a sound, then the take ended by the 4 s
        quiet (`how` "quiet") or by *Done* ("done"); *Writing it down…* (the recorder's stop held so it can be read), and
        the transcript appended with the caret at the end, *Heard you.*, the pill *Add more*. "refused": *Speak* on a
        refused microphone -- typing only (T6) -- then the story typed."""
        page = self.page
        box = ivs.SpeakBox(page, "main")
        out: dict = {"how": how}
        cont = _button(page, IV_CONTINUE)
        box.wait_state("idle")
        out["t1"] = box.read()
        out["before_pill"] = box.counts()
        if how == "refused":
            box.tap()
            out["t6"] = box.wait_state("typing-only")
            out["t6_pill"] = page.locator("main .sot [data-testid=iv-mic]").count()
            out["after_pill"] = box.counts()
            page.locator("main .sot textarea").first.fill(story)
            out["value"] = box.read()["value"]
            self.speak_seen = out
            return
        page.locator("main .sot textarea").first.fill(story)
        out["typed"] = story
        box.tap()
        out["t2"] = box.wait_state("listening")
        page.locator("main [data-testid=iv-listening] [data-testid=ai-mic-on]").first.wait_for(
            state="attached", timeout=10_000)
        out["t2"] = box.read()
        # read three times across 600 ms: the screen's Continue goes off through the box's state (`onBoxState`)
        out["continue_while_listening"] = []
        for _ in range(3):
            out["continue_while_listening"].append({"enabled": cont.is_enabled(),
                                                    "disabled": cont.get_attribute("disabled"), "at": box.now()})
            page.wait_for_timeout(200)
        out["continue_enabled_listening"] = out["continue_while_listening"][-1]["enabled"]
        out["after_pill"] = box.counts()
        box.hold_stop()
        out["sound_at"] = box.speak()
        out["clock_speaking"] = box.read()["clock"]
        if how == "done":
            out["done_at"] = box.now()
            box.done()
        else:
            out["quiet_at"] = box.quiet()
        out["t3"] = box.wait_state("writing", timeout_s=15)
        out["writing_at"] = box.now()
        box.release_stop()
        out["t4"] = box.wait_state("heard", timeout_s=20)
        page.wait_for_timeout(150)                      # the caret is put after the words on the next render
        out["t4"] = box.read()
        out["counts"] = box.counts()
        self.speak_seen = out
    def _items(self, interview: dict, wire_answers: dict) -> None:
        page = self.page
        parts = interview.get("parts") or []
        reveal = interview.get("reveal") or {}
        for p_index, part in enumerate(parts):
            items = part.get("items") or []
            for i_index, item in enumerate(items):
                page.locator("h1.iv-q").first.wait_for(state="visible", timeout=20_000)
                self._keep()
                answer = wire_answers.get(item.get("itemId"))
                if answer is not None:
                    self._answer(item, answer)
                self.screens.append(self._item_screen(item))
                last = p_index == len(parts) - 1 and i_index == len(items) - 1
                if last:
                    # keel-web 076 FR-1: the last *Send my answers* posts the answers to the follow-up route first
                    with page.expect_response(lambda r: r.request.method == "POST"
                                              and r.url.split("?")[0].endswith("/interview/follow-up"),
                                              timeout=30_000) as asked:
                        _button(page, IV_SEND).click()
                    self.route = {"status": asked.value.status, "body": _json_body(asked.value)
                                  if asked.value.status == 200 else {},
                                  "sent": asked.value.request.post_data_json}
                else:
                    _button(page, IV_NEXT).click()
            if interview.get("kind") == "FULL" and reveal and reveal.get("afterPart") == part.get("part") \
                    and p_index < len(parts) - 1:
                _button(page, IV_CONTINUE).wait_for(state="visible", timeout=20_000)
                self._keep()
                self.screens.append({"screen": "reveal", "kicker": _first_text(page, ".iv-kicker"),
                                     "card": _first_text(page, ".iv-card")})
                _button(page, IV_CONTINUE).click()

    def _item_screen(self, item: dict) -> dict:
        """What one item's screen drew, in the order drawn: the kicker, the idea card, the stem, the hint,
        the control's rows, the escape chips (and whether the escape is the last control before the
        buttons)."""
        page = self.page
        main = self._main()
        rows = _safe_all_texts(page, ".iv-control [role=radio], .iv-control [role=checkbox]")
        chips = _safe_all_texts(page, ".iv-chips button")
        order = main.evaluate(
            "(m) => Array.from(m.children).map((c) => c.className || c.tagName)") if main.count() else []
        return {"screen": "item", "dimension": item.get("dimension"), "control": item.get("control"),
                "kicker": _first_text(page, ".iv-kicker"), "question": _first_text(page, "h1.iv-q"),
                "idea_card": _first_text(page, ".iv-ideacard__what"),
                "hint": _first_text(page, ".iv-tick"), "picked_line": _first_text(page, ".iv-picked"),
                "rows": [r.strip() for r in rows], "chips": [c.strip() for c in chips], "order": order}

    def _answer(self, item: dict, answer: dict) -> None:
        main = self._main()
        options = {o.get("optionId"): o.get("label") for o in item.get("options") or []}
        advantages = {a.get("id"): a.get("label") for a in item.get("advantages") or []}
        if answer.get("chip"):
            escape = item.get("escape") or {}
            main.locator(".iv-chips").get_by_role("button", name=escape.get("label"), exact=True).click()
            return
        if "scale" in answer:
            main.get_by_role("radio", name=str(answer["scale"]), exact=True).click()
            return
        if "costTotal" in answer:
            cost = answer["costTotal"]
            modes = main.get_by_role("radiogroup", name=IV_COST_MODE_GROUP, exact=True)
            if modes.count():
                radio = modes.get_by_role("radio", name=IV_COST_MODE_WORD[cost["mode"]], exact=True)
                if radio.get_attribute("aria-checked") != "true":
                    radio.click()
            main.locator(".iv-num input").first.fill(_number(cost["value"]))
            return
        role = "checkbox" if item.get("control") == "pick_two" else "radio"
        for option_id in answer.get("optionIds") or []:
            main.locator(".iv-control").get_by_role(role, name=options[option_id], exact=True).first.click()
        for advantage_id in answer.get("advantageIds") or []:
            main.get_by_role("checkbox", name=advantages[advantage_id], exact=True).click()


# ----------------------------------------------------------------------------------------- Answers

class Answers:
    """The read-only answer pages of a locked study. Reads only."""

    def __init__(self, page: Page, recorder: Recorder, base_url: str):
        self.page = page
        self.base = base_url.rstrip("/")
        self._b = _BrowserStep(recorder, page, "founder")

    # ------------------------------------------------------------------ the report (keel-web 077, spec 052)
    #
    # One page, `/p/{id}`, three views -- Overview, Insights, Pilot -- switched by the segmented control
    # (`report-views`, `button[data-view]`, the view in the hash), and *Download the brief* (`report-download`) opening
    # `/p/{id}/print`, the binding. Selectors are keel-web 077's spec's (its *Selectors (for keel-e2e-eval 052)*
    # section); everything is read as the DOM carries it (`text_content`), never as the CSS capitalises it, and the
    # marks compare words in order (`instructions/overview.in_order`), so the markup between them may move.

    def _report(self, project_id: str, view: str) -> None:
        """The report on `view`: `/p/{id}` loaded afresh, then the tab pressed as a founder would (`report-views`,
        `button[role=tab][data-view]`; keel-web 077 pushes a history entry), and the tab panel `#report-view` drawn
        with that tab selected."""
        # a fresh load every read: the report's standings are read once a mount, so a page left open would draw an
        # earlier wire (the after-four read on S-005 drew 0 answered from the page the zero read left)
        self.page.goto(f"{self.base}/p/{project_id}", wait_until="load")
        views = self.page.get_by_test_id("report-views").first
        views.wait_for(state="visible", timeout=30_000)
        tab = views.locator(f"button[role='tab'][data-view='{view}']").first
        if tab.get_attribute("aria-selected") != "true":
            tab.click()
        self.page.locator(f"button[role='tab'][data-view='{view}'][aria-selected='true']").first.wait_for(
            state="visible", timeout=10_000)
        self.page.locator("#report-view[role='tabpanel']").first.wait_for(state="visible", timeout=10_000)

    def board(self, project_id: str) -> dict:
        """The Overview view (keel-web 077 FR-2, as built): the eyebrow (`.rp-eyebrow`), the hero (`report-hero`:
        `h1.rp-verdict[data-label]` and its class, `.rp-why` with `a.rp-why__more` on KEEP_INTERVIEWING, the ship's
        bands, `.rp-shipcap`), the two tiles (`report-tiles [data-tile]`), the three panels (`report-stage-{STAGE}`:
        `.rp-pname`, `.rp-pill`, `.rp-plead`, one `a.rp-row[data-dim]` a card), the foot (`.rp-foot`), the download,
        and what the old deck drew (each a count that must be 0)."""
        with self._b.step("founder opens the report's overview") as h:
            self._report(project_id, "overview")
            hero = self.page.get_by_test_id("report-hero").first
            hero.wait_for(state="visible", timeout=30_000)
            verdict = hero.locator("h1.rp-verdict")
            send = hero.locator("a.rp-why__more")
            tiles = {}
            for name in ("pilot", "price"):
                tile = self.page.get_by_test_id("report-tiles").locator(f"[data-tile='{name}']")
                tiles[name] = {"present": tile.count() > 0, "text": _tc(tile),
                               "big": _tc(tile.locator(".rp-tile__big")),
                               "none": tile.locator(".rp-tile__big--none").count() > 0}
            panels = {}
            for stage in ("PROBLEM", "SOLUTION", "COMMERCIAL"):
                panel = self.page.get_by_test_id(f"report-stage-{stage}")
                rows = [{"key": r.get_attribute("data-dim"), "status": r.get_attribute("data-status"),
                         "href": r.get_attribute("href"), "text": _tc(r)}
                        for r in panel.locator("a.rp-row").all()]
                head = " ".join(x for x in (_tc(panel.locator(".rp-pname")), _tc(panel.locator(".rp-pill"))) if x)
                panels[stage] = {"present": panel.count() > 0, "head": head, "lead": _tc(panel.locator(".rp-plead")),
                                 "rows": rows, "text": _tc(panel)}
            bands, seen = [], set()
            for band in hero.locator("[data-stage]").all():
                stage = band.get_attribute("data-stage")
                if stage and stage not in seen and "band" in (band.get_attribute("class") or ""):
                    seen.add(stage)
                    bands.append({"stage": stage, "class": band.get_attribute("class") or ""})
            download = self.page.get_by_test_id("report-download")
            text = _text(self.page)
            h.capture_text("stage_screen", text)
            h.add_screenshot(self._b.screenshot("report-overview"))
            return {
                "views": [_tc(b) for b in self.page.get_by_test_id("report-views").locator("button[role='tab']").all()],
                "eyebrow": _tc(self.page.locator(".rp-eyebrow")),
                "hero": {"label": verdict.first.get_attribute("data-label") if verdict.count() else None,
                         "class": verdict.first.get_attribute("class") if verdict.count() else "",
                         "verdict": _tc(verdict), "text": _tc(hero.locator(".rp-hero__text")) or _tc(hero),
                         "send_more": {"text": _tc(send), "href": send.first.get_attribute("href")}
                         if send.count() else None,
                         "caption": _tc(hero.locator(".rp-shipcap"))},
                "bands": bands, "tiles": tiles, "panels": panels,
                "foot": _tc(self.page.locator(".rp-foot")),
                "download": {"present": download.count() > 0,
                             "enabled": download.count() > 0 and download.first.get_attribute("aria-disabled")
                             != "true" and download.first.get_attribute("disabled") is None,
                             "href": download.first.get_attribute("href") if download.count() else None,
                             "target": download.first.get_attribute("target") if download.count() else None},
                # design §4.1 *Gone from today's deck* -- each must be 0
                "old_deck": {"p.overall": self.page.locator("p.overall").count(),
                             ".tile--people": self.page.locator(".tile--people").count(),
                             ".snaprow": self.page.locator(".snaprow").count(),
                             ".panel__count": self.page.locator(".panel__count").count()},
                "text": text,
            }

    def insights(self, project_id: str) -> dict:
        """The Insights view (keel-web 077 FR-3, as built, `report-insights`): per box (`section.rp-ibox[data-dim]`)
        its head (`.rp-ihead`: the name and the pill), its whole text, `.rp-concern`, `.rp-tookby`, `.rp-nofollow`, the
        split line, the themes (`ol.rp-themes > li`: the label, `.rp-themes__n`, the `p.rp-quote`s), the raw quotes
        (`.rp-raw`); the empty state (`.rp-inone`); every quote and the view's own *said why* / *Only k of the n* lines
        (what `report_no_repeat` takes out)."""
        from harness import interviewer_fake as fake                    # noqa: PLC0415
        with self._b.step("founder opens the report's insights") as h:
            self._report(project_id, "insights")
            view = self.page.get_by_test_id("report-insights").first
            view.wait_for(state="visible", timeout=30_000)
            boxes, own_lines = [], []
            for box in view.locator("section.rp-ibox").all():
                text = _words(box)
                themes = []
                for li in box.locator("ol.rp-themes > li").all():
                    quotes = [_tc(q) for q in li.locator(".rp-quote").all()]
                    n = _tc(li.locator(".rp-themes__n"))
                    rest = _tc(li)
                    for cut in quotes + [n]:
                        rest = rest.replace(cut, " ") if cut else rest
                    count = n.strip("()")
                    themes.append({"label": " ".join(rest.split()), "count": int(count) if count.isdigit() else None,
                                   "quotes": quotes})
                concern = _tc(box.locator(".rp-concern"))
                took = _tc(box.locator(".rp-tookby"))
                own_lines += [x for x in (concern, took) if x]
                boxes.append({
                    "key": box.get_attribute("data-dim"), "status": box.get_attribute("data-status"),
                    "head": _tc(box.locator(".rp-ihead")), "concern": concern, "themes": themes, "text": text,
                    "split": fake.SPLIT_NOTE if fake.SPLIT_NOTE in text else None,
                    "took_by": took or None, "no_follow_up": _tc(box.locator(".rp-nofollow")) or None,
                    "raw": [_tc(q) for q in box.locator(".rp-raw .rp-quote").all()]})
            text = _words(view)
            h.capture_text("stage_screen", text)
            h.add_screenshot(self._b.screenshot("report-insights"))
            return {"boxes": boxes, "empty": _tc(view.locator(".rp-inone")) or None,
                    "quotes": [_tc(q) for q in view.locator(".rp-quote").all()], "own_lines": own_lines,
                    "text": text}

    def pilot(self, project_id: str) -> dict:
        """The Pilot view (keel-web 077 FR-4, as built, `report-pilot`): the pilot tile and *What they agreed to*
        (`[data-tile=pilot|agreed]`), one `details.rp-person[data-invitation][data-link]` a person -- its summary
        (`.rp-nm`, `.rp-src`, `.rp-mail__addr`) and, each row opened as the founder would, its body (`.rp-pbody`: the
        gate or the decision-makers' line, the story, `dl.rp-ans`, `.rp-pfollow`) -- and the foot (`.rp-pnote`)."""
        with self._b.step("founder opens the report's pilot list") as h:
            self._report(project_id, "pilot")
            view = self.page.get_by_test_id("report-pilot").first
            view.wait_for(state="visible", timeout=30_000)
            people = []
            for row in view.locator("details.rp-person").all():
                try:
                    if row.get_attribute("open") is None:
                        row.locator("summary .rp-nm").first.click()
                except Exception:  # noqa: BLE001 - a read; the words are in the DOM either way
                    pass
                summary = row.locator("summary")
                people.append({"invitation": row.get_attribute("data-invitation"), "link": row.get_attribute("data-link"),
                               "summary": " ".join(x for x in (_tc(summary.locator(".rp-nm")),
                                                               _tc(summary.locator(".rp-src"))) if x),
                               "email": _tc(row.locator(".rp-mail__addr")) or None,
                               "inside": _words(row.locator(".rp-pbody"))})
            note = _tc(view.locator(".rp-pnote"))
            text = _words(view)
            tiles = {"pilot": {"text": _words(view.locator("[data-tile='pilot']"))},
                     "agreed": {"text": _words(view.locator("[data-tile='agreed']"))}}
            h.capture_text("stage_screen", text)
            h.add_screenshot(self._b.screenshot("report-pilot"))
            return {"tiles": tiles, "people": people,
                    "none": note if note == "Nobody has signed up yet." else None, "foot": note, "text": text}

    def vector_page(self, project_id: str, vector: str, *, open_row: str | None = None,
                    follow_up_rows=()) -> dict:
        """One stage page: every row's name, belief, status and amber; and, `open_row` named, that row
        opened and its per-person list read (keel-web `DimensionStagePage`'s `ul.dimpeople`: each person's
        name and how the answer was read). Spec 052 FR-8: each of `follow_up_rows` (the rungs whose people answered
        the follow-up) opened too, and every person's *One last thing · {rung}: "…"* line read off its list
        (`follow_ups`: `{dimension: [{name, line}]}`)."""
        with self._b.step(f"founder opens the {vector.lower()} page") as h:
            self.page.goto(f"{self.base}/p/{project_id}/s/{vector}", wait_until="load")
            self.page.locator(".dimrow").first.wait_for(state="visible", timeout=30_000)
            rows = {}
            for row in self.page.locator(".dimrow").all():
                rows[row.get_attribute("id")] = {
                    "name": _first_text(row, ".dimrow__name"),
                    "belief": _first_text(row, ".dimrow__belief"),
                    "status": _first_text(row, "span.status"),
                    "amber": row.locator(".dimword--amber").count() > 0,
                }
            people = []
            if open_row:
                row = self.page.locator(f".dimrow[id='{open_row}']").first
                head = row.locator("button.dimrow__head")
                if head.count():
                    head.first.click()
                    row.locator(".dimrow__body").first.wait_for(state="visible", timeout=10_000)
                for li in row.locator("ul.dimpeople li").all():
                    spans = li.locator("span")
                    people.append({"name": _safe_text(lambda s=spans.nth(0): s.inner_text()).strip(),
                                   "readAs": _first_text(li, ".dimpeople__read").strip()})
            follow_ups = {}
            for key in follow_up_rows or ():
                row = self.page.locator(f".dimrow[id='{key}']").first
                head = row.locator("button.dimrow__head")
                body = row.locator(".dimrow__body")
                # one row open at a time: opening another closed this one, so open it again if it is shut
                if head.count() and not (body.count() and body.first.is_visible()):
                    head.first.click()
                    body.first.wait_for(state="visible", timeout=10_000)
                follow_ups[key] = [{"name": _safe_text(lambda li=li: li.locator("span").nth(0).inner_text()).strip(),
                                    "line": _tc(li.locator(".dimpeople__follow")) or None}
                                   for li in row.locator("ul.dimpeople li").all()]
            text = _text(self.page)
            h.capture_text("stage_screen", text)
            h.add_screenshot(self._b.screenshot(f"vector-{vector.lower()}"))
            return {"rows": rows, "text": text, "people": people, "open_row": open_row, "follow_ups": follow_ups,
                    "keel_bars": self.page.locator(".dimrow__said--keel").count(),
                    "headline": _first_text(self.page, "p.answers__headline"),
                    "decider_banner": _first_text(self.page, "p.decider-banner")}

    def brief(self, project_id: str, *, printed: bool = True) -> dict:
        """*Download the brief* -- the binding (keel-web 077 FR-5, `/p/{id}/print`, `report-binding`): the tab's title
        (the file name), whether *Preparing your brief…* was drawn first (a mutation observer installed before the
        page loads), and each `article.page[data-page]` -- its kicker, title, meta line and foot (the page frame), its
        whole text, and how many Overview rows it drew (page 1 draws the lead lines only). `window.print` is stubbed
        (050's), so nothing opens a dialog. `printed=False` is refused: the brief has no on-screen page any more
        (keel-web 077 FR-6 sends `/p/{id}/brief` to the Insights view)."""
        if not printed:
            raise ValueError("keel-web 077 deleted the brief's on-screen pages; read the report's views instead")
        with self._b.step("founder downloads the brief") as h:
            self.page.add_init_script("""window.print = () => {};
                window.__preparingSeen = false;
                new MutationObserver(() => {
                  if ((document.body && document.body.textContent || '').includes('Preparing your brief'))
                    window.__preparingSeen = true;
                }).observe(document, {subtree: true, childList: true, characterData: true});""")
            self.page.goto(f"{self.base}/p/{project_id}/print", wait_until="commit")
            binding = self.page.get_by_test_id("report-binding").first
            binding.locator("article.page.rp-page").first.wait_for(state="visible", timeout=60_000)
            pages = []
            for page in binding.locator("article.page.rp-page").all():
                number = page.get_attribute("data-page")
                pages.append({"page": int(number) if (number or "").isdigit() else number,
                              "kicker": _words(page.locator(".rp-kick")),
                              "title": _words(page.locator(".rp-pt")),
                              "meta": _words(page.locator(".rp-pmeta")),
                              "foot": _words(page.locator(".rp-pfoot")),
                              "block169": page.locator(".rp-block169").count(),
                              "rows": page.locator("a.rp-row").count(),
                              "text": _words(page)})
            text = _screen_text(self.page, "[data-testid='report-binding']")
            h.capture_text("download", text)
            h.add_screenshot(self._b.screenshot("brief-print"))
            return {"title": self.page.title(), "preparing_seen": bool(self.page.evaluate("window.__preparingSeen")),
                    "pages": pages, "old_headline": self.page.locator(".bhead__headline").count(), "text": text}
