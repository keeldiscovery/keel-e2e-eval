# Spec 045 -- the brief on the founder's return

The keel-e2e-eval half of keel-cloud 096 (*The brief is written when the founder comes back, not after every batch*;
keel-cloud-docs master `7b1e4f6`, the 096 worktree's `5b971f3`, the same code; no contract change, document 23). Builds on
spec 044 (contract 16, read on arrival, IM13). Sibling: keel-web `d23895f` (nothing moves there). **No model is called
and no money is spent.**

## What moves

- FR-001 **No batch writes the brief.** After every answer of a journey is read the project holds **no** BRIEF; the
  founder's own read of the project (`GET overview` on their session -- on their own AI the session the agent is bound
  to) starts **one**, which lands (`corpus_scenario._brief_on_return`, at the end of `leg_interview`). A lost revision
  race is 095's: up to three BRIEF rows in all, one APPLIED and the rest `STATE_CONFLICT`. On Keel's door the same step
  follows the arrival batches (`_read_on_arrival`).
- FR-002 **The interviewer leg comes back too.** After it reads what Keel's keyless door left unread (044 call 152), the
  founder's `GET overview` starts the one BRIEF those readings made due and waits for it to end, so the next agent to
  connect (S-007's) finds no stale brief of S-006's to write on S-007's script.
- FR-003 **IM13's reasons**: `brief:on-return` in, `brief:after-batch` out (a lost race stays `retry:<n>:<id>`); a
  batch's brief is a fault. `INTERVIEWER_MARKS_VERSION` stays 1 (IM13's subject on this stack is the reading's reason;
  Keel's keyless door applies no reading, so it never makes a brief due).
- FR-004 **Document 23**: the stored recording is read at any document version from 22 up.

## Judgement calls

170. **The return is a `GET overview`, not a second sign-in**: 096's FR-D and judgement call 4 make either read start the
     brief, and the journeys' founder is already signed in. The step runs after the last reading, before the standings,
     so "zero BRIEF after the readings, one per return" is counted where it is true (on the own door the page's own
     overview poll stops while nothing awaits reading).
171. **A failed brief is not asked for again by more reads** (096 call 10): no journey here meets one; the step fails on
     a BRIEF that ends other than APPLIED or `STATE_CONFLICT`, and a second sign-in is not attempted.
172. **The interviewer leg's late brief is held to end, not to land APPLIED.** The scripted executor repeats the
     journey's last BRIEF entry over a project two answers on; on S-006 keel-cloud's checks refuse it, the repair turn
     carries a `repair` key the script has no entry for, and the BRIEF ends `JOB_FAILED` (on S-005 it lands APPLIED). A
     failed brief stays stale, so S-007's connect tries it again on S-007's runtime (096 call 10; two more `JOB_FAILED`
     rows) -- harmless, because a script's one BRIEF entry repeats and no cursor moves. What the step holds is that the
     return starts one and that nothing of S-006's waits unread for S-007's readings (044 call 152).

## Results

- T001 baseline vs keel-cloud-docs `5b971f3` + keel-web `d23895f`, nothing changed: S-007 passed; S-005 / S-006 failed
  only on the interviewer leg's document pin (22; keel-cloud 096 writes 23). S-006 held ten INTERPRET and one BRIEF.
- With this spec, `make down` then a fresh database each time: **3 passed** (456 s; bundles `runs/20261016T0100*` to
  `runs/20261016T0106*`) and **3 passed** (469 s; `runs/20261016T0108*` to `runs/20261016T0114*`). Every journey: no
  BRIEF before the return, exactly one APPLIED after it. Interviewer marks 12 of 12 on S-006 (IM12 unmeasured) and 8 of
  8 on S-005; contacts marks 13 of 13 and 1 of 1.
- `make unit`: see tasks.md.

## DRIFT

None new. DRIFT #85-#89 stand as spec 044 left them (each step still fires on S-006).
