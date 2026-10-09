# Feature Specification: marks v10 — the ruler follows the registry to twelve, and the corpus to revision 4

**Feature Branch**: `030-marks-v10-deal-breakers` (keel-e2e-eval, off `master` at `2231395`)

**Created**: 2026-10-09

**Status**: Proposed on the founder's word of 2026-10-09 (*"go ahead and then deploy it to staging
once it is done"*); the sibling of keel-cloud `071-deal-breakers-only`, written against its branch.
The run of record (`WHY=marks:10`) spends the founder's money and runs only on his word.

**Input**: keel-cloud `canon/designs/deal-breakers-only-design.md` and spec `071-deal-breakers-only`
(the registry at twelve, 4 / 3 / 5; `asked_in_v1` gone; `b2b_only` on `commercial.ability_to_pay`
and `commercial.purchase_friction`; `Status` without `BAR_SET` / `NOT_TESTED_BY_DESIGN`; corpus
revision 4 in keel-cloud's canon); this repository at `2231395` — `instructions/registry.py`
(the seven invariants, `plan_keys`), `corpus.py` (revision 3, `STATUSES`, the fixture fallback),
`brief.py` (`no_claim_words`), `marks.py` (judgement calls 28–45, `MARKS_VERSION = 9`),
`marks.toml`, `rescore.py`, `report.py`, `contract.py`, the tests under `tests/` and the fixtures
under `tests/fixtures/registry/` and `tests/fixtures/corpus-r3/`; `AGENTS.md`'s gate paragraph.

## The one sentence

**`MARKS_VERSION` goes 9 → 10 with judgement calls 46–49: the registry reader checks eight
invariants on a twelve-key registry with a `b2b_only` pair instead of an `asked_in_v1` count, the
plan is calibrated-and-asked per link, `no_claim_words` retires with the two statuses it scored,
the corpus is read at revision 4 from keel-cloud's canon and nowhere else, every v9 bundle is
refused by name, and the denominators of `dimension_coverage`, `no_leak` and `compare_correctness`
are read off the registry, never typed.**

## What this spec does not do

- It writes no instruction file and no corpus entry — keel-cloud 071 does both. It reads them.
- It does not run the run of record. `WHY=marks:10` is the founder's event; this spec makes
  `make instruction-eval HOST=claude WHY=marks:10 MODELS=exported` ready and `DRY=1` green.
- It does not touch `model-routing.json`, `why.py`'s five events, or the journey evals.

## What changes, stated first

| Where | v9 | v10 |
|---|---|---|
| `registry.py` invariant 1 | 25 keys, 9 / 9 / 7 | 12 keys, 4 / 3 / 5 |
| invariant 2 | Prevalence, Frequency, Duration; Compatibility, Relative advantage, Effectiveness threshold; Existing sacrifice, Buyer/payer, Commitment | Prevalence, Importance, Current-solution satisfaction; Compatibility, Relative advantage, Adoption friction; Existing sacrifice, Buyer/payer, Commitment |
| invariant 3 | 23 `asked_in_v1`, parts 8 / 9 / 6 | `b2b_only` on exactly the two; parts hold 4 / 3 / 5; `PRIMARY` asks 3 / 3 / 3 after the gate, `COMMERCIAL_B2B` 5 |
| invariant 6 | numeric controls: four | one (`segmented_0_to_7`) |
| invariant 8 | — | every `DEAL_BREAKER` reaches `NOT_HOLDING_UP` |
| `plan_keys(part, founder_calibration)` | asked in V1, in part, not unsure | `plan_keys(part, founder_calibration, link, b2b)`: in part, not unsure, not `b2b_only` unless the entry is B2B; on `COMMERCIAL_B2B` the commercial part including the two |
| `FIXED_RESPONDENT_CODES`, `RESPONDENT_ESCAPES`, `NUMERIC_*_CONTROLS` | name removed dimensions and controls | the twelve's only (`nothing_yet` stays; `own_instinct`, `not_useful` go) |
| `corpus.py` | `REVISION = 3`; `STATUSES` eight; fixture fallback `tests/fixtures/corpus-r3/` | `REVISION = 4`; `STATUSES` six; **no fallback** — keel-cloud's canon or a refusal; an r3 file refuses by name |
| `founder_calibration` | 25 keys, every entry | the entry's calibrated set: 10 on B2C, 12 on B2B; a key outside it refuses |
| `brief.py` | five marks, `no_claim_words` scoped to `BAR_SET` / `NOT_TESTED_BY_DESIGN` rows | four marks; `CLAIM_SCOPED_STATUSES`, the two status phrases and `no_claim_words` deleted; `ENUM_NAMES` six statuses |
| `marks.toml` | `dimension_coverage` 25 / 23; `no_leak` 17 + 23 sweeps; `compare_correctness` 25 × 7 + 3 × 7; `brief_paragraphs` "all five" | denominators from the registry and the entry (10 or 12 calibration; 10 `PRIMARY` + 5 `COMMERCIAL_B2B` respondent on a B2B entry, 10 on B2C); `no_leak` 4 + 4 sweeps on Lullaby; `compare_correctness` 10 or 12 standings + 3 verdicts per entry; "all four" |
| `marks.py` | `MARKS_VERSION = 9`, calls to 45 | `= 10`; calls 46–49 (below) |
| `rescore.py` | refuses a v8 bundle | refuses a v8 **or v9** bundle by name (corpus r4 no longer carries what v9 scored) |
| `report.py` | five brief marks | four |
| `AGENTS.md`, `README.md` gate text | v9 run of record | v10: *no run of record until `WHY=marks:10` is spent* |

Judgement calls (appended to `marks.py`, numbered on from 45):

- **46. v10: the registry is twelve, calibrated and asked alike.** Invariants 1, 2, 3 and 8 are
  rewritten as the table says; `asked_in_v1` is not read; a registry carrying it is refused as
  unknown-shaped, not ignored. (keel-cloud 071, registry decision 14.)
- **47. v10: the plan is per link and per persona.** `dimension_coverage`'s respondent denominator
  is `plan_keys(part, founder_calibration, link, b2b)`; on a B2C entry the two `b2b_only` keys are
  not calibrated and a `founder_calibration` naming them is a refusal.
- **48. v10: `no_claim_words` retires** with `BAR_SET` and `NOT_TESTED_BY_DESIGN`; `brief_paragraphs`
  is all four or nothing. Struck through in `marks.toml`'s comment as `golden_belief_recall` is.
- **49. v10: corpus revision 4, read from keel-cloud's canon only.** The fixture fallback of
  2026-10-07 is deleted with its directory; `load()` refuses a directory holding any file at a
  revision other than 4, by entry and by key.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — The ruler reads the twelve-key registry and refuses the old one (Priority: P1)

`contract.read(export)` on keel-cloud 071's export loads a registry of twelve that passes eight
invariants; the v9 fixture (25 keys) is refused naming invariant 1; a fixture with `asked_in_v1`
is refused; a fixture whose Importance is `SHAPES` is refused naming invariant 2; a fixture whose
`b2b_only` is on three entries is refused naming invariant 3; a fixture whose Prevalence vocabulary
lacks `NOT_HOLDING_UP` is refused naming invariant 8.

**Independent Test**: `tests/test_instruction_registry.py` on `tests/fixtures/registry/slice.yaml`
(regenerated at twelve from keel-cloud 071's export) and `tests/fixtures/registry/broken/1…8-*.yaml`.

### User Story 2 — The corpus is read at revision 4, per persona (Priority: P1)

`corpus.load(keel_cloud)` reads keel-cloud 071's seven r4 entries: 01–04 (B2C) with ten
`founder_calibration` keys and `respondent_questions` 3 / 3 / 3; 05–07 (B2B) with twelve keys,
`PRIMARY` plan 3 / 3 and `COMMERCIAL_B2B` plan 5; `expected.standings` on exactly the calibrated
keys with the six status words; `expected.vector_verdicts` as keel-cloud's `GoldenCorpusTest` pins
them. An r3 file in the directory refuses by name; `tests/fixtures/corpus-r3/` no longer exists.

**Independent Test**: `tests/test_corpus_r4_shape.py` (from `test_corpus_r3_shape.py`): totals of
statuses across the seven entries as pinned by keel-cloud 071, the plan check per link, the B2B
entries' `COMMERCIAL_B2B` people on `commercial.*` only.

### User Story 3 — Every scorer's denominator is the registry's (Priority: P1)

`dimension_coverage`, `option_validity`, `no_leak`, `compare_correctness` and `brief_paragraphs`
run on `DRY=1` against keel-cloud 071's export and corpus r4 with every denominator read off the
registry and the entry: calibration 10 / 12, respondent 10 / 5 per link, `no_leak` 4 + 4 on
Lullaby, compare 10 × 1 + 3 (Lullaby) … 12 + 3 (a B2B entry). `compare_correctness` is 1.00 on
`DRY=1` (the engine is keel-cloud's; the corpus is its own test there).

**Independent Test**: `make instruction-eval DRY=1 MODELS=exported` against the 071 worktree
(`stack.toml` `[paths].keel_cloud` pointed at it for the run and reverted): every code mark
measured, `compare_correctness` 1.00, nothing unmeasured; `make unit` green.

### User Story 4 — A v9 bundle is refused, and the v10 run is ready for the founder (Priority: P2)

`rescore.py` on `runs/20261008T194906Z-instructions` says, in one line, that a v9 scorecard cannot
be re-scored at v10 because corpus r4 does not carry what it measured. `make instruction-eval
HOST=claude WHY=marks:10 MODELS=exported` is accepted by `why.py` as the full-run event and would
spend; it is not run here.

### Edge Cases

- A B2C entry whose `founder_calibration` names a `b2b_only` key: refusal naming the key (call 47).
- A B2B entry whose `COMMERCIAL_B2B` person picks on a non-commercial key: refusal, as today.
- A registry export still carrying `axes` under a numeric spec: ignored (an unknown key under
  `normalized` is not an invariant), recorded in the registry's `source` line.
- `judged_fraction` and `judge_calls` keep being reported; nothing about the judge changes.

## Requirements *(mandatory)*

- **FR-001** `instructions/registry.py`: `PER_VECTOR` 4 / 3 / 5; `DEAL_BREAKERS` the nine of the
  table; `ASKED_IN_V1` / `PER_PART` replaced by `B2B_ONLY = ("commercial.ability_to_pay",
  "commercial.purchase_friction")` and `PER_PART = {1: 4, 2: 3, 3: 5}` (entries in the part);
  `Dimension.b2b_only`; `asked_in_v1` deleted from `Dimension` and `Registry`; invariants 1, 2, 3,
  6, 8 as the table; `NUMERIC_RESPONDENT_CONTROLS = ("segmented_0_to_7",)`,
  `NUMERIC_FOUNDER_CONTROLS = ("numeric_interval",)`; `FIXED_RESPONDENT_CODES` and
  `RESPONDENT_ESCAPES` cut to the twelve's; `calibrated(b2b)`, `plan_keys(part, founder_calibration,
  link, b2b)`; the module docstring says eight invariants and twelve keys.
- **FR-002** `instructions/corpus.py`: `REVISION = 4`; `STATUSES` six; `FIXTURE_DIR` and the
  fallback branch of `load()` deleted; `Entry.b2b` (from `persona`), `Entry.calibrated_keys()`,
  `plan()` per link; `founder_calibration` checked against the calibrated set; an r3 file refuses.
- **FR-003** `instructions/brief.py`: `no_claim_words`, `CLAIM_SCOPED_STATUSES`, the two status
  phrase rows and `claim_scoped_names` deleted; `MARK_NAMES` four; `ENUM_NAMES` six statuses.
  `report.py` renders four. `marks.py` 46–49; `MARKS_VERSION = 10`. `marks.toml`: the v10 header,
  the denominators' comments, `no_claim_words` struck through, run of record *none yet*.
- **FR-004** `instructions/rescore.py`: refuses `marks_version` < 10 by name with the reason.
- **FR-005** Scorers (`coverage`, `validity`, `no_leak`, `compare`, whatever module names them):
  every literal 25 / 23 / 9 / 8 / 6 goes; counts come from `registry` and `entry`.
- **FR-006** Fixtures: `tests/fixtures/registry/slice.yaml` regenerated from keel-cloud 071's
  `dimension-registry.json` (twelve keys, Lullaby values); `broken/1-keys … 7-gate` re-cut and
  `broken/3-b2b-only.yaml`, `broken/8-can-fail.yaml` added; `tests/fixtures/corpus-r3/` deleted.
- **FR-007** Tests: `test_instruction_registry.py` (twelve; each invariant's refusal),
  `test_corpus_r4_shape.py`, `test_instruction_compare.py` (10 / 12), `test_instruction_brief.py`
  (four marks), `test_instruction_marks.py` (46–49), `test_instruction_models.py` unchanged in
  meaning; `make unit` green; the DRY run of US3 recorded in `tasks.md`.
- **FR-008** `AGENTS.md` and `README.md`: the gate paragraph at v10 — *no run of record until
  `WHY=marks:10` is spent*, the v9 run named as history; `specs/029-marks-v9-vectors/contracts/`
  untouched (history).
- **FR-009** Nothing in `why.py`, `models.py`, the journey evals or `model-routing` handling.

## Success Criteria *(mandatory)*

- **SC-001** `make unit` green; `make instruction-eval DRY=1 MODELS=exported` against keel-cloud
  071 measures every code mark with `compare_correctness` 1.00 and `dimension_coverage` 1.00.
- **SC-002** `rescore.py` refuses the v9 run of record by name.
- **SC-003** No source file names a removed status, control, rule or dimension; the v9 spec's
  contracts folder is the only place they remain.
