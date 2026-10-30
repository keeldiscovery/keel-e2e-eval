# Spec 104 -- Choose picks the founder's own row, found by its label

The re-walk of 2026-10-30 (21-codyco · SOLUTION, `runs/20261030T183150Z-backtest-21-codyco`; 17-expanse and 08-fresco
the same): the entry's adoption-friction answer types two efforts and `pickedIndex 0` names the first of them (*Let an
AI answer guests in the hotel's voice*). Keel's list writer prepends a setup step the founder did not type (*Forward
unanswered calls to Codyco*, *Connect it to their SLURM or Kubernetes cluster*, *Connect it to Procore or ACC*), so the
drafted list's row 0 is Keel's, not the founder's. `evals/corpus_scenario.py` (~:1630, *the one item Choose picks: the
entry's own, read off the drafted list*) applies the entry's index to the **drafted** list and picks Keel's row; the
stranger is then asked about forwarding, and cycle 3's reader (R5 0 on the choose screen, *"my step is the AI voice but
the screen will test forwarding"*) scored a pick no founder made. The founder, 2026-10-30, named this cluster rank 6 of
the top ten; a third of it is this bug.

## Rules

- **FR-1 By label.** `pickedIndex` indexes the entry's **typed** items (`list.items` in the corpus answer). Choose picks
  the drafted row whose label equals that item's label (the drafted list keeps the founder's labels word for word,
  spec 081); where the drafted list has no row with that label the walk stops by name (`VectorsScriptError`: the
  founder's picked effort is not on the drafted list) -- never a silent fall-back to row 0.
- **FR-2 Every picked dimension.** The same rule for every `PICKED` dimension (`vs.PICKED`): compatibility, adoption
  friction, buyer/payer alignment, purchase friction -- wherever Keel may draft rows of its own beside the founder's.
- **FR-3 The added rows are named.** Where the drafted list carries rows the entry did not type, one finding per
  dimension lists them (*Keel added: 'Forward unanswered calls to Codyco', 'Connect Codyco to the hotel's PMS'*), so the
  record shows what the product invented; no fault, the judge reads it.
- **FR-4 Tests.** `tests/test_choose_by_label_104.py`: the drafted list with two prepended rows picks the founder's
  label; a list in the founder's order picks the same row as before; a missing label refuses by name; FR-3's finding;
  the 21-codyco fixture. `make unit` ZERO failed (master's counts as 103's tasks.md records them, 4,077 / 0 / 53).

## Acceptance

`make unit` ZERO failed. The paid re-walk of 21-codyco · SOLUTION is the coordinator's, on the founder's word. Build
now; one builder at a time.
