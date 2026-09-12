"""Every scenario reaches the stack through the profile's own addresses, never `localhost:<port>`.

**The harness fault this exists to stop happening twice.** The nightly of 2026-09-12 (run
34660286884) was the first time S-005/6/7 and S-013 rode a cell on the `remote` profile. All four
failed in a third of a second, at sign-in, with `ERR_CONNECTION_REFUSED at
http://localhost:443/login`: each one built its base URLs as `f"http://localhost:{stack.web_port}"`,
which is right on the eval and playground profiles and meaningless on the twin, where the port is
443 and the host is eval.keeldiscovery.com. `StackConfig.web_base_url` and `cloud_base_url` have
said the right thing on every profile since spec 017; S-012 read them, nothing else did.

Two things are read statically, the way `test_scenarios_have_no_undefined_names.py` reads names:

1. no scenario module spells a stack address out of a port;
2. every scenario a `remote`-capable set may run signs in as the identity `remote.identity_to_sign_in_as`
   hands it -- this cell's own registered founder on the twin, the built-in Eval Founder anywhere
   else -- because the twin's gated chooser lists registered founders and nothing else.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
EVALS = REPO / "evals"
CELLS = REPO / "matrix" / "cells.toml"

PORT_ADDRESS = re.compile(r"""http://localhost:\{(stack|config|stack_config)\.(web|cloud|oidc)_port\}""")


def _scenario_modules() -> list[Path]:
    return sorted(p for p in EVALS.glob("*.py") if p.name != "conftest.py")


@pytest.mark.parametrize("module", _scenario_modules(), ids=lambda p: p.name)
def test_no_scenario_builds_an_address_from_a_port(module: Path):
    text = module.read_text(encoding="utf-8")
    hits = [line.strip() for line in text.splitlines() if PORT_ADDRESS.search(line)]
    assert not hits, (
        f"{module.name} builds a stack address from a port; read `stack.web_base_url` / "
        f"`stack.cloud_base_url` instead, which are the twin's URLs on the remote profile:\n  "
        + "\n  ".join(hits))


def _scenarios_in_remote_sets() -> set[str]:
    """Every scenario id any set in cells.toml names explicitly (the sets are what the matrix runs
    on the twin), plus the default S-012 every cell runs."""
    doc = tomllib.loads(CELLS.read_text(encoding="utf-8"))
    ids: set[str] = {"s012"}
    for cells in doc.get("sets", {}).values():
        for cell in cells:
            ids.update(cell.get("scenarios") or [])
    return ids


def _module_for(scenario_id: str) -> Path:
    matches = sorted(EVALS.glob(f"test_{scenario_id}_*.py"))
    assert len(matches) == 1, f"{scenario_id}: expected one module, found {matches}"
    return matches[0]


def _body_of(module: Path) -> str:
    """The module and, for the corpus trio, the shared body they delegate to."""
    text = module.read_text(encoding="utf-8")
    if "corpus_scenario.run(" in text:
        text += (EVALS / "corpus_scenario.py").read_text(encoding="utf-8")
    return text


@pytest.mark.parametrize("scenario_id", sorted(_scenarios_in_remote_sets()))
def test_a_scenario_the_matrix_runs_signs_in_as_the_cells_own_founder(scenario_id: str):
    text = _body_of(_module_for(scenario_id))
    assert "remote.identity_to_sign_in_as(" in text, (
        f"{scenario_id} is in a matrix set but signs in as the built-in founder; on the twin it "
        "must sign in as `remote.identity_to_sign_in_as(stack, <label>, fallback=founder_one)`")


def test_the_corpus_scenarios_start_from_a_fresh_runtime_home_on_the_twin():
    """Run 34662465285: with per-scenario founders on the twin, a runtime home carrying the
    previous scenario's credential reconnects as the previous founder's device, and the next
    founder's project-name field is disabled. The shared corpus body resets the home on `remote`
    before it starts the runtime, the way S-013 does unconditionally."""
    text = (EVALS / "corpus_scenario.py").read_text(encoding="utf-8")
    before_start = text.split("start_runtime_via_skill(stack, recorder,", 1)[0]
    assert "stack_runtime.reset(stack)" in before_start, (
        "corpus_scenario.run must reset the runtime home (on the remote profile) before "
        "start_runtime_via_skill, or the second founder inherits the first founder's device")
