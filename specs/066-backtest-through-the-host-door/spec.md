# Spec 066 -- The back-test through the host door: Keel's questions answered by the founder's own Claude Code

The founder, 2026-10-23: *"I thought you were going to use the local environment to create this, and in local we can
use my Anthropic Max plan."* `make backtest` (spec 062) walks a back-test entry through the KEEL door: the founder
signs up at `/signup`, and keel-cloud answers every job on Keel's own Anthropic key. That account ran out of credits
on 2026-10-23 with 27 of 28 entries unrun. Keel's other door already exists: the founder who brings their own AI says
*keel connect* to a CLI, approves the device at `/connect`, and keel-connect-skill's runtime answers every job on that
CLI's model -- S-012 measures that whole journey (spec 019). This spec lets the back-test walk through that door on
this machine, with the founder's own Claude Code login, so the 27 entries run on the plan the founder already pays
for. **Scope: keel-e2e-eval only (`evals/backtest.py`, `evals/run_backtest.py`, the Makefile, one runner script in
`scripts/`); nothing in keel-cloud, keel-web or keel-connect-skill changes; no mark moves; the KEEL door keeps
working exactly as today. Build lean: `make unit` once; one live entry through the host door as the acceptance.**

## Rules

- **FR-1 `make backtest DOOR=host ENTRY=<id>` (default `DOOR=keel`).** On `DOOR=host` the key check is skipped and
  `KEEL_BACKTEST_DOOR=host` reaches `evals/run_backtest.py`; `HOST=claude` is the only host this spec builds (the
  value is recorded; another host is refused by name, as `agent_host.journey_host` refuses). `DOOR=keel` behaves as
  spec 062 built it, byte for byte.
- **FR-2 The runtime, started by the back-test.** S-012's first rule (*no implementation here ever starts the
  runtime*) is S-012's measurement of the host's own behaviour; the back-test measures Keel's questions, not the
  connect flow, so the back-test starts keel-connect-skill's runtime itself, from the sibling checkout
  `/Users/athulrajeev/Documents/projects/keel-connect-skill` (its `VERSION` and `RUNTIME_VERSION` recorded in
  `versions.json`): `python -m keel_runtime connect --base-url <this stack's cloud base> --executor claude --host
  claude --home <run_dir>/keel_home --no-browser`, stdout and stderr to `<run_dir>/keel_home/launch.log`, with the
  founder's own Claude Code login -- `CLAUDE_CONFIG_DIR` left to the caller's shell (the founder's `~/.claude`), or
  `CLAUDE_CODE_OAUTH_TOKEN` passed through when the shell carries one (`claude setup-token`'s long-lived token). The
  model is the CLI's default unless `MODEL=<slug>` is given (the runtime's own `--model` path, as S-012 passes
  `runtime_model`); the choice is recorded in `versions.json` and `backtest.md`'s header. No key, token or login is
  ever logged, written to the run or echoed.
- **FR-3 Sign-in through the door.** `Backtest.sign_in` on `DOOR=host`: wait for the launch log's `KEEL_USER_CODE=`
  (`agent_host.user_code_in`, `read_launch_log`; up to 90 s), then the back-test founder (spec 062's identity) signs in
  with the code (`Auth.sign_in_with_code`), lands on `/connect?user_code=…` and approves exactly as S-012 does
  (reuse its steps, not a copy); then `/v2/me` reads the door's `aiPath` (`OWN`), the heartbeat reaches its connected
  state (`agent_host.read_heartbeat`) before anything is asked of Keel, and `backtest.md`'s header says *answered by
  the founder's own Claude Code (host door)*. The KEEL-only assertions (the grant, *Keel's AI is ON* in the cloud log,
  `creditsAvailable`) are the KEEL door's alone and are not run here; their place is taken by: every job's
  `execution.host` is `claude` and its model is named (keel-cloud's interactions, as `keel_host.jobs_with_their_execution`
  reads them), and the cost section reads the CLI's own usage where it reports one, else *not priced on this door*.
- **FR-4 Patience.** The job wait is the host's (`agent_host.host_type("claude").keels_ai_job_wait_s`, 660 s) or
  longer where a back-test leg already waits longer; a job the CLI refuses for the plan's limit (the runtime's launch
  log names it: a 429, *rate limit*, *usage limit*, *try again at*) is retried by the runtime as it does today, and the
  back-test's `RETRIES` press *Try again* as on the KEEL door; a run that still stops on the limit ends with the
  finding *stopped by the plan's limit at <time>* in `backtest.md`, so the runner can wait and rerun that entry.
- **FR-5 Teardown.** The runtime is stopped (SIGTERM, then SIGKILL after 10 s) when the journey ends, passed or not;
  the heartbeat's last state and the launch log stay in the run; `make down` finds no runtime of ours alive.
- **FR-6 The runner.** `scripts/backtest-host.sh <id>…` runs the given entries one after another through the host
  door (`make down` first; never beside another eval run -- it waits while any `pytest evals` runs), logs each to
  `runs/backtest-host/<id>.log`, and on a run that ended *stopped by the plan's limit* sleeps until the named time (or
  30 min) and reruns that entry, at most three times, before moving on. It prints one line per entry: the id, the run
  directory, steps, bad, the decision label.
- **FR-7 Tests.** `make unit` green: the door switch (`DOOR=keel` unchanged, `DOOR=host` with a fake runtime that
  writes a user code and a heartbeat into `keel_home`), the sign-in leg's assertions on a fixture `/v2/me`, the
  teardown, the runner's limit parsing. The live acceptance: `make backtest DOOR=host ENTRY=08-fresco` on this
  machine, end to end, its `backtest.md` and `backtest.json` written, every job `execution.host: claude`.

## Acceptance

1. `make unit` green with the new tests; `make backtest ENTRY=…` without `DOOR` still refuses on a missing key, as
   today.
2. One live entry through the host door completes on this machine; hand back its run directory, the decision, the
   steps/bad counts and the cost section.
3. No mark or version moved.
