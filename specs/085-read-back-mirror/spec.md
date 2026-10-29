# Spec 085 -- The harness reads the read-back as keel-cloud 149 writes it

keel-cloud 149 (merged 2026-10-29, cloud master `73426a67`) changed the *Keel understands* sentence from one comma-joined
run to two sentences, *{Segment}. When {when}, they want to {what}, counting the last {window}.*, made code's drawn
condition keep the founder's subject (*have jobs that run on Procore or ACC*, never *run on Procore or ACC*; an
organisation's participle qualifier drawn as *work at a startup that banks with ...*), reads a list *A, B or C* as one
part, and breaches a qualifier dropped from both the core and the condition. The harness mirrors the old shape
(`harness/vectors_script.py` `sentence()`, `harness/qualifiers.py`), and the scripted journeys assert the card's sentence
on the wire (`evals/corpus_scenario.py` `leg_context`, strict on a scripted entry; S-005/006/007/014/015/016 where they
read the card). Until this spec, a journey on a cloud at 149 or later reads a sentence the mirror does not compose.

## Rules

- **FR-1 The mirror.** `vectors_script.sentence(core, condition, circumstance, job, window)` composes 149 FR-2's shape:
  the segment as `qualifiers.segment` says it (146 FR-2, 148 FR-2 unchanged), a capital and a full stop; then
  `with_when(circumstance)` with its first letter raised, a comma, *they want to* and the job -- *they {job}* where the
  job opens with *want to*, *need to*, *try to*, *have to* or *must*; *they are trying to ...* on *trying to* / *are
  trying to*; *they want to ...* on a bare *to ...*; a job already opening *they* kept -- then *, counting the last
  {window}.* or *.* (spec 135's scope rule as today). The docstring names 149.
- **FR-2 The drawn condition.** `harness/qualifiers.py` mirrors 149 FR-3 where the harness draws or checks a condition:
  a *whose {thing} {verb} ...* part draws *have {thing} that {verb} ...* (singular *have a {thing} that ...*); the
  tool branch (*bank with*, *run on*, *work on*) only where the people are the subject; an organisation's qualifier by
  participle or relative clause draws 131's frame on the head noun (*work at a startup that banks with Mercury, Brex or
  similar*); a list whose items before the closing *or* / *and* are one to three words and start no clause of their
  own stays one part. The builder copies 149's judgement calls from keel-cloud `specs/149-read-back-reads-once/tasks.md`
  and names any the harness does not need.
- **FR-3 The pins.** Every journey and unit test that asserts a card sentence, a segment line or a drawn condition is
  re-pinned to the new words with why: `tests/` on `sentence()` and `qualifiers`; the corpus scenario's strict compare;
  the six journeys' recorded expectations; the gallery fixtures that carry a sentence (`tests/fixtures/gallery/*`), as
  data only where a test reads them. 17-expanse's *have 100 or more GPUs* stays as 149 left it (the amount rule did not
  move) and is named.
- **FR-4 Decided before.** `quality/decisions.toml` D-2026-10-29-01 gains `merged = "73426a67"` (spec 087's duty).

## Acceptance

`make unit` green with ZERO failed (master's counts as the last spec's tasks.md records them); then, on the local stack
at cloud `c1da0d05` or later and web master, `make eval K=s005` and `K=s007` green (the card asserted with the new
shape; the S-007 chip reading the settled condition as 084 pinned it). Build on the founder's word (the decisions of
2026-10-29).
