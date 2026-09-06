# Implementation Plan: The instruction eval

**Branch**: `009-instruction-eval` | **Date**: 2026-09-06 | **Spec**: [spec.md](./spec.md)

**Input**: [spec.md](./spec.md), and the design of record — keel-cloud
`canon/designs/measured-beliefs-design.md` §10 step 4 and decision 14, as revised 2026-09-06 (commit
`17c7642`). Hard prerequisites, in order: keel-cloud spec 029's **two contract additions**
(`founderPhrase`, a new role's `market`), then its **exporter and validator**
(`specs/029-measured-beliefs-instructions/contracts/exported-contract-format.md`).

**On the artefact set.** Specs 004–008 in this repo are `spec.md` + `tasks.md` and nothing else, and
that is the right shape for a scenario: a browser walk against a running stack, whose design of
record already lives in keel-cloud. This feature is not that. It creates a package, a cross-repo file
contract, a scoring rubric with a version constant, and a set of metric definitions that a founder
has to be able to argue with — the same kinds of thing specs 001–003 wrote a plan, a research note
and a contracts directory for. So this one has them too, in the house voice.

## Summary

Build `instructions/`: a model-backed batch eval that reads keel-cloud's frozen corpus and its
actual instruction files, builds production-identical prompts through keel-runtime's own
`build_prompt`, calls a real `claude` through keel-runtime's own `ClaudeCodeExecutor`, and scores
what comes back — assumptions against the golden beliefs (structure first, a model only to break
ties, and the founder's phrase scored beside its band now that keel-cloud spec 029 puts
`founderPhrase` on the wire) and readings against the golden anchorings (accuracy, and `GUESSED`
precision and recall apart). Every produced belief set is also handed to keel-cloud's own aggregate, in one batch, for its
verdict by rule id. A run leaves a directory in this repo's existing style with per-case diffs — and one page with no
numbers on it at all, rendering every produced anchor and option list per market for a person who
knows that market to read, because the design says the register cannot be scored by code. The first
thing the harness produces is a baseline against the un-rewritten instructions, which is expected to
be red.

**Technical approach**: nothing about the prompt or the call is written here — keel-runtime is
imported and used, keel-cloud's contract is exported and read, keel-cloud's validator is invoked. The
code this repo actually owns is three things: filling a context from a corpus entry, aligning two
belief sets, and turning agreements into numbers. Those three are pure, and all three are unit-tested
with no model at all — which is what makes a red run attributable.

## Technical Context

**Language/Version**: Python 3.11+ (this repo's floor), matching `harness/` and `evals/`. keel-runtime
requires ≥ 3.10 and is stdlib-only, so importing it adds no dependency.

**Primary Dependencies**: `pyyaml` — **the one new requirement**, to read the corpus (`requirements.txt`
today is `pytest`, `playwright`, `requests`; keel-cloud's own `check_corpus.py` uses `yaml`). Plus
keel-runtime on `PYTHONPATH` from the sibling checkout `stack.toml` already names. No Anthropic SDK,
no HTTP client to any model provider — the model is reached the way production reaches it, by the
`claude` CLI under `ClaudeCodeExecutor`.

**Storage**: the run directory. Nothing is written outside `runs/` except the run's own copy of the
exported contract, which the exporter writes into the run directory.

**Testing**: `pytest tests` (`make unit`) for the pure half — alignment, metrics, context filling,
payload shape — with the corpus aligned against itself as the fixed point. The model half has no
unit test and is not meant to have one; it is measured, not asserted.

**Target Platform**: a developer's machine with a logged-in `claude` and a JDK for keel-cloud's
Gradle task. **No Docker, no Postgres, no ports.**

**Project Type**: a fifth package beside `stack/`, `harness/`, `evals/` and `tests/`, with its own
`python -m` entry point, the way `harness.eval_all` and `harness.evidence` already have theirs.

**Performance Goals**: none, but a cost goal, because this one spends money: seven entries × three
stages × N, plus seven entries × their people × N. At N=3 that is roughly 63 assumption calls and
around 150–200 reading calls per full run. The run prints its case count and estimated cost before it
starts and its actual `total_cost_usd` after, summed from the envelopes.

**Constraints**: the corpus is read-only and hash-checked; `make eval`/`eval-all`/`eval-live` and
`evals/policy.py` are untouched; the repo reports and never fixes; every model call goes through
keel-runtime's executor rather than a client of this repo's own.

**Scale/Scope**: one new package of ~9 modules, 4 new unit-test modules, 1 make target, 1 new
requirement, 2 docs edits. No change to `stack/`, `evals/` or the existing `harness/` modules beyond
importing two of `harness.evidence`'s functions.

## Constitution Check

*GATE: passed before Phase 0; re-checked after Phase 1.*

`.specify/memory/constitution.md` is the unfilled spec-kit template, as spec 001's plan recorded. The
binding rules are `AGENTS.md`'s and the design's, checked here in the same way:

| Inherited rule | How this feature meets it | Post-design |
|---|---|---|
| **The repo owns no product code and never fixes the product** | It reads keel-cloud and keel-runtime and writes neither. A bad instruction is a `runs/DRIFT.md` entry with a run bundle, not a patch (FR-020). | Pass |
| **The scenarios are deterministic; no LLM** | The scenarios are untouched — no new pytest collection, no new marker, no change to `evals/policy.py` or `POLICY_VERSION` (SC-006). This eval is not a scenario, does not live in `evals/`, and is not reachable from `make eval`. | Pass |
| **…except where a model is the subject, opt-in and named** | The precedent is S-004. `AGENTS.md`'s blanket sentence is amended to name both exceptions rather than be contradicted by them (FR-019). | Pass, with the doc change |
| **The evidence bundle is the product of a run** | FR-015 and FR-016: a run directory in the existing style, with the prompt and envelope of every call, per-case diffs, and a self-contained report. A green number with no bundle behind it is not a result here. | Pass |
| **A rubric change bumps its version** | `MARKS_VERSION` (FR-014), a separate constant from `POLICY_VERSION` so the two cannot be confused, under the same rule. | Pass |
| **Two sessions never collide** | This eval binds no port and needs no profile, so it cannot collide with a stack; it refuses to start if another instruction-eval run is live, because two would both spend money. | Pass |
| **Contract authority is the running sibling itself** | Strengthened: the contract is *exported* by the sibling rather than read off its running surface, and the aggregate's verdict is the aggregate's own (FR-002, FR-012). | Pass |

**Post-design re-check**: the one judgement worth recording is FR-010's model-as-judge. A repo whose
whole discipline is determinism is adding a component whose output is a model's opinion. It is
allowed because it is *bounded* — it may only choose among candidates the structural matcher already
found, or say *no match* — and because the report states what fraction of the alignment it decided,
so a reader can discount the score by exactly that much.

## Project Structure

### Documentation (this feature)

```text
specs/009-instruction-eval/
├── spec.md
├── plan.md              # this file
├── research.md          # Phase 0 — R1..R8
├── data-model.md        # Phase 1 — the corpus entry, the case, the alignment, the scorecard
├── quickstart.md        # Phase 1 — the baseline, then the loop
├── contracts/
│   ├── run-bundle-contract.md      # what a run leaves behind
│   └── metrics-contract.md         # every metric defined exactly, marks version 1
├── checklists/requirements.md
└── tasks.md
```

### Source (repository root)

```text
instructions/                 # NEW — the eval
├── __init__.py               # "the only package here whose subject is a model's answer"
├── run.py                    # `python -m instructions.run` — the entry point
├── corpus.py                 # FR-001 — read keel-cloud's frozen corpus, hashed
├── contract.py               # FR-002 — run keel-cloud's exporter, read what it wrote
├── instruction.py            # FR-003 — the instruction bytes production serves
├── context.py                # FR-005 — fill a screen's context keys from an entry
├── prompts.py                # FR-004 — the payload, then keel-runtime's build_prompt
├── runner.py                 # FR-006/007 — ClaudeCodeExecutor, N times, everything recorded
├── align.py                  # FR-009 — structural alignment, deterministic
├── judge.py                  # FR-010 — the bounded tie-breaker, counted
├── validate.py               # FR-012 — one batch to keel-cloud's aggregate
├── score.py                  # FR-011/013 — the metrics, incl. founderPhrase and NEEDS_INPUT
├── marks.py                  # FR-014 — MARKS_VERSION and the marks
├── marks.toml                # the default marks, overridable
└── report.py                 # FR-015/016 — the run bundle and report.html
                              # FR-019/020/021 — register.html, the unscored statements, the model line

tests/
├── test_instruction_align.py     # FR-018 — incl. the corpus aligned against itself
├── test_instruction_score.py     # FR-018 — the metrics arithmetic
├── test_instruction_context.py   # FR-018 — key filling against a recorded key list
└── test_instruction_prompts.py   # FR-018 — the payload shape

Makefile                      # + instruction-eval
requirements.txt              # + pyyaml
README.md  AGENTS.md          # FR-019
runs/DRIFT.md                 # FR-020 — where the findings go
```

**Structure Decision**: a fifth top-level package rather than a scenario in `evals/` or a module in
`harness/`. `evals/` is what `make eval` collects and is deterministic by rule; `harness/` is the
machinery the scenarios share and has no model in it. This is neither, and giving it its own name
makes the boundary structural rather than a marker someone has to remember (spec judgement call 1).
It borrows exactly two functions from `harness.evidence` — `new_run_dir` and `write_versions` — so a
run bundle is recognisably one of this repo's.

## Phase sequencing

1. **Read-only halves first**: `corpus.py`, `contract.py`, `instruction.py`, `context.py`,
   `prompts.py`, with their unit tests. At the end of this, `python -m instructions.run --dry-run`
   prints the exact prompt for any case without spending a penny — and that printed prompt is the
   thing to eyeball before three hundred calls are made against it.
2. **Scoring, still with no model**: `align.py`, `score.py`, `marks.py`, and the fixed-point test —
   the corpus aligned against itself must score 100 % on everything. A matcher that cannot recognise
   the golden set as itself cannot be trusted to score a model's.
3. **The calls**: `runner.py`, `report.py`. Now a run can happen.
4. **The baseline** — before keel-cloud edits an instruction. This is a gate on the *other*
   repository, not on this one.
5. **`validate.py` and `judge.py`** last of the code: the first needs keel-cloud 029's `validate`
   verb, the second is the only piece whose absence merely degrades the report rather than stopping
   it (without it, ambiguous pairs are reported unmatched and the recall floor is conservative).
6. **The register page**, which needs no model and no score — it renders what the runs already
   captured, and it is the only answer the design allows to a thing code cannot judge.
7. **Docs and DRIFT**, and then the long part: iterating with keel-cloud until the marks pass.

## Complexity Tracking

| Violation | Why needed | Simpler alternative rejected because |
|---|---|---|
| **A model in the scoring path** (`judge.py`) | Two golden beliefs about the same dimension can be structurally indistinguishable — `01-countly.yaml`'s `P4a`/`P4b` share a selection and an option list — and a purely structural matcher either picks arbitrarily or reports both unmatched. | Structure-only alignment was tried on paper first and is what FR-009 still does for every unambiguous pair; the judge is bounded to a choice among candidates and its influence is measured and printed, so the score degrades gracefully to the structural one if it is distrusted. |
| **A second version constant** (`MARKS_VERSION` beside `POLICY_VERSION`) | The scenario rubric and the instruction rubric change for unrelated reasons and at different rates; one constant would make every marks change invalidate scenario comparability and vice versa. | Reusing `POLICY_VERSION` was rejected on that ground alone. |
| **A page with no metric on it** (`register.html`) | Design §10 step 4: "the register cannot be scored by code; a person who knows the market reads the produced anchors and options, and that reading is recorded". A referee repo that reports only numbers would have had to either invent one or drop the criterion. | A token-overlap score against the corpus's own anchors was the obvious alternative and is worse than nothing: it measures similarity to one hand-written example while reading as though it measured whether a stranger in that market recognised the words. |
| **A new dependency** (`pyyaml`) | The corpus is YAML and it is keel-cloud's format, not ours to change. | Hand-parsing 21 000 lines of YAML, or asking keel-cloud to emit JSON, both put a translation between the harness and the frozen artefact it is supposed to read verbatim. |
