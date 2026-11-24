# Tasks -- spec 163

Base: `origin/master` (161 merged; 162 may be beside). Built by a builder (Claude Opus 5.5) in the worktree
`/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-163`, branch `163-the-film-judged`, once keel-cloud 273 and
keel-web 261 are merged. Nothing paid: no model, no key, no pip install (the main checkout's `.venv`), no network but
`git fetch` / `git push` of this branch; the local stack with `FakePictures` allowed. Push after every commit.

- [ ] T1 FR-1 `quality/FILM-RUBRIC.md`, `quality/film_rubric.py`, `FILM_RUBRIC_VERSION`, the weak rule.
- [ ] T2 FR-2 `make film-walk`: the PROBLEM back-test with no people, the frames at two viewports, the story, the
  pictures, the prompts and the setting in the bundle, the ledger read.
- [ ] T3 FR-3, FR-4 the film reader through the API with vision (`quality/readers/film-reader.md`, `[film_reader]`),
  the score file, `make read-films`, `make read-film-table`, `FILM-TABLE.md`, the record.
- [ ] T4 FR-5, FR-6 `[film] holdout`, `ENTRIES=holdout`, `make film-advise`.
- [ ] T5 FR-7, FR-8 the unit mirrors and fixtures, the report section, DRIFT; `make unit`; the local walk; this file.

## Versions
- FILM_RUBRIC_VERSION: 1. Contract read: 89.

## Runs
| run | result |
|---|---|

## Commits
| Commit | FR | What |
|---|---|---|

## Judgement calls
