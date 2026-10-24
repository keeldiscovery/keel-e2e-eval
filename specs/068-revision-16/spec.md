# Spec 068 -- Corpus revision 16 and the walks of keel-web 106's screens (the harness half of keel-cloud 129)

keel-cloud 129 (keel-cloud-docs master `efdd37bf`) moved the entries to revision 16 (every back-test founder's Commitment
list is the step alone, so all 112 `yes_after_trying` picks became `yes_start`; the golden seven changed their revision line
and two Commitment options cut to 9 words), bumped the contract to 36 (`ContextFields.occasion`), and changed served words
(the gate's No label *I didn't*, Commitment options counted whole at 9 words, the fact frame as a question, the Adoption
plain frame naming the step). keel-web 106 (keel-web master, 3651081 and the contract-36 re-vendor after it) built the web
half of 128 with the selectors listed in `specs/106-after-the-batch-web/tasks.md`. Setting `REVISION = 16` alone leaves
225 unit failures and 191 errors: the fixtures, the slice, the mirrors and the marks digests are revision 15's.

## Rules

- **FR-1 Revision 16.** `instructions/corpus.py REVISION = 16` (with `_REVISION_OF[15]` naming what 15 was), fixtures,
  the slice, the golden mirrors and the marks header's digests re-cut from keel-cloud-docs master; `tests/test_corpus_r15.py`
  becomes the r16 test that diffs every entry against keel-cloud's r15 mirror exactly as `sim/check_corpus_r16.py` rule D16
  lists (the 112 picks, the two cut options, the revision line) and nothing else; the cloud checker prints OK on all 35.
- **FR-2 The spoken mirror follows the served escapes.** `instructions/spoken.py`'s registry escape list reads Ability's
  escape as *I can't say* (the served one; the guard called Issen's clean run RED on it) and Commitment as none; the guard
  stays 109 of 109 on the golden corpus and counts Commitment's options whole (*Yes, I'd …* plus the step) at 9.
- **FR-3 The moved people's lines.** A follow-up line written for a second yes on Commitment (any of the 112) is typed only
  where the served follow-up lands on Commitment's *yes_start*; otherwise it is skipped with a finding, never typed on
  another rung (067 FR-3).
- **FR-4 The walks of keel-web 106's screens** (067 FR-7, owed): the walk reads back and holds on the golden seven and on
  the back-tests, using 106's selectors: consumer words on a consumer study (no *decision-makers*, *the payer*, *per
  person*, *new money*); *Did not hold* on a bar line past the bar; the Insights footers from the stored follow-ups and the
  GUESSED words apart; the friction row's status column at 390; the idea-name suggestion (`idea-name-suggestion`) with the
  box empty; the needs-input screen (`context-needs-input`) answered once; the *Another country* line and the currency list
  opening on the country's own; no plan screen after a closed price (already in the walk; held as a check); the occasion
  field (`context-occasion`) drawn from `occasion.noun` and sent on the PUT; the gate's No label *I didn't*.
- **FR-5 Contract 36.** Wherever this repo names the contract version or reads `ContextFields`, 36 and `occasion`.

## Acceptance

1. Unit suite green; the golden seven's numbers and marks unchanged on the 129 build (v20 stands); the three golden
   journeys (S-005, S-006, S-007) green on the local stack with the fake interviewer.
2. `make backtest DOOR=host ENTRY=…` loads every revision-16 entry (a unit test loads all 28 in back-test mode).
3. No queued chain whose command line carries the words `pytest evals`.
