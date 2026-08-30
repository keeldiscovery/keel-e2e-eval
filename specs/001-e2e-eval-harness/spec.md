# Feature Specification: E2E Eval Harness — Stack, Parties, Evidence, Smoke

**Feature Branch**: `001-e2e-eval-harness`

**Created**: 2026-08-29

**Status**: Draft

**Input**: User description: "Create the keel-e2e-eval repo: stand up keel-cloud locally against
a Docker DB plus a keel-web instance, load the skill, and run end-to-end evals that emulate the
agent↔founder interaction, the redirection to the web UI, and a participant entering the survey
as a real user would — capturing screenshots of the interaction for later review. Scenarios
beyond the smoke are chosen with the user later. specs/e2e-eval-design.md is the design of
record; where this spec and it disagree, it wins."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One command stands the whole stack up (Priority: P1)

An operator runs `make up` and gets a working local Keel: Postgres in Docker, keel-cloud
migrated and serving, keel-web serving the founder and participant routes, all health-gated so
the command returns only when everything answers. `make down` reliably tears it all down.

**Independent Test**: `make up` on a machine with the three sibling repos checked out; then
`curl` the API and load the web root; `make down`; confirm no orphan processes or containers.

**Acceptance Scenarios**:

1. **Given** sibling checkouts at the configured paths, **When** `make up` runs, **Then** it
   returns success only after Postgres, keel-cloud, and keel-web each pass their health gate.
2. **Given** a running stack, **When** the founder web UI calls the API from the browser,
   **Then** requests succeed (no cross-origin failure) without modifying either product repo.
3. **Given** `make down`, **When** it completes, **Then** the Postgres container is gone and no
   gradle/vite child processes survive.

### User Story 2 - The smoke eval plays all three parties end to end (Priority: P1)

`make eval K=s001` drives a complete discovery: the scripted founder-agent runs the SKILL.md
loop on the wire; every handoff is executed in a real browser (approve on REVIEW, mint the
invite link on INVITE); a participant in an isolated browser context opens the tool-issued
link, consents, answers, submits; the agent interprets; verdicts move; the brief renders.

**Independent Test**: run S-001 against a fresh stack; it passes; deliberately break one leg
(e.g. stop keel-web) and it fails at the right step with the right evidence.

**Acceptance Scenarios**:

1. **Given** a fresh project, **When** S-001 runs, **Then** it completes create→frame→roles→
   assumptions→approve (×3 stages)→invite→answer→interpret→brief with a passing verdict.
2. **Given** any URL the protocol hands out (open_web screen, participant link), **When** the
   eval opens it, **Then** it opens exactly the issued URL (never constructed) and asserts the
   page actually renders — the standing cross-repo drift assertion.
3. **Given** a WAITING handoff, **When** the participant answers in the browser, **Then** the
   founder-agent's next poll advances — the interleaving matches a real discovery.

### User Story 3 - Every run leaves reviewable evidence (Priority: P1)

After any run — pass or fail — the user opens `runs/<id>/report.html` and reviews what
happened: numbered screenshots of every browser step (founder screens and the participant's
survey as a stranger saw it), the protocol transcript, the pinned repo versions, the verdict.

**Independent Test**: run S-001, open the report, confirm every browser step has a screenshot
and every protocol step its request/response; force a mid-scenario failure and confirm the
report still generates with page HTML + console dump at the failing step.

**Acceptance Scenarios**:

1. **Given** a completed run, **When** the report is opened, **Then** steps appear in order
   with thumbnails linked to full screenshots and transcript entries.
2. **Given** a failed run, **When** the report is opened, **Then** the failing step carries the
   page HTML and browser console at failure, and the report exists despite the failure.
3. **Given** `versions.json`, **When** read, **Then** it names the git commit of all four repos.

### Edge Cases

- Ports are dedicated (55432/18080/5173): a developer's own Postgres or dev server never
  collides; `make up` fails fast with a clear message if a port is taken.
- `make eval` with the stack already up attaches instead of re-booting (fast iteration).
- A scenario creates its own fresh project; the DB resets only at `make up`.
- The `/mcp` endpoint gets a reachability check even though the driver speaks HTTP.

## Requirements *(mandatory)*

- **FR-001**: `make up|down|eval` MUST orchestrate the stack per design §2, injecting the two
  load-bearing base-URL overrides, with health gates and process-group teardown.
- **FR-002**: An eval-owned vite configuration MUST proxy the API so the browser speaks
  same-origin, with zero changes to keel-cloud or keel-web.
- **FR-003**: The FounderAgent driver MUST load SKILL.md from the keel-skill checkout and run
  the v2 loop deterministically from scenario-supplied payload builders — no LLM calls.
- **FR-004**: Handoffs MUST be executed by their real party: REVIEW/INVITE by the founder
  browser, WAITING by the participant context; the eval MUST NOT shortcut a handoff on the wire.
- **FR-005**: Every tool-issued URL MUST be opened verbatim and asserted to render.
- **FR-006**: The step framework MUST produce per-run `transcript.jsonl`, numbered screenshots,
  `versions.json`, `verdict.json`, and `report.html`, including on failure.
- **FR-007**: S-001 (smoke, design §5) MUST be implemented and passing; the scenario API MUST
  make adding later positive/negative scenarios a matter of one new module.
- **FR-008**: `stack.toml` MUST configure sibling paths with working defaults (`../keel-cloud`,
  `../keel-web`, `../keel-skill`).

### Key Entities

- **Stack**: the orchestrated trio + Postgres; health-gated lifecycle.
- **Scenario**: module of payload builders, answer tables, and assertions.
- **Step**: unit of evidence — transcript entry + screenshot(s) or wire pair.
- **Run bundle**: `runs/<id>/` evidence directory; the reviewable product.

## Success Criteria *(mandatory)*

- **SC-001**: From clean checkouts, `make up && make eval K=s001` passes on the first try.
- **SC-002**: The S-001 report contains screenshots of every founder screen and every
  participant survey step, reviewable without reading any code.
- **SC-003**: Killing keel-web mid-run fails the scenario at the browser step with page-level
  evidence, and the report still generates.
- **SC-004**: A second `make eval K=s001` run against the same stack passes (fresh project per
  scenario; no cross-run bleed).

## Assumptions

- Sibling repos are checked out and buildable per their own docs (JDK21/Gradle for keel-cloud,
  Node for keel-web); Docker (Colima) is running.
- Auth remains deferred on all surfaces (keel-cloud gate 8); evals run unauthenticated.
- The scenario catalog beyond S-001 is explicitly out of scope — chosen with the user later.
