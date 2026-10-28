# Spec 082 -- The back-test under a scope: the study's own people, the cost box read when it is drawn, and a cycle record that names the walks that stopped

The first quality cycle (`quality/cycles/20261028-88bfce8.md`, 2026-10-28) stopped 13 of its 15 walks early. Eight
stopped at the context confirm (keel-cloud's fault: spec 148). The other five are this harness's, and the cycle record
summed the readers' scores as if every walk had reached its end:

- **KeyError `'COMMERCIAL_B2B'`** at the send step on 08-fresco SOLUTION, 17-expanse PROBLEM, 21-codyco PROBLEM and
  SOLUTION (`corpus_scenario.py` ~2527): `vs.person_inputs(entry)` keeps the entry's B2B people under a PROBLEM or
  SOLUTION walk, and the project under those scopes has no `COMMERCIAL_B2B` kind to send them on (keel-cloud 133: the
  B2B link belongs to the money study). 13-aircaps, with no B2B people, walked through.
- **The cost box read before it is drawn** on 13-aircaps and 17-expanse COMMERCIAL (`vectors_screens._chain_cost`):
  the harness reads `chain-base` and `#chain-base-help` right after the mode pill, but keel-web draws the *of* box
  inside the equation (`FounderControl`, `ready`: a mode, a unit and a period), so on a fresh draft the box is not on the
  page until the period is picked -- `base` and `base_help` came back None, on HOURS and RATE alike. Spec 075 FR-2's
  step was never walked live before this cycle.
- **The record's head** says *score_pct 86.8% over 165 screens* and names each walk's stop only in the studies table;
  the respondent audience's 84.6% rests on 12 screens because most walks never reached a link. A reader of the head
  takes a truncated cycle for a whole one. The cloud checkout also moved mid-cycle (`88bfce8` to `f7b0e05` at 10-palus
  COMMERCIAL, keel-cloud 143's merge) and only the file names say so.

The readers, the rubric (version 2), the marks (`MARKS_VERSION` 21) and `REVISION` 17 do not move.

## Rules

- **FR-1 The study's own people.** `person_inputs(entry)` under `entry.scope` PROBLEM or SOLUTION returns the PRIMARY
  people alone -- the B2B people are the money study's (keel-cloud 133) and the project has no kind for them; under
  COMMERCIAL and ALL every person as today. The follow-up lines, the themes screen and `inputs.json` read the list
  that comes back, so nothing downstream names a person who was not sent. The back-test's scope reaches `person_inputs`
  through the entry (`corpus_scenario` replaces `entry.scope` before building the people; `scope_journey` the same),
  not a new parameter.
- **FR-2 The cost box is read when it is drawn.** `_chain_cost` reads `chain-unit` and its helper before anything is
  typed, as today; it reads `chain-base` and `#chain-base-help` (and on HOURS the rate and its note) after the period
  pill, once `chain-equation` is visible -- the moment keel-web 123 FR-1 puts the filled box on the page. The step's
  wording and `_hold_the_cost_fill`'s docstring say so. The pins are unchanged: *of* filled with the occasion, the
  helper line under it, the rate under the hours row.
- **FR-3 The record names the walks that stopped.** The cycle record's head and `TABLE.md`'s head carry one line
  under the score: *N of M walks reached their end; K stopped early (study -- the step, for each); their scores are of
  the screens served before the stop*, and the respondent line says how many screens it rests on (it does: keep it).
  `make quality-walk` pins the keel-cloud and keel-web shas at kick-off; a study walked on another sha is recorded with
  its own sha and the head says *keel-cloud moved mid-cycle: 88bfce8 -> f7b0e05 from 10-palus · COMMERCIAL* -- named,
  never refused (a refusal mid-cycle would waste the paid walks before it). The record of cycle 1 is not rewritten.
- **FR-4 Nothing else moves.** The readers and their prompts, `rubric.py`, the table's weak rule, the adviser, the
  journeys S-005/006/007/014/015/016, the marks.

## Acceptance

`make unit` green with zero failed (master `ecbf1a6`: 3,655 / 0 / 53): `person_inputs` on the 08-fresco fixture under
PROBLEM and SOLUTION yields PRIMARY people only and under ALL and COMMERCIAL the file's people; the themes and
follow-up fixtures under a scope read the reduced list; `_chain_cost`'s read order (a page double that draws the box
only with the equation); the record head on a fixture cycle with two stopped walks and a moved sha. `make read-table`
regenerates `quality/TABLE.md` with the new head line on the committed cycle-1 scores. No paid command. tasks.md in
081's shape. Build on the founder's word -- given 2026-10-28 ("go ahead with the testing, don't wait for my go
ahead"): cycle 2 cannot run without it.
