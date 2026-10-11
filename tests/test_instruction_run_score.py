"""`run._score`: every answered case lands with its own scorer, and nowhere else (spec 029 T037,
T043, T049).

One answer a kind, on the hand-sized entry, through the function a real run and a rescore both
call: the calibration and respondent cases reach the question scorers, a read reaches
`score_interpret` keyed on the person, a brief reaches the five marks, and the three
interpretations are kept for the aggregate and the register and scored by nothing (call 28).
"""

from __future__ import annotations

import types

import pytest

from instructions import prompts as prompts_mod
from instructions import run as run_mod
from tests import v9_fixtures as fx


@pytest.fixture()
def cases(tmp_path):
    return {c.case_id: c for c in prompts_mod.build_cases(
        fx.entry(), fx.exported(tmp_path), fx.instructions(), fx.FakeRuntime, n_runs=1)}


def _answer(result, outcome="COMPLETED"):
    return types.SimpleNamespace(outcome=outcome, schema_valid=True, schema_error=None,
                                 error=None, result=result, questions=None, errored=False)


def test_each_kind_reaches_its_own_scorer(cases):
    entry = fx.entry()
    registry = fx.registry()
    state = run_mod._RunState()
    answers = {
        "09-fixture/CONTEXT_INTERPRET/run1": {"understands": "commuters", "actor": "commuter"},
        "09-fixture/CALIBRATION_PROBLEM/run1": fx.calibration_result(registry, "PROBLEM"),
        "09-fixture/RESPONDENT_PART1/run1": fx.respondent_result(entry, 1),
        "09-fixture/INTERPRET/Ann Abbott/run1": {"invitationId": "09-fixture/Ann Abbott",
                                                  "anchoring": "ANCHORED"},
        "09-fixture/BRIEF/run1": {"headline": {"text": "Not yet.", "cites": []}},
    }
    for case_id, result in answers.items():
        diff = run_mod._score(cases[case_id], entry, _answer(result), None, state, fx.FakeJudge())
        assert diff["case_id"] == case_id
    assert len(state.calibration) == 1 and state.calibration[0].coverage_passed
    assert len(state.respondent) == 1 and state.respondent[0].validity_hit == len(entry.plan()[1])
    assert len(state.interpret) == 1 and state.interpret[0].agreed == 1
    assert len(state.brief) == 1 and set(state.brief[0].marks) == {"shape", "cites", "numbers",
                                                                    "quotes", "bans"}
    assert len(state.shown_to_aggregate) == 5, "every answer goes to the aggregate"
    assert "CONTEXT_INTERPRET" in state.produced["09-fixture"], \
        "the interpretation is kept for the register and scored by nothing"


def test_a_needs_input_is_a_failed_case_on_every_screen(cases):
    entry = fx.entry()
    state = run_mod._RunState()
    run_mod._score(cases["09-fixture/CALIBRATION_PROBLEM/run1"], entry,
                   _answer(None, outcome="NEEDS_INPUT"), None, state, fx.FakeJudge())
    assert state.calibration[0].failed.startswith("NEEDS_INPUT")
    assert state.calibration[0].coverage_hit == 0
