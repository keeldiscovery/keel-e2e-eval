"""The stack fixture (attach if a stack is already up and answering, else boot one and own its
teardown -- design pass 5's fast-iteration path) and the per-scenario run_dir fixture
(contracts/evidence-contract.md).
"""

from __future__ import annotations

import os
import re

import pytest
from playwright.sync_api import sync_playwright

from harness.evidence import new_run_dir, write_versions
from stack.auth import FOUNDER_ONE, FOUNDER_TWO, StubFounder
from stack.config import PROFILES, StackConfig, load_config
from stack.lifecycle import boot, quick_gates_pass
from stack.lifecycle import teardown as stack_teardown


@pytest.fixture(scope="session")
def stack_config() -> StackConfig:
    """Reads `KEEL_EVAL_PROFILE` (the Makefile's `eval`/`eval-all` targets set it from
    `PROFILE=`) so `make eval K=s001 PROFILE=playground` attaches this whole session to the
    split-stacks playground profile instead of the default eval one (relay-design.md §12.5) --
    two referee sessions sharing one checkout must never collide on ports, a database, or a
    runtime home; running one on each profile is how they don't."""
    profile = os.environ.get("KEEL_EVAL_PROFILE", "eval")
    if profile not in PROFILES:
        profile = "eval"
    return load_config(profile=profile)


@pytest.fixture(scope="session")
def stack(stack_config: StackConfig):
    """Attaches to an already-answering stack, or boots one and tears it down at session end.

    A stack this fixture did not boot is left running: `make eval` against an already-up stack
    (from a prior `make up`) is the fast-iteration path (spec edge case), and it would be
    surprising for running the evals to also tear down a stack the operator is still using.
    """
    owns_lifecycle = not quick_gates_pass(stack_config)
    if owns_lifecycle:
        boot(stack_config)
    yield stack_config
    if owns_lifecycle:
        stack_teardown(stack_config)


def _capture_the_login_screen(stack: StackConfig, browser) -> None:
    """**L1, the login screen, before anyone has signed in** (keel-cloud
    `canon/designs/google-sign-in-design.md` §10.4). This replaces the virgin-instance capture it
    stands in the place of, and the replacement is the point: the retired setup route's `accountExists`
    was true exactly once in a stack's whole lifetime, so the old observation could only ever be
    made here, once, before any scenario ran. There is no virgin instance any more -- **this is
    the same screen on a fresh instance and a busy one**, and that sameness is what is asserted.

    **`/` is no longer that screen, and that is the product's own doing** (keel-web spec
    `015-landing-page` FR-001, landed at keel-web `d5d8645`, after this repository's last run of
    record). A visitor keel-cloud does not know used to be bounced from `/` to `/login` -- *"a
    login screen as the first thing a product says about itself"* -- and now renders the landing
    page instead: same route, same one call, no redirect between the two. `LandingRoute` returns
    `<MarketingPage />` on the 401 and `AppRoutes`'s `AuthGate` leaves `/` alone for exactly that
    reason.

    So this waited fifteen seconds for a redirect the product deliberately removed, and took every
    scenario in this repository down with it. It is a **harness fault, not a finding**: a referee
    pinned to the past cannot call the present (AGENTS.md), and keel-web's own spec says `/login`
    is otherwise unchanged -- *"it stays the one-button Google page of spec 014"*. The screen is
    opened directly now, which is what `harness/browser.py::Auth._goto_login` has always done and
    is why sign-in itself never noticed.

    The stranger's door is captured beside it rather than dropped, because *what `/` shows somebody
    with no session* is a thing a run of record should be able to show a reader.

    Evidence goes to `runs/.stack/`, alongside this harness's other stack-lifecycle artifacts, not
    a scored run bundle: it is a one-time stack-boot observation, not a scenario.
    """
    from stack.config import REPO_ROOT

    web_base = f"http://localhost:{stack.web_port}"
    shot_dir = REPO_ROOT / "runs" / ".stack"
    shot_dir.mkdir(parents=True, exist_ok=True)
    context = browser.new_context()
    try:
        page = context.new_page()

        # The stranger's door: `/`, with no session at all.
        page.goto(f"{web_base}/", wait_until="load")
        page.get_by_role("link", name="Log in").first.wait_for(state="visible", timeout=20_000)
        page.screenshot(path=str(shot_dir / "landing-page-before-anyone-signed-in.png"),
                        full_page=True)
        assert "/login" not in page.url, (
            f"a visitor with no session was redirected to {page.url} -- keel-web spec 015 FR-001 "
            f"says `/` splits by session, not by redirect")
        assert page.get_by_label("Password").count() == 0, (
            "a password field anywhere on the stranger's landing page would mean keel-cloud kept "
            "one (google-sign-in-design.md §10.8)")

        # The login screen itself, opened the way `Auth._goto_login` opens it.
        page.goto(f"{web_base}/login", wait_until="load")
        page.locator("h1.auth-title").wait_for(state="visible", timeout=15_000)
        heading = page.locator("h1.auth-title").inner_text()
        page.screenshot(path=str(shot_dir / "login-screen-before-anyone-signed-in.png"),
                        full_page=True)
        assert heading.strip().lower() == "log in", (
            f"expected the login screen, got heading {heading!r} at {page.url}")
        assert page.get_by_role("link", name="Continue with Google").count() == 1, (
            "the login screen must carry exactly one way in (design §6) -- and it is a link, "
            "because signing in is a navigation and not a fetch")
        assert page.get_by_label("Password").count() == 0, (
            "a password field on the login screen would mean keel-cloud kept one (§10.8)")
    finally:
        context.close()


@pytest.fixture(scope="session")
def founder_one(stack: StackConfig, browser) -> StubFounder:
    """Founder A -- *Eval Founder*, the identity every scenario but S-010 signs in as.

    **No I/O and no provisioning.** The password era's `ensure_founder_account` called
    the retired setup route once and stored credentials; there is nothing to provision now, because an
    account exists the moment somebody signs in and the first founder is not special (decision 3).
    What is left is a record naming who to click on the stub's picker.

    It still depends on `browser`, for one reason: the L1 capture above wants to happen once per
    stack session, before any scenario has signed in.
    """
    _capture_the_login_screen(stack, browser)
    return FOUNDER_ONE


@pytest.fixture(scope="session")
def founder_two(stack: StackConfig) -> StubFounder:
    """Founder B -- *Nour Haddad*, the second person on the instance (S-010). No `browser`
    dependency: nothing about B is observed before the scenarios run."""
    return FOUNDER_TWO


def _slug_from_test_name(name: str) -> str:
    slug = re.sub(r"^test_", "", name)
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", slug).strip("-").lower()
    return slug or "run"


@pytest.fixture
def run_dir(request: pytest.FixtureRequest, stack: StackConfig):
    """One evidence-bundle directory per test, with versions.json already written -- a scenario
    that never gets further than the stack fixture still leaves a bundle naming what it ran
    against.
    """
    slug = _slug_from_test_name(request.node.name)
    path = new_run_dir(slug)
    write_versions(path, stack)
    return path


# ------------------------------------------------------------------------------------- browser

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance):
    b = playwright_instance.chromium.launch()
    yield b
    b.close()

