# Spec 117 -- The harness's mirrors follow keel-cloud 178/179 and keel-web 152/153/154

Three merges of 2026-10-31 moved words the harness mirrors or records; `make unit` is still green (4,755) because the
mirrors pin their own words, but the walk's DRY compare (`evals/corpus_scenario.py:4843`) reads the brief's cards
through `instructions/brief_facts.py`, so cycle 4's money studies would report faults that are not faults.

## Rules

- **FR-1 keel-cloud 179 (its tasks.md).** `instructions/brief_facts.py`: `KEEL_BAR[PURCHASE_FRICTION_KEY]` = *holds if
  at least 2 in 3 say it would be needed and would take a long time*; `friction_words` held *Yes, {step} would slow it.
  Plan for it.*, not held *Your fear was {step}. k of n said it would be quick or not needed. Not the blocker you
  expected.*; the card line (~:341) *would need {step}, and it would take a long time*; Compare's status line / insight /
  drift clause words *said it would take a long time* / *said it would be quick or not needed* wherever mirrored;
  `tests/fixtures/sample/s006-reads.json` is a recorded read: mark it for re-recording in tasks.md (do not hand-edit) and
  make its test tolerate the tense until then, with why. Compatibility's served Choose prompt = *Which one do you want to
  test?* where the walk reads it.
- **FR-2 keel-cloud 178.** The answers view's `NOTHING` label is *None* (note at `harness/vectors_script.py:983` stays).
- **FR-3 keel-web 153 (its tasks.md "What keel-e2e-eval must read").** `list_answer` hints for Importance and
  Compatibility; `list_choose` prompt for Purchase friction; the Purchase friction Choose bar; the Commitment Check bar
  on B2B; `keeltest-note`; `frequency-range-hint`; the Importance count-free box.
- **FR-4 keel-web 152 and 154.** The AI story sheet may hold two chips (first still *can't recall*; `tap_chip_named`);
  a spoken refusal ends the interview without a tap. The after-answers leg (109) moves its stage-page selectors to
  154's ids (`stage-page`, `stage-verdict`, `stage-dimension[data-dim][data-opens]`, `stage-dimension-open`,
  `dimension-chart`, `dimension-verdict`, `dimension-count`), classes as fallback.
- **FR-5 Tests.** Each moved mirror pinned with why; `make unit` ZERO failed.

## Acceptance

`make unit` ZERO failed. Build before cycle 4.
