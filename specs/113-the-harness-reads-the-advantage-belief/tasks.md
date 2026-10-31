# Tasks 113 -- The harness reads keel-cloud 173: the advantage belief in one sentence, the occasion in the question

Branch `113-the-harness-reads-the-advantage-belief` (worktree `wt/keel-e2e-eval-113`, its own `make venv`), off master
`ffbddfe` (100's docs; 4,480 / 1 / 56 against keel-cloud-docs `1acc3791`). Built by Claude on 2026-10-30. Read only:
keel-cloud-docs master `1acc3791` (173 merged: `ScaleFour`, `BeliefSentence.benefit`, `SpokenCap.held`, `OccasionNoun`,
`VectorCorpusFixture.spec173Reads`, `src/main/resources/keel/dimension-registry.json`, 173's tasks.md -- its
*keel-e2e-eval pins owed* is the checklist below), keel-web master `98607db` (145). **No stack, no model, no paid call,
no screen run.** Nothing merged into master; the branch pushed after every commit, never force-pushed.

| Commit | What |
|---|---|
| `491cf4d` | FR-1: `corpus.spec173_reads`, `engine_belief`, the belief / drift mirror; the journey's belief checks read through the rule |
| `c0148f9` | FR-2: `ScaleFour`'s 173 question in `vectors_script`; items stored before 173 read in 159's frame |
| `6ccb172` | FR-3: the spoken mirror quotes 173's frame |
| `4811d75` | FR-4: the registry slice; the founder-lists screen's 173 mark |
| `0bfe33f` | FR-5: `tests/test_advantage_belief_113.py` (62) |
| the docs commit | this file and `AGENTS.md`'s spec-113 paragraph |

## Unit (the gate)

| | passed | failed | skipped |
|---|---|---|---|
| master `ffbddfe` against keel-cloud-docs `1acc3791`, keel-web `98607db` (this worktree, before any change; 100's tasks.md records the same) | 4,480 | 1 | 56 |
| **branch at `0bfe33f` (the last code; the docs commit adds none), keel-cloud-docs `1acc3791`, keel-web `98607db`** | **4,543** | **0** | **56** |

+63 passed: `tests/test_advantage_belief_113.py`'s 62 and master's one failure,
`test_controls_089.py::test_the_question_is_scale_fours_and_the_plain_frame_past_the_cap`, now green; none removed
(4,481 + 62 = 4,543). A first baseline run here showed nine more failures: they were this builder's edits landing
mid-run (the files changed under the collection), and all nine pass on master's and the branch's code alike.
keel-cloud 174 had not merged into keel-cloud-docs master by the final gate.

## The checklist (keel-cloud 173's *keel-e2e-eval pins that must move*)

- [x] T001 **The belief mirror** (FR-1). `instructions/corpus.py`: `ADVANTAGE_BELIEF_TEMPLATE` (*For most, their last
  {occasion} would have gone better with it: {value}.*), `advantage_benefit` (`BeliefSentence.benefit`: the first
  benefit whole, stripped, a typed full stop dropped, `lower`'s leading capital dropped unless the second letter is a
  capital), `advantage_belief` (*the last time* with no noun, `OccasionNoun.fill`), `ADVANTAGE_DRIFT_TEMPLATE` /
  `advantage_drift_clause` (*you said it would have gone better: {founder} · {observed} of {n} said better, {a_lot} of
  them a lot*, `{founder}` the sentence's `{value}`, as `Compare` fills it), and **`spec173_reads`**, the cloud's
  `VectorCorpusFixture.spec173Reads` (*given them X* -> *X*; *For most, it would have given them X on their last O.* ->
  *For most, their last O would have gone better with it: X.*; *... X the last time.* -> *For most, the last time ...*;
  anything else as it is). `engine_belief(entry, key)` is the recorded sentence, Relative advantage's read through it.
  The module docstring (`:21`) and `instructions/marks.py` (`:139`, a paragraph before revision 19's) say so; revision
  18's account is history and stays as written.
- [x] T002 **The journey reads the record through the rule** (FR-1, `evals/corpus_scenario.py`): the Keel-will-test box
  (`:1978`) and the review rows (`:2048`) compare the wire with `corpus_mod.engine_belief`, not the raw
  `belief_sentence` -- without it every strict journey (S-005, S-006, S-007) would fail Relative advantage on 173's words.
- [x] T003 **`tests/test_corpus_r19.py:260-262`** stands for the r19 record (152's words asserted as recorded) and now
  also reads it through `spec173_reads` (*For most, their last ... would have gone better with it: ...*, the phrase
  inside it). The record is not rewritten; no corpus revision.
- [x] T004 **The question mirror** (FR-2, `harness/vectors_script.py`): `BENEFIT_FRAME` is 173's *have made your last
  {occasion} go better for you, or not?*, filled by `benefit_frame` through `fill_occasion` (`OccasionNoun.fill`
  ported); `benefit_question` is *Would {idea} {frame}* (*the idea* with no name), past 20 words `benefit_shortened` --
  *Would it have made your last {occasion} go better for you, or not?* -- never 159's *Would {name} have made it go
  better ...*. Kept to read what was stored before: `BENEFIT_FRAME_159` (`ScaleFour.FRAME_159`), `BENEFIT_FRAME_085`
  (`OLD_FRAME`), `BENEFIT_PLAIN_159` (`SpokenCap.PLAIN`), `benefit_question_159`, `benefit_held_with_its_occasion`
  (`heldWithItsOccasion`), `served_benefit_question` (`SpokenCap.held`'s Relative advantage step: 085 -> 159's words,
  a 173 stem past the cap said *it* with its occasion, an old one past the cap 159's plain frame, named where it fits;
  every other stem as stored) and `benefit_frame_of` (`"173"` / `"159"` / `"085"`).
- [x] T005 **`tests/test_controls_089.py:231-240`** re-pinned with why (the one failure on master): `FRAME` and
  `FRAME_159` read off `ScaleFour.java`; the named pin; *refill requests filed for you* on *shift on the phones* is now
  20 words and keeps its name, one longer name gives *Would it have made your last shift on the phones ...*;
  `benefit_question("", "")` is *Would the idea have made the last time go better for you, or not?*. The test's name is
  kept (*..._the_plain_frame_past_the_cap*) though no plain frame is left past the cap -- renaming it would hide the
  re-pin from 100's tasks.md, which names it.
- [x] T006 **`tests/test_vectors_journey.py:313-317`**: the payroll pin in 173's frame; the refill pin keeps its name at 20.
- [x] T007 **The idea-name hold** (`corpus_scenario._hold_the_idea_name`): its docstring says 173's question; a fault
  carries `frame` (`benefit_frame_of` of what the page served), so a stale cloud reads *159* at a glance.
- [x] T008 **The spoken mirror** (FR-3): `instructions/spoken.py:13` (S1's note); `tests/test_instruction_spoken.py:112-121`
  (the 21-word stem *Would a key tag that beeps loudly have made your last busy morning before work go better ...*, an S1
  fault; its short form *Would it have made your last busy morning before work go better for you, or not?* keeps the
  occasion); `evals/interviewer_leg.py:1610` (`_question_words`' example) and `evals/test_s006_paidly.py:20` quote
  173's frame. `evals/corpus_scenario.py:3851` of the brief is `:4002` on this master (the `_hold_the_idea_name`
  docstring, T007).
- [x] T009 **The registry slice** (FR-4, `tests/fixtures/registry/slice.yaml`): `belief_template` (`:264`) and the
  respondent guidance's quoted frame (`:275`, *'Would' your idea, by its short name, 'have made your last {occasion} go
  better for you, or not?'*) are the export's; the header says so. The slice's shorter prose after the frame is its own
  (spec 040 T002) and was not re-exported.
- [x] T010 **The drift clause** (FR-4): no harness code expected a Relative advantage drift clause (`compare` marks
  status and drift codes, never the clause's words; the sample and compare fixtures are older recordings). The expected
  clause is `corpus.advantage_drift_clause`, pinned to the export's `drift_template`.
- [x] T011 **The founder-lists screen's 173 mark** (FR-4, `instructions/screen_entries.py`, `instructions/run.py`, 112's
  `steps_mark` pattern): `backtest_calibration_cases` gives a named back-test entry's Relative advantage redraft
  `meta["benefits"]` = `{mark: "173", dimension, typed}` (the walk's typed Answer split on *; *); `benefits_mark` holds
  the first turn: COMPLETED, one `solution.relative_advantage` question, one row per typed benefit in the typed order --
  more rows is *never split and none added*, fewer *missing or merged* -- each row the typed benefit as typed (case and
  end punctuation aside; past `BENEFIT_MAX_WORDS` = 9, the registry's `saves.max_words`, its own words in order with
  some left out, never a word not typed), no `suggested` row (173 T009: Keel adds none). `benefits_row_of` and
  `run._score_probe` mark it (`state.probes`, the diff's `probe`, the console's *173 held*). 10-palus's case
  `K=10-palus/CALIBRATION_SOLUTION/RELATIVE_ADVANTAGE`, Answer *Higher yield without hiring for treasury*, expects one row.
- [x] T012 **Tests** (FR-5, `tests/test_advantage_belief_113.py`, 62): the two templates against the export; the belief
  on 10-palus / 21-codyco / 13-aircaps, *time*, none, an acronym, a typed full stop; the drift clause; the one rule (six
  shapes) and the cloud's reader's own regex and sentences; the golden seven's record unchanged and read as the mirror
  composes it from the first saved benefit; the journey wired; the frames against `ScaleFour.java`; the question named,
  no noun, no name, at and over the cap, the longest eight-word occasion; the golden seven's questions; held with its
  occasion; five stored items served; an old one past the cap; the gallery's Fresco question read in 159's frame; the
  read-aloud words; the slice; the limit; the 173 mark held and each fault; 10-palus's screen case; the run marking it.
- [x] **Gallery fixtures stay** (older recordings): `expected-interview-fresco.json` (*made things better*, 085's) and
  `20261022T164045Z-backtest-08-fresco/` are untouched; the test reads Fresco's recorded question in 159's frame.
- [x] **`harness/interviewer_fake.py`**: none moves (173's list: the follow-up rung and the heading).
- [x] **`MARKS_VERSION` 24 stands**, no `PRICE_VERSION` / contract pin moves: no mark scores a belief sentence or the
  stem's words (`S1` counts them; every composed stem stays within 20), and the 173 mark is a screen probe, not a
  scorecard mark.
- [ ] `make instruction-screen HOST=claude K=10-palus/CALIBRATION_SOLUTION N=3 WHY=instruction:173`: **not run** -- paid,
  the coordinator's. (`.../RELATIVE_ADVANTAGE` names the one redraft, 3 calls at N=3.)

## Where the spec and the code differ (the code's patterns followed)

- **`corpus_scenario.py:3851`** in the spec is `:4002` on this master (the code moved since 173's tasks.md was read at
  `4b98565`); the line that quotes 159's frame is `_hold_the_idea_name`'s docstring.
- **`instructions/corpus.py:21` / `marks.py:139`** are revision 18's account (*For most, it would have {value} ...*):
  history, kept as written; the 173 reading is a new paragraph before each, as every revision's is.
- **The 173 mark is its own row** (`meta["benefits"]`, `benefits_mark`, mark `"173"`) beside 171's `meta["steps"]`, not
  a generalised one: 112's tests pin `"steps" in meta` to Adoption friction alone, and the two acceptances share nothing
  but the first turn.
- **The grammar check** beside the cap (`StrangerGrammar`) is not mirrored in `served_benefit_question`, as before 173
  (112 says the same for the adoption frame).

## What the spec did not foresee

1. **The journeys compared the raw record with the wire.** `corpus_scenario` held the Keel-will-test box and the review
   rows to the corpus's `belief_sentence`; with 173's words served and r19 unchanged, every strict journey would have
   failed Relative advantage. The spec named the r19 test only; the one rule had to be read where the journeys compare
   (T002).
2. **No harness code composed the drift clause**, so *the expected drift clauses* had nothing to move: the mirror and its
   pin to the export are new (T010).
3. **At 173's frame the old *long* pin fits.** *Would refill requests filed for you have made your last shift on the
   phones go better for you, or not?* is 20 words (159's was 22, the plain frame's example); the over-cap pin needed a
   longer name.
4. **The slice's respondent guidance** was never the export's whole text (spec 040's hand-sized slice); only its quoted
   frame is held to the export.
5. **No 173 failure came from keel-web 145** (merged since 100) or any other spec: the one failure on master was 173's
   `ScaleFour.FRAME`, fixed here.
