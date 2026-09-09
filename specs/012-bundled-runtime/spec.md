# Feature Specification: The referee runs the runtime that travelled inside the skill

**Feature Branch**: `012-bundled-runtime`

**Created**: 2026-09-09

**Status**: Implemented — S-001 and S-008 green against a live stack, runs of record named in
[tasks.md](tasks.md) and `README.md`.

**Input**: keel-cloud `canon/designs/keel-skill-design.md` (design of record, 2026-09-08), §13
step 9: *"`stack/runtime.py` and `harness/connect.py` against the bundled runtime; `kill` →
`disconnect`; scenario **S-008** — the skill resolves and runs the runtime that travelled inside
it."* The sections this feature is a referee of are §3.1 (what ships), §3.2 (resolution order),
§6.3 (the home follows the address), §7 (the seven-outcome contract with `environment`), §10
(testing), §11 (disconnect) and acceptance row **A-7**.

The siblings, read at these commits:

| Sibling | Branch | Commit | What this feature depends on |
|---|---|---|---|
| keel-connect-skill | `master` | `5ced793` | spec 003: `make runtime`, the gitignored `keel_runtime/`, `scripts/_runtime_location.py`'s checkout → bundled → PATH order, the seven shapes with `environment`. `scripts/keel_disconnect.py` (its spec 002) was **present in the working tree, not yet committed**, when this landed. |
| keel-runtime | `master` | `a05f9bc` | spec 004: the derived home, and `home`/`base_url`/`environment`/`executor`/`executor_on_path` on `status`. Spec 003: `keel disconnect` and its four outcomes. `_say_goodbye` is a **deliberate no-op** here — `CloudClient` has no `end_agent_session` yet. |
| keel-cloud | `master` | `d393511` | spec 033's goodbye endpoint (present, and unreachable until keel-runtime calls it); `keel.v2.connect.presence-threshold` = 90 s, which is what a disconnect without a goodbye waits out. |

## What changes, stated first

**Every scenario in this repo has been starting the wrong runtime.** `harness/connect.py` passed
`--runtime-path <the keel-runtime checkout>` to keel-connect-skill's script, which is rule 1 of
that script's resolution order — the development override. A founder is on rule 2: the
`keel_runtime/` package that travelled *inside the skill*, put there by `make runtime` and
gitignored in that repo. The referee was refereeing a path no founder is ever on, and every green
run said something true about a runtime nobody ships.

Four things follow, and they are the whole feature.

1. **The bundled runtime is what runs.** `stack/runtime.py` runs
   `<keel-connect-skill>/keel_runtime/` on `PYTHONPATH`, and `harness/connect.py` passes no
   `--runtime-path` at all. `KEEL_RUNTIME_PATH` survives only as what the design calls it: an
   optional development override — which this stack now **scrubs from the environment** rather
   than sets.
2. **`make up` refuses to boot without it.** The bundled package is generated and gitignored, so a
   checkout of keel-connect-skill nobody has run `make runtime` in has no runtime inside it. The
   stack fails fast, naming the one command that fixes it.
3. **`kill` became `disconnect`.** `make down` and `stop_runtime` ask the runtime to go — through
   keel-connect-skill's own `keel_disconnect.py` when it exists, the bundled runtime's own command
   when it does not — and read the outcome that proves it went.
4. **S-008 walks the founder's path end to end** and asserts the two things no other scenario can:
   that the skill resolves the runtime it carries with nothing pointing at a checkout, and that
   `status` now says which executor, which home and **which Keel**.

## Clarifications

### The home: derived, or isolated? — **isolated, and it must still name its Keel**

The design's rule (§6.3) is that the home follows the address: with no `KEEL_HOME`, keel-runtime
derives `~/.keel/localhost-18080/`. Taking that here would have put this repo's runs under the
founder's own `~/.keel/`.

**Decision: the stack keeps setting `KEEL_HOME`**, to `runs/.stack/keel-home[-<profile>]/`. Three
reasons, none of them a disagreement with the design:

- `KEEL_HOME` is an **override** in §6.3, not a violation — "`KEEL_HOME` and `--home` still win
  outright".
- `make up` **wipes** the home it owns, so a credential or heartbeat from a prior run can never
  make the landing read *Agent connected* before the smoke has connected (spec 005). A referee
  that wiped `~/.keel/localhost-18080/` would be deleting a founder's own credential every time it
  booted.
- Two profiles must never share a home (relay-design.md §12.5, the account-collision incident).
  Derivation happens to give eval `~/.keel/localhost-18080/` and playground
  `~/.keel/localhost-18081/` — two directories, but by consequence of a port number rather than by
  a rule this repo states and holds.

**What the decision costs, and what it pays.** An isolated home is a home whose Keel nobody named:
`keel status` takes `--home` and **no `--base-url`** (keel-runtime's own parser), so the address it
reports can only come from `KEEL_BASE_URL` (scrubbed here), the built-in cloud default (empty until
the design's step 8) or the home's own `config.json`. So `make up` writes that file:
`{"base_url": "http://localhost:<this profile's port>"}`. FR-004 then asserts the other half of the
design's promise — `status.environment` reads `localhost:18080`, on every profile, in every
scenario — so an isolated home can never quietly become an *unnamed* Keel.

### Does the stack build the bundled package, or check for it? — **check, and name the command**

`make -C ../keel-connect-skill runtime` would have made `make up` self-sufficient. It is not run,
for two reasons that are both about whose repository it is:

- **This repo owns no product code and never writes to a sibling** (README, AGENTS.md). A `make up`
  that writes into keel-connect-skill has crossed that line for convenience.
- **That target refuses on a dirty keel-runtime checkout**, by design (it would otherwise stamp
  `RUNTIME_VERSION` with a commit whose working tree is not what was copied). A sibling somebody is
  working in is dirty most of the time — keel-runtime was, all through this feature's own
  implementation — so a referee that ran it would turn another agent's uncommitted work into this
  stack's boot failure.

So the gate is a check, and its message is the command.

### What if `scripts/keel_disconnect.py` has not landed? — **prefer it, fall back to the runtime**

keel-connect-skill's spec `002-keel-disconnect` was in that repo's working tree, uncommitted, while
this feature was implemented. `stack.runtime.disconnect` therefore **prefers the script when the
file exists** and falls through to `<bundled runtime> disconnect` when it does not — the same
command the script shells, one layer lower, answering the same four outcomes. Both names of each
outcome are accepted (`stopped`/`disconnected`, `timeout`/`did_not_stop`), because the two
contracts name them differently on purpose: the skill speaks the founder's vocabulary.

**It landed while this was being written** — keel-connect-skill reached `d5469a0` (its specs 002
and 004) during the live runs — so the runs of record took the script
(`via: keel-connect-skill/scripts/keel_disconnect.py`), and the fallback stays anyway: it is the
same command, and a stack that cannot tear a runtime down because a sibling moved is not a stack.

## User Scenarios & Testing

### US1 — the referee runs what a founder runs (P1)

A referee brings the stack up and runs the smoke. The runtime that starts is the one inside the
skill; no environment variable and no flag names a checkout; the reply names which Keel it reached.

**Acceptance**

1. `make up` prints a `bundled-runtime` gate naming the package and its `RUNTIME_VERSION`.
2. `make up` in a workspace where `make runtime` has never run **fails**, printing
   `make -C ../keel-connect-skill runtime`.
3. S-001's connect leg returns `authorization_started` with `environment == "localhost:18080"`.
4. No `--runtime-path` appears in any command this repo builds, and `KEEL_RUNTIME_PATH` is absent
   from every environment it hands a child.

### US2 — S-008, the runtime that travelled (P1)

**Acceptance** (`evals/test_s008_bundled_runtime.py`)

1. The bundled package is present and no `KEEL_RUNTIME_PATH` reaches the script.
2. `status` before anything runs: `running: false`, plus `home`, `base_url`, `environment`,
   `executor`, `executor_on_path` — with `environment == "localhost:18080"`.
3. A copy of the skill tree **with `keel_runtime/` removed** and an **empty `PATH`** answers
   `runtime_unavailable`, `environment: null`, exit 0, and a message naming neither
   `KEEL_RUNTIME_PATH`, nor `--runtime-path`, nor `pip install` (invariant X-4). This is the
   negative control that makes assertion 1 a proof: with rules 1 and 3 of the resolution order both
   impossible, a runtime that answers can only have come from rule 2.
4. The oldest interpreter on the machine runs the whole script and answers a contract outcome.
   Below 3.9 that outcome is `python_too_old`; at or above it, the floor itself is what is observed
   and the skip is **recorded with its reason** (design §10, C-11).
5. Connect → `authorization_started` (code, URI, pid, log file) → approved in a real browser at
   keel-web's `/connect` → `/v2/me` reads `agent.connected` within 30 s.
6. Saying it again → `already_connected`, carrying `agent_session_id` and `last_heartbeat_at`,
   carrying `environment`, and **not** carrying `base_url` (the one shape that changed, §7).
7. `status` now reads `running: true` and its `agent_session_id` is the one the skill reported.
8. Disconnect → `disconnected`/`stopped` with a pid; disconnect again → `not_running`.
9. keel-cloud learns the agent is gone by goodbye if the runtime has one, by staleness otherwise —
   and either way **local truth is first**: `keel status` reads not-running the moment disconnect
   answered.

## Requirements

- **FR-001** `stack/runtime.py` runs the runtime bundled inside keel-connect-skill
  (`<skill>/keel_runtime/`), as `<this interpreter> -m keel_runtime` with the skill root on
  `PYTHONPATH` and `PYTHONSAFEPATH=1`. It never runs the keel-runtime checkout. `KEEL_RUNTIME_PATH`
  remains an optional override *of the skill's own resolution*, and this repo never sets it.
- **FR-002** `make up` gates on the bundled package and fails fast with `make -C <skill> runtime`
  when it is absent. The stack never writes to a sibling repository.
- **FR-003** `make down` and `stop_runtime` disconnect rather than kill, and assert the outcome:
  `stopped`/`disconnected` or `not_running`/`stale_pid_cleared` is success,
  `timeout`/`did_not_stop` is a failure by name. Teardown stays idempotent and never raises on it.
- **FR-004** Every child of this stack that can reach a runtime is launched with
  `KEEL_RUNTIME_PATH`, `KEEL_HOME` and `KEEL_BASE_URL` removed from its environment; the home this
  stack owns carries a `config.json` naming this profile's Keel; and `status.environment` reads
  `localhost:<this profile's cloud port>`.
- **FR-005** `harness/connect.py` parses all **seven** shapes of the skill's contract, including
  `python_too_old` (its own exception) and `environment` on every one of them. S-001's connect leg
  asserts `environment`.
- **FR-006** `evals/test_s008_bundled_runtime.py` exists, is deterministic, is not `live`, and
  asserts US2's nine points.
- **FR-007** A run bundle names the runtime that actually ran: `versions.json` carries the bundled
  package's path, presence and `RUNTIME_VERSION` (its commit cannot come from `git` — it is
  gitignored in the skill).
- **FR-008** `make unit` grows, and the scenario set's own test knows there are eight scenarios.

## Success Criteria

- **SC-001** `make unit` green, up from 377 (landed at **407**).
- **SC-002** `make eval K=s001` green against a live stack, with `environment` asserted.
- **SC-003** `make eval K=s008` green against a live stack.
- **SC-004** `make down` reports a disconnect outcome, not a signal.
- **SC-005** Every cross-repo gap found is a `runs/DRIFT.md` entry with a bundle, never a
  workaround.

## What this feature deliberately does not do

- **It does not touch the keel-runtime checkout's role as a thing to *read*.** `stack.toml` keeps
  `keel_runtime`: `harness/canary.py` reads its cap defaults and `instructions/prompts.py` imports
  its `build_prompt`. Reading a sibling's source is this repo's business; running a copy of it as
  though it were shipped is not.
- **It does not add the packaging beds.** `dist/`, both hosts, both architectures and S-009 are the
  design's step 10, spec `013-skill-distribution`.
- **It does not make the goodbye work.** That is keel-runtime's spec 003 second pass. S-008
  observes which of the two paths keel-cloud is on and records the debt (`runs/DRIFT.md` #47).
