"""Reading an inference interaction's own status, for the one scenario that can meet a refusal.

(Not `harness/interactions.py` -- that name is taken by the scoring pipeline's derived
`Interaction`, which is a read of a finished transcript. This is a read of the live wire.)

A scripted executor answers every screen the way the script says, so no deterministic scenario has
ever seen a chain die. A **live** one can: keel-cloud validates what the model wrote against its
own domain rules, and a result that breaks one is refused -- the interaction goes to a terminal
status carrying a `detail` a founder can read and a `diagnostic` naming the rule.

When that happens mid-walk the *screen* the harness is watching simply stops changing: the chat
still says *Connected*, the composer still takes text, and nothing more is ever queued. A wait on
the screen then reports what it honestly saw ("the agent never answered within 240s") and says
nothing about why, which is how a live run spends four minutes and a page of evidence on a
question the wire had already answered (`runs/DRIFT.md` #37).

So this reads the chain the stage is actually on and hands back the refusal, if there is one, in
keel-cloud's own words. It asserts nothing and fixes nothing -- the scenario decides what a
refusal means, and the product repo decides what to do about it.
"""

from __future__ import annotations

from typing import Any, Callable

GetJson = Callable[[str], dict]

#: keel-cloud's own terminal-failure statuses for an interaction (`chk_inference_interaction_status`
#: minus the live ones). `ABANDONED` is here too: a chain nobody will finish is a dead wait for the
#: same reason a refused one is.
TERMINAL_FAILURE_STATUSES = frozenset({
    "RESULT_INVALID", "DOMAIN_REFUSED", "STATE_CONFLICT", "JOB_FAILED", "APPLY_ERROR", "ABANDONED",
})

#: How far a chain is followed. A frame auto-chains to its assumptions and no further today; three
#: is room to spare without ever looping on a cycle the wire should not contain.
MAX_CHAIN_HOPS = 3


def chain_refusal(get_json: GetJson, interaction_id: str) -> dict[str, Any] | None:
    """The first terminally-failed interaction at or after `interaction_id`, or `None`.

    Follows `next_interaction_id`, because **the refusal is usually not the row the screen names**:
    an auto-chained frame stays `ACCEPTED` while its own chained assumptions is the row that was
    refused, and the overview goes on reporting the frame as the stage's pending interaction. That
    is exactly the shape #37 was found in.
    """
    seen: set[str] = set()
    current = interaction_id
    for _ in range(MAX_CHAIN_HOPS):
        if not current or current in seen:
            return None
        seen.add(current)
        body = get_json(f"/v2/inference-interactions/{current}") or {}
        status = body.get("status")
        if status in TERMINAL_FAILURE_STATUSES:
            return {
                "interaction_id": body.get("interaction_id") or current,
                "screen": body.get("screen"),
                "stage": body.get("stage"),
                "status": status,
                # keel-cloud writes both: `detail` is what a founder is meant to read, `diagnostic`
                # names the rule. The referee quotes them; it never composes its own.
                "detail": body.get("detail"),
                "diagnostic": body.get("diagnostic"),
            }
        current = body.get("next_interaction_id")
    return None


def stage_refusal(get_json: GetJson, project_id: str, stage: str) -> dict[str, Any] | None:
    """The refusal on whatever chain `stage` is currently on, read from the overview's own
    `pendingInteraction`, or `None` when the stage has no pending interaction or none has failed."""
    overview = get_json(f"/v2/projects/{project_id}/overview") or {}
    for entry in overview.get("stages") or []:
        if entry.get("type") != stage:
            continue
        pending = entry.get("pendingInteraction") or {}
        interaction_id = pending.get("interactionId")
        if not interaction_id:
            return None
        return chain_refusal(get_json, interaction_id)
    return None


def latest_failure(get_json: GetJson, project_id: str, stage: str) -> dict[str, Any] | None:
    """The most recent terminally-failed interaction on `stage`, found **without a pending one**.

    `stage_refusal` above starts from the overview's `pendingInteraction`, and that is the whole of
    its reach. It is enough for the shape spec 008 met -- a chain refused *while the stage is still
    waiting on it* -- and it is structurally blind to the other shape, which spec 016 met:

        SOLUTION_FRAME  status=JOB_FAILED  job=FAILED
        STAGE SOLUTION  framed=False  pending: None

    A job that fails is terminal, so nothing is pending any more, so the overview names no
    interaction, so `stage_refusal` answers `None` and the scenario reports *"the agent never
    answered within 300s"* about a wire that knew exactly why within seconds. That is the same
    sentence `runs/DRIFT.md` #37 was written about, one status wider.

    So this asks the founder-gated list instead -- `GET /v2/inference-interactions?project_id=` --
    and takes the newest terminal failure whose `stage` matches. keel-cloud's own `refusal` (the
    founder-voiced line, `runs/DRIFT.md` #38) travels with it, because what the *founder* was told
    is often the finding rather than the status code.
    """
    rows = get_json(f"/v2/inference-interactions?project_id={project_id}")
    if not isinstance(rows, list):
        return None
    failed = [row for row in rows
              if row.get("stage") == stage and row.get("status") in TERMINAL_FAILURE_STATUSES]
    if not failed:
        return None
    newest = max(failed, key=lambda row: str(row.get("updated_at") or row.get("created_at") or ""))
    return {
        "interaction_id": newest.get("interaction_id"),
        "screen": newest.get("screen"),
        "stage": newest.get("stage"),
        "status": newest.get("status"),
        "detail": newest.get("detail"),
        "diagnostic": newest.get("diagnostic"),
        # What the founder is actually shown. Quoted, never composed.
        "refusal": newest.get("refusal"),
        "job": (newest.get("job") or {}).get("status"),
    }


def why_the_stage_stopped(get_json: GetJson, project_id: str, stage: str) -> dict[str, Any] | None:
    """Whichever of the two reads finds something: the pending chain first (spec 008's shape),
    then the terminal-failure list (spec 016's). One call for a scenario that only wants to know
    *why nothing happened*, however the wire chose to record it."""
    return (stage_refusal(get_json, project_id, stage)
            or latest_failure(get_json, project_id, stage))


def describe(refusal: dict[str, Any]) -> str:
    """One line for an assertion message, in keel-cloud's words and not the referee's."""
    words = refusal.get("diagnostic") or refusal.get("detail") or ""
    line = (f"{refusal.get('screen')} is {refusal.get('status')} "
            f"({refusal.get('interaction_id')}): {words}")
    # The founder-voiced line, when there is one, because what the founder was told is frequently
    # the finding (`runs/DRIFT.md` #60: an agent that never went away, told it went away).
    if refusal.get("refusal"):
        line += f" -- the founder is shown: {refusal['refusal']!r}"
    return line
