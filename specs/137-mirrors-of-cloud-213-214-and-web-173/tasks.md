# Tasks 137 -- Mirrors of keel-cloud 213 and 214, and the walk on keel-web 173

Branch `spec-137`, off `519efef`, in the worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-137` (`.git` a
file). Plan: `plan.md` (eight judgement calls). Against keel-cloud-docs master `219464f9` (213) and keel-web master
`8215beda` (173); keel-cloud 214's part by message. Not merged; nothing paid; no corpus revision, `MARKS_VERSION` or
contract moved here.

## FR-1 The cards

- [x] T001 `quality/readers/dimensions.md` = the vendored copy at `e3cdea00...`; the 133 pin holds the two files equal.
- [ ] T001a 214's digest, if 214 moves the cards (by message).

## FR-2 The instruction and rule mirrors (213)

- [x] T002 `instructions/chain.py`: the price whole and optional, one measure on a percent of a named base, the locked
  words with no unit where the user pays.
- [x] T003 `instructions/corpus.py`: `spec213_chain`, `optional` refused off the plan, `B2B_PAYER` gone, `spec213_reads`
  (the act bare, `owned_subject`), `R24_FACT_FOUR` emptied.
- [x] T004 `instructions/step_cost.py`: moved money (L34 on Palus).
- [x] T005 `instructions/spoken.py`: Commitment's four answers and note, Buyer and payer's share stem, Relative
  advantage's at-stake stem with *{Name}, {what it is}*.
- [x] T006 `evals/backtest.py`: L2 in the lock notes.

## FR-2 The instruction and rule mirrors (214, by message)

- [ ] T007 214's five checks mirrored; the scripted drafts obey each; the eval faults a draft that does not.

## FR-3 The walk on contract 59

- [x] T008 `harness/vectors_screens.py`: the plan's two boxes and *Optional plan*, the PUT kept, the role rows' tags,
  Commitment's block, the strings.
- [x] T009 `evals/corpus_scenario.py`: the chain words owed, the price PUT held, Commitment's Check held, *decided alone*.
- [x] T010 `evals/backtest.py` `READ_JS`: the reader's rows with their tags; Commitment's four and note.

## FR-4 The entries' prices

- [x] T011 `harness/vectors_script.py`: `founder_price`, `plan_optional_sourced`, `price_belief_owed`; the walk posts
  `optional`.

## Tests and re-pins

- [x] T012 `tests/test_cloud_213_mirror_137.py`; the re-pins, each a rule 213 or 173 moves.

## Built so far (213's half, FR-1, FR-3, FR-4)

| Commit | What |
|---|---|
| `4858aa4` | plan.md, tasks.md (written, not built) |
| `ca32d47` | FR-1: the cards, the 133 pin (and 211's step-cost pins, 213 FR-8) |
| `67cc11e` | FR-2 (213's half) and FR-4: the mirrors, the entries' prices, the re-pins |
| `e88ac09` | FR-3: the walk on contract 59, the holds, the readers' read, L2; the re-pins |
| `5389f55` | `tests/test_cloud_213_mirror_137.py` (30) |

Re-pinned, each a rule 213 or 173 moves: `test_cloud_211_mirror_133` (the cards one file; *move idle cash* now money;
10-palus priced by *move*), `test_cloud_199_mirror_130` (`B2B_PAYER` gone, 05-paidly's cost read as recorded),
`test_harness_reads_r24_135` (Voltair's three codes, 213 FR-11a), `test_seven_templates_115` and
`test_advantage_belief_113` (Current solution's act bare), `test_referee_follows_193_123` (Transload's *of the shipments
a month*), `test_reworded_founder_screens_116` (the bar's purchase and *Decided alone counts as support.*),
`test_cloud_205_208_mirror_132` (Importance's hint), `test_screens_as_drawn_090` (the plan's second box),
`test_after_130` (L2 read by name).

Interim gate on `5389f55` against keel-cloud-docs `219464f9` and keel-web `8215beda`, 2026-11-04 ET:
**5,422 passed / 0 failed / 85 skipped** (268.82 s). Master `519efef` on the same siblings: 11 failed (the pins above).

## FR-5 Gate

- [ ] T013 `set -o pipefail; make unit 2>&1 | tail -1` green against keel-cloud-docs master at 214's merge and keel-web
  master `8215beda`.
