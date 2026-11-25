# Tasks -- spec 166

Base: `origin/master` `639a3c0` (162 merged, the trial's table committed, spec 166). Built 2026-11-25 from 01:10 ET by a
builder (Claude Opus 5.5) in the worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-166`, branch
`166-the-solution-film-judged`. Nothing paid: no model, no key, no vendor, no pip install (the main checkout's `.venv`),
no network but `git fetch` / `git push` of this branch and one `npm ci`; `DOOR=fake` only (keel-cloud's fakes,
FakePictures, `KEEL_PICTURES` unset). The local stack served keel-cloud-docs master `c7079b59` (contract 91) and keel-web
master `1ca065b3` from temporary detached worktrees (`wt/keel-cloud-eval-166`, `wt/keel-web-eval-166`, removed after),
named in this worktree's `stack.toml` copy only (never committed; restored before the last commit).

- [x] T0 Set up: the worktrees, the base's `make unit` (the reds listed below), this file.
- [x] T1 FR-1 the solution leg on a project made from the problem's: `film_frames.entry_idea_beats(entry_yaml,
  problem_story)` (the brand, the four beats in the entry's words, the asks' answers), a SOLUTION project created with
  `parentProjectId` by the same founder, the four beats told (typos on Keel's door, the fakes' script on the fakes), the
  board's yes, the build, the pilot ask answered yes; the leg's record.
- [x] T2 FR-2 the solution film captured before any stranger: `FilmCamera` generalised to the idea film
  (`define/idea/check`, up to eleven scenes, the five chapters, the plate frame, `pictureMissing` recorded), the
  pictures and the sheet, `build.pictures.plan / reviews / kept`, `failedReason`, into `film/<entry>/solution/`
  (`film.json` `kind: "solution"`); the problem's folder unchanged.
- [x] T3 FR-3 the strangers on the solution link: the lock on SOLUTION, the entry's people of the SOLUTION scope (their
  recorded answers read yes or no through 272), each walking the solution link, the founder's page after them,
  `backtest.json` `kind: "film-solution"`; `walk.json` naming both projects, both screens bundles and both score files,
  rewritten after every step.
- [x] T4 FR-4 the reader on both films: every film folder read with its kind; the solution request (the persona card,
  the problem's limitations and cost, the idea board, the lines with their chapters, the plate, the frames, the
  pictures and the sheet, the setting and the plan, S1-S9); `...-film-<entry>-solution.json`; the founder's beats on the
  solution; the size rule (the laptop frames dropped first, said).
- [x] T5 FR-5, FR-6 the table: both films a row, the rank, the verdict on either film, findings of both kinds; `BASELINE=`
  and *Compared with ...* (each criterion's move, added / missing entries, the round's means) in the record and
  `FILM-TABLE.md`.
- [x] T6 FR-7, FR-8, FR-10 the switches (`[film] scopes`, `SCOPES=`, `ONLY=solution`, `DRY=1`, `DOOR=fake`, the
  preflight's refusal), the unit tests (`tests/test_the_solution_film_judged_166.py`), no respondent instruction touched.
- [x] T7 FR-9 the fake walk on 08-fresco recorded; `make unit` after; this file's sections.

## Versions
- Contract read: **91** (keel-cloud-docs `c7079b59`: 271's idea routes, 273's pictures, 275's `pictureMissing`,
  `build.pictures.plan / reviews / kept`, `failedReason`, portrait 1024 x 1536). `three_views.CONTRACT` is unmoved (90:
  the e2e-157 walk's pin, not this spec's).
- `FILM_RUBRIC_VERSION` unmoved (1): S1-S9 were in the rubric since 163; no criterion moved. `RUBRIC_VERSION` unmoved.
- The film reader's prompt (`quality/readers/film-reader.md`) gains the solution's own two parts (`solution-*` markers);
  the problem film's two parts are byte for byte as they were.

## How each FR is met

| FR | Where | What holds |
|---|---|---|
| FR-1 | `harness/film_frames.py` (`entry_idea_beats`, `idea_brand`, `idea_setup`, `idea_joy`, `idea_beat_faults`, `SETUP_NONE`); `harness/story_screens.py` (`IdeaWire`); `evals/run_film.py` (`solution_half`, `solution_words`, `idea_questions`, `idea_beats_record`) | after the problem's strangers, `POST /v2/projects {scope: SOLUTION, parentProjectId: <problem>}` by the same founder (the lineage served names the problem), the problem's film stamped (`story/confirm`, no words), `PUT idea/brand`, the four beats on `idea/turns/{n}` (an ask or beat 3's unmatched readback answered from `then`, beat 3's as a correction), `idea/confirm`, the build waited for, `PUT idea/pilot {offer: true}` after the capture; on Keel's door the entry's words (typed with typos on `TYPOS=1`, the brand typed exactly), on the fakes the fakes' idea script under its brand; the record: the project, the create request and its lineage, the beats as told and read back, the board (`idea.json`), the ledger's rows (`IDEA_CHARGES`), the time to the film |
| FR-2 | `film_frames.FilmCamera(kind="solution")` (`_plate`, `scene_count`, `CHECK_PATH`), `idea_chapter_faults`, `missing_scenes`, `fetch_pictures` (a dropped frame recorded `missing`), `picture_faults`, `film_dir`, `build_log`, `idea_board`, `write_folder(idea=)`, `lines_of` (joy, marks, the brand, `pictureMissing`) | the founder's player at `define/idea/check` once the build is ready, before the pilot's yes and before any stranger: the plate shot alone (`frames/plate-<viewport>.png`) then each scene held on the phone and the laptop by parking the next clip, up to eleven scenes, the chapters' words as drawn; the pictures and the sheet (`sheet.reused` against the problem's sheet id); `prompts.json` = setting, prompts, plan, reviews, kept, `failedReason`; `film.json` `kind: "solution"`; the problem's folder keeps its files and their shape (one key added to its `film.json`: the founder, judgement call 6) |
| FR-3 | `harness/film_strangers.py` (`lock_project(scope=, window=None)`, `calibration_ready`, `solution_plans`, `solution_walk_plan`, `owed_whys`, `walk_solution_people`, `solution_watched`, `screens_bundle(scope=, parent=)`, `founder_page_after(scope=, picks=)`, `solution_page_checks`, `clear_for_s`); `evals/run_film.py` (`solution_strangers_leg`); `quality/readers.py` (`FILM_KINDS`); `quality/film.py` (`solution_row`, `walk.json`'s `solution`) | the lock (the SOLUTION calibration written at the board's yes, the credits topped by the stand-in, the ready page's lock, the questions READY; a step that does not hold refused by name); the entry's people of the SOLUTION scope (`PEOPLE=` / `[cycle] people`) each walking the solution link on the orb (`three_views_strangers.walk_link` with spec 162's `picks`: the screener, the problem's film, *Did this happen to you?*, the plate, the solution's film, the three yes-or-no questions by their words, every why in the person's own recorded words else 162's line, the pilot ask); the founder's page after them (the answers leg on SOLUTION, 162 FR-8's reads as checks); `runs/<stamp>-film-<entry>-solution/backtest.json` (`kind: "film-solution"`, `scope: SOLUTION`, the problem's project named) that `make read-screens` reads; `walk.json` per entry: the problem's project, bundle and score file, and under `solution` the same of the solution's, rewritten after every step |
| FR-4 | `quality/film_reader.py` (`film_folders(kind=)`, `film_kind`, `entry_of`, `build_request(kind="solution", problem_story=, idea=, ceiling=)`, `problem_block`, `board_block`, `plate_block`, `plan_block`, `fit`, `founder_lines` with the pilot ask, `score_path(kind=)`); `quality/readers/film-reader.md` | `make read-films RUN=<walk>` reads every film folder with its kind (`KIND=` one); the solution request in order: the persona card, the problem's limitations and cost (the problem film's `story.json`), the idea board (`idea.json`), the lines with their chapters, marks and joy, the plate's words, the setting and the frame plan, the prompts, then the plate frames, every scene's frames, the pictures and the sheet, then `prompt_solution()`; `quality/scores/<bundle>-film-<entry>-solution.json` (`kind: "solution"`, `film_pct` over the nine, flagged on a 0, the projects); the founder's beats (the four beats, the verdict line, the pilot ask) read into it; the size rule: the laptop frames dropped first (from the last scene back), then the phone frames, never the pictures, said in the request and in the file (`dropped`); refused only where the pictures alone pass the ceiling |
| FR-5 | `quality/film_table.py` (`rows(solution_questions=)`, `entry_rows`, `verdict`, `solution_projects_of`, `FINDINGS` s1/s2/s6, `findings` / `drift_text` by kind, `render`) | one row an entry: F1-F8 and the problem's `film_pct`, S1-S9 and the solution's, the mean, flagged (by film), `founder_pct` over both studies' beats, §A and §B of each study (each from its own project's bundle), the dollars of each leg (the film's reading, the walk, the screens' reading); the rank by the mean of the two films' `film_pct`, ties by the problem film then the name, one film alone marked; an entry passes on each film with no 0; the verdict names the entries under the bar with the film; the weak criteria and the DRIFT findings of both kinds |
| FR-6 | `film_table.compare`, `compared_markdown`, `load_baseline`, `baseline_record_name`, `record_path`; `make read-film-table BASELINE=` | *Compared with <the baseline's record>*: per entry in both, every measure's move `before -> after (+/-)` (F1-F8, S1-S9, each film's `film_pct`, founder, §A and §B of each study, the dollars of each leg) and the rank's; the entries added and missing; the round's means (problem, solution, the mean of the two) before and after; written into `FILM-TABLE.md` and the record; a record of another bundle at the same name is never overwritten (this one takes its bundle's stamp) |
| FR-7 | `quality/cycle.toml` `[film] scopes = ["PROBLEM", "SOLUTION"]`; `quality/film.py` (`resolve_scopes`, `solution_words_missing`, `preflight(scopes=, only=, walk=, keep=)`, `plan_steps(scopes=, only=, keep=)`, `walk(--scopes --only --run --keep)`); `evals/run_film.py` (`scopes`, `only`, `keep`, the stack fixture, `_problem_record`, `_stub_founder`); `evals/three_views.py` (`Run.open(founder=)`); the Makefile (`SCOPES=`, `ONLY=`, `RUN=`, `KEEP=`, `BASELINE=`) | `SCOPES=PROBLEM` walks the problem alone; `ONLY=solution ENTRIES=<id> RUN=<walk>` walks the solution half again on the walk's recorded problem (its project and founder, on the stack that still holds it; the walk's record kept, the run named under `again`); `DRY=1` prints both halves; `DOOR=fake` walks both free; the preflight refuses an entry with no `statements.solution` or no `solution_mechanism`, `ONLY=` without a recorded problem, `KEEP=1` on more than one entry, a SOLUTION half without the PROBLEM one |
| FR-8 | `tests/test_the_solution_film_judged_166.py` (28), `tests/fixtures/film_166/` (`payroll.yaml`, `lullaby.yaml`) | `entry_idea_beats` on payroll (the setup-none case, the tagline's fallback, the cost's opposite) and Lullaby (a setup row, the joy in the entry's words), every beat held to the caps; the wire; the camera on a local idea-film page (the plate on both viewports, the chapters' words, a dropped frame); the folder and the ledger; the reader's folders, the request's parts in order, the size rule, the score file `kind: solution`, the founder's beats to the pilot ask; the rank (both films, one film, a failed leg, ties), the verdict on either film, the comparison and its record; the plan with both halves, SCOPES, ONLY, the preflight's refusals, `walk.json` with both, a failed solution leg, ONLY keeping the record; the people's plans, the SOLUTION lock, the bundle read by read-screens; FR-10 |
| FR-9 | *Runs* below | the fake walk on 08-fresco: both halves green |
| FR-10 | nothing under keel-cloud's respondent instructions is read or changed (`test_no_respondent_question_instruction_is_touched_here`); the founder's beats are the founder's words to Keel | |

## Judgement calls

1. **The four beats follow keel-cloud 271's four questions.** The spec lists *beat 1 the product, beat 2 the setup, beat 3
   the steps, beat 4 the limitations solved and the joy*; the served beats ask 1 the workflow (*from the first step to
   the last*), 2 the setup, 3 the limitations, 4 the joy. Each beat answers its question with the spec's parts: beat 1 the
   product in one breath (`statements.solution`'s first sentence) then the steps (trigger -> mechanism -> *What comes out
   is* output), beat 2 the setup or the setup-none words, beat 3 the mechanism once then one clause a limitation of the
   inherited problem story (*{limitation}: {name} takes care of that.*), beat 4 the joy against the cost (*Instead of
   {cost}, they get {joy}.*). Sending the steps on beat 3 would be read as the limitations' statement.
2. **The setup** (*what `solution_mechanism` needs in place*): no entry records a setup field, so one rule reads the
   founder's own recorded Adoption-friction rows (`founder_calibration.solution.adoption_friction`) and keeps those that
   are not the mechanism's own step (a row whose content words are mostly the mechanism's is a step); none left -> the
   setup-none words. Keel's beat-2 reader keeps only what is a setup. On the five of the paid run this keeps one or two
   rows for 09-karsa, 11-issen, 12-transload, 14-code-four, 15-voltair (some of them in-flow steps the reader may drop).
3. **The joy** in the entry's words: the founder's first Relative-advantage row (what it makes better), set against the
   problem story's cost; where none is recorded, *no more {cost}*. The answer to keel-cloud's feature ask is the joy alone.
4. **The idea is told on the wire** (`IdeaWire`), not through `IdeaWalk`'s screens: on Keel's door the page's recording
   would be read by the real transcriber (the seam's recording is the words' bytes), so the founder's words go as the
   page sends them once written down -- as 163 tells the problem's seven beats (`StoryWire`). The requests are keel-web
   259's in its order; `IdeaWalk` stays e2e-157's (spec 162) walk of the screens.
5. **The fake door tells the fakes' idea script** under its brand (*Runcheck*, spec 162's tagline and swatch), the
   plainest telling (beat 3's unmatched limitation matched by its correction): `FakeStoryReadings` answers its own words
   alone, as on the problem half (163 judgement call 3). The entry's composed words are kept in `film.json`
   (`composed`, not told).
6. **`ONLY=solution`** reuses the problem's project and its founder (recorded in the problem's `film.json` as `founder`
   -- the one key the problem's folder gains) on the stack that still holds them: the leg attaches (never boots: a stack
   brought up again starts empty, `docker compose down -v`) and signs in as that founder (Keel's door: `Auth.sign_in`;
   the fakes: `three_views.Run.open(founder=)`, her own AI through the code story again); refused by name where the
   project is not there. Since every DOOR=keel leg tears its stack down, `KEEP=1` (one entry) leaves a stack the leg
   booted standing so a solution half can follow.
7. **The capture is before the pilot's yes** (the founder's player at `define/idea/check` plays the plate and the film
   while the build is ready and the boxes confirmed); the pilot is answered on the wire after, and the lock after it.
8. **A dropped frame (`pictureMissing`) is recorded, never a capture fault** (`film.json` `missing`, the picture row
   `missing: true`): keel-cloud 275 drops a frame on its own and serves the film ready; the reader is told the scene has
   no picture and judges it (S1, S9).
9. **The people of the solution study**: `vectors_script.person_inputs` under SOLUTION (the first `people` own-link
   people in corpus order), each pick read yes or no by `corpus.spec272_solution`; a pick the link cannot carry (a chip:
   `yes_no` has no escape, or no pick recorded) is said *No* and named `remapped` (spec 064 FR-7's rule); a person the
   screener or the check sends away is never remapped. The watched person for read-screens is the first owed a why.
10. **The solution's bundle is its own folder** (`runs/<stamp>-film-<entry>-solution/`, the leg's `versions.json`
    copied in) so `make read-screens` scores it as its own study (`scope: SOLUTION`); the leg's transcript stays one.
11. **The table's layout moved** (spec 166 FR-5): rank first, both films' columns on every row (`--` where a film is not
    there), the entry marked *(problem film alone)*; 163's table mirror moved with it, and its holdout mirrors read the
    founder's nine the integrator wrote (both were red on the base).
12. **The size rule applies to both films**: a problem film over the ceiling drops its laptop frames as the solution's
    does (163 refused it); the file says what was left out.
13. **A late guide sheet over the ready page** (met on the problem half's lock on keel-web `1ca065b3`: the scrim took the
    lock's click for its whole timeout): the page is held clear of any sheet for two seconds first and a click a scrim
    took is pressed again (`film_strangers.clear_for_s`) -- the harness's, not a product red (a guide sheet is
    keel-web's design).
14. **A record never overwrites another bundle's**: the trial's committed record `quality/cycles/20261125-b48e1f4-film.md`
    holds 09-karsa's bundle (`20261125T012454Z-film-walk`) -- the 12-transload table of `20261125T010642Z-film-walk` was
    overwritten at the same name; `record_path` now names a second bundle's record by its stamp.

## Runs
All local, the main checkout's `.venv`, FakeSpeech / FakePictures / the fake transcriber / the fake readings / the
scripted runtime only; `lsof -i :18080 -i :5173` empty before each walk (a stale stub issuer of another worktree on
18090, started 2026-11-05, answered as the issuer and was left alone); the leg booted the stack and tore it down.
Times ET, 2026-11-25.

| run | result |
|---|---|
| walk 1 (01:27) `runs/20261125T062701Z-film-walk` | the problem film captured (14 frames); stopped at the problem half's lock: a guide sheet's scrim took the lock's click (harness, judgement call 13; `clear_for_s`) |
| **walk 2, of record** (01:29-01:44) `runs/20261125T062953Z-film-walk` (`make film-walk ENTRIES=08-fresco DOOR=fake WHY="166's local walk"`), 851 s, `1 passed` | **both halves green**. The problem half: project `74074b8e-e5b9-49e4-9b2e-e174be1ab8a4`, 14 frames, 8 pictures, 0 capture faults, locked, 7 of 7 answered on its link, the founder's page read (bundle `runs/20261125T063028Z-film-08-fresco`). The solution half: project `d31e466e-13d3-4ad9-9bf1-d15b71528417` created on the problem's (`parentProjectId`; lineage `problemProjectId` the problem), the brand *Runcheck* typed, the four beats on the wire (beat 3's readback asked *I did not understand how mistakes are found after the money has gone is solved ...*, the correction matched it), the board's yes, the build ready on **the problem film's character sheet** (`sheetAssetId` the same: `reused: true`), **the solution film captured before any stranger: 18 frames** -- the plate on both viewports (*Runcheck* / *Every changed line, seen before sign-off.* in the brand's green) and eight scenes on both (chapters *The task* on 2, *What it solves* on 5 with three ticks, *Better* on 7, *What they get* on 8, the joy; no *Before*: no setup), 9 pictures (8 scenes and the sheet), none dropped, 0 capture faults; the pilot's yes (`PUT idea/pilot {offer: true}` 200, `pilot` true); the lock on SOLUTION; **7 of 7 answered on the solution link** -- three yes on all three (asked nothing), one No on Compatibility (its why), two No on Relative advantage and Adoption friction (two whys each), one No on the check (`recency: false`, leaving before the plate, no answers); each walked the screener, the problem's film, the check, the plate, the solution's film, the three questions, the pilot ask; every response 201; **the founder's page read after them** (the stage page, the three cards, Insights; five screens; 162 FR-8's five reads all held: share bars counted from the picks, So lines evidence only, Insights as 119's, the brief's rows, the cards drawn as share); bundle `runs/20261125T063028Z-film-08-fresco-solution` (`kind: "film-solution"`) |
| `make read-films RUN=<walk 2> DRY=1` | two film calls written, nothing called: the problem's (22 images, 928 KB) with 8 founder's beats; the solution's (27 images: 2 plate frames, 16 scene frames, 8 pictures, the sheet; 1,073 KB) with 6 founder's beats (the four, the verdict line, the pilot ask) |
| `make read-screens RUN=runs/20261125T063028Z-film-08-fresco-solution DRY=1` | 16 prompts, scope SOLUTION, nothing called: 13 screens (5 after the answers), the whole flow, 2 insight lines |

The solution film's fake draft carries DRIFT #120's one-word scene (*Goes.*, scene 6): the fakes', known, fails nothing.
The ledger read no measured rows for either project on the free founder's account (her own AI; as 165's walk read
nothing on the fakes) -- recorded, not a finding.

## make unit
Both on the same siblings (this worktree's `stack.toml` copy: keel-cloud-docs `c7079b59`, keel-web `1ca065b3`):
- Before (the base `639a3c0`, a detached worktree of it, removed after; 01:16-01:23 ET): **76 failed, 6139 passed, 169
  skipped** -- the siblings' moved words, and two of 163's mirrors red since the integrator wrote the holdout
  (`test_the_table_on_three_fixture_scores`, `test_the_bar_and_the_holdout_live_in_cycle_toml`).
- After (the head, 01:47-01:55 ET): **74 failed, 6169 passed, 169 skipped -- no new red** (the lists diffed): the two
  163 mirrors above fixed, the 28 of `tests/test_the_solution_film_judged_166.py` green; the other 74 reds the base's, by name.

## Commits
| Commit | FR | What |
|---|---|---|
| `bdff58f` | -- | this file's T0..T7 |
| `751224d` | FR-1..FR-8, FR-10 | the solution half (idea beats, `IdeaWire`, the camera on the idea film, the folder, the strangers on the solution link, the bundle), the reader on both films, the ranked and compared table, the switches, `[film] scopes`, the unit mirrors and fixtures, 163's and 165's moved mirrors |
| `da560c5` | FR-7 | `quality/CYCLE.md`'s film runbook |
| `a738e1d` | FR-3 | the fake walk's reading: a person sent away is never named remapped |
| (this commit) | FR-9 | this file: the runs, `make unit`, the judgement calls, open |

## DRIFT
None written: no product red met. The walk's one stop (walk 1) was the harness's (judgement call 13).

## Open
- **The paid run on five** (the founder's word), from the main checkout's root with this branch merged and `stack.toml`
  on keel-cloud-docs master (`c7079b59` or later) and keel-web master (`1ca065b3` or later), nothing answering on the
  eval ports (`make down`):
  ```
  export KEEL_ANTHROPIC_API_KEY=... KEEL_OPENAI_API_KEY=... KEEL_PICTURES=openai KEEL_REVIEW_RESPONDENT_QUESTIONS=true
  make film-walk ENTRIES=09-karsa,12-transload,11-issen,14-code-four,15-voltair WHY="<the founder's words>"
  make read-films RUN=runs/<stamp>-film-walk
  make read-film-table RUN=runs/<stamp>-film-walk BASELINE=runs/20261125T010642Z-film-walk
  ```
  The baseline's film score file `quality/scores/20261125T010642Z-film-walk-film-12-transload.json` is untracked in the
  main checkout (with 09-karsa's `20261125T012454Z-...`): it must stay there (better, be committed) for the comparison.
  Estimate: per entry the two walks (the pictures of two films, ~$0.9; the beats', the people's and the groupings'
  readings on Keel's AI), `read-screens` on two studies (~$10 on the founder's plan) and two film reads (~$0.65 at list
  price) -- some $60-70 for five, a few hours.
- The idea beats' words (`entry_idea_beats`) are unscreened by any model; the setup rule (judgement call 2) keeps some
  in-flow rows Keel's reader may drop.
- `ONLY=solution` on Keel's door needs the stack kept (`KEEP=1`, one entry); untested on the keys.
- The 157 report's walked *time to the first question* is not part of this walk (the leg records `to_film_s`, the
  founder's time to the solution film).
