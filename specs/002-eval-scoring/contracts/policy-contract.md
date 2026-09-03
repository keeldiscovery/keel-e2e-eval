# Contract: Policy v1

`evals/policy.py`, POLICY_VERSION = 1. Category weights: FIDELITY 0.4, GUIDANCE 0.25,
ORIENTATION 0.2, CLARITY 0.15.

## Checks (id — attribute — applies to — passes when)
- ORI-A1 — ORIENTATION — agent-cycle — instruction.content non-empty, names a purpose
- ORI-A2 — ORIENTATION — agent-cycle (stage/invitation-scoped) — detail locates the work
- ORI-H1 — ORIENTATION — agent-handoff — display non-empty, names destination or waiting
- ORI-U1 — ORIENTATION — ui-visit — project identity visible
- ORI-U2 — ORIENTATION — ui-visit (stage) — stage identity visible in founder words
- ORI-P1 — ORIENTATION — participant-page — founder display name + about-line visible
- GUI-A1 — GUIDANCE — agent-cycle — requirements present, sentence-shaped
- GUI-A2 — GUIDANCE — agent-cycle — founder-phrased (no camelCase, no JSON, no raw enums)
- GUI-H1 — GUIDANCE — agent-handoff — display says what to do next
- GUI-U1 — GUIDANCE — ui-visit — next-step affordance present *iff* a need exists (conditional)
- GUI-P1 — GUIDANCE — participant-page — flow reaches submit; thank-you confirms
- FID-* — FIDELITY — generated per fact × hop from the scenario registry (normalized-verbatim;
  waiver-aware). Weight 1 each.
- CLA-U1 — CLARITY — ui-visit/participant-page — no raw enum tokens in rendered text
- CLA-U2 — CLARITY — ui-visit/participant-page — no JSON punctuation / field names in text
- CLA-A1 — CLARITY — agent-cycle/handoff — founder-facing text (instruction, requirements,
  display) free of raw enums (CREATE/INTERPRET licensed) and field names

## Normalization
casefold, collapse whitespace, unify quotes/apostrophes, strip trailing punctuation.

## Clarity token list
workflow states, verdicts, needs, risks, stage enum tokens, handle names, action names (minus
the two licensed), rule literals. URL path segments exempt.

## Waivers (v1)
- `brief-findings-summarize`: hop `brief` for assumption facts may summarize — reference:
  keel-cloud `canon/api-design.md` §6a (Brief.findings loses counts). Flagged in
  scorecard, counts as pass.

Weights: all checks weight 1 in v1 except FID checks on `answer` facts at `interpret_context`
(weight 2 — verbatim participant speech is the product's evidence spine).
