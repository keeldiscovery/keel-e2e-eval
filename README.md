# keel-e2e-eval

The fourth Keel repo. It owns no product code: it stands up `keel-cloud` + `keel-web` locally
against a Docker Postgres, drives a scripted founder-agent over the real HTTP agent protocol,
executes every handoff in a real browser (founder + an isolated participant context), and leaves
a reviewable evidence bundle per run. See `specs/e2e-eval-design.md` for the design of record and
`specs/001-e2e-eval-harness/` for the spec/plan/contracts this build follows.

## Prerequisites

- Sibling checkouts at `../keel-cloud`, `../keel-web`, `../keel-skill` (paths configurable in
  `stack.toml`).
- Docker (Colima on macOS) running.
- JDK 21 (`JAVA_HOME` pointed at it) and Node 20+.
- `make` will create its own `.venv` and install `pytest`, `playwright`, `requests`, plus the
  Chromium browser -- nothing to install by hand.

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

Runs `tests/` -- pure-logic tests for the step recorder, the report generator, and the config
loader, with no Docker/gradle/vite involved.
