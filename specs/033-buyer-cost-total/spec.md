# Feature Specification: marks v13 — the buyer's cost is one total

**Feature Branch**: `033-buyer-cost-total` (keel-e2e-eval, off `master` at `495b06f`, `MARKS_VERSION` 12)

**Created**: 2026-10-10

**Status**: Implemented on its branch, 2026-10-10; the sibling of keel-cloud `077-buyer-cost-total` (branch
`077-buyer-cost-total` at `dc13341`, off `911f08c`), written against that branch. **No run of record**
(`WHY=marks:13` is not run or proposed here, and v12's is still on hold by the founder). `DRY=1` is the only
run this spec makes, and it spends nothing. Not pushed, merged or deployed.

**Input**: keel-cloud `specs/077-buyer-cost-total/spec.md`; `canon/designs/cost-first-price-design.md` §9; the
registry export `src/main/resources/keel/dimension-registry.json` (decision 17); the corpus at revision 7
(`canon/designs/measured-beliefs/corpus/`, `sim/check_corpus_r7.py`); the two instruction files and the inference
`CONTRACT_VERSION` 8; this repository at `495b06f` (specs 031 and 032 as house style).

## The one sentence

**`MARKS_VERSION` goes 12 → 13 with judgement calls 67–70: Existing sacrifice owes the model nothing on either
screen (the calibration entry is key + note, options refused with C2 as Price's are; the respondent item is the key
alone), `W10` and `U1` retire, the registry's respondent control is `cost_total` with no `code_rule`, the corpus is
read at revision 7 (an r6 file refused by name), and `rescore.py` refuses every bundle below 13.**

## What changes, stated first

| Where | v12 | v13 |
|---|---|---|
| `registry.py` | Existing sacrifice respondent `branch_pick_amounts`, a cost `code_rule` of kinds | `cost_total` (yields a number, invariant 6); a cost carrying a `code_rule` or any other respondent control is an invariant-5 fault; `cost_total` is code-written |
| calibration job | Existing sacrifice owes 4–6 options with `unit` (U1) | key + `respondent_note` only; options are `C2`; question not read |
| respondent job | Existing sacrifice owes options + `units[i]` (U1) and a question carrying the recall words (W10) | the key alone; nothing the model writes is read |
| `corpus.py` | `REVISION = 6`; picks `{currency, period, amounts[...]}`, `labels`/`units`, `optionCounts` | **`REVISION = 7`**; picks `{mode, value, currency, period}` / `{nothing: true, ...}` / `{chip}`; no kinds, no `optionCounts`; r6 refused by name as v12's |
| brief figures | time-only from the amounts' hours | time-only = B2C `HOURS` totals; the median hours per the founder's period |
| `marks.py`, `marks.toml`, `rescore.py`, `AGENTS.md`, `README.md` | v12 | v13 (*run of record: none yet*); rescore refuses < 13 |

## What this spec does not do

- It writes no instruction, registry entry or corpus entry: keel-cloud 077 does all three.
- It runs no model and does not run or propose the certificate; `DRY=1` only.
- It touches neither `why.py`'s events nor `models.py` nor the journey evals; it never writes to a sibling.

## Success Criteria

- **SC-001** `make unit` green.
- **SC-002** `make instruction-eval DRY=1 MODELS=exported` against the 077 worktree: `compare_correctness` 1.00, the
  denominators read off the registry.
- **SC-003** A revision-6 corpus file, a v12 registry and a v12 bundle are each refused by name.
