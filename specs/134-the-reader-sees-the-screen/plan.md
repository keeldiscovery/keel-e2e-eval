# Plan 134 -- The reader judges what the screen showed; the corpus rungs fit the card

Branch `spec-134` (worktree `wt/keel-e2e-eval-134`, `.git` a file), off `60d6147` (the spec and its two amendments).
Read only: keel-cloud-docs master `c456c0b3` (the back-test corpus, revision 23, `canon/designs/measured-beliefs/backtest/`),
keel-web master `7509a44b` (`ListQuestion.tsx`: the L32 note drawn as `li.listrow.listrow--note`
`[data-testid=list-founder-note]`, the guidance line `.listcheck__note`). No stack, no model, no walk, no reader, no paid
call, no key read; the unit suite only.

**The coordinator's correction (2026-11-04, mid-build):** the back-test entries live in keel-cloud-docs
(`backtest/<entry>.yaml`, revision 23), not in `instructions/screen_entries.py`. FR-4 is delivered as a review,
`corpus-rewording.md` beside this plan -- every row of the fourteen gallery entries that breaks a card rule, with its
rewording and the rule, and a second table of the eval fixtures and pins that quote those rows. A keel-cloud spec applies
it to the YAMLs and bumps the revision; the fixtures move when that lands. Nothing outside this worktree is touched, and no
fixture or pin moves on this branch (`make unit` stays green against revision 23).

## Where each FR lands

| FR | Where |
|---|---|
| FR-1 the read-back is the screen's | `evals/backtest.py` `read_back` (`SCREEN_DRAWN_BELIEF`: no wire `belief` on an Answer or a Check screen) |
| FR-2 rows are rows | `harness/vectors_screens.py` `_list_rows` (`li.listrow--note` read as `note`, never a row; the guidance line `.listcheck__note` as `guidance`); `evals/backtest.py` `READ_JS` (rows skip `.listrow--note`; `note` captured), `founder_screens` (carries `note`); `quality/readers.py` `founder_screens` (the note labelled under the rows) |
| FR-3 the Check after the edit | `harness/vectors_screens.py` `list_check` (the camera shot again after the edit, `check-<key>-after-edit`; the step named for what it does; the docstring); `evals/backtest.py` `founder_screens` (a Check record carries the after-edit read: rows, Keel will test, the `-saved` shot) and `founder_answer`'s `check` branch (*typed {n} of their own rungs over Keel's draft, then saved*); `quality/readers.py` (rows named the founder's where they typed them) |
| FR-4 the corpus | `specs/134-the-reader-sees-the-screen/corpus-rewording.md` (review only) |
| FR-5 nothing else | prompts, rubric 5 and the cards unchanged; `make unit` green |

## Order

1. The gate at the base (two pins of `tests/test_decided_before_087.py` the file of record moved past: D-2026-11-04-03..05).
2. FR-1, FR-2, FR-3 with their tests (`tests/test_reader_sees_screen_134.py`).
3. FR-4's review file; tasks.md.

## Judgement calls

- FR-2 names the founder note `note`; the guidance line under every list (`.listcheck__note`) was already captured as
  `note` by `_list_rows` -- it keeps that key where no founder note is drawn, and where both are drawn `note` is the
  founder note and `guidance` the line (both labelled for the reader).
- FR-3: the founder screen record is the camera's; `list_check` takes a second camera shot after the founder's edit, and
  `founder_screens` folds it into the Check screen's record (rows, Keel will test, the file of the after-edit shot), so the
  reader is handed one Check screen, as the founder left it.
