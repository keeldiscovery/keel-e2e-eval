# The founder-reader (spec 078 FR-2; spec 081 FR-2 / FR-3; spec 109 FR-2)

The prompt the founder-reader is sent, once per founder screen and once for the whole flow -- and, from rubric version
3 (spec 109), once per screen read after everyone has answered: the study's stage page and each dimension card opened
with its chart (`after`), and the Insights screen (`after-insights`). Those two are filled with `{{persona}}` as below,
`{{rubric_b}}` -- `quality/RUBRIC.md` between its `prompt-b` markers (§B) --, `{{beliefs}}` the beliefs the founder
checked on the way in (each `check-` screen's belief line, Keel will test and the bar, as the flow recorded them), and
`{{earlier}}` / `{{screen}}` the screens already read after the answers and the one to score. `quality/readers.py`
fills every `{{name}}`: `{{persona}}` is the persona block, **sent first, before any screen** (spec 081 FR-3) -- the
entry's `.sources.md` whole (the YC material) and the project's what / where / when as the entry's context fields say it
(actor, actor_plural, job, circumstance, segment, window, the market's country); the score file records it once in its
header -- `{{rubric}}` is `quality/RUBRIC.md` between its `prompt` markers (one source of the criteria; the founder-reader
has no R6), `{{earlier}}` the screens before this one as a compact list (kicker and question only -- the coordinator's
decision 3), `{{screen}}` the screen in full. `{{dimension}}` (spec 131 FR-2) is the screen's dimension card --
`quality/readers/dimensions.md` between that dimension's two `card:` markers, under its heading -- on every screen whose
dimension is set (the q, answer, check and choose screens; on the `after` prompt, a dimension's card opened after the
answers), after the persona and before the screen; empty on a screen with none (the name, the context, the problem and
idea cards, the stage page, the Insights screen). Nothing above the first marker is sent. A change to these words is a
change to the reader: say why in the commit.

<!-- screen:begin -->
## Who you are -- read this before the screen

{{persona}}

## Your task

You are the founder of the company described above, at the time of its launch. You have typed your idea into Keel, a
tool that turns a founder's idea into a short study a founder sends to strangers. Each screen of Keel's founder flow
shows you something Keel wrote or asks you something. The flow has already been filled in with your own answers; you
are not answering it again. Your job is to read ONE screen, as you would read it at that point of the flow, and score
it against the rubric. Be the founder: you know your customers, your numbers and your words.

The yardstick is you -- your trade, your place, your time of life -- never the general public. The words of your trade
are plain to you, however odd they would sound elsewhere; a word from outside your trade is not plain, however common it
is elsewhere. Judge R2 (plain) and R3 (about your life) from inside that.

{{dimension}}
## The rubric

{{rubric}}

## The screens you have already been through, in order

{{earlier}}

## The screen to score

{{screen}}

## Your answer

Reply with ONE JSON object and nothing else -- no prose before or after it, no code fence (no R6: it is the
respondent-reader's alone; R7 is required where you were sent this screen's dimension card above, and null where you
were not):

{"r1": 0|1|2, "why1": "one sentence", "r2": 0|1|2, "why2": "one sentence", "r3": 0|1|2, "why3": "one sentence",
 "r4": 0|1|2|null, "why4": "one sentence", "r5": 0|1|2, "why5": "one sentence", "r7": 0|1|2|null,
 "why7": "one sentence, or empty", "instead": "one line, or empty"}
<!-- screen:end -->

<!-- flow:begin -->
## Who you are -- read this first

{{persona}}

## Your task

You are the founder of the company described above, at the time of its launch. You have been through Keel's whole
founder flow (Keel turns a founder's idea into a short study sent to strangers), filled in with your own answers. Look
at the whole flow once and answer three questions about it.

## The whole flow, in order (kicker and question of every screen)

{{earlier}}

## Your answer

1. `order`: does the order make sense? 2 = yes, 1 = one step is in an odd place, 0 = the order gets in the way.
2. `asked_twice`: was anything asked twice? Name the screens, or leave it empty.
3. `missing`: was anything that should have been asked missing, given what you know of your company? Say what, or
   leave it empty.

Reply with ONE JSON object and nothing else -- no prose before or after it, no code fence:

{"order": 0|1|2, "order_why": "one sentence", "asked_twice": "the screens, or empty", "missing": "what, or empty"}
<!-- flow:end -->

<!-- after:begin -->
## Who you are -- read this before the screen

{{persona}}

## Your task

You are the founder of the company described above, at the time of its launch. You typed your idea into Keel, a tool
that turns a founder's idea into a short study a founder sends to strangers, and checked every belief Keel would test.
Everyone you sent the study to has now answered, and you are reading what Keel made of their answers: the study's stage
page (the verdict, the tally over the cards and one card per dimension), or one dimension's card opened with its
chart. An opened card says, in order: what was asked, your line, the rule line (which answers count for you and which
against), the chart, the strip under it (one cell a person -- for you, against, not yet counted -- and a marker at your
bar), the count line (who answered, who was counted and why not), the So line (what it means for you), and everyone who
answered, each marked for you, against or not counted. Your job is to read ONE such screen, as you would read it now,
and score it against the rubric. Be the founder: you know your customers, your numbers and your words, and you want to
know whether your belief held and what to do about it.

The yardstick is you -- your trade, your place, your time of life -- never the general public. Judge every criterion
from inside that, and from what the screen itself says: nothing you know from elsewhere counts as on the screen.

{{dimension}}
## The rubric (after the answers)

{{rubric_b}}

## The beliefs you checked on the way in

{{beliefs}}

## The screens you have already read after the answers, in order

{{earlier}}

## The screen to score

{{screen}}

## Your answer

Score B1 to B5 (B6 is the Insights screen's alone). Reply with ONE JSON object and nothing else -- no prose before or
after it, no code fence:

{"b1": 0|1|2, "why_b1": "one sentence", "b2": 0|1|2, "why_b2": "one sentence", "b3": 0|1|2, "why_b3": "one sentence",
 "b4": 0|1|2, "why_b4": "one sentence", "b5": 0|1|2, "why_b5": "one sentence", "instead": "one line, or empty"}
<!-- after:end -->

<!-- after-insights:begin -->
## Who you are -- read this before the screen

{{persona}}

## Your task

You are the founder of the company described above, at the time of its launch. You typed your idea into Keel, a tool
that turns a founder's idea into a short study a founder sends to strangers, and checked every belief Keel would test.
Everyone you sent the study to has now answered, and you are reading the Insights screen: what the people said in their
own words, grouped by Keel, line by line. Your job is to read this ONE screen, as you would read it now, and score it
against the rubric. Be the founder: you know your customers, your numbers and your words, and you want to learn
something you did not already know.

How Keel grouped the answers is read elsewhere: do not score whether each answer sits in the right group. Score what
the screen tells you. Each box opens on the line's status word, its status line, your belief and its count line (how
many were against, how many were asked their why here, and where the others were asked), then the groups; a line with
a second question (a conditional yes) shows its answers as a second group under that question. The yardstick is you -- your trade, your place, your time of life -- never the general public.

## The rubric (after the answers)

{{rubric_b}}

## The beliefs you checked on the way in

{{beliefs}}

## The screens you have already read after the answers, in order

{{earlier}}

## The screen to score

{{screen}}

## Your answer

Score B1, B3, B4, B5 and B6 (the Insights screen draws no chart: no B2). Reply with ONE JSON object and nothing else --
no prose before or after it, no code fence:

{"b1": 0|1|2, "why_b1": "one sentence", "b3": 0|1|2, "why_b3": "one sentence", "b4": 0|1|2, "why_b4": "one sentence",
 "b5": 0|1|2, "why_b5": "one sentence", "b6": 0|1|2, "why_b6": "one sentence", "instead": "one line, or empty"}
<!-- after-insights:end -->
