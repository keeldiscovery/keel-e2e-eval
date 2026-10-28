# Tasks 076 -- The harness follows keel-cloud 145 and keel-web 127

Branch `076-founder-walk-round-two` off master `b56b8c8` + the spec (`0277ae7`), worktree `wt/eval-076` (`.git` a file).
The products, read only: keel-cloud-docs master `3b252640` (145: contract 43, corpus REVISION 16 with one row proposed for
17) and keel-web master `b50eb04` (127), reached through the sibling symlinks beside the worktree (`stack.toml`'s `../`
paths). No paid command was run and no key was present: every model, transcriber and renderer the fakes. **`make
instruction-screen` was NOT run** for the two instruction files 145 changed (`respondent-questions.md`: the
decision-maker's third-person chip; `themes.md`: `NOT_ABOUT_THIS`) -- it runs through a paid host and waits for the
founder's word. `REVISION` stays 16, `MARKS_VERSION` stays 20. Nothing merged, pushed or deployed.

| Commit | What |
|---|---|
| `0277ae7` | the spec |
| `adbea0c` | FR-2 Buyer and payer direction-aware; the DRY compares re-pinned to revision 16 with 145's proposed row named |
| `e789ccd` | FR-1, FR-3 - FR-6 (`INTERVIEWER_MARKS_VERSION` 12, `REPORT_MARKS_VERSION` 3), `tests/test_founder_walk_076.py` |
| `33eb99f` | the light gate's two findings (D-01, D-02), runs/DRIFT.md #98 and #99 |
| this commit | this file |

## Unit

| | passed | failed | skipped |
|---|---|---|---|
| master (the hand-off's figure, products before 145 / 127) | 3,504 | 0 | 53 |
| `0277ae7` against keel-cloud-docs `3b252640` + keel-web `b50eb04` | 3,501 | **3** | 53 |
| `33eb99f` and this commit | 3,528 | 0 | 55 |

The three reds at `0277ae7` were this spec's subject: the registry's Buyer and payer `supports` now two answers
(`test_follow_up_ladder`), the DRY compare 107 of 108 (02-compliancelog's proposed row), contract 43 (075's pin of 42).
The two new skips are the brief-facts DRY compare (`test_instruction_brief_facts.py`, 2 tests): keel-cloud-docs'
`build/brief-facts/` dates from 2026-10-25, before 145, and the main checkout is read only here, so it was not rebuilt;
the tests now skip naming why, and on a fresh export pin the one card 145 moves (J-4).

## FR-1 -- Ability to pay's bars -- `e789ccd`

- [x] T001 `Answers.vector_page` reads a said row's bars (`li.dimbar`, muted or not) and its words; `budget_bars_faults`:
  on a row whose said line is the counts sentence (`COUNTS_SENTENCE`, 145 FR-1's line alone), `choice.founderCodes` and
  each option's `founderNamed` are `BUDGET_SUPPORTS` among the options, exactly those bars drawn on, no *which you didn't
  name*. `_hold_the_ability_line` holds it and refuses the old *Keel reads ... where the money would come from. Counts
  ...* pair. Unit-tested against `CommercialChain`, `StandingsAssembler.said` and `DimensionStagePage.tsx`.
- [x] T002 No mark pinned the old all-muted bars or the old two-sentence line, so no mark moved.

## FR-2 -- Buyer and payer is direction-aware -- `adbea0c`

- [x] T003 `interviewer_fake.BUYER_SUPPORTS` = `had_to_agree`, `decided_alone` (the registry's; deciding alone owes no
  follow-up on a named role). `chain.the_role` mirrors `BeliefSentence.theRole` (CEO -> *the CEO*, *The HR director* ->
  *the HR director*, *Priya* bare); `spoken.buyer_answers` and `brief_facts`' card line (*the HR director had to agree, or
  they decided alone*) use it.
- [x] T004 The money page holds Buyer and payer's said line to the served `founderSaid` and to `buyer_said` (*You said
  nobody else has to agree.* on every journey entry -- all six test *Nobody else*, so no status, count or drift moved).
- [x] T005 `test_keel_clouds_engine_agrees_with_corpus_r10_on_all_108_checks` reads 107 of 108 with the one mismatch
  named: 02-compliancelog's Buyer and payer, PEOPLE_DISAGREE/both in revision 16, HOLDING_UP/none from the engine.

## FR-3 -- Send more is the name alone -- `e789ccd`

- [x] T006 `Interviews.send_someone` takes no `about`, counts any second box drawn (`#send-about` or its label) and
  returns what keel-web sent; `name_alone_faults` (no box, `people: [{personName}]`) is asserted on every corpus link
  (`leg_invite`) and every AI-leg link (`_send_link`).

## FR-4 -- the screener on the decision-maker's link -- `e789ccd`

- [x] T007 Which entry: of the corpus, only **05-paidly** is SOMEONE_ELSE with a qualifier in WHICH PEOPLE (*freelance
  translators in the US who work mostly for agencies*: `who ...` drawn as *work mostly for agencies*, the model's own
  condition kept; *in the US* is the market). 06-repeatline and 07-mulchrun carry none, 01-04 are SAME_PERSON. So the walk
  is **S-006's** (and S-014's healthy copy of paidly walks the same code).
- [x] T008 `vs.decider_chip` / `decider_condition` mirror `RespondentQuestionsRules.deciderChip` (third person, the
  organisation's condition as is, the 20-word cap). `Interview._condition` walks `condition-screen` before the idea (the
  served question as `h1`, Yes / No, Continue off until picked, no kicker, no Back); `condition_screen_faults` holds it on
  every decision-maker's link in `_hold_the_screens`; S-006 asserts all eight served
  *Do the freelance translators working for agencies you decide for work mostly for agencies?* and walked condition -> idea.
- [x] T009 `leg_outside_decider` (S-006, after the contacts leg): a ninth decision-maker, Odile Marchetti, answers No:
  `{outsideSegment: true, answers: []}` 201, the exit (*That's it.*), no idea, no pilot box, `standings.outsideSegment`
  +1, no commercial `n` moved. `PersonInputs.response` sends `outsideSegment` alone on either link.
- [x] T010 The X9 / X12 context notes (145 FR-4a): no mark reads them (the scripted condition names the founder's
  qualifier, so none is written on the journeys), so none moved.

## FR-5 -- a story chip ends the interview -- `e789ccd`

- [x] T011 `PersonInputs.response`: a gate Yes with a chip is `{recency: true, anchorChip, answers: []}`; `ends_on_chip`.
  The text walk stops at the gate (no items, no follow-up route), `walks_rungs` false, `follow_up_lines` skips them.
  S-006's Xavier Dubois (*I'd rather not say*) walks it; `hold_the_chip_people` holds his part-1 rows *Would rather not
  say* and no solution or money row listing him.
- [x] T012 `_chip_ends_it` (S-005 and S-006): a second AI link, segment chip and gate held "yes", the story's chip tapped
  -> one chip-only response with `format: AI_INTERVIEWER`, no follow-up call, no pilot write, the done screen, *Microphone
  off*, the rows *Couldn't recall one particular {occasion}* (delivery / invoice) and *said yes* on Prevalence.
- [x] T013 `INTERVIEWER_MARKS_VERSION` 11 -> 12: IM22 gains the chip half (`chip_ended_it`), IM23 reads a chip person's
  text walk as asked nothing. Eight seeded faults added.

## FR-6 -- junk out of Insights -- `e789ccd`, `33eb99f`

- [x] T014 `interviewer_fake.themes_with_junk` (the script's rule; `FakeThemes` and its export untouched): an answer in
  `NOT_ABOUT_THIS_TEXTS` in one last NOT_ABOUT_THIS group. `vs.JUNK_FOLLOW_UPS`: S-005's **Priya Natarajan** types
  *Meow, you are a fool.* on her one owed rung (Current solution) -- the whole study only; she answers first and the cloud
  starts no THEMES job under two answers, so every job there carries her words and the scripted theme resolves.
- [x] T015 `Answers.insights` reads `insights-not-about-this`; `report_marks.not_about_this_faults` (in `report_insights`):
  no NOT_ABOUT_THIS theme, its words in no quote, `notAboutThis` the script's junk on the stack, the line drawn exactly
  when n > 0 (a box without the key read as 0). `hold_not_about_this` (S-005): notAboutThis 1, *1 answer was not about
  this.*, the words still under Priya on the stage row and on the Pilot list. `REPORT_MARKS_VERSION` 2 -> 3.

## FR-7 -- nothing else moves

- [x] T016 `MARKS_VERSION` 20, corpus `REVISION` 16, `GUIDE_MARKS_VERSION` 3, `CONTACTS_MARKS_VERSION` 2,
  `FEEDBACK_MARKS_VERSION` 1, `SCOPE_MARKS_VERSION` 2 unchanged. The noise check, the back-tests, the judge and the paid
  commands untouched.

## The marks: every pin moved

| Mark | Version | Moved | Why |
|---|---|---|---|
| IM22 | 12 | owed also: the story's chip on a second AI link ends it -- one chip-only response, no follow-up, no pilot, done, mic off, the rows' words | keel-cloud 145 FR-5, keel-web 127 FR-3 |
| IM23 | 12 | a text walk whose person taps the chip (Xavier Dubois) is read as asked nothing: no route call, no screen, no `followUps` | keel-web 127 FR-3 |
| report_insights | report 3 | `notAboutThis`: the junk off the box and counted, the muted line exactly when n > 0; a lone answer before any THEMES job read as not yet judged | keel-cloud 145 FR-6, keel-web 127 FR-4; D-01 |
| (DRY) compare_correctness's unit pin | -- | 108 -> 107 of 108 against revision 16, the one row named | keel-cloud 145 FR-2's proposed revision 17 |
| (DRY) brief_facts' unit pin | -- | 101 -> 100 of 101 on a post-145 export (02's buyer card named); skipped on an older one | keel-cloud 145 FR-2 |

Read as before: every other IM, guide, contacts, feedback and scope mark. The Buyer and payer said line, the budget bars,
the name-alone step and the screener are journey assertions (as 075 J-2's dry run), not marks.

## The light gate (local stack, keel-cloud-docs `3b252640` + keel-web `b50eb04`, the scripted executor)

`docker ps` before `make up`: only `focused_robinson` (never touched). `make down` / `make up` between runs (075 D-02).

| Run | On | Result |
|---|---|---|
| `runs/20261028T044641Z-s005-countly` | `e789ccd` | failed after four answers: Priya's lone answer quoted ON_THEIR_OWN, notAboutThis 0 (D-01) |
| `runs/20261028T044949Z-s005-countly` | `e789ccd` + D-01's read | **passed** (360 s): IM 23 of 23 (v12), report 5 of 5 (v3), guide 17 of 17, contacts 1 of 1, feedback 4 of 4 |
| `runs/20261028T045619Z-s006-paidly` | `e789ccd` + D-01 | failed in the AI leg's dry run: the story read twice on the gate's id (D-02) |
| `runs/20261028T050224Z-s006-paidly` | `33eb99f`'s tree | **passed** (400 s): IM 29 of 29 (v12, IM12 unmeasured as on master), report 5 of 5, guide 5 of 5, contacts 13 of 13, feedback 5 of 5 |

`versions.json` of the S-006 run of record: keel-cloud
`3b252640` (clean), keel-web `b50eb04` (dirty by its untracked `.idea/` alone), keel-runtime `3988131`, keel-e2e-eval
`e789ccd` dirty by `33eb99f`'s change. `make down` after it; no container left but `focused_robinson`.

## Discovered

- D-01 A line with one follow-up answer starts no THEMES job (keel-cloud 119, `ThemesOnReturn`), so after S-005's
  fourth answer Priya's *Meow, you are a fool.* stood alone on Current solution, quoted ON_THEIR_OWN with
  `notAboutThis` 0. The product's: **runs/DRIFT.md #98** (no spec asked for it). The mark holds the rule from the
  second answer on.
- D-02 keel-web's *Test your mic* transcribes its hello on the link's first item -- the gate's id
  (`AiInterviewFlow.firstItemId`) -- so 075's `dry_run_written_down` saw two takes on the gate. The harness's: 075 FR-5's
  S-006 half (the dry run's story) had never run on a stack (075's light gate was S-005 alone). Fixed in `33eb99f`.
- D-03 05-paidly's decision-makers are asked *Do the freelance translators working for agencies you decide for work
  mostly for agencies?* -- the qualifier twice (`actor_plural` already carries it). **runs/DRIFT.md #99**.

## What did not hold

- *FR-1 walked on the stack*: neither S-005 (cost-covers-price reading) nor S-006 reads Ability to pay off the budget
  question, so the bars and the counts sentence alone are unit-tested only; the hold runs wherever a journey does.
- *Acceptance: the remaining four journeys* (S-007, S-014, S-015, S-016) and the six remote ones are the coordinator's
  thorough pass after the deploy; not run here. S-014 walks paidly's screener on all its decision-makers by the same code.
- *The brief-facts DRY compare* is skipped (stale export; the main checkout is read only), so 145's brief line is held
  by unit tests against `BriefFacts.java`'s source, not against an export.
- *Instruction screening*: not run (see the head); `respondent-questions.md`'s third-person chip and `themes.md`'s
  `NOT_ABOUT_THIS` are unscreened, as keel-cloud 145's tasks.md also says.

## Judgement calls

- J-1 **The outside decision-maker is a ninth person, walked after the contacts leg.** The corpus's eight answer inside;
  an extra link before the golden reads would move the people counts, and before the contacts leg its kind counts. It
  moves `outsideSegment` alone, which the step holds.
- J-2 **The AI chip walk is IM22's second half, not a new mark**: the spec names the IM-series that walk a chip; no IM had,
  so the story's mark (IM22) takes it and the version moves.
- J-3 **`REPORT_MARKS_VERSION` 3**: `report_insights` reads a new field (075 J-3's rule: a mark that reads its record
  differently moves the version).
- J-4 **Revision 16 is read as written.** The DRY compares name 145's proposed row as the one disagreement rather than
  read it as revision 17 (as keel-cloud's `GoldenCorpusTest` does), since the spec keeps REVISION at 16 until the founder
  commissions 17.
- J-5 **The junk is placed by the script, not by `FakeThemes`**: the cloud's test fake has no NOT_ABOUT_THIS group and
  its export holds this repository's copy word for word, so `themes_with_junk` wraps it.
- J-6 **FR-3 moved `send_someone` only.** The older People-page object (`People.fill_who`, used by preludes and S-002 /
  S-003 / S-004 / S-010) is not 127's popup (*Send more > Someone I know*) and none of the light gate's journeys walk
  it; it was left as it is.
