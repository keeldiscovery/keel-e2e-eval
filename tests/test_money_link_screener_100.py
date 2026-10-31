"""Spec 100 -- the money link is screened (keel-cloud 166, keel-web 145; contract 49, no bump).

On a money-only consumer study the person's link is kind FULL with no gate; it serves the WHICH PEOPLE screener as
`Interview.condition` before the idea card (`reveal.afterPart` 0). An answer outside sends `{outsideSegment: true,
answers: []}` alone, meets the exit and is counted apart (`StandingsView.outsideSegment`, the People row, the Pilot
tile's `notCounted`, Sent's mark).

FR-1: S-016 gains its consumer leg (`scope_journey.consumer_money_entry`, `leg_money_screener`), ten inside and one
outside. FR-2: the walk's money studies answer the screener inside, and a person marked outside answers outside
(`_answer_one` reads the screener wherever served) and is held apart (`hold_outside_apart`). FR-3: SC8 (and SC4 reading
the reveal on the FULL link), `SCOPE_MARKS_VERSION` 3. FR-4: the gate's chip, the decision-maker's screener, nothing
else moves.

No browser, no stack: the mirrors, the seeds, the faults, and `_answer_one` on doubles."""
from __future__ import annotations

import dataclasses
import inspect
from pathlib import Path

import pytest

from evals import corpus_scenario as cs
from evals import interviewer_leg as il
from evals import scope_journey as sj
from evals import scope_marks as sm
from harness import interviews_screens as iv_screens
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from harness.steps import Recorder
from instructions import corpus as corpus_mod
from stack.config import load_config
from tests import v9_fixtures as fx

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
TOKEN = "tok-100"
COUNTLY_ASKS = {"question": "Do you run one or two sites?", "inCodes": ["YES"]}


@pytest.fixture(scope="module")
def countly():
    _corpus, entry = vs.entry_for(KEEL_CLOUD, "01-countly")
    return entry


@pytest.fixture(scope="module")
def seed(countly):
    return sj.consumer_money_entry(countly)


def _bt(name: str):
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / f"{name}.yaml"
    if not path.is_file():
        pytest.skip(f"no back-test entry {path}")
    return corpus_mod.load_file(path, registry=fx.registry(), backtest=True)


def _money_link(condition=COUNTLY_ASKS, **over) -> dict:
    iv = {"kind": "FULL", "parts": [{"part": 3, "items": []}], "reveal": {"afterPart": 0, "what": "Imagine x."},
          "consentText": cs.CONSENT_TEXT, "done": {"thanks": "Thank you -- your answers have gone to Ana."}}
    if condition:
        iv["condition"] = condition
    return {**iv, **over}


# ------------------------------------------------------------------------------- the mirror: keel-cloud chipFrom

@pytest.mark.parametrize("condition, want", [
    ("run one or two sites", "Do you run one or two sites?"),
    ("Run one or two sites.", "Do you run one or two sites?"),
    ("use a baby monitor at night", "Do you use a baby monitor at night?"),         # 166's MoneyStudyScreenerTest
    ("are first-time parents", "Are you first-time parents?"),                     # 166 T007
    ("are past the beginner stage", "Are you past the beginner stage?"),           # 11-issen's drawn condition
    ("  work   at a hotel group in Germany ", "Do you work at a hotel group in Germany?"),
    (" ".join(["word"] * 18), "Do you " + " ".join(["word"] * 18) + "?"),         # 20 words: at the cap
    (" ".join(["word"] * 19), None),                                               # 21 words past the cap: E7
    ("", None), (None, None),
])
def test_chip_from_is_keel_clouds(condition, want):
    assert vs.chip_from(condition) == want


def test_the_decision_makers_chip_reads_the_same_clause():
    """The clause was factored out of `decider_chip`; the decision-maker's chip is unchanged (FR-4)."""
    assert vs.decider_chip("Work at a company with at least 50 employees.", None) == \
        "Does your company have at least 50 employees?"
    assert vs.decider_chip("are past the beginner stage", "language learners") == \
        "Are the language learners you decide for past the beginner stage?"


def test_money_condition_by_study(countly, seed):
    assert vs.money_condition(seed) == COUNTLY_ASKS
    assert vs.money_condition(countly) is None                                     # ALL: the gate's chip
    assert vs.money_condition(sj.problem_entry(countly)) is None
    assert vs.money_condition(sj.money_entry(countly)) is None                     # B2B: no person's link
    assert vs.money_condition(dataclasses.replace(countly, scope="COMMERCIAL")) == COUNTLY_ASKS


def test_money_condition_on_the_back_tests():
    """13-aircaps' context carries no condition (nothing served); 11-issen's does."""
    assert vs.money_condition(dataclasses.replace(_bt("13-aircaps"), scope="COMMERCIAL")) is None
    issen = dataclasses.replace(_bt("11-issen"), scope="COMMERCIAL")
    want = vs.chip_from(vs.segment_of(issen)["condition"])
    assert vs.money_condition(issen) == ({"question": want, "inCodes": ["YES"]} if want else None)


# ------------------------------------------------------------------------------------- the screens a link opens

def test_the_money_link_opens_on_the_screener_then_the_reveal():
    assert vs_screens.first_screens(_money_link()) == ["condition", "reveal"]
    assert vs_screens.first_screens(_money_link(condition=None)) == ["reveal"]


@pytest.mark.parametrize("served, want", [
    (_money_link(), COUNTLY_ASKS),                                                                  # FULL, no gate
    ({"kind": "FULL", "gate": {"condition": {"question": "Gate?"}}, "condition": COUNTLY_ASKS}, {"question": "Gate?"}),
    ({"kind": "FULL", "gate": {"question": "In the last 4 weeks?"}}, None),
    ({"kind": "COMMERCIAL_LINK", "condition": {"question": "Do the x you decide for y?"}},
     {"question": "Do the x you decide for y?"}),
    ({"kind": "COMMERCIAL_LINK"}, None),
])
def test_screener_of_is_keel_webs_condition_of(served, want):
    assert vs_screens.screener_of(served) == want


# ------------------------------------------------------------------------------------------ FR-1: the seed

def test_the_consumer_seed_is_countly_on_its_own_people_and_one_outside(countly, seed):
    assert seed.scope == "COMMERCIAL" and not vs.is_b2b(seed) and not vs.serves_gate(seed)
    people = vs.person_inputs(seed)
    names = [p.person for p in people]
    assert names[-1] == sj.OUTSIDE_PERSON and len(names) == 11
    assert names[:-1] == [p.person for p in countly.people() if p.recency == "yes"]
    assert {p.link for p in people} == {vs.LINK_PRIMARY} and not any(p.gate for p in people)
    assert all(p.in_segment for p in people[:-1]) and not people[-1].in_segment
    assert not any(k.startswith(("problem.", "solution.")) for p in seed.people() for k in p.picks)
    assert vs.study_people(seed) == seed.people()                                  # everyone on the one FULL link
    assert countly.scope == "ALL" and len(countly.answers) > 11                    # the canon entry untouched


def test_the_seeds_bodies(seed):
    """Inside: the answers alone (spec 102); outside: `outsideSegment` alone, the page's own `answers: []`."""
    people = vs.person_inputs(seed)
    for p in people[:-1]:
        assert set(p.response(TOKEN)) == {"answers"} and p.response(TOKEN)["answers"], p.person
    assert people[-1].response(TOKEN) == {"outsideSegment": True, "answers": []}
    assert people[-1].picks == [] and not people[-1].pilot_opt_in


def test_the_seed_is_countlys_alone(countly):
    with pytest.raises(ValueError):
        sj.consumer_money_entry(dataclasses.replace(countly, id="03-lullaby"))
    with pytest.raises(ValueError):
        sj.consumer_money_entry(sj.money_entry(countly))                           # B2B: no person's link


def test_s016_walks_both_links():
    from evals import test_s016_money_only as s016                                 # noqa: PLC0415
    assert inspect.getsource(s016.test_s016_money_only).count("money_entry") == 1
    assert "consumer_money_entry" in inspect.getsource(s016.test_s016_money_only_consumer)
    walk = inspect.getsource(sj.walk)
    assert "leg_money_screener(j)" in walk and walk.index("cs.leg_interview(j)") < walk.index("leg_money_screener(j)")
    assert "cs.hold_outside_apart(j)" in inspect.getsource(sj.leg_scoped_report)


def test_not_walked_off_the_gate_walks_the_outside_person_once_condition_is_served(seed):
    outside = vs.person_inputs(seed)[-1]
    assert vs.not_walked_off_the_gate(outside, _money_link()) is None
    assert vs.not_walked_off_the_gate(outside, _money_link(condition=None)) == \
        vs.OUTSIDE_OFF_THE_GATE.format(person=sj.OUTSIDE_PERSON)


# ----------------------------------------------------------------------- the screener's screen, then the reveal

def _condition_screen(answered="YES", **over):
    return {"screen": "condition", "question": COUNTLY_ASKS["question"], "kicker": None,
            "options": [vs_screens.IV_CHIP_WORD["YES"], vs_screens.IV_CHIP_WORD["NO"]], "continue_before": False,
            "continue_after": True, "back": 0, "answered": answered, **over}


def test_condition_screen_faults_on_the_money_link():
    served = _money_link()
    assert cs.condition_screen_faults(served, [_condition_screen(), {"screen": "reveal"}]) == []
    assert cs.condition_screen_faults(served, [_condition_screen("NO")], inside=False) == []
    assert cs.condition_screen_faults(served, [_condition_screen(), {"screen": "item"}])           # the reveal skipped
    assert cs.condition_screen_faults(served, [_condition_screen(kicker="One more thing"), {"screen": "reveal"}])
    assert cs.condition_screen_faults(_money_link(condition=None), [_condition_screen()])        # drawn, not served
    assert cs.condition_screen_faults(_money_link(condition=None), [{"screen": "reveal"}]) == []


def test_condition_screen_faults_on_the_decision_makers_link_unchanged():
    served = {"kind": "COMMERCIAL_LINK", "condition": COUNTLY_ASKS, "idea": {"what": "Imagine x."}}
    assert cs.condition_screen_faults(served, [_condition_screen(), {"screen": "idea"}]) == []
    assert cs.condition_screen_faults(served, [_condition_screen(), {"screen": "item"}])
    assert cs.condition_screen_faults(served, [_condition_screen("NO")], inside=False) == []


def test_the_screens_hold_reads_the_screener_on_the_money_link():
    source = inspect.getsource(cs._hold_the_screens)
    assert 'interview.get("kind") == "COMMERCIAL_LINK" or not interview.get("gate")' in source


# ---------------------------------------------------------------- FR-2: _answer_one on doubles, outside walked

class _Response:
    def __init__(self, body):
        self.body = body

    def json(self):
        return self.body


class _Stranger:
    def __init__(self, interview):
        self.request = type("R", (), {"get": lambda _s, *_a, **_k: _Response(interview)})()
        self.closed = False

    def new_page(self):
        return object()

    def add_init_script(self, _script):
        raise AssertionError("no seam off the gate")

    def close(self):
        self.closed = True


class _Screens:
    """`vs_screens.Interview` as the page draws the money link for an outside person: the screener, then the exit."""
    walked_as: list = []

    def __init__(self, _page, _recorder):
        self.camera = None

    def open(self, _url):
        pass

    def walk(self, person, interview, by_item, **_kw):
        _Screens.walked_as.append((person.person, person.in_segment))
        screener = vs_screens.screener_of(interview) or {}
        code = "YES" if person.in_segment else "NO"
        return {"body": {"outsideSegment": True, "answers": []}, "status": 201, "done": cs.EXIT_TITLE,
                "done_screen": False, "pilot_box": 0, "word_drawn": 0, "seen": [], "unanswered": [],
                "screens": [_condition_screen(code, question=screener.get("question"), outside=not person.in_segment)],
                "closed_price": [], "retried": [], "follow_up_route": {}, "follow_up": None, "follow_up_routes": [],
                "follow_ups": [], "late": [], "speak": None, "transcribed": [],
                "consent": {"heading": "", "text": cs.CONSENT_TEXT}}


def _journey(tmp_path, entry, interview, *, strict):
    j = cs.Journey(recorder=Recorder(tmp_path), page=None, context=None, web_base="", cloud_base="http://cloud",
                   entry=entry, founder=None, people=[], project_id="p1", scope="COMMERCIAL")
    j.strict = strict
    j.idea_name = "x"                                                              # the reveal's *Imagine x.*
    j.browser = type("B", (), {"new_context": lambda _s: _Stranger(interview)})()
    return j


def test_the_outside_person_on_the_consumer_money_link_meets_the_exit(tmp_path, seed, monkeypatch):
    """S-016's outside person: walked (no 102 finding), outside (never turned inside), the body held."""
    monkeypatch.setattr(cs.vs_screens, "Interview", _Screens)
    _Screens.walked_as = []
    outside = vs.person_inputs(seed)[-1]
    j = _journey(tmp_path, seed, _money_link(occasion=vs.occasion(seed)), strict=True)
    j.links[outside.person] = "http://web/i/tok-100"
    cs._answer_one(j, outside, TOKEN)
    assert _Screens.walked_as == [(sj.OUTSIDE_PERSON, False)]
    assert j.findings == [] and j.walked[sj.OUTSIDE_PERSON]["body"] == {"outsideSegment": True, "answers": []}
    assert cs.outside_people(j.walked) == [sj.OUTSIDE_PERSON]


def test_a_back_tests_outside_person_answers_the_money_links_screener_outside(tmp_path, monkeypatch):
    """11-issen's Nikos Ferrante under COMMERCIAL, where the link serves the screener: walked outside, not turned
    inside by spec 067 FR-6's fallback (which read `gate.condition` alone), and named in no finding."""
    monkeypatch.setattr(cs.vs_screens, "Interview", _Screens)
    _Screens.walked_as = []
    money = dataclasses.replace(_bt("11-issen"), scope="COMMERCIAL")
    nikos = next(p for p in vs.person_inputs(money) if p.person == "Nikos Ferrante")
    j = _journey(tmp_path, money, _money_link({"question": "Are you past the beginner stage?", "inCodes": ["YES"]}),
                 strict=False)
    j.links[nikos.person] = "http://web/i/tok-100"
    cs._answer_one(j, nikos, TOKEN)
    assert _Screens.walked_as == [("Nikos Ferrante", False)]
    assert j.findings == []


# ------------------------------------------------------------------------------ FR-1 / FR-2: counted apart

def _standings(outside=1, answered=10, invited=11, not_counted="Not counted: 1 outside who the study is for."):
    per_link = {"link": "PRIMARY", "words": "the people you asked", "optedIn": 3, "finished": answered}
    if not_counted:
        per_link["notCounted"] = not_counted
    return {"outsideSegment": outside, "people": {"invited": invited, "answered": answered},
            "pilot": {"perLink": [per_link]}}


def _people_view(outside=(sj.OUTSIDE_PERSON,), inside=("Priya Natarajan",)):
    rows = [{"personName": n, "outsideSegment": True} for n in outside] + [{"personName": n} for n in inside]
    return {"roles": [{"roleId": "r", "invitations": rows}]}


def test_outside_apart_faults_none_when_counted_apart():
    marks = {sj.OUTSIDE_PERSON: iv_screens.OUTSIDE_SEGMENT_MARK, "Priya Natarajan": None}
    assert cs.outside_apart_faults(_standings(), _people_view(), [sj.OUTSIDE_PERSON], marks) == []
    assert cs.outside_apart_faults(_standings(0, 10, 10, None), _people_view(outside=()), []) == []


@pytest.mark.parametrize("standings, view, marks", [
    (_standings(outside=0), _people_view(), {}),                                    # not counted apart
    (_standings(answered=11), _people_view(), {}),                                  # counted as answered
    (_standings(), _people_view(outside=()), {}),                                   # no People row
    (_standings(), {"roles": [{"invitations": [{"personName": sj.OUTSIDE_PERSON},
                                               {"personName": "Priya Natarajan"}]}]}, {}),   # row without the flag
    (_standings(), _people_view(inside=()) | {"roles": [{"invitations": [
        {"personName": sj.OUTSIDE_PERSON, "outsideSegment": True},
        {"personName": "Priya Natarajan", "outsideSegment": True}]}]}, {}),         # an inside person flagged
    (_standings(not_counted=None), _people_view(), {}),                             # the tile's line missing
    (_standings(not_counted="Not counted: 2 outside who the study is for."), _people_view(), {}),
    (_standings(), _people_view(), {sj.OUTSIDE_PERSON: None}),                      # Sent draws no mark
    (_standings(), _people_view(), {"Priya Natarajan": iv_screens.OUTSIDE_SEGMENT_MARK}),
])
def test_outside_apart_faults_each(standings, view, marks):
    assert cs.outside_apart_faults(standings, view, [sj.OUTSIDE_PERSON], marks)


def test_hold_outside_apart_strict_and_on_a_back_test(tmp_path):
    walked = {sj.OUTSIDE_PERSON: {"body": {"outsideSegment": True, "answers": []}, "status": 201},
              "Priya Natarajan": {"body": {"answers": [{}]}, "status": 201}}

    def journey(strict, standings):
        j = cs.Journey(recorder=Recorder(tmp_path / str(strict)), page=None, context=None, web_base="",
                       cloud_base="", entry=None, founder=None, people=[], project_id="p1", scope="COMMERCIAL")
        j.strict, j.walked = strict, dict(walked)
        j.get = lambda path: standings if path.endswith("/standings") else _people_view()
        return j
    record = cs.hold_outside_apart(journey(True, _standings()))
    assert record["faults"] == [] and record["outside"] == [sj.OUTSIDE_PERSON]
    with pytest.raises(AssertionError):
        cs.hold_outside_apart(journey(True, _standings(outside=0)))
    j = journey(False, _standings(outside=0))
    cs.hold_outside_apart(j)
    assert j.findings and "not counted apart (spec 100)" in j.findings[0]["what"]
    nobody = journey(True, _standings())
    nobody.walked = {"Priya Natarajan": walked["Priya Natarajan"]}
    assert cs.hold_outside_apart(nobody) is None


def test_the_standings_settle_with_the_outside_counted_apart(monkeypatch):
    """Ten answered and one outside of eleven invited is every link answered: read at once, no wait."""
    monkeypatch.setattr(cs.time, "sleep", lambda _s: (_ for _ in ()).throw(AssertionError("waited")))
    j = type("J", (), {"project": lambda _s, p: p, "get": lambda _s, _p: _standings(), "standings": None})()
    cs._await_standings(j)
    assert j.standings["outsideSegment"] == 1


# ------------------------------------------------------------------------------- FR-1: the money link's leg

def _walked_inside():
    return {"body": {"answers": [{"itemId": "i"}], "pilotOptIn": False}, "status": 201,
            "screens": [_condition_screen(), {"screen": "reveal"}, {"screen": "item"}]}


def _walked_outside():
    return {"body": {"outsideSegment": True, "answers": []}, "status": 201, "done": cs.EXIT_TITLE,
            "done_screen": False, "pilot_box": 0, "screens": [_condition_screen("NO")]}


def test_money_link_faults_none_on_the_served_shape():
    interviews = {"Priya Natarajan": _money_link(), sj.OUTSIDE_PERSON: _money_link(), "Unwalked": _money_link()}
    walked = {"Priya Natarajan": _walked_inside(), sj.OUTSIDE_PERSON: _walked_outside()}
    assert sj.money_link_faults(interviews, walked, COUNTLY_ASKS) == []
    plain = {"Priya Natarajan": _money_link(condition=None)}
    inside = dict(_walked_inside(), screens=[{"screen": "reveal"}, {"screen": "item"}])
    assert sj.money_link_faults(plain, {"Priya Natarajan": inside}, None) == []


@pytest.mark.parametrize("interview, walked", [
    (_money_link(gate={"question": "In the last 4 weeks?"}), _walked_inside()),
    (_money_link(reveal={"afterPart": 1}), _walked_inside()),
    (_money_link(condition=None), _walked_inside()),
    (_money_link(condition={"question": "Are you a restaurant manager?", "inCodes": ["YES"]}), _walked_inside()),
    (_money_link(), dict(_walked_inside(), screens=[{"screen": "reveal"}])),
    (_money_link(), dict(_walked_inside(), body={"recency": True, "answers": []})),
    (_money_link(), dict(_walked_outside(), body={"outsideSegment": True, "answers": [{"itemId": "i"}]})),
    (_money_link(), dict(_walked_outside(), status=422)),
    (_money_link(), dict(_walked_outside(), screens=[_condition_screen("NO"), {"screen": "reveal"}])),
    (_money_link(), dict(_walked_outside(), done="Thank you", done_screen=True)),
])
def test_money_link_faults_each(interview, walked):
    assert sj.money_link_faults({"P": interview}, {"P": walked}, COUNTLY_ASKS)


# --------------------------------------------------------------------------------------- FR-3: SC8 and SC4

def _consumer_record():
    problem = "Independent restaurant managers lose time whenever a delivery does not match its invoice."
    items = [{"dimension": d, "kicker": f"Part 1 of 1 · The money · {n} of 2"}
             for n, d in enumerate(("commercial.price", "commercial.commitment"), 1)]
    iv = _money_link(parts=[{"part": 3, "items": items}],
                     reveal={"afterPart": 0, "what": "Imagine x.", "problem": problem, "kicker": "Part 1 of 1"})
    standings = {"scope": "COMMERCIAL", "question": "Will they pay?", "gateFact": None,
                 "vectors": [{"vector": "COMMERCIAL", "verdict": "HOLDING_UP"}],
                 "ship": [{"vector": "COMMERCIAL", "verdict": "HOLDING_UP"}],
                 "facts": {"vectors": [{"vector": "COMMERCIAL"}], "decision": {"label": "BUILD"}}}
    return {"scope": "COMMERCIAL", "b2b": False,
            "choose": {"picked": {"plan": {"scope": "money", "badge": "Money", "lines": sm.PLAN_LINES["COMMERCIAL"]}}},
            "created": "COMMERCIAL", "served_scope": "COMMERCIAL",
            "kickers": [("commercial.price", "STEP 4 OF 5 · WILL THEY PAY")], "idea_kicker": "STEP 3 OF 5 · YOUR IDEA",
            "counters": ["1 of 2", "2 of 2"], "kinds": ["FULL"], "links": 2, "people": 2,
            "interviews": {"A": iv, "O": dict(iv)}, "pilot_boxes": {"A": 1, "O": 0}, "done": {"A": "Thank you"},
            "idea_screens": {"A": {"screen": "reveal", "card": "Imagine x.", "problem": problem}},
            "screens": {"A": ["condition", "reveal", "item", "item"], "O": ["condition"]}, "outside": ["O"],
            "money_condition": COUNTLY_ASKS, "problem_sentence": problem, "standings": standings,
            "overview": {"question": "Will they pay?", "verdict": {"label": "BUILD", "text": "Build"},
                         "stages_class": "rp-stages rp-stages--one", "panels": ["COMMERCIAL"],
                         "tiles": {"present": True, "class": "rp-tiles", "names": ["pilot", "price"]},
                         "gatefact": None, "ship": ["COMMERCIAL"], "tabs": ["overview", "insights", "pilot"]}}


def test_the_consumer_money_study_meets_all_eight_marks():
    card = sm.score(_consumer_record())
    assert sm.SCOPE_MARKS_VERSION == 3 and sm.MARKS[-1] == "SC8"
    assert card["met"] == card["of"] == 8, card["checks"]


@pytest.mark.parametrize("mark, change", [
    ("SC8", lambda r: r["interviews"]["A"].pop("condition")),                       # not served
    ("SC8", lambda r: r["interviews"]["A"].update(condition={"question": "Other?", "inCodes": ["YES"]})),
    ("SC8", lambda r: r.update(money_condition=None)),                              # served where none is owed
    ("SC8", lambda r: r["screens"].update(A=["reveal", "item"])),                   # the screener not drawn first
    ("SC8", lambda r: r["screens"].update(O=["condition", "reveal"])),              # outside went on
    ("SC4", lambda r: r["interviews"]["A"]["reveal"].update(problem=None)),         # v3: the reveal read on FULL
    ("SC4", lambda r: r["idea_screens"]["A"].update(problem=None)),
])
def test_each_consumer_mark_fails_on_its_own_fault(mark, change):
    record = _consumer_record()
    change(record)
    checks = {c["mark"]: c for c in sm.score(record)["checks"]}
    assert not checks[mark]["ok"], checks[mark]
    assert sum(1 for c in checks.values() if not c["ok"]) == 1, checks


def test_sc4_holds_no_outside_person_to_the_card():
    record = _consumer_record()
    assert "O" not in record["idea_screens"]
    assert sm.sc4(record)["ok"]
    record["outside"] = []
    assert not sm.sc4(record)["ok"]                                                 # inside, the card is owed


def test_sc8_where_the_gate_is_served_and_on_b2b_money_alone():
    gated = {"scope": "PROBLEM", "interviews": {"A": {"kind": "FULL", "gate": {"condition": COUNTLY_ASKS}}}}
    assert sm.sc8(gated)["ok"]
    gated["interviews"]["A"]["condition"] = COUNTLY_ASKS
    assert not sm.sc8(gated)["ok"]                                                  # never beside the gate
    b2b = sm.sc8({"scope": "COMMERCIAL", "interviews": {"A": {"kind": "COMMERCIAL_LINK", "condition": COUNTLY_ASKS}}})
    assert b2b["ok"] and "no person's link" in b2b["why"]


def test_the_record_carries_what_sc8_reads():
    source = inspect.getsource(sj.record_of)
    for key in ('"screens":', '"outside": cs.outside_people(j.walked)', '"money_condition": vs.money_condition(j.entry)',
                'in ("idea", "reveal")'):
        assert key in source, key


# ------------------------------------------------------------------------------- FR-1: the AI door's leg

class _Player:
    pass


@pytest.mark.parametrize("served, want", [
    (_money_link(), COUNTLY_ASKS),
    ({"kind": "FULL", "gate": {"question": "Q?", "condition": {"question": "Gate?"}}}, {"question": "Gate?"}),
    ({"kind": "FULL", "gate": {"question": "Q?"}}, {}),
    ({"kind": "COMMERCIAL_LINK", "condition": COUNTLY_ASKS}, {}),                   # keel-web 145 FR-3: not asked
])
def test_the_ai_walk_asks_the_screener_the_link_serves(served, want):
    walk = il._Walk(_Player(), served, {"answers": []})
    assert walk.screener == want
