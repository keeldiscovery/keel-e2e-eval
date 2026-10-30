# Spec 108 -- A reworded founder row is picked by its nearest label and named as a drift, not a stop

Spec 104 (merged 2026-10-30) picks the founder's own row on Choose by its exact label and stops by name where the drafted
list has no such row. 104's builder found that Keel's list writer sometimes rewords the founder's label -- the tense on
21-codyco's compatibility rows (*could be forwarded* -> *can be*), 13-aircaps's adoption step (*Wear the glasses, paired
to the phone* -> *Pair the glasses to their phone*), 08-fresco's purchase step not drafted at all -- against spec 081's
word-for-word rule, so three of the day's thirty Choose screens would now stop the walk before the reader scores the
rest. The rule stays the product's (keel-cloud owes a founder-lists fix: a founder's row is kept as typed); the harness
must finish the walk and say what it saw.

## Rules

- **FR-1 The nearest row.** Where no drafted row's label equals the typed label, `_choose_label` picks the one drafted
  row that is nearest to it -- the same words after lowercasing, punctuation and the inflections *-s/-ed/-ing* and
  *could/can/would/will* folded, or one that contains every content word of the typed label -- when exactly one row is
  that near; it writes one finding **DRIFT: Keel reworded the founder's row '{typed}' as '{drafted}' (spec 081)** and
  walks on with the drafted label. Where no row or more than one is that near, the stop of 104 stands, by name.
- **FR-2 A row not drafted at all** (08-fresco's *A trial on one live job*) is the same stop as today; the finding names
  the typed rows the draft left out, beside 104's *Keel added* finding.
- **FR-3 `runs/DRIFT.md`** gains one entry naming the three cases of 2026-10-30 as a product fault for keel-cloud
  (founder-lists.md: a founder's row kept as typed, tense and all), owed as a cloud spec; the quality record's findings
  carry the DRIFT lines so the next cycle counts them.
- **FR-4 Tests.** The three cases as fixtures: the tense fold picks the row and writes the DRIFT line; the aircaps
  rewording picks by content words; the fresco missing row stops; two near rows stop. `make unit` ZERO failed (master's
  counts as 105's tasks.md records them).

## Acceptance

`make unit` ZERO failed. Build after 107, before 097; one builder at a time in this repo.
