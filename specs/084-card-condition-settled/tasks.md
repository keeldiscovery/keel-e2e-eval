# Tasks 084 -- The card's *Only people who* line is the settled condition (keel-cloud 148 FR-1)

Branch `084-card-condition-settled` (worktree `wt/eval-084`, `.git` a file), off master `5da2837` (the spec on top of
`851f9db`). Read only: keel-cloud-docs `f48f256e` (spec 148, contract 44 unchanged), keel-web `786d4c3`. `REVISION`
17, `MARKS_VERSION` 21, `INTERVIEWER_MARKS_VERSION` 12 unchanged. **No paid call.** Nothing merged or deployed; every
commit pushed to the branch.

| Commit | What |
|---|---|
| `95f6021` | FR-1 + FR-2: `harness/vectors_script.card_condition`, `evals/corpus_scenario.leg_context`'s comment, `tests/test_drawn_screener_seams_077.py` |
| this commit | this file, `AGENTS.md` (the 084 paragraph) |

## Unit

| | passed | failed | skipped |
|---|---|---|---|
| master `851f9db` | 3,670 | 0 | 53 |
| `95f6021` | **3,670** | **0** | 53 |

The count holds: 077's pin of the old card (`test_the_card_draws_no_condition_line_before_the_confirm`) was rewritten
as 148's, not added beside it. `make unit` 183 s.

## FR-1 -- the card's condition is the settled one

- [x] T001 `card_condition(entry)` returns `segment_of(entry)["condition"]` (code's drawn condition on a `DRAWN` row,
  the scripted one elsewhere); its docstring names keel-cloud 148 FR-1 and spec 084.
- [x] T002 `leg_context`'s comment names 148 (the settled condition, on 07-mulchrun the one code draws), not 077's
  *none on 07-mulchrun*.
- [x] T003 `scripted_segment` stays: the fake's CONTEXT_INTERPRET result still writes none on 07-mulchrun.

## FR-2 -- pinned

- [x] T004 `test_the_card_draws_the_settled_condition`: on 07-mulchrun `card_condition` is *are based in the
  Dallas-Fort Worth suburbs*, equal to `segment_of`'s, while the result's (`scripted_segment`) is none; on 05-paidly it
  is the scripted *work mostly for agencies*. The `read_back` / `segment_line` tests do not move.

## FR-3 -- nothing else moves

- [x] T005 The marks, the readers, the quality cycle, 082's and 083's work, `REVISION` 17: untouched.

## The acceptance

| Command | Result |
|---|---|
| `make unit` | **3,670 passed, 0 failed, 53 skipped** (183 s) |
| `make up` | all gates passed (keel-cloud-docs `f48f256e`, keel-web `786d4c3`; 11 s) |
| `make eval K=s007` | **green** 153 s (`duration_s` 149.2); the card asserted `Only people who: are based in the Dallas-Fort Worth suburbs.` |
| `make down` | done |

## What did not hold

- Nothing in the gate. keel-web's checkout recorded `dirty: true` in `versions.json`: an untracked `.idea/`, no source.
- Not done: the remote six on staging (no deploy, no remote run in this spec's brief).
