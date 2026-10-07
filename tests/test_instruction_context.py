"""The seven context builders at `MARKS_VERSION` 9 (spec 029 contracts/screen-shapes.md §2; T018).

Every key the exporter names, in the exporter's order, filled from corpus revision 3 and the
registry and nothing else -- and, as much to the point, what each one must **not** carry: no
solution field on the PROBLEM calibration job (US2.1), no mechanism and no founder answer on Part 1,
no `stage` and no `anchors[]` on a read, no `claims` on the brief.
"""

from __future__ import annotations

import pytest

from instructions import context as context_mod
from tests import v9_fixtures as fx


@pytest.fixture()
def entry():
    return fx.entry()


@pytest.fixture()
def registry():
    return fx.registry()


def test_every_builder_fills_the_exporters_keys_in_the_exporters_order(entry, registry):
    keys = ["market", "unknown_key", "project_name", "context_fields"]
    built = context_mod.build_context_interpret(entry, keys)
    assert list(built) == keys, "the order is the contract (ScreenContextBuilder's LinkedHashMap)"
    assert built["unknown_key"] is None, "an unknown key is written null, never dropped"


def test_context_interpret_carries_the_four_slots_and_nothing_from_the_mechanism(entry):
    built = context_mod.build_context_interpret(entry)
    assert built["context_fields"] == {"who": "commuter", "what": "get out of the door on time",
                                       "when": "the morning they cannot find their keys",
                                       "which_people": "commuters in Leeds who cycle to work"}
    assert built["project_name"] == entry.title
    assert "whistle" not in repr(built) and "tag" not in repr(built)


def test_problem_interpret_carries_the_context_and_no_solution_field(entry):
    built = context_mod.build_problem_interpret(entry)
    assert set(built) == {"context", "market", "interaction_history"}
    assert built["context"]["actor_plural"] == "commuters who cycle"
    assert context_mod.seed_of(entry, "PROBLEM_INTERPRET") == entry.statements["problem"]


def test_solution_mechanism_reads_the_corpus_problem_sentence_never_a_live_answer(entry):
    built = context_mod.build_solution_mechanism(entry)
    assert built["problem"] == {"statement": entry.interpretations["problem"]}
    assert context_mod.seed_of(entry, "SOLUTION_MECHANISM") == entry.statements["solution"]


def _dotted(dimension: dict) -> set:
    out = set()
    for key, value in dimension.items():
        if key in ("founder", "respondent"):
            out |= {f"{key}.{inner}" for inner in value}
        else:
            out.add(key)
    return out


def test_the_problem_calibration_job_carries_the_slice_with_thirteen_fields_and_no_solution(
        entry, registry):
    built = context_mod.build_calibration(entry, "PROBLEM", registry)
    assert built["vector"] == "PROBLEM"
    assert built["problem"] == {"statement": entry.interpretations["problem"]}
    assert "mechanism" not in built and "solution" not in built and "persona" not in built, \
        "US2.1: the PROBLEM job carries no solution field at all, not even a null one"
    dimensions = built["dimensions"]
    assert [d["key"] for d in dimensions] == [d.key for d in registry.slice("PROBLEM")]
    assert len(dimensions) == 9
    expected = {"key", "order", "name", "meaning", "weight", "founder.control", "founder.guidance",
                "founder.normalized", "founder.option_rule", "founder.belief_template",
                "founder.unsure_allowed", "respondent.anchor", "respondent.guidance"}
    for dimension in dimensions:
        assert _dotted(dimension) == expected, dimension["key"]


def test_the_solution_and_commercial_jobs_see_the_mechanism_and_the_persona(entry, registry):
    solution = context_mod.build_calibration(entry, "SOLUTION", registry)
    assert solution["mechanism"]["mechanism"] == entry.solution_mechanism["mechanism"]
    assert "mechanism_terms" not in solution["mechanism"], "no_leak's list is not an input"
    assert "persona" not in solution
    commercial = context_mod.build_calibration(entry, "COMMERCIAL", registry)
    assert commercial["persona"] == {"decision_maker": "same_person"}
    assert len(commercial["dimensions"]) == 7


def test_part_one_carries_no_mechanism_and_no_founder_answer_ever(entry, registry):
    plan = entry.plan()
    built = context_mod.build_respondent(entry, 1, plan, registry)
    assert "mechanism" not in built
    assert [item["key"] for item in built["items"]] == plan[1]
    assert set(built["items"][0]["respondent"]) == {"anchor", "control", "guidance",
                                                     "option_rule", "chips"}
    text = repr(built)
    for value in ("throws the morning off", "is hit and miss", "2 to 4 nights", "lateness"):
        assert value not in text, f"a founder answer reached the respondent screen: {value}"
    assert built["founder_options"]["problem.severity"] == \
        ["barely", "a_little", "moderately", "very", "extremely"], "the founder's option SET"
    assert "something_else" not in built["founder_options"]["problem.consequence"]


def test_parts_two_and_three_carry_the_mechanism(entry, registry):
    for part in (2, 3):
        built = context_mod.build_respondent(entry, part, entry.plan(), registry)
        assert built["mechanism"]["output"] == entry.solution_mechanism["output"]
        assert built["link"] == "PRIMARY"


def test_the_b2b_link_carries_the_registrys_b2b_block():
    b2b = fx.entry(fx.ENTRY_B2B)
    built = context_mod.build_respondent(b2b, 3, b2b.plan(), b2b.registry,
                                         link=context_mod.LINK_B2B)
    assert built["link"] == "COMMERCIAL_B2B"
    sacrifice = next(i for i in built["items"] if i["key"] == "commercial.existing_sacrifice")
    assert sacrifice["respondent"]["b2b"]["anchor"] == "last_cycle"


def test_a_read_carries_an_invitation_and_one_story_and_no_stage_or_anchors(entry):
    person = entry.person("Bo Brand")
    built = context_mod.build_interpret(entry, person)
    assert built == {"invitation_id": "09-fixture/Bo Brand",
                     "story": {"prompt": None, "text": person.story, "chip": None}}
    assert "anchors" not in built and "stage" not in repr(built)


def test_the_brief_carries_three_vectors_with_their_verdicts_and_belief_sentences(entry, registry):
    built = context_mod.build_brief(entry)
    assert list(built) == ["project_name", "market", "context", "vectors"]
    assert "claims" not in built
    vectors = built["vectors"]
    assert [v["vector"] for v in vectors] == ["PROBLEM", "SOLUTION", "COMMERCIAL"]
    problem = vectors[0]
    assert (problem["verdict"], problem["deciding"]) == ("NOT_HOLDING_UP", "problem.duration")
    duration = next(d for d in problem["dimensions"] if d["key"] == "problem.duration")
    assert duration["belief_sentence"] == \
        entry.founder_calibration["problem.duration"]["belief_sentence"]
    assert duration["founder_phrase"] == "5 to 15 minutes"
    assert duration["observed"] == "8 minutes", "the median in the founder's own unit (call 19)"
    assert duration["below"] is None and duration["above"] is None


def test_the_stage_shaped_builders_are_gone():
    for name in ("earlier_lines", "build_questions", "anchors_for", "roles_for",
                 "measurements_for", "claims_for", "build_assumptions", "build_reading"):
        assert not hasattr(context_mod, name), name
