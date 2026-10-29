"""keel-cloud spec 156 (contract 45, `InferenceCharge.VERSION` 12; `ai-credits-design.md`, amendment 2026-10-29): **one
charge per interview, at Begin** -- mirrored for the referee (keel-e2e-eval spec 088).

One `INTERVIEW` row of 30 credits is written when a person presses Begin (`POST /v2/i/{token}/interview/begin`), once
per invitation (`idempotency_key` `interview:<invitationId>`), never refused and never read against the balance; the
story's reading (`INTERPRET`) and the themes (`THEMES`) are priced 0 from then on (still held, at 0, and settled with
their measured cost). A link opened while the founder's available balance is below 30 is served the INACTIVE body and
nothing else; a link already begun is served whatever the balance. An own-AI founder is never charged and never
inactive.
"""

from __future__ import annotations

# ------------------------------------------------------------------------------------------------ FR-1: the prices

#: keel-cloud `InferenceCharge.VERSION` since spec 156 (the interviewer's and the contacts' fakes carry it as
#: `PRICE_VERSION`).
PRICE_VERSION = 12
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
FRAMING_CREDITS = 540
BRIEF_CREDITS = 105
CONVERSATION_CREDITS = 560
READING_CREDITS_V11 = 9


def project_credits(people: int, *, version: int = PRICE_VERSION) -> int:
    """What §6.3 says a project of `people` participants costs: 1,250 at five on version 11, 1,355 on version 12."""
    if version >= 12:
        return FRAMING_CREDITS + BRIEF_CREDITS + CONVERSATION_CREDITS + people * INTERVIEW_CREDITS
    return FRAMING_CREDITS + BRIEF_CREDITS + CONVERSATION_CREDITS + people * READING_CREDITS_V11


#: The figure the S-012 journey, the `keels-ai` target and the matrix's Keel's-AI cell say a five-participant journey
#: costs.
FIVE_PARTICIPANTS = project_credits(5)
