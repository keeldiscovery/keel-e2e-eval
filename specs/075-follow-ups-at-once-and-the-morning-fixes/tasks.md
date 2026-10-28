# Tasks 075 -- The harness follows keel-cloud 139-142 and 144, keel-web 122-124 and 126

Branch `075-follow-ups-at-once` off master `3ffee85` (worktree `wt/eval-075`, `.git` a file). The products, read only:
keel-cloud-docs master `83d68888` (139 one kind on a money-only study, 140 the cost box in hours, 141 Ability to pay as
Keel's reading, 142 up to two follow-ups -- contract 41, document 32 --, 144 the dry run's transcribe and *One more
thing.* -- contract 42; corpus revision 16) and keel-web master `0d57213` (122 Plans / Terms / Privacy, 123 the cost
step's *Per* and *of*, 124 follow-ups at once, 126 the founder's four defects of 2026-10-27). The stack built from those
checkouts through the four symlinks beside the worktree (`wt/keel-cloud-docs`, `wt/keel-web`, `wt/keel-runtime`,
`wt/keel-connect-skill`, made 2026-10-25; `stack.toml`'s `../` paths resolve through them), keel-runtime 0.8.0 bundled
in keel-connect-skill. No paid command was run, no key was present; every model, transcriber and renderer the fakes.

FR-1 and FR-2 were built by the first builder (cut off before FR-3); FR-3 -- FR-5, the spec's amendment and this file by
the second. Nothing merged or pushed.

| Commit | What |
|---|---|
| `c48056a` | the spec |
| `b46d909` | FR-1 the follow-up marks (`INTERVIEWER_MARKS_VERSION` 10) |
| `197509c` | FR-2 the founder's screens |
| `4db7dfe` | the spec amended: FR-5 (keel-cloud 144, keel-web 126), the light gate |
| `fab5c87` | FR-5 (`INTERVIEWER_MARKS_VERSION` 11) |
| `3fbea0c` | FR-5: the asking state's Continue read across 600 ms (D-01) |
| this commit | FR-3 / FR-4 (no code), AGENTS.md, README.md, this file |

## Unit

| | passed | failed | skipped |
|---|---|---|---|
| master `3ffee85` (the hand-off's figure, against the products before 139) | 3,436 | 0 | 53 |
| `197509c` (FR-2) against keel-cloud-docs `83d68888` + keel-web `0d57213`, before FR-5 | 3,466 | **3** | 53 |
| `fab5c87` (FR-5) | 3,504 | 0 | 53 |
| `3fbea0c` and this commit (the walk's read and docs only) | 3,504 | 0 | 53 |

The three reds at `197509c` were FR-5's subject: keel-web 126 made `FOLLOW_UP_KICKER` *One more thing* and removed
`FOLLOW_UP_SPOT_KICKER`; keel-cloud 144 renamed `ONE_LAST_THING` to `ONE_MORE_THING`.

## FR-1 -- the follow-up marks -- `b46d909`

- [x] T001 `interviewer_fake.owed` / `first_stem` / `first_rung` take `asked` (keel-cloud 142 FR-1: a rung already
  asked is passed over); `interviewer_fake.asks` is the page's own walk -- after each answered item of a rung the link
  walks, fewer than two asked, the route asked with the answers so far; a rung on that item asked there and then; after
  the last item one call more (a rung on it on the spot, then the end's); `late` items' calls held past the beat leave
  the rung to the end. `vectors_script.follow_up_plan` composes each, with `on` (the item it hangs on, or None).
- [x] T002 The text walk (`vectors_screens.Interview`) answers every follow-up screen it meets, after an item's *Next*
  and after *Send my answers* (`_follow_up_screen`, `_after_follow_up`, `_end_follow_ups`); every route call kept
  (`follow_up_routes`); `LATE_FOLLOW_UPS` (05-paidly's Wen Zhang) holds one call past the beat so a golden journey meets
  the end's follow-up too.
- [x] T003 The AI walk (`interviewer_leg._Walk.follow_up`) meets the follow-ups after any item: S-005's person owes two
  (the first through two windows by way of *Back*, *End* pressed in the second's hold), S-006's one (the silent window to
  the cap, then the next item). `_ai_person` picks the answers that owe them.
- [x] T004 The wire legs send `followUps[]` and check 142's refusals (two on one rung, the old `followUp` beside the
  list); `stack.ledger.stored_follow_ups` reads document 32's list (a stored `followUp` as the one-element list);
  `report_marks.expected_person` reads `followUps` (a read before 41 its one `followUp`).
- [x] T005 Unit: `tests/test_follow_ups_075.py` (the ladder offline, the plan, the screen in a real page, the wire legs'
  source); `test_interviewer_marks.py`, `test_follow_up_ladder.py`, `test_recorded_path_074.py`,
  `test_revision_16_walk.py` re-pinned.

## FR-2 -- the founder's screens -- `197509c`

- [x] T010 S-016 (`scope_journey.one_kind`): Sent draws one kind card, the decision-maker's; the register's `kinds[]`
  and the contacts picker's (`GET contacts/datasets`; refused `CONTACTS_NEED_CREDITS` on an account on its own AI, the
  Contacts page then drawing no tabs) are that one kind (keel-cloud 139).
- [x] T011 Every Price step reads its cost box (and the chain's Ability box) as it opens, held to the served
  `costEstimate.said` / `abilityToPay.sentence`; on an hours estimate in 140's words (`hours_cost_box`).
- [x] T012 The chain cost step (walked where a cost is the chain's: the back-tests) reads *Per*, *of*, their helper
  lines, the rate and its note before typing, held to keel-cloud's own defaults (`chain_fill`; keel-web 123).
- [x] T013 The money page opens Ability to pay's row and holds its said line: never *You said your price …*, and the
  budget reading's second sentence the counting one by kind of study (`_hold_the_ability_line`; keel-cloud 141). No
  mark read *You said* on that line, so none moved.
- [x] T014 Unit in `tests/test_follow_ups_075.py` (the words against keel-web's and keel-cloud's sources).

## FR-3 -- the public pages -- this commit (no code)

- [x] T020 Searched: no harness check reads Plans' numbers or the legal pages' sentences (the only `/plans` mention is
  `browser.Overview.says_your_ai`'s note that its sweep stays off the marketing pages; `Auth.STANDING_HINTS` keeps old
  door-card hints as a set, not a pin), and the matrix (`matrix/`) smokes neither `/terms` nor `/privacy`. Keel-web 122
  therefore moves nothing here; no *Last changed* is read.

## FR-4 -- nothing else moves -- this commit (no code)

- [x] T030 `MARKS_VERSION` 20 and corpus `REVISION` 16 unchanged; no corpus, registry, fixture or golden number moved;
  `GUIDE_MARKS_VERSION` 3, `CONTACTS_MARKS_VERSION` 2, `FEEDBACK_MARKS_VERSION` 1, `SCOPE_MARKS_VERSION` 2,
  `REPORT_MARKS_VERSION` 2 unchanged; `INTERVIEWER_MARKS_VERSION` 10 by FR-1, 11 by FR-5. The noise check, the judge
  and the paid commands untouched.

## FR-5 -- keel-cloud 144 and keel-web 126 -- `fab5c87`, `3fbea0c`

(a) *One more thing.*
- [x] T040 `interviewer_fake.ONE_MORE_THING` ("One more thing."), `RETIRED_LEAD_IN` the old line; `follow_up_script`
  opens on it. `FOLLOW_UP_KICKER` is *One more thing* in `interviewer_fake`, `interviewer_screens` and
  `interviewer_marks`; `FOLLOW_UP_SPOT_KICKER` is gone from all three (as from keel-web).
- [x] T041 The text walk's `_end_follow_ups` tells the follow-up *Send my answers* opens on the spot from the end's by
  the rung the route answered (the last item's own is on the spot; a rung is asked once, so the end's is another) --
  the kicker no longer can. The AI walk reads `where` == *One more thing* for a follow-up window.
- [x] T042 The leg's FOLLOW_UP clip asserts (`_follow_up_clips`) and IM27 read `fake.ONE_MORE_THING`;
  `report_marks.ONE_MORE_THING` and `corpus_scenario.follow_up_line` read *One more thing · {rung}: "…"*.
- [x] T043 144 FR-2's re-render of a recording whose clips say *One last thing.*: a recording made on this stack says
  the new line from the start, so nothing is re-rendered and no count moves; S-006's backfill stand-in (all FOLLOW_UP
  clips taken out) is 103's path, unchanged by 144, and stores the clips again in today's words, which IM27 now reads
  as *One more thing.*.

(b) Contract 42, the dry run's transcribe
- [x] T044 `_dry_run_on_screen` (S-006) walks on from the first held answer to the story (a segment chip or the gate
  answered "yes" and held on the way), says `DRY_RUN_STORY` into its window, reads its hold, then *End*; every
  `interviewer/transcribe` the page sent is kept. `dry_run_written_down` holds: the hello written down through the
  founder's route (200, *hello*) and never read through `interviewer/answer` (keel-web 126 FR-2 retired that
  workaround); the story written down once on the gate's id (200, the words said, `maxSeconds` absent or 60), held,
  and no miss words on its window (*That didn't match an option*, *I didn't catch that. Say it again, or type
  instead.*, *Say it again, or type it.*, *not taken*). Asserted in the dry run's step; no mark had read the dry run's
  story (the walk stopped at the first question), so none moved.
- [x] T045 `_dry_run_transcribe` (S-006, beside the follow-up twin), on the wire: the dry run's gate id written down
  (absent and 60), the twin's `FollowUpQuestion.itemId` at 120, an item (the mic test, *hello*); an unknown id and a
  link's own gate id 422 `ITEM_NOT_ON_FORM`, 90 s 422 `SHAPE_MISMATCH`; nothing stored (invitations, answered, pilot,
  ledger rows unchanged). `_said_audio` is the seam's recording shape (UTF-8 zero-padded to 20 KiB).
- [x] T046 The stack's fake transcriber serves the founder's route as the link's (the same `Transcriber`); only
  `stack/cloud.py`'s comment says so.

(c) Keel-web 126's text box
- [x] T047 `text_seam(held=True)` restates keel-web's `installHeldMic` (`__micHeld`; the acquire waits until
  `__grantMic()`); `SpeakBox.read` reads the asking card's line (`asking`), `SpeakBox.grant` answers the sheet. The
  story's speaker (`STORY_SPOKEN` "quiet" / "done") runs held; the refused speaker does not.
- [x] T048 `_speak_story`: the tap, then `asking` read (the line *Allow the microphone…*, *Cancel*, no waveform, no
  clock, no Done, the microphone asked once, nothing recorded, Continue read three times across 600 ms -- D-01), then
  granted and T2 as before; on the done screen the page's releases are read again (`released_at_done`).
  `_hold_the_box` asserts them, and that the take let nothing go (releases at T4 those before the pill -- the dev
  build's StrictMode stamps one at load).
- [x] T049 The free window's didn't-catch words and Sent's *Keel is still writing this question.*: no walk reads them,
  so no mark moved (`ivs.AI_REASON_DIDNT_CATCH`, `AI_SECOND_MISS_FREE`, `AI_REASON_NO_MATCH` are restated for T044's
  check and held to keel-web's `translate.ts`).
- [x] T050 Unit: `tests/test_one_more_thing_075.py` (21: the lead-in against `PassageComposer`, the one kicker, the
  answers line against `followUpLine`, contract 42 in the canon's yaml, `dry_run_written_down` and ten named faults,
  the wire check's source and audio, the held sheet against keel-web's fixture and in a real page, IM26's two new
  reads); the kicker and lead-in pins in `test_follow_up_ladder.py`, `test_follow_ups_075.py` (one kicker; the spot
  told from the end by its rung, in a real page), `test_interviewer_marks.py`, `test_revision_16_walk.py`.

## The marks: every pin moved

| Mark | Version | Moved | Why |
|---|---|---|---|
| IM23 | 10 (FR-1) | the follow-ups as the page asks them: right after the item, at most two, the end's only for a rung still owed, `asked` on every call, `followUps[]` | keel-cloud 142 FR-1 / FR-2, keel-web 124 FR-1 |
| IM24 | 10 (FR-1) | a skip is not sent (not `{dimension, skipped: true}`); the walk goes on to the step after it | keel-web 124 FR-3 |
| IM25 | 10 (FR-1) | the windows of every follow-up asked, each on a planned rung | keel-web 124 |
| IM23 | 11 (FR-5) | one kicker, *One more thing*, on the spot and at the end (the screens, the AI sheet's kicker and where-word) | keel-web 126 FR-5 |
| IM26 | 11 (FR-5) | the box is `asking` before T2; the take lets nothing go; the page lets the microphone go on done | keel-web 126 FR-4 |
| IM27 | 11 (FR-5) | every FOLLOW_UP clip (the ALSO stems too) opens on *One more thing.* | keel-cloud 144 FR-2 |

Read as before: every other IM, and every guide, contacts, feedback, scope, report and instruction mark (the report's
answers line is restated in its new words; `report_pilot` reads its record the same way, so `REPORT_MARKS_VERSION`
stays 2 -- judgement call J-3).

## The journey (local stack, keel-cloud-docs `83d68888` + keel-web `0d57213`, the scripted executor)

`docker ps` before `make up`: only `focused_robinson` (never touched). The light gate (the founder's word, 2026-10-27):
**S-005 only**; S-015, S-016, S-006, S-007 and S-014 are the thorough pass's and were **not run** -- so FR-2's S-016 walk,
FR-5's dry run (T044, T045) and the backfill (T043), which are S-006's, are unit-tested only.

| Run | On | Result |
|---|---|---|
| `runs/20261028T002559Z-s005-countly` | `fab5c87` | failed at Priya Natarajan's box: Continue read enabled the instant the asking card was drawn (D-01, the harness) |
| `runs/20261028T002810Z-s005-countly` | `fab5c87` + D-01's fix | failed at the end: two golden readings "moved" -- the stack still carried the scripted runtime the first run left connected, every reading one person behind (D-02, the protocol) |
| `runs/20261028T003742Z-s005-countly` | `3fbea0c`'s tree, after `make down` / `make up` | **passed** (341 s): IM 23 of 23 (v11: the follow-ups on both links under *One more thing*, IM26's asking and the microphone kept, IM23's order); guide 17 of 17; report 5 of 5; contacts 1 of 1; feedback 4 of 4; the FOLLOW_UP clips say *One more thing.*; the stage pages' lines *One more thing · {rung}: "…"* |

`versions.json` of the run of record: keel-cloud `83d68888` (clean), keel-web `0d57213` (dirty by its untracked
`.idea/` alone), keel-e2e-eval `fab5c87` dirty by `3fbea0c`'s change, keel-runtime `3988131`. `make down` after it.

## Discovered

- D-01 The asking card's Continue: `GateScreen` turns Continue off through the box's state on the render after the card
  (`onBoxState`), as spec 051's D-02 found for *listening*; one read at the card's first draw saw it on. The walk reads
  it three times across 600 ms and holds the last (`3fbea0c`). The harness's, not the product's.
- D-02 A journey that fails mid-way leaves the scripted runtime it started connected, and the scripted executor
  consumes `INTERPRET` in corpus order: the next S-005 on the same stack read Priya Natarajan's story with Marcus
  Lindqvist's GUESSED and Sofia Reyes's with Tom Okafor's, so the standings counted two guessers and dropped two
  anchored people -- eight dimensions' counts off by one, deferred as golden readings the build moved. After `make down`
  (which disconnects it) and `make up`, the same code passed. Written into README's *Run* and AGENTS.md; not a product
  behaviour, not filed.

## Where the spec and the code disagreed

- *FR-1: IM25 and IM27 re-pinned*: the first builder re-pinned IM23, IM24 and IM25 at v10 and left IM27 (keel-cloud
  142 reuses every rung's clip as it is). IM27 moved at v11 with 144's lead-in.
- *FR-1: S-005 meets two on-the-spot follow-ups*: on the AI link, yes (adoption friction, then Commitment on the last
  item). Of S-005's text walks five meet two on the spot and Priya Natarajan one; none meets an end's follow-up on
  01-countly (05-paidly's Wen Zhang does, by `LATE_FOLLOW_UPS`, on S-006).
- *Acceptance: the six journeys green on the local stack, then on staging*: amended with FR-5 to the light gate (S-005);
  staging is not this builder's (no deploy, no push).

## Judgement calls

- J-1 **The spot and the end told apart by the rung.** With one kicker the text page draws nothing that says where a
  follow-up hangs; the route's answer does (`dimension`), and a rung is asked at most once, so the last item's own rung
  is the spot's. IM23's `on` for a follow-up after an item's *Next* is still where the screen appeared.
- J-2 **The dry run's story is a leg assertion, not a new mark.** No mark read the dry run past its first question, so
  none moved; the new check is `dry_run_written_down`, asserted in the dry run's step (and unit-tested), so a broken
  route fails S-006 without a ruler change.
- J-3 **`REPORT_MARKS_VERSION` stays 2.** The answers line's lead word is restated (*One more thing*); `report_pilot`
  reads the same record the same way. `INTERVIEWER_MARKS_VERSION` moved because IM23 and IM26 read their records
  differently.
- J-4 **No stand-in for 144's re-render.** Seeding a recording's FOLLOW_UP scripts back to *One last thing.* would be a
  new stand-in in `stack/ledger.py` whose first run would be S-006's; keel-cloud 144's own `InterviewerRecorderTest`
  covers the re-render, and nothing here counts it. Left open.
- J-5 **The held sheet only for the speakers who take a take.** The refused speaker's acquire resolves at once (T6, as
  before); the other journeys' pages get no seam.
- J-6 **Releases at T4 are compared, not zero**: the dev build's StrictMode runs the page's release once at load (as
  keel-web 116 D-03 found on the AI page), so the take is held to "nothing let go since before the pill".

## Left open

- The thorough pass: S-015, S-016, S-006, S-007 and S-014 on the local stack (S-006 walks FR-5's dry run and wire
  check for the first time), then the six remote journeys on staging after keel-cloud 139-144 and keel-web 122-126 are
  deployed there.
- A stand-in for keel-cloud 144's re-render of *One last thing.* clips (J-4), if the founder wants it walked here.
- No DRIFT written.
