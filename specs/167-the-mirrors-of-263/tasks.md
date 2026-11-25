# Tasks -- spec 167

Base: `origin/master` `c0c80fa` (166 merged, spec 167 committed). Built 2026-11-25 from 02:00 ET by a builder (Claude
Opus 5.5) in the worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-167`, branch `167-the-mirrors-of-263`.
Nothing paid: no model, no key, no vendor, no pip install (the main checkout's `.venv`, symlinked, ignored), no network
but `git fetch` / `git push` of this branch and one `npm ci`; `DOOR=fake` only (keel-cloud's fakes, FakePictures,
`KEEL_PICTURES` unset). The local stack serves keel-cloud-docs master `c7079b59` (contract 91) and keel-web master
`336eb477` (263 merged) from temporary detached worktrees (`wt/keel-cloud-eval-167`, `wt/keel-web-eval-167`, removed
after), named in this worktree's `stack.toml` copy only (never committed; restored before the last commit).

- [x] T0 Set up: the worktrees, the base's `make unit` (the reds listed below), this file.
- [x] T1 FR-1 the camera reads 263's stage (`harness/film_frames.py`): the drawn caption and pill (`story-side-line` /
  `story-side-chapter` where `story-film` is a grid), the layout, the stage's ratio and size on every frame, the
  inside check where the caption is over the picture and the beside-the-stage check (whole, no clipped word) in the
  column, `pictureMissing` recorded on the frame and never a fault (both films), the picture's size recorded (1024 x
  1536 or 1536 x 1024 accepted), the plate and `prompts.json` as 166 writes them.
- [x] T2 FR-2 the founder's screens: the frame plan read on both building screens (`story_screens`), the failed line
  with and without a reason, the candidate frame's ratio; the link's drawn caption on the laptop (`interviewer_screens`
  `FILM_JS`); the copilot still's ratio (`three_views_strangers`).
- [x] T2b FR-2b (added mid-build on the coordinator's word; judgement call 11): keel-web 264's eval mirrors -- the
  card's why outside `followUp.notPicked`, the fake record's follow-up, the face's chip on the plate, DRIFT #121 / #122
  answered (left open).
- [x] T3 FR-3, FR-5 the reader's frame labels name the viewport and the layout (`quality/film_reader.py`, the labels'
  words in `quality/readers/film-reader.md`; the rubric unchanged); the unit mirrors; no respondent instruction touched.
- [x] T4 FR-4 the free walk on 08-fresco, both halves, on keel-cloud `c7079b59` + keel-web `336eb477`; `make unit`
  after; this file's sections.

## Versions
- keel-web **263** at `336eb477` (contract 91 vendored): `story-film` / `story-side` / `story-side-line` /
  `story-side-chapter` (`src/lib/story/StoryPlayer.tsx`), `.sty-film` a grid above 720 px on a portrait film and
  `display: contents` otherwise (`src/styles/story.css`), `FramePlan` (`src/components/story/FramePlan.tsx`:
  `story-plan`, `-tally`, `-row[data-scene][data-status][data-kept]`, `-mark`, `-word`, `-reason`), the reason lines
  (`STORY.pictureFailed.sayWithReason`, `IDEA.failed.sayWithReason`, `bareReason`), `PictureStill`'s `data-ratio`.
- keel-cloud **275** at `c7079b59`: `build.pictures.plan / reviews / kept`, `failedReason`, `pictureMissing`, portrait
  1024 x 1536 (FakePictures stays 48 x 32).
- `FILM_RUBRIC_VERSION` unmoved (1), `quality/FILM-RUBRIC.md` untouched; `three_views.CONTRACT` unmoved.

## How each FR is met

| FR | Where | What holds |
|---|---|---|
| FR-1 | `harness/film_frames.py`: `_READ_STAGE`, `_SCENE_STANDS`, `FRAME_KEYS`, `frame_faults`, `stage_summary`, `picture_drawn`, `chapter_faults`, `FilmCamera._one`; `evals/run_film.py` (`missing`, `stage` on the problem's `film.json`, `stage` on the solution's) | the camera waits for the scene's DRAWN caption (the column's on a laptop around a portrait stage, the stage's otherwise -- the stage's own `story-line` is not drawn there, so 166's `wait_for(visible)` would have timed out on a 275 film); reads the drawn caption and pill; records on every frame `layout` (`over` / `column`), `film_display`, `ratio`, `stage` and `stage_ratio`, `inside`, `beside`, `in_window`, `clipped`, `caption_box`, `held`, `ground`, `missing`; the inside rule over the picture, the beside rule (whole in the window, no word clipped) in the column, the three rows and the sideways scroll on the phone; a frame left out recorded, a fault only where it shows neither the picture before held nor the ground (263 FR-9); `chapter_faults` accepts `pictureMissing` on the problem film; each picture's `ratio` and `drawn` (`275` / `before 275` / `other`) recorded, no size is a fault; the plate frame and `prompts.json` as 166 |
| FR-2 | `harness/story_screens.py`: `PLAN_JS`, `read_plan`, `plan_tally`, `bare_reason`, `picture_failed_say`, `failed_say(chapter, reason)`, `FAILED_SAY_REASON`, `PICTURE_FAILED_SAY(_REASON)`, `StoryWalk._plan_seen` / `building_then_story` (`plan`, `failed_said`), `IdeaWalk.building_then_film` (`plan`) and `failed_build` (`plan`), `SolutionStart.read` (`frame_ratio`), the idea check's *a picture on every scene* (`pictureMissing` counted); `harness/film_frames.py` `watch_building`, `replay_plan`, `building_faults`; `evals/three_views.py` `failed_build_walk` (the reason); `harness/interviewer_screens.py` `FILM_JS` (`layout`, `filmDisplay`, `ratio`, `stageBox`, `captionFrom`, the drawn line and chapter); `evals/three_views_strangers.py` `still_of` (`still_ratio`, `still_box` on every strip, a note of them) | the e2e walk's building screens read the plan (every tally seen, the last read) and the failed line; the film walk opens the founder's building screen (laptop) of each film right after the board's yes and watches it until the wire says ready or failed, every plan drawn held to keel-web's tally rule over its own rows; where the build was ready before the plan drew (the fakes), the screen is shown the build's own served view read as `building` (`replayed`) so `FramePlan`'s ids are read on keel-cloud's served plan and its rows held to it |
| FR-3 | `quality/film_reader.py` `frame_label`, `LAYOUT_WORDS`, `images`, the lines' tag for a frame left out; `quality/readers/film-reader.md` (the header's label paragraph, the two *Read the frames* sentences and the two lines' headings name where the caption is drawn) | *Frame -- scene n on the phone (390x844), the caption over the picture's lower third, a tall stage 358 x 537, as the founder's player held it* / *... on the laptop (1280x800), the caption beside the picture, a tall stage 420 x 630 ...*; a landscape film's laptop frame says *over*; a frame captured before 167 is read as 261's (over); a frame left out says so |
| FR-4 | *Runs* below | |
| FR-5 | no model, key or vendor; `test_no_respondent_question_instruction_is_touched_here` | nothing under keel-cloud's respondent instructions read or changed |

## Judgement calls

1. **The inside rule follows the layout, not the viewport alone.** FR-1 says *the caption-inside check on the phone
   alone, and on the laptop the caption beside the stage*. keel-web 263 keeps 261's layout on a laptop around a
   LANDSCAPE film (its judgement call 3: the column needs a portrait stage; a film before 275 and FakePictures' 48 x 32
   play 3:2 with the caption over the stage). So the camera holds the caption inside the stage wherever it is drawn
   over the picture (`layout: over` -- the phone always, a laptop around a landscape film) and beside the stage, whole
   in the window, no word clipped, wherever it is drawn in the column (`layout: column`). On a 275 film this is exactly
   the spec's phone / laptop split.
2. **The scene's wait reads the drawn caption.** 166's camera waited for the stage's own `story-line` to be visible; on
   a 275 laptop frame it is in the DOM but not drawn (`display: none` beside the column), so that wait would time out
   on every laptop scene of a portrait film. The wait (`_SCENE_STANDS`) now asks for the drawn caption -- the column's
   where `story-film` is a grid, the stage's otherwise -- holding the scene's words.
3. **`clipped`**: the caption's own box overflowing (`scrollWidth` / `scrollHeight` past its client size) or any
   ancestor with `overflow` other than visible cutting its box. `in_window`: the caption's box inside the 1280 x 800
   viewport (the frame is the viewport's screenshot, so a caption out of it is out of the reader's frame too).
4. **A frame left out is a fault only where 263 FR-9 does not hold** (neither the picture before `data-held` nor the
   stage's `data-ground`): keel-cloud dropping a frame is recorded (`missing`), never a fault (166 judgement call 8);
   keel-web drawing it wrong would be a product red. 166's local idea page held a dropped frame on no picture at all
   (261's way); it now holds the picture before, as 263 does, and its assertion moved with it.
5. **The picture's size is recorded, never judged** (`ratio`, `drawn`: `275` for 1024 x 1536, `before 275` for 1536 x
   1024, `other` for FakePictures' 48 x 32). `prompts.json` stays as 166 writes it (the problem's two keys; the
   solution's plan, reviews, kept and `failedReason`); the problem's `film.json` gains `missing`, `stage` and `building`
   beside 166's keys, the solution's `stage` and `building`.
6. **The plan ids in the film walk.** The film walk tells the beats on the wire and opened the founder's player only
   at `ready` -- after the building screen is gone -- so the plan was never on any screen it shot. The walk now opens
   the founder's building screen of each film (laptop) right after the board's yes and watches it while the build runs
   (`watch_building`), every plan it draws held to keel-web's tally rule over its own rows. On the fakes the build is
   ready within a second (the watch found it `ready` before the plan drew), so the screen is then shown the build's
   own served view (`GET story` / `GET idea/spoken`, fetched from keel-cloud as served) with `build.state` read as
   `building` (`replay_plan`, recorded as `replayed`): keel-web's own `FramePlan` draws keel-cloud's served plan and
   its ids are read and held to it (the rows' scenes and statuses, the tally). Nothing is written by either page; each
   is closed once read. The e2e walk's building screens (`StoryWalk.building_then_story`, `IdeaWalk.building_then_film`
   and `failed_build`) read the plan the same way (`read_plan`).
7. **The failed lines** (`failed_say(chapter, reason)`, `picture_failed_say(reason)`) are keel-web 263's words with
   `bareReason` (the reason's own closing stop dropped); the e2e walk's failed build (spec 162 FR-3) is held to the line
   with the served reason where 275 serves one. `building_faults` holds the film walk's failed line only where a
   picture (`failedScene`) or a chapter (`failedChapter`) failed and a line was read (an idea chapter's line navigates at
   once).
8. **The portrait probe** (`KEEL_FILM_PROBE=portrait`, `DOOR=fake` alone): FakePictures draws 48 x 32, so on the free
   walk the stage plays landscape and the laptop column is never drawn (the spec: *the camera records that, no fault*).
   To see the camera read keel-web 263's real column before the paid run, the free walk of record also shoots each film
   once more with every picture the browser asks for answered by a plain grey 32 x 48 PNG (`portrait_probe`), into
   `probe/frames/`, recorded in `film.json` `probe` and never handed to the reader; its faults are its own (not the
   film's).
9. **The reader's words** (`film-reader.md`): the header's label paragraph (not sent), the two *Read the frames* lines
   (*the caption on the picture or beside it, as each frame's label says*) and the two lines' headings (*shown as its
   scene's caption*, was *the caption over its scene*) -- the only sent words moved, so the reader is not told the
   caption is over the picture while the label says beside it; `FILM-RUBRIC.md` (F1-F8, S1-S9) untouched,
   `FILM_RUBRIC_VERSION` unmoved. A frame captured before 167 carries no layout and is labelled as 261's (*over*).
10. **The link's film (`FILM_JS`)**: `sig.line` and `chapter` are now the DRAWN caption and pill (the same words as the
    stage's on any scene; on the ask the stage's, as 263 draws it there); `layout`, `filmDisplay`, `ratio`, `stageBox`,
    `captionFrom` added. The copilot strip records its still's `data-ratio` and box (`still_of`) on every strip, and the
    leg notes them; the ratio is the picture's (no check: landscape on the fakes).

## Runs
All local, the main checkout's `.venv`, FakeSpeech / FakePictures / the fake transcriber / the fake readings / the
scripted runtime only, `KEEL_PICTURES` and both keys unset in the walk's shell; `lsof -i :18080 -i :5173` empty before
each walk; the leg booted the stack and tore it down. Times ET, 2026-11-25.

| run | result |
|---|---|
| walk 1 (02:11-02:28) `runs/20261125T071147Z-film-walk` (`make film-walk ENTRIES=08-fresco DOOR=fake WHY="167's local walk"`), exit 0 | **both halves green**, no probe. The problem: project `18105224-48e3-41c6-ac9f-61ce861e7a66`, 14 frames, 8 pictures, 0 capture faults, 7 of 7 answered on its link; the solution: project `ed915efd-f017-45dc-812f-312ad8efefba` on the problem's, 18 frames (the plate on both viewports, eight scenes), the sheet reused, 0 capture faults, the pilot's yes, 7 of 7 answered on its link. Every frame `layout: over`, `ratio: landscape` (FakePictures 48 x 32), the stage 358 x 239 on the phone and 620 x 413 on the laptop; every picture `ratio: landscape`, `drawn: other`; no frame left out. The building screen: opened while `building`, the wire `ready` before the plan drew (`drawn: false`); `replayed`: *7 frames planned · 7 passed* (problem) and *8 frames planned · 8 passed* (solution), every row `story-plan-row[data-scene][data-status=passed]` with its `Passed` mark, the tally held to its rows and the rows to the served plan |
| **walk 2, of record** (02:29-02:45) `runs/20261125T072907Z-film-walk` (`KEEL_FILM_PROBE=portrait make film-walk ENTRIES=08-fresco DOOR=fake WHY="167's local walk"`), exit 0 | **both halves green**. The problem half: project `1c72ea98-d8cd-45dc-9ab1-622a7ba7cc25`, 14 frames, 8 pictures, 0 capture faults, locked, 7 of 7 answered on its link, the founder's page read (bundle `runs/20261125T072935Z-film-08-fresco`). The solution half: project `9420941f-58da-41b2-ab71-cb7e43be9394` on the problem's, 18 frames (the plate on both viewports, eight scenes: *The task*, *What it solves*, *Better*, *What they get*), 9 pictures (the sheet reused from the problem film), 0 capture faults, the pilot's yes (`PUT idea/pilot` 200), locked on SOLUTION, 7 of 7 answered on its link, the founder's page read (bundle `runs/20261125T072935Z-film-08-fresco-solution`). **The frames as recorded**: every frame of both films `layout: over`, `film_display: contents`, `ratio: landscape` (FakePictures 48 x 32 -- the camera records it, no fault), the stage 358 x 239 on the phone and 620 x 413 on the laptop, the caption inside it; every picture `ratio: landscape`, `drawn: other`; no frame left out. **The plan ids**: the building screen opened (the wire already `ready`: the fakes draw at once), so the plan was read `replayed` on keel-web 263's own `FramePlan` from keel-cloud's served plan -- *7 frames planned · 7 passed* (problem) and *8 frames planned · 8 passed* (solution), one `story-plan-row[data-scene=n][data-status=passed]` a frame with its `Passed` mark, the tally held to its rows, the rows to the served `build.pictures.plan`. **The portrait probe** (32 x 48 pictures in the browser, `probe/frames/`): on both films the phone `layout: over`, the stage **358 x 537** (2:3), the caption inside it; the laptop `layout: column` (`film_display: grid`), the stage **372 x 558** (2:3; the founder's column, as keel-web 263's tasks say), the caption and the pill read from `story-side-line` / `story-side-chapter`, beside the stage, inside the window, nothing clipped on every scene (e.g. scene 4: the caption at x 852, 220 wide, beside a stage ending at x 824), every chapter read (*Who*, *The task*, *Today*, *Where it falls short*, *What it costs them*; *The task*, *What it solves*, *Better*, *What they get*); 0 probe faults |
| `make read-films RUN=<walk 2> DRY=1 FOUNDER=0` | two film calls written, nothing called: the problem's (22 images, 928 KB), the solution's (27 images, 1,077 KB); every scene frame labelled with its viewport and layout (*Frame -- scene 1 on the phone (390x844), the caption over the picture's lower third, a wide stage 358 x 239, ...*); no probe frame handed |
| `make read-screens RUN=runs/20261125T071207Z-film-08-fresco-solution DRY=1` (walk 1's) | 16 prompts, scope SOLUTION, nothing called (as 166's) |

## make unit
Both on the same siblings (this worktree's `stack.toml` copy: keel-cloud-docs `c7079b59`, keel-web `336eb477`):
- Before (the base `c0c80fa`, this worktree before any code change; 02:02-02:10 ET): **74 failed, 6169 passed, 169
  skipped** -- the siblings' moved words and pins of earlier specs (none of the film's, the camera's or the founder's
  building screens').
- After (the head, 02:53-03:01 ET, nothing else running): **74 failed, 6191 passed, 169 skipped -- no new red** (the
  lists diffed by name: the same 74 as the base's), the 22 of `tests/test_the_mirrors_of_263_167.py` green and
  `tests/test_the_solution_film_judged_166.py` green with its idea page moved (judgement call 4). An earlier full run
  beside walk 1's stack (02:21-02:32) read 75 failed: the one more, `test_sign_in_on_the_issuer_095.py::
  test_the_registered_cell_signs_in_and_lands_on_keel_web`, a 30 s click timeout under the load, green alone and green
  in the run of record.

## Commits
| Commit | FR | What |
|---|---|---|
| `a9d47b8` | -- | this file's T0..T4 |
| `946ca61` | FR-1..FR-3, FR-5 | the camera on 263's stage (the drawn caption, the layout, the ratio, the two rules, a frame left out, the picture's size), the building screens' plan and the failed lines, the watch in the film walk and its replay, the candidate frame's and the copilot still's ratio, the link's drawn caption, the reader's labels, the unit mirrors (`tests/test_the_mirrors_of_263_167.py`), 166's idea page moved to 263's held frame |
| `c3c67d5` | FR-1, FR-4 | the portrait probe (`KEEL_FILM_PROBE=portrait`, `DOOR=fake` alone) |
| `97cc3d6` | FR-2 | the watch said in the transcript (`building_read`) |
| `fd6f13c` | -- | an unused selector left out |
| `2fad779` | FR-2 | the transcript line's unit mirror |
| `d64057f` | -- | `quality/CYCLE.md`'s film runbook |
| `e18f86b` | FR-2b | keel-web 264's eval mirrors (the card's why outside `notPicked`, the fake record, the face's chip on the plate, DRIFT #121 / #122 answered and left open), their unit mirrors |
| (this commit) | FR-4 | this file: the runs, `make unit`, the judgement calls, open |

## DRIFT
No new entry: no product red met. keel-web 263's column, frame plan and stage read as its spec says on both films. FR-2b: #121 and #122 gain a status line -- *answered by keel-web 264 (`70147567`, `6da4c9ae`), to be confirmed by the next run of record* -- and stay open.

## Open
- **The paid run on five** can start (the founder's word), as spec 166's *Open* says, with this branch merged: the
  camera now reads 263's portrait stage on a 275 build. On Keel's door the pictures are 1024 x 1536, so the laptop
  frames are the column (`layout: column`) and the reader's labels say *the caption beside the picture*.
- **DRIFT #121 / #122** close only on the next run of record of spec 162's two reds (`problem · copilot` at step 4, `solution · avatar` at the plate) on a keel-web with 264 merged; the mirrors already read 264's card and plate.
- The live building screen's plan (the statuses moving, *checking*, *drawing again*, a reason beside a row, *{k} of {n}
  pictures kept*) is read only on Keel's door: on the fakes the build is ready before the plan draws and the plan is
  read `replayed` (all passed). A failed build's line with the reason (263 FR-10) is held by the unit mirrors and
  would be met on Keel's door (or by spec 162's failed-build walk in e2e-157).
- keel-cloud 275's *Open*: DRIFT #119's consumer entry (09-karsa) re-walked on `KEEL_PICTURES=openai` (the blank rule,
  the third draw) -- paid, on the founder's word; it is among the five.
- On the founder's player (`define/story/check`, `define/idea/check`) the laptop's words' column is at its 220 px floor
  (the founder's column is about 600 px; the stage 372 x 558), so a long line runs to several rows beside the stage
  (the probe: the solution's scene 5 at seven rows, whole and unclipped). keel-web 263's own *Open* (widening the
  founder's voice column is a layout decision outside it); the camera holds the column to *whole, unclipped, in the
  window* and the three-row rule to the phone, as FR-1 says -- recorded, not a fault.
- 275's line *{n} of {m} pictures drawn; scene {k} could not be ...* on a ready build with a frame left out is not drawn
  by keel-web 263 (its *Open*); nothing here reads it.
