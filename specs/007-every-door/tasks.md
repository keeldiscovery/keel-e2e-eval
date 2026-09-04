# Tasks: S-003, every door opens

**Input**: [spec.md](spec.md) (FR-001..006, SC-001..003) and keel-cloud
`canon/designs/every-door-design.md`.

**Rules**: the referee owns no product code; a dead door is a `runs/DRIFT.md` entry. Playground
profile by default (`PROFILE=playground`); bring the stack up with `make up` first, then `make
eval` (a `make up` plus two evals exceeds a ten-minute command limit). Gate: `make unit`, then the
scenario green warm and cold.

- [ ] T001 `harness/doors.py` (FR-001) + `tests/test_doors.py` (FR-004).
- [ ] T002 `Shell.main_text()` (FR-003).
- [ ] T003 `evals/test_s003_every_door.py` (FR-002): seeds, enumeration, opening, external
      checks, the two probes, `doors.json`.
- [ ] T004 First run against keel-web `9771dd7`; DRIFT #20/#21 with evidence (FR-006).
- [ ] T005 Re-run once keel-web `008` lands; mark #20/#21 RESOLVED with the hash; coverage test
      once the ledger row lands (FR-005).
- [ ] T006 `make unit` green; commit with the trailers; no push.

## Discovered

(Record here anything the run taught that the spec did not know.)
