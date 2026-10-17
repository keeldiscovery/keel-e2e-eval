# Spec 051 -- The one follow-up, and speak or type, as the eval sees it

keel-cloud 103 (the ladder in the registry; `Interview.followUps[]`; `InterviewResponse.followUp`; `ClipKind.FOLLOW_UP`
rendered at lock and backfilled free; `transcribe` on every link kind with `maxSeconds`; the consent line) and
keel-web 076 (`SpeakOrTypeBox` on the story and the follow-up; `FollowUpScreen` on the text link; the AI player's
follow-up window; Try it yourself). Design of record: keel-cloud-docs
`canon/designs/report-and-follow-up-design-2026-10-17.md` §2, §5, §6, §9, §11. **Contract 18 -> 19** (the
interview side; 052 takes the standings side). Field and selector names below are the design's; where 076 settles a
selector it is marked *as 076 defines*.

## Rules

- **FR-1 Contract 19** wherever 18 is pinned (`harness/`, `stack/`, README, AGENTS, the corpus marks' header). The
  stack stays free and offline (048 FR-2): fake transcriber, no key, `FakeClassifier`.
- **FR-2 The ladder, one source.** `harness/interviewer_fake.py` gains `LADDER`: the eight rungs of design §2 in order
  -- `(dimension, against codes, text template, spoken wording)` -- copied from keel-cloud 103's registry `follow_up`
  blocks (note the sha), and `first_rung(picks, link_kind)` that walks it the way the cloud does (an escape or a chip
  is not against; COMMERCIAL_B2B walks the commercial rungs only). `tests/test_interviewer_marks.py` holds the copy to
  the registry export the run carries (`export/`, as `brief_facts` does for the cards): every wording and every
  `against` set equal, so a cloud edit fails here first.
- **FR-3 The fakes.**
  - The stack's fake transcriber answers the story and the follow-up on **text** links too (103 opens `transcribe`
    to every link kind): `KEEL_INTERVIEWER_FAKE_TRANSCRIPT` stays one word (`yes`) for the pilot's yes; a story or
    follow-up blob is told apart by `maxSeconds` (60 / 120) -- the fake hands back a fixed sentence per cap, in
    `stack/cloud.py` beside the pin (`KEEL_INTERVIEWER_FAKE_STORY`, `..._FOLLOW_UP`, one sentence each, no name, no
    digit). If 103 keys the fake on something else, follow 103 and note it.
  - `KINDS` gains `FOLLOW_UP` after `IS_THAT_RIGHT`; `UNSPOKEN` gains it (never in the spoken order; played only
    when the walk finds a rung); `role_sets` / `spoken` keep it out of IM3's order. Per role the fake renders one
    FOLLOW_UP clip per rung the link walks (five on FULL, three on COMMERCIAL_B2B), script *One last thing.* + the
    rung's spoken wording; `fake_seconds` as every clip.
  - The themes fake is 052's.
- **FR-4 The text walk** (`harness/vectors_screens.py` `Interview`): after the last item and before *Send my
  answers* / the pilot, `_follow_up(person, interview)` -- reads the screen only when `first_rung` says one is owed:
  kicker *One last thing* (`.iv-kicker`), the question (`h1.iv-q`) equal to the served template filled from the
  person's own picks (the walk fills the placeholders itself, from `Interview.followUps[]` and the item's labels; no
  second source), the note, the box (`SpeakOrTypeBox`, *as 076 defines*: a `textarea` with the *Speak* pill
  `data-testid="iv-speak"`), *Continue*, *Skip this one*. The person either types the corpus's follow-up line
  (`person.follow_up`, new on `corpus_script.Person`, one sentence; absent -> *Skip this one*). The POSTed body's
  `followUp` is asserted: `dimension` = the rung the walk computed, `text` the words typed, `how` TYPED, `skipped`
  as pressed; **absent** when no rung is owed (every pick supporting). On S-005 one person skips, one types; on S-006
  the PRIMARY and the COMMERCIAL_B2B walks each type one.
- **FR-5 Speak or type on the story** (text link, one person per scenario): T1 -> T2 -> T3 -> T4 of design §6 on
  the `SpeakOrTypeBox`: the pill tapped (`iv-speak`), the seam's recorder started (`__recordStarts`, 050's), the
  listening card shown (`data-testid="iv-listening"`, the waveform `ai-mic-on`, the clock *as 076 defines*), ended by
  the 4 s quiet (the seam's analyser silence) once and by *Done* (`iv-done`) once across the two scenarios, *Writing
  it down…* seen, the fake's story sentence **appended** to the textarea's value (caret at the end: `selectionStart`
  equals the length), the footer *Heard you. Fix anything that's wrong.* and the pill now *Add more*; the POST
  carries `story` = the textarea's value and no audio. T6: one walk under a refused microphone (`__keelSpeech.mic`
  acquire false): no pill, the footer line *The microphone is off, so it's typing on this one.*, typing as today.
  The microphone is asked for only on the tap: `__recordStarts` and `getUserMedia` (the seam's `mic.acquire` count)
  are 0 before the pill.
- **FR-6 The AI walk** (`evals/interviewer_leg.py` `_Walk`): after the last item's hold and before the pilot ask,
  `follow_up(entry)` -- the FOLLOW_UP clip of the computed rung plays (the timeline's clip ref equals
  `clips.followUp[dimension]`), the sheet shows the filled text form (`ai-where` or *as 076 defines*), the window is
  the story's path (`AI_STATUS.story` words, no `classify` call, `ai-save` present), ended by the pause on one link
  and by *Save and next* on the other (as IM22); the transcribe call carries `maxSeconds: 120`; the response's
  `followUp` has `how` SPOKEN (browser path) or RECORDED (the recorded link), the fake's sentence as `text`. A walk
  whose picks support every rung sees **no** FOLLOW_UP clip and goes straight from the last hold to the pilot ask.
  Try it yourself plays it too (`_dry_run_on_screen`), writes nothing (IM8).
- **FR-7 The cap and the quiet, recorded path**: on the recorded link's follow-up the window ends 4.0 s after the
  last sound (the seam's level) and never past 120 s; one window on S-006 is left silent to see the question skipped
  (`skipped: true`, no didn't-catch clip, the pilot ask next).
- **FR-8 Backfill**: a recording seeded without FOLLOW_UP clips (050 FR-5's stand-in, widened: drop the kind) gains
  one DONE clip per rung per role on the first respondent read, no ledger row (IM1 still one pair), READY throughout.
- **FR-9 Consent**: the intro's consent block carries the new participant line (design §9) on every link kind --
  *with your name as they have it, and may be quoted to them in their report* present, *Nothing here asks for your
  name* absent; a plain assertion in both walks, no mark.
- **FR-10 Marks** (`evals/interviewer_marks.py`, `INTERVIEWER_MARKS_VERSION` 4 -> 5), each owed on the short form:
  - IM23 *asked on the first rung against*: on every walk the FOLLOW_UP clip played (AI) or the screen shown (text)
    is exactly `first_rung(picks)`, and none when there is none; the response's `followUp.dimension` equals it.
  - IM24 *skipped honoured*: a skip (pressed, or 120 s of silence) posts `skipped: true` with no text, the pilot
    ask follows.
  - IM25 *two minutes, four seconds*: the recorded follow-up window ends within 4,000 +/- 500 ms of the last sound,
    or at 120 s; the browser path ends on the pause or Save as the story does (IM22's measure reused).
  - IM26 *speak or type*: T1 -> T4 observed on a text link; the POSTed story equals the box after the append; 0
    microphone acquisitions before the pill; T6 observed once.
  - IM27 *the follow-up clips*: one FOLLOW_UP clip per rung per role in the stored recording, each saying *One
    last thing.* + the registry's spoken wording, none in the spoken order; the backfill of FR-8.
- **FR-11 Journeys**: S-005 (one role, FULL), S-006 (PRIMARY + COMMERCIAL_B2B, the recorded link) and S-007 gain
  FR-4..FR-9; the corpus people gain `follow_up` lines (`harness/corpus_script.py`, `evals/preludes.py`) chosen so
  each scenario has at least one person per failing rung of its entry and at least one person owed nothing.

## Acceptance

1. `make unit` green (2,391 / 53 skipped before): the ladder copy held to the registry export; `first_rung` on the
   corpus people against a hand-worked table (one case per rung, the escape, the chip, the commercial link, nothing
   owed); the fakes' lines; the five marks each with a seeded fault.
2. `make eval K="s005 or s006 or s007"` green on a fresh stack against keel-cloud 103 + keel-web 076; IM23–IM27
   measured and met on S-006, IM23 / IM24 / IM26 on S-005; counts in tasks.md.
3. Remote journeys green on staging once 103 + 076 are deployed there; DRIFT entries for anything the stack shows
   the cloud or the page doing otherwise (next number #92).

## Judgement calls (decide, document in tasks.md, do not ask)

1. Whether the walk fills the follow-up's placeholders from the served labels or trusts the page's own text (prefer:
   fill them, assert equality -- the page composing per person is the thing under test).
2. Which S-006 window is left silent for IM24, and whether the 120 s wait is shortened through the seam's
   `recordCapMs` (prefer the seam, note the real cap is asserted on the request's `maxSeconds`).
3. The marks' names; the corpus revision stays (no screen schema moves; `MARKS_VERSION` is 052's to bump).
