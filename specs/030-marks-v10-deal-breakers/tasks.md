# Tasks: 030-marks-v10-deal-breakers

**Input**: [spec.md](spec.md), [plan.md](plan.md); keel-cloud `071-deal-breakers-only` (its export and corpus r4).

## Phase 1 — Spec
- [x] T001 `spec.md`, `plan.md`, this file.

## Phase 2 — The registry reader (FR-001, FR-006)
- [x] T002 `instructions/registry.py`: constants, `Dimension.b2b_only`, invariants 1 / 2 / 3 / 6 / 8, `calibrated`, `plan_keys` per link, docstring.
- [x] T003 `tests/fixtures/registry/slice.yaml` regenerated from 071's `dimension-registry.json`; `broken/` re-cut, `3-b2b-only.yaml`, `8-can-fail.yaml`.
- [x] T004 `tests/test_instruction_registry.py`.

## Phase 3 — The corpus at revision 4 (FR-002)
- [x] T005 `instructions/corpus.py`: `REVISION = 4`, six statuses, no fallback, calibrated set per persona, plan per link, r3 refused by name.
- [x] T006 `tests/fixtures/corpus-r3/` deleted; `tests/test_corpus_r4_shape.py`.

## Phase 4 — The marks (FR-003, FR-004, FR-005)
- [x] T007 `brief.py` four marks; `report.py`; `marks.py` calls 46–49, `MARKS_VERSION = 10`; `marks.toml`.
- [x] T008 `rescore.py` refuses < 10.
- [x] T009 Every scorer's literal count replaced by a registry/entry read.
- [x] T010 `tests/test_instruction_compare.py`, `test_instruction_brief.py`, `test_instruction_marks.py`.

## Phase 5 — Gate and canon (FR-007, FR-008, SC-001)
- [x] T011 `make unit` green: **1597 passed, 75 skipped** (2026-10-09; `stack.toml` pointed at the 071 worktree; the skips are the suite's existing named skips -- none is the canon-not-at-r4 skip).
- [x] T012 `make instruction-eval DRY=1 MODELS=exported` against the 071 worktree (`f38ac42`; stack.toml pointed and reverted), 2026-10-09, bundle `runs/20261009T192348Z-instructions`: contract exported, `MODELS=exported` accepted (Sonnet 5.5 / Haiku 4.5), **405 cases at N=3** (135 at N=1: 21 interpretation, 21 calibration, 21 respondent, 65 interpret, 7 brief) + 7 COMPARE rows; **`compare_correctness` 97 of 97 = 1.00** (13 on each B2C entry, 15 on each B2B one). The three structural marks and the rest are unmeasured on a dry run by design (no model answer exists; call 13), so the dry run now prints the denominator each would be counted over, read off the registry: calibration 10 (B2C) / 12 (B2B); respondent 10 PRIMARY (B2C) / 7 PRIMARY + 5 COMMERCIAL_B2B (B2B); no_leak sweep A 8 (4 PROBLEM questions + 4 Part 1 items) + sweep B 10 / 12 -- 76 + 76 an N, 132 sweeps. Nothing called, nothing spent.
- [x] T013 `AGENTS.md`, `README.md` gate text at v10 (no run of record until `WHY=marks:10` is spent; v9's named as history); the Makefile's example list gains `WHY=marks:10`.
