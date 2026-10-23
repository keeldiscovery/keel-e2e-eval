# Spec 064 -- The harness follows the fixed chain: corpus revision 13, the chain's screens, the new gate, the follow-up that names the blocker, insights with a state

After the back-test of 2026-10-22 the founder agreed ten fixes, built as keel-cloud 114–124 and keel-web 093–100. This
spec moves keel-e2e-eval to read that build so the six back-test ideas can be walked once more on it (the founder,
2026-10-22: *"after fixes, you would again run the same six once and see whether it has any issues, right?"* -- yes) and
the golden journeys keep measuring. **Scope: keel-e2e-eval only. Lands after keel-cloud 124 (corpus r13) and keel-web
094/095/096/097/098/099 are on their masters; read their `tasks.md` (selectors, judgement calls) before touching a
locator. No golden number is re-typed: a standing, count or verdict that moves under the new build is a finding for the
operator, named in tasks.md, never edited into a file. Build lean: `make unit` once; `make eval K="s005 or s006 or
s007"` once on a fresh local stack of the finished masters; one `make backtest ENTRY=08-fresco` the operator runs.**

## Rules

- **FR-1 Revision 13 (keel-cloud 124).** `instructions/corpus.py`: docstring opens on **Revision 13 only**; `REVISION =
  13`; `_REVISION_OF` gains `12: "MARKS_VERSION 20's corpus, before the commercial chain (keel-cloud 115: a cost with no
  unit, a price with no shape)"`; the refusal keeps its code. The loader accepts, where present, the chain's shapes of
  124 FR-1 (founder cost `measure/base/unit/lossPhrase`, modes MONEY | HOURS | RATE, the six periods with `each`; price
  `shape/shareBase/upfrontLow/upfrontHigh/thenNothing` with no `period`; `control: value_box`; value-box picks `{low,
  high}`, `{nothing}`, `{chip: dont_know | rather_not_say}`; a two-code price pick; the consumer budget codes) and
  refuses what 124's rule C refuses, in the same sentences; a cost with no unit and a price with no shape are read as
  r12. `price_ladder_codes(low)` learns the chain ladder (1-2-5 points, the founder's low as one edge; spec 115
  judgement call 6) beside spec 073's, chosen by the price's shape. Tests: `test_corpus_r11_shape.py` → revision 13
  (the seven at 13; an r12 file refused by name; a chain fixture entry accepted; each rule-C refusal); the back-test
  loader test loads the six chain entries. `tests/fixtures/corpus/09-fixture.yaml` / `10-fixture-b2b.yaml` move to
  `revision: 13` unchanged otherwise (GB on purpose, as 053 FR-4).
- **FR-1a What keel-cloud 124's build settled (added 2026-10-22).** The consumer budget codes are the engine's `from_spend |
  new_money | could_not` (escape `cant_say`); the readings are the engine's (`CommercialChain.reading`): Palus and Karsa
  `out_of_gain`, Fresco, Transload, Issen and AirCaps `budget`; the B2B budget item is still served on the decider's
  link on every reading (so the picks stay and are answered); AirCaps' `respondent_questions[commercial.price].codes` is
  one list of twelve (the one-off's six, then the plan's six) and its picks are `[<one-off>, <plan>]`; Issen's cost is
  8–16 hours a month (a chain price takes the cost's period); a value-box pick is `{low, high, currency, period}` in the
  founder's unit and period and is sent as is, never re-expressed; `dont_know` replaces `cant_recall` on the cost item.
  The loader's rule-C sentences and the back-test loader test follow `sim/check_corpus_r13.py` as built.
- **FR-2 The founder's chain screens (keel-web 094).** `harness/vectors_script.calibration_answers`: a chain cost posts
  every field the entry carries; a chain price posts `shape` and its numbers and no `period`. `Corridor.single`: on
  `cost_estimate` with a chain answer, the three chips (*Money they spend* / *Time it takes* / *A rate they lose*), the
  unit box, the period chip, the base box on RATE, the numbers, the rate box on HOURS/B2B, then the equation line read
  back (`seen["equation"]`); on `price_range` with a chain answer, the shape pill, the numbers per shape (the share's
  sub-choice; up front + plan; *then nothing*), and the locked words read back (`seen["locked"]`, held to the cost's
  unit and period). Old-shape answers drive the screens exactly as today. Selectors from 094's tasks.md *Selectors (for
  keel-e2e-eval 064)*; none invented. `_hourly_rate` runs only where the entry's cost is HOURS at a rate.
- **FR-3 The stranger's chain items (keel-web 094, keel-cloud 115).** `Pick` gains `interval {low, high}`, `budget`
  (the consumer budget code) and a two-code price; `Pick.as_wire` sends `interval` for a value box (one number as both),
  `optionIds` of two for `UPFRONT_THEN`, `chip` `NOTHING | DONT_KNOW | RATHER_NOT_SAY` as the item serves them
  (`valueBox.nothing` / `valueBox.chips`), and `asked_over` is not applied to an interval (the box is in the founder's
  period; the r13 pick already is). `Interview._answer`: the value box's two inputs, its chips, the plan's second screen,
  the budget single choice; the walker records `valueBox.label`, `whatYouGet`, the plan question and each band label as
  served in `screens`. `plan_keys` / `EvidencePlan`: FREE asks no price item; the budget item is asked on a same-person
  chain study whose cost and price share no base, in Ability to pay's place; part 3 goes to the decider as today.
- **FR-4 The gate (keel-cloud 116, 120; keel-web 096, 099).** `_gate` answers `gate.condition` first when served (the
  person's `in_segment` from the entry, default yes; `outsideSegment` people are thanked and recorded, never walked
  further) and records the chip question; the gate's question is no longer asserted to carry the circumstance -- the
  walker records it and `report_marks` reads *"had <clause> in the last <window>"* on the Prevalence card; the story
  chips include `RATHER_NOT_SAY` where served. A back-test `Person` may carry `in_segment: false` (loader, 124 FR-1's
  reading of the yaml, optional).
- **FR-4a What keel-cloud 116's build settled (no contract change; added 2026-10-23).** The gate is written by the part-1
  RESPONDENT_QUESTIONS job from the founder's Prevalence clause (job context key `problem`), framed by code as *did
  {clause}* when the clause starts with "you"/"your", else *did you {clause}*; `storyPrompt` keeps the circumstance.
  With today's script (`vectors_script.py` founder clause *had a time when {circumstance}*, gate `GATE_EVENTS` / *have a
  time when {circumstance}*) no golden gate text moves. This spec scripts a problem-led founder Prevalence clause per
  golden entry (keel-cloud `specs/116-gate-asks-the-problem/tasks.md` lists a proposed one per entry, each ≤ 20 words
  framed with no time words -- e.g. 01-countly *"did you have to recount stock by hand after a mismatched delivery?"*)
  and reads the served gate against it; the Prevalence card's brief line is `<clause> in <window>`. No golden number
  reads the gate's words, so MARKS_VERSION stays unless a mark pins the old gate text (then FR-10 applies).
- **FR-4b What keel-cloud 120's build settled (contract 30, response contract 21, document version 28; added
  2026-10-23).** The context card serves `occasion {noun, stem, rhythm}`, `segment {core, condition}` and `window.proposed
  {count, unit, from} | null`; the stem is served as its own opening sentence before Importance, Current solution,
  Compatibility and Relative advantage (the walker records it; the eval's 20-word framing check reads the question
  alone); the gate serves `condition {question, inCodes}` and `noLabel` ("I didn't get to") when they apply; a person
  outside posts `{"outsideSegment": true, "answers": []}` and is final; `StandingsView.outsideSegment` is always present;
  rhythm is code's from the window; the new rules X4–X7 and E5 are notes. For the golden entries: with today's script
  nothing moves; once this spec scripts a condition per entry, FIVE golden gates gain a chip (01, 02, 03, 04, 05 per
  keel-cloud `specs/120-…/tasks.md`'s table) -- the harness answers the chip inside for every golden person (no number
  moves) and records the chip question; the Sent register's per-kind count still includes outside people while the
  People page's aim leaves them out (120 judgement call 10).
- **FR-5 The founder's lists (keel-cloud 117, 121; keel-web 097).** The Current-solution Check assertion (`_corpus_list`
  vs the rows) expects the founder's rungs verbatim and first and Keel's appended rungs below to five; the Choose screen
  reads `choose.prompt` (*"Which of these is most likely to be missing?"*) and the `suggested` radio, and picks the
  entry's tested item as today; `outcomeNotDifference` and jargon notes are recorded, not asserted.
- **FR-5a What keel-cloud 117's build settled (contract 29, document version 27; added 2026-10-23).** The draft of
  `problem.current_solution_satisfaction` carries optional `founder_rungs`, `line`, `reason`, `past_five`; the saved list
  and the lock serve `SavedList.line` (2 on lists saved before 117). The eval's scripted draft adds `founder_rungs` (the
  count of the entry's typed rungs) and `line`; without them code counts the leading verbatim rungs and defaults the line
  to 2 capped at the founder's count, so the golden ladders reproduce unchanged (keel-cloud's `src/test/resources/ladders/`
  holds all seven). The Check-screen and brief bar strings change (*"holds if at least 2 in 3 land below '<rung>'"*):
  `report_marks` reads the served `keelBar`, never a fixed string. L9/L10 notes are recorded, not asserted.
- **FR-5b What keel-cloud 121's build settled (contract 31, response contract 22, document version 29; added
  2026-10-23).** `IdeaLines.how` stays the primary string; `howDecider`, `audienceWords[]` and `notes[{rule, line, word,
  note}]` are always served; `PUT /v2/projects/{id}/idea/audience-words {expectedRevision, words[]}`; the decider's link
  serves `Idea.how` = `howDecider`; draft items may carry `suggested` + `suggestedWhy` (Compatibility) and
  `outcomeNotDifference` + `outcomeNote`; `choose.prompt` on Compatibility reads *"Which of these is most likely to be
  missing?"* -- the Choose step picks the entry's tested item by label as today, never the suggested radio. The model may
  return `idea_how {primary, decider}` (a plain string still read); the mechanism context gains `audience_words`, the
  SOLUTION calibration `interpretation` gains `current_way {phrase, outcomes, line}`. With today's script no golden number
  moves; 05-paidly's scripted reveal says "platform", so its mechanism draft now carries a J1 `founderNote` (a string, no
  repair turn): the harness's check that the card's note is null on 05 is updated to expect J1 there.
- **FR-6 The persona step (keel-cloud 123 FR-10; keel-web 099).** `Corridor.persona` fills *"What is their job title?"*
  from the entry's `persona.decision_maker.title` (the loader accepts it, optional, 1–5 words; the six back-test entries
  and `10-fixture-b2b` carry one; golden entries without one get the role word, recorded); `leg_persona` asserts
  `deciderTitle` when sent; the stage-page banner read (`decider_banner`) accepts the title or the role.
- **FR-7 The follow-up ladder (keel-cloud 118).** `harness/interviewer_fake.LADDER` follows 118 FR-4: Purchase friction
  leaves `NO_FOLLOW_UP` (*took a long time* → *"What took the time?"*; *quick* / *not needed* → *"What did slow it down,
  if anything?"*); Adoption friction's two stems; Commitment's *after <smaller step> first* → *"What would the <smaller
  step> have to show you?"*, *probably not* / *no* → *"What would you start with instead?"*; `first_rung` takes the
  stage's deciding line first, then registry order; `LADDER_SHA` re-pinned to keel-cloud's `Ladder.java`; `RUNG_HEADINGS`
  the stems asked. Commitment's served options carry `conditional: true` on the second yes (`fixed_four` of three where
  the step costs nothing): `person_inputs` maps a corpus `yes_after_trying` pick onto the served conditional option when
  one is served and onto *probably not* when none is (a finding, not a silent drop, when a back-test person's pick has
  no rung). `report_marks` reads Commitment's headline as option 1 only and the friction lines in 118 FR-3's words.
- **FR-7a What keel-cloud 118's build settled (contract 27; added 2026-10-22).** The conditional yes is the Commitment
  list's second item (code `smaller_step`) and the served option carries `conditional: true`; Adoption friction's *"Yes,
  if it was clearly worth it"* is `conditional` too. A Commitment option may run to eleven words ("Yes, I'd" plus a
  nine-word step): the spoken-form check's nine-word cap allows that one shape, by rule, not by a widened cap. Purchase
  friction keeps three bands (held = amber, not held = favourable, between = split; keel-cloud 118 judgement call 1) --
  `report_marks` reads all three. Every Purchase friction answer is owed a follow-up; second stems ride as `<dimension>#also`
  clips. The eval's copy of `executor-fixtures/THEMES/cases.json` is re-copied from keel-cloud's export (scenario C3's
  people changed under the deciding-first order); `test_follow_up_ladder.py` re-pinned.
- **FR-8 Insights and the decision (keel-cloud 119, 122; keel-web 095, 098).** `backtest.themes_settle` and the
  corpus scenario's wait read `standings.insights[].state` (`GROUPING | GROUPED | RAW`) and `standings.notAsked`; the
  record keeps `side`, `dissent`, every quote; the Insights view read expects no card for a dimension without words and
  the *"Keel is grouping…"* line while GROUPING; `brief()` records `facts.decision.change` and `contextUnderstands`
  and the overview read takes the change sentence in place of the reason line. The commercial lines' words follow 115
  judgement call 14 (`report_marks` / `instructions/brief_facts.py` read the unit as served; the median only where
  served; *asked against: <claim>* under Price).
- **FR-8a What keel-cloud 119's build settled (contract 28, response contract 20; added 2026-10-22).** `standings.notAsked[]`
  is `{dimension, name, why}`; `insights[]` entries exist only with words and carry `state`, `note` (RAW only),
  `dissent` + `frame`, `quotes[] {invitationId, name, text, option, side, heading}`, `themes[] {label, count, quotes[],
  quoteIds[]}` with up to three themes then `ON_THEIR_OWN` last, `rawQuotes[]` shortest first when not GROUPED;
  `noQuestionWhy` is always null. The eval's THEMES fake (`harness/interviewer_fake.py themes`) puts leftovers in one
  last `ON_THEIR_OWN` group; `executor-fixtures/THEMES/cases.json` re-copied (`maxItems` 4); `report_insights` /
  `report_marks` read the new shape; a dimension with one answer is grouped by code (no job) -- the scenario's job
  counts follow; C5 has no entry (no words).
- **FR-8b What keel-web 095's build settled (added 2026-10-23; the full selector table is in keel-web
  `specs/095-insights-tab-from-every-word/tasks.md`).** `.rp-concern` is the rung heading alone (`.rp-concern__n` gone);
  `.rp-nofollow` is gone, the reasons are `[data-testid=insights-not-asked] li[data-dim]`; `.rp-raw` only on RAW with
  `.rp-raw__note`; `[data-testid=insights-grouping]` while GROUPING (the page re-reads every 10 s); theme labels in
  `span.rp-themes__label`; `li[data-own]` for *On their own*; `section.rp-ibox[data-state]`; `[data-dissent=true]` with
  `.rp-frame` (which `report_no_repeat` must treat as the view's own line); `div.rp-iq > p.rp-pick` with `.rp-opt` and
  `.rp-side[data-side]`; `[data-testid=insights-more]` folds at six quotes. `.rp-quote` text is unchanged. Copy moved:
  *In their own words*, *Keel is grouping what they said…*, *On their own*, the side marks for / against / apart;
  *said why* and *No follow-up on this rung* are gone.
- **FR-9 The back-test runner (062, 063).** `backtest.md` adds the equation and locked lines the founder saw, the value
  box label and bands each stranger saw, the gate chip question, the decider's title, each insight's state; the markdown
  anchor for a refused step stays *"Keel couldn't finish this step"* (093). `make backtest` on an r13 entry drives the
  chain; the harness artefacts of the first round (pooled follow-up lines, the Importance probe, the hourly rate by API,
  quarterly ÷ 3) stay fixed as they are.
- **FR-10 Marks.** `MARKS_VERSION` stays 20 unless a mark's field list or golden number must move; if one must, say which
  and why in tasks.md and stop there -- the operator decides the bump. `instructions/marks.py` gains a Spec 064 paragraph
  (r13 by sha256 of the seven files at the 124 merge).

## Acceptance

1. `make unit` green with the new tests (count before/after in tasks.md).
2. `make eval K="s005 or s006 or s007"` on a fresh local stack of the finished masters: green, or every red named with
   the served text beside the expected one (a golden number that moved is reported, not re-typed); durations recorded.
3. The operator's `make backtest ENTRY=08-fresco` on the same stack walks the chain end to end (the equation, the locked
   price words, the value box, the plan where the entry has one, the gate chip where served, the title, the new stems,
   the insight states) and records it; no mark or version moved by this spec.
