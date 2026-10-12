"""The six-scenario verdicts in `compare_correctness` (spec 035 US3, T003; `MARKS_VERSION` 17, call 80).

`screenContracts compare` takes revision 8's shapes only, so the seven scenarios of `verdicts/six-scenarios.yaml` are
measured by keel-cloud's own `SixScenarioVerdictsTest` at zero spend and its JUnit result read back. Here the gradle
wrapper is a script that writes that result; nothing in this file runs a JVM. One test, against keel-cloud's canon,
counts the real denominators (skipped by name below revision 9)."""

from __future__ import annotations

import stat
import types
from pathlib import Path

import pytest
import yaml

from instructions import compare as compare_mod
from instructions import corpus as corpus_mod
from instructions import prompts as prompts_mod
from instructions import score as score_mod
from stack.config import load_config
from tests import v9_fixtures as fx

SCENARIOS = [
    {"id": "payroll", "expect": {"a": {}, "b": {}, "c": {}}, "verdicts": {"PROBLEM": 1, "SOLUTION": 1, "COMMERCIAL": 1},
     "decision": "BUILD"},
    {"id": "free-app", "expect": {"a": {}}, "verdicts": {"PROBLEM": 1, "SOLUTION": 1, "COMMERCIAL": 1},
     "decision": "KEEP_INTERVIEWING"},
]


def junit(*results):
    cases = "".join(f'<testcase name="{name}" classname="X">'
                    + ("" if why is None else f'<failure message="{why}"/>') + "</testcase>"
                    for name, why in results)
    return f'<?xml version="1.0"?><testsuite name="X" tests="{len(results)}">{cases}</testsuite>'


def checkout(tmp_path, xml, *, exit_code=0):
    root = tmp_path / "keel-cloud"
    target = root / compare_mod.SIX_RESULT
    gradlew = root / "gradlew"
    root.mkdir()
    body = (f'mkdir -p "{target.parent}"\ncat > "{target}" <<\'XML\'\n{xml}\nXML\n' if xml is not None else "")
    gradlew.write_text(f"#!/bin/sh\necho \"$@\" > \"{root}/args.txt\"\n{body}exit {exit_code}\n")
    gradlew.chmod(gradlew.stat().st_mode | stat.S_IEXEC)
    return root


def test_the_checks_of_a_scenario_are_its_rows_its_three_verdicts_and_its_decision():
    assert [compare_mod.six_checks(s) for s in SCENARIOS] == [3 + 3 + 1, 1 + 3 + 1]


def test_every_passing_scenario_agrees_on_all_its_checks(tmp_path):
    root = checkout(tmp_path, junit(("payroll", None), ("free-app", None)))
    score = compare_mod.six_scenarios(root, SCENARIOS)
    assert score.measured and score.entry_id == "six-scenarios"
    assert (score.checks, score.agreed, score.mismatches) == (12, 12, [])
    assert "cleanTest test --tests *SixScenarioVerdictsTest" in (root / "args.txt").read_text()


def test_a_failing_scenario_agrees_on_none_and_keeps_the_tests_own_message(tmp_path):
    root = checkout(tmp_path, junit(("payroll", None), ("free-app", "decision expected KEEP_INTERVIEWING")),
                    exit_code=1)
    score = compare_mod.six_scenarios(root, SCENARIOS)
    assert score.measured and (score.checks, score.agreed) == (12, 7)
    assert score.mismatches[0]["key"] == "free-app"
    assert "KEEP_INTERVIEWING" in score.mismatches[0]["produced"]["why"]


def test_a_scenario_no_test_ran_for_is_a_mismatch_not_a_skip(tmp_path):
    score = compare_mod.six_scenarios(checkout(tmp_path, junit(("payroll", None))), SCENARIOS)
    assert (score.checks, score.agreed) == (12, 7)
    assert score.mismatches[0]["produced"]["why"] == "no test ran for this scenario"


def test_an_engine_that_left_no_result_is_unavailable_by_name(tmp_path):
    with pytest.raises(compare_mod.EngineUnavailable, match="left no result"):
        compare_mod.six_scenarios(checkout(tmp_path, None, exit_code=1), SCENARIOS)
    with pytest.raises(compare_mod.EngineUnavailable, match="no .*gradlew"):
        compare_mod.six_scenarios(tmp_path / "nowhere", SCENARIOS)
    with pytest.raises(compare_mod.EngineUnavailable, match="not readable JUnit"):
        (tmp_path / "x").mkdir()
        compare_mod.six_scenarios(checkout(tmp_path / "x", "<not-xml"), SCENARIOS)


def test_the_row_is_a_compare_row_that_counts_into_compare_correctness(tmp_path):
    case = prompts_mod.six_scenarios_case()
    assert case.kind == "COMPARE" and case.case_id == "six-scenarios/COMPARE" and case.payload == {}
    raw = compare_mod.six_scenarios(checkout(tmp_path, junit(("payroll", None), ("free-app", None))), SCENARIOS)
    entry = types.SimpleNamespace(id=compare_mod.SIX_ID)
    six = score_mod.score_compare(case, entry, raw)
    other = score_mod.CompareCaseScore(case_id="e/COMPARE", entry_id="e", checks=15, agreed=15, measured=True)
    totals = score_mod.totals(compare_scores=[other, six])
    assert (totals["compare_checks"], totals["compare_agreed"], totals["compare_correctness"]) == (27, 27, 1.0)
    unmeasured = score_mod.score_compare(case, entry, compare_mod.unmeasured("six-scenarios", "no gradle"))
    assert score_mod.totals(compare_scores=[other, unmeasured])["compare_correctness"] is None


def test_the_real_denominators_are_counted_off_the_file_and_the_real_engine_agrees():
    fx.canon_entry("03-lullaby.yaml")
    keel_cloud = load_config(validate=False).keel_cloud
    corpus = corpus_mod.load(keel_cloud)
    checks = sum(compare_mod.six_checks(s) for s in corpus.scenarios)
    assert len(corpus.scenarios) == 7 and checks == sum(
        len(s["expect"]) + 3 + 1 for s in yaml.safe_load(
            (Path(keel_cloud) / "canon/designs/measured-beliefs/corpus/verdicts/six-scenarios.yaml")
            .read_text())["scenarios"])
    # the engine itself is keel-cloud's `SixScenarioVerdictsTest`, run by `make instruction-eval DRY=1`
