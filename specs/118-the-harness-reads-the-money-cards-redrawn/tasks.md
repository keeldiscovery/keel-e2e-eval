# Tasks 118 -- The harness reads the cards redrawn and the question screens (keel-cloud 180-185, keel-web 155-156)

Branch `118-the-harness-reads-the-money-cards-redrawn` (worktree `wt/keel-e2e-eval-118`, `.git` a file, its own `make
venv`), off master `82fae86` (the spec and its FR-4b / FR-4c / FR-4d amendments). Built by Claude on 2026-10-31. Read
only: keel-cloud-docs master `f3f0d99e` (contract 55, corpus revision 21; 180-185's tasks.md, *Served words that changed*
and *owed to keel-e2e-eval 118*; `CommercialChain`, `PersonaModel`, `PurchaseFriction`, `BriefFacts`, `IdeaLines`,
`ItemFrames.conditionKind`, `VectorCorpusFixture`, `BacktestCorpusTest`, `CorpusRevisionTwentyTest`,
`CorpusRevisionTwentyOneTest`, the registry of record, `canon/openapi-v2.yaml`), keel-web master `3c0db0c` (155's and
156's tasks.md, *The test ids keel-e2e-eval 118 moves to*; `translate.ts`, `ListQuestion.tsx`, `SendMorePopup.tsx`,
`DimensionStagePage.tsx`, `InsightsView.tsx`, `AnswerChart.tsx`). **The build records of record are keel-cloud-docs
`build/` on `f3f0d99e`** (the marker `build/.records-f3f0d99e`, 22:43 ET): `spoken-corpus.txt` and `brief-facts/` read
by the unit (no fallback to the corpus files was needed; every pin below was checked against them). **No stack, no
model, no walk, no paid call, no key read.** Nothing merged into master; the branch pushed after every commit, never
force-pushed.

**Corpus revision 21, not 20.** The spec says *revision 20*; keel-cloud 182 took the corpus to 20 and 185 to 21 (185's
tasks.md, *not foreseen* 1). Read 21 everywhere the spec says 20; revisions 19 and 20 are refused by name, as 18's was.

| Commit | What |
|---|---|
| `346d451` | FR-2: corpus revision 21 -- the reader, rule C in 180/181's words, Ability to pay at the price, Purchase friction's six, a fact's three, `screeners.decider`; the registry's `duration_bands` / `duration_band`; the three fixtures at 21; D19 kept as the record; the marks header's r21 digests |
| `4210263` | FR-1: `instructions/brief_facts.py` in 180's and 182's words; 117's `retense_179` tolerance removed; the split note gone (keel-web 155) |
| `78fc657` | FR-3: the spoken guard -- a fact's three, *Yes, most of the time*, `condition_kind`, Price's step one *or more* (S8) and its second step (S11) |
| `bd35d4b` | FR-2 / FR-4c / FR-4d: the walk -- the founder's time on Choose, the loss line's box, no hourly rate; `askedAfter`; Price and the plan in two steps on the AI link; the idea card; the writer's decider clause; 156's screens and *Read and tap*; the ladder at 182 / 183; Current solution's two boxes; one line per follow-up |
| `2ae4f8c` | FR-4 / FR-5 / FR-4c(a): the after-answers leg reads keel-web 155's ids; the readers' screens name the strip and the lines; the reader's `{{screen}}` says every served spoken line |
| `d2d99ee` | FR-6: `tests/test_money_cards_redrawn_118.py` (37); runs/DRIFT.md #102 |
| `3ae88f6` | FR-6: spec 115's registry tests run again (their 174 marker, gone since 182, skipped 15) and re-pinned |
| the docs commit | this file and `AGENTS.md`'s spec-118 paragraph |

## Unit (the gate)

| | passed | failed | errors | skipped |
|---|---|---|---|---|
| master `82fae86` (= the branch's base: spec text only past 117's code) against keel-cloud-docs `f3f0d99e` with its fresh records and keel-web `3c0db0c`, run in the worktree before any edit (22:44-22:47 ET) | 4,345 | 193 | 59 | 255 |
| **branch at `3ae88f6` (the last code; the docs commit adds none), the same siblings** | **4,838** | **0** | **0** | **53** |

Master's 193 + 59 are the corpus at revision 21 (`revision is 21; this eval reads revision 19 only`, 254 of them), the
registry refusing `duration_bands` / `duration_band` (which skips the 255), keel-web 156's words and 155's deleted split
note, and one stale pin (`test_quality_081`, TABLE.md rebuilt at RUBRIC_VERSION 3 by cycle 4). The last recorded master
count (117's tasks.md, 4,755 / 0 / 0 / 53) was against keel-cloud-docs `2f147fe7` and keel-web `7243de7`, so master was
run once here against the current siblings (in this worktree at its base, before any edit -- never in the main checkout).
`make unit` on the branch at `3ae88f6`: 23:50:03-23:53:57 ET, exit 0 (234 s); its 53 skips are master's 117-era 53, all
*the corpus is past revision 2* (S-001's r2 readers). A run at `d2d99ee` (23:37:38-23:41:31 ET, 4,824 / 0 / 0 / 68) showed
15 more skips: spec 115's registry tests keyed on 174's *can slow or stop the purchase*, which 182 removed from the
registry -- they skipped by name, silently. `3ae88f6` keys them on 174's decider template instead and re-pins what they
then found (T029). Net against master's run: its 193 failed, 59 errors and 202 extra skips (the registry it refused) now
pass, with the 37 new tests and the re-enabled 15.

## FR-1 -- the mirrors (keel-cloud 180, 181, 182; `instructions/brief_facts.py`) -- `4210263`

- [x] T001 **The cards** (`BriefFacts.card` at `f3f0d99e`): Adoption friction and Commitment count every yes, the
  conditional ones beside it -- *· 2 of them if it was clearly worth it* (184's plain option, `ONLY_IF_WORDS`), *· 4 of
  them after {smaller step} first*, *on a condition* where the list names no smaller step (`ON_A_CONDITION`, 180 FR-7) --
  the number every yes (it read *· k more*, the plain yes alone). Purchase friction counts those against (`n` less the
  FOR side, `friction_against`) and says *expect {step} to take longer than {duration}* on a timed list, *said {step}
  would take a long time* on a list with no time; its bar `keel_bar` -- `friction.BAR` / `BAR_UNDATED`. The fear's words
  (*Yes, {step} would slow it. Plan for it.*, *Your fear was ... Not the blocker you expected.*) and its *Holding up* on
  an amber are gone; `friction_words` is Adoption friction's alone. `VERDICT_WORDS["NOT_REACHED"]` = *Not reached* (181).
  `bar_words` reads a served `statusWord` first (180 FR-8). 06-repeatline's decision change *only 4 of 7 would
  introduce us ..., and 3 did not* (the yes after a short call counts).
- [x] T002 **The DRY compare** against `build/brief-facts/` of record: **101 of 101** (87 cards, 7 pilots, 7 price
  medians); the only reported differences are the insight halves of `statusWords` (184's bounded insights, reported never
  marked). `cloud_facts_at_104`'s 117 tolerance (`retense_179`, `TENSE_179`) is removed; a build before 182 skips by name
  (`_at_182`), never re-worded.
- [x] T003 Unchanged, read and confirmed: `NOT_ASKED_WHY` (*it is derived from what they lose today and your price, so it
  was not asked*, `BriefFacts.DERIVED_WHY`) and `DERIVED_ABILITY_LINE` -- 181 FR-4 moved the belief, not these.
- [x] T004 The chain's beliefs (180 FR-2, 181 FR-4) are rule C's in the corpus reader (FR-2 below), never the brief's.

## FR-2 -- the two new items and corpus revision 21 -- `346d451`, `bd35d4b`

- [x] T005 **The reader** (`instructions/corpus.py`): `REVISION = 21`, `_REVISION_OF` 19 and 20; rule C's beliefs by
  ports of 180 / 181 (`chain.cost_belief(cost, occasion, role_word, deciders, b2b)`, `price_belief(..., deciders, name,
  b2b)`, `ability_belief(derived, ..., price, cost, ..., deciders, b2b)`, `ability_phrase`, `deciders`, `plural_words`,
  `plural_of`), the deciders the decider's `title` (else `role`) in the plural, the phrase the role's (Fresco's sentence
  *Contractor operations leads*, its phrase *contractors* -- `CommercialChain.phrase`). Every chain entry's recorded
  words agree with the port.
- [x] T006 **Ability to pay** (181): on a chain study with a price the row's question is `chain.POINTS_BACK` and its
  escape `cant_say` (`CommercialChain.side`; the registry still names `cant_recall_one`); a pick from a person whose Price
  answer is not at or above the founder's price is refused (`chain.reached`, a port of `Compare.reach`: each step against
  its own low). Fresco keeps Gordon Achebe, Palus Maya Feldman, Expanse Gregory Lindqvist, Nadia Kowalski, Arjun Mehta and
  Marco Bianchi, AirCaps Shirin Tehrani.
- [x] T007 **Purchase friction** (182): `instructions/friction.py` ports `PurchaseFriction` -- `Duration`, `bands` (182's
  table, pinned row for row), `codes`, `labels`, `within`, `longer`, `belief`, `BAR`, `BAR_UNDATED`; the row on a timed
  list is `duration_bands` over the six around the founder's time (escape `cant_tell`), on a list with no time the fixed
  three (`UNDATED_FRICTION_ROW`, the recorded `cant_recall` read as `cant_tell` by 115's one rule). `Entry.duration()`.
- [x] T008 **Compatibility** (185): a fact's row is the three codes (`FACT_CODES`), held to `spoken.condition_kind` (a
  port of `ItemFrames.conditionKind`: a permission on either face, else a fact, else an ability -- it agrees with the
  cloud on all 35 entries); the four on a fact is refused. `Entry.screeners` and `decider_question()`.
- [x] T009 **The registry**: `RESPONDENT_CONTROLS` gains `duration_bands`, `COMPARE_RULES` `duration_band` (182's name
  for `caution_turned`, still read on a registry before 182 -- the eval's fixture slice).
- [x] T010 **The walk answers the two items.** Ability to pay: the corpus already deleted the picks of everyone the
  interview never asks, so the scripted response sends none; the text walk and the AI walk skip an item served
  `askedAfter` unless the person's Price answer sends exactly one entry's `optionIds`, and hold the pointed-back
  question drawn (`vs.asked_after`, `asked_items`; the AI walk maps each pointed-back question to the item). Purchase
  friction: the corpus picks are the band codes and ride on the wire as they are; the founder's time is typed on Choose
  (`list_choose(..., duration=)`: `duration-count`, `duration-unit`) and sent on the save (`saved_list` / the scripted
  `calibration_answers` carry `duration`; `vs_screens.sent_duration` reads it off the PUT). On the AI link the six are
  answered by saying the band whole (keel-web 156 T014: one rung's whole words are that rung; 182 serves no second-step
  lines for them).
- [x] T011 **The back-test yaml**: 182 FR-7 recorded the duration beside the step (`answer.duration`); nothing to write
  here (the corpus is keel-cloud's).
- [x] T012 **D20 and D21** (`tests/test_money_cards_redrawn_118.py`): the revision-19 record beside the revision-20 one
  (35 entries: the five belief fields, Ability to pay's row and 146 deleted picks plus one chip, the three timed entries'
  time, row and picks by 182's one rule; no `expected` moved), and the revision-20 record beside canon (the revision line,
  13 fact rows, 13 picks `only_with_help` -> `no`, the golden rows' counts on Lullaby and Mulchrun, three
  `screeners.decider`; nothing else). D19 (`tests/test_corpus_r19.py`) is mirror against mirror now (`corpus-r18/` beside
  `corpus-r19/`), and `check_corpus_r19.py` runs over the revision-19 records -- r19's tests retired as r18's did.

## FR-3 -- the spoken guard (`instructions/spoken.py`) -- `78fc657`

- [x] T013 `FACT_ANSWERS` the fact's three (174's four kept as `FACT_ANSWERS_174` for a stored item), `ABILITY_ANSWERS`
  *Yes, most of the time* (123's *mostly* as `ABILITY_ANSWERS_123`); `served_labels` knows both.
- [x] T014 S8: Price's step one ends *{top} or more* (`_first_step`; a ladder recorded before 185 keeps *Over*). **S11**
  (new): on a Price item in two steps the record carries both second-step lines, each one question of at most 20 words,
  one *, or*, no escape; on money the side's two bands said whole (`second_step`). `ComposedItem.under` / `over` parsed
  off `spoken-corpus.txt`; `bt.spoken_guard` reads them off the wire.
- [x] T015 **On the regenerated record**: no S1-S11 fault on any of the 74 items (Compatibility's three, Price's two
  steps, the ability's four); the five Adoption friction `K2` faces spec 112 named are unchanged.

## FR-4 -- the after-answers leg (`evals/backtest.py`) -- `2ae4f8c`

- [x] T016 `STAGE_JS` reads `stage-tally`; `CARD_JS` reads `bar-strip` (every one: `data-mode`, `data-counted`,
  `data-bar`, `bar-strip-label`, `-marker`, `-axis`, the cells by `data-side` and `data-kind`), `dimension-asked`,
  `-rule`, `-count-line`, `-so`, `li.dimbar[data-side]` with its side word and `data-founder-band`, `price-part` (each
  with its own strip), the marks (`founder-range`, `most-often`, `chart-caption`, `problem-you-named`,
  `current-solution-line`, `benefit-limit`, `strip-unit`, `strip-median`, `ability-values`), and the people by
  `data-side` with `dimension-person-why` / `-band`; `strip_drawn` says whether a strip was drawn. `INSIGHTS_JS` reads each
  box's `insights-status-line`, `-belief`, `-count-line`, `-also`. `dimension-verdict` is the served `statusWord`.
- [x] T017 The journey's own holds: `bar_words` reads the served word; the money page's said line falls back to the rule
  line where keel-web draws none (155 T006: Ability to pay's `founderSaid` is its rule line), the bars read by side
  (AGAINST muted).

## FR-4b -- the problem and solution cards (keel-cloud 184) -- `bd35d4b`, `4210263`

- [x] T018 The rung headings (`fake.RUNG_HEADINGS`, the registry's: *What made the others more pressing?* ... *What would
  take the time?*), `ALSO_HEADINGS` (`alsoHeading`), the Adoption friction conditional yes's plain words and follow-up
  (*What would make {name} clearly worth it to you?*, the registry's own stem), *you* on a loss (`vs.LOSER`, every miss
  rung), the brief's bounded insights (reported, never marked), the leg's Prevalence strip and Current solution line (T016).
- [x] T019 Adoption friction's and Compatibility's corpus answers follow revision 21's option labels: no entry stores a
  drafted condition (184 T029), and the fact rows are T008's.

## FR-4c -- the question screens (keel-cloud 185, keel-web 156) -- `bd35d4b`, `2ae4f8c`

- [x] T020 (a) **The reader sees the spoken form**: `readers._spoken` says every served line -- anchor, stem, count line,
  options line, escape line -- and on a ladder in two steps the second step's two lines; the plan's own spoken form is
  added; the screener reads its served spoken form where the bundle records one. The guidelines pasted for R6 gain §16
  and §17 where the guidelines read carry them (`GUIDELINE_AMENDMENTS`); criteria unchanged.
- [x] T021 (b) **Price in two steps** on the AI link (`_Walk.price_in_two_steps`, `ladder`): a band on a side is said as
  step one's phrase (`vs.step_one`: *Under $800*, *$2,500 or more*), held, the second step awaited
  (`Player.wait_ask`, `ai-sheet[data-ask=under|over]`; `Player.sheet` records `ask` and the `data-greyed` rows), then the
  band itself; the middle band and *I wouldn't pay* at once; a lock before 185 in one ask. The plan the same, read on the
  page (`plan`, `planUnder` / `planOver`). The corpus's Price answers are one of the six either way (185 T025).
- [x] T022 (c) **Compatibility's three on a fact**: T008, T013.
- [x] T023 (d) **The idea card**: `vs.idea_card(name, what)` -- *Imagine {name}, {what it is}.*, the name once where it is
  the plain words (`what_it_is` = `IdeaLines.whatIs`); the walk types the project name in *The name* (`#idea-what`, test id
  `idea-name`) as before and accepts Keel's suggestion in *What it is* (`idea-what-it-is`, read into `lines["whatItIs"]`);
  the journey holds the served card to the name and `IdeaView.whatItIs`.
- [x] T024 (e) **The screener**: `vs.decider_condition` serves the writer's clause (`decider_screener`, the entry's
  `screeners.decider`), else part 1's shape said to the decision-maker (`chip_from`); `respondent_result` scripts
  `decider_condition` beside the chip on a B2B study that records one; `decider_chip` (*you decide for*) is kept as the
  record of a lock before 185 and read by nothing. Never *you decide for* on any golden entry.
- [x] T025 (f) **The interviewer screens** (156 FR-1 / FR-2): `INTERVIEWER_IS`, `before_interviewer_title` (any length,
  `{actor_plural}`), `before_interviewer_sub`, `face_hear_line`, `BEFORE_SEND_LATER`, `send_format_title`,
  `send_ai_claim`, `READ_AND_TAP_LINE`, `FORMAT_STATUS_RECORDING` / `READY` / `format_status_when_ready`, the status line
  read per row (`formats_now`: `status`, `format`, the heading `send-format-title`); L1 reads `face-hear-line` and
  `send-later`; *Read and tap* everywhere the harness reads the format (`iv.READ_AND_TAP`, `FORMAT_NAMES["TEXT"]`, the
  Format column, `SEND_TEXT_ONLY_LINKS` *Send read-and-tap links*, `browser.choice_write_label`, the founder's
  `send-format` answer). The S1 / S3 holds read the status lines (the foot sentences are no longer drawn).

## FR-4d -- one scripted line per follow-up -- `bd35d4b`

- [x] T026 `vs_screens.distinct_follow_up` (the page object) and `cs.follow_up_lines_owed` (the hold's expectation): a
  line this person already typed on an earlier follow-up of the interview is never typed again -- the second follow-up
  is skipped. The entry carries one why a person (`follow_up`, a string on 297 people, none on 369), so a second
  follow-up has no line of its own. Tested over every back-test person.

## FR-5 -- the quality readers -- `2ae4f8c`

- [x] T027 `readers._after_body` names the tally, the rule line, each strip (its label, cells by side, the marker), the
  price parts, the marks, the count line, the So line, each person's side and why, and each Insights box's status line,
  belief, count line and second group. `founder.md`'s `after` and `after-insights` say what an opened card and a box
  hold, in order. `respondent.md` says the screen carries every spoken line and the amendments. No criterion moved.

## FR-6 -- tests -- `d2d99ee`

- [x] T028 `tests/test_money_cards_redrawn_118.py` (37): D20, D21, the kept Ability to pay picks and a refused one; every
  canon entry at 21 and 19 / 20 refused; a fact's three and four on a fact refused; the chain's beliefs and `reached`;
  182's ladder (8 rows); the timed rows, sides, belief and the save's duration (no rate on the wire); the follow-up on the
  lock's rule; the brief card on a timed list; `askedAfter` skip and question; no Ability to pay answer from a person not
  reached; Price in two steps; S8 / S11 and the record of record; the reader's spoken screen; the question and
  interviewer screens; Current solution's two boxes; one line per follow-up; fewest first; Compatibility's second stem
  only where it names its steps; the leg's reader on a fixture page with and without `bar-strip`; the founder steps.
- [x] T029 Re-pinned with why (each asserted the old words): `test_corpus_r11_shape`, `test_corpus_r19` (D19 mirror
  against mirror, the r14 Transload probe on today's file), `test_instruction_corpus_r11` (the revision table),
  `test_instruction_marks` (the r21 digests), `test_seven_templates_115` (the friction rule retired, the fact's three),
  `test_instruction_brief_facts`, `test_report_marks` (headings, lead lines, the split note, the healthy pick),
  `test_mirror_follows_117` (the Choose bar now differs from the brief's: DRIFT #102), `test_instruction_spoken`,
  `test_lock_frontier_110` (*you* on a loss; the served second step), `test_follow_up_ladder`, `test_follow_ups_075`,
  `test_founder_walk_076`, `test_drawn_screener_seams_077`, `test_revision_16_walk`, `test_screens_as_drawn_090`,
  `test_interviewer_screens`, `test_backtest_scope_082` (the double draws `chain-loss`), `test_choose_by_label_104`,
  `test_phrase_is_the_peoples_093` (`LADDER_SHA`), `test_recorded_path_074` / `test_study_scopes` (revision 21),
  `test_quality_081` (TABLE.md at version 3, stale on master), `test_seven_templates_115` (re-enabled: the timed entries'
  `cant_tell`, 182's template and option rule beside the slice's 174 ones, ItemFrames' `FACT_THREE`); the eval's own fixtures `09-fixture`, `10-fixture-b2b`,
  `99-broken` at 21 (their tested conditions are facts: the row's three, one pick `only_with_help` -> `no`) and the
  compare fixtures' counts.
- [x] T030 `tests/fixtures/sample/s006-reads.json` **not edited**; no test pins a word 180-185 moved in it (117's
  *was quick* test still passes). **Owed: re-record it** (`make sample`, the coordinator's).

## Every mirror that moved, by its source

| Source | Mirror | Was | Now |
|---|---|---|---|
| keel-cloud 180 FR-2 | `chain.cost_belief` | *The problem already costs the payer ...* | *{Deciders} already spend ... on {base}.* / *already lose about ...* |
| keel-cloud 180 FR-2 | `chain.price_belief` | *The payer would think it worth ...* | *{Deciders} would think {name} worth ...* / *a fee of ... fair for {name}* |
| keel-cloud 181 FR-4 | `chain.ability_belief` / `ability_phrase` | *Your price is read against ...* | one sentence per reading over those who would pay the price |
| keel-cloud 181 FR-2 | the Ability to pay row | the registry's question, `cant_recall_one` | `POINTS_BACK`, `cant_say`, asked after a Price at the price |
| keel-cloud 180 FR-1 / FR-7 | `brief_facts.card` Adoption friction / Commitment | *· k more ...*, the plain yes | every yes, *· k of them ...*, *on a condition* |
| keel-cloud 182 FR-3 / FR-4 | `KEEL_BAR`, the friction card | the fear's bar, *would need ..., and it would take a long time* | *holds if no more than 1 in 3 say it would take longer than you expect*; *expect {step} to take longer than {duration}* / *said {step} would take a long time* |
| keel-cloud 182 FR-3 | `bar_words`, `friction_words` | *Holding up* on a held fear; the fear's words | *Did not hold* past the bar; the status words |
| keel-cloud 181 FR-3 | `VERDICT_WORDS` | -- | *Not reached* |
| keel-cloud 180 FR-4 | `DECISION_CHANGE["06-repeatline"]` | *only 2 of 7 ..., and 5 did not* | *only 4 of 7 ..., and 3 did not* |
| keel-cloud 182 FR-2 | `instructions/friction.py` | -- | the six bands around the founder's time |
| keel-cloud 182 FR-5 | `fake.LADDER` / `ALSO` | the fear's rung (*What would slow down buying ...*), the long purchase's second stem | the lock's rule, *What would take the time in buying {solution_name}?*, no second stem |
| keel-cloud 183 FR-1 / T003 | `fake.fewest_first`, `ALSO[compatibility]` | the walk's order | the failing line with the fewest whys first; *What steps did it take?* on *Yes, with some steps* (not *most of the time*) |
| keel-cloud 180 T025 / 182 / 184 T032 | `fake.RUNG_HEADINGS`, `ALSO_HEADINGS` | *Why other things come first* ... *What did slow it down?* | the registry's questions |
| keel-cloud 184 FR-8b (c) | `vs.cost_question`'s miss rungs | *did your team miss* | *did you miss* (`LOSER`) |
| keel-cloud 184 FR-8b (a) | `vs.answer_text` (Current solution) | the phrase and the labels joined by *"; "* | two boxes, each its own sentence (`current_solution_boxes`) |
| keel-cloud 185 FR-1 | `spoken.FACT_ANSWERS`, `ABILITY_ANSWERS` | 174's fact four; *Yes, mostly* | *Yes · Yes, with some steps · No*; *Yes, most of the time* |
| keel-cloud 185 FR-3 | `spoken._first_step`, S11 | *Over {top}*; no second step | *{top} or more*; `under` / `over` held |
| keel-cloud 185 FR-2 | `vs.idea_card` | *Imagine {name}.* | *Imagine {name}, {what it is}.* |
| keel-cloud 185 FR-4 | `vs.decider_condition` | *Do the {people} you decide for ...?* | the writer's clause, else part 1's shape |
| keel-cloud 180 FR-9 / keel-web 155 FR-8 | the walk's hourly rate | `_hourly_rate`'s PUT, `cost.rate`, the rate box held | gone (never called; `rate` not posted) |
| keel-web 155 T014 | `fake.SPLIT_NOTE` in `expected_box` | the split note on an amber box | none |
| keel-web 155 T021 / T022 | `list_choose`, `_chain_cost` | -- | `duration-count` / `duration-unit`; `chain-loss` |
| keel-web 156 FR-1 | `vs_screens.l1_title` | the segment, *them* past ten words | `{actor_plural}`, any length |
| keel-web 156 FR-2 | `iv.TEXT_ONLY` / `FORMAT_NAMES`, `ivs.SEND_TEXT_ONLY_LINKS`, `SEND_FORMAT_RECORDING`, the Format column | *Text only*, *Text*, *Send text-only links*, *... Text only is ready now.* | *Read and tap*, *Send read-and-tap links*, *... Read and tap is ready now.* (not drawn); the status lines |

## The two new items' answering rules

- **Ability to pay** (181): asked only after a Price answer at or above the founder's price -- on the wire, the item's
  `askedAfter` entry whose `optionIds` equal the person's Price `optionIds`; that entry's `question` is drawn. Any other
  Price answer (a lower band, *I wouldn't pay*, the escape) skips it -- no screen, nothing said, no answer sent. The
  corpus (revision 20) carries a pick only for the people reached, so the scripted path sends exactly what the page does;
  the reader refuses a pick from anyone else.
- **Purchase friction** (182): one of the six band codes (or *It wouldn't be needed*, or the escape `cant_tell`), the
  entry's own pick sent as its code; on the AI link the band said whole. The founder's time is typed on Choose and sent
  as `SavedList.duration`; a list with no time keeps the fixed three.
- **Price on the AI link** (185): step one's side phrase, then the band at `data-ask=under|over`; the middle band and *I
  wouldn't pay* at once. **The plan** the same, read on the page (`plan`, `planUnder` / `planOver`).
- **Current solution's Answer** (184 FR-8b (a)): the what box *{the phrase, as a sentence}.* (*Getting the day into the
  log.*), the how box the outcomes it always named, each its own clause, one sentence (*Log done on site; Done in the
  trailer in under an hour.*) -- `founder_rungs` unchanged (2 or 3 on every golden entry).

## What the spec did not foresee

1. **Revision 21, not 20** (the coordinator's word, 185's *not foreseen* 1): read 21; 19 and 20 refused by name.
2. **The chain's beliefs needed the whole 180 / 181 composer**, not a mirror of a few strings: the deciders by
   `PersonaModel.pluralWords` of the decider's title (else role), the idea's name, no unit where the user pays, *each*
   closing its clause, the count base said once, the loss line dropped where it is the base, *Those* / *Of {them}, those*.
   Ported whole (`chain.py`); the phrase reads the decider's *role* in the plural, not the title (`CommercialChain.phrase`
   passes `deciderRole`) -- Fresco's phrase says *contractors* where its sentence says *Contractor operations leads*.
   Copied as the cloud writes it (the corpus records it so), noted for keel-cloud.
3. **The hourly rate is gone** (180 FR-9, keel-web 155 FR-8), which the spec does not name: the walk stopped setting it
   (`_hourly_rate` kept, never called; a PUT with the rate alone is 422 since contract 50), stopped posting `cost.rate`,
   and the rate box's holds read nothing on a stack at 180.
4. **keel-web's Purchase friction Choose bar still says spec 118's fear** (`HOLDS` in `translate.ts` at `3c0db0c`)
   while the cloud's brief and card say 182's time. Not a contradiction of what to mirror -- each mirror follows its own
   source (`vs_screens.PURCHASE_FRICTION_CHOOSE_BAR` the page's, `brief_facts.KEEL_BAR` the cloud's) -- but the founder
   sets one bar and reads another: filed as **runs/DRIFT.md #102** for keel-web; 117's test that held them equal now
   holds that they differ.
5. **The eval's own fixtures are facts** (09-fixture, 10-fixture-b2b, 99-broken: *was your phone ...*), so revision 21's
   rule moves them too: the row's three, one `only_with_help` pick `no`, the compare fixtures' counts `only_with_help=0,
   no=2` (both against: no status moved).
6. **Current solution's what box**: no entry records the founder's own description of today's way (tools, habits,
   workarounds); the box takes the list's phrase as a sentence of its own. An entry field for it is owed to keel-cloud's
   corpus (184 *owed*: "an entry field the eval keeps, from the sources" -- the eval keeps no entry data of its own).
7. **One why a person**: the corpus carries one follow-up text a person (297 of 666), so the second follow-up of
   spec 142 is skipped rather than answered -- the Insights boxes then never read one why twice. A why per rung is owed to
   the corpus if the founder wants the second answered.
8. **Keel-cloud 183's rule needs the run's state**: the walk reads the failing lines off the served standings and counts
   the whys typed so far (`_failing_now`, `_whys_now`) -- on the text walk. The AI walk's plan (S-005 / S-006's one or two
   AI people) is not given the run's counts: it follows the cloud's route as served and holds it as before.
9. **`MARKS_VERSION` 24 stands**: S8 reads step one as the record now serves it and S11 holds a shape the record already
   keeps (no fault at `f3f0d99e`), as spec 089 FR-3 and spec 115 read theirs; no mark scores a belief sentence or a
   pick's shape. AGENTS.md's rule (a moved *ruler*, not a moved record, earns a bump) is kept.
10. **The guidelines' amendments**: R6 was pasted §2, §3, §5 only, which do not say the second step; §16 and §17 are
    pasted after them where the guidelines carry them (a bundle's sha before 182 does not), so R6 reads the two steps
    against the rule that writes them.
11. **A stale pin on master**: `test_quality_081` asserted TABLE.md at RUBRIC_VERSION 2; cycle 4 rebuilt it at 3
    (`7d2026a`). Re-pinned.
12. **The registry of record lags in two places** (documentation, not served words): Compatibility's Lullaby example
    still shows the four for Lullaby's fact, and Ability to pay's `no_follow_up` still reads *it is read from the cost and
    the price ...* while the Insights footer serves *a number has no why worth a question*. Mirrored as the registry says
    (the tests hold the registry); owed to keel-cloud.
13. **The decision-maker's code question** (no clause written -- every golden B2B entry) is mirrored as part 1's
    `chip_from`; 184's one shape for an organisation's relative clause (*Does your ... run ...?*) is not ported -- no
    golden B2B condition has one.

## Owed elsewhere

- **The coordinator**: `tests/fixtures/sample/s006-reads.json` re-recorded (`make sample`); the acceptance back-test
  (`make backtest ENTRY=08-fresco SCOPE=COMMERCIAL`, paid, on the founder's word, inside cycle 5) -- the first walk of the
  new Choose time, the loss box, `askedAfter`, Price's two steps on the AI link, the leg's new reads.
- **keel-web**: DRIFT #102 (Purchase friction's Choose bar and intro in 182's words).
- **keel-cloud**: the registry's Lullaby Compatibility example (a fact's three) and Ability to pay's `no_follow_up`
  words; a corpus field for the founder's own words on today's way (Current solution's what box); a why per rung in the
  corpus if a second follow-up is to be answered; `Spoken.under` / `over` for `duration_bands` (keel-web 156 J-1).
