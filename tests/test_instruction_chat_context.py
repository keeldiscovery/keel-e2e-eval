"""The chat screens' contexts and cases (spec 035 FR-002, FR-003, T004, T005; `MARKS_VERSION` 17, call 76).

Built "exactly as keel-cloud's `ScreenContextBuilder` does": the key order is the exporter's, `chat.opens_with` is
filled with the context slots and the recall window, `chat.frames` is sorted, the dependent beliefs are the ones
`dependsOn` names (Current solution for Relative advantage, Existing sacrifice for Price, Frequency for a habit),
and the feedback context carries the item, the kinds an added option may take and the five rules. The tests that
read keel-cloud's canon skip, by name, below revision 9."""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from instructions import chat as chat_mod
from instructions import context as context_mod
from instructions import contract as contract_mod
from instructions import corpus as corpus_mod
from instructions import models as models_mod
from instructions import prompts as prompts_mod
from instructions import registry as registry_mod
from stack.config import load_config
from tests import v9_fixtures as fx

FIXTURES = Path("src") / "test" / "resources" / "keel" / "executor-fixtures"
REGISTRY_JSON = Path("src") / "main" / "resources" / "keel" / "dimension-registry.json"


@pytest.fixture(scope="module")
def keel_cloud():
    fx.canon_entry("03-lullaby.yaml")
    path = load_config(validate=False).keel_cloud
    if not (Path(path) / FIXTURES / "CALIBRATION_CHAT" / "payload.json").is_file():
        pytest.skip("keel-cloud carries no CALIBRATION_CHAT executor fixture (before 083)")
    return Path(path)


@pytest.fixture(scope="module")
def registry(keel_cloud):
    return registry_mod.load(keel_cloud / REGISTRY_JSON, check=False)


@pytest.fixture(scope="module")
def corpus(keel_cloud, registry):
    return corpus_mod.load(keel_cloud).bind(registry)


def fixture_payload(keel_cloud, screen):
    return json.loads((keel_cloud / FIXTURES / screen / "payload.json").read_text(encoding="utf-8"))


def case_of(corpus, idea, dimension):
    return next(c for c in corpus.idea(idea).cases if c.dimension == dimension)


def chat(corpus, registry, idea, dimension):
    sheet = chat_mod.ideas()[idea]
    scenario = next(s for s in corpus.scenarios if s["id"] == idea)
    return context_mod.build_calibration_chat(case_of(corpus, idea, dimension), sheet, scenario, registry)


def test_the_default_keys_are_the_executor_fixtures_in_its_order(keel_cloud):
    """The context keys keel-cloud's own fixture was written with are the ones (and the order) we fall back to."""
    assert list(fixture_payload(keel_cloud, "CALIBRATION_CHAT")["context"]) == \
        context_mod.DEFAULT_KEYS[contract_mod.SCREEN_CHAT]
    assert list(fixture_payload(keel_cloud, "ITEM_FEEDBACK")["context"]) == \
        context_mod.DEFAULT_KEYS[contract_mod.SCREEN_FEEDBACK]


def test_the_chat_context_has_the_fixtures_shape_and_the_openings_filled(keel_cloud, corpus, registry):
    context = chat(corpus, registry, "lullaby", "problem.current_solution_satisfaction")
    fixture = fixture_payload(keel_cloud, "CALIBRATION_CHAT")["context"]
    assert list(context) == list(fixture)
    assert list(context["chat"]) == list(fixture["chat"]) and list(context["context"]) == list(fixture["context"])
    assert context["chat"]["opens_with"] == fixture["chat"]["opens_with"], "slots filled with the idea's own"
    assert context["chat"]["measures"] == ["TIME", "MONEY", "EFFORT"]
    assert context["chat"]["frames"] == fixture["chat"]["frames"] and list(context["chat"]["frames"]) == \
        sorted(context["chat"]["frames"])
    assert context["context"]["window"] == "the last 7 nights" and context["b2b"] is False
    assert context["proposal_id"] == "p-lullaby-problem.current_solution_satisfaction"
    assert context["depends_on"] == {} and context["idea_words"]


def test_relative_advantage_reads_the_current_solution_cap(corpus, registry):
    context = chat(corpus, registry, "payroll", "solution.relative_advantage")
    assert context["depends_on"] == {"problem.current_solution_satisfaction":
                                     "Today's way costs payroll practitioners at mid-size companies 2 to 3 hours."}
    assert context["context"]["window"] == "the last cycle" and context["b2b"] is True


def test_price_reads_existing_sacrifice_and_a_habit_reads_frequency(corpus, registry):
    price = chat(corpus, registry, "payroll", "commercial.price")
    assert price["depends_on"] == {"commercial.existing_sacrifice":
                                   "It costs the payer $2,400 to $4,800 a quarter."}
    habit = chat(corpus, registry, "voice-notes", "solution.adoption_friction")
    assert list(habit["depends_on"]) in ([], ["problem.frequency"]), "present only when the founder measured it"


def test_a_belief_the_founder_left_out_is_not_a_dependency(corpus, registry):
    # payroll's Frequency is `unsure`; no belief, no key (keel-cloud puts only beliefs that exist)
    context = chat(corpus, registry, "payroll", "solution.adoption_friction")
    assert context["depends_on"] == {}


def test_every_dimension_has_a_context_and_the_statement_is_its_vectors(corpus, registry):
    for idea in corpus.chat:
        for case in idea.cases:
            context = chat(corpus, registry, idea.id, case.dimension)
            sheet = chat_mod.ideas()[idea.id]
            assert context["statement"] == sheet["statements"][registry.by_key(case.dimension).vector]
            assert context["dimension"] == case.dimension and context["b2b"] is idea.b2b


def test_the_feedback_context_has_the_fixtures_shape_and_the_five_rules(keel_cloud):
    case = chat_mod.feedback_cases()[0]
    context = context_mod.build_item_feedback(case, chat_mod.RULES)
    fixture = fixture_payload(keel_cloud, "ITEM_FEEDBACK")["context"]
    assert list(context) == list(fixture)
    assert context["rules"] == fixture["rules"], "the five refusals, in ItemRules.Rule's order"
    assert context["addable"] == ["NONE", "SOMEONE_ELSE"] and context["vector"] == "PROBLEM"
    assert list(context["item"]) == ["question", "options"] and list(context["item"]["options"][0]) == \
        list(fixture["item"]["options"][0])


def test_the_contexts_follow_the_exports_key_order_not_ours():
    context = context_mod.build_item_feedback(chat_mod.feedback_cases()[0], chat_mod.RULES,
                                              ["rules", "dimension", "wibble"])
    assert list(context) == ["rules", "dimension", "wibble"] and context["wibble"] is None


# --------------------------------------------------------------------------------------- the cases

def exported_with(tmp_path, registry):
    ex = fx.exported(tmp_path)
    return dataclasses.replace(ex, registry=registry)


def test_a_case_an_idea_and_dimension_and_a_case_a_feedback_row(tmp_path, corpus, registry):
    ex = exported_with(tmp_path, registry)
    cases = prompts_mod.build_chat_cases(corpus, ex, fx.instructions(), fx.FakeRuntime, n_runs=2)
    chat_cases = [c for c in cases if c.kind == "CHAT"]
    feedback = [c for c in cases if c.kind == "FEEDBACK"]
    assert len(chat_cases) == 41 * 2 and len(feedback) == len(chat_mod.feedback_cases()) * 2
    first = chat_cases[0]
    assert first.case_id == "chat/dark-chocolate/problem.frequency/run1" and first.screen == "CALIBRATION_CHAT"
    assert first.payload["input"]["content"] == "Two to four times a week."
    assert first.entry_id == "dark-chocolate" and first.meta["chat_case"].measure == "COUNT"
    assert first.payload["instruction"] == "INSTRUCTION FOR CALIBRATION_CHAT"
    assert first.payload["response_contract"] == ex.for_screen("CALIBRATION_CHAT")
    assert feedback[0].screen == "ITEM_FEEDBACK" and feedback[0].payload["input"]["content"] == \
        chat_mod.feedback_cases()[0]["request"]
    assert first.prompt.startswith("INSTRUCTION FOR CALIBRATION_CHAT")


def test_both_chat_kinds_route_through_the_calibration_class():
    for kind in ("CHAT", "FEEDBACK"):
        assert models_mod.KIND_TO_CLASS[kind] == "calibration"
    for screen in chat_mod.CHAT_SCREENS:
        assert models_mod.SCREEN_TO_CLASS[screen] == "calibration"
    assert set(chat_mod.CHAT_SCREENS) <= set(contract_mod.MODEL_SCREENS)


def test_the_chat_denominators_are_read_off_the_cases(tmp_path, corpus, registry):
    from instructions import run as run_mod                                  # noqa: PLC0415
    ex = exported_with(tmp_path, registry)
    cases = prompts_mod.build_chat_cases(corpus, ex, fx.instructions(), fx.FakeRuntime, n_runs=3)
    row = run_mod.chat_denominators(cases)
    assert row == {"chat": 41, "ideas": 6, "leave_out": 3, "follow_up_expected": 5, "importance": 4,
                   "feedback": len(chat_mod.feedback_cases()),
                   "feedback_refusals": sum(1 for c in chat_mod.feedback_cases()
                                            if c["expect"]["outcome"] == "refuse")}
    assert "41 chat cases over 6 ideas" in run_mod._chat_denominator_line(row)


def test_the_instruction_stems_name_the_two_templates():
    from instructions import instruction as instruction_mod                  # noqa: PLC0415
    assert instruction_mod.STEMS["CALIBRATION_CHAT"] == "calibration-chat"
    assert instruction_mod.STEMS["ITEM_FEEDBACK"] == "item-feedback"
    assert instruction_mod.path_for(Path("/k"), "ITEM_FEEDBACK").name == "item-feedback.md"
