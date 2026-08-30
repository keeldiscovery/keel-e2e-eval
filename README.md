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
make eval K=s001    # runs one scenario by slug substring (matches evals/test_s001_smoke.py, etc.)
make eval-all       # runs the FULL set (s001-s007) in one stack session, writes runs/INDEX-*.html
make down           # tears everything down; idempotent, safe even half-up
```

`make eval`/`make eval-all` alone (no `make up` first) attach to an already-up stack if one is
answering on all three ports, or boot one and tear it down at the end of the session -- the
fast-iteration path from `make up && make eval` and the from-cold path are the same command.

`runs/INDEX-<stamp>.html` (written by `make eval-all`) lists every run bundle from that
invocation: scenario slug, verdict, run score, a bar per category (an `N/A` bar, not a bare 0,
for a category no interaction in that run could ever carry -- S-007's no-browser scorecard is the
motivating case), and a link to that bundle's own `report.html`.

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
- Why the scenario was, or was not, adapted around it (a legitimate alternate path is fine to
  take; a contortion that stops testing what the scenario is for is not).
- The shape of a fix, explicitly **not applied** -- this repo diagnoses, the product repo fixes.

## The eval set

Seven scenarios ship today (`specs/eval-set-design.md`, feature 003), each its own fresh project
(never shared state -- `evals/recipes.py` shares *code*, not data, between S-002/S-003):

| Scenario | File | Journey | What it walks |
|---|---|---|---|
| S-001 | `evals/test_s001_smoke.py` | -- | The sunny-day discovery: every party, every handoff, every screen, one supportive interview per stage. |
| S-002 | `evals/test_s002_pricing_pivot.py` | §1.7-1.9, §2.4 | A ruled-out pricing deal-breaker, a `FRAME` replacement carrying only the surviving belief, the old claim struck through but readable, problem/solution untouched, a stale pre-pivot link, an already-answered participant never told their work was wasted. |
| S-003 | `evals/test_s003_going_ahead.py` | §1.10 | The founder asks for the brief while a deal-breaker is still disproved -- and documents, live, that the shipped protocol has no path to `PROCEED_TO_BRIEF` in that state at all (`runs/DRIFT.md` #7). |
| S-004 | `evals/test_s004_divided_person.py` | §1.7 | One person with concrete evidence on both sides of one belief -- counted under both headings, people not quotes. |
| S-005 | `evals/test_s005_opinions.py` | §1.7, §2.2 | Opinions move nothing (`STATED_PREFERENCE` never counts); an all-skipped submission is refused gently, not with a raw error. |
| S-006 | `evals/test_s006_consent_decline.py` | §2.1-2.3 | A graceful, never-shamed decline; the consent screen's exactly-four things; a thank-you that promises nothing extra. |
| S-007 | `evals/test_s007_hostile_wire.py` | protocol negatives | No browser: an unknown MCP screen, an ungranted context handle, a schema fault the token survives, a stale token after its own unacknowledged commit -- each scored as its own `agent-refusal` interaction (`GUI-R1`/`ORI-R1`: is the remedy present, actionable, and not just the problem restated?). |

Adding another is a new `evals/test_*.py` module plus a `Scenario` (payload builders, answer
table, about-line, fact registry) per `evals/scenario.py` -- `evals/recipes.py` is the place to
share a setup shape (never state) across more than one scenario.

### Policy v2

`evals/policy.py`'s `POLICY_VERSION` is `2`: `CLA-A1`/`GUI-A2` (the raw-enum/field-name sweep)
apply only to a handoff's `display` now -- the one protocol text a founder actually receives.
`instruction.content` and `requirements` are agent-facing method/payload guidance (confirmed by
re-reading the shipped `ActionSchemas`/`InstructionRegistry`) and are no longer vocabulary-swept;
`GUI-A1`'s presence/sentence-shape check on `requirements` is untouched. This is a recalibration,
not a loosened bar -- a seeded raw enum in a handoff `display` still fails both checks
(`tests/test_policy_v2.py`), and the twenty S-001 failures policy v1 raised against
`instruction`/`requirements` were mismeasurement, re-adjudicated in `runs/DRIFT.md` #4 and
recorded as a dated amendment in `specs/eval-scoring-design.md` §3.

## Stackless unit tests

```bash
make unit
```

Runs `tests/` -- pure-logic tests for the step recorder, the interaction/rubric/scoring pipeline
(including seeded-loss fixtures: a truncated statement, a leaked enum, an empty handoff display,
each failing exactly the check design says should catch it), the report generator, and the config
loader, with no Docker/gradle/vite involved.
