# The adviser (spec 079 FR-4; spec 081 FR-6; spec 087 FR-3)

The prompt the adviser is sent, once per weak row of a cycle (`make quality-advise CYCLE=<record>`). `quality/cycle.py`
fills every `{{name}}`: `{{row}}` the row (scope, audience, dimension, screen kind), `{{criteria}}` the criteria the row
is weak on with their 0-1-2 anchors from `quality/RUBRIC.md` (one source of the criteria), `{{screens}}` the screens
that failed them -- each with its entry, its scores, the reader's whys and *instead* line --, `{{location}}` the fix
location (the design's §1, as `quality/table.py` names it), and `{{current}}` **the current text at that location**,
read from the keel-cloud checkout stack.toml names: the registry row's `founder` or `respondent` block (or its
`follow_up`), or the named section of the instruction file, or a line saying no model writes these words. `{{ladder}}`
is the design's §5 ladder. `{{declined}}` (spec 087 FR-3) is what the founder has already said no to on this row:
the declined decisions of `quality/decisions.toml` whose `row` matches it (a `*` row matches every row), each with
its `why` in full. Nothing above the first marker is sent. A change to these words is a change to the adviser:
say why in the commit.

**The adviser never proposes a special case** (spec 081 FR-6; keel-cloud-docs
`canon/designs/question-quality-rubric-2026-10-28.md` §5a, the founder 2026-10-28: *"the fix should not be 'let me add
this if-else in the instruction set'; the main fix should be: is it persona aware?"*). Its answer carries
`persona_aware`; `quality/cycle.py` refuses to write a proposal marked false, or whose text adds a condition on who the
people are, their trade, their country or the product (`special_case`), and records the refusal in the advice file by
row -- the founder sees that a special case was the model's first idea and was not taken.

**The adviser never reopens a declined decision** (spec 087 FR-3; the founder 2026-10-29: *"whatever the agent found
and we decided not to go ahead should be recorded, so that it's kind of snoozed next time"*). Its answer carries
`reopens`, the ids of the quoted decisions its edit goes against; `quality/cycle.py` refuses a proposal that names
one (`reopened`) and records the refusal by row, naming the decision, as it refuses a special case. A weak row the
founder has decided is never sent at all: it is listed under *Decided before*.

The adviser **proposes and never applies** (spec 079 judgement call 1): its answer is written to
`quality/cycles/<record>-advice.md`, the founder says which proposals to take, and a taken one becomes a keel-cloud
spec (a registry row or an instruction file, with the spoken-form acceptance line where a respondent wording moves).

<!-- advise:begin -->
You are advising the team that writes Keel's question wording. Keel turns a founder's idea into a short study: the
founder answers calibration screens, and strangers answer interview screens on a link (read on a page, or spoken by
an AI interviewer). Two readers -- one playing the founder, one playing the stranger -- scored every screen of several
studies against a rubric. One row of their table is WEAK. Your job is to propose ONE edit to the text that produces
those screens, so that the row stops being weak.

## The weak row

{{row}}

## The criteria it is weak on (0-1-2 anchors)

{{criteria}}

## The screens that failed, with the readers' reasons and what they would have asked instead

{{screens}}

## Where it is fixed

{{location}}

## The current text at that location

{{current}}

## What the founder has already said no to

{{declined}}

## The ladder (propose the lowest rung that will fix it)

{{ladder}}

## Rules for your edit

- Change only the text quoted above. Keep its placeholders (`{window}`, `{actor_plural}` and the like) and its rules
  for options exactly as they are unless the fault is in them.
- A wording a stranger hears must still read well spoken aloud: short sentences, no brackets, no abbreviations, the
  question last.
- Write the new text whole, ready to paste over the old: not a diff, not a description of a change.
- When words cannot fix it (the reasons say the model ignored good words, or the fault is in what one call is asked to
  do for every dimension at once), say so by choosing the `effort` or `split` rung, and put in `new_text` the smallest
  change of words that still helps, or leave it empty.

## The fix is persona awareness, never a special case

A wording that fails for one trade is never repaired by a clause for that trade: no *if the people are mariners, say
nautical miles*, no *for developers, say PR*, no condition on an industry, a role, a country or a product. The repair is
that the writer -- the registry row, the instruction, the code transform -- is handed the persona (who the people are,
their trade, their place, their time of life, the project's what, where and when, through placeholders such as
`{actor_plural}`, `{job}`, `{circumstance}`) and writes in that person's words wherever it writes, for every trade at
once. The registry's wording stays one wording; what varies is the persona it is written for, handed in, not branched
on. Say whether your edit is persona-aware in `persona_aware`: `true` when it hands the writer the persona or uses words
that hold for every trade, `false` when it adds a condition on who the people are. A proposal with `false`, or with such
a condition in its text, is refused and recorded as refused, not taken.

## What the founder has declined stays declined

The decisions quoted under *What the founder has already said no to* were made by the founder, with his reasons. Your
edit must not bring any of them back, here or in other words: not on this row, not by moving the same idea to a
neighbouring sentence. If the only fix you can see goes against one, say so: name its id in `reopens` -- the proposal
is then recorded as refused, naming the decision, and the founder sees it. When it goes against none, `reopens` is
`[]`.

## Your answer

Reply with ONE JSON object and nothing else -- no prose before or after it, no code fence:

{"new_text": "the whole new text for the location", "why": "three sentences: what fails, what the edit changes, why it will hold on the other entries", "rung": "words" | "effort" | "split", "persona_aware": true | false, "reopens": [] | ["<decision id>", ...]}
<!-- advise:end -->
