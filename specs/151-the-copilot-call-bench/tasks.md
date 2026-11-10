# Tasks 151 -- The copilot call bench

Branch `spec-151`, worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-151` (`.git` a file, asserted first).
Nothing paid: no key, no model call, no audio rendered. Plan: `plan.md`.

- [ ] T001 FR-1 `questionnaire.py` + the committed fixture `fixtures/questionnaire-08-fresco.json`
- [ ] T002 FR-2 `catalogue.py`: the 18 founder habits, the 9 respondent behaviours, verdicts, tiers, states, rules
- [ ] T003 FR-3 `plan.py` (the four rounds' coverage, seeded) and `writer.py` (prompt, request, validate, rewrite once,
      drop + count, the fake writer)
- [ ] T004 FR-4 `render.py` (two tracks, one timeline, turn clocks, the noise bed share)
- [ ] T005 FR-5 `stacks/` (one interface, three stacks) + `clients.py` (transports) + the three instructions
- [ ] T006 FR-6 `bars.py`, `score.py` (A--G, certificate, costs), `report.py` (sheets, page, register)
- [ ] T007 FR-7 `bench.py` + `make copilot-bench` (refusal without both keys unless DRY)
- [ ] T008 FR-8 AGENTS.md paragraph beside the noise-capture certificate
- [ ] T009 FR-9 `tests/test_copilot_bench.py`
- [ ] T010 Gate: `make unit`, the DRY run, lint; this file filled in
