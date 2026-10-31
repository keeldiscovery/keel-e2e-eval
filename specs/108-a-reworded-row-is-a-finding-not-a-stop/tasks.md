# Tasks 108 -- A reworded founder row is picked by its nearest label and named as a drift, not a stop

Branch `108-a-reworded-row-is-a-finding-not-a-stop` (worktree `wt/keel-e2e-eval-108`), off master `554bb03` (107
merged). Built by Claude on 2026-10-30. Read only: the bundles `runs/20261030T183150Z-backtest-21-codyco`,
`runs/20261030T150723Z-backtest-13-aircaps`, `runs/20261030T173645Z-backtest-08-fresco`, and keel-cloud-docs at
`4d790648` (spec 177 written, not built). **No stack, no browser, no model, no paid call.** Nothing merged into master;
the branch pushed after every commit, never force-pushed.

| Commit | What |
|---|---|
| `aeacc22` | FR-1 / FR-2 in `evals/corpus_scenario.py`; 104's 21-codyco compatibility test re-pinned |
| `5b45b71` | FR-1: a possessive *'s* folds; a negation never does |
| `0b2b091` | FR-4: `tests/test_reworded_row_108.py` and the 13-aircaps and 08-fresco fixtures |
| `f5930d3` | FR-3: `runs/DRIFT.md` #101 |
| the docs commit | this file and `AGENTS.md`'s spec-108 paragraph |

## Unit (the gate)

| | passed | failed | skipped |
|---|---|---|---|
| 107's tasks.md record, **master** `554bb03` | 4,166 | 0 | 53 |
| **branch at `f5930d3` (the last code; the docs commit adds none)** | **4,186** | **1** | **53** |

The +21 are `tests/test_reworded_row_108.py`; 104's file keeps its 17 (one
re-pinned, none removed). `make unit` run from the worktree, on the worktree's own `make venv`, with `stack.toml`'s
siblings at keel-cloud-docs `4d790648` and keel-web `2332958`. **The one failure is not this spec's and is not fixed
here:** `tests/test_open_link_092.py::test_every_pin_the_harness_reads_is_in_136s_markup[src/components/interviews/GroupSection.tsx-ids2]`
(`missing ['group-link']`) -- keel-web 142 (`9c5d8d0`, 2026-10-30 20:10 ET, merged on keel-web master during this
build) draws no shortened link and moves the URL to `data-url`; the harness's pin (`interviews_screens.GROUP_LINK`,
the 092 test's id list) is keel-e2e-eval spec `098-the-group-url-off-data-url`'s, written and not built. Master
`554bb03` fails the same test against that keel-web (the test and everything it reads are untouched by this branch);
107's 4,166 / 0 / 53 was read against keel-web before 142.

## FR-1 -- the nearest row

- [x] T001 `evals/corpus_scenario.py:1676` `nearest_rows(want, rows, typed)`: the drafted rows nearest a typed label no
  row equals, by the nearest tier that has any -- (1) the same words once folded (`_folded_words`, `:1665`: lowercased,
  a possessive *'s* and punctuation dropped, `_fold` `:1651` takes *-ing / -ed / -s* and then a last *e* off, and
  *could / can / would / will* read one word); (2) a row carrying every content word of the typed label
  (`_content_words`, `:1672`, the folded words less `_NOT_CONTENT`: articles, prepositions, pronouns, *to be*, the
  modals); (3) a row whose content words are all the typed label's and at least half of them (see *Not foreseen* 1).
  Never a candidate: a row that is another of the founder's typed labels word for word (it is the founder's own row),
  or a row whose negations (`_NEGATIONS`, `:1648`; *can't* reads *not*) differ from the typed label's.
- [x] T002 `_choose_label` (`:1706`): an exact label is picked as in 104, no finding. Otherwise exactly one nearest row is
  picked, and one finding is appended: `{"what": "DRIFT: Keel reworded the founder's row '{typed}' as '{drafted}' (spec
  081)", "served": {dimension, typed, drafted, rows}}`; the walk clicks the drafted label and goes on. More than one as
  near: 104's `VectorsScriptError`, by name, with *N rows are as near ([...], spec 108 FR-1)*; no DRIFT line.
- [x] T003 The golden walk (`strict`) is unchanged: the typed label and index, no drafted row read, no finding
  (`test_the_golden_walk_is_unchanged`).

## FR-2 -- a row not drafted at all

- [x] T004 No row near: 104's stop, by name (`leg_calibrate`'s step at `:1819`, unchanged, records both lists and
  re-raises). Before raising, `keel_left_out` (`:1699`: the typed rows with no drafted row of that label and none near
  it, in the entry's order) writes one finding `{"what": "{Dimension}: Keel left out: '...'", "served": {dimension,
  drafted, typed, "left out"}}` and the refusal says *Keel left out [...] (spec 108 FR-2)*. 104's *Keel added*
  finding is written before the pick (`leg_calibrate`), so on 08-fresco both stand: *Purchase friction: Keel added: 'A
  budget approval'* and *Purchase friction: Keel left out: 'A trial on one live job'*.

## FR-3 -- the record and DRIFT.md

- [x] T005 Both findings go to `j.findings`, which `evals/backtest.py` writes as the back-test record's `findings`
  (`backtest.json`, listed in `backtest.md`), so each cycle's record carries the DRIFT lines (they open `DRIFT:`).
- [x] T006 `runs/DRIFT.md` #101 (*Owed, keel-cloud*): the three cases with their bundles and transcript seqs, what the
  harness does now, and keel-cloud-docs spec `177-a-founders-row-is-kept-as-typed` (written at `4d790648`, not built).

## FR-4 -- tests

- [x] T007 `tests/test_reworded_row_108.py` (21): the fold (five pairs) and what does not fold (*took* / *takes*,
  a dropped *not*, *can't*); 21-codyco compatibility: the tense fold picks row 0 and writes the DRIFT line (the row
  picked on screen that day); 13-aircaps adoption friction: picked by content words (the row picked on screen), and its
  compatibility by label, no finding; 08-fresco purchase friction: stops by name with the left-out finding beside *Keel
  added*, and its buyer/payer by label; two near rows stop on every `vs.PICKED` dimension; the nearest tier wins;
  another typed row is never the rewording; a one-word row is not near a long label; strict unchanged.
- [x] T008 Fixtures (runs/ is git-ignored), in 104's shape: `tests/fixtures/runs/13-aircaps-choose-108/solution.json`
  (inputs.json's SOLUTION answers; the review's stored lists, transcript seq 59; Choose seq 48, 55) and
  `tests/fixtures/runs/08-fresco-choose-108/commercial.json` (COMMERCIAL; review seq 67; Choose seq 55, 59). 21-codyco
  reads 104's `21-codyco-choose-104/solution.json`.
- [x] T009 Re-pinned, with why: `tests/test_choose_by_label_104.py`'s
  `test_21_codyco_compatibility_was_reworded_so_the_walk_stops_by_name` is now
  `..._so_the_walk_picks_it_and_names_the_drift` -- 108 replaces that stop; its FR-3 assertion (all three drafted rows
  are *Keel added*, by exact label) stands.

## Not foreseen by the spec

1. **The spec's two tests do not pick 13-aircaps.** The typed *Wear the glasses, paired to the phone* has content words
   *wear, glasses, paired, phone*; the drafted *Pair the glasses to their phone* lacks *wear* (Keel split it into a
   separate row, *Wear the glasses in conversations*), so no row has the same words and none carries every content
   word -- read literally, FR-1 stops aircaps, against FR-4's *picks by content words*. Tier (3) reads the containment
   the other way (every content word of the row is the typed label's, at least half of them): it picks *Pair the
   glasses to their phone* alone (3 of 4), the row the walk picked on screen that day. The half floor and the
   negation guard keep it from reading a short row (*Glasses*) or a dropped *not* as the founder's.
2. **Tiers, not a union.** A row with the same folded words is taken over one that only carries the content words;
   *exactly one* is counted inside the nearest tier with any. A union would stop where one row is plainly nearer.
3. **104's *Keel added* still compares labels exactly**, so a reworded row 108 picks is also named there (21-codyco
   compatibility: all three drafted rows, the picked one included, beside its DRIFT line). Kept as 104 pins it; a
   reader sees both.
4. **Only the picked row is read for a rewording.** 21-codyco's other two re-tensed rows (*took* -> *takes*, an
   irregular past the fold does not read; *were* -> *are*) get no DRIFT line, and the left-out finding is written only
   on FR-2's stop; they show in *Keel added*. DRIFT.md #101 names all three.
5. **Nothing in `quality/` counts findings by name** (`quality/cycle.py` runs the back-test and the readers); *the next
   cycle counts them* is the record carrying the `DRIFT:` lines. `backtest.md`'s findings line prints
   `f.get('refused') or f.get('batch')` after each `what`, which is `None` for these (as for 104's *Keel added*).
