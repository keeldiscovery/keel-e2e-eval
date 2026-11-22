# Tasks -- Spec 157

One commit per task, in order; each commit message names its FRs. Tick as you go. Fill the Gate / Checks table and the Judgement calls section before handing back.

- [x] T0 FR-1 the founder's legs (a)-(d) against the stack with the fakes
  `harness/story_screens.py` (the founder's half): the cloud's own fixtures read off the checkout the stack runs
  (`fake-readings.json`'s `heard` words, `example-prevalence.json`), `story_runtime_script` (the scripted runtime's
  answers for a story-defined project), `StoryWalk` (241: the opening, the seven turns typed or spoken through the
  seam, the boxes, the building screen, the story), `SolutionStart` (242's start), `IdeaWalk` (242: still the problem,
  the three turns with the brand, the boxes, the day with the idea). `evals/three_views.py`: `Run` (a fresh founder on
  her own AI through the code story, the runtime reloaded per scope), `fr1_a` / `fr1_b` / `fr1_c` / `fr1_d`, the lock on
  a stand-in Keel's door (`lock_once`, the drained grant in (d)), `retry_questions`, `send_link`.
  `tests/test_three_views_157.py`: the machinery with no stack and the mirror of the subjects. runs/DRIFT.md #103.
- [x] T1 FR-2 the stranger's nine legs across the three views
  `evals/three_views_strangers.py`: per study (the problem of FR-1 (d), the solution of FR-1 (b) -- calibrated and locked
  here, `lock_the_solution` -- the money of FR-1 (c)) the wire's checks (the story up the chain, a `clipId` on every
  served card on the first read and once read, the story wording of the gate and the anchor, the idea's story and the
  brand, the third-person check) and the three views: `text_view` (`story_screens.StoryLinkText`: the order screener ->
  story -> gate (-> idea card -> idea's story), the story card, both chips, the voice bar and the lettered bubbles on every
  card, the answers sent; a second link's No on the gate / anchor / check ending it), `avatar_view` (the kind's AI
  interviewer set up on a stand-in Keel's door, two AI links walked by voice through the seam: the hand-overs, her return,
  no *Type instead*, Back on every item, the No ending it), `copilot_view` (two calls planned on the wire, the card
  headless on spec 154's fake sources: the set-up steps by their buttons, the strips, *Show the story* / *Story again* /
  the idea's story growing the window, measured and shrunk, the stills, Finish -> done; the No on the gate ending the
  questions). `three_views.open_sent` passes the account's first *Interviews · How it works* page.
- [x] T2 FR-3 make e2e-157 and the report; README paragraph
  `make e2e-157` (`evals/e2e_157_three_views.py`: one test, every leg in order, the report written in a `finally`) and
  `evals/three_views_report.py` (`runs/157/<cloud sha8>-<web sha8>/report.md`: the head, the log scan, the table of legs,
  every named check with a failure's screen and view; `log_scan` reads keel-cloud's log of the run's window for a vendor
  host, a paid adapter's name and the clips' measured cost). README *The three views, end to end*; AGENTS.md paragraph.

## Judgement calls

1. **The founder says keel-cloud's own words.** The story's seven turns and the idea's three are the `heard` words of
   keel-cloud's `src/main/resources/keel/story/fake-readings.json` (259 / 260's fake script), read at run time off the
   keel-cloud checkout the stack runs (`story_screens.said_turns`, `said_idea`), so the scripted readings answer, the
   build reaches `ready` on the script's own draft and room, and no trade word is written in this repository.
2. **The runtime's script for a story-defined project** is the 01-countly study of the project's scope
   (`vectors_script.generate` on `scope_journey.problem_entry` / `solution_entry` / `money_entry`: the lists, faces and
   readings the scripted journeys already walk) with three answers made the story's (`story_runtime_script`):
   CONTEXT_INTERPRET from the story's slots, every PROBLEM calibration answer's Prevalence fields keel-cloud's own
   `example-prevalence.json` (259 judgement call 20: E7 / E9 read them against the story), part 1's screener the story's
   condition (*Do you {only those who}?*), and the anchor's event the story's. The calibrations are walked by the existing
   `corpus_scenario.leg_calibrate` with `strict=False`. The runtime is restarted per scope (`Run.load_runtime`), its
   cursor started past a chain the project already took (`consumed`).
3. **A fresh founder on her own AI.** Each run registers its own stub identity (`stack/remote.register_cell_identity`,
   both profiles) and signs it in through the code story with the runtime home emptied first, so the account is OWN and
   every job is the scripted runtime's. **Keel's door is a stand-in** (`stack/ledger.py`, keys `e2e-eval:157:`) only
   around the lock -- so the one PROJECT row the ledger shows is the product's own, at the lock -- and around the avatar's
   recording; the lock's RESPONDENT_QUESTIONS job, started on Keel's door where this stack has no key, is then written on
   the own door by `POST questionnaire/retry` (the screen's *Try again*). The remote profile refuses every stand-in: the
   drained grant, the charge and the avatar are skipped there by name.
4. **Typed and spoken, where each is walked.** FR-1 (a): one project by *I would rather type the answers*, one through
   the spoken screen (Start, the seam's recorder, the hands-free mic's own pause, `story/transcribe` heard by the stack's
   FakeTranscriber -- typed text in, the same text out; *yes* said on turn 4, *that is all* on turn 6); (b): the problem
   typed, the idea's three turns spoken (*Tap to talk* first: the start's navigation is no tap, 242 judgement call 7);
   (c): typed. The boxes' and the stories' yeses are pressed on both paths.
5. **The money legs ran** because keel-web 243 landed (`9147af63`) while the batch was being built: the stack's keel-web
   checkout was already at it when the first full run began; `fr1_c` runs only where `src/components/money/MoneyStart.tsx`
   is in the checkout and is *written, not run* otherwise.
6. **No new scenario.** `evals/e2e_157_three_views.py` has no `test_` prefix: `make eval` never collects it and the
   scenario set stays as it was; `make e2e-157` names the file. The report and the bundle go under `runs/157/<cloud
   sha8>-<web sha8>/` (the report beside a `<stamp>/` bundle), so a rerun on the same shas keeps both runs' bundles and the
   newest report.
7. **Each item is answered with what the card offers first.** The text view takes an item's escape where it has one, else
   its first bubble (Importance's *Nothing else* after one pick); the avatar says the first option's words (the bubble's
   letter dropped); the copilot presses its first answer. The legs judge the views, not the answers: no standing is held.
8. **Back on every question card** is held on the AI sheet's items; the screener, the gate and its story question are
   the link's opening and draw no Back on keel-web 243 (recorded in each row, not judged).
9. **DRIFT #103 and #104 are failed checks by name and walked past** (`stop=False`): the window screen and the forward
   press in (a), the resume in (d); a link's first read without its clips, then read again until they are there.
10. **The copilot's first-person line** is spec 154's stand-in (`stack/ledger.stand_in_first_person`): a call on a study
    that holds the idea waits on keel-cloud 248's FIRST_PERSON job, which runs on Keel's AI alone (off on this stack).
11. **The mirrors that were red before this spec stay red** (31 on master's suite against these siblings: the price
    version 17 -> 20 of keel-cloud 259 / 260, spec 154's copilot selectors, the How it works page): re-cutting them is
    not this spec's; `harness/interviews_screens.Interviews.walkthrough` does not read today's *Interviews · How it works*
    page, so the legs pass it by their own `open_sent`.

## Gate / Checks

`make unit` with the main checkout's `.venv` (`PY=/Users/athulrajeev/Documents/projects/keel-e2e-eval/.venv/bin/python`); the
local legs on `make up PROFILE=eval` (this worktree's stack: keel-cloud-docs `78237f87` built by `bootRun`, no other Gradle
run up; keel-web served `vite --mode test` from its checkout). Times ET, 2026-11-21.

| Check | Result |
|---|---|
| `make unit` before (base `3579ec3`, keel-cloud-docs `78237f87`, keel-web `8a6b05c9`, 20:52-20:58) | **5,911 passed / 31 failed / 125 skipped** |
| `make unit` after (`spec-157`, keel-cloud-docs `78237f87`, keel-web `9147af63`, 23:11-23:17) | **5,950 passed / 31 failed / 125 skipped** (+31 in `tests/test_three_views_157.py`; the same 31 reds, none in a file this spec touches: the mirrors of specs 144 / 148 / 149 / 154, the price version 17 vs keel-cloud's 20, `test_backtest_host`, `test_follow_ups_075`, `test_instruction_compare`, `test_report_marks` -- judgement call 11) |
| `make e2e-157`, the run of record (keel-cloud-docs `78237f87` + keel-web `f133beac`, 23:29-23:41, `runs/157/78237f87-f133beac/20261122T042947Z`) | **7 of 13 legs green**; the six others fail only on runs/DRIFT.md #103-#106 (below) |
| log scan of that run | no HeyGen, no OpenAI, no Anthropic host contacted; no paid adapter named; Keel AI's clips FakeSpeech at 0 µUSD |

| Leg | Result | Why |
|---|---|---|
| FR-1 (a) typed + spoken to Prevalence, the 259 pair | **failed** (run) | DRIFT #103: the window screen never drawn after the story's yes, the forward press opens the seed chat; every other check held -- both paths' seven turns (spoken: every utterance written down as said), the boxes, the build `ready` on the scripted room, Prevalence with the story's event, **the acceptance pair equal on the wire** |
| FR-1 (b) the solution start to Compatibility | **green** (run) | the start with nothing, the problem created and agreed, the return with it picked, the pick (`parentProjectId`), still the problem, the three turns spoken with the brand's colour, the boxes, the day with the idea, Compatibility, Relative advantage pre-filled with the two benefits |
| FR-1 (c) the money start to one charge and the links | **green** (run, on keel-web 243 at `9147af63` / `f133beac`) | screen 1's create and the story, back on screen 2, the solution created and its idea, *Use {name}*, the persona pre-filled, Existing sacrifice's prompt the story's cost line, the money calibrated, one PROJECT charge of 2,000, the decision-maker's link |
| FR-1 (d) the defined project from the list | **failed** (run) | DRIFT #103: it resumes on Prevalence, not the window screen; *Defined, not sent* under its study, calibrated, refused 422 on a drained grant (100), locked once with one PROJECT charge, its questions READY, a link sent -- all held |
| FR-2 problem · text | **failed** (run) | DRIFT #104 (the first read without every card's clip) and #105 (Frequency's cells unlettered); the order, the story card, both chips, the voice bar, the answers sent and the gate's No ending it held |
| FR-2 problem · avatar | **green** (run) | the hand-over, her return, no *Type instead*, Back on every item, the gate's No ending it |
| FR-2 problem · copilot | **green** (run) | *Show the story* then *Story again*, the window 400 x 360 under half a 1280 x 720 viewport with the card shown, back with the gate up, the stills, Finish -> done; the gate's No ending the questions |
| FR-2 solution · text | **failed** (run) | DRIFT #105 (Relative advantage's four unlettered); the anchor's wording, the idea's story and the brand on the wire, the order story -> anchor -> idea card -> idea's story, the anchor's No ending it held |
| FR-2 solution · avatar | **green** (run) | two hand-overs (*Let me show you how ...'s idea would go*), her return, Back, the pilot, the anchor's No |
| FR-2 solution · copilot | **green** (run) | three story moments (the idea's story after the idea), the first-person line a stand-in (judgement call 10) |
| FR-2 money · text | **failed** (run) | DRIFT #106 (no `ideaStory` on the decision-maker's link: the order stops at the idea card) and #105 (the cost box's Hours / Amount); the story introduced in the third person, the check card, its No ending it held |
| FR-2 money · avatar | **failed** (run) | DRIFT #106: one hand-over, not two; the check, Back, the pilot, the check's No ending it held |
| FR-2 money · copilot | **green** (run) | the check strip's story press, then the idea's story; the check's No ending the questions |

Not run here: `PROFILE=remote` (the coordinator's, never a builder's); nothing paid.
