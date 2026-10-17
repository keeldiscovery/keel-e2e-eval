# Tasks 052

- [x] T001 FR-1 the reading marks retire, deleted: `instructions/brief.py`, `tests/test_instruction_brief.py` (32),
  `tests/test_instruction_brief_reading.py` (5), `tests/fixtures/brief/`; the `BRIEF` case kind, screen, context
  (`context.build_brief`, `brief_facts.beliefs_for` / `stories_for` / `targets_for`), redraw (`run.refused_twice`,
  `runner.UNATTENDED_SCREENS`), validator marker (`validate._CALL_MARKERS`), report rows and register paragraphs,
  `rescore.py`'s BRIEF handling (and a v19 bundle refused by name, `OLDEST` 20); `brief` job class dormant
  (`models.py`: THEMES routes through it, no case measures it); `vectors_script`'s BRIEF entry and `brief_result`;
  `corpus_scenario.leg_brief` / `_brief_pages` / `_brief_on_return`; `MARKS_VERSION` 19 -> 20 with its paragraph and
  calls 116-120, `marks.toml`'s v20 header (`brief_answers` struck through in a comment), README / AGENTS paragraphs
- [x] T002 FR-1 `brief_facts` stays and gains: `priceMedian` (`price_table`, `price_median`, `price_median_for`; one more
  compare check an entry), keel-cloud 103's two card lines (Compatibility `said {condition}`, no `said yes:`;
  Purchase friction counting `yes_quick` + `not_needed`, *did not need {step}, or it was quick*); `facts_for` without
  `targets` / `keys`, with `commercial.priceMedian`
- [x] T003 FR-2 the themes fake (`harness/interviewer_fake.themes`, `first_noun`, `served_quotes`, `THEMES_STOP_WORDS`)
  held to keel-cloud 104's `THEMES/cases.json` (= the exported `themes-cases.json`); the eight rung headings and five
  no-question reasons beside it, held to the registry export; the Insights view's words (as 077 defines)
- [x] T004 FR-3..FR-6 the five report marks (`evals/report_marks.py`, `REPORT_MARKS_VERSION` 1) and the Overview drawing
  (`instructions/overview.py`, `report_overview` also a zero-spend row of `marks.py`), each with seeded faults
- [x] T005 page objects for keel-web 077 (`harness/vectors_screens.Answers`): `board` (the Overview view) rewritten,
  `insights`, `pilot`, `brief(printed=True)` the binding; `breakdown` and the on-screen brief deleted; `vector_page`
  reads the per-person *One last thing* line (`follow_up_rows`)
- [x] T006 FR-7 / FR-8 the journeys re-pointed: `leg_report` in `leg_brief`'s place (the facts on the wire, the price
  median, then the three views and the binding scored), `_themes_on_return` in `_brief_on_return`'s, the Overview
  check in `_board`, the too-few state (`_too_few`, widening `_board_tiles`), the stage page's follow-up lines; S-012
  calls `leg_report`; 044's interviewer leg waits for THEMES, not BRIEF, on the founder's return (IM13 reads
  `themes:on-return`)
- [x] T007 FR-7 S-014 `evals/test_s014_green.py` on the built healthy project (`preludes.healthy_entry`); the scenario
  set is fourteen
- [x] T008 DRIFT #92 and #93 reserved (`runs/DRIFT.md`); `make unit`; this file
- [ ] T009 **owed to the journey pass**: acceptance 2 (`make eval K="s005 or s006 or s007 or s014"` on a fresh stack
  against keel-cloud 104 + keel-web 077, after 051 + 076) -- the page objects held to what 077 built, the four journey
  marks measured and met on S-006 and S-014, the too-few state on S-005
- [ ] T010 **owed to the journey pass**: acceptance 3 (remote journeys on staging with 104 + 077; DRIFT #92 / #93 filled
  or released)

## Measured (2026-10-17, no stack)

- **051 has NOT landed first** (contrary to the spec's acceptance 1), so the count is measured against master
  `3ac82f1`'s own number on the same siblings. `make unit` on `3ac82f1` against keel-cloud-docs `9a033fe` (104):
  **2,444 collected = 2,385 passed / 53 skipped / 2 failed / 4 errors** -- the 2,391 / 53 of spec 050 plus four red
  that 103 / 104 caused: `test_the_real_validator_takes_the_asked_screen` (BRIEF gone from the validator),
  `test_the_kinds_are_keel_clouds_own` (103's `ClipKind.FOLLOW_UP`), and `test_instruction_brief_reading.py`'s four
  (no `brief.md`). All six are fixed or deleted here.
- `make unit` on this branch: **2,490 collected = 2,433 passed / 56 skipped / 1 failed**. The one red is not this spec's:
  keel-web's master moved to 076 (`c9ce17c`) during the run, and `test_interviewer_screens.py::
  test_the_seam_ends_an_utterance_on_a_final_and_grants_the_mic` reads 076's `fakeSpeech.ts`, whose mic `acquire` is no
  longer `async () => true` (076 FR-T6, a refusable mic) -- spec 051's seam to re-read (D-02); it was green in this
  session's first run, before keel-web moved.
- The delta, +46 collected: 37 deleted (`test_instruction_brief.py` 32, `test_instruction_brief_reading.py` 5), and
  `tests/test_report_marks.py` 74 new (41 seeded faults across the four page marks, 5 on the DRY overview, the themes
  fake against the cloud's cases, the registry's headings, the healthy project), `test_instruction_brief_facts.py` +6
  (the price median on a hand-worked table of three edges with the exact half, the table, the entry's own, three
  seeded faults and a null one), the scenario-set / page-object / stack-address tests +5 (S-014's file, the two new
  `Answers` reads), and small moves in the instruction tests (BRIEF's cases and rows out, v20's in).
- **The DRY marks at zero spend against keel-cloud-docs `9a033fe`**: the master checkout's `build/brief-facts/` predates
  104 (no `commercial.priceMedian`; written 2026-10-15), so the two canon tests skip there by name. Measured instead on
  a scratch copy of `9a033fe` (`git archive`, `./gradlew test --tests '*BriefFactsCorpusTest'`, exit 0): **`brief_facts`
  101 of 101** (87 cards, 7 pilots, 7 price medians; 05-paidly *£50 a month or more · 5 of 8*), **`report_overview` 49
  of 49** (7 parts on 7 entries). Nothing was written to the master checkouts.
- The healthy project's expected standings held to keel-cloud's own engine on the same scratch copy
  (`instructions/compare.py`): **16 of 16** after one move -- Ability to pay reads drift *stronger* (a new line signed off
  beyond *mostly from spend*), still HOLDING_UP.

## Where things are

| Piece | Place |
|---|---|
| the price median, the two card lines | `instructions/brief_facts.py` `price_table`, `price_median`, `price_median_for`, `could_phrase`, `card` |
| the Overview drawing, its DRY compare | `instructions/overview.py` (`overview`, `parts`, `compare`, `in_order`, the 077 words) |
| the v20 rubric | `instructions/marks.py` (paragraph, calls 116-120, `report_overview` row), `instructions/marks.toml` |
| the themes fake, the Insights words | `harness/interviewer_fake.py` (end of file) |
| the five report marks | `evals/report_marks.py` (`scorecard(record)`, `owed`), written per journey to `report.json` / `report-marks.json` |
| the readers | `harness/vectors_screens.py` `Answers.board` / `insights` / `pilot` / `brief(printed=True)` / `vector_page` |
| the journey | `evals/corpus_scenario.py` `leg_report`, `report_record`, `_score_report`, `_themes_on_return`, `_board`, `_too_few` |
| the healthy project | `evals/preludes.py` `healthy_entry`, `HEALTHY_PICKS`, `healthy_expected`; `evals/test_s014_green.py` |

## Judgement calls decided

1. **The healthy entry is built, from 05-paidly** (spec call 1). No revision-11 entry holds on every dimension on ten or
   more -- read off each entry's `expected`: every one of the seven has a vector not holding up, split, too few or left
   out -- so the spec's fallback is taken, as keel-cloud's `InsightsSimulationTest` baseline is: 05-paidly's market,
   statements, lists, calibration and window whole; the answers are its ten gate-yes, un-chipped specialists (stories
   kept, each read as anchored) and its eight decision-makers plus two (*Ava Larch*, *Ben Rowan*), each answering one
   supporting template a link (`HEALTHY_PICKS`), so **no pick is against on any rung** (a unit test holds the template to
   the registry's `against` codes) and nobody is owed a follow-up; pilot sign-ups are the corpus's (2 of 20). The
   decision is BUILD, *Fairly sure*; the price tile *£50 a month or more · 10 of 10*. The S00 baseline was not reused:
   it has two people against on every dimension, who would be owed follow-ups.
2. **`report_binding` compares tokens** (spec call 2): words of four letters or more, lower-cased, and every number
   (`report_marks.tokens`) -- a page's tokens minus its frame (kicker, title, meta, foot) must be within its view's; the
   breakdown's within the stage pages', every string and number of `StandingsView`, and the tables' own headings.
3. **Names and the bump** (spec call 3): `report_overview`, `report_insights`, `report_no_repeat`, `report_pilot`,
   `report_binding`. `MARKS_VERSION` 20 retires `brief_answers` (call 116), bears `report_overview` as a zero-spend row of
   `judge()` (call 117: keel-cloud's facts drawn as the Overview against the corpus's reading -- one check a hero, a
   tile, a panel and the foot), refuses bundles below 20 (118), and moves `brief_facts` (119). The other four read a
   page, which an instruction-eval run never has, so they are **journey marks** in `evals/report_marks.py`, owed whenever
   the record carries their subject and failing the journey, never rows of `judge()` -- a row there would fail every
   instruction-eval run by construction (call 120). `report_overview` is scored on the journey too, page against wire.
   Acceptance 2's "the four new corpus marks" is read as these four.
4. **The Insights empty state on a project nobody has answered**: the design's rule draws *Nothing is failing* "otherwise",
   whose line says *Every dimension holds on 10 or more people*; the eval predicts *Nothing to read into yet* whenever the
   decision is KEEP_INTERVIEWING or a card is too few or not asked (`report_marks.thin`). If 077 draws the other one,
   that is DRIFT #92's to read, not a tolerance.
5. **The too-few state is read before anyone answered** (FR-7): its four words -- *Keep interviewing*, *Nothing to read
   into yet*, *Not asked yet* on the price tile, *nobody has answered this yet* on every commercial row -- hold together
   only at zero answers on a consumer entry (Countly asks Price of everyone, so from the first priced answer the tile has
   a median); `_too_few` widens the existing read in `leg_invite` (044's *None yet*), on every corpus journey.
6. **Words in order, not elements** (`overview.in_order`): 077 was not built when this was written, so the readers take
   each part's `text_content` (`report-hero`, `[data-tile]`, `report-stage-*`, `a.rp-row[data-dim]`, `.rp-ibox[data-dim]`,
   `.rp-themes li`, `.rp-quote`, `.rp-person[data-invitation]`, `article.page[data-page]` -- 077's spec's selectors) and
   the marks ask that the predicted words appear in that order. The words *as 077 defines* live in `overview.py`,
   `interviewer_fake.py` and `report_marks.py`, one place each; the journey pass moves them there if 077 words them
   otherwise. A source check holds them to 077's source once `src/components/report/` is on keel-web's master.
7. **The themes prediction's input is the stage row's own follow-ups** (`people[].followUp`, contract 19), in the row's
   order -- the wire's, not the walk's typed lines, so S-012's live cell reads the same; the served quotes are predicted
   shortest first (design §7), the job's order on a tie, three at most. On the live cell (FR-9) themes are held for shape
   only: three at most, counts within `answered`, every quote a named person's verbatim follow-up.
8. **Panel leads**: *{k} of {k} holding.* counts the stage's holding rows; *Too few to call: {n} answered* takes the
   smallest `n` among the stage's too-few rows; the boxes are worst first (NOT_HOLDING_UP, then PEOPLE_DISAGREE), then
   in the registry's order.
9. **The price median is the corpus's own counts restated**: the Price standing's `optionCounts` over the founder's
   ladder (`PriceLadder.bands` low edges; *under* floors at 0, *would not pay* counts in `n` only), not a recount of the
   picks -- the counted picks are the anchored ones, which `optionCounts` already is.
10. **Two of 051's lines made here** so the unit run holds against keel-cloud 103: `KINDS` gains FOLLOW_UP and `UNSPOKEN`
    takes it (051 FR-3, byte for byte as 051 words it); and IM13 / the interviewer leg read THEMES with
    `themes:on-return` where they read BRIEF with `brief:on-return`. `INTERVIEWER_MARKS_VERSION` is not bumped here: 051
    bumps it to 5 and takes this reading with it.
11. **THEMES is in the scripted executor's screen table and the script carries no THEMES entry** (D-01): the runtime
    then names the screen it cannot answer.

## Discovered

- **D-01 (blocks acceptance 2's themes, keel-runtime's to fix or the eval's to work round):** keel-cloud 104 says the
  eval founders' THEMES jobs are "answered by keel-e2e-eval's scripted executor, which mirrors this grouping" -- but
  keel-runtime's `ScriptedExecutor` answers a screen from an ordered list written before the run, and a THEMES answer
  depends on its context (`answerIds` are the stack's invitation ids) while the jobs run one a failing dimension in no
  fixed order. It needs a context resolver beside INTERPRET's (`_resolve_interpret_result`): the fake's grouping
  (`harness/interviewer_fake.themes`, held to `FakeThemes`) applied to `context.answers` with `context.name`. Until
  then every eval founder's THEMES job fails *no entry for THEMES* and the Insights view serves the raw fallback; on
  the scripted stack `report_insights` then fails on the fake's labels (as it should).
- **D-02:** keel-web's master moved from `43cc2ee` to 076 (`c9ce17c`) while this ran; one unit test of 051's seam
  (`fakeSpeech.ts`'s mic `acquire`) went red. Not changed here.
- **D-03:** at `3ac82f1` the unit run was already red against keel-cloud-docs `9a033fe` (2 failed, 4 errors, all from
  103 / 104); spec 052's "2,391 / 53 before" predates the sibling move.
- **D-04:** the master checkout's keel-cloud `build/brief-facts/` predates 104, so both canon DRY tests skip there; a
  `./gradlew test --tests '*BriefFactsCorpusTest'` in keel-cloud-docs would un-skip them (not run there: read-only).
- **D-05:** keel-cloud 103 / 104's Purchase friction line is *did not need {step}, or it was quick*, not the design's
  *needed {step}*; the eval follows the cloud's (`BriefFacts.card`), since the cards are the cloud's one source.
- **D-06:** 077 FR-2 words the price tile *… {chose} of {n} decision-makers* on a consumer study too (Countly: *7 of 8
  decision-makers*); predicted as written, named under DRIFT #92 for the journey pass to look at.
- **D-07:** spec 051 named DRIFT #92 its next number; this spec's reservations are #92 and #93, so 051's first is #94.
- **D-08:** S-014 is in no matrix cell yet (`matrix/cells.toml` carries s005 / s006 / s007 / s013 on the macOS Claude
  cell); adding it is a cost call (20 walks) for the coordinator once it is green.
