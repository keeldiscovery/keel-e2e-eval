---

description: "Task list for feature 023 — the matrix powers the twin"
---

# Tasks: The matrix powers the twin

**Input**: [spec.md](./spec.md), [plan.md](./plan.md), e2e-matrix-design §16.

**Prerequisites**: keel-cloud spec 043 applied by the founder before the first real run; until then
the start step fails at IAM and the workflow reports it — which is a correct, loud failure.

- [X] T001 [US1] `deploy-staging`: "Start the twin" and "Wait for the twin" steps per FR-001, after the assume-role step; the five-minute error message.
- [X] T002 [US2] The `stop-staging` job per FR-002, with its comment; `summary` untouched (diff shows no change in that job).
- [X] T003 [US3] `actionlint` clean; `make unit` green and unchanged.
- [X] T004 FR-003 and FR-004: the dispatch input's description and the founder-facing words.
- [ ] T005 (the founder, after keel-cloud spec 043) A-9: one green dispatch, one forced-red dispatch; instance `stopped` after each; A-11 on the next bill.
