"""S-002 -- the pricing pivot (T007; journeys.md §1.7-1.9, §2.4).

Walks: a commercial deal-breaker ("they would pay annually, upfront") ruled out by one decisive
respondent while its sibling deal-breaker (budget ownership) stays supported; the agent offered a
FRAME replacement, carrying only the surviving belief (§1.8-§1.9); the founder re-approves in the
browser; the old claim strikes through, still readable, on the commercial card, while problem and
solution stay byte-identical (§1.9); a link sent before the pivot and never opened shows the
out-of-date page when opened after it (§2.4); a link that *was* already answered before the pivot
is never told its answer was wasted (§2.4, the other half of the same sentence); the brief renders
clean, with no GOING AHEAD ANYWAY box, because nothing is contradicted any more.

**Discovered choreography, confirmed live against this stack (not assumed from the plan) --
`evals/recipes.py`'s module docstring has the full derivation and source citations:**

1. Ruling out a zero-supporter deal-breaker takes exactly one dissenting answer -- `verdictOf`'s
   split rule only produces `MIXED` when a real minority exists. `rule_out_pricing` therefore
   settles pricing with one decisive respondent (Dana Okafor, journeys.md §1.8's own first quote),
   on her own dedicated buyer-role link, while budget-owner is answered separately and stays
   `SUPPORTED`.
2. **`FRAME` with `carries` never reopens decomposition.** The `get_next` immediately after the
   reframe is submitted is a `REVIEW` handoff, not an `INTRODUCE_ASSUMPTIONS` action -- there is no
   protocol-legal moment at which a *new* pricing question can be introduced alongside the carried
   survivor. Approving that stage with only the carried belief goes straight to `PROCEED_TO_BRIEF`
   ("nothing left to settle"). This directly contradicts journeys.md §1.9's "new things to be true
   appear under the new claim, all unanswered" -- no new things appear, ever, through this
   protocol. This test reproduces the finding every run and records it in `runs/DRIFT.md` rather
   than working around it (design §6): the reframe itself is asserted exactly as the product
   allows, not as the journey describes it should read afterward.
3. Because of (2), this scenario cannot literally satisfy spec.md's acceptance scenario 3 ("the
   fresh link carries the new pricing questions") -- there is no new pricing question to carry, and
   no invite screen to visit for it (there is nothing open left to ask). That absence is itself
   asserted below rather than silently skipped.
"""

from __future__ import annotations

import time

from evals.recipes import (
    COMMERCIAL, COMMERCIAL_BUDGET_ASSUMPTION, COMMERCIAL_CLAIM, COMMERCIAL_PERSON,
    COMMERCIAL_PRICING_ANSWER, COMMERCIAL_PRICING_ASSUMPTION, PROBLEM, PROBLEM_ASSUMPTION,
    PROBLEM_CLAIM, PROBLEM_PERSON, ROLE_LABEL, SOLUTION, SOLUTION_ASSUMPTION, SOLUTION_CLAIM,
    SOLUTION_PERSON, PricingSetupScenario, rule_out_pricing,
)
from evals.scenario import Fact
from harness.browser import FounderBrowser, ParticipantBrowser
from harness.driver import FounderAgentDriver, ProtocolError
from harness.evidence import finalize_run
from harness.steps import Recorder

UNOPENED_PERSON = "Priya Raman"  # journeys.md §1.7's own never-yet-answered respondent

NEW_COMMERCIAL_CLAIM = "Charge per payroll run, billed monthly."  # journeys.md §1.8's agent proposal
REFRAME_RATIONALE = ("Dana ruled out paying annually upfront but said she'd expense it per run "
                      "without blinking -- replacing the claim to test that instead.")


class S002PricingPivot(PricingSetupScenario):
    name = "S-002 pricing pivot"
    slug = "s002-pricing-pivot"

    def reframe_statement(self, stage: str) -> str:
        return NEW_COMMERCIAL_CLAIM

    def reframe_rationale(self, stage: str) -> str:
        return REFRAME_RATIONALE

    def brief_payload(self, context) -> dict:
        return {
            "findings": [
                "Payroll managers handle exceptions themselves, monthly (1 of 1 respondents).",
                "A tool that flags and routes exceptions would get used (1 of 1 respondents).",
                "Someone in the payroll organisation owns a budget for this (1 of 1 respondents).",
            ],
            "openDecisions": [
                "Whether people will actually pay per payroll run has not been asked yet.",
            ],
            # goingAhead omitted: the reframe carried only the SUPPORTED survivor, so nothing
            # applying is CONTRADICTED any more (A9).
        }

    def facts(self) -> dict[str, Fact]:
        return {
            "problem_statement": Fact(text=PROBLEM_CLAIM, kind="statement",
                                       hops=["agent_echo", "stage_screen", "brief"]),
            "solution_statement": Fact(text=SOLUTION_CLAIM, kind="statement",
                                        hops=["agent_echo", "stage_screen", "brief"]),
            "old_commercial_claim": Fact(text=COMMERCIAL_CLAIM, kind="statement",
                                          hops=["agent_echo", "stage_screen"],
                                          absent_hops=["brief"]),  # struck through, not the brief's claim
            "new_commercial_claim": Fact(text=NEW_COMMERCIAL_CLAIM, kind="statement",
                                          hops=["agent_echo", "stage_screen", "brief"]),
            "reframe_rationale": Fact(text=REFRAME_RATIONALE, kind="statement", hops=["stage_screen"]),
            "role_label": Fact(text=ROLE_LABEL, kind="role",
                                hops=["agent_echo", "stage_screen", "invite_screen"]),
            "assumption_problem": Fact(text=PROBLEM_ASSUMPTION, kind="assumption",
                                        hops=["agent_echo", "stage_screen", "interpret_context", "brief"]),
            "assumption_solution": Fact(text=SOLUTION_ASSUMPTION, kind="assumption",
                                         hops=["agent_echo", "stage_screen", "interpret_context", "brief"]),
            "assumption_budget": Fact(text=COMMERCIAL_BUDGET_ASSUMPTION, kind="assumption",
                                       hops=["agent_echo", "stage_screen", "interpret_context", "brief"]),
            "assumption_pricing_old": Fact(text=COMMERCIAL_PRICING_ASSUMPTION, kind="assumption",
                                            hops=["agent_echo", "stage_screen", "interpret_context"],
                                            absent_hops=["brief"]),  # superseded before any brief exists
            "answer_pricing": Fact(text=COMMERCIAL_PRICING_ANSWER, kind="answer",
                                    hops=["interpret_context", "stage_screen"]),
        }


def test_s002_pricing_pivot(stack, run_dir, browser):
    recorder = Recorder(run_dir)
    scenario = S002PricingPivot()
    cloud_base = f"http://localhost:{stack.cloud_port}"
    founder_web_base = f"http://localhost:{stack.web_port}/p"

    driver = FounderAgentDriver(cloud_base, recorder, scenario)
    passed = False
    started = time.monotonic()
    founder_context = browser.new_context()
    try:
        founder_page = founder_context.new_page()
        founder = FounderBrowser(founder_page, founder_web_base, recorder, get_state=driver.get_state)

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

        # Discovered choreography: the very next get_next is a REVIEW handoff, not
        # INTRODUCE_ASSUMPTIONS -- there is no cycle in which a new pricing belief can be added
        # alongside the carried survivor (see this module's + recipes.py's docstrings).
        with recorder.step("discovered: a carrying reframe cannot add a new assumption in the same cycle",
                            party="stack", kind="assert") as h:
            after_reframe = driver.get_next()
            h.record_assert("NOT an INTRODUCE_ASSUMPTIONS action", after_reframe)
            if after_reframe.get("kind") == "action" and after_reframe.get("action") == "INTRODUCE_ASSUMPTIONS":
                # If a future keel-cloud fix makes this reachable, take the win rather than fail.
                driver.advance_one()
                recorder.note("INTRODUCE_ASSUMPTIONS was reachable after all -- prior finding resolved",
                               party="stack")
            else:
                if not (after_reframe.get("kind") == "handoff" and after_reframe.get("reason") == "REVIEW"):
                    h.fail(f"expected the documented REVIEW handoff, got {after_reframe}")
                    raise AssertionError(h.error)

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

        # Discovered gap (recipes.py, DRIFT.md): no new pricing question was ever created, so
        # there is nothing left to invite anyone to ask about pricing -- get_next goes straight to
        # PROCEED_TO_BRIEF, never an INVITE handoff for a fresh pricing question.
        with recorder.step("discovered: no new pricing question ever became reachable to invite anyone to",
                            party="stack", kind="assert") as h:
            next_response = driver.get_next()
            h.record_assert("PROCEED_TO_BRIEF, not an INVITE handoff for a new pricing question",
                             next_response)
            if next_response.get("kind") == "handoff" and next_response.get("reason") == "INVITE" \
                    and (next_response.get("detail") or {}).get("stage") == COMMERCIAL:
                recorder.note("a new pricing question WAS reachable after all -- prior finding resolved",
                               party="stack")
            elif not (next_response.get("kind") == "action" and next_response.get("action") == "PROCEED_TO_BRIEF"):
                h.fail(f"expected PROCEED_TO_BRIEF (nothing left to settle), got {next_response}")
                raise AssertionError(h.error)

        handoff = driver.advance_until_handoff()
        assert handoff is None, f"expected the project to finish (brief proposed), got {handoff}"

        founder.open_brief(project_id)
        with recorder.step("the brief renders with no GOING AHEAD ANYWAY box", party="founder", kind="assert") as h:
            goahead = founder_page.locator(".goahead")
            findings = founder_page.locator(".blist.learned li").all_inner_texts()
            h.record_assert("no .goahead box, 3 findings", {"goahead_count": goahead.count(), "findings": findings})
            if goahead.count() != 0:
                h.fail(f"expected no GOING AHEAD ANYWAY box (nothing is contradicted), found {goahead.count()}")
                raise AssertionError(h.error)
            if len(findings) != 3:
                h.fail(f"expected 3 findings (problem, solution, budget), got {findings}")
                raise AssertionError(h.error)

        passed = True
    finally:
        founder_context.close()
        duration = time.monotonic() - started
        finalize_run(run_dir, scenario=scenario, passed=passed,
                     failed_step=recorder.failed_step, duration_s=duration)
        print(f"\nrun bundle: {run_dir}")
