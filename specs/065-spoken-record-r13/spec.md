# Spec 065 -- The spoken record follows registry revision 13 (keel-cloud 118 / 123)

`tests/test_instruction_spoken.py::test_the_corpus_record_keeps_every_rule_and_nothing_is_known_apart` is red on
master: 34 faults, every one a change keel-cloud 118 and 123 made on purpose and the eval's record (`instructions/
spoken.py`, the §3 and §5 tables of the spoken-questions guidelines) never followed -- Current solution's escape
(*Someone else did it*, not *Someone else does the checking*), Existing sacrifice's (*I don't know*, not *I can't
recall*), Compatibility's four options to the condition's verb (*Yes, easily; yes, mostly; only sometimes; or no*),
Buyer and payer's four, Commitment's three bands (118). **Scope: keel-e2e-eval only (`instructions/spoken.py`, its
tests, the overview's text if it names the counts); MARKS_VERSION stays; no mark's rule changes -- the record moves
to what the registry says, and the guard keeps guarding it. Build lean: `make unit` once.**

## Rules

- **FR-1 The record reads the registry.** Where §3 / §5 named a fixed count or a fixed escape, the record now reads
  the dimension's served options and escape from keel-cloud's `dimension-registry.json` of record (revision 13, read
  through `instructions/cloud.py` as the test already does) and holds the spoken form to THAT: the count line names
  the served number (*I'll read four options.*), the options line reads the served labels in order with *or* before
  the last, the escape line *Or say {escape}.* with the served escape. A registry change then moves the record and
  the test together; a stem over 20 words, a missing *or*, a count line that disagrees with the options drawn are
  still faults.
- **FR-2 What was on purpose, named.** The test's docstring and `instructions/spoken.py`'s header record the five
  changes above with their specs (118 FR-2 three bands; 123 FR-8 four options to the condition's verb; 123's escapes);
  the `KNOWN` ledger stays empty.
- **FR-3 The guideline of record.** If keel-cloud's `canon/designs/spoken-questions-guidelines.md` still says the old
  counts or escapes, list each line in tasks.md as a finding for keel-cloud (do not edit keel-cloud).
- **FR-4 Tests.** `make unit` green: the red test passes on revision 13 with the real record; a fixture test pins
  that a count line disagreeing with the served options is still a fault.

## Acceptance

1. `make unit` green, including the previously red test; the counts the test asserts (units, clean, spoken_form)
   updated to the record's real numbers, named in tasks.md with the before and after.
2. No mark or version moved.
