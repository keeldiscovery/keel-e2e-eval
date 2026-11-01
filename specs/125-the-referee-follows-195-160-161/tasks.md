# Tasks 125 -- The referee follows keel-cloud 195 and keel-web 160 / 161

Branch `123-the-referee-follows-193` (the one branch for 123-125; worktree `wt/keel-e2e-eval-123`), on spec 124's commit
`9b02499`. Built by a builder (Claude, on the coordinator's brief) on 2026-11-01. Read only: keel-cloud-docs master
`2d848360` (195's tasks.md, `domain/vectors/Spelling.java`, `LeakStems.vocabulary`'s four-argument form,
`VectorCorridor.typedProblemTexts`, `FounderWords.droppedAsSpelt`, `Qualifiers.sameQualifier`,
`CommercialChain.sameWords`) and keel-web master `2b84758` (160's and 161's tasks.md, *Owed elsewhere*;
`src/lib/brandPlate.ts`). **No stack, no model, no paid call, no key read.** Nothing merged; the branch pushed after the
spec's commit.

## FR-1 -- spelling corrected, words kept (keel-cloud 195)

- [x] T001 New `instructions/spelling.py`: `same_word`, `in_text`, `run_in`, `words`, `allowed`, `distance` --
  `Spelling.java` word for word: case-folded; equal, or both at least four letters, no digit in either, **the same first
  letter**, within the optimal-string-alignment distance the shorter allows (1 at four letters, 2 from five); under four
  letters exact only.
- [x] T002 `no_leak`'s vocabulary (`corpus.Entry.vocabulary`, call 44a): the problem texts still subtracted exactly, and
  now also every stem `same_word` a stem of the founder's typed problem texts (`Entry.typed_problem_texts`: the four
  typed context fields and the problem seed, `VectorCorridor.typedProblemTexts`).
- [x] T003 Beside it, the two other mirrors keel-cloud 195 routed (see *Not foreseen* 1): `chain._same_words`
  (`CommercialChain.sameWords`, word by word, the same count) and `harness/qualifiers.dropped(..., spelt=True)` /
  `dropped_as_spelt` under `same_qualifier` (the founder's part spelling aside; `in_core`'s model-to-model read exact).
  No mark number moves: `MARKS_VERSION` 24 stands.

| Where | Was | Now |
|---|---|---|
| a typed *erros* beside a mechanism's *errors* | *error* in the leak list | subtracted |
| a typed *mistakes* beside *errors* | *error* in the leak list | still in it |
| the founder's loss *late shipmnts* beside the base *late shipments* | two phrases (the loss line printed) | one phrase |
| the founder's *withot a payrol buerau* against a condition *without a payroll bureau* | qualifier lost | kept |

## FR-2 -- the condition heard before it is answered (keel-web 160)

- [x] T004 `interviewer_leg._Walk.screener` is `vs_screens.screener_of(interview)` on every kind: the decision-maker's
  AI link asks its screener after the opening (it asked none from keel-web 127 to 159).
- [x] T005 `wait_condition_clip(player, clips.condition)`: on the condition step the walk waits for the clip's `play`
  (the stage's `data-clip`, the timeline) and the window after it, then says Yes / No; the step and the play are kept
  (`condition_seen`, the entry's `condition_clip`). With no clip served (a lock from before 194) nothing is waited for.
- [x] T006 `ai_question_count(interview)`: one for the condition, one for the gate, every item (keel-web
  `questionCount`); the AI walk holds the intro's heading to it exactly (*Daphne will ask you N questions.*), the
  condition *Question 1 of N*.

## FR-3 -- the brand plate (keel-web 161)

- [x] T007 `Corridor.brand_plate()` reads `[data-testid=brand-plate]`: drawn, `brand-plate-mark`, `brand-plate-line` (its
  `textContent` whole), anything focusable inside; `idea_check` reads it before the name is typed and once named.
- [x] T008 `vs_screens.brand_plate_faults(plate, typed, whatItIs)`: none before the name; once named the mark is the name
  as typed and the line `vs.idea_card(vs.idea_name_of(name), whatItIs)` (`IdeaLines.card(nameOf, whatIs)`, which
  `plateOf` ports); nothing focusable. Held by the founder's walk on S2 (`corpus_scenario._hold_the_brand_plate`) and on
  money alone's idea card (`scope_journey`).
- [x] T009 The stranger's line read whole: `_line_text` (`textContent`, whitespace folded) for `.iv-ideacard__what`, and
  `idea_mark` for `[data-testid=idea-mark]` (None on a bare *Imagine Fresco.*); the item screen records both.

## Tests

- New `tests/test_spelling_and_the_plate_125.py` (16): the founder's examples, the thresholds and digits, the
  first-letter guard (*apps/maps*, *device/advice*, *night/light*, *four/your*), `in_text` / `run_in` / `words`, the
  port read against `Spelling.java`; the vocabulary less the typed *erros* (not *mistakes*); `MARKS_VERSION` 24;
  `_same_words` and `dropped_as_spelt`; the condition clip waited for (and not, on a lock from before 194, and a clip
  that never plays stops the walk); the decision-maker's screener and the count; the plate read off a page and held;
  the stranger's line read whole around its mark (one text node never the line).
- Re-pinned: `tests/test_read_back_mirror_085.py::test_the_draw_mirror_reads_the_clouds_sources` (Qualifiers' founder
  read now `droppedAsSpelt`, the core's exact); `tests/test_money_link_screener_100.py::
  test_the_ai_walk_asks_the_screener_the_link_serves` (the decision-maker's AI link asks its screener, keel-web 160 T005).

## Gate

`set -o pipefail; make unit 2>&1 | tail -1` on the final tree against keel-cloud-docs `2d848360` and keel-web
`2b84758`, 17:11:44-17:15:43 ET (exit 0):

`4917 passed, 54 skipped in 238.71s (0:03:58)` -- **0 failed, 0 errors**.

The run before it (17:07:28-17:11:27 ET) failed one test, `test_money_link_screener_100::
test_the_ai_walk_asks_the_screener_the_link_serves[served3-want3]` (keel-web 145's *the decision-maker's AI link asks
none*), re-pinned below.

(Master `39a9ccb` in the worktree before spec 123: 154 failed, 4,717 passed, 55 skipped, 2 errors.)

## Not foreseen

1. **"`no_leak` is the only caller today" did not hold.** keel-cloud 195 also routed `CommercialChain.sameWords` and
   `Qualifiers.sameQualifier` through `Spelling`, both of which the eval mirrors, and `test_read_back_mirror_085` failed
   on the moved source line. Both mirrors now follow (a loss line typed misspelt is the base; the founder's qualifier is
   kept spelt right).
2. **The subtraction reaches dictionary neighbours the first-letter guard lets through.** At `2d848360` the typed-word
   subtraction takes a stem off 11 entries' leak lists: 08 *task* (typed *talk*), 09 *amount* (*account*), 11 *adapt*
   (*adult*), 14 *read* (*road*), 15 *along* (*aging*), 20 *chain* (*chang*), 23 *connect* (*collect*), 24 *found*
   (*founder*), 25 *estimat* (*estimator*) and *labor* (*later*), 26 *clon* (*clos*), 31 *plac* (*plan*). The mirror is
   faithful -- keel-cloud's `LeakStems` does the same on the same stems -- so it is recorded here and owed to keel-cloud
   as a finding, not changed.
3. **The plate is held strictly**: a page from before keel-web 161 would fail S2's plate step; the referee pins keel-web
   `2b84758`.
4. **The heading's count is now held exactly** (it was a prefix): keel-web 160's `questionCount` counts the condition
   whether or not its clip was recorded, so a lock from before 194 is held to the same N.

## Owed elsewhere

- keel-cloud: (finding) the leak vocabulary's spelling-aside subtraction drops real words a letter or two from a typed
  word (*task* by *talk*, *read* by *road*, *chain* by *change*) -- a stem-level guard (e.g. only stems the typed word
  does not already share exactly, or a minimum length of five) is the cloud's to decide. Optional: serve `name` beside
  `what` on `Reveal` / `Idea` (keel-web 161 J-2), which the harness would then read as the mark.
- keel-web: nothing.
- The coordinator: the next quality cycle's AI walk on a re-locked payroll link hears the condition and answers it (the
  walk now waits for the clip); a founder's walk sees the plate.
