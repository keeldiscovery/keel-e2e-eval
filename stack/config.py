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
    "keel_skill": "../keel-skill",
}
DEFAULT_PORTS = {"postgres": 55432, "cloud": 18080, "web": 5173}
DEFAULT_TIMEOUTS = {"cloud_boot": 120, "web_boot": 60}


class ConfigError(RuntimeError):
    """Raised for a stack.toml problem a human must fix before anything can boot."""


@dataclass(frozen=True)
class StackConfig:
    keel_cloud: Path
    keel_web: Path
    keel_skill: Path
    postgres_port: int
    cloud_port: int
    web_port: int
    cloud_boot_timeout: int
    web_boot_timeout: int

    @property
    def skill_md_path(self) -> Path:
        return self.keel_skill / "SKILL.md"


def load_config(toml_path: Path | None = None, *, validate: bool = True) -> StackConfig:
    """Loads stack.toml, applying defaults for any missing table/key.

    Raises ConfigError naming the missing sibling directory when `validate` is True and a
    configured path does not exist -- an operator agent should see "no such directory" once,
    with the path it looked for, rather than a stack trace three layers down.
    """
    toml_path = toml_path or (REPO_ROOT / "stack.toml")
    raw: dict = {}
    if toml_path.exists():
        with toml_path.open("rb") as f:
            raw = tomllib.load(f)

    paths = {**DEFAULT_PATHS, **raw.get("paths", {})}
    ports = {**DEFAULT_PORTS, **raw.get("ports", {})}
    timeouts = {**DEFAULT_TIMEOUTS, **raw.get("timeouts", {})}

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
        keel_skill=resolved["keel_skill"],
        postgres_port=int(ports["postgres"]),
        cloud_port=int(ports["cloud"]),
        web_port=int(ports["web"]),
        cloud_boot_timeout=int(timeouts["cloud_boot"]),
        web_boot_timeout=int(timeouts["web_boot"]),
    )
