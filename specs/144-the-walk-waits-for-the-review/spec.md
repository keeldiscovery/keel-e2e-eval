# Spec 144 -- The walk waits for the review and shoots the Check after the band

keel-cloud 233 and keel-web 180: on Importance, Current solution and Compatibility the Save of the Check holds (*Keel is
reading your answers*) until the review lands; when a row changed the Check stays with the band, Was and Put back and the
button reads Continue; Compatibility's list saves before the pick and its rows come back changed the same way. Spec 143's
founder screenshot was taken before Save, so the readers never saw the review's work on the founder's screens; this spec
fixes that for the cycle the founder ordered (2026-11-06: *"run one more cycle and see how the score has come"*).

## Rules

- **FR-1 The walk waits.** On those three Checks the walk presses Save and waits for the button to leave the reading
  state (the `calib__drafting` status; a cap of 90 s, then a `DEFECT (keel-cloud 233)` finding and the walk stops by
  name). When the Check stays with the band (`list-changed`), the walk takes a **second founder screenshot** of that Check
  (`…-check-reviewed`, scored as a screen with the dimension card like the first) and presses Continue; it never presses
  Put back and never edits after the hold (143 FR-2). When the page moved on, nothing more is read.
- **FR-2 Compatibility.** The strict Compatibility checks (spec 104 FR-1, 108 FR-2) count a row present when its `typed`
  equals the founder's words, or a put-aside row's `typed` does (143 FR-2's rule, now on Compatibility); the Choose pick
  is by label as served; a pick the walk planned on a row now put aside falls to the first founder row still on the list
  (recorded in `backtest.json`); `review_changed` / `band` recorded per list as 143 does; a changed row over the cap is
  a `DEFECT (keel-cloud 233)` finding, never a retype.
- **FR-3 The record.** The record's review line (143 FR-1) counts the three dimensions and names the second screenshots;
  the per-dimension fits table (`make read-table`) folds `…-check-reviewed` screens into their dimension. RUBRIC_VERSION
  stands; the readers' prompts are untouched.
- **FR-4 The mirrors.** `quality/readers/dimensions.md` a byte copy at the sha tasks.md names, `CARDS_SHA256` moved; the
  contract pin 62 -> 63 (`SavedListDto` with the Save answer's `review`; the Compatibility list without a pick).
- **FR-5 Gate.** `make unit` green against keel-cloud master at that sha; no paid runs, no model calls, no corpus change.

## Out of scope

The cycle itself (paid; it runs after this merges, with `KEEL_REVIEW_RESPONDENT_QUESTIONS=true` exported and its *Why*
naming it); the rubric.
