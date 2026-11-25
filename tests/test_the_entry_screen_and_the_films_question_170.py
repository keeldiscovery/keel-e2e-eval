"""Spec 170: the harness mirrors keel-web 266 (the entry screen), 268 (the verdict step retired), 269 (the film's one
question) and 270 (the building screen: the frames are the progress).

FR-1 the entry screen walked by its ids -- *Test your mic* -> *Say anything.* -> *Your mic works.* -> **Begin** -- the
hello's words never read, 256's words on a screen a DRIFT capture note (`entry_drift`, `film_strangers.entry_faults`).
FR-2 no wait on `story-verdict`; after the film's yes the window page (a retired card met on the way passed by the quiet
and reported). FR-2b the vendored Prevalence card. FR-2c the building screen's legend and looks (the mirrors of 263
carry the page tests). FR-3 the film's question read, *yes* said aloud, `film-fix` never opened. FR-5 nothing here writes
respondent words.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from evals import three_views_strangers as tvs
from harness import film_strangers as fs
from harness import interviewer_screens as ivs
from harness import story_screens as ss
from harness.steps import Recorder
from quality import cards
from quality import film_reader as fread

BASE = "http://story.test"


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _page(browser, body: str):
    page = browser.new_page()
    page.route(f"{BASE}/**", lambda r: r.fulfill(status=200, content_type="text/html; charset=utf-8",
                                                 body=f"<!doctype html><html><body>{body}</body></html>"))
    page.goto(f"{BASE}/p/p1/define/story/check")
    return page


# ------------------------------------------------------------------------------------------ FR-3 the film's question

#: keel-web 269's film page at its end: the question on `story-check-said`, Yes / No under the frame; the founder's
#: spoken words go to `__say`, and a yes goes on to the window page (keel-web 268: no verdict card).
FILM_269 = """<div data-testid="film-ask"></div><script>
window.__said = [];
window.__listening = () => !!document.querySelector('[data-testid=film-yes]');
window.__say = (w) => { window.__said.push(w);
  if (/^yes/i.test(w)) history.pushState({}, '', '/p/p1/define/context/window'); };
setTimeout(() => { document.querySelector('[data-testid=film-ask]').innerHTML =
  '<p data-testid="story-check-said">Does this film show the problem accurately?</p>'
  + '<button data-testid="film-yes">Yes</button><button data-testid="film-no">No</button>'; }, 300);
</script>"""

#: keel-web 257's end: no Yes / No, a quiet wait, then the verdict card, a second quiet wait, then the window page.
FILM_257 = """<p data-testid="story-check-said">Is that how it goes for them?</p><div id="v"></div><script>
let quiet = 0;
window.__keelSilence = () => { quiet += 1;
  if (quiet === 1) { document.querySelector('#v').innerHTML = '<div data-testid="story-verdict">I will call this real'
    + '</div>'; return true; }
  history.pushState({}, '', '/p/p1/define/context/window'); return true; };
</script>"""


def test_the_films_question_is_read_and_answered_yes_aloud(browser, tmp_path):
    page = _page(browser, FILM_269)
    try:
        walk = ss.StoryWalk(page, Recorder(tmp_path), BASE, patience=0.1)
        yes = walk.story_yes()
        said = page.evaluate("() => window.__said")
    finally:
        page.close()
    assert yes["said"] == ss.STORY_ASK == "Does this film show the problem accurately?"
    assert yes["film"] == {"asked": ss.STORY_ASK, "buttons": True, "answered": ss.FILM_YES, "fix_opened": False,
                           "went_on": False}
    assert said == [ss.FILM_YES] and yes["verdict_seen"] is False and yes["landed"].endswith("/define/context/window")


def test_a_screen_before_268_is_passed_by_the_quiet_and_named(browser, tmp_path):
    """FR-2: the walk never waits on `story-verdict`; a keel-web still drawing it is passed as before (the quiet) and
    reported -- a DRIFT capture note in the founder's check, never what stops the walk."""
    page = _page(browser, FILM_257)
    try:
        walk = ss.StoryWalk(page, Recorder(tmp_path), BASE, patience=0.02)
        yes = walk.story_yes()
    finally:
        page.close()
    assert yes["film"]["buttons"] is False and yes["film"]["answered"] == "the quiet"
    assert yes["film"]["asked"] == ss.STORY_ASK_BEFORE_269
    assert yes["verdict_seen"] is True and yes["landed"].endswith("/define/context/window")


def test_the_solution_films_question_names_the_brand(browser, tmp_path):
    body = FILM_269.replace("story-check-said", "idea-story-said").replace(
        "Does this film show the problem accurately?", ss.film_ask_idea(ss.IDEA_NAME))
    page = _page(browser, body)
    try:
        film = ss.IdeaWalk(page, Recorder(tmp_path), BASE, patience=0.1).film_question("idea-story-said")
    finally:
        page.close()
    assert film["asked"] == f"Does this film show {ss.IDEA_NAME} accurately?" and film["answered"] == ss.FILM_YES
    assert film["buttons"] is True and film["fix_opened"] is False


def test_the_verdict_pins_are_gone():
    for name in ("VERDICT_CARD", "VERDICT_ASK", "VERDICT_LATER"):
        assert not hasattr(ss, name), name
    assert not hasattr(ss.StoryWalk, "hear_verdict") and not hasattr(ss.IdeaWalk, "film_yes_verdict_pilot")
    assert hasattr(ss.IdeaWalk, "film_yes_pilot")
    # the wire still serves `verdictLine`; the screens no longer read it
    assert ss.VERDICT_LINE.startswith("I will call this real if")
    source = Path(ss.__file__).read_text(encoding="utf-8")
    assert "film-fix" in source and ".click()" not in source.split("def film_question", 1)[1].split("def ", 1)[0]


def test_the_founders_transcript_ends_on_the_films_question():
    """FR-3: the film judge's founder lines end on the question keel-web 269 asks; a record made before it keeps the
    verdict line it was said."""
    beats = [{"turn": 1, "asked": "Who has this problem?", "founder": "Clerks."}]
    lines = fread.founder_lines({"beats": beats, "verdict_line": ss.VERDICT_LINE, "film_ask": ss.STORY_ASK})
    assert lines[-1] == {"beat": "the film's question",
                         "said": "After the film, Keel asks: Does this film show the problem accurately?"}
    old = fread.founder_lines({"beats": beats, "verdict_line": ss.VERDICT_LINE})
    assert old[-1]["beat"] == "the verdict line"
    solution = fread.founder_lines({"beats": beats, "film_ask": ss.film_ask_idea("Runcheck"), "pilot_ask": "Pilot?"})
    assert [x["beat"] for x in solution] == ["beat 1", "the film's question", "the pilot ask"]


# ---------------------------------------------------------------------------------------------- FR-1 the entry screen

class _Leg:
    def __init__(self):
        self.checks: list[tuple[str, bool, dict]] = []

    def check(self, run, what, ok, **kw):
        self.checks.append((what, bool(ok), kw))


def _walked(*, old: bool = False) -> dict:
    line = ivs.ai_intro_line(ivs.ORB_NAME, None, 3)
    answers = {"drawn": True, "open": False, "summary": ivs.CONSENT_HEADING,
               "lines": [ivs.AI_INTRO_MIC_LINE, ivs.INTRO_TRANSCRIBED, "Your words may be quoted."]}
    intro = {"speaker": "ORB", "orb": 1, "heading": "Robin has 3 questions for you.", "line": line, "answers": answers,
             "buttons": ["ai-mic-test"], "fallback": 0, "retired": [], "text": f"Robin has 3 questions for you. {line}"}
    after = {"buttons": ["ai-start"], "mic_heard": ivs.MIC_WORKS, "start_words": ivs.BEGIN, "retired": [],
             "text": f"{ivs.MIC_WORKS} {ivs.BEGIN}"}
    if old:
        intro = {**intro, "retired": ["ai-intro-chips"]}
        after = {**after, "mic_heard": "Heard: hello", "start_words": "Start the interview",
                 "text": "Heard: hello Start the interview"}
    return {"intro": intro, "mic": {"after": after}}


INTERVIEW = {"kind": "FULL", "gate": {"question": "In the last month, have you encountered this issue?"},
             "parts": [{"items": [{"itemId": "i1"}, {"itemId": "i2"}]}], "founderName": "Robin", "consentText": "Your words may be quoted."}


def test_the_intro_checks_hold_266s_entry_screen():
    leg = _Leg()
    tvs.intro_checks(None, leg, _walked(), INTERVIEW, view="orb", label="the orb", speaker=ivs.SPEAKER_ORB)
    assert [ok for _, ok, _ in leg.checks] == [True, True, True, True], leg.checks
    leg = _Leg()
    tvs.intro_checks(None, leg, _walked(old=True), INTERVIEW, view="orb", label="the orb", speaker=ivs.SPEAKER_ORB)
    button, drift = leg.checks[2], leg.checks[3]
    assert button[1] is False and drift[1] is False and drift[2]["stop"] is False
    assert drift[2]["detail"]["drift"].startswith("(capture) keel-web 266")
    assert drift[2]["detail"]["found"] == ["ai-intro-chips", "Heard: ", "Start the interview"]


def test_the_strangers_entry_is_kept_and_its_drift_is_a_capture_note():
    assert fs.entry_shape(_walked()) == {"before": ["ai-mic-test"], "after": ["ai-start"], "heard": ivs.MIC_WORKS,
                                         "begin": ivs.BEGIN, "drift": []}
    walks = [{"person": "p1", "entry": fs.entry_shape(_walked())},
             {"person": "p2", "entry": fs.entry_shape(_walked(old=True))}]
    assert fs.entry_faults(walks[:1]) == []
    faults = fs.entry_faults(walks)
    assert len(faults) == 1 and "keel-web 266 FR-1 / FR-2" in faults[0]["owed"] and faults[0]["frame"] is None
    assert faults[0]["detail"] == "1 of 2 walks: p2" and "Start the interview" in faults[0]["what"]
    assert fs.entry_shape(None)["drift"] == [] and fs.entry_faults(None) == []
    run_film = (Path(fs.__file__).resolve().parents[1] / "evals" / "run_film.py").read_text(encoding="utf-8")
    assert run_film.count("fs.entry_faults((strangers or {}).get(\"walks\"))") == 2


# ---------------------------------------------------------------------------------------------- FR-2b the cards

def test_prevalences_card_is_keel_cloud_277s():
    body = cards.card("problem.prevalence")
    flat = " ".join(body.split())
    assert "the gate is the fixed words *In {window}, have you encountered this issue?* (keel-cloud 277)" in flat
    assert "*Did this happen to you?*" not in flat and "never refused, and may be dropped (keel-cloud 277)" in flat
    assert "problem.prevalence" not in cards.CARDS_MOVED_162


# ---------------------------------------------------------------------------------------------- FR-5

def test_nothing_here_writes_respondent_words():
    for module in (ivs, ss, fs, tvs, fread):
        text = Path(module.__file__).read_text(encoding="utf-8")
        assert "respondent-questions" not in text, module.__name__
