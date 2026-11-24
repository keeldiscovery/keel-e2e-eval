# The film rubric

**FILM_RUBRIC_VERSION 1** (spec 163, 2026-11-24). The founder, 2026-11-24: *"the judging criteria should be based on the
quality of the animation that we create for the respondent. Does it cover all the user persona, the things they want to
do, the limitation and the pain? Is it clearly spelled out? And the end-to-end."* -- *"no words are garbled. There's a
clarity on it. If there is anything written on it, it's clearly readable."* -- and, on the solution film: *"if it's a
problem, it should test whether it really represents the person doing the task, having the limitations and the pain, and
the solution the other way around"*.

This file is the one source of the film's criteria: `quality/film_rubric.py` pastes the part between the two
`film-problem` markers into the film reader's prompt for a problem film, the part between the two `film-solution`
markers for a solution film (keel-cloud 271 / 273, once the solution batch is walked), and the part between the two
`film-founder` markers into the founder-reader's prompt for the founder's spoken beats -- so a reader can never be
scoring a different rubric from the one written here. The film reader is `quality/readers/film-reader.md` through the
Anthropic API with vision (`quality/readers.toml` `[film_reader]`); the founder-reader is
`quality/readers/film-founder.md` through the `claude` CLI, as `make read-screens`' readers.

**A change to a criterion, an anchor, the weak rule or `film_pct` bumps `FILM_RUBRIC_VERSION`** (in
`quality/film_rubric.py`), and this file says under *Versions* what changed and why. Film scores of two versions are
never averaged, compared or tabled together: `quality/film_table.py` refuses a mix. The film rubric's version is its
own: it never moves `RUBRIC_VERSION` (the question-quality rubric), and that one never moves this.

<!-- film-problem:begin -->
## The problem film's criteria

Score every criterion 0, 1 or 2, with one sentence of why. A 0 anywhere flags the film.

**The yardstick is this person, never the general public.** You were handed the persona card before the film: who the
person is, their trade and place, the task, the moment it arises, today's way, every limitation of the founder's problem
statement and what it costs them. Judge every criterion from inside that person, and from what you know of that trade:
where such a person does this task, what they wear, what is around them, when in the day it happens.

| # | Criterion | 2 | 1 | 0 |
|---|---|---|---|---|
| F1 | **The persona.** Is the person shown this person in their setting -- the trade's place, their garments, the time of day the task happens -- as the card says and as that trade would be drawn? | yes, recognisably this person in this place | the person or the place is generic, or one detail is off | another person, another trade, or a place they would never be |
| F2 | **The task.** Is what they are trying to get done shown and said, at the moment it arises? | shown and said, at its moment | said but not shown, or shown at the wrong moment | missing |
| F3 | **Today's way.** Is how they do it today shown and said, not only named? | shown and said | named only, or shown without being said | missing, or a way the card does not name |
| F4 | **Every limitation.** Does each limitation of the problem statement have its own scene that shows it (the thing that goes wrong) -- none missing, none invented? | every one, each its own scene | one missing, merged with another, or said but not shown | two or more missing, or one invented |
| F5 | **The pain.** Is the cost to them shown as the person's reaction (slumped, late, behind) in its own scene, and said in the founder's words? | shown as the reaction and said | said but the person does not react, or shared with another scene | missing |
| F6 | **Clearly spelled out.** Is each line plain to this person, in the founder's words, under 20 words, saying one thing, matching its picture -- nothing a stranger would misread? | every line | one line long, doubled, or off its picture | a line a stranger would misread, or most lines off their pictures |
| F7 | **End to end.** Do the lines in order tell the whole -- who, the task, today, where it falls short, the cost, the ask -- with the chapter marks in the right places, so a stranger who never heard of the problem could answer *Did this happen to you?* from the film alone? | yes | one beat thin or out of order, or a chapter mark misplaced | a stranger could not tell what the film asks about |
| F8 | **Legible.** No word garbled anywhere: every word written on the frame (the caption, the chapter mark, the board's ask) clearly readable at the size it is drawn, on the phone frame and the laptop frame; no text, letters, digits or logos inside any picture; no caption cut, overlapping or clipped. | all clear on both frames | one word hard to read, or one caption tight on the phone | a garbled word, text inside a picture, or a caption cut or clipped |

`missing`: a list -- every limitation of the card with no scene of its own, and every box of the board (the person, the
task, today's way, the cost) the film does not show. Empty when nothing is missing.

`instead`: for every criterion scored under 2, one line -- *what the film should have shown or said instead*, in this
person's words (the scene and the line). None for a criterion scored 2.
<!-- film-problem:end -->

<!-- film-solution:begin -->
## The solution film's criteria (the other way around)

Score every criterion 0, 1 or 2, with one sentence of why. A 0 anywhere flags the film. The yardstick is the same
person in the same place as the problem film: you were handed the persona card, the problem's limitations and its cost,
and the founder's idea board (the product, the setup, the steps, the marks, the advantage, what they get).

| # | Criterion | 2 | 1 | 0 |
|---|---|---|---|---|
| S1 | **The same person, the brand on the screen.** The same person in the same setting as the problem film; the brand (its colour and its mark) on the screen wherever the product appears. | yes | the person or the place drifts, or the brand is missing from one screen | another person, or no brand anywhere |
| S2 | **The setup iff named.** The setup is shown before the task where the founder named one, and nowhere where none. | as the board says | shown thinly, or out of place | missing where named, or invented where none |
| S3 | **The task with the product, step by step.** The person doing the task with the product, step by step as the board says. | every step | a step missing or merged | the task is not done with the product |
| S4 | **Each limitation a tick or a cross.** Each limitation of the problem film shown solved (a tick) or shown as not solved (a cross), none missing. | every one, marked as the board marks it | one missing or mismarked | two or more missing |
| S5 | **The advantage, once.** What the product does better is said once. | said once, plainly | said twice, or vaguely | missing |
| S6 | **The joy.** What the person gets back -- the pain's opposite, never a feature -- shown as the person upright. | yes | a feature in its place, or not shown | missing |
| S7 | **Clearly spelled out.** As F6. | every line | one line long, doubled, or off its picture | a line a stranger would misread |
| S8 | **End to end in five chapters.** *Before*, *The task*, *What it solves*, *Better*, *What they get*, in order, the marks in their places. | yes | one chapter thin or misplaced | a stranger could not tell what the product does for them |
| S9 | **Legible.** As F8. | all clear on both frames | one word hard to read | a garbled word, text inside a picture, a caption cut |

`missing` and `instead` as on the problem film (the limitations with no mark, the boxes of the idea board not shown).
<!-- film-solution:end -->

## The founder's beats (the founder-reader)

The founder, 2026-11-24: *"the quality of the questions shown to the respondent [and] to the founder"*. Keel's spoken
lines to the founder on the walk -- the problem's seven beat questions as Keel asked them, its asks and readbacks, and
the verdict line after the film's yes (the solution's four beats and the pilot ask once the solution batch is walked) --
are read by the founder-reader from inside the entry's founder (the founder-reader of `make read-screens`, the entry's
sources whole), one call a beat, on four of the question-quality rubric's criteria:

<!-- film-founder:begin -->
| # | Criterion | 2 | 1 | 0 |
|---|---|---|---|---|
| R1 | **Fits here.** Does Keel ask this at this point of telling the story, for me? | obvious why it is asked | plausible but abrupt | out of place, or asks what I already said |
| R2 | **Plain to me.** Can I answer it on first hearing, in my trade's words? | yes | needs a second hearing, or one word I would not use | confusing, double-barrelled, or words of another trade |
| R3 | **About what I know.** Is it answerable from what I know of my customers and my idea? | yes | partly, I would guess | no |
| R5 | **My words, kept.** Does Keel's readback, and the board, keep what I said? | kept | drifted a little | wrong |

Score each 0, 1 or 2 with one sentence of why. `instead`: one line, *what Keel should have said instead*, in my own
words. Empty when I would change nothing.
<!-- film-founder:end -->

Recorded in the film's score file under `founder` (`beats`: one row a beat, `r1`, `r2`, `r3`, `r5`, their whys and the
instead line), **never folded into `film_pct`**: `founder_pct` = the sum of every R given over 2 x their count x 100,
beside it.

## The score as one number

- `film_pct` = the sum of the eight F (nine S on a solution film) over 2 x their count x 100. Every criterion is always
  scored: a film with no picture is a 0 on what the picture had to show, never a `null`.
- A **0 anywhere flags the film** (`flagged`).
- `founder_pct` = as above, beside it.
- **The bar is `film_bar_pct`** (`quality/cycle.toml` `[film]`, 80, the gallery's gate, the founder's to move): an entry
  passes at `film_pct` >= the bar with no 0; a round passes when every entry does -- and, by `quality/decisions.toml`'s
  rule (*rules not cases*, 2026-11-04), a round whose five pass and whose nine (`[film] holdout`) fall short fails.

## The weak rule

A criterion is **weak** over the entries of one table (the latest film score of each entry at this version) when

- a 0 was given in **two or more entries**, or
- its **mean is under 1.5**,

-- the question-quality rubric's rule (`RUBRIC.md`, *The weak rule*), held equal to it (`FILM_WEAK` in
`quality/film_rubric.py` against `quality/rubric.py`'s `WEAK_ZERO_ENTRIES` and `WEAK_MEAN`; a unit test holds the two
together). The founder's beats are held to the same rule per criterion, R1, R2, R3, R5.

## Versions

- **1** (spec 163, 2026-11-24): F1-F8 on the problem film (the persona, the task, today's way, every limitation, the
  pain, clearly spelled out, end to end, legible); S1-S9 on the solution film; the founder's beats on R1, R2, R3 and R5;
  `film_pct`, `founder_pct`, the flag, the weak rule. Nothing scored before it.
