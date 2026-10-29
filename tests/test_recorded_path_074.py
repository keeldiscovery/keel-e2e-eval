"""Spec 074 FR-1 / FR-2 (keel-web 115 + 116 + 117 + 119, keel-cloud 136): the harness follows one recorded path.

FR-1: the AI walks drive the recorder (`harness/interviewer_screens.SPEECH_SEAM`, keel-web 115 FR-5's fake restated --
its parity with keel-web's fixture is `tests/test_interviewer_screens.py`'s); every read the page sends is kept with the
words its recording carried; the recogniser, `ear()` and the `not-allowed` leg are gone. Keel-web 117: the occasion is
read off the card's *I'll ask about* line through *Change*. Keel-web 119: Send more's AI row carries a link, so the walk
picks a row by its name.

FR-2: the marks re-pinned (IM9, IM19, IM21, IM25 -- `INTERVIEWER_MARKS_VERSION` 9), the *Microphone off* fact read once
the done screen shows it with the release after the thank-you's end (keel-web 116 FR-1), and the pilot ask after *End*
recording on the kept stream (116 FR-2).
"""

from __future__ import annotations

import base64
import contextlib
import copy
import inspect
from types import SimpleNamespace

import pytest
from playwright.sync_api import sync_playwright

from evals import corpus_scenario as cs
from evals import interviewer_leg as leg
from evals import interviewer_marks as marks
from harness import interviewer_screens as ivs
from harness import interviews_screens as iv
from harness import vectors_screens as vs_screens
from instructions import corpus as corpus_mod
from instructions import marks as instruction_marks
from stack.config import REPO_ROOT

from tests.test_interviewer_marks import good


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


# ------------------------------------------------------------------------------------------ FR-1: the recorder

def test_the_recogniser_and_its_leg_are_gone_from_the_harness():
    seams = ivs.SPEECH_SEAM + ivs.text_seam() + ivs.text_seam(refused=True) + ivs.follow_up_cap_seam(9000)
    for gone in ("__speechError", "__speechEnd", "__recognisers", "__speechStarts", "Recognition", "onresult"):
        assert gone not in seams, gone
    walk = (REPO_ROOT / "evals" / "interviewer_leg.py").read_text(encoding="utf-8")
    for gone in ("__speechError(", ".ear()", "wait_ear(", "recorder_seam(", "self.recorded"):
        assert gone not in walk, gone
    assert not hasattr(ivs, "RECORDER_SEAM") and not hasattr(ivs, "recorder_seam")
    assert not hasattr(ivs.Player, "ear") and not hasattr(ivs.Player, "wait_ear")
    assert ivs.INTRO_TRANSCRIBED == "Keel's transcription provider writes your answer down and keeps nothing."


def test_the_text_box_seam_records_the_zeros_alone():
    """The text page's box is driven by a level (`SpeakBox.speak`), never `__say`, so its recording is 20 KiB of zeros:
    keel-cloud 136's fake hears none of it as text and answers its `otherwise` -- `FAKE_TRANSCRIPT` on the stack, as
    before (the old seam's 4 KiB of *a spoken answer* would be text to 136's fake)."""
    seam = ivs.text_seam()
    assert "a spoken answer" not in seam and "a spoken answer" not in ivs.SPEECH_SEAM
    assert "window.__keelSpeech = { recorder, mic: mic(() => window.__levelNow, false), earcons: false };" in seam


def test_decode_said_trims_the_padding_as_the_fake_transcriber_does():
    padded = "the second one".encode() + bytes(20 * 1024 - 14)
    assert ivs.decode_said(base64.b64encode(padded).decode()) == "the second one"
    assert ivs.decode_said(base64.b64encode(bytes(20 * 1024)).decode()) == ""
    assert ivs.decode_said(None) == "" and ivs.decode_said("%%%") == ""


class _Request:
    def __init__(self, url: str, body: dict, method: str = "POST"):
        self.url, self.method, self.post_data_json = url, method, body


def test_every_read_is_kept_with_the_words_its_recording_carried():
    player = ivs.Player.__new__(ivs.Player)
    player.requests, player.classified = [], []
    audio = base64.b64encode("about four".encode() + bytes(20 * 1024 - 10)).decode()
    player._keep(_Request("http://x/v2/i/t/interview/answer", {"itemId": "a", "audio": audio, "mimeType": "audio/webm"}))
    player._keep(_Request("http://x/v2/projects/p/interviewer/answer", {"itemId": "b", "audio": audio}))
    player._keep(_Request("http://x/v2/i/t/interview/transcribe", {"itemId": "g", "audio": audio}))
    player._keep(_Request("http://x/v2/i/t/interview/classify", {"itemId": "c", "heard": "yes"}))
    bodies = [c["body"] for c in player.classified]
    assert [b["itemId"] for b in bodies] == ["a", "b", "c"]                   # a story's transcribe is no read
    assert bodies[0]["heard"] == bodies[1]["heard"] == "about four" and "audio" not in bodies[0]
    assert bodies[0]["audio_bytes"] == 20 * 1024 and bodies[2] == {"itemId": "c", "heard": "yes"}


class _Page:
    """`Player.recorder()`'s evaluate, answered from a script of states."""

    def __init__(self, states: list[dict]):
        self.states = states
        self.waited = 0

    def evaluate(self, _js, *_):
        return self.states[0] if len(self.states) == 1 else self.states.pop(0)

    def wait_for_timeout(self, ms):
        self.waited += ms


def test_wait_listening_waits_for_a_window_recording_newer_than_asked():
    player = ivs.Player.__new__(ivs.Player)
    player.patience = 1.0
    player.page = _Page([{"count": 3, "live": False, "released": 1}, {"count": 3, "live": True, "released": 1},
                         {"count": 4, "live": True, "released": 1}])
    assert player.wait_listening(newer_than=3) == {"count": 4, "live": True, "released": 1}
    player.page = _Page([{"count": 2, "live": False, "released": 0}])
    player.phase = player.status = lambda: None
    with pytest.raises(AssertionError):
        player.wait_listening(timeout_s=0.3)


def test_a_veto_is_said_as_a_final():
    """Keel-web 115: the hold records too; an interim keeps the level up and the recording open, so the word of
    protest is a final."""
    assert inspect.signature(ivs.Player.veto).parameters["final"].default is True


def test_the_walk_says_recorded_for_every_spoken_answer():
    assert leg.SPOKEN_HOW == marks.SPOKEN_HOW == "RECORDED"
    walk = inspect.getsource(leg._Walk)
    assert '"SPOKEN"' not in walk and "SPOKEN_HOW" in walk


# ------------------------------------------------------------------------- FR-1: keel-web 117, the occasion

_LINE_CARD = """<div data-testid="context-step" data-context-state="card"><div class="understands">
  <p class="understands__big">You want to hear from managers.</p>
  <div class="understands__reach"><p class="understands__line"><span data-testid="context-ask-about">I'll ask about: the
  last time you ran payroll.</span> <button type="button" class="ochange" data-testid="context-occasion-change">Change
  </button></p></div>
  <div class="actions cbtns"><button class="btn primary">Yes, that's it</button><button class="btn">Edit</button></div>
</div></div>
<script>
  const reach = document.querySelector('.understands__reach');
  const line = reach.innerHTML;
  const open = () => {
    reach.innerHTML = '<div class="understands__occasion" data-testid="context-occasion"><span class="cfield__tag">' +
      'OCCASION</span><label class="cfield__q" for="context-occasion">What is one time of it called?</label>' +
      '<input id="context-occasion" class="cfield__input cfield__input--line" value="payroll run">' +
      '<span class="cfield__hint" id="context-occasion-hint">One to eight words.</span></div>';
    const input = document.getElementById('context-occasion');
    input.focus();
    input.addEventListener('keydown', (e) => { if (e.key === 'Escape') { reach.innerHTML = line; wire(); } });
  };
  const wire = () => document.querySelector('[data-testid=context-occasion-change]').addEventListener('click', open);
  wire();
</script>"""


def _corridor(page) -> vs_screens.Corridor:
    corridor = vs_screens.Corridor.__new__(vs_screens.Corridor)
    corridor.page, corridor.saves = page, []
    return corridor


def test_the_occasion_is_read_through_change_and_the_line_put_back(browser):
    page = browser.new_page()
    try:
        page.set_content(_LINE_CARD)
        drawn = _corridor(page).context_occasion()
        assert drawn["drawn"] is True and drawn["value"] == "payroll run" and drawn["change"] == "Change"
        assert drawn["focused"] is True and drawn["line_while_open"] == 0 and drawn["line_back"] is True
        assert drawn["block"] == 0 and drawn["primary"] == vs_screens.CONTEXT_YES
        assert drawn["line"].startswith("I'll ask about:")
        assert page.get_by_test_id("context-occasion").count() == 0              # nothing left open
        assert cs.occasion_faults(drawn, "payroll run") == []
    finally:
        page.close()


@pytest.mark.parametrize("fault", [
    {"value": "payroll"},                                                     # not Keel's noun
    {"block": 1},                                                             # the block under the card is back
    {"change": "Edit"},                                                       # the line's link is not *Change*
    {"line_back": False},                                                     # Esc left the field open
    {"line_while_open": 1},                                                   # the field beside the line
    {"focused": False},
    {"primary": "Save and continue"},                                         # the change was kept
    {"drawn": False},
])
def test_an_occasion_off_the_card_is_a_fault(fault):
    good_read = {"drawn": True, "value": "payroll run", "change": "Change", "line": "I'll ask about: x.",
                 "line_back": True, "line_while_open": 0, "focused": True, "block": 0,
                 "primary": vs_screens.CONTEXT_YES}
    assert cs.occasion_faults({**good_read, **fault}, "payroll run")


def test_edits_form_owes_no_occasion_block():
    source = inspect.getsource(cs.context_reopened)
    assert 'assert edited.get("occasion") is None' in source


# ----------------------------------------------------------------------- FR-1: keel-web 119, Send more's AI row

def test_a_send_more_row_is_picked_by_its_name_not_its_middle():
    """Keel-web 119 FR-2 puts *Hear it* inside the AI interviewer's radio (its press opens the popup and does not choose
    the row), so the walk clicks the row's name."""
    source = inspect.getsource(iv.Interviews._step_one)
    assert 'radio.first.locator(".fmt__name").first.click()' in source


# --------------------------------------------------------------------------------------- FR-2: the marks, v9

def _check(record, mark):
    return {c.mark: c for c in marks.score(record)}[mark]


def test_the_version_moves_for_the_re_pins_alone():
    # spec 075 moved it to 10 (IM23-IM25 re-pinned to keel-web 124's order), then 11 (FR-5: IM23, IM26, IM27); 074's
    # own re-pins are still read as 9's; spec 076 FR-5 to 12 (IM22, IM23: a story chip ends the interview)
    assert marks.INTERVIEWER_MARKS_VERSION == 14      # spec 086 FR-5 (keel-cloud 154): IM27; 089 FR-3: IM20
    assert instruction_marks.MARKS_VERSION == 21 and corpus_mod.REVISION == 19       # spec 078: `read`, v21; spec 080: r17; 086: r18; 089: r19


def test_im9_reads_recorded_as_spoken_and_spoken_as_retired():
    record = good()
    assert _check(record, "IM9").ok
    record["ai_answers"]["body"]["answers"][0]["how"] = "SPOKEN"
    check = _check(record, "IM9")
    assert not check.ok and check.detail["said SPOKEN"] == ["a"]


def test_im19_the_first_words_leave_the_window_recording():
    record = good()
    assert _check(record, "IM19").ok
    after = record["hear_out"]["after_first"]["after"]
    after["status"] = marks.HEARING                                           # the retired browser path's words
    assert not _check(record, "IM19").ok
    record = good()
    record["hear_out"]["after_first"]["after"]["heard"] = "Would Agency have made things better for you hearing"
    assert not _check(record, "IM19").ok                                       # words shown before written down


def test_im21_reads_recordings_alone():
    record = good()
    for b in record["beat"]["beats"]:
        b["starts_in"] = 3                                                    # a recogniser count is no longer read
    assert _check(record, "IM21").ok
    record["beat"]["beats"][0]["recordings_in"] = 1
    assert not _check(record, "IM21").ok


def _short_windows() -> list[dict]:
    heard = {"route": "transcribe", "status": 200, "sent": {"itemId": "fu", "maxSeconds": 120}, "body": {"text": "x"}}
    return [{"path": "recorded", "ended": "quiet", "quiet_to_stop_ms": 4_080, "pressed": False, "presses": [],
             "transcribed": [heard]},
            {"path": "recorded", "ended": "save", "pressed": True, "final_to_held_ms": 380,
             "presses": [{"testid": "ai-save"}], "transcribed": [heard]}]


def test_im25_the_short_form_owes_the_pause_and_save_both_written_down():
    record = good()
    record["follow_up_windows"] = {"windows": _short_windows(), "full": False, "page_cap_ms": 120_000}
    assert _check(record, "IM25").ok, _check(record, "IM25").detail
    for fault in ({"transcribed": []}, {"presses": [{"testid": "ai-save"}, {"testid": "ai-next"}]},
                  {"path": "browser"}):
        bad = copy.deepcopy(record)
        bad["follow_up_windows"]["windows"][1].update(fault)
        assert not _check(bad, "IM25").ok, fault
    bad = copy.deepcopy(record)
    bad["follow_up_windows"]["windows"] = bad["follow_up_windows"]["windows"][:1]          # Save never walked
    assert not _check(bad, "IM25").ok
    bad = copy.deepcopy(record)
    bad["follow_up_windows"]["windows"][0]["pressed"] = True                  # the pause pressed something
    assert not _check(bad, "IM25").ok


def test_im25_the_full_leg_still_owes_the_pause_and_the_cap():
    record = good()
    assert _check(record, "IM25").ok
    record["follow_up_windows"]["windows"] = _short_windows()                 # no cap on the full leg
    assert not _check(record, "IM25").ok


# ----------------------------------------------------- FR-2: keel-web 116, the release after the last clip

class _Steps:
    def __init__(self):
        self.asserted: list = []

    def step(self, name, **_):
        @contextlib.contextmanager
        def cm():
            yield SimpleNamespace(record_assert=lambda want, got: self.asserted.append((name, want, got)))
        return cm()


THANKS = {"interviewer": {"clips": {"thanks": {"clipId": "t-1"}}}}
SHOWN = {"shown": True, "text": ivs.MIC_OFF, "role": "status", "listening": False, "released": 2}


def _j():
    return SimpleNamespace(recorder=_Steps())


def _events(played=100.0, ended=4_100.0):
    out = [{"kind": "play", "clip": "t-1", "t": played}]
    return out + ([{"kind": "ended", "clip": "t-1", "t": ended}] if ended is not None else [])


def test_the_microphone_is_let_go_when_the_thanks_ends():
    # StrictMode's release at load (keel-web 116 D-03), then the thanks' at its end
    leg._mic_off_after_thanks(_j(), THANKS, SHOWN, {"record": [50.0], "released": [5.0, 4_120.0]}, _events(), "x")


@pytest.mark.parametrize("starts, events", [
    ({"record": [50.0], "released": [5.0, 1_200.0]}, _events()),               # let go while the thanks played
    ({"record": [50.0], "released": [5.0]}, _events()),                        # never let go after it
    ({"record": [50.0], "released": [5.0, 4_120.0]}, _events(ended=None)),     # the thanks never ended
    ({"record": [50.0, 900.0], "released": [5.0, 4_120.0]}, _events()),        # a recording begun in the thanks
])
def test_a_release_before_the_thanks_ends_fails(starts, events):
    with pytest.raises(AssertionError):
        leg._mic_off_after_thanks(_j(), THANKS, SHOWN, starts, events, "x")


def test_the_pilot_ask_after_end_records_on_the_kept_stream():
    ended = {"pressed_at": 1_000.0, "starts_before": 9, "starts_after": 10, "released_before": 1,
             "released_after": 1, "listening": True, "where": ivs.LAST_QUESTION}
    leg._pilot_after_end(_j(), ended, {"released": [5.0, 9_000.0]})
    for fault in ({"starts_after": 9}, {"released_after": 2}, {"listening": False}, {"where": "Question 9 of 9"}):
        with pytest.raises(AssertionError):
            leg._pilot_after_end(_j(), {**ended, **fault}, {"released": [5.0, 9_000.0]})


def test_only_the_short_form_presses_end_before_the_pilot_ask():
    source = inspect.getsource(leg._Walk.follow_up)
    # spec 075: End in the hold of the second follow-up asked on the spot (the last item's), on the said walk alone
    assert 'self._said_take(line, "quiet", end_in_hold=by == "said", step_after=True)' in source
    assert 'self._silent_window(second)' in source
    assert 'by = "said" if record.get("short") else "sound"' in inspect.getsource(leg._answer_ai_on_screen)


def test_a_card_with_no_stem_draws_the_occasion_nowhere():
    """Keel-web 117 J-4: no served stem (the scripted executor's plain noun), no *I'll ask about* line -- so no
    *Change*, no field and no block; the noun is held on the confirmed view instead."""
    nothing = {"drawn": False, "value": None, "change": None, "block": 0}
    assert cs.occasion_faults(nothing, "delivery", line=None) == []
    assert cs.occasion_faults({**nothing, "block": 1}, "delivery", line=None)
    assert cs.occasion_faults({**nothing, "change": "Change"}, "delivery", line=None)
    assert cs.occasion_faults(nothing, "delivery", line="I'll ask about: the last delivery.")
    assert 'noun == vs.occasion(j.entry)' in inspect.getsource(cs)
