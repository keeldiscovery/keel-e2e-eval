"""keel-web 069's AI interviewer, as page objects (spec 044 T003; keel-web master `d23895f`), and keel-web 072's answer
path (spec 048 T003, contract 18: no *That's my answer*, the three tiers, the hold, Back, Test your mic).

Machinery, not judgement: every class here acts and reads, and asserts nothing -- `evals/interviewer_leg.py` judges.
The words are copied from keel-web `src/lib/translate.ts`; the selectors are the ones 069's tasks.md names for this
repository (*Selectors (for keel-e2e-eval 044)*) and 072's spec names (`ai-yes`, `ai-back`, `ai-mic-test`,
`ai-mic-heard`, `start-talking`).

* `Persona`   -- Sent's persona line (`[data-testid=persona-line]`, `data-state`), its progress bar, *Change who asks* /
                 *Record the interviewer* and the popup (`[data-testid=change-face-popup]`, the carousel,
                 `[data-testid=change-face-confirm]`), the role cards' *Try it yourself*, Send more's format row read
                 and cancelled, L1 revisited; since keel-web 088 the band's *Hear <name>* (`persona-hear`) and the
                 absence of *How it works* (the replay of W1 is gone, spec 059).
* `Player`    -- the AI interviewer's page for a stranger or the founder's dry run: the intros (072: *Test your mic*),
                 the stage (`data-phase`, the one `<video>`, the pills, End, the ship mark), the sheet (options, field,
                 escape, preview, heard, status, Back, *Yes, that's it*, *Save and next* for typed words, *Finish* on
                 the pilot, *Type instead*) and the end screens. 072: an utterance ends on a final result (the seam's
                 recogniser then ends, as Chrome's does); the cloud's classifier decides (`classify`); a confident read
                 is **held** two seconds and the interview goes on by itself (`hold`), a word of protest reopens it
                 (`veto`), an unsure one asks "Is that right?" (`yes`), and *Back* reopens the last question (`back`).
* `SPEECH_SEAM` -- the init script that stands in for the browser's recogniser and microphone through the test build's
                 own seam (`window.__keelSpeech`, present only under `vite --mode test`, which the stack serves): keel-web's
                 own `tests/fixtures/interviewer/fakeSpeech.ts`, restated in JavaScript. `__say(text, final)` is the
                 stranger speaking; a final is followed by the recogniser's end. No microphone is opened. **No `classify`
                 is put on the seam** (spec 048 judgement call 1): the page calls the real route, and the stack's
                 keel-cloud answers it with its `FakeClassifier` -- what staging runs for eval founders too.

Spec 049 (keel-web 073, *hear them out*): nothing lights or fills while they speak, and an utterance is read
`QUIET_MS` (1.5 s) after the recogniser's end after a final -- the page restarts the recogniser for that gap, so a
final said within it joins the same utterance. `say()` keeps what the sheet showed while the words were heard
(`hearing`: nothing newly lit, the field and the preview untouched); `ear()` counts a recogniser as listening only while
the page still hands it results (keel-web's `__listening()`, 073 D-04: recogniser counts now grow on every final's end);
tapped checkboxes wait for *Save and next* (`save_state`); the earcons are switched off on the seam (073 FR-8).

Spec 050 (keel-web 074 + 075): the gap is 4.0 s on every window (the walk still encodes none); the story says how to
end it (`STORY`) and its *Save and next* reads it at once; a yes to *Is that right?* is held (`data-unsure="false"`,
`ai-ring`); the live waveform `ai-mic-on` while a window listens; after the problem and the idea passages a 2.0 s
**beat** (`data-phase="beat"`, the status *Take a moment.*, the pill *pause*, nothing listening) -- the timeline keeps
each beat as it was drawn and the seam stamps every recogniser started, so the leg can say nothing listened in it;
*Microphone off* (`ai-mic-off`) on the end screens once everything is released.

Spec 051 (keel-web 076, contract 19): the one follow-up -- on the AI page the sheet's `data-step="followUp"`, the
`ai-where` pill *One last thing*, the story's window, `ai-skip`; on the text page `SpeakOrTypeBox` (`.sot[data-state]`,
the `iv-mic` pill, the listening card `iv-listening` with `ai-mic-on`, `iv-mic-clock`, `iv-mic-cancel`, `iv-mic-done`)
driven through `text_seam` (a microphone that counts its acquisitions, refused on request, and a recorder whose level
the walk sets) -- `SpeakBox` reads and drives it. `RECORDER_SEAM` adds the same recorder to the AI page's seam, so a
browser that refuses its recogniser (`not-allowed`, Chrome on iPhone) records the window instead.

Spec 058 (keel-web 087, contract 23): **tap to hear** -- a tap on an unpicked card of the carousel picks it and plays
her hello in a `video` inside the card (`face-hear`, the play glyph on each unpicked card), and the respondent's intro
plays it under *Hear <name>* (`intro-hear`). `HEAR_JS` listens for every `video`'s media events on the document (they do
not bubble; a capture listener hears them) and polls the choice buttons while it plays; `hear_card` / `Player.hear`
tap, wait for the clip's `ended` and the still's return, and return what was heard, for IM28 / IM29 to judge.

Spec 059 (keel-web 088, contract 24): Sent's persona line is the **who-asks band** (`.ivband`): READY draws *Hear
<name> · 5 s* (`persona-hear`, the name, never a pronoun; absent for a retired face), which plays the 087 hello in the
band's circle (`video.pface-hello__clip`) while the band carries `data-hearing`; `HEAR_JS` tags an event inside the band
`band`, and `Persona.hear_band` taps it and waits for the end. *How it works* is gone from Sent (the page's pill replaced
it), so `walkthrough_again` retired with it -- `how_it_works()` counts the controls of that name (none). `Persona.sent`
opens Sent through `interviews_screens.pass_interviews_sheet`, which skips 088's first-open sheet when drawn.

Every write a press makes returns the response keel-web received, so the leg holds the wire the page was handed.
"""

from __future__ import annotations

import re

from playwright.sync_api import Page

from harness import interviews_screens as _iv
from harness.browser import _BrowserStep, _safe_text

# ---- keel-web d23895f `translate.ts`
PERSONA_RECORDING = "Recording now, usually ready in about five minutes. You can leave this page."
PERSONA_NOT_RECORDED = "No interviewer recorded yet."
TRY_IT_YOURSELF = "Try it yourself"
TRY_IT_YOURSELF_RECORDING = "Try it yourself · recording"
TRY_NOTHING_STORED = "Nothing was stored."
SEND_TEXT_ONLY_LINKS = "Send text-only links"
SEND_LINKS = "Send links"
SEND_FORMAT_RECORDED = "The interviewer is already recorded for this project."
SEND_FORMAT_RECORDING = "The interviewer is still recording; Text only is ready now."
CHANGE_FACE_TITLE = "Change who asks"
RECORD_FACE_TITLE = "Record the interviewer"
#: keel-web 068's replay of W1 on Sent's header, gone with keel-web 088 FR-1 (spec 059): never on Sent again.
HOW_IT_WORKS = "How it works"
WALKTHROUGH_GOT_IT = "Got it"
MARK = "Keel · AI interviewer"
MARK_TRY = "Keel · AI interviewer · try run"
LAST_QUESTION = "Last question"
#: keel-web 070's press after an answer, gone with keel-web 072 FR-5: never in the DOM again.
THATS_MY_ANSWER = "That’s my answer"
FINISH = "Finish"
#: keel-web 070 F1 / 072 FR-5: typed words keep an explicit press.
SAVE_AND_NEXT = "Save and next"
# ---- keel-web 072 `translate.ts` (spec 072 FR-7, FR-9)
START_THE_INTERVIEW = "Start the interview"
MIC_TEST = "Test your mic"
SAY_HELLO = "Say hello"
MIC_FALLBACK = "You can tap or type your answers instead"
INTRO_TRANSCRIBED = ("Where your browser can't listen, Keel's transcription provider writes your answer down and keeps "
                     "nothing.")
GOT_THAT = "Got that…"
WRITING_DOWN = "Writing it down…"
HELD = "Got it. Moving on… say no to change"
#: keel-web 073 FR-3: the status through the quiet gap (`AI_STATUS.heard`), and a tap's or a Save's 500 ms advance
#: (`AI_STATUS.answered`); the heard line's tags (`AI_TAG_HEARING`, `AI_TAG_NOT_TAKEN`).
HEARING = "Listening. Pause when you’re done."
ANSWERED = "Got it."
TAG_HEARING = "hearing"
TAG_NOT_TAKEN = "not taken"
#: keel-web 073 FR-2 `QUIET_MS` (`src/lib/answerPath.ts`): the gap after a final before the utterance is read -- 1.5 s
#: at 073, 4.0 s on every window from keel-web 074 (the founder's decision, 2026-10-16), and two gaps from keel-web 082
#: (D36): the option questions (yes/no, number, list, amount or hours, the pilot ask, the confirmations) close after
#: `QUIET_OPTION_MS` 2.0 s, free text (the story, the follow-up, the speak-or-type box) after `QUIET_FREE_MS` 4.0 s.
#: The seam: `quietMs` is the option gap, `quietFreeMs` the free one (absent -> `quietMs`). The walk encodes neither:
#: it waits for the held / unsure status or the next question, with timeouts that tolerate the longest gap here plus
#: the 2.0 s hold (spec 049 judgement call 6). The one fixed wait is IM20's: a tapped tick must not go on by itself.
QUIET_OPTION_MS = 2_000
QUIET_FREE_MS = 4_000
GAP_TOLERATED_MS = max(QUIET_OPTION_MS, QUIET_FREE_MS)
TAP_WAIT_MS = 1_500
IS_THAT_RIGHT = "Is that right? Say yes, or tell me the right one"
YES_THATS_IT = "Yes, that’s it"
#: The words a stranger says for each move (design §3-§4).
#: keel-web 074 FR-2 (`AI_STATUS.story`): the story's window says how to end it.
STORY = "Take your time. Pause for a few seconds when you’re done, or tap Save."
#: keel-web 075 FR-1: the beat after the PROBLEM and SOLUTION passage clips (`BEAT_MS`, `AI_STATUS.beat`, the pill's
#: `AI_STATE.beat`); the seam's `beatMs` is left at the page's default on the stack (spec 050 judgement call 3).
BEAT = "Take a moment."
BEAT_PILL = "pause"
BEAT_MS = 2_000
#: keel-web 075 FR-4 (`AI_STATUS.micOff`): the end screens once every holder of the microphone has let go.
MIC_OFF = "Microphone off"
VETO = "no"
SAY_YES = "yes"
GO_BACK = "go back"
#: keel-web 076 `translate.ts` (spec 051): the follow-up and the speak-or-type box, restated where the walks read them.
FOLLOW_UP_KICKER = "One last thing"
FOLLOW_UP_NOTE = "In your own words. A sentence or two is plenty."
FOLLOW_UP_SKIP = "Skip this one"
FOLLOW_UP_HINT = "The only extra question."
SPEAK_HINT_STORY = "A few lines is plenty."
SPEAK_OR_TYPE_PLACEHOLDER = "Type here, or tap the mic and just talk."
SPEAK_TYPE_PLACEHOLDER = "Type here."
SPEAK_LABEL = "Speak"
SPEAK_ADD_MORE = "Add more"
SPEAK_LISTENING = "Listening. Take your time."
SPEAK_LISTENING_NOTE = "Pause for a few seconds when you’re done, or tap Done."
SPEAK_HEARD = "Heard you. Fix anything that’s wrong."
#: keel-web 082 FR-3 (D35, `HEARING_YOU`): the recorded path's status once a sound came in -- the AI sheet's heard line
#: (`ai-heard`) and the box's listening card (`iv-mic-say`); *Nothing heard yet* only while nothing has.
HEARING_YOU = "Hearing you…"
SPEAK_MIC_OFF = "The microphone is off, so it’s typing on this one."
#: keel-web 076: the box's two caps as the clock says them (`clockOf(capMs)`): the story's minute, the follow-up's two.
STORY_CAP = "1:00"
FOLLOW_UP_CAP = "2:00"
#: keel-web `answerPath.ts`: the recorded path's quiet after the last sound -- 4.0 s on every window from 074, by window
#: kind from 082 (D36: `SILENCE_OPTION_MS` 2.0 s, `SILENCE_FREE_MS` 4.0 s; the seam's `silenceMs` overrides both) --
#: and the follow-up's cap (`FOLLOW_UP_RECORD_CAP_MS`, two minutes) -- held to the source by a unit test. The walks
#: measure only free-text windows on the recorded path (the story's box, the follow-up), so they read the free one.
SILENCE_OPTION_MS = 2_000
SILENCE_FREE_MS = 4_000
FOLLOW_UP_RECORD_CAP_MS = 120_000
#: Spec 051 judgement call 2: the AI follow-up's silent window is shortened through the seam (`followUpCapMs`); the
#: real two minutes are held on the wire (`maxSeconds: 120`) and in keel-web's source.
FOLLOW_UP_SEAM_CAP_MS = 9_000
#: A level the recorder hears as a sound (`LEVEL_THRESHOLD` is 0.02) and how long the walk speaks for.
SOUND = 0.3
SPEAK_MS = 1_200


def mic_heard(text: str) -> str:
    return f"Heard: {text}"


def back_to(question: int) -> str:
    return f"‹ Back to question {question}"

#: Spec 046 FM5: the stage's timeline, kept by the page itself from before the app runs -- every `data-phase` the stage
#: takes (`performance.now()`), every `play` of a clip on the stage's `<video>`, and every press of `ai-next` with the
#: words it carried. `window.__keelFlow()` hands it back. Spec 048 (keel-web 072): every change of the sheet's status
#: words (`ai-status`) in order, `window.__keelPhases()`; every press of a button on the sheet with its words; and
#: whether *That's my answer* (`ai-answer`) was ever in the DOM, `window.__keelSawAnswer()`.
FLOW_TIMELINE = r"""
(() => {
  const events = [];
  const statuses = [];
  let phase = null;
  let status = null;
  let sawAnswer = false;
  const beats = [];
  let beat = null;
  let lastClip = null;
  const read = () => {
    const stage = document.querySelector('[data-testid=ai-stage]');
    const now = stage ? stage.getAttribute('data-phase') : null;
    if (now !== phase) {
      const t = performance.now();
      if (beat && phase === 'beat') { beat.t1 = t; beat.next = now; beat = null; }
      phase = now; events.push({ t, kind: 'phase', value: now });
      if (now === 'beat') {
        beat = { t0: t, t1: null, next: null, after: lastClip, statuses: [], pills: [], micOn: false,
                 question: false, options: false, buttons: [] };
        beats.push(beat);
      }
    }
    const line = document.querySelector('[data-testid=ai-status]');
    const words = line ? (line.textContent || '').trim() : null;
    if (beat) {
      // spec 050 (keel-web 075 FR-1): what the beat drew, every time the page changed while it lasted
      const pill = document.querySelector('[data-testid=ai-state]');
      const pillWords = pill ? (pill.textContent || '').trim() : null;
      if (words !== null && beat.statuses[beat.statuses.length - 1] !== words) beat.statuses.push(words);
      if (pillWords !== null && beat.pills[beat.pills.length - 1] !== pillWords) beat.pills.push(pillWords);
      if (document.querySelector('[data-testid=ai-mic-on]')) beat.micOn = true;
      if (document.querySelector('[data-testid=ai-sheet] .iv-q')) beat.question = true;
      if (document.querySelector('[data-testid=ai-options]')) beat.options = true;
      for (const b of document.querySelectorAll('[data-testid=ai-sheet] button')) {
        const id = b.getAttribute('data-testid') || (b.textContent || '').trim();
        if (!beat.buttons.includes(id)) beat.buttons.push(id);
      }
    }
    if (words && words !== status) {
      status = words;
      const q = document.querySelector('[data-testid=ai-sheet] .iv-q');
      statuses.push({ t: performance.now(), status: words, question: q ? (q.textContent || '').trim() : null });
    }
    if (!sawAnswer && document.querySelector('[data-testid=ai-answer]')) sawAnswer = true;
  };
  new MutationObserver(read).observe(document, { subtree: true, childList: true, attributes: true,
                                                 characterData: true });
  document.addEventListener('play', (e) => {
    const v = e.target;
    if (v && v.tagName === 'VIDEO') {
      lastClip = v.getAttribute('data-clip');
      events.push({ t: performance.now(), kind: 'play', clip: lastClip });
    }
  }, true);
  document.addEventListener('click', (e) => {
    const b = e.target && e.target.closest ? e.target.closest('[data-testid=ai-next]') : null;
    if (b) events.push({ t: performance.now(), kind: 'next', value: (b.textContent || '').trim() });
    const any = e.target && e.target.closest ? e.target.closest('[data-testid=ai-sheet] button, [data-testid=ai-sheet] .opt') : null;
    if (any) events.push({ t: performance.now(), kind: 'press', testid: any.getAttribute('data-testid'),
                           value: (any.textContent || '').trim() });
  }, true);
  window.__keelFlow = () => events.slice();
  window.__keelPhases = () => statuses.slice();
  window.__keelSawAnswer = () => sawAnswer;
  window.__keelBeats = () => beats.map((b) => Object.assign({}, b));
})();
"""


def persona_asks(face: str) -> str:
    return f"{face} asks your questions."


def persona_progress(done: int, total: int) -> str:
    return f"{done} of {total} clips done"


def change_who_asks(credits: int) -> str:
    return f"Change who asks · {credits:,} AI credits"


def pick_who_asks(credits: int) -> str:
    return f"Record the interviewer · {credits:,} AI credits"


def walkthrough_asks_title(face: str) -> str:
    return f"{face} asks your questions"


def ai_intro_heading(face: str, questions: int) -> str:
    """keel-web `aiIntroHeading` (since 109, keel-cloud 133 FR-9: *1 question* for one)."""
    return f"{face} will ask you {questions} question{'' if questions == 1 else 's'}."


#: keel-web `tests/fixtures/interviewer/fakeSpeech.ts` `installFakeSpeech`, in JavaScript (an init script runs before
#: the app does; the app reads the seam only in a test-mode build). Spec 048 (keel-web 072): a final result is followed
#: by the recogniser's end, so a final said is an utterance ended and the page reads it; `mic` is a microphone that is
#: always granted with a steady level, so *Test your mic* is driven by `__say("hello", true)`. Unlike keel-web's own
#: fixture it puts **no `classify`** on the seam: the route is left real (judgement call 1). Spec 049 (keel-web 073):
#: the page reads the utterance 1.5 s after that end and restarts the recogniser meanwhile, so `__say` within the gap
#: goes to the gap's own recogniser; `__listening()` is keel-web's (the newest started and still handed results);
#: `earcons: false` silences the two tones (073 FR-8; the fake mic has no AudioContext, so nothing waits on them).
#: Spec 050: every `start()` is stamped (`__speechStarts`, `performance.now()`), and so is every `MediaRecorder.start`
#: (`__recordStarts`), so the leg can say nothing listened in a beat or after the thanks. `quietMs` and `beatMs` are
#: left at the page's defaults (2.0 s on options, 4.0 s on free text since keel-web 082; 2.0 s).
SPEECH_SEAM = r"""
(() => {
  class FakeRecognition {
    constructor() {
      this.continuous = false; this.interimResults = false; this.lang = ""; this.maxAlternatives = 1;
      this.onstart = null; this.onresult = null; this.onerror = null; this.onend = null;
      this.results = []; this.started = false; this.stopped = false;
      (window.__speech = window.__speech || []).push(this);
    }
    start() { this.started = true; (window.__speechStarts = window.__speechStarts || []).push(performance.now()); }
    stop() { this.stopped = true; }
    abort() {}
  }
  window.__keelSpeech = {
    Recognition: FakeRecognition, recorder: null,
    mic: { acquire: async () => true, level: () => 0.12, release: () => undefined },
    earcons: false,
  };
  const last = () => (window.__speech || [])[(window.__speech || []).length - 1];
  window.__say = (text, final) => {
    const r = last();
    if (!r) return false;
    r.results.push({ isFinal: !!final, 0: { transcript: text }, length: 1 });
    if (r.onresult) r.onresult({ resultIndex: r.results.length - 1, results: r.results });
    if (final) setTimeout(() => { if (r.onend) r.onend({}); }, 0);
    return true;
  };
  window.__speechError = (error) => { const r = last(); if (r && r.onerror) r.onerror({ error }); };
  window.__speechEnd = () => { const r = last(); if (r && r.onend) r.onend({}); };
  window.__recognisers = () => (window.__speech || []).length;
  window.__listening = () => { const r = last(); return !!(r && r.started && !r.stopped && r.onresult); };
  // spec 050: every recording started, stamped (the seam's path is the browser's, so none is expected)
  if (window.MediaRecorder && window.MediaRecorder.prototype && window.MediaRecorder.prototype.start) {
    const start = window.MediaRecorder.prototype.start;
    window.MediaRecorder.prototype.start = function (...args) {
      (window.__recordStarts = window.__recordStarts || []).push(performance.now());
      return start.apply(this, args);
    };
  }
})();
"""


#: Spec 051 (keel-web 076 FR-6..FR-8; its `installFakeRecorder` / `installRefusedMic`, restated): the recorder the walks
#: drive and a microphone that counts its acquisitions. `__level(rms)` is what it hears from now on (ten times a second,
#: as the real one); every start, stop and cancel is stamped (`performance.now()`) on `__recordStarts` /
#: `__recordStops` / `__recordCancels`, every level set on `__levels`; `__holdStop()` makes the next stop wait for
#: `__releaseStop()` (so *Writing it down…* can be read). The audio handed back is a few KiB of `audio/webm` -- under
#: every window's size cap and over nothing the cloud checks, so the stack's fake transcriber writes it down.
_RECORDER = r"""
  const stamps = (name) => (window[name] = window[name] || []);
  window.__levelNow = 0;
  let ticker; let held = false; let waiting = null;
  const recorder = {
    start: async (onLevel) => {
      stamps('__recordStarts').push(performance.now());
      clearInterval(ticker);
      ticker = setInterval(() => { if (onLevel) onLevel(window.__levelNow); }, 100);
      return true;
    },
    stop: async () => {
      clearInterval(ticker);
      stamps('__recordStops').push(performance.now());
      if (held) await new Promise((resolve) => { waiting = resolve; });
      return { audio: btoa('a spoken answer '.repeat(256)), mimeType: 'audio/webm' };
    },
    cancel: () => { clearInterval(ticker); stamps('__recordCancels').push(performance.now()); },
  };
  window.__level = (rms) => { window.__levelNow = rms; stamps('__levels').push([performance.now(), rms]); };
  window.__holdStop = () => { held = true; };
  window.__releaseStop = () => { held = false; if (waiting) { const w = waiting; waiting = null; w(); } };
"""


def text_seam(*, refused: bool = False) -> str:
    """The text page's seam (keel-web 076: the box reads `Recognition`, `recorder`, `mic`, `quietMs`, `silenceMs` and
    the caps): no recogniser, so the box records; the microphone counted (`__micAcquired`, 0 until the pill is tapped)
    and refused when `refused` (T6). The quiet and the caps are left at the page's defaults (4 s free text, 60 s, 120 s)."""
    return ("(() => {" + _RECORDER + """
  window.__micAcquired = 0; window.__micReleased = 0;
  window.__keelSpeech = {
    Recognition: null, recorder,
    mic: { acquire: async () => { window.__micAcquired += 1; stamps('__micAcquiredAt').push(performance.now());
                                  return !%s; },
           level: () => window.__levelNow, release: () => { window.__micReleased += 1; } },
    earcons: false,
  };
})();
""" % ("true" if refused else "false"))


def recorder_seam(*, follow_up_cap_ms: int | None = None) -> str:
    """Spec 051 FR-6 / FR-7: the AI page's seam (`SPEECH_SEAM`, installed first) gains the recorder -- the page keeps
    its recogniser until one refuses (`not-allowed`), then records every window (keel-web `listenFailed`) -- and,
    when given, the follow-up's cap through the seam (`followUpCapMs`; the wire's `maxSeconds` stays 120)."""
    cap = f"window.__keelSpeech.followUpCapMs = {int(follow_up_cap_ms)};" if follow_up_cap_ms else ""
    return "(() => {" + _RECORDER + "  window.__keelSpeech.recorder = recorder;\n  " + cap + "\n})();\n"


def _json(response) -> dict:
    try:
        body = response.json()
    except Exception:  # noqa: BLE001 - an empty or non-JSON body
        return {"status": response.status}
    return body if isinstance(body, dict) else {"status": response.status, "body": body}


def _words(locator) -> str:
    return " ".join((locator.text_content() or "").split()) if locator.count() else ""


# ------------------------------------------------------------------------------------- tap to hear (087)

#: keel-web 087's test ids: the play glyph on an unpicked card, the intro's *Hear <name>*; keel-web 088's twin on the
#: who-asks band (`persona-hear`, *Hear Livia · 5 s*).
FACE_HEAR = "face-hear"
INTRO_HEAR = "intro-hear"
PERSONA_HEAR = "persona-hear"
#: keel-web 087 FR-5 `introHear(name, seconds)`: the intro's button starts *Hear <name>* (its seconds after a dot).
HEAR_PREFIX = "Hear "

#: Installed once a page: every `video`'s play / playing / pause / ended / error, heard on the document in the capture
#: phase, with the card (`data-face`) or the intro it plays in, `muted`, the clock, the duration and the source; and
#: `poll(selectors)` -- every 100 ms, whether each selector's element is there and enabled -- until `stop()`.
HEAR_JS = r"""() => {
  if (!window.__keelHear) {
    const log = {events: [], polls: [], timer: null};
    const snap = (v, type) => {
      const card = v.closest('[data-face]');
      log.events.push({type, t: performance.now(), face: card ? card.getAttribute('data-face') : null,
                       intro: !!v.closest('[data-testid=ai-intro]'), band: !!v.closest('[data-testid=persona-line]'),
                       hearing: (v.closest('[data-testid=persona-line]') || {getAttribute: () => null})
                                  .getAttribute('data-hearing'), muted: v.muted, paused: v.paused,
                       currentTime: v.currentTime, duration: Number.isFinite(v.duration) ? v.duration : null,
                       src: v.currentSrc || v.src || '', error: v.error ? v.error.code : null});
    };
    for (const type of ['play', 'playing', 'pause', 'ended', 'error']) {
      document.addEventListener(type, (e) => { if (e.target instanceof HTMLVideoElement) snap(e.target, type); }, true);
    }
    log.reset = () => { log.events = []; log.polls = []; };
    log.poll = (selectors) => {
      log.stop();
      log.timer = setInterval(() => {
        log.polls.push({t: performance.now(), enabled: selectors.map((sel) => {
          const el = document.querySelector(sel);
          return el ? !el.disabled : null; })});
      }, 100);
    };
    log.stop = () => { if (log.timer) clearInterval(log.timer); log.timer = null; };
    log.read = () => ({events: log.events.slice(), polls: log.polls.slice(), now: performance.now()});
    window.__keelHear = log;
  }
  window.__keelHear.reset();
  return true;
}"""

#: Whether a container shows a `video` (laid out) and its still (`role=img`, laid out) -- the clip in place of the still.
_SHOWING_JS = r"""(el) => {
  const shown = (x) => { if (!x) return false; const r = x.getBoundingClientRect(); const cs = getComputedStyle(x);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && cs.opacity !== '0'; };
  const videos = Array.from(el.querySelectorAll('video'));
  return {video: videos.some(shown), videos: videos.length, still: Array.from(el.querySelectorAll('[role=img]')).some(shown)};
}"""

#: The ended (or an error) of a clip in `where` -- a card's code, "intro", or "band" (088's who-asks band).
_ENDED_JS = r"""(where) => (window.__keelHear ? window.__keelHear.events : []).some((e) =>
  (e.type === 'ended' || e.type === 'error') && (where === 'intro' ? e.intro : where === 'band' ? e.band
                                                  : e.face === where))"""


def _showing(locator) -> dict:
    return locator.evaluate(_SHOWING_JS) if locator.count() else {"video": False, "videos": 0, "still": False}


def _heard(page: Page, where: str, start, *, wait_s: float, polls: list[str] | None = None) -> dict:
    """Tap (`start()`), then wait for the clip in `where` to end and the still to return; what the listener heard."""
    page.evaluate(HEAR_JS)
    if polls:
        page.evaluate("(sels) => window.__keelHear.poll(sels)", polls)
    t0 = page.evaluate("() => performance.now()")
    start()
    ended = True
    try:
        page.wait_for_function(_ENDED_JS, arg=where, timeout=wait_s * 1000)
    except Exception:  # noqa: BLE001 - a clip that never ends is the mark's to fail, not the walk's
        ended = False
    page.evaluate("() => window.__keelHear.stop()")
    log = page.evaluate("() => window.__keelHear.read()")
    for e in log["events"]:
        e["ms"] = round(e.pop("t") - t0)
    return {"ended": ended, "events": log["events"],
            "polls": [p["enabled"] for p in log["polls"]], "elapsed_ms": round(log["now"] - t0)}


def _still_back(container, *, wait_s: float) -> dict:
    """The container's still back and no clip showing, waited for up to `wait_s` after the end."""
    deadline = wait_s * 1000
    waited = 0
    shown = _showing(container)
    while (shown["video"] or not shown["still"]) and waited < deadline:
        container.page.wait_for_timeout(100)
        waited += 100
        shown = _showing(container)
    return {**shown, "waited_ms": waited}


def hear_card(page: Page, scope, face: str, *, wait_s: float) -> dict:
    """keel-web 087 FR-2: a tap on `face`'s card in the carousel under `scope` -- what the card was (picked, its glyph,
    its still), what played inside it and in any other card, and the card after the clip's end (picked, the still
    back, no clip showing). Every unpicked card's glyph is counted too."""
    carousel = scope.get_by_test_id("face-carousel") if scope.get_by_test_id("face-carousel").count() else scope
    card = carousel.locator(f'[data-face="{face}"]')
    card.wait_for(state="visible", timeout=10_000)
    cards = carousel.locator('button[role="radio"]')
    before = {"picked": card.get_attribute("aria-checked") == "true",
              "glyph": card.get_by_test_id(FACE_HEAR).count() > 0, **_showing(card),
              "glyphs": {c.get_attribute("data-face"): c.get_by_test_id(FACE_HEAR).count() > 0
                         for c in cards.all() if c.get_attribute("aria-checked") != "true"}}
    heard = _heard(page, face, card.click, wait_s=wait_s)
    after = {"picked": card.get_attribute("aria-checked") == "true", **_still_back(card, wait_s=5)}
    return {"face": face, "before": before, **heard, "after": after,
            "checked": [c.get_attribute("data-face") for c in cards.all() if c.get_attribute("aria-checked") == "true"]}


# --------------------------------------------------------------------------------------------- the founder

class Persona:
    def __init__(self, page: Page, recorder, base_url: str, *, patience: float = 1.0, guide: dict | None = None):
        self.page = page
        self.base = base_url.rstrip("/")
        self.patience = patience
        self._b = _BrowserStep(recorder, page, "founder")
        self.recorder = recorder
        #: Spec 059: the journey's guide record, where the Sent-open helper keeps each pass of 088's sheet.
        self.guide = guide

    def sent(self, project_id: str) -> None:
        """Sent, opened when not already on it, with keel-web 088's first-open sheet passed by (spec 059 FR-4)."""
        if not self.page.url.split("?")[0].endswith(f"/p/{project_id}/interviews/sent"):
            self.page.goto(f"{self.base}/p/{project_id}/interviews/sent", wait_until="load")
        self.page.locator(".sent__kinds").wait_for(state="visible", timeout=60_000 * self.patience)
        _iv.pass_interviews_sheet(self.page, self.recorder, self.base, guide=self.guide)

    def line(self) -> dict:
        """The persona line as drawn: its state, words, bar and action."""
        line = self.page.get_by_test_id("persona-line")
        if not line.count():
            return {"state": None, "text": ""}
        bar = line.locator("[role=progressbar]")
        action = line.get_by_test_id("change-who-asks")
        return {"state": line.get_attribute("data-state"), "text": _words(line),
                "bar": ({"now": bar.get_attribute("aria-valuenow"), "max": bar.get_attribute("aria-valuemax")}
                        if bar.count() else None),
                "action": _words(action) or None,
                "try_again": line.get_by_test_id("persona-try-again").count() > 0}

    def wait_state(self, state: str, *, timeout_s: float = 45) -> dict:
        """The line in place reaching `state` (keel-web polls `GET interviewer` every 10 s while RECORDING)."""
        self.page.locator(f'[data-testid=persona-line][data-state="{state}"]').wait_for(
            state="visible", timeout=timeout_s * 1000 * self.patience)
        return self.line()

    def cards(self) -> list[dict]:
        """Each kind's card: its label, *Try it yourself* (enabled or not, its words) and the primary's words."""
        out = []
        for card in self.page.locator(".sent__kinds .role").all():
            tryit = card.get_by_test_id("try-it-yourself")
            out.append({"label": _words(card.locator(".role__label").first),
                        "try": {"text": _words(tryit), "enabled": tryit.is_enabled()} if tryit.count() else None,
                        "primary": _words(card.locator(".btn.primary").first)})
        return out

    def record(self, face: str, *, expect_status: int | None = None, hear_s: float | None = None) -> dict:
        """*Change who asks* / *Record the interviewer* -> the popup -> the face -> *Record {Face}*: what the popup drew,
        the POST keel-web sent and what it received; on a refusal the popup's words (it stays open; Cancel closes).
        `hear_s` (spec 058): the tap is keel-web 087's tap to hear, its clip waited for up to that long (`hear`)."""
        with self._b.step(f"founder picks {face.title()} in the persona line's popup") as h:
            self.page.get_by_test_id("change-who-asks").click()
            popup = self.page.get_by_test_id("change-face-popup")
            popup.wait_for(state="visible", timeout=10_000)
            drawn = {"title": _words(popup.locator("h2").first), "lead": _words(popup.locator(".ccard__sub").first),
                     "faces": [b.get_attribute("data-face") for b in popup.locator('button[role="radio"]').all()]}
            heard = None
            if hear_s is None:
                popup.locator(f'[data-face="{face}"]').click()
            else:
                heard = hear_card(self.page, popup, face, wait_s=hear_s)
                h.add_screenshot(self._b.screenshot(f"heard-{face.lower()}"))
            confirm = popup.get_by_test_id("change-face-confirm")
            drawn["confirm"] = _words(confirm)
            with self.page.expect_response(lambda r: r.request.method == "POST"
                                           and r.url.endswith("/interviewer/face"), timeout=30_000) as posted:
                confirm.click()
            out = {"popup": drawn, "sent": posted.value.request.post_data_json, "status": posted.value.status,
                   "body": _json(posted.value)}
            if heard is not None:
                out["hear"] = heard
            if posted.value.status >= 400:
                popup.locator(".remedy, [role=alert], .banner").first.wait_for(state="visible", timeout=10_000)
                out["refusal"] = _words(popup.locator(".remedy, [role=alert], .banner").first)
                out["popup_text"] = _words(popup)
                h.add_screenshot(self._b.screenshot("change-face-refused"))
                popup.get_by_role("button", name="Cancel", exact=True).click()
            else:
                popup.wait_for(state="hidden", timeout=10_000)
            h.add_screenshot(self._b.screenshot(f"persona-{face.lower()}"))
            return out

    def formats_now(self, kind_label: str) -> dict:
        """S3: *Send more*'s format row on a kind's card, read and cancelled (nothing is made)."""
        card = self.page.locator(".sent__kinds .role",
                                 has=self.page.locator(".role__label", has_text=re.compile(
                                     rf"^{re.escape(kind_label)}$"))).first
        card.locator(".btn.primary").click()
        dialog = self.page.get_by_role("dialog")
        dialog.locator("[role=radiogroup] [role=radio]").first.wait_for(state="visible", timeout=10_000)
        rows = {}
        for radio in dialog.locator("[role=radiogroup] [role=radio]").all():
            word = radio.locator(".fmt__na")
            rows[_words(radio.locator(".fmt__name").first)] = {
                "disabled": radio.is_disabled(), "checked": radio.get_attribute("aria-checked") == "true",
                "word": _words(word) if word.count() else None}
        out = {"rows": rows, "hint": _words(dialog.locator(".hint").first), "text": _words(dialog)}
        dialog.get_by_role("button", name="Cancel", exact=True).first.click()
        dialog.wait_for(state="hidden", timeout=10_000)
        return out

    def how_it_works(self) -> int:
        """Spec 059: the controls on Sent named *How it works* -- keel-web 088 removed the replay of W1 (none)."""
        return self.page.get_by_role("button", name=HOW_IT_WORKS, exact=True).count() + \
            self.page.get_by_role("link", name=HOW_IT_WORKS, exact=True).count()

    def hear_band(self, *, wait_s: float) -> dict:
        """keel-web 088 FR-2 (IM30): *Hear <name> · 5 s* on the who-asks band (`persona-hear`) -- its words, the clip
        that played in the band's circle in place of the still, `data-hearing` while it played, and the band after the
        end (the still back, no clip showing). `present` False (nothing pressed) where the band draws no button."""
        band = self.page.get_by_test_id("persona-line")
        band.wait_for(state="visible", timeout=10_000)
        button = band.get_by_test_id(PERSONA_HEAR)
        if not button.count():
            return {"present": False, "state": band.get_attribute("data-state"), "text": _words(band)}
        circle = band.locator(".pface-hello").first
        before = {"words": _words(button), "label": button.get_attribute("aria-label"), **_showing(circle),
                  "hearing": band.get_attribute("data-hearing")}
        hearing: list = []

        def tap() -> None:
            button.click()
            try:
                self.page.locator('[data-testid=persona-line][data-hearing="true"]').wait_for(state="attached",
                                                                                            timeout=2_000)
                hearing.append(True)
            except Exception:  # noqa: BLE001 - never marked: the mark's to read
                hearing.append(False)
        heard = _heard(self.page, "band", tap, wait_s=wait_s)
        after = {**_still_back(circle, wait_s=5), "hearing": band.get_attribute("data-hearing")}
        return {"present": True, "before": before, "hearing_while": bool(hearing and hearing[0]), **heard,
                "after": after}

    def l1_again(self, project_id: str) -> dict:
        """L1 revisited on a locked project (the carousel, disabled; no button): its whole text, for the no-price rule."""
        self.page.goto(f"{self.base}/p/{project_id}/define/ready/interviewer", wait_until="load")
        main = self.page.locator(".corridor.before").first
        main.wait_for(state="visible", timeout=30_000)
        self.page.get_by_test_id("face-carousel").wait_for(state="visible", timeout=20_000)
        carousel = self.page.get_by_test_id("face-carousel")
        return {"text": _words(main), "faces": [b.get_attribute("data-face")
                                                for b in carousel.locator('button[role="radio"]').all()],
                "checked": [b.get_attribute("data-face") for b in
                            carousel.locator('button[role="radio"][aria-checked="true"]').all()]}

    def try_it(self, project_id: str, role_label: str) -> None:
        """*Try it yourself* on the kind's card: the dry run's route."""
        card = self.page.locator(".sent__kinds .role",
                                 has=self.page.locator(".role__label", has_text=re.compile(
                                     rf"^{re.escape(role_label)}$"))).first
        card.get_by_test_id("try-it-yourself").click()
        self.page.wait_for_url(re.compile(rf"/p/{project_id}/interviews/try/"), timeout=20_000)


# --------------------------------------------------------------------------------------------- the player

class Player:
    """The AI interviewer's page, for a stranger (a link) or the founder (Try it yourself): driven through the speech
    seam, a tap, a typed field or *Type instead*, the way a person would."""

    def __init__(self, page: Page, recorder, *, party: str = "participant", patience: float = 1.0):
        self.page = page
        self.patience = patience
        self._b = _BrowserStep(recorder, page, party)
        self.requests: list[dict] = []
        #: Spec 049: every `classify` the page sent, its body, in order (the read-aloud step counts its reads here).
        self.classified: list[dict] = []
        #: Spec 049 (keel-web 073 FR-1): what the sheet showed a moment after each final said on a question's or a
        #: confirmation's window, inside the quiet gap -- before the utterance was read.
        self.hearing: list[dict] = []
        page.on("request", self._keep)

    def _keep(self, request) -> None:
        if "/v2/" in request.url and request.method != "GET":
            self.requests.append({"method": request.method, "url": request.url})
            if request.url.split("?")[0].endswith("/classify"):
                try:
                    body = request.post_data_json
                except Exception:  # noqa: BLE001 - a body that is not JSON
                    body = None
                self.classified.append({"url": request.url, "body": body})

    # ---- arriving
    def open(self, url: str) -> dict:
        self.page.goto(url, wait_until="load")
        intro = self.page.get_by_test_id("ai-intro")
        intro.wait_for(state="visible", timeout=30_000)
        return self.intro()

    def intro(self) -> dict:
        intro = self.page.get_by_test_id("ai-intro")
        start = self.page.get_by_test_id("start-talking")
        heard = self.page.get_by_test_id("ai-mic-heard")
        return {"intro": intro.get_attribute("data-intro"), "heading": _words(intro.locator("h1").first),
                "text": _words(intro),
                "buttons": [t for t in ("start-talking", "choice-talk", "choice-write")
                            if self.page.get_by_test_id(t).count()],
                "mic_test": self.page.get_by_test_id("ai-mic-test").count() > 0,
                "mic_heard": _words(heard) or None,
                "start_enabled": start.is_enabled() if start.count() else None}

    def hear(self, *, wait_s: float) -> dict:
        """keel-web 087 FR-3: *Hear <name>* (`intro-hear`) on the intro -- its words, the clip that played in place of
        the round still, the still after the end, and the choice buttons' enabled state polled every 100 ms from the
        tap to the end (`polls`: one [talk, write] pair a poll)."""
        intro = self.page.get_by_test_id("ai-intro")
        button = self.page.get_by_test_id(INTRO_HEAR)
        button.wait_for(state="visible", timeout=10_000)
        before = {"words": _words(button), "label": button.get_attribute("aria-label"), **_showing(intro),
                  "buttons": {t: self.page.get_by_test_id(t).is_enabled() for t in ("choice-talk", "choice-write")
                              if self.page.get_by_test_id(t).count()}}
        heard = _heard(self.page, "intro", button.click, wait_s=wait_s,
                       polls=["[data-testid=choice-talk]", "[data-testid=choice-write]"])
        after = {**_still_back(intro, wait_s=5),
                 "buttons": {t: self.page.get_by_test_id(t).is_enabled() for t in ("choice-talk", "choice-write")
                             if self.page.get_by_test_id(t).count()}}
        return {"before": before, **heard, "after": after}

    def mic_test(self, heard: str = "hello", *, timeout_s: float = 20) -> dict:
        """keel-web 072 FR-7: *Test your mic* -> the seam's microphone (always granted) -> *Say hello* -> `heard` said
        -> *Heard: hello* with its tick, and *Start the interview* enabled. What the intro drew before and after."""
        before = self.intro()
        made = self.ear()["count"]
        self.page.get_by_test_id("ai-mic-test").click()
        deadline = timeout_s * 1000 * self.patience
        # the one-shot recogniser is made by the press, after the microphone is granted: speak once it listens
        self.wait_ear(newer_than=made, timeout_s=timeout_s)
        said = self.say(heard, True)
        line = self.page.get_by_test_id("ai-mic-heard")
        line.wait_for(state="visible", timeout=deadline)
        self.page.locator("[data-testid=start-talking]:not([disabled])").wait_for(timeout=deadline)
        return {"before": before, "said": said, "after": self.intro()}

    def start(self, testid: str = "start-talking") -> None:
        """The intro's button -- pressed again while the page is still the intro: a press that lands before the app
        has hydrated is lost (seen once on S-006: the intro drawn, the stage never left it). Since keel-web 072 it is
        enabled by *Test your mic* (or its fallback), so the leg tests the mic first."""
        button = self.page.get_by_test_id(testid)
        for _ in range(5):
            button.click()
            try:
                self.page.get_by_test_id("ai-intro").wait_for(state="detached", timeout=3_000)
                return
            except Exception:  # noqa: BLE001 - still the intro: press again
                if not button.count():
                    return
        raise AssertionError(f"the intro never left on {testid}")

    # ---- the stage
    def phase(self) -> str | None:
        stage = self.page.get_by_test_id("ai-stage")
        return stage.get_attribute("data-phase") if stage.count() else None

    def wait_phase(self, *phases: str, timeout_s: float = 30) -> str:
        sel = ", ".join(f'[data-testid=ai-stage][data-phase="{p}"]' for p in phases)
        self.page.locator(sel).first.wait_for(state="attached", timeout=timeout_s * 1000 * self.patience)
        return self.phase() or ""

    def stage(self) -> dict:
        video = self.page.locator("video.aiv-stage__video")
        return {"phase": self.phase(), "where": _words(self.page.get_by_test_id("ai-where")),
                "state": _words(self.page.get_by_test_id("ai-state")),
                "mark": _words(self.page.get_by_test_id("ship-mark")),
                "videos": video.count(), "clip": video.first.get_attribute("data-clip") if video.count() else None}

    # ---- the sheet
    def sheet(self) -> dict:
        sheet = self.page.get_by_test_id("ai-sheet")
        options = sheet.locator("[data-testid=ai-options] .opt")
        field = sheet.get_by_test_id("ai-field")
        return {"question": _words(sheet.locator(".iv-q").first), "kicker": _words(sheet.locator(".iv-kicker").first),
                "options": [{"label": _words(o), "checked": o.get_attribute("aria-checked") == "true",
                             "role": o.get_attribute("role"), "unsure": o.get_attribute("data-unsure")}
                            for o in options.all()],
                "field": field.input_value() if field.count() else None,
                "chip": _words(sheet.locator(".iv-chips .chip").first) or None,
                "preview": _words(sheet.get_by_test_id("ai-preview")),
                "heard": _words(sheet.get_by_test_id("ai-heard")),
                "status": _words(sheet.get_by_test_id("ai-status")),
                "banner": _words(sheet.get_by_test_id("ai-banner")) or None}

    def say(self, text: str, final: bool = True, *, look: bool = True) -> bool:
        """The stranger speaks into the newest recogniser. A final ends the utterance (the seam's recogniser then ends,
        keel-web 072 FR-3), and -- keel-web 073 -- the page reads it after the quiet gap; nothing is pressed after it.
        On a question's or a confirmation's window (`listening` / `confirming`) a final is looked at inside the gap
        (`look`): what was ticked, filled and previewed before the words and 250 ms after them, kept on `hearing`."""
        phase = self.phase() if final and look else None
        before = self._drawn() if phase in ("listening", "confirming") else None
        said = bool(self.page.evaluate("([t, f]) => window.__say(t, f)", [text, final]))
        if before is not None and said:
            self.page.wait_for_timeout(250)
            after = self._drawn()
            self.hearing.append({"said": text, "phase": phase, "before": before, "after": after,
                                 "still": self.phase() == phase and after["status"] == HEARING})
        return said

    def _drawn(self) -> dict:
        """The sheet's ticks, field, preview, heard line and status, read in one evaluate (inside the gap it must be
        quick)."""
        return self.page.evaluate("""() => {
            const sheet = document.querySelector('[data-testid=ai-sheet]');
            const words = (el) => el ? (el.textContent || '').replace(/\\s+/g, ' ').trim() : '';
            if (!sheet) return { lit: [], field: null, preview: '', heard: '', status: '' };
            const lit = [...sheet.querySelectorAll('[data-testid=ai-options] .opt[aria-checked="true"]')].map(words);
            const field = sheet.querySelector('[data-testid=ai-field]');
            return { lit, field: field ? field.value : null,
                     preview: words(sheet.querySelector('[data-testid=ai-preview]')),
                     heard: words(sheet.querySelector('[data-testid=ai-heard]')),
                     status: words(sheet.querySelector('[data-testid=ai-status]')) };
        }""")

    def checked(self) -> list[str]:
        """The rows ticked on the sheet now (`aria-checked="true"`)."""
        return list(self._drawn()["lit"])

    def ear(self) -> dict:
        """The seam's recognisers: how many the page has made, and whether the newest is listening -- started, not
        stopped, and still handed results by the page (keel-web 073 `__listening()`: the gap's restart and a read's
        stop leave recognisers behind that no longer hear anything)."""
        return self.page.evaluate("""() => { const s = window.__speech || []; const r = s[s.length - 1];
            return { count: s.length, live: !!(r && r.started && !r.stopped && r.onresult) }; }""")

    def wait_ear(self, *, newer_than: int | None = None, timeout_s: float = 20) -> dict:
        """A recogniser listening -- one made after `newer_than` recognisers when given (a window opened again after
        a clip)."""
        deadline = timeout_s * 1000 * self.patience
        waited = 0.0
        while waited <= deadline:
            ear = self.ear()
            if ear["live"] and (newer_than is None or ear["count"] > newer_than):
                return ear
            self.page.wait_for_timeout(100)
            waited += 100
        raise AssertionError({"no recogniser listening": self.ear(), "newer than": newer_than,
                              "phase": self.phase(), "status": self.status()})

    def status(self) -> str:
        return _words(self.page.get_by_test_id("ai-status"))

    def question(self) -> str:
        return _words(self.page.get_by_test_id("ai-sheet").locator(".iv-q").first)

    def wait_status(self, *words: str, timeout_s: float = 20) -> str:
        """The sheet's status line reading one of `words` (keel-web 072 FR-9)."""
        deadline = timeout_s * 1000 * self.patience
        waited = 0.0
        while waited <= deadline:
            now = self.status()
            if any(w in now for w in words):
                return now
            self.page.wait_for_timeout(100)
            waited += 100
        raise AssertionError({"status never read": words, "it read": self.status(), "phase": self.phase()})

    def wait_missed(self, *, timeout_s: float = 20) -> str:
        """keel-web 073: a miss is read after the quiet gap -- the heard line tagged *not taken*, or her asking again.
        What the heard line or the status then read."""
        deadline = timeout_s * 1000 * self.patience
        waited = 0.0
        while waited <= deadline:
            drawn = self._drawn()
            if TAG_NOT_TAKEN in drawn["heard"] or "asks again" in drawn["status"] or "Say it again" in drawn["status"]:
                return drawn["preview"] or drawn["heard"] or drawn["status"]
            self.page.wait_for_timeout(100)
            waited += 100
        raise AssertionError({"the miss was never read": self._drawn(), "phase": self.phase()})

    def hold(self, *, timeout_s: float = 20) -> dict:
        """A confident read held (keel-web 072 FR-4): the status reads *Got it. Moving on… say no to change* with the
        pick lit, and -- nothing said, nothing tapped -- the question goes on by itself. What the hold drew, and the
        question that came after it."""
        before = self.question()
        status = self.wait_status(HELD, timeout_s=timeout_s)
        phase = self.phase()
        sheet = self.sheet()
        rings = self.page.locator("[data-testid=ai-sheet] .aiv__ring, [data-testid=ai-ring]").count()
        finish = self.page.get_by_test_id("ai-finish")
        finish_shown = finish.count() > 0 and finish.first.is_visible()
        deadline = timeout_s * 1000 * self.patience
        waited = 0.0
        while waited <= deadline and self.question() == before and HELD in self.status():
            self.page.wait_for_timeout(100)
            waited += 100
        return {"question": before, "status": status, "lit": [o["label"] for o in sheet["options"] if o["checked"]],
                "unsure": [o["unsure"] for o in sheet["options"] if o["checked"]], "phase": phase,
                "heard": sheet["heard"], "ring": rings > 0, "finish": finish_shown, "next": self.question(),
                "went_on": self.question() != before or HELD not in self.status()}

    def veto(self, word: str = VETO, *, final: bool = False) -> dict:
        """A word of protest in the hold (FR-4): the hold ends and the question reopens, the pick still lit. Said as an
        interim by default -- keel-web 072 hears a veto in an interim or a final, and keeps the same recogniser for the
        question (its call 5), so what is said next is the new answer, not "no" read on its own."""
        before = self.question()
        self.wait_status(HELD)
        self.wait_ear()                                 # the hold's window listening
        self.say(word, final)
        waited = 0
        while waited < 5_000 * self.patience and HELD in self.status():
            self.page.wait_for_timeout(100)
            waited += 100
        reopened = self.question() == before and HELD not in self.status()
        return {"question": before, "said": word, "reopened": reopened, "status": self.status(),
                "lit": [o["label"] for o in self.sheet()["options"] if o["checked"]]}

    def confirming(self, *, timeout_s: float = 20) -> dict:
        """An unsure read (FR-2): *Is that right? Say yes, or tell me the right one*, the pick lit, the Yes chip."""
        status = self.wait_status(IS_THAT_RIGHT, timeout_s=timeout_s)
        sheet = self.sheet()
        unsure = [_words(o) for o in self.page.locator('[data-testid=ai-sheet] .opt[data-unsure="true"]').all()]
        yes = self.page.get_by_test_id("ai-yes")
        return {"question": self.question(), "status": status,
                "lit": [o["label"] for o in sheet["options"] if o["checked"]], "unsure": unsure,
                "yes": _words(yes) if yes.count() else None}

    def yes(self, *, by: str = "say") -> None:
        """Agreeing to "Is that right?": *Yes, that's it* tapped, or "yes" said -- straight on, no hold."""
        if by == "tap":
            self.page.get_by_test_id("ai-yes").click()
        else:
            self.say(SAY_YES, True)

    def back(self, *, by: str = "tap") -> dict:
        """The way back (FR-6): *‹ Back to question n* tapped, or "go back" said, from the next question -- the previous
        question reopens with its answer lit, no clip replayed."""
        before = self.question()
        button = self.page.get_by_test_id("ai-back")
        drawn = _words(button) if button.count() else None
        if by == "say":
            self.say(GO_BACK, True)
        else:
            button.click()
        deadline = 10_000 * self.patience
        waited = 0.0
        while waited <= deadline and self.question() == before:
            self.page.wait_for_timeout(100)
            waited += 100
        sheet = self.sheet()
        return {"from": before, "button": drawn, "by": by, "to": self.question(),
                "lit": [o["label"] for o in sheet["options"] if o["checked"]], "field": sheet["field"]}

    def timeline(self) -> list[dict]:
        """`FLOW_TIMELINE`'s events, or none where the init script was not installed."""
        try:
            return list(self.page.evaluate("() => window.__keelFlow ? window.__keelFlow() : []") or [])
        except Exception:  # noqa: BLE001 - a page that has gone
            return []

    def statuses(self) -> list[dict]:
        """`FLOW_TIMELINE`'s status words, in order (`window.__keelPhases`)."""
        try:
            return list(self.page.evaluate("() => window.__keelPhases ? window.__keelPhases() : []") or [])
        except Exception:  # noqa: BLE001
            return []

    def saw_thats_my_answer(self) -> bool | None:
        try:
            return self.page.evaluate("() => window.__keelSawAnswer ? window.__keelSawAnswer() : null")
        except Exception:  # noqa: BLE001
            return None

    def beats(self) -> list[dict]:
        """Spec 050 (keel-web 075 FR-1): every beat the timeline kept -- its start and end (`performance.now()`), the clip
        played before it, the statuses and pills it drew, and whether the waveform, a question, the options or a sheet
        button were ever in it."""
        try:
            return list(self.page.evaluate("() => window.__keelBeats ? window.__keelBeats() : []") or [])
        except Exception:  # noqa: BLE001 - a page that has gone
            return []

    def starts(self) -> dict:
        """Spec 050: when every seam recogniser was started and every recording begun (`performance.now()`)."""
        try:
            return dict(self.page.evaluate(
                "() => ({ speech: (window.__speechStarts || []).slice(), record: (window.__recordStarts || []).slice() })"))
        except Exception:  # noqa: BLE001
            return {"speech": [], "record": []}

    def mic_off(self, *, timeout_s: float = 10) -> dict:
        """keel-web 075 FR-4: *Microphone off* (`ai-mic-off`, `role=status`) on the done or the ended screen once every
        holder of the microphone has let go; and the seam's newest recogniser no longer listening."""
        line = self.page.get_by_test_id("ai-mic-off")
        try:
            line.first.wait_for(state="visible", timeout=timeout_s * 1000 * self.patience)
        except Exception:  # noqa: BLE001 - not drawn: reported, the leg judges
            pass
        shown = line.count() > 0 and line.first.is_visible()
        return {"shown": shown, "text": _words(line.first) if shown else None,
                "role": line.first.get_attribute("role") if shown else None,
                "listening": bool(self.page.evaluate("() => window.__listening ? window.__listening() : false")),
                "at": float(self.page.evaluate("() => performance.now()"))}

    def save(self) -> None:
        """*Save and next* -- typed words keep their explicit press (072 FR-5), and since keel-web 073 FR-6 tapped
        checkboxes finish on it too."""
        self.page.get_by_test_id("ai-sheet").get_by_role("button", name=SAVE_AND_NEXT, exact=True).click()

    def save_state(self) -> dict:
        """keel-web 073 FR-6: *Save and next* (`ai-save`) -- drawn or not, enabled or not, its words; and the hold's ring
        (`ai-ring`), which a tick never starts."""
        button = self.page.get_by_test_id("ai-save")
        shown = button.count() > 0 and button.first.is_visible()
        return {"shown": shown, "enabled": button.first.is_enabled() if shown else None,
                "words": _words(button.first) if shown else None,
                "ring": self.page.get_by_test_id("ai-ring").count() > 0, "phase": self.phase(),
                "checked": self.checked()}

    def finish(self) -> None:
        """*Finish* on the pilot ask (072 FR-2). Since keel-web 073 FR-7 the pilot's yes is held and goes on by itself:
        *Finish* only ends that hold early, and after a tap it is on the sheet for the tap's 500 ms alone (073 D-03) --
        the walk waits for the thanks instead of pressing it."""
        button = self.page.get_by_test_id("ai-sheet").get_by_role("button", name=FINISH, exact=True)
        button.wait_for(state="visible", timeout=10_000 * self.patience)
        button.click()

    def tap(self, label: str) -> None:
        self.page.get_by_test_id("ai-sheet").locator("[data-testid=ai-options] .opt", has_text=re.compile(
            rf"^\s*{re.escape(label)}\s*$")).first.click()

    def tap_chip(self) -> None:
        self.page.get_by_test_id("ai-sheet").locator(".iv-chips .chip").first.click()

    def type_instead(self, text: str) -> None:
        """*Type instead*, the words typed; *Save and next* (`save`) sends them on."""
        self.page.get_by_test_id("ai-type").click()
        self.page.get_by_test_id("ai-typed").fill(text)

    def fill_field(self, value: str) -> None:
        self.page.get_by_test_id("ai-field").fill(value)

    def unit(self, mode: str) -> None:
        """The amount-or-hours toggle: *Hours*, or *Amount* (its label carries the currency)."""
        name = re.compile(r"^Hours$") if mode == "HOURS" else re.compile(r"^Amount")
        self.page.get_by_test_id("ai-sheet").get_by_role("radiogroup", name="Hours or amount").get_by_role(
            "radio", name=name).click()

    def end(self) -> None:
        self.page.get_by_test_id("ai-end").click()

    def done(self, *, timeout_s: float = 20) -> dict:
        done = self.page.get_by_test_id("ai-done")
        done.first.wait_for(state="visible", timeout=timeout_s * 1000)
        return {"text": _words(done.first), "tryRun": done.first.get_attribute("data-try-run") == "true"}

    def where_it_stood(self) -> dict:
        """What the page drew when a wait gave up: the stage, the sheet, the intro or the end, and the requests."""
        out: dict = {"url": self.page.url}
        try:
            out["stage"] = self.stage()
            if self.page.get_by_test_id("ai-sheet").count():
                out["sheet"] = self.sheet()
            out["body"] = " ".join((self.page.locator("body").text_content() or "").split())[:1500]
        except Exception as broken:  # noqa: BLE001 - a diagnostic never hides the failure it explains
            out["unreadable"] = repr(broken)
        out["requests"] = self.requests[-10:]
        return out

    def screenshot(self, name: str):
        return self._b.screenshot(name)

    def step(self, name: str):
        return self._b.step(name)


# ------------------------------------------------------------------------------------- speak or type (076)

class SpeakBox:
    """keel-web 076's `SpeakOrTypeBox` on a text page (the story's, or the follow-up's): `.sot[data-state]` around the
    textarea and its footer (`.sot__bar`: the hint / the heard line / the mic-off line, and the `iv-mic` pill), the
    listening card (`iv-listening`: `ai-mic-on`, `iv-mic-clock`, `iv-mic-cancel`, `iv-mic-done`) and the writing card
    drawn over it. Driven through `text_seam`: `speak` sets the recorder's level to a sound, `quiet` back to nothing;
    what the seam counted is `counts()`. Reads and acts; judges nothing."""

    def __init__(self, page: Page, scope: str = "main"):
        self.page = page
        self.scope = scope

    def _sot(self):
        return self.page.locator(f"{self.scope} .sot").first

    def now(self) -> float:
        return float(self.page.evaluate("() => performance.now()"))

    def read(self) -> dict:
        """What the box draws now, read in one evaluate."""
        return self.page.evaluate("""(scope) => {
            const words = (el) => el ? (el.textContent || '').replace(/\\s+/g, ' ').trim() : null;
            const sot = document.querySelector(scope + ' .sot');
            if (!sot) return { state: null };
            const text = sot.querySelector('textarea');
            const card = sot.querySelector('[data-testid=iv-listening]');
            const bar = sot.querySelector('.sot__bar');
            const pill = sot.querySelector('[data-testid=iv-mic]');
            const writing = sot.querySelector('.sot__writing');
            return { state: sot.getAttribute('data-state'), placeholder: text ? text.getAttribute('placeholder') : null,
                     value: text ? text.value : null, caret: text ? text.selectionStart : null,
                     caretEnd: text ? text.selectionEnd : null, focused: !!text && document.activeElement === text,
                     pill: words(pill), footer: bar ? words(bar.querySelector('span')) : null,
                     card: !!card, cardWords: words(card), wave: !!(card && card.querySelector('[data-testid=ai-mic-on]')),
                     clock: words(sot.querySelector('[data-testid=iv-mic-clock]')),
                     cancel: !!sot.querySelector('[data-testid=iv-mic-cancel]'),
                     done: !!sot.querySelector('[data-testid=iv-mic-done]'),
                     writing: words(writing), note: words(sot.querySelector('.sot__note')) };
        }""", self.scope)

    def counts(self) -> dict:
        """The seam's stamps: microphone acquisitions, recordings started / stopped / cancelled, levels set."""
        return self.page.evaluate("""() => ({ acquired: window.__micAcquired || 0,
            acquiredAt: (window.__micAcquiredAt || []).slice(), starts: (window.__recordStarts || []).slice(),
            stops: (window.__recordStops || []).slice(), cancels: (window.__recordCancels || []).slice(),
            levels: (window.__levels || []).slice(), released: window.__micReleased || 0 })""")

    def wait_state(self, *states: str, timeout_s: float = 20) -> dict:
        sel = ", ".join(f'{self.scope} .sot[data-state="{s}"]' for s in states)
        self.page.locator(sel).first.wait_for(state="attached", timeout=timeout_s * 1000)
        return self.read()

    def tap(self) -> None:
        self._sot().get_by_test_id("iv-mic").click()

    def done(self) -> None:
        self._sot().get_by_test_id("iv-mic-done").click()

    def speak(self, ms: int = SPEAK_MS) -> float:
        """The person talks for `ms`: the recorder hears a sound; returns when the sound began."""
        at = self.now()
        self.page.evaluate(f"() => window.__level({SOUND})")
        self.page.wait_for_timeout(ms)
        return at

    def quiet(self) -> float:
        """The person stops: the recorder hears nothing from now on; returns when."""
        at = self.now()
        self.page.evaluate("() => window.__level(0)")
        return at

    def hold_stop(self) -> None:
        self.page.evaluate("() => window.__holdStop()")

    def release_stop(self) -> None:
        self.page.evaluate("() => window.__releaseStop()")
