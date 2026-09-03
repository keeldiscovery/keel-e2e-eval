# keel-e2e-eval

The referee. It owns no product code: it stands up `keel-cloud` + `keel-web` + `keel-runtime`
locally against a Docker Postgres, starts the runtime the way a founder does — through
`keel-connect-skill`'s own script, device code and all — drives the whole payroll-exceptions
discovery in a real browser (founder session, plus three isolated participant contexts), and
leaves a reviewable, **scored** evidence bundle per run: every screen visit, agent turn, and
participant survey is checked against a versioned policy on four attributes (ORIENTATION,
GUIDANCE, FIDELITY, CLARITY) and the run gets an X/5.

No Prism, no LLM, anywhere in this stack — keel-runtime answers every inference job from its own
bundled, deterministic script (`--executor scripted`). See `specs/e2e-eval-design.md` (feature
001) and `specs/eval-scoring-design.md` (feature 002) for the original harness/scoring designs of
record, and `specs/005-connect-stack/` for the spec this rewrite follows.

## Prerequisites

- Sibling checkouts at `../keel-cloud`, `../keel-web`, `../keel-runtime`, `../keel-connect-skill`
  (paths configurable in `stack.toml`).
- Docker (Colima on macOS) running.
- JDK 21 (`JAVA_HOME` pointed at it, per keel-cloud's own AGENTS.md) and Node 20+.
- `make` will create its own `.venv` and install `pytest`, `playwright`, `requests`, plus the
  Chromium browser — nothing to install by hand.

## Run

```bash
make up            # boots Postgres (55432), keel-cloud (18080), keel-web (5173); resets the
                    # runtime home; prints four gates. The runtime itself is NOT started here --
                    # the one scenario starts it, because starting it is part of the journey.
make eval K=s001    # runs the smoke (matches evals/test_s001_smoke.py); prints the run directory
make down           # kills a runtime the smoke left running, then everything else; idempotent
```

`make eval` alone (no `make up` first) attaches to an already-up stack if one is answering on all
three ports, or boots one and tears it down at the end of the session — the fast-iteration path
from `make up && make eval` and the from-cold path are the same command. Either way, the runtime
home (`runs/.stack/keel-home/`) is only ever reset by `make up`/`boot` itself, never mid-session.

## Review a run

Open `runs/<timestamp>-s001-smoke/report.html` in a browser: a header with the verdict, the five
repos' pinned commits (dirty-flagged), and every step in order — the connect skill's own JSON
output, every founder and participant browser screen as a screenshot, and assertions with
expected/actual. A failed run still produces this report, with the failing step anchored at the
top and linked to the page HTML and console log captured at the moment of failure.

To rebuild `report.html` from an existing run's `transcript.jsonl` alone (e.g. after changing the
report template):

```bash
make report RUN=runs/20260903T120000Z-s001-smoke
```

## Scored runs

Every run also gets a scorecard (`specs/eval-scoring-design.md`): steps get tagged into
**interactions** (`ui_visit`, `agent_turn`, `participant_visit`, `arrival` — spec
`005-connect-stack` FR-009), each interaction is checked against `evals/policy.py`'s versioned
rubric (currently v6), and the checks roll up into four category scores and one run score out of
5. `report.html`'s header shows the big X/5, a bar per category, the policy version, and a gated
badge if the run didn't finish; below that, one card per interaction; a scorecard matrix sits at
the bottom.

`scorecard.json` sits beside `transcript.jsonl`/`verdict.json` in the run bundle, and
`verdict.json` gains `score` + `policy_version`. `make report RUN=<dir>` **re-runs scoring**, not
just rendering, straight from the bundle (`transcript.jsonl` + `facts.json`) — so re-scoring an
old run under a newer policy is just:

```bash
make report RUN=runs/20260903T120000Z-s001-smoke
```

`transcript.jsonl` and `screenshots/` are never touched by this; only `scorecard.json` and
`verdict.json`'s score/policy fields are rewritten. An interrupted run (the workflow never
finished) still gets scored on whatever it saw — category scores describe what was observed, but
the run score is capped at 2/5 and the report shows a "GATED" badge.

**Changing the policy** (`evals/policy.py`): any change to a check's condition, a weight, a
category weight, the clarity token list, normalization, or a waiver is a policy change — bump
`POLICY_VERSION` when you make one, because scores under different policy versions describe
different rubrics and aren't comparable.

`evals/payroll_exceptions.py`'s `facts()` declares what FIDELITY traces: one entry per statement,
role, or participant answer, naming which of the four hops it should reach verbatim
(`stage_screen`, `invite_screen`, `participant_page`, `brief`).

## Prove the failure path

`make eval`'s attach-or-boot fixture heals a half-up stack at session start — so killing keel-web
*before* `make eval` starts just gets it quietly restarted before the scenario runs. To see a
genuine mid-run failure, kill it *while a run is already in flight*:

```bash
make up
make eval K=s001 &          # start a run in the background
sleep 1 && kill -TERM -$(cat runs/.stack/web.pid)   # kill keel-web partway through
```

The report still generates, with the failing step anchored at the top, `failure/page.html` and
`failure/console.log` captured at the moment of failure. `tests/test_browser_failure_capture.py`
covers the same failure-capture path automatically, with no stack required.

## Ports (fixed, never 5432/8080)

Postgres 55432, keel-cloud 18080, keel-web 5173 — so this stack never collides with a
developer's own Postgres or dev server. `make up` fails fast, naming the port and its owner, if
any of the three is already taken. The runtime binds no fixed port of its own; it long-polls
keel-cloud over HTTP the same way it would from a founder's own laptop.

## Split stacks: the playground profile

`make up`/`make down`/`make eval*` all default to the **eval** profile above — unchanged. A
second, entirely separate **playground** profile exists for poking at the product by hand without
ever touching an eval run's own data:

```bash
make up PROFILE=playground    # Postgres 55433, keel-cloud 18081, keel-web 5174
make down PROFILE=playground
```

The two profiles cannot collide: separate ports (`stack.toml`'s `[playground.ports]`), separate
pid files (`cloud-playground`/`web-playground`), and separate Docker Compose *projects*
(`stack/postgres.py` runs the playground under `-p keel-eval-playground`, a real named volume
rather than the eval profile's `tmpfs`) — Compose's project name, not the file, is the isolation
boundary, so both profiles' services can live in one `docker-compose.yml` without `make down`'s
default (`eval`) invocation ever being able to see, let alone drop, the playground's own
container or volume.

## Scope and boundaries

This repo **reports** drift and bugs in the product repos (`keel-cloud`, `keel-web`,
`keel-runtime`, `keel-connect-skill`) — it never fixes them. When a run surfaces a genuine
cross-repo bug (not a config problem in this repo), the run's evidence bundle captures it and
`runs/DRIFT.md` gets an entry. See `runs/DRIFT.md` for the current findings, including the
2026-09-03 retirement note explaining what this rewrite removed and why.

**DRIFT.md entry format** — one `##` section per finding:
- **Severity**: blocking (a scenario cannot legitimately work around it) or non-blocking (worked
  around, and how).
- **Where**: repo, file, function/line.
- The offending source excerpt, quoted.
- **Reproduction**: exact `curl`/steps, and the `runs/<id>/` bundle(s) that demonstrate it.
- Why the scenario was, or was not, adapted around it.
- The shape of a fix, explicitly **not applied** — this repo diagnoses, the product repo fixes.

## The one scenario

`evals/test_s001_smoke.py` walks keel-cloud `canon/journeys.md` §3 (2026-09-03's connect-stack
amendment) end to end, once, deterministically: arrival and device-code connect, naming the
project, the problem/solution/commercial frame-and-review cycle (including one scripted
`NEEDS_INPUT` follow-up), inviting and interviewing three participants (Dana Okafor, Wei Zhang,
Marcus Webb — `evals/payroll_exceptions.py`), reading their answers, the resulting standing
(*People disagree* / *Holding up* / *Not holding up*), the evidence drill-down, and the brief
(screen plus its print view). Every assertion enforcing a journey moment cites it (`§n.m`);
`tests/test_journey_coverage.py` checks that against keel-cloud `canon/CANON.md`'s own ledger.

The old S-002…S-011 (an eleven-scenario set against a since-retired agent-protocol/relay stack)
are gone — recorded in git history and in `runs/DRIFT.md`'s 2026-09-03 retirement note, not lost.

## Stackless unit tests

```bash
make unit
```

Runs `tests/` — pure-logic tests for the step recorder, the interaction/rubric/scoring pipeline
(including seeded-loss fixtures: a truncated statement, a leaked enum, a retired string, a
gendered pronoun, a wordless waiting state — each failing exactly the check design says should
catch it), the report generator, the config loader, and the ledger-coverage test, with no
Docker/gradle/vite involved.
