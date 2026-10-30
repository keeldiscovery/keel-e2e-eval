# Spec 096 -- Three stops of the quality walk that were the harness's: the idea-card edit in the money study, the cost step's rate read before it is typed, the decision-maker's line named

Cycle 3's walk (2026-10-30, cloud `fcec4533`, web `78c012f`, eval `9cbbd45`) stopped three studies early, each the same
stop cycle 2 had (`quality/cycles/20261028-f48f256.md` line 10). Two are the harness's, one is keel-cloud's with a
mirror owed here:

1. **10-palus · COMMERCIAL** (`runs/20261030T144756Z-backtest-10-palus`, cycle 2's 10-palus and 21-codyco COMMERCIAL
   the same): after a refused lock `vectors_screens.edit_idea_lines` (`:2082`) waits for `/define/solution/q/\d+$`,
   but the money-only study's *Your idea* Save goes on to who decides (`/define/persona`, keel-web 109 FR-3,
   `IdeaCheck.tsx:170`); 30 s timeout, the walk stops.
2. **08-fresco · COMMERCIAL** (`runs/20261030T142020Z-backtest-08-fresco`, cycle 2 the same): the chain screen types
   the entry's own rate (55) into `chain-rate` and saves (`vectors_screens.py:1706-1709`); then
   `_hold_the_cost_fill` (`corpus_scenario.py:2071-2104`) reads the view **after** that save (`hourlyRate {55,
   defaulted:false}`) and compares it with what was **drawn before typing** (80, Keel's USD default for the role, with
   its note) -- `assert float(filled["rate"]) == float(rate)` fails on (80, 55). The screen was right both times; the
   check reads the wrong moment.
3. **10-palus · SOLUTION** (`runs/20261030T143848Z-backtest-10-palus`, cycle 2's 21-codyco SOLUTION the same): the
   lock refused on the decision-maker's line, announced as *the how line*; keel-cloud 165 reads that line only where
   money is in scope and names it *the idea card's decision-maker's how line* when it refuses on it. `lock_refusal`
   (`corpus_scenario.py:2276-2296`) reads only `(how|belief)` and `LOCK_EDITS["how"]` edits both lines.

## Rules

- **FR-1 The edit lands on the scope's next screen.** `edit_idea_lines` waits for `/define/solution/q/\d+$` **or**
  `/define/persona$` and returns which (`landed`); the step's name says the money study goes to who decides. The
  journey's relock is unchanged.
- **FR-2 The cost step reads the rate as drawn.** The chain screen records, before it types anything into
  `chain-rate`, the rate drawn and whether the note was drawn (it already returns `filled`); `_hold_the_cost_fill`
  holds the drawn rate to the view **as it was before the screen's own save** -- the leg reads
  `GET calibration/COMMERCIAL` once before the screen walk and passes that `hourlyRate` in (`defaulted: true`,
  Keel's default for the market and the role -- `HourlyRates.defaultFor`, 80 for USD's first tier) -- and asserts the
  note is drawn iff `defaulted`. The entry's own rate is a second, separate assertion after the save: the view's
  `hourlyRate.amount` equals the entry's (55) with `defaulted: false`. The `order` checks (the rate under the hours
  row, above what the time goes on) stay as they are.
- **FR-3 The decision-maker's line is named.** `_LOCK_LINE` reads *the idea card's (decision-maker's how|how|belief)
  line* and `lock_refusal` returns `line: "howDecider"` for the first; `LOCK_EDITS` gains `"howDecider":
  ("howDecider",)` and `"how"` edits `how` alone (the cloud now names each); `edit_idea_lines` already types the
  decider's box where it is drawn (`IDEA_BOXES`). Where the box is not drawn (a solution-only study) the cloud no longer
  reads the line (165 FR-1), so no edit is owed; a refusal that still names a line the card does not draw is the
  stop it is today, with the line named.
- **FR-4 Nothing else moves.** `plain_line`, the M5 word list mirror, the other journeys' lock paths, the quality
  readers, the marks.

## Acceptance

`make unit` green with ZERO failed (master's counts as 094's tasks.md records them: 3,970 / 0 / 53); then, on the local
stack at keel-cloud 165 or later and web `78c012f`, `make quality-walk ENTRIES=10-palus,08-fresco
SCOPES=SOLUTION,COMMERCIAL DOOR=host WHY="eval 096 + cloud 165: the three stops"` reaches the end of all four walks (the
coordinator runs it, paid, on the founder's word). Build on the founder's word of 2026-10-30 (*"let the walk complete..
then lets proceed with the fix"*), after the cycle 3 walk has left the machine and after cloud 165 merges (FR-1 and
FR-2 can go first; tasks.md says which).
