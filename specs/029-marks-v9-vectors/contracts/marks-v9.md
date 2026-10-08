# Marks v9 — the instruction screen's rubric for the vector redesign (Phase 0.3, draft 2026-10-06)

Written before any prompt or corpus work (HANDOFF §4 track D); the marks never move to fit a model. Product ceiling: `claude-sonnet-5-5` at `medium`; §2 says of each mark why it is reachable there. Companion file: `marks-v9.draft.toml`, the exact `keel-e2e-eval/instructions/marks.toml` at `MARKS_VERSION` 9. Registry field names are those of `registry-schema.draft.md`; screen names are the instruction table's (`instruction-table.v1.draft.md` §B): five new constants plus today's `INTERPRET` (design name "anchor read", narrowed to the gate story) and `BRIEF`; there is no `ANCHOR_READ` constant. The Lullaby worked example is owned by the registry's `lullaby` objects (§5 re-expresses them).

## 1. What a run is, at v9

| Screen (enum) | Calls per entry (N=1) | Scored by | Golden in corpus r3 |
|---|---|---|---|
| `CONTEXT_INTERPRET`, `PROBLEM_INTERPRET`, `SOLUTION_MECHANISM` | 1 + 1 + 1 | nothing — rendered on `register.html`, judged by the aggregate for `rule_refusal_rate` (judgement call 10) | downstream screens get the corpus's own `context` / `solution_mechanism`, never the live output |
| `CALIBRATION_QUESTIONS` | 3 (one per `Vector`) | `dimension_coverage`, `option_validity`, `no_leak` (PROBLEM vector) | the registry slice; no question text |
| `RESPONDENT_QUESTIONS` | 3 (one per `Part`) | `dimension_coverage`, `option_validity`, `no_leak` | `respondent_questions` (plan: part, control, codes) |
| `INTERPRET` (design name "anchor read"; today's constant, narrowed) | one per respondent who passed the gate and did not chip (9 on Lullaby; a chipped story is `GUESSED` by code, no call — decided 2026-10-07) | `anchoring_accuracy` | `answers[].anchoring` |
| `COMPARE` | 0 — code, keel-cloud's engine shelled | `compare_correctness` | `expected.standings`, `expected.vector_verdicts` |
| `BRIEF` | 1 | `brief_paragraphs` (five per-case marks) | `expected.standings` as context |

Per entry at N=1 ≈ 20 model calls; the screen on `03-lullaby` at N=3 ≈ 60; the full run at N=3 ≈ 7 × 60 ≈ 420 calls, of which ~300 are `light`-tier anchor reads. Nothing is averaged before it is reported; the spread per case stays (call 7).

## 2. The marks

| Mark | Bar | Measured | Screens | Registry fields read | Golden (r3) | Lullaby numbers |
|---|---|---|---|---|---|---|
| `dimension_coverage` | 1.00 | code | `CALIBRATION_QUESTIONS`, `RESPONDENT_QUESTIONS` | `key`, `vector`, `order`, `respondent.asked_in_v1`, `respondent.part` | the registry; `founder_calibration` (which dimensions are `unsure`) | calibration 25/25; respondent 23/23 |
| `option_validity` | 1.00 | code | same two | `founder.control`, `founder.normalized` (`codes` / numeric spec), `founder.option_rule`, `founder.belief_template`, `respondent.control`, `respondent.option_rule`, `respondent.chips` | the registry; `respondent_questions[d].codes` | 48 questions, every check |
| `no_leak` | 1.00 | code list; judge for ties only | `CALIBRATION_QUESTIONS` (PROBLEM), `RESPONDENT_QUESTIONS` (Part 1 for mechanism; all parts for founder values) | `vector`, `respondent.part` | `solution_mechanism` → vocabulary; `founder_calibration[d].answer` + `belief_phrase` → values | 9 + 8 = 17 mechanism sweeps; 23 value sweeps |
| `anchoring_accuracy` | ≥ 0.90 | code; GUESSED precision + recall mandatory | `INTERPRET` (anchor read) | — | `answers[].anchoring` | 9 judgements (8 A / 1 G) at N=1; 27 at N=3 — Jonas's chipped story is `GUESSED` by code, outside |
| `compare_correctness` | 1.00 | code (engine shelled, zero spend, runs on `DRY=1`) | `COMPARE` | `answers.compare_rule`, `answers.status_vocabulary`, `answers.floor`, `weight`, `left_out` | `expected.standings[d].{status,drift}`, `expected.vector_verdicts` | 25 + 3 = 28 checks |
| `brief_paragraphs` | 1.00 | code (five per-case marks, all or nothing) | `BRIEF` | `name`, `weight`, `answers.status_vocabulary` | `expected.standings` (as the context sent) | 1 paragraph; 7 on the full run |
| `rule_refusal_rate` | ≤ 0.02 | the aggregate, by rule id | every model screen | — | — | ≈ 20 answers judged per entry |
| `shape_refusals` | 0 | the runtime | every model screen | — | — | — |
| `judged_fraction` | reported | — | `no_leak` | — | — | judge-decided hits / all hits |
| `golden_belief_recall` | **retired** | — | — | — | — | — |

### 2.1 `dimension_coverage`
Numerator: dimensions with exactly one question in the answer. Denominator: calibration = every `key` in the vector's slice (9 / 9 / 7 — a question is written before the founder can be unsure; `unsure` is a chip); respondent = `{d : respondent.asked_in_v1 ∧ founder_calibration[d] not unsure}`, in `respondent.part` groups. An extra question, a missing one, a doubled one or a dimension key outside the slice fails the case. **Lullaby caveat:** its two left-out dimensions (`problem.urgency`, `commercial.retention_potential`) are exactly the two not asked in V1, so 25 − 2 = 23 exercises the `asked_in_v1` subtraction and not the `unsure` one; another entry must leave out an asked dimension (decision 4).

### 2.2 `option_validity`
Per question, every check passes or the question fails; the mark is questions passed / questions written, bar 1.00. Checks, calibration side: control = `founder.control`; closed control with fixed codes (12 dimensions, registry `checks.5_codes`) → options count = `len(founder.normalized.codes)`, each option's `normalized` is a code, in registry order, none repeated; closed control with `founder.normalized.codes: model_written` (9 set / categorical dimensions) → 4–6 unique slug codes per `founder.normalized.code_rule`, each option's `normalized` one of them, the fixed codes the rule names (`none` on Existing sacrifice; the commitment ladder's rungs) present; numeric control → `founder.normalized.{unit_options, default_unit, axis_max, axis_step, extend_by, bins}` equal the registry's; every option carries `belief_phrase`, non-empty, at most 120 characters, no not-sure word (call 37, founder 2026-10-08, screen 20261008T001657Z: a phrase may equal its label; v9 amended before any run of record); `founder.belief_template` contains `{value}` exactly once and equals the registry's; no option whose label matches `/not sure|don't know|unsure/i`. Respondent side: control = `respondent.control`; set controls: every founder code present, the distractors `respondent.option_rule` names, the fixed respondent-only codes (`own_instinct`, `not_useful`, `nothing_yet`) where the registry adds them, "Something else" last per the registry's `common.something_else` rule; ordinal controls: the fixed scale, nothing added; numeric-as-bands: `founder.normalized.bins`, no founder number among the edges; `chips` = `respondent.chips`; `anchor` = `respondent.anchor`; Importance: the problem's own item never first (superseded by call 38, orchestrator 2026-10-08, bundle 20261008T013837Z: code appends, never the model -- 'Something else', every respondent-only code the registry names and every band, scale-axis and gate option -- so a fixed-code control or the ladder owes exactly one label per remaining plan code, a set every founder label (normalised) plus 2-3 distractors, Importance 4-6 difficulties, and a band, numeric or gate control options null; v9 amended before any run of record). All structural — the smoke's one real fault (non-contiguous bins) cannot recur because the codes are fixed, which is why 1.00 is honest at `medium`. (call 41, founder decision 35, 2026-10-08: scored on the ACCEPTED answer -- the answer after the runtime's rule refusal and ONE redraw, mirroring keel-cloud 058's orchestrator repair turn -- because that is what a founder sees; the same holds for `dimension_coverage` and `no_leak` on both question screens. A second refusal leaves the answer refused: it scores as faults on the raw answer and counts as a second refusal in §2.7.)

### 2.3 `no_leak`
Vocabulary: content words of `solution_mechanism.{actor,trigger,mechanism,output}` and `not_assumed[]`, stemmed, minus a stoplist, minus any stem that occurs in `context`, `statements.problem` or any `answers[].story`. Lullaby's list ≈ `app, listen, classif, card, suggest, record, microphone/mic, most-likely, next-most-likely` (~10 stems; `phone`, `cry`, `need`, `feed`, `nappy`, `wind` are the problem's own words and are excluded). Sweep A: those stems in a PROBLEM calibration question or a Part 1 respondent question (text + options). Sweep B: the founder's chosen label, `belief_phrase` or number for dimension *d* in respondent question *d* (any part). A hit = fault. **Tie:** a hit on a stem that was excluded only because its *inflection* differs from the problem-world form (e.g. `listens` vs a story's `listened`) goes to the judge with one closed question — *does this question tell a stranger what the proposed solution is: `<mechanism one-liner>`? SAME/DIFFERENT* — cached, recorded, counted in `judged_fraction`. Numerator: questions with no fault; denominator: questions swept. Lullaby: 17 + 23 = 40 sweeps; bar 1.00. (call 39, orchestrator 2026-10-08, bundle 20261008T013837Z: the vocabulary is stemmed from the golden mechanism's `mechanism`, `output`, `not_assumed` and `mechanism_terms` only, never `trigger` (it describes the problem moment) or `actor`, less the problem's own stems as before; v9 amended before any run of record; call 40, orchestrator 2026-10-08, bundle 20261008T024419Z: sweep B reads respondent item d's question stem and the part's reveal only, never its option labels -- a fixed-code control shows every rung, the founder's among them, and a set shows the founder's labels verbatim by R2, so a founder label in an option is the rule, not a leak; v9 amended before any run of record.)

### 2.4 `anchoring_accuracy`
`agree / answered` over respondents with `recency: yes` (gate-No respondents write no story and are never shown to the reader); confusion matrix, `guessed_precision`, `guessed_recall`, `missing_ids`, `extra_ids` keyed by person, as today. **A chipped story (`chip: cant_recall` / `rather_not_say`, or an empty story) is set `GUESSED` by code with no `INTERPRET` call and is OUTSIDE the denominator** (decided 2026-10-07, decision 10 below; call 33 amended) — its golden `GUESSED` is a corpus fact the engine reads, never a judgement the model makes. Lullaby r3: 9 judgements at N=1 — Amira, Ben, Chloe, Dev, Elena, Grace, Isla, Keiko `ANCHORED` (8); Finn (vague story, no chip) `GUESSED` (1); Jonas (chip) `GUESSED` by code, never read; Hugo (*ten days ago*, outside the 7-night window) and Leo (sleeps through) answer No. Corpus total at N=1 ≈ 106 people less the gate-Nos; counted when the other six entries are re-expressed, and written into the v9 header then.

### 2.5 `compare_correctness`
The eval builds the engine's input from r3 (`founder_calibration`, `answers[].{anchoring,picks}`) and shells `./gradlew -q screenContracts --args="compare <in> <out>"` (the exporter's sibling, Phase 1 A). Per dimension: `status` and `drift` equal `expected.standings[d]` → agree. Per vector: `vector_verdicts[v].{verdict,deciding}` equal. Counts (`n`, `inside`/`outside`, `optionCounts`, `median`) are compared and listed on the report, never marked. Rules as hand-worked here, which Phase 1 A implements and the founder signs (decision 2):

This is **the one compare table**: the registry's `common.compare_rules` and every `answers.*` block, and the OpenAPI's `CompareRule` / `getStandings` descriptions, agree with it (reconciled 2026-10-06).

| `CompareRule` | Inside when | Status | Drift |
|---|---|---|---|
| `proportion_from_gate` (Prevalence) | p = yes/(yes+no) over **all** gate answers lands in the founder's bin **or above it** | in bin or above → `HOLDING_UP`; below → `NOT_HOLDING_UP`; no `PEOPLE_DISAGREE` | `above` with the clause *"more than you think"* when above the bin; `below` when under; `none` in the bin (registry decision 6, decided by the founder 2026-10-07) |
| `interval_contains_median` (Frequency, Duration) | **today's magnitude rule**: the anchored person's number is in the founder's interval (inclusive); outside in **either** direction is outside | share inside ≥ 2/3 → `HOLDING_UP`; ≤ 1/3 → `NOT_HOLDING_UP`; else `PEOPLE_DISAGREE` (today's thresholds) | side of the outsiders' majority; `both` on a split; `none` when holding; median reported |
| `ordinal_band` (rung picks) | founder's rung ± 1; tolerance dimensions (`solution.reliability_tolerance`, `solution.adoption_friction`) also count the whole more-forgiving side inside; a no-direction escape ("wouldn't have reached for the phone", "free or a gift") is outside / not counted per the registry's `option_rule` | same thresholds | below / above by rung, in the registry's `{side}` words |
| `ordinal_band` (`problem.importance` only) | the share of anchored people who picked the problem's own item, mapped onto the rank band (the registry's `_note`): `biggest` ≥ 1/2 · `top_three` 1/4–1/2 · `middle` 1/10–1/4 · `minor` 1/25–1/10 · `negligible` below | share in the founder's band → `HOLDING_UP`, else `NOT_HOLDING_UP`; no `PEOPLE_DISAGREE` | `lower` / `higher` |
| `choice_majority` | picked the founder's option | same thresholds | `none`; earlier / later where the codes are ordered (`solution.compatibility`) |
| `set_overlap` | **per code, not per person** (the registry's line): every founder code ticked by ≥ half of anchored people and no unpicked code by > half | a founder code under a third, or an unpicked code over half → `NOT_HOLDING_UP`; between → `PEOPLE_DISAGREE` | `none`; `optionCounts` reported, the unpicked code named ("which you didn't name") |
| `ordered_set_overlap` | `set_overlap` on the codes, plus the modal first step = the founder's first step | same | `none`; first action reported |
| `role_chain_match` | `choice_majority` on the role-chain code | same thresholds | `none` |
| `ladder_rung` | ticked the founder's highest rung or a higher one; `nothing_yet` is outside | same thresholds | `none`; "{observed} of {n} would" |
| `threshold_band` | — | `BAR_SET` always; bar = the median band, reported against the founder's number | higher / lower / level with |
| `price_hypothesis` | — | `NOT_TESTED_BY_DESIGN`; median last-paid reported | `none` |
| any, `unsure` | — | `LEFT_OUT` | — |
| any, `respondent.asked_in_v1` false with a belief (Urgency, Retention potential) | — | `NOT_ASKED_YET`, sub-line *"not asked in this round"* (registry decision 3) | — |
| any, anchored < `answers.floor` (5) | — | `TOO_FEW_TO_CALL` | — |

Vector verdict = the worst status among the vector's three `DEAL_BREAKER` dimensions, ordered `NOT_HOLDING_UP > PEOPLE_DISAGREE > TOO_FEW_TO_CALL > BAR_SET > HOLDING_UP`; `NOT_ASKED_YET` until every asked deal-breaker has reached the floor; `LEFT_OUT` never decides unless all three are left out (then `LEFT_OUT`). Guessed people's answers are shown, never counted; a `rough` numeric answer from an anchored person is treated as guessed for that dimension only.

### 2.6 `brief_paragraphs`
Today's four (`shape`, `coverage`, `register`, `source_material`) plus `no_claim_words`. Changes inside the four: `coverage`'s deciding line = `vector_verdicts[v].deciding` (the worst deal-breaker), its number = that line's reported median / proportion / count; allowed `N of M` = `inside`/`outside` of `n` and every `optionCounts` row of `n`; `source_material` sweeps the new enum names (`HOLDING_UP`… `NOT_TESTED_BY_DESIGN`, `DEAL_BREAKER`, `SHAPES`, `PROBLEM`/`SOLUTION`/`COMMERCIAL`) and every dotted dimension key. `no_claim_words`: the sentence(s) naming a dimension whose `answers.status_vocabulary` contains `BAR_SET` or `NOT_TESTED_BY_DESIGN` (by `name`, case-folded) carry none of `works, worked, effective, proves, proven, confirmed, will save, saves, validated, delivers`. Evidence recorded per case; the paragraph is rendered whole beside the standings as before (call 17). Verdict phrasing stays observed, never marked (call 20).

### 2.7 Refusals and the judge
`rule_refusal_rate` = refusals / answers the aggregate judged (all model screens; keel-cloud's validator must take the new case kinds, else the mark is unmeasured and fails — spec 025 FR-019's rule). `shape_refusals` absolute zero. (call 41, founder decision 35, 2026-10-08: the rate counts EVERY rule refusal -- the first draft's and a redraw's -- over the first-draft answers the aggregate judged, the v6 denominator unchanged; one repair turn follows a rule refusal on the five screens keel-cloud redraws (`CALIBRATION_QUESTIONS`, `RESPONDENT_QUESTIONS`, `CONTEXT_INTERPRET`, `PROBLEM_INTERPRET`, `SOLUTION_MECHANISM`; `INTERPRET` and `BRIEF` are never redrawn), costing one more host call each. Shape refusals are not redrawn and stay an absolute zero on the raw answer; a redraw's own shape refusal counts there too.) The judge answers one question only (§2.3); `judged_fraction` and `judge_calls` are reported.

## 3. Judgement calls appended at v9 (28–36; `marks.py`, struck nowhere)

| # | Call |
|---|---|
| 28 | **New subjects are a rubric change.** The five new screens of §1 replace `*_ASSUMPTIONS` and `QUESTIONS`; `INTERPRET` keeps its constant and is narrowed to the gate story (one judgement a respondent); the three interpretation screens are rendered and never scored — their leaks are rule refusals (`X1` / `P1` / `M1`) feeding `rule_refusal_rate` only (call 10). Scores before and after are not comparable. |
| 29 | **`golden_belief_recall` is retired, and `align.py` with it.** A calibration answer is a typed pick against the registry; the model writes the question, the engine writes the belief. There is no structure to align, no option list to overlap, no tie to break. The golden is the registry slice, not text. |
| 30 | **`dimension_coverage` is absolute.** One question per dimension, both screens; denominators per §2.1. A plan the eval built by code from `founder_calibration` is what the respondent screen is handed, exactly as production's `EVIDENCE_PLAN` would. |
| 31 | **`option_validity` is code, and 1.00 is honest only because the registry fixes the codes.** The mark checks the mapping, not the invention. |
| 32 | **`no_leak`'s list is derived from the corpus's golden mechanism, never from the live `SOLUTION_MECHANISM` output** (the ruler must not move with the subject); ties are inflection collisions with the problem's own words and go to the judge; every other hit is a fault. |
| 33 | **One anchoring judgement per respondent.** Gate-No respondents are outside every denominator; **amended 2026-10-07 (decision 10):** a chipped story is set `GUESSED` by code with no call and is OUTSIDE the denominator too — only un-chipped stories are read. Number unchanged. |
| 34 | **`compare_correctness` spends nothing and is measured on `DRY=1`.** Status + drift marked; counts reported; an export without the engine leaves it unmeasured, which fails (call 13). This repo keeps no copy of the arithmetic (DRIFT #33/#36/#41/#44/#45). |
| 35 | **`brief_paragraphs` gains `no_claim_words`**, scoped to the sentence naming a `BAR_SET` or `NOT_TESTED_BY_DESIGN` dimension; the deciding line is the worst deal-breaker; all five or nothing. |
| 36 | **`rule_refusal_rate` keeps 0.02 while its denominator triples**; the new reading is recorded in `marks.toml` and is the founder's decision 1, not a quiet tightening. |

## 4. Corpus revision 3 — schema

Recorded revision (README's rule), the second since the freeze. Seven entries re-expressed, `03-lullaby` first. The registry (exported by keel-cloud beside the contracts) is the schema for every dimension-keyed map below; `check_corpus.py` and `GoldenCorpusTest` read both.

```yaml
id: 03-lullaby                      # unchanged
title: …                            # unchanged
revision: 3                         # NEW; a file without it is a refusal to start
market: {country, region, language} # kept
statements: {problem, solution, commercial}   # kept: the seeds typed in chat, verbatim
roles: [{id, label, roleType, about}]         # kept; a B2B entry adds the decision-maker role
context:                            # NEW — the four fields + the sentence CONTEXT_INTERPRET would write
  actor: …  actor_plural: …  job: …  circumstance: …  segment: …  understood: "Keel understands …"
solution_mechanism:                 # NEW — golden SOLUTION_MECHANISM output; no_leak's source
  actor: …  trigger: …  mechanism: …  output: …  not_assumed: [ … ]
persona:                            # NEW — PERSONA_MODEL's input, from step 4
  decision_maker: same_person | {role: <roles[].id>}
founder_calibration:                # NEW — one entry per registry key (25); the typed belief
  <dimension>: {answer: <code> | {lower, upper, unit} | {value, unit} | [codes] | {lower, upper, per},
                belief_phrase: "…"}       # phrase = the chosen option's, the model's words in the product; hand-written here
  <dimension>: {unsure: true}             # LEFT OUT
  # model-written sets (and the ladder) also carry `labels: ["…"]` -- the labels the founder saw, one per founder option
  # code in the plan row's order (code-appended rows excepted, a founder-side none kept); what production sends the
  # respondent screen as `founder_options` (keel-cloud 058 afe36fd; Lullaby's = the registry's lullaby labels, 058's C6 rewording)
  # belief_sentence per dimension is the engine's output, recorded by the checker like buckets were — never hand-written
respondent_questions:               # NEW — golden PLAN (the eval builds it by code and checks the model's answer against it); no text
  <dimension>: {part: 1|2|3, control: <RespondentControl>, codes: [ … ]}   # codes = founder's + distractors + something_else
# NO golden calibration_questions: the model's questions are scored against the registry (option_validity), not against text
answers:
  - person: …
    recency: yes | no               # NEW — the gate (= problem.prevalence); `no` ends the entry for this person
    story: "…"                      # NEW — the only free text; absent when recency: no
    chip: null | cant_recall | rather_not_say   # NEW — the gate chip
    anchoring: ANCHORED | GUESSED   # golden, one per respondent; null when recency: no
    picks:                          # kept, keyed by DIMENSION now; a value per respondent.control, or {chip: …}
      <dimension>: <code> | <int> | {value, unit, rough: bool} | [codes, in tick order] | {band} | {bought, cost, still_using} | {last_paid, guess}
    pilot_opt_in: bool
expected:
  standings:                        # keyed by dimension; status words from `Status`
    <dimension>: {status, drift, n, inside?, outside?, median?, proportion?, optionCounts?, bar?}   # optionCounts keeps the 2026-10-01 string encoding
  vector_verdicts:                  # NEW — replaces expected.stages
    PROBLEM: {verdict, deciding: <dimension>}   SOLUTION: …   COMMERCIAL: …
```

**Dropped:** `beliefs[]` (type/measure/band/expectation, risk, mark, founderPhrase, selection), `questionnaire.anchors` and selections, per-anchor `text`/`tap`/`anchoring`, the A1-merge semantics and `stages` lists, `expected.buckets`, `expected.stages`, `normalization_rationale`. **Kept with new meaning:** `picks` (by dimension, not selection id); `optionCounts` (same encoding, on set dimensions).

## 5. `03-lullaby` revision 3 — worked excerpt (for this document; the corpus folder is not touched)

**Owned by the registry.** Every founder answer, code, status, count and median below is the registry's `lullaby` object for that dimension and its `founder.normalized.codes`; this excerpt only re-expresses them in the r3 schema and adds the per-person picks the counts imply (chosen for Amira and Jonas to fit the registry's counts). Where the two disagree, the registry wins and this excerpt is wrong.

```yaml
id: 03-lullaby
revision: 3
market: {country: GB, region: null, language: en-GB}
context:                                   # the registry's common.context_placeholders, Lullaby values
  actor: parent
  actor_plural: parents of babies under six months
  job: work out what the baby needs and settle them
  circumstance: the baby cries in the night
  segment: first-time parents in the UK, baby under six months
  understood: "Parents of babies under six months, when the baby cries in the night and they must work out what it needs and settle them."
solution_mechanism:                        # instruction table §C4's worked example
  actor: the parent
  trigger: when the baby is crying at night and the reason is unclear
  mechanism: holds the phone near the cot for about ten seconds while it listens
  output: a short card naming what the baby most likely needs, and the next most likely
  not_assumed: ["stops the guessing", "settles the baby faster"]
  mechanism_terms: [listen, phone, cot, card, most likely, suggestion]
persona: {decision_maker: same_person}
founder_calibration:                       # answer = the registry's normalized code(s) / numbers; belief_phrase = the chosen option's, from lullaby.founder_options
  problem.prevalence:            {answer: p_60_80, belief_phrase: "Most"}                                   # "6 to 8 in 10" (restored from HANDOFF; the above-the-band case)
  problem.frequency:             {answer: {lower: 4, upper: 7, unit: "nights out of 7"}, belief_phrase: "4 to 7 nights out of 7"}
  problem.severity:              {answer: very, belief_phrase: "costs a large part of the night's sleep"}
  problem.duration:              {answer: {lower: 15, upper: 25, unit: minutes}, belief_phrase: "15 to 25 minutes"}
  problem.importance:            {answer: top_three, belief_phrase: "one of the top three"}
  problem.consequence:           {answer: [lost_sleep, stress, next_day_fatigue], belief_phrase: "lost sleep and stress and a worse next day"}
  problem.workaround_burden:     {answer: [feed, change, rock_hold], belief_phrase: "feeding, a nappy change, rocking"}   # tick order stored
  problem.current_solution_satisfaction: {answer: works_poorly, belief_phrase: "works poorly: they end up guessing"}
  problem.urgency:               {unsure: true}
  solution.compatibility:        {answer: before_any_attempt, belief_phrase: "right at the start, before anything is tried"}
  solution.relative_advantage:   {answer: fewer_attempts, belief_phrase: "fewer things tried before the baby settles"}
  solution.effectiveness_threshold: {answer: {value: 5, unit: minutes}, belief_phrase: "at least 5 minutes"}
  solution.trust_risk:           {answer: [labelled_suggestion, safe_actions_only], belief_phrase: "it is plainly labelled a suggestion and it only ever suggests safe things to try"}
  solution.reliability_tolerance: {answer: one_in_five, belief_phrase: "about one time in five"}
  solution.adoption_friction:    {answer: a_few_taps, belief_phrase: "a few taps"}                           # single_choice: one code, not a list
  solution.trialability:         {answer: [free_no_card, easy_exit], belief_phrase: "it is free with no card details and they can delete everything at any time"}
  solution.observability:        {answer: [settled_sooner, fewer_tries], belief_phrase: "the baby settled sooner than usual and they tried fewer things"}
  solution.target_circumstance:  {answer: routine_failed, belief_phrase: "when the usual routine has not stopped the crying"}
  commercial.existing_sacrifice: {answer: [apps_subscriptions, gadgets], belief_phrase: "money on baby apps and money on gadgets"}
  commercial.wtp_hypothesis:     {answer: {lower: 5, upper: 12, currency: GBP, per: month}, belief_phrase: "£5 to £12 per month"}
  commercial.ability_to_pay:     {answer: without_cutting_back, belief_phrase: "fairly easily, without cutting back elsewhere"}
  commercial.buyer_payer_alignment: {answer: same_person, belief_phrase: "the same person uses it, decides and pays"}
  commercial.purchase_friction:  {answer: [partner_approval, privacy], belief_phrase: "needing a partner's agreement and worries about recording the baby"}
  commercial.commitment:         {answer: [install, mic], belief_phrase: "allowing the microphone"}         # the highest ticked rung is the belief (registry decision 9)
  commercial.retention_potential: {unsure: true}
respondent_questions:                      # the plan: part, control, codes = the registry's respondent_options in code form
  problem.frequency:  {part: 1, control: segmented_0_to_7}
  problem.severity:   {part: 1, control: single_choice_5, codes: [barely, a_little, moderately, very, extremely]}
  problem.duration:   {part: 1, control: number_with_unit}
  problem.importance: {part: 1, control: single_choice, codes: [back_down_after_feed, knowing_what_the_cry_means, back_to_sleep_myself, sharing_the_night, early_morning_wakes, something_else]}   # the problem's own item never first
  problem.consequence: {part: 1, control: multi_choice, codes: [lost_sleep, partner_woken, stress, next_day_fatigue, sought_help, looked_it_up, nothing_much, something_else]}
  problem.workaround_burden: {part: 1, control: multi_choice_ordered, codes: [feed, change, rock_hold, soothe_aids, check_comfort, look_up_or_ask, something_else]}
  problem.current_solution_satisfaction: {part: 1, control: single_choice_5, codes: [works_well, mostly_works, hit_and_miss, works_poorly, no_reliable_way]}
  # problem.prevalence is the gate (recency); problem.urgency is left out and not asked in V1
  # solution.* part 2 (9) and commercial.* part 3 (6): codes = lullaby.founder_options plus the registry's fixed respondent-only codes (own_instinct, not_useful, nothing_yet) and escapes
answers:
  - person: Amira Saleh
    recency: yes
    story: "Last night. Up at one, half three and five. The one o'clock took ages, she wanted feeding but I tried the nappy first."
    chip: null
    anchoring: ANCHORED
    picks:
      problem.frequency: 5
      problem.severity: very
      problem.duration: {value: 25, unit: minutes, rough: false}
      problem.importance: knowing_what_the_cry_means
      problem.consequence: [lost_sleep, stress, next_day_fatigue]
      problem.workaround_burden: [change, feed]
      problem.current_solution_satisfaction: mostly_works
      solution.compatibility: before_any_attempt
      solution.relative_advantage: fewer_attempts
      solution.effectiveness_threshold: {band: "10-20", unit: minutes}
      solution.trust_risk: [labelled_suggestion, audio_private]
      solution.reliability_tolerance: one_in_five
      solution.adoption_friction: a_few_taps
      solution.trialability: [free_no_card, easy_exit]
      solution.observability: [settled_sooner, fewer_tries]
      solution.target_circumstance: routine_failed
      commercial.existing_sacrifice: {bought: apps_subscriptions, cost: {value: 24, currency: GBP, per: three_months}, still_using: yes}
      commercial.wtp_hypothesis: {last_paid: {value: 8, currency: GBP, per: month}, guess: {value: 6, currency: GBP, per: month}}
      commercial.ability_to_pay: without_cutting_back
      commercial.buyer_payer_alignment: same_person
      commercial.purchase_friction: [partner_approval, social_proof]
      commercial.commitment: [install, mic, next_episode]
    pilot_opt_in: true
  - person: Jonas Weber
    recency: yes
    story: "Couple of times a night usually. Can't say about last night, my partner did it."
    chip: cant_recall
    anchoring: GUESSED                     # by code (chip), never read — shown hollow, counted nowhere
    picks:
      problem.frequency: 2
      problem.severity: moderately
      problem.duration: {value: 10, unit: minutes, rough: true}
      problem.importance: sharing_the_night
      problem.consequence: [lost_sleep]
      problem.workaround_burden: {chip: cant_recall}
      problem.current_solution_satisfaction: mostly_works
      solution.compatibility: after_first_attempt_fails
      solution.relative_advantage: less_worry
      solution.effectiveness_threshold: {band: "5-10", unit: minutes}
      solution.trust_risk: [own_instinct]
      solution.reliability_tolerance: one_in_ten
      solution.adoption_friction: one_tap
      solution.trialability: [free_no_card]
      solution.observability: [fewer_tries]
      solution.target_circumstance: alone
      commercial.existing_sacrifice: {bought: gadgets, cost: {value: 35, currency: GBP, per: three_months}, still_using: yes}
      commercial.wtp_hypothesis: {last_paid: {value: 35, currency: GBP, per: one_off}, guess: null}
      commercial.ability_to_pay: without_cutting_back
      commercial.buyer_payer_alignment: joint_decision
      commercial.purchase_friction: [partner_approval, privacy]
      commercial.commitment: [nothing_yet]
    pilot_opt_in: false
  # Ben, Chloe, Dev, Elena, Grace, Isla, Keiko: recency yes, ANCHORED; Finn: recency yes, vague story, GUESSED;
  # Hugo ("about ten days ago") and Leo (sleeps through): recency no — no story, no picks, in prevalence's denominator
expected:
  standings:   # problem vector = the registry's lullaby.expected per dimension, under §2.5's rules; 8 anchored, floor 5 met
    problem.prevalence:  {status: HOLDING_UP,      drift: above, n: 12, yes: 10, proportion: 0.83}   # above the 0.6–0.8 bin: "more than you think · you said Most · 10 of 12 said yes"
    problem.frequency:   {status: HOLDING_UP,      drift: none,  n: 8, inside: 6, outside: 2, median: 5}
    problem.severity:    {status: PEOPLE_DISAGREE, drift: below, n: 8, inside: 5, outside: 3}        # ±1 band on `very`; 3 said a_little or barely
    problem.duration:    {status: NOT_HOLDING_UP,  drift: below, n: 7, inside: 2, outside: 5, median: 11}   # "smaller than you think · you said 15 to 25 minutes · middle answer 11 min · 7 described it"; Grace's 40 min is a rough guess, shown not counted
    problem.importance:  {status: HOLDING_UP,      drift: none,  n: 8, own_item_picks: 3, share: 0.38}   # top_three band 1/4–1/2
    problem.consequence: {status: HOLDING_UP,      drift: none,  n: 8,
                          optionCounts: "lost_sleep=8, partner_woken=3, stress=5, next_day_fatigue=6, sought_help=0, looked_it_up=2, nothing_much=0, something_else=0"}
    problem.workaround_burden: {status: HOLDING_UP, drift: none, n: 8, first_action: feed, first_action_count: 5,
                          optionCounts: "feed=7, change=6, rock_hold=6, soothe_aids=2, check_comfort=3, look_up_or_ask=1, something_else=1"}
    problem.current_solution_satisfaction: {status: NOT_HOLDING_UP, drift: above, n: 8, inside: 2, outside: 6}   # "works better than you think · … · most of the 8 said it worked after a try or two"
    problem.urgency:     {status: LEFT_OUT}
    # solution.* and commercial.* per the registry: solution.effectiveness_threshold → BAR_SET (bar set at 10 min); commercial.wtp_hypothesis → NOT_TESTED_BY_DESIGN; commercial.retention_potential → LEFT_OUT
  vector_verdicts:
    PROBLEM:    {verdict: NOT_HOLDING_UP, deciding: problem.duration}          # worst of prevalence HOLDING_UP / frequency HOLDING_UP / duration NOT_HOLDING_UP
    SOLUTION:   {verdict: NOT_HOLDING_UP, deciding: solution.compatibility}
    COMMERCIAL: {verdict: NOT_HOLDING_UP, deciding: commercial.commitment}
```

The eight anchored people's problem picks behind those counts — frequency `5 5 7 4 6 5 3 2` (median 5; 6 in 4–7, Isla and Keiko below), severity `very a_little very barely very extremely very a_little` (5 in the ±1 band, 3 two rungs down), duration `25 5 20 8 12 40* 10 11` (* Grace's forty-minute reflux night is a rough guess, shown not counted; the 7 counted give median 11, 2 inside, 5 below), satisfaction `mostly_works works_well hit_and_miss mostly_works works_poorly mostly_works mostly_works works_well` (2 inside the ±1 band on works_poorly, 6 better; Ben and Keiko knew the cause at once), own-item Importance picks Amira, Chloe, Elena (Amira, Ben, Chloe, Dev, Elena, Grace, Isla, Keiko) — are consistent with their r2 stories; they go into the corpus file when r3 is written, not here. **Flagged, not fixed:** the registry's commercial examples count `n=11` anchored, but under the gate rule (a gate-No answers nothing; marks call 33) at most 10 people and 8 anchored reach part 3 — the registry's part-3 counts are to be reworked at n ≤ 10 when corpus r3 is written (decided 2026-10-07, reconciliation decision 14; no status is expected to change).

## 6. What changes in `keel-e2e-eval`

| File | Change |
|---|---|
| `instructions/marks.py` | `MARKS_VERSION = 9`; `DEFAULTS` = the eight keys of the .toml; `judge()` gains `dimension_coverage`, `option_validity`, `no_leak`, `compare_correctness` rows (each `measured` + `met`, unmeasured fails) and drops `golden_belief_recall`; calls 28–36 appended. |
| `instructions/marks.toml` | `marks-v9.draft.toml`, verbatim. |
| `instructions/corpus.py` | r3 loader: `Entry` gains `revision`, `context`, `solution_mechanism`, `persona`, `founder_calibration`, `respondent_questions`; loses `beliefs`, `questionnaire`; `Person` = `{person, recency, story, chip, anchoring, picks, pilot_opt_in}`; `Entry.plan()` (asked ∧ not unsure, by part), `Entry.vocabulary()`; refusal to start on `revision != 3`, on `beliefs`/`questionnaire` present, on a pick keyed by anything but a registry key. Hashing and `verify_unchanged` untouched. |
| `instructions/contract.py` | screen constants for §1's eight screens (seven model screens + `COMPARE`); `ExportedContract.registry` read from `dimension-registry.json` beside `model-routing.json` (the exporter's new fourth file, Phase 1 A); refusal if absent. |
| `instructions/context.py` | `build_calibration(entry, vector, registry)`, `build_respondent(entry, part, plan)`, `build_anchor_read(entry, person)`, `build_brief(entry, standings)`, the three interpretation contexts; `earlier_lines`, `build_questions`, `anchors_for` deleted. |
| `instructions/prompts.py` | `build_cases` order per entry: interpret ×3 → calibration ×3 → respondent ×3 → anchor reads → compare (no call) → brief; ids `<entry>/CALIBRATION_PROBLEM/run1`, `<entry>/RESPONDENT_PART1/run1`, `<entry>/INTERPRET/<person>/run1`, `<entry>/COMPARE`, `<entry>/BRIEF/run1`; `-k` needles `interpret`, `calibration`, `respondent`, `anchor`, `compare`, `brief`. |
| `instructions/score.py` | `score_calibration`, `score_respondent` (coverage, validity, leak per question, evidence per fault), `score_anchor_read` (replaces `score_reading`, keyed by person), `score_compare` (per dimension + per vector, counts diffed), `totals` with the new keys and the old reading/refusal keys; `spread` per case for coverage, validity, leak, anchoring. `score_assumptions` deleted. |
| `instructions/align.py` | **Retired** (call 29). `normalise` moves to a small `text.py`; nothing else survives. |
| `instructions/judge.py` | One question, `reveals_solution(question_text, mechanism_one_liner)`; `same_answer_space`, `same_expected_option`, `pick` deleted; `JUDGE_UNSET_ENV` kept. |
| `instructions/brief.py` | fifth mark `no_claim_words`; `deciding_line` reads `vector_verdicts`; `ENUM_NAMES`, `CONTEXT_FIELD_NAMES` extended; `VERDICT_MARKERS` keyed by `Status`. |
| `instructions/compare.py` (new) | builds the engine input from r3, shells `screenContracts compare`, diffs; runs on `DRY=1`. |
| `instructions/validate.py` | batch kinds for the nine screens; `fold_in` unchanged; an unknown kind → the mark unmeasured, by name (FR-019's rule). |
| `instructions/rescore.py` | refuses `marks_version < 9` by name: *answered on screens v9 does not have, against corpus r2*; writes `scorecard-v9.json` beside for v9 bundles. |
| `instructions/report.py` | mark table rows: dimension coverage · option validity · no leak · anchoring accuracy · compare correctness · BRIEF paragraphs (five) · shape refusals · refusals rate; `register.html` per entry: the 25 calibration questions beside the registry's `lullaby.founder_question` and the founder's answer → belief sentence; the 23 respondent questions beside the plan; the reveal text; the three interpretations; the brief beside the standings table (columns: dimension · status · drift · n · median/counts). |
| `instructions/models.py` | classes per the cloud's v9 routing export, lower-cased `JobClass`: `context` (CONTEXT_INTERPRET), `frame` (PROBLEM_INTERPRET, SOLUTION_MECHANISM), `calibration`, `respondent`, `reading` (INTERPRET), `brief`; routing stays v8 until the certificate, so `MODELS=exported` refuses until keel-cloud exports the new table. |
| `instructions/why.py` | unchanged events; `WHY=marks:9` is the full run. |
| `tests/` | fixtures for r3, the registry, each scorer, the rescore refusal; `README.md`/`AGENTS.md` gate text. |

## 7. WHY events and the run order

| Step | Command | Event |
|---|---|---|
| 0 | `make instruction-eval DRY=1 K=03-lullaby` | none; `compare_correctness` already measured on r3 + the engine |
| 1 per template | `make instruction-screen K=03-lullaby HOST=claude WHY=instruction:<template>.md MODELS=exported` (N=3) | `instruction:` |
| 1b | same with `WHY=contract:<file>` when the 0.4 contract export lands | `contract:` |
| 2, once | `make instruction-eval HOST=claude WHY=marks:9 MODELS=exported` | `marks:` — the certificate; ≈ 420 calls at N=3 |

A screen certifies one entry and never the gate; a template is edited on its screen's evidence; the full run is spent once, after all templates and all seven r3 entries exist (HANDOFF §4 waits).

## 8. Decisions (closed 2026-10-07)

All ten were taken by the founder on 2026-10-07 (phase0-reconciliation.md §B is the merged list of 18). Outcomes:

1. `rule_refusal_rate` — decided: **0.02 kept** over the tripled denominator (≈ 3 corrections at N=1, 10 at N=3); tighten only on evidence from the full run.
2. §2.5's compare rules — decided: **signed as tabled** (2/3 and 1/3 thresholds, ordinal band = rung ± 1, `set_overlap` per code, Importance share → band, Prevalence above the bin holds with "more than you think", Frequency/Duration keep the magnitude rule).
3. Hugo Laurent — decided: **answers No** at the 7-night gate; his story is not re-dated.
4. Which entry leaves out an asked dimension — decided: **`01-countly` leaves out `problem.severity`**.
5. `compare_correctness` — decided: **in both** the eval (shelled, zero spend, `DRY=1`) and `GoldenCorpusTest`.
6. `no_leak` ties — decided: **inflection collisions only**, with the judge's one closed question as written in §2.3.
7. `founder.unsure_allowed = false` on `problem.prevalence` — decided: **confirmed**; no "I'm not sure" on the gate.
8. BRIEF paragraphs — decided: **one paragraph per project** at the 2 000 edge.
9. The three interpretation screens — decided: **run on every screen** (≈ 3 unscored calls per entry, feeding `rule_refusal_rate`).
10. The chipped story — decided: **set `GUESSED` by code, no call**; `INTERPRET` reads un-chipped stories only, and §2.4's denominator is 9 on Lullaby (8 `ANCHORED` / 1 `GUESSED`), Jonas's chipped story never read.

The questions as they were tabled, kept for the record:

1. `rule_refusal_rate`: keep 0.02 over the tripled denominator (≈ 3 corrections at N=1), or set 0.01.
2. Sign or amend §2.5's compare rules (2/3 thresholds, ordinal ± 1, set ≥ half, Importance share bands, gate drift) before the other six entries are re-expressed.
3. Hugo Laurent's wake-up is ten days old: under the 7-night gate he answers No and leaves the problem vector (accepted above); alternatively re-date his story.
4. Which entry leaves out an *asked* dimension so `dimension_coverage`'s `unsure` subtraction is exercised (proposal: `01-countly` leaves out `problem.severity`).
5. `compare_correctness` lives in the eval (shelled, zero spend) as well as in `GoldenCorpusTest` — or in keel-cloud's test alone.
6. `no_leak`'s tie definition (inflection collisions only) and the judge's single question.
7. `founder.unsure_allowed = false` on `problem.prevalence` — the marks assume the gate cannot be left out.
8. One BRIEF paragraph per project at the 2 000 edge with 25 dimensions, or one per vector (three cases per entry).
9. Run the three interpretation screens on every screen (≈ 3 calls per entry, unscored, feeding `rule_refusal_rate`) or only on the full run.
10. A chipped story is read by the model (in the denominator, golden `GUESSED`) rather than set to `GUESSED` by code — keep, or make the chip deterministic (the instruction table §C6 already says chip or empty story → `GUESSED` by code, no call) and narrow `INTERPRET` to un-chipped stories. The two drafts differ (instruction table §C6: by code, no call; §2.4 here and the .toml: the model reads it and must say GUESSED) — the founder picks; the reconciliation recommends by code, after which §2.4's denominator drops the chipped stories (Lullaby 9, not 10).
