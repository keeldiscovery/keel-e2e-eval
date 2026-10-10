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
- [x] T011 `make unit` green: **1680 passed, 75 skipped** (2026-10-09; `stack.toml` pointed at the 073 worktree by absolute path, the three other siblings at their absolute checkouts; the skips are the suite's existing named skips -- none is the canon-not-at-r5 skip).
- [x] T012 `make instruction-eval DRY=1 MODELS=exported` against the 073 worktree (`0925484`; stack.toml pointed and reverted), 2026-10-09, bundle `runs/20261010T012102Z-instructions`: contract exported, `MODELS=exported` accepted (Sonnet 5.5 / Haiku 4.5), **405 cases at N=3** (135 at N=1: 21 interpretation, 21 calibration, 21 respondent, 65 interpret, 7 brief) + 7 COMPARE rows; **`compare_correctness` 104 of 104 = 1.00** (14 on each B2C entry, 16 on each B2B one). Every other mark unmeasured by design (call 13); the denominators, read off the registry: calibration **11** (B2C) / **13** (B2B) = 83 an N; respondent 11 PRIMARY (B2C), 7 PRIMARY + 6 COMMERCIAL_B2B (Paidly, Repeatline), 7 + 5 (Mulch Run, Price left out) = 82 an N (coverage and validity alike); `no_leak` sweep A 8 / 6 / 6 / 6 / 6 / 8 / 6 = 46, sweep B 10 / 9 / 9 / 9 / 11 / 12 / 11 = 71, **117 sweeps** an N (Countly's *last month* and Repeatline's *last shift* keep a model-written Frequency, so theirs are swept); W3 and W8 **held to no name** on all seven (r5 records none). Nothing called, nothing spent.
- [x] T013 `AGENTS.md`, `README.md` gate text at v11 (no run of record until `WHY=marks:11` is spent, on hold by the founder; v10 named as history, never run); the Makefile's example list gains `WHY=marks:11`.

## Discovered (for keel-cloud; recorded, not fixed here -- this repo never writes to a sibling)

- **The corpus records no `short_name` / `offer_name`.** W3 and W8 are code-checkable only against a golden name; r5 carries neither (`solution_mechanism.short_name`, `interpretations.offer_name`), so the eval holds both to none (call 55). A revision that records them -- Lullaby's are `VectorFixtures.SHORT_NAME` / `OFFER_NAME` already -- is read with no code change here.
- **`context-keys.json` omits `offer_name` on `RESPONDENT_QUESTIONS`.** `ScreenContextBuilder` puts it on every part-3 job (072 FR-006), but the exporter's key list for the screen is still `[part, link, context, market, founder_name, items, founder_options, mechanism]`, so a prompt built from the export cannot carry it. The eval follows the export (plan decision 3).
- **`ScreenContractTool.answerOf` reads no price.** A batch's `founder_values["commercial.price"].answer` (`{low, high, period, currency}`) falls through to the Lullaby fixture's £5-12, so the validator's Price item on another entry is built on Lullaby's range (the item is code's, so no rule reads it today).
- **The validator stands Lullaby's mechanism -- short name and all -- in for a calibration batch that carries none.** The eval now sends the entry's own mechanism on SOLUTION / COMMERCIAL calibration cases; a caller that does not would see W3 refusals against a name the model was never shown.

## Phase 6 — keel-cloud 073 final (`78e1118`, on `ed581f8`, which closed the four findings above)

- [x] T014 Re-read against the final branch. `ed581f8`: every r5 entry records `solution_mechanism.short_name` and `interpretations.offer_name` (additive within revision 5, so the seven sha256s moved and `marks.py`'s header carries the new ones); `context-keys.json` names `offer_name` on `RESPONDENT_QUESTIONS`; `ScreenContractTool.answerOf` reads a price; `dimension-registry.json` leads with `"version": 1`. `78e1118`: `ItemOption.none` (the interview wire; nothing here reads it) and `Market.symbolFor` returning a bare ISO code -- the figures use `Market.moneyPrefix` (`CHF ` + amount), which `context.cost_figure` / `price_figure` already write. Changes here: call 55 amended (before any run of record) -- W3 / W8 now hold to the corpus's names on all seven; `offer_name` written on part 3 only (the export lists the key, production writes it on part 3); the r5 digests; README / AGENTS / marks.toml / spec text; a canon test that every entry records both names within their word caps.
- [x] T015 `make unit` green: **1687 passed, 75 skipped** (stack.toml pointed at the 073 worktree, absolute paths, reverted before the commit).
- [x] T016 `make instruction-eval DRY=1 MODELS=exported` against `78e1118`, bundle `runs/20261010T015826Z-instructions`: contract exported, **registry version 1**; `RESPONDENT_QUESTIONS` keys end in `offer_name`; **`compare_correctness` 104 of 104 = 1.00**; every other mark unmeasured (call 13). Denominators unchanged: calibration 83, respondent 82, `no_leak` 46 + 71 = 117 an N. **W3 / W8 held to real names on all seven**: Countly *an alert on mismatched deliveries* / *a fix for delivery mismatches*; ComplianceLog *a ready-to-sign compliance report* / *a fix for the quarterly report*; Lullaby *a suggested reason for crying* / *something that helps at night*; Linerly *a guard inside the tyre* / *a fix for commuting punctures*; Paidly *payment within seven days* / *a fix for late agency payments*; Repeatline *repeat requests filed for you* / *a fix for repeat-prescription calls*; Mulch Run *mulch delivered to the job* / *a fix for supply-yard waits*. Nothing called, nothing spent.
