# Tasks 064

Built on keel-e2e-eval master `a34fbf9` (+ the spec's last amendment `3f5b520`), branch
`064-harness-follows-the-fixed-chain`, against keel-cloud-docs master `90fd6dc4` (114-124, contract 33, corpus
revision 13) and keel-web master `8b8eb9d` (093, 099, 094, 095, 096, 097). **keel-web 098 (market OTHER, the decision's
named change drawn, 117's / 118's screens) and 100's attribution band were not on keel-web's master when the stack ran**
(see *The eval run*). Neither sibling was written to by this build (the stack run builds and runs them in place, as
every `make up` does). `MARKS_VERSION` 20, unchanged.

Worktree note: `stack.toml`'s four sibling paths are relative and wrong from `wt/`; they were pointed at the absolute
checkouts with `git update-index --skip-worktree stack.toml` for the build and the run, and **restored** (the file
back to master's bytes, `--no-skip-worktree`) before handing back. The worktree has no `.venv`; every command ran with
the main checkout's (`make ... VENV=/Users/athulrajeev/Documents/projects/keel-e2e-eval/.venv`).

## FR-1 Revision 13

- [x] T001 `instructions/corpus.py`: docstring opens on **Revision 13 only**; `REVISION = 13`; `_REVISION_OF[12]`
  (*MARKS_VERSION 20's corpus, before the commercial chain (keel-cloud 115: a cost with no unit, a price with no
  shape)*); the refusal keeps its code.
- [x] T002 `instructions/chain.py` (new): read-only ports of keel-cloud's `CommercialChain` as `sim/check_corpus_r13.py`
  ports them -- `cost_in_chain` / `price_in_chain`, the words (`cost_said`, `cost_belief`, `price_said`,
  `price_belief`, `free_line`, `ability_belief`, `ability_phrase`), `reading`, `derive`, the chain ladder (`bands`,
  `codes`, `floor_of`), `words_fault`, `equation_words` / `locked_words`.
- [x] T003 rule C in the loader (`_check_chain`), in the checker's sentences: the half chain; the cost's fields, mode,
  range, percent at most 100, the six periods, currency, unit / base / measure / lossPhrase words, HOURS at a rate
  only on B2B, the engine's belief sentence and phrase; the price's fields (*a chain price's period, base and unit are
  the cost's*), shape, share / amount bounds, FREE only with a payer, shareBase on SHARE only, the engine's words;
  Ability to pay the engine's reading; the three chain rows (value box / `dont_know`, the chain ladder, the consumer
  budget item); every chain pick (value box `{low, high, currency, period}` in the founder's period, nothing, the
  chips, `[<one-off>, <plan>]`, a budget code only on a budget reading). A cost with no unit and a price with no shape
  are read exactly as r12 (`_check_price_and_total` / `_check_cost_first` skip only the chain's parts).
- [x] T004 Registry-bound: a chain row is held by rule C, never the registry's (`_chain_row`); under keel-cloud's
  registry (decision 24: `value_box`, escape `dont_know`) an off-chain cost row keeps spec 077's `cost_total` /
  `cant_recall` (`_registry_row`, the registry's own guidance). `instructions/registry.py` accepts decision 24 in its
  invariants (`value_box`, the six periods, the chain's three modes) and `plan_keys` learns FREE (no price item) and
  the consumer budget item on a same-person budget study.
- [x] T005 `price_ladder_codes(low, price=None)` chooses the chain ladder by the price's shape (115 judgement call 6).
- [x] T006 `Person.in_segment` (optional, primary link only; an outside person carries nothing else),
  `persona.decision_maker.title` (1-5 words), `Entry.chain / reading / consumer_budget / decider_title`,
  `corpus.PREVALENCE_BINS` / `prevalence_bin` (123 FR-6's half-open edge mirrored).
- [x] T007 Tests: `test_corpus_r11_shape.py` at revision 13 (the seven at 13 and none in the chain; an r12 file
  refused by name; three chain entries accepted -- Fresco, Karsa, AirCaps -- with the engine's reading, the chain
  rows and the consumer budget plan; **twenty** rule-C refusals, each from a one-line change; the half-open bin and no
  entry on an edge); `test_instruction_corpus_r11.py` (the refusal sentence at 13, the r12 refusal); the back-test
  loader test over the folder's **28** entries (26 in the chain, 30-realroots and 35-candle with no cost today).
  `09-fixture.yaml`, `10-fixture-b2b.yaml` and `backtest/99-broken.yaml` at `revision: 13`, nothing else moved.

## FR-2 The founder's chain screens (keel-web 094)

- [x] T008 `vectors_script.calibration_answers`: a chain cost posts every field the entry carries (currency included,
  as the contract allows); a chain price its shape and numbers and no period.
- [x] T009 `Corridor.single` -> `_chain_cost` / `_chain_price` on keel-web 094's selectors (the way's pill, the unit
  box, the period pill, a rate's `%` / count word and *of what they lose*, the two numbers, `chain-rate` on HOURS; the
  shape pill, the two amounts, the share's sub-choice and percent, up front / the plan / *then nothing*), reading the
  equation (`chain-equation`, `chain-per`) and the locked words (`chain-locked`) back; `Corridor.chain_screen`.
  `_hold_the_chain_screen`: the equation and the locked words carry *per <unit>* and the cost's period.
- [x] T010 Old-shape answers drive spec 074's controls as before -- reached by writing the corpus's r12 cost on the wire
  first (judgement call 1).
- [x] T011 `_hourly_rate` runs off the chain as before (every B2B golden entry) and on the chain only for an HOURS cost.

## FR-3 The stranger's chain items (keel-web 094, keel-cloud 115)

- [x] T012 `Pick.interval` (sent as `interval`, never re-expressed by `asked_over`), the value box's chips (`NOTHING`,
  `DONT_KNOW`, `RATHER_NOT_SAY`), two option ids on up front then a plan, the consumer budget code.
- [x] T013 `Interview._answer`: the value box's two inputs, its chips by their served labels, the plan's second screen
  (Next, its question awaited, the plan's band); `_item_screen` records `value_box_label`, `what_you_get` and the plan
  (question and bands) in `screens`. `_answer_one` counts the value box's chips as offered.
- [x] T014 `plan_keys`: FREE asks no price item; the consumer budget item on a same-person chain budget study.

## FR-4 / 4a / 4b / 4c The gate

- [x] T015 A problem-led founder Prevalence clause per golden entry (`PROBLEM_CLAUSES`, 116's *Proposed after*, each
  framed within 20 words) -- `event_past` (the founder's) and `event_base` (the gate's).
- [x] T016 The segment's core and condition per golden entry from 120's table (`SEGMENTS`: 01-05 carry one, 06 and 07
  none); CONTEXT_INTERPRET writes `segment {core, condition}`, the plain occasion noun, `window.proposed` null and no
  `understands`; the part-1 RESPONDENT_QUESTIONS result writes `condition {question, inside}` (E5).
- [x] T017 `Interview._gate`: the chip first where served (`segment-chip`, its radiogroup, Yes / No by `inCodes`),
  outside -> Continue posts `{"outsideSegment": true, "answers": []}` and nothing more; the gate's No reads `noLabel`;
  *I'd rather not say* where served (`STORY_CHIPS` sends `RATHER_NOT_SAY` again). `_hold_the_screens` holds the two
  story chips, the chip's question and the gate's question as served; the gate is no longer asserted to carry the
  circumstance.
- [x] T018 `item-stem` + `h1.iv-q` joined into `question` (`stem` / `asked` kept apart); unused by the golden script (no
  stem scripted) -- judgement call 3.
- [x] T019 `PersonInputs.in_segment` / `response()`; a back-test `in_segment: false` loads (T006).

## FR-5 / 5a / 5b / 5c The lists

- [x] T020 Current solution's draft carries `founder_rungs` (2 or 3, the rungs the Answer types) and `line` 2;
  `_corpus_list` (founder's rungs verbatim and first) unchanged and still true.
- [x] T021 The Choose screens pick by label as before; `choose.prompt` is recorded (`prompt`), never pressed.
- [x] T022 05-paidly's J1 note: `vs.jargon` / `expected_j1` (121's `JARGON_WORDS`); `leg_interpret_solution` holds the
  idea's J1 notes to it on every golden entry (*platform* on 05, none elsewhere).

## FR-6 / 6a The persona and the option words

- [x] T023 `Corridor.persona` types *What is their job title?* -- the entry's `persona.decision_maker.title`, else the
  role word (no golden or back-test entry carries a title: every B2B entry sends its role word, recorded);
  `leg_persona` asserts `deciderTitle`; the decider banner (`_vector_page`, S-006) accepts the title or the role.
- [x] T024 `PREVALENCE_OPTIONS` read as `PrevalenceBins` writes them; every other option word is read off the served
  labels (the walker picks by option id -> served label), so 123's Compatibility, Buyer and payer and escape words need
  no copy.
- [x] T025 `brief_facts.pilot_for` counts the gate's Yes alone and names the rest (`notCounted`).

## FR-7 / 7a The follow-up ladder (keel-cloud 118)

- [x] T026 `interviewer_fake.LADDER` re-copied (Purchase friction a rung; the plain stems), `ALSO` (the three second
  stems), `NO_FOLLOW_UP` the four, `FILL_DEFAULTS` `{smaller_step}`, `LADDER_SHA` `f280c5ae`, `RUNG_HEADINGS`,
  `NO_FOLLOW_UP_WHY`; `ordered`, `apart`, `owed`, `first_stem`, `first_rung(..., first=)`, `deciding_lines`;
  `Founder.chain_price`.
- [x] T027 The journey reads the deciding lines off the served standings before each walk and holds the route to the
  stem it owes (`follow_up_question(..., first=)`, second stems filled).
- [x] T028 Commitment: a corpus `yes_after_trying` rides on the served conditional option where one is served, on
  *probably not* where none is (`_served_commitment`, `PersonInputs.remapped`, `_served_options`, a finding each).
- [x] T029 One follow-up line a rung (judgement call 4); the THEMES script carries every rung's line.
- [x] T030 `brief_facts` cards: Commitment's number the step as asked and the conditional yes apart, Adoption friction's
  the plain yes, Purchase friction the fear held, its bar and its words (`friction_words`, three bands).
- [x] T031 `test_follow_up_ladder.py` re-pinned (the hand-worked table, the second stems, the deciding line first, the
  chain price's edge, the walks' sizes); keel-cloud's `executor-fixtures/THEMES/cases.json` is read in place (the eval
  keeps no copy), and the fake now matches it (ON_THEIR_OWN).

## FR-8 / 8a / 8b / 8c Insights and the decision

- [x] T032 The themes fake: leftovers in one last `ON_THEIR_OWN` group; quotes uncapped; one answer its own group.
- [x] T033 `report_insights` on contract 28: a box a dimension with words (any status), worst first and the dissent
  boxes last, `state`, `quotes` named and covered once, `answered` the quotes', `noQuestionWhy` null, the dissent
  frame, GROUPING / RAW lines, `notAsked` lines (not a line with words), GROUPED on the scripted stack.
- [x] T034 `Answers.insights` on keel-web 095's selectors (`rp-themes__label`, `li[data-own]`, `data-state`,
  `data-dissent` / `.rp-frame`, `.rp-iq .rp-pick .rp-opt .rp-side`, `insights-grouping`, `.rp-raw__note`,
  `insights-more` opened, `insights-not-asked li[data-dim]`); `.rp-frame` is one of the view's own lines.
- [x] T035 `_themes_on_return` and `backtest.themes_settle` read `insights[].state` (and `notAsked`).
- [x] T036 `overview.hero` reads `decision.change` (and `.also`) in place of the semicolon join, deleted;
  `brief_facts.DECISION_CHANGE` (122's seven golden sentences) for the corpus reading.
- [x] T037 `leg_context` holds the card to code's assembled read-back (`vs.read_back`, a port of `ReadBack.sentence`
  over the scripted slots; 06 and 07 equal 122's table word for word, unit-tested) and the *Only people who:* line.
- [x] T038 `leg_project` reads `GET /v2/markets` (the entry's country listed) and `market.kind` (absent on every table
  market); keel-web 098's *Another country* is not built, so no OTHER market is walked.
- [x] T039 `sampling` on job payloads: nothing to do -- keel-runtime's scripted executor matches on the context's keys,
  never the payload's other keys, and the eval's fakes read neither.

## FR-9 The back-test runner

- [x] T040 `backtest.md` / `.json`: the equation and locked words, the value box's label and chips, what you'd get,
  the plan, the gate's chip, the decider's title, the decision's change, `outsideSegment`, each insight's state, note,
  frame and every quote's side, the `notAsked` lines; the refused step's finding keeps *Keel couldn't finish this step*
  (`REFUSED_LEAD`, keel-web 093's lead). The first round's artefacts (pooled lines, the Importance probe, the hourly
  rate by API, quarterly / 3) stand as they were for golden entries; see judgement call 4 for the pooled lines.

## FR-10 Marks

- [x] T041 `MARKS_VERSION` 20 unchanged; `instructions/marks.py` gains the Spec 064 paragraph (r13 by sha256 at
  keel-cloud-docs `7915eef`, equal to `corpus-r13/`) naming the marks whose words or numbers moved (below);
  `test_instruction_marks.py` holds the r13 digests.

## The eval run (2026-10-23, one run, `make eval K="s005 or s006 or s007"`)

A fresh local stack (`make up`, 05:07:25-05:07:46 UTC, all gates passed) of keel-cloud-docs master `90fd6dc4` and
keel-web master `8b8eb9d`; keel-runtime `3988131` (0.8.0, bundled in keel-connect-skill `c677950`). keel-web 098 and
100's attribution band were **absent** from keel-web's master (it still stood at 097's `8b8eb9d`). The run: 05:07:56 to
05:09:50, pytest 113 s, `make down` after.

| Journey | Result | Duration | Failed step |
|---|---|---|---|
| S-005 `01-countly` | **red** | 35.5 s | *founder signs in with Google* |
| S-006 `05-paidly` | **red** | 34.3 s | *founder signs in with Google* |
| S-007 `07-mulchrun` | **red** | 33.6 s | *founder signs in with Google* |

**All three stopped at the first click, on a keel-web master defect, before any step this spec touches.** keel-web's
dev server draws its error overlay over every page: `[plugin:vite:css] [postcss] src/styles/app.css:11686:1: Unclosed
block` -- the phone `@media (max-width: 720px), (pointer: coarse) and (max-height: 520px) {` of spec 100 FR-2 has no
closing `}` before spec 096's `.lt-outside` rule. The brace count of `src/styles/app.css` is balanced at 100's
`d7ef75c` and off by one from 096's `d759a81` on (through `5b31372` and master `8b8eb9d`): the 096 commit, landed onto
100's media block, dropped its `}`. `<vite-error-overlay>` intercepts the click on *Continue with Google* for 30 s
(`runs/20261023T050804Z-s005-countly/screenshots/001-login.png` shows the overlay). This is keel-web's to fix (one
`}`); this repository was not changed to step round it (a disabled overlay would leave keel-web's whole stylesheet
unbuilt). As instructed, the run was not repeated: **the harness changes of FR-2 to FR-9 are unit-tested but were not
walked on a stack.**

Bundles: `runs/20261023T050804Z-s005-countly`, `runs/20261023T050840Z-s006-paidly`, `runs/20261023T050915Z-s007-mulchrun`
(git-ignored, in the worktree).

## Unit (`pytest tests -q`, what `make unit` runs; the main checkout's venv)

| | passed | failed | skipped |
|---|---|---|---|
| Before: master `a34fbf9` (+ the spec's amendment), this worktree | 2,872 | **41** | 169 |
| After: this branch, the last full run (after the last code change) | **3,068** | **3** | 53 |

Before: the 41 reds were 35 refusals of the canon at revision 13 by the r12 reader (the caller's "39" plus the two
`test_backtest` / `test_journey_through_a_host` readers the same refusal reached) and six ladder / THEMES pins moved by
keel-cloud 118 / 119. The skips fell from 169 to 53 because the canon-reading tests skip *by name* when the canon is not
at the reader's revision -- they all run now. +196 passed: those 116 un-skipped, 41 fixed, and the new tests (rule C's
twenty refusals and three chain entries, the bins, the 28-entry loader test, the chain on the wire, the outside person,
the read-back, the rungs, the remap, the clause, the second stems and the deciding line, the contract-28 Insights
faults, the partial-context THEMES resolve).

The three reds are each a **finding** (below, F-6 to F-8): un-skipped DRY compares against keel-cloud's own
`build/` records, which predate the builds -- they are not re-typed and cannot be re-cut without running keel-cloud's
`./gradlew test` in keel-cloud-docs (a write there):

- `test_instruction_brief_facts.py::test_keel_clouds_facts_agree_on_every_card_pilot_and_price_median_of_corpus_r12` --
  71 of 101.
- `test_report_marks.py::test_keel_clouds_facts_draw_the_corpus_overview_on_all_seven_entries` -- 15 of 49.
- `test_instruction_spoken.py::test_the_corpus_record_keeps_every_rule_and_nothing_is_known_apart` -- 102 of 109.

## Findings -- every golden number or string the builds moved (served / recorded beside expected)

No golden number was re-typed in any corpus-read file. Where the spec directs the eval's *reading* to follow a build
(FR-5a, FR-6a, FR-7, FR-8), the reading was moved and the number it now expects is listed here beside the old one, with
its source; none of these was observed on a stack (the run stopped at sign-in).

| # | Where | Expected before (golden / v20 reading) | Now (served, or the build's own record) | Source |
|---|---|---|---|---|
| F-1 | 05-paidly Commitment (`leg_standings`, the card) | HOLDING_UP, n 8, inside 6; `yes_start=3, yes_after_trying=3, probably_not=0, no=2`; card *6 of 8 · open to start a read-only trial* | expected on the stack: PEOPLE_DISAGREE (3 of 8: the three *yes, after trying it first* -- Mo Birch, Uma Elm, Yusuf Hazel -- have no served option and are sent as *probably not*) and the card *3 of 8 · would start a read-only trial* | keel-cloud 118 FR-1 (no smaller step on the founder's one-item list); FR-7 |
| F-2 | 01-countly Commitment | `yes_start=6, yes_after_trying=1, probably_not=0, no=1`, HOLDING_UP 7 of 8 | expected: `yes_after_trying=0, probably_not=1`, HOLDING_UP still (6 of 8 >= 2/3); card *6 of 8 · would install the app* (Daniel Achebe remapped) | as F-1 |
| F-3 | the pilot tile, every golden entry (`pilot_for`, the tile) | 01 *2 of 12* · 05 *2 of 20, PRIMARY 2 of 12* · 07 *2 of 19, PRIMARY 2 of 12* | 01 *2 of 10* (Not counted: 2 who did not have it.) · 05 *2 of 19, PRIMARY 2 of 11* · 07 *2 of 16, PRIMARY 2 of 9* | keel-cloud 123 FR-4 table; the eval's `pilot_for` follows the rule |
| F-4 | the Overview's decision line (`report_overview`) | *{How sure}. {reason}* then *{Dimension} is {status}; ...* | *{How sure}. {reason}* then `decision.change.sentence` (and `.also`): 01 *Not yet: Current solution split them, 5 of 8 say today's way falls short.* · 05 *Build, but change the cost you put on the problem: the middle cost was $58.33 a month against your $100 to $300 a month. Change the price too: 3 of 8 put it below your $60 to $100 a month.* · 07 *Not yet: Prevalence did not hold, 9 of 12 had it in the last 2 weeks against your nearly all. Importance split them too, 4 of 7 put it in their top two.* -- **keel-web 098 (which draws it) is not on master**, so the page still draws the semicolon list: a red expected on `report_overview` until 098 merges | keel-cloud 122 FR-3 table |
| F-5 | the context card's read-back (`leg_context`) | the corpus's `understood` (01 *Independent restaurant managers, when a delivery does not match its invoice, trying to keep ...*) | code's sentence over the scripted slots: 01 *Independent restaurant managers in the US, who run one or two sites, when a delivery does not match its invoice, keep the stock records matching what is on the shelves, counting the last 4 weeks.* (122's table reads *..., one or two sites, ...* -- this spec scripts the condition, judgement call 2); 05 *Freelance translators in the US, who work mostly for agencies, when ...*; 07 equal to 122's table | keel-cloud 122 FR-1, 120 FR-2 |
| F-6 | `brief_facts` DRY (MARKS v20 *101 of 101*) | 101 of 101 against `build/brief-facts/*.json` | **71 of 101**: keel-cloud's record (written 2026-10-22 16:54) still has the pre-116-123 words (e.g. 05-paidly *Purchase friction 5 of 8 · did not need the agency owner's approval, or it was quick*, *Commitment 6 of 8 · open to start a read-only trial*, pilot *finished 20, PRIMARY 12*) while the eval's reading follows 116-123 (*3 of 8 · needed the agency owner's approval, and it took a long time* with the fear's bar; *3 of 8 · would start a read-only trial · 3 more after trying it first*; *PRIMARY 11*). The record predates the builds: re-cut it with keel-cloud's `BriefFactsCorpusTest` and re-measure | the cloud's record; FR-10 |
| F-7 | `report_overview` DRY (v20 *49 of 49*) | 49 of 49 | **15 of 49** on the same stale record (the hero's change line and the moved cards) | as F-6 |
| F-8 | `spoken_form` on keel-cloud's spoken record (v20 *109 of 109*) | 109 of 109 | **102 of 109**: on all seven golden entries the old (r12) cost item's escape reads *I don't know* while its spoken line says *Or say you can't recall.* -- the registry's chain escape label (decision 24) on spec 077's cost total, in `build/spoken-corpus.txt` (2026-10-22 16:54). Whether the stack serves the same mix was not observed (the run stopped at sign-in) | keel-cloud 115's registry; the cloud's record |
| F-9 | every card's Prevalence line (a journey) | *had it in the last 4 weeks* | *had to recount stock by hand after a mismatched delivery in the last 4 weeks* (01; the founder's scripted clause) | keel-cloud 116 FR-3; FR-4a |
| F-10 | Current solution's Keel bar | *holds if at least 2 in 3 say today's way falls short (answers 3 to 5)* | 01 *holds if at least 2 in 3 land below 'A quick recount put it right'*; 05 *... 'Paid a little late, no chasing'*; 07 *... 'A short wait at the yard'* | keel-cloud 117 table |
| F-11 | Purchase friction's card (05, 07) | 05 *5 of 8 · did not need the agency owner's approval, or it was quick*; 07 *4 of 7 ...* | 05 *3 of 8 · needed the agency owner's approval, and it took a long time* (bar *holds if at least 2 in 3 say it was needed last time and took a long time*); 07 *3 of 7 · needed ...*; statuses unchanged (PEOPLE_DISAGREE, a split of the fear) | keel-cloud 118 FR-3 |
| F-12 | Adoption friction's card | 01 *7 of 8 · would ...*; 05 *7 of 9*; 07 *6 of 7* | 01 *6 of 8 · would ... · 1 more if it was clearly worth it*; 05 *6 of 9 · ... · 1 more ...*; 07 *5 of 7 · ... · 1 more ...* | keel-cloud 118 FR-2 |
| F-13 | S-014's green project (not run here) | nobody owed a follow-up | every decision-maker is owed one on Purchase friction (*quick* is against the fear, *a long time* its second stem: keel-cloud 118 judgement call 9) -- `test_the_healthy_answers_are_against_on_no_rung` now excludes that rung, by name | keel-cloud 118 |
| F-14 | keel-web master `8b8eb9d` | the stack serves the app | `src/styles/app.css:11686` unclosed `@media` block since keel-web 096 `d759a81`; every journey stops at sign-in | keel-web, not this repository |

## Judgement calls

1. **The corpus's r12 cost is written on the wire before its screen.** keel-web 094 draws the chain's cost step on a
   fresh project (094 judgement call 1: only a *stored* cost from before the chain gets spec 074's controls), and the
   chain step needs a unit and a way -- so no golden cost (AMOUNT / HOURS, no unit) can be typed there without becoming
   a chain cost, which would move every golden commercial number (keel-cloud keeps spec 077's cost total and 073's
   ladder only for an old-shape cost). `_old_cost_on_the_wire` PUTs the entry's own cost, reloads, asserts spec 074's
   controls are drawn, and the founder answers them as before (the `_hourly_rate` precedent). A chain answer is typed
   on the chain's screens.
2. **The segment's condition is scripted; the occasion stem is not.** FR-4 / 4b ask the condition per golden entry
   (120's table; 01-05 gain a chip, answered inside by every golden person). 120 lets 064 keep the plain occasion; a stem
   would move every golden Importance, Current solution, Compatibility and Relative advantage question and the story
   prompt for no FR, so the noun stays. The item-stem join is built (FR-4c) and reads nothing on the golden journeys.
   Consequence: the read-backs of 01-05 are 122's sentence with the condition after *, who* (F-5), not 122's table
   (which was computed with today's script); 06 and 07 equal the table.
3. **`window.proposed` is scripted null** on every golden entry (02's *quarter closes* proposal equals its own window
   and would only draw the *From* line; 02 is not walked by S-005/6/7).
4. **One follow-up line a rung** (the first of each spec 051 rung's three; Purchase friction gains *Finance wanted
   written quotes before anyone signed.*). Since 118 the rung a person is asked on depends on the deciding lines of
   the standings *at that moment*, and since 119 a THEMES job starts at the end of every reading batch over the answers
   so far -- while keel-runtime 0.8.0's scripted executor resolves a scripted theme's texts verbatim and refuses one the
   job's context does not carry. With one line a rung, any partial context on a dimension resolves to that line's one
   theme, whoever was asked there. The person types the line of the rung the route actually asks (`follow_up_line`), the
   skippers still skip, a back-test person types their own words. FR-9's *pooled follow-up lines stay fixed* is read as
   the back-test's (where each person's own `follow_up` wins) -- the golden pool's shape moved.
5. **The deciding lines are read off the served standings** before each walk (`deciding_lines`: each called stage's
   first dimension whose status is the verdict), never recounted by the eval.
6. **Moved golden numbers are deferred, not fatal at once.** `leg_standings`' standings and verdicts and `leg_report`'s
   cards, broke and pilot record their mismatches on their step and the journey goes on (`Journey.deferred`), failing
   at the end with every one -- so one run names every moved number (F-1 ...). Every other assertion fails where it is.
7. **Commitment's corpus *yes, after trying it first* goes on *probably not*** where no conditional option is served
   (every golden entry), and back on the conditional option where one is (a back-test project on Keel's AI) -- FR-7's
   rule; each remap is a finding (F-1, F-2).
8. **The decider's title is the role word** on every B2B entry: no golden or back-test entry carries
   `persona.decision_maker.title` (FR-6 expected the six back-test entries and 10-fixture-b2b to; none does, and the
   fixture is left unedited beyond its revision line).
9. **`currency` is posted** on a chain cost and price (FR-2: *every field the entry carries*; the contract takes it).
10. **The chain ladder follows the r13 checker** (points to a million; *an amount 0.01 to under 1,000,000*), not 122
    T017's ladder to 100,000,000 -- the same codes for every founder's low under 250,000, every entry's (FR-1a: rule C
    as built).
11. **An off-chain cost row under keel-cloud's registry** reads spec 077's `cost_total` / `cant_recall` -- the registry's
    own guidance says so; the eval's registry slice already did.
12. **One answer is its own group** in the Insights prediction (`ON_THEIR_OWN`, no THEMES job: 119 judgement call 4),
    and every quote -- `quotes`, the themes', `rawQuotes` -- must be a named person's own follow-up.
13. **The overview reads `decision.change` and deletes the semicolon join** (FR-8c), so `report_overview` is expected red
    against keel-web master until 098 draws the change (F-4). The corpus reading carries 122's seven change sentences
    (`DECISION_CHANGE`) for the DRY compare.
14. **The three stale-record DRY tests are left red**, each named (F-6 to F-8): un-skipped by revision 13, they compare
    the eval's reading with keel-cloud `build/` files written before 116-123 (2026-10-22 16:54); re-cutting them is a
    keel-cloud test run (a write in keel-cloud-docs), not this repository's.
15. **`sampling`** needs no code: the scripted executor matches the context's key set; nothing reads the payload's
    other keys.
16. **Commits group FRs where one file carries several** (`vectors_script.py` holds FR-2 to FR-7's script, the journey
    `corpus_scenario.py` FR-2 to FR-8's holds): seven commits, FR-1, FR-2-6 (script and screens), FR-7, FR-8, the
    journey, FR-9, FR-10, and this file.
17. **The marks' versions are not moved** (FR-10): `report_insights` reads contract 28's fields (its rule moved with
    119 / 095) and `brief_facts` / `report_overview` / `spoken_form` read numbers the builds moved (F-3, F-4, F-6 to
    F-12) -- named in the Spec 064 paragraph of `instructions/marks.py` for the operator, `MARKS_VERSION` 20.
18. **Commit trailer**: the hand-off named *Claude Fable 5.1*; the build was run by Claude Opus 5.5.

## Not done / open

- **The eval run measured none of this build** (F-14): S-005/6/7 stopped at sign-in on keel-web master's broken
  stylesheet; not repeated (one run, as instructed). After keel-web's one-brace fix (and 098, for F-4), `make eval
  K="s005 or s006 or s007"` is the next step; expect F-1 / F-2 / F-4 on S-005 and S-006 and the context, chip, chain-free
  golden walk otherwise.
- keel-web 098 (market OTHER, `decision.change` drawn, 117's / 118's screens) and 100's attribution band were not on
  keel-web's master; their specs were followed where the eval reads them (the change sentence, `GET /v2/markets`,
  `market.kind`), and no *Another country* step is driven (098's selectors do not exist yet).
- `make backtest ENTRY=08-fresco` -- the operator's (money, a key). The chain screens (FR-2), the value box and the plan
  screen (FR-3) and the outside person are unit-tested on the script side only; their page objects have not met a page.
- The three stale-record DRY tests (F-6 to F-8) wait on a keel-cloud `./gradlew test` re-cut of `build/`.
- Nothing pushed, merged or rebased; spec.md untouched.
