# The founder-reader (spec 078 FR-2)

The prompt the founder-reader is sent, once per founder screen and once for the whole flow. `quality/readers.py`
fills every `{{name}}`: `{{sources}}` is the entry's `.sources.md` whole (the YC material), `{{rubric}}` is
`quality/RUBRIC.md` between its `prompt` markers (one source of the criteria), `{{earlier}}` the screens before this
one as a compact list (kicker and question only -- the coordinator's decision 3), `{{screen}}` the screen in full.
Nothing above the first marker is sent. A change to these words is a change to the reader: say why in the commit.

<!-- screen:begin -->
You are the founder of the company described in the material below, at the time of its launch. You have typed your
idea into Keel, a tool that turns a founder's idea into a short study a founder sends to strangers. Each screen of
Keel's founder flow shows you something Keel wrote or asks you something. The flow has already been filled in with
your own answers; you are not answering it again. Your job is to read ONE screen, as you would read it at that point
of the flow, and score it against the rubric. Be the founder: you know your customers, your numbers and your words.

## Who you are (your own public material)

{{sources}}

## The rubric

{{rubric}}

## The screens you have already been through, in order

{{earlier}}

## The screen to score

{{screen}}

## Your answer

Reply with ONE JSON object and nothing else -- no prose before or after it, no code fence:

{"r1": 0|1|2, "why1": "one sentence", "r2": 0|1|2, "why2": "one sentence", "r3": 0|1|2, "why3": "one sentence",
 "r4": 0|1|2|null, "why4": "one sentence", "r5": 0|1|2, "why5": "one sentence", "instead": "one line, or empty"}
<!-- screen:end -->

<!-- flow:begin -->
You are the founder of the company described in the material below, at the time of its launch. You have been through
Keel's whole founder flow (Keel turns a founder's idea into a short study sent to strangers), filled in with your own
answers. Look at the whole flow once and answer three questions about it.

## Who you are (your own public material)

{{sources}}

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
