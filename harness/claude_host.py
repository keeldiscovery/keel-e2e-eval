"""Claude Code as a **host** (spec `019-journey-through-a-host`; keel-cloud
`canon/designs/keel-skill-design.md` §5, and `canon/designs/e2e-matrix-design.md` §5.1).

The Copilot half of this pair (`harness/copilot_host.py`, spec 016) was written first and this one
is *mostly a rename* -- the design says so in as many words. What is not a rename is written out
below, because every one of these four differences was measured on 2026-09-10 with CLI **2.1.268**
and each changed a line of code.

**1. An isolated home does not keep the founder's login, and that is the headline.** `COPILOT_HOME`
moves Copilot's configuration while the stored OAuth credential stays outside it, so spec 016's
isolation was free. `CLAUDE_CONFIG_DIR` is not like that: `claude auth status` in a fresh config
dir answers `{"loggedIn": false, "authMethod": "none"}` while the same command against
`~/.claude` answers `{"loggedIn": true, "authMethod": "claude.ai"}`. **A Claude cell therefore
needs a credential in the caller's own shell** -- `ANTHROPIC_API_KEY`, or a
`CLAUDE_CODE_OAUTH_TOKEN` from `claude setup-token` for a subscription. `readiness()` probes
exactly that, in a throwaway empty config dir, and refuses to start rather than letting a paid run
discover it. Same rule as spec 013's T-5: the secret comes from the caller's shell, never from a
file and never from a keychain this harness went looking in.

**2. There is no `claude skill list`.** The proof that the skill is present and came from the
plugin is `claude plugin details keel`'s **component inventory** -- `Skills (1)  keel-connect`.
That is a stronger reading than Copilot's, not a weaker one: the inventory belongs to the plugin
by construction, so a `keel-connect` sitting in some personal skills directory cannot satisfy it,
which on the Copilot side needs an explicit `source` field to rule out.

**3. `--no-custom-instructions` does not exist here.** Copilot has a flag that keeps the
referee's own `AGENTS.md` away from the thing under referee; Claude Code has none, and
`--bare`/`--safe-mode`/`--disable-slash-commands`, which would, all switch off skill discovery,
which is the whole of leg one (spec 013's T-2 trap). So the rule is kept by **where the host is
run**: `AgentHost.work_dir`, a fresh empty directory outside this repository, plus
`--setting-sources user` so the only settings that load are the fresh home's own -- which is where
`claude plugin install` writes the plugin's declaration (measured: `<CLAUDE_CONFIG_DIR>/settings.json`
gains `enabledPlugins: {"keel@keel": true}`).

**4. The runtime's Claude executor has no model knob.** `ClaudeCodeExecutor._build_argv` never
passes `--model`, and there is no `KEEL_CLAUDE_MODEL`. So a Claude journey's runtime model is
**recorded, not pinned** -- read back off the per-job envelopes the CLI itself writes. Copilot's
C-5 pin has no counterpart here and this module does not invent one; an unpinned subject that says
so is honest, and a pin this repository faked would be a fact about the referee.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from harness.agent_host import (MARKETPLACE_SOURCE, PLUGIN_NAME, PLUGIN_SPEC,  # noqa: F401
                                SKILL_NAME, AgentHost, HostRun, HostUnavailable, scrub_session)

#: The two grants leg one makes, and nothing else, in the one comma-separated argument
#: `--allowedTools` takes. `Skill` is the tool the CLI uses to open a discovered skill's body and
#: `Bash(python3:*)` is the one the skill needs (it runs `python3 <skill dir>/scripts/
#: keel_connect_check.py`) -- the same pair spec 013's containerised bed writes for this host, and
#: the same pair the Copilot half grants as `skill` and `shell(python3:*)`. Everything else stays
#: unapproved on purpose: a run that needed `Write` or `WebFetch` to say "keel connect" would be a
#: finding.
ALLOWED_TOOLS = "Skill,Bash(python3:*)"

#: `--permission-mode dontAsk`, not `--dangerously-skip-permissions`: spec 013's bed chose it
#: because the blanket flag is refused as root, and a referee that ran the founder's CLI in a mode
#: no founder is offered would be measuring a different program. With the two grants above
#: named, nothing the skill legitimately does has to ask.
PERMISSION_MODE = "dontAsk"

#: Only the fresh home's own settings. `claude plugin install` declares the plugin in
#: `<CLAUDE_CONFIG_DIR>/settings.json` (measured), which is the `user` source -- so `user` is
#: exactly enough to see the plugin and exactly little enough to keep this repository's own
#: project and local settings out of the host under referee.
SETTING_SOURCES = "user"

#: Every flag that would make the skill invisible or the script unrunnable, held as data so the
#: stackless tests can check an argv against them. `--bare` is spec 013's T-2 trap by name; the
#: other three reach the same end by another road (`--safe-mode` disables plugins and skills,
#: `--disable-slash-commands` disables skills outright, `--restricted` removes Bash).
FORBIDDEN_FLAGS = ("--bare", "--safe-mode", "--disable-slash-commands", "--restricted")

#: The inventory line `claude plugin details <plugin>` prints, and the only thing read out of it.
SKILLS_HEADING = "Skills"


def _auth_status(binary: str, config_dir: Path, base_env: dict[str, str] | None = None) -> dict:
    """`claude auth status` against one config dir, parsed. **Free, and it starts no session.**

    This is the Claude analogue of Copilot's impossible-`--model` probe -- a question the CLI
    answers out of its own state before any inference -- and it is a better one, because it names
    the credential rather than merely proving a catalogue could be reached.
    """
    env = scrub_session(dict(os.environ if base_env is None else base_env))
    env["CLAUDE_CONFIG_DIR"] = str(config_dir)
    try:
        done = subprocess.run([binary, "auth", "status"], capture_output=True, text=True,
                              timeout=60, env=env)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"error": f"`{binary} auth status` did not answer: {exc}"}
    text = (done.stdout or "").strip()
    try:
        body = json.loads(text)
    except json.JSONDecodeError:
        return {"error": f"`{binary} auth status` did not print JSON: {text[:200]!r}"}
    return body if isinstance(body, dict) else {"error": f"unexpected shape: {body!r}"}


def readiness(binary: str = "claude") -> dict[str, Any]:
    """Everything that can be known about this machine's Claude Code **without spending a cent**.

    Three questions, in the order that makes a skip legible: is the CLI there, what version, and
    **would a fresh config dir be able to authenticate at all**. The third is the one spec 016 did
    not have to ask, and it is asked in a throwaway empty directory rather than in the run's own
    home, because a run that discovers its home cannot log in has already created a run bundle
    nobody wanted.

    Returns `{ok, reason, version, auth, isolated_auth}`; `reason` is `None` when `ok`.
    """
    if shutil.which(binary) is None:
        return {"ok": False, "reason": f"no `{binary}` on PATH -- the Claude journey needs Claude "
                                        f"Code", "version": None, "auth": None,
                "isolated_auth": None}
    try:
        version = subprocess.run([binary, "--version"], capture_output=True, text=True,
                                 timeout=60).stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "reason": f"`{binary} --version` did not answer: {exc}",
                "version": None, "auth": None, "isolated_auth": None}

    probe_dir = Path(tempfile.mkdtemp(prefix="keel-journey-claude-auth-"))
    try:
        isolated = _auth_status(binary, probe_dir)
    finally:
        shutil.rmtree(probe_dir, ignore_errors=True)

    if isolated.get("error"):
        return {"ok": False, "reason": isolated["error"], "version": version,
                "auth": None, "isolated_auth": isolated}
    if not isolated.get("loggedIn"):
        return {
            "ok": False,
            "reason": (
                "a fresh CLAUDE_CONFIG_DIR cannot authenticate on this machine, so the journey "
                "would fail on its first word. Unlike COPILOT_HOME, an isolated Claude config dir "
                "does not keep the founder's stored login (measured: `claude auth status` there "
                "reads authMethod=none while ~/.claude reads claude.ai). Put a credential in this "
                "shell and run it again -- `export ANTHROPIC_API_KEY=...`, or "
                "`claude setup-token` and `export CLAUDE_CODE_OAUTH_TOKEN=...` for a "
                "subscription. Nothing here reads a secret from a file or a keychain (T-5)."),
            "version": version, "auth": None, "isolated_auth": isolated}
    return {"ok": True, "reason": None, "version": version,
            "auth": {k: isolated.get(k) for k in ("authMethod", "apiKeySource", "apiProvider",
                                                   "subscriptionType")},
            "isolated_auth": isolated}


def model_accepted(slug: str, binary: str = "claude") -> bool:  # noqa: ARG001
    """**Always true, and the docstring is the point.**

    Copilot's `--model` is checked against its own catalogue before any inference, so
    `copilot_host.model_accepted` can tell an impossible slug from a real one for nothing. Claude
    Code has no equivalent free probe -- every way of finding out starts a session and spends. So
    this host does not pretend to have measured a pin it has not: a slug that is wrong fails the
    run loudly on the first word, and the bundle records the model that actually answered, read
    off the CLI's own `result` event.
    """
    return True


# ---------------------------------------------------------------------- reading what Claude said

def skills_in_details(text: str) -> list[str]:
    """The skill names out of `claude plugin details <plugin>`'s component inventory.

    Read off the `Skills (n)` line, which is a *plugin's own* inventory -- so a name found here
    came from that plugin by construction and needs no second field to say so. Written to survive
    the count moving and the names wrapping onto the same line; a version that stops printing the
    line at all reads as "no skills", which is the honest answer for a reader that cannot see one.
    """
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith(SKILLS_HEADING):
            continue
        rest = stripped[len(SKILLS_HEADING):].lstrip()
        if rest.startswith("("):
            close = rest.find(")")
            if close == -1:
                continue
            rest = rest[close + 1:]
        return [name for name in rest.replace(",", " ").split() if name]
    return []


def installed_plugin_ids(listing: Any) -> list[str]:
    """Every `id` in `claude plugin list --json`, whatever depth the CLI nests them at.

    Structural on purpose, for the reason `copilot_host.find_skill` is: this repository does not
    own that JSON's schema, and a referee pinned to one shape would go red on a rename while the
    plugin was perfectly installed.
    """
    found: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            value = node.get("id") or node.get("pluginId") or node.get("name")
            if isinstance(value, str) and value and value not in found:
                found.append(value)
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(listing)
    return found


def _content_blocks(event: dict) -> list[dict]:
    message = event.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    return [block for block in (content or []) if isinstance(block, dict)]


def _result_event(events: list[dict]) -> dict | None:
    for event in reversed(events):
        if event.get("type") == "result":
            return event
    return None


def _final_answer(events: list[dict]) -> str:
    """The CLI's own `result` event carries the final text; an interrupted stream that never
    reached one falls back to the last assistant text block, so a partial transcript still shows a
    reader what was said."""
    result = _result_event(events)
    if result is not None:
        text = result.get("result")
        if isinstance(text, str) and text.strip():
            return text.strip()
    for event in reversed(events):
        if event.get("type") != "assistant":
            continue
        for block in reversed(_content_blocks(event)):
            if block.get("type") == "text" and str(block.get("text") or "").strip():
                return str(block["text"]).strip()
    return ""


@dataclass
class ClaudeRun(HostRun):
    """One `claude -p` invocation. **Dollars, never premium requests** -- the CLI's own unit, kept
    as the CLI reports it (the mirror of C-7's rule for the other host)."""

    @property
    def total_cost_usd(self) -> float | None:
        result = _result_event(self.events) or {}
        value = result.get("total_cost_usd")
        return value if isinstance(value, (int, float)) else None

    @property
    def num_turns(self) -> int | None:
        result = _result_event(self.events) or {}
        value = result.get("num_turns")
        return value if isinstance(value, int) else None

    @property
    def model(self) -> str | None:
        """Which model actually answered. `modelUsage` is keyed by model id and is the CLI's own
        record of what it billed, so it is read first; `model` beside it is the fallback."""
        result = _result_event(self.events) or {}
        usage = result.get("modelUsage")
        if isinstance(usage, dict) and usage:
            return sorted(usage)[0]
        for key in ("model", "modelId"):
            value = result.get(key)
            if isinstance(value, str) and value:
                return value
        for event in reversed(self.events):
            if event.get("type") != "assistant":
                continue
            message = event.get("message")
            if isinstance(message, dict) and isinstance(message.get("model"), str):
                return message["model"]
        return None

    @property
    def tools_used(self) -> list[str]:
        seen: list[str] = []
        for event in self.events:
            if event.get("type") != "assistant":
                continue
            for block in _content_blocks(event):
                if block.get("type") != "tool_use":
                    continue
                name = block.get("name")
                if isinstance(name, str) and name and name not in seen:
                    seen.append(name)
        return seen

    def spend(self) -> dict:
        return {"unit": "USD (the CLI's own total_cost_usd; never converted into anything else)",
                "total_cost_usd": self.total_cost_usd,
                "num_turns": self.num_turns}


# ---------------------------------------------------------------------------------- the host

class ClaudeHost(AgentHost):
    """The founder's own Claude Code, pointed at a `CLAUDE_CONFIG_DIR` this run owns."""

    name = "claude"
    binary = "claude"
    home_var = "CLAUDE_CONFIG_DIR"
    executor = "claude"
    #: keel-runtime's Claude envelope **is** the CLI's own `result` event, passed through
    #: unchanged (`ClaudeCodeExecutor.execute`: `self.last_envelope = result_event`), and that
    #: event names no executor. Copilot's is built by `CopilotExecutor._envelope`, which stamps
    #: one. So the per-job "which executor answered" cross-check exists on one side only, and this
    #: flag is how the scenario asserts it where it can be asserted and records the absence where
    #: it cannot, rather than quietly asserting less on both.
    envelope_names_its_executor = False
    forbidden_flags = FORBIDDEN_FLAGS

    readiness = staticmethod(readiness)
    model_accepted = staticmethod(model_accepted)

    def _runtime_model_env(self) -> dict[str, str]:
        """**Nothing.** `ClaudeCodeExecutor` takes no model: `_build_argv` never passes `--model`
        and keel-runtime has no `KEEL_CLAUDE_MODEL` to read. A run that set one would be naming a
        variable the runtime ignores and recording a pin that never happened."""
        return {}

    # ------------------------------------------------------------------- installing, and seeing it

    def skill_proof(self) -> dict:
        """`claude plugin details keel`, plus `claude plugin list --json` beside it.

        The inventory is the assertion: a `Skills (n)` line naming `keel-connect` inside **the
        plugin's own** details is proof both that the CLI can see the skill and that it came from
        the plugin, in one document. The JSON listing goes into the bundle beside it as the
        machine-readable record of what is installed at what version.
        """
        details = self._cli(["plugin", "details", PLUGIN_NAME])
        listing = self._cli(["plugin", "list", "--json"])
        raw = details.stdout.strip()
        parsed: Any = None
        try:
            parsed = json.loads(listing.stdout.strip()) if listing.stdout.strip() else None
        except json.JSONDecodeError:
            parsed = None
        skills = skills_in_details(raw)
        (self.artifacts / "claude-plugin-details.txt").write_text(raw + "\n" if raw else "")
        (self.artifacts / "claude-plugin-list.json").write_text(
            listing.stdout.strip() + "\n" if listing.stdout.strip() else "")
        return {
            "found": SKILL_NAME in skills,
            # By construction: the inventory read is one plugin's own.
            "from_plugin": SKILL_NAME in skills,
            "cmd": [self.binary, "plugin", "details", PLUGIN_NAME],
            "raw": raw,
            "detail": {"skills in the plugin's inventory": skills,
                       "installed plugins": installed_plugin_ids(parsed),
                       "details exit_code": details.returncode,
                       "list exit_code": listing.returncode,
                       "stderr": (details.stderr or "").strip()},
        }

    def credential_plan(self) -> dict:
        """**Measured, not guessed** -- `claude auth status` inside *this run's own config dir*.

        The Copilot half reasons about a documented precedence of three environment variables;
        this one asks the CLI, in the home the run will actually use, and records the answer it
        gives. That is possible here and was not there, and it is the better of the two: on the
        day the precedence changes, this says what happened rather than what was expected.
        """
        body = _auth_status(self.binary, self.home, base_env=self._base_env)
        if body.get("error"):
            return {"how": "unknown", "variable": "", "isolated_home": "yes -- and the CLI would "
                    "not say how it is authenticated", "probe": body["error"]}
        method = str(body.get("authMethod") or "none")
        variable = str(body.get("apiKeySource") or "")
        return {
            "how": {"api_key": "an API key from the caller's own shell",
                    "claude.ai": "the stored subscription login",
                    "none": "nothing -- this home cannot authenticate"}.get(method, method),
            "variable": variable,
            "isolated_home": ("yes -- and measured: an isolated CLAUDE_CONFIG_DIR does NOT keep "
                              "the founder's stored login, so a token in this shell is what "
                              "answers"),
            "authMethod": method,
            "loggedIn": bool(body.get("loggedIn")),
        }

    # --------------------------------------------------------------------------------- the run

    def _say_argv(self, prompt: str, *, usage_path: Path) -> list[str]:  # noqa: ARG002
        """`usage_path` is unused and stays in the signature on purpose: Copilot writes its usage
        to a file because a session that ends oddly still leaves one, and Claude reports the same
        facts inside the stream's own `result` event, so there is nothing to ask for."""
        argv = [self.binary, "-p", prompt,
                "--allowedTools", ALLOWED_TOOLS,
                "--permission-mode", PERMISSION_MODE,
                "--setting-sources", SETTING_SOURCES,
                # `stream-json` rather than `json`: the single result line carries the cost and
                # the model but not the tool calls, and *which tools the host called* is what leg
                # one shows about **how** the skill was run.
                "--output-format", "stream-json", "--verbose"]
        if self.model:
            argv += ["--model", self.model]
        return argv

    def _make_run(self, **kwargs) -> ClaudeRun:
        return ClaudeRun(reply_text=_final_answer(kwargs.get("events") or []), **kwargs)

    def envelope_facts(self, envelope: dict | None) -> dict:
        envelope = envelope or {}
        usage = envelope.get("modelUsage")
        return {
            "executor": None,
            "executor_named": False,
            "why": ("keel-runtime passes the `claude` CLI's own `result` event through as the "
                    "envelope, and that event names no executor; only the Copilot executor "
                    "stamps one"),
            "model": sorted(usage)[0] if isinstance(usage, dict) and usage else None,
            "total_cost_usd": envelope.get("total_cost_usd"),
            "num_turns": envelope.get("num_turns"),
            "is_error": envelope.get("is_error"),
        }
