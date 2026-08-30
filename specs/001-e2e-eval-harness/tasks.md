# Tasks: E2E Eval Harness

**Input**: spec.md, plan.md, research.md, data-model.md, contracts/, quickstart.md,
../e2e-eval-design.md (design of record)

## Phase 1: Setup

- [ ] T001 Repo skeleton: Makefile (up/down/eval/report targets), stack.toml (paths/ports/timeouts per data-model.md), docker-compose.yml (postgres:16, port 55432, db/user/pass keel), requirements.txt (pytest, playwright, requests), README.md from quickstart.md
- [ ] T002 stack/config.py: stack.toml loader with defaults and path validation (clear error naming the missing sibling)

## Phase 2: Foundational

- [ ] T003 stack/processes.py: spawn with start_new_session, pgid registry in runs/.stack/, poll-based health-gate helper, killpg teardown (research §3–4)
- [ ] T004 [P] stack/postgres.py + stack/cloud.py + stack/web.py: boot each piece per contracts/stack-contract.md (env injection incl. the two base-URL overrides, gates, /mcp reachability check)
- [ ] T005 [P] stack/vite.eval.config.ts: port 5173 strict, proxy /v2 → http://localhost:18080
- [ ] T006 harness/steps.py + harness/evidence.py: step() context manager, transcript.jsonl, numbered screenshots, versions.json (four repos + dirty flags), verdict.json in finally, report.html generator from transcript alone (contracts/evidence-contract.md)
- [ ] T007 tests/ (stackless): unit tests for steps transcript ordering, report generation from a fixture transcript (incl. crashed-scenario partial transcript), config loader errors

## Phase 3: User Story 1 — one command up/down (P1)

- [ ] T008 [US1] Wire Makefile up/down/report to the stack package; up prints gates as they pass; fails fast on taken ports naming the owner; down idempotent, safe when half-up
- [ ] T009 [US1] evals/conftest.py: session stack fixture (attach if gates pass, else boot and own teardown), function run_dir fixture

## Phase 4: User Story 2 — the smoke plays three parties (P1)

- [ ] T010 [US2] harness/driver.py: FounderAgent — loads SKILL.md from the keel-skill checkout, v2 loop over /v2/agent/** (get_next kind branch, get_context granted handles only, submit with token; refusal recovery per {rule, problem, remedy}; facts store), consults scenario payload builders only
- [ ] T011 [US2] harness/browser.py: founder context + isolated participant context; page objects for overview/stage/invite/invitations/brief and the participant survey; every navigation opens tool-issued URLs verbatim and asserts render (FR-005)
- [ ] T012 [US2] evals/scenario.py: Scenario base (payloads, answers, about_line) per data-model.md
- [ ] T013 [US2] evals/test_s001_smoke.py: full choreography per plan §S-001, assertions on every leg (revision advances, verdicts move, brief renders), screenshots throughout
- [ ] T014 [US2] Failure-path check: with vite killed, S-001 fails at a browser step with page HTML + console captured and report generated (SC-003) — automate as a harness unit test with a stubbed page where practical, verify manually otherwise and document in README

## Phase 5: User Story 3 — evidence reviewable (P1)

- [ ] T015 [US3] report.html polish per evidence-contract: party badges, collapsible wire JSON, failure anchor, self-contained thumbnails; `make report RUN=<dir>` rebuild target
- [ ] T016 [US3] versions.json + header rendering verified against all four repos incl. dirty flags

## Phase 6: Polish

- [ ] T017 Run quickstart end-to-end on this machine: make up, make eval K=s001 twice (SC-004 no cross-run bleed), make down leaves nothing behind; fix what surfaces
- [ ] T018 Document drift-report duty in README (this repo reports product-repo bugs, never fixes them) + template runs/DRIFT.md note format

## Dependencies

T001–T002 → T003 → {T004, T005, T006, T007} → US1 (T008–T009) → US2 (T010–T014; T010∥T011∥T012, T013 after all three) → US3 → Polish.

## Implementation strategy

MVP = Phases 1–3 (stack up/down). US2 is the heart; US3 makes it reviewable; T017 is the real
proof and runs on the actual machine, not in theory.
