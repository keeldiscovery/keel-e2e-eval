# Tasks 123 -- The referee follows keel-cloud 193

Branch `123-the-referee-follows-193` (worktree `wt/keel-e2e-eval-123`, `.git` a file, the main checkout's `.venv`
symlinked), off master `39a9ccb` (specs 123-125 written). Built by a builder (Claude, on the coordinator's brief) on
2026-11-01. Read only: keel-cloud-docs master `2d848360` (193's tasks.md, `CommercialChain.costBelief` / `LACK` /
`LOSS_VERBS` / `ownNoun` / `BASE_ENDS`, `RespondentQuestionsRules.gate` / `servedFrequency` / `condition` /
`deciderCondition`, `WindowFrame.frequencyRespondent`, `ScreenContextBuilder`, the 17 back-test entries amended in place;
and, because the gate met it, 192's `StandingsAssembler.cardsDeciding`). **No stack, no model, no paid call, no key
read.** Nothing merged; the branch pushed after the spec's commits.

## FR-1 -- the cost sentence (`instructions/chain.py`)

- [x] T001 `cost_belief(cost, occasion, role_word, deciders, b2b, *, actor, actor_plural)`: **money** the deciders'
  (unchanged); **hours** the context's `actor_plural` (capitalised, *They* with none), the *per {unit}* dropped where the
  unit is their own noun (`own_noun`: the actor's head word, or the head of the people's plural before `BASE_ENDS`,
  singular or plural), *on {base}* dropped where the base is the lack itself (`LACK`); **a rate with a loss phrase**
  said of its base -- *About {figure} of {base} {per} {loss}.* where the loss opens on a verb (`loss_predicate`,
  `LOSS_VERBS`), else the colon -- consumer studies too; **a rate without one** *{Actor plural} already lose about ...*.
- [x] T002 `corpus._check_chain` (rule C) hands the context's `actor` and `actor_plural`; every chain entry's recorded
  `belief_sentence` is held to the port (the 17 back-test yaml files are the oracle -- all load).

| Entry | Was (the mirror before) | Now (keel-cloud 193, the yaml) |
|---|---|---|
| 08-fresco | *Contractor operations leads already spend 30 to 60 hours per site a month on the daily log.* | *Construction superintendents on commercial jobs already spend 30 to 60 hours per site a month on the daily log.* |
| 14-code-four | *Police chiefs already spend 40 to 60 hours per officer a month on the incident reports.* | *Patrol officers at small and mid-sized police departments already spend 40 to 60 hours a month on the incident reports.* |
| 18-careforce | *Health center directors already lose about 30% to 33% of the patients due for a visit or screening per health center a month: visits and screenings never booked because nobody reached the patient.* | *About 30% to 33% of the patients due for a visit or screening per health center a month: visits and screenings never booked because nobody reached the patient.* |
| money (Retell, Karsa's price ...) | -- | unchanged |

## FR-2 -- E4 in the served frame (`instructions/wording.py`, `harness/vectors_script.py`)

- [x] T003 `wording.framed_fault` (the instruction eval's E4, `score.respondent_checks`) measures the gate and
  `frequency_respondent` (window first) against `STEM_MAX_WORDS`, the breach worded as the cloud's (*the Frequency
  question served N words (...); ... so shorten the clause, keeping its verb and its object*). `frequency_measured`
  stays, read on nothing new.
- [x] T004 `vectors_script.e4_fault(window, event)` (`RespondentQuestionsRules.gate`); `event_base` raises it (the
  scripted writer is asked, never cut). `frequency_held` keeps its cut for items stored before 193.
- [x] T005 The scripted writer's clauses: five golden gate clauses served 21-22 words window first and are the writer's
  shorter ones (verb and object kept; the founder's past-tense clause unchanged), and the B2B test fixture's
  `GATE_EVENTS` clause:

| Entry | Was (served words) | Now (served words) |
|---|---|---|
| 01-countly | *have to recount stock by hand after a mismatched delivery* (21) | *recount stock by hand after a mismatched delivery* (19) |
| 02-compliancelog | *have to pull training completions into a spreadsheet by hand* (21) | *pull training completions into a spreadsheet by hand* (19) |
| 04-linerly | *lose time to a puncture riding to or from work* (21) | *lose time to a puncture riding to work* (19) |
| 05-paidly | *wait beyond agreed terms to be paid for an approved invoice* (22) | *wait beyond agreed terms for an approved invoice* (19) |
| 07-mulchrun | *wait at the supply yard for mulch for a job* (21) | *wait at the supply yard for mulch* (18) |
| `10-fixture-b2b` (tests) | *have a time when the morning they cannot find their keys* (22) | *fail to find your keys in the morning* |

## FR-3 -- the numbers the world has

- [x] T006 Nothing to port: the eval keeps no copy of `P2`. `PROBLEM_INTERPRET`'s statement is judged by keel-cloud's own
  validator (`instructions/validate.py` shells `ScreenContractTool`, which runs `statementNumberFault`), so a world's
  number the founder typed passes here exactly when it passes there; a test pins that the route and the cloud's rule
  exist. No mark number moves (`MARKS_VERSION` unchanged).

## FR-4 -- no fallback condition on the decision-maker's link

- [x] T007 `vectors_script.decider_condition`: the written `screeners.decider` on a study with a condition, else
  **None** (the `chip_from` fallback gone). `context._hands_condition` reads the same (see *Not foreseen*).
- [x] T008 The journeys tolerate the absent screen: S-006 and S-007 expect the idea first on the decision-maker's link
  where nothing is written (both golden entries now); `corpus_scenario.leg_outside_decider` records itself not owed
  (no screener to answer outside) instead of failing.

| Where | Was | Now |
|---|---|---|
| 05-paidly's decision-maker | *Do you work mostly for agencies?* before the idea | no condition; the idea first |
| 07-mulchrun's decision-maker | *Are you based in the Dallas-Fort Worth suburbs?* | no condition; the idea first |
| S-006's outside decision-maker (Odile Marchetti) | walked outside the screener | not walked; recorded as not owed |

## Tests

- New `tests/test_referee_follows_193_123.py` (14): 193's three sentences and the predicate / colon / no-loss / money /
  site-unit / *miss* cases word for word; `LOSS_VERBS`, `BASE_ENDS` and `LACK` read from `CommercialChain.java`; three
  amended yaml sentences and the 17 amended headers; E4 on Careforce's clause and on a scripted overrun (reported, never
  cut); every golden scripted clause fits and is served whole; P2's route; no decider condition on the goldens, a
  written one served only on a study with a condition; 192's stage verdict.
- Re-pinned with why: `test_instruction_window_frame` (E4's 9-word clause, the served frame named),
  `test_lock_frontier_110` (Palus's served 24 words), `test_money_cards_redrawn_118` (Fresco's sentence; no golden
  decider condition), `test_drawn_screener_seams_077` and `test_founder_walk_076` (no golden serves one),
  `test_cycle_5_to_the_end_119::test_revision_22_moves_exactly_187s_edits` (accepts 193's in-place sentence on the 17
  amended entries, and counts them).

## Gate

| | passed | failed | errors | skipped |
|---|---|---|---|---|
| master `39a9ccb` in the worktree, before any edit, against keel-cloud-docs `2d848360` and keel-web `2b84758` (~16:30-16:34 ET) | 4,717 | 154 | 2 | 55 |
| after spec 123 (`set -o pipefail; make unit`, 16:48-16:52 ET) | 4,886 | 2 | 0 | 54 |

The two left are spec 124's (`test_interviewer_marks::test_the_kinds_are_keel_clouds_own`, `ClipKind.CONDITION`) and
spec 125's (`test_read_back_mirror_085::test_the_draw_mirror_reads_the_clouds_sources`, 195's `droppedAsSpelt`); both
specs follow on this branch and their tasks.md carry the zero.

## Not foreseen

1. **No corpus revision 23.** keel-cloud 193 amended revision 22 in place (17 back-test entries, an *AMENDED IN PLACE*
   note at each head, `belief_sentence` moved, `revision: 22` kept, no `event` shortened). So no revision-23 test and no
   yaml edit here; FR-5's `tests/test_revision_*` for 23 is void. The r22 diff test accepts that one path instead.
2. **Rule (b) reaches consumer studies; hours take `actor_plural`; a lack base drops *on {base}*** -- as built
   (193's *Not foreseen*), so `cost_belief` takes the context's actor and plural, which the spec's signature did not.
3. **The scripted writer's clauses moved, not the yaml's.** The E4 mirror reports an overrun the cloud's way and never
   cuts; the clauses the harness scripts for the golden journeys (its own, COMPOSED) overran the served frame, so the
   scripted writer shortens them as the cloud asks a writer to. Back-test entries are walked by the model, not
   scripted, so none of theirs is measured here.
4. **`_hands_condition` is unchanged**: keel-cloud 193 left `ScreenContextBuilder` alone (the decision-maker's part 3 is
   still handed the segment's condition); only what the link serves moved, which is `decider_condition`.
5. **A written decider condition is served only where the study has a segment condition** (`deciderCondition`); the
   three entries that write one (08, 10, 17) carry none today, so no walk serves one.
6. **keel-cloud 192 FR-1 was unmirrored** (the stage reads as its cards read: *Did not hold* raises a PEOPLE_DISAGREE
   stage to NOT_HOLDING_UP, never lowers it), and at `2d848360` the brief-facts compare and the Overview draw failed on
   it (02, 03, 06, 07). `brief_facts.vectors_for(entry, cards)` / `stage_verdict` / `card_status` port
   `StandingsAssembler.cardsDeciding`; `decision` keeps the engine's verdicts (the cloud's did not move).
7. **FR-3 has no eval-side mirror** (the statement's P2 is the cloud validator's), so it is pinned, not ported.

## Owed elsewhere

- keel-cloud: nothing new. (A written `decider_condition` on a study with no segment condition is dropped by
  `deciderCondition`; if the founder wants it served there, that is a cloud spec.)
- keel-web: nothing.
- The coordinator: the next quality cycle walks 18-careforce's money study with no decision-maker's screen and its
  problem study's Frequency clause whole (the writer's, shortened).
