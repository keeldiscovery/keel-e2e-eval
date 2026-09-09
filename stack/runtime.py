"""The runtime the referee runs is **the one that travelled inside the skill** (spec 012; design
of record keel-cloud `canon/designs/keel-skill-design.md` §3.1/§3.2/§13 step 9).

Three things changed here from spec 005's version, and each is one sentence:

**Which runtime.** `status` used to shell `python3 -m keel_runtime` out of the keel-runtime
*checkout*. It now runs `<keel-connect-skill>/keel_runtime/` -- the copy `make runtime` puts
beside the skill's scripts -- on `PYTHONPATH`, exactly as the skill's own
`scripts/_runtime_location.py` runs it. The checkout stays configured in `stack.toml` for the two
places that read keel-runtime's *source* rather than run it (`harness/canary.py`'s caps,
`instructions/prompts.py`'s `build_prompt`); nothing here passes `--runtime-path` any more, and
`harness/connect.py` scrubs `KEEL_RUNTIME_PATH` out of the environment it hands the skill's script
so an operator's ambient override cannot silently substitute a checkout for the runtime a founder
would get (invariant T-1).

**Which home, and which Keel.** The design's rule is that the home follows the address --
`~/.keel/localhost-18080/` by derivation (§6.3). **This stack keeps setting `KEEL_HOME`**, to
`runs/.stack/keel-home[-<profile>]/`, because the referee's own rule outranks the default here:
two profiles must never share a home (relay-design.md §12.5), `make up` wipes the home it owns and
a referee may not wipe a directory under the founder's own `~/.keel/`, and a run's credential must
never be the one the founder's machine is using. `KEEL_HOME`/`--home` is an *override* in the
design, not a violation of it -- and spec 012 pays for using it by asserting the other half:
`status.environment` must still read `localhost:<port>` (FR-004), so an isolated home can never
quietly become an unnamed Keel. That costs one file: `keel status` takes no `--base-url`, so the
home this stack owns carries a `config.json` naming this profile's Keel, and every call that is
handed only a `--home` resolves the address every other call names.

**How it stops.** `kill()` is gone. `make down` and `stop_runtime` ask the runtime to `disconnect`
-- keel-runtime's own command (its spec 003 contract,
`specs/003-keel-disconnect/contracts/disconnect-cli-output.md`), through keel-connect-skill's
`scripts/keel_disconnect.py` when that script exists and directly through the bundled runtime when
it does not -- and read the outcome it answers with. `stopped`/`disconnected` is a *proof* the
process is gone rather than a signal sent and hoped for; `not_running` is the idempotent second
call. Teardown still never fails on `did_not_stop`.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from stack.config import REPO_ROOT, StackConfig

#: Environment variables that name *which runtime, which home and which Keel*. Every one of them
#: is a legitimate founder-facing override and every one of them is a lie inside a referee run:
#: this stack names all three explicitly on every invocation, so an ambient value can only ever
#: disagree with what the run says it did. Scrubbed from every child environment (FR-004).
#: The job knobs (`KEEL_JOB_*`) are deliberately *not* scrubbed -- `runs/DRIFT.md` #46 settled that
#: the referee reads the caps the runtime is actually under and names where each came from.
AMBIENT_RUNTIME_VARS = ("KEEL_RUNTIME_PATH", "KEEL_HOME", "KEEL_BASE_URL")

#: The outcomes `make down` treats as "the runtime is gone" (keel-runtime's contract names the
#: first, third and fourth; keel-connect-skill's script renames `stopped` to `disconnected` for a
#: founder's ears, and this stack accepts both names so it works either side of that repo's spec
#: `002-keel-disconnect` landing).
STOPPED_OUTCOMES = ("stopped", "disconnected", "not_running", "stale_pid_cleared")

#: The one outcome a caller must treat as a failure (disconnect contract, guarantee 3), under both
#: names.
DID_NOT_STOP_OUTCOMES = ("timeout", "did_not_stop")


class BundledRuntimeMissing(RuntimeError):
    """`make up`'s new gate: keel-connect-skill has no `keel_runtime/` beside its scripts, so the
    runtime a founder would run does not exist on this machine yet. Raised with the one command
    that fixes it.

    **The stack does not run that command itself**, deliberately. `make runtime` writes into a
    sibling repository, and this repo owns no product code and never writes to one (README,
    AGENTS.md); it also refuses on a keel-runtime checkout carrying any uncommitted change, which
    is the normal state of a sibling somebody is working in -- so a referee that ran it would turn
    another agent's dirty tree into this stack's boot failure. A gate that names the command is
    honest about whose command it is.
    """


def home_dir(config: StackConfig) -> Path:
    """`runs/.stack/keel-home` for the default (eval) profile, unchanged; `runs/.stack/keel-
    home-<profile>` for any other (split-stacks, relay-design.md §12.5) -- two profiles running
    concurrently (e.g. two referee sessions sharing this checkout, one on each profile) must never
    share a runtime home, or one's `keel connect` heartbeat/credential reads as the other's.

    Spec 012 kept this rather than taking keel-runtime's derived `~/.keel/<host-slug>/`: see this
    module's docstring for why, and `status`'s `--base-url` for what the choice pays for.
    """
    name = "keel-home" if config.profile == "eval" else f"keel-home-{config.profile}"
    return REPO_ROOT / "runs" / ".stack" / name


def bundled_runtime_dir(config: StackConfig) -> Path:
    """`<keel-connect-skill>/keel_runtime/` -- the package `make -C ../keel-connect-skill runtime`
    writes and that repo gitignores."""
    return config.bundled_runtime_path


def bundled_runtime_present(config: StackConfig) -> bool:
    """The same test the skill's own `_runtime_location.py` makes: a directory holding a
    `__main__.py` is a runtime this interpreter can run as `-m keel_runtime`."""
    return (bundled_runtime_dir(config) / "__main__.py").is_file()


def bundled_runtime_version(config: StackConfig) -> str | None:
    """Whatever `RUNTIME_VERSION` beside the skill says the bundled copy is (`0.1.0+<sha>`, or a
    tag once keel-runtime cuts one) -- printed by the `make up` gate and written into a run
    bundle's `versions.json`, so a run can name the runtime it actually ran."""
    stamp = config.keel_connect_skill / "RUNTIME_VERSION"
    try:
        return stamp.read_text().strip() or None
    except OSError:
        return None


def require_bundled_runtime(config: StackConfig) -> Path:
    """`make up`'s gate (FR-002). Returns the package directory, or raises
    `BundledRuntimeMissing` naming the one command that creates it."""
    if bundled_runtime_present(config):
        return bundled_runtime_dir(config)
    raise BundledRuntimeMissing(
        f"keel-connect-skill has no bundled runtime at {bundled_runtime_dir(config)}. "
        f"The skill carries keel-runtime inside it (keel-cloud "
        f"canon/designs/keel-skill-design.md §3.1) and the package is generated, never committed. "
        f"Build it in that repo, on a clean keel-runtime checkout:\n"
        f"    make -C {config.keel_connect_skill} runtime\n"
        f"Nothing in this stack writes to a sibling repository, so this gate names the command "
        f"rather than running it."
    )


def scrubbed_env(extra: dict | None = None, base_env: dict | None = None) -> dict:
    """The caller's environment minus `AMBIENT_RUNTIME_VARS` -- the environment every child of
    this stack that can reach a runtime is launched with (FR-004).

    This is what makes S-008's central claim checkable rather than hopeful: with
    `KEEL_RUNTIME_PATH` gone from the environment, keel-connect-skill's script has no checkout to
    prefer and can only resolve the runtime that travelled inside it (design §3.2 rule 2, T-1).
    """
    env = {k: v for k, v in (os.environ if base_env is None else base_env).items()
           if k not in AMBIENT_RUNTIME_VARS}
    env.update(extra or {})
    return env


def runtime_env(config: StackConfig, extra: dict | None = None) -> dict:
    """`scrubbed_env`, plus the skill root on `PYTHONPATH` so this stack's own `-m keel_runtime`
    calls find the bundled package.

    `PYTHONSAFEPATH` goes with `PYTHONPATH` for the reason keel-connect-skill's
    `_runtime_location.py` sets it: on 3.11+ it drops the working directory from `sys.path`, which
    is the exact fix for a `keel_runtime/` in the cwd shadowing the one that was resolved.
    """
    env = scrubbed_env(extra)
    skill_root = str(config.keel_connect_skill)
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = skill_root + os.pathsep + existing if existing else skill_root
    env["PYTHONSAFEPATH"] = "1"
    return env


def reset(config: StackConfig) -> None:
    """Wiped, then recreated empty, at every `make up` (spec 005 edge case: no credential or
    heartbeat from a prior run survives into a new stack session).

    Spec 012 adds one file to the fresh home: a `config.json` naming this profile's own
    `base_url`. It makes the isolated home **self-describing** -- a caller handed `--home` and
    nothing else (keel-connect-skill's `keel_disconnect.py` takes no `--base-url`) resolves the
    same Keel every other call names, so `environment` reads `localhost:<port>` rather than null.
    The runtime only ever reads this file; it never writes it.
    """
    home = home_dir(config)
    if home.exists():
        shutil.rmtree(home)
    home.mkdir(parents=True, exist_ok=True)
    _write_home_config(config, home)


def _write_home_config(config: StackConfig, home: Path) -> None:
    home.mkdir(parents=True, exist_ok=True)
    (home / "config.json").write_text(
        json.dumps({"base_url": config.cloud_base_url}, indent=2) + "\n")


def ensure_home_names_keel(config: StackConfig) -> Path:
    """Non-destructive: create the home if it is missing and give it a `config.json` naming this
    profile's Keel if it has none. `reset` is the wipe; this is the guarantee that a home which
    already exists (a `make eval` that attached to a stack an older `make up` booted) still tells
    every `--home`-only caller which Keel it belongs to. Never removes or rewrites anything.
    """
    home = home_dir(config)
    if not (home / "config.json").is_file():
        _write_home_config(config, home)
    return home


def _run_runtime(config: StackConfig, argv: list[str], *, timeout: float) -> dict | None:
    """Runs the **bundled** runtime as `<this interpreter> -m keel_runtime <argv>` and returns its
    one line of JSON, or `None` for anything that is not one line of JSON with an exit code the
    contract allows. Never raises: a runtime this stack cannot shell out to is not a runtime this
    stack can call connected.
    """
    if not bundled_runtime_present(config):
        return None
    cmd = [sys.executable, "-m", "keel_runtime", *argv]
    try:
        result = subprocess.run(
            cmd,
            cwd=str(config.keel_connect_skill),
            env=runtime_env(config),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        return None


def status(config: StackConfig) -> dict:
    """`<bundled runtime> status --home <home>`.

    The runtime that answers is the one that travelled inside the skill (spec 012 FR-001), not the
    checkout -- the same package, resolved the same way, a founder's "keel connect" would run.

    **`status` takes no `--base-url`** (keel-runtime's parser: `--home` is its only flag), so the
    address it reports cannot be named on the command line. Two of the three sources that remain
    are wrong for a referee: an ambient `KEEL_BASE_URL` is scrubbed by `runtime_env`, and the
    built-in cloud default is empty. The third is the home's own `config.json`, which is exactly
    why `reset`/`ensure_home_names_keel` write one -- an isolated home that names its Keel makes
    `status.environment` read `localhost:<port>` and FR-004 checkable.

    Never raises: any subprocess or parse failure reads the same as "not running", since a
    `status` this stack cannot even shell out to is definitely not a runtime this stack can call
    connected.
    """
    body = _run_runtime(config, ["status", "--home", str(home_dir(config))], timeout=10)
    if body is None or "running" not in body:
        return {"running": False}
    return body


def is_gate_clear(config: StackConfig) -> bool:
    """The `runtime-home` gate itself (US1 independent test / acceptance scenario 1): the
    directory exists and is empty of a heartbeat -- i.e. `status` reads not-running."""
    home = home_dir(config)
    return home.is_dir() and not status(config).get("running", False)


def disconnect(config: StackConfig, *, timeout: float = 60) -> dict:
    """Stops the runtime the way a founder's "keel disconnect" does, and **reads the proof**.

    Preferred path: keel-connect-skill's `scripts/keel_disconnect.py`, run with this stack's own
    `--home` and a scrubbed environment, so the script resolves the bundled runtime itself (spec
    012 FR-003). That script is that repo's spec `002-keel-disconnect` and may not have landed
    yet; when the file is absent this falls through to `<bundled runtime> disconnect`, which is
    the command the script shells anyway -- the same four outcomes, one layer lower.

    Returns the parsed outcome dict, with `via` naming which of the two paths answered. Never
    raises: `{"outcome": "unavailable", ...}` is the answer when neither path could be run at all,
    so a teardown is never blocked by a missing sibling (idempotent, as `kill` was).
    """
    script = config.disconnect_script_path
    if script.is_file():
        cmd = [sys.executable, str(script), "--home", str(home_dir(config))]
        try:
            result = subprocess.run(
                cmd, env=runtime_env(config), capture_output=True, text=True, timeout=timeout)
            body = json.loads(result.stdout.strip().splitlines()[-1])
            if isinstance(body, dict) and "outcome" in body:
                body["via"] = "keel-connect-skill/scripts/keel_disconnect.py"
                return body
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, IndexError):
            pass  # fall through to the runtime's own command rather than fail a teardown

    body = _run_runtime(config, ["disconnect", "--home", str(home_dir(config))], timeout=timeout)
    if body is None or "outcome" not in body:
        return {"outcome": "unavailable",
                "message": "neither keel-connect-skill's keel_disconnect.py nor the bundled "
                           f"runtime's own `disconnect` could be run against {home_dir(config)}",
                "via": None}
    body["via"] = "bundled keel_runtime disconnect"
    return body
