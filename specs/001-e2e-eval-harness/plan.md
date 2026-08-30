# Implementation Plan: E2E Eval Harness

**Branch**: `001-e2e-eval-harness` | **Date**: 2026-08-29 | **Spec**: [spec.md](./spec.md)

**Input**: spec.md + `specs/e2e-eval-design.md` (design of record)

## Summary

Build the fourth Keel repo from scratch: a Make-fronted Python/Playwright harness that boots
Postgres (Docker) + keel-cloud (gradle) + keel-web (vite behind an eval-owned proxy config),
drives a scripted founder-agent from SKILL.md over the HTTP agent surface, executes handoffs in
real browsers (founder context + isolated participant context), and writes a reviewable
evidence bundle per run. Ships with exactly one scenario, S-001 the smoke.

## Technical Context

**Language/Version**: Python 3.11+ (harness), Node 20+ (only to run keel-web), GNU make

**Primary Dependencies**: `pytest`, `playwright` (chromium), `requests`, `tomli/tomllib`;
`docker compose` for Postgres. Nothing else.

**Storage**: Postgres 16 container (stack state only); `runs/` directory (evidence, gitignored)

**Testing**: the evals are the tests (`pytest evals/`); plus a tiny `tests/` for the harness's
own pure logic (step framework, report generation) that runs with no stack

**Target Platform**: macOS (Colima) first; Linux-compatible

**Project Type**: standalone orchestration/eval repo; no product code ever

**Contract authority**: the running siblings themselves; wire shapes per keel-cloud
`protocol/AgentDtos` (kind-discriminated next, flat `{rule, problem, remedy}` refusals)

## Constitution Check

Constitution is the unfilled template. Inherited rule treated as binding: this repo reports
drift in the product repos, it never fixes them (design §6).

## Project Structure

```text
Makefile                     # up / down / eval / report targets
stack.toml                   # sibling paths + ports (defaults per design §2)
docker-compose.yml           # postgres:16 on 55432
stack/                       # orchestration package
  __init__.py, config.py     # stack.toml loader
  processes.py               # spawn/health-gate/teardown (process groups)
  postgres.py, cloud.py, web.py
  vite.eval.config.ts        # eval-owned config: port 5173, proxy /v2 -> 18080
harness/
  driver.py                  # FounderAgent: SKILL.md-derived v2 loop, deterministic
  browser.py                 # founder + participant Playwright contexts
  steps.py                   # step() context manager -> transcript + screenshots
  evidence.py                # run_dir, versions.json, verdict.json, report.html
evals/
  conftest.py                # stack fixture (attach-or-boot), run_dir fixture
  scenario.py                # Scenario base: payload builders, answer tables
  test_s001_smoke.py
tests/                       # stackless unit tests for steps/evidence/report
runs/                        # gitignored evidence bundles
README.md                    # operator-agent runbook (quickstart.md content)
```

## Phase 0/1 artifacts

`research.md` (transport, proxy, teardown, health-gate decisions), `data-model.md` (transcript
entry, run bundle, scenario shape), `contracts/stack-contract.md` (ports, env injection, health
gates), `contracts/evidence-contract.md` (bundle layout, report requirements), `quickstart.md`.

## S-001 choreography (the one scenario shipped)

FounderAgent: create → frame PROBLEM → introduce roles → introduce assumptions → REVIEW handoff
→ FounderBrowser opens the issued URL, screenshots stage, approves → repeat for SOLUTION and
COMMERCIAL → INVITE handoff → FounderBrowser types the about-line, mints link, captures the
shown URL → Participant context opens it, screenshots consent + each question, answers
supportively, submits → founder-agent polls, WAITING resolved → INTERPRET issuance names the
invitation → driver reads `response` handle, submits interpretation → FounderBrowser overview
shows moved verdicts (screenshot) → PROCEED_TO_BRIEF when offered → brief renders (screenshot).
Assertions ride each leg; every issued URL must render (FR-005).

## Delivery

Implementation by a Sonnet subagent; agent reports judgement calls, never commits; verification
(`make up && make eval K=s001` for real, on this machine) and commits happen centrally.
