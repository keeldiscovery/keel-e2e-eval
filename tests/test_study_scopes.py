"""Spec 071 -- study scopes in the harness (keel-cloud 133, contract 38; keel-web 109).

FR-1: every golden seed and back-test creates its project with `scope: ALL` -- the choose screen walked by picking
nothing and the create request carried with ALL -- and the project is held to it on the overview and the list.
"""

from __future__ import annotations

import dataclasses
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


# ------------------------------------------------------------------- FR-2 / FR-3: the scoped seeds and their walks

from evals import scope_journey as sj                                         # noqa: E402
from evals import scope_marks as sm                                           # noqa: E402
from harness import vectors_screens as vs_screens                             # noqa: E402
from harness import vectors_script as vs                                      # noqa: E402
from stack.config import load_config                                          # noqa: E402


@pytest.fixture(scope="module")
def countly():
    _corpus, entry = vs.entry_for(load_config(validate=False).keel_cloud, "01-countly")
    return entry


def test_the_golden_walk_is_unchanged_under_all(countly):
    """FR-1 / FR-6: an entry as written is ALL, and its script, plan and people are exactly today's."""
    assert countly.scope == "ALL" and vs.scope_vectors(countly) == vs.VECTORS
    assert [v for v, _ in vs.calibration_jobs(countly)] == ["PROBLEM"] * 3 + ["SOLUTION"] * 4 + ["COMMERCIAL"] * 3
    assert vs.respondent_jobs(countly) == [(1, vs.LINK_PRIMARY)]
    assert set(vs.generate(countly).screens) == {"CONTEXT_INTERPRET", "PROBLEM_INTERPRET", "SOLUTION_MECHANISM",
                                                 "CALIBRATION_QUESTIONS", "ASKED", "RESPONDENT_QUESTIONS",
                                                 "INTERPRET", "THEMES"}
    assert all(vs.serves_part(countly, part, vs.LINK_PRIMARY) for part in (1, 2, 3))
    assert vs.read_back(countly).endswith(", counting the last 4 weeks.")
    assert cs.before_counters() == ["1 of 3", "2 of 3", "3 of 3"]
    assert [vs_screens.stage_exit(v) for v in vs.VECTORS] == [vs_screens.STAGE_EXIT[v] for v in vs.VECTORS]
    assert vs.chained_out_of_scope(countly) == ()


def test_the_problem_seed_is_countly_with_its_own_problem_numbers(countly):
    seed = sj.problem_entry(countly)
    assert seed.scope == "PROBLEM" and seed.id == countly.id and seed.answers == countly.answers
    assert set(seed.expected["standings"]) == {"problem.prevalence", "problem.frequency", "problem.importance",
                                               "problem.current_solution_satisfaction"}
    assert seed.expected["standings"] == {k: v for k, v in countly.expected["standings"].items()
                                          if k.startswith("problem.")}
    assert seed.expected["vector_verdicts"] == {"PROBLEM": countly.expected["vector_verdicts"]["PROBLEM"]}
    with pytest.raises(ValueError):
        sj.problem_entry(dataclasses.replace(countly, id="05-paidly"))


def test_the_problem_study_s_expected_walk(countly):
    """FR-2: the scripted walk the problem study runs -- the problem's slice and its two redrafts, part 1's one job,
    no mechanism and no faces; each manager asked part 1 alone and never the pilot; the gate counted."""
    seed = sj.problem_entry(countly)
    script = vs.generate(seed).screens
    assert set(script) == {"CONTEXT_INTERPRET", "PROBLEM_INTERPRET", "CALIBRATION_QUESTIONS", "RESPONDENT_QUESTIONS",
                           "INTERPRET", "THEMES"}
    assert [r["result"]["vector"] for r in script["CALIBRATION_QUESTIONS"]] == ["PROBLEM"] * 3
    (questions,) = script["RESPONDENT_QUESTIONS"]
    assert [i["key"] for i in questions["result"]["items"]] == vs.plan_keys(countly, 1, vs.LINK_PRIMARY)
    assert vs.plan_keys(seed, 2, vs.LINK_PRIMARY) == vs.plan_keys(seed, 3, vs.LINK_PRIMARY) == []
    assert vs.serves_gate(seed) and vs.gate_counts(seed) and vs.primary_link(seed)
    people = vs.person_inputs(seed)
    assert len(people) == 12 and {p.link for p in people} == {vs.LINK_PRIMARY}
    assert all({k.dimension for k in p.picks} <= {"problem.frequency", "problem.importance",
                                                   "problem.current_solution_satisfaction"} for p in people)
    assert not any(p.pilot_opt_in for p in people)                    # no pilot box in the problem study
    assert cs.before_counters("PROBLEM") == ["1 of 2", "2 of 2"]
    assert vs_screens.stage_exit("PROBLEM", "PROBLEM") == "Save and continue to Before people see it"
    assert vs_screens.step_of("problem", "PROBLEM") == (2, 3)
    assert vs.chained_out_of_scope(seed) == ()


def test_the_money_seed_is_countly_with_the_owner_deciding(countly):
    seed = sj.money_entry(countly)
    assert seed.scope == "COMMERCIAL" and vs.is_b2b(seed) and seed.decision_maker_role() == "owner"
    assert seed.decider_title() == sj.OWNER_TITLE
    assert [p.person for p in seed.people()] == list(sj.OWNER_PICKS)
    assert {p.link for p in seed.people()} == {vs.LINK_B2B}
    priya = seed.person("Priya Natarajan")
    assert priya.picks["commercial.existing_sacrifice"] == {"mode": "AMOUNT", "value": 200, "currency": "USD",
                                                            "period": "quarter"}           # 10 hours at $20
    assert priya.picks["commercial.ability_to_pay"] == "existing_line"
    assert not any(k.startswith(("problem.", "solution.")) for p in seed.people() for k in p.picks)
    assert seed.founder_calibration["commercial.purchase_friction"] == sj.FRICTION
    assert countly.founder_calibration.get("commercial.purchase_friction") is None     # the canon entry untouched
    with pytest.raises(ValueError):
        sj.money_entry(dataclasses.replace(countly, id="03-lullaby"))


def test_money_alone_s_expected_walk(countly):
    """FR-3: no recall window, no gate, no part-1 job and no faces; the mechanism (the idea card) and the money slice
    with its three redrafts -- and DRIFT #97's two chained out-of-scope slices before them; the decision-maker's link
    alone, part 3 on it."""
    seed = sj.money_entry(countly)
    script = vs.generate(seed).screens
    assert set(script) == {"CONTEXT_INTERPRET", "PROBLEM_INTERPRET", "SOLUTION_MECHANISM", "CALIBRATION_QUESTIONS",
                           "THEMES"}
    assert [r["result"]["vector"] for r in script["CALIBRATION_QUESTIONS"]] == [
        "PROBLEM", "SOLUTION", "COMMERCIAL", "COMMERCIAL", "COMMERCIAL", "COMMERCIAL"]
    assert vs.chained_out_of_scope(seed) == ("PROBLEM", "SOLUTION")
    assert vs.respondent_jobs(seed) == [] and not vs.serves_gate(seed) and not vs.primary_link(seed)
    assert [vs.plan_keys(seed, part, vs.LINK_PRIMARY) for part in (1, 2, 3)] == [[], [], []]
    assert vs.plan_keys(seed, 3, vs.LINK_B2B) == ["commercial.existing_sacrifice", "commercial.price",
                                                  "commercial.ability_to_pay", "commercial.buyer_payer_alignment",
                                                  "commercial.purchase_friction", "commercial.commitment"]
    assert vs.read_back(seed, window=False).endswith("matching what is on the shelves.")
    assert "counting" not in vs.read_back(seed, window=False)
    assert cs.before_counters("COMMERCIAL") == ["1 of 3", "2 of 3", "3 of 3"]
    assert vs_screens.step_of("solution", "COMMERCIAL") == (3, 5)
    assert sj.problem_sentence(countly.interpretations["problem"]) == (
        "Independent restaurant managers lose time whenever a delivery does not match its invoice.")


@pytest.mark.parametrize("statement, want", [
    ("A long one; with a second clause.", None),                       # under six words once cut
    ("Freelance translators wait months for agency invoices to be paid (most of them), based on interviews.",
     "Freelance translators wait months for agency invoices to be paid."),
    (" ".join(["word"] * 25) + ".", " ".join(["word"] * 20) + "."),
])
def test_the_problem_sentence_mirror(statement, want):
    assert sj.problem_sentence(statement) == want


@pytest.mark.parametrize("text, faults", [
    ("Independent restaurant managers lose time whenever a delivery does not match its invoice.", []),
    ("Too short here.", ["3 words, under six"]),
    ("Savers lose value to inflation every month. They hold rupees.", ["not one sentence"]),
    ("Learners forget words because nobody runs spaced repetition for them at home.", ["M5 word 'spaced repetition'"]),
])
def test_the_spoken_mirror_on_the_problem_sentence(text, faults):
    assert sm.sentence_faults(text) == faults


@pytest.mark.parametrize("scope, verdicts, want", [
    ("PROBLEM", {"PROBLEM": "HOLDING_UP"}, "BUILD"),
    ("PROBLEM", {"PROBLEM": "PEOPLE_DISAGREE"}, "NOT_YET"),
    ("PROBLEM", {"PROBLEM": "TOO_FEW_TO_CALL"}, "KEEP_INTERVIEWING"),
    ("COMMERCIAL", {"COMMERCIAL": "HOLDING_UP"}, "BUILD"),
    ("COMMERCIAL", {"COMMERCIAL": "NOT_HOLDING_UP"}, "BUILD_BUT_CHANGE"),
    ("COMMERCIAL", {"COMMERCIAL": "NOT_ASKED_YET"}, "KEEP_INTERVIEWING"),
    ("SOLUTION_COMMERCIAL", {"SOLUTION": "HOLDING_UP", "COMMERCIAL": "TOO_FEW_TO_CALL"}, "BUILD_BUT_CHANGE"),
    ("ALL", {"PROBLEM": "HOLDING_UP", "SOLUTION": "HOLDING_UP", "COMMERCIAL": "NOT_TESTED"}, "KEEP_INTERVIEWING"),
])
def test_the_decision_rule(scope, verdicts, want):
    assert sm.decision_by_rule(scope, verdicts) == want


def _problem_record():
    gate = {"question": "In the last 4 weeks, did ...?"}
    items = [{"dimension": d, "kicker": f"Part 1 of 1 · {n} of 3"} for n, d in
             enumerate(("problem.frequency", "problem.importance", "problem.current_solution_satisfaction"), 1)]
    standings = {"scope": "PROBLEM", "question": "Should you build it?", "gateFact": None,
                 "vectors": [{"vector": "PROBLEM", "verdict": "PEOPLE_DISAGREE"}],
                 "ship": [{"vector": "PROBLEM", "verdict": "PEOPLE_DISAGREE"}],
                 "facts": {"vectors": [{"vector": "PROBLEM"}], "decision": {"label": "NOT_YET"}}}
    return {"scope": "PROBLEM", "b2b": False,
            "choose": {"picked": {"plan": {"scope": "problem", "badge": "Problem",
                                           "lines": ["Prevalence", "Frequency", "Importance", "Current solution"]}}},
            "created": "PROBLEM", "served_scope": "PROBLEM",
            "kickers": [("problem.prevalence", "STEP 2 OF 3 · THE PROBLEM · WHAT DO YOU BELIEVE IS TRUE?")],
            "counters": ["1 of 2", "2 of 2"], "kinds": ["FULL"], "links": 2, "people": 2,
            "interviews": {"A": {"kind": "FULL", "gate": gate, "parts": [{"part": 1, "items": items}], "done": {}},
                           "B": {"kind": "FULL", "gate": gate, "parts": [], "done": {}}},
            "pilot_boxes": {"A": 0, "B": 0}, "done": {"A": "Thank you", "B": "Thank you"},
            "standings": standings,
            "overview": {"question": "Should you build it?", "verdict": {"label": "NOT_YET", "text": "Not yet"},
                         "stages_class": "rp-stages rp-stages--one", "panels": ["PROBLEM"],
                         "tiles": {"present": False, "names": []}, "gatefact": None, "ship": ["PROBLEM"],
                         "tabs": ["overview", "insights"]}}


def test_the_problem_study_s_marks_on_a_stubbed_walk():
    card = sm.score(_problem_record())
    assert card["met"] == card["of"] == 7 and card["version"] == sm.SCOPE_MARKS_VERSION == 1


@pytest.mark.parametrize("mark, change", [
    ("SC1", lambda r: r.update(created="ALL")),
    ("SC2", lambda r: r.update(counters=["1 of 3", "2 of 3", "3 of 3"])),
    ("SC2", lambda r: r.update(kickers=[("problem.prevalence", "Step 2 of 5 · The problem")])),
    ("SC3", lambda r: r.update(kinds=["FULL", "COMMERCIAL_LINK"])),
    ("SC4", lambda r: r["interviews"]["A"].update(done={"pilot": {"label": "Count me in"}})),
    ("SC4", lambda r: r.update(pilot_boxes={"A": 1, "B": 0})),
    ("SC4", lambda r: r["interviews"]["A"]["parts"].append({"part": 2, "items": []})),
    ("SC5", lambda r: r["standings"]["vectors"].append({"vector": "SOLUTION", "verdict": "NOT_TESTED"})),
    ("SC5", lambda r: r["standings"].update(gateFact="10 of 12 had one")),
    ("SC6", lambda r: r["standings"]["facts"].update(decision={"label": "BUILD_BUT_CHANGE"})),
    ("SC7", lambda r: r["overview"].update(tabs=["overview", "insights", "pilot"])),
    ("SC7", lambda r: r["overview"]["tiles"].update(present=True, names=["pilot"])),
    ("SC7", lambda r: r["overview"].update(ship=["PROBLEM", "SOLUTION", "COMMERCIAL"])),
])
def test_each_problem_mark_fails_on_its_own_fault(mark, change):
    record = _problem_record()
    change(record)
    checks = {c["mark"]: c for c in sm.score(record)["checks"]}
    assert not checks[mark]["ok"], checks[mark]
    assert sum(1 for c in checks.values() if not c["ok"]) == 1, checks


def _money_record():
    problem = "Independent restaurant managers lose time whenever a delivery does not match its invoice."
    items = [{"dimension": d, "kicker": f"The buying decision · {n} of 2"}
             for n, d in enumerate(("commercial.price", "commercial.commitment"), 1)]
    iv = {"kind": "COMMERCIAL_LINK", "gate": None, "parts": [{"part": 3, "items": items}],
          "idea": {"what": "Imagine x.", "problem": problem}, "done": {"pilot": {"label": "Count me in"}}}
    standings = {"scope": "COMMERCIAL", "question": "Will they pay?", "gateFact": None,
                 "vectors": [{"vector": "COMMERCIAL", "verdict": "HOLDING_UP"}],
                 "ship": [{"vector": "COMMERCIAL", "verdict": "HOLDING_UP"}],
                 "facts": {"vectors": [{"vector": "COMMERCIAL"}], "decision": {"label": "BUILD"}}}
    return {"scope": "COMMERCIAL", "b2b": True,
            "choose": {"picked": {"plan": {"scope": "money", "badge": "Money", "lines": sm.PLAN_LINES["COMMERCIAL"]}}},
            "created": "COMMERCIAL", "served_scope": "COMMERCIAL",
            "kickers": [("commercial.price", "STEP 4 OF 5 · WILL THEY PAY")], "idea_kicker": "STEP 3 OF 5 · YOUR IDEA",
            "counters": ["1 of 3", "2 of 3", "3 of 3"], "kinds": ["COMMERCIAL_LINK"], "links": 1, "people": 1,
            "interviews": {"A": iv}, "pilot_boxes": {"A": 1}, "done": {"A": "Thank you"},
            "idea_screens": {"A": {"screen": "idea", "card": "Imagine x.", "problem": problem}},
            "problem_sentence": problem, "standings": standings,
            "overview": {"question": "Will they pay?", "verdict": {"label": "BUILD", "text": "Build"},
                         "stages_class": "rp-stages rp-stages--one", "panels": ["COMMERCIAL"],
                         "tiles": {"present": True, "class": "rp-tiles", "names": ["pilot", "price"]},
                         "gatefact": None, "ship": ["COMMERCIAL"], "tabs": ["overview", "insights", "pilot"]}}


def test_money_alone_s_marks_on_a_stubbed_walk():
    card = sm.score(_money_record())
    assert card["met"] == card["of"] == 7, card["checks"]


@pytest.mark.parametrize("mark, change", [
    ("SC2", lambda r: r.update(idea_kicker="STEP 3 OF 5 · YOUR SOLUTION")),
    ("SC3", lambda r: r.update(kinds=["FULL", "COMMERCIAL_LINK"])),
    ("SC4", lambda r: r["interviews"]["A"].update(gate={"question": "In the last 4 weeks, did ...?"})),
    ("SC4", lambda r: r["interviews"]["A"]["idea"].update(problem=None)),
    ("SC4", lambda r: r["idea_screens"]["A"].update(problem=None)),
    ("SC6", lambda r: r["standings"]["facts"].update(decision={"label": "NOT_YET"})),
    ("SC7", lambda r: r["overview"]["tiles"].update(names=["pilot"], **{"class": "rp-tiles rp-tiles--one"})),
    ("SC7", lambda r: r["overview"].update(tabs=["overview", "insights"])),
])
def test_each_money_mark_fails_on_its_own_fault(mark, change):
    record = _money_record()
    change(record)
    checks = {c["mark"]: c for c in sm.score(record)["checks"]}
    assert not checks[mark]["ok"], checks[mark]
