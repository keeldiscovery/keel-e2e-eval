"""Shared setup for S-002 (the pricing pivot) and S-003 (going ahead anyway): both start from the
same shape -- three stages approved, problem+solution supported, the commercial claim's pricing
deal-breaker driven to `CONTRADICTED`, its budget-owner deal-breaker left `SUPPORTED` -- built
here by running the real protocol loop with scenario-specific participants, **never by copying a
database or reusing a project** (design §5, independence pass: "S-002 and S-003 share a setup
shape... but not state"). Each test module calls `rule_out_pricing(...)` on its own fresh
`PricingSetupScenario` subclass and its own project; nothing here is shared state between the two
test runs, only shared code.

## T004 -- the discovered choreography (read from keel-cloud source, never assumed from the plan)

**`frame(...)`'s `carries` mechanic** (`Project.frame`, `Project.java`): a replacement frame on an
*approved, non-PROBLEM* stage supersedes every currently-applying assumption except the ids named
in `carries`; a `CONTRADICTED` assumption may never be carried (A5). A carried assumption keeps its
id, its accumulated evidence and its verdict -- it is the same entity, not a re-introduced copy --
which is exactly what "carries only the budget-owner belief (evidence never spoke against it)"
(design §3) requires: the survivor's *history* must persist, not just its wording.

**Where the ids to carry come from**: `FRAME`'s token grants the `opportunity` context handle
(`HandleGrants.GRANTS`), whose `stages[].beliefs[]` already carries each applying assumption's own
`id` and `verdict` (`ContextHandleService.opportunity`/`BeliefStatus`). A deterministic scenario
(FR-003: no LLM, consult only context) picks `carries` by filtering that list for
`verdict != "CONTRADICTED"` -- never inventing or remembering an id itself.

**Confirmed live (not just read off the source): `reviewRecommendation` never re-opens
decomposition after a carrying reframe.** `NextRecommendation.reviewRecommendation` only
recommends `INTRODUCE_ROLES`/`INTRODUCE_ASSUMPTIONS` when the stage's `applying()` list is *empty*
-- true for a stage's very first framing (nothing carried, nothing added yet), but **false** the
moment a reframe carries even one assumption forward, because that carried assumption is still
`applying()`. A live probe against this stack (drive `rule_out_pricing`, submit the carrying
`FRAME`, call `get_next` once more) confirms it: the very next `get_next` is a `REVIEW`
**handoff** ("waiting for your approval"), never an `INTRODUCE_ASSUMPTIONS` action -- and
approving *that* stage immediately recommends `PROCEED_TO_BRIEF` ("nothing left to settle"),
because the survivor is already `SUPPORTED` and nothing else was ever asked. Since a token is only
ever minted for the action `get_next` itself recommends (`AgentProtocolService.issue`/`submit`;
there is no "give me a token for a different action" call), an agent that carries a survivor
forward has **no protocol-legal path to ever add a new pricing question again** -- the old claim's
dead deal-breaker is not replaced, it simply vanishes. This contradicts journeys.md §1.9's "new
things to be true appear under the new claim, all unanswered" outright: no new things ever appear.
See `runs/DRIFT.md` for the full write-up (`test_s002_pricing_pivot.py` reproduces this every run
and documents it as a blocking finding rather than working around it).

**A load-bearing `CONTRADICTED` verdict pre-empts interpreting anything else on the same stage.**
`Project.needs(stage)` checks `anyContradictedLoadBearing` (-> `REFRAME`) *before* it ever checks
`anyPending` (-> `ANSWERS`) -- so the instant one respondent's interpreted evidence rules a
deal-breaker out, `currentFocus()` jumps to `REFRAME` even if other respondents' answers are still
sitting unread for the very same stage; those pending interpretations become invisible to
`get_next` until the stage is reframed and re-approved. Combined with the verdict rule itself
(`Project.verdictOf`'s split test, `SPLIT_WHEN_MINORITY_IS_AT_LEAST_ONE_IN = 3`, only produces
`MIXED` when the minority side is non-empty -- with zero supporters, *one* dissenting answer
already satisfies "supporters > dissenters" as false, so the verdict is `CONTRADICTED` outright,
not `MIXED`) -- `rule_out_pricing` below settles pricing with **one decisive dissenter** (Dana
Okafor, journeys.md §1.8's own first quote), not the journey's own three: a second or third
commercial invitation sent *after* Dana's answer is interpreted would already find pricing
`CONTRADICTED` and excluded from `linkFor` (`Verdict.isOpen()` is false) -- there is no open
pricing question left to invite anyone else to. One respondent who is decisive keeps the mechanism
legible without asserting anything journeys.md doesn't also say is true: a claim can die on a
single unambiguous "no".

**Two roles, not one, for the commercial stage's two beliefs -- a judgement call this scenario
makes, not a journeys.md requirement.** `Project.invite`/`linkFor` freezes *every* open, applying,
approved-stage assumption for a role into one invitation's `asks` (matching journeys.md §1.4: "a
payroll manager's carries problem, solution and pricing sections") -- so a single role asked about
both budget-owner and pricing would, if a second invitation to that role went unanswered across
the reframe, still ask about the *carried* survivor and leave `Project.needs` stuck at `ANSWERS`
forever afterward, even though `ParticipantController.stale()` already tells that same participant
not to bother (a real inconsistency, confirmed live and recorded in `runs/DRIFT.md`). Splitting
budget-owner (the manager role, `ROLE_LABEL`) from pricing (a dedicated buyer role,
`BUYER_ROLE_LABEL`) keeps a never-opened stale link's fate independent of the survivor's.

**Confirmed live: A9's brief gate is reachable only from an *empty* `currentFocus()`, which a
disproved, unreframed deal-breaker forecloses forever.** `NextRecommendation.compute` recommends
`PROCEED_TO_BRIEF` in exactly one branch, `focus.isEmpty()`, and `currentFocus()` gives a stage
needing `REFRAME` absolute priority over every other need, including no need at all. The very same
live probe above shows `get_next`, called the moment pricing goes `CONTRADICTED`, hands back
*only* the `FRAME`/`REFRAME` action -- never a handoff, never `PROCEED_TO_BRIEF` -- and it stays
that way on every repeated call, because nothing changes what `currentFocus()` computes until the
stage is reframed. There is no protocol call that mints a token for an action other than the one
`get_next` currently recommends, so **an agent that only ever acts on `get_next`'s own
recommendation can never submit `PROCEED_TO_BRIEF` while a load-bearing deal-breaker sits
contradicted on an approved, unreframed stage** -- journeys.md §1.10's entire "going ahead anyway"
conversation (the founder asks for the brief anyway; Keel warns; the founder writes the sentence)
has no protocol-legal entry point. Corroborating evidence: keel-cloud's own
`AgentProtocolFlowTest` (`src/test/java/.../protocol/AgentProtocolFlowTest.java`) tests A9's
refusal-then-accept behaviour at all only by minting the `PROCEED_TO_BRIEF` token directly via a
test-only `mintDirect` helper that bypasses `get_next` entirely -- not a path any real agent or MCP
client has. See `evals/test_s003_going_ahead.py`'s module docstring for how S-003 documents this,
and `runs/DRIFT.md` for the full write-up (this is the eval set's most significant finding).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from evals.scenario import Scenario, find_role
from harness.browser import FounderBrowser, ParticipantBrowser
from harness.driver import FounderAgentDriver

PROBLEM = "PROBLEM"
SOLUTION = "SOLUTION"
COMMERCIAL = "COMMERCIAL"
STAGES = (PROBLEM, SOLUTION, COMMERCIAL)

ROLE_LABEL = "Payroll Ops Manager"
BUYER_ROLE_LABEL = "Budget Sign-off"  # BUYER-type role, asked commercial's pricing question only

# journeys.md §1.7/§1.8's own worked example, attested verbatim -- reused here rather than
# paraphrased, since the whole point of a journey-referenced assertion is to check the product
# against the document's own words wherever the document actually gives one.
PROBLEM_CLAIM = "Payroll managers at mid-size companies lose hours each month chasing payroll exceptions."
PROBLEM_ASSUMPTION = "They handle payroll exceptions themselves, at least monthly."
PROBLEM_ASK = "Tell me about the last time you had to chase down a payroll exception by hand."
PROBLEM_DISCONFIRMING = "Has there been a month where you had no exceptions to chase down at all?"
PROBLEM_PERSON = "Jordan Casey"
PROBLEM_ANSWER = ("Yeah -- just last month I spent about three hours on a Friday afternoon "
                   "manually tracking down four payroll exceptions before I could run final payroll.")

SOLUTION_CLAIM = "An anomaly investigation workflow inside the payroll tool."  # journeys.md §1.10 trio
SOLUTION_ASSUMPTION = ("A tool that automatically flags and routes payroll exceptions would "
                       "actually get used by payroll managers.")
SOLUTION_ASK = "Tell me about the last tool or spreadsheet you tried to use to track payroll exceptions."
SOLUTION_DISCONFIRMING = "Have you tried something like this before and stopped using it?"
SOLUTION_PERSON = "Sam Rivera"
SOLUTION_ANSWER = ("I tried a shared spreadsheet last quarter, but people kept forgetting to "
                    "update it. Something that automatically flagged and routed them would "
                    "definitely get used.")

COMMERCIAL_CLAIM = "$30 a seat per month, billed annually upfront."  # journeys.md §1.8, verbatim
COMMERCIAL_BUDGET_ASSUMPTION = "Someone in the payroll organisation owns a budget for this."
COMMERCIAL_BUDGET_ASK = "Who signs off on a purchase like this on your team?"
COMMERCIAL_BUDGET_DISCONFIRMING = "Has a tool purchase you wanted ever had nobody able to approve it?"
COMMERCIAL_PRICING_ASSUMPTION = "They would pay annually, upfront."  # journeys.md §1.8, verbatim
COMMERCIAL_PRICING_ASK = "Walk me through the last piece of software your team paid for."
COMMERCIAL_PRICING_DISCONFIRMING = "Has your team ever paid for a full year of something upfront?"

BUDGET_PERSON = "Alex Kim"
COMMERCIAL_BUDGET_ANSWER = "I'm the one who signs off on a tool like this for my team."
COMMERCIAL_PERSON = "Dana Okafor"  # journeys.md §1.8's own first respondent
COMMERCIAL_PRICING_ANSWER = "We've never paid a software invoice before the quarter it covers."  # §1.8, verbatim


@dataclass
class RuledOutSetup:
    """What `rule_out_pricing` hands back: the project id, the commercial invitation link that was
    actually answered, an optional never-opened commercial link (S-002 needs one respondent's link
    who never got to answer at all, to test the "opened after the reframe" out-of-date page,
    journeys.md §2.4 -- distinct from `commercial_link`, which S-002 also re-opens to prove an
    *already-answered* participant is never told their work was wasted), and `peek` -- the raw
    `get_next` response observed *after* pricing settled `CONTRADICTED`, read but not acted on, so
    each scenario decides for itself what to do with it (S-002 reframes; S-003 documents whether a
    brief can be reached without reframing)."""

    project_id: str
    commercial_link: str
    unopened_commercial_link: str | None
    peek: dict[str, Any]


class PricingSetupScenario(Scenario):
    """The shared fact content for S-002/S-003 (T004/T005). `build_payload` is overridden, not
    just the hooks below, because the base `Scenario.build_payload`'s FRAME branch has no notion
    of `rationale`/`carries` -- scenario-specific enough (S-002 actually reframes; S-003 never
    does) that only the FRAME branch needs a full override; every other action reuses the base
    dispatch.
    """

    def problem_statement(self) -> str:
        return PROBLEM_CLAIM

    def frame_statement(self, stage: str) -> str:
        return {SOLUTION: SOLUTION_CLAIM, COMMERCIAL: COMMERCIAL_CLAIM}[stage]

    def roles_payload(self) -> list[dict]:
        return [
            {"label": ROLE_LABEL, "roleType": "MANAGER",
             "about": "How payroll runs work at mid-size companies"},
            {"label": BUYER_ROLE_LABEL, "roleType": "BUYER",
             "about": "How budget gets approved for tools on the team"},
        ]

    def assumptions_payload(self, stage: str, roles: list[dict]) -> list[dict]:
        role_id = find_role(roles, ROLE_LABEL)["id"]
        if stage == PROBLEM:
            specs = [(PROBLEM_ASSUMPTION, PROBLEM_ASK, PROBLEM_DISCONFIRMING, role_id)]
        elif stage == SOLUTION:
            specs = [(SOLUTION_ASSUMPTION, SOLUTION_ASK, SOLUTION_DISCONFIRMING, role_id)]
        else:
            buyer_role_id = find_role(roles, BUYER_ROLE_LABEL)["id"]
            # Two DIFFERENT roles, deliberately (a judgement call this scenario makes, not a
            # journeys.md requirement): budget-owner asked of the manager role, pricing asked of a
            # dedicated buyer role, so the two questions travel on two separate invitations rather
            # than sharing one link. A single never-opened link asking about *both* a carried
            # survivor and a soon-superseded belief was found, live, to leave `Project.needs`
            # permanently at `ANSWERS` after the reframe -- its `asks` still intersects the
            # carried, still-applying assumption, so `anyPending` never clears even though
            # `ParticipantController.stale()` already tells that same participant not to bother.
            # Splitting the roles keeps that (real, recorded in runs/DRIFT.md) inconsistency out of
            # this scenario's own critical path while still asserting the out-of-date page on its
            # own terms.
            specs = [
                (COMMERCIAL_BUDGET_ASSUMPTION, COMMERCIAL_BUDGET_ASK, COMMERCIAL_BUDGET_DISCONFIRMING, role_id),
                (COMMERCIAL_PRICING_ASSUMPTION, COMMERCIAL_PRICING_ASK, COMMERCIAL_PRICING_DISCONFIRMING, buyer_role_id),
            ]
        return [{
            "statement": statement, "stage": stage, "risk": "LOAD_BEARING", "askedOf": asked_of,
            "question": {"ask": ask, "probes": [], "disconfirming": disconfirming},
        } for statement, ask, disconfirming, asked_of in specs]

    def about_line(self, stage: str) -> str:
        return {
            PROBLEM: "A few quick questions about how payroll exception handling goes day to day.",
            SOLUTION: "A few quick questions about tools you've tried for tracking payroll exceptions.",
            COMMERCIAL: "A few quick questions about how budget and buying software work on your team.",
        }[stage]

    def person_name(self, stage: str) -> str:
        return {PROBLEM: PROBLEM_PERSON, SOLUTION: SOLUTION_PERSON}[stage]

    def participant_answer(self, stage: str) -> str:
        return {PROBLEM: PROBLEM_ANSWER, SOLUTION: SOLUTION_ANSWER}[stage]

    def interpret_payload(self, stage: str, response: dict) -> list[dict]:
        per_answer = []
        for answer in response["answers"]:
            if not answer.get("text"):
                continue
            if stage == COMMERCIAL and answer["assumptionStatement"] == COMMERCIAL_PRICING_ASSUMPTION:
                stance = "CONTRADICTS"
            else:
                stance = "SUPPORTS"
            per_answer.append({"assumptionId": answer["assumptionId"], "evidence": [{
                "statement": answer["text"], "claimType": "PAST_BEHAVIOR", "stance": stance,
            }]})
        return per_answer

    def build_payload(self, action: str, detail: dict, context: dict[str, Any]) -> dict:
        if action == "FRAME" and detail.get("reason") == "REFRAME":
            return self.reframe_payload(detail["stage"], context)
        return super().build_payload(action, detail, context)

    # ------------------------------------------------------------------- reframe hooks (S-002 only)

    def reframe_payload(self, stage: str, context: dict[str, Any]) -> dict:
        """Reads the `opportunity` handle FRAME's token grants (never remembers an id itself,
        FR-003) to carry forward every currently-applying assumption the evidence never
        contradicted -- design §3's "carries only the budget-owner belief"."""
        card = next(c for c in context["opportunity"]["stages"] if c["stage"] == stage)
        carries = [b["id"] for b in card["beliefs"] if b["verdict"] != "CONTRADICTED"]
        return {
            "stage": stage,
            "statement": self.reframe_statement(stage),
            "rationale": self.reframe_rationale(stage),
            "carries": carries,
        }

    def reframe_statement(self, stage: str) -> str:
        raise NotImplementedError

    def reframe_rationale(self, stage: str) -> str:
        raise NotImplementedError


# --------------------------------------------------------------------------------- orchestration

def _approve_single_participant_stage(driver: FounderAgentDriver, founder: FounderBrowser,
                                       browser, recorder, scenario: PricingSetupScenario,
                                       stage: str) -> None:
    """One REVIEW -> approve -> INVITE -> one supportive respondent -> WAITING -> INTERPRET cycle,
    S-001-shaped. Assumes the driver's next handoff already names `stage`'s REVIEW (the caller has
    driven CREATE and any earlier stage already)."""
    handoff = driver.advance_until_handoff()
    assert handoff and handoff["reason"] == "REVIEW" and handoff["detail"]["stage"] == stage, (stage, handoff)
    founder.open_stage(driver.project_id, stage)
    founder.approve_current_stage(stage)

    handoff = driver.advance_until_handoff()
    assert handoff and handoff["reason"] == "INVITE", (stage, handoff)
    founder.open_invite(driver.project_id)
    person = scenario.person_name(stage)
    link = founder.send_invite(ROLE_LABEL, person, scenario.about_line(stage))

    handoff = driver.advance_until_handoff()
    assert handoff and handoff["reason"] == "WAITING", (stage, handoff)

    participant_context = browser.new_context()
    try:
        page = participant_context.new_page()
        participant = ParticipantBrowser(page, recorder)
        participant.open(link)
        participant.start()
        participant.answer([scenario.participant_answer(stage)])
        participant.submit()
    finally:
        participant_context.close()


def _invite_and_capture_link(driver: FounderAgentDriver, founder: FounderBrowser,
                              role_label: str, person: str, about_line: str) -> str:
    handoff = driver.advance_until_handoff()
    assert handoff and handoff["reason"] == "INVITE", handoff
    founder.open_invite(driver.project_id)
    return founder.send_invite(role_label, person, about_line)


def rule_out_pricing(driver: FounderAgentDriver, founder: FounderBrowser, browser, recorder,
                      scenario: PricingSetupScenario, *,
                      unopened_person: str | None = None) -> RuledOutSetup:
    """Builds "three stages approved, pricing ruled out" on a fresh project via the real loop
    (T005). See this module's docstring for the discovered choreography this follows.

    `unopened_person`, if given, is invited to the buyer role (pricing only) right alongside Dana
    -- while pricing is still open, so their link freezes that question -- but is never opened or
    answered by this function. S-002 uses this to get a link that is provably valid-when-sent and
    never touched, so opening it after the reframe tests journeys.md §2.4's out-of-date page on
    its own terms, distinct from re-opening Dana's already-answered link (which tests the "never
    told their work was wasted" half). Inviting them to the buyer role rather than the manager role
    matters: a link that also asks about the *carried* survivor was found, live, to leave
    `Project.needs` stuck at `ANSWERS` forever after the reframe (see `assumptions_payload`'s own
    docstring) -- pricing-only keeps this scenario's critical path clear of that (separately
    recorded) finding.
    """
    _approve_single_participant_stage(driver, founder, browser, recorder, scenario, PROBLEM)
    _approve_single_participant_stage(driver, founder, browser, recorder, scenario, SOLUTION)

    handoff = driver.advance_until_handoff()
    assert handoff and handoff["reason"] == "REVIEW" and handoff["detail"]["stage"] == COMMERCIAL, handoff
    founder.open_stage(driver.project_id, COMMERCIAL)
    founder.approve_current_stage(COMMERCIAL)

    # Two roles, two invitations -- budget-owner (manager role) first, so its INTERPRET is picked
    # up before pricing's (invitation list order == pendingInterpretation's search order), keeping
    # the budget belief SUPPORTED before pricing's answer ever risks pre-empting it via REFRAME.
    budget_link = _invite_and_capture_link(driver, founder, ROLE_LABEL, BUDGET_PERSON,
                                            scenario.about_line(COMMERCIAL))
    commercial_link = _invite_and_capture_link(driver, founder, BUYER_ROLE_LABEL, COMMERCIAL_PERSON,
                                                scenario.about_line(COMMERCIAL))

    unopened_link = None
    if unopened_person is not None:
        founder.open_invite(driver.project_id)
        unopened_link = founder.send_invite(BUYER_ROLE_LABEL, unopened_person, scenario.about_line(COMMERCIAL))

    handoff = driver.advance_until_handoff()
    assert handoff and handoff["reason"] == "WAITING", handoff

    for link, answer in ((budget_link, COMMERCIAL_BUDGET_ANSWER), (commercial_link, COMMERCIAL_PRICING_ANSWER)):
        participant_context = browser.new_context()
        try:
            page = participant_context.new_page()
            participant = ParticipantBrowser(page, recorder)
            participant.open(link)
            participant.start()
            participant.answer([answer])
            participant.submit()
        finally:
            participant_context.close()

    # Two respondents, two INTERPRETs -- but `advance_until_handoff` would keep going straight
    # into submitting the FRAME/REFRAME action itself (an ActionRec, not a handoff) the instant
    # pricing settles CONTRADICTED, since it chains through every agent-only action. Advance
    # exactly two steps by hand instead (budget's, then pricing's), then peek at (never act on)
    # what comes next, so each scenario decides.
    driver.advance_one()
    driver.advance_one()
    peek = driver.get_next()  # read-only: reports the recommendation, does not act on it

    return RuledOutSetup(project_id=driver.project_id, commercial_link=commercial_link,
                          unopened_commercial_link=unopened_link, peek=peek)
