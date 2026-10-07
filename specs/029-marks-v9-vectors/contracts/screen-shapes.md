# Screen shapes at v9 — what the eval builds, sends, validates and diffs

Derived from `instruction-table.v1.draft.md` §B (the table) and §C (per-instruction rules and
refusal ids), `openapi-v2-vectors.draft.yaml` (the response objects), `marks-v9.md` §1/§4/§6 and
`phase0-reconciliation.md` §B. **The export is the contract**: every key list below is the order
`context-keys.json` will give, and the eval builds in that order (`context.py`'s rule since spec
009). Where keel-cloud 058 exports something different, 058 wins and this page is corrected.

## 1. Case ids, kinds and needles (FR-016, research R6)

```text
<entry>/CONTEXT_INTERPRET/run<N>          kind CONTEXT      class context      scored: no
<entry>/PROBLEM_INTERPRET/run<N>          kind FRAME        class frame        scored: no
<entry>/SOLUTION_MECHANISM/run<N>         kind FRAME        class frame        scored: no
<entry>/CALIBRATION_PROBLEM/run<N>        kind CALIBRATION  class calibration  dimension_coverage, option_validity, no_leak (sweep A)
<entry>/CALIBRATION_SOLUTION/run<N>       kind CALIBRATION  class calibration  dimension_coverage, option_validity
<entry>/CALIBRATION_COMMERCIAL/run<N>     kind CALIBRATION  class calibration  dimension_coverage, option_validity
<entry>/RESPONDENT_PART1/run<N>           kind RESPONDENT   class respondent   coverage, validity, no_leak (sweeps A and B)
<entry>/RESPONDENT_PART2/run<N>           kind RESPONDENT   class respondent   coverage, validity, no_leak (sweep B)
<entry>/RESPONDENT_PART3/run<N>           kind RESPONDENT   class respondent   coverage, validity, no_leak (sweep B)
<entry>/RESPONDENT_B2B/run<N>             kind RESPONDENT   class respondent   (B2B entry only) same three
<entry>/INTERPRET/<person>/run<N>         kind READING      class reading      anchoring_accuracy   (gate-yes, un-chipped, story non-empty)
<entry>/COMPARE                           kind COMPARE      —                  compare_correctness  (no call, no run index)
<entry>/BRIEF/run<N>                      kind BRIEF        class brief        brief_paragraphs (five per-case marks)
```

`-k` = case-insensitive substring of the id, or one of the kind words `context`, `frame`,
`calibration`, `respondent`, `reading`, `compare`, `brief`. The slash makes `03-lullaby/INTERPRET`
select the reads and not the interpretations. At N=1 on `03-lullaby` r3: 19 model cases + the
`COMPARE` row; at N=3: 57.

## 2. Context keys per screen (instruction-table §B; the exporter's order governs)

| Screen | Context keys the builder fills (from r3 + registry only) | Must NOT carry |
|---|---|---|
| `CONTEXT_INTERPRET` | `context_fields` {who, what, when, which_people} ← `context.{actor, job, circumstance, segment}`; `market`; `project_name` ← `title` | anything from `solution_mechanism` |
| `PROBLEM_INTERPRET` | `input.content` ← `statements.problem` (verbatim seed); `context` {actor, actor_plural, job, circumstance, segment}; `market`; `interaction_history: []` | a solution field |
| `SOLUTION_MECHANISM` | `input.content` ← `statements.solution`; `context`; `problem.statement` ← `interpretations.problem`; `market`; `interaction_history: []` | — |
| `CALIBRATION_QUESTIONS` | `vector`; `context`; `market`; the vector's interpretation (`problem.statement` ← `interpretations.problem` · `mechanism` ← `solution_mechanism` · `persona`); `dimensions[]` ← registry slice with exactly `key, order, name, meaning, weight, founder.control, founder.guidance, founder.normalized, founder.option_rule, founder.belief_template, founder.unsure_allowed, respondent.anchor, respondent.guidance` | **the PROBLEM job: no solution field at all** (US2.1) |
| `RESPONDENT_QUESTIONS` | `part`; `link` (PRIMARY \| COMMERCIAL_B2B); `context`; `market`; `founder_name`; `items[]` ← plan keys × registry `key, order, name, respondent.anchor, respondent.control, respondent.guidance, respondent.option_rule, respondent.chips, respondent.b2b?`; `founder_options` (labels only, for distractor sets); `mechanism` ← `solution_mechanism` **on parts 2 and 3 only** | the founder's answers, ever; `mechanism` on part 1; a context card or reveal on the B2B link |
| `INTERPRET` | `invitation_id` ← `<entry>/<person>`; `story` {prompt, text ← `answers[].story`, chip ← `null`} | a `stage`, an `anchors[]` list, a chipped or empty story (no case is built) |
| `BRIEF` | `project_name`; `market`; `context`; `vectors[]` ← {vector, verdict ← `expected.vector_verdicts[v].verdict`, dimensions[] ← {key, name, weight, status, belief_sentence ← `founder_calibration[k].belief_sentence`, founder_phrase ← `belief_phrase`, observed, inside, outside, below, above, drift, n_anchored, n_guessed} ← `expected.standings[k]` + registry} | a `claims` list, a `stage` |

## 3. Response shapes the validator and the scorers see (OpenAPI draft; the result object only)

```text
CONTEXT_INTERPRET   result: {understands, actor, actor_plural, job, circumstance, segment}      | NEEDS_INPUT ×1
PROBLEM_INTERPRET   result: {statement}  (≤ 600 chars)                                           | NEEDS_INPUT ×1
SOLUTION_MECHANISM  result: {actor, trigger, mechanism, output, not_assumed: [..], mechanism_terms: [3..8]} | NEEDS_INPUT ×1
CALIBRATION_QUESTIONS
                    result: {vector, questions: [{key, question, options: [{label, normalized, belief_phrase}] | null, respondent_note}]}
                    — no ids, no control, no template, no numeric spec (all registry)
RESPONDENT_QUESTIONS
                    result: {part, link, items: [{key, question, options: [label..] | null}], reveal?: {title, body}}
                    — no ids, no control, no chips, no "Something else" (code appends it); reveal on part 2 only
INTERPRET           result: {invitationId, anchoring: ANCHORED|GUESSED, unprompted: [..], flags: [..]}
BRIEF               result: {whatThisSays}  (≤ 2 000 chars; one paragraph per project)
COMPARE             no envelope: compare/<entry>.out.json (§5)
```

A result outside its JSON schema is a **shape refusal** (`RESULT_INVALID`, mark `shape_refusals`,
absolute zero). A second `NEEDS_INPUT` on an interpretation screen is a **rule refusal** (`X3` /
`P3` / `M3`), counted in `rule_refusal_rate`, rendered as refused. An `anchoring` outside the two
words is a shape refusal counted at zero (Edge Cases).

## 4. Rule ids per template (instruction-table §C) — the aggregate's, read by `fold_in`

| Template (keel-cloud spec) | Screen | Rule refusal ids | Shape |
|---|---|---|---|
| `context-interpret.md` (059) | `CONTEXT_INTERPRET` | `X1` product word in `understands` or a slot · `X3` second `NEEDS_INPUT` | `X2` a slot empty |
| `problem-interpret.md` (060) | `PROBLEM_INTERPRET` | `P1` product/mechanism word · `P2` a digit or number word · `P3` second `NEEDS_INPUT` | length |
| `solution-mechanism.md` (061) | `SOLUTION_MECHANISM` | `M1` claim word in the four fields · `M2` `not_assumed` empty while the seed claims · `M3` second `NEEDS_INPUT` | empty field; `mechanism_terms` outside 3–8 |
| `calibration-questions.md` (062) | `CALIBRATION_QUESTIONS` | `C1` keys ≠ slice or out of order · `C2` option count ≠ codes / outside 4–6 · `C3` a not-sure label · `C4` `belief_phrase` = label · `C5` product/mechanism word in a PROBLEM question · `C6` claim word in a SOLUTION question · `C7` 7-night window missing on `problem.prevalence` | empty `belief_phrase`; missing `respondent_note`; `options` on a numeric control |
| `respondent-questions.md` (063) | `RESPONDENT_QUESTIONS` | `R1` keys ≠ plan · `R2` option count / distractors · `R3` a founder value · `R4` mechanism/product word in part 1 or the intro · `R5` a habitual word · `R6` claim word or foreign number in `reveal.body` · `R7` a not-sure option · `R8` 7-night window missing on the gate | missing `reveal` on part 2; missing item fields; lengths |
| `interpret.md` (064, in place) | `INTERPRET` | `I1` `invitationId` ≠ context | `anchoring` not one of two words |
| `brief.md` (065, in place) | `BRIEF` | today's four checks · `B5` claim word when any dimension is `BAR_SET` | length (2 000), labels, links |

`option_validity`, `dimension_coverage` and `no_leak` are **this repository's code** against the
registry and the corpus (marks §2.1–§2.3) and are measured whether or not the aggregate takes the
kind; only `rule_refusal_rate` and `shape_refusals` depend on keel-cloud's validator knowing it
(research R10).

## 5. `compare.py` ⇄ keel-cloud 058 — the two files (research R3)

```text
$ ./gradlew -q screenContracts --args="compare <in.json> <out.json>"      # exit 0; non-zero = unmeasured by name

in.json  (built from r3 and the registry version only; one per entry)
{
  "entry": "03-lullaby", "market": {...}, "registry_version": <int>,
  "persona": {"decision_maker": "same_person" | {"role": "<id>"}},
  "founder_calibration": { "<key>": {"answer": ...} | {"unsure": true}, ... 25 },
  "answers": [ {"person": "...", "recency": "yes"|"no", "anchoring": "ANCHORED"|"GUESSED"|null,
                "picks": { "<key>": <value per respondent.control, incl. rough and chip> }} ]
}

out.json (the engine's; the eval reads, diffs, keeps in the bundle)
{
  "standings": { "<key>": {"status": <Status>, "drift": "above"|"below"|"both"|"none"|null,
                           "n": int, "inside"?, "outside"?, "median"?, "proportion"?,
                           "optionCounts"?: "<option>=<count>, ...", "bar"?, "belief_sentence": "..."} , ... 25 },
  "vector_verdicts": { "PROBLEM": {"verdict": <Status>, "deciding": "<key>"}, "SOLUTION": ..., "COMMERCIAL": ... }
}
```

**Marked** (call 34): `status` and `drift` per dimension (25), `verdict` and `deciding` per vector
(3) → 28 checks on one entry, 196 on seven. **Reported, never marked** (call 3): `n`, `inside`,
`outside`, `median`, `proportion`, `optionCounts`, `bar`, `belief_sentence`. Lullaby's expected
row, signed 2026-10-07 (FR-007): `problem.prevalence` `HOLDING_UP`/`above` (10 of 12, 0.83);
`problem.duration` `NOT_HOLDING_UP`/`below` (median 11, n 7); `problem.severity`
`PEOPLE_DISAGREE`; `problem.current_solution_satisfaction` `NOT_HOLDING_UP`/`above`;
`problem.importance` `HOLDING_UP` (share 0.38 in `top_three`); `problem.urgency` and
`commercial.retention_potential` `LEFT_OUT`; `solution.effectiveness_threshold` `BAR_SET`;
`commercial.wtp_hypothesis` `NOT_TESTED_BY_DESIGN`; totals 12 / 6 / 3 / 1 / 1 / 2; verdicts all
`NOT_HOLDING_UP` deciding `problem.duration`, `solution.compatibility`, `commercial.commitment`.

## 6. The batch `validate.build_batch` hands the aggregate (research R10)

```text
{"cases": [
  {"case_id", "screen": "CONTEXT_INTERPRET",     "market", "context_fields", "result"},
  {"case_id", "screen": "PROBLEM_INTERPRET",     "market", "context", "seed", "result"},
  {"case_id", "screen": "SOLUTION_MECHANISM",    "market", "context", "problem_statement", "seed", "result"},
  {"case_id", "screen": "CALIBRATION_QUESTIONS", "market", "vector", "context", "registry_slice": [keys in order], "result"},
  {"case_id", "screen": "RESPONDENT_QUESTIONS",  "market", "part", "link", "plan": [keys], "founder_options", "founder_values": {...}, "result"},
  {"case_id", "screen": "INTERPRET",             "invitation_id", "story", "result"},
  {"case_id", "screen": "BRIEF",                 "market", "standings", "result"}
]}
```

`founder_values` travels on a respondent case because `R3` is checked against the stored labels
and numbers the model was never shown — the validator needs the state the screen would really have
arrived into (025 D12/D18). A kind the validator does not take → `unmet_prerequisites` names it and
`rule_refusal_rate`/`shape_refusals` are **unmeasured** for that kind's cases.

## 7. `register.html` blocks per entry (FR-022; no score, no tick, no cross)

1. The three interpretations, verbatim, each marked *accepted* / *refused (rule id)* by the
   aggregate — the only words the register adds.
2. The 25 calibration questions in registry order, each beside the registry's
   `lullaby.founder_question` where one exists, the founder's answer (`belief_phrase`) and the
   belief sentence (`belief_sentence`).
3. The 23 (+ B2B) respondent items beside the plan row (`key · part · control · codes`), the
   reveal's title and body between parts 1 and 2.
4. The brief paragraph beside the standings table: `dimension · status · drift · n ·
   median/counts`, with `vector_verdicts` as three header rows.
