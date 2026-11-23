# Tasks -- spec 159

Base: `origin/master` `239f298` (the spec). Worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-159`, branch
`159-the-orb-walked`. Built 2026-11-23 from 11:05 ET by a builder (Claude Opus 5.5). The stack served the sibling main
checkouts `stack.toml` resolves: keel-cloud-docs master `8bd57d6f` (267 merged, contract 84) and keel-web master
`41d18480` (253 merged; 254 still on its branch). Nothing paid; nothing merged or deployed.

- [x] T1 `harness/interviews_screens.py` formats and the popup (FR-4); `harness/interview_charge.py` (no new charge).
- [x] T2 The orb view: the intro with the orb, the film first, the opening, the gate and items; the state collector (FR-1).
- [x] T3 The avatar view moved; the same-passage assertion (FR-2).
- [x] T4 Speak or tap: the letter, the words, the tap, the chip, the refused mic by taps, no typed box (FR-3).
- [x] T5 Report + DRIFT; the contract-84 mirrors (FR-7); `make unit`; `make e2e-157 PROFILE=eval` on the local stack; tasks.md with the commits, the runs and judgement calls.

## How each FR is met

| FR | Where | What the walk holds |
|---|---|---|
| FR-1 | `evals/three_views_strangers.orb_view`, `link_walk`, `wire_checks`, `film_first_checks`, `orb_screen_checks`, `orb_states_check`; `harness/story_screens.ORB_INTERVIEW_WATCH` (+ `stage_sequence`, `orb_answer_runs`, `never_drawn`, `clip_refs`, `cards_carrying_a_clip`) | the wire: `speaker` ORB, `face` null, `formats` [TEXT], every ClipRef on `/v2/clips/`, `clips.problem` null, no card `clipId`; the screen: `ai-intro[data-speaker=ORB]` with `intro-orb`, *Keel AI will ask you ...*, *It is an AI interviewer, not a person.*, the consent, the mic test, Start, no `choice-*`; the stage ORB with no `<video>`; the film first (`ai-story[data-kind=problem][data-first]`, no hand-over line), then the opening spoken before the first question; the orb *speaking > listening > hearing > writing* through an answer; no voice bar, no *Read and tap* on any screen; the response named TEXT |
| FR-2 | `avatar_view`, `same_words`; `stack/ledger.speech_clip`; `story_screens.speech_key` | `speaker` AVATAR, Daphne, `formats` with AI_INTERVIEWER, the clips on the link's own route, `clips.problem` null, no card `clipId`; the film first then the opening; Daphne back after the film and each hand-over; Back on every item; the idea's hand-over line on solution and money; the No ends it; the opening and one item: the face's recorded script keyed as `KeelVoice.key` equals the orb's `speech_clip.cache_key` |
| FR-3 | `link_walk(speak_or_tap=..., story=..., refused=...)`, `speak_or_tap_checks`, `no_typed_box_check`; `interviewer_screens.speech_seam(refused=True)`, `Player.refused_mic_test`, `typed_boxes` | *B* holds the second row; the first row's words hold it; a tap holds it; the chip said (one link) and tapped (the refused link); the refused link walked by taps alone to its end with no `textarea` / `input[type=text]` on any screen |
| FR-4 | `popup_checks`, `dry_run_on_the_orb`; `interviews_screens.FORMAT_NAMES` / `KEELS_VOICE` / `_step_one`; `interview_charge.orb_charge_faults` | New link: *Keel's voice* (checked) and *AI interviewer*, two rows; the NOT_SET_UP kind card's `try-keel-voice` opens `/interviews/try/` on the orb (intro orb, mic test, Start, a question asked) and the ledger moves nothing; per study, every CARD_SPEECH row 0 and no charge but PROJECT / INTERVIEWER_RECORDING |
| FR-5 | `wire_checks` (every orb clip 0.312 s), `fetch_clip`; the report's log scan (unchanged) | FakeSpeech's clip served to a cookieless stranger as audio; no vendor host or paid adapter in keel-cloud's log |
| FR-6 | `copilot_view` / `copilot_walk` unchanged | the three copilot legs as 157 |
| FR-7 | `evals/three_views_report.orb_markdown` (*The orb*); `runs/DRIFT.md` #104-#106 status, #112; mirrors: `tests/test_three_views_157.py`, `tests/test_interviewer_screens.py`, `tests/test_money_cards_redrawn_118.py`, new `tests/test_orb_159.py` (contract 84 pinned at `1002eb90...`) | |

## Judgement calls

1. **One commit for T2-T4.** The orb view, the avatar view and speak-or-tap are one walker (`link_walk`, the AI player is
   one player now) in one module; splitting them would have committed half a walker. T1 and T5 are their own commits.
2. **Four orb links a study (three on money), plus the phone.** By voice (a story told; the letter, the words, the tap),
   the story's chip said aloud, the microphone refused (all by taps), and the No; the decision-maker's link has no
   story question, so no chip link. 158b's phone story card moved onto the orb (`phone_film`: the film on the AI stage,
   measured as before) since the text player's card is no longer reached.
3. **The ways are owed across the voice links.** A problem link has two items with rows (Frequency's cells are not
   rows; its *I can't recall* is a chip): the letter and the tap go to one-pick items, the words to any item with rows
   but the price ladder (`way_for`), and what the first link had no item for is walked on the chip link. Run 2 showed
   why the tap needs a one-pick item: a tap on *pick one, then one more* moves straight to its second ask, so its row is
   never read lit.
4. **The chip said aloud is held to the tap's meaning** (`anchorChip` CANT_RECALL), `stop=False`: on keel-web
   `41d18480` it is kept as the story's words and the interview goes on (DRIFT #112). The tap is held on the refused
   link (the interview ends, `anchorChip` CANT_RECALL, no answers -- the existing chip rule).
5. **"A typed box" is the spec's selector, literally:** `textarea, input[type=text]` anywhere on the page, logged on
   every DOM change (`ORB_INTERVIEW_WATCH`) and read on every question. The AI sheet's number box is an `<input
   inputMode=numeric>` with no `type`; it is not counted (254 does not retire it), and the refused walk would give such
   a box with no escape its digits (`field: 3`) -- none was met: every number item served an escape chip.
6. **`interview_charge.PRICE_VERSION` stays 17.** The pinned older suites read 17 against keel-cloud's 20 (158's
   pre-existing mirror reds); spec 159 adds `PRICE_VERSION_267 = 20` and `CARD_SPEECH` at 0 for its own rule and
   pins them against `InferenceCharge.java` in `test_orb_159.py`.
7. **The same words are read off the keys.** `speech_clip` keeps no words (only `cache_key`, the sha256 of voice and
   words), so the face's clip's `script` (the stored recording, `corridor.lock.recordings[role].clips`) is keyed as
   `KeelVoice.key` keys it and held equal to the orb clip's row; one row read by both. Items are matched across the
   two links by dimension (item ids are per token).
8. **Try it yourself is walked on Keel's door.** On the founder's own AI every kind card offers the primary *Try it
   yourself* (no per-kind interviewer list); FR-4's card is the NOT_SET_UP one on Keel's door, so the dry run runs
   inside the avatar leg's stand-in, before the face is set up, on the problem study.
9. **Without a story** (the opening, then the problem passage) is not walked: all three studies of the run are built
   with their film; keel-web 253's own e2e covers the film-less orb link.
10. **The FORMAT_NAMES move.** `FORMAT_NAMES` is New link's two rows (`TEXT` *Keel's voice*, `AI_INTERVIEWER`);
    `STORED_FORMAT_NAMES` keeps *Let them choose* for a stored CHOICE link; `TEXT_ONLY` is *Keel's voice*, `READ_AND_TAP`
    stays as the retired name; `corpus_scenario`'s Format column and `interviewer_leg`'s rows read the two rows.
11. **The 157 selector mirror** drops `StoryScreen` / `CardVoice` (not walked any more; 254 deletes them) for the AI
    player's, the intro's, the sheet's and the kind card's ids; `ai-type` / `ai-typed` are skipped once keel-web 254 is
    in (`story_screens.web_retired_typing`).
12. **New checks are `stop=False`** where a miss is a product finding the walk can go past (speak or tap, the chip said,
    typed boxes, FakeSpeech's length, the idea's hand-over); the wire's and the screens' others stop the leg.

## Gate / Checks

`make unit` with the main checkout's `.venv`; the local legs on `make e2e-157 PROFILE=eval` from this worktree (the stack
booted and torn down by the run itself; keel-cloud-docs `8bd57d6f` by `bootRun`, keel-web `41d18480` by `vite --mode
test` on 5173; the keel-web 254 builder's own vite on 5390 never collided). Times ET, 2026-11-23.

| Check | Result |
|---|---|
| `make unit` before (base `239f298`, a detached copy, 11:13-11:20) | **5,984 passed / 48 failed / 127 skipped** |
| `make unit` after (the tree of `9464d06`, 11:58-12:05) | **6,012 passed / 45 failed / 127 skipped** -- no new red; three of the base's reds fixed (`test_interviewer_screens`: `choice-talk`, `choice-write`, *Read and tap links can be made meanwhile.*); the 45 are the base's (the mirrors of specs 132 / 144 / 148 / 149 / 154, credits 088, follow-ups 075, founder walk 076, guide sent marks, the instruction / report-marks / brief-facts tests, open link 092, sharing 130, backtest host, classifier guard). `tests/test_orb_159.py` 20 green (21 at `b2da9d6`, run alone), `test_three_views_157.py`, `test_conversation_158.py`, `test_interviewer_screens.py`, `test_money_cards_redrawn_118.py` green |
| run 1 (`b4bb934`, 11:27-11:54, `runs/157/8bd57d6f-41d18480/20261123T162701Z`) | **11 of 13**: problem · orb failed on the harness (the words and the tap had no item left on the problem link) and on DRIFT #112; solution · orb on DRIFT #112 alone |
| run 2 (`9464d06`, 12:02-12:29, `.../20261123T170225Z`) | **11 of 13**: problem · orb and solution · orb on DRIFT #112; problem · orb also on the harness's tap (a tap on *pick one, then one more*; fixed in `b2da9d6`) |
| **run 3, the builder's run of record** (`b2da9d6`, 12:30-12:57, `.../20261123T173000Z`, 375 checks held) | **10 of 13**: every check spec 159 adds held but one -- DRIFT #112 (the chip said aloud), on problem · orb and solution · orb; FR-1 (a) failed on 158c's *one film* (a welcome sheet after the opener: DRIFT #113, intermittent, green in runs 1 and 2) |
| its log scan | no HeyGen, no OpenAI, no Anthropic host contacted; no paid adapter named; 95 Keel AI clips, FakeSpeech at 0 µUSD |

| Leg (run 3) | Result | What held |
|---|---|---|
| FR-1 (a)-(d) | (a) failed on DRIFT #113 alone; (b)-(d) green | 158's founder legs, untouched by 159 |
| FR-2 problem · orb | failed on DRIFT #112 alone | New link's two rows (*Keel's voice* checked); `speaker` ORB, `face` null, [TEXT], every clip on `/v2/clips/` (0.312 s), `clips.problem` null, no card `clipId`, the opening served cookieless as audio; the intro with the orb, the mic test, Start; the film first with no hand-over line, then the opening; the orb *speaking > listening > hearing > writing*; *B* holds the second row, the words the first, a tap the first (on the chip link); no voice bar, no *Read and tap*, no typed box; the response TEXT 201; both chips; the refused link by taps to its end (the chip tapped), no typed box; the gate's No; the film on a phone (fits); the ledger: no charge for the orb |
| FR-2 problem · avatar | green | Try it yourself on the NOT_SET_UP card opens the dry run on the orb and charges nothing; `speaker` AVATAR, Daphne, the face's own clip route, `clips.problem` null; the same words (the opening, Frequency); the film first, then the opening; Daphne back; Back on every item; the gate's No |
| FR-2 solution · orb / avatar | orb failed on DRIFT #112 alone; avatar green | as the problem's, with the anchor, the idea's story after its hand-over line, the same words on Compatibility |
| FR-2 money · orb / avatar | green | as above with the third-person check; the idea's story served and played (DRIFT #106 resolved); the refused link answered every item by tap |
| FR-2 · copilot (three) | green | 157's legs, untouched |

## Commits

| Commit | Task | FRs | What |
|---|---|---|---|
| `fa4c318` | T1 | FR-4, FR-7 | `interviews_screens` (`KEELS_VOICE`, `FORMAT_NAMES` two rows, `STORED_FORMAT_NAMES`, `_step_one`), `interviewer_screens` (the orb's words and ids, `speech_seam(refused)`, `Player.refused_mic_test` / `speaker` / `orb_state` / `typed_boxes`, *Keel's voice* lines), `interview_charge` (`CARD_SPEECH`, `PRICE_VERSION_267`, `orb_charge_faults`); the mirrors on 253 |
| `043d15e` | T2-T4 | FR-1 to FR-6 | `story_screens` (the orb's collector, `clip_refs`, `cards_carrying_a_clip`, `speech_key`, `web_has_orb` / `web_retired_typing`), `stack/ledger.speech_clip`, `three_views_strangers` (the orb view, `link_walk`, the avatar view moved, the same words, the dry run), `three_views.VIEWS` |
| `b4bb934` | T5 | FR-7 | the report's *The orb*; `tests/test_orb_159.py`; 157's mirror on the one player |
| `9464d06` | T4-T5 | FR-3, FR-7 | run 1's fixes (the ways owed across the voice links; the refused walk on the typing phase); DRIFT #104-#106 status, #112 |
| `b2da9d6` | T4 | FR-3 | run 2's fix: the tap on a one-pick item |
| (this) | T5 | FR-7 | DRIFT #113; this file |

## DRIFT written
- **#112** (keel-web): the story's *I can't recall one particular ...* said aloud is kept as the story's words (the
  interview goes on); only *I'd rather not say* is matched as a spoken chip.
- **#113** (keel-web, intermittent): a welcome sheet after the stage opener on the story's start (158c's one film), once
  in six conversations.
- Status lines: **#104** moot (contract 84 retires the cards' `clipId`), **#105** moot (the text player's cards are not
  reached), **#106** resolved on `8bd57d6f` + `41d18480`.

## Open
- keel-web 254 is not on master: the refused-mic walk met no typed box on `41d18480` because it taps the story's chip
  first; the run of record after 254 (the integrator's) re-reads it with `ai-type` / `ai-typed` retired
  (`test_interviewer_screens` skips them once `web_retired_typing`).
- When keel-web takes the spoken chip as the chip (DRIFT #112), the chip link ends at the story, and a problem link
  then has no item left for the tap (its one one-pick item takes the letter on the first link): the tap would have to
  be read on another link's one-pick item (a second problem-link walk, or the solution's). Flagged, not built.
- `PROFILE=remote` not run (the coordinator's).

