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
