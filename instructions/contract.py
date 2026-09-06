"""keel-cloud's own response contracts and context key lists (spec 009 FR-002).

Nothing here is a copy. The contract is produced by keel-cloud's own exporter --
`./gradlew -q screenContracts --args="export <dir>"`, spec 029's
`contracts/exported-contract-format.md` -- and read back whole, so a screen that gains a key or a
field makes this eval build a different prompt without anyone editing this file. That is the
intended behaviour: this repo floats at sibling HEAD, and a referee pinned to the past cannot call
the present.

A missing Gradle task, or a non-zero exit, is a **refusal to start** that names the prerequisite.
It is never a score: an eval that could not ask keel-cloud what its contract is has not measured a
bad instruction, it has measured nothing.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

SCREENS_ASSUMPTIONS = {
    "PROBLEM": "PROBLEM_ASSUMPTIONS",
    "SOLUTION": "SOLUTION_ASSUMPTIONS",
    "COMMERCIAL": "COMMERCIAL_ASSUMPTIONS",
}
SCREEN_READING = "INTERPRET"


class ContractUnavailable(RuntimeError):
    """keel-cloud could not be asked for its contract -- a reason to stop, never a score."""


@dataclass(frozen=True)
class ExportedContract:
    directory: Path
    contracts: dict          # SCREEN -> {allowed_outcomes, completed_result_schema, needs_input_schema?}
    context_keys: dict       # SCREEN -> [key, ...]  ordered; the order is the contract
    manifest: dict

    def for_screen(self, screen: str) -> dict:
        try:
            return self.contracts[screen]
        except KeyError:
            raise ContractUnavailable(
                f"keel-cloud's export carries no contract for {screen}") from None

    def keys_for(self, screen: str) -> list:
        try:
            return list(self.context_keys[screen])
        except KeyError:
            raise ContractUnavailable(
                f"keel-cloud's export carries no context keys for {screen}") from None


def export(keel_cloud: Path, into: Path, *, timeout_s: float = 600.0) -> ExportedContract:
    """Runs keel-cloud's exporter into `into` and reads the three files back."""
    keel_cloud = Path(keel_cloud)
    into = Path(into)
    gradlew = keel_cloud / "gradlew"
    if not gradlew.is_file():
        raise ContractUnavailable(
            f"no {gradlew} -- this eval needs the keel-cloud checkout named in stack.toml")

    into.mkdir(parents=True, exist_ok=True)
    argv = [str(gradlew), "-q", "screenContracts", "--args=export " + str(into.resolve())]
    try:
        done = subprocess.run(argv, cwd=str(keel_cloud), capture_output=True, text=True,
                              timeout=timeout_s)
    except (OSError, subprocess.SubprocessError) as exc:
        raise ContractUnavailable(f"could not run keel-cloud's exporter: {exc}") from exc
    if done.returncode != 0:
        raise ContractUnavailable(
            "keel-cloud's `screenContracts` task failed -- this eval needs keel-cloud spec 029's "
            "exporter (its `contracts/exported-contract-format.md`) on the checked-out branch.\n"
            + (done.stderr.strip() or done.stdout.strip())[-4000:])

    return read(into)


def read(directory: Path) -> ExportedContract:
    """Reads an already-exported directory -- the same three files, no Gradle."""
    directory = Path(directory)
    manifest_path = directory / "manifest.json"
    keys_path = directory / "context-keys.json"
    if not manifest_path.is_file() or not keys_path.is_file():
        raise ContractUnavailable(
            f"{directory} is not an exported contract: expected manifest.json and "
            "context-keys.json beside a contracts/ directory")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    context_keys = json.loads(keys_path.read_text(encoding="utf-8"))
    contracts = {}
    for screen in manifest.get("screens") or []:
        path = directory / "contracts" / f"{screen}.json"
        if not path.is_file():
            raise ContractUnavailable(f"the manifest names {screen} but {path} is missing")
        contracts[screen] = json.loads(path.read_text(encoding="utf-8"))
    return ExportedContract(directory=directory, contracts=contracts,
                            context_keys=context_keys, manifest=manifest)
