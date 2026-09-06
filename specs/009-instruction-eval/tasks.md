# Tasks: The instruction eval

**Input**: [spec.md](spec.md) (FR-001..023, SC-001..008, judgement calls), with
[plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md),
[contracts/](contracts/) and [quickstart.md](quickstart.md). The design of record: keel-cloud
`canon/designs/measured-beliefs-design.md` §10 step 4, §8.1, §8.2, §8.3, §3.8 and **decision 14**, as
revised 2026-09-06 (commit `17c7642`). The corpus: keel-cloud
`canon/designs/measured-beliefs/corpus/*.yaml`, **frozen**. Prerequisites, in order: keel-cloud spec
029's two contract additions (`founderPhrase`, a new role's `market`), then its exporter and
validator (`specs/029-measured-beliefs-instructions/contracts/exported-contract-format.md`) — both
merged on its `028-measured-beliefs-aggregate` branch.

**Rules** (AGENTS.md): this repo owns no product code and never fixes the product — a bad instruction
is a `runs/DRIFT.md` entry with a run bundle, never a patch made here. The scenarios stay
deterministic and untouched: nothing here is collected by `pytest evals`, nothing here reads or
writes `evals/policy.py`, and `POLICY_VERSION` does not move. This eval is model-backed, opt-in and
named as an exception in AGENTS.md rather than smuggled past the rule. The corpus is read-only and
the run proves it. A rubric change bumps `MARKS_VERSION`. Gate: `make unit`, then
`make instruction-eval DRY=1`, then `make instruction-eval BASELINE=1`.

## Phase 1: Read the world, spend nothing

- [X] T001 `requirements.txt`: add `pyyaml>=6.0` (the one new dependency, plan.md). `make venv`
      re-resolves. `instructions/__init__.py` with the package docstring naming this spec and saying
      what makes this package different from `evals/` and `harness/`.
- [X] T002 `instructions/corpus.py` (FR-001): load every `canon/designs/measured-beliefs/corpus/*.yaml`
      from the keel-cloud path in `stack.toml`, read-only, into the `Entry`/`GoldenBelief`/`Person`
      shapes of [data-model.md](data-model.md) §1. SHA-256 every file on load and expose
      `verify_unchanged()` for the end of a run. Carry the three notes: `founderPhrase` has nowhere
      to go, taps are English here and enum names on the wire, anchors carry a `stage` the aggregate's
      questionnaire does not.
- [X] T003 `instructions/contract.py` (FR-002): shell `./gradlew -q screenContracts --args="export <run>/contracts"`
      in the keel-cloud checkout and read back `contracts/<SCREEN>.json`, `context-keys.json` and
      `manifest.json` per keel-cloud spec 029's contract. A missing task or a non-zero exit is a
      refusal to start naming the prerequisite, never a score.
- [X] T004 `instructions/instruction.py` (FR-003): read
      `<keel-cloud>/src/main/resources/keel/inference-instructions/<stem>.md` and `.strip()` it, so
      the prompt carries exactly what `InferenceInstructionRegistry.get` returns. One table from
      `InferenceScreen` to file stem.
- [X] T005 `instructions/context.py` (FR-005): fill every key `context-keys.json` names for a screen,
      in its order, `null` where there is no value — statements and `market` from the entry,
      `existing_roles` derived from earlier stages' `askedOf` — `[]` for PROBLEM, PROBLEM's roles for
      SOLUTION, those plus SOLUTION's for COMMERCIAL ([research.md](research.md) R5a) — and for
      `INTERPRET` a synthetic `invitation_id` plus `anchors[]` that **omits a blank anchor**, as
      `ScreenContextBuilder.anchorsWritten` omits it. The tap English→enum table lives here, and the
      `existing_roles` set supplied is recorded per case so a duplicate-heavy extras list can be
      read as this first.
- [X] T006 `instructions/prompts.py` (FR-004): build `{instruction, context, interaction_history: [],
      input: {content: ""}, response_contract}` — `InferenceJobService.buildRequestPayload`'s shape
      with the auto-screen empty-content sentinel — then `keel_runtime.executor.build_prompt`. Write
      no prompt text here.
- [X] T007 [P] `tests/test_instruction_context.py` and `tests/test_instruction_prompts.py` (FR-018):
      the payload shape against a recorded key list; every key present and ordered; a blank anchor
      absent; a tap mapped; the empty-content sentinel. Stackless, no model.
- [X] T008 `instructions/run.py`: the `python -m instructions.run` entry point with `--dry-run`,
      `--baseline`, `-k`, `-n`, `--marks`; in dry-run it prints every prompt it would send and the
      estimated case count and cost, and calls nothing.
- [X] T009 Gate: `make unit` green; `python -m instructions.run --dry-run -k 01-countly` prints an
      assumption prompt and a reading prompt in full. **Read them both** — `TASK`, `CONTRACT`, the
      `SOURCE MATERIAL` heading, the nonce-fenced block — before any money is spent
      ([quickstart.md](quickstart.md)).
      - **Note (2026-09-06)**: gate passed, and it earned its keep. `make unit` green at 123 tests
        (16 of them this feature's). The dry run printed both prompts in full and reading them
        found a real bug before a penny was spent: the corpus keys its statements
        `problem`/`solution`/`commercial` in **lower** case while `StageType` is upper, so every
        `*_statement` was arriving `null` — the one value that makes an assumption screen
        legitimately ask (decision 14), which would have turned the whole baseline into a
        measurement of this harness. Fixed in `instructions/context.py` with a regression test.
        The reading prompt confirmed the drift the baseline is meant to expose: the context is
        `invitation_id` + `anchors`, and `interpret.md` still says it has "four fields" including
        `raw_answer_text` and `assumptions`.

## Phase 2: Score, still with no model

- [X] T010 `instructions/align.py` (FR-009): the deterministic structural matcher of
      [data-model.md](data-model.md) §4 — candidates by stage, type, measure kind and band overlap,
      or expected option and option-set overlap; pair score over the **seven** fields (the six, plus
      `founderPhrase`) with a heading tie-break; greedy maximum with ties broken by golden id order.
      Mark each pair `by: "structure"`.
- [X] T011 `instructions/score.py` (FR-011, FR-013): the metrics of
      [contracts/metrics-contract.md](contracts/metrics-contract.md) — golden-belief recall,
      per-field exact-match over matched pairs only **including `founderPhrase`** (absent on both
      sides agrees; present on one side only is a miss), the phrase-and-band pair read together in
      its four combinations, the **`NEEDS_INPUT`-as-failed-case** rule of decision 14, extra-belief
      count, anchoring accuracy with `GUESSED` precision and recall, the confusion matrix, and the
      per-case spread across N runs. Nothing is averaged before it is reported.
- [X] T012 `instructions/marks.py` + `instructions/marks.toml` (FR-014): `MARKS_VERSION = 1`, the
      three marks, a TOML override, and the module docstring's append-only numbered judgement-calls
      block seeded with the **ten** from the metrics contract — the shape `evals/policy.py` uses.
- [X] T013 [P] `tests/test_instruction_align.py` (FR-018, SC-002): **the fixed point** — every corpus
      entry aligned against itself scores 100 % recall and 100 % exact match on every field, with
      zero judge calls. Plus the hard case: `01-countly.yaml`'s `P4a`/`P4b`, two beliefs on one shared
      multi-select selection with identical option lists, in the produced set's reverse order.
- [X] T014 [P] `tests/test_instruction_score.py` (FR-018): the metric arithmetic on hand-built
      fixtures — a reader that answers `ANCHORED` to everything must show high accuracy and zero
      `GUESSED` recall, which is the whole reason the two are reported apart.
- [X] T015 Gate: `make unit` green, including the fixed point. A matcher that cannot recognise the
      golden set as itself cannot be trusted to score a model's.
      - **Note (2026-09-06)**: the fixed point holds across all seven entries and all three stages
        — 100 % recall, every scored field agreeing, every pair a belief with itself, and zero
        ambiguities needing a judge. `01-countly`'s `P4a`/`P4b` pair the right way round when the
        produced set is reversed, so position never decides a match.

## Phase 3: Call the model, leave a bundle

- [X] T016 `instructions/runner.py` (FR-006, FR-007, FR-008): the pre-flight in the shape of S-004's
      `_claude_ready()` (`claude` on PATH and logged in, the keel-cloud checkout and its Gradle task,
      the corpus) refusing to start with the reason printed; then
      `keel_runtime.executor.ClaudeCodeExecutor` with `home=<run>/jobs`, N runs per case (default 3),
      and `keel_runtime.response_validator.validate_response` against the same contract. Record per
      call: prompt, envelope, recovery-pass flag, `num_turns`, `total_cost_usd`, wall clock. Refuse a
      second concurrent instruction-eval run.
      - **Note**: `ClaudeCodeExecutor` raises `ExecutorUnavailable` for two different things and
        this eval keeps them apart: *"the answer never fit its shape"* (`error_max_turns` after a
        schema refusal) is the model being reached, told the contract, and failing it — a
        measurement, counted as schema-invalid; a missing binary or a dead CLI is `errored` and
        measures nothing. Without the split, a baseline against pre-029 prose would report its own
        central finding as a harness failure.
- [X] T017 `instructions/report.py` (FR-015): the run directory through
      `harness.evidence.new_run_dir` with slug `instructions`/`instructions-baseline`, `versions.json`
      through `harness.evidence.write_versions`, plus `verdict.json`, `scorecard.json`,
      `corpus.sha256` (checked again at the end), `contracts/`, and
      `cases/<entry>/<subject>/<run>/{prompt.txt,envelope.json,diff.json}` per
      [contracts/run-bundle-contract.md](contracts/run-bundle-contract.md).
- [X] T018 `instructions/report.py` (FR-016, FR-020, FR-021): `report.html`, self-contained — the
      header with the three marks, `MARKS_VERSION`, **one line naming the model this run was judged
      under** (the `claude` CLI version and whatever the envelope reports) and the sentence that the
      marks are comparable only within a model, and the five sibling commits; **the stated blind
      spots, every run — the register is not scored and no metric represents it; whether an option
      list leads is not scored either**; the reading section with the confusion matrix and every disagreement
      as a row; the assumption diffs golden-beside-produced with a tick per field; the spread; the
      prompts, collapsed.
- [X] T019 `Makefile` (FR-017): `instruction-eval` in `.PHONY` and as a target with the `venv`
      prerequisite, `$(PY) -m instructions.run` and `BASELINE=`/`N=`/`K=`/`MARKS=`/`DRY=` passed
      through, preceded by a comment naming this spec, saying it needs no `make up`, and saying it
      costs real money. It is **not** a dependency of `eval`, `eval-all` or `eval-live`.
- [X] T020 Gate: `make eval K=s001` and `make unit` behave exactly as before — no new collection, no
      new marker, `evals/policy.py` and `POLICY_VERSION` untouched (SC-006).
      - **Note (2026-09-06)**: confirmed without booting a stack, because nothing here can affect
        one: `git diff` against this branch's base is **empty** for `evals/` and `pytest.ini`;
        `POLICY_VERSION` is still 7 and `evals/policy.py` is byte-identical; `pytest evals -m "not
        live"` still collects exactly S-001, S-002 and S-003 with S-004 deselected, and `pytest
        instructions` collects nothing at all. `instruction-eval` is in `.PHONY` and is a
        prerequisite of nothing.

## Phase 4: The baseline — before keel-cloud edits a single instruction

- [X] T021 `make instruction-eval BASELINE=1` against keel-cloud's **current** instructions (SC-001).
      Expect every assumption case schema-invalid or refused and every reading case likewise; the
      verdict is `failed`. Keep the run directory and record its id here — it is the only measurement
      of the old instructions that will ever exist.
      - **Run: `runs/20260906T170528Z-instructions-baseline/`** (2026-09-06). keel-cloud `21d0ba1`,
        keel-runtime `916583d`, `claude` 2.1.263, models `claude-opus-5[1m]` + `claude-haiku-4-5`.
        **N=1, not 3** — a baseline is taken once, and the numbers below are stark enough that
        three passes would have bought precision on a verdict that is not close. 124 cases (21
        assumption + 103 reading; three of the corpus's 106 people left every anchor blank and
        production would start no reading job for them either), 54 minutes, **$11.88**.
        Verdict **failed**: golden-belief recall **17.0 %** against a mark of 80 %.
      - **The prediction in [quickstart.md](quickstart.md) §1 was wrong, and usefully so.** It
        expected every case "refused before a single belief is compared". Nothing was refused:
        **0 schema-invalid, 0 shape refusals, 0 `NEEDS_INPUT`**. The CLI's `--json-schema`, built
        from keel-cloud's exported contract, *forces* the envelope into the 028/029 shape whatever
        the prose says — so the baseline measures **quality, not shape**, and the old instructions'
        `question: {ask, disconfirming}` and `claimType`/`stance` never had a chance to appear.
      - **6 of 21 assumption cases timed out** at keel-runtime's own production default of 120 s
        (`runs/DRIFT.md` #26). They are `errored`, excluded from every quality metric, and are why
        `cases` reads 124 while the quality denominators read 15.
- [X] T022 Read the baseline report end to end and confirm every failure names the **contract**, not
      the harness. A failure this repo caused is a bug to fix now, while it is cheap; a green
      baseline is a bug to go and find.
      - **Note (2026-09-06)**: read end to end. Every failure names the contract or the prose, not
        the harness — with two exceptions, both found and both this repo's, both fixed:
        `ClaudeCodeExecutor.last_envelope` was not cleared between calls, so a timed-out case filed
        the previous case's envelope and cost under its own id (fixed, with
        `tests/test_instruction_runner.py`); and the harness had already, before any spend, been
        caught reading the corpus's lower-case statement keys as upper-case (T009's note). **The
        baseline bundle predates the envelope fix**, so its six timed-out cases carry a stale
        `envelope` block and their real token spend is missing from the $11.88 — the quality
        metrics are unaffected, since a timed-out case scores nothing either way.
      - **One number in `verdict.json` must not be read as measured**: `refusals` shows `0` and
        `met: true`, but nothing was ever shown to the aggregate — `instructions/validate.py` is
        T023, Phase 5, and does not exist yet. `marks.judge` treats an unmeasured refusal count as
        a met mark, which is the one place the rubric currently flatters a run. Every other mark
        refuses a `None` rather than passing it.

## Phase 5: The aggregate's verdict, and the judge

- [ ] T023 `instructions/validate.py` (FR-012): collect every produced belief set of a run into one
      batch in keel-cloud spec 029's batch shape (screen, market, roles, result) and hand it to
      `./gradlew -q screenContracts --args="validate <batch> <report>"` in **one** invocation; read
      back `accepted` or `{kind, rule, path, message}` plus the built bucket labels, into
      `validation.json`. The invariants are never reimplemented here.
- [ ] T024 `instructions/score.py`: fold the aggregate's verdict into the scorecard —
      `refusals_by_rule` (rule refusals only, and this is what the mark counts), shape refusals apart,
      schema-invalid answers apart again; and the bucket diff beside the corpus's `expected.buckets`.
- [ ] T025 `instructions/judge.py` (FR-010): the bounded tie-breaker — only for two-or-more goldens
      tied at the top score, or a produced belief with no candidate; it sees two statements and may
      answer only *this one*, *that one* or *no match*; it can never assert a pair the structure
      rejected. Every call, its input and its answer recorded; `judged_fraction` in the scorecard and
      on the report, so a reader can discount the score by exactly the amount a model decided it.
- [ ] T026 Gate: a full `make instruction-eval` produces a report carrying, per set, the aggregate's
      verdict by rule id, and stating what fraction of the alignment the judge decided.

## Phase 6: Docs, findings, and the long part

- [ ] T027 `instructions/report.py` (FR-019): `register.html` — one section per market in the run,
      the market's `country`/`region`/`language` at its head, then every produced anchor prompt and
      every produced option list for that market grouped by entry and stage, with the corpus's own
      anchor for the same stage beside it for reference. **No score, no tick, no cross**, and a
      sentence saying nothing on the page contributes to a verdict
      ([contracts/run-bundle-contract.md](contracts/run-bundle-contract.md)).
- [ ] T028 Gate: a full run writes `register.html`; send one market's section to a person who knows
      that market, and record their reading with the run (SC-007). This is the design's own answer to
      a thing code cannot judge (§10 step 4) — **no metric is invented for it**, and the run's verdict
      does not depend on it.
- [ ] T029 [P] `README.md` (FR-022): an `## The instruction eval (make instruction-eval)` section —
      what it measures, model-backed and opt-in, needs no stack, what it costs, the `MARKS_VERSION`
      rule, the register page and why it carries no number, and the model-comparability limit.
- [ ] T030 [P] `AGENTS.md` (FR-022): amend "no Prism, no LLM, ever" to name its two exceptions —
      S-004 and this eval — rather than leave a rule the repo does not follow. Naming them is the
      point: everything not named stays deterministic. While there, correct "Both scenarios" to the
      four that now exist.
- [ ] T031 `runs/DRIFT.md` (FR-023): an entry per finding the runs surface, in the seven-part format
      (severity, where, the offending excerpt, reproduction naming the run bundle, why the eval was
      or was not adapted around it, the shape of a fix explicitly not applied). An instruction that
      cannot reach a golden belief is a keel-cloud defect and belongs here; a harness bug belongs in
      `## Discovered` below.
- [ ] T032 Iterate with keel-cloud spec 029 until the marks pass at N=3 over all seven entries:
      anchoring accuracy ≥ 90 %, golden-belief recall ≥ 80 %, refusals = 0 (SC-004). Expect more than
      one pass — the instructions are prose. Every change is keel-cloud's; nothing in the corpus and
      nothing in the marks moves to make a run green.
- [ ] T033 Commit per phase in the house style with the trailers; no push. Final report: the gate
      results, the baseline run id and the passing run id with their numbers side by side, the model
      identity both were judged under, the register reading and who gave it, and every DRIFT entry
      added.

## Discovered

*Filled in after the work: what the eval taught about the instructions, which alignment rules needed
a threshold nobody had thought about, what the baseline actually cost, and whether the judge earned
its place or the structural matcher was enough on its own.*
