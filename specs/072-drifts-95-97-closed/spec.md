# Spec 072 -- DRIFT #95, #96, #97 closed: the guards flip, the two out-of-scope script entries go

After keel-cloud spec 134 (the scoped plan reads `complete`; the chain starts the scope's calibrations alone) and
keel-web spec 112 (no recall window sent or drawn on money alone). No marks change; REVISION 16; marks v20.

## Rules

- **FR-1 #95 closed.** `evals/corpus_scenario._drift_95_lock` becomes a guard: on every scoped study the plan reads
  `complete: true` once the scope's calibrations are answered, and *Lock and approve* is pressed on the page as under
  ALL; locking on the wire round the button is removed. The DRIFT entry is marked closed with the keel-cloud commit.
- **FR-2 #96 closed.** `_drift_96_window` becomes a guard: on money alone the PUT carries no `recallWindow`, the served
  sentence is the windowless read-back, and no window line is drawn. Marked closed with the keel-web commit.
- **FR-3 #97 closed.** `harness/vectors_script.chained_out_of_scope` names nothing; the two out-of-scope script entries
  go; `evals/scope_journey.drift_97` asserts one CALIBRATION_QUESTIONS job per vector in scope and none for the others.
  Marked closed with the keel-cloud commit.
- **FR-4 Contract 39.** keel-cloud spec 134 bumped the contract 38 -> 39 (`LockReceiptView.questions.interactionIds`
  `minItems: 0`: money alone's lock starts no model job; `PlanView.complete` described by the scoped rule). Wherever the
  harness pins or reads the contract number or waits on the lock receipt's jobs, it reads 39 and accepts an empty list
  (S-016 locks with no job and proceeds to the money questions).
- **FR-5 Nothing else moves.**

## Acceptance

`make unit` green; S-015 and S-016 green on the local stack (keel-cloud 134 + keel-web 112 merged), S-005/006/007/014
green again; run ids in tasks.md.
