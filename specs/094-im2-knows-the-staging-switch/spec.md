# Spec 094 -- IM2 knows the staging switch: the lock screen's one switch label is the screen's own words too

keel-web 132 (merged 2026-10-30) draws, on a server serving `recordOnSend: true` (staging's overlay sets
`KEEL_V2_INTERVIEWER_LOCK_RECORD_OPTIONAL=true`), one switch at the top of the lock screen: *Record {face} at lock · 400
credits* (`data-testid=record-at-lock`, `role=switch`, on by default). Eval 091 FR-3 taught IM2 to read the sub's one
credits sentence as the screen's words; it accepts only that sentence, so the remote six's lock walk on staging would
fault IM2 on the switch's label (091's builder, call 5). The local stack never sets the variable and never draws the
switch.

## Rules

- **FR-1 IM2 accepts the switch.** `evals/interviewer_marks.py` IM2 reads the switch's label (the element with
  `data-testid=record-at-lock`, its text *Record {face} at lock · {changePrice} credits*) as the screen's own words beside
  the sub's sentence: the only number in it is the served `changePrice`, no currency; a second switch, or a label with
  another number, still faults. Where the server serves `recordOnSend: false` the switch is absent and IM2 reads as 091
  left it. `INTERVIEWER_MARKS_VERSION` 15 → 16 with its note.
- **FR-2 The lock journey leaves the switch on.** `evals/interviewer_leg.py`'s lock step records whether the switch was
  drawn and its state (on), never turns it off, and asserts the lock body carries no `recordOnSend` flag when the
  switch is on (keel-web 132's three states); a journey that wants staging's skip is none of the six.
- **FR-3 Nothing else moves.** The other marks, 091's reading of the sub, the journeys' other steps.

## Acceptance

`make unit` green with ZERO failed (master's counts as 091's tasks.md records them: 3,888 / 0 / 53 on the live
checkouts); a unit test of IM2 with the switch drawn (staging's shape) and without (the local stack's). Build on the
founder's word of 2026-10-30, before the remote six; it touches `evals/interviewer_marks.py` and the lock step of
`evals/interviewer_leg.py`, so it waits for 092's merge or is rebased over it.
