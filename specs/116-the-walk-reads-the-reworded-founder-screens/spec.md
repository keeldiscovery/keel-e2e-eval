# Spec 116 -- The walk reads the reworded founder screens of keel-web 149 and 150

keel-web 149 (merged 2026-10-31, buyer and payer's Choose) and 150 (building: current solution asks twice) move words and
controls the harness reads; their tasks.md name every id. Cycle 4 cannot walk the money and problem studies until the
walk reads them.

## Rules

- **FR-1 Buyer and payer's Choose (149).** `harness/vectors_screens.py` `choose`: `seen["prompt"]` (`.listcheck__title`) is
  *Which one do you want to test?* on this dimension; `seen["options"]` lists the roles first and *Nobody else* **last**,
  so an index taken from `options` is no longer the served `pickedIndex` -- the walk picks by label (104) and records the
  served index from the wire, never from the list's position; `test["bar"]` / `test_before["bar"]` read the three cases
  (*… say the one you pick had to agree …* before a pick; *… say {role} had to agree the last time they bought
  {offer_name}.*; *… say nobody else had to agree …*); new `[data-testid=choose-recall]` and `[data-testid=choose-belief]`
  recorded; the old *they had to agree last time* / *decided on their own* pins moved with why.
- **FR-2 Current solution's two boxes (150).** The answer step types the corpus Answer into the **first** box as 150's
  tasks.md says (whole, or split at its first full stop -- the builder reads 150's tasks.md on keel-web master and
  follows it); the second box typed where the corpus Answer carries a second sentence; the PUT body is today's one text,
  asserted; the question read as *How do {actor_plural} {job} today?*; the `answer` founder screen of record carries both
  boxes' text.
- **FR-3 The pilot screen and the gate** are already read (114, 148: no change); the AI link's heard line (099) and the
  money screener (100) likewise. Nothing else moves.
- **FR-4 Tests.** `tests/test_reworded_founder_screens_116.py`: the Choose order and bar cases on a stand-in page; the
  two boxes and the join; the record. `make unit` ZERO failed (master's counts as 109's tasks.md records them).

## Acceptance

`make unit` ZERO failed. Build after 109, before 095 (and before cycle 4). One builder at a time in this repo.
