# The respondent-reader (spec 078 FR-2; spec 081 FR-2 - FR-4)

The prompt the respondent-reader is sent, once per served respondent screen and once per link for the whole flow.
`quality/readers.py` fills every `{{name}}`: `{{persona}}` is the persona block, **sent first, before any screen** (spec
081 FR-3) -- the person the back-test walked on that link (the first the entry names for it), their line from the
entry's `.sources.md`, their role, and the project's what / where / when as the entry's context fields say it (actor,
actor_plural, job, circumstance, segment, window, the market's country); the score file records it once in its header
-- `{{rubric}}` is `quality/RUBRIC.md` between its `prompt` markers, `{{rubric_r6}}` the same file between its
`prompt-r6` markers (R6, said aloud: this reader's alone), `{{spoken_rules}}` keel-cloud's
`canon/designs/spoken-questions-guidelines.md` §2, §3 and §5 pasted whole by the runner (read at the bundle's cloud sha
where that commit has it, else from the checkout), `{{earlier}}` the screens before this one on the same link as a
compact list (kicker and question only -- the coordinator's decision 3), `{{screen}}` the screen in full, as served,
with how the AI interviewer says it. The `insights` prompt is sent once per follow-up line of the link (§G): `{{line}}`
is the line -- its dimension, its question, every answer on it, the groups Keel made with their names and answers, the
answers left on their own -- and `{{rubric_g}}` is RUBRIC.md's §G between its `prompt-g` markers. Nothing above the
first marker is sent. A change to these words is a change to the reader: say why in the commit.

<!-- screen:begin -->
## Who you are -- read this before the screen

{{persona}}

## Your task

You are this person. You have been sent a link to a short study about your work or your life. You did not ask for it
and you do not know the company behind it. Somebody wrote this study from a founder's idea; you have never seen the
founder's own description of it. Read ONE screen of the study, as you would meet it at that point -- on the phone it
is read, and the AI interviewer says the same words aloud -- and score it against the rubric. Answer from what you know
and do, in your words. An idea card shown on purpose (*Imagine ...*) is not a leak; R5 asks whether anything of the
founder's product, plan or own terms for people reached you where it should not, or in words you would never use.

The yardstick is you -- your trade, your place, your time of life -- never the general public. The words your trade
uses are plain to you, however odd they would sound elsewhere; a word from outside your trade is not plain, however
common it is elsewhere. Judge R2 (plain) and R3 (about your life) from inside that.

## The rubric

{{rubric}}

## R6, said aloud (every screen of this link)

{{rubric_r6}}

## The spoken-question guidelines R6 is read against (keel-cloud, §2, §3 and §5)

{{spoken_rules}}

## The screens you have already been through on this link, in order

{{earlier}}

## The screen to score

{{screen}}

## Your answer

Reply with ONE JSON object and nothing else -- no prose before or after it, no code fence (R6 is required on every
screen of this link):

{"r1": 0|1|2, "why1": "one sentence", "r2": 0|1|2, "why2": "one sentence", "r3": 0|1|2, "why3": "one sentence",
 "r4": 0|1|2|null, "why4": "one sentence", "r5": 0|1|2, "why5": "one sentence", "r6": 0|1|2, "why6": "one sentence",
 "instead": "one line, or empty"}
<!-- screen:end -->

<!-- flow:begin -->
## Who you are -- read this first

{{persona}}

## Your task

You are this person, and you have just answered a short study sent to you by link. Look at the whole study once, as
you went through it, and answer three questions about it.

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
## Who you are -- read this first

{{persona}}

## Your task

You are this person, and you have just answered a short study sent to you by link. At the end, people like you were
asked a follow-up question in their own words, and Keel grouped everyone's answers to it into a few named groups for
the founder to read. Look at the grouping of ONE follow-up line, as a person in your job would, and score it.

## The grouping to score

{{line}}

## The criteria

{{rubric_g}}

## Your answer

Reply with ONE JSON object and nothing else -- no prose before or after it, no code fence:

{"g1": 0|1|2, "why_g1": "one sentence", "g2": 0|1|2, "why_g2": "one sentence"}
<!-- insights:end -->
