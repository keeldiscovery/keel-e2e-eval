# Tasks -- spec 168

Base: `origin/master` `0eede72` (167 merged, spec 168 committed). Built 2026-11-25 from 05:35 ET by a builder (Claude
Opus 5.5) in the worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-168`, branch
`168-the-lock-retried-once`. Nothing paid: no model, no key, no vendor, no stack, no pip install (the main checkout's
`.venv`, symlinked, ignored), no network but `git fetch` / `git push` of this branch. keel-cloud's retry route read with
`git show` on keel-cloud-docs `a64bde86` (read-only).

- [x] T0 Set up: the worktree's `.venv`, the base's `make unit` (the reds listed below), this file.
- [ ] T1 FR-1 the calibration retried once (`harness/film_strangers.lock_project` step 2): on `state: FAILED` the
  walk presses `POST /v2/projects/{id}/calibration/{scope}/retry` once and waits `calibration_wait_s` again;
  `record["calibration_retried"]`; a second FAILED (or the retry refused, `QUESTIONS_NOT_FAILED` aside) raises
  `LockFailed` at the same step with `retried: true`; the solution leg's lock (scope SOLUTION) through the same
  function.
- [ ] T2 FR-2 the retry recorded and tabled: `film.json` (both films) `lock.calibration_retried` and
  `measures.lock_retried` (so the score files carry it, `quality/film_reader.py` copying `measures`);
  `quality/film_table.py`: the DRIFT finding *(capture): the lock's calibration was written again on the founder's
  retry* with the film's frames, *lock retried* beside *flagged* in the entry heading; *Compared with* unchanged.
- [ ] T3 FR-3, FR-5 beat 3 (`harness/film_frames.entry_idea_beats`): *{Limit}: {name} {mechanism}.* for every
  limitation, *takes care of that* gone, `then[3]` unchanged, `idea_beat_faults` as today; the fixture's pin re-cut.
- [ ] T4 FR-4 the tests (`tests/test_the_strangers_on_the_films_link_165.py`, `tests/test_the_solution_film_judged_166.py`);
  `make unit` after; this file's sections.
