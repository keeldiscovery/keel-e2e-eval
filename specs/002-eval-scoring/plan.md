# Implementation Plan: Eval Scoring

**Branch**: `002-eval-scoring` | **Date**: 2026-08-30 | **Spec**: [spec.md](./spec.md)

**Input**: spec.md + ../eval-scoring-design.md (design of record)

## Summary

Layer a deterministic evaluation engine over the feature-001 harness: interaction tags on the
existing transcript, a versioned policy module of weighted checks across four attributes
(ORIENTATION, GUIDANCE, FIDELITY, CLARITY), a scenario-declared fact registry driving hop-by-hop
fidelity, roll-up scoring with a 2/5 completion gate, and a report upgraded with score header,
per-interaction cards, and conversation cards for the agent surface. Everything remains a pure
function of the run bundle, so `make report RUN=` re-scores old bundles.

## Technical Context

**Language/Version**: Python 3.11+ (same venv; no new dependencies)

**Primary Dependencies**: unchanged — pytest, playwright, requests, stdlib

**Storage**: `runs/<id>/scorecard.json` added to the bundle

**Testing**: stackless unit tests over fixture transcripts/artifacts (SC-002 seeded-loss
fixtures); the scored S-001 run is the live proof

**Project Type**: extension of the existing harness packages

## Constitution Check

Unfilled template. Inherited rules binding: no product-repo fixes (drift → DRIFT.md + low
score); report regenerable from the bundle alone; determinism (no LLM, no clock dependence in
scoring).

## Project Structure (files touched/added)

```text
harness/steps.py            # StepRecord gains interaction tag (id, type); recorder helper
harness/interactions.py     # NEW: groups tagged steps into interaction objects
harness/rubric.py           # NEW: check engine — runs policy checks over interactions,
                            #      emits scorecard.json (evidence refs mandatory)
harness/scoring.py          # NEW: roll-ups (interaction→attribute→category→run), gate, halves
harness/evidence.py         # verdict gains score+policy_version; report: score header,
                            #      category bars, interaction cards, conversation cards
harness/browser.py          # page objects expose text-capture hooks the checks need
harness/driver.py           # tags agent-cycle/agent-handoff interactions; captures
                            #      founder-facing text (instruction, requirements, display)
evals/policy.py             # NEW: POLICY_VERSION=1, checks, weights, clarity tokens,
                            #      normalization, waivers (brief-findings ↦ api-design §6a)
evals/scenario.py           # Scenario gains facts() registry (fact id → text → hops)
evals/test_s001_smoke.py    # declares facts; interaction tagging through the choreography
tests/                      # unit tests incl. SC-002 seeded-loss fixtures
```

## Design decisions already closed (design §§2–5, 7–8)

Interaction taxonomy and tagging-not-restructuring; deterministic proxies with the LLM-judge
boundary; fact-registry fidelity with verbatim-by-default + referenced waivers; versioned
policy; half-point scale; 2/5 completion gate; conditional GUIDANCE on screens with no need;
CLARITY exemptions (URL segments, CREATE/INTERPRET).

## Phase 1 artifacts

- `data-model.md` — interaction, check-result, scorecard, fact-registry shapes.
- `contracts/policy-contract.md` — the shipped v1 policy: every check id, weight, condition,
  and waiver, so scores are reviewable against a document.
- `contracts/scorecard-contract.md` — scorecard.json + report additions.
- `quickstart.md` — scored-run walkthrough + re-scoring an old bundle.

## Delivery

Sonnet subagent implements; runs the scored S-001 for real (keel-cloud must carry the
feature-001 fixes first); verification and commits central.
