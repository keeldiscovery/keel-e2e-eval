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
                    # a scenario starts it, because starting it is part of the journey.
make eval K=s001    # runs the smoke (matches evals/test_s001_smoke.py); prints the run directory
make eval K=s002    # runs the agent-optional day (evals/test_s002_agent_optional.py) -- reuses
                    # an S-001 run's own project in the same session, or builds its own prelude
make down           # kills a runtime a scenario left running, then everything else; idempotent
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

## The instruction eval (`make instruction-eval`)

The second of this repo's two model-backed exceptions (the other is S-004). It answers a question
none of the browser scenarios can: **does keel-cloud's inference-instruction prose, sent to a real
model exactly as production sends it, produce the measured beliefs the golden corpus says it
should?**

```bash
make instruction-eval DRY=1 K=01-countly   # prints every prompt it would send; calls nothing
make instruction-eval BASELINE=1           # the before-picture, taken once
make instruction-eval K=reading N=1        # one subject, one run per case
```

- **No stack, and no `make up`.** It talks to no service. It shells keel-cloud's own
  `screenContracts` task for the response contracts and for the aggregate's verdict, imports
  keel-runtime's own `build_prompt` and `ClaudeCodeExecutor`, and reads the frozen corpus at
  `keel-cloud/canon/designs/measured-beliefs/corpus/` — hashed on the way in and checked again at
  the end, because the one thing that must never happen to a golden set is that it quietly moved to
  make a run green.
- **It costs real money**, on the founder's own account: about 124 calls a pass at N=1, and the
  baseline of 2026-09-06 cost **$11.88** in 54 minutes. Start with `DRY=1` and read a prompt.
- **It is a dependency of nothing** — not `eval`, not `eval-all`, not `eval-live` — and no pytest
  run collects `instructions/`.
- **Its rubric is versioned separately.** `instructions/marks.py`'s `MARKS_VERSION` is to this eval
  what `POLICY_VERSION` is to `evals/policy.py`, and deliberately a different constant. Changing a
  mark, a metric definition, an alignment rule or a judgement call bumps it; scores under different
  versions describe different rubrics and are not comparable. A finished run can be re-scored from
  its own bundle without spending again: `python -m instructions.rescore runs/<id>`, which writes
  `scorecard-v<N>.json` beside the original rather than over it.
- **The three marks**: anchoring accuracy ≥ 90 %, golden-belief recall ≥ 80 %, rule refusals = 0.
  An **unmeasured** mark fails; it is not met.
- **The model is not pinned.** keel-runtime sends no `--model` and this repo does not add one. The
  model is named in the report header, and the marks are comparable only within it.

### `register.html` carries no number, on purpose

Every run also writes `register.html`: every produced anchor prompt and option list, grouped by
market, with the corpus's own beside it — and **no score, no tick, no cross**. Whether an anchor
sounds like a supply yard in Texas or a builder's merchant in London cannot be checked by code
(design §3.8), and design §10 step 4 says what is done instead: a person who knows that market
reads it, and **their reading is recorded with the run**. Whether an option list *leads* — the most
expensive authoring mistake in the design — is the other thing that page is for and the other thing
nothing scores. A metric for either would look like evidence and would in fact be similarity to one
hand-written example.

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

## The two scenarios

`evals/test_s001_smoke.py` walks keel-cloud `canon/journeys.md` §3 (2026-09-03's connect-stack
amendment) end to end, once, deterministically: arrival and device-code connect, naming the
project, the problem/solution/commercial frame-and-review cycle (including one scripted
`NEEDS_INPUT` follow-up), inviting and interviewing three participants (Dana Okafor, Wei Zhang,
Marcus Webb — `evals/payroll_exceptions.py`), reading their answers, the resulting standing
(*People disagree* / *Holding up* / *Not holding up*), the evidence drill-down, and the brief
(screen plus its print view). Every assertion enforcing a journey moment cites it (`§n.m`);
`tests/test_journey_coverage.py` checks that against keel-cloud `canon/CANON.md`'s own ledger.

`evals/test_s002_agent_optional.py` (spec `006-agent-optional`) is "the agent-optional day": a
founder connects a runtime, builds up a project (through S-001's own history in the same stack
session, or its own prelude, `evals/preludes.approved_project_with_one_read`, from cold), logs
out, stops the runtime, and logs back in. It proves that *creating* a project or *reading* an
answer are the only two things a live agent gates — everything else (opening an approved card,
inviting someone, generating a real link, downloading and printing the brief) keeps working with
no agent at all, with three direct wire assertions beside the screen (`POST /v2/projects` → 422
`rule: "agent"`; `POST .../invitations` → 201; `GET .../standing` → 200). It also proves the
reconnect: approving a fresh device code (or, when the runtime's own stored credential is still
valid and reconnects silently, logging back in again — `runs/DRIFT.md` #19) brings the agent line
back, and using the read action once reconnected moves the card. As written and run against the
live stack, US1 acceptance scenario 3 (the read action disabled with a reason when no agent) fails
— the product offers the action anyway, refuses it only on the wire, and shows nothing on the
screen (`runs/DRIFT.md` #17); this is `specs/006-agent-optional/spec.md`'s own stated prediction,
confirmed, not an assumption the scenario was written to avoid finding.

The old S-002…S-011 (an eleven-scenario set against a since-retired agent-protocol/relay stack,
unrelated to the current S-002 above) are gone — recorded in git history and in `runs/DRIFT.md`'s
2026-09-03 retirement note, not lost.

## Stackless unit tests

```bash
make unit
```

Runs `tests/` — pure-logic tests for the step recorder, the interaction/rubric/scoring pipeline
(including seeded-loss fixtures: a truncated statement, a leaked enum, a retired string, a
gendered pronoun, a wordless waiting state — each failing exactly the check design says should
catch it), the report generator, the config loader, and the ledger-coverage test, with no
Docker/gradle/vite involved.

## The live run (`make eval-live`)

S-004, *the stranger who gives orders* (`specs/008-stranger-who-gives-orders`), is the one
scenario that runs a **real `claude`** -- it attacks the framing box and a participant's answers
with instructions and checks that the founder's agent only ever answers. It costs real money
(roughly ten jobs at a few cents each; the run prints the sum from the runtime's own envelopes)
and needs a logged-in Claude Code CLI on `PATH`, so it is **opt-in**:

```
make up PROFILE=playground
make eval K=s001 PROFILE=playground      # the approved project it attacks
make eval-live K=s004 PROFILE=playground
make down PROFILE=playground
```

`make eval` and `make eval-all` deselect it (`-m "not live"`). Without a usable `claude` it is
skipped with the reason printed, never silently passed. It leaves two small projects of its own on
the stack; run a fresh `make up` before any scripted scenario after it.
