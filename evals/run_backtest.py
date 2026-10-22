"""Spec 062: `make backtest ENTRY=<id>` -- one back-test entry walked by `corpus_scenario.run` on Keel's AI, locally.

**Not a scenario, and never collected by a directory run.** The file is not `test_*.py`, so `make eval`, `make
eval-all`, `make eval-live` and `make unit` never collect it, and `matrix/cells.py` never names it (it spends the
founder's money -- Keel's own Anthropic key, read into the one command's environment). The Makefile names this file
on pytest's command line, which is the only way it runs.

**It brings its own stack up and down** (judgement call 1 in `specs/062-backtest-runner/tasks.md`): the `stack`
fixture here overrides `evals/conftest.py`'s, refusing a stack that already answers (its keel-cloud was booted without
this shell's key) and otherwise booting one whose keel-cloud inherits this shell's environment (`stack/cloud.py`), key
and all, and tearing it down after.
"""

from __future__ import annotations

import os

import pytest

from evals import backtest, corpus_scenario
from stack.lifecycle import boot, quick_gates_pass
from stack.lifecycle import teardown as stack_teardown

ENTRY_ID = (os.environ.get(backtest.ENTRY_VAR) or "").strip()

pytestmark = pytest.mark.live


@pytest.fixture(scope="session")
def stack(stack_config):
    """The back-test's own stack: refused when one already answers, else booted from this shell and torn down."""
    said = backtest.refusal() or backtest.entry_refusal()
    if said:
        pytest.exit(said, returncode=2)
    if stack_config.is_remote:
        pytest.exit("make backtest refuses: it runs on the local eval profile only (spec 062 FR-2)", returncode=2)
    if quick_gates_pass(stack_config):
        pytest.exit(backtest.stack_up_refusal(), returncode=2)
    boot(stack_config)
    try:
        yield stack_config
    finally:
        stack_teardown(stack_config)


@pytest.mark.bundle(f"backtest-{ENTRY_ID or 'none'}")
def test_backtest(stack, browser, run_dir):
    corpus_scenario.run(stack, None, browser, run_dir, entry_id=ENTRY_ID, slug=f"backtest-{ENTRY_ID}",
                        backtest=backtest.Backtest(run_dir=run_dir, stack=stack))
