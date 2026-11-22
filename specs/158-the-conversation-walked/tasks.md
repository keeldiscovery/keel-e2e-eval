# Spec 158 -- tasks

Base: master `0d7d07ba`. Worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-158`, branch
`158-the-conversation-walked`. Starts only once keel-cloud 263 and keel-web 245 are on their masters.

- [x] T1 FR-1 `story_screens.py` on the beats: `said_turns`, `reading_of`, `limits_read`, the long beat-3 answer, the
  silence hook, the correction, the no-button rule.
- [x] T2 FR-2 the collector: orb states, folded transcript, the cost line, silence confirms.
- [x] T3 FR-5 the solution and money fronts, the spoken window.
- [x] T4 FR-4, FR-6 the three views' legs re-run, the report, DRIFT; `make e2e-157 PROFILE=eval` green on the local
  stack; this file's sections filled.

## Gate / Commits / Judgement calls

Built 2026-11-22 from 10:05 ET by a builder (Claude Opus 5.5) off `origin/master` `82787661` (the spec's three commits on
`0d7d07ba`). The stack served the sibling checkouts `stack.toml` resolves -- `/Users/athulrajeev/Documents/projects/
keel-cloud-docs` and `.../keel-web`, the main checkouts: keel-cloud-docs master **`8927987c`** (263 at `69158457` + 263b:
the drafted cost before the boxes, merged while this was built) and keel-web master `1397c55e`, which moved to **`63c82b2c`**
(246 polish: the boards' layout, the frames, the e2e's times) between the first run and the run of record (vite serves
the working tree). Nothing paid; nothing merged or deployed.

| Check | Result |
|---|---|
| `make unit` (`spec 158` at `4baaa6c` + this file, keel-cloud-docs `8927987c`, keel-web `63c82b2c`, 11:16-11:22 ET) | **5,968 passed / 31 failed / 126 skipped** -- the 31 reds are the pre-existing mirrors (23 in `test_cloud_245_250_248_web_186_190_mirror_154`, one each in the 144 / 148 / 149 mirrors, `test_backtest_host`, `test_credits_at_begin_088`, `test_follow_ups_075`, `test_instruction_compare`, `test_report_marks`); none in a file this spec touches. `tests/test_three_views_157.py` (36, moved onto keel-web 245) and `tests/test_conversation_158.py` (13, new) green |
| `make e2e-157 PROFILE=eval`, first run (`f8a3155`, keel-web `1397c55e`, 10:33-10:53 ET, `runs/157/8927987c-1397c55e/20261122T153341Z`) | **12 of 13 legs green**: every founder leg green; FR-2 money · avatar failed once -- the AI link's third-person check stood listening after the walk's *No* (the words fell between the recorder's windows; the stranger's walk is 157's, unchanged by 158), fixed in the harness (`said_again`, judgement call 9) |
| `make e2e-157 PROFILE=eval`, **the run of record** (`4baaa6c`, keel-cloud-docs `8927987c` + keel-web `63c82b2c`, 10:57-11:16 ET, `runs/157/8927987c-63c82b2c/20261122T155742Z`) | **13 of 13 legs green, 210 named checks, none failed** |
| its log scan | no HeyGen, no OpenAI, no Anthropic host contacted; no paid adapter named; Keel AI's clips FakeSpeech at 0 µUSD |

| Leg | Result | What held |
|---|---|---|
| FR-1 (a) | **green** | two problem projects by voice: the opening (the begin screen's orb), the five questions verbatim, no button but the orb on any screen, the orb *speaking > listening > hearing > writing > speaking* through every beat, beat 3 into its red crosses named by the readback and closed by the quiet (`done: true`), the folded line, beat 4's sentence + *Right?*, beat 5 only because owed, the boxes (no cost label) and the story by the quiet, the window page (no orb, stored), Prevalence with the story's event; the long telling: 2,119 characters sent whole, kept whole in `project_story`, four crosses (*I kept the four that matter most*), *only the ones in Europe* narrowing the condition, the cost drafted (`costDrafted` true) on the seventh line |
| FR-1 (b) | **green** | the which-problem page (no orb, both problems listed with their frames), *A new problem*, its conversation and the return trip picked, the pick, the replay (no cost box, the turn line, the quiet, nothing corrected), *Runcheck, in blue* (the colour written `#2f6db5`, the drop zone), beat 2 into two ticks and a cross, the idea's boxes and build, the name in the story at full opacity, inside its frame, unclipped, 27 px, in the brand's colour, the icon in it; Compatibility, Relative advantage pre-filled |
| FR-1 (c) | **green** | the pages, both conversations, *Use Runcheck*, the orb moment (*This is the problem, and this is Runcheck. Now, will they pay for it?*, the idea's box lit, the quiet, nothing corrected), the persona pre-filled, one PROJECT charge, the link; then *or just the name* (`offerName`, a PROBLEM parent), its orb moment with the name alone, the persona step |
| FR-1 (d) | **green** | as 157: resumed on the window page, calibrated, refused on a drained grant, locked once, a link sent |
| FR-2, nine legs | **green** | 157's legs unchanged (FR-4): the story cards' clips, the gate, the anchor, the check, the views and the No ending each |

## Commits

| Commit | Task | FRs | What |
|---|---|---|---|
| `8958ebb` | T1 | FR-1 | `harness/story_screens.py` on the beats (the fixtures on 263's beats, `long_beat_3`, the correction, `wake`, the silence, the orb's log, the no-button read, `StoryWalk` / `IdeaWalk` / `MoneyReplay`, the pages); `stack/ledger.story_turns`; 157's mirror tests on keel-web 245 |
| `13da431` | T2 | FR-1, FR-2, FR-3 | `evals/three_views.py`: the problem leg on the beats and its checks (the collector: the orb's states, the folded line, the cost line and `costDrafted`, the boxes and the story by the quiet); FR-1 (a)'s two projects; the window page |
| `f8a3155` | T3 | FR-5 | the solution and money fronts: `idea_leg`, `fr1_b`, `fr1_c`, `money_by_name` |
| `4baaa6c` | T4 | FR-4, FR-6 | the report's *The beats*; the first run's fixes; the avatar walk's second say; `tests/test_conversation_158.py`; README and AGENTS paragraphs |
| (this) | T4 | FR-6 | runs/DRIFT.md #107-#109; this file |

## Judgement calls

1. **The stack ran the main sibling checkouts, at their masters as they moved.** `stack.toml`'s `../keel-cloud-docs` and
   `../keel-web` resolve to `/Users/athulrajeev/Documents/projects/...` (not the `wt/` copies). keel-cloud-docs master
   was `8927987c` (263b merged: the cost drafted at the last beat) when the stack booted, and keel-web master moved from
   `1397c55e` to `63c82b2c` (246 polish) under the running vite between runs. Both are what the coordinator merged; the
   legs were written to pass either way on the cost (the brief's note) and hold on both webs.
2. **The window stays a page.** Spec 158 FR-5 asks for *the spoken window after the story*; keel-cloud 263 FR-11 and
   keel-web 245 FR-13 (the founder, 2026-11-22) keep 244's window page and build no spoken window. The leg holds the page
   (no orb on it, `PUT context/window` 200) and Prevalence; no spoken window is walked.
3. **No acceptance pair.** 157's FR-1 (a) compared the typed and the spoken paths; keel-web 245 has no typed path (spoken
   only). FR-1 (a) tells two spoken projects instead -- the script's own words (every reading scripted, the cost heard)
   and the long telling (the echo's readings, a correction, the cost drafted) -- so both roads to the cost line and both
   reading paths are walked, and FR-1 (b)'s which-problem page has two problems to list (with one it is skipped).
4. **The long telling is the script's own vocabulary.** Beat 1 is said *Payroll practitioners in small teams* (the
   script's people, said longer) so the draft is code's and the cost is drafted; beat 3 is the script's three limitations,
   two more (*Managers take days to answer their questions*, *The report comes out late in the day*) and the script's
   cost, told over 2,119 characters (under the fake transcriber's 4 KB). The four kept come first, a sentence each,
   because the fake reader reads an unscripted beat 3 a sentence a row; the fifth, the cost and the telling are one long
   last sentence. No trade, company or title beyond the script's.
5. **"`GET story` holds the words whole" is read off the store.** 263's `StoryView` serves the slots and an unanswered
   beat's `draft`, never the answered words; the leg holds the PUT's text (2,119 characters, 200, no 240 cut) and the
   stored turn (`project_story.story -> turns -> 3`, a plain `SELECT` in `stack/ledger.story_turns`; skipped by name on the
   remote profile).
6. **The cost check passes either way.** Before the confirm the boxes are asked for a cost box only where a cost is known;
   after the build the cost is the story's seventh line (the build's `costLine`: six scenes, then the cost, then the ask),
   and `costDrafted` is true exactly where nobody said it. On `8927987c` the long telling still reached the boxes with no
   cost (the scripted beat 5 skips the fake's `draft_cost`: DRIFT #107).
7. **The orb's states are logged, not sampled.** `ORB_WATCH` (a MutationObserver init script) records every change of the
   orb's `data-state` with the path; a beat holds *speaking > listening > hearing > writing > speaking* in order from the
   first entry on its path. The quiet is let pass only once the orb has spoken after the founder was heard and the mic is
   open again (`await_quiet`), because `__keelSilence()` answers whatever quiet wait stands.
8. **The opener and the begin screen.** `wake` presses a guide sheet's Skip, then taps the begin screen's orb where it
   stands 1.5 s with no sheet coming. After the opener's Skip the begin screen stood every time (DRIFT #108), so the walk
   taps twice there; the problem projects started from the market step drew no opener at all.
9. **The avatar walk says an unheard answer again** (`evals/three_views_strangers.py`, 157's leg): the money link's check
   once stood listening after *No*; the walk now repeats the same words where the same window still listens ten seconds
   on (at most twice, `said_again` on the row). The run of record needed none (`said_again` 0).
10. **The name-only money study** is walked to the persona step and noted on the leg (no lock fixture in keel-cloud yet).
    Its offer name is the script's own product name (*Runcheck*).
11. **The idea's colour is said in words** (*Runcheck, in blue*: no script entry, so the fake's echo writes `#2f6db5`);
    the brand's name in the story is probed while it plays (opacity, inside the frame, unclipped, at least 12 px, the
    colour), the clearest sample kept.
12. **One commit per task, by file where the work is one module.** T1 is the page objects whole (the beats, the collector
    the walk waits on, the fronts' page objects share `Conversation`); T2 is the problem leg with (b) and (c) still 157's;
    T3 moves (b) and (c); T4 the report, the run's fixes and this file.
13. **The stand-in keys stay `e2e-eval:157:`** and the report stays `runs/157/<cloud>-<web>/`: `make e2e-157` keeps its
    name and its folder.

## DRIFT written
- **#107** (keel-cloud, the fakes): a scripted last beat skips 263b's drafted cost, so the boxes draw no cost box.
- **#108** (keel-web): after the stage opener's Skip the begin screen stands; Keel says *Ready?* only after the orb is
  tapped (245 FR-3).
- **#109** (keel-cloud, the fakes; words): a correction after beat 4's readback replaces the condition (*in Europe*) and
  reads back *only those who in Europe*.

## Open
- The idea beats' *Next* column in *The beats* reads `-` (the idea walk does not record where a beat went); cosmetic.
- `PROFILE=remote` not run (the coordinator's).

