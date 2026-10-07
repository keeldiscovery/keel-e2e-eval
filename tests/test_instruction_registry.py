"""`instructions/registry.py`: the registry the export carries, and its seven invariants (spec 029
FR-021, data-model §1, research R4; T011).

The golden every v9 scorer checks a question against is only honest if it is itself well formed,
so each invariant is made to fail once, on its own, by a one-value patch of the hand-sized slice
(`tests/fixtures/registry/broken/`), and the refusal must name the invariant and the key.
"""

from __future__ import annotations

import copy
import json

import pytest
import yaml

from instructions import contract as contract_mod
from instructions import registry as registry_mod
from tests import v9_fixtures as fx


def test_the_slice_loads_and_passes_all_seven_invariants():
    registry = fx.registry()
    assert len(registry.keys()) == 25
    assert registry_mod.check_invariants(registry) == []


def test_a_vector_slice_is_its_dimensions_in_order():
    registry = fx.registry()
    problem = registry.slice("PROBLEM")
    assert [d.order for d in problem] == list(range(1, 10))
    assert problem[0].key == "problem.prevalence" and problem[-1].key == "problem.urgency"
    assert len(registry.slice("SOLUTION")) == 9 and len(registry.slice("COMMERCIAL")) == 7


def test_plan_keys_are_asked_in_v1_by_part_less_what_the_founder_left_out():
    registry = fx.registry()
    calibration = {k: {"answer": "x"} for k in registry.keys()}
    assert [len(registry.plan_keys(p, calibration)) for p in (1, 2, 3)] == [8, 9, 6]
    calibration["problem.severity"] = {"unsure": True}
    calibration["solution.trialability"] = {"unsure": True}
    plan1 = registry.plan_keys(1, calibration)
    assert "problem.severity" not in plan1 and len(plan1) == 7
    assert len(registry.plan_keys(2, calibration)) == 8
    assert "problem.urgency" not in plan1, "not asked in V1, whatever the founder said"


def test_the_fixed_respondent_codes_are_the_registrys_three():
    registry = fx.registry()
    assert registry.fixed_respondent_codes("solution.trust_risk") == ["own_instinct"]
    assert registry.fixed_respondent_codes("commercial.commitment") == ["nothing_yet"]
    assert registry.fixed_respondent_codes("problem.frequency") == []


def _patched(name: str) -> tuple[dict, dict]:
    patch = yaml.safe_load((fx.BROKEN / name).read_text(encoding="utf-8"))
    document = copy.deepcopy(fx.registry_document())
    dimension = next(d for d in document["dimensions"] if d["key"] == patch["key"])
    target = dimension
    for step in patch["path"][:-1]:
        target = target[step]
    target[patch["path"][-1]] = patch["value"]
    return document, patch


@pytest.mark.parametrize("name", sorted(p.name for p in fx.BROKEN.glob("*.yaml")))
def test_each_broken_registry_fails_exactly_its_own_invariant_naming_the_key(name):
    document, patch = _patched(name)
    faults = registry_mod.check_invariants(registry_mod.from_document(document, check=False))
    assert faults, name
    assert all(f.startswith(f"invariant {patch['invariant']} ") for f in faults), faults
    assert any(patch["key"] in f for f in faults), faults
    with pytest.raises(registry_mod.RegistryUnavailable) as refusal:
        registry_mod.from_document(document, source=name)
    assert f"invariant {patch['invariant']}" in str(refusal.value)


def test_there_is_one_broken_fixture_per_invariant():
    invariants = sorted(yaml.safe_load(p.read_text())["invariant"] for p in fx.BROKEN.glob("*.yaml"))
    assert invariants == [1, 2, 3, 4, 5, 6, 7]


def test_a_document_that_is_not_a_registry_is_refused_by_name():
    with pytest.raises(registry_mod.RegistryUnavailable) as refusal:
        registry_mod.from_document({"screens": []}, source="x.json")
    assert "x.json" in str(refusal.value)


def test_an_export_without_the_registry_is_refused_naming_the_file_and_058(tmp_path):
    fx.write_export(tmp_path, with_registry=False)
    with pytest.raises(contract_mod.ContractUnavailable) as refusal:
        contract_mod.read(tmp_path)
    assert "dimension-registry.json" in str(refusal.value)
    assert "058" in str(refusal.value)


def test_an_export_with_a_broken_registry_is_refused_naming_the_invariant(tmp_path):
    fx.write_export(tmp_path)
    document, _patch = _patched("7-gate.yaml")
    (tmp_path / "dimension-registry.json").write_text(json.dumps(document))
    with pytest.raises(contract_mod.ContractUnavailable) as refusal:
        contract_mod.read(tmp_path)
    assert "invariant 7" in str(refusal.value)


def test_an_export_with_the_registry_carries_it_checked(tmp_path):
    fx.write_export(tmp_path)
    exported = contract_mod.read(tmp_path)
    assert exported.registry.by_key("problem.prevalence").respondent["control"] == "gate_yes_no"
    assert exported.registry.version == 1
