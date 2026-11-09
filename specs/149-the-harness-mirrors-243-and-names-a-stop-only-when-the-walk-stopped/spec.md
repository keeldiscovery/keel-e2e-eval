# Spec 149 -- The harness mirrors keel-cloud 243 and keel-web 184, and names a stop only when the walk stopped

Two things from cycle 19 (`quality/cycles/20261109-76c633d.md`) and the founder's staging find of 2026-11-09.

**The read-back's rows.** keel-cloud 243: every read-back hands numbered rows (`[{index, label}]` from 0, the own row
0), reads a 1-based answer (indices 1..count) by shifting it and notes `review.shift: 1`, and suggests a row in place of
every row it puts aside on Importance, Relative advantage and Compatibility (`notes[i].suggest {label, why}`; the item
carries `inPlaceOf`, the put-aside `replacedBy`; the band counts both). keel-web 184 draws one pattern: *Reworded from*,
*In place of*, *Keel's suggestion*, one record list tagged *yours* / *Keel's draft*, Put back on Keel's row, no *Was*.

**The record's stops.** Cycle 19 listed `08-fresco · PROBLEM` and `17-expanse · PROBLEM` as *stopped early -- no step
named (stopped outside a step)*. Both walks reached their end and were scored; what they had was E9 refusals of Keel's
AI at the calibration, retried as the founder's screen retries (spec 148 FR-2's `gate_refusals`, all `stopped: false`).
A refusal that was retried is a finding, never a stop; `stopped` names only a walk that did not reach its end.

## Rules

- **FR-1 The digest and the contract.** `quality/readers/dimensions.md` byte for byte at 243's merged sha; the digest pin
  chain moved; the contract pins (x-keel-contract as 243 moves it) and `CONTRACT_VERSION` per its tasks.md.
- **FR-2 The read-back mirror.** The fake runtime's read-back context hands numbered rows on all three; its answer may
  be 0- or 1-based and the mirror reads both as the cloud does (`review.shift`); a put-aside carries `replacedBy`, a
  Keel row `inPlaceOf`; the band regex counts both.
- **FR-3 The walk.** The walk reads the Check as 184 draws it: the Keel row's line (*Reworded from* / *In place of* /
  *Keel's suggestion*), the record list's tags, one Put back per changed row (never pressed), no *Was*. On Choose a
  suggested row is Keel's as spec 147 has it. `review_picks` and `lists_reviewed` record `inPlaceOf` / `replacedBy`.
- **FR-4 The regression shape, at this layer.** The staging shape of 2026-11-09 (own row + three, a 1-based answer with
  three distinct reasons) is a named test of the mirror AND an assertion in the scripted Importance journey (S-0xx that
  walks an Importance Check): the right rows are struck, each reason on its own row, a Keel row in each place.
- **FR-5 Stops.** `quality/cycle.py` / `evals/backtest.py`: a walk is *stopped early* only when it did not reach its end
  (`stop_rule`, a product stop, a harness stop); a retried refusal is counted on the gate line alone. Cycle 19's record
  re-read gives *15 of 15 reached their end* with 5 refusals; a unit test pins it on the two bundles' json.
- **FR-6 The record.** The review line cites 243; a *suggested in place* count joins the review line.
- **FR-7 Tests.** `make unit` green at the head; the new pins named for what they guard.

## Out of scope

Any paid run (the nine are suspended on the founder's word until the account switch); keel-cloud and keel-web code.
