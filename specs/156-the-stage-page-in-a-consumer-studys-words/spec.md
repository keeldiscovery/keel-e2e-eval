# Spec 156 -- The stage page in a consumer study's words

Found by the first scope-ALL back-test that reached the money page on a consumer study since spec 155 (run
`20261118T013924Z-backtest-13-aircaps`, 2026-11-17 21:05 ET, stack keel-cloud 474aefd1 + keel-web cae3804b). The walk
had every verdict in hand and stopped on its last founder step: *the money page: Ability to pay's said line is Keel's
reading ... off the budget question the counts sentence alone*. The page drew *Counts against: other money, or couldn't
pay it.*; the wire served *... new money ...*; the harness held the drawn line to the served one, word for word.

The product is right. keel-web 106 FR-2 (`CONSUMER_WORDS`, `consumerWords`, `sayOf` in `src/lib/report.ts`) says a
consumer study's report never says *decision-maker(s)*, *the payer*, *per person* or *new money*, and
`DimensionStagePage.tsx` passes every served line it draws through `say` -- the belief, the status line, the insight,
the band label, the measure's unit, the said line, the rule / count / so lines and each person's `readAs`. The harness
already mirrors the list of forbidden words (`report_marks.CONSUMER_REPORT_WORDS`, spec 068 FR-4) for the Overview and
the Insights, but no step of the stage pages applies the rewrite before comparing. The 11/13 money-only run passed only
because its Ability was derived from the price (*Keel reads your price ...*), a sentence with none of the four words.

## Rules

- **FR-1 The rewrite, mirrored.** `report_marks.consumer_words(text)` is keel-web's `consumerWords`: the fourteen
  `[from, to]` pairs of `CONSUMER_WORDS` in `src/lib/translate.ts` (cae3804b), in the same order, as Python regexes with
  the same word boundaries and case; the leading space trimmed as the web trims it. `CONSUMER_REPORT_WORDS` stays and
  is derived from nothing else. A unit test pins every pair on one sentence each, and the counts sentence of
  `vectors_screens.COUNTS_SENTENCE[False]` to *Counts for you: money they already spend. Counts against: other money,
  or couldn't pay it.*
- **FR-2 Every stage-page comparison says it the study's way.** `corpus_scenario` holds a drawn line of a stage page
  to `consumer_words(served)` when the entry is not B2B (`vs.is_b2b(j.entry)` false) and to `served` when it is --
  in `_hold_the_ability_line` (the said line against `founderSaid`, and `budget_bars_faults`'s own equality against
  `COUNTS_SENTENCE`), `_hold_the_buyer_line`, the people's `readAs` (`page["people"] == people`), the follow-up rung
  lines, and any other place the builder finds (`grep -n 'page\[' evals/corpus_scenario.py` around the stage-page
  steps, and `harness/vectors_screens.py`'s stage-page readers). One helper, `said_as(j, text)`, does the choice; no
  comparison rewrites the drawn side. The record of each step keeps both: `served` as the wire gave it and `want` as
  the page should draw it.
- **FR-3 Nothing else moves.** The Overview and Insights steps (spec 068 FR-4) are unchanged; the B2B path compares as
  today; no screen, press or wait changes; nothing paid runs.
- **FR-4 Tests.** `tests/test_consumer_words_156.py`: the fourteen pairs; the counts sentence on a consumer and a B2B
  entry; `_hold_the_ability_line` on a fake page drawing *other money* passes for a consumer entry and fails for a B2B
  one, and the reverse for *new money*. `make unit` green but for the 26 sibling-mirror reds master carries today
  (test_cloud_245_250_248_web_186_190_mirror_154 ×20, mirror_144, mirror_148, mirror_149, test_follow_ups_075,
  test_instruction_compare, test_report_marks), named in tasks.md.

## Not in this spec

Re-cutting the 26 sibling-mirror reds. Any change to keel-web or keel-cloud. A new back-test (on the founder's word
after the merge: `make backtest DOOR=keel ENTRY=13-aircaps SCOPE=ALL`, the proof).
