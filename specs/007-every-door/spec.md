# Feature Specification: S-003, every door opens

**Feature Branch**: `007-every-door`

**Created**: 2026-09-04

**Status**: Draft — for the founder's review

**Input**: the founder's direction of 2026-09-04 ("login to the application, navigate to each
page like the smoke test but check that there are no dead links") and the design of record,
keel-cloud `canon/designs/every-door-design.md` (D1–D4, the walk, the two probes, scoring).

## Scope

A third scenario file, one new harness module, one unit-test module, the journey-coverage test,
`runs/DRIFT.md`. The referee owns no product code: a dead door is a DRIFT entry, never a
workaround. No policy change (the walk registers no facts; FIDELITY is `not_applicable`).

## User Scenarios & Testing

### User Story 1 - The founder's day, every door tried (Priority: P1)

Warm after S-001 (or cold through the prelude), the walk visits every seed route in the smoke's
order, enumerates every rendered link on each, opens each internal one once, checks each external
one once, probes the four unknown paths and the logged-out back door, and passes only if no door
is dead by D1–D4.

**Acceptance Scenarios**:

1. **Given** a seed page, **When** enumerated, **Then** every `a[href]` is listed with its text and
   normalised absolute `href`, and the list is recorded in the step.
2. **Given** an internal door, **When** opened, **Then** the step records the target's screen
   text, screenshot, response statuses, and the D1/D2/D3 judgement.
3. **Given** `/p/{id}/nope`, **When** opened, **Then** D2 fails against keel-web `9771dd7` (blank
   pane) and passes once keel-web spec `008` lands — recorded as DRIFT #20 either way.
4. **Given** any page load, **When** `GET /favicon.ico` answers 404, **Then** D4 fails (DRIFT #21).
5. **Given** the route table, **When** the walk ends, **Then** `doors.json` lists every route with
   the links that reached it; unreached routes are reported, not failed.

### Edge Cases

- One `href` is opened once per run even if many pages link to it; the row lists every source.
- The `?user_code=` query on `/connect` is kept once; other query strings are dropped for identity.
- The participant page `/i/{token}` is visited in its own context (no founder cookie) and has zero
  doors by design; that is recorded, not failed.
- `networkidle` can hang on the long-poll-free founder pages? It cannot — the founder UI polls on
  a 4 s interval, so the walk uses `domcontentloaded` + `fonts.ready` + a 1 s quiet window instead
  of `networkidle`.
- Responses that are expected: `401` on `/v2/me` while logged out (the back-door probe), which is
  the redirect's own cause; everything else `4xx`/`5xx` on `/v2/*` is D3.

## Requirements

- **FR-001** `harness/doors.py`: `enumerate_doors(page) -> list[Door]`, `normalise(href, base)`,
  `open_door(context, door, recorder) -> Verdict`, `check_external(context, door) -> Verdict`,
  `tally(routes, doors) -> Coverage`, the not-found marker (`"This page doesn't exist."`) and the
  empty-main rule in one place; `Verdict` ∈ `opens | not_found | blank | failed_request | unreachable`.
- **FR-002** `evals/test_s003_every_door.py`: seeds in the smoke's order; warm/cold prelude reuse
  exactly as S-002; the two probes; `doors.json` in the bundle; `§` citations for §1.0, §1.2,
  §1.4, §1.10, §2.1; `finalize_run(..., facts={})`.
- **FR-003** `harness/browser.py`: `Shell.main_text()` only.
- **FR-004** `tests/test_doors.py`: the judge against canned DOMs (a not-found body, an empty
  main, a normal page), `normalise` cases, `tally` with an orphan.
- **FR-005** `tests/test_journey_coverage.py` learns S-003 from the ledger once keel-cloud's
  `CANON.md` row lands (spec 026 FR-008); until then the scenario file cites the `§` lines and the
  coverage test is unchanged.
- **FR-006** `runs/DRIFT.md` #20 (blank pane) and #21 (favicon) from the first run, with the
  keel-web fix noted as spec `008` and marked RESOLVED with the hash once re-run green.

## Success Criteria

- **SC-001** `make eval K=s003 PROFILE=playground` green from a stack S-001 has run in, and cold.
- **SC-002** `make unit` green.
- **SC-003** The run bundle's `doors.json` and report list every door with a verdict; a reader can
  see which link on which page led where.

## Assumptions

- External doors fail the run on D4 (design §7.3) — none exist after keel-web spec `009`.
