# Spec 109 -- After everyone has answered, the reader judges the stage page and the Insights screen

The founder, 2026-10-30: *"till now we have only been judging the respondent and the founder screens … we have not been
judging the problem and solution screens: the problem has four dimensions, you click on it, the chart shows up -- is it
helpful for the founder, does it come through? And the Insights tab. After everyone has answered, go back to the problem
screen and the insight screen, per project, and ask: does it make sense?"* Today the quality cycle's readers score the
founder's defining screens (`FOUNDER_SCREENS`), the respondent's screens and the themes' grouping (§G), and nothing
after the answers land: the stage page (`/p/{id}/s/{PROBLEM|SOLUTION|COMMERCIAL}`, the verdict and one card per
dimension whose click opens the chart) and the Insights screen (`/p/{id}#insights`) are never shot or read.

## Rules

- **FR-1 The answers leg.** Once per study, after the last person's answers are in and the standings have settled, the
  walk (the back-test journey in `evals/corpus_scenario.py` / `evals/backtest.py`, the browser as the founder) opens:
  (a) the study's stage page `/p/{id}/s/{scope's stage}` and shoots it (`founder-after-NN-stage.png`), then opens each
  dimension card in turn and shoots the opened card with its chart (`founder-after-NN-dimension-<key>.png`), capturing
  the page text and the chart's own words (title, bar, the n, the verdict line) for each; (b) the Insights screen
  `/p/{id}#insights`, shot once with its text and once more per *open* (`[data-testid=insights-open]`) where it folds;
  (c) nothing else (the Pilot tab and the People rows are out of scope here). Money alone has one stage; the three-study
  cycle three. The screens join the bundle's `screens/` with audience `founder` and the new kinds `stage`,
  `dimension`, `insights-screen`.
- **FR-2 The founder-reader scores them.** `quality/RUBRIC.md` **RUBRIC_VERSION 3**: a section *§B After the answers* with
  five criteria for the stage page and each dimension card, read as the founder who typed the project (the persona and
  the entry the reader already has):
  | # | Criterion | 2 | 1 | 0 |
  |---|---|---|---|---|
  | B1 | **I know the answer and why.** The verdict (held / did not hold / insight) is stated, and the number that decides it is on the screen beside it. | both | one, or the number is there but not tied to the verdict | neither, or they disagree |
  | B2 | **The chart reads at a glance.** What is counted, over how many people, and where the bar sits are plain on first look. | all three | one needs a second look | I cannot tell what the chart counts |
  | B3 | **It is about my belief, in my words.** The dimension's name and the belief line are the ones I checked on the way in. | yes | reworded but recognisable | not mine |
  | B4 | **I know what to do next.** The screen says what this result means for the idea, concretely. | yes | a generic line | nothing, or wrong |
  | B5 | **Nothing misleads.** No claim beyond the people who answered (n stays visible; a low n is said; a held belief with 3 of 7 is not called strong). | none | one soft overstatement | a claim the data cannot carry |
  The Insights screen takes B1, B3, B4, B5 and §G's G1 as read already (no second grouping read), plus **B6 Teaches me
  something I did not type**: the themes and quotes add to what the founder wrote (2), restate it (1), or are noise
  (0). The *instead* line, the `out_of_place` / `looks_stupid` booleans (B1 0 -> out of place; B2 or B5 0 -> looks
  stupid), the weak rule and the fold into the founder's `score_pct` as today's 2 x count arithmetic.
- **FR-3 The table and the record.** `TABLE.md` rows per (scope, kind, dimension) under the three new kinds; the
  adviser's fix locations: `stage` and `dimension` -> keel-web's stage page and chart words plus keel-cloud's
  `BriefFacts` / verdict lines; `insights-screen` -> themes.md and keel-web's Insights tab. `quality/decisions.py`
  `FOUNDER_SCREENS` gains the three kinds; `test_decided_before_087` re-pinned.
- **FR-4 Cost.** About 4 to 6 more screens per study for the founder-reader (one stage, three to five cards, one
  Insights), roughly +40% of a study's reading; `quality/CYCLE.md` says so. Version-3 score files are not compared with
  version-2 ones (the cycle machinery already compares within a rubric version); cycle 4 is the first at 3.
- **FR-5 Tests.** The answers leg on the local stack with fakes (`make eval` journey or the back-test smoke): the shots
  exist with text; the reader's prompt for §B; the fold and the weak rule on a fixture score file; `make unit` ZERO failed.

## Acceptance

`make unit` ZERO failed; one back-test walk on the local stack (the coordinator's, Keel's AI on the founder side costs
about $0.50) shows the new screens in the bundle and the record. Build after 106, before 095. keel-web owes nothing
unless a card or the chart lacks a stable test id the leg needs (the builder lists any in tasks.md).
