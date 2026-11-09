# Spec 148 -- The harness mirrors round A: keel-cloud 238 to 241 and keel-web 183

Round A (the founder's decision of 2026-11-09, after cycle 18 and its adviser): the gate asks the act that hurts
(keel-cloud 238), the Existing sacrifice item names the thing they see go (239), the idea card keeps the founder's claim
(240), Ability to pay's labels fit every organisation (241), the window question names the moment (keel-web 183). The
harness pins what each of those serves, so the next cycle reads the new shapes as right and the old ones as faults.

## Rules

- **FR-1 The digest.** `quality/readers/dimensions.md` is a byte copy of keel-cloud's `dimension-cards.md` at the
  final cloud sha of the round (155eaca9), and the digest pin chain moves (`CARDS_SHA256_*`: 238's d764f34f… as the
  step between, then 239's and 241's).
- **FR-2 The gate (238).** The walk and the readers know the five refusal texts (E7 segment, E7 kind, E7 new word, E9
  no hurt word, E8 blame) and the two new verdict words; E7/E9 after the repair turn are RESULT_INVALID (a stop the
  walk names), E8 blame and the new verdicts are served with a note (never a stop). A seed refusal at the project step
  carries the same `result.questions[0].event` path. The gate's served clause is never the routine (the mirror's own
  test on the served text against the context's circumstance words).
- **FR-3 Existing sacrifice (239).** The served item never carries *go without*, *fell through*, *lose*, *lost*,
  *miss*; the base is the loss line's; *per {unit}* kept on both links; the Check may carry a note that Keel could not
  name what they see go (named, never a stop).
- **FR-4 The idea card and the reveal (240).** The belief opens *would* + the founder's verb (never *would earn* for
  *target*); no *your* before a thing the idea brings; no noun said twice across name, what line, how and belief
  (the heard-once reader rule's regex widened to the whole reveal).
- **FR-5 Ability to pay (241).** The two labels as served: *Charged back to whoever uses it*, *New money from outside,
  such as a grant*; codes unchanged.
- **FR-6 The window question (web 183).** The founder's window screen never reads *the last time it happened* where a
  *when* was typed; the clause is the typed when said of the people; the summary is one sentence.
- **FR-7 The record.** The cycle record's review line cites 238 to 241; `backtest.json` records E7/E9 stops by rule.
- **FR-8 Tests.** `make unit` green at the head; the digest pins, the frame regexes and the new stop names covered.

## Out of scope

Any paid run; keel-cloud and keel-web code; the nine's new-vs-known read (a read of the record, not a spec).
