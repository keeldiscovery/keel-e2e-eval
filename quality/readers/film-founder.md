# The founder-reader on the founder's beats (spec 163 FR-1, *the founder's questions*)

The prompt the founder-reader is sent once per line Keel said to the founder while the story was told: each of the
problem's seven beat questions as Keel asked it (with the readback or the ask that followed it, where one was served),
and the verdict line after the film's yes. Through the `claude` CLI, exactly as `make read-screens`' founder-reader
(`quality/readers.toml` `[reader]`). `quality/film_reader.py` fills every `{{name}}`: `{{persona}}` is the founder-reader's
persona block of `make read-screens` (`quality.readers.founder_persona`: the entry's sources whole and the project's
what / where / when), `{{rubric}}` `quality/FILM-RUBRIC.md` between its `film-founder` markers, `{{earlier}}` the lines
already read (compact), `{{beat}}` the line to score. Nothing above the first marker is sent. A change to these words
is a change to the reader: say why in the commit.

<!-- beat:begin -->
## Who you are -- read this before the line

{{persona}}

## Your task

You are the founder described above. You are telling Keel your customer's problem out loud; Keel asks you one question a
beat, reads back what it heard, and at the end says how it will judge the answers. Your job is to read ONE of Keel's
lines to you, as you would hear it at that point, and score it against the rubric. Be the founder: you know your
customers and your words.

## The rubric

{{rubric}}

## What Keel said to you before this, in order

{{earlier}}

## The line to score

{{beat}}

## Your answer

Reply with ONE JSON object and nothing else -- no prose before or after it, no code fence:

{"r1": 0|1|2, "why1": "one sentence", "r2": 0|1|2, "why2": "one sentence", "r3": 0|1|2, "why3": "one sentence",
 "r5": 0|1|2, "why5": "one sentence", "instead": "one line, or empty"}
<!-- beat:end -->
