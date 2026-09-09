# Implementation Plan: Four trees, one skill — and the beds it is measured in

**Branch**: `013-skill-distribution` | **Date**: 2026-09-09 | **Spec**: [spec.md](./spec.md)

**Input**: [spec.md](./spec.md), keel-cloud `canon/designs/keel-skill-design.md` (§8, §10.1,
§10.2, §10.4, §13 step 10, A-6), and the two sibling contracts this feature calls across:
keel-connect-skill `specs/001-keel-connect-check/contracts/skill-script-output.md` (seven shapes)
and `specs/002-keel-disconnect/contracts/skill-disconnect-output.md` (six).

**On the artefact set.** `spec.md` + `plan.md` + `tasks.md`, the shape specs 004–008, 011 and 012
use. This feature adds one scenario, three bed files, one Makefile target, one config property and
one stackless test file. It moves no versioned constant — `POLICY_VERSION` does not move, because
nothing about *scoring* changed, and S-009 like S-008 is **not scored**: none of the policy's four
attributes applies to a scenario about what ships.

## Summary

L1 compares the four packaging trees as they are built. This feature compares them **as they are
installed** — which is the only place the claim can actually fail, because installing is copying
and copying is the failure the design exists to prevent. S-009 puts each tree where its own
installer puts it, runs the skill out of the result with no checkout reachable, and asserts one
shape across all four; then connects one runtime and makes all four read it, byte for byte. The
beds take the same question to Linux: two Debians, two Pythons, two architectures, one skill, one
`COPY`.

**Technical approach**: install, then ask the contract. Nothing here reads the skill's internals,
patches anything, or teaches this repo how any host CLI works — the four installs are four
directory copies (one of them performed by the skill's own `install.sh`), and every assertion
afterwards is against a contract that lives in the repository that owns it.

## Technical Context

**Language/Version**: Python 3.11+ for the harness, as ever. The *subject* is measured at 3.9 and
3.11 in containers, and the container probe is written in 3.9 syntax for exactly that reason.

**Dependencies**: unchanged. `pyyaml` was already in `requirements.txt` (spec 009's corpus reader)
and is what reads `extension.yml`; Docker is a bed prerequisite, not a package.

**Testing**: `make unit` for everything stackless, `make eval K=s009` for the live scenario,
`make acceptance` for the beds.

**Constraints**: this repo owns no product code, never writes to a sibling repository, and reports
cross-repo gaps as `runs/DRIFT.md` entries with a bundle.

## The five changes, and why each is where it is

### 1. `stack/config.py` — `skill_dist_path`

One property, for the same reason `bundled_runtime_path` exists: a scenario that spelled
`../keel-connect-skill/dist` itself would be the second place that path lives.

### 2. `evals/test_s009_skill_distribution.py` — the scenario

Four installer functions, one per tree, each with a docstring naming the real installer it stands
for. Only `install.sh` is executed; the other three are directory copies, because
`claude plugin install` and `specify extension add` need CLIs, a marketplace and a network — which
is the containerised bed, not this scenario. The manifests are read structurally so a tree whose
manifest names a file the install does not contain is red here rather than in a founder's
terminal.

The strongest assertion is the last one: four installs reading **one** runtime must answer
`already_connected` identically but for `last_heartbeat_at`. Shapes can agree by accident; a
whole object agreeing across four trees cannot.

### 3. The beds — two Dockerfiles and a runner

The Dockerfiles are §10.2 and §10.4 as written, with two accommodations for a Docker that has no
`buildx` (#50) and one for a Debian that has left support (#49), each carrying the measurement
that produced it. `run-acceptance.sh` holds every assertion in one place — a Python probe that
prints one line of JSON (the discipline the contract it tests holds itself to) and an assertion
block beside it, so a reader sees what a green probe means without reading a container log.

### 4. `make acceptance`

Three variables, all overridable, none of them ambient. The target is documented in the Makefile
beside `eval-live` and `instruction-eval`, because when its model-driven half runs it belongs to
the same family: it costs real money and is run on purpose.

### 5. `tests/test_skill_distribution.py`

Twenty-two stackless tests. The ones that read source do so because the alternative is a property
observable only during a twenty-minute build on a machine holding two secrets — *no secret is
baked in*, *`--bare` is never passed*, *the ambient `KEEL_BASE_URL` is not read*. A property
nobody can check without spending money is a property that quietly stops holding.

## Risks, and what each is worth

- **The amd64 stage is emulated.** §10.2 names QEMU's failure modes as exactly the ones that would
  be blamed on us (T-4). Observed here: the emulated npm install of both host CLIs is slow but
  correct, and both amd64 probes pass. The two builder faults that did bite (#50) were the legacy
  builder's, not the emulator's.
- **The floor bed's distribution is out of support** (#49). It builds today from
  `archive.debian.org`; the entry says what has to happen when it does not.
- **The model-driven half has never run.** It is written from §10.2's own command lines and held
  to them by `make unit` — the `--bare` trap, `--permission-mode dontAsk`, `-s` for Copilot — but
  written is not measured, and the run record says `skipped`, not `passed`.
