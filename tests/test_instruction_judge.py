"""`instructions/judge.py` at `MARKS_VERSION` 9: one question, `reveals_solution` (spec 029 FR-005,
research R8; T031).

The judge's plumbing -- `_ask`, the cache, the call record, `judge_env` and `JUDGE_UNSET_ENV` -- is
unchanged and held by `tests/test_instruction_judge_isolation.py`. What is held here is the one
question: its words, which answer is the fault, and that the three v8 questions are gone with
`align.py` (call 29).
"""

from __future__ import annotations

import json

import pytest

from instructions import judge as judge_mod


@pytest.fixture()
def asked(monkeypatch):
    seen = []

    def _fake_run(argv, *, input, **kwargs):
        seen.append(input)
        word = "SAME" if "card" in input.split("The question:")[-1] else "DIFFERENT"

        class _Done:
            stdout = json.dumps({"is_error": False, "result": word})
        return _Done()

    monkeypatch.setattr(judge_mod.subprocess, "run", _fake_run)
    monkeypatch.setattr(judge_mod.shutil, "which", lambda _name: "/usr/local/bin/claude")
    return seen


def test_the_question_is_marks_v9s_closed_question_with_the_golden_one_liner(asked):
    judge = judge_mod.Judge()
    judge.reveals_solution("What did you try first?", "the parent holds the phone near the cot")
    prompt = asked[0]
    assert "Does this question tell a stranger what the proposed solution is: " \
           "the parent holds the phone near the cot?" in prompt
    assert "SAME or DIFFERENT" in prompt
    assert "The question: What did you try first?" in prompt


def test_same_is_the_fault_and_different_is_not(asked):
    judge = judge_mod.Judge()
    assert judge.reveals_solution("Would a card naming the need have helped?", "x") is True
    assert judge.reveals_solution("What did you try first?", "x") is False


def test_no_answer_is_not_a_fault(monkeypatch):
    monkeypatch.setattr(judge_mod.shutil, "which", lambda _name: None)
    assert judge_mod.Judge().reveals_solution("anything", "x") is False
    assert judge_mod.NoJudge().reveals_solution("anything", "x") is False


def test_the_answer_is_cached_by_question_and_every_call_recorded(asked):
    judge = judge_mod.Judge()
    judge.reveals_solution("What did you try first?", "x", context="listen")
    judge.reveals_solution("What did you try first?", "x", context="listen")
    assert len(asked) == 1 and judge.call_count == 1
    assert judge.calls[0]["kind"] == "reveals_solution"
    assert judge.calls[0]["answer"] == "DIFFERENT"


def test_the_three_v8_questions_are_gone():
    for name in ("same_answer_space", "same_expected_option", "pick"):
        assert not hasattr(judge_mod.Judge, name), name
