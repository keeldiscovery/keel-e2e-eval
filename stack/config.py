"""Loads stack.toml (data-model.md): sibling paths, ports, timeouts -- with working defaults and
clear errors when a sibling checkout is missing.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
from urllib.parse import urlsplit

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_PATHS = {
    "keel_cloud": "../keel-cloud",
    "keel_web": "../keel-web",
    "keel_runtime": "../keel-runtime",
    "keel_connect_skill": "../keel-connect-skill",
}
DEFAULT_PORTS = {"postgres": 55432, "cloud": 18080, "web": 5173, "oidc": 18090}
DEFAULT_TIMEOUTS = {"cloud_boot": 120, "web_boot": 60}

# Split-stacks (relay-design.md §12.5, the account-collision incident): the playground profile's
# own ports, used only when `load_config(profile="playground")` is asked for -- the default
# ("eval") profile's own ports above are entirely unchanged. `stack/postgres.py` also puts the
# playground profile in its own Compose *project* (never the eval profile's default project), so
# an eval `make down` can never see, let alone drop, the playground's own container or volume.
DEFAULT_PLAYGROUND_PORTS = {"postgres": 55433, "cloud": 18081, "web": 5174, "oidc": 18091}

#: The third profile (spec 017; keel-cloud `canon/designs/e2e-matrix-design.md` §11). `eval` and
#: `playground` *start* Postgres, keel-cloud, keel-web and the stub as local processes; `remote`
#: starts nothing at all and only **names** three URLs that already answer -- the staging twin, or
#: any other deployment a founder points it at. The referee is not modified to accommodate a
#: deployment: the two local profiles are untouched, byte for byte, and this one adds a third
#: column beside them.
REMOTE_PROFILE = "remote"
PROFILES = ("eval", "playground", REMOTE_PROFILE)

#: What the remote profile reads, and the whole of its configuration. Nothing here is a secret of
#: this repository's: the gate password is the caller's own shell variable (a GitHub secret on a
#: runner, a password manager on the founder's Mac) and is never written to a file by anything
#: here.
REMOTE_WEB_URL_VAR = "KEEL_REMOTE_WEB_URL"
REMOTE_CLOUD_URL_VAR = "KEEL_REMOTE_CLOUD_URL"
REMOTE_OIDC_URL_VAR = "KEEL_REMOTE_OIDC_URL"
REMOTE_GATE_USER_VAR = "KEEL_REMOTE_GATE_USER"
REMOTE_GATE_PASSWORD_VAR = "KEEL_REMOTE_GATE_PASSWORD"  # noqa: S105 - a variable name
#: Optional, and only cosmetic: the cell this run is (`ubuntu-copilot-py3.13`), which names the
#: identity `stack/remote.py:register_cell_identity` registers so the founder's picker reads as
#: the log they asked for (§4.3). A run that does not set it is "local".
REMOTE_CELL_VAR = "KEEL_REMOTE_CELL"


def remote_urls(env: Mapping[str, str] | None = None) -> dict[str, str]:
    """The three base URLs the remote profile talks to (§11).

    `KEEL_REMOTE_WEB_URL` is required and the other two default from it, because on the staging
    twin one Caddy serves all three: keel-web at the root, keel-cloud's `/v2/*` behind the same
    origin, and the stub issuer at `/oidc` (§3). A deployment that splits them names them.
    """
    env = os.environ if env is None else env
    web = (env.get(REMOTE_WEB_URL_VAR) or "").strip().rstrip("/")
    if not web:
        raise ConfigError(
            f"the remote profile needs {REMOTE_WEB_URL_VAR} -- the keel-web origin to run "
            f"against (e.g. https://eval.keeldiscovery.com). "
            f"{REMOTE_CLOUD_URL_VAR} defaults to it and {REMOTE_OIDC_URL_VAR} to <web>/oidc.")
    cloud = (env.get(REMOTE_CLOUD_URL_VAR) or web).strip().rstrip("/")
    oidc = (env.get(REMOTE_OIDC_URL_VAR) or f"{web}/oidc").strip().rstrip("/")
    return {"web": web, "cloud": cloud, "oidc": oidc}


def remote_gate(env: Mapping[str, str] | None = None) -> tuple[str, str] | None:
    """The basic-auth credential Caddy stands in front of the stub's `/authorize` with (§4.2),
    or `None` when this run is not going through a gate at all.

    **Half a credential is an error, not a `None`.** A `KEEL_REMOTE_GATE_USER` with no password
    would read on the wire as an anonymous request and come back 401 from Caddy, which is a
    confusing way to learn that a variable was misspelled.
    """
    env = os.environ if env is None else env
    user = (env.get(REMOTE_GATE_USER_VAR) or "").strip()
    password = env.get(REMOTE_GATE_PASSWORD_VAR) or ""
    if not user and not password:
        return None
    if not user or not password:
        raise ConfigError(
            f"{REMOTE_GATE_USER_VAR} and {REMOTE_GATE_PASSWORD_VAR} are set together or not at "
            f"all -- one without the other reaches the gate as an anonymous request")
    return (user, password)


def _port_of(url: str, default: int = 0) -> int:
    """The port a URL names, or the one its scheme implies. The remote profile has no local
    ports; these exist so a `StackConfig` is still a `StackConfig` and a caller that prints one
    has something true to print."""
    parts = urlsplit(url)
    if parts.port:
        return parts.port
    return 443 if parts.scheme == "https" else (80 if parts.scheme == "http" else default)


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
    # Defaulted, and last, so a StackConfig built by hand before this feature still constructs:
    # the stub OIDC issuer's port (spec 015; keel-cloud google-sign-in-design.md 10.3) -- eval
    # 18090, playground 18091, fixed per profile like every other port here.
    oidc_port: int = 18090
    profile: str = "eval"
    # Spec 017, and empty on both local profiles: the remote profile's three base URLs and the
    # gate credential in front of its issuer. Empty means "derive it from this profile's port",
    # which is what the two properties below do -- so every existing caller of
    # `cloud_base_url` reads exactly what it read before.
    web_url: str = ""
    cloud_url: str = ""
    oidc_url: str = ""
    gate_user: str = ""
    gate_password: str = ""

    @property
    def connect_check_script_path(self) -> Path:
        """keel-connect-skill's own script (contracts/skill-script-output.md) -- the only thing
        this stack ever launches keel-runtime through (spec 005 edge case: never `python3 -m
        keel_runtime` directly, so the connect skill stays under referee)."""
        return self.keel_connect_skill / "scripts" / "keel_connect_check.py"

    @property
    def disconnect_script_path(self) -> Path:
        """keel-connect-skill's own way *out* (its spec `002-keel-disconnect`,
        contracts/skill-disconnect-output.md). Spec 012: `make down` stops the runtime by asking
        the same script a founder's "keel disconnect" asks, instead of signalling a pid.

        It may not exist yet -- spec 002 is being written in that repo as this one lands -- so
        `stack.runtime.disconnect` treats it as *preferred, not required* and falls back to the
        bundled runtime's own `disconnect` subcommand, which is the command this script shells
        anyway. Both answer the same four runtime outcomes.
        """
        return self.keel_connect_skill / "scripts" / "keel_disconnect.py"

    @property
    def bundled_runtime_path(self) -> Path:
        """The runtime that **travelled inside the skill** -- `<skill root>/keel_runtime/`, put
        there by `make -C ../keel-connect-skill runtime` and gitignored in that repo (keel-cloud
        `canon/designs/keel-skill-design.md` §3.1, invariant D2).

        This is the runtime a founder runs, so from spec 012 on it is the runtime the referee
        runs: `stack/runtime.py` reads `status` from it and the connect script resolves it with no
        `KEEL_RUNTIME_PATH` in the environment at all (T-1). `keel_runtime` -- the *checkout* --
        stays configured for the things that read keel-runtime's **source** rather than run it
        (`harness/canary.py`'s caps, `instructions/prompts.py`'s `build_prompt`).
        """
        return self.keel_connect_skill / "keel_runtime"

    @property
    def skill_dist_path(self) -> Path:
        """`<keel-connect-skill>/dist/` -- the four packaging trees `make dist` writes and that
        repo gitignores (keel-cloud `canon/designs/keel-skill-design.md` §8.1).

        Spec `013-skill-distribution` (S-009) installs each of them into a fresh, temporary,
        Claude-Code-shaped home and runs the skill's own script out of the result: the question
        A-6 asks is *does a copied skill still work after an installer moved it*, and it can only
        be answered against the bytes a build wrote, never against a working tree. Like the
        bundled runtime this is **gated on and never built here** -- `make dist` writes into a
        sibling repository, and this repo owns no product code.
        """
        return self.keel_connect_skill / "dist"

    @property
    def cloud_base_url(self) -> str:
        """The Keel this profile's runtime talks to -- `http://localhost:18080` on eval,
        `:18081` on playground, and `KEEL_REMOTE_CLOUD_URL` on remote. Named on the `connect` the
        skill launches, and written into the runtime home's own `config.json` (spec 012 FR-004),
        so an ambient `KEEL_BASE_URL` from the operator's shell can never decide which Keel a
        run's `status` describes."""
        return self.cloud_url or f"http://localhost:{self.cloud_port}"

    @property
    def web_base_url(self) -> str:
        """Where the founder's own screens are: `http://localhost:5173` on eval, `:5174` on
        playground, `KEEL_REMOTE_WEB_URL` on remote."""
        return self.web_url or f"http://localhost:{self.web_port}"

    @property
    def oidc_base_url(self) -> str:
        """The issuer keel-cloud is pointed at: `http://localhost:18090` on eval, `:18091` on
        playground, `KEEL_REMOTE_OIDC_URL` (default `<web>/oidc`) on remote."""
        return self.oidc_url or f"http://localhost:{self.oidc_port}"

    @property
    def is_remote(self) -> bool:
        """`make up` starts nothing and `make down` stops nothing for this profile; it names
        three URLs that already answer (spec 017)."""
        return self.profile == REMOTE_PROFILE

    @property
    def gate_credential(self) -> tuple[str, str] | None:
        """The basic-auth pair for the issuer's origin, or `None` -- which is every local run and
        every remote run against a deployment with no gate in front of it (§4.2). It is carried
        by Playwright's browser context (`harness/browser.py`) and by the browserless sign-in
        (`stack/auth.py`), and by nothing else: keel-cloud's own routes are not behind it."""
        return (self.gate_user, self.gate_password) if self.gate_user else None


def load_config(toml_path: Path | None = None, *, validate: bool = True,
                 profile: str = "eval", env: Mapping[str, str] | None = None) -> StackConfig:
    """Loads stack.toml, applying defaults for any missing table/key.

    `profile` selects which port set this config carries (split-stacks, relay-design.md §12.5):
    "eval" (the default, unchanged) reads `[ports]`; "playground" reads `[playground.ports]`,
    falling back to `DEFAULT_PLAYGROUND_PORTS` for anything unset. Every other table (paths,
    timeouts) is shared between profiles -- only ports (and, in stack/postgres.py, the Compose
    project) differ.

    **"remote" reads no ports at all** (spec 017): its three base URLs come from `env` (the
    process environment unless a mapping is handed in, which is how the tests ask), and the ports
    it carries are the ones those URLs name. `env` is ignored entirely on the two local profiles,
    so an operator whose shell still exports `KEEL_REMOTE_WEB_URL` from a staging run cannot have
    their next `make eval` quietly pointed at staging.

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

    # The remote profile reads the environment rather than `[ports]`: it starts nothing, so a
    # port here would be a fiction. The ports it does carry are the ones its own URLs name, so a
    # printed config says something true (spec 017).
    urls = {"web": "", "cloud": "", "oidc": ""}
    gate: tuple[str, str] | None = None
    if profile == REMOTE_PROFILE:
        urls = remote_urls(env)
        gate = remote_gate(env)
        ports = {
            "postgres": 0,
            "cloud": _port_of(urls["cloud"]),
            "web": _port_of(urls["web"]),
            "oidc": _port_of(urls["oidc"]),
        }

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
        oidc_port=int(ports["oidc"]),
        cloud_boot_timeout=int(timeouts["cloud_boot"]),
        web_boot_timeout=int(timeouts["web_boot"]),
        profile=profile,
        web_url=urls["web"],
        cloud_url=urls["cloud"],
        oidc_url=urls["oidc"],
        gate_user=(gate[0] if gate else ""),
        gate_password=(gate[1] if gate else ""),
    )
