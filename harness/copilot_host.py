"""GitHub Copilot CLI as a **host** (spec `016-copilot-e2e`, keel-cloud
`canon/designs/keel-skill-design.md` §5/§5.5 part 2).

Everything else in this repository that has ever touched Copilot touched it as a *thinker*:
`instructions/` (spec 014) constructs keel-runtime's own `CopilotExecutor` and shells `copilot -p`
with a rendered prompt, and no skill, no plugin and no `SKILL.md` is anywhere near it. This module
is the other half -- the CLI a founder actually types into, with the keel-connect plugin installed
into it from the real marketplace, being asked *"keel connect"* in English.

**Three rules, and each is why a line here looks the way it does.**

1. **This module never starts the runtime.** `harness/connect.py`'s opening rule is that the
   harness never shells `python3 -m keel_runtime`, because keel-connect-skill is one of the four
   applications under referee; S-012 goes one further and never shells the *skill's script*
   either. The only thing that may run `keel_connect_check.py` in leg one is Copilot, having read
   `SKILL.md` and decided to. A helper here that "just ran the script to make sure" would delete
   the measurement.

2. **Nothing here reads Copilot's prose for evidence.** `reply_text` is returned so a scenario can
   make one loose *"it said connected"* check and so the whole transcript lands in the bundle, and
   that is the entire contract. What proves the skill ran is `read_heartbeat` and
   `read_launch_log` below -- artefacts of the *runtime*, which no amount of confident wording
   produces. Spec 013's acceptance bed greps the reply for a `XXXX-XXXX` shape and the word
   `device` and says so in its own comment; that bed has also never run.

3. **The credential is never copied.** `COPILOT_HOME` moves "the directory where configuration and
   state files are stored" (`copilot help environment`), and `credential_plan` states in one place
   which of the three legitimate ways a run is authenticated -- so a bundle can never leave a
   reader guessing whether an isolated home was still the founder's login.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

#: The public marketplace and the plugin in it, exactly as keel-connect-skill's own README tells a
#: founder to type them (`dist/marketplace/.claude-plugin/marketplace.json`: marketplace `keel`,
#: one plugin `keel`, sourced from `keeldiscovery/keel-connect-skill` at ref `release`).
MARKETPLACE_SOURCE = "keeldiscovery/keel-marketplace"
PLUGIN_SPEC = "keel@keel"

#: The skill's own frontmatter `name`, which is what `copilot skill list` prints.
SKILL_NAME = "keel-connect"

#: keel-runtime's `heartbeat.HEARTBEAT_FILENAME` and keel-connect-skill's
#: `keel_connect_check.LAUNCH_LOG_FILENAME`. Named here because leg one asserts them by name
#: against a home no other module in this repository owns.
HEARTBEAT_FILENAME = "runtime.heartbeat.json"
LAUNCH_LOG_FILENAME = "keel-connect-check.launch.log"
STATE_AWAITING_APPROVAL = "awaiting_approval"

USER_CODE_PREFIX = "KEEL_USER_CODE="
VERIFICATION_URI_PREFIX = "KEEL_VERIFICATION_URI="

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


class CopilotUnavailable(RuntimeError):
    """`copilot` is not on PATH, or would not run at all. A reason to skip S-012 by name (C-11),
    never to pass it quietly."""


# ------------------------------------------------------------------------------------ readiness

def readiness(binary: str = "copilot") -> dict[str, Any]:
    """Everything that can be known about this machine's Copilot **without spending a request**.

    `--model <a slug that cannot exist>` is refused by the CLI *before* any inference, against its
    own model catalogue, so it is a free probe that the binary runs, parses flags and can resolve
    a catalogue. It is deliberately not called "authenticated": the CLI may answer this from a
    cache, and a referee that inferred a login from it would be inferring. What S-012 actually
    relies on is the run itself, which fails loudly with keel-runtime's own auth markers if the
    login is not there.

    Returns `{ok, reason, version, catalogue_probe}`; `reason` is `None` when `ok`.
    """
    if shutil.which(binary) is None:
        return {"ok": False, "reason": f"no `{binary}` on PATH -- S-012 needs GitHub Copilot CLI",
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
    env = os.environ if env is None else env
    for name in ("COPILOT_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        if env.get(name):
            return {"how": "env token", "variable": name,
                    "isolated_home": "yes -- the token travels, the home does not"}
    return {"how": "stored OAuth, outside COPILOT_HOME", "variable": "",
            "isolated_home": "yes -- measured: an isolated home still resolves the model catalogue"}


# --------------------------------------------------------------------------------- the host run

@dataclass
class CopilotRun:
    """One `copilot -p` invocation: what it was asked, what it said, what it cost."""

    argv: list[str]
    exit_code: int
    reply_text: str
    events: list[dict] = field(default_factory=list)
    usage: dict = field(default_factory=dict)
    stderr: str = ""
    transcript_path: Path | None = None
    usage_path: Path | None = None

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


class CopilotHost:
    """The founder's own Copilot, pointed at a home this run owns.

    `home` is the fresh `COPILOT_HOME`; `keel_home` and `base_url` are what the *skill* will need
    when Copilot decides to run it, and they are named on the environment rather than on the
    command line because a founder names them nowhere -- `SKILL.md` says in as many words *"Do not
    pass a base URL, an executor or a credential backend"*.
    """

    def __init__(self, *, home: Path, keel_home: Path, base_url: str, artifacts: Path,
                 binary: str = "copilot", model: str | None = None,
                 runtime_model: str | None = None,
                 base_env: dict[str, str] | None = None):
        self.home = Path(home)
        self.keel_home = Path(keel_home)
        self.base_url = base_url
        self.artifacts = Path(artifacts)
        self.binary = binary
        #: `--model` for the **host** CLI: what the founder's own Copilot answers with when they
        #: type "keel connect". Leg one's subject is the founder's real CLI, so this is the plan's
        #: own default rather than a slug chosen to suit the runtime.
        self.model = model
        #: `KEEL_COPILOT_MODEL` for the **runtime**: what keel-runtime's `CopilotExecutor` pins
        #: when it answers a job. A different subject and therefore a different choice -- C-5 says
        #: a measured run pins one, and `runs/DRIFT.md` #59 says which ones the runtime can read
        #: at all. `None` leaves the runtime unpinned, which C-5 forbids in a measured run.
        self.runtime_model = runtime_model
        self._base_env = dict(os.environ if base_env is None else base_env)
        self.home.mkdir(parents=True, exist_ok=True)
        self.keel_home.mkdir(parents=True, exist_ok=True)
        self.artifacts.mkdir(parents=True, exist_ok=True)
        self._runs = 0

    # ------------------------------------------------------------------------------ environment

    def env(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        """The environment Copilot -- and therefore the skill's script, and therefore the runtime
        -- is launched with.

        `KEEL_RUNTIME_PATH` is **removed** (spec 012 FR-004, invariant T-1). This repository is
        worked on from shells that export it (keel-connect-playground's own settings do), and an
        inherited one would put the *checkout* back in place of the runtime that travelled inside
        the plugin -- a green leg one that never touched the thing it claims to referee.
        `KEEL_HOME` and `KEEL_BASE_URL` are set rather than scrubbed, because unlike every other
        caller in this repository there is no command line to name them on: the founder's own
        command is three words long.
        """
        env = {k: v for k, v in self._base_env.items() if k != "KEEL_RUNTIME_PATH"}
        env["COPILOT_HOME"] = str(self.home)
        env["KEEL_HOME"] = str(self.keel_home)
        env["KEEL_BASE_URL"] = self.base_url
        if self.runtime_model:
            # keel-runtime's own resolution order (`config.resolve_copilot_model`): --copilot-model
            # > KEEL_COPILOT_MODEL > config.json > unpinned. The skill passes no --copilot-model,
            # so this is how C-5's pin reaches the executor the runtime builds.
            #
            # **Deliberately not `self.model`.** The host's model and the runtime's are two
            # different measurements: leg one asks what a founder's own Copilot does with the
            # skill, and leg two asks what keel-runtime's executor does with a job. Tying them
            # together would mean choosing one subject's model to suit the other's.
            env["KEEL_COPILOT_MODEL"] = self.runtime_model
        env.update(extra or {})
        return env

    def write_home_config(self) -> Path:
        """One file in the fresh keel home, naming this run's Keel.

        `keel status` and `keel_disconnect.py` take no `--base-url` (the skill's own contract), so
        a home that does not name its Keel answers `environment: null` -- the same reason
        `stack/runtime.py::reset` writes one. It is written *before* the first `copilot -p`, so
        the runtime the skill starts and the runtime this harness later asks are provably the same
        Keel.
        """
        path = self.keel_home / "config.json"
        path.write_text(json.dumps({"base_url": self.base_url}, indent=2) + "\n")
        return path

    # ------------------------------------------------------------- installing, the founder's way

    def _cli(self, args: list[str], *, timeout: float = 240) -> subprocess.CompletedProcess:
        return subprocess.run([self.binary, *args], capture_output=True, text=True,
                              timeout=timeout, env=self.env(), cwd=str(self.artifacts))

    def add_marketplace(self, source: str = MARKETPLACE_SOURCE) -> dict:
        done = self._cli(["plugin", "marketplace", "add", source])
        return {"cmd": [self.binary, "plugin", "marketplace", "add", source],
                "exit_code": done.returncode, "stdout": done.stdout.strip(),
                "stderr": done.stderr.strip()}

    def install_plugin(self, spec: str = PLUGIN_SPEC) -> dict:
        done = self._cli(["plugin", "install", spec])
        return {"cmd": [self.binary, "plugin", "install", spec],
                "exit_code": done.returncode, "stdout": done.stdout.strip(),
                "stderr": done.stderr.strip()}

    def plugin_list(self) -> dict:
        done = self._cli(["plugin", "list"])
        return {"exit_code": done.returncode, "stdout": done.stdout.strip(),
                "stderr": done.stderr.strip()}

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


def _run_copilot(host: CopilotHost, prompt: str, *, timeout: float, slug: str) -> CopilotRun:
    host._runs += 1
    transcript = host.artifacts / f"copilot-{slug}.jsonl"
    usage_path = host.artifacts / f"copilot-{slug}.usage.json"
    argv = [host.binary, "-p", prompt]
    for tool in ALLOWED_TOOLS:
        argv += ["--allow-tool", tool]
    argv += ["--no-auto-update", "--no-ask-user", "--no-remote", "--no-remote-export",
             # **The referee's own AGENTS.md must never reach the thing under referee.** Copilot
             # loads custom instructions from the git root and the working directory, and the
             # working directory here is a run bundle *inside keel-e2e-eval*, whose AGENTS.md
             # describes this harness, its scenarios and what they assert. A host briefed on the
             # measurement is not the host a founder has. keel-runtime's own executor passes the
             # same flag for the same reason (`--no-custom-instructions`, spec 005).
             "--no-custom-instructions",
             "--no-color", "--output-format", "json",
             "--usage-output-file", str(usage_path)]
    if host.model:
        argv += ["--model", host.model]
    assert not any(flag in argv for flag in FORBIDDEN_FLAGS)

    try:
        done = subprocess.run(argv, capture_output=True, text=True, timeout=timeout,
                              env=host.env(), cwd=str(host.artifacts))
    except subprocess.TimeoutExpired as exc:
        transcript.write_text((exc.stdout or b"").decode("utf-8", "replace")
                              if isinstance(exc.stdout, bytes) else (exc.stdout or ""))
        raise CopilotUnavailable(
            f"`copilot -p` did not finish inside {timeout}s; its partial transcript is at "
            f"{transcript}") from exc
    except OSError as exc:
        raise CopilotUnavailable(f"`copilot -p` could not be run: {exc}") from exc

    transcript.write_text(done.stdout)
    events = []
    for line in done.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            events.append(parsed)
    usage: dict = {}
    if usage_path.is_file():
        try:
            usage = json.loads(usage_path.read_text())
        except json.JSONDecodeError:
            usage = {}
    return CopilotRun(argv=argv, exit_code=done.returncode, reply_text=_final_answer(events),
                      events=events, usage=usage, stderr=done.stderr.strip(),
                      transcript_path=transcript, usage_path=usage_path)


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


def say(host: CopilotHost, prompt: str, *, slug: str, timeout: float = 420) -> CopilotRun:
    """Say something to Copilot, once. There is no retry here on purpose (spec 016 FR-009): a live
    run that quietly said it twice would be reporting a number nobody spent."""
    return _run_copilot(host, prompt, timeout=timeout, slug=slug)


# -------------------------------------------------------------- what the skill leaves behind

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


#: The runtime's own startup line, written by the process that is running -- `cli.py`'s
#: `KEEL_EXECUTOR=<name> source=<how> binary=<path> version=<...> model=<slug or auto>`.
EXECUTOR_PREFIX = "KEEL_EXECUTOR="


def launch_executor_in(log_text: str) -> dict[str, str] | None:
    """**Which executor the runtime that is running actually chose**, read off its own startup
    line, plus how it chose it and which model it pinned.

    This exists because `keel status` cannot answer that question, and is not claiming to:
    keel-cloud's own contract says `executor` is *"which executor this home **would** run a job
    with ... resolved the same way `connect` resolves it"* -- a statement about the caller's
    environment, not about the live process (`runs/DRIFT.md` #58). Asking `status` from a
    Claude-hosted shell about a Copilot-hosted runtime therefore answers `claude`, truthfully by
    the contract's words and falsely by every reasonable reading of a key sitting beside
    `running: true`.

    The startup line has no such ambiguity: `connect` prints it once, from inside the process, out
    of the resolution that process actually made. `source=flag` is the whole chain in one word --
    `SKILL.md` told the host to add `--host copilot`, the skill's script mapped that to
    `--executor copilot`, and the runtime took it as an explicit term.

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
    """The one loose check leg one makes of Copilot's own words, and never the only evidence of
    anything (FR-003). Deliberately generous: what is being measured is that the host relayed the
    skill's `already_connected` in *some* English, not which English."""
    lowered = (reply or "").lower()
    return any(word in lowered for word in ("already connected", "is connected", "connected"))
