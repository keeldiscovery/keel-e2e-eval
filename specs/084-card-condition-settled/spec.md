# Spec 084 -- The card's *Only people who* line is the settled condition (keel-cloud 148 FR-1), mirrored

keel-cloud 148 (keel-cloud-docs `f48f256e`, contract 44 unchanged) made the context card's *Keel understands* sentence,
its *Only people who* line and the confirmed slots read ONE settled condition: code's drawn condition where the
founder's WHICH PEOPLE carries a qualifier and the model wrote none or another (145 FR-4a), the model's where it names
the same qualifier or the people carry none. Before 148 the card drew the result's condition as written, so on a
`DRAWN` row (07-mulchrun: the model writes none, code draws *are based in the Dallas-Fort Worth suburbs* at the
confirm) the card had no line; spec 077 FR-1 pinned that in `harness/vectors_script.card_condition` ("the result's, so
none on a DRAWN row"). On staging `f48f256` + keel-web `786d4c3` (2026-10-28) S-007 is red in 48 s at *the card says
what Keel understood ... Only people who*: the card draws `Only people who: are based in the Dallas-Fort Worth
suburbs.` and the harness wants none. Staging is right by 148; the harness moves.

## Rules

- **FR-1 The card's condition is the settled one.** `card_condition(entry)` returns `segment_of(entry)["condition"]`
  (the settled condition: code's drawn one on a `DRAWN` row, the scripted one elsewhere), never
  `scripted_segment(entry)["condition"]`; its docstring names 148 FR-1. `leg_context`'s comment in
  `evals/corpus_scenario.py` (~386, "spec 077 FR-1: ... none on 07-mulchrun") says 148 instead. `scripted_segment`
  stays (the fake's own result still writes none on a `DRAWN` row).
- **FR-2 Pinned.** A unit test: `card_condition` on 07-mulchrun is the drawn condition and equals the confirmed
  segment's condition (`segment_of`), and on an entry with a scripted condition it is that condition; the
  `read_back` / `segment_line` tests do not move.
- **FR-3 Nothing else moves.** The marks, the readers, the quality cycle, 082's and 083's work, `REVISION` 17.

## Acceptance

`make unit` green with zero failed (master `851f9db`: 3,670 / 0 / 53). S-007 green on the local stack against
keel-cloud-docs `f48f256e` + keel-web `786d4c3` (`make up`, `make eval K=s007`, `make down`). No paid command. tasks.md
in 083's shape, short. Build on the founder's word -- given 2026-10-28 (the testing go-ahead): the remote six cannot be
green on the pair that is live without it.

## Observation for the founder (not this spec's)

On 07-mulchrun the card now says the place twice: in the sentence's core (*Landscaping crew leads in the Dallas-Fort
Worth suburbs, ...*) and in the line (*Only people who: are based in the Dallas-Fort Worth suburbs.*). 148 intends the
line to show what every link screens on; whether it should go quiet when the core already keeps the qualifier (as the
sentence does since 146 FR-2) is a keel-cloud product call.
