# Tasks: marks v9, corpus revision 3, and the run that certifies the vectors

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Branch**: `029-marks-v9-vectors`

**Input**: plan.md, research.md (R1–R17), data-model.md, contracts/ (`marks-v9.toml`, `marks-v9.md`,
`dimension-registry.yaml`, `screen-shapes.md`, `models-screen.json`), quickstart.md (S0–S4).

**Tests**: requested — SC-002 names the fixtures (*the loader, the registry invariants, the four
new scorers, the five-mark brief, the models classes and the rescore refusal*), and this repository
tests its scorers with fixtures a person can check by hand. **Tests first within every phase, and
each phase's tests land in the commit of the phase they certify** (025 D11), so `make unit` is
**green at every commit on this branch** — with the one named exception below.

**The named exception.** T051 asserts the r3 shape against keel-cloud's **real** seven files, and
the moment keel-cloud's r3 commit lands every test here that reads the r2 shape of those files is
red (`tests/test_corpus_script.py`'s shape assertions). The rule this repository works to (AGENTS.md:
*nothing committed → a run can never be green against a corpus that moved*; 025 plan §2) is that
the red is **correct and short**: T012 and T016 land in **one commit**, T051 lands in the commit
after keel-cloud's Lullaby r3, and the window is never closed with a fixture copy of the corpus.

**Nothing below spends a model call except T028's siblings and T038, T045, T049, T050, T055** —
the screens and the run of record — and those are the founder's to type, in the order FR-027
fixes. `DRY=1` (T028) spends nothing.

**Format**: `- [ ] [TaskID] [P?] [Story?] Description with file path`. `[P]` = parallelisable
(different files, no dependency on an unfinished task). `[USn]` = the spec's user story.

## Phase 1: Setup (read, pin, fixture)

**Purpose**: the inputs read once and the fixtures every later phase tests against.

- [X] T001 Read, in full, before writing a line: `contracts/marks-v9.md` §1–§8, `contracts/marks-v9.toml`, `contracts/dimension-registry.yaml` (header, `common`, the `problem.*` entries, `checks`), `contracts/screen-shapes.md`, `phase0-reconciliation.md` §B (keel-cloud-docs drafts; decisions 5, 8, 9, 14, 15, 16, 17), `HANDOFF.md` §4; this repository's `instructions/*.py`, `tests/test_instruction_*.py`, `specs/025-one-occasion-marks/{plan,tasks}.md`; the frozen `03-lullaby.yaml` (r2, read only). Record the `make unit` baseline count at `a673a67` as Discovered D1 in `specs/029-marks-v9-vectors/tasks.md`.
- [X] T002 When keel-cloud 058 lands: re-read its actual `screenContracts compare` CLI, its `dimension-registry.json` export and its `ScreenContractTool` case kinds against `specs/029-marks-v9-vectors/contracts/screen-shapes.md` §2, §5, §6; correct **this feature's** contracts page and research R3/R4/R10, never the sibling; record the diff as Discovered.
- [X] T003 [P] Extract judgement calls 1–27 once from `master` (`git show 0165017:instructions/marks.py`, the module docstring from `1.` to the end of `27.`) into `tests/fixtures/marks/calls-1-27.at-0165017.txt`, byte for byte, for SC-001.
- [X] T004 [P] Write `tests/fixtures/registry/slice.yaml`: a hand-sized 25-key registry in `contracts/dimension-registry.yaml`'s shape (Lullaby values; every `founder.normalized`, `respondent.*`, `answers.*`, `weight`, `order`), passing all seven invariants, and `tests/fixtures/registry/broken/` with one file per invariant that fails exactly it.
- [X] T005 [P] Write `tests/fixtures/corpus/09-fixture-r3.yaml` (data-model §2: `revision: 3`, 12 people — 2 `recency: no`, 1 `chip: cant_recall`, 1 vague `GUESSED`, 8 `ANCHORED`; `founder_calibration` on 25 keys with two `unsure`; `respondent_questions` 8/9/6; `expected.standings` on 25; `vector_verdicts`) and `tests/fixtures/corpus/10-fixture-r3-b2b.yaml` (`persona.decision_maker: {role: buyer}`). Neither is a corpus entry; values are invented and small.
- [X] T006 [P] Write `tests/fixtures/compare/09-fixture.agree.out.json` (an engine output matching `09-fixture-r3.yaml`'s `expected` on all 28 marked keys, with `belief_sentence` and counts), `tests/fixtures/compare/09-fixture.disagree.out.json` (two rows wrong: one `status`, one `deciding`), and `tests/fixtures/runs/v8-bundle/{manifest.json,scorecard.json}` (`marks_version: 8`, the v8 record's shape) for the rescore refusal.

---

## Phase 2: Foundational (blocking prerequisites)

**Purpose**: the ruler, the registry, the loader and the module map every story reads. No story
starts until T007–T017 are green.

**⚠️ CRITICAL**: T012 and T016 land in **one commit** (the harness readers go red the moment the
loader reads r3 only — research R14).

- [X] T007 Write `tests/test_instruction_text.py` (the `normalise`/`normalise_phrase` tests carried over from `tests/test_instruction_align.py` unchanged; `stems` on `listens/listened/listening → listen`, `classification → classif`, `cards → card`; `STOPLIST` drops `the, a, when, it, them…`; `content_words`), then `instructions/text.py` to make it green.
- [X] T008 Rewrite `tests/test_instruction_marks.py`: `MARKS_VERSION == 9`; the docstring's call numbers are exactly the set 1–36, none twice; calls 1–27 equal `tests/fixtures/marks/calls-1-27.at-0165017.txt` byte for byte; 28–36 are each marked `**v9**` and carry their key phrase (`New subjects`, `retired`, `absolute`, `fixes the codes`, `golden mechanism`, `One anchoring judgement`, `spends nothing`, `no_claim_words`, `keeps 0.02`); `DEFAULTS == load()` with exactly the eight keys and **no** `golden_belief_recall`; `instructions/marks.toml` equals `specs/029-marks-v9-vectors/contracts/marks-v9.toml` byte for byte; `judge()` on a totals dict with one mark unmeasured returns `passed: False` and `measured: False` on that row.
- [X] T009 `instructions/marks.py`: `MARKS_VERSION = 9`; calls **28–36** appended verbatim from `contracts/marks-v9.md` §3 (one numbered paragraph each, prefixed `**v9**`, 33 carrying *amended 2026-10-07*); `DEFAULTS` = the eight keys; `judge()` returns eight rows — `dimension_coverage`, `option_validity`, `no_leak`, `anchoring_accuracy`, `compare_correctness`, `refusals` (rate), `shape_refusals`, `brief_paragraphs` — each `{value, mark, measured, met}`, unmeasured never met, `golden_belief_recall` gone.
- [X] T010 `instructions/marks.toml` ← `cp specs/029-marks-v9-vectors/contracts/marks-v9.toml instructions/marks.toml` (FR-002; T008 holds the bytes).
- [X] T011 Write `tests/test_instruction_registry.py` (loads `tests/fixtures/registry/slice.yaml`; `slice("PROBLEM")` is 9 in `order`; `plan_keys` per part on a calibration with two `unsure` keys; each `broken/` file refuses naming its invariant and key; `contract.read` on an export directory without `dimension-registry.json` raises `ContractUnavailable` naming the file and keel-cloud 058), then `instructions/registry.py` (`Registry`, `Dimension`, `check_invariants`, `RegistryUnavailable`) per data-model §1.
- [X] T012 Write `tests/test_instruction_corpus_r3.py` (on `09-fixture-r3.yaml`: `Entry.plan() == {1: 8, 2: 9, 3: 6}`; `vocabulary()` holds the mechanism stems and none of the problem's; the inflection ledger carries the one planted collision; `readable()` is the 9; `gate_yes()` is the 10; `people()` is 12; `b2b()` false, true on `10-fixture-r3-b2b.yaml`; every refusal of data-model §2 raised by entry and key from a one-line mutation of the fixture; `sha256` and `verify_unchanged()` unchanged), then `instructions/corpus.py`: the r3 `Entry`/`Person`, `plan()`, `vocabulary()`, `mechanism_one_liner()`, `readable()`, `gate_yes()`, `b2b()`, `_check_revision`, `_check_keys(registry)`; `beliefs`, `questionnaire`, `GoldenBelief`, `anchors_for`, `anchor`, `beliefs_for`, `Person.anchors/written` deleted; docstring note 3 rewritten for r3. **Same commit as T016.**
- [X] T013 `instructions/contract.py`: `SCREEN_CONTEXT_INTERPRET`, `SCREEN_PROBLEM_INTERPRET`, `SCREEN_SOLUTION_MECHANISM`, `SCREEN_CALIBRATION`, `SCREEN_RESPONDENT`, `SCREEN_INTERPRET` (= `INTERPRET`, A-1), `SCREEN_COMPARE`, `SCREEN_BRIEF`; `MODEL_SCREENS` (the seven); `ExportedContract.registry: Registry | None`; `read()` loads `dimension-registry.json` through `registry.py` and refuses by name when absent; `SCREENS_ASSUMPTIONS`/`SCREEN_QUESTIONS` deleted. `instructions/instruction.py`: `STEMS` += `context-interpret`, `problem-interpret`, `solution-mechanism`, `calibration-questions`, `respondent-questions` (the dormant stems stay: keel-cloud keeps the files). T011's contract test goes green.
- [X] T014 Extend `tests/test_instruction_models.py` (a table naming the six classes parses; keel-cloud's v8 shape — `frame, assumptions, reframe, reading, brief, questions`, `version: 8` — refuses with `ModelsUnavailable` naming `context`, `calibration`, `respondent` **and** `version 8`; `specs/029-marks-v9-vectors/contracts/models-screen.json` parses and resolves `calibration → claude-sonnet-5-5 / medium`, `reading → haiku / None`; `models_used`/`efforts_used` report exactly six), then `instructions/models.py`: `CLASSES` = the six + the three dormant tolerated (research R5); `KIND_TO_CLASS` for `CONTEXT, FRAME, CALIBRATION, RESPONDENT, READING, BRIEF`; `SCREEN_TO_CLASS` per FR-023; `REPORTED_CLASSES` the six; the *missing* check over the six, naming the table version.
- [X] T015 [P] Extend `tests/test_instruction_why.py`: `why.check("marks:9", screen=False, dry_run=False) == {"event": "marks", "version": 9}` and `marks:9` refused on a screen. `instructions/why.py` is **not edited** (FR-029).
- [X] T016 `tests/test_corpus_script.py`: the shape assertions on the real seven files and the `CANNED` r2 fixture path **skip by name** — `pytest.skip("the corpus is at revision 3 (spec 029); the journey's readers of the r2 shape are spec 030-journey-vectors' — Open item O-1")` — when `instructions.corpus` is the r3 loader; `harness/corpus_script.py`'s `load()`/`entry_from_file()` raise `CorpusError` with the same sentence rather than failing twenty steps in; `evals/corpus_scenario.py` and `evals/test_s012_journey_through_a_host.py`'s `ENTRY=` prelude surface that refusal by name. **No other line of the harness changes.** Same commit as T012; the founder's decision on O-1 is recorded here when taken.
- [X] T017 `instructions/align.py` deleted (call 29); `tests/test_instruction_align.py`, `tests/test_instruction_reads.py` and `tests/test_instruction_questions.py` removed **with the reason written** in `instructions/text.py`'s docstring (what moved where: `normalise` → `text.py`; `resolve_reads`, `FIELDS`, the structural matcher → retired with the subject they aligned; `QUESTIONS` → no screen) and in Discovered; `tests/test_instruction_modules_import.py`'s `MODULES` loses `align` and gains `compare`, `registry`, `text`; its `_SCORECARD` fixture becomes the v9 totals shape of data-model §6 so `render_report`/`render_register` smoke-render at v9. `make unit` green.

**Checkpoint**: the ruler is v9, the registry loads and refuses, the corpus loads r3 and refuses r2, the module map is final. `make unit` green.

---

## Phase 3: User Story 1 — the ruler moves, the corpus follows, and the engine is read for free (Priority: P1) 🎯 MVP

**Goal**: every context builder, `build_cases` in FR-016's order, `compare.py` shelling keel-cloud's
engine at zero spend, `rescore.py` refusing v8, and `make instruction-eval DRY=1 K=03-lullaby`
printing every prompt and writing `compare_correctness` 28 of 28.

**Independent Test**: `make unit` green on the r3 fixtures; quickstart S1 and S2 (needs the Waits
W2 and W3-Lullaby; until then `compare_correctness` is unmeasured **by name** and the DRY verdict
says so).

### Tests for User Story 1

- [X] T018 [P] [US1] Rewrite `tests/test_instruction_context.py`: the seven builders fill the exporter's keys in the exporter's order from `09-fixture-r3.yaml` + `slice.yaml`; `build_calibration(entry, "PROBLEM", registry)` carries the nine-entry slice with exactly `screen-shapes.md` §2's thirteen fields and **no** `mechanism`/`solution` key (US2.1); `build_respondent(entry, 1, plan)` carries no `mechanism` and no founder answer, part 2 carries `mechanism`; `build_interpret` carries `invitation_id` and `story` and no `anchors`/`stage`; `build_brief` carries `vectors[]` with `belief_sentence` from `founder_calibration` and `verdict` from `vector_verdicts`; `build_context_interpret` carries nothing from `solution_mechanism`; `earlier_lines`, `build_questions`, `anchors_for`, `roles_for`, `measurements_for`, `claims_for` no longer exist.
- [X] T019 [P] [US1] Rewrite `tests/test_instruction_prompts.py`: `build_cases` on `09-fixture-r3.yaml` at `n_runs=1` emits, in order, `CONTEXT_INTERPRET`, `PROBLEM_INTERPRET`, `SOLUTION_MECHANISM`, `CALIBRATION_PROBLEM/SOLUTION/COMMERCIAL`, `RESPONDENT_PART1/2/3`, nine `INTERPRET/<person>` (none for the two gate-No or the chipped person), `COMPARE` (no index, empty payload, no prompt), `BRIEF` — **19 model cases + 1**; the B2B fixture adds `RESPONDENT_B2B`; `-k 09-fixture/INTERPRET` selects nine and no interpretation; each kind word of research R6 selects its kind; a needle matching nothing is reported and builds no case; every payload carries the instruction bytes and keel-cloud's contract for its screen.
- [X] T020 [P] [US1] Write `tests/test_instruction_compare.py`: `compare.build_input(entry, registry)` is `screen-shapes.md` §5's object from r3 only (25 calibration keys, 12 answers, `rough` and `chip` preserved, nothing from `expected`); `compare.diff(entry.expected, agree.out)` scores 28 of 28 and reports every count diff empty; on `disagree.out` scores 26 of 28 naming the two keys; a fake `run` returning non-zero makes the mark **unmeasured** with the engine's stderr tail and keel-cloud 058 named; both files are written under `runs/<bundle>/compare/`.
- [X] T021 [P] [US1] Write `tests/test_instruction_rescore.py`: on `tests/fixtures/runs/v8-bundle` `rescore.main` returns 2 and prints the bundle name, `marks_version 8` and *answered on screens v9 does not have, against corpus r2*, touching no file; on a v9 fixture bundle it writes `scorecard-v9.json` beside and never over `scorecard.json`.

### Implementation for User Story 1

- [X] T022 [US1] `instructions/context.py`: `build_context_interpret`, `build_problem_interpret`, `build_solution_mechanism`, `build_calibration`, `build_respondent`, `build_interpret`, `build_brief`, each filling `keys` in the exporter's order from r3 and the registry per `contracts/screen-shapes.md` §2; `market_of`, `invitation_id`, `TAP_ENUM`-free; everything stage-shaped deleted. T018 green.
- [X] T023 [US1] `instructions/prompts.py`: `Case.kind` ∈ `{CONTEXT, FRAME, CALIBRATION, RESPONDENT, READING, COMPARE, BRIEF}`; `build_cases(entry, exported, instructions_by_screen, executor_module, *, n_runs, host)` in FR-016's order and ids, iterating `entry.readable()` for `INTERPRET`, adding `RESPONDENT_B2B` when `entry.b2b()`, one `COMPARE` row per entry carrying `compare.build_input`; `render` untouched. T019 green.
- [X] T024 [US1] Write `instructions/compare.py` (`build_input`, `run(keel_cloud, entry_input, in_path, out_path, *, timeout_s=600.0)` shelling `./gradlew -q screenContracts --args="compare <in> <out>"` with `contract.export`'s `cwd`/error discipline, `diff(expected, out) -> CompareScore{checks, agreed, mismatches, reported_diffs, measured, reason}`, `EngineUnavailable`). T020 green.
- [X] T025 [US1] `instructions/score.py`: `score_compare(case, entry, compare_score)`; `totals(calibration_scores, respondent_scores, interpret_scores, compare_scores, *, brief_scores, errored, refusals_by_rule, shape_refusals, schema_invalid, refusals_measured, refusals_shown, judge_calls, leak_hits, leak_judged)` with data-model §6's keys; `spread` over the new per-case metrics; `score_assumptions`, `score_reading`, `AssumptionScore`, `FIELDS` deleted (`score_calibration`, `score_respondent`, `score_interpret` arrive in US2/US3 and `totals` takes empty lists until then).
- [X] T026 [US1] `instructions/run.py`: `SCREENS` = the seven model screens; `_all_cases` with research R6's needles and the *no case matches* line; `COMPARE` run at build time for every selected `COMPARE` row (DRY and real) with both files kept in the bundle; `_dry_run` writes `scorecard.json`/`verdict.json` (compare measured, every model mark unmeasured, `passed: false`) and prints the eight screens' keys and one prompt per kind; the printed per-case line per kind; `manifest` gains `registry_version`. `instructions/report.py`: `copy_contracts` copies `dimension-registry.json`; `render_report`'s mark table = the eight v9 rows (`_mark_row` per row, `compare_correctness` as *agreed of checks*, `refusals` as a rate); `render_register` renders a `COMPARE`-only bundle without raising.
- [X] T027 [US1] `instructions/rescore.py`: read `scorecard.json["marks_version"]` first, refuse `< 9` by name with the reason, exit 2; the v9 path re-scores every kind from `cases/**/envelope.json`, re-runs `compare.py` from the bundle's own `compare/*.in.json`, reads the registry from the bundle's `contracts/dimension-registry.json`, writes `scorecard-v9.json` beside. T021 green.
- [X] T028 [US1] **`make instruction-eval DRY=1 K=03-lullaby`** on keel-cloud 058's branch with Lullaby at r3 (quickstart S1): 19 cases + `COMPARE`, zero calls, `$0`, `compare_correctness` **28 of 28**, every refusal of S1 seen once by name; then `python -m instructions.rescore runs/20261001T043420Z-instructions` refused by name (S2). Record both in Discovered. Until W2/W3 land, record instead the DRY verdict naming the unmet prerequisite.

**Checkpoint**: US1 is the MVP — the rubric is v9, r3 loads, the engine is read for free, and a v8 bundle cannot be re-scored. `make unit` green.

---

## Phase 4: User Story 2 — the calibration screen passes on Lullaby (Priority: P2)

**Goal**: `dimension_coverage`, `option_validity` and `no_leak` (sweep A) as code against the
registry; the judge's one question; the aggregate asked by case kind; the calibration register;
keel-cloud 062's screen green at N=3.

**Independent Test**: `make unit` green on the calibration fixtures; quickstart S3's first command
(needs W1 and keel-cloud 062): 9 cases, three marks at 1.00, `shape_refusals` 0, rate 0 of 9.

### Tests for User Story 2

- [X] T029 [P] [US2] `tests/test_instruction_score.py` — `score_calibration` on `slice.yaml`: coverage 9 of 9 only when every slice key appears exactly once in `order` (call 30), a doubled, a missing and a foreign key each fail the case; `option_validity` fails on **each** of marks §2.2's calibration checks made to fail once — count ≠ `len(codes)`, a code out of registry order, a repeated code, a `model_written` set outside 4–6 or missing the fixed code the rule names, numeric spec ≠ registry, `belief_phrase` empty or `== label` after `normalise`, `{value}` not exactly once, a label matching `/not sure|don't know|unsure/i`, `options` on a numeric control, `problem.prevalence` without five contiguous fifths and the 7-night window; evidence per fault.
- [X] T030 [P] [US2] Write `tests/test_instruction_leak.py`: on `09-fixture-r3.yaml` sweep A over nine PROBLEM questions + options — a stem hit is a fault with the word named; a ledger (inflection) hit goes to a fake judge once, cached on repeat, answered `SAME` = fault, `DIFFERENT` = clean, and counts in `leak_judged`/`judged_fraction`; a SOLUTION calibration question is not swept; `judged_fraction` = judged hits / all hits.
- [X] T031 [P] [US2] Write `tests/test_instruction_judge.py`: `reveals_solution` asks exactly marks §2.3's question with the mechanism one-liner, returns `True` on `SAME`, `False` on `DIFFERENT`/`None`, caches by question, records every call; `same_answer_space`, `same_expected_option`, `pick` no longer exist; `tests/test_instruction_judge_isolation.py` untouched and green.
- [X] T032 [P] [US2] Rewrite `tests/test_instruction_validate.py`: `build_batch` emits `screen-shapes.md` §6's entry for a `CALIBRATION_QUESTIONS` case (`vector`, `registry_slice` keys in order, no founder answer) and one per other kind; a `COMPARE` case is never batched; `shapes_taken` reads one marker per screen off a fixture copy of `ScreenContractTool.java`; an unknown kind leaves `rule_refusal_rate`/`shape_refusals` unmeasured **by name** for that kind only, with 058 named — never a warning, never a refusal.
- [X] T033 [P] [US2] Write `tests/test_instruction_report.py`: `register_blocks` per entry renders the 25 calibration questions in registry order beside `lullaby.founder_question` where the registry has one, the founder's `belief_phrase` and `belief_sentence`, and the three interpretations marked accepted/refused by rule id; the HTML carries no `✓`, `✗`, `score`, `met` or `mark` text (call 10).

### Implementation for User Story 2

- [X] T034 [US2] `instructions/judge.py`: `reveals_solution(question_text, mechanism_one_liner, *, context="")`; the three old questions deleted; `_ask`, cache, `calls`, `judge_env`, `JUDGE_UNSET_ENV`, `NoJudge` unchanged. T031 green.
- [X] T035 [US2] `instructions/score.py`: `CalibrationScore` and `score_calibration(case, entry, registry, result, *, judge, failed)` — coverage (call 30), validity (every §2.2 calibration check, evidence per fault), sweep A through `text.stems` and `entry.vocabulary()` with ledger ties to `judge.reveals_solution`; `totals` fills `calibration_*`, `dimension_coverage`, `option_validity`, `no_leak`, `leak_hits`, `leak_judged`, `judged_fraction`. T029, T030 green.
- [X] T036 [US2] `instructions/validate.py`: `build_batch` per `screen-shapes.md` §6 for all seven model kinds; `_SHAPE_MARKERS` per screen constant; `_PREREQUISITE` per screen naming keel-cloud 058 and the two marks it leaves unmeasured; `_STAGE_SCREEN`, `_measurements`, `_earlier_beliefs` deleted; `fold_in` unchanged. T032 green.
- [X] T037 [US2] `instructions/run.py`: score `CALIBRATION` cases, hand them to the aggregate, fold the verdict; the printed line *coverage a/b · validity c/d · leak e/f (judged g)*. `instructions/report.py`: `register_blocks` for the calibration block and the three interpretations (`screen-shapes.md` §7.1–§7.2). T033 green.
- [ ] T038 [US2] **keel-cloud 062's screen** (the founder's; spends ≈ $1): `make instruction-screen K=03-lullaby/CALIBRATION HOST=claude N=3 WHY=instruction:calibration-questions.md MODELS=specs/029-marks-v9-vectors/contracts/models-screen.json` → 9 calls, `dimension_coverage` 1.00 (25 of 25 ×3), `option_validity` 1.00 over 75, `no_leak` 1.00 over 27, `shape_refusals` 0, rate 0 of 9, `passed: false` with the rest unmeasured (SC-006, SC-010). Anything that surprised → `runs/DRIFT.md`; a miss → 062's own ledger, never a mark here. FR-028's one `high` measurement may be taken here, reported and never routed.

**Checkpoint**: US1 + US2 — the first template a founder meets is proven against the registry. `make unit` green.

---

## Phase 5: User Story 3 — the respondent and the reader are screened (Priority: P3)

**Goal**: `score_respondent` (plan denominators, validity on the respondent side, sweeps A and B),
`score_interpret` keyed on the person with the chipped story outside every denominator; the
respondent and reveal register blocks; keel-cloud 063's and 064's screens green.

**Independent Test**: `make unit` green on the respondent/interpret fixtures; quickstart S3's
second and third commands (need W1, 063, 064): 9 cases with the three marks at 1.00; 27 cases with
`anchoring_accuracy` ≥ 0.90 and the confusion matrix beside it.

### Tests for User Story 3

- [X] T039 [P] [US3] `tests/test_instruction_score.py` — `score_respondent` on `09-fixture-r3.yaml` + `slice.yaml`: coverage per part = `Entry.plan()` (8/9/6) exactly once each (US3.1); validity fails on each respondent-side check made to fail once — control ≠ `respondent.control`, a founder code missing, fewer than two distractors, `something_else` not last on a set, a fixed scale with an extra word, a founder number among numeric band edges, `chips` ≠ `respondent.chips`, `anchor` ≠ `respondent.anchor`, `problem.importance`'s own item first; sweep A on the 8 Part-1 items, sweep B (the founder's label, phrase or number for dimension *d* in item *d*) on all 23 across parts; a `RESPONDENT_B2B` case on the B2B fixture scores the six part-3 items with no context card and no reveal.
- [X] T040 [P] [US3] `tests/test_instruction_score.py` — `score_interpret` keys on the person: a result `{invitationId, anchoring}` for each of the nine readable people scores against `answers[].anchoring`; the confusion matrix, `guessed_precision`, `guessed_recall`, `missing_ids`, `extra_ids` keyed by person; a chipped person never appears in any count (`chipped_skipped` = 1); a result carrying `stage` or `anchorId` is neither read nor refused (US3.4); `anchoring` outside the two words is a shape refusal counted at zero; `totals` rolls `anchoring_accuracy` over `people_answered`.
- [X] T041 [P] [US3] `tests/test_instruction_report.py`: the respondent block — 23 items beside the plan row `key · part · control · codes`, the reveal title/body between parts 1 and 2, `RESPONDENT_B2B` as its own block; still no score word anywhere.

### Implementation for User Story 3

- [X] T042 [US3] `instructions/score.py`: `RespondentScore` and `score_respondent(case, entry, registry, plan, result, *, judge, failed)` — coverage against `plan[part]`, validity (every §2.2 respondent check), sweep A on part 1, sweep B on every part with the founder's values read from `founder_calibration`; `totals` fills `respondent_*` and rolls `dimension_coverage`/`option_validity`/`no_leak` over both screens. T039 green.
- [X] T043 [US3] `instructions/score.py`: `InterpretScore` and `score_interpret(case, entry, person, result, *, failed)` — one judgement per person, `GUESSED` precision and recall (call 5), `missing_ids`/`extra_ids` by person; `instructions/run.py`: score `RESPONDENT` and `READING` cases, `chipped_skipped` counted from `entry.people()` − `entry.readable()` − gate-Nos and printed. T040 green.
- [X] T044 [US3] `instructions/report.py`: `register_blocks` for the respondent items, the reveal and the B2B link (`screen-shapes.md` §7.3). T041 green.
- [ ] T045 [US3] **keel-cloud 063's and 064's screens** (the founder's; spends ≈ $1 + ≈ $1): `make instruction-screen K=03-lullaby/RESPONDENT …WHY=instruction:respondent-questions.md…` → 9 calls, coverage 1.00 over 69, validity 1.00 over 69, `no_leak` 1.00 over 93 (SC-007); `make instruction-screen K=03-lullaby/INTERPRET …WHY=instruction:interpret.md…` → 27 calls, `anchoring_accuracy` ≥ 0.90 over 27 (24 `ANCHORED` / 3 `GUESSED`), precision and recall reported, `missing_ids`/`extra_ids` empty (SC-008). Surprises → `runs/DRIFT.md`.

**Checkpoint**: US1–US3 — every scored screen is proven on the entry the calibration was. `make unit` green.

---

## Phase 6: User Story 4 — seven entries, seven templates, one certificate (Priority: P4)

**Goal**: the five-mark brief; the real-file r3 shape tests across all seven entries; the v9 header
finalised; the gate text; 065 and 059–061 screened; the run of record spent once.

**Independent Test**: none that is free (spec). SC-005, SC-009, SC-011, SC-012; quickstart S4.

### Tests for User Story 4

- [X] T046 [P] [US4] Extend `tests/test_instruction_brief.py`: `no_claim_words` fails only on a sentence naming a `BAR_SET` or `NOT_TESTED_BY_DESIGN` dimension by `name` (case-folded) that carries one of `works, worked, effective, proves, proven, confirmed, will save, saves, validated, delivers`, and passes the same word in a sentence naming another dimension; `deciding_line` reads `vector_verdicts[v].deciding`; allowed `N of M` = `inside`/`outside` of `n` and every `optionCounts` row; `source_material` sweeps the eight `Status` words, `DEAL_BREAKER`, `SHAPES`, the three vector names and every dotted key; `BriefScore.met` is **all five or nothing**; one `BRIEF` case per entry, never per vector (FR-019).
- [X] T047 [P] [US4] Write `tests/test_corpus_r3_shape.py` against keel-cloud's **real** seven files through `instructions.corpus.load(load_config().keel_cloud)`: every entry `revision: 3`, 25 `founder_calibration` keys, `plan()` parts summing to ≤ 23, `expected.standings` on all 25, `belief_sentence` and `interpretations.problem` present (O-2/O-3); `03-lullaby` reproduces FR-007's statuses, drifts, the 12 / 6 / 3 / 1 / 1 / 2 totals and the three verdicts, has 12 people, `readable()` of 9, Hugo Laurent and Leo Martins `recency: no` with no story and no picks, Jonas Weber chipped `GUESSED`; `01-countly` leaves out `problem.severity` (FR-009); `05-paidly` (or `02-compliancelog`) carries `persona.decision_maker: {role}` and a B2B plan (FR-010); the seven digests differ from every v8 bundle's `corpus.sha256`. **Red until keel-cloud's r3 lands; one commit wide; never a fixture copy.**

### Implementation for User Story 4

- [X] T048 [US4] `instructions/brief.py`: `no_claim_words` as the fifth per-case mark; `deciding_line(vector_standing)` off `vector_verdicts`; `_coverage` against `vectors[].dimensions[]`; `ENUM_NAMES`, `CONTEXT_FIELD_NAMES` widened; `VERDICT_MARKERS` keyed by `Status`; `STAGE_LABELS` → vector names; `brief.totals` with `brief_by_mark` over five. T046 green.
- [ ] T049 [US4] `instructions/report.py`: the brief beside the standings table (`dimension · status · drift · n · median/counts`, `vector_verdicts` as header rows; `screen-shapes.md` §7.4); `instructions/run.py`: score `BRIEF` cases, the printed line over five marks. **Then keel-cloud 065's screen** (the founder's; ≈ $0.30): `make instruction-screen K=03-lullaby/BRIEF … WHY=instruction:brief.md …` → 3 calls, `brief_paragraphs` 3 of 3 on five marks, `shape_refusals` 0 (SC-009).
- [ ] T050 [US4] **keel-cloud 059–061's screens** (the founder's; ≈ $0.20 each): `K=03-lullaby/CONTEXT_INTERPRET`, `K=03-lullaby/PROBLEM_INTERPRET`, `K=03-lullaby/SOLUTION_MECHANISM`, each `WHY=instruction:<file>` → 3 calls, `shape_refusals` 0, rate 0 of 3, rendered on `register.html` (SC-009); a second `NEEDS_INPUT` shows as a refused `X3`/`P3`/`M3` in the rate.
- [X] T051 [US4] **The corpus revision for the other six entries — a keel-cloud commit on 058's branch, never a file here** (FR-008, FR-012, research R2): `01-countly` (leaves out `problem.severity`), `02-compliancelog`, `04-linerly`, `05-paidly` (B2B, `agency`), `06-repeatline`, `07-mulchrun`, each keeping `market`, `statements`, `roles` and its people, every verdict and drift hand-worked under FR-018's signed rules before `check_corpus.py` confirms counts, headers recording the revision, the date and this spec; `GoldenCorpusTest` green on 175 + 21 checks (SC-005). This task is ticked here when that commit's sha is recorded in Discovered; T047 goes green with it.
- [X] T052 [US4] The v9 header finalised (US4.2): the seven r3 digests and the corpus-wide `anchoring_accuracy` denominator (106 people less every gate-No and every chipped story — counted, not estimated; O-4) written as one dated paragraph at the top of `instructions/marks.py`'s module docstring **above** the call list (never a call, never a line of `marks.toml`, which stays byte for byte the draft — T008 holds it); `tests/test_instruction_marks.py` asserts the paragraph names seven digests.
- [X] T053 [US4] `README.md` and `AGENTS.md`: the v9 gate — eight marks, the new denominators (one judgement a person; every answer the aggregate judged; 28 compare checks an entry), the three unscored screens, the rescore refusal, `MODELS=exported` refusing until the table carries the three classes — and the Waits as they stand (FR-030). Before the run, so the run is read against the gate as written.
- [X] T054 [US4] Run `make instruction-eval DRY=1` (no `-k`) across all seven r3 entries: ≈ 140 cases at N=1 plus seven `COMPARE` rows, `compare_correctness` **196 of 196**, `$0`; then `make unit` green with T047. Record both in Discovered.
- [ ] T055 [US4] **The run of record — the founder's to type, once, after every Wait** (FR-029, SC-011, SC-012; quickstart S4): `make instruction-eval HOST=claude WHY=marks:9 MODELS=exported` with `CLAUDE_CODE_EFFORT_LEVEL` unset — ≈ 420–480 cases at N=3, ≈ 3 h, ≈ $15–20; `passed: true` on all eight marks at `MARKS_VERSION` 9, `shape_refusals` 0, rate ≤ 0.02 over ≈ 510 judged answers, `compare_correctness` 196 of 196, `judged_fraction` reported, `corpus.sha256` identical before and after. **A red mark is a finding, not a reason to run again.**
- [ ] T056 [US4] Whatever T055 found → `README.md` (the run of record for spec 029: bundle, cases, time, price, the eight values, beside the v8 record's 414 / 3 h 11 m / $15.41), `runs/DRIFT.md` (anything that surprised), and this file's Discovered. The certificate's name is what keel-cloud's routing v9 spec reads; `model-routing.json` is not touched here.

**Checkpoint**: the standing gate — *green at the current `MARKS_VERSION`* — means something again.

---

## Phase 7: Polish & cross-cutting

- [X] T057 [P] `specs/029-marks-v9-vectors/{spec,plan,research,tasks}.md` and `contracts/screen-shapes.md` corrected to what the work found (T002's diffs, O-1's decision, O-2/O-3's keys as landed, O-4's count) — the same *Discovered* discipline as 025.
- [X] T058 [P] `tests/test_instruction_modules_import.py`: the report and the register render from a v9 scorecard carrying one unmeasured mark and say so in words; every module under `instructions/` imports.
- [X] T059 Quickstart S0, S1 and S2 run end to end from a clean `make venv` and their outputs pasted into Discovered; S3/S4 left to the founder's record in T038/T045/T049/T050/T055.

---

## Dependencies & execution order

### Phase dependencies

- **Phase 1 (Setup)** → nothing; T003–T006 in parallel.
- **Phase 2 (Foundational)** → Phase 1. T007 first (text.py); T008–T010 together (the ruler); T011 → T012/T013 (the loader and the contract read the registry); **T012 + T016 in one commit**; T014, T015 in parallel after T013; T017 last.
- **Phase 3 (US1)** → Phase 2. Tests T018–T021 in parallel, then T022 → T023 → T024 → T025 → T026 → T027 → T028.
- **Phase 4 (US2)** → Phase 3 (needs `build_cases`, `totals`, the bundle). Tests T029–T033 in parallel; T034 → T035 → T036 → T037 → T038.
- **Phase 5 (US3)** → Phase 4 (shares `score.py`'s validity helpers and `validate.py`'s kinds). Tests T039–T041 in parallel; T042 → T043 → T044 → T045.
- **Phase 6 (US4)** → Phase 5 for T049/T050; T046–T048 may start after Phase 3; T051 is keel-cloud's and may land any time after T012; T052–T054 after T051; T055 after **every** Wait; T056 after T055.
- **Phase 7** → everything.

### User story dependencies

- **US1 (P1)**: Foundational only. Independently testable (`DRY=1`, zero spend) once W2 and W3-Lullaby exist.
- **US2 (P2)**: US1 (cases, totals, bundle). Independently testable on 062's screen once W1 and 062 exist.
- **US3 (P3)**: US2 (the validity helpers, the batch kinds). Independently testable on 063's/064's screens.
- **US4 (P4)**: US1–US3 and every Wait. Not free.

### The Waits, mapped to tasks

| Wait | Blocks | Until then |
|---|---|---|
| W1 registry + contract export (keel-cloud 058) | T028's real export, T038, T045, T049, T050, T055 | fixtures (T004); `contract.read` refuses by name |
| W2 the engine (058) | T028's 28 of 28, T054, T055 | `compare_correctness` unmeasured by name; T020 on fixture outputs |
| W3 corpus r3 — Lullaby first, then six (keel-cloud, 058's branch) | T028, T047, T051, T054, T055 | the loader refuses revision ≠ 3; T005's fixtures |
| W4 the seven templates (keel-cloud 059–065) | T038, T045, T049, T050, T055 | `instruction.read` refuses by name |
| W5 the run of record (the founder) | T055, T056 | routing stays v8; nothing spent |

### Parallel opportunities

- Phase 1: T003 ∥ T004 ∥ T005 ∥ T006.
- Phase 2: T014 ∥ T015 after T013.
- Phase 3: T018 ∥ T019 ∥ T020 ∥ T021 (four test files, four authors).
- Phase 4: T029 ∥ T030 ∥ T031 ∥ T032 ∥ T033.
- Phase 5: T039 ∥ T040 ∥ T041.
- Phase 6: T046 ∥ T047 ∥ T048 (brief tests, shape tests, brief code) while 062–064 are being screened.

## Parallel example: User Story 1

```sh
# the four US1 test files, together, before a line of implementation:
#   tests/test_instruction_context.py   (T018)
#   tests/test_instruction_prompts.py   (T019)
#   tests/test_instruction_compare.py   (T020)
#   tests/test_instruction_rescore.py   (T021)
# then, in order: context.py → prompts.py → compare.py → score.py → run.py/report.py → rescore.py
# then, free:
make instruction-eval DRY=1 K=03-lullaby
```

## Implementation strategy

**MVP first (US1 only).** Phases 1–3 deliver a v9 ruler, an r3 loader, an engine shim and a DRY run
that measures `compare_correctness` with **$0 spent** — and a v8 bundle that cannot be re-scored.
That is enough to prove r3 and 058's engine agree before a template is written, which is HANDOFF
§4's *marks before prompts* in one command.

**Incremental delivery.** US2 proves the registry-driven scorers on the template the registry
exists for; US3 proves the interview and the one judgement per stranger on the same entry; each
screen is one template, one entry, N=3, and its template is edited on its own evidence. US4 is the
paid phase and is ordered last for exactly that reason.

**Who does what.** Everything under `instructions/` and `tests/` is this branch's. The seven
templates, the registry, the engine, the export and all seven corpus files are keel-cloud's
(058–065), named by number wherever this file waits on them. The screens and the run are the
founder's to type, and are the only unticked boxes that should be left when the code is done.

## Discovered

What the code turned out to say that the spec, the plan or this file did not. Each entry names the
task it was found under. Nothing here is a change of mind about the design; it is what the work met.

- **D1 (baseline).** *(T001.)* `make unit` at `977b789` (= `a673a67` + plan and tasks, no code):
  **1401 passed** in 118 s. Taken in the worktree with `stack.toml`'s sibling paths pointed one
  level further up (`../../../../keel-*`, marked `skip-worktree`, never committed): the committed
  `../keel-cloud` resolves to `.claude/worktrees/keel-cloud` from a worktree, and every test that
  reads a sibling refuses at import there.
- **D2 (T004).** The seven `broken/` registry fixtures are **patches** of `slice.yaml`
  (`{base, invariant, key, path, value}`), not seven 800-line copies: one value changed each,
  applied by the test, and each fails exactly the invariant it names.
- **D3 (T005, r3 schema).** The golden plan carries **`problem.prevalence` itself** (`part: 1,
  control: gate_yes_no, codes: [yes, no]`): the registry asks it in Part 1 and counts it in the 8,
  so `respondent_questions` must hold it for `plan()` to equal the file (marks §5's excerpt leaves
  it as a comment). And `problem.importance`'s plan row carries **`own_item: <code>`**: both the
  engine (the share who picked the problem's own item, A-7) and `option_validity` (*never first*)
  need to know which code is the problem's, and nothing else in r3 says. A third ask of the r3
  writer beside O-2/O-3.
- **D4 (Phase 2 + US1, one commit).** Phase 2 could not be green on its own: the r3 loader removes
  `Entry.beliefs`/`questionnaire`, and every v8 builder, scorer and test (`context`, `prompts`,
  `score`, `brief`, `validate` and their tests, which import `GoldenBelief` and the r2 `Entry`)
  breaks with it. So Phase 2 and US1 land as one green commit, and two pieces tasks.md places later
  came forward with them because their v8 tests could not survive the r3 `Entry`: **`brief.py`'s
  v9 rewrite and its tests (T046, T048)** and **`validate.py`'s batch kinds and their tests (T032,
  T036)** -- `run.py` needs the batch to exist. Scoring of `CALIBRATION`/`RESPONDENT`/`READING`/
  `BRIEF` cases in `run.py` is still US2-US4's (T037, T043, T049).
- **D5 (T016, wider than named).** The r2-shape readers are not only `tests/test_corpus_script.py`:
  `tests/test_stranger_stories.py` (two module fixtures), `tests/test_s004_live_choices.py` (one
  fixture), four tests of `tests/test_journey_through_a_host.py` and one of
  `tests/test_policy_v8.py` read the real corpus through `harness.corpus_script` too. All skip **by
  the same O-1 sentence** through one helper, `tests/r2_corpus.py` -- 75 skipped, none deleted, none
  given a fixture copy. `harness/corpus_script.load()`/`entry_from_file()` raise `CorpusError` with
  the sentence; `evals/corpus_scenario.run` and S-012's `ENTRY=` prelude `pytest.fail` with it
  before a browser context or a project exists. No other line of the harness changed.
- **D6 (the cross-track arrangement of 2026-10-07).** Corpus revision 3 is this branch's to write
  but lives in keel-cloud's canon, which this branch may not touch. The r3 entries are recorded under
  `tests/fixtures/corpus-r3/` (README: to be moved verbatim at integration), and
  `instructions.corpus.load` reads that directory **only while keel-cloud's corpus holds no r3
  entry** (its docstring says so; `test_the_loader_reads_the_recorded_revision_while_keel_cloud_
  holds_none`). `03-lullaby.yaml` is written first and complete, re-tallied from its own picks by a
  scratch script before it was written (status totals 12 / 6 / 3 / 1 / 1 / 2; the three verdicts).
  Its `interpretations.problem` says *guessing* and *holds*, and Dev's story *short on sleep*: the
  problem's own words, so the registry's own Lullaby PROBLEM questions sweep clean against the
  vocabulary (`card, faster, likeli, listen, nam, stop, suggest, unclear` + the phrase *most
  likely*).
- **D7 (T020).** `compare.py` shells `<keel_cloud>/gradlew`, as `contract.export` and
  `validate.run` do, so the "fake command" the tests run is a fake `gradlew` in a temporary
  checkout -- one that copies the agreeing output, one that exits 1 the way a checkout without
  058's `compare` would, one that writes nothing.
- **D8 (T022, three shapes the screen-shapes page left open).** (a) The brief's dimension rows
  carry **`option_counts`** beside §2's fourteen fields: marks §2.6 allows every `optionCounts` row
  of `n` as an `N of M`, and a set dimension's standing is nothing else. (b) `founder_options` on a
  respondent job are **codes**, the founder's option *set* -- the registry's fixed codes, or the
  golden plan row less the escapes and respondent-only codes (`registry.RESPONDENT_ESCAPES`) --
  never which the founder picked. (c) r3 records no story prompt, so `story.prompt` is written and
  `null`. All three are requests to 058/063/064 as much as choices here; T002 corrects them.
- **D9 (T028, not run).** `make instruction-eval DRY=1 K=03-lullaby` runs keel-cloud's Gradle
  exporter in the keel-cloud checkout (a build in a sibling this branch may not touch) and, on
  `3e91cfc`, would stop at the export's missing `dimension-registry.json` -- the refusal
  `tests/test_instruction_registry.py` already holds. The dry path end to end is held instead by
  `tests/test_instruction_dry_run.py` (a fixture export, the fixture templates, a fake engine):
  19 cases + the `COMPARE` row, `compare_correctness` 28 of 28, every model mark unmeasured,
  `passed: false`. The real DRY run is the checkpoint after 058 lands.
- **D10 (pre-existing).** `tests/test_instruction_models.py::test_ask_hands_the_jobs_model_...`
  puts `parents[2]/keel-runtime` on `sys.path`, which from a worktree is `.claude/worktrees/
  keel-runtime`; it passes in a full run only because an earlier test has already imported
  `keel_runtime`. Unchanged here; worth a one-line fix on master.
- **D11 (T031, one line of a file tasks.md calls untouched).** `tests/test_instruction_judge_
  isolation.py` drove its "every call gets an explicit env" assertion through
  `same_expected_option`, one of the three questions call 29 deletes. Its one call now goes through
  `reveals_solution`; the plumbing it asserts -- `env=` on every call, `JUDGE_UNSET_ENV` stripped,
  `PATH` kept -- is unchanged, and both tests pass.
- **D12 (T035, what the calibration scorer counts).** `dimension_coverage` is absolute per case:
  a case whose keys are not exactly the slice, in `order`, contributes **0** of its slice (a doubled,
  a missing, a foreign or an out-of-order key). `option_validity` is over the questions written for
  slice keys. Sweep A covers the question, every option label and every belief phrase; a hit is a
  fault naming the word, a multi-word `mechanism_terms` entry is matched as a phrase, and a
  question whose only hits are inflection-ledger stems is one judge call, cached by text.
  `leak_hits` counts words, `leak_judged` judge-decided questions, so `judged_fraction` is
  judge-decided over all hits. A `NEEDS_INPUT` on any v9 screen is a failed case: every screen is
  handed the corpus's own inputs, so there is nothing to ask.
- **D13 (T042, the respondent result carries labels).** screen-shapes §3 gives a respondent item
  `options: [label..]` -- no codes -- so on a label-only item `option_validity` can hold the count
  (the plan's codes less `something_else`, which code appends) but not which codes are there.
  `score_respondent` therefore runs the code checks in full **whenever an option carries a `code`**
  (every plan code present, none foreign, none repeated, `Something else` last, Importance's own
  item -- r3's `own_item`, D3 -- never first) and the count otherwise; the gap is 063's to close by
  returning codes, or 058's batch to close with `R2`. Sweep B reads the founder's chosen phrase and
  any number the founder gave that the registry does not itself put on the item (band edges, the
  axis, the 7-night window): Lullaby's *at least 5 minutes* is the registry's own band edge and is
  not a leak; a founder's *15 to 25 minutes* in a Duration item is.
- **D14 (T043).** A read whose `invitationId` names another person counts that id in `extra_ids`
  and this person in `missing_ids`, and is not answered; an `anchoring` outside the two words is a
  shape refusal added to `shape_refusals` beside the aggregate's own (Edge Cases). The run prints
  each read as *the model's word (corpus word)*, and `chipped_skipped` counts the chipped stories
  of the entries a run read.
- **D15 (T051, the cross-track arrangement, and what r3 needed that marks §4 does not have).** The
  six entries are written **here**, under `tests/fixtures/corpus-r3/`, beside Lullaby -- not as a
  keel-cloud commit on 058's branch (research R2), which this branch may not touch; the README says
  they move verbatim at integration, when `check_corpus.py` and `GoldenCorpusTest` (175 + 21) run on
  them for the first time. Each keeps its market, statements, roles and people; each person's first
  occasion is their gate story; the picks are re-chosen against the registry; every standing is
  tallied from them under §2.5. Countly leaves out `problem.severity` (FR-009). **Three entries are
  B2B**, not one: Paidly (A-5's proposal), Repeatline and Mulch Run, whose r2 files already carry a
  buyer role and its people. That needed a field marks §4 lacks: a decision-maker carries **`link:
  COMMERCIAL_B2B`** (no gate, `recency: null`, `commercial.*` picks only), the loader checks it, the
  engine's input carries it, and nobody reads their story. And three registry values are Lullaby's
  alone -- the gate's *7 nights*, Frequency's *nights out of 7*, Duration's minutes/hours -- which the
  six read per circumstance; recorded in the corpus README as findings for 058.
- **D16 (T052, O-4 counted).** 106 people; 13 answer No at the gate, 6 chip, 22 are decision-makers
  on a B2B link: **65 reads at N=1, 195 at N=3**. A full run is **138 model cases at N=1, 414 at
  N=3**, plus seven `COMPARE` rows -- the plan's ≈ 420-480 estimate lands at its low edge because 22
  people are never read. The seven digests and the 65 are written above the call list in
  `instructions/marks.py`, and `tests/test_instruction_marks.py` checks the digests against the
  files' own bytes.
- **D17 (T049, half done).** `run.py` scores every `BRIEF` case on the five marks and prints them;
  the register puts each paragraph beside its standings with the vector verdicts as header rows.
  065's screen is the founder's, so T049 stays open.
- **D18 (T054, not run).** `make instruction-eval DRY=1` across the seven needs keel-cloud's exporter
  and 058's `compare`; it is the same checkpoint as T028 (D9). The dry path over a fixture export is
  held by `tests/test_instruction_dry_run.py`; `make unit` is green with T047.
- **D19 (T057).** screen-shapes.md gains §8 -- what the implementation found, as requests to 058/063/
  064 -- and plan.md and research.md record O-2/O-3 as landed and O-4 as counted. T002's diffs land
  with T002, when 058 does.
- **D20 (T059, S0 and S2 run; S1 not).** S0: `make unit VENV=<the main checkout's .venv>` (a fresh
  `make venv` in the worktree installs Playwright's browsers, which this run did not need) --
  **1486 passed, 75 skipped**. S2: `python -m instructions.rescore
  runs/20261001T043420Z-instructions` against the real v8 record on the founder's disk -- exit 2,
  *"20261001T043420Z-instructions was scored at marks_version 8: answered on screens v9 does not
  have, against corpus r2. Not re-scored"*; `scorecard.json` and `manifest.json` byte-identical
  after, nothing added. S1 waits on 058 (D9), so T059 stays open.
- **D21 (T002, keel-cloud 058 at `14a1430`, its worktree).** Read off the real export, the
  `screenContracts compare` source and `contracts/compare-command.md`, and corrected here, never there:
  (a) the registry file is named by the manifest (`dimension_registry`) and carries **no
  `version`**, so the engine input omits `registry_version`; (b) the registry carries `{window}` /
  `{window_unit}` placeholders, filled by code to the default *7 nights* (`registry.fill_window`;
  every r3 entry reads the default until the founder's decision 25), and every job's `context` slots
  carry `window`; (c) `CALIBRATION_QUESTIONS` takes **`interpretation`** -- the problem statement on
  PROBLEM, the mechanism card on SOLUTION (058 composes its `statement`; this eval hands the solution
  seed instead), `null` on COMMERCIAL -- in place of `problem` / `mechanism` / `persona`;
  `SOLUTION_MECHANISM` takes `problem_statement`; `PROBLEM_INTERPRET` no `interaction_history`;
  (d) `RESPONDENT_QUESTIONS`' `mechanism` carries `mechanism_terms` and is **absent on the B2B link**,
  and `founder_options` covers the model-written sets only; (e) `INTERPRET` and `BRIEF` are still
  exported in their **v8 shape** (`anchors` / `anchorings[]`, `claims`) until keel-cloud 064 / 065:
  the gate story goes over as the one anchor, `score_interpret` reads a single `anchorings[]` entry,
  and the brief's `claims` key is written `null` -- so `brief_paragraphs` cannot be measured on 058's
  BRIEF screen until 065; (f) `compare`'s input needs `respondent_questions` (`own_item`, or exit 1)
  and accepts `link` and `'yes'`/`'no'`; its output writes drift upper-case and `NONE` where the
  corpus writes `null`, and writes counts the corpus does not record and no belief sentence -- so a
  count is reported only where both sides state it. The export's model table (version 8) now carries
  `context`, `calibration` and `respondent`, and `MODELS=exported` is accepted.
- **D22 (T028, T054, T059's S1 -- run on 058's worktree, `stack.toml` pointed there and reverted, not
  committed).** `make instruction-eval DRY=1 K=03-lullaby N=1`: 19 cases + 1 `COMPARE` row,
  **`compare_correctness` 28 of 28**, 0 counts differ, every model mark unmeasured, `passed: false`,
  nothing spent. The same with `MODELS=exported`: accepted -- context and reading on
  `claude-haiku-4-5-20251001`, frame, calibration, respondent and brief on `claude-sonnet-5-5`.
  `make instruction-eval DRY=1 N=1` over all seven: **138 cases + 7 `COMPARE` rows,
  `compare_correctness` 196 of 196**, 0 counts differ. `make unit` green with T047. No `{window}` is
  left unfilled in any printed prompt.
- **D23 (058's open item 3 / its T049: the Lullaby examples break C4 and C6).** The registry's own
  Lullaby options trip the literal rules: **C4** (phrase = label) on `problem.urgency`
  `within_five_minutes`, `solution.relative_advantage` `fewer_attempts`, `solution.observability`
  `settled_sooner`, `commercial.buyer_payer_alignment` `joint_decision`, and
  `commercial.retention_potential` `daily` / `several_times_a_week` / `a_few_times_a_month`; **C6**
  (claim word) on `solution.relative_advantage`'s question (*better*),
  `solution.reliability_tolerance` `half_the_time`'s label (*helps*) and
  `solution.observability` `back_to_sleep` (*faster*). Of these, r3 Lullaby records two chosen
  phrases, now reworded -- `fewer tries before the baby settles`, `the baby was settled sooner than
  usual and they tried fewer things` -- with their belief sentences; and the registry slice's
  founder questions carry 058's own rewording (*better* -> *more useful*, *faster* -> *sooner*,
  *helps* -> *is useful*). Lullaby's digest moved (`marks.py`'s header follows); 058's
  `src/test/resources/keel/corpus-r3/03-lullaby.yaml` is the earlier copy and should be re-copied.
- **D24 (keel-cloud 062 at `ff316cc`: no code on a calibration option).** The `CALIBRATION_QUESTIONS`
  result carries **no `normalized`**: option *i* is the registry's code *i*, joined by position
  (instruction table §B #3, rule C2). `calibration_checks` now holds the count against the registry's
  codes (or the ladder's rungs) and treats a stated `normalized` as a cross-check against its
  position only; a model-written set is held to 4-6 distinct labels, its slug codes being 058's to
  derive. `score_respondent` likewise takes the plan's codes by position on a label-only item,
  *Something else* last. `tests/fixtures/calibration/03-lullaby.{PROBLEM,SOLUTION,COMMERCIAL}.
  result.json` transcribe 062's golden (`VectorFixtures.calibrationResult`, accepted by
  `screenContracts validate`) and score clean: 9/9, 9/9, 7/7, `no_leak` 9 of 9. `make unit` 1498
  passed, 75 skipped; `DRY=1 K=03-lullaby` on 062's worktree: 19 cases, `compare_correctness` 28 of 28.
- **D25 (call 37, founder decision 32, 2026-10-08; screen `runs/20261008T001657Z-instructions`).**
  call 37, founder 2026-10-08, screen 20261008T001657Z: a phrase may equal its label; v9 amended
  before any run of record. keel-cloud 062 narrowed C4 to empty / over 120 characters / a not-sure
  word, and the screen's nine calibration answers were faulted only for phrases equal to their
  labels; `score.calibration_checks` now reads C4 the same way. `MARKS_VERSION` stays 9.
- **D26 (calls 38 and 39, orchestrator 2026-10-08; bundle `runs/20261008T013837Z-instructions`).**
  call 38: code appends, never the model -- 'Something else', every respondent-only code the
  registry names and every band, scale-axis and gate option -- so a fixed-code control or the
  ladder owes exactly one label per remaining plan code, a set every founder label (normalised)
  plus 2-3 distractors, Importance 4-6 difficulties, and a band, numeric or gate control options
  null; v9 amended before any run of record. call 39: the vocabulary is stemmed from the golden
  mechanism's `mechanism`, `output`, `not_assumed` and `mechanism_terms` only, never `trigger` (it
  describes the problem moment) or `actor`, less the problem's own stems as before; v9 amended
  before any run of record. r3 Lullaby's `mechanism_terms` drops `cot` (digest moved). Re-scored
  offline (`--no-judge`, zero spend): respondent validity 29/69 -> 62/69 (the 7 left: one
  distractor on `target_circumstance`, `existing_sacrifice`, `purchase_friction`), calibration
  `no_leak` 26/27 -> 27/27, refusals R2 8 + R4 1 -> 0 (058's applier, re-read at rescore).
  `MARKS_VERSION` stays 9.
- **D27 (keel-cloud 058 `afe36fd`: `founder_options` are labels).** `context.build_respondent` sent
  r3's codes (*stress*, *lost_sleep*) as `founder_options`; production sends the founder's labels,
  and 058's `ScreenContractTool` now refuses a batch whose `founder_options` differ from the
  project's (`kind: case`). Every r3 model-written set and the ladder gains
  `founder_calibration[d].labels` (one per founder option code, plan order; a founder-side `none`
  kept, the code-appended rows of call 38 not); Lullaby's are the registry's with 058's C6 rewording
  (*faster* -> *sooner*), the other six authored. `build_respondent` sends them;
  `respondent_checks` matches a set against them as 058's R2 does (case, whitespace, punctuation
  ignored; the founder's *none* left to code), and a categorical pick (Target circumstance) takes
  the founder's labels and no distractor, as 058's R2 does. All seven digests moved. Re-scored
  offline against 058: respondent validity 45/69, `no_leak` 1.00 (120/120), refusals R2 x9 and no
  `case` fault -- the bundle's model was shown codes and wrote codes, so its sets now miss the
  labels; a fresh screen is the measure.
- **D28 (call 40, orchestrator 2026-10-08; bundle `runs/20261008T024419Z-instructions`).** The
  bundle's one `no_leak` fault (03-lullaby PART2 run2, `solution.adoption_friction`, sweep B, *the
  founder's phrase 'a few taps'*) was option 3 of five on the fixed-code effort ladder -- "A few
  taps" is the founder's rung, which the respondent must see among the others; the stem ("That
  night, with your phone where it was and your hands as they were, how much effort could you have
  managed before giving up on holding it near the cot?") carries no founder value. Sweep B as
  written contradicted call 38 (one label per plan code) and R2 (a set shows the founder's labels
  verbatim). Narrowed to the item's question and the part's reveal; four scorer tests. Re-scored
  offline (`--no-judge`): `no_leak` 0.992 -> 1.00 (120/120); `option_validity` 0.993 unchanged
  (the one fault: `commercial.purchase_friction` run3 wrote all six founder labels plus one
  distractor, *Having to set up an account before I could use it*; a set takes 2-3); verdict still
  FAIL on that fault alone.
- **D29 (call 41, founder decision 35, 2026-10-08).** The structural marks (`option_validity`,
  `dimension_coverage`, `no_leak`) read the ACCEPTED answer -- after the runtime's rule refusal and
  one redraw -- and `rule_refusal_rate` counts every refusal over the first drafts. The redraw
  mirrors keel-cloud 058 `InferenceOrchestrator` (its worktree, read at `44dab90`): on `CALIBRATION_QUESTIONS`
  and `RESPONDENT_QUESTIONS` (`repairUnattended` -> `queueAnotherQuestionsTurn`) turn one's
  context plus `repair` -- `RecoverySection`'s *NOT DERIVED -- ...* for an `InvalidResult` (every
  vector rule id), *REFUSED by rule R -- problem. remedy Answer again ...* for a `DomainException`
  -- with `interaction_history: []`; on the three draft screens (`refuseOrRepairDraft`) *REFUSED by
  rule path: why. Answer again ...* with `buildHistory`'s turn one (`{turn_number, input, outcome,
  questions}`). Both: same instruction, contract, model and effort, `input.content` empty, turn 2
  of the same interaction, and **the previous answer is never sent**. `INTERPRET` and `BRIEF` are
  never redrawn (the cloud refuses them outright); shape refusals are not redrawn (the cloud does
  repair a question screen's non-rule `InvalidResult` -- the founder's rule keeps shape an absolute
  zero on the raw answer instead). The runner now asks `screenContracts validate` once per answer
  on the five screens (one JVM start each, `verdicts/` in the bundle); the rest stay in the
  end-of-run batch. Cost: one more host call per rule refusal (same model and effort), plus the
  validator's JVM per answer, which spends nothing. Bundle: `answer.{raw,accepted,scored}`,
  `refusals[]` (tagged `draft` 1/2), `redraw{repair, request_payload, result, ...}`,
  `prompt-redraw.txt`; `#redraw` ids in `validation.json`; `report.html` and `register.html` show
  raw -> accepted. Rescore: a v9 bundle with no `answer` block scores raw and says so on the
  console, in `totals.scored_on` and in a new `report-v9.html`. Re-scored
  `runs/20261008T024419Z-instructions` offline (`--no-judge`): scored on raw (no redraws),
  `option_validity` 0.993 (143/144), `no_leak` 1.00, refusals R2 x1 of 57 (1.8%), verdict FAIL on
  the same `commercial.purchase_friction` fault as D28. 11 tests in
  `tests/test_instruction_redraw.py`.
  `make unit`: 1530 passed, 1 failed -- `test_keel_cloud_058s_canon_is_the_recorded_revision_byte_for_byte`,
  failing at `ddadadb` too: keel-cloud 058 moved on to `567f33f` (17 r3 belief sentences
  regenerated by `BeliefSentence`), so canon and `tests/fixtures/corpus-r3/` differ. Syncing the
  mirror also moves the marks header's seven r3 digests and the register's Lullaby sentences (two
  more tests), so it is left for its own change, not folded into call 41.
