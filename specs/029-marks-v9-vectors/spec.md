# Feature Specification: marks v9, corpus revision 3, and the run that certifies the vectors

**Feature Branch**: `029-marks-v9-vectors` (keel-e2e-eval, off `master` at `0165017`)

**Created**: 2026-10-06

**Status**: **PROPOSED — for the founder's review. Nothing here is built, spent or committed.**
Phase 1 track D of the vector redesign (HANDOFF §4): one umbrella spec in keel-e2e-eval. The seven
instruction templates it screens each get their own keel-cloud spec (the table under *The
instruction templates*); routing v9 is a separate keel-cloud spec after the certificate.

**Input**: the Phase 0 drafts in `keel-cloud-docs/canon/drafts/vector-redesign-2026-10-06/`, read in
full — `HANDOFF.md` (§2–§4, §6), `marks-v9.draft.toml`, `marks-v9.draft.md` (§1–§8),
`instruction-table.v1.draft.md` §B, §C, §E, §G, `dimension-registry.v1.draft.yaml` (header, the
`lullaby` objects, `checks`), `registry-schema.draft.md`; keel-cloud-docs `CANON.md` §3; the frozen
corpus `README.md` and `03-lullaby.yaml` (**read only**); this repository at `0165017` — `Makefile`
(`instruction-screen`, `instruction-eval`), `instructions/why.py`, `marks.py`, `marks.toml`,
`models.py`, `contract.py`, `corpus.py`, `rescore.py`, the `README.md`/`AGENTS.md` gate text; spec
`025-one-occasion-marks` and keel-cloud spec `056-questions-coverage` as the house styles. Where the
drafts disagree, the settled decisions of 2026-10-06 (*Assumptions* A-1 to A-9) win, and the
founder's decisions of 2026-10-07 close every clarification this spec had (*Decisions applied*).

## The one sentence

**`MARKS_VERSION` goes 8 → 9 with judgement calls 28–36: the subjects become `CONTEXT_INTERPRET`,
`PROBLEM_INTERPRET`, `SOLUTION_MECHANISM` (rendered, unscored), `CALIBRATION_QUESTIONS`,
`RESPONDENT_QUESTIONS`, `INTERPRET` (narrowed to the gate story), `COMPARE` (code, zero spend) and
`BRIEF`; `golden_belief_recall` and `align.py` retire; four marks are born, every one measured by
code against the registry keel-cloud exports; the corpus is re-expressed as revision 3 across all
seven entries, `03-lullaby` first; each of seven templates passes its own screen on `03-lullaby` at
N=3; and one full run, `WHY=marks:9`, is the certificate routing v9 lands on.**

## What this spec does not do

- **It writes no instruction file** — keel-cloud 059–065 do, one each, under CANON §3. It defines
  the screen each must pass, and the order.
- **It does not score the three interpretation screens** (A-2): rendered on `register.html`, judged
  by the aggregate for `rule_refusal_rate` only. The product-word sweeps `instruction-table` §C1/
  §C2/§C4 attach to them are the aggregate's rules (`X1`, `P1`, `M1`), not a mark here.
- **It does not rename `INTERPRET`** (A-1) and **does not touch `model-routing.json`** (A-9).
- **It adds no golden question text**: the registry slice is the golden (call 29).
- **It carries no corpus file** (spec 021 deviation 3): r3 lands as a keel-cloud commit, hashed here.
- **It re-scores no v8 bundle**: `rescore.py` re-reads the corpus, and the corpus moved. Refused.
- **No change to `why.py`'s events, no repair turn, no second run, no `evals/policy.py`.**

## The siblings, and the Waits (HANDOFF §4)

| Sibling | What this feature depends on | State |
|---|---|---|
| keel-cloud **058** (track A) | the `Dimension` registry class exported as `dimension-registry.json` beside the contracts; `InferenceScreen` += five constants, `JobClass` += `CONTEXT`, `CALIBRATION`, `RESPONDENT`; contract export for the five new and two narrowed screens; `screenContracts compare <in> <out>` (the engine, shelled); `screenContracts validate` taking the new kinds; `check_corpus.py` and `GoldenCorpusTest` reading r3 | not started |
| keel-cloud **059–065** | the seven templates, one spec each | numbers proposed below |
| keel-cloud routing v9 | the certificate's table | after SC-012 |
| this repository | spec 009's `instructions/`, 022's `models.py`, 024's judge isolation, 025's v8 | `master` `0165017` |

**P1 can go green with nothing from a sibling but r3 of `03-lullaby` and the engine; P2–P4 wait for
058's registry and contract exports** (the Waits). Everything provable without them is held by
`make unit` against fixtures.

## What changes, stated first (marks-v9.draft.md §6, reconciled to A-1 to A-9)

| File | Change |
|---|---|
| `instructions/marks.py` | `MARKS_VERSION = 9`; `DEFAULTS` = the .toml's eight keys; `judge()` gains `dimension_coverage`, `option_validity`, `no_leak`, `compare_correctness` (`measured` + `met`; unmeasured fails) and drops `golden_belief_recall`; calls 28–36 appended. |
| `instructions/marks.toml` | `marks-v9.draft.toml` **verbatim**, its `ANCHOR_READ` mention read as `INTERPRET` (A-1). |
| `instructions/corpus.py` | the r3 loader (§4 schema): `Entry` gains `revision`, `context`, `solution_mechanism`, `persona`, `founder_calibration`, `respondent_questions`, loses `beliefs`, `questionnaire`; `Person` = `{person, recency, story, chip, anchoring, picks, pilot_opt_in}`; `Entry.plan()`, `Entry.vocabulary()`; refusals to start. `sha256`, `verify_unchanged()` untouched. |
| `instructions/contract.py` | constants for the eight screens; `ExportedContract.registry` from `dimension-registry.json`; refusal if absent. |
| `instructions/context.py`, `prompts.py` | one builder per screen (`build_calibration(entry, vector, registry)`, `build_respondent(entry, part, plan)`, `build_interpret(entry, person)`, `build_brief(entry, standings)`, the three interpretation contexts); `earlier_lines`, `build_questions`, `anchors_for` deleted; case order and ids per FR-016. |
| `instructions/score.py`, `brief.py` | `score_calibration`, `score_respondent`, `score_interpret` (by person), `score_compare`; `score_assumptions`, `score_reading` deleted; `no_claim_words` as the fifth brief mark; `totals`/`spread` with the new keys. |
| `instructions/align.py`, `judge.py` | `align.py` **retired** (call 29), `normalise` to `text.py`; the judge answers one question, `reveals_solution`; `JUDGE_UNSET_ENV` kept. |
| `instructions/compare.py` (new) | builds the engine's input from r3, shells `./gradlew -q screenContracts --args="compare <in> <out>"`, diffs; runs on `DRY=1`. |
| `instructions/validate.py`, `rescore.py` | batch kinds for the eight screens, unknown kind → mark unmeasured by name; rescore refuses `marks_version < 9` by name. |
| `instructions/report.py`, `models.py` | the v9 mark table and `register.html` per FR-022; `CLASSES = ("context", "frame", "calibration", "respondent", "reading", "brief")` (A-8). |
| `README.md`, `AGENTS.md`, `tests/` | the v9 gate text; fixtures for r3, the registry, each scorer, the refusals. |

**And seven files this repository does not own**: the corpus, at revision 3.

## The instruction templates, one keel-cloud spec each (CANON §3)

Each follows 056's shape — evidence (HANDOFF §3's smoke and the screen's own bundle), diagnosis,
the edit, a byte pin in `GenerationPromptCutsTest` from the first commit, the screen — with the
rules, refusal codes and worked examples of `instruction-table` §C. Numbers assume 058 is track
A's and yield to keel-cloud's live numbering. The screen is always `make instruction-screen
K=<needle> HOST=claude N=3 WHY=instruction:<file> MODELS=…` on `03-lullaby` r3; **a template is
edited on its screen's evidence, never the full run's** (marks §7).

| # | Title | File | Screen | Tier | Needle | Calls at N=3 | Must hold on `03-lullaby` |
|---|---|---|---|---|---|---|---|
| 059 | context-interpret | `context-interpret.md` (new) | `CONTEXT_INTERPRET` | light | `03-lullaby/CONTEXT_INTERPRET` | 3 | `shape_refusals` 0; `rule_refusal_rate` 0 of 3; rendered |
| 060 | problem-interpret | `problem-interpret.md` (new) | `PROBLEM_INTERPRET` | standard | `03-lullaby/PROBLEM_INTERPRET` | 3 | same |
| 061 | solution-mechanism | `solution-mechanism.md` (new) | `SOLUTION_MECHANISM` | standard | `03-lullaby/SOLUTION_MECHANISM` | 3 | same |
| 062 | calibration-questions | `calibration-questions.md` (new) | `CALIBRATION_QUESTIONS` | standard | `03-lullaby/CALIBRATION` | 9 (3 vectors × 3) | `dimension_coverage` 1.00 (25 of 25, three times); `option_validity` 1.00 over 75 questions; `no_leak` 1.00 over 27 PROBLEM questions; `shape_refusals` 0; rate 0 of 9 |
| 063 | respondent-questions | `respondent-questions.md` (new) | `RESPONDENT_QUESTIONS` | standard | `03-lullaby/RESPONDENT` | 9 (3 parts × 3) | `dimension_coverage` 1.00 (23 of 23, three times); `option_validity` 1.00 over 69 items; `no_leak` 1.00 over 24 Part-1 mechanism sweeps + 69 value sweeps; `shape_refusals` 0; rate 0 of 9 |
| 064 | interpret-narrowed | `interpret.md` (in place) | `INTERPRET` | light | `03-lullaby/INTERPRET` | 27 (9 gate-yes people with a typed story × 3; Jonas's chipped story is `GUESSED` by code, no call) | `anchoring_accuracy` ≥ 0.90 over 27 (24 `ANCHORED` / 3 `GUESSED`); `guessed_precision`, `guessed_recall` reported |
| 065 | brief-narrowed | `brief.md` (in place) | `BRIEF` | standard | `03-lullaby/BRIEF` | 3 | `brief_paragraphs` 3 of 3 on all five per-case marks; `shape_refusals` 0 |

**Order**: 062 first (what the registry exists for), then 063 and 064 together, then 065, then
059–061. Every screen's inputs are the corpus's own r3 `context`, `solution_mechanism` and
`expected.standings`, never another screen's live output (marks §1), so no screen waits on another.
A screen of all eight subjects on `03-lullaby` at N=3 is 57 calls and is never a run of record.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The ruler moves, the corpus follows, and the engine is read for free (Priority: P1)

**As** the owner of this rubric, **I want** `MARKS_VERSION` 9, the r3 loader and `compare.py` in
place and `make instruction-eval DRY=1 K=03-lullaby` green on `compare_correctness`, **so that** the
marks exist before any prompt is written and the one mark that spends nothing is measured first.

**Why this priority**: HANDOFF §4 — marks before prompts, never moved to fit a model.
`compare_correctness` runs on `DRY=1` (call 34) and needs no template, so it is the first thing that
can be green, and it proves r3 and the engine agree before a dollar is spent.

**Independent Test**: `make unit` green with r3 fixtures; `make instruction-eval DRY=1 K=03-lullaby`
on the real r3 `03-lullaby` prints every prompt, calls no model, and writes a `scorecard.json` with
`compare_correctness` measured at 28 of 28.

**Acceptance Scenarios**:

1. **Given** `marks.py` at v9, **When** its version and call list are read, **Then** they are `9` and
   36 calls, 1–27 byte-identical to v8's, and `DEFAULTS` has the .toml's eight keys and no
   `golden_belief_recall`.
2. **Given** `03-lullaby.yaml` at revision 3, **When** `corpus.load` reads it, **Then** `Entry.plan()`
   is `{1: 8, 2: 9, 3: 6}`, `Entry.vocabulary()` is the mechanism stems minus the problem's own
   words, and Hugo Laurent has `recency: no`, no story and no picks (his ten-day-old night is
   outside the 7-night gate; founder, 2026-10-07).
3. **Given** an entry carrying `revision: 2`, a `beliefs` or `questionnaire` key, or a pick keyed by
   a non-registry key, **When** loaded, **Then** it refuses to start, naming the entry and the key.
4. **Given** `DRY=1`, **When** `compare.py` shells the engine on the input built from
   `founder_calibration` and `answers[].{anchoring,picks}`, **Then** every `status` and `drift`
   equals `expected.standings[d]` on 25 dimensions and `vector_verdicts` on 3 — `problem.prevalence`
   `HOLDING_UP` / *more than you think* (0.83 above 6-to-8-in-10), `problem.duration`
   `NOT_HOLDING_UP` (median 11 min, 7 anchored), `problem.severity` `PEOPLE_DISAGREE`,
   `problem.current_solution_satisfaction` `NOT_HOLDING_UP`, `problem.urgency` `LEFT_OUT`,
   `PROBLEM: {verdict: NOT_HOLDING_UP, deciding: problem.duration}` — under the compare rules
   signed in FR-018 — and counts and medians are diffed and reported, never marked.
5. **Given** `runs/20261001T043420Z-instructions` (the v8 record), **When** `python -m
   instructions.rescore` is pointed at it, **Then** it refuses, naming the bundle, `marks_version`
   8 and the reason: *answered on screens v9 does not have, against corpus r2*.

---

### User Story 2 - The calibration screen passes on Lullaby (Priority: P2)

**As** the owner of `dimension_coverage`, `option_validity` and `no_leak`, **I want** keel-cloud
062's `calibration-questions.md` screened on `03-lullaby` at N=3, **so that** the first template a
founder meets is proven against the registry before a second is written.

**Why this priority**: it is the screen the registry exists for, and HANDOFF §3's smoke (25/25
valid; four fixes to carry — per-option belief phrase, contiguous bins and the 7-night window,
Retention ≠ Frequency, Importance closed on the founder side) is its evidence.

**Independent Test**: `make instruction-screen K=03-lullaby/CALIBRATION HOST=claude N=3
WHY=instruction:calibration-questions.md MODELS=…` builds 9 cases; the three marks hold at 1.00,
`shape_refusals` 0, `rule_refusal_rate` 0 of 9.

**Acceptance Scenarios**:

1. **Given** the `PROBLEM` job, **When** its context is built, **Then** it carries `vector`, `context`,
   `market`, `problem.statement` and the nine-entry slice with exactly `instruction-table` §B row 3's
   fields, and **no solution field at all**.
2. **Given** a `PROBLEM` answer, **When** `score_calibration` reads it, **Then** `dimension_coverage`
   is 9 of 9 only when every slice key appears exactly once, in `order` (call 30).
3. **Given** a closed-control question, **When** `option_validity` checks it, **Then** it fails on any
   of: count ≠ `len(founder.normalized.codes)`; options not in registry order; a `belief_phrase`
   empty or equal to its label after `normalise`; `{value}` not exactly once in `belief_template`; a
   label matching `/not sure|don't know|unsure/i`; `options` on a numeric control (marks §2.2); and
   `problem.prevalence` fails without the registry's five contiguous fifths and the 7-night window.
4. **Given** Lullaby's vocabulary (≈ `app, listen, classif, card, suggest, record, microphone,
   most-likely, next-most-likely`), **When** `no_leak` sweeps the 9 PROBLEM questions and options,
   **Then** a stem hit is a fault, an inflection collision with the problem's own words goes to
   `judge.reveals_solution` once, cached, and counts in `judged_fraction`.
5. **Given** the bundle, **When** `register.html` is opened, **Then** the 25 questions sit beside the
   registry's `lullaby.founder_question`, the founder's answer and the belief sentence, with no
   score, tick or cross (call 10).

---

### User Story 3 - The respondent and the reader are screened (Priority: P3)

**As** the owner of `anchoring_accuracy` and of the stranger's one closed question per belief,
**I want** 063's `respondent-questions.md` and 064's narrowed `interpret.md` screened on
`03-lullaby`, **so that** the interview and the one judgement per stranger are proven on the entry
the calibration was.

**Why this priority**: both read what 062 established — the plan from `founder_calibration`, the
gate story — and both are where a leak or a guess would reach a stranger.

**Independent Test**: `K=03-lullaby/RESPONDENT` builds 9 cases and holds the three marks at 1.00;
`K=03-lullaby/INTERPRET` builds 27 and holds `anchoring_accuracy` ≥ 0.90 with the confusion matrix
and the `GUESSED` precision and recall beside it.

**Acceptance Scenarios**:

1. **Given** Lullaby's `founder_calibration` with `problem.urgency` and
   `commercial.retention_potential` unsure, **When** `Entry.plan()` runs, **Then** it equals
   `respondent_questions`' keys per part (8 / 9 / 6) and is what the three jobs are handed, as
   production's `EVIDENCE_PLAN` would (call 30).
2. **Given** the Part-1 job, **When** its context is built, **Then** it carries no `mechanism`, no
   part's context carries the founder's answers, sweep A runs on its 8 items and sweep B (the
   founder's label, `belief_phrase` or number for dimension *d* in item *d*) on all 23.
3. **Given** a set item, **When** `option_validity` checks it, **Then** every founder code is present,
   at least two distractors, `something_else` last, control = `respondent.control`, `chips` =
   `respondent.chips`, and `problem.importance`'s own item is never first.
4. **Given** the ten gate-yes people, **When** `build_cases` runs at N=1, **Then** there are exactly nine
   `03-lullaby/INTERPRET/<person>/run1` cases — none for Hugo Laurent or Leo Martins (gate-No), and
   none for Jonas Weber, whose `chip: cant_recall` is set `GUESSED` by code with no call (founder,
   2026-10-07; FR-017); `score_interpret` keys on the person and neither reads nor refuses a `stage`
   or `anchorId` on a produced reading.

---

### User Story 4 - Seven entries, seven templates, one certificate (Priority: P4)

**As** the founder, **I want** the other six entries re-expressed at r3, 065 and 059–061 screened,
then one full run `WHY=marks:9`, **so that** the standing gate — *green at the current
`MARKS_VERSION`* — means something again and routing v9 has a certificate to land on.

**Why this priority**: it is the paid one; HANDOFF §4's Waits put it after all instructions and all
of r3. It is the founder's to type.

**Independent Test**: none that is free. FR-029 and SC-012.

**Acceptance Scenarios**:

1. **Given** the six remaining entries at r3, **When** `check_corpus.py` and `corpus.load` read all
   seven, **Then** every entry carries `revision: 3`, 25 `founder_calibration` keys, a plan whose
   parts sum to ≤ 23 and `expected.standings` on all 25; the B2B entry (A-5) carries
   `persona.decision_maker: {role: …}` and a `COMMERCIAL_B2B` link; the entry of FR-009 leaves out an
   **asked** dimension.
2. **Given** all seven digests, **When** the v9 header is finalised, **Then** it records them and the
   corpus-wide `anchoring_accuracy` denominator (106 people less the gate-Nos and the chipped
   stories).
3. **Given** every template screened green, **When** `make instruction-eval HOST=claude WHY=marks:9
   MODELS=exported` is spent once, **Then** the verdict is `passed: true` on all eight marks, and the
   bundle, the verdict and the price go into `README.md` and, if anything surprised, `runs/DRIFT.md`.

---

### Edge Cases

- A corpus entry at revision 2, or `dimension-registry.json` absent from the export, or the
  registry failing any of `registry-schema.draft.md`'s seven invariants: refusal to start, by name.
- The engine's `compare` command absent, or `screenContracts validate` refusing a new case kind:
  the affected marks **unmeasured** by name → the run fails (025 FR-019); never a warning.
- `MODELS=exported` against a table lacking `context`, `calibration` or `respondent`:
  `ModelsUnavailable` naming the class and the table version (A-9).
- An interpretation screen answers `NEEDS_INPUT` twice: a rule refusal (`X3`/`P3`/`M3`), counted in
  the rate, rendered as refused.
- An anchored person's numeric pick carries `rough: true`: guessed for that dimension only (marks
  §2.5) — why Lullaby's Duration n is 7, not 8.
- A gate-No person carrying a story or picks, or a chipped person carrying a story: `check_corpus.py`
  refuses the file.
- A produced reading with `anchoring` outside `{ANCHORED, GUESSED}`: a shape refusal, counted at zero.
- A `-k` needle matching no case: the run says so and spends nothing.

## Requirements *(mandatory)*

### Functional Requirements

**The rubric (marks §2, §3, §6)**

- **FR-001**: `marks.py` MUST set `MARKS_VERSION = 9` and append calls 28–36 in marks §3's words,
  verbatim, struck nowhere; calls 1–27 MUST NOT change.
- **FR-002**: `marks.toml` MUST be `marks-v9.draft.toml` verbatim (eight keys, marks §2's bars),
  `ANCHOR_READ` in its header read as `INTERPRET` (A-1), `golden_belief_recall` a struck comment only.
- **FR-003**: `marks.judge()` MUST report `measured` and `met` per mark and fail the run on any mark
  unmeasured (call 13). Every artefact a run writes MUST carry `9`.
- **FR-004**: `rescore.py` MUST refuse `marks_version < 9` by name, with the reason, and write
  `scorecard-v9.json` beside, never over, for a v9 bundle.
- **FR-005**: `align.py` MUST be retired and `score_assumptions` deleted (call 29); `normalise`
  survives in `text.py`; `judge.py` answers exactly one question, `reveals_solution`, and keeps
  `JUDGE_UNSET_ENV`.

**Corpus revision 3 (marks §4, §5; README's recorded-revision rule)**

- **FR-006**: The revision MUST be marks §4's schema: `revision: 3`; `context` (six fields);
  `solution_mechanism` (`actor`, `trigger`, `mechanism`, `output`, `not_assumed`); `persona`;
  `founder_calibration` on all 25 keys (`{answer, belief_phrase}` or `{unsure: true}`);
  `respondent_questions` (the plan — `part`, `control`, `codes`; no text); `answers[]` with
  `recency`, `story`, `chip`, `anchoring`, `picks` by dimension, `pilot_opt_in`;
  `expected.standings` by dimension with a `Status` word and `drift`; `expected.vector_verdicts`.
  `beliefs[]`, `questionnaire`, per-anchor `text`/`anchoring`, `expected.buckets`, `expected.stages`
  MUST be absent.
- **FR-007**: `03-lullaby` MUST be first and MUST reproduce the registry's `lullaby` objects (A-6):
  Prevalence *6 to 8 in 10*, 10 of 12 yes → `HOLDING_UP`, *more than you think* (above the bin
  holds; founder, 2026-10-07); Duration *15 to 25
  minutes*, median 11, 7 anchored, 2 inside 5 below → `NOT_HOLDING_UP`; Severity `PEOPLE_DISAGREE`;
  current-solution satisfaction `NOT_HOLDING_UP`; `problem.importance` by `ordinal_band` on the
  share (3 of 8 = 0.38, inside `top_three`'s ¼–½) → `HOLDING_UP` (A-7); urgency and retention
  `LEFT_OUT`; effectiveness threshold `BAR_SET`; wtp `NOT_TESTED_BY_DESIGN`; status totals
  12 / 6 / 3 / 1 / 1 / 2; verdicts deciding `problem.duration`, `solution.compatibility`,
  `commercial.commitment`. The six commercial `lullaby` examples MUST be re-worked at n ≤ 10 (a
  gate-No answers nothing more, so at most 10 people and 8 anchored reach part 3; the registry's
  `n=11` is stale), no status expected to change (founder, 2026-10-07).
- **FR-008**: The other six MUST follow, each keeping `market`, `statements`, `roles` and people,
  every verdict and drift hand-worked under the signed compare rules (FR-018) before the checker
  runs, the checker confirming counts.
- **FR-009**: One entry MUST leave out a dimension the registry **asks** in V1, so
  `dimension_coverage`'s `unsure` subtraction is exercised and not only the `asked_in_v1` one:
  `01-countly` leaves out `problem.severity` (founder, 2026-10-07; marks §8.4 closed).
- **FR-010**: One entry MUST be B2B: `persona.decision_maker: {role: <roles[].id>}`, a
  `COMMERCIAL_B2B` link, Part-3 items answered by that role's people, no context card. Proposal
  `05-paidly` with `agency` (its `BUYER` role exists); alternative `02-compliancelog`.
- **FR-011**: Hugo Laurent's wake-up is ten days old; under the 7-night gate he answers No and
  stays outside the problem vector — his story is not re-dated (founder, 2026-10-07; marks §8.3
  closed). He counts in Prevalence's denominator and nowhere else.
- **FR-012**: The seven files MUST land as a keel-cloud commit, `check_corpus.py` green on each,
  with a header recording the revision, its date and this spec — never a quiet edit. This
  repository MUST carry no copy; `tests/` MUST assert the r3 shape against the real files;
  `corpus.sha256` per file and `Corpus.verify_unchanged()` MUST NOT change.

**The scorers (marks §2.1–§2.6)**

- **FR-013**: `dimension_coverage` MUST be absolute per case (call 30): calibration denominator =
  every key in the vector's slice; respondent denominator = `Entry.plan()` per part.
- **FR-014**: `option_validity` MUST run every check of marks §2.2, both sides, the registry as
  the golden, no question text compared.
- **FR-015**: `no_leak` MUST derive its list from the golden `solution_mechanism` and `not_assumed`
  (call 32), never the live output; sweep A on PROBLEM calibration questions and Part-1 items;
  sweep B on all respondent items; ties — inflection collisions with the problem's own words only,
  nothing else (founder, 2026-10-07; marks §2.3) — to the judge once, cached; `judged_fraction`
  reported.
- **FR-016**: `build_cases` MUST emit per entry and run index, in order: `<entry>/CONTEXT_INTERPRET/
  run<N>`, `<entry>/PROBLEM_INTERPRET/run<N>`, `<entry>/SOLUTION_MECHANISM/run<N>`;
  `<entry>/CALIBRATION_<VECTOR>/run<N>` ×3; `<entry>/RESPONDENT_PART<P>/run<N>` ×3 (+
  `<entry>/RESPONDENT_B2B/run<N>` on the B2B entry); `<entry>/INTERPRET/<person>/run<N>` per gate-yes
  person with a typed story (a chipped story builds no case: FR-017); `<entry>/COMPARE` (no call, no
  index); `<entry>/BRIEF/run<N>`. `-k` matches a substring.
- **FR-017**: `score_interpret` MUST key on the person; gate-No people and chip-carrying stories
  are outside every denominator — a chipped story is set `GUESSED` by code with the call skipped
  and no case built, and that rule is the engine's, checked by `compare_correctness` (founder,
  2026-10-07; marks §8.10 closed, `instruction-table` §C6 wins; call 33's words follow in marks
  v9). Lullaby's denominator is 9, not 10.
- **FR-018**: `compare.py` MUST build the engine's input from r3 only, shell `screenContracts
  compare`, mark `status`/`drift` per dimension and `verdict`/`deciding` per vector, report counts
  and medians unmarked, spend nothing, run on `DRY=1` (call 34), and keep no copy of the
  arithmetic. The rules are 058's to implement against marks §2.5 as signed by the founder on
  2026-10-07 (A-6/A-7 made fact): Prevalence above the bin = `HOLDING_UP` *more than you think*,
  Frequency and Duration keep the magnitude rule; ⅔ and ⅓ thresholds; `ordinal_band` = the
  founder's rung ± 1; `set_overlap` per code, not per person; Importance share → band. The six
  entries are re-expressed under these rules and no others (marks §8.2 closed).
  `compare_correctness` lives here, shelled and DRY, as well as in keel-cloud's
  `GoldenCorpusTest` (founder, 2026-10-07).
- **FR-019**: `brief.py` MUST add `no_claim_words` as the fifth per-case mark (call 35), scoped to
  the sentence naming a `BAR_SET` or `NOT_TESTED_BY_DESIGN` dimension; `deciding_line` reads
  `vector_verdicts[v].deciding`; all five or nothing. The BRIEF case shape is one paragraph per
  project at the 2 000-character edge with 25 dimensions — one case per entry, never one per vector
  (founder, 2026-10-07; marks §8.8 closed).
- **FR-020**: `rule_refusal_rate` MUST keep 0.02 over the new denominator (every answer the
  aggregate judged, ≈ 20 per entry at N=1; ≈ 3 corrections at N=1, 10 at N=3), recorded in the
  .toml as the founder's decision (call 36) and not tightened to 0.01 before the full run's
  evidence (founder, 2026-10-07; marks §8.1 closed).

**The screens, the contract and the models**

- **FR-021**: `contract.py` MUST read `dimension-registry.json` from the export, refuse by name if
  absent, and check `registry-schema.draft.md`'s seven invariants before any case is built. The
  three interpretation screens MUST be built, sent, validated and rendered on every screen and the
  full run, feeding nothing but `rule_refusal_rate` and `shape_refusals` (A-2; founder,
  2026-10-07).
- **FR-022**: `report.register_blocks` MUST render per entry the 25 calibration questions beside
  the registry's `founder_question` (where one exists), the founder's answer and the belief
  sentence; the 23 items beside the plan; the reveal; the three interpretations; the brief beside
  a standings table (dimension · status · drift · n · median/counts). No score on the register.
- **FR-023**: `models.CLASSES` MUST be `context`, `frame`, `calibration`, `respondent`, `reading`,
  `brief` (A-8); `SCREEN_TO_CLASS`: `CONTEXT_INTERPRET → context`, `PROBLEM_INTERPRET` and
  `SOLUTION_MECHANISM → frame`, `CALIBRATION_QUESTIONS → calibration`, `RESPONDENT_QUESTIONS →
  respondent`, `INTERPRET → reading`, `BRIEF → brief`; six classes reported. A screen MAY pin the
  three new classes through `MODELS=<file>` at the ceiling until the export carries them; the
  certificate MUST be `MODELS=exported`.
- **FR-024**: `validate.build_batch` MUST emit a case kind per screen; an unknown kind leaves the
  affected marks unmeasured by name (025 FR-019), never a warning, never a refusal.

**The templates (keel-cloud 059–065)**

- **FR-025**: Each template MUST have its own keel-cloud spec under CANON §3 with the number, title,
  file and screen of the table above; a new file byte-pinned in `GenerationPromptCutsTest` from its
  first commit; the narrowed two edited in place.
- **FR-026**: Each screen MUST be `instruction-screen` on `03-lullaby` r3 at N=3 with
  `WHY=instruction:<file>` (`WHY=contract:<screen>` when the contract export is what moved), MUST
  hold the table's bars, and a template is edited on its screen's evidence.
- **FR-027**: The order MUST be 062, then 063 and 064, then 065, then 059–061; no screen reads
  another's live output.
- **FR-028**: A measurement screen at effort `high` MAY be taken once, on `03-lullaby`, for
  `CALIBRATION_QUESTIONS` only, as `WHY=new-model:claude:claude-sonnet-5-5` with a pinned
  `MODELS=<file>`, reported and never routed (HANDOFF's ceiling; founder, 2026-10-07).

**The run**

- **FR-029**: The run of record MUST be `make instruction-eval HOST=claude WHY=marks:9
  MODELS=exported`, spent once after all seven templates pass their screens and all seven r3
  entries exist (the Waits), at `claude-sonnet-5-5` / `medium` on the standard tier and Haiku on
  the light tier, the judge at the CLI's own default. `why.py` MUST NOT change.
- **FR-030**: `README.md` and `AGENTS.md` MUST state the v9 gate — eight marks, the new
  denominators, the three unscored screens, the rescore refusal — and the run of record when spent.

### Key Entities

- **Mark**: a named bar in `marks.toml` with the screens it reads, how it is measured (code; the
  judge for ties; the aggregate) and `measured`/`met` on every verdict; eight at v9.
- **JudgementCall**: one numbered, append-only sentence in `marks.py`; 36 at v9, none struck.
- **Registry**: keel-cloud's 25-dimension export, the golden for `dimension_coverage` and
  `option_validity`, the source of every control, code, bin, template and compare rule; checked
  against seven invariants before a case is built.
- **CorpusEntry (r3)**: one hand-worked project — context, mechanism, persona, 25 typed founder
  answers, the plan, people with a gate answer, story, chip, golden anchoring and picks by
  dimension, and the standings and vector verdicts every consumer reproduces; hashed, read only.
- **Plan**: the respondent items by part, derived by code from `founder_calibration` and
  `asked_in_v1`; the respondent denominator of `dimension_coverage`.
- **Screen**: one subject — a case kind, its context builder, contract, class, scorer (or none)
  and `-k` needle; eight at v9, three unscored.
- **Scorecard**: per-case evidence and totals for every mark, with the spread (call 7); the
  register beside it, rendered, unscored.
- **Bundle**: a run directory — `manifest.json` (the `WHY`, models, efforts, corpus digests),
  scorecard, verdict, register; carries its `marks_version` forever.
- **Certificate**: the one `WHY=marks:9` bundle, green on all eight marks, named in `README.md` as
  the run of record and the table routing v9 lands on.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `MARKS_VERSION` 9, 36 judgement calls numbered 1–36, none missing or struck, 1–27
  unchanged byte for byte.
- **SC-002**: `make unit` green, with r3 fixtures for the loader, the registry invariants, the four
  new scorers, the five-mark brief, the models classes and the rescore refusal.
- **SC-003**: `make instruction-eval DRY=1 K=03-lullaby` builds 19 cases at N=1 (3 + 3 + 3 + 9 + 1,
  plus the `COMPARE` row; Jonas's chipped story builds none), prints every prompt, makes **zero** calls, spends **$0**, and reports
  `compare_correctness` measured at **28 of 28**.
- **SC-004**: Every bundle under `runs/` whose manifest says `marks_version < 9` — the v8 record
  `runs/20261001T043420Z-instructions` first — is refused by `rescore.py` **by name**.
- **SC-005**: All seven entries carry `revision: 3`, `check_corpus.py` is green on each, and
  `GoldenCorpusTest` reproduces every standing and vector verdict (175 + 21 checks).
- **SC-006**: 062's screen: 9 calls; `dimension_coverage` 1.00, `option_validity` 1.00 over 75,
  `no_leak` 1.00 over 27, `shape_refusals` 0, `rule_refusal_rate` 0 of 9.
- **SC-007**: 063's screen: 9 calls; coverage 1.00 over 69 items, validity 1.00 over 69, `no_leak`
  1.00 over 93 sweeps, `shape_refusals` 0, rate 0 of 9.
- **SC-008**: 064's screen: 27 calls; `anchoring_accuracy` ≥ 0.90 over 27, `guessed_precision` and
  `guessed_recall` reported, `missing_ids` and `extra_ids` empty.
- **SC-009**: 065's screen: 3 calls, `brief_paragraphs` 3 of 3 on five marks; 059–061: 3 calls
  each, `shape_refusals` 0, rate 0 of 3, rendered.
- **SC-010**: A full screen of `03-lullaby` at N=3 is **57 calls** and comes back `passed: false`
  with the other six entries unmeasured — a screen is never a run of record.
- **SC-011**: `WHY=marks:9` earns the full run; on a screen it is refused with the policy; no `WHY`
  still refuses at the door; `DRY=1` needs none.
- **SC-012**: **The run of record is green on all eight marks at `MARKS_VERSION` 9**, `MODELS=exported`,
  ≈ 420 cases at N=3 less three per chipped story (≈ 300 light-tier `INTERPRET` reads over gate-yes
  people with a typed story), `shape_refusals` 0, `rule_refusal_rate`
  ≤ 0.02 over ≈ 510 judged answers, `compare_correctness` 196 of 196, `judged_fraction` reported;
  bundle, time and price in `README.md` beside the v8 record (414 cases, 3 h 11 m, $15.41) and, if
  anything surprised, in `runs/DRIFT.md`.

## Assumptions

- **A-1** The anchor read keeps `INTERPRET`: constant, class `reading`, tier light, case ids
  `<entry>/INTERPRET/<person>/run<N>`. No `ANCHOR_READ` anywhere (settled 2026-10-06).
- **A-2** `CONTEXT_INTERPRET`, `PROBLEM_INTERPRET`, `SOLUTION_MECHANISM` are rendered unscored and
  feed `rule_refusal_rate`/`shape_refusals` only; they run on every screen and the full run
  (marks §8.9 closed by the founder 2026-10-07 on the side of measuring the rate).
- **A-3** `RESPONDENT_QUESTIONS` runs at Lock, one job per part (+ one for the B2B link, charged;
  founder, 2026-10-07); the eval builds the plan by code and hands each part its slice, as
  production will. `CALIBRATION_QUESTIONS` is one constant, three jobs (founder, 2026-10-07).
- **A-4** Routing stays v8 until the certificate; the ceiling is `claude-sonnet-5-5` at `medium`;
  `CONTEXT_INTERPRET` is light (founder, 2026-10-07); effort `high` is FR-028's one measurement
  screen, never routed, never the fix.
- **A-5** The B2B entry is `05-paidly` with `agency` as decision-maker; `02-compliancelog` is the
  alternative. A proposal the r3 work decides, not a clarification.
- **A-6** The Lullaby worked example is the registry's `lullaby` objects where marks §5's excerpt
  differs (Prevalence 6-to-8 not 8-to-10; Duration `NOT_HOLDING_UP` median 11 over 7 anchored, not
  `PEOPLE_DISAGREE` median 20 over 8; Severity `PEOPLE_DISAGREE`; current solution
  `NOT_HOLDING_UP`); the PROBLEM verdict is `NOT_HOLDING_UP`, deciding `problem.duration`. Signed
  (founder, 2026-10-07, decision 8).
- **A-7** `problem.importance` compares by `ordinal_band` with the registry's share-to-band mapping
  (biggest ≥ ½ · top_three ¼–½ · middle 1/10–¼ · minor 1/25–1/10 · negligible below), not marks
  §2.5's `choice_majority` row. Signed (founder, 2026-10-07, decision 9).
- **A-8** `models.py` classes are `context`, `frame`, `calibration`, `respondent`, `reading`,
  `brief`; marks §6's `interpret`/`mechanism`/`anchor_read` names are superseded.
- **A-9** keel-cloud 058 gives the three new `JobClass`es rows at the ceiling in whatever table
  version its own tests require; existing classes' numbers do not move — that is what *routing
  stays v8* means. Until that export exists, a screen pins them with `MODELS=<file>`.
- **A-10** Screens of 9 or 30 cannot separate a fixed fault from a lucky sample (056 A-1, A-3); a
  screen shows the template did not fail on the smoke's entry. The full run is the certificate.

## Decisions applied (2026-10-07)

The founder's decisions consumed by this spec, by number: **1** (questions at Lock — A-3), **2**
(one `CALIBRATION_QUESTIONS` constant — A-3), **3** (`CONTEXT_INTERPRET` light — A-4, 059's row),
**5** (chipped story `GUESSED` by code; Lullaby's `INTERPRET` denominator 9 — FR-016, FR-017,
US3.4, 064's row, SC-003, SC-008, SC-010, SC-012), **8** (split direction rule — FR-007, FR-018,
A-6), **9** (compare parameters as marks §2.5 — FR-018, A-7), **12** (Urgency and Retention
calibrated, `NOT_ASKED_YET` — unchanged, 25 of 25 coverage), **14** (gate-No answers nothing
more; commercial Lullaby examples at n ≤ 10 — FR-007), **15** (`rule_refusal_rate` 0.02 —
FR-020), **16** (Hugo answers No — FR-011; `01-countly` leaves out `problem.severity` — FR-009;
one brief paragraph per project — FR-019; interpretation screens on every screen — FR-021, A-2),
**17** (`compare_correctness` in the eval and `GoldenCorpusTest`; `no_leak` ties = inflection
collisions only — FR-018, FR-015), **18** (one high-effort measurement on
`CALIBRATION_QUESTIONS` / `03-lullaby` — FR-028). Decisions 4, 6, 7, 10, 11, 13 reach this spec
only through the registry export it reads. No `[NEEDS CLARIFICATION]` remains in this spec.
