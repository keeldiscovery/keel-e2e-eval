# Contract: the run bundle

What a run leaves behind. The bundle, not the number, is the product of a run — this repo's oldest
rule, and it applies here unchanged.

## The directory

```
runs/<YYYYMMDDTHHMMSSZ>-instructions[-baseline]/
```

Created through `harness.evidence.new_run_dir(slug)` with slug `instructions` or
`instructions-baseline`, so it sorts and indexes beside every scenario bundle this repo has.

## Files

| File | Contents |
|---|---|
| `versions.json` | the five sibling commits and their dirty flags, via `harness.evidence.write_versions` |
| `verdict.json` | `{scenario: "instructions", baseline: bool, passed, marks, marks_version, model, n_runs, cases, errored, duration_s, total_cost_usd}` |
| `scorecard.json` | every case, every run, every metric ([data-model.md](../data-model.md) §5) |
| `corpus.sha256` | every corpus file hashed at load and again at the end; a difference fails the run |
| `contracts/` | keel-cloud's export exactly as used: `<SCREEN>.json`, `context-keys.json`, `manifest.json` |
| `validation.json` | keel-cloud's own refusal report for the whole batch |
| `cases/<entry>/<subject>/<run>/prompt.txt` | the prompt as sent, in full, nonce and all |
| `cases/<entry>/<subject>/<run>/envelope.json` | the executor's envelope, including `num_turns`, `total_cost_usd`, `is_error` and the recovery flag |
| `cases/<entry>/<subject>/<run>/diff.json` | the alignment or the per-anchor comparison for this run |
| `jobs/` | `ClaudeCodeExecutor`'s own home for this run — its per-job dirs, `request.json`, `events.jsonl` |
| `register.html` | every produced anchor prompt and option list, grouped by market — the one artefact with no number in it |
| `report.html` | self-contained, one file, no network |

`verdict.json` mirrors the scenario bundles' own shape as far as it can, so `runs/INDEX-*.html` and
anything else that reads a bundle keeps working. Where it cannot — there is no `failed_step`, and
`score` is three numbers rather than one out of five — it says so with its own keys rather than
faking theirs.

## `report.html`

One file, no external resources, opens from disk. In order:

1. **The header** — verdict, the three marks against the three numbers, `MARKS_VERSION`, **one line
   naming the model this run was judged under** (the `claude` CLI version and whatever the envelope
   reports) with the sentence that the marks are comparable only within a model, `N`, the five
   sibling commits with dirty flags, the corpus commit, the total cost, and — for a baseline run — a
   banner saying that a red result is the expected one.
2. **The stated blind spots**, every run, not buried: the register is **not scored** and no metric
   represents it — read `register.html` instead; whether an option list leads is not scored either;
   wording is free. The phrase mapping is **no longer** among them: `founderPhrase` is on the wire
   and is a scored field.
3. **The reading section** — accuracy, `GUESSED` precision and recall, the confusion matrix overall
   and per entry, and every disagreement as a row: the anchor prompt, the person's words, the golden
   word, the model's word.
4. **The assumption section**, per entry per stage per run — the **diff**: golden beliefs down one
   side, produced beliefs down the other, matched pairs joined with a tick or a cross per field
   (`type`, `kind`, `unit`, expected-or-band, `risk`, `mark`, `founderPhrase`) and with the golden
   phrase-and-band shown beside the produced phrase-and-band, unmatched goldens marked *missing*,
   extras marked *extra*, pairs the judge decided marked as such, and the aggregate's refusal quoted
   in its own words with its rule id. Where the set was accepted, the produced bucket labels beside
   the corpus's own.
5. **The spread** — per case, each of the N runs' numbers side by side, so an unstable instruction
   reads as unstable rather than as an average.
6. **`NEEDS_INPUT` outcomes**, listed by case with the question the model asked — each one a failed
   case under decision 14, shown so the failure can be read rather than only counted.
7. **The prompts** — collapsed, one per case, the full text as sent.
8. **A link to `register.html`**, with the sentence that nothing on it is scored.

## `register.html`

One section per market in the run — the market's `country`, `region` and `language` at the head, then
every produced anchor prompt and every produced option list for that market, grouped by entry and
stage, with the corpus's own anchor for the same stage shown beside it for reference. No score, no
tick, no cross. It exists so a person who knows that market can read what a stranger there would have
been asked, and their reading is recorded with the run (design §10 step 4).

## What the bundle must make possible

- **Attribution.** Any number in the report traces to a prompt and an envelope on disk. Nothing is
  reported that cannot be opened — and anything that cannot be a number is rendered instead, on
  `register.html`, rather than left out.
- **Re-reading.** `scorecard.json` and `cases/**/diff.json` are enough to regenerate `report.html`
  without calling a model again, the way `make report RUN=…` already rebuilds a scenario report.
- **Comparison, honestly.** A run says its `MARKS_VERSION`, its model and its keel-cloud commit, so
  two runs can be compared when they should be and refuse to be when they should not.
- **A DRIFT entry.** Every finding that belongs in `runs/DRIFT.md` can name this bundle and quote
  from it, which is what the seven-part format requires.
