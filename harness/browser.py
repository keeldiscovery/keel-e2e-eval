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

**That port found a real bug.** Two of its five paths do not match keel-web's actual routes
(`src/routes/AppRoutes.tsx`):

- `overview` builds `.../{projectId}/overview`, but keel-web's overview is the *index* route --
  `/p/:projectId` with no trailing segment at all.
- `stage` builds `.../{projectId}/stages/{stage}`, but keel-web's route is `s/:stage`, i.e.
  `.../{projectId}/s/{stage}`.

Both were verified against a running stack (see `runs/DRIFT.md`), not just read off the source:
opening the OpenWebUrls-shaped URL leaves the inner `<Routes>` with nothing to match, rendering a
blank content area inside `ProjectShell`'s chrome. `invite`, `invitations` and `brief` all match
exactly. This module tries the tool's own contract first, and only falls back to keel-web's actual
route -- recording a DRIFT note each time -- because a scenario that cannot reach the stage screen
at all cannot exercise REVIEW, and reporting a bug is this repo's job, not stopping at the first
one it finds (design §6).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from playwright.sync_api import Page

from harness.evidence import write_failure_capture
from harness.steps import Recorder

_SCREEN_PATHS = {
    "overview": "/{id}/overview",
    "invite": "/{id}/invite",
    "invitations": "/{id}/invitations",
    "brief": "/{id}/brief",
    "stage": "/{id}/stages/{stage}",
}

# keel-web's actual routes (AppRoutes.tsx), used only as the drift fallback for the two screens
# where OpenWebUrls disagrees with them.
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


class FounderBrowser:
    """Executes REVIEW and INVITE handoffs (design §3): opens the URL derived from
    `keel_open_web`'s own contract, reads the stage, approves; opens the invite screen, types the
    about-line, mints the link, and reads back the link the UI shows (never constructs it).
    """

    def __init__(self, page: Page, web_base_url: str, recorder: Recorder):
        self.page = page
        self.base_url = web_base_url.rstrip("/")
        self._bstep = _BrowserStep(recorder, page, party="founder")
        self.drift_notes_emitted: set[str] = set()

    def _note_drift(self, screen: str, tried: str, actual: str) -> None:
        if screen in self.drift_notes_emitted:
            return
        self.drift_notes_emitted.add(screen)
        self._bstep.recorder.note(
            f"DRIFT: keel_open_web's '{screen}' URL ({tried}) does not match keel-web's actual "
            f"route; falling back to {actual}",
            party="stack", ok=True,
        )

    def _goto_screen(self, project_id: str, screen: str, stage: str | None,
                      fingerprint, step_label: str):
        tool_url = _open_web_url(self.base_url, project_id, screen, stage)
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
            if not rendered:
                h.fail(f"{step_label}: page did not render the expected '{screen}' screen at "
                       f"{self.page.url}")
                raise AssertionError(h.error)

    def open_overview(self, project_id: str) -> None:
        self._goto_screen(project_id, "overview", None,
                           lambda p: p.locator(".card:not(.openc)").count() >= 1,
                           "founder opens the project overview")

    def open_stage(self, project_id: str, stage: str) -> None:
        self._goto_screen(project_id, "stage", stage,
                           lambda p: p.locator(".card.openc .bet").count() >= 1,
                           f"founder opens the {stage.lower()} stage card")

    def approve_current_stage(self, stage: str) -> None:
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
        with self._bstep.step(f"founder invites {person_name} ({role_label})") as h:
            self.page.get_by_label(re.compile("who are the questions for", re.I)).select_option(
                label=role_label)
            self.page.get_by_label(re.compile("who are you sending it to", re.I)).fill(person_name)
            self.page.get_by_label(re.compile("what the top of their page will say", re.I)).fill(about_line)
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


class ParticipantBrowser:
    """A stranger: opens the tool-issued link in an isolated browser context (no session with the
    founder), consents, answers, submits (design §3).
    """

    def __init__(self, page: Page, recorder: Recorder):
        self.page = page
        self._bstep = _BrowserStep(recorder, page, party="participant")

    def open(self, url: str) -> None:
        """Opens exactly the URL the founder's invite screen showed -- never reconstructed."""
        with self._bstep.step("participant opens the invitation link") as h:
            self.page.goto(url, wait_until="load")
            self.page.get_by_text(re.compile("asked if you", re.I)).wait_for(
                state="visible", timeout=10_000)
            h.add_screenshot(self._bstep.screenshot("participant-consent-screen"))

    def start(self) -> None:
        with self._bstep.step("participant starts the survey") as h:
            self.page.get_by_role("button", name=re.compile("^start$", re.I)).click()
            self.page.wait_for_timeout(150)
            h.add_screenshot(self._bstep.screenshot("participant-questions"))

    def answer_all(self, answer_text: str) -> None:
        """Fills each question's main answer and its disconfirming answer with the same
        supportive text (S-001 answers supportively throughout), and leaves every probe blank --
        a blank answer is explicitly legal (ParticipantController: "a blank answer is the same
        as an absent one -- skipped, not submitted"). `.q > textarea.box` (a direct-child
        combinator) reaches exactly those two per question: a probe's textarea also carries the
        `box` class (`"box small"`), but sits one level deeper, inside its own wrapper div.
        """
        with self._bstep.step("participant answers every question") as h:
            boxes = self.page.locator(".q > textarea.box").all()
            for box in boxes:
                box.fill(answer_text)
            h.add_screenshot(self._bstep.screenshot("participant-answers-filled"))

    def submit(self) -> None:
        with self._bstep.step("participant submits the response") as h:
            self.page.get_by_role("button", name=re.compile("^submit$", re.I)).click()
            self.page.get_by_text(re.compile("thanks", re.I)).wait_for(state="visible", timeout=10_000)
            h.add_screenshot(self._bstep.screenshot("participant-thank-you"))
