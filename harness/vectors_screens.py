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

import json
import re
import time
from typing import Any, Callable

from playwright.sync_api import Page

from harness import interviewer_screens as ivs
from harness.browser import (INTERVIEW_DONE_TITLE, _SCREEN_TEXT_JS, _BrowserStep, _safe_all_texts, _safe_text,
                             _screen_text)
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
#: keel-web 113 FR-1 (its *Selectors for keel-e2e-eval*): the context step draws one state at a time, named on its root
#: -- the form, the wait (Save pressed: `WaitCompany`'s counter, phase bar and truth card in the form's place), the card
#: (*Keel understands*, *Edit* back to the form) and, re-opened once confirmed, the confirmed sentence.
CONTEXT_STEP = "[data-testid=context-step]"
CONTEXT_STATES = ("form", "wait", "card", "confirmed")
#: keel-web `CONTEXT_READING`, `CONTEXT_CONTINUE_LABEL` and `CARD_EDIT` (the card's and the confirmed state's *Edit*).
CONTEXT_READING = "Keel is reading your four answers."
CONTEXT_CONTINUE = "Continue to the problem"
CONTEXT_EDIT = "Edit"
#: keel-web 117 FR-1 (`SCOPE_CHANGE`, the plan card's word): the end of the card's *I'll ask about* line, which opens the
#: occasion's one field in the line's place (spec 074).
OCCASION_CHANGE = "Change"
#: keel-web 093 FR-2 (`REFUSED_LEAD`): a refused step's lead on Keel's door -- the back-test markdown's anchor.
REFUSED_LEAD = "Keel couldn't finish this step"
CONTINUE = "Continue"
SAVE = "Save"
#: `STAGE_EXIT_LABEL`: a stage's last screen names where it goes next (design §4: P6, S10, C11).
STAGE_EXIT = {"PROBLEM": "Save and continue to the solution",
              "SOLUTION": "Continue to paying",
              "COMMERCIAL": "Save and continue to Before people see it"}
#: Spec 071 (keel-web 109 FR-3, `corridor.ts` / `calibrationWalk.ts`): the stages each scope calibrates, in order.
SCOPE_STAGES = {"PROBLEM": ("PROBLEM",), "SOLUTION": ("SOLUTION",), "SOLUTION_COMMERCIAL": ("SOLUTION", "COMMERCIAL"),
                "COMMERCIAL": ("COMMERCIAL",), "ALL": ("PROBLEM", "SOLUTION", "COMMERCIAL")}
#: keel-web 109 `corridorStepsOf`: every scope's steps, by title (money alone's step 3 is *Your idea*).
SCOPE_STEPS = {"PROBLEM": ("context", "problem", "ready"), "SOLUTION": ("context", "problem", "solution", "ready"),
               "SOLUTION_COMMERCIAL": ("context", "problem", "solution", "commercial", "ready"),
               "COMMERCIAL": ("context", "problem", "solution", "commercial", "ready"),
               "ALL": ("context", "problem", "solution", "commercial", "ready")}


def calibrates(vector: str, scope: str = "ALL") -> bool:
    """keel-web 109 `calibrates`: whether the scope walks a vector's questions (the problem only in the problem study
    and the whole one)."""
    return vector in SCOPE_STAGES[scope]


def stage_exit(vector: str, scope: str = "ALL") -> str:
    """keel-web 109 `stageExitLabel`: the primary on a stage's last screen -- the scope's last stage goes to *Before
    people see it*; under ALL exactly `STAGE_EXIT`."""
    return STAGE_EXIT["COMMERCIAL"] if vector == SCOPE_STAGES[scope][-1] else STAGE_EXIT[vector]


def step_of(key: str, scope: str = "ALL") -> tuple[int, int]:
    """keel-web 109 `scopedStep`: a step's place and the scope's count (*Step 2 of 3*)."""
    steps = SCOPE_STEPS[scope]
    return steps.index(key) + 1, len(steps)
UNSURE_CHIP = "I'm not sure"
PRICE_NONE_CHIP = "No price yet"
LEAVE_OUT_CHIP = "Leave this out of the study"
LIST_DRAFTING = "Keel is writing this from your answer."
COST_MODE_GROUP = "Measured as"
#: keel-web 094 FR-1 (spec 064 FR-2): the chain's cost step -- the three ways, by their pills.
CHAIN_COST_HOW = "How would you put what it costs them?"
CHAIN_MODE_WORD = {"MONEY": "Money they spend", "HOURS": "Time it takes", "RATE": "A rate they lose"}
#: keel-web 094 FR-2: the chain's price step.
CHAIN_SHAPE_GROUP = "The shape of your price"
COST_MODE_WORD = {"AMOUNT": "Fixed amount", "HOURS": "Hours"}
PERSONA_QUESTION = "Who makes the buying decision?"
PERSONA_SAME = "The same person would decide to pay"
PERSONA_SOMEONE_ELSE = "Someone else would decide"
PERSONA_ROLE = "If someone else, what role would that person typically have?"
#: keel-web 099 FR-6 (`PERSONA_TITLE_LABEL`): the decider's job title, one to five words; Continue waits for it.
PERSONA_TITLE = "What is their job title?"
BEFORE_CONTINUE = "Continue"
BEFORE_LOCK = "Lock and write the questions"           # until keel-web 069
#: keel-web 069 `translate.ts`: L1, the last screen of step 5 (2 of 2 since keel-web 113 hid the word; alone in the
#: problem study).
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

#: keel-web 123 (spec 075 FR-2), `translate.ts`: the chain cost step's helper lines and the rate's default note.
CHAIN_UNIT_HELP = "What you count it against: a person, a site, a company."
CHAIN_HOURS_BASE_HELP = "What the time goes on."
CHAIN_BASE_HELP = "What they lose a share of."
HOURLY_RATE_DEFAULTED = "Keel's default for this market. Change it if yours differs."
#: keel-cloud 141 (`CommercialChain.KEEL_READS`, `countsSentence`): Keel's own reading of Ability to pay, and which of the
#: budget question's answers count, by kind of study. Since keel-cloud 145 FR-1 (spec 076 FR-1) the said line of a row
#: read off the budget question is the counts sentence alone (the row's subtitle carries Keel's reading).
KEEL_READS = "Keel reads "
COUNTS_SENTENCE = {True: "Counts for you: a budget line they already had, or other spending. Counts against: a new "
                         "budget line, or none.",
                   False: "Counts for you: money they already spend. Counts against: new money, or couldn't pay it."}
#: keel-cloud 145 FR-1 (`CommercialChain.BUDGET_SUPPORTS`): the budget question's answers that count for the founder --
#: the bars drawn on (green) on a row read off the budget question, every other bar muted.
BUDGET_SUPPORTS = ("from_spend", "existing_line", "taken_from_other_spend")
#: keel-cloud's sub-line for a named set's other bars -- never on a fixed set (145 FR-1: the budget bars).
DIDNT_NAME = "which you didn't name"
#: keel-web `priceCostBox`: the Price step's cost box around the served `costEstimate.said`.
PRICE_COST_BOX = "You estimate the problem costs them {said}."
IV_BEGIN = "Begin"
IV_CONTINUE = "Continue"
IV_NEXT = "Next"
IV_SEND = "Send my answers"
IV_YES = "Yes"
IV_NO = "No"
IV_COST_MODE_GROUP = "Measured as"
IV_COST_MODE_WORD = {"AMOUNT": "Amount", "HOURS": "Hours"}
IV_PICK_TWO = "Pick two."
#: keel-web 099 FR-6 (`GATE_RATHER_NOT_SAY`): the gate story's second chip, after the occasion's.
GATE_RATHER_NOT_SAY = "I'd rather not say"
#: keel-web 096: the segment chip's answers are the gate's own Yes / No.
IV_CHIP_WORD = {"YES": "Yes", "NO": "No"}
IV_TWO_PICKED = "2 of 2 picked. Untick one to change."


def gate_chip_word(occasion: str | None) -> str:
    """keel-web `gateChipWord`: the gate story's one chip (contract 13: CANT_RECALL alone)."""
    return f"I can't recall one particular {(occasion or '').strip() or 'time'}"


def _wait_url(page: Page, pattern: str, *, timeout_s: float = 30) -> None:
    page.wait_for_url(re.compile(pattern), timeout=timeout_s * 1000)


def _button(page, name, *, exact: bool = True):
    return page.get_by_role("button", name=name, exact=exact) if isinstance(name, str) else \
        page.get_by_role("button", name=name)


def _input_value(page, testid: str) -> str | None:
    """An input's value by its test id, or None where it is not drawn."""
    box = page.get_by_test_id(testid)
    return box.first.input_value() if box.count() else None


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


def boxes_overlap(a: dict | None, b: dict | None) -> bool:
    """Whether two bounding boxes (`{x, y, width, height}`) share any area -- keel-web 106 FR-5's friction row: the
    value and the status columns side by side, or wrapped one under the other, never over each other."""
    return bool(a and b and a["x"] < b["x"] + b["width"] and b["x"] < a["x"] + a["width"]
                and a["y"] < b["y"] + b["height"] and b["y"] < a["y"] + a["height"])


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

    def __init__(self, page: Page, recorder: Recorder, base_url: str = "", *, sheet: str = ""):
        self.page = page
        #: The sheet this object reads: the welcome by default; spec 057 hands it 086's report or opener sheet (the
        #: same `GuideSheet`, another test id) and reads it with the same calls.
        self.sheet = sheet or GUIDE_WELCOME
        self.base = (base_url or "").rstrip("/")
        self._b = _BrowserStep(recorder, page, "founder")
        self.recorder = recorder

    # --------------------------------------------------------------------------------------------- reads

    def present(self, timeout_s: float = 10) -> bool:
        """True once the sheet is visible, False if it never was within `timeout_s`."""
        try:
            self.page.locator(self.sheet).first.wait_for(state="visible", timeout=timeout_s * 1000)
            return True
        except Exception:  # noqa: BLE001 - absence is a reading, not a crash
            return False

    def count(self) -> int:
        return self.page.locator(self.sheet).count()

    def clip(self) -> dict:
        """keel-web 114 FR-1 (spec 073 FR-4): the sheet's clip key (`data-clip`) and the face's files -- the video's
        `src` and `poster` and its captions track's `src` -- as drawn."""
        none = {"clip": None, "src": None, "poster": None, "track": None}
        try:
            return self.page.evaluate("""([sheet, face]) => {
              const s = document.querySelector(sheet); const v = document.querySelector(face);
              const t = v && v.querySelector('track');
              return {clip: s ? s.getAttribute('data-clip') : null, src: v ? v.getAttribute('src') : null,
                      poster: v ? v.getAttribute('poster') : null, track: t ? t.getAttribute('src') : null};
            }""", [self.sheet, GUIDE_FACE]) or none
        except Exception:  # noqa: BLE001 - a read
            return none

    def absent(self, after: Callable[[], Any] | None = None, *, timeout_s: float = 15,
               grace_s: float = 5, seen_key: str = "welcomeSeen", screen: str = "") -> dict:
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
                self.page.locator(screen or PROJECT_SCREEN).first.wait_for(state="visible",
                                                                           timeout=timeout_s * 1000)
                drawn = True
            except Exception:  # noqa: BLE001 - recorded
                drawn = False
            guide = _guide_of(responses[0]) if responses else None
            if not (guide or {}).get(seen_key) is True:
                try:
                    self.page.locator(self.sheet).first.wait_for(state="attached", timeout=grace_s * 1000)
                except Exception:  # noqa: BLE001 - the expected outcome
                    pass
            count = self.count()
        finally:
            self.page.remove_listener("response", keep)
        return {"count": count, "received": guide, "screen": drawn, "overviews": len(responses),
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
            return self.page.evaluate(_CONTROLS_JS, self.sheet) or []
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
                self.page.locator(self.sheet).first.wait_for(state="detached", timeout=5_000)
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
            drawn = self.clip()                     # spec 073 FR-4: the clip per scope, read before Skip
            out = {"shown": True, "received": received, **drawn, **self._close(self._press_skip)}
            h.request = {"received": received}
            h.response = out
        return out


# ------------------------------------------------------------- keel-web 086's teaching videos (spec 057)
#
# The report sheet, the openers, the pills and the band (keel-web `specs/086-guide-teaching/spec.md` FR-3 to FR-8),
# spelled once. **The test ids are this spec's reading of 086 as specified** (built in parallel): the report and the
# opener play in 080's `GuideSheet` under their own `testId`; a pill carries its clip's key in `data-clip` and the
# fresh dot as `data-fresh`; the band and its chapter chip have their own ids. tasks.md names any not yet in 086.

GUIDE_REPORT = "[data-testid='guide-report']"
GUIDE_OPENER = "[data-testid='guide-opener']"
#: keel-web 086 `GuidePill`: a pressable pill is `button.guide-pill` (its test id, if any, is per placement); the fresh
#: dot is `guide-pill-new`, named *new* (D45). The pill carries no clip key: it is known by its words.
GUIDE_PILL = "button.guide-pill"
GUIDE_PILL_NEW = "[data-testid='guide-pill-new']"
GUIDE_BAND = "[data-testid='guide-band']"
GUIDE_CHAPTER = "[data-testid='guide-chapter']"
#: keel-web 086 FR-1: every clip key with `present` and its duration; a placement whose clip is absent draws no pill.
GUIDE_MANIFEST_PATH = "/guide/manifest.json"
#: The calibration card's primary (the one `Corridor._primary` presses), read while an explainer band is open.
CALIB_PRIMARY = ".ccard__foot button.btn.primary"

_PILLS_JS = r"""(sel) => Array.from(document.querySelectorAll(sel)).filter(
    (el) => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length)).map((el) => ({
  clip: el.getAttribute('data-clip'), testid: el.getAttribute('data-testid'),
  words: (el.innerText || '').replace(/\s+/g, ' ').trim(), label: el.getAttribute('aria-label'),
  fresh: !!el.querySelector('[data-testid="guide-pill-new"], [aria-label="new" i]')}))"""


def _safe_eval(page: Page, js: str, arg: Any) -> list:
    try:
        return page.evaluate(js, arg) or []
    except Exception:  # noqa: BLE001 - a read on a page mid-navigation
        return []


def normal_manifest(body: Any) -> dict:
    """keel-web 086's `manifest.json` as `{key: {present, duration}}`, whatever its outer shape: a map of key to entry,
    the same under `clips`, or a list of entries carrying `key`. Anything else (a web before 086, a 404) is `{}` --
    every clip absent."""
    if isinstance(body, dict) and isinstance(body.get("clips"), (dict, list)):
        body = body["clips"]
    rows = body.items() if isinstance(body, dict) else (
        ((r.get("key"), r) for r in body if isinstance(r, dict)) if isinstance(body, list) else ())
    out = {}
    for key, row in rows:
        if isinstance(key, str) and isinstance(row, dict):
            out[key] = {"present": row.get("present") is True, "duration": row.get("duration")}
    return out


class GuideTeaching:
    """keel-web 086's teaching videos (spec 057): the served manifest and captions, the pills on a page, the band a pill
    opens (its chapter chip, its face, its snippet's words), and the calibration primary under an open band. Acts and
    reads; asserts nothing -- `evals/corpus_scenario` judges, `evals/guide_marks.py` scores."""

    def __init__(self, page: Page, recorder: Recorder, base_url: str = ""):
        self.page = page
        self.base = (base_url or "").rstrip("/")
        self._b = _BrowserStep(recorder, page, "founder")
        self._manifest: dict | None = None

    # ------------------------------------------------------------------------------------------ served

    def _get(self, path: str):
        try:
            return self.page.context.request.get(f"{self.base}{path}", timeout=10_000)
        except Exception:  # noqa: BLE001 - not served: the reading
            return None

    def manifest(self) -> dict:
        """`/guide/manifest.json` as the web serves it, normalised (`normal_manifest`); read once per object."""
        if self._manifest is None:
            response = self._get(GUIDE_MANIFEST_PATH)
            try:
                body = response.json() if response is not None and response.ok else None
            except Exception:  # noqa: BLE001 - not JSON (a SPA fallback page)
                body = None
            self._manifest = normal_manifest(body)
        return self._manifest

    def present(self, key: str) -> bool:
        return (self.manifest().get(key) or {}).get("present") is True

    def vtt(self, key: str) -> str | None:
        """`/guide/{key}.vtt` as served, or None (absent, or the SPA's HTML fallback)."""
        response = self._get(f"/guide/{key}.vtt")
        if response is None or not response.ok:
            return None
        text = response.text()
        return text if text.lstrip().startswith("WEBVTT") else None

    # -------------------------------------------------------------------------------------------- reads

    def pills(self) -> list[dict]:
        """Every visible pill: its clip (`data-clip`), words, label and fresh dot."""
        try:
            return self.page.evaluate(_PILLS_JS, GUIDE_PILL) or []
        except Exception:  # noqa: BLE001 - a read
            return []

    def band(self) -> dict:
        """The open band: present, its chapter chip's words, its face's source, its snippet's words."""
        band = self.page.locator(GUIDE_BAND)
        if not band.count():
            return {"present": False}
        face = band.first.locator(GUIDE_FACE)
        src = None
        if face.count():
            try:
                src = face.first.evaluate("(v) => v.currentSrc || v.src || ''")
            except Exception:  # noqa: BLE001 - a read
                src = None
        return {"present": True, "chip": _tc(band.first.locator(GUIDE_CHAPTER)), "src": src,
                "snippet": _tc(band.first.locator(GUIDE_SNIPPET))}

    def fields(self) -> int:
        """The question's visible answer fields (inputs, boxes, lists, radios) -- 086 FR-5 hides them under a band."""
        try:
            return int(self.page.evaluate(
                "() => Array.from(document.querySelectorAll('.ccard input, .ccard textarea, .ccard select, "
                ".ccard [role=radio]')).filter((el) => !!(el.offsetWidth || el.offsetHeight "
                "|| el.getClientRects().length)).length"))
        except Exception:  # noqa: BLE001 - a read
            return -1

    def primary_disabled(self) -> bool | None:
        primary = self.page.locator(CALIB_PRIMARY)
        if not primary.count():
            return None
        try:
            return bool(primary.first.evaluate("(b) => b.disabled || b.getAttribute('aria-disabled') === 'true'"))
        except Exception:  # noqa: BLE001 - a read
            return None

    # ------------------------------------------------------------------------------------------ actions

    def _posts_during(self, act: Callable[[], Any], settle_ms: int = GUIDE_SETTLE_MS) -> list[dict]:
        seen: list = []

        def keep(request) -> None:
            if request.method == "POST" and GUIDE_SEEN_PATH.search(request.url):
                seen.append(request)

        self.page.on("request", keep)
        try:
            act()
            if not seen:
                try:
                    self.page.wait_for_event("request", predicate=lambda r: r.method == "POST"
                                             and bool(GUIDE_SEEN_PATH.search(r.url)), timeout=settle_ms)
                except Exception:  # noqa: BLE001 - none went out
                    pass
        finally:
            self.page.remove_listener("request", keep)
        return [_request_row(r) for r in seen]

    def open_pill(self, pill_id: str) -> dict:
        """Presses keel-web 086's pill `guide-pill-{pill_id}` (`report-read`, `report-fails`, `stage`, `explain`);
        `{opened, band}`."""
        clip = pill_id
        with self._b.step(f"founder presses the guide pill {pill_id}") as h:
            pills = self.page.locator(f"{GUIDE_PILL}[data-testid='guide-pill-{pill_id}']")
            if not pills.count():
                return {"opened": False, "band": {"present": False}}
            pills.first.click()
            try:
                self.page.locator(GUIDE_BAND).first.wait_for(state="visible", timeout=5_000)
            except Exception:  # noqa: BLE001 - recorded
                pass
            band = self.band()
            h.add_screenshot(self._b.screenshot(f"guide-band-{clip or 'pill'}"))
        return {"opened": band["present"], "band": band}

    def _gone(self) -> bool:
        try:
            self.page.locator(GUIDE_BAND).first.wait_for(state="detached", timeout=5_000)
            return True
        except Exception:  # noqa: BLE001 - recorded
            return False

    def band_skip(self) -> dict:
        """Skip inside the band; `{closed, requests}` (the `guide-seen` posts the press caused)."""
        out: dict = {}

        def press() -> None:
            self.page.locator(f"{GUIDE_BAND} {GUIDE_SKIP}").first.click()
            out["closed"] = self._gone()

        requests = self._posts_during(press)
        return {"closed": bool(out.get("closed")), "requests": requests}

    def seek(self, seconds: float) -> bool:
        return bool(self.page.evaluate("([n, s]) => window[n] ? (window[n].seek(s), true) : false",
                                       [GUIDE_SEAM, seconds]))

    def seam(self) -> bool:
        try:
            return bool(self.page.evaluate("(n) => !!window[n]", GUIDE_SEAM))
        except Exception:  # noqa: BLE001 - a read
            return False

    def band_end(self, seconds: float) -> dict:
        """Seeks the band's current clip to `seconds` (its end) through the seam; `{closed, requests}`."""
        out: dict = {}

        def end() -> None:
            self.seek(seconds)
            out["closed"] = self._gone()

        requests = self._posts_during(end)
        return {"closed": bool(out.get("closed")), "requests": requests}

    def wait_chip(self, words: str, *, timeout_s: float = 3.0) -> str:
        """Waits (bounded) for the chip to carry `words`; returns what it carries."""
        try:
            self.page.locator(GUIDE_CHAPTER, has_text=words).first.wait_for(state="visible",
                                                                            timeout=timeout_s * 1000)
        except Exception:  # noqa: BLE001 - read whatever is drawn
            pass
        return _tc(self.page.locator(GUIDE_CHAPTER))


# ------------------------------------------------- spec 057: passing 086's opener and report sheets by

#: keel-web 086 FR-8: each founder stage's opener clip; `stageOfPath`'s reading of the address (086 `ProjectShell`).
OPENER_CLIPS = {"PROBLEM": "opener-the-problem", "SOLUTION": "opener-your-solution",
                "COMMERCIAL": "opener-will-they-pay"}
_STAGE_OF_PATH = {"problem": "PROBLEM", "solution": "SOLUTION", "persona": "COMMERCIAL", "commercial": "COMMERCIAL"}
_PROJECT_OF_URL = re.compile(r"/p/([^/?#]+)")
#: One served manifest per web base for the run (the pass-by reads it on every stage and report open).
_MANIFESTS: dict = {}


def _due_guide(page: Page, base: str) -> dict | None:
    """The project's `Overview.guide` off the page's own origin (keel-web proxies `/v2`), or None."""
    found = _PROJECT_OF_URL.search(page.url or "")
    if not found:
        return None
    try:
        response = page.context.request.get(f"{base}/v2/projects/{found.group(1)}/overview", timeout=10_000)
        guide = (response.json() or {}).get("guide") if response.ok else None
    except Exception:  # noqa: BLE001 - not readable: nothing is due
        return None
    return guide if isinstance(guide, dict) else None


def pass_teaching_sheet(page: Page, recorder: Recorder, base: str, kind: str, stage: str | None = None, *,
                        timeout_s: float = 10.0) -> dict:
    """The coordinator's pass-by for spec 057: every journey that does not judge keel-web 086's teaching sheets (all
    but S-005's measured founder journey) skips them as `MarketStep.start` skips the welcome. `kind` is `"opener"`
    (with the founder `stage`, or the one the address names) or `"report"`. Decided without a wait from the served
    manifest and the project's `guide` (contract 22): a sheet already up is skipped; one that is due (clip present,
    the stage not in `openersSeen` / `reportSeen` false) is waited for up to `timeout_s` and skipped in one `note`
    step; nothing due, no wait. Absence is never a failure."""
    base = (base or "").rstrip("/")
    if kind == "opener" and stage is None:
        part = re.search(r"/define/([a-z]+)", page.url or "")
        stage = _STAGE_OF_PATH.get(part.group(1)) if part else None
    if kind == "opener" and stage not in OPENER_CLIPS:
        return {"shown": False, "why": "not a founder stage"}
    selector, clip = (GUIDE_REPORT, "report-read") if kind == "report" else (GUIDE_OPENER, OPENER_CLIPS[stage])
    sheet = GuideWelcome(page, recorder, base, sheet=selector)
    if not sheet.count():
        if base not in _MANIFESTS:
            _MANIFESTS[base] = GuideTeaching(page, recorder, base).manifest()
        if not (_MANIFESTS[base].get(clip) or {}).get("present"):
            return {"shown": False, "why": f"{clip} absent from the manifest"}
        guide = _due_guide(page, base)
        if guide is None or "reportSeen" not in guide:
            return {"shown": False, "why": "no contract-22 guide"}
        due = guide.get("reportSeen") is False if kind == "report" else stage not in (guide.get("openersSeen") or [])
        if not due or not sheet.present(timeout_s=timeout_s):
            return {"shown": False, "due": due}
    with recorder.step(f"keel-web 086's {kind} sheet{f' ({stage})' if stage else ''} opened; this journey does not "
                       "judge it and passes it by with Skip (spec 057)", party="founder", kind="note") as h:
        out = {"shown": True, "kind": kind, "stage": stage, **sheet._close(sheet._press_skip)}
        h.request = {"kind": kind, "stage": stage}
        h.response = out
    return out


# --------------------------------------------------------------------------------------- Corridor

#: Spec 073 FR-1 (keel-web 113 FR-1): every state the context step's root names from the moment it is installed, one
#: row a state as it is entered (`data-context-state`), with what that state draws -- the wait's status line, counter,
#: phase bar and truth card, and no field or Save; the card's sentence, its two buttons and no box; the form's four
#: boxes and Save. A MutationObserver, so a wait that lasts one render is still seen; a state's booleans and counts are
#: merged over its whole stay (the counter mounts with the block) and its words are the last it drew (the card's first
#: render reads *Save and continue* until its occasion field is pre-filled, then *Yes, that's it*).
_CONTEXT_STATES_JS = """() => {
  const words = (el) => el ? (el.textContent || '').replace(/\\s+/g, ' ').trim() : null;
  const read = () => {
    const root = document.querySelector('[data-testid=context-step]');
    if (!root) return null;
    const state = root.getAttribute('data-context-state');
    const out = {state};
    if (state === 'wait') {
      const block = root.querySelector('.waitco-block');
      out.status = words(block && block.querySelector('p.cnote[role=status]'));
      out.elapsed = !!root.querySelector('.waitco .waitco__elapsed');
      out.phasebar = !!root.querySelector('.waitco .phasebar');
      out.truth = !!root.querySelector('.waitco .truth');
      out.fields = root.querySelectorAll('.cfield').length;
      out.save = root.querySelectorAll('[data-testid=context-save]').length;
    } else if (state === 'card') {
      const card = root.querySelector('.understands');
      out.big = words(card && card.querySelector('.understands__big'));
      out.yes = words(card && card.querySelector('.actions .btn.primary'));
      out.edit = words(card && card.querySelector('.actions .btn:not(.primary)'));
      out.boxes = root.querySelectorAll('textarea.cfield__input').length;
    } else {
      out.boxes = root.querySelectorAll('textarea.cfield__input').length;
      out.save = root.querySelectorAll('[data-testid=context-save]').length;
    }
    return out;
  };
  const seen = window.__keelContextStates = [];
  const keep = () => {
    const r = read();
    if (!r) return;
    const last = seen[seen.length - 1];
    if (!last || last.state !== r.state) { seen.push(r); return; }
    for (const [k, v] of Object.entries(r)) {
      if (typeof v === 'boolean') last[k] = last[k] || v;
      else if (typeof v === 'number') last[k] = Math.max(last[k] || 0, v);
      else if (v) last[k] = v;                // words: the state's settled ones (an effect fills the card's field)
    }
  };
  window.__keelContextKeep = keep;
  if (window.__keelContextObserver) window.__keelContextObserver.disconnect();
  window.__keelContextObserver = new MutationObserver(keep);
  window.__keelContextObserver.observe(document.body, {subtree: true, childList: true, characterData: true,
                                                       attributes: true});
  keep();
  return seen.length;
}"""
_CONTEXT_STATES_READ_JS = """() => {
  if (window.__keelContextKeep) window.__keelContextKeep();
  if (window.__keelContextObserver) window.__keelContextObserver.disconnect();
  return window.__keelContextStates || [];
}"""

#: Spec 067 FR-5: how often the context card's wait looks at the CONTEXT_INTERPRET job (ms).
CONTEXT_POLL_MS = 5_000


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
        #: Spec 073 FR-1: each context Save's states as the step's root named them (`_CONTEXT_STATES_JS`).
        self.context_states = []
        self.resent = []
        #: Spec 071: whether the context step drew the recall window (none on money alone, keel-web 109 FR-3).
        self.window_drawn = None
        #: Spec 062 FR-3: the back-test's camera, called with a slug on every founder screen as it is about to be
        #: answered (`evals/backtest.Camera`); None on every other journey, where `_shot` does nothing.
        self.camera = None

    def _shot(self, slug: str) -> None:
        if self.camera is not None:
            self.camera(slug)

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
                "welcome": self.page.locator(GUIDE_WELCOME).count(),
                # spec 057 G10 / G11: the pills under the question (each clip's key) and the opener sheets over it
                "pills": _safe_eval(self.page, _PILLS_JS, GUIDE_PILL),
                "openers": self.page.locator(GUIDE_OPENER).count()}

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

    def context(self, project_id: str, fields: dict, window: dict, *,
                on_wait: Callable[[str | None], None] | None = None) -> str:
        """Types the four fields and the window, saves, and waits for the *Keel understands* card.
        Returns the card's sentence as drawn.

        Spec 067 FR-5 (keel-cloud 128 FR-15): while the card is awaited, `on_wait(interaction_id)` is called every few
        seconds -- the CONTEXT_INTERPRET interaction the Save started, read off its response -- so the journey can see
        a `NEEDS_INPUT` the page draws no screen for (keel-web 106 FR-7 is unbuilt) and answer it, or stop, instead of
        waiting out the card's 660 s."""
        with self._b.step("founder fills the context step: who, what, when, which people, and the "
                          + (f"recall window ({window['count']} {window['unit']})" if window is not None
                             else "no recall window (money alone)")) as h:
            self.page.goto(f"{self.base}/p/{project_id}/define/context", wait_until="load")
            self.page.locator("#context-actor").wait_for(state="visible", timeout=20_000)
            self._shot("context")
            for key in ("actor", "job", "circumstance", "segment"):
                self.page.locator(f"#context-{key}").fill(fields[key])
            if window is not None:
                self.page.locator("input.cwindow__count").fill(str(window["count"]))
                self.page.locator("select.cwindow__unit").select_option(window["unit"])
            # spec 071 (keel-web 109 FR-3): money alone draws no recall window -- `window` None, and none is typed
            self.window_drawn = self.page.locator("input.cwindow__count").count() > 0
            h.add_screenshot(self._b.screenshot("context-filled"))
            self.page.evaluate(_CONTEXT_STATES_JS)
            saved = self._save_context()
            self.saves.append(saved)
            if isinstance(saved.get("status"), int) and saved["status"] >= 400:
                # A refused Save never brings the card (and the screen has no second press): the leg reads
                # `saves` and names what refused it rather than a minute's timeout (spec 054 FR-2 d).
                h.capture_text("stage_screen", _screen_text(self.page, ".ccard"))
                return ""
            card = self.page.locator(".understands").first
            if on_wait is None:
                card.wait_for(state="visible", timeout=60_000 * self.patience)
            else:
                deadline = time.monotonic() + 60 * self.patience
                while True:
                    try:
                        card.wait_for(state="visible", timeout=CONTEXT_POLL_MS)
                        break
                    except Exception:  # noqa: BLE001 - Playwright's timeout: look at the job, then wait again
                        if time.monotonic() > deadline:
                            raise
                        on_wait(saved.get("interaction_id"))
            self.context_states.append(self.page.evaluate(_CONTEXT_STATES_READ_JS))
            h.capture_text("stage_screen", _screen_text(self.page, ".ccard"))
            h.add_screenshot(self._b.screenshot("context-card"))
            self._shot("context-card")
            return _first_text(self.page, ".understands__big")

    #: Every context Save's answer as the page received it (`PUT /v2/projects/{id}/context`): method, path, status.
    saves: list

    def _save_context(self) -> dict:
        try:
            with self.page.expect_response(lambda r: r.request.method == "PUT"
                                           and r.url.split("?")[0].endswith("/context"), timeout=20_000) as got:
                _button(self.page, CONTEXT_SAVE).click()
            response = got.value
            body = _json_body(response)
            try:
                sent = response.request.post_data_json
            except Exception:  # noqa: BLE001 - a body the page did not send as JSON is recorded as none
                sent = None
            return {"method": "PUT", "path": response.url.split("?")[0], "status": response.status,
                    "body": body if response.status >= 400 else None,
                    # spec 068 FR-5 (contract 36, keel-cloud 129 FR-11): the fields the page sent -- the four, the
                    # window and, once the founder's occasion field holds one, `occasion`
                    "sent": sent if isinstance(sent, dict) else None,
                    "occasion": sent.get("occasion") if isinstance(sent, dict) else None,
                    # spec 067 FR-5: the CONTEXT_INTERPRET interaction this Save started (`InteractionView`)
                    "interaction_id": (body or {}).get("interaction_id") if response.status < 400
                    and isinstance(body, dict) else None}
        except Exception as missing:  # noqa: BLE001 - recorded: no Save reached the wire
            return {"method": "PUT", "path": None, "status": None, "error": repr(missing)}

    def context_occasion(self) -> dict:
        """keel-web 106 FR-1 (contract 36, keel-cloud 129 FR-11; spec 068 FR-4): the context card's *occasion*, pre-filled
        with the noun Keel found in its read-back (`occasion.noun`); absent on a contract without it.

        Spec 074 (keel-web 117): the occasion lives on the card's *I'll ask about* line, which ends with *Change*
        (`context-occasion-change`); the block under the card (`.cfield--occasion`) is gone. The walk taps *Change*
        to read the field it opens in the line's place (`[data-testid=context-occasion]`, the input
        `#context-occasion`, its hint), then Esc puts the line back with the change dropped -- nothing is edited or
        saved. Before 117 (no *Change*) the old field under the card is read as it stands."""
        change = self.page.get_by_test_id("context-occasion-change")
        blocks = self.page.locator(".cfield--occasion").count()
        if not change.count():
            node = self.page.get_by_test_id("context-occasion")
            if not node.count():
                return {"drawn": False, "value": None, "change": None, "block": blocks}
            field = self.page.locator("input#context-occasion")
            value = _value(field.first) if field.count() else _first_text(self.page, "#context-occasion")
            return {"drawn": True, "value": " ".join((value or "").split()) or None, "change": None, "block": blocks,
                    "refused": _first_text(self.page, "#context-occasion-refused") or None}
        line = _first_text(self.page, "[data-testid=context-ask-about]") or None
        label = _tc(change)
        change.first.click()
        field = self.page.locator("[data-testid=context-occasion] input#context-occasion").first
        field.wait_for(state="visible", timeout=10_000)
        value = _value(field)
        opened = {"value": " ".join((value or "").split()) or None,
                  "hint": _first_text(self.page, "#context-occasion-hint") or None,
                  "refused": _first_text(self.page, "#context-occasion-refused") or None,
                  "focused": bool(field.evaluate("(el) => document.activeElement === el")),
                  "line_while_open": self.page.get_by_test_id("context-ask-about").count()}
        field.press("Escape")
        self.page.get_by_test_id("context-occasion").first.wait_for(state="detached", timeout=10_000)
        back = _first_text(self.page, "[data-testid=context-ask-about]") or None
        return {"drawn": True, **opened, "change": label, "line": line, "line_back": back == line and back is not None,
                "block": blocks, "primary": _tc(self.page.locator(".understands .actions .btn.primary"))}

    def needs_input(self, content: str) -> dict | None:
        """keel-web 106 FR-7 (spec 068 FR-4): the needs-input screen -- the one question the interpret asked
        (`[data-testid=context-needs-input]`, `.cneeds__q`), answered once in its box and sent
        (`context-needs-input-send`); the re-ask line (`context-reasked`) read where the page reopened the fields
        instead. None where the page draws neither (the caller answers on the wire)."""
        screen = self.page.get_by_test_id("context-needs-input")
        if screen.count() and screen.first.is_visible():
            question = _first_text(screen.first, ".cneeds__q")
            with self._b.step("founder answers the one thing the context read-back asked, once, on the page "
                              "(keel-web 106 FR-7)") as h:
                screen.first.locator("textarea").first.fill(content)
                h.add_screenshot(self._b.screenshot("context-needs-input"))
                self.page.get_by_test_id("context-needs-input-send").first.click()
            return {"via": "page", "question": question or None}
        reasked = self.page.get_by_test_id("context-reasked")
        if reasked.count() and reasked.first.is_visible():
            return {"via": "reasked", "line": _tc(reasked)}
        return None

    def context_window_line(self) -> str:
        return _first_text(self.page, ".understands__window")

    def context_lines(self) -> dict:
        """keel-web 096 FR-2 (spec 064 FR-4c): the card's two muted lines -- *I'll ask about: <stem>.* (absent with no
        stem) and *Only people who: <condition>.* (absent with no condition) -- and the proposed window's line."""
        out = {}
        for key, testid in (("ask_about", "context-ask-about"), ("only_people_who", "context-only-people-who"),
                            ("window_proposed_from", "window-proposed-from")):
            node = self.page.get_by_test_id(testid)
            out[key] = " ".join((node.first.text_content() or "").split()) if node.count() else None
        return out

    def context_confirmed(self, project_id: str) -> dict:
        """keel-web 113 FR-1 (spec 073 FR-1): the context step re-opened once confirmed -- the confirmed state (the
        sentence, the window line, *Continue to the problem* and *Edit*, no box) -- then *Edit*: the form again, its
        four boxes, the occasion and the window filled with what was confirmed. Nothing is saved; the walk goes on
        from another address."""
        with self._b.step("founder re-opens the confirmed context and presses Edit: the form comes back filled "
                          "(keel-web 113 FR-1)") as h:
            self.page.goto(f"{self.base}/p/{project_id}/define/context", wait_until="load")
            root = self.page.locator(f"{CONTEXT_STEP}[data-context-state=confirmed]").first
            root.wait_for(state="visible", timeout=20_000)
            understood = root.locator("[data-testid=context-understood]")
            edit = self.page.get_by_test_id("context-edit")
            out = {"state": root.get_attribute("data-context-state"),
                   "understands": _tc(understood.locator(".understands__big")),
                   "window": _tc(understood.locator(".understands__window")) or None,
                   "continue": _tc(root.locator(".ccard__foot .btn.primary")),
                   "edit": _tc(edit), "boxes": root.locator("textarea.cfield__input").count()}
            h.capture_text("stage_screen", _screen_text(self.page, ".ccard"))
            h.add_screenshot(self._b.screenshot("context-confirmed-reopened"))
            edit.first.click()
            form = self.page.locator(f"{CONTEXT_STEP}[data-context-state=form]").first
            form.wait_for(state="visible", timeout=10_000)
            count = form.locator("input.cwindow__count")
            unit = form.locator("select.cwindow__unit")
            # keel-web 117 FR-2: Edit's form draws no occasion block (the occasion is the card's); read for its absence
            occasion = form.locator("input#context-occasion")
            raw = _value(count.first) if count.count() else None
            out["edited"] = {
                "state": form.get_attribute("data-context-state"),
                "fields": {k: _value(form.locator(f"textarea#context-{k}").first)
                           for k in ("actor", "job", "circumstance", "segment")},
                "window": {"count": int(raw) if raw and raw.isdigit() else raw, "unit": _value(unit.first)}
                if raw is not None else None,
                "occasion": _value(occasion.first) if occasion.count() else None,
                "save": _tc(self.page.get_by_test_id("context-save"))}
            h.add_screenshot(self._b.screenshot("context-edit-filled"))
            return out

    def confirm_context(self) -> None:
        with self._b.step("founder confirms: Yes, that's it") as h:
            _button(self.page, CONTEXT_YES).click()
            _wait_url(self.page, r"/define/problem/seed")
            h.add_screenshot(self._b.screenshot("context-confirmed"))

    # --------------------------------------------------------------------- steps 2-3: the seeds

    def seed(self, project_id: str, vector: str, text: str, *, resend: int = 0) -> dict:
        """Types the seed into the chat and waits for the card. Returns what the card draws.

        `resend` (spec 062, the back-test only; 0 everywhere else, where nothing below the send changes): when the chat
        opens its composer again instead of drawing the card -- the model's answer refused (*came back in a shape this
        step can't use ... Start the step again*) or a clarifying question asked -- the founder sends the seed again,
        up to `resend` times, and each time the chat's last words are kept in `self.resent`."""
        slug = vector.lower()
        kicker = KICKER_INTERPRETATION if vector == "PROBLEM" else KICKER_MECHANISM
        with self._b.step(f"founder types the {slug} seed and sends it") as h:
            if f"/define/{slug}/seed" not in self.page.url:
                self.page.goto(f"{self.base}/p/{project_id}/define/{slug}/seed", wait_until="load")
            box = self.page.get_by_role("textbox", name=SEED_SEND)
            box.wait_for(state="visible", timeout=20_000)
            pass_teaching_sheet(self.page, self._b.recorder, self.base, "opener", vector)
            self._shot(f"{slug}-seed")
            box.fill(text)
            _button(self.page, SEED_SEND).click()
            for attempt in range(resend + 1):
                if not resend:
                    self.page.get_by_text(kicker).first.wait_for(state="visible",
                                                                 timeout=60_000 * self.patience)
                    break
                if self._card_or_composer(kicker, box) == "card":
                    break
                said = _text(self.page)[-600:]
                self._shot(f"{slug}-seed-again")
                self.resent.append({"vector": vector, "chat said": said})
                if attempt == resend:
                    raise AssertionError(f"the {slug} seed drew no card after {resend} resends: {said}")
                box.fill(text)
                _button(self.page, SEED_SEND).click()
            h.add_screenshot(self._b.screenshot(f"{slug}-card"))
            self._shot(f"{slug}-card")
            claim = _first_text(self.page, ".understood__claim")
            rows = {}
            for row in self.page.locator(".mrow").all():
                label = _first_text(row, ".mrow__label")
                rows[label] = _safe_text(lambda: row.inner_text())
            h.capture_text("stage_screen", _text(self.page))
            return {"claim": claim, "rows": rows, "text": _text(self.page)}

    #: Spec 062: what the chat said each time the back-test sent a seed again (`seed(..., resend=n)`).
    resent: list

    def _card_or_composer(self, kicker: str, box) -> str:
        """After a send: "card" once the card's kicker is drawn, "composer" once the composer opened again (the send
        settled with no card), waited for as long as the card is."""
        try:
            box.wait_for(state="hidden", timeout=15_000)          # the composer closes while the step runs
        except Exception:  # noqa: BLE001 - a step quick enough never shows it closed
            pass
        deadline = time.monotonic() + 60 * self.patience
        while time.monotonic() < deadline:
            if self.page.get_by_text(kicker).first.is_visible():
                return "card"
            if box.is_visible() and box.is_enabled():
                return "composer"
            self.page.wait_for_timeout(1_000)
        raise AssertionError(f"neither the card ({kicker!r}) nor the composer came back")

    def confirm_seed(self, vector: str, scope: str = "ALL") -> None:
        """The card confirmed: the problem's opens Prevalence; the solution's is the idea's Answer (keel-web
        063 call 1), so it opens S2, the idea's Check screen. Spec 071 (keel-web 109 FR-3): where the scope does not
        calibrate the problem, its card goes on to the solution's seed (money alone's *Your idea*)."""
        slug = vector.lower()
        name = CARD_YES_PROBLEM if vector == "PROBLEM" else CARD_LOOKS_RIGHT
        nxt = (r"/define/problem/q/1" if calibrates("PROBLEM", scope) else r"/define/solution/seed") \
            if vector == "PROBLEM" else r"/define/solution/idea"
        with self._b.step(f"founder confirms the {slug} card: {name}") as h:
            _button(self.page, name).click()
            _wait_url(self.page, nxt)
            h.add_screenshot(self._b.screenshot(f"{slug}-confirmed"))

    def idea_check(self, name: str | None = None, *, next_url: str = r"/define/solution/q/\d+$") -> dict:
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
            # keel-web 106 FR-6 (spec 068 FR-4): the box opens empty and the seed's name is offered under it
            hint = self.page.locator("[data-testid=idea-name-suggestion] button")
            suggestion = _tc(hint) if hint.count() else None
            frame = self.frame()
            counter = {"drawn": self._name_counter()}
            h.capture_text("stage_screen", _text(self.page))
            h.add_screenshot(self._b.screenshot("idea-check"))
            self._shot("idea")
            if name:
                # keel-web 066 (D14): the counter is live and Save is off over five words -- typed once one word past
                # five, read, then the name itself.
                over = f"{name} {' '.join(['for', 'every', 'single', 'day', 'and', 'night'][:6 - len(name.split())])}"
                what.fill(over)
                counter["over"] = {"typed": over, **self._name_counter()}
                h.add_screenshot(self._b.screenshot("idea-named-over-five"))
                what.fill(name)
                # keel-web 083 (D33): Save waits while a step is open or the screen's revision lags the overview
                # (`corridor-waiting`), and lights within one poll; give it that poll before reading the named state.
                try:
                    self.page.locator("[data-testid=idea-save]:enabled, button:enabled:has-text('Save')").first.wait_for(
                        state="visible", timeout=15_000)
                except Exception:
                    pass
                counter["named"] = {**self._name_counter(),
                                    "waiting": self.page.locator("[data-testid=corridor-waiting]").count() > 0}
                h.add_screenshot(self._b.screenshot("idea-named"))
            label = self._press_primary(SAVE)
            # spec 071 (keel-web 109 FR-3): on money alone the idea card's Save goes to who decides
            _wait_url(self.page, next_url)
            return {"lines": lines, "unnamed": unnamed, "typed": name, "frame": frame, "primary": label,
                    "reloaded": reloaded, "counter": counter, "suggestion": suggestion or None}

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
            self._shot(f"q-{name}")
            control = question.get("control")
            labels = {o.get("normalized"): o.get("label") for o in question.get("options") or []}
            seen_chain: dict = {}
            boxes: dict = {}
            if control == "price_range":
                # spec 075 (keel-cloud 140, 141): as the screen opens, before anything is typed -- the cost box over the
                # price (`priceCostBox`, the served `costEstimate.said`) and the chain's Ability to pay box (the served
                # `abilityToPay.sentence`, drawn while the draft is untouched)
                try:
                    self.page.locator(".calib__costbox").first.wait_for(state="visible", timeout=5_000)
                except Exception:  # noqa: BLE001 - a screen with no cost estimate draws none
                    pass
                boxes = {"costbox": _first_text(self.page, ".calib__costbox") or None,
                         "ability": _first_text(self.page, ".calib__ability p") or None}
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
            elif control == "cost_estimate" and self.page.get_by_test_id("chain-cost").count():
                seen_chain = self._chain_cost(answer["cost"])
            elif control == "price_range" and self.page.get_by_test_id("chain-price").count():
                seen_chain = self._chain_price(answer["price"])
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
                    "belief": _first_text(self.page, ".calib__belief-text"), **seen_chain}
            seen.update(boxes)
            h.capture_text("stage_screen", _text(self.page))
            h.add_screenshot(self._b.screenshot(f"calibration-{name}"))
            seen["primary"] = self._press_primary()
            return seen

    def chain_screen(self, control: str) -> bool:
        """Whether keel-web 094 draws the commercial chain's screen for this control (a fresh project, or one whose
        stored answer is the chain's), rather than spec 074's controls (an answer stored before the chain)."""
        testid = "chain-cost" if control == "cost_estimate" else "chain-price"
        try:
            self.page.locator("h1.calib__q").first.wait_for(state="visible", timeout=30_000)
        except Exception:  # noqa: BLE001 - the screen's own read below says what it drew
            pass
        return self.page.get_by_test_id(testid).count() > 0

    def _chain_cost(self, cost: dict) -> dict:
        """keel-web 094 FR-1 (spec 064 FR-2): the chain's cost step -- the way (*Money they spend* / *Time it takes* /
        *A rate they lose*), the unit box, the period pill, then on the equation a rate's measure (% or a count word)
        and its "of what they lose" box, the two numbers, the hourly rate on time at a B2B study; the equation line
        read back (`equation`, its words after the boxes `per`). A base on money or time is drawn read-only only where
        a stored answer carries one (094 judgement call 4): none is typed."""
        page = self.page
        # spec 075 (keel-web 123 FR-1): *Per* arrives filled (the role word) with its helper line, before anything is
        # typed; *of* arrives filled (the occasion) once a way with the box is picked
        filled = {"unit": _input_value(page, "chain-unit"), "unit_help": _first_text(page, "#chain-unit-help") or None}
        page.get_by_test_id(f"chain-mode-{'MONEY' if cost['mode'] == 'AMOUNT' else cost['mode']}").click()
        filled["base"] = _input_value(page, "chain-base")
        filled["base_help"] = _first_text(page, "#chain-base-help") or None
        page.get_by_test_id("chain-unit").fill(str(cost.get("unit") or ""))
        page.get_by_test_id(f"chain-period-{cost['period']}").click()
        page.get_by_test_id("chain-equation").wait_for(state="visible", timeout=10_000)
        if cost["mode"] == "HOURS":
            # keel-web 123 FR-2: the rate (and, while it is Keel's figure, its note) drawn whenever the view carries
            # `hourlyRate`, directly under the hours row
            filled["rate"] = _input_value(page, "chain-rate")
            filled["rate_note"] = HOURLY_RATE_DEFAULTED if page.locator(
                ".calib__note", has_text=HOURLY_RATE_DEFAULTED).count() else None
            filled["order"] = page.evaluate("""() => {
                const eq = document.querySelector('[data-testid=chain-equation]');
                if (!eq) return [];
                const at = (sel) => { const el = eq.querySelector(sel); return el ? el.getBoundingClientRect().top : null; };
                return [at('[data-testid=chain-low]'), at('[data-testid=chain-rate]'), at('[data-testid=chain-base]')];
            }""")
        if cost["mode"] == "RATE":
            if (cost.get("measure") or "%") == "%":
                page.get_by_test_id("chain-measure-percent").click()
            else:
                page.get_by_test_id("chain-measure-count").click()
                page.get_by_test_id("chain-count").fill(str(cost.get("measure")))
            page.get_by_test_id("chain-base").fill(str(cost.get("base") or ""))
        elif cost["mode"] == "HOURS" and cost.get("base") and page.get_by_test_id("chain-base").count():
            # keel-web 102 FR-3c (keel-cloud 126 FR-2): on hours the founder says what the hours are spent on, so the
            # strangers' question names it ("how many hours did the daily log take your team?"); typed where the box is
            page.get_by_test_id("chain-base").fill(str(cost.get("base")))
        page.get_by_test_id("chain-low").fill(_number(cost["low"]))
        page.get_by_test_id("chain-high").fill(_number(cost["high"]))
        rate = page.get_by_test_id("chain-rate")
        if cost["mode"] == "HOURS" and cost.get("rate") is not None and rate.count():
            rate.fill(_number(cost["rate"]))
        return {"chain": True, "equation": _first_text(page, "[data-testid=chain-equation]"),
                "per": _first_text(page, "[data-testid=chain-per]"), "filled": filled}

    def _chain_price(self, price: dict) -> dict:
        """keel-web 094 FR-2: the chain's price step -- the shape pill, then its numbers (an amount a period's range;
        a share's sub-choice and its one percent; up front and the plan, or *then nothing*; nothing for free), the
        locked words read back (`locked`: the cost's unit and period, never typed or sent)."""
        page = self.page
        shape = price["shape"]
        page.get_by_test_id(f"chain-shape-{shape}").click()
        if shape == "AMOUNT_PERIOD":
            page.get_by_test_id("chain-price-low").fill(_number(price["low"]))
            page.get_by_test_id("chain-price-high").fill(_number(price["high"]))
        elif shape == "SHARE":
            page.get_by_test_id(f"chain-share-{price.get('shareBase') or 'COST_BASE'}").click()
            page.get_by_test_id("chain-share").fill(_number(price["low"]))
        elif shape == "UPFRONT_THEN":
            page.get_by_test_id("chain-upfront").fill(_number(price["upfrontLow"]))
            if price.get("thenNothing"):
                page.get_by_test_id("chain-then-nothing").click()
            else:
                page.get_by_test_id("chain-plan").fill(_number(price["low"]))
        return {"chain": True, "locked": _first_text(page, "[data-testid=chain-locked]")}

    # ------------------------------------------- calibration: a list's Answer, Check and save, Choose

    def list_answer(self, question: dict, text: str | None) -> dict:
        """A list dimension's *Answer* (keel-web 063 FR-004): the founder's words typed and Continue --
        which posts `calibration/{vector}/draft` and opens Check -- or, `text` None, *Leave this out of the
        study* and on past this question. Returns the frame and the prompt drawn."""
        name = question.get("dimension")
        with self._b.step(f"founder answers {name} in their own words" if text else
                          f"founder leaves {name} out of the study") as h:
            self.page.locator("textarea.calib__answerbox").first.wait_for(state="visible", timeout=30_000)
            self._shot(f"answer-{name}")
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

    def edit_rows(self, edits: list[tuple[int, str]], name: str = "list") -> dict:
        """Spec 067 FR-2: the founder's rung typed over Keel's redraft in the same row (the rows are positional), each
        `(row index, label)` into that row's `textarea.listrow__ed`; a row that is not there stops the walk by name."""
        rows = self.page.locator(".listcheck ul.listrows li.listrow textarea.listrow__ed")
        out: dict = {"edited": [], "before": [r.get("text") for r in self._list_rows()["rows"]]}
        with self._b.step(f"founder types {len(edits)} of their own rung{'s' if len(edits) != 1 else ''} over "
                          "Keel's redraft") as h:
            for index, label in edits:
                if index >= rows.count():
                    raise AssertionError(f"the Check screen has no row {index} for the founder's rung {label!r} "
                                         f"(spec 067 FR-2); edited so far: {out['edited']}")
                rows.nth(index).fill(label)
                out["edited"].append({"row": index, "was": out["before"][index] if index < len(out["before"]) else None,
                                      "now": label})
            out["after"] = [r.get("text") for r in self._list_rows()["rows"]]
            h.add_screenshot(self._b.screenshot(f"check-{name}-rungs-edited"))
        return out

    def add_rows(self, labels: list[str], name: str = "list") -> dict:
        """Spec 067 FR-2: the founder's own rungs the draft left out, each typed into a new row (*+ add*, the Check
        screen's `.listcheck__add`). The control gone before every label is typed stops the walk naming the rung."""
        rows = self.page.locator(".listcheck ul.listrows li.listrow textarea.listrow__ed")
        out: dict = {"added": [], "before": [r.get("text") for r in self._list_rows()["rows"]]}
        with self._b.step(f"founder types {len(labels)} of their own rung{'s' if len(labels) != 1 else ''} the draft "
                          "left out") as h:
            for label in labels:
                add = self.page.locator(".listcheck__add")
                if not add.count():
                    raise AssertionError(f"the Check screen offers no row for the founder's rung {label!r} "
                                         f"(spec 067 FR-2); typed so far: {out['added']}")
                before = rows.count()
                add.first.click()
                self.page.wait_for_function("(n) => document.querySelectorAll("
                                            "'.listcheck ul.listrows li.listrow textarea.listrow__ed').length > n",
                                            arg=before, timeout=10_000)
                rows.nth(rows.count() - 1).fill(label)
                out["added"].append(label)
            out["after"] = [r.get("text") for r in self._list_rows()["rows"]]
            h.add_screenshot(self._b.screenshot(f"check-{name}-rungs-typed"))
        return out

    def list_check(self, question: dict, *, timeout_s: float = 60, add: list[str] | None = None,
                   one_more: bool = False, add_rungs=None) -> dict:
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
            self._shot(f"check-{name}")
            seen = {"screen": "check", "frame": self.frame(), **self._list_rows(), "test": self._keel_test()}
            h.capture_text("stage_screen", _text(self.page))
            h.add_screenshot(self._b.screenshot(f"check-{name}"))
        if add is not None:
            seen["importance"] = self.importance_rows(add, one_more=one_more)
            seen["after"] = self._list_rows()
            seen["test_after"] = self._keel_test()
        if add_rungs is not None:
            # spec 067 FR-2: `add_rungs(seen)` -> the plan (rows to edit over, rungs to add), or raises naming the
            # rungs the screen cannot hold
            plan = add_rungs(seen) or {}
            if plan.get("edit"):
                seen["rungs_edited"] = self.edit_rows(plan["edit"], name=name)
            if plan.get("add"):
                seen["rungs"] = self.add_rows(plan["add"], name=name)
            if plan.get("edit") or plan.get("add"):
                seen["after"] = self._list_rows()
                seen["test_after"] = self._keel_test()
        seen["smaller_step_removed"] = self._remove_over_cap_smaller_step(name)
        seen["rows_cut_to_fit"] = self._cut_over_cap_rows(name)
        with self._b.step(f"founder saves {name}") as h:
            seen["primary"] = self._press_primary()
            h.add_screenshot(self._b.screenshot(f"check-{name}-saved"))
            return seen

    def _cut_over_cap_rows(self, name: str) -> list[dict]:
        """A Check screen whose drafted row is over its word cap keeps *Save* disabled (09-karsa, 2026-10-24: Keel drafted
        the Compatibility condition *"They would have a bank account or wallet in their name"*, 11 / 9 words). A founder
        would cut it; this cuts each over-cap row to its first nine words, named as a step so the judge sees Keel's
        draft (a product fault, keel-cloud 130 FR-5). Nothing is touched when the primary is enabled."""
        rows = self.page.locator(".listcheck ul.listrows li.listrow")
        over = [i for i in range(rows.count()) if rows.nth(i).locator(".listrow__wc--over").count()]
        if not over or not self._primary().is_disabled():
            return []
        out = []
        with self._b.step(f"founder cuts {len(over)} of Keel's drafted rows over the word cap on {name}") as h:
            for i in over:
                box = rows.nth(i).locator("textarea.listrow__ed").first
                was = _value(box)
                now = " ".join(str(was or "").split()[:9])
                box.fill(now)
                out.append({"row": i, "was": was, "now": now})
            self.page.wait_for_function("() => !document.querySelector('.listcheck ul.listrows .listrow__wc--over')",
                                        timeout=10_000)
            h.add_screenshot(self._b.screenshot(f"check-{name}-rows-cut"))
        return out

    def _remove_over_cap_smaller_step(self, name: str) -> str | None:
        """Commitment's Check screen (keel-web 098 FR-4): Keel's drafted smaller step over the 9-word cap keeps *Save*
        disabled (10-palus, 2026-10-23: *"Yes, after a look at how it works with no money moved first"*, 10 / 9 words).
        A founder would strike a step they never gave: this presses its × and names the step, so the walk goes on and
        the judge sees it. Nothing is pressed when the primary is enabled or no smaller step is over the cap."""
        smaller = self.page.locator(".listcheck__smaller")
        if not smaller.count():
            return None
        over = smaller.locator(".listrow__wc--over")
        if not over.count() or not self._primary().is_disabled():
            return None
        label = _value(smaller.locator("textarea").first)
        with self._b.step(f"founder removes Keel's smaller step over the word cap on {name}: {label!r}") as h:
            smaller.get_by_test_id("commitment-smaller-step-remove").click()
            self.page.wait_for_function("() => !document.querySelector('.listcheck__smaller .listrow__wc--over')",
                                        timeout=10_000)
            h.add_screenshot(self._b.screenshot(f"check-{name}-smaller-step-removed"))
        return label

    def list_choose(self, question: dict, label: str) -> dict:
        """*Choose* (FR-006): none pre-picked; the radio named `label` picked; the *Keel will test* box
        read with the pick; the primary (*Continue*, or the stage's exit). Returns what it read."""
        name = question.get("dimension")
        with self._b.step(f"founder picks the one item strangers are asked about: {label!r} ({name})") as h:
            _wait_url(self.page, r"/choose")
            group = self.page.locator(".listcheck [role=radiogroup]").first
            group.wait_for(state="visible", timeout=20_000)
            self._shot(f"choose-{name}")
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
            pass_teaching_sheet(self.page, self._b.recorder, self.base, "opener", "COMMERCIAL")
            self._shot("persona")
            if decider["kind"] == "SAME_PERSON":
                group.get_by_role("radio", name=PERSONA_SAME, exact=True).click()
            else:
                group.get_by_role("radio", name=PERSONA_SOMEONE_ELSE, exact=True).click()
                self.page.get_by_label(PERSONA_ROLE, exact=True).fill(decider["role"])
                title = self.page.get_by_label(PERSONA_TITLE)  # the label carries a hint span (One to five words.), so no exact match
                if title.count():
                    # spec 064 FR-6 (keel-web 099): one to five words; the entry's own, else the role word
                    title.fill(decider.get("title") or decider["role"])
            _button(self.page, CONTINUE).click()
            self.page.get_by_text(KICKER_CONTEXT).first.wait_for(state="visible", timeout=20_000)
            text = _text(self.page)
            h.add_screenshot(self._b.screenshot("persona-set"))
            self._shot("persona-who-answers")
            _button(self.page, CONTINUE).click()
            _wait_url(self.page, r"/define/commercial/q/1")
            return {"text": text}

    # ------------------------------------------------------------------- step 5: before people

    def word_pilot_and_lock(self, face: str | None = None, *, pilot: bool = True) -> dict:
        """Step 5 since keel-web 113 FR-2 (spec 073 FR-2): *A word from you* is hidden (`READY_WORD_SCREEN` off), so the
        step starts on its first visible screen -- *The pilot* (1 of 2), then L1 *Who asks the questions* (2 of 2): the
        carousel of faces on Keel's door (`face` tapped when given), one line on an account on its own AI -- and in the
        problem study (`pilot=False`, keel-web 109 FR-3) *Who asks the questions* alone, no counter. The word's own
        address is opened once and answers with that first screen (`ReadyRoute`'s redirect). Then *Lock and record the
        interviewer* / *Lock and approve*. Returns the counters, the landing and the redirect, what L1 drew and the
        lock's receipt as keel-web received it (`LockReceipt`). The method keeps its name (its callers and stubs)."""
        with self._b.step("founder walks the last step from its first screen (no word), picks who asks, then locks") as h:
            first_screen = r"/define/ready/pilot" if pilot else r"/define/ready/interviewer"
            _wait_url(self.page, first_screen)
            landed = self.page.url
            # keel-web 113 FR-2: the word's address answers with the step's first visible screen
            self.page.goto(re.sub(r"/define/ready/[^/?#]+", "/define/ready/word", landed), wait_until="load")
            _wait_url(self.page, first_screen)
            ready: dict = {"landed": landed, "word_redirect": self.page.url}
            counter = self.page.get_by_test_id("before-counter")
            l1: dict = {}
            if not pilot:
                # spec 071 / keel-web 113 FR-2: the problem study asks no pilot question and draws no counter (no *1 of 1*)
                self._shot("ready-interviewer")
                l1 = self.l1(face)
                counters = [(c.text_content() or "").strip() for c in counter.all()]
            else:
                counter.wait_for(state="visible", timeout=20_000)
                self.page.locator("[data-testid=before-counter]", has_text="1 of 2").wait_for(timeout=10_000)
                first = (counter.text_content() or "").strip()
                h.add_screenshot(self._b.screenshot("pilot"))
                self._shot("ready-pilot")
                _button(self.page, BEFORE_CONTINUE).click()
                _wait_url(self.page, r"/define/ready/interviewer")
                self.page.locator("[data-testid=before-counter]", has_text="2 of 2").wait_for(timeout=10_000)
                counters = [first, (counter.text_content() or "").strip()]
                self._shot("ready-interviewer")
                l1 = self.l1(face)
            ready["word_drawn"] = self.page.get_by_text("A word from you", exact=False).count()
            button = self.page.get_by_test_id("lock-and-record")
            try:
                self.page.wait_for_function("(b) => !b.disabled", arg=button.element_handle(), timeout=15_000)
            except Exception:  # noqa: BLE001 - spec 072 FR-1: a lock the page never offers (runs/DRIFT.md #95, closed)
                # the leg fails on it, the plan as served named; nothing is clicked and nothing locks on the wire
                h.add_screenshot(self._b.screenshot("lock-disabled"))
                return {"counters": counters, "receipt": {}, "l1": l1, "status": None, "disabled": True,
                        "button": _safe_text(lambda: button.inner_text()), "ready": ready}
            with self.page.expect_response(lambda r: r.request.method == "POST" and r.url.endswith("/lock"),
                                           timeout=30_000) as locked:
                button.click()
            try:
                receipt = locked.value.json()
            except Exception:  # noqa: BLE001 - a refused lock's body is the leg's to report
                receipt = {"status": locked.value.status, "text": _safe_text(lambda: locked.value.text())}
            l1["sent"] = locked.value.request.post_data_json
            status = locked.value.status
            if status >= 400:
                # spec 070 FR-1 (keel-cloud 131 FR-5): a refused lock (422 TEXT_REFUSED on an M5 word the repair turn did
                # not move) leaves the screen where it is; the leg reads the body and edits the idea card
                h.add_screenshot(self._b.screenshot("lock-refused"))
                return {"counters": counters, "receipt": receipt, "l1": l1, "status": status, "ready": ready}
            _wait_url(self.page, r"/interviews/sent|/people", timeout_s=60)       # keel-web 068: Sent
            h.add_screenshot(self._b.screenshot("locked-people"))
            return {"counters": counters, "receipt": receipt, "l1": l1, "status": status, "ready": ready}

    #: Spec 070 FR-1: the idea card's boxes on the Check screen (keel-web `IdeaCheck`: `idea-{line}`).
    IDEA_BOXES = {"how": "#idea-how", "howDecider": "#idea-howDecider", "belief": "#idea-belief"}

    def edit_idea_lines(self, project_id: str, edits: dict) -> dict:
        """Spec 070 FR-1 (keel-cloud 131 FR-5): after a refused lock, the founder opens the idea's Check screen
        (`define/solution/idea`), types each line's new words into its box (`edits`: {how | howDecider | belief: words};
        a box the screen does not draw is skipped and named) and presses Save -- the edit and the approval keel-web's
        `IdeaCheck` sends -- and the page moves on to the solution's first question. Returns the lines as drawn before
        the edit, what was typed, the boxes not drawn and the primary's label."""
        with self._b.step(f"founder edits the idea card's {', '.join(edits)} line after the lock was refused") as h:
            self.page.goto(f"{self.base}/p/{project_id}/define/solution/idea", wait_until="load")
            self.page.locator("#idea-how").wait_for(state="visible", timeout=20_000)
            self.page.wait_for_function("() => (document.querySelector('#idea-how')?.value || '') !== ''",
                                        timeout=20_000)
            before = {line: _value(self.page.locator(box)) if self.page.locator(box).count() else None
                      for line, box in self.IDEA_BOXES.items()}
            typed, absent = {}, []
            for line, words in edits.items():
                box = self.page.locator(self.IDEA_BOXES[line])
                if not box.count():
                    absent.append(line)
                    continue
                box.fill(words)
                typed[line] = words
            h.capture_text("stage_screen", _text(self.page))
            h.add_screenshot(self._b.screenshot("idea-edited"))
            label = self._press_primary(SAVE)
            _wait_url(self.page, r"/define/solution/q/\d+$")
            return {"before": before, "typed": typed, "absent": absent, "primary": label}

    def relock(self, project_id: str) -> dict:
        """Spec 070 FR-1: the lock pressed again, on L1 (`define/ready/interviewer`, the screen it was refused on), after
        the idea card's edit. Returns the status and the receipt (or the refusal's body), waiting for *Sent* on a 2xx."""
        with self._b.step("founder locks again after editing the idea card") as h:
            self.page.goto(f"{self.base}/p/{project_id}/define/ready/interviewer", wait_until="load")
            button = self.page.get_by_test_id("lock-and-record")
            button.wait_for(state="visible", timeout=20_000)
            self.page.wait_for_function("(b) => !b.disabled", arg=button.element_handle(), timeout=30_000)
            with self.page.expect_response(lambda r: r.request.method == "POST" and r.url.endswith("/lock"),
                                           timeout=30_000) as locked:
                button.click()
            try:
                receipt = locked.value.json()
            except Exception:  # noqa: BLE001 - a refused lock's body is the leg's to report
                receipt = {"status": locked.value.status, "text": _safe_text(lambda: locked.value.text())}
            status = locked.value.status
            if status < 400:
                _wait_url(self.page, r"/interviews/sent|/people", timeout_s=60)
                h.add_screenshot(self._b.screenshot("locked-people"))
            else:
                h.add_screenshot(self._b.screenshot("lock-refused-again"))
            return {"status": status, "receipt": receipt, "sent": locked.value.request.post_data_json}

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

#: Spec 075 (keel-web 124 FR-1's latency rule): how long the walk holds a `late` item's follow-up call -- past the
#: beat the page waits for it (`BEAT_MS`, 2 s), so the page goes on and the rung stays owed for the end.
LATE_FOLLOW_UP_S = 3.5


class Interview:
    """The stranger's `/i/{token}` (keel-web 064): one screen at a time, every word as served. `walk`
    takes the interview as the wire served it (to read the labels of the option ids a pick names) and
    the person's answers; it records what each screen drew (`screens`) for the scenario to judge."""

    def __init__(self, page: Page, recorder: Recorder):
        self.page = page
        self._b = _BrowserStep(recorder, page, "participant")
        self.seen: list[str] = []
        self.screens: list[dict] = []
        self.unanswered: list[dict] = []
        self.closed_price: list[dict] = []   # keel-web 106 FR-9: up-front-then prices closed on the first screen
        self.retried: list[dict] = []
        #: Spec 062 FR-3: the back-test's camera for this person's screens (one person a link), or None.
        self.camera = None

    def _shot(self, slug: str) -> None:
        if self.camera is not None:
            self.camera(slug)

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
            self._shot("intro")

    def walk(self, person, interview: dict, wire_answers: dict, *, follow_up: str | None = None,
             speak: str | None = None, follow_up_rung: str | None = None,
             lines: Callable[[str], str | None] | None = None, late=()) -> dict:
        """Begin, the decision-maker's idea screen, the gate, every item and the reveal, *Send my
        answers*; returns the body the page POSTed, the done screen's heading and what every screen drew.
        `wire_answers` is `{itemId: ItemAnswer}` -- what this person answers, already re-expressed as the
        wire takes it.

        Spec 051 (keel-web 076, keel-cloud 103), as spec 075 has it (keel-web 124, keel-cloud 142): *Next* on an item
        whose dimension is a rung the link walks posts the answers so far, with `asked`, to `POST .../interview/
        follow-up` (never after a gate No; no call once two were asked); a rung on that item opens its follow-up right
        then, any other goes on. *Send my answers* posts once more (not raced): a rung on the last item is
        asked on the spot, any other at the end -- every one under *One more thing* (keel-web 126) -- and after a follow-up on the last item the end is
        asked once more while fewer than two were. On each follow-up `lines(rung)` is typed and *Continue* pressed --
        None presses *Skip this one* (not sent, still asked). `follow_up` / `follow_up_rung` are the one-line form: the
        line typed on its rung (any rung, when none is named). Every route call is kept (`follow_up_routes`, in order)
        and every follow-up screen (`follow_ups`). `late` (spec 075): the items whose *Next* call is held past the beat
        (`LATE_FOLLOW_UP_S`) -- the page goes on, and the rung is the end's to ask. `speak` drives the story's box (`SpeakOrTypeBox`, through `text_seam`): "quiet" or "done" -- the story
        typed, then *Speak*, a sound, and the take ended by the 4 s quiet or by *Done* (T1 -> T4); "refused" -- *Speak*
        on a refused microphone (T6), then typed. What the route answered, the screen drew and the box did is kept."""
        page = self.page
        self.route: dict = {}
        self.follow_up_seen: dict | None = None
        self.follow_ups_seen: list[dict] = []
        if lines is None:
            def lines(rung: str, _line=follow_up, _for=follow_up_rung) -> str | None:   # noqa: E306
                return _line if _line and (_for is None or rung == _for) else None
        self._lines = lines
        self._line_for = follow_up_rung
        self.speak_seen: dict | None = None
        self._transcribe_responses: list = []
        self._route_responses: list = []
        self._responded = False
        self._late_items = set(late or ())
        self._hold_next = False
        if self._late_items:
            page.route("**/interview/follow-up", self._held_route)
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
                inside = True
                if interview.get("kind") == "COMMERCIAL_LINK" and interview.get("condition"):
                    # spec 076 FR-4 (keel-cloud 145 FR-4b, keel-web 127 FR-2): the decision-maker's screener, its own
                    # screen before the idea; outside, Continue sends `outsideSegment` alone and lands on the exit
                    inside = self._condition(person, interview["condition"])
                if inside and interview.get("kind") == "COMMERCIAL_LINK" and interview.get("idea"):
                    self._idea()
                gate = interview.get("gate")
                if gate:
                    self._gate(person, gate, interview.get("occasion"), speak=speak)
                # spec 076 FR-5 (keel-web 127 FR-3): a story chip ends the interview at the gate, as a No does
                if inside and (gate is None or (person.recency and getattr(person, "in_segment", True)
                                                and not getattr(person, "anchor_chip", None))):
                    self._items(interview, wire_answers)
                    self._end_follow_ups(interview)
            body = answered.value.request.post_data_json
            status = answered.value.status
            page.get_by_role("heading", level=1).first.wait_for(state="visible", timeout=20_000)
            self._keep()
            heading = _safe_text(lambda: page.get_by_role("heading", level=1).first.inner_text())
            # spec 071 (keel-cloud 133 FR-4, keel-web 109 call 11): the thank-you's pilot box, drawn or not
            pilot_box = page.locator("input[type=checkbox], [role=checkbox]").count()
            # spec 073 FR-2 (keel-web 113 FR-2): no founder's word -- the done screen's word section, drawn or not
            word_drawn = page.locator(".iv-done__word").count()
            # the thank-you, or the gate's exit (`ExitScreen`: *That's it.*, the same `.iv-done` box) -- a No, or outside
            done_screen = page.locator("main.iv-body .iv-done").count() > 0 and heading.strip() != INTERVIEW_DONE_TITLE
            h.add_screenshot(self._b.screenshot(f"interview-done-{person.person.split()[0]}"))
            self._shot("done")
            if self.speak_seen and self.speak_seen.get("how") in ("quiet", "done"):
                # spec 075 FR-5 (keel-web 126 FR-4): the boxes kept the microphone; the page lets it go on done
                self.speak_seen["released_at_done"] = self._released_on_done()
            page.remove_listener("response", self._keep_transcribe)
            return {"body": body, "status": status, "done": heading, "pilot_box": pilot_box, "word_drawn": word_drawn,
                    "done_screen": done_screen,
                    "seen": list(self.seen),
                    "screens": list(self.screens), "unanswered": list(self.unanswered), "closed_price": list(self.closed_price), "retried": list(self.retried), "follow_up_route": self.route, "follow_up": self.follow_up_seen,
                    "follow_up_routes": self._routes(), "follow_ups": list(self.follow_ups_seen),
                    "late": sorted(self._late_items),
                    "speak": self.speak_seen, "transcribed": self._transcribed(), "consent": self.consent}

    def _released_on_done(self, *, timeout_s: float = 5) -> int:
        """The seam's count of the microphone's releases once the done screen shows (the page's effect runs after the
        render): waited for to move past the take's, or read as it stands at the timeout."""
        box = ivs.SpeakBox(self.page, "main")
        before = ((self.speak_seen or {}).get("counts") or {}).get("released") or 0
        end = time.monotonic() + timeout_s
        released = box.counts().get("released") or 0
        while released <= before and time.monotonic() < end:
            self.page.wait_for_timeout(100)
            released = box.counts().get("released") or 0
        return released

    def _keep_transcribe(self, response) -> None:
        """Every `transcribe` the page sent (the box's recorded take), every follow-up route call (spec 075) and the
        response's own POST: kept as the response, read after (a body read inside an event handler would wait on the
        handler itself)."""
        if response.request.method != "POST":
            return
        url = response.url.split("?")[0]
        if url.endswith("/interview/transcribe"):
            self._transcribe_responses.append(response)
        elif url.endswith("/interview/follow-up"):
            self._route_responses.append(response)
        elif url.endswith("/interview/response"):
            self._responded = True

    def _held_route(self, route) -> None:
        """Spec 075: the one call after a `late` item, held past keel-web's beat before it goes; every other as it is."""
        if self._hold_next:
            self._hold_next = False
            time.sleep(LATE_FOLLOW_UP_S)
        route.continue_()

    def _routes(self) -> list[dict]:
        """Spec 075: every follow-up route call, in order -- what was sent (`answers`, `asked`), the status, the body."""
        return [self._route(r) for r in self._route_responses]

    @staticmethod
    def _route(response) -> dict:
        return {"status": response.status, "body": _json_body(response) if response.status == 200 else {},
                "sent": response.request.post_data_json}

    def _transcribed(self) -> list[dict]:
        out = []
        for response in self._transcribe_responses:
            body = response.request.post_data_json or {}
            got = _json_body(response)
            out.append({"itemId": body.get("itemId"), "maxSeconds": body.get("maxSeconds"),
                        "mimeType": body.get("mimeType"), "language": body.get("language"),
                        "status": response.status, "text": got.get("text")})
        return out

    def _follow_up_screen(self, on: str | None) -> dict:
        """Spec 075 (keel-web 124 FR-1..FR-3; 076 FR-3): one follow-up screen, as drawn -- the kicker (*One more thing*
        on the spot and at the end, keel-web 126 FR-5), the cloud's question as `h1.iv-q`, the note, the box and its hint (*The
        only extra question.* only on the end's with none asked before it), *Continue* off while empty, *Skip this one*
        -- then `lines(rung)` typed and *Continue*, or (no line) *Skip this one*. `on` is the item it was asked right
        after (None at the end); the rung is the last route call's that answered 200."""
        page = self.page
        screen = page.get_by_test_id("iv-follow-up")
        screen.wait_for(state="visible", timeout=20_000)
        self._keep()
        self._shot(f"follow-up-{len(self.follow_ups_seen) + 1}")
        box = ivs.SpeakBox(page, "[data-testid=iv-follow-up]")
        cont = _button(page, IV_CONTINUE)
        asked = next((self._route(r) for r in reversed(self._route_responses) if r.status == 200), {})
        route = asked.get("body") or {}
        self.route = asked
        drawn = {"on": on, "kicker": _first_text(screen, ".iv-kicker"), "question": _first_text(screen, "h1.iv-q"),
                 "note": _first_text(screen, ".iv-note"), "box": box.read(),
                 "continue_enabled_empty": cont.is_enabled(),
                 "skip": _tc(screen.get_by_test_id("iv-follow-up-skip")),
                 "textarea_label": screen.locator("textarea").first.get_attribute("aria-label"),
                 # keel-web 124: *The only extra question.* only on the end's follow-up with none asked before it
                 "only": ivs.FOLLOW_UP_HINT in _tc(screen),
                 "rung": route.get("dimension"), "route": asked}
        self.screens.append({"screen": "follow_up", **{k: drawn[k] for k in ("on", "kicker", "question", "note")}})
        served_rung = route.get("dimension")
        line = self._lines(served_rung) if served_rung else None
        # a person's line was written for one rung (the entry's own words on the harness's owed question); when the
        # route asked another rung, the line would answer a question it was not written for -- skipped instead, and
        # the record says so (the judges of 18-careforce found Commitment answers filed under Purchase friction)
        if self._line_for and served_rung and served_rung != self._line_for:
            drawn["line_for"] = self._line_for
            line = None
        if line:
            screen.locator("textarea").first.fill(line)
            drawn["continue_enabled_typed"] = cont.is_enabled()
            drawn["did"] = "typed"
            drawn["typed"] = line
            cont.click()
        else:
            drawn["did"] = "skipped"
            screen.get_by_test_id("iv-follow-up-skip").click()
        self.follow_ups_seen.append(drawn)
        self.follow_up_seen = drawn
        return drawn

    def _after_follow_up(self, drawn: dict, *, timeout_s: float = 20) -> None:
        """Spec 075: the page off the follow-up screen it just answered -- another screen, another question, or the
        response sent."""
        page = self.page
        end = time.monotonic() + timeout_s
        while time.monotonic() < end:
            if self._responded or page.get_by_test_id("iv-follow-up").count() == 0:
                return
            if _first_text(page, "[data-testid=iv-follow-up] h1.iv-q") != drawn.get("question") \
                    or _first_text(page, "[data-testid=iv-follow-up] .iv-kicker") != drawn.get("kicker"):
                return
            page.wait_for_timeout(100)
        raise AssertionError(json.dumps({"stayed on the follow-up": drawn.get("question"), "url": page.url}))

    def _end_follow_ups(self, interview: dict, *, timeout_s: float = 30) -> None:
        """Spec 075 (keel-web 124 FR-1 / FR-2): after *Send my answers* -- every follow-up the page opens (a rung on the
        last item on the spot, then the end's), each answered, until the response goes."""
        page = self.page
        for _ in range(ivs.MAX_FOLLOW_UPS + 1):
            end = time.monotonic() + timeout_s
            while time.monotonic() < end and not self._responded and not page.get_by_test_id("iv-follow-up").count():
                page.wait_for_timeout(100)
            if self._responded or not page.get_by_test_id("iv-follow-up").count():
                return
            last = self._last_item_dimension(interview)
            # spec 075 FR-5 (keel-web 126 FR-5): one kicker now, so the screen asked on the spot is told from the end's
            # by its rung -- the last item's own (a rung is asked once, so the end's is another)
            asked = next((self._route(r) for r in reversed(self._route_responses) if r.status == 200), {})
            rung = (asked.get("body") or {}).get("dimension")
            drawn = self._follow_up_screen(last if rung is not None and rung == last else None)
            self._after_follow_up(drawn)

    @staticmethod
    def _last_item_dimension(interview: dict) -> str | None:
        items = [i for part in interview.get("parts") or [] for i in part.get("items") or []]
        return items[-1].get("dimension") if items else None

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
        """D9 (keel-web 064 FR-007): the decision-maker's link opens with the idea's three lines -- and, since keel-web 109
        FR-5 (keel-cloud 133 FR-6, `Idea.problem`), the problem in one sentence above the card (`reveal-problem`)."""
        page = self.page
        _button(page, IV_CONTINUE).wait_for(state="visible", timeout=20_000)
        self._keep()
        self._shot("idea")
        problem = page.locator("main.iv-body [data-testid=reveal-problem]")
        self.screens.append({"screen": "idea", "kicker": _first_text(page, ".iv-kicker"),
                             "card": _first_text(page, ".iv-card"),
                             "question": _first_text(page, "h1.iv-q"),
                             "problem": _tc(problem) if problem.count() else None})
        _button(page, IV_CONTINUE).click()

    def _condition(self, person, condition: dict) -> bool:
        """Spec 076 FR-4 (keel-web 127 FR-2, keel-cloud 145 FR-4b): the decision-maker's screener, the link's first
        screen after Begin (`[data-testid=condition-screen]`): the served question as the screen's `h1.iv-q`, Yes / No as
        a radiogroup named by it, *Continue* off until one is picked, no kicker (none is served) -- answered inside for a
        person in the people the founder described, else the other answer; then *Continue*. True when inside (the walk
        goes on to the idea); what the screen drew is kept."""
        page = self.page
        screen = page.get_by_test_id("condition-screen").first
        screen.wait_for(state="visible", timeout=20_000)
        self._keep()
        self._shot("condition")
        inside_codes = list(condition.get("inCodes") or [])
        in_segment = getattr(person, "in_segment", True)
        code = inside_codes[0] if in_segment else next(c for c in ("YES", "NO") if c not in inside_codes)
        cont = _button(page, IV_CONTINUE)
        drawn = {"screen": "condition", "question": _first_text(screen, "h1.iv-q"),
                 "kicker": _first_text(screen, ".iv-kicker") or None,
                 "options": _safe_all_texts(screen, "[role=radio]"), "continue_before": cont.is_enabled(),
                 "back": page.get_by_role("button", name="Back", exact=True).count(), "answered": code,
                 "outside": not in_segment}
        page.get_by_role("radiogroup", name=condition.get("question"), exact=True).get_by_role(
            "radio", name=IV_CHIP_WORD[code], exact=True).click()
        drawn["continue_after"] = cont.is_enabled()
        self.screens.append(drawn)
        cont.click()
        return in_segment

    def _gate(self, person, gate: dict, occasion: str | None, *, speak: str | None = None) -> None:
        """The gate (keel-web 064; spec 064 FR-4 / 4c, keel-web 096 / 099): the segment chip first where the gate serves
        `condition` (`[data-testid=segment-chip]`, a radiogroup named by its question, Yes / No) -- answered inside
        for a person in the segment, else the other answer, which hides the gate and sends `outsideSegment` on
        Continue; then the gate's Yes / No (the No reads the served `noLabel`), and on a Yes the story, its chip (*I
        can't recall one particular {occasion}*, or *I'd rather not say*) or the box. What the screen drew is kept."""
        page = self.page
        condition = gate.get("condition") or None
        chip_seen = None
        if condition:
            chip = page.get_by_test_id("segment-chip").first
            chip.wait_for(state="visible", timeout=20_000)
            inside = list(condition.get("inCodes") or [])
            code = inside[0] if getattr(person, "in_segment", True) else next(
                c for c in ("YES", "NO") if c not in inside)
            group = page.get_by_role("radiogroup", name=condition.get("question"), exact=True)
            chip_seen = {"question": _first_text(chip, "h2.iv-q"), "answered": code,
                         "options": _safe_all_texts(chip, "[role=radio]")}
            self._keep()
            self._shot("segment-chip")
            group.get_by_role("radio", name=IV_CHIP_WORD[code], exact=True).click()
            if not getattr(person, "in_segment", True):
                self.screens.append({"screen": "gate", "kicker": _first_text(page, ".iv-kicker"), "chip": chip_seen,
                                     "question": None, "chips": [], "outside": True})
                _button(page, IV_CONTINUE).click()
                return
        group = page.get_by_role("radiogroup", name=gate["question"], exact=True)
        group.wait_for(state="visible", timeout=20_000)
        self._keep()
        self._shot("gate")
        no = gate.get("noLabel") or IV_NO
        group.get_by_role("radio", name=IV_YES if person.recency else no, exact=True).click()
        chips = []
        if person.recency:
            chips = _safe_all_texts(page, ".iv-story .iv-chips button")
            if person.anchor_chip == "RATHER_NOT_SAY" and GATE_RATHER_NOT_SAY in [c.strip() for c in chips]:
                _button(page, GATE_RATHER_NOT_SAY).click()
            elif person.anchor_chip:
                _button(page, gate_chip_word(occasion)).click()
            elif person.story and speak:
                self._speak_story(person.story, speak)
            elif person.story:
                page.locator("textarea").first.fill(person.story)
        self.screens.append({"screen": "gate", "kicker": _first_text(page, ".iv-kicker"),
                             "question": _first_text(page, "h1.iv-q"), "chips": chips, "chip": chip_seen,
                             "options": _safe_all_texts(group, "[role=radio]")})
        _button(page, IV_CONTINUE).click()

    def _speak_story(self, story: str, how: str) -> None:
        """Spec 051 FR-5 (keel-web 076 FR-6..FR-8, design §6): the story's box, T1 -> T4 through the seam's recorder --
        idle (nothing asked of the microphone yet), the story typed, *Speak* tapped (the microphone asked for now), the
        listening card (the waveform, the clock, Cancel, Done; Continue off), a sound, then the take ended by the 4 s
        quiet (`how` "quiet") or by *Done* ("done"); *Writing it down…* (the recorder's stop held so it can be read), and
        the transcript appended with the caret at the end, *Heard you.*, the pill *Add more*. "refused": *Speak* on a
        refused microphone -- typing only (T6) -- then the story typed. Spec 075 FR-5 (keel-web 126 FR-4): between the
        tap and T2 the box is *asking* (the seam holds the permission sheet until `grant`); the page's releases are
        read again on the done screen (`released_at_done`, the walk's end)."""
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
        # spec 075 FR-5 (keel-web 126 FR-4): the tap is *asking* while the permission sheet is up -- the seam holds it
        # (`text_seam(held=True)`) -- its line and Cancel, no waveform, no clock, nothing recorded, Continue off; then
        # granted, and *listening* once the recorder runs
        out["asking"] = box.wait_state("asking")
        # read three times across 600 ms, as while listening: Continue goes off through the box's state a render after
        # the card is drawn (`onBoxState`, D-02 of spec 051)
        out["continue_while_asking"] = []
        for _ in range(3):
            out["continue_while_asking"].append({"enabled": cont.is_enabled(), "at": box.now()})
            page.wait_for_timeout(200)
        out["continue_enabled_asking"] = out["continue_while_asking"][-1]["enabled"]
        out["asking"] = box.read()
        out["asking_counts"] = box.counts()
        box.grant()
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
                self._shot(f"part{part.get('part')}-{item.get('dimension')}")
                answer = wire_answers.get(item.get("itemId"))
                stem = _first_text(page, "h1.iv-q") or ""
                if item.get("text") and stem.strip() and stem.strip() != str(item.get("text")).strip():
                    # the page is not on the item the walk is about to answer: name both, instead of a click that
                    # times out on a chip or radio the screen never drew
                    raise AssertionError(json.dumps({"walk_item": item.get("dimension"), "walk_stem": item.get("text"),
                                                     "page_stem": stem, "url": page.url}))
                if answer is not None:
                    self._answer(item, answer)
                elif item.get("escape"):
                    # a back-test person whose file says nothing on an item the link asks (13-aircaps, Naomi Adler on
                    # Ability to pay): the page cannot move on unanswered, so they take the item's escape, and the walk
                    # names it -- the entry's author sees it in the findings rather than the run stopping here
                    self._answer(item, {"chip": str((item.get("escape") or {}).get("code") or "").upper()})
                    self.unanswered.append({"dimension": item.get("dimension"), "took": (item.get("escape") or {}).get("label"),
                                            "code": str((item.get("escape") or {}).get("code") or "").upper(),
                                            "itemId": item.get("itemId")})
                self.screens.append(self._item_screen(item))
                last = p_index == len(parts) - 1 and i_index == len(items) - 1
                if last:
                    # keel-web 076 FR-1, 124 FR-2: the last *Send my answers* posts the answers to the follow-up route
                    # first -- while fewer than two were asked and the link walks rungs; the follow-ups it opens are
                    # `_end_follow_ups`' to answer
                    if (interview.get("followUps") or []) and len(self.follow_ups_seen) < ivs.MAX_FOLLOW_UPS:
                        with page.expect_response(lambda r: r.request.method == "POST"
                                                  and r.url.split("?")[0].endswith("/interview/follow-up"),
                                                  timeout=30_000) as asked:
                            _button(page, IV_SEND).click()
                        self.route = {"status": asked.value.status, "body": _json_body(asked.value)
                                      if asked.value.status == 200 else {},
                                      "sent": asked.value.request.post_data_json}
                    else:
                        _button(page, IV_SEND).click()
                else:
                    before = _first_text(page, "h1.iv-q") or ""
                    self._hold_next = item.get("dimension") in self._late_items
                    _button(page, IV_NEXT).click()
                    moved = self._screen_moved(before)
                    self._hold_next = False
                    if not moved:
                        # the page stayed on the item after Next (13-aircaps, Naomi Adler on Ability to pay: the walk
                        # went one item ahead of the page) -- the answer is put again once, Next pressed again, and the
                        # retry is recorded as a finding; a second stay stops the walk with the page's words
                        taken = answer if answer is not None else {"chip": str((item.get("escape") or {}).get("code") or "").upper()}
                        self.retried.append({"dimension": item.get("dimension"), "stem": before, "answer": taken})
                        self._answer(item, taken)
                        _button(page, IV_NEXT).click()
                        if not self._screen_moved(before):
                            raise AssertionError(json.dumps({
                                "stayed_on": item.get("dimension"), "stem": before, "answer": taken,
                                "chips_drawn": [c.strip() for c in self._main().locator(".iv-chips button").all_inner_texts()],
                                "rows": _safe_all_texts(page, ".iv-control [role=radio], .iv-control [role=checkbox]"),
                                "url": page.url}))
                    if page.get_by_test_id("iv-follow-up").count():
                        # spec 075 (keel-web 124 FR-1): the rung on this item, asked right after it
                        drawn = self._follow_up_screen(item.get("dimension"))
                        self._after_follow_up(drawn)
            if interview.get("kind") == "FULL" and reveal and reveal.get("afterPart") == part.get("part") \
                    and p_index < len(parts) - 1:
                _button(page, IV_CONTINUE).wait_for(state="visible", timeout=20_000)
                self._keep()
                self._shot("reveal")
                self.screens.append({"screen": "reveal", "kicker": _first_text(page, ".iv-kicker"),
                                     "card": _first_text(page, ".iv-card")})
                _button(page, IV_CONTINUE).click()

    def _screen_moved(self, before: str, *, timeout_s: float = 10) -> bool:
        """True once the page draws another question (or the reveal, the follow-up, the done screen) than `before`."""
        page = self.page
        end = time.monotonic() + timeout_s
        while time.monotonic() < end:
            now = _first_text(page, "h1.iv-q") or ""
            if now.strip() != before.strip():
                return True
            if page.locator("h1.iv-q").count() == 0:
                return True
            page.wait_for_timeout(200)
        return False

    def _item_screen(self, item: dict) -> dict:
        """What one item's screen drew, in the order drawn: the kicker, the idea card, the stem, the hint,
        the control's rows, the escape chips (and whether the escape is the last control before the
        buttons). Spec 064 FR-4c (keel-web 096): a question opening with the occasion's anchor sentence is drawn as
        `p.iv-stem[data-testid=item-stem]` before `h1.iv-q`, which then holds the rest -- `question` is the two joined
        (what the wire served) and `stem` / `asked` are kept apart. FR-3 (keel-web 094): the value box's label after the
        box, *What you'd get*, and an up-front-then price's plan screen (`plan`, recorded by `_answer`)."""
        page = self.page
        main = self._main()
        rows = _safe_all_texts(page, ".iv-control [role=radio], .iv-control [role=checkbox]")
        chips = _safe_all_texts(page, ".iv-chips button")
        order = main.evaluate(
            "(m) => Array.from(m.children).map((c) => c.className || c.tagName)") if main.count() else []
        stem = _first_text(page, "[data-testid=item-stem]")
        asked = _first_text(page, "h1.iv-q")
        out = {"screen": "item", "dimension": item.get("dimension"), "control": item.get("control"),
               "kicker": _first_text(page, ".iv-kicker"), "question": f"{stem} {asked}" if stem else asked,
               "stem": stem or None, "asked": asked,
               "idea_card": _first_text(page, ".iv-ideacard__what"),
               "hint": _first_text(page, ".iv-tick"), "picked_line": _first_text(page, ".iv-picked"),
               "rows": [r.strip() for r in rows], "chips": [c.strip() for c in chips], "order": order}
        if item.get("control") == "value_box":
            out["value_box_label"] = _first_text(page, "[data-testid=value-box-label]")
        if item.get("whatYouGet"):
            out["what_you_get"] = _first_text(page, "[data-testid=what-you-get]")
        if self._plan_seen is not None:
            out["plan"], self._plan_seen = self._plan_seen, None
        return out

    #: The plan screen an up-front-then price drew (spec 064 FR-3), read by `_item_screen` once.
    _plan_seen: dict | None = None
    #: Items the person's file left unanswered and the walk escaped (a back-test finding), `[{dimension, took}]`.
    unanswered: list

    def _answer(self, item: dict, answer: dict) -> None:
        main = self._main()
        options = {o.get("optionId"): o.get("label") for o in item.get("options") or []}
        plan = item.get("plan") or {}
        options.update({o.get("optionId"): o.get("label") for o in plan.get("options") or []})
        advantages = {a.get("id"): a.get("label") for a in item.get("advantages") or []}
        if answer.get("chip"):
            # an item's one escape, or (keel-web 094) the value box's chips -- *Nothing*, *I don't know*, *I'd rather
            # not say* -- each by its served label
            box = item.get("valueBox") or {}
            served = [item.get("escape") or {}, box.get("nothing") or {}] + list(box.get("chips") or [])
            label = next((e.get("label") for e in served if str(e.get("code") or e.get("chip") or "").upper()
                          == answer["chip"]), (item.get("escape") or {}).get("label"))
            chip = main.locator(".iv-chips").get_by_role("button", name=label, exact=True).first
            if chip.count() == 0:
                # the screen does not draw the chip the served item names (13-aircaps, Naomi Adler): say what it does
                # draw, so the stop can be read without a rerun
                drawn = [c.strip() for c in main.locator(".iv-chips button").all_inner_texts()]
                raise AssertionError(json.dumps({"item": item.get("dimension"), "chip": answer["chip"], "wanted": label,
                                                 "stem": _first_text(self.page, "h1.iv-q"), "chips_drawn": drawn,
                                                 "url": self.page.url}))
            chip.click()
            if plan:
                # keel-web 106 FR-9 (keel-cloud 128 FR-21): a closed price (its escape) shows no plan screen -- the loop's
                # Next goes to the next item; recorded so the judge sees the plan was never drawn (before 106, keel-web
                # 094 FR-4 still opened the plan's own screen: 13-aircaps, Naomi Adler)
                self._plan_seen = {"question": plan.get("question"), "skipped": True, "escaped": True}
                self.closed_price.append({"itemId": item.get("itemId"), "dimension": item.get("dimension"), "chip": answer["chip"]})
            return
        if "scale" in answer:
            main.get_by_role("radio", name=str(answer["scale"]), exact=True).click()
            return
        if "interval" in answer:
            # keel-web 094 FR-3: *Between* [box] *and* [box] in the founder's own unit and period
            interval = answer["interval"]
            main.get_by_test_id("value-box-low").fill(_number(interval["low"]))
            main.get_by_test_id("value-box-high").fill(_number(interval.get("high", interval["low"])))
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
        ids = list(answer.get("optionIds") or [])
        if plan and len(ids) == 2 and _is_would_not_pay(options.get(ids[0])):
            # keel-web 106 FR-9 (keel-cloud 128 FR-21): "I wouldn't pay for this" closes the price item -- one option is
            # sent, the plan screen is not drawn, and the file's second pick is dropped and named (21-codyco, Hannes Moser)
            main.locator(".iv-control").get_by_role(role, name=options[ids[0]], exact=True).first.click()
            self._plan_seen = {"question": plan.get("question"), "skipped": True, "would_not_pay": True}
            self.closed_price.append({"itemId": item.get("itemId"), "dimension": item.get("dimension"),
                                      "optionId": ids[0], "dropped": ids[1]})
            return
        if plan and len(ids) == 2:
            # keel-web 094 FR-4: up front, then a plan -- the thing's band, Next, then the plan's own screen
            main.locator(".iv-control").get_by_role(role, name=options[ids[0]], exact=True).first.click()
            _button(self.page, IV_NEXT).click()
            self.page.locator("h1.iv-q", has_text=plan.get("question") or "").first.wait_for(
                state="visible", timeout=20_000)
            self._keep()
            self._shot(f"plan-{item.get('dimension')}")
            self._plan_seen = {"question": _first_text(self.page, "h1.iv-q"),
                               "rows": [r.strip() for r in _safe_all_texts(self.page, ".iv-control [role=radio]")]}
            ids = ids[1:]
        for option_id in ids:
            main.locator(".iv-control").get_by_role(role, name=options[option_id], exact=True).first.click()
        for advantage_id in answer.get("advantageIds") or []:
            main.get_by_role("checkbox", name=advantages[advantage_id], exact=True).click()


def _is_would_not_pay(label: str | None) -> bool:
    """keel-web 106 FR-9 reads the up-front ladder's refusal by its words, as the wire gives it no code."""
    return " ".join(str(label or "").lower().split()).rstrip(".") in ("i wouldn't pay for this", "i would not pay for this")


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
        pass_teaching_sheet(self.page, self._b.recorder, self.base, "report")
        views = self.page.get_by_test_id("report-views").first
        views.wait_for(state="visible", timeout=30_000)
        tab = views.locator(f"button[role='tab'][data-view='{view}']").first
        if tab.get_attribute("aria-selected") != "true":
            tab.click()
        self.page.locator(f"button[role='tab'][data-view='{view}'][aria-selected='true']").first.wait_for(
            state="visible", timeout=10_000)
        self.page.locator("#report-view[role='tabpanel']").first.wait_for(state="visible", timeout=10_000)

    def scoped_overview(self, project_id: str) -> dict:
        """Spec 071 (keel-web 109 FR-4, keel-cloud 133 FR-7 / FR-8 / FR-5): the Overview of a study of one scope, as
        drawn -- the served question (`.rp-q`), the verdict (`h1.rp-verdict[data-label]`), the stages' row and its
        class (`.rp-stages--one|--two`), each panel's stage (`report-stage-{STAGE}`), the tiles (`report-tiles`, its
        `--one`, each `[data-tile]`), the uncounted gate's fact line (`report-gatefact`), the linked ship's pieces
        (`svg.rp-ship--linked path.band[data-stage]`) and the report's tabs (`report-views [role=tab][data-view]`)."""
        with self._b.step("founder opens the report's overview (a study of one scope)") as h:
            self._report(project_id, "overview")
            hero = self.page.get_by_test_id("report-hero").first
            hero.wait_for(state="visible", timeout=30_000)
            verdict = hero.locator("h1.rp-verdict").first
            stages = self.page.locator(".rp-stages").first
            tiles = self.page.get_by_test_id("report-tiles")
            fact = self.page.get_by_test_id("report-gatefact")
            out = {
                "question": _tc(hero.locator(".rp-q")),
                "verdict": {"label": verdict.get_attribute("data-label"), "text": _tc(verdict)},
                "stages_class": (stages.get_attribute("class") or "") if stages.count() else None,
                "panels": [t.get_attribute("data-testid").removeprefix("report-stage-")
                           for t in self.page.locator("[data-testid^='report-stage-']").all()],
                "tiles": {"present": tiles.count() > 0,
                          "class": (tiles.first.get_attribute("class") or "") if tiles.count() else None,
                          "names": [t.get_attribute("data-tile") for t in tiles.locator("[data-tile]").all()]},
                "gatefact": _tc(fact) if fact.count() else None,
                "ship": [b.get_attribute("data-stage")
                         for b in self.page.locator("svg.rp-ship--linked path.band[data-stage]").all()],
                "tabs": [t.get_attribute("data-view") for t in
                         self.page.get_by_test_id("report-views").locator("[role=tab][data-view]").all()],
            }
            h.capture_text("stage_screen", _text(self.page))
            h.add_screenshot(self._b.screenshot("report-overview-scoped"))
            return out

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
                # keel-web 113 FR-4 (spec 073 FR-3): the full Overview draws no panel lead -- read so its absence is held
                panels[stage] = {"present": panel.count() > 0, "head": head, "lead": _tc(panel.locator(".rp-plead")),
                                 "leads": panel.locator(".rp-plead").count(), "rows": rows, "text": _tc(panel)}
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
                # spec 057 G6 / G7 (keel-web 086 FR-6): the pills the Overview draws and any report sheet over it
                "guide_pills": _safe_eval(self.page, _PILLS_JS, GUIDE_PILL),
                "report_sheet": self.page.locator(GUIDE_REPORT).count(),
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

    def friction_row_at_phone(self, project_id: str) -> dict:
        """keel-web 106 FR-5 (spec 068 FR-4): the Overview's Purchase-friction row at 390 x 844 -- its value column
        (`.rp-rv`) and status column (`.rp-rs`) never overlap, the status words wrapping inside their own column. The
        viewport is put back after the read."""
        before = self.page.viewport_size
        try:
            self.page.set_viewport_size({"width": 390, "height": 844})
            with self._b.step("founder reads the Overview's Purchase friction row on a phone (390 wide)") as h:
                self._report(project_id, "overview")
                self.page.get_by_test_id("report-hero").first.wait_for(state="visible", timeout=30_000)
                row = self.page.locator("a.rp-row[data-dim='commercial.purchase_friction']")
                if not row.count():
                    return {"present": False}
                row.first.scroll_into_view_if_needed()
                value = row.first.locator(".rp-rv").first
                status = row.first.locator(".rp-rs").first
                a = value.bounding_box() if row.first.locator(".rp-rv").count() else None
                b = status.bounding_box() if row.first.locator(".rp-rs").count() else None
                overlap = boxes_overlap(a, b)
                h.add_screenshot(self._b.screenshot("report-friction-row-phone"))
                return {"present": True, "value": a, "status": b, "overlap": overlap,
                        "status_words": _tc(status) if b else None}
        finally:
            if before:
                self.page.set_viewport_size(before)

    def insights(self, project_id: str) -> dict:
        """The Insights view (keel-web 077 FR-3; keel-web 095, spec 064 FR-8b): per box (`section.rp-ibox[data-dim]
        [data-status][data-state]`, `[data-dissent=true]` on a held line) its head (`.rp-ihead`), its whole text, the
        rung heading alone (`.rp-concern`), the dissent frame (`.rp-frame`), `.rp-tookby`, the split line, the themes
        (`ol.rp-themes > li`: `span.rp-themes__label`, `.rp-themes__n`, `li[data-own]` for *On their own*, each quote
        `p.rp-quote` with its `div.rp-iq > p.rp-pick` -- `.rp-opt` and `.rp-side[data-side]`), the GROUPING list
        (`[data-testid=insights-grouping]`), the RAW list (`.rp-raw`, its `.rp-raw__note`); a folded group is opened
        (`[data-testid=insights-more]`) before it is read; the `notAsked` lines (`[data-testid=insights-not-asked]
        li[data-dim]`); the empty state (`.rp-inone`); every quote and the view's own lines (the heading, the frame,
        *Only k of the n*: what `report_no_repeat` takes out; a quote's own pick line, `p.rp-pick` -- *Under $500 per
        site a month*, its `span.rp-opt`; the side word is a span beside it with no text between, so the option span
        is read on its own) -- is the person's answer, read into `quotes` with the quote, so D6 never counts it twice)."""
        from harness import interviewer_fake as fake                    # noqa: PLC0415
        with self._b.step("founder opens the report's insights") as h:
            self._report(project_id, "insights")
            view = self.page.get_by_test_id("report-insights").first
            view.wait_for(state="visible", timeout=30_000)
            for more in view.get_by_test_id("insights-more").all():
                try:
                    more.click()
                except Exception:  # noqa: BLE001 - a fold already open is read as it stands
                    pass
            boxes, own_lines = [], []
            for box in view.locator("section.rp-ibox").all():
                text = _words(box)

                def picks_of(scope):
                    out = []
                    for iq in scope.locator(".rp-iq").all():
                        side = iq.locator(".rp-side")
                        out.append({"quote": _tc(iq.locator(".rp-quote")), "option": _tc(iq.locator(".rp-opt")) or None,
                                    "side": side.first.get_attribute("data-side") if side.count() else None})
                    return out
                themes = []
                for li in box.locator("ol.rp-themes > li").all():
                    quotes = [_tc(q) for q in li.locator(".rp-quote").all()]
                    n = _tc(li.locator(".rp-themes__n"))
                    count = n.strip("()")
                    themes.append({"label": _tc(li.locator(".rp-themes__label")),
                                   "own": li.get_attribute("data-own") == "true",
                                   "count": int(count) if count.isdigit() else None, "quotes": quotes,
                                   "picks": picks_of(li)})
                concern = _tc(box.locator(".rp-concern"))
                frame = _tc(box.locator(".rp-frame"))
                took = _tc(box.locator(".rp-tookby"))
                # spec 076 FR-6 (keel-web 127 FR-4): the muted line under the groups, *{n} answer(s) were not about this*
                not_about = _tc(box.get_by_test_id("insights-not-about-this")) or None
                own_lines += [x for x in (concern, frame, took, not_about) if x]
                grouping = box.get_by_test_id("insights-grouping")
                boxes.append({
                    "key": box.get_attribute("data-dim"), "status": box.get_attribute("data-status"),
                    "state": box.get_attribute("data-state"), "dissent": box.get_attribute("data-dissent") == "true",
                    "head": _tc(box.locator(".rp-ihead")), "concern": concern, "frame": frame or None,
                    "not_about": not_about,
                    "themes": themes, "text": text,
                    "split": fake.SPLIT_NOTE if fake.SPLIT_NOTE in text else None,
                    "took_by": took or None,
                    "grouping": [_tc(q) for q in grouping.locator(".rp-quote").all()] if grouping.count() else None,
                    "raw": [_tc(q) for q in box.locator(".rp-raw .rp-quote").all()],
                    "raw_note": _tc(box.locator(".rp-raw__note")) or None,
                    # keel-web 106 FR-4: a GUESSED person's words, drawn apart at the box's foot under their own line
                    "guessed": [_tc(q) for q in box.get_by_test_id("insights-guessed").locator(".rp-quote").all()],
                    "guessed_head": _tc(box.locator(".rp-guessed__head")) or None,
                    "picks": picks_of(box)})
            not_asked = [{"key": li.get_attribute("data-dim"), "text": _tc(li)}
                         for li in view.locator("[data-testid=insights-not-asked] li[data-dim]").all()]
            text = _words(view)
            h.capture_text("stage_screen", text)
            h.add_screenshot(self._b.screenshot("report-insights"))
            return {"boxes": boxes, "empty": _tc(view.locator(".rp-inone")) or None, "not_asked": not_asked,
                    "quotes": [_tc(q) for q in view.locator(".rp-quote, .rp-opt").all()], "own_lines": own_lines,
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
                    follow_up_rows=(), said_rows=()) -> dict:
        """One stage page: every row's name, belief, status and amber; and, `open_row` named, that row
        opened and its per-person list read (keel-web `DimensionStagePage`'s `ul.dimpeople`: each person's
        name and how the answer was read). Spec 052 FR-8: each of `follow_up_rows` (the rungs whose people answered
        the follow-up) opened too, and every person's *One more thing · {rung}: "…"* line read off its list
        (`follow_ups`: `{dimension: [{name, line}]}`). Spec 075 (keel-cloud 141): each of `said_rows` opened and its said
        line under the belief read (`said`: `{dimension: text}`, `.dimrow__said`, the served `founderSaid`)."""
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
            said, bars, row_text = {}, {}, {}
            for key in said_rows or ():
                row = self.page.locator(f".dimrow[id='{key}']").first
                head = row.locator("button.dimrow__head")
                body = row.locator(".dimrow__body")
                if head.count() and not (body.count() and body.first.is_visible()):
                    head.first.click()
                    body.first.wait_for(state="visible", timeout=10_000)
                said[key] = _first_text(row, ".dimrow__said") or None
                # spec 076 FR-1 (keel-cloud 145 FR-1, keel-web 127 FR-5): the row's bars as drawn -- each label and
                # whether it is muted (`li.dimbar--muted`: not the founder's), and the row's whole words
                bars[key] = [{"label": _first_text(li, "span"), "muted": "dimbar--muted" in (li.get_attribute("class")
                                                                                            or "")}
                             for li in row.locator("ul.dimbars li.dimbar").all()]
                row_text[key] = _words(row)
            text = _text(self.page)
            h.capture_text("stage_screen", text)
            h.add_screenshot(self._b.screenshot(f"vector-{vector.lower()}"))
            return {"rows": rows, "text": text, "people": people, "open_row": open_row, "follow_ups": follow_ups,
                    "said": said, "bars": bars, "row_text": row_text,
                    "keel_bars": self.page.locator(".dimrow__said--keel").count(),
                    "headline": _first_text(self.page, "p.answers__headline"),
                    "decider_banner": _first_text(self.page, "p.decider-banner")}

    def brief(self, project_id: str, *, printed: bool = True) -> dict:
        """*Download the brief* -- the binding (keel-web 077 FR-5, `/p/{id}/print`, `report-binding`): the tab's title
        (the file name), whether *Preparing your brief…* was drawn first (a mutation observer installed before the
        page loads), and each `article.page[data-page]` -- its kicker, title, meta line and foot (the page frame), its
        whole text, how many Overview rows it drew (page 1 draws the lead lines only) and each panel's lead lines
        (`leads`, keel-web 113 FR-4: page one keeps them, the full Overview does not). `window.print` is stubbed
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
                              # keel-web 113 FR-4 (spec 073 FR-3): the panels' lead lines, kept on page one alone
                              "leads": {stage: _tc(page.locator(f"[data-testid='report-stage-{stage}'] .rp-plead"))
                                        for stage in ("PROBLEM", "SOLUTION", "COMMERCIAL")
                                        if page.locator(f"[data-testid='report-stage-{stage}']").count()},
                              "text": _words(page)})
            text = _screen_text(self.page, "[data-testid='report-binding']")
            h.capture_text("download", text)
            h.add_screenshot(self._b.screenshot("brief-print"))
            return {"title": self.page.title(), "preparing_seen": bool(self.page.evaluate("window.__preparingSeen")),
                    "pages": pages, "old_headline": self.page.locator(".bhead__headline").count(), "text": text}
