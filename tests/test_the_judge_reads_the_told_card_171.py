"""Spec 171: the judge reads the told card -- the mirrors `make unit` holds, nothing paid (FR-5).

The truth file from a fixture walk (the payroll fixture: four stub strangers' stories and a chip, read by a stubbed
told-reader); the people sampled for their popups; T1-T4 on a fixture card that matches, one off and wrong; `told_pct`
and the score file's `told` block; the table's `told` column; the DRIFT line with both readings; the absent card (no
`told` served, the card not drawn, no story told); the capture on a page that draws nothing; `make read-films`' told
card end to end on a stubbed door (the truth's calls, the card's call, the dry run, the absent card spending nothing).
No stack and no model.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from harness import film_strangers as fs
from harness import film_told as ftold
from quality import film_reader as fread
from quality import film_rubric as fr
from quality import film_table as ft

REPO = Path(__file__).resolve().parent.parent
FIX_163 = Path(__file__).resolve().parent / "fixtures" / "film_163"

# ----------------------------------------------------------------------------------------------- the payroll fixture

PAYROLL_STORY = {"person": {"who": "payroll practitioners", "job": "run payroll"},
                 "act": "checking the run by hand against the timesheets",
                 "steps": ["export the hours", "check the run by hand"],
                 "limits": ["The hours come from systems that don't agree", "Nobody tells them when a rate changes",
                            "Mistakes are found after the money has gone"],
                 "cost": "A pay run they check twice and still fear"}

STORIES = {
    "Ada": "Last Thursday the hours from the rota did not match the clock system, so I checked the whole run by hand "
           "against the timesheets and it took my afternoon.",
    "Ben": "Two weeks ago a rate changed and nobody told me; we paid three people wrong and found out after the money "
           "had gone out.",
    "Cy": "On Monday the batch sat until the bank cut-off because the approver was away.",
    "Di": "It usually goes fine, I suppose it might happen some time.",
}
#: What the told-reader answers for each story (the truth), as raw JSON.
TRUTH_ANSWERS = {
    "Ada": {"limits": [1], "own": [], "way": "same", "way_said": "checked the run by hand", "pain": "same",
            "pain_said": "took my afternoon", "occasion": "real", "why": "A Thursday, what went wrong, what they did."},
    "Ben": {"limits": [2, 3], "own": [], "way": "none", "way_said": "", "pain": "differs",
            "pain_said": "paid three people wrong", "occasion": "real", "why": "Two weeks ago, one change, one cost."},
    "Cy": {"limits": [], "own": ["the approver was away"], "way": "none", "way_said": "", "pain": "none",
           "pain_said": "", "occasion": "real", "why": "Monday, the batch, the cut-off."},
    "Di": {"limits": [], "own": [], "way": "none", "way_said": "", "pain": "none", "pain_said": "",
           "occasion": "guess", "why": "General, no time told."},
}


def walks() -> list[dict]:
    out = [{"person": p, "invitation": f"inv-{p.lower()}", "story": s, "response": {"status": 201, "story": True}}
           for p, s in STORIES.items()]
    out.append({"person": "Eve", "invitation": "inv-eve", "response": {"status": 201, "story": False,
                                                                        "anchorChip": "CANT_RECALL"}})
    return out


def wire_people(**changes) -> list[dict]:
    """Keel's reading of each person (`InvitationDetail.experience`): by default the same as the truth."""
    base = {
        "Ada": {"way": "by hand", "wayMatch": "same", "limitsHit": [0], "ownLimits": [], "pain": "an afternoon",
                "painMatch": "same", "painCount": None, "confirms": 3, "differs": 0, "guessed": False},
        "Ben": {"way": None, "wayMatch": None, "limitsHit": [1, 2], "ownLimits": [], "pain": "paid wrong",
                "painMatch": "differs", "painCount": 3, "confirms": 2, "differs": 1, "guessed": False},
        "Cy": {"way": None, "wayMatch": None, "limitsHit": [], "ownLimits": ["approver away"], "pain": None,
               "painMatch": None, "painCount": None, "confirms": 0, "differs": 1, "guessed": False},
        "Di": {"way": None, "wayMatch": None, "limitsHit": [], "ownLimits": [], "pain": None, "painMatch": None,
               "painCount": None, "confirms": 0, "differs": 0, "guessed": True},
    }
    for person, change in changes.items():
        base[person] = {**base[person], **change}
    out = [{"person": p, "invitation": f"inv-{p.lower()}", "experience": e,
            "anchoring": "GUESSED" if e["guessed"] else "ANCHORED", "has_story": True, "experience_served": True}
           for p, e in base.items()]
    out.append({"person": "Eve", "invitation": "inv-eve", "experience": None, "anchoring": "GUESSED",
                "has_story": False, "experience_served": True})
    return out


def told_served(**changes) -> dict:
    """`BriefFacts.problem.told` as keel-cloud 281 serves it -- by default what the truth makes (3 tellers, 1 guess)."""
    told = {"tellers": 3, "guessed": 1, "verdict": "HALF_NEW",
            "way": {"yours": {"label": PAYROLL_STORY["act"], "count": 1, "band": "SOME"}, "theirs": [], "notSaid": 2},
            "limits": {"yours": [{"k": 0, "count": 1, "band": "SOME"}, {"k": 1, "count": 1, "band": "SOME"},
                                 {"k": 2, "count": 1, "band": "SOME"}],
                       "theirs": [{"label": "The approver was away", "count": 2,
                                   "words": ["the approver was away", "nobody to sign it off"]}]},
            "pain": {"yours": {"label": PAYROLL_STORY["cost"], "count": 1, "band": "SOME"},
                     "theirs": [{"label": "Paid people wrong", "count": 2, "words": ["paid wrong", "short paid"]}],
                     "notSaid": 1}}
    for path, value in changes.items():
        block, *rest = path.split(".")
        if rest and rest[0] == "limits":
            told["limits"]["yours"][int(rest[1])].update(value)
        elif rest:
            told[block][rest[0]].update(value)
        else:
            told[block] = value
    return told


CARD_TEXT = ("What they told you\nHalf new\n4 said yes · 3 told a time · 1 read as a guess and are set aside below\n"
             "1 · How they do it today\nchecking the run by hand against the timesheets mentioned by some\n"
             "2 · Where it falls short\nThe hours come from systems that don't agree mentioned by some\n"
             "Theirs, not on your board\nThe approver was away new\n3 · What it costs them\n"
             "A pay run they check twice and still fear mentioned by some\nCounted from what people told, not from a "
             "question")


def captured(*, told=None, people=None, drawn=True) -> dict:
    people = people or wire_people()
    out = {"spec": "171", "wire": {"told": told if told is not None else told_served(),
                                   "board": ftold.board_of(PAYROLL_STORY), "people": people},
           "card": ({"drawn": True, "switch": True, "text": CARD_TEXT, "items": []} if drawn else
                    {"drawn": False, "switch": False, "error": "no `insights-view-problem` switch"})}
    out["sampled"] = [{**pick, "drawn": {"drawn": True, "text": "A real occasion"}} for pick in ftold.sample(people)]
    return out


def truth_ask(label: str, prompt: str) -> dict:
    """The stubbed told-reader: the answer for the story the prompt carries, read as a real answer is."""
    person = next(p for p, s in STORIES.items() if s in prompt)
    return ftold.parse_truth(json.dumps(TRUTH_ANSWERS[person]), limits=3)


def film_record(**strangers) -> dict:
    return {"spec": "163", "entry": {"id": "fixture-film", "path": str(FIX_163 / "entry.yaml")}, "project_id": "p1",
            "strangers": {"walks": walks(), **strangers}}


@pytest.fixture
def truth(tmp_path) -> dict:
    return ftold.write_truth(tmp_path, film_record(), PAYROLL_STORY, ask=truth_ask,
                             template=fread.template(fread.TOLD_PROMPT_PATH, "truth"), bundle={})


def answer(placed=((1, [3, 2], None), (2, [2, 1], None)), t4=2, why="Reads in order, the bands say what they mean.",
           instead="") -> dict:
    raw = {"theirs": [{"row": r, "stories": s, "founders": f} for r, s, f in placed], "t4": t4, "why4": why,
           "instead4": instead}
    return ftold.parse_card_answer(json.dumps(raw), rows=len(placed))


# ----------------------------------------------------------------------------------------------- FR-1 the truth

def test_the_truth_file_from_a_fixture_walk(tmp_path, truth):
    written = json.loads((tmp_path / ftold.TRUTH_FILE).read_text())
    assert written == truth and written["spec"] == "171" and written["unread"] == []
    assert [s["person"] for s in written["stories"]] == ["Ada", "Ben", "Cy", "Di"]       # Eve tapped a chip
    by = {s["person"]: s for s in written["stories"]}
    assert by["Ada"]["limits"] == [0] and by["Ben"]["limits"] == [1, 2]                  # 1-based in, 0-based kept
    assert by["Cy"]["own"] == ["the approver was away"] and by["Di"]["occasion"] == "guess"
    assert written["board"] == {"way": PAYROLL_STORY["act"], "steps": PAYROLL_STORY["steps"],
                                "limits": PAYROLL_STORY["limits"], "pain": PAYROLL_STORY["cost"]}
    card = written["card"]
    assert card["tellers"] == 3 and card["guessed"] == 1                                  # a guess is in no row
    assert card["way"] == {"count": 1, "band": "SOME"} and card["pain"] == {"count": 1, "band": "SOME"}
    assert [(r["k"], r["count"], r["band"]) for r in card["limits"]] == [(0, 1, "SOME"), (1, 1, "SOME"), (2, 1, "SOME")]


def test_the_truth_prompt_carries_the_board_and_the_story_alone():
    prompt = ftold.truth_prompt(fread.template(fread.TOLD_PROMPT_PATH, "truth"), ftold.board_of(PAYROLL_STORY),
                                STORIES["Ben"])
    assert "1. The hours come from systems that don't agree" in prompt and STORIES["Ben"] in prompt
    assert PAYROLL_STORY["cost"] in prompt and "{{" not in prompt
    assert STORIES["Ada"] not in prompt                                                   # one story a call


@pytest.mark.parametrize("change, said", [({"limits": [4]}, "limitations 1 to 3"), ({"way": "maybe"}, "way must be"),
                                          ({"occasion": "sure"}, "occasion must be"), ({"why": ""}, "no why")])
def test_a_truth_answer_out_of_shape_is_refused(change, said):
    with pytest.raises(ftold.ToldError, match=said):
        ftold.parse_truth(json.dumps({**TRUTH_ANSWERS["Ada"], **change}), limits=3)


def test_the_stories_are_the_walks_said_words_else_the_bundles_plans():
    assert [s["person"] for s in ftold.stories_of(film_record())] == ["Ada", "Ben", "Cy", "Di"]
    old = {"strangers": {"walks": [{"person": "Ada", "invitation": "i1", "response": {"story": True}},
                                   {"person": "Eve", "invitation": "i2", "response": {"story": False}}]}}
    plans = [{"person": "Ada", "gate": True, "screener": "yes", "story_how": "said", "story": STORIES["Ada"]},
             {"person": "Eve", "gate": True, "screener": "yes", "story_how": "chip-tap", "story": "x"}]
    assert ftold.stories_of(old, {"plans": plans}) == [{"person": "Ada", "invitation": "i1", "story": STORIES["Ada"]}]


def test_the_walk_keeps_the_story_said_never_a_tap():
    plan = {"person": "Ada", "screener": "yes", "gate": True, "story_how": "said"}
    said = fs.walk_summary(plan, {"invitationId": "i1"}, {"rows": [{"screen": "question", "story": "said",
                                                                    "said": STORIES["Ada"]}]})
    assert said["story"] == STORIES["Ada"]
    tapped = fs.walk_summary(plan, {"invitationId": "i1"}, {"rows": [{"screen": "question", "story": "chip-tap",
                                                                      "said": "tap: I can't recall"}]})
    assert "story" not in tapped


def test_the_bands_and_the_verdict_are_keel_cloud_281s():
    assert [ftold.band(c, 4) for c in (0, 1, 2, 3)] == ["NONE", "SOME", "SOME", "MOST"]
    assert ftold.verdict_of(0, 0) is None and ftold.verdict_of(4, 1) == "MOSTLY_KNOWN"
    assert ftold.verdict_of(2, 2) == "HALF_NEW" and ftold.verdict_of(1, 3) == "MOSTLY_NEW"


# ----------------------------------------------------------------------------------------------- FR-2 the capture

def test_three_people_are_sampled_a_hit_a_new_row_a_guess():
    picked = ftold.sample(wire_people())
    assert [(p["person"], p["why"]) for p in picked] == [("Ada", "the first with a hit"),
                                                          ("Cy", "the first with a new row"), ("Di", "the first guess")]
    # one person with a hit and a new row is picked once; the next with a new row is not drawn twice
    both = wire_people(Ada={"ownLimits": ["late approvals"]}, Cy={"ownLimits": []})
    assert [p["person"] for p in ftold.sample(both)] == ["Ada", "Di"]
    plain = [{"person": "Zo", "invitation": "z", "experience": {"limitsHit": [], "ownLimits": [], "guessed": False}}]
    assert ftold.sample(plain)[0]["person"] == "Zo"


def test_the_capture_reads_the_wire_and_names_what_the_page_did_not_draw(tmp_path):
    people = {p["invitation"]: p for p in wire_people()}

    class Page:
        def __getattr__(self, name):
            raise RuntimeError(f"no page here ({name})")

    def get(path):
        if path.endswith("/story"):
            return PAYROLL_STORY
        inv = path.rsplit("/", 1)[1]
        p = people.get(inv) or {}
        return {"experience": p.get("experience"), "interview": {"anchoring": p.get("anchoring"), "story": "s"}}

    run = SimpleNamespace(get=get, page=Page(), recorder=None, web="http://web")
    got = ftold.capture(run, "p1", {"facts": {"problem": {"told": told_served()}}}, walks(), tmp_path)
    assert got["wire"]["told"]["tellers"] == 3 and got["wire"]["board"]["limits"] == PAYROLL_STORY["limits"]
    assert [p["person"] for p in got["wire"]["people"]] == ["Ada", "Ben", "Cy", "Di", "Eve"]
    assert got["card"]["drawn"] is False and got["card"]["error"]
    assert [s["person"] for s in got["sampled"]] == ["Ada", "Cy", "Di"]
    assert all(s["drawn"]["drawn"] is False for s in got["sampled"])
    # served but not drawn: the card is absent (a keel-web before 273), a DRIFT capture note
    assert ftold.absent(got, {"stories": [1]}) == {"why": ftold.absent(got, {"stories": [1]})["why"], "drift": True}
    # no told served: no screen is opened and nobody is sampled
    none = ftold.capture(run, "p1", {"facts": {"problem": {}}}, walks(), tmp_path)
    assert none["card"] == {"drawn": False, "skipped": "no told served"} and none["sampled"] == []


def test_the_capture_reads_nothing_it_could_write():
    source = (REPO / "harness" / "film_told.py").read_text()
    assert '"POST"' not in source and '"PUT"' not in source and "run.call(" not in source


# ----------------------------------------------------------------------------------------------- FR-3 T1-T4

def test_a_card_that_matches_scores_every_t_at_two(truth):
    told = ftold.score(captured(), truth, answer())
    assert told["scores"] == {"t1": 2, "t2": 2, "t3": 2, "t4": 2} and told["told_pct"] == 100.0
    assert not told["flagged"] and told["instead"] == {} and told["version"] == fr.TOLD_VERSION == 1
    assert all(told["whys"][c] for c in fr.T_CRITERIA)
    assert [p["person"] for p in told["people"]] == ["Ada", "Cy", "Di"] and all(p["off"] == 0 for p in told["people"])
    assert all(r["holds"] for r in told["rows"]) and len(told["rows"]) == 5              # the way, three, the pain
    assert told["verdict"]["keel"] == told["verdict"]["truth"] == "HALF_NEW" and told["verdict"]["holds"]   # 4 of 9 theirs
    assert ftold.drift_items(told) == []


def test_a_card_one_off_scores_one_on_each(truth):
    card = captured(told=told_served(**{"x.limits.2": {"count": 3, "band": "MOST"}}),
                    people=wire_people(Ada={"limitsHit": [0, 1]}))
    told = ftold.score(card, truth, answer(placed=((1, [3, 2], None), (2, [2], None)), t4=1,
                                         why="One band word is cut on the phone.",
                                         instead="Say *mentioned by some* in full."))
    assert told["scores"] == {"t1": 1, "t2": 1, "t3": 1, "t4": 1} and told["told_pct"] == 50.0
    assert "Ada" in told["whys"]["t1"] and "limitation 2" in told["whys"]["t1"]
    assert "limitation 3" in told["whys"]["t2"] and "1 of 3" in told["whys"]["t2"]
    assert "*Paid people wrong*" in told["whys"]["t3"] and set(told["instead"]) == {"t1", "t2", "t3", "t4"}
    assert not told["flagged"] and ftold.drift_items(told) == []                          # a 1 is not a DRIFT


def test_a_wrong_card_scores_zero_and_is_flagged(truth):
    card = captured(told=told_served(**{"x.limits.0": {"count": 3, "band": "MOST"},
                                        "x.limits.1": {"count": 3, "band": "MOST"}}),
                    people=wire_people(Ada={"limitsHit": [1, 2]}))
    told = ftold.score(card, truth, answer(placed=((1, [3], None), (2, [2, 1], "pain")), t4=0,
                                         why="The blocks are out of order.", instead="Way, then limitations, then pain."))
    assert told["scores"] == {"t1": 0, "t2": 0, "t3": 0, "t4": 0} and told["told_pct"] == 0.0 and told["flagged"]
    fr.validate_told(told)
    items = ftold.drift_items(told)
    t1 = [i for i in items if i["criterion"] == "T1"]
    t2 = [i for i in items if i["criterion"] == "T2"]
    assert len(t1) == 1 and "Ada" in t1[0]["what"]
    assert "the truth -- the story describes limitations 1" in t1[0]["detail"]
    assert "Keel's reading -- ticked 2, 3" in t1[0]["detail"]
    assert [i["what"] for i in t2] == ["the count of limitation 1 (The hours come from systems that don't agree) "
                                       "does not add up", "the count of limitation 2 (Nobody tells them when a rate "
                                                          "changes) does not add up"]
    assert "the truth -- 1 of 3 (SOME); Keel's reading -- 3 (MOST)" in t2[0]["detail"]


def test_a_card_answer_out_of_shape_is_refused():
    with pytest.raises(ftold.ToldError, match="not placed"):
        ftold.parse_card_answer(json.dumps({"theirs": [], "t4": 2, "why4": "fine"}), rows=1)
    with pytest.raises(ftold.ToldError, match="no instead"):
        ftold.parse_card_answer(json.dumps({"theirs": [], "t4": 1, "why4": "a slip"}), rows=0)
    with pytest.raises(ftold.ToldError):
        ftold.parse_card_answer(json.dumps({"theirs": [], "t4": 3, "why4": "x"}), rows=0)


def test_the_rubric_holds_the_four_and_the_card_prompt_carries_it(truth):
    assert [r["id"] for r in fr.criteria("told")] == list(fr.T_CRITERIA)
    names = [r["name"] for r in fr.criteria("told")]
    assert names == ["The ticks are right", "The counts add up", "Theirs are real", "Legible"]
    request = ftold.card_request(captured(), truth, persona="the persona",
                                 template=lambda part: fread.template(fread.TOLD_PROMPT_PATH, part),
                                 rubric=fr.prompt_told(), cfg=fread.load_film_reader())
    text = request["text"]
    assert fr.prompt_told() in text and "{{" not in text and STORIES["Cy"] in text
    assert "1. [limits] The approver was away -- 2 people" in text and "2. [pain] Paid people wrong" in text
    assert request["body"]["model"] == "claude-opus-5-5" and request["images"] == 0
    assert ftold.drawn_notes(captured()) == []
    shuffled = captured()
    shuffled["card"]["text"] = CARD_TEXT.replace("1 · How they do it today", "").replace(
        "Counted from", "") + "\nHow they do it today"
    notes = ftold.drawn_notes(shuffled)
    assert any("not in the founder's order" in n for n in notes) and any("foot line" in n for n in notes)


def test_told_pct_is_beside_founder_pct_never_in_film_pct(truth):
    told = ftold.score(captured(), truth, answer(t4=1, why="a slip", instead="b"))
    record = {"entry": "e", "bundle": "b", "cloud_sha": "c", "web_sha": "w", "film_rubric_version": 1, "reader": {},
              "founder_reader": None, "cost_usd": 0, "seconds": 0, "scored_at": "2026-11-25", "frames": {},
              "film": fr.film_score("problem", {c: 2 for c in fr.F_CRITERIA}, {c: "w" for c in fr.F_CRITERIA}, [], {}),
              "founder": None, "told": told}
    fr.validate_file(record)
    assert record["film"]["film_pct"] == 100.0 and told["told_pct"] == 87.5
    broken = copy.deepcopy(record)
    broken["told"]["told_pct"] = 100.0
    with pytest.raises(fr.FilmRubricError, match="told_pct"):
        fr.validate_file(broken)
    absent = copy.deepcopy(record)
    absent["told"] = ftold.absent_block({"why": "no told", "drift": True})
    fr.validate_file(absent)
    absent["told"]["told_pct"] = 50.0
    with pytest.raises(fr.FilmRubricError, match="scores nothing"):
        fr.validate_file(absent)


# ----------------------------------------------------------------------------------------------- the absent card

def test_an_absent_card_scores_nothing_and_drifts_only_where_a_story_was_told(truth):
    no_told = captured(told={})
    no_told["wire"]["told"] = None
    told = ftold.score(no_told, truth, answer())
    assert told["absent"].startswith("no `told`") and told["told_pct"] is None and told["scores"] is None
    assert ftold.drift_items(told) == [{"criterion": "capture", "what": "(capture): no told card",
                                        "owed": ftold.ABSENT_OWED, "detail": told["absent"]}]
    undrawn = ftold.score(captured(drawn=False), truth, answer())
    assert undrawn["absent"].startswith("the told card was not drawn") and undrawn["drift"]
    nobody = ftold.score(no_told, {**truth, "stories": []}, None)
    assert nobody["absent"].startswith("no story told") and ftold.drift_items(nobody) == []
    before = ftold.score(None, truth, None)
    assert before["absent"].startswith("the walk captured no told card") and not before["drift"]


# ----------------------------------------------------------------------------------------------- the table and DRIFT

def score_file(entry: str, told: dict | None, film_pct_zero: bool = False) -> dict:
    scores = {c: 2 for c in fr.F_CRITERIA}
    return {"entry": entry, "kind": "problem", "bundle": "w171", "cloud_sha": "2606b07a", "web_sha": "04773133",
            "film_rubric_version": 1, "reader": {}, "founder_reader": None, "cost_usd": 0.1, "seconds": 1,
            "scored_at": "2026-11-25T20:00:00+00:00", "frames": {"frames": [], "folder": "x"},
            "film": fr.film_score("problem", scores, {c: "w" for c in fr.F_CRITERIA}, [], {}),
            "founder": {"beats": [], "founder_pct": 75.0}, "told": told}


def test_the_table_gains_a_told_column_after_founder_pct(tmp_path, truth):
    good = ftold.score(captured(), truth, answer())
    wrong = ftold.score(captured(people=wire_people(Ada={"limitsHit": [1, 2]})), truth, answer())
    gone = ftold.absent_block({"why": "no `told` on the brief's facts (keel-cloud before 281)", "drift": True})
    scores = tmp_path / "scores"
    scores.mkdir()
    for entry, told in (("e1", good), ("e2", wrong), ("e3", gone), ("e4", None)):
        (scores / f"w171-film-{entry}.json").write_text(json.dumps(score_file(entry, told)))
    drift = tmp_path / "DRIFT.md"
    drift.write_text("# DRIFT\n\n## 130. Observation (an earlier one)\n\ntext\n")
    code = ft.main(["--run", "w171", "--scores-dir", str(scores), "--table", str(tmp_path / "T.md"),
                    "--cycles-dir", str(tmp_path / "cycles"), "--drift", "--drift-path", str(drift)])
    assert code == 0
    text = (tmp_path / "T.md").read_text()
    header = next(line for line in text.splitlines() if line.startswith("| rank |"))
    cells = [c.strip() for c in header.strip("|").split("|")]
    assert cells[cells.index("founder_pct") + 1] == "told"
    rule = next(line for line in text.splitlines() if line.startswith("|---|"))
    assert rule.count("|") == header.count("|")
    rows = {line.split("|")[2].strip(): [c.strip() for c in line.strip("|").split("|")]
            for line in text.splitlines() if line.startswith("| ") and "film alone" in line}
    at = cells.index("told")
    assert rows["e1 (problem film alone)"][at] == "100.0" and rows["e2 (problem film alone)"][at] == "75.0 (0)"
    assert rows["e3 (problem film alone)"][at] == "absent" and rows["e4 (problem film alone)"][at] == "--"
    assert "- the told card, told_pct 75.0:" in text and "  - T1 0:" in text
    assert "- the told card: absent -- no `told` on the brief's facts" in text
    appended = drift.read_text()
    assert "## 131. Observation (the film, e2): the ticks are wrong on Ada's popup" in appended
    assert "Ada: the truth -- the story describes limitations 1; Keel's reading -- ticked 2, 3" in appended
    assert "Observation (the film, e3): (capture): no told card" in appended
    assert "(`make read-film-table`, T1)" in appended and "(`make read-film-table`, capture)" in appended


def test_the_weak_rule_covers_t1_to_t4(truth):
    wrong = ftold.score(captured(people=wire_people(Ada={"limitsHit": [1, 2]})), truth, answer())
    files = [score_file("e1", wrong), score_file("e2", wrong), score_file("e3", None)]
    weak = {(w["kind"], w["criterion"]) for w in fr.weak_criteria(files)}
    assert ("told", "t1") in weak and ("told", "t2") not in weak
    assert all(k == "told" for k, _ in weak)


def test_the_comparison_moves_told(truth):
    good = ftold.score(captured(), truth, answer())
    wrong = ftold.score(captured(people=wire_people(Ada={"limitsHit": [1, 2]})), truth, answer())

    def table(told):
        f = {**score_file("e1", told), "_path": "x"}
        return ft.rows([f], {}, 80.0, [])
    cmp = ft.compare(table(good), table(wrong))
    assert cmp["moves"]["e1"]["told_pct"] == "75.0 -> 100.0 (+25.0)" and cmp["moves"]["e1"]["T1"] == "0 -> 2 (+2)"


# ----------------------------------------------------------------------------------------------- make read-films

class Answer:
    def __init__(self, body, status=200):
        self.body, self.status_code = body, status

    def json(self):
        return self.body


def told_walk(root: Path, strangers: dict) -> tuple[Path, Path]:
    walk = root / "20261125T200000Z-film-walk"
    folder = walk / "film" / "fixture-film"
    folder.mkdir(parents=True)
    (folder / "story.json").write_text(json.dumps(PAYROLL_STORY))
    film = {**film_record(), "frames": [], "pictures": [], "measures": {"faults": []}, "dollars": 0.0,
            "stack": {"keel-cloud": "2606b07a", "keel-web": "04773133"}}
    film["strangers"] = {**film["strangers"], **strangers}
    (folder / "film.json").write_text(json.dumps(film))
    return walk, folder


def stub_post(sent: list):
    film_answer = json.loads((FIX_163 / "api-answer.json").read_text())

    def post(url, json=None, timeout=None, headers=None):
        text = json["messages"][0]["content"][0]["text"]
        sent.append(text)
        if "The account (the person's own words" in text:
            person = next(p for p, s in STORIES.items() if s in text)
            said = __import__("json").dumps(TRUTH_ANSWERS[person])
        elif "What each stranger told, as the truth reads it" in text:
            said = __import__("json").dumps({"theirs": [{"row": 1, "stories": [3, 2], "founders": None},
                                                        {"row": 2, "stories": [2, 1], "founders": None}],
                                             "t4": 2, "why4": "Reads in the founder's order.", "instead4": ""})
        else:
            return Answer(film_answer)
        return Answer({"content": [{"type": "text", "text": said}], "model": "claude-opus-5-5",
                       "usage": {"input_tokens": 1000, "output_tokens": 100}})
    return post


def test_read_films_writes_the_truth_then_scores_the_card(tmp_path):
    walk, folder = told_walk(tmp_path, {"told": captured()})
    sent = []
    code = fread.run(["--run", str(walk), "--out", str(tmp_path / "out"), "--scores-dir", str(tmp_path / "scores"),
                      "--no-founder"], post=stub_post(sent), env={"KEEL_ANTHROPIC_API_KEY": "test-key-not-real"})
    assert code == 0 and len(sent) == 1 + 4 + 1                    # the film, a call a story, the card
    truth = json.loads((folder / ftold.TRUTH_FILE).read_text())
    assert truth["card"]["tellers"] == 3 and truth["reader"]["model"] == "claude-opus-5-5"
    record = fr.validate_file(json.loads(fread.score_path(tmp_path / "scores", walk.name, "fixture-film").read_text()))
    assert record["told"]["told_pct"] == 100.0 and record["film"]["film_pct"] == 87.5
    assert record["told_cost_usd"] == round(5 * (1000 * 4 + 100 * 20) / 1e6, 4)
    assert record["cost_usd"] >= record["told_cost_usd"]
    # the truth is written once: a second read reuses it (one film call and the card's)
    sent.clear()
    fread.run(["--run", str(walk), "--out", str(tmp_path / "out2"), "--scores-dir", str(tmp_path / "scores"),
               "--no-founder"], post=stub_post(sent), env={"KEEL_ANTHROPIC_API_KEY": "test-key-not-real"})
    assert len(sent) == 2


def test_an_absent_card_spends_nothing_and_told_0_skips_it(tmp_path):
    no_told = captured()
    no_told["wire"]["told"] = None
    walk, folder = told_walk(tmp_path, {"told": no_told})
    sent = []
    fread.run(["--run", str(walk), "--out", str(tmp_path / "out"), "--scores-dir", str(tmp_path / "scores"),
               "--no-founder"], post=stub_post(sent), env={"KEEL_ANTHROPIC_API_KEY": "k"})
    record = json.loads(fread.score_path(tmp_path / "scores", walk.name, "fixture-film").read_text())
    assert len(sent) == 1 and record["told"]["absent"] and record["told"]["drift"]
    assert not (folder / ftold.TRUTH_FILE).exists()
    fread.run(["--run", str(walk), "--out", str(tmp_path / "out2"), "--scores-dir", str(tmp_path / "scores"),
               "--no-founder", "--no-told"], post=stub_post(sent), env={"KEEL_ANTHROPIC_API_KEY": "k"})
    assert json.loads(fread.score_path(tmp_path / "scores", walk.name, "fixture-film").read_text())["told"] is None


def test_a_dry_read_writes_the_truths_prompts_and_calls_nothing(tmp_path):
    walk, folder = told_walk(tmp_path, {"told": captured()})

    def post(*a, **k):
        raise AssertionError("a dry run calls nothing")
    code = fread.run(["--run", str(walk), "--dry-run", "--out", str(tmp_path / "out"), "--no-founder",
                      "--scores-dir", str(tmp_path / "scores")], post=post, env={})
    prompts = sorted((tmp_path / "out" / "film-fixture-film-told").glob("told-truth-*.prompt.txt"))
    assert code == 0 and len(prompts) == 4 and STORIES["Ada"] in prompts[0].read_text()
    assert not (folder / ftold.TRUTH_FILE).exists() and not (tmp_path / "scores").exists()


def test_read_films_says_told_0():
    makefile = (REPO / "Makefile").read_text()
    read = makefile.split("\nread-films: venv\n", 1)[1].split("\n\n", 1)[0]
    assert "$(if $(filter 0 off,$(TOLD)),--no-told,)" in read
