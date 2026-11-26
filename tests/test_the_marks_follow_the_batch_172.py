"""Spec 172: the marks follow the evening batch -- keel-web 274 (the respondent's long answers), 275 (the beat told by the
orb), 276 (finalize by hand, the solution's frames); keel-cloud 283 (the solution film takes the problem's path, the
recap cut), 285 (the questions in code's own short frames).

FR-1 the founder's beats (four states, one ask, a done word alone after the card ends the beat, *none* at once,
`beat-no-transcript`); FR-2 the player (the story in two parts, acknowledged; the four states); FR-3 the boxes
(Finalize pressed, `boxes-auto-advanced`, the sheet's step two); FR-4 the solution's frames (chapters, chips, notes, a
retired chapter a DRIFT line, a failed build only on no picture); FR-5 the recap's five lines; FR-6 the short frames by
`framed`, the screener's twelve words; FR-7 the version and the fake door's words. Fixtures and the archived siblings
only (FR-8): nothing paid, no stack.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from evals import interviewer_marks as marks
from harness import film_frames as ff
from harness import interviewer_fake as fake
from harness import interviewer_screens as ivs
from harness import solution_surfaces as sol
from harness import story_screens as ss
from harness import three_surfaces as ts
from harness.steps import Recorder
from quality import film_table
from stack.config import load_config

CONFIG = load_config(validate=False)
CLOUD = Path(CONFIG.keel_cloud)
WEB = Path(CONFIG.keel_web)
JAVA = CLOUD / "src" / "main" / "java" / "com" / "keeldiscovery" / "cloud"
BASE = "http://batch.test"


def _need(path: Path) -> Path:
    if not path.exists():
        pytest.skip(f"no {path}")
    return path


def _web(rel: str) -> str:
    return _need(WEB / rel).read_text(encoding="utf-8")


def _java(rel: str) -> str:
    return _need(JAVA / rel).read_text(encoding="utf-8")


def _ts_string(words: str) -> list[str]:
    """A string as a TypeScript source may hold it: double-quoted, or single-quoted with its apostrophes escaped."""
    return [f'"{words}"', "'" + words.replace("'", "\\'") + "'"]


def _in(source: str, words: str) -> bool:
    return any(form in source for form in _ts_string(words))


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _page(browser, path: str, body: str):
    page = browser.new_page()
    page.route(f"{BASE}/**", lambda r: r.fulfill(status=200, content_type="text/html; charset=utf-8",
                                                 body=f"<!doctype html><html><body>{body}</body></html>"))
    page.goto(f"{BASE}{path}")
    return page


# ------------------------------------------------------------------------------------------- FR-1 the words (web 275)

def test_the_beats_words_and_states_are_keel_web_275s():
    translate = _web("src/lib/translate.ts")
    for words in (ss.BEAT_ASK, ss.BEAT_GOT_IT, ss.BEAT_GOT_IT_NONE, ss.SHOW_THE_QUESTION, ss.BEAT_NO_WORDS,
                  *ss.BEAT_STATE_WORDS.values(), *ss.BEAT_SUBS):
        assert _in(translate, words), words
    orb = _web("src/components/voice/KeelOrb.tsx")
    assert "ORB_STATES: readonly OrbState[] = [" + ", ".join(f'"{s}"' for s in ss.ORB_STATES) + "]" in orb
    hands = _web("src/lib/story/handsFree.ts")
    assert f"WAIT_MS = {ss.WAIT_MS:_}" in hands
    web_done = re.search(r"DONE_WORDS = \[(.*?)\] as const", hands, re.S).group(1)
    for word in ss.DONE_WORDS:
        assert f'"{word.lower()}"' in web_done, word
    stage = _web("src/components/voice/VoiceStage.tsx")
    for testid in (ss.BEAT_ASK_ID, ss.BEAT_QUESTION_FOLD_ID, ss.BEAT_NO_WORDS_ID):
        assert f'"{testid}"' in stage, testid
    # 257's small print and the 20 s / 60 s asks are gone from keel-web, and from the harness
    assert '"Take your time. Say \\"that\'s it\\" when you are done."' not in translate
    assert not re.search(r"export const (ANYTHING_ELSE_AGAIN_MS|ANYTHING_ELSE_MS|THINK_MS)\b", hands)
    for gone in ("THINK_LINE", "LONG_BEAT_SUB", "THINK_MS", "ANYTHING_ELSE_MS"):
        assert not hasattr(ss, gone), gone
    assert ss.LONG_BEATS == ss.BEATS and ss.WAIT_MS / 1000 < ss.TWO_PART_QUIET_S


def test_the_orbs_states_are_read_in_the_four_with_272s_mapped():
    assert [ss.orb_state(s) for s in ("speaking", "listening", "hearing", "writing", "dim", "paused", "asking")] == [
        "asking", "hearing", "hearing", "thinking", "waiting", "paused", "asking"]
    assert ss.plain_sequence(["speaking", "listening", "hearing", "writing", "speaking", "listening"]) == ss.BEAT_ORB
    assert ss.beat_orb_holds(["asking", "hearing", "waiting", "hearing", "thinking", "asking", "hearing"])
    assert not ss.beat_orb_holds(["asking", "hearing", "thinking", "hearing"])               # no card read after it
    log = [{"state": "asking", "line": "Keel is asking", "chime": 0, "mic": False, "t": 1},
           {"state": "hearing", "line": "Keel is hearing you", "chime": 1, "mic": True, "t": 2}]
    v = ss.chime_verdict(log)
    assert v["hand_overs"] == 1 and v["one_each"] and v["your_turn"] and v["mic_open"]


def test_the_mark_beat_no_transcript_and_the_one_ask_are_read_off_the_logs():
    clean = [{"path": "/p/x/define/story/3", "transcript": 0, "ask": None},
             {"path": "/p/x/define/story/3", "transcript": 0, "ask": ss.BEAT_ASK},
             {"path": "/p/x/define/story/3", "transcript": 0, "ask": ss.BEAT_ASK}]
    assert ss.no_transcript(clean, [], "/define/story/3")["ok"]
    drew = clean + [{"path": "/p/x/define/story/3", "transcript": 1}]
    assert not ss.no_transcript(drew, [], "/define/story/3")["ok"]
    heard = [{"path": "/p/x/define/story/3", "said": [{"who": "you", "text": "They check it"}], "keel": []}]
    assert not ss.no_transcript(clean, heard, "/define/story/3")["ok"]
    assert ss.no_transcript(drew, [], "/define/story/4")["ok"]                    # another beat's frame is not read
    assert ss.asks_seen(clean) == 1
    assert ss.asks_seen(clean + [{"ask": None}, {"ask": ss.BEAT_ASK}]) == 2          # a second ask is counted
    assert ss.said_none("none") and ss.said_none("No setup.") and not ss.said_none("none of them, they check it")


def test_a_done_word_is_said_after_a_stop():
    assert ss.with_done_word("someone gets paid wrong") == "someone gets paid wrong. That's it."
    assert ss.with_done_word("They check it by hand.") == "They check it by hand. That's it."
    assert ss.ends_on_a_done_word(ss.with_done_word("a b")) and ss.ends_on_a_done_word("It ends. Nothing else.")


# ------------------------------------------------------------------------------------------- FR-1 a beat on a page

#: keel-web 275's beat, restated: the question, the founder's words heard to their done word, the cloud's reading
#: (`PUT story/turns/{n}`), the card with its rows, Keel's one line (`beat-ask`), and a done word alone after the card
#: ends the beat (*Got it.*, the next beat). Nothing the founder says is written. `?reask=1` draws the defect of
#: 2026-11-25 instead: a done word alone after the card asks the question again.
BEAT_275 = """<div class="vstage" data-testid="story-turn" data-turn="1" data-voice="on" data-beat="">
<button data-testid="story-orb" data-state="asking"></button>
<p data-testid="story-state" data-state="asking"><span class="vstage__state-line">Keel is asking</span></p>
<h1 data-testid="story-q">Who has this problem?</h1><div id="card"></div><p id="ask"></p></div>
<script>
const orb = document.querySelector('[data-testid=story-orb]');
const line = document.querySelector('.vstage__state-line');
const st = (s, w) => { orb.setAttribute('data-state', s); document.querySelector('[data-testid=story-state]')
  .setAttribute('data-state', s); line.textContent = w; };
let open = false, carded = false;
window.__said = [];
window.__listening = () => open;
const ask = (w) => { const p = document.querySelector('#ask'); p.setAttribute('data-testid', 'beat-ask'); p.textContent = w; };
setTimeout(() => { open = true; st('hearing', 'Keel is hearing you'); }, 200);
let parts = [];
window.__say = async (w) => {
  window.__said.push(w);
  if (!carded && !/that's it\\.?$/i.test(w)) {
    // a part with no done word: the beat stays open; after the quiet the orb turns amber and Keel asks once
    parts.push(w); st('hearing', 'Keel is hearing you');
    setTimeout(() => { st('waiting', 'Take your time'); ask('Anything else? Say "that\\'s it" when you are done.'); }, 600);
    return true;
  }
  if (!carded && /that's it\\.?$/i.test(w)) {
    open = false; st('thinking', 'Keel is thinking');
    parts.push(w.replace(/\\s*that's it\\.?$/i, ''));
    const r = await fetch('/v2/projects/p1/story/turns/1', { method: 'PUT', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ text: parts.join(' ') }) });
    await r.json();
    carded = true;
    document.querySelector('#card').innerHTML = '<div data-testid="story-understood"><span class="ucard__label">What Keel '
      + 'understood</span><div data-box="person"><span class="ucard__name">The person</span>'
      + '<span class="ucard__words">Payroll leads</span></div></div>';
    document.querySelector('[data-testid=story-q]').setAttribute('data-folded', '');
    st('asking', 'Keel is asking');
    setTimeout(() => { ask('Anything else? Say "that\\'s it" when you are done.'); open = true;
                       st('hearing', 'Keel is hearing you'); }, 150);
    return true;
  }
  if (carded && /^that's it\\.?$/i.test(w)) {
    open = false; ask('Got it.'); st('asking', 'Keel is asking');
    if (location.search.includes('reask')) { setTimeout(() => { document.querySelector('#card').innerHTML = '';
      document.querySelector('#ask').textContent = ''; }, 100); return true; }
    setTimeout(() => history.pushState({}, '', '/p/p1/define/story/2'), 150);
  }
  return true;
};
</script>"""


def _beat_page(browser, query: str = ""):
    page = browser.new_page()
    page.add_init_script(ss.ORB_WATCH)
    page.route(f"{BASE}/p/**", lambda r: r.fulfill(status=200, content_type="text/html; charset=utf-8",
                                                   body=f"<!doctype html><html><body>{BEAT_275}</body></html>"))
    page.route(f"{BASE}/v2/**", lambda r: r.fulfill(status=200, content_type="application/json",
                                                    body=json.dumps({"next": 2, "story": {}, "readback": "unsaid"})))
    page.goto(f"{BASE}/p/p1/define/story/1{query}")
    return page


def test_a_beat_is_answered_its_card_read_and_ended_by_the_done_word_alone(browser, tmp_path):
    page = _beat_page(browser)
    try:
        walk = ss.StoryWalk(page, Recorder(tmp_path), BASE, patience=0.2)
        walk.listen()
        seen = walk.beat(1, "Payroll leads in small teams")
        said = page.evaluate("() => window.__said")
    finally:
        page.close()
    assert said == ["Payroll leads in small teams. That's it.", "That's it."]
    assert seen["put"]["sent"] == {"text": "Payroll leads in small teams."}
    assert seen["card"]["ask"] == ss.BEAT_ASK and not seen["straight_on"]
    assert seen["readback"]["questionFolded"] is True and seen["readback"]["transcript"] == 0
    assert seen["closed"]["by"] == "the done word after the card" and seen["closed"]["got_it"] is True
    assert seen["closed"]["stayed"] is False and seen["next"] == "2"
    assert seen["transcript"]["ok"] and ss.beat_orb_holds(seen["orb"]), seen["orb"]


def test_a_done_word_that_asks_the_question_again_is_named(browser, tmp_path):
    page = _beat_page(browser, "?reask=1")
    try:
        walk = ss.StoryWalk(page, Recorder(tmp_path), BASE, patience=0.05)
        walk.listen()
        with pytest.raises(AssertionError, match="did not end the beat"):
            walk.beat(1, "Payroll leads")
    finally:
        page.close()


# ------------------------------------------------------------------------------------------- FR-2 the player (web 274)

def test_the_players_long_answer_words_are_keel_web_274s():
    translate = _web("src/lib/translate.ts")
    for words in (ivs.STORY, ivs.LONG_ASK, ivs.LONG_GOT_IT, ivs.LONG_CAP):
        assert _in(translate, words), words
    assert ivs.LONG_ASK == ss.BEAT_ASK == fake.ANYTHING_ELSE and ivs.LONG_GOT_IT == fake.GOT_IT
    assert ivs.LONG_CAP == fake.TWO_MINUTES
    sheet = _web("src/components/interview/ai/Sheet.tsx")
    assert f'"{ivs.LONG_ASK_ID}"' in sheet and f'"{ivs.LONG_GOT_IT_ID}"' in sheet
    player = _web("src/components/interview/ai/AiInterviewPlayer.tsx")
    assert f'"{ivs.PASSAGE_CAPTION}"' in player and f'"{ivs.NO_WORDS_ID}"' in player
    flow = _web("src/lib/aiInterviewFlow.ts")
    assert "STORY_LONG_CAP_MS" in flow and str(ivs.STORY_CAP_MS) in flow.replace("_", "")
    assert ivs.STORY_PAUSE_S * 1000 < ivs.LONG_WAIT_MS and ivs.STORY_PAUSE_S * 1000 > 2_500     # past PAUSE_MS
    assert ivs.STORY_BEFORE_274 not in translate
    assert marks.INTERVIEWER_MARKS_VERSION == 20 and marks.STORY == ivs.STORY and marks.LONG_GOT_IT == ivs.LONG_GOT_IT


def test_a_story_is_split_in_two_at_a_sentence_and_ends_on_the_done_word():
    assert ivs.story_parts("We waited six weeks for it. Nobody could say why. Then it came.") == [
        "We waited six weeks for it.", "Nobody could say why. Then it came. That's it."]      # the cut nearest the middle
    assert ivs.story_parts("One long sentence without a stop") == ["One long sentence without a stop. That's it."]
    assert ivs.story_parts("A why.", parts=1) == ["A why. That's it."]


#: keel-web 274's story window, restated: the recorder open through a pause, Keel's one ask after a quiet, the close word
#: heard last closes it and Keel acknowledges (`ai-story-got-it`); a page before 274 (`?held=1`) holds it instead.
PLAYER_274 = """<div data-testid="ai-sheet"><p class="iv-q">Tell me about the last time.</p>
<p data-testid="ai-status">Take your time. Say "that's it" when you are done, or tap Save.</p></div><script>
window.__said = []; let open = true;
window.__listening = () => open;
window.__recordStarts = [1];
window.__say = (w) => { window.__said.push(w);
  if (/that's it\\.?$/i.test(w)) { open = false; const st = document.querySelector('[data-testid=ai-status]');
    if (location.search.includes('held')) { st.textContent = 'Got it. Moving on… say no to change'; return true; }
    st.innerHTML = '<span data-testid="ai-story-got-it" data-ack="gotIt">Got it. Thank you.</span>';
    setTimeout(() => { document.querySelector('.iv-q').textContent = 'How often does this happen to you?';
      st.textContent = 'Listening.'; }, 300); }
  return true; };
</script>"""


def test_the_story_is_told_in_two_parts_and_acknowledged(browser, tmp_path):
    page = _page(browser, "/i/t1", PLAYER_274)
    try:
        p = ivs.Player(page, Recorder(tmp_path), patience=0.2)
        told = p.say_story("We waited six weeks. Nobody could say why.", pause_s=0.5)
        closed = p.long_close(timeout_s=10)
        said = page.evaluate("() => window.__said")
    finally:
        page.close()
    assert said == ["We waited six weeks.", "Nobody could say why. That's it."]
    assert told["open_across"] is True and told["ack"] == ivs.LONG_GOT_IT and told["ack_kind"] == "gotIt"
    assert not told["held"] and closed["went_on"] and closed["next"] == ts.FREQUENCY_FILM


def test_a_story_held_as_before_274_is_named(browser, tmp_path):
    page = _page(browser, "/i/t1?held=1", PLAYER_274)
    try:
        p = ivs.Player(page, Recorder(tmp_path), patience=0.05)
        told = p.say_story("We waited six weeks.", parts=1)
    finally:
        page.close()
    assert told["ack"] is None and told["held"] is True


def test_the_players_runs_read_in_the_four_states():
    log = [{"state": s} for s in ("asking", "hearing", "waiting", "hearing", "thinking", "asking", "hearing")]
    assert ss.orb_answer_runs(log) == [["asking", "hearing", "waiting", "hearing", "thinking"], ["asking", "hearing"]]
    assert "ai-passage-caption" in ss.ORB_INTERVIEW_WATCH and "ai-story-got-it" in ss.ORB_INTERVIEW_WATCH


# ------------------------------------------------------------------------------------------- FR-3 the boxes (web 276)

def test_the_boxes_words_are_keel_web_276s():
    translate = _web("src/lib/translate.ts")
    for kind in ("story", "idea"):
        for words in (ss.BOXES_LINE[kind], ss.BOXES_PRESS[kind], ss.FINALIZE[kind], ss.FINALITY[kind]):
            assert _in(translate, words), words
    for words in (ss.FIX_WHAT_TO_CHANGE, ss.FIX_UPDATED, *ss.STORY_BOX_NAMES.values(), *ss.IDEA_BOX_NAMES.values()):
        assert _in(translate, words), words
    assert "updated: (box: string): string => `${box} is updated.`" in translate
    review = _web("src/components/story/BoxesReview.tsx")
    for testid in (ss.BOXES_YES_ID, ss.BOXES_NO_ID, "boxes-finality", "boxes-fix-said", "boxes-fix-box"):
        assert f'"{testid}"' in review, testid
    assert "It says:" not in translate.split("fix: {")[1][:1500]                       # 276 FR-3: the sheet unrepeated
    assert ss.box_updated("Also on their plate") == f"Also on their plate is updated. {ss.BOXES_LINE['story']}"


#: keel-web 276's table, restated: Keel's line under the two buttons, the table waiting (a bare yes or the quiet never
#: moves it); **Finalize** posts the confirm. `?auto=1`: a page before 276 that confirms by itself after the line.
TABLE_276 = """<div class="vstage" data-testid="story-boxes-screen"><button data-testid="story-orb" data-state="hearing"></button>
<div data-testid="boxes-ask"><p data-testid="story-check-said"></p><div id="btns"></div></div></div><script>
window.__listening = () => true; window.__say = () => true;
setTimeout(() => {
  document.querySelector('[data-testid=story-check-said]').textContent =
    'Take your time. When you are done, press Finalize the problem.';
  document.querySelector('#btns').innerHTML = '<button data-testid="boxes-yes">Finalize the problem</button>'
    + '<button data-testid="boxes-no">No, change something</button><p data-testid="boxes-finality">Once finalized, '
    + 'the problem cannot be changed. The film can still be fixed frame by frame.</p>';
  document.querySelector('[data-testid=boxes-yes]').onclick = () => fetch('/v2/projects/p1/story/confirm',
    { method: 'POST' }).then(() => history.pushState({}, '', '/p/p1/define/story/check/film'));
  if (location.search.includes('auto')) setTimeout(() => fetch('/v2/projects/p1/story/confirm', { method: 'POST' })
    .then(() => history.pushState({}, '', '/p/p1/define/context/window')), 300);
}, 150);
</script>"""


def _table(browser, query: str = ""):
    page = browser.new_page()
    page.add_init_script(ss.ORB_WATCH)
    page.route(f"{BASE}/p/**", lambda r: r.fulfill(status=200, content_type="text/html; charset=utf-8",
                                                   body=f"<!doctype html><html><body>{TABLE_276}</body></html>"))
    page.route(f"{BASE}/v2/**", lambda r: r.fulfill(status=200, content_type="application/json",
                                                    body=json.dumps({"status": "defined"})))
    page.goto(f"{BASE}/p/p1/define/story/check{query}")
    return page


def test_the_table_waits_and_finalize_is_pressed(browser, tmp_path):
    page = _table(browser)
    try:
        walk = ss.StoryWalk(page, Recorder(tmp_path), BASE, patience=0.2)
        walk.listen()
        seen = walk.finalize_boxes("story", hold_s=1.0)
    finally:
        page.close()
    assert seen["line"] == ss.BOXES_LINE["story"] and seen["finalize"] == ss.FINALIZE["story"]
    assert seen["finality"] == ss.FINALITY["story"] and seen["line_once"] and seen["auto_advanced"] is False
    assert seen["pressed"] == ss.FINALIZE["story"] and seen["confirm"]["status"] == 200


def test_a_table_that_moves_on_by_itself_is_boxes_auto_advanced(browser, tmp_path):
    page = _table(browser, "?auto=1")
    try:
        walk = ss.StoryWalk(page, Recorder(tmp_path), BASE, patience=0.2)
        walk.listen()
        seen = walk.finalize_boxes("story", hold_s=3.0)
    finally:
        page.close()
    assert seen["auto_advanced"] is True and "confirm" not in seen and "pressed" not in seen


# ------------------------------------------------------------------------------------------- FR-4 the solution's frames

def test_the_contract_is_96_with_three_chapters_and_the_plan_rows_note():
    import yaml                                                                 # noqa: PLC0415
    doc = yaml.safe_load(_need(CLOUD / "canon" / "openapi-v2.yaml").read_text(encoding="utf-8"))
    assert doc["info"]["x-keel-contract"] >= 96
    scene = doc["components"]["schemas"]["IdeaScene"]["properties"]["chapter"]
    assert scene["enum"] == list(ss.IDEA_CHAPTERS) + [None]
    flat = json.dumps(doc["components"]["schemas"])
    assert '"note"' in flat
    translate = _web("src/lib/translate.ts")
    for key, words in ss.IDEA_PLAN_CHIPS.items():
        assert f'{key}: "{words}"' in translate, key
    plan = _web("src/components/story/FramePlan.tsx")
    assert '"story-plan-chip"' in plan and '"story-plan-note"' in plan


def test_the_chips_and_notes_are_held_to_the_served_plan():
    served = [{"scene": 1, "chapter": "before", "status": "passed"}, {"scene": 2, "chapter": "task", "status": "failed",
                                                                     "note": "The screen shows no brand."},
              {"scene": 3, "chapter": "joy", "status": "planned"}]
    rows = [{"scene": "1", "status": "passed", "chip": "Opening", "note": None},
            {"scene": "2", "status": "failed", "chip": "What it does", "note": "The screen shows no brand."},
            {"scene": "3", "status": "planned", "chip": "What they get", "note": None}]
    assert ss.plan_chip_faults(rows, served, "idea") == []
    wrong = [dict(rows[0]), dict(rows[1], chip="Solves", note=None), rows[2]]
    faults = ss.plan_chip_faults(wrong, served, "idea")
    assert [f["scene"] for f in faults] == ["2"]
    assert ss.plan_chip_faults([{"scene": "4", "status": "passed", "chip": None}],
                               [{"scene": 4, "chapter": "solves", "status": "passed"}], "idea") == []


def test_a_retired_chapter_is_a_drift_line_and_a_failed_build_a_fault_only_on_no_picture():
    view = {"build": {"state": "ready", "story": {"scenes": [{"line": "This time.", "chapter": "before"},
                                                             {"line": "It reads.", "chapter": "solves"},
                                                             {"line": "Calm.", "chapter": "joy", "joy": True}]},
                      "pictures": {"plan": [{"scene": 2, "chapter": "better", "line": "Better."}]}}}
    drift = ss.idea_chapter_drift(view)
    assert len(drift) == 2 and all(d["drift"] and "283 FR-1" in d["owed"] for d in drift)
    lost = ff.failed_build_fault({"build": {"state": "failed", "failedScene": 3, "failedReason": "No picture."}},
                                 "solution")
    assert "no picture could be drawn" in lost["what"] and not lost.get("drift")
    reader = ff.failed_build_fault({"build": {"state": "failed", "failedChapter": "brand"}}, "solution")
    assert reader["drift"] is True


def test_the_film_table_carries_frames_and_chapters():
    row = {"measures": {"frames": 12, "chapters": ["before", "task", "joy"]}}
    assert film_table.frames_chapters_line(row) == "- frames 12, chapters: before, task, joy"
    old = {"measures": {"frames": 14, "chapters": ["before", "task", "solves", "joy"]}}
    assert "retired by keel-cloud 283: solves" in film_table.frames_chapters_line(old)
    assert film_table.frames_chapters_line({}) == "- frames --, chapters: --"


# ------------------------------------------------------------------------------------------- FR-5 the recap cut

def _film() -> dict:
    marks_ = {1: "who", 2: "task", 3: "today", 4: "shortfall", 7: "cost"}
    scenes = [dict({"line": f"Line {n}."}, **({"chapter": marks_[n]} if n in marks_ else {}),
                   **({"pain": True} if n == 7 else {})) for n in range(1, 8)]
    return {"scenes": scenes, "askLine": "Is that how it goes for you?", "clipIds": [f"c{n}" for n in range(1, 9)],
            "readInstead": [s["line"] for s in scenes] + ["Is that how it goes for you?"]}


def test_the_recap_is_five_lines_on_a_solution_link_and_the_whole_film_on_a_problem_link():
    whole = _film()
    assert ss.recap_of(whole) == [1, 4, 5, 6, 7]
    kept = [whole["scenes"][n - 1] for n in (1, 4, 5, 6, 7)]
    recap = {"scenes": kept, "askLine": None, "clipIds": ["c1", "c4", "c5", "c6", "c7"],
             "readInstead": [s["line"] for s in kept]}
    v = ss.recap_verdict(recap, whole)
    assert v["ok"], v
    assert v["scenes"] == ss.RECAP_LINES == 5 and ss.WHOLE_LINES == 8
    served_whole = ss.recap_verdict(whole, whole)
    assert not served_whole["ok"] and not served_whole["parts"]["no ask line"]
    assert ss.recap_of({"scenes": [{"line": "x"}] * 7}) is None                         # no marks: served whole
    cloud = _java("application/SolutionLink.java")
    assert 'RECAP_CHAPTERS = Set.of("' + '", "'.join(ss.RECAP_CHAPTERS) + '")' in cloud


def test_the_cards_gate_passage_carries_the_recaps_lines():
    script = {"passages": [{"kind": "intro"}, {"kind": "gate", "lines": ["Line 1.", "Line 4.", "Line 5.", "Line 6.",
                                                                          "Line 7."]}]}
    assert sol.card_problem_lines(script) == ["Line 1.", "Line 4.", "Line 5.", "Line 6.", "Line 7."]
    assert sol.card_problem_lines({}) == []


# ------------------------------------------------------------------------------------------- FR-6 the short questions

def test_the_short_frames_are_keel_cloud_285s():
    frames = _java("domain/vectors/ItemFrames.java")
    if "FILM_FREQUENCY" not in frames:
        pytest.skip("keel-cloud 285 not in the keel-cloud checkout")
    assert f'FILM_FREQUENCY = "{ts.FREQUENCY_FILM}"' in frames and f'FILM_IMPORTANCE = "{ts.IMPORTANCE_FILM}"' in frames
    questions = _java("domain/vectors/SolutionQuestions.java")
    assert f'FILM_COMPATIBILITY = "{sol.COMPATIBILITY_FILM}"' in questions
    assert f'FILM_ADVANTAGE = "{sol.RELATIVE_ADVANTAGE_FILM}"' in questions
    assert f'FILM_NO_SETUP = "{sol.ADOPTION_NONE_FILM}"' in questions
    assert 'FILM_WITH_SETUP = "You would first need {the setup}."' in questions
    assert sol.ADOPTION_SETUP_FILM.startswith("You would first need {the setup}. ") \
        and sol.ADOPTION_SETUP_FILM.endswith('Could you start without much trouble?')
    assert f"FILM_MAX_WORDS = {sol.FILM_MAX_WORDS}" in questions and f'NO_NAME = "{sol.NO_NAME}"' in questions
    composer = _java("application/InterviewComposer.java")
    assert f'FRAMED_FILM = "{ts.FRAMED_FILM}"' in composer and f'FRAMED_CLAUSE = "{ts.FRAMED_CLAUSE}"' in composer
    rules = _java("application/RespondentQuestionsRules.java")
    assert f"SCREENER_MAX_WORDS = {ts.SCREENER_MAX_WORDS}" in rules
    for dimension, words in fake.FILM_FRAMES.items():
        assert words in (ts.FREQUENCY_FILM, ts.IMPORTANCE_FILM, sol.COMPATIBILITY_FILM, sol.RELATIVE_ADVANTAGE_FILM,
                         sol.ADOPTION_SETUP_FILM), dimension


def _item(dimension: str, question: str, framed: str | None, **kw) -> dict:
    out = {"itemId": dimension, "dimension": dimension, "question": question, "control": "yes_no", "escape": None,
           "options": [{"optionId": "y", "label": "Yes"}, {"optionId": "n", "label": "No"}], **kw}
    if framed:
        out["framed"] = framed
    return out


def test_the_problems_two_are_held_by_their_framed():
    film = {"parts": [{"items": [_item(ts.FREQUENCY, ts.FREQUENCY_FILM, "film"),
                                 _item(ts.IMPORTANCE, ts.IMPORTANCE_FILM, "film")]}]}
    assert ts.problem_question_faults(film) == []
    clause = {"parts": [{"items": [_item(ts.FREQUENCY, "When you check the payroll, how often does it happen?", "clause"),
                                   _item(ts.IMPORTANCE, "Of the things you do as a payroll lead, which would you most "
                                                        "like made easier?", None)]}]}
    assert ts.problem_question_faults(clause) == []                     # no `framed`: a cloud before 285, today's frames
    wrong = {"parts": [{"items": [_item(ts.FREQUENCY, "When you check the payroll, how often does it happen?", "film")]}]}
    assert ts.problem_question_faults(wrong)
    film_said_on_clause = {"parts": [{"items": [_item(ts.FREQUENCY, ts.FREQUENCY_FILM, "clause")]}]}
    assert ts.problem_question_faults(film_said_on_clause)
    long = dict(film, condition={"question": "Do you run the payroll for a small team every single week at work?"})
    assert any("screener" in f for f in ts.problem_question_faults(long))
    assert ts.screener_faults({"gate": {"condition": {"question": "Do you run payroll?"}}}) == []


def test_the_solutions_three_are_held_by_their_framed():
    name = "Runcheck"
    film = {"parts": [{"items": [
        _item(sol.COMPATIBILITY, sol.COMPATIBILITY_FILM, "film"),
        _item(sol.RELATIVE_ADVANTAGE, "Would Runcheck be better than how you do it today?", "film"),
        _item(sol.ADOPTION_FRICTION, "You would first need to connect the two hour systems. Could you start without "
                                     "much trouble?", "film")]}]}
    assert sol.question_faults(film, name=name, setup=["connect the two hour systems"]) == []
    none = {"parts": [{"items": [_item(sol.ADOPTION_FRICTION, "Could you start using Runcheck without much trouble?",
                                       "film")]}]}
    assert not [f for f in sol.question_faults(none, name=name, setup=[]) if sol.ADOPTION_FRICTION in f]
    clause = {"parts": [{"items": [_item(sol.COMPATIBILITY, "Would checking the payroll this way, with Runcheck, fit "
                                                            "into how you work?", "clause")]}]}
    assert not [f for f in sol.question_faults(clause, name=name, setup=[]) if sol.COMPATIBILITY in f]
    long = {"parts": [{"items": [_item(sol.COMPATIBILITY, "Would checking the payroll this way, with Runcheck, fit "
                                                          "into how you work?", "film")]}]}
    assert [f for f in sol.question_faults(long, name=name, setup=[]) if sol.COMPATIBILITY in f]
    assert fake.film_question(sol.RELATIVE_ADVANTAGE, "") == "Would this idea be better than how you do it today?"
    assert fake.film_question(sol.ADOPTION_FRICTION, "Runcheck") == "Could you start using Runcheck without much trouble?"
    assert fake.film_question("problem.prevalence") is None


def test_a_beat_in_two_parts_reads_the_one_ask_in_the_quiet(browser, tmp_path, monkeypatch):
    monkeypatch.setattr(ss, "TWO_PART_QUIET_S", 2.0)
    page = _beat_page(browser)
    try:
        walk = ss.StoryWalk(page, Recorder(tmp_path), BASE, patience=0.2)
        walk.listen()
        seen = walk.beat(1, "", two_part=("Payroll leads.", "In small teams."))
    finally:
        page.close()
    q = seen["two_part"]
    assert q["sent_in_the_quiet"] == 0 and q["still_on_the_beat"] and q["asks"] == 1 and q["waited"], q
    assert q["take_your_time"] and q["joined"] and seen["closed"]["by"] == "the done word after the card"


def test_the_strangers_telling_is_kept_and_a_story_closed_on_the_pause_is_a_capture_fault():
    from harness import film_strangers as fs                                       # noqa: PLC0415
    told = {"parts": ["We waited.", "Nobody knew why. That's it."], "open_across": True, "asked": False,
            "ack": ivs.LONG_GOT_IT, "ack_kind": "gotIt", "held": False}
    walked = {"rows": [{"screen": "question", "step": "story", "story": "said", "said": "We waited. Nobody knew why.",
                        "told": told}], "done": True}
    plan = {"person": "Ada", "screener": "yes", "gate": True}
    summary = fs.walk_summary(plan, {"invitationId": "i1", "url": "u"}, walked)
    assert summary["told"] == told and summary["story"] == "We waited. Nobody knew why."
    assert fs.told_faults([summary]) == []
    closed = dict(summary, told=dict(told, open_across=False, ack=None))
    faults = fs.told_faults([closed])
    assert len(faults) == 1 and "274" in faults[0]["owed"]
