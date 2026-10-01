"""The `QUESTIONS` screen this eval gained (spec 025 US4, FR-013 to FR-017, T016).

One Haiku call per corpus entry, **after** that entry's three assumptions cases and before its
readings, because that is the order production runs them in: the job fires on the approval that
makes every framed stage approved (keel-cloud 048 FR-022), and the case id is what `-k` filters on.

**Its answer is not scored.** It reaches `rule_refusal_rate` through the aggregate -- where `Q5`,
`Q6` and `Q8` are reachable -- and `register.html`, where a person reads the produced anchor prompts
beside the corpus's own. A mark here would be similarity to one hand-written questionnaire, which is
judgement call 10 arriving on a fourth subject.
"""

from __future__ import annotations

import pytest

from instructions import contract as contract_mod
from instructions import context as context_mod
from instructions import instruction as instruction_mod
from instructions import models as models_mod
from instructions import prompts as prompts_mod
from instructions import report as report_mod
from instructions.corpus import Entry, GoldenBelief
from stack.config import load_config

SCREENS = ["PROBLEM_ASSUMPTIONS", "SOLUTION_ASSUMPTIONS", "COMMERCIAL_ASSUMPTIONS",
           "QUESTIONS", "INTERPRET", "BRIEF"]

KEYS = {
    "PROBLEM_ASSUMPTIONS": ["problem_statement", "market"],
    "SOLUTION_ASSUMPTIONS": ["solution_statement", "market"],
    "COMMERCIAL_ASSUMPTIONS": ["commercial_statement", "market"],
    "QUESTIONS": ["project_name", "market", "founder_name", "stage_statements", "measurements"],
    "INTERPRET": ["invitation_id", "anchors"],
    "BRIEF": ["project_name", "market", "claims"],
}


class _Exported:
    """keel-cloud's exported contract, as much of it as `build_cases` reads."""

    def keys_for(self, screen):
        return list(KEYS[screen])

    def for_screen(self, screen):
        return {"allowed_outcomes": ["COMPLETED"], "completed_result_schema": {"screen": screen}}


def _belief(bid, stage, selection):
    return GoldenBelief(id=bid, stage=stage, heading=f"{bid} heading", statement=f"{bid}.",
                        founder_phrase=None, risk="LOAD_BEARING", asked_of="r1", mark="DIRECT",
                        expectation={"type": "CHOICE", "options": ["yes", "no"],
                                     "expected": "yes"},
                        selection=selection, group=None)


@pytest.fixture()
def entry():
    return Entry(
        id="09-fixture", title="A fixture", market={"country": "GB", "region": None,
                                                     "language": "en-GB"},
        statements={"PROBLEM": "The problem.", "SOLUTION": "The solution.",
                    "COMMERCIAL": "The price."},
        roles=[{"id": "r1", "label": "Restaurant managers", "roleType": "PRACTITIONER",
                "about": "runs the kitchen"}],
        beliefs=[_belief("P1", "PROBLEM", "S1"), _belief("P2", "PROBLEM", "S2"),
                 _belief("S3", "SOLUTION", "S3"), _belief("C4", "COMMERCIAL", "S4")],
        questionnaire={"anchors": [
            {"id": "A1", "stages": ["PROBLEM", "SOLUTION"], "prompt": "Think of the last one.",
             "taps": [], "selections": [{"id": "S1", "prompt": "a?"}, {"id": "S2", "prompt": "b?"},
                                        {"id": "S3", "prompt": "c?"}]},
            {"id": "A3", "stages": ["COMMERCIAL"], "prompt": "Think of the last purchase.",
             "taps": [], "selections": [{"id": "S4", "prompt": "d?"}]}]},
        answers=[{"person": "Ada", "anchors": {"A1": {"text": "Tuesday.",
                                                       "anchoring": "ANCHORED"}}, "picks": {}}],
        expected={}, path=None, sha256="0" * 64)


@pytest.fixture(scope="module")
def executor_module():
    config = load_config(validate=False)
    try:
        executor, _validator = prompts_mod.load_runtime(config.keel_runtime)
    except prompts_mod.RuntimeUnavailable as reason:
        pytest.skip(str(reason))
    return executor


def _cases(entry, executor_module, n_runs=1):
    instructions = {screen: f"INSTRUCTION FOR {screen}" for screen in SCREENS}
    return prompts_mod.build_cases(entry, _Exported(), instructions, executor_module,
                                   n_runs=n_runs)


# ------------------------------------------------------------------------------- where it sits

def test_one_questions_case_per_entry_after_the_three_assumptions_cases(entry, executor_module):
    cases = _cases(entry, executor_module)

    assert [c.kind for c in cases] == ["ASSUMPTIONS", "ASSUMPTIONS", "ASSUMPTIONS",
                                       "QUESTIONS", "READING", "BRIEF"]
    questions = [c for c in cases if c.kind == "QUESTIONS"]
    assert len(questions) == 1
    assert questions[0].case_id == "09-fixture/QUESTIONS/run1"
    assert questions[0].subject == "QUESTIONS"
    assert questions[0].screen == contract_mod.SCREEN_QUESTIONS
    assert questions[0].existing_roles == [], "it has no stage and no roles to arrive into"


def test_it_repeats_once_per_run_index_like_every_other_case(entry, executor_module):
    cases = _cases(entry, executor_module, n_runs=3)

    ids = [c.case_id for c in cases if c.kind == "QUESTIONS"]
    assert ids == [f"09-fixture/QUESTIONS/run{n}" for n in (1, 2, 3)]


def test_k_questions_selects_it_beside_k_reading_and_k_brief(entry, executor_module):
    cases = _cases(entry, executor_module, n_runs=2)

    def filtered(needle):
        return [c for c in cases
                if needle in c.case_id.lower()
                or (needle == "reading" and c.kind == "READING")
                or (needle == "assumptions" and c.kind == "ASSUMPTIONS")
                or (needle == "questions" and c.kind == "QUESTIONS")
                or (needle == "brief" and c.kind == "BRIEF")]

    assert [c.kind for c in filtered("questions")] == ["QUESTIONS", "QUESTIONS"]
    assert all(c.kind == "READING" for c in filtered("reading"))


def test_its_payload_is_the_questions_instruction_and_keel_clouds_own_contract(entry,
                                                                              executor_module):
    case = next(c for c in _cases(entry, executor_module) if c.kind == "QUESTIONS")

    assert case.payload["instruction"] == "INSTRUCTION FOR QUESTIONS"
    assert case.payload["response_contract"]["completed_result_schema"] == {"screen": "QUESTIONS"}
    assert list(case.payload["context"]) == KEYS["QUESTIONS"]


# ----------------------------------------------------------------------------------- its context

def test_the_context_is_048_fr_011s_five_keys_and_no_more(entry):
    context = context_mod.build_questions(entry, KEYS["QUESTIONS"])

    assert list(context) == ["project_name", "market", "founder_name", "stage_statements",
                             "measurements"]
    assert context["project_name"] == "A fixture"
    assert context["market"] == {"country": "GB", "region": None, "language": "en-GB"}
    assert context["founder_name"] is None, \
        "a corpus entry records no founder's name; the key is written and left null, not invented"
    assert context["stage_statements"] == {"PROBLEM": "The problem.", "SOLUTION": "The solution.",
                                           "COMMERCIAL": "The price."}


def test_measurements_are_indexed_zero_based_project_wide_across_all_three_stages(entry):
    measurements = context_mod.build_questions(entry, KEYS["QUESTIONS"])["measurements"]

    assert [m["index"] for m in measurements] == [0, 1, 2, 3], "0-based, project-wide, once through"
    assert [m["stage"] for m in measurements] == ["PROBLEM", "PROBLEM", "SOLUTION", "COMMERCIAL"]
    assert list(measurements[0]) == ["index", "stage", "heading", "statement", "risk", "mark",
                                     "role", "expectation"]
    assert measurements[0]["role"] == "Restaurant managers", "the label, not the id"


# ------------------------------------------------------------------------------------- its class

def test_it_routes_to_the_questions_class_on_the_light_tier_and_carries_no_effort():
    table = models_mod.parse({
        "version": 7,
        "hosts": {"claude": {"light": "claude-haiku-4-5", "standard": "claude-sonnet-5-5"}},
        "efforts": {"claude": {"standard": "medium"}},
        "classes": {"frame": "standard", "assumptions": "standard", "reframe": "standard",
                    "reading": "light", "brief": "standard", "questions": "light"}})

    assert table.tier_for("questions") == "light"
    assert table.resolve_kind("claude", "QUESTIONS") == "claude-haiku-4-5"
    assert table.resolve_effort_kind("claude", "QUESTIONS") is None, \
        "`effort` errors on Haiku 4.5 -- the same reason a reading carries none"


def test_the_stem_and_the_screen_constant_exist():
    assert contract_mod.SCREEN_QUESTIONS == "QUESTIONS"
    assert instruction_mod.STEMS["QUESTIONS"] == "questions"


def test_the_questions_instruction_is_where_keel_cloud_keeps_it():
    """Read through `instruction.read` from keel-cloud's own resource directory, `.strip()`ed and
    not templated -- the same rule every other screen's prose is read by."""
    config = load_config(validate=False)
    path = instruction_mod.path_for(config.keel_cloud, "QUESTIONS")
    assert path.name == "questions.md"
    if not path.is_file():
        pytest.skip("keel-cloud has not landed spec 048's questions.md on this checkout")
    assert instruction_mod.read(config.keel_cloud, "QUESTIONS").strip()


# ------------------------------------------------------------- the register, and nothing scored

class _Corpus:
    def __init__(self, entries):
        self.entries = entries


def test_the_register_groups_the_questionnaire_by_entry_and_carries_no_score(entry, tmp_path):
    produced = {"09-fixture": {"introduction": "A few questions.", "anchors": [
        {"occasion": "the last delivery", "prompt": "What happened?",
         "selections": [{"reads": [0, 1], "prompt": "How long?"}]}]}}

    blocks = report_mod.register_blocks(_Corpus([entry]), produced)

    assert list(blocks) == ["GB · en-GB"]
    assert list(blocks["GB · en-GB"]) == ["09-fixture"]
    questionnaire = blocks["GB · en-GB"]["09-fixture"]["questionnaire"]
    assert len(questionnaire["produced"]) == 1
    assert [a["id"] for a in questionnaire["golden"]] == ["A1", "A3"], \
        "the entry's whole revised anchor list, not one stage's"

    path = report_mod.render_register(tmp_path, entries_by_market=blocks)
    html = path.read_text(encoding="utf-8")
    assert "the last delivery" in html and "How long?" in html
    assert "Nothing on this page is scored" in html
    assert "✓" not in html and "✗" not in html
