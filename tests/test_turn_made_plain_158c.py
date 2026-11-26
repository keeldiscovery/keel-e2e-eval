"""Spec 158c: the walk reads keel-web 249's turn made plain with no stack -- the orb log's rows (the state line, the
chime count, the microphone) and the hand-overs read off them, the chime's one-per-hand-over verdict, `writing ->
speaking` between beats, the card's rows by `data-box`, *What I hear* kept apart from Keel's lines, and one film (the
guide sheets logged, never two at once, no welcome on the conversation's routes). The in-page reads run in a headless
Chromium on a page drawn here as keel-web 249 draws its screens.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import sync_playwright

from evals import three_views_report as report
from harness import story_screens as ss


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _row(state, line=None, chime=0, mic=False, path="/p/x/define/story/1", t=0):
    return {"state": state, "line": line, "chime": chime, "mic": mic, "path": path, "t": t}


# ------------------------------------------------------------------------------------------------ the hand-over

def test_a_hand_over_is_speaking_to_listening_only():
    log = [_row("speaking", ss.TURN_ASKING, 0, t=1), _row("listening", ss.TURN_LISTENING, 1, True, t=2),
           _row("hearing", ss.TURN_LISTENING, 1, True, t=3), _row("writing", "One moment. Writing it down.", 1, t=4),
           # a thinking pause: writing -> listening is no hand-over (keel-web 249's judgement call 5)
           _row("listening", ss.TURN_LISTENING, 1, True, t=5), _row("writing", "One moment.", 1, t=6),
           _row("speaking", ss.TURN_ASKING, 1, t=7), _row("listening", ss.TURN_LISTENING, 2, True, t=8)]
    assert [r["t"] for r in ss.hand_overs(log)] == [2, 8]
    v = ss.chime_verdict(log)
    assert v["hand_overs"] == 2 and v["chimes"] == 2 and v["one_each"] and v["your_turn"] and v["mic_open"]


def test_a_missing_or_double_chime_fails():
    missing = [_row("speaking", chime=0, t=1), _row("listening", ss.TURN_LISTENING, 1, True, t=2),
               _row("speaking", chime=1, t=3), _row("listening", ss.TURN_LISTENING, 1, True, t=4)]
    assert not ss.chime_verdict(missing)["one_each"]
    double = [_row("speaking", chime=0, t=1), _row("listening", ss.TURN_LISTENING, 2, True, t=2)]
    assert not ss.chime_verdict(double)["one_each"]
    # a chime while Keel speaks, never followed by its hand-over
    stray = [_row("speaking", chime=0, t=1), _row("speaking", ss.TURN_ASKING, 1, t=2),
             _row("writing", chime=1, t=5000)]
    v = ss.chime_verdict(stray)
    assert not v["one_each"] and v["stray"]


def test_a_chime_logged_a_moment_before_its_listening_frame_is_that_hand_overs():
    """The chime is counted in the microphone's callback, before React draws the listening orb: another change logged
    in between carries the new count first."""
    log = [_row("speaking", ss.TURN_ASKING, 0, t=1000), _row("speaking", "Keel is asking", 1, t=1010),
           _row("listening", ss.TURN_LISTENING, 1, True, t=1030)]
    v = ss.chime_verdict(log)
    assert v["one_each"] and not v["stray"]


def test_the_state_line_and_the_microphone_at_the_hand_over():
    wrong_line = [_row("speaking", chime=0, t=1), _row("listening", ss.TURN_ASKING, 1, True, t=2)]
    assert not ss.chime_verdict(wrong_line)["your_turn"]
    deaf = [_row("speaking", chime=0, t=1), _row("listening", ss.TURN_LISTENING, 1, False, t=2)]
    assert not ss.chime_verdict(deaf)["mic_open"]
    on_boxes = [_row("speaking", chime=0, path="/p/x/define/story/check", t=1),
                _row("listening", ss.TURN_READBACK, 1, True, path="/p/x/define/story/check", t=2)]
    assert ss.chime_verdict(on_boxes)["your_turn"]


def test_between_beats_the_orb_goes_from_writing_to_speaking():
    assert ss.writing_then_speaking(["speaking", "listening", "hearing", "writing", "speaking", "listening"])
    assert not ss.writing_then_speaking(["speaking", "listening", "hearing", "writing", "listening", "speaking"])
    assert ss.writing_then_speaking(["speaking", "listening", "hearing", "writing"])
    assert ss.holds_in_order(["speaking", "listening", "hearing", "writing", "speaking"], ss.BEAT_ORB_249)
    # spec 172 FR-1 (keel-web 275): the same rule in the four states
    assert ss.thinking_then_asking(["asking", "hearing", "thinking", "asking", "hearing"])
    assert not ss.thinking_then_asking(["asking", "hearing", "thinking", "hearing", "asking"])


# ------------------------------------------------------------------------------------------------ one film

def test_one_film_is_the_opener_alone_never_two_sheets_never_the_welcome_on_the_conversation():
    good = [{"up": ["guide-opener"], "path": "/p/x/define/story/start"}, {"up": [], "path": "/p/x/define/story/start"}]
    v = ss.sheet_verdict(good)
    assert v["one_film"] and v["opener_on"] == ["/p/x/define/story/start"] and not v["welcome_on"]
    two = good + [{"up": ["guide-opener", "guide-welcome"], "path": "/p/x/define/story/start"}]
    v = ss.sheet_verdict(two)
    assert not v["one_film"] and v["most_at_once"] == 2 and v["welcome_on"]
    # the welcome on a stage that is not the conversation's is the shell's own rule
    elsewhere = good + [{"up": ["guide-welcome"], "path": "/p/x/define/persona"}]
    assert ss.sheet_verdict(elsewhere)["one_film"]
    assert not ss.sheet_verdict([{"up": [], "path": "/p/x/define/story/start"}])["one_film"]


# ------------------------------------------------------------------------------------------------ heard vs understood

def test_heard_is_the_founders_and_words_are_keels():
    heard = [{"path": "/p/x/define/story/1", "said": [{"who": "you", "text": "Payroll practitioners"}], "keel": []},
             {"path": "/p/x/define/story/3", "said": [{"who": "you", "text": "The hours  come late."}],
              "keel": [{"who": "keel", "text": "Anything else?"}]}]
    v = ss.heard_verdict(heard, {1: "Payroll practitioners", 3: "The hours come late."}, lambda n: f"/define/story/{n}")
    assert v["all_shown"] and v["words_keels_only"]
    leaked = heard + [{"path": "/p/x/define/story/2", "said": [],
                       "keel": [{"who": "you", "text": "They check the payroll"}]}]
    v = ss.heard_verdict(leaked, {1: "Payroll practitioners", 2: "They check the payroll"},
                         lambda n: f"/define/story/{n}")
    assert not v["all_shown"] and not v["words_keels_only"]
    bare = [{"path": "/p/x/define/story/1", "said": [{"who": "you", "text": "Payroll practitioners", "quoted": False}],
             "keel": []}]
    assert not ss.heard_verdict(bare, {1: "Payroll practitioners"}, lambda n: f"/define/story/{n}")["quoted"]


# ------------------------------------------------------------------------------------------------ the page, drawn

TURN = """
<div class="vstage" data-testid="story-turn" data-turn="3" data-voice="on">
 <p class="vstage__kicker" data-testid="story-kicker">Keel AI · the problem</p>
 <div class="vstage__col">
  <div class="vstage__head">
   <button data-testid="story-orb" data-state="speaking" style="width:44px;height:44px"></button>
   <p class="vstage__state" data-testid="story-state"><span class="vstage__state-line">Keel is asking</span>
    <small class="vstage__state-sub">Your turn comes next. No need to say anything yet.</small></p>
  </div>
  <h1 class="vstage__q" data-testid="story-q">While doing that, what limitations do they run into today?</h1>
  <section class="ucard" data-testid="story-understood"><p class="ucard__label">What Keel understood</p>
   <div class="ucard__rows"><div class="ucard__row" data-box="limits"><span class="ucard__name">In the way</span>
    <div class="ucard__words"><ul class="ucard__list" data-testid="story-limits">
     <li data-id="m0" data-mark="cross" data-testid="story-card-limit">The hours come late</li>
     <li data-id="m1" data-mark="cross" data-testid="story-card-limit">Nobody says when a rate changes</li>
    </ul></div></div></div></section>
  <ol class="vstage__lines" data-testid="story-words"><li data-who="keel">Anything else?</li></ol>
  <div class="vheard" data-testid="story-heard"><p class="vheard__label">What I hear</p>
   <ol class="vheard__words"><li data-who="you">The hours come late, and nobody says when a rate changes</li></ol></div>
 </div>
</div>
<section class="ucard" data-testid="story-boxes" data-lit="cost"><p class="ucard__label">What Keel understood</p>
 <div class="ucard__rows">
  <div class="ucard__row" data-box="person" data-wait=""><span class="ucard__name">The person</span>
   <div class="ucard__words"><div class="ucard__plain"><div><p class="ucard__person" data-id="l1">Payroll practitioners</p></div></div></div></div>
  <div class="ucard__row" data-box="task" data-wait=""><span class="ucard__name">Must get done</span>
   <div class="ucard__words"><div class="ucard__plain"><div><p data-id="l2">Check the payroll</p></div></div></div></div>
  <div class="ucard__row" data-box="cost" data-lit=""><span class="ucard__name">So</span>
   <div class="ucard__words"><div class="ucard__plain"><div><p data-id="l5">A day lost each pay period</p></div></div></div></div>
 </div></section>
"""


def test_the_snapshot_and_the_log_read_249s_turn(browser):
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    page = context.new_page()
    try:
        page.set_content("<!doctype html><html><head><style>.vheard__words li::before{content:'\\201C'}"
                         ".vheard__words li::after{content:'\\201D'}</style></head>"
                         f"<body>{TURN}</body></html>")
        page.evaluate("() => { window.__listening = () => window.__mic === true; }")
        page.evaluate(ss.ORB_WATCH)
        # the hand-over, as keel-web 249 makes it: the chime counted, then the orb listens and the line says so
        page.evaluate("""() => { window.__mic = true; window.__keelChime = 1;
            document.querySelector('[data-testid=story-orb]').setAttribute('data-state', 'listening');
            document.querySelector('.vstage__state-line').textContent = 'Your turn. I am listening.'; }""")
        page.wait_for_timeout(100)
        log = page.evaluate("() => window.__orbLog")
        heard = page.evaluate("() => window.__heardLog")
        snap = page.evaluate(ss._SNAPSHOT)
    finally:
        context.close()
    assert log[0]["state"] == "speaking" and log[0]["line"] == ss.TURN_ASKING and log[0]["chime"] == 0
    assert log[-1]["state"] == "listening" and log[-1]["line"] == ss.TURN_LISTENING and log[-1]["chime"] == 1
    assert log[-1]["mic"] is True and ss.chime_verdict(log)["one_each"]
    assert snap["orbs"] == 1 and snap["orbSize"] == 44 and snap["glow"] == 0 and snap["line"] == ss.TURN_LISTENING
    assert snap["words"] == [{"who": "keel", "text": "Anything else?"}]
    assert snap["heard"] == [{"who": "you", "text": "The hours come late, and nobody says when a rate changes"}]
    assert snap["heardLabel"] == "What I hear"
    assert snap["limits"] == ["The hours come late", "Nobody says when a rate changes"]
    assert snap["understood"]["label"] == ss.CARD_LABEL
    assert [m["mark"] for m in ss.card_items(snap["understood"], "limits")] == ["cross", "cross"]
    rows = ss.card_rows(snap["card"])
    assert list(rows) == ["person", "task", "cost"] and rows["cost"] == "A day lost each pay period"
    assert ss.card_name(snap["card"], "cost") == ss.CARD_COST_NAME and snap["card"]["lit"] == "cost"
    assert snap["card"]["svg"] == 0 and snap["chime"] == 1 and snap["buttons"] == []
    assert heard and heard[0]["keel"] == [{"who": "keel", "text": "Anything else?"}]
    assert heard[-1]["said"][0]["quoted"] is True
    assert ss.heard_verdict(heard, {3: "The hours come late, and nobody says when a rate changes"},
                            lambda n: f"/{n}")["quoted"]


def test_the_sheet_log_counts_the_sheets_standing(browser):
    context = browser.new_context()
    page = context.new_page()
    try:
        page.set_content("<!doctype html><html><body><div id=r></div></body></html>")
        page.evaluate(ss.ORB_WATCH)
        page.evaluate("() => { document.getElementById('r').innerHTML = '<div data-testid=guide-opener></div>'; }")
        page.wait_for_timeout(50)
        page.evaluate("() => { document.getElementById('r').innerHTML = ''; }")
        page.wait_for_timeout(50)
        sheets = page.evaluate("() => window.__sheetLog")
    finally:
        context.close()
    assert [r["up"] for r in sheets] == [[], ["guide-opener"], []]


def test_the_report_names_the_turn():
    turns = [{"label": "the script's words", "chime": ss.chime_verdict(
        [_row("speaking", chime=0, t=1), _row("listening", ss.TURN_LISTENING, 1, True, t=2)]),
        "sheets": ss.sheet_verdict([{"up": ["guide-opener"], "path": "/p/x/define/story/start"}]),
        "guide": {"welcomeSeen": True, "openersSeen": ["PROBLEM"]}},
        {"label": "a miss", "chime": ss.chime_verdict([_row("speaking", chime=0, t=1),
                                                       _row("listening", ss.TURN_LISTENING, 3, True, t=2)]),
         "sheets": {}}]
    md = "\n".join(report.turn_markdown(turns))
    assert "## The turn (spec 158c, keel-web 249)" in md
    assert "| the script's words | 1 | 1 | yes | yes (Your turn. I am listening.) | yes | 1 | 0 | 1 | welcome yes, openers PROBLEM |" in md
    assert "### a miss" in md and "wanted [1]" in md
    assert "The turn" in report.report_markdown([], {}, {"measured": False}, None, None, turns)
