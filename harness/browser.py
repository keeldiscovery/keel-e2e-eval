"""Page objects for the round-5 screens (spec 005-connect-stack FR-008): `Auth` (setup/login),
`Connect` (device-approval frames B/C/G), `Landing` (L1-L4), `Shell` (agent line, side nav with
status words), `Chat` (C1-C8: bubbles, composer, confirmation card), `StageCard` (R1/R2/R4,
E1-E3), `People` (P1-P9: toggle, role cards, popup steps, table rows, answers popup, progress
line, toast), `Brief` (B1/B2), `ParticipantBrowser` (unchanged in role, selectors updated).

Selectors are taken from keel-web's built DOM -- `../keel-web/tests/visual/states/*.ts` and the
components under `../keel-web/src` -- never guessed (spec 005 FR-008). This app has no
`data-testid` anywhere: locators are Playwright's accessible-name finders (`get_by_role`,
`get_by_label`, `get_by_text`) plus the CSS classes `src/styles/app.css` actually defines.

Every method records a step and screenshots on entry (spec FR-008); every navigation waits on the
frame's own words, never a sleep, and waits for `document.fonts.ready` before a screenshot (spec
edge cases, matching keel-web's own visual tests).
"""

from __future__ import annotations

import re
from contextlib import contextmanager
from typing import Callable, Iterator

from playwright.sync_api import Page

from harness.evidence import write_failure_capture
from harness.steps import Recorder, StepHandle


class _BrowserStep:
    """Shared plumbing: numbered screenshots, `document.fonts.ready` before every shot, and on
    any exception, dumping page HTML + the console log gathered so far into failure/ before
    re-raising (contracts/evidence-contract.md).
    """

    def __init__(self, recorder: Recorder, page: Page, party: str):
        self.recorder = recorder
        self.page = page
        self.party = party
        self.console_log: list[str] = []
        page.on("console", lambda msg: self.console_log.append(f"[{msg.type}] {msg.text}"))

    def screenshot(self, slug: str) -> str:
        try:
            self.page.wait_for_function("document.fonts.ready", timeout=5_000)
        except Exception:  # noqa: BLE001 - a font-ready wait must never block evidence capture
            pass
        name = self.recorder.next_screenshot_name(slug)
        self.page.screenshot(path=str(self.recorder.screenshot_path(name)), full_page=True)
        return name

    def step(self, name: str):
        return _step_cm(self, name)


def _step_cm(bstep: "_BrowserStep", name: str):
    @contextmanager
    def cm():
        with bstep.recorder.step(name, party=bstep.party, kind="browser") as h:
            try:
                yield h
            except Exception as exc:
                try:
                    page_html = bstep.page.content()
                except Exception as content_exc:  # noqa: BLE001 - best-effort, never mask the real error
                    page_html = (f"<!-- page.content() unavailable: {content_exc} -->\n"
                                 f"<!-- the browser step failed with: {exc} -->")
                write_failure_capture(bstep.recorder.run_dir, page_html=page_html,
                                       console_lines=list(bstep.console_log))
                raise

    return cm()


def _safe_text(getter: Callable[[], str]) -> str:
    """Best-effort text capture for scoring purposes only: a selector that doesn't match must
    never fail the *scenario* -- only the check that reads the resulting captured_text should be
    able to fail."""
    try:
        return getter()
    except Exception:  # noqa: BLE001 - capture is advisory, never load-bearing for the scenario
        return ""


def _safe_all_texts(page: Page, selector: str) -> list[str]:
    try:
        return page.locator(selector).all_inner_texts()
    except Exception:  # noqa: BLE001 - capture is advisory, never load-bearing for the scenario
        return []


def _capture_agent_line(page: Page, h: StepHandle) -> None:
    """`div.agentline > span.st-*` -- the brand row's own live claim about whether a runtime is
    connected, present on every founder screen this harness visits post-login (Landing, Shell)."""
    h.capture_text("agent_line", _safe_text(lambda: page.locator(".agentline").first.inner_text()))


class Auth:
    """Setup and login (`src/routes/auth/{Setup,Login}Route.tsx`)."""

    def __init__(self, page: Page, web_base_url: str, recorder: Recorder, *, party: str = "founder"):
        self.page = page
        self.base_url = web_base_url
        self._bstep = _BrowserStep(recorder, page, party)

    def open_setup(self) -> None:
        with self._bstep.step("founder opens the setup screen") as h:
            self.page.goto(self.base_url, wait_until="load")
            self.page.locator("h1.auth-title").wait_for(state="visible", timeout=15_000)
            h.capture_text("screen", "setup")
            h.capture_text("stage_screen", _safe_text(lambda: self.page.locator("h1.auth-title").inner_text()))
            h.add_screenshot(self._bstep.screenshot("setup"))

    def setup(self, *, name: str, email: str, password: str) -> None:
        with self._bstep.step("founder creates the account") as h:
            self.page.get_by_label("Your name").fill(name)
            self.page.get_by_label("Email").fill(email)
            self.page.get_by_label("Password").fill(password)
            h.add_screenshot(self._bstep.screenshot("setup-filled"))
            self.page.get_by_role("button", name="Create account").click()
            self.page.wait_for_load_state("load")

    def open_login(self) -> None:
        with self._bstep.step("founder opens the login screen") as h:
            self.page.goto(f"{self.base_url}/login", wait_until="load")
            self.page.locator("h1.auth-title").wait_for(state="visible", timeout=15_000)
            h.capture_text("screen", "login")
            h.add_screenshot(self._bstep.screenshot("login"))

    def log_in(self, *, email: str, password: str) -> None:
        """Drives the real `/login` screen -- never a transplanted cookie."""
        with self._bstep.step("founder logs in") as h:
            if "/login" not in self.page.url:
                self.open_login()
            self.page.get_by_label("Email").fill(email)
            self.page.get_by_label("Password").fill(password)
            h.add_screenshot(self._bstep.screenshot("login-filled"))
            self.page.get_by_role("button", name="Log in").click()
            self.page.wait_for_load_state("load")
            h.add_screenshot(self._bstep.screenshot("logged-in"))


class Connect:
    """The device-approval frames (`src/routes/connect/ConnectRoute.tsx`): B (approve/deny), C
    (approved), G (denied), plus the plain `/connect` entry (A/D)."""

    def __init__(self, page: Page, recorder: Recorder, *, party: str = "founder"):
        self.page = page
        self._bstep = _BrowserStep(recorder, page, party)

    def open(self, verification_uri: str) -> None:
        """Opens exactly the URL keel-runtime's connect script handed back -- never
        reconstructed (spec US2 step 1)."""
        with self._bstep.step("founder opens the device-approval link") as h:
            self.page.goto(verification_uri, wait_until="load")
            self.page.locator("h1.auth-title").wait_for(state="visible", timeout=15_000)
            title = _safe_text(lambda: self.page.locator("h1.auth-title").inner_text())
            h.capture_text("screen", "connect")
            h.capture_text("stage_screen", title)
            h.add_screenshot(self._bstep.screenshot("connect-approve"))

    def user_code(self) -> str:
        return _safe_text(lambda: self.page.locator("div.code").first.inner_text())

    def approve(self) -> None:
        """Frame B -> C: *Approve this device*."""
        with self._bstep.step("founder approves the device") as h:
            self.page.get_by_role("button", name="Approve this device").click()
            self.page.get_by_text(re.compile("agent connected", re.I)).wait_for(
                state="visible", timeout=15_000)
            h.capture_text("stage_screen", _safe_text(lambda: self.page.locator(".stateline").inner_text()))
            h.add_screenshot(self._bstep.screenshot("connect-approved"))

    def deny(self) -> None:
        """Frame B -> G."""
        with self._bstep.step("founder denies the device") as h:
            self.page.get_by_role("button", name="Deny").click()
            self.page.get_by_text(re.compile("device denied", re.I)).wait_for(
                state="visible", timeout=15_000)
            h.add_screenshot(self._bstep.screenshot("connect-denied"))

    def go_to_projects(self) -> None:
        with self._bstep.step("founder returns to their projects") as h:
            self.page.get_by_role("link", name=re.compile("go to your projects", re.I)).click()
            self.page.wait_for_load_state("load")
            h.add_screenshot(self._bstep.screenshot("back-at-landing"))


class Landing:
    """`src/routes/LandingRoute.tsx` -- L1 (name the first project), L2 (gated, no agent), L3/L4
    (has projects)."""

    def __init__(self, page: Page, web_base_url: str, recorder: Recorder, *, party: str = "founder"):
        self.page = page
        self.base_url = web_base_url
        self._bstep = _BrowserStep(recorder, page, party)

    def open(self) -> None:
        with self._bstep.step("founder opens the landing page") as h:
            self.page.goto(self.base_url, wait_until="load")
            self.page.locator(".shell").first.wait_for(state="visible", timeout=15_000)
            _capture_agent_line(self.page, h)
            h.capture_text("screen", "landing")
            h.add_screenshot(self._bstep.screenshot("landing"))

    def agent_line_text(self) -> str:
        return _safe_text(lambda: self.page.locator(".agentline").first.inner_text())

    def is_gated(self) -> bool:
        """L2: no agent connected yet, no project can be started."""
        return self.page.locator(".gate").count() > 0

    def open_connect_from_gate(self) -> None:
        with self._bstep.step("founder clicks I have a code from the gated landing") as h:
            self.page.get_by_role("link", name=re.compile("i have a code", re.I)).click()
            self.page.wait_for_load_state("load")
            h.add_screenshot(self._bstep.screenshot("landing-gate-to-connect"))

    def name_project(self, name: str) -> None:
        """L1: the guided lobby's name field -> *Save and continue* -> `/p/:id` (C1)."""
        with self._bstep.step(f"founder names the project: {name!r}") as h:
            box = self.page.locator(".guided-step").get_by_role("textbox")
            if box.count() == 0:
                box = self.page.get_by_label(re.compile("what should we call this project", re.I))
            box.fill(name)
            h.add_screenshot(self._bstep.screenshot("landing-name-filled"))
            self.page.get_by_role("button", name=re.compile("save and continue", re.I)).click()
            self.page.wait_for_load_state("load")

    def project_rows(self) -> list[str]:
        return _safe_all_texts(self.page, "a.project-row")

    def open_project(self, index: int = 0) -> None:
        with self._bstep.step(f"founder opens project row {index}") as h:
            self.page.locator("a.project-row").nth(index).click()
            self.page.wait_for_load_state("load")
            h.add_screenshot(self._bstep.screenshot("landing-open-project"))


class Shell:
    """The project shell's own side nav (`src/components/ProjectShell.tsx`, `SideNav.tsx`) --
    read-only helpers shared by every screen inside `/p/:id/*`."""

    def __init__(self, page: Page):
        self.page = page

    def agent_line_text(self) -> str:
        return _safe_text(lambda: self.page.locator(".agentline").first.inner_text())

    def nav_status(self, label: str) -> str:
        """The status word beside a nav row named `label` (e.g. "The problem", "Your solution",
        "Will they pay", "Brief") -- `span.side-nav__status`'s own rendered text."""
        item = self.page.locator(".side-nav__item", has_text=label).first
        return _safe_text(lambda: item.locator(".side-nav__status").inner_text())

    def people_locked(self) -> bool:
        return self.page.locator(".side-nav__item--locked").count() > 0

    def people_locked_reason(self) -> str:
        return _safe_text(lambda: self.page.locator(".side-nav__locked-why").first.inner_text())

    def open_people(self) -> None:
        self.page.get_by_role("link", name=re.compile("^people$", re.I)).click()
        self.page.wait_for_load_state("load")

    def open_brief(self) -> None:
        self.page.get_by_role("link", name=re.compile("^brief$", re.I)).click()
        self.page.wait_for_load_state("load")

    def open_stage_nav(self, label: str) -> None:
        self.page.locator(".side-nav__item", has_text=label).first.click()
        self.page.wait_for_load_state("load")

    def capture_common(self, h: StepHandle) -> None:
        _capture_agent_line(self.page, h)
        if self.people_locked():
            h.capture_text("locked_reason", self.people_locked_reason())


class Chat:
    """The guided step's own chat (`src/components/chat/ChatFrame.tsx`, `GuidedStep.tsx`) --
    C1-C8: the composer, the agent's turns, and the confirmation card. Every call captures the
    frame's own state line (`chat__sub`) as `chat_state` (an `agent_turn` interaction, spec
    FR-009's "the frame's state line", never a wire read) and, once an agent bubble renders, its
    text as `agent_reply`.
    """

    def __init__(self, page: Page, recorder: Recorder, *, party: str = "founder"):
        self.page = page
        self._bstep = _BrowserStep(recorder, page, party)
        self._interaction_id: str | None = None

    def _scope(self):
        if self._interaction_id is None:
            self._interaction_id = self._bstep.recorder.new_interaction_id()
        return self._bstep.recorder.interaction("agent_turn", self._interaction_id)

    def is_visible(self) -> bool:
        return self.page.locator(".chat").count() > 0

    def state_line(self) -> str:
        return _safe_text(lambda: self.page.locator(".chat__sub").first.inner_text())

    def topic(self) -> str:
        return _safe_text(lambda: self.page.locator(".chat__topic").first.inner_text())

    def kicker(self) -> str:
        return _safe_text(lambda: self.page.locator(".guided-step__kicker").first.inner_text())

    def latest_agent_text(self) -> str:
        return _safe_text(lambda: self.page.locator(".msg.agent .bub").last.inner_text())

    def latest_founder_text(self) -> str:
        return _safe_text(lambda: self.page.locator(".msg.you .bub").last.inner_text())

    def is_typing(self) -> bool:
        return self.page.locator(".typing[role='status']").count() > 0

    def _capture(self, h: StepHandle) -> None:
        h.capture_text("chat_state", self.state_line())
        h.capture_text("waiting_text", self.state_line() if self.is_typing() else "")
        agent_text = self.latest_agent_text()
        if agent_text:
            h.capture_text("agent_reply", agent_text)

    def wait_for_state(self, pattern: str, *, timeout_ms: int = 60_000) -> None:
        """Waits on the frame's own words (spec edge cases: a 60s ceiling per agent turn, never a
        sleep) -- `pattern` matched case-insensitively against `.chat__sub`'s own text."""
        self.page.wait_for_function(
            "(pattern) => { const el = document.querySelector('.chat__sub'); "
            "return !!el && new RegExp(pattern, 'i').test(el.textContent || ''); }",
            arg=pattern, timeout=timeout_ms,
        )

    def send(self, text: str) -> None:
        """Types into the composer and sends -- C1/C2: the opening line, or a follow-up answer."""
        with self._scope():
            with self._bstep.step(f"founder types into the chat: {text[:60]!r}") as h:
                box = self.page.locator(".chat__foot textarea")
                box.fill(text)
                h.add_screenshot(self._bstep.screenshot("chat-composer-filled"))
                self.page.locator(".chat__foot button.btn.primary").click()
                self._capture(h)
                h.add_screenshot(self._bstep.screenshot("chat-sent"))

    def wait_for_understood(self, *, timeout_ms: int = 60_000) -> None:
        """C5: *Here's what we understood*."""
        self.page.locator(".understood").wait_for(state="visible", timeout=timeout_ms)

    def understood_claim(self) -> str:
        return _safe_text(lambda: self.page.locator(".understood__claim").first.inner_text())

    def save_this(self) -> None:
        """C5 -> C8: *Save this* -- the draft becomes the card's claim; the beliefs land."""
        with self._scope():
            with self._bstep.step("founder saves the understood claim") as h:
                h.capture_text("agent_reply", self.understood_claim())
                h.add_screenshot(self._bstep.screenshot("chat-understood"))
                self.page.get_by_role("button", name=re.compile(r"^save this$", re.I)).click()
                self.page.locator(".landed").wait_for(state="visible", timeout=15_000)
                h.capture_text("agent_turn_outcome", "COMPLETED")
                h.add_screenshot(self._bstep.screenshot("chat-landed"))

    def landed_claim(self) -> str:
        return _safe_text(lambda: self.page.locator(".landed__claim").first.inner_text())

    def start_over(self) -> None:
        with self._scope():
            with self._bstep.step("founder cancels and starts over") as h:
                self.page.get_by_role("button", name=re.compile("start over", re.I)).click()
                h.add_screenshot(self._bstep.screenshot("chat-start-over"))

    def draft_kept_note(self) -> str:
        """S2: the "draft kept" note shown when the founder navigates away mid-draft."""
        return _safe_text(lambda: self.page.locator(".draftnote").first.inner_text())

    def back_to_step(self) -> None:
        with self._bstep.step("founder returns to the in-progress step") as h:
            self.page.locator(".draftnote a.btn").click()
            self.page.wait_for_load_state("load")
            h.add_screenshot(self._bstep.screenshot("chat-back-to-step"))


class StageCard:
    """`src/routes/StageRoute.tsx` -- R1/R2/R4 (review/start-over/approved), E1-E3 (evidence,
    once beliefs have readings)."""

    def __init__(self, page: Page, recorder: Recorder, *, party: str = "founder"):
        self.page = page
        self._bstep = _BrowserStep(recorder, page, party)
        self._interaction_id: str | None = None

    def _scope(self):
        if self._interaction_id is None:
            self._interaction_id = self._bstep.recorder.new_interaction_id()
        return self._bstep.recorder.interaction("ui_visit", self._interaction_id)

    def open(self, stage_label: str) -> None:
        with self._scope():
            with self._bstep.step(f"founder opens the {stage_label} stage card") as h:
                self.page.locator(".card.openc").wait_for(state="visible", timeout=15_000)
                self._capture(h, stage_label)
                h.add_screenshot(self._bstep.screenshot("stage-card"))

    def _capture(self, h: StepHandle, stage_label: str) -> None:
        h.capture_text("screen", "stage")
        h.capture_text("stage", stage_label)
        h.capture_text("stage_identity", _safe_text(lambda: self.page.locator(".bet").first.inner_text()))
        h.capture_text("stage_screen", _safe_text(lambda: self.page.locator(".card.openc").first.inner_text()))

    def status_text(self) -> str:
        return _safe_text(lambda: self.page.locator(".card-top .status").first.inner_text())

    def claim_text(self) -> str:
        return _safe_text(lambda: self.page.locator("p.claim").first.inner_text())

    def counts_text(self) -> str:
        return _safe_text(lambda: self.page.locator(".counts").first.inner_text())

    def belief_headings(self) -> list[str]:
        return _safe_all_texts(self.page, ".belief .b-heading")

    def open_belief(self, heading: str) -> None:
        """Opens a belief's own drilldown (the evidence screens, E1-E3) -- clickable only once a
        drilldown exists (`button.b-top[aria-expanded]`)."""
        with self._bstep.step(f"founder opens the belief: {heading!r}") as h:
            row = self.page.locator(".belief", has_text=heading).first
            row.locator(".b-top").click()
            h.add_screenshot(self._bstep.screenshot("belief-drilldown"))

    def evidence_quotes(self, heading: str) -> list[dict]:
        """`{name, words, group}` for every quote under a belief's own drilldown, DOM order --
        `group` is "for"/"against"/"nul" (`.vgroup.for/.against/.nul`)."""
        row = self.page.locator(".belief", has_text=heading).first
        out: list[dict] = []
        for group in ("for", "against", "nul"):
            quotes = row.locator(f".vgroup.{group} .quote")
            for i in range(quotes.count()):
                q = quotes.nth(i)
                out.append({
                    "group": group,
                    "name": _safe_text(lambda q=q: q.locator(".name").inner_text()),
                    "words": _safe_text(lambda q=q: q.locator(".words").inner_text()),
                })
        return out

    def approve(self) -> None:
        """R1 -> R4: *These are right — approve*."""
        with self._scope():
            with self._bstep.step("founder approves the stage card") as h:
                self.page.get_by_role("button", name=re.compile("these are right", re.I)).click()
                self.page.get_by_text(re.compile("approved", re.I)).first.wait_for(
                    state="visible", timeout=15_000)
                h.capture_text("affordance", _safe_text(
                    lambda: self.page.locator(".approved-note").first.inner_text()))
                h.add_screenshot(self._bstep.screenshot("stage-approved"))

    def continue_to_next_step(self) -> None:
        with self._bstep.step("founder continues to the next step") as h:
            self.page.locator(".approved-note").get_by_role("link").first.click()
            self.page.wait_for_load_state("load")
            h.add_screenshot(self._bstep.screenshot("stage-continue"))

    def go_to_people(self) -> None:
        with self._bstep.step("founder goes to People") as h:
            self.page.get_by_role("button", name=re.compile("go to people", re.I)).click()
            self.page.wait_for_load_state("load")
            h.add_screenshot(self._bstep.screenshot("stage-to-people"))


class People:
    """`src/routes/PeopleRoute.tsx` -- P1-P9: role cards, the send popup, the table, the answers
    popup, the reading progress, and the toast."""

    def __init__(self, page: Page, recorder: Recorder, *, party: str = "founder"):
        self.page = page
        self._bstep = _BrowserStep(recorder, page, party)
        self._interaction_id: str | None = None

    def _scope(self):
        if self._interaction_id is None:
            self._interaction_id = self._bstep.recorder.new_interaction_id()
        return self._bstep.recorder.interaction("ui_visit", self._interaction_id)

    def open(self) -> None:
        with self._scope():
            with self._bstep.step("founder opens the People page") as h:
                self.page.wait_for_selector(".role, table.ppl", timeout=15_000)
                h.capture_text("screen", "people")
                h.capture_text("stage_screen", _safe_text(lambda: self.page.locator("body").inner_text()))
                h.capture_text("participant_names", "\n".join(self.answered_names()))
                h.add_screenshot(self._bstep.screenshot("people"))

    def role_labels(self) -> list[str]:
        return _safe_all_texts(self.page, ".role__label")

    def answered_names(self) -> list[str]:
        return _safe_all_texts(self.page, "table.ppl tbody tr td:first-child")

    def send_questions(self, role_label: str, *, name: str, about: str) -> str:
        """P1 -> P2 -> P3 -> P4: opens the send popup for `role_label`'s card, fills who, previews
        the questions, generates the link, and returns the URL exactly as the page renders it
        (never reconstructed)."""
        with self._scope():
            with self._bstep.step(f"founder sends the questions to {name} ({role_label})") as h:
                role_card = self.page.locator(".role", has_text=role_label).first
                role_card.get_by_role("button", name=re.compile("send the questions", re.I)).click()
                self.page.locator(".pop[role='dialog']").wait_for(state="visible", timeout=10_000)
                h.add_screenshot(self._bstep.screenshot("people-send-popup-who"))

                self.page.get_by_label("Their name").fill(name)
                self.page.get_by_label(re.compile("a short line", re.I)).fill(about)
                self.page.get_by_role("button", name=re.compile("next", re.I)).click()

                self.page.locator(".preview").wait_for(state="visible", timeout=10_000)
                h.add_screenshot(self._bstep.screenshot("people-send-popup-preview"))
                self.page.get_by_role("button", name=re.compile("generate", re.I)).click()

                link_box = self.page.locator("p.linkbox")
                link_box.wait_for(state="visible", timeout=10_000)
                url = _safe_text(lambda: link_box.inner_text()).strip()
                h.capture_text("invite_screen", url)
                h.add_screenshot(self._bstep.screenshot("people-send-popup-link"))

                self.page.get_by_role("button", name=re.compile("close|done", re.I)).click()
                return url

    def toggle_who(self) -> None:
        with self._bstep.step("founder switches to Who's been asked") as h:
            self.page.locator(".toggle button", has_text=re.compile("who", re.I)).click()
            h.add_screenshot(self._bstep.screenshot("people-toggle-who"))

    def table_rows(self) -> list[dict]:
        """`{person, kind, sent, their_answer, your_agent}` per row of `table.ppl`."""
        rows = self.page.locator("table.ppl tbody tr")
        out: list[dict] = []
        for i in range(rows.count()):
            cells = rows.nth(i).locator("td")
            out.append({
                "person": _safe_text(lambda c=cells: c.nth(0).inner_text()),
                "kind": _safe_text(lambda c=cells: c.nth(1).inner_text()),
                "sent": _safe_text(lambda c=cells: c.nth(2).inner_text()),
                "their_answer": _safe_text(lambda c=cells: c.nth(3).inner_text()),
                "your_agent": _safe_text(lambda c=cells: c.nth(4).inner_text()) if c.count() > 4 else "",
            })
        return out

    def open_answers(self, name: str) -> dict:
        """P9: *See <name>'s answers* -- returns `{questions: [{ask, answer}]}` read straight off
        the popup, and captures the participant's own words as `participant_page` (FR-013's
        weight-2 FIDELITY hop)."""
        with self._scope():
            with self._bstep.step(f"founder reads {name}'s answers") as h:
                self.page.get_by_role("button", name=re.compile(f"see {re.escape(name.split()[0])}", re.I)).click()
                popup = self.page.locator(".pop")
                popup.wait_for(state="visible", timeout=10_000)
                full_text = _safe_text(lambda: popup.locator(".preview").inner_text())
                h.capture_text("participant_page", full_text)
                h.add_screenshot(self._bstep.screenshot("people-answers-popup"))

                questions = popup.locator(".p-q")
                out = []
                for i in range(questions.count()):
                    q = questions.nth(i)
                    out.append({
                        "ask": _safe_text(lambda q=q: q.inner_text()),
                        "answer": _safe_text(lambda q=q: q.locator(".p-a").inner_text()),
                    })
                self.page.get_by_role("button", name=re.compile("^close$", re.I)).click()
                return {"questions": out, "text": full_text}

    def have_agent_read(self) -> None:
        """P5 -> P6 -> P7: *Have your agent read the N new answers* -- waits on the frame's own
        progress line, never a sleep, then the toast."""
        with self._scope():
            with self._bstep.step("founder has the agent read the new answers") as h:
                self.page.get_by_role("button", name=re.compile("have your agent read", re.I)).click()
                progress = self.page.locator(".bulk")
                if progress.count() > 0:
                    h.capture_text("waiting_text", _safe_text(lambda: progress.inner_text()))
                    h.add_screenshot(self._bstep.screenshot("people-reading-progress"))
                self.page.locator(".toast[role='status']").wait_for(state="visible", timeout=60_000)
                toast_text = _safe_text(lambda: self.page.locator(".toast").inner_text())
                h.capture_text("agent_reply", toast_text)
                h.add_screenshot(self._bstep.screenshot("people-reading-done-toast"))

    def toast_text(self) -> str:
        return _safe_text(lambda: self.page.locator(".toast").first.inner_text())

    def see_the_overview(self) -> None:
        with self._bstep.step("founder follows the toast to the overview") as h:
            self.page.locator(".toast").get_by_role("link").click()
            self.page.wait_for_load_state("load")
            h.add_screenshot(self._bstep.screenshot("people-toast-to-overview"))


class Brief:
    """`src/routes/BriefRoute.tsx` -- B1 (the live standing) and B2 (the print layout)."""

    def __init__(self, page: Page, recorder: Recorder, *, party: str = "founder"):
        self.page = page
        self._bstep = _BrowserStep(recorder, page, party)
        self._interaction_id: str | None = None

    def _scope(self):
        if self._interaction_id is None:
            self._interaction_id = self._bstep.recorder.new_interaction_id()
        return self._bstep.recorder.interaction("ui_visit", self._interaction_id)

    def open(self) -> None:
        with self._scope():
            with self._bstep.step("founder opens the brief") as h:
                self.page.locator(".brief-head").wait_for(state="visible", timeout=15_000)
                h.capture_text("screen", "brief")
                h.capture_text("brief", _safe_text(lambda: self.page.locator(".card.openc").first.inner_text()))
                h.add_screenshot(self._bstep.screenshot("brief"))

    def list_headings(self) -> list[str]:
        return _safe_all_texts(self.page, ".blist h5")

    def list_items(self, heading_substring: str) -> list[str]:
        blist = self.page.locator(".blist", has_text=heading_substring).first
        return blist.locator("li").all_inner_texts()

    def download(self) -> None:
        """B1 -> B2: *Download the brief* triggers `window.print()` -- captured here by emulating
        print media and screenshotting the otherwise-hidden `.doc-page`, exactly as keel-web's own
        print stylesheet renders it (spec US2 step 9)."""
        with self._scope():
            with self._bstep.step("founder downloads the brief") as h:
                self.page.emulate_media(media="print")
                doc = self.page.locator(".doc-page .doc")
                doc.wait_for(state="attached", timeout=10_000)
                h.capture_text("brief", _safe_text(lambda: doc.inner_text()))
                h.add_screenshot(self._bstep.screenshot("brief-print"))
                self.page.emulate_media(media="screen")

    def who_was_asked(self) -> list[str]:
        self.page.emulate_media(media="print")
        try:
            section = self.page.locator(".doc-page .doc")
            heading = section.get_by_text("Who was asked", exact=False)
            if heading.count() == 0:
                return []
            ul = section.locator("h2", has_text="Who was asked").locator("xpath=following-sibling::ul[1]")
            return ul.locator("li").all_inner_texts()
        finally:
            self.page.emulate_media(media="screen")


class ParticipantBrowser:
    """A stranger: opens the tool-issued link in an isolated browser context (no session with the
    founder), consents, answers, submits (design §3). The whole flow -- consent, questions,
    submit -- is one `participant_visit` interaction (spec 005 FR-009): `open` opens the scope and
    every later call folds into it.
    """

    def __init__(self, page: Page, recorder: Recorder):
        self.page = page
        self._bstep = _BrowserStep(recorder, page, party="participant")
        self._interaction_id: str | None = None

    def _capture_page_text(self, h: StepHandle) -> None:
        h.capture_text("participant_page", _safe_text(lambda: self.page.locator("body").inner_text()))

    def _scope(self):
        if self._interaction_id is None:
            self._interaction_id = self._bstep.recorder.new_interaction_id()
        return self._bstep.recorder.interaction("participant_visit", self._interaction_id)

    def open(self, url: str) -> None:
        """Opens exactly the URL the founder's People page showed -- never reconstructed."""
        with self._scope():
            with self._bstep.step("participant opens the invitation link") as h:
                self.page.goto(url, wait_until="load")
                self.page.get_by_text(re.compile("asked if you", re.I)).wait_for(
                    state="visible", timeout=10_000)
                h.add_screenshot(self._bstep.screenshot("participant-consent-screen"))
                self._capture_page_text(h)

    def start(self) -> None:
        with self._scope():
            with self._bstep.step("participant starts the survey") as h:
                self.page.get_by_role("button", name=re.compile("^start$", re.I)).click()
                self.page.wait_for_timeout(150)
                h.add_screenshot(self._bstep.screenshot("participant-questions"))
                self._capture_page_text(h)

    def answer_all(self, answer_text: str) -> None:
        """Fills each question's main answer and its disconfirming answer with the same
        supportive text, and leaves every probe blank -- a blank answer is explicitly legal
        (ParticipantController: "a blank answer is the same as an absent one -- skipped, not
        submitted"). `.q > textarea.box` (a direct-child combinator) reaches exactly those two per
        question: a probe's textarea also carries the `box` class (`"box small"`), but sits one
        level deeper, inside its own wrapper div.
        """
        with self._scope():
            with self._bstep.step("participant answers every question") as h:
                boxes = self.page.locator(".q > textarea.box").all()
                for box in boxes:
                    box.fill(answer_text)
                h.add_screenshot(self._bstep.screenshot("participant-answers-filled"))

    def answer(self, texts: list[str | None]) -> None:
        """Per-question control -- `texts[i]` fills only the i-th question's *main* box (DOM
        order). Iterates `.q` (one per question) rather than `.q > textarea.box` directly: each
        question wraps *two* such boxes (main, disconfirming), so indexing the flat box list
        one-per-question would silently misalign onto the previous question's disconfirming box.
        `None` (or any falsy string) leaves that question's main box, probes and disconfirming
        answer all blank, which the server records as no answer at all for that assumption.
        """
        with self._scope():
            with self._bstep.step("participant answers questions") as h:
                questions = self.page.locator(".q").all()
                for question, text in zip(questions, texts):
                    if text:
                        question.locator("> textarea.box").first.fill(text)
                h.add_screenshot(self._bstep.screenshot("participant-answers-filled"))

    def skip_one_question(self) -> None:
        """Spec US2 step 6: "skip one question" -- leaves the last question's main box blank
        (still legal; the server treats a blank answer as no answer for that assumption)."""
        with self._scope():
            with self._bstep.step("participant skips one question") as h:
                questions = self.page.locator(".q")
                count = questions.count()
                for i in range(count - 1):
                    questions.nth(i).locator("> textarea.box").first.fill(
                        "Answering this one, at least.")
                h.add_screenshot(self._bstep.screenshot("participant-one-skipped"))

    def submit(self) -> None:
        with self._scope():
            with self._bstep.step("participant submits the response") as h:
                self.page.get_by_role("button", name=re.compile("^submit$", re.I)).click()
                self.page.get_by_text(re.compile("thanks", re.I)).wait_for(state="visible", timeout=10_000)
                h.add_screenshot(self._bstep.screenshot("participant-thank-you"))
                self._capture_page_text(h)

    def decline(self) -> None:
        """Clicks "No thanks" on the consent screen -- client-side only: no request is ever sent."""
        with self._scope():
            with self._bstep.step("participant clicks No thanks") as h:
                self.page.get_by_role("button", name=re.compile("no thanks", re.I)).click()
                self.page.wait_for_timeout(150)
                h.add_screenshot(self._bstep.screenshot("participant-declined"))
                self._capture_page_text(h)
