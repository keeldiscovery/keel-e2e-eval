# Tasks 089 -- The harness reads corpus revision 19, the three moved controls, and the question frames in the people's words

Branch `089-revision-19-and-the-controls` (worktree `wt/eval-089`, `.git` a file), off master `305f9b3` (088 merged).
Read only: the live keel-cloud-docs checkout at **`ad5f6441`** (spec 160's docs; carries 158 `e3d34831`, 159 `1cf2ebc3`
and 160, contract 47, **corpus revision 19**). No snapshot was needed: this spec is what makes master green against the
live checkout, and it is gated there. **`REVISION` 18 -> 19**; `MARKS_VERSION` 21 and `RUBRIC_VERSION` 2 unchanged;
**`INTERVIEWER_MARKS_VERSION` 13 -> 14** (FR-3, IM20). **No paid call**: no walk, no reader, no adviser call, no model,
no `make eval`. Nothing merged or deployed; every commit pushed to the branch.

**Built in one step.** 158, 159 and 160 had all merged (cloud master `ad5f6441`) when this was built, so FR-5 went with
the rest. keel-web 135 (the three controls on the screens) is **not built**: the screen and AI-link walks of FR-2 to FR-4
are written to its spec (`keel-web/specs/135-three-respondent-controls/spec.md`) and unit-held by source order; the
journeys that prove them are the coordinator's, on a stack with web 135 (below).

| Commit | What |
|---|---|
| `6bfc2dd` | FR-1: `REVISION = 19`, rule D19 (`tests/test_corpus_r19.py`), RA19 in the reader, the registry tables, the r19 digests, the fixtures |
| `79232af` | FR-2: Frequency from 1; the five recorded 0s replayed as CANT_RECALL, named |
| `9bc2829` | FR-3: Importance one pick, then one more (screens, AI link, IM20 v14, classifier, S7, the fake's MORE) |
| `5388afb` | FR-4: Relative advantage one scale (the question, one code, no advantages anywhere, the brief's line and decisions) |
| `bb07de9` | FR-5: the frames in the people's words (keel-cloud 160) |
| `6a83261` | FR-6: D-2026-10-30-01 held; D-13 / -14 / -15 `merged` confirmed |
| this commit | this file, `AGENTS.md`'s spec-089 paragraph |

## Unit (the gate)

`make unit`, against the live keel-cloud-docs checkout at `ad5f6441`:

| | passed | failed | errors | skipped |
|---|---|---|---|---|
| master `305f9b3` (088's tasks.md records the same) | 3,482 | 78 | 40 | 209 |
| branch at FR-4 (`5388afb`) | 3,765 | 0 | 0 | 63 |
| branch at FR-5 (`bb07de9`) | 3,767 | 0 | 0 | 63 |
| **branch at FR-6 (`6a83261`; the docs commit after it touches no code)** | **3,768** | **0** | **0** | **63** |

FR-1 to FR-3 were committed with reds that later FRs own (the harness still sent `advantageIds` and the old RA ladder
until FR-4); the tree is green from FR-4 on.

Master's red set on the live checkout is 088's, node for node: every error and 72 failures `CorpusError: ... revision is
19; this eval reads revision 18 only`, plus the six 086 and 088 named (`test_backtest.py:76`, `test_corpus_r18.py:135 /
:160 / :276`, `test_follow_up_ladder.py:69`, `test_interviewer_marks.py:918`). **All of them are green on the branch**
(`test_corpus_r18.py` is `test_corpus_r19.py` now). The skips fall from 209 to 63: master skipped every test that reads
the canon off its revision (`v9_fixtures.CANON_NOT_R13`). Of the branch's 63, 55 are the standing ones (the journey's revision-2 readers, keel-web
131's two); the **8** this spec added are the **stale Gradle outputs** (judgement call 7) -- 6 on the spoken record, 2 on
the brief-facts compare (`test_instruction_brief_facts`, `test_report_marks`): keel-cloud's `build/brief-facts/` and `build/spoken-corpus.txt` in the live
checkout were written by a run on 2026-10-28 (before 152, 158 and 159), so the brief-facts compare and the spoken
record's tests skip by name until a `./gradlew test` there rewrites them (`_at_159`, `fx.skip_a_spoken_record_before_159`).

## FR-1 -- revision 19 -- `6bfc2dd`

- [x] T001 `instructions/corpus.py`: `REVISION = 19`; a *Revision 19 read* paragraph (159, the one rule, no standing
  moved, the five 0s read as recorded) above revision 18's, which is kept; `_REVISION_OF[18]` names it *MARKS_VERSION 21's
  corpus before keel-cloud 159 (Relative advantage answered positive / neutral / negative with the founder's benefits
  ticked under positive, `benefit_with_advantages`)*, so a file at 18 is refused by name.
- [x] T002 Rule RA19 in the reader (`_check_benefit_first`): the row `scale_four` over `a_lot_better`, `a_little_better`,
  `no_difference`, `worse`; a pick one of the four (or the chip), never a benefit beside it. The founder's side unchanged
  (a `benefit_list` of one to four). `_check_pick` reads `scale_four` as a fixed answer.
- [x] T003 `instructions/registry.py`: `RESPONDENT_CONTROLS` with `segmented_1_to_n`, `pick_one_then_one`, `scale_four`
  (the three old names gone); `FREQUENCY_MIN` 1, `FREQUENCY_CONTROL`, `IMPORTANCE_CONTROL`, `ONE_MORE` *And one more?*,
  `NOTHING_ELSE` / `NOTHING_ELSE_CHIP` / `NOTHING_ELSE_LABEL`; `FIXED_ANSWER_CONTROLS` gains `scale_four`; `COMPARE_RULES`
  loses `benefit_first`; `BENEFIT_CONTROL` `scale_four`, `BENEFIT_RULE` `fixed_last_two_against`, `BENEFIT_CODES` the four,
  `BENEFIT_LABELS`, `BENEFIT_SUPPORTS`; `from_three` (= `ScaleFour.fromThree`, the one rule); invariant 5 on the scale
  (read by `fixed_last_two_against`, its four, labels and supports code's, the founder's `benefit_list`; 159's own
  invariant). `RECORDED_CONTROLS` (judgement call 1).
- [x] T004 **Rule D19** (`tests/test_corpus_r19.py`, `git mv` of `test_corpus_r18.py`): the 35 canon entries beside
  keel-cloud's `corpus-r18/` and `backtest-r18/`; every leaf difference the revision (18 -> 19), Relative advantage's row
  (control and codes, all 35), a Relative advantage pick equal to `from_three` of its r18 pick (**71** golden, per entry
  10/10/10/10/11/11/9, and **361** back-test: 267 a lot better, 0 a little better, 73 no difference, 21 worse), the chips
  as they were, and on the golden seven the row's `optionCounts` added -- nothing else. A second test: `expected` is r18's
  whole but that field, and the four counts are 159's (*The rows* table), a lot + a little = inside, no difference +
  worse = outside. **D18 kept as the record** (mirror against mirror: `corpus-r17/` + `backtest-r17/` beside `-r18/`),
  D17 and D16 as before; `check_corpus_r19.py` **OK on all 35**; all 35 load at 19; r18's 03-lullaby refused by name.
  The r14 12-transload case reads the scale too (the row and every pick by the one rule) so it still reaches the Answer box.
  **The spec's "two decision sentences reworded" are not in the corpus**: D19 finds no such leaf (the corpus records no
  decision sentence; 159 reworded them in `DecisionChangeCorpusTest`) -- they moved in the brief-facts mirror (FR-4).
- [x] T005 `instructions/marks.py`'s header: a *Corpus revision 19* paragraph above 18's -- **v21 stands** (no mark reads
  the Relative advantage pick's shape or benefits; `compare_correctness` reports `optionCounts`, never marks them) -- and
  the seven r19 digests (below); `marks.toml`'s comment.
- [x] T006 The three fixtures (`09-fixture`, `10-fixture-b2b`, `99-broken`) at 19 by the one rule (a text edit, their
  header saying so); the slice registry's three moved rows in 158 / 159's words, the scale's `fixed_answers` and
  `supports`; `broken/5-benefit-*.yaml` fail invariant 5 on the scale (a wrong support; a non-list founder control).
- [x] T007 `vectors_script._pick` reads Relative advantage's code as it stands (the reader's half; FR-4 drops the rest).

**The marks digests** (revision 19, canon bytes at `1cf2ebc3`, unchanged through `ad5f6441`, equal to `corpus-r19/` and
to 159's tasks.md):

| File | sha256 |
|---|---|
| `01-countly.yaml` | `431a56d23be2de5cf84da10007802aa87daceb75bb0a9b4c57afa0461da273b3` |
| `02-compliancelog.yaml` | `5d2152bf7b0f5a5def830c79907f5e139761a48d3ff121f1a56eb55d6064e16f` |
| `03-lullaby.yaml` | `d96220665201746e05d4b4794eea03bb0887e4d6d6dc0aed4a5db6daa50e4c08` |
| `04-linerly.yaml` | `27a22794db252cd39113498cb48e115a3c1c3200b429ee416bbaa4eb572d434e` |
| `05-paidly.yaml` | `91a37d92128f927516bfaf09ea64cb3a02d0d5fbde25c9637aee835126693ba5` |
| `06-repeatline.yaml` | `c971a78f4ea8be5c2ac1eab6d790576bae7a06f9e188bc3af74e7bb0bd0a44f6` |
| `07-mulchrun.yaml` | `735476c9c828e0ced83695518771499ac298f8dc864c4e1ac2f500418c046e02` |

## FR-2 -- Frequency from 1 -- `79232af`

- [x] T008 `harness/vectors_script.py`: the count is sent 1..N as recorded (`Pick(scale=...)`, `as_wire`'s `scale`);
  `frequency_fits`' docstring on 158's 1..count.
- [x] T009 **The five 0s** (`ZERO_AS_CANT_RECALL`, `_frequency_from_one`): a recorded Frequency below `FREQUENCY_MIN` is
  sent as the item's escape, `{"chip": "CANT_RECALL"}`, and named in **`PersonInputs.notes`** (`zero_note`: who, the
  recorded 0, what is sent, `D-2026-10-30-01`); `corpus_scenario` records each note as a journey finding for that person.
  Across the 35 entries exactly the five carry a note: 04-linerly **Bruno Costa, Dmitri Volkov, Gwen Price** (12 MONTHS)
  and 05-paidly **Petra Novak, Talia Ben-David** (3 MONTHS). The corpus is never edited: the files still say 0 after a
  yes, the reader keeps it (rule A's *0 to the founder's out of* unchanged), the engine reads them as recorded.
- [x] T010 `harness/vectors_screens.py` taps the radio by its count (1..N; no 0 is drawn, none is sent);
  `harness/classifier_guard.py` reads Frequency's controls (`segmented_1_to_n`, the number box, and `segmented_0_to_7` for
  a recorded run) and the number box's least from the served `numeric.min`; the AI leg's one-of filter knows the new name.
- [x] T011 Tests (`tests/test_controls_089.py`): the five and nobody else; the corpus still records them; any other 0
  replayed and named; the classifier's range from 1.

## FR-3 -- one pick, then one more -- `9bc2829`

- [x] T012 The text link (`vectors_screens.Interview._one_then_one`, keel-web 135 FR-2): the first option tapped, the
  served `secondAsk.question` (*And one more?*) waited for, then the second option -- or *Nothing else* for a person with
  one pick; the item's screen is read on the **first** ask (the question, the list, *None of these*) and keeps what the
  second ask drew (`second_ask`: its prompt and chips), which `corpus_scenario` holds to the served `secondAsk` (*And one
  more?*, chips `["Nothing else"]`). A checkbox or a radio, whichever 135 draws (judgement call 3).
- [x] T013 The AI link (`interviewer_leg._Walk.tap_one_then_one`): the first tap; the item stays (same question, no ring,
  1.5 s); the item's `more` clip (ITEM_MORE) waited for; the second tap or *Nothing else* (`Player.tap_chip_named`);
  *Save and next* pressed only where the page still draws it enabled (recorded `save_pressed`); `how` TAPPED.
  `_wait_next` reads *And one more?* as the same item. The spoken pick still names both at once (158 T014: the first ask
  is a multi of two).
- [x] T014 **IM20 re-read, `INTERVIEWER_MARKS_VERSION` 13 -> 14**: one tap holds the item while the ITEM_MORE clip plays,
  the second completes it, the picks sent `how` TAPPED (it read two ticks and Save, a third ignored). The leg records
  `more_played`, `question_same`, `checked`, `save_pressed`.
- [x] T015 `corpus_scenario`: `PICKS_NEEDED["pick_one_then_one"]` 2 and **one pick + `NOTHING_ELSE` a whole answer**
  (`NOTHING_ELSE_CARRIES`: where one of two picks is not offered, the other is sent with *Nothing else*, named, never left
  to the escape); `ROW_CONTROLS` gains `pick_one_then_one` and `scale_four`; the *Pick two.* hint only on a `pick_two`.
- [x] T016 `harness/interviewer_fake.MORE` = *And one more?* (`ItemFrames.ONE_MORE`; IM's framing-line test reads it
  through `PassageComposer.ONE_MORE = ItemFrames.ONE_MORE`); `harness/classifier_guard.py`: `pick_one_then_one`'s second ask
  is its own `Served` (`ask: second`, one pick over the same labels, escape *Nothing else*); `instructions/spoken.py` S7:
  *; pick two* is never said (the transform stays `one_then_one_more`); `evals/noise/pipeline.py`'s docstring.
- [x] T017 Tests: `test_controls_089.py` (the words held to `ItemFrames`, the registry of record, the second ask's read,
  one pick + Nothing else, the two walks by source order, IM20); re-pinned below.

## FR-4 -- one scale -- `5388afb`

- [x] T018 `vectors_script.benefit_question` = `ScaleFour.question`: *On your last {occasion}, would {name} have made it go
  better for you, or not?*, the plain frame *Would {name} ...* past 20 words (06-repeatline's 22); `BENEFIT_FRAME`.
- [x] T019 `Pick.advantages` and `advantageIds` gone; Relative advantage left `PICKED_AMONG_ITEMS` (the stranger answers
  the four, never the founder's benefits); the screens' benefit ticks gone (one radio by its served label); the AI leg's
  advantages ask, `by_prompt`, `advantages()`, the try's advantage mapping and `_heard_for`'s advantages gone; the read-
  aloud still prefers Relative advantage (*A lot better* / *A little better* share words); the way back and the veto on
  every one-of (`plain`); `corpus_scenario`'s unoffered check and body normaliser on `optionIds` alone; the healthy
  prelude's pick `a_lot_better` and its row's `optionCounts` on the four.
- [x] T020 `instructions/spoken.py`: `yes_no_per_benefit` retired (S9: Relative advantage `none`); `classifier_guard`: the
  scale a single, the advantages ask gone.
- [x] T021 The follow-up: `interviewer_fake.LADDER`'s Relative advantage rung on `no_difference` / `worse`, *You said
  {solution_name} wouldn't make much difference on your last {occasion}. What would make {job} better for you, if
  anything?* (text and spoken), `LADDER_SHA` `1cf2ebc3`; `vectors_script.follow_up_question` says a *worse* as worse
  (`codes == ["worse"]`), no `{benefit}`.
- [x] T022 The brief-facts mirror (`instructions/brief_facts.py`): `benefit_view` = `BriefFacts.Benefit` `{better, aLot,
  aLittle, noDifference, worse, n}` (the served `chart.benefit` where present, else the row's counts); the card *N of M ·
  said it would have gone better, K of them a lot* (`gone_better_line`); `DECISION_CHANGE` 02-compliancelog *only 4 of 9
  said it would have gone better, 4 of them a lot, and 5 did not.* and 06-repeatline *only 3 of 9 ..., 3 of them a lot,
  and 6 did not.* (`DecisionChangeCorpusTest`).
- [x] T023 The quality readers' anchors: **none named the benefit tick** (`quality/RUBRIC.md`, `quality/readers.py` read;
  nothing to move, `RUBRIC_VERSION` 2).
- [x] T024 Tests: `test_controls_089.py` (the frame held to `ScaleFour.FRAME`, one code sent, the one rule held to
  `ScaleFour.fromThree`, no transform, the line and the two decisions held to `BriefFacts` / `DecisionChangeCorpusTest`,
  02's card); re-pinned below.

## FR-5 -- the frames (keel-cloud 160) -- `bb07de9`

- [x] T025 The served Frequency, window first: `vectors_script.frequency_served` and `instructions/wording.frequency_respondent`
  (*In the last 7 nights, on how many nights did you ...?*; no clause *... did that happen?*); `frequency_held` (160 FR-2,
  judgement call 4): the whole, else the unit said once (*In the last 7 days, on how many did you ...?*), else the cut,
  else *did that happen?* -- Code Four falls to it, Fresco is cut as before (*... by hand?*).
- [x] T026 **E4 keeps its measure** (160 judgement call 2): `vectors_script.frequency_question` (the gate-clause check in
  `event_base`) and `wording.frequency_measured` (`framed_fault`) are `frequencyMeasured`, the frame before 160, so no gate
  pin moves; `frequency_held_before160` serves a Frequency stored before 160 in its own frame.
- [x] T027 Importance (*Think of your last {occasion}. Which one of these ...?*) and Current solution (*How did {phrase}
  go?*): **no harness code composes either**; the spoken tests' data and the registry's Lullaby examples are held to the
  new words (below).
- [x] T028 Tests: `test_controls_089.py` (the frame held to `WindowFrame`'s source, E4's measure, the registry of record's
  three Lullaby examples); re-pinned below.

## FR-6 -- decided before -- `6a83261`

- [x] T029 `D-2026-10-29-13` and `-14` carry `merged = "e3d34831"` (158) and `-15` `merged = "1cf2ebc3"` (159) --
  **written on master at `c474dfe`**; confirmed, no edit.
- [x] T030 **`D-2026-10-30-01`** added, `held`: cycle `20261028-f48f256` (the cycle that proposed 35, which became 158),
  proposal 35, row PROBLEM / respondent / `problem.frequency` / item, fix *the five recorded 0s*, **`until =
  "spec-merged"` with no spec** -- 087's validator takes it (a spec is required on `taken` only; `merged` only on a
  spec-merged entry), it stays active until the coordinator writes `merged` on the spec the founder's decision becomes, and
  its fix names no location the cycle writes, so it snoozes no weak row (the dry advise still lists 15 and would send 47).
  The cycle-id form was not used: the next cycle's id is a date and a cloud sha not yet known, and a guessed one would end
  the snooze by string order (judgement call 6).

## Every pin moved

| Pin | Was | Now | Why |
|---|---|---|---|
| `test_corpus_r18.py` -> `test_corpus_r19.py` | D18 against canon | D19 against canon; D18 (`-r17` beside `-r18`), D17, D16 mirror against mirror; `check_corpus_r19.py` | FR-1 |
| `test_instruction_corpus_r11` refusal table | *reads revision 18 only*; the benefit-first refusals | *reads revision 19 only*, revision 18 refused by name; RA19's four refusals | FR-1 |
| `REVISION == 18` (`test_follow_ups_075`, `test_founder_walk_076` x2, `test_recorded_path_074`, `test_study_scopes`, `test_corpus_r11_shape` x2) | 18 | 19 | FR-1 |
| `test_corpus_r11_shape` rule R / A, `test_every_relative_advantage_is_benefit_first` | a row's control the registry's; `benefit_with_advantages` | the recorded names read as 158's; `..._is_one_scale` | FR-1 |
| `test_instruction_marks` r18 digests | the seven at `21395ab0` | `..._r19_digests_...`: the seven at `1cf2ebc3`, *v21 stands* | the canon bytes moved |
| `tests/fixtures/registry/slice.yaml`, `broken/5-benefit-*.yaml` | `segmented_0_to_7`, `pick_two`, `benefit_with_advantages` / `benefit_first` | 158 / 159's rows; invariant 5 on the scale | FR-1 |
| `tests/fixtures/corpus/09`, `10`, `backtest/99` | r18, the three answers | r19, the one rule; 09 / 10's row `optionCounts` | FR-1, FR-4 |
| `tests/fixtures/compare/09-fixture.{agree,disagree}.out.json` | `positive=6, neutral=2, negative=0` | the four's counts | FR-4 |
| `test_interviewer_marks` framing lines (`ONE_MORE`) | `PassageComposer`'s literal | read through `ItemFrames.ONE_MORE` | 158 T013 |
| `test_interviewer_marks` IM20 fixture and mutations, `INTERVIEWER_MARKS_VERSION == 13` (x3 files) | two ticks, Save; 13 | one tap, the more clip, the second; 14 | FR-3 |
| `test_instruction_spoken` Importance | *which two*, *; pick two*, the plain count line an S7 fault | *Think of your last morning. Which one ...*, the plain count line; *; pick two* the S7 fault | 158, 160 |
| `test_instruction_spoken` the 21-word stem | the three answers, `yes_no_per_benefit` | the scale's frame and four, `none`; the old transform an S9 fault | 159 |
| `test_instruction_spoken` number and Current solution data | *On how many of those 7 nights*, *0 to 7*; *How well did ... work?* | window first, *1 to 7*; *How did ... go?* | 158, 160 |
| `test_classifier_guard` served items | the advantages ask | the scale a single, no advantages ask | 159 |
| `test_journey_through_a_host` unoffered picks | the advantages kept | a scale code not offered goes to the escape | 159 |
| `test_follow_up_ladder` (the ladder, two picks) | `neutral` / `negative`, 154's words | `no_difference` / `worse`, 159's words | 159 |
| `test_follow_ups_075` (four picks), `test_revision_16_walk` (RA's spoken line, Paidly's owed RA, *worse*) | `neutral` / `negative`; *would have made no difference ... better?* | the scale's codes; *wouldn't make much difference on your last invoice ... better for you, if anything?* | 159 |
| `test_vectors_journey` wire codes, the RA question | `benefit_n` advantages; *made things better* | one scale code, no `advantageIds`; *made it go better for you*, the plain frame | 159 |
| `test_instruction_brief_facts` the card | *said it would have made their last morning better* | *6 of 8 · said it would have gone better, 6 of them a lot* | 159 |
| `test_instruction_window_frame`, `test_after_131` (Code Four, Fresco) | *On how many of those ...* | window first; the measure and the before-160 frame kept beside | 160 |
| `test_decided_before_087` the file of record | 20 entries | 21 (`D-2026-10-30-01`) | FR-6 |

**Not moved, with why:** the gallery's and the back-test's recorders keep their `advantages` / `advantagesPrompt` fields
(an empty list on a 159 build; `test_gallery.py:376` pins the record's key order and the recorded Fresco run carries
them); `tests/fixtures/gallery/*`, `tests/fixtures/sample/s006-reads.json` and the quality score files -- recorded runs,
as 085 and 086 left them (none is compared with served words; rewriting them would falsify the record);
`harness/classifier_cases.py` and `evals/noise/*` -- the classifier corpus and a recorded experiment, whose labels the
classifier reads (159's call 10 keeps keel-cloud's own); `quality/readers.spoken_template`'s `pick_two` flag (a bundle
recorded before 158 said it); `corpus_scenario.ONE_MORE_ASK` (the founder's Check screen, which 158 left);
`instructions/marks.py`'s history paragraphs; `test_interviewer_marks`'s `RA_TEXT` (any served string).

## Acceptance

- [x] `make unit` against the live keel-cloud-docs checkout at `ad5f6441`: **0 failed, 0 errors** (master 78 failed /
  40 errors).
- [x] `tests/test_corpus_r19.py` on keel-cloud at 159's merge or later: green on `ad5f6441`.
- [ ] `make eval K=s005`, `K=s006`, `K=s007` on the local stack at a cloud sha carrying 160 and **web at 135**, the three
  controls walked -- **left for the coordinator** (the stack is down; starting it, and any journey, is the coordinator's;
  keel-web 135 is not built yet). What to look at: the screens' item records' `second_ask` (S-005 / S-006 / S-007's
  Importance), the findings naming Petra Novak and Talia Ben-David (S-006: *I can't recall* sent), the read-aloud and IM20
  on S-005 / S-006's AI link, and Relative advantage tapped on the scale.

## Judgement calls

1. **The corpus's recorded control names are read as 158's** (`registry.RECORDED_CONTROLS`): 158 cut no revision, so
   revision 19's rows still say `segmented_0_to_7` and `pick_two`; the stored answers are the same integer and the same
   two codes (158 T003, T011), so rule R reads them as `segmented_1_to_n` / `pick_one_then_one` rather than refuse the
   whole corpus or edit it.
2. **The five 0s are replayed for any 0, named, not by a list alone**: `_frequency_from_one` sends any recorded count
   below 1 as CANT_RECALL with a note, and `ZERO_AS_CANT_RECALL` names the five the corpus holds (a test holds the two
   equal), so a future 0 is named rather than refused on the wire mid-journey. The notes are `PersonInputs.notes` (and
   journey findings), not `remapped` -- `remapped` is Commitment's re-expression, which the scenario re-reads against the
   served options.
3. **keel-web 135 is not built, so its controls are walked from its spec**: the first tap by option label as a checkbox
   or a radio (`Locator.or_`), the second ask found by its served words, *Nothing else* by label among the chips; on the
   AI link *Save and next* is pressed only where it is still drawn enabled. No marker as 088's: a stack without 135 cannot
   serve contract 46 / 47 to the web at all, so the journeys wait on 135 whole.
4. **The item screen of a one-then-one item is read on the first ask**: after the first tap the page shows the second
   ask's prompt and *Nothing else*, so reading after the answer (as every other item is read) would hold the screen to
   the wrong chips; the second ask is recorded beside it and held to the served `secondAsk`.
5. **IM20 is re-read, not retired** (`INTERVIEWER_MARKS_VERSION` 14): the mark's subject (a tap waits for the person, the
   answer is TAPPED) stands; its record changed, which is the module's rule for a bump. `MARKS_VERSION` 21 stands: no
   corpus mark reads a moved field.
6. **`D-2026-10-30-01` is `until = "spec-merged"` with no spec**, not a cycle id: the next cycle's id (a date and a cloud
   sha) is unknown, and `active` compares ids by string, so a guess could end the snooze early; spec-merged keeps it
   active until the coordinator writes `merged` on whatever spec the founder's decision becomes (or he edits the entry).
   The validator accepts it (spec is required on `taken` only).
7. **A stale Gradle output is skipped by name** (`_at_159` for `build/brief-facts/`, `skip_a_spoken_record_before_159`
   for `build/spoken-corpus.txt`), as `_at_145` / `cloud_facts_at_104` already did: the live checkout's `build/` was
   written on 2026-10-28, before 152, 158 and 159, and this repository never runs Gradle in a sibling checkout.
8. **Relative advantage left `PICKED_AMONG_ITEMS`**: the stranger no longer picks among the founder's benefits, so no
   scripted code is mapped onto `benefit_n`; the founder's `benefit_list` keeps its positional codes on the founder side.
9. **`benefit_view` reads the served `chart.benefit` first, the row's counts else** (and, on a row before revision 19
   with no counts on the four, its inside as *a lot*), so the mirror reads a journey's wire and the corpus alike.
10. **The frames are mirrored where the harness composes them** (Frequency's served and held frames, E4's measure); no
    harness code composes Importance's or Current solution's frame, so those moved only as test data and as the
    registry's examples the tests read.

## What did not hold

- `make eval K=s005` / `s006` / `s007`: not run (the stack is down; the coordinator's) -- and they need keel-web 135.
- **The screen and AI-link walks of the three controls are unproven against a page**: written to keel-web 135's spec,
  held only by source order in `make unit`. The first journey on a 135 build is their real test (roles, the second
  ask's placement, whether the AI link still draws *Save and next* for the second tap).
- **The spec's "two decision sentences reworded" as a D19 leaf**: none is in the corpus; they are `DecisionChangeCorpusTest`'s,
  mirrored in `brief_facts.DECISION_CHANGE` (FR-4).
- The live checkout's `build/brief-facts/` and `build/spoken-corpus.txt` predate 159, so the brief-facts compare and the
  spoken record skip until keel-cloud's Gradle run rewrites them; they were not compared on 159's words here.
- The five 0s wait on the founder (`D-2026-10-30-01`).
