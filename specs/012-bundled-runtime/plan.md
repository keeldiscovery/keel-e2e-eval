# Implementation Plan: The referee runs the runtime that travelled inside the skill

**Branch**: `012-bundled-runtime` | **Date**: 2026-09-09 | **Spec**: [spec.md](./spec.md)

**Input**: [spec.md](./spec.md), keel-cloud `canon/designs/keel-skill-design.md` (§3.1, §3.2, §6.3,
§7, §10, §11, §13 step 9, A-7), and the two sibling contracts this feature calls across:
keel-connect-skill `specs/001-keel-connect-check/contracts/skill-script-output.md` (seven shapes,
rewritten by its spec 003) and keel-runtime
`specs/003-keel-disconnect/contracts/disconnect-cli-output.md` (four outcomes).

**On the artefact set.** `spec.md` + `plan.md` + `tasks.md`, the shape specs 004–008 use. This
feature changes four stack/harness modules, adds one scenario and moves no versioned constant —
`POLICY_VERSION` does not move, because nothing about *scoring* changed. It needs no `research.md`
(the two contracts are read, not researched), no `data-model.md` (it introduces no data), and no
`contracts/` of its own (it is a **consumer** of two contracts that live in the repos that own
them; copying either here would be the fourth copy this design exists to prevent).

## Summary

Point the referee at the runtime a founder gets. `stack/runtime.py` stops shelling the keel-runtime
checkout and runs `<keel-connect-skill>/keel_runtime/` on `PYTHONPATH`; `harness/connect.py` stops
passing `--runtime-path` and starts scrubbing `KEEL_RUNTIME_PATH`; `make up` gains a gate on the
bundled package and `make down` swaps a SIGTERM for a `disconnect` whose outcome it reads; S-001
asserts which Keel it reached; and a new S-008 walks the whole founder path — resolve, status,
connect, approve, say it again, disconnect, say that again — with the negative controls that make
"it resolved the bundled one" a proof rather than a hope.

**Technical approach**: change the *invocation*, not the interface. Every scenario already goes
through `harness/connect.py`, so pointing that one module (and `stack/runtime.py` beneath it) at
the bundled package moves all eight scenarios at once, and the two sibling contracts stay the only
things this repo depends on.

## Technical Context

**Language/Version**: Python 3.11+, as `stack/`, `harness/` and `evals/` already are. The
*subject* has a 3.9 floor and S-008 measures it on whatever the oldest interpreter on the machine
is; the harness itself does not.

**Dependencies**: unchanged. No new package, and nothing new in `requirements.txt`.

**Testing**: `make unit` for everything stackless (offline, against a temporary directory shaped
like keel-connect-skill), `make eval K=s001|s008` for the live legs.

**Constraints**: this repo owns no product code, never writes to a sibling repository, and reports
cross-repo gaps as `runs/DRIFT.md` entries with a bundle.

## The five changes, and why each is where it is

### 1. `stack/runtime.py` — which runtime, which home, and how it stops

The module keeps its three public verbs (`reset`, `status`, `is_gate_clear`) and swaps `kill` for
`disconnect`. New: `bundled_runtime_dir`/`_present`/`_version`, `require_bundled_runtime`,
`scrubbed_env`/`runtime_env`, `ensure_home_names_keel`, and the two outcome vocabularies.

`_run_runtime` is the one place `-m keel_runtime` is spelled: `cwd` is the skill root and
`PYTHONPATH` carries it, which is exactly what keel-connect-skill's own `_runtime_location.py`
does — including the `cwd` half, which that file documents as a **deviation forced by the floor**
(on 3.9 `python -m` prepends the working directory ahead of `PYTHONPATH`, so a stray `keel_runtime/`
in the cwd would shadow the resolved one). Copying the mechanism rather than inventing one means
the referee's `status` and the founder's `connect` resolve the same package by the same rule.

### 2. `stack/lifecycle.py` and `stack/cli.py` — the gate, and how it fails

`boot` gains one gate before the runtime-home reset, so a missing package is a `[up] failed:` line
with a command in it rather than a `runtime_unavailable` from inside a scenario twenty minutes
later, where it would read as a product defect. `cli.main` adds `BundledRuntimeMissing` to the
exceptions it turns into exit 1.

`teardown` calls `runtime.disconnect` and prints the outcome and which path answered it. A
`did_not_stop` prints a warning and does **not** raise: a teardown that raises leaves Postgres and
two JVMs behind, which is a worse failure than the one it is reporting.

### 3. `harness/connect.py` — the seven shapes, and a scrubbed environment

Two lines and one exception. `--runtime-path` leaves the argv; `env` becomes
`stack_runtime.scrubbed_env(env_extra)`. Dropping the flag alone would not have been enough —
this repo is worked on from shells that export `KEEL_RUNTIME_PATH` (keel-connect-playground's
walk-through environment is one), and an inherited one would put the checkout straight back, in a
run that says it did not. `PythonTooOld` is the seventh shape's own exception, because "the
interpreter is below the floor" is a fact about this machine and not a runtime that could not be
found.

`stop_runtime` loses its poll loop. It had one because a SIGTERM is fire-and-forget; a
`disconnect` that answers `stopped` has already observed the pid leave (contract guarantee 4), so
the wait is the runtime's, not the harness's. `status` is still read afterwards — an outcome and a
heartbeat disagreeing would itself be a finding.

### 4. `evals/test_s001_smoke.py` — one assertion

`environment == f"localhost:{stack.cloud_port}"` on the connect leg. One line that says the skill
reached this profile's own keel-cloud, and not the founder's, the playground's, or none at all.

### 5. `evals/test_s008_bundled_runtime.py` — the new scenario

Ordered so that each assertion is cheap before it is expensive: what is on disk, then `status`,
then the two controls that need no stack (the stripped tree, the floor interpreter), then the
browser walk, then the door out, then what keel-cloud knows.

**The negative controls are the design of this scenario.** "It resolved the bundled runtime" is
not directly observable through the contract — `source` is deliberately not an outcome key
(skill contract, *Which runtime runs*). So it is proved structurally: no `KEEL_RUNTIME_PATH` in the
environment kills rule 1, an empty `PATH` kills rule 3, and a tree with `keel_runtime/` removed
must then answer `runtime_unavailable`. Whatever answers when the package *is* there came from
rule 2.

## Where the risk is

| Risk | What it would look like | What is done about it |
|---|---|---|
| The bundled copy is stale against keel-runtime's master | A scenario fails on behaviour that was fixed a week ago | `RUNTIME_VERSION` is printed by the `make up` gate and written into every run bundle (FR-007), so the run names its runtime |
| An ambient `KEEL_*` decides something the run then reports differently | A green run whose `environment` describes another Keel | `scrubbed_env`, plus FR-004's assertion on `status.environment`, plus `config.json` in the home |
| keel-connect-skill's `keel_disconnect.py` lands, changes shape, or is reverted | `make down` stops reaping the runtime | Prefer the script, fall back to the runtime's own command, accept both outcome vocabularies |
| The goodbye lands mid-flight in keel-runtime | S-008's step 9 asserts the wrong branch | The step observes which path happened and asserts only what is true on both (**local truth first**) |

## What is deliberately not here

- No `research.md`: the two contracts were read at named commits; there was nothing to discover.
- No changes to `evals/policy.py` and no `POLICY_VERSION` bump: nothing about scoring moved.
- No amendment to keel-cloud's `canon/CANON.md` ledger: S-008 proves *how the runtime got there*,
  which is a fact about the four applications rather than a journey moment. §1.0 stays S-001's.
