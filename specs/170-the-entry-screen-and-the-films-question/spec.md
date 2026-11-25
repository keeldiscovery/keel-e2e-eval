# Spec 170 -- The harness mirrors the entry screen, the verdict gone and the film's question

keel-web 266 (the respondent's entry screen: one line, *Test your mic* -> *Your mic works.* -> **Begin**; the mic passes
on sound), 268 (the verdict card gone: the film's yes goes to the window page / the pilot ask) and 269 (the film's
question *Does this film show the problem accurately?* / *Does this film show {name} accurately?*, Yes / No, the
`film-fix` sheet). The harness pins the old words and screens: `harness/interviewer_screens.py` (`SAY_HELLO`,
`MIC_LABEL`, `START_THE_INTERVIEW`, the *Heard: {text}* line ~462, `ai-mic-heard`), `harness/story_screens.py`
(`VERDICT_CARD`, `VERDICT_ASK`, `STORY_ASK` ~416-430, the walks ~1317-1360 and ~2309 that wait for the verdict and
answer it). Eval side; nothing paid.

## Rules
- **FR-1 The entry screen.** The strangers' walk and the screens reader press *Test your mic*, wait for `ai-mic-heard`
  (*Your mic works.*) and press **Begin** (`ai-start`); the hello's words are no longer read or asserted (the fake mic
  still makes sound); `MIC_LABEL`, `SAY_HELLO` and the *Heard:* reader go; a screen still showing the old words is a
  DRIFT finding (capture), not a fault of the walk.
- **FR-2 The verdict gone.** The founder stub's walks no longer wait for `story-verdict` or say yes to `VERDICT_ASK`;
  after the film's yes they expect the window page (problem) or the pilot ask (solution). The old pins are removed.
- **FR-3 The film's question.** `STORY_ASK` becomes the new words (the problem's and the solution's with the brand's
  name); the stub founder answers **Yes** (spoken, as today); the `film-fix` sheet is never opened by the stub (the
  film's pictures are the judge's to read, not to fix).
- **FR-4 Tests.** The screens tests, `test_three_views_157.py`, `test_interviewer_screens.py`, the story-screens tests:
  the new words and the new steps; `make unit` green on the base's known reds only.
- **FR-5 The respondent-question rule.** The harness writes no respondent words; everything here is read from the
  screens.

## Acceptance
- `DOOR=fake` journeys on a stack with keel-web 266/268/269 walk the entry screen and the founder's film without a
  wait on the old screens.
