# Feature Specification: marks v12 — cost first: the founder estimates what the pain costs, Price and Ability to pay read against it

**Feature Branch**: `032-cost-first-price` (keel-e2e-eval, off `master` at `1b08ebd`, `MARKS_VERSION` 11)

**Created**: 2026-10-10

**Status**: Implemented on its branch, 2026-10-10; the sibling of keel-cloud `074-cost-first-price`
(branch `074-cost-first-price` at `5311217`, which merges 075), written against that branch. The design's
own name for this work is `032-cost-first-price` (`cost-first-price-design.md` §7). **The run of record
(`WHY=marks:12`) is on hold by the founder**: this spec makes it ready and never runs or proposes it.
`DRY=1` is the only run it makes, and it spends nothing.

**Input**: keel-cloud `canon/designs/cost-first-price-design.md` (§3 to §6 and its dated amendments:
§3.4 the fourth band, §5 time-only consumers), `specs/074-cost-first-price/{spec,tasks}.md` (decisions
D-1…D-14 and the corpus move table), `canon/designs/vectors/dimension-registry.yaml` (decision 16) and its
export `src/main/resources/keel/dimension-registry.json`, `DimensionRegistry.java` (the eight invariants as
the cloud enforces them), `RespondentQuestionsRules.java` (`W10`), `ScreenResultApplier.java` (the cost kinds,
the composed money questions), `Figures.java`, the corpus at revision 6
(`canon/designs/measured-beliefs/corpus/`, `sim/check_corpus_r6.py`), the inference contract
(`CONTRACT_VERSION` 7); this repository at `1b08ebd` — `instructions/{registry,corpus,context,score,brief,
marks,rescore,report,run,wording}.py`, `marks.toml`, the tests and fixtures, `AGENTS.md`'s gate paragraph,
specs 030 and 031 as house style.

## The one sentence

**`MARKS_VERSION` goes 11 → 12 with judgement calls 59–66: the registry reader checks eight invariants on
thirteen keys (4 / 3 / 6) in their cost-first shape (Existing sacrifice `cost_estimate` read by
`interval_contains_median`, Price over five periods fixed to the cost's, Ability to pay `derived` and
`b2b_link_only`), the corpus is read at revision 6 and a revision-5 file refused by name, the two code-framed
money questions owe no model text (Existing sacrifice carries its kinds with units and nothing else, Price its
key, Ability to pay is not in the calibration job at all), `W10` holds the part-3 Existing sacrifice question
to the recall words verbatim, the brief's cost and ability figures are keel-cloud's own, and `rescore.py`
refuses every bundle below 12.**

## What this spec does not do

- It writes no instruction, no registry entry and no corpus entry: keel-cloud 074 does all three.
- It does not run the run of record (`WHY=marks:12`). **It is on hold by the founder.**
- It touches neither `why.py`'s five events nor `models.py` nor the journey evals nor keel-cloud nor keel-web.
- It does not mark a number the product reports apart: the time-only count and hours, `n`, `inside`,
  `median` stay *reported*, never marked (call 3).

## What changes, stated first

| Where | v11 | v12 |
|---|---|---|
| `registry.py` invariant 3 | `b2b_only` on Ability to pay and Purchase friction | `b2b_only` on **Purchase friction alone**; `b2b_link_only` (respondent side) on **Ability to pay alone** |
| invariant 5 | a `price_range` entry's periods are `month · year · one_off` | `price_range` periods are `day · week · month · quarter · year` (`Period.wires`); a `cost` entry names those five and the modes `AMOUNT · HOURS`; `derived` on one side only (control and normalised kind), read by `cost_covers_price`, `from` the registry's keys |
| invariant 6 | numeric respondent controls: `segmented_0_to_7`, `number_with_unit` | + **`branch_pick_amounts`** (`RespondentControl.yieldsNumber`): Existing sacrifice is drawn as an interval |
| calibrated set | 11 B2C / 13 B2B | **12 B2C / 13 B2B** (Ability to pay on every persona); **answered** (the calibration job's) = calibrated less the `derived` one: **11 / 12** |
| asked | `PRIMARY` = all less `b2b_only` two; part 3 of B2B = 6 | `PRIMARY` = all less `b2b_only` and `b2b_link_only` (3 / 3 / 4 after the gate); part 3 of B2B = 6, Ability to pay among them |
| `corpus.py` | `REVISION = 5`; Price period `month · year · one_off` | **`REVISION = 6`**; an r5 file refused by name; the founder's Existing sacrifice answer `{mode, low, high, rate?, period, currency}`; Price's period the cost's; Ability to pay's answer `{ratio_low, ratio_high, band}` recomputed; `period` on every amounts pick; top-level `hourly_rate` on B2B entries; `time_only` / `time_only_hours` on a B2C Existing sacrifice standing |
| calibration job (COMMERCIAL) | Existing sacrifice owes question + options + phrases; Price its key | Existing sacrifice owes **options only** (4–6 kinds with units, no phrase read, any question ignored); Price its key; **Ability to pay is not in the job** — the denominator is the answered set |
| `option_validity`, respondent | W3 / W8 / W7 / W9 / U1 | + **W10** on the part-3 Existing sacrifice question (the recall words, verbatim) |
| `no_leak` | Price, framed Frequency never swept | + Existing sacrifice founder side owes no text, so nothing there is swept (it never was: COMMERCIAL) |
| `context.py` | `{cost_period}` unknown | the job's guidance has `{cost_period}` filled with the recall words (`Period.recallWords`); `observed` figures are keel-cloud's `Figures.cost` / `Figures.ability` |
| `compare.py` | input without a rate | the engine's input carries `hourly_rate` (B2B) |
| `marks.py` | `MARKS_VERSION = 11`, calls to 58 | **`= 12`**; calls 59–66 |
| `marks.toml`, `rescore.py`, `AGENTS.md`, `README.md` | v11 | v12 header (*run of record: none yet*); refuses **< 12**; gate text at v12 |

Judgement calls (appended to `marks.py`, numbered on from 58):

- **59. v12: the registry is thirteen, cost first.** Invariants 3, 5 and 6 restated as in the table:
  `b2b_only` on Purchase friction alone; `b2b_link_only` on exactly Ability to pay; a `price_range` entry's
  periods are the five of `Period.wires`; a `cost` entry names the five periods and the two modes; an entry
  is `derived` on both sides or neither, read by `cost_covers_price`, derived from registry keys;
  `branch_pick_amounts` yields a number so Existing sacrifice is `interval`. Calibrated 12 B2C / 13 B2B,
  answered 11 / 12, asked `PRIMARY` 4 / 3 / 4 (3 / 3 / 4 after the gate). (keel-cloud 074, registry
  decision 16.)
- **60. v12: corpus revision 6, read from keel-cloud's canon only.** `load()` refuses a directory holding
  any file at a revision other than 6, naming an r5 file as v11's. The founder's cost is `{mode, low, high,
  rate?, period, currency}` (mode `AMOUNT`, or `HOURS` with a rate above 0 on a B2B entry only; low above 0,
  high not below it; a period of the five; the market's currency) or `unsure`; Price's period is the cost's
  while both are stated; Ability to pay is recomputed by the eval (`price low ÷ cost high` to `price high ÷
  cost low`, whole percent; the band — `some_from_spend` when the range crosses 100%, else by the high end:
  under 50 `small_share`, to 100 `mostly_from_spend`, over `new_money`) and a file that disagrees is refused
  naming both; `unsure` exactly when the cost or the price is; every Existing sacrifice pick records its
  recall `period` (`week · month · quarter`); a B2B entry records `hourly_rate`; a decision-maker on the
  `COMMERCIAL_B2B` link has no story and no chip and is ANCHORED by rule (keel-cloud 075).
- **61. v12: the code-framed questions owe no model text.** keel-cloud composes Existing sacrifice's
  question (*What does it cost {a decider | the actor plural} today when {circumstance}?*) and Price's
  (*What price do you have in mind for {offer_name}?*) and renders both inputs. So on the calibration side
  Existing sacrifice owes its **options** — 4 to 6 kinds of cost, each with its `unit` money · hours · count
  (U1, the fixed *none* aside), a not-sure label refused (C3), no `belief_phrase` required or read — and any
  question the model writes is not read (never a fault, never swept, never held to W7 / W9 / W8); Price owes
  its key; Ability to pay is derived and **not in the job**, so the job's coverage and validity denominators
  are the answered set. Labels still carry W9.
- **62. v12: `W10`.** The part-3 Existing sacrifice question — on either link — carries the recall words of
  the founder's cost period verbatim (`Wording.carries`): a week or a day → *last week*; a month → *last
  month*; a quarter or a year, or no cost estimate → *the last three months*, because the amounts are
  normalised from them. The words are the corpus's: the registry's guidance names them through a
  `{cost_period}` placeholder the job is handed filled (`Period.recallWords`, mirrored). A fault of
  `option_validity` on that item.
- **63. v12: the commercial slice is read as cost first.** The respondent plan is derived from the registry
  (`b2b_link_only` keeps Ability to pay off `PRIMARY`; a left-out derived answer drops its row on the B2B
  link too, as Mulch Run's); Existing sacrifice's respondent control is a number-yielding control that still
  owes **options** (the kinds, one label each, the founder's labels plus 2–3 distractors with `units[i]`),
  never the null options of the scale and the gate.
- **64. v12: the cost figures are keel-cloud's.** Existing sacrifice's `observed` is `Figures.cost`'s shape
  per the founder's period: *a median £35 a month*, and on B2C the people who gave only time apart (*; 4 lose
  only time: median 3.7 hours a month, valued getting them back at £20 to £50 a month, about £5.45 to £13.64
  an hour*); on B2B, with no money-and-hours split in the corpus (it records only the total median), the
  total alone. Ability to pay's is `Figures.ability`: *{inside} of {n} already spend {price low} {period} or
  more*. Price's is call 57's with the founder's period. Call 57's *over three months* is superseded.
- **65. v12: the time-only are reported, not marked.** A B2C respondent who gave only time (hours or a count,
  no money, no *Nothing*, no *Something else*) is not counted as £0: the corpus's standing records `time_only`
  and `time_only_hours`, `compare_correctness` marks only `status` and `drift` as before, and the two new
  fields are reported and diffed where the engine states them.
- **66. v12: `rescore.py` refuses every bundle below 12** by name: a v11 bundle was answered with a founder
  Existing sacrifice tick list, a Price over `month · year · one_off`, Ability to pay as a model-written
  question and a recall window unnamed in the amounts question, so a v12 number for it would be fiction.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — The ruler reads the cost-first registry and refuses v11's (Priority: P1)

`contract.read(export)` on keel-cloud 074's export loads thirteen keys that pass eight invariants; the v11
slice (Price over `one_off`, Ability to pay `b2b_only`, `branch_pick_number` shapes) is refused naming
invariant 3 or 5; each other broken fixture by its own number.

**Independent Test**: `tests/test_instruction_registry.py` on `tests/fixtures/registry/slice.yaml`
(regenerated from 074's JSON) and `tests/fixtures/registry/broken/*.yaml`.

### User Story 2 — The corpus is read at revision 6 (Priority: P1)

`corpus.load(keel_cloud)` reads the seven r6 entries: eleven…twelve answered keys, Ability to pay recomputed,
every Price on the cost's period, every pick with its period; an r5 file refuses by name.

**Independent Test**: `tests/test_corpus_r6_shape.py` (from `test_corpus_r5_shape.py`, skipping by name when
the configured keel-cloud is not at revision 6), `tests/test_instruction_corpus_r6.py` on the two fixtures
(`09-fixture-r6.yaml`, `10-fixture-r6-b2b.yaml`).

### User Story 3 — The scorers read the code-framed questions (Priority: P1)

`calibration_checks` accepts an Existing sacrifice with options and no question, faults a missing unit and a
not-sure kind; `respondent_checks` faults an Existing sacrifice question without the recall words (W10) and
accepts it with them on either link; the answered set is the job's denominator; the Ability to pay respondent
item appears on the B2B link only.

**Independent Test**: `tests/test_instruction_score.py`, `tests/test_instruction_cost_first.py` (new).

### User Story 4 — DRY against keel-cloud 074, and v11 bundles refused (Priority: P1)

`make instruction-eval DRY=1 MODELS=exported` against the 074 worktree (`stack.toml` pointed at it for the
run and reverted) measures `compare_correctness` 1.00 and prints every code mark's denominator; `rescore.py`
on a v11 scorecard says in one line why it cannot be re-scored.

### Edge Cases

- A B2C entry whose cost is `unsure`: Ability to pay is `unsure`; Price keeps any period of the five.
- Mulch Run (Price `unsure`, cost stated): Ability to pay `unsure`; its respondent plan drops Price and
  Ability to pay both.
- An Existing sacrifice question a model wrote with a currency symbol: not read, not a fault; a *label* with
  one is a W9 fault.
- A calibration result that includes Ability to pay: a coverage fault (`outside the slice`).

## Requirements *(mandatory)*

- **FR-001** `registry.py`: `PER_VECTOR` 4 / 3 / 6; `B2B_ONLY` = Purchase friction; `B2B_LINK_ONLY` = Ability
  to pay; `PRICE_PERIODS` the five; the cost / derived controls; `NUMBER_YIELDING_CONTROLS`; `answered(...)`;
  `asked` less `b2b_link_only` on `PRIMARY`; the docstring at cost first.
- **FR-002** `corpus.py`: `REVISION = 6`; an r5 file refused by name; the cost, derived, period, rate and
  anchored-by-rule checks of call 60; the engine's input carries `hourly_rate`.
- **FR-003** `score.py`: calls 61–63 in `calibration_checks` / `respondent_checks`; the answered set as the
  calibration denominator; `wording.py` mirrors `Period.recallWords` and `Wording.carries` for W10.
- **FR-004** `context.py`: `{cost_period}` filled; the cost and ability figures (call 64).
- **FR-005** `marks.py` calls 59–66, `MARKS_VERSION = 12`; `marks.toml` v12 header; `rescore.py` refuses
  < 12; `report.py` / `run.py` print the new denominators.
- **FR-006** Tests and fixtures as the stories; `make unit` green.
- **FR-007** `AGENTS.md` and `README.md` gate text at v12; the Makefile's example list gains `WHY=marks:12`.

## Success Criteria *(mandatory)*

- **SC-001** `make unit` green; `make instruction-eval DRY=1 MODELS=exported` against keel-cloud 074
  measures `compare_correctness` 1.00 and writes every code mark's denominator.
- **SC-002** `rescore.py` refuses a v11 bundle by name.
- **SC-003** No source file names `branch_pick_number`, `one_off` as a live period, or Ability to pay as a
  `b2b_only` entry outside history.
