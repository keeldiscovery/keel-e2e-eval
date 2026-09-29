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
