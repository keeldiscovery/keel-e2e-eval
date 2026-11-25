# Spec 167 -- The mirrors of keel-web 263 and keel-cloud 275: the portrait stage, the frame plan, a frame left out

keel-web 263 (merged at `336eb477`, contract 91 vendored) draws the film's pictures tall: a 2:3 stage full width on a
phone, a column on a laptop with the caption and the chapter pill BESIDE the stage (`story-side-line`,
`story-side-chapter`; the stage's own caption hidden there by CSS, one DOM at every width), the stills and the copilot
strip portrait (`[data-ratio=portrait]`, 80 x 120), the building screen's frame plan (`FramePlan`: the tally, a mark
per status, the reason), a frame left out held on the picture before (`pictureMissing`), the failed build's reason
line. keel-cloud 275 (merged at `c7079b59`) draws every picture 1024 x 1536 and serves `build.pictures.plan /
reviews / kept`, `failedReason`, `pictureMissing`. The harness mirrors read 261's layout; the film judge's camera and
the strangers' walks must read 263's before the paid run on five (spec 166). Built on keel-e2e-eval master with 166
merged (`9c5dd85` or later).

## Rules
- **FR-1 The camera reads 263's stage.** `harness/film_frames.py`: on the laptop the visible caption and chapter pill
  are `story-side-line` / `story-side-chapter` (the stage's hidden); the layout told apart by
  `getComputedStyle(story-film).display` (grid on the laptop, contents on the phone) and recorded on every frame
  (`layout`, the stage's ratio `portrait|landscape` and its measured size); the *caption inside the stage* check on the
  phone alone, and on the laptop *the caption beside the stage, whole, no clipped word*; `pictureMissing` is recorded
  on the scene (`missing: true`) and is not a fault; a picture is 1024 x 1536 from 275 on (1536 x 1024 on a film drawn
  before 275: both accepted, the size recorded); the plan, the reviews, `kept` and `failedReason` kept in
  `prompts.json` as 166 writes them; the plate frame as 166 shoots it. Both films (the problem's and the solution's).
- **FR-2 The founder's screens.** `harness/story_screens.py` (~1290-1310): the building screen's plan ids
  (`frame-plan`, its tally and rows, a row's status and reason) read into the walk's record; the failed build's line
  with the reason (*Keel could not draw that part: {reason}. Say it again?*) matched with and without a reason; the
  solution candidate frame `[data-ratio=portrait]` (~1488-1495). `harness/interviewer_screens.py` (~1017-1048): the
  link's film caption on the laptop read from the side column as FR-1. `evals/three_views_strangers.py` (~1715,
  1743): `copilot-still` portrait.
- **FR-3 The reader told the layout.** `quality/film_reader.py`: each frame's label names the viewport AND the layout
  (*phone, the caption over the picture's lower third* / *laptop, the caption beside the picture*) so F8/S9 (legibility)
  and F6/S7 (the line matching its picture) are read right; the rubric's words unchanged.
- **FR-4 The free walk once, both halves.** `make film-walk ENTRIES=08-fresco DOOR=fake WHY="167's local walk"` on
  temporary detached worktrees of keel-cloud-docs `c7079b59` and keel-web `336eb477` (FakePictures 48 x 32: the stage
  reads the picture's ratio, so the fake film plays landscape -- the camera records that, no fault); both halves green
  as 166's were, the plan ids read, recorded in tasks.md. `make unit`: no new red against the base (the reds listed).
- **FR-5 Nothing paid; no respondent instruction touched** (the AI-avatar spoken-form guidelines untouched).

## Acceptance
The camera on a 263 laptop frame records the caption beside the stage and the stage portrait; the free walk's two
halves are green on keel-web 336eb477; the paid run on five can start.
