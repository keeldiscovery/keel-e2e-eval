# The adviser (spec 079 FR-4)

The prompt the adviser is sent, once per weak row of a cycle (`make quality-advise CYCLE=<record>`). `quality/cycle.py`
fills every `{{name}}`: `{{row}}` the row (scope, audience, dimension, screen kind), `{{criteria}}` the criteria the row
is weak on with their 0-1-2 anchors from `quality/RUBRIC.md` (one source of the criteria), `{{screens}}` the screens
that failed them -- each with its entry, its scores, the reader's whys and *instead* line --, `{{location}}` the fix
location (the design's §1, as `quality/table.py` names it), and `{{current}}` **the current text at that location**,
read from the keel-cloud checkout stack.toml names: the registry row's `founder` or `respondent` block (or its
`follow_up`), or the named section of the instruction file, or a line saying no model writes these words. `{{ladder}}`
is the design's §5 ladder. Nothing above the first marker is sent. A change to these words is a change to the adviser:
say why in the commit.

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

## Your answer

Reply with ONE JSON object and nothing else -- no prose before or after it, no code fence:

{"new_text": "the whole new text for the location", "why": "three sentences: what fails, what the edit changes, why it will hold on the other entries", "rung": "words" | "effort" | "split"}
<!-- advise:end -->
