# Contract: the metrics, marks version 1

Every number a run reports, defined so that two people reading the report agree on what it says.
Changing any definition on this page bumps `MARKS_VERSION`, under the rule `evals/policy.py` already
states for `POLICY_VERSION`: scores under different versions describe different rubrics and are not
comparable.

## The three marks

| Mark | Default | Read from |
|---|---|---|
| anchoring accuracy | ≥ 0.90 | `totals.anchoring_accuracy` |
| golden-belief recall | ≥ 0.80 | `totals.golden_belief_recall` |
| refusals | = 0 | `totals.refusals_by_rule`, summed |

A run's verdict is `passed` only if all three are met. `errored` cases (an executor failure, not a
model answering badly) make the run `errored` and no verdict is claimed at all — a harness that could
not reach the model has measured nothing.

Marks live in `instructions/marks.toml`, are overridable with `MARKS=<file>` on the target, and are
written into `verdict.json` with the `MARKS_VERSION` that judged them.

## The reading metrics

Over every anchor the model was **given** — an anchor the person left blank, or answered with a tap,
never reaches the model and is not in any denominator.

```
answered           = anchors given, for which the model returned a word
anchoring_accuracy = agree / answered

guessed_precision  = (called GUESSED and was GUESSED) / (called GUESSED)
guessed_recall     = (called GUESSED and was GUESSED) / (was GUESSED)
```

**Both are always reported beside accuracy.** In this corpus most anchors are anchored, so a reader
that answered `ANCHORED` to everything scores high on accuracy and has recall zero on the one
judgement the instrument exists to make. Accuracy alone would call that reader good.

The confusion matrix `{aa, ag, ga, gg}` is reported per entry and overall, and every disagreeing case
links to the anchor text that produced it.

**Not an alignment problem, a failure**: an answer that omits an anchor id it was given, or invents
one, is recorded in `missing_ids`/`extra_ids` and counted against `answered` — never quietly matched
by position.

## The assumption metrics

### golden-belief recall

```
golden_belief_recall = |matched| / |golden beliefs of this stage|
```

Per case, per run; the total is over every assumption case in the run. `matched` is the alignment of
[data-model.md](../data-model.md) §4 — structure first, the judge only for genuine ties.

### exact-match, per field

Over **matched pairs only** — an unmatched golden is already counted by recall and counting it twice
would double-penalise.

| Field | Agrees when |
|---|---|
| `type` | both `INTERVAL` or both `CHOICE` |
| `founderPhrase` | equal after case- and whitespace-normalisation. Absent on both sides agrees (a `CHOICE` has no phrase); present on one side only is a miss |
| `measure.kind` | equal (intervals only; a choice pair scores `n/a`, excluded from the rate) |
| `measure.unit` | equal after case- and whitespace-normalisation (intervals only) |
| expected-or-band | for a `CHOICE`, the expected options are equal after normalisation; for an `INTERVAL`, both bounds agree on value, `inclusive` and `exact` — an absent bound must be absent on both sides |
| `risk` | equal |
| `mark` | equal |

**Reported per field, never merged.** A set that gets every kind right and every unit wrong is a
different problem from one that gets half of each, and one percentage hides which.

The band comparison is exact, not fuzzy. The corpus's bands come from the §8.3 phrase table, which is
"a versioned fixture, not a judgement" — a band that is close but not equal did not apply the table.

**The phrase and the band are read together.** For every matched pair the report shows the golden
phrase and band beside the produced phrase and band, because the four combinations are four different
findings:

| Phrase | Band | What it means |
|---|---|---|
| agrees | agrees | the model read the founder and applied the table |
| agrees | differs | it read the founder and got the §8.3 arithmetic wrong — an instruction fix in the table |
| differs | agrees | it produced a right band from a phrase the founder did not use — right for the wrong reason, and unstable |
| differs | differs | it did not read the founder's size at all |

Before keel-cloud spec 029 put `founderPhrase` on the wire, all four looked like one number.

### `NEEDS_INPUT` is a failure

An assumption screen never asks the founder mid-job; its only legitimate `NEEDS_INPUT` is a missing
statement (design decision 14), and the harness always supplies one. So an ask is a **failed case**:
it counts in the recall denominator as a case that found no goldens, and it is *also* reported as its
own outcome, so the report can say how the failure happened rather than only that it did.

### extra beliefs

```
extra_beliefs = |produced beliefs with no golden match|
```

Reported as a count, not a rate, and **not** a mark. A stage that finds a real belief the corpus did
not think of is a finding, not a failure — but a stage that produces eleven where the golden has five
is over-generating, and the count is how that shows.

### the aggregate's verdict

Per produced set, from keel-cloud's own validator:

- `accepted` — the aggregate would have taken it.
- refused, `kind: "rule"` — it fit the contract and the aggregate refused it, by id: `E1`…`E5`, `Q1`,
  `Q2`, `Q4`, `Q5`, `M1`. **These are what the refusals mark counts.**
- refused, `kind: "shape"` — it did not fit the contract; the model failed to answer, and the
  aggregate never saw it. Reported separately, and separately again from a `schema_valid: false`
  answer, which keel-runtime's own validator rejected before this repo ever asked keel-cloud.

Three different ways of being wrong, three lines in the report, because they call for three different
fixes: the shape of the instruction's envelope section, the instruction's rules, and the
instruction's arithmetic.

### the bucket diff

For an accepted set, the labels keel-cloud's builder produced for each `BUCKETS` selection, shown
beside the corpus's `expected.buckets` for the matched golden's selection. A scale that came out
different is a band that came out different, made visible as a scale — which is the form a founder
would actually have seen.

## Stability

Each of the N runs is scored on its own. The report gives the **spread** — the min and max of each
metric across the runs of a case — and never an average alone. A case that passes twice and fails
once is not 67 %; it is an unstable instruction, and that is the finding.

## What is measured, and what is not

**Measured**: whether the aggregate would take the result; which golden beliefs were reached; how
exactly; what was invented; whether a guess was spotted.

**Not measured, and stated in every report and beside the register page**:

- **The register.** Whether an anchor sounds like a supply yard in Texas or a builder's merchant in
  London cannot be scored by code — design §3.8 and §10 step 4 both say so, the second adding what
  is done instead: "a person who knows the market reads the produced anchors and options, and that
  reading is recorded". The run writes `register.html`: every produced anchor prompt and option
  list, grouped by market. **No metric represents it and no verdict depends on it.**
- **Whether an option list leads.** Design §4's table makes a leading option list the most expensive
  authoring mistake in the design — the leading dropdown's recall collapses to 1 % in the bad world —
  and there is no golden data for it. The register page is where a reader would notice one; nothing
  scores it.
- **Wording.** Headings and statements are free (design §10 step 4); they contribute only a
  tie-break to alignment and nothing to any score.

**No longer on this list**: the phrase mapping. It was unmeasurable at first authoring because the
contract had no field for the founder's phrase; keel-cloud spec 029 added `founderPhrase`, and it is
now a scored field with its own four-way reading above.

## Judgement calls

Append-only, in `instructions/marks.py`'s module docstring, across every version — kept, struck
nowhere, because the rubric's history matters.

1. **v1**: exact-match is over matched pairs only, so recall and exactness are not double-counted.
2. **v1**: `measure.kind`/`measure.unit` are `n/a` for a choice pair and excluded from the rate
   rather than counted as agreeing.
3. **v1**: extra beliefs are counted and not marked. Over-generation is a finding first.
4. **v1**: band equality is exact, because the phrase table is a fixture.
5. **v1**: `GUESSED` precision and recall are mandatory beside accuracy, never optional.
6. **v1**: a shape refusal, a schema-invalid answer and a rule refusal are three different lines.
7. **v1**: the spread is reported; nothing is averaged before it is reported.
8. **v1**: `founderPhrase` is a scored exact-match field, and absent-on-both-sides agrees, because a
   `CHOICE` has no phrase and requiring one would penalise every Choice belief.
9. **v1**: a `NEEDS_INPUT` from an assumption screen whose statement was present is a failed case
   counted in the recall denominator, per design decision 14 — not excluded, and not softened.
10. **v1**: the register is rendered and never scored. A metric here would look like evidence and be
    similarity to one hand-written example; the design requires a person, so the run records what the
    person said.
