"""Spec 062: the back-test runner -- a real founder's idea walked on Keel's AI, locally, recorded, never held to a corpus.

`make backtest ENTRY=<id>` (the Makefile; the pytest entry is `evals/run_backtest.py`, which no `make eval`, `make
unit`, matrix cell or checker collects -- it is not a `test_*.py` file). The entry is a **back-test entry**
(`instructions/corpus.py`, `load(..., backtest=True)`: keel-cloud's `canon/designs/measured-beliefs/backtest/`), a
corpus-shaped file written from public material with no golden expectations. What this module owns:

1. **The refusals** (FR-2): no `KEEL_ANTHROPIC_API_KEY` in the caller's shell, no `ENTRY`, a stack already answering
   (its keel-cloud was booted without this shell's key, so the target brings its own up and down), keel-cloud not saying
   *Keel's AI is ON* -- each one sentence. The key is passed to keel-cloud through the environment `stack/cloud.py`
   hands it and is never read, logged, echoed or written here; only its presence is checked.
2. **The founder** (FR-2): `Backtest Founder`, `backtest@keel-backtest.test`, registered at run time on the local
   stub (`POST /identities`, ungated locally) -- outside keel-cloud's `keel.v2.vendors.fake-for` -- and signed up through
   keel-web's `/signup`, the one door that makes an account on Keel's AI. Contacts, renders and the transcriber stay the
   local stack's fakes (`stack/cloud.py`), so nothing but model calls leaves the machine.
3. **The camera** (FR-3): one full-page screenshot of every founder screen as it is about to be answered, and of every
   served respondent screen on one person a link, into `runs/<run>/screens/` as `founder-NN-<slug>.png` /
   `respondent-<link>-NN-<slug>.png`, with what each screen drew (kicker, question, hint, the options as rendered).
4. **The export** (FR-3): 060/061's at the last answer into `runs/<run>/export/`, names kept, no verdict gate (the
   contract export moves to `runs/<run>/contract-export/` on this run alone).
5. **The transcript** (FR-4): `runs/<run>/backtest.md` (for reading) and `backtest.json` (for a judge), from the
   camera, the recorder's captures and the wire -- founder screens, respondent questions per link, the brief, the
   readings beside the file's anchoring, and cost and time. Nothing in either is asserted.

It lives in `evals/` beside `corpus_scenario.py`, whose `run()` it is handed to (`backtest=`).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

#: FR-2: the one variable the caller's shell must carry. Its value is never read here.
KEY_VAR = "KEEL_ANTHROPIC_API_KEY"
#: The entry `make backtest ENTRY=` names, as the pytest entry reads it.
ENTRY_VAR = "KEEL_BACKTEST_ENTRY"
#: keel-cloud `keel.v2.vendors.fake-for`'s default (`application.yml`), and the variable a shell may override it with.
FAKE_FOR_VAR = "KEEL_VENDORS_FAKE_FOR"
FAKE_FOR_DEFAULT = "keel-e2e-eval.test"

#: FR-2: the back-test founder, registered on the local stub at run time (its `sub` is the stub's `cell-backtest`).
IDENTITY_ID = "backtest"
IDENTITY_NAME = "Backtest Founder"
IDENTITY_EMAIL = "backtest@keel-backtest.test"

#: How many times longer a wait on a model may take than the scripted journeys' -- S-012's on the Keel door
#: (`agent_host` `keels_ai_job_wait_s` 660 s over the scripted 60 s).
PATIENCE = 11.0

#: How many failed model jobs (calibration questions, the questionnaire) the back-test retries as the founder's screen
#: would, before the walk stops -- each one a finding in the transcript (the first paid run, 2026-10-22: PROBLEM's
#: CALIBRATION_QUESTIONS came back RESULT_INVALID, an item of ten words against L2's nine).
RETRIES = int(os.environ.get("KEEL_BACKTEST_RETRIES") or 3)  # KEEL_BACKTEST_RETRIES raises it for one run (062 follow-up, 2026-10-22: 09-karsa
#: spent all three on SOLUTION calibration, which Keel's AI failed four times running; a founder would keep pressing)

#: Where the run's own files go, under `runs/<run>/`.
SCREENS_DIR = "screens"
EXPORT_DIR = "export"
CONTRACT_DIR = "contract-export"
MARKDOWN = "backtest.md"
RECORD = "backtest.json"

#: keel-cloud `AnthropicClientFactory`'s startup line when the key reached it.
KEEL_AI_ON = "Keel's AI is ON"

#: keel-web's link words in a file name.
LINK_SLUG = {"PRIMARY": "primary", "COMMERCIAL_B2B": "decision-maker"}


# ------------------------------------------------------------------------------------------------ 1. refusals

def refusal(env: dict | None = None) -> str | None:
    """FR-2's one sentence when the caller's shell carries no key, else `None`. Reads presence only."""
    env = os.environ if env is None else env
    if not (env.get(KEY_VAR) or "").strip():
        return (f"make backtest refuses: {KEY_VAR} is not set in this shell -- the local stack passes it to keel-cloud, "
                "which answers every job of the back-test on Keel's AI (spec 062 FR-2); it is never logged, echoed or "
                "written")
    return None


def entry_refusal(env: dict | None = None) -> str | None:
    env = os.environ if env is None else env
    if not (env.get(ENTRY_VAR) or "").strip():
        return ("make backtest refuses: no ENTRY -- name a back-test entry, `make backtest ENTRY=<id>` (keel-cloud "
                "canon/designs/measured-beliefs/backtest/<id>.yaml)")
    return None


def stack_up_refusal() -> str:
    return ("make backtest refuses: a stack is already answering on the eval ports, and its keel-cloud was not booted "
            f"from this shell, so it may carry no {KEY_VAR} -- `make down` first; the back-test brings its own stack "
            "up and down")


def fake_for(env: dict | None = None) -> str:
    env = os.environ if env is None else env
    value = env.get(FAKE_FOR_VAR)
    return FAKE_FOR_DEFAULT if value is None else value


def in_fake_for(email: str, listed: str) -> bool:
    """keel-cloud `FakeFor.matches`: exact emails and bare domains, comma- or space-separated, case-insensitive."""
    entries = {e.strip().lower() for e in re.split(r"[,\s]+", listed or "") if e.strip()}
    e = (email or "").strip().lower()
    if e in entries:
        return True
    at = e.rfind("@")
    return 0 <= at < len(e) - 1 and e[at + 1:] in {x for x in entries if "@" not in x}


def keel_ai_on(cloud_log: Path) -> bool:
    try:
        return KEEL_AI_ON in Path(cloud_log).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


# ---------------------------------------------------------------------------------- 1b. the host door (spec 066)

#: FR-1: `make backtest DOOR=` -- `keel` (spec 062, the default) or `host` (the founder's own CLI through the runtime).
DOOR_VAR = "KEEL_BACKTEST_DOOR"
DOORS = ("keel", "host")
DEFAULT_DOOR = "keel"
#: FR-1: `HOST=` on the host door; `claude` is the only host spec 066 builds.
HOST_VAR = "KEEL_BACKTEST_HOST"
HOSTS = ("claude",)
#: FR-2: `MODEL=` -- read, and refused by name: the runtime has no session-wide `--model` (judgement call 2).
MODEL_VAR = "KEEL_BACKTEST_MODEL"

#: FR-2: the runtime's home inside the run, and the log its stdout and stderr go to.
KEEL_HOME_DIR = "keel_home"
RUNTIME_LOG = "launch.log"
#: FR-5: the heartbeat as it last read before the runtime was stopped (the runtime removes its own on SIGTERM).
HEARTBEAT_LAST = "runtime.heartbeat.last.json"
#: FR-3: how long the launch log may take to print `KEEL_USER_CODE=`; how long the heartbeat may take to say connected.
USER_CODE_WAIT_S = 90.0
CONNECTED_WAIT_S = 60.0
#: FR-5: SIGTERM, then SIGKILL after this long.
STOP_GRACE_S = 10.0
#: keel-runtime `heartbeat.STATE_CONNECTED`.
STATE_CONNECTED = "connected"

#: The words the header says on the host door (FR-3).
HOST_DOOR_WORDS = "answered by the founder's own Claude Code (host door)"
NOT_PRICED = "not priced on this door"
#: FR-4: the finding a run that stopped on the plan's limit ends with, and the runner reads back.
LIMIT_FINDING = "stopped by the plan's limit at"
#: FR-6: the runner's wait when the limit names no time it can read.
LIMIT_DEFAULT_WAIT_S = 30 * 60


class UnknownDoor(ValueError):
    """`DOOR=` named something that is neither door -- refused by name, never a fallback (a typo that ran the other
    door would spend the other account's money)."""


def door(env: dict | None = None) -> str:
    env = os.environ if env is None else env
    raw = (env.get(DOOR_VAR) or "").strip().lower()
    if not raw:
        return DEFAULT_DOOR
    if raw not in DOORS:
        raise UnknownDoor(f"make backtest refuses: DOOR={raw!r} is not a door -- `DOOR=keel` (Keel's AI, spec 062) or "
                          "`DOOR=host` (the founder's own Claude Code through the runtime, spec 066)")
    return raw


def host(env: dict | None = None) -> str:
    """FR-1: `HOST=` on the host door, `claude` when unsaid; any other host refused by name (as
    `agent_host.journey_host` refuses one it does not know)."""
    env = os.environ if env is None else env
    raw = (env.get(HOST_VAR) or "").strip().lower() or "claude"
    if raw not in HOSTS:
        raise UnknownDoor(f"make backtest refuses: HOST={raw!r} on the host door -- spec 066 builds `HOST=claude` only "
                          "(the founder's own Claude Code)")
    return raw


def door_refusal(env: dict | None = None) -> str | None:
    """FR-1 / FR-2: the one sentence for a door, host or model the back-test will not run, else `None`."""
    env = os.environ if env is None else env
    try:
        if door(env) != "host":
            return None
        host(env)
    except UnknownDoor as refused:
        return str(refused)
    if (env.get(MODEL_VAR) or "").strip():
        return (f"make backtest refuses: MODEL={(env.get(MODEL_VAR) or '').strip()!r} on the host door -- keel-runtime "
                "has no session-wide --model since its spec 009: every job runs on the model keel-cloud's routing "
                "table names for claude (the job's own `model.claude`), else the CLI's default, so a pin here would be "
                "recorded and never happen")
    return None


def host_readiness(binary: str = "claude", env: dict | None = None) -> dict:
    """What the founder's CLI says about itself, for nothing: its version, and from `claude auth status` the two
    fields `loggedIn` and `authMethod` only (nothing else of that output is kept, printed or written). `refusal` is a
    sentence when the CLI is missing or logged out and no `CLAUDE_CODE_OAUTH_TOKEN` is in the shell."""
    env = dict(os.environ if env is None else env)
    out: dict = {"binary": shutil.which(binary), "version": None, "loggedIn": None, "authMethod": None,
                 "oauth token in the shell": bool((env.get("CLAUDE_CODE_OAUTH_TOKEN") or "").strip()),
                 "CLAUDE_CONFIG_DIR": "the caller's" if env.get("CLAUDE_CONFIG_DIR") else "unset (~/.claude)",
                 "refusal": None}
    if not out["binary"]:
        out["refusal"] = f"make backtest refuses: no `{binary}` on PATH -- the host door answers on the founder's own CLI"
        return out
    run_env = runtime_env(env)
    try:
        out["version"] = subprocess.run([out["binary"], "--version"], capture_output=True, encoding="utf-8",
                                        timeout=30, env=run_env).stdout.strip() or None
        status = subprocess.run([out["binary"], "auth", "status"], capture_output=True, encoding="utf-8",
                                timeout=30, env=run_env)
        parsed = json.loads(status.stdout or "{}")
        out["loggedIn"], out["authMethod"] = parsed.get("loggedIn"), parsed.get("authMethod")
    except (OSError, subprocess.SubprocessError, ValueError, AttributeError):
        pass
    if out["loggedIn"] is not True and not out["oauth token in the shell"]:
        out["refusal"] = (f"make backtest refuses: `{binary} auth status` does not say loggedIn and the shell carries no "
                          "CLAUDE_CODE_OAUTH_TOKEN -- the host door answers on the founder's own Claude Code login")
    return out


#: What never reaches the runtime the back-test starts: an API key would bill an API account in place of the
#: founder's login (judgement call 4), and `KEEL_RUNTIME_PATH` would swap the checkout under test (as S-012 removes it).
RUNTIME_ENV_DROPPED = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", KEY_VAR, "KEEL_RUNTIME_PATH", "KEEL_HOME",
                       "KEEL_BASE_URL", "PYTHONPATH")


def runtime_env(env: dict | None = None, *, pythonpath: str | None = None) -> dict:
    """FR-2: the caller's shell, without the markers of the agent session this harness may itself run in
    (`agent_host.scrub_session`) and without `RUNTIME_ENV_DROPPED` -- but `CLAUDE_CONFIG_DIR` left as the caller's
    shell has it (the founder's `~/.claude` when unset), and `CLAUDE_CODE_OAUTH_TOKEN` passed through when present."""
    from harness import agent_host                                 # noqa: PLC0415
    env = dict(os.environ if env is None else env)
    out = agent_host.scrub_session(env)
    if env.get("CLAUDE_CONFIG_DIR"):
        out["CLAUDE_CONFIG_DIR"] = env["CLAUDE_CONFIG_DIR"]
    for name in RUNTIME_ENV_DROPPED:
        out.pop(name, None)
    if pythonpath:
        out["PYTHONPATH"] = pythonpath
    return out


def runtime_argv(base_url: str, keel_home: Path, *, python: str | None = None, host_name: str = "claude") -> list[str]:
    """FR-2's command, exactly: `python -m keel_runtime connect --base-url … --executor claude --host claude --home
    <run_dir>/keel_home --no-browser`, and the credential kept in that home (`--credential-backend file`, judgement
    call 3) -- never the founder's keychain, and removed at teardown."""
    return [python or sys.executable, "-m", "keel_runtime", "connect", "--base-url", base_url,
            "--executor", host_name, "--host", host_name, "--home", str(keel_home), "--no-browser",
            "--credential-backend", "file"]


def connect_skill_versions(checkout: Path) -> dict:
    """keel-connect-skill's `VERSION` and `RUNTIME_VERSION`, as the checkout carries them (FR-2)."""
    out = {"checkout": str(checkout)}
    for name in ("VERSION", "RUNTIME_VERSION"):
        try:
            out[name] = (Path(checkout) / name).read_text(encoding="utf-8").strip()
        except OSError:
            out[name] = None
    out["commit"] = _sha(Path(checkout))
    return out


@dataclass
class HostRuntime:
    """FR-2 / FR-5: keel-connect-skill's runtime, started by the back-test from the sibling checkout and stopped when
    the journey ends. `argv` / `cwd` / `env` are what `start` runs (a test hands a fake runtime in)."""
    keel_home: Path
    argv: list
    cwd: Path
    #: never in a repr: pytest's `-l` prints a failing frame's locals, and the shell may carry a login token
    env: dict = field(repr=False)
    proc: Any = None
    started_at: float | None = None
    stopped: dict | None = None

    @property
    def log_path(self) -> Path:
        return Path(self.keel_home) / RUNTIME_LOG

    def start(self) -> None:
        Path(self.keel_home).mkdir(parents=True, exist_ok=True)
        log = open(self.log_path, "ab")                       # noqa: SIM115 - the child owns it until it exits
        try:
            self.proc = subprocess.Popen(self.argv, cwd=str(self.cwd), env=self.env, stdout=log,
                                         stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
        finally:
            log.close()
        self.started_at = time.monotonic()

    def log(self) -> str:
        from harness import agent_host                             # noqa: PLC0415
        return agent_host.read_launch_log(self.keel_home, RUNTIME_LOG)

    def heartbeat(self) -> dict | None:
        from harness import agent_host                             # noqa: PLC0415
        return agent_host.read_heartbeat(self.keel_home)

    def alive(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def wait_for_code(self, timeout_s: float = USER_CODE_WAIT_S) -> tuple[str | None, str | None]:
        """FR-3: the launch log's `KEEL_USER_CODE=` and `KEEL_VERIFICATION_URI=`, up to `timeout_s`."""
        from harness import agent_host                             # noqa: PLC0415
        deadline = time.monotonic() + timeout_s
        while True:
            text = self.log()
            code, uri = agent_host.user_code_in(text), agent_host.verification_uri_in(text)
            if (code and uri) or time.monotonic() > deadline or not self.alive():
                return code, uri
            time.sleep(0.5)

    def wait_for_connected(self, timeout_s: float = CONNECTED_WAIT_S) -> dict | None:
        """FR-3: the heartbeat in its connected state (an agent session exists), up to `timeout_s`."""
        deadline = time.monotonic() + timeout_s
        while True:
            beat = self.heartbeat()
            if (beat or {}).get("state") == STATE_CONNECTED or time.monotonic() > deadline or not self.alive():
                return beat
            time.sleep(0.5)

    def stop(self, grace_s: float = STOP_GRACE_S) -> dict:
        """FR-5: SIGTERM, then SIGKILL after `grace_s`; the heartbeat's last state kept in `HEARTBEAT_LAST` first (the
        runtime removes its own file on SIGTERM), the launch log left where it is, the home's credential removed.
        Idempotent: the second call answers the first's record."""
        if self.stopped is not None:
            return self.stopped
        beat = self.heartbeat()
        record: dict = {"pid": getattr(self.proc, "pid", None), "heartbeat at the end": beat, "signal": None,
                        "exit code": None}
        if beat is not None:
            (Path(self.keel_home) / HEARTBEAT_LAST).write_text(json.dumps(beat, indent=2) + "\n", encoding="utf-8")
        if self.proc is not None and self.proc.poll() is None:
            record["signal"] = "SIGTERM"
            try:
                self.proc.send_signal(signal.SIGTERM)
                self.proc.wait(timeout=grace_s)
            except subprocess.TimeoutExpired:
                record["signal"] = "SIGKILL"
                self.proc.kill()
                self.proc.wait(timeout=grace_s)
        if self.proc is not None:
            record["exit code"] = self.proc.returncode
        record["alive after"] = self.alive()
        record["credential removed"] = _remove_credential(Path(self.keel_home))
        if self.started_at is not None:
            record["ran_s"] = round(time.monotonic() - self.started_at, 1)
        self.stopped = record
        return record


#: keel-runtime `credential_store`'s file backend's names (judgement call 3: removed at teardown, never left in a run).
CREDENTIAL_FILES = ("credentials.json", "credential.json")


def _remove_credential(keel_home: Path) -> list[str]:
    removed = []
    for name in CREDENTIAL_FILES:
        path = keel_home / name
        if path.is_file():
            path.unlink()
            removed.append(name)
    return removed


def host_door_refusal(me: dict | None) -> str | None:
    """FR-3: `/v2/me` after the approval reads the door's `aiPath` `OWN` and the back-test founder's email -- `None` when
    it does, else the sentence."""
    me = me or {}
    if me.get("aiPath") != "OWN":
        return (f"the account reads aiPath {me.get('aiPath')!r}, not 'OWN': the sign-in that carried the code did not "
                "make the account on the founder's own AI, so its jobs would go to Keel's")
    if (me.get("email") or "").lower() != IDENTITY_EMAIL:
        return f"the account reads email {me.get('email')!r}, not {IDENTITY_EMAIL!r}"
    return None


def host_door_jobs(per_job: list[dict], host_name: str = "claude") -> dict:
    """FR-3: every job that was answered carries `execution.host` = the host and a named model (`model_used`, else
    `model_requested`): a COMPLETED job without both is bad, and so is any job whose execution names another host. A
    job that failed or was cancelled with no execution at all (nothing answered it) is listed apart, never bad.
    Returns `{"jobs", "landed", "completed", "open", "no execution", "bad"}` -- `bad` empty when it holds."""
    keys = ("screen", "status", "host", "model_used", "model_requested", "job_id")
    landed = [r for r in per_job if r.get("status") not in _OPEN]
    completed = [r for r in landed if r.get("status") == "COMPLETED"]
    bad = [{k: r.get(k) for k in keys} for r in landed
           if (r.get("status") == "COMPLETED"
               and (r.get("host") != host_name or not (r.get("model_used") or r.get("model_requested"))))
           or (r.get("host") not in (None, host_name))]
    return {"jobs": len(per_job), "landed": len(landed), "completed": len(completed),
            "open": [{k: r.get(k) for k in ("screen", "status")} for r in per_job if r.get("status") in _OPEN],
            "no execution": [{k: r.get(k) for k in ("screen", "status")} for r in landed
                             if r.get("status") != "COMPLETED" and r.get("host") is None],
            "bad": bad}


#: Claude Code's `result` event `usage` keys summed per job and in all (spec 066 FR-3; the founder's plan consumption).
USAGE_KEYS = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")


def cli_usage(keel_home: Path, job_ids: list[str] | None = None) -> dict:
    """FR-3: the cost section's own figure on the host door -- what the CLI itself reported per job, read off the
    runtime's `jobs/<id>/envelope.json` (Claude Code's `result` event): `total_cost_usd` and the token counts of
    `modelUsage`. That figure is the CLI's list-price equivalent; on a claude.ai login the plan pays it, nobody is
    billed it. When no envelope carries a cost the section says `NOT_PRICED`."""
    jobs_dir = Path(keel_home) / "jobs"
    rows = []
    wanted = set(job_ids) if job_ids else None
    for envelope in sorted(jobs_dir.glob("*/envelope.json")) if jobs_dir.is_dir() else []:
        job_id = envelope.parent.name
        if wanted is not None and job_id not in wanted:
            continue
        try:
            body = json.loads(envelope.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        tokens: dict = {}
        for model, usage in (body.get("modelUsage") or {}).items():
            for key in ("inputTokens", "outputTokens", "cacheReadInputTokens", "cacheCreationInputTokens"):
                if isinstance((usage or {}).get(key), (int, float)):
                    tokens[key] = tokens.get(key, 0) + usage[key]
        cost_usd = body.get("total_cost_usd")
        # the result event's own `usage` (snake_case: input_tokens, output_tokens, cache_*_input_tokens)
        usage = {k: v for k, v in (body.get("usage") or {}).items() if k in USAGE_KEYS and isinstance(v, (int, float))}
        per_model_cost = {m: (u or {}).get("costUSD") for m, u in (body.get("modelUsage") or {}).items()
                          if isinstance((u or {}).get("costUSD"), (int, float))}
        rows.append({"job_id": job_id, "usd": cost_usd if isinstance(cost_usd, (int, float)) else None,
                     "models": sorted(body.get("modelUsage") or {}), "tokens": tokens, "usage": usage,
                     "costUSD by model": per_model_cost, "duration_ms": body.get("duration_ms"),
                     "is_error": body.get("is_error"), "num_turns": body.get("num_turns")})
    priced = [r for r in rows if r["usd"] is not None]
    total_tokens: dict = {}
    total_usage: dict = {}
    for r in rows:
        for key, value in r["tokens"].items():
            total_tokens[key] = total_tokens.get(key, 0) + value
        for key, value in r["usage"].items():
            total_usage[key] = total_usage.get(key, 0) + value
    return {"envelopes": len(rows), "priced": len(priced),
            "usd": round(sum(r["usd"] for r in priced), 4) if priced else None,
            "tokens": total_tokens, "usage": total_usage, "words": ("the CLI's own total_cost_usd, a list-price equivalent the founder's "
                                              "plan covers -- not billed" if priced else NOT_PRICED),
            "per_job": rows}


# ------------------------------------------------------------------------------- FR-4 / FR-6: the plan's limit

#: The words a CLI refusing for the plan's limit is read by (FR-4): a 429, *rate limit*, *usage limit*, *try again at*,
#: and Claude Code's own *hit your limit* / *limit reached*.
LIMIT_MARKERS = re.compile(r"\b429\b|rate[ _-]?limit|usage limit|try again at|hit your limit|limit reached",
                           re.IGNORECASE)
_EPOCH = re.compile(r"limit reached\|(\d{10})")
_RESETS = re.compile(r"resets\s+(?:at\s+)?(\d{1,2}(?::\d{2})?\s*[ap]m)(?:\s*\(([^)]+)\))?", re.IGNORECASE)
_TRY_AT = re.compile(r"try again at\s+([^.\n\"|]+)", re.IGNORECASE)


def limit_in(text: str) -> dict | None:
    """FR-4: `{"said", "at"}` when `text` names the plan's limit, else `None` -- `at` the time it names, as written
    (`3pm (Europe/London)`, an ISO time for an epoch, the words after *try again at*), or `None`."""
    if not text or not LIMIT_MARKERS.search(text):
        return None
    line = next((ln.strip() for ln in text.splitlines() if LIMIT_MARKERS.search(ln)), "")[:300]
    at = None
    if (m := _EPOCH.search(text)):
        at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(int(m.group(1))))
    elif (m := _RESETS.search(text)):
        at = m.group(1).replace(" ", "") + (f" ({m.group(2)})" if m.group(2) else "")
    elif (m := _TRY_AT.search(text)):
        at = m.group(1).strip()
    return {"said": line, "at": at}


def resume_epoch(at: str | None, *, now: float | None = None) -> float:
    """FR-6: when the runner may rerun -- the named time's next occurrence (an ISO time, or `3pm (Area/City)` in that
    zone, the machine's own when none is named), else `LIMIT_DEFAULT_WAIT_S` from now."""
    import datetime as dt                                         # noqa: PLC0415
    now = time.time() if now is None else now
    if at:
        try:
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", at):
                return dt.datetime.strptime(at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp()
            m = re.fullmatch(r"(\d{1,2})(?::(\d{2}))?([ap]m)(?:\s*\(([^)]+)\))?", at.strip(), re.IGNORECASE)
            if m:
                from zoneinfo import ZoneInfo                      # noqa: PLC0415
                zone = ZoneInfo(m.group(4)) if m.group(4) else None
                hour = int(m.group(1)) % 12 + (12 if m.group(3).lower() == "pm" else 0)
                current = dt.datetime.fromtimestamp(now, zone) if zone else dt.datetime.fromtimestamp(now).astimezone()
                target = current.replace(hour=hour, minute=int(m.group(2) or 0), second=0, microsecond=0)
                if target.timestamp() <= now:
                    target += dt.timedelta(days=1)
                return target.timestamp()
        except (ValueError, KeyError, OSError):
            pass
    return now + LIMIT_DEFAULT_WAIT_S


def limit_stop_in(markdown_text: str) -> str | None:
    """FR-6: the time a `backtest.md` says the run stopped on the plan's limit at, or `None` when it did not stop there
    (the empty string when it did and named no time)."""
    m = re.search(re.escape(LIMIT_FINDING) + r" ([^*\n]*)\*", markdown_text or "")
    if not m:
        return None
    at = m.group(1).strip()
    return "" if at in ("", "an unnamed time") else at


def plan_limit(bt: "Backtest", per_job: list[dict]) -> dict | None:
    """FR-4: what the runtime's launch log, every job the cloud did not complete, and every failed envelope in the
    runtime's home say about the plan's limit -- `None` when nothing does."""
    texts = []
    if bt.runtime is not None:
        texts.append(bt.runtime.log())
    texts += [str(r.get("error") or "") for r in per_job if r.get("status") != "COMPLETED"]
    jobs_dir = Path(bt.keel_home) / "jobs"
    for envelope in sorted(jobs_dir.glob("*/envelope.json")) if jobs_dir.is_dir() else []:
        try:
            body = json.loads(envelope.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if body.get("is_error"):
            texts.append(str(body.get("result") or ""))
    for text in texts:
        found = limit_in(text)
        if found:
            return found
    return None


# -------------------------------------------------------------------------------------------------- 3. camera

#: What one screen drew, read in the page: the kicker, the stem, the hint, every option as rendered (radios,
#: checkboxes, a list's rows -- a textarea's value where the row is editable), the chips, and the main column's text.
READ_JS = """() => {
  const one = (sel) => { const e = document.querySelector(sel); return e ? (e.innerText || e.value || "").trim() : ""; };
  const all = (sel) => Array.from(document.querySelectorAll(sel))
      .map((e) => (e.innerText || e.value || "").replace(/\\s+/g, " ").trim()).filter(Boolean);
  const rows = Array.from(document.querySelectorAll("li.listrow")).map((li) => {
      const ta = li.querySelector("textarea"); return ((ta && ta.value) || li.innerText || "").replace(/\\s+/g, " ").trim();
  }).filter(Boolean);
  const dialog = document.querySelector("[role=dialog]");
  const scope = dialog || document.querySelector("main") || document.body;
  return {kicker: one(".corridor__kicker, .iv-kicker, .guided-step__kicker"),
          question: one("[role=dialog] h2, h1.calib__q, h1.iv-q, .guided-step__question, h1"),
          hint: one(".calib__hint, .iv-tick, .iv-note, .ccard__sub"),
          options: all((dialog ? "[role=dialog] " : "") + "[role=radio], " + (dialog ? "[role=dialog] " : "") + "[role=checkbox]"),
          rows: rows, chips: all(".calib__chip, .iv-chips button"),
          text: (scope.innerText || "").slice(0, 6000)};
}"""


def _safe_slug(slug: str) -> str:
    return "".join(c if (c.isalnum() or c in "-_.") else "-" for c in slug).strip("-")[:70] or "screen"


@dataclass
class Camera:
    """FR-3's screenshots. `founder` is handed to every founder page object (`Corridor.camera`, `Interviews.camera`,
    `create_project(camera=)`); `respondent(person, page)` answers a callable for the one person a link it watches and
    None for everyone else. A shot never fails the journey: a failure is recorded on the shot."""
    run_dir: Path
    page: Any
    watched: dict                                  # link -> the person whose screens are taken
    founder_shots: list = field(default_factory=list)
    respondent_shots: dict = field(default_factory=dict)
    _taken: set = field(default_factory=set)

    @property
    def directory(self) -> Path:
        path = Path(self.run_dir) / SCREENS_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _take(self, page, name: str, slug: str) -> dict:
        shot: dict = {"file": f"{SCREENS_DIR}/{name}", "slug": slug, "url": None}
        try:
            try:
                page.evaluate("document.fonts.ready")
            except Exception:  # noqa: BLE001 - a font wait never blocks evidence
                pass
            shot["url"] = page.url
            shot.update(page.evaluate(READ_JS) or {})
            page.screenshot(path=str(self.directory / name), full_page=True)
        except Exception as missed:  # noqa: BLE001 - recorded, never raised: the camera is evidence, not a step
            shot["error"] = repr(missed)[:300]
        return shot

    def founder(self, slug: str) -> None:
        """One founder screen. The send screen is taken once (its first opening), not once a person."""
        if slug.startswith("send-"):
            if slug in self._taken:
                return
            self._taken.add(slug)
        n = len(self.founder_shots) + 1
        self.founder_shots.append({"n": n, **self._take(self.page, f"founder-{n:02d}-{_safe_slug(slug)}.png", slug)})

    def respondent(self, person, page) -> Callable[[str], None] | None:
        link = getattr(person, "link", None)
        if self.watched.get(link) != getattr(person, "person", None):
            return None
        shots = self.respondent_shots.setdefault(link, {"person": person.person, "shots": []})["shots"]
        word = LINK_SLUG.get(link, str(link).lower())

        def shoot(slug: str) -> None:
            n = len(shots) + 1
            shots.append({"n": n, **self._take(page, f"respondent-{word}-{n:02d}-{_safe_slug(slug)}.png", slug)})
        return shoot


def watched_people(people: list) -> dict:
    """One person a link whose walk serves every screen: on the primary link the first who passed the gate with a
    story typed and no chip (so the gate, every item and the reveal are drawn), else the first; on the decision-maker's
    link the first."""
    out: dict = {}
    for p in people:
        if p.link in out:
            continue
        if p.link == "PRIMARY" and not (p.recency and (p.story or "").strip() and not p.anchor_chip):
            continue
        out[p.link] = p.person
    for p in people:
        out.setdefault(p.link, p.person)
    return out


# --------------------------------------------------------------------------------------------- the run's seam

@dataclass
class Backtest:
    """What `corpus_scenario.run(..., backtest=...)` calls: `sign_in`, `camera`, `lap` (each leg's wall time), `after`
    (the export) and `finish` (the transcript, whatever happened)."""
    run_dir: Path
    stack: Any
    patience: float = PATIENCE
    contract_dir: str = CONTRACT_DIR
    started: float = field(default_factory=time.monotonic)
    legs: list = field(default_factory=list)
    founder_identity: Any = None
    me_at_signup: dict = field(default_factory=dict)
    export: dict | None = None
    cam: Camera | None = None
    themes_settled: dict | None = None
    #: Spec 066 FR-1: which door the founder came through -- `keel` (spec 062) or `host` (the founder's own CLI).
    door: str = DEFAULT_DOOR
    host: str | None = None
    #: Spec 066 FR-2: the runtime the back-test started on the host door, and what the door read.
    runtime: HostRuntime | None = None
    door_facts: dict = field(default_factory=dict)
    jobs_on_the_host: dict | None = None

    def __post_init__(self):
        if self.door == "host":
            from harness import agent_host                         # noqa: PLC0415
            self.host = self.host or "claude"
            # FR-4: the host's own job wait, or the back-test's where that is already longer
            self.patience = max(self.patience, agent_host.host_type(self.host).keels_ai_job_wait_s / 60.0)

    @property
    def keel_home(self) -> Path:
        return Path(self.run_dir) / KEEL_HOME_DIR

    # ---------------------------------------------------------------------------------------- 2. the founder

    def identity(self):
        """The back-test founder on the local stub: registered now (`POST /identities`), or -- registered earlier on
        this same stub process -- the same one again."""
        from stack import remote                                  # noqa: PLC0415
        from stack.auth import StubFounder                        # noqa: PLC0415
        label = f"back-test · {time.strftime('%Y-%m-%d', time.gmtime())}"
        try:
            return remote.register_cell_identity(self.stack, label, name=IDENTITY_NAME, id=IDENTITY_ID,
                                                  email=IDENTITY_EMAIL)
        except remote.RegistryRefused as refused:
            if getattr(refused, "status", None) != 409:
                raise
            from stack.stub_oidc.registry import SUB_PREFIX       # noqa: PLC0415
            return StubFounder(id=IDENTITY_ID, sub=f"{SUB_PREFIX}{IDENTITY_ID}", email=IDENTITY_EMAIL,
                               name=IDENTITY_NAME)

    def sign_in(self, j):
        if self.door == "host":
            return self.sign_in_through_the_host(j)
        return self.sign_up_on_keels_ai(j)

    def sign_up_on_keels_ai(self, j):
        """FR-2: signed up through keel-web's /signup as the back-test founder; held before anything is asked of Keel's
        AI -- keel-cloud said *Keel's AI is ON* at boot, `/v2/me` reads `aiPath: KEEL` and the founder's email, and that
        email is outside `fake-for`."""
        from harness.browser import Auth, Landing                 # noqa: PLC0415
        from stack.config import REPO_ROOT                        # noqa: PLC0415
        founder = self.identity()
        cloud_log = REPO_ROOT / "runs" / ".stack" / "cloud.log"
        listed = fake_for()
        with j.recorder.step("back-test (spec 062 FR-2): keel-cloud booted with Keel's AI on, and the founder is outside "
                             "fake-for", party="stack", kind="assert") as h:
            h.record_assert({"cloud log": KEEL_AI_ON, "fake-for": f"does not match {IDENTITY_EMAIL}"},
                            {"keel ai on": keel_ai_on(cloud_log), "fake-for": listed,
                             "in fake-for": in_fake_for(founder.email, listed)})
            assert keel_ai_on(cloud_log), (f"keel-cloud's log ({cloud_log}) never said {KEEL_AI_ON!r}: the key did not "
                                           "reach it, so every job would fail KEEL_AI_DISABLED")
            assert not in_fake_for(founder.email, listed), (founder.email, listed)
        Auth(j.page, j.recorder, j.web_base).sign_up(founder)
        Landing(j.page, j.recorder, j.web_base).visit()
        with j.recorder.step("back-test (spec 062 FR-2): the account is on Keel's AI -- /signup made it, aiPath KEEL, "
                             "the grant on the wire", party="founder", kind="assert") as h:
            me = j.get("/v2/me") or {}
            self.me_at_signup = {k: me.get(k) for k in ("aiPath", "email", "name", "creditsAvailable")}
            h.record_assert({"aiPath": "KEEL", "email": IDENTITY_EMAIL}, self.me_at_signup)
            assert me.get("aiPath") == "KEEL", me
            assert (me.get("email") or "").lower() == IDENTITY_EMAIL, me
        self.founder_identity = founder
        return founder

    # ------------------------------------------------------------------------------ 2b. the host door (spec 066)

    def start_runtime(self, stack) -> HostRuntime:
        """FR-2: keel-connect-skill's runtime from the sibling checkout `stack.toml` names, on this stack's cloud, its
        home and launch log inside the run -- with the founder's own Claude Code login."""
        checkout = Path(stack.keel_connect_skill)
        self.runtime = HostRuntime(keel_home=self.keel_home,
                                   argv=runtime_argv(stack.cloud_base_url, self.keel_home, host_name=self.host),
                                   cwd=checkout, env=runtime_env(pythonpath=str(checkout)))
        self.runtime.start()
        return self.runtime

    def sign_in_through_the_host(self, j):
        """Spec 066 FR-3: the runtime started first (keel-cloud decides the account's AI from the door it is created
        through), its code read off the launch log, the back-test founder signed in with that code and the device
        approved at `/connect` -- S-012's two steps (`preludes.sign_in_with_the_code`, `preludes.approve_at_connect`)
        -- then held before anything is asked of Keel: `/v2/me` reads `aiPath` `OWN`, and the heartbeat is connected."""
        from evals import preludes                                 # noqa: PLC0415
        from harness.browser import Auth, Landing                  # noqa: PLC0415
        from harness.evidence import write_block                   # noqa: PLC0415
        founder = self.identity()
        ready = host_readiness(self.host)
        self.door_facts = {"door": "host", "host": self.host, "words": HOST_DOOR_WORDS,
                           "cli": {k: ready.get(k) for k in ("version", "loggedIn", "authMethod",
                                                             "oauth token in the shell", "CLAUDE_CONFIG_DIR")},
                           "model": ("per job: keel-cloud's routing table for claude (the job's `model.claude` and "
                                     "`effort.claude`), else the CLI's default -- the runtime has no session-wide pin"),
                           "keel-connect-skill": connect_skill_versions(Path(j.stack.keel_connect_skill)),
                           "runtime": {"home": f"{KEEL_HOME_DIR}/", "log": f"{KEEL_HOME_DIR}/{RUNTIME_LOG}"}}
        write_block(Path(self.run_dir), "backtest door", self.door_facts)
        with j.recorder.step("back-test (spec 066 FR-2): the runtime is started from keel-connect-skill's checkout on "
                             "the founder's own Claude Code, and its launch log prints the device code",
                             party="stack", kind="protocol") as h:
            runtime = self.start_runtime(j.stack)
            code, uri = runtime.wait_for_code(USER_CODE_WAIT_S)
            beat = runtime.heartbeat()
            h.record_wire({"argv": runtime.argv, "cwd": str(runtime.cwd), "log": str(runtime.log_path)},
                          {"pid": runtime.proc.pid, "user_code": code, "verification_uri": uri,
                           "heartbeat": beat, "log": runtime.log()[:2000],
                           "cli": self.door_facts["cli"]})
        from harness import agent_host                             # noqa: PLC0415
        with j.recorder.step("back-test (spec 066 FR-3): a runtime is really there, waiting -- the heartbeat says "
                             "`awaiting_approval` and the launch log carries the code and this stack's /connect",
                             party="stack", kind="assert") as h:
            h.record_assert({"state": agent_host.STATE_AWAITING_APPROVAL, "KEEL_USER_CODE=": "XXXX-XXXX",
                             "KEEL_VERIFICATION_URI=": f"{j.web_base}/connect"},
                            {"heartbeat": beat, "user_code": code, "verification_uri": uri,
                             "alive": runtime.alive()})
            assert ready.get("refusal") is None, ready.get("refusal")
            assert agent_host.looks_like_a_user_code(code), (
                f"no `KEEL_USER_CODE=` in {runtime.log_path} within {USER_CODE_WAIT_S:.0f} s: {runtime.log()[:600]!r}")
            assert uri and uri.startswith(f"{j.web_base}/connect"), uri
            assert (beat or {}).get("state") == agent_host.STATE_AWAITING_APPROVAL, beat
        auth = Auth(j.page, j.recorder, j.web_base)
        preludes.sign_in_with_the_code(auth, j.recorder, founder, code)
        preludes.approve_at_connect(j.page, j.recorder, code, uri, label="back-test (spec 066 FR-3)", timeout_s=60)
        Landing(j.page, j.recorder, j.web_base).visit()
        preludes.own_ai_door(j.page, j.recorder, j.stack, j.get, through_the_code_story=True)
        with j.recorder.step("back-test (spec 066 FR-3): the account is on the founder's own AI -- aiPath OWN, the "
                             "back-test founder -- and the runtime's heartbeat is connected, before anything is "
                             "asked of Keel", party="founder", kind="assert") as h:
            me = j.get("/v2/me") or {}
            beat = runtime.wait_for_connected(CONNECTED_WAIT_S)
            self.me_at_signup = {k: me.get(k) for k in ("aiPath", "email", "name", "creditsAvailable")}
            h.record_assert({"aiPath": "OWN", "email": IDENTITY_EMAIL, "heartbeat": STATE_CONNECTED},
                            {**self.me_at_signup, "heartbeat": beat, "alive": runtime.alive()})
            said = host_door_refusal(me)
            assert said is None, said
            assert (beat or {}).get("state") == STATE_CONNECTED, (
                f"the runtime's heartbeat never said {STATE_CONNECTED!r} after the approval: {beat}")
        self.founder_identity = founder
        return founder

    def stop_runtime(self) -> dict | None:
        """FR-5: the runtime stopped, passed or not (idempotent); `None` on the KEEL door."""
        if self.runtime is None:
            return None
        try:
            return self.runtime.stop()
        except Exception as missed:  # noqa: BLE001 - recorded, never raised: teardown must not mask the run
            return {"error": repr(missed)[:300], "alive after": self.runtime.alive()}

    def check_the_host_answered(self, j) -> None:
        """FR-3: every job that landed was answered by the host -- `execution.host` is `claude` and its model is named
        (keel-cloud's interactions, read as `keel_host.jobs_with_their_execution` reads them)."""
        from harness import keel_host                              # noqa: PLC0415
        with j.recorder.step(f"back-test (spec 066 FR-3): every job was answered by the founder's own CLI -- "
                             f"execution.host {self.host}, its model named", party="stack", kind="assert") as h:
            interactions = j.get(f"/v2/inference-interactions?project_id={j.project_id}") or []
            per_job = keel_host.jobs_with_their_execution(j.get, interactions)
            self.jobs_on_the_host = host_door_jobs(per_job, self.host)
            h.record_assert({"host": self.host, "model": "named", "bad": []}, self.jobs_on_the_host)
            assert self.jobs_on_the_host["completed"] > 0, self.jobs_on_the_host
            assert not self.jobs_on_the_host["bad"], self.jobs_on_the_host["bad"]

    def pass_welcome(self, j, *, timeout_s: float = 30.0) -> dict:
        """The guide's welcome over the project's first screen, passed by with Skip (the golden journeys judge it in
        `leg_welcome`; here it is not the subject). Waited for up to `timeout_s`, not `MarketStep.start`'s 5 s: on a
        fresh local stack vite compiles the sheet's lazy chunk on its first request, and the dry run of 2026-10-22 saw
        it land after the 5 s pass and cover the context step's Save."""
        from harness import vectors_screens as vs_screens          # noqa: PLC0415
        sheet = vs_screens.GuideWelcome(j.page, j.recorder, j.web_base)
        if not sheet.present(timeout_s=timeout_s):
            return {"shown": False}
        return {"shown": True, **sheet.skip()}

    def camera(self, j) -> Camera:
        """The camera -- and, set here because it is the back-test's alone, the retries a founder would press
        (`Journey.retries`, `RETRIES`): a refused model result is a finding, recorded, and the walk goes on."""
        j.retries = RETRIES
        self.cam = Camera(run_dir=self.run_dir, page=j.page, watched=watched_people(j.people))
        return self.cam

    def lap(self, name: str) -> None:
        """FR-4.5: the wall time since the last lap (or the start), named for the leg that just ended."""
        now = time.monotonic()
        since = self.legs[-1]["_at"] if self.legs else self.started
        self.legs.append({"leg": name, "seconds": round(now - since, 1), "_at": now})

    # ---------------------------------------------------------------------------------------------- 4. export

    def after(self, j) -> None:
        """FR-3: the 060/061 export at the last answer into `runs/<run>/export/`, names kept, no verdict gate. A
        refusal (a survivor of the withholding) is recorded, never raised: the transcript is the run's product.

        First the THEMES jobs are given time to land (062 follow-up, 2026-10-22): on the run of record (08-fresco) two
        were still QUEUED / RUNNING when the transcript was written, so the insights carried raw quotes and no
        grouping, which is the very classification the back-test judges. Up to `THEMES_WAIT_S`, never asserted."""
        from evals import sample_export                           # noqa: PLC0415
        self.themes_settled = _safe(lambda: themes_settle(j), None)
        if self.door == "host":
            self.check_the_host_answered(j)
        try:
            result = sample_export.export_sample(j, Path(self.run_dir) / EXPORT_DIR, run_dir=self.run_dir, gated=False)
            self.export = {k: result[k] for k in ("card", "size", "dir", "people") if k in result}
            self.export["files"] = len(result["manifest"]["files"])
        except sample_export.SampleRefused as refused:
            self.export = {"refused": refused.reasons}

    # ------------------------------------------------------------------------------------------ 5. transcript

    def finish(self, j, *, passed: bool, failed_step: Any = None) -> dict:
        """FR-4: `backtest.json` and `backtest.md`, from whatever the journey reached. Never raises. On the host door
        (spec 066 FR-5) the runtime is stopped first, and its teardown is part of the record."""
        teardown = self.stop_runtime()
        record: dict = {"spec": "062", "run": Path(self.run_dir).name, "passed": passed,
                        "failed_step": _step_name(failed_step),
                        "wall_s": round(time.monotonic() - self.started, 1),
                        "legs": [{k: v for k, v in leg.items() if k != "_at"} for leg in self.legs]}
        try:
            record.update(transcript(j, self))
        except Exception as broke:  # noqa: BLE001 - the transcript is evidence; it must never mask the run
            record["transcript_error"] = repr(broke)[:500]
        if self.door == "host":
            record["spec"] = "062+066"
            try:
                record.update(host_door_record(j, self, passed=passed, teardown=teardown))
            except Exception as broke:  # noqa: BLE001 - as the transcript: evidence never masks the run
                record["runtime"] = teardown
                record["host_door_error"] = repr(broke)[:500]
        try:
            (Path(self.run_dir) / RECORD).write_text(json.dumps(record, indent=2, ensure_ascii=False, default=str)
                                                     + "\n", encoding="utf-8")
            (Path(self.run_dir) / MARKDOWN).write_text(markdown(record), encoding="utf-8")
        except Exception as broke:  # noqa: BLE001
            (Path(self.run_dir) / "backtest_error.txt").write_text(repr(broke), encoding="utf-8")
        return record


#: keel-cloud `InteractionStatus` values of a job still to land (as `corpus_scenario.OPEN_STATUSES`).
_OPEN = {"PENDING", "CLAIMED", "RUNNING", "QUEUED", "DRAFT", "NEEDS_INPUT"}
THEMES_WAIT_S = 150


def themes_settle(j, *, timeout_s: float = THEMES_WAIT_S) -> dict:
    """Waits until no THEMES interaction of the project is open, or the timeout; returns what it saw (recorded in the
    transcript's `cost`.`not settled` either way). A founder read of the overview first, so keel-cloud 104's
    themes-on-return starts whatever is still due."""
    _safe(lambda: j.get(j.project("/overview")), None)
    deadline = time.monotonic() + timeout_s
    waited = 0.0
    while True:
        themes = [i for i in (j.get(f"/v2/inference-interactions?project_id={j.project_id}") or [])
                  if i.get("screen") == "THEMES"]
        open_ = [t.get("status") for t in themes if t.get("status") in _OPEN]
        # spec 064 FR-8 (keel-cloud 119 FR-4): and no insight still GROUPING
        standings = _safe(lambda: j.get(j.project("/standings")), {}) or {}
        grouping = [i.get("dimension") for i in standings.get("insights") or [] if i.get("state") == "GROUPING"]
        if (not open_ and not grouping) or time.monotonic() > deadline:
            return {"themes": len(themes), "open": open_, "grouping": grouping,
                    "notAsked": [n.get("dimension") for n in standings.get("notAsked") or []],
                    "waited_s": round(waited, 1)}
        time.sleep(2)
        waited += 2


def _step_name(step: Any) -> str | None:
    if step is None:
        return None
    return getattr(step, "name", None) or str(step)


def _sha(path: Path | None) -> str | None:
    if path is None or not Path(path).is_dir():
        return None
    try:
        return subprocess.run(["git", "-C", str(path), "rev-parse", "--short", "HEAD"], capture_output=True,
                              encoding="utf-8", timeout=10).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def _safe(read: Callable[[], Any], default: Any = None) -> Any:
    try:
        return read()
    except Exception as missed:  # noqa: BLE001 - one section's miss never loses the others
        return {"error": repr(missed)[:300]} if default is None else default


# --------------------------------------------------------------------------------- FR-4.1 the founder's screens

def _vector_of(key: str) -> str:
    return key.split(".", 1)[0].upper()


def founder_answer(j, slug: str) -> Any:
    """The founder's answer from the file for one screen slug (what was typed or picked there)."""
    f = j.founder
    answers = {a.dimension: a for v in ("PROBLEM", "SOLUTION", "COMMERCIAL") for a in (f.calibration.get(v) or [])}
    if slug == "name":
        return f.project_name
    if slug == "market":
        return {"country": f.country, "region": f.region}
    if slug == "context":
        return {**f.context_fields, "recall window": f.window.as_wire()}
    if slug in ("context-card",):
        return "Yes, that's it"
    if slug == "problem-seed":
        return f.problem_seed
    if slug == "problem-card":
        return "Yes, that's the problem"
    if slug == "solution-seed":
        return f.solution_seed
    if slug == "solution-card":
        return "Looks right"
    if slug == "idea":
        return {"what (typed)": f.idea_name, "how / belief": "saved as Keel drafted them"}
    if slug == "persona":
        return f.decider
    if slug in ("persona-who-answers", "ready-word", "ready-pilot"):
        return "Continue"
    if slug == "ready-interviewer":
        return "Lock and record the interviewer (the face Keel preselects)"
    if slug == "send-format":
        return "Text only"
    if slug == "send-who":
        return "Someone I know: each person by name"
    kind, _, key = slug.partition("-")
    answer = answers.get(key)
    if answer is None:
        return None
    if answer.unsure:
        return "left out of the study (the founder is unsure)"
    if kind == "q":
        return {k: v for k, v in answer.as_wire().items() if k != "dimension"}
    if kind == "answer":
        return answer.text
    if kind == "check":
        return "saved as Keel drafted it"
    if kind == "choose":
        listed = answer.listed or {}
        index = listed.get("pickedIndex") or 0
        items = listed.get("items") or []
        return {"pickedIndex": index, "the file's item": (items[index] or {}).get("label") if index < len(items) else None,
                "picked on screen": "the served list's item at that index (or its last)"}
    return None


def read_back(j, slug: str, wire: dict) -> Any:
    """What Keel read back for one screen: the *Keel understands* card, the statement, the idea's lines, the belief
    sentence and the *Keel will test* box, the frame -- from the wire and what the screen drew."""
    if slug in ("context", "context-card"):
        return {"understands": (wire.get("context") or {}).get("understands")}
    if slug in ("problem-seed", "problem-card"):
        return {"statement": (wire.get("review/PROBLEM") or {}).get("statement")}
    if slug in ("solution-seed", "solution-card", "idea"):
        idea = wire.get("idea") or {}
        return {k: idea.get(k) for k in ("what", "how", "belief", "shortName", "approved")}
    if slug in ("persona", "persona-who-answers"):
        persona = wire.get("persona") or {}
        return {"respondentTypes": [{k: t.get(k) for k in ("label", "commercialLink")}
                                    for t in persona.get("respondentTypes") or []], "decider": persona.get("decider"),
                "deciderTitle": persona.get("deciderTitle")}
    _, _, key = slug.partition("-")
    if "." not in key:
        return None
    rows = {r.get("dimension"): r for r in (wire.get(f"review/{_vector_of(key)}") or {}).get("rows") or []}
    row = rows.get(key) or {}
    seen = (j.framing or {}).get(key) or []
    screen = {"q": "single", "answer": "answer", "check": "check", "choose": "choose"}.get(slug.split("-", 1)[0])
    drawn = next((s for s in seen if s.get("screen") == screen), {}) if screen else {}
    out = {"belief": row.get("belief"), "left out": bool(row.get("leftOut") or row.get("unsure")) or None,
           "frame": (drawn.get("frame") or {}).get("progress")}
    if drawn.get("belief"):
        out["belief line on screen"] = drawn.get("belief")
    # spec 064 FR-9 (keel-web 094): the chain's equation line and the price's locked words, as the founder saw them
    for name, field_ in (("equation", "equation"), ("per", "per"), ("locked words", "locked")):
        if drawn.get(field_):
            out[name] = drawn.get(field_)
    test = drawn.get("test_after") or drawn.get("test")
    if test:
        out["keel will test"] = test.get("belief")
        out["bar"] = test.get("bar")
    return {k: v for k, v in out.items() if v not in (None, "")}


def _wire(j) -> dict:
    reads = {}
    for key in ("context", "review/PROBLEM", "review/SOLUTION", "review/COMMERCIAL", "idea", "persona", "plan",
                "standings", "invitations", "overview"):
        reads[key] = _safe(lambda k=key: j.get(j.project(f"/{k}")), {})
    return reads


def founder_screens(j, cam: Camera | None, wire: dict) -> list[dict]:
    out = []
    for shot in (cam.founder_shots if cam else []):
        slug = shot.get("slug") or ""
        out.append({"n": shot["n"], "screen": slug, "file": shot.get("file"), "kicker": shot.get("kicker"),
                    "question": shot.get("question"), "hint": shot.get("hint"),
                    "options": shot.get("options") or [], "rows": shot.get("rows") or [],
                    "chips": shot.get("chips") or [], "answer": _safe(lambda s=slug: founder_answer(j, s)),
                    "keel read back": _safe(lambda s=slug: read_back(j, s, wire)),
                    **({"camera error": shot["error"]} if shot.get("error") else {})})
    return out


# -------------------------------------------------------------------------------- FR-4.2 the respondent questions

def _labels(rows: list | None, key: str = "label") -> list:
    return [(r or {}).get(key) for r in rows or []]


#: Spec 063 FR-3a: what an item carries beyond the six above, kept when served (ids never: `plan`'s options go as
#: labels) so the gallery's interview.json can draw it -- the item's own kicker, the number and money controls, and
#: spec 115's value box, plan and what-you-get.
SERVED_EXTRAS = ("kicker", "advantagesPrompt", "scale", "numeric", "costTotal", "valueBox", "whatYouGet")


def served_items(interview: dict) -> dict:
    """The interview as the respondent page fetched it: the idea, the gate, every item in order (wording, control,
    every option label, the escape) and the reveal. Spec 063: and an item's `SERVED_EXTRAS` and `plan` when served."""
    parts = []
    for part in interview.get("parts") or []:
        items = []
        for item in part.get("items") or []:
            row = {"dimension": item.get("dimension"), "question": item.get("question"),
                   "control": item.get("control"), "hint": item.get("hint"),
                   "options": _labels(item.get("options")), "advantages": _labels(item.get("advantages")),
                   "escape": (item.get("escape") or {}).get("label")}
            row.update({k: item[k] for k in SERVED_EXTRAS if item.get(k) not in (None, "", [], {})})
            if item.get("plan"):
                row["plan"] = {"question": item["plan"].get("question"),
                               "options": _labels(item["plan"].get("options"))}
            items.append(row)
        parts.append({"part": part.get("part"), "kicker": part.get("kicker"), "items": items})
    gate = interview.get("gate") or None
    return {"kind": interview.get("kind"), "occasion": interview.get("occasion"),
            "idea": interview.get("idea"), "gate": gate, "parts": parts, "reveal": interview.get("reveal")}


def respondent_questions(j, cam: Camera | None) -> dict:
    out = {}
    for link, person in (cam.watched if cam else {}).items():
        shots = ((cam.respondent_shots.get(link) or {}).get("shots") or []) if cam else []
        out[link] = {"person": person, "served": served_items((j.interviews or {}).get(person) or {}),
                     "drawn": ((j.walked or {}).get(person) or {}).get("screens") or [],
                     "screens": [s.get("file") for s in shots]}
    return out


# ---------------------------------------------------------------------------------------- spec 067 FR-8: spoken

def spoken_guard(j) -> dict:
    """Spec 067 FR-8 (keel-cloud 128 FR-10): every served item of every link, as the page fetched it, read back through
    the spoken-form rules (`instructions.spoken.item_faults`, S1-S10) with its stem's length -- a stem past 20 words, or
    any fault, is a red line in the transcript, never a note. One row a distinct item a link (people share a link's
    words). Recorded, never asserted: the back-test is a reading."""
    from instructions import cloud_corpus                              # noqa: PLC0415
    from instructions import spoken as spoken_mod                      # noqa: PLC0415
    entry = j.entry
    registry = getattr(j, "registry", None) or getattr(entry, "registry", None)
    rows, seen = [], set()
    for person, interview in (getattr(j, "interviews", None) or {}).items():
        for part in (interview or {}).get("parts") or []:
            for item in part.get("items") or []:
                said = item.get("spoken") or {}
                key = (interview.get("kind"), item.get("dimension"), item.get("question"), said.get("optionsLine"))
                if key in seen:
                    continue
                seen.add(key)
                composed = cloud_corpus.ComposedItem(
                    entry=entry.id, key=item.get("dimension"), part=part.get("part"), question=item.get("question") or "",
                    options=tuple(o.get("label") for o in item.get("options") or []),
                    escape=(item.get("escape") or {}).get("label"), anchor=said.get("anchor"),
                    stem=said.get("stem") or "", count_line=said.get("countLine"),
                    options_line=said.get("optionsLine") or "", escape_line=said.get("escapeLine"),
                    transform=said.get("transform") or "none")
                try:
                    faults = spoken_mod.item_faults(composed, registry, entry)
                except Exception as broke:  # noqa: BLE001 - a reading: one unreadable item never hides the rest
                    faults = [f"unread: {broke!r}"[:200]]
                stem_words = spoken_mod.words(composed.stem)
                rows.append({"link": interview.get("kind"), "person": person, "dimension": item.get("dimension"),
                             "stem": composed.stem, "stem_words": stem_words, "faults": faults,
                             "red": stem_words > spoken_mod.STEM_MAX_WORDS or bool(faults)})
    return {"items": len(rows), "clean": sum(1 for r in rows if not r["red"]),
            "longest_stem": max((r["stem_words"] for r in rows), default=0),
            "red": [r for r in rows if r["red"]], "rows": rows}


# ----------------------------------------------------------------------------- spec 067 FR-7: the changed screens

#: keel-cloud 128 FR-5 / FR-21 (keel-web 106 FR-2): words a consumer link never says.
CONSUMER_BANNED = ("decision-makers", "decision-maker", "the payer", "per person", "per company", "your team",
                   "new money")
#: keel-cloud 128 FR-8 (`BriefFacts.BAR_LINES`): the lines whose amber is never said *People disagree*.
BAR_LINES = ("solution.compatibility", "solution.relative_advantage", "solution.adoption_friction",
             "commercial.purchase_friction", "commercial.commitment")


def _closed_price(raw) -> bool:
    """An entry's price pick that closes the item: an escape chip, or *I wouldn't pay for this* (128 FR-21)."""
    if isinstance(raw, dict):
        return bool(raw.get("chip"))
    codes = raw if isinstance(raw, list) else [raw]
    return any(str(c).endswith("would_not_pay") for c in codes)


def changed_screens(j, standings: dict | None = None) -> dict:
    """Spec 067 FR-7 (judgement call 6): what the wire and today's screens already show of keel-cloud 128's changed
    screens, read on every back-test and recorded as findings -- the consumer vocabulary on a consumer study's served
    items (128 FR-5), a plan screen drawn after a closed price (128 FR-21; keel-web 106 FR-9 skips it), and *People
    disagree* on a bar line in the brief's cards (128 FR-8). keel-web 106's own screens (the occasion field, the seed
    name, the needs-input screen, the market line, the friction row at phone width, the Insights footers) wait for its
    build. Nothing here is asserted."""
    entry = j.entry
    out: dict = {"consumer_words": [], "plan_after_closed_price": [], "people_disagree_on_a_bar_line": []}
    if not entry.b2b():
        seen = set()
        for person, interview in (getattr(j, "interviews", None) or {}).items():
            if (interview or {}).get("kind") != "FULL":
                continue
            for part in interview.get("parts") or []:
                for item in part.get("items") or []:
                    texts = [item.get("question"), item.get("whatYouGet"), (item.get("valueBox") or {}).get("label"),
                             (item.get("plan") or {}).get("question")]
                    texts += [o.get("label") for o in item.get("options") or []]
                    for text in (t for t in texts if t):
                        for word in CONSUMER_BANNED:
                            if word in text.lower() and (item.get("dimension"), word, text) not in seen:
                                seen.add((item.get("dimension"), word, text))
                                out["consumer_words"].append({"dimension": item.get("dimension"), "word": word,
                                                              "said": text})
    for person, walked in (getattr(j, "walked", None) or {}).items():
        mine = entry.person(person)
        if mine is None or not _closed_price((mine.picks or {}).get("commercial.price")):
            continue
        for screen in (walked or {}).get("screens") or []:
            if screen.get("dimension") == "commercial.price" and screen.get("plan"):
                out["plan_after_closed_price"].append({"person": person, "plan": screen.get("plan")})
    facts = (standings or {}).get("facts") or {}
    for card in facts.get("cards") or []:
        if card.get("key") in BAR_LINES and str(card.get("statusWords") or "").startswith("People disagree"):
            out["people_disagree_on_a_bar_line"].append({k: card.get(k) for k in ("key", "number", "statusWords")})
    # spec 068 FR-4: keel-web 106's own screens, as the walk read them (`Journey.changed`)
    read = getattr(j, "changed", None) or {}
    out["web_106"] = {k: read[k] for k in ("occasion_field", "context_wire", "idea_name", "needs_input",
                                           "market_other", "friction_row", "consumer_words", "gate_no") if k in read}
    # spec 069 FR-1 / FR-2: keel-cloud 130's served words beside the harness's mirror, and contract 37's replaced rows
    out["cloud_130"] = cloud_130(j, standings)
    # spec 070 FR-2: keel-cloud 131's served words beside the harness's mirror, and the refused lock's edits (FR-1)
    out["cloud_131"] = cloud_131(j)
    return out


def _tested_item(listed: dict | None) -> dict:
    items = (listed or {}).get("items") or []
    at = (listed or {}).get("pickedIndex") or 0
    return items[at] if 0 <= at < len(items) else (items[0] if items else {})


def _reveal_text(interview: dict) -> str | None:
    """`VectorCorridor.revealText`, as the page was served it: the idea's lines joined (the reveal, else the idea)."""
    lines = (interview or {}).get("reveal") or (interview or {}).get("idea") or {}
    said = [str(lines.get(k) or "").strip() for k in ("what", "how", "howDecider", "belief")]
    return " ".join(t for t in said if t) or None


def cloud_130(j, standings: dict | None = None) -> dict:
    """Spec 069 FR-1 (keel-cloud 130 FR-11, FR-10, FR-6, FR-2): on a back-test, the served Adoption statement and
    Commitment stem beside the harness's mirror of 130's composer (`vs.adoption_statement`, `vs.commitment_stem`, from
    the lock's tested face and step, the served idea name and reveal), a gate that asks the job, and the brief's
    Prevalence and Frequency lines beside the served gate's clause and the window's unit -- each difference a finding,
    never a stop. FR-2: the Check screen's replaced rows (contract 37), as the walk read them. Empty keys left out."""
    from harness import vectors_script as vs                       # noqa: PLC0415
    from instructions import brief_facts as bf                     # noqa: PLC0415
    entry = j.entry
    out: dict = {"stems": [], "gate_asks_the_job": [], "brief_lines": [], "replaced": []}
    project = getattr(j, "project", None)
    plan = _safe(lambda: j.get(project("/plan")), {}) if callable(getattr(j, "get", None)) and callable(project) \
        else {}
    lists = (plan or {}).get("lists") or {}
    tested = _tested_item(lists.get("solution.adoption_friction"))
    steps = ((lists.get("commercial.commitment") or {}).get("items") or [])
    step = (steps[0] or {}).get("label") if steps else None
    gates = set()
    for person, interview in (getattr(j, "interviews", None) or {}).items():
        items = {i.get("dimension"): i for part in (interview or {}).get("parts") or [] for i in part.get("items") or []}
        name = vs.served_idea_name(interview or {})
        adoption = items.get("solution.adoption_friction")
        want = vs.adoption_statement(tested.get("asked") or tested.get("label"), name) if adoption else None
        if adoption and want and adoption.get("question") != want:
            out["stems"].append({"person": person, "dimension": "solution.adoption_friction", "rule": "130 FR-11",
                                 "served": adoption.get("question"), "mirror": want})
        commitment = items.get("commercial.commitment")
        want = vs.commitment_stem(step, name, _reveal_text(interview)) if commitment and step else None
        if commitment and want and commitment.get("question") != want:
            out["stems"].append({"person": person, "dimension": "commercial.commitment", "rule": "130 FR-10",
                                 "served": commitment.get("question"), "mirror": want})
        gate = ((interview or {}).get("gate") or {}).get("question")
        if gate:
            gates.add(gate)
    seen = set()
    out["stems"] = [r for r in out["stems"] if (r["dimension"], r["served"]) not in seen
                    and not seen.add((r["dimension"], r["served"]))]
    window = _safe(lambda: entry.window())
    for gate in sorted(gates):
        if _safe(lambda g=gate: vs.gate_asks_the_job(entry, g), False):
            out["gate_asks_the_job"].append({"gate": gate, "rule": "130 FR-6",
                                             "circumstance before its negative": vs.without_negative_clause(
                                                 (entry.context or {}).get("circumstance"))})
    cards = {c.get("key"): c for c in ((standings or {}).get("facts") or {}).get("cards") or []}
    if window is not None and len(gates) == 1:
        clause = bf.gate_clause_of_them(next(iter(gates)), window)
        prevalence, frequency = cards.get("problem.prevalence") or {}, cards.get("problem.frequency") or {}
        if clause and prevalence.get("line") and prevalence["line"] != bf.prevalence_line(clause, window.words()):
            out["brief_lines"].append({"key": "problem.prevalence", "rule": "130 FR-6", "line": prevalence["line"],
                                       "mirror": bf.prevalence_line(clause, window.words())})
        line = str(frequency.get("line") or "")
        if clause and " · " in line and line != bf.frequency_line(clause, window):
            out["brief_lines"].append({"key": "problem.frequency", "rule": "130 FR-6", "line": line,
                                       "mirror": bf.frequency_line(clause, window)})
        elif " · " in line and not line.startswith(f"the middle answer · {window.plural} they "):
            out["brief_lines"].append({"key": "problem.frequency", "rule": "130 FR-2", "line": line,
                                       "mirror": f"the middle answer · {window.plural} they ..."})
    out["replaced"] = list((getattr(j, "changed", None) or {}).get("replaced") or [])
    findings = getattr(j, "findings", None)
    if isinstance(findings, list):
        for row in out["stems"]:
            findings.append({"what": f"{row['dimension']}: the served stem is not keel-cloud {row['rule']}'s "
                                     "composition as the harness mirrors it (spec 069 FR-1)", "served": row})
        for row in out["gate_asks_the_job"]:
            findings.append({"what": "the gate asks the job, not the occasion's event (keel-cloud 130 FR-6)",
                             "served": row})
        for row in out["brief_lines"]:
            findings.append({"what": f"{row['key']}: the brief's line is not the served gate's ({row['rule']})",
                             "served": row})
    return {k: v for k, v in out.items() if v}


_EACH_AFTER_PER = re.compile(r"(?i)\bper [a-z][a-z' -]{0,30}?, each\b")
_PEOPLE_GET = re.compile(r"(?i)\byour [a-z-]+(?: [a-z-]+)? get\b")


def _item_texts(item: dict) -> list[str]:
    """Every word an item is served with: its stem, the price card's line, the box's label, the plan's stem, the
    options and the ladder's rungs."""
    texts = [item.get("question"), item.get("whatYouGet"), (item.get("valueBox") or {}).get("label"),
             (item.get("plan") or {}).get("question")]
    texts += [o.get("label") for o in item.get("options") or []]
    texts += [o.get("label") for o in (item.get("plan") or {}).get("options") or []]
    return [t for t in texts if isinstance(t, str) and t]


def cloud_131(j) -> dict:
    """Spec 070 FR-2 (keel-cloud 131 FR-1, FR-2, FR-8, FR-9, FR-13): on a back-test, the served gate beside the gate on
    the circumstance's event (`vs.gate_from_circumstance`), a Frequency stem past the spoken cap (`vs.frequency_held`),
    *per {unit}, each* said on any served item, the price card's *your {people} get*, the Buyer set's *... instead* --
    each a finding, never a stop; and FR-1's `lock_refused` edits as the walk made them. Empty keys left out."""
    from harness import vectors_script as vs                       # noqa: PLC0415
    entry = j.entry
    out: dict = {"gate": [], "frequency_over_the_cap": [], "per_each": [], "people_get": [], "buyer_instead": [],
                 "lock_refused": list((getattr(j, "changed", None) or {}).get("lock_refused") or [])}
    window = _safe(lambda: vs.window_of(entry))
    mirror = _safe(lambda: vs.gate_from_circumstance(window, (entry.context or {}).get("circumstance"))) \
        if window is not None else None
    seen: set = set()
    for person, interview in (getattr(j, "interviews", None) or {}).items():
        gate = ((interview or {}).get("gate") or {}).get("question")
        if gate and mirror and gate != mirror and ("gate", gate) not in seen:
            seen.add(("gate", gate))
            out["gate"].append({"rule": "131 FR-1", "served": gate, "mirror": mirror})
        for part in (interview or {}).get("parts") or []:
            for item in part.get("items") or []:
                key = item.get("dimension")
                stem = str(item.get("question") or "")
                if key == "problem.frequency" and len(stem.split()) > vs.STEM_MAX_WORDS and ("f", stem) not in seen:
                    seen.add(("f", stem))
                    out["frequency_over_the_cap"].append({"rule": "131 FR-2", "served": stem,
                                                          "words": len(stem.split())})
                for text in _item_texts(item):
                    if _EACH_AFTER_PER.search(text) and ("e", text) not in seen:
                        seen.add(("e", text))
                        out["per_each"].append({"rule": "131 FR-8", "dimension": key, "said": text})
                    if key == "commercial.price" and text == item.get("whatYouGet") and _PEOPLE_GET.search(text) \
                            and ("g", text) not in seen:
                        seen.add(("g", text))
                        out["people_get"].append({"rule": "131 FR-9", "said": text})
                    if key == "commercial.buyer_payer_alignment" and "agree instead" in text and ("b", text) not in seen:
                        seen.add(("b", text))
                        out["buyer_instead"].append({"rule": "131 FR-13", "said": text})
    findings = getattr(j, "findings", None)
    if isinstance(findings, list):
        words = {"gate": "the served gate is not the circumstance's event as the harness mirrors 131 FR-1",
                 "frequency_over_the_cap": "Frequency served over the 20-word cap (131 FR-2)",
                 "per_each": "a unit said twice, *per {unit}, each* (131 FR-8)",
                 "people_get": "the price card pastes a benefit after *your {people} get* (131 FR-9)",
                 "buyer_instead": "the Buyer set's *someone else would have to agree instead* (131 FR-13)"}
        for key, what in words.items():
            for row in out[key]:
                findings.append({"what": what, "served": row})
    return {k: v for k, v in out.items() if v}


# ------------------------------------------------------------------------- spec 069 FR-3: the lock-time notes

#: keel-cloud 130's new notes, by name: S13 a saved row over its screen's cap (at the lock, FR-5), L21 a drafted
#: condition in place of the founder's own (FR-1), M5 a trade word or a design note in the reveal (FR-9); X12 the
#: condition code drew for a qualified people (FR-8), read beside them.
LOCK_NOTES = {"S13": "a saved row over its screen's word cap (keel-cloud 130 FR-5)",
              "L21": "a drafted condition in place of the founder's own (keel-cloud 130 FR-1)",
              "M5": "a trade word or a design note in the reveal (keel-cloud 130 FR-9)",
              "X12": "a condition code drew from the founder's people (keel-cloud 130 FR-8)"}
_NOTE = re.compile(r"\b(" + "|".join(LOCK_NOTES) + r"): ([^\n]{1,400})")


def lock_notes(j, interactions: list | None = None) -> list[dict]:
    """Spec 069 FR-3: the project's interactions (`GET /v2/inference-interactions?project_id=`), read once at the
    transcript -- each row's `detail` (*breach <path>: <why>*, the first note of a row applied over a word rule),
    `founderNote`, `diagnostic` and its turns' `content` (a repair turn names the rule it repairs) -- for keel-cloud 130's
    notes by name (`LOCK_NOTES`); each found once, `{rule, means, screen, said}`. A reading, never asserted."""
    if interactions is None:
        project_id = getattr(j, "project_id", None)
        if not project_id or not callable(getattr(j, "get", None)):
            return []
        interactions = _safe(lambda: j.get(f"/v2/inference-interactions?project_id={project_id}"), []) or []
    out, seen = [], set()
    for row in interactions if isinstance(interactions, list) else []:
        texts = [row.get(k) for k in ("detail", "founderNote", "diagnostic")]
        texts += [(t or {}).get("content") for t in row.get("turns") or [] if isinstance(t, dict)]
        for text in texts:
            if not isinstance(text, str):
                continue
            for m in _NOTE.finditer(text):
                said = m.group(2).strip()
                key = (m.group(1), said[:160])
                if key in seen:
                    continue
                seen.add(key)
                out.append({"rule": m.group(1), "means": LOCK_NOTES[m.group(1)], "screen": row.get("screen"),
                            "said": f"{m.group(1)}: {said}"})
    return out


# ------------------------------------------------------------------------------------------- FR-4.3 the brief

def brief(standings: dict) -> dict:
    facts = standings.get("facts") or {}
    decision = facts.get("decision") or {}
    stages = {}
    for vector in ("problem", "solution", "commercial"):
        stage = facts.get(vector) or {}
        stages[vector.upper()] = {"broke": stage.get("broke"), "notAsked": stage.get("notAsked")}
    insights = []
    for i in standings.get("insights") or []:
        insights.append({"dimension": i.get("dimension"), "name": i.get("name"), "status": i.get("status"),
                         "rungHeading": i.get("rungHeading"), "noQuestionWhy": i.get("noQuestionWhy"),
                         "against": i.get("against"), "asked": i.get("asked"), "answered": i.get("answered"),
                         "themes": [{"label": t.get("label"), "count": t.get("count"),
                                     "evidence": [{"name": q.get("name"), "text": q.get("text")}
                                                  for q in t.get("quotes") or []]}
                                    for t in i.get("themes") or []],
                         "raw": i.get("raw"), "rawQuotes": [{"name": q.get("name"), "text": q.get("text")}
                                                           for q in i.get("rawQuotes") or []],
                         # spec 064 FR-8a / FR-9 (keel-cloud 119): the state, the dissent frame, every quote's side
                         "state": i.get("state"), "note": i.get("note"), "dissent": i.get("dissent"),
                         "frame": i.get("frame"),
                         "quotes": [{k: q.get(k) for k in ("name", "text", "option", "side", "heading")}
                                    for q in i.get("quotes") or []]})
    return {"decision": {k: decision.get(k) for k in ("label", "howSure", "reason", "smallestN", "split", "notTested",
                                                      "change")},
            "notAsked": standings.get("notAsked"), "outsideSegment": standings.get("outsideSegment"),
            "verdicts": {v.get("vector"): v.get("words") or v.get("verdict") for v in facts.get("vectors") or []},
            "cards": [{k: c.get(k) for k in ("key", "name", "number", "line", "status", "statusWords", "keelBar")}
                      for c in facts.get("cards") or []],
            "stages": stages, "insights": insights, "pilot": standings.get("pilot"),
            "price": standings.get("priceMedian"), "people": standings.get("people"),
            "contextUnderstands": standings.get("contextUnderstands")}


# ------------------------------------------------------------------------------------------ FR-4.4 the readings

def readings(j, invitations: dict) -> list[dict]:
    by_name = {r.get("personName"): r.get("invitationId") or r.get("id")
               for r in (invitations or {}).get("invitations") or []}
    out = []
    for p in j.people:
        row = {"person": p.person, "link": p.link, "gate": p.recency, "story": p.story,
               "chip": p.anchor_chip, "file anchoring": p.anchoring}
        invitation = by_name.get(p.person)
        if invitation:
            detail = _safe(lambda i=invitation: j.get(j.project(f"/invitations/{i}")), {})
            interview = (detail or {}).get("interview") or {}
            row["model anchoring"] = interview.get("anchoring")
            row["status"] = (detail or {}).get("status")
        row["same"] = (row.get("model anchoring") == p.anchoring) if p.anchoring else None
        out.append(row)
    return out


# ------------------------------------------------------------------------------------------ FR-4.5 cost and time

def cost(j, bt: Backtest | None = None) -> dict:
    from harness import keel_host                                  # noqa: PLC0415
    interactions = j.get(f"/v2/inference-interactions?project_id={j.project_id}") or []
    per_job = keel_host.jobs_with_their_execution(j.get, interactions)
    total = sum(r.get("actual_cost_micro_usd") or 0 for r in per_job)
    by_class: dict = {}
    for r in per_job:
        c = by_class.setdefault(r.get("screen") or "?", {"jobs": 0, "micro_usd": 0, "models": set()})
        c["jobs"] += 1
        c["micro_usd"] += r.get("actual_cost_micro_usd") or 0
        if r.get("model_used"):
            c["models"].add(r["model_used"])
    for c in by_class.values():
        c["models"] = sorted(c["models"])
        c["usd"] = round(c["micro_usd"] / 1_000_000, 4)
    on_host = bt is not None and bt.door == "host"
    host_side = {}
    if on_host:
        # spec 066 FR-3: keel-cloud prices nothing on the host door; the CLI's own report, where it gives one
        host_side = {"door": "host", "cli": cli_usage(bt.keel_home, [r.get("job_id") for r in per_job])}
        screen_of = {r.get("job_id"): r.get("screen") for r in per_job}
        for row in host_side["cli"]["per_job"]:
            row["screen"] = screen_of.get(row["job_id"])
    return {**host_side, "jobs": len(per_job), "micro_usd": total, "usd": round(total / 1_000_000, 4),
            "by_class": by_class, "models": sorted({r.get("model_used") for r in per_job if r.get("model_used")}),
            "hosts": sorted({str(r.get("host")) for r in per_job}),
            "not settled": [{k: r.get(k) for k in ("screen", "status", "error")} for r in per_job
                            if r.get("status") != "COMPLETED"],
            "not on the wire": ("the answer path's classifier calls (keel-cloud 099) are no job, so their cost is not "
                                "here; tokens are not on the wire either"),
            "per_job": [{k: r.get(k) for k in ("screen", "status", "model_requested", "model_used",
                                               "actual_cost_micro_usd", "host")} for r in per_job]}


def host_door_record(j, bt: Backtest, *, passed: bool, teardown: dict | None) -> dict:
    """Spec 066: the host door's part of the record -- the runtime's teardown, the jobs on the host, the CLI's own
    usage in the cost section, and the plan's limit when it was met (FR-4's finding when the run stopped on it)."""
    from harness import keel_host                                  # noqa: PLC0415
    per_job = []
    if j is not None and getattr(j, "project_id", None):
        per_job = _safe(lambda: keel_host.jobs_with_their_execution(
            j.get, j.get(f"/v2/inference-interactions?project_id={j.project_id}") or []), []) or []
        if isinstance(per_job, dict):
            per_job = []
    out: dict = {"runtime": {**(teardown or {}), "launch log": f"{KEEL_HOME_DIR}/{RUNTIME_LOG}",
                             "heartbeat kept": f"{KEEL_HOME_DIR}/{HEARTBEAT_LAST}"},
                 "jobs on the host": bt.jobs_on_the_host or (host_door_jobs(per_job, bt.host) if per_job else None)}
    limit = plan_limit(bt, per_job)
    out["plan limit"] = limit
    if limit and not passed:
        out["limit_stop"] = limit.get("at") or ""
    return out


def transcript(j, bt: Backtest) -> dict:
    if j is None:
        return {"journey": "never opened"}
    entry = j.entry
    wire = _wire(j)
    standings = wire.get("standings") or j.standings or {}
    me = _safe(lambda: j.get("/v2/me"), {})
    # read before the findings are listed: these readings add their own (spec 067 FR-7, spec 069 FR-1)
    changed = _safe(lambda: changed_screens(j, standings))
    notes = _safe(lambda: lock_notes(j), []) or []
    findings = getattr(j, "findings", None)
    if isinstance(findings, list):
        findings.extend({"what": f"{n['rule']} on {n['screen']}: {n['means']} (spec 069 FR-3)", "served": n["said"]}
                        for n in notes)
    return {
        "entry": {"id": entry.id, "title": entry.title, "path": str(entry.path), "sha256": entry.sha256,
                  "idea_name": getattr(entry, "idea_name", None), "b2b": entry.b2b()},
        "stack": {"keel-cloud": _sha(getattr(j.stack, "keel_cloud", None)),
                  "keel-web": _sha(getattr(j.stack, "keel_web", None))},
        "founder": {"identity": IDENTITY_EMAIL, "at sign-up": bt.me_at_signup,
                    "credits now": (me or {}).get("creditsAvailable"), "project": j.project_id},
        **({"door": bt.door_facts} if bt.door == "host" else {}),
        "founder_screens": founder_screens(j, bt.cam, wire),
        "respondents": respondent_questions(j, bt.cam),
        "spoken_guard": _safe(lambda: spoken_guard(j)),
        "changed_screens": changed,
        "lock_notes": notes,
        "brief": _safe(lambda: brief(standings)),
        "readings": _safe(lambda: readings(j, wire.get("invitations") or {}), []),
        "cost": _safe(lambda: cost(j, bt)),
        "export": bt.export,
        "themes_settled": bt.themes_settled,
        "findings": list(getattr(j, "findings", []) or []),
        "screenshots": {"founder": len(bt.cam.founder_shots) if bt.cam else 0,
                        "respondent": {link: len(v.get("shots") or [])
                                       for link, v in (bt.cam.respondent_shots if bt.cam else {}).items()}},
    }


# --------------------------------------------------------------------------------------------- the markdown

def _q(value: Any) -> str:
    if value in (None, "", [], {}):
        return "--"
    if isinstance(value, (dict, list)):
        return "`" + json.dumps(value, ensure_ascii=False) + "`"
    return str(value).replace("\n", " ")


def markdown(r: dict) -> str:
    """`backtest.md`: for reading. Every value as served; nothing asserted."""
    entry = r.get("entry") or {}
    b = r.get("brief") or {}
    decision = b.get("decision") or {}
    c = r.get("cost") or {}
    shots = r.get("screenshots") or {}
    host_door = (r.get("door") or {}).get("door") == "host"
    answered_by = ("the founder's own Claude Code (host door)" if host_door else "Keel's AI (local)")
    cli = c.get("cli") or {}
    lines = [f"# Back-test: {entry.get('title') or entry.get('id') or '?'}", "",
             f"- Entry: `{entry.get('id')}` ({entry.get('path')}), the founder's idea name *{entry.get('idea_name')}*",
             f"- Run: `{r.get('run')}` -- {'walked to the end' if r.get('passed') else 'stopped at: ' + _q(r.get('failed_step'))}",
             f"- Stack: keel-cloud `{(r.get('stack') or {}).get('keel-cloud')}`, keel-web "
             f"`{(r.get('stack') or {}).get('keel-web')}`, {answered_by}, founder `{IDENTITY_EMAIL}`",
             f"- Decision: **{decision.get('label')}** ({decision.get('howSure')}; {decision.get('reason')})",
             f"- Verdicts: {_q(b.get('verdicts'))}",
             f"- Pilot: {_q(b.get('pilot', {}) and {k: (b.get('pilot') or {}).get(k) for k in ('optedIn', 'finished', 'percent')})}"
             f"; price: {_q((b.get('price') or {}).get('edgeSaid') if isinstance(b.get('price'), dict) else b.get('price'))}",
             (f"- Cost: ${c.get('usd')} over {c.get('jobs')} jobs; models {_q(c.get('models'))}" if not host_door else
              f"- Cost: {('the CLI reported $' + str(cli.get('usd'))) if cli.get('usd') is not None else NOT_PRICED} "
              f"over {c.get('jobs')} jobs; models {_q(c.get('models'))}"),
             f"- Wall time: {r.get('wall_s')} s; screenshots: {shots.get('founder')} founder, "
             f"{_q(shots.get('respondent'))} respondent",
             f"- Export: {_q(r.get('export'))}",
             f"- THEMES settled before the export: {_q(r.get('themes_settled'))}",
             f"- Keel's AI refused and retried (findings): {len(r.get('findings') or [])}"
             + "".join(f"\n  - {f.get('what')}: "
                       + (f"*{f['anchor']}* -- " if f.get("anchor") else "")
                       + f"{f.get('refused') or f.get('batch')}" for f in r.get("findings") or []),
             "", "Nothing here is asserted: the model's words are the finding (spec 062 FR-4).", ""]
    if host_door:
        door_ = r.get("door") or {}
        hosted = r.get("jobs on the host") or {}
        skill = door_.get("keel-connect-skill") or {}
        extra = [f"- Door: {door_.get('words') or HOST_DOOR_WORDS}; CLI {_q((door_.get('cli') or {}).get('version'))}, "
                 f"login {_q((door_.get('cli') or {}).get('authMethod'))}; keel-connect-skill "
                 f"{_q(skill.get('VERSION'))}, runtime {_q(skill.get('RUNTIME_VERSION'))}",
                 f"- Model: {_q(door_.get('model'))}",
                 f"- Jobs on the host: {_q({k: hosted.get(k) for k in ('jobs', 'completed', 'open', 'no execution', 'bad')})}",
                 f"- Runtime teardown: {_q({k: (r.get('runtime') or {}).get(k) for k in ('signal', 'exit code', 'alive after', 'credential removed')})}"]
        if r.get("limit_stop") is not None:
            extra.append(f"- Finding: *{LIMIT_FINDING} {r.get('limit_stop') or 'an unnamed time'}* "
                         f"({_q((r.get('plan limit') or {}).get('said'))})")
        elif r.get("plan limit"):
            extra.append(f"- The plan's limit was met and the run went on: {_q(r.get('plan limit'))}")
        at = lines.index("Nothing here is asserted: the model's words are the finding (spec 062 FR-4).") - 1
        lines[at:at] = extra
    lines += ["## 1. Founder screens, in order", ""]
    for s in r.get("founder_screens") or []:
        lines.append(f"### {s['n']:02d}. {s['screen']}  (`{s.get('file')}`)")
        for label, key in (("Kicker", "kicker"), ("Question", "question"), ("Hint", "hint")):
            if s.get(key):
                lines.append(f"- {label}: {_q(s[key])}")
        if s.get("options"):
            lines.append("- Options: " + " | ".join(str(o) for o in s["options"]))
        if s.get("rows"):
            lines.append("- List: " + " | ".join(str(o) for o in s["rows"]))
        if s.get("chips"):
            lines.append("- Chips: " + " | ".join(str(o) for o in s["chips"]))
        lines.append(f"- Founder (from the file): {_q(s.get('answer'))}")
        lines.append(f"- Keel read back: {_q(s.get('keel read back'))}")
        lines.append("")
    lines += ["## 2. Respondent questions, per link", ""]
    for link, v in (r.get("respondents") or {}).items():
        served = v.get("served") or {}
        lines.append(f"### {link} -- as served to {v.get('person')} ({served.get('kind')})")
        if served.get("idea"):
            lines.append(f"- Idea: {_q(served['idea'])}")
        if served.get("gate"):
            gate = served["gate"]
            if gate.get("condition"):
                lines.append(f"- Gate chip (asked first): **{(gate['condition'] or {}).get('question')}** "
                             f"(inside: {_q((gate['condition'] or {}).get('inCodes'))})")
            lines.append(f"- Gate: {_q(gate)}")
        for part in served.get("parts") or []:
            lines.append(f"- Part {part.get('part')}:")
            for n, item in enumerate(part.get("items") or [], start=1):
                lines.append(f"  {n}. **{item.get('question')}** ({item.get('dimension')}, {item.get('control')})")
                opts = item.get("options") or item.get("advantages") or []
                if opts:
                    lines.append("     options: " + " | ".join(str(o) for o in opts))
                if item.get("escape"):
                    lines.append(f"     escape: {item['escape']}")
                if item.get("valueBox"):
                    box = item["valueBox"]
                    lines.append(f"     value box: between __ and __ {box.get('label')} (chips: "
                                 + " | ".join(str((c or {}).get("label")) for c in [box.get("nothing")]
                                              + list(box.get("chips") or [])) + ")")
                if item.get("whatYouGet"):
                    lines.append(f"     what you'd get: {item['whatYouGet']}")
                if item.get("plan"):
                    lines.append(f"     then: **{item['plan'].get('question')}** -- "
                                 + " | ".join(str(o) for o in item["plan"].get("options") or []))
        if served.get("reveal"):
            lines.append(f"- Reveal: {_q(served['reveal'])}")
        lines.append("- Screens: " + ", ".join(f"`{f}`" for f in v.get("screens") or []))
        lines.append("")
    guard = r.get("spoken_guard") or {}
    if guard:
        lines += ["### The spoken guard (spec 067 FR-8: S1-S10 on every served item, the stem at most 20 words)", "",
                  f"- {guard.get('clean')} of {guard.get('items')} items clean; the longest stem "
                  f"{guard.get('longest_stem')} words"]
        for row in guard.get("red") or []:
            lines.append(f"- **RED** {row.get('link')} · {row.get('dimension')} · stem {row.get('stem_words')} words: "
                         f"*{row.get('stem')}* -- " + ("; ".join(row.get("faults") or []) or "past 20 words"))
        lines.append("")
    notes = r.get("lock_notes") or []
    if notes:
        lines += ["### keel-cloud 130's notes, by name (spec 069 FR-3)", ""]
        lines += [f"- **{n.get('rule')}** on {n.get('screen')} ({n.get('means')}): {n.get('said')}" for n in notes]
        lines.append("")
    changed = r.get("changed_screens") or {}
    if any(changed.values()):
        lines += ["### keel-cloud 128's changed screens, as read (spec 067 FR-7)", ""]
        for row in changed.get("consumer_words") or []:
            lines.append(f"- consumer link says *{row.get('word')}* ({row.get('dimension')}): {row.get('said')}")
        for row in changed.get("plan_after_closed_price") or []:
            lines.append(f"- {row.get('person')} closed the price and was shown the plan: {_q(row.get('plan'))}")
        for row in changed.get("people_disagree_on_a_bar_line") or []:
            lines.append(f"- *People disagree* on a bar line: {row.get('key')} {row.get('number')}")
        cloud = changed.get("cloud_130") or {}
        if cloud:
            lines.append("- keel-cloud 130's words beside the harness's mirror (spec 069 FR-1, FR-2):")
            for row in cloud.get("stems") or []:
                lines.append(f"  - {row.get('dimension')} ({row.get('rule')}): served *{row.get('served')}*; "
                             f"mirror *{row.get('mirror')}*")
            for row in cloud.get("gate_asks_the_job") or []:
                lines.append(f"  - the gate asks the job ({row.get('rule')}): *{row.get('gate')}*")
            for row in cloud.get("brief_lines") or []:
                lines.append(f"  - {row.get('key')} ({row.get('rule')}): *{row.get('line')}*; mirror "
                             f"*{row.get('mirror')}*")
            for row in cloud.get("replaced") or []:
                lines.append(f"  - replaced on {row.get('dimension')} (L21, contract 37): *{row.get('label')}* in "
                             f"place of the founder's *{row.get('replaces')}*")
        cloud = changed.get("cloud_131") or {}
        if cloud:
            lines.append("- keel-cloud 131's words beside the harness's mirror (spec 070 FR-1, FR-2):")
            for row in cloud.get("lock_refused") or []:
                lines.append(f"  - the lock refused the {row.get('line')} line on *{row.get('word')}* ({row.get('rule')}, "
                             f"{row.get('code')}): before *{_q(row.get('before'))}*; after *{_q(row.get('after'))}*")
            for row in cloud.get("gate") or []:
                lines.append(f"  - the gate ({row.get('rule')}): served *{row.get('served')}*; mirror "
                             f"*{row.get('mirror')}*")
            for key in ("frequency_over_the_cap", "per_each", "people_get", "buyer_instead"):
                for row in cloud.get(key) or []:
                    lines.append(f"  - {key} ({row.get('rule')}): *{row.get('served') or row.get('said')}*")
        web = changed.get("web_106") or {}
        if web:
            lines.append("- keel-web 106's screens (spec 068 FR-4):")
            for key in ("occasion_field", "context_wire", "idea_name", "needs_input", "market_other", "friction_row",
                        "gate_no"):
                if key in web:
                    lines.append(f"  - {key}: {_q(web[key])}")
            for row in web.get("consumer_words") or []:
                lines.append(f"  - the consumer report says *{row.get('word')}* ({row.get('where')}): {row.get('text')}")
        lines.append("")
    change = decision.get("change") or {}
    lines += ["## 3. The brief", "", f"- Decision: {_q(decision)}", f"- Verdicts: {_q(b.get('verdicts'))}"]
    for sentence in (change.get("sentence"), (change.get("also") or {}).get("sentence")):
        if sentence:
            lines.append(f"- The change: {sentence}")
    lines += [f"- Outside the people described: {_q(b.get('outsideSegment'))}", ""]
    for card in b.get("cards") or []:
        lines.append(f"- **{card.get('name')}** {card.get('number')} -- {card.get('line')} -- {card.get('statusWords')}"
                     + (f" (Keel's bar: {card['keelBar']})" if card.get("keelBar") else ""))
    lines.append("")
    for vector, stage in (b.get("stages") or {}).items():
        lines.append(f"- {vector}: broke {_q(stage.get('broke'))}; not asked {_q(stage.get('notAsked'))}")
    lines += ["", "### Insights", ""]
    for i in b.get("insights") or []:
        lines.append(f"- **{i.get('name')}** ({i.get('status')}, {i.get('state')}; against {i.get('against')}, asked "
                     f"{i.get('asked')}, answered {i.get('answered')}) {i.get('rungHeading') or ''}"
                     + (f" -- {i.get('frame')}" if i.get("dissent") else "")
                     + (f" -- {i.get('note')}" if i.get("note") else ""))
        for t in i.get("themes") or []:
            lines.append(f"  - {t.get('label')} ({t.get('count')})")
            for q in t.get("evidence") or []:
                lines.append(f"    - {q.get('name')}: \"{q.get('text')}\"")
        for q in i.get("rawQuotes") or []:
            lines.append(f"  - (raw) {q.get('name')}: \"{q.get('text')}\"")
    for n in b.get("notAsked") or []:
        lines.append(f"- {n.get('name')}: {n.get('why')}.")
    lines += ["", f"- Pilot: {_q(b.get('pilot'))}", f"- Price: {_q(b.get('price'))}", ""]
    lines += ["## 4. Readings: the model's anchoring beside the file's", "",
              "| Person | Link | Gate | File | Model | Same |", "|---|---|---|---|---|---|"]
    for row in r.get("readings") or []:
        lines.append(f"| {row.get('person')} | {row.get('link')} | {_q(row.get('gate'))} | {_q(row.get('file anchoring'))}"
                     f" | {_q(row.get('model anchoring'))} | {_q(row.get('same'))} |")
    lines += ["", "## 5. Cost and time", "",
              f"- Summed: {c.get('micro_usd')} micro-USD (${c.get('usd')}), {c.get('jobs')} jobs, hosts {_q(c.get('hosts'))}",
              f"- Models: {_q(c.get('models'))}"]
    if host_door:
        lines += [f"- The CLI's own usage: {cli.get('words') or NOT_PRICED} -- "
                  f"{('$' + str(cli.get('usd'))) if cli.get('usd') is not None else '--'} over {cli.get('priced')} of "
                  f"{cli.get('envelopes')} envelopes; tokens {_q(cli.get('tokens'))}",
                  f"- The result events' usage, summed: {_q(cli.get('usage'))}",
                  "- keel-cloud priced nothing: on the host door the founder's own plan answers every job"]
        for row in cli.get("per_job") or []:
            u = row.get("usage") or {}
            lines.append(f"  - {row.get('screen') or '?'} `{row.get('job_id')}`: "
                         f"${round(row['usd'], 4) if isinstance(row.get('usd'), (int, float)) else '--'}, in {u.get('input_tokens')} / out {u.get('output_tokens')} / cache read "
                         f"{u.get('cache_read_input_tokens')} / cache write {u.get('cache_creation_input_tokens')}, "
                         f"{_q(row.get('models'))}, {row.get('num_turns')} turns"
                         + (" (error)" if row.get("is_error") else ""))
    for name, k in (c.get("by_class") or {}).items():
        lines.append(f"- {name}: {k.get('jobs')} jobs, ${k.get('usd')}, {_q(k.get('models'))}")
    if c.get("not settled"):
        lines.append(f"- Not settled: {_q(c.get('not settled'))}")
    lines.append(f"- {c.get('not on the wire', '')}")
    lines += ["", f"Wall time {r.get('wall_s')} s:"]
    for leg in r.get("legs") or []:
        lines.append(f"- {leg.get('leg')}: {leg.get('seconds')} s")
    if r.get("transcript_error"):
        lines += ["", f"Transcript error: {r['transcript_error']}"]
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------------------------------ FR-6: the runner's read

def run_dir_in(log_text: str) -> Path | None:
    """The run directory a `make backtest` log names (`corpus_scenario.run` prints `run bundle: <dir>` at its end)."""
    found = re.findall(r"run bundle: (\S+)", log_text or "")
    return Path(found[-1]) if found else None


def latest_run_dir(entry_id: str, log_path: Path | None = None, runs: Path | None = None) -> Path | None:
    """The run directory of a `make backtest` that passed: pytest -q prints no captured stdout for a green test, so the
    log names no `run bundle:` (2026-10-23: every clean host-door run printed `(no run directory)`). The newest
    `runs/<ts>-backtest-<id>` whose record was written while the log was being written (between the log file's birth and
    its last write); a run that stopped before its directory existed (a load refusal) matches nothing, and `None` says so."""
    root = Path(runs) if runs is not None else Path(__file__).resolve().parents[1] / "runs"
    found = sorted(d for d in root.glob(f"*-backtest-{entry_id}") if d.is_dir() and (d / RECORD).is_file())
    if not found:
        return None
    if log_path is None or not Path(log_path).is_file():
        return found[-1]
    st = Path(log_path).stat()
    start = getattr(st, "st_birthtime", None)
    fits = [d for d in found
            if (start is None or (d / RECORD).stat().st_mtime >= start - 5) and (d / RECORD).stat().st_mtime <= st.st_mtime + 5]
    return fits[-1] if fits else None


def summary(run_dir: Path | None, entry_id: str) -> dict:
    """FR-6's one line, as data: the id, the run directory, the steps and the bad ones (the transcript's `ok: false`),
    the decision label, and -- when `backtest.md` says the run stopped on the plan's limit -- that time."""
    out: dict = {"id": entry_id, "run_dir": str(run_dir) if run_dir else None, "steps": None, "bad": None,
                 "decision": None, "limit_stop": None}
    if run_dir is None or not Path(run_dir).is_dir():
        return out
    steps = bad = 0
    try:
        for line in (Path(run_dir) / "transcript.jsonl").read_text(encoding="utf-8").splitlines():
            if line.strip():
                steps += 1
                bad += json.loads(line).get("ok") is False
        out["steps"], out["bad"] = steps, bad
    except (OSError, ValueError):
        pass
    out.update(run=Path(run_dir).name, door="KEEL", score=None)
    try:
        record = json.loads((Path(run_dir) / RECORD).read_text(encoding="utf-8"))
        out["decision"] = (((record.get("brief") or {}).get("decision")) or {}).get("label")
        out["run"] = record.get("run") or out["run"]
        out["door"] = "host" if (record.get("door") or {}).get("door") == "host" or record.get("spec") == "062+066" \
            else "KEEL"
        out["score"] = record.get("score")             # a judge's; a run's own record carries none today
    except (OSError, ValueError, AttributeError):
        pass
    try:
        out["limit_stop"] = limit_stop_in((Path(run_dir) / MARKDOWN).read_text(encoding="utf-8"))
    except OSError:
        pass
    return out


#: Spec 067 (keel-cloud 128 acceptance 4): the judgement register, keel-cloud's -- read here, never written.
REGISTER = Path("canon") / "designs" / "measured-beliefs" / "backtest" / "judgements" / "README.md"


def register_scores(text: str, entry_id: str) -> list[str]:
    """The *Score* cells of the register's rows for `entry_id`, in the table's order (the header names the column)."""
    header, scores = None, []
    for line in (text or "").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None and "Entry" in cells and "Score" in cells:
            header = cells
            continue
        if header and cells and cells[0] == entry_id and len(cells) == len(header):
            scores.append(cells[header.index("Score")])
    return scores


def rerun_row(row: dict, register_text: str) -> str:
    """Spec 067 (the register's *Re-run* column): the row a re-run on the 128 build adds -- entry, run id, door,
    decision, the score the run's record carries (none until judged), and the previous row's score for the entry read
    from the register. The parent session fills *Judged* and the judge's score and adds the row; nothing is written."""
    was = (register_scores(register_text, row["id"]) or [None])[-1]
    return (f"re-run row: | {row['id']} | (judged: to fill) | {row.get('run') or '--'} | {row.get('door') or '--'} | "
            f"{row.get('decision') or '--'} | {row.get('score') or 'to be judged'} | Re-run: after 128 · was "
            f"{was or 'no earlier row'} |")


def _register_text() -> str:
    try:
        from stack.config import load_config                           # noqa: PLC0415
        return (Path(load_config(validate=False).keel_cloud) / REGISTER).read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001 - no register to read is a line that says so, never a failed summary
        return ""


def main(argv: list[str] | None = None) -> int:
    """`python -m evals.backtest summary <log> <id>` prints FR-6's line (and, spec 067, the register's re-run row); `... resume <log> <id>` prints the seconds to
    wait before a rerun when the run stopped on the plan's limit, and nothing when it did not. Reads run files only --
    never an environment, a key or a login."""
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 3 or argv[0] not in ("summary", "resume"):
        print("usage: python -m evals.backtest {summary|resume} <make log> <entry id>", file=sys.stderr)
        return 2
    what, log, entry_id = argv
    try:
        log_text = Path(log).read_text(encoding="utf-8", errors="replace")
    except OSError:
        log_text = ""
    row = summary(run_dir_in(log_text) or latest_run_dir(entry_id, Path(log)), entry_id)
    if what == "summary":
        print(f"{row['id']}\t{row['run_dir'] or '(no run directory)'}\tsteps {row['steps']}\tbad {row['bad']}\t"
              f"{row['decision'] or '--'}" + (f"\tstopped by the plan's limit at {row['limit_stop'] or 'an unnamed time'}"
                                             if row["limit_stop"] is not None else ""))
        if row["run_dir"]:
            print(rerun_row(row, _register_text()))
    elif row["limit_stop"] is not None:
        print(int(max(60.0, resume_epoch(row["limit_stop"] or None) - time.time())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
