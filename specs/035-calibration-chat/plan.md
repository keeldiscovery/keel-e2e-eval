# Plan: 035

Python 3.12, pytest. The eval reads keel-cloud from the sibling checkout (083 worktree).

1. **Corpus r8 reader.** `instructions/corpus.py` reads revision 8, refuses r7 by name (as v14's), and reads
   `chat/*.yaml`, `chat/feedback.yaml` and `verdicts/six-scenarios.yaml`.
2. **Contexts.** `instructions/context.py`: `build_calibration_chat(entry, dimension, turn)` and
   `build_item_feedback(entry, dimension, request)`.
3. **Chat marks.** `instructions/chat.py` (new) holds the marks `one_measurable`, `follow_up_budget`,
   `preview_rules`, `no_founder_leak` (the measure stems; it reuses `score.registry_stems` and LeakStems'
   list), `importance_list` and `feedback_obeys`, each as a pure function over `(case, result)`.
4. **Validation.** `instructions/validate.py`: build_batch for chat cases `{context, turns, result}` and
   feedback cases `{item, request, result}`.
5. **Compare.** `instructions/compare.py`: `build_input` for the new picks (TopThree, Band, TeamSize,
   single pick, furthest rung). It diffs Placement AT/BEYOND/SHORT and drift STRONGER/SHORT, and adds the
   `six_scenarios` cases.
6. **Version and rescore.** `marks.py`, `marks.toml` and `rescore.py` move to v15, with calls 74–80:
   - 74: CALIBRATION_CHAT is a subject;
   - 75: one measure;
   - 76: the follow-up budget and its expected labels;
   - 77: the preview rules are keel-cloud's `ItemRules`;
   - 78: ITEM_FEEDBACK;
   - 79: the shrunken calibration and respondent denominators;
   - 80: corpus r8 and the six-scenario verdicts.
7. **Tests.** Fixtures in `tests/fixtures/chat/` (payroll Current solution with and without a follow-up,
   Relative advantage leak, chocolate leave-out, feedback per rule, the Importance list). The tests are
   `tests/test_instruction_chat_marks.py`, `test_instruction_chat_rules.py` (parity),
   `test_instruction_chat_context.py`, `test_instruction_corpus_r8.py`,
   `test_instruction_compare_six_scenarios.py` and the rescore and version tests.
8. **Docs.** AGENTS.md, README.md and Makefile at v15. DRY=1 against keel-cloud 083.

Phasing follows keel-cloud:
- Steps 1, 5 and 6 can run once 083's P3 lands (compare).
- Steps 2–4 and 7 need 083's P4 (chat and feedback contracts).
