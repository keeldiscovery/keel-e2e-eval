# Tasks 110 -- The harness reads keel-cloud 170: price version 14, the gate's No, the chips, the cost frame, the screen

Branch `110-the-harness-reads-the-lock-jobs-frontier-tier` (worktree `wt/keel-e2e-eval-110`, its own `make venv`), off
master `20ac3e8` (098's docs). Built by Claude on 2026-10-30. Read only: keel-cloud-docs at `8c53497f` (170 merged; its
tasks.md's *eval pins* section is the checklist) and, by the gate run, `2edd98bf` (176 merged during the build; it moved
none of this spec's pins). **No stack, no browser beyond the unit tests' local Chromium, no model, no paid call, no
Gradle run in keel-cloud.** Nothing merged into master; the branch pushed after every commit, never force-pushed.

| Commit | What |
|---|---|
| `d4cbe12` | FR-1: `PRICE_VERSION` 13 -> 14; RESPONDENT_QUESTIONS 70 in the mirror test |
| `d11525a` | FR-2: the gate's No, the story clip's chips, S6's *I can't recall* (the record's age), `subject_led` |
| `41dd36a` | FR-3: the stranger's cost item mirrored (`harness/loss_line.py`, `vectors_script.cost_question` ...) |
| `342d9e5` | FR-4: the screen reads `RESPONDENT_PART1` for back-test entries and a respondent probe |
| the docs commit | this file and `AGENTS.md`'s spec-110 paragraph |

## Unit (the gate)

| | passed | failed | skipped |
|---|---|---|---|
| master `20ac3e8` (the brief's, 098's tasks.md), keel-cloud-docs `8c53497f` | 4,186 | 3 | 53 |
| **branch at `342d9e5` (the last code; the docs commit adds none), keel-cloud-docs `2edd98bf`** | **4,238** | **0** | **56** |

+52 passed are `tests/test_lock_frontier_110.py`'s; master's three failures are cleared -- one passes
(`test_the_mirror_is_keel_clouds_charge_table`), **two skip by name** (below), and a third test that read the same stale
record (`test_the_record_follows_registry_revision_13s_five_changes`, re-pinned to *I can't recall*) skips with them:
53 + 3 = 56. No new failure from keel-cloud 176 (merged on keel-cloud-docs master during the build).

## FR-1 -- price version 14

- [x] T001 `harness/interview_charge.py` (`PRICE_VERSION` 14, `RESPONDENT_QUESTIONS_CREDITS` 70, the module note, the
  row-fault docstring), `harness/interviewer_fake.py`, `harness/contacts_fake.py`: 14, each note naming 170.
- [x] T002 `tests/test_credits_at_begin_088.py` (14; the mirror test asserts `RESPONDENT_QUESTIONS` 70 against
  keel-cloud's `InferenceCharge`; the INTERVIEW row's `price_version` 14), `tests/test_frontier_tier_105.py` (14; the
  prose test also wants *14* and *170* beside each pin), `tests/test_interviewer_marks.py:834` (14 -- not in the spec's
  list, it pins the fake's version). The IM1 seed of -35 stays (its comment: the lock's job at 13, 70 at 14, still not
  400 -- a fault either way). `evals/test_s012_journey_through_a_host.py`'s prose and the per-job model check's comment
  name v15 / 14 (the check itself already resolves the frontier class through 105's fallback).

## FR-2 -- the gate's No, the chips, S6, `subjectLed`

- [x] T003 `evals/corpus_scenario.py`: `gate_no_faults(gate, served_gate)` (called from `_hold_the_screens`): a gate
  drawn with a question is served no `noLabel` but the want's *I didn't* (`GATE_SERVED_NO_LABELS`; a served *I didn't
  get to* is a fault named `retired`), and draws as its No the served label, else the page's own *No*
  (`gate_no_label`, `vs_screens.IV_NO`). Before, a gate served no label was not checked at all.
- [x] T004 `harness/interviewer_fake.py`: `story_escape(chips, occasion)` / `story_chip_word` mirror
  `PassageComposer.storyEscape` -- *Or say: I can't recall one particular payroll run, or I'd rather not say.*, the
  served order, one chip one, none `None` -- and `GATE_YES_OR_NO`. No harness code reads a story clip today (170's note:
  no gate or story script is in the fake); the mirror is held to keel-cloud's source and to the screen's chip words.
- [x] T005 `instructions/spoken.py`: S6 **already** read the registry's escape (`registry_escape`, since spec 065);
  module note item 2 rewritten (*I can't recall* since 170; *I don't know* 115-169; one escape on and off the chain) and
  `OFF_CHAIN_COST_ESCAPE`'s note. See *not foreseen* 1 for why master failed anyway.
- [x] T006 `instructions/wording.py`: `subject_led` mirrors `WindowFrame.subjectLed` whole (116's *you* / *your*, 129's
  subject before a present verb, 130's plural subject, 131's determiners, 170's *any* / *some*), and `gate`,
  `frequency_respondent`, `frequency_measured` frame through it -- *did any of the cash from your raise stay in ...?*,
  never *did you any of*. `harness/vectors_script._SUBJECT_LED` (the narrow mirror) gains *any* / *some*;
  `harness/qualifiers._IRREGULAR` gains 170's *ring* / *catch*. E4 measures the Palus clause at 22 words in the older
  frame (170's not-foreseen 2), asserted.

## FR-3 -- the cost item

- [x] T007 **New `harness/loss_line.py`**: `LossLine` (read, the four shapes, `past`, `after_did`,
  `without_its_clause`) with the parts of `StrangerGrammar` (`IRREGULAR`, `KEEP`, `past_of`, `second_person`,
  `third_person`), `BeliefSentence.lower`, `OccasionNoun.of`, `CostEstimate.plural` it stands on, line for line.
- [x] T008 `harness/vectors_script.py`: `cost_question` (`CommercialChain.costQuestion`'s chain branch: HOURS *spend
  on*, RATE the loss line's verb and thing else *miss*, MONEY *what did ... cost*, each give-way ladder held to 20
  words), `stranger_cost_label`, `value_box_answer_line`, `VALUE_BOX_LABELS` (*None* / *I can't recall* / *I'd rather
  not say*; codes unmoved), `value_box_escapes`, and `cost_item(entry)` (the item on the link carrying part 3).
- [x] T009 `evals/corpus_scenario.py`: on every drawn value box, `value_box_word_faults` (the chip words, a fault) and
  `cost_item_drift` (a chain entry's served question, label or spoken lines parting from `cost_item` is a **finding**,
  never a stop: the mirror is proved on the cases below, not on every entry's wording). `vectors_screens`' chip comment
  says the new words.
- [x] T010 Proved against: keel-cloud's **seventeen worked cases** (`src/test/resources/commercial-chain/*.json`,
  question, label, *None*, chips, escape -- all seventeen agree on the first port), 170's
  `CostQuestionInTheirWordsTest` cases word for word (eleven frames, five labels, four answer lines), and **the three
  entries' lines** off their back-test files: 10-palus *Last year, about how much interest did your team miss on cash
  that sat in the operating account?*, 17-expanse *Last month, about what share of the cluster's GPU hours did jobs
  reserve and never use?*, 21-codyco *Last month, about what share of the reservation calls were lost?*. The port's word
  lists are held to `LossLine.java` / `StrangerGrammar.java`.

## FR-4 -- the screen reader

- [x] T011 `instructions/context.py`: `build_respondent` hands part 1 `problem` (`problem_of`: the Prevalence clause
  the eval's walk writes, `vectors_script.event_past`) and `condition` (`condition_of`: `card_condition`), and the
  condition on the decision-maker's part 3 and on a gateless study's part 3 (`_hands_condition`, as
  `ScreenContextBuilder` 120 / 145 / 166 do); a key the builder does not write on a part is left out, as `mechanism` is.
  `DEFAULT_KEYS` gains the two, in the builder's order.
- [x] T012 `instructions/screen_entries.py`: `BACKTEST_SCREENS` gains `RESPONDENT_QUESTIONS` (part 1, cased
  `<id>/RESPONDENT_PART1/run<N>` -- the golden corpus's name; 170's tasks.md says the same); `load_probe` hands a probe
  carrying `job_context` to `load_respondent_probe` (rows: `screen`, `item`, `planted`, `verdict_words`, `keeps`,
  `first_turn`; each planted word in `problem` or `context.circumstance`; refusals by name); `respondent_probe_context`
  fills each item's registry fields and the window as `respondent_item` / `fill_window` do; `respondent_probe_mark`:
  COMPLETED, part 1, one `event` E1-E3 clean in the probe's window, **no verdict word** (whole words), **the object
  kept** (`keeps`), the framed gate and the register recorded for a reader; `mark_for` picks the mark by the plant.
- [x] T013 `instructions/run.py`: `_score` returns before scoring an extra (a back-test or probe case has no golden
  entry -- a `RESPONDENT` extra would have crashed `score_respondent` on `None`); `_score_probe` calls `mark_for`; the
  dry run's denominators read the golden cases only.
- [x] T014 Tests (`tests/test_lock_frontier_110.py`, 52): the version pins (beside 088 / 105), the gate-No read, the
  story clip and its source, S6's escape and the stale record, `subjectLed` in `wording.gate`, the cost frames, labels,
  answer lines, chips, the seventeen cases, the three entries, the screen's respondent case, the probe's reading,
  refusals and mark (held on its own expected wording; faults on a verdict, a lost object, part 2, no event, a time word,
  NEEDS_INPUT), and the run's handling. `tests/test_frontier_tier_105.py`'s back-test case-list test re-pinned with why.

## Not foreseen by the spec

1. **Master's two spoken failures were the record's age, not S6.** `instructions/spoken.py` had read the registry's
   escape since spec 065; keel-cloud's `build/spoken-corpus.txt` (a Gradle run's output, written 2026-10-30 08:28,
   before 170 merged at 20:37) still says Existing sacrifice's *I don't know* while the registry of record says *I can't
   recall*. `test_corpus_r19`'s *10 served, 9 clean* (the brief's *9 expected, 10 served*) is the same line: Lullaby's
   one item of ten, Existing sacrifice, red on S6 -- **170's doing** (it moved the registry), but nothing to re-pin: the
   counts are right. Such a record is now skipped by name (`fx.skip_a_spoken_record_before_170`, 089's pattern for
   158 / 159), and `test_a_record_written_after_170_keeps_every_rule` proves the same record with 170's one moved line
   is 109 of 109 and Lullaby 10 of 10. **Owed (the coordinator's)**: rerun `./gradlew test --tests
   '*SpokenGuidelinesCorpusTest'` in keel-cloud-docs, then the three skips run (not done here: no Gradle in another
   repo).
2. **The spec's `cost_how_line` is the founder page's line** (keel-web 134, `harness/vectors_screens.py`), untouched by
   170. The eval had **no** mirror of the stranger's cost item at all; FR-3 is a new port (T007-T008), wired as a
   finding, not an assertion.
3. **A back-test entry records no founder Prevalence clause of its own.** `problem` on its screen is the clause the
   eval's walk writes (`event_past`: *had a time when {circumstance}*), which is what a back-test walk hands keel-cloud
   too -- so 170's acceptance on 08-fresco / 10-palus / 13-aircaps / 17-expanse screens a gate written from a
   circumstance-shaped `problem`. The golden entries hand their own (`PROBLEM_CLAUSES`); the probe hands its planted one.
4. **`build_respondent` also writes `condition` on part 3** where keel-cloud does (the decision-maker's link, a
   gateless study) -- not in the spec, which named part 1; and leaves `problem` / `condition` out where keel-cloud's
   builder writes neither (before, every exported key was written `null` on every part).
5. **`_score` would have crashed** on a `RESPONDENT` extra (no golden entry): extras are now never scored, and the dry
   run's denominators count golden cases only.
6. **keel-cloud-docs moved during the build** (`8c53497f` -> `2edd98bf`, spec 176); no new failure.
7. The instruction screens 170 owes (`make instruction-screen ... K=<entry>/RESPONDENT_PART1`, `K=170-judgement-verb`,
   `WHY=instruction:170`) now build cases; they are paid and the coordinator's, not run here.
