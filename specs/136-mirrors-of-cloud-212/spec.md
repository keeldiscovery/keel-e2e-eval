# Spec 136 -- Mirrors of keel-cloud 212: one event, the act that hurts

Owed by keel-cloud 212 (merged 2026-11-04, master `55bf014`). Since that merge `make unit` on master is red on two
pins: `test_cloud_211_mirror_133::test_nothing_else_in_the_cards_moved_and_the_clouds_copy_is_owed` (the vendored
cards moved: one-clause lines under Prevalence and Frequency, digest `877a5d80…`) and
`test_seven_templates_115::test_the_slice_says_174s_words[problem.frequency-founder-guidance]` (the registry's
Frequency founder guidance changed). This spec makes master green again and carries the rest of what 212 owes.

## Rules

- **FR-1 The cards.** `quality/readers/dimensions.md` gains, under Prevalence and Frequency, the one-clause lines as
  keel-cloud's vendored copy carries them (the strangers' event is the founder's own clause, turned to the second
  person by code; Compatibility's `settled_by`), so the source and the vendored copy agree again and the 133 pin
  holds at the new digest. The 115 slice pin moves to the registry's new Frequency founder guidance.
- **FR-2 The instruction mirrors.** `instructions/*.py` mirrors of founder-lists.md (routine, went_wrong, the event
  from went_wrong, the per-window cap in the Sizes line, settled_by) and respondent-questions.md (the gate is code's
  where the founder's clause exists; the writer's clause only where `problem` is null, capped) move to the merged
  text, with the pins that read them.
- **FR-3 The scripted results.** Every scripted CALIBRATION_QUESTIONS result for Prevalence carries `routine`,
  `went_wrong` and an `event` of at most the window's cap (20 minus the frame; 9 on a 7-day or 3-month window, 8 on
  5 working days) that passes E7/E8 (not the routine; no cause, state or judgement); every scripted Compatibility row
  carries `settled_by: nobody` (one row per entry may be another value where the entry tests the rule); scripted
  RESPONDENT_QUESTIONS carry no `event` where the founder's clause exists. The contract export re-vendored
  (descriptions changed; version 25).
- **FR-4 The fourteen entries' clauses** are read against the cap by a unit test (the golden seven and the gallery:
  each entry's Prevalence event fits its window's cap, else the test names the entry and the count); an entry over
  the cap is a finding for the next corpus revision, not a failure, until the founder's word.
- **FR-5** `make unit` green on master's cloud (55bf014). Nothing else moves.
