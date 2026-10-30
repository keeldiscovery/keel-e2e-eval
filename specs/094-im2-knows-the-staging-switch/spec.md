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
- **FR-1a IM2 accepts Send more's one credits note.** keel-web 131 put one note under S3's format rows, *Each person who
  answers uses 30 credits, whichever way they answer.* (`data-testid=format-credits`, `FORMAT_CREDITS_NOTE`); IM2 v15
  faults S3 on *credits* (journey s006, 2026-10-30, bundle `runs/20261030T125356Z-s006-paidly`). IM2 reads that one
  note as the screen's own words: the only number in it is 30 (the interview price), no currency; a second credits
  line on S3, or any other price word, still faults.
- **FR-2 The lock journey leaves the switch on.** `evals/interviewer_leg.py`'s lock step records whether the switch was
  drawn and its state (on), never turns it off, and asserts the lock body carries no `recordOnSend` flag when the
  switch is on (keel-web 132's three states); a journey that wants staging's skip is none of the six.
- **FR-2a The open-link leg reads keel-web 140's card.** Spec 092 was built against web `e4f204e`; web 140 (master
  `aec26ec`) now draws the served face on the arrival card and the email on the intro (journey s017 faulted on the
  card, 2026-10-30, bundle `runs/20261030T130043Z-s017-open-link`). `harness/browser.py` `arrival_interviewer` reads
  *{name}, Keel's interviewer, asks the questions · about {minutes} minutes* when `GroupArrival.interviewer` is served
  and the null form (*Keel's interviewer asks the questions · ...*) when it is null (contract 49); the intro's
  `arrival-who` reads *Signed in with Google as {email}* (the stranger's email, from `Interview.arrival`), and
  `arrival-not-you`'s href is the absolute `groupUrl`; the greeting needs no button press. `evals/open_link_leg.py`'s
  card and intro asserts and `tests/test_open_link_092.py`'s fixtures follow, with why.
- **FR-3 Nothing else moves.** The other marks, 091's reading of the sub, the journeys' other steps.

## Acceptance

`make unit` green with ZERO failed (master's counts as 091's tasks.md records them: 3,888 / 0 / 53 on the live
checkouts); a unit test of IM2 with the switch drawn (staging's shape) and without (the local stack's). Build on the
founder's word of 2026-10-30, before the remote six; it touches `evals/interviewer_marks.py` and the lock step of
`evals/interviewer_leg.py`, so it waits for 092's merge or is rebased over it.
