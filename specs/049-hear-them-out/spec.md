# Spec 049 -- Hear them out, as the eval sees it

keel-web 073 (the page lights nothing while they speak and reads the utterance only after a 1.5 s quiet gap) and
keel-cloud 100 (the classifier reads a question-read-aloud-then-answered utterance; new case group `readaloud`).
Contract 18 unchanged.

## Rules

- **FR-1 The cases copy**: `harness/classifier_cases.py` re-copied whole from the canon's `cases.py` at the keel-cloud
  100 sha (note the sha in the docstring); the guard (`harness/classifier_guard.py`, `tests/test_classifier_guard.py`)
  runs the `readaloud` group on the stack's fake: never a confident wrong answer.
- **FR-2 The walk** (`evals/interviewer_leg.py`): one question is answered the way people do -- the question's first
  words said as a final, then within a second the option's own words as a final -- and the leg asserts one classify
  request on `window.__classified` (or the stack's log) carrying both, and that no row was checked between the two
  (the `Player` reads `aria-checked` after the first final). `Player.say()` waits for the gap (`hold` / `confirming` /
  the next question, as 048 already does).
- **FR-3 Marks**: IM19 *hears them out* (no row lit before the utterance ends; one read for a two-final utterance),
  owed on S-005 and S-006. Corpus revision bumped as 048 did.
- **FR-4 Timing**: the journeys get slower by the gap per spoken answer; raise any per-step timeout that the gap
  breaks, none other.

## Acceptance

1. `make unit` green; the guard green on the stack for `readaloud`.
2. `make eval K="s005 or s006 or s007"` green on the stack against keel-cloud 100 + keel-web 073; remote journeys
   green on staging once deployed.

## Judgement calls (decide, document in tasks.md, do not ask)

1. Which question carries the read-aloud step (prefer the yes/no "better" one: its labels share words).
