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
- **FR-5 The solution and the money fronts.** The solution leg: the which-problem page, the film, the replay of the
  problem's boxes closed by silence, the two idea beats (the name and a colour said in words; one answer mapped to
  ticks and crosses), the idea boxes, the build, the story with the icon and the colour (the review condition: the
  name clearly visible, never faded, cropped or shrunk), Compatibility with Relative advantage pre-filled. The money
  leg: the two pick pages (a solution, and once with only a name), the replay with the idea box, then today's persona
  step reached. The problem leg adds the spoken window after the story (the proposal said, a number said back, the
  window stored).
- **FR-6 Report + DRIFT.** `evals/three_views_report.py` names the beats; DRIFT entries for anything the walk finds
  against 263/245 as written, with the screen, the wire and the words.

## Out of scope
Scoring; the copilot bench; paid readings.

## 158c -- the walk reads the turn made plain (keel-web 249, master `824ede0a`; 2026-11-22)

- **FR-7 The turn screen as 249 draws it.** The orb (`story-orb`, `data-state`) is present on every voice screen
  again, 44px, with the state line beside it; there is no `story-glow` (the walk and `test_three_views_157.py`'s
  `WEB_SELECTORS` drop it, and point `story-boxes` at `src/components/voice/UnderstoodCard.tsx`). The founder's words
  are no longer in `story-words` (Keel's lines only): they are in the grey *What I hear* panel, `story-heard`, in
  quotation marks; the snapshot's `heard` field carries them, `words` Keel's. Between beats the orb goes `writing` ->
  `speaking` (no `listening` in between: `listening` now means the microphone is open); `BEAT_ORB` becomes
  `speaking -> listening -> hearing -> writing -> speaking` with `listening` only where the microphone opened. The
  hand-over is checked: `window.__keelChime` (a counter in the test build) rises by exactly one per hand-over, and
  `data-state="listening"` is first seen in the same snapshot as the state line *Your turn. I am listening.*
  (`story-state`). The readback is the card: `story-boxes` rows carry `data-box` and `data-lit`; the walk reads the
  rows by `data-box` (`person`, `job`, `when`, `today`, `limits`, `cost` -- as the card names them), not by the
  board's text; beat 3's crosses are the `story-understood` card and the idea beat's ticks `idea-understood`.
- **FR-8 One film.** On a new project's story route exactly one sheet (`guide-opener`) is mounted and after its
  close both OPENER and WELCOME are seen on the cloud (`GET overview` `guide.openersSeen` has PROBLEM,
  `guide.welcomeSeen` true); the eval founder's walk no longer meets a welcome sheet on the conversation routes.
- **FR-9 DRIFT.** DRIFT #110's `corrections` entry (cloud fake) lands with keel-cloud 264; until then FR-1a's
  correction leg stays `stop=False` and is reported as such. DRIFT #111 (the phone page scrolls by the footer) stays
  open for the web. Anything the walk finds on 249 is a new DRIFT entry.
- **Run of record** on keel-cloud master `af49e837` (or the 264 branch once merged) + keel-web `824ede0a`, fakes
  only, nothing paid; report under `runs/157/<cloud>-<web>/`, the 13 legs named; the report's drawn-story section
  (158b) kept.
