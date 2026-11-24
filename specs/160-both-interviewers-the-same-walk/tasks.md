# Tasks -- spec 160

Base: `origin/master` `55e7e83` (the spec). Worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-160`, branch
`160-both-interviewers-the-same-walk`. Built 2026-11-23 from 18:52 ET by a builder (Claude Opus 5.5). The stack served
the sibling main checkouts `stack.toml` resolves: keel-cloud-docs master `8bd57d6f` (contract 84) and keel-web master
`3b19090c` (256 merged). Nothing paid; nothing merged or deployed.

- [x] T1 The mirrors move (FR-1); the refused mic is a block (FR-2).
- [x] T2 The same walk on both speakers, recorded and compared (FR-3); the film, the replay mark, the last page (FR-4 to FR-6).
- [x] T3 The report's two-speaker section, DRIFT, `make unit`, the local run (FR-8); tasks.md with the commits, judgement calls and runs.

## How each FR is met

| FR | Where | What the walk holds |
|---|---|---|
| FR-1 | `harness/interviewer_screens.py` (`ai-start`, `MIC_BLOCK_ID` / `MIC_BLOCK` / `MIC_BLOCK_HOW` / `MIC_LABEL`, `ai_intro_heading(founder, n)` + `intro_founder`, `ORB_NAME` *Keel* / `ORB_STAGE_NAME` *Keel AI*, `ai_intro_spoken` / `ai_intro_asks` / `ai_intro_chips`, `AI_INTRO_MIC_LINE`, `INTRO_ANSWERS`, `face_mark`, the film's / replay's / tick's ids, `AI_REASON_DIDNT_CATCH` / `AI_SECOND_MISS_FREE` on 254's words; `Player.intro` reads the one button, the chips, the closed disclosure and the block; `mic_test` waits for `ai-start`; `start("ai-start")`); `evals/interviewer_leg.py` (the heading, `buttons == ["ai-mic-test"]`, her chip `face_mark` on the walk and the dry run); `evals/three_views_strangers.py` (`intro_checks`, `watch_film` -- `ai-film-begin` waited for and pressed --, `retired_checks`, the dry run presses Begin); `harness/story_screens.py` (`filmOrb` read as a retired id, `story-play` noted as the worded player's); the unit mirrors in `tests/` | the intro on both speakers: the headline, the spoken line, the one sentence, the chips, *What happens to your answers* closed with its three lines, `ai-mic-test` -> `ai-start`; `ai-story-orb`, `ai-story-go-on`, `ai-again`, `ai-mic-fallback` on no screen; her chip *{name} · AI interviewer* in `ai-caption` (large) / `ai-facecol` (small), the orb's *Keel · AI interviewer* in `ai-orb` (`chip_checks`) |
| FR-2 | `speech_seam(refused=True)` (`window.__micRefused`), `Player.refused_mic_test` / `allow_mic`; `blocked_walk`, `blocked_checks` | per study, one orb link and one face link: *Test your mic* refused -> `ai-mic-block` with its two lines, the button still *Test your mic*, no `ai-start`, 2 s later still nothing: no stage, no question; the mic allowed, *Test your mic* again -> *Heard: hello* and `ai-start` |
| FR-3 | `story_screens.ORB_INTERVIEW_WATCH` (`size`, `ids` of `WALK_IDS`, `words` / `lit`, `chip`, the `play()` stamps), `walk_steps` / `step_record` / `same_walk`; `speaker_walk`, `same_walk_check` (the avatar leg) | the orb's voice link and the face's link walked alike (the same ways from the start, the film's controls, the replay on the first item); every step's state, sizes, ids and words equal, else the check fails naming the step; 159's same words by clip key (`same_words`) unchanged |
| FR-4 | `film_controls`, `watch_film`, `film_checks`; `Player.film` (`FILM_JS`), `speaker_box` | on both: nothing inside the film, the speaker's box under it; two icons, no worded button; pause -> *Play the story*, `data-paused`, the drawing held 1.5 s; resume; start over draws it again; the board's words shown and hidden; at the end *Begin the interview*, 2 s with no `play()`, the phase still the film; after the press the opening's clip first and the speaker seen large. The founder's `define/story` player and 158's checks untouched |
| FR-5 | `press_replay`, `replay_checks` | on the first item of each compared link: *Hear the question again*, the item's clip (`data-clip`) played after the press, a new window recording; `ai-again` nowhere |
| FR-6 | `last_page`, `last_page_checks` | the tick before the title *Done. Your answers have gone to {founder}.*, *Microphone off*, *What is Keel?*, the served `done.thanks` not drawn |
| FR-7 | untouched: `copilot_view` / `copilot_walk`, `tv.fr1_*`, the ledger and charge checks, `PROFILE=remote` | |
| FR-8 | `three_views_report.orb_markdown` (*The two speakers*), `speaker_rows`; `e2e_157_three_views` passes the walks; `runs/DRIFT.md` | one row a study a speaker: the steps, the sizes, the verdict; where they part, both records |

## Judgement calls

1. **T1 and T2 are one commit** (as 159's T2-T4): the mirrors and the two-speaker walk share `link_walk`; the report went
   with them so the run could write *The two speakers*.
2. **What a step is.** The intro (`intro`, `intro+start`, `intro+block`; the mic test's asking / listening / writing are
   folded into it -- a microtask apart on one, not the other), the film (`film:<kind>`, `+begin`), the stage's
   `<phase>:<where>` (speaking, beat, listening, held, confirming), `done` / `ended`. `loading` and `sending` are not
   steps (a fetch's length), nor the one frame run 1 met in which the stage is shown on the Start tap while the flow is
   still `intro` (`intro:`, on both speakers alike). Per step the ids are the union of its rows (a frame drawn a moment
   late is still the step's).
3. **The ids compared are speaker-neutral** (`WALK_IDS`): the speaker's own box (`ai-orb` / `ai-facecol`) is `speaker`;
   ids only one speaker has by design (`intro-orb`, `ai-face`, `ai-caption`, `ai-face-state`, `ai-orb-state`) are not
   compared. On the film only the ids inside `ai-story` count (it covers the stage, z-index 40); under the intro and on
   the last page the hidden stage's ids do not count.
4. **The words lit**: the words drawn and that they lit from the first word are compared; how many were lit when the
   clip ended is reported, not compared -- an 80 ms timer against a 0.312 s clip (the orb, FakeSpeech) and a 1 s clip
   (the face, the fake renderer) races the clip's end on both (run 2: the face's solution walk had 7 of its 8 asked
   steps fully lit at the end, the orb's 8 of 8; every one lit from its first word on both).
5. **The face's link is walked as the orb's voice link**: a fresh `SPEAK_OR_TAP` (the voice link's own start), the
   story told, the film's controls, the replay on the first item. The chip-said link, the No links and the phone link
   are not compared (no face twin walked alike).
6. **The refused mic, one link a study a speaker** (FR-2's "one link per study, both speakers"). The refusal is
   `window.__micRefused` (keel-web's own fixture's name) so the walk can allow it again; Start is not pressed after (the
   link stays unanswered: no response, no charge).
7. **The story's chip by tap is no longer walked**: 159 tapped it on the refused link, which keel-web 256 no longer
   lets start. The chip said aloud keeps its link; the FR-3 tap way is still owed across the voice links (`way_for`,
   carried to the next study).
8. **`start_enabled` reads False where *Start the interview* is not drawn** (256: it appears only after the hello), so
   the interviewer marks' IM17 (*Start disabled before the test*) means the same on the new screen.
9. **The film at its real pace.** The seam sets no `filmScale` (keel-web's own fake sets 0): the walk needs a drawing
   that takes time to see pause hold it, and the film's end is waited for (up to 240 s) on every link.
10. **Nothing plays** is read off a wrapper on `HTMLMediaElement.prototype.play` in the collector, which stamps the
    element's `data-clip` (the one player swaps `blob:` sources and names the clip there).
11. **The chip is checked on the desktop viewport** the walks use; on a phone her chip hides with the sheet open (256
    judgement call 9).
12. **The dry run's chip** (`interviewer_leg`, S-0xx) is her `face_mark(..., try_run=True)` by the served face's name.
13. **A stale stub OIDC issuer** (pid 92364, started 2026-11-05 from a removed `wt/eval-140`) answers on 18090 for this
    profile; `stack.oidc.is_up` reuses it, as 159's runs did. Not mine: left alone.

## Commits

| Commit | Task | FRs | What |
|---|---|---|---|
| `c4b98ee` | T1-T2 | FR-1 to FR-8 | the mirrors, the block, the two-speaker walk and its steps, the film / replay / last page checks, the report's *The two speakers*, `tests/test_both_speakers_160.py` and the moved mirrors |
| `fbcccdb` | T3 | FR-3, FR-8 | run 1's reading: the on-stage `intro` frame is not a step; the report says how the asked steps' words lit; tasks.md drafted |
| (this) | T3 | FR-8 | `runs/DRIFT.md` #112 resolved, #113 status; tasks.md: the runs, the gate |

## Gate / Checks

`make unit` with the main checkout's `.venv` (`VENV=` on the make line); the local legs on `make e2e-157 PROFILE=eval`
from this worktree (the stack booted and torn down by the run itself: Postgres in Colima, keel-cloud-docs `8bd57d6f` by
`bootRun`, keel-web `3b19090c` by `vite --mode test` on 5173; the keel-web visual suite's vite on 5273 and Prism on 4010
never collided). Times ET, 2026-11-23.

| Check | Result |
|---|---|
| `make unit` before (base `55e7e83`, a detached copy, 18:55-19:02) | **5,999 passed / 55 failed / 130 skipped** |
| `make unit` after (`c4b98ee`, 19:10-19:16) | **6,037 passed / 46 failed / 130 skipped** -- no new red; nine of the base's reds fixed (the 256 mirrors: `test_follow_up_ladder` x2, `test_interviewer_screens` x4, `test_orb_159::test_keel_web_plays_the_orb`, `test_three_views_157` x2); the 46 are the base's (mirrors of 132 / 144 / 148 / 149 / 154, credits 088, follow-ups 075, founder walk 076, guide sent marks, instruction / report marks, open link 092, sharing 130, backtest host, classifier guard, `test_one_more_thing_075`) |
| `make unit` final (`fbcccdb`'s tree, 20:18-20:25) | **6,037 passed / 46 failed / 130 skipped** -- the same 46 as after `c4b98ee`, no new red |
| run 1 (`c4b98ee`, 19:16-19:46, `runs/157/8bd57d6f-3b19090c/20261124T001713Z`, 474 checks held) | **13 of 13 legs green**, no check failed; the two speakers *same* on all three studies (35 / 33 / 40 steps); read: a one-frame `intro:` step on both (made transient in `fbcccdb`) |
| **run 2, the builder's run of record** (`fbcccdb`, 19:47-20:17, `runs/157/8bd57d6f-3b19090c/20261124T004746Z`, 474 checks held) | **13 of 13 legs green**, no check failed; the two speakers *same* on every study (problem 34 steps, solution 32, money 39), the asked steps' words lit from the first word on both (10 / 8 / 10) |
| the log scans | run 1: 94 Keel AI clips, run 2: 95, every one FakeSpeech at 0 µUSD; no HeyGen, OpenAI or Anthropic host, no paid adapter |
| teardown | after each run: no keel container, no `bootRun`, no vite on 5173 (the gradle daemons 49488 / 72161 and the stub issuer 92364 predate this build and are not mine) |

| Leg (run 2) | Result | What held |
|---|---|---|
| FR-1 (a)-(d) | green | 158's founder legs, untouched (*one film* held: DRIFT #113 not met) |
| FR-2 problem / solution / money · orb | green | 159's wire, the orb, speak or tap (letter, words, tap across the studies), the chip said aloud taken as the chip (DRIFT #112 resolved), no typed box, the No; 160: the intro's headline, spoken line, sentence, chips, closed disclosure and one button; no retired id; the film's two icons, pause held, start over, the board's words, *Begin the interview* with nothing played for 2 s, then the opening first and the orb large; the replay mark on the first item (its clip again, the window again); the last page's tick and title; the orb's chip; the refused mic's block, nothing started, allowed again -> Start; the phone film; the ledger |
| FR-2 problem / solution / money · avatar | green | 159's (Try it yourself on the orb, the wire, the same words by clip key, the film first, Daphne back, Back on every item, the No); 160: the same intro with her name, the film / replay / last page as the orb's, her chip in the caption band (large) and her column (small), **the same walk as the orb's, step for step**, her refused mic's block and Start once allowed |
| FR-2 · copilot (three) | green | 157's legs, untouched |

## Runs

Two, both above: run 1 on `c4b98ee` and run 2 (of record) on `fbcccdb`, each 13 of 13. Nothing harness-side or web-side
failed; run 1's one reading (the on-stage `intro` frame) was equal on both speakers and is folded out since.

## DRIFT written

- No new web finding: keel-web 256 holds every 160 check on both speakers, and the two speakers walk the same.
- **#112** status: resolved on keel-web `3b19090c` -- the chip said aloud is the chip (`anchorChip` CANT_RECALL).
- **#113** status: not met in either run; kept open as intermittent.

## Open

- The integrator's run of record on the merged masters.
- The story's chip *by tap* is no longer walked anywhere (judgement call 7): the refused link that tapped it cannot start
  under keel-web 256. A second chip link (tapped) would put it back if wanted.
- The beat (*Take a moment.*) did not occur on these studies' links (no passage before an item with the film served), so
  the beat's step was not compared; where it occurs, the orb draws its chip in the beat and the face, by 256's judgement
  call 10, draws no caption band -- the same-walk check would name it at that step.
- `PROFILE=remote` not run (the coordinator's).
