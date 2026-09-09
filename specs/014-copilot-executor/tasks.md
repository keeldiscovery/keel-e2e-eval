# Tasks: Every mark, on both hosts

**Input**: [spec.md](spec.md) (FR-001..008, SC-001..004, the five clarifications) with
[plan.md](plan.md).

**The siblings, read at**: keel-runtime `271c01c` (spec `005-copilot-executor`), keel-cloud
`8acb805`, keel-web `b0a5015`, keel-connect-skill `4eb0548`.

**Rules** (AGENTS.md): this repo owns no product code, never writes to a sibling repository, and
reports cross-repo gaps as `runs/DRIFT.md` entries with a bundle. `POLICY_VERSION` does not move,
and neither does `MARKS_VERSION` — **a second host is not a rubric change**, and a rubric that
moved would be the one thing that made the two hosts' runs incomparable. The two named
model-driven exceptions do not change in number or in name: this is the same
`make instruction-eval`, asked of somebody else.

---

## Phase 1: the prompt, which nothing can be measured before

- [X] T001 `instructions/prompts.py`: `render(..., host=)` calls keel-runtime's `build_prompt` for
      `claude` and its `_render_copilot_prompt` (over `_prompt_sections` and
      `_build_envelope_schema`) for `copilot` (FR-004, C-8). A missing renderer is
      `RuntimeUnavailable` naming it, never a fallback to the other host's prompt.
- [X] T002 `instructions/prompts.py`: `canonical_host` asks keel-runtime's own
      `canonical_executor_name` — `claude-code` is the runtime's permanent alias (C-12) and this
      repo is not the second place that knows it.
- [X] T003 `instructions/prompts.py`: `build_cases(..., host=)` threads it through **all three**
      loops — assumptions, reading and BRIEF — because a host threaded into two of them leaves a
      bundle two-thirds honest.

## Phase 2: the pre-flight, per host

- [X] T004 `instructions/runner.py`: `preflight(..., host=, executor_module=)`, and `binary_for`
      reading `EXECUTOR_BINARIES` out of `keel_runtime.config` (FR-002). A host the runtime has no
      binary for is a refusal naming the ones it has.
- [X] T005 `instructions/runner.py`: `_copilot_ready` — one probe, in the executor's own closed
      shape (`COPILOT_EXCLUDED_TOOLS`), **decided by the JSONL and never by the exit code** (C-3),
      with keel-runtime's own `COPILOT_AUTH_MARKERS` read off stderr *and* every `session.error`
      (C-6). The probe costs one premium request and is taken anyway: FR-006/7/8's rule does not
      soften for a metered host.
- [X] T006 `instructions/runner.py`: `Answer.premium_requests` and `Answer.reported_model`, filled
      on the success path **and on both failure paths**, so a case that timed out or refused its
      shape still says what it cost and what answered it.
- [X] T007 `instructions/runner.py`: `reported_model` — the envelope first, then this run's own
      events (`session.auto_mode_resolved.chosenModel`, else the usage checkpoint's per-model
      breakdown). `runs/DRIFT.md` #53 is why the second half exists.

## Phase 3: the run, and what it records

- [X] T008 `instructions/run.py`: `--host {claude,copilot}` with `choices`, so an unknown host
      costs nothing at all — not a Gradle export, not a corpus load (FR-001).
- [X] T009 `instructions/run.py`: the executor through `executor_module.get_executor(host,
      home=run_dir, copilot_model=$KEEL_COPILOT_MODEL)`, never by naming a class (FR-003).
- [X] T010 `instructions/run.py`: `_model_block` and `_manifest` — host, CLI, pinned and reported
      model, this host's own caps (`getattr`, because `CopilotExecutor` has neither a turn cap nor
      a dollar cap and reporting Claude's beside it would describe a cap nothing enforced), and
      `judge_host`, which stays `claude` on both hosts on purpose.
- [X] T011 `instructions/run.py`: the premium sum, and `total_cost_usd` **or**
      `total_premium_requests` in the verdict, never both and never one derived from the other
      (FR-007, C-7).

## Phase 4: the bundle, and the pages a person reads

- [X] T012 `instructions/report.py`: `start_bundle(..., host=)` — `-copilot` suffixed, `claude`
      keeping the bare name every existing run of record is cited under; and `write_manifest`,
      written before the first call and again after the last (FR-005).
- [X] T013 `instructions/report.py`: `render_report(..., host=)` — the host in the `<title>`, in
      the `<h1>`, in a banner saying two hosts' runs must never be averaged, and in the
      "judged under" line, which now names the pinned model or says nothing pinned one (FR-006).
- [X] T014 `instructions/report.py`: `_spend`, and caps rendered as *"no turn cap — this CLI has
      no flag for one"* rather than as a blank.
- [X] T015 `instructions/report.py`: `render_register(..., host=, cli_version=, model=)` — whose
      words these are, before the first word of them.
- [X] T016 `instructions/report.py`: `write_case(..., host=)` — the host and this case's own
      `premium_requests` and `reported_model` in `envelope.json`.
- [X] T017 `instructions/rescore.py`: `_host_of` — a re-scored Copilot bundle keeps its own host on
      the register it rewrites.

## Phase 5: the way in, and the guards

- [X] T018 `Makefile`: `HOST={claude,copilot}`, default `claude`, documented at the target with
      what it does and does not decide.
- [X] T019 `tests/test_instruction_host.py` (35 tests): the prompt is the host's; a renamed
      renderer refuses; all three case loops; the binary comes from keel-runtime's **real** table;
      the probe reads the JSONL and not the exit code; an unauthenticated Copilot is named as
      that; the model comes from the envelope, then the router, then nothing rather than a guess;
      no dollar figure is invented; the bundle and both pages name the host; the rubric did not
      move; an unknown host exits 2 before anything is spent.
- [X] T020 `tests/test_instruction_modules_import.py`: the model block's new shape.

## Phase 6: the run of record

- [X] T021 `make instruction-eval DRY=1 HOST=copilot K=01-countly` — the Copilot prompt, with
      `SYSTEM` and `RESPONSE` above the fence, and nothing spent (SC-002).
- [X] T022 `make instruction-eval DRY=1 HOST=claude K=01-countly` — `TASK` first, exactly as
      before (SC-003).
- [X] T023 `make instruction-eval HOST=copilot N=1`, **once**, on the founder's own plan.
      Run of record: `runs/20260909T061537Z-instructions-copilot`.
- [X] T024 `runs/DRIFT.md` and `README.md`.

## The run of record

`runs/20260909T061537Z-instructions-copilot` — GitHub Copilot CLI 1.0.83, nothing pinned, the
router's own choice recorded per case. Read the numbers, the comparison against the Claude run of
record and the three findings in `README.md`'s own section; they are not repeated here.

`make unit`: **448 → 483**, green.
