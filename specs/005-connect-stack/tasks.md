# Tasks: The referee for the connect stack

**Input**: [spec.md](spec.md) (FR-001..015, SC-001..004, judgement calls). The journey:
keel-cloud `canon/journeys.md` §3 (2026-09-03) and `canon/mockups/` (frame letters used below).
Prerequisite: keel-runtime spec 001 (`--executor scripted`) implemented on its `master`.

**Rules** (AGENTS.md): this repo owns no product code and never fixes the product — a cross-repo
defect goes to `runs/DRIFT.md` with evidence. Scenarios are deterministic (no LLM). Every
assertion enforcing a journey moment cites it (`§n.m`). Gate: `make unit`, then `make up && make
eval K=s001 && make down`.

## Phase 1: Retire and re-plumb

- [x] T001 Delete the agent-protocol harness and its tests per FR-006 (`harness/driver.py`,
      `mcp_client.py`, `bridge.py`, `relay.py`, `founder_sim.py`, `agent_session.py`,
      `shaping_scoring.py`; `tests/test_bridge.py`, `test_relay.py`, `test_founder_sim.py`,
      `test_shaping_scoring.py`, `test_policy_v5.py`); delete `evals/test_s002…s011*.py`,
      `test_shaping_gauntlet.py`, `recipes.py`, `scenario.py`; drop `eval-shaping` from the
      Makefile and the `shaping` marker from `pytest.ini`. `runs/DRIFT.md`: the dated retirement
      note.
- [x] T002 `stack.toml` (FR-001); `stack/config.py` reads the two new paths; `tests/test_config.py`.
- [x] T003 `stack/cloud.py` (FR-002): connect verification URI; remove MCP/relay overrides.
- [x] T004 `stack/runtime.py` (FR-003) + `stack/lifecycle.py` (FR-004): the `runtime-home` gate,
      reset at up, kill at down via the heartbeat pid.
- [x] T005 `stack/auth.py` (FR-005): new response shapes; `login_and_keel_session`.
- [x] T006 Gate: `make unit` green (whatever remains), `make up` prints four gates, `make down`.

## Phase 2: Harness for the round-5 screens

- [x] T007 `harness/connect.py` (FR-007): run the skill script, parse its one line of JSON,
      record the step; raise on `runtime_unavailable`/`internal_error`; treat
      `authorization_pending_timeout` as a recorded stack failure.
- [x] T008 `harness/browser.py` (FR-008): the page objects listed, selectors taken from keel-web's
      built DOM (read `../keel-web/tests/visual/states/*.ts` and the components under
      `../keel-web/src` — do not guess). Wait on the frame's own words, never on sleeps; wait for
      `document.fonts.ready` before screenshots.
- [x] T009 `harness/interactions.py` (FR-009): the new kinds; `tests/test_interactions.py`
      updated; `harness/evidence.py` (FR-012): repo labels, report cards.
- [x] T010 `evals/policy.py` v6 + `harness/rubric.py` (FR-010/011); `tests/test_policy_v6.py`;
      `tests/test_scoring_math.py` / `test_scoring_seeded_loss.py` updated for the new category
      set.
- [x] T011 Gate: `make unit` green.

## Phase 3: S-001

- [x] T012 `evals/payroll_exceptions.py`: names, statements, the participants' typed answers
      (mirroring `../keel-runtime/keel_runtime/testing/scripts/payroll-exceptions.json`), the
      expected headline words and counts.
- [x] T013 `evals/test_s001_smoke.py` (FR-013): US2 steps 1–9 with `§` citations; the wire
      assertions of US2 scenarios 3 and 4.
- [x] T014 `tests/test_journey_coverage.py`: read `canon/CANON.md`; S-001 file lookup; passes
      against the amended ledger (FR-014 — the ledger edit is made in keel-cloud by the founder's
      session; if it is not there yet, say so in the report and leave the test red rather than
      editing keel-cloud).
- [ ] T015 Gate: `make up && make eval K=s001 && make down` green from cold; inspect the run
      bundle (screenshots per frame, report.html, score under policy v6). Anything the product
      does wrong → `runs/DRIFT.md` with evidence, not a harness workaround.

## Phase 4: Docs and hand-off

- [x] T016 `AGENTS.md`, `README.md`, `specs/005-connect-stack/quickstart.md` (FR-015).
- [ ] T017 Commit per phase in the house style with the trailers; no push. Final report: gate
      results, wall clock of the smoke, the run id, every DRIFT entry added.

## Discovered

- **T006's `make unit` is not fully green yet, by design.** `tests/test_interactions.py`,
  `test_scoring_math.py`, `test_scoring_seeded_loss.py`, `test_report_interaction_cards.py` still
  import `evals.scenario`/`evals.recipes`, which T001 deleted per FR-006; `test_journey_coverage.py`
  still points at the old `specs/projectv2/CANON.md` path. These four are explicitly Phase 2/3's
  own tasks (T009, T010, T014) to update, not Phase 1's -- recorded here rather than either
  blocking on it or quietly deleting tests that still describe real, needed coverage. T011's gate
  (end of Phase 2) and the final `make unit` run are where this must actually be green.
