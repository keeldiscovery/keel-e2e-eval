# Tasks 132 -- The harness mirrors keel-cloud 205-208 and keel-web 166, 168, 169

Branch `spec-132` (worktree `wt/keel-e2e-eval-132`, `.git` a file; the venv the main checkout's, linked), off
origin/master `994bb8a`. Built by a builder on the coordinator's brief, 2026-11-03 (ET). Read only: keel-cloud-docs master
`7c96988d`, keel-web master `a1848dc3`. No stack, no model, no walk, no paid call, no key read. Nothing merged; the branch
pushed after every commit. Plan: `plan.md`.

| Commit | What |
|---|---|
| `74ce81b` | FR-11: corpus revision 23 -- the reader, `_REVISION_OF[22]`, `Entry.idea_what`, the marks header's r23 digests, the three fixtures, the revision pins |
| `9111344` | the gate's re-pins of master's own records (`test_decided_before_087`, `test_quality_081`) |
| `a2f2b00` | FR-4: the cards' settled Open points, the card tests |
| `92e9e6a` | FR-1 / FR-6 / FR-12 / FR-13: `founders_offer`, score's L32, the lock notes, the idea screen's boxes |
| `564553a` | FR-2 / FR-3 / FR-5 / FR-7 / FR-8 / FR-9 / FR-10 / FR-11 / FR-14: the writer, the walker, the screens |
| `c6cc5f6` | FR-15: the follow-up texts; `tests/test_cloud_205_208_mirror_132.py` (56); 093's ladder commit pin |
| this commit | `plan.md`, these tasks |

## Unit (the gate)

| | passed | failed | errors | skipped |
|---|---|---|---|---|
| origin/master `994bb8a` against keel-cloud-docs `7c96988d` and keel-web `a1848dc3`, in the worktree before any edit (about 20:12-20:16 ET) | 4,714 | 298 | 65 | 248 |
| **branch at `c6cc5f6`, the same siblings (20:48:40-20:52:55 ET)** | **5,332** | **0** | **0** | **61** |

`set -o pipefail; make unit 2>&1 | tail -1` at `c6cc5f6`: `5332 passed, 61 skipped in 253.90s (0:04:13)`, exit 0. Master's 298 + 65 are the corpus at revision 23
(`revision is 23; this eval reads revision 22 only`, behind 187 of its extra skips), keel-cloud 205-208's and keel-web 166-169's
words, and the two stale pins of master's own records.

## Spec 132

- [x] FR-1 `L32` by name -- `instructions.friction.OFFER` / `founders_offer` restate `PurchaseFriction.OFFER`
  (*trial(s)*, *pilot(s)*, *guarantee(s)*, *onboarding*, *money back*, whole words; held to the Java and to
  `FounderReason`'s note by test); `instructions/score.py` names `L32` on a Purchase friction draft row naming one (one
  repair turn, then a note, as the cloud's `breach`); `backtest.LOCK_NOTES["L32"]`.
- [x] FR-2 -- `vectors_script.offer_rows` (eight back-test entries type one: 08-fresco, 14-code-four, 17-expanse,
  21-codyco, 22-andy-ai, 25-bidflow, 26-cubic, 27-blacksmith, 28-relvy-ai; no golden entry), `kept_items` /
  `kept_picked`: the scripted founder-lists writer's draft and the stored list leave the row out, as the cloud does (typed
  and left out: a note, never `L23`); where the entry picked it (08-fresco, 14-code-four), the pick moves to the first row
  kept. The walker's typed rows (`calibration_answers`) are the kept ones, so no *Keel left out* finding names it; the
  Answer still types it.
- [x] FR-3 -- `buyer_payer_pick`: 1 wherever the corpus Answer names a role (Palus: the board, though the corpus picks
  *Nobody else*), 0 only where it names nobody; `saved_list` and `founder_side` (the follow-up's supports) read it.
- [x] FR-4 -- the six cards' Open points 205 settled, in the card's lines word for word as the YAML's `_note_205`:
  Prevalence's and Frequency's wording notes and Purchase friction's `b2b_only` (section 2), Adoption friction's condition
  and Commitment's soft yes with its drift template without *now* (section 3), Ability to pay's escape (section 4); no
  other card line moved but Ability to pay's Registry pointer (*see the escape*, plan call 7). The card tests re-pin to
  the registry (`test_the_open_points_205_settled_are_the_cards_lines_in_the_registrys_words`, the unmoved Open points,
  the drift template).
- [x] FR-5 -- the drift template (the card test, against the JSON export); the two moved Answer questions
  (`vs_screens.PURCHASE_FRICTION_ANSWER_QUESTION`, `COMMITMENT_ANSWER_QUESTION`, held to `AnswerPrompts.java`; the
  registry's Lullaby rows keep the old words, as 205 kept them byte for byte). No code of the harness pinned either
  before; 115's Frequency guidance pin moved to 205's.
- [x] FR-6 -- `E9`, `K10`, `K8` in `LOCK_NOTES` (read off a detail and a repair turn).
- [x] FR-7 -- `adoption_condition`: every scripted Adoption friction row carries `only_if` -- the entry's own where it
  records one, else the step's -ing phrase and *never slowed my work*, within K7's seven words, no word true of every
  step (held to `AskedRules.ONLY_IF_MAX_WORDS` and its rules over every entry).
- [x] FR-8 -- `walker_duration` types the corpus entry's time (10-palus 4 weeks, 17-expanse 6 weeks, every timed
  back-test entry), *not sure* only where the corpus records none.
- [x] FR-9 -- 206's Existing sacrifice stems ported in `cost_question` (`seen_event`, `one_verb`, `without_the_measure`,
  `_loss_gone_without`; *go without*, *fell through*, *what percent of*; `held` skips every rung saying *lose* or *miss*,
  `loss_word`): keel-cloud's 17 worked cases and `CostQuestionInTheirWordsTest`'s frames held word for word, no corpus
  stem says *miss* or *lose*; Commitment's first label *Yes, I would* (the registry's fixed answers, test); the window's
  third clause (`circumstance_clause_of`, `said_of_the_people`, 166's `circumstanceClauseOf`); Purchase friction's held
  Choose -- the walker reads the muted line (`keeltest-waiting`) and no `.keeltest__b` between the pick and the time, and
  `said_faults` holds them.
- [x] FR-10 -- `list_choose(index=)` picks Buyer and payer by index (1 the roles, 0 nobody), never by a role's label; a
  Nobody-else-only list is read and confirmed as a statement (`_choose_confirm`, `choose-confirm`, `choose-statement`,
  sent 0); `choose_faults` holds 168's two options (*Nobody else* first, every role joined: `roles_joined`), the index,
  the recall, the beliefs and the bar over every role; `chain-share-RECOVERED` read before the price pick and a price of
  that shape stopped by name (`RECOVERED_NOT_DRAWN`, `recovered_drawn_faults`); the constants `IMPORTANCE_ANSWER_HINT`,
  `COMPATIBILITY_ANSWER_HINT`, `CURRENT_SOLUTION_HOW_HINT`, `PURCHASE_FRICTION_CHOOSE_BAR_UNDATED` (*Holds if no more
  than 1 in 3 say it would take a long time.*) and `CHAIN_BASE_HELP` (`chain_base_help`) in 168's words, the old ones kept
  by name.
- [x] FR-11 -- corpus revision 23 (the commit above); the scripted writer sends `idea_what` where the entry records one;
  a test holds 22 -> 23 to exactly 207's edits.
- [x] FR-12 -- `W12`, `M7`, `M8`, `P6` in `LOCK_NOTES`.
- [x] FR-13 -- the camera's `idea_boxes` (the name, the what-it-is box, the how, the belief), `read_back`'s `name`,
  `whatItIs`, `line`, the founder-reader's *The idea's boxes, as drawn* lines, the walk's capture beside the page text
  (`idea_boxes_text`); tested on cycle 9's Codyco card (*an AI agent that answers unanswered booking calls*).
- [x] FR-14 -- the codyco typist fixture's intro reads *Five short answers, a phrase each.*; `context_intro(scope)`
  (five on every scope with a gate, four on money alone), held to `translate.ts`.
- [x] FR-15 -- `interviewer_fake`'s ladder and named wordings are the registry's (`test_the_ladder_is_the_registrys_own`,
  `test_the_named_wordings_are_the_registrys_own`): Importance's one / several / none-picked texts and its clip,
  Compatibility's second stem, the six-word short form (`said_short`) where a row has no short name, two picks past the
  cap saying the first alone (`over_cap`), Price's band said back (`band_written`, `unit_of`, `band_round`), Purchase
  friction's band first (`duration_said`), a percent in words on a whole text's spoken line (`percent_said`); the walk's
  composer (`follow_up_question`, `lock_values`, `pick_said`) the same; `named_pattern` reads a pick and a cut row.
  `test_follow_up_ladder.py`, `test_after_131.py` and `test_cloud_200_mirror_129.py` re-pinned, with 130's, 118's and
  093's pins. The walk's follow-up screens are read for R2 and R6 on the next cycle (paid: not run).

## Re-pinned (the specs move them)

- Corpus revision 23: the revision pins of 074, 075, 076, 086, 089, 118, 119 and the r11 shape; 119's 187-edits test
  reads the r21 and r22 records (canon is at 23); the marks header's digests test names the r23 paragraph.
- keel-cloud 205: 115's Frequency guidance; the cards (131).
- keel-cloud 206: 110's cost frames and the three entries' cost items; 082's and 075's cost-step pins
  (`chainBaseHelp`); 199's walker time (FR-8).
- keel-web 166 / 168: 164's Purchase friction Choose page (the held box, the undated bar); 116's Buyer and payer Choose
  page (168's two options, the index, the statement); 117's Compatibility hint.
- keel-cloud 208: the ladder (`test_follow_up_ladder`), 129's named wordings, 131's Importance text, 130's price
  say-back, 118's Compatibility second stem, 093's ladder commit.
- Master's own records: `test_decided_before_087` (the D-2026-11-03 decisions and the D-2026-11-02 merged marks: 52
  snoozed, 10 sent), `test_quality_081` (TABLE.md at RUBRIC_VERSION 5).

## Not done as written / owed

- E9, K10, K8, W12, M7, M8, P6 are reported by name in the lock notes; `instructions/score.py` restates none of them (plan
  call 1).
- The cards' *Yes, I'd start one* bad example (cycle 4's AirCaps) is history and stays; the eval's own fixture registry
  (`tests/v9_fixtures`) keeps 118's labels.
- R2 and R6 on the walk's follow-up screens, and every walk, wait for the next paid cycle (the founder's word).
