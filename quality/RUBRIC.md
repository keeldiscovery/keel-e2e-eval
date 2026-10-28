# The question-quality rubric

**RUBRIC_VERSION 1** (spec 078, 2026-10-28). The design of record is keel-cloud-docs
`canon/designs/question-quality-rubric-2026-10-28.md` §3 (the five criteria and their anchors) and §4 (the weak
rule); this file is the one source of the criteria -- `quality/rubric.py` pastes the part between the two `prompt`
markers below into both readers' prompts, so a reader can never be scoring a different rubric from the one written here.

**A change to a criterion, an anchor, the booleans, the weak rule or `score_pct` bumps `RUBRIC_VERSION`** (in
`quality/rubric.py`), and this file says under *Versions* what changed and why -- the pattern of `MARKS_VERSION`.
Scores of two rubric versions are never averaged, compared or tabled together: `quality/table.py` refuses a mix.

<!-- prompt:begin -->
## The five criteria

Score every criterion 0, 1 or 2, with one sentence of why. A 0 anywhere flags the screen.

| # | Criterion | 2 | 1 | 0 |
|---|---|---|---|---|
| R1 | **Fits here.** Does this question belong at this point of the study, for this person? | obvious why it is asked | plausible but abrupt | out of place, or asks what was already answered |
| R2 | **Plain.** Can this person answer it on first reading (or first hearing, on the AI link)? | yes | needs a second read | confusing, double-barrelled, jargon |
| R3 | **About their life.** Is it answerable from what this person actually knows and does? | yes | partly, they would guess | no, it asks about someone else's job or a thing they never see |
| R4 | **The options.** Complete, distinct, in the person's words, no stupid or missing one; the escape chip fits | all four | one option odd or overlapping | an option is nonsense, two mean the same, or the true answer is missing |
| R5 | **The founder's words, kept.** The founder-reader: does the screen still mean what I typed? The respondent-reader: is nothing of the founder's product or roles leaking to me? | kept | drifted a little | wrong, or leaks |

R4 is `null` only on a screen that shows no options, rows, chips or value box at all (a card to read, a box to type
in); every other criterion is always scored.

## The instead line

`instead`: one line, *what I would have asked instead* -- the question (and options) you would have put on this screen,
in this person's words. Empty when you would change nothing.
<!-- prompt:end -->

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

## The two booleans (code's, never the reader's)

The founder asked for two flags by name. They are **derived by code** from the reader's scores, so they can never
disagree with them:

- `out_of_place` = R1 is 0.
- `looks_stupid` = R2 is 0 or R4 is 0.

## The three whole-flow questions

Once per study, per audience (the founder-reader once; the respondent-reader once per link), after every screen is
scored, the reader is shown the whole walk as a compact list and answers:

1. `order` -- does the order make sense? (0 / 1 / 2 and one sentence)
2. `asked_twice` -- was anything asked twice? (the screens, or empty)
3. `missing` -- was anything that should be asked missing? (what, or empty; the founder-reader knows the YC material,
   so it can say *nobody asked about X*)

## The score as one number

- `score_pct` = (the sum of every r1..r5 given over the screens, plus every g1 and g2 of the insight lines) / (2 x the
  count of those scores) x 100 -- a `null` R4 is not a score and is in neither sum; the insight readings are the
  respondent-reader's, so they count in the respondent's and the overall `score_pct`, never the founder's.
- `insights_pct` = the same over the g1 and g2 alone, beside it. Per audience and overall, on every score file and in `TABLE.md`.
- `flagged_pct` = the screens with any 0 / the screens scored x 100.
- **The bar is 90%** (the founder, 2026-10-28): the overall `score_pct` over the latest file of every entry, before
  the remaining entries are walked.

## The weak rule

A row of `TABLE.md` -- one (dimension, audience, screen kind) over the latest score file of each entry -- is **weak**
when, on any one criterion,

- a 0 was given in **two or more entries**, or
- the **mean is under 1.5**.

The weak rule is a first guess (the design's open item 4) and moves only with a version bump.

## The verdict against the baseline

`make read-table BASELINE=1` compares each row with `BASELINE.md`'s: the five deltas, and one verdict line --

- **worse** when any row is weak now that was not weak in the baseline, or the overall `score_pct` fell by a point or more;
- **better** when no row became weak and either a weak row stopped being weak or the overall `score_pct` rose by a point
  or more;
- **same** otherwise.

## Versions

- **1** (spec 078, 2026-10-28): the design's five criteria and anchors, the two booleans, the instead line, the three
  whole-flow questions and the weak rule as the design states them; `score_pct`, `flagged_pct` and the bar of 90% (the
  coordinator's decision 2); R4 `null` on a screen with nothing to pick; §G, the Insights grouping (G1, G2), read by the
  respondent-reader once per follow-up line and folded into `score_pct` (the founder, 2026-10-28, before any score
  file was written -- so version 1 carries it from the start).
