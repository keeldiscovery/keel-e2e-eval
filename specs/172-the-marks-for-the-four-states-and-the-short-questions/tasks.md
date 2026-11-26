# Tasks -- spec 172

Base: `origin/master` `3d6ad49` (171 merged at `dd4f124`; spec 172 committed). Built 2026-11-26 by a builder (Claude
Opus 5.5) in the worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-172`, branch
`172-the-marks-for-the-four-states-and-the-short-questions`. Nothing paid: no model, no key, no vendor, no stack, no pip
install (the main checkout's `.venv`, symlinked, ignored), no network but `git fetch` / `git push` of this branch.
keel-web's words read from web master `edc30008` (274, 275, 276, 277 merged; read-only); keel-cloud 283 / 284 from
keel-cloud-docs master `38e8c5fa` (contract 96); keel-cloud 285's words from its spec on that master and the builder's
worktree `wt/keel-cloud-285` (`SolutionQuestions.java`, `ItemFrames.java`, read only, at `5c2435cb`).

- [ ] T0 Set up: the worktree's `.venv`, the base's `make unit` on archived siblings (the reds listed below), this file.
- [ ] T1 FR-1 the founder's beats (keel-web 275): `harness/story_screens.py` -- `LONG_BEAT_SUB`, `THINK_LINE`, `THINK_MS`
  and the 20 s / 60 s asks gone; `WAIT_MS` 8 s; the orb's `data-state` asking | hearing | waiting | thinking | paused
  (272's six read through the mapping); the state words; `beat-ask` read once (never a second); no *What I hear* and
  no founder lines (`beat-no-transcript`); the card's rows in order; a done word alone after the card ends the beat;
  *none* on the setup beat closes at once; `beat-question-fold`; every beat a long beat. The legs' checks
  (`evals/three_views.py`).
- [ ] T2 FR-2 the respondent's player (keel-web 274): `harness/interviewer_screens.py` -- the story's status line, the
  acknowledgement `ai-story-got-it` (*Got it. Thank you.*), the ask once at 8 s, every passage captioned
  (`ai-passage-caption`), the four states on the player's orb; the strangers say the story in two parts with a pause
  under 8 s and end on *that's it* (`evals/three_views_strangers.link_walk`, `harness/film_strangers.py`); the dry
  run's story closed by the done word and acknowledged (`evals/interviewer_leg.py`).
- [ ] T3 FR-3 the boxes (keel-web 276): **Finalize the problem** / **Finalize the solution** (`boxes-yes`) pressed on
  every board; a page that moved on by itself within 10 s of Keel's line is a fault (`boxes-auto-advanced`); Keel's line
  read once; the sheet's step two reads only *What do you want to change?*.
- [ ] T4 FR-4 the solution's frames (keel-cloud 283, keel-web 276): `idea-building` read as the problem's (chapters
  before | task | joy, chips *Opening*, *What it does*, *What they get*, *drawing again* rows with a `note`); a failed
  build a fault only on *no picture could be drawn*; `frames` / `chapters` in the film table; a `solves` / `better`
  chapter a DRIFT line; contract 96.
- [ ] T5 FR-5 the recap cut (keel-cloud 283 FR-8): five problem lines before the check on a solution link, eight on a
  problem link; the copilot card the same five.
- [ ] T6 FR-6 the short questions (keel-cloud 285): `harness/three_surfaces.py` and `harness/solution_surfaces.py` carry
  285's frames; a link with no film keeps the old frames by the item's `framed`; the screener at most twelve words.
- [ ] T7 FR-7 versions and record: `INTERVIEWER_MARKS_VERSION` 20; the DRIFT lines; `harness/interviewer_fake.py` serves
  the new words; `runs/DRIFT.md` force-added.
- [ ] T8 FR-8 the tests on fixtures and `make unit` after; this file's sections.
