# Feature Specification: Every mark, on both hosts

**Feature Branch**: `014-copilot-executor`

**Created**: 2026-09-09

**Status**: Implemented — `make instruction-eval HOST=copilot N=1` run once, on the founder's own
Copilot plan, and its bundle is the run of record named in [tasks.md](tasks.md) and `README.md`.

**Input**: keel-cloud `canon/designs/keel-skill-design.md` (design of record, 2026-09-08), §5
*"Two hosts: Claude Code and GitHub Copilot"* — and inside it §5.5, *"'Supported' is a four-part
gate"*, whose third part is this repository's:

> `make instruction-eval` grows `HOST={claude,copilot}` (default `claude`), choosing the executor
> class `instructions/run.py` constructs and the CLI `instructions/runner.py::preflight` requires.
> Nothing else in that package changes — corpus, marks, `MARKS_VERSION`, judge, scorer, bundle and
> `build_prompt` are shared, because a comparison whose sides were sent different prompts measures
> nothing. The bundle and `verdict.json` record host, CLI version and pinned model; **two runs
> under different hosts are different measurements and must never be averaged.**

The siblings, read at these commits:

| Sibling | Branch | Commit | What this feature depends on |
|---|---|---|---|
| keel-runtime | `master` | `271c01c` | spec `005-copilot-executor`: `CopilotExecutor` beside `ClaudeCodeExecutor`, `get_executor`'s name table, `canonical_executor_name`, `EXECUTOR_BINARIES`, and the shared `build_prompt`/`_prompt_sections`/`_build_envelope_schema`. |
| keel-cloud | `master` | `8acb805` | the `screenContracts` exporter, the frozen measured-beliefs corpus, the aggregate's own validator — all host-independent, and all unchanged by this feature. |
| keel-web | `master` | `b0a5015` | nothing. This eval talks to no service. |
| keel-connect-skill | `master` | `4eb0548` | nothing at run time; named in `versions.json` like every other run. |

## What changes, stated first

**Every number this repository has ever published about keel-cloud's instruction prose was
measured through one host.** `marks.toml`'s four marks, the run of record, the baseline that
justified `MARKS_VERSION` 2, the BRIEF paragraphs that justified 5 — all of them are the Claude
Code CLI's answers. The design now says Claude Code is *one of two*, and a host is "supported"
only when the instruction eval's run of record is green **on that host**. So the eval has to be
able to ask the other one.

Four things follow, and they are the whole feature.

1. **`HOST={claude,copilot}` on `make instruction-eval`, default `claude`.** It decides three
   things and nothing else: which CLI `preflight` requires and probes, which executor
   `run.py` constructs, and which prompt `prompts.render` builds. Corpus, contract, marks,
   `MARKS_VERSION`, judge, scorer, aligner and bundle layout are untouched.
2. **The executor is chosen through keel-runtime's own selection, not through a second table
   here.** `run.py` calls `executor_module.get_executor(host, home=run_dir, ...)` — the same
   function `keel_runtime.cli` calls for `--executor` — so `claude-code`'s permanent alias, the
   `copilot_model` pin and the per-host constructor arguments are keel-runtime's to define and
   this repo cannot drift from them. `runner.preflight` reads the binary name out of
   `EXECUTOR_BINARIES` for the same reason.
3. **The bundle says which host.** `manifest.json` (new, at the bundle root) and `verdict.json`
   both carry `host`, the CLI's own `--version` string, the pinned `--model` slug (`null` when
   nothing pinned one) and the model the CLI *reported*; a Copilot bundle is named
   `<stamp>-instructions-copilot`, and `register.html` and `report.html` are titled per host, so
   nobody reads two hosts' paragraphs side by side believing they came from one.
4. **One Copilot run of record, at `N=1`**, and three findings recorded rather than worked
   around — `runs/DRIFT.md` #53, #54 and #55.

`MARKS_VERSION` stays at **5**. Nothing about the rubric changed; only who was asked.

## Clarifications

### Is the prompt shared, or is it the host's? — **the body is shared; two sections are the host's, and this repo renders them the same way the runtime does**

§5.4 (C-8) is explicit both ways: `build_prompt`, `_prompt_sections`, `_render_prompt` and
`_build_envelope_schema` are *"shared unchanged — the prompt is the runtime's, not the host's"* —
**and** the fixed `SYSTEM_PROMPT` and the envelope schema, which Claude receives as `--system-prompt`
and `--json-schema` flags, *"move into the text"* on Copilot because that CLI has neither flag.

So the prompt a Copilot job is sent is genuinely not byte-identical to the Claude one, and a
harness that recorded the Claude rendering in a Copilot bundle would be publishing a prompt nobody
sent. `prompts.render` therefore takes the host and calls `_render_copilot_prompt` for Copilot —
**keel-runtime's own function, imported like everything else here, never reimplemented.** Two
consequences, both deliberate:

- `make instruction-eval DRY=1 HOST=copilot` prints the Copilot prompt. The dry run exists so a
  prompt can be read before money is spent, and it would be worth nothing if it printed the other
  host's.
- The bundle's `cases/**/prompt.txt` is what that host was sent, byte for byte.

A keel-runtime that renamed those helpers makes this eval **refuse to start**, by name, rather
than fall back to the Claude rendering (`prompts.RuntimeUnavailable`). Falling back would measure
the wrong prompt and call it Copilot.

### A Copilot pre-flight probe costs a premium request. Probe anyway? — **yes**

`preflight`'s rule is spec 009's FR-006/7/8 and it does not soften for a metered host: *a run that
cannot reach the model has measured nothing, and a harness that reported that as a bad instruction
would be lying about keel-cloud.* One probe against a hundred and thirty-one cases is the cheapest
insurance in the run. It is the same closed shape the executor uses (Copilot's tools excluded by
keel-runtime's own `COPILOT_EXCLUDED_TOOLS`), and **success is decided by the JSONL, never by the
exit code** — C-3, which was measured on a run that failed while exiting 0.

### Copilot reports no dollars. Report zero? — **no: premium requests, or nothing**

C-7 says the runtime never invents a dollar figure it was not given, and `CopilotExecutor`'s
envelope carries `premium_requests` with **no `total_cost_usd` at all**. So the verdict carries
`total_premium_requests` on a Copilot run and `total_cost_usd` on a Claude one, each named for
what it is. A `$0.00` on a Copilot report would be a lie in the shape of a number.

### Which model? — **whatever the CLI reports, recorded; nothing pinned, and the report says so**

C-5 wanted `--model` pinned, because *"a Copilot subject that does not pin `--model` measures the
router, not a model"*. keel-runtime spec 005 then measured that this account's CLI 1.0.83 rejects
**every** slug offered to `--model`, its own router's chosen one included, so `CopilotExecutor`'s
`model` defaults to `None` and `KEEL_COPILOT_MODEL` supplies one where a machine has one that
works. This run pins nothing, and both the bundle and the report say `pinned_model: null` beside
the model the CLI reported — an unpinned run is recorded as unpinned rather than silently
measured. See `runs/DRIFT.md` #53 for what that costs a comparison.

### A Copilot run is scored by a Claude judge. Is that a contamination? — **no, and it is recorded**

`instructions/judge.py` is the referee's own tie-breaker, not the subject: it reads two short
strings out of this bundle and answers one fixed word, with no nonce fence, no response contract
and no `build_prompt`. It stays on `claude` on both hosts precisely so the *scoring* is one
constant across the comparison. `judge_host` is written into the model block so a reader can see
it rather than assume it.

## Requirements

- **FR-001** `make instruction-eval` accepts `HOST={claude,copilot}`, default `claude`, and passes
  it to `python -m instructions.run --host`. An unknown host is refused by `argparse`, before any
  prerequisite is checked and before anything is spent.
- **FR-002** `instructions/runner.py::preflight` takes the host, resolves its CLI name through
  keel-runtime's `EXECUTOR_BINARIES`, requires that binary on `PATH`, records its `--version`
  string, and probes it in the host's own closed shape. Any failure is a **refusal to start** that
  names the prerequisite, never a score.
- **FR-003** `instructions/run.py` constructs its executor through
  `keel_runtime.executor.get_executor(host, ...)` — never by naming a class — with the run
  directory as `home`, keel-runtime's own default caps, and `copilot_model` from
  `KEEL_COPILOT_MODEL` when set.
- **FR-004** `instructions/prompts.py::render` and `build_cases` take the host and render the
  prompt that host's executor sends, through keel-runtime's own renderers. A missing renderer is
  `RuntimeUnavailable`, never a silent fallback to the other host's prompt.
- **FR-005** The bundle carries `manifest.json` at its root with `scenario`, `host`, `cli`
  (binary and version), `model` (pinned and reported), `marks_version`, `n_runs`, `baseline` and
  the start time; `verdict.json` carries `host`, `cli_version` and the same `model` block.
  A non-Claude run's directory is suffixed with its host (`<stamp>-instructions-copilot`).
- **FR-006** `report.html` and `register.html` name the host in their `<title>` and on the page,
  and `report.html` states that two hosts' runs are different measurements and must never be
  averaged.
- **FR-007** A Copilot answer's `premium_requests` is carried onto the `Answer`, summed, and
  written to `verdict.json` as `total_premium_requests`. No dollar figure is invented.
- **FR-008** `MARKS_VERSION`, `marks.toml`, `instructions/score.py`, `instructions/align.py`,
  `instructions/brief.py`, `instructions/corpus.py`, `instructions/contract.py` and
  `instructions/validate.py` are unchanged by this feature.

## Success criteria

- **SC-001** `make unit` grows from **448** and is green.
- **SC-002** `make instruction-eval DRY=1 HOST=copilot K=01-countly` prints a prompt carrying a
  `SYSTEM` and a `RESPONSE` section above the nonce fence, and spends nothing.
- **SC-003** `make instruction-eval HOST=claude` builds a prompt byte-identical to the one it
  built before this feature, and constructs a `ClaudeCodeExecutor` with the same four caps.
- **SC-004** One `make instruction-eval HOST=copilot N=1` completes, its bundle names the host,
  the CLI version and the reported model, and its result — green or red — is read as a finding
  about Copilot rather than as a harness fault, unless the fault is in this repository.
