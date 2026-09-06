# Quickstart: the baseline, then the loop

## Prerequisites

Different from every other target in this repo: **no stack, and no `make up`.**

```bash
which claude && claude --version          # logged in; the run refuses to start otherwise
ls ../keel-cloud/canon/designs/measured-beliefs/corpus/   # seven YAML files
ls ../keel-runtime/keel_runtime/executor.py               # imported, not copied
cd ../keel-cloud && ./gradlew -q screenContracts --args="export /tmp/probe" && ls /tmp/probe
```

The last one is the hard prerequisite: keel-cloud spec 029's exporter and validator. Without it there
is no contract to build a prompt against and no aggregate to ask for a verdict. Check that the
exported contract already carries spec 029's two additions, or the baseline measures the wrong one:

```bash
python3 -c "import json;d=json.load(open('/tmp/probe/contracts/PROBLEM_ASSUMPTIONS.json'));print('founderPhrase' in json.dumps(d), 'market' in json.dumps(d))"
```

```bash
make venv          # pyyaml joins pytest/playwright/requests
make unit          # green, including the corpus-aligned-against-itself fixed point
```

## Look before you spend

```bash
make instruction-eval DRY=1 K=01-countly
```

Prints the exact prompt for every case it would run and the estimated cost, and calls nothing. Read
one assumption prompt and one reading prompt in full before authorising three hundred calls against
them: `TASK`, `CONTRACT`, the `SOURCE MATERIAL` heading, and the nonce-fenced block with
`project_context`. If the context keys look wrong, the fault is in `instructions/context.py` or in
keel-cloud's exporter, and it is far cheaper to find now.

## 1. The baseline — before keel-cloud edits an instruction

```bash
make instruction-eval BASELINE=1
```

**Expect it to fail, loudly, and keep the directory.** Today's `*-assumptions.md` emit
`question: {ask, disconfirming}` and today's `interpret.md` emits `claimType` and `stance`; neither
fits the contract spec 028 shipped, so every case is refused before a single belief is compared. A
baseline that passed would mean the harness was measuring something other than the instruction, and
the right response to a green baseline is to go and find the bug.

```bash
open runs/<id>-instructions-baseline/report.html
```

This is the only measurement of the old instructions that will ever exist. After keel-cloud rewrites
them it cannot be taken again.

## 2. The loop

keel-cloud spec 029 rewrites `interpret.md` first, then Problem, Solution, Commercial, then the
frames. After each:

```bash
make instruction-eval K=reading          # the reading eval alone, cheap
make instruction-eval K=01-countly       # one entry, all three stages
make instruction-eval                    # everything, N=3
```

Read four things in the report, in this order:

1. **`GUESSED` recall.** Before accuracy. A reader that never spots a guess scores well on accuracy
   in this corpus and has failed at the one job it has.
2. **The refusals, by rule id.** A refusal is not a low score — it is a result the founder would
   never have been shown, and it names exactly which sentence of the instruction is missing.
3. **The phrase beside the band.** A right band from a phrase the founder never used is right for
   the wrong reason and will not stay right. The diff shows both, golden against produced.
4. **The spread.** A case that passes twice and fails once is an unstable instruction, not a 67 %.

Then open `register.html` and read the anchors and option lists for a market you know — or send it to
someone who does. Nothing on that page is scored, and it is the only place the register is visible.

## 3. The marks

```
anchoring accuracy       ≥ 90 %
golden-belief recall     ≥ 80 %
refusals                 0
```

In `instructions/marks.toml`, overridable with `MARKS=<file>`, recorded in every `verdict.json` with
the `MARKS_VERSION` that judged it. **Change a mark, a metric definition or an alignment rule and
bump `MARKS_VERSION`** — the same rule `evals/policy.py` states for `POLICY_VERSION`, and a separate
constant so the two can never be confused.

## 4. Where a finding goes

- An instruction that cannot reach a golden belief, an anchor prompt that trips `Q5`, a questionnaire
  that writes its own buckets → **`runs/DRIFT.md`**, seven-part format, naming this run bundle. This
  repo diagnoses; keel-cloud fixes.
- A harness bug, a judgement call, a gate result → this feature's `tasks.md` `## Discovered`.
- **Never the corpus.** It froze at the end of step 3. If an instruction cannot reach a golden
  belief, the instruction is wrong, or the design is wrong and goes back to step 1. `corpus.sha256`
  makes that a check the run performs on itself.

## What this run does not tell you

Printed in every report header, so it is never forgotten:

- **The register is not scored, and no metric represents it.** Whether an anchor sounds like a
  builder's merchant in London is design §3.8's "cannot be checked by code", and §10 step 4 says what
  is done instead: a person who knows the market reads the produced anchors and options, and that
  reading is recorded. That is what `register.html` is for.
- **Whether an option list leads is not scored either.** It is design §4's most expensive authoring
  mistake and there is no golden data for it. The register page is where a reader would notice one.
- **The model is not pinned.** keel-runtime sends no `--model`, and this repo does not add one. The
  model is named in the report header; the marks are comparable only within it.

**One thing that used to be on this list and is not any more**: the §8.3 phrase mapping. keel-cloud
spec 029 puts `founderPhrase` on the wire, so the phrase is scored beside the band.

## Nothing is open

Both questions this spec first raised were answered by the design's revision of 2026-09-06:
`existing_roles` for a later stage is derived from earlier stages' `askedOf`, and a `NEEDS_INPUT`
from an assumption screen whose statement was present is a **failed case** — decision 14 removed the
two cases where such a screen could legitimately ask.
