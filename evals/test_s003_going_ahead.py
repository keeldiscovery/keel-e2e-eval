"""S-003 -- going ahead anyway (T008; journeys.md §1.10).

The journey: a founder reads *ruled out* on their pricing claim, does not reframe, and asks their
agent for the brief anyway. Keel warns, in the founder's own words if they go ahead:

    "Before I write anything -- one of the things that has to be true for your pricing isn't...
     You can change the claim... or you can tell me you're going ahead anyway, and I'll write down
     why, in your words, at the top of the brief. Which is it?"

If they go ahead, `proceedToBrief`'s A9 rule requires a `goingAhead` sentence exactly when an
applying load-bearing assumption is `CONTRADICTED`, and the brief renders a GOING AHEAD ANYWAY box
first, with the disproved belief filed under "what the evidence said no to" -- never blurred into
"taking on faith" (`FounderViewAssembler.brief`: `CONTRADICTED` -> `saidNoTo`, everything else open
-> `takingOnFaith`, by construction, never both).

**Upgraded 2026-08-30 (keel-cloud commit c63ad4a, DRIFT #7 resolved, action-protocol-design-r2
§8a)**: this journey moment used to have no protocol-legal entry point at all -- `get_next` now
accepts an optional `request="brief"` (harness/driver.py's `FounderAgentDriver.get_next`), which
issues `PROCEED_TO_BRIEF` outright regardless of `currentFocus()`, refusing only `"legality"` if
some stage was never framed. This test replaces the old "documented block" design (three plain
`get_next` calls proving the front door didn't exist) with the real walk journeys.md §1.10 always
described: the founder reads *ruled out*, asks their agent for the brief anyway, the agent calls
`get_next(request="brief")`, a first submission that omits `goingAhead` is refused by A9 with a
remedy actionable enough for a lost agent to follow, the identical token is resubmitted with the
founder's own sentence, and the project reaches `READY_TO_BUILD` with the brief rendering the GOING
AHEAD ANYWAY box first and the disproved pricing belief filed only under "what the evidence said no
to".

**Discovered choreography, confirmed live against this stack (`evals/recipes.py`'s module docstring
has the shared setup's full derivation):** ruling out a zero-supporter deal-breaker takes exactly
one dissenting answer (Dana Okafor, journeys.md §1.8's own first quote) -- `rule_out_pricing`
builds "commercial pricing CONTRADICTED, budget-owner SUPPORTED, commercial approved and
unreframed" without ever submitting a reframe, which is exactly journeys.md §1.10's opening state.

Before this fix, three separate ordinary `get_next` calls in this state all recommended
`FRAME`/`REFRAME` on COMMERCIAL, never `PROCEED_TO_BRIEF` -- see `runs/DRIFT.md` #7 for that full
write-up (kept for history, not deleted, per this repo's own practice of recording what was wrong
and why). This test keeps one quick check of that unchanged default behaviour (`request` omitted
still recommends `FRAME`/`REFRAME`) before demonstrating that the explicit ask opens the front
door -- the fix is additive, not a change to what `get_next` recommends by default.
"""

from __future__ import annotations

import time

from evals.recipes import (
    COMMERCIAL, COMMERCIAL_BUDGET_ASSUMPTION, COMMERCIAL_PRICING_ASSUMPTION, PROBLEM,
    PROBLEM_ASSUMPTION, PROBLEM_CLAIM, ROLE_LABEL, SOLUTION, SOLUTION_ASSUMPTION, SOLUTION_CLAIM,
    PricingSetupScenario, rule_out_pricing,
)
from evals.scenario import Fact
from harness.browser import FounderBrowser
from harness.driver import FounderAgentDriver, ProtocolError
from harness.evidence import finalize_run
from harness.steps import Recorder

GOING_AHEAD_SENTENCE = ("The one person I asked was firmly against annual upfront pricing, but I "
                         "think a larger customer buys differently -- I'm going ahead to find out.")


def _capture_refusal(recorder: Recorder, step_name: str, err: ProtocolError) -> None:
    """Mirrors S-007's own `_capture_refusal` (evals/test_s007_hostile_wire.py): stashes
    {rule, problem, remedy} as captured_text so ORI-R1/GUI-R1 (harness/rubric.py's
    `_agent_refusal_checks`) can score this refusal on its own terms."""
    with recorder.step(step_name, party="agent", kind="assert") as h:
        h.capture_text("rule", err.rule or "")
        h.capture_text("problem", err.problem or "")
        h.capture_text("remedy", err.remedy or "")
        h.record_assert("an actionable {rule, problem, remedy}",
                         {"rule": err.rule, "problem": err.problem, "remedy": err.remedy})


class S003GoingAhead(PricingSetupScenario):
    name = "S-003 going ahead anyway"
    slug = "s003-going-ahead"

    # This scenario never reframes -- these hooks exist only to satisfy PricingSetupScenario's
    # abstract contract and must never actually be called.
    def reframe_statement(self, stage: str) -> str:
        raise AssertionError("S-003 must never reframe -- that is S-002's scenario")

    def reframe_rationale(self, stage: str) -> str:
        raise AssertionError("S-003 must never reframe -- that is S-002's scenario")

    def brief_payload(self, context) -> dict:
        return {
            "findings": [
                "Payroll managers handle exceptions themselves, monthly (1 of 1 respondents).",
                "A tool that flags and routes exceptions would get used (1 of 1 respondents).",
                "Someone in the payroll organisation owns a budget for this (1 of 1 respondents).",
            ],
            "openDecisions": [],
        }

    def facts(self) -> dict[str, Fact]:
        return {
            "problem_statement": Fact(text=PROBLEM_CLAIM, kind="statement",
                                       hops=["agent_echo", "stage_screen", "brief"]),
            "solution_statement": Fact(text=SOLUTION_CLAIM, kind="statement",
                                        hops=["agent_echo", "stage_screen", "brief"]),
            # Unlike S-002, this claim is never replaced -- it survives, unreframed, all the way
            # to the brief (journeys.md §1.10 opens from exactly this: ruled out, not changed).
            "commercial_claim": Fact(text="$30 a seat per month, billed annually upfront.",
                                      kind="statement", hops=["agent_echo", "stage_screen", "brief"]),
            "role_label": Fact(text=ROLE_LABEL, kind="role",
                                hops=["agent_echo", "stage_screen", "invite_screen"]),
            "assumption_problem": Fact(text=PROBLEM_ASSUMPTION, kind="assumption",
                                        hops=["agent_echo", "stage_screen", "interpret_context", "brief"]),
            "assumption_solution": Fact(text=SOLUTION_ASSUMPTION, kind="assumption",
                                         hops=["agent_echo", "stage_screen", "interpret_context", "brief"]),
            "assumption_budget": Fact(text=COMMERCIAL_BUDGET_ASSUMPTION, kind="assumption",
                                       hops=["agent_echo", "stage_screen", "interpret_context", "brief"]),
            # The disproved deal-breaker -- still applying, still on the card, and now reaching the
            # brief for real (unlike S-002, where the reframe supersedes it before any brief exists).
            "assumption_pricing": Fact(text=COMMERCIAL_PRICING_ASSUMPTION, kind="assumption",
                                        hops=["agent_echo", "stage_screen", "interpret_context", "brief"]),
            # The founder's own sentence, written only because A9 demanded it -- traced all the way
            # to the one place it is meant to render: the top of the brief, verbatim, in their words.
            "going_ahead_sentence": Fact(text=GOING_AHEAD_SENTENCE, kind="statement", hops=["brief"]),
        }


def test_s003_going_ahead(stack, run_dir, browser):
    recorder = Recorder(run_dir)
    scenario = S003GoingAhead()
    cloud_base = f"http://localhost:{stack.cloud_port}"
    founder_web_base = f"http://localhost:{stack.web_port}/p"

    driver = FounderAgentDriver(cloud_base, recorder, scenario)
    passed = False
    started = time.monotonic()
    founder_context = browser.new_context()
    try:
        founder_page = founder_context.new_page()
        founder = FounderBrowser(founder_page, founder_web_base, recorder, get_state=driver.get_state)

        setup = rule_out_pricing(driver, founder, browser, recorder, scenario)
        project_id = setup.project_id

        # journeys.md §1.10 opens exactly here: "read *ruled out* and asked for the brief anyway."
        # Show it on the stage screen before touching anything else.
        founder.open_stage_evidence(project_id, COMMERCIAL)
        with recorder.step("the commercial card shows pricing ruled out, still approved, unreframed",
                            party="founder", kind="assert") as h:
            card_text = founder_page.locator(".card.openc").first.inner_text()
            state = driver.get_state(project_id)
            commercial_state = next(s for s in state["stages"] if s["stage"] == COMMERCIAL)
            h.record_assert("card mentions 'Ruled out'; stage approved with need REFRAME",
                             {"card_text": card_text, "commercial_state": commercial_state})
            if "ruled out" not in card_text.lower():
                h.fail(f"expected the commercial card to show pricing ruled out, got: {card_text!r}")
                raise AssertionError(h.error)
            if not commercial_state["approved"] or commercial_state["need"] != "REFRAME":
                h.fail(f"expected COMMERCIAL approved with need REFRAME, got {commercial_state}")
                raise AssertionError(h.error)

        # The fix is additive: the ordinary recommendation (no `request`) is unchanged -- still
        # FRAME/REFRAME on COMMERCIAL -- while pricing sits contradicted and unreframed.
        with recorder.step("the ordinary recommendation is unchanged: still FRAME/REFRAME on COMMERCIAL",
                            party="agent", kind="assert") as h:
            ordinary = driver.get_next()
            h.record_assert("action FRAME, reason REFRAME (unchanged default)", ordinary)
            is_reframe_action = (ordinary.get("kind") == "action" and ordinary.get("action") == "FRAME"
                                  and (ordinary.get("detail") or {}).get("reason") == "REFRAME")
            if not is_reframe_action:
                h.fail(f"expected the unchanged FRAME/REFRAME default, got {ordinary}")
                raise AssertionError(h.error)

        # journeys.md §1.10: "the founder... asks their agent for the brief anyway." The founder's
        # own ask, not a change in what get_next would otherwise recommend -- driven explicitly by
        # this scenario's own script (harness/driver.py's `get_next` docstring: request stays
        # scenario-consulted, never automatic).
        issuance_id = recorder.new_interaction_id()
        with recorder.interaction("agent-cycle", issuance_id):
            with recorder.step("the founder asks their agent for the brief anyway",
                                party="agent", kind="assert") as h:
                brief_request = driver.get_next(request="brief")
                h.record_assert("action PROCEED_TO_BRIEF, issued past the REFRAME focus", brief_request)
                if not (brief_request.get("kind") == "action" and brief_request.get("action") == "PROCEED_TO_BRIEF"):
                    h.fail(f"expected PROCEED_TO_BRIEF from request=brief, got {brief_request}")
                    raise AssertionError(h.error)
            token = brief_request["token"]
            context = {h_name: driver.get_context(token, h_name) for h_name in brief_request.get("context") or []}

        # journeys.md §1.10: "The agent checks one thing before it writes a word." A9's
        # warn-don't-block: the first submission omits `goingAhead` and must be refused, with a
        # remedy that would tell a lost agent what to do next -- not just restate the problem.
        with recorder.interaction("agent-refusal"):
            payload_without = scenario.brief_payload(context)
            payload_without.pop("goingAhead", None)
            try:
                driver.submit_with_recovery(token, payload_without, "PROCEED_TO_BRIEF",
                                             "PROCEED_TO_BRIEF (no goingAhead)")
                raise AssertionError("expected an A9 refusal for omitting goingAhead while pricing "
                                      "is CONTRADICTED")
            except ProtocolError as err:
                _capture_refusal(recorder, "PROCEED_TO_BRIEF without goingAhead is refused (A9)", err)
                if err.rule != "A9":
                    raise AssertionError(f"expected rule A9, got {err.rule!r}: {err.problem!r}")
                remedy = (err.remedy or "").strip()
                if len(remedy.split()) < 3:
                    raise AssertionError(f"expected an actionable, sentence-shaped remedy, got {remedy!r}")
                lowered = remedy.lower()
                if "goingahead" not in lowered.replace(" ", "") or "sentence" not in lowered:
                    raise AssertionError(
                        f"remedy doesn't tell a lost agent what to do (write a sentence, set "
                        f"goingAhead): {remedy!r}")

        # "Token survives" (A9's contract, unchanged): the refusal never touched the aggregate, so
        # the SAME token -- not a freshly minted one -- is resubmitted with the founder's own
        # sentence.
        with recorder.interaction("agent-cycle", issuance_id):
            payload_with = scenario.brief_payload(context)
            payload_with["goingAhead"] = GOING_AHEAD_SENTENCE
            result = driver.submit_with_recovery(token, payload_with, "PROCEED_TO_BRIEF",
                                                  "PROCEED_TO_BRIEF (goingAhead)")
            with recorder.step("the project reaches READY_TO_BUILD", party="agent", kind="assert") as h:
                h.record_assert("state READY_TO_BUILD", result)
                if result.get("state") != "READY_TO_BUILD":
                    h.fail(f"expected state READY_TO_BUILD, got {result}")
                    raise AssertionError(h.error)

        founder.open_brief(project_id)
        with recorder.step("the brief renders GOING AHEAD ANYWAY first, pricing under said-no-to, "
                            "never taking-on-faith", party="founder", kind="assert") as h:
            first_child_class = founder_page.locator(".brief > *").first.get_attribute("class")
            goahead_text = founder_page.locator(".goahead p").inner_text()
            said_no = founder_page.locator(".blist.saidno li").all_inner_texts()
            faith = founder_page.locator(".blist.faith li").all_inner_texts()
            h.record_assert("goahead first, pricing in said-no-to, never in taking-on-faith",
                             {"first_child_class": first_child_class, "goahead_text": goahead_text,
                              "said_no": said_no, "faith": faith})
            if first_child_class != "goahead":
                h.fail(f"expected the GOING AHEAD ANYWAY box to render first, got class={first_child_class!r}")
                raise AssertionError(h.error)
            if goahead_text.strip() != GOING_AHEAD_SENTENCE:
                h.fail(f"expected the founder's own sentence in the box, got {goahead_text!r}")
                raise AssertionError(h.error)
            if not any(COMMERCIAL_PRICING_ASSUMPTION in line for line in said_no):
                h.fail(f"expected the disproved pricing belief under said-no-to, got {said_no}")
                raise AssertionError(h.error)
            if any(COMMERCIAL_PRICING_ASSUMPTION in line for line in faith):
                h.fail("the disproved pricing belief leaked into taking-on-faith -- never blurred "
                       "(journeys.md §1.10)")
                raise AssertionError(h.error)

        passed = True
    finally:
        founder_context.close()
        duration = time.monotonic() - started
        finalize_run(run_dir, scenario=scenario, passed=passed,
                     failed_step=recorder.failed_step, duration_s=duration)
        print(f"\nrun bundle: {run_dir}")
