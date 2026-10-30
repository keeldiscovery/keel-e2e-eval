"""keel-cloud spec 156 (contract 45, `InferenceCharge.VERSION` 12; `ai-credits-design.md`, amendment 2026-10-29): **one
charge per interview, at Begin** -- mirrored for the referee (keel-e2e-eval spec 088). `InferenceCharge.VERSION` is
**13** since keel-cloud 169 (keel-e2e-eval spec 105): `PROBLEM_INTERPRET` 13 -> 26 and `SOLUTION_MECHANISM` 14 -> 28
(the frame class on frontier, Opus 5.5), the New-project gate 273 -> 300; no row this module mirrors moved.

One `INTERVIEW` row of 30 credits is written when a person presses Begin (`POST /v2/i/{token}/interview/begin`), once
per invitation (`idempotency_key` `interview:<invitationId>`), never refused and never read against the balance; the
story's reading (`INTERPRET`) and the themes (`THEMES`) are priced 0 from then on (still held, at 0, and settled with
their measured cost). A link opened while the founder's available balance is below 30 is served the INACTIVE body and
nothing else; a link already begun is served whatever the balance. An own-AI founder is never charged and never
inactive.
"""

from __future__ import annotations

import os

# ------------------------------------------------------------------------------------------------ FR-1: the prices

#: keel-cloud `InferenceCharge.VERSION` (the interviewer's and the contacts' fakes carry it as `PRICE_VERSION`): 12
#: since spec 156, **13** since keel-cloud 169 (spec 105 FR-2: the two frame prices doubled; INTERVIEW, the readings
#: and every founder-side row unmoved). No corridor sum is mirrored here; the gate those prices sum to is 300
#: (3 + 26 + 28 + 3 x 81).
PRICE_VERSION = 13
#: `InferenceCharge.INTERVIEW` -- the one row a person's Begin writes ($0.06 basis x 5).
INTERVIEW = "INTERVIEW"
INTERVIEW_CREDITS = 30
#: The two readings priced 0 by 156 (10 and 8 at version 11): their HOLD is written at 0 and their SPEND carries the
#: measured cost, so a balance never moves for a reading.
READ_PRICES = {"INTERPRET": 0, "THEMES": 0}
#: ... and what they were at version 11, kept for the record of what moved.
READ_PRICES_V11 = {"INTERPRET": 10, "THEMES": 8}

#: `ai-credits-design.md` §6.3's five-participant row, re-summed at version 12: framing 540 (the six kinds), the brief
#: 105 and the conversation 560 as they were; each person's reading 0 (was 9 in §6.3's table) and each person's Begin 30.
#: Version 13 leaves it as it is: it is the classic walk's figure (the six framing kinds), recorded and asserted against
#: nothing, and 13 moved only the corridor's two frame prices (spec 105 FR-2).
FRAMING_CREDITS = 540
BRIEF_CREDITS = 105
CONVERSATION_CREDITS = 560
READING_CREDITS_V11 = 9


def project_credits(people: int, *, version: int = PRICE_VERSION) -> int:
    """What §6.3 says a project of `people` participants costs: 1,250 at five on version 11, 1,355 on version 12 and
    on 13 (which moved no row of this figure)."""
    if version >= 12:
        return FRAMING_CREDITS + BRIEF_CREDITS + CONVERSATION_CREDITS + people * INTERVIEW_CREDITS
    return FRAMING_CREDITS + BRIEF_CREDITS + CONVERSATION_CREDITS + people * READING_CREDITS_V11


#: The figure the S-012 journey, the `keels-ai` target and the matrix's Keel's-AI cell say a five-participant journey
#: costs.
FIVE_PARTICIPANTS = project_credits(5)


# ------------------------------------------------------------------------------------------- FR-2: Begin on the wire

#: `InterviewController.begin` (contract 45, `beginInterview`): no body; 204 on any open link, the first time charged and
#: every later time nothing; an answered link the AlreadyAnswered body (200); an unknown token the bare 404.
BEGIN_PATH = "/interview/begin"
BEGIN_STATUS = 204

#: keel-web 131 posts Begin from the intro's button and draws the inactive page. Until it merges, every assertion that
#: needs the browser to post Begin, or the page to draw the inactive line, is recorded as skipped with this reason and
#: asserts only what holds either way; the coordinator turns them on by setting `WEB_131_BUILT = True` here (or
#: `KEEL_WEB_131=1` in the environment for one run against a 131 build).
WEB_131_PENDING = "keel-web 131 not yet built"
WEB_131_BUILT = True  # keel-web 131 merged 2026-10-29, web master 58ba87f


def web_131_built() -> bool:
    return WEB_131_BUILT or os.environ.get("KEEL_WEB_131") == "1"


def key(invitation_id: str) -> str:
    """`CreditLedgerEntry.interviewKey`: the one key a person's Begin writes under -- the UNIQUE index that makes a
    second Begin nothing."""
    return f"interview:{invitation_id}"


def rows_for(ledger: list[dict], invitation_id: str) -> list[dict]:
    """Every ledger row written under one invitation's Begin key (one at most, by the UNIQUE index)."""
    return [x for x in ledger if x.get("idempotency_key") == key(invitation_id)]


def row_faults(row: dict, *, invitation_id: str, project_id: str | None = None) -> list[str]:
    """What is wrong with one Begin's row against `CreditLedgerEntry.interview`: kind and action `INTERVIEW`, credits
    -30, `price_credits` 30, `price_version` 13 (12 before keel-cloud 169), no job, no cost, `reason` `invitation:<id>`, the key, the project."""
    want = {"kind": INTERVIEW, "action": INTERVIEW, "credits": -INTERVIEW_CREDITS, "price_credits": INTERVIEW_CREDITS,
            "price_version": PRICE_VERSION, "inference_job_id": None, "actual_cost_micro_usd": None,
            "reason": f"invitation:{invitation_id}", "idempotency_key": key(invitation_id)}
    if project_id is not None:
        want["project_id"] = project_id
    faults = []
    for field, value in want.items():
        got = row.get(field)
        if field in ("credits", "price_credits", "price_version") and got is not None:
            got = int(got)
        if got != value:
            faults.append(f"{field}: {got!r}, not {value!r}")
    return faults


def charged_once(ledger: list[dict], invitation_id: str, project_id: str | None = None) -> list[str]:
    """FR-2's assertion on one person's Begin: exactly one row under the key, of the shape above."""
    mine = rows_for(ledger, invitation_id)
    if len(mine) != 1:
        return [f"{len(mine)} rows under {key(invitation_id)}, not one"]
    return row_faults(mine[0], invitation_id=invitation_id, project_id=project_id)


def is_charge(row: dict, project_id: str | None = None) -> bool:
    """A Begin's row (any invitation) of this project -- what a leg's *no other row* sweep lets through: kind INTERVIEW
    under an `interview:` key, -30."""
    return (row.get("kind") == INTERVIEW and row.get("action") == INTERVIEW
            and (row.get("idempotency_key") or "").startswith("interview:")
            and int(row.get("credits") or 0) == -INTERVIEW_CREDITS
            and (project_id is None or row.get("project_id") == project_id))


def charges(ledger: list[dict], project_id: str | None = None) -> list[dict]:
    return [x for x in ledger if is_charge(x, project_id)]


# ------------------------------------------------------------------------------------------ FR-3: the inactive link

#: `ParticipantDtos.InactiveResponse` as `InterviewController` serves it (200) on a link opened while the founder's
#: available balance is below `INTERVIEW_CREDITS` and the link was never begun -- the shape of `AlreadyAnswered`.
INACTIVE_STATE = "INACTIVE"
INACTIVE_MESSAGE = "This link is no longer active."
INACTIVE_BODY = {"state": INACTIVE_STATE, "message": INACTIVE_MESSAGE}
#: The highest balance a never-begun link is inactive at (one under an interview).
INACTIVE_BELOW = INTERVIEW_CREDITS


def inactive_faults(status: int, body) -> list[str]:
    """What is wrong with a served link that should read inactive: 200, the body exactly `INACTIVE_BODY`, and nothing
    in it a stranger could read as money -- no digit, no *credit*."""
    faults = []
    if status != 200:
        faults.append(f"status {status}, not 200")
    if body != INACTIVE_BODY:
        faults.append(f"body {body!r}, not {INACTIVE_BODY!r}")
    words = " ".join(str(v) for v in (body or {}).values()) if isinstance(body, dict) else str(body)
    if any(c.isdigit() for c in words) or "credit" in words.lower():
        faults.append(f"a number or the word credits in {words!r}")
    return faults


#: `Interview.state` on a served interview (contract 45: `enum [OPEN]`); the notices carry INACTIVE / ALREADY_ANSWERED.
OPEN = "OPEN"


def served(status: int, body) -> bool:
    """The interview itself, not a notice: 200, `state` OPEN, and its parts."""
    return status == 200 and isinstance(body, dict) and body.get("state") == OPEN and bool(body.get("parts"))


def page_faults(text: str | None) -> list[str]:
    """keel-web 131's inactive page: the one line, *This link is no longer active.*, and no number, no *credits*."""
    text = (text or "").strip()
    faults = []
    if INACTIVE_MESSAGE not in text:
        faults.append(f"the line {INACTIVE_MESSAGE!r} is not on the page: {text[:200]!r}")
    if any(c.isdigit() for c in text) or "credit" in text.lower():
        faults.append(f"a number or the word credits on the page: {text[:200]!r}")
    return faults
