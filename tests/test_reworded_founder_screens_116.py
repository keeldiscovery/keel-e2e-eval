"""Spec 116 -- the walk reads the reworded founder screens of keel-web 149 and 150.

FR-1: `Corridor.list_choose` walked in Chromium against a page shaped as keel-web 149's `ChooseList` (the title *Which one
do you want to test?*, the recall line, the roles first and *Nobody else* LAST with each row's belief under it, the
*Keel will test* box and the bar's three cases, the `PUT calibration/{vector}` carrying the SERVED `pickedIndex`): the
pick by label, the served index read off the wire (never the drawn position), `corpus_scenario.choose_faults` holding
each against 149. FR-2: `Corridor.list_answer` against 150's two boxes (`answer-what`, `answer-how`): the corpus Answer
split at its first full stop as 150's `splitAnswer` does, the draft POST's one text (`joinAnswer`), the question named;
the one box of a page before 150 typed as before. FR-4: the founder screens of record (`backtest.founder_answer`,
`read_back`).
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

BASE = "http://keel.test"
BUYER = "commercial.buyer_payer_alignment"
CURRENT = "problem.current_solution_satisfaction"
ROLES = ["Their partner", "The CFO"]
SERVED = ["Nobody else", *ROLES]                    # the list as served: the fixed row first (the wire's order)
DECIDERS = "partners who pay the household bills"
OFFER = "Lullaby"
TEMPLATE = "The partner who pays the household bills decides, and {value} has to agree."


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


# ------------------------------------------------------------------------------------------- FR-1: 149's Choose

#: keel-web 149's Buyer and payer Choose, as far as the walker reads it: `.listcheck__title`, the recall line
#: (`choose-recall`), the radiogroup drawn in `chooseOrder` (the served rows, the fixed first last), a
#: `choose-belief` under each radio, the *Keel will test* box (`.keeltest__t`, `.keeltest__b`: `buyerPayerBar`) and
#: Continue, which PUTs the list as served with the served `pickedIndex`. `%(opts)s`: `title`, `order` (drawn order of
#: served indexes), `offer`, `deciders`, `wrongIndex` (a page that sends the drawn position).
_CHOOSE = """<!doctype html><html><head><meta charset="utf-8"></head><body><div id="app"></div><script>
const O = %(opts)s;
const rows = O.rows; let pick = null;
const pid = location.pathname.split('/')[2];
const lower = (t) => /^[A-Z][A-Z]/.test(t) ? t : t.charAt(0).toLowerCase() + t.slice(1);
const fill = (t, v) => { const s = t.replace('{value}', lower(v)); return s.charAt(0).toUpperCase() + s.slice(1); };
const bar = () => {
  const who = pick === null ? 'the one you pick' : pick === 0 ? 'nobody else' : lower(rows[pick]);
  return `Holds if at least 2 in 3${O.deciders ? ' ' + O.deciders : ''} say ${who} had to agree the last time`
    + `${O.offer ? ' they bought ' + O.offer : ''}.`;
};
const belief = (i) => i === 0 ? O.template.slice(0, O.template.indexOf(', and {value}')) + ' alone.' : fill(O.template, rows[i]);
function render() {
  const app = document.getElementById('app');
  if (/\\/next$/.test(location.pathname)) { app.innerHTML = '<main><h1>Next</h1></main>'; return; }
  const radios = O.order.map((i) => `<button type="button" role="radio" class="calib__opt" aria-checked="${pick === i}"
      aria-describedby="b-${i}" data-i="${i}"><i aria-hidden="true"></i>${rows[i]}</button>
      <p class="calib__optbelief" id="b-${i}" data-testid="choose-belief">${belief(i)}</p>`).join('');
  app.innerHTML = `<main class="corridor"><section class="ccard"><div class="ccard__body"><div class="listcheck">
    <p class="listcheck__title" id="t">${O.title}</p>
    <p class="calib__derived" data-testid="choose-recall">Who decides: the partner who pays the household bills, from your
      who-decides answer. Who else has to agree: ${rows.slice(1).join(', ')}, from your last answer.</p>
    <div class="calib__opts" role="radiogroup" aria-labelledby="t">${radios}</div></div>
    <div class="keeltest"><p class="keeltest__t">${pick === null ? 'Pick one and the test appears here.' : belief(pick)}</p>
      <p class="keeltest__b">${bar()}</p></div></div>
    <div class="ccard__foot"><button type="button" class="btn primary" ${pick === null ? 'disabled' : ''}>Continue</button>
    </div></section></main>`;
  app.querySelectorAll('[role=radio]').forEach((b) => b.addEventListener('click', () => { pick = Number(b.dataset.i); render(); }));
  app.querySelector('.btn.primary').addEventListener('click', async () => {
    const sent = O.wrongIndex ? O.order.indexOf(pick) : pick;
    const r = await fetch(`/v2/projects/${pid}/calibration/COMMERCIAL`, {method: 'PUT',
      headers: {'content-type': 'application/json'}, body: JSON.stringify({expectedRevision: 7, answers: [
        {dimension: '%(dim)s', list: {items: rows.map((label) => ({label})), pickedIndex: sent}}]})});
    await r.json(); history.pushState({}, '', `/p/${pid}/next`); render();
  });
}
render();
</script></body></html>"""


def _choose(browser, tmp_path, label, **opts):
    page = browser.new_page()
    sent: list = []
    defaults = {"title": vs_screens.BUYER_PAYER_CHOOSE_PROMPT, "rows": SERVED, "order": [1, 2, 0],
                "deciders": DECIDERS, "offer": OFFER, "template": TEMPLATE}

    def serve(route):
        request = route.request
        if request.method == "PUT" and "/calibration/" in request.url:
            sent.append(request.post_data_json)
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"revision": 8}))
        else:
            route.fulfill(status=200, content_type="text/html",
                          body=_CHOOSE % {"opts": json.dumps({**defaults, **opts}), "dim": BUYER})
    page.route(f"{BASE}/**", serve)
    page.goto(f"{BASE}/p/p1/define/commercial/q/3/choose", wait_until="load")
    try:
        corridor = vs_screens.Corridor(page, Recorder(tmp_path), BASE)
        shots: list = []
        corridor.camera = shots.append
        seen = corridor.list_choose({"dimension": BUYER}, label)
        return seen, sent, shots
    finally:
        page.close()


@pytest.mark.parametrize("label, served", [("The CFO", 2), ("Their partner", 1), ("Nobody else", 0)])
def test_the_walk_picks_by_label_and_records_the_served_index_off_the_wire(browser, tmp_path, label, served):
    seen, sent, shots = _choose(browser, tmp_path, label)
    assert seen["prompt"] == "Which one do you want to test?"
    # roles first, Nobody else LAST -- the drawn position is not the served index
    assert seen["options"] == ["Their partner", "The CFO", "Nobody else"]
    assert seen["label"] == label and seen["drawn_index"] == seen["options"].index(label)
    assert seen["served_index"] == served == sent[0]["answers"][0]["list"]["pickedIndex"]
    assert [(w["method"], w["path"], w["status"]) for w in seen["writes"]] == \
        [("PUT", f"{BASE}/v2/projects/p1/calibration/COMMERCIAL", 200)]
    assert seen["recall"].startswith("Who decides: the partner who pays the household bills, from your who-decides")
    assert seen["recall"].endswith("Who else has to agree: Their partner, The CFO, from your last answer.")
    assert seen["beliefs"] == ["The partner who pays the household bills decides, and their partner has to agree.",
                               "The partner who pays the household bills decides, and the CFO has to agree.",
                               "The partner who pays the household bills decides alone."]
    assert seen["picked_before"] == [] and seen["test_before"]["belief"] == cs.KEEL_TEST_PENDING
    assert cs.choose_faults(seen, BUYER, row=served) == []
    assert shots == [f"choose-{BUYER}"]


def test_the_bar_reads_its_three_cases():
    """149 FR-3 (`buyerPayerBar`): before a pick *the one you pick*, a role in a sentence, *nobody else*; the deciders
    and the offer where served, *... the last time.* where no offer name is stored."""
    read = vs_screens.buyer_payer_bar
    assert read(f"Holds if at least 2 in 3 {DECIDERS} say the one you pick had to agree the last time they bought "
                f"{OFFER}.") == {"case": "unpicked", "who": "the one you pick", "deciders": DECIDERS, "offer": OFFER}
    assert read(f"Holds if at least 2 in 3 {DECIDERS} say the CFO had to agree the last time they bought {OFFER}.") \
        == {"case": "role", "who": "the CFO", "deciders": DECIDERS, "offer": OFFER}
    assert read("Holds if at least 2 in 3 say nobody else had to agree the last time.") == \
        {"case": "nobody", "who": "nobody else", "deciders": None, "offer": None}
    # the old pins: gone from the page (149), so they read as no case at all
    assert read("Holds if at least 2 in 3 say they had to agree last time.") is None
    assert read("Holds if at least 2 in 3 say they decided on their own.") is None


@pytest.mark.parametrize("label, row, bar_after", [
    ("The CFO", 2, "role"), ("Nobody else", 0, "nobody")])
def test_the_bar_on_the_walked_page_is_the_pick_s_case(browser, tmp_path, label, row, bar_after):
    seen, _, _ = _choose(browser, tmp_path, label, offer=None)
    assert vs_screens.buyer_payer_bar(seen["test_before"]["bar"])["case"] == "unpicked"
    after = vs_screens.buyer_payer_bar(seen["test"]["bar"])
    assert after["case"] == bar_after and after["offer"] is None
    assert seen["test"]["bar"].endswith("had to agree the last time.")
    assert cs.choose_faults(seen, BUYER, row=row) == []


@pytest.mark.parametrize("opts, what", [
    ({"title": "Who has to agree?"}, "the Choose title"),                       # the title before 149
    ({"order": [0, 1, 2]}, "Nobody else drawn last"),                          # Nobody else first again
    ({"wrongIndex": True}, "the served pickedIndex"),                          # the drawn position sent
])
def test_a_choose_not_as_149_draws_it_is_a_fault(browser, tmp_path, opts, what):
    seen, _, _ = _choose(browser, tmp_path, "The CFO", **opts)
    assert what in [f["what"] for f in cs.choose_faults(seen, BUYER, row=2)]


def test_the_faults_name_a_missing_recall_belief_and_a_wrong_bar():
    good = {"screen": "choose", "label": "The CFO", "prompt": vs_screens.BUYER_PAYER_CHOOSE_PROMPT,
            "options": ["Their partner", "The CFO", "Nobody else"], "drawn_index": 1, "served_index": 2,
            "recall": "Who decides: x, from your who-decides answer. Who else has to agree: Their partner, The CFO, "
                      "from your last answer.",
            "beliefs": ["a", "b", "c"],
            "test_before": {"bar": "Holds if at least 2 in 3 say the one you pick had to agree the last time."},
            "test": {"bar": "Holds if at least 2 in 3 say the CFO had to agree the last time."}}
    assert cs.choose_faults(good, BUYER, row=2) == []
    for change, what in [({"recall": ""}, "the recall line"), ({"beliefs": ["a", "b"]}, "a belief under each row"),
                         ({"test": {"bar": "Holds if at least 2 in 3 say nobody else had to agree the last time."}},
                          "the bar after the pick"),
                         ({"test_before": {"bar": "Holds if at least 2 in 3 say they had to agree last time."}},
                          "the bar before a pick"),
                         ({"served_index": None}, "the served pickedIndex")]:
        assert what in [f["what"] for f in cs.choose_faults({**good, **change}, BUYER, row=2)], change


def test_another_dimension_s_choose_is_held_to_its_served_index_alone():
    seen = {"label": "Pair the glasses", "options": ["Pair the glasses", "Charge it"], "drawn_index": 0,
            "served_index": 0, "prompt": "Which one is most likely to stop them?", "recall": "", "beliefs": []}
    assert cs.choose_faults(seen, "solution.adoption_friction", row=0) == []
    assert [f["what"] for f in cs.choose_faults(seen, "solution.adoption_friction", row=1)] == \
        ["the served pickedIndex"]


def test_the_leg_holds_each_choose_and_answer_in_one_step():
    """Wired into `leg_calibrate`: the row the label was found at kept on the Choose screen, then one step holding every
    typed Answer and every Choose of the stage."""
    source = inspect.getsource(cs.leg_calibrate)
    assert "label, row = _choose_label(j, question, answer)" in source
    assert 'seen[-1]["row"] = row' in source
    held = source[source.index("each Answer sends its one text"):]
    assert "answer_boxes_faults(screen, key, answers[key].text)" in held
    assert 'choose_faults(screen, key, row=screen.get("row"))' in held
    assert "assert not faults" in held


# ------------------------------------------------------------------------------------- FR-2: 150's two boxes

@pytest.mark.parametrize("text, what, how", [
    ("your way of following that conversation; Followed nearly everything said",
     "your way of following that conversation; Followed nearly everything said", ""),
    ("Hearing aids, lipreading, captions on a phone. In a group they catch the gist at best and nod along.",
     "Hearing aids, lipreading, captions on a phone.", "In a group they catch the gist at best and nod along."),
    ("One. Two. Three", "One.", "Two. Three"),
    ("v2.1 tools only", "v2.1 tools only", ""),                      # a stop with no space after is no sentence's end
])
def test_the_answer_splits_at_its_first_full_stop_and_joins_back(text, what, how):
    """150 FR-3 (`splitAnswer` / `joinAnswer`): the first box keeps the stop, the rest is the second; joined back it is
    the one text."""
    assert vs_screens.split_answer(text) == (what, how)
    assert vs_screens.join_answer(what, how) == text
    assert vs_screens.join_answer("Hearing aids", "It goes badly") == "Hearing aids. It goes badly"
    assert vs_screens.join_answer("Hearing aids", "") == "Hearing aids"


#: keel-web 150's Answer screen of Current solution: the question (*How do {actor_plural} {job} today?*), the first box
#: (`.calib__answerbox`, `answer-what`), the second under *And how well does that usually go?* (`.calib__howbox`,
#: `answer-how`), Continue, which POSTs `calibration/PROBLEM/draft` with the two joined (`joinAnswer`) and opens Check.
#: `two: false` is the page before 150 (one box). `firstOnly`: a page that drops the second box.
_ANSWER = """<!doctype html><html><head><meta charset="utf-8"></head><body><div id="app"></div><script>
const O = %(opts)s;
const pid = location.pathname.split('/')[2];
const join = (a, b) => { a = a.trim(); b = b.trim(); if (!b) return a; if (!a) return b;
  return /[.!?]$/.test(a) ? `${a} ${b}` : `${a}. ${b}`; };
function render() {
  const app = document.getElementById('app');
  if (/\\/check$/.test(location.pathname)) { app.innerHTML = '<main><h1>Check</h1></main>'; return; }
  app.innerHTML = `<main class="corridor"><section class="ccard"><div class="ccard__body">
    <h1 class="calib__q">${O.question}</h1><p class="calib__hint">${O.two ? 'What they do: the tools, the habits, the workarounds.' : 'What they do, and how well it works.'} Up to 25 words.</p>
    <label class="calib__answer"><textarea class="calib__answerbox" ${O.two ? 'data-testid="answer-what"' : ''}></textarea></label>
    <p class="calib__wc">0 / 25 words</p>`
    + (O.two ? `<h2 class="calib__howq" data-testid="answer-how-q">And how well does that usually go?</h2>
    <p class="calib__hint">Where it falls short, in a sentence. Up to 25 words.</p>
    <label class="calib__answer"><textarea class="calib__howbox" data-testid="answer-how"></textarea></label>
    <p class="calib__wc">0 / 25 words</p>` : '')
    + `<button type="button" class="calib__chip">Leave this out of the study</button></div>
    <div class="ccard__foot"><button type="button" class="btn primary">Continue</button></div></section></main>`;
  app.querySelector('.btn.primary').addEventListener('click', async () => {
    const what = app.querySelector('.calib__answerbox').value;
    const how = O.two && !O.firstOnly ? app.querySelector('.calib__howbox').value : '';
    const r = await fetch(`/v2/projects/${pid}/calibration/PROBLEM/draft`, {method: 'POST',
      headers: {'content-type': 'application/json'},
      body: JSON.stringify({dimension: '%(dim)s', answer: O.two ? join(what, how) : what.trim()})});
    await r.json(); history.pushState({}, '', `/p/${pid}/define/problem/q/4/check`); render();
  });
}
render();
</script></body></html>"""

ASKED = "How do deaf or hard-of-hearing adults follow a conversation with hearing people today?"


def _answer(browser, tmp_path, text, **opts):
    page = browser.new_page()
    sent: list = []
    defaults = {"two": True, "question": ASKED}

    def serve(route):
        request = route.request
        if request.method == "POST" and request.url.endswith("/draft"):
            sent.append(request.post_data_json)
            route.fulfill(status=202, content_type="application/json", body=json.dumps({"interaction_id": "i1"}))
        else:
            route.fulfill(status=200, content_type="text/html",
                          body=_ANSWER % {"opts": json.dumps({**defaults, **opts}), "dim": CURRENT})
    page.route(f"{BASE}/**", serve)
    page.goto(f"{BASE}/p/p1/define/problem/q/4/answer", wait_until="load")
    try:
        corridor = vs_screens.Corridor(page, Recorder(tmp_path), BASE)
        corridor.camera = lambda slug: None
        return corridor.list_answer({"dimension": CURRENT}, text), sent
    finally:
        page.close()


TWO = "Hearing aids, lipreading, captions on a phone. In a group they catch the gist at best and nod along."
CORPUS = "your way of following that conversation; Followed nearly everything said; Missed a little, caught up quickly"


@pytest.mark.parametrize("text, what, how", [(TWO, "Hearing aids, lipreading, captions on a phone.",
                                              "In a group they catch the gist at best and nod along."),
                                             (CORPUS, CORPUS, "")])
def test_the_walk_types_the_two_boxes_and_the_draft_carries_one_text(browser, tmp_path, text, what, how):
    seen, sent = _answer(browser, tmp_path, text)
    assert seen["boxes"] == {"what": what, "how": how}
    assert seen["how_question"] == "And how well does that usually go?"
    assert seen["question"] == ASKED
    assert sent == [{"dimension": CURRENT, "answer": text}]
    assert seen["sent_answer"] == text
    assert [(w["method"], w["path"], w["status"]) for w in seen["sent"]] == \
        [("POST", f"{BASE}/v2/projects/p1/calibration/PROBLEM/draft", 202)]
    assert cs.answer_boxes_faults(seen, CURRENT, text) == []


def test_a_page_before_150_takes_the_answer_in_its_one_box(browser, tmp_path):
    seen, sent = _answer(browser, tmp_path, TWO, two=False, question="How do they deal with it today?")
    assert "boxes" not in seen and sent == [{"dimension": CURRENT, "answer": TWO}]
    assert seen["sent_answer"] == TWO
    assert cs.answer_boxes_faults(seen, CURRENT, TWO) == []


def test_a_page_that_drops_the_second_box_or_asks_the_old_question_is_a_fault(browser, tmp_path):
    seen, _ = _answer(browser, tmp_path, TWO, firstOnly=True, question="How do they deal with it today?")
    whats = [f["what"] for f in cs.answer_boxes_faults(seen, CURRENT, TWO)]
    assert whats == ["the draft's one Answer", "the question names the people and the job"]


def test_another_list_answer_is_held_to_its_one_text():
    seen = {"question": "What gets in the way?", "sent_answer": "Pairing; Charging", "sent": [{}]}
    assert cs.answer_boxes_faults(seen, "solution.compatibility", "Pairing; Charging") == []
    assert [f["what"] for f in cs.answer_boxes_faults({**seen, "sent_answer": "Pairing"}, "solution.compatibility",
                                                     "Pairing; Charging")] == ["the draft's one Answer"]


# ------------------------------------------------------------------------------------- the screens of record

def _j(framing):
    answers = [vs.CalibrationAnswer(dimension=CURRENT, body={"dimension": CURRENT, "list": {"items": []}}, text=TWO),
               vs.CalibrationAnswer(dimension=BUYER, body={"dimension": BUYER, "list": {
                   "items": [{"label": label} for label in SERVED], "pickedIndex": 2}}, text="Their partner; The CFO")]
    founder = SimpleNamespace(calibration={"PROBLEM": answers[:1], "COMMERCIAL": answers[1:]})
    return SimpleNamespace(founder=founder, framing=framing)


def test_the_answer_screen_of_record_carries_both_boxes():
    j = _j({CURRENT: [{"screen": "answer", "boxes": {"what": "Hearing aids, lipreading, captions on a phone.",
                                                    "how": "In a group they catch the gist at best and nod along."},
                       "sent_answer": TWO}]})
    assert bt.founder_answer(j, f"answer-{CURRENT}") == {
        "what they do (first box)": "Hearing aids, lipreading, captions on a phone.",
        "how well it goes (second box)": "In a group they catch the gist at best and nod along.",
        "sent as one Answer": TWO}
    # a walk on one box (keel-web before 150), or no walk at all: the one text, as before
    assert bt.founder_answer(_j({CURRENT: [{"screen": "answer"}]}), f"answer-{CURRENT}") == TWO
    assert bt.founder_answer(_j({}), f"answer-{CURRENT}") == TWO


def test_the_choose_screen_of_record_names_the_label_and_the_served_index():
    j = _j({BUYER: [{"screen": "choose", "label": "The CFO", "drawn_index": 1, "served_index": 2,
                     "recall": "Who decides: ...", "beliefs": ["a", "b", "c"],
                     "test": {"belief": "b", "bar": "Holds ..."}, "frame": {"progress": "Money · 3 of 5"}}]})
    assert bt.founder_answer(j, f"choose-{BUYER}") == {
        "pickedIndex": 2, "the file's item": "The CFO", "picked on screen (by label)": "The CFO",
        "drawn at": 1, "served pickedIndex (the wire)": 2}
    back = bt.read_back(j, f"choose-{BUYER}", {})
    assert back["recall"] == "Who decides: ..." and back["beliefs on screen"] == ["a", "b", "c"]
    assert back["keel will test"] == "b" and back["bar"] == "Holds ..."
