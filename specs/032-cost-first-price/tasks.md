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
- [x] T006 `score.py` (calls 61–63), `wording.py` (W10), `context.py` (`{cost_period}`, figures), denominators in `run.py` / `report.py`.
- [x] T007 `marks.py` calls 59–66, `MARKS_VERSION = 12`; `marks.toml`; `rescore.py` < 12.
- [x] T008 Tests: `test_instruction_cost_first.py` (new), score, brief, marks, rescore, leak.

## Phase 5 — Gate and canon (FR-006, FR-007)
- [x] T009 `make unit` green: **1744 passed, 75 skipped** (2026-10-10; `stack.toml` pointed at the 074 worktree and the three other siblings by absolute path, reverted before every commit; the 75 skips are the suite's existing named skips).
- [x] T010 `make instruction-eval DRY=1 MODELS=exported` against keel-cloud 074 (`5311217`), bundle `runs/20261010T175605Z-instructions`: 405 cases at N=3 (135 at N=1) + 7 COMPARE rows; **`compare_correctness` 108 of 108 = 1.00** (15 on each B2C entry, 16 on each B2B one); every other mark unmeasured by design (call 13); denominators read off the registry: calibration **11** (B2C) / **12** (B2B) = **80** an N; respondent 11 PRIMARY (B2C), 7 + 6 COMMERCIAL_B2B (Paidly, Repeatline), 7 + 4 (Mulch Run: Price and Ability to pay left out) = **81** an N; `no_leak` sweep A 8 / 6 / 6 / 6 / 6 / 8 / 6 = 46, sweep B 10 / 9 / 9 / 9 / 11 / 12 / 10 = 70, **116** an N; W3 / W8 held to the real names on all seven. Nothing called, nothing spent.
- [x] T011 `AGENTS.md`, `README.md`, Makefile at v12 (no run of record until `WHY=marks:12` is spent, on hold by the founder).

## Discovered (for keel-cloud; recorded, not fixed here -- this repo never writes to a sibling)

- **The calibration job's copy of Existing sacrifice's `respondent.guidance` keeps the literal `{cost_period}`.** `ScreenContextBuilder` fills it on respondent items only (`RegistrySlices.filledCost`), so the COMMERCIAL calibration job is handed the placeholder in the `respondent.guidance` field. Harmless to the marks (the field is context, not a rule), but the model is shown an unfilled token; the eval mirrors the export.
- **Corpus r6 records no money-and-hours split.** `Figures.cost` on a B2B study writes *-- $108.33 in money plus 8 hours at $25 an hour*; the corpus standing carries the total median only, so the eval's B2B figure is the total alone (a shorter figure quoted inside the longer one).
- **`ScreenContractTool.answerOf` reads no `ratio_*` answer.** A batch's `founder_values` for `commercial.ability_to_pay` (a derived answer) falls through; the item is not in the job, so no rule reads it today.
