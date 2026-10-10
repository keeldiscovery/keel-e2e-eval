# Implementation Plan: marks v11

**Branch**: `031-window-frame-and-price` (off `master` at `cc37efb`) | **Date**: 2026-10-09 | **Spec**: [spec.md](spec.md)

## Summary

The ruler follows keel-cloud 072 + 073: the registry reader to thirteen, the corpus to revision 5,
the scorers to the shapes code now writes (an `event` clause, framed questions, Price's ladder, amounts
by unit, two names), and the wording rules the subject only instructs into a report that is never a
mark. v10 bundles are refused.

## Technical Context

**Language/Version**: Python 3.13, pytest; `make unit`; the instruction eval under `instructions/`.

**Storage**: none; `runs/` is gitignored.

**Testing**: `make unit`; `make instruction-eval DRY=1 MODELS=exported` with `stack.toml`
`[paths].keel_cloud` pointed at the 073 worktree **by absolute path** for the run (and the three other
siblings at their absolute checkouts, since a relative path resolves inside the worktree), reverted before
every commit.

## Constitution Check

The three named LLM places are untouched; the DRY run spends nothing; `why.py`'s events are unchanged
(`marks:11` is the fifth event's existing shape); the run of record is on hold by the founder. PASS.

## Decisions

1. **Mirror, never re-derive.** E1–E3, W3, W7, W8 and W9 are keel-cloud's `WindowFrame.fault` and
   `Wording`, ported line for line into one module (`instructions/wording.py`) with the Java source
   named; the ladder is `PriceLadder.bands`. The aggregate still decides the refusals (`validate.py`
   shells it); these copies only let `option_validity` read the accepted answer the way the product
   does, as the v9 checks already mirrored C2–C4.
2. **Names are the corpus's or none** (call 55). The eval never feeds one screen's live output to
   another (marks-v9 §1), and revision 5 records no `short_name` / `offer_name`; the job and the
   validator are handed `null`, so neither W3 nor W8 can refuse — the same rule keel-cloud applies to a
   card confirmed before 072. Recorded as a keel-cloud follow-up (a revision that records both).
3. **The export decides the keys.** The respondent context gains `offer_name` only if keel-cloud's
   `context-keys.json` names it (073's does not; recorded as a keel-cloud follow-up). The calibration
   `interpretation` is a value, so the COMMERCIAL one becomes the persona map keel-cloud writes.
4. **Reported rules are counted in `score.py`'s totals and rendered**, never passed to `judge()`.
5. **The judge is untouched.**

## Project Structure

```text
specs/031-window-frame-and-price/{spec,plan,tasks}.md
instructions/{registry,corpus,context,score,brief,marks,rescore,report,run,validate,contract}.py, marks.toml
instructions/wording.py                                                    # new: the mirrored rules
tests/fixtures/registry/{slice.yaml, broken/*.yaml}; tests/fixtures/corpus/{09-fixture-r5,10-fixture-r5-b2b}.yaml
tests/test_instruction_registry.py, test_corpus_r5_shape.py, test_instruction_corpus_r5.py,
tests/test_instruction_window_frame.py (new), test_instruction_score.py, test_instruction_brief.py,
tests/test_instruction_marks.py, test_instruction_rescore.py, test_instruction_leak.py, v9_fixtures.py
AGENTS.md, README.md, Makefile (example list)
```
