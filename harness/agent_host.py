"""One journey, two hosts (spec `019-journey-through-a-host`; keel-cloud
`canon/designs/e2e-matrix-design.md` §5.1, §5.3 and decision 5).

S-012 was written as a Copilot scenario. The matrix design needs it to be **the** scenario -- *"the
S-012 shape (plugin from the marketplace into a fresh host home, three words to the host, device
approval in the browser, the runtime on that host's executor, every job answered by that host's
model), parameterised by host rather than a Copilot-only scenario"* -- because eighteen cells
differ by an OS, a Python and a **host**, and a cell whose scenario only exists for one host can
only ever fill a third of the grid.

This module is where the two hosts are told apart, and it is deliberately the **only** place. What
a founder does is the same on both: add the public marketplace, install the plugin, check the CLI
can see the skill, say *"keel connect"*, approve the device, and let the runtime the skill started
answer the journey. What differs is three flags, one environment variable and the way each CLI
prints what it knows -- so the scenario asks this interface the questions and never asks a CLI.

**Three rules carried forward from `harness/copilot_host.py`, and they now bind both hosts.**

1. **No implementation here ever starts the runtime.** The only thing that may run
   `keel_connect_check.py` is the host, having read `SKILL.md` and decided to. A helper that "just
   ran the script to make sure" would delete the measurement.

2. **Nothing here reads the host's prose for evidence.** `reply_text` exists so a scenario can
   make one loose *"it said connected"* check and so the transcript lands in the bundle. What
   proves the skill ran is `read_heartbeat` and `read_launch_log` -- artefacts of the *runtime*,
   which no amount of confident wording produces.

3. **The credential is never copied.** Each host says, in `credential_plan`, which of its own
   legitimate ways this run is authenticated -- so a bundle can never leave a reader guessing
   whether an isolated home was still the founder's login. The two hosts answer that question
   **differently**, which is the single most important thing this module measures: an isolated
   `COPILOT_HOME` keeps the founder's GitHub login (the stored credential is not in it), and an
   isolated `CLAUDE_CONFIG_DIR` does **not** keep the founder's Anthropic login -- `claude auth
   status` in a fresh config dir reads `{"loggedIn": false, "authMethod": "none"}`, measured on
   this Mac on 2026-09-10 with CLI 2.1.268. A Claude cell therefore needs a token in the caller's
   own shell, and `readiness` says so by name rather than letting a run find out by spending.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# --------------------------------------------------------------------------------- which host

#: The two hosts the plugin ships for, co-equal (keel-cloud `canon/designs/keel-skill-design.md`
#: §5). Ordered as the design's matrix axis orders them, which is also alphabetical.
HOSTS = ("claude", "copilot")

#: **Copilot, so today's command keeps working.** `make eval-live K=s012` with no `HOST=` is the
#: command that produced `runs/20260910T211318Z-s012-copilot-host-and-thinker-live`, and a default
#: that silently moved it to the other host would make every earlier run record ambiguous.
DEFAULT_HOST = "copilot"

#: The one environment variable the scenario reads, set by `make eval-live HOST=`.
HOST_ENV = "KEEL_JOURNEY_HOST"


class UnknownHost(ValueError):
    """`KEEL_JOURNEY_HOST` named something that is not a host.

    Deliberately an error and never a fallback to the default: a typo that quietly ran the *other*
    host would spend the founder's money on a measurement nobody asked for and file it under a
    name nobody chose.
    """


def journey_host(environ: dict[str, str] | None = None) -> str:
    """Which host this run is the journey through -- `KEEL_JOURNEY_HOST`, or `copilot`.

    Whitespace and case are forgiven (`HOST=Claude` off a Makefile is a founder's typing, not a
    different intention); anything else is refused by name.
    """
    env = os.environ if environ is None else environ
    raw = (env.get(HOST_ENV) or "").strip().lower()
    if not raw:
        return DEFAULT_HOST
    if raw not in HOSTS:
        raise UnknownHost(
            f"{HOST_ENV}={raw!r} is not a host this journey knows. It is one of {list(HOSTS)} -- "
            f"`make eval-live K=s012 HOST=claude` or `HOST=copilot`.")
    return raw


def bundle_slug(host: str | None = None) -> str:
    """The run bundle's own name: `s012-journey-<host>`.

    The host is *in the directory name* because the matrix uploads one bundle per cell and a
    reader looking at eighteen of them has only the name to go on until they open one. It is also
    why this is a function rather than a constant: the name is a fact about the run, resolved
    once, at import, from the same place the scenario resolves everything else about the host.
    """
    return f"s012-journey-{journey_host() if host is None else host}"


#: Which executor name each host's runtime must end up on. It is the *canonical* name -- the skill
#: sends `claude-code` for Claude (a permanent accepted alias, keel-connect-skill's invariant
#: C-12) and keel-runtime's `canonical_executor_name` resolves it before it prints the startup
#: line, so this is what a log actually says.
EXECUTOR_FOR_HOST = {"claude": "claude", "copilot": "copilot"}


# ------------------------------------------------------------------- the plugin, and what it leaves

#: The public marketplace and the plugin in it, exactly as keel-connect-skill's own README and
#: `keeldiscovery/keel-marketplace`'s README tell a founder to type them -- **one repository serves
#: both hosts** (`.claude-plugin/marketplace.json`, which Copilot's CLI reads too), so these two
#: strings are shared rather than per-host, and a run that had to pass a different source for a
#: different host would be evidence that the design's "one marketplace" claim had broken.
MARKETPLACE_SOURCE = "keeldiscovery/keel-marketplace"
PLUGIN_SPEC = "keel@keel"

#: The plugin's own name, which is how each CLI refers to it after the install.
PLUGIN_NAME = "keel"

#: The skill's own frontmatter `name`, which is what both CLIs print.
SKILL_NAME = "keel-connect"

#: keel-runtime's `heartbeat.HEARTBEAT_FILENAME` and keel-connect-skill's
#: `keel_connect_check.LAUNCH_LOG_FILENAME`. Named here because leg one asserts them by name
#: against a home no other module in this repository owns.
HEARTBEAT_FILENAME = "runtime.heartbeat.json"
LAUNCH_LOG_FILENAME = "keel-connect-check.launch.log"
STATE_AWAITING_APPROVAL = "awaiting_approval"

USER_CODE_PREFIX = "KEEL_USER_CODE="
VERIFICATION_URI_PREFIX = "KEEL_VERIFICATION_URI="

#: The runtime's own startup line, written by the process that is running -- `cli.py`'s
#: `KEEL_EXECUTOR=<name> source=<how> binary=<path> version=<...> model=<slug or auto>`.
EXECUTOR_PREFIX = "KEEL_EXECUTOR="


def read_heartbeat(keel_home: Path) -> dict | None:
    """`<home>/runtime.heartbeat.json`, or `None`.

    This is leg one's first assertion and it is deliberately the *first*: a runtime that has a pid
    and a home writes it the moment `connect` starts, in `state="awaiting_approval"` and with no
    `agent_session_id` yet (keel-runtime `bfc0ad6`, which closed `runs/DRIFT.md` #51). So its
    presence, in that state, is the narrowest available proof that something really launched a
    runtime -- earlier than a code, earlier than a reply, and impossible to write by talking.
    """
    path = Path(keel_home) / HEARTBEAT_FILENAME
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def read_launch_log(keel_home: Path) -> str:
    path = Path(keel_home) / LAUNCH_LOG_FILENAME
    return path.read_text() if path.is_file() else ""


def _prefixed(text: str, prefix: str) -> str | None:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith(prefix):
            value = line[len(prefix):].strip()
            if value:
                return value
    return None


def launch_executor_in(log_text: str) -> dict[str, str] | None:
    """**Which executor the runtime that is running actually chose**, read off its own startup
    line, plus how it chose it and which model it pinned.

    This exists because `keel status` cannot answer that question, and is not claiming to:
    keel-cloud's own contract says `executor` is *"which executor this home **would** run a job
    with ... resolved the same way `connect` resolves it"* -- a statement about the caller's
    environment, not about the live process (`runs/DRIFT.md` #58).

    The startup line has no such ambiguity: `connect` prints it once, from inside the process, out
    of the resolution that process actually made.

    Returns `{"executor", "source", "model", ...}` or `None`.
    """
    line = _prefixed(log_text, EXECUTOR_PREFIX)
    if line is None:
        return None
    # `KEEL_EXECUTOR=copilot source=flag binary=/opt/homebrew/bin/copilot version=GitHub Copilot
    # CLI 1.0.83. model=claude-sonnet-5` -- `version=` carries spaces, so this splits on the keys
    # it knows rather than on whitespace.
    out: dict[str, str] = {"executor": line.split(" ", 1)[0].strip()}
    for key in ("source", "binary", "version", "model"):
        match = re.search(rf"\b{key}=(.*?)(?=\s+\w+=|$)", line)
        if match:
            out[key] = match.group(1).strip()
    return out


def user_code_in(log_text: str) -> str | None:
    """The `KEEL_USER_CODE=` line keel-runtime's own `connect` prints and the skill's script reads
    (`keel_connect_check.USER_CODE_PREFIX`)."""
    return _prefixed(log_text, USER_CODE_PREFIX)


def verification_uri_in(log_text: str) -> str | None:
    return _prefixed(log_text, VERIFICATION_URI_PREFIX)


_CODE_SHAPE = re.compile(r"^[A-Z0-9]{4}-[A-Z0-9]{4}$")


def looks_like_a_user_code(code: str | None) -> bool:
    return bool(code) and bool(_CODE_SHAPE.match(code or ""))


def mentions_connected(reply: str) -> bool:
    """The one loose check leg one makes of the host's own words, and never the only evidence of
    anything (FR-003). Deliberately generous: what is being measured is that the host relayed the
    skill's `already_connected` in *some* English, not which English."""
    lowered = (reply or "").lower()
    return any(word in lowered for word in ("already connected", "is connected", "connected"))


# ------------------------------------------------------------------------- one run of one host

@dataclass
class HostRun:
    """One `<host> -p "keel connect"` invocation: what it was asked, what it said, what it cost.

    The subclasses differ in exactly two places -- `spend()`, because the two CLIs report in two
    different units and **neither is ever converted into the other** (keel-runtime spec 005 C-7),
    and `model`, because each reads it out of its own event stream.
    """

    argv: list[str]
    exit_code: int
    reply_text: str
    events: list[dict] = field(default_factory=list)
    usage: dict = field(default_factory=dict)
    stderr: str = ""
    transcript_path: Path | None = None
    usage_path: Path | None = None

    @property
    def model(self) -> str | None:
        """Which model actually answered -- `runs/DRIFT.md` #53's question, asked of the host
        rather than of a job envelope."""
        raise NotImplementedError

    @property
    def tools_used(self) -> list[str]:
        """Every tool the host called, in order of first use -- what leg one shows about *how* the
        skill was run, and the reason each host's grant is two names and not a blanket one."""
        raise NotImplementedError

    def spend(self) -> dict:
        """What this run cost, in **the host's own unit and no other**. Copilot reports premium
        requests against a plan; Claude reports dollars against an account. A referee that turned
        one into the other would be inventing an exchange rate nobody published."""
        raise NotImplementedError


# ---------------------------------------------------------------------------------- the host

#: Every environment name that says *this process is already inside an agent host's session*.
#: They are scrubbed from the environment every host is launched with, for one reason: **the
#: subject is a founder's own CLI, and a founder's CLI is not running inside another one.**
#:
#: It is not hygiene. keel-connect-skill's `detect_host` reads exactly these names, and *"two
#: different answers means no answer"* -- so an inherited `COPILOT_AGENT_SESSION_ID` (which leaks
#: arbitrarily deep down a process tree, as that function's own comment says) sitting beside the
#: `CLAUDECODE=1` this harness runs under would make the skill decline to name a host at all, and
#: the runtime would fall through to `source=ambiguous-path`. The assertion that the skill's own
#: line put the runtime on the right executor would then be measuring this repository's shell.
HOST_SESSION_VARS_EXACT = (
    "CLAUDECODE", "CLAUDE_PID", "CLAUDE_EFFORT", "AI_AGENT",
    "COPILOT_CLI", "COPILOT_AGENT_SESSION_ID",
    # Both home variables go too, and each host puts its own back in `env()`: an inherited one is
    # the founder's real home, which is the one thing an isolated run must not reach.
    "CLAUDE_CONFIG_DIR", "COPILOT_HOME",
)

#: `CLAUDE_CODE_*` is swept by prefix rather than by name, because it is a growing family of
#: per-session handles (a messaging socket, a bridge session id, an entrypoint) and a new one
#: would otherwise reach the child on the day it is added.
HOST_SESSION_VARS_PREFIX = ("CLAUDE_CODE_",)

#: ...with one exception, and it is a credential rather than a handle: `claude setup-token` mints
#: `CLAUDE_CODE_OAUTH_TOKEN` for exactly the case a Claude cell is in -- a fresh config dir with no
#: stored login. Scrubbing it would break the only subscription-shaped way to authenticate a cell.
HOST_SESSION_VARS_KEEP = ("CLAUDE_CODE_OAUTH_TOKEN",)


def scrub_session(env: dict[str, str]) -> dict[str, str]:
    """`env` without the markers of the agent session this harness itself is running in."""
    out = {}
    for key, value in env.items():
        if key in HOST_SESSION_VARS_KEEP:
            out[key] = value
            continue
        if key in HOST_SESSION_VARS_EXACT:
            continue
        if any(key.startswith(prefix) for prefix in HOST_SESSION_VARS_PREFIX):
            continue
        out[key] = value
    return out


class HostUnavailable(RuntimeError):
    """The host's CLI is not on PATH, would not run, or could not authenticate the fresh home this
    run gives it. A reason to skip the journey **by name** (C-11), never to pass it quietly."""


class AgentHost:
    """The founder's own agent CLI, pointed at a home this run owns.

    `home` is the fresh host home (`CLAUDE_CONFIG_DIR` / `COPILOT_HOME`); `keel_home` and
    `base_url` are what the *skill* will need when the host decides to run it, and they are named
    on the environment rather than on the command line because a founder names them nowhere --
    `SKILL.md` says in as many words *"Do not pass a base URL, an executor or a credential
    backend"*.

    Subclasses supply five things and nothing else: `name`, `binary`, `home_var`, the argv builders
    (`_install_argv`, `_say_argv`), and the two readers their CLI's own output needs
    (`skill_proof`, `credential_plan`).
    """

    #: `"claude"` / `"copilot"` -- the host axis's own value, and what the bundle is named for.
    name: str = ""
    #: The CLI on PATH.
    binary: str = ""
    #: The environment variable that moves this CLI's configuration and state to a fresh directory.
    home_var: str = ""
    #: What the runtime's `KEEL_EXECUTOR=` line must read when the skill ran under this host.
    executor: str = ""
    #: Whether this host's per-job envelopes name the executor that wrote them. Copilot's do
    #: (`executor.py`'s `_envelope`); Claude's are the CLI's own `result` event, which names no
    #: executor at all -- so the scenario asserts it only where it can be asserted, and records
    #: the absence rather than papering over it.
    envelope_names_its_executor: bool = False
    #: The flags that must never appear in a `-p` argv, per host. Held as data so
    #: `tests/test_journey_through_a_host.py` can check an argv against them rather than trusting
    #: that nobody ever pastes one in.
    forbidden_flags: tuple[str, ...] = ()

    def __init__(self, *, home: Path, keel_home: Path, base_url: str, artifacts: Path,
                 binary: str | None = None, model: str | None = None,
                 runtime_model: str | None = None,
                 base_env: dict[str, str] | None = None,
                 work_dir: Path | None = None):
        self.home = Path(home)
        self.keel_home = Path(keel_home)
        self.base_url = base_url
        self.artifacts = Path(artifacts)
        if binary:
            # Resolved through PATH: on Windows the CLI is a `.cmd` shim, which Popen cannot launch
            # by its bare name (keel-runtime PR #1 found the same; the first cloud run re-found it).
            self.binary = shutil.which(binary) or binary
        #: `--model` for the **host** CLI: what the founder's own agent answers with when they type
        #: "keel connect". Leg one's subject is the founder's real CLI, so this is each host's own
        #: default rather than a slug chosen to suit the runtime.
        self.model = model
        #: What the *runtime* pins when it answers a job. A different subject and therefore a
        #: different choice; how it is passed is the host's business (`_runtime_model_env`).
        self.runtime_model = runtime_model
        self._base_env = dict(os.environ if base_env is None else base_env)
        self.home.mkdir(parents=True, exist_ok=True)
        self.keel_home.mkdir(parents=True, exist_ok=True)
        self.artifacts.mkdir(parents=True, exist_ok=True)
        #: **The directory the host is run from, and it is outside this repository on purpose.**
        #: Both CLIs discover instructions from the working directory and its git root, and a run
        #: bundle lives inside keel-e2e-eval, whose `AGENTS.md` describes this harness, its
        #: scenarios and what they assert. A host briefed on the measurement is not the host a
        #: founder has. Copilot has `--no-custom-instructions` and still passes it; Claude has no
        #: such flag, so for that host this is the whole of the rule -- and holding both hosts to
        #: one rule means the rule survives a flag being renamed.
        self.work_dir = Path(work_dir) if work_dir is not None else Path(
            tempfile.mkdtemp(prefix=f"keel-journey-{self.name}-"))
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self._runs = 0

    # ------------------------------------------------------------------------------ environment

    def _runtime_model_env(self) -> dict[str, str]:
        """How this host's runtime pin reaches keel-runtime's executor, if it has one at all."""
        return {}

    def env(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        """The environment the host -- and therefore the skill's script, and therefore the runtime
        -- is launched with.

        `KEEL_RUNTIME_PATH` is **removed** (spec 012 FR-004, invariant T-1). This repository is
        worked on from shells that export it (keel-connect-playground's own settings do), and an
        inherited one would put the *checkout* back in place of the runtime that travelled inside
        the plugin -- a green leg one that never touched the thing it claims to referee.
        `KEEL_HOME` and `KEEL_BASE_URL` are set rather than scrubbed, because unlike every other
        caller in this repository there is no command line to name them on: the founder's own
        command is three words long.
        """
        env = scrub_session({k: v for k, v in self._base_env.items()
                             if k != "KEEL_RUNTIME_PATH"})
        env[self.home_var] = str(self.home)
        env["KEEL_HOME"] = str(self.keel_home)
        env["KEEL_BASE_URL"] = self.base_url
        env.update(self._runtime_model_env())
        env.update(extra or {})
        return env

    def write_home_config(self) -> Path:
        """One file in the fresh keel home, naming this run's Keel.

        `keel status` and `keel_disconnect.py` take no `--base-url` (the skill's own contract), so
        a home that does not name its Keel answers `environment: null` -- the same reason
        `stack/runtime.py::reset` writes one. It is written *before* the first `-p`, so the runtime
        the skill starts and the runtime this harness later asks are provably the same Keel.
        """
        path = self.keel_home / "config.json"
        path.write_text(json.dumps({"base_url": self.base_url}, indent=2) + "\n")
        return path

    # ------------------------------------------------------------- installing, the founder's way

    def _cli(self, args: list[str], *, timeout: float = 240) -> subprocess.CompletedProcess:
        return subprocess.run([self.binary, *args], capture_output=True, text=True,
                              timeout=timeout, env=self.env(), cwd=str(self.work_dir))

    def _marketplace_argv(self, source: str) -> list[str]:
        """Both CLIs spell it identically, which is the design's *"one repository serves both
        hosts"* showing up in an argv. Overridable all the same, because the day they diverge the
        scenario must not have to know."""
        return ["plugin", "marketplace", "add", source]

    def _install_argv(self, spec: str) -> list[str]:
        return ["plugin", "install", spec]

    def add_marketplace(self, source: str = MARKETPLACE_SOURCE) -> dict:
        argv = self._marketplace_argv(source)
        done = self._cli(argv)
        return {"cmd": [self.binary, *argv], "exit_code": done.returncode,
                "stdout": done.stdout.strip(), "stderr": done.stderr.strip()}

    def install_plugin(self, spec: str = PLUGIN_SPEC) -> dict:
        argv = self._install_argv(spec)
        done = self._cli(argv)
        return {"cmd": [self.binary, *argv], "exit_code": done.returncode,
                "stdout": done.stdout.strip(), "stderr": done.stderr.strip()}

    def plugin_list(self) -> dict:
        done = self._cli(["plugin", "list"])
        return {"exit_code": done.returncode, "stdout": done.stdout.strip(),
                "stderr": done.stderr.strip()}

    def skill_proof(self) -> dict:
        """**Can this CLI see `keel-connect`, and did it come from the plugin?**

        The two CLIs answer in two different documents -- Copilot has `skill list --json`, Claude
        has `plugin details <plugin>`'s component inventory -- so what is shared is the *question*
        and the shape of the answer, never the parsing. Returns
        `{found, from_plugin, cmd, raw, detail}`; `found` and `from_plugin` are what leg one
        asserts, `raw` is what the bundle carries so a reader can check the reading by eye.
        """
        raise NotImplementedError

    def credential_plan(self) -> dict:
        """Which of this host's legitimate ways **this run** is authenticated, decided once and
        recorded. Returns `{how, variable, isolated_home}`."""
        raise NotImplementedError

    # --------------------------------------------------------------------------------- the run

    def _say_argv(self, prompt: str, *, usage_path: Path) -> list[str]:
        raise NotImplementedError

    def _parse(self, stdout: str) -> list[dict]:
        """Both CLIs stream JSON objects, one per line; a line that is not one is skipped rather
        than fatal, because a CLI is allowed to print a banner."""
        events = []
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                events.append(parsed)
        return events

    def _make_run(self, **kwargs) -> HostRun:
        raise NotImplementedError

    def _run(self, prompt: str, *, timeout: float, slug: str) -> HostRun:
        self._runs += 1
        transcript = self.artifacts / f"{self.name}-{slug}.jsonl"
        usage_path = self.artifacts / f"{self.name}-{slug}.usage.json"
        argv = self._say_argv(prompt, usage_path=usage_path)
        assert not any(flag in argv for flag in self.forbidden_flags), argv

        try:
            done = subprocess.run(argv, capture_output=True, text=True, timeout=timeout,
                                  env=self.env(), cwd=str(self.work_dir))
        except subprocess.TimeoutExpired as exc:
            partial = exc.stdout
            transcript.write_text(partial.decode("utf-8", "replace")
                                  if isinstance(partial, bytes) else (partial or ""))
            raise HostUnavailable(
                f"`{self.binary} -p` did not finish inside {timeout}s; its partial transcript is "
                f"at {transcript}") from exc
        except OSError as exc:
            raise HostUnavailable(f"`{self.binary} -p` could not be run: {exc}") from exc

        transcript.write_text(done.stdout)
        events = self._parse(done.stdout)
        usage: dict = {}
        if usage_path.is_file():
            try:
                usage = json.loads(usage_path.read_text())
            except json.JSONDecodeError:
                usage = {}
        return self._make_run(argv=argv, exit_code=done.returncode, events=events, usage=usage,
                              stderr=done.stderr.strip(), transcript_path=transcript,
                              usage_path=usage_path if usage_path.is_file() else None)

    def say(self, prompt: str, *, slug: str, timeout: float = 420) -> HostRun:
        """Say something to the host, once. There is no retry here on purpose (spec 016 FR-009): a
        live run that quietly said it twice would be reporting a number nobody spent."""
        return self._run(prompt, timeout=timeout, slug=slug)

    # ----------------------------------------------------------------- what the runtime left behind

    def envelope_facts(self, envelope: dict | None) -> dict:
        """What **this host's own per-job envelope** says about who answered and what it cost.

        The two are not the same document and are not pretended to be: Copilot's is written by
        keel-runtime's `CopilotExecutor._envelope`, which stamps `executor` and `model` and
        deliberately carries **no dollar figure** (C-7); Claude's *is* the `claude` CLI's own
        `result` event, passed through, which carries `total_cost_usd` and names no executor at
        all. Each subclass reports what its own envelope actually holds.
        """
        raise NotImplementedError


# ------------------------------------------------------------------------------ the two of them

def host_type(name: str | None = None) -> type[AgentHost]:
    """The class for a host name. Imported inside the function so the two implementations may
    import this module's vocabulary without a cycle."""
    chosen = journey_host() if name is None else name
    if chosen not in HOSTS:
        raise UnknownHost(f"{chosen!r} is not one of {list(HOSTS)}")
    if chosen == "claude":
        from harness.claude_host import ClaudeHost  # noqa: PLC0415 -- see docstring

        return ClaudeHost
    from harness.copilot_host import CopilotHost  # noqa: PLC0415

    return CopilotHost


def build_host(name: str | None = None, **kwargs) -> AgentHost:
    """The scenario's one construction site: a host by name, with this run's two homes."""
    return host_type(name)(**kwargs)


def readiness(name: str | None = None, **kwargs) -> dict[str, Any]:
    """Everything that can be known about this machine's host CLI **without spending anything**.

    Returns `{ok, reason, version, ...}`; `reason` is `None` when `ok`, and is a sentence a
    `pytest.skip` can print verbatim when it is not (C-11).
    """
    return host_type(name).readiness(**kwargs)


def which(binary: str) -> str | None:
    return shutil.which(binary)
