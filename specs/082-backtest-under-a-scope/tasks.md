# Tasks 082 -- The back-test under a scope: the study's own people, the cost box read when it is drawn, and a cycle record that names the walks that stopped

Branch `082-backtest-under-a-scope` (worktree `wt/eval-082`, `.git` a file), off master `088cbb6` (the spec on top of
cycle 1's `ecbf1a6`). Read only: keel-cloud 133 (the B2B link is the money study's), keel-web 123 FR-1
(`FounderControl`'s `ready`: the *of* box drawn inside the equation once a mode, a unit and a period are picked),
keel-cloud-docs `f48f256e` spec 148's tasks.md (DRIFT #100). `RUBRIC_VERSION` 2, `MARKS_VERSION` 21, `REVISION` 17
unchanged. **No paid call**: no walk, no reader, no adviser, no API key. Nothing merged or deployed; every commit pushed
to the branch (the founder's rule of 2026-10-28).

| Commit | What |
|---|---|
| `886f346` | FR-1: `harness/vectors_script.py`, `tests/test_backtest_scope_082.py` (4) |
| `24e0021` | FR-2: `harness/vectors_screens.py`, `evals/corpus_scenario.py`, the tests (+4) |
| `91f3dbb` | FR-3: `quality/cycle.py`, `quality/table.py`, `quality/CYCLE.md`, `quality/TABLE.md` (regenerated), the 079 fixture record, the tests (+5) |
| `e15485b` | `runs/DRIFT.md` #100 |
| this commit | this file, `AGENTS.md` |

## Unit

| | passed | failed | skipped |
|---|---|---|---|
| master `ecbf1a6` / `088cbb6` | 3,655 | 0 | 53 |
| `91f3dbb` (FR-1..FR-3), keel-cloud checkout at `f48f256e` | 3,667 | 1 | 53 |

The +13 are `tests/test_backtest_scope_082.py`'s 13 (3,655 + 13 = 3,668 = 3,667 passed + the one red); no earlier test
moved by this spec (the 079 fixture record was recomposed by `compose`, so `test_the_record_is_composed_from_...` holds
the new line unchanged). **The one red is not this spec's**: `test_interviewer_marks::test_the_faces_are_keel_clouds_own`
reads keel-cloud's `InterviewerFace.java` from the sibling checkout, which keel-cloud 143 (`5f77bf4d`, merged 2026-10-28
10:15, after master's 3,655 was counted) changed to Daphne and Saskia with the four photo faces retired; the harness's
`interviewer_fake.FACES` still names LIVIA first. This branch touches neither file (`git diff master` on
`harness/interviewer_fake.py` and the test is empty), so master red the same against today's checkout. Left for the
spec that mirrors keel-cloud 143 (FR-4: nothing else moves).

## FR-1 -- the study's own people

- [x] T001 `vectors_script.study_people(entry)`: under `entry.scope` PROBLEM or SOLUTION (`PRIMARY_ONLY_SCOPES`) the
  entry's PRIMARY people alone; under COMMERCIAL, SOLUTION_COMMERCIAL and ALL every person, as before.
  `person_inputs(entry)` builds from it, so `follow_up_lines`, the THEMES screen (`generate`'s `walked_follow_ups(entry,
  person_inputs(entry))`) and `inputs_json` read the reduced list. The scope arrives through the entry
  (`corpus_scenario` and `scope_journey` already replace `entry.scope` before building the people); no new parameter.
- [x] T002 Tests: 08-fresco (keel-cloud's back-test file) under PROBLEM and SOLUTION -- its 12 PRIMARY people, no B2B
  link; under ALL and COMMERCIAL the file's 20; the golden B2B fixture (`10-fixture-b2b`) under PROBLEM and SOLUTION --
  no decision-maker owed a follow-up line, in `inputs.json` or behind THEMES (under ALL they are); the signature and the
  replace-before-build order in both journeys.

## FR-2 -- the cost box is read when it is drawn

- [x] T003 `Corridor._chain_cost`: `chain-unit` and `#chain-unit-help` read before anything is typed, as before; the mode
  pill, the unit, the period pill, `chain-equation` visible -- then `chain-base` and `#chain-base-help`, and on HOURS the
  rate, its note and the rows' order (as before). The docstring says why (keel-web 123 FR-1, `ready`).
- [x] T004 `_hold_the_cost_fill`: the step reads *the cost step: Per arrives filled from the project with its helper line
  before anything is typed; of with its helper line, and on hours the rate under the hours row with its default note,
  once the period is picked and the equation is drawn (keel-web 123)*; the docstring says when `filled` is read. The
  pins unchanged (the role word, the occasion, each helper, the rate and its note, the rate between the hours and *of*).
- [x] T005 Tests on a page double (`_ChainPage`) that draws `chain-base` / `#chain-base-help` only with the equation and
  the rate only on hours: *of* read after the period pill and before anything is typed in it, on HOURS and RATE; no
  *of* read on money; the step and the docstring. The two read-order tests fail on master's order (checked by reverting
  the change: 2 failed).

## FR-3 -- the record names the walks that stopped

- [x] T006 `cycle.walks_of(record)`: `walks`, `ended`, `stopped` (`study -- the step`: the step's words before its first
  colon; *no step named (stopped outside a step)* where the walk raised between steps, as cycle 1's KeyError walks;
  the error where no bundle was written), `pins` (the kick-off's keel-cloud and keel-web shas) and `moved` (every
  change of either sha from the pin, in walk order, with the study it was first seen on). `compose` stores it in the
  data block as `walks`.
- [x] T007 `table.walks_lines`: under the score, on the record's head and on `TABLE.md`'s (`cycle_head`), as sub-lines
  of *this cycle*: *N of M walks reached their end; K stopped early (study -- the step; ...); their scores are of the
  screens served before the stop*, then *keel-cloud moved mid-cycle: a -> b from <study>* (and keel-web the same) where
  a sha moved. `TABLE.md`'s respondent line keeps *of N screens* (unchanged).
- [x] T008 `make quality-walk`: the shas pinned at kick-off as before (`cloud7`, `web7`, the record's name and header);
  each `Study` now records `cloud_sha` / `web_sha` -- the bundle's `stack` (`walk_one`), else the checkouts after the
  walk -- and a study on another sha is printed *recorded, not refused*; nothing refuses mid-cycle.
- [x] T009 A record from before 082 (cycle 1) carries no `walks`: `table_head` computes it from the record's studies and
  each study's sha from its score file's header (else the sha in the file's name). Cycle 1's record is **not
  rewritten**; `make read-table CYCLE=quality/cycles/20261028-88bfce8.md` regenerated `quality/TABLE.md` -- two lines
  added, nothing else moved: *2 of 15 walks reached their end; 13 stopped early (...)* and *keel-cloud moved mid-cycle:
  88bfce8 -> f7b0e05 from 10-palus · COMMERCIAL*.
- [x] T010 `quality/CYCLE.md`: step 1 *What it pins*, step 2 the walks line under *this cycle*.
- [x] T011 Tests: the 079 fixture cycle with two walks stopped (one at a named step, one outside any step) and the third
  study walked on `bcdef12` against the pin `abcdef1` -- the record head's two lines, the data block (`walks`, each
  study's sha, the whole step kept); the same two lines on `TABLE.md`'s head; a whole cycle (*4 of 4 ...; 0 stopped
  early*, no move); cycle 1 read from its files and never rewritten, the committed `TABLE.md` carrying the lines and the
  respondent's *of 12 screens*; `walk_one` recording the bundle's sha.

## FR-4 -- nothing else moves

- [x] T012 The readers and their prompts, `quality/rubric.py`, the weak rule, the adviser, the journeys
  S-005/006/007/014/015/016 (S-015 and S-016 walk 01-countly, B2C, so FR-1 changes none of their people), the marks
  (`MARKS_VERSION` 21), `REVISION` 17.

## runs/DRIFT.md #100

Filed from keel-cloud 148's tasks.md (that build was confined to the keel-cloud worktree): `chipFrom` / `deciderChip`
paste a *whose* / *that* / *which* condition after *Do you* / *you decide for* (*Do you whose work is documented in
digital systems?*); `StrangerGrammar.fault` passes the *whose* and *which* forms; reachable past X6's repair turn, since
148 FR-1 only where WHICH PEOPLE carries no qualifier. The harness pins nothing yet. Second paragraph: 08-fresco's drawn
*run on Procore or ACC* (145's `conditionFrom`), asked as *Do you run on Procore or ACC?* -- open.

## The acceptance

| Command | Result |
|---|---|
| `make unit` | **3,667 passed, 1 failed, 53 skipped** (195 s); the one red keel-cloud 143's faces, not this spec's (above) |
| `make read-table CYCLE=quality/cycles/20261028-88bfce8.md` | `quality/TABLE.md` regenerated over the committed cycle-1 scores: 15 studies, 86.8%, the walks line and the moved line under *this cycle*; nothing else in the file moved |

## Judgement calls

1. **The step by its name.** Thirteen whole steps in one line would bury the head; the line names each by its words
   before the first colon (*the context is confirmed on the wire*, *the cost step*), and the data block and the studies
   table keep the whole step. A walk stopped outside any step (cycle 1's four KeyErrors, `failed_step` null) says so.
2. **The walks line is a sub-line of *this cycle*.** *Under the score* read literally: it sits indented under the score
   line on both heads, so the three lines the founder reads first (this cycle, the baseline, the bar) stay three.
3. **Cycle 1 read, not rewritten.** Its studies carry no sha of their own; the score files' headers carry the bundle's
   (`cloud_sha`), so `table_head` computes `walks` for a record without it -- the record file is untouched and the
   regenerated table names the move the file names only in its score files.
4. **A sha from the bundle, else the checkout.** The bundle's `stack` is what was walked; where a bundle carries none
   (no bundle, or an older one) the checkout after the walk is the next best and is recorded as such.
5. **SOLUTION_COMMERCIAL keeps everyone.** FR-1 names PROBLEM and SOLUTION; SOLUTION_COMMERCIAL tests the money, whose
   decision-maker link the project has (keel-cloud 133 FR-4), so it stays as before.
6. **Every move named, not the first alone.** Two merges in one cycle say *a -> b from X, then b -> c from Y*.

## What did not hold

- **Zero failed.** One red outside this spec: the faces pin against keel-cloud 143 (*Unit*, above). Every test this
  spec names is green, and the 3,655 of master pass.
- The record's head line for the respondent audience (*respondent 84.6%*) still carries no
  screen count of its own -- FR-3 asks to keep `TABLE.md`'s, which has it (*of 12 screens*); the record's was left as
  079 wrote it.
