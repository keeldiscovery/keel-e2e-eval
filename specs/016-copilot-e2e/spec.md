# Feature Specification: Copilot, host and thinker

**Feature Branch**: `016-copilot-e2e`

**Created**: 2026-09-10

**Status**: Implemented. One live run of record, `make eval-live K=s012`, plus one
`make instruction-eval HOST=copilot N=1` on the upgraded plan.

**Input**: the founder upgraded their GitHub Copilot plan and asked for proof of two things this
repository had never measured together:

1. **the keel-connect skill loads and runs with Copilot CLI as the host** -- not merely that
   keel-runtime can shell `copilot`;
2. **keel-runtime is compatible with Copilot doing the inference end to end** -- a whole founder
   journey answered by Copilot, not by `--executor scripted`.

The siblings, read at these commits:

| Sibling | Commit | What this feature depends on |
|---|---|---|
| keel-cloud | `085382e` | `canon/designs/keel-skill-design.md` §5 (two hosts), §5.4 (`CopilotExecutor`), §5.5 (the four-part "supported" gate -- parts **2** and **3** are this repository's). |
| keel-web | `d5d8645` | `/connect`, the device-approval screen the founder approves the code on. |
| keel-runtime | `d30dbd0` | `CopilotExecutor`, `resolve_executor`'s `--host` step, `KEEL_COPILOT_MODEL`, spec `005-copilot-executor` C-3/C-5/C-6/C-7. |
| keel-connect-skill | `f06f481` (`release` `f1ea305`) | `SKILL.md`'s one Copilot line -- *"If you are GitHub Copilot, add `--host copilot`"* -- and the `keel` plugin on the public `keeldiscovery/keel-marketplace`. |

## What changes, stated first

**Every Copilot measurement this repository has ever made stopped short of the founder's own
machine.** Spec 013's acceptance bed writes `copilot -p "keel connect"` and has **never run it**:
all four run records read `"result": "skipped"`, because the model-driven half reads
`COPILOT_GITHUB_TOKEN` from the caller's shell and the founder logs in with stored OAuth instead.
Spec 014 ran Copilot 131 times but as a *thinker only* -- `instructions/` shells the executor
directly and no skill, no host and no CLI-loaded `SKILL.md` is anywhere near it. And the skill's
own Copilot packaging is refereed by S-009 as a **directory copy**, never as an install.

So the two halves of §5.5 that name a host had one measured side each, and there was no run in
which the two were the same runtime. **S-012 is that run.** One scenario, two legs, one runtime
carried between them:

- **Leg one, the host.** The plugin is installed into a **fresh `COPILOT_HOME`** from the real
  public marketplace with Copilot's own two commands, `copilot skill list` is asked whether it can
  see `keel-connect` as a *plugin* skill, and then `copilot -p "keel connect"` is run for real.
  What is asserted is never Copilot's prose: it is **the traces the skill leaves when it really
  ran** -- a heartbeat file in state `awaiting_approval`, a launch log carrying `KEEL_USER_CODE=`
  and the device page URL, and a code the **eval cloud** confirms it issued. Then the founder
  approves it in a browser, and a second `copilot -p "keel connect"` must reach the skill's
  `already_connected`.
- **Leg two, the thinker.** That same runtime -- on the Copilot executor, because the skill read
  `SKILL.md` and passed `--host copilot` -- answers a whole founder journey: three stages framed,
  reviewed and approved, one person invited and answered, the reading read, *What this says*
  written by Copilot, the overview and one card opened. Zero refusals, every job COMPLETED, and
  the premium requests counted.

**This is the first time C-5 has been exercisable.** keel-runtime spec 005 measured, on this Mac
on 2026-09-09, that CLI 1.0.83 rejected **every** slug offered to `--model` -- its own router's
choice included -- so `CopilotExecutor.model` defaults to `None` and C-5 ("the Copilot path pins
`--model`; `auto` is never used in a measured run") was closed *by mechanism, not by measurement*.
On the upgraded plan `--model claude-sonnet-5` is accepted, and `claude-sonnet-5` is what the CLI's
own resolver now names as the default. Both legs and the instruction eval pin it through
`KEEL_COPILOT_MODEL`, and every bundle records `pinned_model` beside the reported one.

## User scenarios

### S-012 -- "Copilot, host and thinker" (live, `make eval-live K=s012`)

**Leg one -- the host.**

1. A fresh `COPILOT_HOME` is created under `runs/<stamp>/copilot-home/` and a fresh `KEEL_HOME`
   under `runs/<stamp>/keel-home/`. Nothing of the founder's own Copilot home is copied. The login
   survives the isolation on this machine because the stored credential does not live under
   `~/.copilot` -- measured, and recorded in the bundle as `credential: "stored OAuth, outside
   COPILOT_HOME"`. Had it not survived, `COPILOT_GITHUB_TOKEN` would have been used when present
   and the real home otherwise, saying so.
2. `copilot plugin marketplace add keeldiscovery/keel-marketplace` and `copilot plugin install
   keel@keel` -- Copilot's own two commands, against the real public marketplace, into that home.
3. `copilot skill list --json` names `keel-connect`, and its source is a **plugin**.
4. `copilot -p "keel connect" --allow-tool 'shell(python3:*)' --allow-tool skill --no-auto-update
   --no-ask-user --output-format json --model claude-sonnet-5`, with `KEEL_BASE_URL` naming the
   eval cloud and `KEEL_RUNTIME_PATH` scrubbed. **Never `--bare`** -- there is no such flag on this
   CLI, and its Claude equivalent skips skill discovery (spec 013 T-2).
5. The traces, asserted in this order and none of them Copilot's prose:
   - `<KEEL_HOME>/runtime.heartbeat.json` exists and reads `state: "awaiting_approval"`;
   - `<KEEL_HOME>/keel-connect-check.launch.log` carries a `KEEL_USER_CODE=` line and a
     `KEEL_VERIFICATION_URI=` line naming keel-web's `/connect`;
   - `GET /v2/device-authorizations?user_code=<that code>` on the **eval cloud**, with a founder
     session, answers 200 -- the code is one this Keel issued, and it is not yet approved.
6. The founder approves it: sign in as founder A through the stub issuer's picker, open the
   verification URI, click *Approve this device*, and read *device approved*.
7. `copilot -p "keel connect"` a second time -> the skill's `already_connected`. Asserted through
   the **runtime's own `status`** (running, connected, `executor == "copilot"`), with a loose
   check that Copilot's reply says *connected*. Both transcripts go into the bundle.

**Leg two -- the thinker.** The same runtime, now connected, on the Copilot executor.

8. `status.executor == "copilot"` -- the skill passed `--host copilot` because `SKILL.md` told it
   to, and nothing in this scenario passed `--executor`.
9. The founder's journey, on `evals/payroll_exceptions.yaml`'s own market and statements: name and
   market; PROBLEM, SOLUTION and COMMERCIAL each framed by Copilot, reviewed and **approved
   as-is**; one person invited; that person's own corpus answers typed in an isolated browser
   context; the answer read; *What this says* waited for and non-empty; the overview and one card
   opened. A screenshot at every step.
10. The cards are asserted as **shapes, never content** (spec 008's judgement call 8): lines
    present and numbered, at least one deal-breaker, no refusal.
11. Zero refusals on the wire, every job `COMPLETED`, and the premium requests recorded from
    Copilot's own `--usage-output-file` for the host legs and from keel-runtime's own per-job
    envelopes (`premium_requests`, C-7 -- never a dollar figure) for the thinking.
12. The runtime leaves the way a founder leaves it: `scripts/keel_disconnect.py` against this
    run's own home.

### Then, once: the instruction eval on the upgraded plan

`make instruction-eval HOST=copilot N=1` with `KEEL_COPILOT_MODEL=claude-sonnet-5`, compared
against `runs/20260909T061537Z-instructions-copilot` (recall 76.1 %, anchoring 95.3 %, BRIEF 5/7,
errored 2) at the same `MARKS_VERSION` **5**, and read against §5.5's gate.

## Requirements

- **FR-001** S-012 is `live`-marked, opt-in through `make eval-live`, deselected from `make eval`
  and `make eval-all`, and skipped **by name with its reason** when `copilot` is absent or not
  usable -- never silently passed (C-11).
- **FR-002** Leg one installs the plugin with Copilot's own two commands from the real
  marketplace. No directory copy, no `--plugin-dir`, no `--add-dir`.
- **FR-003** Leg one asserts skill discovery from `copilot skill list --json` and the run's effect
  from the **runtime's own artefacts**, never from Copilot's reply. A reply may be read only for a
  loose "it said connected" check, which can never be the sole evidence of anything.
- **FR-004** The device code leg one relays must be one the eval cloud issued, proven by
  `GET /v2/device-authorizations?user_code=` against a founder session.
- **FR-005** `COPILOT_HOME` and `KEEL_HOME` are both fresh, under the run bundle, and named on the
  command line. `KEEL_RUNTIME_PATH` is scrubbed (T-1), so the runtime that answers can only be the
  one that travelled inside the plugin.
- **FR-006** Leg two asserts `status.executor == "copilot"` before the first job.
- **FR-007** Every card assertion is a shape or an absence. Nothing asserts what Copilot wrote.
- **FR-008** The bundle records: both Copilot transcripts, both usage files, the plugin/skill
  listings, the launch log, the heartbeat, the per-job envelopes, the pinned and reported model,
  the premium requests spent, and the cap sources (`runs/DRIFT.md` #46).
- **FR-009** A job that fails with an auth or plan error **stops the run and is reported as a
  finding**, never retried.
- **FR-010** Nothing here writes to a sibling repository, and no product code is fixed. Product
  faults go to `runs/DRIFT.md`.

## What is deliberately not built

- **No second attempt at anything live.** One `copilot -p` per leg-one step, one journey, one
  instruction eval.
- **No `HOST=both`**, no averaging, and no mark moved -- §5.5: *a mark that moves to accommodate a
  result has stopped being a mark.*
- **No change to the acceptance bed.** Its model-driven half is still `COPILOT_GITHUB_TOKEN`-only
  and still skips itself here; S-012 is the run that covers that ground on the founder's own
  login, and says so.
- **No new page objects.** Leg two drives `harness/browser.py` exactly as S-001 does.
- **Not scored.** No attribute of `evals/policy.py` applies to a scenario about which host loaded
  a skill and which model answered a job; the evidence is the transcript.
