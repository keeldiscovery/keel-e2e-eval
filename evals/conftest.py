"""The stack fixture (attach if a stack is already up and answering, else boot one and own its
teardown -- design pass 5's fast-iteration path) and the per-scenario run_dir fixture
(contracts/evidence-contract.md).
"""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import sync_playwright

from harness.evidence import new_run_dir, write_versions
from stack import auth as stack_auth
from stack.auth import FounderCredentials
from stack.config import StackConfig, load_config
from stack.lifecycle import boot, quick_gates_pass
from stack.lifecycle import teardown as stack_teardown


@pytest.fixture(scope="session")
def stack_config() -> StackConfig:
    return load_config()


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


def _capture_virgin_instance_routes_to_setup(stack: StackConfig, browser) -> None:
    """Task item 5's other auth moment (S-008's own "unauthenticated screen routes to login" is a
    per-scenario, always-reproducible check; this one is not -- `GET /v2/setup`'s `accountExists`
    is only ever `false` once in a stack's whole lifetime, the instant before this same fixture's
    `ensure_founder_account` call provisions it). **Judgement call**: captured here, once, rather
    than inside a scenario -- a scenario can't safely observe a virgin instance without either
    running first by accident of collection order or tearing down the shared account every other
    scenario in the same `pytest evals` session depends on. Evidence (a screenshot) goes to
    `runs/.stack/`, alongside this harness's other stack-lifecycle artifacts, not a scored run
    bundle's own directory -- this is a one-time stack-boot observation, not a scenario.
    """
    from pathlib import Path

    from stack.config import REPO_ROOT

    if stack_auth.account_exists(stack):
        return  # not virgin -- either a prior session already set it up, or the file was reused
    context = browser.new_context()
    try:
        page = context.new_page()
        page.goto(f"http://localhost:{stack.web_port}/", wait_until="load")
        page.wait_for_url("**/setup", timeout=10_000)
        heading = page.locator("h1.auth-title").inner_text()
        shot_dir = REPO_ROOT / "runs" / ".stack"
        shot_dir.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(shot_dir / "virgin-instance-routes-to-setup.png"), full_page=True)
        assert "set up" in heading.lower(), (
            f"expected a virgin instance's landing visit to route to the setup screen, got heading "
            f"{heading!r} at {page.url}")
    finally:
        context.close()


@pytest.fixture(scope="session")
def founder_credentials(stack: StackConfig, browser) -> FounderCredentials:
    """Founder-experience round 2: the "recipes/conftest step" that checks `GET /v2/setup` and
    performs setup once, idempotent (`stack.auth.ensure_founder_account`'s own docstring has the
    full derivation). Session-scoped, same lifetime as `stack`: every scenario in one `pytest
    evals` invocation shares the one founder account this establishes, exactly as a real founder's
    single account would persist across every discovery they start.

    Depends on `browser` (not just `stack`) so the virgin-instance-routes-to-setup observation
    (task item 5) can run *before* `ensure_founder_account` provisions the account -- the one and
    only moment in a stack's lifetime that instance is genuinely virgin.
    """
    _capture_virgin_instance_routes_to_setup(stack, browser)
    return stack_auth.ensure_founder_account(stack)


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

