# Tasks 119 -- The harness walks cycle 5's studies to the end, and the reader hears what the voice says

Branch `119-the-harness-walks-cycle-5-to-the-end` (worktree `wt/keel-e2e-eval-119`, `.git` a file, its own `make venv`),
off master `082dc9e` (the spec and its FR-8 amendment). Built by Claude on 2026-11-01. Read only: keel-cloud-docs master
`bc172359` (contract 56, corpus revision 22: 187's and 188's tasks.md, *owed to keel-e2e-eval 119*; `CommercialChain.side`
/ `POINTS_BACK` / `CANT_SAY`, `SpokenForm.of` / `durationFirstStep` / `sideQuestion` / `percentSaid`,
`VectorCorridorService.ANSWER_MAX_WORDS`, `TheQuestionScreensSayItOnceTest`, the guidelines' §18, the corpus and its
`corpus-r21/`, `corpus-r22/`, `backtest-r21/` records; the build records of record, marker `build/.records-bc172359`),
keel-web master `f02595c` (158's and 159's tasks.md; `ListQuestion.tsx`'s `DurationInput`, `founderLists.ts`'s
`joinAnswer` / `splitAnswer`, `translate.ts`'s `kindPeoplePlural` / `sendFormatTitle`), and cycle 5's record and bundles
in the main checkout (`quality/cycles/20261101-e65afec.md`; `runs/20261101T051335Z-backtest-10-palus`,
`20261101T055117Z-backtest-17-expanse`, `20261101T061252Z-backtest-21-codyco`, `20261101T050851Z-backtest-10-palus`,
`20261101T053028Z-backtest-13-aircaps`; the reader's prompt `read-10-palus-COMMERCIAL/calls/030-...price.prompt.txt`).
**No stack, no model, no walk, no paid call, no key read.** Nothing merged into master; the branch pushed after every
commit, never force-pushed.

| Commit | What |
|---|---|
| `b7f6d9d` | FR-6: corpus revision 22 -- the reader, `current_solution.today`, the Answer's first box, the fixtures at 22, the marks header's r22 paragraph, the revision pins re-pinned |
| `578d827` | FR-1 / FR-2 / FR-3 / FR-8: the walk -- the served idea line, Ability to pay's written question, Choose's named stop, the idea step captured once, a refused job as evidence, DRIFT #97's count; the served Check cap and 159's heading |
| `a2ce9e2` | FR-4 / FR-5 / FR-3 / FR-8: the bundle records the served spoken form, the reader says it and pastes §18, the Choose boxes handed to the founder-reader, `failure_screens`, the guard (the escape where it points back, the percent step, the duration bands as Price's); 118's tests re-pinned |
| `e96767e` | FR-7: `tests/test_cycle_5_to_the_end_119.py` (25) and `tests/fixtures/cycle5/` (four fixtures cut from the recorded bundles) |
| the docs commit | this file and `AGENTS.md`'s spec-119 paragraph |

## Unit (the gate)

| | passed | failed | errors | skipped |
|---|---|---|---|---|
| master `082dc9e` against keel-cloud-docs `bc172359` (records fresh) and keel-web `f02595c`, run in the worktree before any edit (03:50:12-03:53:54 ET) | 4,404 | 186 | 59 | 244 |
| **branch at `e96767e` (the last code; the docs commit adds none), the same siblings** (`set -o pipefail; make unit 2>&1 \| tail -3`, 04:23:26-04:27:22 ET, exit 0) | **4,866** | **0** | **0** | **53** |

Master's 186 + 59 are the corpus at revision 22 (`revision is 22; this eval reads revision 21 only`) and the 191 extra
skips the registry tests it refused. The last recorded master count (118's tasks.md + the two commits after it, 4,840 /
0 / 0 / 53) was against keel-cloud-docs `f3f0d99e` and keel-web `3c0db0c`. The branch's 53 skips are master's 53 (S-001's
revision-2 readers). +26 tests: the 25 of `test_cycle_5_to_the_end_119.py` and revision 21's refusal in
`test_instruction_corpus_r11.py`'s table.

## Cycle 5's nine stops, and what handles each now

| Study | Stop | Whose | What handles it |
|---|---|---|---|
| 08-fresco PROBLEM, SOLUTION, COMMERCIAL | step 5's L1 title (*Who should ask ...?*) | the harness's | fixed mid-cycle on master: `5bde940` + `a1b92a3` (`people_plural` ported from `translate.ts`, `l1_title_owed` reads the served actor). 119 adds the send dialog's heading in the same plural (keel-web 159, `ivs.kind_people_plural`) |
| 10-palus SOLUTION | DRIFT #97's count, *wire 6, script 4* | keel-cloud's refusals (L1, then L2 at 10 words -- 187 FR-1 widens Compatibility to 16), and the harness's count | `scope_journey.drift_97` holds the APPLIED jobs to the script and requires every refused in-scope job to be one the walk retried (spec 062's finding, now with its served `reason`); `changed["drift_97"]["refused_and_retried"]`. FR-8: the two `failed-solution-calibration` shots were `_retried`'s camera on the idea step while the job ran -- now `Camera.evidence` (`failure_screens`, never a founder screen), and a recorded bundle's `failed-*` screen is never scored (`readers.WAITING_STATE`) |
| 13-aircaps SOLUTION | the same count, *wire 5, script 4* | the same | the same |
| 10-palus COMMERCIAL | Sofia Marchetti: *want Imagine Palus.* beside the served *Imagine Palus, a managed reserve portfolio.* | the harness's (money alone never read `whatItIs`) | FR-1: `cs.idea_line_faults` -- the served line names the idea (*Imagine {name}* then `.` or `,`), equals the founder's `IdeaView.line` where read, and every drawn card opens with it; `scope_journey.leg_idea_card` keeps `whatItIs` and `line` |
| 13-aircaps COMMERCIAL | Harriet Coleman's reveal, the same | the same | the same (the reveal on the person's own link) |
| 17-expanse COMMERCIAL | Gregory Lindqvist: the drawn *You said about $10,000 to $25,000 a month. ...* held to the item's spoken `question` | the harness's | FR-2: `cs.pointed_back_question` -- the walk's `pointed_back` (now in its return), else the `askedAfter` entry of the sent Price answer; `_hold_the_screens` wants it as the drawn question |
| 21-codyco COMMERCIAL | Choose: Continue never lit (30 s) | test data (r21 named no time) | FR-6: revision 22's `duration` on every B2B entry, typed by `list_choose` (`vs.founder_duration`); FR-3: a drawn box with no time stops by name; the Choose shot carries the box for the reader |

## FR-1 -- the idea's line -- `578d827`

- [x] T001 `cs.idea_line_faults(name, served, drawn_screens, want=)` -- the check holds the served line, never one composed
  here: it names the idea, it is the founder's `IdeaView.line` where the walk read one, every drawn reveal / idea card
  opens with it, the Relative advantage item's idea card is it. *Imagine {name}.* alone holds only where the served line
  is that (keel-cloud 188: no plain words but the name). On a scripted journey the line also equals `vs.idea_card(name,
  whatItIs)`.
- [x] T002 `Journey.idea_line`; set at S2 (`corpus_scenario`) and on money alone's idea card (`scope_journey.leg_idea_card`,
  which kept neither `whatItIs` nor `line` -- the stop).

## FR-2 -- Ability to pay's written question -- `578d827`

- [x] T003 `Interview.walk` returns `pointed_back`; `cs.pointed_back_question(item, walked)`; `_hold_the_screens` holds
  an `askedAfter` item's drawn question to the written one. The AI link's held as before (`interviewer_leg`).

## FR-3 -- the Choose time -- `578d827`, `a2ce9e2`

- [x] T004 `list_choose` types the entry's time (r22: every B2B entry); a drawn `duration-input` with no time is a named
  stop, never Continue's 30-second wait.
- [x] T005 `bt.READ_JS` reads a Choose screen's `title` (`.listcheck__title`), `intro`, `time_box` (question, count,
  unit, units, hint) and `keel_test` (belief, bar, note); `founder_screens` keeps them; `founder_answer` adds the time
  typed and the time the save sent; `readers._choose_boxes` hands the founder-reader *Title over the list*, *Under the
  list, a time box: ... -- a number box and a unit menu (...)*, its hint, and *the Keel will test box: ... (the bar:
  ...)*.

## FR-4 -- the reader hears the voice, on either link -- `a2ce9e2`

- [x] T006 **The spoken recording's shape in the bundle.** `backtest.json` → `respondents[<link>].served.parts[].items[]`
  gains `spoken` -- the served block as the interview wire served it to the page (`bt.SPOKEN_FIELDS`: `anchor`, `stem`,
  `countLine`, `optionsLine`, `escapeLine`, `transform`, `under`, `over`, the served ones only) -- on every item whichever
  link the person walked (the wire serves it on the text link too: the guard has always read it there); the plan's
  `plan.spoken`; `askedAfter: {itemId, answers: [{question}]}` (the written questions); and `served.condition` (the
  screener, with its spoken form).
- [x] T007 **How the reader's `{{screen}}` carries it.** `readers.said_line` finds the served block, so the line is
  *Said aloud by the AI interviewer (the served spoken form): {anchor} {stem} {count line} {options line} {escape
  line} Then, after a side is picked, the second step -- on the lower side: {under} On the upper side: {over}* (and the
  plan's after it). *The bundle records no spoken form for it* is written only where the wire served none (a reveal, a
  follow-up). The guidelines pasted for R6 gain §18 (`GUIDELINE_AMENDMENTS` 16, 17, 18; keel-cloud 187's duration bands'
  second step); `respondent.md` says so. No criterion moved; `RUBRIC_VERSION` stays 3.

## FR-5 -- the spoken guard (`instructions/spoken.py`) -- `a2ce9e2`

- [x] T008 **S6**: where Ability to pay points back (`points_back`: a B2B entry whose price is the chain's and not free,
  `chain.asks_back`), the escape named and said is Price's row's escape in the registry the item was served from (the
  bundle's export: `cant_say`, *I can't say*) -- `pointed_back_escape`; no pinned label.
- [x] T009 **S8 on a percent ladder**: step one is said in words (keel-cloud's `percentSaid`, not ported), so it is held
  to §3's shape -- four pieces, *Under ...* first, *... or more* / *Over ...* third, the last option said whole after
  *; or* (`_percent_first_step_holds`). A money ladder is held word for word as before.
- [x] T010 **The duration bands read as Price's**: `first_step(key, options)` (`duration_first_step`, a port of
  `durationFirstStep`), `transform_of` (`two_steps` on the six, `none` on the fixed three), S3 counts the first step's
  four, S7 its count line, S8 its four, S9 `two_steps`, S11 the two lines (`side_question`, a port of `sideQuestion`
  without the percent words; a lock before 187 serves none and is not asked them).
- [x] T011 On Palus's three items as cycle 5 served them (the fixture, the recorded faults kept beside them) the guard
  reads clean; 118's record-of-record test passes on `bc172359`'s `spoken-corpus.txt` (the golden seven: no time, no
  pointing back).

## FR-6 -- corpus revision 22 -- `b7f6d9d`

- [x] T012 **The revision 22 reading.** `corpus.REVISION` 22; `_REVISION_OF[21]` names it (*before keel-cloud 187: 13 B2B
  back-test entries with no founder's time ... and no `current_solution.today`*). Every B2B back-test entry (16) names a
  time (`Entry.duration()`): its row is code's six (`duration_bands`, `cant_tell`), its belief the dated form, its picks
  the band codes -- read by the rules 118 ported, nothing new to check. `current_solution: {today}` is read into
  `Entry.current_solution` / `Entry.today()` and refused by name unless it is `{today}` alone, one sentence of at most 25
  words. No standing moved. The golden seven moved by their revision line alone (the marks header's r22 paragraph
  records their digests, equal to `corpus-r22/`).
- [x] T013 `vs.current_solution_boxes`: the first box is `today` where the entry records it; the rungs fill the second
  within what is left of the Answer's 25 words (see *not foreseen* 2). An entry with none keeps 184's phrase.
- [x] T014 The eval's fixtures `09-fixture`, `10-fixture-b2b`, `99-broken` at 22 (their revision line alone).
- [x] T015 Contract 56: no field the harness reads moved (`Spoken.under` / `over` on the duration bands are read by the
  generic two-step code since 118: `vs.two_steps_of`, `vs.step_one`, `Player.wait_ask`).

## FR-8 -- the waiting state -- `578d827`, `a2ce9e2`

- [x] T016 `cs._retried` no longer calls `camera.founder`: `Camera.evidence(<what>-<reason>, said)` keeps the page in
  `failure_shots` (`failed-NN-...png`, the bundle's `failure_screens`), the finding carries `reason` (the served status,
  e.g. `RESULT_INVALID`) and the step's name the served reason.
- [x] T017 `Corridor.idea_check` waits for the served how and belief (`IDEA_LINES_DRAWN`) before it captures the idea
  step, once.
- [x] T018 `readers.founder_screens` leaves out a recorded `failed-*` screen; the rest keep their recorded numbers (on
  the Palus fixture: 9, 12, 13 of 20).

## FR-7 -- tests -- `e96767e`

- [x] T019 `tests/test_cycle_5_to_the_end_119.py` (25): the four stops replayed on `tests/fixtures/cycle5/` (cut from
  the recorded bundles: Palus and AirCaps COMMERCIAL through `_hold_the_idea_name`, Expanse's written question, Palus
  SOLUTION's screens and its six jobs through `drift_97`); `idea_line_faults`' faults; the Choose box read off a page and
  handed to the reader; D22 (the r21 records beside canon: 13 times, 13 rows and beliefs, 80 picks by 182's one rule,
  Transload's chip, 14 today's ways, the golden seven's revision line, nothing else); r21 refused by name;
  `current_solution.today` held; the Answer within 25; the spoken form recorded and said on the text link; Palus's three
  red guard rows clean; the pointed-back escape; the duration bands read as Price's; the percent step's shape; the AI
  walk's two steps on the duration bands; 159's heading; the served Check cap; §18 pasted.
- [x] T020 Re-pinned with why: `test_instruction_corpus_r11` (the refusal words at 22; revision 21 added),
  `test_corpus_r11_shape`, `test_corpus_r19`, `test_follow_ups_075`, `test_founder_walk_076`, `test_recorded_path_074`,
  `test_study_scopes` (revision 22), `test_seven_templates_115` (Codyco's dated belief and `cant_tell`; every B2B
  back-test entry timed; Transload's chip recorded `cant_tell`), `test_money_cards_redrawn_118` (D21 mirror against
  mirror; canon at 22, 19-21 refused; Transload timed, the untimed path on golden Paidly; the two boxes on 22-andy-ai,
  which records no today; §16 / §17 then §18). `tests/fixtures/sample/s006-reads.json` not edited.

## Owed by keel-web 158 / 159 and keel-cloud 187 / 188 -- `578d827`

- [x] T021 The Check screen's cap is the served `saves.maxWords` (`served_word_cap`; Compatibility's 16): an over-cap
  row is cut to it (it was cut to a fixed nine), and the intro's *under {n} words each* is read (`check_intro_cap`) --
  another number than the served cap is a finding (`_hold_check_intro`), never a stop. The counter (*n / 16*) is the
  page's and is not held.
- [x] T022 `ivs.send_format_title(label, label_short)` -- 159's `sendFormatTitle`: the kind's people in the plural, the
  long label first (`kind_people_plural`); *someone* / *somebody* read *people* in `_PLURAL_IRREGULAR`. The dialog's
  heading is read and recorded as before (`title`); no leg held it to a word.
- [x] T023 SHARE greyed on 08, 13 and 21 (158 T007): the corpus prices there are `AMOUNT_PERIOD` (08) and `UPFRONT_THEN`
  (13, 21), so the walk never presses a percent pill; nothing to build.
- [x] T024 188 FR-2's templates: no mirror of *The problem already costs the payer* / *The payer would think it worth*
  exists here but `corpus.py`'s check of a recorded pre-chain cost sentence, which 188 says stays while the corpus
  records the old words. The founder screens record the served belief line as drawn (`belief line on screen`). 188 FR-1:
  the walk reads `whatItIs` as drawn and accepts it -- the noun phrase or an empty box; the strangers' check holds the
  served line (FR-1).

## What the spec did not foresee

1. **The export does not say `cant_say` for Ability to pay.** FR-5 says the escape of record is the registry export's
   `cant_say`; the export's Ability to pay row still names `cant_recall_one` (the registry of record, unchanged by 181),
   and keel-cloud serves `cant_say` through `CommercialChain.side` -- *the consumer's and Price's own*. Decision: where
   the item points back, the guard reads **Price's row's escape in the same export** -- still read, never pinned.
2. **Today's way fills the Answer.** keel-cloud holds the two boxes joined to 25 words (`ANSWER_MAX_WORDS`, 422
   `VALUE_OUT_OF_SHAPE`) while keel-web lets each box take 25. The 14 `today` sentences are 22 to 25 words, so no rung
   fits beside any of them: the second box is left empty and the founder types the rungs on the Check screen (spec 067
   FR-2's `_rungs_to_type`, unchanged). Typing the rungs past 25 would be refused by the server. Named for both repos.
3. **The two SOLUTION stops were the harness's count as well as the model's refusals.** The walk retried the refused
   jobs (spec 062) and went on; DRIFT #97's step then counted the refused rows as chained jobs. Decision: the applied
   jobs are held to the script, a refused in-scope job must be one the walk retried, and the stop stays where a refusal
   was never retried.
4. **FR-8's two screens came from `_retried`, not from the idea capture.** The camera shot the page when the SOLUTION
   job was refused -- the idea step still drawing. Decision: those shots are evidence apart (`failure_screens`), and the
   idea step is captured once its how and belief are drawn.
5. **The Choose screen's title and intro were never read** (`READ_JS` reads `h1`), so the founder-reader saw no
   question there either. Read with the time box and the Keel-will-test box.
6. **Percent words are not ported.** keel-cloud says a percent ladder in words (`percentSaid`); the guard holds a percent
   ladder's first step and second step to their shape only (S8, S11) rather than port the fraction table.
7. **Contract 56 moved nothing the harness reads**: the duration bands' second step rides the generic two-step code 118
   wrote for Price (`two_steps_of`, `step_one`, `wait_ask`), so the AI walk answers them in two steps with no new code;
   a test pins it.
8. **`MARKS_VERSION` 24 stands**: the guard now reads the duration bands and the pointed-back escape as keel-cloud serves
   them -- a shape the record of record already keeps (no fault at `bc172359`; the golden seven name no time and do not
   point back) -- as spec 089 FR-3, 115 and 118 read theirs. AGENTS.md's rule (a moved ruler, not a moved record, earns a
   bump) is kept. `RUBRIC_VERSION` 3 stands (no criterion moved; §18 is pasted as §16 / §17 were).

## Owed elsewhere

- **The coordinator**: the acceptance -- the next cycle's fifteen walks (paid, on the founder's word); the matrix's s012
  red on the Insights view (a Commitment box's served group not drawn), whether it is the harness's (this spec's
  successor) or the product's, from that cycle's bundles; `tests/fixtures/sample/s006-reads.json` re-recorded
  (`make sample`), still owed from 118.
- **keel-cloud / keel-web**: the Answer's cap -- the page takes 25 words in each of Current solution's two boxes and the
  server refuses a joined Answer past 25 (*not foreseen* 2); `WHY=instruction:asked.md` and
  `WHY=instruction:solution-mechanism.md` (187 / 188's screens, the coordinator's).
- **keel-cloud**: the registry's Ability to pay row still names `cant_recall_one` where every chain study serves `cant_say`
  (*not foreseen* 1; 118 named its `no_follow_up` words too).
