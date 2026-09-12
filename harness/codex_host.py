"""Codex CLI as a **host** (keel-runtime spec `008-codex-executor`; spec `019-journey-through-a-host`
generalised to a third host; keel-cloud `canon/designs/keel-skill-design.md` decision 11).

The Copilot and Claude halves were written first and this one is *mostly a rename* again. What is
not a rename was measured on 2026-09-12 with **codex-cli 0.154.0** on the founder's Mac, and each
measurement changed a line below.

**1. An isolated home does not keep the founder's login, and the credential is an API key.**
`CODEX_HOME` holds `auth.json` -- the ChatGPT-plan tokens or an API key -- so a fresh home is
`Not logged in` (measured: `codex login status`). Unlike Claude, no environment variable alone
signs a run in: `OPENAI_API_KEY` in the environment was measured **ignored** by `codex exec`
(still `Missing bearer or basic authentication`). What works is `codex login --with-api-key`,
reading the key from stdin, which writes `auth.json` into `CODEX_HOME`. So this host signs the
fresh home in itself, from **`KEEL_CODEX_API_KEY` in the caller's shell** (the matrix hands it
the organisation secret `KEEL_RUNTIME_CI_CODEX`), and `credential_plan` records that. The key
is never written anywhere but the isolated home this run owns, which the bundle never carries.

**2. Codex strips `CODEX_HOME` from the shells it runs commands in** (measured: a command asked
to print it saw nothing while `KEEL_*` and `GH_*` came through). The runtime is started from
inside such a shell by the skill's script, and its executor's own `codex` must find the same
`auth.json` -- so `env()` also names the home as `KEEL_CODEX_HOME`, keel-runtime's twin
(`executor._CREDENTIAL_TWINS`), which nothing strips.

**3. The sandbox, not approvals, is what stands between the skill and the runtime.** Under
Codex's default sandbox the check script's first write, `~/.keel/<slug>/...launch.log`, is
refused and a spawned runtime would inherit `CODEX_SANDBOX_NETWORK_DISABLED=1`. `codex exec`
never asks anyone anything, so the journey runs with `--sandbox danger-full-access` -- an
explicit sandbox choice, recorded in the argv -- and **not** `--dangerously-bypass-approvals-and-
sandbox`, the blanket the design's own tests forbid. Every command the model runs still lands in
the stream as a `command_execution` item, so *what the skill needed* stays observable
(`tools_used`), which is the reason the two other hosts grant two tools and not all of them.
Measured: with `-s danger-full-access` alone, "keel connect" read `SKILL.md`, ran the check and
reached `authorization_started`, the runtime alive afterwards.

**4. The proof that the skill came from the plugin is `codex plugin list`.** It prints one block
per marketplace with `keel@keel  installed, enabled  <version>  <source>`, and the source names
the release branch; beside it the skill file sits under
`$CODEX_HOME/plugins/cache/keel/keel/<version>/skills/keel-connect/SKILL.md` (measured). Both
are read.

**5. No model in the stream.** `codex exec --json` names no model anywhere (measured; the CLI's
plain-mode header does). So `model` is the pin when there is one and `None` when there is not,
and the bundle says so rather than guessing. Tokens are the unit (`turn.completed.usage`), never
dollars -- C-7's rule, a third unit.
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

#: The key's name in the caller's shell. The matrix sets it from `KEEL_RUNTIME_CI_CODEX`; a
#: founder running the journey from the Mac exports it themselves. Never read from a file (T-5).
API_KEY_ENV = "KEEL_CODEX_API_KEY"
SANDBOX = "danger-full-access"
FORBIDDEN_FLAGS = ("--bare", "--dangerously-bypass-approvals-and-sandbox",
                   "--dangerously-bypass-hook-trust", "--ignore-user-config")
#: Item types that are an answer rather than a tool -- keel-runtime's own rule
#: (`executor._CODEX_ANSWER_ITEM_TYPES`), so leg one and leg two read the stream the same way.
ANSWER_ITEM_TYPES = frozenset({"agent_message", "reasoning"})
#: Where `codex plugin add` puts an installed plugin's tree (measured 0.154.0).
PLUGIN_CACHE = ("plugins", "cache")


def login_status(binary: str, home: Path, base_env: dict[str, str] | None = None) -> dict:
    """`codex login status` against one home. **Free, and it starts no session.** Measured
    wording: `Not logged in`, `Logged in using an API key - ***`, `Logged in using ChatGPT`."""
    env = scrub_session(dict(os.environ if base_env is None else base_env))
    env["CODEX_HOME"] = str(home)
    try:
        done = subprocess.run([binary, "login", "status"], capture_output=True, encoding="utf-8",
                              errors="replace", timeout=60, env=env)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"error": f"`{binary} login status` did not answer: {exc}"}
    text = ((done.stdout or "") + (done.stderr or "")).strip()
    lowered = text.lower()
    return {"loggedIn": "logged in" in lowered and "not logged in" not in lowered,
            "how": ("api_key" if "api key" in lowered else
                    "chatgpt" if "chatgpt" in lowered else "none"),
            "text": text[:200], "exit_code": done.returncode}


def login_with_api_key(binary: str, home: Path, key: str,
                       base_env: dict[str, str] | None = None) -> dict:
    """`codex login --with-api-key`, the key on stdin, into `home`. Writes `auth.json` there and
    nowhere else (measured: `auth_mode: apikey`)."""
    env = scrub_session(dict(os.environ if base_env is None else base_env))
    env["CODEX_HOME"] = str(home)
    home.mkdir(parents=True, exist_ok=True)
    try:
        done = subprocess.run([binary, "login", "--with-api-key"], input=key, capture_output=True,
                              encoding="utf-8", errors="replace", timeout=60, env=env)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "error": f"`{binary} login --with-api-key` did not answer: {exc}"}
    return {"ok": done.returncode == 0,
            "text": ((done.stdout or "") + (done.stderr or "")).strip()[:200]}


def readiness(binary: str = "codex", env: dict[str, str] | None = None) -> dict[str, Any]:
    """Everything that can be known about this machine's Codex **without spending a token**.

    Three questions, the Claude shape: is the CLI there, what version, and **would a fresh home
    be able to authenticate at all**. The third has one answer on this host: only if the caller's
    shell carries `KEEL_CODEX_API_KEY`, because an isolated `CODEX_HOME` is `Not logged in` and no
    environment variable alone signs `codex exec` in. The key is proved in a throwaway home with
    `codex login --with-api-key` then `codex login status` -- both local, neither a model call --
    and the home is removed.

    Returns `{ok, reason, version, auth, isolated_auth}`; `reason` is `None` when `ok`.
    """
    env = os.environ if env is None else env
    resolved = shutil.which(binary)
    if resolved is None:
        return {"ok": False, "reason": f"no `{binary}` on PATH -- the Codex journey needs Codex "
                                        f"CLI (`npm install -g @openai/codex`)",
                "version": None, "auth": None, "isolated_auth": None}
    binary = resolved
    try:
        version = subprocess.run([binary, "--version"], capture_output=True, encoding="utf-8",
                                 errors="replace", timeout=60).stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "reason": f"`{binary} --version` did not answer: {exc}",
                "version": None, "auth": None, "isolated_auth": None}
    key = (env.get(API_KEY_ENV) or "").strip()
    if not key:
        return {
            "ok": False,
            "reason": (
                f"no {API_KEY_ENV} in this shell, so a fresh CODEX_HOME cannot authenticate and "
                "the journey would fail on its first word. Unlike COPILOT_HOME, an isolated Codex "
                "home does not keep the founder's stored login (measured: `codex login status` "
                "there reads Not logged in), and OPENAI_API_KEY in the environment alone is "
                "ignored by `codex exec` (measured). Export an OpenAI API key as "
                f"{API_KEY_ENV} and run it again; nothing here reads a secret from a file or a "
                "keychain (T-5)."),
            "version": version, "auth": None, "isolated_auth": None}
    probe_dir = Path(tempfile.mkdtemp(prefix="keel-journey-codex-auth-"))
    try:
        before = login_status(binary, probe_dir, base_env=env)
        logged = login_with_api_key(binary, probe_dir, key, base_env=env)
        after = login_status(binary, probe_dir, base_env=env)
    finally:
        shutil.rmtree(probe_dir, ignore_errors=True)
    if not logged.get("ok") or not after.get("loggedIn"):
        return {"ok": False,
                "reason": (f"`{binary} login --with-api-key` did not sign a fresh home in: "
                           f"{logged.get('error') or logged.get('text') or after.get('text')!r}"),
                "version": version, "auth": None, "isolated_auth": {"before": before, "after": after}}
    return {"ok": True, "reason": None, "version": version,
            "auth": {"how": after.get("how"), "variable": API_KEY_ENV},
            "isolated_auth": {"before": before, "after": after}}


def model_accepted(slug: str, binary: str = "codex") -> bool:  # noqa: ARG001
    """**Always true, and the docstring is the point** -- the Claude answer. Codex has no free
    catalogue probe: every way of finding out whether `-m <slug>` is honoured starts a session.
    A wrong slug fails the run loudly on the first word, and the bundle records the pin."""
    return True


def _final_answer(events: list[dict]) -> str:
    """The last completed `agent_message` with text -- keel-runtime's own rule
    (`executor._codex_final_answer`): a run measured emitting a sentence of intent and then the
    answer, so the last one is the one."""
    for event in reversed(events):
        if event.get("type") != "item.completed":
            continue
        item = event.get("item") or {}
        if item.get("type") != "agent_message":
            continue
        text = item.get("text")
        if isinstance(text, str) and text.strip():
            return text.strip()
    return ""


def _usage(events: list[dict]) -> dict:
    usage: dict = {}
    for event in events:
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            usage = event["usage"]
    return usage


@dataclass
class CodexRun(HostRun):
    """One `codex exec` invocation. **Tokens, never dollars and never premium requests** -- the
    CLI's own unit, kept as the CLI reports it (C-7, a third unit)."""

    pinned_model: str | None = None

    @property
    def tokens(self) -> dict:
        return {k: v for k, v in _usage(self.events).items() if isinstance(v, (int, float))}

    @property
    def num_turns(self) -> int:
        return sum(1 for event in self.events if event.get("type") == "turn.completed")

    @property
    def model(self) -> str | None:
        """Which model answered. The `--json` stream names none (measured), so this is the pin
        when there was one and `None` when there was not -- recorded, never guessed."""
        return self.pinned_model

    @property
    def tools_used(self) -> list[str]:
        """Every command or tool the host called, in order of first use: the `command_execution`
        items' commands, and any other non-answer item's type."""
        seen: list[str] = []
        for event in self.events:
            if event.get("type") != "item.started":
                continue
            item = event.get("item") or {}
            kind = item.get("type")
            if kind in ANSWER_ITEM_TYPES or not kind:
                continue
            name = item.get("command") if kind == "command_execution" else None
            label = f"{kind}: {name}" if isinstance(name, str) and name else str(kind)
            if label not in seen:
                seen.append(label)
        return seen

    def spend(self) -> dict:
        return {"unit": "tokens (the CLI's own turn.completed usage; never converted into a "
                        "dollar figure or a premium request)",
                "tokens": self.tokens, "num_turns": self.num_turns}


class CodexHost(AgentHost):
    """The founder's own Codex, pointed at a `CODEX_HOME` this run owns and signs in itself."""

    name = "codex"
    binary = "codex"
    home_var = "CODEX_HOME"
    executor = "codex"
    envelope_names_its_executor = True
    forbidden_flags = FORBIDDEN_FLAGS
    stdin_devnull = True
    readiness = staticmethod(readiness)
    model_accepted = staticmethod(model_accepted)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._login: dict = {"how": "none"}
        key = (self._base_env.get(API_KEY_ENV) or "").strip()
        if key:
            done = login_with_api_key(self.binary, self.home, key, base_env=self._base_env)
            self._login = {"how": "api_key" if done.get("ok") else "failed",
                           "detail": done.get("text") or done.get("error")}

    def env(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        """The base environment plus the twin: Codex strips `CODEX_HOME` from the shells it runs
        commands in (measured), and keel-runtime reads `KEEL_CODEX_HOME` back into it for the
        executor's own `codex`. The API key itself does not travel: it is already in `auth.json`."""
        env = super().env(extra)
        env.pop(API_KEY_ENV, None)
        env["KEEL_CODEX_HOME"] = str(self.home)
        return env

    def _runtime_model_env(self) -> dict[str, str]:
        """keel-runtime's own resolution order (`config.resolve_codex_model`): `--codex-model` >
        `KEEL_CODEX_MODEL` > `config.json` > the account's default. The skill passes no
        `--codex-model`, so this is how a pin reaches the executor the runtime builds."""
        return {"KEEL_CODEX_MODEL": self.runtime_model} if self.runtime_model else {}

    def _install_argv(self, spec: str) -> list[str]:
        """`codex plugin add <name>@<marketplace>` -- the one verb that differs from the other two
        CLIs' `plugin install`. Measured: installs the release branch's tree as it is."""
        return ["plugin", "add", spec]

    def credential_plan(self) -> dict:
        """**Measured, not guessed** -- `codex login status` inside this run's own home, after
        this host signed it in from the caller's shell."""
        body = login_status(self.binary, self.home, base_env=self._base_env)
        if body.get("error"):
            return {"how": "unknown", "variable": "", "isolated_home": "yes -- and the CLI would "
                    "not say how it is authenticated", "probe": body["error"]}
        return {
            "how": {"api_key": f"an API key from the caller's own shell ({API_KEY_ENV}), signed "
                               "into this run's own CODEX_HOME by `codex login --with-api-key`",
                    "chatgpt": "a stored ChatGPT login (not this harness's doing)",
                    "none": "nothing -- this home cannot authenticate"}.get(body.get("how"), str(body.get("how"))),
            "variable": API_KEY_ENV if body.get("how") == "api_key" else "",
            "isolated_home": ("yes -- and measured: an isolated CODEX_HOME does NOT keep the "
                              "founder's stored login, and OPENAI_API_KEY in the environment alone "
                              "is ignored, so the key in this shell is what signs it in"),
            "loggedIn": bool(body.get("loggedIn")),
            "status": body.get("text"),
            "login": self._login,
        }

    def _cache_skill_file(self) -> Path | None:
        root = self.home.joinpath(*PLUGIN_CACHE)
        if not root.is_dir():
            return None
        hits = sorted(root.glob(f"*/{PLUGIN_NAME}/*/skills/{SKILL_NAME}/SKILL.md"))
        return hits[-1] if hits else None

    def skill_proof(self) -> dict:
        """`codex plugin list`, read for `keel@keel installed, enabled`, plus the skill file in the
        plugin cache -- the two facts that say the skill is visible and came from the plugin."""
        done = self._cli(["plugin", "list"])
        raw = ((done.stdout or "") + ("\n" + done.stderr if done.stderr else "")).strip()
        (self.artifacts / "codex-plugin-list.txt").write_text(raw + "\n" if raw else "")
        line = next((ln.strip() for ln in raw.splitlines()
                     if ln.strip().startswith(PLUGIN_SPEC)), "")
        installed = "installed" in line
        skill_file = self._cache_skill_file()
        return {"found": installed and skill_file is not None,
                "from_plugin": installed,
                "cmd": [self.binary, "plugin", "list"],
                "raw": raw,
                "detail": {"listing line": line, "skill file": str(skill_file) if skill_file else None,
                           "exit_code": done.returncode, "stderr": (done.stderr or "").strip()}}

    def _say_argv(self, prompt: str, *, usage_path: Path) -> list[str]:  # noqa: ARG002
        """`codex exec "<prompt>"`: non-interactive, one event per line, in this run's own working
        directory, the sandbox off by name (see the module docstring, point 3). `usage_path` is
        unused: the stream's own `turn.completed` carries the usage."""
        argv = [self.binary, "exec", prompt, "--json", "--skip-git-repo-check",
                "--sandbox", SANDBOX, "--color", "never", "-C", str(self.work_dir)]
        if self.model:
            argv += ["-m", self.model]
        return argv

    def _make_run(self, **kwargs) -> CodexRun:
        return CodexRun(reply_text=_final_answer(kwargs.get("events") or []),
                        pinned_model=self.model, **kwargs)

    def envelope_facts(self, envelope: dict | None) -> dict:
        """keel-runtime's `CodexExecutor._envelope`: stamps `executor`, carries `tokens`, and no
        dollar figure and no premium requests (C-7)."""
        envelope = envelope or {}
        return {"executor": envelope.get("executor"),
                "executor_named": True,
                "model": envelope.get("model"),
                "tokens": envelope.get("tokens"),
                "num_turns": envelope.get("num_turns"),
                "is_error": envelope.get("is_error")}


def say(host: CodexHost, prompt: str, *, slug: str, timeout: float = 420) -> CodexRun:
    """Say something to Codex, once. No retry, on purpose (spec 016 FR-009)."""
    return host.say(prompt, slug=slug, timeout=timeout)
