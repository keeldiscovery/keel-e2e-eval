# Feature Specification: the journey through a host

**Feature Branch**: `journey-through-a-host`

**Created**: 2026-09-10

**Status**: Implemented, **not yet run live on either host**. `make unit` **638 → 690**, green.
The Copilot instance is today's command unchanged (`make eval-live K=s012`) and its spec 016 run
of record still stands; the Claude instance is new and **has never been run** — §13 step 4 of the
design spends one run on it, and this spec's own quickstart says what that run needs from the
founder first.

**Input**: keel-cloud `canon/designs/e2e-matrix-design.md`, §5.1, §5.3, §11 and decision 5. The
matrix's three axes are an OS, a host and a Python, and the design is explicit about what each
cell runs:

> *"The scenario each cell runs is **S-001, the founder's journey, through the host** — the S-012
> shape (plugin from the marketplace into a fresh host home, three words to the host, device
> approval in the browser, the runtime on that host's executor, every job answered by that host's
> model), parameterised by host rather than a Copilot-only scenario. S-012 becomes the Copilot
> instance of it; the Claude instance is new and is mostly a rename."*

And decision 5: *"the cells install from the public marketplace, never from a checkout. A cell
that used a checkout would test a plugin no founder has."*

The siblings, read at these commits:

| Sibling | What this feature depends on |
|---|---|
| keel-cloud | `canon/designs/e2e-matrix-design.md` §5.1/§5.3/§11 and decision 5; `canon/designs/keel-skill-design.md` §5 (two hosts, co-equal) and §5.5 (the four-part "supported" gate). |
| keel-web | `/connect`, the device-approval screen — unchanged, and the same screen for both hosts. |
| keel-runtime | `resolve_executor`'s step 1 and `canonical_executor_name` (`claude-code` → `claude`); `ClaudeCodeExecutor`, which takes **no model**; `CopilotExecutor`, which pins one and stamps `executor` on every job envelope. |
| keel-connect-skill | `SKILL.md`'s one Copilot line, `keel_connect_check`'s `--host` and its host-detection table, and the `keel` plugin on the public `keeldiscovery/keel-marketplace` — one repository that serves **both** hosts. |

## What changes, stated first

S-012 was a Copilot scenario. It is now **the** scenario, and the host is a parameter:
`KEEL_JOURNEY_HOST`, set by `make eval-live K=s012 HOST=claude|copilot`, default `copilot`.

Nothing about what is asserted changed. The legs are the same legs, in the same order, against the
same shapes, on the same wire; the Copilot argv is unchanged flag for flag, so the Copilot
instance is still the run that produced `runs/20260910T211318Z-s012-copilot-host-and-thinker-live`.
What moved is **where the difference between two hosts is allowed to live**: `harness/agent_host.py`,
and nowhere else.

### The four differences, each measured before a line was written

Every one of these was measured on 2026-09-10 against Claude Code **2.1.268**, for nothing.

1. **An isolated home does not keep the founder's login, and this is the headline.**
   `COPILOT_HOME` moves Copilot's configuration while the stored OAuth credential stays outside
   it, so spec 016's isolation was free. `CLAUDE_CONFIG_DIR` is not like that: `claude auth
   status` in a fresh config dir answers `{"loggedIn": false, "authMethod": "none"}` where the
   same command against `~/.claude` answers `{"loggedIn": true, "authMethod": "claude.ai"}`. **A
   Claude run therefore needs a credential in the caller's own shell.** `readiness()` probes
   exactly that — `claude auth status` in a throwaway empty config dir — and skips the scenario
   **by name, with the two commands that would fix it**, rather than letting a paid run discover
   it. Same rule as spec 013's T-5: the secret comes from the caller's shell, never from a file
   and never from a keychain this harness went looking in.
2. **There is no `claude skill list`.** The proof that the skill is present *and came from the
   plugin* is `claude plugin details keel`'s component inventory — `Skills (1)  keel-connect`.
   That is a **stronger** reading than Copilot's, not a weaker one: the inventory belongs to the
   plugin by construction, so a `keel-connect` sitting in a personal skills directory cannot
   satisfy it, which on the Copilot side takes an explicit `source` field to rule out.
3. **`--no-custom-instructions` does not exist on Claude Code**, and the three flags that would
   have the same effect (`--bare`, `--safe-mode`, `--disable-slash-commands`) all switch off skill
   discovery, which is the whole of leg one (spec 013's T-2 trap). So the rule *the referee's own
   instructions never reach the thing under referee* is kept by **where the host is run**: a fresh
   empty working directory outside this repository, for both hosts, plus `--setting-sources user`
   on Claude so the only settings that load are the fresh home's own — which is where `claude
   plugin install` writes the plugin's declaration (measured: `<CLAUDE_CONFIG_DIR>/settings.json`
   gains `enabledPlugins: {"keel@keel": true}`). Copilot keeps its flag as well.
4. **keel-runtime's Claude executor takes no model.** `ClaudeCodeExecutor._build_argv` never
   passes `--model` and there is no `KEEL_CLAUDE_MODEL`. So a Claude journey's runtime model is
   **recorded, not pinned**, and the bundle says so in those words. Copilot's C-5 pin
   (`KEEL_COPILOT_MODEL=gpt-5.6-luna`, `runs/DRIFT.md` #59) is unchanged and has no counterpart
   here; a pin this repository faked would be a fact about the referee.

### And one asymmetry found by reading, recorded rather than worked around

**keel-runtime names the executor in one of its two job envelopes.** `CopilotExecutor._envelope`
stamps `"executor": "copilot"` on every per-job envelope — the second, independent proof that
Copilot did the thinking, written per job by the process that ran it. `ClaudeCodeExecutor` passes
the `claude` CLI's own `result` event through unchanged (`self.last_envelope = result_event`), and
that event names no executor at all. So the per-job cross-check exists on one host and not on the
other. The scenario asserts it where it can be asserted and **records the absence in the bundle**
where it cannot, rather than quietly asserting less on both. It is not written up in
`runs/DRIFT.md`: that file is for what a *run* found, and no run has found this yet — the Claude
instance's first live run is where it becomes an entry, if the founder wants one.

## User scenarios

### S-012 — "the journey through a host" (live, `make eval-live K=s012 [HOST=…]`)

Identical for both hosts except where a host's name appears.

**Leg one — the host.**

1. A fresh host home is created under `runs/<stamp>-s012-journey-<host>/<host>-home/`
   (`CLAUDE_CONFIG_DIR` or `COPILOT_HOME`) and a fresh `KEEL_HOME` beside it. Nothing of the
   founder's own home is copied. Which credential answers is **measured and recorded**, per host.
2. `<cli> plugin marketplace add keeldiscovery/keel-marketplace` and `<cli> plugin install
   keel@keel` — that host's own two commands, against the real public marketplace, into that
   home. The two argvs are identical but for the binary, because one marketplace repository
   serves both hosts.
3. The CLI is asked whether it can see `keel-connect` and whether it came from the plugin —
   `copilot skill list --json`, or `claude plugin details keel`'s component inventory.
4. `<cli> -p "keel connect"`, with the two tool grants that host spells its own way
   (`Skill,Bash(python3:*)` / `--allow-tool skill --allow-tool 'shell(python3:*)'`), from a
   working directory outside this repository, with `KEEL_BASE_URL` naming the eval cloud,
   `KEEL_RUNTIME_PATH` scrubbed (T-1) and **the markers of the agent session this harness itself
   runs in scrubbed too** (see FR-005).
5. The traces, asserted in this order and none of them the host's prose: the heartbeat in
   `awaiting_approval`; the launch log's `KEEL_USER_CODE=` and `KEEL_VERIFICATION_URI=`; and
   `GET /v2/device-authorizations?user_code=` on the eval cloud answering 200, not yet approved.
6. The founder approves it at keel-web's `/connect`.
7. `<cli> -p "keel connect"` a second time → the skill's `already_connected`, asserted through the
   runtime's own `status`, with one loose check that the reply says *connected*.

**Leg two — the thinker.**

8. The runtime is on **that host's executor**, read off the runtime's own `KEEL_EXECUTOR=` startup
   line and never off `keel status` (`runs/DRIFT.md` #58), with `source=flag` asserted beside the
   name. It is the same chain on both hosts and it is the *skill's*: Copilot because `SKILL.md`
   carries the one D5 exception telling it to add `--host copilot`, Claude because the script's
   own host detection reads the `CLAUDECODE=1` its CLI sets for the shell it runs the script in.
   Either way the script passes an executor and the runtime records an explicit term. **Nothing in
   the scenario passes `--executor`.**
9. The founder's journey, exactly as spec 016 wrote it: three stages framed, reviewed and approved
   as-is; one person invited and answered; the reading read; *What this says*; the overview and one
   card opened. Shapes and absences only.
10. Zero refusals, every job `COMPLETED`, and what it cost **in that host's own unit** — premium
    requests for Copilot (C-7: never a dollar figure), dollars for Claude (and never converted into
    premium requests).
11. The runtime leaves the way a founder leaves it: the skill's own door out.

## Requirements

- **FR-001** One scenario, two hosts. `KEEL_JOURNEY_HOST` chooses; `copilot` is the default so the
  command that produced the spec 016 run of record still means what it meant. An unknown value
  **raises by name** rather than falling back — a typo that quietly ran the other host would spend
  the founder's money on a measurement nobody asked for.
- **FR-002** Nothing that is asserted changes: the same shapes, the same wire, the same runtime
  artefacts, and never the model's prose. The Copilot argv does not move a flag.
- **FR-003** Every difference between the two hosts lives in `harness/agent_host.py` and its two
  implementations. The scenario names a host in messages and in the bundle, and asks the interface
  for everything else.
- **FR-004** Each host is skipped **by name with its reason** (C-11) when its CLI is missing, will
  not run, or — Claude — could not authenticate the fresh home this run gives it.
- **FR-005** The environment each host is launched with drops `KEEL_RUNTIME_PATH` (T-1), both
  hosts' home variables, and the markers of the agent session *this harness* runs in
  (`CLAUDECODE`, `CLAUDE_CODE_*`, `AI_AGENT`, `COPILOT_CLI`, `COPILOT_AGENT_SESSION_ID`) — with
  `CLAUDE_CODE_OAUTH_TOKEN` kept, because it is a credential and not a handle. Not hygiene: the
  skill's own host detection reads exactly those names and *"two different answers means no
  answer"*, so a leaked marker would make the runtime fall through to `source=ambiguous-path` and
  FR-006's assertion would be measuring this repository's shell.
- **FR-006** The runtime ends up on the host's executor **because the skill put it there**, read
  off the startup line with `source=flag`. Nothing passes `--executor`.
- **FR-007** The run bundle is `runs/<stamp>-s012-journey-<host>/`, and `verdict.json`'s scenario
  is the same string.
- **FR-008** `versions.json` carries a `host` block: the host, the CLI version, the binary, the
  home variable and directory, the working directory, the expected executor, both models and how
  each was arrived at, and the measured credential. `facts.json` carries the same in one line, as
  a **string**, so the scorer skips it and a reader does not.
- **FR-009** The two spend units are never converted into each other.
- **FR-010** Nothing here writes to a sibling repository and no product code is fixed. Product
  faults go to `runs/DRIFT.md` — and only once a run has found one.

## What is deliberately not built

- **No `HOST=both`.** Two hosts are two measurements and are never averaged (§5.5's own rule).
- **No second scenario, and no second live entry in `AGENTS.md`.** A named place was *widened*,
  which the amendment rule permits explicitly; a fourth place would still have to be argued for.
- **No `KEEL_CLAUDE_MODEL` invented in this repository.** keel-runtime has no such knob; a
  referee that faked one would be recording a pin that never happened.
- **No free `--model` probe for Claude.** Copilot's is free because an impossible slug is refused
  against a catalogue before inference; Claude Code has no equivalent, so `model_accepted` returns
  `True` and says in its docstring that it has measured nothing. (A *wrong* `ANTHROPIC_API_KEY`
  likewise passes readiness — the CLI cannot validate a key for free either — and fails loudly on
  the first word.)
- **No change to `evals/preludes.py`, `harness/browser.py`, `evals/policy.py` or the acceptance
  bed.**
- **Not scored**, for S-008's and S-009's reason.
