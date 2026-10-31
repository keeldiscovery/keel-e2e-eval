# Tasks 099 -- The interviewer marks read the ear's three states: *Listening…*, *Writing down what you said…*, the words

Branch `099-the-marks-read-writing-down` (worktree `wt/keel-e2e-eval-099`, its own `make venv`), off master `cd03a7e`
(111's docs). Built by Claude on 2026-10-30. Read only: keel-web at `1d83a28` (143 merged: `MicWave.tsx`, `Sheet.tsx`'s
`heardLineOf`, `AiIntro.tsx`'s `MicBlock`, `src/lib/micCheck.ts`, `translate.ts`, `tests/fixtures/interviewer/
fakeSpeech.ts`), keel-cloud-docs at `2edd98bf`. **No stack, no browser beyond the unit tests' local Chromium, no model,
no paid call.** Nothing merged into master; the branch pushed after every commit, never force-pushed.

| Commit | What |
|---|---|
| `d74063a` | FR-1: the selector pin reads 143's expression form (`_builds_testid`); master's one failure cleared |
| `93a23f2` | FR-1 / FR-2: the walker samples the heard line (`__keelHeard`, `Player.heard_lines`); `mic_test` holds the writing state |
| `dc55edb` | FR-1 / FR-2 / FR-3: `heard_windows`, IM19 and IM17 re-read, v17; the pins, the seeded faults, `tests/test_heard_line_099.py` |
| the docs commit | this file and `AGENTS.md`'s spec-099 paragraph |

## Unit (the gate)

| | passed | failed | skipped |
|---|---|---|---|
| master `cd03a7e`, keel-web `1d83a28`, keel-cloud-docs `2edd98bf` (111's count) | 4,255 | 1 | 56 |
| **branch at `dc55edb` (the last code; the docs commit adds none), the same siblings** | **4,294** | **0** | **56** |

+39 passed: the one failure now passing (`test_the_mic_and_beat_selectors_are_in_keel_web[ai-mic-on]`), one new pin test,
18 seeded IM17 / IM19 faults in `tests/test_interviewer_marks.py`, and `tests/test_heard_line_099.py`'s 19. None
removed. (A baseline run started while the harness was being edited showed three more failures -- `inspect.getsource`
pins reading a file that changed under them; the clean run above has none.)

## The checklist

- [x] T001 **The selector pin** (FR-1, `tests/test_interviewer_screens.py`): `_builds_testid` accepts a literal
  `data-testid="…"`, a quoted arm of a `data-testid={…}` expression (143's `MicWave`: `writing ? "ai-mic-writing" :
  (testId ?? "ai-mic-on")`) and a `testId="…"` prop (Test your mic's `ai-mic-wave`); a word that only names the id
  elsewhere is not one (`test_the_testid_pin_reads_a_literal_an_expression_and_a_prop`).
- [x] T002 **The words** (FR-1): `evals/interviewer_marks.py` `LISTENING_LINE` *Listening…*, `HEARD_WRITING_DOWN`
  *Writing down what you said…*, `HEARD_NOTHING` *Heard so far: nothing yet*; `harness/interviewer_screens.py`
  `HEARD_LISTENING`, `HEARD_WRITING_DOWN`, `HEARD_NOTHING`, `HEARD_STATES`. Held to `translate.ts`'s
  `AI_HEARD_LISTENING` / `AI_HEARD_WRITING_DOWN` / `AI_HEARD_NOTHING` and `Sheet.tsx`'s `data-heard` union.
- [x] T003 **The walker samples the heard line through the send** (FR-1): `FLOW_TIMELINE` keeps every change of
  `[data-testid=ai-sheet] [data-testid=ai-heard]` -- its `data-heard` (None when not drawn), its words and the question
  above it -- on the same MutationObserver that keeps the status; `window.__keelHeard()`, `Player.heard_lines()`. The
  stranger's walk (`evals/interviewer_leg.py`) puts it on `record["hear_out"]["heard_lines"]`. `Player.say`'s `still`
  accepts *Writing down what you said…* beside *Hearing you…*.
- [x] T004 **The recorded windows** (FR-1): `heard_windows(lines)` cuts the timeline into windows -- open at `hearing`,
  closed at `words`; the line gone, back to `listening` or under another question closes one unread. Faults: words with
  no `writing` before them; `nothing` straight after a sound; `nothing` then the words with no new window between (the
  old *nothing yet* through the send). `nothing` straight after `writing` is an empty transcript and closes the window.
- [x] T005 **IM19** (FR-1, `hears_them_out`): the first words' heard line may be *Hearing you…* or *Writing down what
  you said…*; at least one window read and no heard-line fault; the detail names `windows read` and `heard line
  faults`.
- [x] T006 **IM17** (FR-2, `mic_tested`): `Player.mic_test` reads the block once it listens (`mic_block`: the state,
  the wave inside `ai-mic-level` -- `ai-mic-wave`, five `i`, `data-level` -- the retired `.aiv__level`, any `ai-mic-on`
  on the intro, the writing line, *Say hello*, the heard line, Start), then calls `__holdStop()` before the hello, reads
  the `writing` block, and `__releaseStop()` (in a `finally`), well inside the 8 s fallback. The mark owes listening
  (`ai-mic-wave`, 5 bars, level 0-4, no meter, no `ai-mic-on`, Start disabled) and writing (`ai-mic-writing` held, the
  line *Writing down what you said…*, *Say hello* kept, nothing heard, Start disabled); `start_enabled` and the
  fallback as before.
- [x] T007 **The version** (FR-3): `INTERVIEWER_MARKS_VERSION` 16 -> 17 with its `#: v17` note (the live `make eval-live
  K=s012` re-run named as the founder's call); the six `== 16` pins re-pinned to 17 with why (`test_interviewer_marks`,
  `test_recorded_path_074`, `test_im2_staging_switch_094`, `test_controls_089`, `test_draft_list_minimum_091`,
  `test_founder_walk_076`).
- [x] T008 **Tests**: `good()` carries the listening / writing blocks and a heard-line timeline of two windows (one an
  empty transcript said again); 13 seeded IM17 and 5 IM19 faults; `tests/test_heard_line_099.py` (19): the words and
  ids from keel-web 143's source (and that `micCheck` draws `writing` before `await recorder.stop()`, so a held stop
  keeps it on screen), `heard_windows`' cases, the timeline sampled in Chromium, `Player.mic_test` against a page shaped
  as 143's `MicBlock` over the harness's own `SPEECH_SEAM` (the held stop read, IM17 met on the result), the version.
- [ ] `make eval K=s005` on the local stack at keel-web 143 (the spec's acceptance): **not run** -- this build brings no
  stack up (the brief's rule); it is the coordinator's step.

## Where the spec and the code differ (the code's patterns followed)

- **`WRITING_DOWN` is taken.** FR-1 names the new words `WRITING_DOWN`; that constant already holds the status line's
  *Writing it down…* (IM26's speak-or-type box reads it, and the addendum says the harness's `WRITING_DOWN` still reads
  it). Keel-web 143 met the same clash with `AI_HEARD_WRITING_DOWN`; the marks follow: `HEARD_WRITING_DOWN`.
- **The walker is `harness/interviewer_screens.py`** (the spec's name), not `vectors_screens.py`: the AI link's walk and
  `mic_test()` live in `Player`; `vectors_screens.py` only waits for `ai-mic-on` on the text page's card, which 143 kept.
- **The new check lives in IM19, not a new mark.** FR-1 attaches it to the recorded-path mark and FR-4 moves nothing
  else, so the mark count stays 30 and the check is IM19's extra condition; a v16 record (no `heard_lines`) is measured
  and fails it.
- **IM17's `ai-mic-level` is read as the wave's holder.** FR-2 says *`ai-mic-level` wrapping `MicWave`'s bars*; while
  writing, `MicWave` swaps `ai-mic-wave` for `ai-mic-writing` (its `writing` arm wins over `testId`), so the writing
  block owes `ai-mic-writing` inside `ai-mic-level`, as the addendum says.

## What the spec did not foresee

- `micCheck`'s 8 s fallback timer is started at `listening` and not cleared on `writing`, so a stop held past it would
  fall back; `mic_test` releases as soon as the writing block is read (a few hundred ms).
- The story / follow-up windows that end on *Save and next* may move to the next question in the same render as the
  words; `heard_windows` then closes that window unread (no fault, not counted) -- IM19 needs only one window read and
  the read-aloud question always draws its words under its own question.
