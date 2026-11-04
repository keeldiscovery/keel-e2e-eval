# Spec 138 -- Compatibility's suggested row is the founder's own

Cycle 13 (`quality/cycles/20261104-e3e22a8.md`, 2026-11-04): 10-palus' SOLUTION walk stopped at Compatibility --
*the founder's picked item 'could wait one to two business days for their cash' is not on the drafted list (spec 104
FR-1)* -- while Keel's list held that row, capitalised (*Could wait one to two business days for their cash*). The
walk lost its last five screens; the record calls the walk failed.

Why: keel-cloud spec 121 marks ONE of the founder's own Compatibility conditions `suggested` (the one most likely to be
missing, with `suggestedWhy`). Spec 112 FR-2 taught `_founders_rows` (`evals/corpus_scenario.py`) to drop every
`suggested` row as Keel's own, which is true on Adoption friction (keel-cloud 171: Keel's one-time step) and Purchase
friction (Keel's suggested step), never on Compatibility -- there the marked row is the founder's, reworded by Keel's
capital letter alone. With the picked row dropped, spec 108's nearest-row search had nothing to find and the walk
stopped by name. The same walk on 21-codyco passed only because Keel marked a different row.

## Rules

- **FR-1 The founder's rows.** `_founders_rows(question)` drops `suggested` rows on Adoption friction and Purchase
  friction only (`ADOPTION_KEY`, `PURCHASE_FRICTION_KEY`); on Compatibility (`COMPATIBILITY_KEY`) and every other
  dimension every drafted row is the founder's and a typed label may be found near it (spec 108 FR-1). `_choose_label`
  then finds Palus' *could wait one to two business days for their cash* at *Could wait …* with the DRIFT finding of
  spec 081, as 21-codyco's *could forward …* was found in cycle 13, and the walk goes on.
- **FR-2 Keel added, folded.** `keel_added` (spec 104 FR-3) names a drafted row the entry did not type. A row that is
  a typed label once folded (`_folded_words`, spec 108's first tier: case, stops, spacing) is the founder's, never
  *Keel added* -- cycle 13's finding *Compatibility: Keel added: 'Could keep …', 'Could wait …'* on rows the founder
  typed word for word is a false finding and goes. A row that is near but not equal once folded (tiers 2 and 3) stays
  the DRIFT finding of spec 108 and is not *Keel added* either. On Adoption friction the flag rules, as before.
- **FR-3 The pick on a suggested founder row.** Where the entry's typed pick is the row Keel marked `suggested` on
  Compatibility, the pick lands on it (it is the founder's own, word for word or folded); spec 112 FR-2's rule -- the
  pick never lands on a `suggested` row unless typed word for word -- is read as *on Adoption friction*. Purchase
  friction keeps 112's rule (Keel's step is Keel's).
- **FR-4 Tests.** A unit test on `_choose_label` with Palus' three typed rows, Keel's two drafted rows capitalised and
  the second marked `suggested` with a why, on `solution.compatibility`: the pick is row 1 with the DRIFT finding, no
  stop. The same shape on `solution.adoption_friction` with the suggested row Keel's own step: the stop of spec 104
  stands (unchanged). A test on `keel_added`: a capitalised typed row is not Keel's; a new row is.
- **FR-5** `make unit` green against keel-cloud-docs master `e3e22a8d` and keel-web master `d5b117c`. Nothing else
  moves: no corpus revision, no `MARKS_VERSION`, no contract, no reader, nothing paid.
