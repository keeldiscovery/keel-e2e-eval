# Tasks: the journey through a host

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Branch**: `journey-through-a-host`

`make unit`: **638** before, **690** after, green.

## Phase 1 — read before writing anything

- [X] T001 keel-cloud `canon/designs/e2e-matrix-design.md` §5.1, §5.3, §11 and decision 5 — what a
      cell is, and that the scenario it runs is *"S-001, the founder's journey, through the host"*.
- [X] T002 `specs/016-copilot-e2e/` (spec, plan, tasks) — the shape this repeats, and the run of
      record it must not invalidate.
- [X] T003 `evals/test_s012_copilot_host_and_thinker.py` and `harness/copilot_host.py`, line by
      line: which of its rules are Copilot's and which are the journey's. Answer: the three rules
      at the top, the artefact readers, the marketplace constants and the environment discipline
      are the journey's; the model probe, the usage file, `skill list --json` and the credential
      precedence are Copilot's.
- [X] T004 `evals/test_s009_skill_distribution.py` — **and the finding that the Claude-side
      marketplace install does not exist anywhere in this repository.** S-009 *copies* four
      packaging trees to where four installers put them and says so in its own docstring
      (*"installing the plugin through `claude plugin install` … would need those two host CLIs, a
      marketplace and a network — that is §10.2's containerised bed, not this scenario"*). The only
      `claude plugin marketplace add` in the tree is in `README.md`. So the Claude instance's leg
      one is genuinely new ground, not a copy of S-009's.
- [X] T005 `evals/test_s001_smoke.py`, the `Makefile` (`eval-live`, and `instruction-eval`'s
      existing `HOST=` for its own two hosts), `README.md`, `runs/DRIFT.md`'s referee stance.
- [X] T006 keel-runtime `keel_runtime/executor.py` — `ClaudeCodeExecutor._build_argv` (**no
      `--model` anywhere**), `_CLAUDE_ENV_PREFIXES`, `self.last_envelope = result_event` (**no
      `executor` key**), and `CopilotExecutor._envelope` beside it for the contrast. And
      `config.resolve_executor` / `canonical_executor_name`, which is why `claude-code` from the
      skill reads as `claude` in the log.
- [X] T007 keel-connect-skill `SKILL.md` and `scripts/keel_connect_check.py` — the one D5 line for
      Copilot, and `detect_host`'s table, which is how Claude arrives at `source=flag` without a
      line of its own in `SKILL.md`.

## Phase 2 — measure the machine before writing the run that depends on it

Each of these was a real measurement on 2026-09-10 against Claude Code **2.1.268**, each cost
nothing, and each changed a decision.

- [X] T008 `claude --help`, `claude plugin --help`, `claude plugin install --help`,
      `claude auth --help`. Findings: `--allowedTools`, `--permission-mode dontAsk`,
      `--setting-sources`, `--output-format stream-json --verbose` and `--model` all exist;
      **there is no `--no-custom-instructions`** and **no `claude skill list`**; `--bare`,
      `--safe-mode`, `--disable-slash-commands` and `--restricted` would each make the skill
      invisible or the script unrunnable.
- [X] T009 **Do the two install commands work against the real marketplace, into an isolated
      `CLAUDE_CONFIG_DIR`?** Yes, and with **no `-y`** — the founder's own two commands, verbatim:
      *"✔ Successfully added marketplace: keel (declared in user settings)"*, *"✔ Successfully
      installed plugin: keel@keel (scope: user)"*. Costs nothing.
- [X] T010 **Where does the install declare the plugin?** `<CLAUDE_CONFIG_DIR>/settings.json`,
      `{"extraKnownMarketplaces": {"keel": …}, "enabledPlugins": {"keel@keel": true}}` — the
      **user** source. Which is why the run passes `--setting-sources user`: exactly enough to see
      the plugin, exactly little enough to keep this repository's own settings out.
- [X] T011 **What proves the skill is there, and that it came from the plugin?**
      `claude plugin details keel` → *"Component inventory / Skills (1)  keel-connect"*, under
      *"Source: keel@keel"*. The inventory is the plugin's own, so this is a stronger reading than
      Copilot's `source` field, not a weaker one. `claude plugin list --json` gives the machine
      -readable install record beside it (`{"id": "keel@keel", "version": "1.0.0", "scope":
      "user", "enabled": true}`).
- [X] T012 **Does an isolated `CLAUDE_CONFIG_DIR` keep the founder's login?** **No — and this is
      the finding of the day.** `claude auth status` in a fresh config dir:
      `{"loggedIn": false, "authMethod": "none"}`. Against `~/.claude`:
      `{"loggedIn": true, "authMethod": "claude.ai"}`. With `ANTHROPIC_API_KEY` in the shell and
      the same fresh dir: `{"loggedIn": true, "authMethod": "api_key", "apiKeySource":
      "ANTHROPIC_API_KEY"}`. So the Copilot half's *"isolation is free"* does **not** carry over,
      a Claude cell needs a token in the caller's own shell, and `readiness()` can say so for
      nothing before anything is created.
- [X] T013 **Is there a free `--model` probe?** No. Copilot's is free because an impossible slug is
      refused against a catalogue before inference; every Claude equivalent starts a session.
      `model_accepted` returns `True` and its docstring says it has measured nothing — better than
      a probe that pretends.

## Phase 3 — the harness

- [X] T014 `harness/agent_host.py` — the interface, the `KEEL_JOURNEY_HOST` axis, the bundle name,
      the shared artefact readers, the session-marker scrub, `HostRun`, `build_host`/`readiness`.
- [X] T015 `harness/claude_host.py` — `readiness`, `credential_plan`, `skill_proof`,
      `skills_in_details`, `installed_plugin_ids`, `ClaudeRun`, the `-p` argv.
- [X] T016 `harness/copilot_host.py` — reseated on the interface, every public name kept, the argv
      unmoved.
- [X] T017 `evals/test_s012_journey_through_a_host.py` — renamed, parameterised, every assertion
      the one that was there.
- [X] T018 `evals/conftest.py`, `pytest.ini`, `harness/evidence.py::write_host`,
      `harness/scoring.py::write_facts`, `Makefile`.
- [X] T019 `tests/test_journey_through_a_host.py` — **52 stackless tests**; and
      `tests/test_s012_copilot_host.py`'s 37 kept passing unchanged but for one filename, which is
      what proves the Copilot instance did not move.
- [X] T020 `tests/test_scenario_set.py` — the twelfth scenario's new filename, the live set, and
      `eval-live`'s recipe now being more than one line.

## Phase 4 — the documents

- [X] T021 `AGENTS.md` — the third named LLM place is **widened, not multiplied**, and says so:
      the amendment rule permits exactly this, and a fourth place would still have to be argued
      for.
- [X] T022 `README.md` — the two commands, what a Claude run needs from the founder's shell, and
      the S-012 section rewritten as *the journey through a host*.

## Phase 5 — the run, which is the founder's to spend

- [ ] T023 `make up`, `make eval-live K=s012 HOST=claude`, `make down`. **Not run here.** It needs
      `ANTHROPIC_API_KEY` (or `CLAUDE_CODE_OAUTH_TOKEN` from `claude setup-token`) exported in the
      caller's own shell — see T012 — and it is the design's §13 step 4, one paid run.
- [ ] T024 `make eval-live K=s012` (Copilot) again at these commits, to confirm the refactor left
      the measurement where it was. Also the founder's to spend; the argv is unchanged and its 37
      stackless tests are green, which is the most that can be said without spending.
- [ ] T025 Whatever T023 finds → `runs/DRIFT.md`, `README.md`, and this file's *What the runs said*.
