# Spec 166 -- The solution film walked and judged, the table ranked and compared

The founder, 2026-11-24: *"the solution the other way around"* -- the judge grades the solution film too: the person
doing the task with the product, the limitations solved, the joy. And 2026-11-25, going to sleep: *"run the judgment
run with, say, now 5 use cases and rank them and compare with the previous run and see how it goes."* Built on
keel-e2e-eval master with 162 (the solution walked), 163 (the film judged), 164 and 165 (the strangers on the film's
link) merged; keel-cloud 271/272/273/275 (contract 91, the pictures portrait 1024 x 1536 from 275, the solution project
reusing the problem film's character sheet) and keel-web 259/260/261/263.

## Today
`make film-walk` (163, 165) tells the problem's seven beats in the entry's words on one project, captures the problem
film, locks it, sends its link to the people and reads §A/§B; `make read-films` reads F1-F8 (`--kind problem`, the
default) and the founder's beats; `make read-film-table` tables one film a row. `quality/FILM-RUBRIC.md` carries S1-S9
and `film_rubric.prompt_solution()` the reader's part for it; `film_table` knows the S columns; `quality/cycle.toml`
`[film] scopes = ["PROBLEM"]` says the solution film *is read once the solution batch is walked*. Spec 162's `IdeaWalk`
and `three_views.idea_leg` walk the founder's solution on a SOLUTION project created on the problem (the create
request's `parentProjectId`, the product's *A new solution*): the problem's film then the opening, the brand page, the
four long beats, the board, the build, the plate and the film, the verdict, the pilot ask, the ready page -- with a
scripted idea (`IDEA_TELLINGS`, `IDEA_NAME`), not the entry's words. Nothing walks the solution film for the judge.

## Rules
- **FR-1 The solution leg, on a project made from the problem's.** After an entry's problem leg has its strangers'
  record (165), the walk's second half: a SOLUTION project created on that problem project (`parentProjectId`, the
  pick the product offers, by the same founder), then `IdeaWalk` as 162 drives it -- the problem's film then the
  opening, the brand page, the four beats, the board's six rows, the build, the plate and the film in chapters, the
  verdict line, the pilot ask answered yes, the ready page -- **in the entry's words**: `film_frames.entry_idea_beats
  (entry_yaml, problem_story)` composes the brand (`idea_name`; a tagline from `interpretations.offer_name` else
  `solution_mechanism.short_name`, under eight words; a swatch by the entry's number), beat 1 the product in one
  breath (`statements.solution`'s first sentence, else `solution_mechanism`'s actor + mechanism + output), beat 2 the
  setup (what `solution_mechanism` needs in place, else the setup-none words), beat 3 the steps (`trigger` -> `mechanism`
  -> `output`), beat 4 the limitations solved (one clause per limitation of the inherited problem story, answered from
  the mechanism; `not_assumed` left out) and the joy (the opposite of the problem story's cost, in the entry's words).
  Typed with a person's typos on Keel's door as the problem beats are (TYPOS); the fake door tells the fakes' script.
  The build runs with the real pictures (`KEEL_PICTURES=openai`): keel-cloud reuses the problem film's character sheet
  (the same person, S1). The leg records the project (`solution_project_id`), the create request, the beats as told and
  read back, the board, the idea (`idea/spoken`: the product, the setup, the steps, the marks, the advantage, the joy,
  the verdict line, the pilot), the ledger's rows (IDEA_TURN, STORY_PICTURES, PICTURE_REVIEW, the clips) and the time
  to the film.
- **FR-2 The solution film captured before any stranger sees it.** `FilmCamera` generalised to the idea film: the
  founder's player on the solution project (`define/idea/...`'s film screen, or the founder's film page keel-web 259
  serves), every scene held on the phone and the laptop (as the problem film: 263's portrait stage on a phone, the
  column on a laptop), the chapter keys of keel-cloud 273 FR-6 for the idea film (*Before / The task / What it solves /
  Better / What they get*), up to eleven scenes, the plate frame (the brand's mark and the stranger's line, ~3 s) as its
  own frame, a scene with `pictureMissing` recorded as missing (275), the pictures fetched (the sheet's id the
  problem's), the build's `pictures.plan` / `reviews` / `kept` and `failedReason` kept with the prompts, into
  `film/<entry>/solution/` (frames, pictures, `story.json` = the idea story, `idea.json`, `prompts.json`, `film.json`
  with `kind: "solution"`). The problem film's folder is unchanged (`film/<entry>/`).
- **FR-3 The strangers on the solution link.** Then on the same solution project: the lock (the ready page's lock as
  165; the stand-in top-up as 165), its link sent to the entry's people of the role the SOLUTION scope sends (cycle.toml's
  `people`; PEOPLE= overrides), each answering the solution link as 162 FR-5/FR-7 walk it (the opening, the plate, the
  problem film, the solution film, the three yes-or-no questions, the whys where owed, by `solution_surfaces.answers_for`
  from the entry's recorded answers), the founder's page read after them (§B), `backtest.json` (`kind: "film-solution"`)
  written beside the problem's; `make read-screens` on it on Keel's door (paid). `walk.json` names, per entry, both
  projects, both screens bundles and both score files; it is rewritten after every step.
- **FR-4 The reader on both films.** `make read-films RUN=<walk>` reads every film folder it finds: the problem's with
  `kind: problem`, the solution's with `kind: solution` (KIND= still forces one). The solution request carries the
  persona card, **the problem's limitations and cost** (from the problem film's `story.json`), **the founder's idea
  board** (`idea.json`: the product, the setup, the steps, the marks, the advantage, the joy), the lines with their
  chapter marks, the plate frame, every frame on both viewports, the pictures and the sheet, the prompts' setting and
  the plan -- then `prompt_solution()`'s S1-S9. Score file `quality/scores/<bundle>-film-<entry>-solution.json`
  (`kind: "solution"`, `film_pct` over the nine, flagged on a 0). The founder's beats on the solution (163 FR-1's R1,
  R2, R3, R5 on the four beats and the pilot ask) read as the problem's are, into the same score file. The reader's
  `[reader]` model and effort unchanged (claude-opus-5-5, medium); `MAX_REQUEST_BYTES` holds -- a solution film of
  eleven scenes on two viewports plus pictures must fit, else the laptop frames are dropped first and the file says so.
- **FR-5 The table: both films a row, ranked.** `make read-film-table RUN=<walk>` tables per entry: the problem film's
  `film_pct` and its F criteria, the solution film's `film_pct` and its S criteria, `founder_pct` (both studies'
  beats), §A and §B of each study, the cost of each leg; an entry passes at the bar on **each** film with no 0. A
  **rank** column: the entries sorted by the mean of the two films' `film_pct` (an entry whose solution leg failed or
  was not walked ranks on its problem film alone, marked), ties by the problem film. The verdict names the entries
  under the bar on either film. `findings` and the DRIFT text name the weak criteria of both kinds (the `s*` map).
- **FR-6 Compared with the previous run.** `make read-film-table RUN=<walk> BASELINE=<earlier walk or bundle>` adds
  *Compared with <baseline's record name>*: per entry present in both, each criterion's move (F1-F8, S1-S9, founder,
  §A, §B, the cost) as `before -> after (+/-)`, the entries added or missing, and the round's means before and after;
  the baseline's score files read from `quality/scores/` by its bundle name (the trial on two:
  `runs/20261125T010642Z-film-walk`, its table committed at `quality/cycles/20261125-b48e1f4-film.md`). The record
  `quality/cycles/<yyyymmdd>-<cloud7>-film.md` keeps the comparison. `FILM-TABLE.md` the same.
- **FR-7 The walk's switches.** `quality/cycle.toml` `[film] scopes = ["PROBLEM", "SOLUTION"]`; `SCOPES=PROBLEM` on
  `make film-walk` walks the problem alone (today's walk); `ONLY=solution ENTRIES=<id> RUN=<walk>` walks the solution
  half again on an entry whose problem leg is recorded in that walk (its `project_id` reused), the problem's record
  kept. `DRY=1` prints both halves. `DOOR=fake` walks both halves free (the fakes answering the idea turns -- DRIFT
  #120's fake draft is what it is -- and `FakePictures`); the reads are paid and not run. The preflight refuses an
  entry whose yaml has no `statements.solution` or `solution_mechanism`.
- **FR-8 Tests.** Unit (no stack, nothing paid): `entry_idea_beats` on the payroll and Lullaby fixtures (the four
  beats, the brand, the joy, the setup-none case, every beat under the spoken-form caps keel-cloud 271 holds the
  founder to -- no number a founder would not say, no placeholder); the camera's idea-film chapter keys and the plate
  frame on a fixture page; the solution request's parts named in order and the size rule; the score file's shape for
  `kind: solution`; the table's rank (both films, one film, a failed leg), the verdict on either film, the comparison's
  moves and its missing/added entries; the walk's plan with both halves, SCOPES, ONLY and the preflight's refusals.
  `make unit`: no new red against the base (the base's reds listed in tasks.md).
- **FR-9 Nothing paid in the build; the fake walk once.** The builder runs `make film-walk ENTRIES=08-fresco DOOR=fake
  WHY="166's local walk"` on the local stack (keel-cloud-docs main checkout on master, keel-web master; `KEEL_PICTURES`
  unset) and records both halves' outcome in tasks.md; no key, no read. The paid run on five is the integrator's, on the
  founder's word.
- **FR-10 Respondent-question rule.** No instruction that generates respondent-facing questions is read or changed by
  this spec; the AI-avatar spoken-form guidelines are untouched. The founder's beats composed from an entry are the
  founder's words to Keel, never a respondent's question.

## Acceptance
`make film-walk ENTRIES=09-karsa,12-transload,11-issen,14-code-four,15-voltair DOOR=keel WHY="..."` leaves, per
entry, a problem film and a solution film captured before any stranger saw them, both links answered by the entry's
people and both founder's pages read; `make read-films` scores F1-F8 and S1-S9 with their whys; `make read-film-table
BASELINE=runs/20261125T010642Z-film-walk` ranks the five on both films and shows each criterion's move against the
trial on two. A stranger's solution link shows the same person the problem film showed, now using the product.
