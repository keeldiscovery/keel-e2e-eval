"""Playwright page objects for the measured-beliefs screens (spec 010 T015-T022, on top of spec
005-connect-stack FR-008).

**What spec 010 added, and why this layer earns its keep** (plan.md's Complexity Tracking):
keel-web has exactly **one** `data-testid` in its whole tree -- `median-tick` on the strip's median
line -- so every other handle is a role, an `aria-label`, a heading or a stable class. Inline
selectors are what specs 001-008 did with four screens, and they were already the thing most often
broken; with a popover, a modal, an SVG strip and a print page, concentrating them here is the only
way one keel-web pass does not redden seven scenarios at once. **Page objects hold selectors and
never assertions**, so the rule against abstraction for its own sake still bites.

New here: `MarketStep`, `ReviewCard`, `CorrectionChat`, `Overview`, `OpenedCard`, `SaidBox`,
`AnswersModal`, `PrintPage`, and `ParticipantPage` (which replaces `ParticipantBrowser` -- there is
no consent screen and no *Start* any more; the form is the page). **`Brief` is deleted** with the
route it named: keel-web has no `BriefRoute.tsx` and no `/p/:id/brief`, and the `brief` hop retires
with it (policy v8 FR-026). `StageCard` stays for the walk's own approve/continue moments, which
are unchanged.

The original round-5 note follows.

Playwright page objects for the round-5 screens (spec 005-connect-stack FR-008): `Auth`
(setup/login), `Connect` (device-approval frames B/C/G, plus A/D/E/F), `Landing` (L1-L4), `Shell`
(agent line, side nav with status words), `Chat` (C1-C8: bubbles, composer, confirmation card),
`StageCard` (R1/R2/R4, E1-E3), `People` (P1-P9: toggle, role cards, popup steps, table rows,
answers popup, progress line, toast), `Brief` (B1/B2), `ParticipantBrowser` (unchanged in role,
selectors updated). Method names/signatures below are the exact contract `evals/
test_s001_smoke.py` (the one scenario) drives -- read in full before this rewrite, since it is the
one real consumer of this module and settles every naming/return-shape question FR-008 leaves
open.

Selectors are taken from keel-web's real source under `../keel-web/src` -- routes and components
read in full -- cross-checked against `../keel-web/tests/visual/states/*.ts`, keel-web's own
visual-regression fixtures and the most direct evidence of what the built DOM actually looks like
for a named state. This app has no `data-testid` anywhere: locators are Playwright's
accessible-name finders (`get_by_role`, `get_by_label`, `get_by_text`) plus the real CSS classes.

**Constructor shape, uniform**: every class takes `(page, recorder, base_url)` except `Shell` and
`ParticipantBrowser`, which take `(page, recorder)` -- neither ever builds a top-level URL from
scratch (`Shell` only ever clicks something already on the page; `ParticipantBrowser` is always
handed a complete URL to visit -- the founder's own send popup, or a scenario's own fixture link).
`Connect.open` is likewise always handed a complete URL (the runtime's own verification URI) --
its own stored `base_url` exists only so its constructor shape matches every other class's.

**Interaction scoping is split deliberately, matching how the scenario actually drives this file**
(FR-009): `Auth`, `Landing`, and `Connect` record plain steps and open no interaction scope of
their own -- the scenario reads their results directly, in line, wrapping the moments it wants
scored in its own `with recorder.interaction(...):` blocks (the arrival walk -- login, the gated
landing, the device approval, the reconnected landing -- and the rare screen it reads without a
page object at all, the overview's own three-card standing). `Chat` tags every one of its own
steps `agent_turn` (the whole guided-step exchange -- composing, waiting, confirming -- is watched
entirely through the frame's own state line, never a wire call). `Shell`, `StageCard`, `People`,
`Brief`, and `ParticipantBrowser` tag their own steps `ui_visit`/`participant_visit` and fold
every later call on the same instance into the interaction its own first action opened
(`_scope()`'s reuse of `self._interaction_id`, the "look at the screen, act on it, is one
reviewable interaction" precedent the pre-round-5 harness set).

**A client-routed SPA transition is not a navigation.** Every route change this file drives after
the first `page.goto` is a React Router push, not a full page load -- `page.wait_for_load_state
("load")` after a click never resolves (nothing to load), and Playwright's own `page.wait_for_url`
listens for a *future* navigation event, which can race a route change that already happened by
the time the listener attaches. Every wait below is therefore either a positive element/text wait
for the destination screen's own rendered word (preferred), or `_wait_for_url_change`, a small
same-thread poll of `page.url` that checks the *current* value first -- never a bare sleep.

Every method records a step and screenshots on entry (spec FR-008; a pure getter that neither
navigates nor acts -- `state_line()`, `claim()`, `table_rows()`, and the like -- does not, matching
every class's own consistent split between "reads" and "actions"), after waiting on
`document.fonts.ready` (spec edge cases, matching keel-web's own visual tests, `tests/visual/
harness.ts`'s `driveTo`); on any exception the step dumps page HTML + the console log gathered so
far into `failure/` before re-raising (`harness/evidence.write_failure_capture`).

**Judgement call -- `state` JSON / GUI-U1 / CLA-U3.** `harness/rubric.py`'s `_need_exists`/
`_cla_u3` read a `captured_text["state"]` JSON shaped `{stages: [{stage, need, needLabel, approved,
verdictLabel}], awaitingInterpretation}` -- `needLabel`/`verdictLabel` are fields the now-retired
agent-protocol surface composed (grepping keel-cloud confirms both names live only in
`protocol/AgentDtos.java`/`protocol/FounderVoice.java`, the retired HTTP surface `harness/
driver.py` used to call). keel-web's own `/overview` wire response (confirmed against every
`tests/visual/states/*.ts` fixture) carries a different, unlabelled shape (`type` not `stage`, no
`needLabel`/`verdictLabel` -- those words are composed client-side by `lib/translate.ts`'s own
`betStatus`/`beliefStatus`, never sent as such). No live HTTP surface hands back rubric.py's exact
shape any more, and guessing at `need`/`needLabel` values would risk scoring on fabricated data --
worse than the check simply skipping, which is what it already does with no `state` captured
(rubric's own "don't guess" stance). A `state_reader` keyword stays available on the methods that
could use it (mirroring the pre-round-5 `FounderBrowser` shape) so a future caller can wire one
up, but none is passed by the current scenario -- GUI-U1/CLA-U3 read as skipped, not failed, for
every interaction this file records.

**Judgement call -- GUI-U2 (the pointer-to-agent sentence).** `.next.agent` only ever renders
inside `GuidedStep.tsx`'s landed phase, and every one of `Chat`'s own steps is tagged `agent_turn`
(above) -- a type `harness/rubric.py`'s `evaluate()` never runs any check against. `Shell.
capture_common` still captures `pointer_to_agent` when it is present (so a *future* caller that
re-visits the landed state under an explicit `ui_visit` wrapper is covered), but no `ui_visit`
interaction in this scenario's own choreography ever re-reads the landed state, so GUI-U2 has
nothing to check today. Recorded here rather than silently patched around.
"""

from __future__ import annotations

import json
import re
import time
from contextlib import contextmanager
from typing import Any, Callable
from urllib.parse import urlsplit

from playwright.sync_api import Page

from harness.evidence import write_failure_capture
from harness.steps import Recorder, StepHandle

StateReader = Callable[[str], dict]


# --------------------------------------------------------------------------------------- helpers

def _origin(page: Page) -> str:
    """The scheme+host+port of wherever `page` currently is -- the fallback a class without an
    explicit `base_url` uses to build a full URL (see `_split_recorder_and_base`)."""
    parts = urlsplit(page.url)
    return f"{parts.scheme}://{parts.netloc}"


def _split_recorder_and_base(args: tuple, page: Page) -> tuple[Recorder, str]:
    """This module's real callers have, at different points, constructed these classes as
    `(page, recorder)`, `(page, recorder, base_url)`, and `(page, base_url, recorder)` -- the
    order of the last two arguments moved more than once while `evals/test_s001_smoke.py` (the
    one scenario) was still being written against this same rewrite. Rather than betting on
    whichever shape happens to be on disk at any one moment, every constructor below accepts any
    of the three: the `Recorder` instance is told apart from a base-url string by type, and a
    missing base url falls back to `_origin(page)` (the scheme+host+port `page` is already on --
    always correct once the caller has navigated anywhere at all). Flagged in the task report as
    a genuine, unresolved instability in this module's own real callers, not one this file
    introduces.
    """
    recorder: Recorder | None = None
    base_url: str | None = None
    for arg in args:
        if isinstance(arg, str):
            base_url = arg
        elif arg is not None:
            recorder = arg
    if recorder is None:
        raise TypeError("expected a Recorder among the constructor arguments")
    return recorder, (base_url.rstrip("/") if base_url else _origin(page))


def _wait_for_url_change(page: Page, predicate: Callable[[str], bool], *, timeout_ms: int = 15_000) -> None:
    """Polls `page.url` in Python rather than Playwright's own `wait_for_url` -- that method
    listens for a *future* navigation event and can race a client-side route change that already
    happened by the time it attaches its listener (this app is a client-routed SPA: every route
    change after the first `page.goto` is a React Router push, not a browser navigation). Checks
    the current URL immediately, then every 100ms."""
    deadline = time.monotonic() + timeout_ms / 1000
    while True:
        if predicate(page.url):
            return
        if time.monotonic() >= deadline:
            raise TimeoutError(f"URL never matched the expected condition within {timeout_ms}ms "
                                f"(last seen: {page.url!r})")
        page.wait_for_timeout(100)


def _safe_text(getter: Callable[[], str]) -> str:
    """Best-effort text capture for scoring purposes only: a selector that doesn't match (a screen
    variant that doesn't render this element at all) must never fail the *scenario* -- only the
    check that reads the resulting captured_text should be able to fail."""
    try:
        return getter()
    except Exception:  # noqa: BLE001 - capture is advisory, never load-bearing for the scenario
        return ""


# What a founder reads, word-separated. `innerText` runs two adjacent inline elements together --
# `<b>…not minutes</b><span class="db">deal-breaker</span>` comes back as `minutesdeal-breaker`,
# which the CLARITY sweep then reads as a camelCase field name on a screen that shows nothing of
# the sort (live-confirmed: `runs/20260907T143953Z-s001-smoke`, `CLA-U2 violations=['minutesDEAL',
# 'seatASKED']`). CSS puts visible space between them; this walker puts it back, by joining each
# element's own text nodes rather than concatenating them. It also picks up SVG `<text>`, which
# `innerText` drops entirely -- the band label lives there.
_SCREEN_TEXT_JS = r"""(el) => {
  if (!el) return "";
  const parts = [];
  const walk = (node) => {
    for (const child of node.childNodes) {
      if (child.nodeType === 3) {
        const text = child.textContent.replace(/\s+/g, ' ').trim();
        if (text) parts.push(text);
      } else if (child.nodeType === 1) {
        if (child.hidden) continue;
        walk(child);
      }
    }
  };
  walk(el);
  return parts.join(' ');
}"""


def _screen_text(page, selector: str) -> str:
    """The rendered words of one region, separated (see `_SCREEN_TEXT_JS`)."""
    try:
        locator = page.locator(selector).first
        if locator.count() == 0:
            return ""
        return locator.evaluate(_SCREEN_TEXT_JS) or ""
    except Exception:  # noqa: BLE001 - a region that will not evaluate reads as no text
        return ""


def _safe_all_texts(page, selector: str) -> list[str]:
    try:
        return [t.strip() for t in page.locator(selector).all_inner_texts() if t.strip()]
    except Exception:  # noqa: BLE001 - capture is advisory, never load-bearing for the scenario
        return []


def _capture_state(h: StepHandle, project_id: str, state_reader: StateReader | None) -> None:
    if state_reader is None:
        return
    try:
        h.capture_text("state", json.dumps(state_reader(project_id)))
    except Exception:  # noqa: BLE001 - capture is advisory; a state-fetch failure must not fail
        pass          # the scenario, only leave GUI-U1/CLA-U3 unresolvable for this visit.


# ---------------------------------------------------------------------------------- base plumbing

class _BrowserStep:
    """Shared plumbing: numbered screenshots (waiting on `document.fonts.ready` first),
    console-log capture, and on any exception, dumping page HTML + the console log gathered so far
    into `failure/` before re-raising (contracts/evidence-contract.md)."""

    def __init__(self, recorder: Recorder, page: Page, party: str):
        self.recorder = recorder
        self.page = page
        self.party = party
        self.console_log: list[str] = []
        page.on("console", lambda msg: self.console_log.append(f"[{msg.type}] {msg.text}"))

    def screenshot(self, slug: str) -> str:
        try:
            self.page.evaluate("document.fonts.ready")
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
            except Exception as exc:  # noqa: BLE001 - re-raised after capturing failure evidence
                try:
                    page_html = bstep.page.content()
                except Exception as content_exc:  # noqa: BLE001 - best-effort, never mask the real error
                    page_html = (f"<!-- page.content() unavailable: {content_exc} -->\n"
                                 f"<!-- the browser step failed with: {exc} -->")
                write_failure_capture(bstep.recorder.run_dir, page_html=page_html,
                                       console_lines=list(bstep.console_log))
                raise

    return cm()


# ------------------------------------------------------------------------------------------- Auth

class Auth:
    """`/setup` and `/login` (design §2.3/§2.5/§2.6; `routes/auth/SetupRoute.tsx`/
    `LoginRoute.tsx`).

    **Accepts its `recorder`/`base_url` arguments in either order** -- same reasoning, and same
    fix, as `Landing`'s own docstring below: told apart by type (a `Recorder` vs. a plain string)
    rather than by position, since this file's own callers have not agreed on one order.
    """

    def __init__(self, page: Page, arg2: Any, arg3: Any, *, party: str = "founder"):
        self.page = page
        recorder, base_url = (arg3, arg2) if isinstance(arg2, str) else (arg2, arg3)
        self.base_url = base_url.rstrip("/")
        self._bstep = _BrowserStep(recorder, page, party)

    def set_up(self, *, name: str, email: str, password: str) -> None:
        """Fills and submits the setup form; ends on `ScreenA` ("Your founder account is ready")
        -- setup no longer shows an agent key (FR-005). Rubric's ORI-U1 is explicitly exempt for
        `screen="setup"` (`harness/rubric.py`'s `_ui_visit_checks`)."""
        with self._bstep.step("founder sets up the founder account") as h:
            self.page.goto(f"{self.base_url}/setup", wait_until="load")
            self.page.locator(".auth-title").wait_for(state="visible", timeout=15_000)
            self.page.get_by_label("Your name").fill(name)
            self.page.get_by_label("Email").fill(email)
            self.page.get_by_label("Password").fill(password)
            h.add_screenshot(self._bstep.screenshot("setup-filled"))
            self.page.get_by_role("button", name="Create account").click()
            self.page.get_by_text("Your founder account is ready").wait_for(
                state="visible", timeout=15_000)
            h.capture_text("screen", "setup")
            h.add_screenshot(self._bstep.screenshot("setup-done"))

    def log_in(self, *, email: str, password: str) -> None:
        """Drives the real `/login` screen -- never a transplanted cookie."""
        with self._bstep.step("founder logs in") as h:
            self.page.goto(f"{self.base_url}/login", wait_until="load")
            self.page.locator(".auth-title").wait_for(state="visible", timeout=15_000)
            self.page.get_by_label("Email").fill(email)
            self.page.get_by_label("Password").fill(password)
            h.add_screenshot(self._bstep.screenshot("login-filled"))
            self.page.get_by_role("button", name="Log in").click()
            # This transition re-renders in place -- no URL change, no full navigation (post-login
            # routes to Connect frame A/H when no live agent is bound yet or one already is) -- so
            # wait for the auth card's own heading to move on from "Log in", or vanish entirely
            # (the landing has none).
            self.page.wait_for_function(
                "() => { const h = document.querySelector('.auth-title'); "
                "return !h || !/^log in$/i.test((h.textContent || '').trim()); }",
                timeout=15_000,
            )
            h.capture_text("screen", "login")
            h.add_screenshot(self._bstep.screenshot("logged-in"))


# ---------------------------------------------------------------------------------------- Connect

_CONNECT_FRAME_TITLES = {
    "F": "Log in to approve a device",
    "B": "A device wants to act as your agent",
    "C": "Device approved",
    "G": "Device denied",
    "E": "That code has run out",
}


class Connect:
    """The device-authorization screens (`routes/connect/ConnectRoute.tsx`, design §2.2-§2.4):
    B (decide)/C (approved)/G (denied) per FR-008, plus honest detection of the incidental states
    (A, D, E, F) even though the smoke's own happy path only ever lands on B. `base_url` is stored
    only for constructor-shape consistency -- `open()` always visits a complete URL handed to it
    (the runtime's own verification URI), never one built from `base_url`."""

    def __init__(self, page: Page, *args: Any, party: str = "founder"):
        self.page = page
        recorder, self.base_url = _split_recorder_and_base(args, page)
        self._bstep = _BrowserStep(recorder, page, party)

    def open(self, verification_uri: str) -> str:
        """Navigates to exactly the URL `harness.connect.start_runtime_via_skill` handed back
        (never reconstructed) and identifies which frame rendered. Returns one of
        `"A"|"B"|"C"|"D"|"E"|"F"|"G"|"?"`."""
        with self._bstep.step("founder opens the device-approval link") as h:
            self.page.goto(verification_uri, wait_until="load")
            self.page.locator(".auth-title").wait_for(state="visible", timeout=15_000)
            title = _safe_text(lambda: self.page.locator(".auth-title").first.inner_text())
            frame = next((k for k, v in _CONNECT_FRAME_TITLES.items() if v in title), None)
            if frame is None:
                lowered = title.lower()
                frame = "A" if ("connect your agent" in lowered or "account is ready" in lowered) else "?"
            h.capture_text("screen", "connect")
            h.capture_text("stage_screen", title)
            h.add_screenshot(self._bstep.screenshot(f"connect-{frame.lower()}"))
        return frame

    def user_code(self) -> str:
        return _safe_text(lambda: self.page.locator("div.code").first.inner_text())

    def approve(self) -> None:
        """Frame B's *Approve this device* -- the direct, no-judgement action the constitution's
        new row names (screen-review-design.md §11: "an errand, not a judgement")."""
        with self._bstep.step("founder approves the device") as h:
            self.page.get_by_role("button", name="Approve this device").click()
            self.page.get_by_text(re.compile("device approved", re.I)).wait_for(
                state="visible", timeout=15_000)
            h.add_screenshot(self._bstep.screenshot("connect-b-approved"))

    def wait_for_connected(self, *, timeout_s: float = 30) -> None:
        """Frame C's own truthful state line, polled until it reads *Agent connected* (US2
        acceptance scenario 1: "within 30 s `/v2/me` reads `agent.connected: true` and the page
        reads *Agent connected*") -- waited on the rendered word, never a fixed sleep;
        `useMe({poll: true})`'s own polling is what flips it, not a reload."""
        with self._bstep.step("the runtime finishes connecting") as h:
            # Not a bare text match: "No agent connected" contains "agent connected" as a
            # case-insensitive substring, so `get_by_text(re.compile("agent connected", re.I))`
            # matches the *disconnected* state line too (a real false-positive, live-confirmed).
            # `.dot.good` is the unambiguous positive signal (`app.css`: `.dot.good{background:
            # var(--keel-good)}`, the same class `AgentLine`/Landing's own agentline use).
            self.page.locator(".stateline .dot.good").wait_for(
                state="visible", timeout=timeout_s * 1000)
            h.capture_text("stage_screen", _safe_text(
                lambda: self.page.locator(".stateline").first.inner_text()))
            h.add_screenshot(self._bstep.screenshot("connect-agent-connected"))

    def deny(self) -> None:
        """Frame B's *Deny* -- terminal (screen-review-design.md §2.2): a denied code cannot be
        re-approved; the way back is running `keel connect` again for a fresh one."""
        with self._bstep.step("founder denies the device") as h:
            self.page.get_by_role("button", name="Deny").click()
            self.page.get_by_text(re.compile("device denied", re.I)).wait_for(
                state="visible", timeout=15_000)
            h.add_screenshot(self._bstep.screenshot("connect-g-denied"))

    def go_to_projects(self) -> None:
        """The one button onward from C, G, or H -- *Go to your projects →* -- landing on `/`.
        A `<button>`, not an `<a>` (live-confirmed: `get_by_role("link", ...)` timed out against
        the real DOM), even though it reads like a link -- this screen navigates via router push
        from a click handler, not an anchor tag."""
        with self._bstep.step("founder returns to the project list") as h:
            self.page.get_by_role("button", name=re.compile("go to your projects", re.I)).click()
            _wait_for_url_change(self.page, lambda url: "/connect" not in url)
            self.page.locator(".hello").wait_for(state="visible", timeout=15_000)
            h.add_screenshot(self._bstep.screenshot("connect-back-to-landing"))


# ---------------------------------------------------------------------------------------- Landing

class Landing:
    """`/` -- four shapes decided by two facts, never told to this harness in advance: does the
    founder have any project, and is the agent connected right now (design §3; `landing/
    LandingRoute.tsx`). `visit()` reads whichever of L1-L4 rendered off the DOM.

    **Accepts its `recorder`/`base_url` arguments in either order** (same as `Auth` above): told
    apart by type (a `Recorder` vs. a plain string) rather than by position, since this file's
    own callers have not agreed on one order.
    """

    def __init__(self, page: Page, arg2: Any, arg3: Any, *, party: str = "founder"):
        self.page = page
        recorder, base_url = (arg3, arg2) if isinstance(arg2, str) else (arg2, arg3)
        self.base_url = base_url.rstrip("/")
        self._bstep = _BrowserStep(recorder, page, party)

    def visit(self) -> dict[str, Any]:
        """Navigates to `/` and reads whichever of L1-L4 rendered. The very first landing visit(s)
        -- before any project exists at all -- are the spec's own `arrival` moment (FR-009); this
        method always captures `arrival_display` (harmless, and simply unread, once a project
        exists and the scenario tags the surrounding interaction `ui_visit` instead) so
        `harness/rubric.py`'s `CLA-AR1` finds it whichever way the caller has scoped the call.
        Returns `{frame, has_projects, agent_connected}`.
        """
        with self._bstep.step("founder visits the landing") as h:
            self.page.goto(f"{self.base_url}/", wait_until="load")
            self.page.locator(".hello").wait_for(state="visible", timeout=15_000)
            has_projects = self.page.locator(".project-list").count() > 0
            agent_connected = self.page.locator(".agentline .st-good").count() > 0
            greeting = _safe_text(lambda: self.page.locator(".hello").first.inner_text())
            h.capture_text("screen", "landing")
            h.capture_text("identity", greeting)
            h.capture_text("arrival_display", greeting)
            affordance = _safe_all_texts(self.page, ".list-head, .project-row")
            if affordance:
                h.capture_text("affordance", "\n".join(affordance))
            h.add_screenshot(self._bstep.screenshot("landing"))
        if has_projects:
            frame = "L3" if agent_connected else "L4"
        else:
            frame = "L1" if agent_connected else "L2"
        return {"frame": frame, "has_projects": has_projects, "agent_connected": agent_connected}

    def agent_line_text(self) -> str:
        return _safe_text(lambda: self.page.locator(".agentline").first.inner_text())

    def is_gated(self) -> bool:
        """L2: no agent connected yet, no project can be started."""
        return self.page.locator(".gate").count() > 0

    def new_project_locked_reason(self) -> dict[str, Any]:
        """L4 (spec 006-agent-optional, mockups `landing-mock.html` frame L4): the list-head's own
        `.locked` card -- *New project* rendered `disabled`, with its own reason (`.locked .why`,
        `LANDING_LOCKED_REASON`) beside it, once projects exist but no agent is connected.
        `{present, enabled, reason}` -- `present=False` when `.locked` never rendered at all (L1/
        L3, agent connected: plain *New project*, never disabled)."""
        locked = self.page.locator(".locked")
        if locked.count() == 0:
            return {"present": False, "enabled": True, "reason": ""}
        button = locked.get_by_role("button", name=re.compile(r"^new project$", re.I))
        enabled = button.count() > 0 and button.first.is_enabled()
        reason = _safe_text(lambda: locked.locator(".why").first.inner_text())
        return {"present": True, "enabled": enabled, "reason": reason}

    def new_project_enabled(self) -> bool:
        """L3/L1 (agent connected): the plain, unlocked *New project* button -- true once step 8
        (spec 006-agent-optional: "and now a new project is allowed again") is reached."""
        button = self.page.get_by_role("button", name=re.compile(r"^new project$", re.I))
        return button.count() > 0 and button.first.is_enabled()

    def log_out(self) -> None:
        """The landing's own *Log out* -- closes the keel session (spec 006-agent-optional US1
        step 1; spec 020 US3: logging out closes the keel session, the runtime keeps polling on
        its own until this scenario's own `harness.connect.stop_runtime` stops it)."""
        with self._bstep.step("founder logs out") as h:
            self.page.get_by_role("button", name=re.compile(r"^log out$", re.I)).click()
            self.page.locator(".auth-title").wait_for(state="visible", timeout=15_000)
            h.add_screenshot(self._bstep.screenshot("landing-logged-out"))

    def open_connect_from_gate(self) -> None:
        """L2's gate card -- *I have a code* -- opens the bare `/connect` entry (frame D)."""
        with self._bstep.step("founder clicks I have a code from the gated landing") as h:
            self.page.get_by_role("link", name=re.compile("i have a code", re.I)).click()
            _wait_for_url_change(self.page, lambda url: "/connect" in url)
            h.add_screenshot(self._bstep.screenshot("landing-gate-to-connect"))

    def name_project(self, name: str) -> None:
        """L1/L3's own step 1 (`CreateProjectStep.tsx`): the name, and then *Save and continue*.

        **It no longer creates the project.** Spec 013 put the market step between naming and
        starting -- the market is what decides units, register and currency, and it is chosen
        before anything is framed (design §3.8) -- so `POST /v2/projects` now carries
        `{name, market}` and fires from `MarketStep.start()`. This method leaves the founder on
        that step; `MarketStep` returns the project id.
        """
        with self._bstep.step(f"founder names the project: {name!r}") as h:
            box = self.page.locator(".guided-step").get_by_role("textbox")
            if box.count() == 0:
                box = self.page.get_by_label(re.compile("what should we call this project", re.I))
            box.fill(name)
            h.add_screenshot(self._bstep.screenshot("landing-name-filled"))
            self.page.get_by_role("button", name=re.compile("save and continue", re.I)).click()
            self.page.locator(".guided-step select").first.wait_for(state="visible", timeout=15_000)
            h.capture_text("screen", "market")
            h.capture_text("stage_screen", _safe_text(
                lambda: self.page.locator(".guided-step").first.inner_text()))

    def start_new_project(self) -> None:
        """L3's *New project* -- opens the same inline step-1 form L1 shows directly."""
        with self._bstep.step("founder starts a new project from the list") as h:
            self.page.get_by_role("button", name=re.compile(r"^new project$", re.I)).click()
            self.page.locator(".guided-step").wait_for(state="visible", timeout=10_000)
            h.add_screenshot(self._bstep.screenshot("landing-new-project"))

    def project_rows(self) -> list[str]:
        return _safe_all_texts(self.page, "a.project-row")

    def open_project(self, index: int = 0) -> None:
        with self._bstep.step(f"founder opens project row {index}") as h:
            self.page.locator("a.project-row").nth(index).click()
            _wait_for_url_change(self.page, lambda url: "/p/" in url)
            h.add_screenshot(self._bstep.screenshot("landing-open-project"))


_STAGE_NAV_LABEL = {"PROBLEM": "The problem", "SOLUTION": "Your solution", "COMMERCIAL": "Will they pay"}

# An agent bubble that carries words. `ChatFrame.tsx` renders the typing indicator inside the
# very same `.msg.agent > .bub` shell as a real turn (`<div class="typing" role="status">` in a
# `.bub`), so a bare `.msg.agent .bub` count reads "opening bubble + typing" (2) before the answer
# and "opening bubble + question" (2) after it -- the count never moves, and a wait keyed on it
# times out against a runtime that answered in milliseconds (live-confirmed, this repo's own
# S-001 run `20260903T215038Z`, keel-cloud's `inference_job` row COMPLETED 12ms after creation).
_AGENT_BUBBLE = ".chat__body .msg.agent .bub:not(:has(.typing))"


# ------------------------------------------------------------------------------------------ Shell

class Shell:
    """The founder project shell's own chrome (`routes/founder/ProjectShell.tsx`, `components/
    AgentLine.tsx`, `components/SideNav.tsx`) -- read/click helpers shared by every screen inside
    `/p/:id/*`. Takes no `base_url` (it never navigates anywhere by URL, only by clicking whatever
    the current screen already renders)."""

    def __init__(self, page: Page, recorder: Recorder | None = None, *, party: str = "founder"):
        self.page = page
        self._recorder = recorder
        self._bstep = _BrowserStep(recorder, page, party) if recorder is not None else None
        self._interaction_id: str | None = None

    @contextmanager
    def _scope(self):
        if self._recorder is None:
            yield
            return
        if self._interaction_id is None:
            self._interaction_id = self._recorder.new_interaction_id()
        with self._recorder.interaction("ui_visit", self._interaction_id):
            yield

    @contextmanager
    def _maybe_step(self, name: str):
        """Every action below records a step when this instance was given a `Recorder`
        (`evals/test_s001_smoke.py` constructs some call sites as `Shell(page, recorder)`, others
        as the older, unrecorded `Shell(page)` -- both are live; see the class docstring). With no
        recorder, the click/wait still happens for real, just without a transcript entry."""
        if self._bstep is None:
            yield None
            return
        with self._bstep.step(name) as h:
            yield h

    # ------------------------------------------------------------------------------------- reads

    def agent_line_text(self) -> str:
        return _safe_text(lambda: self.page.locator(".agentline").first.inner_text())

    def nav_status(self, stage: str) -> str:
        """The status word beside a stage's own side-nav entry (`SideNav.tsx`'s `StageEntry`) --
        e.g. *Being described*, *Reviewing*, *Approved · nobody asked yet*, *Holding up · 2 read,
        1 to read* (design §7.5). `stage` is either the enum (`"PROBLEM"`) or the nav's own label
        ("The problem")."""
        label = _STAGE_NAV_LABEL.get(stage, stage)
        item = self.page.locator(".side-nav__item", has_text=label).first
        return _safe_text(lambda: item.locator(".side-nav__status").first.inner_text())

    def people_locked(self) -> bool:
        return self.page.locator(".side-nav__item--locked").count() > 0

    def people_locked_reason(self) -> str:
        return _safe_text(lambda: self.page.locator(".side-nav__locked-why").first.inner_text())

    def main_text(self) -> str:
        """The shell's own main pane (`ProjectShell.tsx`'s `.shell__main`) -- what a screen inside
        the project actually rendered, chrome excluded (spec 007-every-door FR-003)."""
        return _safe_text(lambda: self.page.locator(".shell__main").first.inner_text())

    def pointer_to_agent_text(self) -> str:
        """`.next.agent` -- the pointer-to-agent variant of the next-step box (design §4 item 4):
        present only in `GuidedStep.tsx`'s own landed phase, a sentence, never a link."""
        return _safe_text(lambda: self.page.locator(".next.agent").first.inner_text())

    def capture_common(self, h: StepHandle) -> None:
        """For a caller that wants the shell's own evidence folded into its own already-open step
        (`h`) -- the agent line, the locked-People-why (ORI-U3) when present, and the
        pointer-to-agent sentence (GUI-U2) when present."""
        h.capture_text("agent_line", self.agent_line_text())
        if self.people_locked():
            h.capture_text("locked_reason", self.people_locked_reason())
        pointer = self.pointer_to_agent_text()
        if pointer:
            h.capture_text("pointer_to_agent", pointer)

    # ----------------------------------------------------------------------------------- actions

    def click_stage_link(self, stage: str) -> None:
        """Clicks a stage's own side-nav entry (only a link once framed/approved or a draft is
        open on it -- `SideNav.tsx`'s `clickable`) rather than typing its URL (design §6.1 S2's
        own "click the problem link" moment). Lands either on that stage's approved card
        (read-only, with the "draft kept" note, if another stage is the open draft) or its own
        chat/guided-step (if it is itself the open draft)."""
        with self._scope():
            with self._maybe_step(f"founder clicks {stage.lower()} in the side nav") as h:
                label = _STAGE_NAV_LABEL.get(stage, stage)
                self.page.locator(".side-nav__item", has_text=label).first.click()
                self.page.wait_for_selector(".card.openc, .guided-step, .draftnote", timeout=10_000)
                if h is not None:
                    h.capture_text("screen", "stage")
                    h.capture_text("stage", stage)
                    h.capture_text("stage_identity", _safe_text(
                        lambda: self.page.locator(".bet, .guided-step__kicker").first.inner_text()))
                    self.capture_identity(h)
                    h.add_screenshot(self._bstep.screenshot(f"nav-click-{stage.lower()}"))

    def capture_identity(self, h: StepHandle) -> None:
        """ORI-U1's substrate: the shell's own brand row names the project on every founder page
        (`ProjectShell.tsx`: `Keel · <span class="hint">{projectDisplayName}</span>`) -- captured
        as `identity` so the rubric can see which project this screen is about. Live-confirmed
        gap (run `20260904T020336Z`, 11 ORI-U1 misses): every stage/People/brief visit rendered
        the name and none of them captured it."""
        h.capture_text("identity", _safe_text(
            lambda: self.page.locator(".shell__brand .hint").first.inner_text()))

    def open_people(self) -> None:
        with self._scope():
            with self._maybe_step("founder opens People from the side nav") as h:
                self.page.get_by_role("link", name=re.compile(r"^people$", re.I)).click()
                _wait_for_url_change(self.page, lambda url: "/people" in url)
                if h is not None:
                    h.capture_text("screen", "people")
                    self.capture_identity(h)
                    h.add_screenshot(self._bstep.screenshot("nav-click-people"))

    def open_brief(self) -> None:
        """Live-confirmed (`failure/page.html`, `runs/20260904T014230Z-s001-smoke`): unlike
        *People*'s bare `<a>People</a>`, the side nav's *Brief* entry carries a trailing status
        span (`Brief<span class="side-nav__status mute">as of today</span>`), same shape as a
        stage entry -- its accessible name is "Brief as of today", not "Brief", so an anchored
        `^brief$` role match never finds it. `.side-nav__item` + `has_text` (the same convention
        `click_stage_link` already uses) matches on either shape."""
        with self._scope():
            with self._maybe_step("founder opens the brief from the side nav") as h:
                self.page.locator(".side-nav__item", has_text=re.compile(r"^brief", re.I)).first.click()
                _wait_for_url_change(self.page, lambda url: "/brief" in url)
                if h is not None:
                    h.capture_text("screen", "brief")
                    self.capture_identity(h)
                    h.add_screenshot(self._bstep.screenshot("nav-click-brief"))


# ------------------------------------------------------------------------------------------- Chat

# The waiting phases the walk narrates (keel-cloud waiting-with-the-agent-design.md §5). The
# first two are wire-true (job QUEUED / RUNNING), the rest are the clock's; "Done." is C9's.
WAIT_PHASES = {
    "Sending your words…", "Sending your claim…", "Your agent has picked it up.",
    "Thinking it over…", "Working out what must be true…", "Still working — longer than usual.",
    "Done.",
}
_ELAPSED_RE = re.compile(r"^\d+ s$")

# Records every value the chat's own state line (`div.chat__sub[role=status]`) ever holds, from
# the moment it is installed. See `Chat.send`'s own note for why watching beats polling here.
_PHASE_RECORDER = """() => {
  window.__keelPhases = [];
  if (window.__keelPhaseObserver) window.__keelPhaseObserver.disconnect();
  const push = () => {
    const el = document.querySelector('.chat .chat__sub');
    const text = el ? (el.innerText || el.textContent || '').trim() : '';
    if (text && window.__keelPhases[window.__keelPhases.length - 1] !== text) {
      window.__keelPhases.push(text);
    }
  };
  push();
  const observer = new MutationObserver(push);
  observer.observe(document.body, {subtree: true, childList: true, characterData: true});
  window.__keelPhaseObserver = observer;
}"""


class Chat:
    """The guided step's own chat (`components/chat/ChatFrame.tsx`, `chat/GuidedStep.tsx`) --
    C1-C8: the composer, the agent's turns, and the confirmation card. Never navigates anywhere
    itself (`OverviewRoute` mounts the frame it acts on -- `base_url` is stored only for
    constructor-shape consistency); the whole exchange -- composing, waiting, confirming -- is one
    `agent_turn` interaction, watched entirely through the frame's own rendered state, never a
    wire read (spec FR-009).
    """

    def __init__(self, page: Page, *args: Any, party: str = "founder"):
        self.page = page
        recorder, self.base_url = _split_recorder_and_base(args, page)
        self._bstep = _BrowserStep(recorder, page, party)
        self._interaction_id: str | None = None

    def _scope(self):
        if self._interaction_id is None:
            self._interaction_id = self._bstep.recorder.new_interaction_id()
        return self._bstep.recorder.interaction("agent_turn", self._interaction_id)

    # ------------------------------------------------------------------------------------- reads

    def is_visible(self) -> bool:
        return self.page.locator(".chat").count() > 0

    def state_line(self) -> str:
        return _safe_text(lambda: self.page.locator(".chat__sub").first.inner_text())

    def topic(self) -> str:
        return _safe_text(lambda: self.page.locator(".chat__topic").first.inner_text())

    def kicker(self) -> str:
        return _safe_text(lambda: self.page.locator(".guided-step__kicker").first.inner_text())

    def latest_agent_text(self) -> str:
        return _safe_text(lambda: self.page.locator(_AGENT_BUBBLE).last.inner_text())

    def is_typing(self) -> bool:
        return self.page.locator(".typing[role='status']").count() > 0

    def confirmation_card(self) -> dict[str, str] | None:
        """C5's own confirmation card (`.understood`) -- `{kicker, claim, note}`, or `None` before
        it renders."""
        card = self.page.locator(".understood")
        if card.count() == 0:
            return None
        return {
            "kicker": _safe_text(lambda: card.locator(".understood__kicker").first.inner_text()),
            "claim": _safe_text(lambda: card.locator(".understood__claim").first.inner_text()),
            # keel-web spec 011: the card carries no note any more (the statement names its own
            # unknowns); read it if an older build still renders one, else empty.
            "note": _safe_text(lambda: card.locator(".understood__note").first.inner_text())
            if card.locator(".understood__note").count() > 0 else "",
        }

    def _recorded_phase(self) -> str | None:
        """The first waiting phase the `MutationObserver` `send()` installed ever saw."""
        try:
            seen = self.page.evaluate("() => window.__keelPhases || []") or []
        except Exception:  # noqa: BLE001 - a page that navigated away has nothing to report
            return None
        return next((line for line in seen if line in WAIT_PHASES), None)

    def landed_claim(self) -> str:
        """C8's own landed claim (`.landed__claim`) -- empty until the confirmation is saved."""
        return _safe_text(lambda: self.page.locator(".landed__claim").first.inner_text())

    def draft_kept_note(self) -> str:
        """S2: the "draft kept" note shown when another screen is opened mid-draft."""
        return _safe_text(lambda: self.page.locator(".draftnote").first.inner_text())

    # ----------------------------------------------------------------------------------- actions

    def send(self, text: str) -> None:
        """Types into whichever composer is live (C1's opening ask, or C3's follow-up answer --
        the label changes, the textarea/button selectors don't) and submits.

        Captures the agent's own bubble count in the same breath as the click (`self.
        _bubbles_before_send`) -- `wait_for_agent_turn` reads it back rather than re-measuring
        after the fact. Live-confirmed race, the mirror image of the "reading" text-absence bug
        this file's own docstring already records: keel-runtime's scripted executor can answer
        fast enough that the reply is *already* rendered by the time a *separate*, later call
        gets around to counting bubbles as its own "before" baseline -- at which point the count
        never goes up again and the wait times out despite the answer being right there. Counting
        immediately before the click that triggers the reply closes that gap.
        """
        with self._scope():
            with self._bstep.step(f"founder writes to the agent: {text[:60]!r}") as h:
                box = self.page.locator(".chat__foot textarea")
                # The composer stays disabled ("Your agent is thinking…") for a beat after the
                # agent's own reply first renders -- live-confirmed: `wait_for_agent_turn`
                # returning the instant a new bubble appears can still be a moment ahead of the
                # composer re-enabling itself. Wait for it, rather than racing straight into fill.
                box.wait_for(state="visible", timeout=15_000)
                self.page.wait_for_function(
                    "() => { const t = document.querySelector('.chat__foot textarea'); "
                    "return !!t && !t.disabled; }",
                    timeout=15_000,
                )
                box.fill(text)
                h.add_screenshot(self._bstep.screenshot("chat-composer-filled"))
                self._bubbles_before_send = self.page.locator(_AGENT_BUBBLE).count()
                self._had_card_before_send = self.confirmation_card() is not None
                # Watch every render of the state line, rather than sampling it. keel-runtime's
                # scripted executor answers a framing job in a fraction of a second (live-
                # confirmed: `runs/20260907T143729Z-s001-smoke`, `phase_line=None` on COMMERCIAL),
                # and a poll -- however tight -- can miss a phase that was genuinely on screen for
                # one frame. A `MutationObserver` sees every value the element ever held, so this
                # stops the *harness* from being the reason nobody saw the narration; it cannot
                # make a phase render that never rendered, which is what keeps the assertion
                # honest. Installed immediately before the click that starts the turn.
                self.page.evaluate(_PHASE_RECORDER)
                self.page.locator(".chat__foot button.btn.primary").click()
                # The waiting phase, sampled in the same breath as the click. Spec 010's
                # generated script answers a framing job in well under a second (live-confirmed:
                # `runs/20260907T143214Z-s001-smoke`, `phase_line=None` on SOLUTION), so
                # `wait_for_agent_turn`'s own first poll can already be too late to see the
                # narration the design promises. Reading it here does not make the phase render;
                # it stops the harness from being the reason nobody saw it. Exactly the mirror of
                # the bubble-count baseline above, and recorded for the same reason.
                self._phase_after_send = self.state_line()
                h.capture_text("chat_sent", text)
                h.capture_text("chat_phase_at_send", self._phase_after_send or "")
                h.add_screenshot(self._bstep.screenshot("chat-sent"))

    def wait_for_agent_turn(self, *, timeout_s: float = 60) -> dict[str, str]:
        """The one wait every C2/C4/C6-shaped moment is (design edge cases: "the walk's screens
        poll the interaction; the harness waits on the screen... with a 60 s ceiling per agent
        turn, never on sleeps"). Returns `{chat_state, agent_reply, outcome}`.

        **Not a text-absence wait.** An earlier draft waited for `.chat__sub` to stop containing
        "Reading what you wrote…" -- live-confirmed flaky (this repo's own S-001 runs): `send()`
        returns the instant the click fires, before React has re-rendered the "reading" state at
        all, so `wait_for_function`'s first poll can observe the *pre-send* state line (which
        also doesn't contain that phrase) and resolve immediately, long before the agent has
        actually answered. Waits on a positive signal instead: the agent's own bubble count
        going up, or the confirmation card appearing -- either is real new content, never a
        stale read of the state line's wording.
        """
        with self._scope():
            with self._bstep.step("the founder's agent answers") as h:
                # Read back the baseline `send()` captured in the same breath as its own click --
                # see `send()`'s docstring for why re-measuring here, after the fact, can already
                # be too late against a fast scripted executor. Falls back to measuring now only
                # if this instance never sent anything itself (e.g. a caller waiting on a step
                # that already had a pending interaction when the chat was first opened).
                bubbles_before = getattr(self, "_bubbles_before_send", None)
                had_card = getattr(self, "_had_card_before_send", None)
                phase_at_send = getattr(self, "_phase_after_send", None)
                # Consumed once -- a later, unrelated wait on this same instance must not reuse
                # a stale baseline from a send() several turns back.
                self._bubbles_before_send = None
                self._had_card_before_send = None
                self._phase_after_send = None
                if bubbles_before is None:
                    bubbles_before = self.page.locator(_AGENT_BUBBLE).count()
                if had_card is None:
                    had_card = self.confirmation_card() is not None
                waiting_box = self.page.locator(".chat .sys")
                if waiting_box.count() > 0:
                    h.capture_text("waiting_text", _safe_text(lambda: waiting_box.first.inner_text()))
                h.capture_text("chat_state", self.state_line())
                # A plain Python poll, not `page.wait_for_function` -- easier to reason about and
                # to prove correct than trusting an inline JS closure's own argument-serialization
                # to round-trip a captured-before count exactly.
                deadline = time.monotonic() + timeout_s
                turn_started = time.monotonic()
                phase_seen: str | None = None
                elapsed_seen: str | None = None
                while True:
                    # Waiting-with-the-agent (design §2): while the turn is pending the state line
                    # narrates a phase and a counter ticks. Sampled *before* the landed check --
                    # a scripted agent answers inside the first poll (live: 0.37 s), and the phase
                    # is still on screen for that one read. Remember the first phase seen and the
                    # last counter reading; the scenario asserts on them after the turn lands.
                    line = self.state_line()
                    if phase_seen is None and line in WAIT_PHASES:
                        phase_seen = line
                    if phase_seen is None and phase_at_send in WAIT_PHASES:
                        phase_seen = phase_at_send
                    if phase_seen is None:
                        phase_seen = self._recorded_phase()
                    counter = self.page.locator(".chat__elapsed")
                    if counter.count() > 0:
                        elapsed_seen = _safe_text(lambda c=counter: c.first.inner_text()).strip() or elapsed_seen
                    bubbles_now = self.page.locator(_AGENT_BUBBLE).count()
                    has_card_now = self.page.locator(".understood").count() > 0
                    if bubbles_now > bubbles_before or (has_card_now and not had_card):
                        break
                    if time.monotonic() > deadline:
                        raise TimeoutError(
                            f"the agent never answered within {timeout_s}s "
                            f"(bubbles stayed at {bubbles_now}, confirmation card "
                            f"{'already' if had_card else 'never'} present)")
                    self.page.wait_for_timeout(300)
                h.add_screenshot(self._bstep.screenshot("chat-agent-responded"))
                new_state = self.state_line()
                if phase_seen is None and new_state in WAIT_PHASES:
                    phase_seen = new_state  # the reply landed while the phase line was still up
                if phase_seen is None:
                    phase_seen = self._recorded_phase()
                h.capture_text("chat_state", new_state)
                outcome = _infer_chat_outcome(new_state)
                reply = self._latest_reply_text()
                h.capture_text("agent_reply", reply)
                h.capture_text("agent_turn_outcome", outcome)
                try:
                    h.capture_text("phases_observed", json.dumps(
                        self.page.evaluate("() => window.__keelPhases || []")))
                except Exception:  # noqa: BLE001 - evidence only
                    pass
                if phase_seen:
                    h.capture_text("phase_line", phase_seen)
                if elapsed_seen:
                    h.capture_text("elapsed_label", elapsed_seen)
        return {"chat_state": new_state, "agent_reply": reply, "outcome": outcome,
                "phase_line": phase_seen, "elapsed_label": elapsed_seen,
                "turn_seconds": round(time.monotonic() - turn_started, 3)}

    def _latest_reply_text(self) -> str:
        card = self.confirmation_card()
        if card is not None:
            return card["claim"] or card["kicker"]
        bubbles = self.page.locator(_AGENT_BUBBLE)
        if bubbles.count() > 0:
            return _safe_text(lambda: bubbles.last.inner_text())
        return ""

    def save_confirmation(self) -> None:
        """C5's *Save this* -- accepts the draft statement (never written to the project yet;
        design §4.6) and starts the chained assumptions interaction, landing on C8's own waiting
        line -- or, when the scripted runtime answers the chained beliefs faster than the screen
        polls, straight on the review (R1) with C8 never observable at all (live-confirmed, run
        `20260904T014221Z`: `COMMERCIAL_ASSUMPTIONS` reached `AWAITING_CONFIRMATION` in the same
        second the frame was confirmed, and the app had already flipped to `/s/COMMERCIAL`)."""
        with self._scope():
            with self._bstep.step("founder saves the understood claim") as h:
                card = self.confirmation_card()
                if card:
                    h.capture_text("agent_reply", card["claim"])
                h.add_screenshot(self._bstep.screenshot("chat-understood"))
                self.page.get_by_role("button", name=re.compile(r"^save this$", re.I)).click()
                self.page.locator(".landed, .card.openc").first.wait_for(state="visible", timeout=15_000)
                h.capture_text("agent_turn_outcome", "COMPLETED")
                h.capture_text("chat_state", "Understood · working out the beliefs")
                h.add_screenshot(self._bstep.screenshot("chat-landed"))

    def wait_for_review(self, project_id: str, stage: str, *, timeout_s: float = 60) -> dict[str, Any]:
        """C8's landed clearing carries its own *Continue* button. Waits for the review card
        (`.card.openc`), clicking *Continue* once it is enabled -- on the screen's own words,
        never a reload.

        History: `runs/DRIFT.md` #14 (keel-web's `OverviewRoute`/`StageRoute` redirect bounce
        right after the beliefs land) was worked around here with a hard reload every 4s. keel-web
        `ccf822c` fixed the product (the stage route holds a "Recording…" state on the transient
        instead of redirecting), so the workaround is gone and this wait is the plain positive
        wait it always should have been.
        """
        with self._scope():
            with self._bstep.step("the founder's agent works out the beliefs") as h:
                waited_from = time.monotonic()
                waiting_text = _safe_text(lambda: self.page.locator(".next.agent").first.inner_text())
                if waiting_text:
                    h.capture_text("waiting_text", waiting_text)
                deadline = time.monotonic() + timeout_s
                clicked = False
                phase_seen: str | None = None
                landed_rows = 0
                truth_seen: str | None = None
                landed_at: float | None = None
                while self.page.locator(".card.openc").count() == 0:
                    if time.monotonic() > deadline:
                        raise TimeoutError(
                            f"the {stage} review card never rendered within {timeout_s}s "
                            f"of saving the confirmed claim")
                    # Waiting-with-the-agent (design §3-§4): the dashed rail narrates a phase,
                    # and the beliefs land in place (C9) before the founder presses Review them.
                    sub = _safe_text(lambda: self.page.locator(".next__sub").first.inner_text()).strip()
                    if phase_seen is None and sub in WAIT_PHASES:
                        phase_seen = sub
                    landed_rows = max(landed_rows, self.page.locator(".coming .belief").count())
                    # keel-web spec 012 (design §8.1): one truth at a time keeps the founder company;
                    # the review then opens itself (§8.2) -- no button to press, the loop's head sees
                    # the card arrive.
                    if truth_seen is None:
                        truth_seen = _safe_text(lambda: self.page.locator(".truth__t").first.inner_text()).strip() or None
                    # When the *landed* screen -- the one the truth card lives on -- first
                    # appeared. The wait a founder sees is measured from here, not from the click
                    # that started the job: an auto-chain can spend half a minute getting to this
                    # screen, and a truth card cannot keep anybody company before it mounts.
                    if landed_at is None and self.page.locator(".next.agent, .landed").count() > 0:
                        landed_at = time.monotonic()
                    if not clicked:
                        continue_btn = self.page.get_by_role("button", name=re.compile(r"^(continue|review them)", re.I))
                        # `is_enabled`/`click` auto-wait on an element that can vanish between
                        # this poll's `count()` and the call itself -- the scripted runtime lands
                        # the beliefs fast enough that the app flips to the review mid-poll
                        # (live-confirmed, run `20260904T015718Z`: a 30s `is_enabled` auto-wait on a
                        # Continue button that had already gone). A vanished button is not a
                        # failure; the loop's own head re-checks for the review card.
                        try:
                            if continue_btn.count() > 0 and continue_btn.first.is_enabled(timeout=1_000):
                                continue_btn.first.click(timeout=2_000)
                                clicked = True
                        except Exception:  # noqa: BLE001 - the button left; the review is arriving
                            pass
                    self.page.wait_for_timeout(500)
                h.add_screenshot(self._bstep.screenshot("chat-review-ready"))
                claim = _safe_text(lambda: self.page.locator(".card.openc .claim").first.inner_text())
                h.capture_text("agent_reply", claim)
                try:
                    h.capture_text("phases_observed", json.dumps(
                        self.page.evaluate("() => window.__keelPhases || []")))
                except Exception:  # noqa: BLE001 - evidence only
                    pass
                if phase_seen:
                    h.capture_text("phase_line", phase_seen)
                h.capture_text("landed_rows", str(landed_rows))
                if truth_seen:
                    h.capture_text("truth_seen", truth_seen)
                h.capture_text("agent_turn_outcome", "beliefs_ready")
        return {"phase_line": phase_seen, "landed_rows": landed_rows, "truth_seen": truth_seen,
                "wait_seconds": round(time.monotonic() - waited_from, 3),
                "landed_seconds": (round(time.monotonic() - landed_at, 3)
                                   if landed_at is not None else 0.0)}

    def start_over(self) -> None:
        with self._scope():
            with self._bstep.step("founder cancels and starts over") as h:
                self.page.get_by_role("button", name=re.compile("start over", re.I)).first.click()
                self.page.wait_for_selector(".msg.agent", timeout=15_000)
                h.add_screenshot(self._bstep.screenshot("chat-start-over"))

    def back_to_step(self) -> None:
        """The draft-kept note's own *← Back to step N* -- returns to this instance's own chat/
        guided-step, wherever the interaction has gotten to while it was out of view."""
        with self._bstep.step("founder returns to the in-progress step") as h:
            self.page.locator(".draftnote a.btn").click()
            self.page.wait_for_selector(".chat", timeout=15_000)
            h.add_screenshot(self._bstep.screenshot("chat-back-to-step"))


def _infer_chat_outcome(state_line: str) -> str:
    """A short, human-readable label for the report's own conversation card -- descriptive only,
    never swept by policy (agent_turn interactions carry no rubric checks of their own; see
    `harness/rubric.py`'s `evaluate`)."""
    if "Done asking" in state_line:
        return "awaiting_confirmation"
    if "Lost" in state_line:
        return "lost"
    if "Not connected" in state_line:
        return "not_connected"
    if "question" in state_line:
        return "needs_input"
    return "connected"


# --------------------------------------------------------------------------------------- StageCard

class StageCard:
    """`routes/founder/StageRoute.tsx` -- the draft review (R1/R2) and the approved card
    (R4/S2/S4, plus the evidence drill-down E1-E3) -- both render the identical `.card.openc`
    shell (`DraftReview`/`ApprovedCard` share every class name), so `open()` is one method for
    both. `open()`'s own wait is generous (matching the spec's 60s agent-turn ceiling): the
    founder's runtime may still be working out the beliefs in the background even after
    `Chat.wait_for_review` returns.
    """

    def __init__(self, page: Page, *args: Any, party: str = "founder"):
        self.page = page
        recorder, self.base_url = _split_recorder_and_base(args, page)
        self._bstep = _BrowserStep(recorder, page, party)
        self._interaction_id: str | None = None

    def _scope(self):
        if self._interaction_id is None:
            self._interaction_id = self._bstep.recorder.new_interaction_id()
        return self._bstep.recorder.interaction("ui_visit", self._interaction_id)

    def open(self, project_id: str, stage: str, *, state_reader: StateReader | None = None) -> dict[str, Any]:
        with self._scope():
            with self._bstep.step(f"founder opens the {stage.lower()} stage card") as h:
                self.page.goto(f"{self.base_url}/p/{project_id}/s/{stage}", wait_until="load")
                self.page.locator(".card.openc .bet").wait_for(state="visible", timeout=65_000)
                h.capture_text("screen", "stage")
                h.capture_text("stage", stage)
                h.capture_text("stage_identity", _safe_text(
                    lambda: self.page.locator(".card.openc .bet").first.inner_text()))
                h.capture_text("stage_screen", _safe_text(
                    lambda: self.page.locator(".card.openc").first.inner_text()))
                Shell(self.page).capture_identity(h)
                names = _safe_all_texts(self.page, ".quote .name")
                if names:
                    h.capture_text("participant_names", "\n".join(names))
                _capture_state(h, project_id, state_reader)
                h.add_screenshot(self._bstep.screenshot(f"stage-{stage.lower()}"))
        status = self.status_word()
        is_draft = self.page.locator(".review-hint").count() > 0
        return {"status": status, "is_draft": is_draft}

    def claim(self) -> str:
        return _safe_text(lambda: self.page.locator(".card.openc .claim").first.inner_text())

    def status_word(self) -> str:
        return _safe_text(lambda: self.page.locator(".card.openc .status").first.inner_text())

    def counts_text(self) -> str:
        return _safe_text(lambda: self.page.locator(".counts").first.inner_text())

    def belief_headings(self) -> list[str]:
        return _safe_all_texts(self.page, ".belief .b-heading")

    def approve(self) -> None:
        """R1's *These are right — approve* -- the one write (design §4.6): claim, roles and
        beliefs land in the project together with the approval."""
        with self._scope():
            with self._bstep.step("founder approves the stage card") as h:
                button = self.page.get_by_role("button", name=re.compile("these are right", re.I))
                button.wait_for(state="visible", timeout=10_000)
                button.click()
                self.page.get_by_role("button", name=re.compile("these are right", re.I)).wait_for(
                    state="detached", timeout=15_000)
                h.capture_text("stage_screen", _safe_text(
                    lambda: self.page.locator(".card.openc").first.inner_text()))
                h.capture_text("affordance", _safe_text(
                    lambda: self.page.locator(".approved-note").first.inner_text()))
                h.add_screenshot(self._bstep.screenshot("stage-approved"))

    def start_over(self) -> None:
        """R2's *Start over* -- opens the inline warn-edged confirm ("Start over?")."""
        with self._scope():
            with self._bstep.step("founder asks to start over") as h:
                self.page.get_by_role("button", name=re.compile(r"^start over$", re.I)).first.click()
                self.page.get_by_text("Start over?").wait_for(state="visible", timeout=10_000)
                h.add_screenshot(self._bstep.screenshot("stage-start-over-confirm"))

    def confirm_start_over(self) -> None:
        """R2's *Yes, start over* -- cancels the whole draft chain; back to C1, empty."""
        with self._scope():
            with self._bstep.step("founder confirms starting over") as h:
                self.page.get_by_role("button", name=re.compile(r"^yes, start over$", re.I)).click()
                self.page.wait_for_selector(".msg.agent, .guided-step", timeout=15_000)
                h.add_screenshot(self._bstep.screenshot("stage-start-over-done"))

    def keep_draft(self) -> None:
        """R2's *Keep it* -- closes the confirm note; nothing changes."""
        with self._scope():
            with self._bstep.step("founder keeps the draft") as h:
                self.page.get_by_role("button", name=re.compile(r"^keep it$", re.I)).click()
                h.add_screenshot(self._bstep.screenshot("stage-start-over-kept"))

    def continue_to_next_step(self) -> None:
        """R4's *Continue to step N — <stage> →* -- the walk's own next step. The link is a
        `<Link to="/p/:id">` (`StageRoute.tsx`), rendered by `ApprovedCard` only when `!readOnly
        && nobodyAskedYet`. Before keel-web `6912f7e`, `nobodyAskedYet` could never read true
        once a stage was approved (`runs/DRIFT.md` #16) -- resolved now, but `readOnly` is a
        separate, by-design gate (a stage the auto-chain just opened the *next* draft for is
        read-only, live-confirmed run `20260903T220650Z`), so the link can still legitimately be
        absent. This clicks it when it renders and otherwise goes to the overview -- the exact
        destination the link would have opened -- rather than assuming either shape."""
        with self._bstep.step("founder continues to the next step") as h:
            link = self.page.locator(".actions").get_by_role("link", name=re.compile("continue to step", re.I))
            if link.count() > 0:
                link.first.click()
            else:
                match = re.search(r"(/p/[^/?#]+)", self.page.url)
                if not match:
                    raise AssertionError(f"not on a project route, cannot continue: {self.page.url}")
                self.page.goto(f"{self.base_url}{match.group(1)}", wait_until="load")
            self.page.wait_for_selector(".chat", timeout=15_000)
            h.add_screenshot(self._bstep.screenshot("stage-continue"))

    def go_to_people(self) -> None:
        """S4's *Go to People →* -- the final stage's own closing note (`ApprovedCard`,
        `StageRoute.tsx`), gated by the same `!readOnly && nobodyAskedYet` as R4's continue link
        above. There is no successor stage to auto-chain into on the final stage, so `readOnly`
        is always false here -- unlike `continue_to_next_step`, this link has no legitimate reason
        to be absent once `nobodyAskedYet` is correct (keel-web `6912f7e`, `runs/DRIFT.md` #16,
        resolved), so this waits on it rather than falling back."""
        with self._bstep.step("founder goes to People") as h:
            link = self.page.get_by_role("link", name=re.compile("go to people", re.I))
            link.wait_for(state="visible", timeout=15_000)
            link.click()
            _wait_for_url_change(self.page, lambda url: "/people" in url)
            h.add_screenshot(self._bstep.screenshot("stage-to-people"))

    def see_the_overview(self) -> None:
        """S4's *See the overview* -- the other of its two buttons."""
        with self._bstep.step("founder sees the overview") as h:
            self.page.get_by_role("link", name=re.compile(r"^see the overview$", re.I)).click()
            self.page.wait_for_selector(".card:not(.openc), .guided-step", timeout=15_000)
            h.add_screenshot(self._bstep.screenshot("stage-to-overview"))

    def expand_belief(self, heading: str) -> None:
        """Expands one belief's testimony drill-down (E1-E3) by clicking its `.b-top` toggle --
        the belief whose own verdict matches the card's status already renders open by default
        (`StageRoute.tsx`'s `firstMatchingVerdictId`), so this is for reading a DIFFERENT belief's
        evidence."""
        with self._bstep.step(f"founder opens the evidence for {heading!r}") as h:
            row = self.page.locator(".belief", has_text=heading).first
            row.locator(".b-top").click()
            h.add_screenshot(self._bstep.screenshot("belief-expanded"))

    def drilldown(self, heading: str) -> dict[str, list[dict[str, str]]]:
        """`{for, against, not}` -- each a list of `{name, quote, why}` -- from one belief's
        expanded testimony drill-down (`Drilldown.tsx`'s own three groups). Also folds the quotes
        into `participant_page` (a participant's own words, read back verbatim on the founder's
        screen -- `HOP_INTERACTION_TYPES["participant_page"]` names `ui_visit` as a legitimate
        place this hop is judged, beside the participant's own page).
        """
        row = self.page.locator(".belief", has_text=heading).first
        out: dict[str, list[dict[str, str]]] = {"for": [], "against": [], "not": []}
        quote_text: list[str] = []
        for cls, key in (("for", "for"), ("against", "against"), ("nul", "not")):
            group = row.locator(f".vgroup.{cls} .quote")
            for i in range(group.count()):
                q = group.nth(i)
                name = _safe_text(lambda q=q: q.locator(".name").first.inner_text())
                words = _safe_text(lambda q=q: q.locator(".words").first.inner_text())
                why = _safe_text(lambda q=q: q.locator(".why").first.inner_text())
                out[key].append({"name": name, "quote": words, "why": why})
                quote_text.append(f"{name}: {words}")
        if quote_text:
            with self._scope():
                with self._bstep.step(f"founder reads the testimony for {heading!r}") as h:
                    h.capture_text("participant_page", "\n".join(quote_text))
        return out



# ------------------------------------------------------------------------------------ MarketStep

# `lib/markets.ts`: the country list is fixed, grouped, and the region field is optional. The three
# optgroup labels are asserted by name because the design's own point is that a founder picks from
# a list rather than typing a country.
MARKET_GROUPS = ("North America", "Europe", "Asia")


class MarketStep:
    """The market step (`components/MarketStep.tsx`), an inline frame of `/` between naming the
    project and starting it (design §3.8: the market is what decides units, register and currency,
    and it is chosen **before** anything is framed).

    **The region input is found positionally.** Its `aria-label` is its own placeholder and the
    placeholder depends on the country (`regionPlaceholder`: *"State or region, if it matters —
    Texas, California, New York (optional)"* for US, and a shorter sentence everywhere else), so a
    label-matched locator would find it for `07-mulchrun` and silently mismatch for every GB entry
    (research R7). The text input that follows the country select is the region box, and that is
    stable in a way its label is not.
    """

    def __init__(self, page: Page, *args: Any, party: str = "founder"):
        self.page = page
        recorder, self.base_url = _split_recorder_and_base(args, page)
        self._bstep = _BrowserStep(recorder, page, party)
        self._interaction_id: str | None = None

    def _scope(self):
        if self._interaction_id is None:
            self._interaction_id = self._bstep.recorder.new_interaction_id()
        return self._bstep.recorder.interaction("ui_visit", self._interaction_id)

    # ------------------------------------------------------------------------------------- reads

    def _country_select(self):
        return self.page.locator(".guided-step select").first

    def _region_input(self):
        return self.page.locator(".guided-step input[type='text']").first

    def question(self) -> str:
        return _safe_text(lambda: self.page.locator(".guided-step__question").first.inner_text())

    def kicker(self) -> str:
        return _safe_text(lambda: self.page.locator(".guided-step__kicker").first.inner_text())

    def hints(self) -> list[str]:
        return _safe_all_texts(self.page, ".guided-step p.hint")

    def country_groups(self) -> list[str]:
        return [g.get_attribute("label") or ""
                for g in self._country_select().locator("optgroup").all()]

    def country_codes(self) -> list[str]:
        return [o.get_attribute("value") or ""
                for o in self._country_select().locator("option").all()]

    def region_placeholder(self) -> str:
        return self._region_input().get_attribute("placeholder") or ""

    def described_sentence(self, *, timeout_s: float = 10) -> str:
        """`Market.described`, off `GET /v2/markets/{country}` -- *"So the questions will be in
        British English, in pounds and pence, kilometres, metres and working days."* Composed by
        keel-cloud (spec 030 FR-014) and rendered verbatim; the read is debounced behind the
        country select, so this waits rather than reading an empty string a moment too early.

        `""` when it never arrives, which is the finding rather than a crash."""
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            for hint in _safe_all_texts(self.page, ".guided-step p.hint"):
                lowered = hint.casefold()
                if "so the questions" in lowered or "the questions will be" in lowered:
                    return hint
            self.page.wait_for_timeout(250)
        return ""

    def is_visible(self) -> bool:
        return self._country_select().count() > 0

    # ----------------------------------------------------------------------------------- actions

    def fill(self, country: str, region: str | None = None) -> None:
        """Chooses the country from the list and types the region, or leaves it empty. An entry
        whose `market.region` is `null` (countly, paidly) leaves the box untouched -- never the
        word "null", and never a space."""
        with self._scope():
            with self._bstep.step(
                    f"founder says where this sells first: {country}"
                    + (f", {region}" if region else " (no region)")) as h:
                self._country_select().select_option(country)
                if region:
                    self._region_input().fill(region)
                h.capture_text("screen", "market")
                h.capture_text("stage_screen", _safe_text(
                    lambda: self.page.locator(".guided-step").first.inner_text()))
                h.capture_text("identity", self.kicker())
                h.add_screenshot(self._bstep.screenshot("market-step"))

    def back(self) -> None:
        with self._scope():
            with self._bstep.step("founder goes back from the market step") as h:
                self.page.get_by_role("button", name=re.compile(r"^back$", re.I)).click()
                self.page.locator(".guided-step__question").wait_for(state="visible", timeout=10_000)
                h.add_screenshot(self._bstep.screenshot("market-back"))

    def start(self) -> str:
        """*Start* -- `POST /v2/projects {name, market}` (vendored fact V7: the request carries no
        `language`; the server derives it). Returns the new project id off the resulting URL."""
        with self._scope():
            with self._bstep.step("founder starts the project") as h:
                self.page.get_by_role("button", name=re.compile(r"^start$", re.I)).click()
                _wait_for_url_change(self.page, lambda url: "/p/" in url)
                h.capture_text("screen", "overview")
                h.add_screenshot(self._bstep.screenshot("market-started"))
        match = re.search(r"/p/([^/?#]+)", self.page.url)
        if not match:
            raise AssertionError(f"starting the project did not land on a project shell: {self.page.url}")
        return match.group(1)


# ------------------------------------------------------------------------------------ ReviewCard

class ReviewCard:
    """`StageRoute.tsx`'s `DraftReview` -- the unapproved draft (mockup screen 2), the one screen
    a founder reads before anyone is asked anything.

    Holds the handles; asserts nothing. Everything below is a read the scenario judges.
    """

    def __init__(self, page: Page, *args: Any, party: str = "founder"):
        self.page = page
        recorder, self.base_url = _split_recorder_and_base(args, page)
        self._bstep = _BrowserStep(recorder, page, party)
        self._interaction_id: str | None = None

    def _scope(self):
        if self._interaction_id is None:
            self._interaction_id = self._bstep.recorder.new_interaction_id()
        return self._bstep.recorder.interaction("ui_visit", self._interaction_id)

    def _card(self):
        return self.page.locator(".card.openc").first

    # ------------------------------------------------------------------------------------- reads

    def claim(self) -> str:
        return _safe_text(lambda: self._card().locator("p.claim").first.inner_text())

    def status_word(self) -> str:
        return _safe_text(lambda: self._card().locator(".card-top .status").first.inner_text())

    def landing_note(self) -> str:
        return _safe_text(lambda: self.page.locator("p.landing-note").first.inner_text())

    def group_headings(self) -> list[str]:
        return _safe_all_texts(self.page, ".card.openc .who > h4")

    def rule_lines(self) -> list[str]:
        return _safe_all_texts(self.page, ".card.openc p.rule-line")

    def asked_first(self) -> str:
        """The *What they'll be asked first* block -- the `<h4>` and its own `dl.qa` (ORI-U4's
        substrate). `""` when the block never rendered, which is itself the finding."""
        block = self.page.locator(".card.openc .who", has=self.page.locator("dl.qa")).first
        if block.count() == 0:
            return ""
        return _safe_text(lambda: block.inner_text())

    def rationale_lines(self) -> list[str]:
        """*Not asked, on purpose:* -- `StageCard.rationaleLines`, one `<li>` each. Empty is legal
        (an entry whose normalization rationale named nothing)."""
        return _safe_all_texts(self.page, ".card.openc ul.rationale > li")

    def lines(self) -> list[dict[str, Any]]:
        """One row per `div.belief`, in rendered order: `{number, heading, proxy, statement,
        you_said, status, chips}` -- `chips` being `{text, expected, band, escape}` per
        `Chips.tsx` (`span.chip`, `.expected` for the founder's own pick, `.band` for a bucket
        inside the band, `.esc` for a way out)."""
        out: list[dict[str, Any]] = []
        rows = self.page.locator(".card.openc .belief")
        for i in range(rows.count()):
            row = rows.nth(i)
            chips: list[dict[str, Any]] = []
            chip_nodes = row.locator(".chips .chip")
            for j in range(chip_nodes.count()):
                chip = chip_nodes.nth(j)
                classes = chip.get_attribute("class") or ""
                chips.append({
                    "text": _safe_text(lambda c=chip: c.inner_text()),
                    "expected": "expected" in classes,
                    "band": "band" in classes,
                    "escape": "esc" in classes,
                })
            out.append({
                "number": _safe_text(lambda r=row: r.locator(".b-num").first.inner_text()),
                "heading": _safe_text(lambda r=row: r.locator(".b-heading").first.inner_text()),
                "proxy": row.locator(".stand-in").count() > 0,
                "statement": _safe_text(lambda r=row: r.locator(".b-detail").first.inner_text()),
                "you_said": _safe_text(lambda r=row: r.locator("p.you-said").first.inner_text()),
                "status": _safe_text(lambda r=row: r.locator(".b-status").first.inner_text()),
                "chips": chips,
            })
        return out

    def chip_labels(self, heading: str) -> list[str]:
        """The offered list for the line headed `heading`, **in order** -- FR-013's own
        `expected.buckets` comparison, read off a screen. Escapes are excluded: the corpus's
        `buckets` are the scale, and the ways out are the selection's `escape` beside it."""
        row = self.page.locator(".card.openc .belief", has_text=heading).first
        labels: list[str] = []
        chips = row.locator(".chips .chip")
        for i in range(chips.count()):
            chip = chips.nth(i)
            if "esc" in (chip.get_attribute("class") or ""):
                continue
            text = _safe_text(lambda c=chip: c.inner_text())
            labels.append(text.replace("\u2713", "").strip())
        return labels

    # ----------------------------------------------------------------------------------- actions

    def open(self, project_id: str, stage: str) -> dict[str, Any]:
        with self._scope():
            with self._bstep.step(f"founder reads the {stage.lower()} review card") as h:
                self.page.goto(f"{self.base_url}/p/{project_id}/s/{stage}", wait_until="load")
                self._card().locator(".bet").wait_for(state="visible", timeout=65_000)
                self._capture(h, stage)
                h.add_screenshot(self._bstep.screenshot(f"review-{stage.lower()}"))
        return {"status": self.status_word(), "claim": self.claim()}

    def recapture(self, stage: str, *, slug: str = "review-again") -> None:
        """Reads the card again into a fresh step -- what the correction turn's before-and-after
        is judged on."""
        with self._scope():
            with self._bstep.step(f"founder reads the {stage.lower()} card again") as h:
                self._capture(h, stage)
                h.add_screenshot(self._bstep.screenshot(slug))

    def _capture(self, h: StepHandle, stage: str) -> None:
        h.capture_text("screen", "review_card")
        h.capture_text("stage", stage)
        h.capture_text("stage_identity", _safe_text(
            lambda: self._card().locator(".bet").first.inner_text()))
        h.capture_text("review_card", _screen_text(self.page, ".card.openc"))
        h.capture_text("asked_first", self.asked_first())
        Shell(self.page).capture_identity(h)

    def approve(self) -> None:
        with self._scope():
            with self._bstep.step("founder approves the card") as h:
                button = self.page.get_by_role("button", name=re.compile("these are right", re.I))
                button.wait_for(state="visible", timeout=15_000)
                button.click()
                button.wait_for(state="detached", timeout=20_000)
                h.capture_text("affordance", _safe_text(
                    lambda: self.page.locator(".approved-note").first.inner_text()))
                h.add_screenshot(self._bstep.screenshot("review-approved"))

    def is_approved(self) -> bool:
        """False while *These are right — approve* is still on the screen. The correction turn
        must leave it False (FR-008): a card that answers a correction by approving itself has
        taken a decision that was not offered."""
        return self.page.get_by_role(
            "button", name=re.compile("these are right", re.I)).count() == 0

    def continue_onward(self) -> None:
        """The approved card's own onward door -- *Continue to step N* or, on the last stage,
        *Go to People*. Clicks whichever rendered rather than assuming a shape."""
        with self._bstep.step("founder takes the card's onward door") as h:
            link = self.page.locator(".actions").get_by_role(
                "link", name=re.compile("continue to step|go to people", re.I))
            if link.count() > 0:
                link.first.click()
            else:
                match = re.search(r"(/p/[^/?#]+)", self.page.url)
                self.page.goto(f"{self.base_url}{match.group(1)}", wait_until="load")
            self.page.wait_for_selector(".chat, .ppl, .role, .ocards", timeout=20_000)
            h.add_screenshot(self._bstep.screenshot("review-onward"))


# --------------------------------------------------------------------------------- CorrectionChat

class CorrectionChat:
    """`components/review/CorrectionChat.tsx` -- the founder says what they meant and the agent
    redoes one line, in the same card (mockup screen 2; keel-cloud spec 030's
    `POST /v2/inference-interactions/{id}/corrections`).

    This is the one place the smoke's founder types free text after the walk, and it is box **B6**
    of S-004's nine.
    """

    COMPOSER_LABEL = "Say what you meant…"

    def __init__(self, page: Page, recorder: Recorder, *, party: str = "founder"):
        self.page = page
        self._bstep = _BrowserStep(recorder, page, party)
        self._interaction_id: str | None = None

    def _scope(self):
        if self._interaction_id is None:
            self._interaction_id = self._bstep.recorder.new_interaction_id()
        return self._bstep.recorder.interaction("ui_visit", self._interaction_id)

    def is_visible(self) -> bool:
        return self.page.locator(".chat .chat__composer").count() > 0

    def turns(self) -> list[dict[str, str]]:
        out: list[dict[str, str]] = []
        msgs = self.page.locator(".chat__body .msg")
        for i in range(msgs.count()):
            msg = msgs.nth(i)
            classes = msg.get_attribute("class") or ""
            out.append({
                "who": "you" if "you" in classes else "agent",
                "text": _safe_text(lambda m=msg: m.locator(".bub").first.inner_text()),
            })
        return out

    def changes(self) -> list[str]:
        """The before-and-after lines the agent's own answer carries (`div.diffline`, rendered
        `<s>{before}</s> → {after}`)."""
        return _safe_all_texts(self.page, ".chat__body .diffline")

    def send(self, message: str, *, timeout_s: float = 90) -> dict[str, Any]:
        """Types the correction, sends it, and waits for the agent's answer to land in the same
        card. Returns `{turns, changes}`."""
        with self._scope():
            with self._bstep.step(f"founder says what they meant: {message[:60]!r}") as h:
                before = len(self.turns())
                box = self.page.get_by_label(self.COMPOSER_LABEL)
                box.wait_for(state="visible", timeout=15_000)
                box.fill(message)
                h.add_screenshot(self._bstep.screenshot("correction-typed"))
                self.page.locator(".chat").get_by_role(
                    "button", name=re.compile(r"^send$", re.I)).click()
                deadline = time.monotonic() + timeout_s
                while time.monotonic() < deadline:
                    turns = self.turns()
                    if len(turns) > before + 1 and turns[-1]["who"] == "agent":
                        break
                    self.page.wait_for_timeout(500)
                h.capture_text("screen", "review_card")
                h.capture_text("review_card", _screen_text(self.page, ".card.openc"))
                # The card is still on screen behind the chat, so this visit is judged as the
                # review card it is: ORI-U1 wants the project's identity and ORI-U4 wants the
                # *asked first* block, and both are right here to be read.
                Shell(self.page).capture_identity(h)
                block = self.page.locator(".card.openc .who", has=self.page.locator("dl.qa")).first
                if block.count() > 0:
                    h.capture_text("asked_first", _safe_text(lambda: block.inner_text()))
                h.capture_text("correction_turns", json.dumps(self.turns()))
                h.add_screenshot(self._bstep.screenshot("correction-answered"))
        return {"turns": self.turns(), "changes": self.changes()}


# -------------------------------------------------------------------------------------- Overview

class Overview:
    """`routes/founder/OverviewRoute.tsx` -- where it stands (mockup screen 4): the
    lines-have-answers bar, the four-count legend, *What this says*, one card per stage, and the
    Download link."""

    LEGEND_WORDS = ("holding up", "not holding up", "people disagree", "not tested")

    def __init__(self, page: Page, *args: Any, party: str = "founder"):
        self.page = page
        recorder, self.base_url = _split_recorder_and_base(args, page)
        self._bstep = _BrowserStep(recorder, page, party)
        self._interaction_id: str | None = None

    def _scope(self):
        if self._interaction_id is None:
            self._interaction_id = self._bstep.recorder.new_interaction_id()
        return self._bstep.recorder.interaction("ui_visit", self._interaction_id)

    # ------------------------------------------------------------------------------------- reads

    def evidence_line(self) -> str:
        return _safe_text(lambda: self.page.locator(".evidence__title").first.inner_text())

    def percent_line(self) -> str:
        return _safe_text(lambda: self.page.locator(".evidence__pct").first.inner_text())

    def people_line(self) -> str:
        return _safe_text(lambda: self.page.locator(".evidence__people span").first.inner_text())

    def lines_with_answers(self) -> tuple[int, int] | None:
        """`(have, total)` off *N of T lines have answers*, or `None` when the bar never
        rendered."""
        match = re.search(r"(\d+) of (\d+) lines? have answers", self.evidence_line())
        return (int(match.group(1)), int(match.group(2))) if match else None

    def legend(self) -> dict[str, int]:
        """The four counts, by their own founder-facing words rather than by position -- keel-web
        renders `<span class="up"><i/>{n} holding up</span>` and its neighbours."""
        out: dict[str, int] = {}
        for cls, word in zip(("up", "down", "split", "none"), self.LEGEND_WORDS):
            text = _safe_text(lambda c=cls: self.page.locator(f".legend .{c}").first.inner_text())
            match = re.search(r"(\d+)", text)
            out[word] = int(match.group(1)) if match else 0
        return out

    def what_this_says(self) -> str:
        return _safe_text(lambda: self.page.locator(".next").first.inner_text())

    def stage_cards(self) -> list[dict[str, str]]:
        """`{bet, status, claim, counts, must, see}` per card, in rendered order."""
        out: list[dict[str, str]] = []
        cards = self.page.locator(".ocards .card")
        for i in range(cards.count()):
            card = cards.nth(i)
            out.append({
                "bet": _safe_text(lambda c=card: c.locator(".bet").first.inner_text()),
                "status": _safe_text(lambda c=card: c.locator(".card-top .status").first.inner_text()),
                "claim": _safe_text(lambda c=card: c.locator("p.claim").first.inner_text()),
                "counts": _safe_text(lambda c=card: c.locator(".counts").first.inner_text()),
                "must": _safe_text(lambda c=card: c.locator(".must").first.inner_text()),
                "see": _safe_text(lambda c=card: c.locator(".see").first.inner_text()),
            })
        return out

    def download_link_text(self) -> str:
        return _safe_text(lambda: self.page.locator(".evidence__people a").first.inner_text())

    # ----------------------------------------------------------------------------------- actions

    def open(self, project_id: str, *, state_reader: StateReader | None = None) -> dict[str, Any]:
        with self._scope():
            with self._bstep.step("founder opens the overview") as h:
                self.page.goto(f"{self.base_url}/p/{project_id}", wait_until="load")
                self.page.wait_for_selector(".ocards, .guided-step", timeout=30_000)
                self._capture(h)
                _capture_state(h, project_id, state_reader)
                h.add_screenshot(self._bstep.screenshot("overview"))
        return {"evidence": self.evidence_line(), "legend": self.legend()}

    def recapture(self, *, slug: str = "overview-again") -> None:
        with self._scope():
            with self._bstep.step("founder reads the overview again") as h:
                self._capture(h)
                h.add_screenshot(self._bstep.screenshot(slug))

    def _capture(self, h: StepHandle) -> None:
        h.capture_text("screen", "overview")
        h.capture_text("overview", _screen_text(self.page, ".shell__main"))
        h.capture_text("evidence_line", self.evidence_line())
        Shell(self.page).capture_identity(h)
        affordance = _safe_all_texts(self.page, ".ocards .see, .evidence__people a")
        if affordance:
            h.capture_text("affordance", "\n".join(affordance))

    def open_card(self, stage_label: str) -> None:
        with self._scope():
            with self._bstep.step(f"founder opens the {stage_label!r} card") as h:
                self.page.locator("a.card-link", has_text=stage_label).first.click()
                _wait_for_url_change(self.page, lambda url: "/s/" in url)
                h.add_screenshot(self._bstep.screenshot("overview-open-card"))

    def download(self) -> None:
        """*Download as PDF* -- an `<a href="/p/:id/print">`, not a button. `PrintPage` stubs
        `window.print` before the route mounts; this follows the link the founder actually sees."""
        with self._scope():
            with self._bstep.step("founder takes Download") as h:
                self.page.locator(".evidence__people a").first.click()
                _wait_for_url_change(self.page, lambda url: url.endswith("/print"))
                h.add_screenshot(self._bstep.screenshot("overview-download"))


# ------------------------------------------------------------------- OpenedCard / SaidBox / modal

class OpenedCard:
    """`StageRoute.tsx`'s `OpenedCard` -- the framed, approved card once people have answered
    (mockup screen 5): *What it measures*, one strip per line, the dots, and the median tick.

    Two mechanics are recorded here rather than left to a scenario:

    - **The row is the click target, not the caret glyph.** `span.caret` is a `<span>`; the handler
      lives on the whole `div.strip` and deliberately ignores clicks that land on `svg`, `.said`
      or a `button` (research R7). Clicking the caret works only by accident of hit-testing, and
      D5's opener judge exercises the row.
    - **SVG text is not `inner_text`.** The band label (*you said 1 to 2*), the tick numbers and
      the unit all live in `<text>` inside the strip's `<svg>`, which Chromium's `innerText` does
      not return. The `opened_card` capture appends them explicitly, or the fact registry's
      `band.*` would be unprovable on the one screen that renders it.
    """

    def __init__(self, page: Page, *args: Any, party: str = "founder"):
        self.page = page
        recorder, self.base_url = _split_recorder_and_base(args, page)
        self._bstep = _BrowserStep(recorder, page, party)
        self._interaction_id: str | None = None

    def _scope(self):
        if self._interaction_id is None:
            self._interaction_id = self._bstep.recorder.new_interaction_id()
        return self._bstep.recorder.interaction("ui_visit", self._interaction_id)

    def _card(self):
        return self.page.locator(".card.openc").first

    # ------------------------------------------------------------------------------------- reads

    def claim(self) -> str:
        return _safe_text(lambda: self._card().locator("p.claim").first.inner_text())

    def status_word(self) -> str:
        return _safe_text(lambda: self._card().locator(".card-top .status").first.inner_text())

    def counts_text(self) -> str:
        return _safe_text(lambda: self._card().locator(".counts").first.inner_text())

    def deal_breakers_text(self) -> str:
        return _safe_text(lambda: self._card().locator(".must").first.inner_text())

    def what_it_measures(self) -> str:
        return _safe_text(lambda: self._card().locator(".measures .hint").first.inner_text())

    def key_legend(self) -> list[str]:
        """The strip key's own four lines -- what a filled dot, a hollow dot, the band and the
        median mean, in the founder's words (`StripKey`)."""
        return _safe_all_texts(self.page, ".key > span")

    def _strip(self, heading: str):
        return self.page.locator(".strip", has_text=heading).first

    def strips(self) -> list[dict[str, Any]]:
        """One row per line, in rendered order: `{number, heading, deal_breaker, you_said, status,
        counts_note, read_line, open, dots, median}`."""
        out: list[dict[str, Any]] = []
        rows = self.page.locator(".strip")
        for i in range(rows.count()):
            row = rows.nth(i)
            classes = row.get_attribute("class") or ""
            status_node = row.locator(".strip__status").first
            out.append({
                "number": _safe_text(lambda r=row: r.locator(".b-num").first.inner_text()),
                "heading": _safe_text(lambda r=row: r.locator(".strip__head > b").first.inner_text()),
                "deal_breaker": row.locator(".db").count() > 0,
                "you_said": _safe_text(lambda r=row: r.locator(".strip__you").first.inner_text()),
                "status": _safe_text(lambda s=status_node: s.inner_text()),
                "counts_note": _safe_text(lambda s=status_node: s.locator(".sub").first.inner_text()),
                "read_line": _safe_text(lambda r=row: r.locator(".strip__read").first.inner_text()),
                "open": "open" in classes,
                "dots": self._dots_of(row),
                "median": row.locator("[data-testid='median-tick']").count() > 0,
                "band_label": self._svg_text(row),
            })
        return out

    @staticmethod
    def _dots_of(row) -> list[str]:
        """Every person's own mark on this strip, by the `aria-label` keel-web gives it -- a
        `<circle>` for an Interval, a `<rect>` for a Choice."""
        nodes = row.locator("svg [role='button'][aria-label]")
        return [nodes.nth(i).get_attribute("aria-label") or "" for i in range(nodes.count())]

    @staticmethod
    def _svg_text(row) -> str:
        nodes = row.locator("svg text")
        return " ".join((nodes.nth(i).text_content() or "").strip() for i in range(nodes.count()))

    def has_median(self, heading: str) -> bool:
        """`line[data-testid="median-tick"]` -- the one testid keel-web has, and exactly the right
        handle: where the entry's `expected.standings` gives no `median`, the screen must show
        none, and an invented midpoint is a red run (research R10)."""
        return self._strip(heading).locator("[data-testid='median-tick']").count() > 0

    def strip(self, heading: str) -> dict[str, Any]:
        return next(s for s in self.strips() if heading in s["heading"])

    def dots(self, heading: str) -> list[str]:
        return self._dots_of(self._strip(heading))

    # ----------------------------------------------------------------------------------- actions

    def open(self, project_id: str, stage: str, *,
             expectations: dict[str, str] | None = None,
             drifts: dict[str, str] | None = None,
             state_reader: StateReader | None = None) -> dict[str, Any]:
        """`expectations` and `drifts` map a line's heading to its own `INTERVAL`/`CHOICE` and its
        wire drift. They are not read off the screen because they are not *on* the screen -- they
        are what GUI-U4 judges the screen's status words against, and a page object that inferred
        them from the picture it is checking would be marking its own homework."""
        with self._scope():
            with self._bstep.step(f"founder opens the {stage.lower()} card") as h:
                self.page.goto(f"{self.base_url}/p/{project_id}/s/{stage}", wait_until="load")
                self._card().locator(".bet").wait_for(state="visible", timeout=65_000)
                self._capture(h, stage, expectations, drifts)
                _capture_state(h, project_id, state_reader)
                h.add_screenshot(self._bstep.screenshot(f"opened-{stage.lower()}"))
        return {"status": self.status_word(), "claim": self.claim()}

    def recapture(self, stage: str, *, expectations: dict[str, str] | None = None,
                  drifts: dict[str, str] | None = None, slug: str = "opened-again") -> None:
        with self._scope():
            with self._bstep.step(f"founder reads the {stage.lower()} card again") as h:
                self._capture(h, stage, expectations, drifts)
                h.add_screenshot(self._bstep.screenshot(slug))

    def _capture(self, h: StepHandle, stage: str, expectations, drifts) -> None:
        strips = self.strips()
        h.capture_text("screen", "opened_card")
        h.capture_text("stage", stage)
        h.capture_text("stage_identity", _safe_text(
            lambda: self._card().locator(".bet").first.inner_text()))
        h.capture_text("opened_card", _screen_text(self.page, ".card.openc"))
        h.capture_text("belief_statuses", json.dumps([
            {"heading": s["heading"], "status": s["status"],
             "expectation": (expectations or {}).get(s["heading"], ""),
             "drift": (drifts or {}).get(s["heading"], "")}
            for s in strips]))
        names = sorted({name for s in strips for name in s["dots"] if name})
        if names:
            h.capture_text("participant_names", "\n".join(names))
        Shell(self.page).capture_identity(h)

    def toggle_line(self, heading: str) -> None:
        """Opens (or closes) one line. The whole row is the click target -- see the class
        docstring -- so this clicks `div.strip__head`, never the caret glyph."""
        with self._scope():
            with self._bstep.step(f"founder opens the line {heading!r}") as h:
                self._strip(heading).locator(".strip__head").first.click()
                self.page.wait_for_timeout(250)
                h.add_screenshot(self._bstep.screenshot("strip-toggled"))

    def ensure_open(self, heading: str) -> None:
        """The line whose verdict matches the card's own status already renders open
        (`StageRoute.tsx`'s default-open rule), and a second click would collapse it."""
        if "open" not in (self._strip(heading).get_attribute("class") or ""):
            self.toggle_line(heading)

    def click_dot(self, heading: str, person: str) -> None:
        """One person's own mark on one line -- a D5 opener, judged by what it reveals."""
        with self._scope():
            with self._bstep.step(f"founder clicks {person}'s answer on {heading!r}") as h:
                self._strip(heading).locator(
                    f"svg [role='button'][aria-label={json.dumps(person)}]").first.click()
                self.page.locator(".said").first.wait_for(state="visible", timeout=10_000)
                h.capture_text("participant_names", person)
                h.add_screenshot(self._bstep.screenshot("strip-dot-open"))

    def strip_locator(self, heading: str):
        """The raw locator, for `harness/doors.py`'s D5 walk -- which exercises controls this
        class does not otherwise name."""
        return self._strip(heading)


class SaidBox:
    """`components/strip/SaidBox.tsx` -- the popover one dot opens: who, what kind of person, what
    they wrote, and how it was read (*Read as anchored… / a number offered as a guess…*)."""

    def __init__(self, page: Page, recorder: Recorder, *, party: str = "founder"):
        self.page = page
        self._bstep = _BrowserStep(recorder, page, party)

    def _box(self):
        return self.page.locator(".said").first

    def is_open(self) -> bool:
        return self.page.locator(".said").count() > 0

    def read(self) -> dict[str, str]:
        box = self._box()
        return {
            "name": _safe_text(lambda: box.locator(".n").first.inner_text()),
            "kind": _safe_text(lambda: box.locator(".k").first.inner_text()),
            "words": _safe_text(lambda: box.locator(".w").first.inner_text()),
            "read_as": _safe_text(lambda: box.locator(".r").first.inner_text()),
            "see_all": _safe_text(lambda: box.locator(".a button").first.inner_text()),
        }

    def see_all(self) -> None:
        with self._bstep.step("founder asks to see all of that person's answers") as h:
            self._box().locator(".a button").first.click()
            self.page.locator(".pop[role='dialog']").wait_for(state="visible", timeout=10_000)
            h.add_screenshot(self._bstep.screenshot("said-see-all"))

    def close(self) -> None:
        with self._bstep.step("founder closes the answer popover") as h:
            self._box().locator("button.x").first.click()
            self.page.wait_for_timeout(200)
            h.add_screenshot(self._bstep.screenshot("said-closed"))


class AnswersModal:
    """`components/people/PersonAnswersModal.tsx` -- one person's whole page, read back: their
    story in their own words and every pick with the question that asked it.

    Four ways to close (`FR-018`'s D5): the scrim, the `×`, the footer *Close*, and `Escape`.
    """

    CLOSERS = ("scrim", "x", "footer", "escape")

    def __init__(self, page: Page, recorder: Recorder, *, party: str = "founder"):
        self.page = page
        self._bstep = _BrowserStep(recorder, page, party)
        self._interaction_id: str | None = None

    def _scope(self):
        if self._interaction_id is None:
            self._interaction_id = self._bstep.recorder.new_interaction_id()
        return self._bstep.recorder.interaction("ui_visit", self._interaction_id)

    def _pop(self):
        return self.page.locator(".pop[role='dialog']").first

    def is_open(self) -> bool:
        return self.page.locator(".pop[role='dialog']").count() > 0

    def read(self) -> dict[str, Any]:
        pop = self._pop()
        picks: list[dict[str, str]] = []
        rows = pop.locator("p.p-q")
        for i in range(rows.count()):
            row = rows.nth(i)
            picks.append({
                "asked": _safe_text(lambda r=row: r.inner_text()),
                "picked": _safe_text(lambda r=row: r.locator(".p-a").first.inner_text()),
                "line": _safe_text(lambda r=row: r.locator(".p-r").first.inner_text()),
            })
        return {
            "title": _safe_text(lambda: pop.locator("h2").first.inner_text()),
            "kicker": _safe_text(lambda: pop.locator(".pop__kicker").first.inner_text()),
            "story": _safe_text(lambda: pop.locator("p.story").first.inner_text()),
            "section": _safe_text(lambda: pop.locator(".p-sec").first.inner_text()),
            "picks": picks,
        }

    def capture(self, person: str) -> dict[str, Any]:
        body = self.read()
        with self._scope():
            with self._bstep.step(f"founder reads all of {person}'s answers") as h:
                h.capture_text("screen", "answers_modal")
                h.capture_text("answers_modal", _screen_text(self.page, ".pop[role='dialog']"))
                h.capture_text("participant_names", person)
                Shell(self.page).capture_identity(h)
                h.add_screenshot(self._bstep.screenshot("answers-modal"))
        return body

    def close(self, *, via: str = "footer") -> None:
        with self._scope():
            with self._bstep.step(f"founder closes the answers modal ({via})") as h:
                if via == "scrim":
                    self.page.locator(".scrim").first.click()
                elif via == "x":
                    self._pop().locator("button.x").first.click()
                elif via == "escape":
                    self.page.keyboard.press("Escape")
                else:
                    self._pop().get_by_role(
                        "button", name=re.compile(r"^close$", re.I)).first.click()
                self.page.locator(".pop[role='dialog']").wait_for(state="detached", timeout=10_000)
                h.add_screenshot(self._bstep.screenshot("answers-modal-closed"))


# ------------------------------------------------------------------------------------- PrintPage

class PrintPage:
    """`routes/founder/PrintRoute.tsx` -- the download (mockup screen 6), outside the project
    shell: no brand row, no side nav, nothing but the sheets.

    **`window.print()` fires on mount.** `PrintRoute` calls it as soon as the data lands, so an
    unstubbed visit hangs the walk on a native dialog no Playwright locator can dismiss. `open()`
    installs `window.print = () => {}` with `add_init_script` **before** navigating, exactly as
    keel-web's own e2e suite does (research R9). That is a harness mechanic, recorded as one; the
    PDF itself is out of scope and no scenario opens one.
    """

    COLUMNS = ("What it measures", "You said", "The answers")

    def __init__(self, page: Page, *args: Any, party: str = "founder"):
        self.page = page
        recorder, self.base_url = _split_recorder_and_base(args, page)
        self._bstep = _BrowserStep(recorder, page, party)
        self._interaction_id: str | None = None
        self._stubbed = False

    def _scope(self):
        if self._interaction_id is None:
            self._interaction_id = self._bstep.recorder.new_interaction_id()
        return self._bstep.recorder.interaction("ui_visit", self._interaction_id)

    def stub_print(self) -> None:
        """Idempotent, and safe to call before following the founder's own *Download as PDF*
        link rather than navigating by URL."""
        if not self._stubbed:
            self.page.add_init_script("window.print = () => {};")
            self._stubbed = True

    # ------------------------------------------------------------------------------------- reads

    def sheets(self) -> list[str]:
        return _safe_all_texts(self.page, ".pages > .page")

    def title_page(self) -> dict[str, str]:
        title = self.page.locator(".ptitle").first
        return {
            "kicker": _safe_text(lambda: title.locator(".pkicker").first.inner_text()),
            "name": _safe_text(lambda: title.locator("h1").first.inner_text()),
            "sub": _safe_text(lambda: title.locator("p.psub").first.inner_text()),
            "meta": " ".join(_safe_all_texts(self.page, ".ptitle p.pmeta")),
        }

    def headings(self) -> list[str]:
        return _safe_all_texts(self.page, ".pages h2")

    def table_columns(self) -> list[list[str]]:
        """The four `<th>` of each per-stage table -- three named columns and one deliberately
        unnamed status column."""
        out: list[list[str]] = []
        tables = self.page.locator("table.ptab")
        for i in range(tables.count()):
            out.append([h.strip() for h in tables.nth(i).locator("thead th").all_inner_texts()])
        return out

    def table_rows(self, index: int = 0) -> list[list[str]]:
        rows = self.page.locator("table.ptab").nth(index).locator("tbody tr")
        return [[c.strip() for c in rows.nth(i).locator("td").all_inner_texts()]
                for i in range(rows.count())]

    def quotes(self) -> list[str]:
        return _safe_all_texts(self.page, ".pquotes p")

    def fresh_page_rule(self) -> str | None:
        """*A stage starts on a fresh page*, read off **the stylesheet's own rule** and never off
        a pixel offset (research R9): the `@media print` block's `.page + .page` declaration.
        `None` when no such rule exists, which is the finding rather than a crash."""
        return self.page.evaluate(
            r"""() => {
                for (const sheet of Array.from(document.styleSheets)) {
                  let rules;
                  try { rules = Array.from(sheet.cssRules || []); } catch (e) { continue; }
                  for (const rule of rules) {
                    if (!rule.media || !String(rule.conditionText || rule.media.mediaText).includes('print')) continue;
                    for (const inner of Array.from(rule.cssRules || [])) {
                      if (inner.selectorText && inner.selectorText.replace(/\s+/g, ' ').includes('.page + .page')) {
                        return inner.style.getPropertyValue('break-before')
                            || inner.style.getPropertyValue('page-break-before') || null;
                      }
                    }
                  }
                }
                return null;
            }""")

    def has_founder_chrome(self) -> bool:
        """The download page is its own page (spec 013 FR-033): no brand row, no side nav."""
        return (self.page.locator(".side-nav").count() > 0
                or self.page.locator(".brandrow").count() > 0)

    # ----------------------------------------------------------------------------------- actions

    def open(self, project_id: str) -> None:
        self.stub_print()
        with self._scope():
            with self._bstep.step("founder opens the download") as h:
                self.page.goto(f"{self.base_url}/p/{project_id}/print", wait_until="load")
                self.page.locator(".pages .page").first.wait_for(state="visible", timeout=30_000)
                self._capture(h)
                h.add_screenshot(self._bstep.screenshot("print"))

    def capture_here(self) -> None:
        """For a caller that reached `/print` by clicking the founder's own link."""
        with self._scope():
            with self._bstep.step("founder reads the download") as h:
                self.page.locator(".pages .page").first.wait_for(state="visible", timeout=30_000)
                self._capture(h)
                h.add_screenshot(self._bstep.screenshot("print"))

    def _capture(self, h: StepHandle) -> None:
        h.capture_text("screen", "print")
        h.capture_text("download", _screen_text(self.page, ".pages"))
        h.capture_text("identity", self.title_page()["name"])
        names = _safe_all_texts(self.page, ".pquotes p span")
        if names:
            h.capture_text("participant_names", "\n".join(names))

# ------------------------------------------------------------------------------------------ People

class People:
    """`routes/founder/PeopleRoute.tsx` -- P1-P9: role cards, the three-step send popup, the
    two-actor table, the answers popup, the reading progress, and the toast."""

    def __init__(self, page: Page, *args: Any, party: str = "founder"):
        self.page = page
        recorder, self.base_url = _split_recorder_and_base(args, page)
        self._bstep = _BrowserStep(recorder, page, party)
        self._interaction_id: str | None = None

    def _scope(self):
        if self._interaction_id is None:
            self._interaction_id = self._bstep.recorder.new_interaction_id()
        return self._bstep.recorder.interaction("ui_visit", self._interaction_id)

    def open(self, project_id: str, *, state_reader: StateReader | None = None) -> dict[str, Any]:
        with self._scope():
            with self._bstep.step("founder opens People") as h:
                self.page.goto(f"{self.base_url}/p/{project_id}/people", wait_until="load")
                self.page.wait_for_selector(".role, table.ppl", timeout=15_000)
                h.capture_text("screen", "people")
                Shell(self.page).capture_identity(h)
                # P1's role cards ARE the invite screen (journeys §1.4: "People opens on the
                # kinds of person the beliefs depend on, one card per role") -- every role's
                # label, invited or not, is FID's `invite_screen` hop here, not only the roles
                # the send popup is later opened for.
                role_labels = _safe_all_texts(self.page, ".role__label")
                if role_labels:
                    h.capture_text("invite_screen", "\n".join(role_labels))
                names = _safe_all_texts(self.page, "table.ppl td b")
                if names:
                    h.capture_text("participant_names", "\n".join(names))
                _capture_state(h, project_id, state_reader)
                h.add_screenshot(self._bstep.screenshot("people"))
        any_invited = self.page.locator("table.ppl").count() > 0
        return {"any_invited": any_invited}

    # ------------------------------------------------------------------------------ role cards

    def role_cards(self) -> list[dict[str, str]]:
        """`{label, meta, about}` per `.role` card (P1/P8)."""
        cards = self.page.locator(".role")
        out: list[dict[str, str]] = []
        for i in range(cards.count()):
            card = cards.nth(i)
            out.append({
                "label": _safe_text(lambda c=card: c.locator(".role__label").first.inner_text()),
                "meta": _safe_text(lambda c=card: c.locator(".role__meta").first.inner_text()),
                "about": _safe_text(lambda c=card: c.locator(".role__about").first.inner_text()),
            })
        return out

    def switch_to_who_tab(self) -> None:
        with self._scope():
            with self._bstep.step("founder switches to Who's been asked") as h:
                self.page.locator(".toggle button", has_text=re.compile("who", re.I)).click()
                self.page.wait_for_selector("table.ppl", timeout=10_000)
                h.add_screenshot(self._bstep.screenshot("people-who-tab"))

    def switch_to_kinds_tab(self) -> None:
        """P8: the toggle's other side -- the role cards again, now with per-role counts."""
        with self._scope():
            with self._bstep.step("founder switches to Kinds of people") as h:
                self.page.locator(".toggle button", has_text=re.compile("kinds", re.I)).click()
                self.page.wait_for_selector(".role", timeout=10_000)
                h.add_screenshot(self._bstep.screenshot("people-kinds-tab"))

    # -------------------------------------------------------------------------- the send popup

    def open_send_popup(self, role_label: str) -> None:
        """P2 -- opens the three-step send popup for the role card matching `role_label`."""
        with self._scope():
            with self._bstep.step(f"founder starts sending the questions for {role_label!r}") as h:
                card = self.page.locator(".role", has_text=role_label).first
                card.get_by_role("button", name=re.compile("send the questions", re.I)).click()
                self.page.locator(".pop[role='dialog']").wait_for(state="visible", timeout=10_000)
                h.capture_text("invite_screen", role_label)
                h.add_screenshot(self._bstep.screenshot("people-send-popup-who"))

    def fill_who(self, person_name: str, about: str | None = None) -> None:
        """P2's two fields: the person's name, and (optionally) a replacement for the agent's own
        prefilled about-line."""
        with self._scope():
            with self._bstep.step(f"founder names {person_name!r}") as h:
                self.page.get_by_label("Their name").fill(person_name)
                about_field = self.page.get_by_label(re.compile("a short line", re.I))
                if about is not None:
                    about_field.fill(about)
                about_value = _safe_text(about_field.input_value)
                h.capture_text("invite_screen", f"{person_name}\n{about_value}")
                h.capture_text("participant_names", person_name)
                h.add_screenshot(self._bstep.screenshot("people-send-popup-who-filled"))

    def go_to_preview(self) -> str:
        """P3 -- *Next — see what they'll be asked →*; returns the rendered preview text (the
        participant page's own top, then the sections by stage -- design §7.2's own promise: "the
        preview, as the person will see it")."""
        with self._scope():
            with self._bstep.step("founder previews what they'll be asked") as h:
                self.page.get_by_role("button", name=re.compile("next", re.I)).click()
                self.page.locator(".preview").wait_for(state="visible", timeout=10_000)
                preview = _safe_text(lambda: self.page.locator(".preview").first.inner_text())
                h.capture_text("invite_screen", preview)
                h.add_screenshot(self._bstep.screenshot("people-send-popup-preview"))
        return preview

    def generate_link(self, first_name: str | None = None) -> str:
        """P3→P4 -- *Generate <name>'s link*; waits for the link box and returns the URL shown --
        never reconstructed."""
        with self._scope():
            with self._bstep.step("founder generates the invitation link") as h:
                self.page.get_by_role("button", name=re.compile("generate", re.I)).click()
                link_box = self.page.locator("p.linkbox")
                link_box.wait_for(state="visible", timeout=15_000)
                url = _safe_text(lambda: link_box.inner_text()).strip()
                h.record_wire(None, {"invite_url_shown_by_ui": url})
                h.add_screenshot(self._bstep.screenshot("people-send-popup-link"))
                if not url:
                    h.fail("the send popup showed an empty link")
                    raise AssertionError("the send popup showed an empty link")
        return url

    def copy_link(self) -> None:
        with self._scope():
            with self._bstep.step("founder copies the link") as h:
                self.page.get_by_role("button", name=re.compile(r"^copy link$", re.I)).click()
                self.page.get_by_text("Copied").wait_for(state="visible", timeout=5_000)
                h.add_screenshot(self._bstep.screenshot("people-link-copied"))

    def close_popup(self, *, label: str = "Done") -> None:
        with self._scope():
            with self._bstep.step("founder closes the send popup") as h:
                self.page.get_by_role("button", name=re.compile(f"^{re.escape(label)}$|^close$", re.I)).click()
                self.page.wait_for_selector(".pop", state="detached", timeout=10_000)
                h.add_screenshot(self._bstep.screenshot("people-popup-closed"))

    # ------------------------------------------------------------------------------- the table

    def table_rows(self) -> list[dict[str, str]]:
        """`{person, kind, sent, their_answer, your_agent}` per `table.ppl tbody tr` (P5/P8)."""
        rows = self.page.locator("table.ppl tbody tr")
        out: list[dict[str, str]] = []
        for i in range(rows.count()):
            cells = rows.nth(i).locator("td")
            out.append({
                "person": _safe_text(lambda c=cells: c.nth(0).inner_text()),
                "kind": _safe_text(lambda c=cells: c.nth(1).inner_text()),
                "sent": _safe_text(lambda c=cells: c.nth(2).inner_text()),
                "their_answer": _safe_text(lambda c=cells: c.nth(3).inner_text()),
                "your_agent": _safe_text(lambda c=cells: c.nth(4).inner_text()) if cells.count() > 4 else "",
            })
        return out

    def open_answers_popup(self, first_name: str) -> None:
        """P9 -- *See <name>'s answers*, from the table row's own read link."""
        with self._scope():
            with self._bstep.step(f"founder reads {first_name}'s answers") as h:
                self.page.get_by_role(
                    "button", name=re.compile(f"see {re.escape(first_name)}", re.I)).click()
                self.page.locator(".pop").wait_for(state="visible", timeout=10_000)
                h.capture_text("participant_names", first_name)
                h.add_screenshot(self._bstep.screenshot("people-answers-popup"))

    def answers_popup_text(self) -> dict[str, Any]:
        """The read-only popup's own words (`.pop` with `.preview` inside): `{title, note,
        qa: [{text, answer}]}` -- the answer text is the participant's own, verbatim
        (`participant_page` FID hop, reachable from a `ui_visit` per `HOP_INTERACTION_TYPES`)."""
        with self._scope():
            with self._bstep.step("founder reads the popup's own words") as h:
                pop = self.page.locator(".pop")
                title = _safe_text(lambda: pop.locator("h2").first.inner_text())
                note = _safe_text(lambda: pop.locator(".hint").first.inner_text())
                qa: list[dict[str, str]] = []
                blocks = pop.locator(".preview .p-q")
                for i in range(blocks.count()):
                    block = blocks.nth(i)
                    full = _safe_text(lambda b=block: b.inner_text())
                    answer = _safe_text(lambda b=block: b.locator(".p-a").first.inner_text())
                    qa.append({"text": full, "answer": answer})
                text = "\n".join([title, note] + [row["text"] for row in qa])
                h.capture_text("participant_page", text)
        return {"title": title, "note": note, "qa": qa}

    def close_answers_popup(self) -> None:
        with self._scope():
            with self._bstep.step("founder closes the answers popup") as h:
                self.page.get_by_role("button", name=re.compile(r"^close$", re.I)).click()
                self.page.wait_for_selector(".pop", state="detached", timeout=10_000)
                h.add_screenshot(self._bstep.screenshot("people-answers-popup-closed"))

    # -------------------------------------------------------------------- reading (agent_turn)

    def read_all_and_wait(self, *, timeout_s: float = 60) -> dict[str, str]:
        """*Have your agent read the N new answers* (P5→P6→P7): clicks the button, then waits on
        the screen's own progress line and per-row *Reading…* state, then the completion toast --
        never a wire poll of its own."""
        with self._scope():
            with self._bstep.step("founder has the agent read the new answers") as h:
                self.page.get_by_role("button", name=re.compile("have your agent read", re.I)).click()
                progress = self.page.locator(".bulk")
                if progress.count() > 0:
                    h.capture_text("waiting_text", _safe_text(lambda: progress.first.inner_text()))
                    h.add_screenshot(self._bstep.screenshot("people-reading-progress"))
                toast = self.page.locator(".toast[role='status']")
                toast.wait_for(state="visible", timeout=timeout_s * 1000)
                toast_text = _safe_text(lambda: toast.first.inner_text())
                h.capture_text("agent_reply", toast_text)
                h.add_screenshot(self._bstep.screenshot("people-reading-done-toast"))
        return {"toast_text": toast_text}

    def toast_text(self) -> str:
        return _safe_text(lambda: self.page.locator(".toast").first.inner_text())

    def read_action_state(self) -> dict[str, Any]:
        """Spec 006-agent-optional (FR-003, US1 acceptance scenario 3): the *Have your agent read
        the N new answers* button's own enabled/disabled state, its rendered label, and whatever
        reason text sits beside it in `.actions` (the `.hint` line design's `landing`/`.locked`
        pattern for *New project* uses -- a reason shown beside a disabled action, not merely a
        refusal after a click). A pure getter, like `table_rows()`: records nothing of its own,
        so the caller decides which step/interaction this observation belongs to.

        `{present, enabled, label, reason}` -- `present=False` only if the actions row itself
        never rendered (a screen this file doesn't expect); the button is present and *enabled*
        whenever `unreadCount > 0` today, agent connected or not (this is exactly the gap spec
        006 predicts keel-web has not closed yet).
        """
        button = self.page.locator(".actions button.primary, .actions button.btn.primary").first
        if button.count() == 0:
            return {"present": False, "enabled": False, "label": "", "reason": ""}
        label = _safe_text(lambda: button.inner_text())
        enabled = button.is_enabled()
        reason = _safe_text(lambda: self.page.locator(".actions .hint").first.inner_text())
        return {"present": True, "enabled": enabled, "label": label, "reason": reason}

    def follow_toast_link(self) -> None:
        """The toast's own *See the overview →* -- app-level (bottom centre), asserted on the
        People page per spec edge cases ("assert it on the People page and again after See the
        overview")."""
        with self._scope():
            with self._bstep.step("founder follows the toast to the overview") as h:
                self.page.locator(".toast").get_by_role("link").click()
                _wait_for_url_change(self.page, lambda url: "/people" not in url)
                h.add_screenshot(self._bstep.screenshot("people-toast-to-overview"))


# ---------------------------------------------------------------------------------- Participant

# `ParticipantRoute.tsx`'s own words for the three taps, and the enum names keel-cloud sends them
# as. Matched by word first, by position second (the route does the same thing in reverse), so a
# copy change in either repo shows up as a mismatch rather than as a silently unclicked chip.
TAP_WORDS = {
    "HASNT_HAPPENED": "it hasn't happened to me",
    "CANT_RECALL": "it has, but I can't recall one",
    "RATHER_NOT_SAY": "rather not say",
}
TAP_ORDER = ("HASNT_HAPPENED", "CANT_RECALL", "RATHER_NOT_SAY")
#: The phrase that carries the meaning, whichever repo's wording rendered it.
TAP_NEEDLE = {"HASNT_HAPPENED": "hasn't happened", "CANT_RECALL": "recall",
              "RATHER_NOT_SAY": "rather not"}
OTHER_SAY_WHAT = "other, say what"


class ParticipantPage:
    """The stranger's page (`routes/participant/ParticipantRoute.tsx`, mockup screen 3), rewritten
    for measured beliefs: **one story, then picks**.

    What changed, and why the old `ParticipantBrowser` could not be patched into this: there is no
    consent screen and no *Start* -- the form is the page, and consent is starting it; there is no
    per-belief question with a free-text box each -- there is one story box per *anchor*, with its
    taps, and then a pick per selection; and a tap is an answer of its own that greys the story and
    gates that anchor's picks.

    **What this page must never show** is as much of its job as what it does: no belief statement,
    no band value, no `founderPhrase` and no expected option (design rule `Q5`). That is not
    asserted here -- a page object asserts nothing -- but the whole page's text is captured under
    the `participant_page` hop, which is what `evals/corpus_facts.py`'s `absent_hops` are scored
    against.
    """

    def __init__(self, page: Page, recorder: Recorder):
        self.page = page
        self._bstep = _BrowserStep(recorder, page, party="participant")
        self._interaction_id: str | None = None

    def _capture_page_text(self, h: StepHandle) -> None:
        h.capture_text("participant_page", _screen_text(self.page, "body"))

    def _scope(self):
        if self._interaction_id is None:
            self._interaction_id = self._bstep.recorder.new_interaction_id()
        return self._bstep.recorder.interaction("participant_visit", self._interaction_id)

    # ------------------------------------------------------------------------------------- reads

    def introduction(self) -> str:
        return _safe_text(lambda: self.page.locator("p.hello").first.inner_text())

    def hints(self) -> list[str]:
        return _safe_all_texts(self.page, ".iv > p.hint")

    def sections(self) -> list[str]:
        return _safe_all_texts(self.page, ".sect")

    def _anchor_blocks(self):
        """An anchor's own block is the `div.q` that carries a story box; a selection's block is a
        `div.q` nested inside that one's `div.picks`. Both share the class, which is why this is
        `:has(textarea.box)` rather than an index."""
        return self.page.locator("div.q:has(> textarea.box)")

    def anchors(self) -> list[dict[str, Any]]:
        """`{prompt, taps, selections}` per anchor, in rendered order."""
        out: list[dict[str, Any]] = []
        blocks = self._anchor_blocks()
        for i in range(blocks.count()):
            block = blocks.nth(i)
            out.append({
                "prompt": _safe_text(lambda b=block: b.locator("> p").first.inner_text()),
                "taps": [t.strip() for t in block.locator(".taps > .chip").all_inner_texts()],
                "selections": [
                    _safe_text(lambda s=s: s.locator("> p").first.inner_text())
                    for s in block.locator(".picks > div.q").all()],
            })
        return out

    def options_for(self, selection_prompt: str, *, anchor_prompt: str | None = None) -> list[str]:
        """The list this selection actually offered, **in order** -- FR-013's `expected.buckets`,
        read off the stranger's own screen. The ways out (`.opt.esc`) and the *other* box are
        excluded: the corpus's `buckets` are the scale, and the escapes sit beside it."""
        block = self._selection_block(selection_prompt, anchor_prompt=anchor_prompt)
        labels: list[str] = []
        # Each row is wrapped in a keyed `<div>` of its own so its reveal box can sit beside it
        # (`ParticipantRoute.tsx`'s `renderRow`), so `.opt` is a grandchild of `.opts`, never a
        # direct child. Live-confirmed the hard way: a `>` here reads every selection as offering
        # nothing at all.
        rows = block.locator(".opts .opt")
        for i in range(rows.count()):
            row = rows.nth(i)
            classes = row.get_attribute("class") or ""
            text = _safe_text(lambda r=row: r.inner_text()).strip()
            if "esc" in classes or text == OTHER_SAY_WHAT:
                continue
            labels.append(text)
        return labels

    def escapes_for(self, selection_prompt: str, *, anchor_prompt: str | None = None) -> list[str]:
        block = self._selection_block(selection_prompt, anchor_prompt=anchor_prompt)
        return [_safe_text(lambda r=r: r.inner_text()).strip()
                for r in block.locator(".opts .opt.esc").all()]

    def _anchor_block(self, prompt: str):
        needle = " ".join(prompt.split())[:60]
        blocks = self._anchor_blocks()
        for i in range(blocks.count()):
            block = blocks.nth(i)
            text = " ".join(_safe_text(lambda b=block: b.locator("> p").first.inner_text()).split())
            if needle in text:
                return block
        raise AssertionError(f"no story box on this page for the anchor {prompt[:60]!r}")

    def _selection_block(self, prompt: str, *, anchor_prompt: str | None = None):
        """The selection asking `prompt`, **scoped to its own anchor** when one is named.

        Two anchors can ask the identical question -- `05-paidly` asks *"Was that within the last
        twelve months?"* on both `A2c` (`S7`) and `A3` (`S10`) -- and a page-wide match on the
        prompt puts every `S10` pick into `S7`'s block, which reads on the wire as `S7` moving to
        `MIXED` and `S10` reading `UNTESTED` with nobody's answer at all. Live-confirmed
        (`runs/20260907T150329Z-s006-paidly`). The anchor is the scope that makes a prompt unique.
        """
        needle = " ".join(prompt.split())[:60]
        # `div.picks` is the anchor's **sibling**, not its child: `AnchorBlock` returns a fragment
        # of `<div class="q">…</div>` followed by `<div class="picks">…</div>`. So the scope is the
        # next `.picks` after this anchor's own block, which is exactly the picks that anchor gates.
        blocks = (self._anchor_block(anchor_prompt).locator(
                      "xpath=following-sibling::div[contains(@class,'picks')][1]"
                  ).locator("> div.q")
                  if anchor_prompt else self.page.locator(".picks > div.q"))
        for i in range(blocks.count()):
            block = blocks.nth(i)
            text = " ".join(_safe_text(lambda b=block: b.locator("> p").first.inner_text()).split())
            if needle in text:
                return block
        raise AssertionError(
            f"no selection asking {prompt[:60]!r}"
            + (f" under the anchor {anchor_prompt[:50]!r}" if anchor_prompt else " on this page"))

    def offers(self, prompt: str) -> bool:
        """Whether this page asks a given anchor or selection at all. A person offered an anchor
        their role is not asked is a **refusal**, not a shrug (spec edge case), and this is how a
        scenario proves the negative."""
        needle = " ".join(prompt.split())[:60]
        body = " ".join(_safe_text(lambda: self.page.locator(".iv").first.inner_text()).split())
        return needle in body

    # ----------------------------------------------------------------------------------- actions

    def open(self, url: str) -> None:
        """Opens exactly the URL the founder's send popup showed -- never reconstructed."""
        with self._scope():
            with self._bstep.step("the stranger opens their link") as h:
                self.page.goto(url, wait_until="load")
                self.page.locator(".iv p.hello").wait_for(state="visible", timeout=15_000)
                h.add_screenshot(self._bstep.screenshot("participant-opened"))
                self._capture_page_text(h)

    def tell_story(self, anchor_prompt: str, text: str | None, tap: str | None = None) -> None:
        """One anchor: the story, or a tap instead of one. A tap of *it hasn't happened to me*
        hides that anchor's picks entirely, which is the product's own rule and not this
        harness's."""
        with self._scope():
            with self._bstep.step(f"the stranger answers {anchor_prompt[:50]!r}") as h:
                block = self._anchor_block(anchor_prompt)
                if text:
                    block.locator("> textarea.box").first.fill(text)
                if tap:
                    chips = block.locator(".taps > .chip")
                    # keel-cloud composes the tap's own words ("It hasn't happened"), keel-web has
                    # its own constants ("it hasn't happened to me"), and neither is this repo's
                    # to fix -- so the match is on the phrase that carries the meaning, and the
                    # wire's own order is the fallback.
                    needle = TAP_NEEDLE.get(tap, "")
                    target = None
                    for i in range(chips.count()):
                        text = _safe_text(lambda c=chips.nth(i): c.inner_text()).strip().casefold()
                        if needle and needle in text:
                            target = chips.nth(i)
                            break
                    if target is None and tap in TAP_ORDER and chips.count() > TAP_ORDER.index(tap):
                        target = chips.nth(TAP_ORDER.index(tap))
                    if target is None:
                        raise AssertionError(
                            f"no tap on this anchor reads {needle!r} (offered: "
                            f"{chips.all_inner_texts()})")
                    target.click()
                    self.page.wait_for_timeout(150)
                h.add_screenshot(self._bstep.screenshot("participant-story"))

    def pick(self, selection_prompt: str, values: list[str], *, other_text: str | None = None,
             roughly: str | None = None, anchor_prompt: str | None = None) -> None:
        """One selection. `values` are the labels as the person reads them; a multi-select takes
        more than one. `other_text` fills the *other, say what* reveal and `roughly` the *say
        roughly* one -- both left `None` by every deterministic scenario, because the corpus
        records the bucket and not a number behind it, and inventing one would be inventing
        corpus data."""
        with self._scope():
            with self._bstep.step(f"the stranger picks {values} for {selection_prompt[:40]!r}") as h:
                block = self._selection_block(selection_prompt, anchor_prompt=anchor_prompt)
                for value in values:
                    row = self._option_row(block, value)
                    row.click()
                    self.page.wait_for_timeout(80)
                    label = _safe_text(lambda r=row: r.inner_text()).strip()
                    # The reveal is the row's *sibling*, inside the same keyed wrapper.
                    reveal = row.locator("xpath=..").locator(".opt__more input")
                    if label.endswith("say roughly") and roughly and reveal.count() > 0:
                        reveal.first.fill(roughly)
                    if label == OTHER_SAY_WHAT and other_text and reveal.count() > 0:
                        reveal.first.fill(other_text)
                h.add_screenshot(self._bstep.screenshot("participant-picked"))

    @staticmethod
    def _option_row(block, value: str):
        rows = block.locator(".opts .opt")
        wanted = " ".join(str(value).split()).casefold()
        for i in range(rows.count()):
            row = rows.nth(i)
            text = " ".join((row.inner_text() or "").split()).casefold()
            if text == wanted:
                return row
        raise AssertionError(
            f"no option on this selection reads {value!r} (offered: {rows.all_inner_texts()})")

    def answer_as(self, person, entry) -> dict[str, Any]:
        """Types one corpus person's whole page: their story (or tap) per anchor, then every pick
        their role's selections ask for.

        `person` is a `harness.corpus_script.PersonInputs`; `entry` the corpus entry it came from,
        which is what turns an anchor id into the prompt the screen shows. Returns
        `{anchors, picks, skipped}` -- `skipped` naming any pick whose selection this page never
        offered, which a scenario asserts on rather than this method deciding.
        """
        typed_anchors: list[str] = []
        typed_picks: list[str] = []
        skipped: list[str] = []
        for answer in person.anchors:
            anchor = entry.anchor(answer.anchor_id) or {}
            prompt = anchor.get("prompt") or ""
            if not self.offers(prompt):
                skipped.append(answer.anchor_id)
                continue
            self.tell_story(prompt, answer.text, tap=answer.tap)
            typed_anchors.append(answer.anchor_id)
        for pick in person.picks:
            owner, selection = None, None
            for anchor in entry.questionnaire.get("anchors") or []:
                for candidate in anchor.get("selections") or []:
                    if candidate["id"] == pick.selection_id:
                        owner, selection = anchor, candidate
            prompt = (selection or {}).get("prompt") or ""
            if not selection or not self.offers(prompt):
                skipped.append(pick.selection_id)
                continue
            # Scoped to the anchor that owns it: two anchors can ask the same question, and the
            # anchor is what tells them apart (`_selection_block`'s own note).
            self.pick(prompt, pick.values, anchor_prompt=(owner or {}).get("prompt"))
            typed_picks.append(pick.selection_id)
        with self._scope():
            with self._bstep.step(f"{person.person} has filled their page") as h:
                self._capture_page_text(h)
                h.capture_text("typed", json.dumps(
                    {"anchors": typed_anchors, "picks": typed_picks, "skipped": skipped}))
        return {"anchors": typed_anchors, "picks": typed_picks, "skipped": skipped}

    def submit(self) -> None:
        """Sends the page. **A blank story is nudged once before it is accepted** -- the product's
        own `BLANK_ANCHOR_NUDGE` ("Can you think of one specific time this happened?"), and a
        second press sends anyway (`ParticipantRoute.tsx`). Corpus people who left an anchor blank
        (`01-countly`'s Oliver, `05-paidly`'s Yara) meet it every run, so this presses twice when
        the first press produced a nudge rather than a thank-you, and never more than twice.
        """
        with self._scope():
            with self._bstep.step("participant submits their answers") as h:
                button = self.page.get_by_role("button", name=re.compile(r"^submit$", re.I))
                thanks = self.page.get_by_text(re.compile("thanks", re.I))
                button.click()
                for press in (1, 2):
                    try:
                        thanks.wait_for(state="visible", timeout=6_000)
                        break
                    except Exception:  # noqa: BLE001 - a nudge is not a failure, it is the design
                        if press == 2:
                            raise
                        notice = _safe_text(
                            lambda: self.page.locator(".stale").first.inner_text())
                        if notice:
                            h.capture_text("refusal", notice)
                            raise AssertionError(
                                f"the server refused this response rather than nudging: {notice!r}")
                        h.capture_text("nudge", _safe_text(
                            lambda: self.page.locator(".iv .hint").last.inner_text()))
                        button.click()
                h.add_screenshot(self._bstep.screenshot("participant-thank-you"))
                self._capture_page_text(h)

    def submit_expect_nudge(self) -> str:
        """A blank story is nudged once before it is accepted (`BLANK_ANCHOR_NUDGE`) -- the
        product's own "can you think of one specific time" line, not a refusal."""
        with self._scope():
            with self._bstep.step("the stranger submits with a blank story") as h:
                self.page.get_by_role("button", name=re.compile(r"^submit$", re.I)).click()
                self.page.wait_for_timeout(500)
                nudge = _safe_text(lambda: self.page.locator(".iv .hint").last.inner_text())
                h.add_screenshot(self._bstep.screenshot("participant-nudged"))
        return nudge

    def submit_expect_notice(self) -> None:
        with self._scope():
            with self._bstep.step("the stranger submits and the server refuses gently") as h:
                self.page.get_by_role("button", name=re.compile(r"^submit$", re.I)).click()
                self.page.locator(".stale").wait_for(state="visible", timeout=10_000)
                h.add_screenshot(self._bstep.screenshot("participant-notice"))
                self._capture_page_text(h)

    def open_expect_notice(self, url: str) -> None:
        """A link that will not render a fresh page -- gone stale (410), already answered, or
        never real (404) -- capturing whatever the page shows instead."""
        with self._scope():
            with self._bstep.step("the stranger opens a link that is no longer fresh") as h:
                self.page.goto(url, wait_until="load")
                self.page.wait_for_selector(".hello, .stale", timeout=15_000)
                h.add_screenshot(self._bstep.screenshot("participant-link-notice"))
                self._capture_page_text(h)


#: The old name, kept so a scenario this feature did not rewrite still imports. It is the same
#: class: there is only one participant page, and it is this one.
ParticipantBrowser = ParticipantPage
