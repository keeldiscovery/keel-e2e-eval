"""S-001, the smoke (T013): every party, every handoff reason, every founder/participant screen,
the URL contract, in one discovery.

**The real choreography, not the plan's** (see harness/driver.py's module docstring for the full
derivation from `NextRecommendation.compute`): CREATE frames PROBLEM as a side effect, so the
opening pass only ever issues FRAME for SOLUTION and COMMERCIAL; then roles are introduced once,
project-wide, at PROBLEM's first REVIEW cycle; and each stage runs its own
assumptions -> REVIEW -> approve -> INVITE -> participant -> WAITING -> INTERPRET cycle in turn --
three full cycles, not one shared invite at the end. `harness.driver.FounderAgentDriver.
advance_until_handoff` chains straight through every agent-only action, so from this test's
vantage point each cycle is just: expect REVIEW, approve; expect INVITE, invite; expect WAITING;
have the participant answer; advance again (which runs INTERPRET internally, and -- on the last
stage -- PROCEED_TO_BRIEF too, ending the loop with `None`).
"""

from __future__ import annotations

import time

from harness.browser import FounderBrowser, ParticipantBrowser
from harness.driver import FounderAgentDriver
from harness.evidence import finalize_run
from harness.steps import Recorder
from evals.scenario import Fact, Scenario, find_role

ROLE_LABEL = "Payroll Ops Manager"
STAGES = ["PROBLEM", "SOLUTION", "COMMERCIAL"]


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
            "ask": "Tell me about the last time you had to chase down a payroll exception by hand.",
            "probes": ["About how long did that take?", "How often does something like that happen?"],
            "disconfirming": "Has there been a month where you had no exceptions to chase down at all?",
        },
        "SOLUTION": {
            "statement": "A tool that automatically flags and routes payroll exceptions would "
                         "actually get used by payroll managers.",
            "ask": "Tell me about the last tool or spreadsheet you tried to use to track payroll "
                   "exceptions.",
            "probes": ["What made you keep using it, or stop?"],
            "disconfirming": "Have you tried something like this before and stopped using it?",
        },
        "COMMERCIAL": {
            "statement": "Payroll Ops Managers can get budget approved for a tool that reduces "
                         "exception-chasing time.",
            "ask": "Tell me about the last time you got budget approved for a payroll-related tool.",
            "probes": ["Who had to sign off on it?", "How long did approval take?"],
            "disconfirming": "Has a payroll tool purchase you wanted ever been turned down?",
        },
    }

    _about_lines = {
        "PROBLEM": "A few quick questions about how payroll exception handling goes day to day.",
        "SOLUTION": "A few quick questions about tools you've tried for tracking payroll exceptions.",
        "COMMERCIAL": "A few quick questions about how budget gets approved for tools on your team.",
    }

    _person_names = {
        "PROBLEM": "Jordan Casey",
        "SOLUTION": "Sam Rivera",
        "COMMERCIAL": "Taylor Brooks",
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
        return self._about_lines[stage]

    def person_name(self, stage: str) -> str:
        return self._person_names[stage]

    def participant_answer(self, stage: str) -> str:
        return self._answers[stage]

    # ---------------------------------------------------------------------------- fact registry

    def facts(self) -> dict[str, Fact]:
        """002-eval-scoring, US2 (T011): every founder- or participant-entered text S-001 cares
        about tracing hop-by-hop, per design §3's table. `role_label` is declared once (the same
        role is reused across all three stages); the rest are declared per stage. The
        `assumption_*` facts' `brief` hop is expected to be waived (policy's
        `brief-findings-summarize`), not to pass verbatim -- `brief_payload` above writes
        founder-authored summary sentences with respondent counts, not the raw statement.
        """
        facts: dict[str, Fact] = {
            "problem_statement": Fact(
                text=self.problem_statement(), kind="statement",
                hops=["agent_echo", "stage_screen", "brief"],
                absent_hops=["invite_screen", "participant_page", "interpret_context"],
            ),
            "role_label": Fact(
                text=ROLE_LABEL, kind="role",
                hops=["agent_echo", "stage_screen", "invite_screen"],
                absent_hops=["participant_page", "interpret_context", "brief"],
            ),
        }
        for stage in ("SOLUTION", "COMMERCIAL"):
            facts[f"{stage.lower()}_frame"] = Fact(
                text=self.frame_statement(stage), kind="statement",
                hops=["agent_echo", "stage_screen", "brief"],
                absent_hops=["invite_screen", "participant_page", "interpret_context"],
            )
        for stage in STAGES:
            lower = stage.lower()
            facts[f"assumption_{lower}"] = Fact(
                text=self._assumptions[stage]["statement"], kind="assumption",
                hops=["agent_echo", "stage_screen", "interpret_context", "brief"],
                absent_hops=["invite_screen", "participant_page"],
            )
            facts[f"about_line_{lower}"] = Fact(
                text=self.about_line(stage), kind="about_line",
                hops=["invite_screen", "participant_page"],
                absent_hops=["agent_echo", "stage_screen", "interpret_context", "brief"],
            )
            facts[f"answer_{lower}"] = Fact(
                text=self.participant_answer(stage), kind="answer",
                hops=["interpret_context", "stage_screen"],
                absent_hops=["agent_echo", "invite_screen", "participant_page", "brief"],
            )
            # translate.ts's betStatus: an approved, evidence-SUPPORTED stage reads "Holding up"
            # -- S-001 answers supportively throughout, so every stage should land here.
            facts[f"interpretation_{lower}"] = Fact(
                text="Holding up", kind="interpretation",
                hops=["stage_screen"],
                absent_hops=["agent_echo", "invite_screen", "participant_page", "interpret_context", "brief"],
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

        handoff = driver.advance_until_handoff()
        assert handoff is not None and handoff["kind"] == "handoff"
        assert handoff["reason"] == "REVIEW", handoff
        assert handoff["detail"]["stage"] == "PROBLEM", handoff
        project_id = driver.project_id
        assert project_id

        founder_page = founder_context.new_page()
        founder = FounderBrowser(founder_page, founder_web_base, recorder, get_state=driver.get_state)

        for stage in STAGES:
            assert handoff["reason"] == "REVIEW", (stage, handoff)
            assert handoff["detail"]["stage"] == stage, (stage, handoff)
            founder.open_stage(project_id, stage)
            founder.approve_current_stage(stage)

            handoff = driver.advance_until_handoff()
            assert handoff is not None and handoff["reason"] == "INVITE", (stage, handoff)
            founder.open_invite(project_id)
            link = founder.send_invite(ROLE_LABEL, scenario.person_name(stage),
                                        scenario.about_line(stage))

            handoff = driver.advance_until_handoff()
            assert handoff is not None and handoff["reason"] == "WAITING", (stage, handoff)

            participant_context = browser.new_context()
            try:
                participant_page = participant_context.new_page()
                participant = ParticipantBrowser(participant_page, recorder)
                participant.open(link)
                participant.start()
                participant.answer_all(scenario.participant_answer(stage))
                participant.submit()
            finally:
                participant_context.close()

            # Acceptance scenario #3: the participant answering in the browser is what makes the
            # founder-agent's next poll advance -- the interleaving of a real discovery.
            with recorder.step(
                    f"founder-agent's next poll advances past {stage}'s WAITING handoff",
                    party="agent", kind="assert") as h:
                handoff = driver.advance_until_handoff()
                observed = handoff.get("reason") if handoff else "PROCEED_TO_BRIEF"
                h.record_assert("not WAITING", observed)
                if observed == "WAITING":
                    h.fail(f"still WAITING after {stage}'s participant answered: {handoff}")
                    raise AssertionError(h.error)

            # FID hop capture (T012): the participant's verbatim answer only ever renders on the
            # stage screen inside a belief's (collapsed-by-default) testimony drilldown, which
            # only exists once evidence has been interpreted -- so this stage needs a second
            # visit, now that INTERPRET has run, to put that hop's text on a rendered page at all.
            founder.open_stage_evidence(project_id, stage)

        assert handoff is None, f"expected the project to be finished (brief proposed), got {handoff}"

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
