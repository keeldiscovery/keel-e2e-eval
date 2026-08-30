# Feature Specification: The Eval Set — Six Journeys and a Hostile Wire

**Feature Branch**: `003-eval-set`

**Created**: 2026-08-30

**Status**: Draft

**Input**: User description: "Read the journeys, the mockups, and the designs and come up with a
good eval set: design the evals, implement using specs, run them, and fix glaring issues found.
specs/eval-set-design.md is the design of record."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The policy measures the right surfaces (Priority: P1)

Policy v2 recalibrates the v1 category error: protocol vocabulary sweeps apply to the handoff
`display` (founder-relayed) but not to `instruction.content` or `requirements` (agent-facing
method and payload guidance); the UI and participant-page sweeps stay at full strength. DRIFT #4
is re-adjudicated in place.

**Independent Test**: re-score the existing S-001 bundle under policy v2 — the twenty
mismeasured failures disappear, the UI sweeps still run, and a seeded enum in a display string
still fails.

**Acceptance Scenarios**:

1. **Given** policy v2, **When** S-001 re-scores, **Then** GUIDANCE and CLARITY no longer carry
   the agent-text false positives and the policy version stamps 2.
2. **Given** a seeded raw enum in a handoff display fixture, **When** scored, **Then** CLA-A1
   fails it.

### User Story 2 - The pivot journey holds end to end (Priority: P1)

S-002 drives the §1.7–1.9 arc: a ruled-out pricing deal-breaker, a replacement claim carrying
only what evidence never spoke against, re-approval, fresh links that re-ask nothing settled,
recovery, brief — while the old link dies politely (§2.4) and the untouched stages stay
untouched.

**Independent Test**: run S-002 scored; its assertion list maps one-to-one to the journey
sections it names.

**Acceptance Scenarios**:

1. **Given** the reframe, **When** the commercial card renders, **Then** the old claim is
   struck through but readable and problem/solution cards are byte-identical in status and
   counts to before.
2. **Given** the pre-pivot link opened after the reframe, **Then** the §2.4 out-of-date page
   shows and nothing entered there reaches the founder.
3. **Given** the fresh link, **Then** it carries the new pricing questions and the still-open
   problem belief, and nothing the evidence settled.

### User Story 3 - The hard conversations are walked, not skipped (Priority: P1)

S-003 (going ahead anyway: refusal-first, founder's sentence, GOING AHEAD ANYWAY box first,
disproved never blurred into faith), S-004 (divided person on both sides; people not quotes;
wishes in "said, but didn't count"), S-005 (opinions move nothing; all-skipped handled gently),
S-006 (decline graceful; consent screen carries exactly its four things).

**Independent Test**: each scenario runs scored and its named journey assertions pass or become
DRIFT entries with evidence.

**Acceptance Scenarios**:

1. **Given** PROCEED_TO_BRIEF with a contradicted deal-breaker and no goingAhead, **Then** the
   server refuses with an actionable remedy, and the retry with the founder's sentence renders
   it first in the brief.
2. **Given** one person's evidence in both directions, **Then** they appear under both headings
   and the collapsed line counts people.
3. **Given** an all-skipped submission, **Then** the stranger sees a kind page and the
   founder's counts stay honest.

### User Story 4 - The wire pushes back usefully (Priority: P2)

S-007, no browser: unknown screen, ungranted handle, stale token after a concurrent commit —
every refusal's remedy would tell a lost agent what to do; the token survives payload faults;
scored on agent-surface attributes with absent categories marked not-applicable.

**Independent Test**: run S-007 scored; assert each refusal shape and the facts-preserved
retry.

### Edge Cases

- Scenario independence: every scenario creates its own project; S-002/S-003 share a setup
  recipe, never state.
- A scenario that discovers a product gap does not fail silently or work around it: DRIFT
  entry + low score + (per the user's authorization) a product fix and rerun.
- Strikethrough asserted via accessible text/styling hooks, not pixels.

## Requirements *(mandatory)*

- **FR-001**: Policy v2 per design §2, with DRIFT #4 re-adjudication and an amendment note in
  eval-scoring-design.md §3.
- **FR-002**: Scenarios S-002 through S-007 implemented as Scenario modules with fact
  registries, each runnable via `make eval K=<slug>` and fully scored.
- **FR-003**: Every scenario assertion that enforces a named journey sentence MUST reference
  the journey section in its test code.
- **FR-004**: S-007's scorecard MUST mark non-applicable categories as absent, not zero, and
  the aggregate MUST stay honest.
- **FR-005**: A `make eval-all` target MUST run the full set against one stack and produce an
  index of run bundles with scores.
- **FR-006**: Product gaps found MUST land in runs/DRIFT.md with evidence; fixes authorized by
  the user go to the owning repo, and the affected scenarios rerun green.

### Key Entities

- **Scenario modules** s002–s007 with per-scenario fact registries and answer tables.
- **Policy v2**: the recalibrated check set.
- **Eval-all index**: one page listing the night's runs and scores.

## Success Criteria *(mandatory)*

- **SC-001**: All seven scenarios (S-001 rerun included) complete scored runs in one
  `make eval-all` session.
- **SC-002**: Every journey section named in design §3 has at least one passing assertion or a
  DRIFT entry with evidence.
- **SC-003**: Stackless suite still green; policy v2 seeded fixtures behave per US1.
- **SC-004**: After authorized fixes, a full rerun leaves no scenario failing on a known
  product gap.

## Assumptions

- The user has authorized fixing glaring product issues found tonight ("if you find any glaring
  issues, fix it, rerun the eval").
- keel-cloud/keel-web behavior discovered to differ from the journeys is a finding to fix or
  record, never to paper over in the eval.
