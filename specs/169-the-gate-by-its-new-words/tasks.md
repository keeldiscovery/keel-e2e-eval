# Tasks -- spec 169

Base: `origin/master` `9fa2d6f` (168 merged at `12e7804`, spec 169 committed). Built 2026-11-25 by a builder (Claude
Opus 5.5) in the worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-169`, branch
`169-the-gate-by-its-new-words`. Nothing paid: no model, no key, no vendor, no stack, no pip install (the main
checkout's `.venv`, symlinked, ignored), no network but `git fetch` / `git push` of this branch. keel-cloud 277's words
read from its spec (`keel-cloud-docs/specs/277-have-you-encountered-this-issue/spec.md`, read-only; the cloud build is
not on master yet): `story_gate` = *In {window}, have you encountered this issue?*, `{window}` filled by code
(*the last month*, *the last 7 days*), the same words on the solution link's uncounted check.

- [ ] T0 Set up: the worktree's `.venv`, the base's `make unit` (the reds listed below), this file.
- [ ] T1 FR-1 the gate found by its new words: `harness/three_surfaces.py` `GATE_WORDS` a case-insensitive regex on
  *have you encountered this issue?* with any window before it, the question mark optional, and `is_gate_words` /
  `gate_found`; `harness/interviewer_screens.py` and `evals/three_views_strangers.py` `GATE_WORDS` the same match;
  the readers (`evals/three_views_strangers.py`'s wire checks of the gate and the anchor, `harness/solution_surfaces
  .link_faults`' check) and the walks (the orb / face walk `link_walk`, the text walk `story_screens.StoryLinkText`)
  find the gate by that match; the strangers' plan answers it by `recency` as today; the one-script check (269 FR-8)
  compares the three surfaces' gate words to each other; the old words match nowhere.
- [ ] T2 FR-2 `quality/FILM-RUBRIC.md` (F7) and `quality/CYCLE.md` quote the new words; no criterion moves,
  `FILM_RUBRIC_VERSION` stays 1; 168's DRIFT finding unchanged in code, `CYCLE.md` saying it is now a capture note on
  a study with no film only.
- [ ] T3 FR-3, FR-4 the tests (`tests/test_the_strangers_on_the_films_link_165.py`, the surfaces tests, the solution
  tests): *In the last month, have you encountered this issue?* found and answered, the old words not; 168's
  READY-first test unchanged; `make unit` after; nothing here writes respondent words; this file's sections.
