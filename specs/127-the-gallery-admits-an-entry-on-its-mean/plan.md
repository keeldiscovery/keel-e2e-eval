# Plan 127 -- The gallery admits an entry on its mean

Branch `spec-127` (worktree `wt/keel-e2e-eval-127`), on master `a65834f` (the spec's commit `7eb3f4d` beneath it). No
stack, no model, no paid call, no key read.

## Where the gate lives

`make quality-accept` (`quality/cycle.py accept`) and `make gallery --scores` (`evals/gallery.py main`) share one path,
`evals.gallery.promote`. Today its readers' gate is `score_gate` (a study refused for a missing score file or a flagged
screen), then spec 106 FR-3's cycle gate (`gate` against `last_accepted`), then `three_studies`, then `export`.

## The change

1. **The line** (FR-1). `quality/cycle.toml [gallery] entry_mean_pct = 84.0`, checked by `cycle.load_config` (refused,
   by name, when absent or not a percentage) and read by `gallery.entry_mean_line()` for `make gallery`;
   `promote(..., entry_mean_pct=)` takes it explicitly (`accept` passes the config's; `make gallery --entry-mean`
   overrides it for one export).
2. **The entry gate** (FR-1). `gallery.entry_gate(runs, scores, line=)`: `score_gate` still refuses a study with no
   score file (and, with `--bar`, one under the bar) -- its flagged-screen refusal is off by default now; an entry whose
   three studies are each scored once is admitted when the mean of their three `score_pct` (exact, in decimals) is at or
   above the line, else refused by name, *10-palus 83.0 < 84.0*; an entry not whole is passed on to `three_studies`,
   which names why, as today.
3. **The older example stays** (FR-1). An entry refused (on its mean, or for a study unscored or missing) keeps its row
   in the index and its folder as they were (`export(held=)`); a slug with none stays absent. Rows rewritten or held are
   ordered by the map, as `gallery_order` says. A slug neither in the cycle nor refused is left out of the index, as spec
   106 left it.
4. **The provenance** (FR-2). Each accepted example's provenance row carries `studies[<study>].score_pct`, `mean` and
   `flagged: [{study, screen, criterion, n, audience}]` (one per 0 given); `accepted` carries `entry_mean_pct`; the file
   names the rows `kept` as they were.
5. **The summary** (FR-2). `promote` says *N entries accepted on a mean of at least 84.0, M refused (names and means)*
   after the gate, for both commands.
6. **The cycle gate stands** (FR-3): `gate` and `last_accepted` untouched; the baseline cut unchanged; `[bar]` and the
   weak rule untouched.
7. **Tests** (FR-4): `tests/test_gallery_127.py` on fixtures shaped like the real score files; spec 106 / 079 tests
   re-pinned only where the flagged screen now passes or the entry's line refuses a 50% fixture.
