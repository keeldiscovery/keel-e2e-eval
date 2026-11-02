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
- [x] T004 A refused entry keeps the gallery's row and folder for it; a slug with none stays absent (widened by FR-5).

## FR-2 -- the flagged screens travel

- [x] T005 Provenance: `studies[<study>].score_pct`, `mean`, `flagged [{study, screen, criterion, n, audience}]` per
  accepted example; `accepted.entry_mean_pct`; `kept`.
- [x] T006 The summary line, said by `promote`: *N entries accepted on a mean of at least 84.0, M refused (names and
  means)*; `quality-accept`'s snapshot line names the slugs kept as they were.

## FR-3 -- the cycle gate stands

- [x] T007 `gate` / `last_accepted` / the baseline cut untouched; `[bar]` and `[weak]` untouched.

## FR-5 -- the gallery grows by new entries only (the coordinator's decision, 2026-11-01)

The founder's standing rule (2026-11-01): the gallery grows by new entries only, and a certified entry is never re-walked
just to stay in. So an accept on a cycle that walks some entries leaves every slug not in the cycle exactly as it is.
**This supersedes spec 106's "left out of the index"** (106 FR-1 / FR-4 rewrote `index.json` with the exported slugs
alone, so a cycle of five would have dropped the nine other certified examples from the homepage).

- [x] T012 `gallery.export`: every row already in `index.json` stays whole and in its place (`existing_rows`), its
  folder untouched; a rewritten slug is replaced in place (keel-web's `title`, `image`, `tests` kept on it); a new slug
  is appended, the new ones among themselves in `gallery_order`. `export(held=)` / `_map_order` retired with it;
  `result["kept"]` and the provenance's `kept` list the rows left as they were.
- [x] T013 `quality-accept` / `make gallery` print *kept as they were (not rewritten this cycle)*; nothing is left out
  of the index any more.
- [x] T014 Re-pinned: spec 106's `test_accept_builds_the_three_studies_records_the_score_and_holds_the_next_cycle_to_it`
  (karsa, not in the cycle, now keeps its row: *kept as they were ... karsa; left out of the index ... none*) -- the
  founder's rule supersedes 106 here. New: `test_a_cycle_of_two_entries_leaves_twelve_existing_rows_untouched` (a
  gallery of fourteen; a cycle walks fresco, refreshed in place, and palus, refused; the twelve others' rows and folders
  byte for byte as they were, in order).

## FR-4 -- tests and docs

- [x] T008 `tests/test_gallery_127.py`: at, above, below the line; a flagged screen admitted; a missing score file
  refused; the provenance's new keys; the summary line; the older example kept; cycle 7's five entries on their real
  score files (Expanse 86.9 accepted; Fresco 83.9, AirCaps 83.3, Palus 83.0, Codyco 83.9 refused).
- [x] T009 Re-pinned (spec 106 / 079 tests): a flagged screen no longer refuses; the 50% fixtures pass an explicit line
  where the test is about the cycle gate; `cfg["gallery"]`.
- [x] T010 `quality/CYCLE.md` step 5, `evals/gallery.py` / `quality/cycle.py` docstrings, the Makefile's comments.
- [x] T011 `make unit` green (`set -o pipefail`).
