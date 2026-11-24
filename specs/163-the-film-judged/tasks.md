# Tasks -- spec 163

Base: `origin/master` (161 merged; 162 may be beside). Built by a builder (Claude Opus 5.5) in the worktree
`/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-163`, branch `163-the-film-judged`, once keel-cloud 273 and
keel-web 261 are merged. Nothing paid: no model, no key, no pip install (the main checkout's `.venv`), no network but
`git fetch` / `git push` of this branch; the local stack with `FakePictures` allowed. Push after every commit.

- [x] T1 FR-1 `quality/FILM-RUBRIC.md`, `quality/film_rubric.py`, `FILM_RUBRIC_VERSION`, the weak rule.
- [x] T2 FR-2 `make film-walk`: the PROBLEM back-test with no people, the frames at two viewports, the story, the
  pictures, the prompts and the setting in the bundle, the ledger read.
- [x] T3 FR-3, FR-4 the film reader through the API with vision (`quality/readers/film-reader.md`, `[film_reader]`),
  the score file, `make read-films`, `make read-film-table`, `FILM-TABLE.md`, the record.
- [x] T4 FR-5, FR-6 `[film] holdout`, `ENTRIES=holdout`, `make film-advise`.
- [x] T5 FR-7, FR-8 the unit mirrors and fixtures, the report section, DRIFT; `make unit`; the local walk; this file.

## Versions
- FILM_RUBRIC_VERSION: 1 (`quality/FILM-RUBRIC.md`, `quality/film_rubric.py`). RUBRIC_VERSION unmoved (5). Contract read:
  89 (keel-cloud 273's `pictureAssetId`, `chapter`, `sheetAssetId`, `build.pictures`, `GET /v2/assets/{id}`).

## How each FR is met
| FR | Where |
|---|---|
| FR-1 | `quality/FILM-RUBRIC.md` (three marked parts: `film-problem` F1-F8, `film-solution` S1-S9, `film-founder` R1/R2/R3/R5; `film_pct`, `founder_pct`, the flag, the bar, the weak rule, *Versions*); `quality/film_rubric.py` (`FILM_RUBRIC_VERSION` 1, `prompt_problem` / `prompt_solution` / `prompt_founder`, `criteria`, `parse_film_answer`, `parse_founder_beat`, `founder_summary`, `validate_file`, `aggregate` refusing two versions, `weak_criteria` with `FILM_WEAK` held to `rubric.WEAK_ZERO_ENTRIES` / `WEAK_MEAN`, `passes`) |
| FR-2 | `make film-walk` (`quality/film.py`): per entry `make film-leg` (`evals/run_film.py`, `harness/film_frames.py`), then on Keel's door `make backtest ENTRY= SCOPE=PROBLEM DOOR=keel PEOPLE= TYPOS=1` and `make read-screens` on its bundle; `runs/<stamp>-film-walk/walk.json` names each entry's film folder, back-test bundle and score file, rewritten after every step. The film leg: a founder (outside `fake-for` on Keel's door), a PROBLEM project, the seven beats on the wire (`StoryWire`; the entry's words by `entry_beats` on Keel's door, the fake script's on the fakes), the boxes' yes, the build, then `FilmCamera`: `define/story/check` on 390 x 844 and 1280 x 800, less motion, each scene held by parking the next line's clip on the route, the caption settled, `frames/scene-<n>-<phone|laptop>.png` (fourteen) with each frame's caption, chapter, shown picture, rows and inside-the-stage; `story.json`; `pictures/scene-<n>.png` + `sheet.png` from `GET /v2/assets/{id}`; `prompts.json` (setting and prompts); `film.json` with the lines, the beats Keel asked, the verdict line, the ledger's `STORY_PICTURES` / `PICTURE_REVIEW` rows and their dollars, and the capture's own faults |
| FR-3 | `make read-films` (`quality/film_reader.py`): one Messages API call a film (`POST /v1/messages` through `requests`, `claude-opus-5-5`, `output_config.effort` medium, adaptive thinking, `fallbacks: "default"` with its beta, the key in `x-api-key` alone), the prompt `quality/readers/film-reader.md` (persona card, lines with chapter marks and the ask, setting, prompts, then each frame and picture as a labelled image, then the rubric and the answer's shape), read twice at most (spec 122's rule), `refuse_cli` (the `claude` CLI door and any other refused by name), `[film_reader]` in `quality/readers.toml` with the list prices for the dollars; the founder's beats through the `claude` CLI (`quality/readers/film-founder.md`, one call a line); `quality/scores/<bundle>-film-<entry>.json` with the reader and founder-reader blocks, the version, the dollars, the frames; DRY=1, ENTRY=, FOUNDER=0 |
| FR-4 | `make read-film-table` (`quality/film_table.py`): one row an entry (the criteria, `film_pct`, flagged, `founder_pct`, §A `score_pct` over the R screens and §G, §B `after_pct`, the dollars, passes) from the same walk's read-screens score files (`walk.json`'s back-test bundles), the mean, the bar `[film] film_bar_pct` 80, the weak criteria, the round's verdict (a tabled holdout entry short fails it by name); `quality/FILM-TABLE.md` and `quality/cycles/<yyyymmdd>-<cloud7>-film.md` |
| FR-5 | `quality/cycle.toml` `[film] holdout = []` (comment: the integrator writes the founder's nine), `ENTRIES=holdout` refused while empty |
| FR-6 | `make film-advise` (`quality/film_advise.py`, `quality/readers/film-adviser.md`): one claude CLI call per weak criterion, the entries by number alone, the current `picture-setting.md` / `PicturePrompts` / `story-draft.md` text at the bundle's sha; a proposal naming an entry or adding a condition on who the people are (`cycle.special_case`) refused; `<record>-film-advice.md`, never applied |
| FR-7 | `tests/test_the_film_judged_163.py` (31) and `tests/fixtures/film_163/` (an invented entry, three film scores, a recorded API answer): the paste, the answer and its refusals, the score file through a stub door and a stub CLI (one call, the request's shape, twenty-two images, the key never written), the CLI door refused, the key refused, the dry run, the table on the three fixture scores (A passes at 100, B flagged on F4 at 81.2, C weak on F8 at 87.5; F4 and F8 weak; the round fails; DRIFT appended), the holdout, the walk's and the leg's refusals, nothing paid from `make unit`, the entry's beats, the capture on a local page that plays like keel-web 261's film (fourteen frames, each scene held, every clip let go), the pictures, the ledger, the chapter faults, the adviser's refusal. The local walk on the stack: see *Runs* |
| FR-8 | the record's and `FILM-TABLE.md`'s *The film, judged* (the table, the whys a line a criterion, the frames linked, the findings for DRIFT; `DRIFT=1` appends them to `runs/DRIFT.md` in its shape); `quality/CYCLE.md`'s runbook section |

## Runs
| run | result |
|---|---|
| `make unit` before (2026-11-24 17:56 ET, base `667e393`, the default stack.toml siblings) | 99 failed, 6,043 passed, 137 skipped -- every red a mirror of a sibling checkout's moved words (164's batch and others), none this spec's |
| `make unit` after (18:13 ET, `3f70f4f`, the same siblings) | 99 failed, **6,076 passed**, 137 skipped -- the same 99 reds by name (the lists diffed: identical), the 31 of `tests/test_the_film_judged_163.py` green |
| local walk 1 (18:24 ET; keel-cloud `b48e1f49`, keel-web `69e9f2a5` from detached worktrees, `FakePictures`, the stack booted by the leg and torn down) | `make film-walk ENTRIES=08-fresco DOOR=fake` -> `runs/20261124T232414Z-film-walk`: build ready, 14 frames, 7 pictures + the sheet, 0 capture faults; the ledger read **empty** -- the harness filtered `kind`, keel-cloud's measured rows carry `kind SPEND` and the charge in `action` (fixed in `37ceea9`) |
| local walk 2 (18:26 ET, the same) | `runs/20261124T232614Z-film-walk`: build ready, 14 frames (scene-1..7 x phone 390x844, laptop 1280x800), 8 pictures (48x32 FakePictures PNGs, 133 bytes each), story.json, prompts.json (setting: *a small office beside the finance team ...*; 8 prompts), the ledger one `STORY_PICTURES` row at 0 credits and seven `PICTURE_REVIEW` rows (0 µUSD on the fakes), 0 capture faults, 1 passed in 38 s |
| `make read-films RUN=<walk 2> DRY=1` | one film call (22 images, 927 KB in base64) and 8 founder's beats written as prompts; nothing called |
| `read-film-table` on the three fixture scores (`tests/fixtures/film_163/scores`, written to the scratchpad) | mean 89.6; entry-a 100.0 passes, entry-b 81.2 flagged (F4 0) fails, entry-c 87.5 passes (F8 1); F4 and F8 weak; the round fails; one DRIFT finding (entry-b, F4) |

## Commits
| Commit | FR | What |
|---|---|---|
| `83ecec9` | FR-1 | the film rubric and its module |
| `2e2d358` | FR-3, FR-4 | the film reader (API, vision), the founder's beats (CLI), the score file, the table, `[film_reader]`, `[film]` |
| `fb922e8` | FR-5, FR-6 | the holdout, the film adviser |
| `576ca14` | FR-2, FR-7, FR-8 | the walk, the leg, the capture, the Makefile targets, the unit mirrors and fixtures |
| `3f70f4f` | FR-8 | CYCLE.md's runbook section |
| `942fa5e` | FR-3, FR-8 | the frames' folder and links |
| `37ceea9` | FR-2..FR-4 | the ledger by its charge, the prompts once each, the dollars, FILM-TABLE.md |
| (this commit) | -- | this file |

## Judgement calls
1. **The film is told on its own project, before the scenario-maker's** (FR-2). The back-test (`corpus_scenario`) types
   the context at `define/context` and never tells the story, so its project has no film; rewriting it to tell the
   story would change the scenario-maker the spec keeps unchanged. `make film-walk` therefore runs, per entry, a film
   leg (`evals/run_film.py`: its own PROBLEM project, the seven beats on the wire as keel-web 257's page sends them, the
   boxes' yes, the build, the capture -- no stranger ever sees that film before it is shot), then `make backtest
   ENTRY= SCOPE=PROBLEM` and `make read-screens` as `quality-walk` runs them; one walk bundle (`runs/<stamp>-film-walk`,
   `walk.json`) carries the films and names each back-test bundle and score file, so the table reads the three scores
   an entry. The strangers of §A answer the typed project's link, not the film's.
2. **The entry's words, by one rule** (`film_frames.entry_beats`): 1 `actor_plural` and the segment; 2 the job and the
   circumstance; 3 `current_solution.today` then the problem statement whole; 4 the interpretation's problem line (else
   the statement); 5 the segment; 6 the circumstance (told only where Keel asks it); 7 the Importance rows after the
   founder's own. No trade is named in code; the paid walk is the first time a model reads them (open: the beats'
   wording is unscreened).
3. **The free walk tells the fake script's words** (`said_turns`), not the entry's: `FakeStoryReadings` answers from its
   own script, so the local film is the script's story under 08-fresco's name and persona card (said in `film.json`'s
   `telling`). The DRY prompt shows it: the persona card is a superintendent's, the lines are the payroll script's.
4. **The held clock is the parked clip**, as keel-web 261's own frames hold a scene (a scene stands until the next
   line's clip sounds): `context.route("**/v2/clips/**")` parks `clipIds[n+1]` until scene n's frames are shot, then
   lets it fall through. Playwright's page clock is not installed: it would freeze the page's own timers (the begin
   screen, the orb) as well. Less motion is asked for (no push-in, a cut), so a frame is a photograph.
5. **Fourteen frames are viewport shots**, the stage scrolled into view, the caption settled 400 ms; each frame records
   its caption, chapter, shown picture, rows and whether the caption sits inside the stage -- the capture's own faults
   (a scene with no picture, a caption outside the stage or over three rows on the phone, a sideways scroll, a chapter
   key off 273's places) go to `measures.faults` and the table's DRIFT findings, never patched around.
6. **The film reader is raw HTTP through `requests`**: no Anthropic SDK is installed and nothing is pip-installed. The
   request: `claude-opus-5-5`, `max_tokens` 16,000, `output_config.effort` medium, adaptive thinking (Opus 5.5 cannot
   disable it), `fallbacks: "default"` with `server-side-fallback-2026-07-01` (a fallback is recorded as `served_by` /
   `fallback` in the score file, so a film read by another model is named, never hidden), anthropic-version
   `2026-10-21`. The dollars are the usage at `[film_reader]`'s list prices ($4 / $20 per million).
7. **The founder's beats are read by the founder-reader of read-screens** (the `claude` CLI, `[reader]`), one call a
   line (seven beat questions with the founder's words, the ask and the readback the wire served, and the verdict
   line), inside `make read-films` (`FOUNDER=0` skips them). They are never folded into `film_pct`.
8. **The score file's path is the spec's** (`quality/scores/<bundle>-film-<entry>.json`, top level), so `make
   read-table`'s `*/*.json` glob never reads a film score as a question score; `<bundle>` is the walk bundle's name.
9. **The record** is `quality/cycles/<yyyymmdd>-<cloud7>-film.md` (the cycle's `record_files` pattern does not match it,
   so the question cycle's records are untouched); `quality/FILM-TABLE.md` is committed as a placeholder until a round
   of record -- the fixture table is never committed as one.
10. **The solution film (S1-S9) is in the rubric and the reader (`KIND=solution`) but not walked**: its capture waits for
    the solution batch (keel-cloud 271/272, keel-web 259/260) as the spec says; the table's solution column with it.
11. **DRIFT is appended only on `DRIFT=1`**: the table prints the findings; the operator appends them after reading.
    The local walks found no product red (0 capture faults; the ledger miss was the harness's, fixed).
12. **The orchestrator never runs `make down` before a step** (it could stop another builder's stack): DOOR=keel refuses
    a stack that answers; DOOR=fake attaches to one or boots its own, and the leg tears down only what it booted.

## Open
- **The holdout**: `quality/cycle.toml` `[film] holdout = []` -- the integrator writes the founder's nine.
- **The paid run of record** (the founder's word), from the main checkout's root with keel-cloud at 273+ and keel-web
  at 261+ in stack.toml:
  `export KEEL_ANTHROPIC_API_KEY=... KEEL_OPENAI_API_KEY=... KEEL_PICTURES=openai KEEL_REVIEW_RESPONDENT_QUESTIONS=true`;
  `make film-walk ENTRIES=holdout WHY="<his words>"`; `make read-films RUN=runs/<stamp>-film-walk`;
  `make read-film-table RUN=runs/<stamp>-film-walk` (then `DRIFT=1` once read); `make film-advise RUN=... DRY=1`.
  Estimate for nine: the walks about $9 (pictures ~$0.45 and the back-test ~$0.50 an entry on the keys) plus the
  readings about $45 on the founder's plan (read-screens ~$5 a PROBLEM study), the films about $2.70 at list price and
  the beats about $4.50 on the plan -- some $60 all told, a few hours.
- `entry_beats`' words, `film-reader.md` and `film-founder.md` are unscreened by any model.
- The paid door's founder signs up outside `fake-for` (`@keel-backtest.test`) as the back-test's does; untested on the
  keys (nothing paid here).
