"""S-008 -- wrong-moment visits (feedback item 7's blind spot; founder-experience design §4 item 3).

Every eval scenario before this one visits a screen only once its data actually exists: a stage
after it is framed, People after a role exists, the brief after `READY_TO_BUILD`. Item 7 of the
2026-08-30 feedback session existed precisely because nobody had checked the *other* moments -- a
founder (or a stray link, or an impatient double-click) can reach any of these screens before
there is anything to show, and what renders there is either a designed, founder-worded quiet state
(the fix) or the wire's own raw refusal leaking through (the bug the fix was for).

This scenario does the one thing every other scenario in this eval set deliberately avoids:
**stops right after `CREATE`** -- one action, no `FRAME` for SOLUTION/COMMERCIAL, no role, nothing
`READY_TO_BUILD` about it -- and then visits three screens that, at this exact moment, have
nothing real to show:

1. **A stage pre-framing** (SOLUTION has never been framed) -- `StageRoute.tsx`'s own "Not
   described yet" state.
2. **People pre-gate** (no role has ever been introduced -- necessarily before the invite gate,
   founder-experience design §6, could ever be open) -- `PeopleRoute.tsx`'s "Nobody can be asked
   anything yet."
3. **Brief pre-`READY_TO_BUILD`** -- keel-web's own designed "not yet" state
   (`BriefRoute.BRIEF_NOT_YET_TEXT`), never the wire's raw 409 `{rule, problem, remedy}`.

Each is asserted twice: the specific founder-worded sentence keel-web is documented to show, and a
generic sweep (`evals.policy.clarity_violations` plus a few wire-only markers -- `rule`, `remedy`,
an HTTP status code) proving nothing from the refusal shape leaked through. Scored on ORIENTATION
(does the screen still orient the founder, even with nothing to show) and CLARITY (founder words,
never wire words) -- no FIDELITY facts are declared, the same honest absence S-007 declares for the
same reason (nothing founder-authored exists yet to trace hop-by-hop).
"""

from __future__ import annotations

import re
import time

from evals import policy
from evals.scenario import Fact, Scenario, find_role
from harness.browser import FounderBrowser
from harness.driver import FounderAgentDriver
from harness.evidence import finalize_run
from harness.steps import Recorder, StepHandle

ROLE_LABEL = "Payroll Ops Manager"
PROBLEM_CLAIM = "Payroll managers at mid-size companies lose hours each month chasing payroll exceptions."
ASSUMPTION = "They handle payroll exceptions themselves, at least monthly."
HEADING = "Manual exception chasing"
ASK = "Tell me about the last time you had to chase down a payroll exception by hand."
DISCONFIRMING = "Has there been a month where you had no exceptions to chase down at all?"

_STATUS_CODE_RE = re.compile(r"\b[45]\d{2}\b")
_WIRE_ONLY_WORDS = ("remedy", "rule:")


def _assert_no_wire_leak(h: StepHandle, text: str) -> None:
    """Nothing about a refusal's shape -- its enum vocabulary, its JSON punctuation, its {rule,
    problem, remedy} field names, an HTTP status code -- may leak into a founder-worded quiet
    state (founder-experience design §4 item 3)."""
    violations = policy.clarity_violations(text)
    if violations:
        h.fail(f"founder-facing quiet state leaked wire vocabulary {violations}: {text!r}")
        raise AssertionError(h.error)
    lowered = text.lower()
    leaked_words = [w for w in _WIRE_ONLY_WORDS if w in lowered]
    if leaked_words:
        h.fail(f"founder-facing quiet state mentions wire-only word(s) {leaked_words}: {text!r}")
        raise AssertionError(h.error)
    status_match = _STATUS_CODE_RE.search(text)
    if status_match:
        h.fail(f"founder-facing quiet state names a raw status code {status_match.group(0)!r}: {text!r}")
        raise AssertionError(h.error)


class S008WrongMoment(Scenario):
    name = "S-008 wrong-moment visits"
    slug = "s008-wrong-moment"

    def project_name(self) -> str:
        return "Payroll Exception Radar (Wrong Moment)"

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
        return [{"statement": ASSUMPTION, "heading": HEADING, "stage": "PROBLEM", "risk": "LOAD_BEARING",
                 "askedOf": role_id, "question": {"ask": ASK, "probes": [], "disconfirming": DISCONFIRMING}}]

    def about_line(self, stage: str) -> str:
        return "A few quick questions about how payroll exception handling goes day to day."

    def person_name(self, stage: str) -> str:
        return "Jordan Casey"

    def participant_answer(self, stage: str) -> str:
        return "Just last month I spent about three hours tracking down a payroll exception."

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
        # Nothing founder-authored exists yet at any of the moments this scenario visits -- there
        # is nothing to trace hop-by-hop, the same honest absence S-007 declares for its own,
        # different reason (protocol negatives, no browser at all).
        return {}


def test_s008_wrong_moment(stack, run_dir, browser):
    recorder = Recorder(run_dir)
    scenario = S008WrongMoment()
    cloud_base = f"http://localhost:{stack.cloud_port}"
    founder_web_base = f"http://localhost:{stack.web_port}/p"

    driver = FounderAgentDriver(cloud_base, recorder, scenario)
    passed = False
    started = time.monotonic()
    founder_context = browser.new_context()
    try:
        founder_page = founder_context.new_page()
        founder = FounderBrowser(founder_page, founder_web_base, recorder, get_state=driver.get_state)

        # CREATE only. PROBLEM is framed as a side effect (the aggregate's own rule); SOLUTION and
        # COMMERCIAL are not, no role has ever been introduced, and the project is nowhere near
        # READY_TO_BUILD. Every screen visited from here on is a wrong-moment visit by construction.
        driver.advance_one()
        project_id = driver.project_id
        assert project_id

        # 1. A stage pre-framing (item 7's blind spot, reachable): SOLUTION has never been framed.
        founder.open_stage(project_id, "SOLUTION")
        with recorder.step("an unframed stage reads a founder-worded quiet state, not wire text",
                            party="founder", kind="assert") as h:
            card_text = founder_page.locator(".card.openc").first.inner_text()
            h.record_assert("'Not described yet', no wire leak", card_text)
            if "not described yet" not in card_text.lower():
                h.fail(f"expected the unframed-stage quiet state, got {card_text!r}")
                raise AssertionError(h.error)
            _assert_no_wire_leak(h, card_text)

        # 2. People, before any role exists at all -- the truest "nothing to show" moment here, and
        # necessarily before the invite gate (founder-experience design §6) could ever be open.
        founder.open_people(project_id)
        with recorder.step("People, with no role yet, reads a founder-worded quiet state, not wire text",
                            party="founder", kind="assert") as h:
            body_text = founder_page.locator("body").inner_text()
            h.record_assert("'Nobody can be asked anything yet', no wire leak", body_text)
            if "nobody can be asked anything yet" not in body_text.lower():
                h.fail(f"expected the no-roles-yet quiet state, got {body_text!r}")
                raise AssertionError(h.error)
            _assert_no_wire_leak(h, body_text)

        # 3. Brief, long before READY_TO_BUILD -- keel-web's own designed "not yet" state, never
        # the wire's raw 409 {rule, problem, remedy} (founder-experience design §4 item 3).
        founder.open_brief(project_id)
        with recorder.step("Brief, before READY_TO_BUILD, reads a founder-worded quiet state, "
                            "not the wire's 409", party="founder", kind="assert") as h:
            hint_text = founder_page.locator(".card.openc .hint").first.inner_text()
            h.record_assert("BRIEF_NOT_YET_TEXT, no wire leak", hint_text)
            if "no brief yet" not in hint_text.lower():
                h.fail(f"expected the brief's not-yet quiet state, got {hint_text!r}")
                raise AssertionError(h.error)
            _assert_no_wire_leak(h, hint_text)

        passed = True
    finally:
        founder_context.close()
        duration = time.monotonic() - started
        finalize_run(run_dir, scenario=scenario, passed=passed,
                     failed_step=recorder.failed_step, duration_s=duration)
        print(f"\nrun bundle: {run_dir}")
