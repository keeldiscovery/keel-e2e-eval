# Phase 0 research: the instruction eval

Eight decisions taken before any code, each with what it was taken over.

---

## R1 — Where the eval lives, and why not in `evals/`

**Decision**: its own top-level package, `instructions/`, with a `python -m instructions.run` entry
point and a `make instruction-eval` target. Not a pytest test, not in `evals/`, not a module of
`harness/`.

**Why**: `make eval` is `pytest evals -q -m "not live"`. Anything in `evals/` is collected by
default and stays out only by carrying a marker — one more thing between the deterministic set and
an accident, and a marker is exactly what got forgotten in the class of mistakes this repo exists to
catch. `harness/` is the machinery the scenarios share and has no model call in it; putting one
there would make every scenario's shared code import a model path it never uses.

The entry-point precedent already exists: `harness.eval_all` and `harness.evidence` are both
`python -m` modules driven by make targets. This follows them.

**Rejected**: a pytest test with a `instructions` marker (collection by default is the wrong
default); a subcommand of `harness.eval_all` (that module's job is to run the scenario set and index
it).

## R2 — No stack, and what that buys

**Decision**: the eval requires no `make up`. No Postgres, no keel-cloud server, no keel-web, no
runtime process, no port.

**What it needs instead**: the keel-cloud checkout on disk (for the corpus, the instruction files and
one Gradle task), a JDK for that task, keel-runtime on `PYTHONPATH`, and a logged-in `claude`.

**Why it matters more than convenience**: this repo's sharpest operational rule is that two referee
sessions must never share a profile, because the stack's ports and runtime home are fixed per profile
and a second `make up` drops the database out from under a running eval. An eval that binds nothing
is outside that rule entirely — it can run while a scenario runs, on either profile, without a
thought. The only shared resource left is money, which is why the target still refuses a concurrent
run of itself.

**What was rejected**: reaching `introduceAssumptions` over the founder HTTP API against a running
keel-cloud. It would have required creating a project, framing a stage, approving it and posting as
an authenticated founder for each of 21 cases per run, and every one of those set-ups is a way for
the eval to go red for a reason that has nothing to do with an instruction. keel-cloud spec 029's
`validate` verb exists precisely so this repo does not have to.

## R3 — Reuse, never re-implement: the prompt and the call

**Decision**: `keel_runtime.executor.build_prompt` builds the prompt and
`keel_runtime.executor.ClaudeCodeExecutor` makes the call. This repo writes no prompt text and
constructs no argv.

**What that pins, exactly** (and why copying would have been wrong):

- The prompt is `TASK` / `CONTRACT` / a `SOURCE MATERIAL` heading / a nonce-fenced
  `<<<KEEL-DATA {nonce}>>>` block carrying `founder_text`, `participant_answers`, `earlier_turns`
  and `project_context`. The heading is a single long module constant and the nonce is fresh per
  call. A hand-written copy would be wrong in an invisible way the first time either changed.
- The envelope schema is `_build_envelope_schema(response_contract)`, which reads exactly
  `allowed_outcomes` and `completed_result_schema` and sets `additionalProperties: false` at the
  top level.
- The call is `claude -p --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence
  --max-turns … --max-budget-usd … --output-format stream-json --verbose --json-schema … --system-prompt …`,
  with the prompt on **stdin**, a per-job cwd, and a strict env allow-list. And one conditional
  recovery pass when the answer never fit its shape.

**The consequence to state plainly**: there is no `--model` flag anywhere in keel-runtime, so the
model is whatever the CLI defaults to. This repo does not add one — adding it would stop the call
being production's call. So the model is *recorded* (R7), and the marks are comparable only within a
model.

**Also reused**: `keel_runtime.response_validator.validate_response`, so "did the answer fit the
contract" is answered by the same code production answers it with. Note that its behaviour changes
if `jsonschema` is installed (the extra `[schema]`); the run records which path was taken.

## R4 — Reuse, never re-implement: the invariants

**Decision**: every produced belief set is validated by **keel-cloud's own aggregate**, through spec
029's `screenContracts validate` verb, in one Gradle invocation per run.

**Why**: `E1`–`E5`, `Q1`, `Q2`, `Q4`, `Q5` and `M1` are fourteen rules with real arithmetic behind
them — floors, ceilings, resolutions, a unit table, a currency table, a literal string check. A
Python re-implementation here would be a second source of truth for a set of rules that are still
young, and the day one changed the eval would keep reporting the old one. Worse, the failure would be
silent in the wrong direction: a refusal the eval does not know about is a belief the founder would
never have been shown, scored as though they would have.

**The cost**: a Gradle start per run, and a hard dependency on keel-cloud 029 landing first. Both
accepted; the batch shape means the cost is per run rather than per case.

## R5 — Alignment: structure first, a model only for ties

**Decision**: a produced belief and a golden belief are candidates only if they agree structurally —
same stage, same expectation type, same measure kind for an interval with overlapping bands, the
same expected option (or a stated option-set overlap) for a choice. Candidate pairs are scored and
matched by a deterministic greedy maximum with ties broken by golden id order. A model is asked only
where the structure genuinely leaves two answers.

**Why not a model for the whole thing**: a rubric nobody can read is not a rubric. If the score is a
model's opinion end to end, a red run cannot be attributed and a green one cannot be trusted, and
this repo's whole existence is the claim that a run's bundle explains its number.

**Why not structure alone**: `01-countly.yaml`'s `P4a` and `P4b` are two beliefs on one shared
multi-select selection with the same option list, differing only in which option each expects — and
a model that produced them in the other order, or produced one, is a case a structural matcher will
either mis-pair or drop. Dropping is safe but pessimistic; mis-pairing is worse. So: the judge
chooses among the candidates the structure already found, and may say *no match*; it can never
assert a pair the structure rejected, and it never sees a pair the structure already settled.

**And it is measured**: the report states what fraction of the alignment a model decided. If that
fraction is large, the number should be discounted, and a reader can see by how much.

## R5a — `existing_roles` per stage  *(answered)*

**Decision**: derive them from what earlier stages' beliefs are `askedOf` — `[]` for `PROBLEM`,
`PROBLEM`'s roles for `SOLUTION`, those plus `SOLUTION`'s for `COMMERCIAL`.

**Why it is a reading and not a lookup**: a corpus entry lists its roles flat and records no
creating stage; the entries were written to check the aggregate, not to reconstruct a screen's
context. The `askedOf` edge is the only evidence in the file of which stage needed which role, and it
mirrors production, where each assumption screen sees what earlier ones introduced.

**What it changes if it is wrong**: the extra-belief count, mostly — a later stage that is shown no
roles invents duplicates of ones the corpus already has, and every one of those is an "extra" that is
really a harness artefact. So the report names the `existing_roles` it supplied for every case, and a
suspiciously duplicate-heavy extras list is read as this first.

## R6 — The metrics, and the one that matters most

**Decision**: report **anchoring accuracy** with **`GUESSED` precision and recall beside it**, always,
never accuracy alone.

**Why**: in the corpus most anchors are `ANCHORED` — a reader that answered `ANCHORED` to everything
would score high on accuracy and be the exact failure the whole instrument was built to prevent.
Design §4's table is the argument: the hybrid instrument's virtue is that "the anchor removes
guessers before they touch a count", and a reader that never spots a guess removes nobody. Letting a
guess through is the costly error, so the recall of `GUESSED` is the number to read first.

The same logic shapes the assumption metrics: **exact-match is reported per field**
(`type`, `measure.kind`, `measure.unit`, expected-or-band, `risk`, `mark`, `founderPhrase`) rather
than as one figure, because a set that gets every kind right and every unit wrong is a different
problem from one that gets half of each, and a single percentage hides which.

**`founderPhrase` is the field that makes the band readable.** keel-cloud spec 029 puts it on the
wire (design §8.1 step 4), and it turns one number into a pair: the phrase the model read, and the
band it produced from it. A right band from a wrong phrase, and a right phrase mapped to a wrong
band, are different faults with different fixes — one is comprehension, one is the §8.3 table — and
without the phrase they were the same number. The report shows the golden pair beside the produced
pair for every match.

**And a `NEEDS_INPUT` from an assumption screen is a failure**, not an outcome to be excluded.
Decision 14 removed both cases where such a screen could legitimately ask, and the harness always
supplies a statement, so an ask means the instruction did not do its job. It counts in the recall
denominator as a case that found nothing, and is reported separately so the report can say *how* it
failed.

## R6a — What cannot be scored, and what is done instead

**Decision**: the register gets a **page**, not a number. Every run renders every produced anchor
prompt and option list, grouped by market, with that market's country, region and language at the
head; the report says in its header and beside the page that these are unscored; a person who knows
the market reads them and that reading is recorded with the run. **No metric is invented.**

**Why not a metric**: design §10 step 4 is explicit — "the register cannot be scored by code; a
person who knows the market reads the produced anchors and options, and that reading is recorded".
It would have been easy to compute token overlap against the corpus's own anchors and call it a
register score. It would have measured similarity to one hand-written example and been reported as
though it measured whether a Texan supply-yard manager recognised the words. A number that looks like
evidence and is not is worse than a blank, because a blank prompts someone to go and look.

**What this leaves genuinely unmeasured**, stated in every report: the register; whether an option
list *leads* (design §4's most expensive authoring mistake, whose recall collapses to 1 % in the bad
world) — there is no golden data for it, and the register page is where a reader would notice it; and
wording, which is free by design and contributes only an alignment tie-break.

**What stopped being unmeasured**: the phrase mapping. It was on this list at first authoring and
came off it when keel-cloud spec 029 put `founderPhrase` on the wire.

## R7 — What a run must record to be explicable later

**Decision**: `versions.json` (the five sibling commits and their dirty flags, via
`harness.evidence.write_versions`), the corpus file hashes before and after, the exported contract as
used, `MARKS_VERSION` and the marks, `N`, the `claude` CLI version and whatever the envelope reports
about the model, the per-call `num_turns` / `total_cost_usd` / recovery-pass flag, and every prompt
and envelope in full.

**Why the model identity is not optional**: it is the one input to the score that this repo cannot
pin (R3) and cannot infer afterwards. Without it a run six weeks later reads as an instruction
regression when it may be a model change. So it is not merely in a file — it is a line in the report
header, beside the marks it qualifies.

**And the `existing_roles` supplied per case** (R5a), because a duplicate-heavy extras list is more
often that reading being wrong than the instruction being wrong.

**Why the recovery-pass flag**: `ClaudeCodeExecutor` retries once when the answer never fit its
shape. An instruction whose results only validate on the second pass has a problem the final envelope
does not show.

## R8 — Where a finding goes

**Decision**: three places, and the distinction is this repo's existing one.

- **`runs/DRIFT.md`** — an instruction that cannot reach a golden belief, an anchor prompt that trips
  `Q5`, a produced questionnaire that writes its own buckets. These are keel-cloud defects, in the
  seven-part format, with the run bundle named. This repo diagnoses; keel-cloud fixes.
- **this feature's `tasks.md` `## Discovered`** — a harness bug, a judgement call made mid-flight, a
  gate result, an alignment rule that turned out to need a threshold nobody had thought about.
- **`instructions/marks.py`'s module docstring** — a numbered, append-only judgement-calls block,
  exactly as `evals/policy.py` keeps one, so the rubric's history survives its versions.

**The one thing that does not go anywhere**: a change to the corpus. It froze at the end of step 3.
If an instruction cannot reach a golden belief, the instruction is wrong, or the design is wrong and
goes back to step 1 — and either way the answer is a DRIFT entry and a conversation, never an edit
(design §10). FR-001's hashes make that a check the run performs on itself rather than a promise it
makes.
