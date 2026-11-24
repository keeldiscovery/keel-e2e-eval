# Spec 162 -- The solution, walked: the film opening it, the brand typed, four beats, the board, the film in five chapters, the verdict and the pilot ask; the screener first, two films and the plate, three yes-or-no questions, every why; the orb, the face and the Copilot card compared

The founder, 2026-11-24 (`keel-cloud-docs/canon/designs/solution-study-design-2026-11-24.md`, the design of record;
§5 D9: *"ensure that this works perfectly fine in the AI interviewer, the Keel audio and the Copilot"*). keel-cloud
271 (the founder's solution, contract 88), 272 (the three questions, contract 89), keel-web 259 (the founder) and 260
(the stranger, the founder's page, the Copilot card). Spec 161's walks read the problem study; this spec moves every
solution mirror and extends the three-surfaces check to the solution study. Nothing paid (FakeSpeech, the fake
avatar, the fake transcriber, the fake readers).

## Rules

- **FR-1 The founder's solution.** `harness/story_screens.py`: `IdeaWalk` learns the new walk -- `replay` becomes
  `film_then_opening` (the problem film played through the one player, the opening line heard, `story/confirm`
  stamped with no words, no board, no *still the problem*); a new `brand_page` (the name typed, a colour picked, a
  tagline typed, the logo line read word for word, a non-square PNG refused on the spot with that line, *Continue*);
  `said_idea` reads four beats (1 the workflow with who does each step; 2 the setup, or none; 3 the limitations in
  one breath; 4 the joy) and refuses any other order; `idea_reading_of` and `fake_readings`' idea scripts carry the
  four beats with `workflow`, `setup`, `setupNone`, `statement`, `limitAnswers`, `advantage`, `joy` -- one script
  answering beat 1 with advantages alone (the one ask *Start from the first thing they do. What happens first?*
  walked), one answering beat 3 with one limitation unmatched (the ask naming it, a correction, and a cross), one
  answering beat 4 with a feature (the ask *That is what it does. What do they get back because of it?*). Every beat
  is a long beat (161 FR-1's rule: closed by a done word, never on quiet; one two-part beat 3 across 7 s of quiet
  asserting *Take your time.* and the beat still open). `boxes` reads the six rows (the product with the tagline,
  with it, before that, what it does, in the way with the marks, what they get) by `data-box`, each lit as named.
- **FR-2 The verdict, the pilot and the corridor.** After the film's yes the walk hears the verdict line (the served
  `verdictLine` word for word) and goes on by silence; then the pilot state: the pilot ask heard word for word, a
  yes said, `PUT idea/pilot {offer: true}` on the wire, the Before screen's pilot question absent (`pilot-first-step`
  not drawn, the counter *1 of 1*); then the ready page: no belief page on a spoken SOLUTION project
  (`vectors_screens.calibrates(spoken)` extended to SOLUTION; the review table's three rows read as written, *6 or
  7 in 10* each). On a SOLUTION_COMMERCIAL project the money pages follow as today. The typed path still walks the
  three pages (`LIST_CONTROLS` and `PICKED` in `vectors_script.py` keep them for the typed corpus; a spoken project
  reads `single_choice` bins).
- **FR-3 The film in five chapters.** `story_screens` reads the idea's build: up to eleven scenes from
  `idea`'s build and the link's `ideaStory`; the chapters in order (the opening line exactly *This time, {name} is on
  the screen.*; the setup scene present if and only if the setup is non-empty; one scene per workflow step; the
  limitations scene with every mark equal to the board's; the advantage scene if and only if one was read; the joy
  scene last, `joy: true`, its line the board's joy, the person upright); the chapter words on the band (*Before*,
  *The task*, *What it solves*, *Better*, *What they get*); the plate (`build.story.plate` with the tagline) drawn
  for about three seconds before the film (the fake clock); the brand on every screen scene; `clipIds` one per line.
  A failed build (`build.state` failed, `failedChapter`) is walked once on a scripted second review no: the line
  *Keel could not draw {chapter}. Say that part again?* read and the beat reopened.
- **FR-4 The money replay.** `MoneyReplay` reads the workflow, the setup, the statement and the joy in place of the
  product sentence and the SO line; the money questions unchanged.
- **FR-5 The link's order.** `interviewer_screens` / `interviewer_leg` on a solution link: the state sequence is
  opening (272's words with the founder's first name), screener, the bridge *Let us see it.*, the problem film ending
  on the pain scene, *Begin*, the problem check *Did this happen to you?* (a No leaves with the thanks before the
  plate: one stranger per study), the plate (`plate.before` heard, the plate on screen, `plate.after` heard over the
  fade), the solution film ending on the joy, the three questions, the whys, the pilot ask where offered, the
  thanks. The idea card's three lines are nowhere on a link with the film. Both films at full length (the walk
  measures the time to the first question and records it in the report: no assertion, D6).
- **FR-6 Three yes-or-no questions.** `classifier_guard`: `_SINGLE` gains `yes_no`; `SOLUTION_CONTROLS =
  ("yes_no",)` replaces the `fixed_four` / `scale_four` reads on the three; the corpus's three solution dimensions on
  each entry become a founder bin (`p_0_20` .. `p_80_100`) and each person's pick `yes` or `no` (corpus revision
  bumped; the shape tests follow); the stranger answers by *yes*, *no*, *A*, *B* and by the option's words on the
  orb; *si* on the two-row item is unclear, never C. The questions read on the wire: Compatibility carries the
  brand's name and the job in -ing form, Relative advantage the base job, Adoption friction its setup form on a
  fixture with a setup and its no-setup form on one with none; each sentence at most 20 words. `working_rung.py`:
  yes supports, no against.
- **FR-7 Every why.** Each study's strangers include: one yes on all three (asked nothing), one no on Compatibility
  alone (*What would get in the way?*), one no on Relative advantage alone (*What would it have to do better?*), one
  no on Adoption friction alone (*What makes it a trouble?*), one with three nos (two whys, the third capped,
  `capped` on Insights). The Insights tab's cards read as spec 119's: one card per line with words, the headings of
  the three blocks, the quotes with the option *No*, `tookBy` nowhere.
- **FR-8 The founder's page.** `report` reads: the three Overview cards as share bars (the yes of n, the founder's
  band shaded, the status word), the So lines evidence only (no recommendation words: *should*, *next*, *try*
  refused as DRIFT), no benefit scale anywhere, the brief's solution rows on `{yes, n, share, founderBand}`.
- **FR-9 Three surfaces, one script.** 161 FR-9's record and check extended to the solution study: the orb link, the
  face link and the Copilot card (`calls_leg.py`, the `plate` passage: the plate's words and the solution film's
  lines as text) walked through the same study; the record per step: the opening, the screener, the problem film's
  lines, the check, the plate's two lines, the solution film's lines, the three questions with their options, the
  three whys and their headings, the pilot ask; the three records equal step for step but for the face's own clip
  routes and the card's digits; the leg fails by name and says which step and which surface differ.
- **FR-10 Untouched.** The ledger and charge checks (nothing bought; `IDEA_TURN` priced 0, the review one small
  call per build read on the ledger as `STORY_CHECK` is); the problem journey (161) unchanged; `PROFILE=remote`
  untouched.
- **FR-11 Report and DRIFT.** The report's *The three surfaces* section gains the solution study's rows; a *The
  founder's solution* section with the board's six rows, the film's chapters, the verdict and the pilot answer heard;
  the time to the first question on the solution link; every cloud or web finding to `runs/DRIFT.md` in the usual
  shape. Contract read: 89. The run of record (`make e2e-157 PROFILE=eval`) on merged masters once keel-web 260 is
  merged; until then the web-side reds are recorded as *pending keel-web 259/260*, not DRIFT.

## Acceptance

- `make unit` green with the new mirrors (`tests/test_the_solution_walked_162.py`); one local run of the three
  views on the stack (keel-cloud-docs with 272, keel-web with 260) with every solution leg green or recorded as
  pending by name; the founder's solution walked by voice end to end with no typed page but the brand's; the three
  surfaces equal on the solution study; the report sections present.
