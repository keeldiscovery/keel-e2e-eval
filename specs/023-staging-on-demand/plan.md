# Implementation Plan: The matrix powers the twin

**Branch**: `023-staging-on-demand` | **Date**: 2026-09-23 | **Spec**: [spec.md](./spec.md)

## Summary

The workflow already assumes the role, already knows the instance id from a repository variable,
and already serialises itself. It gains a start, a wait that needs no new permission, and a stop
in a job that runs under `always()`. The wait is the only design point: with no `Describe*` in
the role, "is it up" is answered by asking it to do something and seeing whether it does.

## Structure

```
.github/workflows/matrix.yml
  deploy-staging:  + "Start the twin" (ec2 start-instances)
                   + "Wait for the twin" (send-command true, 10 s × 30, get-command-invocation Success)
  stop-staging:    new job; needs select, deploy-staging, cell; if always() && deploy == 'true';
                   id-token: write; assume role; ec2 stop-instances
README.md / header comment: the twin is off between runs
```

## Decisions

1. **A job, not a step in `summary`.** `summary`'s permissions omit `id-token` on purpose (spec
   021); a stop is an AWS call and belongs with the other AWS calls.
2. **Wait by doing.** `send-command` + `get-command-invocation` are already granted; the loop
   proves the SSM agent is up, which is the readiness `deploy.sh` needs.
3. **Skip the stop when there was no start.** `deploy == 'false'` means a founder brought the box
   up; the workflow does not take it down.
4. **No terminate, anywhere.** The role cannot (keel-cloud spec 043) and the workflow does not ask.
