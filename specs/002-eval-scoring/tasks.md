# Tasks: Eval Scoring

**Input**: spec.md, plan.md, data-model.md, contracts/{policy,scorecard}-contract.md,
../eval-scoring-design.md (design of record)

## Phase 1: Setup

- [ ] T001 harness/steps.py: StepRecord gains optional `interaction: {id, type}`; Recorder helper to open/close an interaction scope so steps inside are auto-tagged

## Phase 2: Foundational

- [ ] T002 harness/interactions.py: derive interaction objects from a tagged transcript (+ captured_text and conversation content per data-model.md)
- [ ] T003 evals/policy.py: POLICY_VERSION=1 — every check, weight, category weight, clarity token list, normalization, and the brief-findings waiver, exactly per contracts/policy-contract.md
- [ ] T004 harness/rubric.py: check engine — evaluates policy checks over interactions, emits check results with mandatory evidence refs; FID-* generated from the scenario fact registry
- [ ] T005 harness/scoring.py: roll-ups per data-model.md scoring math (halves, waived-counts-as-pass-but-flagged, 2/5 completion gate)
- [ ] T006 [P] evals/scenario.py: `facts()` registry hook (fact id, text, kind, hops, absent_hops)

## Phase 3: User Story 1 — every interaction scored (P1)

- [ ] T007 [US1] harness/driver.py: open agent-cycle/agent-handoff interaction scopes; capture founder-facing text (instruction, requirements, display, outcome) into captured_text
- [ ] T008 [US1] harness/browser.py: open ui-visit/participant-page scopes; page objects capture rendered text (headings, chips, body) for ORI/GUI/CLA/FID checks
- [ ] T009 [US1] harness/evidence.py + evals/conftest.py: run rubric+scoring after each eval; write scorecard.json; verdict.json gains score+policy_version (still in finally — interrupted runs score what they saw, gated)
- [ ] T010 [P] [US1] tests: fixture transcript → interactions → scorecard with resolving evidence refs (SC-001 mechanics)

## Phase 4: User Story 2 — loss of information caught (P1)

- [ ] T011 [US2] evals/test_s001_smoke.py: declare S-001's full fact registry (statements, roles, assumptions, about-line, participant answers, interpretations) with hops per design §3
- [ ] T012 [US2] FID hop capture: wire the six hop ids (agent_echo, stage_screen, invite_screen, participant_page, interpret_context, brief) through driver/browser captured_text
- [ ] T013 [P] [US2] tests (SC-002): seeded-loss fixtures — truncated statement fails its FID check naming fact+hop; brief summarizing passes waived-with-reference; corrupt answer at interpret_context fails its weight-2 check

## Phase 5: User Story 3 — one usable score (P1)

- [ ] T014 [US3] Report header: X/5, category bars, policy version, gated badge (evidence contract)
- [ ] T015 [P] [US3] tests: scoring math (halves, category weights, gate); interrupted-run fixture scores gated 2/5 (SC-003); re-score idempotence — bundle files untouched, policy stamp updates (SC-004)

## Phase 6: User Story 4 — visually reviewable (P2)

- [ ] T016 [US4] Report interaction cards: transcript order, badges, attribute chips, inline failed/waived checks, screenshots; conversation cards for agent surface (raw JSON collapsed); scorecard matrix at bottom
- [ ] T017 [P] [US4] tests: report renders one card per interaction from a fixture bundle; conversation card shows instruction/requirements/outcome, not raw JSON

## Phase 7: Polish

- [ ] T018 Run scored S-001 for real (stack up, eval, down): SC-001 live — confirm the full pass scores, every FID hop green or waived; where a check exposes a product gap, record it in runs/DRIFT.md and let the score be low (FR-008) — no local workarounds
- [ ] T019 README + quickstart alignment: scored-run walkthrough, re-scoring, policy-change protocol (bump POLICY_VERSION)

## Dependencies

T001 → T002 → {T003, T006} → T004 → T005 → US1 (T007–T010) → US2 (T011–T013) → US3 → US4 → Polish.
T018 requires keel-cloud to carry the feature-001 fixes (brief crash, /error, OpenWebUrls).

## Implementation strategy

MVP = Phases 1–3 (scored interactions with evidence). US2 is the user's sharpest ask; US3 the
usable number; US4 the review surface. T018 is the live proof on this machine.
