# Contract: Scorecard & Report

## scorecard.json
Shape per data-model.md. Every check carries evidence refs that resolve inside the same bundle
(step seqs exist in transcript.jsonl; screenshot files exist on disk). Absence of scorecard.json
in a run dir = scoring layer crashed (same signal contract as verdict.json).

## report.html additions
- Header: run score X/5 (large), four category bars, policy version, gated badge when capped.
- Interaction cards in transcript order: title, type/party badges, attribute chips (score-
  colored), screenshots or conversation card, failed/waived checks inline (passed checks
  collapsed), links to raw steps.
- Conversation card (agent surface): instruction purpose + content, requirements list, the
  scripted founder reply (summarized from the submitted payload), outcome line (committed
  revision N / refusal rule / handoff reason). Raw JSON stays available, collapsed.
- Scorecard table at the bottom: interaction × attribute matrix.
- `make report RUN=<dir>` re-runs scoring + rendering from the bundle alone; re-scoring under a
  newer policy stamps that policy_version and never mutates transcript or screenshots.

## verdict.json
Gains `score`, `policy_version`; written in finally as before.
