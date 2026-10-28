# Spec 075 -- The harness follows keel-cloud 139–142 and keel-web 122–124

The founder's morning of 2026-10-27 produced six product specs; this one moves the harness with them. Keel-cloud
139: a B2B money-only study lists no *has the problem* kind on the Interviews page or the contacts picker. 140: the
Price step's cost box names hours and rate (*40 to 80 hours a month at $80 an hour, $3,200 to $6,400 a month*).
141: Ability to pay's belief reads *Keel reads …*, never *You said …*, with a counting sentence under it. 142 +
keel-web 124: up to two follow-ups, each asked on the answer it hangs on under the kicker *About that*; the end
keeps *One last thing* for what is still owed; `followUps[]` on the response; contract 41. Keel-web 122: Plans,
Terms and Privacy rewritten; 123: the cost step's *Per* and *of* pre-filled with helper lines and the rate field
always shown when hours are priced. REVISION unchanged (the corpus is 16); marks change only where named.

## Rules

- **FR-1 The follow-up marks.** IM25 (the follow-up's windows: two minutes, four seconds) and IM27 (the follow-up
  after the answer against) are re-pinned to the new order: a follow-up asked right after its item under *About
  that*, at most two, *One last thing* only for an owed rung at the end; each pin's why names this spec. The AI
  walks that press *End* inside the follow-up's hold (S-005) press it inside the first on-the-spot follow-up instead,
  and the pilot-ask assertion of 074 holds there. The scripted respondents' answers that go against the founder are
  counted so each walk meets at least one on-the-spot follow-up and S-005 meets two; the corpus facts that read
  `followUp` read `followUps[]`.
- **FR-2 The founder's screens.** The money-only walk (S-016) asserts one kind card on Sent and one kind in the
  contacts picker; the cost-step walk reads the pre-filled *Per* and *of* and the rate field with its default note,
  and the Price step's cost box in 140's words; the Ability to pay stage-page read accepts *Keel reads* and asserts
  the counting sentence; any mark that read *You said* on that line is re-pinned and says why.
- **FR-3 The public pages.** The landing/plans checks (if any read the plans' numbers or the legal pages' sentences)
  follow keel-web 122's words; the matrix's smoke of `/terms` and `/privacy` (if any) reads the new *Last changed*.
- **FR-4 Nothing else moves.** The noise check, the six journeys' scripts beyond the lines above (and FR-5's), the
  judge, the paid commands.
- **FR-5 Keel-cloud 144 and keel-web 126** (amendment of 2026-10-27, evening: both built after this spec was written
  and merged on their masters, keel-cloud-docs `83d68888`, keel-web `0d57213`). (a) *One more thing.* The follow-up's
  lead-in is *One more thing.* in every FOLLOW_UP clip's script (`PassageComposer.ONE_MORE_THING`; the ALSO stems too),
  and the page draws one kicker, *One more thing*, on the spot and at the end, the AI sheet's and header's where-word
  and the text link's alike (*About that* is gone); the answers line under a person reads *One more thing · {rung}:
  "…"*. The harness's copies move (`interviewer_fake`, `interviewer_screens`, `interviewer_marks`, `report_marks`),
  the leg's clip asserts read the new lead-in, and the text walk tells a follow-up asked on the spot after *Send my
  answers* from the end's by its rung (the last item's), no longer by its kicker. A READY recording whose follow-up
  clips said *One last thing.* is re-rendered once each (144 FR-2): a fresh recording on the stack says the new line
  from the start, so no count moves; any mark that counts clips or backfills is held to the new words. (b) Contract
  42, `POST /v2/projects/{id}/interviewer/transcribe`: Try it yourself writes the hello, the story and the follow-up
  down through it, exactly as a link's are, and stores nothing. The dry run's screen (S-006) walks on to the story,
  says it, and holds it written down through the founder's route on the gate's id and taken as the story (never *That
  didn't match an option*, never a miss); the hello is written down through it too (keel-web 126 FR-2 retired the
  `answer` workaround). On the wire beside the dry run's follow-up twin: the gate's id and the follow-up's id written
  down (60 and 120 s), an id no role serves and a link's gate refused 422 `ITEM_NOT_ON_FORM`, 90 s 422
  `SHAPE_MISMATCH`, nothing stored. The stack's fake transcriber serves the route as it serves the link's (the same
  `Transcriber`; no stack change). (c) Keel-web 126's text box: the first *Speak* is `data-state="asking"` (*Allow the
  microphone…*, *Cancel*, no waveform, no clock, nothing recorded) until the recorder runs, then `listening`; the
  microphone is kept between takes and let go by the page on done. The story's speaker on S-005 / S-006 holds the
  permission sheet through the seam (keel-web's `installHeldMic`, restated) so *asking* can be read, then grants it;
  IM26 reads *asking* before T2, the take ended with nothing let go, and the release on the done screen. The free
  question's didn't-catch words (*I didn't catch that. Say it again, or type instead.*, the second miss *Say it again,
  or type it.*) and Sent's *Keel is still writing this question.* are read by no walk: no mark moves for them (the
  dry run's story asserts it is not a miss in those words). Marks move only where they read these states or words
  (`INTERVIEWER_MARKS_VERSION` 11); `MARKS_VERSION` 20 and corpus REVISION 16 unchanged.

## Acceptance

`make unit` green; the six journeys green on the local stack against the merged checkouts (cloud through 142, web
through 124), then on staging after the deploy. As amended with FR-5 (the founder's light gate of 2026-10-27): one
journey, S-005, on the local stack against keel-cloud-docs `83d68888` (through 144) and keel-web `0d57213` (through
126); the other five journeys are the thorough pass's, and tasks.md says so. Marks table in tasks.md: every pin moved, its why. No DRIFT filed
silently: a product behaviour the walks find that none of the six specs asked for is filed in `runs/DRIFT.md`.
