# Feature Specification: The matrix powers the twin

**Feature Branch**: `023-staging-on-demand`

**Created**: 2026-09-23

**Status**: Draft — for the founder's review

**Input**: keel-cloud `canon/designs/e2e-matrix-design.md` §16 (the amendment of 2026-09-23) and
keel-marketing-service `canon/designs/cloud-deployment-design.md` §9 and A-9…A-11; keel-cloud
spec 043 (the two IAM actions this workflow needs, applied by the founder before the first run
that relies on them).

## The one sentence

`matrix.yml` starts `keel-staging` before it deploys, waits for it by retrying the one call the
role already has, and stops it in a job of its own that runs whatever happened to the cells — so
the twin costs its disk and its address and a few hours a month, and nothing else.

## What changes, stated first

Two steps in `deploy-staging`, one new job `stop-staging`, one repository variable read in one
more place. `summary` does not change and still goes nowhere near AWS. `reset.sh` does not move.
Nothing in `stack/`, `harness/` or the cells changes.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A run starts a stopped twin (Priority: P1)
1. **Given** `KEEL_STAGING_ENABLED=true`, `KEEL_INSTANCE_ID` set, and the instance `stopped`,
   **When** `deploy-staging` runs, **Then** after the assume-role step it runs
   `aws ec2 start-instances --instance-ids "$KEEL_INSTANCE_ID"`, then loops on
   `aws ssm send-command --instance-ids "$KEEL_INSTANCE_ID" --document-name AWS-RunShellScript
   --parameters commands=true` every 10 s, up to 30 tries, until the command is accepted **and**
   `get-command-invocation` reports `Success`; only then does the existing tag step run.
2. **Given** the instance already `running`, **Then** `start-instances` is a no-op and the loop
   passes on its first try.
3. **Given** SSM never answers within five minutes, **Then** the job fails with
   `::error::keel-staging did not come online in 5 minutes` and `stop-staging` still runs.

### User Story 2 - Every run stops it (Priority: P1)
1. **Given** a green run, **Then** `stop-staging` — `needs: [select, deploy-staging, cell]`,
   `if: always() && needs.select.outputs.deploy == 'true'`, `permissions: {contents: read,
   id-token: write}` — assumes `keel-ci-deploy` and runs `aws ec2 stop-instances
   --instance-ids "$KEEL_INSTANCE_ID"`.
2. **Given** a red cell, or a cancelled run, **Then** the same.
3. **Given** `deploy == 'false'` (cells only, no deploy), **Then** `stop-staging` is skipped —
   a run that did not start the box must not stop a box a founder started by hand.
4. `summary` is byte-identical to before.

### User Story 3 - It is lintable and it skips when it should (Priority: P1)
1. `actionlint` (with shellcheck) clean.
2. **Given** `KEEL_STAGING_ENABLED` unset, **Then** the whole workflow still skips as spec 020
   built it; the new job is gated by the same `select` outputs.

## Requirements

- **FR-001** `deploy-staging`: the start step and the wait loop, between "Assume keel-ci-deploy"
  and "Which keel-cloud tag the twin should be running"; the loop uses only `ssm:SendCommand` and
  `ssm:GetCommandInvocation`.
- **FR-002** The `stop-staging` job per User Story 2, placed after `cell` and before `summary` in
  the file, with a comment naming the design and why it is not a step in `summary`.
- **FR-003** The `workflow_dispatch` description for the reset input gains "(the box is started
  first and stopped after)".
- **FR-004** `README.md` (or the workflow's header comment, whichever spec 020 used for the
  founder-facing words): the twin is off between runs; a dispatched run with `deploy: false`
  against a stopped box will fail at the gate, by design — dispatch with `deploy: true`.
- **FR-005** `actionlint` clean; `make unit` unchanged and green.

## Success criteria

Two dispatched runs after keel-cloud spec 043 is applied — one green, one with a cell forced red —
each leave the instance `stopped` within five minutes of `stop-staging` (A-9), checked from the
Mac with the founder's credential; the next bill's staging EC2 hours are in the tens (A-11).
