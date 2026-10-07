"""`instructions/compare.py`: keel-cloud's engine, shelled at zero spend (spec 029 FR-018,
contracts/screen-shapes.md §5, judgement call 34; T020).

The engine is never imitated here. What is tested is the shim around it: the input is built from
corpus revision 3 and nothing in `expected`; the command is the exporter's sibling, run in the
keel-cloud checkout; the output is diffed 25 + 3 checks marked, everything else reported; and an
engine that cannot be asked leaves the mark **unmeasured, by name** -- with a fake `gradlew` that
fails the way a checkout without 058 would.
"""

from __future__ import annotations

import json
import stat
from pathlib import Path

import pytest

from instructions import compare as compare_mod
from tests import v9_fixtures as fx


@pytest.fixture()
def entry():
    return fx.entry()


def test_the_input_is_built_from_r3_only(entry):
    built = compare_mod.build_input(entry, entry.registry)
    assert built["entry"] == "09-fixture" and built["registry_version"] == 1
    assert len(built["founder_calibration"]) == 25
    assert built["founder_calibration"]["problem.urgency"] == {"unsure": True}
    assert len(built["answers"]) == 12
    ed = next(a for a in built["answers"] if a["person"] == "Ed Eze")
    assert ed["picks"]["problem.duration"]["rough"] is True, "rough is preserved"
    jo = next(a for a in built["answers"] if a["person"] == "Jo Judd")
    assert jo["chip"] == "cant_recall"
    assert jo["picks"]["problem.workaround_burden"] == {"chip": "cant_recall"}
    text = json.dumps(built)
    assert "standings" not in text and "vector_verdicts" not in text, \
        "nothing from expected: that is what the output is diffed against"


def _load(name):
    return json.loads((fx.COMPARE / f"09-fixture.{name}.out.json").read_text(encoding="utf-8"))


def test_an_agreeing_engine_scores_twenty_eight_of_twenty_eight(entry):
    score = compare_mod.diff(entry.expected, _load("agree"), entry=entry)
    assert (score.agreed, score.checks) == (28, 28)
    assert score.mismatches == [] and score.reported_diffs == []
    assert score.compare_correctness == 1.0 and score.measured


def test_a_disagreeing_engine_scores_twenty_six_naming_the_two(entry):
    score = compare_mod.diff(entry.expected, _load("disagree"), entry=entry)
    assert (score.agreed, score.checks) == (26, 28)
    assert sorted(m["key"] for m in score.mismatches) == ["COMMERCIAL", "problem.severity"]
    assert score.reported_diffs == [{"key": "problem.frequency", "field": "median",
                                     "expected": 2.5, "produced": 3}], \
        "a count is reported, never marked (call 3)"


def test_a_dimension_the_engine_left_out_is_a_mismatch_not_a_skip(entry):
    produced = _load("agree")
    del produced["standings"]["problem.duration"]
    score = compare_mod.diff(entry.expected, produced, entry=entry)
    assert (score.agreed, score.checks) == (27, 28)


def _fake_checkout(tmp_path, script: str) -> Path:
    checkout = tmp_path / "keel-cloud"
    checkout.mkdir()
    gradlew = checkout / "gradlew"
    gradlew.write_text("#!/bin/sh\n" + script)
    gradlew.chmod(gradlew.stat().st_mode | stat.S_IEXEC)
    return checkout


def test_the_engine_is_shelled_as_the_exporters_sibling_and_both_files_stay(tmp_path, entry):
    agree = fx.COMPARE / "09-fixture.agree.out.json"
    checkout = _fake_checkout(tmp_path, f"""
echo "$@" > "$PWD/argv.txt"
out=$(echo "$3" | sed 's/^.* //')
cp "{agree}" "$out"
""")
    bundle = tmp_path / "bundle" / "compare"
    score = compare_mod.compare_entry(checkout, entry, entry.registry, bundle)
    assert (score.agreed, score.checks, score.measured) == (28, 28, True)
    assert (bundle / "09-fixture.in.json").is_file() and (bundle / "09-fixture.out.json").is_file()
    argv = (checkout / "argv.txt").read_text()
    assert argv.startswith("-q screenContracts --args=compare ")


def test_an_engine_that_exits_non_zero_leaves_the_mark_unmeasured_naming_058(tmp_path, entry):
    checkout = _fake_checkout(tmp_path, "echo 'Unknown command: compare' >&2\nexit 1\n")
    score = compare_mod.compare_entry(checkout, entry, entry.registry, tmp_path / "compare")
    assert score.measured is False and score.compare_correctness is None
    assert "Unknown command: compare" in score.reason
    assert "keel-cloud 058" in score.reason
    assert (tmp_path / "compare" / "09-fixture.in.json").is_file(), \
        "the input is kept even when the engine could not be asked"


def test_a_checkout_without_gradlew_is_unmeasured_too(tmp_path, entry):
    score = compare_mod.compare_entry(tmp_path, entry, entry.registry, tmp_path / "compare")
    assert score.measured is False and "058" in score.reason


def test_an_engine_that_writes_nothing_readable_is_unmeasured(tmp_path, entry):
    checkout = _fake_checkout(tmp_path, "exit 0\n")
    score = compare_mod.compare_entry(checkout, entry, entry.registry, tmp_path / "compare")
    assert score.measured is False and "not readable JSON" in score.reason


def test_the_input_carries_the_plan_for_the_engines_own_item_rule(entry):
    """keel-cloud 058's compare-command.md: `problem.importance` needs `own_item` or the run exits 1."""
    built = compare_mod.build_input(entry, entry.registry)
    assert built["respondent_questions"]["problem.importance"]["own_item"] == "finding_keys"


def test_an_engine_none_drift_agrees_with_the_corpus_null_and_case_is_folded(entry):
    produced = _load("agree")
    for row in produced["standings"].values():
        row["drift"] = (row.get("drift") or "NONE").upper()
    score = compare_mod.diff(entry.expected, produced, entry=entry)
    assert (score.agreed, score.checks) == (28, 28)


def test_a_count_only_the_engine_states_is_not_a_disagreement(entry):
    produced = _load("agree")
    produced["standings"]["problem.severity"]["optionCounts"] = "barely=1"
    produced["standings"]["problem.urgency"]["n"] = 0
    assert compare_mod.diff(entry.expected, produced, entry=entry).reported_diffs == []
