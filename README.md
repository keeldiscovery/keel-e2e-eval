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

**The runtime this stack runs is the one that travelled inside the skill** (spec
`012-bundled-runtime`; keel-cloud `canon/designs/keel-skill-design.md` §3.1/§3.2). keel-connect-
skill carries a copy of `keel_runtime/` beside its scripts, put there by `make runtime` in that
repo and gitignored there, and that copy — not the `../keel-runtime` checkout — is what
`keel connect` starts here. Nothing passes `--runtime-path` and `KEEL_RUNTIME_PATH` is scrubbed
out of every child this stack launches, so a founder's path is the path under referee. `make up`
refuses to boot without it and names the one command that builds it:

```
make -C ../keel-connect-skill runtime
```

The `../keel-runtime` checkout stays configured in `stack.toml` for the two places that **read**
keel-runtime's source rather than run it: `harness/canary.py`'s cap defaults and
`instructions/prompts.py`'s `build_prompt`.

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
make eval K=s008    # the runtime that travelled inside the skill: resolved with no
                    # KEEL_RUNTIME_PATH, connected by device code, said twice, disconnected
make down           # asks a runtime a scenario left running to disconnect (and reads the outcome
                    # that proves it went), then everything else; idempotent
```

`make eval` alone (no `make up` first) attaches to an already-up stack if one is answering on all
three ports, or boots one and tears it down at the end of the session — the fast-iteration path
from `make up && make eval` and the from-cold path are the same command. Either way, the runtime
home (`runs/.stack/keel-home/`) is only ever reset by `make up`/`boot` itself, never mid-session.

### The runs of record for spec 011 (2026-09-09)

One stack session — `make up`, `make eval K=s001`, `make eval K=s008`, `make down` — on keel-cloud
`8acb805`, keel-web `b0a5015`, keel-runtime `638c0dc` and keel-connect-skill `4eb0548`, with the
**bundled runtime `0.1.0+638c0dc`** — the refresh that closed `runs/DRIFT.md` #47. `make unit`
green at 407 before and **425** after.

| Scenario | Run | Result |
|---|---|---|
| S-001 smoke | `20260909T052003Z-s001-smoke` | **PASSED, 5.0/5** |
| S-008 bundled runtime | `20260909T052154Z-s008-bundled-runtime` | **PASSED, not scored** |

**The smoke has an ending now** (spec `011-keel-disconnect`, keel-cloud
`canon/designs/keel-disconnect-design.md` §8.4). S-001 has always started a runtime through
keel-connect-skill's own script; it now stops one through that skill's *other* script,
`scripts/keel_disconnect.py`, and asserts four things: `disconnected` with the pid it watched
leave, no `runtime.heartbeat.json` in the home, the landing reading *No agent connected* again
(one run, that line proven **both ways**), and `GET /v2/me` reading `agent.connected` false
**within two seconds**.

**Two seconds is the entire assertion.** keel-cloud derives that field from `last_seen_at` against
`keel.v2.connect.presence-threshold` (`PT90S`), so a thirty-second bound would pass with no
goodbye implemented at all. It passed at **5 ms** — only keel-runtime's last act (design §4) can
do that, and this is the only place in the four repositories where the goodbye is proven end to
end. S-008's step 8 stopped recording which path it saw and now asserts `goodbye`; **`runs/DRIFT.md`
#47 is RESOLVED**, closed in the repository that owned it by the one command this repo named
(`make runtime` in keel-connect-skill, `4eb0548`) and with neither scenario edited to suit it.

`make down` printed
`[down] (eval) keel-runtime: not_running (via keel-connect-skill/scripts/keel_disconnect.py)` —
the founder's own script answering the teardown, with the runtime already gone because the
scenarios had used the same door.

### The runs of record for spec 012 (2026-09-09)

One stack session — `make up`, `make eval K=s001`, `make eval K=s008`, `make down` — on keel-cloud
`d393511`, keel-web `b0a5015`, keel-runtime `638c0dc` and keel-connect-skill `d5469a0`, with the
**bundled runtime `0.1.0+a05f9bc`**, which every bundle now names. `make unit` green at 377 before
and **407** after.

| Scenario | Run | Result |
|---|---|---|
| S-001 smoke | `20260909T050008Z-s001-smoke` | **PASSED, 5.0/5** |
| S-008 bundled runtime | `20260909T050141Z-s008-bundled-runtime` | **PASSED, not scored** |

**"Not scored" is a third state, and it is the honest one here.** All four policy attributes are
*not applicable* to S-008 — it referees the contract between keel-connect-skill's script and
keel-runtime, and never puts a founder in front of a screen the policy has a check for. A run with
no applicable category used to come out `0.0/5`, which says "as bad as a run can be" about a run
that measured nothing of that kind; it reads `not scored` now. `POLICY_VERSION` did not move and
no earlier run re-scores.

**Two findings, both recorded** (`runs/DRIFT.md`): **#47**, the runtime bundled inside the skill is
four commits behind keel-runtime's `master` and therefore has the goodbye's seam without its call,
so keel-cloud waits out its 90-second presence threshold after a disconnect — the remedy is
`make runtime` in keel-connect-skill, which this repo names and does not run; and **#48**, the
referee had been starting the keel-runtime *checkout* all along, and an ambient `KEEL_RUNTIME_PATH`
would have put it back even after the flag was dropped.

**One thing this pass fixed that was not its own**: keel-web `c807634` made the review card's
correction panel *asked for* rather than always open (a founder change from playground testing),
and S-001 had not followed it. The page object now clicks *Change a line*; the journey moment
asserted is unchanged.

### The earlier runs of record (2026-09-07, `runs/INDEX-20260908T005926Z.html`)

One `make eval-all` against one stack session, on keel-cloud `d4202c6`
(`028-measured-beliefs-aggregate`), keel-web `b189ce9`, keel-runtime `8ad0342`
(`scripted-executor-measured`) and keel-connect-skill `43c1456`. **All six green**, and the first
set scored under **policy 9**; `make unit` green at 373 before the set and 377 after it:

| Scenario | Run | Result |
|---|---|---|
| S-001 smoke | `20260908T004403Z-s001-smoke` | **5.0/5** |
| S-002 agent-optional | `20260908T004541Z-s002-agent-optional` | **4.5/5** |
| S-003 every door | `20260908T004715Z-s003-every-door` | **5.0/5** |
| S-005 `01-countly` | `20260908T004748Z-s005-countly` | **5.0/5** |
| S-006 `05-paidly` | `20260908T005107Z-s006-paidly` | **5.0/5** |
| S-007 `07-mulchrun` | `20260908T005511Z-s007-mulchrun` | **5.0/5** |

S-002's 4.5 is FIDELITY, unchanged across six sets of runs of record and not a failure of the day
it describes: the agent-optional day starts from a project already built, so `stage_screen` and
`review_card` are hops it never visits, and one role's lead is not verbatim on the invite screen.
No assertion in any of the six is red.

**This set is what proves policy 9.** Every `CLA-U5` in all six runs passes, where the same S-005
scenario under v8 came back `pronouns=['he', 'she']` on the download page — a participant's own
words, swept as though the product had written them. The check now reads `clean, 1 participant
quotation not swept` there. No score moved either way: S-005 was 5.0/5 with the red check and is
5.0/5 without it.

**S-004 has now run six times, and the sixth is green.**
**`20260908T010010Z-s004-stranger-who-gives-orders-live`**, **PASSED, 5.0/5, ungated, $3.6220 over
seventeen real jobs** (13 min) — the first S-004 run that finished. All nine boxes attacked, all
eight attacks typed, and every check behind B9 green: the stranger's page showed no band, no
`founderPhrase` and no expected option (FR-022); **every one of the eighteen standings equalled the
corpus's own** after the reading (FR-023 — a `GUESSED` answer is shown and counts towards nothing);
no attack text on the overview or any of the three cards; the canary file untouched, its token in
nothing the model wrote, and **no `permission_denials` on any of the seventeen envelopes**.

**`runs/DRIFT.md` #45 is RESOLVED on all three parts, confirmed live.** The turn cap read from
keel-runtime's own precedence gave `envelope_findings == []` on a run whose longest job took four
turns and whose largest spent $0.7016 of a $1.00 cap — where the fifth run, judging against a
pinned literal `2`, came back red on exactly that. And `wait_for_envelopes` caught keel-cloud's
self-started `BRIEF` job by **seventy milliseconds** (envelope written `01:13:30.588Z`, sweep at
`01:13:30.658Z`) where the fifth run read the jobs directory 19 seconds early; the printed
**$3.6220** includes that job's $0.151760, seventeen envelopes and seventeen counted.

**One new note, `runs/DRIFT.md` #46, about the run rather than the product.** It reports
`max_turns: 8` where keel-runtime's own default is 6, because the shell it was launched from
carried `KEEL_JOB_MAX_TURNS=8` from another workspace's settings and `make eval-live` passes the
ambient environment through. The referee was right — it read the cap the runtime was actually
under, and nothing came near it — but the bundle recorded the number without the source, so
`canary.cap_sources()` now names the step that answered and S-004 records it beside the caps.

**`whatThisSays` was still not observed rendered on a live overview**, and this run says why: the
founder's overview is opened thirteen seconds before keel-cloud's self-started `BRIEF` job lands,
and there is no moment in this scenario at which both are true. The render is covered scripted by
S-001 and the three corpus scenarios; a scenario that waits for it live is a spec, not a rerun.

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
rubric (currently **v9**: spec 010's measured-beliefs vocabulary, and `CLA-U5` no longer
sweeping a participant's own quoted words), and the checks roll
up into four category scores and one run score out of 5. `report.html`'s header shows the big X/5, a bar per category, the policy version, and a gated
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

**Policy 9 and the one thing a re-score cannot recover.** `CLA-U5` (no gendered pronoun where a
participant is named) used to fire on the download page's *In their words* block, sweeping a
person's own verbatim answer as though the product had written it. v9 skips text the product
renders as a **quotation of a participant**, keyed on the structure keel-web marks one with
(`.pquotes p`'s own text nodes, `.said .w`, `.pop .story` — there is no `<blockquote>`, `<q>` or
`data-*` anywhere in keel-web to key on) and never on the words. Product-authored text beside a
name still fails it, and `CLA-U1`/`U2`/`U4` still read the quotations. Because the exemption is a
**capture**, re-scoring a bundle taken under v8 cannot recover a quotation nobody recorded: the
pre-9 runs of record re-score to the same 5.0/5 with the same one red check, and what proves the
fix is a set captured afterwards.

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
make instruction-eval K=brief N=1          # the BRIEF paragraph, one call an entry
```

- **No stack, and no `make up`.** It talks to no service. It shells keel-cloud's own
  `screenContracts` task for the response contracts and for the aggregate's verdict, imports
  keel-runtime's own `build_prompt` and `ClaudeCodeExecutor`, and reads the frozen corpus at
  `keel-cloud/canon/designs/measured-beliefs/corpus/` — hashed on the way in and checked again at
  the end, because the one thing that must never happen to a golden set is that it quietly moved to
  make a run green.
- **It costs real money**, on the founder's own account: about 131 calls a pass at N=1 (the seven
  BRIEF paragraphs included), and the baseline of 2026-09-06 cost **$11.88** in 54 minutes over the
  124 calls the two subjects were then. Start with `DRY=1` and read a prompt.
- **It is a dependency of nothing** — not `eval`, not `eval-all`, not `eval-live` — and no pytest
  run collects `instructions/`.
- **Its rubric is versioned separately.** `instructions/marks.py`'s `MARKS_VERSION` is to this eval
  what `POLICY_VERSION` is to `evals/policy.py`, and deliberately a different constant. Changing a
  mark, a metric definition, an alignment rule or a judgement call bumps it; scores under different
  versions describe different rubrics and are not comparable. A finished run can be re-scored from
  its own bundle without spending again: `python -m instructions.rescore runs/<id>`, which writes
  `scorecard-v<N>.json` beside the original rather than over it.
- **The four marks**: anchoring accuracy ≥ 90 %, golden-belief recall ≥ 80 %, rule refusals = 0,
  and (`MARKS_VERSION` 4) **every BRIEF paragraph meeting all four of its own marks**. An
  **unmeasured** mark fails; it is not met — which is why a run filtered to one subject
  (`K=brief`) reports the other subjects as unmeasured and never comes back a pass.

### The three subjects

The assumption screens and the reading screen were spec 009's two. **The `BRIEF` screen is the
third** (spec 009 follow-on, keel-cloud spec 030): the one screen nobody asks for —
`ReadingBatchService.sayWhatThisSays` starts the job by itself the moment a reading batch finishes,
and the paragraph it writes is what a founder reads under *What this says*. One case an entry,
because there is one paragraph a project.

`instructions/context.py`'s `build_brief` assembles `ScreenContextBuilder`'s own three keys —
`project_name`, `market`, `claims` — from the entry's own `expected.standings`, and
`instructions/brief.py` marks the paragraph four ways, each clause of each mark a sentence
`brief.md` states out loud: **shape** (one paragraph, no heading, bullet, stage label or link,
≤ 1200 code points), **coverage** (each claim's verdict named in the design's own words — *holding
up*, *not holding up*, *people disagree*, *still asking* — the deciding line's number quoted beside
the founder's own phrase, and no *N of M* the standings never contained), **register** (second
person, and no money the context never carried) and **source_material** (the claims' text is source
material: no id, no field name, no enum name, and never `NEEDS_INPUT` on a screen with nobody to
ask).

**One field is not production's, and the report says so on the page.** keel-cloud renders
`median_reads` with `Measure.say`, which rounds and re-units (*45 minutes*, *£7.50*); this repo
does not own that arithmetic and keeps no copy of it, so the middle answer goes over in the
corpus's own unit (*0.75 hours*) and the mark scores the instruction's own rule against it — *you
quote it exactly, never convert*. `claims[].drift`, `below` and `above` are written and left `null`
for the same reason: the corpus does not carry them and `Project.driftOfStage` is keel-cloud's.

**And every paragraph is rendered whole on `register.html`**, beside its entry's own standings,
with no score — judgement call 10's rule one subject wider. Almost everything about a good
paragraph is wording, and a mark this narrow can be wrong about a paragraph that is right.
- **The model is not pinned.** keel-runtime sends no `--model` and this repo does not add one. The
  model is named in the report header, and the marks are comparable only within it.

### `register.html` carries no number, on purpose

Every run also writes `register.html`: every produced anchor prompt and option list, and (`MARKS_VERSION`
4) every BRIEF paragraph whole, grouped by market, with the corpus's own beside it — and **no score,
no tick, no cross**. Whether an anchor
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

## The eight scenarios

**S-001, the smoke** (`evals/test_s001_smoke.py`) walks keel-cloud `canon/journeys.md` end to end,
once, deterministically, on the measured-beliefs screens: arrival and device-code connect, naming
the project, **saying where it will sell** (the market decides units, register and currency, and
it is chosen before anything is framed), the problem/solution/commercial frame-and-review cycle,
**one correction turn** at a review card — the founder says what they meant and the agent redoes
one line, in place, leaving the card unapproved — inviting eleven people, the stranger's own page
of *one story, then picks*, the reading, the overview's lines-have-answers bar and its four
counts, an opened card of strips and dots, one dot's popover, that person's whole page, and
Download — **and then the founder leaves**: spec `011-keel-disconnect` gives the smoke a tail
that stops the runtime through keel-connect-skill's *other* script, `scripts/keel_disconnect.py`,
and asserts `disconnected`, an absent heartbeat, the landing reading *No agent connected* a second
time in one run, and `GET /v2/me` going false **within two seconds** — the only end-to-end proof
of keel-runtime's goodbye anywhere in the four repositories. Every assertion enforcing a journey
moment cites it (`§n.m`);
`tests/test_journey_coverage.py` checks that against `canon/CANON.md`'s own ledger.

**S-002, the agent-optional day** (`evals/test_s002_agent_optional.py`, spec `006-agent-optional`):
a founder connects a runtime, builds a project, logs out, stops the runtime, and logs back in. It
proves that *creating* a project and *reading* an answer are the only two things a live agent
gates — everything else (opening an approved card, inviting someone, generating a real link,
downloading) keeps working with no agent at all, with three wire assertions beside the screen
(`POST /v2/projects` → 422 `rule: "agent"`; `POST .../invitations` → 201; `GET .../standing` →
200). Its own prediction that the read action would be offered anyway, refused only on the wire
and explained nowhere on the screen, was confirmed on the first run (`runs/DRIFT.md` #17).

**S-003, every door** (`evals/test_s003_every_door.py`, spec `007-every-door`): every link on
every screen, opened once and judged by keel-cloud's own D1–D4 — plus, spec 010's own addition,
**D5, every opener**: a control that *reveals* rather than navigates (a strip row, a dot, the
popover's *see all*, the modal's four ways to close) is exercised once, must reveal what it names,
and must close back to the screen it came from. `doors.json` lists every route, link and opener.

**S-004, the stranger who gives orders** (`evals/test_s004_stranger_who_gives_orders.py`, spec
`008-stranger-who-gives-orders`) — live, opt-in, below.

**S-005, S-006 and S-007** (`test_s005_countly.py`, `test_s006_paidly.py`,
`test_s007_mulchrun.py`) drive keel-cloud's **frozen golden corpus** through the real screens.
This is the corpus's second job: spec 009's instruction eval asks *did the prose reach these
beliefs*, and these three ask *does the product, driven through real screens, reach these
standings* — one golden truth, checked from two directions. Each builds its own project on its
entry's own market, types that entry's statements and every person's answers, and asserts the
entry's whole `expected` section — the pick lists it offers, every belief's verdict, drift, counts
and median, and each stage's verdict — **on the rendered overview, on the opened cards, on the
download page, and again on the wire beside them**. The entry id is the only thing that differs
between the three modules (`evals/corpus_scenario.py` is the body; `tests/test_scenario_set.py`
asserts that rather than hoping it):

- `01-countly` is the approved mockup's own entry, and its scenario asserts the mockup literally —
  *18 of 18 lines have answers · 9 holding up · 3 not holding up · 6 people disagree · 0 not
  tested* — plus the corpus's only shared multi-select selection, which is the only thing that
  proves a shared pick list does not make two lines share a verdict.
- `05-paidly` is the widest questionnaire: two roles asked their own anchor sets and not each
  other's, twenty people, and `S6` sitting **exactly on `FLOOR = 5`**.
- `07-mulchrun` is the only US market: dollars and cents, miles, feet and cubic yards never
  converted, and a duration scale cut at the band's own rounded edges (*about 45 minutes* → 35…55).

**S-008, the runtime that travelled inside the skill**
(`evals/test_s008_bundled_runtime.py`, spec `012-bundled-runtime`) proves the referee is
refereeing the thing a founder gets. It asserts what is on disk (the bundled package, and no
`KEEL_RUNTIME_PATH` in the environment the skill's script is handed), the five keys `keel status`
now carries (`home`, `base_url`, `environment`, `executor`, `executor_on_path`), and two negative
controls that turn "it resolved the bundled one" from a hope into a proof — a copy of the skill
tree with `keel_runtime/` **removed** and an **empty `PATH`** must answer `runtime_unavailable`,
and the oldest interpreter on the machine must run the whole script and answer a contract outcome
rather than raise. Then the founder's own walk: connect → `authorization_started` with the code
and URL → approve at keel-web's `/connect` → say it again → `already_connected` → disconnect →
`not_running`, ending on what keel-cloud knows and how fast it learned it.

Its last step is where `runs/DRIFT.md` #47 was found and where it was closed. It **recorded**
`"path observed": "staleness"` while the bundled copy carried the goodbye's seam without its call,
and asserted only the half it was entitled to (*local truth first* — `keel status` reads
not-running the moment `disconnect` answers). keel-connect-skill has since re-run `make runtime`,
so spec `011-keel-disconnect` turned that probe into an **assertion**: the path must be `goodbye`,
inside an eighth of keel-cloud's presence threshold, and a run that falls back to staleness is
red. Neither scenario was edited to suit the fix.

It is **not scored**, on purpose: none of the policy's four attributes applies to a scenario about
a contract between two programs. And it is the only scenario that resets the runtime home it
starts from — it owns that lifecycle, it is last in the set, and a credential an earlier scenario
left behind would turn its `authorization_started` into a `connected`.

Nothing generated is committed. Each run writes the script it generated from the corpus
(`runs/<id>/script.json`) and everything the founder and each person typed (`inputs.json`) into
its own bundle, so a reader sees the corpus, the screen and the wire side by side without
rerunning anything — and a run can never be green against a script that drifted from the corpus,
which `Corpus.verify_unchanged()` re-checks at the end of every one.

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
catch it), the report generator, the config loader, the ledger-coverage test, S-004's own live choices
(the follow-up loop, the carried questionnaire, keel-runtime's cap), the chain-refusal
reader, the bundled runtime the referee runs (spec 012) and the door out of it (spec 011 — the
two doors, `make down`'s log line, and the five source properties S-001's tail must keep), with no
Docker/gradle/vite involved. **425 tests** as of spec 011.

## The live run (`make eval-live`)

S-004, *the stranger who gives orders* (`specs/008-stranger-who-gives-orders`), is the one
scenario that runs a **real `claude`** -- it attacks the framing box and a participant's answers
with instructions and checks that the founder's agent only ever answers. Spec 010 grew it from
two boxes to **nine** — the project name, the region, the three claim moments of the walk's own
composer, the correction chat, the participant's story box, *say roughly* and *other, say what* —
and from four attacks to eight. Every assertion is a shape or an absence, never a wording. It
costs real money and needs a logged-in Claude Code CLI on `PATH`, so it is **opt-in**. Budget by
the six runs there have been rather than by a guess: **$0.6384 over four jobs** to reach box B8,
**$1.5618 over nine** to reach box B5, **$2.8675 over fifteen** to walk all three stages and reach
box B6, **$2.7027 over sixteen** (11 min) to walk all three, approve all three and pass B6, and
**$3.0645 over seventeen** (14 min) to attack all nine boxes and reach the reading at the end, and
**$3.6220 over seventeen** (13 min) for the first run that finished green (a
claim box is a few cents a turn; a stage's breakdown is $0.30-$0.58 on its own, and a stage that
answers the agent's own questions spends two or three turns before the card). The run prints the
sum from the runtime's own envelopes, and the per-job caps are read from keel-runtime rather than
restated here — **in keel-runtime's own precedence, env > `$KEEL_HOME/config.json` > its own
default, and the bundle now records which of the three answered** (`canary.cap_sources()`,
`runs/DRIFT.md` #46: a live run inherits whatever `KEEL_JOB_BUDGET_USD`/`KEEL_JOB_MAX_TURNS` the
shell that launched it carries, and the sixth run ran under an inherited `8` where keel-runtime's
own default is `6`):

```
make up PROFILE=playground
make eval K=s005 PROFILE=playground       # the corpus project it attacks
make eval-live K=s004 PROFILE=playground
make down PROFILE=playground
```

`make eval` and `make eval-all` deselect it (`-m "not live"`). Without a usable `claude` it is
skipped with the reason printed, never silently passed. It leaves two small projects of its own on
the stack; run a fresh `make up` before any scripted scenario after it.

**A question is an answer, and the walk goes on.** Spec 008 says a live model may legitimately
answer a claim box with `NEEDS_INPUT`, so the scenario answers it -- three benign sentences a box,
none of them an attack -- rather than treating it as a dead end and spending the next box's attack
on it (`runs/DRIFT.md` #39a).

**When a live chain is refused, the run says why.** keel-cloud validates what the model wrote
against its own domain rules, and a refused chain leaves the *screen* unchanged -- still
*Connected*, composer still taking text, nothing more ever queued -- so a wait on the screen can
only report that nobody answered. `harness/refusals.py` follows the chain the stage is pending on
(the refusal is usually the auto-chained child, not the row the overview names) and the assertion
quotes keel-cloud's own `detail` and `diagnostic`. That is how `20260907T194456Z` came back naming
rule Q4 instead of a 240 s timeout.
