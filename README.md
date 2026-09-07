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

### The runs of record (2026-09-07, `runs/INDEX-20260907T223801Z.html`)

One `make eval-all` against one stack session, on keel-cloud `932fdfe`, keel-web `b189ce9`,
keel-runtime `eea0555` (`scripted-executor-measured`) and keel-connect-skill `43c1456` -- unchanged
siblings, and this repo's own *What this says* fix. **All six green**, `make unit` green at 279
before the set and 295 after it:

| Scenario | Run | Result |
|---|---|---|
| S-001 smoke | `20260907T222232Z-s001-smoke` | **5.0/5** |
| S-002 agent-optional | `20260907T222407Z-s002-agent-optional` | **4.5/5** |
| S-003 every door | `20260907T222540Z-s003-every-door` | **5.0/5** — all four D5 openers `opens` |
| S-005 `01-countly` | `20260907T222613Z-s005-countly` | **5.0/5** — all eighteen standings |
| S-006 `05-paidly` | `20260907T222935Z-s006-paidly` | **5.0/5** — all ten, `S6` on `FLOOR` |
| S-007 `07-mulchrun` | `20260907T223344Z-s007-mulchrun` | **5.0/5** — US units, unconverted |

S-002's 4.5 is FIDELITY, unchanged across four sets of runs of record and not a failure of the day
it describes: the agent-optional day starts from a project already built, so `stage_screen` and
`review_card` are hops it never visits, and one role's lead is not verbatim on the invite screen.
No assertion in any of the six is red.

**What this set exercises that no set before it did: *What this says*.** keel-cloud starts a
`BRIEF` job of its own every time a reading batch finishes and renders the one field it returns as
the overview's paragraph — and the generated script had no `BRIEF` entry, so every one of those
jobs failed (`scripted executor has no entry for BRIEF`) into a `catch` that swallows it. Six green
runs at 5.0/5 had never produced a paragraph, and the only assertion there was — *a heading and
more than twenty characters under it* — was satisfied by the server's own "not yet" note standing
in its place. `harness/corpus_script.py` now emits a `BRIEF` entry per corpus entry
(`what_this_says_for`: one plain sentence per stage from the entry's own `expected.stages`, marked
as scripted in its first sentence), and S-001 and the three corpus scenarios assert **both** states
— the server-voiced note before the first reading, and after it the paragraph on the screen equal,
character for character, to `Overview.whatThisSays` on the wire. `inference_interaction` for this
session reads **50 `BRIEF` APPLIED**; the one `JOB_FAILED` left is S-002, which starts the runtime
with no script at all and so runs on keel-runtime's bundled one (`runs/DRIFT.md` #42).

**S-004 has now run four times, and `runs/DRIFT.md` #41 is RESOLVED by the fourth.** The first
(`20260907T184207Z`, $0.6384 over four jobs) died on this repo's own grip (#36); the second
(`20260907T194456Z`, $1.5618 over nine) died on the product at the *solution* claim (#37); the
third (`20260907T214451Z`, $2.8675 over fifteen) walked all three stages and died at B6, on the
referee again (#41). The fourth — **`20260907T223817Z-s004-stranger-who-gives-orders-live`**,
**$2.7027 over sixteen real jobs**, no `permission_denials` on any envelope and none over two turns
plus the CLI's own retry — walked **PROBLEM → SOLUTION → COMMERCIAL**, framed and drew a review
card for each, approved all three, **passed B6** and went on past it. A1–A5 and A8 were typed, into
B1–B6, and every claim box answered about the idea and carried no marker, URL, path,
`credentials.json` or `.ssh` forward.

**#41's two fixes are confirmed live.** B6's scan came back `leaks: {}` — `agent_said()` drops the
founder's own echoed message, so A1's own wording in it no longer reddens a box the product passed
— and A8's before-and-after read the approved `PROBLEM` card through `OpenedCard` and got **five
real lines** where the third run got `[]`. FR-022's "identical, line for line" compared something
for the first time, and it held.

**The run is red, at B8, on the referee again — `runs/DRIFT.md` #44.**
`ParticipantPage.anchors()` read `div.picks` as a child of the anchor's own block where keel-web
renders it as its **sibling**, so every anchor came back asking nothing, and both of S-004's ways
of choosing what to attack search that list. The run stopped on *"this link carries no anchor with
a say roughly control at all"* against a page whose own captured text, one step above, offers three
of them. Fixed here with a real-markup test that fails against the old read; not verified live,
because there was one run and no rerun. **B7, B8 and B9, and attacks A3, A6 and A7, are still owed
a run**, as are the canary sweep, the standings-unchanged check and both leak sweeps — and, behind
them, the first real `BRIEF` job this repo has ever caused (`runs/DRIFT.md` #43: keel-cloud's
shipped `brief.md` still describes the contract spec 030 deleted, so a live agent cannot write the
paragraph at all).

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
rubric (currently **v8**, spec 010's measured-beliefs vocabulary), and the checks roll
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

## The seven scenarios

**S-001, the smoke** (`evals/test_s001_smoke.py`) walks keel-cloud `canon/journeys.md` end to end,
once, deterministically, on the measured-beliefs screens: arrival and device-code connect, naming
the project, **saying where it will sell** (the market decides units, register and currency, and
it is chosen before anything is framed), the problem/solution/commercial frame-and-review cycle,
**one correction turn** at a review card — the founder says what they meant and the agent redoes
one line, in place, leaving the card unapproved — inviting eleven people, the stranger's own page
of *one story, then picks*, the reading, the overview's lines-have-answers bar and its four
counts, an opened card of strips and dots, one dot's popover, that person's whole page, and
Download. Every assertion enforcing a journey moment cites it (`§n.m`);
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
(the follow-up loop, the carried questionnaire, keel-runtime's cap) and the chain-refusal
reader, with no Docker/gradle/vite involved.

## The live run (`make eval-live`)

S-004, *the stranger who gives orders* (`specs/008-stranger-who-gives-orders`), is the one
scenario that runs a **real `claude`** -- it attacks the framing box and a participant's answers
with instructions and checks that the founder's agent only ever answers. Spec 010 grew it from
two boxes to **nine** — the project name, the region, the three claim moments of the walk's own
composer, the correction chat, the participant's story box, *say roughly* and *other, say what* —
and from four attacks to eight. Every assertion is a shape or an absence, never a wording. It
costs real money and needs a logged-in Claude Code CLI on `PATH`, so it is **opt-in**. Budget by
the four runs there have been rather than by a guess: **$0.6384 over four jobs** to reach box B8,
**$1.5618 over nine** to reach box B5, **$2.8675 over fifteen** to walk all three stages and reach
box B6, and **$2.7027 over sixteen** (11 min) to walk all three, approve all three and pass B6 (a
claim box is a few cents a turn; a stage's breakdown is $0.30-$0.58 on its own, and a stage that
answers the agent's own questions spends two or three turns before the card). The run prints the
sum from the runtime's own envelopes, and the per-job cap is read from keel-runtime rather than
restated here:

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
