# Tasks 120 -- the Insights view's second-stem group

Built by the coordinator (Claude Fable 5.1) on 2026-11-01 in the worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-120`
(branch `120-the-insights-also-group`, cut off master `da5ff05`), while cycle 6 walked on the main checkout.

- [x] FR-1 `harness/vectors_screens.py`: `also = {heading, quotes}` from `[data-testid=insights-also]`, the heading added to
  the box's own lines (so `report_no_repeat` takes it out), `None` where the page draws none.
- [x] FR-2 `evals/report_marks.py` `expected_box`: `is_also(q)` on `alsoHeading`; groups keep the first-stem quotes, a
  group emptied by it is dropped, its count follows; `also` expected; `took_by` = the served `countLine`, else the
  composed line. The box loop compares the drawn `also` group (quotes and heading) and faults a second-stem group drawn
  where the wire has none.
- [x] FR-3 `tests/test_insights_also_group_120.py` (2). The targeted suites `test_report_marks`, `test_after_131`,
  `test_revision_16_walk` pass (130).

## Gate

`set -o pipefail; make unit 2>&1 | tail -1` on the final tree, 04:45-04:49 ET: **4,868 passed, 0 failed, 53 skipped**
(master `da5ff05`: 4,866 + 53).

## Not foreseen

- The page's `say()` on the count line is the identity on these words; held as drawn.
- The s012 cell's other expectations (*Keep interviewing*, *Nothing to read into yet*) were already met; only the box
  comparison failed.
