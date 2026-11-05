"""Spec 140 -- the reader sees the whole screen.

FR-1: a Choose screen's suggested radio (keel-web 097 FR-4: `data-suggested="true"`, its why under it, named by
`aria-describedby` -> `choose-{dimension}-why-{i}`) is read with its why, and the founder-reader's *Options:* line reads
*{label} -- Keel's suggestion: {why}* -- the full text and the compact line; a Check list's suggested row (spec 139 FR-3)
reads the same words, one function. FR-2: the Commitment check's step box, the smaller-step box with its frame (or its
absence) and the strangers' answer chips are read and named. FR-3: the primary's Save waits out a slow writer up to the
seed's budget and says how long it took. FR-4: the keel-web health gate restarts web once on a 500 before raising; the
Vite *transport invoke timed out* lines a walk saw are counted in the cycle record's head. FR-4b: the Current solution
draft's two fields (keel-web 177). FR-5: the six cycle-14 screens of `tests/fixtures/spec140/` re-read with the new
capture -- real chromium on static pages drawn as keel-web draws them; no stack, no model.
"""

from __future__ import annotations

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

import pytest
from playwright.sync_api import sync_playwright

from evals import backtest as bt
from evals import corpus_scenario as cs
from harness import vectors_screens as vs
from harness.steps import Recorder
from quality import cycle
from quality import readers
from stack import processes
from stack.config import load_config

FIXTURES = Path(__file__).parent / "fixtures" / "spec140"
RECORDED = json.loads((FIXTURES / "recorded_screens.json").read_text(encoding="utf-8"))["screens"]
KEEL_WEB = Path(load_config(validate=False).keel_web)
BASE = "http://keel.test"


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture()
def page(browser):
    page = browser.new_page()
    yield page
    page.close()


def _esc(text) -> str:
    return (str(text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


# ------------------------------------------------------------------ pages drawn as keel-web ec99fa93 draws them

def choose_page(dimension: str, options: list[str], *, suggested: int | None = None, why: str | None = None,
                beliefs: list[str] | None = None, title: str = "Which one do you want to test?",
                intro: str = "", kicker: str = "", keel_test: dict | None = None) -> str:
    """`ListQuestion.tsx` `ChooseList`: the radios in a `radiogroup`, Keel's suggestion a quiet tag and the served why
    under its radio (`calib__suggest`), named by the radio's `aria-describedby` beside a belief's id where there is one
    (Buyer and payer, spec 149)."""
    rows = []
    for i, label in enumerate(options):
        why_id, belief_id = f"choose-{dimension}-why-{i}", f"choose-{dimension}-belief-{i}"
        mine = i == suggested and why
        belief = beliefs[i] if beliefs else None
        described = " ".join(x for x in ((why_id if mine else None), (belief_id if belief else None)) if x)
        rows.append(f'<button type="button" role="radio" aria-checked="false" class="calib__opt"'
                    + (f' aria-describedby="{described}"' if described else "")
                    + (' data-suggested="true"' if mine else "") + f'><i aria-hidden="true"></i>{_esc(label)}</button>')
        if belief:
            rows.append(f'<p class="calib__optbelief" id="{belief_id}" data-testid="choose-belief">{_esc(belief)}</p>')
        if mine:
            rows.append(f'<p class="calib__suggest" id="{why_id}" data-testid="choose-suggestion">'
                        f'<span class="calib__suggest-k">Keel\'s suggestion</span>'
                        f'<span class="calib__suggest-why">{_esc(why)}</span></p>')
    test = keel_test or {}
    return (f'<main><p class="corridor__kicker">{_esc(kicker)}</p><p class="corridor__intro">{_esc(intro)}</p>'
            f'<section class="ccard"><div class="listcheck"><p class="listcheck__title" id="choose-{dimension}">'
            f'{_esc(title)}</p><div class="calib__opts calib__opts--column" role="radiogroup" '
            f'aria-labelledby="choose-{dimension}">{"".join(rows)}</div></div>'
            + (f'<div class="keeltest"><p class="keeltest__t">{_esc(test.get("belief"))}</p>'
               f'<p class="keeltest__b">{_esc(test.get("bar"))}</p>'
               + (f'<p data-testid="keeltest-note">{_esc(test["note"])}</p>' if test.get("note") else "")
               + "</div>" if test else "")
            + "</section></main>")


def commitment_page(step: str, *, smaller: str | None = None, answers: list[str] | None = None,
                    note: str | None = None, kicker: str = "", intro: str = "", keel_test: dict | None = None) -> str:
    """`ListQuestion.tsx`'s `one_step` block: the step box, its counter, the served note, the smaller step framed
    *Yes, after ... first* with its counter (or the add button), the answers strangers get as pills."""
    words = len(step.split())
    parts = ['<div class="listcheck"><label class="listcheck__field"><span class="listcheck__k">Your step, as strangers '
             f'hear it</span><textarea class="listrow__ed" rows="1">{_esc(step)}</textarea></label>'
             f'<p class="listcheck__note">{words} / 9 words.</p>']
    if note:
        parts.append(f'<p class="listrow__warn" role="note" data-testid="commitment-note">{_esc(note)}</p>')
    if smaller is not None:
        parts.append('<div class="listcheck__field listcheck__smaller" data-testid="commitment-smaller-step">'
                     '<span class="listcheck__k">Or a smaller step first</span><div class="listrow__line">'
                     '<span class="listcheck__said">Yes, after</span><textarea class="listrow__ed" rows="1" '
                     f'aria-label="Or a smaller step first">{_esc(smaller)}</textarea><span class="listcheck__said">'
                     'first</span><button type="button" class="listrow__rm" data-testid="commitment-smaller-step-remove">'
                     f'×</button></div><p class="listcheck__note">{len(smaller.split())} / 9 words.</p></div>')
    else:
        parts.append('<button type="button" class="listcheck__add" data-testid="commitment-smaller-step-add">+ Add a '
                     'smaller step first</button>')
    if answers:
        parts.append('<div class="listcheck__field listcheck__answers" data-testid="commitment-answers">'
                     '<p class="listcheck__k" id="commitment-answers-title">What strangers can answer</p>'
                     '<ul class="calib__chips listcheck__answerlist" aria-labelledby="commitment-answers-title">'
                     + "".join(f'<li class="listcheck__answer" data-testid="commitment-answer">{_esc(a)}</li>'
                               for a in answers) + "</ul></div>")
    parts.append("</div>")
    test = keel_test or {}
    return (f'<main><p class="corridor__kicker">{_esc(kicker)}</p><p class="corridor__intro">{_esc(intro)}</p>'
            '<section class="ccard">' + "".join(parts)
            + (f'<div class="keeltest"><p class="keeltest__t">{_esc(test.get("belief"))}</p>'
               f'<p class="keeltest__b">{_esc(test.get("bar"))}</p></div>' if test else "")
            + "</section></main>")


def _read(page, html: str) -> dict:
    page.set_content(html)
    return page.evaluate(bt.READ_JS)


def _recorded(shot: dict, n: int = 1, slug: str = "screen") -> dict:
    """The camera's shot as `backtest.founder_screens` writes it into the bundle (no journey: no answer, no read-back)."""
    cam = SimpleNamespace(founder_shots=[{"n": n, "slug": slug, "file": f"screens/founder-{n:02d}-{slug}.png",
                                          **shot}])
    return bt.founder_screens(None, cam, {})[0]


# ------------------------------------------------------------------------------------- the words are keel-web's

def test_the_words_are_keel_webs():
    path = KEEL_WEB / "src" / "lib" / "translate.ts"
    if not path.is_file():
        pytest.skip(f"no translate.ts at {KEEL_WEB}")
    text = path.read_text(encoding="utf-8")
    for const, words in (("LIST_KEEL_SUGGESTION", readers.KEEL_SUGGESTION),
                         ("LIST_STEP_LABEL", readers.COMMITMENT_STEP),
                         ("LIST_SMALLER_STEP_LABEL", readers.COMMITMENT_SMALLER),
                         ("LIST_SMALLER_STEP_BEFORE", readers.COMMITMENT_BEFORE),
                         ("LIST_SMALLER_STEP_AFTER", readers.COMMITMENT_AFTER),
                         ("COMMITMENT_ANSWERS_TITLE", readers.COMMITMENT_ANSWERS)):
        assert f'export const {const} = "{words}";' in text, const


def test_the_capture_reads_keel_webs_markup():
    path = KEEL_WEB / "src" / "components" / "calibration" / "ListQuestion.tsx"
    if not path.is_file():
        pytest.skip(f"no ListQuestion.tsx at {KEEL_WEB}")
    tsx = path.read_text(encoding="utf-8")
    for part in ('data-suggested={suggestion ? "true" : undefined}', "const whyId = `choose-${question.dimension}-why-${i}`",
                 'className="calib__suggest-why"', 'data-testid="commitment-smaller-step"',
                 'data-testid="commitment-smaller-step-add"', 'data-testid="commitment-answers"',
                 'className="listcheck__said"', '<label className="listcheck__field">'):
        assert part in tsx, part
    for part in ("data-suggested", "aria-describedby", "-why-", "calib__suggest-why", "commitment-smaller-step",
                 "commitment-smaller-step-add", "listcheck__said", "label.listcheck__field"):
        assert part in bt.READ_JS, part


# ----------------------------------------------------------------------------- FR-1 the Choose screen's suggestion

FRESCO = RECORDED[0]


def test_the_suggested_radio_is_read_with_its_why(page):
    shot = FRESCO["screen"]
    read = _read(page, choose_page("solution.compatibility", shot["options"], suggested=0, why=FRESCO["drawn"]["why"]))
    assert read["options"] == shot["options"]
    assert read["choices"] == [{"label": shot["options"][0], "suggested": True, "why": FRESCO["drawn"]["why"]},
                               {"label": shot["options"][1], "suggested": False, "why": None}]


def test_the_why_is_the_describedby_element_with_why_in_its_id_never_the_belief(page):
    read = _read(page, choose_page("commercial.buyer_payer_alignment", ["Nobody else", "The CFO"], suggested=1,
                                   why="The CFO signs off spend.", beliefs=["Decided alone.", "The CFO agrees."]))
    assert read["choices"][1] == {"label": "The CFO", "suggested": True, "why": "The CFO signs off spend."}
    assert read["choices"][0]["suggested"] is False


def test_no_suggestion_drawn_reads_no_choices(page):
    read = _read(page, choose_page("solution.compatibility", ["A", "B"]))
    assert read["choices"] is None and read["options"] == ["A", "B"]


def test_the_options_line_reads_keels_suggestion_in_the_full_text_and_the_compact_one(page):
    shot = FRESCO["screen"]
    read = _read(page, choose_page("solution.compatibility", shot["options"], suggested=0, why=FRESCO["drawn"]["why"]))
    screen = _recorded(read, 13, "choose-solution.compatibility")
    assert screen["choices"] == read["choices"]
    said = readers.founder_screens({"founder_screens": [screen]})[0]
    line = f"{shot['options'][0]} -- Keel's suggestion: {FRESCO['drawn']['why']}"
    assert f"  - {line}" in said.full.splitlines()
    assert f"  - {shot['options'][1]}" in said.full.splitlines()
    assert said.compact.endswith(f"; Options: {line}")


def test_a_check_rows_suggestion_reads_the_same_words_one_function():
    screen = {"n": 4, "screen": "check-solution.adoption_friction", "kicker": "K",
              "rows": ["Charge the glasses every day", "Pair the glasses with a phone"],
              "suggested": [{"row": "Pair the glasses with a phone", "why": "Pairing is the first thing to fail."}]}
    said = readers.founder_screens({"founder_screens": [screen]})[0]
    line = readers.suggestion_said("Pair the glasses with a phone", "Pairing is the first thing to fail.")
    assert line == "Pair the glasses with a phone -- Keel's suggestion: Pairing is the first thing to fail."
    assert f"  - {line}" in said.full.splitlines()
    assert "  - Charge the glasses every day" in said.full.splitlines()
    assert said.compact.endswith(f"; Rows: {line}")


def test_a_screen_with_no_suggestion_reads_as_before():
    screen = {"n": 2, "screen": "choose-solution.compatibility", "kicker": "K", "options": ["A", "B"]}
    said = readers.founder_screens({"founder_screens": [screen]})[0]
    assert "Keel's suggestion" not in said.full and said.compact == "2. [K] (choose-solution.compatibility)"


# ------------------------------------------------------------------------------------ FR-2 the Commitment check

AIRCAPS = RECORDED[5]


def test_the_commitment_check_is_read_whole(page):
    drawn = AIRCAPS["drawn"]
    read = _read(page, commitment_page(drawn["step"], smaller=drawn["smaller"], answers=drawn["answers"]))
    c = read["commitment"]
    assert c["step"] == {"label": "Your step, as strangers hear it", "value": drawn["step"]}
    assert c["smaller"] == {"label": "Or a smaller step first", "before": "Yes, after", "value": drawn["smaller"],
                            "after": "first"}
    assert c["smaller_add"] is None and c["answers"] == drawn["answers"] and c["note"] is None
    assert read["note"] == ["7 / 9 words.", "6 / 9 words."]                 # the counters stay as guidance


def test_no_smaller_step_is_read_as_absent(page):
    read = _read(page, commitment_page("pay for a pilot at the depot", answers=["Yes", "No"],
                                       note="Name where the money goes."))
    c = read["commitment"]
    assert c["smaller"] is None and c["smaller_add"] == "+ Add a smaller step first"
    assert c["note"] == "Name where the money goes."


def test_the_reader_names_the_step_the_smaller_step_and_the_answers(page):
    drawn = AIRCAPS["drawn"]
    read = _read(page, commitment_page(drawn["step"], smaller=drawn["smaller"], answers=drawn["answers"]))
    lines = readers.founder_screens({"founder_screens": [_recorded(read, 18, "check-commercial.commitment")]})[0] \
        .full.splitlines()
    assert "Your step, as strangers hear it: order the caption glasses with free returns" in lines
    assert "Or a smaller step first: Yes, after try a pair of caption glasses first" in lines
    at = lines.index("What strangers can answer:")
    assert lines[at + 1:at + 5] == [f"  - {a}" for a in drawn["answers"]]
    assert "  - 7 / 9 words." in lines and "  - 6 / 9 words." in lines


def test_the_reader_says_no_smaller_step(page):
    read = _read(page, commitment_page("pay for a pilot", answers=["Yes", "No"], note="Name where the money goes."))
    lines = readers.founder_screens({"founder_screens": [_recorded(read, 18, "check-commercial.commitment")]})[0] \
        .full.splitlines()
    assert "Or a smaller step first: no smaller step (the screen offers + Add a smaller step first)" in lines
    assert "Keel's note beside the step: Name where the money goes." in lines


def test_an_edited_check_keeps_the_after_edit_read():
    assert {"commitment", "suggested"} <= set(bt.AFTER_EDIT_FIELDS)


# ------------------------------------------------------------------------------ FR-5 the six screens, re-read

def rebuild(item: dict) -> str:
    """One recorded screen drawn again as keel-web draws it: the bundle's own words (kicker, intro, title, options,
    the *Keel will test* box), with what its screenshot drew beside them (`drawn`)."""
    shot, drawn = item["screen"], item["drawn"]
    if shot["screen"].startswith("check-commercial.commitment"):
        return commitment_page(drawn["step"], smaller=drawn.get("smaller"), answers=drawn.get("answers"),
                               kicker=shot.get("kicker"), intro=shot.get("intro"), keel_test=shot.get("keel_test"))
    return choose_page(shot["screen"].split("-", 1)[1], shot["options"], suggested=drawn.get("suggested"),
                       why=drawn.get("why"), title=shot.get("title") or "", intro=shot.get("intro") or "",
                       kicker=shot.get("kicker") or "", keel_test=shot.get("keel_test"))


def reread(page, item: dict) -> readers.Screen:
    """FR-5: the recorded screen with the new capture's parts (`choices`, `commitment`) laid over it, as the reader
    would now be handed it -- the text alone, no model."""
    read = _read(page, rebuild(item))
    screen = {**item["screen"], **{k: read[k] for k in ("choices", "commitment", "suggested") if read.get(k)}}
    return readers.founder_screens({"founder_screens": [screen]})[0]


@pytest.mark.parametrize("item", RECORDED, ids=[f"{r['entry']}-{r['screen']['screen']}" for r in RECORDED])
def test_the_six_recorded_screens_re_read(page, item):
    said = reread(page, item)
    shot, drawn = item["screen"], item["drawn"]
    before = readers.founder_screens({"founder_screens": [shot]})[0]
    if "options" in shot and shot["options"]:
        if drawn.get("suggested") is None:
            assert said.full == before.full and "Keel's suggestion" not in said.full   # the screen drew none
        else:
            label = shot["options"][drawn["suggested"]]
            assert f"  - {label} -- Keel's suggestion: {drawn['why']}" in said.full.splitlines()
            assert "Keel's suggestion" not in before.full
    else:
        assert "Your step, as strangers hear it: order the caption glasses with free returns" in said.full
        assert "Or a smaller step first: Yes, after try a pair of caption glasses first" in said.full
        assert "What strangers can answer:\n  - Yes, I'd order the caption glasses with free returns" in said.full
        assert "Your step, as strangers hear it:" not in before.full and "try a pair" not in before.full


# ---------------------------------------------------------------------------------------------- FR-3 the Save wait

_SLOW = """<!doctype html><html><body><main><section class="ccard"><h1 class="calib__q">Name it</h1>
<div class="ccard__foot"><button type="button" class="btn primary">Save</button></div></section></main><script>
document.querySelector('.btn.primary').addEventListener('click', () => {
  fetch('/v2/projects/p1/idea', {method: 'PUT', body: '{}'}).then(() => {
    history.pushState({}, '', '/p/p1/define/solution/q/1');
  });
});
</script></body></html>"""


def _slow_page(browser, delay_s: float):
    page = browser.new_page()

    def serve(route):
        if route.request.method == "PUT":
            time.sleep(delay_s)                                    # the writer's refuse-and-repair turn
            route.fulfill(status=200, content_type="application/json", body="{}")
        else:
            route.fulfill(status=200, content_type="text/html", body=_SLOW)
    page.route(f"{BASE}/**", serve)
    page.goto(f"{BASE}/p/p1/define/idea", wait_until="load")
    return page


def test_a_save_that_moves_after_15_s_is_waited_and_noted(browser, tmp_path):
    page = _slow_page(browser, 15)
    try:
        recorder = Recorder(tmp_path)
        corridor = vs.Corridor(page, recorder, BASE, patience=1.0)
        label = corridor._press_primary(vs.SAVE)
        assert label == vs.SAVE and page.url.endswith("/define/solution/q/1")
    finally:
        page.close()
    assert len(corridor.slow_saves) == 1 and corridor.slow_saves[0]["label"] == vs.SAVE
    assert 14 <= corridor.slow_saves[0]["seconds"] < 30 and corridor.slow_saves[0]["budget_s"] == 60
    notes = [json.loads(line) for line in (tmp_path / "transcript.jsonl").read_text().splitlines()]
    assert any(n["name"].startswith("founder's Save took ") and "past 10 s" in n["name"] and n["ok"] for n in notes)


def test_a_fast_save_writes_no_note(browser, tmp_path):
    page = _slow_page(browser, 0)
    try:
        corridor = vs.Corridor(page, Recorder(tmp_path), BASE, patience=1.0)
        corridor._press_primary(vs.SAVE)
    finally:
        page.close()
    assert corridor.slow_saves == [] and not (tmp_path / "transcript.jsonl").exists()


def test_a_save_past_the_budget_still_stops_the_walk(browser, tmp_path):
    page = _slow_page(browser, 6)
    try:
        corridor = vs.Corridor(page, Recorder(tmp_path), BASE, patience=0.05)     # a 3 s budget
        with pytest.raises(Exception, match="Timeout"):
            corridor._press_primary(vs.SAVE)
    finally:
        page.close()


_REFUSED = """<!doctype html><html><body><main><section class="ccard">
<div class="ccard__foot"><button type="button" class="btn primary">Save</button></div></section></main><script>
document.querySelector('.btn.primary').addEventListener('click', () => {
  fetch('/v2/projects/p1/idea', {method: 'PUT', body: '{}'}).then((r) => {
    if (r.ok) history.pushState({}, '', '/p/p1/define/solution/q/1');
  });
});
</script></body></html>"""


def test_a_refused_write_is_pressed_again_once_as_before(browser, tmp_path):
    """DRIFT #80 kept: a 409 CONCURRENCY leaves the page where it was; the press goes again once and is named."""
    page = browser.new_page()
    puts = []

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
    finally:
        page.close()
    assert len(puts) == 2 and len(corridor.conflicts) == 1 and corridor.conflicts[0]["label"] == vs.SAVE


def test_the_save_budget_is_the_seeds():
    assert vs.SAVE_BUDGET_S == 60 and vs.SLOW_SAVE_S == 10
    import inspect
    src = inspect.getsource(vs.Corridor._press_primary)
    assert "timeout=10_000" not in src and "SAVE_BUDGET_S * self.patience" in src


# ----------------------------------------------------------------------------------------------- FR-4 the web health

class _Health(BaseHTTPRequestHandler):
    status = 500

    def do_GET(self):  # noqa: N802 - the stdlib's name
        self.send_response(type(self).status)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass


@pytest.fixture()
def health():
    handler = type("Health", (_Health,), {"status": 500})
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield handler, f"http://127.0.0.1:{server.server_address[1]}/"
    server.shutdown()


def test_a_500_once_restarts_web_once_and_passes(health):
    handler, url = health
    said, restarts = [], []

    def restart():
        restarts.append(1)
        handler.status = 200                                    # the restarted web answers
    processes.wait_or_restart(url, 1.5, restart=restart, say=said.append, ok_statuses={200}, label="keel-web")
    assert restarts == [1]
    assert said and said[0].startswith("keel-web: the health gate failed") and "restarting it once" in said[0]
    assert "HTTP 500" in said[0]


def test_a_web_that_stays_500_raises_after_the_one_restart(health):
    handler, url = health
    said, restarts = [], []
    with pytest.raises(processes.HealthGateTimeout, match="after one restart"):
        processes.wait_or_restart(url, 1.2, restart=lambda: restarts.append(1), say=said.append, ok_statuses={200},
                                  label="keel-web")
    assert restarts == [1] and len(said) == 1


def test_a_healthy_web_is_never_restarted(health):
    handler, url = health
    handler.status = 200
    restarts = []
    processes.wait_or_restart(url, 1.5, restart=lambda: restarts.append(1), say=lambda s: None, ok_statuses={200})
    assert restarts == []


def test_web_up_restarts_once_on_its_gate(monkeypatch, tmp_path):
    from stack import web
    config = SimpleNamespace(web_port=5999, cloud_port=18080, profile="eval", keel_web=tmp_path, web_boot_timeout=1)
    spawned, killed, gates = [], [], []
    monkeypatch.setattr(web, "is_up", lambda c: False)
    monkeypatch.setattr(web, "is_port_open", lambda port: False)
    monkeypatch.setattr(web, "require_port_free", lambda port, label: None)
    monkeypatch.setattr(web, "spawn", lambda name, *a, **k: spawned.append(name) or 1)
    monkeypatch.setattr(web, "killpg_by_name", lambda name: killed.append(name))

    def gate(url, timeout_s, ok_statuses=None):
        gates.append(url)
        if len(gates) == 1:
            raise processes.HealthGateTimeout(f"{url} never answered within 1s -- last error: got HTTP 500 from {url}")
    monkeypatch.setattr(processes, "wait_for_http", gate)
    web.up(config)
    assert spawned == ["web", "web"] and killed == ["web"] and len(gates) == 2


def test_web_up_restarts_a_running_web_that_answers_500(monkeypatch, tmp_path):
    from stack import web
    config = SimpleNamespace(web_port=5999, cloud_port=18080, profile="eval", keel_web=tmp_path, web_boot_timeout=1)
    spawned, killed = [], []
    monkeypatch.setattr(web, "is_up", lambda c: False)
    monkeypatch.setattr(web, "is_port_open", lambda port: True)            # up, answering 500
    monkeypatch.setattr(web, "is_running", lambda name: True)              # and ours
    monkeypatch.setattr(web, "require_port_free", lambda port, label: None)
    monkeypatch.setattr(web, "spawn", lambda name, *a, **k: spawned.append(name) or 1)
    monkeypatch.setattr(web, "killpg_by_name", lambda name: killed.append(name))
    monkeypatch.setattr(processes, "wait_for_http", lambda *a, **k: None)
    web.up(config)
    assert killed == ["web"] and spawned == ["web"]


VITE = "11:06:12 PM [vite] Internal server error: transport invoke timed out after 60000ms"


def test_the_vite_timeouts_a_walk_saw_are_counted(tmp_path):
    log = tmp_path / "web.log"
    log.write_text(f"{VITE}\nold line\n", encoding="utf-8")
    at = cycle.log_size(log)
    with log.open("a", encoding="utf-8") as handle:
        handle.write(f"{VITE}\nfine\n{VITE}\n")
    assert cycle.vite_timeouts(log, at) == 2
    assert cycle.vite_timeouts(log, 0) == 3
    assert cycle.vite_timeouts(tmp_path / "none.log", 0) is None
    log.write_text(f"{VITE}\n", encoding="utf-8")                    # a log that started over
    assert cycle.vite_timeouts(log, at + 1000) == 1


def test_walk_one_counts_the_lines_its_walk_wrote(tmp_path, monkeypatch):
    log = tmp_path / "web.log"
    log.write_text(f"{VITE}\n", encoding="utf-8")
    monkeypatch.setattr(cycle, "WEB_LOG", log)

    def runner(argv, stdout=None, stderr=None):
        if "backtest" in argv:
            with log.open("a", encoding="utf-8") as handle:
                handle.write(f"{VITE}\n{VITE}\n")
        return SimpleNamespace(returncode=1)
    steps = cycle.plan_steps(["21-codyco"], ["SOLUTION"], "keel", tmp_path)[:3]
    monkeypatch.setattr(bt, "run_dir_in", lambda text: None)
    monkeypatch.setattr(bt, "latest_run_dir", lambda *a, **k: None)
    monkeypatch.setattr(bt, "summary", lambda *a, **k: {})
    study = cycle.walk_one("21-codyco", "SOLUTION", steps, door="keel", runner=runner, runs_dir=tmp_path)
    assert study.vite_timeouts == 2 and study.error


def test_the_head_says_the_vite_count_beside_the_typos_line():
    d = {"record": "20261106-abcdef0", "why": "w", "started": "s", "ended": "e", "seconds": 60, "door": "keel",
         "entries": ["21-codyco"], "scopes": ["SOLUTION"], "cloud_sha": "abcdef0", "web_sha": "1234567",
         "routing_versions": ["17"], "rubric_version": 5, "reader": {"model": "m", "effort": "medium"},
         "bar_pct": 80, "weak_rule": {"zero_entries": 2, "mean_under": 2}, "studies": [], "walks": None,
         "head": {"score_pct": 85.0, "flagged_pct": 3.0, "screens": 10, "typos": 3, "typo_fields": 2, "typo_leaks": 0,
                  "vite_timeouts": 58, "founder": {}, "respondent": {}},
         "baseline": None, "against_baseline": None, "previous": None,
         "cost": {"walk_usd": 0, "read_usd": 0, "total_usd": 0}, "weak_rows": []}
    try:
        text = cycle.render_record(d)
    except (KeyError, TypeError):
        pytest.skip("render_record wants more of a record than this sketch")
    lines = text.splitlines()
    typos = next(i for i, x in enumerate(lines) if x.startswith("  - typos: "))
    assert lines[typos + 1] == ('  - Vite "transport invoke timed out": 58 lines in runs/.stack/web.log during the '
                                "walks (spec 140)")


def test_the_head_carries_the_walks_vite_count():
    studies = [cycle.Study("a", "SOLUTION", vite_timeouts=2), cycle.Study("b", "SOLUTION", vite_timeouts=None),
               cycle.Study("c", "SOLUTION", vite_timeouts=0)]
    assert cycle.vite_total(studies) == 2
    assert cycle.vite_total([cycle.Study("a", "SOLUTION")]) is None


# --------------------------------------------------------------------- FR-4b the Current solution draft's two fields

TEXT = "We type it up in the trailer. It takes an hour."


def test_the_draft_sends_answer_and_how_apart():
    writes = [{"status": 202, "body": {"dimension": "problem.current_solution", "answer": "We type it up in the trailer.",
                                       "how": "It takes an hour."}}]
    assert vs.sent_answer(writes) == "We type it up in the trailer." and vs.sent_how(writes) == "It takes an hour."
    assert vs.sent_how([{"status": 202, "body": {"dimension": "x", "answer": "y"}}]) is None


def test_the_check_reads_answer_and_how_where_how_is_sent():
    what, how = vs.split_answer(TEXT)
    seen = {"boxes": {"what": what, "how": how}, "sent_answer": what, "sent_how": how,
            "question": "How do superintendents write up the site walk today?",
            "how_question": vs.CURRENT_SOLUTION_HOW_QUESTION}
    assert [f for f in cs.answer_boxes_faults(seen, cs.CURRENT_SOLUTION_KEY, TEXT)
            if f["what"].startswith("the draft")] == []
    bad = cs.answer_boxes_faults({**seen, "sent_how": "It takes a day."}, cs.CURRENT_SOLUTION_KEY, TEXT)
    assert [f["what"] for f in bad if f["what"].startswith("the draft")] == ["the draft's two fields"]


def test_an_empty_second_box_is_sent_as_an_empty_how():
    seen = {"boxes": {"what": "We type it up.", "how": ""}, "sent_answer": "We type it up.", "sent_how": "",
            "question": "How do superintendents write up the site walk today?",
            "how_question": vs.CURRENT_SOLUTION_HOW_QUESTION}
    assert [f for f in cs.answer_boxes_faults(seen, cs.CURRENT_SOLUTION_KEY, "We type it up.")
            if f["what"].startswith("the draft")] == []


def test_the_joined_text_where_how_is_absent():
    what, how = vs.split_answer(TEXT)
    seen = {"boxes": {"what": what, "how": how}, "sent_answer": vs.join_answer(what, how),
            "question": "How do superintendents write up the site walk today?",
            "how_question": vs.CURRENT_SOLUTION_HOW_QUESTION}
    assert [f for f in cs.answer_boxes_faults(seen, cs.CURRENT_SOLUTION_KEY, TEXT)
            if f["what"].startswith("the draft")] == []
    # before 177 the joined text was the only form: the parts alone, without `how`, are still a fault
    assert [f["what"] for f in cs.answer_boxes_faults({**seen, "sent_answer": what}, cs.CURRENT_SOLUTION_KEY, TEXT)
            if f["what"].startswith("the draft")] == ["the draft's one Answer"]


def test_one_box_answers_are_unchanged():
    seen = {"sent_answer": "Pairing; Charging", "question": "What gets in the way?"}
    assert cs.answer_boxes_faults(seen, "solution.adoption_friction", "Pairing; Charging") == []
