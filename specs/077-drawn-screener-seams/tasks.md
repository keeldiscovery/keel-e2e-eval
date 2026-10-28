# Tasks 077 -- The harness follows keel-cloud 146 (the drawn screener's seams)

Branch `077-drawn-screener-seams` off master `ad540c3` + the spec (`8fb1b41`), worktree `wt/eval-077` (`.git` a file).
The products, read only: keel-cloud-docs master `427d8701` (146: contract 43 unchanged, corpus REVISION 16, no golden row
moved -- 146's tasks.md *Corpus*) and keel-web master `b50eb04` (nothing changed for 146), reached through the sibling
symlinks beside the worktree (`stack.toml`'s `../` paths). No paid command was run: every model, transcriber and renderer
the fakes. No instruction file moved in 146, so no screening is owed. `REVISION` stays 16, `MARKS_VERSION` 20,
`INTERVIEWER_MARKS_VERSION` 12, `REPORT_MARKS_VERSION` 3. Nothing merged, pushed or deployed.

| Commit | What |
|---|---|
| `8fb1b41` | the spec |
| `afcbaf2` | FR-1 - FR-4: `harness/qualifiers.py`, `vectors_script` (07's row under `DRAWN`, `scripted_segment`, `sentence`, `decider_people`), the pins moved, `tests/test_drawn_screener_seams_077.py` |
| `bc0a151` | FR-1 / FR-3 on the journeys: the card's condition line, the confirm step's stored condition, S-007's screener step |
| `2c23be3` | runs/DRIFT.md #99 resolved |
| this commit | this file |

## Unit

| | passed | failed | skipped |
|---|---|---|---|
| master `ad540c3` (the hand-off's figure) | 3,528 | 0 | 55 |
| `8fb1b41` against keel-cloud-docs `427d8701` + keel-web `b50eb04` | 3,528 | 0 | 55 |
| `2c23be3` and this commit | 3,543 | 0 | 55 |

146 broke no unit test on the spec's tree: the old `decider_chip` was pinned only on its own examples (none of which 146
moved) and on 05-paidly's doubled question, which the stack -- not a unit test -- read. The +15 are
`tests/test_drawn_screener_seams_077.py`.

## FR-1 -- 07-mulchrun carries a code-drawn screener -- `afcbaf2`, `bc0a151`

- [x] T001 `vs.SEGMENTS` gains 07-mulchrun's row: the core as the fake writes it (the founder's WHICH PEOPLE, *landscaping
  crew leads in the Dallas-Fort Worth suburbs, spring season*), *are based in the Dallas-Fort Worth suburbs*, *Are you
  based in the Dallas-Fort Worth suburbs?*, YES. `vs.DRAWN = {"07-mulchrun"}` names the rows whose condition is code's:
  `scripted_segment` (what `context_result` writes -- the core alone, as before) and `card_condition` (the pre-confirm
  card's *Only people who:* line -- none) read the result; `segment_of` (the confirmed context), `chip_of` (the part-1
  job, handed the drawn condition, writes the chip -- no E5 repair turn) and `decider_condition` read the condition.
- [x] T002 The confirm step (`corpus_scenario.leg_context`, the thorough pass's red at ~412): the confirmed sentence is the
  card's word for word (as written) and, strict, the mirror's `read_back(confirmed=True)`; `confirmed_segment_faults`
  holds `GET context`'s `segment.condition` to the one predicted (the model's kept on 01-05, code's on 07).
- [x] T003 S-007's new step: all twelve crew leads' FULL links serve *Are you based in the Dallas-Fort Worth suburbs?*
  (`inCodes` YES), all owners' commercial links *Are the landscaping crew leads you decide for based in the Dallas-Fort
  Worth suburbs?* walked condition -> idea, `outsideSegment` 0. The chip and the screener are walked by the wire-driven
  `Interview._gate` / `_condition` and held by `_hold_the_screens` as on every journey.

## FR-2 -- a qualifier is said once -- `afcbaf2`

- [x] T004 `harness/qualifiers.py` mirrors `Qualifiers` (`QUALIFIER`, `DRAWN_QUALIFIER`, `FRAME`, `OPENS_QUALIFIER`,
  `sameQualifier`, `inCore`, `carries`), `FounderWords` (`words`, `stem`, `dropped`, `negationDropped`, `STOP`,
  `MOST_DROPPED`) and `ReadBack.segment` / `phrase` / `ContextSlots.segmentLine`, compiled ASCII as Java reads `\w`.
- [x] T005 `vs.sentence` mirrors `ReadBack.sentence(core, condition, circumstance, job, window)`; `read_back` reads it
  (card or `confirmed`). 05-paidly's line unchanged (*Freelance translators in the US, who work mostly for agencies,
  when ...*); 07's gains no clause; 01-04 keep theirs. `segment_line` keeps `segmentLine`'s own *, who* join.

## FR-3 -- the decision-maker's chip names the people once -- `afcbaf2`

- [x] T006 `vs.decider_people` mirrors `deciderPeople`: `qualifiers.head` (cut at the last relative pronoun or
  preposition at or before the qualifier), else `actor_plural` whole, else *people* where `qualifiers.says`, *people*
  with no plural. `decider_chip` reads it in both the *Do the* and the *Are the* shape; the organisation's branch as 145.
- [x] T007 S-006's step holds as written (opens *Do the*, carries *you decide for*, equals the mirror): all eight
  agency decision-makers and Odile Marchetti served *Do the people you decide for work mostly for agencies?*.

## FR-4 -- "when" once -- `afcbaf2`

- [x] T008 `qualifiers.with_when` / `OPENS_WITH_CONJUNCTION` (145's five, not widened), read by `vs.sentence`;
  `qualifiers.default_about` and `interview_topic` mirror `Project.defaultAbout` and `InterviewComposer.topic` for the unit
  test alone -- no mark composes either line (the interviewer marks read the served `topic`). No corpus circumstance
  opens with a conjunction (held by a unit test), so no journey line moved.

## FR-5 -- nothing else moves

- [x] T009 Marks versions unchanged (no mark pinned a moved wording: the doubled question was a journey assertion read
  off the mirror, not a mark). `REVISION` 16; 146 moved no golden row, so nothing is listed for revision 17 beside 145's
  02-compliancelog row. The noise check, the back-tests, the judge and the paid commands untouched.

## Every pin moved

| Pin | Was | Now | Why |
|---|---|---|---|
| `test_founder_walk_076::test_which_journey_entries_serve_the_screener` | 05-paidly alone, the doubled question | 05-paidly and 07-mulchrun; *Do the people you decide for work mostly for agencies?* | 146 FR-3 (DRIFT #99); 146 FR-1 draws 07's condition |
| `test_founder_walk_076::test_the_screener_screen_is_first_and_the_idea_after_it` | the doubled question as fixture | the served one | the fixture reads as the stack serves |
| `test_vectors_journey::test_the_script_answers_every_corridor_screen_from_the_entry` | context result's segment == `segment_of` | == `scripted_segment` | 07's condition is code's, never the fake's |
| `test_vectors_journey::test_the_read_back_is_keel_clouds_assembled_sentence` | 07's card sentence | the same, and equal to the confirmed one | 146 FR-2 |
| S-006 screener step | the mirror's doubled question | the mirror's *the people* (assertion unchanged) | 146 FR-3 |
| S-007 confirm step | red on staging (*..., who are based in the Dallas, when ...*) | the card's sentence, the drawn condition stored | 146 FR-1 / FR-2 |

## The light gate (local stack, keel-cloud-docs `427d8701` + keel-web `b50eb04`, the scripted executor)

`docker ps` before `make up`: only `focused_robinson` (never touched). `make down` / `make up` between runs.

| Run | On | Result |
|---|---|---|
| `runs/20261028T061806Z-s007-mulchrun` | `2c23be3` (clean) | **passed** (151 s): report 5 of 5 (v3), guide 3 of 3, feedback 3 of 3; the drawn-screener step 12 chips + every owner's screener, condition -> idea |
| `runs/20261028T062110Z-s006-paidly` | `2c23be3` | **passed** (407 s): IM 29 of 29 (v12), report 5 of 5, guide 5 of 5, contacts 13 of 13, feedback 5 of 5; screener *Do the people you decide for work mostly for agencies?* |
| `runs/20261028T062824Z-s005-countly` (smoke) | `2c23be3` | **passed** (367 s): IM 23 of 23, report 5 of 5, guide 17 of 17, contacts 1 of 1, feedback 4 of 4 |

`versions.json`: keel-cloud `427d8701` (clean), keel-web `b50eb04` (dirty by its untracked `.idea/` alone), keel-runtime
`3988131`, keel-e2e-eval `2c23be3` (clean). Each journey green on its first run; no rerun. `make down` after the last; no
container left but `focused_robinson`.

## DRIFT #99 -- closed

`runs/DRIFT.md` #99 is RESOLVED by keel-cloud 146 FR-3 (keel-cloud-docs `427d8701`): the heading says so and a paragraph
above the observation as filed names the served question and the harness's mirror.

## What did not hold

- *Remote six*: the coordinator's, after the deploy (the spec says so). S-014 (paidly's healthy copy) was not run here; it
  walks the same mirror.
- *FR-4 on the stack*: no corpus circumstance opens with a conjunction, so *when* once is unit-tested only.
- *146's Docker half* (`./gradlew test` with Colima up) is keel-cloud's own, owed before its merge per its tasks.md; this
  gate ran the merged master on the stack, which booted and served every line read here.

## Judgement calls

- J-1 **07's condition stays code's on the wire.** The spec offered a `SEGMENTS` row or reading the chip off the wire; a
  row alone would have made the fake write the condition and stopped the stack exercising 145 FR-4a's draw -- the path
  the thorough pass found red. So the row is added and marked `DRAWN`: the fake's CONTEXT_INTERPRET writes the core
  alone, while the part-1 job (handed the drawn condition, as a model would be) writes the chip 146 pins.
- J-2 **146's judgement calls mirrored as written**: the "said once" rule from core and condition alone (Issen keeps
  its clause), `says` allowing one content word and reading *working* as *work*, the cut stepping back to the
  qualifier's own preposition (*learners at intermediate level* -> *learners*). Each has a unit test.
- J-3 **A new module, not more of `vectors_script`.** `harness/qualifiers.py` mirrors one cloud class family and is held
  to its sources (`test_the_mirror_reads_the_clouds_patterns`); `vectors_script`'s older `QUALIFIER` / `condition_from` /
  `drawn_condition` (130's X12 mirror, which the findings path reads) were left as they are.
- J-4 **The stored condition is asserted on the wire** (`GET context`'s `segment.condition`, contract 30), so a
  regression in 146 FR-1's place (*are based in the Dallas*) fails at the confirm step by name, not only by the sentence.
