"""Spec 102 -- on a consumer entry's money study the person's body is answers alone (the re-walk of 2026-10-30,
`quality/cycles/20261030-35dfb74.md`: 13-aircaps · COMMERCIAL stopped at Harriet Coleman, *the page sent exactly this
person's answers*).

FR-1: money alone serves no gate (keel-cloud 133 FR-4), so the FULL link's page posts `{answers, followUps, pilotOptIn}`
-- no `recency`, no `story`, no `anchorChip`; the expected body is the answers alone, as on the decision-maker's link.
FR-2: off the gate there is no No and no chip ending the interview; every inside person walked meets the items and the
follow-ups. A gate No in the file has no money answers and is refused by name.
FR-3: off the gate there is no story box, so nobody speaks.
FR-4: a person outside the segment on a gateless study is not walked until the money link asks a screener, and is named.

No browser, no stack: the bodies off the back-test files, the walk's decision on doubles."""
from __future__ import annotations

import dataclasses
import inspect
from pathlib import Path

import pytest

from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from stack.config import load_config
from tests import v9_fixtures as fx

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
TOKEN = "tok-102"


def _bt(name: str):
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / f"{name}.yaml"
    if not path.is_file():
        pytest.skip(f"no back-test entry {path}")
    return corpus_mod.load_file(path, registry=fx.registry(), backtest=True)


def _scoped(entry, scope: str):
    return dataclasses.replace(entry, scope=scope)


PICK = vs.Pick(dimension="commercial.commitment", codes=["yes_start"])


def _person(*, link=vs.LINK_PRIMARY, recency=True, story="I lost the thread at dinner.", chip=None, gate=True,
            in_segment=True) -> vs.PersonInputs:
    return vs.PersonInputs(person="Harriet Coleman", link=link, recency=recency, story=story, anchor_chip=chip,
                           picks=[PICK], pilot_opt_in=False, anchoring="ANCHORED", in_segment=in_segment, gate=gate)


ANSWERS = [PICK.as_wire(TOKEN)]


# ----------------------------------------------------------------------------------------------- FR-1: the body

def test_off_the_gate_the_full_links_body_is_the_answers_alone():
    """The aircaps stop: the page sent `{answers, followUps, pilotOptIn}`; the harness expected the gate's shape."""
    assert _person(gate=False).response(TOKEN) == {"answers": ANSWERS}


def test_off_the_gate_the_files_chip_is_dropped_and_the_items_answered():
    """A story chip is the gate's; money alone never asks it, so the person answers part 3 (13-aircaps, Naomi Adler)."""
    person = _person(gate=False, story=None, chip="CANT_RECALL")
    assert person.response(TOKEN) == {"answers": ANSWERS}
    assert person.ends_on_chip is False


def test_with_the_gate_the_full_links_body_is_as_today():
    assert _person().response(TOKEN) == {"recency": True, "answers": ANSWERS, "story": "I lost the thread at dinner."}
    assert _person(story=None, chip="CANT_RECALL").response(TOKEN) == {
        "recency": True, "anchorChip": "CANT_RECALL", "answers": []}
    assert _person(story=None, chip="CANT_RECALL").ends_on_chip is True
    assert _person(recency=False).response(TOKEN) == {"recency": False, "answers": []}


@pytest.mark.parametrize("gate", [True, False])
def test_the_decision_makers_link_is_as_today(gate):
    person = _person(link=vs.LINK_B2B, recency=None, story=None, gate=gate)
    assert person.response(TOKEN) == {"answers": ANSWERS}


def test_outside_the_segment_sends_outside_alone_on_or_off_the_gate():
    for gate in (True, False):
        assert _person(in_segment=False, recency=None, gate=gate).response(TOKEN) == {
            "outsideSegment": True, "answers": []}


def test_aircaps_money_alone_is_twenty_people_and_no_body_carries_the_gate():
    """13-aircaps under COMMERCIAL: all 20 on the one FULL link, none served the gate; every body walked is the answers
    alone. The three gate Noes of the file are refused by name (FR-2) -- the spec's *the corpus has none today* is
    wrong: every consumer entry records gate Noes (tasks.md)."""
    money = _scoped(_bt("13-aircaps"), "COMMERCIAL")
    people = vs.person_inputs(money)
    assert len(people) == 20 and {p.link for p in people} == {vs.LINK_PRIMARY}
    assert not any(p.gate for p in people)
    bodies, refused = {}, []
    for p in people:
        try:
            bodies[p.person] = p.response(TOKEN, "month")
        except vs.VectorsScriptError as e:
            refused.append(p.person)
            assert p.person in str(e) and "spec 102 FR-2" in str(e)
    assert sorted(refused) == ["Desmond Hale", "Lucia Ferraro", "Patrick Moran"]
    assert len(bodies) == 17
    assert all(set(b) == {"answers"} and b["answers"] for b in bodies.values()), bodies
    assert "Harriet Coleman" in bodies and "Naomi Adler" in bodies
    assert not any(p.ends_on_chip for p in people)


def test_aircaps_under_the_whole_study_keeps_the_gates_body():
    whole = _scoped(_bt("13-aircaps"), "ALL")
    people = vs.person_inputs(whole)
    assert all(p.gate for p in people)
    harriet = next(p for p in people if p.person == "Harriet Coleman")
    assert harriet.response(TOKEN, "month")["recency"] is True and harriet.response(TOKEN, "month").get("story")
    naomi = next(p for p in people if p.person == "Naomi Adler")
    assert naomi.ends_on_chip and naomi.response(TOKEN)["answers"] == []


@pytest.mark.parametrize("scope, gate", [("PROBLEM", True), ("SOLUTION", True), ("SOLUTION_COMMERCIAL", True),
                                         ("ALL", True), ("COMMERCIAL", False)])
def test_person_inputs_threads_serves_gate(scope, gate):
    assert {p.gate for p in vs.person_inputs(_scoped(_bt("13-aircaps"), scope))} == {gate}


# ------------------------------------------------------------------------------------- FR-2: no gate, no No

def test_a_gate_no_off_the_gate_is_refused_by_name_and_says_what_a_revision_records():
    with pytest.raises(vs.VectorsScriptError) as raised:
        _person(recency=False, story=None, gate=False).response(TOKEN)
    words = str(raised.value)
    assert words.startswith("Harriet Coleman: the file records a gate No")
    assert "money alone serves no gate" in words and "a revision would have to record their money picks" in words


@pytest.mark.parametrize("person, served, want", [
    (_person(gate=True, recency=False), {}, None),                                 # the gate's No: walked to the exit
    (_person(gate=False), {}, None),                                               # inside: walked
    (_person(gate=False, story=None, chip="CANT_RECALL"), {}, None),               # a file chip: walked on part 3
    (_person(link=vs.LINK_B2B, recency=None, gate=False), {}, None),               # the decision-maker's link
    (_person(gate=False, recency=False), {}, vs.NO_ANSWERS_OFF_THE_GATE),
    (_person(gate=False, in_segment=False, recency=None), {}, vs.OUTSIDE_OFF_THE_GATE),
    # keel-cloud 166 / keel-web 145 landed: the screener is served, the person is walked to its exit (spec 100)
    (_person(gate=False, in_segment=False, recency=None), {"condition": {"question": "?"}}, None),
    (_person(gate=True, in_segment=False, recency=None), {}, None),
])
def test_not_walked_off_the_gate(person, served, want):
    got = vs.not_walked_off_the_gate(person, {"kind": "FULL", **served})
    assert got == (want.format(person=person.person) if want else None)


def test_the_walk_takes_the_rungs_for_every_inside_person_off_the_gate():
    """`walks_rungs` in `_answer_one`: off the gate every inside person walked meets the items and the follow-ups."""
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    source = inspect.getsource(cs._answer_one)
    assert 'not getattr(person, "gate", True)' in source
    assert "vs.not_walked_off_the_gate(person, interview)" in source
    assert source.index("not_walked_off_the_gate") < source.index("person.response(token, recall)")


def test_follow_up_lines_off_the_gate_skip_only_the_unwalked():
    """The file's chip person is owed a follow-up line like anyone inside (no chip ends the interview off the gate);
    the gate Noes, who are not walked, are owed none."""
    money = _scoped(_bt("13-aircaps"), "COMMERCIAL")
    lines = vs.follow_up_lines(money, vs.person_inputs(money))
    assert not {"Patrick Moran", "Lucia Ferraro", "Desmond Hale"} & set(lines)
    whole = _scoped(_bt("13-aircaps"), "ALL")
    assert "Naomi Adler" not in vs.follow_up_lines(whole, vs.person_inputs(whole))


# --------------------------------------------------------------------------------- FR-3: no story, no seam

class _J:
    def __init__(self, entry_id: str):
        self.entry = type("E", (), {"id": entry_id})()
        self.stack = type("S", (), {"is_remote": False})()


def test_nobody_speaks_off_the_gate():
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    spoken = dataclasses.replace(_person(), person="Priya Natarajan")
    assert vs.STORY_SPOKEN["01-countly"]["Priya Natarajan"] == "quiet"
    assert cs._speak_for(_J("01-countly"), spoken) == "quiet"                                   # as today
    assert cs._speak_for(_J("01-countly"), dataclasses.replace(spoken, gate=False)) is None
    assert set(vs.STORY_SPOKEN) == {"01-countly", "05-paidly", "07-mulchrun"}                   # the table untouched


# ------------------------------------------------------------------------------- FR-4: outside the segment

class _Response:
    def __init__(self, body):
        self.body = body

    def json(self):
        return self.body


class _Stranger:
    def __init__(self, interview):
        self.request = type("R", (), {"get": lambda _s, *_a, **_k: _Response(interview)})()
        self.closed = False
        self.pages = 0

    def new_page(self):                                                  # never reached: the person is not walked
        self.pages += 1
        raise AssertionError("walked")

    def close(self):
        self.closed = True


def _walk_one(person, interview):
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    stranger = _Stranger(interview)
    j = type("J", (), {"browser": type("B", (), {"new_context": lambda _s: stranger})(), "cloud_base": "http://cloud",
                       "interviews": {}, "findings": [], "strict": False})()
    cs._answer_one(j, person, TOKEN)
    return j, stranger


MONEY_LINK = {"kind": "FULL", "parts": [{"part": 3, "items": []}], "reveal": {"afterPart": 0}}


def test_an_outside_person_off_the_gate_is_named_in_one_finding_and_not_walked():
    """11-issen's Nikos Ferrante under COMMERCIAL: outside the segment, on a money link that serves no screener (spec
    100 moved the words: keel-cloud 166 serves one wherever the people carry a condition)."""
    money = _scoped(_bt("11-issen"), "COMMERCIAL")
    nikos = next(p for p in vs.person_inputs(money) if p.person == "Nikos Ferrante")
    assert not nikos.in_segment and not nikos.gate
    j, stranger = _walk_one(nikos, MONEY_LINK)
    assert [f["what"] for f in j.findings] == [
        "Nikos Ferrante: outside the segment; the money link served no screener (keel-cloud 166 serves `condition` "
        "there -- a project locked before it, or a condition past 20 words, has none), so they are not walked (spec 100)"]
    assert stranger.pages == 0 and stranger.closed


def test_a_gate_no_off_the_gate_is_named_in_one_finding_and_not_walked():
    money = _scoped(_bt("13-aircaps"), "COMMERCIAL")
    patrick = next(p for p in vs.person_inputs(money) if p.person == "Patrick Moran")
    j, stranger = _walk_one(patrick, MONEY_LINK)
    assert len(j.findings) == 1 and j.findings[0]["what"].startswith("Patrick Moran: the file records a gate No")
    assert stranger.pages == 0 and stranger.closed


def test_the_walked_entries_outside_people():
    """The five walked money entries have nobody outside the segment; 11-issen has one."""
    for name in ("08-fresco", "10-palus", "13-aircaps", "17-expanse", "21-codyco"):
        assert all(p.in_segment for p in vs.person_inputs(_scoped(_bt(name), "COMMERCIAL"))), name
    issen = vs.person_inputs(_scoped(_bt("11-issen"), "COMMERCIAL"))
    assert [p.person for p in issen if not p.in_segment] == ["Nikos Ferrante"]
