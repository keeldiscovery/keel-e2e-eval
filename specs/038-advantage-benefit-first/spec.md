# Spec 038 -- Relative advantage, benefit first (marks v17)

Sibling of keel-cloud 085 (merged at b8a4eed; `DimensionRegistry.VERSION` 2 -> 3, document 17 -> 18, `CONTRACT_VERSION`
stays 10). The 035 chat work stays reverted; nothing of it returns.

- FR-001 Corpus revision 9 only (canon, mirrored in keel-cloud `corpus-r9/`, checked by `sim/check_corpus_r9.py` rule B).
  A revision-8 file is refused by name (`corpus._REVISION_OF[8]`). Relative advantage: founder `answer` is a list of 1-4
  distinct advantages; plan row `benefit_with_advantages` over `[positive, neutral, negative]`; a pick is
  `{answer, advantages}` (advantages a non-empty subset of the ticks exactly under `positive`) or a chip
  (`corpus._check_benefit_first`, shape half; counts are the engine's). No status/count/verdict moved; drifts did:
  02-compliancelog both, 04-linerly and 06-repeatline short.
- FR-002 The respondent RA item is code-written (`registry.CODE_WRITTEN_RESPONDENT_CONTROLS` gains
  `benefit_with_advantages`): the model's item is `{"key"}` alone; no question, options, W3/W7/W9 or sweep for it. The
  founder side is unchanged and still the model's, so `score.model_text` / `is_swept` read the control only when
  `founder=False`. Invariant 5 gains: `benefit_first` iff `benefit_with_advantages`, and its founder control is
  `multi_choice`.
- FR-003 `BriefFacts.solution.benefit {better, noDifference, worse, n}` (`brief_facts.benefit`), counted off the picks of
  the people the engine counts and held to the standing's `n`.
- FR-004 MARKS_VERSION 16 -> 17 (call 76): the marks' meaning moved (a model-written RA respondent item is no longer
  scored; sweep B 63 -> 56 at N=1, 109 -> 102 sweeps; compare expects three new drifts; corpus r9). No threshold moved.
- FR-005 `rescore.py` refuses every bundle below 17.
- SC `make unit` green with the same 75 skips; `DRY=1` against b8a4eed compare 108/108. No live call; no run of record.
