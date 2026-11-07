"""Spec 144 FR-1 / FR-2 -- the walk waits for the review (keel-cloud 233, keel-web 180), on a page that draws the Check
as 180 is specified to: Save posts `PUT calibration/{vector}`, whose answer (contract 63) names `review:
{interactionId}`; the page holds (*Keel is reading your answers*, the primary disabled, `calib__drafting`,
`role="status"`), then either moves on, or stays with the band (`list-changed`), the changed rows and the put-aside rows,
the primary reading *Continue* (Compatibility: *Continue to choose*).

Offline: the page and its API are routed in the browser (`http://keel.test`); no stack, no model, no key.
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

BASE = "http://keel.test"
CHECK_URL = f"{BASE}/projects/p1/define/solution/q/3/check"
PUT_URL = f"{BASE}/v2/projects/p1/calibration/SOLUTION"
COMPAT = "solution.compatibility"
INTERACTION = "6f0c6c0e-46b2-4c39-9c39-7d3c1c3c0a11"
#: keel-cloud 233 tasks.md, *What a reviewed Compatibility list serves* (the journey's fixture: Codyco).
TYPED = ["could forward unanswered calls to another number", "could take a booking call at the front desk",
         "had their phone online"]
PERMISSION = "was allowed to have unanswered calls forwarded to another number"
WHY = "Forwarding is set on the phone system, which someone else holds, not the desk."
SETTLED = "Most of your segment already has this: they work with a phone that is online."
BAND = ("Keel changed one condition so strangers are asked what they can do themselves, and put one condition aside "
        "because your segment already has it.")
REVIEWED = {"items": [{"code": "condition_1", "label": PERMISSION, "typed": TYPED[0], "why": WHY,
                       "asked": "you were allowed to have unanswered calls forwarded to another number"},
                      {"code": "condition_2", "label": TYPED[1]}],
            "putAside": [{"typed": TYPED[2], "why": SETTLED}], "changed": {"line": BAND, "why": WHY}}

_PAGE = """<!doctype html><html><body><main><div class="ccard calib"><div class="ccard__body">
<p class="corridor__kicker">Solution</p><div id="band"></div>
<div class="listcheck"><p class="listcheck__title">Check</p><ul class="listrows" id="rows">
<li class="listrow"><div class="listrow__line"><textarea class="listrow__ed">could forward unanswered calls to another number</textarea><span class="listrow__wc">7 / 16</span></div></li>
<li class="listrow"><div class="listrow__line"><textarea class="listrow__ed">could take a booking call at the front desk</textarea><span class="listrow__wc">8 / 16</span></div></li>
<li class="listrow"><div class="listrow__line"><textarea class="listrow__ed">had their phone online</textarea><span class="listrow__wc">4 / 16</span></div></li>
</ul><div id="aside"></div></div><div id="status"></div></div>
<div class="ccard__foot"><button class="btn primary" id="primary">Save</button></div></div></main>
<script>
const MODE = "%(mode)s";
window.putBacks = 0;
document.addEventListener("click", (e) => {
  if (e.target.dataset && (e.target.dataset.testid === "row-put-back" || e.target.dataset.testid === "put-aside-back"))
    window.putBacks += 1;
});
const primary = document.getElementById("primary");
function moveOn(to) { history.pushState({}, "", to); document.querySelector("main").innerHTML = "<p>next</p>"; }
function changed() {
  document.getElementById("status").innerHTML = "";
  document.getElementById("band").innerHTML = '<div class="calib__changed" role="status" data-testid="list-changed">'
    + '<p class="calib__changed-line">%(band)s</p><p class="calib__changed-why">%(why)s</p></div>';
  document.getElementById("rows").innerHTML =
    '<li class="listrow"><div class="listrow__line"><textarea class="listrow__ed">%(permission)s</textarea>'
    + '<span class="listrow__tag listrow__tag--changed" data-testid="row-changed">changed</span></div>'
    + '<p class="listrow__warn listrow__warn--why" role="note" data-testid="row-why">%(why)s</p>'
    + '<p class="listrow__was" data-testid="row-was"><span class="listrow__was-k">Was:</span> '
    + '<span class="listrow__was-said">%(typed0)s</span><button type="button" data-testid="row-put-back">Put back'
    + '</button></p></li>'
    + '<li class="listrow"><div class="listrow__line"><textarea class="listrow__ed">%(typed1)s</textarea>'
    + '<span class="listrow__wc">8 / 16</span></div></li>';
  document.getElementById("aside").innerHTML = '<div class="listcheck__aside" data-testid="put-aside">'
    + '<ul class="listrows"><li class="listrow listrow--aside" data-testid="put-aside-row"><p class="listrow__aside">'
    + '<s class="listrow__struck">%(typed2)s</s></p><p class="listrow__warn listrow__warn--why" role="note">'
    + '%(settled)s</p><p class="listrow__was"><button type="button" data-testid="put-aside-back">Put back</button>'
    + '</p></li></ul></div>';
  primary.textContent = "Continue to choose";
  primary.disabled = false;
  primary.onclick = () => moveOn("/projects/p1/define/solution/q/3/choose");
}
primary.onclick = async () => {
  const body = {expectedRevision: 11, answers: [{dimension: "solution.compatibility", list: {items: [
    {label: "could forward unanswered calls to another number"}, {label: "could take a booking call at the front desk"},
    {label: "had their phone online"}]}}]};
  const answer = await (await fetch("/v2/projects/p1/calibration/SOLUTION",
    {method: "PUT", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)})).json();
  if (!answer.review) { moveOn("/projects/p1/define/solution/q/3/choose"); return; }
  primary.disabled = true;
  primary.textContent = "Keel is reading your answers";
  document.getElementById("status").innerHTML =
    '<p class="calib__drafting" role="status">Keel is reading your answers</p>';
  if (MODE === "stuck") return;
  setTimeout(() => MODE === "changed" ? changed() : moveOn("/projects/p1/define/solution/q/3/choose"), 700);
};
</script></body></html>"""


def _html(mode: str) -> str:
    return _PAGE % {"mode": mode, "band": BAND, "why": WHY, "permission": PERMISSION, "typed0": TYPED[0],
                    "typed1": TYPED[1], "typed2": TYPED[2], "settled": SETTLED}


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _walk(browser, tmp_path, mode: str, *, review: bool = True):
    """The page in `mode` (`changed`: the review changed rows, the Check stays; `moved`: it changed none, the page moves
    on; `stuck`: the hold never leaves) behind a routed API whose Save names `review` (or not)."""
    page = browser.new_page()
    put: list = []

    def handle(route):
        url = route.request.url
        if url == PUT_URL:
            put.append(route.request.post_data_json)
            answer = {"revision": 12, "rows": [], **({"review": {"interactionId": INTERACTION}} if review else {})}
            route.fulfill(status=200, content_type="application/json", body=json.dumps(answer))
        else:
            route.fulfill(status=200, content_type="text/html", body=_html(mode))

    page.route(f"{BASE}/**", handle)
    page.goto(CHECK_URL)
    cam = bt.Camera(run_dir=tmp_path, page=page, watched={})
    corridor = vs_screens.Corridor(page, Recorder(tmp_path), BASE)
    corridor.camera = cam.founder
    return page, corridor, cam, put


def test_a_save_that_holds_and_stays_is_shot_again_after_the_band(browser, tmp_path):
    """FR-1, step by step: Save pressed; *Keel is reading your answers* seen (the primary disabled) and waited out; the
    Check stays with the band and *Continue to choose*; the Check read again and shot a second time
    (`check-solution.compatibility-reviewed`, its record carrying `review`); Continue pressed; never Put back."""
    page, corridor, cam, put = _walk(browser, tmp_path, "changed")
    try:
        seen = corridor.list_check({"dimension": COMPAT, "saves": {"maxWords": 16}})
        assert page.url.endswith("/choose")
        assert page.evaluate("window.putBacks") == 0, "never Put back"
    finally:
        page.close()
    hold = seen["review_hold"]
    assert hold["review"] == INTERACTION and hold["held"] is True and hold["outcome"] == "stayed"
    assert hold["held_s"] >= 0.3 and hold["picked_sent"] is False
    assert put[0]["answers"][0]["list"].get("pickedIndex") is None, "233 FR-2: Compatibility's Check sends no pick"
    assert seen["primary"] == "Save" and seen["continue"] == vs_screens.LIST_CONTINUE_CHOOSE
    assert [r["text"] for r in seen["rows"]] == TYPED, "the first read: the Check as drafted, before the Save"
    reviewed = seen["reviewed"]
    assert [r["text"] for r in reviewed["rows"]] == [PERMISSION, TYPED[1]]
    assert reviewed["rows"][0]["changed"] and reviewed["rows"][0]["was"] == TYPED[0]
    assert reviewed["band"] == {"line": BAND, "why": WHY}
    assert reviewed["put_aside"] == [{"typed": TYPED[2], "why": SETTLED}]
    slugs = [s["slug"] for s in cam.founder_shots]
    assert slugs == [f"check-{COMPAT}", f"check-{COMPAT}-reviewed"]
    first, second = cam.founder_shots
    assert not first.get("review") and second["review"]["band"]["line"] == BAND
    assert second["review"]["changed"] == [{"row": PERMISSION, "was": TYPED[0], "why": WHY}]
    assert second["file"].endswith(f"founder-02-check-{COMPAT}-reviewed.png")


def test_a_save_that_holds_and_moves_on_reads_nothing_more(browser, tmp_path):
    """FR-1: the review changed nothing -- the hold leaves and the page moves on; one shot, nothing read after."""
    page, corridor, cam, _ = _walk(browser, tmp_path, "moved")
    try:
        seen = corridor.list_check({"dimension": COMPAT, "saves": {"maxWords": 16}})
    finally:
        page.close()
    assert seen["review_hold"]["outcome"] == "moved" and seen["review_hold"]["held"] is True
    assert "reviewed" not in seen and "continue" not in seen
    assert [s["slug"] for s in cam.founder_shots] == [f"check-{COMPAT}"]


def test_a_save_with_no_review_moves_on_as_before(browser, tmp_path):
    """FR-1: the answer names no `review` (the switch off; a stack before 233) -- the page moves on at once."""
    page, corridor, cam, _ = _walk(browser, tmp_path, "moved", review=False)
    try:
        seen = corridor.list_check({"dimension": COMPAT, "saves": {"maxWords": 16}})
    finally:
        page.close()
    assert seen["review_hold"] == {"review": None, "held": False, "held_s": None, "outcome": "moved",
                                   "picked_sent": False}
    assert [s["slug"] for s in cam.founder_shots] == [f"check-{COMPAT}"]


def test_a_hold_past_the_cap_stops_the_walk_by_name(browser, tmp_path, monkeypatch):
    """FR-1: the hold never leaves -- past the cap a `DEFECT (keel-cloud 233)` stop; the page kept as evidence, never a
    founder screen; `_check_screen` files the finding and the hold before the stop goes on up."""
    monkeypatch.setattr(vs_screens, "REVIEW_HOLD_CAP_S", 1)
    page, corridor, cam, _ = _walk(browser, tmp_path, "stuck")
    j = SimpleNamespace(entry=None, strict=False, findings=[], review_holds={}, corridor=corridor)
    try:
        with pytest.raises(vs_screens.ReviewHoldStop, match=r"DEFECT \(keel-cloud 233\): solution.compatibility's "
                                                            r"Check held on \*Keel is reading your answers\* past 1 s"):
            cs._check_screen(j, {"dimension": COMPAT, "saves": {"maxWords": 16}}, COMPAT)
    finally:
        page.close()
    assert [s["slug"] for s in cam.founder_shots] == [f"check-{COMPAT}"]
    assert [s["slug"] for s in cam.failure_shots] == [f"failed-check-{COMPAT}-held"]
    assert j.findings[0]["what"].startswith("DEFECT (keel-cloud 233)")
    assert j.review_holds[COMPAT]["outcome"] == "timeout" and j.review_holds[COMPAT]["review"] == INTERACTION


def test_the_lists_that_hold_are_the_three():
    """FR-1: Importance, Current solution and Compatibility save through the hold; every other list as before."""
    assert all(vs.is_list(k) for k in vs_screens.REVIEWED_LISTS)
    assert bt.REVIEWED_SUFFIX == vs_screens.REVIEWED_SUFFIX
    assert vs_screens.reviewed_slug(COMPAT) == "check-solution.compatibility-reviewed"
    assert vs_screens.unreviewed("check-solution.compatibility-reviewed") == "check-solution.compatibility"
    assert vs_screens.unreviewed("problem.importance") == "problem.importance"
    assert vs_screens._sent_picks({"body": {"answers": [{"dimension": COMPAT, "list": {"pickedIndex": 0}}]}}, COMPAT)
    assert not vs_screens._sent_picks({"body": {"answers": [{"dimension": COMPAT, "list": {}}]}}, COMPAT)


def test_the_second_shot_is_its_dimensions_in_the_bundle(browser, tmp_path):
    """FR-1: the second shot goes into `backtest.json`'s founder screens with its `review`, the founder's answer (read
    the band, pressed Continue, nothing put back) and Keel's read-back of its dimension (the *Keel will test* box as the
    review left it); the hold is recorded per list and said in `backtest.md`."""
    page, corridor, cam, _ = _walk(browser, tmp_path, "changed")
    try:
        seen = corridor.list_check({"dimension": COMPAT, "saves": {"maxWords": 16}})
    finally:
        page.close()
    answer = vs.CalibrationAnswer(COMPAT, {"dimension": COMPAT, "list": {"items": [{"label": t} for t in TYPED],
                                                                         "pickedIndex": 0}}, "typed")
    j = SimpleNamespace(founder=SimpleNamespace(calibration={"SOLUTION": [answer]}), framing={COMPAT: [seen]},
                        review_holds={COMPAT: seen["review_hold"]}, review_picks={})
    wire = {"review/SOLUTION": {"rows": [{"dimension": COMPAT, "belief": "the wire's"}]}}
    screens = bt.founder_screens(j, cam, wire)
    assert [s["screen"] for s in screens] == [f"check-{COMPAT}", f"check-{COMPAT}-reviewed"]
    assert screens[1]["review"]["put_aside"] == [{"typed": TYPED[2], "why": SETTLED}]
    assert screens[1]["answer"].startswith("read what Keel changed after their Save") and \
        "pressed Continue to choose -- nothing put back, nothing edited" in screens[1]["answer"]
    assert screens[0]["answer"] == bt.CHECK_AS_DRAFTED
    assert isinstance(screens[1]["keel read back"], dict), "its dimension's read-back, never None"
    assert bt.read_back(j, f"check-{COMPAT}-reviewed", wire) == bt.read_back(j, f"check-{COMPAT}", wire)
    md = bt.markdown({"review_holds": j.review_holds, "respondents": {}, "founder_screens": []})
    assert (f"- The Save of {COMPAT}'s Check: held on *Keel is reading your answers* "
            f"{seen['review_hold']['held_s']} s, then stayed with the band (shot again, Continue pressed) "
            f"(review `{INTERACTION}`)") in md
    assert bt.review_hold_said({"held": False, "outcome": "moved", "review": None}) == \
        "no hold seen, then moved on (the answer named no review)"
