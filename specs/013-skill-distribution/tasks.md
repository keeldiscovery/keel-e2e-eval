# Tasks: Four trees, one skill — and the beds it is measured in

**Input**: [spec.md](spec.md) (FR-001..008, SC-001..005, the four clarifications) with
[plan.md](plan.md).

**The siblings, read at**: keel-cloud `8acb805`, keel-web `b0a5015`, keel-runtime `638c0dc`,
keel-connect-skill `4eb0548` — skill `VERSION` **1.0.0**, bundled runtime **`0.1.0+638c0dc`**.

**Rules** (AGENTS.md): this repo owns no product code, never writes to a sibling repository, and
reports cross-repo gaps as `runs/DRIFT.md` entries with a bundle — this feature added **four**,
#49 to #52. `POLICY_VERSION` does not move. The scenarios stay deterministic and the two named
LLM exceptions do not change in number or in name: S-009 drives no model, and the beds' one
model-driven half is a separate target that did not run.

---

## Phase 1: the trees, and the scenario that installs them

- [X] T001 `stack/config.py`: `skill_dist_path` (FR-001). Gated on, never built here.
- [X] T002 `evals/test_s009_skill_distribution.py` (FR-002): four installers — the plugin's
      `skills/` out to a project's `.claude/skills/`, **`install.sh --host claude` executed** into
      a `HOME` of its own, the Copilot tree into a repository's `.github/skills/`, the Spec Kit
      tree into `.specify/extensions/keel/` — then a sha256 comparison of all four installed
      trees, both manifests read structurally, four `authorization_started`s with one key set, and
      four `already_connected`s byte for byte but the heartbeat's clock.
- [X] T003 S-009's teardown (FR-003): the shared runtime through an installed tree's own door, and
      the four pre-approval runtimes by the pid the contract handed back (`runs/DRIFT.md` #51).
- [X] T004 `tests/test_scenario_set.py`: there are **nine** scenarios now.

## Phase 2: the beds

- [X] T005 `stack/containers/acceptance/Dockerfile` (FR-004): Debian 12, Node 22 from nodejs.org's
      own tarball, `@anthropic-ai/claude-code` and `@github/copilot` with both versions printed
      into the image (T-6), and one source tree `COPY`d into **both** hosts' skill directories
      (D1/T-3). No secret, no `KEEL_RUNTIME_PATH`, no `KEEL_HOME`.
- [X] T006 `stack/containers/acceptance/Dockerfile.floor` (FR-005): Debian 11, *nothing else*, via
      `archive.debian.org` (#49).
- [X] T007 Both Dockerfiles: `ARG BUILD_PLATFORM` in the cache key and every `COPY` ahead of every
      `RUN` — the two legacy-builder accommodations (#50), each with its measurement above it.
- [X] T008 `stack/containers/acceptance/run-acceptance.sh` (FR-006): the gates (docker, the built
      trees with the command named, the stack answering), four builds, the Python probe and its
      assertion block, the model-driven half with its named skip, and the JSON record.
- [X] T009 `Makefile`: `acceptance`, documented beside `eval-live` and `instruction-eval` because
      when its model half runs it belongs to that family.
- [X] T010 `tests/test_skill_distribution.py` — 22 stackless tests (FR-007).
- [X] T011 `runs/DRIFT.md` **#49** (Debian 11 has left support, and what that costs the floor bed),
      **#50** (no `buildx`; the legacy builder's two faults), **#51** (a live runtime that "keel
      disconnect" says is not running) and **#52** (`source: "bundled"` is a design field no
      shipped contract carries).

## Phase 3: the runs of record

One stack session — `make up` → `make eval K=s009` → `make acceptance` → `make eval K=s001` →
`make eval K=s008` → `make down` — on keel-cloud `8acb805`, keel-web `b0a5015`, keel-runtime
`638c0dc`, keel-connect-skill `4eb0548`, bundled runtime `0.1.0+638c0dc`.

| What | Run | Result |
|---|---|---|
| S-009 skill distribution | `20260909T054513Z-s009-skill-distribution` | **PASSED, not scored** |
| `make acceptance` | `20260909T054621Z-acceptance` | **PASSED (stackless half)**; model-driven half **SKIPPED** |
| S-001 smoke | `20260909T055055Z-s001-smoke` | **PASSED, 5.0/5** — the goodbye again at **5 ms** |
| S-008 bundled runtime | `20260909T055234Z-s008-bundled-runtime` | **PASSED, not scored** |

**What the acceptance run measured**, from its own `acceptance.json`:

| Probe | Distribution | Python | Outcome | Home |
|---|---|---|---|---|
| `cli-arm64` | Debian 12 (bookworm) | 3.11.2 | `authorization_started`, `host.docker.internal:18080` | `~/.keel/host.docker.internal-18080/` |
| `cli-amd64` | Debian 12 (bookworm) | 3.11.2 | same | same |
| `floor-arm64` | Debian 11 (bullseye) | **3.9.2** | same | same |
| `floor-amd64` | Debian 11 (bullseye) | **3.9.2** | same | same |

Host CLIs baked into the CLI image, printed by the build (T-6): **claude 2.1.266**, **GitHub
Copilot CLI 1.0.83**, Node **v22.14.0**.

- [X] T012 `make unit` green: **425 → 448**.
- [X] T013 `make down` printed
      `[down] (eval) keel-runtime: not_running (via keel-connect-skill/scripts/keel_disconnect.py)`.
- [X] T014 `README.md` and `AGENTS.md` amended: nine scenarios, the beds, `make acceptance`, and
      the runs of record above.

## What is left undone, and where it goes

- **The model-driven half has never run.** `ANTHROPIC_API_KEY` and `COPILOT_GITHUB_TOKEN` are not
  in this shell and nothing here went looking for them (T-5). Both are written, both are held to
  §10.2's own command lines by `make unit` — including the `--bare` trap that would have made the
  skill invisible — and both are recorded as `skipped` with the variable named. **A-4, A-6's model
  half and A-11 are not green**; they are unmeasured, which is a different thing and is what the
  record says.
- **`runs/DRIFT.md` #51 is open, and it is the finding of the night.** Between
  `authorization_started` and approval there is a live `keel connect` that `keel disconnect`
  reports `not_running` for. It is keel-runtime's to close; S-009 asserts what it observed.
- **#52 is open**: `source` is a design field with no contract behind it. One key on `status` and
  one line in keel-cloud's `status-cli-output.md` would close it.
- **#49 has a deadline nobody has set**: the floor bed builds from `archive.debian.org` today.
- **The Windows job** (`acceptance.yml`, §10.3) is keel-runtime's, step 11, and out of scope here.
- **The instruction eval and S-004** were not run: neither is touched by this feature and both
  cost real money.
