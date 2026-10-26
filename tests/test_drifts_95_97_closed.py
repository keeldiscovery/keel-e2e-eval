"""Spec 072 -- DRIFT #95, #96, #97 closed (keel-cloud 134 / 135, contract 39; keel-web 112): the guards flip.

FR-1 #95: on every study the plan reads complete over the scope before *Lock and approve* is pressed on the page; a
button that stays disabled fails the journey, and nothing locks on the wire round it.
"""

from __future__ import annotations

import pytest

from evals import corpus_scenario as cs
from evals import scope_journey as sj
from harness import vectors_script as vs
from harness.steps import Recorder
from stack.config import load_config


@pytest.fixture(scope="module")
def countly():
    _corpus, entry = vs.entry_for(load_config(validate=False).keel_cloud, "01-countly")
    return entry


def _seed(countly, scope):
    return {"ALL": countly, "PROBLEM": sj.problem_entry(countly), "COMMERCIAL": sj.money_entry(countly)}[scope]


def _journey(tmp_path, entry, plan, persona="SET", calls=None):
    j = cs.Journey(recorder=Recorder(tmp_path), page=None, context=None, web_base="", cloud_base="", entry=entry,
                   founder=None, people=[], project_id="p1", scope=entry.scope)
    j.get = lambda path: plan if path.endswith("/plan") else {"state": persona}

    def call(method, path, body=None, ok=()):
        (calls if calls is not None else []).append((method, path, body))
        return 201, {}

    j.call = call
    return j


def _plan(vectors, complete=True, each=True):
    return {"complete": complete, "vectors": [{"vector": v, "complete": each} for v in vectors]}


# ------------------------------------------------------------------------------------------------ FR-1: #95

@pytest.mark.parametrize("scope, vectors, persona", [
    ("ALL", ["PROBLEM", "SOLUTION", "COMMERCIAL"], "SET"),
    ("PROBLEM", ["PROBLEM"], "NOT_SET"),                       # the problem study's lock composes the type itself
    ("COMMERCIAL", ["COMMERCIAL"], "SET"),
])
def test_the_plan_reads_complete_over_the_scope(tmp_path, countly, scope, vectors, persona):
    j = _journey(tmp_path, _seed(countly, scope), _plan(vectors), persona=persona)
    cs.plan_complete(j)
    assert j.changed["plan_complete"]["complete"] is True
    assert j.changed["plan_complete"]["persona"] == persona


@pytest.mark.parametrize("scope, plan", [
    ("PROBLEM", _plan(["PROBLEM"], complete=False)),                                 # DRIFT #95 as filed
    ("COMMERCIAL", _plan(["COMMERCIAL"], complete=False)),
    ("PROBLEM", _plan(["PROBLEM", "SOLUTION", "COMMERCIAL"])),                       # vectors outside the scope
    ("COMMERCIAL", _plan(["COMMERCIAL"], each=False)),
    ("ALL", _plan(["PROBLEM", "SOLUTION", "COMMERCIAL"], complete=False)),
])
def test_a_plan_that_does_not_read_complete_fails(tmp_path, countly, scope, plan):
    with pytest.raises(AssertionError):
        cs.plan_complete(_journey(tmp_path, _seed(countly, scope), plan))


@pytest.mark.parametrize("scope", ["ALL", "PROBLEM", "COMMERCIAL"])
def test_a_lock_the_page_never_offers_fails_and_nothing_locks_on_the_wire(tmp_path, countly, scope):
    calls: list = []
    j = _journey(tmp_path, _seed(countly, scope), _plan(vs.scope_vectors(_seed(countly, scope)), complete=False),
                 calls=calls)
    with pytest.raises(AssertionError, match="DRIFT.md #95"):
        cs._drift_95_guard(j, {"disabled": True, "button": "Lock and approve"})
    assert calls == []
    assert not hasattr(cs, "_drift_95_lock")


def test_leg_lock_holds_the_plan_then_presses_the_button(tmp_path, countly, monkeypatch):
    seed = _seed(countly, "PROBLEM")
    order: list = []
    j = _journey(tmp_path, seed, _plan(["PROBLEM"]), persona="NOT_SET")

    class _Corridor:
        def word_pilot_and_lock(self, face=None, *, pilot=True):
            order.append(("pressed", pilot))
            return {"counters": ["1 of 2", "2 of 2"], "receipt": {"version": 1}, "l1": {}, "status": 201}

    j.corridor = _Corridor()
    monkeypatch.setattr(cs, "plan_complete", lambda j: order.append("plan"))
    monkeypatch.setattr(cs, "_own_door_l1", lambda j, drawn: None)
    monkeypatch.setattr(cs, "_lock_lands", lambda j: None)
    monkeypatch.setattr(cs, "_drift_95_guard", lambda j, drawn: order.append("guard"))
    cs.leg_lock(j)
    assert order == ["plan", ("pressed", False)]
    assert j.receipt == {"version": 1}


# ------------------------------------------------------------------------------------------------ FR-2: #96

class _Corridor:
    def __init__(self, *sent):
        self.saves = [{"method": "PUT", "status": 202, "sent": b} for b in sent]


FIELDS = {"actor": "a", "job": "j", "circumstance": "c", "segment": "s"}


def _context_journey(tmp_path, entry, *sent):
    j = _journey(tmp_path, entry, {})
    j.corridor = _Corridor(*sent)
    return j


def test_money_alone_sends_draws_and_reads_back_no_window(tmp_path, countly):
    seed = _seed(countly, "COMMERCIAL")
    j = _context_journey(tmp_path, seed, dict(FIELDS), {**FIELDS, "occasion": "delivery"})
    cs._drift_96_guard(j, vs.read_back(seed, window=False), "")
    assert j.changed["drift_96"]["sent"] == [None, None]
    assert "counting" not in j.changed["drift_96"]["understands"]


@pytest.mark.parametrize("sent, drawn, line", [
    ({**FIELDS, "recallWindow": cs.STORED_WINDOW_DEFAULT}, None, ""),                 # DRIFT #96 as filed: the PUT
    (dict(FIELDS), None, "Counting the last 7 nights."),                               # the card's window line
    (dict(FIELDS), "over the default", ""),                                            # the read-back's clause
    ({**FIELDS, "recallWindow": None}, None, ""),                                     # a key sent at all
])
def test_a_window_sent_drawn_or_read_back_on_money_alone_fails(tmp_path, countly, sent, drawn, line):
    seed = _seed(countly, "COMMERCIAL")
    sentence = (vs.read_back(seed, window=vs.Window(7, "NIGHTS")) if drawn else vs.read_back(seed, window=False))
    with pytest.raises(AssertionError):
        cs._drift_96_guard(_context_journey(tmp_path, seed, sent), sentence, line)


def test_the_windowless_read_back_and_the_stored_default():
    assert cs.STORED_WINDOW_DEFAULT == {"count": 7, "unit": "NIGHTS"}           # keel-cloud `RecallWindow.DEFAULT`
    assert not hasattr(cs, "DRIFT_96_WINDOW") and not hasattr(cs, "_drift_96_window")


def test_money_alone_s_read_back_drops_the_clause_the_whole_study_keeps_it(countly):
    seed = _seed(countly, "COMMERCIAL")
    assert not vs.serves_gate(seed) and vs.serves_gate(countly)
    assert vs.read_back(seed, window=False).endswith("matching what is on the shelves.")
    assert vs.read_back(countly).endswith(", counting the last 4 weeks.")


# ------------------------------------------------------------------------------------------------ FR-3: #97

def _jobs_journey(tmp_path, entry, rows):
    j = _journey(tmp_path, entry, {})
    j.get = lambda path: rows
    return j


def _rows(vectors, status="APPLIED"):
    return [{"screen": "CALIBRATION_QUESTIONS", "vector": v, "status": status} for v in vectors] + [
        {"screen": "PROBLEM_INTERPRET", "vector": "PROBLEM", "status": "APPLIED"}]


@pytest.mark.parametrize("scope", ["ALL", "PROBLEM", "COMMERCIAL"])
def test_the_chain_writes_the_scope_s_calibrations_alone(tmp_path, countly, scope):
    seed = _seed(countly, scope)
    assert vs.chained_out_of_scope(seed) == ()
    vectors = [v for v, _ in vs.calibration_jobs(seed)]
    assert set(vectors) == set(vs.scope_vectors(seed))
    j = _jobs_journey(tmp_path, seed, _rows(vectors))
    sj.drift_97(j)
    assert j.changed["drift_97"]["out_of_scope"] == [] and j.changed["drift_97"]["jobs"] == len(vectors)


def test_money_alone_scripts_the_money_slice_and_its_redrafts_alone(countly):
    seed = _seed(countly, "COMMERCIAL")
    assert vs.calibration_jobs(seed)[0] == ("COMMERCIAL", None)
    assert [v for v, _ in vs.calibration_jobs(seed)] == ["COMMERCIAL"] * 4
    assert [r["result"]["vector"] for r in vs.generate(seed).screens["CALIBRATION_QUESTIONS"]] == ["COMMERCIAL"] * 4


@pytest.mark.parametrize("scope, rows", [
    ("COMMERCIAL", _rows(["PROBLEM", "SOLUTION"] + ["COMMERCIAL"] * 4)),     # DRIFT #97 as filed
    ("COMMERCIAL", _rows(["SOLUTION"] + ["COMMERCIAL"] * 4)),
    ("PROBLEM", _rows(["PROBLEM"] * 3 + ["SOLUTION"])),
    ("COMMERCIAL", _rows(["COMMERCIAL"] * 3)),                                # a redraft missing
    ("COMMERCIAL", _rows([])),                                                # no slice for the vector in scope
    ("COMMERCIAL", _rows(["COMMERCIAL"] * 4, status="RESULT_INVALID")),
])
def test_a_calibration_outside_the_scope_or_off_the_script_fails(tmp_path, countly, scope, rows):
    with pytest.raises(AssertionError):
        sj.drift_97(_jobs_journey(tmp_path, _seed(countly, scope), rows))
