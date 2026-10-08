"""`instructions/validate.py` at `MARKS_VERSION` 9: one batch kind per screen (spec 029 FR-024,
contracts/screen-shapes.md §6, research R10; T032).

The aggregate is asked, never restated. What is tested is what it is handed -- the state each
screen's applier reads, and never a founder value in front of the model -- and what happens when
keel-cloud's validator does not take a kind yet: that kind's two marks are **unmeasured, by name**,
with keel-cloud 058 named, and the other kinds are still asked.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from instructions import prompts as prompts_mod
from instructions import validate as validate_mod
from tests import v9_fixtures as fx


@pytest.fixture()
def cases(tmp_path):
    return prompts_mod.build_cases(fx.entry(), fx.exported(tmp_path), fx.instructions(),
                                   fx.FakeRuntime, n_runs=1)


def _batch(cases):
    return validate_mod.build_batch([(c, {"some": "result"}) for c in cases])


def _by_screen(batch, screen):
    return [c for c in batch["cases"] if c["screen"] == screen]


def test_a_calibration_case_carries_its_vector_and_the_slices_keys_and_no_founder_answer(cases):
    batch = _batch(cases)
    problem = next(c for c in _by_screen(batch, "CALIBRATION_QUESTIONS")
                   if c["vector"] == "PROBLEM")
    assert set(problem) >= {"case_id", "screen", "market", "vector", "context", "registry_slice",
                            "result"}
    assert problem["context"]["window"], "the job's own context, window and all (058 4ea3062)"
    assert problem["registry_slice"][0] == "problem.prevalence"
    assert len(problem["registry_slice"]) == 9
    assert "throws the morning off" not in repr(problem)


def test_a_respondent_case_carries_the_plan_the_option_sets_and_the_founders_values(cases):
    part1 = next(c for c in _by_screen(_batch(cases), "RESPONDENT_QUESTIONS") if c["part"] == 1)
    assert set(part1) >= {"case_id", "screen", "market", "part", "link", "plan",
                          "founder_options", "founder_values", "result", "context", "items"}
    assert part1["link"] == "PRIMARY" and len(part1["plan"]) == 8
    assert part1["founder_values"]["problem.severity"] == {
        "answer": "moderately", "belief_phrase": "throws the morning off"}, \
        "R3 is checked against values the model was never shown (025 D12/D18)"


def test_a_respondent_batch_entry_carries_the_jobs_context_window_and_mechanism(cases):
    """keel-cloud 058 (4ea3062) reads R8's window off the entry's own `context`: without it the
    validator fell back to Lullaby's 7 nights (18 R8 refusals in 20261008T115552Z, the eval's)."""
    respondent = [(c, e) for c in cases if c.kind == "RESPONDENT"
                  for e in _by_screen(_batch([c]), "RESPONDENT_QUESTIONS")]
    assert respondent
    for case, entry in respondent:
        sent = case.payload["context"]
        assert entry["context"] == sent["context"] and entry["context"]["window"]
        assert entry["items"] == sent["items"]
        assert entry.get("mechanism") == (sent.get("mechanism")
                                          or case.meta["validation_mechanism"])
        assert entry["case_id"] == case.case_id and entry["screen"] == "RESPONDENT_QUESTIONS"
    assert any(e.get("mechanism") for c, e in respondent if c.meta.get("part") in (2, 3)
               and c.meta.get("link") == "PRIMARY")


def test_a_part_one_batch_entry_carries_the_golden_mechanism_its_prompt_never_had(cases):
    """R4 at 058 bf5c75e reads the project's own vocabulary: the Part 1 entry carries the golden
    mechanism (terms and `not_assumed` too) as validation state, and the prompt still has none."""
    part1 = next(c for c in cases if c.kind == "RESPONDENT" and c.meta.get("part") == 1)
    assert "mechanism" not in part1.payload["context"], "the model is never told the idea on Part 1"
    assert "the commuter" not in json.dumps(part1.payload["context"])
    entry = _by_screen(_batch([part1]), "RESPONDENT_QUESTIONS")[0]
    golden = fx.entry().solution_mechanism
    assert entry["mechanism"]["mechanism"] == golden["mechanism"]
    assert entry["mechanism"]["mechanism_terms"] == golden["mechanism_terms"]
    assert entry["mechanism"]["not_assumed"] == golden["not_assumed"]
    assert entry["problem_statement"] == fx.entry().interpretations["problem"]
    assert "problem_statement" not in part1.payload["context"]
    part2 = next(c for c in cases if c.kind == "RESPONDENT" and c.meta.get("part") == 2)
    assert _by_screen(_batch([part2]), "RESPONDENT_QUESTIONS")[0]["mechanism"] \
        == part2.payload["context"]["mechanism"], "a part 2 entry keeps what its job was handed"


def test_every_other_kind_carries_what_its_applier_reads(cases):
    batch = _batch(cases)
    read = _by_screen(batch, "INTERPRET")[0]
    assert set(read) == {"case_id", "screen", "invitation_id", "story", "result"}
    assert set(_by_screen(batch, "CONTEXT_INTERPRET")[0]) == {
        "case_id", "screen", "market", "context_fields", "result"}
    assert _by_screen(batch, "PROBLEM_INTERPRET")[0]["seed"] == fx.entry().statements["problem"]
    mechanism = _by_screen(batch, "SOLUTION_MECHANISM")[0]
    assert mechanism["problem_statement"] == fx.entry().interpretations["problem"]
    brief = _by_screen(batch, "BRIEF")[0]
    assert [v["vector"] for v in brief["standings"]] == ["PROBLEM", "SOLUTION", "COMMERCIAL"]


def test_a_compare_row_is_never_batched(cases):
    assert not _by_screen(_batch(cases), "COMPARE")
    assert len(_batch(cases)["cases"]) == 19


def _tool(tmp_path, *screens) -> Path:
    tool = tmp_path / validate_mod._TOOL
    tool.parent.mkdir(parents=True)
    tool.write_text("class ScreenContractTool {\n" + "\n".join(
        f"  case {validate_mod._SHAPE_MARKERS[s]} -> apply();" for s in screens) + "\n}\n")
    return tmp_path


def test_shapes_taken_reads_one_marker_a_screen_off_the_validator(tmp_path):
    keel_cloud = _tool(tmp_path, "INTERPRET", "BRIEF")
    taken = validate_mod.shapes_taken(keel_cloud)
    assert taken["INTERPRET"] and taken["BRIEF"]
    assert not taken["CALIBRATION_QUESTIONS"]
    assert not any(validate_mod.shapes_taken(tmp_path / "nowhere").values()), \
        "an unreadable sibling is a prerequisite that has not landed"



def test_an_enum_switch_label_is_a_screen_taken_and_prose_is_not(tmp_path):
    # 058's validator dispatches vector screens as `case CONTEXT_INTERPRET -> ...` inside
    # `switch (screen)`, where the qualified name is illegal (run 20261008T001657Z).
    tool = tmp_path / validate_mod._TOOL
    tool.parent.mkdir(parents=True)
    tool.write_text("switch (screen) {\n"
                    "  case CONTEXT_INTERPRET -> a();\n"
                    "  case CALIBRATION_QUESTIONS, RESPONDENT_QUESTIONS -> b();\n"
                    "}\n/** INTERPRET and BRIEF are described here, in prose only. */\n")
    taken = validate_mod.shapes_taken(tmp_path)
    assert taken["CONTEXT_INTERPRET"] and taken["CALIBRATION_QUESTIONS"]
    assert taken["RESPONDENT_QUESTIONS"]
    assert not taken["INTERPRET"], "`case CONTEXT_INTERPRET` is not a label for INTERPRET"
    assert not taken["BRIEF"]

def test_a_kind_the_validator_does_not_take_is_unmeasured_by_name_for_that_kind_only(tmp_path,
                                                                                      cases):
    keel_cloud = _tool(tmp_path, "CONTEXT_INTERPRET", "PROBLEM_INTERPRET", "SOLUTION_MECHANISM",
                       "RESPONDENT_QUESTIONS", "INTERPRET", "BRIEF")
    batch = _batch(cases)
    unmet = validate_mod.unmet_by_screen(keel_cloud, batch)
    assert list(unmet) == ["CALIBRATION_QUESTIONS"]
    reason = unmet["CALIBRATION_QUESTIONS"]
    assert "058" in reason and "UNMEASURED" in reason
    assert "rule_refusal_rate" in reason and "shape_refusals" in reason
    sent = validate_mod.without_screens(batch, unmet)
    assert not _by_screen(sent, "CALIBRATION_QUESTIONS")
    assert len(sent["cases"]) == 16, "every other kind is still asked"


def test_fold_in_counts_rule_refusals_by_id_and_keeps_shape_and_case_faults_apart():
    folded = validate_mod.fold_in([
        {"case_id": "a", "accepted": True},
        {"case_id": "b", "accepted": False, "refusal": {"kind": "rule", "rule": "C3"}},
        {"case_id": "c", "accepted": False, "refusal": {"kind": "shape", "path": "x"}},
        {"case_id": "d", "accepted": False, "refusal": {"kind": "case"}},
    ])
    assert folded["accepted"] == 1 and folded["refusals_by_rule"] == {"C3": 1}
    assert folded["shape_refusals"] == 1 and folded["case_faults"] == 1
