# Tasks: 035

- [ ] T001 spec, plan, tasks.
- [ ] T002 `instructions/corpus.py`: revision 8 only; r7 refused by name; readers for `chat/`, `feedback`
  and `verdicts/`. Test: `tests/test_instruction_corpus_r8.py`.
- [ ] T003 `instructions/compare.py`:
  - new pick shapes;
  - AT/BEYOND/SHORT and STRONGER in `diff`;
  - six-scenario cases.
  Test: `tests/test_instruction_compare_six_scenarios.py`.
- [ ] T004 `instructions/contract.py`, `instruction.py` and `validate.py`: the CALIBRATION_CHAT and
  ITEM_FEEDBACK screens and batch shapes. Test: update `tests/test_instruction_validate.py`.
- [ ] T005 `instructions/context.py`: the chat and feedback contexts, with the dependent beliefs. Test:
  `tests/test_instruction_chat_context.py`.
- [ ] T006 Fixtures in `tests/fixtures/chat/`: pass and fail for every clause of every mark.
- [ ] T007 `instructions/chat.py`: six marks. Test: `tests/test_instruction_chat_marks.py`.
- [ ] T008 Parity: `tests/test_instruction_chat_rules.py` against `screenContracts validate` (keel-cloud
  083).
- [ ] T009 `marks.py` / `marks.toml`: v15, calls 74–80, thresholds, and the calibration and respondent
  denominators read from the shrunken plans. `rescore.py` refuses < 15. Test: rescore and version tests.
- [ ] T010 AGENTS.md, README.md, Makefile at v15.
- [ ] T011 `make unit` green; `DRY=1` against keel-cloud 083 prints the denominators; compare 1.00.
- [ ] T012 (not here) the `WHY=marks:15` run of record, and the live journey's scripted chat answers.
