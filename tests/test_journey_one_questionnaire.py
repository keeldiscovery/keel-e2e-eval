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

def test_the_review_step_no_longer_requires_a_pick_list_on_every_line():
    """FR-002, and the whole of why this spec exists.

    keel-cloud 048 makes the questionnaire the project's, written by one `QUESTIONS` call after the
    last framed stage is approved. Every card `_read_the_lines` reads is read before that. Matrix
    run 36862514753 failed in under two minutes on the first of three.
    """
    body = _code_of("_read_the_lines")
    assert "assert all(line.get(\"chips\")" not in body, (
        "the review step still requires chips on every line -- the assertion run 36862514753 died "
        "on. It belongs to the questionnaire, not to a card drawn before one exists.")
    assert "offers no pick list at all" not in body, (
        "the old failure sentence is still in the review step")
    assert "assert all(line.get(\"chips\")" in _function_source("_read_the_lines"), (
        "the comment that replaced it no longer quotes it, so a reader cannot see what left")


def test_the_three_assertions_that_stood_beside_it_still_stand():
    """FR-001: numbered lines and a separated deal-breaker did not move, and nothing was weakened
    in the course of moving the fourth."""
    body = _function_source("_read_the_lines")
    assert "rendered no lines at all" in body
    assert "is unnumbered" in body
    assert "separates no deal-breaker" in body


def test_the_reason_stands_where_the_assertion_stood():
    """SC-003: a reader of the step can find the assertion that left it, and why, without opening
    keel-cloud. The three names are the three documents that decide it."""
    body = _function_source("_read_the_lines")
    for name in ("048", "026 FR-012", "36862514753"):
        assert name in body, f"the review step's comment never names {name}"
    assert "_the_questions_land" in body, (
        "the review step does not say where the moved assertion went")


def test_the_chips_are_still_recorded_so_the_bundle_keeps_the_number():
    """FR-003. A number that stops being asserted must not stop being written down: a run where a
    `SOLUTION` line carried chips is a run where keel-cloud 049's cross-stage half worked, and that
    is a finding for the bundle."""
    body = _code_of("_read_the_lines")
    assert "chipped" in body and "line.get(\"chips\")" in body, (
        "the review step records no chip count at all")
    assert "asserted nowhere" in body


def test_the_absence_of_chips_is_not_asserted_either():
    """FR-003. `assert not any(...)` here would go red on exactly the run that proves keel-cloud
    049 FR-013 works -- a later stage's line reading an earlier stage's measurement is given the
    referent's own control."""
    body = _code_of("_read_the_lines")
    assert "assert not chipped" not in body
    assert "049" in body, "the review step never says why an early chip is legal"


# ------------------------------------------------------ phase 3: the newest terminal failure, by screen

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

def test_the_questions_step_is_called_between_the_last_approval_and_people():
    """plan §2. The `QUESTIONS` job fires on every approval; only the last one's questionnaire is
    the one a stranger answers, and the founder's own next click after the third *Continue* is
    People -- which keel-web 026 FR-017 locks until `READY`."""
    walk = SCENARIO.index("_walk_stage_live(page, recorder, _get, project_id, stage, founder")
    lands = SCENARIO.index("_the_questions_land(page, recorder, _get, _post")
    # `_invite_one_live` builds a `People` of its own far earlier in the file, so the one this is
    # about is the one AFTER the wait -- the founder's own next screen.
    people = SCENARIO.index("people = People(page, recorder, web_base)", lands)
    assert walk < lands < people, (
        "the questions wait is not between the stage loop and People")


def test_the_wait_polls_the_overview_for_the_state_the_product_reads():
    """FR-004 and FR-015: `Overview.questionsState`, the same field keel-web's side nav gates on and
    the same gate `Project.invite` enforces. A fourth computation of it, in the referee, is exactly
    what keel-web 026 FR-017 stopped doing."""
    body = _function_source("_the_questions_land")
    assert "questionsState" in body
    assert "/overview" in body
    assert "READY" in body


def test_the_ceiling_is_read_off_the_host_object_and_never_branched_on_by_name():
    """FR-005, and the rule `KEELS_AI_JOB_WAIT_S` already works to: per-host facts are read off the
    host type, never written as an `if HOST == "keel"` beside each wait."""
    assert "QUESTIONS_WAIT_S" in SCENARIO
    constant = re.search(r"QUESTIONS_WAIT_S = .*?\n\n", SCENARIO, re.S)
    assert constant, "QUESTIONS_WAIT_S is not defined at module level"
    assert "KEELS_AI_JOB_WAIT_S" in constant.group(0)
    body = _function_source("_the_questions_land")
    assert 'HOST == "keel"' not in body


def test_the_ceiling_is_the_abandonment_plus_slack_and_says_so():
    """FR-005. keel-cloud's own `QUESTIONS` abandonment is PT300S; a Haiku 4.5 call is estimated at
    ~18 s and measured at one to three minutes live. 420 is a number with an argument behind it."""
    assert "420" in SCENARIO
    assert "PT300S" in SCENARIO or "300s" in SCENARIO


def test_a_failed_attempt_is_retried_exactly_once_through_the_products_own_endpoint():
    """FR-006. `POST /v2/projects/{id}/questionnaire/retry` is refused in every state but `FAILED`
    (422, rule `screen`), so the only state it is sent in is the only one it is legal in."""
    body = _function_source("_the_questions_land")
    assert "/questionnaire/retry" in body
    assert body.count("/questionnaire/retry") == 1, (
        "the retry endpoint is named more than once; one send, one place")
    assert "retried" in body


def test_a_second_failure_fails_with_keel_clouds_own_reason():
    """FR-006 and FR-008: never *nothing happened within 420 s* about a wire that named it."""
    body = _function_source("_the_questions_land")
    assert "latest_failure_on_screen" in body
    assert "QUESTIONS" in body


def test_the_keel_door_asks_the_wire_on_every_poll():
    """FR-007, spec 024 FR-010: `KEEL_AI_DISABLED` is answered before a socket is opened, and a run
    that sat out the whole ceiling for it would be reporting the referee's patience."""
    body = _function_source("_the_questions_land")
    assert "_refuse_if_the_door_is_shut" in body
    assert "KEELS_AI" in body


# ------------------------------------------------------- phase 3: what the questions have to be

def test_every_selection_must_offer_a_pick_list_and_that_is_the_moved_assertion():
    """FR-010. This is `assert all(line.get("chips"))`, on the document that owns it now."""
    body = _function_source("_the_questions_land")
    assert "offers no pick list" in body, (
        "the moved assertion has not landed: nothing in the questions step says a selection must "
        "offer something to pick")
    assert "BUCKETS" in body and "OPTIONS" in body


def test_the_ids_are_asserted_project_wide_because_q7_is_project_wide_now():
    """FR-011. `Q7` scoped ids to a stage until 048; it scopes them to the project now, and 049
    reduced `AnchorRef`/`SelectionRef` to a bare id. An id still carrying a stage would mean the
    wire had not moved."""
    body = _function_source("_the_questions_land")
    assert "Q7" in body
    assert "stage" in body


def test_each_stage_cards_slice_resolves_against_the_one_questionnaire():
    """FR-012: `GET /v2/projects/{id}/stages/{stage}`, every `selectionId` resolved by bare id."""
    body = _function_source("_the_questions_land")
    assert "/stages/" in body
    assert "selectionId" in body


def test_reads_resolve_to_a_stage_and_a_line_a_founder_can_count_to():
    """FR-013, and D-2: `reads` itself never reaches a founder -- `readsBelief` is what does."""
    body = _function_source("_the_questions_land")
    assert "readsBelief" in body
    assert "line" in body


def test_the_slice_is_read_on_the_screen_too_and_not_only_on_the_wire():
    """FR-014: keel-web 026 FR-020's `strip__read`, through `OpenedCard.strips()`'s own `read_line`
    -- written for spec 030 and load-bearing for the first time here."""
    body = _function_source("_the_questions_land")
    assert "OpenedCard" in body
    assert "read_line" in body


def test_no_assertion_is_made_about_the_words_the_model_wrote():
    """Spec 016 FR-007 stands. The questions step asserts counts, resolutions and presences; the
    prompts, the option labels and the `Asked:` sentences are the model's own."""
    body = _function_source("_the_questions_land")
    for forbidden in ("Think of the last", "About that night", "Asked:"):
        assert forbidden not in body, f"the questions step pins the model's own words: {forbidden}"
