# Tasks -- spec 170

Base: `origin/master` `59a5352` (169 merged at `eac199d`; specs 170 and 171 committed). Built 2026-11-25 by a builder
(Claude Opus 5.5) in the worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-170`, branch
`170-the-entry-screen-and-the-films-question`. Nothing paid: no model, no key, no vendor, no stack, no pip install (the
main checkout's `.venv`, symlinked, ignored), no network but `git fetch` / `git push` of this branch. keel-web's words
read from web master `04773133` (specs 266, 268, 269, 270, 271 merged; their specs and `git show master:<path>`,
read-only); keel-cloud 277's `dimension-cards.md` from keel-cloud-docs master `61ba9069` (read-only).

- [x] T0 Set up: the worktree's `.venv`, the base's `make unit` (the reds listed below), this file.
- [x] T1 FR-1 the entry screen (keel-web 266): `harness/interviewer_screens.py` -- *Test your mic* (`ai-mic-test`) ->
  *Say anything.* (`ai-mic-say`, the wave) -> *Your mic works.* (`ai-mic-heard`) -> **Begin** (`ai-start`); the intro's
  one line (`ai-intro-line`, `aiIntroLine`); the block's two lines; `SAY_HELLO`, `MIC_LABEL`, `MIC_BLOCK_HOW`,
  `START_THE_INTERVIEW` and the *Heard:* reader (`mic_heard`) gone; the old words found on a screen a DRIFT capture
  note (`entry_drift`), never a fault of the walk; the readers (`evals/three_views_strangers.py` intro / blocked checks,
  `evals/interviewer_leg.py`, IM17 in `evals/interviewer_marks.py`, v18 -> v19), the strangers' bundle
  (`harness/film_strangers.walk_summary`'s `entry`, `entry_faults` into the film's capture faults).
- [x] T2 FR-2 / FR-3 the verdict gone and the film's question (keel-web 268, 269): `harness/story_screens.py`
  `VERDICT_CARD` / `VERDICT_ASK` / `VERDICT_LATER` / `hear_verdict` / `film_yes_verdict_pilot` gone; `STORY_ASK` the
  new words, `film_ask_idea(name)`; `film_question` waits for Yes (`film-yes`) / No (`film-no`), reads the line and
  says *yes* aloud; `film-fix` never opened; the problem's yes lands on the window page, the solution's on the pilot
  ask; a retired verdict card met on the way is passed by the quiet and recorded (DRIFT capture). `evals/three_views.py`
  checks, `evals/three_views_report.py`, `quality/film_reader.founder_lines` (the film's question beat).
- [x] T3 FR-2b the vendored Prevalence card: `quality/readers/dimensions.md`'s Prevalence gate sentence re-cut to
  keel-cloud 277's `dimension-cards.md`; `CARDS_SHA256` (and the pin chain's `CARDS_SHA256_141`) re-pinned;
  `CARDS_MOVED_162` checked.
- [x] T4 FR-2c the building screen (keel-web 270): `PLAN_JS`, `read_plan`, the rows' looks and chip words, the bar's
  legend (`plan_legend`, `legend_holds`), `.story-build-steps` gone, *Drawing your story.* and no `story-q` while it
  builds; `harness/film_frames.watch_building` / `building_faults`, `evals/run_film.building_read`.
- [x] T5 FR-4 / FR-5 the tests and `make unit` after; nothing here writes respondent words; this file's sections.

## How each FR is met

| FR | Where | What holds |
|---|---|---|
| FR-1 | `harness/interviewer_screens.py` (`BEGIN`, `SAY_ANYTHING`, `MIC_SAY_ID`, `MIC_WORKS`, `MIC_NOT_HEARD`, `MIC_BLOCK`, `MIC_SOUND`, `ai_intro_line`, `INTRO_LINE_ID`, `ENTRY_IDS_BEFORE_266`, `ENTRY_WORDS_BEFORE_266`, `entry_drift`; `Player.intro` / `mic_test` / `mic_block`); `evals/three_views_strangers.py` (`intro_checks`, `blocked_checks`, `block_line`); `evals/interviewer_leg.py`; `evals/interviewer_marks.py` (IM17, v19); `harness/film_strangers.py` (`entry_shape`, `entry_faults`); `evals/run_film.py` (the strangers' capture faults); `harness/story_screens.py` `WALK_IDS` | *Test your mic* pressed, the wave and *Say anything.* read while it listens (the button not drawn), a sound made through the seam (its words never read back), *Your mic works.* (`ai-mic-heard`) and **Begin** (`ai-start`) waited for and pressed; the intro's one line (`aiIntroLine`, minutes in words up to ten) checked; the block's one line. `SAY_HELLO`, `MIC_LABEL`, `MIC_BLOCK_HOW`, `START_THE_INTERVIEW`, `mic_heard`, `ai_intro_spoken` / `_asks` / `_chips`, `ORB_NOT_A_PERSON` and spec 099's held stop in `mic_test` are gone. 256's words or ids on an intro are a check with `stop=False` and `drift: (capture) keel-web 266 ...` on the three-views walk, and on the film's strangers one capture fault in `measures.faults` (into `runs/DRIFT.md` through `quality.film_table`); the walk presses the same ids either way |
| FR-2 | `harness/story_screens.py` (`VERDICT_IDS_BEFORE_268`, `Conversation.land_past_verdict`, `StoryWalk.story_yes`, `IdeaWalk.film_yes_pilot` / `film_yes_to_money`); `evals/three_views.py`, `evals/three_views_report.py` | `VERDICT_CARD`, `VERDICT_ASK`, `VERDICT_LATER`, `hear_verdict`, `film_yes_verdict_pilot` and `story_yes(verdict=)` are gone. After the film's yes the walk waits for the window page (problem) or the pilot card (solution), never for a verdict card; one met on the way (a keel-web before 268) is passed by the quiet as before and reported (`verdict_seen`, a capture note on the founder's check). `VERDICT_LINE` / `SOLUTION_VERDICT_LINE` stay (still served on the wire, `verdict_wire_checks`) |
| FR-2b | `quality/readers/dimensions.md`, `quality/cards.py`, `tests/test_cloud_219_228_mirror_141.py` | Prevalence's card is keel-cloud 277's `dimension-cards.md` card byte for byte (the gate sentence: *In {window}, have you encountered this issue?*, the clause noted, never refused); `CARDS_SHA256` and the pin chain's `CARDS_SHA256_141` moved `dbcb2196...` -> `aec2abb9...`; `CARDS_MOVED_162` unchanged (the cloud's copy now differs in those four alone) |
| FR-2c | `harness/story_screens.py` (`PLAN_LOOKS`, `PLAN_LOOK_LABEL`, `PLAN_DRAWING`, `PLAN_DRAWING_AGAIN`, `PLAN_NO_PICTURE`, `BAR_PLANNING`, `BAR_VOICING`, `DRAWING_SAY`, `PLAN_JS`, `plan_look`, `plan_word`, `frames_done`, `plan_legend`, `plan_row_faults`; `building_then_story` / `building_then_film`); `harness/film_frames.py` (`plan_held`, `watch_building`, `building_faults`); `evals/run_film.building_read`; `evals/three_views.py` | the plan read is the bar's legend (`story-bar-legend`, its value / max / phase) and each row's status, look, chip word (its leading *·* dropped), mark label, reason, thumbnail; each read held to keel-web 270: the legend one its rows allow (*planning the frames* / *{done} of {n} frames done* / *voicing the lines*), every row's look, word and mark from its status (`kept` done), a thumbnail on a done row only, 263's tally not drawn. `plan_tally` and `.story-build-steps` are gone; the founder's building check holds *Drawing your story.* as the one line, no `story-q`, no steps list (`stop=False`) |
| FR-3 | `harness/story_screens.py` (`STORY_ASK`, `STORY_ASK_BEFORE_269`, `film_ask_idea`, `FILM_YES`, `FILM_YES_ID`, `FILM_NO_ID`, `FILM_FIX_ID`, `Conversation.film_question`); `evals/three_views.py`; `quality/film_reader.founder_lines`, `evals/run_film.py` (`film_ask`) | at the film's end the walk waits for **Yes** / **No**, reads the question (`story-check-said` / `idea-story-said`), says *yes* aloud through the seam and never presses or opens `film-fix`; the checks hold *Does this film show the problem accurately?* / *Does this film show {name} accurately?*. On a keel-web before 269 (no Yes drawn) the quiet answers as before, recorded `buttons: false`. The film judge's founder transcript ends on *After the film, Keel asks: {the question}* where the record carries `film_ask` (a record before it keeps its verdict line) |
| FR-4 | `tests/test_the_entry_screen_and_the_films_question_170.py` (new, 9), `tests/test_interviewer_screens.py`, `tests/test_both_speakers_160.py`, `tests/test_heard_line_099.py`, `tests/test_interviewer_marks.py`, `tests/test_three_views_157.py`, `tests/test_the_mirrors_of_263_167.py`, `tests/test_orb_159.py`, `tests/test_cloud_219_228_mirror_141.py`, the version pins (`test_controls_089`, `test_founder_walk_076`, `test_recorded_path_074`) | the words and ids held to keel-web master `04773133` (266's constants, `aiIntroLine`, 269's `filmAsk` / `filmAskIdea`, 270's `STORY.plan`, FramePlan's ids); the retired ones absent from keel-web and from the harness; the mic test on a 266 page (passes on three ticks of sound); the intro and a 256 intro read, the latter named as drift; the film's question answered yes on a 269 page, a 257 page passed by the quiet with its verdict named; the building screen watched on a 270 page and its legend / rows held; `make unit` below |
| FR-5 | -- | nothing here writes respondent words: the entry, the film's question and the building screen are read from the screens; `MIC_SOUND` is only the seam's sound and never read back |

## Judgement calls
1. **266's whole intro, not only the button.** FR-1 names the button's states; keel-web 266 FR-1 also retired the
   sub-line, the study line, the asks line and the chips. `intro_checks` would fail on every 266 screen with them, so the
   intro's one line (`ai_intro_line`) is mirrored too and the retired ids join the DRIFT capture note.
2. **The sound.** The seam still says `MIC_SOUND` (*hello*) to make the level pulse (three ticks = keel-web's 300 ms);
   `mic_test(sound=...)` keeps the callers' positional `"hello"`, and nothing reads the words back (the warm-up
   transcription is ignored by the page).
3. **IM17 bumped to v19.** The mark read *Heard: hello* and the writing state, both gone; it now reads the wave with
   *Say anything.* (button not drawn) and *Your mic works.* with **Begin** -- `INTERVIEWER_MARKS_VERSION` 18 -> 19 with its
   note, the four version pins moved. The paid s012 re-score stays the founder's.
4. **Old screens are passed, not waited on.** A keel-web before 269 draws no Yes: the walk waits its normal time, then
   answers by the quiet as before (`buttons: false`); a verdict card before 268 is passed by the quiet and reported. So
   the walk never stops on an old screen; the checks name it as a capture note.
5. **The film judge's transcript.** `founder_lines` said *After the film, Keel says: {verdictLine}*, which 268 no longer
   says; the film record now carries `film_ask` and the transcript ends on the question. A record without `film_ask`
   (made before) keeps its verdict line, so old bundles read as they were.
6. **FR-2b re-pin.** The eval's Prevalence card is replaced by keel-cloud 277's card whole (only the gate sentence
   differed); `CARDS_SHA256` and `CARDS_SHA256_141` move to `aec2abb9...`; `CARDS_MOVED_162` keeps its four (Prevalence
   now matches the cloud's, so it does not join them). The cloud's own `RespondentReview.CARDS_SHA256` (`061c0777...`) is
   its copy's, as before.
7. **FR-2c names.** The brief said the rows carry `data-state`; keel-web 270's `FramePlan` keeps `data-status` (the
   served status) and adds `data-look`: both are read. 263's *tally* key became `legend` in the plan read, the watch's
   record (`legend_rule`, `legend_holds`, `row_faults`) and `building_read` (`legends`); the voice lines' state is not on
   the page, so once every frame is settled either legend is accepted.
8. **`film_question` on `Conversation`.** The problem's and the solution's films share it (and `land_past_verdict`).
9. **`make unit` on archived siblings**, as 168 / 169: this worktree's `stack.toml` (never committed; restored) pointed
   at `git archive` copies in the scratchpad (`sib170/`: keel-cloud-docs master `61ba9069`, keel-web master `04773133`,
   keel-runtime `3988131`, keel-connect-skill `c677950`); the keel-cloud Gradle gate beside me and the sibling checkouts
   untouched.

## make unit
Both on the same archived siblings (judgement call 9), the main checkout's `.venv`:
- Before (the base `59a5352` + T0's tasks.md, no code change; 16:30-16:39 ET): **94 failed, 6198 passed, 169 skipped**.
- After (`40cfe41`; 16:59-17:06 ET): **79 failed, 6228 passed, 169 skipped -- no new red** (the lists diffed by
  name). Fifteen of the base's reds are green: the fourteen this spec owed (keel-web 266's words and ids in
  `test_interviewer_screens`, `test_both_speakers_160`, `test_heard_line_099`, `test_three_views_157`'s AiIntro /
  IdeaBoxes selectors and the story lines, 263's words in `test_the_mirrors_of_263_167`, the cards' digest in
  `test_cloud_219_228_mirror_141` and `test_the_solution_walked_162`) and
  `test_overview_board_markup::test_the_status_word_is_read_off_the_pill_with_its_tone_and_its_glyph`, which is not
  this spec's and passed and failed on separate runs here (a flaky page test, named under Open). The remaining 79 are
  the base's (none touched here).

## Commits
| Commit | FR | What |
|---|---|---|
| `802cd38` | -- | this file's T0..T5 |
| `40cfe41` | FR-1..FR-5 | the entry screen, the verdict gone, the film's question, the Prevalence card, the building screen, the tests |
| (this commit) | -- | this file: how each FR is met, the judgement calls, `make unit`, open |

## DRIFT
No new entry: no stack was run here, so no product red was met.

## Open
- **The acceptance on a stack** (`DOOR=fake` journeys on keel-web 266/268/269/270) waits on the next walk; nothing was
  run here.
- The paid s012 re-score of IM17 v19 is the founder's call.
- `test_overview_board_markup`'s pill test is flaky here (red on the base run, green on two later ones).
- The base's other reds (the contract 90 -> 94 pins, the connect `VERSION` 24, the charge tables, the git-dependent
  165/166 tests on non-git sibling copies, ...) are not this spec's and are unchanged.
