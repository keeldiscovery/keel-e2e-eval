# Tasks: 035

> **Amended 2026-10-12, at implementation.** The spec was written against keel-cloud 083 at registry v2 / contract 10 /
> corpus r8 / `MARKS_VERSION` 15. It is implemented against 083 at `805688a` after 084 and 037 merged: **registry 3,
> document 18, contract 11, `InferenceCharge.VERSION` 6, V45 (18 screens), corpus r9 (additions only),
> `MARKS_VERSION` 17** (judgement calls 76-80, not 74-80). Deviations are listed at the end of this file.

- [x] T001 spec, plan, tasks.
- [x] T002 `instructions/corpus.py`: revision 8 only; r7 refused by name; readers for `chat/`, `feedback`
  and `verdicts/`. Test: `tests/test_instruction_corpus_r8.py`.
- [x] T003 `instructions/compare.py`:
  - new pick shapes;
  - AT/BEYOND/SHORT and STRONGER in `diff`;
  - six-scenario cases.
  Test: `tests/test_instruction_compare_six_scenarios.py`.
- [x] T004 `instructions/contract.py`, `instruction.py` and `validate.py`: the CALIBRATION_CHAT and
  ITEM_FEEDBACK screens and batch shapes. Test: update `tests/test_instruction_validate.py`.
- [x] T005 `instructions/context.py`: the chat and feedback contexts, with the dependent beliefs. Test:
  `tests/test_instruction_chat_context.py`.
- [x] T006 Fixtures in `tests/fixtures/chat/`: pass and fail for every clause of every mark.
- [x] T007 `instructions/chat.py`: six marks. Test: `tests/test_instruction_chat_marks.py`.
- [x] T008 (partial, deviation 3) Parity: `tests/test_instruction_chat_rules.py` against `screenContracts validate` (keel-cloud
  083).
- [x] T009 `marks.py` / `marks.toml`: v17, calls 76–80, thresholds, and the calibration and respondent
  denominators read from the shrunken plans. `rescore.py` refuses < 15. Test: rescore and version tests.
- [x] T010 AGENTS.md, README.md, Makefile at v17.
- [x] T011 `make unit` green; `DRY=1` against keel-cloud 083 prints the denominators; compare 1.00.
- [ ] T012 (not here) the `WHY=marks:17` run of record, and the live journey's scripted chat answers.

## Deviations (what was built instead of, or beside, what the spec says)

1. **Versions.** v17 (not 15), calls 76-80 (not 74-80), corpus r9 (not r8), registry 3, contract 11. `rescore.py` refuses every
   bundle below 17.
2. **Corpus.** r9 moves no entry: `corpus.REVISION` is 9 and `ENTRY_REVISION` 8. `chat/*.yaml` is 41 cases over six
   ideas; there is **no `chat/feedback.yaml`** in the corpus, so the feedback cases (and the six ideas' context,
   market, statements and idea words) are this repository's own: `instructions/chat_feedback.yaml`,
   `instructions/chat_ideas.yaml`.
3. **Parity (T008) is not possible at 083**: `screenContracts validate` takes neither chat screen. The restatements are
   proved against keel-cloud's own `ItemRulesTest` / `CalibrationChatContractTest` cases, transcribed
   (`tests/test_instruction_chat_rules.py`); `validate._SHAPE_MARKERS` lists the screens so they batch when the validator
   names them. Until then they are dropped from the batch (`validate.OWN_RULES`) and are not an unmet prerequisite.
4. **keel-cloud defect, not copied.** `CalibrationChatRules.MONEY` has no closing `\b`, so *payroll* (and *ordering*,
   *planning*) read as money and trip CC5 on any Adoption friction question that says them. The eval's `MONEY` has the
   word ending.
5. **The chat is one call.** The corpus has no reply to a follow-up, so on a case where the model asks the marks that
   read a proposal are unmeasured for that case (T012's scripted answers). `follow_up_budget` is 1.00, not 0.95 (the
   2026-10-12 brief).
6. **Six-scenarios compare** runs keel-cloud's `SixScenarioVerdictsTest` (the `compare` command refuses chat frames) and
   reads its JUnit result; a scenario is all-or-nothing, since the result does not say which row.
7. **Denominators.** The calibration and respondent denominators did not move (the pre-chat screens are still built:
   80 and 81 an N); the spec's FR-005 does not apply at 083.
