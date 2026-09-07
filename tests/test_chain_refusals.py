"""A wedged chain, read off the wire instead of waited out (`runs/DRIFT.md` #37).

Every fixture below is the shape keel-cloud actually returned on the live run that found this --
`runs/20260907T194456Z-s004-stranger-who-gives-orders-live`, project
`f17b0a61-1f8c-4630-a2a6-3eb55abe2809`, four minutes of a real model's money spent waiting for an
answer that had already been refused. No stack, no browser, no model.
"""

from __future__ import annotations

import pytest

from harness import refusals

FRAME_ID = "bf051875-eeca-47e0-91e2-6ba86ab0c709"
CHILD_ID = "ea1e3cef-45d8-48ec-b1be-729308cf7be5"
PROJECT = "f17b0a61-1f8c-4630-a2a6-3eb55abe2809"
DIAGNOSTIC = ("Q4: beliefs share selection 'S1', which offers only one choice, so they cannot all "
              "be answered — make the selection multi-select, or split the beliefs onto selections "
              "of their own")

#: **The refusal is not the row the overview names.** The frame stayed `ACCEPTED` for as long as
#: the stack was up; the row that failed is its auto-chained child, and the stage went on
#: reporting the frame as its pending interaction.
OVERVIEW = {
    "stages": [
        {"type": "PROBLEM", "framed": True, "approved": True},
        {"type": "SOLUTION", "framed": False, "approved": False,
         "pendingInteraction": {"interactionId": FRAME_ID, "screen": "SOLUTION_FRAME",
                                 "status": "ACCEPTED"}},
        {"type": "COMMERCIAL", "framed": False, "approved": False},
    ],
}
FRAME = {"interaction_id": FRAME_ID, "screen": "SOLUTION_FRAME", "stage": "SOLUTION",
         "status": "ACCEPTED", "next_interaction_id": CHILD_ID}
CHILD = {"interaction_id": CHILD_ID, "screen": "SOLUTION_ASSUMPTIONS", "stage": "SOLUTION",
         "status": "DOMAIN_REFUSED", "parent_interaction_id": FRAME_ID,
         "detail": "Your agent's answer couldn't be recorded — start the step again.",
         "diagnostic": DIAGNOSTIC}


def _wire(**overrides):
    bodies = {f"/v2/projects/{PROJECT}/overview": OVERVIEW,
              f"/v2/inference-interactions/{FRAME_ID}": FRAME,
              f"/v2/inference-interactions/{CHILD_ID}": CHILD}
    bodies.update(overrides)
    calls: list[str] = []

    def get_json(path):
        calls.append(path)
        return bodies.get(path, {})

    get_json.calls = calls
    return get_json


def test_the_refusal_is_found_through_the_chain_the_overview_does_not_name():
    refusal = refusals.stage_refusal(_wire(), PROJECT, "SOLUTION")
    assert refusal is not None, "the refused child was not reached from the frame the stage names"
    assert refusal["status"] == "DOMAIN_REFUSED"
    assert refusal["screen"] == "SOLUTION_ASSUMPTIONS"
    assert refusal["diagnostic"] == DIAGNOSTIC
    assert refusal["interaction_id"] == CHILD_ID


def test_describe_quotes_keel_clouds_own_words():
    line = refusals.describe(refusals.stage_refusal(_wire(), PROJECT, "SOLUTION"))
    assert "SOLUTION_ASSUMPTIONS is DOMAIN_REFUSED" in line
    assert "Q4: beliefs share selection 'S1'" in line, (
        "the rule that was broken is the whole point of the line")


def test_a_healthy_chain_is_not_a_refusal():
    """A slow model is not a refused one -- this must stay `None`, or every real timeout starts
    reporting a refusal that never happened."""
    healthy = dict(CHILD, status="PENDING", detail=None, diagnostic=None)
    wire = _wire(**{f"/v2/inference-interactions/{CHILD_ID}": healthy})
    assert refusals.stage_refusal(wire, PROJECT, "SOLUTION") is None


def test_a_stage_with_nothing_pending_is_not_a_refusal():
    assert refusals.stage_refusal(_wire(), PROJECT, "COMMERCIAL") is None
    assert refusals.stage_refusal(_wire(), PROJECT, "PROBLEM") is None


def test_an_unknown_stage_reads_as_no_refusal_rather_than_raising():
    assert refusals.stage_refusal(_wire(), PROJECT, "NOT_A_STAGE") is None


def test_the_frame_itself_failing_is_found_without_a_hop():
    failed_frame = dict(FRAME, status="JOB_FAILED", detail="the executor reported an error")
    wire = _wire(**{f"/v2/inference-interactions/{FRAME_ID}": failed_frame})
    refusal = refusals.stage_refusal(wire, PROJECT, "SOLUTION")
    assert refusal["screen"] == "SOLUTION_FRAME" and refusal["status"] == "JOB_FAILED"
    assert f"/v2/inference-interactions/{CHILD_ID}" not in wire.calls, (
        "the chain was followed past a row that had already failed")


def test_a_chain_that_points_at_itself_ends_rather_than_loops():
    looping = dict(FRAME, next_interaction_id=FRAME_ID)
    wire = _wire(**{f"/v2/inference-interactions/{FRAME_ID}": looping})
    assert refusals.stage_refusal(wire, PROJECT, "SOLUTION") is None
    assert wire.calls.count(f"/v2/inference-interactions/{FRAME_ID}") == 1


@pytest.mark.parametrize("status", sorted(refusals.TERMINAL_FAILURE_STATUSES))
def test_every_terminal_status_keel_cloud_can_write_is_a_refusal(status):
    """`chk_inference_interaction_status`'s own terminal set. A status this misses is a wait that
    runs to its timeout with the answer sitting on the wire."""
    wire = _wire(**{f"/v2/inference-interactions/{CHILD_ID}": dict(CHILD, status=status)})
    assert (refusals.stage_refusal(wire, PROJECT, "SOLUTION") or {}).get("status") == status
