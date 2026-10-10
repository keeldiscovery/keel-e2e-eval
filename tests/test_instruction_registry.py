"""`instructions/registry.py`: the registry the export carries, and its eight invariants (spec 029
FR-021, data-model §1, research R4; T011; at twelve keys by spec 030 T004, judgement calls 46-47;
at thirteen by spec 031 T004, judgement call 50; cost first by spec 032 T002, judgement call 59).

The golden every v12 scorer checks a question against is only honest if it is itself well formed,
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
    assert len(registry.keys()) == sum(registry_mod.PER_VECTOR.values()) == 13
    assert registry_mod.check_invariants(registry) == []


def test_a_vector_slice_is_its_dimensions_in_order():
    registry = fx.registry()
    problem = registry.slice("PROBLEM")
    assert [d.order for d in problem] == [1, 2, 3, 4]
    assert problem[0].key == "problem.prevalence"
    assert problem[-1].key == "problem.current_solution_satisfaction"
    assert len(registry.slice("SOLUTION")) == 3 and len(registry.slice("COMMERCIAL")) == 6
    assert registry.slice("COMMERCIAL")[1].key == registry_mod.PRICE_KEY


def test_price_is_shapes_asked_of_whoever_pays_over_the_costs_five_periods():
    """Call 59 (keel-cloud 074, registry decision 16): Price at order 2, SHAPES, not b2b_only, a price_range
    over day · week · month · quarter · year, a price_ladder item, ordinal_band."""
    registry = fx.registry()
    price = registry.by_key(registry_mod.PRICE_KEY)
    assert (price.order, price.weight, price.b2b_only) == (2, "SHAPES", False)
    assert price.founder_price and price.respondent_code_written and not price.founder_numeric
    assert tuple(price.normalized["periods"]) == registry_mod.PRICE_PERIODS == registry_mod.PERIODS
    assert price.answers["compare_rule"] == "ordinal_band" and price.part == 3
    assert "would_not_pay" in registry_mod.RESPONDENT_ESCAPES


def test_existing_sacrifice_is_a_cost_estimate_read_as_an_interval():
    """Call 59: `cost_estimate` over the five periods and the modes AMOUNT / HOURS, `cost_total` (call 67)
    yields a number so it is drawn as an interval, read by `interval_contains_median`; no kinds anywhere."""
    sacrifice = fx.registry().by_key(registry_mod.SACRIFICE_KEY)
    assert sacrifice.founder_cost and sacrifice.founder_code_framed and not sacrifice.derived
    assert tuple(sacrifice.normalized["periods"]) == registry_mod.PERIODS
    assert tuple(sacrifice.normalized["modes"]) == registry_mod.COST_MODES
    assert sacrifice.respondent["control"] == registry_mod.COST_TOTAL_CONTROL == "cost_total"
    assert registry_mod.COST_TOTAL_CONTROL in registry_mod.NUMBER_YIELDING_CONTROLS
    assert registry_mod.COST_TOTAL_CONTROL not in registry_mod.NUMERIC_RESPONDENT_CONTROLS
    assert "code_rule" not in sacrifice.normalized and sacrifice.respondent_code_written
    assert sacrifice.respondent["chips"] == ["It cost us nothing", "I can't recall", "That's a rough guess"]
    assert sacrifice.answers["shape"] == "interval"
    assert sacrifice.answers["compare_rule"] == "interval_contains_median"


def test_ability_to_pay_is_derived_and_asked_on_the_decision_makers_link_only():
    """Call 59: `derived` (a price_cost_ratio from the cost and the price), `cost_covers_price`,
    b2b_link_only, calibrated on every persona; the four rungs stay the budget source's codes."""
    ability = fx.registry().by_key(registry_mod.ABILITY_KEY)
    assert ability.derived and ability.founder_code_framed and ability.b2b_link_only
    assert not ability.b2b_only
    assert ability.normalized["kind"] == "price_cost_ratio"
    assert ability.normalized["from"] == [registry_mod.SACRIFICE_KEY, registry_mod.PRICE_KEY]
    assert ability.answers["compare_rule"] == registry_mod.DERIVED_COMPARE_RULE
    assert ability.respondent["codes"] == [
        "existing_line", "new_line_signed_off", "taken_from_other_spend", "no_budget"]


def test_the_nine_deal_breakers_are_the_registrys_and_every_one_can_fail():
    registry = fx.registry()
    for vector in registry_mod.VECTORS:
        assert registry.deal_breakers(vector) == list(registry_mod.DEAL_BREAKERS[vector])
        for key in registry.deal_breakers(vector):
            assert "NOT_HOLDING_UP" in registry.by_key(key).status_vocabulary


def test_the_calibrated_set_is_twelve_on_b2c_and_thirteen_on_b2b_the_answered_set_less_the_derived():
    """Calls 47, 59 (keel-cloud 074 `calibrated(b2b)` / `answered`): Purchase friction only on a B2B
    persona; the calibration job's set is the calibrated one less Ability to pay (derived)."""
    registry = fx.registry()
    assert registry.b2b_only() == list(registry_mod.B2B_ONLY) == ["commercial.purchase_friction"]
    assert registry.b2b_link_only() == list(registry_mod.B2B_LINK_ONLY)
    b2c, b2b = registry.calibrated_keys(False), registry.calibrated_keys(True)
    assert (len(b2c), len(b2b)) == (12, 13)
    assert set(b2b) - set(b2c) == set(registry_mod.B2B_ONLY)
    assert (len(registry.answered(False)), len(registry.answered(True))) == (11, 12)
    assert [d.key for d in registry.calibrated_slice("COMMERCIAL", False)] == [
        "commercial.existing_sacrifice", "commercial.price", "commercial.ability_to_pay",
        "commercial.buyer_payer_alignment", "commercial.commitment"]
    assert [d.key for d in registry.answered_slice("COMMERCIAL", False)] == [
        "commercial.existing_sacrifice", "commercial.price", "commercial.buyer_payer_alignment",
        "commercial.commitment"]
    assert len(registry.answered_slice("COMMERCIAL", True)) == 5
    assert len(registry.calibrated_slice("COMMERCIAL", True)) == 6


def test_plan_keys_are_per_part_and_link_less_what_the_founder_left_out():
    """Calls 30, 47, 59: PRIMARY asks 4 / 3 / 4 (3 / 3 / 4 after the gate), never Purchase friction nor
    Ability to pay; COMMERCIAL_B2B asks the commercial part whole (6), and only on a B2B persona."""
    registry = fx.registry()
    primary, b2b = registry_mod.LINK_PRIMARY, registry_mod.LINK_B2B
    calibration = {k: {"answer": "x"} for k in registry.keys()}
    for persona in (False, True):
        assert [len(registry.plan_keys(p, calibration, primary, persona))
                for p in (1, 2, 3)] == [4, 3, 4]
    assert "commercial.ability_to_pay" not in registry.plan_keys(3, calibration, primary, False)
    assert registry.plan_keys(3, calibration, b2b, True) == registry.calibrated_keys(True)[-6:]
    assert "commercial.ability_to_pay" in registry.plan_keys(3, calibration, b2b, True)
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


def test_there_is_a_broken_fixture_per_invariant_and_the_cost_first_extras():
    invariants = sorted(yaml.safe_load(p.read_text())["invariant"] for p in fx.BROKEN.glob("*.yaml"))
    assert invariants == [1, 2, 3, 3, 4, 5, 5, 5, 5, 5, 6, 6, 7, 8]
    for name in ("5-price-periods", "5-cost-modes", "5-derived-sides", "3-b2b-link-only", "6-shape-amounts",
                 "5-cost-kinds"):
        assert (fx.BROKEN / f"{name}.yaml").is_file()


def test_a_registry_still_carrying_asked_in_v1_is_refused_as_unknown_shaped():
    """Call 46: `asked_in_v1` is not read, and a registry carrying it is refused, not ignored."""
    document = copy.deepcopy(fx.registry_document())
    document["dimensions"][1]["respondent"]["asked_in_v1"] = True
    with pytest.raises(registry_mod.RegistryUnavailable) as refusal:
        registry_mod.from_document(document, source="v9.json")
    assert "asked_in_v1" in str(refusal.value)
    assert "problem.frequency" in str(refusal.value)


def test_the_v11_registry_is_refused_naming_invariant_3_and_5():
    """v11's shape (Ability to pay b2b_only, Price over month / year / one_off, no cost) fails invariants 3 and 5
    before anything is built against it (call 59)."""
    document = copy.deepcopy(fx.registry_document())
    by_key = {d["key"]: d for d in document["dimensions"]}
    by_key["commercial.ability_to_pay"]["b2b_only"] = True
    del by_key["commercial.ability_to_pay"]["respondent"]["b2b_link_only"]
    by_key["commercial.price"]["founder"]["normalized"]["periods"] = ["month", "year", "one_off"]
    faults = registry_mod.check_invariants(registry_mod.from_document(document, check=False))
    assert any(f.startswith("invariant 3 ") for f in faults), faults
    assert any(f.startswith("invariant 5 ") and "price periods" in f for f in faults), faults
    with pytest.raises(registry_mod.RegistryUnavailable):
        registry_mod.from_document(document, source="v11.json")


def test_the_v10_registry_of_twelve_is_refused_naming_invariant_1():
    """A twelve-key registry (v10's: no Price) fails invariant 1 before anything is built against it
    (call 50)."""
    document = copy.deepcopy(fx.registry_document())
    document["dimensions"] = [d for d in document["dimensions"] if d["key"] != "commercial.price"]
    for d in document["dimensions"]:
        if d["vector"] == "COMMERCIAL" and d["order"] > 2:
            d["order"] -= 1
    faults = registry_mod.check_invariants(registry_mod.from_document(document, check=False))
    assert any(f.startswith("invariant 1 ") and "COMMERCIAL has 5" in f for f in faults), faults


def test_the_v9_registry_of_twenty_five_is_refused_naming_invariant_1():
    """A 25-key registry (v9's shape) fails invariant 1 before anything is built against it."""
    document = copy.deepcopy(fx.registry_document())
    extra = copy.deepcopy(document["dimensions"][1])
    extra.update(key="problem.one_too_many", order=5)
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
    assert len(contract_mod.read(tmp_path).registry.keys()) == 13


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


def test_a_window_frames_frequency_above_one_unit_and_is_refused_when_unreadable():
    """Call 52 (`WindowFrame.framesFrequency`): C7 and R8 are retired with the ways they read a
    window; what is left is whether code frames Frequency -- a count above one."""
    assert registry_mod.RecallWindow(7, "NIGHTS").frames_frequency
    assert not registry_mod.RecallWindow(1, "SHIFTS").frames_frequency
    assert not hasattr(registry_mod.RecallWindow, "is_named_in")
    assert registry_mod.RecallWindow.read(None) is None
    for bad in ({"count": 0, "unit": "NIGHTS"}, {"count": 2, "unit": "YEARS"},
                {"count": 1.5, "unit": "DAYS"}, "FORTNIGHT"):
        with pytest.raises(ValueError):
            registry_mod.RecallWindow.read(bad)


def test_the_v12_registry_is_refused_for_its_kinds_and_its_amounts_control():
    """Call 67: v12's Existing sacrifice (a `code_rule` of kinds, `branch_pick_amounts`) fails invariants 5 and 6."""
    document = copy.deepcopy(fx.registry_document())
    sacrifice = next(d for d in document["dimensions"] if d["key"] == registry_mod.SACRIFICE_KEY)
    sacrifice["founder"]["normalized"]["code_rule"] = "4-6 slug codes for the kinds of cost"
    sacrifice["respondent"]["control"] = registry_mod.GONE_AMOUNTS_CONTROL
    faults = registry_mod.check_invariants(registry_mod.from_document(document, check=False))
    assert any("a cost has no kinds" in f for f in faults), faults
    assert any(f.startswith("invariant 5 (one total)") for f in faults), faults
    assert any(f.startswith("invariant 6 ") for f in faults), faults
