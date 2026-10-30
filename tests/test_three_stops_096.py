"""Spec 096 -- three stops of the quality walk that were the harness's (cycle 3, 2026-10-30).

FR-1: after a refused lock the idea card's Save lands on the scope's next screen -- the solution's first question, or who
decides in the money-only study (keel-web 109 FR-3) -- and `edit_idea_lines` says which.
FR-2: the cost step's rate is held to the view as it was before the screen's own save (Keel's default, 80, with its
note); the entry's own rate (55, `defaulted: false`) is a second check after the save.
FR-3: keel-cloud 165 names the decision-maker's line *the idea card's decision-maker's how line* -- read as `howDecider`
and edited alone; *how* edits `how` alone.

No browser, no stack: the URL pattern, the pure checks and a page double."""
from __future__ import annotations

import contextlib
import re

import pytest

from evals import corpus_scenario as cs
from harness import vectors_screens as vs_screens

# ------------------------------------------------------------------- FR-1: the edit lands on the scope's next screen

BASE = "http://localhost:5173/p/0b7a1c2e"


@pytest.mark.parametrize("url, landed", [
    (f"{BASE}/define/solution/q/1", "solution"),
    (f"{BASE}/define/solution/q/12", "solution"),
    (f"{BASE}/define/persona", "persona"),
])
def test_the_save_lands_on_either_of_the_scopes_next_screens(url, landed):
    """Playwright's `wait_for_url` with a compiled pattern searches the url: both landings meet the one pattern."""
    assert re.compile(vs_screens.IDEA_SAVE_LANDS).search(url)
    assert vs_screens.idea_save_landing(url) == landed


@pytest.mark.parametrize("url", [
    f"{BASE}/define/solution/idea",            # the Check screen itself: Save has not moved on
    f"{BASE}/define/solution/q/",
    f"{BASE}/define/persona/edit",
    f"{BASE}/define/ready/interviewer",        # L1, where the lock was refused
    f"{BASE}/interviews/sent",
])
def test_no_other_screen_is_a_landing(url):
    assert not re.compile(vs_screens.IDEA_SAVE_LANDS).search(url)
    assert vs_screens.idea_save_landing(url) is None


def test_the_palus_stop_url_is_a_landing_now():
    """10-palus COMMERCIAL (`runs/20261030T144756Z-backtest-10-palus`, seq 70): the wait was for the solution's first
    question alone; the money study's Save went on to `/define/persona`."""
    assert not re.compile(r"/define/solution/q/\d+$").search(f"{BASE}/define/persona")
    assert vs_screens.idea_save_landing(f"{BASE}/define/persona") == "persona"


class _IdeaBox:
    def __init__(self, page, selector):
        self.page, self.selector = page, selector

    def count(self) -> int:
        return 1 if self.selector in self.page.values else 0

    def wait_for(self, state="visible", timeout=0) -> None:
        if not self.count():
            raise TimeoutError(self.selector)

    def input_value(self) -> str:
        return self.page.values[self.selector]

    def fill(self, words: str) -> None:
        self.page.values[self.selector] = words


class _IdeaPage:
    """The idea's Check screen (`IdeaCheck`): its boxes, and on Save the scope's next address."""

    def __init__(self, next_url: str, *, decider: bool):
        self.url = ""
        self.next_url = next_url
        self.values = {"#idea-how": "It writes into the PMS.", "#idea-belief": "The people building it believe ..."}
        if decider:
            self.values["#idea-howDecider"] = "Your agents write into the PMS."
        self.waited: list[str] = []

    def goto(self, url, wait_until="load") -> None:
        self.url = url

    def locator(self, selector):
        return _IdeaBox(self, selector)

    def wait_for_function(self, script, **kw) -> None:
        return None

    def save(self) -> None:
        self.url = self.next_url

    def wait_for_url(self, pattern, timeout=0) -> None:
        self.waited.append(pattern.pattern)
        if not pattern.search(self.url):
            raise TimeoutError(f"waiting for navigation to {pattern!r}")


class _Step:
    def capture_text(self, *a) -> None:
        return None

    def add_screenshot(self, *a) -> None:
        return None


class _B:
    def __init__(self):
        self.names: list[str] = []

    @contextlib.contextmanager
    def step(self, name):
        self.names.append(name)
        yield _Step()

    def screenshot(self, slug):
        return None


def _corridor(page: _IdeaPage, monkeypatch) -> vs_screens.Corridor:
    corridor = vs_screens.Corridor.__new__(vs_screens.Corridor)
    corridor.page, corridor.base, corridor._b = page, "http://localhost:5173", _B()

    def press(expected=None):
        assert expected == vs_screens.SAVE
        page.save()
        return vs_screens.SAVE
    corridor._press_primary = press
    monkeypatch.setattr(vs_screens, "_text", lambda p: "")
    return corridor


@pytest.mark.parametrize("next_path, decider, landed", [
    ("/define/persona", True, "persona"),              # the money-only study: Save goes on to who decides
    ("/define/solution/q/1", True, "solution"),        # money and the solution: the solution's first question
    ("/define/solution/q/1", False, "solution"),       # the solution alone: no decider's box
])
def test_edit_idea_lines_returns_where_save_landed(monkeypatch, next_path, decider, landed):
    page = _IdeaPage(f"{BASE}{next_path}", decider=decider)
    corridor = _corridor(page, monkeypatch)
    out = corridor.edit_idea_lines("0b7a1c2e", {"how": "It writes into the hotel's booking system."})
    assert out["landed"] == landed and out["primary"] == vs_screens.SAVE
    assert out["typed"] == {"how": "It writes into the hotel's booking system."} and out["absent"] == []
    assert page.waited == [vs_screens.IDEA_SAVE_LANDS]
    assert "who decides in the money study" in corridor._b.names[0]


def test_edit_idea_lines_still_stops_where_save_goes_nowhere_owed(monkeypatch):
    page = _IdeaPage(f"{BASE}/define/solution/idea", decider=True)
    with pytest.raises(TimeoutError):
        _corridor(page, monkeypatch).edit_idea_lines("0b7a1c2e", {"how": "plain words"})


def test_a_decider_box_not_drawn_is_named_absent(monkeypatch):
    page = _IdeaPage(f"{BASE}/define/solution/q/1", decider=False)
    out = _corridor(page, monkeypatch).edit_idea_lines("0b7a1c2e", {"howDecider": "plain words"})
    assert out["absent"] == ["howDecider"] and out["typed"] == {} and out["before"]["howDecider"] is None


# ------------------------------------------------------------------- FR-2: the cost step reads the rate as drawn

NOTE = vs_screens.HOURLY_RATE_DEFAULTED
BEFORE = {"amount": 80, "currency": "USD", "currencySymbol": "$", "defaulted": True}
AFTER = {"amount": 55, "currency": "USD", "currencySymbol": "$", "defaulted": False}
#: 08-fresco COMMERCIAL as the chain screen read it before typing (`runs/20261030T142020Z-backtest-08-fresco`, seq 46)
FRESCO_FILLED = {"unit": "contractor", "unit_help": vs_screens.CHAIN_UNIT_HELP, "base": "site walk",
                 "base_help": vs_screens.CHAIN_HOURS_BASE_HELP, "rate": "80", "rate_note": NOTE,
                 "order": [-20.296875, 61.078125, 172.59375]}


def test_the_rate_drawn_is_held_to_the_view_before_the_save():
    """The cycle-3 stop: the box drew 80 with its note, the view before the save says 80 defaulted -- it holds."""
    assert cs.cost_fill_rate_owed(BEFORE) == {"rate": "80", "rate_note": NOTE}
    assert cs.cost_fill_rate_faults(FRESCO_FILLED, BEFORE) == []


def test_the_view_after_the_save_is_not_what_the_box_drew():
    """The check as it read before 096 -- the box against the view after the save (55, not defaulted) -- faults on the
    amount and on the note: the wrong moment, both named."""
    faults = cs.cost_fill_rate_faults(FRESCO_FILLED, AFTER)
    assert {"rate": "80", "owed": "55"} in faults
    assert any(f.get("rate_note") == NOTE and f.get("owed") is None and f.get("defaulted") is False for f in faults)


def test_the_note_is_drawn_iff_defaulted():
    own = {"amount": 55, "defaulted": False}
    assert cs.cost_fill_rate_faults({**FRESCO_FILLED, "rate": "55", "rate_note": None}, own) == []
    assert cs.cost_fill_rate_faults({**FRESCO_FILLED, "rate": "55"}, own)            # a note on the founder's own rate
    assert cs.cost_fill_rate_faults({**FRESCO_FILLED, "rate_note": None}, BEFORE)    # Keel's figure, no note


def test_a_rate_not_drawn_or_another_amount_faults():
    assert cs.cost_fill_rate_faults({**FRESCO_FILLED, "rate": None}, BEFORE)[0]["rate"] == "not drawn"
    assert cs.cost_fill_rate_faults({**FRESCO_FILLED, "rate": ""}, BEFORE)[0]["rate"] == "not drawn"
    assert cs.cost_fill_rate_faults({**FRESCO_FILLED, "rate": "90"}, BEFORE) == [{"rate": "90", "owed": "80"}]
    assert cs.cost_fill_rate_faults({**FRESCO_FILLED, "rate": "80.0"}, BEFORE) == []


def test_the_order_checks_stay():
    assert cs.cost_fill_rate_faults({**FRESCO_FILLED, "order": [70, 61, 172]}, BEFORE) == \
        [{"the rate sits above the hours": [70, 61, 172]}]
    assert cs.cost_fill_rate_faults({**FRESCO_FILLED, "order": [-20, 180, 172]}, BEFORE) == \
        [{"the rate sits under what the time goes on": [-20, 180, 172]}]
    assert cs.cost_fill_rate_faults({**FRESCO_FILLED, "order": [None, None, None]}, BEFORE) == []


def test_no_hourly_rate_owes_nothing():
    assert cs.cost_fill_rate_owed(None) is None and cs.cost_fill_rate_owed({"amount": None}) is None
    assert cs.cost_fill_rate_faults({"rate": None}, None) == []


def test_after_the_save_the_view_carries_the_entrys_own_rate():
    assert cs.saved_rate_faults(AFTER, 55) == []
    assert cs.saved_rate_faults(AFTER, 55.0) == []
    assert cs.saved_rate_faults(BEFORE, 55) == [{"amount": 80, "entry": 55}, {"defaulted": True, "owed": False}]
    assert cs.saved_rate_faults({**AFTER, "defaulted": True}, 55) == [{"defaulted": True, "owed": False}]
    assert cs.saved_rate_faults({"amount": 55}, 55) == [{"defaulted": None, "owed": False}]
    assert cs.saved_rate_faults(None, 55) == [{"amount": None, "entry": 55}, {"defaulted": None, "owed": False}]
    assert cs.saved_rate_faults(BEFORE, None) == []                              # no rate typed, none owed


class _J:
    """The journey double `_hold_the_cost_fill` reads: the wire's three views and its step recorder."""

    def __init__(self, after: dict, *, strict: bool = False):
        self.views = {"/calibration/COMMERCIAL": {"hourlyRate": after},
                      "/persona": {"decider": {"role": "contractor"}}, "/context": {}}
        self.strict = strict
        self.steps: list[dict] = []
        self.entry = None

    def project(self, path: str) -> str:
        return path

    def get(self, path: str):
        return self.views.get(path)


@pytest.fixture
def held(monkeypatch):
    j = _J(AFTER)
    monkeypatch.setattr(cs.vs, "is_b2b", lambda entry: True)

    @contextlib.contextmanager
    def step(journey, name, **kw):
        row = {"name": name, "ok": True}
        journey.steps.append(row)

        class H:
            def record_assert(self, want, got):
                row["want"], row["got"] = want, got
        try:
            yield H()
        except AssertionError as e:
            row["ok"], row["error"] = False, e
            raise
    monkeypatch.setattr(cs, "_step", step)
    return j


HOURS = {"mode": "HOURS", "low": 30, "high": 60, "rate": 55, "period": "month", "unit": "site", "base": "site walk"}


def test_the_fresco_cost_step_holds_both_moments(held):
    """08-fresco's two readings: the box against the view before the save (80, defaulted), then the view after it
    (55, not defaulted) against the entry's rate -- two steps, both met."""
    cs._hold_the_cost_fill(held, HOURS, FRESCO_FILLED, BEFORE)
    assert [s["ok"] for s in held.steps] == [True, True]
    assert held.steps[0]["want"]["rate"] == "80" and held.steps[0]["want"]["rate_note"] == NOTE
    assert held.steps[1]["want"] == {"amount": 55, "defaulted": False} and held.steps[1]["got"] == AFTER


def test_the_box_held_to_the_view_after_the_save_is_the_old_stop(held):
    with pytest.raises(AssertionError):
        cs._hold_the_cost_fill(held, HOURS, FRESCO_FILLED, AFTER)
    assert held.steps[0]["ok"] is False and len(held.steps) == 1


def test_a_save_that_kept_keels_default_faults_the_second_step(held):
    held.views["/calibration/COMMERCIAL"] = {"hourlyRate": BEFORE}
    with pytest.raises(AssertionError):
        cs._hold_the_cost_fill(held, HOURS, FRESCO_FILLED, BEFORE)
    assert [s["ok"] for s in held.steps] == [True, False]


def test_no_rate_in_the_entry_owes_no_second_step(held):
    held.views["/calibration/COMMERCIAL"] = {"hourlyRate": BEFORE}
    cs._hold_the_cost_fill(held, {**HOURS, "rate": None}, FRESCO_FILLED, BEFORE)
    assert len(held.steps) == 1 and held.steps[0]["ok"]


def test_the_leg_passes_the_view_read_before_the_walk():
    import inspect                                                     # noqa: PLC0415
    leg = inspect.getsource(cs.leg_calibrate)
    assert 'drawn_rate=view.get("hourlyRate")' in leg
    assert leg.index("view = _wait_calibration(j, vector)") < leg.index("for question in questions:")
    assert "_hold_the_cost_fill(j, cost, seen[\"filled\"], drawn_rate)" in inspect.getsource(cs._hold_the_chain_screen)
