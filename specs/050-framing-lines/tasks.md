# Tasks 050

- [x] T001 Fake's lines (FR-1)
- [x] T002 Walk: beat, gap, story Save, held yes (FR-2..FR-4), marks
- [x] T003 DRIFT #91 closes on S-006 (FR-6); `ai-mic-off` (FR-7)
- [x] T004 Backfill check (FR-5); `make unit`, `make eval`; counts + judgement calls here -- remote journeys on staging
  wait for keel-cloud 101 / 102 + keel-web 074 / 075 to be deployed there

## Measured (2026-10-16 / 17 UTC, stack fakes only, one fresh stack, green on the first run)

- `make unit`: **2,391 passed / 53 skipped** (2,342 / 53 after spec 049; +49: 11 framing-line source checks, 3 fake
  line tests, 21 seeded marks faults + the wait-path IM22 test, 2 remote refusals of the new reads, 10 074 / 075
  source checks).
- `make eval K="s005 or s006 or s007"`: **3 passed in 706 s** (622 s at 049: the 4.0 s gap on every spoken answer, the
  two 2 s beats and the held yes per walk, S-006's 12 s backfill), on keel-cloud-docs **`2c79e30`** (code `3a6b045`) +
  keel-web **`43cc2ee`**; S-005 290 s, S-006 273 s, S-007 126 s (`runs/20261017T000732Z-s005-countly`,
  `...T001223Z-s006-paidly`, `...T001656Z-s007-mulchrun`). `quietMs` and `beatMs` left at the page's defaults.
- Interviewer marks v4: S-005 **16 of 16** owed met (IM21, IM22 among them; IM2 / IM8 / IM10-IM12 / IM18 are the full
  leg's); S-006 **21 of 21** measured met (IM1-IM22 but IM12, unmeasured as before, DRIFT #86).
- IM21: two beats on each link, after PROBLEM then SOLUTION and nowhere else -- 2,000 / 2,002 ms (S-005), 2,002 /
  2,003 ms (S-006); the status *Take a moment.* alone, the pill *pause*, no waveform, no question, no options, no
  sheet button, 0 recognisers started and 0 recordings begun inside, then `speaking`.
- IM22: S-005 by the pause -- held 4,007 ms after the final, nothing pressed; S-006 by *Save and next* -- held 15 ms
  after the press (297 ms after the final); both: the story's status before, Save absent before a final and enabled
  after, the words on the heard line, 0 `classify`, the response's story the one said.
- IM15 (the held yes): S-005 2 turns ("yes"; "the fourth one"), S-006 1 turn ("yes") -- each `data-phase` held, the
  ring, `data-unsure` "false", then on.
- FR-1: every role's OPENING / PROBLEM / SOLUTION in 101's words (S-005 PRIMARY 3/3; S-006 PRIMARY 3/3 and
  COMMERCIAL_B2B 2/2), e.g. *"I'm Keel's interviewer. I'm an AI, not a person. Eval has an idea for a problem you may
  know. First the problem, then the idea, ..."* (the corpus founders' first name is *Eval*).
- FR-5 (S-006): 5 passages seeded in the old words (3 PRIMARY, 2 COMMERCIAL_B2B); after the first read each was one
  new DONE clip in today's words within 12 s, the old ids served by neither role's next read, READY throughout, 0
  ledger rows.
- FR-6, DRIFT #91 RESOLVED: the recorded link's pilot ask -- `transcribe` 200 "yes", `POST pilot` 204, the stored
  opt-in false -> true, a second `transcribe` 409.
- FR-7: *Microphone off* (`role=status`) after the thanks on the S-005 and S-006 AI links, and on the dry run's End
  screen; the seam's recogniser no longer listening; 0 recognisers started after the thanks clip began.
- Classifier guard, never a confident wrong: S-005 128 asked / 115 right / 13 safe / **0 wrong**; S-006 92 / 82 / 10 /
  **0** (93 / 83 / 10 at 049, D-02).

## Where things are

| Piece | Place |
|---|---|
| the framing lines | `harness/interviewer_fake.py` `opening`, `problem_passage`, `solution_close`, `before_101` (and the constants), held to `PassageComposer` by `tests/test_interviewer_marks.py` |
| the beat, the starts, mic off | `harness/interviewer_screens.py` `FLOW_TIMELINE` (`__keelBeats`), `SPEECH_SEAM` (`__speechStarts`, `__recordStarts`), `Player.beats` / `starts` / `mic_off`; `hold()` reads `data-phase` and `data-unsure` |
| the walk | `evals/interviewer_leg.py` `_Walk.story` (`story_by`), `_held_facts`, `_beats_seen`, `_mic_off_after_thanks`, `_framing_lines`, `_backfill`, `_recorded_pilot` |
| the stand-in and the read | `stack/ledger.py` `stand_in_old_words` (stand-in 4), `pilot_opt_in` |
| the marks | `evals/interviewer_marks.py` IM21 `a_beat_after_the_passages`, IM22 `the_storys_save`, IM15 `_held_yes`; `INTERVIEWER_MARKS_VERSION` 4 |

## Judgement calls decided

1. **The marks' names and the bump** (spec call 1): IM21 *a beat after the passages*, IM22 *the story's Save*;
   `INTERVIEWER_MARKS_VERSION` 3 -> 4 (IM15 reads the held yes). As 048 / 049, the corpus is **not** bumped (revision
   11, `MARKS_VERSION` 19): 101 / 102 / 074 / 075 move no screen schema and no corpus item. Both new marks are owed on
   the short form too (`SHORT_FORM`).
2. **The framing lines are a plain assertion, not a mark** (FR-1): a step after the recording is read holds every
   role's OPENING and PROBLEM whole and its SOLUTION's opening and close to the fake's composition from the interview
   that role is served (`founderFirstName`, `topic`, the parts' counts -- the gate counted in part 1, every served
   item on the decision-maker's link). The reveal's three lines between are IM4's, unchanged. The fake's constants are
   held to `PassageComposer`'s source literals (cloud-docs `3a6b045`), so a reworded line fails `make unit` first.
3. **`quietMs` and `beatMs` stay at the page's defaults** (4.0 s, 2.0 s): the three journeys took 706 s, well inside the
   matrix job's 45-minute `timeout-minutes`, so nothing is set in the init script. The walk encodes no gap length
   (049 call 6 stands); IM21
   holds the beat to at least 90 % of keel-web's `BEAT_MS` (a source check holds `BEAT_MS` == 2,000), so a seam that
   shortened it -- keel-web's own e2e fake's 200 ms -- is a failed mark, not a pass.
4. **What "nothing listens" is measured by**: the seam stamps every `start()` of a recogniser and every
   `MediaRecorder.start` (`performance.now()`, the timeline's clock); the timeline keeps each beat as drawn on every
   mutation while it lasts (statuses, pills, waveform, question, options, sheet buttons) and the clip played before
   it, mapped to its kind by the served interview's clip ids. The beat is owed after exactly the served PROBLEM and
   SOLUTION clips, in order, and is followed by `speaking`.
5. **The story** (FR-3): S-005 ends it by the pause, S-006 by *Save and next*, pressed as soon as it is drawn. "At
   once" is held as *held before the gap could have run* (final -> held under 4,000 ms) on the Save path; the wait
   path is held to "nothing pressed" and encodes no length (4,007 ms measured). The story's hold is IM22's, not IM14's
   (a press in it is the point on S-006).
6. **The held yes is measured on every "Is that right?" turn** (FR-4): the answer that settles it -- "yes", the chip,
   or the one meant by its place -- is held with `data-phase` held, the ring and `data-unsure` "false" on every lit
   row before the next question. IM15 now owes that on each turn; no new mark.
7. **FR-5 is walked, not skipped**: the stack cannot record in old words, so stand-in 4 rewrites the stored scripts of
   the opening, problem and idea clips (only `script`; ids, files, statuses, places and the project's revision kept)
   to what 094 / 099's composer said (`fake.before_101`); the first read is the founder's Try it yourself (`GET
   interviewer/try/{roleId}`, both roles) -- keel-cloud 101 call 4: the same `backfill` a stranger's link read runs --
   so no extra link is made. S-006 only (the full leg), right after the recording is read and before the dry run, so
   every page after it is served the new clips (no swap mid-walk). The record the other marks read (`recording`) is the
   one stored before the seeding.
8. **FR-6's opt-in is read off the document** (`stack.ledger.pilot_opt_in`), not `GET standings`: 049 D-03's trap (a
   standings read on Keel's keyless door starts the stale brief) still holds. A second `transcribe` after the pilot
   must be 409 -- 102's window closes on the yes.
9. **FR-7 on each link and the dry run**: asserted once on every AI link walked on screen (S-005's, S-006's) after the
   thanks, and on the dry run's End screen (075: *the dry run's too*); "after the thanks" is after the THANKS clip's
   `play`. No mark (the spec's plain assertion).
10. **FR-8 is not journeyed** (as the spec says): a clip 404 needs a swap while a page holds the old refs; the backfill
    here finishes before any page loads. keel-web 075's own e2e covers the refetch; the walk would see it only as a
    `GET interview` mid-walk.

## Discovered

- D-01 Nothing failed. The framing lines, the beat, the held yes, the story's Save, *Microphone off* and the recorded
  pilot all read as keel-cloud 101 / 102 and keel-web 074 / 075's notes for this repository say.
- D-02 Observation, not filed: S-006's classifier guard asked 92 cases where 049 asked 93 (82 right where 83); the
  guard asks what the link's own items can carry, so one case found no item on this run's link. Still 0 wrong; worth
  a look if the count keeps moving.
- D-03 The corpus founders' first name is *Eval*: the opening says *"Eval has an idea for a problem you may know."* --
  right by 101 (the served `founderFirstName`), odd to read in a run bundle.
