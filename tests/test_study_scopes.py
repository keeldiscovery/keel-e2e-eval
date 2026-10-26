"""Spec 071 -- study scopes in the harness (keel-cloud 133, contract 38; keel-web 109).

FR-1: every golden seed and back-test creates its project with `scope: ALL` -- the choose screen walked by picking
nothing and the create request carried with ALL -- and the project is held to it on the overview and the list.
"""

from __future__ import annotations

import json

import pytest

from evals import corpus_scenario as cs
from harness import browser
from harness.steps import Recorder


# ------------------------------------------------------------------------------------- FR-1: the create request

def test_the_create_request_carries_the_scope_and_nothing_else_moves():
    sent = json.loads(browser.with_scope(json.dumps({"name": "Countly", "scope": "PROBLEM",
                                                     "market": {"country": "US"}}), "ALL"))
    assert sent == {"name": "Countly", "scope": "ALL", "market": {"country": "US"}}
    assert json.loads(browser.with_scope(json.dumps({"name": "x"}), "COMMERCIAL"))["scope"] == "COMMERCIAL"


@pytest.mark.parametrize("scope", ["", "all", "MONEY", "SOLUTION+COMMERCIAL"])
def test_a_scope_the_wire_does_not_take_is_refused(scope):
    with pytest.raises(ValueError):
        browser.with_scope("{}", scope)
    with pytest.raises(ValueError):
        browser.ScopeRewrite(scope)


def test_the_five_scopes_are_contract_38s():
    assert browser.SCOPES == ("PROBLEM", "SOLUTION", "SOLUTION_COMMERCIAL", "COMMERCIAL", "ALL")
    assert set(browser.SCOPE_CARD) == set(browser.SCOPES) - {"ALL"}     # ALL is never offered by the web
    assert browser.SCOPE_DEFAULT == "PROBLEM"                           # keel-web 109 judgement call 1


@pytest.mark.parametrize("method, url, want", [
    ("POST", "http://localhost:18080/v2/projects", True),
    ("POST", "http://localhost:18080/v2/projects/", True),
    ("GET", "http://localhost:18080/v2/projects", False),
    ("POST", "http://localhost:18080/v2/projects/p1/lock", False),
    ("POST", "http://localhost:18080/v2/projects/p1/scope", False),
])
def test_only_the_create_request_is_rewritten(method, url, want):
    assert browser.is_create_request(method, url) is want


class _Request:
    def __init__(self, method, url, body=None):
        self.method, self.url, self.post_data = method, url, body


class _Route:
    def __init__(self):
        self.calls = []

    def continue_(self, **kwargs):
        self.calls.append(("continue", kwargs))

    def fallback(self, **kwargs):
        self.calls.append(("fallback", kwargs))


def test_the_rewrite_is_one_shot_and_lets_everything_else_through():
    rewrite = browser.ScopeRewrite("ALL")
    url = "http://localhost:18080/v2/projects"
    listed, created, again = _Route(), _Route(), _Route()
    rewrite(listed, _Request("GET", url))
    rewrite(created, _Request("POST", url, json.dumps({"name": "Countly", "scope": "PROBLEM"})))
    rewrite(again, _Request("POST", url, json.dumps({"name": "Second", "scope": "PROBLEM"})))
    assert listed.calls == [("fallback", {})]
    (what, kwargs), = created.calls
    assert what == "continue" and json.loads(kwargs["post_data"]) == {"name": "Countly", "scope": "ALL"}
    assert rewrite.seen == {"web": "PROBLEM", "sent": "ALL"}
    assert again.calls == [("fallback", {})]


# ------------------------------------------------------------------------------- FR-1: the project held to it

def _journey(tmp_path, scope="ALL", served=None, listed=None, choose=None):
    j = cs.Journey(recorder=Recorder(tmp_path), page=None, context=None, web_base="", cloud_base="", entry=None,
                   founder=None, people=[], project_id="p1", scope=scope)
    served = served if served is not None else {"scope": scope}
    listed = listed if listed is not None else {"projects": [{"projectId": "p1", "scope": scope}]}
    j.get = lambda path: served if path.endswith("/overview") else listed
    if choose is not None:
        j.changed["choose"] = choose
    return j


ALL_CHOOSE = {"scope": "ALL", "opened": {"cards": [{"pick": "problem", "checked": True},
                                                   {"pick": "solution", "checked": False},
                                                   {"pick": "money", "checked": False}]},
              "create": {"web": "PROBLEM", "sent": "ALL"}}


def test_an_all_project_is_held_on_the_overview_the_list_and_the_request(tmp_path):
    cs._hold_the_scope(_journey(tmp_path, choose=ALL_CHOOSE))


def test_a_project_the_web_created_as_problem_fails_an_all_journey(tmp_path):
    with pytest.raises(AssertionError):
        cs._hold_the_scope(_journey(tmp_path, served={"scope": "PROBLEM"}, choose=ALL_CHOOSE))
    with pytest.raises(AssertionError):
        cs._hold_the_scope(_journey(tmp_path, choose={**ALL_CHOOSE, "create": {"web": "PROBLEM", "sent": "PROBLEM"}}))
    with pytest.raises(AssertionError):
        cs._hold_the_scope(_journey(tmp_path, listed={"projects": [{"projectId": "p1", "scope": "PROBLEM"}]}))


def test_a_scoped_project_is_held_to_its_own_scope(tmp_path):
    cs._hold_the_scope(_journey(tmp_path, scope="COMMERCIAL", choose={"scope": "COMMERCIAL", "create": {}}))


def test_every_golden_journey_and_back_test_asks_for_all(monkeypatch, tmp_path):
    asked = {}

    def create(page, recorder, web_base, founder, **kwargs):
        asked.update(kwargs)
        return "p1"

    monkeypatch.setattr(cs, "create_project", create)
    monkeypatch.setattr(cs, "_hold_the_scope", lambda j: None)
    monkeypatch.setattr(cs, "_hold_the_other_market", lambda j: None)
    monkeypatch.setattr(cs, "_market_inputs", lambda founder: founder)

    class _Founder:
        country, region, language = "US", None, "en-US"

    j = _journey(tmp_path, served={"scope": "ALL", "market": {"country": "US", "region": None, "language": "en-US"}},
                 listed={"markets": [{"country": "US"}], "other": {}})
    j.founder = _Founder()
    j.entry = type("E", (), {"id": "01-countly"})()
    assert cs.Journey.__dataclass_fields__["scope"].default == "ALL"
    cs.leg_project(j)
    assert asked["scope"] == "ALL"
