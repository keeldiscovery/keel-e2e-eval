"""Drives the locally installed `claude` CLI headless, playing the role of the real agent client
the shaping gauntlet's Layer 2 puts in front of a scripted founder (specs/shaping-eval-design.md
§1: "the playground's shape, automated"). Never stubbed -- design's own boundary: "the agent
process gets ONLY what a real host gets" -- the real keel-discovery SKILL.md (copied fresh from
the keel-skill checkout every run, never hand-edited: this repo does not touch keel-skill) and the
real MCP stack, reached over the same HTTP a real `claude` CLI's own MCP client speaks.

Confirmed live against this machine's own `claude` CLI (v2.1.251, 2026-08-30) before writing this
module, not assumed from `--help` alone:

1. `claude -p "<line>" --output-format json --dangerously-skip-permissions` exits 0 and prints one
   JSON object on stdout carrying (among many cost/usage fields this module ignores) `session_id`
   (the id `--resume` takes), `result` (the assistant's final turn, plain text) and `is_error`.
2. `claude -p --resume <id> "<line>" --output-format json --dangerously-skip-permissions` reuses
   that same session id and continues the conversation -- confirmed with a two-turn probe
   ("pong" / "pang") that came back correctly ordered.

Neither call printed anything to stderr in that probe; a non-zero exit or a JSON-decode failure on
stdout is this module's only signal the CLI itself is broken, and `is_error: true` in the parsed
body is the signal a turn *ran* but the agent reported trouble.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from harness.steps import Recorder

MCP_SERVER_NAME = "keel"
SKILL_DIR_NAME = "keel-discovery"

_BASE_ARGS = ("-p", "--strict-mcp-config", "--dangerously-skip-permissions",
              "--output-format", "json")


class AgentSessionError(RuntimeError):
    """The claude CLI is missing, or the FIRST call in a session failed -- the task's own
    contract: "If the claude CLI is missing or errors on first call, fail fast with a clear
    message -- never stub the agent." A later turn's failure is captured onto that turn's own
    `Turn.ok=False` instead of raised, so a partial conversation still leaves an honestly-
    truncated, scoreable transcript (evals/test_shaping_gauntlet.py decides what to do with it)."""


@dataclass
class Turn:
    index: int
    founder_line: str
    agent_reply: str
    raw: dict = field(default_factory=dict)
    duration_s: float = 0.0
    ok: bool = True
    error: str | None = None


def require_claude_cli() -> str:
    path = shutil.which("claude")
    if not path:
        raise AgentSessionError(
            "the `claude` CLI is not on PATH -- Layer 2 (make eval-shaping) requires the real, "
            "locally installed Claude Code CLI, headless. Install it and retry; this harness "
            "never stubs the agent (design's own boundary)."
        )
    return path


def prepare_workspace(workspace_dir: Path, skill_md_source: Path, mcp_base_url: str,
                       agent_key: str) -> Path:
    """Builds the throwaway workspace a real host would give this agent: `.claude/skills/
    keel-discovery/SKILL.md` copied verbatim from the keel-skill checkout (this repo's own
    boundary: never edit keel-skill, and a copy -- not a symlink -- survives an `rmtree` cleanup
    without touching the source), and `.mcp.json` pointing at the real stack's `/mcp` endpoint
    with the harness's own agent key header, exactly what a real agent host would hold (design
    §2: "the agent process gets ONLY what a real host gets"). Returns the `.mcp.json` path.
    """
    if not skill_md_source.exists():
        raise AgentSessionError(
            f"no SKILL.md at {skill_md_source} -- check the keel-skill sibling checkout")
    skill_dir = workspace_dir / ".claude" / "skills" / SKILL_DIR_NAME
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(skill_md_source.read_text())
    # The shipped founder workspace (keel-playground) carries a one-line CLAUDE.md framing the
    # room; the gauntlet mirrors the real host shape exactly -- fidelity, not scaffolding
    # (DRIFT #8: the first run omitted it and also exposed the skill's own activation gap,
    # fixed separately in keel-skill 2.4.0's description).
    (workspace_dir / "CLAUDE.md").write_text(
        "This is a founder's workspace. Keel is available through the configured Keel MCP "
        "tools;\nthe keel-discovery skill teaches how to use them. There is no code here to "
        "explore.\n")

    mcp_config = {
        "mcpServers": {
            MCP_SERVER_NAME: {
                "type": "http",
                "url": f"{mcp_base_url.rstrip('/')}/mcp",
                "headers": {"X-Keel-Agent-Key": agent_key},
            }
        }
    }
    mcp_config_path = workspace_dir / ".mcp.json"
    mcp_config_path.write_text(json.dumps(mcp_config, indent=2))
    return mcp_config_path


class AgentSession:
    """One `claude` CLI conversation, `--resume`d turn by turn. `send()` is the only thing a
    caller needs after construction -- the workspace, mcp config, and session id are this
    class's own bookkeeping.
    """

    def __init__(self, workspace_dir: Path, mcp_config_path: Path, recorder: Recorder | None = None,
                 *, timeout_s: float = 180.0):
        self.workspace_dir = workspace_dir
        self.mcp_config_path = mcp_config_path
        self.recorder = recorder
        self.timeout_s = timeout_s
        self.session_id: str | None = None
        self.turns: list[Turn] = []
        self._claude = require_claude_cli()

    def _run(self, args: list[str]) -> dict:
        started = time.monotonic()
        result = subprocess.run(
            [self._claude, *args],
            cwd=str(self.workspace_dir),
            capture_output=True, text=True, timeout=self.timeout_s,
        )
        duration = time.monotonic() - started
        if result.returncode != 0:
            raise AgentSessionError(
                f"`claude` exited {result.returncode}: stderr={result.stderr.strip()[:2000]!r}")
        try:
            body = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise AgentSessionError(
                f"`claude` did not print valid JSON on stdout: {exc}; "
                f"stdout={result.stdout[:2000]!r}"
            ) from exc
        return {"body": body, "duration_s": duration}

    def send(self, founder_line: str, *, fact_released: str | None = None) -> Turn:
        """Sends one founder line and returns the agent's reply. The first call starts a fresh
        session (nothing to `--resume` yet); every later call resumes `self.session_id`, and also
        re-supplies `--mcp-config`/`--strict-mcp-config` -- each CLI invocation is a fresh process,
        so the MCP server has to be named again even on a resumed session.

        A failure on the FIRST call re-raises `AgentSessionError` (fail fast, never stub -- this
        module's own contract). A failure on any LATER call is captured onto the returned `Turn`
        (`ok=False`) instead, so the conversation ends there but everything before it is still a
        legitimate, scoreable partial transcript.

        `fact_released`, if given, is purely for the transcript (harness/founder_sim.py decided
        it, not this class) -- which fact id, if any, this founder line was releasing for the
        first time this run.
        """
        args = ["--mcp-config", str(self.mcp_config_path), *_BASE_ARGS]
        index = len(self.turns) + 1
        if self.session_id is not None:
            args = [*args, "--resume", self.session_id]
        args = [*args, founder_line]

        try:
            outcome = self._run(args)
        except AgentSessionError:
            if self.session_id is None:
                raise  # first call: fail fast, per this module's own contract
            turn = Turn(index=index, founder_line=founder_line, agent_reply="", ok=False,
                        error="claude CLI call failed after the session was already established "
                              "(see the run's own stderr capture, if any, for detail)")
            self.turns.append(turn)
            self._record(turn, fact_released)
            return turn

        body = outcome["body"]
        self.session_id = body.get("session_id") or self.session_id
        reply = body.get("result") or ""
        ok = not body.get("is_error", False)
        turn = Turn(index=index, founder_line=founder_line, agent_reply=reply, raw=body,
                    duration_s=outcome["duration_s"], ok=ok,
                    error=None if ok else f"claude reported is_error=true (subtype={body.get('subtype')})")
        self.turns.append(turn)
        self._record(turn, fact_released)
        return turn

    def _record(self, turn: Turn, fact_released: str | None) -> None:
        if self.recorder is None:
            return
        with self.recorder.interaction("shaping-turn"):
            with self.recorder.step(f"turn {turn.index}: founder says", party="founder",
                                     kind="note") as h:
                h.capture_text("founder_line", turn.founder_line)
            with self.recorder.step(f"turn {turn.index}: agent replies", party="agent",
                                     kind="protocol") as h:
                h.record_wire({"founder_line": turn.founder_line}, turn.raw)
                h.capture_text("agent_reply", turn.agent_reply)
                h.capture_text("fact_released", fact_released or "none")
                if not turn.ok:
                    h.fail(turn.error or "agent turn failed")
