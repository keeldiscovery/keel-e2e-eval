"""S-004 -- the divided person (T009; journeys.md §1.7, the Marcus example).

One belief, three respondents, on its own fresh project (design §5 independence pass): Dana
describes concrete evidence for it happening; Marcus describes concrete evidence *both* ways in
one answer (he handled an exception himself, which supports it -- and his tooling now catches most
of them, which contradicts it); Priya offers a wish, not a report of anything that happened.

Asserts journeys.md §1.7's own claims about the drill-down, verbatim:

- **"Somebody who said something concrete in both directions appears under both headings"** --
  Marcus shows up in *both* "Counted for it" and "Counted against it".
- **"People, not quotes."** The collapsed line reads *2 described it happening, 1 described it
  not* -- two people for, one against -- not three (Marcus's two claims are not double-counted as
  two people).
- **"Said, but didn't count" carries the plain-words reason.** Priya's wish lands there with
  *"a wish, not something that happened"* -- `FounderViewAssembler.whyNot`'s own phrase for a
  `STATED_PREFERENCE`/`SUPPORTS` claim, never named as such to the founder (P1).
- The verdict itself follows the people-counted rule (`Project.verdictOf`, aggregate r7):
  2 supporters, 1 dissenter, minority non-empty -> `MIXED` -> "People disagree".

This scenario never touches `SOLUTION`/`COMMERCIAL` beyond the opening pass's mandatory framing
(`NextRecommendation.compute` frames every stage up front, a side effect of `CREATE`+the first two
`FRAME`s) -- it stops the instant the problem belief's drill-down is on screen.
"""

from __future__ import annotations

import time

from evals.scenario import Fact, Scenario, find_role
from harness.browser import FounderBrowser, ParticipantBrowser
from harness.driver import FounderAgentDriver
from harness.evidence import finalize_run
from harness.steps import Recorder

ROLE_LABEL = "Payroll Ops Manager"
PROBLEM_CLAIM = "Payroll managers at mid-size companies lose hours each month chasing payroll exceptions."
ASSUMPTION = "They handle payroll exceptions themselves, at least monthly."  # journeys.md §1.7, verbatim
ASK = "Tell me about the last time you had to chase down a payroll exception by hand."
DISCONFIRMING = "Has there been a month where you had no exceptions to chase down at all?"
ABOUT_LINE = "A few quick questions about how payroll exception handling goes day to day."

DANA = "Dana Okafor"
MARCUS = "Marcus Webb"
PRIYA = "Priya Raman"

DANA_ANSWER = "Last Tuesday I spent about two hours reconciling against invoices."  # §1.7, verbatim
MARCUS_ANSWER = "We had one last quarter, but our system catches most of it now."  # §1.7, verbatim
MARCUS_SUPPORTS_CLAIM = "He handled a payroll exception himself last quarter."
MARCUS_CONTRADICTS_CLAIM = "His tooling now catches most exceptions before he has to."
PRIYA_ANSWER = "I'd like better reporting on this, if that's an option."  # §1.7's own wish, verbatim


class S004DividedPerson(Scenario):
    name = "S-004 divided person"
    slug = "s004-divided-person"

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
        person = response["personName"]
        answer = next(a for a in response["answers"] if a.get("text"))
        assumption_id = answer["assumptionId"]
        if person == DANA:
            evidence = [{"statement": DANA_ANSWER, "claimType": "PAST_BEHAVIOR", "stance": "SUPPORTS"}]
        elif person == MARCUS:
            evidence = [
                {"statement": MARCUS_SUPPORTS_CLAIM, "claimType": "PAST_BEHAVIOR", "stance": "SUPPORTS"},
                {"statement": MARCUS_CONTRADICTS_CLAIM, "claimType": "CURRENT_WORKFLOW", "stance": "CONTRADICTS"},
            ]
        elif person == PRIYA:
            evidence = [{"statement": PRIYA_ANSWER, "claimType": "STATED_PREFERENCE", "stance": "SUPPORTS"}]
        else:
            raise AssertionError(f"unexpected respondent {person!r}")
        return [{"assumptionId": assumption_id, "evidence": evidence}]

    def facts(self) -> dict[str, Fact]:
        return {
            "problem_statement": Fact(text=PROBLEM_CLAIM, kind="statement", hops=["agent_echo", "stage_screen"]),
            "assumption": Fact(text=ASSUMPTION, kind="assumption",
                                hops=["agent_echo", "stage_screen", "interpret_context"]),
            "answer_dana": Fact(text=DANA_ANSWER, kind="answer", hops=["interpret_context", "stage_screen"]),
            # Marcus's raw answer is split into two separate evidence claims (MARCUS_SUPPORTS_CLAIM/
            # MARCUS_CONTRADICTS_CLAIM below) -- each renders on its own drilldown row, but his one
            # combined sentence is never reassembled as a single contiguous quote anywhere on the
            # stage screen, so `stage_screen` is a legitimately absent hop for this fact (not a
            # product gap -- a scenario-level consequence of a divided person's answer becoming two
            # claims, same shape as policy's own brief-summarization waiver, but not a policy
            # matter: nothing here fails a check, this is just an honest declared absence).
            "answer_marcus": Fact(text=MARCUS_ANSWER, kind="answer", hops=["interpret_context"],
                                   absent_hops=["stage_screen"]),
            "marcus_supports_claim": Fact(text=MARCUS_SUPPORTS_CLAIM, kind="answer", hops=["stage_screen"]),
            "marcus_contradicts_claim": Fact(text=MARCUS_CONTRADICTS_CLAIM, kind="answer", hops=["stage_screen"]),
            "answer_priya": Fact(text=PRIYA_ANSWER, kind="answer", hops=["interpret_context", "stage_screen"]),
        }


def test_s004_divided_person(stack, run_dir, browser):
    recorder = Recorder(run_dir)
    scenario = S004DividedPerson()
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

        # `INVITE` is only ever *recommended* once per assumption (get_next's own need computation
        # -- `Project.needs`'s `anyUninvited` is already false once any invitation asks about it):
        # the founder invites Dana on the agent's recommendation, then invites Marcus and Priya
        # herself, directly, exactly as journeys.md §1.4/§1.5 shows a founder doing from the
        # project page -- nothing about `invite()` requires get_next's blessing for a second or
        # third respondent to the same still-open belief.
        handoff = driver.advance_until_handoff()
        assert handoff and handoff["reason"] == "INVITE", handoff
        links: dict[str, str] = {}
        founder.open_invite(project_id)
        links[DANA] = founder.send_invite(ROLE_LABEL, DANA, ABOUT_LINE)
        for person in (MARCUS, PRIYA):
            founder.open_invite(project_id)
            links[person] = founder.send_invite(ROLE_LABEL, person, ABOUT_LINE)

        handoff = driver.advance_until_handoff()
        assert handoff and handoff["reason"] == "WAITING", handoff

        for person, answer in ((DANA, DANA_ANSWER), (MARCUS, MARCUS_ANSWER), (PRIYA, PRIYA_ANSWER)):
            participant_context = browser.new_context()
            try:
                page = participant_context.new_page()
                participant = ParticipantBrowser(page, recorder)
                participant.open(links[person])
                participant.start()
                participant.answer([answer])
                participant.submit()
            finally:
                participant_context.close()

        # No load-bearing CONTRADICTED verdict is possible here (the collapsed verdict is MIXED,
        # never CONTRADICTED -- see module docstring), so nothing pre-empts interpretation: one
        # advance_until_handoff chains through all three INTERPRETs.
        handoff = driver.advance_until_handoff()
        assert handoff is not None, "expected a handoff once the belief is MIXED (still open), got None"

        founder.open_stage_evidence(project_id, "PROBLEM")

        with recorder.step("the belief reads People disagree, 2 for / 1 against -- people, not quotes",
                            party="founder", kind="assert") as h:
            status = founder_page.locator(".b-status").first
            label = status.inner_text()
            sub = status.locator(".sub").inner_text() if status.locator(".sub").count() else ""
            h.record_assert("People disagree / 2 described it happening, 1 described it not",
                             {"label": label, "sub": sub})
            if "people disagree" not in label.lower():
                h.fail(f"expected 'People disagree', got {label!r}")
                raise AssertionError(h.error)
            if "2 described it happening" not in sub or "1 described it not" not in sub:
                h.fail(f"expected the collapsed line to count 2 people for / 1 against, got {sub!r}")
                raise AssertionError(h.error)

        with recorder.step("Marcus appears under BOTH counted-for and counted-against (§1.7)",
                            party="founder", kind="assert") as h:
            for_names = founder_page.locator(".vgroup.for .quote .name").all_inner_texts()
            against_names = founder_page.locator(".vgroup.against .quote .name").all_inner_texts()
            h.record_assert("Marcus in both groups", {"for": for_names, "against": against_names})
            if MARCUS not in for_names:
                h.fail(f"expected {MARCUS!r} under counted-for, got {for_names}")
                raise AssertionError(h.error)
            if MARCUS not in against_names:
                h.fail(f"expected {MARCUS!r} under counted-against, got {against_names}")
                raise AssertionError(h.error)
            if DANA not in for_names:
                h.fail(f"expected {DANA!r} under counted-for, got {for_names}")
                raise AssertionError(h.error)

        with recorder.step("Priya's wish lands in said-but-didn't-count with its plain-words reason (§1.7)",
                            party="founder", kind="assert") as h:
            nul_rows = founder_page.locator(".vgroup.nul .quote")
            nul_names = nul_rows.locator(".name").all_inner_texts()
            h.record_assert("Priya, 'a wish, not something that happened'", nul_names)
            if PRIYA not in nul_names:
                h.fail(f"expected {PRIYA!r} under said-but-didn't-count, got {nul_names}")
                raise AssertionError(h.error)
            priya_index = nul_names.index(PRIYA)
            why = nul_rows.nth(priya_index).locator(".why").inner_text()
            if why.strip() != "a wish, not something that happened":
                h.fail(f"expected Priya's plain-words reason to be the wish phrase, got {why!r}")
                raise AssertionError(h.error)
            if MARCUS in nul_names:
                h.fail("Marcus's concrete evidence should not also appear in said-but-didn't-count")
                raise AssertionError(h.error)

        passed = True
    finally:
        founder_context.close()
        duration = time.monotonic() - started
        finalize_run(run_dir, scenario=scenario, passed=passed,
                     failed_step=recorder.failed_step, duration_s=duration)
        print(f"\nrun bundle: {run_dir}")
