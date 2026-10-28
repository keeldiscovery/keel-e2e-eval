# Spec 080 -- The harness reads corpus revision 17 (keel-cloud 147)

keel-cloud 147 cuts corpus revision 17: 02-compliancelog's `commercial.buyer_payer_alignment` from PEOPLE_DISAGREE /
BOTH / 5 of 9 to HOLDING_UP / NONE / 7 of 9 under 145's direction-aware rule; every other entry moves by its revision
line alone; no verdict moves. This is spec 068's shape (revision 16) one number on: stackless, the eval's own diff,
the cloud's checker. Today `tests/test_report_marks.py::...corpus_overview_on_all_seven_entries` is red on master
(48 of 49) because the cloud's fresh `build/brief-facts/` already serves the 7 of 9 lead; this spec makes it green by
pinning what revision 17 records. Build after keel-cloud 147 is merged (the coordinator names its sha).

## Rules

- **FR-1 `REVISION = 17`** in `instructions/corpus.py`, with the revision-16 note kept and a revision-17 note (the one
  row, 145 FR-2, 147); a file at 16 is refused by name, as 15 is today.
- **FR-2 Rule D17**, the eval's own diff (`tests/test_corpus_r17.py`, 068's D16 one on): every entry read beside its
  revision-16 record (keel-cloud's `corpus-r16/` and `backtest-r16/` mirrors where they exist), every leaf difference
  one of 147's edits -- the revision line everywhere, and on 02-compliancelog the one standings row (status, drift,
  inside). The cloud's checker `sim/check_corpus_r17.py` prints OK on all 35. Rule Q still holds.
- **FR-3 The pins.** The corpus-overview pin (02-compliancelog's COMMERCIAL panel: *Buyer and payer · 7 of 9 the HR
  director had to agree, or they decided alone*, the pill as the engine says), the brief-facts DRY compare (076's
  107-of-108 / 100-of-101 pins become all agreed, the "one disagreement" wording retired), the zero-spend compare
  (108 of 108), the marks header's seven r17 digests (`MARKS_VERSION` 21 stands: the ruler did not move, the record
  did), `tests/fixtures/corpus/*-r17` if 068 made r16 fixtures. Every pin that names revision 16's 5 of 9 moves, listed
  in tasks.md with why.
- **FR-4 Nothing else moves.** The journeys (their scripted answers are the harness's, not the corpus's standings),
  the readers, the quality cycle, the noise check, the golden readings of every other row.

## Acceptance

`make unit` green with ZERO failed (master at 078/079's merge: 3,590 passed / 1 failed / 53 skipped -- the one red
is this spec's subject); `tests/test_corpus_r17.py` on the cloud checkout at 147's merge; the DRY instruction eval
(`make instruction-screen DRY=1 K=02-compliancelog`) shows `compare_correctness` and `brief_facts` measured and
agreed. tasks.md in 077's shape. No paid command.
