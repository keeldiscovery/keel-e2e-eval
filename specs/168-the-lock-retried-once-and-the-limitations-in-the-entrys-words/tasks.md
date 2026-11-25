# Tasks -- spec 168

Base: `origin/master` `0eede72` (167 merged, spec 168 committed). Built 2026-11-25 05:35-06:05 ET by a builder (Claude
Opus 5.5) in the worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-168`, branch
`168-the-lock-retried-once`. Nothing paid: no model, no key, no vendor, no stack, no pip install (the main checkout's
`.venv`, symlinked, ignored), no network but `git fetch` / `git push` of this branch. keel-cloud's retry route read with
`git show` on keel-cloud-docs `a64bde86` (read-only): `VectorsController.retryCalibration` (`POST
/v2/projects/{id}/calibration/{vector}/retry`, 202 `{interactionId}`), `VectorCorridorService.retryCalibration` (only
on FAILED, else `QUESTIONS_NOT_FAILED`, a 4xx `VectorRefusalBody` with `code`), `calibration()` (the retry opens an
interaction at once, so the next read is WRITING).

- [x] T0 Set up: the worktree's `.venv`, the base's `make unit` (the reds listed below), this file.
- [x] T1 FR-1 the calibration retried once (`harness/film_strangers.lock_project` step 2): on `state: FAILED` the
  walk presses `POST /v2/projects/{id}/calibration/{scope}/retry` once and waits `calibration_wait_s` again;
  `record["calibration_retried"]`; a second FAILED (or the retry refused, `QUESTIONS_NOT_FAILED` aside) raises
  `LockFailed` at the same step with `retried: true`; the solution leg's lock (scope SOLUTION) through the same
  function.
- [x] T2 FR-2 the retry recorded and tabled: `film.json` (both films) `lock.calibration_retried` and
  `measures.lock_retried` (so the score files carry it, `quality/film_reader.py` copying `measures`);
  `quality/film_table.py`: the DRIFT finding *(capture): the lock's calibration was written again on the founder's
  retry* with the film's frames, *lock retried* beside *flagged* in the entry heading; *Compared with* unchanged.
- [x] T3 FR-3, FR-5 beat 3 (`harness/film_frames.entry_idea_beats`): *{Limit}: {name} {mechanism}.* for every
  limitation, *takes care of that* gone, `then[3]` unchanged, `idea_beat_faults` as today; the fixture's pin re-cut.
- [x] T4 FR-4 the tests (`tests/test_the_strangers_on_the_films_link_165.py`, `tests/test_the_solution_film_judged_166.py`);
  `make unit` after; this file's sections.

## How each FR is met

| FR | Where | What holds |
|---|---|---|
| FR-1 | `harness/film_strangers.py`: `lock_project` step 2, `RETRY_NOT_FAILED`, `calibration_seen`, `LockFailed(record=)`, `lock_record` | the calibration's wait no longer stops on the first FAILED: it records `calibration_first` (state, total, answered), presses `POST calibration/{scope}/retry` once (`calibration_retry`: its status and code), resets the wait to `calibration_wait_s` and reads again; READY goes on to the credits; a second FAILED, or a retry refused with any code but `QUESTIONS_NOT_FAILED`, raises `LockFailed` at *the {scope} calibration (GET calibration/{scope})* with `retried: true` in its detail (a timeout with no FAILED says `retried: false`); `QUESTIONS_NOT_FAILED` lets the wait go on. `record["calibration_retried"]` is always written (false where READY the first time). Every `LockFailed` now carries the record so far. The solution leg (`run_film.solution_strangers_leg`, scope SOLUTION) calls the same function, so it presses `calibration/SOLUTION/retry` the same way |
| FR-2 | `evals/run_film.py` (`lock_retried`, `strangers_leg` / `solution_strangers_leg` `held=`, both `film.json`s); `quality/film_reader.py` (`film_measures`); `quality/film_table.py` (`LOCK_RETRIED_WHAT`, `LOCK_RETRIED_OWED`, `lock_retried_why`, `lock_retried_mark`, `findings`, `render`) | both legs hand the lock as tried (`fs.lock_record`: `locked`, `calibration`, `calibration_retried`, `calibration_first`, `calibration_retry`, `questions`, `questions_retried`, and `step` / `detail` where refused) to the film record: `film.json` `lock` and `measures.lock_retried` on the problem film and on the solution film (the strangers' `backtest.json` carries the whole lock record as before). The score file's `measures` always carries `lock_retried` true or false (an older `film.json` read from its `lock` or `strangers.lock`, else false). `make read-film-table`: a row with `measures.lock_retried` gains the finding *{entry} (capture): the lock's calibration was written again on the founder's retry -- {the film's first two frames}* (*no frame* on a solution film with none), DRIFT=1 appends it as an *Observation*; the entry heading reads *### {entry} -- the problem film, film_pct x, flagged, lock retried*; `_measures` / `compare` untouched |
| FR-3 | `harness/film_frames.py` (`limit_answer`, `entry_idea_beats`) | beat 3 = *{name} solves them like this. {steps} {output}* then, per limitation, *{Limit}: {name} {mechanism}.* -- `solution_mechanism.mechanism` through `_bare_end`, the same answer for every limitation; *takes care of that* is gone; `then[3]` unchanged. `idea_beat_faults` unchanged and clean on both fixtures and on all 28 back-test entries (read at run time, with a two-limitation stand-in story; nothing copied) |
| FR-4 | `tests/test_the_strangers_on_the_films_link_165.py` (`test_a_failed_calibration_is_retried_once_and_the_lock_goes_on`, `test_a_calibration_failed_twice_stops_the_lock_at_the_same_step_with_retried`, `test_a_refused_retry_stops_the_lock_and_one_not_failed_any_more_waits_on`, `test_a_calibration_ready_the_first_time_presses_no_retry`, `test_the_solutions_lock_presses_its_own_calibrations_retry`; the stub wire answers the retry); `tests/test_the_solution_film_judged_166.py` (the payroll pin re-cut, `test_beat_three_answers_each_limitation_with_the_entrys_mechanism_168`, `test_a_lock_retried_is_a_drift_finding_and_marked_in_the_entry_heading_168`, the score file's `measures.lock_retried`) | *make unit* below |
| FR-5 | beat 3's words | one wording, the entry's own words (no number the entry does not say, no placeholder: `idea_beat_faults` holds them), one sentence a limitation a listener follows once; no respondent-question instruction read or touched (`test_no_respondent_question_instruction_is_touched_here` green) |

**Beat 3 on the payroll fixture** (the new clauses, verbatim): *The hours come from systems that don't agree: Runsure
opens the checker, which reads the run and compares every line with last period. Nobody tells them when a rate changes:
Runsure opens the checker, which reads the run and compares every line with last period. Mistakes are found after the
money has gone: Runsure opens the checker, which reads the run and compares every line with last period.*

## Judgement calls

1. **The mechanism exactly as the entry records it.** The acceptance's example for the language learner reads *Issen
   holds a spoken conversation with an AI tutor ...*; the entry's `solution_mechanism.mechanism` opens *opens the app
   and holds a spoken conversation ...*. FR-3 says the mechanism as a bare clause, one rule for every entry, nothing
   invented -- so the walk says *A tutor is hard to schedule: Issen opens the app and holds a spoken conversation with
   an AI tutor that adapts to their level, goals and interests.* Dropping *opens the app and* would need a rule that
   cuts a mechanism's first step, which no other entry asks for and the spec does not name.
2. **A mechanism that opens on its own subject.** Ten of the 28 entries' mechanisms open on their subject, not their
   verb (*its existing security cameras ...*, *a model reads ...*, *an AI agent calls ...*); *{name} {mechanism}* would
   read *{name} its existing cameras ...*. The one rule `_steps_sentence` already uses (`_verb_first`) decides: verb
   first, *{Limit}: {name} {mechanism}.*; otherwise *{Limit}: With {name}, {mechanism}.* -- still the brand's name and
   the entry's mechanism, nothing added but the preposition. Where an entry records no mechanism, the limitation is
   said alone (no answer invented).
3. **A SOLUTION calibration with its three answered stays ready whatever its state.** 166's `calibration_ready` counts
   a spoken SOLUTION calibration with `total: 3, answered >= 3` as ready (keel-cloud 271 FR-8); kept unchanged, so the
   retry is pressed on SOLUTION where FAILED and not all three answered. Whether keel-cloud's lock accepts a
   FAILED-but-answered SOLUTION calibration is left to the lock's own press (step 4), as before.
4. **`QUESTIONS_NOT_FAILED` is not a refusal** (the spec's *aside*): the calibration left FAILED between the read and
   the press; the wait goes on and the retry counts as pressed (`calibration_retried` true, `calibration_retry` naming
   the code). Any other non-2xx refuses at the calibration step with `retried: true`.
5. **The DRIFT finding's words and owner.** *what*: the spec's words; *owed*: keel-cloud's calibration writer (the
   window-frame rules, spec 107's one repair turn); *why*: what the walk did (*GET calibration/{SCOPE} read FAILED at
   the lock; the walk pressed FounderVoice's retry ... once*). Frames: the film's first two, as the criterion findings
   take them; none on a solution film without frames. A lock that failed after its retry carries `lock_retried` too
   (the writer refused once; the refusal itself is the walk's own *owed* line).
6. **`make unit` on archived siblings.** The brief forbids touching the keel-cloud / keel-web checkouts while the
   integrator's gates run there (several unit tests run `gradlew` in the configured keel-cloud), so this worktree's
   `stack.toml` (never committed; restored) pointed at `git archive` copies in the scratchpad -- keel-cloud-docs
   `a64bde86`, keel-web `e732c7b6`, keel-runtime `3988131e`, keel-connect-skill `c6779509` -- with keel-cloud's
   `gradlew` left out (its JVM tests skip by name). The copies are not git repositories, so five tests of 165 / 166
   that read `git rev-parse` of the siblings are red on both base and head for that reason alone; they were run again
   on `git init` copies of the same trees and are green there (below).

## make unit
Both on the same archived siblings (judgement call 6), the main checkout's `.venv`, nothing else of mine running:
- Before (the base `0eede72`, before any code change; 05:36-05:43 ET): **79 failed, 6184 passed, 171 skipped**.
- After (the code of `6b5cb80` less one line; 05:49-05:58 ET): **79 failed, 6191 passed, 171 skipped -- no new red**
  (the lists diffed by name: the same 79), the seven new mirrors green. The one line after (`record["calibration"]`
  set before a refused retry raises, and its assertion) was run in the three film test files below.
- `tests/test_the_strangers_on_the_films_link_165.py`, `tests/test_the_solution_film_judged_166.py` and
  `tests/test_the_mirrors_of_263_167.py` at the head on the `git init` sibling copies: **85 passed** (the five
  git-dependent reds of the archived run among them).
- The 79 base reds: the sibling-mirror suites of earlier specs reading keel-cloud-docs `a64bde86` / keel-web `e732c7b6`
  (words and pins moved since: `test_cloud_245_250_248_web_186_190_mirror_154.py` 24, `test_seven_templates_115.py` 4,
  ...), keel-web's absent `node_modules`, and the five git-dependent tests above. None is the lock's, beat 3's or the
  table's.

## Commits
| Commit | FR | What |
|---|---|---|
| `70a5bbd` | -- | this file's T0..T4 |
| `6b5cb80` | FR-1..FR-5 | the calibration retried once, the lock record, `film.json` `lock` / `measures.lock_retried`, the score file's `lock_retried`, the DRIFT finding and the heading mark, beat 3 in the entry's words, the mirrors |
| (this commit) | FR-4 | this file: how each FR is met, the judgement calls, `make unit`, open |

## DRIFT
No new entry: no stack was run here, so no product red was met. The run on five's two refused locks (*the PROBLEM
calibration ... {'state': 'FAILED', 'total': 3, 'answered': 3}*) are the calibration writer's (keel-cloud); the next
run of record tables them as *(capture): the lock's calibration was written again on the founder's retry* where the
retry passes, and as the lock's refusal (now with `retried: true`) where it does not.

## Open
- **The acceptance on a stack** (*a calibration writer that fails once and passes on the retry, the link sent, the
  strangers walk, the table's mark and the DRIFT finding*) is held here by the unit mirrors only: the fakes do not fail
  the calibration writer, so `DOOR=fake` would not press the retry. The next run on Keel's door (paid, the founder's
  word) is where it is met.
- The language learner's beat 3 says *Issen opens the app and holds ...*, not the acceptance's *Issen holds ...*
  (judgement call 1); if the shorter form is wanted, it is a rule on the entry's mechanism (or the entry's words), to
  be named in a spec.
- Whether a FAILED SOLUTION calibration with its three answered should also be retried (judgement call 3) waits on
  keel-cloud's answer to what that state means at the lock.
- The branch is on `0eede72`; `origin/master` has moved to `8fc1274` (the judge's run on five: `quality/FILM-TABLE.md`,
  `quality/cycles/`, `quality/scores/`, `runs/DRIFT.md`) -- none of this branch's files; the merge is the integrator's.
