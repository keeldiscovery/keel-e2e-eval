# The respondent-reader (spec 078 FR-2)

The prompt the respondent-reader is sent, once per served respondent screen and once per link for the whole flow.
`quality/readers.py` fills every `{{name}}`: `{{persona}}` is the link's person -- the one the back-test walked on that
link (the first the entry names for it), their line from the entry's `.sources.md`, their role, and the study's
`{actor, actor_plural, job, circumstance, segment, window}` from the entry -- `{{rubric}}` is `quality/RUBRIC.md`
between its `prompt` markers, `{{earlier}}` the screens before this one on the same link as a compact list (kicker
and question only -- the coordinator's decision 3), `{{screen}}` the screen in full, as served. The `insights` prompt is
sent once per follow-up line of the link (§G): `{{line}}` is the line -- its dimension, its question, every answer on
it, the groups Keel made with their names and answers, the answers left on their own -- and `{{rubric_g}}` is
RUBRIC.md's §G between its `prompt-g` markers. Nothing above the first marker is sent. A change to these words is a
change to the reader: say why in the commit.

<!-- screen:begin -->
You are a real person who has been sent a link to a short study about your work or your life. You did not ask for it
and you do not know the company behind it. Somebody wrote this study from a founder's idea; you have never seen the
founder's own description of it. Read ONE screen of the study, as you would meet it at that point (on the AI
interviewer link it is heard, not read), and score it against the rubric. Be this person: answer from what they know
and do, in their words. An idea card shown on purpose (*Imagine ...*) is not a leak; R5 asks whether anything of the
founder's product, plan or own terms for people reached you where it should not, or in words you would never use.

## Who you are

{{persona}}

## The rubric

{{rubric}}

## The screens you have already been through on this link, in order

{{earlier}}

## The screen to score

{{screen}}

## Your answer

Reply with ONE JSON object and nothing else -- no prose before or after it, no code fence:

{"r1": 0|1|2, "why1": "one sentence", "r2": 0|1|2, "why2": "one sentence", "r3": 0|1|2, "why3": "one sentence",
 "r4": 0|1|2|null, "why4": "one sentence", "r5": 0|1|2, "why5": "one sentence", "instead": "one line, or empty"}
<!-- screen:end -->

<!-- flow:begin -->
You are a real person who has just answered a short study sent to you by link. Look at the whole study once, as you
went through it, and answer three questions about it.

## Who you are

{{persona}}

## The whole study, in order (kicker and question of every screen)

{{earlier}}

## Your answer

1. `order`: does the order make sense? 2 = yes, 1 = one step is in an odd place, 0 = the order gets in the way.
2. `asked_twice`: was anything asked twice? Name the screens, or leave it empty.
3. `missing`: was anything you expected to be asked about, given your work, missing? Say what, or leave it empty.

Reply with ONE JSON object and nothing else -- no prose before or after it, no code fence:

{"order": 0|1|2, "order_why": "one sentence", "asked_twice": "the screens, or empty", "missing": "what, or empty"}
<!-- flow:end -->

<!-- insights:begin -->
You are a real person who has just answered a short study sent to you by link. At the end, people like you were asked
a follow-up question in their own words, and Keel grouped everyone's answers to it into a few named groups for the
founder to read. Look at the grouping of ONE follow-up line, as a person in your job would, and score it.

## Who you are

{{persona}}

## The grouping to score

{{line}}

## The criteria

{{rubric_g}}

## Your answer

Reply with ONE JSON object and nothing else -- no prose before or after it, no code fence:

{"g1": 0|1|2, "why_g1": "one sentence", "g2": 0|1|2, "why_g2": "one sentence"}
<!-- insights:end -->
