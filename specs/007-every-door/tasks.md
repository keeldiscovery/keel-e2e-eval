# Tasks: S-003, every door opens

**Input**: [spec.md](spec.md) (FR-001..006, SC-001..003) and keel-cloud
`canon/designs/every-door-design.md`.

**Rules**: the referee owns no product code; a dead door is a `runs/DRIFT.md` entry. Playground
profile by default (`PROFILE=playground`); bring the stack up with `make up` first, then `make
eval` (a `make up` plus two evals exceeds a ten-minute command limit). Gate: `make unit`, then the
scenario green warm and cold.

- [x] T001 `harness/doors.py` (FR-001) + `tests/test_doors.py` (FR-004).
- [x] T002 `Shell.main_text()` (FR-003).
- [x] T003 `evals/test_s003_every_door.py` (FR-002): seeds, enumeration, opening, external
      checks, the two probes, `doors.json`.
- [x] T004 First run against keel-web `9771dd7`; DRIFT #20/#21 with evidence (FR-006).
- [x] T005 Re-run once keel-web `008` lands (`71c045a`): green, #20 RESOLVED. The coverage test
      learns S-003 when keel-cloud's ledger row lands (spec 026 FR-008) -- nothing to change here,
      the file already cites every `§` the row will name (FR-005).
- [x] T006 `make unit` green; commit with the trailers; no push.

## Discovered

- **Playwright never requests a favicon.** Headless Chromium under Playwright does not fetch
  `/favicon.ico`, so D4's resource half cannot observe design §5 F2 either before or after the
  fix; the fix is verified by inspection of `index.html`. DRIFT #21 was therefore not opened --
  the finding is folded into #20's note.
- **An honest 404 is D1, not D3.** `/i/nope` asks the wire `GET /v2/i/nope`, gets 404, and renders
  the not-found page; the first run scored that `failed_request`. The judge now reads "the wire
  said 404 and the screen said so too" as `not_found` (`harness/doors.py` `judge`, unit-tested).
- **Probes and the participant seed are untagged steps.** The rubric's GUI-P1 judges an
  interview reaching submit, and ORI-U1 wants a project identity; a probe of `/nope` has neither
  by design. Untagged, they are asserted but not scored, and the run scores 5.0 on ORIENTATION
  and CLARITY with FIDELITY and GUIDANCE `not_applicable`.
- **Unreached routes on this build**: `/login` (no link while logged in), `/connect` (only when no
  agent), the two People aliases, and `/i/:token` (the link is shown as text to copy, not an
  anchor). Reported in `doors.json`, not failed (design §3.5).
- **63 doors on 12 seeds, all open** on keel-web `9771dd7` already; the only dead thing was a
  path nobody links to.
