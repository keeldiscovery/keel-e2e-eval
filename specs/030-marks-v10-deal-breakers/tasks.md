# Tasks: 030-marks-v10-deal-breakers

**Input**: [spec.md](spec.md), [plan.md](plan.md); keel-cloud `071-deal-breakers-only` (its export and corpus r4).

## Phase 1 — Spec
- [x] T001 `spec.md`, `plan.md`, this file.

## Phase 2 — The registry reader (FR-001, FR-006)
- [x] T002 `instructions/registry.py`: constants, `Dimension.b2b_only`, invariants 1 / 2 / 3 / 6 / 8, `calibrated`, `plan_keys` per link, docstring.
- [x] T003 `tests/fixtures/registry/slice.yaml` regenerated from 071's `dimension-registry.json`; `broken/` re-cut, `3-b2b-only.yaml`, `8-can-fail.yaml`.
- [x] T004 `tests/test_instruction_registry.py`.

## Phase 3 — The corpus at revision 4 (FR-002)
- [ ] T005 `instructions/corpus.py`: `REVISION = 4`, six statuses, no fallback, calibrated set per persona, plan per link, r3 refused by name.
- [ ] T006 `tests/fixtures/corpus-r3/` deleted; `tests/test_corpus_r4_shape.py`.

## Phase 4 — The marks (FR-003, FR-004, FR-005)
- [ ] T007 `brief.py` four marks; `report.py`; `marks.py` calls 46–49, `MARKS_VERSION = 10`; `marks.toml`.
- [ ] T008 `rescore.py` refuses < 10.
- [ ] T009 Every scorer's literal count replaced by a registry/entry read.
- [ ] T010 `tests/test_instruction_compare.py`, `test_instruction_brief.py`, `test_instruction_marks.py`.

## Phase 5 — Gate and canon (FR-007, FR-008, SC-001)
- [ ] T011 `make unit` green (count here).
- [ ] T012 `make instruction-eval DRY=1 MODELS=exported` against the 071 worktree (stack.toml pointed and reverted); result here.
- [ ] T013 `AGENTS.md`, `README.md` gate text at v10.
