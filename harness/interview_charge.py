"""keel-cloud spec 156 (contract 45, `InferenceCharge.VERSION` 12; `ai-credits-design.md`, amendment 2026-10-29): **one
charge per interview, at Begin** -- mirrored for the referee (keel-e2e-eval spec 088). `InferenceCharge.VERSION` is
**13** since keel-cloud 169 (keel-e2e-eval spec 105): `PROBLEM_INTERPRET` 13 -> 26 and `SOLUTION_MECHANISM` 14 -> 28
(the frame class on frontier, Opus 5.5), the New-project gate 273 -> 300; no row this module mirrors moved. **14** since
keel-cloud 170 (keel-e2e-eval spec 110): `RESPONDENT_QUESTIONS` 35 -> 70 (the lock's job on frontier), the lock's gate
70, or 470 with the recording; no row this module mirrors moved. **15** since keel-cloud 190 (keel-e2e-eval spec 121):
the light tier on Claude Haiku 5.5 (routing v16) -- `CONTEXT_INTERPRET` and `ASKED` 3 -> 1, so the New-project gate is
300 -> **298**; INTERPRET's, CONTEXT_INTERPRET's, ASKED's and EXAMPLE_MATCH's measured cost re-based (1.3 times the
tokens at a tenth of Haiku 4.5's rate), their prices otherwise unmoved; no row the interview's charge reads moved.

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

#: keel-cloud `InferenceCharge.VERSION` (the interviewer's fake carries it as `PRICE_VERSION`, and the contacts' fake
#: did until spec 150): 12
#: since spec 156, **13** since keel-cloud 169 (spec 105 FR-2: the two frame prices doubled; INTERVIEW, the readings
#: and every founder-side row unmoved), **14** since keel-cloud 170 (spec 110 FR-1: `RESPONDENT_QUESTIONS` 35 -> 70, the
#: lock's job on the frontier tier, routing v15), **15** since keel-cloud 190 (spec 121 FR-3: `CONTEXT_INTERPRET` and
#: `ASKED` 3 -> 1, the light tier on Haiku 5.5, routing v16). The New-project gate those prices sum to is **298** (1 +
#: 26 + 28 + 3 x 81; 300 at 13 and 14, 273 before), the lock's 70 (470 with the recording).
#: **17** since keel-cloud 250 (spec 154 FR-1): the two gates -- `PROJECT` 1,000 written whole at New project (one SPEND,
#: `project:new`), INTERVIEWER_RECORDING 1,500 once per project at the first kind's set-up (247); every job row priced 0,
#: INTERVIEW among them (**nothing writes it any more**: Begin writes no row, and no link is ever INACTIVE for the balance).
PRICE_VERSION = 17
#: The founder-side rows of `InferenceCharge` at version 15 that `CreditPolicy.NEW_PROJECT_PRICE` sums, and the asked
#: turn: the light tier's two priced rows at 1 credit since keel-cloud 190 (3 at 14 and before), the frame and
#: calibration rows unmoved since 169. Mirrored for the record and pinned against keel-cloud's enum; no walk sums them.
LIGHT_PRICES = {"CONTEXT_INTERPRET": 1, "ASKED": 1}
LIGHT_PRICES_V14 = {"CONTEXT_INTERPRET": 3, "ASKED": 3}
FRAME_PRICES = {"PROBLEM_INTERPRET": 26, "SOLUTION_MECHANISM": 28}
CALIBRATION_QUESTIONS_CREDITS = 81
#: `CreditPolicy.NEW_PROJECT_PRICE`: the context, the problem, the mechanism and three calibrations, summed, never typed.
NEW_PROJECT_PRICE_V15 = (LIGHT_PRICES["CONTEXT_INTERPRET"] + FRAME_PRICES["PROBLEM_INTERPRET"]
                         + FRAME_PRICES["SOLUTION_MECHANISM"] + 3 * CALIBRATION_QUESTIONS_CREDITS)
#: Spec 250 (`InferenceCharge.PROJECT`, `CreditPolicy.PROJECT_PRICE`): the project's own price, 1,000, no longer the
#: corridor's sum (298 at 15); one SPEND row `PROJECT` of -1,000 at New project, reason `project:new`.
PROJECT = "PROJECT"
PROJECT_PRICE = 1000
NEW_PROJECT_PRICE = PROJECT_PRICE
#: keel-cloud 251 (contract 71): the row is written at the project's FIRST LOCK, never at creation, reason `project:lock`;
#: a row written under 250 (at New project) keeps `project:new` and is read as the project's one row too.
PROJECT_REASON = "project:lock"
PROJECT_REASON_250 = "project:new"
#: Spec 250: the grant a Google sign-up writes, sized to the two gates (one project with the interviewer leaves 0).
GRANT_CREDITS = 2500
#: `InferenceCharge.RESPONDENT_QUESTIONS` at version 14 (35 at 13): the lock's one job, and with it
#: `CreditPolicy.LOCK_PRICE`.
RESPONDENT_QUESTIONS_CREDITS = 70
#: `InferenceCharge.INTERVIEW` -- the one row a person's Begin writes ($0.06 basis x 5).
INTERVIEW = "INTERVIEW"
INTERVIEW_CREDITS_V16 = 30
#: Spec 250 (price version 17): the INTERVIEW row is 0 and **never written** -- `written_at_begin()` says so.
INTERVIEW_CREDITS = 0
#: The two readings priced 0 by 156 (10 and 8 at version 11): their HOLD is written at 0 and their SPEND carries the
#: measured cost, so a balance never moves for a reading.
READ_PRICES = {"INTERPRET": 0, "THEMES": 0}
#: ... and what they were at version 11, kept for the record of what moved.
READ_PRICES_V11 = {"INTERPRET": 10, "THEMES": 8}

#: `ai-credits-design.md` §6.3's five-participant row, re-summed at version 12: framing 540 (the six kinds), the brief
#: 105 and the conversation 560 as they were; each person's reading 0 (was 9 in §6.3's table) and each person's Begin 30.
#: Versions 13, 14 and 15 leave it as it is: it is the classic walk's figure (the six framing kinds), recorded and asserted
#: against nothing, 13 moved only the corridor's two frame prices (spec 105 FR-2), 14 only the lock's job (spec 110 FR-1)
#: and 15 only the light tier's two priced rows (spec 121 FR-3).
FRAMING_CREDITS = 540
BRIEF_CREDITS = 105
CONVERSATION_CREDITS = 560
READING_CREDITS_V11 = 9


def written_at_begin(version: int = PRICE_VERSION) -> bool:
    """Whether a person's Begin writes the INTERVIEW row: 12 to 16 yes, 17 (keel-cloud 250) no."""
    return 12 <= version < 17


def project_credits(people: int, *, version: int = PRICE_VERSION) -> int:
    """What §6.3 says a project of `people` participants costs: 1,250 at five on version 11, 1,355 on version 12 and
    on 13, 14 and 15 (which moved no row of this figure); **1,000 flat from 17** (spec 250: the project is bought once,
    and nothing inside it takes credits)."""
    if version >= 17:
        return PROJECT_PRICE
    if version >= 12:
        return FRAMING_CREDITS + BRIEF_CREDITS + CONVERSATION_CREDITS + people * INTERVIEW_CREDITS_V16
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
    -30, `price_credits` 30, `price_version` 15 (14 before keel-cloud 190, 13 before 170, 12 before 169), no job, no cost, `reason` `invitation:<id>`, the key, the project."""
    want = {"kind": INTERVIEW, "action": INTERVIEW, "credits": -INTERVIEW_CREDITS_V16, "price_credits": INTERVIEW_CREDITS_V16,
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
    """FR-2's assertion on one person's Begin: exactly one row under the key, of the shape above -- **at 17 and later,
    none** (spec 250: Begin writes no row), so a row found is the fault."""
    mine = rows_for(ledger, invitation_id)
    if not written_at_begin():
        return [f"{len(mine)} INTERVIEW rows under {key(invitation_id)}: Begin writes none at price version {PRICE_VERSION}"] \
            if mine else []
    if len(mine) != 1:
        return [f"{len(mine)} rows under {key(invitation_id)}, not one"]
    return row_faults(mine[0], invitation_id=invitation_id, project_id=project_id)


def is_charge(row: dict, project_id: str | None = None) -> bool:
    """A Begin's row (any invitation) of this project -- what a leg's *no other row* sweep lets through: kind INTERVIEW
    under an `interview:` key, -30."""
    return (row.get("kind") == INTERVIEW and row.get("action") == INTERVIEW
            and (row.get("idempotency_key") or "").startswith("interview:")
            and int(row.get("credits") or 0) == -INTERVIEW_CREDITS_V16
            and (project_id is None or row.get("project_id") == project_id))


def charges(ledger: list[dict], project_id: str | None = None) -> list[dict]:
    return [x for x in ledger if is_charge(x, project_id)]


# ------------------------------------------------------------------------------------------ FR-3: the inactive link

#: `ParticipantDtos.InactiveResponse` as `InterviewController` serves it (200) on a link opened while the founder's
#: available balance is below `INTERVIEW_CREDITS` and the link was never begun -- the shape of `AlreadyAnswered`.
INACTIVE_STATE = "INACTIVE"
INACTIVE_MESSAGE = "This link is no longer active."
INACTIVE_BODY = {"state": INACTIVE_STATE, "message": INACTIVE_MESSAGE}
#: The highest balance a never-begun link was inactive at (one under an interview) -- until keel-cloud 250: **no link is
#: INACTIVE for the balance any more** (`INACTIVE_RETIRED`); a link is served with the owner at 0.
INACTIVE_BELOW = INTERVIEW_CREDITS_V16
INACTIVE_RETIRED = PRICE_VERSION >= 17


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


# ------------------------------------------------------------------------------- spec 154 (keel-cloud 250): the two gates

def project_key(project_id: str) -> str:
    """`CreditLedgerEntry.projectKey`: one PROJECT row per project, ever."""
    return f"project:{project_id}:spend"


def project_rows(ledger: list[dict], project_id: str | None = None) -> list[dict]:
    """Every `PROJECT` row (any project, or `project_id`'s)."""
    return [x for x in ledger if x.get("action") == PROJECT
            and (project_id is None or x.get("project_id") == project_id)]


def project_row_faults(row: dict, *, project_id: str) -> list[str]:
    """What is wrong with the project's one row against `CreditLedgerEntry.project` (spec 250 FR-1): one SPEND, credits
    -1,000, `price_credits` 1,000, `price_version` 17, no job, reason `project:new`, the key, the project."""
    want = {"kind": "SPEND", "action": PROJECT, "credits": -PROJECT_PRICE, "price_credits": PROJECT_PRICE,
            "price_version": PRICE_VERSION, "inference_job_id": None, "reason": PROJECT_REASON,
            "idempotency_key": project_key(project_id), "project_id": project_id}
    faults = []
    for field, value in want.items():
        got = row.get(field)
        if field in ("credits", "price_credits", "price_version") and got is not None:
            got = int(got)
        if got != value:
            faults.append(f"{field}: {got!r}, not {value!r}")
    return faults


def bought_once(ledger: list[dict], project_id: str) -> list[str]:
    """Spec 250 FR-1: exactly one PROJECT row under the project's key, of the shape above."""
    mine = project_rows(ledger, project_id)
    if len(mine) != 1:
        return [f"{len(mine)} PROJECT rows for {project_id}, not one"]
    return project_row_faults(mine[0], project_id=project_id)


def moves_balance(row: dict) -> bool:
    """Whether a ledger row moves `creditsAvailable` at all: at 17 only PROJECT and INTERVIEWER_RECORDING (and the
    stand-ins / grants / refunds) carry credits; every job row is 0."""
    return int(row.get("credits") or 0) != 0
