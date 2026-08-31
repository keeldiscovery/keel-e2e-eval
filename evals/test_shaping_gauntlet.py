"""Layer 2 of the shaping gauntlet (specs/shaping-eval-design.md §1) -- a real `claude` CLI agent,
headless, loaded with the actual keel-discovery SKILL.md and the real MCP stack
(harness/agent_session.py), converses with a scripted founder simulator (harness/founder_sim.py)
that opens vague per phase and holds a small fact bank hostage, released only on a keyword-matched
probe. LLM in the loop, real API spend, opt-in -- `pytestmark` below carries the `shaping` marker
`pytest.ini` excludes by default, so this module is invisible to `make eval`/`make eval-all`'s
bare `pytest evals -q`; `make eval-shaping` is the one command that re-includes it
(`-m shaping`, overriding the default `-m "not shaping"`).

**The verdict is a pure function of stack state, not the transcript** (design §1's own words):
after the conversation, this reads the founder-session `GET /v2/projects/{id}/stages/{stage}`
(`FounderAgentDriver.get_stage_card`, no agent token needed -- the project may well be sitting at
a REVIEW handoff by the time the gauntlet ends, which has no token to mint at all) for PROBLEM,
SOLUTION and COMMERCIAL, and computes SHP-1..SHP-7 (`harness/shaping_scoring.py`) against what the
founder simulator actually released this run -- never against the transcript, and never against
what the simulator merely *said* (a claim quoting the simulator's own opener is not evidence of
anything; only the fact bank's held-back facts are).

**Phase-to-protocol-stage alignment is a judgement call, not a guarantee.** The real protocol's own
choreography (harness/driver.py's module docstring) frames all three stages up front, then
decomposes only the earliest stage needing it -- so within this gauntlet's bounded turn budget,
SOLUTION/COMMERCIAL will likely only ever be *framed* (a claim, no beliefs yet), while PROBLEM
alone reaches roles+assumptions. SHP-1/3/4 are scored off each stage's own *claim* text
accordingly (never off beliefs that plausibly do not exist yet); SHP-6 (near-duplicates) and the
belief-level half of SHP-5/7 are scored off PROBLEM's own beliefs, the one stage this gauntlet's
phase order and turn budget give a real chance to reach ASSUMPTIONS on.

A failing SHP check here is a *methodology* finding about the CREATE/FRAME/INTRODUCE_ASSUMPTIONS
instruction text (v2-instructions.yaml) -- design §2's contamination pass names, explicitly, the
temptation this file must never give in to: tune `v2-instructions.yaml`, never
`harness/founder_sim.py`, to make a red run go green.

**Relay re-venue (relay-design.md §12 item 3), unchanged measurement.** `founder_sim`'s turns and
the real `claude` CLI's own replies now ALSO travel the relay -- every founder line this gauntlet
sends and every reply `claude` gives is posted through `FounderRelay`/`AgentRelay` alongside the
existing `claude -p --resume` call, so the same conversation the ChatPane would render is really on
the wire. **Judgement call, made explicit rather than silently assumed**: the `claude` CLI cannot
itself poll the relay (design §12 item 3's own words: "the bridge feeds founder turns to it exactly
as before") -- this test plays the bridge's role directly (it already knows both sides of the
conversation, so there is nothing to actually long-poll for), posting the founder's line and then
`claude`'s reply as the two relay turns that same exchange produces, in order. The relay can only
address a project that exists, and this gauntlet's own conversation starts before any project does
(the same "opens vague" design the fact bank hostage depends on) -- so the first handful of turns,
before `claude` ever calls `keel_create`, are never retroactively relayed; the moment a fresh
project id is first observed (a cheap `reader.arrive()` read, already this module's own harness-
only side channel), every turn from then on rides the relay too. SHP-1..SHP-7 are computed exactly
as before, from stack state (`get_stage_card`), never from the relay transcript -- the relay is
additional evidence here, not a new input to the score.
"""

from __future__ import annotations

import shutil
import tempfile
import time
from pathlib import Path

import pytest

from evals.recipes import open_relay
from harness import shaping_scoring
from harness.agent_session import AgentSession, AgentSessionError, prepare_workspace
from harness.bridge import BridgeReply
from harness.driver import FounderAgentDriver
from harness.evidence import generate_report, write_verdict
from harness.founder_sim import ASSUMPTIONS, COMMERCIAL, PROBLEM, SOLUTION, FounderSimulator
from harness.steps import Recorder

pytestmark = pytest.mark.shaping

STAGE_ORDER = (PROBLEM, SOLUTION, COMMERCIAL, ASSUMPTIONS)
MAX_TURNS_PER_STAGE = 15
WALL_CLOCK_BUDGET_S = 15 * 60
CLI_TIMEOUT_S = 180.0


def _fetch_stage(reader: FounderAgentDriver, project_id: str | None, stage: str
                  ) -> shaping_scoring.StageSnapshot:
    if project_id is None:
        return shaping_scoring.empty_stage(stage)
    card = reader.get_stage_card(project_id, stage)
    return shaping_scoring.stage_snapshot_from_card(stage, card)


def test_shaping_gauntlet(stack, run_dir, founder_credentials):
    recorder = Recorder(run_dir)
    sim = FounderSimulator()
    workspace_dir = Path(tempfile.mkdtemp(prefix="keel-shaping-workspace-"))
    cloud_base = f"http://localhost:{stack.cloud_port}"
    passed = False
    started = time.monotonic()
    try:
        mcp_config_path = prepare_workspace(workspace_dir, stack.skill_md_path, cloud_base,
                                             founder_credentials.agent_key)
        session = AgentSession(workspace_dir, mcp_config_path, recorder, timeout_s=CLI_TIMEOUT_S)

        # A harness-only side channel (the same status `get_founder_roles`/`get_founder_people`
        # already carry): this driver never submits anything -- it only reads the arrival list
        # (to find the project the real agent creates) and, later, each stage's founder-session
        # card. `scenario=None` is safe because neither `create_project`/`advance_one` is ever
        # called on it.
        reader = FounderAgentDriver(cloud_base, recorder, None, agent_key=founder_credentials.agent_key)
        reader.log_in(founder_credentials.email, founder_credentials.password)
        before = reader.arrive()
        before_ids = {p["projectId"] for p in (before.get("projects") or [])}

        # Relay re-venue (module docstring): populated the moment a fresh project id is first
        # observed mid-conversation; every turn before that point is never retroactively relayed
        # (the relay can only address a project that exists).
        relay_project_id: str | None = None
        founder_relay = agent_relay = None

        try:
            for stage in STAGE_ORDER:
                reply_text = ""
                consecutive_quiet = 0
                for turn_i in range(MAX_TURNS_PER_STAGE):
                    if time.monotonic() - started > WALL_CLOCK_BUDGET_S:
                        recorder.note("wall-clock budget exceeded -- ending the gauntlet early",
                                      party="stack")
                        raise _WallClockBudgetExceeded()
                    if turn_i == 0:
                        line, fact_id = sim.opener(stage), None
                    else:
                        outcome = sim.respond(reply_text)
                        line = outcome.reply
                        fact_id = outcome.fact_id if outcome.newly_earned else None
                    turn = session.send(line, fact_released=fact_id)
                    if not turn.ok:
                        break
                    reply_text = turn.agent_reply

                    if relay_project_id is None:
                        probe = reader.arrive()
                        fresh = [p["projectId"] for p in (probe.get("projects") or [])
                                 if p["projectId"] not in before_ids]
                        if fresh:
                            relay_project_id = fresh[0]
                            founder_relay, agent_relay = open_relay(reader, relay_project_id)
                    if founder_relay is not None:
                        founder_relay.post_turn(line)
                        agent_relay.post_turns([BridgeReply(text=reply_text).to_turn_input()])

                    consecutive_quiet = 0 if "?" in reply_text else consecutive_quiet + 1
                    if turn_i > 0 and consecutive_quiet >= 2:
                        break  # the agent stopped asking questions -- move to the next phase
        except _WallClockBudgetExceeded:
            pass
        except AgentSessionError as exc:
            pytest.fail(f"the claude CLI failed on its first call -- Layer 2 requires the real "
                        f"agent, never a stub: {exc}")

        after = reader.arrive()
        new_ids = [p["projectId"] for p in (after.get("projects") or []) if p["projectId"] not in before_ids]
        project_id = new_ids[0] if new_ids else None
        if project_id is None:
            recorder.note("the conversation never produced a new project", party="stack",
                          ok=False, error="no fresh project id found after the gauntlet's own conversation")

        problem = _fetch_stage(reader, project_id, PROBLEM)
        solution = _fetch_stage(reader, project_id, SOLUTION)
        commercial = _fetch_stage(reader, project_id, COMMERCIAL)

        checks = shaping_scoring.compute_shp_checks(problem, solution, commercial, sim)
        score = shaping_scoring.shaping_score(checks)
        passed = project_id is not None and all(c.passed for c in checks)

        shaping_scoring.write_shaping_bundle(run_dir, checks=checks, score=score, sim=sim,
                                              project_id=project_id)
    finally:
        duration = time.monotonic() - started
        shutil.rmtree(workspace_dir, ignore_errors=True)
        write_verdict(run_dir, scenario="shaping-gauntlet", passed=passed,
                      failed_step=recorder.failed_step, duration_s=duration)
        generate_report(run_dir)
        print(f"\nrun bundle: {run_dir}")


class _WallClockBudgetExceeded(Exception):
    """Internal control-flow signal only -- breaks out of the nested stage/turn loops the moment
    the ~15-minute wall-clock budget (design §1's "bounded at ~15 turns per stage") is spent,
    without losing whatever the conversation already produced."""
