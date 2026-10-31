# Spec 099 -- The interviewer marks read the ear's three states: *Listening…*, *Writing down what you said…*, the words

keel-web 143 (the founder, 2026-10-30): the AI link's heard line never falls to *Heard so far: nothing yet* once a sound
was heard -- *Listening…* before any sound, *Hearing you…* while the microphone hears, *Writing down what you said…*
from the send to the transcript, then *Heard: <words>*; *nothing yet* only on an empty transcript; *Test your mic*
draws the sheet's waveform and the same writing state before *Heard: hello*.

## Rules

- **FR-1 The words.** `evals/interviewer_marks.py` gains `WRITING_DOWN = "Writing down what you said…"` and
  `LISTENING_LINE = "Listening…"`; the recorded-path mark (`:606-617`, v9's *Recording your answer.* + *Hearing you…*)
  also accepts *Writing down what you said…* on the heard line after the pause; **a new check** on every recorded
  window's capture: the heard line never reads *Heard so far: nothing yet* between the first sound and the words (the
  screens walker, `harness/interviewer_screens.py`, samples the heard line through the send as it samples the status).
- **FR-2 IM17.** `mic_tested` (`:563`) reads the wave (`ai-mic-level` wrapping `MicWave`'s bars) in the meter's place and
  the intro's `writing` state before *Heard: hello*; `start_enabled` and the fallback as today.
- **FR-3 Versions.** `INTERVIEWER_MARKS_VERSION` 16 -> 17 (a mark reads a moved line); the certificate's note says why;
  the live `make eval-live K=s012` re-run is the founder's call (paid).
- **FR-4 Nothing else moves.** The tiers, the hold, the browser path's marks, the classifier guard.

## Acceptance

`make unit` green with ZERO failed; `make eval K=s005` green on the local stack at keel-web 143 (the recorded path's
captures carry the three states). Build on the founder's word of 2026-10-30, after 143 merges and after 098.

## Addendum 2026-10-30 -- what keel-web 143 built (merged; read these)

- Heard line `[data-testid=ai-heard]` carries `data-heard` = `listening | hearing | writing | words | nothing`; words
  *Listening…* / *Hearing you…* / *Writing down what you said…* (new string `AI_HEARD_WRITING_DOWN`; the status line's
  `AI_WRITING_DOWN` *Writing it down…* is unchanged and the harness's `WRITING_DOWN` still reads it) / the tag + words /
  *Heard so far: nothing yet*. The recorded-path mark reads `writing` between the pause and the words, never `nothing`
  there; `nothing` only after an empty transcript. Option questions: the line starts at `hearing` and stays `writing`
  until the read lands. No heard line where nothing listens (typing with nothing typed; a recorder that won't start).
- The wave: `ai-mic-on` still marks a listening window (the beat check stands); while a recording is written down the
  bars are `[data-testid=ai-mic-writing]` (`.aiv__wave[data-state=writing]`) inside `ai-status`.
- IM17 Test your mic: `ai-mic[data-state]` adds `writing` (idle | asking | listening | writing | passed | fallback);
  while listening `ai-mic-level` holds `[data-testid=ai-mic-wave]` (five `i`, `data-level` 0-4; `.aiv__level` is gone;
  `ai-mic-on` never on the intro); while writing: `ai-mic-writing`, `[data-testid=ai-mic-writing-line]` *Writing down
  what you said…*, *Say hello* stays, `start-talking` disabled; then `ai-mic-heard` *Heard: hello* unchanged. To catch
  the writing state: `window.__holdStop()` before the hello, `__releaseStop()` after. Test seams `window.__micTimeoutMs`,
  `__micCapMs`, `installLongMicTest` exist for frames.
- The 8 s fallback is unchanged; the stage pill still says *listening* during the send.
