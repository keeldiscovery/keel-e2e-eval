"""Spec 101 -- the money study's people (cycle 3's two remaining stops, 2026-10-30).

FR-1: on money alone the person's link (kind FULL, no gate) opens with the idea card -- served as `reveal` with
`afterPart` 0 (keel-cloud 133 FR-4), walked before part 3 as keel-web's `screensOf` draws it; the screener first wherever
`Interview.condition` is served, whatever the kind (keel-cloud 166, keel-web 145). Nobody is read on money alone: no gate,
no story, nothing awaits a reading.
FR-2: a money-only study on a B2B entry sends the decision-makers alone (keel-cloud 133: the register serves the
COMMERCIAL_B2B kind only); the PRIMARY people are recorded as not on this study.

No browser, no stack: the pure decisions, the back-test files and a page double for the items' reveal."""
from __future__ import annotations

import dataclasses
import inspect
from pathlib import Path

import pytest

from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from stack.config import load_config
from tests import v9_fixtures as fx

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)


def _bt(name: str):
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / f"{name}.yaml"
    if not path.is_file():
        pytest.skip(f"no back-test entry {path}")
    return corpus_mod.load_file(path, registry=fx.registry(), backtest=True)


def _scoped(entry, scope: str):
    return dataclasses.replace(entry, scope=scope)


# ----------------------------------------------------------------- FR-1: the screens before the first item

IDEA = {"what": "Imagine AirCaps.", "how": "You wear glasses.", "belief": "it would help", "problem": "They lose it."}
GATE = {"question": "Have you had a dinner out?", "options": []}
CONDITION = {"question": "Are you deaf or hard of hearing?", "inCodes": ["YES"]}
PART3 = [{"part": 3, "items": []}]
PARTS123 = [{"part": 1, "items": []}, {"part": 2, "items": []}, {"part": 3, "items": []}]


def _iv(kind, *, gate=None, idea=None, reveal=None, condition=None, parts=PART3) -> dict:
    out = {"kind": kind, "parts": parts}
    for key, value in (("gate", gate), ("idea", idea), ("reveal", reveal), ("condition", condition)):
        if value is not None:
            out[key] = value
    return out


def test_the_aircaps_stop_the_money_studys_person_link_opens_with_the_idea_card():
    """13-aircaps COMMERCIAL (`runs/20261030T152257Z-backtest-13-aircaps`, seq 115): kind FULL, no gate, the reveal served
    with `afterPart` 0 and part 3 alone -- the intro's *First, an idea, in three lines.* -- so the card is walked first
    (the stop waited 20 s for `h1.iv-q` on the card)."""
    served = _iv("FULL", reveal=dict(IDEA, afterPart=0))
    assert vs_screens.first_screens(served) == ["reveal"]


@pytest.mark.parametrize("kind, gate, idea, reveal, want", [
    # the decision-maker's link: the idea card first, no gate
    ("COMMERCIAL_LINK", None, IDEA, None, ["idea"]),
    ("COMMERCIAL_LINK", None, None, None, []),
    # the money study's person link: no gate, the reveal before part 3
    ("FULL", None, None, dict(IDEA, afterPart=0), ["reveal"]),
    # a FULL link with a gate: the gate, the reveal after its part as today (inside the items)
    ("FULL", GATE, None, dict(IDEA, afterPart=1), ["gate"]),
    # the problem study: the gate, no reveal
    ("FULL", GATE, None, None, ["gate"]),
    # `idea` on a FULL link is not keel-web's idea screen (it reads `idea` on the decision-maker's link alone)
    ("FULL", None, IDEA, None, []),
    ("FULL", GATE, IDEA, dict(IDEA, afterPart=1), ["gate"]),
])
def test_the_opening_screens_by_kind_gate_and_idea(kind, gate, idea, reveal, want):
    parts = PART3 if reveal is None or reveal.get("afterPart") == 0 else PARTS123
    assert vs_screens.first_screens(_iv(kind, gate=gate, idea=idea, reveal=reveal, parts=parts)) == want


@pytest.mark.parametrize("kind, extra, want", [
    ("COMMERCIAL_LINK", {"idea": IDEA}, ["condition", "idea"]),                       # spec 076 FR-4, as today
    ("FULL", {"reveal": dict(IDEA, afterPart=0)}, ["condition", "reveal"]),           # keel-cloud 166 / keel-web 145
    ("FULL", {"gate": GATE, "reveal": dict(IDEA, afterPart=1)}, ["condition", "gate"]),
])
def test_the_screener_comes_first_wherever_condition_is_served_whatever_the_kind(kind, extra, want):
    served = dict(_iv(kind, parts=PART3 if "gate" not in extra else PARTS123), condition=CONDITION, **extra)
    assert vs_screens.first_screens(served) == want


def test_a_gates_own_screener_is_the_gates_not_an_opening_screen():
    """A FULL link with a gate asks its screener inside the gate (`gate.condition`, spec 064 FR-4c), not before it."""
    served = _iv("FULL", gate=dict(GATE, condition=CONDITION), reveal=dict(IDEA, afterPart=1), parts=PARTS123)
    assert vs_screens.first_screens(served) == ["gate"]


@pytest.mark.parametrize("reveal, part, revealed, want", [
    ({"afterPart": 0}, 3, False, True),        # money alone: before part 3
    ({"afterPart": 1}, 1, False, False),       # the solution's reveal: not before its own part
    ({"afterPart": 1}, 2, False, True),        # before the first part after it, where part 1 was not served
    ({"afterPart": 1}, 2, True, False),        # walked already, after part 1
    ({"afterPart": 2}, 3, True, False),
    (None, 3, False, False),
    ({}, 3, False, False),                     # no afterPart: never guessed
    ({"afterPart": 0}, None, False, False),
])
def test_reveal_opens(reveal, part, revealed, want):
    assert vs_screens.reveal_opens(reveal, part, revealed=revealed) is want


class _Button:
    def __init__(self, log, name):
        self.log, self.name = log, name

    def wait_for(self, **_):
        return None

    def click(self):
        self.log.append(("click", self.name))


def _walker(monkeypatch, log):
    iv = vs_screens.Interview.__new__(vs_screens.Interview)
    iv.page = object()
    iv.screens = []
    iv._keep = lambda: None
    iv._shot = lambda slug: log.append(("shot", slug))
    iv._idea = lambda screen="idea": log.append(("idea", screen))
    monkeypatch.setattr(vs_screens, "_button", lambda _page, name: _Button(log, name))
    monkeypatch.setattr(vs_screens, "_first_text", lambda *_a, **_k: None)
    return iv


def test_items_walk_money_alones_card_before_part_3_once(monkeypatch):
    log: list = []
    iv = _walker(monkeypatch, log)
    iv._items(_iv("FULL", reveal=dict(IDEA, afterPart=0)), {})
    assert log == [("idea", "reveal")]


def test_items_walk_the_solutions_reveal_after_part_1_as_before(monkeypatch):
    log: list = []
    iv = _walker(monkeypatch, log)
    iv._items(_iv("FULL", gate=GATE, reveal=dict(IDEA, afterPart=1), parts=PARTS123), {})
    assert ("idea", "reveal") not in log
    assert log.count(("shot", "reveal")) == 1 and [s["screen"] for s in iv.screens] == ["reveal"]


def test_items_on_the_decision_makers_link_walk_no_reveal(monkeypatch):
    log: list = []
    iv = _walker(monkeypatch, log)
    iv._items(_iv("COMMERCIAL_LINK", idea=IDEA, reveal=dict(IDEA, afterPart=0)), {})
    assert log == []


def test_the_walk_reads_its_opening_off_first_screens():
    walk = inspect.getsource(vs_screens.Interview.walk)
    assert "opening = first_screens(interview)" in walk
    assert '"condition" in opening' in walk and '"idea" in opening' in walk
    assert 'interview.get("kind") == "COMMERCIAL_LINK" and interview.get("idea")' not in walk
    assert walk.index('"condition" in opening') < walk.index('"idea" in opening') < walk.index("self._gate(")
    items = inspect.getsource(vs_screens.Interview._items)
    assert "reveal_opens(reveal, part.get(\"part\"), revealed=revealed)" in items
    assert 'self._idea(screen="reveal")' in items


# ------------------------------------------------------------------- FR-1: nobody is read on money alone

def test_nobody_is_read_on_money_alone_the_file_story_is_not_the_walks():
    """13-aircaps has sixteen readable people in the file; under COMMERCIAL no gate is served, no story typed, and the
    founder's `POST readings` would be refused NOTHING_TO_READ -- so none is owed a reading."""
    aircaps = _bt("13-aircaps")
    readable = [p.person for p in vs.readable_people(aircaps)]
    assert len(readable) == 16
    assert all(vs.read_owed(aircaps, name) for name in readable)                # ALL, as before
    money = _scoped(aircaps, "COMMERCIAL")
    assert not any(vs.read_owed(money, p.person) for p in money.people())
    for scope in ("PROBLEM", "SOLUTION", "SOLUTION_COMMERCIAL"):
        assert all(vs.read_owed(_scoped(aircaps, scope), name) for name in readable), scope


def test_a_person_not_readable_is_never_owed_a_reading():
    aircaps = _bt("13-aircaps")
    unread = [p.person for p in aircaps.people() if not p.readable]
    assert unread and not any(vs.read_owed(aircaps, name) for name in unread)
    assert not vs.read_owed(aircaps, "Nobody In The File")


def test_the_read_step_asks_read_owed():
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    read = inspect.getsource(cs._read)
    assert "vs.read_owed(j.entry, person.person)" in read
    assert "readable_people" not in read
