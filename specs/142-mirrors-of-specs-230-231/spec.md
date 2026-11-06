# Spec 142 -- The harness mirrors keel-cloud specs 230 and 231

keel-cloud specs 230 (a Compatibility redraft keeps the founder's rows; a blank optional face is absent; a refused
redraft reads FAILED, never an older draft) and 231 (an E8 moment-shape fault is served with a note past the repair
turn; the Prevalence card amended) are merged on keel-cloud master (231 at 21b896f9, 230 merged after it). Cycle 15's
two product stops were theirs. This spec brings the harness to that master before the re-walk of 08-fresco SOLUTION
and 10-palus PROBLEM.

## Rules

- **FR-1 The reader digest.** `quality/readers/dimensions.md` is a byte copy of keel-cloud master's
  `src/main/resources/keel/dimension-cards.md` at the sha tasks.md names; its sha256 equals keel-cloud's
  `CARDS_SHA256` (spec 231's tasks.md: `06fcd867…`); the pin `CARDS_SHA256_141` (and any other digest pin) moves.
- **FR-2 E8's messages (231).** `instructions/wording.py` `packed_fault` mirrors the two changed messages (the state
  words and the head verb of state now end on `WindowFrame.leftStanding(unit)`'s tail and use the window's unit);
  the pin in `test_a_head_verb_of_state_is_refused` moves. No harness pin expects an E8 to end `RESULT_INVALID`; if
  one does, it expects the note (`breach result.questions[0].event: E8: …`) and a served clause.
- **FR-3 Spec 230.** The walk's strict Compatibility check (spec 104 FR-1, 108 FR-2) stands: the founder's typed rows
  are on the drafted list. A redraft that fails reads FAILED and the harness's retry path (spec 062) applies, as it
  did for Palus; nothing new is read. tasks.md says what was checked and found already true.
- **FR-4 Gate.** `make unit` green against keel-cloud master at the sha tasks.md names (the tests red today against
  it -- `test_cloud_213_mirror_137.py`, `test_cloud_211_mirror_133.py`, the 141 digest pin -- back to green, nothing
  else red). No paid runs, no model calls, no corpus change, RUBRIC_VERSION stands.

## Out of scope

The reader's rubric; the cycle record; the re-walk itself.
