# Tasks 051

- [x] T001 Contract 19 pins (README, AGENTS, `stack/cloud.py`, the interviewer leg, `instructions/marks.py`'s header);
  `LADDER`, `first_rung`, `fill` in `harness/interviewer_fake.py`, held to the registry export (FR-1, FR-2)
- [x] T002 The fakes: FOLLOW_UP in `KINDS` / `UNSPOKEN`, the per-role clips held (IM27), the fake transcriber as 103
  keys it (FR-3); stand-in 5 (`stack/ledger.stand_in_no_follow_ups`) and the backfill (FR-8)
- [x] T003 Text walk: the follow-up route, screen and response on every text walk; the story's box T1 -> T4 and T6
  (`harness/vectors_screens.py`, `harness/interviewer_screens.SpeakBox` / `text_seam`); the consent line (FR-4, FR-5,
  FR-9)
- [x] T004 AI walk: the follow-up's two windows by way of Back (S-005 browser, S-006 recorded and silent), the dry run's
  twin, the recorded link's follow-up on the wire (FR-6, FR-7)
- [x] T005 IM23-IM27, `INTERVIEWER_MARKS_VERSION` 5, each with seeded faults; the corpus people's follow-up lines
  (FR-10, FR-11)
- [x] T006 `make unit`, `make eval K="s005 or s006 or s007"` on a fresh stack; counts and judgement calls here --
  remote journeys on staging wait for keel-cloud 103 + keel-web 076 to be deployed there

## Measured (2026-10-17 UTC, stack fakes only, one fresh stack, green on the first run of the three)

- `make unit`: **2,477 passed / 57 skipped** (against keel-cloud-docs `4cda99a` + keel-web `c9ce17c`). Before, on the
  same pins: 2,385 passed / 2 failed / 57 skipped (master's 2,391 / 53 was measured on 102 + 075: on these pins two
  tests failed -- `test_the_kinds_are_keel_clouds_own`, 103's FOLLOW_UP, and the seam test, 076's counting microphone --
  and four more skip because the pin worktree carries no keel-cloud `build/` outputs, D-05). +90: 50 in
  `tests/test_follow_up_ladder.py` (the copy held to the registry, 21 hand-worked walks, the fill, the composer's
  defaults and literals, the consent line, 12 + 2 keel-web word / cap / seam checks, the corpus lines on three entries,
  the founder's side, 2 remote refusals), 40 seeded IM23-IM27 faults (the brief_facts card-line tests moved in place, call 12).
- `make eval K="s005 or s006 or s007"`: **3 passed in 770 s** (706 s at 050), on keel-cloud-docs **`4cda99a`** (spec
  103, the `keel-cloud-103-pin` worktree) + keel-web **`c9ce17c`** (076): S-005 307 s, S-006 303 s, S-007 138 s
  (`runs/20261017T170418Z-s005-countly`, `...T170927Z-s006-paidly`, `...T171432Z-s007-mulchrun`).
- Interviewer marks v5: S-005 **21 of 21** measured met (19 owed: IM23, IM24, IM26 among them; IM25 and IM27 measured
  and met, not owed; IM2 / IM8 / IM10-IM12 / IM18 the full leg's); S-006 **26 of 26** measured met (IM1-IM27 but IM12,
  unmeasured as before, DRIFT #86).
- The text follow-ups (IM23 / IM24): S-005 12 walks -- 7 owed (6 typed, Lena Fischer skipped), 3 owed nothing, 2 gate
  No (no route); S-006 20 -- 10 owed (9 typed, Viktor Fern skipped; five rungs: Importance, Relative advantage, Price,
  Buyer and payer, Commitment), 9 owed nothing, 1 gate No; S-007 19 -- 9 owed (8 typed, Jamal Washington skipped), 7
  owed nothing, 3 gate No. Every route answer on the harness's rung, its `text` equal to the harness's composition, no
  clip on a text link; the screen *One last thing*, that text, the note, *Continue* off while empty, *Skip this one*.
- The AI links: S-005 Commitment -- first window held 4,005 ms after the final with nothing pressed (the pause), Back,
  Commitment tapped again, the route asked again, second window held 32 ms after the final on *Save and next*; the
  response's `followUp` `{commercial.commitment, "A free trial on one small job first.", SPOKEN}`. S-006 Relative
  advantage -- the recogniser refused, the seam's recorder: stopped 3,996 ms after the last sound, `transcribe`
  `maxSeconds` 120 -> "yes", held; Back, Adoption friction tapped again, the second window silent to the seam's cap
  (9,002 ms of 9,000), skipped, no didn't-catch, *Last question* next; `followUp` `{solution.relative_advantage,
  skipped: true}`; the pilot ask then recorded too (transcribe "yes", held with the ring, pilot 204). Both windows of
  each link opened on the rung's FOLLOW_UP clip (`clips.followUp[dimension]` = the route's `clip`), never classified.
- The box (IM26): S-005 Priya Natarajan -- T1 idle, 0 acquisitions; T2 on the tap (1 acquisition, 1 recording, the
  card, the waveform, *0:00 · up to 1:00*); stopped 3,943 ms after the last sound; T3 *Writing it down…* / *Microphone
  off*; T4 the story + " yes", caret 147 of 147, *Heard you.*, *Add more*; `transcribe` 60 s. S-006 Nadia Petrova the
  same ended by *Done*; S-007 Travis Buckley by the quiet (3,963 ms). T6: Hana Yoshida (S-005), Omar Farouk (S-006) --
  the tap asks once, typing only, the pill gone.
- On the wire (S-006): Try it yourself's twin 200 on Relative advantage with the harness's text and its clip 206 on
  the founder's route, 204 for Nadia Petrova, nothing stored; the recorded link's follow-up -- route 200, `transcribe`
  `maxSeconds` 90 -> 422 *"90 seconds is not a window we listen for."*, 120 -> "yes", a response naming another rung
  422 SHAPE_MISMATCH, then 201 and stored `{solution.relative_advantage, "yes", RECORDED, skipped false}`; the
  Let-them-choose link's TEXT response with no `followUp` stored `{dimension, text null, how null, skipped true}`.
- FR-8 / IM27 (S-006): every role's set five / three FOLLOW_UP clips in ladder order, *One last thing.* + the
  registry's wording, DONE, served by rung; stand-in 5 took out 8, the first read served `{}` on both roles, then 8
  stored again DONE in the same words with new ids, served by rung, READY throughout, 0 ledger rows (on the same read
  as 050's stand-in 4). S-005's one role: eight.
- FR-9: the served consent line on every intro, text and AI, *Nothing here asks for your name* nowhere (DRIFT #92 on
  the words).
- Classifier guard, never a confident wrong: S-005 128 asked / 115 right / 13 safe / **0 wrong**; S-006 90 / 81 / 9 /
  **0**.

## Where things are

| Piece | Place |
|---|---|
| the ladder copy and the walk | `harness/interviewer_fake.py` `LADDER` (from cloud-docs `4cda99a`'s registry), `first_rung`, `against`, `walks`, `fill`, `lower`, `joined`, `follow_up_script`; held by `tests/test_follow_up_ladder.py` to keel-cloud's `dimension-registry.json` (the export the stack runs) and to `FollowUpComposer` / `PassageComposer` / `PriceLadder` / `Compare` |
| the founder's side, the composed question, the people's lines | `harness/vectors_script.py` `founder_side`, `founder_follow_up_words`, `follow_up_question`, `FOLLOW_UP_LINES`, `FOLLOW_UP_SKIPS`, `STORY_SPOKEN`, `PersonInputs.follow_up`, `with_pick` |
| the text walk | `harness/vectors_screens.py` `Interview.walk(follow_up=, speak=)`, `_follow_up`, `_speak_story`; `evals/corpus_scenario.py` `_hold_the_follow_up`, `_hold_the_box`, `_hold_the_consent`, `CONSENT_TEXT` |
| the seams | `harness/interviewer_screens.py` `text_seam`, `recorder_seam`, `SpeakBox`, the 076 words |
| the AI walk | `evals/interviewer_leg.py` `_Walk.follow_up`, `_browser_take`, `_recorded_take`, `_silent_window`, `pilot` (recorded path); `_follow_up_on_the_ai_link`, `_ai_person`, `_dry_run_follow_up`, `_recorded_follow_up`, `_follow_up_clips`, `_backfill` (stand-in 5), `_consent_on_the_intro`, `_follow_up_record` |
| the stand-in and the reads | `stack/ledger.py` `stand_in_no_follow_ups` (stand-in 5), `stored_follow_ups` |
| the marks | `evals/interviewer_marks.py` IM23 `asked_on_the_first_rung`, IM24 `skipped_honoured`, IM25 `two_minutes_four_seconds`, IM26 `speak_or_type`, IM27 `the_follow_up_clips`; `INTERVIEWER_MARKS_VERSION` 5 |

## Judgement calls decided

1. **The walk fills the placeholders itself** (spec call 1, as preferred): `harness/vectors_script.follow_up_question`
   walks the person's own corpus picks up the harness's `LADDER` (`first_rung`, the founder's side read off the corpus
   founder: Importance's item 0 `own`, the price's low, Buyer and payer's tested item) and fills the text the way
   `FollowUpComposer` does -- the served labels of the person's link (their picks, the own item, their answer, the
   band, the advantages), `Interview.occasion`, and the founder's tested condition / effort as the corpus founder wrote
   them, each lower-cased by `BeliefSentence.lower`'s rule, a missing value the composer's default (held to its source).
   The route's `text`, the text screen's `h1.iv-q` and the AI sheet's question are held to it on the strict journeys (S-012
   would hold the rung only). Equal on all 26 owed text walks and both AI links.
2. **The silent window** (spec call 2) is **S-006's AI link, its second follow-up window**, on the recorded path, and
   the 120 s are shortened through the seam -- 076's key is `followUpCapMs` (the spec's draft said `recordCapMs`), 9 s
   (`FOLLOW_UP_SEAM_CAP_MS`). The real two minutes are held three ways: the first window's `transcribe` carries
   `maxSeconds` 120 (and 90 is refused on the wire), keel-web's `FOLLOW_UP_RECORD_CAP_MS` is 120,000 in the source the
   stack serves (IM25 reads it, a unit test pins it), and the clock reads *up to 2:00* (the box's `capMs`, untouched by
   the seam). `silenceMs` is left at the page's 4 s, which IM25 measures.
3. **The marks' names and the bump** (spec call 3): IM23 *asked on the first rung against*, IM24 *skipped honoured*,
   IM25 *two minutes, four seconds*, IM26 *speak or type*, IM27 *the follow-up clips*; `INTERVIEWER_MARKS_VERSION` 4 ->
   5. Owed on the short form: IM23, IM24, IM26 (IM25's recorded window and IM27's backfill are the full leg's; both are
   still measured on S-005). The corpus stays revision 11 and `MARKS_VERSION` 19 (052's to bump).
4. **Two follow-up windows a link, by way of Back** (076: Back from the follow-up lands on the last item, and passing it
   again asks the route again). One link cannot end one window two ways, and a skip posts the response, so: S-005's
   first window ends by the pause, its second by *Save and next* (the response SPOKEN with the words); S-006's first is
   recorded and ends 4 s after the last sound, its second is silent and skipped. The last item is re-answered by one tap
   (`how` TAPPED on the wire; the walk expects it). The holds Back interrupts are not IM14's (they are pressed by
   design); IM23 holds both asks of the route.
5. **The recorded path is reached the way Chrome on iPhone reaches it**: the follow-up window's recogniser refuses
   (`__speechError('not-allowed')`), keel-web's `listenFailed` hands the window to the recorder (`recorder_seam`, the
   076 fixture's recorder restated with stamps). Everything before it stays 050's spoken walk (IM14-IM22 unchanged);
   everything after it -- the hold, the last item after Back, the pilot ask -- records, and the pilot's "yes" is written
   down by `transcribe` as DRIFT #91's fix serves it.
6. **The AI link's person stays the last reader** (044 call 152, the scripted executor's last INTERPRET entry). On
   01-countly Mei Chen is owed nothing, so on the AI link her Commitment is answered *Yes, after trying it first* --
   a support in `Compare` (no standing moves) and the ladder's last rung against (design §2: asked too) -- so the short
   form has a follow-up. On 05-paidly Wen Zhang is owed Relative advantage as she is.
7. **Try it yourself's follow-up is held on the wire, not walked on the screen**: the founder twin
   (`POST /v2/projects/{id}/interviewer/follow-up`) with the AI person's answers carried onto the dry run's own ids (by
   dimension and label) -- 200, the harness's rung and text, the clip on the founder's clip route (206), 204 for one owed
   nothing, the counts unchanged. Walking the dry run to its follow-up would be a second whole spoken walk (~150 s); the
   dry run's screen walk stays 050's (first question, End, *Nothing was stored.*, *Microphone off*).
8. **The fake transcriber is 103's, not the spec's** (FR-3's "if 103 keys the fake on something else, follow 103"):
   103's `FakeTranscriber` keys a line by the window's item word (`story`, `follow_up`) through `answer(item, text)`, a
   test-only seam no environment variable reaches; the stack can set only `otherwise`. So no `KEEL_INTERVIEWER_FAKE_STORY`
   / `..._FOLLOW_UP` were added (nothing would read them) and every window is heard "yes": the spoken story is the typed
   story + " yes" (the walk types the corpus story first, then speaks, so the append is visible), and the response's
   `story` is held to the box's value. The reading on arrival is unaffected (INTERPRET results carry no quotes).
9. **The box's people**: one take a scenario and one refusal where IM26 is owed -- S-005 Priya Natarajan (quiet) and
   Hana Yoshida (refused), S-006 Nadia Petrova (*Done*) and Omar Farouk (refused); S-007 Travis Buckley (quiet), a plain
   assertion. Only their pages carry `text_seam`; everyone else's runs with no seam. T6 is reached by tapping *Speak* on
   a refused microphone (one acquisition, `typing-only`, the pill gone) -- "no pill" by construction would need no
   microphone at all, which asks nothing to refuse. *Writing it down…* is read by holding the recorder's stop
   (`__holdStop`, as 076's frames do).
10. **The follow-up lines** are composed in `harness/vectors_script.py` (`FOLLOW_UP_LINES`, three a rung, no name, no
    digit, one sentence), on `PersonInputs.follow_up` -- the spec's `corpus_script.Person` is the old reader, and
    `evals/preludes.py` walks the retired People page; neither is on S-005/6/7. Every person owed a follow-up types the
    line of their place on their rung, but one skipper a scenario (`FOLLOW_UP_SKIPS`, each on a rung another types for).
    Every scenario has someone owed nothing.
11. **FR-8 shares 050's first read**: stand-in 5 (`stand_in_no_follow_ups`) takes the FOLLOW_UP clips out of the stored
    set beside stand-in 4's old words, and the one founder read (Try it yourself, both roles) is held to backfill both.
12. **The card lines follow 103 FR-9**: `instructions/brief_facts.py`'s `could_phrase` reads *said {condition}* (no
    *yes:*) and Purchase friction counts its supporters (*did not need {step}, or it was quick*), as `BriefFacts` does --
    the journeys' *the brief's cards are the entry's own* step failed on S-005 without it. No `MARKS_VERSION` move here:
    the `brief_facts` mark's golden is keel-cloud's own `BriefFactsCorpusTest` output, and the report side is 052's.
13. **The follow-up route is a read** for IM8 (`READS` gains `follow-up`): it stores nothing (103).
14. **What is stored is read off the document** (`stack.ledger.stored_follow_ups`): the recorded link's RECORDED
    follow-up and the Let-them-choose link's missing one, stored skipped -- no founder route serves a response whole on
    103 (`people[].followUp` is the standings side, 052's).
15. **Consent** (FR-9) is held to the served line, which is not design §9's words (DRIFT #92): what D17 decided (the
    name travels, quotes allowed, the old door line gone) is asserted; the design's phrase is not.

## Discovered

- D-01 **DRIFT #92** (filed): the served consent line is `InterviewComposer.CONSENT_TEXT`, not design §9's -- it drops
  *Keel's AI reads them ... not used to train anything* and adds *There is no way to delete it once you send it*
  (keel-web 076 D-09 saw it too). For the founder.
- D-02 Observation, not filed: on the text page the screen's *Continue* goes off one render after the listening card is
  drawn (enabled at the first read ~70 ms after the tap, off by 200 ms) -- it follows the box's state through an effect
  (`onBoxState`). The walk reads it three times across 600 ms and holds the last.
- D-03 keel-cloud 103 moved two card lines (FR-9), which the eval's `brief_facts` reading followed (call 12).
- D-04 Two tests failed on the new pins before any of this: `test_the_kinds_are_keel_clouds_own` (FOLLOW_UP, now in
  `KINDS`) and the seam test (076's fixture microphone counts its acquisitions; the test reads either form now).
- D-05 The pin worktree (`keel-cloud-103-pin`) carries no keel-cloud `build/`, so the four tests that read
  `SpokenGuidelinesCorpusTest` / `BriefFactsCorpusTest` output skip (57 skipped, not 53).
- D-06 The AI sheet's heard line reads *heardyes* as text (the tag and the words, no space) -- `textContent`; the walk
  reads the words inside it.
- D-07 Not walked: keel-web 076 call 6 builds no Back from the pilot ask (design §5.2 says Back returns to the
  follow-up; the response has gone by then). Left to the founder / coordinator, as 076 says.

## Amendment 2026-10-17: the remote profile types

- **What.** On the remote profile (`j.stack.is_remote`) nobody speaks the story: `corpus_scenario._speak_for` hands the
  walk `speak = None` for everyone, so no page gets `ivs.text_seam`, the story is typed as everyone else's is, and
  `_hold_the_box` (T1 -> T4, T6) is not run -- one note step per would-be speaker says so ("... skipped on the remote
  profile", `REMOTE_TYPES`). The interviewer leg's remote return now writes its `interviewer-marks.json` too, with
  `owed: []`, IM26 among the unmeasured, and one `note` line (`interviewer_leg.REMOTE_MARKS`); the step reads *none owed
  on the remote profile*. Locally nothing changes: the five speakers of FR-5 / call 9 still speak through the seam.
- **Why.** keel-web reads `window.__keelSpeech` only under `import.meta.env.MODE === "test"`
  (`useSpeechRecognition.ts`, `useRecorderFallback.ts`, `useMicStream.ts`) and staging serves the production build, so
  the seam was ignored there and the box never left *listening* / never drew its card. The AI walk already skipped on
  remote (`interviewer_leg._leg`); the text link's speak step had no such gate. The eval's own gap, not the product's:
  no DRIFT entry.
- **Seen in** the four remote journeys of 2026-10-17 ~19:25 local (`make eval K="s005 or s006 or s007 or s014"
  PROFILE=remote`): `runs/20261017T191744Z-s005-countly`, `runs/20261017T191954Z-s006-paidly`,
  `runs/20261017T192220Z-s007-mulchrun`, `runs/20261017T192433Z-s014-green` -- S-005 / S-007 timed out waiting for
  `main .sot[data-state="writing"]`, S-006 / S-014 for `iv-mic-done`.
- **Checked behind the same gate already:** every other `add_init_script` of the speech seam (`SPEECH_SEAM`,
  `recorder_seam(follow_up_cap_ms=...)`, `FLOW_TIMELINE` in Try it yourself and the AI link) and `_page_cap`'s read of
  the keel-web checkout sit after the interviewer leg's remote return. The text follow-up screen reads the DOM only.
- `make unit`: **2,535 passed / 55 skipped** (+3 in `tests/test_follow_up_ladder.py`: remote installs no
  `__keelSpeech` and `speak` is None, local still speaks, the remote card owes nothing).
