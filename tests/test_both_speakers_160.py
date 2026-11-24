"""Spec 160: both interviewers, the same walk -- the harness's machinery with no stack (the walk folded into steps and
two walks compared, the collector's new fields and the film's read off drawn pages in a headless Chromium, the intro's
one button and its block, the refused seam allowed again, the report's *The two speakers*) and the mirror of the subject:
keel-web 256 (the player pared down), read from the sibling checkout the stack runs."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from evals import three_views_report as report
from evals import three_views_strangers as strangers
from harness import interviewer_screens as ivs
from harness import story_screens as ss
from harness.steps import Recorder
from stack.config import load_config

WEB = Path(load_config(validate=False).keel_web)


def _web(rel: str) -> str:
    path = WEB / rel
    if not path.exists():
        pytest.skip(f"{path} is not in the sibling checkout")
    text = path.read_text(encoding="utf-8")
    if rel.endswith("AiInterviewPlayer.tsx") and 'data-testid="ai-film-begin"' not in text:
        pytest.skip("keel-web before 256 (the player pared down)")
    return text


def _row(**kw) -> dict:
    base = {"onStage": False, "film": None, "begin": False, "phase": None, "where": None, "size": None, "ids": [],
            "words": None, "lit": 0, "litFirst": None, "intro": None}
    return {**base, **kw}


def _walk(size_at_listening: str = "small", words: str = "Did it happen?") -> list[dict]:
    return [
        _row(intro="ORB", ids=["ai-intro", "ai-mic-test"]),
        _row(intro="ORB", ids=["ai-intro", "ai-mic-test"]),
        _row(intro="ORB", ids=["ai-intro", "ai-start"]),
        _row(onStage=True, phase="loading", ids=["ai-where"]),                       # transient: no step
        _row(onStage=True, phase="story", film="problem", ids=["ai-film-pause", "ai-film-again", "ai-film-board"]),
        _row(onStage=True, phase="story", film="problem", ids=["ai-film-board", "story-read"]),
        _row(onStage=True, phase="story", film="problem", begin=True, ids=["ai-film-begin", "ai-film-board"]),
        _row(onStage=True, phase="story", ids=[]),                                    # the frame after the film
        _row(onStage=True, phase="speaking", where="Opening", size="large", ids=["speaker", "ship-mark"]),
        _row(onStage=True, phase="speaking", where="Question 1 of 7", size="large", ids=["speaker", "ai-words"],
             words=words, lit=1, litFirst=True),
        _row(onStage=True, phase="speaking", where="Question 1 of 7", size="large", ids=["speaker", "ai-words"],
             words=words, lit=3, litFirst=True),
        _row(onStage=True, phase="listening", where="Question 1 of 7", size=size_at_listening,
             ids=["speaker", "ai-sheet", "ai-replay"]),
        _row(onStage=True, phase="sending", where="Question 1 of 7", size="small", ids=["speaker"]),   # transient
        _row(ids=["ai-done", "ai-done-tick", "ai-mic-off"]),
    ]


# ------------------------------------------------------------------------------------------- the steps

def test_the_walk_folds_into_its_steps():
    steps = ss.walk_steps(_walk())
    assert [s["step"] for s in steps] == ["intro", "intro+start", "film:problem", "film:problem+begin",
                                          "speaking:Opening", "speaking:Question 1 of 7", "listening:Question 1 of 7",
                                          "done"]
    film = steps[2]
    assert film["ids"] == ["ai-film-again", "ai-film-board", "ai-film-pause", "story-read"] and film["sizes"] == []
    asked = steps[5]
    assert asked["sizes"] == ["large"] and asked["words"] == "Did it happen?" and asked["lit_first"]
    assert asked["lit_max"] == 3
    assert steps[6]["sizes"] == ["small"] and "ai-replay" in steps[6]["ids"]
    assert ss.sizes_line(steps) == "- - - - L L S -"


def test_a_block_is_a_step_of_its_own():
    assert ss.step_of(_row(intro="AVATAR", ids=["ai-intro", "ai-mic-test", "ai-mic-block"])) == "intro+block"
    assert ss.step_of(_row(ids=["ai-ended"])) == "ended"
    assert ss.step_of(_row(onStage=True, phase="beat", where="Opening")) == "beat:Opening"


def test_the_same_walk_on_both_speakers_is_the_same():
    orb, face = ss.walk_steps(_walk()), ss.walk_steps(_walk())
    face[5]["lit_max"] = 1                       # the words' count at the clip's end is a timer's race: not compared
    assert ss.same_walk(orb, face) == {"same": True, "at": None, "steps": 8}


def test_where_the_speakers_part_is_named_by_step():
    parted = ss.same_walk(ss.walk_steps(_walk()), ss.walk_steps(_walk(size_at_listening="large")))
    assert parted["same"] is False and parted["at"] == 6 and parted["differs"] == ["sizes"]
    assert parted["orb"]["step"] == parted["face"]["step"] == "listening:Question 1 of 7"
    words = ss.same_walk(ss.walk_steps(_walk()), ss.walk_steps(_walk(words="Did that happen?")))
    assert words["at"] == 5 and words["differs"] == ["words"]
    short = ss.same_walk(ss.walk_steps(_walk()), ss.walk_steps(_walk())[:-1])
    assert short["at"] == 7 and short["differs"] == ["missing on the face"]


def test_the_report_names_the_two_speakers():
    orb, face = ss.walk_steps(_walk()), ss.walk_steps(_walk(size_at_listening="large"))
    rows = report.speaker_rows({"problem": {"ORB": orb, "AVATAR": face}},
                               {"problem": ss.same_walk(orb, face)})
    assert [(r["study"], r["speaker"]) for r in rows] == [("problem", "ORB"), ("problem", "AVATAR")]
    md = report.report_markdown([], {"cloud": "c", "web": "w"}, report.log_scan(""), speakers=rows)
    assert "## The two speakers (spec 160, keel-web 256 on keel-cloud 267)" in md
    assert "| problem | ORB | intro > intro+start > film:problem > film:problem+begin > speaking:Opening" in md
    assert "| - - - - L L S - |" in md and "| - - - - L L L - |" in md
    assert "**parts at step 7**: orb `listening:Question 1 of 7`, face `listening:Question 1 of 7` (sizes)" in md
    assert "### problem: where the two speakers part" in md


def test_the_walk_helpers():
    interview = {"kind": "FULL", "gate": {"question": "In your last month, did this happen to you?",
                                          "condition": {"question": "Do you run it?"}},
                 "parts": [{"items": [{"itemId": "i1", "text": "Which comes closest?"}, {"itemId": "i2"}]}],
                 "interviewer": {"clips": {"opening": {"clipId": "o1"}}, "items": {"i1": {"clip": {"clipId": "c1"}}}}}
    assert strangers.question_count(interview) == 4
    assert strangers.question_count({**interview, "kind": "SHORT"}) == 3
    assert strangers.opening_clip(interview) == "o1"
    assert strangers.item_clip(interview, "Which comes closest?") == "c1"
    assert strangers.item_clip(interview, "Something else") is None
    line = strangers.block_line({"refused": {"block": {"line": ivs.MIC_BLOCK, "how": ivs.MIC_BLOCK_HOW},
                                             "at": {"buttons": ["ai-mic-test"]}, "stage_shown": False},
                                 "allowed": {"after": {"buttons": ["ai-start"], "mic_heard": "Heard: hello"}}})
    assert ivs.MIC_BLOCK in line and "['ai-start'], Heard: hello" in line


def test_the_words_the_walk_holds():
    assert ivs.ai_intro_spoken("Keel") == "A spoken interview with Keel, an AI interviewer, not a person."
    assert ivs.ai_intro_asks("Robin").startswith("Robin asks each question aloud")
    assert ivs.ai_intro_chips(7) == ["About 7 minutes", "Microphone needed", "Sound on"]
    assert ivs.ai_intro_chips(None) == ["Microphone needed", "Sound on"]
    assert ivs.face_mark("Robin") == "Robin · AI interviewer"
    assert ivs.face_mark("Robin", try_run=True) == "Robin · AI interviewer · try run"
    assert ivs.ai_done_title("Robin") == "Done. Your answers have gone to Robin."


# ------------------------------------------------------------------------------------------- drawn pages

@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright    # noqa: PLC0415
    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as missing:  # noqa: BLE001 - no browser on this machine
            pytest.skip(f"no Chromium: {missing}")
        yield b
        b.close()


_STAGE = """<main>
  <div data-testid="ai-intro" data-speaker="AVATAR"><h1>Robin has 3 questions for you.</h1></div>
  <div data-testid="ai-stage" data-phase="intro" data-speaker="AVATAR" hidden>
    <div data-testid="ai-facecol" data-size="large"><div data-testid="ai-face"><video></video></div></div>
    <span data-testid="ai-where"></span>
  </div>
</main>"""


def test_the_collector_reads_the_size_the_ids_the_words_the_chip_and_the_plays(browser):
    ctx = browser.new_context()
    ctx.add_init_script(ss.ORB_INTERVIEW_WATCH)
    page = ctx.new_page()
    try:
        page.set_content(_STAGE)
        page.evaluate("""() => { document.querySelector('[data-testid=ai-intro]').remove();
          const s = document.querySelector('[data-testid=ai-stage]'); s.removeAttribute('hidden');
          s.setAttribute('data-phase', 'speaking');
          document.querySelector('[data-testid=ai-where]').textContent = 'Question 1 of 3';
          s.insertAdjacentHTML('beforeend', '<div data-testid="ai-caption"><span data-testid="ship-mark">Robin · AI '
            + 'interviewer</span><p data-testid="ai-words"><span data-lit="true">Did </span><span data-lit="false">it'
            + '</span></p></div>');
          const v = document.querySelector('video'); v.setAttribute('data-clip', 'c1'); v.play().catch(() => {}); }""")
        page.wait_for_timeout(50)
        page.evaluate("""() => { document.querySelector('[data-lit=false]').setAttribute('data-lit', 'true'); }""")
        page.wait_for_timeout(50)
        page.evaluate("""() => { document.querySelector('[data-testid=ai-caption]').remove();
          const s = document.querySelector('[data-testid=ai-stage]'); s.setAttribute('data-phase', 'listening');
          const col = document.querySelector('[data-testid=ai-facecol]'); col.setAttribute('data-size', 'small');
          col.insertAdjacentHTML('beforeend', '<span data-testid="ship-mark">Robin · AI interviewer</span>'); }""")
        page.wait_for_timeout(50)
        log, plays = ss.iv_log(page), ss.iv_plays(page)
    finally:
        ctx.close()
    hidden = log[0]
    assert hidden["onStage"] is False and hidden["size"] is None and "ai-where" not in hidden["ids"]
    asked = [r for r in log if r.get("phase") == "speaking"]
    assert asked[0]["size"] == "large" and "speaker" in asked[0]["ids"] and "ai-words" in asked[0]["ids"]
    assert asked[0]["chip"] == "Robin · AI interviewer" and asked[0]["chipIn"] == "caption"
    assert asked[0]["litFirst"] is True and max(r["lit"] for r in asked) == 2 and asked[0]["words"] == "Did it"
    listening = [r for r in log if r.get("phase") == "listening"][-1]
    assert listening["size"] == "small" and listening["chipIn"] == "facecol" and listening["words"] is None
    assert plays and plays[0][2] is True and plays[0][3] == "c1"
    steps = ss.walk_steps(log)
    assert [s["step"] for s in steps][-2:] == ["speaking:Question 1 of 3", "listening:Question 1 of 3"]


_FILM = """<div data-testid="ai-stage" data-phase="story" data-speaker="ORB">
  <div data-testid="ai-orb" data-size="large" style="width:200px;height:200px">orb</div>
  <div data-testid="ai-story" data-kind="problem" data-first=""
       style="position:absolute;inset:0;z-index:40;background:#fff">
    <div data-testid="story-player" data-state="playing">
      <div data-testid="ai-film-board" aria-expanded="false"><div data-testid="story-board">
        <i class="on"></i><i class="on"></i><i></i></div></div>
      <p data-testid="story-line">Every month the report is late.</p>
      <div><button data-testid="ai-film-pause" aria-label="Pause the story"><svg></svg></button>
        <button data-testid="ai-film-again" aria-label="Start the story over"><svg></svg></button></div>
    </div>
  </div>
</div>"""


def test_the_film_is_read_whole(browser, tmp_path):
    page = browser.new_page()
    try:
        page.set_content(_FILM)
        p = ivs.Player(page, Recorder(tmp_path))
        playing = p.film()
        page.evaluate("""() => { const b = document.querySelector('[data-testid=ai-film-board]');
          b.setAttribute('aria-expanded', 'true');
          b.insertAdjacentHTML('afterend', '<ol data-testid="story-read"><li>Every month</li><li>late</li></ol>');
          const pl = document.querySelector('[data-testid=story-player]'); pl.setAttribute('data-state', 'ended');
          const acts = document.querySelector('[data-testid=ai-film-pause]').parentElement;
          acts.innerHTML = '<button data-testid="ai-film-begin">Begin the interview</button>'; }""")
        ended = p.film()
        box = p.speaker_box()
    finally:
        page.close()
    assert playing["drawn"] and playing["kind"] == "problem" and playing["first"] and playing["state"] == "playing"
    assert playing["pause"] and playing["again"] and playing["pauseLabel"] == ivs.FILM_PAUSE_LABEL
    assert playing["worded"] == [] and not playing["begin"] and playing["expanded"] == "false"
    assert playing["sig"] == {"on": 2, "off": 0, "gone": 0, "line": "Every month the report is late."}
    assert playing["inside"] == {"orb": 0, "face": 0, "video": 0} and playing["covered"] is True
    assert ended["begin"] and ended["beginWords"] == ivs.FILM_BEGIN_WORDS and ended["worded"] == [ivs.FILM_BEGIN_WORDS]
    assert ended["read"] and ended["lines"] == ["Every month", "late"] and not ended["pause"]
    assert box["drawn"] and box["id"] == "ai-orb" and box["size"] == "large" and box["covered"] is True


_INTRO_256 = """<main data-testid="ai-intro" data-intro="AI_INTERVIEWER" data-speaker="ORB">
  <div class="ivhello"><span data-testid="intro-orb"><span data-testid="story-orb"></span></span>
    <div><h1>Robin has 3 questions for you.</h1>
      <p class="iv-note">A spoken interview with Keel, an AI interviewer, not a person.</p></div></div>
  <p data-testid="ai-intro-study">About what closing the month is like for bookkeepers.</p>
  <p data-testid="ai-intro-asks">Keel asks each question aloud and listens to your answer, so you will need your
    microphone and the sound on.</p>
  <ul data-testid="ai-intro-chips"><li>About 4 minutes</li><li>Microphone needed</li><li>Sound on</li></ul>
  <section data-testid="ai-mic" data-state="fallback"><div data-testid="ai-mic-block">
    <p class="aiv-mic__block-line">This interview needs your microphone.</p>
    <p class="aiv-mic__block-how">Allow the microphone for this page in your browser, then test your mic again.</p>
  </div></section>
  <details data-testid="ai-intro-answers"><summary>What happens to your answers</summary>
    <p data-testid="ai-intro-mic-line">Your microphone is used only while you answer, and only your answers are kept.</p>
    <p data-testid="ai-intro-transcribed">Keel's transcription provider writes your answer down and keeps nothing.</p>
    <p data-testid="ai-intro-consent">Your words may be quoted.</p></details>
  <div class="aiv-intro__go"><button data-testid="ai-mic-test">Test your mic</button></div>
</main>"""


def test_the_intro_is_read_with_its_one_button_and_its_block(browser, tmp_path):
    page = browser.new_page()
    try:
        page.set_content(_INTRO_256)
        intro = ivs.Player(page, Recorder(tmp_path)).intro()
    finally:
        page.close()
    assert intro["heading"] == ivs.ai_intro_heading("Robin", 3) and intro["spoken"] == ivs.ORB_NOT_A_PERSON
    assert intro["asks"] == ivs.ai_intro_asks(ivs.ORB_NAME) and intro["chips"] == ivs.ai_intro_chips(4)
    assert intro["answers"] == {"drawn": True, "open": False, "summary": ivs.CONSENT_HEADING,
                                "lines": [ivs.AI_INTRO_MIC_LINE, ivs.INTRO_TRANSCRIBED, "Your words may be quoted."]}
    assert intro["buttons"] == ["ai-mic-test"] and intro["start_enabled"] is False and intro["mic_state"] == "fallback"
    assert intro["block"] == {"drawn": True, "line": ivs.MIC_BLOCK, "how": ivs.MIC_BLOCK_HOW}
    assert intro["fallback"] == 0 and intro["orb"] == 1


def test_the_refused_microphone_is_allowed_again(browser, tmp_path):
    page = browser.new_page()
    try:
        page.add_init_script(ivs.speech_seam(refused=True))
        page.goto("data:text/html,<p>seam</p>")
        refused = page.evaluate("() => window.__keelSpeech.mic.acquire()")
        ivs.Player(page, Recorder(tmp_path)).allow_mic()
        allowed = page.evaluate("() => window.__keelSpeech.mic.acquire()")
    finally:
        page.close()
    assert refused is False and allowed is True


# ------------------------------------------------------------------------------------------- the subject's mirror

def test_keel_webs_intro_words_are_the_walks():
    translate = _web("src/lib/translate.ts")
    if "aiIntroHeadline" not in translate:
        pytest.skip("keel-web before 256")
    assert '`${founder} has ${questions} question${questions === 1 ? "" : "s"} for you.`' in translate
    assert '`A spoken interview with ${name}, an AI interviewer, not a person.`' in translate
    assert ('`${name} asks each question aloud and listens to your answer, so you will need your microphone and the '
            'sound on.`') in translate
    assert '`About ${minutes} minutes`' in translate
    for name, words in (("AI_INTRO_MIC_NEEDED", ivs.AI_INTRO_MIC_NEEDED), ("AI_INTRO_SOUND_ON", ivs.AI_INTRO_SOUND_ON),
                        ("AI_MIC_BLOCK", ivs.MIC_BLOCK), ("AI_MIC_LABEL", ivs.MIC_LABEL),
                        ("AI_REPLAY_LABEL", ivs.REPLAY_LABEL), ("ORB_INTRO_NAME", ivs.ORB_NAME),
                        ("INTERVIEW_CONSENT_HEADING", ivs.CONSENT_HEADING)):
        assert re.search(rf'export const {name} = "{re.escape(words)}";', translate), name
    assert f'"{ivs.MIC_BLOCK_HOW}"' in translate and f'"{ivs.AI_INTRO_MIC_LINE}"' in translate
    assert '`Done. Your answers have gone to ${founder}.`' in translate
    assert '`${name} · AI interviewer`' in translate
    for key, words in (("pause", ivs.FILM_PAUSE_LABEL), ("resume", ivs.FILM_RESUME_LABEL),
                       ("begin", ivs.FILM_BEGIN_WORDS)):
        assert f'{key}: "{words}"' in translate, key
    assert 'export const INTERVIEW_WHAT_IS_KEEL = "What is Keel? →";' in translate
    assert 'AI_SAY_IT_AGAIN' not in translate and 'AI_MIC_FALLBACK' not in translate


def test_keel_webs_player_draws_what_the_walk_reads():
    player = _web("src/components/interview/ai/AiInterviewPlayer.tsx")
    assert 'data-size={isSample ? undefined : size}' in player
    assert 'const size: "large" | "small" = sheetOpen && phase !== "beat" ? "small" : "large";' in player
    assert 'data-testid="ai-story-orb"' not in player and 'data-testid="ai-story-go-on"' not in player
    assert 'title={aiDoneTitle(interview.founderFirstName?.trim() || interview.founderName)}' in player
    sheet = _web("src/components/interview/ai/Sheet.tsx")
    assert 'data-testid="ai-replay"' in sheet and 'data-testid="ai-again"' not in sheet
    words = _web("src/components/interview/ai/SpokenWords.tsx")
    assert 'data-testid="ai-words"' in words and 'data-lit={i < lit ? "true" : "false"}' in words
    film = _web("src/lib/story/StoryPlayer.tsx")
    assert 'data-paused={state === "playing" ? undefined : "true"}' in film
    assert 'aria-label={state === "playing" ? AI_FILM.pause : AI_FILM.resume}' in film
    intro = _web("src/components/interview/ai/AiIntro.tsx")
    assert '<details className="iv-consent aiv-intro__answers" data-testid="ai-intro-answers">' in intro
    assert 'data-testid="ai-start"' in intro and 'data-testid="ai-mic-block"' in intro
    assert 'data-testid="ai-mic-fallback"' not in intro and 'data-testid="start-talking"' not in intro


def test_the_web_side_walks_the_same_states():
    """keel-web 256's own two-speaker walk (`walk("ORB")` / `walk("AVATAR")`): the states this harness's steps mirror --
    the film, the film's end, the opening and the first question speaking large, the sheet small."""
    test = _web("tests/unit/the-player-pared-down-256.test.tsx")
    want = ['"film"', '"film+begin"', '"speaking:Opening:large"', '"speaking:Question 1 of 7:large"',
            '"listening:Question 1 of 7:small"']
    at = [test.find(w) for w in want]
    assert all(i >= 0 for i in at) and at == sorted(at), dict(zip(want, at))
    assert "expect(face.states).toEqual(orb.states);" in test and "expect(face.words).toEqual(orb.words);" in test


def test_the_refusal_hook_is_keel_webs_name():
    fixture = WEB / "tests" / "fixtures" / "interviewer" / "fakeSpeech.ts"
    if not fixture.exists():
        pytest.skip("no fakeSpeech fixture in the checkout")
    text = fixture.read_text(encoding="utf-8")
    assert "__micRefused" in text and "__micRefused" in ivs.speech_seam(refused=True)
