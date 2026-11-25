# Tasks -- spec 162

Base: `origin/master` `1469005` (165 merged, DRIFT #119). Built 2026-11-24 from 20:42 ET by a builder (Claude Opus 5.5)
in the worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-162`, branch `162-the-solution-walked`, beside
keel-web 260's builder (`origin/260-three-questions-on-the-link`). The stack served keel-cloud-docs `94051ba8` (271,
273, 272 merged; contract 90) and keel-web from temporary detached worktrees
(`wt/keel-cloud-eval-162`, `wt/keel-web-eval-162`, `npm ci` once), named in this worktree's `stack.toml` copy only (never
committed, restored before the last commit): keel-web master `7c98d472` for run 2, then -- once 260's builder pushed
T1-T5 -- the 260 branch's head `f1ef43cf` for run 3 (the brief's leave: its screens early), then, on the coordinator's
word that 260 is merged, keel-web master **`a7d805b3`** for runs 4-6 (run 6 reported). Nothing paid: no model, no
key, no pip install (the main checkout's `.venv`), no network but `git fetch` / `git push` of this branch and the one
`npm ci`; the local stack on keel-cloud's fakes (FakeSpeech, FakePictures, the fake avatar, the fake transcriber, the
fake readings, the scripted runtime). Nothing merged or deployed.

- [x] T1 FR-1..FR-4 the founder's mirrors: `story_screens.py` (`IdeaWalk`, the brand page, four long beats, the six
  rows, the chapters, the plate, the failed build), `three_views.py`'s `idea_leg`, `vectors_screens.py`
  (`calibrates(spoken)` on SOLUTION), the money replay, their unit mirrors.
- [x] T2 FR-5, FR-6 the stranger's mirrors: `interviewer_screens.py`, the link walk, `classifier_guard.py`,
  `classifier_cases.py`, the corpus read through 272 (`instructions/corpus.py`, `instructions/registry.py`),
  `working_rung.py`; `harness/solution_surfaces.py`.
- [x] T3 FR-7, FR-8 the why roster per study, the Insights reads, the Overview and brief reads.
- [x] T4 FR-9 the three-surfaces record on the solution study (`three_views_strangers.py`, `calls_leg.py`).
- [x] T5 FR-10, FR-11 the report sections, DRIFT entries, `tests/test_the_solution_walked_162.py`; `make unit`; the
  local run; this file's sections.

## Versions
- Contract read: **90** -- `info.x-keel-contract` of the stack's `canon/openapi-v2.yaml` (sha256
  `c4584f584a4fbb8acddbdf0bf9e290bac57b6ce01a46e0a62915bf8619a29593`, keel-cloud 272's head), read by the run (the
  report's head) and pinned by `tests/test_the_solution_walked_162.py::test_contract_90_is_the_one_the_walk_reads`
  (`three_views.CONTRACT`; 161's 87 kept as `CONTRACT_161`). The spec names 89 (judgement call 1).
- `InferenceCharge.VERSION` read: **22** (keel-cloud 273: STORY_PICTURES, PICTURE_REVIEW at 0; IDEA_TURN 0;
  `interview_charge.PRICE_VERSION_273`).
- `DimensionRegistry.VERSION` read: **7** (keel-cloud 272: the solution's three `yes_no` / `share_yes`, no escape, the
  founder's side a share bin; `instructions/registry.py` reads it -- `YES_NO_CONTROL`, `SHARE_YES_RULE`).
- Corpus revision: the files stay keel-cloud's (23 golden, 25 gallery); the eval's read revision moves
  `r23+269` -> **`r23+269+272`** (`instructions/corpus.READ_REVISION_162`; judgement call 7).
- The dimension cards: `CARDS_SHA256` `4dc14231...` (141's, the eval's copy before 269) -> **`dbcb2196638915e48a5aefa055b856f27c84657921c1edb7a1a7e109dcf87c39`**
  (`quality.cards.CARDS_SHA256`; keel-cloud's own copy at `94051ba8` is `4702073d...`, owed the vendoring; judgement
  call 8).

## How each FR is met

| FR | Where | What the walk holds |
|---|---|---|
| FR-1 | `harness/story_screens.py`: `IdeaWalk` rewritten -- `film_then_opening` (the problem's film through `idea-problem-film`, `idea-start-said`, `story/confirm` with no body, no board, no `idea-still`), `brand_page` (`idea-name`, `idea-tagline` and its counter, a swatch, `idea-logo-line`, a 400x300 PNG (`png_bytes`) refused with `idea-icon-fault`, nothing posted to `idea/icon`, `idea-brand-continue` -> `PUT idea/brand`), `beat` / `_two_parts` / `beats` (four long beats closed by *That's it.*; the asks and beat 3's `done: false` answered from `then`, the correction sent `correction: true`), `boxes` (`idea-board` by `data-box`); `said_idea`, `idea_reading_of`, `idea_scripts`, `idea_question`, `idea_opening`, `unmatched_line`, `pilot_ask`, `IDEA_QUESTIONS` / `IDEA_OPENING` / `STEP_ASK` / `UNMATCHED_ASK` / `NOT_SOLVED` / `FEATURE_ASK` / `NOTHING_TO_SET_UP` / `PILOT_ASK` (keel-cloud 271's words), `IDEA_BOARD_ROWS`, `board_six_verdict`, `LOGO_LINE`; `ORB_WATCH` lights `idea-board`; `evals/three_views.py`: `IDEA_TELLINGS`, `idea_plan`, `idea_beats_checks`, `idea_leg` | the film, then the opening heard word for word (= the served `opening`), the stamp with no words; the brand page (no orb, the logo line, the non-square PNG refused on the spot with the same line, nothing uploaded, the PUT's `{name, colour, tagline}`); 271's four questions (beat 3 word for word); every beat closed by the done word and sent without it; beat 1 with advantages alone -> *Start from the first thing they do. What happens first?* -> the steps; beat 3 two parts across 7 s (*Take your time.*), one limitation unmatched -> *I did not understand how ... Can you think about it?* -> the correction -> *I will show ... as not solved.*; beat 4 a feature -> *That is what it does. What do they get back because of it?* -> the joy; the board's six rows in order with the idea's words, *Is that your idea?*, the quiet confirms |
| FR-2 | `IdeaWalk.film_yes_verdict_pilot` (`story-verdict`, `idea-verdict-said`, `idea-pilot-card`, *Yes, please.* -> `PUT idea/pilot`); `three_views.ready_checks`; `vectors_screens.calibrates` (`SPOKEN_WRITTEN`), `solution_written`, `solution_calibration_answered`, `SOLUTION_BIN_LABEL` | the served `verdictLine` (= `SolutionBeliefs.DEFAULT_VERDICT`) on its card, the quiet going on; the pilot ask (= `pilotAsk`) answered yes, `PUT idea/pilot {offer: true}` 200, `pilot` true; the ready page with no belief page; the review's three rows `p_60_80` (*6 or 7 in 10*), the calibration answered; the Before step with no pilot screen and no `pilot-first-step` |
| FR-3 | `IdeaWalk.building_then_film` (the plate `idea-plate`, its time, the band's `story-chapter`, `story-picture`), `failed_build`; `story_screens.idea_scenes_verdict`, `IDEA_CHAPTERS`, `CHAPTER_WORDS`, `FILM_OPENING`, `FAILED_SAY` / `FAILED_PARTS` / `BEAT_OF_CHAPTER`, `failed_say`; `three_views.failed_build_walk` | the build's scenes against the board (at most eleven, the opening line, the chapters in order, the setup scene iff a setup, one scene a step, the marks the board's, the advantage iff read, the joy last `joy: true`, the brand on every screen, `pictureAssetId` on every scene, one clip a line, the plate); the plate alone before the film and the chapters' words in order; the failed build (the script's always-refused brand): `failedChapter` joy, *Keel could not draw what they get. Say that part again?*, beat 4 opened again |
| FR-4 | `three_views.money_card(idea=)` | the money replay's card reads the board's rows (the person, then the product, the workflow, the setup, the statement, the limitations, the joy), no product sentence, no *So* row |
| FR-5 | `harness/solution_surfaces.py` (`link_faults`, `films_lines`, `first_question_seconds`, the words); `three_views_strangers.solution_wire_checks`, `solution_view`; on keel-web 260: `watch_plate`, `solution_order`, `solution_walk_checks`, `link_walk` (the plate row, each row's time) | on the wire every run: the opening with the founder's first name and *First, one question.*, *Let us see it.*, *Did this happen to you?*, both films, the plate and its two lines, no idea card, *Would you try Runcheck for real?*, every sentence within 20 words; the time to the first question recorded (never asserted); on 260's screens the order, the plate, the check's No before the plate |
| FR-6 | `harness/classifier_guard.py` (`SOLUTION_CONTROLS`, `yes_no` in `_SINGLE`, `served_items`); `harness/classifier_cases.py` (the canon's `yesno` re-copied); `harness/working_rung.yes_no_side`; `instructions/registry.py` (registry 7: `yes_no`, `share_yes`, no escape); `instructions/corpus.py` (`READ_REVISION_162`, `spec272_solution`, `spec272_founder_bin`, `SPEC_272_MOVES`, `SPEC_272_SOLUTION`, the loader through 272); `solution_surfaces.question_faults`; `link_walk` (a plan's `picks`, by its words or its letter) | the three questions on `yes_no` in 272's words (Compatibility with the brand and the -ing job, Relative advantage the base job, Adoption friction its setup form); *yes*, *no*, *A*, *B*; *si* unclear on two rows |
| FR-7 | `solution_surfaces.SOLUTION_ROSTER`, `owed`, `answers_for`, `response_for`, `WHY_SAID`, `themes_entries`, `insights_faults`; `three_views_strangers.solution_whys_on_the_wire`, `solution_roster_on_the_wire`, `solution_roster_on_screen` (260) | yes on all three asked nothing; one No on each dimension its why (*What would get in the way?*, *What would it have to do better?*, *What makes it a trouble?*) on the spot; three Nos two whys, the third capped; every response 201; the check's No and the screener's No |
| FR-8 | `solution_surfaces.share_faults`, `so_line_faults`, `brief_faults`, `standing_of`; `three_views_strangers.solution_founder_page` | the three Overview cards' `chart.share` (the yes of n, the founder's band), the bars *Yes* / *No*, no `chart.benefit`; the So lines without *should*, *next*, *try*; Insights' headings, quotes with *No*, `capped`, no `tookBy`; the brief's rows `{yes, n, share, founderBand}` |
| FR-9 | `solution_surfaces.served_record`, `card_record`, `first_person_faults`; `three_views_strangers.solution_surfaces_check`; `evals/calls_leg.py` (`PLATE_KIND`, `plate_passage`, `plate_words`) | the orb's link, the face's link and the call's script, step for step: the opening, the screener, the bridge, the problem film's lines, the check, the plate's two lines, the idea film's lines, the three questions with their options and whys, the pilot ask; the card's first-person forms |
| FR-10 | `harness/interview_charge.py` (`PRICE_VERSION_273`, `SOLUTION_READINGS`, `solution_reading_faults`, `reading_rows`) | every IDEA_TURN, STORY_PICTURES, PICTURE_REVIEW row 0 credits; the problem's legs (161) unchanged; `PROFILE=remote` untouched |
| FR-11 | `evals/three_views_report.py` (`founders_solution_markdown`, the solution rows of *The three surfaces*, the head); `three_views.CONTRACT` 90; `runs/DRIFT.md` | the report's sections; contract 90 read |

## Judgement calls

1. **The contract read is 90, not 89.** The spec names 89 (written before keel-cloud 272 merged); keel-cloud-docs master
   `94051ba8` carries 271 (88), 273 (89) and 272 (90). `three_views.CONTRACT` is 90 (`CONTRACT_161` keeps 87).
2. **keel-web 260 on the screens.** keel-web 260 was being built beside this spec: run 2 served keel-web master
   `7c98d472` (no 260), so the stranger's solution screens were named *pending keel-web 260*
   (`three_views_strangers.SCREEN_CHECKS_260`, one failed check a leg) while the cloud's side of every solution leg was
   read on the wire (`solution_view`); run 3 served 260's pushed head `f1ef43cf` (the brief's leave), and once the
   coordinator reported 260 merged, runs 4-6 (run 6 the run reported) served keel-web master **`a7d805b3`**. The cloud's side
   is read on the wire every run; on a keel-web with 260 (`story_screens.web_has_260`) the solution's screens are walked
   too (`solution_roster_on_screen` on the orb and the face, the stage page's three cards, the card's plate passage) and
   then the 159-164 screen walks; keel-web 260's tasks.md *Eval mirrors to move for keel-e2e-eval 162* are folded in
   (the card's `line` / `plate` passages, no hand-over line on the plated idea film, `yes_no` in `ONE_PICK`, the
   questionnaire and `ROW_CONTROLS`, the breakdown's *Yes k · No n-k*, `web_has_260`); the bridge's lit words and the
   pilot ask's served words on the sheet are walked by where they stand (`ai-where`), not by their words.
3. **The opening is read before the idea is served.** `GET idea/spoken` is a 404 until the brand is saved (keel-web 259
   judgement call 2), so the opening heard is held to keel-cloud's `IdeaTurns.OPENING` with the story's people and to
   the served `opening` once the brand page has saved.
4. **The brand the walk types** is the name the cloud's fake script tells its beats with (*Runcheck*, keel-cloud 271
   judgement call 21: an invented product), a tagline and a colour of the walk's own; the failed build walks the
   script's always-refused brand (`ideaReviews[0].name`) on FR-1a's defined problem, once.
5. **Which special script each leg walks** (`three_views.IDEA_TELLINGS`): FR-1b's solution beat 1 with advantages
   alone (code's ask), beat 2 with two rows, beat 3 in two parts across 7 s of quiet with one limitation left unmatched
   and corrected to a cross, beat 4 a feature first (code's ask); FR-1c's money solution beat 1 with its steps, beat 2
   with none, beat 3 corrected to a match, beat 4 the joy at once; the failed build's plain telling.
6. **The Before step's counter**: the spec says *1 of 1*; keel-web 113 FR-2 draws no counter on a step of one screen
   and 259's `beforeScreensOf` drops the pilot screen where the pilot was spoken. The check holds the pilot screen and
   `pilot-first-step` absent and keeps the counter as drawn in its detail.
7. **The corpus revision is a read** (spec 161 judgement call 6). keel-cloud 272 judgement call 17 leaves *the
   revision that records the two* to this spec, but the files are keel-cloud's canon and are never written here; the
   eval's read revision moves to `READ_REVISION_162 = "r23+269+272"` -- every solution pick read yes or no by
   `spec272_solution` (keel-cloud's `VectorCorpusFixture.spec272Solution`, one rule), the founder's recorded list as the
   default bin, the golden rows moved as `SPEC_272_MOVES` / `SPEC_272_SOLUTION`; the loader skips the recorded solution
   rows against registry 7 and refuses a pick that reads neither yes nor no.
8. **The dimension cards are this repository's to author** (spec 131; keel-cloud 272 judgement call 16). The eval's copy
   starts from keel-cloud's at `94051ba8` (269's twelve) with the three solution cards re-cut on yes or no; Frequency's
   registry line gains its supports and its bad example *What breaks it:* (the cards test reads both). `CARDS_SHA256`
   moves to `dbcb2196...`; keel-cloud's copy owes the vendoring and differs from this one in the moved cards alone
   (`quality.cards.differing_cards`, held by `test_cloud_219_228_mirror_141`). The earlier pins on the retired list
   and scale words (236, 237) skip by name (`cards.solution_cards_at_272`).
9. **The typed SOLUTION path** is keel-cloud 272's to retire (its judgement call 12: a SOLUTION list is refused, a stored
   list read as the bin). `LIST_CONTROLS` / `PICKED` stay for the recorded corpus's reads; the typed S-0xx journeys'
   SOLUTION belief pages (`corpus_scenario.leg_calibrate`) are not moved here -- owed to the spec that moves those
   journeys onto the spoken walk (open).
10. **The film in pictures on the founder's and the link's players** (keel-web 261's eval mirrors, owed since 163): the
    158b fit read (`measure_story`) reads `story-stage` -- the caption kept inside the stage is the *no text on the
    drawing* verdict in picture mode (the words inside the picture are the film judge's), the caption's rows the spoken
    line's; `FILM_JS` reads the stage in the board's place; `scenes_verdict`'s picture is `pictureAssetId` on a 273
    build.
11. **The time to the first question** (FR-5, D6) is recorded by the cloud's own count (`solution_surfaces
    .first_question_seconds`: the films' lines at 2.5 words a second, a second's hold a scene, the plate's three
    seconds) beside the served `minutes`; the walked measure is keel-web 260's screen (pending). Never asserted.
12. **The solution's whys on the wire are asked as keel-web 260's page asks them** (FR-3 of 260: the follow-up route
    after each of the three items, with the answers so far and the rungs asked), and the response carries no story
    (keel-cloud 272 FR-3: the film anchors it).
13. **keel-web 261's eval mirrors are folded in here** (owed since spec 163, named in this spec's brief): the founder's
    and the link's films are in pictures on keel-cloud 273's stack (FakePictures), so the 157 / 158b reads that waited on
    stick strokes (`film_controls`: three strokes on, the pause holding them, *Start over* drawing from the start) read
    the shown picture instead (`FILM_JS`'s `sig.shown`: the pause holds it, *Start over* brings the first scene's back
    within 3 s -- a picture follows the voice); the pain hold is read to within 40 ms (`HOLD_SLACK_MS`, the crossfade's
    frame or two); a caption with no words between two pictures has no box and is not read as outside the band.
14. **The failed build is walked on its own solution project** (FR-1a's defined problem picked on the which-problem
    page), after FR-1b's ready page, so FR-1b's project keeps its build ready for the strangers' legs.
15. **The stand-ins**: `solution_view`'s face is stood in under its own key (`solution-wire-avatar-...`), since on keel-web
    260 the 159-164 face walk stands Keel's door in again for the same study (run 3 met the duplicate key).
16. **Two product findings are left red, never patched around**: the Copilot card does not open Importance's why on the
    problem study (**DRIFT #121**, keel-web; #116's cloud side answered by keel-cloud 272's `followUp.notPicked`) and the
    face's plate frame draws no ship mark (**DRIFT #122**, keel-web 260). The fake idea draft's one-word scene (**DRIFT
    #120**, keel-cloud's fakes) fails nothing: the film's parts hold.

## Runs
All local (`make e2e-157 PROFILE=eval`, the main checkout's `.venv`), FakeSpeech / FakePictures / the fake avatar / the fake
transcriber / the fake readings / the scripted runtime only: no vendor host contacted in any run (the log scan), every
Keel AI clip FakeSpeech at 0 µUSD; the stack (`make up` from this worktree, `lsof -i :18080 -i :5173` empty before) torn
down after the last run (`make down`; no java, vite or container of this build left). Times ET, 2026-11-24/25. The run
reported is **run 6**.

| run | stack | result |
|---|---|---|
| 1 (21:06) | cloud `94051ba8`, web `7c98d472`, eval `6797728` | stopped at the founder's sign-in (*.auth-title* never drawn): vite's first-load re-optimisation in the new worktree's empty cache -- environment; the cache warmed before every later run |
| 2 `runs/157/94051ba8-7c98d472/20261125T021052Z` | cloud `94051ba8` (contract 90), web `7c98d472` (no 260), eval `6797728`, 1442 s | **2 of 13 green** (FR-1d, money copilot). The founder's solution walked end to end by voice on 259's screens (the film and the opening, the brand page with the non-square PNG refused, the four long beats with the three asks, the two parts and the cross, the board, the build, the plate and the chapters, the verdict, the pilot ask yes, the ready page, the failed build) -- red only by harness reads fixed in `4d59f5a`: the films in pictures (the 158b fit read, the film's controls -- keel-web 261's mirrors), the board's lit rows (`idea-board`), the chapters as built (`before` the setup's); the solution study on the wire all green (the words, the three questions, the five people's whys, the check's and the screener's No, the share bars, the So lines, Insights, the brief, the ledger) but for *pending keel-web 260* and the card's plate passage (the ask line has no picture) and the three surfaces (the opening said with the interviewer's introduction) -- harness, fixed in `4d59f5a` / `b8b71cb`; problem copilot **DRIFT #121** |
| 3 `runs/157/94051ba8-f1ef43cf/20261125T023818Z` | cloud `94051ba8`, web 260's pushed head `f1ef43cf`, eval `6a7d2ad`, 2041 s, 21:38-22:12 | **5 of 13 green** (FR-1a-d, money copilot). On 260's screens the solution walked on the orb (the order, the plate, `yes_no` by words and letter, the idea card nowhere, every why, the check's No before the plate, the screener's No). Red: *Start over* on a picture film read too soon, the card's story moments and records on the plated study, a duplicate stand-in key on the face, the old hand-over check on the plated link -- harness, fixed in `b8b71cb`; the face's plate frame without a ship mark (**DRIFT #122**); #121 |
| 4 `runs/157/94051ba8-a7d805b3/20261125T031400Z` | cloud `94051ba8`, web master **`a7d805b3`** (260 merged), eval `b8b71cb`, 3056 s, 22:14-23:05 | **9 of 13 green**. Red: problem copilot (**#121**), solution avatar (**#122**), solution copilot (the plated card's check reached by its own *Story again* -- harness, `2a939bf`), money avatar (*Start over* read to the first scene -- harness, `2a939bf`) |
| 5 `runs/157/94051ba8-a7d805b3/20261125T041804Z` | as run 4, eval `0b9349b`, 3347 s, 23:18-00:14, the machine under another builder's load (load average 5-7) | **8 of 13 green**: #121, #122, and three timing reads under the load, each green in runs 4 and 6 -- a chime counted a frame before its hand-over (FR-1b), the gate's clip read while the orb was still small (problem orb), and one phone read of a caption with no words between two pictures (FR-1a; harness: not read as outside the band since `904a92c`) |
| **6 (the run reported)** `runs/157/94051ba8-a7d805b3/20261125T051446Z` | cloud `94051ba8` (contract 90), web master **`a7d805b3`**, eval `904a92c`, 2378 s, 00:14-00:54 | **11 of 13 green**: FR-1a, FR-1b, FR-1c, FR-1d, problem orb, problem avatar, solution orb, solution copilot, money orb, money avatar, money copilot. Red, each by one check and each the product's: **problem copilot** -- the walked one script at `problem.importance` (the card opens no Importance why: **DRIFT #121**); **solution avatar** -- the same walk at the plate (the face's frame draws no ship mark: **DRIFT #122**). The founder's solution by voice with no typed page but the brand's; the three surfaces of the solution study one script (11 steps, as served); the report's *The founder's solution* and the solution rows of *The three surfaces*; the time to the first question recorded (106.6 s by the cloud's count; 33.0 s / 38.1 s on the walks' clocks at FakeSpeech's pace) |

The legs pending keel-web 260 in run 2 (`SCREEN_CHECKS_260`) all ran green on `a7d805b3` (runs 4 and 6) but #122's one check.

## make unit
Both on the same siblings (this worktree's `stack.toml` copy: keel-cloud-docs `94051ba8`, keel-web `a7d805b3`), run side
by side 00:55-01:03 ET:
- Before (the base `1469005`, a detached worktree of it, removed after): **129 failed, 6051 passed, 180 skipped** --
  every red a mirror of a sibling checkout's moved words (271-273's and 259-261's, the cards behind 269, the canon's
  classifier copy). The same 129 on keel-web `7c98d472` at 20:43 ET.
- After (the head): **72 failed, 6143 passed, 169 skipped -- no new red**; 57 of the base's reds fixed (the cards on
  registry 7, the classifier copy, the registry and corpus read through 272, the 157 / 158 / 159 / 161 mirrors re-pinned
  to 259 / 271-273). `tests/test_the_solution_walked_162.py`: 27 passed.

## Commits
| Commit | FR | What |
|---|---|---|
| `871a16b` | FR-1..FR-11 | T1-T3 first cut: `IdeaWalk` on 259, `idea_leg` / `ready_checks` / `failed_build_walk`, the money replay's board, `harness/solution_surfaces.py`, the solution study on the wire, `yes_no` in the classifier and the working rung, registry 7, the corpus read through 272, the report's sections, contract 90 |
| `6797728` | FR-6, FR-11 | the dimension cards' solution three re-cut on yes or no (`CARDS_SHA256` `dbcb2196...`), the cards test on registry 7, `tests/test_the_solution_walked_162.py` |
| `4d59f5a` | FR-1..FR-9 | run 2's reading: the films in pictures (keel-web 261's mirrors), the board lit, the chapters as built, the solution's screen walks for keel-web 260, the card's plate passage, the opening as said |
| `6a7d2ad` | FR-11 | DRIFT #120, #121, #116's status |
| `b8b71cb` | FR-5, FR-9 | keel-web 260's eval mirrors folded in; run 3's reading |
| `2a939bf` | FR-9, FR-11 | run 4's reading; DRIFT #122 |
| `0b9349b` | -- | the earlier pins on retired card words skip by name |
| `904a92c` | FR-3 | run 5's reading (a caption with no words) |
| (this commit) | FR-11 | this file; the report's walked time wording |

## DRIFT written
- **#120** (keel-cloud 271, the fakes): the fake idea draft cuts a long statement at twenty words into a scene of one
  word (*Changed.*, *Goes.*) and says the joy to *they*. Met in runs 2-6; fails nothing.
- **#121** (keel-web, the Copilot card's machine): the card does not read `followUp.notPicked` (contract 90), so it never
  asks Importance's why where the orb and the face do. Met in runs 2-6 (problem copilot).
- **#122** (keel-web 260, the face's plate): the face's plate frame draws no ship mark. Met in runs 3-6 (solution avatar).
- **#116** status: the cloud's side answered by keel-cloud 272 (`followUp.notPicked`); the remainder is #121.

## Open
- The dimension cards' vendoring: keel-cloud's `dimension-cards.md` and `RespondentReview.CARDS_SHA256` owe this spec's
  copy (`dbcb2196...`); the earlier rounds' digest pins (232, 233, 235, 236/237, 243) stay red until they do (they were
  red on the base).
- The typed SOLUTION path in the S-0xx journeys (`corpus_scenario.leg_calibrate` on lists keel-cloud 272 refuses) --
  judgement call 9.
- The bridge's lit words and the opening's words are not lit on the link (keel-web 260's own open: the opening clip
  carries the introduction first); the walks read the order by `ai-where`.
- The run of record on merged masters is the integrator's (`make e2e-157 PROFILE=eval` on keel-cloud-docs `94051ba8`,
  keel-web `a7d805b3`, this branch merged); run 6 is that run on this branch's head.
