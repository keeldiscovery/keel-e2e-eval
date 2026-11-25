# Tasks -- spec 170

Base: `origin/master` `59a5352` (169 merged at `eac199d`; specs 170 and 171 committed). Built 2026-11-25 by a builder
(Claude Opus 5.5) in the worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-170`, branch
`170-the-entry-screen-and-the-films-question`. Nothing paid: no model, no key, no vendor, no stack, no pip install (the
main checkout's `.venv`, symlinked, ignored), no network but `git fetch` / `git push` of this branch. keel-web's words
read from web master `04773133` (specs 266, 268, 269, 270, 271 merged; their specs and `git show master:<path>`,
read-only); keel-cloud 277's `dimension-cards.md` from keel-cloud-docs master `61ba9069` (read-only).

- [ ] T0 Set up: the worktree's `.venv`, the base's `make unit` (the reds listed below), this file.
- [ ] T1 FR-1 the entry screen (keel-web 266): `harness/interviewer_screens.py` -- *Test your mic* (`ai-mic-test`) ->
  *Say anything.* (`ai-mic-say`, the wave) -> *Your mic works.* (`ai-mic-heard`) -> **Begin** (`ai-start`); the intro's
  one line (`ai-intro-line`, `aiIntroLine`); the block's two lines; `SAY_HELLO`, `MIC_LABEL`, `MIC_BLOCK_HOW`,
  `START_THE_INTERVIEW` and the *Heard:* reader (`mic_heard`) gone; the old words found on a screen a DRIFT capture
  note (`entry_drift`), never a fault of the walk; the readers (`evals/three_views_strangers.py` intro / blocked checks,
  `evals/interviewer_leg.py`, IM17 in `evals/interviewer_marks.py`, v18 -> v19), the strangers' bundle
  (`harness/film_strangers.walk_summary`'s `entry`, `entry_faults` into the film's capture faults).
- [ ] T2 FR-2 / FR-3 the verdict gone and the film's question (keel-web 268, 269): `harness/story_screens.py`
  `VERDICT_CARD` / `VERDICT_ASK` / `VERDICT_LATER` / `hear_verdict` / `film_yes_verdict_pilot` gone; `STORY_ASK` the
  new words, `film_ask_idea(name)`; `film_question` waits for Yes (`film-yes`) / No (`film-no`), reads the line and
  says *yes* aloud; `film-fix` never opened; the problem's yes lands on the window page, the solution's on the pilot
  ask; a retired verdict card met on the way is passed by the quiet and recorded (DRIFT capture). `evals/three_views.py`
  checks, `evals/three_views_report.py`, `quality/film_reader.founder_lines` (the film's question beat).
- [ ] T3 FR-2b the vendored Prevalence card: `quality/readers/dimensions.md`'s Prevalence gate sentence re-cut to
  keel-cloud 277's `dimension-cards.md`; `CARDS_SHA256` (and the pin chain's `CARDS_SHA256_141`) re-pinned;
  `CARDS_MOVED_162` checked.
- [ ] T4 FR-2c the building screen (keel-web 270): `PLAN_JS`, `read_plan`, the rows' looks and chip words, the bar's
  legend (`plan_legend`, `legend_holds`), `.story-build-steps` gone, *Drawing your story.* and no `story-q` while it
  builds; `harness/film_frames.watch_building` / `building_faults`, `evals/run_film.building_read`.
- [ ] T5 FR-4 / FR-5 the tests and `make unit` after; nothing here writes respondent words; this file's sections.
