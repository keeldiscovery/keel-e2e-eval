"""Spec 101 -- the money study's people (cycle 3's two remaining stops, 2026-10-30).

FR-1: on money alone the person's link (kind FULL, no gate) opens with the idea card -- served as `reveal` with
`afterPart` 0 (keel-cloud 133 FR-4), walked before part 3 as keel-web's `screensOf` draws it; the screener first wherever
`Interview.condition` is served, whatever the kind (keel-cloud 166, keel-web 145). Nobody is read on money alone: no gate,
no story, nothing awaits a reading.
FR-2: a money-only study on a B2B entry sends the decision-makers alone (keel-cloud 133: the register serves the
COMMERCIAL_B2B kind only); the PRIMARY people are recorded as not on this study.

No browser, no stack: the pure decisions, the back-test files and a page double for the items' reveal."""
from __future__ import annotations

import contextlib
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


# ------------------------------------------------------------------- FR-2: a B2B money study sends the deciders alone

def _names(people):
    return [p.person for p in people]


def test_the_expanse_stop_money_alone_on_a_b2b_entry_is_the_deciders_alone():
    """17-expanse COMMERCIAL (`runs/quality-walk/20261030T135615Z-20261030-fcec453/17-expanse-COMMERCIAL.backtest.log`):
    the register served `kinds` COMMERCIAL_B2B alone, and the leg sent Priyanka Raghunathan on `labels['PRIMARY']`. The
    study's people are the seven decision-makers; the thirteen PRIMARY people are not on this study."""
    expanse = _bt("17-expanse")
    money = _scoped(expanse, "COMMERCIAL")
    deciders = [p.person for p in expanse.people() if p.link == vs.LINK_B2B]
    primary = [p.person for p in expanse.people() if p.link != vs.LINK_B2B]
    assert vs.is_b2b(expanse) and len(deciders) == 7 and len(primary) == 13
    assert _names(vs.study_people(money)) == deciders
    assert _names(vs.person_inputs(money)) == deciders
    assert {p.link for p in vs.person_inputs(money)} == {vs.LINK_B2B}
    left, why = vs.not_on_study(money)
    assert left == primary and "Priyanka Raghunathan" in left
    assert why == vs.NOT_ON_STUDY["DECIDERS_ONLY"] and "decision-maker's link only" in why


@pytest.mark.parametrize("name", ["08-fresco", "10-palus", "21-codyco"])
def test_the_other_b2b_money_studies_are_their_deciders_alone(name):
    """08-fresco, 10-palus and 21-codyco: the same stop once 096 carries them past the cost step and the lock."""
    entry = _bt(name)
    if not vs.is_b2b(entry):
        pytest.skip(f"{name} is not a B2B entry")
    money = _scoped(entry, "COMMERCIAL")
    assert _names(vs.person_inputs(money)) == [p.person for p in entry.people() if p.link == vs.LINK_B2B]
    for scope in ("ALL", "SOLUTION_COMMERCIAL"):
        assert _names(vs.study_people(_scoped(entry, scope))) == _names(entry.people()), scope


def test_money_alone_on_a_b2c_entry_sends_everyone_on_the_one_full_link():
    """13-aircaps: no decision-maker of its own, so money alone sends every person, as today."""
    aircaps = _bt("13-aircaps")
    money = _scoped(aircaps, "COMMERCIAL")
    assert not vs.is_b2b(aircaps)
    assert _names(vs.person_inputs(money)) == _names(aircaps.people())
    assert vs.not_on_study(money) == ([], None)


def test_the_problem_and_solution_studies_keep_082s_rule_and_reason():
    expanse = _bt("17-expanse")
    deciders = [p.person for p in expanse.people() if p.link == vs.LINK_B2B]
    for scope in ("PROBLEM", "SOLUTION"):
        left, why = vs.not_on_study(_scoped(expanse, scope))
        assert left == deciders and why == vs.NOT_ON_STUDY["PRIMARY_ONLY"], scope
    assert vs.not_on_study(_scoped(expanse, "ALL")) == ([], None)


def test_downstream_reads_the_deciders_alone_on_a_b2b_money_study():
    """The follow-up lines and `inputs.json` are worked out over the study's people: nobody left out is named there."""
    expanse = _scoped(_bt("17-expanse"), "COMMERCIAL")
    people = vs.person_inputs(expanse)
    primary = {p.person for p in expanse.people() if p.link != vs.LINK_B2B}
    assert not primary & set(vs.follow_up_lines(expanse, people))
    named = {p["person"] for p in vs.inputs_json(expanse, vs.founder_inputs(expanse), people)["people"]}
    assert named == {p.person for p in people} and not primary & named


# the register, as `leg_invite` reads it: {respondentType: label}
ONE_KIND = {"COMMERCIAL_B2B": "Operator"}
TWO_KINDS = {"PRIMARY": "Researcher", "COMMERCIAL_B2B": "Operator"}


@dataclasses.dataclass(frozen=True)
class _P:
    person: str
    link: str


MIXED = [_P("Ada", "PRIMARY"), _P("Ben", "COMMERCIAL_B2B"), _P("Cy", "PRIMARY"), _P("Di", "COMMERCIAL_B2B")]


def test_people_to_send_from_a_register_with_one_kind():
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    sent, unserved = cs.people_to_send(MIXED, ONE_KIND)
    assert _names(sent) == ["Ben", "Di"] and _names(unserved) == ["Ada", "Cy"]
    sent, unserved = cs.people_to_send([p for p in MIXED if p.link == "COMMERCIAL_B2B"], ONE_KIND)
    assert _names(sent) == ["Ben", "Di"] and unserved == []


def test_people_to_send_from_a_register_with_two_kinds_is_everyone_in_order():
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    assert cs.people_to_send(MIXED, TWO_KINDS) == (MIXED, [])
    assert cs.people_to_send(MIXED, ["PRIMARY", "COMMERCIAL_B2B"]) == (MIXED, [])
    sent, unserved = cs.people_to_send(MIXED, {"PRIMARY": "Researcher"})
    assert _names(sent) == ["Ada", "Cy"] and _names(unserved) == ["Ben", "Di"]


def test_a_b2c_money_study_one_full_kind_sends_everyone():
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    people = [_P("Harriet Coleman", "PRIMARY"), _P("Naomi Adler", "PRIMARY")]
    assert cs.people_to_send(people, {"PRIMARY": "Diner"}) == (people, [])


class _Step:
    def __init__(self, log):
        self.log = log

    def record_assert(self, want, got):
        self.log.append(("assert", want, got))


def _journey(monkeypatch, entry, labels_people=None):
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    log: list = []

    @contextlib.contextmanager
    def step(_j, name, **_k):
        log.append(("step", name))
        yield _Step(log)

    monkeypatch.setattr(cs, "_step", step)
    people = labels_people if labels_people is not None else vs.person_inputs(entry)
    return cs, type("J", (), {"entry": entry, "people": people})(), log


def test_leg_invite_records_the_primary_people_as_not_on_this_study(monkeypatch):
    money = _scoped(_bt("17-expanse"), "COMMERCIAL")
    cs, j, log = _journey(monkeypatch, money)
    sending = cs.not_on_this_study(j, ONE_KIND)
    assert sending == j.people and {p.link for p in sending} == {vs.LINK_B2B}
    names = [entry[1] for entry in log if entry[0] == "step"]
    assert len(names) == 1 and "13 of the entry's people not on this study" in names[0]
    assert "decision-maker's link only" in names[0]
    _, want, got = next(entry for entry in log if entry[0] == "assert")
    assert want["unserved"] == [] and got["unserved"] == [] and got["register kinds"] == ["COMMERCIAL_B2B"]
    assert "Priyanka Raghunathan" in got["not on this study"]


def test_a_kind_the_register_does_not_serve_is_a_named_fault_not_a_key_error(monkeypatch):
    """The old stop, reproduced: everyone on a register serving the decision-maker's kind alone."""
    expanse = _bt("17-expanse")
    cs, j, log = _journey(monkeypatch, _scoped(expanse, "ALL"))
    with pytest.raises(AssertionError, match="no kind for") as raised:
        cs.not_on_this_study(j, ONE_KIND)
    assert "Priyanka Raghunathan" in str(raised.value)


@pytest.mark.parametrize("scope, labels", [("ALL", TWO_KINDS), ("SOLUTION_COMMERCIAL", TWO_KINDS),
                                           ("PROBLEM", {"PRIMARY": "Researcher"}),
                                           ("SOLUTION", {"PRIMARY": "Researcher"})])
def test_no_new_step_where_nothing_is_left_out_on_money_alone(monkeypatch, scope, labels):
    """FR-3: the whole study, the solution and the money, and the problem and solution studies (082's) record nothing
    new."""
    cs, j, log = _journey(monkeypatch, _scoped(_bt("17-expanse"), scope))
    assert cs.not_on_this_study(j, labels) == j.people and log == []


def test_a_b2c_money_study_records_nothing_new(monkeypatch):
    cs, j, log = _journey(monkeypatch, _scoped(_bt("13-aircaps"), "COMMERCIAL"))
    assert cs.not_on_this_study(j, {"PRIMARY": "Diner"}) == j.people and log == []


def test_leg_invite_sends_on_the_study_and_the_register():
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    leg = inspect.getsource(cs.leg_invite)
    assert "sending = not_on_this_study(j, labels)" in leg
    assert "for person in sending:" in leg and "for person in j.people:" not in leg
    assert "labels[kind]" in leg and leg.index("not_on_this_study") < leg.index("labels[kind]")
