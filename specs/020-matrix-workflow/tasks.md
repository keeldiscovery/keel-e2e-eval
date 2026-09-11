# Tasks: the matrix workflow

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Branch**: `matrix-workflow`

`make unit`: **765** before, **814** after, green. `actionlint` 1.7.12 (with shellcheck 0.11):
clean on all five workflow files. No AWS call, no image pushed, no model asked anything.

## Phase 1 — read before writing anything

- [X] T001 keel-cloud `canon/designs/e2e-matrix-design.md` in full, and §5, §6, §8, §10, §11, §12,
      §14 twice — the axes, the three schedules, what a cell is, what the deploy job does, where a
      verdict goes, what a green matrix is allowed to trigger (nothing).
- [X] T002 The §3/§4.2 amendments spec 036 made: the twin's own instance role, the gate in front of
      `/oidc/identities*`, the stripped `X-Keel-Gate-User`, and **the CI role carrying no
      `ec2:Describe*`** — which is why `KEEL_INSTANCE_ID` and `KEEL_ELASTIC_IP` are repository
      variables and not a lookup.
- [X] T003 `specs/017-remote-profile/`, `specs/018-gated-registry-stub/`,
      `specs/019-journey-through-a-host/` — what a cell already has: the three `KEEL_REMOTE_*`
      URLs, the gate credential, `register_cell_identity`, `--gated`, `KEEL_JOURNEY_HOST`.
- [X] T004 `stack/remote.py` and `stack/config.py` — `REMOTE_CELL_VAR`, `remote_urls`,
      `remote_gate` (half a credential is a `ConfigError`), and `identity_to_sign_in_as`, which is
      the one call a scenario makes.
- [X] T005 `evals/test_s012_journey_through_a_host.py` — how `KEEL_JOURNEY_HOST`,
      `KEEL_REMOTE_CELL` and `KEEL_COPILOT_MODEL` are read, and that the Copilot pin is
      `gpt-5.6-luna` (C-5, `runs/DRIFT.md` #59) while Claude has no pin at all.
- [X] T006 `stack/containers/oidc/Dockerfile` and `make oidc-image` — its `TAG`, `PUSH`,
      `PLATFORM`, `OIDC_IMAGE_REPO` and its `DOCKER_HOST` default, which is the founder's Colima
      socket and must be overridden on a runner.
- [X] T007 `Makefile` end to end — `venv`'s guard (`$(PY)` exists → nothing reinstalls), `eval`,
      `eval-live`'s `HOST`/`PROFILE`, and the **unquoted `-k $(K)`**, which a multi-scenario cell
      would have split into four arguments.
- [X] T008 keel-cloud `deploy/bin/common.sh` (`apply_target`, `KEEL_PROFILE`, `instance_id`,
      `elastic_ip`, `read_deployed_tag`) and `deploy/bin/deploy.sh` (its eight steps, its
      preconditions, `KEEL_WEB_DIR`) and `deploy/README.md` Part 3.
- [X] T009 keel-cloud `deploy/bin/provision.sh` step 9 — the `keel-ci-deploy` role's one trusted
      subject and its five statements, and **both ECR repositories being `IMMUTABLE`**, which is
      what decided how the redeploy path behaves.
- [X] T010 keel-runtime `.github/workflows/acceptance.yml` — the per-OS CLI installs, the 1.0.83
      pin with its `latest` fallback, and the two secrets' names and mapping.
- [X] T011 keel-cloud `.github/workflows/deploy-image.yml` — the repository family's existing idiom
      for an inert workflow (`if: ${{ vars.X != '' }}`) and for OIDC into AWS.

## Phase 2 — measure before writing what depends on it

- [X] T012 **Is keel-e2e-eval still private?** No: `gh repo view` says **PUBLIC**. §10's runner-minute
      arithmetic and decision 10 are therefore closed, and the spec says so rather than repeating a
      bill nobody pays. keel-cloud and keel-web are still **private**, which is what forced T013.
- [X] T013 **Can a runner check out keel-cloud and keel-web?** Not with `GITHUB_TOKEN` — it is
      scoped to the repository the workflow is in. A fine-grained read-only token is the smallest
      answer, and `KEEL_SIBLINGS_TOKEN` is recorded in the spec as a deviation, with the job
      failing by name when it is missing.
- [X] T014 **Does `actions/checkout` take a short sha?** No — `ref` must be a full sha or a ref
      name, and `/keel/staging/deployed-tag` holds a short one. So keel-cloud is checked out at
      master with `fetch-depth: 0` and the right commit is reached with `git checkout`.
- [X] T015 **Does `deploy.sh` work with environment credentials?** No: every call passes
      `--profile "$KEEL_PROFILE"`, and botocore drops the environment provider when a profile is
      named. Hence the `aws configure set` step and `AWS_PROFILE=default`.
- [X] T016 **Is the harness runnable on Python 3.9?** No — `stack/config.py` imports `tomllib`
      (3.11+). So the cell's Python is the **runtime's** and the harness gets its own 3.12, which
      is also what the acceptance beds already do (the container's Python is the floor; the
      referee's is not).
- [X] T017 **Do the corpus scenarios cost a model request?** No: S-005/6/7 are not marked `live`
      and drive the frozen corpus through the real screens. That is what makes decision 11 free,
      and why a cell carries two selectors (`live_k`, `eval_k`) rather than one.

## Phase 3 — the data and its reader

- [X] T018 `matrix/cells.toml`: `[axes]`, `[scenarios]` (`default`, `live`) and the three sets.
- [X] T019 The Python-axis reconciliation, written into the file's header rather than decided
      silently: §5.2 and §10 count eighteen and six, §4.3's picker sample shows `py3.12`, and
      3 × 2 × 2 is neither.
- [X] T020 `matrix/cells.py`: `Cell` (frozen; `id`, `k`, `as_dict`), `Matrix` (`cells`,
      `as_matrix`, `product`).
- [X] T021 `load()` — every problem in one message, never the first one found.
- [X] T022 `coverage_problems()` — §5.2's three rules as checks, run by `validate()`, so
      `make matrix-check` enforces them and not only `make unit`.
- [X] T023 `render()` and `main()`: `--set`, `--cells`, `--json`, `--file`; exit 2 with the reason
      on a bad file.
- [X] T024 `matrix/__init__.py`, `matrix/__main__.py`.

## Phase 4 — the tests

- [X] T025 `tests/test_matrix_cells.py`, 49 tests. The coverage half asserts the **real**
      `cells.toml`: the axes, the three sets' sizes, per_change's OS × host coverage and its
      3.9/3.13 split, nightly's Ubuntu-only rule and its one corpus-carrying Claude cell, weekly
      being the product, ids unique everywhere, every cell running something.
- [X] T026 The reader half: a missing file, broken TOML, an OS/host/python outside its axis, a
      missing axis, an unknown key, a set naming a cell twice, an empty scenario list, a missing
      set, and **every problem reported at once**.
- [X] T027 The CLI half: the three sets printed, one set printed, `--json` shaped as
      `strategy.matrix` takes it, `--cells` narrowing and keeping the caller's order, an unknown
      cell raising by name, exit 2 on a bad file.

## Phase 5 — the workflow

- [X] T028 `select`: the event → set mapping (two crons, two sets; `workflow_dispatch`'s input;
      everything else `per_change`), the `{repo, sha, why}` triple, and `python -m matrix --json`.
- [X] T029 The gate: `KEEL_STAGING_ENABLED != 'true'` → `enabled=false`, one line of summary,
      green, and every expensive job `needs` it.
- [X] T030 `concurrency: matrix-${{ client_payload.repo || github.repository }}` with
      `cancel-in-progress` — §6.2's debounce, in the receiver.
- [X] T031 `deploy-staging` on `ubuntu-24.04-arm`: the siblings' token guard, the three checkouts,
      Java 21 and Node 22, the tools `deploy.sh` names (aws CLI installed when the arm image lacks
      it), OIDC into `keel-ci-deploy`, the profile shim, the tag decision, ECR login.
- [X] T032 The `keel-oidc` image: a content-addressed tag, `describe-images` as the "has the stub
      changed" question, `make oidc-image … PUSH=1` with the runner's own `DOCKER_HOST`, and
      `/keel/staging/oidc-image-tag` written every run.
- [X] T033 `deploy.sh --target staging <tag>` with `KEEL_INSTANCE_ID`, `KEEL_ELASTIC_IP` and
      `KEEL_WEB_DIR`; skipped, with a reason, when the tag is already in an immutable ECR.
- [X] T034 §6.3's gate: `/v2/me` 401 **and** the discovery document 200, polled, failing with both
      codes named.
- [X] T035 `cell`: `fromJSON` of `select`'s output, `fail-fast: false`, the two Pythons, Node 22,
      the venv from the harness interpreter, Playwright's chromium.
- [X] T036 The host CLI, installed exactly as `acceptance.yml` installs it, with the two
      organisation secrets under the names that file uses.
- [X] T037 The run step: `make eval-live` when `make` exists and the same pytest line when it does
      not (Windows), both selectors, the exit status of either failing the cell.
- [X] T038 The collect step (`if: always()`): the `runs/` diff, `_cell/runs/`, `rows.json`, the
      job-summary row from each bundle's `verdict.json`.
- [X] T039 The two artifacts: `runs-<cell>` for 30 days (§6.4) and `row-<cell>` for 7.
- [X] T040 `summary`: `download-artifact` with `pattern: row-*`, one sorted table, and the two
      sentences that say what a red cell is and is not.

## Phase 6 — the Makefile, the README, the senders

- [X] T041 `make matrix-check` (`SET=`, `CELLS=`), stdlib only, no venv.
- [X] T042 `-k "$(K)"` quoted in `eval`, `eval-live` and `instruction-eval` — and
      `tests/test_scenario_set.py`'s pin on that exact string moved with it, with the reason
      written beside it. The pin caught the change, which is what a pin is for.
- [X] T043 `README.md`: the section *The matrix* — the three sets, what a cell is, the variables
      and secrets table, §13 step 5's first-run order, and where a verdict ends up.
- [X] T044 keel-cloud `.github/workflows/dispatch-matrix.yml`.
- [X] T045 keel-runtime's, with the comment that a runtime change reaches the matrix only after
      keel-connect-skill's `make runtime` + `make release`, and that spec 005 there is a separate
      task that is **not built**.
- [X] T046 keel-web's, with §6.2's eight paths verbatim and the note that `src/styles/`,
      `src/components/marketing/`, `public/` and `specs/` are absent on purpose.
- [X] T047 keel-connect-skill's.
- [X] T048 All four: `[skip e2e]` on the head commit's message, a no-op with a notice when
      `KEEL_DISPATCH_TOKEN` is absent, the payload built with `jq` from environment values (a
      commit message is data, never shell), and a non-204 failing with the secret named.

## Phase 7 — verification

- [X] T049 `make unit` → **814 passed**, green.
- [X] T050 `make matrix-check`, and with `SET=` and `CELLS=`.
- [X] T051 `actionlint` (brew, 1.7.12) with shellcheck on all five workflow files → clean.
- [X] T052 The two inline Python blocks extracted, compiled, and run against a fixture `runs/`.
- [X] T053 Merged `--no-ff` into each repository's `master` and pushed; worktrees removed.

## Not done, on purpose

- [ ] The monthly reset as a workflow (§8) — it is `reset.sh --target staging` from the Mac, and
      keel-cloud's README Part 3 step 5 carries it. A scheduled job that drops a database volume is
      not something the referee should own.
- [ ] keel-connect-skill spec `005-release-on-runtime-change` — a separate task; only the comment
      pointing at it was written.
- [ ] Any run at all. §13 step 5 is the founder's, one cell at a time.
