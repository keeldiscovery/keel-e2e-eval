"""Spec 155 -- the harness waits as the founder does.

FR-1: `Corridor._wait_for_the_gate` before every corridor primary press -- while keel-web's gate line (*Keel is
finishing the previous step…*, keel-web 083 `CORRIDOR_WAITING`) is drawn the walk waits, at the page's cadence, up to
the step budget; a primary disabled with no line is a screen waiting for input and keeps today's limit and failure.
FR-2: a wait past `SLOW_SAVE_S` is a `gate_waits` row and a transcript note, the bundle carries the rows and
`backtest.md` one line under the Stack line; past the budget the walk stops naming the screen and the line. FR-3: the
wire's own wait stays. FR-4: real chromium on static pages drawn as keel-web draws them, budgets scaled down through
`patience` and the module's limits; no stack, no model. FR-5: the lock screen's shot is taken after `l1()` has waited
for the problem box and the plan's rows.
"""

from __future__ import annotations

import inspect
import json
import time
from pathlib import Path
from types import SimpleNamespace

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from evals import backtest as bt
from evals import corpus_scenario as cs
from harness import vectors_screens as vs
from harness.steps import Recorder

BASE = "http://keel.test"
KEEL_WEB_TRANSLATE = Path("/Users/athulrajeev/Documents/projects/keel-web/src/lib/translate.ts")


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture()
def fast(monkeypatch):
    """The 30 s limit, the 10 s note and the 3 s cadence scaled down so the suite stays fast; the budget is scaled
    through `patience` (60 s * 0.1 = 6 s)."""
    monkeypatch.setattr(vs, "PRIMARY_ENABLED_MS", 1_000)
    monkeypatch.setattr(vs, "SLOW_SAVE_S", 1)
    monkeypatch.setattr(vs, "GATE_POLL_MS", 200)
    return 0.1


def _notes(tmp_path: Path) -> list[dict]:
    path = tmp_path / "transcript.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


# ------------------------------------------------------------------ a corridor card as keel-web 083 draws its gate

#: One card: the primary disabled with the gate's line under it (`StepWaiting`: `p.cnote.corridor-waiting`) for
#: `gate_ms`, then the line gone and the primary enabled; `line: false` draws a disabled primary with no line, never
#: enabled (a screen waiting for a pick). Each press is counted (`window.__presses`) and moves the address.
_CARD = """<!doctype html><html><head><meta charset="utf-8"></head><body><main><section class="ccard">
<h1 class="ccard__title">A corridor screen</h1>
<div class="cbtns ccard__foot pact"><button type="button" class="btn">Back</button>
<button type="button" class="btn primary" %(disabled)s>%(label)s</button><span id="wait"></span></div></section></main>
<script>
const O = %(opts)s;
window.__presses = 0;
const primary = document.querySelector('.btn.primary');
const wait = document.getElementById('wait');
if (O.line) {
  primary.disabled = true;
  wait.outerHTML = '<p class="cnote corridor-waiting" data-testid="corridor-waiting" data-open-steps="1" role="status">'
    + '<span class="kmark live" aria-hidden="true"></span>Keel is finishing the previous step…</p>';
  if (O.gate_ms !== null) setTimeout(() => {
    document.querySelector('[data-testid=corridor-waiting]').remove();
    primary.disabled = false;
  }, O.gate_ms);
}
primary.addEventListener('click', () => {
  window.__presses += 1;
  history.pushState({}, '', '/p/p1/define/next');
});
</script></body></html>"""


def _card(browser, *, line: bool, gate_ms: int | None = None, disabled: bool = False, label: str = vs.SAVE):
    page = browser.new_page()
    body = _CARD % {"opts": json.dumps({"line": line, "gate_ms": gate_ms}), "label": label,
                    "disabled": "disabled" if disabled else ""}
    page.route(f"{BASE}/**", lambda route: route.fulfill(status=200, content_type="text/html", body=body))
    page.goto(f"{BASE}/p/p1/define/persona", wait_until="load")
    return page


def test_the_gate_held_past_the_old_30_s_is_waited_out_and_pressed_once(browser, tmp_path, fast):
    """FR-1 / FR-4: disabled with the gate's line for longer than the plain limit (scaled 30 s -> 1 s), then enabled --
    pressed once, one `gate_waits` row, the transcript's note."""
    page = _card(browser, line=True, gate_ms=2_500)
    try:
        corridor = vs.Corridor(page, Recorder(tmp_path), BASE, patience=fast)
        assert corridor._press_primary(vs.SAVE) == vs.SAVE
        assert page.evaluate("window.__presses") == 1 and page.url.endswith("/define/next")
    finally:
        page.close()
    assert len(corridor.gate_waits) == 1
    row = corridor.gate_waits[0]
    assert row["screen"] == f"{BASE}/p/p1/define/persona" and row["label"] == vs.SAVE
    assert 2.0 <= row["seconds"] < 6 and row["budget_s"] == 6
    assert any(n["name"].startswith("founder's Save waited ") and vs.GATE_LINE in n["name"] for n in _notes(tmp_path))
    assert corridor.slow_saves == []                          # the press itself moved at once


def test_a_disabled_primary_without_the_line_keeps_the_old_failure_by_name(browser, tmp_path, fast):
    """FR-1 / FR-4: no line -- not the gate; today's limit (scaled) and today's Playwright timeout, naming the press."""
    page = _card(browser, line=False, disabled=True, label=vs.CONTINUE)
    try:
        corridor = vs.Corridor(page, Recorder(tmp_path), BASE, patience=fast)
        started = time.monotonic()
        with pytest.raises(PlaywrightTimeoutError, match=r"Timeout 1000ms exceeded: the founder's 'Continue' stayed "
                                                         r"disabled with no \*Keel is finishing"):
            corridor._press_primary(vs.CONTINUE)
        assert time.monotonic() - started < 4                 # the plain limit, never the 6 s budget
        assert page.evaluate("window.__presses") == 0
    finally:
        page.close()
    assert corridor.gate_waits == [] and _notes(tmp_path) == []


def test_an_enabled_primary_is_pressed_at_once_with_no_row(browser, tmp_path, fast):
    page = _card(browser, line=False)
    try:
        corridor = vs.Corridor(page, Recorder(tmp_path), BASE, patience=fast)
        started = time.monotonic()
        corridor._press_primary(vs.SAVE)
        assert time.monotonic() - started < 2 and page.evaluate("window.__presses") == 1
    finally:
        page.close()
    assert corridor.gate_waits == [] and _notes(tmp_path) == []


def test_a_short_gate_is_waited_and_kept_out_of_the_record(browser, tmp_path, monkeypatch):
    """FR-2: a wait under `SLOW_SAVE_S` is waited, never a row."""
    monkeypatch.setattr(vs, "GATE_POLL_MS", 200)
    page = _card(browser, line=True, gate_ms=600)
    try:
        corridor = vs.Corridor(page, Recorder(tmp_path), BASE, patience=1.0)
        corridor._press_primary(vs.SAVE)
        assert page.evaluate("window.__presses") == 1
    finally:
        page.close()
    assert corridor.gate_waits == []


def test_a_gate_past_the_budget_stops_the_walk_naming_the_screen_and_the_line(browser, tmp_path, fast):
    """FR-2: the line still drawn past `SAVE_BUDGET_S * patience` -- `GateStillDrawn` names both; the row is kept."""
    page = _card(browser, line=True, gate_ms=None)
    try:
        corridor = vs.Corridor(page, Recorder(tmp_path), BASE, patience=0.02)          # a 1.2 s budget
        with pytest.raises(vs.GateStillDrawn, match=r"define/persona: \*Keel is finishing the previous step…\* still "
                                                    r"drawn after"):
            corridor._press_primary(vs.SAVE)
        assert page.evaluate("window.__presses") == 0
    finally:
        page.close()
    assert len(corridor.gate_waits) == 1 and corridor.gate_waits[0]["seconds"] >= 1.2
    assert isinstance(vs.GateStillDrawn("x"), AssertionError)


_REFUSED = """<!doctype html><html><head><meta charset="utf-8"></head><body><main><section class="ccard">
<div class="ccard__foot"><button type="button" class="btn primary">Save</button><span id="wait"></span></div></section>
</main><script>
const primary = document.querySelector('.btn.primary');
primary.addEventListener('click', async () => {
  const r = await fetch('/v2/projects/p1/idea', {method: 'PUT', body: '{}'});
  if (r.ok) { history.pushState({}, '', '/p/p1/define/solution/q/1'); return; }
  // the refused write: the step it left open gates the screen until the overview's next poll
  primary.disabled = true;
  document.getElementById('wait').outerHTML = '<p data-testid="corridor-waiting">Keel is finishing the previous step…</p>';
  setTimeout(() => { document.querySelector('[data-testid=corridor-waiting]').remove(); primary.disabled = false; }, 9000);
});
</script></body></html>"""


def test_the_409_second_press_waits_on_the_gate_too(browser, tmp_path, monkeypatch):
    """DRIFT #80 kept: the refused write is pressed again once -- after the gate drawn behind it is waited out."""
    monkeypatch.setattr(vs, "GATE_POLL_MS", 200)
    monkeypatch.setattr(vs, "SLOW_SAVE_S", 1)
    monkeypatch.setattr(vs, "PRIMARY_ENABLED_MS", 1_000)
    page = browser.new_page()
    puts: list = []

    def serve(route):
        if route.request.method == "PUT":
            puts.append(1)
            route.fulfill(status=409 if len(puts) == 1 else 200, content_type="application/json", body="{}")
        else:
            route.fulfill(status=200, content_type="text/html", body=_REFUSED)
    page.route(f"{BASE}/**", serve)
    page.goto(f"{BASE}/p/p1/define/idea", wait_until="load")
    try:
        corridor = vs.Corridor(page, Recorder(tmp_path), BASE, patience=1.0)
        assert corridor._press_primary(vs.SAVE) == vs.SAVE
        assert page.url.endswith("/define/solution/q/1")
    finally:
        page.close()
    assert len(puts) == 2 and len(corridor.conflicts) == 1
    assert len(corridor.gate_waits) == 1 and corridor.gate_waits[0]["seconds"] >= 1


# --------------------------------------------------- who decides: the screen keel-web re-keys under the gate's re-read

#: keel-web's `PersonaRoute` keys `PersonaStep` on the persona's revision, so the gate's re-read (FR-1's refresh) draws
#: the screen afresh and a pick made under the line is gone -- the back-test's stop of 2026-11-17. Drawn with the line for `gate_ms`,
#: then re-rendered with no pick; Continue held until a pick; D2 (*Keel understands*) and its Continue to Will they pay.
_PERSONA = """<!doctype html><html><head><meta charset="utf-8"></head><body><div id="app"></div><script>
const O = %(opts)s;
const S = {gated: true, pick: null, presses: 0};
window.__S = S;
const Q = 'Would the person with the problem decide to use and pay for the idea, or would someone else?';
function render() {
  const app = document.getElementById('app');
  if (/\\/define\\/commercial\\/q\\/1$/.test(location.pathname)) { app.innerHTML = '<h1>Will they pay</h1>'; return; }
  if (S.set) {
    app.innerHTML = `<div class="corridor"><div class="ccard"><p class="understands__kicker">Keel understands</p>
      <p class="understands__big">The person decides.</p><div class="cbtns ccard__foot pact">
      <button type="button" class="btn primary">Continue</button></div></div></div>`;
    app.querySelector('.btn.primary').addEventListener('click', () => {
      history.pushState({}, '', '/p/p1/define/commercial/q/1'); render(); });
    return;
  }
  const radio = (kind, words) => `<button type="button" role="radio" aria-checked="${S.pick === kind}"
      class="calib__opt" data-kind="${kind}"><i aria-hidden="true"></i>${words}</button>`;
  app.innerHTML = `<div class="corridor corridor--fit"><div class="ccard ccard--fit"><div class="ccard__body">
    <h1 class="ccard__title">${Q}</h1><div class="decider-opts calib__opts" role="radiogroup" aria-label="${Q}">
    ${radio('SAME_PERSON', 'The person with the problem decides')}${radio('SOMEONE_ELSE', 'Someone else decides')}
    </div></div><div class="cbtns cbtns--split ccard__foot pact"><button type="button" class="btn">Back</button>
    <button type="button" class="btn primary" ${S.pick === null || S.gated ? 'disabled' : ''}>Continue</button>`
    + (S.gated ? '<p class="cnote corridor-waiting" data-testid="corridor-waiting" role="status">'
       + 'Keel is finishing the previous step…</p>' : '') + `</div></div></div>`;
  app.querySelectorAll('[role=radio]').forEach((b) => b.addEventListener('click', () => {
    S.pick = b.dataset.kind; render(); }));
  app.querySelector('.btn.primary').addEventListener('click', () => {
    if (S.pick === null || S.gated) return; S.presses += 1; S.set = true; render(); });
}
render();
// the step lands: the overview's poll lifts the gate and the re-read draws the screen afresh, with no pick
setTimeout(() => { S.gated = false; S.pick = null; render(); }, O.gate_ms);
</script></body></html>"""


def test_who_decides_waits_out_the_gate_before_the_pick_and_continues(browser, tmp_path, monkeypatch):
    """The back-test's stop of 2026-11-17: the pick waits for the gate, so the re-read cannot drop it; Continue is pressed once."""
    monkeypatch.setattr(vs, "GATE_POLL_MS", 200)
    monkeypatch.setattr(vs, "SLOW_SAVE_S", 1)
    monkeypatch.setattr(vs, "pass_teaching_sheet", lambda *a, **k: {"shown": False})
    page = browser.new_page()
    body = _PERSONA % {"opts": json.dumps({"gate_ms": 2_000})}
    page.route(f"{BASE}/**", lambda route: route.fulfill(status=200, content_type="text/html", body=body))
    page.goto(f"{BASE}/p/p1/define/persona", wait_until="load")
    try:
        corridor = vs.Corridor(page, Recorder(tmp_path), BASE, patience=1.0)
        out = corridor.persona({"kind": "SAME_PERSON"})
        assert page.url.endswith("/define/commercial/q/1") and "Keel understands" in out["text"]
        assert page.evaluate("window.__S.presses") == 1
    finally:
        page.close()
    assert len(corridor.gate_waits) == 1 and corridor.gate_waits[0]["label"] == vs.CONTINUE
    assert corridor.gate_waits[0]["seconds"] >= 1.5


def test_every_corridor_press_site_goes_through_the_wait():
    """FR-1: no corridor primary is pressed through the old bare 30 s `!b.disabled` wait; the listed sites call the
    wait (tasks.md names them)."""
    src = inspect.getsource(vs.Corridor)
    assert 'wait_for_function("(b) => !b.disabled"' not in src
    for method, calls in (("_press_primary", 2), ("_save_holding", 2), ("persona", 4), ("word_pilot_and_lock", 1),
                          ("_pilot_pick", 1), ("relock", 1), ("seed", 2), ("confirm_seed", 1), ("confirm_context", 1),
                          ("_save_context", 1), ("_context_window_page", 1), ("needs_input", 1),
                          ("context_confirmed", 1)):
        assert inspect.getsource(getattr(vs.Corridor, method)).count("self._wait_for_the_gate(") == calls, method
    lock = inspect.getsource(vs.Corridor.word_pilot_and_lock)
    assert lock.index("except GateStillDrawn:") < lock.index("except Exception:")


def test_the_line_is_keel_webs_and_the_limits_are_todays():
    assert vs.GATE_LINE == "Keel is finishing the previous step…"
    assert vs.PRIMARY_ENABLED_MS == 30_000 and vs.GATE_POLL_MS == 3_000 and vs.LOCK_PARTS_WAIT_MS == 15_000
    assert vs.SAVE_BUDGET_S == 60 and vs.SLOW_SAVE_S == 10
    if KEEL_WEB_TRANSLATE.exists():
        assert f'export const CORRIDOR_WAITING = "{vs.GATE_LINE}";' in KEEL_WEB_TRANSLATE.read_text(encoding="utf-8")


# ------------------------------------------------------------------------------------------------ FR-2 the record

def test_the_bundle_carries_the_rows_and_the_md_says_one_line_under_the_stack():
    rows = [{"screen": f"{BASE}/p/p1/define/persona", "label": "Continue", "seconds": 212.4, "budget_s": 660},
            {"screen": f"{BASE}/p/p1/define/solution/q/2", "label": "Save", "seconds": 14.0, "budget_s": 660}]
    j = SimpleNamespace(corridor=SimpleNamespace(gate_waits=rows))
    assert bt.gate_waits(j) == rows and bt.gate_waits(SimpleNamespace(corridor=None)) == []
    assert bt.gate_waits_said(rows) == "Gate waits: 2, the longest 212.4 s on `/p/p1/define/persona`"
    assert bt.gate_waits_said([]) == "Gate waits: 0"
    base = {"run": "r", "passed": True, "stack": {"keel-cloud": "a", "keel-web": "b"}}
    md = bt.markdown({**base, "gate_waits": rows}).splitlines()
    stack = next(i for i, line in enumerate(md) if line.startswith("- Stack:"))
    assert md[stack + 1] == "- Gate waits: 2, the longest 212.4 s on `/p/p1/define/persona`"
    assert "- Gate waits: 0" in bt.markdown({**base, "gate_waits": []}).splitlines()
    assert not any(line.startswith("- Gate waits") for line in bt.markdown(base).splitlines())   # a bundle before 155


def test_the_transcript_carries_gate_waits():
    src = inspect.getsource(bt.transcript)
    assert '"gate_waits": _safe(lambda: gate_waits(j), [])' in src


# --------------------------------------------------------------------------------------- FR-3 the wire's own wait

def test_the_wires_own_wait_stays():
    src = inspect.getsource(cs._wait_steps_landed)
    assert "openSteps" in src and "timeout_s * j.patience" in src


# ------------------------------------------------------------------------- FR-5 the lock screen shot after it loaded

#: keel-web 191's lock screen on the problem study (no pilot, no counter): the frame and the sentence at once, the
#: problem box (`lock-problem`) and the plan's rows (`lock-plan-row`) after their own reads (`rows_ms`); the lock's POST
#: and *Sent*. `define/ready/word` answers with the screen.
_LOCK = """<!doctype html><html><head><meta charset="utf-8"></head><body><div id="app"></div><script>
const O = %(opts)s;
if (/\\/define\\/ready\\/word\\/?$/.test(location.pathname)) history.replaceState({}, '', '/p/p1/define/ready/interviewer');
const app = document.getElementById('app');
if (/\\/interviews\\/sent$/.test(location.pathname)) { app.innerHTML = '<h1>Sent</h1>'; }
else {
  app.innerHTML = `<main class="corridor before"><h1>Who should ask them your questions?</h1>
    <p data-testid="lock-sentence">Keel writes the questions people will be asked from these answers.</p>
    <div id="rows"></div><div class="ccard__foot"><button class="btn primary" data-testid="lock-and-record">Lock and
    write the questions</button></div></main>`;
  if (O.rows_ms !== null) setTimeout(() => {
    document.getElementById('rows').innerHTML = `<section data-testid="lock-problem"><p>The problem, as you wrote it</p>
      <p>The problem, in the founder's words.</p><button>Change</button></section>
      <ol data-testid="lock-plan"><li data-testid="lock-plan-row">Most of them met it last week</li></ol>`;
  }, O.rows_ms);
  app.querySelector('[data-testid=lock-and-record]').addEventListener('click', async () => {
    await (await fetch('/v2/projects/p1/lock', {method: 'POST', body: '{}'})).json();
    history.pushState({}, '', '/p/p1/interviews/sent'); app.innerHTML = '<h1>Sent</h1>';
  });
}
</script></body></html>"""


def _lock_walk(browser, tmp_path, rows_ms):
    page = browser.new_page()
    body = _LOCK % {"opts": json.dumps({"rows_ms": rows_ms})}

    def serve(route):
        if route.request.method == "POST":
            route.fulfill(status=201, content_type="application/json", body=json.dumps({"version": 1}))
        else:
            route.fulfill(status=200, content_type="text/html", body=body)
    page.route(f"{BASE}/**", serve)
    page.goto(f"{BASE}/p/p1/define/ready/interviewer", wait_until="load")
    shots: list = []
    try:
        corridor = vs.Corridor(page, Recorder(tmp_path), BASE)
        corridor.camera = lambda slug: shots.append(
            (slug, page.get_by_test_id("lock-problem").count(), page.get_by_test_id("lock-plan-row").count()))
        drawn = corridor.word_pilot_and_lock(pilot=False)
    finally:
        page.close()
    return drawn, shots


def test_the_lock_screen_is_shot_after_the_problem_and_the_rows_have_loaded(browser, tmp_path):
    drawn, shots = _lock_walk(browser, tmp_path, rows_ms=1_200)
    assert shots == [("ready-interviewer", 1, 1)]
    assert drawn["status"] == 201 and drawn["l1"]["problem"] == 1 and drawn["l1"]["plan_rows"] == 1


def test_the_shot_is_still_taken_where_the_rows_never_load_and_l1_names_them_missing(browser, tmp_path, monkeypatch):
    monkeypatch.setattr(vs, "LOCK_PARTS_WAIT_MS", 300)          # l1's 15 s a part, scaled: the parts never come
    drawn, shots = _lock_walk(browser, tmp_path, rows_ms=None)
    assert shots == [("ready-interviewer", 0, 0)]
    assert drawn["l1"]["problem"] == 0 and drawn["l1"]["plan_rows"] == 0


def test_both_branches_shoot_after_l1():
    src = inspect.getsource(vs.Corridor.word_pilot_and_lock)
    calls = [i for i in range(len(src)) if src.startswith("l1 = self.l1(face)", i)]
    shots = [i for i in range(len(src)) if src.startswith('self._shot("ready-interviewer")', i)]
    assert len(calls) == 2 and len(shots) == 2
    assert all(call < shot for call, shot in zip(calls, shots))
    assert shots[0] < calls[1]                        # one shot a branch, each after its own l1
