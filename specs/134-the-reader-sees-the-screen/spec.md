# Spec 134 -- The reader judges what the screen showed; the corpus rungs fit the card

The founder, 2026-11-04: "we need to fix the harness." Cycle 11 (quality/cycles/20261104-e485abe.md) scored 14
screens 0 on R7; eight of them were the harness's, not Keel's (the page of record: cycle11-misses, 2026-11-04).

## Rules

- **FR-1 The read-back is the screen's.** `evals/backtest.py` `read_back`: on an Answer and a Check screen the reader
  gets the belief the screen drew (`belief line on screen`, `keel will test`, `bar` from the camera's `test` /
  `test_after`) and never the wire's row `belief`, which is read after the walk and carries what the founder typed on
  later screens (purchase friction's time, typed on Choose, reached the Answer and Check reads on Fresco, Palus and
  Codyco: six zeros). On a Choose and a `q` screen the wire's belief stays, as today.
- **FR-2 Rows are rows.** `harness/vectors_screens.py` `_list_rows`: the Check screen's guidance line (keel-web's
  note under purchase friction's list, *Your own offer … stays off this list*, and any `.listcheck__note`) is captured
  as `note`, never as a row; the reader's screen text keeps it, labelled.
- **FR-3 The Check screen is judged after the founder's edit.** Where `list_check` typed rungs over or added rungs
  (spec 067 FR-2, `rungs_edited` / `rungs`), the founder screen record carries the rows, the *Keel will test* box and
  the screenshot from after the edit (`after`, `test_after`, the `-saved` shot) and `founder_did` says *typed {n} of
  their own rungs over Keel's draft, then saved* -- never the hard-coded *saved as Keel drafted it* (`backtest.py`
  `founder_did`, the `check` branch). The reader's prompt names the rows as the founder's. `list_check`'s step name
  and docstring say what it does.
- **FR-4 The corpus rungs fit the card.** The five entries' Current solution rungs (the walk's own words, typed on the
  Check screen and served to strangers) are reworded against the card: one measure, the working rung first, outright
  failure last, no rung joining two states, the stem's occasion matching the options -- Fresco (time to get the day's
  photos and notes into the log), Palus (what the cash earned after fees, one measure), Aircaps (how much was followed,
  no *and*), Expanse (how the request turned out, no method), Codyco (the shift, matching the stem). The readers'
  proposed rungs in the cycle 11 score files (`instead`) are the starting point; the entries' other words do not move.
- **FR-5 Nothing else moves**; the readers' prompts, rubric 5 and the cards are unchanged by this spec (the one-clause
  rule of keel-cloud 212 is the next eval spec's, with the mirrors). `make unit` green; a dry walk of one entry
  (`BUILD` any) shows the new read-back on a Check screen.
