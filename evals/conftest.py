"""The stack fixture (attach if a stack is already up and answering, else boot one and own its
teardown -- design pass 5's fast-iteration path) and the per-scenario run_dir fixture
(contracts/evidence-contract.md).
"""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import sync_playwright

from harness.evidence import new_run_dir, write_versions
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

