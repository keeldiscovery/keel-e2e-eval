# Spec 113 -- The harness reads keel-cloud 173: the advantage belief in one sentence, the occasion in the question

keel-cloud 173 (merged 2026-10-30; its tasks.md lists every pin): `solution.relative_advantage`'s belief is *For most,
their last {occasion} would have gone better with it: {value}.* (the first benefit whole, leading capital dropped; *the
last time* with no noun); the stranger's question is *Would {idea} have made your last {occasion} go better for you, or
not?*, past the 20-word cap *Would it have made your last {occasion} go better …* (never the plain frame; the spec-120
anchor stays first); items stored before 173 keep 159's wording; the drift clause reads *you said it would have gone
better: {founder} · …*; `benefit_list`: one item per benefit as typed, never split, add none; no corpus revision (the
r19 record keeps 152's words; the cloud reads them through one rule).

## Rules

- **FR-1 The belief mirror.** `instructions/corpus.py:21`, `instructions/marks.py:139`; `tests/test_corpus_r19.py:260-262`
  stands for the r19 record (read through one rule as the cloud's `spec173Reads`), never rewritten.
- **FR-2 The question mirror.** `harness/vectors_script.py:627-633` (`BENEFIT_FRAME`, `benefit_question`: the new frame,
  *the last time*, the over-cap *it* form); `tests/test_controls_089.py:231-240`, `tests/test_vectors_journey.py:313-317`;
  an item stored before 173 (the gallery's older recordings) is read in 159's frame.
- **FR-3 The spoken mirror.** `instructions/spoken.py:13`; `tests/test_instruction_spoken.py:112-121` (the short form keeps
  the occasion); `evals/interviewer_leg.py:1610`, `evals/corpus_scenario.py:3851`, `evals/test_s006_paidly.py:20` (they
  quote 159's frame -> 173's).
- **FR-4 The slice and the marks.** `tests/fixtures/registry/slice.yaml:275`; the expected drift clauses *you said it
  would have gone better: {benefit} · …*; the whole-row rule in the founder-lists screen's mark (112's `steps_mark`
  pattern) for `CALIBRATION_SOLUTION/RELATIVE_ADVANTAGE`: one row per typed benefit, never split; the case
  `K=10-palus/CALIBRATION_SOLUTION/RELATIVE_ADVANTAGE` with the Answer *Higher yield without hiring for treasury* expects
  one row. Gallery fixtures stay (older recordings).
- **FR-5 Tests.** `tests/test_advantage_belief_113.py`; `make unit` ZERO failed (master's counts as 100's tasks.md records
  them).

## Acceptance

`make unit` ZERO failed. Build after 100, before 106; one builder at a time in this repo.
