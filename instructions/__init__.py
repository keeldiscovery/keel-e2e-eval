"""The instruction eval (spec `009-instruction-eval`): does keel-cloud's inference-instruction
prose, sent to a real model exactly as production sends it, produce the measured beliefs the
frozen golden corpus says it should?

**Why this is not in `evals/`.** Everything under `evals/` is a deterministic browser scenario:
keel-runtime answers from its own bundled script, no model is ever called, and `pytest evals`
collects the lot. This package calls a real model, costs real money, needs no stack at all, and is
collected by nothing -- `python -m instructions.run`, through `make instruction-eval`, and never a
dependency of `eval`, `eval-all` or `eval-live`. It reads `evals/policy.py` never and writes it
never; its own rubric is versioned separately as `instructions.marks.MARKS_VERSION`, so an
instruction-eval rubric change can never be mistaken for a scenario-scoring one.

**Why this is not in `harness/`.** `harness/` is the browser scenarios' own machinery -- a step
recorder, a page-object layer, a scoring pipeline for screens a person looked at. The only two
things this package borrows from it are `evidence.new_run_dir` and `evidence.write_versions`, so
an instruction-eval bundle sorts and indexes beside every scenario bundle this repo has ever
written.

**What it never does.** It owns no product code and fixes none: an instruction that cannot reach a
golden belief is a keel-cloud defect, and it goes to `runs/DRIFT.md` with a run bundle, never into
a patch made here. It re-implements nothing either -- the prompt comes from keel-runtime's own
`build_prompt`, the envelope schema from keel-runtime's own validator, the response contract and
every invariant from keel-cloud's own exporter and aggregate. The corpus is read-only, hashed on
the way in and checked again at the end, because the one thing that must never happen to a golden
set is that it quietly moved to make a run green.
"""
