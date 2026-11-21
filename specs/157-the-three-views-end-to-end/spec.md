# Spec 157 -- The three views, end to end: the spoken problem, the solution and the money chain, on text, avatar and copilot, with nothing bought

The founder, 2026-11-21: build everything first, run the e2e once, hand over for manual testing, then run all the
scenarios. The harness walks the new screens of keel-web 241/242/243 against keel-cloud 259/260/261 on the eval
stack, across the three views, and buys nothing: HeyGen stays on the stack's fake avatar, Keel AI's voice is the
cloud's `FakeSpeech`, the copilot leg feeds a recorded answer in place of the Meet audio (the copilot bench's way),
and the transcriber runs on the stack's fake for the founder's turns (typed text in, the same text out). The readings
are real and run once. Marks as the current gallery's; no new score.

## Rules

- **FR-1 The founder's legs.** (a) Problem: a new project, the seven turns by the typed path (the harness types what
  the founder would say), the boxes' yes, the build to `ready`, the story's yes, the window screen, Prevalence; the
  project's context and statement equal the typed path's for the same words (the 259 acceptance pair). (b) Solution:
  from a solution start with no problem project: create, the problem leg to its yes, the return with it picked, the
  brand with a colour, the three turns, the boxes, the story, Compatibility with Relative advantage pre-filled.
  (c) Money: from a money start with nothing: problem, solution, return twice, the persona screen pre-filled, lock
  once (the ledger shows one project charge), the links.
  (d) The defined project: the problem project of (b), opened from the list, resumes at the window screen,
  calibrates, locks with enough credits and sends a link; with too few credits it refuses as today.
- **FR-2 The stranger's legs, three views each.** For each of (a), (b), (c): the text view walked as today's harness
  walks a link, asserting the story card, the gate or anchor or the third-person check, the chips on the story
  question, the lettered bubbles, the voice bar's `clipId` on every card; the avatar view through the fake avatar,
  asserting the hand-over card, Daphne's return, no Type instead, Back on every question; the copilot view through
  the bench with a recorded answer, asserting the strips in order, the two story moments, the grown window's state
  and its return. A No on the gate, the anchor and the third-person check ends the interview in all three.
- **FR-3 One run.** `make e2e-157` runs the lot once against the stack and writes `runs/157/<sha>/report.md` with
  every assertion named; a failure names the screen and the view. No gallery, no noise check, no paid cycle.

## Acceptance
- The report lists FR-1 (a)-(d) and FR-2's nine legs green on the staging-bound shas, with the ledger showing only the
  locks as charges and no HeyGen or OpenAI call in the stack's logs.
