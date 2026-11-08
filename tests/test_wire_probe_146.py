"""Spec 146 -- the Importance wire probe (keel-cloud 097 F9, `_importance_needs_three`) is the live journeys' alone, and
waits for the steps it opens.

Cycle 17 (2026-11-07): 17-expanse PROBLEM spent its three retries on RESULT_INVALID calibration drafts, `retries` reached
0, the probe ran on a back-test, its two wire saves queued reviews, and the lock page stayed greyed past the drift-95
guard. FR-1: the skip is `Journey.backtest`, never the retries left. FR-2: the probe waits for `Overview.openSteps` to
read 0 before the walk goes on.
"""
from __future__ import annotations

import inspect
from types import SimpleNamespace

import pytest

from evals import backtest as backtest_mod
from evals import corpus_scenario


def _journey(**over):
    base = {"patience": 1.0, "retries": 0, "backtest": False}
    base.update(over)
    return SimpleNamespace(**base)


# ---------------------------------------------------------------------------------------------------------- FR-1

def test_the_journey_carries_the_back_tests_own_flag():
    """`Journey.backtest` is a field, False by default (the live journeys), and the back-test's camera sets it beside
    the retries."""
    assert corpus_scenario.Journey.__dataclass_fields__["backtest"].default is False
    source = inspect.getsource(backtest_mod.Backtest.camera)
    assert "j.retries = RETRIES" in source and "j.backtest = True" in source


def test_the_probe_is_skipped_on_the_back_test_whatever_the_retries_left():
    """The gate reads the flag, not the retries: a back-test with its retries spent (cycle 17's 17-expanse) skips the
    probe; a live journey runs it even with retries set."""
    lines = inspect.getsource(corpus_scenario).splitlines()
    calls = [n for n, line in enumerate(lines) if line.strip() == "_importance_needs_three(j)"]
    assert len(calls) == 1, calls
    condition = lines[calls[0] - 1]
    assert 'vector == "PROBLEM"' in condition and 'getattr(j, "backtest", False)' in condition, condition
    assert "retries" not in condition


@pytest.mark.parametrize("retries,backtest,ran", [(0, True, False), (3, True, False), (3, False, True), (0, False, True)])
def test_the_gate_as_written(retries, backtest, ran, monkeypatch):
    """The gate's own expression, evaluated as the walk evaluates it."""
    j = _journey(retries=retries, backtest=backtest)
    answers = {"problem.importance": SimpleNamespace(unsure=False)}
    vector = "PROBLEM"
    assert (vector == "PROBLEM" and not answers["problem.importance"].unsure
            and not getattr(j, "backtest", False)) is ran


# ---------------------------------------------------------------------------------------------------------- FR-2

def test_the_probe_waits_for_the_steps_it_opened_before_the_reload():
    source = inspect.getsource(corpus_scenario._importance_needs_three)
    waits, reloads = source.index("_wait_steps_landed(j,"), source.index('j.page.reload(wait_until="load")')
    assert waits < reloads


def test_the_wait_returns_once_no_step_is_open(monkeypatch):
    reads = iter([{"openSteps": 2, "revision": 7}, {"openSteps": 1, "revision": 7}, {"openSteps": 0, "revision": 9}])
    j = _journey(get=lambda path: next(reads), project=lambda tail: f"/v2/projects/p{tail}")
    monkeypatch.setattr(corpus_scenario.time, "sleep", lambda s: None)
    assert corpus_scenario._wait_steps_landed(j, "probe") == {"openSteps": 0, "revision": 9}


def test_the_wait_names_the_overview_when_a_step_never_lands(monkeypatch):
    j = _journey(get=lambda path: {"openSteps": 1, "revision": 7}, project=lambda tail: f"/v2/projects/p{tail}")
    clock = iter([0.0, 0.0, 1.0, 91.0, 92.0])
    monkeypatch.setattr(corpus_scenario.time, "monotonic", lambda: next(clock))
    monkeypatch.setattr(corpus_scenario.time, "sleep", lambda s: None)
    with pytest.raises(AssertionError) as caught:
        corpus_scenario._wait_steps_landed(j, "probe")
    assert "Overview.openSteps" in str(caught.value) and "'openSteps': 1" in str(caught.value)


def test_a_missing_overview_counts_as_nothing_open():
    j = _journey(get=lambda path: None, project=lambda tail: f"/v2/projects/p{tail}")
    assert corpus_scenario._wait_steps_landed(j, "probe") == {}
