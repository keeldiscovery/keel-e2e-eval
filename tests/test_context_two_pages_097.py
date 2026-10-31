"""Spec 097 (keel-web 141): the context walker turns two pages -- the four fields and *Continue* on 1 of 2, then the
recall window's own page at `define/context/window`, nothing pre-filled, the entry's window picked there (the chip that
names it, else the count and the unit) and *Save and continue*; money alone keeps the one screen.

FR-1: `Corridor.context` walked in Chromium against a page shaped as keel-web 141's `ContextStep` (the two screens on
one document, the URL moved by the history API as react-router does), its selectors held to keel-web's source. FR-2:
`Corridor.context_confirmed` reads the saved window on 2 of 2 after Edit's *Continue*. FR-3: the back-test's founder
screens and the readers' screen kinds gain `context-window`.
"""

from __future__ import annotations

import json
import re
from types import SimpleNamespace

import pytest
from playwright.sync_api import sync_playwright

from evals import backtest as bt
from evals import corpus_scenario as cs
from harness import vectors_screens as vs_screens
from harness.steps import Recorder
from quality import decisions as dec
from quality import table
from stack.config import load_config

BASE = "http://keel.test"
FIELDS = {"actor": "Restaurant managers", "job": "check the delivery against the invoice",
          "circumstance": "a delivery does not match the invoice", "segment": "Restaurant managers in the US"}
SENTENCE = "Restaurant managers in the US. When a delivery does not match, they want to check it."


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


#: keel-web 141's `ContextStep`, as far as the walker reads it: the root's state and screen, the counter, 1 of 2's four
#: boxes and Continue, 2 of 2's question, chips, count, unit (on *Choose*), Back and Save; the wait and the card at
#: `define/context`; re-opened confirmed, the sentence, *Continue to the problem* and Edit.
_PAGE = """<!doctype html><html><body><div id="app"></div><script>
const S = window.__S = Object.assign({fields: {actor: '', job: '', circumstance: '', segment: ''}, count: '', unit: '',
                                      stage: 'form', put: null}, %(state)s);
const GATE = %(gate)s;
const CHIPS = [[7, 'NIGHTS', '7 nights'], [7, 'DAYS', '7 days'], [5, 'WORKING_DAYS', '5 working days'],
               [30, 'DAYS', '30 days']];
const UNITS = [['NIGHTS', 'nights'], ['DAYS', 'days'], ['WORKING_DAYS', 'working days'], ['WEEKS', 'weeks'],
               ['MONTHS', 'months']];
const base = location.pathname.replace(/\\/window\\/?$/, '');
const onWindow = () => GATE && S.stage === 'form' && /\\/define\\/context\\/window\\/?$/.test(location.pathname);
const go = (path) => { history.pushState({}, '', path); render(); };
const boxes = () => ['actor', 'job', 'circumstance', 'segment'].map((k) =>
  `<div class="cfield"><textarea id="context-${k}" class="cfield__input" data-k="${k}"></textarea></div>`).join('');
const windowControls = () => `<div class="cwindow"><div class="cwindow__presets">` + CHIPS.map(([c, u, w], i) =>
  `<button type="button" class="cwindow__chip" data-i="${i}" aria-pressed="${String(S.count) === String(c)
    && S.unit === u}">${w}</button>`).join('') + `</div><input class="cwindow__count" value="${S.count}">
  <select class="cwindow__unit">` + (S.unit === '' ? '<option value="" disabled selected>Choose</option>' : '')
  + UNITS.map(([u, w]) => `<option value="${u}" ${S.unit === u ? 'selected' : ''}>${w}</option>`).join('')
  + `</select></div>`;
function render() {
  const app = document.getElementById('app');
  const win = onWindow();
  const screen = GATE && S.stage === 'form' ? (win ? 'window' : 'fields') : null;
  let body = '', foot = '';
  if (S.stage === 'confirmed') {
    body = `<div class="understands" data-testid="context-understood"><p class="understands__big">${S.big}</p>
      <p class="understands__window">Counting the last ${S.count} ${S.unit.toLowerCase()}.</p></div>`;
    foot = `<button class="btn primary">Continue to the problem</button>
      <button class="btn" data-testid="context-edit">Edit</button>`;
  } else if (S.stage === 'wait') {
    body = `<div class="waitco-block"><p class="cnote" role="status">Keel is reading your four answers.</p>
      <div class="waitco"><span class="waitco__elapsed">0:01</span><div class="phasebar"></div><div class="truth">
      </div></div></div>`;
  } else if (S.stage === 'card') {
    body = `<div class="understands"><p class="understands__big">${S.big}</p><div class="actions cbtns">
      <button class="btn primary">Yes, that's it</button><button class="btn">Edit</button></div></div>`;
  } else if (win) {
    body = `<section data-testid="context-window-page"><h1 class="ccard__title" id="context-window-label">How recent
      should an episode be to count?</h1>${windowControls()}</section>`;
    foot = `<button class="btn" data-testid="context-back">Back</button>
      <button class="btn primary" data-testid="context-save">Save and continue</button>`;
  } else {
    body = `<h1 class="ccard__title">Who it's for</h1><div class="cfields">${boxes()}</div>`;
    foot = GATE ? `<button class="btn primary" data-testid="context-continue">Continue</button>`
                : `<button class="btn primary" data-testid="context-save">Save and continue</button>`;
  }
  const state = S.stage === 'confirmed' ? 'confirmed' : S.stage;
  app.innerHTML = `<div data-testid="context-step" data-context-state="${state}"`
    + (screen ? ` data-context-screen="${screen}"` : '') + `>`
    + (screen ? `<p class="before__counter" data-testid="context-counter">${win ? 2 : 1} of 2</p>` : '')
    + `<div class="ccard"><div class="ccard__body">${body}</div>`
    + `<div class="cbtns ccard__foot">${foot}</div></div></div>`;
  app.querySelectorAll('textarea[data-k]').forEach((t) => { t.value = S.fields[t.dataset.k];
    t.addEventListener('input', () => { S.fields[t.dataset.k] = t.value; }); });
  const count = app.querySelector('input.cwindow__count');
  if (count) count.addEventListener('input', () => { S.count = count.value; });
  const unit = app.querySelector('select.cwindow__unit');
  if (unit) unit.addEventListener('change', () => { S.unit = unit.value; render(); });
  app.querySelectorAll('button.cwindow__chip').forEach((b) => b.addEventListener('click', () => {
    const [c, u] = CHIPS[Number(b.dataset.i)]; S.count = String(c); S.unit = u; render(); }));
  const cont = app.querySelector('[data-testid=context-continue]');
  if (cont) cont.addEventListener('click', () => go(base + '/window'));
  const edit = app.querySelector('[data-testid=context-edit]');
  if (edit) edit.addEventListener('click', () => { S.stage = 'form'; render(); });
  const save = app.querySelector('[data-testid=context-save]');
  if (save) save.addEventListener('click', async () => {
    const sent = Object.assign({}, S.fields);
    if (GATE) sent.recallWindow = {count: Number(S.count), unit: S.unit};
    const pid = location.pathname.split('/')[2];
    const r = await fetch(`/v2/projects/${pid}/context`, {method: 'PUT', body: JSON.stringify(sent),
                                                            headers: {'content-type': 'application/json'}});
    await r.json();
    S.stage = 'wait'; history.replaceState({}, '', base); render();
    setTimeout(() => { S.stage = 'card'; S.big = %(sentence)s; render(); }, 80);
  });
}
render();
</script></body></html>"""


def _page(browser, *, gate: bool, state: dict | None = None):
    page = browser.new_page()
    sent: list = []

    def serve(route):
        if route.request.method == "PUT":
            sent.append(route.request.post_data_json)
            route.fulfill(status=202, content_type="application/json", body=json.dumps({"interaction_id": "i1"}))
        else:
            route.fulfill(status=200, content_type="text/html",
                          body=_PAGE % {"gate": json.dumps(gate), "state": json.dumps(state or {}),
                                        "sentence": json.dumps(SENTENCE)})
    page.route(f"{BASE}/**", serve)
    return page, sent


def _walk(browser, tmp_path, window: dict | None, *, gate: bool = True):
    page, sent = _page(browser, gate=gate)
    try:
        corridor = vs_screens.Corridor(page, Recorder(tmp_path), BASE)
        drawn = corridor.context("p1", FIELDS, window)
        return corridor, drawn, sent, page.url
    finally:
        page.close()


# ---------------------------------------------------------------------------------- FR-1: the walker turns the page

@pytest.mark.parametrize("window, via", [({"count": 7, "unit": "NIGHTS"}, "chip"),
                                         ({"count": 4, "unit": "WEEKS"}, "count and unit")])
def test_the_walker_fills_the_fields_continues_and_picks_the_window_on_its_own_page(browser, tmp_path, window, via):
    corridor, drawn, sent, url = _walk(browser, tmp_path, window)
    assert drawn == SENTENCE and url == f"{BASE}/p/p1/define/context"
    assert corridor.window_drawn is True
    page = corridor.window_page
    assert page["via"] == via
    assert page["drawn"] == {"count": "", "unit": "", "chips": ["7 nights", "7 days", "5 working days", "30 days"],
                             "pressed": [], "screen": "window", "counter": "2 of 2",
                             "question": "How recent should an episode be to count?", "back": "Back"}
    assert (page["picked"]["count"], page["picked"]["unit"]) == (str(window["count"]), window["unit"])
    assert page["picked"]["pressed"] == (["7 nights"] if via == "chip" else [])
    assert cs.window_page_faults(page, window) == []
    assert sent == [{**FIELDS, "recallWindow": window}]
    assert corridor.saves[0]["status"] == 202 and corridor.saves[0]["interaction_id"] == "i1"


def test_the_form_row_spans_both_screens_and_the_states_hold(browser, tmp_path):
    """The tracker is installed on 1 of 2: its four boxes and 2 of 2's Save are one form row, then the wait and the
    card -- 113's states unchanged."""
    corridor, drawn, _, _ = _walk(browser, tmp_path, {"count": 7, "unit": "NIGHTS"})
    states = corridor.context_states[-1]
    assert [s["state"] for s in states] == ["form", "wait", "card"]
    assert states[0] == {"state": "form", "boxes": 4, "save": 1, "fields_screen": True, "window_screen": True}
    assert cs.context_states_faults(states, drawn) == []


def test_money_alone_keeps_the_one_screen_and_draws_no_window(browser, tmp_path):
    corridor, drawn, sent, _ = _walk(browser, tmp_path, None, gate=False)
    assert drawn == SENTENCE
    assert corridor.window_drawn is False and corridor.window_page is None
    assert sent == [FIELDS]
    states = corridor.context_states[-1]
    assert states[0] == {"state": "form", "boxes": 4, "save": 1, "fields_screen": False, "window_screen": False}
    assert cs.context_states_faults(states, drawn) == []


def test_a_window_page_on_a_study_with_no_gate_is_recorded_not_waited_out(browser, tmp_path):
    corridor, drawn, sent, _ = _walk(browser, tmp_path, None, gate=True)
    assert drawn == "" and sent == [] and corridor.window_drawn is True
    assert corridor.saves[-1]["status"] is None and "no gate" in corridor.saves[-1]["error"]


def test_the_step_says_which_path():
    import inspect
    source = inspect.getsource(vs_screens.Corridor.context)
    assert "Continue, then the recall window on its own page" in source
    assert "and Save on its one screen -- no recall window (money alone)" in source


_WINDOW = {"count": 4, "unit": "WEEKS"}
_GOOD = {"drawn": {"count": "", "unit": "", "pressed": [], "screen": "window", "counter": "2 of 2"},
         "picked": {"count": "4", "unit": "WEEKS"}, "via": "count and unit"}


@pytest.mark.parametrize("fault", [
    lambda p: p["drawn"].update(count="7"),                         # the count pre-filled
    lambda p: p["drawn"].update(unit="NIGHTS"),                     # the unit pre-picked
    lambda p: p["drawn"].update(pressed=["7 nights"]),              # a chip pressed before the pick
    lambda p: p["drawn"].update(counter="1 of 2"),                  # the counter not 2 of 2
    lambda p: p["drawn"].update(screen="fields"),                   # the root names another screen
    lambda p: p["picked"].update(count="5"),                        # the pick left another count
    lambda p: p["picked"].update(unit="DAYS"),                      # ... another unit
    lambda p: p.clear(),                                            # no window page at all
])
def test_each_window_page_not_as_keel_web_141_draws_it_is_a_fault(fault):
    page = json.loads(json.dumps(_GOOD))
    assert cs.window_page_faults(page, _WINDOW) == []
    fault(page)
    assert cs.window_page_faults(page or None, _WINDOW)


# ------------------------------------------------------------------------------ FR-2: Edit and the saved window

def test_edit_opens_1_of_2_filled_and_continue_reads_the_saved_window(browser, tmp_path):
    page, sent = _page(browser, gate=True, state={"stage": "confirmed", "fields": FIELDS, "count": "4",
                                                  "unit": "WEEKS", "big": SENTENCE})
    try:
        seen = vs_screens.Corridor(page, Recorder(tmp_path), BASE).context_confirmed("p1")
        url = page.url
    finally:
        page.close()
    assert seen["state"] == "confirmed" and seen["understands"] == SENTENCE and seen["boxes"] == 0
    assert seen["edited"] == {"state": "form", "fields": FIELDS, "occasion": None, "screen": "fields",
                              "continue": vs_screens.CONTINUE, "window": _WINDOW, "save": vs_screens.CONTEXT_SAVE}
    assert url == f"{BASE}/p/p1/define/context/window" and sent == []       # nothing saved


def test_the_reopened_leg_owes_continue_to_the_window_page():
    import inspect
    source = inspect.getsource(cs.context_reopened)
    assert '"continue": vs_screens.CONTINUE' in source and '("fields", vs_screens.CONTINUE)' in source


# -------------------------------------------------------------------------- FR-3: the founder screens of record

def test_the_window_page_is_a_founder_screen_the_readers_score():
    assert "context-window" in dec.FOUNDER_SCREENS and "context-window" in dec.SCREENS
    assert dec.FOUNDER_SCREENS.index("context") < dec.FOUNDER_SCREENS.index("context-window") \
        < dec.FOUNDER_SCREENS.index("context-card")
    assert table.fix_location("founder", "context-window", None)[0] == "no model"


def test_the_back_test_answers_each_context_screen_with_what_was_typed_there():
    founder = SimpleNamespace(context_fields=FIELDS, window=SimpleNamespace(as_wire=lambda: _WINDOW), calibration={})
    two = SimpleNamespace(founder=founder, corridor=SimpleNamespace(window_page={"via": "chip"}))
    one = SimpleNamespace(founder=founder, corridor=SimpleNamespace(window_page=None))
    assert bt.founder_answer(two, "context") == FIELDS
    assert bt.founder_answer(two, "context-window") == {"recall window": _WINDOW, "picked with": "chip"}
    assert bt.founder_answer(one, "context") == {**FIELDS, "recall window": _WINDOW}
    wire = {"context": {"understands": SENTENCE}}
    assert bt.read_back(two, "context-window", wire) == {"understands": SENTENCE}


# ------------------------------------------------------------------------------ keel-web 141's own selectors

def _web_141() -> tuple[str, str]:
    web = load_config(validate=False).keel_web
    step = web / "src/components/corridor/ContextStep.tsx"
    if not step.is_file():
        pytest.skip("keel-web has no ContextStep.tsx")
    text = step.read_text(encoding="utf-8")
    if "context-window-page" not in text:
        pytest.skip("keel-web predates spec 141 (the recall window on the context form)")
    return text, (web / "src/lib/translate.ts").read_text(encoding="utf-8")


@pytest.mark.parametrize("needle", ['data-testid="context-continue"', 'data-testid="context-window-page"',
                                    'data-testid="context-save"', 'data-testid="context-back"',
                                    'data-testid="context-counter"', '"data-context-screen"', '"window" : "fields"',
                                    'className="cwindow__count"', 'className="cwindow__unit"',
                                    'className="cwindow__chip"', 'id="context-window-label"',
                                    "`${fieldsPath}/window`", "RECALL_WINDOW_UNIT_PLACEHOLDER", "BEFORE_COUNTER("])
def test_the_walkers_selectors_are_keel_web_141s(needle):
    step, _ = _web_141()
    assert needle in step, needle


def test_the_walkers_words_are_keel_web_141s():
    step, translate = _web_141()
    assert re.search(r'CONTINUE_LABEL = "Continue";', translate) and vs_screens.CONTINUE == "Continue"
    assert f'RECALL_WINDOW_UNIT_PLACEHOLDER = "{vs_screens.RECALL_UNIT_CHOOSE}";' in translate
    assert f'CONTEXT_SAVE_LABEL = "{vs_screens.CONTEXT_SAVE}";' in translate
    assert "BEFORE_COUNTER = (n: number, of = 3): string => `${n} of ${of}`" in translate
    assert re.search(r"/\\/define\\/context\\/window\\/\?\$/", step), "the window page's URL test"
    assert re.fullmatch(vs_screens.CONTEXT_WINDOW_PATH.replace("/?$", "/?"), "/define/context/window")
