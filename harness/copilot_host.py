"""GitHub Copilot CLI as a **host** (spec `016-copilot-e2e`, generalised by spec
`019-journey-through-a-host`; keel-cloud `canon/designs/keel-skill-design.md` §5/§5.5 part 2).

Everything else in this repository that has ever touched Copilot touched it as a *thinker*:
`instructions/` (spec 014) constructs keel-runtime's own `CopilotExecutor` and shells `copilot -p`
with a rendered prompt, and no skill, no plugin and no `SKILL.md` is anywhere near it. This module
is the other half -- the CLI a founder actually types into, with the keel-connect plugin installed
into it from the real marketplace, being asked *"keel connect"* in English.

**What spec 019 moved, and what it deliberately did not.** The three rules below, the readers for
the runtime's own artefacts, the marketplace constants and the environment discipline are now
`harness/agent_host.py`'s, because they were never Copilot's -- they are the journey's, and the
journey has two hosts. What stayed here is everything this CLI alone knows: its free model probe,
its usage file, its `skill list --json`, its three-way credential precedence, and the argv that
was measured green on 2026-09-10. **Not one flag of that argv moved**, which is the point: the
Copilot instance of the journey must still be the run that produced
`runs/20260910T211318Z-s012-copilot-host-and-thinker-live`.

**Three rules, and each is why a line here looks the way it does.**

1. **This module never starts the runtime.** `harness/connect.py`'s opening rule is that the
   harness never shells `python3 -m keel_runtime`, because keel-connect-skill is one of the four
   applications under referee; the journey goes one further and never shells the *skill's script*
   either. The only thing that may run `keel_connect_check.py` in leg one is the host, having read
   `SKILL.md` and decided to. A helper here that "just ran the script to make sure" would delete
   the measurement.

2. **Nothing here reads Copilot's prose for evidence.** `reply_text` is returned so a scenario can
   make one loose *"it said connected"* check and so the whole transcript lands in the bundle, and
   that is the entire contract. What proves the skill ran is `read_heartbeat` and
   `read_launch_log` -- artefacts of the *runtime*, which no amount of confident wording produces.
   Spec 013's acceptance bed greps the reply for a `XXXX-XXXX` shape and the word `device` and
   says so in its own comment; that bed has also never run.

3. **The credential is never copied.** `COPILOT_HOME` moves "the directory where configuration and
   state files are stored" (`copilot help environment`), and `credential_plan` states in one place
   which of the three legitimate ways a run is authenticated -- so a bundle can never leave a
   reader guessing whether an isolated home was still the founder's login. (The Claude half of the
   pair answers that question the other way, and `harness/claude_host.py` says so at the top.)
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from harness.agent_host import (  # noqa: F401 -- re-exported: one vocabulary, two hosts
    EXECUTOR_PREFIX, HEARTBEAT_FILENAME, LAUNCH_LOG_FILENAME, MARKETPLACE_SOURCE, PLUGIN_NAME,
    PLUGIN_SPEC, SKILL_NAME, STATE_AWAITING_APPROVAL, USER_CODE_PREFIX, VERIFICATION_URI_PREFIX,
    AgentHost, HostRun, HostUnavailable, launch_executor_in, looks_like_a_user_code,
    mentions_connected, read_heartbeat, read_launch_log, user_code_in, verification_uri_in)

#: The two grants leg one makes, and nothing else. `shell(python3:*)` is the one the skill needs
#: (it runs `python3 <skill dir>/scripts/keel_connect_check.py`); `skill` is the tool the CLI uses
#: to open a discovered skill's body, and is the same grant spec 013's `claude` half makes with
#: `--allowedTools "Skill,Bash(python3:*)"`. Everything else stays unapproved on purpose: a run
#: that needed `write` or `web_fetch` to say "keel connect" would be a finding.
ALLOWED_TOOLS = ("shell(python3:*)", "skill")

#: `--bare` is a *Claude Code* flag and skips skill auto-discovery (spec 013 T-2). It does not
#: exist on this CLI at all, and this constant exists so `tests/test_s012_copilot_host.py` can
#: hold the argv against it rather than trusting that nobody ever pastes one in.
FORBIDDEN_FLAGS = ("--bare",)


class CopilotUnavailable(HostUnavailable):
    """`copilot` is not on PATH, or would not run at all. A reason to skip the journey by name
    (C-11), never to pass it quietly."""


# ------------------------------------------------------------------------------------ readiness

def readiness(binary: str = "copilot") -> dict[str, Any]:
    """Everything that can be known about this machine's Copilot **without spending a request**.

    `--model <a slug that cannot exist>` is refused by the CLI *before* any inference, against its
    own model catalogue, so it is a free probe that the binary runs, parses flags and can resolve
    a catalogue. It is deliberately not called "authenticated": the CLI may answer this from a
    cache, and a referee that inferred a login from it would be inferring. What the journey
    actually relies on is the run itself, which fails loudly with keel-runtime's own auth markers
    if the login is not there.

    Returns `{ok, reason, version, catalogue_probe}`; `reason` is `None` when `ok`.
    """
    # The resolved path, never the bare name: on Windows the CLI is `copilot.cmd`, which a bare
    # name cannot launch without a shell (the runtime met the same wall, keel-runtime PR #1;
    # the first cloud run skipped every Windows cell on it).
    binary = shutil.which(binary) or binary
    if shutil.which(binary) is None:
        return {"ok": False, "reason": f"no `{binary}` on PATH -- the Copilot journey needs "
                                        f"GitHub Copilot CLI",
                "version": None, "catalogue_probe": None}
    try:
        version = subprocess.run([binary, "--version"], capture_output=True, text=True,
                                 timeout=30).stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "reason": f"`{binary} --version` did not answer: {exc}",
                "version": None, "catalogue_probe": None}
    try:
        probe = subprocess.run(
            [binary, "-p", "say ok", "--model", "keel-e2e-eval-no-such-model",
             "--no-ask-user", "--no-auto-update", "--log-level", "none"],
            capture_output=True, text=True, timeout=120)
        text = (probe.stdout + probe.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "reason": f"`{binary} -p` did not answer: {exc}",
                "version": version, "catalogue_probe": None}
    if "is not available" not in text:
        return {"ok": False,
                "reason": f"`{binary}` did not refuse an impossible --model slug, so its model "
                          f"catalogue could not be reached: {text[:200]!r}",
                "version": version, "catalogue_probe": text[:400]}
    return {"ok": True, "reason": None, "version": version, "catalogue_probe": text[:400]}


def model_accepted(slug: str, binary: str = "copilot") -> bool:
    """Whether `--model <slug>` survives the CLI's own catalogue check, **without inference**.

    keel-runtime spec 005's C-5 wants the Copilot path pinned, and could not exercise it: on
    2026-09-09 this machine's CLI 1.0.83 refused every slug it was offered. `KEEL_COPILOT_MODEL`
    exists for the day that changes, and this is how a run finds out that it has -- an impossible
    slug and a real one are told apart by the same one sentence the CLI prints, before a single
    premium request is spent. **`-p ""` is the reason it is free**: an accepted slug reaches the
    empty-prompt check and is refused there with *"No prompt provided"* and a usage file reading
    `totalPremiumRequestCost: 0` (measured, CLI 1.0.83), so the probe can never buy inference by
    accident on the day a slug starts working.
    """
    # The resolved path, never the bare name: on Windows the CLI is `copilot.cmd`, which a bare
    # name cannot launch without a shell (the runtime met the same wall, keel-runtime PR #1;
    # the first cloud run skipped every Windows cell on it).
    binary = shutil.which(binary) or binary
    try:
        probe = subprocess.run(
            [binary, "-p", "", "--model", slug, "--no-ask-user", "--no-auto-update",
             "--log-level", "none"],
            capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return f'Model "{slug}" from --model flag is not available.' not in (probe.stdout + probe.stderr)


def credential_plan(env: dict[str, str] | None = None) -> dict[str, str]:
    """Which of the three legitimate ways this run is authenticated, decided once and recorded.

    In the CLI's own precedence (`copilot help environment`): `COPILOT_GITHUB_TOKEN` >
    `GH_TOKEN` > `GITHUB_TOKEN` > the stored OAuth credential. The stored credential does not live
    under `COPILOT_HOME` on macOS, so an isolated home keeps the founder's login -- which is what
    makes leg one's isolation free. The third case is here because a machine where that is untrue
    must **say so in the bundle** rather than quietly run against the founder's real home as if
    nothing had changed.
    """
    import os  # noqa: PLC0415 -- the default is the live environment, read at call time

    env = os.environ if env is None else env
    for name in ("COPILOT_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        if env.get(name):
            return {"how": "env token", "variable": name,
                    "isolated_home": "yes -- the token travels, the home does not"}
    return {"how": "stored OAuth, outside COPILOT_HOME", "variable": "",
            "isolated_home": "yes -- measured: an isolated home still resolves the model catalogue"}


# --------------------------------------------------------------------------------- the host run

@dataclass
class CopilotRun(HostRun):
    """One `copilot -p` invocation: what it was asked, what it said, what it cost."""

    @property
    def premium_requests(self) -> float | None:
        """Copilot's own number, never a dollar figure (keel-runtime spec 005 C-7). The
        `--usage-output-file` JSON is preferred because it is written even when a session ends
        oddly; the final `result` event is the fallback."""
        for key in ("totalPremiumRequestCost", "totalPremiumRequests"):
            value = self.usage.get(key)
            if isinstance(value, (int, float)):
                return value
        for event in reversed(self.events):
            if event.get("type") == "result":
                value = (event.get("usage") or {}).get("premiumRequests")
                if isinstance(value, (int, float)):
                    return value
        return None

    @property
    def model(self) -> str | None:
        """Which model actually answered -- `runs/DRIFT.md` #53's question, asked of the host
        rather than of a job envelope."""
        current = self.usage.get("currentModel")
        if isinstance(current, str) and current:
            return current
        for event in reversed(self.events):
            if event.get("type") == "assistant.message":
                model = (event.get("data") or {}).get("model")
                if isinstance(model, str) and model:
                    return model
        return None

    @property
    def tools_used(self) -> list[str]:
        """Every tool the host called, in order of first use -- what leg one shows about *how*
        the skill was run, and the reason `--allow-tool` is two names and not `--allow-all-tools`.
        """
        seen: list[str] = []
        for event in self.events:
            if event.get("type") not in ("tool.call_start", "assistant.tool_call",
                                          "tool.execution_start"):
                continue
            name = (event.get("data") or {}).get("name") or (event.get("data") or {}).get("tool")
            if isinstance(name, str) and name and name not in seen:
                seen.append(name)
        return seen

    def spend(self) -> dict:
        return {"unit": "premium requests (C-7: never converted into a dollar figure)",
                "premium_requests": self.premium_requests}


class CopilotHost(AgentHost):
    """The founder's own Copilot, pointed at a home this run owns."""

    name = "copilot"
    binary = "copilot"
    home_var = "COPILOT_HOME"
    executor = "copilot"
    #: `CopilotExecutor._envelope` stamps `"executor": "copilot"` on every per-job envelope, which
    #: is the second, independent proof that Copilot did the thinking -- written per job by the
    #: process that ran it. The Claude executor's envelope is the CLI's own `result` event and
    #: names none, so this is `True` on one side of the pair only.
    envelope_names_its_executor = True
    forbidden_flags = FORBIDDEN_FLAGS

    readiness = staticmethod(readiness)
    model_accepted = staticmethod(model_accepted)

    def _runtime_model_env(self) -> dict[str, str]:
        """keel-runtime's own resolution order (`config.resolve_copilot_model`): `--copilot-model`
        > `KEEL_COPILOT_MODEL` > `config.json` > unpinned. The skill passes no `--copilot-model`,
        so this is how C-5's pin reaches the executor the runtime builds.

        **Deliberately not `self.model`.** The host's model and the runtime's are two different
        measurements: leg one asks what a founder's own Copilot does with the skill, and leg two
        asks what keel-runtime's executor does with a job. Tying them together would mean choosing
        one subject's model to suit the other's.
        """
        return {"KEEL_COPILOT_MODEL": self.runtime_model} if self.runtime_model else {}

    def credential_plan(self) -> dict:
        return credential_plan(self._base_env)

    def skill_list(self) -> dict:
        """`copilot skill list --json`, parsed. Returns `{exit_code, skills, raw}` -- `skills` is
        whatever list the CLI hands back, untouched, so `find_skill` can read it however this
        version of the CLI shapes it."""
        done = self._cli(["skill", "list", "--json"])
        raw = done.stdout.strip()
        skills: Any = None
        try:
            skills = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            skills = None
        (self.artifacts / "copilot-skill-list.json").write_text(raw + "\n" if raw else "")
        return {"exit_code": done.returncode, "skills": skills, "raw": raw,
                "stderr": done.stderr.strip()}

    def skill_proof(self) -> dict:
        """`copilot skill list --json`, read for the one skill this journey is about and for
        whether the listing says it came from a **plugin**."""
        listing = self.skill_list()
        hit = find_skill(listing["skills"])
        return {"found": hit is not None,
                "from_plugin": describes_a_plugin(hit),
                "cmd": [self.binary, "skill", "list", "--json"],
                "raw": listing["raw"],
                "detail": {"found": hit, "exit_code": listing["exit_code"],
                           "stderr": listing["stderr"]}}

    def _say_argv(self, prompt: str, *, usage_path: Path) -> list[str]:
        argv = [self.binary, "-p", prompt]
        for tool in ALLOWED_TOOLS:
            argv += ["--allow-tool", tool]
        argv += ["--no-auto-update", "--no-ask-user", "--no-remote", "--no-remote-export",
                 # **The referee's own AGENTS.md must never reach the thing under referee.**
                 # Copilot loads custom instructions from the git root and the working directory.
                 # `AgentHost.work_dir` puts the working directory outside this repository, which
                 # is the rule both hosts keep; this flag is the belt beside those braces, and
                 # keel-runtime's own executor passes it for the same reason (spec 005).
                 "--no-custom-instructions",
                 "--no-color", "--output-format", "json",
                 "--usage-output-file", str(usage_path)]
        if self.model:
            argv += ["--model", self.model]
        return argv

    def _make_run(self, **kwargs) -> CopilotRun:
        return CopilotRun(reply_text=_final_answer(kwargs.get("events") or []), **kwargs)

    def envelope_facts(self, envelope: dict | None) -> dict:
        envelope = envelope or {}
        return {"executor": envelope.get("executor"),
                "executor_named": True,
                "model": envelope.get("model"),
                "premium_requests": envelope.get("premium_requests"),
                "num_turns": envelope.get("num_turns"),
                "is_error": envelope.get("is_error")}


def find_skill(listing: Any, name: str = SKILL_NAME) -> dict | None:
    """The one skill this scenario is about, found in whatever shape `copilot skill list --json`
    hands back on this CLI version.

    Written to walk the JSON structurally rather than to know its schema: the listing is grouped by
    source in the CLI's *text* output ("Project / Personal / Plugin / Custom"), and a referee that
    pinned one JSON shape would go red on a CLI upgrade that renamed a key while the skill was
    perfectly visible. Returns the object carrying the name, plus every string value beside it, so
    a caller can ask whether the word `plugin` is among them.
    """
    found: list[dict] = []

    def walk(node: Any, trail: tuple[str, ...]) -> None:
        if isinstance(node, dict):
            values = {k: v for k, v in node.items() if isinstance(v, (str, int, float, bool))}
            if any(isinstance(v, str) and v == name for v in values.values()):
                found.append({"entry": values, "trail": list(trail)})
            for key, value in node.items():
                walk(value, trail + (str(key),))
        elif isinstance(node, list):
            for item in node:
                walk(item, trail)

    walk(listing, ())
    return found[0] if found else None


#: The field names a CLI version might use to say where a skill came from. CLI 1.0.83 uses
#: `source`, with the value `"plugin"` (measured); the others are here so a rename is a still-green
#: run rather than a red one, and the *fallback* below covers a version that names none of them.
SOURCE_FIELDS = ("source", "kind", "type", "origin", "from")


def describes_a_plugin(hit: dict | None) -> bool:
    """Whether the listing says this skill came from a **plugin**.

    An explicit source field wins outright when the listing has one, because it is the only field
    that *means* it: 1.0.83 also prints a `path`, and an installed plugin's path contains the word
    `installed-plugins`, so a search over every value would call a skill a plugin skill for living
    in a directory rather than for being installed as one. With no such field the path through the
    document and the values beside the name are the fallback -- this repository does not own that
    JSON's shape, and a referee that pinned one would go red on a rename while the skill was
    perfectly visible.
    """
    if not hit:
        return False
    for field_name in SOURCE_FIELDS:
        value = hit["entry"].get(field_name)
        if isinstance(value, str) and value.strip():
            return "plugin" in value.lower()
    words = [str(v).lower() for v in hit["entry"].values()] + [t.lower() for t in hit["trail"]]
    return any("plugin" in word for word in words)


def _final_answer(events: list[dict]) -> str:
    """The last `assistant.message` carrying content -- keel-runtime's own rule
    (`executor._copilot_final_answer`), because a tool-calling turn emits an `assistant.message`
    with empty content and "the last assistant message" would find that one."""
    for event in reversed(events):
        if event.get("type") != "assistant.message":
            continue
        content = (event.get("data") or {}).get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
    return ""


def _run_copilot(host: CopilotHost, prompt: str, *, timeout: float, slug: str) -> CopilotRun:
    """Kept as a module function because `tests/test_s012_copilot_host.py` holds the argv against
    it by name -- the argv this CLI is run with is a property worth naming in one place."""
    return host._run(prompt, timeout=timeout, slug=slug)


def say(host: CopilotHost, prompt: str, *, slug: str, timeout: float = 420) -> CopilotRun:
    """Say something to Copilot, once. There is no retry here on purpose (spec 016 FR-009): a live
    run that quietly said it twice would be reporting a number nobody spent."""
    return host.say(prompt, slug=slug, timeout=timeout)
