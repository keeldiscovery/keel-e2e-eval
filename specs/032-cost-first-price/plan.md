# Implementation Plan: marks v12

**Branch**: `032-cost-first-price` (off `master` at `1b08ebd`) | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md)

## Summary

The ruler follows keel-cloud 074 (cost first; merges 075): the registry reader to the cost-first shape, the
corpus to revision 6, the scorers to the two code-framed money questions and `W10`, the brief's cost and
ability figures to keel-cloud's own. v11 bundles are refused.

## Technical Context

**Language/Version**: Python 3.13, pytest; `make unit`; the instruction eval under `instructions/`.
**Testing**: `make unit`; `make instruction-eval DRY=1 MODELS=exported` with `stack.toml` `[paths].keel_cloud`
pointed at the 074 worktree **by absolute path** (and the three other siblings at their absolute checkouts),
reverted before every commit. No model call; no `make instruction-screen` / `instruction-eval` without `DRY=1`.

## Constitution Check

The three named LLM places are untouched; the DRY run spends nothing; `why.py`'s events are unchanged
(`marks:12` is the fifth event's existing shape); the run of record is on hold by the founder. PASS.

## Decisions

1. **Mirror, never re-derive** (as 031). `DimensionRegistry`'s invariants 1–8 are ported from the Java as it
   stands at `5311217`; `Period.recallWords`, `AbilityToPay.band` and `Figures.cost/ability` are mirrored in
   the module that needs them with the Java named. The aggregate still decides refusals (`validate.py`).
2. **The corpus recomputes what it can, and the engine decides the rest.** Ability to pay's ratio and band are
   cheap and are recomputed on load (a disagreeing file is a refusal); Existing sacrifice's and Ability to pay's
   standings are the engine's, diffed by `compare_correctness` — this repo keeps no copy of that arithmetic.
3. **Answered, calibrated, asked.** Three sets read off the registry, none typed: calibrated (12 / 13),
   answered (calibrated less `derived`: 11 / 12; the calibration job and its denominators), asked (per link).
4. **Existing sacrifice stays a set on the respondent side.** `branch_pick_amounts` yields a number
   (invariant 6) but still owes its kinds as options; the scale / gate controls' "options are null" rule stays
   on `segmented_0_to_7`, `number_with_unit` and `gate_yes_no` only.
5. **The judge is untouched.**

## Project Structure

```text
specs/032-cost-first-price/{spec,plan,tasks}.md
instructions/{registry,corpus,context,score,wording,compare,marks,rescore,report,run}.py, marks.toml
tests/fixtures/registry/{slice.yaml, broken/*.yaml}; tests/fixtures/corpus/{09-fixture-r6,10-fixture-r6-b2b}.yaml
tests/test_instruction_registry.py, test_corpus_r6_shape.py, test_instruction_corpus_r6.py,
tests/test_instruction_cost_first.py (new), test_instruction_score.py, test_instruction_brief.py,
tests/test_instruction_marks.py, test_instruction_rescore.py, v9_fixtures.py
AGENTS.md, README.md, Makefile (example list)
```
