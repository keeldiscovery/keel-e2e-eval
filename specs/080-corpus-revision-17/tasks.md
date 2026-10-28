# Tasks 080 -- The harness reads corpus revision 17 (keel-cloud 147)

Branch `080-corpus-revision-17` off eval master `fc7cad5` (079 merged, 081's spec on top), worktree `wt/eval-080` (`.git`
a file). The product, read only: keel-cloud-docs master `88bfce8d` (147 merged: corpus revision 17, contract 43
unchanged, the mirrors `src/test/resources/keel/corpus-r17/` and `backtest-r16/`, the checker
`canon/designs/measured-beliefs/sim/check_corpus_r17.py`, `build/brief-facts/` exported at 17,
`GoldenCorpusTest.PROPOSED_REVISION_17` / `PROPOSED_FROM` gone), reached through the sibling symlink beside the worktree.
No paid command was run. `REVISION` 16 -> 17; `MARKS_VERSION` 21, `RUBRIC_VERSION`, the interviewer and report marks
versions unchanged. Nothing merged, pushed or deployed.

| Commit | What |
|---|---|
| `095ef97` | FR-1: `REVISION = 17`, the notes, `_REVISION_OF[16]`, the fixtures, the refusal table, the version pins (the rename of `test_corpus_r16.py` rode here, content unchanged) |
| `9e4d7f0` | FR-2: `tests/test_corpus_r17.py`, rule D17, D16 kept as the record, the checker, the loads |
| `f86b321` | FR-3: the pins that named revision 16's 5 of 9 |
| this commit | this file |

## Unit

| | passed | failed | skipped |
|---|---|---|---|
| master `fc7cad5` as the hand-off quotes it (keel-cloud-docs before 147's merge) | 3,627 | 1 | 53 |
| master `fc7cad5` re-run here against keel-cloud-docs `88bfce8d` | 3,361 | 76 (+38 errors) | 206 |
| `f86b321` and this commit | 3,630 | 1 | 53 |

On `88bfce8d` master refuses every canon file (*revision is 17; this eval reads revision 16 only*) -- the 76 failures and
38 errors are that one refusal. After FR-1 to FR-3 one red is left, and it is **not this spec's**:
`test_quality_078::test_the_rubric_parses_into_five_criteria_with_their_anchors_as_the_design_has_them` reads the design
of record `question-quality-rubric-2026-10-28.md`, whose R2 anchors keel-cloud-docs `f7e7c333` rewrote for rubric
version 2 -- spec 081's subject, closed there. The +3 are D17's two tests and D16 kept on the record beside the moved
ones.

## FR-1 -- revision 17 -- `095ef97`

- [x] T001 `instructions/corpus.py`: `REVISION = 17`; the module's *Revision 17 read* paragraph (147, 145 FR-2's
  direction-aware Buyer and payer, the one row, no verdict moved) above revision 16's, which is kept;
  `_REVISION_OF[16]` names revision 16 as *MARKS_VERSION 21's corpus before keel-cloud 147 (02-compliancelog's Buyer and
  payer recorded PEOPLE_DISAGREE / both / 5 of 9 ...)*, so a file at 16 is refused by name as 15 is.
- [x] T002 The three fixtures (`tests/fixtures/corpus/09-fixture.yaml`, `10-fixture-b2b.yaml`,
  `tests/fixtures/backtest/99-broken.yaml`) at revision 17, their revision line alone. 068 made no r16 fixture of its
  own (it moved these three the same way), so there is no `*-r17` fixture to make.
- [x] T003 `tests/test_instruction_corpus_r11.py`'s refusal table reads *this eval reads revision 17 only* and gains
  revision 16.

## FR-2 -- rule D17 -- `9e4d7f0`

- [x] T004 `tests/test_corpus_r16.py` becomes `tests/test_corpus_r17.py` (068's way: the file is the current revision's).
  **D17**: the 35 canon entries beside keel-cloud's `corpus-r16/` and `backtest-r16/` mirrors; every leaf difference the
  revision line (16 -> 17) or, on 02-compliancelog alone, `expected.standings.commercial.buyer_payer_alignment`'s
  `status` PEOPLE_DISAGREE -> HOLDING_UP, `drift` both -> none, `inside` 5 -> 7, `outside` 4 -> 2 (147 T001: four
  fields, the spec's *status, drift, inside* plus the `outside` that follows from them); the row moved; one difference
  per entry, five on 02. A second test holds the row's `n` (9) and `optionCounts` as revision 16's and every entry's
  `expected` other than its standings (the verdicts, the decision) unmoved.
- [x] T005 **D16 kept as the record**, mirror against mirror (`corpus-r15/` + `backtest-r15/` beside `corpus-r16/` +
  `backtest-r16/`): the 112 picks, Issen's seven, the golden seven by their revision line -- revision 16's account no
  longer depends on canon being at 16.
- [x] T006 The cloud's `check_corpus_r17.py` prints OK on all 35; all 35 load at 17 (the 28 in back-test mode) and
  r16's 02-compliancelog is refused by name; rule Q, the Answer box, the rungs, the follow-up's rung, the served bar,
  the needs-input, the spoken guard, the changed screens and the register's re-run row (067 / 068) kept as they were.

## FR-3 -- the pins -- `f86b321`

- [x] T007 `instructions/marks.py`'s header: a *Corpus revision 17* paragraph above revision 16's -- the one row, no
  verdict moved, **v21 stands** (the ruler did not move, the record did; v21's *the corpus stays revision 16* is
  history), the DRY figures, the seven revision-17 files by sha256 (canon bytes at `88bfce8d`, equal to `corpus-r17/`);
  `instructions/marks.toml`'s comment names revision 17 (no key moved).
- [x] T008 The pins, listed below with why.

## FR-4 -- nothing else moves

- [x] T009 The journeys, the readers, the quality cycle, the noise check and every other golden reading untouched; the
  harness's mentions of *revision 16* in `harness/vectors_script.py` and `evals/corpus_scenario.py` name 129's moved
  Commitment picks (a revision-16 back-test header's *Changed:* line, still in every r17 back-test file) and stay.

## Every pin moved

| Pin | Was | Now | Why |
|---|---|---|---|
| `test_report_marks::test_keel_clouds_facts_draw_the_corpus_overview_on_all_seven_entries` | 48 of 49 (master's red) | 49 of 49, plus 02-compliancelog's COMMERCIAL row pinned: *Buyer and payer · Holding up · 7 of 9 the HR director had to agree, or they decided alone*, the pill *Not holding up* (the engine's Price), no Buyer and payer lead | the corpus records what the facts already drew |
| `test_instruction_brief_facts::test_keel_clouds_facts_agree_on_every_card_pilot_and_price_median_of_corpus_r12` | 100 of 101, the one named disagreement `PROPOSED_R17_CARD` (`GoldenCorpusTest.PROPOSED_REVISION_17`) | 101 of 101, no mismatch; the constant `R17_CARD` (the card `_at_145` reads) | the proposed map is gone; the card is recorded |
| `test_instruction_compare::test_keel_clouds_engine_agrees_with_corpus_r10_on_all_108_checks` | 107 of 108, the one row named | 108 of 108, no mismatch | the zero-spend compare: the engine's reading is the record's |
| `test_instruction_marks::test_the_header_names_the_seven_r16_digests_...` | r16 digests at `efdd37bf` | `..._r17_digests_...`: the seven at `88bfce8d`, *v21 stands* | the canon bytes moved |
| `test_corpus_r11_shape` (four tests) | revision 16; 02's Buyer and payer PEOPLE_DISAGREE / both; totals HOLDING_UP 58, PEOPLE_DISAGREE 18 | revision 17; HOLDING_UP / none; 59, 17 | the one row |
| `test_founder_walk_076::test_every_six_journey_entry_tests_nobody_else_...` | `REVISION == 16`; the cloud's `PROPOSED_REVISION_17` map strings | 17; the row as recorded; the cloud's `SPEC_147_ROW_FROM` / `_TO` readings, the proposed map absent | 147 removed the map |
| `REVISION == 16` beside `MARKS_VERSION == 21` (`test_follow_ups_075`, `test_founder_walk_076`, `test_recorded_path_074`, `test_study_scopes`) | 16 | 17 | FR-1 |
| `test_instruction_corpus_r11` refusal table | *reads revision 16 only* | *reads revision 17 only*, revision 16 refused by name | FR-1 |

## The DRY instruction eval

`make instruction-screen DRY=1 K=02-compliancelog` (no call, nothing spent): `compare_correctness` **15 of 15** agreed
(0 counts differ), `brief_facts` **14 of 14**, `report_overview` **7 of 7**, `spoken_form` 15 of 15; every model mark
unmeasured (`passed: false` is the dry run's, as always).

## Judgement calls

1. **`test_corpus_r16.py` renamed, not kept beside.** 068 renamed r15's; the r16 file's D16 read canon (now 17) and its
   checker (`check_corpus_r16.py`) refuses an r17 file, so it could not stay as written. D16 survives inside the r17 file
   on the cloud's two record mirrors, so revision 16's account is still held.
2. **The row's four fields.** FR-2 names *status, drift, inside*; the record moved `outside` too (5 + 4 -> 7 + 2 of n 9),
   as 147 T001 and the cloud checker's `R17_ROW` say; D17 holds all four, and nothing else.
3. **`_REVISION_OF[16]` says MARKS_VERSION 21's**: v21 (spec 078) was cut on revision 16; v20 read 16 before it. Naming
   the latest ruler that read a revision follows the table's own entries (11: *v19's and v20's*).

## What did not hold

- `make unit` is not at zero failed: the one red is spec 081's (the design's R2 anchors, above), left to 081.
