"""Spec 161: the four questions walked -- the machinery with no stack, and the mirrors of the subjects read off the
sibling checkouts the stack serves (keel-cloud 268-270 at contract 87; keel-web 257 / 258 where merged, else skipped by
name): the founder's seven beats and the long beats' done word, the board's rows, the verdict line, the film's pain
scene, the gate's words, Frequency's five rows, every why, the No that goes on, the three surfaces' one script, the
founder's page on bands, the corpus read through 269, the report's two sections."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

from evals import three_views as tv
from evals import three_views_report as report
from harness import interview_charge as charge
from harness import story_screens as ss
from harness import three_surfaces as ts
from harness import vectors_screens as vs_screens
from harness import working_rung
from instructions import corpus as corpus_mod
from instructions import registry as registry_mod
from stack.config import load_config

CONFIG = load_config(validate=False)
CLOUD = Path(CONFIG.keel_cloud)
WEB = Path(CONFIG.keel_web)
#: keel-cloud 270 T0 (`969bd043`, unchanged at master `bf5a5b7d`): sha256 of `canon/openapi-v2.yaml` at contract 87.
CONTRACT_87 = "d3e7424c1c37f8d0d848f565a4c8a57311b8c2ffc6a7d3a4e968b202faac9e25"


def _need(path: Path) -> Path:
    if not path.exists():
        pytest.skip(f"{path} is not in the sibling checkout")
    return path


def _java(*parts: str) -> str:
    return _need(CLOUD.joinpath("src", "main", "java", "com", "keeldiscovery", "cloud", *parts)).read_text(
        encoding="utf-8")


def readings() -> dict:
    _need(CLOUD / ss.FAKE_READINGS)
    script = ss.fake_readings(CLOUD)
    if not any(int(t.get("turn", 0)) == 7 for t in script.get("turns") or []):
        pytest.skip("keel-cloud before 268 (the fake readings not yet on seven beats)")
    return script


def registry_entries() -> dict:
    raw = json.loads(_need(CLOUD / "src" / "main" / "resources" / "keel" / "dimension-registry.json").read_text())
    return {d["key"]: d for d in raw["dimensions"]}


# ------------------------------------------------------------------------------------------- FR-1 the seven beats

def test_said_turns_reads_seven_beats_and_refuses_any_other_order():
    seven = {"turns": [{"turn": n, "heard": str(n), "result": {}} for n in (1, 2, 3, 4, 5, 6, 7)]}
    assert [n for n, _ in ss.said_turns(seven)] == [1, 2, 3, 4, 5, 6, 7]
    six = {"turns": [{"turn": n, "heard": str(n), "result": {}} for n in (1, 2, 3, 4, 5, 7)]}
    assert [n for n, _ in ss.said_turns(six)] == [1, 2, 3, 4, 5, 7]           # beat 6 only where the when is owed
    for beats in ((1, 2, 3, 4, 5), (1, 2, 3, 4), (1, 2, 4, 3, 5, 7), (1, 2, 3, 5, 7)):
        with pytest.raises(ValueError, match="seven"):
            ss.said_turns({"turns": [{"turn": n, "heard": str(n), "result": {}} for n in beats]})


def test_the_cloud_script_is_seven_beats_with_the_way_the_cost_and_the_tasks():
    script = readings()
    told = ss.said_turns(script)
    assert [n for n, _ in told] == [1, 2, 3, 4, 5, 6, 7]
    assert ss.moment_beat(script) == ss.WHEN_BEAT                  # beat 2 names no moment: beat 6 is owed
    assert ss.steps_read(script) and ss.act_read(script)          # beat 3's way
    assert ss.heard_cost(script) and ss.cost_read(script)         # heard on beat 3, said again on beat 4
    assert 2 <= len(ss.other_tasks_read(script)) <= 4             # beat 7
    fix = ss.tasks_correction(script)
    assert fix and len(fix[1]) >= 2                               # the tasks row corrected on the board


def test_the_seven_questions_are_keel_clouds_and_keel_webs():
    turns = _java("domain", "story", "StoryTurns.java")
    for n, question in ss.STORY_QUESTIONS.items():
        assert f'"{question}"' in turns, (n, question)
    assert f'WAY_ASK = "{ss.WAY_ASK}"' in turns
    if not ss.web_has_257(WEB):
        pytest.skip("keel-web 257 is not in the keel-web checkout (the seven beats pending keel-web 257)")
    lines = (WEB / ss.STORY_LINES_SOURCE).read_text(encoding="utf-8")
    for n, question in ss.STORY_QUESTIONS.items():
        assert f'"{question}"' in lines, (n, question)


def test_the_long_beats_close_on_the_done_word_and_send_none():
    assert ss.LONG_BEATS == (3, 4, 7)
    said = ss.with_done_word("They check it by hand.")
    assert said.endswith(ss.DONE_WORD) and ss.ends_on_a_done_word(said)
    assert ss.without_done_word(said) == "They check it by hand."
    assert not ss.ends_on_a_done_word("Yes, that's it: someone gets paid wrong")     # inside a sentence: no close
    assert not ss.ends_on_a_done_word("and that's it for the first step, then more")
    for word in ss.DONE_WORDS:
        assert ss.ends_on_a_done_word(f"It costs them a day. {word}."), word
    assert ss.ends_on_a_done_word("it costs them a day. That’s it.")
    assert ss.THINK_MS / 1000 < ss.TWO_PART_QUIET_S < ss.ANYTHING_ELSE_MS / 1000


def _echo_beat_3(words: str) -> dict:
    """keel-cloud 268 `FakeStoryReadings`' beat 3, restated: a *Today* sentence the way (its steps split on *, then*), an
    *In the end* one the cost heard, every other sentence a limitation, four kept."""
    steps, limits, cost = [], [], None
    for sentence in re.split(r"(?<=[.;!?])\s+", words.strip()):
        bare = re.sub(r"[.!?;,\s]+$", "", sentence.strip())
        today = re.match(r"(?i)^(?:today|these days|right now)[,\s]+(?:they\s+)?", bare)
        if today:
            steps += [x.strip() for x in re.split(r"(?i)\s*(?:,\s*(?:and\s+)?then\s+|\bthen\s+|,\s*and\s+|,\s+)",
                                                  bare[today.end():]) if x.strip()]
            continue
        said = re.match(r"(?i)^(?:so\s+)?(?:in the end|it costs them|which means)[,:\s]+", bare)
        if said:
            cost = cost or bare[said.end():]
            continue
        limits.append(bare)
    return {"steps": steps[:5], "limits": limits[:4], "kept_four": len(limits) > 4, "cost": cost}


def test_the_long_telling_tells_the_way_five_limitations_and_the_cost():
    script = readings()
    words, rows = ss.long_beat_3(script)
    assert ss.LONG_ANSWER_MIN <= len(words) <= ss.LONG_ANSWER_MAX
    read = _echo_beat_3(words)
    assert read["steps"] and len(read["steps"]) == len(ss.steps_read(script))
    assert read["limits"] == rows and read["kept_four"]
    assert (read["cost"] or "").lower() == (ss.heard_cost(script) or "").lower()


def test_the_limitations_alone_are_asked_their_way_once():
    script = readings()
    alone = _echo_beat_3(ss.limits_only_beat_3(script))
    assert not alone["steps"] and alone["limits"] == ss.limits_read(script)      # no way: code asks WAY_ASK
    way = ss.way_answer(script)
    assert way.startswith("They ") and all(s.lower() in way.lower() for s in ss.steps_read(script))
    first, second = ss.two_part_beat_3(script)
    assert first.startswith("Today they ") and second and _echo_beat_3(f"{first} {second}")["limits"] \
        == ss.limits_read(script)


def test_the_context_is_read_off_beats_5_and_6():
    script = readings()
    ctx = ss.context_interpret_result(script, "WEEKLY")
    assert ctx["segment"]["condition"] == ss.reading_of(script, ss.ALL_OF_THEM_BEAT).get("only_those_who")
    assert ctx["circumstance"] == ss.reading_of(script, ss.WHEN_BEAT).get("circumstance")


def test_the_board_reads_seven_rows_tasks_last():
    card = {"rows": [{"box": b, "text": t} for b, t in (
        ("person", "Plot keepers"), ("task", "Check the rota"), ("when", "every week"),
        ("today", "Today they check it line by line"), ("limits", "The hours do not agree"),
        ("cost", "It costs them: someone misses a turn"), ("tasks", "Besides this they run the reports, file forms"))]}
    v = ss.board_rows_verdict(card, {"tasks": ["run the reports", "file forms"], "limits": ["The hours do not agree"]})
    assert v["ok"] and v["order"] == list(ss.BOARD_ROWS)
    out_of_order = {"rows": list(reversed(card["rows"]))}
    assert not ss.board_rows_verdict(out_of_order, {})["ok"]
    assert not ss.board_rows_verdict(card, {"tasks": ["answer the phones"]})["ok"]
    assert ss.CARD_ROWS[-1] == "tasks"


# ------------------------------------------------------------------------------------------- FR-2 the verdict, the corridor

def test_the_verdict_line_is_keel_clouds():
    beliefs = _java("domain", "vectors", "ProblemBeliefs.java")
    assert "DEFAULT_VERDICT" in beliefs
    joined = re.sub(r'"\s*\+\s*"', "", beliefs)
    assert ss.VERDICT_LINE in joined


def test_no_belief_page_on_a_spoken_problem_and_the_typed_path_unchanged():
    assert not vs_screens.calibrates("PROBLEM", "PROBLEM", spoken=True)
    assert vs_screens.calibrates("PROBLEM", "PROBLEM") and vs_screens.calibrates("PROBLEM", "ALL")
    assert vs_screens.calibrates("SOLUTION", "SOLUTION", spoken=True)
    assert vs_screens.SCOPE_STEPS["PROBLEM"] == ("context", "problem", "ready")
    assert "problem.current_solution_satisfaction" not in vs_screens.REVIEWED_LISTS
    assert vs_screens.REVIEWED_LISTS == ("problem.importance", "solution.compatibility", "solution.relative_advantage")


def test_the_review_tables_three_rows_as_written():
    review = {"complete": True, "counts": {"dimensions": 3}, "rows": [
        {"dimension": "problem.prevalence", "answer": {"codes": ["p_60_80"]}, "belief": "6 to 7 in 10 ..."},
        {"dimension": "problem.frequency", "answer": {"codes": ["p_60_80"]}},
        {"dimension": "problem.importance", "answer": {"list": {"items": [{"label": "Checking the rota"},
                                                                          {"label": "Running the reports"}]}}}]}
    read = vs_screens.written_beliefs(review)
    assert read["prevalence"] == read["frequency"] == ["p_60_80"]
    assert read["importance"] == ["Checking the rota", "Running the reports"] and read["dimensions"] == 3
    assert vs_screens.calibration_answered({"total": 3, "answered": 3})
    assert not vs_screens.calibration_answered({"total": 4, "answered": 3})


# ------------------------------------------------------------------------------------------- FR-3 the pain scene

def _story(*, pain_at: int = 6, cost_line: str | None = "And someone gets paid wrong.", clips: int = 8) -> dict:
    scenes = [{"line": f"Line {i}.", "pictogramId": "changed", "clipId": None} for i in range(6)]
    scenes.append({"line": "And someone gets paid wrong.", "pictogramId": "paidwrong", "clipId": None})
    if pain_at is not None:
        scenes[pain_at]["pain"] = True
    return {"scenes": scenes, "costLine": cost_line, "clipIds": [None] * clips}


def test_the_pain_is_the_seventh_scene_with_its_picture_and_eight_clips():
    assert ss.scenes_verdict(_story(), cost="Someone gets paid wrong")["ok"]
    assert not ss.scenes_verdict(_story(pain_at=5))["ok"]
    assert not ss.scenes_verdict(_story(cost_line="Something else."))["ok"]
    assert not ss.scenes_verdict(_story(clips=7))["ok"]
    six = _story()
    six["scenes"] = six["scenes"][:6]
    assert not ss.scenes_verdict(six)["ok"]


def test_the_pain_is_held_longer_on_the_films_clock():
    story = _story()
    log = [{"film": "problem", "t": t, "line": line} for t, line in (
        (0, "Line 4."), (1500, "Line 5."), (3300, "And someone gets paid wrong."), (6900, "Is that how it goes for you?"))]
    holds = ss.film_holds(log, story)
    assert (holds["scene"], holds["pain"]) == (1500.0, 3600.0) and ss.held_longer(holds)
    assert not ss.held_longer({"scene": 2000, "pain": 1500}) and not ss.held_longer({})
    assert not ss.held_longer({"scene": 1500, "pain": 1700})                   # under the hold the pain adds


# ------------------------------------------------------------------------------------------- FR-4 the gate, the order

def test_the_gate_words_and_the_follow_ups_are_the_registrys():
    reg = registry_entries()
    if "problem.current_solution_satisfaction" in reg:
        pytest.skip("keel-cloud before 269")
    prevalence, frequency = reg["problem.prevalence"], reg["problem.frequency"]
    assert prevalence["respondent"]["story_gate"] == ts.GATE_WORDS
    assert (prevalence["follow_up"]["text"], prevalence["follow_up"]["heading"]) == (ts.PREVALENCE_WHY,
                                                                                    ts.PREVALENCE_HEADING)
    assert prevalence["follow_up"]["against"] == ["NO"]
    f = frequency["follow_up"]
    assert (f["text"], f["heading"], f["against"]) == (ts.DIFFERENCE_WHY, ts.DIFFERENCE_HEADING,
                                                       list(ts.FREQUENCY_AGAINST))
    assert (f["also"]["text"], f["also"]["heading"], f["also"]["on"]) == (ts.NEVER_WHY, ts.NEVER_HEADING, ["never"])
    assert [a["label"] for a in frequency["respondent"]["fixed_answers"]] == list(ts.FREQUENCY_LABELS)
    assert [a["code"] for a in frequency["respondent"]["fixed_answers"]] == list(ts.FREQUENCY_CODES)
    assert frequency["respondent"]["supports"] == list(ts.FOR_CODES)
    assert frequency["respondent"]["control"] == "fixed_five" and frequency["respondent"]["escape"] is None


def test_the_screener_comes_before_the_film_and_the_gate_after_it():
    good = ["speaking:opening", "screener", "film:problem", "gate"]
    assert ts.screener_first(good, screener=True)["ok"]
    assert not ts.screener_first(["speaking:opening", "film:problem", "screener", "gate"], screener=True)["ok"]
    assert ts.screener_first(["speaking:opening", "film:problem", "gate"], screener=False)["ok"]


# ------------------------------------------------------------------------------------------- FR-5, FR-7 every why

def test_the_roster_is_owed_every_why_up_to_two():
    for person in ts.ROSTER:
        assert ts.owed_whys(person["gate"], person["frequency"], person["own"]) == person["owed"], person["who"]
    assert ts.owed_whys(True, "every_time", True) == []                   # held and the own row picked: nothing asked
    assert ts.owed_whys(False, None, False) == [ts.PREVALENCE, ts.IMPORTANCE]
    assert len(ts.owed_whys(True, "now_and_then", False)) == ts.MAX_FOLLOW_UPS


def _interview() -> dict:
    return {"gate": {"itemId": "g", "dimension": ts.PREVALENCE, "question": ts.GATE_WORDS, "noLabel": "No",
                     "condition": {"question": "Do you work at a company with more than 50 employees?"}},
            "story": {"scenes": []},
            "followUps": [{"dimension": ts.PREVALENCE, "itemId": "f", "spoken": ts.PREVALENCE_WHY},
                          {"dimension": ts.FREQUENCY, "itemId": "f", "spoken": ts.DIFFERENCE_WHY},
                          {"dimension": ts.IMPORTANCE, "itemId": "f", "spoken": "What mattered more to you?"}],
            "parts": [{"part": 1, "items": [
                {"itemId": "i1", "dimension": ts.FREQUENCY, "control": "fixed_five",
                 "question": "When you check the rota before it goes out, how often does it happen?",
                 "options": [{"optionId": f"o{i}", "label": x} for i, x in enumerate(ts.FREQUENCY_LABELS)]},
                {"itemId": "i2", "dimension": ts.IMPORTANCE, "control": "pick_one_then_one",
                 "question": "Of the things you do as a plot keeper, which would you most like made easier?",
                 "options": [{"optionId": "a", "label": "Running the month-end reports"},
                             {"optionId": "b", "label": "Checking the rota before it goes out"},
                             {"optionId": "c", "label": "Keeping the forms up to date"}]}]}]}


def test_the_responses_on_the_wire_are_269s_shapes():
    iv = _interview()
    tasks = ["Running the month-end reports", "Keeping the forms up to date"]
    no_sayer = next(p for p in ts.ROSTER if not p["gate"])
    body = ts.response_for(no_sayer, iv, fmt="TEXT", whys=[{"dimension": ts.PREVALENCE, "text": ts.PREVALENCE_WHY}],
                           other_tasks=tasks)
    assert body["recency"] is False and "story" not in body and len(body["answers"]) == 1
    assert body["answers"][0]["itemId"] == "i2" and body["answers"][0]["optionIds"][0] == "b"   # the own row
    assert body["followUps"] == [{"dimension": ts.PREVALENCE, "text": ts.WHY_SAID[ts.PREVALENCE], "how": "RECORDED"}]
    half = dict(ts.ROSTER[0], story=ts.STORIES[0])
    body = ts.response_for(half, iv, fmt="TEXT", whys=[], other_tasks=tasks)
    assert body["recency"] is True and body["story"] == ts.STORIES[0]
    assert body["answers"][0] == {"itemId": "i1", "optionIds": ["o2"]}                # About half the time
    every = ts.ROSTER[1]
    picks = ts.answers_for(every, iv, other_tasks=tasks)[1]["optionIds"]
    assert "b" not in picks and len(picks) == 2                                          # the own row not picked
    assert ts.why_said({"text": ts.NEVER_WHY, "dimension": ts.FREQUENCY}) == ts.NEVER_SAID


def test_the_scripted_readings_cover_the_words_said():
    said = {ts.PREVALENCE: [ts.WHY_SAID[ts.PREVALENCE]], ts.FREQUENCY: [ts.WHY_SAID[ts.FREQUENCY]]}
    entries = ts.themes_entries(said)
    assert [e["dimension"] for e in entries] == [ts.PREVALENCE, ts.FREQUENCY]
    assert [t["label"] for t in entries[1]["result"]["themes"]] == ["Depends on the changes that week"]
    for dimension, themes in ts.THEMES.items():
        for theme in themes:
            words = set(re.findall(r"[a-z']+", theme["label"].lower()))
            assert any(words & set(re.findall(r"[a-z']+", a.lower())) for a in theme["answers"]), theme  # T11
            assert not re.search(r"\d", theme["label"])                                              # T4
    stories = list(zip(("i1", "i2", "i3", "i4"), ts.STORIES))
    ways = ts.ways_entry(stories, "checking the rota line by line")["result"]["ways"]
    assert ways[0] == {"label": "checking the rota line by line", "answerIds": ["i1", "i3"]}
    assert ways[-1] == {"label": ts.ON_THEIR_OWN, "answerIds": ["i4"]}
    assert sorted(i for w in ways for i in w["answerIds"]) == ["i1", "i2", "i3", "i4"]       # every story once


def test_frequency_is_held_on_a_and_b_and_against_on_c_d_and_e():
    assert [working_rung.frequency_side(c) for c in ts.FREQUENCY_CODES] == ["held", "held", "against", "against",
                                                                            "against"]
    assert [working_rung.frequency_side(x) for x in "ABCDE"] == ["held", "held", "against", "against", "against"]
    assert working_rung.frequency_side("CANT_RECALL") is None


# ------------------------------------------------------------------------------------------- FR-8 the founder's page

def test_the_founders_page_on_bands():
    row = {"dimension": ts.FREQUENCY, "chart": {"frequency": {"forCodes": list(ts.FOR_CODES), "share": 0.25, "n": 4,
                                                               "founderBand": "6 or 7 in 10"}},
           "choice": {"optionCounts": [{"label": x, "count": 1} for x in ts.FREQUENCY_LABELS]}}
    assert ts.frequency_faults(row, picks=["about_half", "every_time", "now_and_then", "never"]) == []
    assert ts.frequency_faults({"chart": {"window": {}}}) != []
    assert ts.frequency_faults(row, picks=["every_time", "most_times"]) != []
    facts = {"problem": {"frequency": {"n": 2, "mostOrEvery": 1, "bands": [
        {"code": c, "label": x, "count": int(c == "every_time" or c == "never")}
        for c, x in zip(ts.FREQUENCY_CODES, ts.FREQUENCY_LABELS)]}}}
    assert ts.brief_frequency_faults(facts, picks=["every_time", "never"]) == []
    facts["problem"]["frequency"]["median"] = 3
    assert ts.brief_frequency_faults(facts) != []
    assert ts.current_solution_anywhere({"a": [{"dimension": ts.CURRENT_SOLUTION}]}) == ["view0.a[0].dimension"]
    assert ts.current_solution_anywhere({"facts": {"problem": {"frequency": {}}}}) == []


def test_the_ways_panel_and_the_insights_cards():
    grouped = {"ways": {"state": "GROUPED", "read": 4, "groups": [{"label": "x", "count": 2, "founders": True}]}}
    assert ts.ways_faults(grouped, {"insights": []}, stories=4, founder_way="x") == []
    assert ts.ways_faults({}, {}, stories=1) == []                      # under two stories: no panel
    assert ts.ways_faults({}, {}, stories=2) != []
    assert ts.ways_faults({"ways": {"state": "RAW"}}, {}, stories=3) != []
    good = {"dimension": ts.PREVALENCE, "name": "Prevalence", "rungHeading": ts.PREVALENCE_HEADING, "against": 1,
            "asked": 1, "capped": 0, "quotes": [{"option": "No", "text": "x"}], "dissent": True,
            "frame": "Prevalence held, 4 of 5; the 1 who said no:"}
    assert ts.insights_faults({"insights": [good]}) == []
    assert ts.insights_faults({"insights": [dict(good, tookBy=[])]}) != []
    assert ts.insights_faults({"insights": [dict(good, capped=1)]}) != []
    assert ts.insights_faults({"insights": [dict(good, quotes=[{"option": "Yes"}])]}) != []


# ------------------------------------------------------------------------------------------- FR-9 three surfaces

def _card(interview: dict, *, gate: str | None = None, hint: str = ts.PREVALENCE_WHY) -> dict:
    g = interview["gate"]
    passages = [{"kind": "intro"},
                {"kind": "gate", "stem": gate or g["question"], "condition": g["condition"],
                 "options": [{"optionId": "YES", "label": "Yes"}, {"optionId": "NO", "label": "No"}],
                 "followUp": {"against": ["NO"], "hint": {"first": hint, "third": hint}}}]
    whys = {f["dimension"]: f["spoken"] for f in interview["followUps"]}
    for item in interview["parts"][0]["items"]:
        p = {"kind": "item", "dimension": item["dimension"], "stem": item["question"],
             "options": [{"optionId": o["optionId"], "label": o["label"]} for o in item["options"]]}
        if item["dimension"] in whys:
            p["followUp"] = {"against": [], "hint": {"first": whys[item["dimension"]], "third": whys[item["dimension"]]}}
        passages.append(p)
    return {"passages": passages}


def test_one_script_on_three_surfaces_and_where_one_parts():
    iv = _interview()
    orb = ts.served_record(iv)
    assert [s["step"] for s in orb] == ["screener", "gate", ts.FREQUENCY, ts.IMPORTANCE]
    assert ts.gate_words(orb) == ts.GATE_WORDS
    same = ts.same_script({"orb": orb, "face": ts.served_record(iv), "card": ts.card_record(_card(iv))})
    assert same["same"] is True and same["steps"] == 4
    framed = ts.same_script({"orb": orb, "face": orb, "card": ts.card_record(_card(iv, gate="In the last 7 nights, "
                                                                                       "did you check the rota?"))})
    assert (framed["same"], framed["surface"], framed["step"], framed["differs"]) == (False, "card", "gate", ["words"])
    other_hint = ts.same_script({"orb": orb, "card": ts.card_record(_card(iv, hint="Why not?"))})
    assert other_hint["differs"] == ["follow_ups"] and other_hint["step"] == "gate"
    # the decision-maker's check (and a screener) compared only where every surface carries it -- noted, not a part
    checked = [ts.step("check", "Does your team have this problem?", ["Yes", "No"])] + orb[2:]
    card = [s for s in ts.card_record(_card(iv)) if s["step"] not in ("screener", "gate")]
    v = ts.same_script({"orb": checked, "face": checked, "card": card})
    assert v["same"] is True and v["not_on_every_surface"] == {"check": ["card"]}


def test_a_walked_record_folds_each_why_onto_its_question():
    rows = [{"screen": "question", "key": "gate", "question": ts.GATE_WORDS, "options": []},
            {"screen": "question", "step": "story", "question": "Tell me about it."},
            {"screen": "question", "step": "followUp", "follow_up": {"dimension": ts.PREVALENCE},
             "question": ts.PREVALENCE_WHY},
            {"screen": "question", "key": ts.FREQUENCY, "question": "How often?", "options": list(ts.FREQUENCY_LABELS)}]
    record = ts.walked_record(rows)
    assert [s["step"] for s in record] == ["gate", ts.FREQUENCY]
    assert record[0]["options"] == ["Yes", "No"] and record[0]["follow_ups"] == [ts.PREVALENCE_WHY]


# ------------------------------------------------------------------------------------------- FR-6 the corpus read through 269

def test_a_recorded_count_reads_on_the_five_rows():
    rows = {7: "every_time", 5: "most_times", 4: "most_times", 3: "now_and_then", 1: "now_and_then", 0: "never"}
    for count, code in rows.items():
        assert corpus_mod.spec269_frequency(count, 7) == code, count
    assert corpus_mod.spec269_frequency(2, 4) == "about_half"
    assert corpus_mod.spec269_frequency({"value": 3, "unit": "MONTHS"}, 3) == "every_time"
    assert corpus_mod.spec269_frequency({"chip": "cant_recall"}, 7) == {"chip": "cant_recall"}
    assert corpus_mod.spec269_frequency("most_times", 7) == "most_times"
    assert corpus_mod.spec269_founder_bin({"problem.frequency": {"answer": {"lower": 1}}}) == "p_60_80"
    assert corpus_mod.spec269_founder_bin({"problem.frequency": {"unsure": True}}) is None
    assert corpus_mod.picks_269({"problem.frequency": 5, "problem.current_solution_satisfaction": ["x"],
                                 "problem.importance": ["a"]}, 7) == {"problem.frequency": "most_times",
                                                                      "problem.importance": ["a"]}


def test_the_golden_verdicts_that_move_through_269():
    expected = {"standings": {"problem.frequency": {"status": "HOLDING_UP", "drift": None, "n": 8, "inside": 6,
                                                    "median": 3},
                              "problem.current_solution_satisfaction": {"status": "PEOPLE_DISAGREE"}},
                "vector_verdicts": {"PROBLEM": {"verdict": "PEOPLE_DISAGREE",
                                                "deciding": "problem.current_solution_satisfaction"}}}
    read = corpus_mod.expected_269("01-countly", expected)
    assert "problem.current_solution_satisfaction" not in read["standings"]
    assert read["standings"]["problem.frequency"]["status"] == "NOT_HOLDING_UP"
    assert "median" not in read["standings"]["problem.frequency"]
    assert read["vector_verdicts"]["PROBLEM"] == {"verdict": "NOT_HOLDING_UP", "deciding": "problem.frequency"}
    assert expected["standings"]["problem.frequency"]["status"] == "HOLDING_UP"          # the record never rewritten
    assert corpus_mod.SPEC_269_MOVES["04-linerly"][0] == "NOT_HOLDING_UP"
    assert corpus_mod.SPEC_269_PROBLEM["03-lullaby"] == ("PEOPLE_DISAGREE", "problem.importance")


def test_the_eval_reads_the_corpus_as_keel_clouds_fixture_does():
    fixture = _need(CLOUD / "src" / "test" / "java" / "com" / "keeldiscovery" / "cloud" / "corpus"
                    / "VectorCorpusFixture.java")
    if not fixture.exists():
        pytest.skip("no VectorCorpusFixture")
    text = fixture.read_text(encoding="utf-8")
    for entry_id, (status, drift, n, inside) in corpus_mod.SPEC_269_MOVES.items():
        assert f'"{entry_id}", java.util.Map.of("problem.frequency", shared("{status}", "{drift}", {n}, {inside}))' \
            in text, entry_id
    for entry_id, (verdict, deciding) in corpus_mod.SPEC_269_PROBLEM.items():
        assert f'"{entry_id}", new String[] {{"{verdict}", "{deciding}"}}' in text, entry_id


def test_registry_five_is_read():
    path = _need(CLOUD / "src" / "main" / "resources" / "keel" / "dimension-registry.json")
    registry = registry_mod.load(path)
    if not registry_mod.is_269(registry):
        pytest.skip("keel-cloud before 269")
    assert len(registry.dimensions) == 12 and "problem.current_solution_satisfaction" not in registry.keys()
    assert registry.by_key("problem.frequency").respondent_control == registry_mod.FIXED_FIVE_CONTROL
    assert registry.by_key("problem.frequency").compare_rule == registry_mod.SHARE_RULE


# ------------------------------------------------------------------------------------------- FR-11, FR-12

def test_a_free_reading_that_moved_credits_is_named():
    rows = [{"action": "STORY_TURN", "credits": 0, "price_credits": 0},
            {"action": "EXPERIENCE_WAYS", "credits": 0, "price_credits": 0}]
    assert charge.free_reading_faults(rows) == [] and charge.reading_rows(rows) == {"STORY_TURN": 1,
                                                                                   "EXPERIENCE_WAYS": 1}
    assert charge.free_reading_faults([{"action": "EXPERIENCE_WAYS", "credits": -5, "price_credits": 5}])
    table = _java("domain", "connect", "InferenceCharge.java")
    assert int(re.search(r"public static final int VERSION = (\d+);", table).group(1)) == charge.PRICE_VERSION_270
    assert re.search(r"EXPERIENCE_WAYS\s*\(\s*0,", table) and re.search(r"STORY_TURN\s*\(\s*0,", table)


def test_contract_87_is_the_one_the_walk_reads():
    text = _need(CLOUD / "canon" / "openapi-v2.yaml").read_bytes()
    assert tv.contract_version(CLOUD) == tv.CONTRACT
    for field in (b"verdictLine", b"otherTasks", b"fixed_five", b"capped", b"ExperienceWays", b"pain:"):
        assert field in text, field
    digest = hashlib.sha256(text).hexdigest()
    if digest != CONTRACT_87:
        pytest.skip(f"keel-cloud's contract moved past 87 ({digest[:12]}): re-cut this pin")
    assert digest == CONTRACT_87


def test_the_report_names_the_three_surfaces_and_the_seven_beats():
    iv = _interview()
    surfaces = {"problem": {"wire": {"orb": {"record": ts.served_record(iv), "source": "the link as served"},
                                     "face": {"record": ts.served_record(iv), "source": "the link as served"},
                                     "card": {"record": ts.card_record(_card(iv, gate="In the last week, did you?")),
                                              "source": "the call's script"}}}}
    verdicts = {"problem": {"wire": ts.same_script({k: v["record"] for k, v in surfaces["problem"]["wire"].items()})}}
    rows = report.surface_rows(surfaces, verdicts)
    assert [(r["surface"], r["kind"]) for r in rows] == [("orb", "wire"), ("face", "wire"), ("card", "wire")]
    md = "\n".join(report.surfaces_markdown(rows))
    assert "## The three surfaces (spec 161" in md and "**parts at step 2** (`gate`) on the card: words" in md
    founder = [{"label": "the script's words", "project": "12345678-a", "wire": True, "telling": "script",
                "beats": [1, 2, 3, 4, 5, 6, 7], "board": {"who": "Plot keepers", "otherTasks": ["a", "b"]},
                "verdictLine": ss.VERDICT_LINE, "scenes": ss.scenes_verdict(_story())}]
    md = "\n".join(report.founder_beats_markdown(founder))
    assert "## The founder's seven beats (spec 161" in md and "(on the wire)" in md and "otherTasks: a; b" in md
    assert "the pain at [6]" in md and report.surfaces_markdown([]) == [] and report.founder_beats_markdown(None) == []


def test_the_web_checkouts_are_named():
    assert isinstance(ss.web_has_257(WEB), bool) and isinstance(ss.web_has_258(WEB), bool)
    assert tv.FR1B_TELLING == "two-part" and tv.FR1C_TELLING == "limits-only"
    assert [k for k, _, _ in tv.FR1A_TOLD] == ["a-script", "a-long"]


def test_a_ladder_is_compared_as_its_bands():
    """Spec 161 FR-9 (the run's reading): the card lays the price ladder out in two steps -- its bands held as a set."""
    served = [ts.step("commercial.price", "Worth?", ["Under $10", "$10 to $20", "$20 or more", "I wouldn't pay"])]
    card = {"passages": [{"kind": "item", "dimension": "commercial.price", "stem": "Worth?",
                          "options": [{"optionId": None, "label": "$10 to $20"}, {"optionId": "x", "label": "I wouldn't pay"}],
                          "twoSteps": {"under": {"options": [{"optionId": "a", "label": "Under $10"},
                                                             {"optionId": "b", "label": "$10 to $20"}]},
                                       "over": {"options": [{"optionId": "c", "label": "$20 or more"}]}}}]}
    assert ts.same_script({"orb": served, "card": ts.card_record(card)})["same"] is True


def test_a_second_stem_on_the_card_is_reported_not_compared():
    """Spec 161 FR-9 (run 3's reading): the card carries a rung's second stem's hint (`followUp.also`), the link one
    `followUps` entry a rung -- the second stem is kept on the card's record and not compared."""
    served = [ts.step(ts.FREQUENCY, "How often?", list(ts.FREQUENCY_LABELS), [ts.DIFFERENCE_WHY])]
    card = {"passages": [{"kind": "item", "dimension": ts.FREQUENCY, "stem": "How often?",
                          "options": [{"optionId": str(i), "label": x} for i, x in enumerate(ts.FREQUENCY_LABELS)],
                          "followUp": {"against": [], "hint": {"third": ts.DIFFERENCE_WHY},
                                       "also": {"on": ["4"], "hint": {"third": ts.NEVER_WHY}}}}]}
    record = ts.card_record(card)
    assert record[0]["also"] == [ts.NEVER_WHY]
    assert ts.same_script({"orb": served, "card": record})["same"] is True
