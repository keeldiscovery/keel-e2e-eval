# Data model: what the eval reads, builds and writes

Four shapes. Two are read (keel-cloud's corpus, keel-cloud's exported contract), one is built (a
case, and its prompt), one is written (the run bundle). Nothing here is a domain model; it is the
vocabulary the modules share.

---

## 1. The corpus entry — read, never written

One `canon/designs/measured-beliefs/corpus/NN-name.yaml` from the keel-cloud checkout, loaded by
`instructions/corpus.py` and hashed on the way in.

```
Entry
  id           str                     "01-countly"
  title        str
  market       Market                  {country, region|None, language}
  statements   {stage → str}           PROBLEM / SOLUTION / COMMERCIAL, the framed statements
  roles        [Role]                  {id, label, roleType, about, market?}
  beliefs      [GoldenBelief]
  questionnaire  {anchors: [GoldenAnchor]}
  answers      [Person]
  expected     {buckets, standings, stages}   read for the bucket diff only
```

```
GoldenBelief
  id            str            "P4a"        — corpus-local, not the aggregate's
  stage         PROBLEM|SOLUTION|COMMERCIAL
  heading       str
  statement     str
  founderPhrase str            the §8.3 phrase this band came from — see the note below
  risk          LOAD_BEARING|SUPPORTING
  askedOf       str            a role id in `roles`
  mark          DIRECT|PROXY
  expectation   Interval{measure{kind,unit,per}, lower?, upper?} | Choice{options, expected}
  selection     str            a selection id on the questionnaire
  group         str?           present where two beliefs share a selection
```

```
GoldenAnchor  {id, stage, prompt, taps: [str], selections: [GoldenSelection]}
GoldenSelection {id, prompt, control: BUCKETS|OPTIONS, multiSelect?, options?, other?, escape}
Person        {person, anchors: {anchorId → {text, tap?, anchoring: ANCHORED|GUESSED}}, picks}
```

**Three notes the harness must carry**:

1. **`founderPhrase` is comparable.** keel-cloud spec 029 puts it on the wire beside the band
   (design §8.1 step 4), so the corpus's own `founderPhrase` has something to be compared with. It is
   a scored exact-match field, and a matched pair's phrase and band are reported together — a right
   band from a wrong phrase is a different fault from a right phrase mapped to a wrong band.
2. **`taps` are English here and enum names on the wire.** The corpus writes *hasn't happened*; the
   contract wants `HASNT_HAPPENED`. The mapping belongs to `context.py` and is one table.
3. **Anchors carry a `stage`; the aggregate's questionnaire does not.** A corpus questionnaire is the
   whole project's; a screen emits one stage's. So a stage's expected questionnaire is the anchors
   whose `stage` matches, and their selections.

---

## 2. The exported contract — read, never written

Produced into `<run>/contracts/` by keel-cloud's exporter and consumed exactly as
`specs/029-measured-beliefs-instructions/contracts/exported-contract-format.md` defines it:

```
contracts/<SCREEN>.json   {allowed_outcomes, completed_result_schema, needs_input_schema?}
context-keys.json         {"<SCREEN>": ["key", …]}      ordered — the order is the contract
manifest.json             {generated_at, keel_cloud_commit, keel_cloud_dirty, screens}
```

`needs_input_schema` is absent for `INTERPRET` and present elsewhere. The whole
`contracts/<SCREEN>.json` object goes into `request_payload["response_contract"]` unmodified.

---

## 3. A case — built here

```
Case
  case_id    str      "01-countly/PROBLEM/run2"  or  "01-countly/Priya Natarajan/run1"
  kind       ASSUMPTIONS | READING
  entry_id   str
  screen     str      PROBLEM_ASSUMPTIONS | … | INTERPRET
  subject    str      the stage, or the person
  run_index  int      1..N
  payload    dict     what production would have sent
  prompt     str      keel_runtime.executor.build_prompt(payload)
```

### `payload` — production's shape, exactly

```json
{ "instruction": "<the stripped instruction bytes>",
  "context": { "<key>": <value>, … },
  "interaction_history": [],
  "input": {"content": ""},
  "response_contract": { … } }
```

- `instruction` — the file at `<keel-cloud>/src/main/resources/keel/inference-instructions/<stem>.md`,
  `.strip()`ed, because `InferenceInstructionRegistry.get` returns `section.strip()`.
- `interaction_history` — `[]`: this is always turn one.
- `input.content` — `""`: the empty-string sentinel an auto screen carries, which is what
  `InferenceOrchestrator.start` passes for a screen with nothing founder-typed.
- `context` — every key `context-keys.json` names for the screen, in that order, `null` where there
  is no value.

### Filling an assumptions context

| Key | From |
|---|---|
| `problem_statement` / `solution_statement` / `commercial_statement` | `entry.statements[stage]` |
| the upstream statements | the same, for the earlier stages |
| `market` | `entry.market` |
| `existing_roles` | `[]` for PROBLEM; for SOLUTION the roles PROBLEM's beliefs are `askedOf`; for COMMERCIAL those plus SOLUTION's (research.md R5a) — each `{id, label, roleType, about, market?}`, and the set supplied is recorded per case |

### Filling a reading context

| Key | From |
|---|---|
| `invitation_id` | a stable synthetic id per person: `"<entry_id>/<person>"` |
| `anchors` | one `{anchor_id, prompt, text, tap}` per anchor the person wrote text under — **a blank anchor is omitted**, as `ScreenContextBuilder.anchorsWritten` omits it; `prompt` from the corpus's questionnaire; `tap` mapped to its enum name |

---

## 4. An answer, and its alignment

```
Answer   {case_id, envelope, outcome, result|None, schema_valid, schema_error|None,
          recovery_pass: bool, num_turns, total_cost_usd, duration_s}
```

```
Alignment                      per assumptions case
  matched   [Pair]             {golden_id, produced_index, score, by: "structure"|"judge",
                                fields: {type, kind, unit, expected_or_band, risk, mark, founder_phrase → bool}}
  missing   [golden_id]        golden beliefs no produced belief reached
  extra     [produced_index]   produced beliefs no golden explains
  judged    int                how many pairs a model decided
```

**The candidate rule** (deterministic, unit-tested):

| Expectation | Candidate when |
|---|---|
| `INTERVAL` | same stage, same `measure.kind`, and the bands intersect (an absent bound is infinite) |
| `CHOICE` | same stage, and either the normalised `expected` strings are equal, or the option sets overlap above the stated threshold |

Pair score is the count of agreeing fields among the six, plus a small tie-break on heading
similarity. Matching is greedy over descending score, ties broken by golden id order, so the same
inputs always give the same alignment.

**Ambiguity, and only then the judge**: two or more goldens tied at the top score for one produced
belief, or a produced belief with no candidate at all. The judge sees the two statements and answers
*this one* / *that one* / *no match*, and its answer is recorded with the pair.

```
Reading                        per reading case
  per_anchor [{anchor_id, golden: ANCHORED|GUESSED, produced: ANCHORED|GUESSED|None, agree: bool}]
  missing_ids [str]            an anchor the model failed to answer — a failure, not an alignment
  extra_ids   [str]            an anchor id the model invented
```

---

## 5. The scorecard

```
Scorecard
  marks_version int
  marks         {anchoring_accuracy, golden_belief_recall, refusals}
  model         {claude_version, reported_model|None, jsonschema_installed: bool}
  n_runs        int
  cases         [CaseScore]
  totals        Totals
```

```
CaseScore (ASSUMPTIONS)
  golden_belief_recall     matched / golden
  exact_match              {type, kind, unit, expected_or_band, risk, mark, founder_phrase}
                           → rate over matched, per field
  needs_input              bool    an ask with a statement present: a failed case (decision 14)
  extra_beliefs            int
  aggregate                {accepted: bool, refusal: {kind, rule, path, message}|None}
  buckets                  {selectionId → [label]}   present only when accepted
  judged_fraction          judged / matched

CaseScore (READING)
  anchoring_accuracy       agree / answered
  guessed_precision        of the anchors called GUESSED, how many were
  guessed_recall           of the anchors that were GUESSED, how many were called so
  confusion                {aa, ag, ga, gg}
```

```
Totals
  anchoring_accuracy, guessed_precision, guessed_recall
  golden_belief_recall, exact_match{…}, extra_beliefs
  refusals_by_rule  {"E4": 2, "Q5": 1, …}      the number the marks read
  errored           int                        ExecutorUnavailable/Timeout — not a score
  spread            per case, the min/max across the N runs
```

`refusals` is a count over rule refusals only; a shape refusal is reported apart, because a result
that did not fit the contract never reached the aggregate at all.

---

## 6. The run bundle

Specified in [contracts/run-bundle-contract.md](./contracts/run-bundle-contract.md). In summary:

```
runs/<ts>-instructions[-baseline]/
├── versions.json          the five sibling commits (harness.evidence.write_versions)
├── verdict.json           {passed, marks, marks_version, model, n_runs, cases, errored,
│                           duration_s, total_cost_usd}
├── scorecard.json         §5
├── corpus.sha256          every corpus file, hashed before and after
├── contracts/             keel-cloud's export, as used
├── validation.json        the aggregate's report for the whole batch
├── cases/<entry>/<subject>/<run>/{prompt.txt, envelope.json, diff.json}
├── jobs/                  ClaudeCodeExecutor's own home for this run
└── report.html            self-contained
```
