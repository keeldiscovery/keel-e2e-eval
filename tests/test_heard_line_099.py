"""Spec 099 (keel-web 143): the interviewer marks read the ear's states -- *Listening…*, *Hearing you…*, *Writing down
what you said…*, the words; *Heard so far: nothing yet* only after an empty transcript; *Test your mic* draws the sheet's
waveform and the same writing state before *Heard: hello*.

FR-1: the words restated (`evals/interviewer_marks.py`, `harness/interviewer_screens.py`) and held to keel-web's
`translate.ts`; the screens walker samples the heard line (`FLOW_TIMELINE`'s `__keelHeard`, `Player.heard_lines`) and
IM19 reads every recorded window off it (`heard_windows`). FR-2: IM17 reads the wave and the writing state
(`Player.mic_test` holds the recorder's stop to catch it). FR-3: `INTERVIEWER_MARKS_VERSION` 16 -> 17 with its note.
"""

from __future__ import annotations

import copy
import inspect
import re

import pytest
from playwright.sync_api import sync_playwright

from evals import interviewer_leg as leg
from evals import interviewer_marks as marks
from harness import interviewer_screens as ivs
from harness.steps import Recorder
from stack.config import load_config

from tests.test_interviewer_marks import good


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _web_143(rel: str) -> str:
    path = load_config(validate=False).keel_web / rel
    if not path.is_file():
        pytest.skip(f"keel-web has no {rel}")
    text = path.read_text(encoding="utf-8")
    translate = (load_config(validate=False).keel_web / "src/lib/translate.ts").read_text(encoding="utf-8")
    if "AI_HEARD_WRITING_DOWN" not in translate:
        pytest.skip("keel-web predates spec 143 (no writing state on the heard line)")
    return text


def _check(record: dict, mark: str) -> marks.Check:
    return {c.mark: c for c in marks.score(record)}[mark]


# ------------------------------------------------------------------------------------------- FR-1: the words

@pytest.mark.parametrize("name, word", [("AI_HEARD_LISTENING", marks.LISTENING_LINE),
                                        ("AI_HEARD_WRITING_DOWN", marks.HEARD_WRITING_DOWN),
                                        ("AI_HEARD_NOTHING", marks.HEARD_NOTHING),
                                        ("HEARING_YOU", marks.HEARING_YOU),
                                        ("AI_WRITING_DOWN", marks.WRITING_DOWN)])
def test_the_heard_lines_words_are_keel_webs_own(name, word):
    """keel-web 143 kept the status line's *Writing it down…* (`AI_WRITING_DOWN`) and added the heard line's
    *Writing down what you said…* (`AI_HEARD_WRITING_DOWN`); the marks keep both, under keel-web's split."""
    assert f'export const {name} = "{word}";' in _web_143("src/lib/translate.ts"), name


def test_the_marks_and_the_screens_say_the_same_words():
    assert (marks.LISTENING_LINE, marks.HEARD_WRITING_DOWN, marks.HEARD_NOTHING, marks.HEARING_YOU) == (
        ivs.HEARD_LISTENING, ivs.HEARD_WRITING_DOWN, ivs.HEARD_NOTHING, ivs.HEARING_YOU)
    assert marks.WRITING_DOWN == ivs.WRITING_DOWN == "Writing it down…"            # the status line, unchanged


def test_the_heard_line_carries_its_state_in_keel_web():
    sheet = _web_143("src/components/interview/ai/Sheet.tsx")
    assert 'data-testid="ai-heard" data-heard={heardLine.state}' in sheet
    union = '"listening" | "hearing" | "writing" | "words" | "nothing"'
    assert union in sheet and tuple(s.strip(' "') for s in union.split("|")) == ivs.HEARD_STATES


def test_test_your_mics_ids_are_keel_webs_own():
    intro = _web_143("src/components/interview/ai/AiIntro.tsx")
    for built in ('data-testid="ai-mic" data-state={state}', 'data-testid="ai-mic-level"', 'testId="ai-mic-wave"',
                  'data-testid="ai-mic-writing-line"', "{AI_HEARD_WRITING_DOWN}", "{AI_SAY_HELLO}"):
        assert built in intro, built
    assert 'state === "listening" || state === "writing"' in intro          # Say hello and the wave stay while writing
    check = _web_143("src/lib/micCheck.ts")
    assert '"idle" | "asking" | "listening" | "writing" | "passed" | "fallback"' in check
    # the writing state is drawn before the recorder's stop, so a held stop keeps it on the screen
    assert check.index('this.state = "writing";') < check.index("await recorder.stop()")
    wave = _web_143("src/components/interview/ai/MicWave.tsx")
    assert 'data-testid={writing ? "ai-mic-writing" : (testId ?? "ai-mic-on")}' in wave
    assert 'data-state={writing ? "writing" : "listening"}' in wave and "data-level={bucket}" in wave
    assert wave.count("BARS = [") == 1 and wave.split("BARS = [", 1)[1].split("]", 1)[0].count(",") + 1 == \
        marks.MIC_WAVE_BARS
    # the meter is gone (a comment may still name it; no element is classed with it)
    assert not re.search(r'className=[^>]*\baiv__level\b', "".join(
        p.read_text(encoding="utf-8") for p in (load_config(validate=False).keel_web / "src").rglob("*.tsx")))


# -------------------------------------------------------------------------- FR-1: the recorded windows (IM19)

def _line(*states: str, question: str = "Which fits?") -> list[dict]:
    words = {"listening": marks.LISTENING_LINE, "hearing": marks.HEARING_YOU, "writing": marks.HEARD_WRITING_DOWN,
             "words": "Heard Agency A", "nothing": marks.HEARD_NOTHING, None: None}
    return [{"t": float(i), "state": s, "words": words[s], "question": question} for i, s in enumerate(states)]


def test_143s_window_is_read_and_the_old_lines_window_is_named():
    windows, faults = marks.heard_windows(_line("listening", "hearing", "writing", "words"))
    assert windows == [["hearing", "writing", "words"]] and faults == []
    # before 143: *nothing yet* through the send
    windows, faults = marks.heard_windows(_line("listening", "hearing", "nothing", "words"))
    assert windows == [] and faults[0]["fault"] == "nothing yet after a sound"
    windows, faults = marks.heard_windows(_line("hearing", "words"))
    assert faults[0]["fault"] == "no writing between the pause and the words"
    windows, faults = marks.heard_windows(_line("hearing", "writing", "nothing", "words"))
    assert faults[0]["fault"] == "nothing yet between the pause and the words"


def test_nothing_yet_closes_a_window_on_an_empty_transcript_alone():
    windows, faults = marks.heard_windows(_line("hearing", "writing", "nothing", "hearing", "writing", "words"))
    assert windows == [["hearing", "writing", "words"]] and faults == []
    windows, faults = marks.heard_windows(_line("hearing", "writing", "nothing", "listening"))
    assert windows == [] and faults == []


def test_an_option_question_stays_writing_until_the_read_lands():
    """keel-web 143: on an option question the line starts at `hearing` and stays `writing` until the read lands --
    the timeline keeps one entry per change, so a long send is still one `writing`."""
    lines = _line("listening", "hearing", "writing", "writing", "words")
    assert marks.heard_windows(lines) == ([["hearing", "writing", "words"]], [])


def test_a_window_closed_unread_is_neither_read_nor_a_fault():
    for states in (("hearing", None, "words"), ("hearing", "listening", "words"), ("listening", "words")):
        assert marks.heard_windows(_line(*states)) == ([], []), states
    moved = _line("hearing", "writing") + _line("words", question="Next?")
    assert marks.heard_windows(moved) == ([], [])


def test_im19_reads_the_heard_line_and_a_writing_line_after_the_pause():
    record = good()
    assert _check(record, "IM19").ok, _check(record, "IM19").detail
    assert _check(record, "IM19").detail["windows read"] == 2
    record["hear_out"]["after_first"]["after"]["heard"] = marks.HEARD_WRITING_DOWN        # FR-1: accepted
    assert _check(record, "IM19").ok
    record["hear_out"]["after_first"]["after"]["heard"] = marks.HEARD_NOTHING
    assert not _check(record, "IM19").ok
    record = good()
    del record["hear_out"]["heard_lines"]                                               # a v16 record
    check = _check(record, "IM19")
    assert check.measured and not check.ok and check.detail["windows read"] == 0


def test_im19_names_the_window_that_said_nothing_yet():
    record = good()
    record["hear_out"]["heard_lines"][2]["state"] = "nothing"
    check = _check(record, "IM19")
    assert not check.ok and check.detail["heard line faults"][0]["states"] == ["hearing", "nothing"]


_SHEET = """<div data-testid="ai-sheet"><p class="iv-q">Which fits?</p><p data-testid="ai-heard"
  data-heard="listening">Listening…</p><p data-testid="ai-status">Recording your answer.</p></div>"""


def test_the_timeline_samples_the_heard_line_through_the_send(tmp_path, browser):
    page = browser.new_page()
    try:
        page.set_content(f"<script>{ivs.FLOW_TIMELINE}</script>{_SHEET}")
        for state, words in (("hearing", marks.HEARING_YOU), ("writing", marks.HEARD_WRITING_DOWN),
                             ("words", "Heard Agency A")):
            page.evaluate("([s, w]) => { const l = document.querySelector('[data-testid=ai-heard]');"
                          " l.setAttribute('data-heard', s); l.textContent = w; }", [state, words])
            page.wait_for_timeout(30)
        page.evaluate("() => document.querySelector('[data-testid=ai-heard]').remove()")
        page.wait_for_timeout(30)
        lines = ivs.Player(page, Recorder(tmp_path)).heard_lines()
    finally:
        page.close()
    assert [(e["state"], e["words"], e["question"]) for e in lines] == [
        ("listening", "Listening…", "Which fits?"), ("hearing", "Hearing you…", "Which fits?"),
        ("writing", "Writing down what you said…", "Which fits?"), ("words", "Heard Agency A", "Which fits?"),
        (None, None, "Which fits?")]
    assert marks.heard_windows(lines) == ([["hearing", "writing", "words"]], [])


def test_the_leg_keeps_the_heard_line_on_hear_out():
    source = inspect.getsource(leg)
    assert "heard_lines = player.heard_lines()" in source and '"heard_lines": heard_lines' in source


# --------------------------------------------------------------------------- FR-2: Test your mic's wave (IM17)

#: keel-web 143's `MicBlock`, as a page: *Test your mic* -> listening (the wave in `ai-mic-level`) -> the hello's
#: silence -> writing (the wave held, the writing line) -> the recorder's stop -> *Heard: hello*, Start enabled. The
#: harness's own seam (`SPEECH_SEAM`) is the recorder; its stop is what `Player.mic_test` holds.
_INTRO = """<main data-testid="ai-intro" data-intro="AI_INTERVIEWER"><h1>Daphne will ask you 5 questions.</h1>
<section data-testid="ai-mic" data-state="idle"><button data-testid="ai-mic-test">Test your mic</button></section>
<button data-testid="start-talking" disabled>Start the interview</button></main>
<script>
(() => {
  const block = document.querySelector('[data-testid=ai-mic]');
  const wave = (writing) => '<span class="aiv__wave" data-testid="' + (writing ? 'ai-mic-writing' : 'ai-mic-wave')
    + '" data-state="' + (writing ? 'writing' : 'listening') + '" data-level="2">' + '<i></i>'.repeat(5) + '</span>';
  const draw = (state, heard) => {
    block.setAttribute('data-state', state);
    if (state === 'passed') { block.innerHTML = '<p data-testid="ai-mic-heard">Heard: ' + heard + '</p>'; return; }
    block.innerHTML = '<div><p class="aiv-mic__say">Say hello</p><div data-testid="ai-mic-level">'
      + wave(state === 'writing') + '</div>'
      + (state === 'writing' ? '<p data-testid="ai-mic-writing-line">Writing down what you said…</p>' : '') + '</div>';
  };
  document.querySelector('[data-testid=ai-mic-test]').addEventListener('click', async () => {
    const recorder = window.__keelSpeech.recorder;
    draw('listening');
    let silence;
    const finish = async () => {
      draw('writing');
      const { audio } = await recorder.stop();
      const bytes = Uint8Array.from(atob(audio), (c) => c.charCodeAt(0));
      const text = new TextDecoder().decode(bytes).replace(/\\0+$/, '');
      draw('passed', text);
      document.querySelector('[data-testid=start-talking]').disabled = false;
    };
    await recorder.start((rms) => {
      if (rms > 0.02) { clearTimeout(silence); silence = setTimeout(finish, 300); }
    });
  });
})();
</script>"""


def test_the_mic_test_reads_the_wave_then_the_writing_state_it_held(tmp_path, browser):
    page = browser.new_page()
    try:
        page.set_content(f"<script>{ivs.SPEECH_SEAM}</script>{_INTRO}")
        mic = ivs.Player(page, Recorder(tmp_path)).mic_test("hello", timeout_s=10)
        stops = page.evaluate("() => (window.__recordStops || []).length")
    finally:
        page.close()
    assert mic["listening"] == {"state": "listening", "wave": "ai-mic-wave", "wave_state": "listening", "bars": 5,
                                "level": "2", "meter": 0, "mic_on": 0, "writing_line": None, "say": "Say hello",
                                "mic_heard": None, "start_enabled": False}
    assert mic["writing"] == {"state": "writing", "wave": "ai-mic-writing", "wave_state": "writing", "bars": 5,
                              "level": "2", "meter": 0, "mic_on": 0, "writing_line": marks.HEARD_WRITING_DOWN,
                              "say": "Say hello", "mic_heard": None, "start_enabled": False}
    assert mic["after"]["mic_heard"] == "Heard: hello" and mic["after"]["start_enabled"] is True and stops == 1
    record = good()
    record["mic_test"] = mic
    assert _check(record, "IM17").ok, _check(record, "IM17").detail


def test_im17_owes_the_wave_and_the_writing_state():
    record = good()
    assert _check(record, "IM17").ok
    for key in ("listening", "writing"):
        old = copy.deepcopy(record)
        del old["mic_test"][key]                                                       # a v16 record
        assert not _check(old, "IM17").ok, key
    record["mic_test"]["listening"]["wave"] = None                                     # the meter, not the wave
    record["mic_test"]["listening"]["meter"] = 1
    assert not _check(record, "IM17").ok


# ------------------------------------------------------------------------------------------ FR-3: the version

def test_the_version_moved_with_its_note():
    assert marks.INTERVIEWER_MARKS_VERSION == 17
    source = inspect.getsource(marks)
    assert "#: v17 (spec 099 FR-1 / FR-2, keel-web 143" in source and "#: v16 (spec 094 FR-1" in source
    assert "make eval-live K=s012" in source                                           # the paid re-run is the founder's
