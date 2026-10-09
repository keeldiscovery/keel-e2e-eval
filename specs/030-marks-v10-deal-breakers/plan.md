# Implementation Plan: marks v10

**Branch**: `030-marks-v10-deal-breakers` (off `master` at `2231395`) | **Date**: 2026-10-09 | **Spec**: [spec.md](spec.md)

## Summary

The ruler follows the registry: every count a v9 scorer typed (25, 23, 9 / 9 / 7, 8 / 9 / 6, the
nine deal-breakers, four numeric controls, eight statuses) is replaced by a read of keel-cloud 071's
exported registry and the corpus entry's persona; `no_claim_words` retires with the two statuses it
scored; the corpus is revision 4 from keel-cloud's canon alone; v9 bundles are refused.

## Technical Context

**Language/Version**: Python 3.13, pytest; `make unit`; the instruction eval under `instructions/`.

**Storage**: none; `runs/` is gitignored.

**Testing**: `make unit`; `make instruction-eval DRY=1 MODELS=exported` with `stack.toml`
`[paths].keel_cloud` pointed at the 071 worktree for the run and reverted (absolute path; the
worktree quirk of 2026-10-08).

## Constitution Check

The three named LLM places are untouched; the DRY run spends nothing; `why.py`'s events are
unchanged (`marks:10` is the fifth event's existing shape). PASS.

## Decisions

1. **Counts are read, never typed** (spec US3): `PER_VECTOR`, `PER_PART`, `B2B_ONLY` and
   `DEAL_BREAKERS` remain the schema's fixed expectations for the invariants (the point of an
   invariant is that the file cannot quietly move), but every scorer denominator is computed from
   the loaded registry and the entry's persona.
2. **The fallback corpus directory goes.** keel-cloud's canon has carried the corpus since
   2026-10-08; the cross-track arrangement is over.
3. **v9 bundles are refused, not re-scored**: corpus r4 has no standings for thirteen of the
   dimensions a v9 bundle scored, so a v10 number for it would be fiction.
4. **The judge is untouched.**

## Project Structure

```text
specs/030-marks-v10-deal-breakers/{spec,plan,tasks}.md
instructions/{registry,corpus,brief,marks,rescore,report}.py, marks.toml, and the scorers that count
tests/test_instruction_registry.py, test_corpus_r4_shape.py (from r3), test_instruction_compare.py,
tests/test_instruction_brief.py, test_instruction_marks.py
tests/fixtures/registry/{slice.yaml, broken/*.yaml}; tests/fixtures/corpus-r3/ (deleted)
AGENTS.md, README.md
```
