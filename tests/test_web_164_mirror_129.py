"""Spec 129 -- the harness follows keel-web 164 (the defects of cycles 7 and 8, the web's half).

What the walk reads as 164 draws it: the card's legend chip by chip joined with *·*, the median's word apart from the
tick row, the strip's own line (`bar-strip-people`), the stage kicker by its id (`stage-kicker`, *· N counted*), an
option drawn as a name over its line (`.fmt__name`, `.fmt__d`) read as the two apart; the walker presses the time box's
*I'm not sure* (`duration-unsure`, a button with `aria-pressed`); Purchase friction's Choose bar in the card's framing,
and a single question's intro naming the escape only where the chip is drawn. Read in Chromium against stand-ins.
"""

from __future__ import annotations

import json

import pytest
from playwright.sync_api import sync_playwright

from evals import backtest as bt
from evals import corpus_scenario as cs
from harness import vectors_screens as vs_screens
from harness.steps import Recorder
from quality import readers

BASE = "http://keel.test"
FRICTION = "commercial.purchase_friction"
FREQUENCY = "problem.frequency"


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


# -------------------------------------------------------------- W3 / W2 / W7: the stage page and a card, as read

#: keel-web 164's Frequency card on Voltair's stage page, as far as the leg reads it: the kicker by its id, the window
#: chart's ticks with the median's word under its tick, the legend's chips, the strip with its own line.
_STAGE_164 = """<main><div class="corridor answers" data-testid="stage-page" data-stage="PROBLEM">
<p class="corridor__kicker" data-testid="stage-kicker">The problem · 7 people answered · 3 to 7 counted</p>
<p class="answers__headline" data-testid="stage-verdict">Too few to call · Frequency: 3 counted</p>
<div class="dimrow" id="problem.frequency" data-testid="stage-dimension" data-dim="problem.frequency" data-opens="true"
  data-open="true"><button class="dimrow__head" data-testid="stage-dimension-open">open</button>
  <span class="dimrow__name">Frequency</span><span class="status" data-testid="dimension-verdict">Too few to call
  <span class="sub" data-testid="dimension-count">3 counted · 5 needed to call it</span></span>
  <div class="dimrow__body"><div class="dimrow__drawing" data-testid="dimension-chart">
  <div class="achart" data-chart="window-steps">
    <div class="achart__cellticks" style="display:grid;grid-template-columns:repeat(4,1fr)"><span>0</span><span>1</span>
    <span class="achart__tick--mid">2<span class="achart__midword" style="display:block">median</span></span><span>3</span></div>
    <div class="achart__caption"><span>days out of 3</span></div>
    <div class="achart__legend"><span><i class="achart__key"></i>at what you said</span>
    <span><i class="achart__key"></i>short of it</span></div></div>
  <div class="barstrip barstrip--people" data-testid="bar-strip" data-mode="cells" data-counted="3" data-bar="4">
    <p class="barstrip__people" data-testid="bar-strip-people">one cell per person · 3 counted · 2 empty until 5 are
    counted</p><p data-testid="bar-strip-label">your bar · 4 of 5 (at least 2 in 3)</p>
    <i class="barstrip__cell" data-side="FOR" data-kind="for"></i><i class="barstrip__cell" data-side="AGAINST"
    data-kind="against"></i><i class="barstrip__cell" data-side="FOR" data-kind="for"></i>
    <i class="barstrip__cell" data-side="GHOST" data-kind="ghost"></i><i class="barstrip__cell" data-side="GHOST"
    data-kind="ghost"></i></div></div></div></div></div></main>"""


def test_the_card_reads_the_legend_chip_by_chip_the_median_apart_and_the_strips_own_line(browser):
    page = browser.new_page()
    try:
        page.set_content(_STAGE_164)
        stage = page.evaluate(bt.STAGE_JS)["page"]
        card = page.evaluate(bt.CARD_JS, FREQUENCY)
        midword_display = page.evaluate("() => document.querySelector('.achart__midword').style.display")
    finally:
        page.close()
    assert stage["kicker"] == "The problem · 7 people answered · 3 to 7 counted"
    chart = card["chart"]
    assert chart["legend"] == "at what you said · short of it", "164 W3: never 'at what you said short of it'"
    assert chart["midwords"] == [{"tick": "2", "word": "median"}]
    assert "median" not in chart["drawing"] and "2" in chart["drawing"]
    assert "one cell per person" not in chart["drawing"] and "your bar" not in chart["drawing"], \
        "the strip is read apart, never run on from the chart's words"
    assert midword_display == "block", "the page is put back as it was drawn"
    strip = chart["strips"][0]
    assert strip["people"] == "one cell per person · 3 counted · 2 empty until 5 are counted"
    assert strip["label"] == "your bar · 4 of 5 (at least 2 in 3)" and strip["sides"]["GHOST"] == 2
    assert "median" in card["text"], "the card's own text stays as drawn, in order"
    body, _ = readers._after_body({"kind": "dimension", "n": 2, "stage": "PROBLEM", "dimension": FREQUENCY,
                                   "chart": chart}, 3)
    said = "\n".join(body)
    assert "The chart's legend: at what you said · short of it" in said
    assert "Under the tick 2 on the chart's tick row: median" in said
    assert "its own line: one cell per person · 3 counted · 2 empty until 5 are counted; your bar · 4 of 5" in said


def test_a_stage_page_before_164_reads_the_kicker_by_its_class(browser):
    page = browser.new_page()
    try:
        page.set_content(_STAGE_164.replace(' data-testid="stage-kicker"', "")
                         .replace("The problem · 7 people answered · 3 to 7 counted", "The problem · 7 people answered"))
        stage = page.evaluate(bt.STAGE_JS)["page"]
    finally:
        page.close()
    assert stage["kicker"] == "The problem · 7 people answered"


# ------------------------------------------------------------------------- W4: a name over its line, read apart

_SEND_WHO = """<main><div role="dialog"><h2>Who are you sending this to?</h2><div role="radiogroup">
<button role="radio" aria-checked="true"><span class="fmt__t"><span class="fmt__name">People I know by name</span>
<span class="fmt__d">I send each one their own link.</span></span></button>
<button role="radio" aria-checked="false"><span class="fmt__t"><span class="fmt__name">Anyone with the link</span>
</span></button>
<button role="radio" aria-checked="false">A plain option</button></div></div></main>"""


def test_an_option_drawn_as_a_name_over_its_line_is_read_as_the_two_apart(browser):
    page = browser.new_page()
    try:
        page.set_content(_SEND_WHO)
        read = page.evaluate(bt.READ_JS)
    finally:
        page.close()
    assert read["options"] == ["People I know by name -- I send each one their own link.", "Anyone with the link",
                               "A plain option"]


# ------------------------------------------------------------------ W6 / W8: the time box's not sure, the bar

#: keel-web 164's Purchase friction Choose, as far as the walker reads it: the radios, then (once a step is picked) the
#: time box with its count, its unit and *I'm not sure* (`duration-unsure`, `aria-pressed`), and the *Keel will test*
#: box whose bar is `purchaseFrictionBar(true, said)`.
_CHOOSE_164 = """<!doctype html><html><head><meta charset="utf-8"></head><body><div id="app"></div><script>
const O = %(opts)s;
let pick = null, count = '', unit = 'WEEKS', unsure = false;
const words = {DAYS: ['day', 'days'], WEEKS: ['week', 'weeks'], MONTHS: ['month', 'months']};
const pid = location.pathname.split('/')[2];
function bar() {
  if (unsure) return 'Holds if at least 2 in 3 say quick or not needed.';
  const n = parseInt(count, 10);
  return n > 0 ? `Holds if at least 2 in 3 say under ${n} ${words[unit][n === 1 ? 0 : 1]} or not needed.`
               : 'Holds if at least 2 in 3 say under your time or not needed.';
}
function paint() { document.querySelector('.keeltest__b').textContent = bar(); }
function render() {
  const app = document.getElementById('app');
  if (/\\/next$/.test(location.pathname)) { app.innerHTML = '<main><h1>Next</h1></main>'; return; }
  const radios = O.rows.map((r, i) => `<button type="button" role="radio" aria-checked="${pick === i}" data-i="${i}">${r}</button>`).join('');
  const box = pick === null ? '' : `<div data-testid="duration-input"><p class="calib__durationq">How long do you expect this step to take?</p>
    <input data-testid="duration-count" value="${count}"><select data-testid="duration-unit">
    <option value="DAYS">days</option><option value="WEEKS" ${unit === 'WEEKS' ? 'selected' : ''}>weeks</option>
    <option value="MONTHS">months</option></select>
    ${O.chip ? `<button type="button" class="calib__chip" data-testid="duration-unsure" aria-pressed="${unsure}">I'm not sure</button>` : ''}</div>`;
  app.innerHTML = `<main class="corridor"><p class="corridor__intro">${O.intro}</p><section class="ccard"><div class="ccard__body">
    <div class="listcheck"><p class="listcheck__title" id="t">Which one do you want to test?</p>
    <div role="radiogroup" aria-labelledby="t">${radios}</div></div>${box}
    <div class="keeltest"><p class="keeltest__t">${pick === null ? 'Pick one and the test appears here.' : O.rows[pick] + ' can slow or stop the purchase.'}</p>
      <p class="keeltest__b"></p></div></div>
    <div class="ccard__foot"><button type="button" class="btn primary" ${pick === null ? 'disabled' : ''}>Continue</button></div>
    </section></main>`;
  paint();
  app.querySelectorAll('[role=radio]').forEach((b) => b.addEventListener('click', () => { pick = Number(b.dataset.i); render(); }));
  const c = app.querySelector('[data-testid=duration-count]');
  if (c) c.addEventListener('input', () => { count = c.value; unsure = false; paint();
    const u = app.querySelector('[data-testid=duration-unsure]'); if (u) u.setAttribute('aria-pressed', 'false'); });
  const s = app.querySelector('[data-testid=duration-unit]');
  if (s) s.addEventListener('change', () => { unit = s.value; paint(); });
  const u = app.querySelector('[data-testid=duration-unsure]');
  if (u) u.addEventListener('click', () => { unsure = !unsure; count = ''; render(); });
  app.querySelector('.btn.primary').addEventListener('click', async () => {
    const list = {items: O.rows.map((label) => ({label})), pickedIndex: pick};
    if (!unsure && count) list.duration = {count: parseInt(count, 10), unit};
    const r = await fetch(`/v2/projects/${pid}/calibration/COMMERCIAL`, {method: 'PUT',
      headers: {'content-type': 'application/json'}, body: JSON.stringify({answers: [{dimension: O.dim, list}]})});
    await r.json(); history.pushState({}, '', `/p/${pid}/next`); render();
  });
}
render();
</script></body></html>"""

ROWS = ["A data protection review of guest calls", "A trial at one hotel first"]


def _choose(browser, tmp_path, duration, **opts):
    page = browser.new_page()
    screen = {"intro": vs_screens.PURCHASE_FRICTION_CHOOSE_INTRO, "rows": ROWS, "dim": FRICTION, "chip": True, **opts}
    sent: list = []

    def serve(route):
        if route.request.method == "PUT":
            sent.append(route.request.post_data_json)
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"revision": 2}))
        else:
            route.fulfill(status=200, content_type="text/html", body=_CHOOSE_164 % {"opts": json.dumps(screen)})
    page.route(f"{BASE}/**", serve)
    page.goto(f"{BASE}/p/p1/define/COMMERCIAL/q/4/choose", wait_until="load")
    try:
        corridor = vs_screens.Corridor(page, Recorder(tmp_path), BASE)
        corridor.camera = lambda slug: None
        return corridor.list_choose({"dimension": FRICTION}, ROWS[1], duration=duration), sent
    finally:
        page.close()


def test_the_walker_presses_not_sure_and_the_bar_says_quick_or_not_needed(browser, tmp_path):
    seen, sent = _choose(browser, tmp_path, {"unsure": True, "count": 4, "unit": "WEEKS"})
    assert seen["duration_unsure"] == "ticked" and seen["duration"] is None
    assert seen["test_before"]["bar"] == vs_screens.PURCHASE_FRICTION_CHOOSE_BAR_YOUR_TIME
    assert seen["test"]["bar"] == "Holds if at least 2 in 3 say quick or not needed."
    assert "duration" not in sent[0]["answers"][0]["list"], "the pick is sent with no time"
    assert cs.said_faults(seen, FRICTION, b2b=True) == []


def test_a_time_typed_reads_under_that_time(browser, tmp_path):
    seen, sent = _choose(browser, tmp_path, {"count": 6, "unit": "WEEKS"})
    assert "duration_unsure" not in seen and seen["duration"] == {"count": "6", "unit": "WEEKS"}
    assert seen["test"]["bar"] == "Holds if at least 2 in 3 say under 6 weeks or not needed."
    assert sent[0]["answers"][0]["list"]["duration"] == {"count": 6, "unit": "WEEKS"}
    assert cs.said_faults(seen, FRICTION, b2b=True) == []
    moved = {**seen, "test": {**seen["test"], "bar": vs_screens.PURCHASE_FRICTION_CHOOSE_BAR_157}}
    assert [f["what"] for f in cs.said_faults(moved, FRICTION, b2b=True)] == ["the bar after the pick"], \
        "157's *longer than you expect* is a fault on a 164 page"


def test_a_page_before_164_draws_no_not_sure_and_the_walker_types_its_default(browser, tmp_path):
    seen, _ = _choose(browser, tmp_path, {"unsure": True, "default": True, "count": 2, "unit": "WEEKS"}, chip=False)
    assert seen["duration_unsure"] == "not drawn, default typed"
    assert seen["duration"] == {"count": "2", "unit": "WEEKS"}


def test_the_bar_mirrors_purchase_friction_bar():
    bar = vs_screens.purchase_friction_choose_bar
    assert bar(False) == bar(False, "6 weeks") == bar(True, None) == vs_screens.PURCHASE_FRICTION_CHOOSE_BAR_UNDATED
    assert bar(True) == "Holds if at least 2 in 3 say under your time or not needed."
    assert bar(True, vs_screens.duration_said({"count": 1, "unit": "MONTHS"})) == (
        "Holds if at least 2 in 3 say under 1 month or not needed.")
    assert vs_screens.duration_said({"count": "", "unit": "WEEKS"}) == "" and vs_screens.duration_said(None) == ""


# ------------------------------------------------------------------------ W5: the intro's escape, where drawn

INTRO = "Let's turn your problem belief into something we can test. Four short questions."


@pytest.mark.parametrize("question, intro, faults", [
    ({"control": "single_choice", "unsureAllowed": False}, INTRO, []),
    ({"control": "single_choice", "unsureAllowed": False},
     INTRO + ' Pick "I\'m not sure" and Keel leaves that dimension out of the study.', ["the intro's escape"]),
    ({"control": "numeric_interval", "unsureAllowed": True},
     INTRO + ' Pick "I\'m not sure" and Keel leaves that dimension out of the study.', []),
    ({"control": "price_range", "unsureAllowed": True},
     'Five short questions about paying. Pick "No price yet" and Keel leaves that dimension out of the study.', []),
    ({"control": "price_range", "unsureAllowed": True},
     'Five short questions about paying. Pick "I\'m not sure" and Keel leaves that dimension out of the study.',
     ["the intro's escape"]),
    ({"control": "numeric_interval", "unsureAllowed": True}, INTRO, ["the intro's escape"])])
def test_a_single_questions_intro_names_the_escape_only_where_the_chip_is(question, intro, faults):
    seen = {"screen": "single", "intro": intro, "chip_served": vs_screens.unsure_chip_of(question)}
    assert [f["what"] for f in cs.said_faults(seen, "problem.prevalence", b2b=False)] == faults
    assert cs.said_faults({"screen": "single", "intro": None, "chip_served": None}, "problem.prevalence",
                          b2b=False) == [], "a locked stage draws no intro"
