"""`instructions/runner.py`: what a case's envelope is allowed to say about it (spec 009 FR-007).

Both tests here come from the baseline run of 2026-09-06, which found both faults with real money
on the line. They are stackless and modelless: a fake executor stands in for
`ClaudeCodeExecutor`, because what is being guarded is how this module *reads* an executor, not
what the CLI does.
"""

from __future__ import annotations

import types

from instructions import runner as runner_mod
from instructions.prompts import Case


class _FakeExecutorModule:
    """Just enough of `keel_runtime.executor` for `ask` to work against."""

    class ExecutorUnavailable(Exception):
        pass

    class ExecutorTimeout(Exception):
        pass

    class ExecutorAuthFailure(Exception):
        pass

    class InvalidResponse(Exception):
        pass

    @staticmethod
    def InferenceRequest(**kw):                       # noqa: N802 - mirrors the real dataclass
        return types.SimpleNamespace(**kw)


class _FakeValidatorModule:
    class InvalidResponse(Exception):
        pass

    @staticmethod
    def validate_response(response, contract):
        return None


def _case(case_id="e/PROBLEM/run1"):
    return Case(case_id=case_id, kind="ASSUMPTIONS", entry_id="e", screen="PROBLEM_ASSUMPTIONS",
                subject="PROBLEM", run_index=1,
                payload={"response_contract": {"allowed_outcomes": ["COMPLETED"]}})


class _Executor:
    """Raises on demand, and keeps `last_envelope` the way the real one does -- only writing it
    when a call got far enough to have one."""

    def __init__(self, *, raises=None, envelope=None, response=None):
        self.raises = raises
        self.envelope = envelope
        self.response = response
        self.last_envelope = None

    def execute(self, request):
        if self.raises is not None:
            raise self.raises
        self.last_envelope = self.envelope
        return self.response


def test_a_timed_out_case_carries_no_envelope_rather_than_the_previous_cases():
    """Found by the baseline run: `ClaudeCodeExecutor` writes `last_envelope` only after a call
    that got that far, so a timeout left the *previous* case's envelope standing and the bundle
    filed it under the wrong case id -- a `total_cost_usd` and a `num_turns` belonging to somebody
    else. Every number in a report must trace to an envelope that belongs to it."""
    executor = _Executor(response={"outcome": "COMPLETED", "result": {}},
                         envelope={"num_turns": 3, "total_cost_usd": 0.41})

    first = runner_mod.ask(_FakeExecutorModule, _FakeValidatorModule, executor, _case("e/A/run1"))
    assert first.total_cost_usd == 0.41

    executor.raises = _FakeExecutorModule.ExecutorTimeout("'claude' did not respond within 120.0s")
    second = runner_mod.ask(_FakeExecutorModule, _FakeValidatorModule, executor, _case("e/B/run1"))

    assert second.envelope == {}, "a timed-out case must not inherit the last case's envelope"
    assert second.total_cost_usd is None
    assert second.num_turns is None
    assert second.errored is True


def test_the_answer_never_fitting_its_shape_is_a_measurement_not_an_executor_failure():
    """`ClaudeCodeExecutor` raises `ExecutorUnavailable` for two very different things, and a
    baseline against instructions that predate the contract turns on telling them apart: a missing
    binary measures nothing, while "the answer never fit its shape" is the model being reached,
    told the contract, and failing it in six turns -- which is the finding."""
    never_fit = _FakeExecutorModule.ExecutorUnavailable(
        "the answer never fit its shape -- result: 'question' is not a permitted property")

    answer = runner_mod.ask(_FakeExecutorModule, _FakeValidatorModule,
                            _Executor(raises=never_fit), _case())

    assert answer.never_fit is True
    assert answer.errored is False, "the model was reached; this is a score, not a harness failure"
    assert "never fit its shape" in answer.schema_error


def test_a_missing_binary_is_an_executor_failure_and_scores_nothing():
    gone = _FakeExecutorModule.ExecutorUnavailable("'claude' executable not found on PATH")

    answer = runner_mod.ask(_FakeExecutorModule, _FakeValidatorModule,
                            _Executor(raises=gone), _case())

    assert answer.never_fit is False
    assert answer.errored is True
    assert answer.schema_error is None
