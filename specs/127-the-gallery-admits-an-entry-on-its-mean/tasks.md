# Tasks 127 -- The gallery admits an entry on its mean

Branch `spec-127` (worktree `wt/keel-e2e-eval-127`) on master `a65834f`. Built by a builder (Claude, on the
coordinator's brief) on 2026-11-01. **No stack, no model, no paid call, no key read.** Nothing merged; the branch pushed
after each commit.

## FR-1 -- the entry's line

- [x] T001 `quality/cycle.toml [gallery] entry_mean_pct = 84.0`, its why beside it (the founder, 2026-11-01).
- [x] T002 `cycle.load_config` reads it, refused by name when absent or not a percentage; the retired-keys message no
  longer says a flagged screen always refuses.
- [x] T003 `evals/gallery.py`: `entry_mean_line()` (cycle.toml's line, for `make gallery`), `entry_gate()` (the mean of
  three `score_pct`, exact, at or above the line), `score_gate(refuse_flagged=False)` by default; `promote(...,
  entry_mean_pct=)`; `make gallery --entry-mean` / `ENTRY_MEAN=`.
- [x] T004 A refused entry keeps the gallery's row and folder for it (`export(held=)`); a slug with none stays absent.

## FR-2 -- the flagged screens travel

- [x] T005 Provenance: `studies[<study>].score_pct`, `mean`, `flagged [{study, screen, criterion, n, audience}]` per
  accepted example; `accepted.entry_mean_pct`; `kept`.
- [x] T006 The summary line, said by `promote`: *N entries accepted on a mean of at least 84.0, M refused (names and
  means)*; `quality-accept`'s snapshot line names the slugs kept as they were.

## FR-3 -- the cycle gate stands

- [x] T007 `gate` / `last_accepted` / the baseline cut untouched; `[bar]` and `[weak]` untouched.

## FR-4 -- tests and docs

- [x] T008 `tests/test_gallery_127.py`: at, above, below the line; a flagged screen admitted; a missing score file
  refused; the provenance's new keys; the summary line; the older example kept; cycle 7's five entries on their real
  score files (Expanse 86.9 accepted; Fresco 83.9, AirCaps 83.3, Palus 83.0, Codyco 83.9 refused).
- [x] T009 Re-pinned (spec 106 / 079 tests): a flagged screen no longer refuses; the 50% fixtures pass an explicit line
  where the test is about the cycle gate; `cfg["gallery"]`.
- [x] T010 `quality/CYCLE.md` step 5, `evals/gallery.py` / `quality/cycle.py` docstrings, the Makefile's comments.
- [x] T011 `make unit` green (`set -o pipefail`).
