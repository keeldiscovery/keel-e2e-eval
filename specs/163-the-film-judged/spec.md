# Spec 163 -- The film, judged: the scenario-maker as before, a film reader that grades the respondent's film on the persona, the task, the limitations, the pain, clarity, legibility and the whole; then the nine

The founder, 2026-11-24 (two messages): *"we had earlier an agent who used to create the scenario, the problem, and
another agent who will judge it. Now I would like to do the same, but the judging criteria should be based on the
quality of the animation that we create for the respondent. Does it cover all the user persona, the things they want
to do, the limitation and the pain? Is it clearly spelled out? And the end-to-end."* -- *"one more criteria ... no words
are garbled. There's a clarity on it. If there is anything written on it, it's clearly readable."* And, the same
afternoon: the film is the drawn pictures of keel-cloud 273 / keel-web 261 (*"we should only use the persons one"*), so
this judge grades that film. Built after the problem batch and the pictures are on staging; the paid run on the nine
only on the founder's word.

## Today

The quality cycle (`quality/CYCLE.md`, spec 079): `make quality-walk` back-tests each entry of `quality/cycle.toml`
on the stack (the scenario-maker: the corpus entry typed as the founder, seven simulated people), `make read-screens`
scores every respondent screen with the question-quality rubric (`quality/RUBRIC.md`, RUBRIC_VERSION 5, two readers
through the `claude` CLI, `quality/readers.toml`), `make read-table` tables it against the bar (90) and the baseline;
the gallery admits an entry on its mean (spec 127, >= 80). Nothing reads the film: the problem is told by voice since
keel-cloud 263 and the film is built from the board (268), drawn by keel-web's engine; with 273 it is the pictures.

## Rules

- **FR-1 The film rubric.** A new file `quality/FILM-RUBRIC.md` (`FILM_RUBRIC_VERSION` 1, `quality/film_rubric.py`
  pasting the part between its prompt markers into the reader's prompt, the pattern of `rubric.py`). Eight criteria,
  each 0, 1 or 2 with one sentence of why, judged from inside the entry's persona (the corpus entry's `context`,
  `roles` and `statements.problem` are the yardstick):
  - **F1 The persona.** The person shown is this person in their setting: the trade's place, their garments, the
    time of day the task happens -- as the entry's context says, and as the model's own knowledge of that trade
    would draw it (273 FR-2).
  - **F2 The task.** What they are trying to get done, at the moment it arises, is shown and said.
  - **F3 Today's way.** How they do it today is shown and said, not only named.
  - **F4 Every limitation.** Each limitation of the entry's problem statement has its own scene that shows it (the
    thing that goes wrong), none missing, none invented.
  - **F5 The pain.** The cost to them is shown as the person's reaction (slumped, late, behind), its own scene, and
    said in the founder's words.
  - **F6 Clearly spelled out.** Each line is plain to this person, in the founder's words, under 20 words, says one
    thing, and matches its picture; nothing a stranger would misread.
  - **F7 End to end.** The eight lines in order tell the whole: who, the task, today, where it falls short, the
    cost, the ask; the chapter marks in the right places; a stranger who had never heard of the problem could
    answer *Did this happen to you?* from the film alone.
  - **F8 Legible.** No word garbled anywhere: every word written on the frame (the caption, the chapter mark, the
    board's ask) is clearly readable at the size it is drawn, on the phone frame and the laptop frame; no text,
    letters, digits or logos inside any picture; no caption cut, overlapping or clipped.
  **The solution film, the other way around** (the founder, 2026-11-24: *"if it's a problem, it should test whether it
  really represents the person doing the task, having the limitations and the pain, and the solution the other way
  around"*), nine criteria on a study whose solution film is served (keel-cloud 271/273; walked once the solution batch
  is built): **S1** the same person in the same setting, the brand (its colour and mark) on the screen wherever the
  product appears; **S2** the setup shown before the task where the founder named one, and nowhere where none;
  **S3** the person doing the task with the product, step by step as the board says; **S4** each limitation of the
  problem film shown solved (a tick) or shown as not solved (a cross), none missing; **S5** what the product does
  better, said once; **S6** the joy as what the person gets back, the pain's opposite, never a feature; **S7** clearly
  spelled out (as F6); **S8** end to end in the five chapters (as F7); **S9** legible (as F8).
  **The founder's questions** (the founder, 2026-11-24: *"the quality of the questions shown to the respondent [and]
  to the founder"*): the founder-reader (the rubric's §B reader, from inside the entry's founder) scores Keel's spoken
  beat questions, asks and readbacks on the founder's walk -- the problem's seven beats and the verdict line, the
  solution's four beats, the pilot ask -- on R1 fits here, R2 plain to this founder, R3 about what they know, R5 the
  founder's words kept in the readback and on the board, the instead line as today; `founder_pct` per study.
  The film's score is `film_pct` = the mean over the eight (nine on the solution film) as a percentage of 2; a 0 anywhere flags the film; the
  weak rule as `RUBRIC.md`'s (`FILM_WEAK`). A change to a criterion bumps `FILM_RUBRIC_VERSION`; scores of two
  versions are never tabled together.
- **FR-2 The frames.** `make film-walk ENTRIES=<ids> WHY=<...>` (PAID, the founder's word): for each entry, the
  PROBLEM back-test as `quality-walk` runs it (the scenario-maker unchanged: the entry typed as the founder, its
  story told on the seven beats, the board's yes, the build with the real pictures on keel-cloud's `openai`
  pictures port), then the film captured: the founder's player opened at `define/story` on the stack, each scene's
  frame photographed on a phone (390 x 844) and a laptop (1280 x 800) as the scene is held (the fake clock pauses
  the player at each scene; the caption settled), plus the served story JSON (`roomId`, scenes with `pictureAssetId`,
  `chapter`, lines, `clipIds`), the pictures themselves (`GET /v2/assets/{id}`), the build's `pictures.setting` and
  `pictures.prompts`; all in the bundle under `film/<entry>/` (`frames/scene-<n>-phone.png`, `-laptop.png`,
  `story.json`, `pictures/`, `prompts.json`). The film is captured before any stranger sees it; then the walk goes
  on as `quality-walk` does -- the seven simulated people answer on the person's own link (`cycle.toml`'s `people`),
  the founder's page is read after the answers -- so one bundle carries the three things the founder named
  (2026-11-24: *"that agent also should evaluate the dashboard finally created post the interview, which we used to
  do earlier"*): the film (FR-3), every respondent screen (`make read-screens`, the question-quality rubric's §A and
  R6), and the founder's page after the answers (the rubric's §B, spec 109: the Overview's cards, the Insights tab,
  the brief, read by the founder-reader as the earlier cycles read them; `report_marks` on the dimension cards). The ledger is read: one `STORY_PICTURES` row at 0 credits with its cost, one `PICTURE_REVIEW` row
  per picture; the bundle records the dollars.
- **FR-3 The film reader.** `make read-films RUN=<bundle>` (PAID): one call per entry through the **Anthropic API
  with vision** (`KEEL_ANTHROPIC_API_KEY` in the shell, as the walks' door `keel`; the `claude` CLI door cannot carry
  the frames and is refused for this reader), model and effort pinned in `quality/readers.toml` `[film_reader]`
  (`claude-opus-5-5`, medium): the prompt is `quality/readers/film-reader.md` -- the persona card (the entry's
  context, the problem statement with its limitations and cost), then the eight lines with their chapter marks, the
  setting and the prompts, then the fourteen frames (seven scenes, two viewports) and the seven pictures as images,
  then the rubric; the answer the eight scores with their whys, `film_pct`, a `missing[]` list (limitations or boxes
  not shown) and an `instead` line per criterion under 2. Written as `quality/scores/<bundle>-film-<entry>.json`
  with the reader block and `FILM_RUBRIC_VERSION`.
- **FR-4 The table and the gate.** `make read-film-table RUN=<bundle>` (free): one row per entry (F1..F8, `film_pct`,
  flagged, the dollars) **beside the same entry's question score (`score_pct`, §A) and its founder's-page score (§B)
  from `read-screens` on the same bundle** plus `founder_pct` (the founder's beats) and, once the solution batch is built, the solution film's
  `film_pct` (four or five columns a study, one record; the Insights tab's cards and quotes and the brief are inside
  §B's reads, named in the record), the mean over the entries, the bar `film_bar_pct` (`quality/cycle.toml` `[film]`, 80 as the
  gallery's gate, the founder's to move), the weak rows; `quality/FILM-TABLE.md` rewritten; `quality/cycles/<record>-
  film.md` the record. An entry passes at `film_pct` >= the bar with no 0; a round passes when every entry does.
- **FR-5 The nine.** `quality/cycle.toml` gains `[film] holdout = [...]`: the nine entries the founder named as the
  holdout (2026-11-04, *rules not cases*), written by the integrator from the founder's list before the run; `make
  film-walk ENTRIES=holdout` walks them. The five of `entries` are not the gate: if the five pass and the nine fall
  short, the round fails (`quality/decisions.toml`'s rule, unchanged).
- **FR-6 The adviser.** `make film-advise RUN=<bundle>` (PAID, the claude CLI as `quality-advise`): one bounded call
  per weak criterion over the nine, proposing a change to keel-cloud's `picture-setting.md`, `PicturePrompts`'
  rules or `story-draft.md` -- a rule, never a case (no entry named in a proposal; the persona-aware rule); it
  proposes, it never applies.
- **FR-7 What is free.** `make unit` covers the rubric paste, the score file's shape, the table on fixture scores
  (three fixture entries: one passing, one with a 0 on F4, one weak on F8), the frames' capture on the local stack
  with `FakePictures` (`PROFILE=eval`: the frames show the fake PNGs; the reader is not called), and the refusal of
  the CLI door for the film reader. Nothing paid runs from `make unit`, `make eval`, the matrix or a schedule.
- **FR-8 Report and DRIFT.** The run's report gains *The film, judged*: the table, each entry's eight whys in one
  line each, the frames linked; a cloud or web finding (a picture with text, a caption clipped, a limitation with no
  scene, a setting that names a company) goes to `runs/DRIFT.md` in the usual shape with the frame's path.

## Acceptance

- `make unit` green with the new mirrors (`tests/test_the_film_judged_163.py`); one local `film-walk` on the stack
  (keel-cloud with 273, keel-web with 261, `FakePictures`) on 08-fresco producing the bundle's `film/` folder with
  fourteen frames, the story JSON, seven pictures and the prompts; `read-film-table` on the three fixture scores.
- The paid run of record on the nine (`make film-walk ENTRIES=holdout`, then `read-films` and `read-screens`, then `read-film-table`)
  runs only on the founder's word and is recorded in `quality/cycles/` with its dollars.
