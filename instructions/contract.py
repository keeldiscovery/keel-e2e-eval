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

# MARKS_VERSION 9 (spec 029 FR-016/FR-021, data-model §4): the eight subjects of the vector
# redesign. Seven are model screens; `COMPARE` is keel-cloud's engine, shelled, and never a call.
# `*_ASSUMPTIONS` and `QUESTIONS` are gone with the subjects they named (judgement call 28).
SCREEN_CONTEXT_INTERPRET = "CONTEXT_INTERPRET"
SCREEN_PROBLEM_INTERPRET = "PROBLEM_INTERPRET"
SCREEN_SOLUTION_MECHANISM = "SOLUTION_MECHANISM"
SCREEN_CALIBRATION = "CALIBRATION_QUESTIONS"
SCREEN_RESPONDENT = "RESPONDENT_QUESTIONS"
# A-1: the anchor read keeps today's constant, narrowed to the gate story. There is no ANCHOR_READ.
SCREEN_INTERPRET = "INTERPRET"
SCREEN_READING = SCREEN_INTERPRET
SCREEN_COMPARE = "COMPARE"
# The screen nobody asks for -- keel-cloud starts it by itself once the answers are read.
SCREEN_BRIEF = "BRIEF"

#: The seven screens a model answers, in the order a run builds them (FR-016).
MODEL_SCREENS = (SCREEN_CONTEXT_INTERPRET, SCREEN_PROBLEM_INTERPRET, SCREEN_SOLUTION_MECHANISM,
                 SCREEN_CALIBRATION, SCREEN_RESPONDENT, SCREEN_INTERPRET, SCREEN_BRIEF)

#: The exporter's new fourth file (keel-cloud 058, research R4), read into `ExportedContract.registry`.
REGISTRY_NAME = "dimension-registry.json"


class ContractUnavailable(RuntimeError):
    """keel-cloud could not be asked for its contract -- a reason to stop, never a score."""


@dataclass(frozen=True)
class ExportedContract:
    directory: Path
    contracts: dict          # SCREEN -> {allowed_outcomes, completed_result_schema, needs_input_schema?}
    context_keys: dict       # SCREEN -> [key, ...]  ordered; the order is the contract
    manifest: dict
    #: The optional fourth file, `model-routing.json` -- keel-cloud's own model-routing table
    #: (canon/designs/model-routing-design.md §4), exported beside the contracts so a run of
    #: record can say it measured the cloud's table and not a file of its own. `None` on an
    #: export older than that design; `instructions.models.select("exported", ...)` refuses then.
    model_routing: dict | None = None
    #: `dimension-registry.json` -- keel-cloud 058's export of the 25-dimension registry, checked
    #: against its seven invariants on the way in (`instructions/registry.py`). `read` refuses an
    #: export without it, so on any contract a case is built from this is never `None`.
    registry: object = None

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
    """Reads an already-exported directory -- the same files, no Gradle.

    **`dimension-registry.json` is required** (spec 029 FR-021): the registry is the golden every
    v9 scorer checks a question against, so an export without it is a refusal to start naming the
    file and keel-cloud 058 -- before any case is built -- and a registry failing one of its seven
    invariants is a refusal naming the invariant and the key.
    """
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
    routing_path = directory / "model-routing.json"
    model_routing = None
    if routing_path.is_file():
        model_routing = json.loads(routing_path.read_text(encoding="utf-8"))
        if not isinstance(model_routing, dict):
            raise ContractUnavailable(f"{routing_path} is not a JSON object")
    registry_path = directory / REGISTRY_NAME
    if not registry_path.is_file():
        raise ContractUnavailable(
            f"{directory} carries no {REGISTRY_NAME} -- keel-cloud 058's exporter writes it beside "
            "model-routing.json, and MARKS_VERSION 9 scores every question against it (spec 029 "
            "FR-021). Check out keel-cloud on 058's branch, or wait for it to land.")
    from . import registry as registry_mod                    # noqa: PLC0415
    try:
        registry = registry_mod.load(registry_path)
    except registry_mod.RegistryUnavailable as reason:
        raise ContractUnavailable(str(reason)) from reason
    return ExportedContract(directory=directory, contracts=contracts,
                            context_keys=context_keys, manifest=manifest,
                            model_routing=model_routing, registry=registry)
