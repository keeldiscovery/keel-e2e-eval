# Feature Specification: Four trees, one skill — and the beds it is measured in

**Feature Branch**: `013-skill-distribution`

**Created**: 2026-09-09

**Status**: Implemented — S-009 and the stackless half of `make acceptance` green against a live
stack, runs of record named in [tasks.md](tasks.md) and `README.md`. The model-driven half is
**skipped, by name**, for want of two secrets this shell does not hold.

**Input**: keel-cloud `canon/designs/keel-skill-design.md` (design of record, 2026-09-08), §13
step 10: *"keel-e2e-eval, `013-skill-distribution` — **S-009** and the beds:
`stack/containers/acceptance/{Dockerfile,Dockerfile.floor,run-acceptance.sh}`, `make acceptance`,
both hosts, both architectures."* The sections this feature is a referee of are §8 (packagings —
one source, four trees, one build), §10.1 (the three layers, and L2 is this scenario), §10.2 (B1,
the CLI stage), §10.4 (B3, the floor stage) and acceptance row **A-6**.

The siblings, read at these commits:

| Sibling | Branch | Commit | What this feature depends on |
|---|---|---|---|
| keel-connect-skill | `master` | `4eb0548` | spec 004: `VERSION`, `RUNTIME_VERSION`, `packaging/`, `make dist` and the four trees, with L1 asserting them byte-identical *as built*. Spec 003's `_runtime_location.py` and the seven shapes; spec 002's `keel_disconnect.py`. Bundled runtime `0.1.0+638c0dc`. |
| keel-runtime | `master` | `638c0dc` | the derived home (`~/.keel/<host-slug>/`), `environment` on `status`, and `keel disconnect`. |
| keel-cloud | `master` | `8acb805` | the device-authorization flow S-009 walks, and the design itself. |
| keel-web | `master` | `b0a5015` | `/connect`, where an installed skill's device approval lands. |

## What changes, stated first

**L1 proves the four trees are byte-identical *as built*. Nobody had checked what an installer
does to them.** keel-connect-skill's own tests compare `dist/plugin`, `dist/speckit`, `dist/bare`
and `dist/copilot-repo` against the source and against each other on every commit — and then the
bytes leave: into a plugin cache, into `~/.claude/skills/`, into a team's `.github/`, into
`.specify/extensions/keel/`. Acceptance row **A-6** is the question nobody could answer: *does a
copied skill still work after an installer moved it?*

Three things follow, and they are the whole feature.

1. **S-009 installs all four the way their own installers do** — the plugin's `skills/` directory
   copied out as a project's `.claude/skills/keel-connect`, the bare tree through **`install.sh
   --host claude`, run for real**, the Copilot tree into a repository's `.github/skills/`, the
   Spec Kit tree into `.specify/extensions/keel/` with its manifest read structurally — and then
   runs the skill's own script out of each, with no `KEEL_RUNTIME_PATH` and no checkout anywhere.
   All four must answer `authorization_started` with **one key set**, and, against a single
   connected runtime, `already_connected` **byte for byte** but the heartbeat's own clock.
2. **The beds exist**: `stack/containers/acceptance/{Dockerfile,Dockerfile.floor,
   run-acceptance.sh}` and `make acceptance`. Debian 12 with Python 3.11, Node 22 and both host
   CLIs; Debian 11, which *is* the 3.9 floor; `linux/arm64` and `linux/amd64`; the skill reached
   at `http://host.docker.internal:18080`, which is the eval stack on the host.
3. **Four findings, and none of them worked around** — `runs/DRIFT.md` #49 (the floor bed's
   distribution has left support), #50 (this machine's Docker has no `buildx`, and the legacy
   builder gets both architectures wrong in two different ways), #51 (**a live runtime that "keel
   disconnect" says is not running**) and #52 (the design reads a `source` key off `keel status`
   that no shipped contract carries).

## Clarifications

### `make acceptance` with no secret — refuse to start, or skip a half? — **skip the half, by name**

§10.2 says *"`make acceptance` refuses to start when either is unset rather than falling back to a
file"*. The second clause is the invariant (T-5) and it is kept exactly: no secret is baked into
an image, read out of `~/.claude/.credentials.json`, or looked for anywhere but the caller's own
environment.

The first clause is softened, deliberately. Refusing to start would make the **stackless half**
unrunnable — the half that needs no model, no host CLI and no money, and that answers A-6's actual
question on four images. Every machine this repository has ever run on lacks at least one of the
two secrets. So the refusal moves one level down: the half that needs the secret refuses *itself*,
names which variable is missing, says what it would have measured, and writes
`{"result": "skipped", "reason": "…is not set in the caller's shell; no secret is read from
anywhere else (T-5)"}` into the run record. **A run whose record says that is not a green run of
B1, and the record says so in those words.**

### Does this repo run `make dist`? — **no; it gates and names the command**

Identical to spec 012's clarification about `make runtime`, for identical reasons: this repo owns
no product code and never writes to a sibling repository. S-009 and `run-acceptance.sh` both check
for the built trees and fail naming `make -C ../keel-connect-skill dist`. (The trees for the runs
of record were built by hand, once, in that repository — it writes only into that repo's own
gitignored `dist/`, and the record says so.)

### Why is the container's Keel not named by `KEEL_BASE_URL`? — **because this shell exports one**

`runs/DRIFT.md` #48 recorded that this repository is worked on from shells exporting
`KEEL_RUNTIME_PATH`. The same shell exports `KEEL_BASE_URL=http://localhost:18081` — the
playground's address. Inside a container `localhost` is the container, so an inherited value would
have pointed the entire bed at nothing and the failure would have read as the skill's. The bed's
override is **`ACCEPTANCE_BASE_URL`**, which no shell exports by accident, and the ambient
`KEEL_BASE_URL` is never read. Inside the container it *is* set — to
`http://host.docker.internal:18080` — because naming the Keel on the environment is the founder's
own path, and it is what makes the derived home `~/.keel/host.docker.internal-18080/` checkable.

### What the beds could not assert, and what they assert instead

§10.2's assertion 2 is *"`keel status` reports `source: "bundled"`"*. **There is no `source` key**
on any shipped shape (`runs/DRIFT.md` #52): `scripts/_runtime_location.py` computes one and no
contract carries it out. The bed proves the same thing by elimination instead — with
`KEEL_RUNTIME_PATH` absent (asserted), no `keel` on `PATH` and no checkout in the image, rules 1
and 3 of the resolution order are impossible, so a runtime that answers came from rule 2. That is
S-008's own stripped-tree argument, one line longer, depending on nothing unshipped.

## User Scenarios & Testing

### US1 — S-009: four installers, one skill (P1)

**Acceptance** (`evals/test_s009_skill_distribution.py`)

1. All four `dist/` trees exist; the gate names `make -C <skill> dist` and never runs it.
2. Each is installed the way its own installer installs it, into a fresh temporary
   Claude-Code-shaped home or project. The bare tree's `install.sh --host claude` is **executed**.
3. The four installed trees carry byte-identical `SKILL.md`, `scripts/` and `keel_runtime/`
   (D1, D2) — L1's gate, re-asserted on the far side of four different installs.
4. `plugin.json` parses, carries `VERSION`, and declares nothing that would make the plugin behave
   differently from a bare drop (D6, D7). `extension.yml` parses, carries `VERSION`, and every
   path it names resolves **in the installed tree**.
5. Each install answers `authorization_started` with `environment == "localhost:18080"`, exit 0,
   one line of JSON — and all four key sets are identical, while the four user codes differ.
6. Each install's `keel_disconnect.py` answers `not_running` before approval — **finding #51**,
   asserted as observed and cited in place.
7. One install connects; the device is approved in a real browser at keel-web's `/connect`; all
   four then answer `already_connected`, identical byte for byte but `last_heartbeat_at`.
8. A runtime one tree started is stopped through **another** tree's door — `disconnected`.

### US2 — the beds, built and run (P1)

**Acceptance** (`make acceptance`)

1. Four images build: CLI and floor, `linux/arm64` and `linux/amd64`.
2. In each, with no `KEEL_RUNTIME_PATH` and no `KEEL_HOME`: `keel status` reads not-running with
   its five keys; the skill's script answers `authorization_started` naming
   `host.docker.internal:18080`; the derived home is `~/.keel/host.docker.internal-18080/` and
   nothing is loose at `~/.keel` itself.
3. Both Pythons are observed by running, not by claiming: 3.11.2 on Debian 12, **3.9.2 on Debian
   11** — the floor, on a real distribution.
4. The model-driven half runs, or is skipped with its reason in the record.

## Requirements

- **FR-001** `stack/config.py` gains `skill_dist_path`; nothing builds the trees.
- **FR-002** `evals/test_s009_skill_distribution.py` exists, is deterministic, is not `live`, and
  asserts US1's eight points. It hands no tree a checkout and scrubs the ambient variables.
- **FR-003** S-009 leaves no process behind: connected runtimes through the skill's own door,
  pre-approval ones by the pid `authorization_started` handed back (#51's cleanup, not its fix).
- **FR-004** `stack/containers/acceptance/Dockerfile` is Debian 12 + Node 22 + both host CLIs,
  with one source tree `COPY`d into both hosts' skill directories and both CLI versions printed
  into the image. No secret, no `KEEL_RUNTIME_PATH`, no `KEEL_HOME`.
- **FR-005** `stack/containers/acceptance/Dockerfile.floor` is Debian 11 and carries nothing else.
- **FR-006** `stack/containers/acceptance/run-acceptance.sh` and `make acceptance` build both
  images for both architectures and run the stackless half in each; the model-driven half runs
  only from the caller's own environment and is otherwise skipped **by name, with its reason, in
  the record**.
- **FR-007** `make unit` grows, and the growth holds every property of the bed that would
  otherwise only be observable during a paid run: the secret rule, the `--bare` trap, the ambient
  base URL, both builder accommodations, and the shape of S-009's own assertions.
- **FR-008** Every finding is a `runs/DRIFT.md` entry with a bundle: #49, #50, #51, #52.

## Success Criteria

- **SC-001** `make unit` green, up from 425 (landed at **448**).
- **SC-002** `make eval K=s009` green against a live stack.
- **SC-003** `make acceptance` green on its stackless half: four images, two architectures, two
  Pythons, four probes.
- **SC-004** S-001 and S-008 still green in the same stack session.
- **SC-005** Every cross-repo gap found is a `runs/DRIFT.md` entry with a bundle, never a
  workaround.

## What this feature deliberately does not do

- **It does not drive a host CLI.** The model-driven half is written, gated and skipped; nothing
  here goes looking for a key.
- **It does not build the Windows job.** `acceptance.yml` is keel-runtime's, §10.3's, and another
  repository's (§13 step 11).
- **It does not install a `buildx`.** Two accommodations for the legacy builder live in the files
  that need them, each with the measurement that produced it (#50); changing how the founder's
  Docker works is not this session's to do.
- **It does not fix #51.** The pre-approval window is keel-runtime's to close; S-009 asserts what
  it observed and cleans up after itself.
