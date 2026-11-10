"""Spec 149 FR-3 -- the walk reads the Check as keel-web 184 draws it (keel-cloud 243): Keel's row and its kind
(*Reworded from* / *In place of* / *Keel's suggestion*), its number shared with the record, the words behind it, its why
and one Put back per changed row (never pressed), no *Was*; the record *What Keel changed* (struck, *yours* / *Keel's
draft*, *Replaced by* / *Reworded as*) as the rows put aside; on Choose a suggested row is Keel's (several now), and
`review_picks` / `lists_reviewed` carry `inPlaceOf` / `replacedBy`.

Offline: the pages are 184's DOM written by `tests/keel_pattern_184.py` and routed in the browser (`http://keel.test`);
no stack, no model, no key. The studies are keel-cloud 243's invented ones.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
from playwright.sync_api import sync_playwright

from evals import backtest as bt
from evals import corpus_scenario as cs
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from harness.steps import Recorder
from tests import keel_pattern_184 as k184
from tests.test_read_back_rows_149 import (EXPLAINING, GAMES, GAMES_WHY, NEW_HIRE, NEW_HIRE_WHY, OVERTIME,
                                           OVERTIME_WHY, OWN, RECONCILING, RERUNNING, STAGING, STAGING_BAND,
                                           staging_answer)

BASE = "http://keel.test"
CHECK_URL = f"{BASE}/projects/p1/define/problem/q/2/check"
PUT_URL = f"{BASE}/v2/projects/p1/calibration/PROBLEM"
IMPORTANCE, COMPAT = "problem.importance", "solution.compatibility"
INTERACTION = "5b0c2f1e-0d43-4b7a-9e57-2f1d0c3a9b11"


def staging_saved() -> dict:
    """The staging shape as keel-cloud 243 serves it (contract 64): own + three Keel rows in place, three put aside."""
    listed = vs.in_place_applied(STAGING, vs.read_back_answer(staging_answer(1), STAGING)["readings"], floor=3)
    return {"items": [{"code": "own" if i == 0 else f"rival_{i}", **item} for i, item in enumerate(listed["items"])],
            "putAside": listed["putAside"], "changed": {"line": STAGING_BAND, "why": GAMES_WHY}}


# keel-web 184's Compatibility fixture, its every kind (an invented returns desk would do; here 243's payroll study)
C_EXPORT = "could export the payroll register to a spreadsheet"
C_AUDIT = "had a payroll system that keeps an audit trail"
C_READ = "were allowed to let an outside tool read the payroll register"
C_SIDE = "could see last month's register beside this month's"
C_SIDE_NOW = "could open last month's register beside this month's"
C_DRAFT = "could print the register for the auditor"
C_DRAFT_NOW = "could hand the auditor the register on paper"
C_SUGGEST = "could send a payslip correction the same day"
COMPAT_SAVED = {
    "items": [{"code": "condition_1", "label": C_DRAFT_NOW, "typed": C_DRAFT, "why": "Said as what they can do.",
               "typedKeels": True},
              {"code": "condition_2", "label": C_READ, "suggested": True, "suggestedWhy": "No row asks whether they may.",
               "inPlaceOf": C_AUDIT},
              {"code": "condition_3", "label": C_SIDE_NOW, "typed": C_SIDE, "why": "Said as a step they take."},
              {"code": "condition_4", "label": C_SUGGEST, "suggested": True, "suggestedWhy": "The step no row tests."}],
    "putAside": [{"typed": C_AUDIT, "why": "Most of your segment already has this.", "replacedBy": C_READ}],
    "changed": {"line": "Keel changed two conditions so strangers are asked what they can do themselves, put one "
                        "condition aside because your segment already has it, and suggested one in its place.",
                "why": "Said as what they can do."}}


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _corridor(browser, body: str, tmp_path):
    page = browser.new_page()
    page.route(f"{BASE}/**", lambda route: route.fulfill(status=200, content_type="text/html", body=body))
    page.goto(CHECK_URL)
    return page, vs_screens.Corridor(page, Recorder(tmp_path), BASE)


def test_the_importance_check_is_read_as_184_draws_it(browser, tmp_path):
    """FR-3: the staging shape's Check -- the own row, three Keel rows *In place of "..."* numbered 1-3 with their whys
    and Put back each; the record's three *replaced* entries, *yours*, *Replaced by* the Keel row; read as the rows put
    aside with `replaced_by`. No row reads a *Was*."""
    saved = staging_saved()
    page, corridor = _corridor(browser, k184.page(saved, IMPORTANCE, own_locked=True), tmp_path)
    try:
        drawn = corridor._list_rows()
    finally:
        page.close()
    rows = drawn["rows"]
    assert [r["text"] for r in rows] == [OWN, RECONCILING, RERUNNING, EXPLAINING]
    assert rows[0] == {"text": OWN, "tag": "yours", "locked": True}
    for n, (row, struck) in enumerate(zip(rows[1:], (GAMES, OVERTIME, NEW_HIRE)), start=1):
        assert row["keel"] == "in-place" and row["n"] == n and row["in_place_of"] == struck
        assert row["line"] == f'In place of "{struck}".' and row["put_back"] is True and row["suggested"] is True
        assert row["why"] == saved["items"][n]["suggestedWhy"] and "was" not in row and "changed" not in row
        assert row["warn"] == "", "the why is the line's, never a `.listrow__warn`"
    assert [(e["kind"], e["whose"], e["n"], e["struck"], e["now"], e["put_back"]) for e in drawn["keel_changed"]] == [
        ("replaced", "yours", 1, [GAMES], RECONCILING, False), ("replaced", "yours", 2, [OVERTIME], RERUNNING, False),
        ("replaced", "yours", 3, [NEW_HIRE], EXPLAINING, False)]
    assert [e["why"] for e in drawn["keel_changed"]] == [GAMES_WHY, OVERTIME_WHY, NEW_HIRE_WHY]
    assert drawn["put_aside"] == [{"typed": GAMES, "why": GAMES_WHY, "replaced_by": RECONCILING},
                                  {"typed": OVERTIME, "why": OVERTIME_WHY, "replaced_by": RERUNNING},
                                  {"typed": NEW_HIRE, "why": NEW_HIRE_WHY, "replaced_by": EXPLAINING}]
    assert drawn["band"] == {"line": STAGING_BAND, "why": GAMES_WHY}
    assert cs.check_pattern_faults(drawn, saved) == []


def test_the_compatibility_check_every_kind(browser, tmp_path):
    """FR-3 (184's Compatibility fixture, its every kind): reworded Keel's draft, in place, reworded yours, Keel's
    suggestion (no number, no Put back); the record *replaced yours / reworded Keel's draft / reworded yours* and the
    numbers shared with it (2, 1, 3, none)."""
    page, corridor = _corridor(browser, k184.page(COMPAT_SAVED, COMPAT), tmp_path)
    try:
        drawn = corridor._list_rows()
    finally:
        page.close()
    rows = drawn["rows"]
    assert [(r["keel"], r.get("n"), r["put_back"]) for r in rows] == [
        ("reworded", 2, True), ("in-place", 1, True), ("reworded", 3, True), ("suggestion", None, False)]
    assert rows[0]["changed"] is True and rows[0]["was"] == C_DRAFT and rows[2]["was"] == C_SIDE
    assert rows[1]["in_place_of"] == C_AUDIT and rows[3]["suggested"] is True and rows[3]["line"] == "Keel's suggestion."
    assert [(e["kind"], e["whose"], e.get("n")) for e in drawn["keel_changed"]] == [
        ("replaced", "yours", 1), ("reworded", "keels", 2), ("reworded", "yours", 3)]
    assert drawn["put_aside"] == [{"typed": C_AUDIT, "why": "Most of your segment already has this.",
                                   "replaced_by": C_READ}]
    assert cs.check_pattern_faults(drawn, COMPAT_SAVED) == []


def test_the_pattern_faults_name_what_parts_from_the_wire():
    """FR-3: a Keel row in place drawn with another row's words, a row drawn with *Was* (179's), a numbered row with no
    record entry, a row put aside missing from the record -- each a fault; a page with neither Keel's rows nor the
    record (a web before 184) is read as 179 drew it, no fault."""
    saved = staging_saved()
    good = {"rows": [{"text": OWN}] + [{"text": i["label"], "keel": "in-place", "n": n, "in_place_of": i["inPlaceOf"],
                                        "put_back": True, "suggested": True}
                                       for n, i in enumerate(saved["items"][1:], start=1)],
            "keel_changed": [{"kind": "replaced", "whose": "yours", "n": n, "struck": [a["typed"]],
                              "now": a["replacedBy"], "put_back": False} for n, a in enumerate(saved["putAside"], 1)]}
    assert cs.check_pattern_faults(good, saved) == []
    bad = json.loads(json.dumps(good))
    bad["rows"][1]["in_place_of"] = OVERTIME
    bad["rows"][2] = {"text": RERUNNING, "changed": True, "was": OVERTIME}
    bad["keel_changed"] = bad["keel_changed"][:1]
    whats = [f["what"] for f in cs.check_pattern_faults(bad, saved)]
    assert "Keel's row in place is not drawn *In place of* its row with Put back" in whats
    assert "a changed row drawn with *Was* (keel-web 179), not Keel's line" in whats
    assert "a numbered row with no record entry of its number" in whats
    assert "a row put aside is not in the record" in whats
    assert cs.check_pattern_faults({"rows": [{"text": OWN}], "put_aside": [{"typed": GAMES}]}, saved) == []


READ_PAGE = "<!doctype html><html><body><main>%s</main></body></html>"


def test_the_screen_of_record_reads_the_pattern(browser):
    """FR-3: the readers' screen (`backtest.READ_JS`) reads Keel's rows in place (with the words behind each and their
    number), the reworded rows' words from their line (no *Was*), the record, and the rows put aside with
    `replaced_by`; Keel's standalone suggestion among the suggested rows."""
    page = browser.new_page()
    try:
        page.set_content(READ_PAGE % k184.check_html(COMPAT_SAVED, COMPAT))
        drawn = page.evaluate(bt.READ_JS)
        page.set_content(READ_PAGE % k184.check_html(staging_saved(), IMPORTANCE, own_locked=True))
        staging = page.evaluate(bt.READ_JS)
    finally:
        page.close()
    review = drawn["review"]
    assert review["changed"] == [{"row": C_DRAFT_NOW, "was": C_DRAFT, "why": "Said as what they can do.", "n": 2},
                                 {"row": C_SIDE_NOW, "was": C_SIDE, "why": "Said as a step they take.", "n": 3}]
    assert review["in_place"] == [{"row": C_READ, "in_place_of": C_AUDIT, "why": "No row asks whether they may.", "n": 1}]
    assert review["put_aside"] == [{"typed": C_AUDIT, "why": "Most of your segment already has this.",
                                    "replaced_by": C_READ}]
    assert [(e["kind"], e["whose"]) for e in review["record"]] == [("replaced", "yours"), ("reworded", "keels"),
                                                                    ("reworded", "yours")]
    assert {"row": C_SUGGEST, "why": "The step no row tests."} in drawn["suggested"]
    assert staging["rows"][1:] == [RECONCILING, RERUNNING, EXPLAINING]
    assert [r["in_place_of"] for r in staging["review"]["in_place"]] == [GAMES, OVERTIME, NEW_HIRE]
    assert staging["review"]["band"]["line"] == STAGING_BAND


# ------------------------------------------------------------------------------------ the hold, never Put back

_HOLD = """<!doctype html><html><body><main><div class="ccard calib"><div class="ccard__body">
<p class="corridor__kicker">Problem</p><div id="check">%(before)s</div><div id="status"></div></div>
<div class="ccard__foot"><button class="btn primary" id="primary">Save</button></div></div></main>
<script>
window.putBacks = 0;
document.addEventListener("click", (e) => {
  if (e.target.dataset && (e.target.dataset.testid === "row-put-back" || e.target.dataset.testid === "put-aside-back"))
    window.putBacks += 1;
});
const primary = document.getElementById("primary");
function moveOn() { history.pushState({}, "", "/projects/p1/define/problem/q/3"); document.querySelector("main").innerHTML = "<p>next</p>"; }
primary.onclick = async () => {
  const answer = await (await fetch("/v2/projects/p1/calibration/PROBLEM",
    {method: "PUT", headers: {"Content-Type": "application/json"}, body: JSON.stringify({answers: []})})).json();
  if (!answer.review) { moveOn(); return; }
  primary.disabled = true;
  primary.textContent = "Keel is reading your answers";
  document.getElementById("status").innerHTML =
    '<p class="calib__drafting calib__reviewing" role="status" data-testid="list-reviewing">Keel is reading your answers</p>';
  setTimeout(() => {
    document.getElementById("status").innerHTML = "";
    document.getElementById("check").innerHTML = %(after)s;
    primary.textContent = "Continue"; primary.disabled = false; primary.onclick = moveOn;
  }, 600);
};
</script></body></html>"""


def test_the_walk_holds_reads_the_pattern_and_never_puts_back(browser, tmp_path):
    """FR-3 (144 FR-1's path on 184's Check): Save pressed, the hold waited out, the Check stays with the band; read again
    as 184 draws it (the three pairs), shot a second time, Continue pressed; Put back never pressed."""
    before = k184.check_html({"items": [{"label": r} for r in STAGING]}, IMPORTANCE, own_locked=True)
    after = json.dumps(k184.check_html(staging_saved(), IMPORTANCE, own_locked=True))
    page = browser.new_page()

    def handle(route):
        if route.request.url == PUT_URL:
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"revision": 9, "rows": [], "review": {"interactionId": INTERACTION}}))
        else:
            route.fulfill(status=200, content_type="text/html", body=_HOLD % {"before": before, "after": after})

    page.route(f"{BASE}/**", handle)
    page.goto(CHECK_URL)
    cam = bt.Camera(run_dir=tmp_path, page=page, watched={})
    corridor = vs_screens.Corridor(page, Recorder(tmp_path), BASE)
    corridor.camera = cam.founder
    try:
        seen = corridor.list_check({"dimension": IMPORTANCE, "saves": {"maxWords": 9}})
        assert page.url.endswith("/q/3")
        assert page.evaluate("window.putBacks") == 0, "never Put back"
    finally:
        page.close()
    assert seen["review_hold"]["outcome"] == "stayed"
    reviewed = seen["reviewed"]
    assert [r.get("keel") for r in reviewed["rows"]] == [None, "in-place", "in-place", "in-place"]
    assert [r.get("n") for r in reviewed["rows"]] == [None, 1, 2, 3]
    assert [a["replaced_by"] for a in reviewed["put_aside"]] == [RECONCILING, RERUNNING, EXPLAINING]
    assert [s["slug"] for s in cam.founder_shots] == [f"check-{IMPORTANCE}", f"check-{IMPORTANCE}-reviewed"]
    assert cs.handed_rows(seen) == STAGING


# ------------------------------------------------------------------------- Choose, the record (inPlaceOf / replacedBy)

def _answer(*typed: str, picked: int = 0):
    return SimpleNamespace(listed={"items": [{"label": t} for t in typed], "pickedIndex": picked}, unsure=False)


def test_on_choose_the_pick_falls_to_keels_row_in_its_place_and_the_pair_is_recorded():
    """FR-3 (147's rule, several suggested rows now): the planned pick put aside with Keel's row in its place and no
    founder row left -- the pick falls to that Keel row (not the first suggestion); `review_picks` records the pair."""
    draft = {"items": [{"code": "condition_1", "label": C_EXPORT}, {"code": "condition_2", "label": C_AUDIT}]}
    saved = {"items": [{"code": "condition_1", "label": C_SUGGEST, "suggested": True, "suggestedWhy": "w1",
                        "inPlaceOf": C_EXPORT},
                       {"code": "condition_2", "label": C_READ, "suggested": True, "suggestedWhy": "w2",
                        "inPlaceOf": C_AUDIT}],
             "putAside": [{"typed": C_EXPORT, "why": "Most have it."}, {"typed": C_AUDIT, "why": "Most have this."}],
             "changed": {"line": "Keel put two conditions aside because your segment already has them, and suggested "
                                 "two in their place.", "why": "Most have it."}}
    question = {"dimension": COMPAT, "draft": saved, "answer_draft": draft,
                "review_suggested": [r["label"] for r in vs.review_suggested(saved, draft)]}
    assert question["review_suggested"] == [C_SUGGEST, C_READ]
    j = SimpleNamespace(strict=False, findings=[], review_picks={})
    assert cs._choose_label(j, question, _answer(C_EXPORT, C_AUDIT, picked=1)) == (C_READ, 1)
    assert j.review_picks[COMPAT] == {"planned": C_AUDIT, "why": "Most have this.", "picked": C_READ, "row": 1,
                                      "replacedBy": C_READ, "inPlaceOf": C_AUDIT}
    assert "fell to Keel's review suggested in its place" in j.findings[-1]["what"]
    # the record of the walk names each pair, and the review's suggestion finding says which row each stands for
    j = SimpleNamespace(findings=[])
    cs._name_keel_added(j, COMPAT, question, _answer(C_EXPORT, C_AUDIT))
    assert j.findings[-1]["what"] == (f"Compatibility: Keel's review suggested at the Check: '{C_SUGGEST}' in place of "
                                      f"'{C_EXPORT}' -- w1, '{C_READ}' in place of '{C_AUDIT}' -- w2 (keel-cloud 243 FR-3)")
    view = {"SOLUTION": {"questions": [{"dimension": COMPAT, "answer": {"list": saved}}]}}
    reviewed = vs.lists_reviewed(view)[COMPAT]
    assert [c.get("replacedBy") for c in reviewed["review_changed"]] == [C_SUGGEST, C_READ]
    assert [r["inPlaceOf"] for r in reviewed["in_place"]] == [C_EXPORT, C_AUDIT]
    # Choose offers the rows as served, no put-aside row among them
    assert cs.choose_after_review_faults(question, {"options": [C_SUGGEST, C_READ], "writes": []}) == []


def test_a_keel_row_the_review_wrote_is_never_cut_to_fit():
    """FR-3: the over-cap cut skips Keel's rows the review wrote (reworded, in place) -- a keel-cloud defect to file,
    never a retype (143 FR-2's rule, on 184's hooks)."""
    import inspect                                                     # noqa: PLC0415
    source = inspect.getsource(vs_screens.Corridor._cut_over_cap_rows)
    assert 'get_attribute(KEEL_KIND_ATTR) not in ("reworded", "in-place")' in source
