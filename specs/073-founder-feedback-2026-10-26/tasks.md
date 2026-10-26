# Tasks 073 -- The harness follows keel-web 113 and 114 (the founder's staging review of 2026-10-26)

Branch `073-founder-feedback` off master `99c48b2` (worktree `wt/eval-073`). The products, read only: keel-web master
`2477fb0` (113 -- the context step's four states, *A word from you* behind `READY_WORD_SCREEN`, the player's crop, the
Overview's lead -- and 114, the welcome per scope; the manifest at 42 keys) and keel-cloud-docs master, whose checkout
stood at `d6837fe3` = `bc2505c6` + three commits under `canon/designs/noise-capture-check-2026-10-26/` alone (no
`src/` change, D-01). The stack built from those checkouts through the four symlinks beside the worktree, keel-runtime
0.8.0 bundled in keel-connect-skill. No paid command, no key.

One commit per FR, each gated on `make unit` green. FR-4 was committed first: master was one red against keel-web 114,
and that red was FR-4's own subject (D-02).

## Unit

| | passed | failed | skipped |
|---|---|---|---|
| master `99c48b2` against keel-web `2477fb0` (before any change) | 3,298 | **1** | 53 |
| FR-4 `3ceb5fa` | 3,316 | 0 | 53 |
| FR-1 `deae906` | 3,332 | 0 | 53 |
| FR-2 `fbb2190` | 3,357 | 0 | 53 |
| FR-3 `0072464` | 3,360 | 0 | 53 |
| FR-5 `4b1dd84` | 3,363 | 0 | 53 |
| FR-6 (this commit) | 3,364 | 0 | 53 |

(The hand-off's 3,299 / 53 at `99c48b2` was against keel-web before 114; against `2477fb0` the manifest test is red.)

## FR-4 -- the welcome per scope -- `3ceb5fa`

- [x] T001 `evals/guide_marks.WELCOME_CLIPS` / `welcome_clip(scope)`: keel-web 114 `welcomeClipOf` -- ALL (and no scope)
  `welcome`, PROBLEM `welcome-problem`, SOLUTION `welcome-solution`, SOLUTION_COMMERCIAL `welcome-solution-money`,
  COMMERCIAL `welcome-money`.
- [x] T002 `GuideWelcome.clip()`: the sheet's `data-clip`, the face's `src` / `poster` and its track's `src`. `pass_by`
  reads it before Skip; `MarketStep.welcome` keeps the pass; `create_project` puts it in `seen["welcome_pass"]`.
- [x] T003 `leg_welcome` (S-005/006/007/014, ALL) holds `welcome` and `/guide/welcome.mp4` at the first open;
  `corpus_scenario.hold_the_welcome_clip` holds the scope's key and its three files on S-015 and S-016, right after
  the project (`scope_journey.run`).
- [x] T004 The G-series count the four new clips: `test_every_present_clip_in_keel_webs_manifest_is_one_the_marks_know`
  knows them (master's red); G12 reads every present clip's captions, 42 on S-005's run. No mark reads its record
  differently: `GUIDE_MARKS_VERSION` stays 3.
- [x] T005 Unit `tests/test_welcome_per_scope_073.py` (17): the key per scope, the sheet read off 114's markup, the hold
  on both scoped journeys and six faults, the hold's place in the run, the four clips' files in keel-web's checkout.

## FR-1 -- the context step's flow -- `deae906`

- [x] T010 `Corridor.context` installs `_CONTEXT_STATES_JS` before Save: a MutationObserver keeping every state the step's
  root names (`data-context-state`) with what it draws -- the form's four boxes and Save; the wait's *Keel is reading
  your four answers.*, `.waitco__elapsed`, `.phasebar`, `.truth`, no `.cfield`, no Save; the card's sentence, *Yes,
  that's it*, *Edit*, no box -- booleans and counts merged over a state's stay, its words the last it drew (D-03).
  `Corridor.context_states`.
- [x] T011 `leg_context` holds form -> wait -> card on every walk (`context_states_faults`; a finding on a back-test).
- [x] T012 S-005 (`run(..., context_edit=True)`): after the problem's opener, `context_reopened` -- the confirmed state
  (`Corridor.context_confirmed`: the sentence the card's, *Continue to the problem*, *Edit*, no box), then *Edit*: the
  form, the four boxes, Countly's `{4, WEEKS}` and the occasion filled with what was confirmed; nothing saved (the wire
  still CONFIRMED). The four states asserted on S-005.
- [x] T013 Unit `tests/test_founder_feedback_073.py` FR-1 (16, +1 in FR-6): the tracker over keel-web's markup in a real
  page, a late-mounting wait merged, a form drawn again named, eleven faults, S-005 alone re-opening.

## FR-2 -- *A word from you* is not walked -- `fbb2190`

- [x] T020 `Corridor.word_pilot_and_lock` (its name kept: callers and stubs) waits for the step's first visible screen
  (`/define/ready/pilot`; the problem study `/define/ready/interviewer`), opens `/define/ready/word` once and waits for
  the redirect back to it, then the pilot (*1 of 2*), Continue, who asks (*2 of 2*); the problem study who asks alone,
  no counter. `ready = {landed, word_redirect, word_drawn}`; `_hold_no_word` holds them. `before_counters`:
  `["1 of 2", "2 of 2"]`, `[]` in the problem study. The back-test camera's `ready-word` slug goes.
- [x] T021 The pitch dropped: the interviewer leg's `_founders_word` (`PUT word` with `FOUNDERS_WORD` after the lock,
  call 149) is gone -- a founder has no screen to write one on.
- [x] T022 The thank-you's default words on the respondent's last screen: `Interview.walk` reads `.iv-done__word` and
  whether the screen is the thank-you or the gate's exit (D-04); `thanks_faults` / `_hold_the_thanks` on every text
  link -- the served thanks *Thank you -- your answers have gone to {first}.*, drawn as served, no `done.word`, no word
  section.
- [x] T023 Re-pinned, the marks that counted the word screen:
  - **SC2** (`SCOPE_MARKS_VERSION` 1 -> 2): step 5 counts two screens, none in the problem study (was three; two).
  - **IM5** (`INTERVIEWER_MARKS_VERSION` 7 -> 8): with no word stored, every role's THANKS clip is the default
    thank-you and nothing after it (`THANKS_DEFAULT`, keel-cloud `InterviewComposer.done` through
    `PassageComposer.said`); a word stored by another door still owes the old six-word rule.
- [x] T024 Unit: `test_founder_feedback_073.py` FR-2 (19), `test_interviewer_marks.py` (v8, IM5's no-word path, four
  faults), `test_study_scopes.py` and `test_drifts_95_97_closed.py` follow the two screens.

## FR-3 -- the Overview card's lead -- `0072464`

- [x] T030 `Answers.board` reads each panel's `.rp-plead` count; `report_marks.overview_faults` holds it absent on the
  full Overview (heading and pill, every row as before).
- [x] T031 `Answers.brief` reads each page's panel leads; `binding_faults` holds page one's to `instructions/overview.py`'s
  drawing from the wire and counts them as the sheet's own words (keel-web 113 J-13).
- [x] T032 `REPORT_MARKS_VERSION` 1 -> 2 (report_overview and report_binding read their record differently). The
  instruction eval's zero-spend `report_overview` (`instructions/overview.py`) is untouched.
- [x] T033 Unit `tests/test_report_marks.py`: the faithful report follows 113; two binding faults; v2's own case.

## FR-5 -- the player's crop -- `4b1dd84`

- [x] T040 `Player.band()`: `data-band`, `aiv-stage__face--band`, the band's one video, `ai-band-blur`; `stage()` carries
  it; the AI link's walk records `record["ai_band"]`; no mark reads it (D-05).
- [x] T041 Unit: the reader over 113's markup, a face in the table and one not; `stage()`'s video selector finds the band's
  video.

## FR-6 -- nothing else moves -- this commit

- [x] T050 `MARKS_VERSION` 20 and corpus `REVISION` 16 unchanged (`test_marks_and_revision_do_not_move`); no corpus,
  registry, fixture or golden number moved; `GUIDE_MARKS_VERSION` 3, `CONTACTS_MARKS_VERSION` 2,
  `FEEDBACK_MARKS_VERSION` 1 unchanged.
- [x] T051 The two fixes the first S-015 runs found (D-03, D-04), with their unit case. AGENTS.md: the spec 073
  paragraph, `SCOPE_MARKS_VERSION` 2. This file.

## The journeys (local stack, keel-cloud-docs `d6837fe3` (= `bc2505c6`'s `src/`) + keel-web `2477fb0`, the scripted executor)

`docker ps` before `make up`: only `focused_robinson` (an unrelated postgres). Booted with `make up`, the journeys run one
at a time with `make eval K=...`, torn down with `make down`. Runs of record on `4b1dd84` (FR-5) with this commit's
harness change in the tree uncommitted (`versions.json` dirty: `evals/corpus_scenario.py`, `harness/vectors_screens.py`,
`tests/test_founder_feedback_073.py` -- byte for byte this commit's code; keel-web dirty only by its own `.idea/`):

| Journey | Run | Result |
|---|---|---|
| S-015 | `runs/20261026T173622Z-s015-problem-only` | **passed** (91 s), SC1-SC7 7 of 7 (v2), welcome `welcome-problem`, counters `[]` |
| S-016 | `runs/20261026T173824Z-s016-money-only` | **passed** (82 s), SC1-SC7 7 of 7 (v2), welcome `welcome-money`, counters 1 of 2 / 2 of 2 |
| S-005 | `runs/20261026T173952Z-s005-countly` | **passed** (313 s): four context states, Edit filled; IM 23 of 23 (v8, IM5 `thanks: 1, off: []`); guide 17 of 17 (G12 42 clips); report 5 of 5 (v2); crop `CHUKWU` band |
| S-006 | `runs/20261026T174528Z-s006-paidly` | **passed** (347 s): IM 29 of 29 (v8, IM5 `thanks: 2`); report 5 of 5 (v2) |
| S-007 | `runs/20261026T175127Z-s007-mulchrun` | **passed** (134 s): report 5 of 5 (v2) |
| S-014 | `runs/20261026T175349Z-s014-green` | **passed** (136 s): report 5 of 5 (v2) |

On every journey the context step read form -> wait (the status line, the counter, the phase bar, the truth card; no field,
no Save) -> card (*Yes, that's it*, *Edit*, no box); the last step landed on the pilot (who asks on S-015) and the word's
address redirected there; every text link that reached the thank-you drew *Thank you -- your answers have gone to Eval.*
with no word.

## Discovered

- D-01 keel-cloud-docs' checkout stood at `d6837fe3`, three commits past the named `bc2505c6`; all three add files under
  `canon/designs/noise-capture-check-2026-10-26/` only (`git diff --name-only bc2505c6 d6837fe3`), so the built cloud is
  `bc2505c6`'s. Not changed.
- D-02 Master `99c48b2` was red against keel-web `2477fb0`: `test_every_present_clip_in_keel_webs_manifest_is_one_the_marks_know`
  did not know the four scoped welcomes. That is FR-4's subject, so FR-4 went first to keep every commit green.
- D-03 S-015's first run (`runs/20261026T173305Z-s015-problem-only`, failed) read the card's primary as *Save and
  continue*: the card's first render reads it until an effect pre-fills the occasion field, then *Yes, that's it*. The
  tracker kept a state's first words; it now keeps the last (the settled screen). A harness fault, not a DRIFT.
- D-04 S-015's second run (`runs/20261026T173418Z-s015-problem-only`, failed) held Oliver Grant (no occasion in the
  window: the gate's No) to the thank-you; he meets `ExitScreen` (*That's it.*, the same `.iv-done` box). The walk now
  tells the exit from the thank-you by its heading (`browser.INTERVIEW_DONE_TITLE`); the exit owes no thank-you. A
  harness fault, not a DRIFT.
- D-05 FR-5 names *the phone walk*: the harness walks the AI link at its own window and has no phone walk of the player,
  so the crop's classes are read and recorded on the AI link's walk and asserted nowhere.

## Where the spec and the code disagreed

- FR-1 *where a walk edits the context it presses Edit*: no walk ever edited the context on the card, and pressing the
  card's *Edit* and saving again would start a second CONTEXT_INTERPRET the scripted executor has no entry for. The card's
  *Edit* is read (its label held on every walk); S-005 presses the confirmed state's *Edit* (the fourth state) and holds
  the form filled, nothing saved.
- FR-2 *the pitch the walks typed*: no walk typed one on the word screen (it pressed Continue); the only pitch was the
  interviewer leg's `PUT word` after the lock (call 149). That is what was dropped. IM5 existed to hold that word
  unspoken, so with no word it is re-pinned to hold the default thank-you (v8) rather than left owed and unmeasured.
- FR-2 *re-pinned (say which)*: SC2 and IM5; each ruler's version moved by its own rule (*bumped whenever a mark reads its
  record differently*); `MARKS_VERSION` did not.
- FR-3 is not named among FR-2's re-pins but moves two journey marks' readings (report_overview, report_binding), so
  `REPORT_MARKS_VERSION` moved by the same rule.
- FR-4 *the guide marks count the four new clips*: no G-mark counts clips by number; G12 reads every present clip, so it
  read the four with no change, and the manifest-knowledge test learned them. `GUIDE_MARKS_VERSION` stays 3.
- FR-5 *the phone walk*: there is none (D-05).

## Left open

- No DRIFT written: every journey met the products as keel-web 113 / 114 say.
- The card's primary reads *Save and continue* for one render before the occasion is pre-filled (D-03): what a founder
  sees for a frame; not filed.
