# Plan 138 -- Compatibility's suggested row is the founder's own

Branch `spec-138` (worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-138`, `.git` a file), off the spec's
commit on master. Read only: keel-cloud-docs master `e3e22a8d` (`SavedList.java` -- spec 121's `suggested` on
Compatibility; `VectorDtos.java`; spec 171's Adoption friction step; spec 205/214's Purchase friction step) and this
repo's `evals/corpus_scenario.py` (`_founders_rows`, `_choose_label`, `keel_added`, `keel_left_out`, `keel_unmarked`,
`nearest_rows`, `_folded_words`), `specs/104`, `108`, `112`. No stack, no model, no walk, no paid call, no key read; the
unit suite only.

| FR | Where |
|---|---|
| FR-1 | `evals/corpus_scenario._founders_rows`: the drop of `suggested` rows gated on `question["dimension"] in (ADOPTION_KEY, PURCHASE_FRICTION_KEY)`; its docstring says why (121 vs 171). |
| FR-2 | `evals/corpus_scenario.keel_added`: on every dimension but Adoption friction, a drafted row is *added* only where no typed label equals it folded and `nearest_rows` of no typed label returns it; the `Compatibility: Keel added:` finding in `vectors_script` / `backtest` follows. |
| FR-3 | `_choose_label`: the `flagged` skip (`not flagged[i]`) applies on Adoption friction and Purchase friction; on Compatibility the first equal row is the pick. |
| FR-4 | `tests/test_spec_138_compat_suggested.py`. |
