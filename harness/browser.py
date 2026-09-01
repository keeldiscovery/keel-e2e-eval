"""FounderBrowser + ParticipantBrowser (T011): Playwright page objects for the founder's five
web screens and the participant survey. Every navigation opens a URL derived from the protocol's
own contract -- never a guess -- and asserts the page actually renders (FR-005).

**Judgement call -- there is no HTTP `keel_open_web`.** `OpenWebUrls`/`keel_open_web` is an
MCP-only tool (keel-cloud's own javadoc says so): the HTTP agent surface this driver speaks has
no endpoint that hands back a founder screen URL. Research explicitly ruled out adding an MCP
client just to fetch one string. So `_open_web_url` below is a straight Python port of
`OpenWebUrls.urlFor` -- the same founder-base-url, the same five path templates -- which is the
closest thing to "tool-issued" available over HTTP: it is derived from the published contract,
never hand-built to make something work.

**That port found a real bug -- since fixed.** `runs/DRIFT.md` #2 recorded that two of
`OpenWebUrls`'s five paths didn't match keel-web's actual routes (`overview` built
`.../{projectId}/overview` instead of the index route `.../{projectId}`; `stage` built
`.../{projectId}/stages/{stage}` instead of `.../{projectId}/s/{stage}`). keel-cloud's
`OpenWebUrls` now builds both paths keel-web's way (its own javadoc credits this module's DRIFT
finding). `_SCREEN_PATHS` below is updated to match, so the primary path renders on the first try
and `_note_drift`/`_ACTUAL_FALLBACK_PATHS` fire zero times on a healthy stack; the fallback
machinery itself is left in place as a safety net (and a canary -- if a DRIFT note ever fires
again, the two contracts have drifted apart again and that's worth knowing immediately, not
worked around silently).

002-eval-scoring layers interaction tagging and FID/ORIENTATION/GUIDANCE/CLARITY text capture
onto these same page objects (T008): every screen visit opens (or continues) a `ui-visit`
interaction scope, and the participant's whole flow is one `participant-page` interaction
(design §2's taxonomy) -- see `_goto_screen`'s and `ParticipantBrowser`'s docstrings.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Callable

from playwright.sync_api import Page

from harness.evidence import write_failure_capture
from harness.steps import Recorder, StepHandle

_SCREEN_PATHS = {
    "overview": "/{id}",
    "invite": "/{id}/invite",
    "invitations": "/{id}/invitations",
    "brief": "/{id}/brief",
    "stage": "/{id}/s/{stage}",
}

# Kept only as a defensive fallback + drift canary (see module docstring) -- both entries now
# equal `_SCREEN_PATHS`'s own primary path, so this fires only if the two contracts drift apart
# again in the future.
_ACTUAL_FALLBACK_PATHS = {
    "overview": "/{id}",
    "stage": "/{id}/s/{stage}",
}


def _open_web_url(base_url: str, project_id: str, screen: str, stage: str | None = None) -> str:
    """Port of keel-cloud's OpenWebUrls.urlFor -- see this module's docstring."""
    template = _SCREEN_PATHS[screen]
    path = template.format(id=project_id, stage=stage or "")
    return base_url.rstrip("/") + path


def _actual_url(base_url: str, project_id: str, screen: str, stage: str | None = None) -> str:
    template = _ACTUAL_FALLBACK_PATHS[screen]
    path = template.format(id=project_id, stage=stage or "")
    return base_url.rstrip("/") + path


class _BrowserStep:
    """Shared plumbing: numbered screenshots, and on any exception, dumping page HTML + the
    console log gathered so far into failure/ before re-raising (contracts/evidence-contract.md).
    """

    def __init__(self, recorder: Recorder, page: Page, party: str):
        self.recorder = recorder
        self.page = page
        self.party = party
        self.console_log: list[str] = []
        page.on("console", lambda msg: self.console_log.append(f"[{msg.type}] {msg.text}"))

    def screenshot(self, slug: str) -> str:
        name = self.recorder.next_screenshot_name(slug)
        self.page.screenshot(path=str(self.recorder.screenshot_path(name)), full_page=True)
        return name

    def step(self, name: str):
        return _step_cm(self, name)


def _step_cm(bstep: "_BrowserStep", name: str):
    from contextlib import contextmanager

    @contextmanager
    def cm():
        with bstep.recorder.step(name, party=bstep.party, kind="browser") as h:
            try:
                yield h
            except Exception as exc:
                # A navigation that never landed anywhere (e.g. keel-web is down entirely) can
                # make page.content() itself raise -- still write *something* to failure/page.html
                # rather than silently dropping the file the evidence contract promises.
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
    """Best-effort text capture for scoring purposes only: a selector that doesn't match (a
    screen variant with no NextBox, say) must never fail the *scenario* -- only the check that
    reads the resulting captured_text should be able to fail."""
    try:
        return getter()
    except Exception:  # noqa: BLE001 - capture is advisory, never load-bearing for the scenario
        return ""


class FounderBrowser:
    """Executes REVIEW and INVITE handoffs (design §3): opens the URL derived from
    `keel_open_web`'s own contract, reads the stage, approves; opens the invite screen, types the
    about-line, mints the link, and reads back the link the UI shows (never constructs it).

    `get_state`, if given, is `FounderAgentDriver.get_state` -- called on every screen visit so
    the resulting `ui-visit` interaction carries its own state snapshot (analysis finding A1):
    GUI-U1 ("a next-step affordance iff a need exists") reads it straight out of captured_text,
    never reaching back out to a live driver at scoring time.
    """

    def __init__(self, page: Page, web_base_url: str, recorder: Recorder,
                 *, get_state: Callable[[str], dict] | None = None):
        self.page = page
        self.base_url = web_base_url.rstrip("/")
        self._bstep = _BrowserStep(recorder, page, party="founder")
        self._get_state = get_state
        self.drift_notes_emitted: set[str] = set()
        # The ui-visit interaction most recently opened by _goto_screen -- approve_current_stage
        # and send_invite fold into it rather than opening their own, since "open a screen" and
        # "act on it" are one reviewable interaction (design §2: "one founder screen visit").
        self._current_interaction: str | None = None

    def log_in(self, web_root_base_url: str, email: str, password: str) -> None:
        """Founder-experience round 2 (design §2/§4 item 1): the founder browser earns its own
        session by driving the real `/login` screen, once, before any founder screen is opened --
        never a transplanted cookie. `/login` and `/setup` live outside the `/p/:projectId` tree
        (`AppRoutes.tsx`), so this needs the site root, not `FounderBrowser`'s own `base_url`
        (which is already `.../p`).

        **Judgement call**: driving the actual login form (rather than injecting the cookie
        `stack.auth.ensure_founder_account` already obtained via `requests`) means every scenario's
        founder context exercises the real login screen at least once, and needs no cookie-jar
        plumbing between two unrelated HTTP clients (`requests` vs. Playwright) -- the cost is one
        extra screen visit per scenario, which is cheap next to a JVM-backed discovery.
        """
        interaction_id = self._bstep.recorder.new_interaction_id()
        with self._bstep.recorder.interaction("ui-visit", interaction_id):
            with self._bstep.step("founder logs in") as h:
                root = web_root_base_url.rstrip("/")
                self.page.goto(f"{root}/login", wait_until="load")
                self.page.get_by_label(re.compile(r"^email$", re.I)).fill(email)
                self.page.get_by_label(re.compile(r"^password$", re.I)).fill(password)
                h.add_screenshot(self._bstep.screenshot("login-filled"))
                self.page.get_by_role("button", name=re.compile(r"^log in$", re.I)).click()
                self.page.wait_for_url(f"{root}/", timeout=10_000)
                h.add_screenshot(self._bstep.screenshot("login-landed"))
                h.capture_text("screen", "login")
        self._current_interaction = interaction_id

    def _note_drift(self, screen: str, tried: str, actual: str) -> None:
        if screen in self.drift_notes_emitted:
            return
        self.drift_notes_emitted.add(screen)
        self._bstep.recorder.note(
            f"DRIFT: keel_open_web's '{screen}' URL ({tried}) does not match keel-web's actual "
            f"route; falling back to {actual}",
            party="stack", ok=True,
        )

    def _capture_common(self, h: StepHandle, project_id: str, screen: str, stage: str | None) -> None:
        """Text every ui-visit interaction carries regardless of which screen it is: the
        project-identity marker (ORI-U1), a state snapshot (GUI-U1), and a generic pool of
        next-step-ish text (NextBox, status chips, primary actions) that stands in for "the
        affordance", whatever form it takes on this particular screen.
        """
        h.capture_text("identity", _safe_text(lambda: self.page.locator(".shell__brand .hint").inner_text()))
        if self._get_state is not None:
            try:
                state = self._get_state(project_id)
                h.capture_text("state", json.dumps(state))
            except Exception:  # noqa: BLE001 - capture is advisory; a state-fetch failure must
                pass          # not fail the scenario, only leave GUI-U1 unresolvable for this visit.

        affordance_parts: list[str] = []
        # `.next`/`.status`/`.review-hint` cover overview/stage/invitations' own next-step cues;
        # `button.btn.primary` covers a screen whose only "what to do next" is its own primary
        # action (the invite screen has no NextBox at all -- being on it, with a working submit
        # button, *is* the affordance for its INVITE need).
        for selector in (".next", ".status", ".review-hint", "button.btn.primary"):
            affordance_parts.extend(t.strip() for t in _safe_all_texts(self.page, selector) if t.strip())
        if affordance_parts:
            h.capture_text("affordance", "\n".join(affordance_parts))

        # Founder-experience round 2 (design §4 item 6): every founder screen renders the same
        # three-section side nav (`ProjectShell`) -- capture the locked People section's founder-
        # worded "why" whenever it is present, so policy v4's ORI-U3 can score it without a
        # dedicated screen visit of its own.
        locked_why = _safe_text(lambda: self.page.locator(".side-nav__locked-why").first.inner_text())
        if locked_why:
            h.capture_text("locked_reason", locked_why)

        # Founder-experience round 2 (design §4 item 4): the pointer-to-agent variant of the
        # next-step box (`.next.agent`) -- a sentence, deliberately never a link. Captured
        # separately from the generic `affordance` sweep above (which already folds `.next`'s text
        # in regardless of variant) so policy v4's GUI-U2 can check this specific text for the
        # absence of a URL without also catching a *clickable* pointer's own resolvable link.
        pointer_to_agent = _safe_text(lambda: self.page.locator(".next.agent").first.inner_text())
        if pointer_to_agent:
            h.capture_text("pointer_to_agent", pointer_to_agent)
            # The design's own literal promise ("a destination that is a sentence, not a link"):
            # confirmed live, not just swept from text -- no anchor exists inside the agent variant.
            if self.page.locator(".next.agent a").count() > 0:
                h.fail("the pointer-to-agent variant rendered an <a> link -- it must be a sentence only")
                raise AssertionError(h.error)

    def _goto_screen(self, project_id: str, screen: str, stage: str | None,
                      fingerprint, step_label: str):
        tool_url = _open_web_url(self.base_url, project_id, screen, stage)
        interaction_id = self._bstep.recorder.new_interaction_id()
        with self._bstep.recorder.interaction("ui-visit", interaction_id):
            with self._bstep.step(step_label) as h:
                self.page.goto(tool_url, wait_until="load")
                self.page.wait_for_timeout(150)
                rendered = fingerprint(self.page)
                if not rendered and screen in _ACTUAL_FALLBACK_PATHS:
                    actual = _actual_url(self.base_url, project_id, screen, stage)
                    self._note_drift(screen, tool_url, actual)
                    self.page.goto(actual, wait_until="load")
                    self.page.wait_for_timeout(150)
                    rendered = fingerprint(self.page)
                h.add_screenshot(self._bstep.screenshot(step_label))
                h.capture_text("screen", screen)
                if stage:
                    h.capture_text("stage", stage)
                self._capture_common(h, project_id, screen, stage)
                if screen == "stage":
                    h.capture_text("stage_identity", _safe_text(
                        lambda: self.page.locator(".card.openc .bet").first.inner_text()))
                    h.capture_text("stage_screen", _safe_text(
                        lambda: self.page.locator(".card.openc").first.inner_text()))
                elif screen == "overview":
                    # Also feeds the FIDELITY `stage_screen` hop pool for `interpretation` facts
                    # (design §3's table: verdicts show on "overview/stage screens" -- the six
                    # contract hop ids have no separate "overview" id, so this policy folds
                    # both screens' text into the one `stage_screen` key).
                    h.capture_text("stage_screen", _safe_text(lambda: self.page.locator("body").inner_text()))
                elif screen == "brief":
                    h.capture_text("brief", _safe_text(lambda: self.page.locator(".brief").first.inner_text()))
                if not rendered:
                    h.fail(f"{step_label}: page did not render the expected '{screen}' screen at "
                           f"{self.page.url}")
                    raise AssertionError(h.error)
        self._current_interaction = interaction_id

    def _continue_current_interaction(self):
        """approve_current_stage/send_invite act on the screen the last `_goto_screen` opened --
        folded into that same interaction rather than starting a new one. Falls back to a fresh
        id if called with none open (shouldn't happen in a well-formed scenario, but a scored
        step is better than a crash)."""
        interaction_id = self._current_interaction or self._bstep.recorder.new_interaction_id()
        return self._bstep.recorder.interaction("ui-visit", interaction_id)

    def open_overview(self, project_id: str) -> None:
        """Founder-experience-3-design.md §3 (keel-web commit 96c83af, "the guided walk"): the
        overview now renders ONE OF TWO shapes -- the classic three-card grid (`.card:not(.openc)`,
        round 2, untouched once every stage clears `translate.ts#guidedWalkStep`'s own test), or
        (new) the guided walk's single active step (`.guided-step`, `GuidedStep` below) while some
        stage is still unframed or framed-but-undecomposed and no OTHER stage has real review work
        waiting. Both are a legitimate render of "the overview actually loaded" -- the fingerprint
        accepts either, exactly the same "more than one legitimate render" precedent `open_brief`
        already sets for its own not-yet/ready split.
        """
        self._goto_screen(project_id, "overview", None,
                           lambda p: p.locator(".card:not(.openc)").count() >= 1
                           or p.locator(".guided-step").count() >= 1,
                           "founder opens the project overview")

    def open_stage(self, project_id: str, stage: str) -> None:
        self._goto_screen(project_id, "stage", stage,
                           lambda p: p.locator(".card.openc .bet").count() >= 1,
                           f"founder opens the {stage.lower()} stage card")

    def open_stage_evidence(self, project_id: str, stage: str) -> None:
        """Re-opens a stage once its assumptions have been interpreted, and expands every
        belief's testimony drilldown -- the only place a participant's verbatim answer renders on
        this screen (`Drilldown`'s `.quote .words`; design §3's "stage screen evidence view" hop
        for `answer` facts). Re-visiting and expanding closes that hop; without it, an approved
        stage's collapsed drilldown never puts the answer text on the rendered page at all.
        """
        self.open_stage(project_id, stage)
        with self._continue_current_interaction():
            with self._bstep.step(f"founder reviews {stage.lower()} evidence") as h:
                for button in self.page.locator(".belief button.b-top").all():
                    button.click()
                h.add_screenshot(self._bstep.screenshot(f"{stage.lower()}-evidence-expanded"))
                h.capture_text("stage_screen", _safe_text(
                    lambda: self.page.locator(".card.openc").first.inner_text()))

    def approve_current_stage(self, stage: str) -> None:
        with self._continue_current_interaction():
            with self._bstep.step(f"founder approves the {stage.lower()} stage") as h:
                button = self.page.get_by_role("button", name=re.compile("approve", re.I))
                button.wait_for(state="visible", timeout=10_000)
                h.add_screenshot(self._bstep.screenshot(f"before-approve-{stage.lower()}"))
                button.click()
                self.page.get_by_role("button", name=re.compile("approve", re.I)).wait_for(
                    state="detached", timeout=10_000)
                h.add_screenshot(self._bstep.screenshot(f"after-approve-{stage.lower()}"))

    def open_invite(self, project_id: str) -> None:
        """Opens the `invite` screen key -- founder-experience design §5: both `invite` and
        `invitations` now route to the same merged **People** screen (`keel-web`'s
        `PeopleRoute.tsx`; wire unchanged, so `keel_open_web`'s old screen names never 404). This
        one opens compose-focused (`composeFocus`), matching what `/invite` always meant. The
        compose card (`.card.openc h1`, "Invite someone to answer") renders unconditionally --
        before any role exists, before the gate opens, after it -- so this fingerprint holds at
        every moment a scenario might visit, including S-008's wrong-moment visits.
        """
        self._goto_screen(project_id, "invite", None,
                           lambda p: p.locator(".card.openc h1").count() >= 1,
                           "founder opens the People screen (invite)")

    def open_people(self, project_id: str) -> None:
        """Opens the `invitations` screen key -- the same merged People screen as `open_invite`,
        without the compose-scroll focus (replaces the old standalone invitations screen; design
        §5's "one screen, organized by role"). Same always-true fingerprint as `open_invite` --
        both screen keys render the identical component."""
        self._goto_screen(project_id, "invitations", None,
                           lambda p: p.locator(".card.openc h1").count() >= 1,
                           "founder opens the People screen (roles)")

    def people_role_cards(self) -> list[dict[str, str]]:
        """`{label, counts, aim}` per role card (`.card.people-role`, design §5's mockup) --
        standing-assertion and S-008 material: read directly off the currently-open People page,
        no reconstruction."""
        cards = self.page.locator(".card.people-role")
        rows = []
        for i in range(cards.count()):
            card = cards.nth(i)
            rows.append({
                "label": _safe_text(lambda c=card: c.locator(".bet").first.inner_text()),
                "counts": _safe_text(lambda c=card: c.locator(".counts").first.inner_text()),
                "aim": _safe_text(lambda c=card: c.locator(".hint").first.inner_text()),
            })
        return rows

    def role_picker_options(self) -> list[dict[str, str | bool]]:
        """`{text, disabled}` for every `<option>` in the People screen's role picker (`#invite-
        role`) -- the domain's own per-role invite-time gate (`Project.invite`'s `blockedBy`),
        rendered as-is (`PeopleRoute.tsx`'s own comment: this is NOT re-derived against the newer
        approve-all-then-invite gate). Used by the standing invite-gate assertion to confirm a
        blocked role's option text is founder-worded (`"... — approve <stage> first"`), never a
        raw enum."""
        options = self.page.locator("#invite-role option")
        rows = []
        for i in range(options.count()):
            option = options.nth(i)
            rows.append({
                "text": _safe_text(lambda o=option: o.inner_text()),
                "disabled": bool(option.get_attribute("disabled") is not None),
            })
        return rows

    def follow_display_url(self, url: str, project_id: str) -> None:
        """Follows a URL exactly as carried in a wire `display` sentence -- never reconstructed via
        `_open_web_url` -- and asserts it renders the founder shell (founder-experience design §2.3:
        every sentence that points at a screen now embeds its own door; policy v3's `GUI-A3` checks
        the sentence is well-formed, and this is the click-through no static sweep can stand in
        for -- the "every door must open" rule, extended from screen navigation to a sentence's own
        URL). Opens its own `ui-visit` interaction, tagged with a generic 'display-door' screen
        name rather than one of the five known ones, since the URL's own path is what is under
        test here, not a scenario-chosen screen key.
        """
        interaction_id = self._bstep.recorder.new_interaction_id()
        with self._bstep.recorder.interaction("ui-visit", interaction_id):
            with self._bstep.step(f"founder follows the door a display sentence carried: {url}") as h:
                self.page.goto(url, wait_until="load")
                self.page.wait_for_timeout(150)
                rendered = self.page.locator(".shell").count() >= 1
                h.add_screenshot(self._bstep.screenshot("display-door-opened"))
                h.capture_text("screen", "display-door")
                self._capture_common(h, project_id, "display-door", None)
                if not rendered:
                    h.fail(f"the URL a display sentence carried did not render the founder shell: {url}")
                    raise AssertionError(h.error)
        self._current_interaction = interaction_id

    def send_invite(self, role_label: str, person_name: str, about_line: str) -> str:
        """Picks the role, types the name and about-line, sends, and reads back the link the UI
        shows -- that string, not anything this harness builds, is what the participant opens.
        """
        with self._continue_current_interaction():
            with self._bstep.step(f"founder invites {person_name} ({role_label})") as h:
                self.page.get_by_label(re.compile("who are the questions for", re.I)).select_option(
                    label=role_label)
                # `select_option(label=role_label)` only succeeds because `role_label` is exactly
                # one rendered <option>'s visible text -- the `invite_screen` FIDELITY hop for the
                # role-label fact.
                h.capture_text("invite_screen", role_label)
                self.page.get_by_label(re.compile("who are you sending it to", re.I)).fill(person_name)
                about_field = self.page.get_by_label(re.compile("what the top of their page will say", re.I))
                about_field.fill(about_line)
                # The `invite_screen` FIDELITY hop for the about-line fact: the about-line never
                # renders as static page text on this screen (only as this field's value), so the
                # value itself is the closest thing to "what this screen shows" for that fact.
                h.capture_text("invite_screen", _safe_text(about_field.input_value))
                h.add_screenshot(self._bstep.screenshot("invite-form-filled"))
                self.page.get_by_role("button", name=re.compile("send invite", re.I)).click()
                link_box = self.page.locator(".linkbox")
                link_box.wait_for(state="visible", timeout=10_000)
                url = link_box.inner_text().strip()
                h.record_wire(None, {"invite_url_shown_by_ui": url})
                h.add_screenshot(self._bstep.screenshot("invite-link-shown"))
                if not url:
                    h.fail("invite screen showed an empty link")
                    raise AssertionError("invite screen showed an empty link")
                return url

    def open_invitations(self, project_id: str) -> None:
        """Deprecated name, kept so call sites written before the People merge still read
        sensibly -- identical to `open_people` (design §5: "wire unchanged", one component behind
        both screen keys)."""
        self.open_people(project_id)

    def open_brief(self, project_id: str) -> None:
        """The `brief` screen key renders one of two things (founder-experience design §4 item 3):
        the brief itself (`.brief`) once `READY_TO_BUILD`, or -- before that -- a designed "not yet"
        quiet state (`.card.openc .hint`, keel-web's `BRIEF_NOT_YET_TEXT`), never a raw 409. Both
        count as a legitimate render; S-008's wrong-moment visit is exactly the second case."""
        self._goto_screen(project_id, "brief", None,
                           lambda p: p.locator(".card.openc .brief").count() >= 1
                           or p.locator(".card.openc .hint").count() >= 1,
                           "founder opens the brief")

    def continue_current_interaction(self):
        """Public alias for `_continue_current_interaction` -- `GuidedStep` below folds its own
        actions into whichever `ui-visit` the founder's last screen visit opened, the same
        "look at the screen, act on it is one interaction" precedent `approve_current_stage`/
        `send_invite` already set for this class's own methods."""
        return self._continue_current_interaction()


class GuidedStep:
    """The guided walk's single active step (founder-experience-3-design.md §3; keel-web commit
    96c83af): `OverviewRoute` renders this INSTEAD OF the classic three-card grid + next-step
    pointer whenever some stage is still unframed or framed-but-undecomposed and no OTHER stage has
    real review work waiting (`translate.ts#guidedWalkStep`'s own guard, live-confirmed against
    `evals/test_s001_smoke.py`'s own choreography: CREATE frames PROBLEM as a side effect, so the
    walk is already showing PROBLEM's own landed claim before this harness ever issues `FRAME` for
    SOLUTION or COMMERCIAL).

    Two phases (`step.phase`, mirrored here as `is_landed()`): `"ask"` -- a question, and either a
    first-answer composer (`ask`, no exchange yet) or the step-scoped overlay (`reply`, once one
    exists) -- and `"landed"` -- the claim rendered in place (`landed_claim`), with Continue/Reopen
    buttons. `continue_()` is purely a client-side acknowledgement (there is no wire action for "I'm
    done looking at this for now"); it never posts anything.

    **Judgement call, live-confirmed**: only a FOUNDER turn can ever carry a `step` tag (spec 017
    FR-003, `RelayService#postFounderTurn`) -- `POST /v2/agent/relay` always stores `step=null`
    (`RelayService#appendAgentTurn`'s own draft call), so an agent's reply, however it answers a
    step's own question, never shows up inside THIS overlay's own `turnsForStep` filter -- only in
    `HistoryDrawer`'s unfiltered transcript. Recorded as a real product gap, not worked around here
    (`runs/DRIFT.md`): this harness only ever asserts the FOUNDER's own line lands inside the step
    exchange, never an agent reply.

    Rides `FounderBrowser`'s already-open `ui-visit` interaction (`continue_current_interaction`) --
    "the overview is showing this step, and the founder acts on it" is one reviewable interaction,
    not a second kind of visit.
    """

    def __init__(self, founder: "FounderBrowser"):
        self.page = founder.page
        self._founder = founder
        self._bstep = founder._bstep

    def is_visible(self) -> bool:
        return self.page.locator(".guided-step").count() > 0

    def is_landed(self) -> bool:
        return self.page.locator(".guided-step .landed").count() > 0

    def kicker(self) -> str:
        return _safe_text(lambda: self.page.locator(".guided-step__kicker").first.inner_text())

    def question(self) -> str:
        return _safe_text(lambda: self.page.locator(".guided-step__question").first.inner_text())

    def landed_claim(self) -> str:
        """The claim rendered in place once the step has landed (`.landed__claim`) -- empty string
        while the step is still in its `"ask"` phase (nothing has landed yet)."""
        return _safe_text(lambda: self.page.locator(".landed__claim").first.inner_text())

    def ask(self, text: str) -> None:
        """Types into the first-answer composer (no exchange exists yet for this step) and submits
        -- the real product path (`GuidedStep.tsx`'s own `postTurn.mutate({text, step: step.stage})`)
        tags the resulting relay turn with this step's own stage, never something this harness sets
        itself."""
        with self._founder.continue_current_interaction():
            with self._bstep.step(f"founder answers the guided step: {text[:60]!r}") as h:
                box = self.page.locator(".guided-step__first-answer textarea")
                box.fill(text)
                h.add_screenshot(self._bstep.screenshot("guided-step-first-answer-filled"))
                self.page.get_by_role("button", name=re.compile("send to your agent", re.I)).click()
                h.capture_text("guided_step_sent", text)

    def reply(self, text: str) -> None:
        """Types into the overlay's own reply composer -- only rendered once a step-scoped exchange
        already exists (`ask` was called, or the step already carries turns from an earlier visit)."""
        with self._founder.continue_current_interaction():
            with self._bstep.step(f"founder replies inside the guided step: {text[:60]!r}") as h:
                box = self.page.locator(".overlay.ov .reply textarea")
                box.fill(text)
                h.add_screenshot(self._bstep.screenshot("guided-step-reply-filled"))
                self.page.get_by_role("button", name=re.compile(r"^send$", re.I)).click()
                h.capture_text("guided_step_sent", text)

    def wait_for_step_turns(self, n: int, *, timeout_ms: int = 15_000) -> None:
        """Polls until at least `n` turns render inside the step's own overlay -- the composer's
        `postTurn` mutation and the read-back refetch are both async, so a caller reading
        `step_turns()` right after `ask`/`reply` needs this rather than a fixed sleep."""
        self.page.wait_for_function(
            "(n) => document.querySelectorAll('.overlay.ov .turn').length >= n", arg=n, timeout=timeout_ms)

    def step_turns(self) -> list[dict]:
        """`{author, text}` per rendered turn inside the step's own overlay, DOM order -- `author`
        read off the alternating alignment class (`turn you` / `turn agent`), since the overlay
        carries no machine-readable author attribute of its own."""
        rows = self.page.locator(".overlay.ov .turn")
        out: list[dict] = []
        for i in range(rows.count()):
            row = rows.nth(i)
            classes = (row.get_attribute("class") or "").split()
            text = _safe_text(lambda r=row: r.inner_text())
            out.append({"author": "founder" if "you" in classes else "agent", "text": text})
        return out

    def continue_(self) -> None:
        """The landed phase's own "Continue" button -- purely client-side (there is no wire action
        for "I'm done looking at this for now"); advances the walk to the next stage still needing
        attention, or hands the overview back to the classic cards once none remain. Waits for the
        landed claim itself to detach (the same "don't just click and hope" discipline
        `approve_current_stage` already applies to its own button) before returning, so a caller
        reading the next step's own kicker/question right after this call never races the
        re-render."""
        with self._founder.continue_current_interaction():
            with self._bstep.step("founder continues past the landed claim") as h:
                self.page.get_by_role("button", name=re.compile(r"^continue$", re.I)).click()
                self.page.locator(".guided-step .landed").wait_for(state="detached", timeout=10_000)
                h.add_screenshot(self._bstep.screenshot("guided-step-continued"))


class ChatPane:
    """The relay's chat pane page object (design §12 item 1; keel-web commit 07745c2): turns,
    kickers, playback tables, the presence banner, the thinking state, the composer. Rides the
    SAME Playwright `Page` as the founder's project shell -- `ProjectShell` mounts `ChatPane` as a
    persistent right rail alongside every founder route (confirmed live: it never unmounts on
    navigation between overview/stage/people/brief), so this class never navigates anywhere
    itself; a caller opens whatever founder screen it likes first via `FounderBrowser`.

    Reads its own `chat-visit` interaction scope (design §12 item 5's own home for the chat-
    surface sweeps: `harness/rubric.py`'s `CLA-C1`/`ORI-C1`/`GUI-C1`) -- distinct from `ui-visit`,
    since the pane's own state is orthogonal to whichever screen happens to be open beside it.

    **STALE as of keel-web commit 96c83af (the guided walk)**: the right rail this class reads
    (`.chat-rail`) is gone from every founder route -- `ProjectShell` mounts `HistoryDrawer` (below)
    along the bottom instead. Left in place, unmodified, only because `evals/test_s011_relay.py`
    and `evals/test_shaping_gauntlet.py` still import and drive it (out of this round's scope --
    S-001 + the shared recipes/page objects it needs, only; see `runs/DRIFT.md`); those two will
    need the same `HistoryDrawer` treatment `test_s001_smoke.py` got here before they can pass
    against a live stack again.
    """

    AUTHOR_KICKERS = {"YOU": "founder", "YOUR KEEL AGENT": "agent"}

    def __init__(self, page: Page, recorder: Recorder, *, presence_reader: Callable[[], dict] | None = None):
        self.page = page
        self._bstep = _BrowserStep(recorder, page, party="founder")
        self._presence_reader = presence_reader

    def expand(self) -> None:
        """The rail collapses to a single toggle button (`.chat-rail--collapsed`) -- every read or
        composer action needs it open first. A no-op if it already is."""
        rail = self.page.locator(".chat-rail")
        if rail.count() and "chat-rail--collapsed" in (rail.first.get_attribute("class") or ""):
            self.page.locator(".chat-rail__toggle").first.click()
            self.page.wait_for_timeout(100)

    def turns(self) -> list[dict]:
        """`{kicker, text, playback}` per rendered `.chat-turn`, in DOM (chronological) order --
        the substrate S-011's own ordering-under-interleaving proof reads."""
        rows = self.page.locator(".chat-turn")
        out: list[dict] = []
        for i in range(rows.count()):
            row = rows.nth(i)
            kicker = _safe_text(lambda r=row: r.locator(".chat-turn__kicker").first.inner_text())
            is_playback = row.locator(".chat-playback").count() > 0
            if is_playback:
                text = _safe_text(lambda r=row: r.locator(".chat-playback").first.inner_text())
            else:
                text = _safe_text(lambda r=row: r.locator(".chat-turn__text").first.inner_text())
            out.append({"kicker": kicker, "text": text, "playback": is_playback})
        return out

    def playback_table_rows(self) -> list[list[str]]:
        """Cell text for every row of the first `table.invites` rendered inside a `.chat-playback`
        block (`RolesRecordedTable` -- the one playback shape that renders an actual `<table>`
        element; a `beliefs`-shaped or bullet-list-shaped playback renders div/li structure
        instead, never a `<table>` -- this feature's own live-confirmed finding, see
        `evals/test_s001_smoke.py`'s module docstring for the judgement call it drove)."""
        table = self.page.locator(".chat-playback table.invites").first
        if table.count() == 0:
            return []
        rows = table.locator("tr")
        out: list[list[str]] = []
        for i in range(rows.count()):
            cells = rows.nth(i).locator("th, td")
            out.append([cells.nth(j).inner_text().strip() for j in range(cells.count())])
        return out

    def wait_for_presence(self, *, connected: bool, timeout_ms: int = 20_000) -> None:
        """Polls until the pane's own rendered banner state (present iff disconnected) agrees
        with `connected`, TWICE in a row -- the pane refetches presence on its own interval, not
        on every render, so a caller checking right after a wire-level change (a poll/post, or a
        real silence) needs to wait for that refetch rather than assume it already landed.
        Debounced (two consecutive matching reads, not just one) because the query's own initial
        loading state renders no banner at all -- indistinguishable, on a single read, from
        "connected" -- and live-confirmed to otherwise report a false "connected" a moment before
        the real fetch resolves and the disconnected banner actually appears."""
        self.expand()
        deadline = time.monotonic() + timeout_ms / 1000
        stable_hits = 0
        while time.monotonic() < deadline:
            shown = bool(self.presence_banner_text())
            matches = (not shown) if connected else shown
            stable_hits = stable_hits + 1 if matches else 0
            if stable_hits >= 2:
                return
            self.page.wait_for_timeout(500)
        raise TimeoutError(
            f"the chat pane's presence banner never stabilized to connected={connected} "
            f"within {timeout_ms}ms")

    def presence_banner_text(self) -> str:
        """Empty when connected (the design's own "connected silently" rule -- absence of banner
        is the positive signal); the disconnected copy otherwise.

        **Bug found and fixed live (2026-08-31, S-011's own first full run)**: this used to be
        `_safe_text(lambda: self.page.locator(".chat-presence").first.inner_text())` -- but
        `.first.inner_text()` on a locator matching zero elements does not return "" immediately;
        Playwright auto-waits for the element to attach, and while connected (the element
        legitimately never renders at all) that wait blocks for many seconds. Confirmed live: the
        wait was long enough, on its own, to starve this harness's own poll/post calls of the CPU
        time to run during it -- which let the relay's own presence genuinely go stale mid-wait,
        so the call would "eventually" return the disconnected banner text once it finally
        rendered, having itself caused the very disconnect it was checking for. A `.count()` guard
        first (the same pattern every other optional element in this file already uses, e.g.
        `.next.agent`/`.side-nav__locked-why` above) makes the absent case return "" in
        microseconds, exactly as a presence check needs.
        """
        banner = self.page.locator(".chat-presence")
        return _safe_text(lambda: banner.first.inner_text()) if banner.count() else ""

    def thinking_visible(self) -> bool:
        return self.page.locator(".chat-thinking").count() > 0

    def agent_turn_links(self) -> list[str]:
        """Every `href` inside a rendered agent turn's own text -- the every-door-opens rule's
        chat-surface extension (design §12 item 5): `GUI-C1` sweeps these for well-formedness the
        same way `GUI-A3` sweeps a wire `display`'s own URL; a scenario wanting the live click-
        through demonstration itself calls `click_agent_turn_link` below."""
        links = self.page.locator(".chat-turn__text a")
        return [links.nth(i).get_attribute("href") or "" for i in range(links.count())]

    def click_agent_turn_link(self, href: str, project_id: str) -> None:
        """The live click-through no static sweep can stand in for (`FounderBrowser.
        follow_display_url`'s own precedent, extended to a chat turn's own link): opens `href`
        exactly as rendered and asserts the founder shell actually renders."""
        interaction_id = self._bstep.recorder.new_interaction_id()
        with self._bstep.recorder.interaction("ui-visit", interaction_id):
            with self._bstep.step(f"founder follows a door an agent turn carried: {href}") as h:
                self.page.goto(href, wait_until="load")
                self.page.wait_for_timeout(150)
                rendered = self.page.locator(".shell").count() >= 1
                h.add_screenshot(self._bstep.screenshot("chat-turn-door-opened"))
                h.capture_text("screen", "chat-turn-door")
                if not rendered:
                    h.fail(f"the URL a chat turn carried did not render the founder shell: {href}")
                    raise AssertionError(h.error)

    def send(self, text: str) -> None:
        """Types into the composer and clicks Send (rather than relying on the Enter-submits
        binding -- deterministic either way, this is the one that never risks a stray Shift)."""
        with self._bstep.step(f"founder types into the chat composer: {text[:60]!r}") as h:
            self.expand()
            box = self.page.locator(".chat-composer__input")
            box.fill(text)
            h.add_screenshot(self._bstep.screenshot("chat-composer-filled"))
            self.page.get_by_role("button", name=re.compile(r"^send$", re.I)).click()
            h.capture_text("chat_sent", text)

    def wait_for_turn_count(self, n: int, *, timeout_ms: int = 15_000) -> None:
        """Polls until at least `n` `.chat-turn` elements have rendered -- the composer's own
        `postTurn` mutation and the pane's own poll are both async, so a caller reading turns
        right after `send()`/a relay post needs this rather than a fixed sleep."""
        self.expand()
        self.page.wait_for_function(
            "(n) => document.querySelectorAll('.chat-turn').length >= n", arg=n, timeout=timeout_ms)

    def capture(self, h: StepHandle) -> None:
        """Folds the pane's current rendered state into the caller's own step -- `chat_turns`/
        `chat_playback_table`/`chat_presence_banner`/`chat_turn_links` are policy v5's own hop ids
        (`harness/rubric.py`'s `_chat_visit_checks`)."""
        self.expand()
        turns = self.turns()
        h.capture_text("chat_turns", "\n".join(f"{t['kicker']}: {t['text']}" for t in turns if t["text"]))
        table_rows = self.playback_table_rows()
        if table_rows:
            h.capture_text("chat_playback_table", "\n".join(" | ".join(r) for r in table_rows))
        h.capture_text("chat_presence_banner", self.presence_banner_text())
        if self._presence_reader is not None:
            try:
                presence = self._presence_reader()
                h.capture_text("chat_presence_state", json.dumps(presence))
            except Exception:  # noqa: BLE001 - capture is advisory, never load-bearing
                pass
        links = self.agent_turn_links()
        if links:
            h.capture_text("chat_turn_links", "\n".join(links))

    def read(self) -> dict:
        """Opens (or continues) a `chat-visit` interaction, captures the pane's rendered state for
        policy v5's sweeps, and returns `{turns, playback_rows, presence_banner}` for the caller's
        own live assertions (e.g. "the INTRODUCE_ROLES playback renders as a table")."""
        interaction_id = self._bstep.recorder.new_interaction_id()
        with self._bstep.recorder.interaction("chat-visit", interaction_id):
            with self._bstep.step("founder reads the chat pane") as h:
                self.capture(h)
                h.add_screenshot(self._bstep.screenshot("chat-pane"))
        return {"turns": self.turns(), "playback_rows": self.playback_table_rows(),
                "presence_banner": self.presence_banner_text()}


class HistoryDrawer:
    """The relay's history, collapsed along the bottom of the founder shell (founder-experience-
    3-design.md §3; keel-web commit 96c83af: "the rail does not die; it demotes"). `ProjectShell`
    mounts this ONE drawer regardless of which founder route is on screen (overview -- classic
    cards or the guided walk's own step -- a stage, brief, or people), exactly the same
    "never unmounts on navigation" precedent `ChatPane` set for the right rail it replaces; this
    class never navigates anywhere itself either.

    Shows EVERY turn, never step-filtered (`GuidedStep`'s own overlay is the step-scoped view;
    this is the plain, complete transcript) -- including the server-authored `event` turns spec 017
    FR-001 introduced (`kind: "event"`, `author: "system"`), rendered as green-tick lines
    (`.chat-turn--event`) recording something the founder just did through the founder API (an
    approval, an invitation created) rather than said.

    Reads its own `chat-visit` interaction scope, unchanged in NAME from `ChatPane`'s own (policy
    v5's `CLA-C1`/`ORI-C1`/`GUI-C1` sweep the same `chat_turns`/`chat_playback_table`/
    `chat_presence_banner`/`chat_turn_links` capture keys by string, regardless of which page
    object wrote them -- renaming the class changes nothing about how a run scores).
    """

    def __init__(self, page: Page, recorder: Recorder, *, presence_reader: Callable[[], dict] | None = None):
        self.page = page
        self._bstep = _BrowserStep(recorder, page, party="founder")
        self._presence_reader = presence_reader

    def expand(self) -> None:
        """The drawer's panel only renders while `expanded` (its own bottom bar's toggle button is
        always visible either way) -- a no-op if the panel is already showing."""
        if self.page.locator(".history-drawer__panel").count() == 0:
            self.page.locator(".history-drawer__toggle").first.click()
            self.page.wait_for_timeout(100)

    def turns(self) -> list[dict]:
        """`{kicker, author, kind, text, playback}` per rendered `.history-drawer__turns .chat-turn`
        row, DOM (chronological) order. An event row (`.chat-turn--event`) reports
        `author="system"`, `kind="event"`, `kicker=""` -- the green-tick line spec 017 FR-001
        introduced; a founder/agent row's `author` is read off the visible marker (the `YOU` kicker
        vs. the Keel mark, which carries no text kicker of its own)."""
        rows = self.page.locator(".history-drawer__turns .chat-turn")
        out: list[dict] = []
        for i in range(rows.count()):
            row = rows.nth(i)
            classes = (row.get_attribute("class") or "").split()
            if "chat-turn--event" in classes:
                text = _safe_text(lambda r=row: r.locator(
                    "span:not(.chat-turn--event__tick):not(.chat-turn__time)").first.inner_text())
                out.append({"kicker": "", "author": "system", "kind": "event", "text": text, "playback": False})
                continue
            kicker_el = row.locator(".chat-turn__kicker")
            is_founder = kicker_el.count() > 0
            kicker = _safe_text(lambda e=kicker_el: e.first.inner_text()) if is_founder else ""
            is_playback = row.locator(".chat-playback").count() > 0
            if is_playback:
                text = _safe_text(lambda r=row: r.locator(".chat-playback").first.inner_text())
            else:
                text = _safe_text(lambda r=row: r.locator(".chat-turn__text").first.inner_text())
            out.append({"kicker": kicker, "author": "founder" if is_founder else "agent",
                        "kind": "playback" if is_playback else "message", "text": text,
                        "playback": is_playback})
        return out

    def playback_table_rows(self) -> list[list[str]]:
        """Same `table.invites`-inside-`.chat-playback` shape `ChatPane` reads (`RolesRecordedTable`
        is unchanged by the guided walk) -- scoped to the drawer's own turn list."""
        table = self.page.locator(".history-drawer__turns .chat-playback table.invites").first
        if table.count() == 0:
            return []
        rows = table.locator("tr")
        out: list[list[str]] = []
        for i in range(rows.count()):
            cells = rows.nth(i).locator("th, td")
            out.append([cells.nth(j).inner_text().strip() for j in range(cells.count())])
        return out

    def wait_for_presence(self, *, connected: bool, timeout_ms: int = 20_000) -> None:
        """Identical debounce discipline to `ChatPane.wait_for_presence` (same live-confirmed bug
        this mirrors: a `.count()` guard before ever calling `.inner_text()`, and two consecutive
        matching reads before declaring the banner stable) -- see that method's own docstring."""
        self.expand()
        deadline = time.monotonic() + timeout_ms / 1000
        stable_hits = 0
        while time.monotonic() < deadline:
            shown = bool(self.presence_banner_text())
            matches = (not shown) if connected else shown
            stable_hits = stable_hits + 1 if matches else 0
            if stable_hits >= 2:
                return
            self.page.wait_for_timeout(500)
        raise TimeoutError(
            f"the drawer's presence banner never stabilized to connected={connected} "
            f"within {timeout_ms}ms")

    def presence_banner_text(self) -> str:
        banner = self.page.locator(".chat-presence")
        return _safe_text(lambda: banner.first.inner_text()) if banner.count() else ""

    def thinking_visible(self) -> bool:
        return self.page.locator(".chat-thinking").count() > 0

    def agent_turn_links(self) -> list[str]:
        links = self.page.locator(".history-drawer__turns .chat-turn__text a")
        return [links.nth(i).get_attribute("href") or "" for i in range(links.count())]

    def click_agent_turn_link(self, href: str, project_id: str) -> None:
        """The live click-through no static sweep can stand in for -- see
        `FounderBrowser.follow_display_url`'s own precedent."""
        interaction_id = self._bstep.recorder.new_interaction_id()
        with self._bstep.recorder.interaction("ui-visit", interaction_id):
            with self._bstep.step(f"founder follows a door a history turn carried: {href}") as h:
                self.page.goto(href, wait_until="load")
                self.page.wait_for_timeout(150)
                rendered = self.page.locator(".shell").count() >= 1
                h.add_screenshot(self._bstep.screenshot("history-turn-door-opened"))
                h.capture_text("screen", "chat-turn-door")
                if not rendered:
                    h.fail(f"the URL a history turn carried did not render the founder shell: {href}")
                    raise AssertionError(h.error)

    def send(self, text: str) -> None:
        """Types into the drawer's own general composer and clicks Send -- untagged (no `step`),
        exactly like a pre-006 relay turn (`HistoryDrawer.tsx`'s own `postTurn.mutate({text})`)."""
        with self._bstep.step(f"founder types into the drawer's composer: {text[:60]!r}") as h:
            self.expand()
            box = self.page.locator(".chat-composer__input")
            box.fill(text)
            h.add_screenshot(self._bstep.screenshot("drawer-composer-filled"))
            self.page.get_by_role("button", name=re.compile(r"^send$", re.I)).click()
            h.capture_text("chat_sent", text)

    def wait_for_turn_count(self, n: int, *, timeout_ms: int = 15_000) -> None:
        """Polls until at least `n` `.history-drawer__turns .chat-turn` elements have rendered --
        mirrors `ChatPane.wait_for_turn_count`'s own async-mutation rationale."""
        self.expand()
        self.page.wait_for_function(
            "(n) => document.querySelectorAll('.history-drawer__turns .chat-turn').length >= n",
            arg=n, timeout=timeout_ms)

    def capture(self, h: StepHandle) -> None:
        """Folds the drawer's current rendered state into the caller's own step -- same capture
        keys as `ChatPane.capture` (policy v5's own hop ids); an event row's kicker is empty, so it
        reads as `SYSTEM: <text>` in `chat_turns`."""
        self.expand()
        turns = self.turns()
        h.capture_text("chat_turns", "\n".join(
            f"{t['kicker'] or t['author'].upper()}: {t['text']}" for t in turns if t["text"]))
        table_rows = self.playback_table_rows()
        if table_rows:
            h.capture_text("chat_playback_table", "\n".join(" | ".join(r) for r in table_rows))
        h.capture_text("chat_presence_banner", self.presence_banner_text())
        if self._presence_reader is not None:
            try:
                presence = self._presence_reader()
                h.capture_text("chat_presence_state", json.dumps(presence))
            except Exception:  # noqa: BLE001 - capture is advisory, never load-bearing
                pass
        links = self.agent_turn_links()
        if links:
            h.capture_text("chat_turn_links", "\n".join(links))

    def read(self) -> dict:
        """Opens (or continues) a `chat-visit` interaction, captures the drawer's rendered state
        for policy v5's sweeps, and returns `{turns, playback_rows, presence_banner}` -- same shape
        as `ChatPane.read`."""
        interaction_id = self._bstep.recorder.new_interaction_id()
        with self._bstep.recorder.interaction("chat-visit", interaction_id):
            with self._bstep.step("founder reads the history drawer") as h:
                self.capture(h)
                h.add_screenshot(self._bstep.screenshot("history-drawer"))
        return {"turns": self.turns(), "playback_rows": self.playback_table_rows(),
                "presence_banner": self.presence_banner_text()}


def _safe_all_texts(page: Page, selector: str) -> list[str]:
    try:
        return page.locator(selector).all_inner_texts()
    except Exception:  # noqa: BLE001 - capture is advisory, never load-bearing for the scenario
        return []


class ParticipantBrowser:
    """A stranger: opens the tool-issued link in an isolated browser context (no session with the
    founder), consents, answers, submits (design §3). The whole flow -- consent, questions,
    submit -- is one `participant-page` interaction (design §2's taxonomy): `open` opens the
    scope and every later call folds into it.
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
        return self._bstep.recorder.interaction("participant-page", self._interaction_id)

    def open(self, url: str) -> None:
        """Opens exactly the URL the founder's invite screen showed -- never reconstructed."""
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
        supportive text (S-001 answers supportively throughout), and leaves every probe blank --
        a blank answer is explicitly legal (ParticipantController: "a blank answer is the same
        as an absent one -- skipped, not submitted"). `.q > textarea.box` (a direct-child
        combinator) reaches exactly those two per question: a probe's textarea also carries the
        `box` class (`"box small"`), but sits one level deeper, inside its own wrapper div.
        """
        with self._scope():
            with self._bstep.step("participant answers every question") as h:
                boxes = self.page.locator(".q > textarea.box").all()
                for box in boxes:
                    box.fill(answer_text)
                h.add_screenshot(self._bstep.screenshot("participant-answers-filled"))

    def answer(self, texts: list[str | None]) -> None:
        """003-eval-set (T006): per-question control -- `texts[i]` fills only the i-th question's
        *main* box (DOM order, matching `Invitation.asks()`'s stage-then-risk-then-introducedAt
        ordering, per api-design.md's `form()` assembly). Iterates `.q` (one per question) rather
        than `.q > textarea.box` directly: each question wraps *two* such boxes (main,
        disconfirming -- `answer_all`'s own docstring), so indexing the flat box list one-per-
        question would silently misalign onto the previous question's disconfirming box. `None`
        (or any falsy string) leaves that question's main box, probes and disconfirming answer all
        blank, which the server records as no answer at all for that assumption
        (ParticipantController: "a blank answer is the same as an absent one"). Lets a scenario
        give one participant supportive evidence on one belief while skipping another entirely
        (S-002/S-003's two-question commercial link; S-005's opinions-only sweep), or hand a
        single participant one combined sentence that the scenario's own `interpret_payload` later
        splits into both a supporting and a contradicting claim (S-004's divided person -- the
        split is an INTERPRET-time decision, not a textarea one; see that scenario's module
        docstring).
        """
        with self._scope():
            with self._bstep.step("participant answers questions") as h:
                questions = self.page.locator(".q").all()
                for question, text in zip(questions, texts):
                    if text:
                        question.locator("> textarea.box").first.fill(text)
                h.add_screenshot(self._bstep.screenshot("participant-answers-filled"))

    def submit(self) -> None:
        with self._scope():
            with self._bstep.step("participant submits the response") as h:
                self.page.get_by_role("button", name=re.compile("^submit$", re.I)).click()
                self.page.get_by_text(re.compile("thanks", re.I)).wait_for(state="visible", timeout=10_000)
                h.add_screenshot(self._bstep.screenshot("participant-thank-you"))
                self._capture_page_text(h)

    def decline(self) -> None:
        """003-eval-set (T006, S-006, journey §2.1): clicks "No thanks" on the consent screen --
        client-side only (`ParticipantRoute.tsx`'s `OpenForm`): no request is ever sent, so nothing
        reaches the founder as an answer. Captures the resulting "No problem" page.
        """
        with self._scope():
            with self._bstep.step("participant clicks No thanks") as h:
                self.page.get_by_role("button", name=re.compile("no thanks", re.I)).click()
                self.page.wait_for_timeout(150)
                h.add_screenshot(self._bstep.screenshot("participant-declined"))
                self._capture_page_text(h)

    def submit_expect_notice(self) -> None:
        """003-eval-set (T006, S-005): submits when every question was left blank -- the server
        refuses gently (422, `ParticipantController.respond`: "Every question was left blank, so
        there's nothing to send") and the page renders an inline `.stale`-styled notice *on the
        same answering screen* rather than advancing to "thanks" -- distinct from `submit()`,
        which waits for the thank-you text and would time out here.
        """
        with self._scope():
            with self._bstep.step("participant submits with everything skipped") as h:
                self.page.get_by_role("button", name=re.compile("^submit$", re.I)).click()
                self.page.wait_for_timeout(300)
                h.add_screenshot(self._bstep.screenshot("participant-all-skipped-notice"))
                self._capture_page_text(h)

    def open_expect_notice(self, url: str) -> None:
        """003-eval-set (T006, S-002 §2.4 / already-answered): opens a link that will *not* render
        the fresh consent screen -- gone stale (410, the founder reframed since sending it) or
        already answered (200, `ALREADY_ANSWERED`) -- capturing whatever the page shows instead.
        Distinct from `open()`, which waits for the consent screen's "asked if you" text and would
        time out on either of these paths.

        Scoring note: this still opens a `participant-page` interaction, so the generic rubric's
        `ORI-P1`/`GUI-P1` (consent intro found / reached a successful submit) will read as failed
        against it -- expected and self-explanatory in the scorecard (neither a stale nor an
        already-answered page is a consent flow), not a product finding.
        """
        with self._scope():
            with self._bstep.step("participant opens a link that is no longer a fresh consent screen") as h:
                self.page.goto(url, wait_until="load")
                self.page.wait_for_timeout(200)
                h.add_screenshot(self._bstep.screenshot("participant-link-notice"))
                self._capture_page_text(h)
