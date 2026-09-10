# Implementation Plan: Copilot, host and thinker

**Branch**: `016-copilot-e2e` | **Spec**: [spec.md](spec.md) | **Tasks**: [tasks.md](tasks.md)

## 1. Where the new code goes

| File | What it is |
|---|---|
| `harness/copilot_host.py` | **New.** The Copilot CLI as a *host*, driven from Python: an isolated `COPILOT_HOME`, the two install commands, `skill list --json`, one `copilot -p` run with its transcript and `--usage-output-file`, and the readers for the two artefacts the skill leaves (`runtime.heartbeat.json`, `keel-connect-check.launch.log`). It shells `copilot`; it never shells `python3 -m keel_runtime` and never shells the skill's own script -- **the host does that, and that is the whole point of leg one.** |
| `stack/runtime.py` | `status`, `disconnect_via_skill_script` and `disconnect` grow an optional `home=`. Default unchanged (`home_dir(config)`), so every existing caller is untouched; S-012 needs the same three doors pointed at a home under its own run bundle. |
| `evals/test_s012_copilot_host_and_thinker.py` | **New**, `pytestmark = pytest.mark.live`. Both legs, in one test, because leg two needs the runtime leg one connected. |
| `tests/test_s012_copilot_host.py` | **New**, stackless: the properties that would otherwise only be observable during a paid run. |

## 2. The three decisions worth writing down

**The credential is not copied, and isolation is measured rather than assumed.** `COPILOT_HOME`
overrides "the directory where configuration and state files are stored" (`copilot help
environment`). On this Mac the stored OAuth credential is **not** in it -- an isolated home still
authenticates, measured before the run with a model-catalogue probe that costs nothing and a
one-word prompt that cost one premium request. `harness/copilot_host.credential_plan()` states the
three cases in order and the bundle records which one answered: `COPILOT_GITHUB_TOKEN` when the
shell carries one, the isolated home when isolation keeps the login, and the founder's real home
**with that said out loud** when it does not. A referee that quietly fell back to the real home
would be measuring a different machine than the one it named.

**Nothing asserts Copilot's prose.** A host that answered *"Keel is connected!"* while starting
nothing would pass any grep. Spec 013's acceptance half greps the reply for a `XXXX-XXXX` shape
and the word `device`, and its own prose admits that is all it does. Leg one instead reads the
runtime's own three artefacts and then asks the **cloud** whether the code is one it issued. The
reply is read exactly once, for a loose *"it said connected"* on the second run, and that check
can never be the only evidence of anything (FR-003).

**Leg two is a live walk, so it asserts shapes.** `evals/preludes.py::walk_stage` asserts the
confirmation card **verbatim** against the script -- correct for a scripted executor and
meaningless against a model. S-012 therefore carries its own `_walk_stage_live`, which is
`walk_stage` with the verbatim assertion replaced by a shape assertion and the timeouts widened
to a live model's, and which answers a `NEEDS_INPUT` question with a bounded set of benign
follow-ups exactly as S-004 does (spec 008: *a question is an answer, and the walk goes on*).
Copying rather than parameterising is deliberate: `walk_stage` is the deterministic scenarios'
contract with the corpus and it must not grow a "live" branch that makes six scenarios read like
one.

## 3. What is deliberately not built

- **No new `make` target.** `make eval-live K=s012` already selects by keyword.
- **No retry, anywhere.** FR-009: an auth or plan failure stops the run and is reported.
- **No change to `evals/preludes.py`, `harness/browser.py`, `evals/policy.py` or the acceptance
  bed.** Leg two drives the existing page objects unchanged.
- **No `--plugin-dir`, no `--add-dir`, no copying `dist/`.** The plugin comes from the marketplace
  or leg one has not proven what it claims.
- **No scoring.** `finalize_run(..., facts={})` with no policy attributes, as S-008 and S-009 do.

## 4. Risks, and what each one costs

| Risk | Cost | What is done about it |
|---|---|---|
| Copilot does not load the skill at all | leg one red on the first `-p` | Nothing. It is the measurement. The bundle carries the transcript and the empty home. |
| Copilot loads it but calls the script wrong (a base URL it guessed, `--executor` it invented) | leg one red at the heartbeat or the code lookup | Nothing -- it is a `runs/DRIFT.md` entry against keel-connect-skill. |
| The `skill` tool is refused for want of permission | leg one red | `--allow-tool skill` is passed beside `--allow-tool 'shell(python3:*)'`, the same grant spec 013's `claude` half makes with `--allowedTools "Skill,Bash(python3:*)"`. |
| A live model writes a claim keel-cloud's own rules refuse | leg two red with a screen that says nothing | `harness/refusals.py`, exactly as S-004 uses it: the wire is asked why the chat stopped. |
| The journey costs more than expected | premium requests | Recorded, never capped by this repo. keel-runtime's `--max-ai-credits 30` per job is its own. |
