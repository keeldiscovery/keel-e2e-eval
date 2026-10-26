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
