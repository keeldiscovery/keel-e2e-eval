"""Spec 114 -- the lock walk picks Yes or No on the pilot screen, and reads the window card once.

FR-1: `Corridor.word_pilot_and_lock` walked in Chromium against a page shaped as keel-web 146's `BeforeStep` (the pilot
screen and who asks on one document, the URL moved by the history API as react-router does): the two cards unticked
and Continue held on open, the pick and *Continue · Yes* / *Continue · No*, the `PUT /word` on *No* only, the quoted
first step; `corpus_scenario.pilot_pick_faults` holds each against 146, and the back-test records `{step, picked}` as
the `ready-pilot` screen's founder answer. FR-2: the context card's muted window line, owed on every windowed card
until keel-web 147 is built, then only under a sentence that does not end *We'll ask about the last ...*.
"""

from __future__ import annotations

import copy
import dataclasses
import inspect
import json
import re
from pathlib import Path
from types import SimpleNamespace

import pytest
from playwright.sync_api import sync_playwright

from evals import backtest as bt
from evals import corpus_scenario as cs
from evals import scope_journey as sj
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from harness.steps import Recorder
from stack.config import load_config

BASE = "http://keel.test"
STEP = "install the app"
CONFIG = load_config(validate=False)


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture(scope="module")
def countly():
    _corpus, entry = vs.entry_for(CONFIG.keel_cloud, "01-countly")
    return entry


#: keel-web 146's step 5, as far as the walker reads it: `define/ready/word` answers with the first screen; the pilot
#: screen (*1 of 2*, *Offer a pilot?*, the quoted step, the two radio cards unticked, `before-continue` disabled until a
#: pick, then *Continue · Yes* / *· No*; a tap writes `PUT /word` only where the pick differs from the stored opt-in);
#: who asks (*2 of 2*, its title, *Lock and write the questions*), the lock's POST and *Sent*. `%(opts)s`: `stored`
#: (the stored `pilotEnabled`), `step` (the quoted step or null), `preticked` / `unheld` (a page not as 146 draws it).
_PAGE = """<!doctype html><html><head><meta charset="utf-8"></head><body><div id="app"></div><script>
const O = %(opts)s;
const S = {pick: O.preticked === undefined ? null : O.preticked, stored: O.stored};
const pid = location.pathname.split('/')[2];
const go = (path) => { history.pushState({}, '', path); render(); };
if (/\\/define\\/ready\\/word\\/?$/.test(location.pathname)) history.replaceState({}, '', `/p/${pid}/define/ready/pilot`);
async function persist(yes) {
  if (yes === S.stored) return;
  const r = await fetch(`/v2/projects/${pid}/word`, {method: 'PUT', headers: {'content-type': 'application/json'},
    body: JSON.stringify({expectedRevision: 3, pitch: null, incentive: null, pilotEnabled: yes})});
  await r.json(); S.stored = yes;
}
function render() {
  const app = document.getElementById('app');
  const path = location.pathname;
  if (/\\/interviews\\/sent$/.test(path)) { app.innerHTML = '<h1>Sent</h1>'; return; }
  if (/\\/define\\/ready\\/interviewer$/.test(path)) {
    app.innerHTML = `<main class="corridor before"><p data-testid="before-counter">2 of 2</p>
      <h1>Who should ask them your questions?</h1><p class="ccard__sub">This account runs on its own AI.</p>
      <div class="ccard__foot"><button class="btn primary" data-testid="lock-and-record">Lock and write the questions
      </button></div></main>`;
    app.querySelector('[data-testid=lock-and-record]').addEventListener('click', async () => {
      const r = await fetch(`/v2/projects/${pid}/lock`, {method: 'POST', headers: {'content-type': 'application/json'},
                                                         body: JSON.stringify({expectedRevision: 4})});
      await r.json(); go(`/p/${pid}/interviews/sent`);
    });
    return;
  }
  const label = S.pick === null ? 'Continue' : `Continue · ${S.pick ? 'Yes' : 'No'}`;
  const held = S.pick === null && !O.unheld;
  const card = (yes) => `<button type="button" role="radio" class="calib__opt" data-testid="pilot-${yes ? 'yes' : 'no'}"
      aria-checked="${S.pick === yes}"><i aria-hidden="true"></i><span class="fmt__t"><span class="fmt__name">${yes
      ? 'Yes, ask them' : 'No pilot'}</span></span></button>`;
  app.innerHTML = `<main class="corridor before"><p data-testid="before-counter">1 of 2</p><h1>Offer a pilot?</h1>
    <p class="ccard__sub">People who say yes get a line at the end.</p>
    <section class="ccard before__card" aria-label="Offer a pilot?">`
    + (O.step ? `<p class="before__step" data-testid="pilot-first-step">Your first step: ${O.step}</p>` : '')
    + `<div class="calib__opts" role="radiogroup" aria-label="Offer a pilot?" data-testid="pilot-pick">${card(true)}${card(false)}
    </div>` + (O.offerBox ? '<input type="text" id="pilot-offer">' : '') + `</section>
    <div class="ccard__foot"><button type="button" class="btn primary" data-testid="before-continue"
      ${held ? 'disabled' : ''}>${label}</button></div></main>`;
  app.querySelectorAll('[role=radio]').forEach((b) => b.addEventListener('click', () => {
    const yes = b.dataset.testid === 'pilot-yes'; S.pick = yes; render(); void persist(yes); }));
  app.querySelector('[data-testid=before-continue]').addEventListener('click', () => {
    if (S.pick === null && !O.unheld) return; go(`/p/${pid}/define/ready/interviewer`); });
}
render();
</script></body></html>"""


def _page(browser, **opts):
    page = browser.new_page()
    sent: list = []

    def serve(route):
        request = route.request
        if request.method == "PUT" and request.url.endswith("/word"):
            sent.append(request.post_data_json)
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"revision": 4}))
        elif request.method == "POST" and request.url.endswith("/lock"):
            route.fulfill(status=201, content_type="application/json", body=json.dumps({"version": 1}))
        else:
            route.fulfill(status=200, content_type="text/html",
                          body=_PAGE % {"opts": json.dumps({"stored": True, **opts})})
    page.route(f"{BASE}/**", serve)
    page.goto(f"{BASE}/p/p1/define/ready/pilot", wait_until="load")
    return page, sent


def _walk(browser, tmp_path, *, yes=True, step=STEP, **opts):
    page, sent = _page(browser, step=step, **opts)
    try:
        corridor = vs_screens.Corridor(page, Recorder(tmp_path), BASE)
        shots: list = []
        corridor.camera = shots.append
        drawn = corridor.word_pilot_and_lock(pilot=True, pilot_yes=yes, step=step is not None)
        return drawn, sent, shots, page.url
    finally:
        page.close()


# ---------------------------------------------------------------------------------- FR-1: the pilot pick, walked

@pytest.mark.parametrize("yes", [True, False])
def test_the_walk_reads_the_screen_as_it_opens_picks_and_presses_the_named_continue(browser, tmp_path, yes):
    drawn, sent, shots, url = _walk(browser, tmp_path, yes=yes)
    pilot = drawn["ready"]["pilot"]
    assert drawn["counters"] == ["1 of 2", "2 of 2"] and drawn["status"] == 201
    assert url == f"{BASE}/p/p1/interviews/sent"
    assert pilot["group"] == {"role": "radiogroup", "label": "Offer a pilot?"}
    # the cards' states on open, Continue disabled
    assert [(c["testid"], c["role"], c["text"], c["checked"]) for c in pilot["opened"]["cards"]] == \
        [("pilot-yes", "radio", "Yes, ask them", "false"), ("pilot-no", "radio", "No pilot", "false")]
    assert pilot["opened"]["continue"] == {"text": "Continue", "disabled": True}
    assert (pilot["textboxes"], pilot["checkboxes"]) == (0, 0)
    # the pick and the label
    label = "Continue · Yes" if yes else "Continue · No"
    assert pilot["picked"] == ("Yes" if yes else "No") and pilot["pressed"] == label
    assert [(c["testid"], c["checked"]) for c in pilot["after"]["cards"]] == \
        [("pilot-yes", "true" if yes else "false"), ("pilot-no", "false" if yes else "true")]
    assert pilot["after"]["continue"] == {"text": label, "disabled": False}
    # the PUT on No, none on Yes (a new project's stored opt-in is already true)
    assert sent == ([] if yes else [{"expectedRevision": 3, "pitch": None, "incentive": None, "pilotEnabled": False}])
    assert [(w["method"], w["path"], w["status"]) for w in pilot["writes"]] == \
        ([] if yes else [("PUT", f"{BASE}/v2/projects/p1/word", 200)])
    # the quoted step
    assert pilot["step_line"] == f"Your first step: {STEP}" and pilot["step"] == STEP
    assert cs.pilot_pick_faults(pilot, yes=yes, step=STEP) == []
    # the screen stays a founder screen of record, shot before the pick
    assert shots == ["ready-pilot", "ready-interviewer"]


def test_no_step_is_quoted_where_none_is_stored_or_the_money_is_out_of_scope(browser, tmp_path):
    drawn, _, _, _ = _walk(browser, tmp_path, step=None)
    pilot = drawn["ready"]["pilot"]
    assert pilot["step_line"] is None and pilot["step"] is None
    assert cs.pilot_pick_faults(pilot, yes=True, step=None) == []
    assert cs.pilot_pick_faults(pilot, yes=True, step=STEP)          # a stored step the screen never quoted


def test_a_quoted_step_where_none_is_owed_is_a_fault(browser, tmp_path):
    drawn, _, _, _ = _walk(browser, tmp_path)
    faults = cs.pilot_pick_faults(drawn["ready"]["pilot"], yes=True, step=None)
    assert [f["what"] for f in faults] == ["the quoted first step"]


def test_plain_continue_goes_nowhere_until_a_pick(browser, tmp_path):
    """146: a walk that pressed plain *Continue* on the pilot screen finds it disabled -- the press moves nothing."""
    page, sent = _page(browser, step=None)
    try:
        button = page.get_by_test_id("before-continue")
        assert button.is_disabled() and button.inner_text().strip() == "Continue"
        button.click(force=True)
        page.wait_for_timeout(200)
        assert page.url.endswith("/define/ready/pilot") and sent == []
    finally:
        page.close()


@pytest.mark.parametrize("opts, what", [
    ({"preticked": True}, "the cards on open"),                         # a card ticked as the screen opens
    ({"unheld": True}, "Continue on open"),                             # Continue live before a pick
    ({"offerBox": True}, "text boxes on the screen"),                   # the offer box came back
])
def test_a_screen_not_as_146_draws_it_is_a_fault(browser, tmp_path, opts, what):
    drawn, _, _, _ = _walk(browser, tmp_path, **opts)
    assert what in [f["what"] for f in cs.pilot_pick_faults(drawn["ready"]["pilot"], yes=True, step=STEP)]


def test_yes_on_a_stored_opt_out_writes_and_is_named(browser, tmp_path):
    """The walk's projects are new (stored true); a Yes that writes is a fault the leg names, never passed over."""
    drawn, sent, _, _ = _walk(browser, tmp_path, stored=False)
    assert sent == [{"expectedRevision": 3, "pitch": None, "incentive": None, "pilotEnabled": True}]
    faults = cs.pilot_pick_faults(drawn["ready"]["pilot"], yes=True, step=STEP)
    assert [f["what"] for f in faults] == ["PUT /word on Yes"]


_GOOD_NO = {"group": {"role": "radiogroup"}, "step_line": None, "step": None, "textboxes": 0, "checkboxes": 0,
            "opened": {"cards": [{"testid": "pilot-yes", "role": "radio", "text": "Yes, ask them", "checked": "false"},
                                 {"testid": "pilot-no", "role": "radio", "text": "No pilot", "checked": "false"}],
                       "continue": {"text": "Continue", "disabled": True}},
            "picked": "No", "pressed": "Continue · No",
            "after": {"cards": [{"testid": "pilot-yes", "checked": "false"}, {"testid": "pilot-no", "checked": "true"}],
                      "continue": {"text": "Continue · No", "disabled": False}},
            "writes": [{"method": "PUT", "path": "/v2/projects/p1/word", "status": 200,
                        "body": {"pitch": None, "incentive": None, "pilotEnabled": False}}]}


@pytest.mark.parametrize("fault", [
    lambda p: p.update(writes=[]),                                                   # No wrote nothing
    lambda p: p["writes"][0]["body"].update(pilotEnabled=True),                      # ... wrote the wrong opt-in
    lambda p: p["writes"][0].update(status=409),                                     # ... was refused
    lambda p: p.update(writes=p["writes"] * 2),                                      # ... wrote twice
    lambda p: p.update(pressed="Continue"),                                          # plain Continue pressed
    lambda p: p["after"]["continue"].update(text="Continue · Yes"),                  # Continue names the other pick
    lambda p: p["after"]["cards"][0].update(checked="true"),                         # both cards ticked
    lambda p: p.update(picked="Yes"),                                                # the other card picked
    lambda p: p["opened"]["cards"].pop(),                                            # one card only
    lambda p: p.update(checkboxes=1),                                                # the old preview checkbox
    lambda p: p.clear(),                                                             # no pilot screen read
])
def test_each_pick_not_as_146_takes_it_is_a_fault(fault):
    pilot = copy.deepcopy(_GOOD_NO)
    assert cs.pilot_pick_faults(pilot, yes=False, step=None) == []
    fault(pilot)
    assert cs.pilot_pick_faults(pilot or None, yes=False, step=None)


def test_the_step_owed_is_the_stored_commitment_step(countly):
    def view(answer):
        return {"questions": [{"dimension": "commercial.price", "answer": {}},
                              {"dimension": "commercial.commitment", "answer": answer}]}
    items = [{"code": "step", "label": "  install   the app "}, {"code": "smaller", "label": "try a demo"}]
    assert cs.commitment_step(view({"list": {"items": items, "pickedIndex": None}})) == "install the app"
    assert cs.commitment_step(view({"list": {"items": items, "pickedIndex": 1}})) == "try a demo"
    assert cs.commitment_step(view({"unsure": True, "list": {"items": items}})) is None      # left out
    assert cs.commitment_step(view({})) is None and cs.commitment_step({}) is None          # unsaved
    assert cs.commitment_step(view({"list": {"items": [{"label": " "}]}})) is None

    read: list = []
    for scope, owed in (("ALL", True), ("COMMERCIAL", True), ("SOLUTION_COMMERCIAL", True), ("SOLUTION", False)):
        j = SimpleNamespace(entry=dataclasses.replace(countly, scope=scope), project=lambda p: f"/v2/projects/p1{p}",
                            get=lambda path: read.append(path) or view({"list": {"items": items}}))
        assert cs.stored_first_step(j) == ("install the app" if owed else None), scope
    assert read == ["/v2/projects/p1/calibration/COMMERCIAL"] * 3                 # SOLUTION makes no read


def test_the_founder_picks_yes_on_every_entry_and_no_where_one_opts_out(countly):
    """No corpus entry records a founder who opts out of the pilot, so the walk picks Yes everywhere (the corpus's
    `pilot_opt_in` people expect the line at the end, spec 067 FR-6); an entry that says so picks No."""
    assert vs.founder_pilot(countly) is True
    assert vs.founder_pilot(SimpleNamespace(founder_pilot=False)) is False
    corpus = Path(CONFIG.keel_cloud) / "canon" / "designs" / "measured-beliefs"
    for path in sorted((corpus / "corpus").glob("*.yaml")) + sorted((corpus / "backtest").glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"^\s*(founder_pilot|pilot_enabled|pilotEnabled|offer_pilot)\s*:", text, re.M), path.name


class _Corridor:
    def __init__(self, pilot):
        self.pilot, self.calls = pilot, []

    def word_pilot_and_lock(self, face=None, *, pilot=True, pilot_yes=True, step=False):
        self.calls.append({"pilot": pilot, "pilot_yes": pilot_yes, "step": step})
        ready = {"landed": "http://w/p/x/define/ready/pilot", "word_redirect": "http://w/p/x/define/ready/pilot",
                 "word_drawn": 0, "pilot": self.pilot}
        return {"counters": ["1 of 2", "2 of 2"], "receipt": {"version": 1}, "l1": {}, "status": 201, "ready": ready}


def _lock_journey(tmp_path, countly, scope, pilot, monkeypatch):
    entry = dataclasses.replace(countly, scope=scope)
    j = cs.Journey(recorder=Recorder(tmp_path), page=None, context=None, web_base="", cloud_base="", entry=entry,
                   founder=None, people=[], project_id="p1", scope=scope)
    items = [{"code": "step", "label": STEP}]
    j.get = lambda path: ({"questions": [{"dimension": "commercial.commitment", "answer": {"list": {"items": items}}}]}
                          if path.endswith("/calibration/COMMERCIAL") else {})
    j.corridor = _Corridor(pilot)
    monkeypatch.setattr(cs, "plan_complete", lambda j: None)
    monkeypatch.setattr(cs, "_own_door_l1", lambda j, drawn: None)
    monkeypatch.setattr(cs, "_lock_lands", lambda j: None)
    return j


def test_leg_lock_asks_for_the_pick_and_holds_it(tmp_path, countly, monkeypatch):
    good_yes = {**copy.deepcopy(_GOOD_NO), "picked": "Yes", "pressed": "Continue · Yes", "writes": [],
                "step_line": f"Your first step: {STEP}", "step": STEP,
                "after": {"cards": [{"testid": "pilot-yes", "checked": "true"}, {"testid": "pilot-no", "checked": "false"}],
                          "continue": {"text": "Continue · Yes", "disabled": False}}}
    j = _lock_journey(tmp_path, countly, "ALL", good_yes, monkeypatch)
    cs.leg_lock(j)
    assert j.corridor.calls == [{"pilot": True, "pilot_yes": True, "step": True}]
    assert j.changed["pilot"] == {"step": STEP, "picked": "Yes", "pressed": "Continue · Yes"}
    # the screen of record's founder answer: {step, picked}
    j.founder = SimpleNamespace(calibration={})
    assert bt.founder_answer(j, "ready-pilot") == {"pilot": {"step": STEP, "picked": "Yes"}, "pressed": "Continue · Yes"}

    j = _lock_journey(tmp_path, countly, "ALL", {**good_yes, "pressed": "Continue"}, monkeypatch)
    with pytest.raises(AssertionError):
        cs.leg_lock(j)                                                  # plain Continue: the leg stops

    j = _lock_journey(tmp_path, countly, "SOLUTION", {**good_yes, "step_line": None, "step": None}, monkeypatch)
    cs.leg_lock(j)
    assert j.corridor.calls == [{"pilot": True, "pilot_yes": True, "step": False}]


def test_the_problem_study_has_no_pilot_pick(tmp_path, countly, monkeypatch):
    j = _lock_journey(tmp_path, sj.problem_entry(countly), "PROBLEM", None, monkeypatch)
    j.corridor.word_pilot_and_lock = lambda face=None, *, pilot=True, **kw: (
        j.corridor.calls.append({"pilot": pilot, **kw}) or
        {"counters": [], "receipt": {"version": 1}, "l1": {}, "status": 201,
         "ready": {"landed": "http://w/p/x/define/ready/interviewer",
                   "word_redirect": "http://w/p/x/define/ready/interviewer", "word_drawn": 0}})
    cs.leg_lock(j)
    assert j.corridor.calls[0]["pilot"] is False and "pilot" not in j.changed


def test_the_walk_never_presses_plain_continue_on_the_pilot_screen():
    source = inspect.getsource(vs_screens.Corridor.word_pilot_and_lock)
    assert "_button(self.page, BEFORE_CONTINUE)" not in source
    assert "self._pilot_opened(step)" in source and "self._pilot_pick(pilot_yes)" in source
    assert vs_screens.pilot_continue(True) == "Continue · Yes" and vs_screens.pilot_continue(False) == "Continue · No"


def test_the_harness_reads_keel_webs_146_words():
    """The cards' words, Continue's and the step's, held to keel-web master's `translate.ts` (146)."""
    path = Path(CONFIG.keel_web) / "src" / "lib" / "translate.ts"
    if not path.is_file():
        pytest.skip("keel-web is not beside this checkout")
    source = path.read_text(encoding="utf-8")
    assert f'BEFORE_PILOT_YES = "{vs_screens.PILOT_CARDS["pilot-yes"]}"' in source
    assert f'BEFORE_PILOT_NO = "{vs_screens.PILOT_CARDS["pilot-no"]}"' in source
    assert 'beforePilotContinue = (yes: boolean): string => `Continue · ${yes ? "Yes" : "No"}`' in source
    assert "beforePilotFirstStep = (step: string): string => `Your first step: ${step}`" in source
    step = (Path(CONFIG.keel_web) / "src" / "components" / "corridor" / "BeforeStep.tsx").read_text(encoding="utf-8")
    for testid in ("pilot-pick", "pilot-first-step", "before-continue"):
        assert f'data-testid="{testid}"' in step, testid
    assert 'data-testid={yes ? "pilot-yes" : "pilot-no"}' in step


# ------------------------------------------------------------------------------------- FR-2: the window line

WINDOW = vs.Window(7, "NIGHTS")
NEW = "Restaurant managers. When a delivery comes in, they want to check it. We'll ask about the last 7 nights."
CURLY = NEW.replace("We'll", "We’ll")
OLD = "Restaurant managers. When a delivery comes in, they want to check it, counting the last 7 nights."
LINE = "Counting the last 7 nights."


def test_keel_web_147_is_on_master_so_the_line_goes_under_168s_sentence_and_stays_on_an_old_one(monkeypatch):
    """FR-2 as built: keel-web 147 merged on 2026-10-31 (web master `d6dc5a9`) while 114 was built -- the card draws no
    *Counting the last ...* line where the sentence ends *We'll ask about the last ...*, and the line on an old one."""
    monkeypatch.delenv("KEEL_WEB_147", raising=False)
    assert cs.WEB_147_BUILT is True and cs.web_147_built()
    for sentence in (NEW, CURLY):
        assert cs.window_line_owed(sentence, WINDOW) is None
        assert cs.window_line_faults(sentence, "", WINDOW) == []
        assert cs.window_line_faults(sentence, LINE, WINDOW)                # said twice
    assert cs.window_line_owed(OLD, WINDOW) == LINE
    assert cs.window_line_faults(OLD, LINE, WINDOW) == []
    assert cs.window_line_faults(OLD, "", WINDOW)                           # an old sentence lost its window


def test_against_a_build_before_147_the_old_pin_stands(monkeypatch):
    """`KEEL_WEB_147=0`: the line owed on every windowed card, whatever the sentence (the pin since spec 071)."""
    monkeypatch.setenv("KEEL_WEB_147", "0")
    assert not cs.web_147_built()
    for sentence in (NEW, CURLY, OLD):
        assert cs.window_line_owed(sentence, WINDOW) == LINE
        assert cs.window_line_faults(sentence, LINE, WINDOW) == []
        assert cs.window_line_faults(sentence, "", WINDOW)                  # the line missing
    assert cs.window_line_owed(NEW, WINDOW, once=True) is None              # `once` given wins over the flag


def test_the_window_sentence_mirror_is_147s():
    assert vs.read_back_says_window(NEW) and vs.read_back_says_window(CURLY) and vs.read_back_says_window(NEW + "  ")
    assert vs.read_back_says_window("We'll ask about the last 4 weeks.")
    assert not vs.read_back_says_window(OLD) and not vs.read_back_says_window(None)
    assert not vs.read_back_says_window(NEW + " More.") and not vs.read_back_says_window("SoWe'll ask about the last 7 nights.")
    path = Path(CONFIG.keel_web) / "src" / "lib" / "contextReach.ts"
    if not path.is_file():
        pytest.skip("keel-web is not beside this checkout")
    source = path.read_text(encoding="utf-8")
    assert "export function readBackSaysWindow" in source
    assert "/(?:^|\\s)We['\\u2019]ll ask about the last [^.]+\\.$/" in source


def test_the_context_leg_holds_the_line_through_the_rule():
    source = inspect.getsource(cs.leg_context)
    assert "window_line_faults(drawn, window_line, founder.window)" in source
    assert "assert vs.window_words(founder.window) in window_line" not in source


def test_money_alone_draws_no_window_line_either_way(tmp_path, countly, monkeypatch):
    """`tests/test_drifts_95_97_closed.py`'s money-alone case (the card's *Counting the last 7 nights.* fails) stands
    before and after 147: money alone serves no window to draw a line for."""
    seed = sj.money_entry(countly)
    for flag in ("0", "1"):                     # before 147 and since
        monkeypatch.setenv("KEEL_WEB_147", flag)
        j = cs.Journey(recorder=Recorder(tmp_path), page=None, context=None, web_base="", cloud_base="", entry=seed,
                       founder=None, people=[], project_id="p1", scope=seed.scope)
        j.corridor = SimpleNamespace(saves=[{"method": "PUT", "status": 202, "sent": {"actor": "a"}}])
        with pytest.raises(AssertionError):
            cs._drift_96_guard(j, vs.read_back(seed, window=False), LINE)
