"""Spec 062: `make backtest ENTRY=<id>` -- one back-test entry walked by `corpus_scenario.run` on Keel's AI, locally.

**Not a scenario, and never collected by a directory run.** The file is not `test_*.py`, so `make eval`, `make
eval-all`, `make eval-live` and `make unit` never collect it, and `matrix/cells.py` never names it (it spends the
founder's money -- Keel's own Anthropic key, read into the one command's environment). The Makefile names this file
on pytest's command line, which is the only way it runs.

**It brings its own stack up and down** (judgement call 1 in `specs/062-backtest-runner/tasks.md`): the `stack`
fixture here overrides `evals/conftest.py`'s, refusing a stack that already answers (its keel-cloud was booted without
this shell's key) and otherwise booting one whose keel-cloud inherits this shell's environment (`stack/cloud.py`), key
and all, and tearing it down after.

**Spec 066: `DOOR=host`** (`KEEL_BACKTEST_DOOR=host`): no key is asked for -- the founder comes in through the device code
of a runtime the back-test starts from keel-connect-skill's checkout, and every job is answered by the founder's own
Claude Code (`HOST=claude`, the one host built). The door, host and model refusals are `backtest.door_refusal`'s, the
CLI's login `backtest.host_readiness`'s; the runtime is stopped however the journey ends (`Backtest.stop_runtime`).

**Spec 071 FR-4: `SCOPE=`** (`KEEL_BACKTEST_SCOPE`, `scripts/backtest-host.sh --scope`): the study's scope the project is
created with on the choose screen (keel-cloud 133), ALL when unsaid; any other is walked by `evals/scope_journey.walk`
with `strict=False` and recorded in `backtest.json` (`scope`) and the register row's Door cell.
"""

from __future__ import annotations

import os

import pytest

from evals import backtest, corpus_scenario
from stack.lifecycle import boot, quick_gates_pass
from stack.lifecycle import teardown as stack_teardown

ENTRY_ID = (os.environ.get(backtest.ENTRY_VAR) or "").strip()
#: Spec 066 FR-1: read once, refused in the fixture when it names no door.
DOOR = (os.environ.get(backtest.DOOR_VAR) or "").strip().lower() or backtest.DEFAULT_DOOR

pytestmark = pytest.mark.live


@pytest.fixture(scope="session")
def stack(stack_config):
    """The back-test's own stack: refused when one already answers, else booted from this shell and torn down."""
    said = backtest.door_refusal()
    if not said and DOOR == "host":
        said = backtest.entry_refusal() or backtest.host_readiness(backtest.host()).get("refusal")
    elif not said:
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
    if DOOR != "host":
        corpus_scenario.run(stack, None, browser, run_dir, entry_id=ENTRY_ID, slug=f"backtest-{ENTRY_ID}",
                            backtest=backtest.Backtest(run_dir=run_dir, stack=stack, scope=backtest.scope()))
        return
    # spec 066: the host door -- and the runtime stopped whatever happens (FR-5; `finish` stops it first)
    bt = backtest.Backtest(run_dir=run_dir, stack=stack, door="host", host=backtest.host(), scope=backtest.scope())
    try:
        corpus_scenario.run(stack, None, browser, run_dir, entry_id=ENTRY_ID, slug=f"backtest-{ENTRY_ID}",
                            backtest=bt)
    finally:
        bt.stop_runtime()
