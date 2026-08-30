# Data Model: Eval Scoring

## Interaction tag (on StepRecord)
`interaction: {id: "I012", type: agent-cycle|agent-handoff|ui-visit|participant-page}` —
optional; untagged steps (stack plumbing) belong to no interaction.

## Interaction (derived, harness/interactions.py)
`{id, type, title, party, step_seqs: [int], screenshots: [file], conversation?: {instruction,
requirements, reply_summary, outcome}, captured_text: {source→text}}`

## Check result (rubric.py)
`{check_id, attribute, weight, pass: bool, waived?: {reason, reference}, detail, evidence:
{steps: [seq], screenshots: [file], fact_id?, hop?}}`

## Fact registry (Scenario.facts())
`{fact_id: {text, kind: statement|role|assumption|about_line|answer|interpretation,
hops: [hop_id], absent_hops?: [hop_id]}}` — hop ids named by the policy (e.g.
`agent_echo`, `stage_screen`, `participant_page`, `interpret_context`, `brief`).

## scorecard.json
`{policy_version, scenario, generated_at, interactions: [{id, type, title, attributes:
{ORIENTATION?: score, ...}, checks: [check result]}], categories: {attr: score},
run_score, gated: bool, complete: bool}`

## verdict.json additions
`score: float, policy_version: int` (existing fields unchanged)

## Scoring math (scoring.py)
attribute(interaction) = round_half(5 × Σw(pass|waived) / Σw) — waived counts as pass but is
flagged; category = weighted mean over carrying interactions; run = Σ category_weight ×
category; if not complete → min(run, 2.0). All weights from policy.
