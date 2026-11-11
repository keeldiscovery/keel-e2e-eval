# Tasks 152 -- The copilot prototype

Branch `spec-152`, worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-152` (`.git` a file, asserted first),
cut at `c86bd08` (the spec). Built by a builder (Claude Opus 5.5) on 2026-11-11 ET. Nothing paid: no key read or looked
for, no vendor called; the server is exercised on `FakeClients`. Plan: `plan.md`.

- [ ] T1 plan.md and tasks.md before code
- [ ] T2 FR-1 `evals/copilot/prototype/server.py`: Session (turn, keys, ordering, record), Handler (GET static +
  copilot.json, POST /turn, POST /key), main (refusal, URL, run folder)
- [ ] T3 FR-4 the log: turns/*.wav, events.jsonl, keys.jsonl, session.json
- [ ] T4 FR-3 `frames.json` for the fixture's six items
- [ ] T5 FR-2/FR-3 `copilot.html`, `copilot.js`, `copilot.css`
- [ ] T6 FR-1 `make copilot-prototype`
- [ ] T7 FR-5 `tests/test_copilot_prototype.py`
- [ ] T8 FR-6 AGENTS.md paragraph
- [ ] T9 tasks.md closed with what was built
