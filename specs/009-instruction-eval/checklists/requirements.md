# Specification Quality Checklist: The instruction eval

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-06
**Updated**: 2026-09-06, after keel-cloud's design revision (commit `17c7642`)
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

**16/16 items passing** (was 15/16 at first authoring). The one previously unchecked item — "No
[NEEDS CLARIFICATION] markers remain" — is now checked. Both questions were answered by the founder's
revision of the design of record on 2026-09-06 (keel-cloud commit `17c7642`), and the answers are in
the spec's `## Clarifications` section and folded through FR-005, FR-011, User Story 2, the Edge
Cases, and [research.md](../research.md) R5a and R6.

| Question | Answer | Where it landed |
|---|---|---|
| `existing_roles` for the later stages | **Derive from earlier stages' `askedOf`** — `[]` for PROBLEM, PROBLEM's roles for SOLUTION, those plus SOLUTION's for COMMERCIAL | FR-005, [data-model.md](../data-model.md) §3, R5a, task T005 |
| What a `NEEDS_INPUT` result scores | **A failed case** — decision 14 removed both cases where an assumption screen could legitimately ask, and the harness always supplies a statement | US2 scenario 8, the Edge Cases, [contracts/metrics-contract.md](../contracts/metrics-contract.md), R6, task T011 |

**Three things changed beyond the two questions**, because the same revision changed what this
harness can and cannot do:

- **The §8.3 phrase mapping became scorable.** keel-cloud spec 029 puts `founderPhrase` on the wire
  (design §8.1 step 4). It is now a seventh exact-match field, and the report reads the phrase and
  the band **together** in their four combinations — a right band from a phrase the founder never
  used is right for the wrong reason, and used to look identical to a right one. It has come off the
  spec's list of blind spots.
- **The register got a page and stayed unscored.** Design §10 step 4 now says what to do instead of
  scoring it: "a person who knows the market reads the produced anchors and options, and that
  reading is recorded". FR-019 writes `register.html`, FR-020 makes the report say plainly that
  nothing on it is scored, SC-007 records the reading, and **no metric was invented**. That is a
  deliberate hole in a scored artefact, argued in the plan's Complexity Tracking and in judgement
  call 7.
- **The model limit got a line in the header.** Pinning it is out of scope (keel-runtime sends no
  `--model` and this repo calls the executor the way production does), so FR-021 puts the CLI version
  and the reported model in the report header with the sentence that the marks are comparable only
  within a model. Recorded as an assumption rather than left implicit.

**On "Content Quality — no implementation details".** Marked passing under this repo's own house
style, which specs 004–008 set: an FR here is a file plus its contract (`- **FR-001**
\`instructions/corpus.py\`: …`), because the reader is the founder plus the agent that will build it,
and because a referee's spec that does not name the file it reads is not checkable. The *outcomes* —
what is measured, against what marks, with what evidence — are stated without reference to how.

**On the constitution.** `.specify/memory/constitution.md` is the unfilled spec-kit template here, as
spec 001's plan recorded. The binding rules are `AGENTS.md`'s, and this spec honours them explicitly:
the repo reports and never fixes (FR-023); the deterministic scenario set is untouched (SC-006); the
policy version convention is mirrored rather than borrowed (FR-014's `MARKS_VERSION`, a separate
constant so a marks change can never be mistaken for a policy change).

**One rule is deliberately amended rather than obeyed.** AGENTS.md says "no Prism, no LLM, ever".
That sentence was already inexact — S-004 has called a real `claude` since spec 008 — and this
feature makes it inexact twice over. FR-022 amends it to name its two exceptions rather than leave a
rule the repo does not follow. Naming them is the point: everything not named stays deterministic.

**No questions remain open.**
