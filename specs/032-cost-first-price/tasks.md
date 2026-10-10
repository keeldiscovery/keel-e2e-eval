# Tasks: 032-cost-first-price

**Input**: [spec.md](spec.md), [plan.md](plan.md); keel-cloud `074-cost-first-price` at `5311217`.

## Phase 1 — Spec
- [x] T001 `spec.md`, `plan.md`, this file.

## Phase 2 — The registry reader (FR-001)
- [x] T002 `instructions/registry.py`: cost-first invariants 3 / 5 / 6, answered / calibrated / asked, the controls, docstring.
- [x] T003 `tests/fixtures/registry/slice.yaml` regenerated from 074's `dimension-registry.json`; `broken/` re-cut; `tests/test_instruction_registry.py`.

## Phase 3 — The corpus at revision 6 (FR-002)
- [x] T004 `instructions/corpus.py`: `REVISION = 6`, r5 refused by name, cost / derived / period / rate / anchored checks; `compare.py` carries `hourly_rate`.
- [x] T005 fixtures `09-fixture-r6.yaml`, `10-fixture-r6-b2b.yaml`; `tests/test_corpus_r6_shape.py`, `tests/test_instruction_corpus_r6.py`.

## Phase 4 — The marks (FR-003 … FR-005)
- [ ] T006 `score.py` (calls 61–63), `wording.py` (W10), `context.py` (`{cost_period}`, figures), denominators in `run.py` / `report.py`.
- [ ] T007 `marks.py` calls 59–66, `MARKS_VERSION = 12`; `marks.toml`; `rescore.py` < 12.
- [ ] T008 Tests: `test_instruction_cost_first.py` (new), score, brief, marks, rescore, leak.

## Phase 5 — Gate and canon (FR-006, FR-007)
- [ ] T009 `make unit` green.
- [ ] T010 `make instruction-eval DRY=1 MODELS=exported` against the 074 worktree.
- [ ] T011 `AGENTS.md`, `README.md`, Makefile at v12.
