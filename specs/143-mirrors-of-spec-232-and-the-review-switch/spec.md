# Spec 143 -- The harness mirrors keel-cloud spec 232, and the cycle runs with the review on

keel-cloud spec 232 (the review changes a founder's row that breaks the card: Current solution rungs rewritten onto the
first rung's measure, Importance rivals reworded into the moment or put aside; the Check says so in one line; the
founder puts a row back; contract 61 -> 62) and keel-web 179 (the band, the changed row, Put back) land behind spec 209's
review switch. Cycle 15 (quality/cycles/20261105-8b28177.md) found that switch OFF in every measured cycle; the founder's
word 2026-11-06: the next cycle runs with it ON. This spec brings the harness to that master and makes the cycle say
which way the switch was.

## Rules

- **FR-1 The switch in the cycle.** The cycle stack already hands keel-cloud the shell's environment (`stack/cloud.py`,
  `env = dict(os.environ)`, as `KEEL_KEELS_AI_EFFORT` rides). `make quality-walk` / the cycle record read
  `KEEL_REVIEW_RESPONDENT_QUESTIONS` from the environment and the record's head line (`quality/cycle.py`, beside
  *routing v…; RUBRIC_VERSION …; reader …*) names it: *review ON* or *review OFF*; the walk's bundle (`backtest.json`)
  records it (`review_switch`); a record whose walks disagree on it is refused as a mixed cycle. The README's cycle
  section says to export it. Nothing turns it on by itself: an unset variable is OFF, as keel-cloud has it.
- **FR-2 The walk leaves a changed row alone.** On a Check that serves `list.changed` / `items[i].typed` /
  `list.put_aside` (contract 62): the walk's strict list checks -- spec 104 FR-1 and 108 FR-2 (the founder's typed rows
  are on the drafted list), spec 064 FR-5a (`founder_rungs`, the leading rungs typed, kept verbatim), the Importance
  typed rows (`importance_typed`) -- count a row present when its `typed` equals the founder's words (the review changed
  it) and a put-aside row present in `put_aside`; the walk never presses Put back and never retypes a changed row; the
  Choose pick stays by label as served (spec 104, the changed words). `backtest.json` records per list
  `review_changed` (`[{typed, label, why}]`, the put-aside rows with `label: null`) and the band's two sentences, so
  the record and the reader can see what the review did. A changed row that fails the walk's own word caps is a
  keel-cloud defect to file, never a retype.
- **FR-3 The reader.** The reader scores the screen as served (the band, the changed rows, the Was lines are on the
  screenshot; R7 reads the rows as served). RUBRIC_VERSION stands; no card of the reader's digest is written here.
- **FR-4 The mirrors.** `quality/readers/dimensions.md` a byte copy of keel-cloud master's `dimension-cards.md` at the
  sha tasks.md names (232 FR-6 amends Importance §2 and Current solution §2), its sha256 equal to keel-cloud's
  `CARDS_SHA256`; every digest pin moves. `instructions/` pins of the read-back shape (if any pin the contract-25 result)
  gain `label` / `drop`. The Palus anchor (232 FR-7, *Think of the {occasion}* where the occasion opens on *last*): a pin
  that expects *Think of your last last …* or builds the anchor itself moves; `instructions/wording.py` mirrors the rule
  if the harness writes anchors.
- **FR-5 Gate.** `make unit` green against keel-cloud master at the sha tasks.md names (anything red today against it
  back to green, nothing else red). No paid runs, no model calls, no corpus change.

## Out of scope

The cycle itself (paid; the founder's word; it exports `KEEL_REVIEW_RESPONDENT_QUESTIONS=true` and its *Why this cycle*
names it); the reader's rubric; the weighted fits score (its own proposal).
