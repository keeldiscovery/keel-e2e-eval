# Spec 123 -- The referee follows keel-cloud 193

keel-cloud 193 (2026-11-01, the founder's four approved improvements from the nine-entry run) moves four things the
harness mirrors. Builds on 119-122.

- **FR-1 The cost sentence** (`instructions/chain.py` ~256-286, the mirror of `CommercialChain.costBelief`): hours
  are spent by `actor_plural` (never the deciders; the per-unit tail dropped when the unit is the subject's own noun);
  a rate with a verb-phrase loss reads *About {figure} of {base} {per} {loss}.*, else the colon form; an hours base that
  is the lack itself (*go without*, *lack*, *miss*) drops *on {base}*. Money unchanged. Fixtures and
  `tests/test_chain*.py` move with why; `build/brief-facts` if it is checked in.
- **FR-2 E4 in the served frame** (`instructions/score.py` ~627 and `marks.py`): the gate and the **served** Frequency
  question (`spoken.py`'s window-first frame, *In {window}, on how many {unit} did you {clause}?*) are each at most
  `STEM_MAX_WORDS`; the scripted part-1 job's `event` on every back-test entry is measured in that frame and, where it
  overruns (18-careforce at least), the entry's `event` is shortened in keel-cloud's
  `canon/designs/measured-beliefs/backtest/*.yaml` as **corpus revision 23** (a note at the head of each moved entry,
  the clause's verb and object kept); `cut_to_fit` stays for stored items only.
- **FR-3 The numbers mark** (`marks.py` ~1010, `problem.infer`'s `numbers`; `corpus.py` ~878 `_digits`): a digit run
  in Keel's statement passes when it appears in the founder's typed problem text and is not one the beliefs ask (a
  count of people, a frequency, a duration of the job, a cost to them, a price); any other digit still fails. The
  fixture statements that carried none are unchanged.
- **FR-4 No fallback condition on the decision-maker's link** (`harness/vectors_script.py` `decider_condition` ~506):
  with no written `screeners.decider` the link serves **no** condition (`None`), never the segment's chip said to the
  decision-maker; `context._hands_condition` for `LINK_B2B` reads the same. The journeys and the walk tolerate the
  absent screen (they already do on an entry with no condition).
- **FR-5** `make unit` green (`set -o pipefail`); `tests/test_revision_*` for revision 23.

## Acceptance

`make unit` ZERO failed against keel-cloud 193's worktree or master. The next quality cycle walks 18-careforce's money
study with no condition screen and its problem study's Frequency clause whole.
