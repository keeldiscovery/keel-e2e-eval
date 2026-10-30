# Tasks 104 -- Choose picks the founder's own row, found by its label

Branch `104-choose-picks-the-founders-own-row` (worktree `wt/keel-e2e-eval-104`), off master `92c0b75`. Built by Claude
on 2026-10-30. Read only: the bundle `runs/20261030T183150Z-backtest-21-codyco` (and, for the survey below, every
`runs/20261030T*-backtest-*` bundle of the day). **No browser, no stack, no paid call.** Nothing merged into master; the
branch pushed after every commit, never force-pushed.

| Commit | What |
|---|---|
| `b1209bb` | FR-1..FR-3 in `evals/corpus_scenario.py`; the old `_choose_label` test re-pinned |
| `b92b4d1` | FR-4: `tests/test_choose_by_label_104.py` and the 21-codyco fixture |
| `b8aeb00` | the refusal's line wrapped; `_choose_label`'s docstring names the reworded-label case |
| the docs commit | this file and `AGENTS.md`'s spec-104 paragraph |

## Unit (the gate)

| | passed | failed | skipped |
|---|---|---|---|
| 103's tasks.md record (branch `1f38236`) | 4,077 | 0 | 53 |
| **master `92c0b75`** (103, 105's spec, 106 merged) against keel-cloud-docs at `9f5be079` | **4,076** | **1** | **53** |
| **branch at `b8aeb00` (the last code; the docs commit adds none)** | **4,093** | **1** | **53** |

The +17 are `tests/test_choose_by_label_104.py`. Master's row was run on a detached worktree at `92c0b75` (removed
after). **The one failure is not this spec's and is not fixed here:**
`tests/test_credits_at_begin_088.py::test_the_mirror_is_keel_clouds_charge_table` (`assert 13 == 12`) -- the sibling
keel-cloud-docs is past keel-cloud 169 (`d5fdce45`, `InferenceCharge.VERSION` 13) while the harness mirrors 12. That is
spec 105 FR-2's (`PRICE_VERSION` 12 -> 13 in `harness/interview_charge.py`, `interviewer_fake.py`, `contacts_fake.py`
and this test's pins), built after 104; fixing it here would build half of 105 on this branch. 103's 4,077 / 0 / 53 was
read against the sibling before 169.

## FR-1 -- by label

- [x] T001 `evals/corpus_scenario.py:1639` `_choose_label`: `pickedIndex` indexes the entry's typed items
  (`_typed_labels`, `:1629`, `answer.listed["items"]`); off strict the label is looked up on the drafted rows
  (`_drafted_labels`, `:1634`, `question["draft"]["items"]`, the list the Check screen saved untouched) and the row is
  `rows.index(label)`. No row of that label (or no draft at all) raises `VectorsScriptError`: *{dimension}: the
  founder's picked item {label!r} is not on the drafted list (spec 104 FR-1); Keel drafted [...], the founder typed
  [...]*. The old clamp (`min(index, len(rows) - 1)`, the model's item at the entry's index or the last) is gone.
- [x] T002 `leg_calibrate` (`:1728`) catches the refusal and records it in its own step (*{dimension}: the founder's
  picked row is on Keel's drafted list, found by its label (spec 104 FR-1)*, expected `{picked}`, actual `{drafted}`),
  then re-raises -- the walk stops there, the bundle shows both lists.
- [x] T003 The comparison is exact (the radio is clicked by `name=label, exact=True` as before). Labels are compared as
  served; no case or tense folding (see *Not foreseen* below).

## FR-2 -- every picked dimension

- [x] T004 The rule sits on the one `if key in vs.PICKED:` branch, so it holds for compatibility, adoption friction,
  buyer/payer alignment and purchase friction alike. Buyer/payer's typed list carries *Nobody else* at 0 (the corpus's
  `saved_list` shape) and its draft does too, so the founder's `pickedIndex` (1 for 21-codyco, *The hotel's owner*) is
  found by label as any other.

## FR-3 -- the added rows are named

- [x] T005 `keel_added` (`:1658`): the drafted labels not among the typed ones, in the drafted order.
  `_name_keel_added` (`:1664`) appends one finding per picked dimension where that is not empty:
  `{"what": "Adoption friction: Keel added: 'Forward unanswered calls to Codyco', 'Connect Codyco to the hotel's PMS'",
  "served": {dimension, drafted, typed, added}}` (the name is `vs.NAMES`). No fault. It is written before the pick, so a
  refused pick still leaves the finding in the record.
- [x] T006 Rows typed but not drafted (Keel left the founder's row out) are not this finding's -- the spec names added
  rows only; where the left-out row is the picked one, FR-1's refusal names it.

## FR-4 -- tests

- [x] T007 `tests/test_choose_by_label_104.py` (17 tests): two prepended rows pick the founder's label (row 2, where
  the old clamp gave Keel's row 0) and a list in the founder's order picks the row the index picked -- each over all
  four `vs.PICKED` dimensions; a missing label refuses by name, an empty draft too; the golden walk keeps the typed
  label and index; FR-3's finding (one, none where Keel drafted only the founder's); the leg's wiring; the 21-codyco
  fixture, both SOLUTION picked dimensions.
- [x] T008 The fixture `tests/fixtures/runs/21-codyco-choose-104/solution.json` (runs/ is git-ignored): inputs.json's
  typed compatibility and adoption-friction answers (items, faces, `pickedIndex 0`) and Keel's drafted lists as the
  review stored them (transcript seq 60), with the label the walk picked on Choose (seq 49, 56).
- [x] T009 `tests/test_vectors_journey.py:560` re-pinned: its live case (`("y", 1)`, the index clamped to the model's
  last row) is now a by-label pick (`("C", 1)`).

## Strict and back-test: how they differ

- **Strict** (the golden walk, the scripted executor: S-005/6/7): unchanged. `_choose_label` returns the typed label and
  the typed index without reading the drafted rows -- the scripted draft is the entry's own list, and the leg's *each
  drafted list is the entry's own* step already fails the journey if it is not. No FR-3 finding is written (it could
  only ever be empty).
- **Back-test / S-012** (`strict=False`, Keel's own model): the label is looked up on the drafted rows (FR-1), a miss
  stops the walk by name, and Keel's added rows are one finding per picked dimension (FR-3).

## Not foreseen by the spec

- **The drafted list does not always keep the founder's labels word for word.** In the very bundle the spec cites,
  21-codyco's **compatibility** draft moved the founder's tense on all three conditions (*Unanswered calls could be
  forwarded ...* -> *... can be forwarded ...*, *took* -> *takes*, *were* -> *are*); the earlier re-walk of the day
  (`20261030T161100Z`) drafted them word for word. Under FR-1 that walk now **stops at compatibility, by name, before
  adoption friction** (`test_21_codyco_compatibility_was_reworded_so_the_walk_stops_by_name`). Across the day's
  bundles the typed picked label was off the drafted list on three Choose screens of about thirty: 21-codyco
  compatibility (`183150Z`, the tense), 13-aircaps adoption friction (`150723Z`, *Wear the glasses, paired to the
  phone* drafted as *Pair the glasses to their phone*), 08-fresco purchase friction (`173645Z`, *A trial on one live
  job* not drafted). Each of those walks would now stop where it used to pick a row the founder never chose. Whether
  that is a product fault (spec 081's word-for-word rule) for `runs/DRIFT.md`, or the harness should match a reworded
  label some other way, is the coordinator's call; this build implements FR-1 as written.
- `question["draft"]` is read before the Check screen's save, so a row `_cut_over_cap_rows` cuts to nine words is
  matched (and FR-3 names it) as Keel drafted it, before the cut. A founder's own label over the Check screen's nine
  words would be cut too and then not clicked by its full label on Choose -- as before this spec (the old branch also
  clicked the drafted label); none of the day's bundles cut a founder's row.
