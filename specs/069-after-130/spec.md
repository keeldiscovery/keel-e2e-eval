# Spec 069 -- The harness after keel-cloud 130 (contract 37)

keel-cloud 130 (keel-cloud-docs master `48502f95`, contract 37, corpus still r16) changed served words the harness mirrors
for the golden journeys and the back-test walk. This spec brings the mirrors level so the golden journeys hold and the
back-test walk's expectations name 130's words; the re-runs themselves are the parent's.

## Rules

- **FR-1 The follow-up mirror follows 130.** `harness/vectors_script.py`'s composer (and `interviewer_fake` where it speaks)
  mirrors: the Price follow-up composed whole, text and spoken alike (*You put it below €3,000.* when the price was shown,
  the band said back on a rung, *You put it low. What would make it worth more?* when no price was shown); the Adoption
  statement frame *{Name} means {step}. Would you do that, or not?* wherever the idea's name is known (130 FR-11); the
  Commitment stem introducing a step the card never named (*Issen starts with a trial. Would you pay for one month after
  the trial, or not?*, 130 FR-10); the gate's event clause before the job, with the person's own time kept (*did a booking
  call come in on your shift?*, 130 FR-6) and the brief's line (*had a booking call come in on their shift*); Frequency's
  line in the window's unit (*months they …*, 130 FR-2); X12's drawn condition from a negative qualifier (*are past the
  beginner stage*, 130 FR-8).
- **FR-2 Contract 37.** Wherever this repo names the contract version or reads `SavedList.items`, 37 and the optional
  `replaces` (draft-only; read and recorded on the Check screen when present, never asserted on Save).
- **FR-3 The lock-time notes.** The walk records 130's new lock notes (S13 a saved row over the cap, L21 a replaced
  condition, M5 a jargon word) as findings when a back-test meets them, by name.
- **FR-4 Nothing else moves.** REVISION stays 16; marks v20 stands; the golden seven's numbers unchanged.

## Acceptance

1. Unit suite green.
2. S-005, S-006 and S-007 green on the local stack with the fake interviewer (the parent runs them after the host-door
   re-runs, since one stack runs at a time; the builder runs them only if `pgrep -fi "[p]ython -m pytest evals"` and the
   back-test runner are both idle, and tears the stack down after).
3. No queued chain whose command line carries the words `pytest evals`.
