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
one entry per founder- or participant-entered text, naming which of the seven hops
(`agent_echo`, `stage_screen`, `invite_screen`, `participant_page`, `interpret_context`, `brief`,
`recorded` -- policy v3's addition) it should reach verbatim, and which it legitimately never
reaches (`absent_hops`, documented
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

Eight scenarios ship today (`specs/eval-set-design.md`, feature 003; S-008 added for the founder-
experience design's item-7 blind spot), each its own fresh project (never shared state --
`evals/recipes.py` shares *code*, not data, across scenarios):

| Scenario | File | Journey | What it walks |
|---|---|---|---|
| S-001 | `evals/test_s001_smoke.py` | -- | The sunny-day discovery: every party, every handoff, every screen -- all three cards approved before any invite (the invite gate), one combined interview settling all three beliefs, and a live proof that a commit's own `display` sentence carries a door the browser actually opens. |
| S-002 | `evals/test_s002_pricing_pivot.py` | §1.7-1.9, §2.4 | A ruled-out pricing deal-breaker, a `FRAME` replacement carrying only the surviving belief, the old claim struck through but readable, problem/solution untouched, a stale pre-pivot link, an already-answered participant never told their work was wasted. |
| S-003 | `evals/test_s003_going_ahead.py` | §1.10 | The founder asks for the brief while a deal-breaker is still disproved -- and documents, live, that the shipped protocol has no path to `PROCEED_TO_BRIEF` in that state at all (`runs/DRIFT.md` #7). |
| S-004 | `evals/test_s004_divided_person.py` | §1.7 | One person with concrete evidence on both sides of one belief -- counted under both headings, people not quotes. |
| S-005 | `evals/test_s005_opinions.py` | §1.7, §2.2 | Opinions move nothing (`STATED_PREFERENCE` never counts); an all-skipped submission is refused gently, not with a raw error. |
| S-006 | `evals/test_s006_consent_decline.py` | §2.1-2.3 | A graceful, never-shamed decline; the consent screen's exactly-four things; a thank-you that promises nothing extra. |
| S-007 | `evals/test_s007_hostile_wire.py` | protocol negatives | No browser: an unknown MCP screen, an ungranted context handle, a schema fault the token survives, a stale token after its own unacknowledged commit -- each scored as its own `agent-refusal` interaction (`GUI-R1`/`ORI-R1`: is the remedy present, actionable, and not just the problem restated?). |
| S-008 | `evals/test_s008_wrong_moment.py` | item 7 (feedback-2026-08-30.md) | Wrong-moment visits: a stage before it's framed, People before any role exists, the brief long before `READY_TO_BUILD` -- each a founder-worded quiet state, never the wire's raw refusal shape. |

Adding another is a new `evals/test_*.py` module plus a `Scenario` (payload builders, answer
table, about-line, fact registry) per `evals/scenario.py` -- `evals/recipes.py` is the place to
share a setup shape (never state) across more than one scenario.

### The invite gate (founder-experience design §6; keel-cloud commits 8b13d04/ff1ed48)

`Project.needs` no longer offers `INVITE`/`EVIDENCE` for any stage until every framed stage is
approved. Every scenario above that used to interleave "approve this stage, invite for it" now
approves all three first (`evals/recipes.advance_to_all_stages_approved`, or the same choreography
inlined in `evals/recipes.rule_out_pricing`) -- and `evals.recipes.assert_invite_gate_closed` is
the standing assertion (run after each of the first two approvals): no stage reports `INVITE` and
no role reads as invitable while any framed stage still awaits approval. A single-stage scenario
(S-004/S-005/S-006) that never actually cares about SOLUTION/COMMERCIAL still has to get them
approved to open the gate -- `evals.recipes.filler_role_payload`/`filler_assumption_payload` is
that judgement call: a placeholder belief on a role nobody ever invites, so `approve()` has
something to require without ever touching the scenario's own single-question interview. One
consequence worth naming: a scenario using one role across multiple stages (S-001) now gets one
combined invitation once the gate opens, not one per stage -- `Project.invite`/`linkFor` freezes
every open belief for a role into the *first* invitation sent to it.

### Policy v3

`evals/policy.py`'s `POLICY_VERSION` is `3` (founder-experience design; keel-cloud commits
8b13d04/ff1ed48 gave the wire a founder voice on every commit, not only a handoff):

- **`recorded` playback fidelity** -- a seventh FID hop. A scenario's fact registry can now
  declare `hops=["recorded", ...]`: the fact must appear verbatim in the agent-cycle's own
  captured `SubmitResponse.recorded` JSON (`harness/driver.py`'s `_capture_commit_voice`).
- **`ORI-A3`/`GUI-A3`/`CLA-A2`** -- a commit's own `display` (not only a handoff's) is checked for
  presence, actionability, a well-formed door (any URL it names must be `http(s)://`), and the
  same raw-enum/field-name sweep `CLA-A1` already ran on a handoff. The literal click-through on a
  door a `display` carries is `FounderBrowser.follow_display_url` -- a scenario assertion, not a
  transcript-only check -- demonstrated in `test_s001_smoke.py`.
- **`CLA-U3`** -- `verdictLabel`/`needLabel`, read off a ui-visit's own captured `state` snapshot:
  present and enum-clean once a stage is `approved` (`verdictLabel`) or has a `need` other than
  `EVIDENCE` (`needLabel` -- `FounderVoice.needLabel` deliberately returns `null` there).

This is additive, not a loosened bar -- `tests/test_policy_v3.py` seeds a failure for each new
check and a clean control that passes it, the same construction-not-assertion method
`tests/test_policy_v2.py` (its v2 fixtures, kept, are in the same file now) used to prove v2's own
recalibration.

## Stackless unit tests

```bash
make unit
```

Runs `tests/` -- pure-logic tests for the step recorder, the interaction/rubric/scoring pipeline
(including seeded-loss fixtures: a truncated statement, a leaked enum, an empty handoff display,
each failing exactly the check design says should catch it), the report generator, and the config
loader, with no Docker/gradle/vite involved.
