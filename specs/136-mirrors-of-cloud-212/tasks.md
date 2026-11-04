# Tasks 136 -- Mirrors of keel-cloud 212

Branch `spec-136`, off `786ab2e`, in the worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-136` (`.git` a
file). Built 2026-11-04 (ET) against keel-cloud-docs master `55bf014d` (212 merged). Plan: `plan.md` (seven judgement
calls). Not merged; nothing paid (no quality-walk, advise, remote journey, instruction screen or `claude -p`); no corpus
revision, `MARKS_VERSION` or contract moved.

| Commit | What |
|---|---|
| `59e7835` | plan.md, tasks.md (written, not built) |
| `7b3aaac` | FR-1: the cards, the 115 slice pin |
| `358359c` | FR-2: the mirrors, the instruction fixtures' good answers, the pins that read them |
| `3db0ebc` | FR-3: the scripted results, the re-pins |
| `9775de0` | FR-4 and the mirror's tests (`tests/test_cloud_212_mirror_136.py`, 30) |
| this commit | these tasks |

## FR-1 The cards

- [x] T001 `quality/readers/dimensions.md`: the two *One clause (keel-cloud 212)* bullets, byte for byte as the vendored
  copy carries them; the eval's cards now differ from keel-cloud's only by spec 135's pointer, so the 133 pin holds at
  `CARDS_SHA256` `877a5d80...` (its docstring names it).
- [x] T002 `tests/test_seven_templates_115.py`: `FREQUENCY_GUIDANCE_212` (212's Frequency founder guidance), 205's kept and
  held unequal to it by the new test.

## FR-2 The instruction mirrors

- [x] T003 `instructions/wording.py`: `event_max_words(window)` (`WindowFrame.eventMaxWords`: 9 on nights, days, weeks,
  months; 8 on working days), `CLAUSE_MAX_WORDS` 25 (`EVENT_MAX_WORDS` gone, as in the Java), `event_fault(event, window,
  max_words=None)` with Java's E2 message, `packed_fault` (E8), `routine_fault` (E7) with `base_of` / `_based`
  (`WindowFrame.baseOf`, `based`), `SETTLED_BY`.
- [x] T004 `instructions/score.py`: `act_that_hurts` (the missing fields, E7, E8) and E2 at the window's cap in
  `calibration_checks` (`actor_plural` off the sent context, else the entry's); `settled_faults` (L35) in `list_faults`
  on Compatibility; `respondent_checks(..., founders=)` -- with the founder's clause the gate is its key alone and an
  `event` is `E10`, with `problem` null the writer's clause keeps E1-E4 at `CLAUSE_MAX_WORDS`; `score_respondent` reads
  `problem` off the sent context, else `context.problem_of` (`_founders_clause`). `instructions/screen_entries.py`: the
  respondent probe's clause at `CLAUSE_MAX_WORDS`.
- [x] T005 Pins: `test_instruction_window_frame` (E1-E3 read at `CLAUSE_MAX_WORDS`; new: the cap by window),
  `test_instruction_score` (Lullaby's drafted conditions settled by nobody; the gate's rules on a study with `problem`
  null; new: the gate its key alone, E10, E2).

## FR-3 The scripted results

- [x] T006 `harness/vectors_script.py`: `ACT_THAT_HURTS` / `act_that_hurts` (`routine`, `went_wrong`: the golden seven's
  own; elsewhere the context's job and `event_past`); `calibration_question` writes both beside `event`;
  `PROBLEM_CLAUSES` cut to the window's cap where they ran over (01 *by hand*, 02 *by hand*, 04 *or from*, 05 *to be
  paid*, 07 *for a job* off; 03 and 06 stand), the strangers' clause the founder's in the second person; every
  Compatibility row `settled_by: nobody` (`drafted_list`); `respondent_item` writes no gate `event` where `gate_counts`.
  Re-pins: `test_lock_frontier_110` (Countly's clause), `test_referee_follows_193_123` (Paidly's pair),
  `test_vectors_journey` (the gate its key alone where the problem is in scope).
- [x] T007 `tests/v9_fixtures.py`: Prevalence's good answer carries `ROUTINE` / `WENT_WRONG`, the conditions
  `settled_by: nobody`, the gate `event` only where `problem_of` gives none.
- [x] T007a The contract export: nothing vendored in this repository (plan.md call 1); the run-time export reads 212's.

## FR-4 The fourteen's clauses

- [x] T008 `tests/test_cloud_212_mirror_136.py`: the golden seven fit; the gallery's fourteen are all over the cap --
  `event_past` writes *had a time when {circumstance}* for a back-test entry, which records no founder clause -- pinned
  as findings `(words, cap)`: 08-fresco 23/8, 09-karsa 16/9, 10-palus 17/9, 11-issen 11/9, 12-transload 14/8,
  13-aircaps 17/9, 14-code-four 21/9, 15-voltair 24/9, 16-pairio 18/8, 17-expanse 22/8, 18-careforce 20/8, 19-veles
  21/9, 20-lemma 19/8, 21-codyco 24/9. Beyond the cap, these stand-ins also fail E1 (08, 15, 18, 21: *day's*, *one*)
  and E8 (09 *left*, 13 *too noisy to*) -- for the next corpus revision to record `routine`, `went_wrong` and `event`.

## FR-5 Gate

- [x] T009 `set -o pipefail; make unit 2>&1 | tail -1` at `9775de0` (the tree this commit adds only this file to),
  against keel-cloud-docs `55bf014d`: **5,392 passed / 0 failed / 85 skipped** (268.65 s). Master `786ab2e` on the same
  sibling: 5,354 passed / 2 failed / 85 skipped (the two pins the spec names). +38 = 30 new in
  `test_cloud_212_mirror_136.py`, 5 in `test_instruction_window_frame` (the cap by window), 1 in
  `test_instruction_score`, and the two red pins green.

## Left open

- keel-cloud's vendored card (and so ours) says the event is *at most 8 words*; the code (212 FR-3 as amended) caps it at
  9, 8 on working days. The card's line is the cloud's to move (with `CARDS_SHA256`), then ours by its own spec.
- `L36`, `K11`, `Y7` (the served Compatibility question's grammar guard) are not mirrored (plan.md call 6).
- The gallery's founder clauses (FR-4's findings) wait on a corpus revision and the founder's word.
