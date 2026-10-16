# Tasks 046

- [x] T001 baseline vs keel-cloud-docs `3002978` (097 merged; exported, = the 097 worktree's `8060a7e`) + keel-web 070's
  worktree at `785cc52`, nothing changed: `make unit` 2,032 passed / 57 skipped; S-005 / S-006 / S-007 all failed at the
  same place, before any approve -- PROBLEM's first CALIBRATION_QUESTIONS draft was refused (097 call 10: Importance's
  first draft is the own item alone; the script sent the five) and its repair turn carried a `repair` key the script
  has no entry for (JOB_FAILED, `LLM_UNAVAILABLE ... ['answers', 'context', 'dimensions', 'interpretation', 'market',
  'repair', 'vector']`). With that fixed S-006's COMMERCIAL first draft met `L6` (Purchase friction's *agency owner* and
  *finance* are named by the Answer, not before it), and every journey then met IDEA_NAME_REQUIRED at S2.
- [x] T002 page objects + the flow driver without Next question (keel-web 070 `7d72b3a`): S2's empty name box
  (`vectors_screens.Corridor.idea_check`), Importance's counter, ask and typed rows (`importance_rows`), the page of
  names' Select all / Clear and C3's missing Copy (`interviews_screens`), Send more's every batch response (the silent
  retry), the AI flow with no Next question and `FLOW_TIMELINE` (`interviewer_screens`)
- [x] T003 FM1-FM6 + unit tests (`evals/feedback_marks.py`, `tests/test_feedback_marks.py`: each met on a good record and
  failed on a seeded fault, an absent subject unmeasured, keel-cloud's `RoleWordsTest` cases and its exported
  `common.role_words`)
- [x] T004 journeys updated (Importance with two / with one, idea name, select all, no Copy, batch 422) -- the wire half
  done: the script's first drafts (Importance the own item alone; a list item naming a role the founder has not yet
  written left to the Answer's redraft), Importance's Answer the others alone; the idea arrives unnamed (what null,
  approve and an empty name 422 IDEA_NAME_REQUIRED) and is named on the wire (`NAME_ON_THE_WIRE`); Importance own + 1
  422 ONE_MORE_NEEDED, own + 2 200 *out of three*, the founder's list again *out of five*; the batch's 422
  INTERVIEWER_NEEDS_CREDITS; the base query's empty `categories` recorded (FM3); the typed field's `heard` (FM6); the
  feedback marks scored at the end of every journey. S-007 passed against `3002978` + keel-web `785cc52`; S-005 and
  S-006 pass every leg up to the AI interviewer's stage, which waits for *Next question* (070 F1 removed it). The screen
  half: S2 named on screen (`NAME_ON_THE_WIRE` off), Importance with one other (the one-more ask, 422 ONE_MORE_NEEDED, a
  line opened) on S-005 and with two on S-006, the rest typed by the founder; no *Someone else would use it*; Select
  all / Clear, no Copy; the AI flow without Next question; DRIFT #87 / #88 asserts
- [x] T005 `make unit` 2,074 passed / 57 skipped; `make eval K="s005 or s006 or s007"` 3 passed twice on a fresh database
  (498 s, 512 s) vs keel-cloud-docs `3002978` + keel-web `752e873`; DRIFT #85 / #87 / #88 / #89 resolved, #90 new;
  AGENTS.md
