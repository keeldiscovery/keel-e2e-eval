"""S-002 -- the pricing pivot (T007; journeys.md §1.7-1.9, §2.4).

Walks: a commercial deal-breaker ("they would pay annually, upfront") ruled out by one decisive
respondent while its sibling deal-breaker (budget ownership) stays supported; the agent offered a
FRAME replacement, carrying only the surviving belief (§1.8-§1.9); the founder re-approves in the
browser; the old claim strikes through, still readable, on the commercial card, while problem and
solution stay byte-identical (§1.9); a link sent before the pivot and never opened shows the
out-of-date page when opened after it (§2.4); a link that *was* already answered before the pivot
is never told its answer was wasted (§2.4, the other half of the same sentence); the brief renders
clean, with no GOING AHEAD ANYWAY box, because nothing is contradicted any more.

**Upgraded 2026-08-30 (keel-cloud commit c63ad4a, DRIFT #5/#6 resolved, action-protocol-design-r2
§8a)**: the reframe now actually gains a belief of its own in the same review cycle --
`Stage.decomposedForActiveFrame()` distinguishes "this frame only inherited a carried survivor"
from "this frame has its own belief introduced against it", so the very next `get_next` after a
carrying reframe is `INTRODUCE_ASSUMPTIONS`, not the `REVIEW` handoff this module used to document
as a dead end. This test now walks journeys.md §1.9's full promise: the carried budget belief keeps
its verdict and evidence; a new pricing belief (the one the old claim's dead deal-breaker was never
replaced with) arrives unapproved; the stage reopens for review with both beliefs on it; the
founder approves; and a fresh invitation for the new belief carries *only* that question -- nothing
already settled rides along, because `Stage.linkFor` only ever freezes a role's currently *open*
assumptions (budget is `SUPPORTED`, so it is never re-frozen into a new link regardless of role).

**Discovered choreography, confirmed live against this stack (not assumed from the plan) --
`evals/recipes.py`'s module docstring has the full derivation and source citations:**

1. Ruling out a zero-supporter deal-breaker takes exactly one dissenting answer -- `verdictOf`'s
   split rule only produces `MIXED` when a real minority exists. `rule_out_pricing` therefore
   settles pricing with one decisive respondent (Dana Okafor, journeys.md §1.8's own first quote),
   on her own dedicated buyer-role link, while budget-owner is answered separately and stays
   `SUPPORTED`.
2. **`FRAME` with `carries` now reopens decomposition (DRIFT #5, resolved).** The very next
   `get_next` after the reframe is submitted is `INTRODUCE_ASSUMPTIONS` -- the stage's active frame
   has no belief of its own yet, only the carried survivor -- giving the agent a protocol-legal
   moment to introduce the new pricing question journeys.md §1.9 always promised ("new things to
   be true appear under the new claim, all unanswered").
3. This scenario's own judgement call from before the fix -- two separate roles for the two
   commercial beliefs, to keep a never-opened link that spans a carried-and-superseded pair (DRIFT
   #6's exact trigger shape) off this scenario's critical path -- is kept unchanged: the new pricing
   belief is still asked of the dedicated buyer role. See `assumptions_payload`'s own docstring
   below for why this test still doesn't manufacture DRIFT #6's precise mixed-ask reproduction, and
   what it asserts instead about the fix.
"""

from __future__ import annotations

import time

from evals.recipes import (
    BUYER_ROLE_LABEL, COMMERCIAL, COMMERCIAL_BUDGET_ASK, COMMERCIAL_BUDGET_ASSUMPTION,
    COMMERCIAL_CLAIM, COMMERCIAL_PERSON, COMMERCIAL_PRICING_ANSWER, COMMERCIAL_PRICING_ASK,
    COMMERCIAL_PRICING_ASSUMPTION, PROBLEM, PROBLEM_ASSUMPTION, PROBLEM_CLAIM, PROBLEM_HEADING,
    PROJECT_NAME, ROLE_LABEL, SOLUTION, SOLUTION_ASSUMPTION, SOLUTION_CLAIM, SOLUTION_HEADING,
    PricingSetupScenario, assert_participant_has_no_founder_auth, open_founder_session,
    rule_out_pricing,
)
from evals.scenario import Fact, find_role
from harness.browser import ParticipantBrowser
from harness.evidence import finalize_run
from harness.steps import Recorder

UNOPENED_PERSON = "Priya Raman"  # journeys.md §1.7's own never-yet-answered respondent

NEW_COMMERCIAL_CLAIM = "Charge per payroll run, billed monthly."  # journeys.md §1.8's agent proposal
REFRAME_RATIONALE = ("Dana ruled out paying annually upfront but said she'd expense it per run "
                      "without blinking -- replacing the claim to test that instead.")

# The belief the old claim's dead deal-breaker was never replaced with, before DRIFT #5's fix --
# the whole reason journeys.md §1.9's "new things to be true appear under the new claim" now has
# somewhere to land.
NEW_COMMERCIAL_PRICING_ASSUMPTION = "They would pay per payroll run, billed monthly."
NEW_COMMERCIAL_PRICING_HEADING = "Pays per run, billed monthly"
NEW_COMMERCIAL_PRICING_ASK = "Walk me through how your team would rather be billed for a tool like this."
NEW_COMMERCIAL_PRICING_DISCONFIRMING = "Would monthly per-run billing ever be worse for your team than paying upfront?"
NEW_PRICING_PERSON = "Jamie Cole"
NEW_PRICING_ANSWER = "We'd expense it per run without blinking -- monthly billing is exactly how we'd want it."


class S002PricingPivot(PricingSetupScenario):
    name = "S-002 pricing pivot"
    slug = "s002-pricing-pivot"

    def __init__(self) -> None:
        super().__init__()
        # Set once COMMERCIAL's *first* decompose (the original budget+pricing pair) has run, so
        # a second INTRODUCE_ASSUMPTIONS call for the same stage -- only reachable post-DRIFT-#5,
        # once the reframe reopens decomposition -- is recognised as the *new* pricing question,
        # not another copy of the original pair.
        self._commercial_decomposed_once = False

    def reframe_statement(self, stage: str) -> str:
        return NEW_COMMERCIAL_CLAIM

    def reframe_rationale(self, stage: str) -> str:
        return REFRAME_RATIONALE

    def assumptions_payload(self, stage: str, roles: list[dict]) -> list[dict]:
        """Overridden only for COMMERCIAL's *second* decompose -- the one DRIFT #5 made reachable:
        `INTRODUCE_ASSUMPTIONS` recommended a second time for the same stage, once against the
        reframed claim, introducing the new pricing question the old claim's dead deal-breaker was
        never replaced with (journeys.md §1.9). Every other call (every stage's first decompose)
        defers to the base class unchanged.

        **Still asked of the dedicated buyer role, not the manager role budget lives on** -- the
        same judgement call `recipes.py` documents from before DRIFT #5 existed, for a different
        reason now: `Stage.linkFor` only ever freezes a role's currently-*open* assumptions
        (`Verdict.isOpen()`), and budget is already `SUPPORTED` by the time this belief is
        introduced -- so no invitation minted after this point, to *either* role, could ever ask
        about budget again regardless of role assignment. Manufacturing DRIFT #6's precise
        mixed-ask reproduction (one never-opened invitation asking about both a carried survivor
        and a soon-superseded belief) would require both commercial beliefs to share one role
        *from their very first introduction*, before either resolves -- a real restructuring of
        this scenario's own critical path, not a one-line change here. This test instead asserts
        DRIFT #6's fix where it genuinely is exercised on this scenario's own terms: see the test
        function's "orphaned unanswered link" step below.
        """
        if stage == COMMERCIAL and self._commercial_decomposed_once:
            buyer_role_id = find_role(roles, BUYER_ROLE_LABEL)["id"]
            return [{
                "statement": NEW_COMMERCIAL_PRICING_ASSUMPTION, "heading": NEW_COMMERCIAL_PRICING_HEADING,
                "stage": COMMERCIAL, "risk": "LOAD_BEARING", "askedOf": buyer_role_id,
                "question": {"ask": NEW_COMMERCIAL_PRICING_ASK, "probes": [],
                             "disconfirming": NEW_COMMERCIAL_PRICING_DISCONFIRMING},
            }]
        payload = super().assumptions_payload(stage, roles)
        if stage == COMMERCIAL:
            self._commercial_decomposed_once = True
        return payload

    def brief_payload(self, context) -> dict:
        return {
            "findings": [
                "Payroll managers handle exceptions themselves, monthly (1 of 1 respondents).",
                "A tool that flags and routes exceptions would get used (1 of 1 respondents).",
                "Someone in the payroll organisation owns a budget for this (1 of 1 respondents).",
                "They would pay per payroll run, billed monthly (1 of 1 respondents).",
            ],
            "openDecisions": [],
            # goingAhead omitted: the reframe carried only the SUPPORTED survivor and the new
            # pricing belief settled SUPPORTED too, so nothing applying is CONTRADICTED any more (A9).
        }

    def facts(self) -> dict[str, Fact]:
        return {
            "project_name": Fact(text=PROJECT_NAME, kind="statement", hops=["recorded", "stage_screen"]),
            "problem_statement": Fact(text=PROBLEM_CLAIM, kind="statement",
                                       hops=["agent_echo", "stage_screen", "brief", "recorded"]),
            "problem_heading": Fact(text=PROBLEM_HEADING, kind="assumption", hops=["stage_screen", "recorded"]),
            "solution_statement": Fact(text=SOLUTION_CLAIM, kind="statement",
                                        hops=["agent_echo", "stage_screen", "brief", "recorded"]),
            "solution_heading": Fact(text=SOLUTION_HEADING, kind="assumption", hops=["stage_screen", "recorded"]),
            "old_commercial_claim": Fact(text=COMMERCIAL_CLAIM, kind="statement",
                                          hops=["agent_echo", "stage_screen"],
                                          absent_hops=["brief"]),  # struck through, not the brief's claim
            "new_commercial_claim": Fact(text=NEW_COMMERCIAL_CLAIM, kind="statement",
                                          hops=["agent_echo", "stage_screen", "brief", "recorded"]),
            "reframe_rationale": Fact(text=REFRAME_RATIONALE, kind="statement", hops=["stage_screen"]),
            "role_label": Fact(text=ROLE_LABEL, kind="role",
                                hops=["agent_echo", "stage_screen", "invite_screen", "recorded"]),
            "assumption_problem": Fact(text=PROBLEM_ASSUMPTION, kind="assumption",
                                        hops=["agent_echo", "stage_screen", "interpret_context", "brief", "recorded"]),
            "assumption_solution": Fact(text=SOLUTION_ASSUMPTION, kind="assumption",
                                         hops=["agent_echo", "stage_screen", "interpret_context", "brief", "recorded"]),
            "assumption_budget": Fact(text=COMMERCIAL_BUDGET_ASSUMPTION, kind="assumption",
                                       hops=["agent_echo", "stage_screen", "interpret_context", "brief", "recorded"]),
            "assumption_pricing_old": Fact(text=COMMERCIAL_PRICING_ASSUMPTION, kind="assumption",
                                            hops=["agent_echo", "stage_screen", "interpret_context", "recorded"],
                                            absent_hops=["brief"]),  # superseded before any brief exists
            "answer_pricing": Fact(text=COMMERCIAL_PRICING_ANSWER, kind="answer",
                                    hops=["interpret_context", "stage_screen"]),
            # New under DRIFT #5's fix: the belief the reframe's own review cycle introduces, and
            # the evidence that settles it -- both now reachable, and both traced end to end.
            "assumption_pricing_new": Fact(text=NEW_COMMERCIAL_PRICING_ASSUMPTION, kind="assumption",
                                            hops=["agent_echo", "stage_screen", "interpret_context", "brief", "recorded"]),
            "pricing_new_heading": Fact(text=NEW_COMMERCIAL_PRICING_HEADING, kind="assumption",
                                         hops=["stage_screen", "recorded"]),
            "answer_pricing_new": Fact(text=NEW_PRICING_ANSWER, kind="answer",
                                        hops=["interpret_context", "stage_screen"]),
        }


def test_s002_pricing_pivot(stack, run_dir, browser, founder_credentials):
    recorder = Recorder(run_dir)
    scenario = S002PricingPivot()
    passed = False
    started = time.monotonic()
    driver, founder, founder_context = open_founder_session(stack, founder_credentials, recorder,
                                                              scenario, browser)
    founder_page = founder.page
    try:
        setup = rule_out_pricing(driver, founder, browser, recorder, scenario,
                                  unopened_person=UNOPENED_PERSON)
        project_id = setup.project_id

        # journeys.md §1.8: "The claim needs to change." -- the agent is offered a FRAME
        # replacement for COMMERCIAL, never a handoff, the instant pricing is ruled out.
        with recorder.step("agent is offered a FRAME replacement on the ruled-out commercial claim",
                            party="agent", kind="assert") as h:
            h.record_assert("action FRAME, reason REFRAME", setup.peek)
            if not (setup.peek.get("kind") == "action" and setup.peek.get("action") == "FRAME"
                    and (setup.peek.get("detail") or {}).get("reason") == "REFRAME"):
                h.fail(f"expected a REFRAME FRAME offer, got {setup.peek}")
                raise AssertionError(h.error)

        # FID hop capture (assumption_pricing_old/answer_pricing): the ruled-out belief's
        # testimony drilldown, while it still exists un-superseded -- the only place Dana's raw
        # contradicting answer renders on a founder screen (Drilldown's `.quote .words`).
        founder.open_stage_evidence(project_id, COMMERCIAL)

        # Snapshot problem/solution BEFORE the reframe -- journeys.md §1.9: "The problem and
        # solution cards are untouched -- same statuses, same evidence, same counts."
        founder.open_stage(project_id, PROBLEM)
        problem_before = founder_page.locator(".card.openc").first.inner_text()
        founder.open_stage(project_id, SOLUTION)
        solution_before = founder_page.locator(".card.openc").first.inner_text()

        # Submit the reframe -- PricingSetupScenario.build_payload's REFRAME branch reads the
        # `opportunity` handle and carries only the non-CONTRADICTED survivor (budget-owner).
        driver.advance_one()

        # journeys.md §1.9, now reachable (DRIFT #5 resolved): the very next get_next is
        # INTRODUCE_ASSUMPTIONS, not a REVIEW handoff -- the reframed claim has no belief of its
        # own yet, only the carried survivor. Peek the token's own `opportunity` grant first, to
        # confirm the carried belief kept its verdict and its applying status across the reframe,
        # before submitting anything.
        with recorder.step("the reframe reopens decomposition instead of handing straight to REVIEW",
                            party="agent", kind="assert") as h:
            after_reframe = driver.get_next()
            h.record_assert("action INTRODUCE_ASSUMPTIONS", after_reframe)
            if not (after_reframe.get("kind") == "action"
                    and after_reframe.get("action") == "INTRODUCE_ASSUMPTIONS"):
                h.fail(f"expected INTRODUCE_ASSUMPTIONS (DRIFT #5 resolved), got {after_reframe}")
                raise AssertionError(h.error)

        with recorder.step("the carried budget belief keeps its verdict across the reframe",
                            party="agent", kind="assert") as h:
            opportunity = driver.get_context(after_reframe["token"], "opportunity")
            commercial_card = next(c for c in opportunity["stages"] if c["stage"] == COMMERCIAL)
            budget_belief = next((b for b in commercial_card["beliefs"]
                                   if b["statement"] == COMMERCIAL_BUDGET_ASSUMPTION), None)
            h.record_assert("budget belief present, verdict SUPPORTED, still applying", commercial_card)
            if budget_belief is None or budget_belief["verdict"] != "SUPPORTED" or not budget_belief["applying"]:
                h.fail(f"expected the carried budget belief SUPPORTED and applying, got {budget_belief}")
                raise AssertionError(h.error)
            if any(b["statement"] == COMMERCIAL_PRICING_ASSUMPTION for b in commercial_card["beliefs"]):
                h.fail("the superseded pricing belief is still applying after the reframe carried "
                       "only budget-owner")
                raise AssertionError(h.error)

        # Submit INTRODUCE_ASSUMPTIONS -- the new pricing belief, under the new claim.
        driver.advance_one()

        # journeys.md §1.9: "New things to be true appear under the new claim, all unanswered --
        # and unapproved." Confirm the stage came back unapproved before touching the UI at all.
        with recorder.step("the new belief arrives unapproved -- the stage is not auto-approved",
                            party="agent", kind="assert") as h:
            state = driver.get_state(project_id)
            commercial_state = next(s for s in state["stages"] if s["stage"] == COMMERCIAL)
            h.record_assert("approved=False, need=REVIEW", commercial_state)
            if commercial_state["approved"] or commercial_state["need"] != "REVIEW":
                h.fail(f"expected COMMERCIAL unapproved with need REVIEW, got {commercial_state}")
                raise AssertionError(h.error)

        # "The commercial card reopens for review, the same way it did at the very start."
        handoff = driver.advance_until_handoff()
        assert handoff and handoff["reason"] == "REVIEW" and handoff["detail"]["stage"] == COMMERCIAL, handoff
        founder.open_stage(project_id, COMMERCIAL)

        # journeys.md §1.9: "the old one underneath it, struck through and still readable."
        with recorder.step("the old commercial claim strikes through but stays readable",
                            party="founder", kind="assert") as h:
            new_claim = founder_page.locator(".card.openc .claim").first.inner_text()
            dead_claim = founder_page.locator(".card.openc .claim.dead")
            dead_text = dead_claim.inner_text() if dead_claim.count() > 0 else ""
            h.record_assert(f"new={NEW_COMMERCIAL_CLAIM!r} dead(struck-through, readable)={COMMERCIAL_CLAIM!r}",
                             {"new_claim": new_claim, "dead_claim_text": dead_text,
                              "dead_claim_count": dead_claim.count()})
            if new_claim.strip() != NEW_COMMERCIAL_CLAIM:
                h.fail(f"expected the new claim on .claim, got {new_claim!r}")
                raise AssertionError(h.error)
            if dead_claim.count() != 1 or dead_text.strip() != COMMERCIAL_CLAIM:
                h.fail(f"expected the old claim struck-through-but-readable on .claim.dead, got "
                       f"count={dead_claim.count()} text={dead_text!r}")
                raise AssertionError(h.error)

        founder.approve_current_stage(COMMERCIAL)

        # journeys.md §1.9: problem/solution "untouched -- same statuses, same evidence, same counts."
        with recorder.step("problem and solution cards are byte-identical before and after the reframe",
                            party="founder", kind="assert") as h:
            founder.open_stage(project_id, PROBLEM)
            problem_after = founder_page.locator(".card.openc").first.inner_text()
            founder.open_stage(project_id, SOLUTION)
            solution_after = founder_page.locator(".card.openc").first.inner_text()
            h.record_assert("identical", {"problem_before": problem_before, "problem_after": problem_after,
                                           "solution_before": solution_before, "solution_after": solution_after})
            if problem_before != problem_after or solution_before != solution_after:
                h.fail("problem or solution card text changed across the commercial reframe")
                raise AssertionError(h.error)

        # journeys.md §2.4: a link sent before the pivot and never opened shows the out-of-date
        # page when finally opened -- nothing entered there would reach the founder.
        stale_context = browser.new_context()
        try:
            stale_page = stale_context.new_page()
            stale_participant = ParticipantBrowser(stale_page, recorder)
            with recorder.step("a never-opened pre-pivot link shows the out-of-date page (§2.4)",
                                party="participant", kind="assert") as h:
                stale_participant.open_expect_notice(setup.unopened_commercial_link)
                body = stale_page.locator("body").inner_text()
                h.record_assert("mentions the questions no longer being valid, no consent form",
                                 body)
                if "asked if you" in body.lower():
                    h.fail("the stale link still rendered a fresh consent screen")
                    raise AssertionError(h.error)
                if not any(w in body.lower() for w in ("stale", "no longer", "changed", "out of date")):
                    h.fail(f"expected an out-of-date notice, got: {body!r}")
                    raise AssertionError(h.error)
        finally:
            stale_context.close()

        # journeys.md §2.4: "A person who has already submitted is never told their work was
        # wasted" -- the SAME link, but this one was answered before the pivot.
        answered_context = browser.new_context()
        try:
            answered_page = answered_context.new_page()
            answered_participant = ParticipantBrowser(answered_page, recorder)
            with recorder.step("an already-answered pre-pivot link is never told its work was wasted",
                                party="participant", kind="assert") as h:
                answered_participant.open_expect_notice(setup.commercial_link)
                body = answered_page.locator("body").inner_text()
                h.record_assert("thanks/already-answered, not a stale/wasted-effort message", body)
                lowered = body.lower()
                if any(w in lowered for w in ("stale", "out of date", "wasted", "no longer valid")):
                    h.fail(f"an already-answered participant was told their link was stale/wasted: {body!r}")
                    raise AssertionError(h.error)
                if "already answered" not in lowered and "thanks" not in lowered:
                    h.fail(f"expected an already-answered/thank-you notice, got: {body!r}")
                    raise AssertionError(h.error)
        finally:
            answered_context.close()

        # DRIFT #6, resolved: the never-opened pre-pivot pricing link (`unopened_commercial_link`,
        # asking only about the now-superseded old pricing belief) is answered by nobody and never
        # opened for the rest of this run. Before the fix, `Project.needs`/`ParticipantController`
        # disagreed about exactly this shape of link when its `asks` spanned a carried survivor and
        # a superseded belief together; this scenario's own two-role split (recipes.py's judgement
        # call, unchanged by the DRIFT #5 fix -- see `assumptions_payload`'s docstring above) keeps
        # this particular link single-ask, so it was never literally the failure mode's trigger --
        # but it is still a real never-opened, permanently-stale invitation, and the fix's actual
        # code change (`Project.isInvitationStale`, read by both `needs()` and the participant
        # page) is the same derivation this link's own out-of-date notice above already exercised.
        # What we can and do assert here is the observable consequence design r2 §8a promises: this
        # orphaned link never wedges COMMERCIAL's workflow -- the founder is never told WAITING
        # because of it, all the way through to the fresh invitation below actually being reachable.
        with recorder.step("the orphaned unanswered pre-pivot link never wedges the workflow (DRIFT #6)",
                            party="stack", kind="assert") as h:
            state = driver.get_state(project_id)
            commercial_state = next(s for s in state["stages"] if s["stage"] == COMMERCIAL)
            h.record_assert("COMMERCIAL's need is INVITE (the new pricing belief), not stuck on ANSWERS",
                             commercial_state)
            if commercial_state["need"] == "ANSWERS":
                h.fail(f"COMMERCIAL is stuck waiting on answers -- the orphaned pre-pivot link may be "
                       f"wedging it again: {commercial_state}")
                raise AssertionError(h.error)

        # journeys.md §1.9: "a new manager's link carries the fresh pricing questions... it carries
        # nothing that is done." Invite someone new to the buyer role and confirm the fresh link
        # asks about the new pricing belief alone -- budget (SUPPORTED) never rides along.
        handoff = driver.advance_until_handoff()
        assert handoff and handoff["reason"] == "INVITE" and handoff["detail"]["stage"] == COMMERCIAL, handoff
        founder.open_invite(project_id)
        fresh_link = founder.send_invite(BUYER_ROLE_LABEL, NEW_PRICING_PERSON, scenario.about_line(COMMERCIAL))

        fresh_context = browser.new_context()
        try:
            fresh_page = fresh_context.new_page()
            fresh_participant = ParticipantBrowser(fresh_page, recorder)
            with recorder.step("the fresh link carries only the new pricing question, nothing settled",
                                party="participant", kind="assert") as h:
                fresh_participant.open(fresh_link)
                fresh_participant.start()
                questions = fresh_page.locator(".q").all_inner_texts()
                h.record_assert("exactly one question, the new pricing ask; nothing about budget or "
                                 "the old pricing claim", questions)
                if len(questions) != 1:
                    h.fail(f"expected exactly one question on the fresh link, got {len(questions)}: {questions}")
                    raise AssertionError(h.error)
                if NEW_COMMERCIAL_PRICING_ASK not in questions[0]:
                    h.fail(f"expected the new pricing question, got: {questions[0]!r}")
                    raise AssertionError(h.error)
                if any(term in questions[0] for term in (COMMERCIAL_BUDGET_ASK, COMMERCIAL_PRICING_ASK)):
                    h.fail(f"the fresh link leaked an already-settled question: {questions[0]!r}")
                    raise AssertionError(h.error)
            fresh_participant.answer([NEW_PRICING_ANSWER])
            fresh_participant.submit()
            assert_participant_has_no_founder_auth(fresh_context)
        finally:
            fresh_context.close()

        # The new pricing answer reads as supportive -- interpret_payload's default (no override
        # needed: only the OLD pricing statement is special-cased to CONTRADICTS).
        handoff = driver.advance_until_handoff()
        assert handoff is None, f"expected the project to finish (brief proposed), got {handoff}"

        # FID hop capture: the new pricing belief's own testimony (Jamie Cole's answer) only
        # renders on the stage screen once this second visit expands its drilldown.
        founder.open_stage_evidence(project_id, COMMERCIAL)

        # FID hop capture: the project name reaches a founder screen only via the overview's own
        # full-body capture (browser.py's `_goto_screen` -- a stage visit only captures its own
        # card, not the shell header this scenario never otherwise visits).
        founder.open_overview(project_id)

        founder.open_brief(project_id)
        with recorder.step("the brief renders with no GOING AHEAD ANYWAY box", party="founder", kind="assert") as h:
            goahead = founder_page.locator(".goahead")
            findings = founder_page.locator(".blist.learned li").all_inner_texts()
            h.record_assert("no .goahead box, 4 findings", {"goahead_count": goahead.count(), "findings": findings})
            if goahead.count() != 0:
                h.fail(f"expected no GOING AHEAD ANYWAY box (nothing is contradicted), found {goahead.count()}")
                raise AssertionError(h.error)
            if len(findings) != 4:
                h.fail(f"expected 4 findings (problem, solution, budget, new pricing), got {findings}")
                raise AssertionError(h.error)

        passed = True
    finally:
        founder_context.close()
        duration = time.monotonic() - started
        finalize_run(run_dir, scenario=scenario, passed=passed,
                     failed_step=recorder.failed_step, duration_s=duration)
        print(f"\nrun bundle: {run_dir}")
