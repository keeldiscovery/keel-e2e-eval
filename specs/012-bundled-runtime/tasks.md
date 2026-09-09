# Tasks: The referee runs the runtime that travelled inside the skill

**Input**: [spec.md](spec.md) (FR-001..008, SC-001..005, the three clarifications) with
[plan.md](plan.md).

**The siblings, read at**: keel-connect-skill `5ced793`, keel-runtime `a05f9bc`, keel-cloud
`d393511`. Two of them moved *while this feature was implemented* — keel-runtime to `638c0dc`
(spec 005's Copilot executor, and spec 003's second pass making the goodbye real) and
keel-connect-skill to `d5469a0` (its specs 002 and 004) — which is what the referee floating at
sibling HEADs looks like from the inside, and what `runs/DRIFT.md` #47 is about.

**Rules** (AGENTS.md): this repo owns no product code and never fixes the product — a cross-repo
finding is a `runs/DRIFT.md` entry with a bundle, starting at **#47**. `POLICY_VERSION` does not
move: nothing in `evals/policy.py` is touched. The scenarios stay deterministic and the two named
LLM exceptions do not change in number or in name.

---

## Phase 1: the stack runs the bundled runtime

- [X] T001 `stack/config.py`: `bundled_runtime_path`, `disconnect_script_path`, `cloud_base_url`
      on `StackConfig`. `keel_runtime` (the checkout) stays — it is still what `harness/canary.py`
      and `instructions/prompts.py` *read*.
- [X] T002 `stack/runtime.py` rewritten (FR-001): `_run_runtime` runs
      `<this interpreter> -m keel_runtime` with the skill root as `cwd` **and** on `PYTHONPATH`,
      with `PYTHONSAFEPATH=1` — the mechanism keel-connect-skill's own `_runtime_location.py`
      uses, including its documented floor deviation, so the referee's `status` and the founder's
      `connect` resolve one package by one rule.
- [X] T003 `stack/runtime.py`: `bundled_runtime_dir` / `_present` / `_version`,
      `require_bundled_runtime` and `BundledRuntimeMissing` (FR-002). The exception's message
      carries `make -C <skill> runtime` **and the reason this stack does not run it**.
- [X] T004 `stack/runtime.py`: `scrubbed_env` / `runtime_env` (FR-004). `KEEL_JOB_*` deliberately
      survives — `runs/DRIFT.md` #46 settled that.
- [X] T005 `stack/runtime.py`: `reset` writes `config.json` naming this profile's Keel, and
      `ensure_home_names_keel` guarantees it non-destructively for a session that attached to an
      older `make up`. **Found while implementing**: `keel status` takes no `--base-url`, so this
      file is not a convenience — it is the only remaining source of the address for an isolated
      home (`runs/DRIFT.md` #48).
- [X] T006 `stack/runtime.py`: `kill` → `disconnect` (FR-003), preferring
      keel-connect-skill's `scripts/keel_disconnect.py` and falling back to the bundled runtime's
      own command, accepting both outcome vocabularies, and never raising.
- [X] T007 `stack/lifecycle.py`: the `bundled-runtime` gate in `boot`; `teardown` disconnects,
      prints the outcome and the path that answered it, and warns without raising on
      `did_not_stop`. `stack/cli.py` turns `BundledRuntimeMissing` into `[up] failed:` and exit 1.

## Phase 2: the harness and the scenarios

- [X] T008 `harness/connect.py` (FR-005): no `--runtime-path`; `scrubbed_env`; `PythonTooOld` for
      the seventh shape; `stop_runtime` reads the disconnect outcome instead of polling after a
      SIGTERM, and returns it.
- [X] T009 `harness/evidence.py` (FR-007): `versions.json` carries
      `keel-runtime (bundled, the one that runs)` with its path, presence and `RUNTIME_VERSION`.
- [X] T010 `evals/test_s001_smoke.py`: the connect leg asserts
      `environment == f"localhost:{stack.cloud_port}"`.
- [X] T011 `evals/test_s008_bundled_runtime.py` (FR-006): step 0 (put the home back the way
      `make up` leaves it), the on-disk assertions, `status`'s five keys, the stripped-tree and
      floor-interpreter controls, the device flow, `already_connected`, the two disconnects, and
      the goodbye-or-staleness probe.
- [X] T012 `tests/test_bundled_runtime.py` — 26 stackless tests. `tests/test_scenario_set.py`
      knows there are **eight** scenarios.

## Phase 3: what the live runs found

- [X] T013 **keel-web moved and S-001 had not followed it.** `c807634` (*"The correction panel is
      asked for, not always open — founder change, playground"*) made the review card's correction
      composer open on a *Change a line* link. S-001 was asserting the composer was already there
      and went red on it, before this feature's own legs were reached. The page object follows the
      product: `CorrectionChat.is_offered()` / `.ask()`, a placeholder matched on its opening words
      rather than in full, and `send()` opens the panel on its way past. S-001 and S-004 assert the
      journey moment (*a founder who disagrees with a line has somewhere to say so*) and click the
      link. **Not a `runs/DRIFT.md` entry**: the product changed on purpose and the referee had not
      caught up, which is this repo's own maintenance.
- [X] T014 **A false green, caught by the next assertion** (`runs/DRIFT.md` #47). S-008's first
      draft asserted `/v2/me`'s `agent.connected` after approving the device; it passed instantly,
      on the *previous* scenario's session, still inside keel-cloud's 90-second presence threshold.
      The scenario now waits on `keel status` — local truth, against a home it wiped itself — and
      then asserts `/v2/me` names **that** `agentSessionId`.
- [X] T015 **A run with nothing to score was scoring 0.0.** Every one of the policy's four
      attributes is *not applicable* to S-008, and `compute_run_score` returned `0.0` for an empty
      weight total — "as bad as a run can be" about a run that measured nothing of that kind, and
      the opposite of the rule the same function already applies to a single absent category. It
      returns `None` now and the report reads **not scored**. `POLICY_VERSION` does not move: no
      check, weight or waiver changed, and every run with one applicable category scores exactly
      what it scored before (asserted).
- [X] T016 `runs/DRIFT.md` **#47** (the bundled runtime is behind master by the goodbye; the
      remedy is `make runtime` in keel-connect-skill) and **#48** (the referee had been starting
      the checkout, and an ambient `KEEL_RUNTIME_PATH` would have put it back).

## Phase 4: the runs of record

One stack session, `make up` → `make eval K=s001` → `make eval K=s008` → `make down`, on
keel-cloud `d393511`, keel-web `b0a5015`, keel-runtime `638c0dc` and keel-connect-skill `d5469a0`,
with the **bundled runtime `0.1.0+a05f9bc`** — which the bundle names, and which #47 is about.

| Scenario | Run | Result |
|---|---|---|
| S-001 smoke | `20260909T050008Z-s001-smoke` | **PASSED, 5.0/5** |
| S-008 bundled runtime | `20260909T050141Z-s008-bundled-runtime` | **PASSED, not scored** |

- [X] T017 `make unit` green: **377 → 407**.
- [X] T018 `make up` prints the `bundled-runtime` gate; `make down` prints
      `keel-runtime: not_running (via keel-connect-skill/scripts/keel_disconnect.py)` — the
      disconnect path, live, through the founder's own script.
- [X] T019 `README.md` and `AGENTS.md` amended: eight scenarios, the runtime the stack runs, and
      the runs of record above.

## What is left undone, and where it goes

- **The bundled copy is stale** (`runs/DRIFT.md` #47). The fix is `make runtime` in
  keel-connect-skill and it is that repo's to make; this stack names the command and refuses to
  guess.
- **`python_too_old` has never been observed**, because no interpreter below 3.9 exists on this
  machine. S-008 records the skip with its reason and asserts the floor instead. It becomes real
  on the design's step 10 beds (`debian:11-slim` is the floor, and a 3.8 image would be the gate).
- **S-009 and the packaging beds** are spec `013-skill-distribution`, the design's step 10.
- **The instruction eval and S-004** were not run: neither is touched by this feature and both
  cost real money.
