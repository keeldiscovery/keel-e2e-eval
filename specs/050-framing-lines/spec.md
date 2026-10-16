# Spec 050 -- Framing lines and the beat, as the eval sees it

keel-cloud 101 (new OPENING / PROBLEM / SOLUTION words, re-rendered at no charge on old recordings) and keel-web 075
(a 2 s beat after the problem and the idea passages) and keel-web 074 (4 s quiet gap everywhere; the story's Save; a
held yes; the waveform; start tone off). Contract 18 unchanged.

## Rules

- **FR-1** `harness/interviewer_fake.py` mirrors the new OPENING / PROBLEM / SOLUTION words from keel-cloud 101
  (one source: the cloud's `PassageComposer`; copy the strings, note the sha).
- **FR-2** The walk tolerates the beat (2 s after the problem and the idea passages: the sheet shows *Take a moment.*
  and nothing listens) and the 4 s gap: the `Player`'s waits for the next clip / the next question allow it. A mark:
  IM21 *a beat after the passages* (status seen, no window opened in it).
- **FR-3** The story step: say the story, then either wait for `held` (4 s + hold) or press `ai-save`; prefer the
  wait on S-005 and the Save on S-006 so both ends are measured (IM22 *the story's Save*).
- **FR-4** The held yes: after "yes" to *Is that right?* the walk sees `data-phase="held"` with `data-unsure` false
  before the next question (IM15's measure updated; no new mark).
- **FR-5** Backfill check on the stack: a project recorded with the old words (seed one, or lock before the stack's
  cloud moves) reads the new words after the first respondent read -- if the stack cannot seed an old recording,
  skip with a note; the remote journeys on staging cover it on the founder's project.

## Acceptance

`make unit` green; `make eval K="s005 or s006 or s007"` green on the stack against cloud 101 + web 075; remote
journeys green on staging.

## Judgement calls (decide, document in tasks.md, do not ask)

1. The marks' names and the corpus bump.
