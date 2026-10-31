"""Spec 109: after everyone has answered, the walk shoots the stage page, each dimension card and the Insights screen,
and the founder-reader judges them on §B (RUBRIC_VERSION 3) -- with no model, no stack and no network.

The walk is held against `FakePage`, a stand-in for the founder's page that answers the back-test camera's reads
(`STAGE_JS`, `CARD_JS`, `INSIGHTS_JS`, `FOLD_JS`) and the leg's clicks as keel-web's stage page and Insights tab
would: one PROBLEM stage page with three cards (Frequency left out, so it does not open) and an Insights screen with one
fold. What the leg records is the committed fixture `tests/fixtures/quality/after-screens.json` (held equal here), which
the readers' tests then read as the bundle's `after_screens`: the walk and the reader meet on one file.
"""

from __future__ import annotations

import copy
import json
import re
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from evals import backtest as bt
from quality import cycle, decisions as dec, readers, rubric, table
from tests.test_quality_078 import BUNDLE, ENTRIES, GUIDE, FakeCli, SCREEN_ANSWER

REPO = Path(__file__).resolve().parent.parent
AFTER = Path(__file__).parent / "fixtures" / "quality" / "after-screens.json"
BASE = "http://localhost:5173"
PID = "p-109"

# ------------------------------------------------------------------------------------- the founder's page, faked

PREVALENCE = "Most night porters had a guest arrive after midnight in the last 7 days."
IMPORTANCE = "For most night porters, a late arrival is among the two things that matter most on a shift."
STAGE_TEXT = ("Problem · 7 people answered\nProblem\nThe problem holds on 1 of 2.\nNight porters at small hotels are "
              "alone at the desk when guests arrive after midnight.\n1 held · 1 did not hold · 1 of 2 holding · 7 people "
              "answered\n1. Prevalence " + PREVALENCE + " Held 6 of 7 had one\n2. Importance " + IMPORTANCE +
              " Did not hold 3 of 7 put it in their two\n3. Frequency Left out")
PAGE = {"kicker": "Problem · 7 people answered", "title": "Problem", "headline": "The problem holds on 1 of 2.",
        "statement": "Night porters at small hotels are alone at the desk when guests arrive after midnight.",
        "foot": "1 held · 1 did not hold · 1 of 2 holding · 7 people answered", "decider": "", "measures": "",
        "rows": [{"dimension": "problem.prevalence", "n": "1.", "name": "Prevalence", "belief": PREVALENCE,
                  "status": "Held 6 of 7 had one", "opens": True, "open": False},
                 {"dimension": "problem.importance", "n": "2.", "name": "Importance", "belief": IMPORTANCE,
                  "status": "Did not hold 3 of 7 put it in their two", "opens": True, "open": False},
                 {"dimension": "problem.frequency", "n": "3.", "name": "Frequency", "belief": "",
                  "status": "Left out", "opens": False, "open": False}]}
CARDS = {
    "problem.prevalence": {
        "chart": {"title": "Prevalence", "belief": PREVALENCE, "verdict": "Held 6 of 7 had one", "insight": "",
                  "count": "6 of 7 had one", "asked": "Asked: \"In the last 7 days, did a guest arrive after "
                  "midnight?\" — the last 7 days", "bar": "You said 8 or more in 10", "chart": "prevalence",
                  "caption": "6 of 7 people", "legend": "One person", "line": "",
                  "drawing": "6 of 7 people One person",
                  "people": [{"name": "Ada Lindqvist", "read": "Yes, on Saturday"},
                             {"name": "Ben Okoro", "read": "Yes, twice"}]},
        "open": True,
        "text": "1. Prevalence " + PREVALENCE + " Held 6 of 7 had one The drawing Everyone who answered Asked: ..."},
    "problem.importance": {
        "chart": {"title": "Importance", "belief": IMPORTANCE, "verdict": "Did not hold 3 of 7 put it in their two",
                  "insight": "", "count": "3 of 7 put it in their two", "asked": "", "bar": "", "chart": "bars",
                  "caption": "", "legend": "", "line": "",
                  "drawing": "A late arrival 3 Noise 4 Check-out 0",
                  "people": [{"name": "Ada Lindqvist", "read": "Noise came first"}]},
        "open": True,
        "text": "2. Importance " + IMPORTANCE + " Did not hold 3 of 7 put it in their two A late arrival 3 Noise 4"},
}
INSIGHTS_FOLDED = {
    "insights": {"boxes": [{"dimension": "problem.importance", "status": "PEOPLE_DISAGREE", "state": "GROUPED",
                            "head": "Importance Did not hold", "concern": "Why other things come first",
                            "themes": [{"label": "Noise at night", "count": "7"}], "quotes": 6, "folds": 1}],
                 "empty": None, "not_asked": ["Frequency was not asked: its window does not fit the study."],
                 "opens": 0, "folds": 1},
    "text": "Importance Did not hold\nWhy other things come first\nNoise at night (7)\n... and 1 more"}
INSIGHTS_OPEN = copy.deepcopy(INSIGHTS_FOLDED)
INSIGHTS_OPEN["insights"]["boxes"][0].update(quotes=7, folds=0)
INSIGHTS_OPEN["insights"]["folds"] = 0
INSIGHTS_OPEN["text"] = ("Importance Did not hold\nWhy other things come first\nNoise at night (7)\n“Noise complaints eat "
                         "my night.” — Ada Lindqvist\n“Drunk guests in the corridor.” — Ben Okoro")


class FakePage:
    """The founder's page as keel-web draws it, for the leg alone: `goto`, `wait_for_selector`, `evaluate` (each of the
    leg's reads, by its script), `click` and `screenshot` (a file written, as Playwright's)."""

    def __init__(self, *, stage_page=True, hash_view=True):
        self.url, self.open_row, self.view, self.folded = "about:blank", None, None, 1
        self.stage_page, self.hash_view = stage_page, hash_view
        self.seen: list = []

    def goto(self, url, wait_until=None):
        self.seen.append(("goto", url))
        self.url, self.open_row = url, None
        self.view = "insights" if url.endswith("#insights") and self.hash_view else None

    def _on_stage(self):
        return self.stage_page and re.search(r"/s/[A-Z]+$", self.url)

    def wait_for_selector(self, selector, state=None, timeout=None):
        self.seen.append(("wait", selector))
        if selector == bt.STAGE_ROW and self._on_stage():
            return
        if selector == bt.INSIGHTS_VIEW and self.view == "insights":
            return
        body = re.fullmatch(r"\.dimrow\[id='(.+)'\] \.dimrow__body", selector)
        if body and body.group(1) == self.open_row:
            return
        raise TimeoutError(f"no {selector} on {self.url}")

    def evaluate(self, script, arg=None):
        if script == "document.fonts.ready":
            return None
        if script == bt.STAGE_JS:
            return {"page": copy.deepcopy(PAGE), "text": STAGE_TEXT}
        if script == bt.CARD_JS:
            return copy.deepcopy(CARDS[arg]) if arg == self.open_row else {"chart": None, "text": ""}
        if script == bt.INSIGHTS_JS:
            return copy.deepcopy(INSIGHTS_FOLDED if self.folded else INSIGHTS_OPEN)
        if script == bt.FOLD_JS:
            return "problem.importance" if self.folded else None
        if script.startswith("(sel) => !!document.querySelector"):
            return False
        raise AssertionError(f"an unknown read: {script[:60]!r}")

    def click(self, selector):
        self.seen.append(("click", selector))
        head = re.fullmatch(r"\.dimrow\[id='(.+)'\] button\.dimrow__head", selector)
        if head:
            self.open_row = head.group(1)
        elif selector == bt.FOLD_BUTTON:
            self.folded = 0
        elif selector == bt.INSIGHTS_TAB:
            self.view = "insights"
        else:
            raise AssertionError(f"an unknown click: {selector}")

    def screenshot(self, path, full_page=False):
        Path(path).write_bytes(b"\x89PNG fake")


def journey(page):
    return SimpleNamespace(page=page, web_base=BASE + "/", project_id=PID, recorder=None,
                           entry=SimpleNamespace(scope="PROBLEM"))


def walk(tmp_path, **page_kw):
    page = FakePage(**page_kw)
    cam = bt.Camera(run_dir=tmp_path, page=page, watched={})
    done = bt.answers_leg(journey(page), cam, stages=["PROBLEM"], pass_sheet=lambda j: None, timeout_s=0.01)
    return page, cam, done


def fixture() -> dict:
    return json.loads(AFTER.read_text(encoding="utf-8"))


def write_the_fixture(tmp_path) -> dict:
    """What the committed fixture is: the leg's record over `FakePage`, beside one check screen of the founder's flow
    (`python -c` it to rebuild after a change to the leg's record)."""
    _, cam, _ = walk(tmp_path)
    check = {"n": 4, "screen": "check-problem.prevalence", "kicker": "STEP 2 OF 5 · THE PROBLEM · CHECK", "question": "",
             "hint": "", "options": [], "rows": [], "chips": [], "answer": "saved as Keel drafted it",
             "keel read back": {"belief": PREVALENCE, "belief line on screen": PREVALENCE,
                                "keel will test": "Most night porters had a guest arrive after midnight",
                                "bar": "8 or more in 10"}}
    return {"check_screen": check, "after_screens": bt.after_screens(cam)}


# ------------------------------------------------------------------------------------------ FR-1 the answers leg

def test_the_leg_shoots_the_stage_page_each_card_that_opens_and_the_insights_screen_with_its_fold(tmp_path):
    page, cam, done = walk(tmp_path)
    names = [Path(s["file"]).name for s in cam.after_shots]
    assert names == ["founder-after-01-stage.png", "founder-after-02-dimension-problem.prevalence.png",
                     "founder-after-03-dimension-problem.importance.png", "founder-after-04-insights.png",
                     "founder-after-05-insights-more-problem.importance.png"]
    assert all((tmp_path / bt.SCREENS_DIR / n).is_file() for n in names), "every shot is a file in screens/"
    assert [s["kind"] for s in cam.after_shots] == ["stage", "dimension", "dimension", "insights-screen", "fold"]
    assert done == {"stages": ["PROBLEM"], "folds": ["problem.importance"], "errors": [],
                    "not_opened": [{"stage": "PROBLEM", "dimension": "problem.frequency",
                                    "why": "the card does not open (keel-web: a LEFT_OUT row has no body)"}]}
    gone = [u for k, u in page.seen if k == "goto"]
    assert gone == [f"{BASE}/p/{PID}/s/PROBLEM", f"{BASE}/p/{PID}#insights"], "the stage page, then the Insights"
    clicks = [u for k, u in page.seen if k == "click"]
    assert clicks == [bt.card_selector("problem.prevalence", "button.dimrow__head"),
                      bt.card_selector("problem.importance", "button.dimrow__head"), bt.FOLD_BUTTON]
    assert not any("pilot" in u.lower() or "people" in u.lower() for u in gone + clicks), "FR-1(c): nothing else"


def test_every_shot_carries_its_words_and_a_card_the_charts_own(tmp_path):
    _, cam, _ = walk(tmp_path)
    stage, prevalence = cam.after_shots[0], cam.after_shots[1]
    assert stage["page"]["headline"] == "The problem holds on 1 of 2." and stage["text"] == STAGE_TEXT
    assert stage["url"] == f"{BASE}/p/{PID}/s/PROBLEM" and stage["stage"] == "PROBLEM"
    chart = prevalence["chart"]
    assert (chart["title"], chart["verdict"], chart["count"], chart["bar"]) == (
        "Prevalence", "Held 6 of 7 had one", "6 of 7 had one", "You said 8 or more in 10"), "title, verdict, n, bar"
    assert prevalence["dimension"] == "problem.prevalence" and prevalence["text"].startswith("1. Prevalence")


def test_the_record_is_the_committed_fixture_and_nests_the_fold_under_the_insights_screen(tmp_path):
    built = write_the_fixture(tmp_path)
    assert built == fixture(), "the committed fixture is what the leg records over FakePage"
    screens = built["after_screens"]
    assert [s["kind"] for s in screens] == ["stage", "dimension", "dimension", "insights-screen"]
    insights = screens[-1]
    assert insights["folds"] == [{"n": 5, "file": "screens/founder-after-05-insights-more-problem.importance.png",
                                  "line": "problem.importance"}]
    assert insights["insights"]["folds"] == 0 and "Drunk guests" in insights["text"], "read with every fold open"


def test_the_hash_alone_not_opening_the_view_presses_the_tab(tmp_path):
    page, cam, done = walk(tmp_path, hash_view=False)
    assert ("click", bt.INSIGHTS_TAB) in page.seen and not done["errors"]
    assert cam.after_shots[3]["kind"] == "insights-screen"


def test_the_leg_never_fails_the_walk_a_stage_page_that_does_not_draw_is_an_error_recorded(tmp_path):
    _, cam, done = walk(tmp_path, stage_page=False)
    assert done["stages"] == [] and done["errors"][0]["stage"] == "PROBLEM"
    assert done["errors"][0]["at"] == "the stage page"
    assert [s["kind"] for s in cam.after_shots] == ["insights-screen", "fold"], "the Insights screen is still read"


def test_the_stages_are_the_studys_scope_in_the_ships_order():
    """Money alone has one stage page, each study of the three-study cycle its own, the whole study three."""
    for scope, want in (("PROBLEM", ["PROBLEM"]), ("SOLUTION", ["SOLUTION"]), ("COMMERCIAL", ["COMMERCIAL"]),
                        ("SOLUTION_COMMERCIAL", ["SOLUTION", "COMMERCIAL"]),
                        ("ALL", ["PROBLEM", "SOLUTION", "COMMERCIAL"])):
        assert bt._after_stages(SimpleNamespace(entry=SimpleNamespace(scope=scope))) == want, scope


def test_the_export_step_runs_the_leg_after_the_themes_settle(monkeypatch, tmp_path):
    from evals import sample_export                                # noqa: PLC0415
    order = []
    monkeypatch.setattr(bt, "themes_settle", lambda j: order.append("themes") or {"open": []})
    monkeypatch.setattr(bt, "answers_leg", lambda j, cam: order.append("leg") or {"stages": ["PROBLEM"]})

    def refuse(*a, **k):
        order.append("export")
        raise sample_export.SampleRefused(["x"])
    monkeypatch.setattr(sample_export, "export_sample", refuse)
    run = bt.Backtest(run_dir=tmp_path, stack=None)
    run.cam = bt.Camera(run_dir=tmp_path, page=FakePage(), watched={})
    run.after(SimpleNamespace())
    assert order == ["themes", "leg", "export"] and run.answers == {"stages": ["PROBLEM"]}


def test_the_markdown_lists_the_screens_after_the_answers():
    record = {"run": "r", "passed": True, "entry": {"id": "99-fixture"}, "brief": {}, "cost": {},
              "screenshots": {"founder": 3, "after": 5}, "after_screens": fixture()["after_screens"],
              "answers_leg": {"not_opened": [{"dimension": "problem.frequency", "why": "the card does not open"}]}}
    md = bt.markdown(record)
    section = md.split("### After the answers", 1)[1].split("## 2.", 1)[0]
    assert "`screens/founder-after-01-stage.png`" in section and "dimension · PROBLEM · problem.prevalence" in section
    assert "Held 6 of 7 had one" in section and "founder-after-05-insights-more-problem.importance.png" in section
    assert "not opened: problem.frequency" in section and "5 after the answers" in md


# ------------------------------------------------------------------------------------ FR-2 the rubric, version 3

def test_the_rubric_is_at_version_3_and_says_what_changed_and_why():
    assert rubric.RUBRIC_VERSION == 3 == rubric.file_version()
    assert 2 not in rubric.RETIRED, "version 2 is set aside, never refused (cycles 1-3 stay of record)"
    three = rubric.rubric_text().split("## Versions", 1)[1].split("- **2**", 1)[0]
    assert "- **3** (spec 109" in three and "§B, after the answers" in three
    assert "never compared and never refused" in three and "cycle 4 is the first at 3" in three


def test_section_b_carries_the_specs_six_criteria_word_for_word():
    spec = (REPO / "specs" / "109-the-reader-judges-the-stage-page-and-insights" / "spec.md").read_text("utf-8")
    rows = rubric.b_criteria()
    assert [r["id"] for r in rows] == list(rubric.B_CRITERIA)
    assert [r["name"] for r in rows] == ["I know the answer and why", "The chart reads at a glance",
                                         "It is about my belief, in my words", "I know what to do next",
                                         "Nothing misleads", "Teaches me something I did not type"]
    for row in rows[:5]:                                   # the spec's table, anchors and all
        assert f"| {row['id'].upper()} | {row['question']} | {row['2']} | {row['1']} | {row['0']} |" in spec, row["id"]
    assert (rows[5]["2"], rows[5]["1"], rows[5]["0"]) == ("they add to what I wrote", "they restate it", "noise")
    assert rubric.B_OF_KIND == {"stage": ("b1", "b2", "b3", "b4", "b5"), "dimension": ("b1", "b2", "b3", "b4", "b5"),
                                "insights-screen": ("b1", "b3", "b4", "b5", "b6")}
    part = rubric.prompt_after()
    assert "weak" not in part.lower() and "score_pct" not in part, "the reader scores; code judges weak"
    assert "| R1 |" not in part and "| B6 |" in part and "`instead`" in part


B_STAGE = {"b1": 2, "why_b1": "the verdict and its 6 of 7", "b2": 1, "why_b2": "the n needs a second look",
           "b3": 2, "why_b3": "my belief", "b4": 1, "why_b4": "a generic line", "b5": 2, "why_b5": "n is there",
           "instead": ""}
B_INSIGHTS = {"b1": 2, "why_b1": "said", "b3": 2, "why_b3": "mine", "b4": 2, "why_b4": "concrete", "b5": 2,
              "why_b5": "nothing beyond", "b6": 1, "why_b6": "restates noise", "instead": "Say what to change"}


def test_a_section_b_answer_is_read_by_its_kind_and_the_wrong_criterion_refused():
    stage = rubric.parse_after(json.dumps(B_STAGE), kind="stage")
    assert stage["b6"] is None and stage["b2"] == 1
    insights = rubric.parse_after(json.dumps(B_INSIGHTS), kind="insights-screen")
    assert insights["b2"] is None and insights["b6"] == 1 and insights["instead"] == "Say what to change"
    with pytest.raises(rubric.RubricError, match="b2 on a insights-screen screen"):
        rubric.parse_after(json.dumps({**B_INSIGHTS, "b2": 2}), kind="insights-screen")
    with pytest.raises(rubric.RubricError, match="b6 on a dimension screen"):
        rubric.parse_after(json.dumps({**B_STAGE, "b6": 2}), kind="dimension")
    with pytest.raises(rubric.RubricError, match="b1 must be 0, 1 or 2"):
        rubric.parse_after(json.dumps({**B_STAGE, "b1": None}), kind="stage")
    with pytest.raises(rubric.RubricError, match="not read after the answers"):
        rubric.parse_after(json.dumps(B_STAGE), kind="q")


def test_the_booleans_on_a_section_b_screen_are_codes():
    meta = {"n": 1, "screen": "stage", "audience": "founder", "link": None, "dimension": None, "kind": "stage"}
    score = rubric.screen_score(meta, rubric.parse_after(json.dumps({**B_STAGE, "b1": 0}), kind="stage"))
    assert list(score) == list(rubric.AFTER_SCORE_KEYS) and "r1" not in score
    assert score["out_of_place"] and not score["looks_stupid"], "B1 0 -> out of place"
    for crit in ("b2", "b5"):
        score = rubric.screen_score(meta, rubric.parse_after(json.dumps({**B_STAGE, crit: 0}), kind="stage"))
        assert score["looks_stupid"] and not score["out_of_place"], f"{crit} 0 -> looks stupid"
    assert rubric.flagged(score)


def test_section_b_folds_into_the_founders_score_pct_never_the_respondents():
    meta = {"n": 1, "screen": "stage", "audience": "founder", "link": None, "dimension": None, "kind": "stage"}
    after = rubric.screen_score(meta, rubric.parse_after(json.dumps(B_STAGE), kind="stage"))      # 8 of 10
    flow = {"audience": "founder", "r1": 2, "r2": 2, "r3": 2, "r4": None, "r5": 2, "r6": None}  # 8 of 8
    stranger = {"audience": "respondent", "r1": 2, "r2": 2, "r3": 2, "r4": 2, "r5": 2, "r6": 2}
    sums = rubric.summaries([flow, after, stranger])
    assert sums["founder"]["score_pct"] == round(100 * 16 / 18, 1) and sums["founder"]["after_pct"] == 80.0
    assert sums["respondent"]["score_pct"] == 100.0 and sums["respondent"]["after_pct"] is None
    assert sums["overall"]["score_pct"] == round(100 * 28 / 30, 1)
    assert sums["founder"]["means"]["b2"] == 1.0 and sums["founder"]["means"]["b6"] is None


# --------------------------------------------------------------------------------- FR-2 the founder-reader's prompt

def _bundle(tmp_path) -> Path:
    """The 078 fixture bundle with spec 109's screens merged in (and the check screen of the flow they quote)."""
    run = tmp_path / "bundle"
    shutil.copytree(BUNDLE, run)
    data = json.loads((run / "backtest.json").read_text(encoding="utf-8"))
    extra = fixture()
    data["founder_screens"] = data["founder_screens"] + [extra["check_screen"]]
    data["after_screens"] = extra["after_screens"]
    (run / "backtest.json").write_text(json.dumps(data), encoding="utf-8")
    return run


def _work(tmp_path, **over):
    _, bundle = readers.load_bundle(_bundle(tmp_path))
    entry = readers.load_entry(bundle, ENTRIES)
    return bundle, entry, readers.plan(bundle, entry, guidelines=GUIDE, **over)


def test_the_bundles_after_screens_are_founder_screens_of_the_three_kinds(tmp_path):
    _, bundle = readers.load_bundle(_bundle(tmp_path))
    after = readers.after_screens(bundle)
    assert [(s.kind, s.dimension, s.label()) for s in after] == [
        ("stage", None, "founder-after-01-stage"),
        ("dimension", "problem.prevalence", "founder-after-02-dimension-problem.prevalence"),
        ("dimension", "problem.importance", "founder-after-03-dimension-problem.importance"),
        ("insights-screen", None, "founder-after-04-insights")]
    assert all(s.audience == "founder" and s.after and not s.has_options for s in after)
    stage, card, insights = after[0].full, after[1].full, after[3].full
    assert "the problem stage page" in stage and "The verdict line under the title: The problem holds on 1 of 2." in stage
    assert "  - 3. Frequency -- Left out (does not open)" in stage
    assert "The verdict (the status word, its line and the count under it): Held 6 of 7 had one" in card
    assert "The bar line: You said 8 or more in 10" in card and "Ada Lindqvist -- Yes, on Saturday" in card
    assert "every fold opened" in insights and "groups: Noise at night (7)" in insights and "Drunk guests" in insights


def test_the_founder_reader_is_sent_section_b_the_beliefs_and_the_screens_before(tmp_path):
    _, entry, work = _work(tmp_path)
    after = [(s, p) for s, p in work["screens"] if s.after]
    assert len(after) == 4 and work["after"] == 4
    for screen, prompt in after:
        assert rubric.prompt_after() in prompt and "{{" not in prompt
        assert rubric.prompt_rubric() not in prompt, "§B, never the R criteria"
        assert prompt.startswith("## Who you are -- read this before the screen") and entry["sources"].strip() in prompt
        beliefs = prompt.split("## The beliefs you checked on the way in", 1)[1].split("##", 1)[0]
        assert f"problem.prevalence (STEP 2 OF 5 · THE PROBLEM · CHECK): {PREVALENCE}" in beliefs
        assert "your bar: 8 or more in 10" in beliefs
    card = after[1][1]
    earlier = card.split("## The screens you have already read after the answers, in order", 1)[1].split("##", 1)[0]
    assert "1. [the problem stage page] The problem holds on 1 of 2." in earlier
    assert '"b5": 0|1|2' in card and '"b6"' not in card.split("## Your answer", 1)[1]
    insights = after[3][1]
    shape = insights.split("## Your answer", 1)[1]
    assert '"b6": 0|1|2' in shape and '"b2"' not in shape and "do not score whether each answer sits" in insights


def test_a_limit_counts_the_after_screens_as_the_founders(tmp_path):
    _, _, work = _work(tmp_path, only="problem.importance")
    picked = [s.label() for s, _ in work["screens"] if s.audience == "founder"]
    assert picked == ["founder-after-03-dimension-problem.importance"]


class AfterCli(FakeCli):
    """078's fake CLI, answering §B on a screen after the answers."""

    def __call__(self, argv, *, input, capture_output, text, timeout, env, cwd):    # noqa: A002
        if "## The beliefs you checked on the way in" in input:
            self.seen.append({"argv": argv, "input": input})
            answer = B_INSIGHTS if "the Insights screen" in input.split("## The rubric", 1)[0] else B_STAGE
            body = {"type": "result", "is_error": False, "result": json.dumps(answer), "total_cost_usd": 0.01}
            return SimpleNamespace(stdout=json.dumps(body) + "\n", stderr="", returncode=0)
        return super().__call__(argv, input=input, capture_output=capture_output, text=text, timeout=timeout,
                                env=env, cwd=cwd)


@pytest.fixture
def wired_after(monkeypatch, tmp_path):
    monkeypatch.setattr(readers, "entries_dir", lambda: ENTRIES)
    cli = AfterCli()
    monkeypatch.setattr(readers.Reader, "available", lambda self: True)
    original = readers.Reader.__init__

    def init(self, config, run_dir, runner=None, calls=None, _cache=None):
        original(self, config, run_dir, runner=cli)
    monkeypatch.setattr(readers.Reader, "__init__", init)
    monkeypatch.setattr(readers, "routing_version", lambda run_dir: "13")
    monkeypatch.setattr(readers, "spoken_guidelines", lambda bundle, cloud=None: GUIDE)
    return SimpleNamespace(cli=cli, scores=tmp_path / "scores", out=tmp_path / "run", bundle=_bundle(tmp_path))


def test_a_run_scores_the_after_screens_on_section_b_and_folds_them_into_the_founders(wired_after):
    w = wired_after
    assert readers.run(["--run", str(w.bundle), "--out", str(w.out), "--scores-dir", str(w.scores)]) == 0
    path = next(w.scores.glob("99-fixture/*.json"))
    assert re.fullmatch(r"\d{8}-PROBLEM-r3-abcdef1-v13-claude-opus-5-5\.json", path.name)
    obj = rubric.load_file(path)
    after = [s for s in obj["screens"] if rubric.is_after(s["kind"])]
    assert [(s["kind"], s["dimension"]) for s in after] == [("stage", None), ("dimension", "problem.prevalence"),
                                                            ("dimension", "problem.importance"),
                                                            ("insights-screen", None)]
    assert all(s["audience"] == "founder" and "r1" not in s for s in after)
    assert after[3]["b2"] is None and after[3]["b6"] == 1 and after[0]["b6"] is None
    founder = [s for s in obj["screens"] if s["audience"] == "founder"]
    assert obj["summary"]["founder"] == rubric.summary(founder)
    assert obj["summary"]["founder"]["after_pct"] == round(100 * (8 * 3 + 9) / (2 * 20), 1)
    assert obj["after_note"] is None and not obj["unread"]
    calls = sorted((w.out / "calls").glob("*founder-after-*.prompt.txt"))
    assert [c.name.split("-", 1)[1] for c in calls] == [
        "founder-after-01-stage.prompt.txt", "founder-after-02-dimension-problem.prevalence.prompt.txt",
        "founder-after-03-dimension-problem.importance.prompt.txt", "founder-after-04-insights.prompt.txt"]


def test_a_bundle_walked_before_109_says_so_and_is_not_penalised(wired_after):
    w = wired_after
    assert readers.run(["--run", str(BUNDLE), "--out", str(w.out), "--scores-dir", str(w.scores)]) == 0
    obj = rubric.load_file(next(w.scores.glob("99-fixture/*.json")))
    assert obj["after_note"].startswith("no screen after the answers in the bundle")
    assert obj["summary"]["founder"]["after_pct"] is None


def test_a_version_3_file_with_a_section_b_screen_out_of_shape_is_refused():
    obj = json.loads(next((REPO / "tests" / "fixtures" / "quality" / "scores").glob("aa-alpha/*-r3-*.json")).read_text())
    meta = {"n": 1, "screen": "insights", "audience": "founder", "link": None, "dimension": None,
            "kind": "insights-screen"}
    good = rubric.screen_score(meta, rubric.parse_after(json.dumps(B_INSIGHTS), kind="insights-screen"))
    rubric.validate_file({**obj, "screens": obj["screens"] + [good]})
    with pytest.raises(rubric.RubricError, match="carries b2, which it is not scored on"):
        rubric.validate_file({**obj, "screens": obj["screens"] + [{**good, "b2": 2}]})
    with pytest.raises(rubric.RubricError, match="the founder-reader reads the screens after the answers"):
        rubric.validate_file({**obj, "screens": obj["screens"] + [{**good, "audience": "respondent"}]})


# ------------------------------------------------------------------------------- FR-3 the table and the record

def _with_after(src: Path, entry: str, b: dict, kinds=(("stage", None), ("dimension", "problem.prevalence"))) -> dict:
    obj = json.loads(src.read_text())
    obj["entry"] = entry
    for n, (kind, dim) in enumerate(kinds, 1):
        meta = {"n": n, "screen": kind, "audience": "founder", "link": None, "dimension": dim, "kind": kind}
        answer = {k: v for k, v in b.items() if k not in ("b6", "why_b6")} if kind != "insights-screen" else b
        obj["screens"].append(rubric.screen_score(meta, rubric.parse_after(json.dumps(answer), kind=kind)))
    obj["summary"] = rubric.summaries(obj["screens"], obj.get("insights") or [])
    return obj


def _scores(tmp_path, b_alpha: dict, b_beta: dict) -> Path:
    root = tmp_path / "scores"
    fx = REPO / "tests" / "fixtures" / "quality" / "scores"
    for entry, b in (("aa-alpha", b_alpha), ("bb-beta", b_beta)):
        src = sorted(fx.glob(f"{entry}/*-r3-*.json"))[-1]
        (root / entry).mkdir(parents=True)
        (root / entry / src.name).write_text(json.dumps(_with_after(src, entry, b)))
    return root


def test_the_after_rows_are_per_scope_kind_and_dimension_and_held_to_the_weak_rule(tmp_path):
    zero = {**B_STAGE, "b1": 0}
    files = table.load_scores(_scores(tmp_path, zero, zero))
    rows = {table.row_key(r): r for r in table.rows(table.latest_per_entry(files))}
    stage = rows["PROBLEM · founder · - · stage"]
    assert stage["weak"] and stage["weak_on"] == ["b1", "b2", "b4"], "a 0 on B1 in two entries; B2, B4 at 1.0"
    assert stage["zero_entries"]["b1"] == ["aa-alpha", "bb-beta"] and list(stage["means"]) == list(rubric.B_CRITERIA)
    assert stage["means"]["b6"] is None and stage["fix"] == {"category": "no model", "place": table.AFTER_FIX["stage"][1]}
    card = rows["PROBLEM · founder · problem.prevalence · dimension"]
    assert "DimensionStagePage, AnswerChart" in card["fix"]["place"] and "BriefFacts" in card["fix"]["place"]
    flow = rows["PROBLEM · founder · problem.prevalence · q"]
    assert list(flow["means"]) == list(rubric.CRITERIA), "a flow row is read on R1-R6 alone"
    text = table.render(files)
    after = text.split("## After the answers", 1)[1].split("## Insights", 1)[0]
    assert "| **WEAK** | PROBLEM | - | stage | 2 | 0.00 | 1.00 | 2.00 | 1.00 | 2.00 | – |" in after
    assert "| stage |" not in text.split("## The rows", 1)[1].split("## After the answers", 1)[0]
    assert "### PROBLEM · founder · - · stage -- weak on B1, B2, B4" in text
    assert "- founder: score_pct" in text and "after_pct 60.0%" in text


def test_a_middling_row_is_weak_by_its_mean_and_a_good_one_is_not(tmp_path):
    good = {**B_STAGE, "b2": 2, "b4": 2}
    files = table.load_scores(_scores(tmp_path, good, good))
    rows = {table.row_key(r): r for r in table.rows(table.latest_per_entry(files))}
    assert not rows["PROBLEM · founder · - · stage"]["weak"]


def test_the_insights_screen_is_fixed_in_themes_md_and_the_insights_tab(tmp_path):
    assert table.fix_location("founder", "insights-screen", None) == table.AFTER_FIX["insights-screen"]
    category, place = table.AFTER_FIX["insights-screen"]
    assert category == "shared file" and place.startswith("themes.md") and "Insights tab" in place
    row = {"fix": {"category": category, "place": place}, "dimension": "-", "audience": "founder",
           "kind": "insights-screen"}
    cloud = tmp_path / "cloud"
    (cloud / cycle.INSTRUCTIONS_REL).mkdir(parents=True)
    (cloud / cycle.INSTRUCTIONS_REL / "themes.md").write_text("# THEMES\nGroup the answers.\n")
    quoted = cycle.current_text(row, cloud=cloud, cfg=cycle.load_config())
    assert "themes.md" in quoted["where"] and "Group the answers." in quoted["text"]


def test_the_adviser_reads_section_bs_anchors_and_whys(tmp_path):
    zero = {**B_STAGE, "b1": 0}
    files = table.load_scores(_scores(tmp_path, zero, zero))
    row = next(r for r in table.rows(table.latest_per_entry(files)) if r["kind"] == "stage")
    lines = cycle._criteria_lines(row)
    assert "- B1 **I know the answer and why.**" in lines and "neither, or they disagree" in lines
    failing = "\n".join(cycle.failing_screens(row, files))
    assert "B1 0 -- the verdict and its 6 of 7" in failing and "B4 1 -- a generic line" in failing


def test_the_cycle_scores_the_three_kinds_and_a_decision_may_name_them():
    assert set(rubric.AFTER_KINDS) <= set(dec.FOUNDER_SCREENS) and dec.FOUNDER_SCREENS[-3:] == rubric.AFTER_KINDS
    assert set(table.AFTER_FIX) == set(rubric.AFTER_KINDS)
    entry = {"id": "D-x", "cycle": "20261101-abcdef1", "proposals": [1], "decision": "held", "until": "never",
             "why": "the founder's words", "fix": "*",
             "row": {"scope": "PROBLEM", "audience": "founder", "dimension": "-", "screen": ["stage", "insights-screen"]}}
    assert dec.validate(entry, 1)["_row"]["screen"] == {"stage", "insights-screen"}


def test_a_previous_cycle_at_another_rubric_version_is_named_and_never_compared(tmp_path):
    from tests import test_quality_cycle_079 as c079                # noqa: PLC0415
    shutil.copy(c079.EARLIER, tmp_path / c079.EARLIER.name)
    old = (tmp_path / c079.EARLIER.name).read_text(encoding="utf-8").replace('"rubric_version": 3', '"rubric_version": 2')
    (tmp_path / c079.EARLIER.name).write_text(old, encoding="utf-8")
    _, data = c079.compose_the_fixture(cycles_dir=tmp_path)
    prev = data["previous"]
    assert prev["record"] == "20261025-0000aaa" and prev["studies"] == {} and prev["verdict"] == "not compared"
    assert "rubric version 2 and this one at 3" in prev["why"]


# ------------------------------------------------------------------------------------------------- FR-4 the cost

def test_the_runbook_says_what_the_answers_leg_costs():
    text = " ".join((REPO / "quality" / "CYCLE.md").read_text(encoding="utf-8").split())
    assert "spec 109" in text and "+40%" in text and "4 to 6 more screens" in text
    assert "cycle 4 is the first at 3" in text
