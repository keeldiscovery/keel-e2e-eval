# Tasks: Copilot, host and thinker

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Branch**: `016-copilot-e2e`

`make unit`: **571** before, **634** after, green.

## Phase 1 — read before writing anything

- [X] T001 `AGENTS.md`, `README.md`, and what the two of them already claim about Copilot.
- [X] T002 `specs/014-copilot-executor/` and `runs/20260909T061537Z-instructions-copilot` — the
      marks to compare against, and DRIFT #53–#56.
- [X] T003 `specs/013-skill-distribution/` and `stack/containers/acceptance/run-acceptance.sh` —
      the pattern for leg one, **and the finding that it has never run**: all four run records read
      `"result": "skipped"` for both hosts, and its "did the skill run" check is two greps over the
      model's own reply.
- [X] T004 `evals/test_s004_stranger_who_gives_orders.py`, `evals/preludes.py`,
      `evals/test_s001_smoke.py`, `harness/connect.py`, `harness/browser.py`.
- [X] T005 keel-runtime `specs/005-copilot-executor/` and `keel_runtime/executor.py`'s
      `CopilotExecutor` — the flags, `COPILOT_AUTH_MARKERS`, C-5's unexercised pin, C-7.
- [X] T006 keel-connect-skill `SKILL.md` (the one `--host copilot` line) and `dist/plugin`;
      keel-cloud `canon/designs/keel-skill-design.md` §5.5.

## Phase 2 — measure the machine before writing the run that depends on it

Each of these was a real measurement on 2026-09-10, and each changed a decision.

- [X] T007 `copilot --help`, `copilot help environment`, `copilot skill --help`,
      `copilot plugin --help`. Findings: `--allow-tool`, `--usage-output-file`,
      `--no-custom-instructions` and `--model` all exist; **there is no `--bare`**;
      `COPILOT_HOME` moves "configuration and state files".
- [X] T008 **Does an isolated `COPILOT_HOME` keep the login?** Yes. The founder's stored OAuth
      credential is not under `~/.copilot`, so leg one's isolation is free and no token has to be
      copied anywhere. Recorded in the bundle by `credential_plan`.
- [X] T009 **Does `--model` accept a slug now?** Yes — **every** slug offered was accepted
      (`gpt-5.6-luna`, `gpt-5.1`, `gpt-5`, `gpt-4.1`, `gpt-5-mini`, `gpt-5-codex`,
      `claude-haiku-4.5`, `claude-sonnet-5`, `mai-code-1.1-flash`), where on 2026-09-09 every one
      was refused. **C-5 has never been exercisable before** (keel-runtime spec 005). One tiny
      call confirmed it end to end and cost **1 premium request**. The plan's own default is now
      `claude-sonnet-5`, which the CLI's resolver logs as *"Using default model"*.
- [X] T009a **Which model does the run pin?** Two, for two subjects, and they had to differ
      (`runs/DRIFT.md` #59). The **host** keeps the founder's own default `claude-sonnet-5`,
      because leg one asks what a founder's own Copilot does with the skill. The **runtime** pins
      `gpt-5.6-luna` through `KEEL_COPILOT_MODEL`, because on `claude-sonnet-5` keel-runtime cannot
      read an answer at all — and because it is the model spec 014's router chose, which makes the
      instruction-eval comparison one measurement rather than two.
- [X] T010 **Is the model probe free?** Yes: `-p ""` with an accepted slug reaches the
      empty-prompt check and is refused there, with a usage file reading
      `totalPremiumRequestCost: 0`. So `model_accepted` can never buy inference by accident.
- [X] T011 **Do the two install commands work against the real marketplace?** Yes, into a throwaway
      `COPILOT_HOME`: *Marketplace "keel" added successfully* / *Plugin "keel" installed
      successfully. Installed 1 skill.* And `copilot skill list --json` prints
      `{"name": "keel-connect", "source": "plugin", "path": ".../installed-plugins/keel/keel/skills/keel-connect"}`.
      The measured shape is pinned in `tests/test_s012_copilot_host.py`. Installing costs no
      premium requests, so proving the path before spending anything was free.

## Phase 3 — the harness

- [X] T012 `harness/copilot_host.py` — `readiness`, `model_accepted`, `credential_plan`,
      `CopilotHost` (env, `write_home_config`, the two install commands, `skill_list`), `say`,
      `CopilotRun` (premium requests, model, tools), `find_skill`/`describes_a_plugin`, and the
      readers for the heartbeat and the launch log.
- [X] T013 `stack/runtime.py`: an optional `home=` on `status`, `disconnect_via_skill_script` and
      `disconnect`. Default unchanged, so no existing caller moved.
- [X] T014 `evals/test_s012_copilot_host_and_thinker.py` — both legs, `_walk_stage_live`,
      `_agent_answers`.
- [X] T015 `tests/test_s012_copilot_host.py` — **37 stackless tests**, every one of them a
      property that would otherwise only be observable during a paid run.

## Phase 4 — the amendment AGENTS.md's own rule requires

- [X] T016 `AGENTS.md`: **two named LLM places become three**, with the argument written out
      (§5.5 has a part nobody could measure; a gate with an unmeasurable part is not a gate).
      The rule asks for exactly this — *"a third would have to be argued for and added to this
      line rather than quietly written"* — so the sentence and the test moved in one commit.
- [X] T017 `tests/test_scenario_set.py`: twelve scenarios, two live, and a new test that fails if a
      live scenario is not named in `AGENTS.md`.

## Phase 5 — the harness fault the first attempt found

- [X] T018 **`/` no longer redirects a stranger to `/login`.** keel-web spec `015-landing-page`
      FR-001 — *"`/` splits by session, not by redirect"* — landed at keel-web `d5d8645`, after
      this repository's last run of record. `evals/conftest.py::_capture_the_login_screen` waited
      fifteen seconds for that redirect inside a **session-scoped fixture**, so it took all twelve
      scenarios down, none of them for a reason in their own subject. Found on the first attempt at
      the live run, **before a single premium request was spent** — it fails in the fixture, ahead
      of the test body.
      A harness fault, not a `runs/DRIFT.md` entry: keel-web changed a thing keel-web owns, said so
      in its own spec, and left `/login` itself untouched. Fixed by opening `/login` directly (as
      `Auth._goto_login` always has, which is why signing in never noticed) and by capturing and
      asserting the stranger's own door beside it rather than dropping it.
- [X] T019 `tests/test_the_strangers_door.py` — 5 stackless tests holding the fix, including that
      the `/` visit is not quietly dropped and that a keel-web which put the redirect back would
      read as red.
- [X] T020 The deterministic smoke re-run as a rehearsal, free, before spending anything: it
      proves sign-in, the walk, the invitation, the answer, the reading and the overview all still
      work at these sibling HEADs, so the paid run's only unknowns are the Copilot-shaped ones.

## Phase 6 — the runs of record

- [X] T021 `make up`, `make eval-live K=s012`, `make down`.
- [X] T022 `make instruction-eval HOST=copilot N=1` with `KEEL_COPILOT_MODEL` pinned, once.
- [X] T023 `runs/DRIFT.md` for anything found; `README.md` for both runs.

## What the runs said

**S-012, `runs/20260910T211318Z-s012-copilot-host-and-thinker-live`** -- leg one **green** (plugin
installed from the real marketplace, `copilot skill list` names it as a plugin skill, Copilot
called the `skill` tool and then ran the script with `--host copilot`, heartbeat
`awaiting_approval`, the code confirmed by the eval cloud, approved in the browser,
`already_connected` on the second ask); leg two **red at SOLUTION**, four attempts, every one
`INVALID_LLM_RESPONSE: result.statement: longer than maxLength 400`. PROBLEM went the whole way --
framed, assumptions applied, card reviewed and approved, zero refusals. 2 hosting + 7 thinking
premium requests recorded.

**The instruction eval, `runs/20260910T213217Z-instructions-copilot`** -- `KEEL_COPILOT_MODEL=gpt-5.6-luna`,
131 cases, 35 min, 131 premium requests, **PASSED**: anchoring 95.4 %, recall 81.8 %, refusals 0,
BRIEF 7/7, errored 0, at `MARKS_VERSION` 5 unmoved.

**Findings**: `runs/DRIFT.md` **#58** (`keel status` names the caller's executor, not the
runtime's), **#59** (no `phase` on Anthropic-vendored events -- every job fails on the plan's
default model), **#60** (a `JOB_FAILED` says "your agent went away" while `diagnostic` names the
real cause), **#61** (the single recovery pass does not check the field it named got shorter).
**#54 amended** (the commercial-screen collapse was mostly one sample: 61.5 % -> 80.8 % with
nothing changed on either side) and **#56 amended** (the `proxy` leak did not recur and is not
fixed).

**The gate** (keel-cloud `canon/designs/keel-skill-design.md` §5.5): part 3 **met for the first
time**; part 2 **not met**, because the journey does not finish. Copilot remains "runs,
unmeasured" -- for a narrower reason than on 2026-09-09, and with both blockers named.

**Three harness faults of this repository's own**, each fixed with stackless tests: the stranger's
door (keel-web spec 015 removed the `/login` redirect and a session fixture waited for it),
`harness/refusals.py`'s blindness to a terminal job failure, and a scenario reading a name nothing
defined. `make unit` **571 -> 634**.
