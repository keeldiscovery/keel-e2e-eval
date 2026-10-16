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
* `Answers`    -- the board (`/p/{id}`), the stage pages (`/p/{id}/s/{VECTOR}`) with one row's
                  per-person list, the overview's pilot tile, and keel-web 065's brief: page one
                  (`/p/{id}/brief`, and the download's `/p/{id}/print`) and page two
                  (`/p/{id}/brief/breakdown`).
"""

from __future__ import annotations

import re

from playwright.sync_api import Page

from harness.browser import _BrowserStep, _safe_all_texts, _safe_text, _screen_text
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

    # ------------------------------------------------------------------------ every screen's frame

    def frame(self) -> dict:
        """What frames the screen on display (keel-web 063 FR-003, FR-009): the kicker, *Problem · k of n*
        and its dots (how many, which one is now), and the side nav's lock."""
        dots = self.page.locator(".calib__progress .calib__dots i")
        classes = [dots.nth(i).get_attribute("class") or "" for i in range(dots.count())]
        nav = self.page.locator(f"nav[aria-label='{NAV_LOCKED_LABEL}']")
        return {"kicker": _first_text(self.page, ".corridor__kicker"),
                "progress": _first_text(self.page, ".calib__progress > span"),
                "dots": len(classes),
                "now": next((i + 1 for i, c in enumerate(classes) if "now" in c.split()), None),
                "done": sum(1 for c in classes if "done" in c.split()),
                "nav_locked": nav.count() > 0 and NAV_LOCK_LINE in _first_text(self.page, ".side-nav__lockline"),
                "nav_links": self.page.locator("nav.side-nav a").count()}

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
            _button(self.page, CONTEXT_SAVE).click()
            self.page.locator(".understands").first.wait_for(state="visible",
                                                             timeout=60_000 * self.patience)
            h.capture_text("stage_screen", _screen_text(self.page, ".ccard"))
            h.add_screenshot(self._b.screenshot("context-card"))
            return _first_text(self.page, ".understands__big")

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
        """keel-web 070 F9 on Importance's Check screen: the counter (*yours + n*) and the one-more ask as drawn, then the
        founder's own further difficulties typed in. With `one_more` the list is own + 1: *Save* is pressed first and
        answered 422 ONE_MORE_NEEDED, which opens an empty line, and the first of `add` is typed into it; every other
        is typed into a line *+ Write a difficulty they'd recognise* opens. Returns what each stage drew."""
        name = "problem.importance"
        counter = lambda: _first_text(self.page, "[data-testid=importance-counter]")  # noqa: E731
        ask = lambda: _first_text(self.page, "[data-testid=importance-one-more]")  # noqa: E731
        rows = self.page.locator(".listcheck ul.listrows li.listrow textarea.listrow__ed")
        out: dict = {"counter": counter(), "ask": ask(), "save_enabled": self._primary().is_enabled(), "added": []}
        with self._b.step(f"founder names {len(add)} more difficult{'y' if len(add) == 1 else 'ies'} on Importance's "
                          "Check screen" + (" after Save asks for one more" if one_more else "")) as h:
            h.add_screenshot(self._b.screenshot(f"check-{name}-as-drafted"))
            if one_more:
                before = rows.count()
                with self.page.expect_response(lambda r: r.request.method == "PUT" and "/calibration/PROBLEM" in r.url,
                                               timeout=20_000) as refused:
                    self._primary().click()
                out["refused"] = {"status": refused.value.status, "body": _json_body(refused.value)}
                self.page.wait_for_function("(n) => document.querySelectorAll("
                                            "'.listcheck ul.listrows li.listrow textarea.listrow__ed').length > n",
                                            arg=before, timeout=10_000)
                out["after_refusal"] = {"rows": rows.count(), "ask": ask(), "remedy": _first_text(
                    self.page, ".listcheck ~ .err[role=alert], .ccard .err[role=alert]"), "text": _text(self.page)}
                h.add_screenshot(self._b.screenshot(f"check-{name}-one-more"))
                rows.nth(rows.count() - 1).fill(add[0])
                out["added"].append(add[0])
                add = add[1:]
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

    def walk(self, person, interview: dict, wire_answers: dict) -> dict:
        """Begin, the decision-maker's idea screen, the gate, every item and the reveal, *Send my
        answers*; returns the body the page POSTed, the done screen's heading and what every screen drew.
        `wire_answers` is `{itemId: ItemAnswer}` -- what this person answers, already re-expressed as the
        wire takes it."""
        page = self.page
        with self._b.step(f"{person.person} answers the interview, screen by screen") as h:
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
                    self._gate(person, gate, interview.get("occasion"))
                if gate is None or person.recency:
                    self._items(interview, wire_answers)
            body = answered.value.request.post_data_json
            status = answered.value.status
            page.get_by_role("heading", level=1).first.wait_for(state="visible", timeout=20_000)
            self._keep()
            heading = _safe_text(lambda: page.get_by_role("heading", level=1).first.inner_text())
            h.add_screenshot(self._b.screenshot(f"interview-done-{person.person.split()[0]}"))
            return {"body": body, "status": status, "done": heading, "seen": list(self.seen),
                    "screens": list(self.screens)}

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

    def _gate(self, person, gate: dict, occasion: str | None) -> None:
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
            elif person.story:
                page.locator("textarea").first.fill(person.story)
        self.screens.append({"screen": "gate", "kicker": _first_text(page, ".iv-kicker"),
                             "question": _first_text(page, "h1.iv-q"), "chips": chips})
        _button(page, IV_CONTINUE).click()

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
                _button(page, IV_SEND if last else IV_NEXT).click()
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

    def board(self, project_id: str) -> dict:
        with self._b.step("founder opens the board") as h:
            self.page.goto(f"{self.base}/p/{project_id}", wait_until="load")
            self.page.locator(".panels a.panel").first.wait_for(state="visible", timeout=30_000)
            panels = []
            for panel in self.page.locator(".panels a.panel").all():
                panels.append({
                    "stage": panel.get_attribute("data-stage"),
                    "class": panel.get_attribute("class") or "",
                    "name": _first_text(panel, ".panel__name"),
                    "pill": _first_text(panel, ".panel__pill"),
                    "counts": [_safe_text(lambda c=c: c.inner_text())
                               for c in panel.locator(".panel__count").all()],
                })
            bands = [{"stage": b.get_attribute("data-stage"), "class": b.get_attribute("class") or ""}
                     for b in self.page.locator("svg.ship path.band").all()]
            tiles = _safe_all_texts(self.page, ".tile b")
            # keel-web 066 (D15): two tiles -- the people asked, then the pilot sign-ups (*None yet* and no line before
            # anyone finishes) -- and the people line under them.
            cards = [{"class": t.get_attribute("class") or "", "big": _tc(t.locator("b")),
                      "label": _tc(t.locator(".tile__label")), "line": _tc(t.locator(".tile__line")),
                      "has_line": t.locator(".tile__line").count() > 0}
                     for t in self.page.locator(".deck .tiles > .tile").all()]
            pilot_tile = self.page.locator(".tile--pilot")
            pilot = {"big": _tc(pilot_tile.locator("b")), "label": _tc(pilot_tile.locator(".tile__label")),
                     "line": _tc(pilot_tile.locator(".tile__line")), "present": pilot_tile.count() > 0,
                     "has_line": pilot_tile.locator(".tile__line").count() > 0}
            download = self.page.get_by_role("link", name="Download the brief")
            text = _text(self.page)
            h.capture_text("stage_screen", text)
            h.add_screenshot(self._b.screenshot("board"))
            return {"panels": panels, "bands": bands, "tiles": tiles, "tile_cards": cards, "pilot": pilot,
                    "people_line": _tc(self.page.locator("p.deck__people")),
                    "overall": _first_text(self.page, "p.overall"),
                    "download": download.count() > 0, "text": text}

    def vector_page(self, project_id: str, vector: str, *, open_row: str | None = None) -> dict:
        """One stage page: every row's name, belief, status and amber; and, `open_row` named, that row
        opened and its per-person list read (keel-web `DimensionStagePage`'s `ul.dimpeople`: each person's
        name and how the answer was read)."""
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
            text = _text(self.page)
            h.capture_text("stage_screen", text)
            h.add_screenshot(self._b.screenshot(f"vector-{vector.lower()}"))
            return {"rows": rows, "text": text, "people": people, "open_row": open_row,
                    "keel_bars": self.page.locator(".dimrow__said--keel").count(),
                    "headline": _first_text(self.page, "p.answers__headline"),
                    "decider_banner": _first_text(self.page, "p.decider-banner")}

    def brief(self, project_id: str, *, printed: bool = False) -> dict:
        """The brief's **page one** (keel-web 065, `/p/{id}/brief`; `printed` reads the download's tab,
        `/p/{id}/print`, the same page): the decision and how sure, the headline, the four tiles (three verdict
        words and the pilot sign-ups, *k of n · p%* over its per-link line), per stage its question, the served
        answer and its cards (name, number, line, status words, each linking to its block), the next tests and the
        footer. Every word read as the DOM carries it, not as the CSS capitalises it."""
        where = "print" if printed else "brief"
        with self._b.step("founder opens the brief to hand over" if printed else "founder opens the brief") as h:
            if printed:
                self.page.add_init_script("window.print = () => {};")
            self.page.goto(f"{self.base}/p/{project_id}/{where}", wait_until="load")
            self.page.locator("div.brief").first.wait_for(state="visible", timeout=30_000)
            brief = self.page.locator("div.brief").first
            text = _screen_text(self.page, "div.brief")
            h.capture_text("download" if printed else "stage_screen", text)
            h.add_screenshot(self._b.screenshot("brief-print" if printed else "brief"))
            stages = {}
            for stage in ("problem", "solution", "commercial"):
                section = brief.locator(f"#brief-{stage}")
                stages[stage] = {
                    "question": _tc(section.locator(".bq")),
                    "answer": _tc(section.locator(".bans")),
                    "cards": [{"key": c.get_attribute("data-dim"), "href": c.get_attribute("href"),
                               "name": _tc(c.locator(".bcard__name")),
                               "number": _tc(c.locator(".bcard__number")) or None,
                               "line": _tc(c.locator(".bcard__line")),
                               "statusWords": _tc(c.locator(".bcard__status"))}
                              for c in section.locator("a.bcard").all()],
                }
            tiles = [{"label": _tc(t.locator(".btile__label")), "word": _tc(t.locator(".btile__word")),
                      "big": _tc(t.locator(".btile__big")), "line": _tc(t.locator(".btile__line")),
                      "has_line": t.locator(".btile__line").count() > 0,
                      "pilot": "btile--pilot" in (t.get_attribute("class") or "")}
                     for t in brief.locator(".btile").all()]
            nxt = [{"text": _tc(li.locator(".bnext__text")),
                    "chip": li.locator("a.bchip").first.get_attribute("data-dim") if li.locator("a.bchip").count()
                    else None} for li in brief.locator("#brief-next .bnext li").all()]
            return {
                "decision": brief.get_attribute("data-decision"),
                "decision_words": _tc(brief.locator(".bdecision")),
                "how": _tc(brief.locator(".bhow")),
                "headline": _tc(brief.locator(".bhead__headline")),
                "tiles": tiles,
                "sections": [s_.get_attribute("id") for s_ in brief.locator("section.bsec").all()],
                "stages": stages,
                "next": nxt,
                "footer": _tc(brief.locator(".bfooter")),
                "text": text,
            }

    def breakdown(self, project_id: str) -> dict:
        """The brief's **page two** (keel-web 065, `/p/{id}/brief/breakdown`): per stage section, one block per card
        -- its name and status words, the card's number and line, its rows (*Tested*, *What broke*, *Not tested*,
        *Not asked*), whether the stage row's own body is drawn -- and the back link."""
        with self._b.step("founder opens the brief's breakdown") as h:
            self.page.goto(f"{self.base}/p/{project_id}/brief/breakdown", wait_until="load")
            root = self.page.locator("div.brief--breakdown").first
            root.wait_for(state="visible", timeout=30_000)
            text = _screen_text(self.page, "div.brief--breakdown")
            h.capture_text("stage_screen", text)
            h.add_screenshot(self._b.screenshot("brief-breakdown"))
            stages = {}
            for stage in ("problem", "solution", "commercial"):
                section = root.locator(f"#breakdown-{stage}")
                blocks = []
                for block in section.locator(".bd").all():
                    key = block.get_attribute("id")
                    if not key:
                        continue                       # the problem's quotes and sharpest line, no card
                    blocks.append({"key": key, "name": _tc(block.locator(".bd__name")),
                                   "statusWords": _tc(block.locator(".bd__status")),
                                   "card": _tc(block.locator(".bd__card")),
                                   "rows": [_tc(r) for r in block.locator(":scope > .bd__row").all()],
                                   "broke": _tc(block.locator(".bd__broke")) or None,
                                   "body": block.locator(".dimrow__body").count() > 0,
                                   # keel-web 067: Keel's bar in the row body's bar slot, where Keel sets it
                                   "keel_bar": [_tc(k) for k in block.locator("p.dimrow__said.dimrow__said--keel").all()],
                                   "said": [_tc(k) for k in block.locator("p.dimrow__said").all()]})
                stages[stage] = {"present": section.count() > 0, "blocks": blocks,
                                 # keel-web 067: each quote credited by its served words, its link on `data-link`
                                 "quotes": [{"link": q.get_attribute("data-link"), "words": _tc(q.locator(":scope > cite"))}
                                            for q in section.locator(".bquote").all()]}
            return {"stages": stages, "back": root.locator("a.bback").count(), "text": text,
                    "keel_bars": len(root.locator(".dimrow__said--keel").all())}
