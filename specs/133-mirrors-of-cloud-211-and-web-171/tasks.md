# Tasks 133 -- The harness mirrors keel-cloud 211 and keel-web 171

Branch `spec-133`, cut off origin/master `b1678e5`, in the worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-133`
(`.git` a file). Built 2026-11-04 (ET) against keel-cloud-docs master `e485abeb` (211 merged) and keel-web master
`2523777e` (171). Not merged; nothing paid (no quality-walk, advise, remote journey or `claude -p`); no corpus revision,
contract or `MARKS_VERSION` moved (211 moved none).

| Commit | What |
|---|---|
| `8d28b22` | the gate's own: `respondent_review` in `DORMANT_CLASSES` (master red, see Deviations) |
| `a3eea51` | FR-1 to FR-4: the rules, the scripted writer, the pins, the card |
| this commit | `tests/test_cloud_211_mirror_133.py` (20), these tasks |

## FR-1 Rules by name

- [x] T001 `evals/backtest.LOCK_NOTES`: `L33` (a Buyer and payer row for a role never typed in this Answer), `L34` (a
  priced Commitment step without a free smaller step), `X8` (the circumstance or job drops a founder word, or adds
  words in neither) -- `lock_notes` reports them by name.
- [x] T002 `instructions/score.py`: `founders_own_step` (`ScreenResultApplier.foundersOwnStep`), `untyped_role`
  (`untypedRole`, `L33`, read only where the Answer is typed, `named` the decider's words and role and the person with
  the problem) and `L34` on Commitment in `list_faults` (new keyword `named`, default none).
- [x] T003 `instructions/step_cost.py` (new): `StepCost` ported -- `of`, `costs`, the three closed vocabularies held to
  the cloud's source by test, and `l34` in the cloud's words.
- [x] T004 `harness/qualifiers.x8`: `X8`'s circumstance and job halves as 211 moved them -- no founder word of WHEN or
  WHAT dropped (was more than `MOST_DROPPED`), a preposition the clause swaps aside (`PREPOSITIONS`, `content_only`,
  held equal to the cloud's set); an added word keeps its one. The negation and WHICH PEOPLE halves did not move.

## FR-2 The fake writer's rows

- [x] T005 `vectors_script.keels_smaller_step` / `KEELS_SMALLER_STEP` (*a look at how it works*, keel-cloud's own words
  for Keel's step in `AfterTheReRunsTest`): where the entry's Commitment list is its step alone and the step costs
  money, data or a signature, the scripted draft (`drafted_list`, so `first_draft` too) carries the free smaller step
  with its `reason` (L7); the founder saves both rows (`saved_list`); `smaller_step` serves the soft yes on it
  (*Probably, after a look at how it works first*). Eleven back-test entries (08, 09, 11, 13, 15, 21, 23, 25, 30, 32,
  34); no golden step is priced, so no golden list moved.
- [x] T006 `wire_code` for `one_step`: `step`, then `smaller_step` (`SavedList.codeFor`; the harness sent `step` twice).
- [x] T007 Buyer and payer: every scripted redraft's rows are roles the walker's Answer (`answer_text`) types -- held
  by test with no named people at all; nothing in the writer had to move.
- [x] T008 The context result: `context_result` keeps the typed WHAT and WHEN whole -- held by `qualifiers.x8` on every
  entry; nothing had to move.

## FR-3 Pins

- [x] T009 `vectors_screens.COMMITMENT_ANSWER_QUESTION` *What's the first real step you'd want them to take, and what
  would it cost them?* (205's kept as `COMMITMENT_ANSWER_QUESTION_205`); 132's pin re-pinned to refuse 205's.
- [x] T010 `friction.UNTIMED_BELIEF`, `time_owed`, `belief(..., owed=)` -- Codyco's untimed, not-sure and timed beliefs.
- [x] T011 `vectors_script.prevalence_people` / `founder_prevalence_question` (`WindowFrame.people`, `prevalence`):
  Fresco's, AirCaps' and Codyco's frames, Lullaby's *... under six months in the US had to ...*, the bare plural with no
  segment.
- [x] T012 `vectors_script.who_answers` (`PersonaModel.whoAnswers`), asserted on the persona leg
  (`corpus_scenario.leg_persona`, B2B: the decision-maker's type's label is the whole title, no co-decider yet).
- [x] T013 `corpus.every_benefit`, `every_benefit_served` (`BeliefSentence.everyBenefit`,
  `VectorsController.everyBenefitServed`).
- [x] T014 The typist fixture's *Four short answers, a phrase each.* (171; on master `6b7a8bd`) -- held by test.

## FR-4 The Commitment card's good example

- [x] T015 `quality/readers/dimensions.md`: Fresco's paid pilot carries the free smaller step *a look at how it works*,
  its options *Yes, I'd start a paid pilot on one site · Probably, after a look at how it works first · Probably not ·
  No*; no rule line moved. `tests/test_dimension_cards_131.py`'s example re-pinned; a test holds the file equal to
  keel-cloud's vendored copy but for those lines.

## FR-5 Gate

`set -o pipefail; make unit 2>&1 | tail -1` at the head: see the commit's line below (master `b1678e5` against the same
siblings: 5,327 passed / 5 failed / 61 skipped -- four the routing v17 pin, one 132's Commitment pin that 211 moved).

**5,352 passed / 0 failed / 61 skipped** (257.86 s; the tree this commit adds only this file to): +20 = `tests/test_cloud_211_mirror_133.py`.

## Deviations

- **Master was red** on `tests/test_instruction_models.py` (2) and two routing tests: `b1678e5` pinned keel-cloud 209's
  `respondent_review` class last without adding it to `instructions/models.py`. The main checkout held the fix
  uncommitted; `8d28b22` carries the same hunk byte for byte (so the two merge clean). Not 133's scope; needed for the
  gate.
- `wire_code` (T006) was not named by the spec: the harness coded Commitment's second row `step`; it now sends the
  cloud's `smaller_step`. The cloud derives codes itself, so nothing stored moves.
- Keel's smaller step is one fixed phrase, the cloud test's own (*a look at how it works*), not composed per entry --
  no trade's word, the same on every entry (the persona rule).

## Owed elsewhere

- **keel-cloud**: the vendored cards (`src/main/resources/keel/dimension-cards.md`) and `RespondentReview.CARDS_SHA256`
  move to this file's bytes in their own commit (FR-4): the review turn still reads Fresco's example without its free
  step.
