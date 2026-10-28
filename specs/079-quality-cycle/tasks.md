# Tasks 079 -- The quality cycle: one kick-off, a comparison, an adviser, a rerun, an acceptance that becomes the homepage

Branch `079-quality-cycle` off master `c4f169c` (078 merged), worktree `wt/eval-079` (`.git` a file). The designs of
record, read only: keel-cloud-docs `canon/designs/question-quality-rubric-2026-10-28.md` (§1 the fix locations, §5 the
ladder, §8 the homepage examples follow the baseline) and `canon/testing-pyramid.md`. `RUBRIC_VERSION` 1,
`MARKS_VERSION` 21, `REVISION` 16 unchanged. **No paid call in this build** -- no back-test, no reader, no adviser call:
the first real cycle is the coordinator's, on the founder's kick-off. Nothing merged, pushed or deployed.

| Commit | What |
|---|---|
| `df5ffb1` | FR-8 / FR-4: `quality/cycle.toml`, `quality/readers/adviser.md` |
| `9534942` | FR-6: `evals/gallery.py --scores` (063 amended), `--scope-order` |
| `2c45ab7` | FR-2 - FR-7: `quality/cycle.py` (walk, advise, accept, due), `quality/table.py`'s cycle head, the five make targets |
| `b46de8c` | `tests/test_quality_cycle_079.py` (37) and `tests/fixtures/quality/cycle/` |
| `46fcfb2` | FR-1: `quality/CYCLE.md`, AGENTS.md *The quality cycle* |
| this commit | this file |

## Unit

| | passed | failed | skipped |
|---|---|---|---|
| master `c4f169c` (re-run in this worktree, its own `.venv`) | 3,590 | 1 | 53 |
| this branch | 3,627 | 1 | 53 |

The +37 are `tests/test_quality_cycle_079.py`. **The one failure is not this branch's**:
`tests/test_report_marks.py::test_keel_clouds_facts_draw_the_corpus_overview_on_all_seven_entries` reads 48 of 49 (the
COMMERCIAL panel's lead in keel-cloud-docs' fresh `build/brief-facts/` export -- corpus revision 17's row), red on
master's tree alike; left red.

## FR-1 -- the runbook is a file

- [x] T001 `quality/CYCLE.md`: its first line says a session told *kick off the instruction set* reads it and nothing
  else; the four FR-8 questions answered from files; six steps, each with its command, its cost, what it writes and
  what the founder decides; the keel-web refresh spec's shape; the rules that do not move (the thirteen bundles of
  2026-10-24 never scored, judgement call 0).
- [x] T002 AGENTS.md *The quality cycle* points at it.

## FR-2 -- step 1, the kick-off: `make quality-walk` (paid)

- [x] T003 `ENTRIES=<ids>` or `ENTRIES=default` (`cycle.toml`), `SCOPES=` (default the three), `DOOR=keel|host`,
  `BUILD=<cloud7>`, `WHY=` (the founder's words, carried in the record), `DRY=1`.
- [x] T004 Refusals before anything runs, one sentence, exit 2: no ENTRIES; no WHY; a dirty keel-cloud checkout (a
  tracked change, or an untracked file under `src/`); DOOR=keel without `KEEL_ANTHROPIC_API_KEY` (its presence only:
  the value is never read); no `claude` CLI (the readers' door, and DOOR=host's); an entry keel-cloud has no back-test
  file for; an unknown scope or door; BUILD= not the checkout's sha. On `DRY=1` the paid-run refusals are printed as
  warnings and the plan still printed.
- [x] T005 Per entry per scope: `make down`, `make backtest ENTRY= SCOPE= DOOR=` (logged), the bundle found from the log
  (`evals.backtest.run_dir_in` / `latest_run_dir`) and checked for its scope, `make read-screens RUN=<bundle> OUT=`, the
  score file read from `score-path.txt`; a host-door walk stopped by the plan's limit rerun after it, at most three
  times (scripts/backtest-host.sh's rule); a failed walk or reading recorded, never hidden. Then `make read-table
  BASELINE=1 CYCLE=<record>` (without BASELINE when none is cut, or when the baseline refuses).
- [x] T006 The record `quality/cycles/<yyyymmdd>-<cloud7>.md` (`-2` on a second cycle of the day and build): the why,
  the shas and branch, routing and rubric versions, the reader, the bar and the weak rule held to; the head (score_pct /
  flagged_pct overall, per audience, per scope); against the baseline (verdict, moved rows); against the previous
  cycle (verdict, per-study delta); the studies (bundle, walk, score file, score_pct, flagged, cost, minutes); the weak
  rows; cost and time; the three next commands; a data block the other commands read.

## FR-3 -- step 2, the comparison

- [x] T007 `make read-table CYCLE=<record>` (`--cycle`): TABLE.md's head is three lines -- this cycle, the baseline, the
  bar -- then 078's table; with `BASELINE=1` a section *Moved since the baseline* (a mean moved by 0.25 or more, or a row
  turned weak or mended) with the *instead* lines. `BASELINE.md` records `flagged_pct` now.

## FR-4 -- step 3, the adviser: `make quality-advise` (paid)

- [x] T008 One call per weak row of the cycle's own score files, through the readers' `Reader` (the judge's argv +
  `--model claude-opus-5-5 --effort medium`, `judge_env`, recorded under `runs/<stamp>-advise-<record>/calls/`), after a
  one-word probe; refused on no CYCLE, an unknown CYCLE, a missing `claude`, a failed probe, score files at another
  rubric version.
- [x] T009 The current text at the fix location, from the keel-cloud checkout: the registry row's `founder`,
  `respondent` or `follow_up` block by audience and kind; a shared file's named section (`[adviser.sections]`) or the
  whole file; *no model writes these words* for a code or page row. The quotes' sha named, and a moved checkout said.
- [x] T010 `quality/cycles/<record>-advice.md`: per row the proposal (rung, why, the new text whole), the current text,
  *Taken: (the founder's word)*; an unreadable answer named as *No proposal*; a data block. Never applied. `DRY=1`
  prints the prompts and writes nothing; a cycle without a weak row calls nothing.

## FR-5 -- step 4, the rerun

- [x] T011 The record names the previous cycle and the baseline, both deltas; the rerun line printed in every record.

## FR-6 -- step 5, the acceptance: `make quality-accept` (free)

- [x] T012 `BASELINE.md` cut from the cycle's score files (`table.cut_baseline`), the old one under
  `quality/baselines/<cut>.md`; `QUALITY_OUT=` writes elsewhere (a rehearsal).
- [x] T013 The gallery from the cycle's bundles (found by path, else by name under `RUNS_DIR=`): a study with no bundle,
  a bundle not on this machine, an entry without a `gallery_names.toml` row set aside by name; the readers' gate
  (`gallery.score_gate`) refuses by name; one example per entry by `scope_order`; `gallery.export` into keel-web's
  `public/sample` (`OUT=` elsewhere); each slug's `cover.jpg` kept across the refresh.
- [x] T014 Printed: the equivalent `make gallery` line, the slugs refreshed / added / missing a cover / missing a row,
  the provenance file, the keel-web refresh sentence, the `git add` line. Nothing committed anywhere.

## FR-7 -- step 6, the cadence

- [x] T015 `make quality-due` (free): due on a keel-cloud commit touching the registry, an instruction file or the
  routing since the last record's build, or `[cadence] days` since it; it runs nothing.

## FR-8 / FR-9 -- everything on disk; nothing else moves

- [x] T016 Every setting in `quality/cycle.toml`, read by the commands; the records and advice committed under
  `quality/cycles/` (`README.md` there). No gate names a cycle target (a test holds `eval`, `eval-live`, `unit`,
  `sample`, `instruction-eval` and the matrix to it); `quality/` has no `test_*.py`; the journeys, the corpus, the
  noise check, the marks untouched.

## The gate

| Run | Result |
|---|---|
| `make unit` | 3,627 passed / 1 failed / 53 skipped (master 3,590 / 1 / 53; the one red is master's, above) |
| `make quality-walk DRY=1 ENTRIES=21-codyco SCOPES=PROBLEM WHY="dry"` | the plan printed (down, backtest ENTRY=21-codyco SCOPE=PROBLEM DOOR=keel, read-screens, read-table BASELINE=1 CYCLE=quality/cycles/20261028-ffadc44.md), one warning (no key in this shell), nothing run, nothing written |
| `make quality-advise DRY=1 CYCLE=tests/fixtures/quality/cycle/cycles/20261101-abcdef1.md` | one prompt (the fixture's one weak row, PROBLEM · respondent · problem.importance · item) with keel-cloud `ffadc44`'s real `problem.importance` respondent block quoted; no call |
| `make quality-accept CYCLE=<the same> RUNS_DIR=<tmp> OUT=<tmp> QUALITY_OUT=<tmp> PROVENANCE_DIR=<tmp>` (bundles from `build_runs`) | baseline cut; 08-fresco PROBLEM refused by name (1 flagged screen, 86.7% under 90%), 08-fresco COMMERCIAL refused (no score file); fresco (SOLUTION) and karsa (COMMERCIAL) built; the keel-web sentence printed |
| `make quality-walk` / `quality-advise` / `quality-accept` without their arguments | refused, exit 2 |

## What did not hold

- *ENTRIES required and a default in cycle.toml* (FR-2 vs FR-8): both kept -- ENTRIES must be said, and
  `ENTRIES=default` walks the file's list.
- *The five of the baseline* are not named anywhere (078 FR-6 leaves them to the founder): `cycle.toml` carries five
  the builder proposed (08-fresco, 10-palus, 13-aircaps, 17-expanse, 21-codyco), marked PROPOSED.
- *"The bar and the weak rule live in cycle.toml"* (judgement call 3) against 078 FR-1 (the weak rule is the rubric's,
  versioned): both homes kept, held equal, the commands refusing when they differ.
- *`make gallery` from a cycle's bundles* refuses as 063 wrote it (an entry given twice): a cycle has three studies per
  entry, so `--scope-order` picks one.
- *063 replaces a slug's folder whole*, so a plain `make gallery` drops keel-web's `cover.jpg`; `quality-accept` keeps it.
- *The keel-cloud checkout moved* during the build (`767d7e4e` -> `ffadc44`, another hand); nothing here depends on it.

## Judgement calls

- J-1 **One example per entry, the SOLUTION study first** (`[gallery] scope_order`), then PROBLEM, then COMMERCIAL.
- J-2 **A bundle with no score file is refused** by the gate (the design's §8: *a run without a passing score file*).
- J-3 **Dirty = a tracked change or an untracked file under `src/`**; untracked design notes under `canon/` do not move
  a build.
- J-4 **DRY=1 needs no WHY and no key** (as the instruction eval's dry run), and prints what a paid walk would refuse.
- J-5 **The adviser is quoted the checkout as it is**, its sha named, a moved checkout said -- the proposal is an edit
  to today's text.
- J-6 **The adviser runs at medium**, as the readers; `[adviser] effort` moves it by commit.
- J-7 **`make quality-due`** added (free): FR-7's three triggers checked from files, so the cadence is not memory either.
