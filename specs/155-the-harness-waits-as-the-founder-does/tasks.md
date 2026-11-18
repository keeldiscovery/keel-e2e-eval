# Tasks 155 -- The harness waits as the founder does

Branch `spec-155`, worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-155` (`.git` a file, asserted first),
cut at master `8027b83` or later. Nothing paid: no host, no stack, no cycle -- the unit suite alone (`make unit` with the
main checkout's `.venv`). Not merged; master untouched; every commit pushed as it lands.

- [x] T1 (FR-1) `_wait_for_the_gate`; every corridor primary press through it; the list of the presses found.

  The press sites routed through `Corridor._wait_for_the_gate` (`harness/vectors_screens.py`):
  1. `_press_primary` -- the first press (was `wait_for_function("(b) => !b.disabled")`, 30 s).
  2. `_press_primary` -- the 409 CONCURRENCY second press (DRIFT #80; was the same 30 s wait), after its 4 s.
  3. `_save_holding` -- the Check's Save (was the same 30 s wait).
  4. `_save_holding` -- its 409 second press (was a bare `self._primary().click()`).
  5. `persona` -- *Continue* on who decides (was a bare `_button(CONTINUE).click()`), plus the line waited out
     (`enabled=False`) before the pick and again after it (judgement call 2).
  6. `persona` -- *Continue* on the summary that follows (was a bare click).
  7. `word_pilot_and_lock` -- *Lock and record* (`lock-and-record`; was a 15 s wait, kept as its plain limit; a
     `GateStillDrawn` is not swallowed by the DRIFT #95 branch).
  8. `_pilot_pick` -- *Continue · Yes / No* (`before-continue`; was a 10 s wait, kept).
  9. `relock` -- *Lock and record* again (was a 30 s wait).
  10. `_context_window_page` -- 1 of 2's *Continue* (`context-continue`; was a bare click).
  11. `_save_context` -- *Save and continue* (outside its `expect_response`, so a long gate cannot time that out;
      `GateStillDrawn` re-raised past its record-the-error branch).
  12. `needs_input` -- `context-needs-input-send` (was a bare click).
  13. `context_confirmed`'s Edit path -- 1 of 2's *Continue* (`go_on`; was a bare click).
  14. `confirm_context` -- *Yes, that's it* (was a bare click).
  15. `seed` -- *Send*, first and on every resend (two sites; were bare clicks).
  16. `confirm_seed` -- the card's *Yes* / *Looks right* (was a bare click).
  Every other caller presses through `_press_primary` (the idea's Save, each Answer / Check / Choose, the cost box,
  Continue after a review's band, `edit_idea_lines`). Not routed: radios, chips, the cost-mode / period / measure picks,
  *Add* / remove, *Edit* / *Change*, the face carousel and the pilot cards -- inputs, not the screen's primary; and every
  respondent page (FR-3, out of the spec).
- [x] T2 (FR-2) `gate_waits`, the transcript note, the backtest.md line and the bundle rows. `Corridor.gate_waits` (`{screen, label, seconds, budget_s}`, past `SLOW_SAVE_S`) and the transcript note (`_gate_row`, T1); `backtest.json` carries `gate_waits` always (`[]` where none -- its presence marks a 155 bundle); `backtest.md` says `- Gate waits: N, the longest S s on `<path>`` (`- Gate waits: 0` where none) under the Stack line, and nothing on a bundle before 155. A gate still drawn past the budget raises `GateStillDrawn` naming the screen and the line, its row kept first.
- [x] T3 (FR-3, FR-4, FR-5) the lock screen's shot after `l1()`'s waits; the unit tests; `make unit` green; AGENTS.md's one paragraph.
  FR-5: `word_pilot_and_lock` calls `l1()` first and shoots `ready-interviewer` after it, in both branches; `l1()`'s
  per-part wait is named `LOCK_PARTS_WAIT_MS` (15 s, unchanged) so the never-loads case is testable fast. FR-3:
  `_wait_steps_landed` untouched; nothing else in `evals/` moved but `backtest.py`'s record (T2). FR-4:
  `tests/test_harness_waits_155.py` (15 tests, real chromium on static pages, limits scaled through `patience` and
  monkeypatched module limits): the gate held past the (scaled) 30 s then lifted -- pressed once, one row, the note; a
  disabled primary with no line -- today's Playwright timeout naming the press, inside the plain limit; enabled at once
  -- no row; a short gate -- waited, no row; the gate past the budget -- `GateStillDrawn` naming screen and line, row
  kept; DRIFT #80's second press waiting on a gate drawn behind the 409; who decides re-keyed under the gate (the pick
  made after the line, Continue pressed once); every routed site counted by source; the line equal to keel-web's
  `CORRIDOR_WAITING`; the bundle rows and the md line (and none on a pre-155 bundle); the wire's wait kept; FR-5's shot
  after the problem box and the rows load, still taken (after the waits, parts counted 0) where they never do, and
  the source order in both branches. `tests/test_revision_16_walk.py`'s `_SavePage` fake gained what the wait reads
  (the button's count / is_disabled / inner_text, `evaluate`, `url`) and its `_corridor` a `patience`. AGENTS.md: one
  paragraph after spec 121's.

## Gate

`make unit` with the main checkout's `.venv` (`PY=/Users/athulrajeev/Documents/projects/keel-e2e-eval/.venv/bin/python`),
the sibling checkouts as the worktree resolves them (`../keel-cloud-docs` `474aefd1`, `../keel-web` `cae3804b`):

- before (master `9860f10`, a clean `git archive` export with the same siblings -- the first run in the worktree was
  taken while T1 was being edited and is not counted): **5,901 passed / 26 failed / 125 skipped**.
- after (`spec-155`): **5,916 passed / 26 failed / 125 skipped** (+15, all in `tests/test_harness_waits_155.py`; `test_revision_16_walk.py`'s fake re-cut, still passing).

The 26 reds are the same 26 before and after, none in a file this spec touches: contract / selector mirrors against
siblings that moved past them (`test_cloud_245_250_248_web_186_190_mirror_154.py` 20, `test_cloud_233_mirror_144.py`,
`test_cloud_238_241_mirror_148.py`, `test_cloud_243_web_184_mirror_149.py`, `test_follow_ups_075.py`,
`test_instruction_compare.py`, `test_report_marks.py`) -- the coordinator's to re-cut against the checkouts of record.

## Judgement calls

1. **The line is read off the whole page's text** (`document.body.innerText`, which skips hidden nodes), not scoped to
   the card: keel-web's `BeforeStep` draws `StepWaiting` outside `.ccard` on the lock screen.
2. **Who decides waits out the line before the pick, not only before Continue.** keel-web's `PersonaRoute` keys
   `PersonaStep` on `${state}-${revision}`; the gate's re-read raises the revision, so the screen is drawn afresh and a
   pick made under the line is dropped. The stopped run's `failure/page.html` shows exactly that: both radios
   `aria-checked="false"`, no line, Continue disabled -- so a wait before Continue alone would still have failed 30 s
   later, now as a "no line" failure. The walk waits out the line (`enabled=False`), picks, looks again, and makes a
   dropped pick again with a transcript note, then waits for Continue enabled.
3. **The context, seed and card forward buttons are routed too** (sites 10-16), though keel-web draws no gate on those
   screens today: with no line the wait is the click's own 30 s actionability wait, so nothing changes there, and a
   gate drawn there later is waited out.
4. **The no-line failure stays a Playwright `TimeoutError`** (the type every caller and DRIFT #95's branch already
   handle), its message *Timeout Nms exceeded: the founder's 'X' stayed disabled with no \*Keel is finishing the
   previous step…\* under it -- the screen waits for input the walk did not give (url)*. Each site keeps its old limit
   (the lock 15 s, the pilot 10 s, the rest 30 s).
5. **The gate past the budget is `GateStillDrawn(AssertionError)`**, re-raised through the two broad excepts it would
   otherwise fall into (the lock's DRIFT #95 branch, `_save_context`'s record-the-error branch); its row is kept before
   it raises, so the bundle shows the overrun.
6. **The budget is per press, over all the time the line was drawn** for that press; the plain 30 s restarts each time
   the line goes. Rows only past `SLOW_SAVE_S` (as `slow_saves`), with `budget_s` beside `seconds` as `slow_saves` has.
7. **The primary is re-read through its locator on every look** (no element handle): a re-keyed screen draws a new
   button and a handle to the old one would read stale.
8. **`backtest.json` always carries `gate_waits`** (`[]` where none, so its presence marks a 155 bundle, as
   `gate_refusals` does); `backtest.md` says *Gate waits: 0* where none, nothing on a bundle before 155, and names the
   screen by its path (`/p/<id>/define/persona`), not the full URL.
9. **FR-5: `l1()` taps the face before its waits**, so the `ready-interviewer` shot now shows the face already picked
   as well as the problem and the rows. `LOCK_PARTS_WAIT_MS` names l1's existing 15 s so a test can scale it.
10. **No rename of the existing waits elsewhere** (`idea_check`'s 15 s *Save enabled* read before the named state,
   `CHOOSE_ASKED_CAP_S`, the review hold): they read states, they press nothing; the press after them goes through
   `_press_primary`.
