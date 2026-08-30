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
        self._goto_screen(project_id, "overview", None,
                           lambda p: p.locator(".card:not(.openc)").count() >= 1,
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
        self._goto_screen(project_id, "invite", None,
                           lambda p: p.locator(".card.openc h1").count() >= 1,
                           "founder opens the invite screen")

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
        self._goto_screen(project_id, "invitations", None,
                           lambda p: p.locator("table.invites").count() > 0
                           or p.get_by_text(re.compile("nobody has been invited", re.I)).count() > 0,
                           "founder opens the invitations screen")

    def open_brief(self, project_id: str) -> None:
        self._goto_screen(project_id, "brief", None,
                           lambda p: p.locator(".card.openc .brief").count() >= 1,
                           "founder opens the brief")


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
