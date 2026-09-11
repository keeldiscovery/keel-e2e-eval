# Implementation Plan: the journey through a host

**Branch**: `journey-through-a-host` | **Spec**: [spec.md](spec.md) | **Tasks**: [tasks.md](tasks.md)

## 1. Where the code goes

| File | What it is |
|---|---|
| `harness/agent_host.py` | **New.** The interface, and the only place the two hosts are told apart: `journey_host()`/`bundle_slug()` (the `KEEL_JOURNEY_HOST` axis), the marketplace constants, the readers for the runtime's own artefacts (heartbeat, launch log, `KEEL_EXECUTOR=` line, user code), the environment discipline, `HostRun`, and `AgentHost` with the install/say/skill-proof/credential contract. Everything in it was `harness/copilot_host.py`'s and was never Copilot's — it is the journey's. |
| `harness/claude_host.py` | **New.** Claude Code's half: `readiness` (which, `--version`, and `claude auth status` **in a throwaway empty config dir**), `credential_plan` (the same command in *this run's* home — measured, not reasoned), `skill_proof` (`plugin details` + `plugin list --json`), the `-p` argv, and `ClaudeRun` (dollars, tool-use blocks, `modelUsage`). |
| `harness/copilot_host.py` | Now an implementation of that interface. Its module functions keep their names and its argv does not move a flag: `tests/test_s012_copilot_host.py` passes **unchanged but for the scenario's filename**, which is the cheapest proof that the Copilot instance is still the same measurement. |
| `evals/test_s012_copilot_host_and_thinker.py` → `evals/test_s012_journey_through_a_host.py` | Renamed and parameterised. Every assertion is the one that was there. |
| `evals/conftest.py` | `run_dir` honours `@pytest.mark.bundle(<slug>)`. Four lines. |
| `harness/evidence.py` | `write_host(run_dir, record)` merges a `host` block into `versions.json`. |
| `harness/scoring.py` | `write_facts` writes a non-`Fact` entry through as it stands. |
| `Makefile` | `eval-live` gains `KEEL_JOURNEY_HOST=$(if $(HOST),$(HOST),copilot)`. |
| `pytest.ini` | the `bundle` marker, registered. |
| `tests/test_journey_through_a_host.py` | **New**, 52 stackless tests: the two command lines side by side, the environment and home isolation, the bundle's name, `HOST` parsing, each CLI's proof-reader, and the scenario's own promises. |

## 2. The four decisions worth writing down

**The host is an environment variable, not a pytest parameter.** A parameter would put the host in
the test's *node id*, which is where `run_dir` gets the bundle name from — and the design wants
`s012-journey-<host>`, not `…-live[claude]`. It would also make `make eval-live K=s012` collect two
tests and run both, which is two paid runs where the founder asked for one. So the host is read
once at import, the bundle is named from it through one marker, and a cell that wants the other
host is a second invocation with `HOST=` — which is exactly what a matrix job is.

**The Copilot argv does not move.** Every line of it was measured green on 2026-09-10 and the
Copilot instance has a run of record. The refactor is allowed to move where those flags are
*written*, never which flags they are; `tests/test_s012_copilot_host.py` holds all 37 of its
original assertions against the new code path to prove it.

**Both hosts run from outside this repository.** Copilot has `--no-custom-instructions` and keeps
it; Claude Code has no such flag and its three near-equivalents all switch off skill discovery,
which is the whole of leg one. Rather than give one host a rule and the other a flag, both get the
rule — a fresh empty working directory, recorded in the bundle — and Copilot keeps the flag as
well. One rule survives a flag being renamed.

**A host that cannot authenticate is a skip, not a red run.** The Claude measurement that forced
this: an isolated `CLAUDE_CONFIG_DIR` has no login, and `claude auth status` says so for free, in a
throwaway directory, before anything is created. C-11's rule was written for an absent CLI; this is
the same rule with one more question, and its `reason` is a sentence that names the two commands
that fix it.

## 3. What is deliberately not built

- **No new `make` target.** `K=` selects; `HOST=` parameterises.
- **No `HOST=both`, no averaging, no mark moved.**
- **No `keel-runtime` change**, though this specification names two places where one would help
  (a model knob on the Claude executor; an `executor` key on its job envelopes). The referee owns
  no product code, and neither has been found by a run yet.
- **No retry, anywhere.** FR-009 of spec 016 stands.

## 4. Risks, and what each one costs

| Risk | Cost | What is done about it |
|---|---|---|
| The Claude half has never been run live | the first `HOST=claude` run is the measurement | Deliberate, and the design says so (§13 step 4 is one paid run). Everything that *can* be proven without spending — install, skill proof, credential, argv, readiness — was proven for free and is held by tests. |
| A founder runs `HOST=claude` with no token in the shell | nothing; a named skip | `readiness()` measures a fresh config dir and skips with the two commands that fix it. |
| A founder runs `HOST=claude` with a *wrong* key | one failed first word | The CLI cannot validate a key for free either. It fails loudly, and the bundle records `authMethod: api_key` beside it. |
| Claude Code loads the skill but the per-job envelope cannot corroborate the executor | one assertion weaker on that host | Recorded in the bundle as an absence with its reason, never asserted as if it were there. The startup line still proves which executor was chosen. |
| A CLI upgrade renames a key in either listing | a red run on a green install | Both proof-readers walk their document structurally and both measured shapes are pinned in stackless tests. |
