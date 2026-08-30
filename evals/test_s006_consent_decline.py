"""S-006 -- the stranger declines, the stranger consents (T011; journeys.md §2.1-2.3).

One belief, two strangers, its own fresh project (design §5 independence pass): one opens the link
and clicks "No thanks" -- `ParticipantRoute.tsx`'s `OpenForm` handles this entirely client-side
(no request is ever sent), so nothing reaches the founder as an answer, and the invitations screen
never has a "declined" status to show in the first place (`lib/translate.ts` `invitationStatus`
has exactly four states -- not opened yet / opened, not answered / answered / link no longer
valid -- decline is not one of them, by construction: there is nothing here to shame). The other
consents by starting, answers, and the thank-you page promises nothing the product cannot keep --
the founder's name and that words went to them, no deletion path, no account, no score
(journeys.md §2.3: "Nothing else. No score, no results, no account, no follow-up.").

Consent-screen fidelity (§2.1): "Four things and no more: who is asking, what it is about, how
long, what happens to their words" -- asserted as exactly those four, not fewer and not padded
with a fifth.

The invite gate (founder-experience design §6, keel-cloud commits 8b13d04/ff1ed48) now requires
SOLUTION and COMMERCIAL *approved*, not just framed, before PROBLEM's own invite is legal -- see
`evals.recipes.advance_to_all_stages_approved`/`filler_assumption_payload` for the shared judgement
call this scenario needs (a placeholder belief on a never-invited role).
"""

from __future__ import annotations

import time

from evals.recipes import (
    FILLER_ROLE_LABEL, advance_to_all_stages_approved, filler_assumption_payload, filler_role_payload,
)
from evals.scenario import Fact, Scenario, find_role
from harness.browser import FounderBrowser, ParticipantBrowser
from harness.driver import FounderAgentDriver
from harness.evidence import finalize_run
from harness.steps import Recorder

PROJECT_NAME = "Payroll Exception Radar (Consent)"
ROLE_LABEL = "Payroll Ops Manager"
PROBLEM_CLAIM = "Payroll managers at mid-size companies lose hours each month chasing payroll exceptions."
ASSUMPTION = "They handle payroll exceptions themselves, at least monthly."
HEADING = "Manual exception chasing"
ASK = "Tell me about the last time you had to chase down a payroll exception by hand."
DISCONFIRMING = "Has there been a month where you had no exceptions to chase down at all?"
ABOUT_LINE = "How payroll exception handling goes day to day."

DECLINE_PERSON = "Sam Rivera"
CONSENT_PERSON = "Wei Zhang"
CONSENT_ANSWER = "Usually 90 minutes, sometimes half a day if the bureau's involved."  # journeys.md §1.7


class S006ConsentDecline(Scenario):
    name = "S-006 consent and decline"
    slug = "s006-consent-decline"

    def project_name(self) -> str:
        return PROJECT_NAME

    def problem_statement(self) -> str:
        return PROBLEM_CLAIM

    def frame_statement(self, stage: str) -> str:
        return {"SOLUTION": "A tool that flags and routes payroll exceptions automatically.",
                "COMMERCIAL": "$30 a seat per month."}[stage]

    def roles_payload(self) -> list[dict]:
        return [{"label": ROLE_LABEL, "roleType": "MANAGER",
                 "about": "How payroll runs work at mid-size companies"},
                filler_role_payload()]

    def assumptions_payload(self, stage: str, roles: list[dict]) -> list[dict]:
        if stage != "PROBLEM":
            return [filler_assumption_payload(stage, find_role(roles, FILLER_ROLE_LABEL)["id"])]
        role_id = find_role(roles, ROLE_LABEL)["id"]
        return [{"statement": ASSUMPTION, "heading": HEADING, "stage": "PROBLEM", "risk": "LOAD_BEARING",
                 "askedOf": role_id, "question": {"ask": ASK, "probes": [], "disconfirming": DISCONFIRMING}}]

    def about_line(self, stage: str) -> str:
        return ABOUT_LINE

    def interpret_payload(self, stage: str, response: dict) -> list[dict]:
        per_answer = []
        for answer in response["answers"]:
            if not answer.get("text"):
                continue
            per_answer.append({"assumptionId": answer["assumptionId"], "evidence": [{
                "statement": answer["text"], "claimType": "PAST_BEHAVIOR", "stance": "SUPPORTS",
            }]})
        return per_answer

    def facts(self) -> dict[str, Fact]:
        return {
            "project_name": Fact(text=PROJECT_NAME, kind="statement", hops=["recorded"],
                                 absent_hops=["agent_echo", "stage_screen", "invite_screen",
                                              "participant_page", "interpret_context", "brief"]),
            "problem_statement": Fact(text=PROBLEM_CLAIM, kind="statement",
                                       hops=["agent_echo", "stage_screen", "recorded"]),
            "assumption": Fact(text=ASSUMPTION, kind="assumption",
                                hops=["agent_echo", "stage_screen", "interpret_context", "recorded"]),
            "heading": Fact(text=HEADING, kind="assumption", hops=["stage_screen", "recorded"]),
            "about_line": Fact(text=ABOUT_LINE, kind="about_line", hops=["invite_screen", "participant_page"]),
            "answer_consent": Fact(text=CONSENT_ANSWER, kind="answer", hops=["interpret_context", "stage_screen"]),
        }


def test_s006_consent_decline(stack, run_dir, browser):
    recorder = Recorder(run_dir)
    scenario = S006ConsentDecline()
    cloud_base = f"http://localhost:{stack.cloud_port}"
    founder_web_base = f"http://localhost:{stack.web_port}/p"

    driver = FounderAgentDriver(cloud_base, recorder, scenario)
    passed = False
    started = time.monotonic()
    founder_context = browser.new_context()
    try:
        founder_page = founder_context.new_page()
        founder = FounderBrowser(founder_page, founder_web_base, recorder, get_state=driver.get_state)

        # The invite gate (module docstring): all three stages approved before any invitation
        # exists, even though this scenario's own subject is PROBLEM alone.
        advance_to_all_stages_approved(driver, founder)
        project_id = driver.project_id

        handoff = driver.advance_until_handoff()
        assert handoff and handoff["reason"] == "INVITE", handoff
        founder.open_people(project_id)
        decline_link = founder.send_invite(ROLE_LABEL, DECLINE_PERSON, ABOUT_LINE)
        founder.open_people(project_id)
        consent_link = founder.send_invite(ROLE_LABEL, CONSENT_PERSON, ABOUT_LINE)

        # journeys.md §2.1: "Four things and no more: who is asking, what it is about, how long,
        # what happens to their words." Checked on the consent screen before anyone acts on it.
        decline_context = browser.new_context()
        try:
            page = decline_context.new_page()
            participant = ParticipantBrowser(page, recorder)
            with recorder.step("the consent screen carries exactly its four things, no more",
                                party="participant", kind="assert") as h:
                participant.open(decline_link)
                hello = page.locator(".iv .hello").inner_text()
                meta = page.locator(".iv .meta").inner_text()
                consent_text = page.locator(".iv .consent").inner_text()
                h.record_assert("who/what in .hello, how-long in .meta, where-words-go in .consent",
                                 {"hello": hello, "meta": meta, "consent": consent_text})
                if "asked if you" not in hello.lower():
                    h.fail(f"expected 'asked if you' (who is asking + what it's about) in {hello!r}")
                    raise AssertionError(h.error)
                if ABOUT_LINE.split(" ")[0].lower() not in hello.lower() and ABOUT_LINE not in hello:
                    h.fail(f"expected the about-line ('what it's about') inside {hello!r}")
                    raise AssertionError(h.error)
                if "minutes" not in meta.lower():
                    h.fail(f"expected how-long ('About N minutes') in {meta!r}")
                    raise AssertionError(h.error)
                if not consent_text.strip():
                    h.fail("expected a non-empty consent line naming where the words go")
                    raise AssertionError(h.error)
                # No fifth thing: score/account/results would be promises about what happens
                # *after* submission, not "where the words go" -- out of scope for this screen.
                # ("delete" legitimately belongs here: CONSENT_TEXT's own honest "no way to delete
                # it" is part of the fourth thing, not a fifth one.)
                full_text = page.locator(".iv").inner_text().lower()
                for leak in ("account", "score", "results"):
                    if leak in full_text:
                        h.fail(f"consent screen mentions {leak!r} -- more than the four things (§2.1)")
                        raise AssertionError(h.error)

            # journeys.md §2.1: "Declining is a button of the same size." -- client-side only,
            # nothing is ever sent (harness/browser.py's `decline` docstring).
            with recorder.step("declining is graceful and sends nothing", party="participant", kind="assert") as h:
                participant.decline()
                body = page.locator("body").inner_text()
                h.record_assert("a graceful acknowledgement, no error, no form", body)
                if "no problem" not in body.lower() and "thanks for reading" not in body.lower():
                    h.fail(f"expected a graceful decline acknowledgement, got {body!r}")
                    raise AssertionError(h.error)
        finally:
            decline_context.close()

        consent_context = browser.new_context()
        try:
            page = consent_context.new_page()
            participant = ParticipantBrowser(page, recorder)
            participant.open(consent_link)
            participant.start()
            participant.answer([CONSENT_ANSWER])
            with recorder.step("the thank-you page promises nothing the product cannot keep (§2.3)",
                                party="participant", kind="assert") as h:
                participant.submit()
                body = page.locator("body").inner_text()
                h.record_assert("relays the founder's name; no deletion, no account, no score/results",
                                 body)
                lowered = body.lower()
                if "gone to" not in lowered and "thanks" not in lowered:
                    h.fail(f"expected the plain thank-you sentence, got {body!r}")
                    raise AssertionError(h.error)
                for over_promise in ("delete", "account", "score", "results", "follow-up", "follow up"):
                    if over_promise in lowered:
                        h.fail(f"thank-you page over-promises ({over_promise!r} mentioned): {body!r}")
                        raise AssertionError(h.error)
        finally:
            consent_context.close()

        # Agent reads what came back (journeys.md §1.6) -- and the stage evidence view is the
        # only place the participant's verbatim answer renders (FID hop capture).
        handoff = driver.advance_until_handoff()
        assert handoff is not None, "expected a handoff once the belief is settled, got None"
        founder.open_stage_evidence(project_id, "PROBLEM")

        # journeys.md §2.1/§1.5: "The UI never interprets" and never shames a decline -- the
        # invitations screen shows only the four statuses `invitationStatus` knows, and a decline
        # never reached the server to become a fifth one.
        founder.open_people(project_id)
        with recorder.step("the invitations screen never shames a decline", party="founder", kind="assert") as h:
            rows_text = founder_page.locator("table.invites").inner_text()
            h.record_assert("Sam Rivera shows a neutral status, never 'declined'", rows_text)
            lowered = rows_text.lower()
            if "declin" in lowered or "refused" in lowered or "no thanks" in lowered:
                h.fail(f"the invitations screen names the decline -- it should have nothing to say: {rows_text!r}")
                raise AssertionError(h.error)
            if DECLINE_PERSON not in rows_text:
                h.fail(f"expected {DECLINE_PERSON!r} still listed, got {rows_text!r}")
                raise AssertionError(h.error)

        passed = True
    finally:
        founder_context.close()
        duration = time.monotonic() - started
        finalize_run(run_dir, scenario=scenario, passed=passed,
                     failed_step=recorder.failed_step, duration_s=duration)
        print(f"\nrun bundle: {run_dir}")
