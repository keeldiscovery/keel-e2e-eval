"""Referee tooling that is **not** a scenario.

A module in `evals/` is normally a pytest scenario: it asserts an entry's own `expected` section
and its verdict is the finding. What lives here is the other thing a referee sometimes needs --
a run driven for its *artefacts* rather than for its assertions. `curated_proof_run` is the first:
it walks `07-mulchrun` end to end against a **real** model and hands back two screenshots, and it
deliberately asserts nothing about what the model concluded, because a real model is allowed to
disagree with the corpus and that is the whole point of shooting the frame from it.

Nothing here is collected by `make eval`/`make eval-all` (no `test_` prefix, no pytest fixtures),
and nothing here may be imported by a scenario: a tool that a scenario depended on would be
machinery, and machinery belongs in `harness/`.
"""
