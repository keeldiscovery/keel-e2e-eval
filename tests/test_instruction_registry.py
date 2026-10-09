"""`instructions/registry.py`: the registry the export carries, and its eight invariants (spec 029
FR-021, data-model §1, research R4; T011; at twelve keys by spec 030 T004, judgement calls 46-47).

The golden every v10 scorer checks a question against is only honest if it is itself well formed,
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


def test_the_slice_loads_and_passes_all_eight_invariants():
    registry = fx.registry()
    assert len(registry.keys()) == sum(registry_mod.PER_VECTOR.values()) == 12
    assert registry_mod.check_invariants(registry) == []


def test_a_vector_slice_is_its_dimensions_in_order():
    registry = fx.registry()
    problem = registry.slice("PROBLEM")
    assert [d.order for d in problem] == [1, 2, 3, 4]
    assert problem[0].key == "problem.prevalence"
    assert problem[-1].key == "problem.current_solution_satisfaction"
    assert len(registry.slice("SOLUTION")) == 3 and len(registry.slice("COMMERCIAL")) == 5


def test_the_nine_deal_breakers_are_the_registrys_and_every_one_can_fail():
    registry = fx.registry()
    for vector in registry_mod.VECTORS:
        assert registry.deal_breakers(vector) == list(registry_mod.DEAL_BREAKERS[vector])
        for key in registry.deal_breakers(vector):
            assert "NOT_HOLDING_UP" in registry.by_key(key).status_vocabulary


def test_the_calibrated_set_is_ten_on_b2c_and_twelve_on_b2b():
    """Call 47 (keel-cloud 071 `calibrated(b2b)`): the b2b_only pair only on a B2B persona."""
    registry = fx.registry()
    assert registry.b2b_only() == list(registry_mod.B2B_ONLY)
    b2c, b2b = registry.calibrated_keys(False), registry.calibrated_keys(True)
    assert (len(b2c), len(b2b)) == (10, 12)
    assert set(b2b) - set(b2c) == set(registry_mod.B2B_ONLY)
    assert [d.key for d in registry.calibrated_slice("COMMERCIAL", False)] == [
        "commercial.existing_sacrifice", "commercial.buyer_payer_alignment",
        "commercial.commitment"]
    assert len(registry.calibrated_slice("COMMERCIAL", True)) == 5


def test_plan_keys_are_per_part_and_link_less_what_the_founder_left_out():
    """Calls 30 and 47: PRIMARY asks 4 / 3 / 3 (3 / 3 / 3 after the gate), never the b2b_only
    pair; COMMERCIAL_B2B asks the commercial part whole, and only on a B2B persona."""
    registry = fx.registry()
    primary, b2b = registry_mod.LINK_PRIMARY, registry_mod.LINK_B2B
    calibration = {k: {"answer": "x"} for k in registry.keys()}
    for persona in (False, True):
        assert [len(registry.plan_keys(p, calibration, primary, persona))
                for p in (1, 2, 3)] == [4, 3, 3]
    assert registry.plan_keys(3, calibration, b2b, True) == registry.calibrated_keys(True)[-5:]
    assert registry.plan_keys(3, calibration, b2b, False) == []
    assert registry.plan_keys(1, calibration, b2b, True) == []
    calibration["problem.frequency"] = {"unsure": True}
    calibration["commercial.ability_to_pay"] = {"unsure": True}
    plan1 = registry.plan_keys(1, calibration)
    assert "problem.frequency" not in plan1 and len(plan1) == 3
    assert "commercial.ability_to_pay" not in registry.plan_keys(3, calibration, b2b, True)
    assert registry.link_of(3, True) == b2b and registry.link_of(3, False) == primary
    assert registry.link_of(1, True) == primary


def test_the_fixed_respondent_codes_are_the_registrys_one():
    registry = fx.registry()
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
    assert invariants == [1, 2, 3, 4, 5, 6, 7, 8]


def test_a_registry_still_carrying_asked_in_v1_is_refused_as_unknown_shaped():
    """Call 46: `asked_in_v1` is not read, and a registry carrying it is refused, not ignored."""
    document = copy.deepcopy(fx.registry_document())
    document["dimensions"][1]["respondent"]["asked_in_v1"] = True
    with pytest.raises(registry_mod.RegistryUnavailable) as refusal:
        registry_mod.from_document(document, source="v9.json")
    assert "asked_in_v1" in str(refusal.value)
    assert "problem.frequency" in str(refusal.value)


def test_the_v9_registry_of_twenty_five_is_refused_naming_invariant_1():
    """A 25-key registry (v9's shape) fails invariant 1 before anything is built against it."""
    document = copy.deepcopy(fx.registry_document())
    extra = copy.deepcopy(document["dimensions"][1])
    extra.update(key="problem.duration", order=5)
    document["dimensions"].insert(4, extra)
    faults = registry_mod.check_invariants(registry_mod.from_document(document, check=False))
    assert any(f.startswith("invariant 1 ") for f in faults), faults


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


def test_the_manifest_names_the_registry_file_as_058_writes_it(tmp_path):
    fx.write_export(tmp_path, with_registry=False)
    (tmp_path / "registry-under-another-name.json").write_text(json.dumps(fx.registry_document()))
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    manifest["dimension_registry"] = "registry-under-another-name.json"
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    assert len(contract_mod.read(tmp_path).registry.keys()) == 12


def test_the_window_placeholders_are_filled_by_code():
    assert registry_mod.fill_window({"g": ["in {window}, in {window_unit}"]}) == \
        {"g": ["in the last 7 nights, in nights out of 7"]}
    months = registry_mod.RecallWindow(3, "MONTHS")
    assert registry_mod.fill_window("in {window}", months) == "in the last 3 months"


@pytest.mark.parametrize("raw, words, unit", [
    ({"count": 7, "unit": "NIGHTS"}, "the last 7 nights", "nights out of 7"),
    ({"count": 3, "unit": "MONTHS"}, "the last 3 months", "months out of 3"),
    ({"count": 1, "unit": "SHIFTS"}, "the last shift", "shifts out of 1"),
    ({"count": 5, "unit": "WORKING_DAYS"}, "the last 5 working days", "working days out of 5"),
    ("LAST_CYCLE", "the last cycle", "cycles out of 1"),
])
def test_a_recall_window_renders_as_keel_cloud_058s_record_does(raw, words, unit):
    """`RecallWindow.words()` / `unit()` (058 `cb0422a`): a count of 1 drops the number, and
    `{window_unit}` is the plural out of the count; a legacy enum name is upcast."""
    window = registry_mod.RecallWindow.read(raw)
    assert (window.words(), window.unit_words()) == (words, unit)


def test_a_recall_window_is_named_the_ways_c7_accepts_and_refused_when_unreadable():
    seven = registry_mod.RecallWindow(7, "NIGHTS")
    assert seven.is_named_in("In the last SEVEN NIGHTS, did it happen?")
    assert seven.is_named_in("in the past week") and not seven.is_named_in("recently")
    shift = registry_mod.RecallWindow(1, "SHIFTS")
    assert shift.is_named_in("On your most recent shift") and not shift.is_named_in("1 shifts")
    assert registry_mod.RecallWindow(3, "MONTHS").is_named_in("in the last quarter")
    assert registry_mod.RecallWindow.read(None) is None
    for bad in ({"count": 0, "unit": "NIGHTS"}, {"count": 2, "unit": "YEARS"},
                {"count": 1.5, "unit": "DAYS"}, "FORTNIGHT"):
        with pytest.raises(ValueError):
            registry_mod.RecallWindow.read(bad)
