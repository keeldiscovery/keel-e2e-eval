"""`instructions/compare.py`: keel-cloud's engine, shelled at zero spend (spec 029 FR-018,
contracts/screen-shapes.md §5, judgement call 34; T020; spec 030 T010, call 47).

The engine is never imitated here. What is tested is the shim around it: the input is built from
the corpus entry and nothing in `expected`; the command is the exporter's sibling, run in the
keel-cloud checkout; the output is diffed -- one marked check a calibrated standing (10 on a B2C
entry, 12 on a B2B one) and one a vector, everything else reported, the count read off the entry
and never typed; and an
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


def test_the_input_is_built_from_the_corpus_only(entry):
    built = compare_mod.build_input(entry, entry.registry)
    assert built["entry"] == "09-fixture" and built["registry_version"] == 3
    assert list(built["founder_calibration"]) == entry.calibrated_keys()
    assert len(built["founder_calibration"]) == len(entry.registry.calibrated_keys(False)) == 12
    assert built["founder_calibration"]["commercial.buyer_payer_alignment"] == {"unsure": True}
    assert len(built["answers"]) == 12
    jo = next(a for a in built["answers"] if a["person"] == "Jo Judd")
    assert jo["chip"] == "cant_recall"
    assert jo["picks"] == {"problem.frequency": 3}


def test_a_b2b_entrys_input_carries_its_thirteen_and_the_hourly_rate(tmp_path):
    b2b = fx.entry(fx.ENTRY_B2B)
    built = compare_mod.build_input(b2b, b2b.registry)
    assert len(built["founder_calibration"]) == len(b2b.registry.calibrated_keys(True)) == 13
    assert built["founder_calibration"]["commercial.price"]["answer"] == {
        "low": 3, "high": 5, "period": "month", "currency": "GBP"}, "Price's answer, as the engine reads it"
    assert built["hourly_rate"] == {"value": 20, "currency": "GBP"}, "the engine prices B2B hours at it"
    assert built["founder_calibration"]["commercial.existing_sacrifice"]["answer"]["mode"] == "HOURS"
    assert "hourly_rate" not in compare_mod.build_input(fx.entry(), fx.registry()), "B2C records none"
    text = json.dumps(built)
    assert "standings" not in text and "vector_verdicts" not in text, \
        "nothing from expected: that is what the output is diffed against"


def _load(name):
    return json.loads((fx.COMPARE / f"09-fixture.{name}.out.json").read_text(encoding="utf-8"))


def _checks(entry) -> int:
    """The entry's own count -- its calibrated set plus three vectors -- never a literal."""
    return len(entry.calibrated_keys()) + len(entry.expected["vector_verdicts"])


def test_an_agreeing_engine_agrees_on_every_calibrated_standing_and_vector(entry):
    score = compare_mod.diff(entry.expected, _load("agree"), entry=entry)
    assert (score.agreed, score.checks) == (_checks(entry), _checks(entry)) == (15, 15)
    assert score.mismatches == [] and score.reported_diffs == []
    assert score.compare_correctness == 1.0 and score.measured


def test_a_disagreeing_engine_misses_two_naming_them(entry):
    score = compare_mod.diff(entry.expected, _load("disagree"), entry=entry)
    assert (score.agreed, score.checks) == (_checks(entry) - 2, _checks(entry))
    assert sorted(m["key"] for m in score.mismatches) == ["COMMERCIAL", "problem.importance"]
    assert score.reported_diffs == [{"key": "problem.frequency", "field": "median",
                                     "expected": 2.5, "produced": 3}], \
        "a count is reported, never marked (call 3)"


def test_a_dimension_the_engine_left_out_is_a_mismatch_not_a_skip(entry):
    produced = _load("agree")
    del produced["standings"]["problem.frequency"]
    score = compare_mod.diff(entry.expected, produced, entry=entry)
    assert (score.agreed, score.checks) == (_checks(entry) - 1, _checks(entry))


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
    assert (score.agreed, score.checks, score.measured) == (_checks(entry), _checks(entry), True)
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
    assert (score.agreed, score.checks) == (_checks(entry), _checks(entry))


def test_a_count_only_the_engine_states_is_not_a_disagreement(entry):
    produced = _load("agree")
    produced["standings"]["problem.current_solution_satisfaction"]["optionCounts"] = "works_well=1"
    produced["standings"]["commercial.buyer_payer_alignment"]["n"] = 0
    assert compare_mod.diff(entry.expected, produced, entry=entry).reported_diffs == []
