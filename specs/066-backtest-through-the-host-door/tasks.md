# Tasks 066

Built by Claude Opus 5.5 against keel-cloud-docs master `720f67ca` (corpus revision 14), keel-web `48068d1`,
keel-connect-skill `c677950` (`VERSION` 2.5.0, `RUNTIME_VERSION` 0.8.0+3988131), Claude Code 2.1.300; `MARKS_VERSION`
20 and every other version unchanged.

- [x] T001 FR-1 `make backtest DOOR={keel,host}` (Makefile): an unknown `DOOR` refused by name first; the key check
  skipped on `DOOR=host` only; `KEEL_BACKTEST_DOOR=host KEEL_BACKTEST_HOST=<HOST or claude>` (and `KEEL_BACKTEST_MODEL`
  when `MODEL=` is said) reach `evals/run_backtest.py`. `DOOR=keel` and no `DOOR` expand to spec 062's command line
  byte for byte (held by `make -n` in a test). `evals/backtest.door / host / door_refusal`: another host refused by
  name, as `agent_host.journey_host` refuses one.
- [x] T002 FR-2 `evals/backtest.HostRuntime` + `runtime_argv` + `runtime_env`: `python -m keel_runtime connect
  --base-url <cloud> --executor claude --host claude --home <run>/keel_home --no-browser --credential-backend file`,
  from the checkout `stack.toml` names (`/Users/athulrajeev/Documents/projects/keel-connect-skill` here), stdout and
  stderr to `<run>/keel_home/launch.log`. `connect_skill_versions` (VERSION, RUNTIME_VERSION, commit) and the CLI's
  version and `loggedIn` / `authMethod` (nothing else of `claude auth status`) go into `versions.json`'s
  `backtest door` block and `backtest.json`'s `door`; `host_readiness` refuses before the stack boots when `claude` is
  missing or logged out with no `CLAUDE_CODE_OAUTH_TOKEN`.
- [x] T003 FR-3 `Backtest.sign_in_through_the_host`: the runtime started, `KEEL_USER_CODE=` / `KEEL_VERIFICATION_URI=`
  waited for up to 90 s (`agent_host.user_code_in`, `read_launch_log`), the heartbeat held to `awaiting_approval`, then
  S-012's own two steps -- `preludes.sign_in_with_the_code` and `preludes.approve_at_connect`, factored out of S-012
  (its step names and assertions unchanged) -- and `preludes.own_ai_door`; then `/v2/me` held to `aiPath` `OWN` and the
  back-test founder (`host_door_refusal`) and the heartbeat to `connected` (`read_heartbeat`) before anything is asked.
  After the walk, `check_the_host_answered`: every answered job's `execution.host` is `claude` and its model is named
  (`keel_host.jobs_with_their_execution`, `host_door_jobs`). The cost section reads the CLI's own usage
  (`cli_usage`), else says *not priced on this door*; `backtest.md`'s header says *answered by the founder's own Claude
  Code (host door)*. The KEEL-only checks (the key in the cloud log, fake-for, `creditsAvailable`) are not run.
- [x] T004 FR-4 patience `max(PATIENCE, host_type("claude").keels_ai_job_wait_s / 60)` = 11 (660 s); `RETRIES` as on the
  KEEL door; `plan_limit` / `limit_in` read a 429, *rate limit*, *usage limit*, *try again at*, *hit your limit*,
  *limit reached* and the time named; a run that did not pass with the limit seen ends *stopped by the plan's limit at
  <time>* in `backtest.md` (`limit_stop` in `backtest.json`).
- [x] T005 FR-5 `HostRuntime.stop`: the heartbeat kept as `keel_home/runtime.heartbeat.last.json`, SIGTERM, SIGKILL
  after 10 s, the credential file removed, the teardown in `backtest.json`'s `runtime`; `Backtest.finish` stops it
  before the transcript, and `run_backtest.py` again in a `finally` (idempotent).
- [x] T006 FR-6 `scripts/backtest-host.sh <id>...`: waits while a `-m pytest evals` process runs, `make down`,
  `make backtest DOOR=host ENTRY=<id>` into `runs/backtest-host/<id>.log`, one line (`python -m evals.backtest summary`:
  id, run dir, steps, bad, decision), and on *stopped by the plan's limit* sleeps until the named time or 30 min
  (`... resume`) and reruns, at most three times. It prints nothing else.
- [x] T007 FR-7 `tests/test_backtest_host.py` (26): the door switch and `make -n`, the runtime's argv and env, a fake
  runtime that prints a code and a heartbeat into `keel_home` and connects, its teardown by SIGTERM and by SIGKILL, the
  sign-in leg on fixture `/v2/me` (OWN passes, KEEL stops), the jobs on the host, the CLI's usage, the limit's words
  and times, the host door's markdown, the runner's line and its run with a fake `make`. S-012's
  `tests/test_keels_ai_cell.py` door tests read the two steps where they now live (judgement call 10).
- [x] T008 Acceptance (below).

`make unit`: master `677e96f` 3,079 passed, 53 skipped -> 066 3,105 passed, 53 skipped (+26, the new file).

## Judgement calls

1. **The runtime started by the back-test** is keel-connect-skill's own `keel_runtime` package from the checkout
   `stack.toml` names (the spec's path on this machine), run as `<this venv's python> -m keel_runtime connect ...` with
   `cwd` and `PYTHONPATH` the checkout -- not the skill's `keel_connect_check.py` (the back-test measures Keel's
   questions, not the connect flow) and not `stack/runtime.py`'s shared home: its home is the run's `keel_home/`.
2. **How the model pin travels: it does not, from here.** keel-runtime has had no session-wide `--model` since its spec
   009 (`connect --help`: no flag; *"the model a job runs on comes with the job, from the cloud's routing table"*), and
   S-012's `ClaudeHost._runtime_model_env` passes nothing either. So every job runs on keel-cloud's routing table's
   `model.claude` / `effort.claude` (routing v13: light `claude-haiku-4-5-20251001`, standard `claude-sonnet-5-5` at
   `medium` -- the KEEL door's own pins), else the CLI's default. `MODEL=` is refused by name rather than recorded as
   a pin that never happens; the per-job `model_used` is in the transcript.
3. **The device credential stays in the run's home and dies there**: `--credential-backend file` (the default `auto`
   could write a local stack's agent credential into the founder's keychain, or block on a keychain prompt), and
   `credentials.json` is deleted at teardown, so no token is left in `runs/`.
4. **The runtime's environment** is the caller's shell through `agent_host.scrub_session` (this harness's own Claude
   Code session markers off, as S-012 does), `CLAUDE_CONFIG_DIR` put back when the caller set one, and
   `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `KEEL_ANTHROPIC_API_KEY`, `KEEL_RUNTIME_PATH`, `KEEL_HOME`,
   `KEEL_BASE_URL`, `PYTHONPATH` dropped -- an API key in the shell would bill an API account in place of the founder's
   login. `CLAUDE_CODE_OAUTH_TOKEN` passes through. The env is never in a repr (pytest's `-l` prints locals).
5. **What the CLI reports as usage** (the founder's plan consumption, the coordinator's addition): Claude Code's
   `result` event, which the runtime keeps per job as `keel_home/jobs/<id>/envelope.json`. Fields read, per job and
   summed: `total_cost_usd` (a list-price equivalent the plan covers; nobody is billed it), `usage.input_tokens`,
   `usage.output_tokens`, `usage.cache_read_input_tokens`, `usage.cache_creation_input_tokens`, `modelUsage.<model>`'s
   `inputTokens` / `outputTokens` / `cacheReadInputTokens` / `cacheCreationInputTokens` / `costUSD`, plus `num_turns`,
   `duration_ms` and `is_error`; `backtest.md`'s cost section lists every job (screen, id, dollars, the four usage
   counts, model, turns) under the sums. Note `modelUsage.cacheCreationInputTokens` and `usage.cache_creation_input_tokens`
   disagreed on the live run (the latter is the larger); both are kept. keel-cloud's `actual_cost_micro_usd` is not set on this door, so the
   summed micro-USD line reads 0 and the section says so.
6. **Patience**: `host_type("claude").keels_ai_job_wait_s` is 480 s (the spec's 660 s is `KeelHost`'s); the back-test's
   `PATIENCE` 11 (660 s) is already longer, so the host door keeps it -- the spec's *"or longer where a back-test leg
   already waits longer"*.
7. **The launch log is `launch.log`** (FR-2's name), read with `agent_host.read_launch_log(home, "launch.log")` -- the
   reader gained a `filename` argument whose default is the skill's log, so every other caller is unchanged.
8. **Where the plan's limit is read**: the runtime prints no job failure to its log, so `plan_limit` reads the launch
   log, every job keel-cloud did not complete (its error text) and every `is_error` envelope in the runtime's home. The
   finding *stopped by the plan's limit at <time>* is written only when the run did not pass; a limit met on a run that
   passed is recorded as such.
9. **The jobs on the host are the answered ones**: a COMPLETED job must name `claude` and a model; an execution naming
   any other host is bad; a job cancelled or failed with no execution at all (nothing answered it) is listed apart.
10. **S-012's two steps were factored, not copied**: `preludes.sign_in_with_the_code` (the sign-in and the *code
    survived the login* assertion) and `preludes.approve_at_connect` (frame B, the code on screen, approve, connected).
    S-012's step names, messages and order are unchanged; five source-shape tests in `tests/test_keels_ai_cell.py` that
    pinned the moved lines now read the call sites in S-012 (same order) and the bodies in `preludes`.
11. **`Journey.keels_door` stays False on the host door**, so L1 and the format screen are held as an own-AI account's
    are on the golden journeys (one line and *Lock and approve*; the other two formats greyed *needs Keel's credits*).
12. **The bundle keeps its name** (`runs/<stamp>-backtest-<id>/`), so `make gallery`'s newest-run pick sees host-door
    runs; the door is in `versions.json` (`backtest door`) and `backtest.json` (`door`, `spec: "062+066"`).
13. **One eval stack at a time is waited for on `-m [p]ytest evals`**: another session's waiting shell whose own command
    line said `pgrep -f "pytest evals"` matched itself (it would have held any waiter forever), so the runner, and this
    build's own wait for the acceptance, match the python process only.
14. **A boot that fails in `run_backtest.py`'s fixture leaks what it started** (found on the first attempt: another
    session's postgres held 55432 and this run's stub issuer was left on 18090 until `make down` from the worktree).
    Spec 062's fixture is the KEEL door's too and is left as it is; recorded here, not changed.

## Acceptance

1. `make unit` green (above); `make backtest ENTRY=08-fresco` with no `DOOR` and no key still refuses with spec 062's
   sentence (exit 2, held in `test_door_keel_is_spec_062_byte_for_byte_and_door_host_asks_for_no_key`).
2. LIVE, `make backtest DOOR=host ENTRY=08-fresco` from the worktree, 2026-10-23 11:45:32Z -> 11:51:33Z (6 min, not
   the 20-40 expected): run `runs/20261023T114546Z-backtest-08-fresco/` (worktree), keel-cloud `720f67ca`, keel-web
   `ca973a0`. **The host door held end to end through the device code**: the runtime printed `KEEL_USER_CODE=`, the
   founder signed in with it and approved at /connect, `/v2/me` read `aiPath` OWN, the heartbeat `connected`, and all 19
   completed jobs report `execution.host: claude` with a model (`claude-sonnet-5-5` x14, `claude-haiku-4-5-20251001`
   x5); one THEMES job CANCELLED `AGENT_DISCONNECTED` with no execution (the teardown stopped the runtime mid-job);
   bad `[]`. `backtest.md` and `backtest.json` written. **The walk stopped at step 186 of 186 (1 bad), _the report
   after 4 answers_ (spec 052 FR-7)**: `report_marks.insight_faults` expects *Only 0 of the 1 were asked here: 1 had
   already been asked about Importance, the first rung they failed.* where keel-web draws *None of the 1 were asked
   here: all 1 had already been asked about Importance.* (keel-web 102's line at zero) -- a harness-vs-keel-web drift
   on Adoption friction, not a host-door fault, and outside this spec (no mark moves). Decision at the stop
   **KEEP_INTERVIEWING** (LOW; 4 answered). Cost: keel-cloud priced nothing (0 micro-USD); the CLI reported **$0.75**
   over 19 envelopes -- usage summed `input_tokens` 108, `output_tokens` 19,475, `cache_read_input_tokens` 86,358,
   `cache_creation_input_tokens` 159,762. The plan's limit was not met. Teardown: SIGTERM, exit 0, not alive after,
   `credentials.json` removed; `runtime.heartbeat.last.json` and `launch.log` kept; no `keel_runtime connect` process
   alive after; no token in the run. `claude auth status` kept as `loggedIn: true`, `authMethod: claude.ai`.
3. No mark or version moved (`MARKS_VERSION` 20, `POLICY_VERSION`, corpus revision 14).
