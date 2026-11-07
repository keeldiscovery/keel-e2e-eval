# Spec 145 -- The harness mirrors keel-cloud spec 235 (the ladder rewritten as one scale)

keel-cloud spec 235 (master 1c53c31e carries the spec; tasks.md names the merged sha) changes what the review's read-back
does behind spec 209's switch: Current solution's five rungs are rewritten **as one scale** on the first rung's measure
(whole or not at all, one more review turn inside the Save hold when code refuses a rung, else the notes alone), the band's
first line reads *Keel rewrote the scale so every answer is a step in {measure}.*; an Importance rival that is a part, a
cause or a means of the own row is **put aside**, never reworded. The wire (contract 63) does not change: `items[i].typed`
/ `why`, `list.put_aside`, `list.changed`, `review.interactionId` as spec 144 reads them. Cycle 16
(quality/cycles/20261107-e9de1b8.md) is the baseline this spec's cycle is read against.

## Rules

- **FR-1 The mirrors.** `quality/readers/dimensions.md` a byte copy of keel-cloud master's `dimension-cards.md` at the
  sha tasks.md names (235 FR-6 amends Current solution §2 *The notes* and Importance §2 *The notes under the rows*), its
  sha256 equal to keel-cloud's `CARDS_SHA256`; every digest pin moves (`CARDS_SHA256_141` and the pins that chain to it).
  The mirror fixtures that carry the band's line (`tests/test_cloud_232_mirror_143.py`, `review_band`) gain the new first
  line for a ladder rewritten whole and keep 232's line for the case `measure` was dropped; the record and the reader
  read whatever line is served, as today.
- **FR-2 The record.** The record's review line (143 FR-1, 144 FR-3) says, beside the rows changed and put aside per
  dimension, how many Current solution ladders were rewritten whole (a band whose line opens *Keel rewrote the scale*),
  and the longest `review_holds` hold per dimension (`held_s`), so a second review turn shows in the record without a new
  wire field. A hold that reaches the page's cap stays the DEFECT stop of 144 FR-1.
- **FR-3 The walk.** Nothing new: a rewritten rung counts present by `typed` (143 FR-2), the walk never presses Put back,
  never retypes a changed row, shoots `check-{dim}-reviewed` after the band (144 FR-1). A test pins that a ladder with
  rungs 2-5 all changed (Codyco's five as 235 FR-7 has them) passes the strict rung checks (spec 064 FR-5a) by `typed`.
- **FR-4 Gate.** `make unit` green against keel-cloud master at the sha tasks.md names (anything red today against it back
  to green, nothing else red). No paid runs, no model calls, no corpus change.

## Out of scope

The cycle itself (paid; the founder's word; `export KEEL_REVIEW_RESPONDENT_QUESTIONS=true`, BUILD = the merged cloud sha,
*Why this cycle* names spec 235 and compares against cycle 16: fits 78.0; Current solution 63.9, Importance 55.0);
keel-web (owed nothing by 235).
