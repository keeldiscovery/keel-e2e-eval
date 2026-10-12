"""`BriefFacts.gaps` (keel-cloud 083, design §8.9 and §8.10; `MARKS_VERSION` 17, call 80), mirrored from keel-cloud's
`BriefGapsTest`: `problemSplit` is the decision's split flag; `strongerProblemWeakerFix` is Current solution holding
STRONGER while Relative advantage is not holding up -- and only then."""

from __future__ import annotations

from instructions import brief_facts

CURRENT = "problem.current_solution_satisfaction"
ADVANTAGE = "solution.relative_advantage"


def row(status, drift):
    return {"status": status, "drift": drift}


def test_a_problem_split_is_the_decisions_split():
    gaps = brief_facts.gaps({"problem.importance": row("PEOPLE_DISAGREE", "both")}, {"split": True})
    assert gaps == {"problemSplit": True, "strongerProblemWeakerFix": False}


def test_a_bigger_problem_and_a_smaller_fix_is_current_stronger_beside_advantage_not_holding():
    gaps = brief_facts.gaps({CURRENT: row("HOLDING_UP", "stronger"), ADVANTAGE: row("NOT_HOLDING_UP", "short")},
                            {"split": False})
    assert gaps == {"problemSplit": False, "strongerProblemWeakerFix": True}


def test_only_when_the_problem_reads_stronger_and_the_fix_does_not_hold():
    both = {CURRENT: row("HOLDING_UP", "none"), ADVANTAGE: row("NOT_HOLDING_UP", "short")}
    assert not brief_facts.gaps(both, {})["strongerProblemWeakerFix"], "only when the problem reads stronger"
    holding = {CURRENT: row("HOLDING_UP", "stronger"), ADVANTAGE: row("HOLDING_UP", "none")}
    assert not brief_facts.gaps(holding, {})["strongerProblemWeakerFix"]
    assert brief_facts.gaps({}, {}) == {"problemSplit": False, "strongerProblemWeakerFix": False}


def test_the_facts_carry_gaps_whatever_the_entry(tmp_path):
    from instructions import corpus as corpus_mod                    # noqa: PLC0415
    from tests import v9_fixtures as fx                              # noqa: PLC0415
    entry = corpus_mod.load_file(fx.ENTRY, registry=fx.registry())
    from instructions import context as context_mod                  # noqa: PLC0415
    facts = context_mod.build_brief(entry)["facts"]
    assert set(facts["gaps"]) == {"problemSplit", "strongerProblemWeakerFix"}
    assert facts["gaps"]["problemSplit"] == facts["decision"]["split"]
