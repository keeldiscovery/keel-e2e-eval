# Tasks 141 -- The harness mirrors keel-cloud's cycle 14 round

Branch `spec-141`, worktree `/Users/athulrajeev/Documents/projects/wt/eval-141` (`.git` a file), off master `245d398`.
Nothing paid; no stack, no model, no key, no walk; the unit suite only. Against keel-cloud-docs master `d019f1ca`
(219, 228, 220, 224, 221, 226, 227, 222, 225 and -- merged while this branch was built -- 223; 229 builds on `spec-229`)
and keel-web master `480463e1` (178 built); neither checkout edited. Not merged; master untouched. The corpus yaml,
`quality/decisions.toml`, the readers' rubric and `RUBRIC_VERSION` untouched.

| Commit | What |
|---|---|
| `d67ad78` | plan.md; FR-4 Commitment (221) -- six of master's nine back to green |
| `7b37850` | FR-5 Prevalence (224); `tests/test_cloud_219_228_mirror_141.py` |
| `174aba7` | FR-2 Relative advantage (219) |
| `c2eec3c` | FR-3 Price (220) |
| `2c8a63f` | FR-6 Current solution (226, 228) |
| `efcb813` | FR-7 Existing sacrifice (222, 227) |
| `94798c4` | FR-8 Compatibility (225) |
| `32b1ec6` | FR-8 Importance (223) |
| `862c0cb` | FR-8 keel-web 178 (the coordinator's addition): the note, the line, *Per* empty; `tests/test_web_178_mirror_141.py` |
| `9dc02e1` | FR-1 the reader digest, last |

- [x] T001 FR-4 Commitment (221). `instructions/spoken.py`: `STEP_OPTION_MAX_WORDS` 9 -> 11, `STEP_MAX_WORDS` 9;
  `first_yes` cuts at nine; `step_cut` (`ItemFrames.stepCut`, the lock's S4 note); `_second_step` held to eleven less the
  frame through `smaller_said` (an act-first smaller step in its -ing form, `opens_on_its_act`, `SMALLER_ACT_VERBS`);
  `smaller_act` / `SIZE_OR_COST` and `restates_the_step` (`ItemFrames.restatesTheStep`, now mirrored) read by
  `commitment_answers`; 129's cut kept by spec number (`first_yes_before221`, `second_yes_before221`) in `served_labels`
  for a lock stored before. `instructions/step_cost.py` `DATA_ACTS` (pinned to the cloud's pattern string).
  `harness/vectors_script.the_step` says an act-first step as its act. `instructions/brief_facts.py` the soft yes
  through `smaller_said` (`BriefFacts.secondYes`). `instructions/marks.py` revision 16's note retired.
  **Pins moved:** `test_instruction_spoken` (the eleven-word test replaces the nine-word one; Lullaby's Yes whole; 198's
  Buyer and payer four in the record), `test_cloud_198_mirror_130` (`BriefFacts`' soft-yes source line),
  `test_cloud_211_mirror_133` (`PRICED` gains 01-countly *install*, 17-expanse *measure*, 26-cubic *install*; the one
  golden priced step is Countly's; Linerly stands in for a free step), `tests/v9_fixtures.GOOD_LISTS` (the good
  Commitment draft carries Keel's free step), `test_vectors_journey.SAVES` (Commitment 1 to 2).
- [x] T002 FR-5 Prevalence (224). `instructions/wording.py`: `STATE_VERBS`, `STATE_FORMS`, `VERDICT_WORDS` (every tense,
  `_VERDICT_VERB_FORMS`), `state_head` (*have* read whole: obligation, perfect, *had X do Y*), `verdict_word` (*have to*
  at the head allowed), `packed_fault(event, went_wrong, window)` after 212's checks, the window's unit in the sentence;
  `score.act_that_hurts(window=)`. `harness/vectors_script.PROBLEM_CLAUSES["06-repeatline"]` -> *had to type a refill
  request in* / *have to type a refill request in* (the harness's fixture; `ACT_THAT_HURTS` keeps *by hand*, as 224
  says). The lists pinned to the cloud's source and the instruction's gate rule. `test_cloud_212_mirror_136[06]` green.
- [x] T003 FR-2 Relative advantage (219). `spoken.hard_case_clean` / `hard_case_said` / `hard_case_anchor`
  (`HardCase.clean/said/anchor`), `advantage_stem(..., hard_case_field)` -- *Think of {hard_case}.* first, then 214's,
  then 198's; `corpus.hard_case_belief` (`HardCase.belief`), `advantage_belief_219` and `advantage_belief(...,
  hard_case_theirs)`. `harness/vectors_script`: `HARD_CASES` (empty, judgement call 3), `hard_cases`, the scripted
  Prevalence carries them where held; `problem_clause` -- the scripted PROBLEM_INTERPRET result carries the clause
  fields (event, routine, went_wrong, no_sayer, the hard cases) in a study without the problem's questions where the
  entry holds the founder's clause, so the gate the card's clause asks is the writer's (`event_base`): no E10.
  Pinned: `RelativeAdvantageHardCaseTest`'s five items and beliefs word for word, Lullaby's `VectorFixtures.HARD_CASE`.
- [x] T004 FR-3 Price (220). `vs.price_question` (`CostEstimate.priceQuestion` / `priceSubject`),
  `corpus_scenario.price_question_faults` held in `_hold_the_price_boxes` (the served COMMERCIAL question); the five
  cycle-14 gallery entries' question and `price_belief_owed` name the idea (four beliefs word for word as
  `PriceNamesTheIdeaTest`; AirCaps' people are the corpus's *Deaf and ...*, the cloud fixture's *Deaf or ...*).
- [x] T005 FR-6 Current solution (226, 228). `corpus_scenario.served_line` (`line`, else `lineAfter` + 1) and
  `line_after_faults`, read in `_served_line`; the walk sends no `lineAfter` (`vs.saved_list` carries none); the golden
  Countly and Linerly ladders' W-rung repair turn is read by name (`backtest.LOCK_NOTES["W-rung"]`, with 219's H1-H4 and
  E10, 225's L-kind) and counted nowhere; `brief_facts.current_solution_bar` stands. 228: spec 140 FR-4b already reads
  the draft's two fields; nothing more.
- [x] T006 FR-7 Existing sacrifice (222, 227). 222: `vectors_script._rate_stem` (`CommercialChain.rateStem`, code's own
  readings marked), `loss_clause_wanted`, `loss_clause_said` (`LossClause.said`: the cut, the did-you turn),
  `loss_clause_frames`, `loss_clause_question`, `cost_question(..., loss_clause)`; the scripted part-1 result's
  `loss_clause` (`scripted_loss_clause`, `LOSS_CLAUSES` empty -- judgement call 4) and `cost_item` reading it. Pinned:
  `SacrificeItemNamesTheLossTest.theFiveEntries` (wanted on Codyco, AirCaps, Palus; Expanse and Fresco unchanged).
  227: `chain.typed_unit`, `count_rate`, `cost_said` / `cost_belief` (a count *about 12 conversations per person a
  month*, no *of {base}*; the typed unit kept beside a percent of a named base and where the user pays, the people's
  own noun dropped; `role_word` read no more), `cost_said_before227` by spec number; `corpus.spec227_cost`
  (`VectorCorpusFixture.spec227Cost`) after `spec216_payer` / `spec213_chain` in the loader's sentence and phrase
  checks; `chain.equation_per_drawn` owes *· per {unit} ·* beside a percent (`equation_per_drawn_173` the web before);
  `corpus_scenario.chain_words_owed` bans it no more. **Pins moved:** `test_cloud_213_mirror_137` (Palus' phrase, the
  count, the chain words, the equation), `test_cloud_199_mirror_130` (Expanse's phrase read by 227's rule),
  `test_referee_follows_193_123` (*per person*, *per terminal* -- as the cloud's own test moved).
- [x] T007 FR-8 Compatibility (225). The scripted writer writes `kind` beside `settled_by` (`condition_kind(...).lower()`:
  today's frame, no L-kind turn); `spoken.KINDS`, `written_kind`, `kind_of` (`ItemFrames.kindOf`), `opens_on_could`,
  `held_kind` (`ScreenResultApplier.heldKind`); `score.kind_faults` (L-kind, `rowKinds`) in `list_faults`; the tested
  kind read first where a row records one (`corpus._tested_kind`, `vs.founder_side`'s `compatibility_steps`).
  `score.settled_faults` stands (`settledRows` did not move; the hand-on 225 retired lives in `heldSuggestion`, which
  the eval never mirrored). Pins: the good fixture and `test_instruction_score`'s drafted Compatibility rows carry a kind.
- [x] T008 FR-8 Importance (223, merged at `d019f1ca`). `writers_rules.own_row_from_clause` (`OwnRow.fromClause`:
  act first, *had to* / negation read past, subject first, *and* turned, the cut) and `own_row_note` / `OWN_ROW_NOTE`
  (`OwnRow.note`); `vs.code_own_row` (from the scripted `went_wrong`; none off the problem's scope or where another row
  says it); the strict walk's Check list (`_corpus_list`) and its belief box
  (`importance_belief_on_code_own_row`) on code's row. Pinned: 223's seven (owed list) and five (tasks table), word for
  word.
- [x] T009 FR-8 keel-web 178 (the coordinator's addition). `vectors_screens.ROW_NOTE_TESTID`, `LINE_CONTROL_TESTID`;
  `Corridor._list_rows`: `note` from `[data-testid=row-note]` on every row (locked too), `warn` the reword line alone,
  `line_at` (`data-line`) and `line_control` beside `line`; the walk never moves the line, so the Save sends the served
  `lineAfter`. `backtest.READ_JS`: a Choose option's `note` (its `-note-` describedby id; `choices` recorded where a
  suggestion or a note is drawn), `row_notes` (`{row, note}`), and a row's words never carry its note; the bundle keeps
  `row_notes`. `corpus_scenario.chain_fill` -- *Per* arrives empty (`chain_fill_177` the role word before); the strict
  `unit` check and `owed["unit"]` follow it. The equation text (*a percent* / the count word) is recorded, not asserted.
  `cost_line_parts` unchanged (178 says so). `tests/test_web_178_mirror_141.py` (4, chromium on pages drawn as 178
  draws them, the markup pinned to `ListQuestion.tsx` / `translate.ts`); `test_follow_ups_075` re-pinned.
- [x] T010 FR-1 the reader digest, last: `quality/readers/dimensions.md` = keel-cloud-docs **`d019f1ca`**'s
  `src/main/resources/keel/dimension-cards.md`, sha256 `9bbdd6a39cc18a7589588f19904d19a49df24bff751a050182d0a63565587b5c`
  = `RespondentReview.CARDS_SHA256`. `CARDS_SHA256_141` in `test_cloud_219_228_mirror_141` is the one constant the
  213 and 216 pins read for the current copy; `test_dimension_cards_131`'s Relative advantage good stem moves to the
  card's (*Think of the last night your baby would not settle. ...*).
- [ ] T011 FR-9 the gate (below).

## The gate

GATE_PLACEHOLDER

## Judgement calls (each with the spec line it bends)

1. **The spoken-corpus record was the six reds** (FR-9, *the nine back to green*): keel-cloud's
   `build/spoken-corpus.txt` (written 15:50 ET) is the first record after 198 the fixtures did not skip by age, so
   `test_instruction_spoken`, `test_corpus_r19`, `test_lock_frontier_110`, `test_money_cards_redrawn_118` and 198's
   mirror read 198's Buyer and payer four and 221's whole step for the first time. FR-4 turned five green with no record
   pin moved but Lullaby's (its Buyer four and Commitment whole); the sixth was 198's `BriefFacts` source line.
2. **Older locks keep 129's cut by spec number** (FR-4, *the pins move to the whole step*): `served_labels` carries the
   whole Yes and, where it differs, 129's cut (`first_yes_before221`, `second_yes_before221`), as 130 kept 118's.
3. **No scripted hard case** (FR-2, *may carry*): `HARD_CASES` is empty -- the golden seven's walks keep today's item
   and belief (219: *without them the build serves today's wording, no pin moves*), and a back-test entry's scripted
   `went_wrong` (*had a time when ...*) carries no hurt a hard case could share under H1. The functions are pinned on
   the cloud's five; H1-H4 (`HardCase.fault`) are not ported (no harness writer is held to them yet).
4. **No scripted loss clause** (FR-7, *where the scripted result carries one*): `LOSS_CLAUSES` empty -- no golden line
   falls to a neutral verb, and the cycle-14 five are COMMERCIAL studies, which run no part-1 job (222 call 2). S1-S4
   (`LossClause.fault`) are not ported; the frame and `said` are.
5. **Countly's golden step now costs data** (FR-4, `DATA_ACTS`): *install the app* is an install, so the scripted writer
   adds Keel's free smaller step to a golden entry for the first time, as the cloud's L34 asks; Countly's served soft yes
   becomes *Probably, after a look at how it works first* on a scripted run. The corpus records *Probably yes*
   (`build/spoken-corpus.txt` composes from the corpus, which has no smaller step).
6. **The problem card carries the clause only where the entry holds the founder's own** (FR-2): `problem_clause` writes
   the six only for the golden seven in a solution study, whose clauses pass E7-E9 by test and whose turned form is the
   gate's `event_base`; a back-test entry's *had a time when ...* is over the cap (E2) and would be dropped with E10.
7. **The API path's Save keeps the corpus's own row** (FR-8, 223's *the scripted Save sends the own row unchanged*):
   `vs.saved_list` still posts the recorded own row, so the stored belief stays the record's; where it reads as the job
   again 223's note is served and read by nobody. The browser walk saves the drawn (code's) row, and its strict Check
   and belief reads expect code's row. Changing the API path would move every Importance belief off the record.
8. **`chain_words_owed` bans neither form beside a percent** (FR-7, *no longer ban*): it owes the period; keel-web 178
   draws *· per {unit} ·* (`equation_per_drawn`), a web before it not (`equation_per_drawn_173`).
9. **L-kind is a fault in the instruction eval's score** (FR-8, *the Compatibility row `kind`*), as L35 is: the cloud
   breaches it (one repair turn, then a note). The passive permission face (`ItemFrames.permissionFace`) is not ported:
   no eval mirror predicts a Compatibility stem; walks read the served item.
10. **A row's note never enters the reader's rows** (keel-web 178, *the row scrape now sees the note*): the note is cut
    off the row's words and kept in `row_notes` / `choices[].note`; the reader is not told it (no reader instruction or
    rubric moved), so cycle 15's reader text is cycle 14's where no note is drawn.
11. **The digest's current constant lives in one place** (FR-1): the 213 and 216 pins accept their own digests and
    `CARDS_SHA256_141`, so the re-copy after 229 moves one line.

## Left open

- **229 moves Importance's own row and the card again** (`own_row` written by the writer, A1-A4, else 223's row):
  `writers_rules.own_row_from_clause` stays the fallback, but the scripted writer will owe an `own_row` field, the
  strict walk's own row and belief (`code_own_row`) will read the writer's act, and the cards' digest
  (`CARDS_SHA256_141`, `quality/readers/dimensions.md`) is re-copied by the coordinator.
- 219's H1-H4 and 222's S1-S4 are not ported (calls 3, 4); a scripted hard case or loss clause would need them.
- 225's open item: the follow-up after *No* on a passive permission item still says *You said you couldn't ...*
  (`vectors_script` `could_not`), as the cloud's `ItemFrames.couldNot` does; not moved.
- The instruction mirrors and the contract export have no byte copy here (the instruction eval reads keel-cloud's at
  run time, spec 137 call 11); nothing regenerated.
- The corpus records 216's/227's old words (Importance's registry own rows, the cost sentences); the loader reads them by
  rule (`spec227_cost`) until a corpus revision.
- Commits carry the brief's `Claude Fable 5.1` trailer; the builder was Claude Opus 5.5.
