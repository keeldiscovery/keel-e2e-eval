"""Shared setup for S-002 (the pricing pivot) and S-003 (going ahead anyway): both start from the
same shape -- three stages approved, problem+solution supported, the commercial claim's pricing
deal-breaker driven to `CONTRADICTED`, its budget-owner deal-breaker left `SUPPORTED` -- built
here by running the real protocol loop with scenario-specific participants, **never by copying a
database or reusing a project** (design §5, independence pass: "S-002 and S-003 share a setup
shape... but not state"). Each test module calls `rule_out_pricing(...)` on its own fresh
`PricingSetupScenario` subclass and its own project; nothing here is shared state between the two
test runs, only shared code.

**Update, 2026-08-30 (keel-cloud commit c63ad4a, DRIFT #5/#6/#7 resolved)**: the choreography
findings below (T004) are kept verbatim, as the historical record of what this module's own live
probes found before the fix -- this docstring is not rewritten to erase them, the way `runs/
DRIFT.md` appends RESOLVED notes rather than striking its own findings. What actually changed: a
carrying `FRAME` reframe now reopens decomposition (`Stage.decomposedForActiveFrame`), so
`test_s002_pricing_pivot.py` walks the real `INTRODUCE_ASSUMPTIONS` cycle the second finding below
says never happened; and `get_next` now accepts `request="brief"` (harness/driver.py), so
`test_s003_going_ahead.py` walks the real A9 conversation the fourth finding below says had no
entry point. `rule_out_pricing` itself is unchanged in *purpose* -- it only ever built the
*starting* state ("pricing ruled out, budget-owner supported, commercial approved") both journeys
open from -- but its *choreography* is rewritten again below (founder-experience design §6, keel-
cloud commits 8b13d04/ff1ed48): see "Update, 2026-08-30 (the invite gate)" further down.

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

## Update, 2026-08-30 (the invite gate; keel-cloud commits 8b13d04/ff1ed48)

`Project.needs` now gates `INVITE`/`EVIDENCE` on `allFramedStagesApproved()` (founder-experience
design §6, journeys.md §1.4): nothing invites until every framed stage is approved. `invite()`
itself refuses the same way (ff1ed48: "the invite gate applies to the act, not just the advice").
Two consequences this module's own choreography now has to live inside, discovered live against
this stack:

1. **Approve-all-then-invite, not per-stage interleave.** `advance_to_all_stages_approved` (below)
   replaces this module's old `_approve_single_participant_stage` entirely: it drives CREATE
   through approving COMMERCIAL, one `REVIEW` handoff at a time, with **no invitation sent until
   all three are approved** -- the standing assertion `assert_invite_gate_closed` runs after each
   of the first two approvals to pin exactly that.
2. **One role, one combined invitation.** `ROLE_LABEL` is `askedOf` for the problem belief, the
   solution belief, *and* the commercial budget-owner belief. `Project.invite`/`linkFor` freezes
   *every* open, applying, approved-stage assumption for a role into the *first* invitation sent to
   that role -- so the moment the gate opens, inviting `ROLE_LABEL` once already asks about all
   three cards in one sitting (design §5's own mockup: "A PAYROLL MANAGER... can settle 4 beliefs
   across 2 cards"). There is no longer a protocol-legal way to keep problem/solution/budget on
   three separate invitations to the same role once every stage is approved before any of them is
   sent -- `COMBINED_PERSON` answers all three in one interview, and the resulting `INTERPRET`
   settles all three beliefs in one commit. Pricing stays on its own dedicated `BUYER_ROLE_LABEL`
   invitation (`COMMERCIAL_PERSON`), unaffected by this -- see the two-roles judgement call above,
   which this gate change does not disturb.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from evals.scenario import Scenario, find_role
from harness.bridge import BridgeLoop, BridgeReply
from harness.browser import ChatPane, FounderBrowser, ParticipantBrowser
from harness.driver import FounderAgentDriver
from harness.relay import AgentRelay, FounderRelay
from stack.auth import FounderCredentials
from stack.config import StackConfig

_URL_RE = re.compile(r"https?://\S+")

PROBLEM = "PROBLEM"
SOLUTION = "SOLUTION"
COMMERCIAL = "COMMERCIAL"
STAGES = (PROBLEM, SOLUTION, COMMERCIAL)

# founder-experience design §3: CREATE now requires a founder-given project name, distinct from
# the claim itself.
PROJECT_NAME = "Payroll Exception Radar"

ROLE_LABEL = "Payroll Ops Manager"
BUYER_ROLE_LABEL = "Budget Sign-off"  # BUYER-type role, asked commercial's pricing question only

# journeys.md §1.7/§1.8's own worked example, attested verbatim -- reused here rather than
# paraphrased, since the whole point of a journey-referenced assertion is to check the product
# against the document's own words wherever the document actually gives one.
PROBLEM_CLAIM = "Payroll managers at mid-size companies lose hours each month chasing payroll exceptions."
PROBLEM_ASSUMPTION = "They handle payroll exceptions themselves, at least monthly."
PROBLEM_HEADING = "Manual exception chasing"  # founder-experience design §7: a name, not a restatement
PROBLEM_ASK = "Tell me about the last time you had to chase down a payroll exception by hand."
PROBLEM_DISCONFIRMING = "Has there been a month where you had no exceptions to chase down at all?"
PROBLEM_ANSWER = ("Yeah -- just last month I spent about three hours on a Friday afternoon "
                   "manually tracking down four payroll exceptions before I could run final payroll.")

SOLUTION_CLAIM = "An anomaly investigation workflow inside the payroll tool."  # journeys.md §1.10 trio
SOLUTION_ASSUMPTION = ("A tool that automatically flags and routes payroll exceptions would "
                       "actually get used by payroll managers.")
SOLUTION_HEADING = "Automated flagging gets used"
SOLUTION_ASK = "Tell me about the last tool or spreadsheet you tried to use to track payroll exceptions."
SOLUTION_DISCONFIRMING = "Have you tried something like this before and stopped using it?"
SOLUTION_ANSWER = ("I tried a shared spreadsheet last quarter, but people kept forgetting to "
                    "update it. Something that automatically flagged and routed them would "
                    "definitely get used.")

COMMERCIAL_CLAIM = "$30 a seat per month, billed annually upfront."  # journeys.md §1.8, verbatim
COMMERCIAL_BUDGET_ASSUMPTION = "Someone in the payroll organisation owns a budget for this."
COMMERCIAL_BUDGET_HEADING = "Someone owns the budget"
COMMERCIAL_BUDGET_ASK = "Who signs off on a purchase like this on your team?"
COMMERCIAL_BUDGET_DISCONFIRMING = "Has a tool purchase you wanted ever had nobody able to approve it?"
COMMERCIAL_PRICING_ASSUMPTION = "They would pay annually, upfront."  # journeys.md §1.8, verbatim
COMMERCIAL_PRICING_HEADING = "Pays annually, upfront"
COMMERCIAL_PRICING_ASK = "Walk me through the last piece of software your team paid for."
COMMERCIAL_PRICING_DISCONFIRMING = "Has your team ever paid for a full year of something upfront?"

# The invite gate (module docstring, "Update, 2026-08-30"): one combined respondent for
# problem+solution+budget -- the first (and only, in this scenario) invitation ROLE_LABEL ever
# gets, once the gate opens, already carries all three.
COMBINED_PERSON = "Jordan Casey"
COMBINED_ABOUT_LINE = ("A few quick questions about payroll exception handling, the tools you've "
                        "tried, and how budget gets approved on your team.")
COMMERCIAL_BUDGET_ANSWER = "I'm the one who signs off on a tool like this for my team."

COMMERCIAL_PERSON = "Dana Okafor"  # journeys.md §1.8's own first respondent -- pricing only
COMMERCIAL_PRICING_ANSWER = "We've never paid a software invoice before the quarter it covers."  # §1.8, verbatim


@dataclass
class RuledOutSetup:
    """What `rule_out_pricing` hands back: the project id, the combined problem/solution/budget
    invitation link (answered), the commercial pricing invitation link that was actually answered,
    an optional never-opened pricing link (S-002 needs one respondent's link who never got to
    answer at all, to test the "opened after the reframe" out-of-date page, journeys.md §2.4 --
    distinct from `commercial_link`, which S-002 also re-opens to prove an *already-answered*
    participant is never told their work was wasted), and `peek` -- the raw `get_next` response
    observed *after* pricing settled `CONTRADICTED`, read but not acted on, so each scenario
    decides for itself what to do with it (S-002 reframes; S-003 documents whether a brief can be
    reached without reframing)."""

    project_id: str
    combined_link: str
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

    def project_name(self) -> str:
        return PROJECT_NAME

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
            specs = [(PROBLEM_ASSUMPTION, PROBLEM_HEADING, PROBLEM_ASK, PROBLEM_DISCONFIRMING, role_id)]
        elif stage == SOLUTION:
            specs = [(SOLUTION_ASSUMPTION, SOLUTION_HEADING, SOLUTION_ASK, SOLUTION_DISCONFIRMING, role_id)]
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
                (COMMERCIAL_BUDGET_ASSUMPTION, COMMERCIAL_BUDGET_HEADING, COMMERCIAL_BUDGET_ASK,
                 COMMERCIAL_BUDGET_DISCONFIRMING, role_id),
                (COMMERCIAL_PRICING_ASSUMPTION, COMMERCIAL_PRICING_HEADING, COMMERCIAL_PRICING_ASK,
                 COMMERCIAL_PRICING_DISCONFIRMING, buyer_role_id),
            ]
        return [{
            "statement": statement, "heading": heading, "stage": stage, "risk": "LOAD_BEARING",
            "askedOf": asked_of, "question": {"ask": ask, "probes": [], "disconfirming": disconfirming},
        } for statement, heading, ask, disconfirming, asked_of in specs]

    def about_line(self, stage: str) -> str:
        return {
            PROBLEM: "A few quick questions about how payroll exception handling goes day to day.",
            SOLUTION: "A few quick questions about tools you've tried for tracking payroll exceptions.",
            COMMERCIAL: "A few quick questions about how budget and buying software work on your team.",
        }[stage]

    def about_line_combined(self) -> str:
        """The invite gate (module docstring): one combined invitation now carries problem,
        solution and commercial-budget together, so it needs one about-line covering all three,
        not any single stage's own."""
        return COMBINED_ABOUT_LINE

    def person_name(self, stage: str) -> str:
        return COMBINED_PERSON

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


# ------------------------------------------------------------------- round 2: auth + arrival (T0)

def open_founder_session(stack: StackConfig, founder_credentials: FounderCredentials, recorder,
                          scenario: Scenario, browser) -> tuple[FounderAgentDriver, FounderBrowser, Any]:
    """Founder-experience round 2: every scenario's founder now needs both credentials the design
    introduced -- the agent key (`X-Keel-Agent-Key`, gating `/v2/agent/**` and `/mcp`) for the
    driver, and a real browser session (driving the actual `/login` screen once, never a
    transplanted cookie -- `harness/browser.py.FounderBrowser.log_in`'s own judgement call) for the
    founder's Playwright context. Centralized here so a new scenario gets both by construction
    rather than re-deriving the choreography; returns `(driver, founder, founder_context)` -- the
    caller still owns closing `founder_context` in its own `finally` block, exactly as before.
    """
    cloud_base = f"http://localhost:{stack.cloud_port}"
    web_root_base = f"http://localhost:{stack.web_port}"
    founder_web_base = f"{web_root_base}/p"

    driver = FounderAgentDriver(cloud_base, recorder, scenario, agent_key=founder_credentials.agent_key)
    driver.log_in(founder_credentials.email, founder_credentials.password)

    founder_context = browser.new_context()
    founder_page = founder_context.new_page()
    founder = FounderBrowser(founder_page, founder_web_base, recorder, get_state=driver.get_state)
    founder.log_in(web_root_base, founder_credentials.email, founder_credentials.password)
    return driver, founder, founder_context


# ------------------------------------------------------------------------ relay re-venue (§12.2)

def open_relay(driver: FounderAgentDriver, project_id: str) -> tuple[FounderRelay, AgentRelay]:
    """Both relay halves (design §12 item 1), riding the SAME session `open_founder_session`
    already built (its founder cookie and agent-key header both already set) -- this harness plays
    both parties of the conversation, exactly as `FounderAgentDriver` already plays founder-
    session reads alongside its own agent-key writes.

    Cached on `driver` itself (`driver.founder_relay`/`driver.agent_relay`), not returned fresh
    every call: `AgentRelay.lease` is a bearer token minted on first contact and re-presented on
    every later call -- constructing a second, lease-ignorant `AgentRelay` for the same project
    while the first one's lease is still live would itself trip the very refusal S-011 exists to
    prove, for the wrong reason (a harness bug, not a genuine competing bridge).
    """
    cached = getattr(driver, "agent_relay", None)
    if cached is not None and cached.project_id == project_id:
        return driver.founder_relay, driver.agent_relay
    founder_relay = FounderRelay(driver.base_url, driver.session, project_id, driver.recorder)
    agent_relay = AgentRelay(driver.base_url, driver.session, project_id, driver.recorder)
    driver.founder_relay = founder_relay
    driver.agent_relay = agent_relay
    return founder_relay, agent_relay


def relay_round_trip(founder_relay: FounderRelay, agent_relay: AgentRelay, founder_text: str,
                      reply: BridgeReply | list[BridgeReply]) -> None:
    """The founder-reply pattern (design §12 item 2): the founder's line posts through the relay,
    then one mechanical bridge cycle answers with a SCRIPTED reply -- `reasoning` here is the
    caller's own canned `reply`, never an LLM (FR-003's "no LLM anywhere" rule extends to the
    relay), the same discipline `evals.scenario.Scenario.build_payload` already lives by for the
    protocol side. One `step()` is enough: both turns already exist in the store by the time the
    single mechanical poll runs, so there is nothing to actually wait on.

    **Bug found and fixed live (2026-08-31, S-001's own guided-walk re-choreography)**: this used
    to construct a brand-new `BridgeLoop(agent_relay, ...)` on every call -- `BridgeLoop.__init__`
    starts its OWN `cursor` at 0, ignoring `agent_relay`'s own already-advanced one, so a second (or
    third) call in the same scenario re-polled from the very beginning of the conversation, found
    EVERY prior founder turn "unanswered" again (including ones an earlier round trip already
    replied to), and posted the same canned `reply` once per stale turn -- silent duplicate agent
    turns a caller's own loose assertions (`len(rows) >= 2`, an index-order check) never happened to
    notice, until a stricter one did. Seeding the loop's cursor from `agent_relay.cursor` (updated
    as a side effect of every real poll, `harness.relay.AgentRelay.poll`) makes each call see only
    the turn(s) actually new since the last one -- the invariant this function's own one-turn-in,
    one-reply-out contract already assumed.
    """
    founder_relay.post_turn(founder_text)
    loop = BridgeLoop(agent_relay, reasoning=lambda _text: reply)
    loop.cursor = agent_relay.cursor
    loop.step()


def arrive_and_create(driver: FounderAgentDriver, founder: FounderBrowser, scenario: Scenario) -> str:
    """The shared opening step every scenario now takes (founder-experience round 2 design §2,
    task item 2's "a new shared opening step"): the arrival read, greeting first -- then `CREATE`,
    with its own completed display (name, next step, the overview link) proven live the same way
    `test_s001_smoke.py` already proves PROBLEM's `INTRODUCE_ASSUMPTIONS` door -- and, finally, a
    second arrival read proving the founder's own project list grew by exactly this fresh project,
    newest-first and flagged `latest`. Self-contained (never depends on how many other scenarios
    ran earlier in the same `pytest evals` session, even though the founder account -- and
    therefore its project list -- persists across all of them): the "grows" assertion compares
    this scenario's own before/after snapshot, not an absolute count. Returns the fresh project id.
    """
    before = driver.arrive()
    with driver.recorder.step("the arrival greeting is non-empty before anything exists to greet",
                               party="agent", kind="assert") as h:
        display = (before.get("display") or "").strip()
        h.record_assert("non-empty display", display)
        if len(display) < 10:
            h.fail(f"expected a non-empty arrival greeting, got {display!r}")
            raise AssertionError(h.error)
    before_count = len(before.get("projects") or [])

    result = driver.create_project()
    project_id = result["projectId"]
    display = result.get("display") or ""
    with driver.recorder.step("CREATE's own display carries the project name and a resolvable door",
                               party="agent", kind="assert") as h:
        match = _URL_RE.search(display)
        h.record_assert(f"{scenario.project_name()!r} and a URL in display", display)
        if scenario.project_name() not in display:
            h.fail(f"expected the project name in CREATE's own display, got {display!r}")
            raise AssertionError(h.error)
        if not match:
            h.fail(f"expected CREATE's display to carry a resolvable door, got {display!r}")
            raise AssertionError(h.error)
    founder.follow_display_url(match.group(0), project_id)

    # Relay re-venue (relay-design.md §12 item 2): the shared opening's own conversation moment --
    # CREATE's own commit -- now travels the relay too, exactly as keel-skill's M15 instructs a
    # relay-connected host to behave ("post display together with recorded as one playback turn").
    # This is the carrier every scenario shares (design's own "pragmatic scope" for the re-venue);
    # the protocol-side assertions above are unchanged, and this adds to them rather than replacing
    # any of them.
    founder_relay, agent_relay = open_relay(driver, project_id)
    relay_round_trip(founder_relay, agent_relay, f"I want to look into: {scenario.problem_statement()}",
                      BridgeReply.playback(display, result.get("recorded")))

    after = driver.arrive()
    after_projects = after.get("projects") or []
    with driver.recorder.step("the founder's project list grows by this scenario's own fresh project",
                               party="agent", kind="assert") as h:
        h.record_assert(f"{before_count + 1} project(s), latest is this one",
                         {"before": before_count, "after_count": len(after_projects),
                          "latest": after_projects[0] if after_projects else None})
        if len(after_projects) != before_count + 1:
            h.fail(f"expected the project list to grow by exactly one, got "
                    f"{before_count} -> {len(after_projects)}")
            raise AssertionError(h.error)
        if (not after_projects or after_projects[0].get("projectId") != project_id
                or not after_projects[0].get("latest")):
            h.fail(f"expected this fresh project newest-first and flagged latest, got "
                    f"{after_projects[0] if after_projects else None}")
            raise AssertionError(h.error)
    return project_id


def assert_pointer_to_agent(founder: FounderBrowser, project_id: str) -> None:
    """Policy v4 / founder-experience design §4 item 4: once a stage is approved and the workflow's
    next need is agent-side (framing or decomposing the next stage), the founder is told the next
    move is the agent's, never a link to click.

    **Updated 2026-08-31 for the guided walk (founder-experience-3-design.md §3; keel-web commit
    96c83af)**: exactly this moment -- some stage approved, the NEXT one still framed-but-
    undecomposed or unframed, and nothing else with real review work pending -- is also precisely
    `translate.ts#guidedWalkStep`'s own trigger, so the overview now shows the walk's own step
    INSTEAD OF the classic `.next.agent` sentence (`OverviewRoute.tsx`: the guided walk and the
    classic pointer never render at the same time). Both are the same underlying fact rendered two
    different ways: confirmed live against this stack, `assert_pointer_to_agent` now branches on
    which one is actually showing rather than assuming the classic sentence always is.
    """
    founder.open_overview(project_id)
    with founder._bstep.step("the next-step pointer names the agent, not a link") as h:
        guided = founder.page.locator(".guided-step")
        if guided.count() > 0:
            # The guided walk's own step IS the pointer-to-agent variant for this moment: neither
            # its "ask" nor "landed" phase renders a link anywhere (Continue/Reopen are buttons,
            # never anchors) -- the same "a destination that is a sentence, not a link" guarantee
            # `.next.agent`'s own live check makes, just over a different element.
            text = _safe_text_or_empty(guided.first.inner_text)
            h.record_assert("the guided walk's own step renders, no link inside it", text)
            if guided.locator("a").count() > 0:
                h.fail(f"expected the guided walk's step to carry no link, got an <a> inside it: {text!r}")
                raise AssertionError(h.error)
            if not text.strip():
                h.fail("expected the guided walk's step to render some text")
                raise AssertionError(h.error)
            return
        pointer = founder.page.locator(".next.agent")
        text = pointer.first.inner_text() if pointer.count() else ""
        h.record_assert("mentions 'Keel agent', no anchor, no URL", text)
        if "keel agent" not in text.lower():
            h.fail(f"expected the pointer-to-agent sentence on the overview, got {text!r}")
            raise AssertionError(h.error)


def _safe_text_or_empty(getter) -> str:
    try:
        return getter()
    except Exception:  # noqa: BLE001 - capture is advisory, never load-bearing for the scenario
        return ""


def assert_participant_has_no_founder_auth(participant_context) -> None:
    """Standing assertion (task item 1): the participant surface stays open, and the participant's
    own browser context must never carry the founder's session -- a fresh Playwright context
    already starts with an empty cookie jar and this harness never adds one to a participant
    context, but this makes the invariant a checked fact rather than an assumption a future change
    could silently break.
    """
    cookies = participant_context.cookies()
    session_cookies = [c for c in cookies if "session" in c.get("name", "").lower()
                        or c.get("name", "").upper() == "JSESSIONID"]
    assert not session_cookies, (
        f"the participant's browser context carries a founder session cookie -- it must stay "
        f"anonymous: {session_cookies}")


# --------------------------------------------------------------------------------- orchestration

# A single-stage scenario's own judgement call, shared here rather than tripled (S-004/S-005/S-006:
# each cares about PROBLEM alone, but the invite gate now requires SOLUTION and COMMERCIAL approved
# too before PROBLEM's own invite is legal). This placeholder belief exists only to give `approve()`
# something LOAD_BEARING to require -- it is never invited to on purpose (`roles_payload` below asks
# it of a role nobody ever sends a link to), so it never rides along on the scenario's own, carefully
# single-question invitation.
FILLER_ROLE_LABEL = "Not This Scenario's Subject"
_FILLER_CONTENT: dict[str, dict[str, str]] = {
    SOLUTION: {
        "statement": "A tool that automatically flags and routes payroll exceptions would get used.",
        "heading": "Not this scenario's subject",
        "ask": "Tell me about the last tool you tried for this.",
        "disconfirming": "Have you tried something like this and stopped using it?",
    },
    COMMERCIAL: {
        "statement": "Someone can approve paying for a tool like this.",
        "heading": "Not this scenario's subject",
        "ask": "Who signs off on a purchase like this?",
        "disconfirming": "Has a purchase like this ever had nobody able to approve it?",
    },
}


def filler_role_payload() -> dict:
    """The never-invited role a single-stage scenario adds to `roles_payload()` alongside its own
    real role, so SOLUTION/COMMERCIAL's placeholder belief (below) never shares a role -- and
    therefore never shares an invitation -- with the scenario's own carefully single-question
    interview."""
    return {"label": FILLER_ROLE_LABEL, "roleType": "MANAGER", "about": "Never actually invited"}


def filler_assumption_payload(stage: str, filler_role_id: str) -> dict:
    """One placeholder LOAD_BEARING belief for `stage` (SOLUTION or COMMERCIAL), asked of the
    never-invited filler role -- see the module comment above."""
    content = _FILLER_CONTENT[stage]
    return {
        "statement": content["statement"], "heading": content["heading"], "stage": stage,
        "risk": "LOAD_BEARING", "askedOf": filler_role_id,
        "question": {"ask": content["ask"], "probes": [], "disconfirming": content["disconfirming"]},
    }


def advance_to_all_stages_approved(driver: FounderAgentDriver, founder: FounderBrowser,
                                    scenario: Scenario | None = None) -> None:
    """The invite gate's own choreography (founder-experience design §6): the arrival read and
    `CREATE` (via `arrive_and_create`, task item 2's shared opening step -- skipped if `scenario`
    is omitted, for a caller that already ran it itself) through approving COMMERCIAL, one
    `REVIEW` handoff at a time, with no invitation sent along the way -- `Project.needs` refuses
    `INVITE` for every stage until all three are approved, so there is nothing legitimate to invite
    anyone to yet. `assert_invite_gate_closed` runs after each of the first two approvals (never
    the third -- the gate opens the instant COMMERCIAL is approved) as the standing assertion
    (design §6, task item 4): no `INVITE` need and no invitable role while any framed stage still
    awaits approval. Those same two approvals also demonstrate the pointer-to-agent variant
    (policy v4's `GUI-U2`, design §4 item 4): once PROBLEM (then SOLUTION) is approved, the next
    stage still needs agent-side framing/decomposing, so the overview's own next-step pointer
    hands off to the agent instead of offering a link. Usable by any `Scenario` whose
    `assumptions_payload` can decompose all three stages, even trivially -- not only
    `PricingSetupScenario`.
    """
    if scenario is not None:
        arrive_and_create(driver, founder, scenario)
    for index, stage in enumerate(STAGES):
        handoff = driver.advance_until_handoff()
        assert handoff and handoff["reason"] == "REVIEW" and handoff["detail"]["stage"] == stage, (stage, handoff)
        founder.open_stage(driver.project_id, stage)
        founder.approve_current_stage(stage)
        if index < len(STAGES) - 1:
            assert_invite_gate_closed(driver)
            assert_pointer_to_agent(founder, driver.project_id)


def assert_invite_gate_closed(driver: FounderAgentDriver) -> None:
    """The standing assertion (founder-experience design §6, task item 4): while any framed stage
    awaits approval, no stage reports an `INVITE` need (the agent state read) and no role reads as
    `invitable` (the founder role-picker read, `Project.invite`'s own per-role legality check).
    Two independent reads, both consulted live rather than assumed, matching this module's own
    "confirmed live, not assumed" practice throughout.
    """
    state = driver.get_state(driver.project_id)
    invite_stages = [s["stage"] for s in state.get("stages", []) if s.get("need") == "INVITE"]
    assert not invite_stages, (
        f"INVITE need surfaced before every framed stage was approved: {invite_stages} ({state})")
    roles = driver.get_founder_roles(driver.project_id)
    invitable = [r["label"] for r in roles.get("roles", []) if r.get("invitable")]
    assert not invitable, (
        f"a role read as invitable before every framed stage was approved: {invitable} ({roles})")


def rule_out_pricing(driver: FounderAgentDriver, founder: FounderBrowser, browser, recorder,
                      scenario: PricingSetupScenario, *,
                      unopened_person: str | None = None) -> RuledOutSetup:
    """Builds "three stages approved, pricing ruled out" on a fresh project via the real loop
    (T005). See this module's docstring for the discovered choreography this follows, including
    the invite-gate rewrite (2026-08-30): every stage is approved before any invitation exists, and
    the first (only) invitation to `ROLE_LABEL` already carries problem+solution+budget together.

    `unopened_person`, if given, is invited to the buyer role (pricing only) right alongside Dana
    -- while pricing is still open, so their link freezes that question -- but is never opened or
    answered by this function. S-002 uses this to get a link that is provably valid-when-sent and
    never touched, so opening it after the reframe tests journeys.md §2.4's out-of-date page on
    its own terms, distinct from re-opening Dana's already-answered link (which tests the "never
    told their work was wasted" half).
    """
    advance_to_all_stages_approved(driver, founder, scenario)

    # The gate is open now (all three approved). currentFocus scans PROBLEM first, and ROLE_LABEL
    # is uninvited there -- the resulting handoff is the one, combined invitation for problem,
    # solution and commercial-budget together (module docstring, "Update, 2026-08-30").
    handoff = driver.advance_until_handoff()
    assert handoff and handoff["reason"] == "INVITE", handoff
    founder.open_people(driver.project_id)
    combined_link = founder.send_invite(ROLE_LABEL, COMBINED_PERSON, scenario.about_line_combined())

    handoff = driver.advance_until_handoff()
    assert handoff and handoff["reason"] == "WAITING", handoff

    # The combined respondent answers problem, solution and budget in one sitting -- DOM order
    # matches Invitation.asks()'s stage-then-risk-then-introducedAt ordering (PROBLEM, SOLUTION,
    # COMMERCIAL's budget belief; pricing lives on the separate buyer-role link).
    participant_context = browser.new_context()
    try:
        page = participant_context.new_page()
        participant = ParticipantBrowser(page, recorder)
        participant.open(combined_link)
        participant.start()
        participant.answer([PROBLEM_ANSWER, SOLUTION_ANSWER, COMMERCIAL_BUDGET_ANSWER])
        participant.submit()
    finally:
        participant_context.close()

    # `currentFocus()` scans PROBLEM first (module docstring's "earliest stage with any need") --
    # while the combined invitation sits unanswered, PROBLEM's own need is ANSWERS/WAITING, and
    # COMMERCIAL's pricing INVITE cannot surface no matter how many invitations this function sends
    # ahead of time (confirmed live: sending both invitations before either is answered hands back
    # a WAITING handoff for PROBLEM, not COMMERCIAL's INVITE). So the combined invitation must be
    # answered and *interpreted* -- settling problem, solution and budget in the one INTERPRET call
    # its single response produces -- before pricing's own INVITE need can ever be offered.
    # `advance_until_handoff` chains straight through that INTERPRET (an ActionRec, not a handoff)
    # and stops exactly at the next real handoff.
    handoff = driver.advance_until_handoff()
    assert handoff and handoff["reason"] == "INVITE" and handoff["detail"]["stage"] == COMMERCIAL, handoff
    founder.open_people(driver.project_id)
    commercial_link = founder.send_invite(BUYER_ROLE_LABEL, COMMERCIAL_PERSON, scenario.about_line(COMMERCIAL))

    unopened_link = None
    if unopened_person is not None:
        founder.open_people(driver.project_id)
        unopened_link = founder.send_invite(BUYER_ROLE_LABEL, unopened_person, scenario.about_line(COMMERCIAL))

    handoff = driver.advance_until_handoff()
    assert handoff and handoff["reason"] == "WAITING", handoff

    participant_context = browser.new_context()
    try:
        page = participant_context.new_page()
        participant = ParticipantBrowser(page, recorder)
        participant.open(commercial_link)
        participant.start()
        participant.answer([COMMERCIAL_PRICING_ANSWER])
        participant.submit()
    finally:
        participant_context.close()

    # `advance_until_handoff` would keep going straight into submitting the FRAME/REFRAME action
    # itself (an ActionRec, not a handoff) the instant pricing settles CONTRADICTED, since it
    # chains through every agent-only action. Advance exactly one step by hand instead (pricing's
    # own INTERPRET), then peek at (never act on) what comes next, so each scenario decides.
    driver.advance_one()
    peek = driver.get_next()  # read-only: reports the recommendation, does not act on it

    return RuledOutSetup(project_id=driver.project_id, combined_link=combined_link,
                          commercial_link=commercial_link, unopened_commercial_link=unopened_link,
                          peek=peek)
