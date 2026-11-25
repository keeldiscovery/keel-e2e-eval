# The told-reader on the told card (spec 171)

Two prompts, both sent through the film reader's door (`quality/readers.toml` `[film_reader]`: the Anthropic API, the
film reader's model and effort) by `harness/film_told.py`:

- **`truth`** -- one call a story (FR-1): one stub stranger's story after their yes, read from its text alone against
  the founder's board, independent of Keel's reading. `{{board}}` is the founder's board (the way, the limitations
  numbered, the pain), `{{story}}` the story as the stranger said it. The answer is the ground truth
  (`told_truth.json`).
- **`card-before-images` / `card-after-images`** -- one call a card (FR-3): the told card as Keel served and drew it,
  beside the truth. `{{persona}}` the persona card (`quality.film_reader.persona_card`), `{{board}}` as above,
  `{{truth}}` every story with the truth's reading, `{{served}}` the card as served (`BriefFacts.problem.told`, the
  amber rows numbered), `{{drawn}}` the card's and the three popups' words as drawn, `{{notes}}` what code already found
  on the drawn words, `{{rubric}}` `quality/FILM-RUBRIC.md` between its `film-told` markers; the screenshots between
  the two parts.

Nothing above the first marker is sent. A change to these words is a change to the reader: say why in the commit.

<!-- truth:begin -->
## Your task

You read ONE person's account of a time something happened to them, and you mark what it says against a founder's
board. Read only the account below: never guess what the person meant beyond their words, never fill a box the account
does not fill.

## The founder's board

{{board}}

## The account (the person's own words, after they said it happened to them)

{{story}}

## What to mark

- `limits`: the numbers of the founder's limitations the account says happened to them that time, by meaning, not by
  shared words; `[]` where none.
- `own`: limitations the account names that match none of the founder's (at most two, each under ten words, in plain
  words); `[]` where none.
- `way`: `same` where the account says they did it the founder's way (by meaning), `differs` where it says another
  way, `none` where it does not say how they did it; `way_said`: how they did it, under thirteen words, or "".
- `pain`: `same` where what it cost them is the founder's pain (by meaning), `differs` where it is another cost,
  `none` where no cost is said; `pain_said`: the cost, under ten words, or "".
- `occasion`: `real` where the account tells one real time it happened (a when, a what, a what next), `guess` where it
  is general, hypothetical or a reason not to tell.
- `why`: one sentence on the occasion's call.

## Your answer

Reply with ONE JSON object and nothing else -- no prose before or after it, no code fence:

{"limits": [1, 2], "own": ["..."], "way": "same|differs|none", "way_said": "...", "pain": "same|differs|none",
 "pain_said": "...", "occasion": "real|guess", "why": "one sentence"}
<!-- truth:end -->

<!-- card-before-images:begin -->
## Who the card is for

{{persona}}

## The founder's board

{{board}}

## What each stranger told, as the truth reads it (independent of Keel)

{{truth}}

## The card as Keel served it (`What they told you`)

{{served}}

## The card and three people's popups as drawn

{{drawn}}

## What code already found on the drawn words

{{notes}}

The screenshots follow: the card, then each popup's Insights tab.
<!-- card-before-images:end -->

<!-- card-after-images:begin -->
## The rubric

{{rubric}}

## Your task

You are the founder above, reading the card after the strangers answered. Two things:

1. For every amber row (`Theirs, not on your board`) numbered above, say which of the stories above say it (their
   numbers) and whether it is in fact one of the founder's own rows reworded (`"way"`, `"limit <n>"`, `"pain"`) or
   none (`null`).
2. Score T4 (legible) 0, 1 or 2 with one sentence of why, and an `instead` line where it is under 2: what the card
   should have said instead, in the founder's words.

## Your answer

Reply with ONE JSON object and nothing else -- no prose before or after it, no code fence:

{"theirs": [{"row": 1, "stories": [1, 3], "founders": null}], "t4": 0|1|2, "why4": "one sentence", "instead4": "one
line, or empty"}
<!-- card-after-images:end -->
