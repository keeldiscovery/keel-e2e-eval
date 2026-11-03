# Spec 131 -- The readers know the dimension

The founder, 2026-11-03 08:30 ET, after staging's Current solution scale showed five shortfall rungs and nothing where
today's way works (keel-cloud 203): *"the agents which are evaluating the quality of the founder's questions ... and the
questions shown to the respondent need to be re-evaluated ... is it because our agents do not have enough context? ...
our agent should be dimension aware. It should understand the person who is seeing the thing. Can they understand the
terms? ... is this question valid -- do the options meet the criteria for that dimension, including the option?"*

Why it was missed: the readers are handed the persona (spec 081) and one screen's text, and score R1-R6
(quality/RUBRIC.md). R4 asks whether the options are *complete, distinct, in the person's words, no stupid or missing
one*; nothing tells the reader what the dimension measures, the shape its options must have, or which answers count
for and against the belief. On cycle 8 all fourteen Current solution Check screens were scored R4 1 or 2 for overlap and
coverage; none said *no rung where today's way works*. The adviser has the same blind spot. Builds on 078, 081, 109, 129.

## Rules

- **FR-1 The dimension card.** `quality/readers/dimensions.md`: one short card per registry dimension (the thirteen),
  hand-written in plain words from the registry row and checked against it by a test (`meaning`, the founder
  `control`, the option rule's shape, `answers.compare_rule`, the escape): *what it measures*; *the shape the options
  must have* (Current solution: *a scale from today's way getting the job done, down to failing outright, the
  founder's line between them; every rung on one measure, the one the founder's Answer names*; Importance: *the
  founder's own difficulty first, then rivals the same people meet in the same circumstance, each distinct*; Prevalence:
  *the gate's yes/no over the window, no unsure*; the money rows as their 115/181/182 forms say; and so on); *what the
  belief this screen tests will count for and against*; *what the escape means and when it must be there*. Each card
  says the same thing for the founder's screens and the respondent's item of that dimension.
- **FR-2 In every prompt with a dimension.** `quality/readers.py` sends the screen's dimension card to the
  founder-reader and the respondent-reader after the persona and before the screen (`{{dimension}}`), on every screen
  whose `dimension` is set (answer, check, choose, q, the respondent item and gate, the after-the-answers dimension
  card); screens with none (context, idea, send) get no block. The score file records which card was sent.
- **FR-3 R7, fits the dimension.** `quality/RUBRIC.md` gains R7: *Do the options meet this dimension's own rules --
  the measure, the shape, the escape -- and does the belief this screen will test make sense against them?* 2 all
  met; 1 one rule bent; 0 a rule broken (a scale with no working rung, an item whose options cannot answer the
  belief, a missing escape the card requires). Scored by both readers on every screen with a dimension, `null`
  elsewhere; a 0 flags the screen like any other. RUBRIC_VERSION 4 -> 5; version-4 files set aside as before.
- **FR-4 The adviser** is handed the same card for the row it advises, and its proposal is refused as a special case if
  it contradicts the card (spec 081 FR-6's refusal extended).
- **FR-5 The weak rule and the score** treat R7 as any criterion. The record's head and TABLE.md carry R7's column.
- **FR-6 Tests.** The thirteen cards exist and match the registry; a Check screen with five shortfall rungs (the
  angel-group scale of 2026-11-03, as a fixture) scores R7 0 under a scripted reader; a prompt for a screen with a
  dimension carries its card and one without carries none; the rubric's prompt markers hold R7. `make unit` green.
  No paid run.

## Not in this spec

A walk (none until the founder's word); changing R1-R6; the readers' model or effort.

## Amendment 2026-11-03 08:50 ET -- the cards are the whole of it

The founder: *"while writing the dimension check ... spend a good amount of time for how each dimension would look like,
and how the options should look like, how much of them should be for and how much should be against, and ensure that
that's foolproof."*

- **FR-1a Each card carries, in this order, for the founder's screens and the respondent's item alike:**
  1. **What it measures**, one sentence, from the registry's `meaning`.
  2. **The options' shape**: how many, in what order, on what one measure, what the first and the last must be
     (Current solution: the first is today's way getting the job done, the last today's way failing outright, the
     founder's line between; Commitment: the founder's step as a firm yes, a probable yes, probably not, no; Importance:
     the founder's own difficulty locked first, then rivals the same people meet in the same circumstance, each distinct,
     none the whole job; Prevalence: yes / no over the window, no unsure; Frequency: the window's units as bands; the
     money rows exactly as specs 115, 180, 181, 182 and 198 shaped them), with the registry's `control`,
     `option_rule` and `fixed_answers` as the source.
  3. **Which answers count for the belief, which against, which neither**, by the registry's `answers` block
     (`compare_rule`, `supports`, `conditional`, the `against` sets, the `floor`): the card names them in plain words
     (Current solution: the belief is *their way still falls short*, so *for the belief: every rung below the founder's line; against: the rungs above it, where today's way did the job; the escape counts nobody* -- the registry's `below_line` is the source, as the card says; the review of 2026-11-03 corrected this spec's first sketch, which had the direction reversed) and says what a healthy scale therefore needs (*at least one rung above the line, else nothing can count
     for today's way and the belief is tested against nothing*).
  4. **The escape**: which chip, what it means, when it must be there and when it must not (Prevalence's gate has none).
  5. **Two examples**: one scale that meets the card and one that breaks it, each with the words that break it named
     (the angel-group scale of 2026-11-03 is Current solution's bad example).
- **FR-1b Foolproof by test.** For every card a test reads the registry row and asserts: the counts and order in the
  card's shape match `option_rule` / `fixed_answers`; the for / against / neither lists equal the codes the registry's
  `answers` block counts; the escape matches `escape` / `left_out`; the bad example is scored R7 0 by a scripted reader
  and the good one 2. A card that drifts from the registry fails `make unit`.
- **FR-1c R7's wording asks the reader the card's own questions**, in order: the measure, the shape, the for/against
  balance (*could the belief ever be supported by these options? could it ever be refuted?*), the escape. A scale where
  every option counts one way is a 0.
