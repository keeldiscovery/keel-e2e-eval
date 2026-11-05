"""Spec 116 -- the walk reads the reworded founder screens of keel-web 149 and 150.

FR-1: `Corridor.list_choose` walked in Chromium against a page shaped as keel-web 149's `ChooseList` (the title *Which one
do you want to test?*, the recall line, each option's belief under it, the *Keel will test* box and the bar's three
cases, the `PUT calibration/{vector}` carrying the SERVED `pickedIndex`) -- since spec 132 FR-10 as keel-web 168 draws it:
*Nobody else* first and one option holding every role, picked by index, and a Nobody-else-only list a statement
confirmed as 0 -- `corpus_scenario.choose_faults` holding each against 168. FR-2: `Corridor.list_answer` against 150's two boxes (`answer-what`, `answer-how`): the corpus Answer
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


# --------------------------------------------------------------------- FR-1: 149's Choose, as keel-web 168 draws it

#: keel-web 168's Buyer and payer Choose (spec 132 FR-10; 149's title, recall line, beliefs and bar), as far as the walker
#: reads it: `.listcheck__title`, the recall line (`choose-recall`), the radiogroup -- *Nobody else* first (index 0), then
#: ONE option holding every role joined with *and* (index 1), tagged *· has to agree* outside the radio's name -- a
#: `choose-belief` under each, the *Keel will test* box (`buyerPayerBar`, over every role) and Continue, which PUTs the
#: list as served with the pressed `pickedIndex` (0 or 1). A list holding only *Nobody else* draws no radiogroup but a
#: statement to confirm (`choose-confirm`, `choose-statement`, the belief), Continue sending 0. `%(opts)s`: `title`,
#: `order` (drawn order of the two options), `purchase` (keel-web 173's bar, spec 137), `deciders`, `wrongIndex` (a page that sends 2 for the roles),
#: `three` (a page that still draws a radio a role, 149's).
_CHOOSE = """<!doctype html><html><head><meta charset="utf-8"></head><body><div id="app"></div><script>
const O = %(opts)s;
const rows = O.rows; let pick = rows.length === 1 ? 0 : null;
const roles = rows.slice(1);
const pid = location.pathname.split('/')[2];
const lower = (t) => /^[A-Z][A-Z]/.test(t) ? t : t.charAt(0).toLowerCase() + t.slice(1);
const theRole = (r) => /^(the|a|an|their|your|my)\\s/i.test(r) ? lower(r) : 'the ' + lower(r);
const joined = (xs) => xs.length <= 1 ? (xs[0] || '') : xs.slice(0, -1).join(', ') + ' and ' + xs[xs.length - 1];
const together = joined(roles.map(theRole));
const options = O.three ? rows : ['Nobody else', together.charAt(0).toUpperCase() + together.slice(1)];
const fill = (t, v) => { const s = t.replace('{value}', v); return s.charAt(0).toUpperCase() + s.slice(1); };
const bar = () => {
  const who = pick === null ? 'the one you pick' : pick === 0 ? 'nobody else' : together;
  // spec 137 (keel-web 173 FR-5): the purchase named (never the offer), *Decided alone counts* on Nobody else
  return `Holds if at least 2 in 3${O.deciders ? ' ' + O.deciders : ''} say ${who} had to agree the last time they paid`
    + ` for ${O.purchase || 'something for this'}.${pick === 0 ? ' Decided alone counts as support.' : ''}`;
};
const belief = (i) => i === 0 ? O.template.slice(0, O.template.indexOf(', and {value}')) + ' alone.' : fill(O.template, together);
const recall = 'Who decides: the partner who pays the household bills, from your who-decides answer.'
  + (roles.length ? ` Who else has to agree: ${roles.join(', ')}, from your last answer.` : '');
function render() {
  const app = document.getElementById('app');
  if (/\\/next$/.test(location.pathname)) { app.innerHTML = '<main><h1>Next</h1></main>'; return; }
  let list;
  if (!roles.length) {
    list = `<div class="listcheck" data-testid="choose-confirm"><p class="calib__derived" data-testid="choose-recall">${recall}</p>
      <p class="listcheck__title" data-testid="choose-statement">You named nobody else who has to agree, so there is nothing to pick. Continue to test this, or go back and name who has to agree.</p>
      <p class="calib__optbelief" data-testid="choose-belief">${belief(0)}</p></div>`;
  } else {
    const radios = O.order.map((i) => `<button type="button" role="radio" class="calib__opt" aria-checked="${i > 0 ? pick !== null && pick > 0 : pick === 0}"
        aria-describedby="b-${i}" data-i="${i}"><i aria-hidden="true"></i>${options[i]}${i > 0 && !O.three ? '<span class="listrow__tag" data-testid="role-agree" aria-hidden="true">· has to agree</span>' : ''}</button>
        <p class="calib__optbelief" id="b-${i}" data-testid="choose-belief">${belief(i)}</p>`).join('');
    list = `<div class="listcheck"><p class="listcheck__title" id="t">${O.title}</p>
      <p class="calib__derived" data-testid="choose-recall">${recall}</p>
      <div class="calib__opts" role="radiogroup" aria-labelledby="t">${radios}</div></div>`;
  }
  app.innerHTML = `<main class="corridor"><section class="ccard"><div class="ccard__body">${list}
    <div class="keeltest"><p class="keeltest__t">${pick === null ? 'Pick one and the test appears here.' : belief(pick)}</p>
      <p class="keeltest__b">${bar()}</p></div></div>
    <div class="ccard__foot"><button type="button" class="btn primary" ${pick === null ? 'disabled' : ''}>Continue</button>
    </div></section></main>`;
  app.querySelectorAll('[role=radio]').forEach((b) => b.addEventListener('click', () => { pick = Number(b.dataset.i); render(); }));
  app.querySelector('.btn.primary').addEventListener('click', async () => {
    const sent = O.wrongIndex && pick > 0 ? 2 : pick;
    const r = await fetch(`/v2/projects/${pid}/calibration/COMMERCIAL`, {method: 'PUT',
      headers: {'content-type': 'application/json'}, body: JSON.stringify({expectedRevision: 7, answers: [
        {dimension: '%(dim)s', list: {items: rows.map((label) => ({label})), pickedIndex: sent}}]})});
    await r.json(); history.pushState({}, '', `/p/${pid}/next`); render();
  });
}
render();
</script></body></html>"""


def _choose(browser, tmp_path, index, **opts):
    page = browser.new_page()
    sent: list = []
    defaults = {"title": vs_screens.BUYER_PAYER_CHOOSE_PROMPT, "rows": SERVED, "order": [0, 1],
                "deciders": DECIDERS, "purchase": None, "template": TEMPLATE}

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
        seen = corridor.list_choose({"dimension": BUYER}, None, index=index)
        seen["roles"] = [r for r in (opts.get("rows") or SERVED) if r != "Nobody else"]
        return seen, sent, shots
    finally:
        page.close()


JOINED = "Their partner and the CFO"


@pytest.mark.parametrize("index", [1, 0])
def test_the_walk_picks_by_index_and_records_the_served_index_off_the_wire(browser, tmp_path, index):
    """Spec 132 FR-10 (keel-web 168 FR-3): two options, *Nobody else* first and every role in one, picked by index --
    never by a role's label -- and the index pressed is the one served."""
    seen, sent, shots = _choose(browser, tmp_path, index)
    assert seen["prompt"] == "Which one do you want to test?"
    assert seen["options"][0] == "Nobody else" and " ".join(seen["options"][1].split()).startswith(JOINED)
    assert len(seen["options"]) == 2 and seen["index"] == index
    assert seen["served_index"] == index == sent[0]["answers"][0]["list"]["pickedIndex"]
    assert [(w["method"], w["path"], w["status"]) for w in seen["writes"]] == \
        [("PUT", f"{BASE}/v2/projects/p1/calibration/COMMERCIAL", 200)]
    assert seen["recall"].startswith("Who decides: the partner who pays the household bills, from your who-decides")
    assert seen["recall"].endswith("Who else has to agree: Their partner, The CFO, from your last answer.")
    assert seen["beliefs"] == ["The partner who pays the household bills decides alone.",
                               "The partner who pays the household bills decides, and their partner and the CFO has "
                               "to agree."]
    assert seen["picked_before"] == [] and seen["test_before"]["belief"] == cs.KEEL_TEST_PENDING
    assert cs.choose_faults(seen, BUYER, row=index) == []
    assert shots == [f"choose-{BUYER}"]


def test_a_list_of_nobody_else_alone_is_a_statement_confirmed_as_0(browser, tmp_path):
    """Spec 132 FR-10 (keel-web 168 T006): no radiogroup -- the statement and its belief, Continue sending 0."""
    seen, sent, _ = _choose(browser, tmp_path, 0, rows=["Nobody else"])
    assert seen["confirm"] is True and seen["options"] == []
    assert seen["statement"] == vs_screens.BUYER_PAYER_CONFIRM_ONLY
    assert seen["beliefs"] == ["The partner who pays the household bills decides alone."]
    assert seen["served_index"] == 0 == sent[0]["answers"][0]["list"]["pickedIndex"]
    assert cs.choose_faults(seen, BUYER, row=0) == []
    assert [f["what"] for f in cs.choose_faults(seen, BUYER, row=1)] == ["the served pickedIndex", "the pick"]


def test_the_bar_reads_its_three_cases():
    """149 FR-3 (`buyerPayerBar`): before a pick *the one you pick*, a role in a sentence, *nobody else*; the deciders
    where served. Spec 137 (keel-web 173 FR-5, keel-cloud 213 FR-5c): the purchase named -- *something for this*, or the
    founder's purchase noun -- never the offer; *Decided alone counts as support.* on Nobody else."""
    read = vs_screens.buyer_payer_bar
    some = vs_screens.BUYER_PAYER_PURCHASE
    # spec 139 FR-3 (keel-web 175 FR-3): each read says which form it is (`b2b`), the user-pays one here
    assert read(f"Holds if at least 2 in 3 {DECIDERS} say the one you pick had to agree the last time they paid for "
                f"{some}.") == {"case": "unpicked", "who": "the one you pick", "deciders": DECIDERS, "purchase": some,
                                "alone": False, "b2b": False}
    assert read(f"Holds if at least 2 in 3 {DECIDERS} say the CFO had to agree the last time they paid for the "
                "payroll software.") == {"case": "role", "who": "the CFO", "deciders": DECIDERS,
                                         "purchase": "the payroll software", "alone": False, "b2b": False}
    assert read(f"Holds if at least 2 in 3 say nobody else had to agree the last time they paid for {some}. "
                f"{vs_screens.BUYER_PAYER_ALONE_COUNTS}") == \
        {"case": "nobody", "who": "nobody else", "deciders": None, "purchase": some, "alone": True, "b2b": False}
    # the old pins: gone from the page (149, 173), so they read as no case at all
    assert read(f"Holds if at least 2 in 3 {DECIDERS} say the CFO had to agree the last time they bought {OFFER}.") \
        is None
    assert read("Holds if at least 2 in 3 say nobody else had to agree the last time.") is None
    assert read("Holds if at least 2 in 3 say they had to agree last time.") is None
    assert read("Holds if at least 2 in 3 say they decided on their own.") is None


@pytest.mark.parametrize("index, bar_after", [(1, "role"), (0, "nobody")])
def test_the_bar_on_the_walked_page_is_the_pick_s_case(browser, tmp_path, index, bar_after):
    seen, _, _ = _choose(browser, tmp_path, index)
    assert vs_screens.buyer_payer_bar(seen["test_before"]["bar"])["case"] == "unpicked"
    after = vs_screens.buyer_payer_bar(seen["test"]["bar"])
    assert after["case"] == bar_after and after["purchase"] == vs_screens.BUYER_PAYER_PURCHASE
    assert after["alone"] is (bar_after == "nobody")
    assert "the last time they paid for something for this." in seen["test"]["bar"]
    assert cs.choose_faults(seen, BUYER, row=index) == []


@pytest.mark.parametrize("opts, what", [
    ({"title": "Who has to agree?"}, "the Choose title"),                       # the title before 149
    ({"order": [1, 0]}, "Nobody else drawn first"),                            # 149's order: Nobody else last
    ({"wrongIndex": True}, "the served pickedIndex"),                          # a role's own index sent
    ({"three": True, "order": [0, 1, 2]}, "two options at most"),             # a radio a role, as 149 drew
])
def test_a_choose_not_as_168_draws_it_is_a_fault(browser, tmp_path, opts, what):
    seen, _, _ = _choose(browser, tmp_path, 1, **opts)
    assert what in [f["what"] for f in cs.choose_faults(seen, BUYER, row=1)]


def test_the_faults_name_a_missing_recall_belief_and_a_wrong_bar():
    good = {"screen": "choose", "label": JOINED, "index": 1, "prompt": vs_screens.BUYER_PAYER_CHOOSE_PROMPT,
            "options": ["Nobody else", f"{JOINED} · has to agree"], "drawn_index": 1, "served_index": 1,
            "roles": ROLES,
            "recall": "Who decides: x, from your who-decides answer. Who else has to agree: Their partner, The CFO, "
                      "from your last answer.",
            "beliefs": ["a", "b"],
            "test_before": {"bar": "Holds if at least 2 in 3 say the one you pick had to agree the last time they "
                                   "paid for something for this."},
            "test": {"bar": "Holds if at least 2 in 3 say their partner and the CFO had to agree the last time they "
                            "paid for something for this."}}
    assert cs.choose_faults(good, BUYER, row=1) == []
    for change, what in [({"recall": ""}, "the recall line"), ({"beliefs": ["a"]}, "a belief under each option"),
                         ({"test": {"bar": "Holds if at least 2 in 3 say nobody else had to agree the last time they "
                                           "paid for something for this. Decided alone counts as support."}},
                          "the bar after the pick"),
                         # spec 137: *decided alone* said on a role's pick
                         ({"test": {"bar": "Holds if at least 2 in 3 say their partner and the CFO had to agree the "
                                           "last time they paid for something for this. Decided alone counts as "
                                           "support."}}, "the bar says deciding alone counts"),
                         # spec 137: 149's offer pasted in reads as no bar at all
                         ({"test": {"bar": "Holds if at least 2 in 3 say their partner and the CFO had to agree the "
                                           "last time they bought Lullaby."}}, "the bar after the pick"),
                         ({"test_before": {"bar": "Holds if at least 2 in 3 say they had to agree last time."}},
                          "the bar before a pick"),
                         ({"options": ["Nobody else", "The CFO · has to agree"]}, "one option holding every role"),
                         ({"index": 2}, "the pick by index"),
                         ({"served_index": None}, "the served pickedIndex")]:
        assert what in [f["what"] for f in cs.choose_faults({**good, **change}, BUYER, row=1)], change


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
    # spec 139 FR-3 (keel-web 175 FR-3): the bar's form read by the study's B2B flag
    assert 'choose_faults(screen, key, row=screen.get("row"), b2b=vs.is_b2b(j.entry))' in held
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
