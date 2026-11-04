# Plan 132 -- The harness mirrors keel-cloud 205-208 and keel-web 166, 168, 169

Branch `spec-132` (worktree `wt/keel-e2e-eval-132`, `.git` a file), off origin/master `994bb8a` (the spec and its five
amendments). Read only: keel-cloud-docs master `7c96988d` (205-208's tasks.md, *Owed elsewhere*; `PurchaseFriction`,
`FounderReason`, `ScreenResultApplier`, `AskedRules`, `IdeaLines`, `CommercialChain`, `FollowUpComposer`, `BandSaid`,
`SpokenForm`, `AnswerPrompts`, the registry YAML of record and its JSON export, `CostQuestionInTheirWordsTest`, the
`commercial-chain/*.json` worked cases, `corpus-r22/`, `backtest-r22/`, `corpus-r23/`), keel-web master `a1848dc3`
(166's, 168's and 169's tasks.md; `translate.ts`, `founderLists.ts`, `contextReach.ts`, `ListQuestion.tsx`,
`KeelTest.tsx`, `scope.ts`). No stack, no model, no walk, no paid call, no key read; the fake interviewer and the unit
suite only.

## Where each FR lands

| FR | Where |
|---|---|
| FR-1 L32 | `instructions/friction.py` (`OFFER`, `founders_offer`, `OFFER_NOTE`), `instructions/score.py` (`list_faults`), `evals/backtest.py` (`LOCK_NOTES`) |
| FR-2 the offer rows | `harness/vectors_script.py` (`offer_rows`, `kept_items`, `kept_picked`; `drafted_list`, `saved_list`) |
| FR-3 / FR-10 Buyer and payer | `vectors_script.buyer_payer_pick` / `buyer_payer_roles` / `founder_side`; `vectors_screens.Corridor.list_choose(index=)`, `_choose_confirm`, `roles_joined`; `corpus_scenario.leg_calibrate`, `choose_faults` |
| FR-4 the cards | `quality/readers/dimensions.md`; `tests/test_dimension_cards_131.py` |
| FR-5 pins | `vectors_screens.PURCHASE_FRICTION_ANSWER_QUESTION`, `COMMITMENT_ANSWER_QUESTION`; Commitment's drift template (the card test); 115's Frequency guidance |
| FR-6 / FR-12 rules by name | `backtest.LOCK_NOTES` |
| FR-7 only_if | `vectors_script.adoption_condition`, `drafted_list` |
| FR-8 the time | `vectors_script.walker_duration` |
| FR-9 stems, label, window, held Choose | `vectors_script.cost_question` and its ladder (206's port, `held` / `loss_word`); the registry's *Yes, I would* (test); `vectors_screens.circumstance_clause_of`, `said_of_the_people`; `list_choose`'s `waiting` read, `corpus_scenario.said_faults` |
| FR-10 the screen words | `vectors_screens` constants (`IMPORTANCE_ANSWER_HINT`, `COMPATIBILITY_ANSWER_HINT`, `CURRENT_SOLUTION_HOW_HINT`, `PURCHASE_FRICTION_CHOOSE_BAR_UNDATED`, `CHAIN_BASE_HELP` / `chain_base_help`), `_chain_price`'s RECOVERED read |
| FR-11 corpus r23 | `instructions/corpus.py` (`REVISION`, `_REVISION_OF[22]`, `Entry.idea_what`), `instructions/marks.py`'s header, `vectors_script.mechanism_result` |
| FR-13 the idea screen | `backtest.READ_JS` (`idea_boxes`), `founder_screens`, `read_back`; `quality/readers._idea_boxes`; `vectors_screens.idea_boxes_text` |
| FR-14 the intro | `vectors_screens.context_intro`; the codyco typist fixture |
| FR-15 follow-ups | `harness/interviewer_fake.py` (`LADDER`, `ALSO`, `NAMED`, `ALSO_NAMED`, `FILL_DEFAULTS`, `named_pattern`, `said_short`, `over_cap`, `band_written`, `unit_of`, `duration_said`, `percent_said`, `price_said_back`); `vectors_script.follow_up_question`, `lock_values`, `pick_said` |

## Order

1. Corpus revision 23 first: canon is at 23 on the cloud's master, so the suite at the branch's base reads nothing.
2. The rules by name and the score's L32; the idea screen's capture.
3. The writer and the walker (FR-2, 3, 7, 8, 9, 10, 14), with the screen constants.
4. The follow-ups (FR-15).
5. The cards (FR-4) on their own commit; then this plan and the tasks.

## Judgement calls

1. **Where L-rules are reported.** `backtest.LOCK_NOTES` is where every rule since 130 is reported by name; score.py
   restates only L1-L5 and L31. FR-1 names score.py for L32, so L32 is scored there; E9, K10, K8, W12, M7, M8 and P6 are
   reported by name in the lock notes alone (scoring them would move the instruction eval's ruler, which is paid to
   re-measure).
2. **A typed offer row that is the corpus pick** (08-fresco, 14-code-four pick their trial): the cloud leaves the row
   out, so the walker's pick moves to the first row kept, on the draft, the stored list and the walker's typed rows.
   The Answer the founder types still names it -- the cloud's note is the product's.
3. **Buyer and payer's pick wins over the corpus's `picked`** wherever the Answer names a role (Palus's *Nobody else*
   beside the board, and nine more back-test entries): the founder's side, the stored list and the walker all read 1.
4. **The scripted condition** is the step's own -ing phrase and *never slowed my work* (a step over three words by its
   verb, or its two joined verbs), within K7's seven words -- no trade's word; the corpus records none.
5. **The walker's time** no longer reads spec 130's `time_sourced` to answer *not sure*: FR-8 says the corpus entry's
   time. `time_sourced` stays (it still reads the sources) for the record.
6. **206's `held`**: the harness never mirrored 198 FR-3's filter (a rung saying *lose* is never served); 206 widens it
   to *miss*, and the worked cases need it, so it is ported with `LOSS_WORDS`.
7. **The Ability to pay card's Registry line** said *(served `cant_say`: see Open)*; the Open point moved into the
   escape section, so the pointer reads *see the escape* -- the one card line moved beyond FR-4's list, to keep it true.
8. **Two stale pins on master** (`test_decided_before_087`, `test_quality_081`) failed at the branch's base for reasons
   of master's own records (the D-2026-11-03 decisions, cycle 9's table); re-pinned so the gate is green at the head.
9. **The idea screen's boxes** are told to the founder-reader as their own lines (`The idea's boxes, as drawn:`), beside
   the wire's read-back (now with `name`, `whatItIs`, `line`); the readers' prompt moves for the next cycle only.
