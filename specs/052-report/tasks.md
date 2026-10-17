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
- [x] T008 DRIFT #93 and #94 reserved (`runs/DRIFT.md`; written #92 / #93, renumbered on the rebase onto 051, whose
  #92 is the consent line); `make unit`; this file
- [x] T008b D-01 resolved on keel-runtime 012 (master `3988131` = 0.8.0, bundled in keel-connect-skill 2.5.0
  `c677950`): `vectors_script.themes_entries` writes the script's THEMES entries -- one a dimension the entry leaves
  failing that the walks give follow-ups on, the fake's piles of the posted texts, then the catch-all -- and
  `context_keys_for` refuses a THEMES row that is not `dimension, name, rungHeading, answers`
- [x] T009 acceptance 2: `make eval K="s005 or s006 or s007 or s014"` **4 passed in 862 s** on a fresh stack (keel-cloud-docs
  `80d4259` = code `9a033fe` + keel-web `b89bc32` + runtime 0.8.0) -- the page objects held to 077 as built, all five
  report marks measured and met on every journey, the too-few state on S-005 (and on the other three), THEMES resolved
  on the stack for every predicted dimension (see *Acceptance 2, measured*)
- [ ] T010 **owed**: acceptance 3 -- remote journeys on staging once 104 + 077 are deployed there. DRIFT #93 filled
  (the zero-answer Insights line, and 077's own words), #94 released (nothing repeated)

## Acceptance 2, measured (2026-10-17 UTC, the journey pass)

One fresh stack, `make eval K="s005 or s006 or s007 or s014"`: **4 passed in 862 s** on keel-cloud-docs `80d4259` (code
`9a033fe`, spec 104) + keel-web `b89bc32` (077 on 076) + keel-runtime `3988131` 0.8.0 bundled in keel-connect-skill
`c677950` 2.5.0; `make down` after. Earlier single-journey runs (each on its own fresh stack) found the eight fixes
listed under *The journey pass's fixes*; this run is the first after the last of them.

| Journey | Run | Time | Report marks | Interviewer marks | THEMES on the stack |
|---|---|---|---|---|---|
| S-005 countly | `20261017T185504Z-s005-countly` | 303 s | **5 of 5** | 21 of 21 | Current solution: *quick* (1), *habit* (1); against 3, asked 2, Importance took 1 |
| S-006 paidly | `20261017T190008Z-s006-paidly` | 299 s | **5 of 5** | 26 of 26 | Price: *proof* (1), *seeing* (1), against 3, asked 3, 1 skipped; Buyer and payer: *manager* (1), *finance* (1), against 4, asked 2, Price took 2 |
| S-007 mulchrun | `20261017T190507Z-s007-mulchrun` | 132 s | **5 of 5** | (no leg) | Importance: *two* (2), against 3, asked 3, 1 skipped; Commitment: *free* (1), *short* (1), Buyer and payer took 1 |
| S-014 green | `20261017T190719Z-s014-green` | 125 s | **5 of 5** | (no leg) | none due: `insights[]` empty, the catch-all unused |

- Every scripted THEMES entry resolved on keel-runtime 0.8.0: the served labels are the fake's, the counts its, the
  quotes the walks' own lines under the invitations' names -- `report_insights` strict on all four. The dimensions with
  no question (S-006 Existing sacrifice, Ability to pay, Purchase friction; S-007 Prevalence, Purchase friction) and
  S-007's Current solution (every one against taken by Importance) are boxes with no themes, as served.
- The too-few state, every journey: before anyone answered *Keep interviewing*, the price tile *Not asked yet*,
  *nobody has answered this yet* on every commercial row not left out, and the Insights view **Nothing is failing**
  (077's rule; DRIFT #93); after the fourth answer *Keep interviewing* and **Nothing to read into yet · 4 people have
  answered** (`_too_few_answered`).
- The price median on the wire equals `brief_facts.price_median_for` on the three corpus entries (*£20 a month · 7 of 8*,
  *£50 · 5 of 8*, none on Mulch Run's left-out Price) and on S-014 (*£50 · 10 of 10*); S-014's standings hold up on ten
  everywhere, decision BUILD, nobody owed a follow-up, the binding pages 1-4.
- `report_no_repeat` met everywhere (DRIFT #94 released); `report_binding` met with the tab title *{project} — Keel
  brief — 17 October 2026* and *Preparing your brief…* seen first.
- `make unit` after the pass: **2,587 collected = 2,532 passed / 55 skipped, 0 failed** (the 077 words source check now
  runs against keel-web's master and passes).

### The journey pass's fixes

1. **Each read loads the report afresh** (`Answers._report`): the page reads the standings once a mount, so a page left
   open drew the earlier wire (S-005's after-four read drew *0 answered*).
2. **One stage row open at a time**: opening a second rung's row closed the first, so each follow-up row is opened (again)
   right before its people are read; the line is `.dimpeople__follow`.
3. **Tokens from spaced DOM words** (`_words`, the harness's `_SCREEN_TEXT_JS`): `text_content` runs two elements'
   words together (*call* + *Pilot* = *callpilot*), so the binding's pages, their frames and the Insights / Pilot view
   texts are read with a space between text nodes.
4. **077's words as built**: *k of n holding.* over `dimensionsHolding` / `dimensionsTotal`, *Too few to call* over
   `peopleAnswered` (both off the wire's vector); a left-out card's row reads its served line (077 call 8); the
   said-why tail and `TOOK_BY` / `NO_FOLLOW_UP` as `translate.ts` composes them; KEEL_MANAGED *Keel-managed*; *Keel
   never emails …* only beside people; the tab title's date as `dayWords(asOf)`; the breakdown's own labels (price
   table, *Start here*, *Test this* ...) as chrome.
5. **Call 4 re-decided to 077's rule** (`report_marks.thin`: a card TOO_FEW_TO_CALL), the zero-answer line filed as
   DRIFT #93.
6. **`InferenceCharge.VERSION` 10** (keel-cloud 104: BRIEF out, THEMES in): the interviewer's and the contacts' HOLD pins
   moved 9 -> 10 (`interviewer_fake.PRICE_VERSION`, `contacts_fake.PRICE_VERSION`); IM1 failed on 9.
7. **S-006's people count** reads the eyebrow and the foot (*Overview · locked · 20 answered*); the people tile went with
   the deck.
8. **The relink after a return** (keel-cloud 104 Discovered 5): Sent's *Make a new link* may meet 409 once and keel-web
   retries (`withOneRetry`); `Interviews.make_new_link` keeps every relink response and reads the last, the one the
   dialog drew (`retried` records the others; none on the acceptance run). The report's scorecard moved off
   `j.screens` (`Journey.report_card`), whose every entry S-007's currency sweep reads for text.

## Measured (2026-10-17, no stack)

- **051 has NOT landed first** (contrary to the spec's acceptance 1), so the count is measured against master
  `3ac82f1`'s own number on the same siblings. `make unit` on `3ac82f1` against keel-cloud-docs `9a033fe` (104):
  **2,444 collected = 2,385 passed / 53 skipped / 2 failed / 4 errors** -- the 2,391 / 53 of spec 050 plus four red
  that 103 / 104 caused: `test_the_real_validator_takes_the_asked_screen` (BRIEF gone from the validator),
  `test_the_kinds_are_keel_clouds_own` (103's `ClipKind.FOLLOW_UP`), and `test_instruction_brief_reading.py`'s four
  (no `brief.md`). All six are fixed or deleted here.
- **After the rebase onto 051 (master `ad916b8`)**: master itself on keel-cloud-docs `9a033fe` is **2,475 passed / 53
  skipped / 2 failed / 4 errors** (the coordinator's 2,477 / 57: the same run, the six BRIEF reds counted in), the six
  BRIEF-only reds this spec deletes or fixes. This branch: **2,587 collected = 2,531 passed / 56 skipped, 0 failed**.
- Before the rebase: **2,490 collected = 2,433 passed / 56 skipped / 1 failed** at `93623d0`; **2,495 = 2,438 /
  56 / 1** after T008b (five THEMES-script tests). The one red then was not this spec's:
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
| the THEMES script | `harness/vectors_script.py` `themes_entries`, `walked_follow_ups`, `failing_keys`, `THEMES_KEYS` |

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
4. **The Insights empty state follows 077's rule** (re-decided on the journey pass): *Nothing to read into yet* when no box
   and a card is TOO_FEW_TO_CALL (`report_marks.thin`, keel-web `insightsStateOf`), else *Nothing is failing* -- which on a
   project nobody has answered says *Every dimension holds on 10 or more people*: filed as DRIFT #93, not tolerated
   in the prediction and not a fault of the page against the wire.
5. **The too-few state is read twice** (FR-7): before anyone answered (`_too_few`, widening 044's *None yet* read in
   `leg_invite`) -- *Keep interviewing*, *Not asked yet* on the price tile, *nobody has answered this yet* on every
   commercial row not left out -- and after the fourth answer (`_too_few_answered`) -- *Keep interviewing* and *Nothing
   to read into yet* -- because with 077's rule the spec's four words never hold at one moment (at zero the Insights view
   is *Nothing is failing*; from the first priced answer the price tile has a median). Both on every corpus journey.
6. **Words in order, not elements** (`overview.in_order`), on 077's selectors as built (its tasks.md table: the tabs
   `button[role=tab][data-view]`, `#report-view`, `h1.rp-verdict[data-label]`, `.rp-why`, `.rp-shipcap`, `[data-tile]`
   with `.rp-tile__*`, `.rp-pname` / `.rp-pill` / `.rp-plead`, `a.rp-row[data-dim][data-status]`, `.rp-ibox`,
   `.rp-concern`, `.rp-themes > li`, `.rp-quote`, `.rp-tookby`, `.rp-nofollow`, `.rp-raw`, `.rp-inone`, `details.rp-person`,
   `.rp-pbody`, `.rp-pnote`, `article.page.rp-page` with `.rp-kick` / `.rp-pt` / `.rp-pmeta` / `.rp-pfoot`); a part's
   words are its `text_content`, a token's text the spaced DOM words (fix 3), and
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
10. **Two of 051's lines were made here before 051 landed** (`KINDS` / `UNSPOKEN` gaining FOLLOW_UP); on the rebase onto
    `ad916b8` 051's own words were kept. IM13 / the interviewer leg read THEMES with `themes:on-return` where they read
    BRIEF with `brief:on-return` -- this spec's reading, carried under 051's `INTERVIEWER_MARKS_VERSION` 5. The Insights
    view's no-question reasons are `interviewer_fake.NO_FOLLOW_UP_WHY` (a dict, beside 051's `NO_FOLLOW_UP`, the tuple
    of the five keys; the first build of this branch shadowed 051's name, renamed on the rebase).
11. **THEMES is scripted by dimension and by text** (D-01, resolved): keel-runtime 012 chooses a THEMES entry by the
    context's `dimension` (never the cursor) and resolves each theme's verbatim `answers` texts to the context's ids.
    `themes_entries(entry, follow_ups)` writes, for each dimension in `failing_keys(entry)` (the entry's standings not
    holding up or split, registry order) that `follow_ups` (`[(rung, text)]`) reaches, the fake's piles
    (`interviewer_fake.themes`, labels the fake's) with each pile's texts once each in posting order (a text two
    people typed resolves to both ids), then a catch-all `{themes: []}` -- so a dimension nobody expected to fail is
    accepted with no themes (served as the raw fallback where it has answers) rather than refused. `follow_ups` comes
    from `walked_follow_ups(entry, person_inputs(entry))`: each person's posted line (`PersonInputs.follow_up`) on the
    rung their own picks go against first (`interviewer_fake.first_rung` over `founder_side(entry)`), read directly
    since the rebase onto 051 (the `getattr` seam is gone). The texts are 051's composed `FOLLOW_UP_LINES` (r11 records
    no follow-up), the strings the text walk types -- not corpus text. The scripts carry, after the rebase: S-005
    Current solution (*quick* / *habit*); S-006 Price (*proof* / *seeing*), Buyer and payer (*manager* / *finance*);
    S-007 Importance (*two*, both lines), Commitment (*free* / *short*); S-014 the catch-all alone; S-012 is live
    (no script). Each held by `test_every_scripted_text_is_a_line_the_walk_posts` against 051's real lines and the
    fake's grouping of them; S-006's Existing sacrifice, Ability to pay and Purchase friction fail but have no rung.

## Discovered

- **D-01 RESOLVED (keel-runtime 012, 0.8.0; judgement call 11):** keel-cloud 104 says the
  eval founders' THEMES jobs are "answered by keel-e2e-eval's scripted executor, which mirrors this grouping" -- but
  keel-runtime's `ScriptedExecutor` answers a screen from an ordered list written before the run, and a THEMES answer
  depends on its context (`answerIds` are the stack's invitation ids) while the jobs run one a failing dimension in no
  fixed order. It needs a context resolver beside INTERPRET's (`_resolve_interpret_result`): the fake's grouping
  (`harness/interviewer_fake.themes`, held to `FakeThemes`) applied to `context.answers` with `context.name`. Until
  then every eval founder's THEMES job failed *no entry for THEMES*. keel-runtime 012 now chooses entries by dimension
  and resolves texts to ids; the script writes them (`themes_entries`). Held by `tests/test_report_marks.py`: the
  entries written from C3's and S03's texts alone, resolved by keel-runtime's own `ScriptedExecutor` (imported from the
  sibling checkout, 0.8.0) against the jobs' contexts in reverse order and twice, equal `FakeThemes`' results; a
  dimension nobody scripted gets the catch-all's empty themes; every scripted text of the three corpus scripts is a
  line some person posts. **What may still not resolve cleanly**, for the journey pass: (a) a follow-up said on an AI
  link (S-005's and S-006's interviewer legs) is the stack's fake transcriber sentence (051's
  `KEEL_INTERVIEWER_FAKE_FOLLOW_UP`), not a scripted line -- those people answer after `leg_report`, so the report
  marks never see it, but the THEMES regrouping on the next return leaves that sentence out of every theme (accepted,
  not refused), so a later Insights read would differ from the fake over the whole context; (b) the cloud stores the
  follow-up under `TextBoundary` -- a line it trimmed or normalised would no longer equal the scripted text and the job
  would be refused by name (051's lines carry no edge space, so none is expected); (c) the rung of each line is 051's
  `first_rung`; the cloud refuses a response whose `followUp.dimension` is not its own walk's, so a disagreement would
  fail the walk before it reached THEMES.
- **D-02 (resolved by 051):** keel-web's master moved from `43cc2ee` to 076 (`c9ce17c`) while this ran; one unit test of
  051's seam (`fakeSpeech.ts`'s mic `acquire`) went red. 051 (`ad916b8`) re-read it; green after the rebase.
- **D-03:** at `3ac82f1` the unit run was already red against keel-cloud-docs `9a033fe` (2 failed, 4 errors, all from
  103 / 104); spec 052's "2,391 / 53 before" predates the sibling move.
- **D-04:** the master checkout's keel-cloud `build/brief-facts/` predates 104, so both canon DRY tests skip there; a
  `./gradlew test --tests '*BriefFactsCorpusTest'` in keel-cloud-docs would un-skip them (not run there: read-only).
- **D-05:** keel-cloud 103 / 104's Purchase friction line is *did not need {step}, or it was quick*, not the design's
  *needed {step}*; the eval follows the cloud's (`BriefFacts.card`), since the cards are the cloud's one source.
- **D-06:** 077 FR-2 words the price tile *… {chose} of {n} decision-makers* on a consumer study too (Countly: *7 of 8
  decision-makers*); predicted as written, named under DRIFT #93 for the journey pass to look at.
- **D-07:** 051 landed first after all (master `ad916b8`) and took DRIFT #92 (the served consent line is not design
  §9's); on the rebase this spec's two reservations moved #92 -> #93 (what the report shows that the wire does not say)
  and #93 -> #94 (a number the Insights view repeats), each entry saying so.
- **D-09:** `GET /v2/inference-interactions?project_id=` lists no THEMES row on the stack, so `_themes_on_return`'s job
  count reads none (vacuous) and its wait ends on `insights[]` itself (every insight with answers carrying themes or
  raw); the themes' arrival is proved by their labels, which only the scripted executor's resolution can produce.
- **D-10 (051's to read):** a spoken story on the speak-or-type box ends in the stack fake's *yes* (S-005, Priya
  Natarajan's: *… fixed the sheet. yes*), the transcript appended to what she typed -- 051's walk, not this spec's.
- **D-08:** S-014 is in no matrix cell yet (`matrix/cells.toml` carries s005 / s006 / s007 / s013 on the macOS Claude
  cell); adding it is a cost call (20 walks) for the coordinator once it is green.
