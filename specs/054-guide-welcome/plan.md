# Plan 054 -- The guide's welcome

Branch `054-guide-welcome` off master `03b31c2` (rebase onto 053 if it merges first: re-find line numbers, renumber
DRIFT). Lands with keel-cloud 106 (contract 20) and keel-web 080; nothing here runs until both are on a stack.

## Files

- `harness/vectors_screens.py` -- the six test ids and the seam's name as constants (080's words, spelled once);
  `GuideWelcome` (FR-1); `Corridor.frame()` gains `welcome`. The page-state read is one `evaluate` over the sheet
  and the `<video>`, so a read costs one round trip (FR-5's 5 s).
- `harness/browser.py` -- `MarketStep.start(welcome="pass" | "hold")`; the pass-by imports `GuideWelcome` inside the
  method (`vectors_screens` imports from `browser`, so no top-level import).
- `evals/preludes.py` -- `create_project(…, welcome="pass")` forwards it.
- `evals/corpus_scenario.py` -- `Journey.hold_welcome`, `Journey.guide` (the record); `leg_project` forwards
  `welcome="hold"` when set; `leg_welcome(j, walk=False)` (FR-2, FR-3); a `page.on("request")` listener from *Start*
  to the end of the leg collecting every `guide-seen` request and the summary responses (kept off after, so later
  legs pay nothing); `_score_guide(j)` beside `_score_report` (`guide.json`, `guide-marks.json`); `run(…,
  welcome_walk=False)` sets `hold_welcome` and calls `leg_welcome` after `leg_project`, `_score_guide` after
  `score_feedback`. FR-2 (d)'s next write is read inside `leg_context` from the same listener's response.
- `evals/test_s005_countly.py` -- `welcome_walk=True`. S-006 / S-007 / S-014: no edit (they inherit FR-2 via `run`).
- `evals/guide_marks.py` -- new (FR-4), `GUIDE_MARKS_VERSION = 1` with its history comment.
- `tests/test_guide_marks.py` -- new: a good record per journey shape (S-005 local, S-006 local, remote), then each
  seeded fault of Acceptance 1; the unmeasured rule. `tests/test_vectors_screens_guide.py` -- the pass-by and
  `skip_in_view` over a stub page whose `evaluate` / `locator` answer canned values (no browser in `make unit`).
- `runs/DRIFT.md` -- entries from #95 as found.

## Order

1. Marks + unit tests (no stack): `make unit`, count recorded.
2. Page object + pass-by + leg against a stack on 106 + 080; the first run reads the page's real ids, menu and
   caption, and files DRIFT for anything the design does not say.
3. `make eval K="s005 or s006 or s007 or s014"` green; seconds per journey in tasks.md.
4. After the deploy: remote journeys on staging (G4 / G5 unmeasured with the why).

## Risks

- Bundled Chromium may not decode the `mp4` (judgement call 1): the hold never needs frames, only `paused`/`muted`.
- A 409 on the context Save would hang `Corridor.context` (it has no second press): the listener asserts the status
  before the card wait, so the failure names G3, not a 60 s timeout.
