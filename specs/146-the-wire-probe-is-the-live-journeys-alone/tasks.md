# Tasks 146 -- The wire probe is the live journeys' alone, and waits for the steps it opens

Branch `146-the-wire-probe-is-the-live-journeys-alone`, worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-146`
(`.git` a file), cut at master `9c373e9` (the cycle 17 record), the spec merged in at `16616d9`. Nothing paid: no stack,
no model, no key, no walk -- the unit suite only. keel-cloud and keel-web untouched (read only, for the cause).

## The cause, from the stack log (2026-11-07, 15:12 ET, project `63c3d919`)

- 15:10:14 -> 15:11:09: PROBLEM's calibration drafts refused three times (rules E2, E9 on Keel's own Prevalence rows), each
  retried by the walk as a founder would (spec 062) -- `Journey.retries` 3 -> 0.
- 15:12:30 -> 15:12:58: the Current solution Save held 28 s (keel-cloud 235's repair turn: one rung refused W-rung, the
  second turn's notes alone).
- 15:12:59.07 and 15:12:59.14: `rows read back queued` twice for Importance -- the walk's wire probe
  (`_importance_needs_three`) saving the founder's list on `PUT /calibration/PROBLEM` twice, which the gate
  `not getattr(j, "retries", 0)` no longer skipped. Each save queued a read-back review (Haiku, ~10 s each, serial on
  the one worker) and an ASKED job with its own review.
- 15:12:59 -> 15:13:14: the lock page gated on `Overview.openSteps` (keel-web 083) under *Keel is finishing the previous
  step…*; the harness's 15 s guard (`_drift_95_guard`) fired. 15 founder screens scored, no strangers.

## What was built, per FR

- [x] **FR-1** `Journey.backtest: bool = False` (`evals/corpus_scenario.py`), set True in `Backtest.camera`
  (`evals/backtest.py`) beside `retries`; the probe's gate reads `getattr(j, "backtest", False)`, never the retries.
- [x] **FR-2** `_wait_steps_landed(j, what)` (`evals/corpus_scenario.py`): polls `GET /overview` every 0.5 s until
  `openSteps` is 0, 90 s x patience, else `AssertionError` naming the overview as last read; called inside the probe's
  step after its three writes and before the page reload.
- [x] **FR-3** `tests/test_wire_probe_146.py`: 10 tests -- the field and its default, the camera setting it, the gate's
  line as written (flag, no retries), the gate's expression over four (retries, backtest) pairs, the wait before the
  reload, the wait returning on 0, raising with the view, and a missing overview counted as nothing open.

## Gate

`make unit`: **5705 passed, 81 skipped** (5695 + the 10 new).

## Judgement calls

- The 15 s guard stays: a page a founder reaches with nothing open lights within one poll, and the guard exists to catch
  drift 95 coming back. The probe now reaches it the way a founder does.
- The wait is the probe's own, not a general one before every lock: the page's Save already holds (keel-web 180); only
  a write on the wire bypasses it.

## Open, for the founder

- Expanse's three RESULT_INVALID Prevalence drafts (E2: the event clause; E9: the healthy row) in one run, one in cycle
  16 as well: Keel's own Prevalence writer on that entry; a finding, not a stop, but three in a row spend the walk's
  retries. A keel-cloud matter.
- keel-cloud runs a read-back that a later save has already superseded, then drops it (*saved again since*): one Haiku
  turn, 0 credits; unreachable from the page while the Save is held.
- Re-walking 17-expanse PROBLEM alone is a paid run (his word).
