# Tasks -- spec 172

Base: `origin/master` `3d6ad49` (171 merged at `dd4f124`; spec 172 committed). Built 2026-11-26 by a builder (Claude
Opus 5.5) in the worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-172`, branch
`172-the-marks-for-the-four-states-and-the-short-questions`. Nothing paid: no model, no key, no vendor, no stack, no pip
install (the main checkout's `.venv`, symlinked, ignored), no network but `git fetch` / `git push` of this branch.
keel-web's words read from web master `edc30008` (274, 275, 276, 277 merged; read-only); keel-cloud 283 / 284 from
keel-cloud-docs master `38e8c5fa` (contract 96); keel-cloud 285's words from its spec and, at the end, from
keel-cloud-docs master `496ded8b` (285 merged; read-only).

- [x] T0 Set up: the worktree's `.venv`, the base's `make unit` on archived siblings (the reds listed below), this file.
- [x] T1 FR-1 the founder's beats (keel-web 275): `harness/story_screens.py` -- `LONG_BEAT_SUB`, `THINK_LINE`, `THINK_MS`
  and the 20 s / 60 s asks gone; `WAIT_MS` 8 s; the orb's `data-state` asking | hearing | waiting | thinking | paused
  (272's six read through the mapping); the state words; `beat-ask` read once (never a second); no *What I hear* and
  no founder lines (`beat-no-transcript`); the card's rows in order; a done word alone after the card ends the beat;
  *none* on the setup beat closes at once; `beat-question-fold`; every beat a long beat. The legs' checks
  (`evals/three_views.py`).
- [x] T2 FR-2 the respondent's player (keel-web 274): `harness/interviewer_screens.py` -- the story's status line, the
  acknowledgement `ai-story-got-it` (*Got it. Thank you.*), the ask once at 8 s, every passage captioned
  (`ai-passage-caption`), the four states on the player's orb; the strangers say the story in two parts with a pause
  under 8 s and end on *that's it* (`evals/three_views_strangers.link_walk`, `harness/film_strangers.py`); the dry
  run's story closed by the done word and acknowledged (`evals/interviewer_leg.py`).
- [x] T3 FR-3 the boxes (keel-web 276): **Finalize the problem** / **Finalize the solution** (`boxes-yes`) pressed on
  every board; a page that moved on by itself within 10 s of Keel's line is a fault (`boxes-auto-advanced`); Keel's line
  read once; the sheet's step two reads only *What do you want to change?*.
- [x] T4 FR-4 the solution's frames (keel-cloud 283, keel-web 276): `idea-building` read as the problem's (chapters
  before | task | joy, chips *Opening*, *What it does*, *What they get*, *drawing again* rows with a `note`); a failed
  build a fault only on *no picture could be drawn*; `frames` / `chapters` in the film table; a `solves` / `better`
  chapter a DRIFT line; contract 96.
- [x] T5 FR-5 the recap cut (keel-cloud 283 FR-8): five problem lines before the check on a solution link, eight on a
  problem link; the copilot card the same five.
- [x] T6 FR-6 the short questions (keel-cloud 285): `harness/three_surfaces.py` and `harness/solution_surfaces.py` carry
  285's frames; a link with no film keeps the old frames by the item's `framed`; the screener at most twelve words.
- [x] T7 FR-7 versions and record: `INTERVIEWER_MARKS_VERSION` 20; the DRIFT lines; `harness/interviewer_fake.py` serves
  the new words; `runs/DRIFT.md` force-added.
- [x] T8 FR-8 the tests on fixtures and `make unit` after; this file's sections.

## How each FR is met
- **FR-1 (web 275)** -- `harness/story_screens.py`: every beat is a long beat; `LONG_BEAT_SUB`, `THINK_LINE`, `THINK_MS`
  and the 20 s / 60 s asks are gone. The orb's `data-state` is read as `asking | hearing | waiting | thinking | paused`,
  and 272's six states map onto these through `orb_state`. `BEAT_ASK` (`beat-ask`, *Anything else? Say "that's it" when
  you are done.*) is read once after `WAIT_MS` 8 s of quiet, and a second ask is a fault (`asks_seen`). The card's rows
  are read in order, then the walk says *That's it.* alone and expects the next question (`close_by_done_word`,
  `card_then_ask`). *none* on the solution's setup beat and on the problem's beat 7 closes at once. `beat-question-fold`
  is read. The absence of *What I hear* (`story-heard`) and of the founder's lines (`story-words li[data-who=you]`) is
  the mark `beat-no-transcript` (`no_transcript`). The legs' checks are in `evals/three_views.py`. DRIFT #146.
- **FR-2 (web 274)** -- `harness/interviewer_screens.py`: `Player.say_story` says the story in two parts across a
  pause of `STORY_PAUSE_S` 4 s, which is past the page's 2.5 s `PAUSE_MS` and under 8 s, and ends on *That's it.*. A
  follow-up is one part plus the done word. `Player.long_close` reads the close as `ai-story-got-it` (*Got it. Thank
  you.*), never as the short answers' hold. `STORY` is 274's status line; 074's line is kept as `STORY_BEFORE_274`.
  `ai-passage-caption` is logged for every passage, and the player's orb is read in the four states.
  `evals/three_views_strangers.link_walk` and `evals/interviewer_leg.py` (the dry run and the story walk) close by the
  done word. `harness/film_strangers.py` puts the telling on the walk record (`told`). `told_faults` makes a capture
  fault (never the person's) of a story that the page closed on the pause or held instead of acknowledging. It is called
  in both halves of `evals/run_film.py`. IM22 re-pinned. DRIFT #147.
- **FR-3 (web 276)** -- `Conversation.finalize_boxes`: Keel's line *Take your time. When you are done, press Finalize
  the problem / the solution.* is read once. The table is watched for `AUTO_ADVANCE_S` 10 s, and a page that moves on
  by itself, or sends the confirm, is the fault `boxes-auto-advanced`. Then `boxes-yes` is pressed. `fix_one_box` runs
  the sheet: the box is named, step two reads only *What do you want to change?*, and the box is shown back before the
  *yes*. `BOXES_ASK` / `IDEA_BOXES_ASK` are now `*_BEFORE_276`. DRIFT #148.
- **FR-4 (cloud 283, web 276)** -- `IDEA_CHAPTERS` is `before, task, joy`; 271's five chapters are
  `IDEA_CHAPTERS_BEFORE_283`. The plan's chips are held to the served rows (*Opening* on scene 1, *Before that*, *What
  it does*, *What they get*; never *Solves* / *The advantage*), with the `note` under a frame drawn again
  (`plan_chip_faults`, `story-plan-chip`, `story-plan-note`). A `solves` / `better` chapter gives one DRIFT line each
  (`idea_chapter_drift`). A build that failed on a chapter is a DRIFT line owed by keel-cloud 283 FR-3. The walk's own
  failed-build fault is only *no picture could be drawn* (`film_frames.failed_build_fault`). When the reader refuses
  twice, the walk ends ready with its frames (`evals/three_views.failed_build_walk`). The film table carries `frames` /
  `chapters` (`quality/film_table.frames_chapters_line`, `measures.chapters`). Contract 96. DRIFT #149.
- **FR-5 (cloud 283 FR-8)** -- `story_screens.recap_verdict` / `recap_of`: a solution link reads the problem film's
  `who`, `shortfall` and `cost` scenes in order, with no ask line. That is `RECAP_LINES` five lines on 268's seven-scene
  film. A problem link keeps eight lines. The copilot card's gate passage carries the same five
  (`solution_surfaces.card_problem_lines`). DRIFT #150.
- **FR-6 (cloud 285)** -- `FREQUENCY_FILM`, `IMPORTANCE_FILM`, `COMPATIBILITY_FILM`, `RELATIVE_ADVANTAGE_FILM` and
  `ADOPTION_*_FILM` in `harness/three_surfaces.py` / `harness/solution_surfaces.py` hold 285's words where the item is
  framed `film`. An item framed `clause`, or with no `framed`, keeps 272's / 269's frames. The screener is at most twelve
  words (`screener_faults`). DRIFT #151.
- **FR-7** -- `INTERVIEWER_MARKS_VERSION` 19 -> 20 (`evals/interviewer_marks.py`). `harness/interviewer_fake.py`
  serves the long-answer lines and `FILM_FRAMES` / `film_question`, so the stub walks read the new words. `runs/DRIFT.md`
  #146-#151 force-added. AGENTS.md has the spec 172 line.
- **FR-8** -- `tests/test_the_marks_follow_the_batch_172.py` (25 tests, fixtures and fake pages only) plus the touched
  tests that follow the new words (157, 158, 158c, 159, 161, 162, 166, 167, 074, 075, 076, 089, 099, the interviewer
  marks and screens). No eval run, no model call.

## Judgement calls
1. **The two-part story's pause is 4 s** (`STORY_PAUSE_S`). It has to be past the page's 2.5 s `PAUSE_MS` to test that
   the window stays open, and under the spec's 8 s so it never triggers the ask. A founder's two-part beat is watched
   across `TWO_PART_QUIET_S` 12 s.
2. **The auto-advance watch is 10 s** (`AUTO_ADVANCE_S`), as FR-3 says. Both kinds of move count as the fault: the page
   moving on, and the confirm being sent.
3. **285's cap is per sentence.** The adoption frame with the setup is two sentences, so the film frames are checked at
   no more than 17 words per sentence, not per frame. The person's screener is held to twelve words overall.
4. **`framed` absent = the old frames.** A cloud before 285 serves no `framed`, so the harness treats it like `clause`
   and keeps 272's / 269's words. A link with no film gets the same treatment.
5. **`InterviewTimeline` is not read.** No route of it is walked by this harness, so the copilot card stands for it in
   FR-5 (DRIFT #150).
6. **The S-005 follow-up walk is not re-cut.** It pressed *Back* in a follow-up's hold, and since 274 a follow-up has no
   hold. This is owed to the next interviewer-leg spec (DRIFT #147).
7. **A retired chapter is DRIFT, not a fault.** A served `solves` / `better` chapter is the product's to fix (283), so
   it is recorded and does not fail the walk.
8. **`make unit` after, on the main checkouts.** For the final run, this worktree's `stack.toml` (not committed;
   restored afterwards) pointed `keel_cloud` at `/Users/athulrajeev/Documents/projects/keel-cloud-docs` (master
   `496ded8b`, 285 merged) and `keel_web` at `/Users/athulrajeev/Documents/projects/keel-web` (master `edc30008`), both
   read-only, as spec 154's builder did. The repo has no environment override for these paths. The before run had used
   archived copies (`sib172/`, which were removed for disk space).

## make unit
The main checkout's `.venv`:
- **Before** (base `3d6ad49` + T0, archived siblings at keel-cloud-docs `38e8c5fa` and keel-web `edc30008`; finished
  03:27 ET): **87 failed, 6246 passed, 169 skipped**.
- **After** (this branch at `fc4b3d4`, siblings = the main checkouts keel-cloud-docs `496ded8b` and keel-web
  `edc30008`; 04:08-04:16 ET): **89 failed, 6285 passed, 157 skipped**.
- **Diffed by name:** 77 reds are common to both runs. 10 are gone: the story-sub pin, 167's words, 162's failed-build
  words, and 157's StoryTurn / VoiceStage selectors, which now follow 274-276; and the git-dependent 165 / 166 tests,
  which pass on a real git checkout and could not on non-git copies. 12 are new, and **none are this branch's**. The
  twelve are `test_corpus_r19`, `test_haiku_5_5_121`, `test_instruction_brief_facts`, `test_instruction_compare`,
  `test_instruction_spoken` (4), `test_instruction_validate`, `test_lock_frontier_110`, `test_money_cards_redrawn_118`
  and `test_report_marks` (corpus overview). They read keel-cloud's registry and engine, which moved from `38e8c5fa` to
  `496ded8b`. For example, compatibility's `fixed_answer_codes` is now `['yes', 'no']`, while the corpus record pins
  `yes_easily / only_with_help / no`. All 12 also fail on the base `3d6ad49` against the same siblings (a detached
  worktree run only on those 12, 12 failed; removed afterwards). They are owed to the next corpus / mirror re-pin, not to
  172.
- `test_cloud_245_250_248_web_186_190_mirror_154[call-see-answers]` (web 273) stays red. It is a base red, red in both
  runs: the 154 mirror's pin, not this spec's.
- 172's own 25 tests are green.

## Commits
| Commit | FR | What |
|---|---|---|
| `1bafd03` | -- | this file's T0..T8 |
| `ce46c76` | FR-1..FR-4 | the four states, one ask, finalize by hand, the solution's frames; IM22 on 274 (v20) |
| `22bb942` | FR-5..FR-7 | the recap's five lines, the short frames by `framed`, the fake door's words, DRIFT #146-#151, the tests |
| `fc4b3d4` | FR-2 | the strangers' telling on the walk record (`told`), a story closed on the pause a capture fault; AGENTS.md |
| (this commit) | -- | this file: ticked, how each FR is met, judgement calls, `make unit` |

## DRIFT
`runs/DRIFT.md` (force-added):
- #146 FR-1 (web 275): the founder's beats in the orb's four states, one ask, ended by a done word alone after the card.
- #147 FR-2 (web 274): the respondent's story in two parts closed by *that's it*, acknowledged *Got it. Thank you.*;
  the S-005 follow-up walk owed to the next interviewer-leg spec.
- #148 FR-3 (web 276): the boxes finalized by hand (`boxes-yes`); `boxes-auto-advanced`.
- #149 FR-4 (cloud 283, web 276, contract 96): the solution film in three chapters, read on the building screen as the
  problem's; #144 / #145 (failed at `solves`) to be confirmed gone by the next run of record.
- #150 FR-5 (cloud 283 FR-8): the solution link's problem recap, five lines.
- #151 FR-6 (cloud 285, keel-cloud-docs `496ded8b`): the short frames by the item's `framed`.

## Open
- **The acceptance on a walk of record**: the first walk on a stack with cloud 283-285 and web 274-276 (paid, on the
  founder's word). Nothing was run here.
- **The 12 corpus / registry reds** against keel-cloud-docs `496ded8b` (see above) wait for a re-pin spec.
