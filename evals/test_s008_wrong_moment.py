"""S-008 -- wrong-moment visits (feedback item 7's blind spot; founder-experience design §4 item 3),
now also the auth-moment sweep (round 2, task item 5).

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

**Round 2 addition -- the wrong *moment* to hold no session at all.** A fourth wrong-moment visit,
the same family as the other three (nothing real to show, and what renders instead must be
founder-worded, never wire-shaped): a founder screen opened by a browser context that never logged
in at all. `AppRoutes.tsx`'s `AuthGate` routes any 401 to `/login` (this harness's own account
always exists by the time this scenario runs, `evals/conftest.py`'s `founder_credentials` fixture
having already provisioned it -- so this is always the `/login` branch, never `/setup`). The
*other* branch (`accountExists === false` routing to `/setup`) is a genuinely once-per-stack-
lifetime moment -- captured instead in `evals/conftest.py`'s `founder_credentials` fixture, before
it provisions the account, rather than reproduced here; see that fixture's own docstring for the
judgement call.
"""

# Journey coverage (CANON.md ledger): proves §1.0's arrival gates (login/setup routing) and
# §1.2's no-status-before-approval quiet states at their wrong moments.

from __future__ import annotations

import re
import time

from evals import policy
from evals.recipes import arrive_and_create, open_founder_session
from evals.scenario import Fact, Scenario, find_role
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


def test_s008_wrong_moment(stack, run_dir, browser, founder_credentials):
    recorder = Recorder(run_dir)
    scenario = S008WrongMoment()
    founder_web_base = f"http://localhost:{stack.web_port}/p"
    passed = False
    started = time.monotonic()
    driver, founder, founder_context = open_founder_session(stack, founder_credentials, recorder,
                                                              scenario, browser)
    founder_page = founder.page
    try:
        # CREATE only (via the shared opening step, task item 2). PROBLEM is framed as a side
        # effect (the aggregate's own rule); SOLUTION and COMMERCIAL are not, no role has ever
        # been introduced, and the project is nowhere near READY_TO_BUILD. Every screen visited
        # from here on is a wrong-moment visit by construction.
        project_id = arrive_and_create(driver, founder, scenario)
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

        # 4. Round 2's own auth-moment addition (task item 5): a founder screen opened by a
        # browser context that never logged in at all -- a fresh context, never `founder.log_in`.
        # `AuthGate` routes the resulting 401 to `/login` (this instance's account already exists
        # by the time this scenario runs) -- founder-worded, never the wire's own 401 body.
        unauth_context = browser.new_context()
        try:
            unauth_page = unauth_context.new_page()
            with recorder.step("an unauthenticated founder screen visit routes to login, "
                                "founder-worded, no wire text", party="founder", kind="assert") as h:
                unauth_page.goto(f"{founder_web_base}/{project_id}", wait_until="load")
                unauth_page.wait_for_url("**/login", timeout=10_000)
                heading = unauth_page.locator("h1.auth-title").inner_text()
                body_text = unauth_page.locator("body").inner_text()
                h.record_assert("routed to /login, 'Log in' heading, no wire leak",
                                 {"url": unauth_page.url, "heading": heading})
                if "log in" not in heading.lower():
                    h.fail(f"expected the login screen's own heading, got {heading!r} at {unauth_page.url}")
                    raise AssertionError(h.error)
                _assert_no_wire_leak(h, body_text)
        finally:
            unauth_context.close()

        passed = True
    finally:
        founder_context.close()
        duration = time.monotonic() - started
        finalize_run(run_dir, scenario=scenario, passed=passed,
                     failed_step=recorder.failed_step, duration_s=duration)
        print(f"\nrun bundle: {run_dir}")
