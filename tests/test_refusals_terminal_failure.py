"""`harness/refusals.py` can see a job that failed, not only a chain that was refused
(spec `016-copilot-e2e`).

**The blind spot this closes.** `stage_refusal` starts from the overview's own
`pendingInteraction` and that is the whole of its reach. It answers spec 008's question -- *this
stage is still waiting on a chain, and the chain was refused* -- and it is structurally unable to
answer spec 016's, because a **failed job is terminal**: nothing is pending any more, the overview
names no interaction, and the read comes back `None`.

Live-confirmed, `runs/20260910T205507Z-s012-copilot-host-and-thinker-live`:

    SOLUTION_FRAME  status=JOB_FAILED  job=FAILED
    STAGE SOLUTION  framed=False  pending: None

The scenario reported *"the agent never answered within 300.0s"* about a wire that had known
exactly why within seconds -- the same sentence `runs/DRIFT.md` #37 exists about, one status wider.
S-004 has the identical blind spot and this fixes it for both.
"""

from __future__ import annotations

from harness import refusals

PROJECT = "p-1"

FAILED_ROW = {
    "interaction_id": "i-solution-frame",
    "screen": "SOLUTION_FRAME",
    "stage": "SOLUTION",
    "status": "JOB_FAILED",
    "detail": "Your agent went away before it answered.",
    "diagnostic": None,
    "refusal": "Your agent went away before it answered, so nothing was saved.",
    "job": {"status": "FAILED"},
    "updated_at": "2026-09-10T21:02:00Z",
}
APPLIED_ROW = {
    "interaction_id": "i-problem-frame", "screen": "PROBLEM_FRAME", "stage": "PROBLEM",
    "status": "APPLIED", "job": {"status": "COMPLETED"}, "updated_at": "2026-09-10T21:00:00Z",
}


def _wire(rows, *, pending=None):
    def get_json(path: str):
        if path.startswith("/v2/inference-interactions?project_id="):
            return rows
        if path.endswith("/overview"):
            return {"stages": [{"type": "SOLUTION", "pendingInteraction": pending}]}
        return {}
    return get_json


def test_a_failed_job_is_found_even_though_nothing_is_pending():
    found = refusals.latest_failure(_wire([FAILED_ROW, APPLIED_ROW]), PROJECT, "SOLUTION")
    assert found is not None
    assert found["status"] == "JOB_FAILED"
    assert found["screen"] == "SOLUTION_FRAME"
    assert found["job"] == "FAILED"


def test_the_founder_voiced_line_travels_with_it():
    """What the founder was told is frequently the finding rather than the status code
    (`runs/DRIFT.md` #60: an agent that never went away, told that it went away)."""
    found = refusals.latest_failure(_wire([FAILED_ROW]), PROJECT, "SOLUTION")
    assert found["refusal"] == FAILED_ROW["refusal"]
    assert FAILED_ROW["refusal"] in refusals.describe(found)


def test_another_stages_failure_is_not_this_stages():
    other = {**FAILED_ROW, "stage": "COMMERCIAL"}
    assert refusals.latest_failure(_wire([other]), PROJECT, "SOLUTION") is None


def test_a_healthy_stage_has_nothing_to_report():
    assert refusals.latest_failure(_wire([APPLIED_ROW]), PROJECT, "PROBLEM") is None
    assert refusals.latest_failure(_wire([]), PROJECT, "SOLUTION") is None
    assert refusals.latest_failure(_wire({"not": "a list"}), PROJECT, "SOLUTION") is None


def test_the_newest_failure_wins():
    older = {**FAILED_ROW, "interaction_id": "i-old", "updated_at": "2026-09-10T20:00:00Z"}
    found = refusals.latest_failure(_wire([FAILED_ROW, older]), PROJECT, "SOLUTION")
    assert found["interaction_id"] == "i-solution-frame"


def test_the_one_call_prefers_the_pending_chain_and_falls_back_to_the_list():
    """`why_the_stage_stopped` keeps spec 008's read first -- a chain the stage is *still* waiting
    on is the more precise answer -- and only then asks the list."""
    pending = {"interactionId": "i-pending"}

    def get_json(path: str):
        if path.endswith("/overview"):
            return {"stages": [{"type": "SOLUTION", "pendingInteraction": pending}]}
        if path.startswith("/v2/inference-interactions/i-pending"):
            return {"interaction_id": "i-pending", "screen": "SOLUTION_ASSUMPTIONS",
                    "stage": "SOLUTION", "status": "DOMAIN_REFUSED", "diagnostic": "Q4"}
        if path.startswith("/v2/inference-interactions?project_id="):
            return [FAILED_ROW]
        return {}

    assert refusals.why_the_stage_stopped(get_json, PROJECT, "SOLUTION")["status"] == \
        "DOMAIN_REFUSED"
    assert refusals.why_the_stage_stopped(
        _wire([FAILED_ROW]), PROJECT, "SOLUTION")["status"] == "JOB_FAILED"
