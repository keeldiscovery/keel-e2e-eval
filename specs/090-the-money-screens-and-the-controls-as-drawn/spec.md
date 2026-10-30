# Spec 090 -- The harness walks the money screens as keel-web 134 draws them, and the three controls as keel-web 135 draws them

Two keel-web merges of 2026-10-30 move what the harness clicks and reads on the founder's and the stranger's pages:

- **134** (web master `e5577d2`): the cost box asks the mode first -- three chips *Money they spend* / *Time it takes* /
  *A share they lose* in a radiogroup `chain-modes` under the page's own line `chain-cost-line` (*How would you put the
  cost of {core} to {payer}?*, `lib/costLine.ts`) -- and only once a mode is picked draws the rest: the range, the base,
  *Per* (`chain-unit`, its help line) and the label *How often* (`chain-period-label`) over the period chips, *each*
  drawn as *each time* (the id `chain-period-each` stays; the belief sentence keeps *each*). The price shapes are six
  named choices in one group: *A fixed fee each {period}* (`chain-shape-AMOUNT_PERIOD`), *A percent of {base}*
  (`chain-shape-SHARE`, the COST_BASE share -- **`chain-share-COST_BASE` is gone**), *A percent of what it gets back*
  (`chain-share-RECOVERED`), *One price, then a fee each {period}* (`chain-shape-UPFRONT_THEN`), *One price, then nothing
  more* (`chain-then-nothing`), *Free to them* (`chain-shape-FREE`). A walk that clicks the shape then its second
  outcome still lands (134 J-4). Contract 45 unchanged; the wire unchanged. Where the harness reads today:
  `harness/vectors_screens.py` `CHAIN_COST_HOW` (108), `CHAIN_MODE_WORD` (109, `RATE: "A rate they lose"`),
  `_chain_cost` (1556-1607: reads *Per* and `#chain-unit-help` BEFORE the mode click), `_chain_price` (1609-1626:
  clicks `chain-share-COST_BASE`), and every test that pins those words or that order.
- **135** (web master after its merge): Frequency draws 1..N from the served `scale.min`; Importance is
  `PickOneThenOne` (`data-testid pick-one-then-one`, `data-picks`, `data-first`; the served second ask drawn as
  `p.iv-second[data-testid=second-ask]`; *Nothing else* in `.iv-chips` where *None of these* stood; the AI link plays
  the item's `more` clip after the first tap and sends `ask: second`); Relative advantage is `ScaleFour`
  (`data-testid scale-four`, radio rows named by the question, *I can't tell* apart; `BenefitWithAdvantages` retired).
  Contract 47 vendored. **135's tasks.md lists every selector, role name and word the harness reads that the build
  serves differently** (the builder was asked for that list by name); it is the input to FR-2.

## Rules

- **FR-1 The money screens.** `_chain_cost` clicks the mode first, then reads *Per* and its helper, then fills the
  unit, clicks the period chip, waits for the equation, and reads the base as today; `CHAIN_MODE_WORD["RATE"]` becomes
  *A share they lose*; `CHAIN_COST_HOW` becomes the composed line's shape (the harness reads `chain-cost-line` and holds
  it to *How would you put the cost of ... to ...?* where both parts are served, the shorter forms where not -- never
  the circumstance); the returned frame records the mode-first order (the periods not on the page before the mode).
  `_chain_price` clicks the six choices by 134's ids: SHARE with COST_BASE is `chain-shape-SHARE` alone; RECOVERED is
  `chain-share-RECOVERED`; UPFRONT_THEN then-nothing is `chain-then-nothing`; the locked words read back as today.
  Every founder-walk recording, fixture and test that pins the old words, ids or order is re-pinned with why.
- **FR-2 The three controls as drawn.** Spec 089 walked them to 135's spec; this spec walks them to 135's build: every
  item in 135's tasks.md's harness list is mirrored in `harness/vectors_screens.py`, `harness/interviewer_screens.py`
  and `evals/interviewer_leg.py` (the radio 1..N, the first tap and the `second-ask` line, *Nothing else*, the `more`
  clip, the `scale-four` rows), with the test ids the build serves; nothing hard-codes a label code can change.
- **FR-3 Nothing else moves.** The marks, the corpus (revision 19), the readers, the quality cycle's rubric, the
  prices (088), the frames (089 FR-5).

## Acceptance

`make unit` green with ZERO failed (master's counts as 089's tasks.md and the 2026-10-30 handoff record them: 3,776
passed / 55 skipped on the live cloud); then on the local stack at keel-cloud `ad5f6441` and keel-web at 135's merge:
`make eval K=s005`, `K=s006`, `K=s007` green with the three controls walked, and `K=s012` green with 088's Begin and
INACTIVE assertions now on (WEB_131_BUILT). Build after web 135 merges (one builder at a time). Build on the founder's
word (the overnight run of 2026-10-29).
