# Spec 121 -- The referee follows the light tier to Claude Haiku 5.5

keel-cloud 190 (2026-11-01, the founder: *"Anthropic has launched a new Haiku version 5.5 … switch to that"*) moves the
`claude` host's `light` row to `claude-haiku-5-5` at effort `low` (routing v16, the `sampling` block gone), adds
`ModelRates.HAIKU_5_5` with two rate cards chosen per call, sends adaptive thinking with the row's effort instead of a
budget or a temperature, raises the classifier's `max_tokens` to 1,024 and reads its text by type, and re-prices the
light holds (`InferenceCharge.VERSION` 15: CONTEXT_INTERPRET and ASKED 3 -> 1 credit, `NEW_PROJECT_PRICE` 300 -> 298).
The referee mirrors every one of these. Builds on 119, 120.

- **FR-1 Routing v16.** `instructions/models.py` `resolve` / `resolve_effort`: the light row is `claude-haiku-5-5` at
  `low`, no `sampling`; `tests/test_instruction_models.py`, `specs/029-*/contracts/models-screen.json` and the S-012
  model check move with why; every fixture's light id moves.
- **FR-2 The noise check's classifier** (`evals/noise/pipeline.py`): `CLASSIFY_MODEL = "claude-haiku-5-5"`, the
  product's request as keel-cloud 190 sends it -- no temperature, `max_tokens` 1,024, adaptive thinking at effort low,
  the answer read from text blocks by type; the Makefile's comment at its `noise-check` target follows. (The check
  itself is paid and runs only on the founder's word; nothing here runs it.)
- **FR-3 Price version 15.** `harness/interviewer_fake.py`, `contacts_fake.py`, `interview_charge.py` and its note of
  the New-project gate (300 -> 298); the ledger mirrors of the light charges (CONTEXT_INTERPRET, ASKED at 1 credit).
- **FR-4 The settled line's cache fields on the light classes** are read by the cycle's cost note where it reads them
  (if it does); otherwise recorded as the coordinator's log check.
- **FR-5 Nothing else moves.** Contract 56, corpus revision 22, the marks.
- **FR-6 Tests.** Each mirror pinned with why; `make unit` ZERO failed.

## Acceptance

`make unit` green against keel-cloud 190 merged. The next quality cycle on the five catalog entries is the switch's
run of record, against cycle 6's 85.4%.
