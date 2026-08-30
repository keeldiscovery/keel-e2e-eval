# keel-e2e-eval

The fourth Keel repo. It owns no product code: it stands up `keel-cloud` + `keel-web` locally
against a Docker Postgres, drives a scripted founder-agent over the real HTTP agent protocol,
executes every handoff in a real browser (founder + an isolated participant context), and leaves
a reviewable, **scored** evidence bundle per run -- every founder-agent cycle, handoff, screen
visit, and participant page is checked against a versioned policy on four attributes
(ORIENTATION, GUIDANCE, FIDELITY, CLARITY) and the run gets an X/5. See
`specs/e2e-eval-design.md` (feature 001, the harness) and `specs/eval-scoring-design.md`
(feature 002, the scoring layer) for the designs of record, and `specs/001-e2e-eval-harness/` /
`specs/002-eval-scoring/` for the specs/plans/contracts each build follows.

## Prerequisites

- Sibling checkouts at `../keel-cloud`, `../keel-web`, `../keel-skill` (paths configurable in
  `stack.toml`).
- Docker (Colima on macOS) running.
- JDK 21 (`JAVA_HOME` pointed at it) and Node 20+.
- `make` will create its own `.venv` and install `pytest`, `playwright`, `requests`, plus the
  Chromium browser -- nothing to install by hand.
- `stack/cloud.py` boots keel-cloud with `SPRING_AI_MCP_SERVER_PROTOCOL=STREAMABLE` -- a same-
  binary environment override, not a keel-cloud code change -- because `spring-ai-bom 2.0.1`'s
  actual default (`SSE`, mounted at `/sse`) doesn't match what keel-cloud's own `SecurityConfig`
  permits (`/mcp`). See `runs/DRIFT.md` #3.

## Run

```bash
make up            # boots Postgres (55432), keel-cloud (18080), keel-web (5173); prints each gate
make eval K=s001    # runs the smoke scenario; prints the run directory
make down           # tears everything down; idempotent, safe even half-up
```

`make eval` alone (no `make up` first) attaches to an already-up stack if one is answering on all
three ports, or boots one itself and tears it down at the end of the session -- the fast-iteration
path from `make up && make eval` and the from-cold path are the same command.

## Review a run

Open `runs/<timestamp>-<scenario>/report.html` in a browser: a header with the verdict, the four
repos' pinned commits (dirty-flagged), and every step in order -- founder-agent wire calls with
collapsible request/response JSON, every founder and participant browser screen as a screenshot,
and assertions with expected/actual. A failed run still produces this report, with the failing
step anchored at the top and linked to the page HTML and console log captured at the moment of
failure.

To rebuild `report.html` from an existing run's `transcript.jsonl` alone (e.g. after changing the
report template):

```bash
make report RUN=runs/20260829T210000Z-s001-smoke
```

## Scored runs

Every run also gets a scorecard (`specs/eval-scoring-design.md`): steps get tagged into
**interactions** (one founder-agent cycle, one handoff, one screen visit, one participant survey),
each interaction is checked against `evals/policy.py`'s versioned rubric, and the checks roll up
into four category scores and one run score out of 5. `report.html`'s header shows the big X/5,
a bar per category, the policy version, and a gated badge if the run didn't finish; below that,
one card per interaction (a conversation card for the agent surface, screenshots for the browser
surface, failed/waived checks called out inline); a scorecard matrix sits at the bottom.

`scorecard.json` sits beside `transcript.jsonl`/`verdict.json` in the run bundle, and
`verdict.json` gains `score` + `policy_version`. `make report RUN=<dir>` **re-runs scoring**, not
just rendering, straight from the bundle (`transcript.jsonl` + `facts.json`) -- so re-scoring an
old run under a newer policy is just:

```bash
make report RUN=runs/20260829T210000Z-s001-smoke
```

`transcript.jsonl` and `screenshots/` are never touched by this; only `scorecard.json` and
`verdict.json`'s score/policy fields are rewritten. An interrupted run (the workflow never
finished) still gets scored on whatever it saw -- category scores describe what was observed, but
the run score is capped at 2/5 and the report shows a "GATED" badge.

**Changing the policy** (`evals/policy.py`): any change to a check's condition, a weight, a
category weight, the clarity token list, normalization, or a waiver is a policy change -- bump
`POLICY_VERSION` when you make one, because scores under different policy versions describe
different rubrics and aren't comparable. The bumped version shows up in every newly-scored
bundle's `scorecard.json`/`verdict.json` (including old bundles re-scored via `make report`).

A scenario declares what it wants FIDELITY to trace via `Scenario.facts()` (`evals/scenario.py`):
one entry per founder- or participant-entered text, naming which of the six hops
(`agent_echo`, `stage_screen`, `invite_screen`, `participant_page`, `interpret_context`, `brief`)
it should reach verbatim, and which it legitimately never reaches (`absent_hops`, documented
rather than silently omitted).

## Prove the failure path

`make eval`'s attach-or-boot fixture heals a half-up stack at session start (it checks each of
Postgres/keel-cloud/keel-web independently and only restarts what's actually down) -- so killing
keel-web *before* `make eval` starts just gets it quietly restarted before the scenario runs.
To see a genuine mid-run failure, kill it *while a run is already in flight*:

```bash
make up
make eval K=s001 &          # start a run in the background
sleep 1 && kill -TERM -$(cat runs/.stack/web.pid)   # kill keel-web partway through
```

S-001 fails at whichever browser step was in flight (verified: `founder.open_stage`, with
`net::ERR_CONNECTION_REFUSED`), `failure/page.html` and `failure/console.log` are captured, and
`report.html` is still generated. `tests/test_browser_failure_capture.py` covers the same
failure-capture path automatically (a closed port standing in for a dead keel-web), with no stack
required.

## Ports (fixed, never 5432/8080)

Postgres 55432, keel-cloud 18080, keel-web 5173 -- so this stack never collides with a
developer's own Postgres or dev server. `make up` fails fast, naming the port and its owner, if
any of the three is already taken.

## Scope and boundaries

This repo **reports** drift and bugs in the product repos (`keel-cloud`, `keel-web`,
`keel-skill`) -- it never fixes them. When a run surfaces a genuine cross-repo bug (not a config
problem in this repo), the run's evidence bundle captures it and `runs/DRIFT.md` gets an entry.
See `runs/DRIFT.md` if one exists in this checkout for the current findings.

**DRIFT.md entry format** -- one `##` section per finding:
- **Severity**: blocking (a scenario cannot legitimately work around it) or non-blocking (worked
  around, and how).
- **Where**: repo, file, function/line.
- The offending source excerpt, quoted.
- **Reproduction**: exact `curl`/steps, and the `runs/<id>/` bundle(s) that demonstrate it (page
  HTML, server log excerpt, transcript `DRIFT:` notes -- whatever is closest to the metal).
- Why S-001 was, or was not, adapted around it (a legitimate alternate path is fine to take; a
  contortion that stops testing what the scenario is for is not).
- The shape of a fix, explicitly **not applied** -- this repo diagnoses, the product repo fixes.

Only one scenario ships today: **S-001**, the smoke (`evals/test_s001_smoke.py`). The
positive/negative catalog beyond it (contradicted load-bearing warning, stale-link reframe,
concurrency, all-skipped submission, unknown screen, ...) is chosen with the user later; adding
one is a new `evals/test_*.py` module plus a `Scenario` (payload builders, answer table,
about-line) per `evals/scenario.py`.

## Stackless unit tests

```bash
make unit
```

Runs `tests/` -- pure-logic tests for the step recorder, the interaction/rubric/scoring pipeline
(including seeded-loss fixtures: a truncated statement, a leaked enum, an empty handoff display,
each failing exactly the check design says should catch it), the report generator, and the config
loader, with no Docker/gradle/vite involved.
