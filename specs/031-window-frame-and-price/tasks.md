# Tasks: 031-window-frame-and-price

**Input**: [spec.md](spec.md), [plan.md](plan.md); keel-cloud `073-price` at `0925484` (stacked on `072-window-frame`): its export, corpus r5 and the Java it mirrors.

## Phase 1 — Spec
- [x] T001 `spec.md`, `plan.md`, this file.

## Phase 2 — The registry reader (FR-001)
- [x] T002 `instructions/registry.py`: 4 / 3 / 6, invariant 5's periods, the Price and amounts controls, `would_not_pay`, `said` / `is_named_in` deleted, docstring.
- [x] T003 `tests/fixtures/registry/slice.yaml` regenerated from 073's `dimension-registry.json`; `broken/` re-cut, `5-price-periods.yaml` added.
- [x] T004 `tests/test_instruction_registry.py`.

## Phase 3 — The corpus at revision 5 (FR-002)
- [x] T005 `instructions/corpus.py`: `REVISION = 5`, r4 refused by name, Price / units / amounts checks, the ladder mirrored.
- [x] T006 fixtures `09-fixture-r5.yaml`, `10-fixture-r5-b2b.yaml`; `tests/test_corpus_r5_shape.py`, `tests/test_instruction_corpus_r5.py`.

## Phase 4 — The marks (FR-003 … FR-006)
- [x] T007 `instructions/wording.py` (E1–E3, W3/W8 verbatim, W7, W9, the reported counts).
- [x] T008 `score.py`: calls 52–56; `context.py`: names and figures (call 57); `validate.py`'s batch.
- [x] T009 `marks.py` calls 50–58, `MARKS_VERSION = 11`; `marks.toml`; `rescore.py` < 11; `report.py`; `run.py`'s denominators.
- [x] T010 Tests: `test_instruction_window_frame.py` (new), `test_instruction_score.py`, `test_instruction_leak.py`, `test_instruction_brief.py`, `test_instruction_marks.py`, `test_instruction_rescore.py`.

## Phase 5 — Gate and canon (FR-007, FR-008, SC-001)
- [ ] T011 `make unit` green.
- [ ] T012 `make instruction-eval DRY=1 MODELS=exported` against the 073 worktree (stack.toml pointed and reverted); every code mark's denominator recorded here.
- [ ] T013 `AGENTS.md`, `README.md` gate text at v11; the Makefile's example list.
