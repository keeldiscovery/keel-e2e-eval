"""Spec 162 -- the solution, walked: the mirrors of keel-cloud 271 / 272 / 273 and keel-web 259 / 260 / 261, held here
without a stack (the walk itself is `make e2e-157`).

- FR-1 the founder's four beats (`story_screens.said_idea`, `idea_scripts`, `idea_question`), the brand page's words,
  the board's six rows (`board_six_verdict`);
- FR-2 the verdict line, the pilot ask, no belief page on a spoken SOLUTION (`vectors_screens.calibrates`);
- FR-3 the film in five chapters (`idea_scenes_verdict`) on keel-cloud's own example;
- FR-5 / FR-6 the solution link's words and the three yes-or-no questions (`harness/solution_surfaces.py`), `yes_no` in
  the classifier and the working rung, the corpus read through 272 (`instructions/corpus.READ_REVISION_162`);
- FR-7 / FR-8 the whys owed, the share bars, the So lines, the brief's rows, Insights;
- FR-9 the three surfaces' records; FR-10 nothing bought; FR-11 the contract and the report's sections;
- the dimension cards the three moved to (`quality.cards.CARDS_SHA256`).

The words are read off the stack's sibling checkouts (`stack.toml`), word for word; a checkout without them skips.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

from evals import three_views as tv
from evals import three_views_report as report
from harness import classifier_guard as guard
from harness import interview_charge as charge
from harness import solution_surfaces as sol
from harness import story_screens as ss
from harness import three_surfaces as ts
from harness import vectors_screens as vs_screens
from harness import working_rung as wr
from instructions import corpus as corpus_mod
from quality import cards
from stack.config import load_config

CONFIG = load_config(validate=False)
CLOUD = Path(CONFIG.keel_cloud)
WEB = Path(CONFIG.keel_web)
JAVA = CLOUD / "src" / "main" / "java" / "com" / "keeldiscovery" / "cloud"


def _need(path: Path) -> Path:
    if not path.exists():
        pytest.skip(f"no {path}")
    return path


def _java_string(rel: str, name: str) -> str:
    """A Java `static final String NAME = "..." + "...";` constant, its pieces joined."""
    text = _need(JAVA / rel).read_text(encoding="utf-8")
    block = re.search(rf"String {name} = (.*?);\n", text, re.S)
    assert block, name
    return "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', block.group(1)))


def readings() -> dict:
    _need(CLOUD / ss.FAKE_READINGS)
    return ss.fake_readings(CLOUD)


def _needs_271() -> None:
    if not (JAVA / "domain" / "story" / "IdeaTurns.java").exists() or \
            "TAGLINE_MAX_WORDS" not in (JAVA / "domain" / "story" / "IdeaTurns.java").read_text(encoding="utf-8"):
        pytest.skip("keel-cloud 271 not in the checkout")


# ------------------------------------------------------------------------------------------------ FR-1 the beats

def test_the_four_beats_are_the_scripts_in_order():
    _needs_271()
    script = readings()
    said = ss.said_idea(script)
    assert [n for n, _ in said] == [1, 2, 3, 4]
    with pytest.raises(ValueError, match="not keel-cloud 271's four"):
        ss.said_idea({"ideaTurns": [{"turn": 1, "heard": "a", "result": {}}, {"turn": 3, "heard": "b", "result": {}}]})


def test_the_special_scripts_are_the_clouds():
    """FR-1: one beat 1 with advantages alone (no step: code's ask), one beat 3 leaving a limitation unmatched and its two
    corrections (a match, a cross), beat 4's features (code's ask) and its joy -- every word the fake script's."""
    _needs_271()
    script = readings()
    s = ss.idea_scripts(script)
    assert all(s[k] for k in ("workflow", "advantages_only", "first_step", "setup", "setup_none", "limits", "match",
                              "cross", "joy")) and s["features"]
    assert not ss.idea_reading_of(script, 1, s["advantages_only"]).get("workflow")
    assert ss.idea_reading_of(script, 1, s["first_step"]).get("workflow")
    assert any(not a["solved"] for a in ss.idea_reading_of(script, 3, s["limits"])["limit_answers"])
    assert all(a["solved"] for a in ss.idea_reading_of(script, 3, s["match"], correction=True)["limit_answers"])
    assert not all(a["solved"] for a in ss.idea_reading_of(script, 3, s["cross"], correction=True)["limit_answers"])
    assert all(ss.idea_reading_of(script, 4, f)["is_feature"] for f in s["features"])
    assert ss.idea_reading_of(script, 4, s["joy"])["is_feature"] is False
    assert len(s["limits"]) > ss.LONG_ANSWER_MIN // 2


def test_every_telling_says_the_scripts_words_and_the_long_beat_3_splits_whole():
    _needs_271()

    class _Run:
        pass
    run = _Run()
    run.readings = readings()
    heard = {str(t["heard"]) for t in run.readings["ideaTurns"]}
    for telling in tv.IDEA_TELLINGS:
        plan = tv.idea_plan(run, telling)
        assert sorted(plan) == [1, 2, 3, 4]
        for n, p in plan.items():
            assert p["words"] in heard and all(t in heard for t in p.get("then") or [])
    asks = tv.idea_plan(run, "asks")
    first, second = asks[3]["two_part"]
    assert f"{first} {second}" == asks[3]["words"] and first.endswith("That is the first one.")
    assert asks[1]["then"] and asks[4]["then"] and asks[3]["then"]


def test_the_questions_asks_and_lines_are_keel_clouds_word_for_word():
    _needs_271()
    rel = "domain/story/IdeaTurns.java"
    text = (JAVA / rel).read_text(encoding="utf-8")
    block = text.split("QUESTIONS = List.of(", 1)[1].split(");", 1)[0]
    questions = [ "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', q)) for q in re.split(r'",\s*\n\s*"', block)]
    joined = "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', block))
    assert joined == "".join(ss.IDEA_QUESTIONS[n] for n in ss.IDEA_BEATS) and questions
    for name, ours in (("OPENING", ss.IDEA_OPENING), ("STEP_ASK", ss.STEP_ASK), ("UNMATCHED_ASK", ss.UNMATCHED_ASK),
                       ("NOT_SOLVED", ss.NOT_SOLVED), ("FEATURE_ASK", ss.FEATURE_ASK),
                       ("NOTHING_TO_SET_UP", ss.NOTHING_TO_SET_UP), ("PILOT_ASK", ss.PILOT_ASK)):
        assert _java_string(rel, name) == ours, name
    assert _java_string("domain/vectors/SolutionBeliefs.java", "DEFAULT_VERDICT") == ss.SOLUTION_VERDICT_LINE


def test_a_question_is_filled_as_the_cloud_fills_it():
    """keel-cloud 271 `IdeaTurns.question`: the person with an article, the job bare; the limitations counted in words,
    lower-cased and joined; the cost lower-cased; *it* where no name."""
    assert ss.idea_question(1, name="Runcheck", person="payroll practitioner", job="check the payroll.") == (
        "Now I want to know how Runcheck does the same task. With Runcheck in their hands, how does a payroll "
        "practitioner check the payroll, from the first step to the last?")
    assert ss.idea_question(3, name="Runcheck", limits=["The hours disagree", "Rates change", "IT signs off"]) == (
        "Today they ran into three things: the hours disagree, rates change and IT signs off. Tell me how Runcheck "
        "solves them.")
    assert ss.idea_question(4, name="", cost="Someone gets paid wrong.") == (
        "In the problem, the cost to them was someone gets paid wrong. Now, with it, what do they get instead? Tell me "
        "the opposite of that cost.")
    assert ss.idea_opening("payroll practitioners").startswith("Now we know what payroll practitioners are trying")
    assert ss.unmatched_line(ss.NOT_SOLVED, ["Mistakes are found late"]) == "I will show mistakes are found late as not solved."
    assert ss.pilot_ask("Runcheck").startswith("Now Runcheck is defined.")


def test_the_brand_page_and_the_failed_build_say_keel_webs_words():
    translate = _need(WEB / "src" / "lib" / "translate.ts").read_text(encoding="utf-8")
    if not ss.web_has_259(WEB):
        pytest.skip("keel-web 259 not in the checkout")
    flat = re.sub(r'"\s*\+\s*"', "", translate)
    assert ss.LOGO_LINE in " ".join(flat.split())
    assert "`Keel could not draw ${part}. Say that part again?`" in translate
    for chapter, part in ss.FAILED_PARTS.items():
        assert f'{chapter}: "{part}"' in translate, chapter
    for chapter, words in ss.CHAPTER_WORDS.items():
        assert f'{chapter}: "{words}"' in translate, chapter
    lines = (WEB / "src" / "lib" / "ideaLines.ts").read_text(encoding="utf-8")
    assert f"PLATE_MS = {ss.PLATE_MS:_}" in lines and "TAGLINE_MAX_WORDS = 8" in lines
    for hex_ in ss.BRAND_SWATCHES:
        assert f'"{hex_}"' in lines
    assert len(ss.IDEA_TAGLINE.split()) <= 8 and ss.IDEA_COLOUR in ss.BRAND_SWATCHES


def test_a_non_square_png_is_built_with_its_sides():
    png = ss.png_bytes(400, 300)
    assert png[:8] == b"\x89PNG\r\n\x1a\n" and int.from_bytes(png[16:20], "big") == 400 \
        and int.from_bytes(png[20:24], "big") == 300


BOARD = {"rows": [
    {"box": "product", "text": "Runcheck Every changed line, seen before sign-off.", "items": []},
    {"box": "workflow", "text": "they Open Runcheck when the run is ready Runcheck Flags every line that changed",
     "items": []},
    {"box": "setup", "text": "Connect the two hour systems", "items": []},
    {"box": "statement", "text": "Runcheck reads the hours from both systems.", "items": []},
    {"box": "limits", "text": "The hours disagree Nobody tells them", "items": [{"mark": "tick"}, {"mark": "cross"}]},
    {"box": "joy", "text": "A pay run they can sign off calmly", "items": []}]}
IDEA = {"workflow": [{"step": "open Runcheck when the run is ready", "by": "PERSON"},
                     {"step": "flags every line that changed", "by": "PRODUCT"}],
        "setup": ["connect the two hour systems"], "setupNone": False,
        "statement": "Runcheck reads the hours from both systems.",
        "limitAnswers": [{"limit": "The hours disagree", "solved": True}, {"limit": "Nobody tells them", "solved": False}],
        "advantage": "Every line checked", "joy": "A pay run they can sign off calmly"}


def test_the_board_is_six_rows_by_data_box_holding_the_ideas_words():
    v = ss.board_six_verdict(BOARD, IDEA, name="Runcheck", tagline="Every changed line, seen before sign-off.")
    assert v["ok"], v
    swapped = {"rows": [BOARD["rows"][1], BOARD["rows"][0]] + BOARD["rows"][2:]}
    assert not ss.board_six_verdict(swapped, IDEA, name="Runcheck", tagline=None)["ok"]
    wrong = {"rows": BOARD["rows"][:4] + [dict(BOARD["rows"][4], items=[{"mark": "tick"}, {"mark": "tick"}])]
             + BOARD["rows"][5:]}
    assert "marks" in ss.board_six_verdict(wrong, IDEA, name="Runcheck", tagline=None)["missing"]


# ------------------------------------------------------------------------------------------------ FR-2 the corridor

def test_no_belief_page_on_a_spoken_solution_and_the_typed_path_unchanged():
    assert not vs_screens.calibrates("SOLUTION", "SOLUTION", spoken=True)
    assert not vs_screens.calibrates("SOLUTION", "SOLUTION_COMMERCIAL", spoken=True)
    assert vs_screens.calibrates("SOLUTION", "SOLUTION") and vs_screens.calibrates("COMMERCIAL", "SOLUTION_COMMERCIAL",
                                                                                  spoken=True)
    review = {"rows": [{"dimension": k, "answer": {"codes": ["p_60_80"]}} for k in vs_screens.SOLUTION_WRITTEN],
              "complete": True}
    calibration = {"questions": [{"dimension": k, "options": [{"normalized": "p_60_80", "label": "6 or 7 in 10"}]}
                                 for k in vs_screens.SOLUTION_WRITTEN], "total": 3, "answered": 3}
    written = vs_screens.solution_written(review, calibration)
    assert written["codes"] == {k: ["p_60_80"] for k in vs_screens.SOLUTION_WRITTEN}
    assert set(written["labels"].values()) == {vs_screens.SOLUTION_BIN_LABEL}
    assert vs_screens.solution_calibration_answered(calibration)
    assert not vs_screens.solution_calibration_answered({"total": 3, "answered": 2})


# ------------------------------------------------------------------------------------------------ FR-3 the film

def _idea_example() -> dict:
    import yaml                                                                 # noqa: PLC0415
    doc = yaml.safe_load(_need(CLOUD / "canon" / "openapi-v2.yaml").read_text(encoding="utf-8"))
    return doc["components"]["schemas"]["IdeaView"]["examples"][0]


def test_the_films_example_reads_in_five_chapters():
    """FR-3 on keel-cloud's own IdeaView example (the Runcheck board): the opening line, the chapters in order, the joy
    last and upright with the board's joy (said to *you*), a picture on every scene, the plate the brand."""
    example = _idea_example()
    story = example["build"]["story"]
    v = ss.idea_scenes_verdict(story, example, name="Runcheck", tagline=example["brand"]["tagline"])
    parts = v["parts"]
    for name in ("at most eleven", "the opening line", "the joy last", "the brand on every screen",
                 "a picture on every scene", "the plate the brand"):
        assert parts[name], (name, v)
    assert v["chapters"] == ["before", "task", "joy"]
    # the example is the contract's sample (three scenes): the chapters it leaves out are named, never passed
    assert not parts["the chapters in order"] and not parts["one scene a step"]


def test_a_full_film_holds_every_part_and_a_broken_one_names_it():
    name = "Runcheck"
    screen = {"name": name, "colour": "#2255aa", "iconAssetId": None, "letter": "R"}
    scene = lambda line, **kw: dict({"line": line, "pictogramId": "screen", "screen": screen, "clipId": None,
                                     "pictureAssetId": "p", "mark": None}, **kw)        # noqa: E731
    story = {"scenes": [scene("This time, Runcheck is on the screen.", chapter="before"),
                        scene("First you connect the two hour systems."),
                        scene("You open Runcheck when the run is ready.", chapter="task"),
                        scene("Runcheck flags every line that changed."),
                        scene("It reads the hours from both systems.", chapter="solves",
                              marks=[{"limit": "The hours disagree", "mark": "tick"},
                                     {"limit": "Nobody tells them", "mark": "cross"}]),
                        scene("Every line checked.", chapter="better"),
                        scene("A pay run you can sign off calmly.", chapter="joy", joy=True)],
             "clipIds": ["c"] * 8, "plate": {"name": name, "tagline": "T"}}
    v = ss.idea_scenes_verdict(story, IDEA, name=name, tagline="T")
    assert v["ok"], v
    no_setup = dict(IDEA, setup=[], setupNone=True)
    assert not ss.idea_scenes_verdict(story, no_setup, name=name)["parts"]["the setup scene iff a setup"]
    no_adv = dict(IDEA, advantage=None)
    assert not ss.idea_scenes_verdict(story, no_adv, name=name)["parts"]["the advantage iff read"]
    unpictured = dict(story, scenes=[dict(s, pictureAssetId=None) for s in story["scenes"]])
    assert not ss.idea_scenes_verdict(unpictured, IDEA, name=name)["parts"]["a picture on every scene"]
    assert ss.failed_say("joy") == "Keel could not draw what they get. Say that part again?"
    assert ss.BEAT_OF_CHAPTER["joy"] == 4 and ss.BEAT_OF_CHAPTER["task"] == 1


# ------------------------------------------------------------------------------------------------ FR-5 the link

def test_the_links_words_are_keel_clouds():
    rel = "application/SolutionLink.java"
    _need(JAVA / rel)
    for name, ours in (("TO_THE_FILM", sol.TO_THE_FILM), ("BELIEVES", sol.OPENING), ("BELIEVES_SPLIT", sol.OPENING_SPLIT),
                       ("ONE_QUESTION", sol.ONE_QUESTION), ("PLATE_BEFORE", sol.PLATE_BEFORE),
                       ("PLATE_AFTER", sol.PLATE_AFTER), ("PILOT", sol.PILOT)):
        assert _java_string(rel, name) == ours, name
    questions = (JAVA / "domain" / "vectors" / "SolutionQuestions.java").read_text(encoding="utf-8")
    flat = re.sub(r'"\s*\+\s*"', "", questions)
    for words in (sol.COMPATIBILITY_Q, sol.COMPATIBILITY_GIVING, sol.RELATIVE_ADVANTAGE_Q, sol.RELATIVE_ADVANTAGE_GIVING,
                  sol.ADOPTION_NONE_Q):
        assert words.split("{")[0] in flat, words


def _interview(*, setup: bool = True, pilot: bool = True) -> dict:
    name, founder = "Runcheck", "Ada"
    af = (sol.ADOPTION_SETUP_Q.replace("{name}", name).replace("{the setup}", "to connect the two hour systems")
          if setup else sol.ADOPTION_NONE_Q.replace("{name}", name))
    items = [{"itemId": f"i{k}", "dimension": key, "control": "yes_no", "escape": None, "question": q,
              "options": [{"optionId": f"i{k}y", "label": "Yes"}, {"optionId": f"i{k}n", "label": "No"}]}
             for k, (key, q) in enumerate(zip(sol.SOLUTION_DIMENSIONS, (
                 "Would checking the payroll before it goes out this way, with Runcheck, fit into how you work?",
                 "Compared with the way you check the payroll before it goes out today, would Runcheck be better?",
                 af)))]
    out = {"founderFirstName": founder,
           "passages": {"opening": f"{founder} believes payroll practitioners have a problem when they check the "
                                   "payroll. First, one question.", "toTheFilm": sol.TO_THE_FILM},
           "gate": {"question": ts.GATE_WORDS, "condition": {"question": "Do you run payroll?"}, "noLabel": "No"},
           "story": {"scenes": [{}], "readInstead": ["One.", "Two two."]},
           "ideaStory": {"scenes": [{}, {"joy": True}], "readInstead": ["Three three three."],
                         "plate": {"name": name}},
           "plate": {"name": name, "tagline": "T", "before": f"Now {founder} has built {name}.",
                     "after": sol.PLATE_AFTER},
           "parts": [{"items": items}],
           "followUps": [{"dimension": k, "spoken": sol.WHYS[k][0]} for k in sol.SOLUTION_DIMENSIONS],
           "minutes": 3}
    if pilot:
        out["pilot"] = {"question": f"Would you try {name} for real?"}
    return out


def test_the_links_order_and_words_read_clean_and_faults_are_named():
    iv = _interview()
    assert sol.link_faults(iv, founder="Ada", name="Runcheck", tagline="T") == []
    assert sol.question_faults(iv, name="Runcheck", setup=["connect the two hour systems"]) == []
    none = _interview(setup=False)
    assert sol.question_faults(none, name="Runcheck", setup=[]) == []
    assert sol.question_faults(none, name="Runcheck", setup=["connect the two hour systems"])
    revealed = dict(iv, reveal={"what": "Imagine Runcheck"})
    assert any("reveal" in f for f in sol.link_faults(revealed, founder="Ada", name="Runcheck", tagline="T"))
    unoffered = _interview(pilot=False)
    assert sol.link_faults(unoffered, founder="Ada", name="Runcheck", tagline="T", pilot=False) == []
    assert sol.link_faults(unoffered, founder="Ada", name="Runcheck", tagline="T", pilot=True)
    long = dict(iv, passages=dict(iv["passages"], opening="Ada believes " + "very " * 25 + "much. First, one question."))
    assert any("past 20" in json.dumps(f) for f in sol.link_faults(long, founder="Ada", name="Runcheck", tagline="T"))
    timed = sol.first_question_seconds(iv)
    assert timed["seconds"] > sol.PLATE_SECONDS and timed["minutes served"] == 3


# ------------------------------------------------------------------------------------------------ FR-6 yes or no

def test_yes_no_is_one_pick_of_two_with_no_escape():
    assert guard.SOLUTION_CONTROLS == ("yes_no",) and "yes_no" in guard._SINGLE
    served = guard.served_items(_interview())
    three = [s for s in served if s.dimension in sol.SOLUTION_DIMENSIONS]
    assert len(three) == 3 and all(s.kind == "single" and s.options == ("Yes", "No") and s.escape is None
                                   for s in three)
    yesno = {(c.said): c.expected for c in guard.all_cases() if c.item == "yesno"}
    assert yesno == {"yes": {"picks": [1]}, "no": {"picks": [2]}, "A": {"picks": [1]}, "B": {"picks": [2]},
                     "si": {"unclear": True}}
    assert [wr.yes_no_side(x) for x in ("yes", "Yes", "A", "no", "b", "si", None)] == [
        "held", "held", "held", "against", "against", None, None]


def test_the_corpus_is_read_through_272():
    """FR-6 (keel-cloud 272 judgement call 17): the corpus's three solution dimensions read yes or no by one rule, the
    founder's list as the default bin, the golden rows moved as keel-cloud's fixture moves them."""
    assert corpus_mod.READ_REVISION_162 == "r23+269+272"
    for code in ("yes_easily", "yes_with_steps", "a_lot_better", "a_little_better", "yes", "yes_if_worth_it"):
        assert corpus_mod.spec272_solution(code) == "yes"
    for code in ("only_with_help", "no", "no_difference", "worse", "probably_not"):
        assert corpus_mod.spec272_solution(code) == "no"
    assert corpus_mod.spec272_solution({"answer": "positive", "advantages": []}) == "yes"
    assert corpus_mod.spec272_solution({"chip": "cant_tell"}) == {"chip": "cant_tell"}
    assert corpus_mod.spec272_founder_bin({"solution.compatibility": {"answer": {}}}, "solution.compatibility") == \
        "p_60_80"
    assert corpus_mod.spec272_founder_bin({"solution.compatibility": {"unsure": True}}, "solution.compatibility") is None
    fixture = _need(CLOUD / "src/test/java/com/keeldiscovery/cloud/corpus/VectorCorpusFixture.java").read_text(
        encoding="utf-8")
    moves = " ".join(fixture.split("SPEC_272_MOVES =", 1)[1].split("SPEC_272_SOLUTION", 1)[0].split())
    entries = re.findall(r'"(\d\d-[a-z]+)", java\.util\.Map\.of\(', moves)
    assert set(entries) == set(corpus_mod.SPEC_272_MOVES)
    pairs = re.findall(r'"(solution\.[a-z_]+)", statusOnly\("([A-Z_]+)", (null|"[a-z]+")\)', moves)
    assert sorted((k, s, "" if d == "null" else d.strip('"')) for k, s, d in pairs) == sorted(
        (k, s, d or "") for e in corpus_mod.SPEC_272_MOVES.values() for k, (s, d) in e.items())
    assert '"03-lullaby", new String[] {"HOLDING_UP", "solution.compatibility"}' in fixture
    read = corpus_mod.expected_269("03-lullaby", {"standings": {"solution.adoption_friction": {"status": "PEOPLE_DISAGREE",
                                                                                               "drift": "short"}},
                                                  "vector_verdicts": {"SOLUTION": {"verdict": "PEOPLE_DISAGREE"}}})
    assert read["standings"]["solution.adoption_friction"] == {"status": "HOLDING_UP"}
    assert read["vector_verdicts"]["SOLUTION"] == {"verdict": "HOLDING_UP", "deciding": "solution.compatibility"}
    assert corpus_mod.picks_269({"solution.relative_advantage": "a_lot_better", "problem.frequency": 7}, 7) == {
        "solution.relative_advantage": "yes", "problem.frequency": "every_time"}


# ------------------------------------------------------------------------------------------------ FR-7 every why

def test_the_roster_owes_a_why_after_every_no_two_at_most():
    assert [p["owed"] for p in sol.SOLUTION_ROSTER] == [list(sol.owed(p["picks"])[0]) for p in sol.SOLUTION_ROSTER]
    assert [p["capped"] for p in sol.SOLUTION_ROSTER] == [list(sol.owed(p["picks"])[1]) for p in sol.SOLUTION_ROSTER]
    assert sol.SOLUTION_ROSTER[0]["owed"] == [] and sol.SOLUTION_ROSTER[-1]["capped"] == [sol.ADOPTION_FRICTION]
    assert {tuple(p["owed"]) for p in sol.SOLUTION_ROSTER[1:4]} == {(k,) for k in sol.SOLUTION_DIMENSIONS}
    body = sol.response_for(sol.SOLUTION_ROSTER[-1], _interview(), fmt="TEXT",
                            whys=[{"dimension": sol.COMPATIBILITY}, {"dimension": sol.RELATIVE_ADVANTAGE}])
    assert body["recency"] is True and "story" not in body and [a["optionIds"] for a in body["answers"]] == [
        ["i0n"], ["i1n"], ["i2n"]] and [f["dimension"] for f in body["followUps"]] == [sol.COMPATIBILITY,
                                                                                        sol.RELATIVE_ADVANTAGE]


def test_the_whys_are_the_registrys():
    registry = _need(CLOUD / "src/main/resources/keel/dimension-registry.json")
    rows = {d["key"]: d for d in json.loads(registry.read_text(encoding="utf-8"))["dimensions"]}
    if rows["solution.compatibility"]["respondent"]["control"] != "yes_no":
        pytest.skip("keel-cloud 272 not in the checkout")
    for key, (text, heading) in sol.WHYS.items():
        f = rows[key]["follow_up"]
        assert (f["text"], f["spoken"], f["heading"], f["against"]) == (text, text, heading, ["no"]), key


# ------------------------------------------------------------------------------------------------ FR-8 the page

def _standings(*, yes=3, n=5, so="3 of 5 said yes.") -> dict:
    dims = [{"dimension": k, "chart": {"share": {"yes": yes, "n": n, "proportion": round(yes / n, 2),
                                                 "founderBand": "p_60_80"}},
             "choice": {"optionCounts": [{"label": "Yes", "count": yes}, {"label": "No", "count": n - yes}]},
             "so": so} for k in sol.SOLUTION_DIMENSIONS]
    return {"vectors": [{"vector": "SOLUTION", "dimensions": dims}],
            "insights": [{"dimension": k, "against": 2, "asked": 1, "capped": 1, "rungHeading": sol.WHYS[k][1],
                          "quotes": [{"option": "No", "text": "x"}]} for k in sol.SOLUTION_DIMENSIONS],
            "facts": {"solution": {"rows": [{"key": k, "yes": yes, "n": n, "share": round(yes / n, 2),
                                             "founderBand": "p_60_80"} for k in sol.SOLUTION_DIMENSIONS]}}}


def test_the_founders_page_reads_share_bars_evidence_and_the_brief():
    picks = [p["picks"] for p in sol.SOLUTION_ROSTER]
    page = _standings(yes=3, n=5)
    assert sol.share_faults(page, picks) == [] and sol.brief_faults(page["facts"], picks) == []
    assert sol.so_line_faults(page) == [] and sol.insights_faults(page, capped_by={sol.ADOPTION_FRICTION: 1}) == []
    assert sol.share_faults(_standings(yes=4, n=5), picks)
    assert sol.so_line_faults(_standings(so="3 of 5 said yes. You should try a pilot next."))
    scaled = _standings()
    scaled["vectors"][0]["dimensions"][1]["chart"]["benefit"] = {"codes": ["a_lot_better"]}
    assert sol.share_faults(scaled) and sol.so_line_faults(scaled)
    took = _standings()
    took["insights"][0]["tookBy"] = 1
    assert sol.insights_faults(took)


# ------------------------------------------------------------------------------------------------ FR-9 three surfaces

def _script() -> dict:
    iv = _interview()
    return {"passages": [
        {"kind": "intro", "text": {"third": iv["passages"]["opening"], "first": "I believe payroll ..."}},
        {"kind": "gate", "condition": {"question": "Do you run payroll?"}, "bridge": sol.TO_THE_FILM,
         "lines": iv["story"]["readInstead"], "stem": ts.GATE_WORDS,
         "options": [{"optionId": "YES", "label": "Yes"}, {"optionId": "NO", "label": "No"}]},
        {"kind": "plate", "name": "Runcheck", "before": {"third": iv["plate"]["before"], "first": "Now I have built "
                                                                                                  "Runcheck."},
         "after": {"third": sol.PLATE_AFTER, "first": "and I believe it solves this. Let us see."},
         "lines": iv["ideaStory"]["readInstead"], "pictures": ["p"]},
        *[{"kind": "item", "itemId": i["itemId"], "dimension": i["dimension"], "stem": i["question"],
           "options": i["options"], "followUp": {"against": [i["options"][1]["optionId"]],
                                                 "hint": {"third": sol.WHYS[i["dimension"]][0],
                                                          "first": sol.WHYS[i["dimension"]][0]}}}
          for i in iv["parts"][0]["items"]],
        {"kind": "pilot", "question": {"third": "Would you try Runcheck for real?",
                                       "first": "Would you try Runcheck for real?"}}]}


def test_the_three_records_are_one_script_and_a_part_is_named():
    served = sol.served_record(_interview())
    assert [r["step"] for r in served] == ["opening", "screener", "bridge", "film:problem", "check", "plate", "film:idea",
                                           *sol.SOLUTION_DIMENSIONS, "pilot"]
    card = sol.card_record(_script())
    assert ts.same_script({"orb": served, "face": served, "card": card})["same"] is True
    assert sol.first_person_faults(_script(), name="Runcheck") == []
    moved = _script()
    moved["passages"][2]["after"]["third"] = "and believes it solves that."
    v = ts.same_script({"orb": served, "face": served, "card": sol.card_record(moved)})
    assert v["same"] is False and v["step"] == "plate" and v["surface"] == "card" and "words" in v["differs"]


# ------------------------------------------------------------------------------------------------ FR-10, FR-11

def test_nothing_is_bought_on_the_solution():
    rows = [{"action": a, "credits": 0, "price_credits": 0} for a in ("IDEA_TURN", "STORY_PICTURES", "PICTURE_REVIEW")]
    assert charge.solution_reading_faults(rows) == []
    assert charge.reading_rows(rows) == {"IDEA_TURN": 1, "STORY_PICTURES": 1, "PICTURE_REVIEW": 1}
    assert charge.solution_reading_faults([{"action": "STORY_PICTURES", "credits": -40, "price_credits": 40}])
    table = next(JAVA.rglob("InferenceCharge.java"), None)
    if table is None:
        pytest.skip("no InferenceCharge in the checkout")
    text = table.read_text(encoding="utf-8")
    if int(re.search(r"public static final int VERSION = (\d+);", text).group(1)) < charge.PRICE_VERSION_273:
        pytest.skip("keel-cloud 273 not in the checkout")
    for row in ("IDEA_TURN", "STORY_PICTURES", "PICTURE_REVIEW"):
        assert re.search(rf"{row}\s*\(\s*0,", text), row


def test_contract_90_is_the_one_the_walk_reads():
    text = _need(CLOUD / "canon" / "openapi-v2.yaml").read_text(encoding="utf-8")
    if tv.contract_version(CLOUD) != tv.CONTRACT:
        pytest.skip(f"keel-cloud's contract is {tv.contract_version(CLOUD)}, not {tv.CONTRACT}")
    for field in ("toTheFilm", "plateBefore", "yes_no", "share_yes", "pilotAsk", "failedChapter", "pictureAssetId"):
        assert field in text, field


def test_the_report_has_the_founders_solution_and_the_solution_surfaces():
    solution = {"label": "the solution", "project": "abcdef12",
                "idea": {"brand": {"name": "Runcheck", "tagline": "T", "colour": "#1f7a5a"}, **IDEA,
                         "verdictLine": ss.SOLUTION_VERDICT_LINE, "pilot": True},
                "after": {"verdict": {"drawn": True, "words": ss.SOLUTION_VERDICT_LINE},
                          "pilot": {"ask": ss.pilot_ask("Runcheck"), "put": {"status": 200}}}}
    lines = report.founders_solution_markdown(solution, [{"label": "the solution", "verdict": {
        "scenes": 7, "chapters": ["before", "task", "joy"], "clips": 8, "parts": {"x": True}}}],
        {"orb": sol.first_question_seconds(_interview())})
    text = "\n".join(lines)
    assert "## The founder's solution" in text and "pilot ask heard" in text and "time to the first question" in text
    rows = report.surface_rows({"solution": {"wire": {"orb": {"record": sol.served_record(_interview()),
                                                              "source": "s"}}}}, {})
    assert rows[0]["gate"] == ts.GATE_WORDS


# ------------------------------------------------------------------------------------------------ the cards

def test_the_cards_digest_is_the_one_spec_162_moved():
    """keel-cloud 272 judgement call 16: the dimension cards for the three are this spec's -- `quality.cards`
    `CARDS_SHA256` is the file's digest; keel-cloud's copy differs from it in the moved cards alone until vendored."""
    ours = cards.CARDS_PATH.read_bytes()
    assert hashlib.sha256(ours).hexdigest() == cards.CARDS_SHA256
    theirs = CLOUD / "src/main/resources/keel/dimension-cards.md"
    if theirs.exists():
        assert set(cards.differing_cards(theirs.read_text(encoding="utf-8"))) <= set(cards.CARDS_MOVED_162)
    for key in ("solution.compatibility", "solution.relative_advantage", "solution.adoption_friction"):
        body = cards.card(key)
        assert "stranger `yes_no`" in cards.registry_line(body) and "compare `share_yes`" in cards.registry_line(body)
