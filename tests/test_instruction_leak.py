"""`no_leak`'s sweep A on calibration questions (spec 029 FR-015, marks-v9 §2.3, judgement call 32;
T030; at the twelve by spec 030).

The list is the corpus's own -- `09-fixture-r5.yaml`'s golden mechanism, stemmed, less every word of
the problem's own world -- never the live `SOLUTION_MECHANISM` answer. A hit on it is a fault, with
the word named. A hit on the one stem the fixture plants in the inflection ledger (*listens* in the
mechanism, *listened* in Bo's story) is a tie, and only a tie reaches the judge: once, cached, and
counted in `judged_fraction`.
"""

from __future__ import annotations

import pytest

from instructions import score as score_mod
from tests import v9_fixtures as fx

#: A PROBLEM dimension with a fixed five-point scale (Severity's place at v9).
SCALE = "problem.current_solution_satisfaction"


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
    result = _with_question(registry, SCALE, "How bad is it before the beep?")
    score = _score(entry, registry, result, judge)
    leak = [f for f in score.faults if f["check"] == "no_leak"]
    assert len(leak) == 1 and "beep" in leak[0]["evidence"]
    # Calls 52, 53: Frequency over the framed 7 nights has no model text, and is not swept.
    count = len(registry.calibrated_slice("PROBLEM", entry.b2b())) - 1
    assert (score.leak_clean, score.leak_of) == (count - 1, count)
    assert judge.calls == [], "a plain hit is code's to decide, never the judge's"


def test_a_mechanism_phrase_in_a_calibration_option_is_a_fault_outright(entry, registry):
    """Call 45: a PROBLEM calibration question is swept for the product words and the golden
    `mechanism_terms` only, stem, options and phrases alike, and nothing goes to the judge."""
    result = fx.calibration_result(registry, "PROBLEM")
    scale = next(q for q in result["questions"] if q["key"] == SCALE)
    scale["options"][0]["label"] = "Works well, the key ring helps"
    judge = fx.FakeJudge(answer=False)
    score = _score(entry, registry, result, judge)
    assert judge.calls == []
    assert any("key ring" in f["evidence"] for f in score.faults if f["check"] == "no_leak")


def test_a_mechanism_phrase_in_the_stem_is_a_fault_outright(entry, registry):
    judge = fx.FakeJudge(answer=False)
    result = _with_question(registry, SCALE, "Would a key ring have helped?")
    score = _score(entry, registry, result, judge)
    assert judge.calls == []
    assert any("key ring" in f["evidence"] for f in score.faults if f["check"] == "no_leak")


def test_a_problem_word_is_no_hit_at_all(entry, registry):
    result = _with_question(registry, SCALE,
                            "When you cannot find your keys in the morning, how bad is it?")
    score = _score(entry, registry, result, fx.FakeJudge())
    assert score.leak_hits == 0
    assert score.leak_clean == len(registry.calibrated_slice("PROBLEM", entry.b2b())) - 1


@pytest.mark.parametrize("text, hit", [
    ("Did you open an app to look?", "app"), ("Was there a website for it?", "website"),
    ("How long were you listening for them?", None), ("Did the tag go off?", "tag")])
def test_calibration_sweeps_the_product_words_and_the_terms_and_nothing_derived(entry, registry,
                                                                               text, hit):
    """Call 45: *listening* is in the derived vocabulary's ledger, not a term -- the runtime
    cannot refuse it at the PROBLEM calibration step, so neither does the mark."""
    judge = fx.FakeJudge(answer=True)
    score = _score(entry, registry, _with_question(registry, SCALE, text), judge)
    leak = [f for f in score.faults if f["check"] == "no_leak"]
    assert judge.calls == [] and score.leak_judged == 0
    assert bool(leak) is bool(hit)
    if hit:
        assert hit in leak[0]["evidence"]


def test_a_solution_calibration_question_is_not_swept(entry, registry):
    result = _with_question(registry, "solution.compatibility", "When would the tag beep?",
                            vector="SOLUTION")
    score = _score(entry, registry, result, fx.FakeJudge(), vector="SOLUTION")
    assert score.leak_of == 0 and not [f for f in score.faults if f["check"] == "no_leak"]


# ------------------------------- Part 1 respondent items keep the full vocabulary and the judge

def _part1(entry, registry, key, judge, *, question=None, option=None):
    result = fx.respondent_result(entry, 1)
    item = next(i for i in result["items"] if i["key"] == key)
    if question is not None:
        item["question"] = question
    if option is not None:
        first = item["options"][0]
        if isinstance(first, dict):
            first["label"] = option
        else:
            item["options"][0] = option
    return score_mod.score_respondent(fx.respondent_case(entry, 1), entry, registry,
                                      entry.plan(), result, judge=judge)


@pytest.mark.parametrize("answer, faulted", [(True, True), (False, False)])
def test_an_inflection_tie_goes_to_the_judge_once_and_its_answer_decides(entry, registry,
                                                                         answer, faulted):
    judge = fx.FakeJudge(answer=answer)
    score = _part1(entry, registry, SCALE, judge,
                   question="How long were you listening for them?")
    assert len(judge.calls) == 1
    assert "the commuter" in judge.calls[0]["mechanism"], "the golden one-liner, not a live one"
    assert score.leak_judged == 1
    assert any(f.get("sweep") == "A" for f in score.faults) is faulted


def test_the_judge_is_cached_so_a_repeated_question_is_asked_once(entry, registry):
    judge = fx.FakeJudge(answer=False)
    _part1(entry, registry, SCALE, judge, question="How long were you listening?")
    _part1(entry, registry, SCALE, judge, question="How long were you listening?")
    assert len(judge.calls) == 1


def test_judged_fraction_is_items_judged_over_items_with_any_hit(entry, registry):
    """Call 45 / decision 47's companion: one unit, items over items -- never items over words."""
    judge = fx.FakeJudge(answer=False)
    plain = _part1(entry, registry, SCALE, judge,
                   question="Before the beep, and the whistle, and the tag?")
    # Frequency over a framed window is code's sentence (call 52): the tie is on Importance.
    tie = _part1(entry, registry, "problem.importance", judge, question="Listening how often?")
    totals = score_mod.totals(respondent_scores=[plain, tie], judge_calls=judge.call_count)
    assert totals["leak_hits"] == 4, "three words on one item, one on the other"
    assert totals["leak_hit_items"] == 2 and totals["leak_judged"] == 1
    assert totals["judged_fraction"] == 0.5


@pytest.mark.parametrize("answer, faulted", [(True, True), (False, False)])
def test_a_mechanism_stem_only_in_a_part_one_option_label_goes_to_the_judge(entry, registry,
                                                                           answer, faulted):
    judge = fx.FakeJudge(answer=answer)
    key = next(i["key"] for i in fx.respondent_result(entry, 1)["items"] if i.get("options"))
    score = _part1(entry, registry, key, judge, option="Barely, a beep would do")
    assert len(judge.calls) == 1 and score.leak_judged == 1
    leak = [f for f in score.faults if f.get("sweep") == "A"]
    assert bool(leak) is faulted
    if leak:
        assert "option label" in leak[0]["evidence"] and "beep" in leak[0]["evidence"]


def test_a_part_one_stem_hit_stays_a_direct_fault(entry, registry):
    judge = fx.FakeJudge(answer=False)
    score = _part1(entry, registry, SCALE, judge,
                   question="How bad was it before the beep?")
    assert judge.calls == []
    assert any("beep" in f["evidence"] for f in score.faults if f.get("sweep") == "A")
