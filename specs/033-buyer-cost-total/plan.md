# Implementation Plan: marks v13

**Branch**: `033-buyer-cost-total` (off `master` at `495b06f`) | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md)

## Summary

The ruler follows keel-cloud 077: the registry reader to `cost_total`, the corpus to revision 7, the scorers
to a code-written Existing sacrifice on both screens (no W10, no U1), the brief's time-only figure to `HOURS`
totals. v12 bundles are refused.

## Technical Context

Python 3.13, pytest; `make unit`; `make instruction-eval DRY=1 MODELS=exported` with `stack.toml` `[paths].keel_cloud`
pointed at the 077 worktree by absolute path (and the three siblings at their absolute checkouts), reverted before
every commit. No model call; no run without `DRY=1`.

## Constitution Check

The three named LLM places are untouched; the DRY run spends nothing; `why.py`'s events are unchanged; no run of
record. PASS.

## Decisions

1. **Existing sacrifice joins Price as code's whole** (call 67). `CODE_WRITTEN_RESPONDENT_CONTROLS` gains
   `cost_total`; the calibration side shares Price's C2 branch. Nothing is added to the option-validity code that
   v12 needed for the kinds: it is deleted.
2. **The registry refuses v12's shape** (call 69): a `code_rule` on the cost, or a respondent control other than
   `cost_total`, is an invariant-5 fault; `branch_pick_amounts` is not number-yielding, so invariant 6 fails too.
3. **The corpus collapses nothing here** (call 68): revision 7 is read as keel-cloud wrote it; an `amounts` pick,
   a `labels`/`units` entry or an `optionCounts` row on Existing sacrifice is a refusal by key.
4. **Mirror, never re-derive.** The engine decides the standings (`compare_correctness` diffs them); the figures
   that the brief quotes are keel-cloud's `Figures.cost`, with the time-only people now the `HOURS` picks.

## Project Structure

```text
specs/033-buyer-cost-total/{spec,plan,tasks}.md
instructions/{registry,corpus,context,score,wording,marks,rescore}.py, marks.toml
tests/fixtures/registry/{slice.yaml, broken/5-cost-kinds.yaml}; tests/fixtures/corpus/{09-fixture-r7,10-fixture-r7-b2b}.yaml
tests/test_instruction_*.py, tests/test_corpus_r7_shape.py, tests/test_instruction_corpus_r7.py, tests/v9_fixtures.py
AGENTS.md, README.md, Makefile (example list)
```
