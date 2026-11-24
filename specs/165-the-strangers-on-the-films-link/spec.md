# Spec 165 -- The strangers on the film's link: the judge's seven people answer the film project's four questions, and the founder's page read after them is that project's

Spec 163's walk tells the problem by voice on its own project and captures the film there, then runs the back-test on
a second, typed project (judgement call 1: the back-test types the context and never tells the story) and reads the
strangers' screens and the founder's page on that typed project. So the question score (§A) grades the typed path's
questions and the dashboard score (§B) a page the film never fed. The founder (2026-11-24): the judge measures *"the
quality of the questions shown to the respondent ... the film ... post that the interview, the dashboard and the
insights"* -- all of one study. This spec makes the film's project the study the people answer.

## Rules

- **FR-1 One project.** `make film-walk` (`evals/run_film.py`, `quality/film.py`): after the film is captured, the same
  project is locked (the four questions; the ready page's lock with enough credits, as `three_views.py`'s FR-1d does),
  its link is sent to the entry's seven people (the corpus's first seven of the role the PROBLEM scope sends, as
  `cycle.toml`'s `people` has it; `TYPOS=1` on the founder's words as today), and each answers **the film's link**:
  the opening, the screener, the film, *Did this happen to you?*, the experience, Frequency's five, Importance over
  the role's tasks, the whys where owed -- the walk of 161's stranger legs (`three_views_strangers.py` / 164's
  mirrors), the person's answers from the corpus mapped onto the four questions as 161 FR-6 maps them. No second,
  typed project is made.
- **FR-2 The reads on that project.** `make read-screens` reads the strangers' screens of the film's link (§A, R6) and
  the founder's page of the film's project after the seven answers (§B: the Overview's cards, the ways panel, the
  Insights tab, the brief), as 163 FR-2 says; the bundle's `walk.json` names the one project and its score files.
- **FR-3 The table.** `read-film-table`'s `score_pct` and `after_pct` columns come from that project; the record says
  *the film's project* and never mixes a typed project's scores in.
- **FR-4 Free.** `make unit`: the walk on the local stack with `FakePictures` and the fake readers sends the seven
  people on the film project's link and reads the founder's page there (the fixture answers); the refusal when the
  lock fails names the step.

## Acceptance
- One local `make film-walk ENTRIES=08-fresco DOOR=fake` on the stack (keel-cloud master with 273, keel-web master
  with 261 and 259): one project in `walk.json`, seven responses on its link with the four questions walked, the
  founder's page read after them; `make unit` green with no new red; `tasks.md` with the commits and judgement calls.
