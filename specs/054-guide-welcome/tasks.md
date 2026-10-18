# Tasks 054

Built against keel-cloud **as built** (keel-cloud-docs master `7c4d9a9` = spec 106, contract 20, read-only) and keel-web
080 **as specified** (keel-web `specs/080-guide-welcome/spec.md`, read-only; being built in parallel). This pass ran **no
stack** (`make unit` only): the journeys and the remote run are owed to the journey pass once 080 is merged.

## Corrections to the spec, from the cloud as built

- There is **no `ProjectSummary`** (106 judgement call 3: the guide is on the overview only). Wherever the spec says the
  summary, the eval reads `GET /v2/projects/{id}/overview` -> `Overview.guide {welcomeSeen, openersSeen[]}` (both
  required). FR-2 (a) reads the overview **the page received** (`GuideWire`), FR-2 (d) both the page's and the wire's.
- `POST /v2/projects/{id}/guide-seen {what: "WELCOME"}` -> **204, no body**, idempotent, no `expectedRevision`; 422
  `{rule: "guide", ...}` on a bad body; bare 404 on a foreign / absent / malformed id. G3 reads `Overview.revision` before
  the press, after it and after the eval's own repeat.
- **The context Save answers 202, not 200** (`proposeContext`, keel-cloud-docs `canon/openapi-v2.yaml`: it starts
  CONTEXT_INTERPRET and carries no `expectedRevision`). G3 holds the next founder write to *a 2xx on its first press,
  never 409* and records the status; the revision-neutrality proof is the overview's revision (above) and keel-cloud's
  own `VectorCorridorJourneyTest` (a revisioned PUT at the earlier revision is 200). The page's first revisioned write
  comes several revisions later (after the context and problem confirms), so it would prove nothing about the mark.

## Tasks

- [x] T001 FR-4 the marks: `evals/guide_marks.py` (the shape of `interviewer_marks.py`: `MARKS` rows of mark / record key
  / rule, `score`, `owed`, `scorecard` with `why_unmeasured`), **`GUIDE_MARKS_VERSION = 1`** with its history comment;
  G1 `welcome` once per project, G2 `welcome` skippable from the first frame, G3 `welcome` remembered on the wire, G4
  `replay` replay posts nothing, G5 `walk` the cues fire in order; `openers` / `explainers` reserved (G6 on) in the
  docstring. `MARKS_VERSION` untouched (20, asserted by the test)
- [x] T002 FR-4 seeded faults, `tests/test_guide_marks.py` (**53 tests**, 2 skip while keel-web master predates 080):
  good records for S-005 local (5 of 5), S-006 local and remote (3 of 3, G4 / G5 unmeasured with the why); Acceptance
  1's faults -- a second sheet at the next open, a sheet over a later frame, a second WELCOME POST (G1); Skip below the
  fold at 390 x 844, a second control, a stray wordless control, cues fired before the reads, a close over 1 s (G2); a
  409 on the next write, a second press, a revision moved by the POST or the repeat, a POST not 204 or with a stage, a
  repeat not 204, the wire forgetting (G3); a POST during either replay, a replay that never opened or closed, far from
  0 s, Skip out of view, the revision moved (G4); cue ids out of order, a drawn cue out of order, `cuesFired` shrinking
  or repeating, eleven cues, `at` not rising, a duplicate id (G5); the unmeasured rule (no `walk` / `replay` -> G4 / G5
  unmeasured, never met, not owed); an unreadable record fails rather than crashes; `_playing`'s judgement call 1 cases;
  `guide_record`'s later frames; the twelve cue ids and the words against keel-web's own files (skip until 080 merges)
- [x] T003 FR-1 the page object, `harness/vectors_screens.py`: the six test ids, the seam's name, the files and the
  Feedback trigger spelled once; **`GuideWelcome(page, recorder, base_url="")`** -- `present(timeout_s)`, `count()`,
  `absent(after=…, timeout_s, grace_s)` (listens for the overview from before `after`, waits for it and for the shell's
  first screen, and waits up to `grace_s` for a sheet only when the received overview does not say seen), `face()` (one
  async `evaluate`: paused, muted, autoplay, readyState, currentTime twice 600 ms apart, the error code, duration, the
  track's src / kind / mode), `clock()`, `caption()`, `caption_visible()`, `cue()`, `wait_cue(id)`, `controls()`,
  `skip_in_view()`, `served_cues()`, `seam()`, `seek(seconds)`, `cues_fired()`, `hold_face()`, `skip()`, `escape()`,
  `end(seconds)` (each returning `{door, gone_ms, requests}`), `replay()` (`guide-replay` if visible, else the Feedback
  panel's trigger first; `{found, via, opened, requests}`), `pass_by(wire, timeout_s)`; **`GuideWire(page)`** --
  `attach()` / `detach()`, `guide_posts()`, `overviews()`, `received()`, `writes_after_guide()`, `wait_overview()`
  (Playwright objects kept and read after, never inside the handler); `Corridor.frame()` gains `welcome`
- [x] T004 FR-6 the pass-by: `MarketStep.start(welcome="pass" | "hold")` (the import inside the method),
  `preludes.create_project(…, welcome="pass")` forwards it; S-001, S-003, S-004, the curated proof run and every prelude
  inherit "pass"; S-012's file untouched (its `leg_project` passes it by: `Journey.hold_welcome` is False there).
  `tests/test_vectors_screens_guide.py` (**23 tests**, 6 skip until 080 merges): the pass-by with the sheet (one note
  step, one POST, listeners off), with none due (`welcomeSeen: true`, and an overview with no `guide`: no wait), due but
  never come (not a failure), `hold` (left up), a bad value refused; Skip / Escape / end / replay over the stub; the
  wire's sorting; the six test ids and the Feedback trigger against keel-web
- [x] T005 FR-2 `evals/corpus_scenario.leg_welcome(j, walk=False)` right after `leg_project`, both profiles:
  `Journey.hold_welcome` (set by `run()`), `Journey.guide` (the record), `Journey.guide_wire` (attached in
  `leg_project` before *Start*, detached after the context Save); (a) present, the received overview, face and captions;
  (b) Skip at 1280 x 720 and 390 x 844 (`set_viewport_size`, then back) and the controls; (c) Skip / Escape, the
  revision before / after, the repeat POST on the wire; (d) the next open (`goto /p/{id}`), the wire's `guide`; the next
  write read in `leg_context` (`_next_write_after_the_welcome`) from the wire and from `Corridor.saves`
- [x] T006 FR-2 e: `_hold_frame` asserts `frame["welcome"] == 0` on every corridor frame, and `guide_record` hands G1
  every frame in `j.framing` (the journey's later frames)
- [x] T007 FR-3 S-005 local: `run(…, welcome_walk=True)` from `evals/test_s005_countly.py`; `_walk_the_cues` (served
  cues, the face held, `seek(at + 0.05)` per cue, the snippet and `cuesFired` after each) before (c); Escape for (c);
  `_replay_twice` after (d) (Skip closes the first, `end` the second, zero `guide-seen`, the flag and revision after)
- [x] T008 FR-5: on the remote profile the walk and the replays are a `kind="note"` step naming
  `guide_marks.REMOTE_WHY`, the door is Skip; elsewhere on local the note names `ELSEWHERE_WHY`; `WELCOME_BUDGET_S` 5 s
  asserted on both profiles over the sheet seen -> the next open's absence read, the walk excluded, the seconds in the
  record (`welcome.seconds`) and the step
- [x] T009 `_score_guide(j)` after `score_feedback`: `guide.json`, `guide-marks.json`, the journey fails on any owed mark
  unmet; README / AGENTS one paragraph each; this file
- [x] T010 Acceptance 1 `make unit`: **2,611 passed / 61 skipped** (below)
- [x] T011 acceptance 2, the journey pass: `make eval K="s005 or s006 or s007 or s014"` **4 passed, 11 deselected in
  894 s** on a fresh stack (keel-cloud-docs `7c4d9a9` = 106, contract 20; keel-web `3c83ac4` = 080 on `248a41f`; runtime
  0.8.0), the first run, **no fix needed**: G1-G3 met on all four, G4 and G5 met on S-005 (see *Acceptance 2, measured*).
  No DRIFT written: everything the sheet showed is what 080 or 106 says (below)
- [ ] T012 **owed**: acceptance 3, the remote journeys on staging once 106 + 080 are deployed: G1-G3 met, G4 / G5
  unmeasured with the step's why, each journey's welcome seconds under 5

## Measured (2026-10-17, no stack)

- **`make unit` before** (master `14513c1`'s code in this worktree): **2,541 passed / 53 skipped**.
- **`make unit` after**: **2,672 collected = 2,611 passed / 61 skipped, 0 failed**. Against 2,541 / 53: **+78** --
  `tests/test_guide_marks.py` 53 (51 pass, 2 skip), `tests/test_vectors_screens_guide.py` 23 (17 pass, 6 skip), and 2
  parametrized rows the existing sweeps grow for the new `evals/guide_marks.py` (`test_page_object_calls_exist`,
  `test_scenarios_use_the_stack_addresses`). **The 8 new skips** are the checks against keel-web's own files (the twelve
  cue ids, the words, the six test ids; the Feedback trigger's check runs on master already) that wait for 080 on
  keel-web master; read against the 080 worktree (`wt/keel-web-080`, read-only) the cue ids and times, the sound labels and all
  six test ids are there.
- **`make unit` on the journey pass** (keel-web master `3c83ac4`, 080 merged): **2,619 passed / 53 skipped** -- the 8
  checks against keel-web's own files now run and pass (the twelve cue ids and times, the words, the six test ids).
- The first full run after the change was red once: `test_vectors_journey`'s classic-word sweep found `SUPPORTED`
  inside `MEDIA_ERR_SRC_NOT_SUPPORTED`; the constant is `MEDIA_ERR_NO_DECODE` now.

## Acceptance 2, measured (2026-10-18 UTC, the journey pass)

One fresh stack (`COMPOSE_PROJECT_NAME=keel-e2e-eval-054`, `make up`), `make eval K="s005 or s006 or s007 or s014"`:
**4 passed, 11 deselected in 894.03 s** on keel-cloud-docs `7c4d9a9` (106) + keel-web `3c83ac4` (080) + keel-runtime
`3988131` 0.8.0; `make down` after. Every other mark family on these journeys held as before (the journeys passed whole).

| Journey | Run | Time | Guide marks | Door | Welcome leg | Sheet gone | Next write | Later frames |
|---|---|---|---|---|---|---|---|---|
| S-005 countly | `20261018T022340Z-s005-countly` | 309 s | **5 of 5** (G1-G5) | Escape | **0.88 s** | 28 ms | PUT context 202 | 22, no sheet |
| S-006 paidly | `20261018T022850Z-s006-paidly` | 306 s | **3 of 3** (G4, G5 unmeasured) | Skip | **0.90 s** | 64 ms | PUT context 202 | 25, no sheet |
| S-007 mulchrun | `20261018T023356Z-s007-mulchrun` | 140 s | **3 of 3** (G4, G5 unmeasured) | Skip | **0.90 s** | 71 ms | PUT context 202 | 25, no sheet |
| S-014 green | `20261018T023616Z-s014-green` | 135 s | **3 of 3** (G4, G5 unmeasured) | Skip | **0.91 s** | 55 ms | PUT context 202 | 25, no sheet |

- **The welcome's cost** is under a second on every journey against the 5 s budget (FR-5): the face read's 600 ms is
  most of it; the press ~0.1 s, the repeat POST and the revision reads ~0.1 s, the next open's `goto` and absence read
  ~0.16 s. S-005's cue walk took 0.2 s and its two replays 3.5 s (outside the budget, as FR-5 says).
- **On every journey**: the sheet at `/p/{id}/define/context` (where *Start* lands) over an overview the page received
  with `{welcomeSeen: false, openersSeen: []}`; one `guide-seen {what: WELCOME}` from the page, 204; the repeat on the
  wire 204; the overview's revision 0 before the press, after it and after the repeat; the next open received
  `{welcomeSeen: true, openersSeen: []}` and drew no sheet; the context Save 202 on its first press.
- **The face decoded in the bundled Chromium** (judgement call 1's note never fired): muted, unpaused, `readyState` 4 and
  the clock rising (~0.6 s over 600 ms) on S-006 / 007 / 014; on S-005 the first read caught it still loading
  (`readyState` 1, 0 s) and the second at `readyState` 4, 0.39 s -- call 8's "still loading" branch, met. The track
  `/guide/welcome.vtt`, mode `hidden`. The caption read *What if you could find out whether your* on all four (S-005's
  through the seam's `seek(0.35)`: its clock was still under 0.30 s at the read).
- **Skip** *Skip ›*, 67 x 44 px, in view and hit at both sizes (1280 x 720: at 971, 519; 390 x 844: at 291, 637), focused;
  the controls on the sheet: Skip and the face's wordless `button` *Sound on* (call 6, which the design now allows).
  `cuesFired` `[]` at the reads on every local journey.
- **S-005's walk**: the served `welcome.cues.json` the twelve in order (080's times), `cuesFired` `["wordmark"]` before the
  walk (the caption nudge), the face held, each seek drawing its cue and the list growing by one to twelve.
  **Replays**: both through the Feedback panel (`button.fb-tab`, then `guide-replay`), the first at 0.0003 s and closed
  by Skip, the second ended by the seek to the end, zero `guide-seen` requests, `welcomeSeen` true, revision 0 -> 0.
- **No DRIFT** (#95 stays free): the sound toggle is allowed (the coordinator: the design now says so); *Skip ›* is
  080's `GUIDE_SKIP`; *Play the welcome again* at the Feedback panel's foot is 080's judgement call 2 (keel-web has no
  help menu) -- each is said by 080, so none is an unsaid thing the page showed.

## Judgement calls

Confirmed by the coordinator (the spec's five and its reading of them):

1. **The phone size is 390 x 844**, set with `set_viewport_size` while the sheet shows, then back to the window's own
   (Playwright's default 1280 x 720: no context passes a viewport).
2. **"Playing" is `paused` false and `muted` true** at the first read; a MediaError 4 in the bundled Chromium (no H.264)
   is a note step, never a failure or a DRIFT.
3. **S-005 dismisses with Escape** on local, the other three with Skip; the remote S-005 presses Skip.
4. **The next open is a plain `goto`** in the same page.
5. **S-012 is untouched**; DRIFT numbers from **#95** (#95 is still free on master `14513c1`: 053 did not spend it).

Decided this pass (each a reading of the spec against 106 as built and 080 as specified; the journey pass may move them):

6. **G2's "only control" is "the only control with a word"**, plus at most one wordless `button` whose `aria-label` is
   *Sound on* / *Sound off*: 080 FR-2.1 puts a speaker glyph on the face (no visible word), so a strict "no other
   button" would fail 080 as specified. Any other control -- worded or not -- fails G2. If the founder reads D24 as no
   button at all, this is DRIFT #95's first candidate.
7. **"Before any cue" admits the wordmark** (cue 1 at 0.30 s, *the wordmark draws itself; the face appears* -- the
   opening frame itself): local reads `cuesFired` at the reads (`[]` or `["wordmark"]`), remote (no seam) the face's
   clock below cue 2's 13.25 s. A playing face has always fired cue 1 before a read can land.
8. **The clock must rise only where the face has decoded enough to play** (`readyState >= 3` at the second read): a
   face still loading (no error, `readyState < 3`) is recorded, not failed -- staging's 11 MB file may not be in within
   the first second.
9. **The caption line before 0.30 s is empty by design** (`captionAt`: nothing before the first cue). Where the face did
   not play, the local journeys move it with `seek(0.35)` and require words; on remote with the clock under 0.30 s only
   the track (`src` ending `welcome.vtt`) is required, recorded either way.
10. **The walk holds the face first** (`hold_face()`, `pause()` on the `<video>`): a decoding browser would otherwise play
    from 84.98 s to the end and close the sheet (posting WELCOME) before Escape; the seam drives the cues either way.
11. **G5 holds the served ids to §7.1's twelve in order** (080 FR-1's ids), not only unique: "cue ids out of order" is
    otherwise unmeasurable. `cuesFired` after step *i* must be the twelve's prefix to *i*.
12. **The pass-by decides from the overview the page received**: no wait when it says `welcomeSeen: true` or carries no
    `guide` (a cloud before contract 20); else up to 5 s for the sheet. `absent()` likewise waits for a returning sheet
    only when the received overview does not say seen (the sheet's chunk is lazy), never a bare sleep.
13. **G1's "one WELCOME POST in the journey"** is read over `GuideWire`'s window, *Start* to the context Save (the plan:
    off after, so later legs pay nothing); the replays sit inside the window, so a replay that posts fails G1 and G4.
    G1 also needs at least one later frame read.
14. **A refused context Save returns at once** (`Corridor.context` keeps each Save's answer in `saves` and skips the
    60 s card wait on a status >= 400), so a 409 names G3 rather than a timeout (the plan's risk). No other caller
    changes: an unanswered or 2xx Save waits for the card as before.
15. **Play again's trigger is `button.fb-tab[aria-haspopup='dialog']`**, the Feedback panel's one button (080 judgement
    call 2: no help menu exists), read at the desktop size; a class, not a test id -- 080 gives the trigger none.

## Discovered

- **D-01 (the DRIFT candidates, closed by the journey pass without an entry):** the face's speaker glyph (call 6; the
  design now allows it), Skip's word *Skip ›* (080 `GUIDE_SKIP`), where *Play again* lives (080 judgement call 2); no
  control or label beyond Skip and the speaker showed on the sheet.
- **D-02:** 080 calls `play()` rather than setting `autoplay`, so `face()["autoplay"]` reads false on a sheet that plays
  on its own; it is recorded and never required.
- **D-03:** on a phone, *Play again* lives in the Lines sheet's Feedback row, which exists only after the lock (080
  judgement call 2), so the replays run at the desktop size.

## Where things are

| Piece | Place |
|---|---|
| the marks, the version, the whys | `evals/guide_marks.py` |
| the leg, the walk, the replays, the next write, the score | `evals/corpus_scenario.py` (`leg_welcome`, `_walk_the_cues`, `_replay_twice`, `_next_write_after_the_welcome`, `guide_record`, `_score_guide`) |
| the page object and the wire | `harness/vectors_screens.py` (`GuideWelcome`, `GuideWire`, the `GUIDE_*` ids) |
| the pass-by | `harness/browser.py` `MarketStep.start(welcome=…)`, `evals/preludes.create_project` |
| the walk's switch | `evals/test_s005_countly.py` (`welcome_walk=True`) |
| the tests | `tests/test_guide_marks.py`, `tests/test_vectors_screens_guide.py` |
