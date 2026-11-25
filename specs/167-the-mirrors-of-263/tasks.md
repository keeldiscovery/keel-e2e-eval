# Tasks -- spec 167

Base: `origin/master` `c0c80fa` (166 merged, spec 167 committed). Built 2026-11-25 from 02:00 ET by a builder (Claude
Opus 5.5) in the worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-167`, branch `167-the-mirrors-of-263`.
Nothing paid: no model, no key, no vendor, no pip install (the main checkout's `.venv`, symlinked, ignored), no network
but `git fetch` / `git push` of this branch and one `npm ci`; `DOOR=fake` only (keel-cloud's fakes, FakePictures,
`KEEL_PICTURES` unset). The local stack serves keel-cloud-docs master `c7079b59` (contract 91) and keel-web master
`336eb477` (263 merged) from temporary detached worktrees (`wt/keel-cloud-eval-167`, `wt/keel-web-eval-167`, removed
after), named in this worktree's `stack.toml` copy only (never committed; restored before the last commit).

- [ ] T0 Set up: the worktrees, the base's `make unit` (the reds listed below), this file.
- [ ] T1 FR-1 the camera reads 263's stage (`harness/film_frames.py`): the drawn caption and pill (`story-side-line` /
  `story-side-chapter` where `story-film` is a grid), the layout, the stage's ratio and size on every frame, the
  inside check where the caption is over the picture and the beside-the-stage check (whole, no clipped word) in the
  column, `pictureMissing` recorded on the frame and never a fault (both films), the picture's size recorded (1024 x
  1536 or 1536 x 1024 accepted), the plate and `prompts.json` as 166 writes them.
- [ ] T2 FR-2 the founder's screens: the frame plan read on both building screens (`story_screens`), the failed line
  with and without a reason, the candidate frame's ratio; the link's drawn caption on the laptop (`interviewer_screens`
  `FILM_JS`); the copilot still's ratio (`three_views_strangers`).
- [ ] T3 FR-3, FR-5 the reader's frame labels name the viewport and the layout (`quality/film_reader.py`, the labels'
  words in `quality/readers/film-reader.md`; the rubric unchanged); the unit mirrors; no respondent instruction touched.
- [ ] T4 FR-4 the free walk on 08-fresco, both halves, on keel-cloud `c7079b59` + keel-web `336eb477`; `make unit`
  after; this file's sections.
