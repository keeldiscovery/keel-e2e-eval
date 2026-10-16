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

- **FR-5 Checkboxes finish on Save** (web 073 FR-6): on a pick-two and on the advantages pick-any, a tap only ticks;
  *Save and next* (`ai-save`) shows once a row is ticked, enabled at exactly two (pick-two) / one or more (pick-any).
  The walk's tapped pick-two (the change-by-tap after Back) presses Save; `Player.save()` exists already. A mark:
  IM20 *taps wait for Save* (one tick on a pick-two: no advance within 1.5 s, Save disabled; two ticks: Save enabled).
- **FR-6 The pilot ask finishes by itself** (web 073 FR-7): a spoken yes is held 2.0 s with the ring and goes on without
  *Finish*; the walk says "yes" and waits for the thanks (no `finish()` tap on the spoken route; the tapped route
  still may). The response's pilot opt-in is asserted as before. On the recorded link (S-006's AI link) the pilot
  ask records: the fake transcript "yes" (stack/cloud.py pins it) must reach the pilot -- assert the opt-in there too.
- **FR-7 Earcons** (web 073 FR-8): the page plays two short tones through Web Audio; the eval's browser has no
  AudioContext worth asserting on -- set `window.__keelSpeech.earcons = false` in the init script, or leave it on and
  make sure nothing waits on it. No mark.
- **FR-8 Cases copy** is from keel-cloud-docs **e20d8aa** (spec 100: 18 `readaloud` cases, 170 in all; the fake's bar is
  137 of 152 + 17 of 18, never a confident wrong).

## Acceptance

1. `make unit` green; the guard green on the stack for `readaloud`.
2. `make eval K="s005 or s006 or s007"` green on the stack against keel-cloud 100 + keel-web 073; remote journeys
   green on staging once deployed.

## Judgement calls (decide, document in tasks.md, do not ask)

1. Which question carries the read-aloud step (prefer the yes/no "better" one: its labels share words).
2. The marks' names (IM19, IM20) and where the pilot's auto-finish is observed.
