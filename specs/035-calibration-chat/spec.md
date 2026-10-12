# Feature Specification: 035 Calibration chat marks (MARKS_VERSION 17 as implemented; written for 15)

**Branch**: `035-calibration-chat` (off `e3f192f`) · **Created**: 2026-10-12 · **Status**: Implemented, DRY only (see `tasks.md`, *Deviations*: v17, calls 76-80, corpus r9, no parity possible at 083)

**Sibling of**: keel-cloud `083-calibration-chat`:
- registry v2;
- inference `CONTRACT_VERSION` 9 → 10, with new screens `CALIBRATION_CHAT` and `ITEM_FEEDBACK`;
- `CALIBRATION_QUESTIONS` reduced to Prevalence and `RESPONDENT_QUESTIONS` to the gate;
- corpus revision 7 → 8.

It builds on keel-cloud 082 (direction-aware compare: AT/BEYOND/SHORT, drift STRONGER/SHORT, NOT_TESTED).
Design of record: keel-cloud `canon/designs/calibration-chat-design.md` §7 (marks per screen: one
measurable, ≤1 follow-up, preview obeys §2.5, no founder number leaks) and
`direction-aware-verdicts-design.md` §7–§8.

**Lean, as 034 was**: DRY only. No live model call, no run of record (`WHY=marks:15` is never spent or
proposed here), no push and no merge. Design §5 items 1–4 (keel-cloud 084 / keel-web 059) are out of
scope.

## User Scenarios & Testing

### US1: each chat turn is scored against the one-measure rule (P1)

The eval builds a `CALIBRATION_CHAT` case per (idea, dimension) from corpus r8 `chat/*.yaml`. That covers
the six simulated ideas (payroll, dark chocolate cheaper, superior chocolate, Lullaby, writing checker,
voice notes) across every dimension except Prevalence. It scores the model's turn(s) against these marks:

| Mark | Passes when |
|---|---|
| `one_measurable` | the COMPLETED proposal carries exactly one measure, of a kind in the registry's `chat.measures`, with the unit and occasion the corpus expects (or `leave_out` where the corpus says nothing fits) |
| `follow_up_budget` | at most one NEEDS_INPUT, asked only on cases the corpus marks `follow_up: expected` (two things named, or no number/unit); a needless follow-up and a missed one both fail |
| `preview_rules` | the respondent slots, framed by keel-cloud's `ItemFramer`, pass `ItemRules`: no leading option, escapes kept, frame untouched, balanced *…, or not?* where the frame is yes/no |
| `no_founder_leak` | no digit, number word or belief-phrase stem of the founder's measure in any respondent slot (LeakStems, extended to measures); sweep-A and sweep-B as today |
| `importance_list` | exactly six others, none naming the idea, none the problem restated or its result |

**Acceptance**
1. Payroll Current solution, with the answer *hours … and they still miss some*:
   - one follow-up passes;
   - zero follow-ups fail `follow_up_budget`;
   - a proposal measuring both time and errors fails `one_measurable`.
2. Payroll Relative advantage, with *About half the checking time* as the reply: a respondent slot with
   *half* or *50%* fails `no_founder_leak`.
3. Dark chocolate Adoption friction: `leave_out` passes; inventing *paying more* fails `one_measurable`.

### US2: feedback obeys the can and can't rules (P1)

`ITEM_FEEDBACK` cases (corpus r8 `chat/feedback.yaml`) give at least one per rule plus the allowed changes,
and are scored with the mark `feedback_obeys`:
- an allowed change is applied, with nothing else changed;
- a forbidden request is REFUSED with the right `rule` (SHOWS_NUMBER, SHOWS_BELIEF, LEADING_OPTION,
  DROPS_ESCAPE, CHANGES_FRAME);
- the post-change item passes `ItemRules`.

**Acceptance**: ChatPreview's example (occasion reworded; *Someone else checks it* added as SOMEONE_ELSE;
the band change refused as CHANGES_FRAME) scores 1.00.

### US3: DRY compare on the new rules (P1)

`compare_correctness` runs keel-cloud 083's engine over:
- corpus r8's seven reshaped entries;
- `verdicts/six-scenarios.yaml` (every row's status, drift, vector verdict and decision label from the
  Verdicts board).

`DRY=1` against keel-cloud 083 measures 1.00. The denominators are counted and printed, never typed.

### Edge cases
- A one-unit window has no Frequency case.
- B2B decision-maker items (Price team total, team size, Buyer/payer, Purchase friction, Commitment, a
  RULES fit point) are scored on the `COMMERCIAL_B2B` link.
- An r7 corpus file is refused by name as v14's.

## Requirements
- **FR-001** `MARKS_VERSION` 14 → 15, with new judgement calls 74 onwards. `rescore.py` refuses every bundle
  below 15.
- **FR-002** `contract.MODEL_SCREENS` adds `CALIBRATION_CHAT` and `ITEM_FEEDBACK`. `instruction.py` maps
  them to `calibration-chat` and `item-feedback`. `validate.py` maps them to the `InferenceScreen` values.
- **FR-003** `context.build_calibration_chat` and `build_item_feedback` build each context exactly as
  keel-cloud's `ScreenContextBuilder` does, including the dependent beliefs: the Current solution cap for
  Relative advantage, Existing sacrifice for Price, Frequency for a habit.
- **FR-004** The five chat marks above, plus `feedback_obeys`. Each restates keel-cloud's code check where
  one exists (`ItemRules`, C9, the FR-051/052 refusals) and is **proved equal** to the real
  `screenContracts validate` by `tests/test_instruction_chat_rules.py`. Only `follow_up_budget`'s
  *expected* label and `importance_list`'s near-neighbour check are corpus judgements.
- **FR-005** The calibration and respondent denominators move: CALIBRATION_QUESTIONS is the Prevalence
  entry only, and RESPONDENT_QUESTIONS is the gate only. They are read off the registry and plan, never
  typed.
- **FR-006** `corpus.py` reads revision 8 only, with the r8 shape checks mirrored from keel-cloud
  `sim/check_corpus_r8.py`.
- **FR-007** Thresholds in `marks.toml`: `one_measurable` 1.00, `follow_up_budget` 0.95,
  `preview_rules` 1.00, `no_founder_leak` 1.00, `importance_list` 1.00, `feedback_obeys` 1.00. The
  existing marks are unchanged except for their denominators.
- **FR-008** `make unit` is green with nothing skipped by this spec; `DRY=1` compare is 1.00.

## Success criteria
- **SC-001** Every new mark has a fixture that passes and one that fails each of its clauses.
- **SC-002** The parity test shows the eval's restatement and keel-cloud's validator agree on every fixture.
- **SC-003** DRY against keel-cloud 083 prints every denominator, and compare is 1.00.

## Open questions for the founder
- **Q1** `follow_up_budget` at 0.95 (a needless or missed follow-up tolerated 1 in 20), or 1.00?
- **Q2** Should balanced wording also be judged by the model judge (tone), or only by structure (proposed:
  structure only)?
