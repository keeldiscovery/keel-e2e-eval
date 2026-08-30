"""S-009 -- incremental roles (feedback item 8's dead end, now fixed; founder-experience round 2
design §5, keel-cloud commit `cef132c`, spec 015 FR-004).

Item 8 of the 2026-08-30 feedback session was a genuine dead end: `reviewRecommendation` used to
ask "does the *project* have roles?" -- so once the problem stage's own role existed, COMMERCIAL's
own decompose step had no path forward at all (`INTRODUCE_ASSUMPTIONS` would be recommended and
then legally refused, A3, with nothing on the wire able to say why -- and the eval set never caught
it, because every scenario before this one introduces all its roles in one batch). The fix asks the
right question instead -- "does *this stage* have a role that can settle its beliefs" -- and this
scenario is its one live demonstration.

PROBLEM and SOLUTION share a PRACTITIONER role (`Project.roleTypesCompatibleWith`: CONSUMER,
PRACTITIONER or MANAGER for PROBLEM; those three plus GATEKEEPER for SOLUTION) -- deliberately never
a type COMMERCIAL's own beliefs may be asked of (BUYER, MANAGER or GATEKEEPER). So COMMERCIAL's own
decompose step genuinely has no compatible role yet: `INTRODUCE_ROLES` is recommended (never
`INTRODUCE_ASSUMPTIONS`), and its `detail` carries the stage's compatible role picture
(`compatibleRoleKinds`, `existingCompatibleRoles`) an agent can act on instead of discovering the
rule by refusal (feedback item 7, closed the same commit). Both moments are driven by hand here --
never through `advance_until_handoff`'s auto-chain -- the same "every door must open" discipline
`test_s001_smoke.py` uses for the PROBLEM assumptions door: COMMERCIAL's `INTRODUCE_ROLES` issuance
(compatible kinds named, no existing role qualifies yet) and, once the buyer is introduced through
that front door, COMMERCIAL's own `INTRODUCE_ASSUMPTIONS` issuance (the identical detail shape,
design §5's own promise -- now naming the buyer as an existing qualifying role, so an agent never
has to branch on which action it got to learn what it could propose).

FID trace (task item 3, "buyer label through roles context -> People screen"): the buyer's own
label reaches the `roles_context` hop (the `roles` handle's own echo, re-read once the buyer exists,
immediately before COMMERCIAL's `INTRODUCE_ASSUMPTIONS`) and the invite screen's own role picker,
once the gate opens and the founder actually invites them -- "the flow proceeds to invitable"
(task item 3), checked live on the People screen's own role picker before either invitation is sent.
"""

# Journey coverage (CANON.md ledger): proves §1.4's inviting reach when a later stage needs a
# kind of person the earlier stages never met -- the buyer arrives through the front door.

from __future__ import annotations

import time

from evals.recipes import (
    arrive_and_create, assert_invite_gate_closed, assert_participant_has_no_founder_auth,
    assert_pointer_to_agent, open_founder_session,
)
from evals.scenario import Fact, Scenario, find_role
from harness.browser import ParticipantBrowser
from harness.evidence import finalize_run
from harness.steps import Recorder

PROJECT_NAME = "Payroll Exception Radar (Incremental Roles)"
PROBLEM = "PROBLEM"
SOLUTION = "SOLUTION"
COMMERCIAL = "COMMERCIAL"
STAGES = (PROBLEM, SOLUTION, COMMERCIAL)

PRACTITIONER_LABEL = "Payroll Practitioner"
BUYER_LABEL = "Finance Buyer"

PROBLEM_CLAIM = "Payroll managers at mid-size companies lose hours each month chasing payroll exceptions."
PROBLEM_ASSUMPTION = "They handle payroll exceptions themselves, at least monthly."
PROBLEM_HEADING = "Manual exception chasing"
PROBLEM_ASK = "Tell me about the last time you had to chase down a payroll exception by hand."
PROBLEM_DISCONFIRMING = "Has there been a month where you had no exceptions to chase down at all?"
PROBLEM_ANSWER = ("Yeah -- just last month I spent about three hours tracking down a payroll "
                   "exception before I could run final payroll.")

SOLUTION_CLAIM = "A tool that automatically flags and routes payroll exceptions."
SOLUTION_ASSUMPTION = "A tool that automatically flags and routes payroll exceptions would get used."
SOLUTION_HEADING = "Automated flagging gets used"
SOLUTION_ASK = "Tell me about the last tool you tried for tracking payroll exceptions."
SOLUTION_DISCONFIRMING = "Have you tried something like this before and stopped using it?"
SOLUTION_ANSWER = ("I tried a spreadsheet, but people forgot to update it -- something automatic "
                    "would get used.")

COMMERCIAL_CLAIM = "$30 a seat per month, billed annually upfront."
COMMERCIAL_ASSUMPTION = "Someone in finance can approve a purchase like this without a lengthy process."
COMMERCIAL_HEADING = "Approval is workable"
COMMERCIAL_ASK = "Walk me through the last time your team approved a purchase like this."
COMMERCIAL_DISCONFIRMING = "Has a purchase like this ever gotten stuck with nobody able to approve it?"
COMMERCIAL_ANSWER = ("Last quarter we approved a similar tool in about a week -- finance signs off "
                      "fast here.")

PRACTITIONER_PERSON = "Jordan Casey"
PRACTITIONER_ABOUT_LINE = ("A few quick questions about payroll exception handling and the tools "
                            "you've tried.")
BUYER_PERSON = "Morgan Ellis"
BUYER_ABOUT_LINE = "A few quick questions about how your team approves purchases like this."


class S009IncrementalRoles(Scenario):
    name = "S-009 incremental roles"
    slug = "s009-incremental-roles"

    def __init__(self) -> None:
        self._roles_calls = 0

    def project_name(self) -> str:
        return PROJECT_NAME

    def problem_statement(self) -> str:
        return PROBLEM_CLAIM

    def frame_statement(self, stage: str) -> str:
        return {SOLUTION: SOLUTION_CLAIM, COMMERCIAL: COMMERCIAL_CLAIM}[stage]

    def build_payload(self, action: str, detail: dict, context) -> dict:
        if action == "INTRODUCE_ROLES":
            self._roles_calls += 1
            if self._roles_calls == 1:
                # PROBLEM's own first decompose (item 8's ladder always worked from zero roles) --
                # deliberately a type COMMERCIAL's beliefs may never be asked of
                # (`Project.roleTypesCompatibleWith`: PRACTITIONER fits PROBLEM/SOLUTION, not
                # COMMERCIAL).
                return {"roles": [{"label": PRACTITIONER_LABEL, "roleType": "PRACTITIONER",
                                    "about": "How payroll exception handling works day to day"}]}
            # COMMERCIAL's own decompose, through the front door the fix opens (design §5): a
            # BUYER-type role, the kind COMMERCIAL's beliefs may actually be asked of.
            return {"roles": [{"label": BUYER_LABEL, "roleType": "BUYER",
                                "about": "How purchases like this get approved on their team"}]}
        return super().build_payload(action, detail, context)

    def assumptions_payload(self, stage: str, roles: list[dict]) -> list[dict]:
        if stage == PROBLEM:
            role_id = find_role(roles, PRACTITIONER_LABEL)["id"]
            return [{"statement": PROBLEM_ASSUMPTION, "heading": PROBLEM_HEADING, "stage": PROBLEM,
                     "risk": "LOAD_BEARING", "askedOf": role_id,
                     "question": {"ask": PROBLEM_ASK, "probes": [], "disconfirming": PROBLEM_DISCONFIRMING}}]
        if stage == SOLUTION:
            role_id = find_role(roles, PRACTITIONER_LABEL)["id"]
            return [{"statement": SOLUTION_ASSUMPTION, "heading": SOLUTION_HEADING, "stage": SOLUTION,
                     "risk": "LOAD_BEARING", "askedOf": role_id,
                     "question": {"ask": SOLUTION_ASK, "probes": [], "disconfirming": SOLUTION_DISCONFIRMING}}]
        role_id = find_role(roles, BUYER_LABEL)["id"]
        return [{"statement": COMMERCIAL_ASSUMPTION, "heading": COMMERCIAL_HEADING, "stage": COMMERCIAL,
                 "risk": "LOAD_BEARING", "askedOf": role_id,
                 "question": {"ask": COMMERCIAL_ASK, "probes": [], "disconfirming": COMMERCIAL_DISCONFIRMING}}]

    def about_line(self, stage: str) -> str:
        return {PROBLEM: PRACTITIONER_ABOUT_LINE, SOLUTION: PRACTITIONER_ABOUT_LINE,
                COMMERCIAL: BUYER_ABOUT_LINE}[stage]

    def person_name(self, stage: str) -> str:
        return {PROBLEM: PRACTITIONER_PERSON, SOLUTION: PRACTITIONER_PERSON,
                COMMERCIAL: BUYER_PERSON}[stage]

    def participant_answer(self, stage: str) -> str:
        return {PROBLEM: PROBLEM_ANSWER, SOLUTION: SOLUTION_ANSWER, COMMERCIAL: COMMERCIAL_ANSWER}[stage]

    def interpret_payload(self, stage: str, response: dict) -> list[dict]:
        per_answer = []
        for answer in response["answers"]:
            if not answer.get("text"):
                continue
            per_answer.append({"assumptionId": answer["assumptionId"], "evidence": [{
                "statement": answer["text"], "claimType": "PAST_BEHAVIOR", "stance": "SUPPORTS",
            }]})
        return per_answer

    def brief_payload(self, context) -> dict:
        return {
            "findings": [
                "Payroll managers handle exceptions themselves, monthly (1 of 1 respondents).",
                "A tool that flags and routes exceptions would get used (1 of 1 respondents).",
                "Someone in finance can approve a purchase like this (1 of 1 respondents).",
            ],
            "openDecisions": [],
        }

    # ---------------------------------------------------------------------------- fact registry

    def facts(self) -> dict[str, Fact]:
        return {
            "project_name": Fact(text=PROJECT_NAME, kind="statement", hops=["recorded", "stage_screen"]),
            "problem_statement": Fact(text=PROBLEM_CLAIM, kind="statement",
                                       hops=["agent_echo", "stage_screen", "brief", "recorded"]),
            "solution_statement": Fact(text=SOLUTION_CLAIM, kind="statement",
                                        hops=["agent_echo", "stage_screen", "brief", "recorded"]),
            "commercial_statement": Fact(text=COMMERCIAL_CLAIM, kind="statement",
                                          hops=["agent_echo", "stage_screen", "brief", "recorded"]),
            "practitioner_label": Fact(
                text=PRACTITIONER_LABEL, kind="role",
                hops=["agent_echo", "stage_screen", "invite_screen", "recorded", "roles_context"]),
            # The task's own worked example: the buyer's label, introduced through the roles-ladder
            # front door, traced from the `roles` handle's own echo through to the People screen.
            "buyer_label": Fact(
                text=BUYER_LABEL, kind="role",
                hops=["roles_context", "agent_echo", "stage_screen", "invite_screen", "recorded"]),
            "assumption_problem": Fact(text=PROBLEM_ASSUMPTION, kind="assumption",
                                        hops=["agent_echo", "stage_screen", "interpret_context", "brief", "recorded"]),
            "heading_problem": Fact(text=PROBLEM_HEADING, kind="assumption", hops=["stage_screen", "recorded"]),
            "assumption_solution": Fact(text=SOLUTION_ASSUMPTION, kind="assumption",
                                         hops=["agent_echo", "stage_screen", "interpret_context", "brief", "recorded"]),
            "heading_solution": Fact(text=SOLUTION_HEADING, kind="assumption", hops=["stage_screen", "recorded"]),
            "assumption_commercial": Fact(text=COMMERCIAL_ASSUMPTION, kind="assumption",
                                           hops=["agent_echo", "stage_screen", "interpret_context", "brief", "recorded"]),
            "heading_commercial": Fact(text=COMMERCIAL_HEADING, kind="assumption", hops=["stage_screen", "recorded"]),
            "answer_problem": Fact(text=PROBLEM_ANSWER, kind="answer", hops=["interpret_context", "stage_screen"]),
            "answer_solution": Fact(text=SOLUTION_ANSWER, kind="answer", hops=["interpret_context", "stage_screen"]),
            "answer_commercial": Fact(text=COMMERCIAL_ANSWER, kind="answer", hops=["interpret_context", "stage_screen"]),
        }


def test_s009_incremental_roles(stack, run_dir, browser, founder_credentials):
    recorder = Recorder(run_dir)
    scenario = S009IncrementalRoles()
    passed = False
    started = time.monotonic()
    driver, founder, founder_context = open_founder_session(stack, founder_credentials, recorder,
                                                              scenario, browser)
    founder_page = founder.page
    try:
        # The shared opening step (task item 2): arrival, then CREATE with its own completed
        # display proven live, then the project list growing by this fresh project.
        project_id = arrive_and_create(driver, founder, scenario)

        driver.advance_one()  # FRAME SOLUTION
        driver.advance_one()  # FRAME COMMERCIAL

        # PROBLEM and SOLUTION each decompose against zero-or-compatible roles the ordinary way
        # (item 8's ladder always worked from here) -- auto-chained, then approved.
        for stage in (PROBLEM, SOLUTION):
            handoff = driver.advance_until_handoff()
            assert handoff and handoff["reason"] == "REVIEW" and handoff["detail"]["stage"] == stage, \
                (stage, handoff)
            founder.open_stage(project_id, stage)
            founder.approve_current_stage(stage)
            assert_invite_gate_closed(driver)
            assert_pointer_to_agent(founder, project_id)

        # COMMERCIAL's own decompose -- the roles-ladder fix's one live demonstration (item 8):
        # PRACTITIONER (PROBLEM/SOLUTION's role) does not qualify for COMMERCIAL
        # (`Project.roleTypesCompatibleWith(COMMERCIAL)` is BUYER/MANAGER/GATEKEEPER), so
        # `INTRODUCE_ROLES` is recommended -- never `INTRODUCE_ASSUMPTIONS` -- with the
        # compatibility detail (design §5) naming what would qualify and what already does
        # (nothing, yet).
        with recorder.interaction("agent-cycle"):
            with recorder.step(
                    "COMMERCIAL's decompose recommends INTRODUCE_ROLES, with the compatibility "
                    "detail (item 8, fixed)", party="agent", kind="assert") as h:
                issuance = driver.get_next()
                detail = issuance.get("detail") or {}
                h.record_assert(
                    "action INTRODUCE_ROLES, compatibleRoleKinds={BUYER,MANAGER,GATEKEEPER}, "
                    "existingCompatibleRoles=[]", issuance)
                if not (issuance.get("kind") == "action" and issuance.get("action") == "INTRODUCE_ROLES"
                        and detail.get("stage") == COMMERCIAL):
                    h.fail(f"expected INTRODUCE_ROLES for COMMERCIAL, got {issuance}")
                    raise AssertionError(h.error)
                if set(detail.get("compatibleRoleKinds") or []) != {"BUYER", "MANAGER", "GATEKEEPER"}:
                    h.fail("expected COMMERCIAL's compatible role kinds "
                           f"{{'BUYER', 'MANAGER', 'GATEKEEPER'}}, got {detail.get('compatibleRoleKinds')}")
                    raise AssertionError(h.error)
                if detail.get("existingCompatibleRoles") != []:
                    h.fail(f"expected no existing compatible role yet, got {detail.get('existingCompatibleRoles')}")
                    raise AssertionError(h.error)
            token = issuance["token"]
            context = {name: driver.get_context(token, name) for name in issuance.get("context") or []}
            payload = scenario.build_payload("INTRODUCE_ROLES", detail, context)
            driver.submit_with_recovery(token, payload, "INTRODUCE_ROLES",
                                         "INTRODUCE_ROLES (COMMERCIAL buyer, through the front door)")

        # The buyer now exists -- COMMERCIAL's decompose recommends INTRODUCE_ASSUMPTIONS, the
        # identical detail shape (design §5's own promise), now naming the buyer as an existing
        # qualifying role. This read is the buyer label's own `roles_context` hop (task item 3).
        with recorder.interaction("agent-cycle"):
            with recorder.step(
                    "COMMERCIAL's decompose now recommends INTRODUCE_ASSUMPTIONS, the buyer "
                    "already qualifying", party="agent", kind="assert") as h:
                issuance2 = driver.get_next()
                detail2 = issuance2.get("detail") or {}
                h.record_assert("action INTRODUCE_ASSUMPTIONS, existingCompatibleRoles=[buyer]", issuance2)
                if not (issuance2.get("kind") == "action"
                        and issuance2.get("action") == "INTRODUCE_ASSUMPTIONS"
                        and detail2.get("stage") == COMMERCIAL):
                    h.fail(f"expected INTRODUCE_ASSUMPTIONS for COMMERCIAL, got {issuance2}")
                    raise AssertionError(h.error)
                if set(detail2.get("compatibleRoleKinds") or []) != {"BUYER", "MANAGER", "GATEKEEPER"}:
                    h.fail(f"expected the same compatible role kinds, got {detail2.get('compatibleRoleKinds')}")
                    raise AssertionError(h.error)
                if detail2.get("existingCompatibleRoles") != [BUYER_LABEL]:
                    h.fail(f"expected the buyer to now qualify, got {detail2.get('existingCompatibleRoles')}")
                    raise AssertionError(h.error)
            token2 = issuance2["token"]
            context2 = {name: driver.get_context(token2, name) for name in issuance2.get("context") or []}
            payload2 = scenario.build_payload("INTRODUCE_ASSUMPTIONS", detail2, context2)
            driver.submit_with_recovery(token2, payload2, "INTRODUCE_ASSUMPTIONS",
                                         "INTRODUCE_ASSUMPTIONS (COMMERCIAL)")

        handoff = driver.advance_until_handoff()
        assert handoff and handoff["reason"] == "REVIEW" and handoff["detail"]["stage"] == COMMERCIAL, handoff
        founder.open_stage(project_id, COMMERCIAL)
        founder.approve_current_stage(COMMERCIAL)

        # The gate is open now (all three approved). currentFocus scans PROBLEM first -- the
        # practitioner's combined problem+solution invitation goes out first.
        handoff = driver.advance_until_handoff()
        assert handoff and handoff["reason"] == "INVITE", handoff
        founder.open_people(project_id)
        practitioner_link = founder.send_invite(PRACTITIONER_LABEL, PRACTITIONER_PERSON,
                                                 PRACTITIONER_ABOUT_LINE)

        handoff = driver.advance_until_handoff()
        assert handoff and handoff["reason"] == "WAITING", handoff

        participant_context = browser.new_context()
        try:
            page = participant_context.new_page()
            participant = ParticipantBrowser(page, recorder)
            participant.open(practitioner_link)
            participant.start()
            participant.answer([PROBLEM_ANSWER, SOLUTION_ANSWER])
            participant.submit()
            assert_participant_has_no_founder_auth(participant_context)
        finally:
            participant_context.close()

        # Once problem+solution settle, COMMERCIAL's own INVITE need surfaces -- "the flow
        # proceeds to invitable" (task item 3): checked live on the People screen's own role
        # picker before the buyer's invitation is ever sent.
        handoff = driver.advance_until_handoff()
        assert handoff and handoff["reason"] == "INVITE" and handoff["detail"]["stage"] == COMMERCIAL, handoff
        founder.open_people(project_id)
        with recorder.step(
                "the buyer role reads invitable on the People screen -- the front door the "
                "ladder fix opens", party="founder", kind="assert") as h:
            options = founder.role_picker_options()
            h.record_assert(f"{BUYER_LABEL} present and enabled", options)
            buyer_option = next((o for o in options if BUYER_LABEL in str(o["text"])), None)
            if buyer_option is None or buyer_option["disabled"]:
                h.fail(f"expected {BUYER_LABEL!r} to read invitable, got {options}")
                raise AssertionError(h.error)
        buyer_link = founder.send_invite(BUYER_LABEL, BUYER_PERSON, BUYER_ABOUT_LINE)

        handoff = driver.advance_until_handoff()
        assert handoff and handoff["reason"] == "WAITING", handoff

        participant_context = browser.new_context()
        try:
            page = participant_context.new_page()
            participant = ParticipantBrowser(page, recorder)
            participant.open(buyer_link)
            participant.start()
            participant.answer([COMMERCIAL_ANSWER])
            participant.submit()
            assert_participant_has_no_founder_auth(participant_context)
        finally:
            participant_context.close()

        handoff = driver.advance_until_handoff()
        assert handoff is None, f"expected the project to finish (brief proposed), got {handoff}"

        # FID hop capture: the participant's verbatim answers only render on a stage screen inside
        # a belief's testimony drilldown once evidence has been interpreted.
        for stage in STAGES:
            founder.open_stage_evidence(project_id, stage)

        founder.open_overview(project_id)

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
