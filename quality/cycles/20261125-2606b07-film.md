# The film, judged

Bundle `20261125T225938Z-film-walk` · FILM_RUBRIC_VERSION 1 · the film reader claude-opus-5-5 medium (anthropic api) · the founder-reader claude-opus-5-5 medium (claude CLI) · the bar 80% (`quality/cycle.toml` [film] film_bar_pct) · specs 163, 166.

**This round**: 1 entry; mean film_pct 75.0 on the problem films, 0.0 on the solution films, 37.5 on the mean of the two; 0 pass on each film, 1 fall short (12-transload (the problem film and the solution film)); the round **fails**. Holdout tabled: 12-transload; holdout short: 12-transload.
**Dollars**: the reading $1.94, the walk $1.00.

## The table

Ranked by the mean of the two films' film_pct (ties by the problem film); an entry with one film ranks on it alone, marked. An entry passes at the bar on each of its films with no 0.

| rank | entry | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | problem film_pct | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | solution film_pct | mean | flagged | founder_pct | told | §A problem | §B problem | §A solution | §B solution | $ problem | $ solution | passes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 12-transload (holdout) | 2 | 1 | 2 | 1 | 2 | 1 | 1 | 2 | 75.0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 37.5 | solution | 81.7 | 87.5 | 65.7 | 70.0 | -- | -- | 2.51 | 1.38 | no |

§A and §B are `make read-screens` on **the film's project** (spec 165: the one project an entry -- the film told, locked, its link answered by the entry's people, its page read after them) -- and for the solution, on the solution's own project made from the problem's (spec 166): §A the strangers' screens of each film's link (RUBRIC.md R1-R6, and §G), §B the founder's page after the answers (the Overview's cards, the Insights tab, the brief); `--` where it has not been read. No typed project's score is tabled here. founder_pct is over both studies' beats. `told` is the problem study's told card (spec 171: the Insights tab's *On your problem* view against what the strangers told, T1-T4), never in film_pct; *absent* where the card was not there. The dollars of a leg are its film's reading, its walk and its screens' reading, where known.

The film's project: 12-transload `4de04871-f4f3-4397-9b8f-a0280bce5e9a`.

## Weak criteria

- **F2** (problem): mean 1.00, a 0 in 0 entries -- `make film-advise` proposes a rule for it.
- **F4** (problem): mean 1.00, a 0 in 0 entries -- `make film-advise` proposes a rule for it.
- **F6** (problem): mean 1.00, a 0 in 0 entries -- `make film-advise` proposes a rule for it.
- **F7** (problem): mean 1.00, a 0 in 0 entries -- `make film-advise` proposes a rule for it.
- **S1** (solution): mean 0.00, a 0 in 1 entry (12-transload) -- `make film-advise` proposes a rule for it.
- **S2** (solution): mean 0.00, a 0 in 1 entry (12-transload) -- `make film-advise` proposes a rule for it.
- **S3** (solution): mean 0.00, a 0 in 1 entry (12-transload) -- `make film-advise` proposes a rule for it.
- **S4** (solution): mean 0.00, a 0 in 1 entry (12-transload) -- `make film-advise` proposes a rule for it.
- **S5** (solution): mean 0.00, a 0 in 1 entry (12-transload) -- `make film-advise` proposes a rule for it.
- **S6** (solution): mean 0.00, a 0 in 1 entry (12-transload) -- `make film-advise` proposes a rule for it.
- **S7** (solution): mean 0.00, a 0 in 1 entry (12-transload) -- `make film-advise` proposes a rule for it.
- **S8** (solution): mean 0.00, a 0 in 1 entry (12-transload) -- `make film-advise` proposes a rule for it.
- **S9** (solution): mean 0.00, a 0 in 1 entry (12-transload) -- `make film-advise` proposes a rule for it.
- **T4** (told): mean 1.00, a 0 in 0 entries -- `make film-advise` proposes a rule for it.
- **R2** (founder): mean 1.46, a 0 in 0 entries -- `make film-advise` proposes a rule for it.
- **R5** (founder): mean 1.46, a 0 in 0 entries -- `make film-advise` proposes a rule for it.

## Each entry's whys

### 12-transload -- the problem film, film_pct 75.0

- F1 2: A supervisor in hard hat and hi-vis on the dock floor, among open trailer doors, staged shrink-wrapped pallets and a moving forklift, under a low late-afternoon sun, is recognisably this person in this place.
- F2 1: The task line is said, but the picture shows only a stack of papers landing on a desk; nothing shows freight needing to be billed at its true size while the dock keeps moving. -- *instead*: Scene 2: show a line of freight arriving at the dock with its paperwork, a trailer waiting at the door, and the supervisor deciding which pallets go to measuring. Line: 'You must get every shipment billed at its true size, without slowing the dock.'
- F3 2: One pallet is pointed into the dimensioning gantry while the other pallets sit in their lanes, and the line says the same.
- F4 1: Paperwork billing and the oversized freight are shown, but the forklift travel and congestion line sits over a supervisor idly seated with hands folded and no jam of forklifts, and the lost trailer space the founder names has no scene. -- *instead*: Scene 6: show forklifts queued and backed up at the dimensioning station while trailers wait at their doors, over 'Measuring every shipment adds forklift travel and dock congestion.' Add a scene of an oversized pallet filling more of the trailer than was paid for, over 'And it still takes up the trailer space.'
- F5 2: Scene 7 has its own picture of the supervisor slumped, chin on hand, beside a coin crossed out in orange, said as 'Oversized shipments are billed short.'
- F6 1: The lines are plain and short, but line 6 (forklift travel and dock congestion) is off its picture, which shows a calm, idle supervisor. -- *instead*: Draw scene 6 as the jam the line names, forklifts crossing back and forth and stuck in a queue at the station, not a seated, idle supervisor.
- F7 1: The whole story is there with chapters in place, but the reason for sampling (measuring everything clogs the dock) comes after the 10% finding instead of with today's way, so that beat reads out of order. -- *instead*: Put 'Measuring every shipment adds forklift travel and dock congestion' in the Today chapter, right before 'So you send only a sample…', then follow with the paperwork billing and the 10% oversized finding.
- F8 2: The captions and chapter marks read clearly on both phone and laptop, and the pictures carry no letters, digits or logos; tape ticks, blank clipboards and the clock face hold no text.
- missing: the carrier still gives up the trailer space the oversized freight takes (named in the problem statement, shown nowhere); forklift travel and dock congestion from measuring are said but not shown
- the told card, told_pct 87.5:
  - T1 2: All 3 sampled people's ticks match what their stories describe.
  - T2 2: Every one of the founder's 5 rows matches the truth's count within one of 5.
  - T3 2: All 1 amber rows are said by two or more stories and none is the founder's.
  - T4 1: The card reads in my order (way, limitations, pain) and in my words, and the bands mostly fit; the headings are drawn, uppercased, despite code's flag. One slip: the header '7 said yes · 5 told a time · 1 read as a guess and are set aside' is garbled grammar and doesn't square with the six people I heard from. -- *instead*: 6 answered · 5 told a real shift · 1 (Hamid) only guessed, so his answer is set aside
- frames: [scene-1-phone.png](../runs/20261125T225938Z-film-walk/film/12-transload/frames/scene-1-phone.png), [scene-1-laptop.png](../runs/20261125T225938Z-film-walk/film/12-transload/frames/scene-1-laptop.png), [scene-2-phone.png](../runs/20261125T225938Z-film-walk/film/12-transload/frames/scene-2-phone.png), [scene-2-laptop.png](../runs/20261125T225938Z-film-walk/film/12-transload/frames/scene-2-laptop.png), [scene-3-phone.png](../runs/20261125T225938Z-film-walk/film/12-transload/frames/scene-3-phone.png), [scene-3-laptop.png](../runs/20261125T225938Z-film-walk/film/12-transload/frames/scene-3-laptop.png), [scene-4-phone.png](../runs/20261125T225938Z-film-walk/film/12-transload/frames/scene-4-phone.png), [scene-4-laptop.png](../runs/20261125T225938Z-film-walk/film/12-transload/frames/scene-4-laptop.png), [scene-5-phone.png](../runs/20261125T225938Z-film-walk/film/12-transload/frames/scene-5-phone.png), [scene-5-laptop.png](../runs/20261125T225938Z-film-walk/film/12-transload/frames/scene-5-laptop.png), [scene-6-phone.png](../runs/20261125T225938Z-film-walk/film/12-transload/frames/scene-6-phone.png), [scene-6-laptop.png](../runs/20261125T225938Z-film-walk/film/12-transload/frames/scene-6-laptop.png), [scene-7-phone.png](../runs/20261125T225938Z-film-walk/film/12-transload/frames/scene-7-phone.png), [scene-7-laptop.png](../runs/20261125T225938Z-film-walk/film/12-transload/frames/scene-7-laptop.png)

### 12-transload -- the solution film, film_pct 0.0, flagged

- S1 0: The build served no scene and no brand plate, so no dock supervisor, no cross-dock, and no Transload colour #b8432f or mark appears anywhere. -- *instead*: Show the same dock supervisor on the same LTL cross-dock as the problem film, with Transload's #b8432f mark on every screen where the product appears.
- S2 0: The founder named a setup (reviewing each flagged shipment, keeping freight from blocking the door cameras), but the film shows none of it. -- *instead*: Before the task, show the supervisor reviewing a flagged shipment and keeping freight clear of the door cameras.
- S3 0: No frame shows the supervisor's crew scanning a shipment or Transload linking the scan, fitting a 3D box, and flagging oversize freight, so the task is never done with the product. -- *instead*: Show a worker scanning a pallet as it crosses the dock, then Transload linking the scan to the camera video, fitting a 3D box, and flagging the oversize shipment with the clip.
- S4 0: None of the three limitations (the rest billed by paperwork size, the roughly 10% bigger than declared, the forklift travel and congestion) gets a tick or a cross. -- *instead*: Mark all three limitations with a tick, each with the founder's reason: every shipment measured by existing cameras, oversize flagged with video evidence, no forklift travel or congestion.
- S5 0: The advantage, no change to the dock workflow, is never said. -- *instead*: Say once, plainly: no change to the dock workflow.
- S6 0: The film never shows the person getting back every undercharged shipment caught rather than just a sample. -- *instead*: End on the supervisor upright as every undercharged shipment is caught and billed at its true size, not just a sample.
- S7 0: There are no lines at all, so a stranger reads nothing and cannot learn what Transload does. -- *instead*: Write one short, plain caption per scene, spoken and shown on its picture.
- S8 0: None of the five chapters exists, so a stranger could not tell what the product does for a dock supervisor. -- *instead*: Build the film in five chapters in order: Before, The task, What it solves, Better, What they get, with the ticks in What it solves.
- S9 0: There is no frame or caption to read on either the phone or the laptop. -- *instead*: Render frames whose captions sit clear and uncut on both phone and laptop, with no lettering inside the pictures.
- missing: limitation 1: The rest are billed by the size (tick: existing security cameras link the scan to the freight); limitation 2: Roughly 10% of checked shipments are bigger than declared (tick: flagged with video evidence); limitation 3: Measuring every shipment adds forklift travel and dock congestion (tick: existing cameras measure, no forklift travel); the product: Transload, with its colour #b8432f and mark; the setup: review each shipment the system flags; keep freight from blocking the door cameras; step 1: scan a shipment as it crosses the dock; step 2: links the scan to the freight in the video; step 3: fits a 3D box around the freight; step 4: flags shipments bigger than their paperwork with video evidence; better: No change to the dock workflow; what they get: Every undercharged shipment caught, not just a sample

## Findings for DRIFT

- 12-transload (the solution film) (S9): a word garbled or text inside a picture on the solution film -- no frame
- 12-transload (the solution film) (S4): a limitation with no tick or cross on the solution film -- no frame
- 12-transload (the solution film) (S1): another person than the problem film's, or no brand on the screen, on the solution film -- no frame
- 12-transload (the solution film) (S6): the solution film does not end on what the person gets back (a feature, or no joy) -- no frame
- 12-transload (the solution film) (S2): the setup shown where none was named, or missing where it was -- no frame
- 12-transload (the solution film) (capture): the failed build says 'Today they ran into three things: the rest are billed by the size, roughly 10% of checked shipments are bigger than declared and measuring every shipment adds forklift travel and dock congestion. Tell me how Transload solves them.', keel-web 263 FR-10 says "Keel could not draw what it solves: Scene 7 states the first limitation only as 'The rest are billed by the size: Transload.', and says the how ('existing security cameras link the scan to the freight') nowhere, so a stranger cannot tell how it is solved; scene 8 does cover the third. Say that part again?" -- no frame
- 12-transload (the solution film) (capture): the solution's build ended 'failed' (failedChapter solves, failedScene None: Scene 7 states the first limitation only as 'The rest are billed by the size: Transload.', and says the how ('existing security cameras link the scan to the freight') nowhere, so a stranger cannot tell how it is solved; scene 8 does cover the third.) -- no frame

`make read-film-table RUN=... DRIFT=1` appends them to `runs/DRIFT.md` in its shape.

## Compared with `20261125-c7079b5-film.md`

The baseline: bundle `20261125T084949Z-film-walk` (its film score files in `quality/scores/`). Each move is `before -> after (+/-)`.

**The round's means**: problem film_pct 70.0 -> 75.0 (+5.0); solution film_pct 34.4 -> 0.0 (-34.4); the mean of the two films 52.2 -> 37.5 (-14.7).

Entries missing (in the baseline, not here): 09-karsa, 11-issen, 14-code-four, 15-voltair.

### 12-transload -- rank 1 -> 1

| measure | before -> after |
|---|---|
| F1 | 1 -> 2 (+1) |
| F2 | 1 -> 1 (±0) |
| F3 | 2 -> 2 (±0) |
| F4 | 1 -> 1 (±0) |
| F5 | 2 -> 2 (±0) |
| F6 | 0 -> 1 (+1) |
| F7 | 1 -> 1 (±0) |
| F8 | 2 -> 2 (±0) |
| problem film_pct | 62.5 -> 75.0 (+12.5) |
| S1 | 2 -> 0 (-2) |
| S2 | 1 -> 0 (-1) |
| S3 | 1 -> 0 (-1) |
| S4 | 2 -> 0 (-2) |
| S5 | 2 -> 0 (-2) |
| S6 | 2 -> 0 (-2) |
| S7 | 1 -> 0 (-1) |
| S8 | 1 -> 0 (-1) |
| S9 | 2 -> 0 (-2) |
| solution film_pct | 77.8 -> 0.0 (-77.8) |
| founder_pct | 81.7 -> 81.7 (±0.0) |
| T1 | -- -> 2 |
| T2 | -- -> 2 |
| T3 | -- -> 2 |
| T4 | -- -> 1 |
| told_pct | -- -> 87.5 |
| §A problem | 60.0 -> 65.7 (+5.7) |
| §B problem | 66.0 -> 70.0 (+4.0) |
| $ problem | 4.5 -> 2.5 (-2.0) |
| §A solution | 81.6 -> -- |
| §B solution | 74.0 -> -- |
| $ solution | 5.5 -> 1.4 (-4.1) |
