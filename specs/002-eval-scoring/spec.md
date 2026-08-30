# Feature Specification: Eval Scoring — Rubric, Fidelity, and a Run Score

**Feature Branch**: `002-eval-scoring`

**Created**: 2026-08-30

**Status**: Draft

**Input**: User description: "Evals must evaluate, not just execute: assume a founder unfamiliar
with the framework — at each step, does the agent give enough context to know where you are and
what to do next; when the founder enters information, is it processed without loss; in the UI,
is there no loss of information; can the whole workflow complete. Validate on both the skill/agent
surface and the UI. Every execution gets its own folder with a screenshot of each interaction;
each interaction is evaluated against a policy on designed attributes; the run gets a score out
of five we can use. specs/eval-scoring-design.md is the design of record."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Every interaction is scored against the policy (Priority: P1)

After `make eval K=s001`, the run bundle contains a scorecard: every interaction (agent cycle,
handoff, founder screen visit, participant page) evaluated on ORIENTATION, GUIDANCE, FIDELITY,
and CLARITY by deterministic policy checks, each check carrying evidence references.

**Independent Test**: run S-001; open scorecard.json; every interaction has attribute scores
and every check names its evidence (step seqs, screenshot files).

**Acceptance Scenarios**:

1. **Given** a completed run, **When** the scorecard is read, **Then** each interaction carries
   per-attribute scores on a 0–5 half-point scale derived from weighted checks.
2. **Given** any check result, **When** its evidence refs are followed, **Then** they resolve to
   real transcript steps and screenshot files in the same bundle.
3. **Given** the policy, **When** a check, weight, or waiver changes, **Then** policy_version
   changes, and the version is stamped in scorecard.json and verdict.json.

### User Story 2 - Loss of information is caught, hop by hop (Priority: P1)

The scenario declares its facts (statements, roles, assumptions, about-line, participant
answers, interpretations). The FIDELITY attribute verifies each fact at each declared hop —
agent echo, founder screens, participant page, interpret context, brief — verbatim by default,
with summarizing hops allowed only via a referenced waiver in the policy.

**Independent Test**: run S-001 and confirm all fact-hops pass (or are waived with reference);
then deliberately corrupt one expected hop in a unit-test fixture and confirm the check fails
with the fact id and hop named.

**Acceptance Scenarios**:

1. **Given** S-001's facts, **When** the run completes, **Then** every declared hop is checked
   and the scorecard lists each fact × hop result.
2. **Given** the brief-findings hop, **When** it summarizes, **Then** the result is a waiver
   citing keel-cloud api-design §6a, not a silent pass.
3. **Given** a rendering that truncates a founder-typed statement, **When** fidelity runs,
   **Then** that hop fails and names the fact.

### User Story 3 - The run gets one usable score (Priority: P1)

The report opens with X/5: category bars for the four attributes, the run score computed by
policy weights, and the completion gate — an incomplete workflow caps the run at 2/5 regardless
of how well its interactions scored.

**Independent Test**: S-001 full pass produces a score ≥ the gate; kill the stack mid-run and
the bundle still scores what it saw, capped at 2/5, verdict failed.

**Acceptance Scenarios**:

1. **Given** a complete S-001, **When** the report opens, **Then** the header shows the run
   score, four category bars, and the policy version.
2. **Given** an interrupted run, **When** scoring runs, **Then** category scores exist for what
   was observed and the run score is capped at 2/5.
3. **Given** two runs under the same policy version, **When** compared, **Then** their scores
   are comparable (same checks, same weights).

### User Story 4 - Every interaction is visually reviewable (Priority: P2)

Browser interactions already have screenshots; agent-surface interactions (issuances, handoffs)
gain conversation cards in the report — the instruction and requirements as the founder's agent
would voice them, the scripted reply, the outcome — so a reviewer pages through the whole
discovery interaction by interaction.

**Independent Test**: open the S-001 report; count interaction cards == interactions in
scorecard.json; every card shows either screenshots or a conversation card plus its checks.

**Acceptance Scenarios**:

1. **Given** the report, **When** an agent-cycle card is viewed, **Then** it shows the
   conversation content, not raw JSON (raw stays available, collapsed).
2. **Given** any interaction card, **When** viewed, **Then** its attribute chips and failed
   checks (if any) are inline.

### Edge Cases

- Screens with nothing to do (all approved, waiting): GUIDANCE checks are conditional on a need
  existing — calm emptiness passes (design §8.1).
- CLARITY exempts URL path segments and the two licensed action names.
- A fact that legitimately does not reach a hop in a scenario variant (e.g. a skipped answer)
  is declared absent by the scenario, not silently unchecked.
- Scoring is a pure function of the transcript + captured artifacts: `make report RUN=` re-runs
  scoring too, so old bundles can be re-scored under a new policy (stamped accordingly).

## Requirements *(mandatory)*

- **FR-001**: Steps MUST carry interaction tags; interactions MUST cover both surfaces (agent
  cycles/handoffs, founder screens, participant pages) per design §2.
- **FR-002**: A versioned policy module MUST define all checks, weights, category weights,
  clarity token lists, normalization, and waivers (each waiver: hop, reason, reference).
- **FR-003**: The four attributes MUST be evaluated by deterministic checks only — no LLM, no
  wall-clock dependence; every check result MUST carry evidence refs.
- **FR-004**: Scenarios MUST declare a fact registry; FIDELITY MUST check each fact at each
  declared hop with normalized-verbatim matching and waiver support.
- **FR-005**: CLARITY MUST sweep founder-facing protocol text and rendered pages for raw enum
  tokens, JSON punctuation, and field names, with the design's exemptions.
- **FR-006**: Scoring MUST roll up checks → interaction attributes → categories → run score
  (X/5, halves), with the 2/5 completion gate; scorecard.json and verdict.json MUST carry
  score and policy_version.
- **FR-007**: report.html MUST add the score header, category bars, per-interaction cards with
  inline checks, and conversation cards for the agent surface; the report (including scores)
  MUST remain regenerable from the bundle alone via `make report RUN=`.
- **FR-008**: S-001 MUST be upgraded to declare its facts and run fully scored; scoring
  failures caused by product gaps MUST surface as low scores + DRIFT.md entries, never local
  workarounds.

### Key Entities

- **Interaction**: tagged span of transcript steps; the unit of evaluation.
- **Policy**: versioned checks/weights/waivers module; sole scoring authority.
- **Fact registry**: scenario-declared texts with expected hops.
- **Scorecard**: per-run JSON of check results, attribute/category/run scores.

## Success Criteria *(mandatory)*

- **SC-001**: A complete S-001 produces a scorecard where every interaction is scored and every
  check's evidence resolves; the report shows X/5 with category bars.
- **SC-002**: Seeded-loss unit fixtures (truncated statement, leaked enum, empty display) each
  fail exactly their intended check.
- **SC-003**: An interrupted run still yields a scored bundle capped at 2/5.
- **SC-004**: Re-scoring an old bundle under a bumped policy stamps the new version and never
  mutates the original transcript or screenshots.

## Assumptions

- Feature 001's harness is the substrate; the transcript stays the single source of truth.
- keel-cloud carries the brief/URL fixes found by feature 001, so a full S-001 pass exists to
  score.
- Qualitative judging by an operator agent is out of scope (design §6).
