# Tasks -- spec 165

Base: `origin/master` (163 merged at 1d427cc; 164 merged beside at abf3ecb, which this branch is cut from). Builder worktree
`/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-165`, branch `165-the-strangers-on-the-films-link`. Nothing paid:
no model, no key, no pip install (the main checkout's `.venv`), no network but `git fetch` / `git push`; the local stack
on keel-cloud's fakes, `FakePictures`, the fake transcriber and the founder's scripted runtime.

- [x] T1 FR-1 the lock, the link, the seven people on the film's link.
- [x] T2 FR-2, FR-3 the reads and the table on the one project.
- [x] T3 FR-4 the unit mirrors; the local walk; this file.

## How each FR is met

| FR | Where |
|---|---|
| FR-1 | `evals/run_film.py` (`strangers_leg`, after the capture, on the same project): `harness/film_strangers.lock_project` -- the window (`PUT context/window`, the entry's `recall_window` on Keel's door), the PROBLEM calibration READY, the credits (`GET /v2/me`, a short balance topped to the grant by `ledger.stand_in_balance`), the ready page's lock (`press_on_the_ready_page`: `define/ready/interviewer`, a guide sheet passed by, `three_views.press_lock`), the questions READY (a FAILED set retried once on `questionnaire/retry`); then `people_plans` over `vectors_script.person_inputs` (the PROBLEM scope, `people_cap` = `KEEL_FILM_PEOPLE`, `quality/cycle.toml`'s seven when unsaid: the first seven own-link people in corpus order), `walk_people` (`three_views_strangers.make_links` -- one TEXT link a person on `invitations/batch`, the orb -- then `read_served` and `walk_link` with each person's plan: the screener by `in_segment`, the gate by `recency`, their story, a recorded chip tapped, Frequency by their code, Importance by their first code (`importance_pick`: `own` the own row, `rival_<k>` the k-th other row), every why in their own recorded words where the file has them). `make film-walk` runs no back-test (`quality/film.plan_steps`: the film leg with `PEOPLE=` / `TYPOS=`, then on Keel's door `read-screens` on its bundle); `TYPOS=1` types the founder's beats on Keel's door (`typed_beats`, spec 126's typist) |
| FR-2 | `film_strangers.founder_page_after`: the themes and the ways let settle, `backtest.answers_leg` (the stage page, every card opened, the Insights screen and folds -- §B's screens) and spec 164's `founder_page_on_screen` (the ways panel, Frequency's card, the Insights boxes, the brief's breakdown) kept as checks; `screens_bundle` writes `backtest.json` (`kind: "film"`, the one `project_id`, no founder screen, `respondents` = the watched person's drawn screens on the film link -- the screener with its served spoken form where served, the gate, the experience, each item, each why, the pilot ask -- every walk's summary, the after screens, the brief) in the leg's evidence folder; `film.json` names it (`screens_bundle`); `quality/readers.py` reads a `kind: "film"` bundle with no founder screen (no founder flow; the score file names `project_id`); `walk.json` names `project_id`, `screens_bundle`, `screens`, `people`, `answered`, the score file, a lock's `refused` |
| FR-3 | `quality/film_table.py`: `projects_of` (the entry's screens bundle and project from `walk.json`; a row naming only a `backtest` -- 163's typed project -- is left out, `typed_rows` names it in the record), `question_scores` (a score file is taken only for that bundle and, where it names one, that project; §A = the strangers' screens and §G, never a founder screen); the record says *the film's project* with each entry's project id |
| FR-4 | `tests/test_the_strangers_on_the_films_link_165.py` (28, an invented study): the people's mapping, Importance's pick by code, the walk plan, the window; the lock step by step and each failing step named (`LockFailed`: *the film's project did not lock at {step}*), the top-up and the retry; the walked rows as the reader's screens; a walk's shape and a remapped chip; the screener's spoken form; read-screens on a film bundle (and its refusals); the typed beats; the walk with no back-test step, `walk.json` naming the project, a refused lock reading nothing; the leg's `PEOPLE` / `TYPOS`; the table from the film's project alone and its record; the free walk's runtime scripts. `tests/test_the_film_judged_163.py`: two mirrors moved (the walk's steps; §A on the strangers' screens). The walk on the local stack: *Runs* |

## Runs

| run | result |
|---|---|
| `make unit` before (2026-11-24 18:32-18:39 ET, base `abf3ecb`, the default stack.toml siblings: keel-cloud-docs `b48e1f49`, keel-web `7c98d472`) | 96 failed, 6,099 passed, 137 skipped -- the siblings' moved words (none this spec's) |
| `make unit` after (19:06 ET, `d90496c`, the same siblings) | 96 failed, **6,127 passed**, 137 skipped -- the same 96 reds by name (the lists diffed: identical), the 28 of `tests/test_the_strangers_on_the_films_link_165.py` green |
| local walk 1 (18:45 ET; keel-cloud `b48e1f49`, keel-web `7c98d472` from detached worktrees `wt/keel-cloud-eval-165`, `wt/keel-web-eval-165`; the stack booted by the leg and torn down) | `runs/20261124T234553Z-film-walk`: the film captured (14 frames, 8 pictures, 0 faults); then **refused by name**: *the film's project did not lock at the PROBLEM calibration (GET calibration/PROBLEM) -- {'state': 'FAILED'}* -- the free founder was on Keel's door, which on a keyless stack answers only `fake-for`'s seams (judgement call 1) |
| local walk 2 (18:49-18:56 ET) | `runs/20261124T234951Z-film-walk`: **7 of 7 answered on the film's link** (project `cfea2160`) -- found: the screener's spoken form not kept, a recorded chip the link does not draw (both handled since) |
| local walk 3a (18:57 ET) | stopped at the lock: a guide sheet's scrim over the ready page took the click (harness; passed by since, `d90496c`) |
| **local walk 3, of record** (18:59-19:05 ET) | `runs/20261124T235945Z-film-walk` (`make film-walk ENTRIES=08-fresco DOOR=fake`), screens bundle `runs/20261124T235958Z-film-08-fresco`: **one project** `366140d0-b326-4eff-b9b1-31fc155567e4` in `walk.json`; the film 14 frames, 8 pictures, 0 capture faults; the lock 201, the questions READY (written on her own door after one retry); **seven responses on its link, all 201, each person shown the film first, then the four questions**: five yes-sayers with a story, Frequency and Importance (two on the own row: no why; two not: Importance's why in their own words), one whose recorded chip is not drawn tapped *I can't recall* (`anchorChip` CANT_RECALL, no answers -- the chip ends the interview; `chip_remapped`), one No-sayer (`recency: false`, Prevalence's why on the spot, Importance, its why); **the founder's page read after them**: the stage page, the three cards opened, the Insights screen (Importance 3 quotes, Prevalence 1, both GROUPED; the ways GROUPED), spec 164's four reads all held (the ways panel, Frequency's card, the Insights boxes, the breakdown) |
| `make read-screens RUN=<walk 3's screens bundle> DRY=1` | 12 prompts, nothing called: 5 founder screens after the answers (§B), 5 stranger screens on the film link (screener, gate, the experience, Frequency, Importance), the link's whole-flow, 1 insight line |

## Commits

| Commit | FR | What |
|---|---|---|
| `455b039` | FR-1..FR-4 | the strangers' machinery, the leg, the walk with no back-test, read-screens on a film bundle, the table from the film's project, the mirrors |
| `afadb58` | FR-1, FR-2 | the free founder on her own AI; the lock bought by a stand-in; the groupings and the ways handed; the screener's spoken form; a remapped chip named |
| `d90496c` | FR-1 | the ready page's guide sheet passed by |
| (this commit) | -- | this file |

## Judgement calls

1. **The free walk's founder is on her own AI** (`DOOR=fake`). The eval stack has no key: Keel's door answers a `fake-for`
   founder's story readings, pictures, voice and transcriber, but not the calibration, the questions, the stories'
   readings or the groupings (walk 1 was refused at the calibration). So on the fakes the leg opens a
   `three_views.Run` -- e2e-157's founder through the code story with the scripted runtime -- and the film, the lock and
   the people all run on that founder; the lock is bought on Keel's door by `stand_in_keels_door` and the door given
   back so the questions are written on her own (`three_views.lock_once`'s way); before the people walk the runtime
   reads every story ANCHORED; after them it is handed `THEMES` (one theme a rung, every text said on it, labelled from
   its first words) and `EXPERIENCE_WAYS` (every story under the founder's act). Keel's door (`DOOR=keel`, paid) is
   unchanged: Keel's AI answers everything and the credits are the grant's (topped once by a stand-in when short).
2. **The window**: the entry's `recall_window` on Keel's door; on the fakes the fake script's (7 nights), since the free
   film tells the script's story (163's judgement call 3) -- the free walk's questions are the script's words.
3. **One person a link is read** (`respondents`, the first in segment with a story said and no chip), as every back-test
   is read; all seven walks are kept in the bundle (`walks`). Reading all seven would multiply the read's dollars by
   seven for screens that differ only in the whys.
4. **A recorded chip the film link does not draw** (the corpus's *rather not say*; the link draws one chip, *I can't
   recall*) is tapped as the one chip drawn and named on the walk (`chip_remapped`), spec 064 FR-7's rule.
5. **Importance's second ask** is left to `link_walk` (*Nothing else*): one pick a person, the corpus's first, as 161's
   roster walks it.
6. **The film is not a respondent screen** for read-screens: the film reader judges it (`make read-films`); the founder's
   beats are not founder screens (163 FR-1's founder-reader scores them) -- a film bundle carries none and asks no
   founder whole-flow question.
7. **The ways panel** is read and checked on screen (spec 164's `founder_page_on_screen`) and kept in the bundle
   (`founder_page`), not made a new §B kind: a new kind would move `RUBRIC_VERSION`.
8. **`link_walk` gained two plan keys** (`pick`, `why`; `evals/three_views_strangers.py`, a file 164 touched): two lines
   in the Importance and the follow-up branches; 161's roster passes neither and walks as before.
9. **`make unit` mirrors the walk with stubs** (the wire, the runner); the walk on the stack is the local walk above,
   never collected by `make unit` (163's rule: `evals/run_film.py` is not `test_*.py`).
10. **`walk.json`'s `spec` is `163+165`**; a 163 walk's row naming only `backtest` is never tabled (FR-3) and is named in
    the record.

## DRIFT

None. Walk 1's refusal was the harness's (judgement call 1), walk 3a's scrim the harness's; no product red met.

## Open

- **The paid run** (the founder's word): `make film-walk ENTRIES=holdout WHY=...` on Keel's door now walks the seven on
  each film's project (no back-test); untested on the keys. Keel's AI then answers the seven interviews' readings and the
  groupings (about what the back-test spent).
- The screener's served spoken form was not in the walked interview (`gate.condition.spoken` absent): R6 reads the §3
  template there, as the prompt says.
- `[film] holdout` is still empty (the integrator writes the founder's nine).
