"""The payroll-exceptions journey's own names, statements, and participants' typed answers (spec
005-connect-stack FR-012/T012), mirrored from keel-runtime's bundled script
(`../keel-runtime/keel_runtime/testing/scripts/payroll-exceptions.json`) -- word for word, since
both fixtures name the same three people and the same claims so the run reads true (spec
judgement call 3): the runtime's own INTERPRET entries decide the verdicts regardless of what a
participant types here (the executor is scripted, not this typed text), but P9 must show a
participant's real words and the participant page must be genuinely exercised, not skipped.

**Discovered while wiring this against the real domain**: keel-cloud's `Invitation.read` (rule
A6) refuses INTERPRET evidence for any assumption a participant's own invitation never carried a
question for -- an invitation's `asks` is frozen, at invite time, to exactly the open beliefs of
the role it was sent to. So Marcus Webb (invited as *someone who runs a payroll team*) can only
ever answer that role's own one belief; he never sees, and never answers, a payroll-manager or
buyer question. A second rule bites the same belief: `Project.introduceAssumptions` (rule A3) only lets a
BUYER, MANAGER or GATEKEEPER role settle a COMMERCIAL assumption -- live-confirmed
(`COMMERCIAL_ASSUMPTIONS` came back `DOMAIN_REFUSED: A3: role 'A payroll manager' is
PRACTITIONER, which cannot settle a COMMERCIAL assumption`, run `20260903T221034Z`). The bundled
script was corrected to match (keel-runtime commits `910a75f` and its follow-up): "They'd pay
annually, upfront" is asked of *someone who runs a payroll team* (a MANAGER -- Marcus), the buyer
role stays introduced per spec FR-003 but uninvited, so its own belief stays honestly untested.
This fixture mirrors that correction rather than the spec prose's literal "three against
annually, upfront": the commercial verdict comes from Marcus's one dissent (0 for / 1 against is
CONTRADICTED under `Project.verdictOf`), and the stage headline is the worst load-bearing
verdict, so the buyer's untested belief never masks it.

`facts()` is the one function `evals/test_s001_smoke.py` calls to build the Fact registry
`harness/scoring.py`'s FID-* checks trace -- a plain function, not a `Scenario` subclass
(`evals/scenario.py` is retired, spec FR-006).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from evals.facts import Fact

PROJECT_NAME = "Payroll Exceptions"

PROBLEM_STATEMENT = (
    "Payroll managers at 200-800-person companies lose a day of two people's time every month "
    "reconciling payroll exceptions that nobody owns until payday forces the question."
)
SOLUTION_STATEMENT = (
    "An exceptions queue inside the payroll tool that assigns every exception an owner the day "
    "it appears."
)
COMMERCIAL_STATEMENT = "$30 a seat per month, billed annually upfront."

# The script's one NEEDS_INPUT entry, first on PROBLEM_FRAME (keel-runtime spec 001 FR-003) --
# the founder answers this before C5 shows the statement above verbatim.
PROBLEM_FOLLOWUP_QUESTION = (
    "When you say chasing exceptions — is the cost the hours, or is it that mistakes get "
    "through to payday?"
)
PROBLEM_FOLLOWUP_ANSWER = "It's the hours -- two people lose most of a day to it every month."

PAYROLL_MANAGER_ROLE = "A payroll manager"
PAYROLL_TEAM_LEAD_ROLE = "Someone who runs a payroll team"
BUYER_ROLE = "Someone who signs off on payroll software spend"

# The belief headings, in the order keel-runtime's bundled script introduces them per stage
# (PROBLEM, then SOLUTION, then COMMERCIAL) -- the same order `Project.invite`/`linkFor` freezes
# them into a role's combined invitation, so this is also the order each of the payroll manager's
# questions should render on the participant page.
PAYROLL_MANAGER_HEADINGS = [
    "They handle exceptions themselves",
    "It costs hours, not minutes",
    "They've tried to fix it",
    "Exceptions have nowhere to live today",
    "Someone would accept being the owner",
]
TEAM_LEAD_HEADINGS = ["Finance isn't already handling it", "They'd pay annually, upfront"]

PROBLEM_BELIEF_HOURS_NOT_MINUTES = "It costs hours, not minutes"
SOLUTION_BELIEF_NOWHERE_TO_LIVE = "Exceptions have nowhere to live today"
COMMERCIAL_BELIEF_ANNUALLY_UPFRONT = "They'd pay annually, upfront"


@dataclass(frozen=True)
class Participant:
    name: str
    role_label: str
    headings: list[str]
    # heading -> the participant's own typed words for it; a heading present in `headings` but
    # absent here is the one question this participant leaves blank (US2 step 6, "skip one
    # question") -- still legal (a blank answer is the same as an absent one).
    answers: dict[str, str] = field(default_factory=dict)

    def answer_texts(self) -> list[str | None]:
        """In `headings` order -- `None` for a skipped question, for
        `harness.browser.ParticipantBrowser.answer`."""
        return [self.answers.get(heading) for heading in self.headings]


# Order matters: the runtime's ScriptedExecutor consumes its INTERPRET entries in this same
# order, one per participant, per process (keel-runtime spec 001 §Edge Cases) -- the smoke must
# invite and interpret them in this order for the verdicts (People disagree / Holding up / Not
# holding up) to land the way keel-runtime's bundled script produces them.
PARTICIPANTS: list[Participant] = [
    Participant(
        name="Dana Okafor", role_label=PAYROLL_MANAGER_ROLE, headings=PAYROLL_MANAGER_HEADINGS,
        answers={
            "They handle exceptions themselves":
                "I'm the one who catches these every pay cycle, not anyone else on my team.",
            "It costs hours, not minutes":
                "Last Tuesday I spent about two hours reconciling against invoices.",
            "They've tried to fix it":
                "I've tried flagging them in a shared spreadsheet before -- nobody else ever "
                "opened it.",
            "Exceptions have nowhere to live today":
                "A shared spreadsheet, if I remember. Usually I don't.",
            "Someone would accept being the owner":
                "When something like this came up before, I ended up handling it without anyone "
                "assigning it to me.",
        },
    ),
    Participant(
        name="Wei Zhang", role_label=PAYROLL_MANAGER_ROLE, headings=PAYROLL_MANAGER_HEADINGS,
        answers={
            "They handle exceptions themselves": "It lands on my desk pretty much every time.",
            "It costs hours, not minutes":
                "We had one last quarter, but our system catches most of it before it costs "
                "anyone real time.",
            # "They've tried to fix it" is left unanswered on purpose (US2 step 6).
            "Exceptions have nowhere to live today":
                "Email, mostly. Whoever spotted it emails whoever they think should fix it.",
            "Someone would accept being the owner":
                "I already end up owning most of these whether the tool assigns them or not.",
        },
    ),
    Participant(
        name="Marcus Webb", role_label=PAYROLL_TEAM_LEAD_ROLE, headings=TEAM_LEAD_HEADINGS,
        answers={
            "Finance isn't already handling it": "If a payroll number looks wrong, it comes to "
                                                  "me, not finance.",
            "They'd pay annually, upfront": "I'd expense it per run without blinking. Upfront, no.",
        },
    ),
]

# spec US2 steps 7/8: the three cards' own headline + counts, once all three participants have
# answered and been read -- keel-cloud's Standing/StageCard reads (FounderDtos.StandingClaim's
# `headline`, FounderDtos.Belief's `countsNote`), derived here from the same evidence above so
# the smoke's assertions and the fixture can never silently drift apart.
PROBLEM_HEADLINE = "People disagree"
PROBLEM_COUNTS_NOTE = "1 described it happening, 1 described it not"
SOLUTION_HEADLINE = "Holding up"
SOLUTION_COUNTS_NOTE = "2 described it happening, nobody described it not"
COMMERCIAL_HEADLINE = "Not holding up"
COMMERCIAL_COUNTS_NOTE = "1 described the opposite, nobody described it"


def facts() -> dict[str, Fact]:
    """The Fact registry this scenario cares about tracing verbatim (data-model.md's "Fact
    registry", spec 005 FR-013) -- checked by harness/rubric.py's FID-* checks against the
    screens (`stage_screen`, `invite_screen`, `brief`) or the participant page
    (`participant_page`) a real value should reach.
    """
    result: dict[str, Fact] = {
        "project_name": Fact(text=PROJECT_NAME, kind="statement", hops=["stage_screen"]),
        "problem_statement": Fact(
            text=PROBLEM_STATEMENT, kind="statement", hops=["stage_screen", "brief"]),
        "solution_statement": Fact(
            text=SOLUTION_STATEMENT, kind="statement", hops=["stage_screen", "brief"]),
        "commercial_statement": Fact(
            text=COMMERCIAL_STATEMENT, kind="statement", hops=["stage_screen", "brief"]),
        "payroll_manager_role": Fact(
            text=PAYROLL_MANAGER_ROLE, kind="role", hops=["invite_screen"]),
        "payroll_team_lead_role": Fact(
            text=PAYROLL_TEAM_LEAD_ROLE, kind="role", hops=["invite_screen"]),
        "buyer_role": Fact(text=BUYER_ROLE, kind="role", hops=["invite_screen"]),
    }
    for participant in PARTICIPANTS:
        slug = participant.name.lower().replace(" ", "_")
        for heading, text in participant.answers.items():
            heading_slug = heading.lower().replace(" ", "_").replace(",", "").replace("'", "")
            result[f"{slug}_{heading_slug}"] = Fact(
                text=text, kind="answer", hops=["participant_page"])
    return result
