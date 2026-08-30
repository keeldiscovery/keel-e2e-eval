"""S-001, the smoke (T013): every party, every handoff reason, every founder/participant screen,
the URL contract, in one discovery.

**The real choreography, not the plan's** (see harness/driver.py's module docstring for the full
derivation from `NextRecommendation.compute`): CREATE frames PROBLEM as a side effect, so the
opening pass only ever issues FRAME for SOLUTION and COMMERCIAL; then roles are introduced once,
project-wide, at PROBLEM's first REVIEW cycle; and each stage runs its own
assumptions -> REVIEW -> approve cycle in turn.

**Rewritten 2026-08-30 for the invite gate (founder-experience design §6; keel-cloud commits
8b13d04/ff1ed48): approve all three, then invite -- once, combined.** `Project.needs` no longer
offers `INVITE` for any stage until every framed stage is approved, so this scenario now finishes
approving PROBLEM, SOLUTION and COMMERCIAL *before* the People screen is ever visited (the standing
assertion, `evals.recipes.assert_invite_gate_closed`, pins that no `INVITE` need and no invitable
role surface in between). And since this scenario uses one role (`ROLE_LABEL`) across all three
stages, `Project.invite`/`linkFor` freezes every open belief for that role into the *first*
invitation sent to it -- so, once the gate opens, one combined invitation carries problem, solution
and commercial together (design §5's own mockup: "A PAYROLL MANAGER... can settle 4 beliefs across
2 cards"), one respondent answers all three in one sitting, and one `INTERPRET` settles all three
beliefs in one commit. `harness.driver.FounderAgentDriver.advance_until_handoff` chains straight
through every agent-only action in between, so from this test's vantage point the whole discovery
is: three REVIEW/approve cycles, one INVITE/invite/WAITING/answer cycle, done.

This module is also where policy v3's "every door must open" rule (evals/policy.py's judgement
call 4) gets its one live demonstration: `PROBLEM`'s own `INTRODUCE_ASSUMPTIONS` commit is driven
by hand (not through `advance_until_handoff`) so the test can read that commit's own `display`
sentence, pull the URL it carries out *verbatim*, and prove the browser actually renders it via
`FounderBrowser.follow_display_url` -- never a URL this harness reconstructs itself.
"""

from __future__ import annotations

import re
import time

from harness.browser import FounderBrowser, ParticipantBrowser
from harness.driver import FounderAgentDriver
from harness.evidence import finalize_run
from harness.steps import Recorder
from evals.recipes import assert_invite_gate_closed
from evals.scenario import Fact, Scenario, find_role

ROLE_LABEL = "Payroll Ops Manager"
STAGES = ["PROBLEM", "SOLUTION", "COMMERCIAL"]
PROJECT_NAME = "Payroll Exception Radar"

_URL_RE = re.compile(r"https?://\S+")


class S001Smoke(Scenario):
    name = "S-001 smoke"
    slug = "s001-smoke"

    _frame_statements = {
        "SOLUTION": "An automated tool that flags and routes payroll exceptions for a payroll "
                    "manager to resolve, instead of them finding exceptions by hand.",
        "COMMERCIAL": "Payroll Ops Managers can get budget approved to pay for a tool that cuts "
                      "down exception-chasing time.",
    }

    _assumptions = {
        "PROBLEM": {
            "statement": "Payroll managers spend multiple hours every month manually chasing "
                         "down payroll exceptions.",
            "heading": "Manual exception chasing",
            "ask": "Tell me about the last time you had to chase down a payroll exception by hand.",
            "probes": ["About how long did that take?", "How often does something like that happen?"],
            "disconfirming": "Has there been a month where you had no exceptions to chase down at all?",
        },
        "SOLUTION": {
            "statement": "A tool that automatically flags and routes payroll exceptions would "
                         "actually get used by payroll managers.",
            "heading": "Automated flagging gets used",
            "ask": "Tell me about the last tool or spreadsheet you tried to use to track payroll "
                   "exceptions.",
            "probes": ["What made you keep using it, or stop?"],
            "disconfirming": "Have you tried something like this before and stopped using it?",
        },
        "COMMERCIAL": {
            "statement": "Payroll Ops Managers can get budget approved for a tool that reduces "
                         "exception-chasing time.",
            "heading": "Budget approval is workable",
            "ask": "Tell me about the last time you got budget approved for a payroll-related tool.",
            "probes": ["Who had to sign off on it?", "How long did approval take?"],
            "disconfirming": "Has a payroll tool purchase you wanted ever been turned down?",
        },
    }

    _answers = {
        "PROBLEM": "Yeah -- just last month I spent about three hours on a Friday afternoon "
                   "manually tracking down four different payroll exceptions across two "
                   "departments before I could run final payroll.",
        "SOLUTION": "I tried a shared spreadsheet to log exceptions last quarter, but people "
                    "kept forgetting to update it. Something that automatically flagged and "
                    "routed them would definitely get used, since nothing catches this early "
                    "right now.",
        "COMMERCIAL": "Last year I got budget approved for a scheduling tool in about two weeks "
                      "-- my director just needed a one-pager showing time saved, so getting "
                      "sign-off for something like this wouldn't be hard.",
    }

    COMBINED_PERSON = "Jordan Casey"
    COMBINED_ABOUT_LINE = ("A few quick questions about how payroll exception handling goes day to "
                            "day, the tools you've tried, and how budget gets approved on your team.")

    def project_name(self) -> str:
        return PROJECT_NAME

    def problem_statement(self) -> str:
        return ("Payroll managers at mid-size companies lose hours every month manually chasing "
                "down payroll exceptions.")

    def frame_statement(self, stage: str) -> str:
        return self._frame_statements[stage]

    def roles_payload(self) -> list[dict]:
        return [{
            "label": ROLE_LABEL,
            "roleType": "MANAGER",
            "about": "How payroll exception handling works day to day on their team",
        }]

    def assumptions_payload(self, stage: str, roles: list[dict]) -> list[dict]:
        role_id = find_role(roles, ROLE_LABEL)["id"]
        spec = self._assumptions[stage]
        return [{
            "statement": spec["statement"],
            "heading": spec["heading"],
            "stage": stage,
            "risk": "LOAD_BEARING",
            "askedOf": role_id,
            "question": {
                "ask": spec["ask"],
                "probes": spec["probes"],
                "disconfirming": spec["disconfirming"],
            },
        }]

    def interpret_payload(self, stage: str, response: dict) -> list[dict]:
        per_answer = []
        for answer in response["answers"]:
            if not answer.get("text"):
                continue
            per_answer.append({
                "assumptionId": answer["assumptionId"],
                "evidence": [{
                    "statement": answer["text"],
                    "claimType": "PAST_BEHAVIOR",
                    "stance": "SUPPORTS",
                }],
            })
        return per_answer

    def brief_payload(self, context) -> dict:
        return {
            "findings": [
                "Payroll managers do spend multiple hours a month manually chasing payroll "
                "exceptions (1 of 1 respondents).",
                "A tool that automatically flags and routes exceptions would get used (1 of 1 "
                "respondents).",
                "Payroll Ops Managers can get budget approved for a tool like this (1 of 1 "
                "respondents).",
            ],
            "openDecisions": [],
            # goingAhead deliberately omitted: nothing is CONTRADICTED (instruction content for
            # PROCEED_TO_BRIEF -- "if nothing is CONTRADICTED, do not write goingAhead at all").
        }

    def about_line(self, stage: str) -> str:
        return self.COMBINED_ABOUT_LINE

    def person_name(self, stage: str) -> str:
        return self.COMBINED_PERSON

    def participant_answer(self, stage: str) -> str:
        return self._answers[stage]

    # ---------------------------------------------------------------------------- fact registry

    def facts(self) -> dict[str, Fact]:
        """002-eval-scoring, US2 (T011); extended 2026-08-30 for the founder voice (policy v3):
        every founder- or participant-entered text S-001 cares about tracing hop-by-hop, per design
        §3's table plus the new `recorded` hop (a fact submitted appears in the server's own
        played-back commit, verbatim). `role_label` is declared once (the same role is reused
        across all three stages, and now the same invitation too); the rest are declared per stage.
        The `assumption_*`/`heading_*` facts' `brief` hop is expected to be waived (policy's
        `brief-findings-summarize`), not to pass verbatim -- `brief_payload` above writes
        founder-authored summary sentences with respondent counts, not the raw statement.
        `about_line`/`answer_*` are no longer per-stage: one combined invitation, one about-line,
        one participant page.
        """
        facts: dict[str, Fact] = {
            "project_name": Fact(
                text=PROJECT_NAME, kind="statement",
                hops=["recorded", "stage_screen"],
                absent_hops=["agent_echo", "invite_screen", "participant_page", "interpret_context", "brief"],
            ),
            "problem_statement": Fact(
                text=self.problem_statement(), kind="statement",
                hops=["agent_echo", "stage_screen", "brief", "recorded"],
                absent_hops=["invite_screen", "participant_page", "interpret_context"],
            ),
            "role_label": Fact(
                text=ROLE_LABEL, kind="role",
                hops=["agent_echo", "stage_screen", "invite_screen", "recorded"],
                absent_hops=["participant_page", "interpret_context", "brief"],
            ),
            "combined_about_line": Fact(
                text=self.COMBINED_ABOUT_LINE, kind="about_line",
                hops=["invite_screen", "participant_page"],
                absent_hops=["agent_echo", "stage_screen", "interpret_context", "brief", "recorded"],
            ),
        }
        for stage in ("SOLUTION", "COMMERCIAL"):
            facts[f"{stage.lower()}_frame"] = Fact(
                text=self.frame_statement(stage), kind="statement",
                hops=["agent_echo", "stage_screen", "brief", "recorded"],
                absent_hops=["invite_screen", "participant_page", "interpret_context"],
            )
        for stage in STAGES:
            lower = stage.lower()
            facts[f"assumption_{lower}"] = Fact(
                text=self._assumptions[stage]["statement"], kind="assumption",
                hops=["agent_echo", "stage_screen", "interpret_context", "brief", "recorded"],
                absent_hops=["invite_screen", "participant_page"],
            )
            facts[f"heading_{lower}"] = Fact(
                text=self._assumptions[stage]["heading"], kind="assumption",
                hops=["stage_screen", "recorded"],
                absent_hops=["agent_echo", "invite_screen", "participant_page", "interpret_context", "brief"],
            )
            facts[f"answer_{lower}"] = Fact(
                text=self.participant_answer(stage), kind="answer",
                hops=["interpret_context", "stage_screen"],
                absent_hops=["agent_echo", "invite_screen", "participant_page", "brief", "recorded"],
            )
            # translate.ts's betStatus: an approved, evidence-SUPPORTED stage reads "Holding up"
            # -- S-001 answers supportively throughout, so every stage should land here.
            facts[f"interpretation_{lower}"] = Fact(
                text="Holding up", kind="interpretation",
                hops=["stage_screen"],
                absent_hops=["agent_echo", "invite_screen", "participant_page", "interpret_context", "brief", "recorded"],
            )
        return facts


def test_s001_smoke(stack, run_dir, browser):
    recorder = Recorder(run_dir)
    scenario = S001Smoke()
    cloud_base = f"http://localhost:{stack.cloud_port}"
    founder_web_base = f"http://localhost:{stack.web_port}/p"

    driver = FounderAgentDriver(cloud_base, recorder, scenario)
    passed = False
    started = time.monotonic()
    founder_context = browser.new_context()
    try:
        driver.load_skill(stack.skill_md_path)
        driver.check_mcp_reachable()

        founder_page = founder_context.new_page()
        founder = FounderBrowser(founder_page, founder_web_base, recorder, get_state=driver.get_state)

        # CREATE (name required), FRAME x2, INTRODUCE_ROLES -- agent-only, nothing renders yet.
        for _ in range(4):
            driver.advance_one()
        project_id = driver.project_id
        assert project_id

        # Policy v3's "every door must open" rule, demonstrated live (module docstring): drive
        # PROBLEM's own INTRODUCE_ASSUMPTIONS commit by hand (the same manually-replicated-cycle
        # pattern test_s003_going_ahead.py already uses for its own request=brief call) so this
        # test can read the commit's own `display` sentence and pull the URL it carries verbatim.
        with recorder.interaction("agent-cycle"):
            issuance = driver.get_next()
            assert (issuance["kind"] == "action" and issuance["action"] == "INTRODUCE_ASSUMPTIONS"
                    and issuance["detail"]["stage"] == "PROBLEM"), issuance
            token = issuance["token"]
            context = {h: driver.get_context(token, h) for h in issuance.get("context") or []}
            payload = scenario.build_payload("INTRODUCE_ASSUMPTIONS", issuance.get("detail") or {}, context)
            result = driver.submit_with_recovery(token, payload, "INTRODUCE_ASSUMPTIONS",
                                                  "INTRODUCE_ASSUMPTIONS (PROBLEM)")

        with recorder.step("the commit's own display sentence carries a resolvable door",
                            party="agent", kind="assert") as h:
            display = result.get("display") or ""
            match = _URL_RE.search(display)
            h.record_assert("display names a URL", display)
            if not match:
                h.fail(f"expected the INTRODUCE_ASSUMPTIONS commit's display to carry a URL, got {display!r}")
                raise AssertionError(h.error)
        door_url = match.group(0)

        handoff = driver.advance_until_handoff()
        assert handoff is not None and handoff["kind"] == "handoff"
        assert handoff["reason"] == "REVIEW", handoff
        assert handoff["detail"]["stage"] == "PROBLEM", handoff
        with recorder.step("the commit's own predicted door matches the handoff's own display",
                            party="agent", kind="assert") as h:
            h.record_assert(door_url, handoff.get("display"))
            if door_url not in (handoff.get("display") or ""):
                h.fail(f"expected the handoff's display to carry the same door {door_url!r}, "
                       f"got {handoff.get('display')!r}")
                raise AssertionError(h.error)

        founder.follow_display_url(door_url, project_id)
        founder.approve_current_stage("PROBLEM")

        # The invite gate's standing assertion (founder-experience design §6): closed while
        # SOLUTION/COMMERCIAL are still framed and unapproved.
        assert_invite_gate_closed(driver)

        for stage in ("SOLUTION", "COMMERCIAL"):
            handoff = driver.advance_until_handoff()
            assert handoff is not None and handoff["reason"] == "REVIEW", (stage, handoff)
            assert handoff["detail"]["stage"] == stage, (stage, handoff)
            founder.open_stage(project_id, stage)
            founder.approve_current_stage(stage)
            if stage == "SOLUTION":
                assert_invite_gate_closed(driver)

        # The gate is open now -- one combined invitation, carrying all three cards, is next.
        handoff = driver.advance_until_handoff()
        assert handoff is not None and handoff["reason"] == "INVITE", handoff

        # founder-experience design §5: both old screen names route to the identical merged People
        # screen -- assert that once, here, where the INVITE handoff first makes it relevant.
        founder.open_invite(project_id)
        invite_heading = founder_page.locator(".card.openc h1").first.inner_text()
        founder.open_people(project_id)
        people_heading = founder_page.locator(".card.openc h1").first.inner_text()
        with recorder.step("both /invite and /invitations render the identical People screen",
                            party="founder", kind="assert") as h:
            h.record_assert("same compose heading", {"invite": invite_heading, "people": people_heading})
            if invite_heading != people_heading:
                h.fail(f"/invite and /invitations rendered different screens: "
                       f"{invite_heading!r} vs {people_heading!r}")
                raise AssertionError(h.error)

        link = founder.send_invite(ROLE_LABEL, scenario.person_name("PROBLEM"), scenario.about_line("PROBLEM"))

        handoff = driver.advance_until_handoff()
        assert handoff is not None and handoff["reason"] == "WAITING", handoff

        participant_context = browser.new_context()
        try:
            participant_page = participant_context.new_page()
            participant = ParticipantBrowser(participant_page, recorder)
            participant.open(link)
            participant.start()
            participant.answer([scenario.participant_answer(stage) for stage in STAGES])
            participant.submit()
        finally:
            participant_context.close()

        # Acceptance scenario #3: the participant answering in the browser is what makes the
        # founder-agent's next poll advance -- the interleaving of a real discovery.
        with recorder.step(
                "founder-agent's next poll advances past the combined WAITING handoff",
                party="agent", kind="assert") as h:
            handoff = driver.advance_until_handoff()
            observed = handoff.get("reason") if handoff else "PROCEED_TO_BRIEF"
            h.record_assert("not WAITING", observed)
            if observed == "WAITING":
                h.fail(f"still WAITING after the combined participant answered: {handoff}")
                raise AssertionError(h.error)

        assert handoff is None, f"expected the project to be finished (brief proposed), got {handoff}"

        # FID hop capture (T012): the participant's verbatim answer only ever renders on the stage
        # screen inside a belief's (collapsed-by-default) testimony drilldown, which only exists
        # once evidence has been interpreted -- one combined INTERPRET settled all three, so all
        # three stages need their own second visit now.
        for stage in STAGES:
            founder.open_stage_evidence(project_id, stage)

        founder.open_overview(project_id)
        with recorder.step("verdicts moved on the overview", party="founder", kind="assert") as h:
            cards = founder_page.locator(".card:not(.openc)")
            claim_texts = cards.locator(".claim").all_inner_texts()
            h.record_assert("at least one stage shows a claim", claim_texts)
            if not any(claim_texts):
                h.fail("expected at least one framed stage claim on the overview")
                raise AssertionError(h.error)

        founder.open_brief(project_id)
        with recorder.step("brief renders with findings", party="founder", kind="assert") as h:
            findings = founder_page.locator(".blist.learned li").all_inner_texts()
            h.record_assert("3 findings", findings)
            if len(findings) != 3:
                h.fail(f"expected 3 findings on the brief, got {findings}")
                raise AssertionError(h.error)

        passed = True
    finally:
        founder_context.close()
        duration = time.monotonic() - started
        finalize_run(run_dir, scenario=scenario, passed=passed,
                     failed_step=recorder.failed_step, duration_s=duration)
        print(f"\nrun bundle: {run_dir}")
