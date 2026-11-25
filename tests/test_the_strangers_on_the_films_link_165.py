"""Spec 165: the strangers on the film's link -- the mirrors `make unit` holds, nothing paid (FR-4).

The film's project is the study the people answer: the lock step by step and its refusal naming the step (FR-1, FR-4),
each person's recorded answers mapped onto the four questions (FR-1), the walked rows as the screens the
respondent-reader is handed and the one bundle `make read-screens` reads with no founder screen (FR-2), the walk with no
back-test step and its `walk.json` naming the one project (FR-1, FR-2), and the table's §A / §B from that project alone
(FR-3). An invented study (tests/fixtures/film_163); no stack, no model.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from harness import film_strangers as fs
from harness import three_surfaces as ts
from quality import film as film_walk
from quality import film_table as ft
from quality import readers

FIX = Path(__file__).resolve().parent / "fixtures" / "film_163"


def pick(dimension: str, *codes: str):
    return SimpleNamespace(dimension=dimension, codes=list(codes), scale=None)


def person(name: str, *, recency=True, story="It happened on the last day.", chip=None, frequency="every_time",
           importance=("own", "rival_1"), follow_up=None, in_segment=True, link="PRIMARY"):
    picks = ([pick("problem.frequency", frequency)] if frequency else []) + \
        ([pick("problem.importance", *importance)] if importance else [])
    return SimpleNamespace(person=name, link=link, recency=recency, story=story if recency else None,
                           anchor_chip=chip, picks=picks if recency else [], follow_up=follow_up,
                           in_segment=in_segment)


#: Importance as the film link serves it: the own row and the story's other tasks.
IMPORTANCE_ITEM = {"itemId": "i3", "dimension": ts.IMPORTANCE, "control": "pick_one_then_one",
                   "options": [{"optionId": "o1", "label": "Keeping the day's list"},
                               {"optionId": "o2", "label": "Ordering the stock"},
                               {"optionId": "o3", "label": "Answering the phone"}]}
INTERVIEW = {"gate": {"question": ts.GATE_EXAMPLE, "dimension": ts.PREVALENCE,
                      "condition": {"question": "Do you work in a team of five or fewer?"}},
             "parts": [{"part": 1, "items": [
                 {"itemId": "i2", "dimension": ts.FREQUENCY, "control": "fixed_five", "question": "How often?",
                  "options": [{"optionId": f"f{i}", "label": label} for i, label in enumerate(ts.FREQUENCY_LABELS)]},
                 IMPORTANCE_ITEM]}],
             "followUps": [{"dimension": ts.PREVALENCE, "text": ts.PREVALENCE_WHY}]}
OWN, TASKS = "Keeping the day's list", ["Ordering the stock", "Answering the phone"]


# ------------------------------------------------------------------------------------------------ FR-1 the people

def test_each_persons_recorded_answers_map_onto_the_four_questions():
    plans = fs.people_plans([
        person("A", follow_up="Their own words for a why."),
        person("B", frequency="now_and_then", importance=("rival_2", "own")),
        person("C", chip="RATHER_NOT_SAY"),
        person("D", recency=False),
        person("E", in_segment=False),
        person("F", link="COMMERCIAL_B2B"),
    ])
    assert [p["person"] for p in plans] == ["A", "B", "C", "D", "E"]       # the decision-makers are not this study's
    a, b, c, d, e = plans
    assert (a["screener"], a["gate"], a["frequency"], a["own"], a["why"]) == ("yes", True, "every_time", True,
                                                                             "Their own words for a why.")
    assert a["story_how"] == "said" and a["story"]
    assert (b["frequency"], b["own"], b["importance"], b["why"]) == ("now_and_then", False, ["rival_2", "own"], None)
    assert c["story_how"] == "chip-tap" and c["chip"] == "RATHER_NOT_SAY"
    assert (d["gate"], d["story"], d["frequency"], d["importance"]) == (False, None, None, [])
    assert e["screener"] == "no"
    assert fs.watched(plans) == "A"
    assert fs.watched([c, d]) == "C"


@pytest.mark.parametrize("code, want", [("own", "Keeping the day's list"), ("rival_1", "Ordering the stock"),
                                        ("rival_2", "Answering the phone"), ("rival_9", "Answering the phone"),
                                        (None, "Ordering the stock"), ("odd", "Ordering the stock")])
def test_importance_picks_the_persons_row_by_its_code(code, want):
    assert fs.importance_pick(IMPORTANCE_ITEM, code, own_label=OWN, other_tasks=TASKS) == want


def test_the_walk_plan_carries_the_pick_and_the_persons_why():
    plan = fs.people_plans([person("B", importance=("rival_2",), follow_up="Mine.")])[0]
    how = fs.walk_plan(plan, INTERVIEW, own_label=OWN, other_tasks=TASKS)
    assert how["pick"] == "Answering the phone" and how["why"] == "Mine." and how["own"] is False
    assert how["gate"] is True and how["frequency"] == "every_time" and how["other_tasks"] == TASKS


def test_the_window_is_the_entrys_recall_window():
    assert fs.recall_window({"context": {"recall_window": {"count": 5, "unit": "WORKING_DAYS"}}}) == \
        {"count": 5, "unit": "WORKING_DAYS"}
    assert fs.recall_window({}) == fs.DEFAULT_WINDOW


# ------------------------------------------------------------------------------------------------ FR-1 / FR-4 the lock

class Wire:
    """A stub of the founder's wire: answers by (method, path), records every call."""

    def __init__(self, over: dict | None = None):
        self.calls = []
        self.answers = {("PUT", "context/window"): (200, {}), ("GET", "calibration/PROBLEM"): (200, {"state": "READY"}),
                        ("GET", "/v2/me"): (200, {"creditsAvailable": 2500}),
                        ("GET", "overview"): [(200, {"questionsState": "WRITING"}), (200, {"questionsState": "READY"})],
                        ("POST", "questionnaire/retry"): (202, {}),
                        ("POST", "calibration/PROBLEM/retry"): (202, {"interactionId": "i1"})}
        self.answers.update(over or {})

    def __call__(self, method, path, body=None):
        self.calls.append((method, path, body))
        for (m, tail), answer in self.answers.items():
            if m == method and path.endswith(tail):
                if isinstance(answer, list):
                    return answer.pop(0) if len(answer) > 1 else answer[0]
                return answer
        return 404, None


def lock(wire, *, press=lambda: (201, {}), top_up=None, need=2000):
    ticks = iter(range(0, 10_000))
    return fs.lock_project(wire, "p1", window={"count": 5, "unit": "WORKING_DAYS"}, press=press, need=need,
                           top_up=top_up, sleep=lambda s: None, clock=lambda: next(ticks),
                           calibration_wait_s=5, questions_wait_s=5)


def test_the_lock_holds_step_by_step():
    wire = Wire()
    got = lock(wire)
    assert got["window_status"] == 200 and got["calibration"] == "READY" and got["credits_before"] == 2500
    assert got["lock_status"] == 201 and got["questions"] == "READY" and got["questions_retried"] is False
    assert wire.calls[0] == ("PUT", "/v2/projects/p1/context/window",
                             {"recallWindow": {"count": 5, "unit": "WORKING_DAYS"}})


@pytest.mark.parametrize("over, press, step", [
    ({("PUT", "context/window"): (422, {"code": "BAD"})}, None, "the window (PUT context/window)"),
    ({("GET", "calibration/PROBLEM"): (200, {"state": "FAILED"})}, None, "the PROBLEM calibration"),
    ({("GET", "/v2/me"): (200, {"creditsAvailable": 30})}, None, "the credits (GET /v2/me)"),
    ({}, lambda: (422, {"code": "UNCALIBRATED"}), "the lock (the ready page's button, POST lock)"),
    ({("GET", "overview"): (200, {"questionsState": "WRITING"})}, None, "the questions (GET overview questionsState)"),
])
def test_a_lock_that_does_not_hold_names_its_step(over, press, step):
    with pytest.raises(fs.LockFailed) as failed:
        lock(Wire(over), press=press or (lambda: (201, {})))
    assert failed.value.step.startswith(step.split(" (")[0])
    assert str(failed.value).startswith(f"spec 165 refuses: the film's project did not lock at {failed.value.step}")
    assert "no link is sent on an unlocked project" in str(failed.value)


def test_a_short_balance_is_topped_once_and_a_failed_question_set_retried_once():
    wire = Wire({("GET", "/v2/me"): [(200, {"creditsAvailable": 30}), (200, {"creditsAvailable": 2500})],
                   ("GET", "overview"): [(200, {"questionsState": "FAILED"}), (200, {"questionsState": "READY"})]})
    topped = []
    got = lock(wire, top_up=lambda: topped.append(1) or 2470)
    assert topped == [1] and got["topped_up"] == 2470 and got["credits_topped"] == 2500
    assert got["questions_retried"] is True and ("POST", "/v2/projects/p1/questionnaire/retry", None) in wire.calls
    with pytest.raises(fs.LockFailed, match="after the top-up"):
        lock(Wire({("GET", "/v2/me"): (200, {"creditsAvailable": 30})}), top_up=lambda: 0)


# ------------------------------------------------------------------------------------------------ spec 168 FR-1, FR-4

RETRY = ("POST", "/v2/projects/p1/calibration/PROBLEM/retry", None)


def test_a_failed_calibration_is_retried_once_and_the_lock_goes_on():
    # the calibration writer's result refused twice (the product's one repair turn): FAILED, the founder's retry
    # pressed once, the wait again, READY
    wire = Wire({("GET", "calibration/PROBLEM"): [(200, {"state": "FAILED", "total": 3, "answered": 3}),
                                                  (200, {"state": "WRITING"}), (200, {"state": "READY"})]})
    got = lock(wire)
    assert wire.calls.count(RETRY) == 1
    assert got["calibration"] == "READY" and got["calibration_retried"] is True
    assert got["calibration_first"] == {"state": "FAILED", "total": 3, "answered": 3}
    assert got["calibration_retry"] == {"status": 202}
    assert got["lock_status"] == 201 and got["questions"] == "READY"
    # the retry is pressed before anything after the calibration is asked
    assert wire.calls.index(RETRY) < wire.calls.index(("GET", "/v2/me", None))
    assert fs.lock_record(got) == {"locked": True, "calibration": "READY", "calibration_retried": True,
                                   "calibration_first": {"state": "FAILED", "total": 3, "answered": 3},
                                   "calibration_retry": {"status": 202}, "questions": "READY",
                                   "questions_retried": False}


def test_a_calibration_failed_twice_stops_the_lock_at_the_same_step_with_retried():
    wire = Wire({("GET", "calibration/PROBLEM"): (200, {"state": "FAILED", "total": 3, "answered": 3})})
    with pytest.raises(fs.LockFailed) as failed:
        lock(wire)
    assert failed.value.step == "the PROBLEM calibration (GET calibration/PROBLEM)"
    assert failed.value.detail == {"state": "FAILED", "total": 3, "answered": 3, "retried": True}
    assert "'retried': True" in str(failed.value)
    assert wire.calls.count(RETRY) == 1 and ("GET", "/v2/me", None) not in wire.calls
    held = fs.lock_record(failed=failed.value)
    assert held["locked"] is False and held["calibration_retried"] is True and held["calibration"] == "FAILED"
    assert held["step"] == failed.value.step


def test_a_refused_retry_stops_the_lock_and_one_not_failed_any_more_waits_on():
    # the retry refused (not QUESTIONS_NOT_FAILED): the step, retried, the refusal's status and code
    wire = Wire({("GET", "calibration/PROBLEM"): (200, {"state": "FAILED"}),
                 ("POST", "calibration/PROBLEM/retry"): (422, {"code": "NOT_OWNED"})})
    with pytest.raises(fs.LockFailed) as failed:
        lock(wire)
    assert failed.value.detail == {"state": "FAILED", "retried": True, "retry": {"status": 422, "code": "NOT_OWNED"}}
    assert fs.lock_record(failed=failed.value)["calibration"] == "FAILED"
    # QUESTIONS_NOT_FAILED: the calibration moved on by itself -- the wait goes on
    wire = Wire({("GET", "calibration/PROBLEM"): [(200, {"state": "FAILED"}), (200, {"state": "READY"})],
                 ("POST", "calibration/PROBLEM/retry"): (409, {"code": "QUESTIONS_NOT_FAILED"})})
    got = lock(wire)
    assert got["calibration"] == "READY" and got["calibration_retried"] is True
    assert got["calibration_retry"] == {"status": 409, "code": "QUESTIONS_NOT_FAILED"}


def test_a_calibration_ready_the_first_time_presses_no_retry():
    wire = Wire()
    got = lock(wire)
    assert got["calibration_retried"] is False and "calibration_first" not in got
    assert not any(c[0] == "POST" and c[1].endswith("/retry") and "calibration" in c[1] for c in wire.calls)
    assert fs.lock_record(got)["calibration_retried"] is False and fs.lock_record() is None
    # a calibration that never reads READY in the wait (no FAILED) is not retried either
    with pytest.raises(fs.LockFailed) as failed:
        lock(Wire({("GET", "calibration/PROBLEM"): (200, {"state": "WRITING"})}))
    assert failed.value.detail == {"state": "WRITING", "retried": False}


def test_the_solutions_lock_presses_its_own_calibrations_retry():
    calls = []
    # the three beliefs not answered yet (a SOLUTION calibration with its three answered is ready whatever its state:
    # 166's `calibration_ready`, unchanged -- 168 judgement call 3)
    views = [(200, {"state": "FAILED", "total": 3, "answered": 0}), (200, {"state": "READY", "total": 3,
                                                                          "answered": 0})]

    def call(method, path, body):
        calls.append((method, path))
        if method == "GET" and path.endswith("/calibration/SOLUTION"):
            return views.pop(0) if len(views) > 1 else views[0]
        if path.endswith("/calibration/SOLUTION/retry"):
            return 202, {"interactionId": "i2"}
        if path == "/v2/me":
            return 200, {"creditsAvailable": 2000}
        if path.endswith("/overview"):
            return 200, {"questionsState": "READY"}
        return 200, {}
    got = fs.lock_project(call, "s1", window=None, press=lambda: (201, {}), need=2000, scope=fs.SOLUTION_SCOPE,
                          sleep=lambda s: None)
    assert ("POST", "/v2/projects/s1/calibration/SOLUTION/retry") in calls and got["calibration_retried"] is True


# ------------------------------------------------------------------------------------------------ FR-2 the bundle

ROWS = [
    {"screen": "question", "key": "screener", "question": "Do you work in a team of five or fewer?", "where": "Before",
     "options": ["Yes", "No"], "said": "yes"},
    {"screen": "film", "kind": "problem", "first": True},
    {"screen": "question", "key": "gate", "question": ts.GATE_EXAMPLE, "where": "Question 1", "options": ["Yes", "No"],
     "chips": [], "said": "yes"},
    {"screen": "question", "step": "story", "story": "said", "question": "Tell me about the last time.",
     "where": "Question 1", "chips": ["I can't recall one"], "said": "It happened on the last day."},
    {"screen": "question", "key": ts.FREQUENCY, "control": "fixed_five", "question": "How often?",
     "where": "Question 2", "options": list(ts.FREQUENCY_LABELS), "said": "Now and then"},
    {"screen": "question", "step": "followUp", "follow_up": {"dimension": ts.FREQUENCY, "text": ts.DIFFERENCE_WHY},
     "question": ts.DIFFERENCE_WHY, "where": "One more thing", "said": "Mine."},
    {"screen": "question", "key": ts.IMPORTANCE, "control": "pick_one_then_one", "question": "Which most?",
     "where": "Question 3", "options": [o["label"] for o in IMPORTANCE_ITEM["options"]], "said": OWN},
    {"screen": "question", "step": "pilot", "question": "Would you try it?", "where": "Last question",
     "options": ["Yes", "No"], "said": "yes"},
]
WALKED = {"rows": ROWS, "done": "Thank you", "responses": [{"status": 201, "sent": {
    "recency": True, "story": "It happened on the last day.", "answers": [{}, {}],
    "followUps": [{"dimension": ts.FREQUENCY, "text": "Mine."}]}}]}


def test_the_walked_rows_are_the_screens_the_respondent_reader_is_handed():
    drawn = fs.drawn_of(ROWS)
    assert [d["screen"] for d in drawn] == ["screener", "gate", "story", "item", "follow_up", "item", "pilot"]
    bundle = {"respondents": fs.respondents_record("A", INTERVIEW, WALKED)}
    screens = readers.respondent_screens(bundle)["PRIMARY"]
    assert [s.kind for s in screens] == ["screener", "gate", "story", "item", "follow_up", "item", "pilot"]
    assert [s.dimension for s in screens if s.kind == "item"] == [ts.FREQUENCY, ts.IMPORTANCE]
    assert all(s.said for s in screens)                                     # R6 has what the voice says, every screen


def test_a_walk_is_kept_by_its_shape():
    summary = fs.walk_summary({"person": "A", "screener": "yes", "gate": True, "story_how": "said",
                               "frequency": "now_and_then", "importance": ["own"], "own": True},
                              {"invitationId": "inv1", "url": "http://x/i/t"}, WALKED)
    assert summary["steps"] == ["screener", "gate", "story", ts.FREQUENCY, f"why:{ts.FREQUENCY}", ts.IMPORTANCE,
                                "pilot"]
    assert summary["whys"] == [ts.FREQUENCY] and summary["done"] is True
    assert summary["response"] == {"status": 201, "recency": True, "story": True, "anchorChip": None, "answers": 2,
                                   "followUps": [ts.FREQUENCY], "outsideSegment": None}
    assert "error" in fs.walk_summary({"person": "B"}, {}, None, error="stopped")
    chip_rows = [{"screen": "question", "story": "chip-tap", "said": "tap: I can't recall one"}]
    assert fs.walk_summary({"person": "C", "chip": "RATHER_NOT_SAY"}, {}, {"rows": chip_rows})["chip_remapped"] == \
        {"recorded": "RATHER_NOT_SAY", "tapped": "I can't recall one"}


def test_the_screener_carries_its_served_spoken_form():
    interview = dict(INTERVIEW, gate=dict(INTERVIEW["gate"], condition={
        "question": "Do you work in a team of five or fewer?", "spoken": {"stem": "Do you work in a small team?"}}))
    record = fs.respondents_record("A", interview, WALKED)["PRIMARY"]
    assert record["drawn"][0]["spoken"] == {"stem": "Do you work in a small team?"}
    screener = readers.respondent_screens({"respondents": {"PRIMARY": record}})["PRIMARY"][0]
    assert screener.said == "Do you work in a small team?"


def film_bundle(**over) -> dict:
    plans = fs.people_plans([person("A")])
    bundle = fs.screens_bundle(
        entry={"id": "fixture-film", "title": "Fixture", "path": str(FIX / "entry.yaml"), "sha256": "0" * 64},
        project_id="p1", door="fake", stack={"keel-cloud": "b48e1f49", "keel-web": "7c98d472"}, people=1,
        lock={"questions": "READY"}, plans=plans, walks=[fs.walk_summary(plans[0], {}, WALKED)],
        respondents=fs.respondents_record("A", INTERVIEW, WALKED),
        after_screens=[{"n": 1, "kind": "stage", "stage": "PROBLEM", "screen": "stage", "page": {"title": "Problem"},
                        "text": "Problem"}],
        answers_leg={}, brief={"insights": []}, themes_settled={}, founder_page={"checks": []}, run="r-film-x")
    bundle.update(over)
    return bundle


def test_read_screens_reads_the_film_projects_bundle_with_no_founder_screen(tmp_path):
    (tmp_path / "backtest.json").write_text(json.dumps(film_bundle()))
    run_dir, bundle = readers.load_bundle(tmp_path)
    assert bundle["kind"] == "film" and bundle["project_id"] == "p1" and bundle["founder_screens"] == []
    entry = readers.load_entry(bundle, FIX)
    work = readers.plan(bundle, entry, guidelines={"text": "the rules", "source": "fixture", "sections": [],
                                                    "sha256": "0"})
    audiences = [s.audience for s, _ in work["screens"]]
    assert audiences.count("respondent") == 7 and audiences.count("founder") == 1     # the stage page after (§B)
    assert all(s.after for s, _ in work["screens"] if s.audience == "founder")
    assert [(a, link) for a, link, _ in work["flows"]] == [("respondent", "PRIMARY")]   # no founder flow
    (tmp_path / "backtest.json").write_text(json.dumps(film_bundle(respondents={}, after_screens=[])))
    with pytest.raises(readers.Refused, match="film project's bundle with no stranger's screen"):
        readers.load_bundle(tmp_path)
    (tmp_path / "backtest.json").write_text(json.dumps(film_bundle(kind=None)))
    with pytest.raises(readers.Refused, match="no founder screen"):
        readers.load_bundle(tmp_path)


def test_the_founders_beats_can_be_typed_with_typos():
    entry = SimpleNamespace(idea_name=None, interpretations={}, solution_mechanism={}, path=None)
    beats = [(1, "Example workers in small teams."), (2, "They need to remember everything, when the evening ends.")]
    typed, record = fs.typed_beats(beats, entry, seed="fixture-film")
    again, _ = fs.typed_beats(beats, entry, seed="fixture-film")
    assert typed == again and [n for n, _ in typed] == [1, 2]
    assert record and all(r["field"].startswith("beat-") and r["meant"] != r["typed"] for r in record)


# ------------------------------------------------------------------------------------------------ FR-1 the walk

def test_the_walk_is_the_film_leg_then_the_read_on_its_project_and_no_back_test(tmp_path):
    steps = film_walk.plan_steps(["e1"], door="keel", walk=tmp_path, people=7, typos=True)
    assert [s["what"] for s in steps] == ["film", "read"]
    assert steps[0]["argv"][-5:] == ["ENTRY=e1", "DOOR=keel", f"OUT={tmp_path}", "PEOPLE=7", "TYPOS=1"]
    assert steps[1]["argv"][-2:] == ["read-screens", "RUN=<bundle>"]
    fake = film_walk.plan_steps(["e1"], door="fake", walk=tmp_path, people=None, typos=False)
    assert [s["what"] for s in fake] == ["film"] and fake[0]["argv"][-1] == "TYPOS=0"
    assert not any("backtest" in a for s in steps + fake for a in s["argv"])


def stub_runner(walk: Path, *, refused: str | None = None, screens: Path | None = None):
    seen = []

    def run(argv, stdout=None, stderr=None):
        seen.append(argv)
        if "film-leg" in argv:
            entry = next(a.split("=", 1)[1] for a in argv if a.startswith("ENTRY="))
            folder = walk / "film" / entry
            folder.mkdir(parents=True, exist_ok=True)
            film = {"project_id": "p1", "screens_bundle": None if refused else str(screens),
                    "strangers": None if refused else {"people": 7, "answered": 7}}
            if refused:
                film["refused"] = refused
            (folder / "film.json").write_text(json.dumps(film))
            return SimpleNamespace(returncode=1 if refused else 0)
        stdout.write("score file: quality/scores/e1/x.json\n")
        return SimpleNamespace(returncode=0)
    return run, seen


def test_walk_json_names_the_one_project_and_its_screens_bundle(tmp_path):
    walk = tmp_path / "w"
    runner, seen = stub_runner(walk, screens=tmp_path / "runs" / "x-film-e1")
    env = {"KEEL_ANTHROPIC_API_KEY": "k", "KEEL_OPENAI_API_KEY": "k", "KEEL_PICTURES": "openai"}
    # spec 166: SCOPES=PROBLEM is this spec's walk (the problem alone); the record's spec names all three
    code = film_walk.walk(["--entries", "08-fresco", "--why", "w", "--door", "keel", "--out", str(walk),
                           "--scopes", "PROBLEM"],
                          runner=runner, env=env, which=lambda b: "/bin/x", stack_up=lambda: False)
    record = json.loads((walk / "walk.json").read_text())
    row = record["entries"][0]
    assert code == 0 and record["spec"] == "163+165+166" and "solution" not in row
    assert (row["project_id"], row["screens"], row["people"], row["answered"]) == ("p1", "x-film-e1", 7, 7)
    assert seen[1][-1] == f"RUN={tmp_path / 'runs' / 'x-film-e1'}" and row["score_file"] == "quality/scores/e1/x.json"
    assert "backtest" not in row


def test_a_refused_lock_reads_nothing_and_the_walk_fails(tmp_path):
    walk = tmp_path / "w"
    runner, seen = stub_runner(walk, refused="spec 165 refuses: the film's project did not lock at the lock")
    env = {"KEEL_ANTHROPIC_API_KEY": "k", "KEEL_OPENAI_API_KEY": "k", "KEEL_PICTURES": "openai"}
    code = film_walk.walk(["--entries", "08-fresco", "--why", "w", "--door", "keel", "--out", str(walk)],
                          runner=runner, env=env, which=lambda b: "/bin/x", stack_up=lambda: False)
    row = json.loads((walk / "walk.json").read_text())["entries"][0]
    assert code == 1 and len(seen) == 1 and row["refused"].endswith("did not lock at the lock")
    assert row["read"].startswith("not run")


def test_the_leg_reads_its_people_and_typos():
    from evals import run_film
    assert run_film.people_cap({"KEEL_FILM_PEOPLE": "3"}) == 3
    assert run_film.people_cap({}) == 7                                    # quality/cycle.toml's people
    assert run_film.typos_on({"KEEL_FILM_TYPOS": "1"}) and not run_film.typos_on({"KEEL_FILM_TYPOS": "0"})


# ------------------------------------------------------------------------------------------------ FR-3 the table

def write_score(scores: Path, name: str, *, bundle: str, project: str | None, after: float, r: int):
    (scores / "e1").mkdir(parents=True, exist_ok=True)
    screens = [{"kind": "gate", "audience": "respondent", "r1": r, "r2": r, "r3": r, "r4": r, "r5": r, "r6": r,
                "r7": None},
               {"kind": "q-problem.prevalence", "audience": "founder", "r1": 0, "r2": 0, "r3": 0, "r4": 0, "r5": 0,
                "r6": None, "r7": None}]
    (scores / "e1" / name).write_text(json.dumps({
        "entry": "e1", "bundle": bundle, **({"project_id": project} if project else {}), "screens": screens,
        "summary": {"overall": {"after_pct": after}}}))


def test_the_table_reads_the_films_project_alone(tmp_path):
    scores = tmp_path / "scores"
    write_score(scores, "a.json", bundle="x-film-e1", project="p1", after=90.0, r=2)
    write_score(scores, "b.json", bundle="x-backtest-e1", project=None, after=10.0, r=0)      # a typed project's
    write_score(scores, "c.json", bundle="x-film-e1", project="p-other", after=20.0, r=0)    # another project's
    walk = tmp_path / "w"
    walk.mkdir()
    (walk / "walk.json").write_text(json.dumps({"entries": [
        {"entry": "e1", "project_id": "p1", "screens_bundle": str(tmp_path / "x-film-e1"), "screens": "x-film-e1"},
        {"entry": "e2", "backtest": "x-backtest-e2"}]}))
    projects = ft.projects_of(walk)
    assert projects == {"e1": {"bundle": "x-film-e1", "project_id": "p1"}}
    assert ft.typed_rows(walk) == ["e2"]
    got = ft.question_scores("w", scores, projects)
    assert got["e1"]["qa_pct"] == 100.0 and got["e1"]["after_pct"] == 90.0 and got["e1"]["project_id"] == "p1"


def test_the_record_says_the_films_project_and_never_tables_a_typed_one():
    table = [{"entry": "e1", "kind": "problem", "scores": {f"f{i}": 2 for i in range(1, 9)}, "film_pct": 100.0,
              "flagged": False, "founder_pct": None, "qa_pct": 95.0, "after_pct": 90.0, "project_id": "p1",
              "usd": 0.3, "walk_usd": None, "passes": True, "holdout": False, "file": "f.json",
              "whys": {f"f{i}": "fine" for i in range(1, 9)}, "instead": {}, "missing": [], "frames": {},
              "measures": None, "cloud_sha": "b48e1f4", "web_sha": "7c98d47"}]
    text = ft.render(table, [{}], [], {"film_bar_pct": 80.0, "holdout": []}, bundle="w", found=[], typed=["e2"])
    assert "**the film's project**" in text and "The film's project: e1 `p1`." in text
    assert "Not tabled (a walk before spec 165, whose §A and §B were a second, typed project's): e2." in text


# ------------------------------------------------------------------------------------------------ the free walk's runtime

def test_the_free_walk_hands_its_runtime_the_groupings_of_what_was_said():
    walked = {"A": WALKED, "B": {"rows": [{"screen": "question", "follow_up": {"dimension": ts.FREQUENCY},
                                           "said": "Mine."},
                                          {"screen": "question", "follow_up": {"dimension": ts.PREVALENCE},
                                           "said": "We check it twice, always."}]}}
    said = fs.said_by_rung(walked)
    assert said == {ts.FREQUENCY: ["Mine.", "Mine."], ts.PREVALENCE: ["We check it twice, always."]}
    themes = {e["dimension"]: e["result"]["themes"] for e in fs.themes_script(said)}
    assert themes[ts.FREQUENCY] == [{"label": "Mine", "answers": ["Mine."]}]
    assert themes[ts.PREVALENCE][0]["label"] == "We check it twice always"
    stories = fs.stories_told([{"person": "A", "invitation": "inv1"}, {"person": "B", "invitation": "inv2"}], walked)
    assert stories == [("inv1", "It happened on the last day.")]
    assert fs.ways_script(stories, "they write it on paper")["result"]["ways"] == [
        {"label": "they write it on paper", "answerIds": ["inv1"]}]
    assert fs.ways_script(stories, None)["result"]["ways"][0]["label"] == ts.ON_THEIR_OWN


# ---------------------------------------------------------------------------------- spec 169: the gate's new words

@pytest.mark.parametrize("words", [
    "In the last month, have you encountered this issue?",               # keel-cloud 277's acceptance
    "In the last 7 days, have you encountered this issue?",
    "In the last 3 months, have you encountered this issue",              # the question mark optional
    "in the last month, HAVE YOU ENCOUNTERED THIS ISSUE?",                # case-insensitive
    "In the last month have you encountered this issue?",
    "  In the last month,  have you\nencountered this issue? ",          # spaces folded
    "In {window}, have you encountered this issue?",                      # the registry's own template
    "Have you encountered this issue?",                                   # no window: still the words
])
def test_the_gate_is_found_by_its_new_words_with_any_window(words):
    assert ts.is_gate_words(words)


@pytest.mark.parametrize("words", [
    "Did this happen to you?",                                            # 269's words: no longer matched
    ts.GATE_WORDS_BEFORE_277,
    "In your last month, did this happen to you?",                        # 259's story gate
    "In the last month, did you check the rota?",                         # the framed clause of a link with no film
    "In the last month, have you encountered this issue? Tell me more.",
    "Before we start: have you encountered this issue?",
    "", None,
])
def test_the_old_words_and_others_are_not_the_gate(words):
    assert not ts.is_gate_words(words)


def test_the_gate_on_the_films_link_is_found_and_answered_by_recency():
    film_link = dict(INTERVIEW, gate=dict(INTERVIEW["gate"], question=ts.GATE_EXAMPLE), story={"scenes": [{}]})
    yes, no = fs.people_plans([person("A"), person("D", recency=False)])
    said = {p["person"]: ts.gate_answer("In the last month, have you encountered this issue?", film_link,
                                        fs.walk_plan(p, film_link, own_label=OWN, other_tasks=TASKS))
            for p in (yes, no)}
    assert said == {"A": "yes", "D": "no"}                                  # `recency`, as before
    assert ts.gate_answer(ts.GATE_EXAMPLE, film_link, None, no_on="gate") == "no"
    # the old words are not the gate on a film link -- not even where the link served them
    old = dict(film_link, gate=dict(film_link["gate"], question=ts.GATE_WORDS_BEFORE_277))
    assert ts.gate_answer(ts.GATE_WORDS_BEFORE_277, old, yes) is None
    assert ts.gate_answer("Do you work in a team of five or fewer?", film_link, yes) is None
    # a link with no film keeps its framed clause, found as served
    framed = dict(INTERVIEW, gate=dict(INTERVIEW["gate"], question="In the last month, did you keep the list?"))
    assert ts.gate_answer("In the last month, did you keep the list?", framed, yes) == "yes"
    assert ts.gate_answer(ts.GATE_EXAMPLE, framed, yes) is None
    assert not ts.gate_found(ts.GATE_EXAMPLE, {"story": {"scenes": [{}]}})   # no gate served, none found


def test_the_one_script_check_holds_the_three_surfaces_gate_to_each_other():
    same = ts.same_gate({"orb": ts.GATE_EXAMPLE, "face": ts.GATE_EXAMPLE, "card": " " + ts.GATE_EXAMPLE})
    assert same["same"] is True
    other = ts.same_gate({"orb": ts.GATE_EXAMPLE, "face": ts.GATE_EXAMPLE,
                          "card": "In the last 7 days, have you encountered this issue?"})
    assert other["same"] is False and all(other["found"].values())         # each the gate, not the same words
    old = ts.same_gate({k: ts.GATE_WORDS_BEFORE_277 for k in ("orb", "face", "card")})
    assert old["same"] is False and not any(old["found"].values())         # one script, but not the gate's words
    assert ts.same_gate({"orb": ts.GATE_EXAMPLE, "face": None, "card": ts.GATE_EXAMPLE})["same"] is False


def test_every_reader_finds_the_gate_by_the_one_match():
    from evals import three_views_strangers as tvs                          # noqa: PLC0415
    from harness import interviewer_screens as ivs                          # noqa: PLC0415
    assert ivs.GATE_WORDS is ts.GATE_WORDS and tvs.GATE_WORDS is ts.GATE_WORDS
    orb = ts.served_record(dict(INTERVIEW, gate=dict(INTERVIEW["gate"], question=ts.GATE_EXAMPLE)))
    assert ts.is_gate_words(ts.gate_words(orb))
