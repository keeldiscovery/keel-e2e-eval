# Spec 146 -- The wire probe is the live journeys' alone, and waits for the steps it opens

Cycle 17 (2026-11-07, `quality/cycles/20261107-74a04fb.md`): 17-expanse's problem study stopped at the lock page --
*Lock and record Daphne* greyed under *Keel is finishing the previous step…* for the 15 s the drift-95 guard allows, and
the strangers never walked. The stack log shows why: at 15:12:59 ET the walk's Importance wire probe
(`_importance_needs_three`, keel-cloud 097 F9) saved the founder's Importance list twice on the wire, each save queued a
row read-back review and an ASKED job on the one worker, and `Overview.openSteps` stayed above zero past the guard.

The probe is meant to be skipped on a back-test (the 062 follow-up of 2026-10-22: the judges saw the founder approve one
list and strangers served another). The skip is keyed on `Journey.retries` being set, and the back-test spends those
retries: Expanse's three calibration drafts came back RESULT_INVALID (rules E2 and E9), the walk retried each, `retries`
reached 0, and the probe ran on a back-test for the first time since the review went on. Cycle 16 never hit it because no
study spent all three.

## Rules

- **FR-1 The skip is the back-test's, not the retries'.** `Journey.backtest` (a bool, False everywhere) is set True where
  the back-test sets `retries` (`Backtest.camera`); the probe runs only where it is False. Retries left or spent change
  nothing. The 2026-10-22 follow-up's reason stands in the comment.
- **FR-2 The probe waits for what it opened.** On the journeys that still run it (the remote journeys and S-015/S-016,
  which walk staging with the review ON), the probe bypasses keel-web's Save hold (keel-web 180), so it waits itself:
  after its writes and before the reload, it polls `GET /overview` until `openSteps` is 0 -- 90 s times the journey's
  patience, then an `AssertionError` naming the overview as last read. The wait is inside the probe's step; the lock
  page is reached with nothing open, as a founder reaches it.
- **FR-3 Tests.** (a) a back-test journey with `retries` 0 never calls the probe; (b) a live journey with `retries` 3
  does; (c) the wait returns once `openSteps` reads 0 and raises with the view when it never does. `make unit` green.

## Out of scope

The three RESULT_INVALID calibration drafts on Expanse (rules E2 and E9 refusing Keel's own Prevalence rows; a
keel-cloud matter, a finding in the record); keel-cloud running a read-back that a later save has already superseded
before dropping it (*saved again since*: one Haiku turn, 0 credits; the founder cannot reach it through the page because
the Save is held); the drift-95 guard's 15 s, which is right for a page a founder reaches with nothing open; any paid run.
