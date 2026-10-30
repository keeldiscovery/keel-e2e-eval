# Spec 105 -- The harness reads the frontier tier, the new prices, and screens the back-test and probe entries

keel-cloud 169 (merging 2026-10-30; its tasks.md lists every pin): routing v14 puts the two frame jobs (`PROBLEM_INTERPRET`,
`SOLUTION_MECHANISM`) on the frontier tier, `claude-opus-5-5` at medium with no sampling, and codex / copilot fall back to
their standard row one rung down; `InferenceCharge.VERSION` 13 with `PROBLEM_INTERPRET` 26 and `SOLUTION_MECHANISM` 28
(`NEW_PROJECT_PRICE` 300); `ModelRates` gains Opus 5.5; the probe fixture
`canon/designs/measured-beliefs/probes/169-banking-gaming.yaml`. Today `make instruction-screen` reads only the golden
corpus (01-07), so `K=08-fresco/…` and the probe match no case and nothing runs.

## Rules

- **FR-1 The fallback mirror.** `instructions/models.py` `resolve` (~:146-151) and `resolve_effort` (~:166-176): a class
  on a tier the host has no row for falls back one rung (frontier -> standard), model and effort together, as
  `ModelRouting.FALLBACK` does; the S-012 per-job model check (`evals/test_s012_journey_through_a_host.py:1345`) follows.
  The routing export is read as the file; the mirror applies the fallback.
- **FR-2 `PRICE_VERSION` 12 -> 13** in `harness/interview_charge.py:20`, `harness/interviewer_fake.py:39`,
  `harness/contacts_fake.py:40`, with the prose beside each; `tests/test_credits_at_begin_088.py` (:3, :53, :95),
  `tests/test_interviewer_marks.py:834`; the S-012 journey's prose (:35, :1244). No corridor sum is mirrored; if a gate
  check is added it is 300.
- **FR-3 The screen reads back-test and probe entries.** `instructions/run.py` `_all_cases` takes the back-test corpus
  (`backtest-r19/`) and `probes/*.yaml` beside the golden corpus, so `K=08-fresco/PROBLEM_INTERPRET` and
  `K=169-banking-gaming` match. A **probe mark**: the first turn is `NEEDS_INPUT` with one question that names the
  planted term and offers two readings (the gaming sense, the banking sense); a statement or card that keeps or
  rewrites the term is a fault. The screen's records name the probe apart from the entries.
- **FR-4 Nothing else moves.** Routing `v14` reaches the quality score names from the cloud commit on its own
  (`quality/readers.py:172`); the synthetic `v13` fixtures in `tests/test_quality_0{78,79,81}.py` stay. The gallery, the
  marks, the corpus.
- **FR-5 Tests.** The fallback on a routing file with a frontier class and no host row; the price version pins; the
  screen's case list with a back-test entry and a probe; the probe mark on a NEEDS_INPUT and on a card.

## Acceptance

`make unit` ZERO failed (master's counts as 104's tasks.md records them). Build after 104; one builder at a time. The
screens themselves are the coordinator's, paid, on the founder's word.
