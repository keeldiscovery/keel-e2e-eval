"""keel-web's vector-corridor screens, as page objects (spec 039).

Machinery, not judgement: every class here acts and reads, and asserts nothing -- the scenario
(`evals/corpus_scenario.py`) judges what they read. The labels a page object **presses** are spelled
once, below, copied from keel-web `src/lib/translate.ts`; a copy change in keel-web shows up as a
named mismatch rather than as a fifteen-second wait on nothing (the rule DRIFT #71 taught).

Four groups, in the journey's order:

* `Corridor`   -- the founder's five steps under `/p/{id}/define/...`: the context, the two seeds and
                  their cards, one calibration screen per dimension, the review, the persona, and
                  step 5 (the idea, the word, the pilot, *Lock and write the questions*).
* `PeopleLinks` -- the People page's two send popups: the specialist's three steps and, on a B2B
                  study, the decision-maker's commercial link.
* `Interview`  -- the stranger's `/i/{token}` pager: intro, gate, items, reveal, done.
* `Answers`    -- the board (`/p/{id}`), the vector pages (`/p/{id}/s/{VECTOR}`) and the brief
                  (`/p/{id}/print`).
"""

from __future__ import annotations

import re

from playwright.sync_api import Page

from harness.browser import _BrowserStep, _safe_all_texts, _safe_text, _screen_text
from harness.steps import Recorder

# ------------------------------------------------------------------- keel-web's own words (pressed)

CONTEXT_SAVE = "Save and continue"
CONTEXT_YES = "Yes, that's it"
WINDOW_COUNT = "How many"
WINDOW_UNIT = "Unit"
SEED_SEND = "Send"
CARD_YES_PROBLEM = "Yes, that's the problem"
CARD_LOOKS_RIGHT = "Looks right"
KICKER_INTERPRETATION = "Here's what Keel understood"
KICKER_MECHANISM = "Here's the mechanism Keel understood"
KICKER_CONTEXT = "Keel understands"
CALIB_CONTINUE = "Continue"
UNSURE_CHIP = "I'm not sure"
PRICE_NONE_CHIP = "No price yet"
COST_MODE_GROUP = "Measured as"
COST_MODE_WORD = {"AMOUNT": "Fixed amount", "HOURS": "Hours"}
REVIEW_CONFIRM = {"PROBLEM": "Confirm problem · on to your solution",
                  "SOLUTION": "Confirm solution · on to will they pay",
                  "COMMERCIAL": "Continue to people"}
PERSONA_QUESTION = "Who makes the buying decision?"
PERSONA_SAME = "The same person would decide to pay"
PERSONA_SOMEONE_ELSE = "Someone else would decide"
PERSONA_ROLE = "If someone else, what role would that person typically have?"
BEFORE_CONTINUE = "Continue"
BEFORE_APPROVE = "This describes my idea correctly"
BEFORE_LOCK = "Lock and write the questions"
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
IV_AMOUNT = {"AMOUNT": "Amount", "HOURS": "Hours"}
IV_NOTHING = "It cost us nothing"
IV_DONE_TITLE = "That's it."


def chip_word(chip: str, *, on_gate: bool = False, occasion: str | None = None) -> str:
    """keel-web `chipWord`: the words a chip button carries."""
    return {"NOTHING": IV_NOTHING,
            "CANT_RECALL": (f"I can't recall one particular {(occasion or '').strip() or 'time'}"
                            if on_gate else "I can't recall"),
            "RATHER_NOT_SAY": "I'd rather not say",
            "ROUGH_GUESS": "That's a rough guess",
            "CANT_SAY": "I can't say",
            "SKIP": "Skip this one"}[chip]


def _wait_url(page: Page, pattern: str, *, timeout_s: float = 30) -> None:
    page.wait_for_url(re.compile(pattern), timeout=timeout_s * 1000)


def _button(page: Page, name, *, exact: bool = True):
    return page.get_by_role("button", name=name, exact=exact) if isinstance(name, str) else \
        page.get_by_role("button", name=name)


# --------------------------------------------------------------------------------------- Corridor

class Corridor:
    """The founder's corridor screens. One instance per founder page.

    `patience` scales the waits that wait on a **model** -- a card landing, questions being written
    -- and nothing else: 1 on the scripted journeys, where the scripted executor answers in well
    under a second, more on S-012, where a host's model writes each one."""

    def __init__(self, page: Page, recorder: Recorder, base_url: str, *, patience: float = 1.0):
        self.page = page
        self.base = base_url.rstrip("/")
        self.patience = patience
        self._b = _BrowserStep(recorder, page, "founder")

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
        slug = vector.lower()
        name = CARD_YES_PROBLEM if vector == "PROBLEM" else CARD_LOOKS_RIGHT
        with self._b.step(f"founder confirms the {slug} card: {name}") as h:
            _button(self.page, name).click()
            _wait_url(self.page, rf"/define/{slug}/q/1")
            h.add_screenshot(self._b.screenshot(f"{slug}-confirmed"))

    # ------------------------------------------------------------------ calibration, one screen

    def wait_questions(self, *, timeout_s: float = 60) -> None:
        self.page.locator("h1.calib__q").first.wait_for(
            state="visible", timeout=timeout_s * 1000 * self.patience)

    def calibration_screen(self) -> dict:
        return {"name": _first_text(self.page, ".calib__name"),
                "question": _first_text(self.page, "h1.calib__q"),
                "progress": _first_text(self.page, ".calib__progress span"),
                "belief": _first_text(self.page, ".calib__belief-text")}

    def answer(self, question: dict, answer: dict) -> dict:
        """Answers the calibration screen on display for `question` (a `CalibrationQuestion` read
        off the wire) with `answer` (the wire's `CalibrationAnswer`), then *Continue*. Returns what
        the screen showed, the belief line included, just before Continue."""
        name = question.get("dimension")
        with self._b.step(f"founder answers {name}") as h:
            self.page.locator("h1.calib__q").first.wait_for(state="visible", timeout=30_000)
            control = question.get("control")
            labels = {o.get("normalized"): o.get("label") for o in question.get("options") or []}
            if answer.get("unsure"):
                chip = PRICE_NONE_CHIP if control == "price_range" else UNSURE_CHIP
                self.page.locator("button.calib__chip", has_text=chip).first.click()
            elif control in ("single_choice", "rank_pick"):
                group = self.page.get_by_role("radiogroup", name=question.get("name"), exact=True)
                group.get_by_role("radio", name=labels[answer["codes"][0]], exact=True).click()
            elif control == "multi_choice":
                group = self.page.get_by_role("group", name=question.get("name"), exact=True)
                for code in answer["codes"]:
                    group.get_by_role("checkbox", name=labels[code], exact=True).click()
            elif control == "numeric_interval":
                interval = answer["interval"]
                nums = self.page.locator("input.calib__num")
                nums.nth(0).fill(_number(interval["low"]))
                nums.nth(1).fill(_number(interval["high"]))
                unit = self.page.locator("select.calib__unit")
                if unit.count():
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
                raise AssertionError(f"no screen for the calibration control {control!r} ({name})")
            seen = self.calibration_screen()
            h.capture_text("stage_screen", _text(self.page))
            h.add_screenshot(self._b.screenshot(f"calibration-{name}"))
            before = self.page.url
            _button(self.page, CALIB_CONTINUE).click()
            # Continue writes and then navigates: the next screen is a new URL (`q/{n+1}` or the
            # review). Typing into this one before it has gone types into the wrong question.
            self.page.wait_for_function("(u) => window.location.href !== u", arg=before,
                                        timeout=30_000)
            return seen

    # ---------------------------------------------------------------------------------- review

    def review(self, project_id: str, vector: str) -> dict:
        slug = vector.lower()
        with self._b.step(f"founder reads the {slug} review") as h:
            _wait_url(self.page, rf"/define/{slug}/review")
            self.page.locator(".rtable, .rstrips").first.wait_for(state="visible", timeout=20_000)
            rows = []
            for row in self.page.locator(".rtable tbody tr").all():
                cells = [_safe_text(lambda c=c: c.inner_text()) for c in row.locator("td").all()]
                rows.append(cells)
            h.add_screenshot(self._b.screenshot(f"{slug}-review"))
            return {"rows": rows, "foot": _first_text(self.page, ".rfoot"),
                    "text": _text(self.page)}

    def confirm_review(self, vector: str) -> None:
        nxt = {"PROBLEM": r"/define/solution/seed", "SOLUTION": r"/define/persona",
               "COMMERCIAL": r"/define/ready"}[vector]
        with self._b.step(f"founder confirms the {vector.lower()} review") as h:
            _button(self.page, REVIEW_CONFIRM[vector]).click()
            _wait_url(self.page, nxt)
            h.add_screenshot(self._b.screenshot(f"{vector.lower()}-review-confirmed"))

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
            _button(self.page, CALIB_CONTINUE).click()
            self.page.get_by_text(KICKER_CONTEXT).first.wait_for(state="visible", timeout=20_000)
            text = _text(self.page)
            h.add_screenshot(self._b.screenshot("persona-set"))
            _button(self.page, CALIB_CONTINUE).click()
            _wait_url(self.page, r"/define/commercial/q/1")
            return {"text": text}

    # ------------------------------------------------------------------- step 5: before people

    def approve_idea_and_lock(self) -> dict:
        """The idea screen (approve the three lines), the word, the pilot, and *Lock and write the
        questions*. Returns what the idea preview drew."""
        with self._b.step("founder approves the idea's three lines, then locks") as h:
            _wait_url(self.page, r"/define/ready")
            self.page.get_by_test_id("before-counter").wait_for(state="visible", timeout=20_000)
            preview = _safe_text(lambda: self.page.get_by_test_id("idea-preview").inner_text())
            self.page.get_by_label(BEFORE_APPROVE, exact=True).check()
            self.page.wait_for_timeout(500)
            h.add_screenshot(self._b.screenshot("idea-approved"))
            _button(self.page, BEFORE_CONTINUE).click()
            _wait_url(self.page, r"/define/ready/word")
            _button(self.page, BEFORE_CONTINUE).click()
            _wait_url(self.page, r"/define/ready/pilot")
            h.add_screenshot(self._b.screenshot("pilot"))
            _button(self.page, BEFORE_LOCK).click()
            _wait_url(self.page, r"/people", timeout_s=60)
            h.add_screenshot(self._b.screenshot("locked-people"))
            return {"idea_preview": preview}


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
    """The stranger's `/i/{token}`: one screen at a time. `walk` takes the interview as the wire
    served it (to read the labels of the option ids a pick names) and the person's picks."""

    def __init__(self, page: Page, recorder: Recorder):
        self.page = page
        self._b = _BrowserStep(recorder, page, "participant")
        self.seen: list[str] = []

    def _keep(self) -> None:
        text = _screen_text(self.page, "div.iv-page") or _screen_text(self.page, "body")
        if text and (not self.seen or self.seen[-1] != text):
            self.seen.append(text)

    def kicker(self) -> str:
        return _first_text(self.page, ".iv-kicker")

    def _main(self):
        return self.page.locator("main").first

    def open(self, url: str) -> None:
        with self._b.step("the stranger opens their link") as h:
            self.page.goto(url, wait_until="load")
            _button(self.page, IV_BEGIN).wait_for(state="visible", timeout=20_000)
            self._keep()
            h.add_screenshot(self._b.screenshot("interview-intro"))

    def walk(self, person, interview: dict, wire_answers: dict) -> dict:
        """Begin, the gate, every item and the reveal, *Send my answers*; returns the body the page
        POSTed and the done screen's heading. `wire_answers` is `{itemId: ItemAnswer}` -- what this
        person answers, already re-expressed as the wire takes it."""
        page = self.page
        with self._b.step(f"{person.person} answers the interview, screen by screen") as h:
            with page.expect_request(lambda r: r.method == "POST"
                                     and r.url.endswith("/interview/response"),
                                     timeout=120_000) as sent:
                _button(page, IV_BEGIN).click()
                gate = interview.get("gate")
                if gate:
                    self._gate(person, gate, interview.get("occasion"))
                    if not person.recency:
                        pass
                if gate is None or person.recency:
                    self._items(interview, wire_answers)
            body = sent.value.post_data_json
            page.get_by_role("heading", level=1).first.wait_for(state="visible", timeout=20_000)
            self._keep()
            heading = _safe_text(lambda: page.get_by_role("heading", level=1).first.inner_text())
            h.add_screenshot(self._b.screenshot(f"interview-done-{person.person.split()[0]}"))
            return {"body": body, "done": heading, "seen": list(self.seen)}

    def opt_in_to_pilot(self, interview: dict) -> None:
        label = ((interview.get("done") or {}).get("pilot") or {}).get("label")
        if not label:
            return
        with self.page.expect_request(lambda r: r.method == "POST" and r.url.endswith("/interview/pilot"),
                                      timeout=20_000):
            self.page.get_by_role("checkbox", name=label, exact=True).click()

    def _gate(self, person, gate: dict, occasion: str | None) -> None:
        page = self.page
        group = page.get_by_role("radiogroup", name=gate["question"], exact=True)
        group.wait_for(state="visible", timeout=20_000)
        self._keep()
        group.get_by_role("radio", name=IV_YES if person.recency else IV_NO, exact=True).click()
        if person.recency:
            if person.anchor_chip:
                _button(page, chip_word(person.anchor_chip, on_gate=True, occasion=occasion)).click()
            elif person.story:
                page.locator("textarea").first.fill(person.story)
        _button(page, IV_CONTINUE).click()

    def _items(self, interview: dict, wire_answers: dict) -> None:
        page = self.page
        parts = interview.get("parts") or []
        for p_index, part in enumerate(parts):
            if p_index > 0 and interview.get("reveal") and part.get("anchor") == "the_reveal":
                _button(page, IV_CONTINUE).wait_for(state="visible", timeout=20_000)
                self._keep()
                _button(page, IV_CONTINUE).click()
            items = part.get("items") or []
            for i_index, item in enumerate(items):
                page.locator("h1.iv-q").first.wait_for(state="visible", timeout=20_000)
                self._keep()
                answer = wire_answers.get(item.get("itemId"))
                if answer is not None:
                    self._answer(item, answer)
                last = p_index == len(parts) - 1 and i_index == len(items) - 1
                _button(page, IV_SEND if last else IV_NEXT).click()

    def _answer(self, item: dict, answer: dict) -> None:
        main = self._main()
        options = {o.get("optionId"): o.get("label") for o in item.get("options") or []}
        advantages = {a.get("id"): a.get("label") for a in item.get("advantages") or []}
        if answer.get("chip"):
            _button(self.page, chip_word(answer["chip"])).click()
            return
        if "scale" in answer:
            main.get_by_role("radio", name=str(answer["scale"]), exact=True).click()
            return
        if "costTotal" in answer:
            cost = answer["costTotal"]
            if cost.get("nothing"):
                _button(self.page, IV_NOTHING).click()
                return
            main.get_by_role("radiogroup", name="Measured as", exact=True) \
                .get_by_role("radio", name=IV_AMOUNT[cost["mode"]], exact=True).click()
            main.locator("input").first.fill(_number(cost["value"]))
            return
        multi = item.get("control") in ("multi_choice", "multi_choice_ladder")
        for option_id in answer.get("optionIds") or []:
            role = "checkbox" if multi else "radio"
            main.get_by_role(role, name=options[option_id], exact=True).first.click()
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
            download = self.page.get_by_role("link", name="Download the brief")
            text = _text(self.page)
            h.capture_text("stage_screen", text)
            h.add_screenshot(self._b.screenshot("board"))
            return {"panels": panels, "bands": bands, "tiles": tiles,
                    "overall": _first_text(self.page, "p.overall"),
                    "download": download.count() > 0, "text": text}

    def vector_page(self, project_id: str, vector: str) -> dict:
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
            text = _text(self.page)
            h.capture_text("stage_screen", text)
            h.add_screenshot(self._b.screenshot(f"vector-{vector.lower()}"))
            return {"rows": rows, "text": text,
                    "headline": _first_text(self.page, "p.answers__headline"),
                    "decider_banner": _first_text(self.page, "p.decider-banner")}

    def brief(self, project_id: str) -> dict:
        with self._b.step("founder opens the brief to hand over") as h:
            self.page.add_init_script("window.print = () => {};")
            self.page.goto(f"{self.base}/p/{project_id}/print", wait_until="load")
            self.page.locator("div.brief").first.wait_for(state="visible", timeout=30_000)
            text = _screen_text(self.page, "div.brief")
            h.capture_text("download", text)
            h.add_screenshot(self._b.screenshot("brief"))
            return {
                "decision": self.page.locator("div.brief").first.get_attribute("data-decision"),
                "headline": _first_text(self.page, ".bhead__headline"),
                "tiles": [_first_text(t, ".btile__word")
                          for t in self.page.locator(".btile").all()],
                "sections": [s.get_attribute("id") for s in self.page.locator("section.bsec").all()],
                "text": text,
            }
