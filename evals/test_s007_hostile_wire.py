"""S-007 -- the wire pushes back (T012; protocol negatives, no browser).

Four ways a lost or confused agent can hit the wire, and what it gets back, on its own fresh
project (design §5 independence pass):

1. **Unknown screen** -- `keel_open_web` (MCP-only, `harness/mcp_client.py`'s docstring) refused
   with rule `screen`, remedy naming the five real ones.
2. **Ungranted handle** -- `get_context` for a handle the current token's action was never granted
   (`HandleGrants`), refused with rule `context`.
3. **A payload fault the token survives** -- a schema-invalid `FRAME` payload refused with rule
   `schema` (`Payloads`'s own validation, before any domain call), then the *same* token
   resubmitted with a corrected payload succeeds -- nothing about the fault invalidated it.
4. **A stale token after a "concurrent" commit** -- the realistic shape of this, absent a second
   real actor: an agent that never saw its own successful response and retries the identical
   submit. The token's revision has already moved (its own first attempt wrote it), so the retry
   is refused with rule `concurrency` (`ProjectConcurrentlyModified`, the compare-and-swap losing
   a race against reality) -- and recovering (get_next for a fresh token) finds the founder's
   original facts (the one role actually introduced) exactly once, not duplicated and not lost.

Every refusal is scored as its own `agent-refusal` interaction (harness/rubric.py's
`_agent_refusal_checks`, GUI-R1/ORI-R1 -- design §3: "its GUIDANCE checks measure whether the
*remedies* would tell a lost agent what to do"). No ui-visit or participant-page interaction ever
happens here, so ORIENTATION's/CLARITY's UI-only checks and every FIDELITY check (no fact registry
is declared) never fire at all -- `not_applicable_categories` names them, per design §6.1 (T003),
rather than the run score silently treating them as zero.
"""

from __future__ import annotations

import time

from evals.scenario import Fact, Scenario, find_role
from harness.driver import FounderAgentDriver, ProtocolError
from harness.evidence import finalize_run
from harness.mcp_client import McpClient, McpToolError
from harness.steps import Recorder

ROLE_LABEL = "Payroll Ops Manager"
PROBLEM_CLAIM = "Payroll managers at mid-size companies lose hours each month chasing payroll exceptions."


class S007HostileWire(Scenario):
    name = "S-007 hostile wire"
    slug = "s007-hostile-wire"

    def project_name(self) -> str:
        return "Payroll Exception Radar (Hostile Wire)"

    def problem_statement(self) -> str:
        return PROBLEM_CLAIM

    def frame_statement(self, stage: str) -> str:
        return {"SOLUTION": "A tool that flags and routes payroll exceptions automatically.",
                "COMMERCIAL": "$30 a seat per month."}[stage]

    def facts(self) -> dict[str, Fact]:
        return {}  # protocol negatives only -- no UI, no participant, nothing to trace hop-by-hop


def _capture_refusal(recorder: Recorder, step_name: str, err) -> None:
    with recorder.step(step_name, party="agent", kind="assert") as h:
        h.capture_text("rule", err.rule or "")
        h.capture_text("problem", err.problem or "")
        h.capture_text("remedy", err.remedy or "")
        h.record_assert("an actionable {rule, problem, remedy}", {"rule": err.rule, "problem": err.problem,
                                                                     "remedy": err.remedy})


def test_s007_hostile_wire(stack, run_dir):
    recorder = Recorder(run_dir)
    scenario = S007HostileWire()
    cloud_base = f"http://localhost:{stack.cloud_port}"

    driver = FounderAgentDriver(cloud_base, recorder, scenario)
    passed = False
    started = time.monotonic()
    try:
        driver.advance_one()  # CREATE (frames PROBLEM as a side effect)
        driver.advance_one()  # FRAME SOLUTION
        driver.advance_one()  # FRAME COMMERCIAL

        # get_next now recommends INTRODUCE_ROLES (PROBLEM's decompose step) -- every probe below
        # uses this one issuance's token/context. Reused as `issuance_id` so the schema-fault-then-
        # corrected submit folds into the SAME reviewable interaction as the issuance that granted
        # the token (browser.py's `_continue_current_interaction` pattern, ported to the wire).
        issuance_id = recorder.new_interaction_id()
        with recorder.interaction("agent-cycle", issuance_id):
            issuance = driver.get_next()
        assert issuance["kind"] == "action" and issuance["action"] == "INTRODUCE_ROLES", issuance
        token = issuance["token"]

        # ---------------------------------------------------------- 1. unknown screen (MCP-only)
        with recorder.interaction("agent-refusal"):
            mcp = McpClient(cloud_base, recorder)
            mcp.initialize()
            try:
                mcp.call_tool("keel_open_web", {"projectId": driver.project_id, "screen": "not-a-screen"})
                raise AssertionError("expected a 'screen' refusal for an unknown screen name")
            except McpToolError as err:
                _capture_refusal(recorder, "unknown screen refusal", err)
                assert err.rule == "screen", err.rule
                for name in ("overview", "stage", "invite", "invitations", "brief"):
                    assert name in (err.remedy or ""), f"remedy should list {name!r}: {err.remedy!r}"

        # ------------------------------------------------------------- 2. ungranted handle
        with recorder.interaction("agent-refusal"):
            # INTRODUCE_ROLES grants [opportunity, roles] (HandleGrants) -- "response" is not one.
            try:
                driver.get_context(token, "response")
                raise AssertionError("expected a 'context' refusal for an ungranted handle")
            except ProtocolError as err:
                _capture_refusal(recorder, "ungranted handle refusal", err)
                assert err.rule == "context", err.rule

        # ------------------------------------------------ 3. a payload fault the token survives
        with recorder.interaction("agent-refusal"):
            try:
                driver._submit(token, {}, "INTRODUCE_ROLES (malformed: no roles field)")
                raise AssertionError("expected a 'schema' refusal for a missing required field")
            except ProtocolError as err:
                _capture_refusal(recorder, "schema-fault refusal", err)
                assert err.rule == "schema", err.rule

        with recorder.interaction("agent-cycle", issuance_id):
            # The SAME token, corrected payload -- the schema fault never touched it.
            result = driver._submit(token, {"roles": [
                {"label": ROLE_LABEL, "roleType": "MANAGER", "about": "How payroll runs work"},
            ]}, "INTRODUCE_ROLES (corrected)")
        driver.project_id = result["projectId"]

        # --------------------------------------------------- 4. stale token after a "concurrent" commit
        # The realistic shape of this without a second real actor: the agent never saw its own
        # successful response and retries the identical submit. Its own prior success already
        # moved the revision, so the retry is refused with 'concurrency', not silently re-applied.
        with recorder.interaction("agent-refusal"):
            try:
                driver._submit(token, {"roles": [
                    {"label": ROLE_LABEL, "roleType": "MANAGER", "about": "How payroll runs work"},
                ]}, "INTRODUCE_ROLES (retried against the same now-stale token)")
                raise AssertionError("expected a 'concurrency' refusal for a stale-revision token")
            except ProtocolError as err:
                _capture_refusal(recorder, "stale-token-after-a-commit refusal", err)
                assert err.rule == "concurrency", err.rule

        # Facts preserved on retry: exactly one role exists, not two -- the retried resubmission
        # never actually wrote anything (the compare-and-swap refused it before persisting).
        # get_next now recommends INTRODUCE_ASSUMPTIONS (roles already exist), which grants
        # 'roles' too (HandleGrants), so this is a plain read against the next legitimate token.
        with recorder.interaction("agent-cycle"):
            fresh = driver.get_next()
            assert "roles" in (fresh.get("context") or []), fresh
            roles_view = driver.get_context(fresh["token"], "roles")
        role_count = len([r for r in roles_view.get("roles", []) if r["label"] == ROLE_LABEL])
        assert role_count == 1, f"expected exactly one {ROLE_LABEL!r} role after the retry, found {role_count}"

        passed = True
    finally:
        duration = time.monotonic() - started
        finalize_run(run_dir, scenario=scenario, passed=passed,
                     failed_step=recorder.failed_step, duration_s=duration)
        print(f"\nrun bundle: {run_dir}")
