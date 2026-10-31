# The question-quality rubric

**RUBRIC_VERSION 3** (spec 109, 2026-10-31; version 2 was spec 081's, version 1 spec 078's). The design of record is
keel-cloud-docs `canon/designs/question-quality-rubric-2026-10-28.md` §3 as amended 2026-10-28 (the criteria and their
anchors: R2 plain to *this* person, R6 said aloud) and §4 (the weak rule), and spec 109 for §B (the screens after the
answers); this file is the one source of the criteria -- `quality/rubric.py` pastes the part between the two `prompt`
markers below into both readers' prompts, the part between the two `prompt-r6` markers into the respondent-reader's
alone, and the part between the two `prompt-b` markers into the founder-reader's prompts for the screens after the
answers, so a reader can never be scoring a different rubric from the one written here.

**A change to a criterion, an anchor, the booleans, the weak rule or `score_pct` bumps `RUBRIC_VERSION`** (in
`quality/rubric.py`), and this file says under *Versions* what changed and why -- the pattern of `MARKS_VERSION`.
Scores of two rubric versions are never averaged, compared or tabled together: `quality/table.py` refuses a mix.

<!-- prompt:begin -->
## The criteria

Score every criterion 0, 1 or 2, with one sentence of why. A 0 anywhere flags the screen.

**The yardstick is this person, never the general public.** You were told who you are before the screen: your trade,
your place, your time of life, and the project's what, where and when. Judge every criterion from inside that person.
The words your trade uses are plain to you (*nautical miles* to a mariner, *PR* to a developer); a word from outside your
trade is not, however common it is elsewhere.

| # | Criterion | 2 | 1 | 0 |
|---|---|---|---|---|
| R1 | **Fits here.** Does this question belong at this point of the study, for this person? | obvious why it is asked | plausible but abrupt | out of place, or asks what was already answered |
| R2 | **Plain to this person.** Can *this* person -- in their trade, their place, their time of life -- answer it on first reading (or first hearing, on the AI link)? The words their trade uses are plain to them; a word from outside their trade is not, however common elsewhere. | yes, in their own words | needs a second read, or one word they would not use | confusing, double-barrelled, or words of another trade |
| R3 | **About their life.** Is it answerable from what this person actually knows and does? | yes | partly, they would guess | no, it asks about someone else's job or a thing they never see |
| R4 | **The options.** Complete, distinct, in the person's words, no stupid or missing one; the escape chip fits | all four | one option odd or overlapping | an option is nonsense, two mean the same, or the true answer is missing |
| R5 | **The founder's words, kept.** The founder-reader: does the screen still mean what I typed? The respondent-reader: is nothing of the founder's product or roles leaking to me? | kept | drifted a little | wrong, or leaks |

R4 is `null` only on a screen that shows no options, rows, chips or value box at all (a card to read, a box to type
in); every other criterion is always scored.

## The instead line

`instead`: one line, *what I would have asked instead* -- the question (and options) you would have put on this screen,
in this person's words. Empty when you would change nothing.
<!-- prompt:end -->

## R6, said aloud (the respondent-reader, every respondent screen)

One wording serves the phone screen and the AI interviewer (spoken-questions-guidelines §1), so no respondent screen is
exempt. The runner hands the respondent-reader the screen as the avatar says it (the served spoken form, else the
guidelines' §3 template filled from the screen) and keel-cloud's `canon/designs/spoken-questions-guidelines.md` §2, §3
and §5 pasted whole (one source, read from the cloud checkout at the bundle's sha where that commit has it, else the
checkout's). The founder-reader has no R6.

<!-- prompt-r6:begin -->
| # | Criterion | 2 | 1 | 0 |
|---|---|---|---|---|
| R6 | **Said aloud.** Read it as the AI interviewer says it, options and escape included, against the spoken-question guidelines below (§2 the writing rules, §3 the spoken rendering, §5 one escape): would this person hear it once and answer? | says well: short, one question, the options spoken as a list a person can hold | one option or clause is a mouthful, a number or symbol that does not say well | cannot be said: a parenthesis, a slash, an abbreviation only the eye reads, two questions in one breath |

R6 is scored on every screen of this link, the cards to read and the boxes to type in included (a card is said aloud
too). It is your judgement of how it sounds; the code's own `spoken_form` mark (a word cap and three transforms) is a
different check.
<!-- prompt-r6:end -->

## §G The Insights grouping (the respondent-reader, once per follow-up line)

After a link's screens, the respondent-reader is handed the bundle's follow-up groupings for that link (the founder,
2026-10-28): for each follow-up line with two answers or more -- the line's question and every answer on it, the
groups Keel made with their names and the answers in each, and the answers left on their own -- it answers two
criteria, one call a line:

<!-- prompt-g:begin -->
| # | Criterion | 2 | 1 | 0 |
|---|---|---|---|---|
| G1 | **Grouped as a person in this job would.** Every answer sits in a group a person in this job would recognise, and the group names are plain. | all | one odd placement, or a vague name | an answer in a group it does not belong to, or two groups that mean the same |
| G2 | **Junk kept out.** Junk, explicit or off-topic answers are kept out of the groups. | none in | a borderline one in | a junk answer grouped as if it were about this |

G2 is 2 by default when there is no junk answer on the line -- say so in its why. Answers left on their own (not in a
group) are not a fault of G1 by themselves: judge whether they belong in a group that exists.
<!-- prompt-g:end -->

Recorded as `insights: [{line, dimension, link, g1, g2, whys}]` and **folded into the respondent's `score_pct`** (and
the overall) by the same 2 x count arithmetic, with `insights_pct` beside. A bundle with no follow-up line of two
answers records *no grouping to read* (`insights_note`) and is not penalised. In `TABLE.md` the readings are rows of
their own, one per (scope, dimension), under the *insights* kind, held to the same weak rule.

## §B After the answers (the founder-reader, once per study, after everyone has answered)

The founder, 2026-10-30: *"After everyone has answered, go back to the problem screen and the insight screen, per
project, and ask: does it make sense?"* Once the last person's answers are in and the standings have settled, the
back-test walk opens the study's stage page (`/p/{id}/s/{STAGE}`: the verdict and one card per dimension), opens each
dimension's card in turn (the card with its chart), and opens the Insights screen (`/p/{id}#insights`) -- the kinds
`stage`, `dimension` and `insights-screen` (spec 109 FR-1). The founder-reader reads each as the founder who typed the
project: the persona block it already has, and the beliefs it checked on the way in.

<!-- prompt-b:begin -->
| # | Criterion | 2 | 1 | 0 |
|---|---|---|---|---|
| B1 | **I know the answer and why.** The verdict (held / did not hold / insight) is stated, and the number that decides it is on the screen beside it. | both | one, or the number is there but not tied to the verdict | neither, or they disagree |
| B2 | **The chart reads at a glance.** What is counted, over how many people, and where the bar sits are plain on first look. | all three | one needs a second look | I cannot tell what the chart counts |
| B3 | **It is about my belief, in my words.** The dimension's name and the belief line are the ones I checked on the way in. | yes | reworded but recognisable | not mine |
| B4 | **I know what to do next.** The screen says what this result means for the idea, concretely. | yes | a generic line | nothing, or wrong |
| B5 | **Nothing misleads.** No claim beyond the people who answered (n stays visible; a low n is said; a held belief with 3 of 7 is not called strong). | none | one soft overstatement | a claim the data cannot carry |
| B6 | **Teaches me something I did not type.** The themes and quotes add to what I wrote. | they add to what I wrote | they restate it | noise |

The stage page and each dimension card are scored on B1 to B5. The Insights screen is scored on B1, B3, B4, B5 and
B6: it draws no chart, so B2 is not scored there, and how the answers were grouped is not read again (the
respondent-reader's G1 already reads it). Every criterion a screen is scored on is always scored.

`instead`: one line, *what I would have this screen say instead*, in my own words. Empty when I would change
nothing.
<!-- prompt-b:end -->

Recorded on the screen's own score, `b1`..`b6` with `why_b1`..`why_b6` (a §B screen carries no `r1`..`r6`; B2 is
`null` on the Insights screen, B6 on the stage page and the cards), audience `founder`, and **folded into the founder's
and the overall `score_pct`** by the same 2 x count arithmetic, `after_pct` beside. In `TABLE.md` the screens are rows
of their own, one per (scope, kind, dimension) under the three kinds, held to the same weak rule.

## The two booleans (code's, never the reader's)

The founder asked for two flags by name. They are **derived by code** from the reader's scores, so they can never
disagree with them:

- `out_of_place` = R1 is 0; on a §B screen, B1 is 0 (version 3).
- `looks_stupid` = R2 is 0, R4 is 0 or R6 is 0 (R6 since version 2); on a §B screen, B2 or B5 is 0 (version 3).

## The three whole-flow questions

Once per study, per audience (the founder-reader once; the respondent-reader once per link), after every screen is
scored, the reader is shown the whole walk as a compact list and answers:

1. `order` -- does the order make sense? (0 / 1 / 2 and one sentence)
2. `asked_twice` -- was anything asked twice? (the screens, or empty)
3. `missing` -- was anything that should be asked missing? (what, or empty; the founder-reader knows the YC material,
   so it can say *nobody asked about X*)

## The score as one number

- `score_pct` = (the sum of every r1..r6 and b1..b6 given over the screens, plus every g1 and g2 of the insight lines)
  / (2 x the count of those scores) x 100 -- a `null` R4 (nothing to pick), R6 (a founder screen), B2 (the Insights
  screen) or B6 (the stage page, a card) is not a score and is in neither sum; R6 and the insight readings are the
  respondent-reader's, so they count in the respondent's and the overall `score_pct`, never the founder's; B1-B6 are
  the founder-reader's, so they count in the founder's and the overall, never the respondent's.
- `spoken_pct` = the same over R6 alone, beside it (version 2), per audience where there is an R6 and overall; the
  head of `TABLE.md` shows it beside `insights_pct`.
- `insights_pct` = the same over the g1 and g2 alone, beside it. Per audience and overall, on every score file and in `TABLE.md`.
- `after_pct` = the same over b1..b6 alone, beside it (version 3), per audience where there is a §B screen and overall;
  the head of `TABLE.md` shows it on the founder's line.
- `flagged_pct` = the screens with any 0 / the screens scored x 100.
- **The bar is 90%** (the founder, 2026-10-28): the overall `score_pct` over the latest file of every entry, before
  the remaining entries are walked.

## The weak rule

A row of `TABLE.md` -- one (dimension, audience, screen kind) over the latest score file of each entry -- is **weak**
when, on any one criterion,

- a 0 was given in **two or more entries**, or
- the **mean is under 1.5**.

R6 is a criterion like the others under this rule (version 2 did not move the rule), and so is each of B1-B6 on a §B
row (version 3 did not move it either). The weak rule is a first guess (the design's open item 4) and moves only with a
version bump.

## The verdict against the baseline

`make read-table BASELINE=1` compares each row with `BASELINE.md`'s: the deltas (the six criteria; G1 and G2 on an
insights row; B1-B6 on a §B row), and one verdict line --

- **worse** when any row is weak now that was not weak in the baseline, or the overall `score_pct` fell by a point or more;
- **better** when no row became weak and either a weak row stopped being weak or the overall `score_pct` rose by a point
  or more;
- **same** otherwise.

## Versions

- **3** (spec 109, 2026-10-31; the founder, 2026-10-30: *"till now we have only been judging the respondent and the
  founder screens ... we have not been judging the problem and solution screens ... After everyone has answered, go
  back to the problem screen and the insight screen, per project, and ask: does it make sense?"*):
  - **§B, after the answers**: the founder-reader scores the study's stage page and each dimension card (B1-B5) and
    the Insights screen (B1, B3, B4, B5 and B6), read as the founder who typed the project, with the instead line;
    `out_of_place` gains B1 = 0 and `looks_stupid` B2 or B5 = 0; the B scores fold into the founder's and the overall
    `score_pct` by the same arithmetic, `after_pct` beside; the weak rule unmoved. Why: the screens the founder reads
    after the answers -- the verdict, the chart, the Insights -- were never read at all.
  - **Version-2 files are set aside, never compared and never refused** (cycles 1 to 3 are version 2's, and stay of
    record): the table, the baseline and the cycle record compare within one version, and cycle 4 is the first at 3.
    Nothing is re-scored.
- **2** (spec 081, 2026-10-28; the founder: *"if a question says nautical miles and the person is a mariner, that's
  perfectly fine ... and the rubric should check whether our questions and options are AI-avatar friendly"*), before any
  score file was committed, so nothing is re-scored:
  - **R2 is judged from inside the persona.** Its question is *plain to this person* and its anchors *yes, in their own
    words* / *needs a second read, or one word they would not use* / *confusing, double-barrelled, or words of another
    trade* (were *yes* / *needs a second read* / *confusing, double-barrelled, jargon*): a trade's own word is not jargon
    to the trade, and version 1's anchors scored it as if read by the general public. Both prompts say the yardstick is
    this person (the founder's trade for the founder-reader).
  - **The persona block is handed before any screen**: both readers' prompts open with who they are and the project's
    what / where / when (actor, actor_plural, job, circumstance, segment, window, the market's country), and the score
    file records the blocks once in its header (`persona`), not per screen.
  - **R6, said aloud**, on every respondent screen, against the spoken-question guidelines §2, §3 and §5 the runner
    pastes (`spoken_guidelines` in the header names where they were read); folded into the respondent's and the
    overall `score_pct`, `spoken_pct` beside; `looks_stupid` gains R6 = 0; a respondent answer without R6 and a founder
    answer with one are refused. Why: one wording is said by the avatar and read on the phone, and version 1 read only
    the page.
  - A score file at version 1 is refused by name (`rubric.RETIRED`), never set aside: none was committed.
- **1** (spec 078, 2026-10-28): the design's five criteria and anchors, the two booleans, the instead line, the three
  whole-flow questions and the weak rule as the design states them; `score_pct`, `flagged_pct` and the bar of 90% (the
  coordinator's decision 2); R4 `null` on a screen with nothing to pick; §G, the Insights grouping (G1, G2), read by the
  respondent-reader once per follow-up line and folded into `score_pct` (the founder, 2026-10-28, before any score
  file was written -- so version 1 carries it from the start).
