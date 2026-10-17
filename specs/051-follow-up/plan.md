# Plan 051

Read first: the design (§2 the ladder, §5 the follow-up, §6 speak or type, §9 consent, §11 eval), keel-cloud 103's
spec and its registry `follow_up` blocks, keel-web 076's tasks.md selectors, specs 048–050 here (the seam, the
walk, the stand-ins), `harness/interviewer_fake.py`, `evals/interviewer_leg.py` `_Walk`, `harness/vectors_screens.py`
`Interview`, `stack/cloud.py` (the transcriber pin), `stack/ledger.py` (the stand-ins).

| Piece | Place | Modelled on |
|---|---|---|
| contract 19 pins | `harness/`, `stack/`, README, AGENTS, `instructions/marks.py` header | 048 FR-1 |
| `LADDER`, `first_rung` | `harness/interviewer_fake.py` | 050's framing-line constants held to the composer |
| FOLLOW_UP in `KINDS` / `UNSPOKEN`, the fake's per-role clips | `harness/interviewer_fake.py` | IS_THAT_RIGHT (048) |
| the fake transcriber's two sentences | `stack/cloud.py` env | `KEEL_INTERVIEWER_FAKE_TRANSCRIPT` |
| text walk: `_follow_up`, `_speak_or_type` | `harness/vectors_screens.py` `Interview` | `_gate`, `_items` |
| AI walk: `_Walk.follow_up`, the silent window | `evals/interviewer_leg.py` | `_Walk.story`, `_recorded_pilot` |
| people's `follow_up` lines | `harness/corpus_script.py`, `evals/preludes.py` | `story`, `anchor_chip` |
| backfill stand-in | `stack/ledger.py` `stand_in_old_words` (drop FOLLOW_UP) | 050 FR-5 |
| consent assertion | both walks' intro step | 050 FR-7 (mic off) |
| IM23–IM27 | `evals/interviewer_marks.py`, `tests/test_interviewer_marks.py` | IM21 / IM22 |

Order: 1 pins + ladder + unit tests (no stack); 2 fakes + stand-in; 3 text walk (S-005 first); 4 AI walk (S-006);
5 marks + seeded faults; 6 full `make unit`, `make eval`, tasks.md counts; remote journeys when staging has it.

Notes: the walk never hard-codes a wording -- every question it expects is composed from the ladder copy and the
served labels; a mismatch is a DRIFT, not a tolerance. Keep 050's gap and beat tolerances. The 120 s cap is asserted
on the wire (`maxSeconds`), shortened on the seam for the clock.
