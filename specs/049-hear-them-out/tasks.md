# Tasks 049

- [x] T001 Cases copy + guard on `readaloud` (FR-1)
- [x] T002 Walk: the read-aloud step, IM19, corpus bump (FR-2, FR-3)
- [x] T003 Walk: Save on tapped checkboxes (FR-5), the pilot's auto-finish on both links (FR-6), earcons seam (FR-7)
- [x] T004 `make unit`, `make eval` on the stack; judgement calls + counts here -- remote journeys on staging wait for
  keel-cloud 100 + keel-web 073 to be deployed there

## Measured (2026-10-16, keel-web `baf934f`, stack fakes only, a fresh stack)

- `make unit`: **2,342 passed / 53 skipped** (2,298 / 53 after spec 048; +44: the 18 `readaloud` identity cases, 16
  seeded marks faults, the 073 source checks).
- `make eval K="s005 or s006 or s007"`: **3 passed in 622 s** (582 s at 048; the gap's 1.5 s per spoken answer), on
  keel-cloud-docs **`b1007f1`** -- master moved past the brief's `d2f00d4` to spec 101 (framing lines) while this ran
  (D-05); the S-005 that first went green here ran on `6e2683d`, whose code is `d2f00d4`'s.
- Interviewer marks v3: S-005 **14 of 14** owed met (IM19, IM20 among them; IM2 / IM8 / IM10-IM12 / IM18 are the full
  leg's); S-006 **19 of 19** measured met (IM1-IM20 but IM12, unmeasured as before, DRIFT #86).
- Classifier guard (stranger's route; the same on Try it yourself's founder route on S-006), never a confident wrong:
  S-005 128 asked / 115 right / 13 safe / **0 wrong** (42 not asked), **`readaloud` 12 asked / 12 right / 0 wrong**
  (6 not asked); S-006 93 / 83 / 10 / **0** (77 not asked), **`readaloud` 9 / 9 / 0** (9 not asked). The three
  corrections asked right on both. (keel-cloud 100's own bar for its fake on its own items -- 137 of 152 + 17 of 18 --
  is keel-cloud's table test; here the cases are carried onto the links' own items, 048 call 5.)
- The read-aloud step: S-005 *"On your last delivery would an alert on mismatched deliveries have made things better"*
  then *"It would have made things better"* 262 ms later -> one `classify`, `heard` both joined, held; S-006 the same
  question on Paidly's link, then *"No difference"* 261 ms later -> one read, held on No difference. Nothing ticked,
  no field, no preview inside the gap after any of the 18 (S-005) / 10 (S-006) finals looked at.

## Where things are

| Piece | Place |
|---|---|
| the 170 cases, copied whole | `harness/classifier_cases.py` (canon `cases.py` at keel-cloud-docs `d2f00d4`, unchanged since `e20d8aa`) |
| the guard's groups | `harness/classifier_guard.py` `Report.groups()`; 100's three fake reasons in `FAKE_REASONS` |
| the seam | `harness/interviewer_screens.py` `SPEECH_SEAM` (`earcons: false`, `__listening()`); `Player.say` looks inside the gap (`hearing`), `ear()` counts a recogniser live only while it is handed results, `save_state`, `wait_missed`, `checked`, `classified` |
| the walk | `evals/interviewer_leg.py` `_Walk.read_aloud`, `.tap_pick_two`, `.pilot`; `_read_aloud_item`, `_question_words`; `_recorded_pilot` |
| the marks | `evals/interviewer_marks.py` IM19 `hears_them_out`, IM20 `taps_wait_for_save`, IM14 reads the pilot's hold; `INTERVIEWER_MARKS_VERSION` 3 |

## Judgement calls decided

1. **The read-aloud step is on the "better" question** (spec call 1, as preferred): Relative advantage
   (`benefit_with_advantages`) where the person picks one of its options, else the first one-of question whose labels
   share a word, else the first one-of. What is read aloud is the served question up to its question mark, its closing
   "or not" left off, without punctuation (a recogniser writes none) -- the words that hold "made things better", which
   072 lit as they arrived. FR-2's "first words" up to the first comma was tried first and read *"On your last
   delivery"* on both corpus links: no option word in it, nothing to prove. The step is tried before any other move on
   that question, and the read is settled where it lands (held on the one meant; held on another -> "no" and its place;
   *Is that right?* -> "yes" or its place), so the response is still held to `sent == want`.
2. **"One read" is measured on the wire**: the `Player` keeps every `classify` request body the page sends (the eval's
   seam carries no `classify`, so there is no `window.__classified`); IM19 wants none in the gap and exactly one for the
   item before the read settled, its `heard` the two finals joined by a space.
3. **IM19 also looks inside the gap after every spoken final** on a question's or a confirmation's window (250 ms after
   the words, the status still *Listening. Pause when you're done.*): no row newly ticked, the field as it was, no
   preview drawn by the words. A miss's reason drawn before the words may stay (D-02).
4. **IM20 is on the first pick-two answered with two options, by taps** (FR-5 named "the change-by-tap after Back", but
   the walk's Back lands on a one-of question -- 048 call 13 -- whose change is a radio tap with the 500 ms advance; no
   Save there). One tick: *Save and next* drawn and disabled, the same question 1.5 s later, `listening`, no ring; two:
   enabled; a third row tapped: ignored; Save: *Got it.* (read off the status timeline) and on; the response carries
   both, `how` TAPPED. Later pick-twos are spoken as before.
5. **The pilot's auto-finish is observed in IM14** (spec call 2): the spoken yes is a hold like any other -- the held
   status, `ai-ring`, `ai-finish` drawn -- and the thanks come with nothing pressed (no `finish()` on the spoken route,
   `ai-finish` presses 0). IM6 still counts the opt-in. The marks' names: IM19 *hears them out*, IM20 *taps wait for
   Save*.
6. **The walk encodes no gap length** (the coordinator's two notes of 2026-10-16: keel-web 074 makes the gap 4.0 s on
   every window, the story's too, and holds a yes to *Is that right?* 2.0 s). It waits for the held or unsure status or
   the next question (20-30 s timeouts, ample for 4 s + 2 s); after a yes it already takes a hold or the next question
   (`_held_or_on`), and a hold's presses are counted from after the answer. `quietMs` is left at the page's default
   (073 FR-4): the journeys pay the gap honestly. `GAP_TOLERATED_MS` 4,000 is held to keel-web's `QUIET_MS` by a source
   check (at most); the only fixed wait is IM20's 1.5 s. Timeouts raised: `mic_test` 15 -> 20 s; no other (FR-4).
7. **The recorded link's pilot is walked on the wire in the page's order**: the response, then `transcribe` of the
   pilot ask's recording against the first question's item (no `expected`, 073 D-02), then `POST pilot` when the
   transcript is "yes". It is refused 409 on the answered link -- DRIFT #91 -- recorded by name and not posted (the page
   would not post it); the step turns into a failing guard (transcript "yes", pilot 204) once that is fixed. No
   `GET standings` there (D-03); the opt-in count stays IM6's.
8. **Earcons**: `earcons: false` on the eval's seam (FR-7's first option); no mark.
9. **The corpus is not bumped**, as 048 did not bump it: 100 / 073 moved no screen schema and no corpus item. Revision
   11 and `MARKS_VERSION` 19 stay; `INTERVIEWER_MARKS_VERSION` 2 -> 3 is the bump.
10. **The live budget stays $0.10** (048 FR-2). 170 cases at $0.0006 would be $0.102, but the live check asks only what
    its link can carry (83-130 on the corpus links) and refuses a plan over 166 calls by name before the first call.
11. **FR-8's sha**: the spec names `e20d8aa`, the hand-off `d2f00d4`; `cases.py` is the same file at both, so the copy
    names `d2f00d4` and says so.

## Discovered

- D-01 **DRIFT #91**: on the recorded path the pilot ask's yes is never written down -- the page sends the answers
  first, then `transcribe`s the pilot recording, and keel-cloud refuses `transcribe` 409 on an answered link; the page
  reads that as nothing heard and never posts the pilot. The founder's "I said yes, it was not recorded" still holds
  for recorded browsers (Chrome on iPhone). For keel-cloud (serve `transcribe` for the pilot ask on an answered AI
  link) or keel-web (write the pilot down before the answers go).
- D-02 Observation, not filed: after a miss (*"A number from 0 to 4, please."*), the reason stays drawn under the next
  words while they are heard. It is the earlier read's, not a live match, so IM19 lets it stand.
- D-03 The eval's own trap, fixed here: `GET standings` starts the stale brief on Keel's keyless door exactly as
  `GET overview` does (keel-cloud 096 FR-D, `VectorsController.getStandings`); a standings read after the recorded
  link's answer left the staleness "tried" and the founder's return later started no brief (S-006 red once). The
  recorded pilot step reads no standings.
- D-04 `__recognisers()` grows on every final's end now (073 D-04): `Player.ear()` counts a recogniser as listening
  only while the page still hands it results (`onresult`), as keel-web's `__listening()` does, and the miss waits for
  *not taken* (`wait_missed`) instead of a newer recogniser.
- D-05 keel-cloud-docs master moved to `b1007f1` (spec 101; `ClipKind` now closes on `;` before a method) during the
  run: the green journeys of record built `b1007f1`. `tests/test_interviewer_marks.py::test_the_kinds_are_keel_clouds_own`
  read the enum with `,?$` and failed against it; it now reads `[,;]?$`.
