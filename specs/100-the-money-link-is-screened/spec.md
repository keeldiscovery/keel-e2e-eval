# Spec 100 -- The money link is screened: S-016 walks one person inside and one outside the founder's people

keel-cloud 166 + keel-web 145 (the founder, 2026-10-30): on a money-only study the person's link, which has no gate,
asks the WHICH PEOPLE screener as `Interview.condition` before the idea card; an answer outside goes to the exit with
`outsideSegment: true` alone, final on the token and counted apart. S-016 (`evals/test_s016_money_only.py`,
`evals/scope_journey.py`) today walks the founder to the lock and never opens a person's link; the quality walk's
COMMERCIAL studies answer the money link without a screener.

## Rules

- **FR-1 S-016 opens two links.** After the lock, one person answers the screener inside (the entry's own people) and
  goes on through the idea card and the six money questions; a second answers it outside and meets the exit; the
  journey asserts the served interview carries `condition` and no gate, the outside response is `{outsideSegment:
  true}` alone and the People page / Pilot tile count that person apart (the words the web uses for a gate's
  outside). Text door; the AI door's leg (`evals/interviewer_leg.py`) asks the same screen where its link carries
  `condition` (as it does for the decision-maker's, spec 076 FR-4).
- **FR-2 The walk's money studies.** `evals/corpus_scenario.py`'s respondent leg on a COMMERCIAL-scope study answers
  the screener inside for every scripted person (the entry's people are inside by construction); a scripted person
  marked outside in the corpus (where one exists) answers outside and is asserted apart.
- **FR-3 Marks.** The scope marks (`evals/scope_marks.py`) gain one row: *the money link screens* -- `condition` served
  on a money-only link with a context condition, none where the context carries none; `MARKS_VERSION` moves if a
  mark reads it.
- **FR-4 Nothing else moves.** S-015 (problem alone keeps its gate screener), the decision-maker's screener legs, the
  instruction screens.

## Acceptance

`make unit` green with ZERO failed; `make eval K=s016` green on the local stack at keel-cloud 166 and keel-web 145;
`make eval K=s006` (the decision-maker's screener) still green. Build on the founder's word of 2026-10-30, after both
merge, after 099.
