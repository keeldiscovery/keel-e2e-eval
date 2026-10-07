"""`no_leak`'s sweep A on calibration questions (spec 029 FR-015, marks-v9 §2.3, judgement call 32;
T030).

The list is the corpus's own -- `09-fixture-r3.yaml`'s golden mechanism, stemmed, less every word of
the problem's own world -- never the live `SOLUTION_MECHANISM` answer. A hit on it is a fault, with
the word named. A hit on the one stem the fixture plants in the inflection ledger (*listens* in the
mechanism, *listened* in Bo's story) is a tie, and only a tie reaches the judge: once, cached, and
counted in `judged_fraction`.
"""

from __future__ import annotations

import pytest

from instructions import score as score_mod
from tests import v9_fixtures as fx


@pytest.fixture()
def entry():
    return fx.entry()


@pytest.fixture()
def registry():
    return fx.registry()


def _with_question(registry, key, text, vector="PROBLEM"):
    result = fx.calibration_result(registry, vector)
    next(q for q in result["questions"] if q["key"] == key)["question"] = text
    return result


def _score(entry, registry, result, judge, vector="PROBLEM"):
    return score_mod.score_calibration(fx.calibration_case(entry, vector), entry, registry,
                                       result, judge=judge)


def test_a_mechanism_stem_in_a_problem_question_is_a_fault_naming_the_word(entry, registry):
    judge = fx.FakeJudge()
    result = _with_question(registry, "problem.severity", "How bad is it before the beep?")
    score = _score(entry, registry, result, judge)
    leak = [f for f in score.faults if f["check"] == "no_leak"]
    assert len(leak) == 1 and "beep" in leak[0]["evidence"]
    assert (score.leak_clean, score.leak_of) == (8, 9)
    assert judge.calls == [], "a plain hit is code's to decide, never the judge's"


def test_a_mechanism_phrase_in_an_option_is_a_fault_too(entry, registry):
    result = fx.calibration_result(registry, "PROBLEM")
    severity = next(q for q in result["questions"] if q["key"] == "problem.severity")
    severity["options"][0]["label"] = "Barely, the key ring helps"
    score = _score(entry, registry, result, fx.FakeJudge())
    assert any("key ring" in f["evidence"] for f in score.faults if f["check"] == "no_leak")


def test_a_problem_word_is_no_hit_at_all(entry, registry):
    result = _with_question(registry, "problem.severity",
                            "When you cannot find your keys in the morning, how bad is it?")
    score = _score(entry, registry, result, fx.FakeJudge())
    assert score.leak_hits == 0 and score.leak_clean == 9


@pytest.mark.parametrize("answer, faulted", [(True, True), (False, False)])
def test_an_inflection_tie_goes_to_the_judge_once_and_its_answer_decides(entry, registry,
                                                                         answer, faulted):
    judge = fx.FakeJudge(answer=answer)
    result = _with_question(registry, "problem.severity", "How long were you listening for them?")
    score = _score(entry, registry, result, judge)
    assert len(judge.calls) == 1
    assert "the commuter" in judge.calls[0]["mechanism"], "the golden one-liner, not a live one"
    assert score.leak_judged == 1 and score.leak_hits == 1
    assert any(f["check"] == "no_leak" for f in score.faults) is faulted


def test_the_judge_is_cached_so_a_repeated_question_is_asked_once(entry, registry):
    judge = fx.FakeJudge(answer=False)
    result = _with_question(registry, "problem.severity", "How long were you listening for them?")
    _score(entry, registry, result, judge)
    _score(entry, registry, result, judge)
    assert len(judge.calls) == 1


def test_a_solution_calibration_question_is_not_swept(entry, registry):
    result = _with_question(registry, "solution.compatibility", "When would the tag beep?",
                            vector="SOLUTION")
    score = _score(entry, registry, result, fx.FakeJudge(), vector="SOLUTION")
    assert score.leak_of == 0 and not [f for f in score.faults if f["check"] == "no_leak"]


def test_judged_fraction_is_the_judged_hits_over_all_hits(entry, registry):
    judge = fx.FakeJudge(answer=False)
    plain = _score(entry, registry,
                   _with_question(registry, "problem.severity", "Before the beep?"), judge)
    tie = _score(entry, registry,
                 _with_question(registry, "problem.duration", "Listening how long?"), judge)
    totals = score_mod.totals([plain, tie], judge_calls=judge.call_count)
    assert totals["leak_hits"] == 2 and totals["leak_judged"] == 1
    assert totals["judged_fraction"] == 0.5
    assert totals["no_leak"] == 17 / 18
