# Spec 159 -- The orb, walked: the harness on keel-cloud 267 + keel-web 253/254

The founder, 2026-11-23: one respondent flow, the AI avatar's screen with the orb in the face's place, speak or tap,
nothing typed; the orb and the face speak the same passages from the same Nova audio; the film first, then the
interviewer. keel-cloud 267 (master `8bd57d6f`, contract 84) serves `Interview.interviewer` on every TEXT and
AI_INTERVIEWER link with `speaker` ORB | AVATAR, the orb's clips at `/v2/clips/{id}`, `clips.problem` null where the
film is served, the cards' `clipId` gone; keel-web 253 (master `41d18480`) plays it, 254 (building) deletes the text
player and typing. This spec moves spec 157's stranger legs onto it so `make e2e-157` keeps walking all three views
with nothing bought. Marks as the current gallery's; no new score.

## Rules

- **FR-1 The text view is the orb view.** 157 FR-2's text view becomes the orb view: a TEXT link opens on the AI intro
  (`ai-intro`) with the orb (`story-orb`) where the face's hello was, "not a person", the topic line, the consent, the
  mic test (`ai-mic-test` -> `ai-mic-heard` through the fake mic) and Start (`start-talking`); no `choice-talk` /
  `choice-write`, no "Read and tap" anywhere, no text player, no voice bar, no `clipId` on any served card. After
  Start on a project with a built story: the film plays first (its scenes, its clips from `ServedStory.clipIds`),
  then the orb speaks the opening (`speaker: ORB`, the opening clip's `url` under `/v2/clips/`), then the condition
  where one is served, the gate, the items; no PROBLEM passage and no hand-over card before the film. Without a story:
  the opening, then the problem passage, as 157's avatar view had them. The orb's `data-state` runs speaking ->
  listening -> hearing -> writing through one answer (158 FR-2's collector, reused).
- **FR-2 The avatar view, the same walk.** The avatar view keeps 157's assertions less the hand-over card and "no Type
  instead" (there is nothing to type anywhere now): the face, Back on every question, the film first on a story
  project, then the opening. The leg asserts the two views' served passages are the same words: for the same role,
  the orb link's and the avatar link's `interviewer.clips.opening` (and one item's `clip`) resolve to clips whose
  text (the stack's `speech_clip` row, or the fake recorder's script) is identical.
- **FR-3 Speak or tap.** On the orb view one item is answered by its letter through the fake transcriber ("B" -> the
  second row held), one by its words, one by tap; the story question is answered by its chip (`I can't recall one
  particular ...`) by voice on one link and by tap on another; the mic refused on one link (the harness's refusal
  hook) walks the whole interview by taps alone and finds no typed box on any screen (`textarea`, `input[type=text]`
  inside the interview: the leg fails on one).
- **FR-4 The founder's side.** The new-link popup offers *Keel's voice* (the default) and *AI interviewer*, no third
  row (`interviews_screens.FORMAT_NAMES` moved; `_step_one`'s patterns); a kind card not yet set up offers *Try it
  yourself* and the dry run opens on the orb; the lock's ledger shows no new charge for the orb's clips (the
  `CARD_SPEECH` rows priced 0, `InferenceCharge.VERSION` 20 unchanged: `harness/interview_charge.py`).
- **FR-5 Nothing bought, as 157.** FakeSpeech serves every orb clip (the 0.312 s mp3), the stack's fake avatar the
  face, the fake transcriber the voice; the log scan unchanged.
- **FR-6 The copilot view** (157 FR-2) is untouched; the legs stay.
- **FR-7 Report + DRIFT.** `evals/three_views_report.py` names the orb view; DRIFT entries for anything the walk finds
  against 267/253/254 as written (the screen, the wire, the words). The wire assertions of contract 83 that 84 moved
  (`clipId`, `speaker`, `formats`) are updated in the mirrors this spec touches, never loosened elsewhere.

## Acceptance
- `make unit` green on every file this spec touches (`tests/test_three_views_157.py`, `tests/test_conversation_158.py`,
  a new `tests/test_orb_159.py`); the pre-existing mirror reds listed in 158's tasks.md are not made worse.
- `make e2e-157 PROFILE=eval` on the local stack (the sibling main checkouts: keel-cloud-docs master `8bd57d6f` or
  later, keel-web master `41d18480` or later) with every leg named in the report; the run of record is the one on the
  merged masters after keel-web 254, run by the integrator. `runs/` stays gitignored; `runs/DRIFT.md` tracked.

## Out of scope
Scoring; the copilot bench; paid readings; the HeyGen live check (staging, on the founder's word).
