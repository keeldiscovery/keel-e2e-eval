"""Spec 090 -- the harness walks the money screens as keel-web 134 draws them, the three controls as keel-web 135 draws
them, the five recorded 0s sent as 1, and Send more's words as keel-web 130 draws them.

FR-1 the cost box asks the mode first under a line that names the cost, who pays it and the core of the loss; the price
shapes are six named choices, each clicked by its own id (`chain-share-COST_BASE` is gone).
"""

from __future__ import annotations

import pytest

from evals import corpus_scenario as cs
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from harness.steps import Recorder
from stack.config import load_config


# ------------------------------------------------------------------------------------- FR-1: the money screens

def test_the_modes_are_134s_words():
    """keel-web 134 `CHAIN_COST_MODE_WORD`: *A share they lose* (was *A rate they lose*)."""
    assert vs_screens.CHAIN_MODE_WORD == {"MONEY": "Money they spend", "HOURS": "Time it takes",
                                          "RATE": "A share they lose"}


@pytest.mark.parametrize("payer, core, line", [
    ("the buyer's organisation", "each job", "How would you put the cost of each job to the buyer's organisation?"),
    ("deaf and hard-of-hearing adults", "each conversation",
     "How would you put the cost of each conversation to deaf and hard-of-hearing adults?"),
    (None, "each night", "How would you put the cost of each night?"),
    ("parents of babies", None, "How would you put what it costs parents of babies?"),
    (None, None, "How would you put what it costs them?"),
])
def test_the_line_is_134s_four_forms(payer, core, line):
    """keel-web 134 T003 (`costHowLine`): both parts, the core alone, the payer alone, neither."""
    assert vs_screens.cost_how_line(payer, core) == line


def test_the_lines_parts_are_the_pages_reads():
    """keel-web 134 `costPayer` / `costCore`: the buyer's organisation on B2B (never the people who do the work),
    else the context's people lower-cased as a sentence takes them, an acronym kept; the core *each <occasion>*."""
    context = {"segment": {"core": "Deaf and hard-of-hearing adults"}}
    assert vs_screens.cost_line_parts(True, context, "Conversation") == ("the buyer's organisation", "each conversation")
    assert vs_screens.cost_line_parts(False, context, "conversation") == ("deaf and hard-of-hearing adults",
                                                                         "each conversation")
    assert vs_screens.cost_line_parts(False, {"segment": {"core": "HR leads at startups"}}, None) == (
        "HR leads at startups", None)
    assert vs_screens.cost_line_parts(False, {}, None) == (None, None)


@pytest.mark.parametrize("price, choice", [
    ({"shape": "AMOUNT_PERIOD", "low": 10, "high": 20}, "chain-shape-AMOUNT_PERIOD"),
    ({"shape": "SHARE", "low": 5}, "chain-shape-SHARE"),
    ({"shape": "SHARE", "shareBase": "COST_BASE", "low": 5}, "chain-shape-SHARE"),
    ({"shape": "SHARE", "shareBase": "RECOVERED", "low": 5}, "chain-share-RECOVERED"),
    ({"shape": "UPFRONT_THEN", "upfrontLow": 100, "low": 10}, "chain-shape-UPFRONT_THEN"),
    ({"shape": "UPFRONT_THEN", "upfrontLow": 100, "thenNothing": True}, "chain-then-nothing"),
    ({"shape": "FREE"}, "chain-shape-FREE"),
])
def test_the_price_is_one_of_six_named_choices_clicked_by_its_id(price, choice):
    """keel-web 134 FR-2 (J-4): one click on the choice's own id, then its numbers; `chain-share-COST_BASE` is never
    clicked (gone), nor a shape's first choice before its second outcome."""
    log: list = []

    class Box:
        def __init__(self, key):
            self.key = key

        @property
        def first(self):
            return self

        def count(self):
            return 1

        def click(self):
            log.append(("click", self.key))

        def fill(self, value):
            log.append(("fill", self.key, value))

        def inner_text(self):
            return "per site · a month"

    class Page:
        def get_by_test_id(self, key):
            return Box(key)

        def locator(self, key):
            return Box(key)

    corridor = vs_screens.Corridor.__new__(vs_screens.Corridor)
    corridor.page = Page()
    seen = corridor._chain_price(price)
    clicks = [k for kind, k, *_ in log if kind == "click"]
    assert clicks == [choice] and seen["choice"] == choice
    assert "chain-share-COST_BASE" not in str(log)
    fills = [k for kind, k, *_ in log if kind == "fill"]
    assert fills == {"AMOUNT_PERIOD": ["chain-price-low", "chain-price-high"], "SHARE": ["chain-share"],
                     "UPFRONT_THEN": ["chain-upfront"] + ([] if price.get("thenNothing") else ["chain-plan"]),
                     "FREE": []}[price["shape"]]


@pytest.fixture(scope="module")
def countly():
    _corpus, entry = vs.entry_for(load_config(validate=False).keel_cloud, "01-countly")
    return entry


def _journey(tmp_path, entry, context, persona=None):
    j = cs.Journey(recorder=Recorder(tmp_path), page=None, context=None, web_base="", cloud_base="", entry=entry,
                   founder=None, people=[], project_id="p1", scope=entry.scope)
    j.get = lambda path: context if path.endswith("/context") else (persona or {})
    return j


CONTEXT = {"state": "CONFIRMED", "segment": {"core": "Payroll practitioners"}, "occasion": {"noun": "payroll run"},
           "fields": {"circumstance": "they close the month and the numbers do not tie"}}


def test_the_mode_first_hold_takes_the_composed_line(tmp_path, countly):
    """FR-1: nothing of *Per* or the periods before the mode; the line is the composed one, never the circumstance."""
    j = _journey(tmp_path, countly, CONTEXT)
    owed, shape = cs.cost_line_owed(vs.is_b2b(countly), CONTEXT, {})
    payer = "the buyer's organisation" if vs.is_b2b(countly) else "payroll practitioners"
    assert owed == f"How would you put the cost of each payroll run to {payer}?" and shape.fullmatch(owed)
    cs._hold_the_mode_first(j, {"order": "mode-first", "before_mode": {"unit": 0, "periods": 0}, "line": owed})


@pytest.mark.parametrize("seen", [
    {"before_mode": {"unit": 1, "periods": 0}},                                     # *Per* drawn before the mode
    {"before_mode": {"unit": 0, "periods": 6}},                                     # the periods before the mode
    {"line": "How would you put what it costs them?"},                              # the old line where both are served
    {"line": "How would you put the cost of when they close the month and the numbers do not tie to them?"},
])
def test_the_mode_first_hold_fails_the_old_order_and_the_old_line(tmp_path, countly, seen):
    owed, _shape = cs.cost_line_owed(vs.is_b2b(countly), CONTEXT, {})
    drawn = {"order": "mode-first", "before_mode": {"unit": 0, "periods": 0}, "line": owed, **seen}
    with pytest.raises(AssertionError):
        cs._hold_the_mode_first(_journey(tmp_path, countly, CONTEXT), drawn)


def test_with_no_context_the_line_names_the_payer_or_nothing(tmp_path, countly):
    """The shorter forms where the wire serves less: no confirmed context -- no core, and the people only on B2B."""
    owed, shape = cs.cost_line_owed(False, {}, {})
    assert owed == vs_screens.CHAIN_COST_HOW and shape.fullmatch(owed)
    owed, shape = cs.cost_line_owed(True, {}, {})
    assert owed == "How would you put what it costs the buyer's organisation?" and shape.fullmatch(owed)
