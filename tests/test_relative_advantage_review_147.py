"""Spec 147 FR-2 -- the walk on Relative advantage (keel-cloud 237, keel-web 181): the Check's Save may hold, the walk
waits on *Keel is reading your answers*, shoots `check-solution.relative_advantage-reviewed` after the band and presses
Continue, never Put back; a put-aside benefit is present by its `typed`; the belief read after the hold is the served
one; the stem check holds the idea's name and the frame, never the anchor's words.

Offline: the page and its API are routed in the browser (`http://keel.test`); no stack, no model, no key.
"""

from __future__ import annotations

import inspect
import json
from types import SimpleNamespace

import pytest
from playwright.sync_api import sync_playwright

from evals import backtest as bt
from evals import corpus_scenario as cs
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from harness.steps import Recorder
from instructions import spoken as spoken_mod

BASE = "http://keel.test"
CHECK_URL = f"{BASE}/projects/p1/define/solution/q/1/check"
PUT_URL = f"{BASE}/v2/projects/p1/calibration/SOLUTION"
RA = "solution.relative_advantage"
INTERACTION = "0b6f8e64-2a7c-4c55-9a3e-6c1d2a7b9e01"

# keel-cloud 237 tasks.md, *The Check after a read-back* (the cluster study, `TheBenefitsReadBackJourneyTest`).
BENEFITS = ["A job that runs to the end first time", "A run after one resubmit with more memory",
            "A tidier list of past jobs", "A job that finishes on its first run"]
WHYS = ["Today's way already gives this: a resubmit with more memory gets the job to run.",
        "A tidier list does nothing for a job killed for too little memory.",
        "This is the same gain as 'A job that runs to the end first time'."]
BAND = ("Keel put three benefits aside so what is left is what only your idea would have given them, and changed the "
        "moment the question asks about so it is the one that went wrong.")
BELIEF = ("For most, with it, their last job that was killed for too little memory or time would have given them a job "
          "that runs to the end first time.")
BELIEF_BEFORE = "For most, with it, their last job would have given them a job that runs to the end first time."
SAVED = {"items": [{"code": "benefit_1", "label": BENEFITS[0]}],
         "putAside": [{"typed": t, "why": w} for t, w in zip(BENEFITS[1:], WHYS)],
         "changed": {"line": BAND, "why": WHYS[0]}}
#: keel-cloud 237 tasks.md: the band where only the moment changed (no `why`).
MOMENT_ONLY = {"items": [{"code": f"benefit_{n + 1}", "label": b} for n, b in enumerate(BENEFITS)],
               "changed": {"line": "Keel changed the moment the question asks about so it is the one that went wrong."}}

_ROWS = "".join(f'<li class="listrow"><div class="listrow__line"><textarea class="listrow__ed">{b}</textarea>'
                f'<span class="listrow__wc">7 / 9</span></div></li>' for b in BENEFITS)
_PAGE = """<!doctype html><html><body><main><div class="ccard calib"><div class="ccard__body">
<p class="corridor__kicker">Solution</p><div id="band"></div>
<div class="listcheck"><p class="listcheck__title">Check</p><ul class="listrows" id="rows">%(rows)s</ul>
<div id="aside"></div></div>
<div class="keeltest"><p class="keeltest__t" id="belief">%(before)s</p></div><div id="status"></div></div>
<div class="ccard__foot"><button class="btn primary" id="primary">Save</button></div></div></main>
<script>
window.putBacks = 0;
document.addEventListener("click", (e) => {
  if (e.target.dataset && (e.target.dataset.testid === "row-put-back" || e.target.dataset.testid === "put-aside-back"))
    window.putBacks += 1;
});
const primary = document.getElementById("primary");
function moveOn() { history.pushState({}, "", "/projects/p1/define/solution/q/2"); document.querySelector("main").innerHTML = "<p>next</p>"; }
function changed() {
  document.getElementById("status").innerHTML = "";
  document.getElementById("band").innerHTML = %(band_html)s;
  document.getElementById("rows").innerHTML = '<li class="listrow"><div class="listrow__line"><textarea '
    + 'class="listrow__ed">%(lead)s</textarea><span class="listrow__wc">7 / 9</span></div></li>';
  document.getElementById("aside").innerHTML = '<div class="listcheck__aside" data-testid="put-aside"><ul class="listrows">'
    + %(aside)s + '</ul></div>';
  document.getElementById("belief").textContent = "%(belief)s";
  primary.textContent = "Continue";
  primary.disabled = false;
  primary.onclick = moveOn;
}
primary.onclick = async () => {
  const body = {expectedRevision: 11, answers: [{dimension: "solution.relative_advantage", list: {items: %(items)s}}]};
  const answer = await (await fetch("/v2/projects/p1/calibration/SOLUTION",
    {method: "PUT", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)})).json();
  if (!answer.review) { moveOn(); return; }
  primary.disabled = true;
  primary.textContent = "Keel is reading your answers";
  document.getElementById("status").innerHTML =
    '<p class="calib__drafting calib__reviewing" role="status" data-testid="list-reviewing">Keel is reading your answers</p>';
  setTimeout(changed, 700);
};
</script></body></html>"""


def _html() -> str:
    aside = " + ".join(json.dumps(
        f'<li class="listrow listrow--aside" data-testid="put-aside-row"><p class="listrow__aside"><s '
        f'class="listrow__struck">{t}</s></p><p class="listrow__warn listrow__warn--why" role="note">{w}</p><p '
        f'class="listrow__was"><button type="button" data-testid="put-aside-back">Put back</button></p></li>')
        for t, w in zip(BENEFITS[1:], WHYS))
    band = json.dumps(f'<div class="calib__changed" role="status" data-testid="list-changed"><p '
                      f'class="calib__changed-line">{BAND}</p><p class="calib__changed-why">{WHYS[0]}</p></div>')
    return _PAGE % {"rows": _ROWS, "before": BELIEF_BEFORE, "band_html": band, "lead": BENEFITS[0],
                    "aside": aside, "belief": BELIEF, "items": json.dumps([{"label": b} for b in BENEFITS])}


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def test_relative_advantage_is_the_fourth_reviewed_list():
    """FR-2 (keel-cloud 237 FR-1, keel-web 181 FR-2): the Check's Save holds on Relative advantage too."""
    assert vs_screens.REVIEWED_LISTS == ("problem.importance", "problem.current_solution_satisfaction",
                                         "solution.compatibility", RA)
    assert vs.is_list(RA)


def test_the_walk_waits_on_relative_advantage_and_shoots_it_again(browser, tmp_path):
    """FR-2 (144 FR-1's path): Save pressed, the hold waited out, the Check stays with the band; read again (the lead
    benefit left, three put aside with their whys, no changed row, the box the served belief), shot a second time
    (`check-solution.relative_advantage-reviewed`), Continue pressed; never Put back."""
    page = browser.new_page()
    put: list = []

    def handle(route):
        if route.request.url == PUT_URL:
            put.append(route.request.post_data_json)
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"revision": 12, "rows": [], "review": {"interactionId": INTERACTION}}))
        else:
            route.fulfill(status=200, content_type="text/html", body=_html())

    page.route(f"{BASE}/**", handle)
    page.goto(CHECK_URL)
    cam = bt.Camera(run_dir=tmp_path, page=page, watched={})
    corridor = vs_screens.Corridor(page, Recorder(tmp_path), BASE)
    corridor.camera = cam.founder
    try:
        seen = corridor.list_check({"dimension": RA, "saves": {"maxWords": 9}})
        assert page.url.endswith("/q/2")
        assert page.evaluate("window.putBacks") == 0, "never Put back"
    finally:
        page.close()
    hold = seen["review_hold"]
    assert hold["review"] == INTERACTION and hold["held"] is True and hold["outcome"] == "stayed"
    assert hold["continue_put"] == 0 and len(put) == 1
    assert seen["continue"] == vs_screens.LIST_CONTINUE
    assert [r["text"] for r in seen["rows"]] == BENEFITS and seen["test"]["belief"] == BELIEF_BEFORE
    reviewed = seen["reviewed"]
    assert [r["text"] for r in reviewed["rows"]] == [BENEFITS[0]]
    assert not any(r.get("changed") for r in reviewed["rows"]), "a benefit is never reworded"
    assert reviewed["put_aside"] == [{"typed": t, "why": w} for t, w in zip(BENEFITS[1:], WHYS)]
    assert reviewed["band"] == {"line": BAND, "why": WHYS[0]}
    assert reviewed["test"]["belief"] == BELIEF, "the box after the hold is the served belief"
    assert [s["slug"] for s in cam.founder_shots] == [f"check-{RA}", f"check-{RA}-reviewed"]
    assert cam.founder_shots[1]["review"]["band"]["line"] == BAND
    # the bundle and the record read the second shot as Relative advantage's
    j = SimpleNamespace(framing={RA: [seen]}, findings=[], review_holds={})
    assert cs.belief_after_the_hold(j, RA) == BELIEF
    cs._after_the_review(j, "SOLUTION", {"dimension": RA}, seen)
    assert j.review_holds[RA]["outcome"] == "stayed"


def test_a_put_aside_benefit_is_present_by_its_typed():
    """FR-2 (spec 104 FR-1 / 108 FR-2, 143 FR-2's rule now on Relative advantage): the founder's four benefits are on the
    list -- the lead as a row, three put aside -- never missing, never retyped; the stored list holds as saved."""
    assert vs.missing_rows(BENEFITS, SAVED) == []
    assert vs.held_by_review(BENEFITS, SAVED) == BENEFITS[1:]
    assert sorted(vs.founder_words(SAVED)) == sorted(BENEFITS)
    assert vs.review_changed(SAVED) == [{"typed": t, "label": None, "why": w} for t, w in zip(BENEFITS[1:], WHYS)]
    want = {"items": [{"code": f"benefit_{n + 1}", "label": b} for n, b in enumerate(BENEFITS)], "pickedIndex": None,
            "phrase": None}
    assert cs.reviewed_as_saved(want, SAVED)
    # the moment alone changed: no row moved, the band read as served
    assert vs.review_changed(MOMENT_ONLY) == [] and vs.missing_rows(BENEFITS, MOMENT_ONLY) == []
    assert vs.review_band(MOMENT_ONLY) == {"line": MOMENT_ONLY["changed"]["line"], "why": None}
    assert vs.lists_reviewed({"SOLUTION": {"questions": [{"dimension": RA, "answer": {"list": MOMENT_ONLY}}]}}) == {
        RA: {"review_changed": [], "band": {"line": MOMENT_ONLY["changed"]["line"], "why": None}}}


def test_no_cap_defect_is_filed_on_a_benefit():
    """FR-2: a benefit is never reworded, so no changed row is ever over the cap; the defect, were one served, names
    keel-cloud 237."""
    j = SimpleNamespace(findings=[])
    assert cs.review_defects(j, RA, SAVED, 9) == [] and j.findings == []
    long = {"items": [{"label": " ".join(["word"] * 12), "typed": BENEFITS[0], "why": "x"}]}
    assert cs.review_defects(j, RA, long, 9) and j.findings[0]["what"].startswith("DEFECT (keel-cloud 237)")


def test_the_review_rows_belief_is_the_one_served_after_the_hold():
    """FR-2: where the Check stayed with the band, the `/review` row's belief is held to the box read after the hold;
    nowhere else is it read (no hold, no reviewed box: None)."""
    assert cs.belief_after_the_hold(SimpleNamespace(framing={RA: [{"screen": "check"}]}), RA) is None
    assert cs.belief_after_the_hold(SimpleNamespace(framing={}), RA) is None
    source = inspect.getsource(cs.leg_calibrate)
    assert "served = belief_after_the_hold(j, key)" in source and "want = served" in source


# ------------------------------------------------------------------------------------- the stem: name and frame

SIZER_WHAT = "software on every node that predicts each job's resource needs"
CLUSTER_JOB = "get each job to run to the end without wasting the cluster"


@pytest.mark.parametrize("anchor", [
    "Think of the last job that was killed for too little memory or time.",       # the review's rewrite
    "Think of the last job that ran out of memory.",                              # the Prevalence draft's
    "Think of the most recent time a job ran out of memory on the cluster.",      # the stem's
])
def test_the_strict_stem_check_holds_the_name_and_the_frame_never_the_anchor(anchor):
    """FR-2 (keel-cloud 237 FR-2 / FR-3): the hard case may differ from the Prevalence draft's -- the scripted journey's
    want is the question after the anchor, composed around the idea's name and the job's tail, whatever the anchor."""
    asked = "Would Sizer, software on every node, have helped you get each job to run to the end better, or not?"
    want = cs.advantage_question_want(f"{anchor} {asked}", "Sizer", SIZER_WHAT, job=CLUSTER_JOB, occasion="job",
                                      strict=True)
    assert want == asked
    wrong = f"{anchor} Would Sizer, software on every node, have done that better for you, or not?"
    assert cs.advantage_question_want(wrong, "Sizer", SIZER_WHAT, job=CLUSTER_JOB, occasion="job", strict=True) == asked


def test_the_strict_stem_check_on_the_at_stake_anchor_wants_done_that_better():
    """FR-2: the at-stake anchor names the job itself; its question keeps *done that better* (frame 198)."""
    served = spoken_mod.advantage_stem("job", "Sizer", SIZER_WHAT, CLUSTER_JOB)
    _, asked = vs.benefit_split(served)
    assert cs.advantage_question_want(served, "Sizer", SIZER_WHAT, job=CLUSTER_JOB, occasion="job",
                                      strict=True) == asked
    assert asked.endswith(spoken_mod.DONE_BETTER)


def test_the_back_test_holds_the_name_or_it_where_the_ladder_reaches_it():
    """FR-2: on the back-test the anchor and the job are the model's -- the question names the idea, or says *it* where
    237's cap ladder reaches it with the job served (Fresco's ten-word job); *it* where the name fits is a fault."""
    fresco = ("Think of the last daily log when you lost site notes before writing it. Would it have helped you keep an "
              "accurate record of the day's work on site better, or not?")
    what = "an AI scribe that turns your site-walk videos into notes"
    want = cs.advantage_question_want(fresco, "Fresco", what)
    assert want == vs.benefit_split(fresco)[1]
    short = "Think of the last job that ran out of memory. Would it have helped you finish jobs better, or not?"
    assert cs.advantage_question_want(short, "Sizer", "software on every node") == \
        "Would Sizer, software on every node, have helped you finish jobs better, or not?"
    assert cs.advantage_question_want("Would Palus have made your last cash decision go better for you, or not?",
                                      "Palus", None) is None


def test_the_idea_name_hold_wants_the_name_and_the_frame():
    """FR-2 wired: `_hold_the_idea_name` holds the question after the anchor (`advantage_question_want`), the frame named
    in its fault; *it* on the back-test a finding, never a stop."""
    source = inspect.getsource(cs._hold_the_idea_name)
    assert "advantage_question_want(served_q, name" in source and "vs.benefit_split(served_q)" in source
    assert '"frame": vs.benefit_frame_of(served_q)' in source and "vs.benefit_question(occasion, name)" in source
    assert "j.findings.append" in source
