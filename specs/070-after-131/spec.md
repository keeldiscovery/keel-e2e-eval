# Spec 070 -- The harness after keel-cloud 131

keel-cloud 131 (keel-cloud-docs master after `2531ac86`, contract still 37, corpus r16) changed the lock and the served words
the harness mirrors. The re-runs of the eight held entries (08-fresco, 10-palus, 13-aircaps, 14-code-four, 15-voltair,
16-pairio, 20-lemma, 21-codyco) are the parent's; this spec makes them possible and keeps the golden journeys green.

## Rules

- **FR-1 A refused lock is answered, not a stop.** 131 FR-5: the lock answers `TEXT_REFUSED` (422) when the idea card still
  carries an M5 word or a design-note belief after its repair turn (Codyco's *PMS (OPERA Cloud, Sihot, Apaleo)*, Transload's
  *3D box*, Voltair's *use cheap charging pads along the lines*, Issen's *adapt to …*, Pairio's product names, Palus's bond
  phrase, Code Four's *check words*). On a back-test the founder simulation reads the refusal's `problem` and `fix`, edits the
  idea card's line the way a founder would -- the named word replaced by the entry's own plain phrase where the entry has one
  (a small per-entry map in the corpus loader: *PMS* → *the hotel's booking system*, *3D box* → *measures the freight from the
  video*, *check words* → *a few planted mistakes to catch*, a parenthesised list of names dropped, a design-note belief
  replaced by the entry's first benefit) -- locks again, and records the refusal and the edit as a finding (`lock_refused`,
  with the words before and after). A second refusal on the same line stops with the words named. Golden walks never meet
  it (unit test: no golden reveal trips M5; the lock on the golden seven is 200).
- **FR-2 The spoken mirror follows 131.** Importance's follow-up text is its spoken line; the Compatibility follow-ups are
  spoken as they read on every path (ability, fact, partly, no; no *couldn't be allowed*, no possessive slip); the Buyer set's
  third option *No, several people would have to agree* when the party is named; Frequency under 20 with a cut gate clause;
  the Adoption frame whole (every verb in -ing; a step stored as a question); *per pole* with no *, each*; the price card's
  benefits as the founder wrote them (no *your {people} get*); the gate's fallback on an organisation- or thing-subject
  circumstance (*did you decide where cash from a raise would sit?*, *did a machine on your line go down?*) and on a
  failure-event occasion (*did your agent in production start failing on real inputs?*).
- **FR-3 The report_insights mark reads 130's fear-held head.** `evals/report_marks.py` expects *Not the blocker you expected.
  What did slow it down?* over a Purchase-friction fear that held (S-014 went red on it).
- **FR-4 Nothing else moves.** REVISION 16, marks v20, contract 37; the golden numbers unchanged.

## Acceptance

1. Unit suite green.
2. S-005, S-006, S-007 and S-014 green on the local stack with the fake interviewer (the parent runs them; the builder runs
   them only if `pgrep -fi "[p]ython -m pytest evals"` and the back-test runner are both idle, and tears the stack down after).
3. `make backtest DOOR=host ENTRY=21-codyco` reaches the interviews (the lock refusal answered) -- the parent's run.
