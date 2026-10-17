# Plan 053

Read first: the design §13a (D19, D20); keel-cloud-docs `specs/105-corpus-in-dollars/{spec,plan}.md` (FR-1's table
and 06-repeatline's renames, FR-6's GB that stays, FR-7's hand-off); the r12 corpus itself once 105 lands; keel-web
078's tasks.md (the drop-down's markup, for `MARKET_GROUPS`); spec 052 here (the healthy project, the DRY numbers);
`instructions/corpus.py` (the revision and its refusal), `tests/v9_fixtures.py`, `evals/contacts_leg.py`,
`harness/contacts_fake.py`, `evals/payroll_exceptions.yaml`, `harness/browser.py` `MarketStep`.

| Piece | Place | Modelled on |
|---|---|---|
| `REVISION = 12`, `_REVISION_OF[11]`, the docstring | `instructions/corpus.py` | spec 042's r10 -> r11 (call 110) |
| the canon skip, the refusal cases, the US test | `tests/v9_fixtures.py`, `tests/test_instruction_corpus_r11.py`, `tests/test_corpus_r11_shape.py` | the r11 cases beside them |
| the Spec 053 paragraph, r12 sha256s | `instructions/marks.py` | 051's paragraph, v19's hash list |
| the two fixtures at r12, GB kept | `tests/fixtures/corpus/09-fixture.yaml`, `10-fixture-b2b.yaml` | their r11 headers |
| fallbacks, the locator note, `MARKET_GROUPS` | `harness/vectors_script.py`, `harness/corpus_script.py`, `harness/browser.py` | -- |
| D20's journeys | `evals/payroll_exceptions.yaml`, `evals/test_s004_stranger_who_gives_orders.py`, `evals/test_s001_smoke.py` | -- |
| the currency guard, every journey | `evals/corpus_scenario.py` (from `evals/test_s007_mulchrun.py`) | S-007's sweep |
| S-014 in USD | `evals/preludes.py`, `tests/test_report_marks.py` | -- |
| contacts on the US | `evals/contacts_leg.py` | its GB counts |
| the participant language | `evals/interviewer_leg.py` | -- |

## Order

1. **Before 105 lands** (keel-cloud-docs still r11): FR-1's code and tests with the fixtures at r12 -- the canon
   tests then skip by name (`CANON_NOT_R12`) and the fixture tests run; `make unit` green with the skips counted.
2. **105 merged in keel-cloud-docs**: FR-5's two gradle commands there; the canon tests un-skip; fix only what reads
   a symbol, a market or a renamed phrase (FR-3h); FR-2's sha256s from `shasum -a 256` on the canon files.
3. FR-3 (a)-(g) and the D20 moves; S-001 / S-004 / contacts need 078 on the stack to prove, so their page reads wait
   for step 5; their unit-level files (scenario-set, page-object, stack-address tests) go green here.
4. The zero-spend re-measure (FR-5's five numbers) and the two grep gates (Acceptance 4), into tasks.md.
5. A fresh stack on keel-cloud 105 + keel-web 078: `make eval K="s005 or s006 or s007 or s014"`; then remote
   journeys once staging carries 105 + 078; DRIFT #95 only on a pound a page shows.

## Risks

- **Merge order.** r12 in the cloud and `REVISION = 11` here refuse each other by name: merge 105 and 053 together,
  then 078, then staging (105's plan says the same). A half-merge is a loud refusal, never a wrong read.
- **Stale exports.** keel-cloud's `build/brief-facts/` written at r11 compares `£` against r12's `$` and fails; it is
  the reminder to regenerate, not a tolerance to add. The master checkout's stack is running from keel-cloud-docs:
  regenerate only with no stack up from it.
- **Contacts counts.** S-006 is the only journey whose numbers change with the market (27 -> 26, 2 -> 1, the low
  balance); read each from `fake.size`, and if 105's fake contacts ever move, the leg follows the fixture, not this
  spec's digits.
- **078's drop-down.** Its markup is not written yet; `MARKET_GROUPS` and S-001's *three groups* are *as 078
  defines* -- if 078 keeps an optgroup or drops it, the read follows the page, and the smoke still asserts US is
  offered and selected.
- **Rollback**: revert 053 with 105; the fixtures' revision moves with `REVISION`, so a half-revert is refused.
