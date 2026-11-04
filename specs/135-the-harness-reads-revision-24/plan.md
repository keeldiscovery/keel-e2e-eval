# Plan 135 -- The harness reads corpus revision 24

Branch `spec-135` (worktree `wt/keel-e2e-eval-135`, `.git` a file), off `80771da` (the spec). Read only: keel-cloud-docs
master `0464e20f` (keel-cloud 215 merged: the fourteen gallery entries at revision 24 under
`canon/designs/measured-beliefs/backtest/`, `CONSTITUTION.md` beside them, the revision-23 records under
`src/test/resources/keel/backtest-r23/`). No stack, no model, no walk, no reader, no paid call, no key read; the unit
suite only.

## Where each FR lands

| FR | Where |
|---|---|
| FR-1 the loader and the pins | `instructions/corpus.py`: `GALLERY` (the fourteen, as keel-cloud's `VectorCorpusFixture.GALLERY`), `GALLERY_REVISION` 24, `revision_of(id)`; `_check_revision` reads 24 for a gallery entry and 23 for every other (22 to 35 and the golden seven), a gallery file at 23 and any other file at 24 refused by name. `instructions/screen_entries.py` reads through `corpus.load(..., backtest=True)` and moves by its docstring's quote alone. The pins and fixture lines of spec 134's Table 2 moved to the revision-24 words (tasks.md lists each), the run records kept as served (see the judgement calls). |
| FR-2 the scripted walk | `harness/vectors_script.py`: nothing in the walk names a row or a code by entry -- `founder_list`, `kept_items`, `kept_picked`, `offer_rows` read the entry -- so the new codes, Fresco's pick at index 0 of two with its 2 weeks, AirCaps' four conditions and Issen's pick on `speak_aloud` arrive with the data; the docstrings that quoted a revision-23 row move; `tests/test_harness_reads_r24_135.py` holds each of FR-2's facts on canon; the L32 expectation is reported, not asserted (`offer_rows` empty on all fourteen). |
| FR-3 the constitution | `quality/readers/dimensions.md` head: a pointer to `CONSTITUTION.md` (212's one-clause rule waits for 212's mirror spec); `instructions/gallery_names.toml` head (the gallery's map, the only place an entry is added) and `quality/CYCLE.md`'s gallery step: an entry enters only through the constitution's gate (section 9). |
| FR-4 the recorded Fresco run | `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/backtest.json` marked `"revision": 23`; the test that compares it to `expected-interview-fresco.json` skipped with that reason; neither file's words hand-edited. |

## Order

1. Plan; the loader (FR-1's code) and the suite read on canon at `0464e20f`.
2. The pins and fixtures that fail on revision 24, each moved to the revision-24 words with why; FR-4's mark and skip.
3. FR-2's tests; FR-3's pointers; tasks.md.

## Judgement calls

1. **A mixed folder, held by name** (keel-cloud 215's plan, call 4): `GALLERY` is a constant here as it is in keel-cloud,
   and a test holds it equal to `gallery_names.toml`'s entries, so a gallery that grows must move both.
2. **Run records are what was served on their day** (Table 2's own preface): a recorded run's `backtest.json`,
   `inputs.json`, `export/*.json`, the `runs/`, typist and cycle fixtures are not reworded; where a test reads a record
   against canon, the test is re-pinned (to the revision-23 record keel-cloud keeps, or skipped with its reason), never
   the record. The gallery's Fresco run and its pinned interview are FR-4's.
