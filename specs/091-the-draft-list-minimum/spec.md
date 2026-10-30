# Spec 091 -- A drafted list is held to the draft's rule, not the save's: the Importance mark reads the registry's minimum where it belongs

The founder-lists.md screen of 2026-10-29 (`runs/20261029T193750Z-instructions`) faulted `problem.importance` on every
run with *L1: problem.importance takes 2 to 5 items, and 1 were written*. The writer was right: `founder-lists.md` says
that with `answers` `{}` the Importance list is the problem itself alone, and the registry's `saves.min_items 2` is the
rule at Save, once the founder has named the other difficulties (keel-cloud 087, 152). The harness's `option_validity`
reads `saves.min_items` against the draft, so a correct draft scores 3 of 4 and the screen's validity reads 78.8%.

## Rules

- **FR-1 The draft's minimum.** `option_validity` (`instructions/score.py` / `validate.py`, rule L1) reads a drafted
  list against the draft's own rule: on `rival_list` with no founder answer the list is one item (the own item); with
  an answer naming N difficulties it is 1 + N (at most `saves.max_items`); `saves.min_items` is applied where the
  harness checks a saved list (the Check screen's post, the corpus's recorded lists), never a draft. The faulted case
  on 03-lullaby's bundle scores 4 of 4 under the new reading; a draft that truly writes fewer than its answer names is
  still faulted, by the right rule, with a test for each.
- **FR-2 Decided before.** `quality/decisions.toml` gains no entry (a harness mark, not a founder's decision).
- **FR-3 Nothing else moves.** The other rules, the marks version (unless a mark's reading moved: then `MARKS_VERSION`
  and its note), the screens' other marks.

## Acceptance

`make unit` green with ZERO failed; `make instruction-screen K=03-lullaby/CALIBRATION DRY=1` unchanged in its case list;
the recorded bundle `runs/20261029T193750Z-instructions` re-scored (`make rescore` or the bundle's own re-read, as the
harness offers it) shows `problem.importance` valid on all three runs. Build after 090. Build on the founder's word of
2026-10-30.
