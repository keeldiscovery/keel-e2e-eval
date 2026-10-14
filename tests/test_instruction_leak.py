"""`no_leak` at `MARKS_VERSION` 18 (spec 029 FR-015, marks-v9 §2.3, judgement calls 32, 45, 83, 85; spec 040).

The list is the corpus's own -- `09-fixture.yaml`'s golden mechanism, stemmed, less every word of the problem's own
world -- never the live `SOLUTION_MECHANISM` answer. Since keel-cloud 087 / 088 the model writes no question, so what
is swept is what it does write a reader is shown: on the PROBLEM founder-lists job, Prevalence's clause and fifths,
Importance's five and Current solution's phrase and outcomes (sweep A, the product words and the mechanism terms
only, call 45 -- nothing goes to the judge); on the respondent job, the gate's clause on Part 1 of the primary link
(sweep A with the full vocabulary and the judge for an inflection tie, and sweep B, the founder's own values).
"""

from __future__ import annotations

import pytest

from instructions import score as score_mod
from tests import v9_fixtures as fx

IMPORTANCE = "problem.importance"
CURRENT = "problem.current_solution_satisfaction"


@pytest.fixture()
def entry():
    return fx.entry()


@pytest.fixture()
def registry():
    return fx.registry()


def _score(entry, registry, result, judge=None, vector="PROBLEM"):
    return score_mod.score_calibration(fx.calibration_case(entry, vector), entry, registry,
                                       result, judge=judge)


def _with_label(registry, key, label, *, index=1, vector="PROBLEM"):
    result = fx.calibration_result(registry, vector)
    question = next(q for q in result["questions"] if q["key"] == key)
    question["list"]["items"][index]["label"] = label
    return result


def test_the_problem_job_sweeps_prevalence_and_the_two_lists_and_nothing_else(entry, registry):
    """Calls 83, 85: Frequency writes nothing a reader is shown, so three of the four are swept."""
    score = _score(entry, registry, fx.calibration_result(registry, "PROBLEM"))
    assert (score.leak_clean, score.leak_of) == (3, 3)
    assert [d.key for d in registry.answered_slice("PROBLEM", False) if score_mod.is_swept(d)] == [
        "problem.prevalence", IMPORTANCE, CURRENT]


def test_a_mechanism_term_in_an_importance_rival_is_a_fault_naming_it(entry, registry):
    judge = fx.FakeJudge()
    score = _score(entry, registry, _with_label(registry, IMPORTANCE, "Waiting for the beep to start"), judge)
    leak = [f for f in score.faults if f["check"] == "no_leak"]
    assert len(leak) == 1 and leak[0]["key"] == IMPORTANCE and "beep" in leak[0]["evidence"]
    assert (score.leak_clean, score.leak_of) == (2, 3)
    assert judge.calls == [], "a PROBLEM calibration hit is code's to decide, never the judge's"


def test_a_multi_word_term_in_the_current_solution_phrase_is_a_fault(entry, registry):
    result = fx.calibration_result(registry, "PROBLEM")
    next(q for q in result["questions"] if q["key"] == CURRENT)["list"]["phrase"] = "your key ring routine"
    score = _score(entry, registry, result)
    assert any("key ring" in f["evidence"] for f in score.faults if f["check"] == "no_leak")


def test_a_product_word_in_the_prevalence_clause_is_a_fault(entry, registry):
    result = fx.calibration_result(registry, "PROBLEM")
    next(q for q in result["questions"] if q["key"] == "problem.prevalence")["event"] = "opened an app to find keys"
    score = _score(entry, registry, result)
    assert any("app" in f["evidence"] for f in score.faults if f["check"] == "no_leak")


@pytest.mark.parametrize("label, hit", [
    ("Checking an app for the keys", "app"), ("Looking up a website about it", "website"),
    ("Listening for the keys", None), ("Hearing the tag go off", "tag")])
def test_calibration_sweeps_the_product_words_and_the_terms_and_nothing_derived(entry, registry, label, hit):
    """Call 45: *listening* is in the derived vocabulary's ledger, not a term -- the runtime cannot refuse it at the
    PROBLEM calibration step, so neither does the mark."""
    judge = fx.FakeJudge(answer=True)
    score = _score(entry, registry, _with_label(registry, IMPORTANCE, label), judge)
    leak = [f for f in score.faults if f["check"] == "no_leak"]
    assert judge.calls == [] and score.leak_judged == 0
    assert bool(leak) is bool(hit)
    if hit:
        assert hit in leak[0]["evidence"]


def test_a_problem_word_is_no_hit_at_all(entry, registry):
    score = _score(entry, registry, _with_label(registry, IMPORTANCE, "Finding the keys in the morning"))
    assert score.leak_hits == 0 and score.leak_clean == 3


def test_a_solution_list_is_not_swept(entry, registry):
    result = _with_label(registry, "solution.compatibility", "The tag could beep", index=0, vector="SOLUTION")
    score = _score(entry, registry, result, vector="SOLUTION")
    assert score.leak_of == 0 and not [f for f in score.faults if f["check"] == "no_leak"]


# ------------------------------------------------- the gate's clause: the full vocabulary and the judge

def _gate(entry, registry, event, judge, *, part=1, link="PRIMARY"):
    result = fx.respondent_result(entry, part, link=link)
    for item in result["items"]:
        if item["key"] == "problem.prevalence":
            item["event"] = event
    return score_mod.score_respondent(fx.respondent_case(entry, part, link=link), entry, registry,
                                      entry.plan(), result, judge=judge)


def test_the_gate_clause_is_swept_twice_and_nothing_else_on_the_respondent_screen(entry, registry):
    """Call 83: sweeps A and B over the one model-written respondent word; parts 2 and 3 sweep nothing."""
    score = _gate(entry, registry, "lose your keys on the way out", fx.FakeJudge())
    assert (score.leak_clean, score.leak_of) == (2, 2)
    for part in (2, 3):
        later = score_mod.score_respondent(fx.respondent_case(entry, part), entry, registry, entry.plan(),
                                           fx.respondent_result(entry, part), judge=fx.FakeJudge())
        assert later.leak_of == 0


@pytest.mark.parametrize("answer, faulted", [(True, True), (False, False)])
def test_an_inflection_tie_goes_to_the_judge_once_and_its_answer_decides(entry, registry, answer, faulted):
    judge = fx.FakeJudge(answer=answer)
    score = _gate(entry, registry, "have to keep listening for your keys", judge)
    assert len(judge.calls) == 1
    assert "the commuter" in judge.calls[0]["mechanism"], "the golden one-liner, not a live one"
    assert score.leak_judged == 1
    assert any(f.get("sweep") == "A" for f in score.faults) is faulted


def test_the_judge_is_cached_so_a_repeated_clause_is_asked_once(entry, registry):
    judge = fx.FakeJudge(answer=False)
    _gate(entry, registry, "keep listening for your keys", judge)
    _gate(entry, registry, "keep listening for your keys", judge)
    assert len(judge.calls) == 1


def test_a_mechanism_stem_in_the_clause_is_a_direct_fault(entry, registry):
    judge = fx.FakeJudge(answer=False)
    score = _gate(entry, registry, "wait for a beep to find your keys", judge)
    assert judge.calls == []
    assert any("beep" in f["evidence"] for f in score.faults if f.get("sweep") == "A")


def test_the_founders_own_phrase_in_the_clause_is_sweep_b(entry, registry):
    """Sweep B (call 32): the founder's Prevalence phrase (*Most*) told to the stranger is the answer hoped for."""
    score = _gate(entry, registry, "lose your keys most mornings like most people", fx.FakeJudge())
    assert any(f.get("sweep") == "B" and "most" in f["evidence"].lower() for f in score.faults)


def test_judged_fraction_is_items_judged_over_items_with_any_hit(entry, registry):
    judge = fx.FakeJudge(answer=False)
    plain = _gate(entry, registry, "wait for the beep and the whistle", judge)
    tie = _gate(entry, registry, "keep listening for your keys", judge)
    totals = score_mod.totals(respondent_scores=[plain, tie], judge_calls=judge.call_count)
    assert totals["leak_hit_items"] == 2 and totals["leak_judged"] == 1
    assert totals["judged_fraction"] == 0.5
