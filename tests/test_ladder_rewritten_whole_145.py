"""Spec 145 FR-3 -- the walk on a ladder the review rewrote whole (keel-cloud 235 FR-7, Codyco's five as its tasks.md
serves them: rungs 3-5 rewritten onto *how soon a missed call was called back*, the founder's words behind Put back;
rungs 1 and 2 -- the founder's leading rungs, 064 FR-5a's kept verbatim -- untouched).

Nothing new is built for it: a rewritten rung counts present by its `typed` (143 FR-2), the walk never presses Put back
and never retypes a changed rung, it waits out the Save's hold (both of 235's read-back turns run inside it) and shoots
`check-{dim}-reviewed` after the band (144 FR-1). These tests pin that on 235's ladder.

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
from tests.test_cloud_235_mirror_145 import CS, LADDER, MEASURE, RUNGS_SERVED, RUNGS_TYPED, SCALE_LINE, WHY

BASE = "http://keel.test"
CHECK_URL = f"{BASE}/projects/p1/define/problem/q/4/check"
PUT_URL = f"{BASE}/v2/projects/p1/calibration/PROBLEM"
INTERACTION = "3a1d5c2e-2350-4a35-9235-0000000000a5"
BAND = SCALE_LINE.format(measure=MEASURE)
QUESTION = {"dimension": CS, "saves": {"maxItems": 5, "maxWords": 9}, "draft": None, "answer": {"list": LADDER}}


@pytest.fixture
def founders_five(monkeypatch):
    """The entry's five rungs as the founder saved them (cycle 16's Codyco), for the walk's plan."""
    monkeypatch.setattr(vs, "founder_list", lambda entry, key: {"items": [{"label": r} for r in RUNGS_TYPED],
                                                                "phrase": LADDER["phrase"]})
    monkeypatch.setattr(cs, "_step", _no_step)


class _no_step:
    def __init__(self, *a, **k):
        self.h = SimpleNamespace(record_assert=lambda *x, **y: None)

    def __enter__(self):
        return self.h

    def __exit__(self, *exc):
        return False


# ------------------------------------------------------------------------------- the strict rung checks, by `typed`

def test_every_founder_rung_is_present_by_typed(founders_five):
    """143 FR-2 on 235's ladder: the three rewritten rungs are the founder's by their `typed`; the two leading rungs
    (064 FR-5a) are served verbatim, untouched."""
    assert vs.missing_rows(RUNGS_TYPED, LADDER) == []
    assert vs.held_by_review(RUNGS_TYPED, LADDER) == RUNGS_TYPED[2:]
    assert [i["label"] for i in LADDER["items"][:2]] == RUNGS_TYPED[:2]
    assert not any(i.get("typed") for i in LADDER["items"][:2]), "the leading rungs typed, kept verbatim"
    assert vs.founder_words(LADDER) == RUNGS_TYPED


def test_the_rungs_plan_types_over_no_rewritten_rung(founders_five):
    """064 FR-5a / 067 FR-2: off the wire (`typed_by_label`) no rung is planned over; without the review's `typed` the
    same served rows would be three edits -- the check bites."""
    assert vs.rungs_plan(None, RUNGS_SERVED, 5, vs.typed_by_label(LADDER)) == {"edit": [], "add": [], "cannot": []}
    assert vs.rungs_plan(None, RUNGS_SERVED, 5)["edit"] == [(2, RUNGS_TYPED[2]), (3, RUNGS_TYPED[3]),
                                                            (4, RUNGS_TYPED[4])]


def test_the_walk_reads_the_was_lines_when_the_wire_says_nothing(founders_five):
    """The Check's *Was:* lines alone (keel-web 179) hold the three rungs as the founder's -- no edit, no finding."""
    j = SimpleNamespace(entry=None, findings=[])
    drawn = {"rows": [{"text": i["label"], **({"was": i["typed"]} if i.get("typed") else {})}
                      for i in LADDER["items"]]}
    assert cs._rungs_to_type(j, {**QUESTION, "answer": None}, drawn) == {"edit": [], "add": [], "cannot": []}
    assert cs._rungs_to_type(j, QUESTION, {"rows": [{"text": r} for r in RUNGS_SERVED]})["edit"] == []
    assert j.findings == []


def test_the_stored_ladder_is_the_founders_as_saved(founders_five):
    """The strict stored-list check: read back to the founder's words the ladder is their five, the phrase standing; a
    rewritten rung over the 9-word cap would be a defect to file -- none here."""
    want = {"items": [{"code": f"outcome_{n + 1}", "label": r} for n, r in enumerate(RUNGS_TYPED)],
            "pickedIndex": None, "phrase": LADDER["phrase"]}
    assert cs.reviewed_as_saved(want, LADDER)
    assert vs.changed_over_cap(LADDER, 9) == []
    j = SimpleNamespace(findings=[])
    assert cs.review_defects(j, CS, LADDER, 9) == [] and j.findings == []


# -------------------------------------------------------------------------------------- the walk on the Check page

_PAGE = """<!doctype html><html><body><main><div class="ccard calib"><div class="ccard__body">
<p class="corridor__kicker">Problem</p><div id="band"></div>
<div class="listcheck"><p class="listcheck__title">Check</p><ul class="listrows" id="rows">%(drafted)s</ul></div>
<div id="status"></div></div>
<div class="ccard__foot"><button class="btn primary" id="primary">Save</button></div></div></main>
<script>
window.putBacks = 0;
document.addEventListener("click", (e) => {
  if (e.target.dataset && e.target.dataset.testid === "row-put-back") window.putBacks += 1;
});
const primary = document.getElementById("primary");
function moveOn(to) { history.pushState({}, "", to); document.querySelector("main").innerHTML = "<p>next</p>"; }
function rewritten() {
  document.getElementById("status").innerHTML = "";
  document.getElementById("band").innerHTML = '<div class="calib__changed" role="status" data-testid="list-changed">'
    + '<p class="calib__changed-line">%(band)s</p><p class="calib__changed-why">%(why)s</p></div>';
  document.getElementById("rows").innerHTML = %(reviewed)s;
  primary.textContent = "Continue";
  primary.disabled = false;
  primary.onclick = () => moveOn("/projects/p1/define/problem/q/5");
}
primary.onclick = async () => {
  const answer = await (await fetch("/v2/projects/p1/calibration/PROBLEM",
    {method: "PUT", headers: {"Content-Type": "application/json"}, body: JSON.stringify({expectedRevision: 7})})).json();
  if (!answer.review) { moveOn("/projects/p1/define/problem/q/5"); return; }
  primary.disabled = true;
  primary.textContent = "Keel is reading your answers";
  document.getElementById("status").innerHTML =
    '<p class="calib__drafting calib__reviewing" role="status" data-testid="list-reviewing">Keel is reading your answers</p>';
  // keel-cloud 235 FR-3: the first answer refused, one more turn on the same interaction -- both inside the hold
  setTimeout(rewritten, 1200);
};
</script></body></html>"""


def _row(label: str, was: str | None = None, why: str | None = None) -> str:
    if was is None:
        return (f'<li class="listrow"><div class="listrow__line"><textarea class="listrow__ed">{label}</textarea>'
                f'<span class="listrow__wc">{len(label.split())} / 9</span></div></li>')
    return (f'<li class="listrow"><div class="listrow__line"><textarea class="listrow__ed">{label}</textarea>'
            '<span class="listrow__tag listrow__tag--changed" data-testid="row-changed">changed</span></div>'
            f'<p class="listrow__warn listrow__warn--why" role="note" data-testid="row-why">{why}</p>'
            '<p class="listrow__was" data-testid="row-was"><span class="listrow__was-k">Was:</span> '
            f'<span class="listrow__was-said">{was}</span><button type="button" data-testid="row-put-back">Put back'
            '</button></p></li>')


def _html() -> str:
    reviewed = "".join(_row(i["label"], i.get("typed"), i.get("why")) for i in LADDER["items"])
    return _PAGE % {"drafted": "".join(_row(r) for r in RUNGS_TYPED), "band": BAND, "why": WHY[0],
                    "reviewed": json.dumps(reviewed)}


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def test_the_walk_saves_waits_out_both_turns_shoots_the_band_and_never_puts_back(browser, tmp_path, founders_five):
    """144 FR-1 on 235's ladder: the Check drawn with the founder's five (nothing to type), Save; the hold waited out
    (235's two turns inside it); the Check stays with the scale's band and three changed rungs; read and shot again
    (`check-{CS}-reviewed`); Continue pressed; Put back never pressed, no rung typed."""
    page = browser.new_page()
    put: list = []

    def handle(route):
        if route.request.url == PUT_URL:
            put.append(route.request.post_data_json)
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"revision": 8, "rows": [], "review": {"interactionId": INTERACTION}}))
        else:
            route.fulfill(status=200, content_type="text/html", body=_html())

    page.route(f"{BASE}/**", handle)
    page.goto(CHECK_URL)
    cam = bt.Camera(run_dir=tmp_path, page=page, watched={})
    corridor = vs_screens.Corridor(page, Recorder(tmp_path), BASE)
    corridor.camera = cam.founder
    j = SimpleNamespace(entry=None, strict=False, findings=[], review_holds={}, corridor=corridor)
    try:
        seen = cs._check_screen(j, QUESTION, CS)
        assert page.url.endswith("/q/5")
        assert page.evaluate("window.putBacks") == 0, "never Put back"
    finally:
        page.close()
    assert len(put) == 1, "one Save, nothing typed after the hold"
    assert "rungs_edited" not in seen and "rungs" not in seen, "no rung typed over or added"
    hold = seen["review_hold"]
    assert hold["review"] == INTERACTION and hold["held"] is True and hold["outcome"] == "stayed"
    assert hold["held_s"] >= 1.0, "the hold spans both turns"
    reviewed = seen["reviewed"]
    assert [r["text"] for r in reviewed["rows"]] == RUNGS_SERVED
    assert [r.get("was") for r in reviewed["rows"] if r.get("changed")] == RUNGS_TYPED[2:]
    assert reviewed["band"] == {"line": BAND, "why": WHY[0]}
    assert seen["continue"] == vs_screens.LIST_CONTINUE
    assert [s["slug"] for s in cam.founder_shots] == [f"check-{CS}", f"check-{CS}-reviewed"]
    second = cam.founder_shots[1]
    assert second["review"]["band"]["line"] == BAND
    assert [c["was"] for c in second["review"]["changed"]] == RUNGS_TYPED[2:]
    assert j.findings == []
    # the record reads the hold and the scale off what this walk wrote
    from quality import cycle                                                    # noqa: PLC0415
    assert cycle.review_held({CS: hold}) == {CS: {"held_s": hold["held_s"], "outcome": "stayed"}}
    assert cycle.review_scales({CS: {"band": reviewed["band"]}}) == 1
