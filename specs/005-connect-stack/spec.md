# Feature Specification: The referee for the connect stack (keel-e2e-eval, rewritten)

**Feature Branch**: `005-connect-stack`

**Created**: 2026-09-03

**Status**: Draft — for the founder's review

**Input**: the founder's direction of 2026-09-03: "rewrite keel-e2e-eval with the new
keel-connect-skill, keel-runtime, keel-cloud and keel-web, and after the rewrite write one journey
defined in the journey page, e2e, like a smoke test." The journey is keel-cloud
`canon/journeys.md` §3's amendment of 2026-09-03 (the screen review, round 5), drawn in
`canon/mockups/` and built by keel-web spec 007 and keel-cloud spec 023.

## What changes, stated first

The stack this repo referees has changed underneath it. Until today it stood up keel-cloud and
keel-web and drove a **scripted founder-agent over the MCP action protocol** from keel-skill
(`harness/driver.py`, `harness/mcp_client.py`, `harness/bridge.py`, `harness/relay.py`,
`harness/founder_sim.py`, `harness/agent_session.py`). That path is retired: keel-skill is
archived, the relay is no longer a founder surface, and every judgement now runs as an inference
job through the founder's own **keel-runtime**, connected by device code through
**keel-connect-skill**, and confirmed by the founder in **keel-web**.

So this feature:

1. **Re-plumbs the stack** — Postgres, keel-cloud, keel-web (as today), plus **keel-runtime**
   with the scripted executor (keel-runtime spec 001) — and launches the runtime the way a founder
   does: through `keel-connect-skill`'s script, whose one line of JSON hands back the device code
   the browser then approves.
2. **Replaces every scenario with one**: S-001, the smoke — the whole journey, once, deterministic.
3. **Keeps the referee's own machinery** where it is still true: the stack lifecycle and gates,
   the step recorder, the evidence bundle and report, the scoring layer's UI-visit checks, the
   DRIFT log, the ledger-coverage test.
4. **Retires** the agent-protocol half of the harness and its checks, the shaping gauntlet, and
   the old scenarios S-002…S-011 — recorded, not lost (git history; `runs/DRIFT.md` gains a dated
   note naming what was retired and why).

## User Scenarios & Testing

### User Story 1 - `make up` stands the connect stack up and proves each gate (Priority: P1)

Postgres, keel-cloud (with its founder base URL pointed at keel-web's `/p` and the connect
verification URI at keel-web's `/connect`), keel-web through the eval-owned Vite config (same-origin
proxy), and — new — a **runtime home** directory under `runs/.stack/keel-home/` that the connect
skill's script and the runtime share. `make up` ends with the runtime **not yet running**: the
smoke starts it, because starting it is part of the journey.

**Independent Test**: `make up` → gates print for postgres, cloud (`GET /v2/setup` answers), web
(`/` answers 200), and `runtime-home` (the directory exists and is empty of a heartbeat) → `make
down` kills every process the stack owns, including a runtime the smoke left behind.

**Acceptance Scenarios**:

1. **Given** a cold machine with the sibling checkouts, **When** `make up`, **Then** four gates
   pass in order and `runs/.stack/` holds a log per process.
2. **Given** a stack already answering, **When** `make eval`, **Then** the fixture attaches
   without booting (fast-iteration path, unchanged).
3. **Given** `KEEL_V2_CONNECT_VERIFICATION_URI` set by the stack to `http://localhost:<web>/connect`,
   **When** the runtime is started, **Then** the URL it prints is a keel-web URL the browser can
   open.

---

### User Story 2 - S-001: one founder's whole discovery, deterministic, scored (Priority: P1)

The smoke walks journeys.md §3 (2026-09-03) end to end in one run, in a real browser, against the
real four applications, with the runtime answering from keel-runtime's bundled
payroll-exceptions script:

1. **Arrival** (§1.0). Setup on the virgin instance (no agent key in the response). Login →
   the landing reads *No agent connected* and is gated (L2). The harness runs
   `keel_connect_check.py --runtime-path <keel-runtime> --base-url <cloud> --executor scripted
   --credential-backend file --no-browser --home <runtime home> --wait-seconds 15` and parses
   `authorization_started`'s `user_code`/`verification_uri`. The browser opens the URL → F/B →
   *Approve this device* → C reads *Agent connected*. Back at `/` → L1: the name field.
2. **Naming and the problem** (§1.1). Type the project name → *Save and continue* → C1. Type the
   problem → C2 (*Waiting on your agent*) → the scripted `NEEDS_INPUT` → C3 (the agent's one
   question) → answer → C5 (*Here's what we understood*, the script's statement verbatim) →
   *Save this* → C8 (*Understood*, *Continue* disabled) → the beliefs land → R1.
3. **The review** (§1.2). The card reads *Reviewing*; groups by role; both questions per belief;
   *Start over* present; *These are right — approve* → R4 → *Continue to step 3*.
4. **Steps 3 and 4** (§1.1 again, §1.2 again). Same walk for the solution and the price; during
   the solution draft, click *The problem* in the nav → S2 (approved card, "draft kept" note) →
   *Back to step 3*. After the last approval → S4's three-part note → *Go to People*.
5. **People** (§1.4). P1: one card per role with the pills. *Send the questions* for *A payroll
   manager* → P2 (name "Dana Okafor") → P3 (the preview: sections by stage, the questions) →
   *Generate Dana's link* → P4 → copy the URL. Repeat for Wei Zhang and, for *Someone who runs a
   payroll team*, Marcus Webb. The toggle now shows; *Who's been asked* lists three rows *Not
   opened*.
6. **The participants** (§2.1–§2.3). In three isolated browser contexts, open each link: the
   four honest lines and consent by starting; answer with the script's evidence-bearing answers
   (the harness types the participant's words from a fixture that mirrors the script's INTERPRET
   evidence); skip one question; submit → thanks. The founder's table now reads *Answered · See
   Dana's answers*; open P9 and read Dana's words verbatim; close.
7. **The reading** (§1.6). *Have your agent read the 3 new answers* → P6 (progress, per-row
   *Reading…*) → P7 → the toast names what moved → *See the overview* → the three cards read
   *People disagree* / *Holding up* / *Not holding up* with their counts (§1.7).
8. **The evidence** (§1.7). Open the problem card → E1 (a belief opened: counted for / against /
   said-but-didn't-count with reasons); the price card → E3 (*Not holding up*, "more people of
   this kind can still change it", no conversation beneath).
9. **The brief** (§1.10). Nav *Brief* → B1: every belief of every approved card in exactly one of
   the four lists, counts in people, *Download the brief* present; `page.emulate_media("print")`
   → B2's document renders with *Who was asked*.

Every step is recorded; every screen visited is screenshotted; every assertion enforcing a moment
cites it (`§n.m`).

**Independent Test**: `make eval K=s001` from a cold `make up` → passes → `runs/<id>/` holds
`transcript.jsonl`, screenshots for every frame lettered above, `facts.json`, `scorecard.json`,
`verdict.json` with a score, `report.html`, and `versions.json` naming keel-e2e-eval, keel-cloud,
keel-web, keel-runtime, keel-connect-skill at their HEADs.

**Acceptance Scenarios**:

1. **Given** the runtime is started through the skill script, **When** the browser approves the
   code, **Then** within 30 s `/v2/me` reads `agent.connected: true` and the page reads *Agent
   connected*.
2. **Given** the scripted `NEEDS_INPUT` on the problem, **When** the founder answers, **Then** the
   next interaction turn completes with the statement and C5 shows it verbatim.
3. **Given** *Save this* then the beliefs, **When** the project is read directly (`GET …/overview`),
   **Then** PROBLEM is still **unframed** until *These are right — approve*, and framed +
   approved afterwards (the draft model, keel-cloud spec 023 §4.6 — asserted on the wire, not
   only on the screen).
4. **Given** three answers read, **When** the standing is read (`GET …/standing`), **Then** every
   applying belief appears exactly once across the four lists, and each `line` equals the same
   belief's `countsNote` on its stage card.
5. **Given** the run, **When** scored, **Then** every CLARITY check over every visited screen
   passes (no enum token, no retired string, no gendered pronoun for a participant), and the
   score is reported under policy v6.

---

### User Story 3 - The ledger is enforced against the one scenario (Priority: P2)

`tests/test_journey_coverage.py` reads `canon/CANON.md` (new path) and checks every moment is
proven by S-001 or waived in §5 with a reason.

**Acceptance Scenarios**:

1. **Given** the ledger as amended (every proven row names S-001 only), **When** the stackless
   tests run, **Then** every cited `§n.m` appears in `evals/test_s001_smoke.py`.
2. **Given** §1.3, §1.8, §1.9 (deferred by the founder) and §2.4 (the dead-link page, not on
   the smoke's path), **When** checked, **Then** each is WAIVED with an entry in §5.

### Edge Cases

- **Prism is not in this stack.** The referee only ever talks to the real applications.
- **The runtime must be started by the skill script, not by the harness calling `python3 -m
  keel_runtime` itself** — the skill is one of the four applications under referee. Its
  `authorization_pending_timeout` (the script's own bounded wait) is a stack failure, recorded.
- **The runtime is a child the stack owns**: the script launches it detached, so `stack/runtime.py`
  reads the heartbeat file's `pid` (`status` subcommand) and kills it on `make down`.
- **Clean per run**: the runtime home is wiped at `make up`, so no credential from a prior run
  makes the landing read *Agent connected* before the smoke has connected (the smoke asserts L2
  first).
- **The scripted executor answers per screen in order** across the whole run; the smoke's own
  sequence (problem, solution, commercial, three interprets) must match the script's order —
  the fixture that drives the participants' typed answers lives here and mirrors the script.
- **Polling**: the walk's screens poll the interaction; the harness waits on the screen (the
  frame's own words), with a 60 s ceiling per agent turn, never on sleeps.
- **The toast is app-level**: assert it on the People page and again after *See the overview*.
- **Fonts**: the stack's browser waits for `document.fonts.ready` before any screenshot, as
  keel-web's own visual tests do.

## Requirements

### Stack

- **FR-001** `stack.toml`: `[paths]` gains `keel_runtime = "../keel-runtime"` and
  `keel_connect_skill = "../keel-connect-skill"`; `keel_skill` is removed. `[ports]` unchanged.
- **FR-002** `stack/cloud.py`: also sets `KEEL_V2_CONNECT_VERIFICATION_URI=http://localhost:<web>/connect`
  and `KEEL_V2_FOUNDER_BASE_URL=http://localhost:<web>/p` (unchanged). The MCP/relay overrides
  are removed with their comments (the relay presence threshold override goes — nothing here
  reads presence any more).
- **FR-003** `stack/runtime.py` (new): `home_dir(config)` under `runs/.stack/keel-home/`; `reset()`
  at `make up`; `status(config)` shelling `python3 -m keel_runtime status --home …`; `kill(config)`
  from the heartbeat's `pid`; the `runtime-home` gate.
- **FR-004** `stack/lifecycle.py`: the four gates; `teardown` kills the runtime first.
- **FR-005** `stack/auth.py`: `ensure_founder_account` uses the new `SetupResponse`/`LoginResponse`
  (no `agentKey`; stores nothing but email/password); a `login_and_keel_session` helper that
  returns `keelSessionId`/`boundAgentSessionId` for assertions.

### Harness

- **FR-006** Delete `harness/driver.py`, `mcp_client.py`, `bridge.py`, `relay.py`,
  `founder_sim.py`, `agent_session.py`, `shaping_scoring.py`, and their tests; delete
  `evals/test_s002…s011*.py`, `test_shaping_gauntlet.py`, `evals/recipes.py`,
  `evals/scenario.py` (the smoke is one file with its own fixture module,
  `evals/payroll_exceptions.py`, holding the names, statements, answers — mirrored from the
  runtime's script).
- **FR-007** `harness/connect.py` (new): `start_runtime_via_skill(config, recorder) ->
  {user_code, verification_uri}` running the skill script exactly as spec US2 step 1 shows, with
  the JSON contract of `keel-connect-skill/specs/001-keel-connect-check/contracts/skill-script-output.md`.
- **FR-008** `harness/browser.py`: page objects rewritten to the round-5 screens, selectors from
  keel-web's built DOM (the same ones keel-web's `tests/visual/states/*.ts` drive): `Auth`
  (setup/login), `Connect` (B/C/G), `Landing` (L1–L4), `Shell` (agent line, nav rows with status
  words), `Chat` (C1–C8: bubbles, composer, confirmation card), `StageCard` (R1/R2/R4, E1–E3),
  `People` (P1–P9: toggle, role cards, popup steps, table rows by person, answers popup,
  progress line, toast), `Brief` (B1/B2), `ParticipantBrowser` (unchanged in role, updated
  selectors). Every method records a step and screenshots on entry.
- **FR-009** `harness/interactions.py`: the interaction kinds become `ui_visit`, `agent_turn`
  (an inference job observed through the screen — the frame's state line), `participant_visit`,
  `arrival`; the agent-cycle/handoff/refusal kinds are removed.

### Scoring — policy v6

- **FR-010** `evals/policy.py` → `POLICY_VERSION = 6`: remove the agent-cycle, handoff and
  refusal checks (ORI-A*, GUI-A*, CLA-A2, ORI-H1, GUI-H1, ORI-R1, GUI-R1); keep the UI-visit
  checks (ORI-U*, GUI-U*, CLA-U*) and the arrival check; add **CLA-U4** (no retired string:
  *Conversation history*, *Tell your Keel agent*, *Something's off*, *Ruled out*, *This isn't
  working*, *Recorded*, *Not what I meant*) and **CLA-U5** (no gendered pronoun in an element
  that renders a participant name), and **GUI-U3** (every waiting state names what is waited for:
  the wait box/typing indicator carries a sentence). `CLARITY_TOKENS` gains
  `AWAITING_CONFIRMATION`, `ACCEPTED`, `PENDING`, `RUNNING`, `DONE`, `EXPIRED`. Category weights
  renormalised; documented in the module's judgement-calls block as v6.
- **FR-011** `harness/rubric.py`: the corresponding check functions; `tests/test_policy_v6.py`
  replaces `test_policy_v5.py`.

### Evidence

- **FR-012** `harness/evidence.py`: `REPO_LABELS = ["keel-e2e-eval", "keel-cloud", "keel-web",
  "keel-runtime", "keel-connect-skill"]`; `versions.json` records each HEAD; the report's
  interaction cards render the new kinds.

### The one scenario

- **FR-013** `evals/test_s001_smoke.py`: US2 steps 1–9 as one test with the `§` citations for
  §1.0, §1.1, §1.2, §1.4, §1.5, §1.6, §1.7, §1.10, §2.1, §2.2, §2.3 in its module docstring and
  beside each assertion; the wire-level assertions of US2 scenarios 3 and 4 made with
  `requests` against the cloud using the founder session cookie.

### Ledger

- **FR-014** keel-cloud `canon/CANON.md` §4: every proven row names **S-001** only; §1.3, §1.8,
  §1.9, §2.4 are WAIVED with §5 entries (the first three "deferred by the founder,
  screen-review-design §5.5/§8.5"; §2.4 "not on the smoke's path; the participant page is
  unchanged this round"). The existing §5 waivers for flow 1 and the derived brief are **closed**
  (S-001 now proves them). `tests/test_journey_coverage.py` reads `canon/CANON.md`. *(This edit
  to keel-cloud is made by the founder's session alongside this spec, not by the referee — the
  referee never edits the product repos.)*

### Docs

- **FR-015** `AGENTS.md`, `README.md`: the four applications, the new gates, `make up / eval /
  down`, the rule that the runtime is started through the skill; `specs/005-connect-stack/
  quickstart.md`. `runs/DRIFT.md` gains the dated retirement note.

## Success Criteria

- **SC-001** `make unit` green (stackless: config, steps, evidence, report, policy v6, journey
  coverage against the amended ledger).
- **SC-002** `make up && make eval K=s001 && make down` green on this machine from cold, under
  ten minutes wall clock, zero LLM calls.
- **SC-003** The run bundle's screenshots include one per lettered frame named in US2; the
  report opens and shows the score.
- **SC-004** `test_journey_coverage.py` passes against the amended ledger; no moment is silent.

## Judgement calls

1. **One scenario, not a trimmed set.** The founder asked for one; the old set proved a protocol
   that no longer exists. The scoring layer's *scenario* diversity is gone, so the score's
   comparability is only run-to-run for S-001 — acceptable for a smoke that gates.
2. **The skill script starts the runtime.** The alternative — the harness launching `python3 -m
   keel_runtime connect` itself — would leave the connect skill un-refereed, and it is one of the
   four applications the founder named.
3. **The participants' typed answers live in this repo, mirroring the runtime's script.** The
   runtime's INTERPRET entries decide the verdicts regardless of what the participants typed
   (the executor is scripted); the typed answers exist so P9 shows real words and the
   participant page is genuinely exercised. Both fixtures name the same three people and the
   same claims so the run reads true.
4. **Wire assertions beside screen assertions** for the draft model and the standing (US2
   scenarios 3, 4): the screen can be right for the wrong reason; the referee checks the
   aggregate too.

## Assumptions

- keel-runtime spec 001 (the scripted executor) lands first; this feature pins to its HEAD.
- keel-cloud `master` at `7ee395b` or later; keel-web `master` at `89338b9` or later.
- One founder account per stack lifetime, as today.
