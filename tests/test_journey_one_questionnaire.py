"""The live journey under one questionnaire (spec `026-journey-one-questionnaire`).

Stackless, offline, and honest about what it can prove. S-012 is live: nothing here runs it, and
nothing here claims a green run. What these tests hold is the two things that **are** stackless and
that would have caught matrix run 36862514753 before a staging box was deployed and two model jobs
were bought:

1. **the scenario's own source** -- the shape `tests/test_journey_through_a_host.py` already uses:
   that the chips assertion is gone from the review step, that the three that stood with it still
   stand, that the step that now owns it is called where the founder waits, and that the ceiling is
   read off the host object rather than branched on by name;
2. **the new reader in `harness/refusals.py`** -- a pure function over the wire's own rows, which is
   the one piece of this spec that can be run for real.

The markup half -- that a review card with no questionnaire really does render no chips, and that
an approved card's `strip__read` really is the slice's founder-facing end -- is
`tests/test_review_card_chips_markup.py`, against keel-web's own markup.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from harness import refusals

REPO = Path(__file__).resolve().parents[1]
SCENARIO = (REPO / "evals" / "test_s012_journey_through_a_host.py").read_text()


def _function_source(name: str) -> str:
    """The body of one top-level `def` in the scenario, up to the next top-level statement."""
    match = re.search(rf"^def {re.escape(name)}\(.*?(?=^\S)", SCENARIO, re.S | re.M)
    assert match, f"the scenario has no top-level `{name}`"
    return match.group(0)


def _code_of(name: str) -> str:
    """The same body with its `#` comment lines dropped.

    Load-bearing, not tidiness: the whole point of this spec is that the assertion it removes is
    **quoted** in the comment that replaced it, so a reader finds what left and why. A test that
    grepped the raw source would read that quotation as the assertion still standing -- and it did,
    on the first run of these tests.
    """
    return "\n".join(line for line in _function_source(name).splitlines()
                      if not line.strip().startswith("#"))


# ------------------------------------------------- phase 2: the review card asks for what it can have

def _rows() -> list[dict]:
    """Two failures and one good row, in the shape `GET /v2/inference-interactions` answers.

    The `QUESTIONS` row carries **no stage**, which is the whole point: `InferenceScreen.QUESTIONS`
    is not a stage's screen and never was.
    """
    return [
        {"interaction_id": "i1", "screen": "PROBLEM_ASSUMPTIONS", "stage": "PROBLEM",
         "status": "APPLIED", "updated_at": "2026-10-01T10:00:00Z"},
        {"interaction_id": "i2", "screen": "QUESTIONS", "stage": None, "status": "JOB_FAILED",
         "updated_at": "2026-10-01T10:05:00Z", "detail": "the model gave up",
         "diagnostic": "RESULT_INVALID", "refusal": {"rule": "screen", "problem": "no questions"},
         "job": {"status": "FAILED"}},
        {"interaction_id": "i3", "screen": "QUESTIONS", "stage": None, "status": "JOB_FAILED",
         "updated_at": "2026-10-01T10:09:00Z", "detail": "and again",
         "job": {"status": "FAILED"}},
    ]


def _get_json(rows):
    def get(path: str):
        assert path.startswith("/v2/inference-interactions?project_id="), path
        return rows
    return get


def test_the_newest_terminal_failure_on_a_screen_is_found():
    """FR-021. The newest of the two `QUESTIONS` failures, with keel-cloud's own words beside it."""
    found = refusals.latest_failure_on_screen(_get_json(_rows()), "p1", "QUESTIONS")
    assert found is not None
    assert found["interaction_id"] == "i3"
    assert found["screen"] == "QUESTIONS"
    assert found["job"] == "FAILED"


def test_the_stage_keyed_reader_is_blind_to_it_which_is_why_the_new_one_exists():
    """D-5. `latest_failure` filters on `row["stage"] == stage`, and a `QUESTIONS` row has none, so
    asked about any of the three stages it answers `None` -- *nothing happened* about a wire that
    knows exactly what did (`runs/DRIFT.md` #37's shape, one axis over)."""
    get = _get_json(_rows())
    for stage in ("PROBLEM", "SOLUTION", "COMMERCIAL"):
        assert refusals.latest_failure(get, "p1", stage) is None


def test_a_screen_that_never_failed_answers_none_rather_than_the_newest_row():
    found = refusals.latest_failure_on_screen(_get_json(_rows()), "p1", "BRIEF")
    assert found is None


def test_a_settled_row_on_that_screen_is_not_a_failure():
    rows = [{"interaction_id": "i1", "screen": "QUESTIONS", "stage": None, "status": "APPLIED"}]
    assert refusals.latest_failure_on_screen(_get_json(rows), "p1", "QUESTIONS") is None


def test_a_wire_that_answers_something_other_than_a_list_is_not_guessed_at():
    assert refusals.latest_failure_on_screen(lambda path: {"error": "nope"}, "p1",
                                             "QUESTIONS") is None


def test_the_stage_keyed_reader_still_reads_exactly_what_it_read():
    """The refactor that gave the two functions one private helper must not have moved the old
    one. Same rows, keyed by stage, same answer."""
    rows = [
        {"interaction_id": "a", "screen": "SOLUTION_FRAME", "stage": "SOLUTION",
         "status": "JOB_FAILED", "updated_at": "2026-10-01T09:00:00Z", "job": {"status": "FAILED"}},
        {"interaction_id": "b", "screen": "SOLUTION_FRAME", "stage": "SOLUTION",
         "status": "JOB_FAILED", "updated_at": "2026-10-01T09:30:00Z", "job": {"status": "FAILED"}},
    ]
    found = refusals.latest_failure(_get_json(rows), "p1", "SOLUTION")
    assert found is not None and found["interaction_id"] == "b"
    assert found["stage"] == "SOLUTION"


# ------------------------------------------------------------- phase 3: the wait, where the founder waits

def test_the_ceiling_is_the_abandonment_plus_slack_and_says_so():
    """FR-005. keel-cloud's own `QUESTIONS` abandonment is PT300S; a Haiku 4.5 call is estimated at
    ~18 s and measured at one to three minutes live. 420 is a number with an argument behind it."""
    assert "420" in SCENARIO
    assert "PT300S" in SCENARIO or "300s" in SCENARIO


def test_the_short_journey_no_longer_claims_to_buy_the_questions():
    """FR-019 / D-8. Since 048 the assumptions job writes no questionnaire and the `QUESTIONS` job
    fires on the **approval**, which the short run deliberately never makes."""
    from harness import agent_host
    sentence = agent_host.short_stops_at("keel")
    assert "questions" not in sentence.lower(), sentence
    assert "PROBLEM_ASSUMPTIONS" in sentence, (
        "the sentence lost the screens it was right about along with the word it was wrong about")


def test_the_accounting_step_says_a_questions_retry_shows_up_in_it():
    """FR-020 / D-9. The retry does not remove the first attempt's failed interaction, and the
    tail's *every job COMPLETED* step will name it. Deliberate, and said out loud."""
    at = SCENARIO.index("leg two: zero refusals")
    # The reason stands *above* the step, which is where this branch's reasons go.
    tail = SCENARIO[at - 1200:at + 1400]
    assert "QUESTIONS" in tail
    assert "retry" in tail


def test_the_review_cards_asked_first_reader_names_the_block_keel_web_deleted():
    """D-6. Not fixed here -- three other places in this repository still require it, and what
    ORI-U4 measures now is a rubric question with its own spec. Named, so the next reader finds the
    ledger entry instead of an empty string."""
    browser = (REPO / "harness" / "browser.py").read_text()
    reader = browser[browser.index("def asked_first"):][:1600]
    assert "026" in reader and "FR-011" in reader


# ------------------------------------------------------------------- phase 6: the bundle says what it did

def test_the_bundle_name_does_not_move():
    """FR-022. `s012-journey-<host>` means what it meant; a reader comparing this week's bundle
    with last week's must not have to translate a name."""
    from harness import agent_host
    assert agent_host.bundle_slug("claude", "full", "plugin") == "s012-journey-claude"
    assert agent_host.bundle_slug("claude", "short", "plugin") == "s012-journey-claude-short"


@pytest.mark.parametrize("name", ["spec.md", "plan.md", "tasks.md"])
def test_the_spec_kit_trio_is_on_the_branch(name):
    assert (REPO / "specs" / "026-journey-one-questionnaire" / name).is_file()


def test_the_next_live_run_is_written_down_and_not_typed():
    """FR-024. S-012 spends; this branch spends nothing. The command the founder types is in the
    spec, with its dispatch inputs and its bundle name."""
    spec = (REPO / "specs" / "026-journey-one-questionnaire" / "spec.md").read_text()
    assert "make eval-live K=s012" in spec
    assert "macos-latest-claude-py3.13" in spec
    assert "runs/<stamp>-s012-journey-claude/" in spec


def test_there_is_no_why_invented_for_the_journey():
    """FR-024, and `instructions/why.py`'s own boundary: `WHY=` gates the instruction eval and
    nothing else. A sixth named event for S-012 would be adding a gate where the design has none."""
    spec = (REPO / "specs" / "026-journey-one-questionnaire" / "spec.md").read_text()
    assert "WHY" in spec
    assert "instruction-eval" in spec
    scenario_has_why = "WHY" in SCENARIO
    assert not scenario_has_why, "the journey scenario grew a WHY gate it does not have"
