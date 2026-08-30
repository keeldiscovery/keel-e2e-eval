"""S-005 -- opinions move nothing (T010; journeys.md §1.7 "nothing solid yet", §2.2).

One belief, two strangers, its own fresh project (design §5 independence pass): one answers with a
guess rather than a report of anything that happened -- speculation and stated preference are
never "strong" evidence (`ClaimType.isStrong`), so the belief stays `UNTESTED` no matter how
supportive the words sound, and the stage reads "Nothing solid yet -- people gave opinions rather
than examples" (`lib/translate.ts` `beliefStatus`). The other skips every question outright --
`ParticipantController.respond` refuses an all-blank submission gently (422, a kind page, journeys
§2.2: "a blank answer is information; a fabricated one is damage") and the founder's own counts
never learn about an attempt that never became an answer.

Asserts end to end: the belief's own status surfaces the opinions-not-examples explanation
(without ever naming `STATED_PREFERENCE`/`SPECULATION`/`UNTESTED` -- P1); the all-skipped stranger
sees a kind page throughout, not a raw error; and the founder's people-answered count stays honest
(one, not two) despite two invitations having been sent.
"""

from __future__ import annotations

import time

from evals.scenario import Fact, Scenario, find_role
from harness.browser import FounderBrowser, ParticipantBrowser
from harness.evidence import finalize_run
from harness.driver import FounderAgentDriver
from harness.steps import Recorder

ROLE_LABEL = "Payroll Ops Manager"
PROBLEM_CLAIM = "Payroll managers at mid-size companies lose hours each month chasing payroll exceptions."
ASSUMPTION = "They handle payroll exceptions themselves, at least monthly."
ASK = "Tell me about the last time you had to chase down a payroll exception by hand."
DISCONFIRMING = "Has there been a month where you had no exceptions to chase down at all?"
ABOUT_LINE = "A few quick questions about how payroll exception handling goes day to day."

OPINION_PERSON = "Jordan Casey"
OPINION_ANSWER = "I guess it probably happens sometimes, but honestly it's hard to say for sure."
SKIP_PERSON = "Taylor Brooks"


class S005Opinions(Scenario):
    name = "S-005 opinions move nothing"
    slug = "s005-opinions"

    def problem_statement(self) -> str:
        return PROBLEM_CLAIM

    def frame_statement(self, stage: str) -> str:
        return {"SOLUTION": "A tool that flags and routes payroll exceptions automatically.",
                "COMMERCIAL": "$30 a seat per month."}[stage]

    def roles_payload(self) -> list[dict]:
        return [{"label": ROLE_LABEL, "roleType": "MANAGER",
                 "about": "How payroll runs work at mid-size companies"}]

    def assumptions_payload(self, stage: str, roles: list[dict]) -> list[dict]:
        role_id = find_role(roles, ROLE_LABEL)["id"]
        return [{"statement": ASSUMPTION, "stage": "PROBLEM", "risk": "LOAD_BEARING", "askedOf": role_id,
                 "question": {"ask": ASK, "probes": [], "disconfirming": DISCONFIRMING}}]

    def about_line(self, stage: str) -> str:
        return ABOUT_LINE

    def interpret_payload(self, stage: str, response: dict) -> list[dict]:
        per_answer = []
        for answer in response["answers"]:
            if not answer.get("text"):
                continue
            # A guess, not a report -- STATED_PREFERENCE is deliberately not "strong"
            # (ClaimType.isStrong), so this never counts as a supporter or a dissenter.
            per_answer.append({"assumptionId": answer["assumptionId"], "evidence": [{
                "statement": answer["text"], "claimType": "STATED_PREFERENCE", "stance": "SUPPORTS",
            }]})
        return per_answer

    def facts(self) -> dict[str, Fact]:
        return {
            "problem_statement": Fact(text=PROBLEM_CLAIM, kind="statement", hops=["agent_echo", "stage_screen"]),
            "assumption": Fact(text=ASSUMPTION, kind="assumption",
                                hops=["agent_echo", "stage_screen", "interpret_context"]),
            "answer_opinion": Fact(text=OPINION_ANSWER, kind="answer", hops=["interpret_context", "stage_screen"]),
        }


def test_s005_opinions(stack, run_dir, browser):
    recorder = Recorder(run_dir)
    scenario = S005Opinions()
    cloud_base = f"http://localhost:{stack.cloud_port}"
    founder_web_base = f"http://localhost:{stack.web_port}/p"

    driver = FounderAgentDriver(cloud_base, recorder, scenario)
    passed = False
    started = time.monotonic()
    founder_context = browser.new_context()
    try:
        founder_page = founder_context.new_page()
        founder = FounderBrowser(founder_page, founder_web_base, recorder, get_state=driver.get_state)

        handoff = driver.advance_until_handoff()
        assert handoff and handoff["reason"] == "REVIEW" and handoff["detail"]["stage"] == "PROBLEM", handoff
        project_id = driver.project_id

        founder.open_stage(project_id, "PROBLEM")
        founder.approve_current_stage("PROBLEM")

        handoff = driver.advance_until_handoff()
        assert handoff and handoff["reason"] == "INVITE", handoff
        founder.open_invite(project_id)
        opinion_link = founder.send_invite(ROLE_LABEL, OPINION_PERSON, ABOUT_LINE)
        # Second respondent, founder-initiated (the belief stays open; `invite()` never needs
        # get_next's blessing for a second person -- same mechanism as S-004).
        founder.open_invite(project_id)
        skip_link = founder.send_invite(ROLE_LABEL, SKIP_PERSON, ABOUT_LINE)

        handoff = driver.advance_until_handoff()
        assert handoff and handoff["reason"] == "WAITING", handoff

        # The opinion-only respondent: answers, but with a guess, not a report.
        opinion_context = browser.new_context()
        try:
            page = opinion_context.new_page()
            participant = ParticipantBrowser(page, recorder)
            participant.open(opinion_link)
            participant.start()
            participant.answer([OPINION_ANSWER])
            participant.submit()
        finally:
            opinion_context.close()

        # journeys.md §2.2: "Every question can be skipped... a blank answer is information."
        # The all-skipped stranger sees a kind page, end to end -- never a raw error, never moved
        # past the questions screen into a false "thanks."
        skip_context = browser.new_context()
        try:
            page = skip_context.new_page()
            participant = ParticipantBrowser(page, recorder)
            with recorder.step("an all-skipped submission is handled gently, not as a raw error",
                                party="participant", kind="assert") as h:
                participant.open(skip_link)
                participant.start()
                # Answers nothing at all -- every field stays blank -- then submits anyway.
                participant.submit_expect_notice()
                body = page.locator("body").inner_text()
                h.record_assert("a kind notice, still on the form, no raw error, no false thank-you",
                                 body)
                lowered = body.lower()
                if "thanks" in lowered and "gone to" in lowered:
                    h.fail(f"the all-skipped submission was wrongly accepted as a real answer: {body!r}")
                    raise AssertionError(h.error)
                if not any(w in lowered for w in ("nothing to send", "left blank", "skip", "close the page")):
                    h.fail(f"expected a gentle explanation of the all-blank refusal, got: {body!r}")
                    raise AssertionError(h.error)
                # Still on the questions screen -- the stranger can simply close the page, per
                # ParticipantDtos.NoticeBody's own remedy, rather than being stranded on an error.
                if page.locator("textarea.box").count() == 0:
                    h.fail("expected to remain on the answering screen after the gentle refusal")
                    raise AssertionError(h.error)
        finally:
            skip_context.close()

        handoff = driver.advance_until_handoff()
        assert handoff is not None, "expected an EVIDENCE/INVITE handoff (still open), got None"

        founder.open_stage_evidence(project_id, "PROBLEM")
        with recorder.step("the belief reads Nothing solid yet -- opinions, not examples (§1.7)",
                            party="founder", kind="assert") as h:
            status = founder_page.locator(".b-status").first
            label = status.inner_text()
            sub = status.locator(".sub").inner_text() if status.locator(".sub").count() else ""
            h.record_assert("Nothing solid yet / people gave opinions rather than examples",
                             {"label": label, "sub": sub})
            if "nothing solid yet" not in label.lower():
                h.fail(f"expected 'Nothing solid yet', got {label!r}")
                raise AssertionError(h.error)
            if "opinions" not in sub.lower():
                h.fail(f"expected the opinions-not-examples explanation, got {sub!r}")
                raise AssertionError(h.error)

        with recorder.step("the founder's people-answered count stays honest despite the gentle refusal",
                            party="founder", kind="assert") as h:
            counts = founder_page.locator(".card.openc .counts").inner_text()
            h.record_assert("1 person answered, not 2", counts)
            if "1 person answered" not in counts:
                h.fail(f"expected exactly one person to be counted as answered, got {counts!r}")
                raise AssertionError(h.error)

        passed = True
    finally:
        founder_context.close()
        duration = time.monotonic() - started
        finalize_run(run_dir, scenario=scenario, passed=passed,
                     failed_step=recorder.failed_step, duration_s=duration)
        print(f"\nrun bundle: {run_dir}")
