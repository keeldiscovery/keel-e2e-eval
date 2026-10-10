# Tasks: 033-buyer-cost-total

**Input**: [spec.md](spec.md), [plan.md](plan.md); keel-cloud `077-buyer-cost-total` at `dc13341`.

## Phase 1 — Spec
- [x] T001 `spec.md`, `plan.md`, this file.

## Phase 2 — The registry reader (call 69)
- [x] T002 `instructions/registry.py`: `cost_total` number-yielding and code-written, a cost with a `code_rule` or another respondent control fails invariant 5, `AMOUNTS_CONTROL` / `UNITS` gone; `tests/fixtures/registry/slice.yaml` re-cut from 077's export, `broken/5-cost-kinds.yaml`; `tests/test_instruction_registry.py`.

## Phase 3 — The corpus at revision 7 (call 68)
- [x] T003 `instructions/corpus.py`: `REVISION = 7`, r6 refused by name as v12's, the one-total pick / plan row / no-kinds / no-`optionCounts` checks, `Entry.units` gone.
- [x] T004 fixtures `09-fixture-r7.yaml`, `10-fixture-r7-b2b.yaml` (with one-total picks); `tests/test_corpus_r7_shape.py`, `tests/test_instruction_corpus_r7.py`.

## Phase 4 — The marks (call 67, 70)
- [x] T005 `score.py` (Existing sacrifice: C2 on options, key alone on the respondent screen; W10 / U1 gone), `wording.py` (`recall_fault` deleted), `context.py` (time-only = B2C `HOURS` totals; no founder option set for Existing sacrifice).
- [x] T006 `marks.py` calls 67–70, `MARKS_VERSION = 13`, v13 header with the r7 digests; `marks.toml` v13 header (*run of record: none yet*); `rescore.py` refuses < 13.
- [x] T007 Tests: `test_instruction_cost_first.py`, score, brief, context, marks, rescore, window-frame, dry-run, `v9_fixtures.py`; the lullaby calibration golden re-cut (key + note).

## Phase 5 — Gate
- [x] T008 `make unit` green: **1,750 passed, 75 skipped** (`stack.toml` pointed at the 077 worktree and the three siblings by absolute path, reverted before every commit; the 75 skips are the suite's existing named skips).
- [x] T009 `make instruction-eval DRY=1 MODELS=exported` against keel-cloud 077 (`dc13341`), bundle `runs/20261010T231559Z-instructions`: 405 cases at N=3 + 7 COMPARE rows; **`compare_correctness` 108 of 108 = 1.00**; every other mark unmeasured by design; denominators read off the registry: calibration **80**, respondent **81**, `no_leak` sweep A 46 + sweep B 63 = **109** an N (v12: 116 -- the buyer's Existing sacrifice is no longer swept). Nothing called, nothing spent.
- [x] T010 `AGENTS.md`, `README.md`, Makefile example list at v13 (no run of record).

## Discovered (for keel-cloud; recorded, not fixed here -- this repo never writes to a sibling)

- **The calibration job's Existing sacrifice `respondent.guidance` still carries a literal `{cost_period}`** (the same as v12's note): `ScreenContextBuilder` fills it on respondent items only. Harmless -- the field is context.
- **`founder_options` for Price**: the eval's builder offers none after 077 for Existing sacrifice (mirroring `ScreenContextBuilder`, which now sends only `Codes.modelWritten` sets); Price's ladder codes are still sent by this repo's builder where production sends none -- context only, no mark reads it.
- Nothing else for keel-cloud: registry JSON, corpus r7 and its checker, the two instruction files and contract 8 were read as shipped.
