"""Loads stack.toml (data-model.md): sibling paths, ports, timeouts -- with working defaults and
clear errors when a sibling checkout is missing.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_PATHS = {
    "keel_cloud": "../keel-cloud",
    "keel_web": "../keel-web",
    "keel_runtime": "../keel-runtime",
    "keel_connect_skill": "../keel-connect-skill",
}
DEFAULT_PORTS = {"postgres": 55432, "cloud": 18080, "web": 5173}
DEFAULT_TIMEOUTS = {"cloud_boot": 120, "web_boot": 60}

# Split-stacks (relay-design.md §12.5, the account-collision incident): the playground profile's
# own ports, used only when `load_config(profile="playground")` is asked for -- the default
# ("eval") profile's own ports above are entirely unchanged. `stack/postgres.py` also puts the
# playground profile in its own Compose *project* (never the eval profile's default project), so
# an eval `make down` can never see, let alone drop, the playground's own container or volume.
DEFAULT_PLAYGROUND_PORTS = {"postgres": 55433, "cloud": 18081, "web": 5174}
PROFILES = ("eval", "playground")


class ConfigError(RuntimeError):
    """Raised for a stack.toml problem a human must fix before anything can boot."""


@dataclass(frozen=True)
class StackConfig:
    keel_cloud: Path
    keel_web: Path
    keel_runtime: Path
    keel_connect_skill: Path
    postgres_port: int
    cloud_port: int
    web_port: int
    cloud_boot_timeout: int
    web_boot_timeout: int
    profile: str = "eval"

    @property
    def connect_check_script_path(self) -> Path:
        """keel-connect-skill's own script (contracts/skill-script-output.md) -- the only thing
        this stack ever launches keel-runtime through (spec 005 edge case: never `python3 -m
        keel_runtime` directly, so the connect skill stays under referee)."""
        return self.keel_connect_skill / "scripts" / "keel_connect_check.py"


def load_config(toml_path: Path | None = None, *, validate: bool = True,
                 profile: str = "eval") -> StackConfig:
    """Loads stack.toml, applying defaults for any missing table/key.

    `profile` selects which port set this config carries (split-stacks, relay-design.md §12.5):
    "eval" (the default, unchanged) reads `[ports]`; "playground" reads `[playground.ports]`,
    falling back to `DEFAULT_PLAYGROUND_PORTS` for anything unset. Every other table (paths,
    timeouts) is shared between profiles -- only ports (and, in stack/postgres.py, the Compose
    project) differ.

    Raises ConfigError naming the missing sibling directory when `validate` is True and a
    configured path does not exist -- an operator agent should see "no such directory" once,
    with the path it looked for, rather than a stack trace three layers down.
    """
    if profile not in PROFILES:
        raise ConfigError(f"unknown profile {profile!r} -- expected one of {PROFILES}")

    toml_path = toml_path or (REPO_ROOT / "stack.toml")
    raw: dict = {}
    if toml_path.exists():
        with toml_path.open("rb") as f:
            raw = tomllib.load(f)

    paths = {**DEFAULT_PATHS, **raw.get("paths", {})}
    timeouts = {**DEFAULT_TIMEOUTS, **raw.get("timeouts", {})}
    if profile == "playground":
        ports = {**DEFAULT_PLAYGROUND_PORTS, **raw.get("playground", {}).get("ports", {})}
    else:
        ports = {**DEFAULT_PORTS, **raw.get("ports", {})}

    resolved = {}
    for name, value in paths.items():
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = (REPO_ROOT / candidate).resolve()
        resolved[name] = candidate

    if validate:
        for name, candidate in resolved.items():
            if not candidate.is_dir():
                raise ConfigError(
                    f"stack.toml: sibling '{name}' is configured at {candidate}, but no such "
                    f"directory exists. Check out the sibling repo there, or edit stack.toml's "
                    f"[paths] table to point at it."
                )

    return StackConfig(
        keel_cloud=resolved["keel_cloud"],
        keel_web=resolved["keel_web"],
        keel_runtime=resolved["keel_runtime"],
        keel_connect_skill=resolved["keel_connect_skill"],
        postgres_port=int(ports["postgres"]),
        cloud_port=int(ports["cloud"]),
        web_port=int(ports["web"]),
        cloud_boot_timeout=int(timeouts["cloud_boot"]),
        web_boot_timeout=int(timeouts["web_boot"]),
        profile=profile,
    )
