# Feature Specification: The instruction eval — a real model against the frozen corpus

**Feature Branch**: `009-instruction-eval`

**Created**: 2026-09-06

**Status**: Draft — for the founder's review. **No questions open**: both were answered by the
design's revision of 2026-09-06 (keel-cloud commit `17c7642`, decision 14 and §10 step 4).

**Input**: the founder's direction of 2026-09-06: step 4 of the measured-beliefs implementation
strategy, "the instructions … evaluated against the frozen corpus with a real model, in
keel-e2e-eval where the DRIFT log lives". The design of record is keel-cloud
`canon/designs/measured-beliefs-design.md` §10 step 4, with §8.1 (extraction), §8.2 (reading), §8.3
(the phrase table), §3.8 (the market) and decision 14; the corpus is keel-cloud
`canon/designs/measured-beliefs/corpus/*.yaml`, frozen at the end of step 3. The contract the
harness measures against is exported by keel-cloud spec 029, whose
`specs/029-measured-beliefs-instructions/contracts/exported-contract-format.md` this feature
consumes.

## What changes, stated first

Everything this repo does today is deterministic: two scenarios walk a browser through a stack whose
inference jobs are answered from a bundled script, and the one live scenario (S-004) exists to prove
a boundary holds, not to measure a model's quality. This feature adds the first eval whose *subject*
is a model's answer.

So it is built to be separate in every direction that matters:

1. **Its own package** — `instructions/`, not `evals/`. `make eval` is `pytest evals`; nothing here
   is a pytest test, so nothing here can be swept into the deterministic set by accident.
2. **Its own make target** — `make instruction-eval`, opt-in, never a dependency of `eval`,
   `eval-all` or `eval-live`, and never run by CI.
3. **Its own stack, which is no stack.** It needs no Postgres, no keel-cloud server, no keel-web and
   no runtime process — so it cannot collide with a running profile, and `make up` is not a
   prerequisite. It imports keel-runtime as a library, reads keel-cloud's files, and shells one
   Gradle task in the keel-cloud checkout.
4. **Its own version constant** — `MARKS_VERSION`, beside `POLICY_VERSION` in spirit and under the
   same rule: change a mark, a metric's definition or an alignment rule, and bump it, because scores
   under different versions describe different rubrics.

What it keeps from the house: the run directory under `runs/`, `versions.json` pinning the five
sibling commits, a self-contained `report.html`, per-case evidence, and `runs/DRIFT.md` for what it
finds in the product.

## Scope

The `instructions/` package, a `make instruction-eval` target and its `--baseline` mode, stackless
unit tests of everything in it that is not a model call, and the DRIFT entries the first runs
produce. **It reads keel-cloud; it never writes it** — not the instructions, and above all not the
corpus, which froze at the end of step 3 and which nothing downstream may change.

**Not in scope**: the browser scenarios and their scoring policy (untouched — `evals/policy.py` and
`POLICY_VERSION` are not read or written here); keel-web; the instructions themselves, which are
keel-cloud spec 029's to write; the aggregate, which is spec 028's and already landed.

## Clarifications

### Session 2026-09-06 — resolved from the design of record

- Q: Where does the harness get the contract and the instruction text? → A: **From the keel-cloud
  checkout, never a copy.** The instruction is the file production serves,
  `src/main/resources/keel/inference-instructions/<stem>.md`, stripped exactly as
  `InferenceInstructionRegistry.get` strips it. The response contract and the context key list come
  from spec 029's exporter.
- Q: How does the harness know what the aggregate would say about a produced belief set? → A: **It
  asks the aggregate**, through spec 029's `validate` verb, one invocation per run. The invariants
  are not reimplemented here; a rule that exists twice is a rule that will disagree with itself.
- Q: What must a run leave behind? → A: **A run directory in this repo's existing style** —
  `runs/<ts>-instructions[-baseline]/` with `versions.json`, `verdict.json`, a scorecard, the full
  prompt and envelope for every case, and a self-contained `report.html` with per-case diffs.
- Q: Is the baseline expected to pass? → A: **No — it is expected to fail loudly**, and a baseline
  that passed would mean the harness was measuring something other than the instruction.

### Session 2026-09-06 — answered by the design's revision (keel-cloud commit `17c7642`)

- Q: **`existing_roles` for the later stages** — a corpus entry lists its roles flat, with no record
  of which stage created which. → A: **derive them from what earlier stages' beliefs are `askedOf`.**
  `PROBLEM` gets `[]`; `SOLUTION` gets the roles `PROBLEM`'s beliefs are asked of; `COMMERCIAL` gets
  those plus `SOLUTION`'s. It mirrors production, where each stage's assumption screen sees what the
  earlier stages introduced.
- Q: **What does a `NEEDS_INPUT` result score?** → A: **a failed case**, per decision 14. An
  assumption screen never asks the founder mid-job; its only legitimate `NEEDS_INPUT` is a missing
  statement, and the harness always supplies one. So a `NEEDS_INPUT` from an assumption screen whose
  statement was present is a failure of the instruction — reported as its own outcome *and* counted
  in the recall denominator as a case that found no goldens. A case the harness deliberately runs
  with an empty statement (there is none in this feature) would be the only exception.
- Q: **Can the eval score the §8.3 phrase mapping?** → A: **Yes, now.** keel-cloud spec 029 puts
  `founderPhrase` on the wire beside the band, "so the mapping can be audited and, in step 4, scored
  — a right band from a wrong reading must be visible" (design §8.1 step 4). It becomes a seventh
  exact-match field, and the blind spot this spec first recorded is closed.
- Q: **Can the register be scored?** → A: **No, and the design says so.** "The register cannot be
  scored by code; a person who knows the market reads the produced anchors and options, and that
  reading is recorded" (design §10 step 4). The run bundle therefore renders every produced anchor
  and option list per market on one page for a person to read, the report says plainly that they are
  unscored, and **no metric is invented for them**.
- Q: **Can the model be pinned?** → A: **Not here.** keel-runtime sends no `--model` and changing
  that is out of scope for this feature. The harness records the `claude` CLI version and whatever
  the envelope reports about the model, prints both in the report header, and states that the marks
  are comparable only within a model.

## User Scenarios & Testing

### User Story 1 - The baseline: what today's instructions do, recorded before they are touched (Priority: P1)

Nothing has been edited yet. The harness reads keel-cloud's instructions as they stand, builds the
assumption prompt for each of the seven corpus entries' three stages exactly as production builds
it, calls a real `claude` three times per case, and scores what comes back. Every case fails, and
the report says why in the product's own words: the result carried `question: {ask, disconfirming}`
and the contract has no such field; the reading carried `claimType` and `stance` and the contract
asks for anchorings. The run directory is kept, and every later run is read beside it.

**Independent Test**: `make instruction-eval BASELINE=1` on the current keel-cloud HEAD, before any
instruction is edited. A report exists, its verdict is `failed`, and its failure reasons name the
contract, not the harness.

**Acceptance Scenarios**:

1. **Given** keel-cloud at a commit where `problem-assumptions.md` still emits `ask` and
   `disconfirming`, **When** the baseline runs, **Then** every assumption case is recorded as
   schema-invalid or refused, with the envelope and the refusal captured, and the run's verdict is
   `failed`.
2. **Given** the same run, **Then** `versions.json` pins all five sibling commits with their dirty
   flags, so the baseline can be attributed to an exact keel-cloud.
3. **Given** the same run, **Then** the model's identity is recorded — the `claude` CLI version and
   whatever the result envelope reports about the model — because the marks are not comparable
   across a model change and nothing else in the run says which one answered.
4. **Given** a `claude` that is missing or not logged in, **Then** the run refuses to start with the
   reason printed, exactly as S-004's probe does — never a silent pass and never a zero score
   attributed to the instruction.

---

### User Story 2 - The assumption eval: does the instruction reach the founder's number? (Priority: P1)

For each corpus entry and each of its three stages, the harness builds the production prompt from
that entry's statement, its roles and its market, calls the model N times, and asks four questions
of every answer: did the aggregate take it; which golden beliefs did it find; how exactly did it
find them; and what did it invent.

**Independent Test**: `make instruction-eval K=01-countly` writes a run directory whose report shows,
per stage per run, the matched pairs, the unmatched goldens, the extras, and the aggregate's verdict.

**Acceptance Scenarios**:

1. **Given** a corpus entry, **When** the `PROBLEM_ASSUMPTIONS` prompt is built, **Then** it is
   assembled by keel-runtime's own `build_prompt` from `{instruction, context, interaction_history,
   input, response_contract}` — the instruction stripped as the registry strips it, the context keys
   in the exporter's order, `interaction_history` empty and `input.content` the empty-string sentinel
   an auto screen carries — and the envelope schema by keel-runtime's own
   `_build_envelope_schema`. Nothing about the prompt is written by this repo.
2. **Given** that prompt, **When** the model is called, **Then** it is called the way
   `ClaudeCodeExecutor` calls it, by using that class — same argv, same system prompt, same stdin,
   same recovery pass — with its `home` pointed at the run directory so the job dirs and envelopes
   land in the evidence rather than in `~/.keel`.
3. **Given** a produced belief set, **When** it is aligned to the entry's golden beliefs, **Then**
   alignment is **structural first**: same stage, same expectation type, same measure kind, and
   either the same expected option or overlapping bands. Only a genuinely ambiguous pair — two
   goldens equally close, or a produced belief with no structural candidate — reaches a
   model-as-judge, and the judge may only choose among candidates or say *no match*; it can never
   create a match structure rejected.
4. **Given** the aligned set, **Then** the report gives **golden-belief recall**, the **exact-match
   rate** on `type`, `measure.kind`, `measure.unit`, expected-option-or-band, `risk`, `mark` and
   **`founderPhrase`** (each reported separately, not merged into one number), and the **count of
   extra beliefs** the model produced that no golden explains.
4a. **Given** a matched pair, **Then** the phrase and the band are read **together**: the report
   shows the golden phrase and band beside the produced phrase and band, so a right band from a
   wrong phrase — and a right phrase mapped to a wrong band — are each visible as what they are.
   This is only possible because keel-cloud spec 029 puts `founderPhrase` on the wire.
5. **Given** every produced belief set in the run, **When** they are handed to keel-cloud's own
   validator in one batch, **Then** the report carries the aggregate's verdict per set: accepted, or
   refused with the rule id — `E1`–`E5`, `Q1`, `Q2`, `Q4`, `Q5`, `M1` — and a shape refusal is
   reported apart from a rule refusal.
6. **Given** an accepted set, **Then** the bucket labels the builder produced for its `BUCKETS`
   selections are shown beside the corpus's own `expected.buckets` for the matched golden, so a
   scale that came out of a different band is visible as a scale, not only as a number.
7. **Given** N runs of the same case, **Then** each is scored on its own and the spread is reported
   — a case that passes twice and fails once is not an average, it is an unstable instruction.
8. **Given** an assumption case whose statement was present, **When** the model returns
   `NEEDS_INPUT`, **Then** the case is a **failure**: an assumption screen never asks the founder
   mid-job, and its only legitimate `NEEDS_INPUT` is a missing statement (design decision 14). It is
   reported as its own outcome and counted in the recall denominator as a case that found nothing.

---

### User Story 3 - The reading eval: is a guess let through? (Priority: P1)

Every corpus entry carries named people, their anchor texts, their taps, and the golden anchoring
for each. The harness builds the reading prompt per person, calls the model, and compares one word
to one word. It reports accuracy — and then reports the thing accuracy hides: how often a guess was
called anchored.

**Independent Test**: `make instruction-eval K=reading` scores every person of every entry and prints
accuracy with `GUESSED` precision and recall beside it.

**Acceptance Scenarios**:

1. **Given** a corpus entry's answers, **When** the `INTERPRET` prompt is built per person, **Then**
   its context is `invitation_id` and `anchors[]`, each anchor carrying `anchor_id`, `prompt`, `text`
   and `tap` — and an anchor the person left blank is **not** in it, because production's context
   builder skips it.
2. **Given** the model's answer, **Then** it is one `ANCHORED`/`GUESSED` per anchor given, and an
   answer with a missing or extra anchor id is a failure recorded as such, not silently aligned.
3. **Given** all anchorings in a run, **Then** the report gives overall **anchoring accuracy**, and
   **precision and recall on `GUESSED` separately**, because letting a guess through is the costly
   error: a guessed answer counted as anchored moves a verdict that nothing anchored supports.
4. **Given** a person whose tap was *it hasn't happened*, **Then** their anchor never reaches the
   model and is excluded from the denominator — the aggregate decided it, not the reader.
5. **Given** a confusion matrix over the run, **Then** it is in the report, per entry and overall,
   with every disagreeing case linked to the anchor text that produced it.

---

### User Story 4 - The marks, and a run that says whether they were met (Priority: P2)

A run ends with a verdict a founder can read: three numbers against three marks, and the numbers are
recorded with the marks that judged them, so a later run under changed marks is not mistaken for an
improvement.

**Independent Test**: `make instruction-eval` on rewritten instructions; the verdict is `passed` only
when all three marks are met, and `verdict.json` carries the marks and the `MARKS_VERSION` that
produced it.

**Acceptance Scenarios**:

1. **Given** the default marks — anchoring accuracy ≥ 90 %, golden-belief recall ≥ 80 %, refusals
   = 0 — **When** a run finishes, **Then** the verdict is `passed` only if every one is met.
2. **Given** a marks file, **When** a mark is changed, **Then** `MARKS_VERSION` must be bumped, and a
   run records the version it was judged under.
3. **Given** two runs under different `MARKS_VERSION`s, **Then** the index says so rather than
   comparing them.
4. **Given** any run, **Then** `N` (default 3), the marks, the model identity, the five sibling
   commits and the corpus commit are all in the run directory, so the run can be explained a month
   later.

### Edge Cases

- **The corpus is read-only, and the harness proves it.** The run records the corpus files' hashes
  and fails the run if any changed during it. Nothing downstream may change the corpus (design §10).
- **The model has no pin.** `ClaudeCodeExecutor` passes no `--model`; the model is whatever the CLI
  defaults to. The harness cannot fix it, so it records it, and the report says the marks are only
  comparable within a model.
- **A refused envelope is not a zero.** `ExecutorUnavailable` (not logged in, budget, max turns) is a
  harness-environment failure and is reported apart from a model answering badly; a run with any of
  them is `errored`, not `failed`.
- **The recovery pass counts.** `ClaudeCodeExecutor` retries once when the answer never fit its
  shape. The report records which cases needed it — an instruction whose result only validates on
  the second try is an instruction with a problem.
- **A `BUCKETS` selection with options** is a produced questionnaire doing the aggregate's job. It is
  not a schema error (the schema allows the key); it is a finding, and the report names it.
- **An anchor prompt quoting a band value** trips `Q5` and shows up as a refusal, not as a low score
  — which is the right shape: the founder never sees it.
- **A stage that returns `NEEDS_INPUT`** is a **failed case**, and is also recorded as its own
  outcome so the report can say how the failure happened. Decision 14 settles it: an assumption
  screen never asks the founder mid-job, its only legitimate `NEEDS_INPUT` is a missing statement,
  and the harness always supplies one.
- **A produced belief with a band but no `founderPhrase`** is an exact-match miss on that field, not
  a schema error — the schema does not require it, because a `CHOICE` has no phrase. A `CHOICE` that
  carries one is likewise a miss.
- **A new role carrying its own market.** keel-cloud spec 029 lets a result introduce a role for
  another market. The harness passes it through to `validate` unchanged, and an `M1` refusal on such
  a belief is a real finding rather than a harness artefact.
- **Two harness sessions.** This eval needs no stack and no ports, so it does not collide with a
  running profile — but two concurrent runs would both write `runs/` and both spend money. The
  target refuses to start if another instruction-eval run is live, the way the stack refuses a taken
  port.
- **Cost.** Seven entries × three stages × N runs, plus seven entries × their people × N runs, is
  hundreds of real `claude` calls. The run prints its estimated case count and total cost before it
  starts and its actual `total_cost_usd` after, summed from the envelopes.
- **keel-cloud not present, or its Gradle task missing.** The run refuses to start with the reason —
  spec 029's exporter is a hard prerequisite and a missing one is not a score.

## Requirements

### The corpus and the contract

- **FR-001** `instructions/corpus.py`: read every `canon/designs/measured-beliefs/corpus/*.yaml` from
  the keel-cloud checkout named in `stack.toml`, **read-only**, and expose `Entry` with `market`,
  `statements`, `roles`, `beliefs` (each with `stage`, `heading`, `risk`, `mark`, `askedOf`,
  `expectation`, `selection`, optional `group`, `founderPhrase`), `questionnaire`, `answers` (person,
  per-anchor `text`/`tap`/golden `anchoring`, `picks`) and `expected`. Hash every file on load and
  again at the end of the run; a change is a failed run.
- **FR-002** `instructions/contract.py`: run keel-cloud's exporter
  (`./gradlew -q screenContracts --args="export <run>/contracts"`) into the run directory and read
  `contracts/<SCREEN>.json`, `context-keys.json` and `manifest.json` per keel-cloud spec 029's
  `contracts/exported-contract-format.md`. Never hand-write a schema or a key list.
- **FR-003** `instructions/instruction.py`: read the instruction text from
  `<keel-cloud>/src/main/resources/keel/inference-instructions/<stem>.md` and strip it exactly as
  `InferenceInstructionRegistry.get` does, so the prompt carries the bytes production carries.

### The prompt and the call

- **FR-004** `instructions/prompts.py`: build `request_payload` as
  `{instruction, context, interaction_history: [], input: {content: ""}, response_contract}` — the
  shape `InferenceJobService.buildRequestPayload` writes, with the empty-string content sentinel an
  auto screen carries — and build the prompt with keel-runtime's own
  `keel_runtime.executor.build_prompt`. **This repo writes no prompt text.**
- **FR-005** `instructions/context.py`: fill each screen's context keys in the exporter's order from
  a corpus entry — `<stage>_statement` and the upstream statements from `statements`, `market` from
  the entry's market, `existing_roles` derived from what earlier stages' beliefs are `askedOf` —
  `[]` for `PROBLEM`, `PROBLEM`'s roles for `SOLUTION`, those plus `SOLUTION`'s for `COMMERCIAL` —
  and for `INTERPRET`
  `invitation_id` plus `anchors[]` built from one person's answers, skipping a blank anchor exactly
  as `ScreenContextBuilder.anchorsWritten` skips it. Every key the exporter names is present, `null`
  where there is no value.
- **FR-006** `instructions/runner.py`: call the model with
  `keel_runtime.executor.ClaudeCodeExecutor`, constructed with `home=<run>/jobs` so its job
  directories, `envelope.json`, `request.json` and `events.jsonl` land in the evidence. Validate the
  answer with `keel_runtime.response_validator.validate_response` against the same contract. Record
  per call: the prompt, the envelope, whether the recovery pass fired, `num_turns`,
  `total_cost_usd`, and the wall clock.
- **FR-007** `instructions/runner.py`: N runs per case, default 3, `N=` on the make target. Cases are
  independent and each is scored on its own; nothing is averaged before it is reported.
- **FR-008** A pre-flight, in the shape of S-004's `_claude_ready()`: `claude` on PATH and logged in;
  the keel-cloud checkout present with the `screenContracts` task; the corpus present. Any missing
  one is a refusal to start with the reason printed, never a zero score.

### Scoring — marks version 1

- **FR-009** `instructions/align.py`: align produced beliefs to golden beliefs **structurally
  first** — same stage; same `expectation.type`; for an `INTERVAL` the same `measure.kind` and
  overlapping bands (open bounds treated as infinite); for a `CHOICE` the same expected option after
  normalisation, else an option-set overlap above a stated threshold. Matching is a deterministic
  greedy maximum over the pair scores with ties broken by golden id order, and it is unit-tested with
  no model.
- **FR-010** `instructions/judge.py`: a model-as-judge, used **only** where FR-009 leaves genuine
  ambiguity — two or more goldens tied at the top score, or a produced belief with no structural
  candidate. It is given the two statements and may answer only *this one*, *that one* or *no match*;
  it can never assert a match that FR-009's structure rejects. Every judge call, its input and its
  answer are recorded, and the report states **what fraction of the alignment a model decided**.
- **FR-011** `instructions/score.py`: per case, per run — **golden-belief recall**; **exact-match
  rate**, reported per field on `type`, `measure.kind`, `measure.unit`, expected-option-or-band,
  `risk`, `mark` and **`founderPhrase`**; **extra-belief count**; the **`NEEDS_INPUT`-as-failure**
  rule of decision 14; and the aggregate's verdict from FR-012. A matched pair's phrase and band are
  reported side by side, golden against produced, so a right band from a wrong phrase is visible.
- **FR-012** `instructions/validate.py`: collect every produced belief set of a run into one batch
  and hand it to keel-cloud's `screenContracts validate` in **one** invocation, reading back the
  refusal report — `accepted`, or `{kind: shape|rule, rule, path, message}`, plus the built bucket
  labels for an accepted set (keel-cloud spec 029 FR-030…FR-032). **The invariants are never
  reimplemented here.**
- **FR-013** `instructions/score.py`: for the reading — **anchoring accuracy** over every anchor the
  model was given, plus **precision and recall on `GUESSED` reported separately**, plus a confusion
  matrix per entry and overall.
- **FR-014** `instructions/marks.py`: `MARKS_VERSION` and the marks — anchoring accuracy ≥ 0.90,
  golden-belief recall ≥ 0.80, refusals = 0 — overridable from `instructions/marks.toml` and on the
  command line, and **recorded in the run's verdict with the version that judged it**. Any change to
  a mark, a metric's definition or an alignment rule bumps `MARKS_VERSION`, under the same rule
  `evals/policy.py` states for `POLICY_VERSION`.

### The run, the report, the target

- **FR-015** `instructions/report.py`: a run directory `runs/<ts>-instructions[-baseline]/` created
  through `harness.evidence.new_run_dir`, carrying `versions.json` (the five sibling commits, via
  `harness.evidence.write_versions`), `verdict.json` (`{passed, marks, marks_version, model,
  n_runs, cases, errored, duration_s, total_cost_usd}`), `scorecard.json` (every case, every run,
  every metric), `cases/<entry>/<stage|person>/<run>/{prompt.txt,envelope.json,diff.json}`,
  `contracts/` (FR-002's export), `corpus.sha256`, and a self-contained `report.html`.
- **FR-016** `report.html` carries, per case, a **diff**: the golden beliefs down one side, the
  produced beliefs down the other, matched pairs joined with their per-field agreement, unmatched
  goldens marked missing, extras marked extra, and the aggregate's refusal, if any, quoted in its
  own words. A reading case shows the anchor prompt, the person's words, the golden word and the
  model's.
- **FR-017** `Makefile`: `instruction-eval` (opt-in, `venv` prerequisite, `$(PY) -m instructions.run`
  with `BASELINE=`, `N=`, `K=` and `MARKS=` passed through), added to `.PHONY`, with a comment naming
  this spec and the money it costs. It is **not** a dependency of `eval`, `eval-all` or `eval-live`,
  and it needs no `make up`.
- **FR-018** `tests/test_instruction_align.py`, `tests/test_instruction_score.py`,
  `tests/test_instruction_context.py`, `tests/test_instruction_prompts.py`: stackless, model-free
  unit tests of the alignment (including the golden corpus aligned against itself, which must reach
  100 % recall and 100 % exact match on every field), the metrics arithmetic, the context filling
  against a recorded key list, and the payload shape. They run under `make unit` with the rest.

### What cannot be scored, rendered so a person can

- **FR-019** `instructions/report.py` MUST write a **register page** into every run: one section per
  market in the run, rendering every produced anchor prompt and every produced option list for that
  market, grouped by entry and stage, with the market's own country, region and language at the head
  of the section. It is for a person who knows that market to read.
- **FR-020** The report MUST state, in its header and beside the register page, that the register is
  **not scored** and that no metric represents it — design §10 step 4: "the register cannot be
  scored by code; a person who knows the market reads the produced anchors and options, and that
  reading is recorded". **No metric may be invented for it**, and a run's verdict never depends on
  it.
- **FR-021** The report header MUST carry one line naming the model the run was judged under — the
  `claude` CLI version and whatever the envelope reports — and stating that the marks are comparable
  only within a model, because keel-runtime sends no `--model` and this feature does not change that.

### Docs and findings

- **FR-022** `README.md` gains an `## The instruction eval (make instruction-eval)` section — what it
  measures, that it is model-backed and opt-in, that it needs no stack, what it costs, and the
  `MARKS_VERSION` rule. `AGENTS.md`'s "no LLM, ever" sentence is amended to name its two exceptions
  by name — S-004 and this — rather than being contradicted by them.
- **FR-023** Findings go where this repo already puts them: an instruction that cannot reach a golden
  belief is a **keel-cloud defect** and goes to `runs/DRIFT.md` in the seven-part format, with the
  run bundle named; a harness bug, a judgement call or a gate result goes in this feature's
  `tasks.md` `## Discovered`.

## Success Criteria

- **SC-001** `make instruction-eval BASELINE=1` against keel-cloud before spec 029's rewrite
  produces a complete run directory whose verdict is `failed` and whose failures name the contract —
  and produces it without editing a single file in keel-cloud.
- **SC-002** `make unit` green, including the self-alignment test: the corpus aligned against itself
  scores 100 % recall and 100 % exact match on every field, so a zero in a real run is the model's
  and never the matcher's.
- **SC-003** A run against rewritten instructions reports anchoring accuracy, `GUESSED` precision and
  recall, golden-belief recall, per-field exact-match rates **including `founderPhrase`**,
  extra-belief counts, `NEEDS_INPUT` outcomes and the aggregate's verdict per set — for all seven
  entries, three stages and every person, at N=3.
- **SC-004** The marks are met and the verdict is `passed`: anchoring accuracy ≥ 90 %, golden-belief
  recall ≥ 80 %, refusals = 0.
- **SC-005** No file under keel-cloud's `canon/designs/measured-beliefs/` differs before and after
  any run — asserted by the run's own hashes, not by inspection.
- **SC-006** `make eval`, `make eval-all` and `make eval-live` behave exactly as before: no new
  collection, no new marker, no change to `evals/policy.py` and no change to `POLICY_VERSION`.
- **SC-007** Every run writes a register page rendering every produced anchor prompt and option list,
  grouped by market, and states in its header that the register is unscored and that no metric
  represents it. A person who knows the market reads it and that reading is recorded with the run
  (design §10 step 4). **No run's verdict depends on it.**
- **SC-008** Every run's header names the model it was judged under — the `claude` CLI version and
  whatever the envelope reports — and says the marks are comparable only within a model.

## Judgement calls

1. **Its own package, not a scenario.** A scenario is a browser walking a journey against a running
   stack; this is a batch of model calls against files. Putting it in `evals/` would have made
   `pytest evals` collect it and forced a marker to keep it out — one more thing between the
   deterministic set and an accident. Its own package and its own entry point cost nothing and make
   the separation structural.
2. **No stack.** It would have been easy to require `make up` and reach `introduceAssumptions` over
   HTTP. It would also have made every eval result contingent on Postgres, Flyway, a seeded project
   per case and a free port. The Gradle task keel-cloud spec 029 adds is the whole dependency, and it
   needs none of that.
3. **Structure first, the model second.** Alignment by a model alone would be a rubric nobody can
   read. Alignment by structure alone would miss a belief that is right and worded differently. So:
   structure decides, the model only breaks ties, and the report says how often it was asked —
   because a score that a model largely produced should say so.
4. **`GUESSED` precision and recall, not just accuracy.** A reader that calls everything `ANCHORED`
   scores well on accuracy in a corpus where most answers are anchored, and is exactly the failure
   the whole instrument exists to prevent (design §4: "the anchor removes guessers before they touch
   a count"). Reporting the two separately is the only way the number can be trusted.
5. **The baseline is a deliverable, not a warm-up.** It is the only measurement of the old
   instructions that will ever exist, and after the rewrite it cannot be taken again. So it is
   User Story 1, it has its own acceptance scenarios, and it is expected to be red.
6. **The model is recorded, not pinned.** `ClaudeCodeExecutor` sends no `--model`, and this repo does
   not add one — it calls the executor the way production does, which is the point. The cost is that
   the marks are only comparable within a model, and the report header says so out loud (FR-021).
7. **The register gets a page, not a number.** It would have been easy to invent a metric — token
   overlap against the corpus's own anchors, say — and it would have been a number that looked like
   evidence and was not. The design is explicit that a person who knows the market has to read it, so
   the run renders every anchor and option list per market and records what that person said. An
   unscored thing rendered honestly beats a scored thing measured wrongly.
8. **A `NEEDS_INPUT` is a failure, not a neutral.** Decision 14 removed the two cases where an
   assumption screen could legitimately ask, and the harness always supplies a statement. So an ask
   is the instruction failing to do its job, and folding it into a rate as anything softer would hide
   exactly the regression the eval exists to catch.

## Assumptions

**This feature depends on keel-cloud spec 029, and the two run in a fixed order.**

1. keel-cloud 029 lands its **two contract additions** — `founderPhrase` beside every band, and an
   optional `market` on a new role — and then its **exporter and validator**. Both are hard
   prerequisites, and in that order: the exporter serialises the contract whole, so a baseline taken
   before `founderPhrase` exists measures a different contract and cannot be compared with a later
   run that scores the §8.3 mapping.
2. **This feature is built and its baseline recorded**, against keel-cloud's *current*, un-rewritten
   instructions. The baseline must be taken before any instruction is edited or it cannot be taken.
3. keel-cloud 029 rewrites `interpret.md`, then the three `*-assumptions.md`, then the frames.
4. The two repositories iterate together until SC-004's marks pass. This is expected to take more
   than one pass; the instructions are prose.
5. keel-cloud removes its `awaiting-step-4` tag last, when the reading actually works.

**The corpus is frozen and is the reviewer.** Type, kind, expected option and risk must match the
golden beliefs exactly; wording is free (design §10 step 4). If an instruction cannot reach a golden
belief, the instruction is wrong — or the design is wrong and goes back to step 1. This repo never
edits it, and FR-001's hashes make that a check rather than a promise.

**keel-runtime is imported, not copied.** `build_prompt`, `_build_envelope_schema`,
`ClaudeCodeExecutor` and `validate_response` are used as they are, from the sibling checkout on
`PYTHONPATH` or installed editable. It is stdlib-only and needs Python ≥ 3.10; nothing about it must
change for this feature.

**The model is recorded, not pinned, and that is a limit on every number here.** keel-runtime sends
no `--model`; changing it is out of scope for this feature, and adding one would stop the call being
production's call. So the harness records the `claude` CLI version and whatever the envelope reports,
prints both in the report header (FR-021), and the marks are comparable only within a model. Two runs
under different models are two different measurements, and the report never pretends otherwise.

**The register and the phrase are two different kinds of unmeasurable, and only one stayed that
way.** The phrase mapping *became* measurable when keel-cloud spec 029 put `founderPhrase` on the
wire, and it is now a scored field. The register did not and will not: "the register cannot be scored
by code" (design §10 step 4). It is rendered per market for a person to read, that reading is
recorded, and no metric is invented for it.

**No credential, no cloud.** Nothing here calls `keel_runtime.cloud_client`, `config.load()` or the
poller, so no device authorisation and no keel-cloud server is involved. The executor's own env
allow-list already excludes `KEEL_HOME` and `KEEL_BASE_URL`.

**This repo still reports and never fixes.** An instruction that scores badly is a keel-cloud
finding with a run bundle behind it, not a patch made here (AGENTS.md).
