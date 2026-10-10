# Feature Specification: marks v11 — the window frame and Price: the subjects' words moved, and the ruler follows

**Feature Branch**: `031-window-frame-and-price` (keel-e2e-eval, off `master` at `cc37efb`, `MARKS_VERSION` 10)

**Created**: 2026-10-09

**Status**: Implemented on its branch, 2026-10-09; the sibling of keel-cloud `072-window-frame` and
`073-price`, written against keel-cloud branch `073-price` at `0925484` (stacked on 072). The
design's own names for this work were `031-window-frame` (`window-frame-design.md` §5) and `032-price`
(`price-design.md` §7); both subjects landed on one stacked keel-cloud branch, so the ruler moves once.
**The run of record (`WHY=marks:11`) is on hold by the founder**: this spec makes it ready and never
runs or proposes it.

**Input**: keel-cloud `canon/designs/window-frame-design.md` (§3.1–§3.8, the frames, E1–E3, S1/S2,
W1–W8), `canon/designs/price-design.md` (§3–§8), specs `072-window-frame` and `073-price` (spec, plan,
tasks, decisions D-1…D-11), `canon/designs/vectors/dimension-registry.yaml` and its export
`src/main/resources/keel/dimension-registry.json` (thirteen keys, 4 / 3 / 6), `DimensionRegistry.java`
(the eight invariants as the cloud enforces them), `WindowFrame.java` and `Wording.java` (E1–E3, W3,
W7, W8, W9), `RespondentQuestionsRules.java` and `ScreenResultApplier.java` (U1, the Price item, the
framed questions, B6), `Figures.java` (the brief's two commercial figures), the corpus at revision 5
(`canon/designs/measured-beliefs/corpus/`, `sim/check_corpus_r5.py`); this repository at `cc37efb` —
`instructions/{registry,corpus,context,score,brief,marks,rescore,report,run,validate,contract}.py`,
`marks.toml`, the tests and fixtures, `AGENTS.md`'s gate paragraph and spec 030's house style.

## The one sentence

**`MARKS_VERSION` goes 10 → 11 with judgement calls 50–58: the registry reader checks eight invariants
on thirteen keys (4 / 3 / 6, Price back as SHAPES with its three periods), the corpus is read at revision
5 and a revision-4 file refused by name, the windowed questions are read as code writes them (an `event`
clause on Prevalence and the gate held to E1–E3, no question text owed on a framed Frequency, C7 and R8
retired), Price is code's on both sides, W7 / W9 / U1 and — where the corpus names them — W3 / W8 are
faults of `option_validity`, the wording rules S1 / W1 / W2 / W5 / W6 are reported per question and never
marked, the brief's two commercial figures are keel-cloud's own shapes, and `rescore.py` refuses every
bundle below 11.**

## What this spec does not do

- It writes no instruction, no registry entry and no corpus entry: keel-cloud 072 / 073 do all three.
- It does not run the run of record (`WHY=marks:11`). **It is on hold by the founder.** `DRY=1` is the
  only run this spec makes, and it spends nothing.
- It touches neither `why.py`'s five events nor `models.py` nor the journey evals nor keel-cloud.
- It does not mark a wording rule the subject itself only instructs (W1, W2, W4, W5, W6, S1, S2):
  `window-frame-design.md` §3.6 and §3.7 say *counted and reported, not refused*; a mark the product
  does not enforce would be the ruler inventing a rule.

## What changes, stated first

| Where | v10 | v11 |
|---|---|---|
| `registry.py` invariant 1 | 12 keys, 4 / 3 / 5 | **13 keys, 4 / 3 / 6** |
| invariant 3 | parts 4 / 3 / 5 | parts **4 / 3 / 6**; `PRIMARY` asks 3 / 3 / 4 after the gate, `COMMERCIAL_B2B` 6 |
| invariant 5 | 4–6 codes, bins | + a `price_range` entry's `periods` are exactly `month · year · one_off` (`PriceLadder.PERIODS`) |
| controls | `branch_pick_number` | `branch_pick_amounts` (Existing sacrifice), `price_ladder` (Price), founder `price_range` |
| `RESPONDENT_ESCAPES` | … | + `would_not_pay` (code appends it to every Price item) |
| `corpus.py` | `REVISION = 4` | **`REVISION = 5`**; an r4 file refused by name; Price's answer `{low, high, period, currency}` or `unsure`; Existing sacrifice `units` (money · hours · count) on the founder's kinds and the plan row; picks `{currency, amounts: [{kind, value?, unit?}]}`; Price's plan row the ladder's five bands around the founder's low plus `would_not_pay`, checked |
| calibrated set | 10 B2C / 12 B2B | **11 B2C / 13 B2B** (read, never typed) |
| `option_validity`, calibration | C7 (Prevalence names the window) | C7 **retired**; Prevalence owes `event` (E1–E3); Frequency on a framed window owes no text; Price owes no options (C2) and no text; W7, W9; U1 on every Existing sacrifice kind but `none`; W3 / W8 where the corpus names the idea / the offer |
| `option_validity`, respondent | — (R8 was the aggregate's) | the gate owes `event` (E1–E3); framed Frequency owes no text; Price owes nothing; W7, W9; U1 on every Existing sacrifice distractor; W3 on part 2 and the reveal, W8 on part 3 / the decision-maker's link, where named |
| `no_leak` | question stems | + the `event` clause (Prevalence, the gate); code-written items (Price; framed Frequency's text) are never swept; sweep B reads a founder price's `low` / `high` |
| reported, never marked | — | **per question**: words, W1 (> 20, or > 25 with a scene), W2 (*do you think / believe*, founder side), W6 (second person, founder side), S1 (scene, then question), W5 (an option over 8 words) |
| `brief.py` / `context.py` | `£165 per three months` (call 42) | Existing sacrifice's observed figure is `Figures.cost`'s (*a median £22 over three months*, hours apart); Price's is `Figures.price`'s (*5 of 8 said it would be worth £5 a month or more*); four marks, unchanged |
| `marks.py` | `MARKS_VERSION = 10`, calls to 49 | **`= 11`**; calls 50–58 |
| `marks.toml` | v10 header | v11 header, *run of record: none yet* |
| `rescore.py` | refuses < 10 | refuses **< 11** by name |
| `AGENTS.md`, `README.md` | v10 gate | v11: *no run of record until `WHY=marks:11` is spent*; on hold by the founder |

Judgement calls (appended to `marks.py`, numbered on from 49):

- **50. v11: the registry is thirteen.** Invariants 1, 3 and 5 restated: thirteen keys, 4 / 3 / 6;
  `commercial.price` at commercial order 2, SHAPES, not `b2b_only` (asked of whoever pays), founder
  control `price_range` whose `periods` are exactly `month · year · one_off`, respondent control
  `price_ladder`, `ordinal_band`; Existing sacrifice's respondent control `branch_pick_amounts`; Ability
  to pay's codes `existing_line · new_line_signed_off · taken_from_other_spend · no_budget`. The nine
  deal-breakers and the `b2b_only` pair do not move. (keel-cloud 073, registry decision 15.)
- **51. v11: corpus revision 5, read from keel-cloud's canon only.** `load()` refuses a directory
  holding any file at a revision other than 5, naming a revision-4 file as v10's. The founder's Price is
  `{low, high, period, currency}` (low 1 to under 10,000, high not below it, a period of the three, the
  market's currency) or `unsure` (Mulch Run: LEFT_OUT); Existing sacrifice's kinds carry units; Price's
  plan row is the ladder's five bands around the founder's low plus `would_not_pay` — the eval recomputes
  it (`PriceLadder.bands`, mirrored) and refuses a row that disagrees.
- **52. v11: the window is code's.** `option_validity` reads a Prevalence calibration entry's and the
  gate's **`event`** and holds it to E1–E3 as `WindowFrame.fault` does (no digit, number word or time
  word; one clause of at most 25 words, no `?`, no sentence break; not opening with the frame's words);
  a missing `event` is E2. Frequency on a window of more than one unit owes no question text, and a text
  the model wrote anyway is ignored, never a fault (keel-cloud D-7); on a one-unit window it keeps its
  question. C7 and R8 are retired from every check; `RecallWindow.said` / `is_named_in` are deleted with
  them.
- **53. v11: Price is code's on both sides.** Its calibration entry owes its key and nothing else
  (options are a C2 fault; text is ignored); its respondent item owes its key and nothing else (what a
  model writes there is not read). Both count once in `dimension_coverage` and `option_validity`;
  neither is ever swept by `no_leak` (no model text exists to sweep).
- **54. v11: the money, the hint and the unit are structural.** W9 (a currency symbol, an ISO 4217
  code in capitals, or an amount with a currency word — `Wording.money`, mirrored) in any model-written
  question, event, option label or belief phrase; W7 (*tick / select / choose all|every*, *pick all*,
  *all that apply(ies)* — `Wording.tickAll`) in a question; U1 (an Existing sacrifice founder option
  but `none` without `unit` money · hours · count; a respondent distractor without its `units[i]`) —
  each an `option_validity` fault on the screen it is found on.
- **55. v11: one name for the idea, one for the offer — held only to a name the corpus records.** W3:
  every SOLUTION calibration question, every part-2 item and the reveal carry
  `solution_mechanism.short_name` verbatim; W8: every COMMERCIAL calibration question and every part-3 /
  decision-maker item (Existing sacrifice and Price aside) carry `interpretations.offer_name` verbatim —
  `Wording.carries`, mirrored (case, accents, apostrophes, punctuation and a leading article free).
  **Revision 5 records neither name**, so on r5 both are held to none, exactly as keel-cloud holds a card
  confirmed before 072 to none, and the case meta says so; the job is handed `null` and the validator
  the same. A name the corpus gains later is read without a code change.
- **56. v11: the wording rules are reported, never marked.** Per question and item: its words; W1
  (more than 20, or more than 25 where a scene sentence comes first); W2 (*do you think* / *do you
  believe*, founder side); W6 (*you / your* in a founder question); S1 (a scene sentence, then the
  question — reported where the question is one sentence over 20 words with a clause in front); W5 (an
  option over 8 words). Totals carry the counts; the report renders them; `judge()` reads none of them.
  S2 and W4 need a name or a jargon list the corpus does not carry and are left to the register page.
- **57. v11: the brief's commercial figures are keel-cloud's.** Existing sacrifice's `observed` is
  `Figures.cost`'s shape with no hourly rate (the corpus records none): *a median £22 over three
  months*, hours apart (*; 11 hours*); Price's is `Figures.price`'s, *{inside} of {n} said it would be
  worth {floor} {period} or more*. Call 42's `£… per three months` is superseded. `brief_paragraphs`
  stays four per-case marks; B6 (*will pay / will buy*) is the aggregate's rule, counted by
  `rule_refusal_rate` and, refused twice, scored as a fault on every mark (call 41).
- **58. v11: `rescore.py` refuses every bundle below 11** by name: a v10 bundle answered without Price,
  without units and with the window in the model's own words, so a v11 number for it would be fiction.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — The ruler reads the thirteen-key registry and refuses the twelve (Priority: P1)

`contract.read(export)` on keel-cloud 073's export loads a registry of thirteen that passes eight
invariants; the v10 slice (twelve keys) is refused naming invariant 1; a slice whose Price `periods`
lack `one_off` is refused naming invariant 5; every other broken fixture is refused by its own number.

**Independent Test**: `tests/test_instruction_registry.py` on `tests/fixtures/registry/slice.yaml`
(regenerated at thirteen from keel-cloud 073's `dimension-registry.json`) and
`tests/fixtures/registry/broken/{1…8}-*.yaml` plus `5-price-periods.yaml`.

### User Story 2 — The corpus is read at revision 5 (Priority: P1)

`corpus.load(keel_cloud)` reads keel-cloud 073's seven r5 entries: 01–04 with eleven calibrated keys,
05–07 with thirteen; every founder price on the ladder in its market's currency (Mulch Run's `unsure`);
every Price plan row the ladder's recomputed codes; every Existing sacrifice pick in amounts whose kinds
are on the row and whose units are the row's. An r4 file refuses by name.

**Independent Test**: `tests/test_corpus_r5_shape.py` (from `test_corpus_r4_shape.py`), skipping by
name when the configured keel-cloud is not at revision 5; `tests/test_instruction_corpus_r5.py` on the
two fixtures (`09-fixture-r5.yaml`, `10-fixture-r5-b2b.yaml`).

### User Story 3 — The scorers read the new shapes (Priority: P1)

`calibration_checks` and `respondent_checks` accept a Prevalence / gate `event` that E1–E3 accept and
fault each of the three; accept a framed Frequency with no text; fault Price options; fault W7, W9 and
U1; fault a missing short name / offer name only where one is recorded. `no_leak` sweeps the `event`
and never a code-written item. The wording report counts W1 / W2 / W5 / W6 / S1 per question and
`judge()` never reads it.

**Independent Test**: `tests/test_instruction_score.py`, `tests/test_instruction_window_frame.py` (new),
`tests/test_instruction_leak.py`.

### User Story 4 — DRY against keel-cloud 073, and v10 bundles refused (Priority: P1)

`make instruction-eval DRY=1 MODELS=exported` against the 073 worktree (`stack.toml` pointed at it for
the run and reverted) measures `compare_correctness` 1.00 and prints every code mark's denominator, read
off the registry; `rescore.py` on a v10 scorecard says in one line why it cannot be re-scored.

### Edge Cases

- A Prevalence entry that carries `question` and no `event`: E2 (the frame needs the clause).
- A Frequency entry on *the last shift* (a one-unit window) with no question: a fault, as today.
- A respondent Price item a model filled with options: not read, not a fault (keel-cloud reads none).
- An Existing sacrifice founder option `none` without a unit: valid (the fixed none has none).
- A B2C entry with an `hours` kind: reported as hours in the brief's figure, never priced.
- A corpus entry whose Price row disagrees with the recomputed ladder: a refusal naming both.

## Requirements *(mandatory)*

- **FR-001** `registry.py`: `PER_VECTOR` 4 / 3 / 6, `PER_PART` {1: 4, 2: 3, 3: 6}; `PRICE_PERIODS`;
  `PRICE_FOUNDER_CONTROL`, `CODE_WRITTEN_RESPONDENT_CONTROLS = ("price_ladder",)`; `would_not_pay`
  among `RESPONDENT_ESCAPES`; invariant 5's periods; `RecallWindow.said` / `is_named_in` deleted; the
  docstring at thirteen.
- **FR-002** `corpus.py`: `REVISION = 5`; an r4 file refused by name; the Price, units and amounts
  checks of call 51; `price_ladder_codes(low)` mirroring `PriceLadder.bands`.
- **FR-003** `score.py`: calls 52–56 in `calibration_checks` / `respondent_checks` / the sweeps; a
  `wording` module (`instructions/wording.py`) mirroring `WindowFrame.fault`, `Wording.money`,
  `Wording.tickAll`, `Wording.carries` and counting the reported rules.
- **FR-004** `context.py`: the SOLUTION interpretation and the respondents' mechanism carry
  `short_name` (the corpus's, else `null`); the COMMERCIAL interpretation is keel-cloud's persona map
  with `offer_name`; Existing sacrifice's and Price's `observed` are keel-cloud's figures (call 57).
  The validator's batch carries `offer_name` and the mechanism with `short_name` as the job had them.
- **FR-005** `marks.py` calls 50–58, `MARKS_VERSION = 11`; `marks.toml` v11 header (*run of record:
  none yet*); `rescore.py` refuses < 11; `report.py` renders the wording counts.
- **FR-006** `run.py`'s dry run prints every code mark's denominator, Price and the framed items
  included, and the names W3 / W8 are held to.
- **FR-007** Tests and fixtures as the stories; `make unit` green.
- **FR-008** `AGENTS.md` and `README.md` gate text at v11; the Makefile's example list gains
  `WHY=marks:11`.

## Success Criteria *(mandatory)*

- **SC-001** `make unit` green; `make instruction-eval DRY=1 MODELS=exported` against keel-cloud 073
  measures `compare_correctness` 1.00 and writes every code mark's denominator.
- **SC-002** `rescore.py` refuses a v10 bundle by name.
- **SC-003** No source file names C7 or R8 as a live check, `branch_pick_number`, or Ability to pay's
  old codes, outside history.
