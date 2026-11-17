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
  11. `_save_context` -- *Save and continue* (outside its `expect_response`, so a long gate cannot time that out).
  12. `needs_input` -- `context-needs-input-send` (was a bare click).
  13. `context_confirmed`'s Edit path -- 1 of 2's *Continue* (`go_on`; was a bare click).
  14. `confirm_context` -- *Yes, that's it* (was a bare click).
  15. `seed` -- *Send*, first and on every resend (two sites; were bare clicks).
  16. `confirm_seed` -- the card's *Yes* / *Looks right* (was a bare click).
  Every other caller presses through `_press_primary` (the idea's Save, each Answer / Check / Choose, the cost box,
  Continue after a review's band, `edit_idea_lines`). Not routed: radios, chips, the cost-mode / period / measure picks,
  *Add* / remove, *Edit* / *Change*, the face carousel and the pilot cards -- inputs, not the screen's primary; and every
  respondent page (FR-3, out of the spec).
- [ ] T2 (FR-2) `gate_waits`, the transcript note, the backtest.md line and the bundle rows.
- [ ] T3 (FR-3, FR-4, FR-5) the lock screen's shot after `l1()`'s waits; the unit tests; `make unit` green; AGENTS.md's one paragraph.

## Gate

(the builder fills this in)

## Judgement calls

(the builder records them here)
