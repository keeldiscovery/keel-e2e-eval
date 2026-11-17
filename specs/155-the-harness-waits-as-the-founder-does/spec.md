# Spec 155 -- The harness waits as the founder does

The founder, 2026-11-17 18:42 ET, after the 13-aircaps back-test at scope ALL stopped on *who decides to pay*
(`runs/20261117T223509Z-backtest-13-aircaps`): *"the harness should wait just like our founder does. I think we should
fix that."* What happened: the walk saved the solution study's last screen and reached the persona step while the
solution's calibration job and its review (spec 209) were still running. keel-web's corridor gate (keel-web 083 FR-1,
`useStepGate`) disabled Continue and drew *Keel is finishing the previous step…* under it, as it does for a founder;
`harness/vectors_screens.py` `Corridor.persona()` pressed Continue through Playwright's 30 s limit and the run died as a
harness stop. The quality cycles walk the five entries one scope at a time, where no screen follows the solution save
directly, so the gap never showed. Nothing here is paid.

## Rules

- **FR-1 One wait, before every primary press.** `Corridor` gains `_wait_for_the_gate(label)`: while the card draws
  the gate's line (keel-web's `CORRIDOR_WAITING` sentence, *Keel is finishing the previous step…*, under the primary;
  read by text, as the screen draws it) or the primary is disabled with that line present, wait, polling at the page's
  own cadence, up to the walk's step budget (`SAVE_BUDGET_S * patience`, 660 s on a back-test, spec 140 FR-3). Every
  press of a corridor primary goes through it: `_press_primary()`'s two `wait_for_function("(b) => !b.disabled")`
  calls, `persona()`'s two `_button(self.page, CONTINUE).click()`, and any other `.click()` on a corridor primary
  the builder finds (list them in tasks.md). A primary disabled WITHOUT the gate's line is not the gate: it is a screen
  waiting for input the walk did not give, and keeps today's 30 s and today's failure, so a missing pick still fails
  by name.
- **FR-2 The wait is evidence, never a stop.** Past `SLOW_SAVE_S` the seconds waited are noted in the transcript and
  kept on the corridor as `gate_waits` (screen address, label, seconds), beside `slow_saves`; `backtest.md` gains one
  line *Gate waits: N, the longest S s on <screen>* under the Stack line and the bundle's `backtest.json` carries the
  rows. A wait that runs past the budget fails naming the screen and the line still drawn, as `_wait_steps_landed`
  does on the wire.
- **FR-3 The wire's own wait stays.** `_wait_steps_landed` (spec 146 FR-2) keeps guarding writes made on the wire;
  nothing else in `evals/` changes. The respondent pages are not corridor screens and are not in this spec.
- **FR-4 Tests, no spend.** Unit tests over a fake page (the pattern the existing corridor tests use): the primary
  disabled with the gate's line for longer than 30 s, then enabled -- pressed once, one `gate_waits` row, the
  transcript's note; disabled without the line -- the old 30 s failure by name; enabled at once -- no row. Budgets
  scaled through `patience` so the suite stays fast. `make unit` green. The proof on a live walk -- 13-aircaps at
  scope ALL on the prod build -- is one paid run on the founder's word after the merge, not part of the gate.

## Not in this spec

The product's gate (keel-web 083). The respondent pages. Any change to what the cycles walk.
