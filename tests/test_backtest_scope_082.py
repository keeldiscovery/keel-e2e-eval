"""Spec 082: the back-test under a scope -- the study's own people (FR-1), the cost box read when it is drawn (FR-2),
and a cycle record that names the walks that stopped and the sha that moved (FR-3).

Zero spend: the people from keel-cloud's back-test file and the golden B2B fixture, the cost step on a page double that
draws the *of* box only with the equation, the record composed from the 079 fixture cycle's score files.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from stack.config import load_config
from tests import v9_fixtures as fx

REPO = Path(__file__).resolve().parent.parent
KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)


def _scoped(entry, scope: str):
    return dataclasses.replace(entry, scope=scope)


@pytest.fixture(scope="module")
def fresco():
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / "08-fresco.yaml"
    if not path.is_file():
        pytest.skip(f"no back-test entry {path}")
    return corpus_mod.load_file(path, registry=fx.registry(), backtest=True)


# ------------------------------------------------------------------------------- FR-1: the study's own people

def test_08_fresco_under_problem_and_solution_is_its_primary_people_alone(fresco):
    """FR-1: the cycle's KeyError 'COMMERCIAL_B2B' -- 08-fresco's eight B2B people are the money study's (keel-cloud
    133); under PROBLEM and SOLUTION the walk sends the twelve PRIMARY people and nobody else."""
    primary = [p.person for p in fresco.people() if p.link == vs.LINK_PRIMARY]
    b2b = [p.person for p in fresco.people() if p.link == vs.LINK_B2B]
    assert vs.is_b2b(fresco) and len(primary) == 12 and len(b2b) == 8
    for scope in ("PROBLEM", "SOLUTION"):
        people = vs.person_inputs(_scoped(fresco, scope))
        assert [p.person for p in people] == primary, scope
        assert {p.link for p in people} == {vs.LINK_PRIMARY}, scope


def test_08_fresco_under_all_and_commercial_is_every_person_in_the_file(fresco):
    """FR-1: the money study and the whole study send every person, as before."""
    everyone = [p.person for p in fresco.people()]
    for entry in (fresco, _scoped(fresco, "ALL"), _scoped(fresco, "COMMERCIAL")):
        assert [p.person for p in vs.person_inputs(entry)] == everyone, vs.scope_of(entry)
    assert vs.study_people(_scoped(fresco, "SOLUTION_COMMERCIAL")) == list(fresco.people())


def test_a_b2b_entry_under_a_scope_names_nobody_downstream_who_was_not_sent():
    """FR-1: the follow-up lines, the themes screen and `inputs.json` read the list that comes back -- under PROBLEM
    and SOLUTION no decision-maker is owed a line or written into the inputs; under ALL they are, as before."""
    entry = fx.entry(fx.ENTRY_B2B)
    deciders = {p.person for p in entry.people() if p.link == vs.LINK_B2B}
    assert deciders and deciders & set(vs.follow_up_lines(entry, vs.person_inputs(entry)))
    for scope in ("PROBLEM", "SOLUTION"):
        seed = _scoped(entry, scope)
        people = vs.person_inputs(seed)
        assert not deciders & {p.person for p in people}, scope
        lines = vs.follow_up_lines(seed, people)
        assert lines and not deciders & set(lines), (scope, lines)
        assert {p.person: p.follow_up for p in people if p.follow_up} == {k: v for k, v in lines.items() if v}
        inputs = vs.inputs_json(seed, vs.founder_inputs(seed), people)
        named = {p["person"] for p in inputs["people"]}
        assert named == {p.person for p in people} and not deciders & named, scope
        themes = vs.generate(seed).screens["THEMES"]
        assert themes == vs.themes_entries(seed, vs.walked_follow_ups(seed, people)), scope


def test_the_scope_reaches_person_inputs_through_the_entry_not_a_parameter():
    """FR-1: `corpus_scenario` and `scope_journey` replace `entry.scope` before they build the people; no new
    parameter."""
    import inspect                                                     # noqa: PLC0415

    from evals import corpus_scenario, scope_journey                   # noqa: PLC0415
    assert list(inspect.signature(vs.person_inputs).parameters) == ["entry"]
    source = inspect.getsource(corpus_scenario)
    at_replace = source.index("entry = dataclasses.replace(entry, scope=scope)")
    assert at_replace < source.index("people = vs.person_inputs(entry)", at_replace)
    walk = inspect.getsource(scope_journey)
    assert walk.index("entry.scope != scope") < walk.index("people = vs.person_inputs(entry)")


# ------------------------------------------------------------------------ FR-2: the cost box read when it is drawn

class _Box:
    """One locator on the page double: present or not, by the page's state at the moment it is asked."""

    def __init__(self, page, key: str):
        self.page, self.key = page, key

    @property
    def first(self):
        return self

    def count(self) -> int:
        return 1 if self.page.drawn(self.key) else 0

    def input_value(self) -> str:
        self.page.log.append(("read", self.key))
        return self.page.values[self.key]

    def inner_text(self) -> str:
        self.page.log.append(("read", self.key))
        return self.page.texts[self.key]

    def click(self) -> None:
        self.page.press(self.key)

    def fill(self, value: str) -> None:
        self.page.log.append(("fill", self.key))
        self.page.values[self.key] = value

    def wait_for(self, state: str = "visible", timeout: float = 0) -> None:
        if not self.page.drawn(self.key):
            raise TimeoutError(f"{self.key} never drawn")


class _ChainPage:
    """keel-web 123's cost step as `FounderControl` draws it: *Per* (`chain-unit`, its helper) from the start, the
    equation -- and inside it the *of* box (`chain-base`, `#chain-base-help`) on a way with the box, and on hours the
    rate and its note -- only once a mode, a unit and a period are picked (`ready`)."""

    def __init__(self):
        self.mode = self.period = None
        self.log: list[tuple[str, str]] = []
        self.values = {"chain-unit": "superintendent", "chain-base": "job", "chain-rate": "80", "chain-low": "",
                       "chain-high": "", "chain-count": ""}
        self.texts = {"#chain-unit-help": vs_screens.CHAIN_UNIT_HELP, "[data-testid=chain-equation]":
                      "40 to 80 hours of job · per superintendent · a month", "[data-testid=chain-per]":
                      "per superintendent · a month", ".calib__note": vs_screens.HOURLY_RATE_DEFAULTED}

    @property
    def ready(self) -> bool:
        return bool(self.mode and self.values["chain-unit"] and self.period)

    def drawn(self, key: str) -> bool:
        if key in ("chain-unit", "#chain-unit-help") or key.startswith(("chain-mode-", "chain-period-")):
            return True
        if key in ("chain-equation", "[data-testid=chain-equation]", "[data-testid=chain-per]", "chain-low",
                   "chain-high", "chain-measure-percent", "chain-measure-count", "chain-count"):
            return self.ready
        if key in ("chain-base", "#chain-base-help"):
            return self.ready and self.mode in ("HOURS", "RATE")
        if key in ("chain-rate", ".calib__note"):
            return self.ready and self.mode == "HOURS"
        raise AssertionError(f"the double draws no {key}")

    def press(self, key: str) -> None:
        self.log.append(("press", key))
        if key.startswith("chain-mode-"):
            self.mode = key.removeprefix("chain-mode-")
        elif key.startswith("chain-period-"):
            self.period = key.removeprefix("chain-period-")

    def get_by_test_id(self, testid: str) -> _Box:
        return _Box(self, testid)

    def locator(self, selector: str, has_text: str | None = None) -> _Box:
        if has_text is not None and has_text != self.texts.get(selector):
            return _Box(self, "#never")
        return _Box(self, selector)

    def evaluate(self, script: str):
        return [10, 20, 30]

    @property
    def help_text(self) -> str:
        return vs_screens.CHAIN_HOURS_BASE_HELP if self.mode == "HOURS" else vs_screens.CHAIN_BASE_HELP


def _never_drawn(page: _ChainPage):
    original = page.drawn

    def drawn(key: str) -> bool:
        return False if key == "#never" else original(key)
    page.drawn = drawn
    return page


def _chain_cost(cost: dict) -> tuple[dict, _ChainPage]:
    page = _never_drawn(_ChainPage())
    page.texts["#chain-base-help"] = ""
    corridor = vs_screens.Corridor.__new__(vs_screens.Corridor)
    corridor.page = page
    original_press = page.press

    def press(key: str) -> None:
        original_press(key)
        page.texts["#chain-base-help"] = page.help_text
    page.press = press
    return corridor._chain_cost(cost), page


@pytest.mark.parametrize("mode", ["HOURS", "RATE"])
def test_the_of_box_is_read_after_the_period_once_the_equation_is_drawn(mode):
    """FR-2: on a fresh draft the *of* box is not on the page until the period is picked (cycle 1's 13-aircaps and
    17-expanse COMMERCIAL read None there); `_chain_cost` reads *Per* first, as before, then *of* and its helper -- and
    on hours the rate -- after the period pill, once `chain-equation` is visible."""
    cost = {"mode": mode, "unit": "superintendent", "period": "month", "low": 40, "high": 80, "base": "job",
            "measure": "%", "rate": None}
    seen, page = _chain_cost(cost)
    filled = seen["filled"]
    assert filled["unit"] == "superintendent" and filled["unit_help"] == vs_screens.CHAIN_UNIT_HELP
    assert filled["base"] == "job" and filled["base_help"] == page.help_text
    log = page.log
    period = log.index(("press", "chain-period-month"))
    assert log.index(("read", "chain-unit")) < log.index(("press", f"chain-mode-{mode}")) < period
    assert period < log.index(("read", "chain-base")) and period < log.index(("read", "#chain-base-help"))
    assert log.index(("read", "chain-base")) < log.index(("fill", "chain-low")), "read before anything is typed in it"
    if mode == "HOURS":
        assert filled["rate"] == "80" and filled["rate_note"] == vs_screens.HOURLY_RATE_DEFAULTED
        assert period < log.index(("read", "chain-rate"))
    else:
        assert "rate" not in filled and log.index(("read", "chain-base")) < log.index(("fill", "chain-base"))


def test_on_money_no_of_box_is_drawn_and_none_is_read():
    seen, page = _chain_cost({"mode": "AMOUNT", "unit": "superintendent", "period": "month", "low": 400, "high": 900})
    assert seen["filled"]["base"] is None and seen["filled"]["base_help"] is None
    assert ("read", "chain-base") not in page.log


def test_the_step_and_the_docstring_say_when_the_box_is_read():
    """FR-2: the step's wording and `_hold_the_cost_fill`'s docstring; the pins are unchanged."""
    import inspect                                                     # noqa: PLC0415

    from evals import corpus_scenario as cs                            # noqa: PLC0415
    source = inspect.getsource(cs._hold_the_cost_fill)
    assert "before anything is typed; " in source and "the equation is drawn (keel-web 123)" in source
    assert "Spec 082 FR-2" in source
    for pin in ('owed["base_help"] = vs_screens.CHAIN_HOURS_BASE_HELP if mode == "HOURS" else '
                'vs_screens.CHAIN_BASE_HELP', 'assert filled.get("rate_note") == vs_screens.HOURLY_RATE_DEFAULTED',
                'assert at <= base, {"the rate sits under what the time goes on"'):
        assert pin in source, pin
