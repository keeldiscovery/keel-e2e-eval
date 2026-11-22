"""Spec 158b: the drawn story's fit with no stack -- the in-page read (`story_screens._MEASURE_STORY`) on a page drawn here
(a text over a drawn element found, a clear one not, `[data-draw]` preferred to the SVG's groups, a caption plate not a
drawing, the spoken line's rows, the band between the header and the tab bar, the page scrolling), the loop that reads
until the player ends, the verdicts and the report's *The drawn story*; and the walk's two builds of keel-web 245 FR-4
(a readback and the quiet on the beat's screen, or straight on to the next question), and the orb read off the glow.
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


def _page(browser, body: str, *, viewport=None):
    context = browser.new_context(viewport=viewport or {"width": 1280, "height": 800})
    page = context.new_page()
    page.set_content(f"<!doctype html><html><head><style>body{{margin:0;font:16px/24px sans-serif}}"
                     f".lb{{position:absolute}}</style></head><body>{body}</body></html>")
    return context, page


#: A player: a 360 x 240 frame, a room and two pictograms drawn, a label over `p1`, one clear, and the spoken line.
PLAYER = """
<div class="pbar" style="height:56px;background:#eee"></div>
<div id="col" style="padding:8px">
 <div class="sty-player" data-testid="story-player" data-state="{state}">
  <div class="sty-board" data-testid="story-board" style="position:relative;width:360px;height:240px">
   <svg width="360" height="240" style="position:absolute;left:0;top:0">
    <g class="room" {room}><rect x="0" y="180" width="360" height="60"/></g>
    <g data-id="p1" {p1}><rect x="20" y="20" width="60" height="60"/></g>
    <g data-id="p2" {p2}><rect x="280" y="20" width="60" height="60"/></g>
    {caption}
   </svg>
   <div class="lb" data-id="over" style="left:30px;top:40px"><span>Rates change</span></div>
   <div class="lb" data-id="clear" style="left:120px;top:100px"><span>Clear</span></div>
  </div>
  <p data-testid="story-line" style="width:{line_w}px">{line}</p>
 </div>
</div>
<div class="ptabs" style="position:fixed;bottom:0;left:0;right:0;height:56px;background:#ddd"></div>
"""


def _player(state="playing", line="They check the payroll by hand.", line_w=340, tagged=False, caption=""):
    tag = (lambda kind: f'data-draw="{kind}"') if tagged else (lambda kind: "")
    return PLAYER.format(state=state, line=line, line_w=line_w, room=tag("room"), p1=tag("pictogram"),
                         p2=tag("pictogram"), caption=caption)


def _read(page, root="[data-testid=story-player]", state=None):
    return page.evaluate(ss._MEASURE_STORY, {"root": root, "state": state, "notDrawn": list(ss.DRAW_KINDS_NOT_DRAWN)})


def test_a_text_over_a_drawn_element_is_found_and_a_clear_one_is_not(browser):
    context, page = _page(browser, _player())
    try:
        read = _read(page)
    finally:
        context.close()
    assert read["drawn_by"] == "top-level g"
    pairs = {(o["text_id"], o["drawn"]) for o in read["overlaps"]}
    assert ("over", "p1") in pairs
    assert not [o for o in read["overlaps"] if o["text_id"] == "clear"]
    assert read["frame"]["w"] == 360 and read["frame"]["h"] == 240
    assert {p["id"] for p in read["pictograms"]} == {"p1", "p2"}
    assert read["line"]["rows"] == 1 and read["fit"]["frame"] and not read["fit"]["page_scrolls"]


def test_data_draw_groups_are_preferred_and_a_caption_plate_is_not_a_drawing(browser):
    caption = '<g data-draw="caption" data-id="plate"><rect x="25" y="35" width="120" height="30"/></g>'
    context, page = _page(browser, _player(tagged=True, caption=caption))
    try:
        read = _read(page)
    finally:
        context.close()
    assert read["drawn_by"] == "data-draw"
    assert "plate" not in {o["drawn"] for o in read["overlaps"]}
    assert ("over", "p1") in {(o["text_id"], o["drawn"]) for o in read["overlaps"]}


def test_a_hidden_drawing_is_not_met(browser):
    context, page = _page(browser, _player().replace('<g data-id="p1" ', '<g data-id="p1" style="opacity:0" '))
    try:
        read = _read(page)
    finally:
        context.close()
    assert not [o for o in read["overlaps"] if o["drawn"] == "p1"]


def test_the_spoken_line_rows_are_counted(browser):
    long = "They check the payroll by hand every week, line by line, before it goes out, and still find the mistakes " \
           "after the money has gone to the wrong people in the wrong amounts."
    context, page = _page(browser, _player(line=long, line_w=120))
    try:
        read = _read(page)
    finally:
        context.close()
    assert read["line"]["rows"] > ss.LINE_ROWS_MAX
    assert read["line"]["font"] == "16px"


def test_on_a_phone_a_frame_past_the_tab_bar_does_not_fit(browser):
    tall = _player().replace("height:240px", "height:900px").replace('height="240"', 'height="900"')
    context, page = _page(browser, tall, viewport=ss.PHONE)
    try:
        read = _read(page)
    finally:
        context.close()
    assert read["viewport"] == {"w": 390, "h": 844}
    assert read["band"] == {"top": 56, "bottom": 844 - 56}
    assert read["fit"]["frame"] is False and read["fit"]["page_scrolls"] is True


def test_measure_story_reads_until_the_player_ends(browser):
    context, page = _page(browser, _player(state="idle"))
    try:
        page.evaluate("""() => {
          const p = document.querySelector('[data-testid=story-player]');
          setTimeout(() => p.setAttribute('data-state', 'playing'), 300);
          setTimeout(() => { document.querySelector('[data-testid=story-line]').textContent = 'A second line.'; }, 700);
          setTimeout(() => p.setAttribute('data-state', 'ended'), 1200);
        }""")
        out = ss.measure_story(page, "[data-testid=story-player]", timeout_s=10)
    finally:
        context.close()
    assert out["played"] is True and out["samples"] >= 3
    assert set(out["lines"]) == {"They check the payroll by hand.", "A second line."}
    assert ("Rates change", "p1") in {(o["text"], o["drawn"]) for o in out["overlaps"]}
    assert len(out["overlaps"]) == len({(o["text"], o["drawn"]) for o in out["overlaps"]})   # one row a pair


def _measured(**over):
    base = {"samples": 8, "played": True, "overlaps": [], "unfit": [],
            "lines": {"They check it by hand.": {"rows": 2, "font": "16px", "line_height": "24px"}},
            "numbers": {"drawn": 5, "drawn_by": "data-draw", "frame": {"w": 358, "h": 238}, "person_ratio": 0.42,
                        "pictograms": [{"id": "p1", "w": 48, "h": 48}], "viewport": {"w": 390, "h": 844},
                        "band": {"top": 56, "bottom": 788}}}
    base.update(over)
    return base


def test_the_verdicts():
    clean = ss.fit_verdicts(_measured(), phone=True)
    assert {k: v[0] for k, v in clean.items()} == {"drawn": True, "rows": True, "fits": True}
    assert "fits" not in ss.fit_verdicts(_measured(), phone=False)
    over = ss.fit_verdicts(_measured(overlaps=[{"text": "Rates change", "drawn": "p1", "kind": "pictogram"}]),
                           phone=False)
    assert over["drawn"][0] is False and over["drawn"][1]["overlaps"][0]["drawn"] == "p1"
    four = ss.fit_verdicts(_measured(lines={"x": {"rows": 4}}), phone=False)
    assert four["rows"][0] is False and four["rows"][1]["over"] == {"x": 4}
    unfit = ss.fit_verdicts(_measured(unfit=[{"what": ["the page scrolls"]}]), phone=True)
    assert unfit["fits"][0] is False
    never = ss.fit_verdicts({"samples": 0}, phone=True)
    assert not any(v[0] for v in never.values())


def test_the_report_names_the_drawn_story():
    fits = [{"label": "the long telling", "where": "define/story/check (story)", "view": "founder · desktop",
             "phone": False, "measured": _measured(), "verdicts": {"drawn": True, "rows": True}},
            {"label": "the problem link's story card", "where": "the story card", "view": "text · phone", "phone": True,
             "measured": _measured(overlaps=[{"text": "Rates change", "drawn": "p1", "kind": "pictogram",
                                              "text_box": {"x": 1}, "drawn_box": {"x": 2}}],
                                   unfit=[{"what": ["the page scrolls"], "band": {}, "frame": {}, "line": {}, "doc": {}}]),
             "verdicts": {"drawn": False, "rows": True, "fits": False}}]
    text = "\n".join(report.drawn_story_markdown(fits))
    assert "## The drawn story (spec 158b)" in text
    assert "| the long telling | define/story/check (story) | founder · desktop | yes | - | yes | 358x238 | 0.42 |" in text
    assert "text on the drawing: *Rates change* over `p1`" in text
    assert "does not fit: the page scrolls" in text
    assert report.drawn_story_markdown(None) == []
    assert "The drawn story" in report.report_markdown([], {}, {"measured": False}, None, fits)


# ------------------------------------------------------------------------------------------------ keel-web 245 FR-4

class _Loc:
    def __init__(self, page):
        self.page = page
        self.first = self

    def wait_for(self, **_):
        return None


class _FakePage:
    """The page `StoryWalk.after_answer` reads: its url moving on a timeline (ticks of `wait_for_timeout`), the orb log
    and the recorder's state answered from scripts."""

    def __init__(self, urls, log, listening=True):
        self.urls, self.log, self._listening, self.tick, self.waited = urls, log, listening, 0, []

    @property
    def url(self):
        return self.urls[min(self.tick, len(self.urls) - 1)]

    def wait_for_timeout(self, _ms):
        self.tick += 1

    def evaluate(self, script, *_):
        if "__orbLog" in script:
            return self.log[: self.tick + 1]
        if "__listening" in script:
            return self._listening
        return None

    def wait_for_function(self, script, arg=None, timeout=None):
        self.waited.append(arg)

    def get_by_test_id(self, _testid):
        return _Loc(self)

    def locator(self, selector):
        self.waited.append(selector)
        return _Loc(self)


def _walk(page):
    walk = object.__new__(ss.StoryWalk)
    walk.page, walk.patience, walk.voice = page, 1.0, ss.FounderVoice(page)
    return walk


B1 = "/p/x/define/story/1"


def test_straight_on_waits_for_the_next_question_not_a_readback():
    log = [{"state": "listening", "path": B1}, {"state": "hearing", "path": B1}, {"state": "writing", "path": B1},
           {"state": "speaking", "path": "/p/x/define/story/2"}]
    page = _FakePage([B1, B1, "/p/x/define/story/2"], log)
    out = _walk(page).after_answer(1, 0, timeout_s=5)
    assert out["straight_on"] is True and out["next"] == "2"
    assert page.waited == [ss.STORY_QUESTIONS[2]]


def test_the_readback_and_its_quiet_on_the_beats_screen_today():
    log = [{"state": "listening", "path": B1}, {"state": "hearing", "path": B1}, {"state": "writing", "path": B1},
           {"state": "speaking", "path": B1}, {"state": "listening", "path": B1}]
    page = _FakePage([B1] * 10, log)
    out = _walk(page).after_answer(1, 0, timeout_s=5)
    assert out == {"straight_on": False, "spoke": True, "orb": ["listening", "hearing", "writing", "speaking", "listening"]}


def test_a_next_question_spoken_elsewhere_is_not_the_beats_readback():
    """The orb's speaking on beat 2's screen must not read as beat 1's readback (the path keeps them apart)."""
    log = [{"state": "hearing", "path": B1}, {"state": "writing", "path": B1},
           {"state": "speaking", "path": "/p/x/define/story/2"}, {"state": "listening", "path": "/p/x/define/story/2"}]
    page = _FakePage([B1] * 6 + ["/p/x/define/story/2"], log)
    out = _walk(page).after_answer(1, 0, timeout_s=5)
    assert out["straight_on"] is True


# ------------------------------------------------------------------------------------------------ the glow

def test_the_orb_is_read_off_the_glow_where_no_orb_is_drawn(browser):
    context, page = _page(browser, '<div class="vstage"><div data-testid="story-glow" data-state="speaking"></div>'
                                   '<button data-testid="story-glow">x</button></div>')
    try:
        page.evaluate(ss.ORB_WATCH)
        page.evaluate("() => document.querySelector('div[data-testid=story-glow]').setAttribute('data-state', 'listening')")
        page.wait_for_timeout(100)
        log = page.evaluate("() => window.__orbLog")
        snap = page.evaluate(ss._SNAPSHOT)
    finally:
        context.close()
    assert [row["state"] for row in log] == ["speaking", "listening"]
    assert snap["orb"] == "listening" and snap["buttons"] == []
    assert "story-glow" in ss.ORB and ss.ORB_TAP == "[data-testid=story-orb]"


def test_said_turns_takes_the_scripts_first_story():
    """keel-cloud 263c (`1fb1fa71`) adds tellings after the first story (another who, beat 2 said several ways)."""
    script = {"turns": [{"turn": n, "heard": str(n)} for n in (1, 2, 3, 4, 5)]
              + [{"turn": 1, "heard": "Angel investors"}] + [{"turn": 2, "heard": f"way {i}"} for i in range(4)]}
    assert ss.said_turns(script) == [(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")]


def test_an_idea_beat_straight_on_waits_for_the_next_idea_beat():
    """keel-web 248: the idea's beat 1 goes straight on (its spelling check agreeing) -- the walk waits for beat 2's
    screen, never a readback."""
    i1 = "/p/x/define/idea/1"
    log = [{"state": "hearing", "path": i1}, {"state": "writing", "path": i1}]
    page = _FakePage([i1, "/p/x/define/idea/2"], log)
    out = _walk(page).after_answer(1, 0, timeout_s=5, flow="idea")
    assert out["straight_on"] is True and out["next"] == "2" and out["asked"] is None
    assert page.waited == [f"{ss.IDEA_TURN}[data-turn='2']"]


def test_a_stroke_not_yet_inked_and_a_wiped_board_are_not_met(browser):
    """keel-web draws a stroke by `.on` (dash offset 1 -> 0) and wipes the board between scenes (`.sty-wipe.on`): a label
    standing where a figure is not yet drawn, or over a wiped board, is not on the drawing."""
    inked = _player(tagged=True).replace(
        '<g data-id="p1" data-draw="pictogram"><rect x="20" y="20" width="60" height="60"/></g>',
        '<g data-id="p1" data-draw="pictogram"><path class="ink" d="M20 20 L80 80"/></g>')
    context, page = _page(browser, inked)
    try:
        before = _read(page)
        page.evaluate("() => document.querySelector('[data-id=p1] .ink').classList.add('on')")
        drawn = _read(page)
        page.evaluate("""() => { const b = document.querySelector('[data-testid=story-board]');
          const w = document.createElement('div'); w.className = 'sty-wipe on';
          w.style.cssText = 'position:absolute;left:0;top:0;width:100%;height:100%'; b.appendChild(w); }""")
        wiped = _read(page)
    finally:
        context.close()
    assert "p1" not in {o["drawn"] for o in before["overlaps"]}
    assert ("over", "p1") in {(o["text_id"], o["drawn"]) for o in drawn["overlaps"]}
    assert not wiped["overlaps"]


def test_a_footer_under_the_story_is_not_the_story_failing_to_fit(browser):
    """The site's footer below the screen's <main> makes the page scroll; the story fits all the same. Content of the
    screen itself below the fold does not."""
    body = "<main>" + _player() + "</main><footer style='height:120px;margin-top:400px'>Keel · Privacy</footer>"
    context, page = _page(browser, body, viewport=ss.PHONE)
    try:
        footer = _read(page)
        page.evaluate("() => { const d = document.createElement('div'); d.style.height = '600px'; "
                      "document.querySelector('main').appendChild(d); }")
        tall = _read(page)
    finally:
        context.close()
    assert footer["fit"]["page_scrolls"] is True and footer["fit"]["content_below"] is None
    assert footer["fit"]["frame"] and footer["fit"]["line"]
    assert tall["fit"]["content_below"] and tall["fit"]["content_below"] > 844
