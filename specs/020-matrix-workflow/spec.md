# Feature Specification: the matrix workflow

**Feature Branch**: `matrix-workflow`

**Created**: 2026-09-10

**Status**: Implemented, **never run**. `make unit` **765 → 814**, green. `actionlint` (1.7.12, with
shellcheck) is clean on all five workflow files. Nothing here has touched AWS, pushed an image or
spent a model request, and it cannot: every job that costs anything is gated on a repository
variable that does not exist yet, and the twin it deploys to does not exist yet either (keel-cloud
spec `036-staging-twin`, design §13 steps 1–4). **This spec ships a workflow that skips.** That is
the point: merging it today is free, and the day the founder sets `KEEL_STAGING_ENABLED=true` the
matrix is already in `master` on every repository that has to dispatch to it.

**Input**: keel-cloud `canon/designs/e2e-matrix-design.md` — §5 (the matrix), §6 (the workflow end
to end), §8 (retention), §10 (cost), §11 (row four: *"`020-matrix-workflow` — `matrix.yml`: dispatch
receiver, staging deploy job, the three schedules, artifacts, summary"*), §12 (the invariants),
§13 step 5 (the first-run order) and §14 decisions 4, 5, 6, 8, 11 and 12.

The siblings, read at these commits:

| Sibling | What this feature depends on |
|---|---|
| keel-cloud | `deploy/bin/deploy.sh --target staging <tag>` and `deploy/bin/common.sh`'s `apply_target`, `read_deployed_tag`, `KEEL_INSTANCE_ID`/`KEEL_ELASTIC_IP`; `provision.sh` step 9, which creates the `keel-ci-deploy` role, its one trusted subject and its five statements; `deploy/README.md` Part 3. |
| keel-runtime | `.github/workflows/acceptance.yml`'s model-driven job: how each host's CLI is installed per OS (`npm install -g @anthropic-ai/claude-code`; `@github/copilot@1.0.83` with a `latest` fallback) and how the two secrets are read (`ANTHROPIC_API_KEY`; `KEEL_RUNTIME_CI_COPILOT`, mapped to `COPILOT_GITHUB_TOKEN`, the name the CLI itself reads). Both are now **organisation** secrets, shared with this repository. |
| keel-web | nothing but a path filter — the eight paths §6.2 names, in that repository's own `dispatch-matrix.yml`. |
| keel-connect-skill | decision 5: a cell installs the plugin **from the public marketplace**, so a runtime change reaches the matrix only after `make runtime` + `make release`. Spec 005 there is the workflow that closes that; it is **not built here** and the dispatch file says so in a comment. |
| this repository | spec 017's `remote` profile (`KEEL_REMOTE_*`, the gate credential, `register_cell_identity`/`label_cell_identity`), spec 018's gated stub and `make oidc-image`, spec 019's `KEEL_JOURNEY_HOST` and the `s012-journey-<host>` bundle. |

## What changes, stated first

This repository has **no GitHub workflow at all** today. It gains one that matters and one file of
data behind it, and four sibling repositories gain a four-line one each.

| File | What it is |
|---|---|
| `matrix/cells.toml` | **The matrix, as data.** The three axes, the two scenario lists, and the three named sets, cell by cell. |
| `matrix/cells.py` | The one reader: load, validate, the design's coverage rules, and `--json` for the workflow. |
| `matrix/__init__.py`, `matrix/__main__.py` | `python -m matrix`. |
| `.github/workflows/matrix.yml` | `select` → `deploy-staging` → `cell` (the matrix) → `summary`. |
| `Makefile` | `make matrix-check`, and `-k` is now quoted so a multi-scenario selector survives. |
| `tests/test_matrix_cells.py` | 49 stackless tests. |
| `tests/test_scenario_set.py` | one line: the pin on the Makefile's `-k` moved with the quoting it pins. |
| `README.md` | the section *The matrix*. |

**The coverage rules are asserted against the real file, not against a fixture.** `per_change`
covers every OS once per host and spends at least one cell on the 3.9 floor; `nightly` never leaves
Ubuntu; `weekly` **is** the product of the axes; every cell everywhere is a combination the axes
allow, and no set names a cell twice. A `cells.toml` that drifts from §5.2 fails `make unit` on the
founder's Mac and fails `select` on a runner — in both cases before a runner minute or a model
request is spent.

### The Python axis has three values, and the design's §5.1 names two

Stated here rather than quietly reconciled, because it is the one number this spec changed.

§5.1's table names *"3.9 (the floor), 3.13 (current)"*. But §5.2 counts **eighteen** weekly cells
and **six** nightly ones, §10's cost table splits the weekly eighteen as *"6 / 6 / 6"* per operating
system, and §4.3's own picker sample reads `2026-09-11 · ubuntu · copilot · py3.12`. Three
operating systems × two hosts × two Pythons is twelve and four, not eighteen and six; with three
Pythons it is exactly eighteen and exactly six, and 3.12 is the value the design's own sample
shows. So the axis is **3.9, 3.12, 3.13** — the floor spec 004 promised, what Ubuntu 24.04 ships as
its system Python (and what this harness itself runs on), and what `brew`/`winget` hand out today.

Nothing about the cheap set moved: `per_change` is still six, still 3.9 on the Ubuntu cells and
3.13 elsewhere, exactly as §5.2 words it. 3.12 is spent only by the nightly and the weekly, which
are the two sets the design sized for it.

### The billing half of §10 is moot; the model half is not

§10 assumed this repository was private and priced macOS minutes at ten times Linux
(*"roughly $25 a month of minutes … making keel-e2e-eval public makes all of it $0 and is the
single largest lever here"*). **The founder pulled that lever: keel-e2e-eval is public.** Runner
minutes are free, on every operating system, and decision 10 is closed.

What is left is the real number, unchanged:

| Set | Cells | Copilot cells | Claude cells | Premium requests | Claude API |
|---|---|---|---|---|---|
| per change | 6 | 3 | 3 | ~39 | ~`$4.50` |
| nightly | 6 | 3 | 3 | ~39 | ~`$4.50` |
| weekly | 18 | 9 | 9 | ~117 | ~`$13.50` |

A Copilot cell is about **13 premium requests**; a Claude cell about **`$1.50`** of API. At ten
qualifying changes a week that is about **1 900 premium requests and `$220` of Claude a month**.
That is why the per-change set is six and not eighteen, why `[skip e2e]` exists in every sender,
and why `concurrency` debounces in the receiver rather than in the senders.

## User scenarios

### The founder merges this, today, and nothing happens

`KEEL_STAGING_ENABLED` is unset. A push to `master` runs `select`: it reads `cells.toml`, validates
it, prints the six cells that *would* have run, writes one line to the job summary — *"Matrix
skipped: the staging twin is not switched on … per_change would have run 6 cell(s) — push to
master."* — and stops. No role is assumed, no box is deployed, no model is asked anything. Every
sender is the same: without `KEEL_DISPATCH_TOKEN` its one job prints a notice naming the secret and
exits green.

### The founder switches it on (design §13 step 5)

1. `make matrix-check` on the Mac.
2. The twin exists and answers `/v2/me` 401 (keel-cloud spec 036, §13 steps 1–4).
3. The four repository variables and the two repository secrets below.
4. `KEEL_STAGING_ENABLED=true`.
5. **Run workflow** → `set: per_change`, `cells: ubuntu-24.04-claude-py3.13`. One cell.
6. Then `cells: windows-latest-copilot-py3.9`.
7. Then the six, then the schedules.

### A merge to keel-cloud's master, once it is on

keel-cloud's `dispatch-matrix.yml` POSTs `{repo, sha, why}`. `select` chooses `per_change`;
`deploy-staging` assumes `keel-ci-deploy` through OIDC, checks out keel-cloud at that sha and
keel-web at master, builds the arm64 image natively on `ubuntu-24.04-arm`, runs
`deploy.sh --target staging <short sha>`, and gates on `/v2/me` answering 401 **and** the stub's
discovery document answering 200. Only then do six cells start, each registering its own founder
with the twin's picker, installing the plugin from the public marketplace, and walking the journey.
Each uploads its bundle; the last job prints one table.

### A merge to keel-web's `src/styles/`

Nothing. The path filter does not name it, so the workflow does not start, so no dispatch is sent
(§6.2, decision 6).

## Requirements

- **FR-001 The referee owns the schedule** (M9). Every trigger lives in this repository's
  `matrix.yml`: `repository_dispatch` (type `matrix`), `push` to master, `schedule` at 03:00 UTC
  and Sunday 04:00 UTC, and `workflow_dispatch` with `set` and `cells`. A sender chooses nothing
  but whether to speak.
- **FR-002 The whole workflow skips cleanly when the twin is off.** `KEEL_STAGING_ENABLED != 'true'`
  → one free job, one line of summary, green. No job that costs anything runs, and no secret is
  needed for that path.
- **FR-003 The cells are data and the data is checked.** `matrix/cells.toml` is the only place a
  cell is written down; `python -m matrix` validates it against the axes **and** the design's
  coverage rules; `make matrix-check` and the workflow's `select` job are the same command.
- **FR-004 Debounce in the receiver** (§6.2): `concurrency: matrix-<repo>` with
  `cancel-in-progress`, keyed on `client_payload.repo` so five merges to one repository in ten
  minutes cost one run and a keel-web merge never cancels a keel-cloud run.
- **FR-005 No AWS key anywhere** (decision 8). `deploy-staging` assumes the role named by
  `KEEL_CI_DEPLOY_ROLE_ARN` through GitHub's OIDC token. `KEEL_INSTANCE_ID` and `KEEL_ELASTIC_IP`
  come from repository variables because the CI role deliberately carries no `ec2:Describe*`
  (§4.2's spec 036 amendment).
- **FR-006 A keel-cloud change moves the twin; anything else leaves it where it is** (§6.3). The
  tag is the short sha of the commit the job checks out — this sha for keel-cloud, the value of
  `/keel/staging/deployed-tag` otherwise — so the image tag always names the source it was built
  from (M1).
- **FR-007 The stub's image is rebuilt when the stub changed, and never otherwise.** The tag is the
  sha1 of `stack/stub_oidc` and `stack/containers/oidc`'s tree objects, so *changed* and *absent
  from ECR* are one question; `/keel/staging/oidc-image-tag` is written every run.
- **FR-008 The cells start only when the twin answers** (§6.3's gate): `/v2/me` 401 **and** the
  issuer's discovery document 200, polled, with the failure naming both codes.
- **FR-009 A cell is the founder's own command.** `make eval-live K=<scenarios>` with
  `KEEL_EVAL_PROFILE=remote`, the twin's URL, the gate credential as `harness`, `KEEL_REMOTE_CELL`,
  `KEEL_JOURNEY_HOST`, and `KEEL_COPILOT_MODEL=gpt-5.6-luna` on Copilot cells as spec 016 pins it.
  The host CLI is installed exactly as keel-runtime's `acceptance.yml` installs it, with the same
  secrets under the same names.
- **FR-010 A cell's Python is the runtime's.** Two `setup-python` steps: the harness's own 3.12
  (it needs `tomllib`), then the cell's, which is what `python3` resolves to for the skill's script
  and the bundled runtime. A 3.9 cell measures the thing under test, never the referee.
- **FR-011 Every cell uploads its bundle, always** (§6.4, §8): the artifact `runs-<cell>`, 30 days,
  written even when the cell is red — a red cell is exactly the bundle the founder wants. The
  bundles **this run wrote** are found by diffing `runs/` against a listing taken before it, which
  is what makes each summary row name the right bundle.
- **FR-012 One table** (§6.4): each cell appends its own row to its job summary and uploads it, and
  a final `summary` job collects them into one table of at most eighteen rows — cell, scenario,
  verdict, score, failed step.
- **FR-013 A green matrix triggers nothing and a red one rolls nothing back** (M8, decision 12).
  Nothing in these workflows deploys production, and nothing rolls staging back.
- **FR-014 The senders are four lines and a comment.** On push to master, skip when the head
  commit's message contains `[skip e2e]`, and POST `{repo, sha, why}` with `KEEL_DISPATCH_TOKEN`.
  keel-web adds §6.2's path filter verbatim. **A missing token is a no-op that says so**, never a
  red check on a repository that has nothing to do with it.

## What the founder must set, and where

**In keel-e2e-eval** — Settings → Secrets and variables → Actions.

| Repository variable | Value |
|---|---|
| `KEEL_STAGING_ENABLED` | `true`. The master switch. Anything else skips the whole matrix. |
| `KEEL_CI_DEPLOY_ROLE_ARN` | the ARN of `keel-ci-deploy`, which `provision.sh --target staging` creates and whose trust policy names exactly `repo:keeldiscovery/keel-e2e-eval:ref:refs/heads/master`. |
| `KEEL_INSTANCE_ID` | the twin's EC2 instance id. |
| `KEEL_ELASTIC_IP` | the twin's Elastic IP. |

| Repository secret | Value |
|---|---|
| `KEEL_STAGING_HARNESS_PASSWORD` | the plaintext of the `harness` gate user, whose bcrypt sits in `/keel/staging/oidc-gate-harness-hash`. **The `founder` gate password is never here** (§4.2). |
| `KEEL_SIBLINGS_TOKEN` | a fine-grained token with read-only **Contents** on `keeldiscovery/keel-cloud` and `keeldiscovery/keel-web`, and nothing else. **Not in the design**, and needed because those two repositories are private and `deploy-staging` checks them out. |
| `ANTHROPIC_API_KEY` | already an organisation secret shared with keel-runtime. Nothing to do. |
| `KEEL_RUNTIME_CI_COPILOT` | likewise; read as `COPILOT_GITHUB_TOKEN`, the name the CLI reads. |

**In each sender** (keel-cloud, keel-runtime, keel-web, keel-connect-skill):

| Repository secret | Value |
|---|---|
| `KEEL_DISPATCH_TOKEN` | a fine-grained token whose only permission is to POST `/dispatches` on `keeldiscovery/keel-e2e-eval`. One per repository, or one token added to all four. **It is never set in keel-e2e-eval** — that is the receiving end. |

## What is deliberately not built

- **No monthly reset job.** §8's reset is `reset.sh --target staging` from the Mac on the first
  Sunday, and keel-cloud's `deploy/README.md` Part 3 step 5 already carries it as a founder's
  command. A workflow that dropped a Postgres volume on a schedule is a deletion this repository
  should not own, and M7 is *"cells never delete"*.
- **No keel-connect-skill release workflow.** Spec 005 there is a separate task; this feature only
  leaves the comment in keel-runtime's dispatch file that says so.
- **No scenario change, no harness change.** `make eval-live` is the founder's own command and a
  cell runs it unedited. The only Makefile change is quoting `-k`, which a multi-scenario selector
  needs and a single one cannot notice.
- **No second table, no dashboard, no badge.** §6.4 names three places a verdict is recorded and
  this adds none.
- **No `runs/` retention policy.** 30 days is §6.4's number and artifacts expire themselves.

## Deviations from the design, and why

Three, each visible in the files themselves:

1. **Three Pythons, not two** — §5.2's and §10's own counts, and §4.3's own sample. Written up
   above and in `cells.toml`'s header.
2. **`KEEL_SIBLINGS_TOKEN`** — the design says nothing about how a runner checks out two *private*
   repositories. It cannot be `GITHUB_TOKEN` (that is scoped to this repository) and it must not be
   an AWS credential (decision 8). A read-only fine-grained token is the smallest thing that works,
   and the job fails with its name when it is absent.
3. **`deploy.sh` is skipped when the tag is already in ECR.** §6.3 says a non-keel-cloud change
   *"redeploys the tag production is on"*. Spec 036 made both ECR repositories **immutable**, so
   re-pushing an existing tag is refused by AWS — and a tag that is already in ECR is a tag the twin
   is already running, so the redeploy would reach the same end state by failing first. The job
   says which it did, and still runs §6.3's gate either way. The one case this defers is a new
   `keel-oidc` image with an unchanged keel-cloud tag: `/keel/staging/oidc-image-tag` is written,
   the workflow prints a notice, and the twin takes it on its next deploy.
