# Tasks 072 -- DRIFT #95, #96, #97 closed: the guards flip, the two out-of-scope script entries go

Branch `072-drifts-closed` off master `379e08b` (worktree `wt/eval-072`). The products, read only: keel-cloud-docs master
`bc2505c6` (spec 134 at `741d631c` -- `VectorCorridor.complete()` over the scope, `ScreenChain` chaining the scope's
calibrations alone, contract 39 -- and spec 135 -- `ReadBack` drops the window clause where no gate is served, the stored
window unchanged) and keel-web master `3a31502` (spec 112 -- no `recallWindow` sent and no window line drawn where
`servesGate(scope)` is false; contract 39 vendored). The stack built from those checkouts through the four symlinks
beside the worktree (spec 071 D-02), keel-runtime 0.8.0 bundled in keel-connect-skill `c677950`. No paid command, no key.

One commit per FR, each gated on `make unit` green.

## Unit

| | passed | failed | skipped |
|---|---|---|---|
| master `379e08b` (before any change) | 3,265 | 0 | 53 |
| FR-1 `fd9822d` | 3,277 | 0 | 53 |
| FR-2 `5fd797b` | 3,284 | 0 | 53 |
| FR-3 `41d1a28` | 3,294 | 0 | 53 |
| FR-4 `2894bb8` | 3,299 | 0 | 53 |
| FR-5 (this commit) | 3,299 | 0 | 53 |

## FR-1 -- #95 closed -- `fd9822d`

- [x] T001 `evals/corpus_scenario.plan_complete`: before *Lock and approve* is pressed, on every study (ALL included),
  `GET plan` reads `complete: true` and lists the scope's vectors, each complete (the persona recorded: NOT_SET on the
  problem study, which needs none).
- [x] T002 `_drift_95_lock` (the lock on the wire with `{expectedRevision}` round the disabled button) removed;
  `_drift_95_guard` fails a journey whose button stays disabled for 15 s, the plan as served named. `leg_lock` holds the
  plan, then presses the button on the page; `vectors_screens.word_pilot_and_lock`'s disabled branch clicks nothing.
- [x] T003 Unit `tests/test_drifts_95_97_closed.py`: the plan held on ALL / PROBLEM / COMMERCIAL, five faults (as filed,
  outside the scope, a vector incomplete), the guard locking nothing, `leg_lock`'s order. DRIFT #95 marked RESOLVED.

## FR-2 -- #96 closed -- `5fd797b`

- [x] T010 `_drift_96_guard`, on every study that serves no gate: no `recallWindow` key in any `PUT context` the page
  sent, no window line on the card, the served sentence the windowless read-back (`vs.read_back(window=False)`; on a
  non-strict walk no *counting the last* clause). `leg_context` holds the windowless sentence as its main assertion.
- [x] T011 The confirmed context's `fields.recallWindow` is held to keel-cloud's `RecallWindow.DEFAULT`
  (`STORED_WINDOW_DEFAULT`, `{7, NIGHTS}`): none was sent, keel-cloud stores its default (contract 39: always present
  on a GET) and keel-cloud 135 leaves its clause out. `_drift_96_window` / `DRIFT_96_WINDOW` removed.
- [x] T012 Unit: the guard green on money alone, four faults (the PUT as filed, the line, the clause, a key sent as
  null). DRIFT #96 marked RESOLVED with both halves.

## FR-3 -- #97 closed -- `41d1a28`

- [x] T020 `harness/vectors_script.chained_out_of_scope` names nothing; `calibration_jobs` scripts the scope's vectors
  alone -- the two stand-in entries gone (money alone's CALIBRATION_QUESTIONS script: the money slice and its three
  redrafts, four entries where it was six).
- [x] T021 `evals/scope_journey.drift_97`: the wire's CALIBRATION_QUESTIONS jobs counted by `vector` equal the script's
  (one slice a vector in scope and its redrafts), every one APPLIED, none for a vector outside the scope.
- [x] T022 Unit: the chain on three scopes, money alone's script, six faults (as filed, one out-of-scope slice, a
  redraft or the slice missing, a refused job). `tests/test_study_scopes.py`'s money walk follows. DRIFT #97 RESOLVED.

## FR-4 -- contract 39 -- `2894bb8`

- [x] T030 `_lock_lands` holds the receipt's `questions.interactionIds` present as a list (required since contract 38,
  `minItems: 0` since 39), its length the scope's RESPONDENT_QUESTIONS jobs -- 0 on money alone, which goes on to the
  links with nothing waited on, 1 elsewhere.
- [x] T031 The harness pins and reads no contract number anywhere (no `x-keel-contract` read, no constant); the
  docstrings naming contract 38 describe what 133 introduced and stay.
- [x] T032 Unit: money alone's empty receipt lands, a gated study still names its one job, three receipts off contract
  39 refused.

## FR-5 -- nothing else moves -- this commit

- [x] T040 `MARKS_VERSION` 20 and corpus `REVISION` 16 unchanged (`test_marks_and_revision_do_not_move`); no corpus,
  registry, fixture or golden number moved; under ALL the script is unchanged (`chained_out_of_scope` was already empty
  there). AGENTS.md's study-scopes paragraph says the three are closed. The DRIFT entries name the runs below.

## The journeys (local stack, keel-cloud-docs `bc2505c6` + keel-web `3a31502`, the scripted executor)

`docker ps` before `make up`: only `focused_robinson` (an unrelated postgres). Booted with `make up`, the journeys run one
at a time with `make eval K=...`, torn down with `make down`. Runs of record (the FR-4 tree, `versions.json` `2894bb8`,
clean; keel-web dirty only by its own untracked `.idea/`):

| Journey | Run | Result |
|---|---|---|
| S-015 | `runs/20261026T063941Z-s015-problem-only` | **passed** (91 s), SC1-SC7 7 of 7 |
| S-016 | `runs/20261026T064147Z-s016-money-only` | **passed** (71 s), SC1-SC7 7 of 7 |
| S-005 | `runs/20261026T064856Z-s005-countly` | **passed** (295 s) |
| S-006 | `runs/20261026T065403Z-s006-paidly` | **passed** (321 s) |
| S-007 | `runs/20261026T065935Z-s007-mulchrun` | **passed** (133 s) |
| S-014 | `runs/20261026T070159Z-s014-green` | **passed** (138 s) |

What the two scoped journeys read now: on both the plan reads complete over the scope (`[PROBLEM]` with the persona
NOT_SET; `[COMMERCIAL]` with it SET) and *Lock and approve* is pressed on the page; S-015 chains three
CALIBRATION_QUESTIONS jobs, all PROBLEM; S-016 four, all COMMERCIAL, its context PUT carries no `recallWindow`, the card
draws no window line, the sentence ends *"... keep the stock records matching what is on the shelves."*, and the lock's
receipt carries `interactionIds: []` before the owners' links go out.

## Discovered

- D-01 The first S-005 (`runs/20261026T064323Z-s005-countly`) failed on guide mark G4 alone: the second *Play the
  welcome again*, seeked to its end through the seam, did not close the sheet (`second: {opened: true, closed: false}`,
  no `guide-seen` request). Nothing this spec touches (the guide's welcome, keel-web 080); the re-run on the same stack
  passed with G4 met. A timing flake of the seam's end-seek, recorded, not a DRIFT.

## Left open

- No DRIFT written: every journey met the products as their specs say.
- No journey walks the solution or solution + money studies (spec 071's *Left open* stands).
