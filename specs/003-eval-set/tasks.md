# Tasks: The Eval Set

**Input**: spec.md, plan.md, ../eval-set-design.md, keel-cloud specs/projectv2/journeys.md

## Phase 1: Setup

- [X] T001 Policy v2: restrict CLA-A1/GUI-A2 protocol sweep to display; POLICY_VERSION=2; update unit fixtures incl. seeded-display-enum still failing; re-score the existing S-001 bundle as proof (US1)
- [X] T002 [P] eval-scoring-design.md §3 amendment + runs/DRIFT.md #4 re-adjudication (append, never strike)
- [X] T003 harness/scoring.py: not-applicable categories (design §6.1) + unit tests

## Phase 2: Foundational

- [X] T004 Read the server before scripting: keel-cloud NextRecommendation, Project frame/carries, invitation link + invalid-link path, participant submit; record the discovered choreography for S-002/S-003 as module docstrings
- [X] T005 evals/recipes.py: "approved-through-invites" and "pricing-ruled-out" recipes on the real loop
- [X] T006 harness/browser.py captures: struck-through claim, said-but-didn't-count, both-headings person, decline button, invalid-link page, thank-you page

## Phase 3: US2 — the pivot (P1)

- [X] T007 [US2] evals/test_s002_pricing_pivot.py per design §3 S-002 with journey refs (§1.7–1.9, §2.4), full fact registry incl. old-claim and new-claim facts

## Phase 4: US3 — hard conversations (P1)

- [X] T008 [P] [US3] evals/test_s003_going_ahead.py: refusal-first PROCEED_TO_BRIEF, founder sentence, box-first brief, disproved-never-faith (§1.10)
- [X] T009 [P] [US3] evals/test_s004_divided_person.py: both headings, people-not-quotes, wish in said-but-didn't-count (§1.7)
- [X] T010 [P] [US3] evals/test_s005_opinions.py: nothing-solid explanation, all-skipped gentle end to end (§1.7, §2.2)
- [X] T011 [P] [US3] evals/test_s006_consent_decline.py: decline graceful + never shamed; consent four-things; thank-you promises nothing extra (§2.1–2.3)

## Phase 5: US4 — hostile wire (P2)

- [X] T012 [US4] evals/test_s007_hostile_wire.py: unknown screen, ungranted handle, concurrency with facts preserved, token survives payload fault; remedies actionable; N/A categories

## Phase 6: Polish & the night run

- [X] T013 Makefile eval-all + harness/evidence.py INDEX page (slug, verdict, score, categories, report links) + unit test
- [X] T014 Live: make up; make eval-all; make down. Record every scenario's verdict+score; every gap → runs/DRIFT.md with evidence; do NOT fix product repos yourself — report
- [X] T015 Stackless suite green; README eval-set section

## Dependencies

T001–T003 → T004–T006 → T007–T012 (parallel after T005/T006) → T013 → T014 → T015.
