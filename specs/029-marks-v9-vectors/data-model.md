# Data model: marks v9, corpus revision 3, and the run that certifies the vectors

**Branch**: `029-marks-v9-vectors` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

Phase 1 of the plan. The entities the spec names under *Key Entities*, as the code will hold them,
with the validation rules the loader and the scorers enforce and the states a bundle moves through.
Field names are `registry-schema.draft.md`'s and marks §4's; where a field is this repository's
own it says so. Nothing here is a copy of the cloud's arithmetic — every rule below is either a
refusal to start, a shape check, or a diff against a golden the corpus or the registry carries.

## 1. `Registry` and `Dimension` (`instructions/registry.py`, read from the export)

The 25-dimension export keel-cloud 058 writes as `dimension-registry.json`; the golden for
`dimension_coverage` and `option_validity`; the source of every control, code, bin, template and
compare rule. Design-time copy: [contracts/dimension-registry.yaml](contracts/dimension-registry.yaml).

```text
Registry
  version: int                       # the export's; recorded in the bundle manifest
  common: {left_out, chips, something_else, floor, context_placeholders, drift_placeholders, compare_rules}
  dimensions: [Dimension × 25]       # in file order == vector order == `order` within vector
  slice(vector) -> [Dimension]       # the calibration job's input, in `order`
  by_key(key) -> Dimension
  plan_keys(part, founder_calibration) -> [key]    # asked_in_v1 ∧ not unsure, in order
  fixed_respondent_codes(key) -> [code]            # own_instinct / not_useful / nothing_yet where added

Dimension
  key: str                 # "problem.prevalence" …; dotted vector.snake_case
  vector: PROBLEM | SOLUTION | COMMERCIAL
  order: int               # 1-based within the vector
  name, meaning: str
  weight: DEAL_BREAKER | SHAPES
  founder: {control, guidance, normalized: {kind, codes? | code_rule? | unit_options, default_unit,
            axis_max, axis_step, extend_by, bins?}, option_rule, belief_template, unsure_allowed}
  respondent: {asked_in_v1, part: 1|2|3|null, anchor, control, guidance, option_rule, chips, b2b?}
  answers: {shape: interval|choice, compare_rule, status_vocabulary: [Status], drift_template, floor}
  left_out?: {ask_respondent, status, note}
  lullaby?: {…}            # the worked example; rendered on the register, read by no scorer
```

**Invariants checked on load** (`registry.check_invariants`, each a refusal naming the invariant):

1. 25 keys, 9 / 9 / 7, `order` contiguous from 1 within each vector.
2. Deal-breakers exactly the nine of `registry-schema` §Invariants 2.
3. `respondent.asked_in_v1` true on exactly 23; parts 1/2/3 = 8/9/6.
4. Every `founder.belief_template` contains `{value}` exactly once.
5. Every fixed `founder.normalized.codes` list has 4–6 codes, none repeated; numeric `bins`
   contiguous and ordered.
6. `answers.shape == interval` iff `respondent.control` ∈ {`segmented_0_to_7`, `number_with_unit`,
   `single_choice_bands`, `two_numbers_optional`}.
7. `problem.prevalence.respondent.control == gate_yes_no` and no other dimension's is.

## 2. `Entry` and `Person` at revision 3 (`instructions/corpus.py`)

One hand-worked project, read-only, hashed (`sha256`, `Corpus.verify_unchanged()` **unchanged**).

```text
Entry
  id, title: str                     # unchanged
  revision: int                      # MUST be 3
  market: {country, region, language}
  statements: {problem, solution, commercial}      # the seeds, verbatim
  roles: [{id, label, roleType, about, market?}]
  context: {actor, actor_plural, job, circumstance, segment, understood}
  interpretations: {problem: str}    # the golden PROBLEM_INTERPRET sentence (research R16; r3 writer)
  solution_mechanism: {actor, trigger, mechanism, output, not_assumed: [str], mechanism_terms: [str]}
  persona: {decision_maker: "same_person" | {role: <roles[].id>}}
  founder_calibration: {<key>: {answer, belief_phrase, belief_sentence} | {unsure: true}}   # 25 keys
  respondent_questions: {<key>: {part, control, codes?}}       # the golden plan; no text
  answers: [Person]
  expected: {standings: {<key>: Standing}, vector_verdicts: {<vector>: {verdict, deciding}}}
  path, sha256                       # unchanged

  plan() -> {1: [key], 2: [key], 3: [key]}        # from founder_calibration × registry (call 30)
  vocabulary() -> set[str]                        # mechanism stems − problem-world stems (call 32)
  mechanism_one_liner() -> str                    # the judge's clause, from solution_mechanism
  people() -> [Person]
  gate_yes() -> [Person]                          # recency == yes
  readable() -> [Person]                          # gate_yes ∧ chip is None ∧ story non-empty
  b2b() -> bool                                   # persona.decision_maker is a role

Person
  person: str
  recency: "yes" | "no"
  story: str | None                  # absent when recency == no
  chip: None | "cant_recall" | "rather_not_say"
  anchoring: ANCHORED | GUESSED | None            # golden; None when recency == no
  picks: {<key>: code | int | {value, unit, rough} | [codes] | {band, unit} | {bought, cost, still_using} | {last_paid, guess} | {chip}}
  pilot_opt_in: bool
```

**Refusals to start** (`CorpusError`, by entry and key, never a fallback):

- `revision` absent or `!= 3`.
- Any of `beliefs`, `questionnaire`, `expected.buckets`, `expected.stages` present; any
  `answers[].anchors`.
- `founder_calibration` not exactly the registry's 25 keys; an entry carrying neither `answer`
  nor `unsure: true`.
- A `picks` key, a `respondent_questions` key or an `expected.standings` key outside the registry.
- A `recency: no` person carrying a `story`, a `chip`, an `anchoring` or any `picks`; a
  chip-carrying person whose `anchoring` is not `GUESSED`.
- `persona.decision_maker` a role id not in `roles`.
- `expected.standings[key].status` outside `Status`; `vector_verdicts[v].deciding` not a
  `DEAL_BREAKER` of `v`.

**Derived rules.** `plan()` = for each part, the registry's keys with `asked_in_v1` and
`respondent.part == part` whose `founder_calibration` entry is not `unsure`, in `order`; on
Lullaby `{1: 8, 2: 9, 3: 6}`. `vocabulary()` = `text.stems` of `solution_mechanism.{actor,
trigger, mechanism, output}` and `not_assumed[]` and `mechanism_terms[]`, minus `text.STOPLIST`,
minus every stem of `context.*`, `statements.problem`, `interpretations.problem` and every
`answers[].story` (the problem's own words). The **inflection ledger** — a stem excluded only
because its problem-world form differs by inflection — is kept beside, because that is the tie
`no_leak` sends to the judge (FR-015).

## 3. `Plan` (derived, `Entry.plan()`)

The respondent items by part. Not stored; derived by code and compared with the file's own
`respondent_questions` keys per part — a mismatch is a corpus refusal (the file disagrees with the
registry it is keyed by). It is what `build_respondent(entry, part, plan)` hands each job and the
denominator of `dimension_coverage` on the respondent side (FR-013).

## 4. `Screen` (`instructions/contract.py` constants + `prompts.build_cases`)

Eight subjects at v9. One row each, fixed:

| Constant | Kind (`Case.kind`) | Class | Builder (`context.py`) | Scorer | Needle |
|---|---|---|---|---|---|
| `CONTEXT_INTERPRET` | `CONTEXT` | `context` | `build_context_interpret` | — (rate, shape, register) | `context` |
| `PROBLEM_INTERPRET` | `FRAME` | `frame` | `build_problem_interpret` | — | `frame` |
| `SOLUTION_MECHANISM` | `FRAME` | `frame` | `build_solution_mechanism` | — | `frame` |
| `CALIBRATION_QUESTIONS` | `CALIBRATION` | `calibration` | `build_calibration(entry, vector, registry)` | `score_calibration` | `calibration` |
| `RESPONDENT_QUESTIONS` | `RESPONDENT` | `respondent` | `build_respondent(entry, part, plan)` | `score_respondent` | `respondent` |
| `INTERPRET` | `READING` | `reading` | `build_interpret(entry, person)` | `score_interpret` | `reading` |
| `COMPARE` | `COMPARE` | — | `compare.build_input` | `score_compare` | `compare` |
| `BRIEF` | `BRIEF` | `brief` | `build_brief(entry, standings)` | `brief.score_brief` (five marks) | `brief` |

`Case` (`prompts.py`) keeps its fields; `subject` is the vector, the part, the person, `COMPARE`
or `BRIEF`; `COMPARE` carries `payload = {}` and `prompt = ""` and is never sent.

## 5. `Mark` and `JudgementCall` (`instructions/marks.py`, `marks.toml`)

```text
Mark          name, bar (from marks.toml), measured: bool, value, met: bool
              eight at v9: dimension_coverage 1.00 · option_validity 1.00 · no_leak 1.00 ·
              anchoring_accuracy 0.90 · compare_correctness 1.00 · rule_refusal_rate 0.02 ·
              shape_refusals 0 · brief_paragraphs 1.00
JudgementCall number (1–36), version tag, one sentence; append-only; 28–36 verbatim from marks §3
```

`marks.judge(totals, marks) -> {<mark>: {value, mark, measured, met}, passed}`; **unmeasured is
not met** (call 13) on every row.

## 6. `Scorecard`, `Verdict`, `Bundle` (`instructions/run.py`, `report.py`)

```text
Bundle  runs/<stamp>-instructions[-<host>]/
  manifest.json      {why, host, models, effort.per_class, marks_version: 9, corpus_digests,
                      registry_version, keel_cloud_commit, started_at, …}
  corpus.sha256      before and after (unchanged mechanism)
  contracts/         the export, copied whole (now incl. dimension-registry.json)
  cases/<entry>/<subject>/<runN>/{prompt.txt, envelope.json, …}
  compare/<entry>.{in,out}.json      # NEW: the engine's input and output, kept
  validation.json    the aggregate's report, or "unavailable: <reason>"
  scorecard.json     per-case evidence + totals + spread (below)
  verdict.json       marks.judge() + models_used + efforts_used + unmet_prerequisites
  report.html, register.html

Scorecard.totals (v9 keys)
  calibration_cases, calibration_coverage {hit, of}, calibration_validity {hit, of}, calibration_leak {clean, of}
  respondent_cases, respondent_coverage {hit, of}, respondent_validity {hit, of}, respondent_leak {clean, of}
  dimension_coverage, option_validity, no_leak             # the rolled fractions
  leak_hits, leak_judged, judged_fraction, judge_calls
  anchoring_accuracy, guessed_precision, guessed_recall, confusion {aa, ag, ga, gg},
  people_given, people_answered, reading_missing_ids, reading_extra_ids, chipped_skipped
  compare_checks, compare_agreed, compare_correctness, compare_measured, compare_reported_diffs
  refusals_by_rule, refusals_measured, refusals_shown, shape_refusals, schema_invalid, errored
  brief_cases, brief_paragraphs, brief_measured, brief_by_mark {shape, coverage, register, source_material, no_claim_words}
Scorecard.spread  per case for coverage, validity, leak, anchoring, brief (call 7)
```

**State transitions of a bundle** (what a reader may conclude from it):

```text
dry        DRY=1: cases built, prompts printed, COMPARE measured, every model mark UNMEASURED → passed: false, by name
screen     -k on one entry, WHY=instruction:|prompt:|contract:|new-model: → the selected marks measured on one entry;
           every other entry's marks UNMEASURED → passed: false (a screen is never a run of record)
record     no -k, WHY=marks:9, MODELS=exported, all seven r3 entries → eight marks measured → passed: true|false
certified  the one `record` bundle green on all eight, named in README.md (the Certificate)
```

A mark's own states: `unmeasured` (no case reached its scorer, or a prerequisite is unmet by name)
→ `measured` (a value exists) → `met` (value within the bar). `unmeasured` never becomes `met`.

## 7. `Certificate`

The one `WHY=marks:9` bundle with `verdict.passed == true`, written into `README.md` as *the run of
record for spec 029 — `MARKS_VERSION` 9, Claude* with its time, price, case count and the eight
values, beside the v8 record (414 cases, 3 h 11 m, $15.41). It is what keel-cloud's routing v9
spec reads; nothing in this repository changes `model-routing.json`.

## 8. Relationships, in one line each

- A `Registry` has 25 `Dimension`s; an `Entry` is keyed by them (calibration, plan, picks,
  standings) and refuses a key outside them.
- An `Entry` has 1 `COMPARE` row, 3 calibration jobs, 3 (+1 B2B) respondent jobs, 3
  interpretations, 1 brief, and one `INTERPRET` case per `readable()` person.
- A `Screen` is scored by at most one scorer; three screens are scored by none and feed the rate.
- A `Bundle` carries exactly one `marks_version` for ever; `rescore.py` reads it first.
