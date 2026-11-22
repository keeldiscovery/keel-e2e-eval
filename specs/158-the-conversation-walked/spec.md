# Spec 158 -- The conversation, walked: the harness on keel-cloud 263 + keel-web 245

The founder's redesign of the spoken intake (2026-11-22): four beats, one long answer each, the limitations broken out
by Keel, nothing to press, nothing cut. This spec moves spec 157's harness onto it so `make e2e-157` keeps walking all
three views with nothing bought. Marks as the current gallery's; no new score.

## Rules

- **FR-1 The founder's legs on the beats.** `harness/story_screens.py` walks the five beats (`said_turns` -> the
  beats 1..4 and 5 only when owed), with the fake transcriber's text in: beat 2's one answer carries the job and the
  moment; beat 3's one answer is a long one (at least 1,500 characters, five limitations named in one breath, a cost
  said in passing) and the leg checks it is stored whole (`GET story`'s turn words, no 240 cut), read into four red
  crosses, the readback names them, and the harness's "silence" hook closes the beat; beat 4's readback is confirmed
  by silence; a correction after beat 4's readback ("only the ones in Europe", through the fake mic) narrows the
  condition and the readback says so. No button is clicked anywhere on the beats: the harness fails a leg that finds
  one (`button` elements other than the orb inside the story screens).
- **FR-2 The orb and the screens.** The screen collector records the orb's `data-state` through a beat (speaking ->
  listening -> hearing -> writing -> speaking), the folded transcript line after beat 3, the cost line present on the boxes (`costDrafted` on the wire,
  no label on screen), and that the boxes confirm by silence and the story closes by silence to the window screen (244 FR-1).
- **FR-3 Nothing bought, as 157.** FakeSpeech, the stack's fake avatar, the fake transcriber; the log scan unchanged.
- **FR-4 The three views** (157 FR-2) are unchanged except the story cards' clips, which now come from the beats'
  slots; the legs stay.
- **FR-5 Report + DRIFT.** `evals/three_views_report.py` names the beats; DRIFT entries for anything the walk finds
  against 263/245 as written, with the screen, the wire and the words.

## Out of scope
Scoring; the copilot bench; paid readings.
