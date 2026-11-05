"""Spec 139 FR-3: the walk on keel-web 175 (the screens keep the cards; keel-web master `a73c4f5c`, its tasks.md
*Owed elsewhere -- keel-e2e-eval*). No stack, no model, no paid call; the web's sources are read from the checkout
`stack.toml` names, skipped without it; the Answer screen is walked on a page drawn here (no web server).

- the list Answer's chip is pressed and read by its name *I'm not sure*, `leave-out-line` beside it;
- Buyer and payer's Check is read with `check-nobody-else` first;
- the B2B buyer bar's three forms (roles picked, *Nobody else*, before a pick) where `b2b`, 149 / 173's elsewhere;
- a fact row's Compatibility bar *Holds if no more than 1 in 3 say no.*;
- `chain-shape-FREE` and `chain-free-hint` absent where the user pays;
- a suggested row read from `li.listrow--suggested` with `check-suggestion`;
- Importance's Answer carries `answer-own-row`, read into what the reader gets.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from evals import backtest as bt
from evals import corpus_scenario as cs
from harness import vectors_screens as vs_screens
from harness.steps import Recorder
from stack.config import load_config

KEEL_WEB = Path(load_config(validate=False).keel_web)
BASE = "http://keel.test"
DECIDERS = "contractor operations leads"
BP = "commercial.buyer_payer_alignment"


def _web(rel: str) -> str:
    path = KEEL_WEB / rel
    if not path.is_file():
        pytest.skip(f"no {rel} at {KEEL_WEB}")
    return path.read_text(encoding="utf-8")


# ------------------------------------------------------------------------------------- the words are keel-web's

def test_the_chip_and_its_line_are_keel_webs():
    translate = _web("src/lib/translate.ts")
    assert "export const LEAVE_OUT_CHIP = UNSURE_CHIP;" in translate
    assert f'export const UNSURE_CHIP = "{vs_screens.UNSURE_CHIP}";' in translate
    assert f'export const LEAVE_OUT_LINE = "{vs_screens.LEAVE_OUT_LINE}";' in translate
    assert vs_screens.LEAVE_OUT_CHIP == "I'm not sure" and vs_screens.LEAVE_OUT_CHIP_063 == "Leave this out of the study"
    page = _web("src/components/calibration/ListQuestion.tsx")
    for testid in (vs_screens.LEAVE_OUT_LINE_TESTID, vs_screens.ANSWER_OWN_ROW_TESTID,
                   vs_screens.CHECK_NOBODY_ELSE_TESTID, vs_screens.CHECK_SUGGESTION_TESTID):
        assert f'"{testid}"' in page, testid
    assert vs_screens.LIST_ROW_SUGGESTED in page and "calib__own" in page


def test_the_bars_are_keel_webs():
    translate = _web("src/lib/translate.ts")
    assert "say they could sign off on it themselves${alone ? \"\" : `, or that ${who} would have to agree`}." in \
        translate
    bar = _web("src/lib/compatibilityBar.ts")
    assert 'export const FACT_THREE = ["Yes", "Yes, with some steps", "No"] as const;' in bar
    assert "`Holds if no more than 1 in 3 say ${(labels[2] ?? FACT_THREE[2]).toLowerCase()}.`" in bar
    assert vs_screens.COMPATIBILITY_FACT_BAR == "Holds if no more than 1 in 3 say no."


def test_the_free_pill_and_hint_are_keel_webs():
    control = _web("src/components/calibration/FounderControl.tsx")
    assert f'testId: "{vs_screens.CHAIN_FREE_TESTID}"' in control
    assert f'data-testid="{vs_screens.CHAIN_FREE_HINT_TESTID}"' in control
    assert "locked.unit === null" in control


# ------------------------------------------------------------------------------------ the B2B buyer bar's forms

@pytest.mark.parametrize("text, case, who", [
    (f"Holds if at least 2 in 3 {DECIDERS} say they could sign off on it themselves, or that the CFO and the project "
     "executive would have to agree.", "role", "the CFO and the project executive"),
    (f"Holds if at least 2 in 3 {DECIDERS} say they could sign off on it themselves.", "nobody", "nobody else"),
    (f"Holds if at least 2 in 3 {DECIDERS} say they could sign off on it themselves, or that the one you pick would "
     "have to agree.", "unpicked", "the one you pick"),
])
def test_the_b2b_bar_reads_its_three_forms(text, case, who):
    read = vs_screens.buyer_payer_bar(text)
    assert read == {"case": case, "who": who, "deciders": DECIDERS, "purchase": None, "alone": False, "b2b": True}


def _choose(before: str, after: str, row: int) -> dict:
    return {"label": None, "options": ["Nobody else", "The CFO and the project executive"], "served_index": row,
            "index": row, "prompt": vs_screens.BUYER_PAYER_CHOOSE_PROMPT,
            "roles": ["The CFO", "The project executive"],
            "recall": "Who else has to agree: The CFO, The project executive, from your last answer.",
            "beliefs": ["a", "b"], "test_before": {"bar": before}, "test": {"bar": after}}


B2B_BEFORE = (f"Holds if at least 2 in 3 {DECIDERS} say they could sign off on it themselves, or that the one you pick "
              "would have to agree.")


def test_choose_holds_the_b2b_bar_on_a_b2b_study():
    role = _choose(B2B_BEFORE, f"Holds if at least 2 in 3 {DECIDERS} say they could sign off on it themselves, or that "
                               "the CFO and the project executive would have to agree.", 1)
    assert cs.choose_faults(role, BP, row=1, b2b=True) == []
    nobody = _choose(B2B_BEFORE, f"Holds if at least 2 in 3 {DECIDERS} say they could sign off on it themselves.", 0)
    assert cs.choose_faults(nobody, BP, row=0, b2b=True) == []
    # the user-pays bar on a B2B study is a fault, and the B2B bar where the user pays
    some = vs_screens.BUYER_PAYER_PURCHASE
    old = _choose(f"Holds if at least 2 in 3 say the one you pick had to agree the last time they paid for {some}.",
                  f"Holds if at least 2 in 3 say nobody else had to agree the last time they paid for {some}. "
                  f"{vs_screens.BUYER_PAYER_ALONE_COUNTS}", 0)
    assert [f["what"] for f in cs.choose_faults(old, BP, row=0, b2b=True)] == ["the bar's form",
                                                                              "the bar says deciding alone counts"]
    assert cs.choose_faults(old, BP, row=0, b2b=False) == []
    assert [f["what"] for f in cs.choose_faults(nobody, BP, row=0, b2b=False)] == ["the bar's form",
                                                                                  "the bar says deciding alone counts"]


# ------------------------------------------------------------------------------------------------ said_faults

def test_said_faults_hold_the_chip_line_the_own_row_and_nobody_else():
    answer = {"screen": "answer", "hint": vs_screens.IMPORTANCE_ANSWER_HINT,
              "leave_out_line": vs_screens.LEAVE_OUT_LINE, "own_row": {"text": "Typing up the log", "tag": "yours"}}
    assert cs.said_faults(answer, "problem.importance", b2b=True) == []
    assert [f["what"] for f in cs.said_faults({**answer, "leave_out_line": None}, "problem.importance",
                                              b2b=True)] == ["the chip's line"]
    assert [f["what"] for f in cs.said_faults({**answer, "chip": vs_screens.LEAVE_OUT_CHIP_063}, "problem.importance",
                                              b2b=True)] == ["the chip pressed"]
    check = {"screen": "check", "rows": [{"text": "Nobody else", "tag": "", "locked": True, "nobody_else": True},
                                         {"text": "Construction superintendent · has the problem", "locked": True}]}
    assert cs.said_faults(check, BP, b2b=True) == []
    assert [f["what"] for f in cs.said_faults({"screen": "check", "rows": check["rows"][1:]}, BP, b2b=True)] == \
        ["Nobody else drawn first on Check"]


@pytest.mark.parametrize("bar, faults", [(vs_screens.COMPATIBILITY_FACT_BAR, 0), (vs_screens.COMPATIBILITY_ABILITY_BAR, 0),
                                         (vs_screens.COMPATIBILITY_PERMISSION_BAR, 0),
                                         (vs_screens.COMPATIBILITY_FACT_BAR_128, 1), (None, 0)])
def test_the_compatibility_bar_is_one_of_the_three(bar, faults):
    assert len(vs_screens.compatibility_bar_faults(bar)) == faults


def test_the_free_pill_is_absent_where_the_user_pays():
    absent = {"chain": True, "free_drawn": False, "free_hint_drawn": False}
    drawn = {"chain": True, "free_drawn": True, "free_hint_drawn": True}
    assert vs_screens.free_drawn_faults(absent, False, {"shape": "UPFRONT_THEN"}) == []
    assert len(vs_screens.free_drawn_faults(drawn, False, {"shape": "UPFRONT_THEN"})) == 2
    assert vs_screens.free_drawn_faults(drawn, True, {"shape": "AMOUNT_PERIOD"}) == [], "someone else pays: drawn"
    assert vs_screens.free_drawn_faults(drawn, False, {"shape": "FREE"}) == [], "a saved FREE is drawn"


def test_the_reader_gets_the_new_parts():
    for key in ("leave_out_line", "nobody_else", "suggested", "own_row", "li.listrow--suggested",
                "[data-testid=check-suggestion]", "[data-testid=answer-own-row]", "[data-testid=leave-out-line]",
                "[data-testid=check-nobody-else]"):
        assert key in bt.READ_JS, key


# ---------------------------------------------------------------------------- the walk on a page drawn as 175

#: keel-web 175's list Answer and Check, as far as the walker reads them: the Answer's own row above the box
#: (`answer-own-row`), the chip *I'm not sure* with `leave-out-line` beside it; Buyer and payer's Check with *Nobody
#: else* first, then the role rows, and Adoption friction's suggested row with its why.
_PAGE = """<!doctype html><html><head><meta charset="utf-8"></head><body><div id="app"></div><script>
const pid = location.pathname.split('/')[2];
function render() {
  const app = document.getElementById('app');
  if (/\\/check$/.test(location.pathname)) {
    app.innerHTML = `<main class="corridor"><section class="ccard"><div class="listcheck">
      <h1 class="listcheck__title">Check</h1><ul class="listrows">
      <li class="listrow" data-testid="check-nobody-else"><div class="listrow__line">
        <span class="listrow__ed listrow__ed--lock">Nobody else</span></div></li>
      <li class="listrow"><div class="listrow__line"><span class="listrow__ed listrow__ed--lock">Construction
        superintendent · has the problem</span></div></li>
      <li class="listrow" data-tag="· has to agree"><div class="listrow__line"><textarea class="listrow__ed">The CFO</textarea></div></li>
      <li class="listrow listrow--suggested"><div class="listrow__line"><textarea class="listrow__ed">Check and fix the notes</textarea>
        <span class="listrow__tag">suggested</span></div>
        <p class="listrow__why" data-testid="check-suggestion">Most supers check what goes out.</p></li>
      </ul></div></section></main>`;
    return;
  }
  app.innerHTML = `<main class="corridor"><section class="ccard"><div class="ccard__body">
    <h1 class="calib__q">Which of these is hard?</h1><p class="calib__hint">A hint.</p>
    <ul class="listrows calib__own" data-testid="answer-own-row"><li class="listrow"><div class="listrow__line">
      <span class="listrow__ed listrow__ed--lock">Typing up the log after the walk</span>
      <span class="listrow__tag">yours</span></div></li></ul>
    <label class="calib__answer"><textarea class="calib__answerbox"></textarea></label>
    <span class="calib__unsure"><button type="button" class="calib__chip" aria-describedby="lo">I'm not sure</button>
      <span class="calib__unsure-line" id="lo" data-testid="leave-out-line">Leaves this out of the study</span></span>
    <div class="ccard__foot"><button type="button" class="btn primary">Continue</button></div></div></section></main>`;
  app.querySelector('.calib__chip').addEventListener('click', () => { window.pressed = 'chip'; });
  app.querySelector('.btn.primary').addEventListener('click', async () => {
    await fetch(`/v2/projects/${pid}/calibration/PROBLEM/draft`, {method: 'POST',
      headers: {'content-type': 'application/json'}, body: JSON.stringify({dimension: 'problem.importance',
      unsure: window.pressed === 'chip'})});
    history.pushState({}, '', `/p/${pid}/define/problem/q/3/check`); render();
  });
}
render();
</script></body></html>"""


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _page(browser, path: str):
    page = browser.new_page()

    def serve(route):
        if route.request.method == "POST":
            route.fulfill(status=202, content_type="application/json", body=json.dumps({"interaction_id": "i1"}))
        else:
            route.fulfill(status=200, content_type="text/html", body=_PAGE)
    page.route(f"{BASE}/**", serve)
    page.goto(f"{BASE}{path}", wait_until="load")
    return page


def test_the_walk_presses_i_m_not_sure_and_reads_the_line_and_the_own_row(browser, tmp_path):
    page = _page(browser, "/p/p1/define/problem/q/3/answer")
    try:
        corridor = vs_screens.Corridor(page, Recorder(tmp_path), BASE)
        corridor.camera = lambda slug: None
        seen = corridor.list_answer({"dimension": "problem.importance"}, None)
        assert page.evaluate("window.pressed") == "chip"
    finally:
        page.close()
    assert seen["chip"] == "I'm not sure" and seen["leave_out_line"] == "Leaves this out of the study"
    assert seen["own_row"] == {"text": "Typing up the log after the walk", "tag": "yours"}


def test_the_check_reads_nobody_else_first_and_the_suggested_row(browser, tmp_path):
    page = _page(browser, "/p/p1/define/commercial/q/2/check")
    try:
        corridor = vs_screens.Corridor(page, Recorder(tmp_path), BASE)
        rows = corridor._list_rows()["rows"]
        read = page.evaluate(bt.READ_JS)
    finally:
        page.close()
    assert rows[0]["nobody_else"] is True and rows[0]["text"] == "Nobody else" and rows[0]["locked"]
    assert rows[2]["said"] == "The CFO · has to agree"
    assert rows[3]["suggested"] is True and rows[3]["why"] == "Most supers check what goes out."
    assert read["nobody_else"] is True and read["rows"][0] == "Nobody else"
    assert read["suggested"] == [{"row": "Check and fix the notes", "why": "Most supers check what goes out."}]


def test_the_reader_gets_the_own_row_apart_from_the_rows(browser):
    page = _page(browser, "/p/p1/define/problem/q/3/answer")
    try:
        read = page.evaluate(bt.READ_JS)
    finally:
        page.close()
    assert read["own_row"] == "Typing up the log after the walk yours"
    assert read["rows"] == [] and read["leave_out_line"] == "Leaves this out of the study"
    assert "Typing up the log after the walk" in read["text"]
