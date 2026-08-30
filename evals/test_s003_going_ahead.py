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

**This journey moment turns out to be unreachable through the shipped v2 agent protocol --
confirmed live, not assumed.** `evals/recipes.py`'s module docstring has the full derivation; the
short version:

`NextRecommendation.compute` recommends `PROCEED_TO_BRIEF` in exactly one branch,
`Project.currentFocus().isEmpty()`. `currentFocus()` gives a stage needing `REFRAME` *absolute*
priority over every other need, including no need at all (`Project.needs`: the
`anyContradictedLoadBearing` check runs before `anyUninvited`/`anyPending`/`anyOpenRemains`, and a
`REFRAME` focus wins the whole-project scan outright). A commercial stage with a `CONTRADICTED`,
`LOAD_BEARING`, applying, approved assumption -- exactly the state journeys.md §1.10 opens from --
therefore keeps `currentFocus()` non-empty **forever**, until that stage is reframed. Since a token
is only ever minted for the action `get_next` itself just recommended
(`AgentProtocolService.issue`/`submit`; there is no "give me a token for `PROCEED_TO_BRIEF`
specifically" call), **an agent that only ever acts on `get_next`'s own recommendation can never
submit `PROCEED_TO_BRIEF` in this state at all** -- not "refused with A9", genuinely never offered
a token for it. journeys.md §1.10's entire warn-then-accept conversation, and the "ask for the
brief anyway" moment it hinges on, has no protocol-legal entry point.

Corroborating evidence: keel-cloud's own `AgentProtocolFlowTest`
(`src/test/java/.../protocol/AgentProtocolFlowTest.java`) tests A9's refusal-then-accept behaviour
at all only via a test-only `mintDirect(AgentAction.PROCEED_TO_BRIEF, ...)` helper that mints the
token directly, bypassing `get_next` entirely -- not a call any real agent or MCP client has
access to. That test proves A9's *domain rule* is correct; it does not prove any real client can
ever reach it, and this scenario's own live run shows that, through the protocol this driver
actually speaks, none can.

**What this test does, honestly (design §6, discovery-honesty pass)**: builds the exact state
journeys.md §1.10 opens from (pricing `CONTRADICTED`, commercial approved, unreframed, problem and
solution supported), shows it on the stage screen ("Ruled out"), then demonstrates -- three
separate `get_next` calls, not one, so a transient blip cannot be mistaken for the finding -- that
`PROCEED_TO_BRIEF` is never offered. It does not reach a brief, does not fabricate a refusal that
never happened, and does not silently substitute the pricing-pivot flow (that is S-002's own
scenario, not this one's escape hatch). The scenario's own `passed` flag is `False`: the journey
moment it exists to walk cannot be walked, and the harness's completion gate is the honest way to
say so in the run's score. See `runs/DRIFT.md` #7 for the full write-up -- this is the eval set's
single most significant finding.
"""

from __future__ import annotations

import time

from evals.recipes import COMMERCIAL, COMMERCIAL_PRICING_ASSUMPTION, PricingSetupScenario, rule_out_pricing
from harness.browser import FounderBrowser
from harness.driver import FounderAgentDriver
from harness.evidence import finalize_run
from harness.steps import Recorder


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
        # Only ever used if a future fix makes PROCEED_TO_BRIEF reachable while pricing stays
        # CONTRADICTED (see `_walk_going_ahead_conversation`) -- goingAhead is added/removed by
        # the caller per A9's two directions.
        return {
            "findings": [
                "Payroll managers handle exceptions themselves, monthly (1 of 1 respondents).",
                "A tool that flags and routes exceptions would get used (1 of 1 respondents).",
                "Someone in the payroll organisation owns a budget for this (1 of 1 respondents).",
            ],
            "openDecisions": [],
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

        # journeys.md §1.10: "Before I write anything..." -- the agent would ask for the brief
        # here. Demonstrate, three separate calls, that PROCEED_TO_BRIEF is never offered.
        with recorder.step("PROCEED_TO_BRIEF is never offered while pricing sits contradicted and "
                            "unreframed (checked three times, not once)", party="agent", kind="assert") as h:
            observations = [setup.peek, driver.get_next(), driver.get_next()]
            h.record_assert("every call recommends FRAME/REFRAME on COMMERCIAL, never PROCEED_TO_BRIEF",
                             observations)
            for obs in observations:
                is_reframe_action = (obs.get("kind") == "action" and obs.get("action") == "FRAME"
                                      and (obs.get("detail") or {}).get("reason") == "REFRAME")
                reached_brief = obs.get("kind") == "action" and obs.get("action") == "PROCEED_TO_BRIEF"
                if reached_brief:
                    # If a future keel-cloud fix makes this reachable, take the win: walk the A9
                    # conversation for real instead of failing the block-detection assertion.
                    recorder.note("PROCEED_TO_BRIEF was reachable after all -- prior finding resolved; "
                                  "walking the A9 refusal-then-accept conversation for real", party="stack")
                    _walk_going_ahead_conversation(driver, scenario, founder, founder_page, project_id, recorder)
                    passed = True
                    break
                if not is_reframe_action:
                    h.fail(f"expected the documented FRAME/REFRAME offer, got something else: {obs}")
                    raise AssertionError(h.error)
            else:
                # The documented, currently-live finding: no path to PROCEED_TO_BRIEF exists here.
                recorder.note(
                    "CONFIRMED: PROCEED_TO_BRIEF is unreachable while a load-bearing CONTRADICTED "
                    "assumption sits on an approved, unreframed stage -- NextRecommendation.compute "
                    "recommends FRAME/REFRAME on every call instead; there is no protocol operation "
                    "that mints a token for an action other than the one get_next currently "
                    "recommends. See runs/DRIFT.md #7 and evals/recipes.py's module docstring.",
                    party="stack",
                )

        # `passed` stays False on the documented-block branch: the journey moment this scenario
        # exists to walk (the founder asks for the brief, is warned, writes the sentence, and sees
        # the GOING AHEAD ANYWAY box first) cannot be walked through the shipped protocol. That is
        # the finding, and the completion gate is the honest way to score it.
    finally:
        founder_context.close()
        duration = time.monotonic() - started
        finalize_run(run_dir, scenario=scenario, passed=passed,
                     failed_step=recorder.failed_step, duration_s=duration)
        print(f"\nrun bundle: {run_dir}")


def _walk_going_ahead_conversation(driver: FounderAgentDriver, scenario, founder: FounderBrowser,
                                    founder_page, project_id: str, recorder) -> None:
    """Only runs if a future fix makes PROCEED_TO_BRIEF reachable while pricing stays contradicted
    -- journeys.md §1.10's actual conversation, walked for real: first submit omits `goingAhead`
    and must be refused (A9); the retry carries the founder's own sentence; the brief renders the
    GOING AHEAD ANYWAY box first, with pricing filed under "what the evidence said no to"."""
    from harness.driver import ProtocolError

    going_ahead_sentence = ("The one person I asked was firmly against annual upfront pricing, but "
                             "I think a larger customer buys differently -- I'm going ahead to find out.")

    response = driver.get_next()
    assert response["action"] == "PROCEED_TO_BRIEF", response
    token = response["token"]
    context = {h: driver.get_context(token, h) for h in response.get("context") or []}

    with recorder.step("PROCEED_TO_BRIEF without goingAhead is refused (A9)", party="agent", kind="assert") as h:
        payload_without = scenario.brief_payload(context)
        payload_without.pop("goingAhead", None)
        try:
            driver.submit_with_recovery(token, payload_without, "PROCEED_TO_BRIEF", "PROCEED_TO_BRIEF (no goingAhead)")
            h.fail("expected an A9 refusal for omitting goingAhead while pricing is CONTRADICTED")
            raise AssertionError(h.error)
        except ProtocolError as err:
            h.record_assert("A9 refusal with an actionable remedy", {"rule": err.rule, "remedy": err.remedy})
            if err.rule != "A9" or not err.remedy:
                h.fail(f"expected an actionable A9 refusal, got rule={err.rule} remedy={err.remedy}")
                raise AssertionError(h.error)

    retry = driver.get_next()
    assert retry["action"] == "PROCEED_TO_BRIEF", retry
    payload_with = scenario.brief_payload(context)
    payload_with["goingAhead"] = going_ahead_sentence
    driver.submit_with_recovery(retry["token"], payload_with, "PROCEED_TO_BRIEF", "PROCEED_TO_BRIEF (goingAhead)")

    founder.open_brief(project_id)
    with recorder.step("the brief renders GOING AHEAD ANYWAY first, pricing under said-no-to",
                        party="founder", kind="assert") as h:
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
        if goahead_text.strip() != going_ahead_sentence:
            h.fail(f"expected the founder's own sentence in the box, got {goahead_text!r}")
            raise AssertionError(h.error)
        if not any(COMMERCIAL_PRICING_ASSUMPTION in line for line in said_no):
            h.fail(f"expected the disproved pricing belief under said-no-to, got {said_no}")
            raise AssertionError(h.error)
        if any(COMMERCIAL_PRICING_ASSUMPTION in line for line in faith):
            h.fail("the disproved pricing belief leaked into taking-on-faith -- never blurred (journeys.md §1.10)")
            raise AssertionError(h.error)
