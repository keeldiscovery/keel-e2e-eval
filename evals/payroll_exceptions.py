"""The payroll-exceptions journey's own names, statements, and participants' typed answers (spec
005-connect-stack FR-012/T012), mirrored from keel-runtime's bundled script
(`../keel-runtime/keel_runtime/testing/scripts/payroll-exceptions.json`) -- word for word, since
both fixtures name the same three people and the same claims so the run reads true (spec
judgement call 3): the runtime's own INTERPRET entries decide the verdicts regardless of what a
participant types here (the executor is scripted, not this typed text), but P9 must show a
participant's real words and the participant page must be genuinely exercised, not skipped.

`facts()` is the one function `evals/test_s001_smoke.py` calls to build the Fact registry
`harness/scoring.py`'s FID-* checks trace -- a plain function, not a `Scenario` subclass
(`evals/scenario.py` is retired, spec FR-006).
"""

from __future__ import annotations

from dataclasses import dataclass

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

# The three belief headings each participant's evidence actually moves (spec FR-003's edge
# cases), verbatim from the runtime's bundled script.
PROBLEM_BELIEF_HOURS_NOT_MINUTES = "It costs hours, not minutes"
SOLUTION_BELIEF_NOWHERE_TO_LIVE = "Exceptions have nowhere to live today"
COMMERCIAL_BELIEF_ANNUALLY_UPFRONT = "They'd pay annually, upfront"


@dataclass(frozen=True)
class Participant:
    name: str
    role_label: str
    problem_answer: str
    solution_answer: str
    commercial_answer: str
    skips_probe: str  # the one question this participant leaves blank (US2 step 6)


# Order matters: the runtime's ScriptedExecutor consumes its INTERPRET entries in this same
# order, one per participant, per process (keel-runtime spec 001 §Edge Cases) -- the smoke must
# invite and interpret them in this order for the verdicts (People disagree / Holding up / Not
# holding up) to land the way keel-runtime's bundled script produces them.
PARTICIPANTS: list[Participant] = [
    Participant(
        name="Dana Okafor", role_label=PAYROLL_MANAGER_ROLE,
        problem_answer="Last Tuesday I spent about two hours reconciling against invoices.",
        solution_answer="A shared spreadsheet, if I remember. Usually I don't.",
        commercial_answer="We've never paid a software invoice before the quarter it covers.",
        skips_probe="worth-knowing",
    ),
    Participant(
        name="Wei Zhang", role_label=PAYROLL_MANAGER_ROLE,
        problem_answer="Usually 90 minutes, sometimes half a day if the bureau's involved.",
        solution_answer="Email, mostly. Whoever spotted it emails whoever they think should fix it.",
        commercial_answer="Anything annual goes to procurement, and that's a two-month conversation.",
        skips_probe="worth-knowing",
    ),
    Participant(
        name="Marcus Webb", role_label=PAYROLL_TEAM_LEAD_ROLE,
        problem_answer="We had one last quarter, but our system catches most of it now.",
        solution_answer="Post-its. I'm not proud of it.",
        commercial_answer="I'd expense it per run without blinking. Upfront, no.",
        skips_probe="worth-knowing",
    ),
]

# spec US2 steps 7/8: the three cards' own headline + counts, once all three participants have
# answered and been read -- keel-cloud's Standing/StageCard reads (FounderDtos.StandingClaim's
# `headline`, FounderDtos.Belief's `countsNote`), derived here from the same evidence above so
# the smoke's assertions and the fixture can never silently drift apart.
PROBLEM_HEADLINE = "People disagree"
PROBLEM_COUNTS_NOTE = "2 described it happening, 1 described it not"
SOLUTION_HEADLINE = "Holding up"
SOLUTION_COUNTS_NOTE = "3 described it happening, nobody described it not"
COMMERCIAL_HEADLINE = "Not holding up"
COMMERCIAL_COUNTS_NOTE = "3 described the opposite, nobody described it"


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
        result[f"{slug}_problem_answer"] = Fact(
            text=participant.problem_answer, kind="answer", hops=["participant_page"])
        result[f"{slug}_solution_answer"] = Fact(
            text=participant.solution_answer, kind="answer", hops=["participant_page"])
        result[f"{slug}_commercial_answer"] = Fact(
            text=participant.commercial_answer, kind="answer", hops=["participant_page"])
    return result
