# Spec 169 -- The judge finds the gate by its new words, and the lock never waits on a failed calibration

keel-cloud 277 (the founder, 2026-11-25 morning: *"Have you encountered this issue? ... Make it very simple."*) changes
the film's gate to *In {window}, have you encountered this issue?* and makes the problem study's calibration READY on
its first write (every clause rule a note, never a refusal). The harness pins the old words
(`harness/interviewer_screens.py` `GATE_WORDS`, `harness/film_strangers.py`'s docstrings and the check it answers by
`recency`, `harness/three_surfaces.py`, `harness/solution_surfaces.py`) and `quality/FILM-RUBRIC.md` names them; spec
168's retry at the lock stays (a study with no film still has the framed clause and its breaches). Eval side, built
on 168 (`12e7804`); nothing paid.

## Rules
- **FR-1 The gate found by its new words.** `GATE_WORDS` becomes a match on the words *have you encountered this
  issue?* with any window before them (a prefix *In the last ...*): the screens reader, the strangers' walk (the
  check answered by `recency` as today), the three-surfaces and solution-surfaces readers find the gate on the text
  link, the orb and the Copilot's card by that match; the old words are no longer matched. The one-script check
  (269 FR-8) compares the three surfaces' words to each other, not to a constant.
- **FR-2 The rubric and the table.** `quality/FILM-RUBRIC.md` and `quality/CYCLE.md` say the new words where they
  quote the gate; no criterion moves. The film table's DRIFT finding of 168 (*the lock's calibration was written again
  on the founder's retry*) stays and now reads as a capture note on a study with no film only.
- **FR-3 Tests.** `tests/test_the_strangers_on_the_films_link_165.py` and the surfaces tests: a gate reading *In the
  last month, have you encountered this issue?* is found and answered; the old words are not; a stub whose calibration
  reads READY on the first read POSTs no retry (168's test unchanged). `make unit` green on the base's known reds only.
- **FR-4 The respondent-question rule.** The stub founder's and the strangers' words are unchanged; the gate's words
  are keel-cloud's, read from the wire, never written here.

## Acceptance
- `DOOR=fake` and unit tests only; on the next paid walk (the founder's word) every entry's problem leg sends its link
  with no `LockFailed` at step 2.
