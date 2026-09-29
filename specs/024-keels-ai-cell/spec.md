# Feature Specification: the Keel's-AI door

**Feature Branch**: `024-keels-ai-cell`

**Created**: 2026-09-29

**Status**: Draft — for the founder's review. **Implemented; never run live, and not runnable
live today** (see *What the siblings are, read at these commits*): the door it walks through is on
a keel-web branch, the `aiPath` it reads is on a keel-cloud branch, and the executor that answers
its jobs is an untracked draft. Everything that can be proven without a twin is proven and held by
`make unit`; the first run is the founder's to spend, and the cell is weekly-only so it can only
ever be spent once a Saturday.

**Input**: keel-cloud `canon/designs/ai-credits-design.md` §5 (the free grant), §6 (*the door
decides the AI*, §6.2 the one line at the top right, §6.3 what a project costs), §7 (the one gate)
and §8 (the ledger); keel-cloud spec `044-ai-credits` (`/v2/me`'s `aiPath` and `creditsAvailable`;
the 409 at New project; `GoogleSignIn.doorOf`); keel-cloud spec `045-keels-ai-executor` (what a
`KEEL` job looks like on the wire, and what it says when it cannot run); keel-web spec
`024-front-door` (the two doors, the shell line, the refusal, the words that read *Keel*).

The design's own sentence is the whole of the argument for this cell:

> **"The door decides the AI."** Signing up with Google is Keel's AI and the grant. Running
> `keel connect` is the founder's own AI and no ledger rows at all. There is no switching once
> inside.

There are two doors into this product and this repository has only ever refereed one of them.

## The one sentence

S-012 gains a host that is not a host: `KEEL_JOURNEY_HOST=keel` signs the founder up through
keel-web's `/signup`, walks the **same journey** with no runtime, no host CLI and no device
approval, and asserts the things that are only true on Keel's own AI — 1,500 credits on the shell
line, `aiPath: "KEEL"` on the wire, `execution.host: "api"` and a real `actual_cost_micro_usd` on
every job, the founder's screens saying *Keel* where they used to say *your AI*, and a `KEEL_HOME`
that is still empty when the brief is written.

## What changes, stated first

One value on the journey's host axis, one harness module that does nothing but say so, three
skipped legs, six new assertions, one cell in `weekly`, one `make` target. **Nothing that any
existing cell asserts moves**: the four host values and their four executors are untouched, the
plugin and Spec Kit roads are untouched, and the Copilot argv still does not move a flag.

It is **one scenario**, not a fourteenth. AGENTS.md's rule about the three named LLM places is that
a fourth must be *argued for and added to that line rather than quietly written*; spec 019 widened
S-012 by a host and spec 022 widened it by a packaging, and this widens it by a **door**. The legs
are the same legs where they exist, the verdict is the same verdict, the scorecard is the same
scorecard (none: S-012 is unscored), and the marks are the same marks.

## What the siblings are, read at these commits

| Sibling | What this feature depends on | Where it is today |
|---|---|---|
| keel-cloud | `ai-credits-design.md` §5–§8 (design of record, 2026-09-29); spec 044 FR-013/014 (the door writes `ai_path`), FR-017 (+1,500 at creation), FR-028 (the 409), FR-033 (`/v2/me`); spec 045 FR-043 (`execution.host: "api"`), FR-023/025/027 (`actual_cost_micro_usd`), FR-032 (`KEEL_AI_DISABLED`), FR-037 (the daily cap), FR-039 (the timeout), FR-045/046 (no live-agent refusal for a `KEEL` account). | 044 is **implemented on the branch `044-ai-credits` (`a5474c5`), not on `master`** — `master` carries only its spec draft. 045 is an **untracked draft in the working tree**: no code, no commit, no branch, and `KEEL_AI_DISABLED` exists nowhere but its own spec. `canon/openapi-v2.yaml`'s `execution.host` enum is still `[claude, copilot, codex]`. |
| keel-web | spec 024 FR-003 (`/signup` and *Sign up with Google*), FR-004 (`/login` is now *Log in with Google*), FR-011 (`.creditsline` vs `.agentline`), FR-013 (the gate and the lock are not rendered), FR-014 (*Keel* for *your AI*), FR-016 (the refusal dialog), FR-020 (an unknown `aiPath` falls to the own-AI road). | Implemented on the branch **`024-front-door` (`f2627e1`)**, not on `master`. |
| keel-runtime | **nothing.** This is the point of the cell. | `161b649` |
| keel-connect-skill | **nothing.** No marketplace, no plugin, no `SKILL.md`, no script. | `58e5490` |

**So the cell cannot pass against the twin today, and that is a statement about the twin and not
about the cell.** What it does against today's staging is fail fast and legibly: `POST /v2/projects`
answers `422 rule: "agent"` (spec 044's own *what this pass does not do*: a `KEEL` account with no
runtime bound still meets today's live-agent refusal, **after** the credit gate has answered), and
the bundle says so in that sentence. Spec 045 FR-045 is what removes it.

## User scenarios

### S-012 through the Keel door (live, `make keels-ai`, or `make eval-live K=s012 HOST=keel`)

The same journey, in the same order, asserting the same shapes — except where the door is the
subject.

**There is no leg one.** Nothing is installed, nothing is said to a CLI, no code is issued, no
device is approved, no runtime is started. The three assertions that belong to leg one — the
plugin in the marketplace, `keel-connect` seen as a plugin skill, *"Your AI is connected"* — are
**not made loosely; they are not made at all**, and the bundle says which and why.

1. **The founder makes an account at the sign-up door.** keel-web's `/signup`, the one
   `<a class="btn google">` reading *Sign up with Google*, the gated stub picker, this cell's own
   registered founder, and back through the real callback with `return_to=/`. No password, no
   transplanted cookie, no seeded session — the same three hops `stack/auth.py` has walked since
   spec 015, through a different door.
2. **The landing says a number, not an agent.** The shell line reads **`1,500 credits available`**
   and there is **no agent line at all**. `GET /v2/me` answers `aiPath: "KEEL"` and
   `creditsAvailable: 1500`.
3. **This run's `KEEL_HOME` is empty and stays empty.** No heartbeat, no launch log, no `jobs/`
   directory — before the first screen and again after the last one.
4. **The project starts with no runtime bound.** *New project* is not locked, no gate card is
   rendered, and `POST /v2/projects` answers `201` — because a `KEEL` account is not asked for an
   agent (spec 045 FR-045) and has more than a framing's 540 credits (spec 044 FR-028).
5. **The number goes down when the first framing starts.** Read from `/v2/me` before the founder
   types the PROBLEM statement and again once the first job is under way: strictly less, because
   the `HOLD` is written in the same transaction as the job insert (design §8.3, X1) — *"the number
   drops when the hold is written, not when the job ends"*.
6. **The founder's screens say *Keel*.** The chat's own name, the chat mark, the People page's
   reading column: *Keel*, and the words *your AI* appear nowhere on a founder screen inside the
   project (keel-web spec 024 FR-014, `AI_SUBJECT_KEEL`).
7. **The journey itself, unchanged.** Three stages framed, reviewed and approved as-is; the
   entry's first five people invited and answered in their own words; the reading read; *What this
   says*; the overview and one card opened. Shapes and absences only (spec 016 FR-007).
8. **Every job was answered by Keel's own account, and cost something.** Every interaction's job
   carries `execution.host == "api"` and an `actual_cost_micro_usd` that is present and `> 0`
   (spec 045 FR-043, FR-023). The model ids the report carries — `model_requested`,
   `model_used` — go into the bundle and are asserted against nothing.
9. **Nothing ever started a process.** The harness's own Keel host has run no subprocess, said
   nothing to any CLI, and written no host home; `KEEL_HOME` is as empty as it was at step 3.
10. **There is no way out to take.** No `keel disconnect`: there was never a runtime, and a
    scenario that shelled the skill's own door out would be asserting something about a repository
    this cell does not touch.

### The door that is shut (live, the same command, against a twin without the key)

**Given** keel-cloud has no `KEEL_ANTHROPIC_API_KEY` (or the executor is otherwise disabled),
**when** the founder types the PROBLEM statement, **then** the first job fails **immediately** with
`error.code = "LLM_UNAVAILABLE"` and `error.message` carrying **`KEEL_AI_DISABLED`** — and the cell
**fails on that sentence, at that step, within seconds**. It does not spend five minutes of
follow-ups on a door that is bolted, and it never reports a timeout for a refusal the wire named at
once.

## Requirements

- **FR-001** `KEEL_JOURNEY_HOST=keel` is a fourth value of the journey's host axis. It is refused
  by name like any other typo, it is read once at import like the other three, and the bundle it
  names is `runs/<stamp>-s012-journey-keel/`.
- **FR-002** **`keel` in a cell id, `api` on the wire, and the two are not the same word.** The
  founder's door is *Keel's AI*; keel-runtime's vocabulary for *no CLI, the provider's API* is
  `execution.host: "api"` (spec 045 FR-043). The cell id, the bundle name and the summary row say
  `keel`, because that is what a reader of eight rows needs; the assertion says `api`, because that
  is what the wire says. The bundle records both, beside each other, with this sentence.
- **FR-003** Leg one is **skipped, not weakened**. `harness/keel_host.py` refuses
  `add_marketplace`, `install_plugin`, `plugin_list`, `skill_proof`, `install_extension`,
  `extension_proof` and `say` **by raising, by name**, so a future edit that reached for one gets a
  sentence rather than an empty dict. The scenario never calls them.
- **FR-004** The sign-up path is keel-web's own: `/signup`, `get_by_role("link", name="Sign up with
  Google")`, the stub picker, the real callback, `return_to=/`. Nothing about `ai_path` is sent by
  this harness and nothing could be: the door is the whole of the message (keel-cloud spec 044
  FR-014, `GoogleSignIn.doorOf`).
- **FR-005** The shell line: `.creditsline` reads exactly `1,500 credits available` after sign-up,
  `.agentline` is absent, and `GET /v2/me` answers `aiPath: "KEEL"` with `creditsAvailable == 1500`.
  The comma is keel-web's `toLocaleString("en-US")` and the word `credits` never becomes singular.
- **FR-006** The credits line **decreases** once the first framing job is under way, read off
  `/v2/me` and not off the screen, and the drop is recorded in credits.
- **FR-007** Every job of the journey carries `execution.host == "api"` and an
  `actual_cost_micro_usd` that is present, an integer, and `> 0`. A job with a null cost is a
  **failure of this cell** and the message names invariant X6 — *every settled job records its
  actual cost beside its price* — because a cell that passed on a null would be certifying the one
  thing spec 045 exists to deliver.
- **FR-008** **No runtime process ever started**, asserted three ways: this run's `KEEL_HOME` holds
  no heartbeat, no launch log and no `jobs/` directory, at the start and at the end; the Keel host
  reports zero subprocesses; and `GET /v2/me`'s `agent` block reads not connected throughout
  (spec 045 FR-047: a `KEEL` account's agent block is answered truthfully and it is *not
  connected*).
- **FR-009** The founder's screens say *Keel*: the chat name reads `Keel`, and the rendered text of
  the project shell contains no occurrence of *your AI* in any case, on the chat screen and on the
  People screen. Marketing pages are not founder screens and are not swept.
- **FR-010** **Fail fast on a shut door.** Whenever a job of this journey ends `FAILED`, the wire's
  own `error.code`/`error.message` are read at once; if the message names `KEEL_AI_DISABLED`,
  `KEEL_AI_DAILY_CAP`, `KEEL_AI_TIMEOUT` or `KEEL_AI_RESTARTED`, the scenario raises **there**,
  with keel-cloud's own sentence, and the verdict's `failed_step` carries the named reason. It is
  never reported as a timeout, and the bounded follow-ups of a live walk are not spent on it.
  (Spec 045 Assumption 11: none of the four is an `error.code`; they travel in `error_message`,
  which is free text. So the reading is of the message, and `error.code` is `LLM_UNAVAILABLE` for
  the first two, `EXECUTOR_TIMEOUT` for the third and `INTERNAL_ERROR` for the fourth.)
- **FR-011** The cell is `weekly` and only `weekly`: `macos-latest`, host `keel`, Python `3.13`,
  `legs = full`, `install = none`. **Never `per_change`**, and the coverage rules refuse it there
  rather than trusting anybody to remember — because every run of this cell spends real money on
  **Keel's own Anthropic account**, not the founder's plan, and a merge that spent it would be a
  merge that billed the company.
- **FR-012** The expected spend is written down where a reader will meet it, in the design's own
  numbers: a five-participant journey is **1,250 credits** — 540 of framing, 45 of readings, 105
  for the brief and 560 of conversation (`ai-credits-design.md` §6.3, the five-participant row) —
  which is **$12.50 at list price** and **$2.44 of Keel's own inference cost**, comfortably inside
  spec 045 FR-037's default daily cap of **$10.00 per founder per day** and comfortably inside the
  1,500 the grant gives, with 250 credits spare.
- **FR-013** The run bundle says it is the Keel door: `versions.json`'s `host` block carries
  `host: "keel"`, **no CLI version** (`cli: null`, with the sentence saying there is no CLI to
  version), the expected `execution.host`, the credential plan (*none — the founder has none and
  this harness has none; the key is keel-cloud's and never leaves the box*), and the model ids read
  back off the jobs' own `execution` reports. `facts.json` carries the same in one string, as every
  other S-012 bundle does.
- **FR-014** **Nothing in `matrix.yml` changes.** A `keel` cell installs no CLI, needs no model
  pin and reads no host secret, so every host-gated step and every host-gated secret line in the
  cell job is already `false` for it. The cell is data in `matrix/cells.toml` and nowhere else.
- **FR-015** Unit tests that run with no stack, no browser and no network hold every one of the
  above that can be held without one, in the manner of `tests/test_journey_through_a_host.py`.
- **FR-016** Nothing here writes to a sibling repository and no product code is fixed. What a run
  finds goes to `runs/DRIFT.md`, and only once a run has found it.

## What this pass also fixes: the other three doors were on the wrong one

**Found while writing this spec, on 2026-09-29, and it is the more urgent half.**

keel-cloud spec 044 FR-014 decides which AI an account runs on from the door it was **created**
through, read back off the pre-login record's own stored `return_to`:

> *"an account created on a sign-in whose stored `return_to` is the connect-approval path
> (`/connect`, which is the only `return_to` keel-web builds carrying a `user_code`) is `OWN`;
> every other first sign-in is `KEEL`."*

S-012 signed in at the plain `/login`, with a `return_to` of `/`, **before** installing anything
and before saying *"keel connect"*. So did the corpus riders and S-013. On the twin each of those
cells registers a brand-new identity minutes before it signs in, so that sign-in is the one that
**creates** the account — and every one of them was creating a `KEEL` account, taking a
1,500-credit grant it was never entitled to, on a founder who was about to connect their own
runtime. Once keel-cloud spec 045 lands, keel-cloud would answer all eight weekly cells' jobs on
**Keel's own Anthropic key** instead of on the CLI the cell had just installed and just paid for.

Nothing was wrong with the product. The referee was walking a door no founder walks: the design's
own first-time flow is *install → say "keel connect" → the runtime prints a code and a URL → sign
in at `/login?user_code=…` → approve at `/connect`*, and a founder cannot sign in before that
because until their AI has printed them a code **they have nothing to sign in with**.

### The leg order, before and after

| | before | after |
|---|---|---|
| 1 | sign in at `/login` (`return_to=/`) | this run's homes are empty — a filesystem read, no session |
| 2 | the landing: no agent connected, homes empty | install the plugin (or the Spec Kit extension) |
| 3 | install the plugin / the Spec Kit extension | the CLI sees `keel-connect`, and as a plugin skill |
| 4 | the CLI sees `keel-connect` | say *"keel connect"* |
| 5 | say *"keel connect"* | the heartbeat reads `awaiting_approval` |
| 6 | the heartbeat reads `awaiting_approval` | the launch log carries the code and the device URL |
| 7 | the launch log carries the code and the URL | **sign in at `/login?user_code=…`** (`return_to=/connect?user_code=…`) |
| 8 | the code is one this Keel issued, unapproved | **the code survived the login** — the founder lands back on `/connect` |
| 9 | `/connect` opens frame B; approve | the landing: no agent connected |
| 10 | say *"keel connect"* again → `already_connected` | **the door: `aiPath == "OWN"`, `creditsAvailable == null`, no credits line** |
| 11 | the executor startup line, `source=flag` | the code is one this Keel issued, unapproved |
| 12 | the journey | `/connect` opens frame B; approve |
| 13 | | say *"keel connect"* again → `already_connected` |
| 14 | | the executor startup line, `source=flag` |
| 15 | | the journey |

Two assertions are **added** (steps 8 and 10), one is **split** (§1.0's homes-are-empty half moves
*earlier*, before a single command has run; its no-agent-connected half moves to where the session
now is), and **not one is removed or loosened**.

### Requirements

- **FR-017** On the three CLI doors and on the Spec Kit road the founder signs in through
  `Auth.sign_in_with_code(founder, user_code)` — `/login?user_code=…`, *Continue with Google*,
  `return_to=/connect?user_code=…` — and the plain `/login` appears in S-012 **nowhere at all**.
  The Keel door keeps `/signup` and `return_to=/`, which is the whole of what makes it the Keel
  door.
- **FR-018** The code is asserted to have **survived the login**: the sign-in lands back on
  `/connect?user_code=…` and not on the project list (keel-cloud
  `canon/designs/google-sign-in-design.md` §10.6; S-010's own docstring says this assertion
  belongs to the connect journey, and this is that journey).
- **FR-019** After that sign-in and before the approval: `/v2/me.aiPath == "OWN"`,
  `creditsAvailable` is `null` (not zero — spec 044 assumption 8 makes null mean *this account has
  no balance* and absent mean *this server predates the field*), and the shell draws **no** credits
  line. One reader, `evals/preludes.py::own_ai_door`, is used by S-012, by the corpus riders and by
  S-013, because two copies of *which door did this account come through* is how two scenarios
  quietly stop meaning the same thing.
  It **asserts** only where the answer is about this run — a code travelled, `stack.is_remote`
  (so the founder was registered minutes ago and this sign-in wrote the row), and keel-cloud
  answers the field at all — and records which of the three it got otherwise. Locally every
  scenario is the one built-in *Eval Founder*, whose account may have been created by a run weeks
  ago against a database `make down` does not drop, and `ai_path` is immutable.
- **FR-020** keel-cloud's own `execution` report on a CLI cell's jobs must name **that cell's
  host** and never `api`. It is the same document FR-007 judges the Keel door by, read the other
  way round: a cell that had quietly become a `KEEL` account would say `api` there and nowhere
  else, while every runtime artefact went on saying exactly what it always said. Jobs that carry
  no `execution` at all are a **note** naming the bundled runtime's version (keel-runtime reports
  it from 0.5.0, spec 042), never a pass.
- **FR-021** The corpus riders (S-005/6/7) and S-013 start their runtime **before** they sign in,
  for the same reason and through the same door. A rider whose runtime reconnected on a credential
  its home already held prints no code; there is then no door to choose — keel-cloud reads `doorOf`
  only on the branch that **creates** an account, and a returning founder keeps whatever their row
  already says — so it signs in as a returning founder and the bundle says which of the two
  happened. S-013 does not take that branch: it resets the home itself and its own next assertion
  is `authorization_started`, so a missing code there is a product fault.

### What could not be moved, and why

`GET /v2/device-authorizations?user_code=` is **founder-session gated** — keel-cloud's
`SecurityConfig` gates the GET on `founderSession` while the two POSTs on the same base path are
`permitAll`, deliberately (spec 023 FR-001: *"a runtime has no credential yet when it starts or
polls a device authorization, but only the founder's own browser ever reads one back by code"*).
So *"is this a code this Keel issued, and is it unapproved"* **cannot** be asked before the
sign-in by anybody, including keel-web's own code story, whose time-left line simply does not
render until the founder is back. It moves to immediately after the sign-in and before the
approval, where it asserts exactly what it asserted before, and the scenario says why it is there
rather than leaving the next reader to rediscover it.

## And one more cell: the framing alone, for the effort comparison (2026-09-29)

**The founder:** *"I want to test only the framing-and-assumptions part -- the problem framed,
broken into lines and questions -- at different effort settings, not the whole journey, to keep
spend down."*

So the Keel door is bought twice a Saturday: once whole, and once at one stage.

- **FR-022** A second weekly cell, `macos-latest-keel-py3.13-short` -- same door, same OS, same
  Python, `legs = "short"`, `install = "none"` -- which signs up through `/signup`, starts a
  project, types the PROBLEM statement, and stops on the review card that keel-cloud's chained
  `PROBLEM_ASSUMPTIONS` produced. **Un-approved**: approving is the one thing the founder did not
  ask for.
- **FR-023** **`short` reaches the assumptions on a door with no host leg, and nowhere else.** Spec
  021 defined `short` as *the host leg plus the first model job*, and on the three CLI doors the
  host leg is the thing being measured -- the plugin from the marketplace, the three words, the
  device approval, the executor chosen by flag -- so a confirmation card is a fair place to stop,
  and **that is left byte for byte as it was**: the per-change cell and the Spec Kit cell buy
  exactly what they have always bought. The Keel door has no host leg, so a `short` that stopped
  after one model job there would have measured a claim with no lines under it, which is not a
  thing a founder ever sees. `agent_host.SHORT_REACHES_THE_ASSUMPTIONS` is the one place that says
  which, and `short_stops_at(host)` is the one sentence the bundle carries about it.
- **FR-024** The lines are read through `_read_the_lines`, **the same function the full journey
  calls at the same point** -- spec 021's own rule, one stage further along: the assertion the
  short run makes is *literally* the assertion the full run makes, not a copy that would have to be
  kept in step. It returns the card un-approved and the caller decides.
- **FR-025** **The expected spend, from the design.** `PROBLEM_FRAME` 30 credits +
  `PROBLEM_ASSUMPTIONS` 155 credits = **185 credits**, which is **$1.85 at list price** and
  60,000 + 307,500 = **367,500 µUSD ≈ $0.37** of Keel's own measured inference at `xhigh`
  (`ai-credits-design.md` §4.1's two rows, `n=21`, run of record
  `20260913T024219Z-instructions`) — against 1,250 credits and about $2.44 for the whole journey
  (§6.3). Ten framing runs cost less than two whole ones.
- **FR-026** **Nothing here pins an effort.** `output_config.effort` is keel-cloud's, `xhigh` by
  default (spec 045 FR-017); two runs of this cell against two settings differ by what keel-cloud
  was configured with, and a referee that set it would be measuring itself. What the cell owes the
  comparison is the **pair of numbers each run produced**, on the bundle, readable without opening
  a database: `facts.json` gains one line — *what the framing measured* — carrying the job count,
  the models that answered (`execution.model_used`), what keel-cloud says it paid
  (`actual_cost_micro_usd`, in µUSD and in dollars), and how long the founder waited by this
  harness's own clock.
- **FR-027** **No token counts, and their absence is said rather than filled in.** keel-cloud's
  `execution` object is five strings, a boolean and the cost (spec 045 FR-043; design §15 amendment
  1); FR-023 computes the cost *from* usage and reports only the cost. So `tokens` reads `null` with
  the reason beside it, and whatever timestamps the job row happens to carry are picked up when
  present and named absent when not — with the harness's own wall clock recorded either way,
  because it is the one timing that is always there.
- **FR-028** **`legs` becomes part of a cell's id.** Spec 021 kept it out on the grounds that *"the
  same cell appearing short in per_change and full in nightly is one runner job in two sets, not
  two cells"*. No cell is short in one set and full in another today — `per_change` is full,
  `nightly` is empty — and the case that does exist inverts it: two Keel's-AI cells in the **same**
  set are two runner jobs, two bundles, two artifacts and two founders in the twin's picker, and an
  id **is** a founder (design §4.3). So the id names everything that is not the default, which is
  the rule `install` already followed. The Spec Kit cell's id gains `-short` with it — truthfully:
  it buys two model jobs where the plugin cell beside it buys thirteen, and until today its id said
  nothing about that.
- **FR-029** The coverage rule is revised from *exactly one Keel's-AI cell in weekly* to **exactly
  one FULL one, with at most one SHORT one beside it** — both installing nothing, both weekly's
  alone, both refused in `per_change`. A third is somebody forgetting whose money this is; a second
  *full* one is paying twice for the same measurement.

### Success criteria

- **SC-008** `python -m matrix --set weekly` prints **ten** cells, the tenth being
  `macos-latest-keel-py3.13-short`, and `--set per_change` still prints exactly one.
- **SC-009** One dispatched run of that cell alone lands a bundle whose verdict is `PASSED`, whose
  transcript ends on the PROBLEM review card, and whose `facts.json` carries *what the framing
  measured* with a non-zero µUSD figure. *Not met; the founder's to spend.*

## Where the `execution` report lives (found by matrix run 36643795391)

The short Keel cell got its lines and failed on its **last** step -- *"a job of this project was
not answered by Keel's AI"* -- while keel-cloud's own log showed both jobs settled by the executor
with `host=api` and a cost. The harness was reading the wrong document.

`GET /v2/inference-interactions?project_id=` answers an array of `InteractionView`, and
`InteractionView.job` carries **five things**:

```
job: { job_id, turn_number, status, outcome, error{code, message} }
```

**There is no `execution` on it and there never was.** The report lives on
`InferenceJobDetail.execution`, from `GET /v2/inference-jobs/{jobId}` (keel-cloud
`canon/openapi-v2.yaml` on `045-keels-ai-executor`), whose `host` enum spec 045 FR-043 widened to
`[claude, copilot, codex, api]`. The key is `execution` and **not** `execution_payload`:
`ConnectDtos.JobDetail` declares it as a bare record component with no `@JsonProperty`, so Jackson
serialises the name as written.

- **FR-030** Every reading of an `execution` report goes through
  `harness/keel_host.py::jobs_with_their_execution(get_json, interactions)`, which fetches each
  job's own detail and carries the interaction's `screen` across (the only place `screen` exists,
  and what tells `PROBLEM_FRAME`'s 30 credits from `PROBLEM_ASSUMPTIONS`'s 155). `execution_facts`
  takes an `InferenceJobDetail` and its docstring says so; a test asserts no scenario passes it a
  list stub again.
- **FR-031** **The CLI doors' cross-check (FR-020) had the same bug, and worse.** It filtered on
  `job["execution"]`, a key the stub never has, so its list was always empty and the step asserted
  **nothing** while reading green. It now reads every job's detail, asserts on the ones that report
  a host, and records how many it read beside how many reported.
- **FR-032** `facts.json`'s *what the framing measured* sums the same `door_jobs` the assertion
  reads, so the cost on the bundle and the cost in the assertion are one number read once.

**Why this was the worst shape a reading can have**: the stub and the detail agree on `job_id`,
`status` and `error`, so a reader pointed at the wrong one does not raise, does not miss a key, and
does not say it could not answer -- it answers `None` to everything and reports `cost_reported:
false`, which looks exactly like a keel-cloud that has not reported yet.

## What this pass does not do

- **It does not add a fourteenth scenario, or a fourth named LLM place.** S-012 is widened by a
  door, exactly as spec 019 widened it by a host and spec 022 by a packaging. `AGENTS.md`'s third
  named place gains one sentence; its count does not change, and
  `tests/test_scenario_set.py::test_exactly_two_scenarios_are_live` is untouched.
- **It does not test the credit gate.** The 409 at New project (`INSUFFICIENT_CREDITS_FOR_NEW_
  PROJECT`, `required: 540`) and keel-web's refusal dialog are keel-cloud's `SC-006` and keel-web's
  own unit tests. Driving it here would mean **spending 1,000 credits to arrive at 539**, which is
  a four-dollar way to observe a number two test suites already observe for nothing. The cell reads
  the refusal's shape only if it meets one, and treats meeting one as a failure.
- **It does not test the grant budget, the ledger, the daily cap or a refund.** All four are
  keel-cloud's, all four are observable from a database this repository does not open, and three of
  the four would need a second account or a broken key to reach.
- **It does not assert a model id.** `model_requested` and `model_used` are recorded. Pinning
  `claude-sonnet-5` here would put a fact about keel-cloud's routing table into a bundle that
  cannot see the table, and spec 045's own Assumption 5 says the mismatch between `host: "api"` and
  a `claude`-row model is deliberate.
- **It does not switch an account.** There is no route that does (keel-cloud spec 044 FR-013), so a
  cell that walked both doors would be two founders, which is two cells.
- **It does not run on `per_change`, and it has no `short` cell.** `short` resolves — the length
  axis is the journey's, not the host's — but no set buys one, because the part of this journey
  that is new is the part `short` stops before.
- **It is not scored**, for S-008's, S-009's and S-012's reason: no attribute of `evals/policy.py`
  applies to a question about which door made an account.

## Success criteria

- **SC-001** `make unit` is green, and larger by the tests FR-015 asks for.
- **SC-002** `python -m matrix --set weekly` validates and prints **nine** cells, the ninth being
  `macos-latest-keel-py3.13`, and `--set per_change` still prints exactly one, unchanged.
- **SC-003** Collecting `evals/test_s012_journey_through_a_host.py` with `KEEL_JOURNEY_HOST=keel`
  in the environment resolves the host, the bundle name and the expected `execution.host` without
  touching a stack, a browser or a network.
- **SC-004** Against a twin running keel-cloud with spec 044 and spec 045 deployed and
  `KEEL_ANTHROPIC_API_KEY` set, one dispatched weekly run of this cell alone lands a bundle whose
  verdict is `PASSED`, whose `spend.json` names a per-job cost for every job, and whose founder in
  the twin's picker is labelled with the verdict. *Not met, and cannot be met today.*
- **SC-005** Against a twin whose executor is disabled, the same run lands a bundle whose verdict
  is `FAILED` and whose `failed_step` names `KEEL_AI_DISABLED`, **within one minute of the first
  statement being typed**, with no `TimeoutError` anywhere in the transcript. *Not met, and cannot
  be met today.*
- **SC-006** On a twin running keel-cloud spec 044, every CLI cell of the weekly set lands a
  bundle whose door step reads `aiPath: "OWN"` and `creditsAvailable: null`, and whose
  `credit_ledger` holds **no row at all** for that cell's founder (keel-cloud spec 044 FR-016;
  checked by the founder from the Mac, not by this repository, which does not open that database).
  *Not met: keel-cloud spec 044 is on a branch.*
- **SC-007** The same bundles' `execution` reports name `claude`, `copilot` or `codex` and never
  `api`. *Not met, for the same reason, and because the `execution` key itself needs keel-runtime
  0.5.0 on the cell.*
