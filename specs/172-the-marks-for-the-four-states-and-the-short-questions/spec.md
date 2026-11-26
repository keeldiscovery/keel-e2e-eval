# Spec 172 -- The marks follow the batch: four orb states, one ask, finalize by hand, the solution's frames, the recap cut, the short questions

The founder's evening batch of 2026-11-25 (keel-cloud 283, 284, 285; keel-web 274, 275, 276; the decision record
`beat-orb-four-states-2026-11-25.md`). The harness reads the screens as the specs now say them; nothing here is a
judgement change.

## Today
`story_screens.py` reads `LONG_BEAT_SUB` (*Take your time. Say "that's it" when you are done.*), `THINK_LINE`, the
*What I hear* words, *Anything else?* at 20 s and again at 60 s, the done words (`DONE_WORDS`), `TURN_ASKING`;
`interviewer_screens.py` reads `STORY` (*Take your time. Pause for a few seconds when you're done, or tap Save.*) and
the *Got it. Moving on…* hold; the boxes step relies on the primary button (`boxes-yes`) and tolerates the silence
confirm; `three_surfaces.py` and `solution_surfaces.py` vendor the long question frames (`FREQUENCY_QUESTION`,
`IMPORTANCE_QUESTION`, `COMPATIBILITY_Q`, `RELATIVE_ADVANTAGE_Q`, the friction pair); the film walk's solution step
reads the idea's building screen by its steps and treats a failed build as the end.

## Rules
- **FR-1 The founder's beats (web 275).** The orb's `data-state` is one of `asking | hearing | waiting | thinking |
  paused`; the state words *Keel is asking*, *Keel is hearing you*, *Take your time*, *Keel is thinking*; the one
  ask line `beat-ask` *Anything else? Say "that's it" when you are done.* read once after 8 s of quiet (never a
  second); no *What I hear* and no founder lines on the page (their absence is a mark: `beat-no-transcript`); the
  card's rows read in order; a done word alone after the card ends the beat (the walk says *that's it* after the
  card and expects the next question); *none* on the setup beat closes at once; the folded question
  (`beat-question-fold`). `LONG_BEAT_SUB`, `THINK_LINE` and the 20 s / 60 s asks go. The walk's beats keep
  speaking their answer and `DONE_WORD` as today.
- **FR-2 The respondent's player (web 274).** The story window across a pause: the walk's strangers say the story
  in two parts with a pause under 8 s between them and end on *that's it*; the ask line once at 8 s of quiet; the
  acknowledgement `ai-story-got-it` *Got it. Thank you.*; every passage captioned (`ai-passage-caption` with the
  passage's words, the solution's opening and *Let us see it.* among them); the four states on the player's orb. The
  `STORY` sub and the *Got it. Moving on…* hold on the story are no longer read. Spoken strangers (`film_strangers.py`)
  append the done word to the story they say; typed strangers tap Save as today.
- **FR-3 The boxes (web 276).** The walk presses **Finalize the problem** / **Finalize the solution** (`boxes-yes`)
  on every board and never waits for a silence confirm (a page that moved on by itself within 10 s of the readback is
  a fault, `boxes-auto-advanced`); Keel's line *When you are done, press Finalize …* read once; the sheet's step
  two reads only *What do you want to change?*.
- **FR-4 The solution's frames (cloud 283, web 276).** The film walk's solution step reads `idea-building` as the
  problem's: the plan rows with chapters `before | task | joy` and the chips *Opening*, *What it does*, *What they
  get*; *drawing again* rows with a `note`; a build that the reader refused twice still ends on the film review with
  its frames, and a failed build is a fault only on *no picture could be drawn*. The frames' count and chapters go
  into the film table (`frames`, `chapters`); `IdeaScene.chapter` has no `solves` / `better` (a draft with one is a
  DRIFT line). Contract 96 vendored.
- **FR-5 The recap cut (cloud 283 FR-8).** On a solution link the walk expects five problem lines before the check
  (who, the limitations, the cost) and eight on a problem link; the timeline and the copilot card the same five.
- **FR-6 The short questions (cloud 285).** The vendored frames become: *How often does this happen to you?*; *Which
  of these would you most like made easier?*; *Would this fit how you work?*; *Would {name} be better than how you do
  it today?*; *You would first need {the setup}. Could you start without much trouble?* / *Could you start using
  {name} without much trouble?*; the why, the gate, the pilot ask unchanged. A link with no film keeps the old frames
  (the item's `framed`). The screener at most twelve words. The marks of the told card, the gate and the film review
  are unchanged.
- **FR-7 Versions and record.** `INTERVIEWER_MARKS_VERSION` 20; the DRIFT lines for each read that changed, with the
  spec named; the fake door (`interviewer_fake.py`) serves the new words so the stub walks pass; `runs/DRIFT.md`
  force-added as today.
- **FR-8 Nothing paid.** No eval run; unit tests on the readers against fixtures only; the main checkout's `.venv`.

## Out of scope
The film-told judge (171, unchanged); the thirty-second film budget (parked).
