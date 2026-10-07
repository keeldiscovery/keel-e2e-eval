# Research: marks v9, corpus revision 3, and the run that certifies the vectors

**Branch**: `029-marks-v9-vectors` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

Phase 0 of the plan. Every unknown the Technical Context raised, resolved against the code at
`a673a67` (this branch, spec only; `master` `0165017` underneath) and the drafts at the digests
recorded in [contracts/README.md](contracts/README.md). Each entry: **Decision · Rationale ·
Alternatives**. Nothing here spends a model call; nothing here edits a sibling.

## R1. Runtime, tooling and the floor

**Decision.** Python **3.12** (the venv `make venv` builds from the machine's `python3`, 3.12.5 on
the founder's Mac); the floor is **3.11**, because `instructions/marks.py` reads `marks.toml` with
`tomllib`. `pytest>=8.0` through `make unit` (`$(PY) -m pytest tests -q`); `pyyaml>=6.0` for the
corpus; `playwright`/`requests` are the browser scenarios' and are not touched. Three host CLIs:
`claude` (Claude Code CLI, 2.1.284 on the v8 run of record), `copilot`, `codex` — this feature's
run of record is `HOST=claude` only (FR-029). keel-cloud is reached through `./gradlew -q
screenContracts --args=…` (export, validate, and — new — compare); keel-runtime through
`prompts.load_runtime` (import, never a copy).

**Rationale.** All read off `Makefile`, `requirements.txt`, `pytest.ini`, `instructions/contract.py`
and `instructions/prompts.py`. The 3.9 floor `README.md` talks about is keel-connect-skill's, not
this repository's.

**Alternatives.** None worth taking: a `toml` dependency to lower the floor would buy nothing.

## R2. Where corpus revision 3 lands, and who writes it

**Decision.** **keel-cloud, on spec 058's branch** (track A of HANDOFF §4, the next number after
`057-listing-skips-unreadable` on keel-cloud `master` `3e91cfc`), as a recorded revision of
`canon/designs/measured-beliefs/corpus/*.yaml`: `03-lullaby.yaml` first, in its own commit, the
other six after, each with a header recording *revision 3, 2026-10-xx, keel-e2e-eval spec 029*.
`canon/designs/measured-beliefs/sim/check_corpus.py` and
`src/test/java/com/keeldiscovery/cloud/corpus/GoldenCorpusTest.java` move **in the same commit
series** (the 025 precedent: keel-cloud `4652739` on `049-one-occasion-once` carried the files, the
checker and `CorpusFixture` together — tasks.md Discovered D4). The corpus `README.md` gains its
second *Revised* paragraph. **This repository writes no corpus file** (spec 021 deviation 3,
FR-012) and its loader **refuses `revision != 3` by entry and by value** — not a fallback, the same
shape as v8's scalar-`stage` refusal in `corpus._check_anchors`.

**Rationale.** The corpus is keel-cloud's (`instructions/corpus.py` docstring; `README.md` of the
corpus: *"a change before then is a recorded corpus revision, not a quiet edit"*). The branch is
058's because 058 is the keel-cloud spec that owns the registry the corpus is keyed by and the
engine that must reproduce `expected.standings` — a corpus r3 with no reader on the other side
would be a file nobody had checked.

**Alternatives.** A separate keel-cloud spec for the revision alone (rejected: 025 put the
revision inside 049 and it was the right size); a fixture copy here (rejected: the single thing
freezing exists to prevent).

## R3. The compare engine's command line and its two files

**Decision.** `compare.py` shells **`./gradlew -q screenContracts --args="compare <in> <out>"`**
in the keel-cloud checkout `stack.toml` names — the exporter's and validator's sibling, same task,
same `cwd`, same timeout discipline as `contract.export` and `validate.run`. `<in>` is one JSON
object per entry built **from r3 only**: `{entry, market, registry_version, founder_calibration,
persona, answers: [{person, recency, anchoring, picks}]}` — exactly the fields the engine's
production inputs are made of (registry `answers.*` + belief + responses with `Anchoring`,
instruction-table §B row 11). `<out>` is `{standings: {<dimension>: {status, drift, n, inside?,
outside?, median?, proportion?, optionCounts?, bar?, belief_sentence}}, vector_verdicts: {PROBLEM:
{verdict, deciding}, …}}`. The eval **diffs** `status`/`drift` per dimension and `verdict`/
`deciding` per vector against `expected` and **marks** them; every other key is diffed and
**reported** (call 34, call 3). The shapes are written down in
[contracts/screen-shapes.md](contracts/screen-shapes.md) §5 as the request to 058; if 058 ships a
different shape the eval reads 058's and this document is corrected, never the other way round.

**Rationale.** FR-018 and A-9: *this repo keeps no copy of the cloud's arithmetic* (`runs/DRIFT.md`
#33, #36, #41, #44, #45). Shelling the same Gradle task the contract and the validator already use
adds no second process model and no second prerequisite check: a missing `compare` sub-command is
a non-zero exit, which is `compare_correctness` **unmeasured by name** (spec Edge Cases), never a
warning.

**Alternatives.** A Python port of the compare rules for `DRY=1` (rejected outright — it is the
copy the DRIFT entries forbid, and it would be the ruler certifying itself); reading
`GoldenCorpusTest`'s verdict instead of running the engine (rejected: a JUnit run is 1,548 tests
and three environment variables — 025 D2 — and the eval would be reading a test's opinion rather
than the engine's output).

## R4. The registry export: file, place, invariants

**Decision.** `contract.read` reads **`dimension-registry.json`** from the export directory, beside
`manifest.json`, `context-keys.json`, `contracts/` and `model-routing.json`, into
`ExportedContract.registry` (an `instructions/registry.py` `Registry` object). Absent → 
`ContractUnavailable` naming the file and keel-cloud 058, **before any case is built** (FR-021).
Present → the **seven invariants of `registry-schema.draft.md`** are checked on the way in and
any failure is a refusal naming the invariant and the key. The registry's YAML draft in
[contracts/dimension-registry.yaml](contracts/dimension-registry.yaml) is the **design-time golden
for this plan and the shape every fixture copies**; it is never read by code at run time — the run
reads keel-cloud's export, because the export is what production reads.

**Rationale.** `contract.py`'s whole argument: *nothing here is a copy; the contract is produced by
keel-cloud's own exporter and read back whole*. The registry is one more file from the same
exporter. The invariants are checked here because `option_validity` and `dimension_coverage` are
only honest against a registry that is itself well-formed (marks §2.2's *"1.00 is honest only
because the registry fixes the codes"*).

**Alternatives.** Reading `canon/…/dimension-registry.yaml` straight out of the keel-cloud
checkout (rejected: the run must read what production reads, and `models.from_keel_cloud` exists
only for scenarios that have a checkout and not an export).

## R5. `MODELS=exported` against the v8 table — what refuses, and what must not

**Decision.** `models.CLASSES` becomes the **six** classes of FR-023 (`context`, `frame`,
`calibration`, `respondent`, `reading`, `brief`) **plus the three dormant names a v8 table still
carries** (`assumptions`, `reframe`, `questions`), tolerated by `parse` and reported by nobody.
`KIND_TO_CLASS` maps the eight v9 kinds; `REPORTED_CLASSES` is the six. `parse`'s *missing* check
runs over the six measured classes, so keel-cloud's **v8 table (`version: 8`, classes `frame,
assumptions, reframe, reading, brief, questions`) refuses with `ModelsUnavailable` naming
`context`, `calibration`, `respondent` and `version 8`** — the spec's Edge Case, found by reading
`models.parse` and `src/main/resources/keel/model-routing.json` rather than by a failed run (the
025 D13 lesson, the other way round). Until 058 exports a table carrying the three new classes,
a screen pins them with `MODELS=<file>` — [contracts/models-screen.json](contracts/models-screen.json)
is that file at the ceiling (A-4, A-9).

**Rationale.** `parse` raises on an unknown class name (`models.py:479`), so dropping the dormant
names from `CLASSES` would make every v8-era table — including the one the export carries today —
unreadable for the wrong reason (*"classes names 'assumptions'"*) instead of the right one. A-9
says existing rows do not move; tolerating their names is what that costs.

**Alternatives.** Keep `CLASSES` at nine with the three new ones appended and report all nine
(rejected: `models_used`/`efforts_used` would carry three classes no v9 case runs, and the verdict
would name models that wrote nothing).

## R6. Case ids, the `-k` needle, and the screens' table

**Decision.** Case ids per FR-016, in build order per entry and run index:
`<entry>/CONTEXT_INTERPRET/run<N>` · `<entry>/PROBLEM_INTERPRET/run<N>` ·
`<entry>/SOLUTION_MECHANISM/run<N>` · `<entry>/CALIBRATION_<VECTOR>/run<N>` ×3 ·
`<entry>/RESPONDENT_PART<P>/run<N>` ×3 (+ `<entry>/RESPONDENT_B2B/run<N>`) ·
`<entry>/INTERPRET/<person>/run<N>` per gate-yes, un-chipped person · `<entry>/COMPARE` (one row,
no index, no call) · `<entry>/BRIEF/run<N>`. `-k` is a **case-insensitive substring of the case
id**, as today (`run._all_cases`), plus **kind words** that select by `Case.kind` exactly:
`context`, `frame` (the two typed-seed interpretations), `calibration`, `respondent`, `reading`
(= `INTERPRET`), `compare`, `brief`. The spec's needles work because of the slash:
`03-lullaby/INTERPRET` is a substring of `03-lullaby/INTERPRET/Amira Saleh/run1` and **not** of
`03-lullaby/CONTEXT_INTERPRET/run1` or `03-lullaby/PROBLEM_INTERPRET/run1`. A needle matching no
case prints *"no case matches"* and spends nothing (Edge Cases).

**Rationale.** The Makefile has documented `K=` as *a subject* since the four subjects existed;
`K=questions` was the cheapest slice reaching every entry on 025's screen. Keeping substring
semantics keeps every command in `README.md` meaning what it meant. The kind word `interpret` is
deliberately **not** offered: it would be ambiguous between the three interpretation screens and
the anchor read, and the spec's own table uses the slash form.

**Alternatives.** A `--screen` flag (rejected: a second selector to document and a second place
for a typo to quietly select nothing).

## R7. `compare_correctness` on a screen, and on `DRY=1`

**Decision.** The `COMPARE` row is **a case like any other for the needle's purposes** — selected
by `K=03-lullaby`, `K=compare` or `K=03-lullaby/COMPARE`; left out by `K=03-lullaby/CALIBRATION`.
On `DRY=1` the run **writes a `scorecard.json` and a `verdict.json`** (today's dry run writes
nothing) carrying `compare_correctness` measured and every model-scored mark **unmeasured**, so
`passed: false` with the reason legible — a dry verdict is never a pass and the file says so.
`compare.py` runs **at case-build time** (it needs no answer), so the DRY path and the real path
share one code path and one output.

**Rationale.** Call 34: *measured on `DRY=1` too*; SC-003: *reports `compare_correctness`
measured at 28 of 28*; SC-010: a screen comes back `passed: false` with the other six entries
unmeasured. A screen that selects a model subject and not `COMPARE` reports `compare_correctness`
unmeasured, which is correct: a screen is never a run of record.

**Alternatives.** Always running `COMPARE` for any entry that has a selected case (rejected: a
hidden extra; the needle should select what it says).

## R8. The judge's one question, cached, isolated

**Decision.** `judge.Judge` keeps `_ask`, the cache, the call record, `judge_env` and
`JUDGE_UNSET_ENV` byte for byte, and offers **one** question:
`reveals_solution(question_text, mechanism_one_liner, *, context="") -> bool`, worded as marks
§2.3 — *does this question tell a stranger what the proposed solution is: `<mechanism one-liner>`?
SAME/DIFFERENT* — where `SAME` means *it reveals* and is the fault. `same_answer_space`,
`same_expected_option` and `pick` are deleted with `align.py` (call 29). `judged_fraction` at v9 =
judge-decided `no_leak` hits over all `no_leak` hits (`marks.toml`'s last paragraph); `judge_calls`
reported as today. The mechanism one-liner is composed by code from the corpus's golden
`solution_mechanism.{actor,trigger,mechanism,output}` — four clauses joined, never the live
`SOLUTION_MECHANISM` answer (call 32).

**Rationale.** FR-005 and FR-015; `tests/test_instruction_judge_isolation.py` must keep passing
unchanged, which fixes the plumbing.

**Alternatives.** Keeping `same_answer_space` "in case" (rejected: dead code on the ruler is the
one place dead code is not harmless).

## R9. Where the belief sentence comes from, for `BRIEF` and the register

**Decision.** The eval **never composes a belief sentence**. `BELIEF_SENTENCE` is a code row in
production (instruction-table §B row 4: registry template + chosen phrase + context slots), which
makes it cloud arithmetic this repo does not copy — even though it is one `str.format`. So the
sentence must be **recorded in r3**: `founder_calibration[<dimension>].belief_sentence`, written
by `check_corpus.py` the way `expected.buckets` used to be (marks §4's own comment: *"the engine's
output, recorded by the checker like buckets were — never hand-written"*). `build_brief` reads it
from there; `register.html` shows it beside the founder's answer (FR-022). **This is a request to
the r3 writer** (R2) and is listed in plan §Open items; until the key exists `build_brief` sends
`belief_sentence: null` and `tests/` assert the key's presence on the real files, which is the
named red window of R14.

**Rationale.** DRIFT #33/#36/#41/#44/#45 again, and judgement call 19's precedent (`median_reads`
goes over in the corpus's own unit because this repo will not keep `Measure.say`).

**Alternatives.** Taking it from `compare`'s `<out>` (R3 carries `belief_sentence` there too, so
either works; the corpus is chosen because the brief context must be buildable when the engine is
absent — otherwise a missing engine would leave `BRIEF` unmeasured as well as `COMPARE`, two
marks for one prerequisite).

## R10. What keel-cloud's validator must take, and how the eval knows

**Decision.** `validate.build_batch` emits a **case kind per screen** — the eight v9 constants plus
`COMPARE` is never batched (nothing to validate) — carrying what each screen's `ScreenResultApplier`
reads: `vector`/`registry_slice` on a calibration case, `part`/`plan`/`founder_options` on a
respondent case, `invitation_id`/`story` on an `INTERPRET` case, `context`/`seed` on the three
interpretations, `standings` on `BRIEF`. `_SHAPE_MARKERS` gains one marker per new screen, read off
`ScreenContractTool.java` as the **constant reference** (`InferenceScreen.CALIBRATION_QUESTIONS`
…), the way `questions` is read today; `_PREREQUISITE` gains one sentence per screen naming
keel-cloud 058 and the marks it leaves unmeasured (`rule_refusal_rate`, `shape_refusals`, and —
for the two question screens — nothing else: coverage, validity and leak are this repo's code).
An unknown kind is **unmeasured by name**, never a warning, never a refusal (FR-024, 025 FR-019).

**Rationale.** `validate.py`'s own rule: *the only honest way to ask what the aggregate refuses is
to hand it to the aggregate*; and D12/D18's lesson that a batch shown the wrong state measures
something else.

**Alternatives.** Skipping the aggregate on the new screens until 058 lands (rejected: that is
exactly the flattery call 13 forbids).

## R11. `rescore.py` across the bump, and for a v9 bundle

**Decision.** `rescore.main` reads `scorecard.json`'s `marks_version` **first** and refuses
anything below 9 with the bundle name, the version and the reason *answered on screens v9 does
not have, against corpus r2* (FR-004, SC-004). For a v9 bundle it re-scores every case kind from
the envelopes, re-runs `compare.py` (free), re-reads the registry from the bundle's own copied
`contracts/` directory (which now includes `dimension-registry.json` — `report.copy_contracts`
copies the whole export), and writes `scorecard-v9.json` **beside**, never over. The v8 record
`runs/20261001T043420Z-instructions` is on the founder's disk and not in git (`runs/` is ignored),
so the unit test for the refusal uses a two-file fixture bundle (`manifest.json` + `scorecard.json`
with `marks_version: 8`) and the quickstart names the real one.

**Rationale.** `marks.toml` v8 header already states the rule for v7→v8; v9 writes it into code
because this time the subjects moved as well as the corpus.

## R12. `why.py` is untouched

**Decision.** No change. `why.parse` already takes any integer after `marks:`; `WHY=marks:9` earns
the full run and is refused on a screen by the existing `FULL_EVENTS` rule; `tests/test_instruction_why.py`
gains one assertion that `marks:9` parses to `{"event": "marks", "version": 9}`.

**Rationale.** FR-029: *`why.py` MUST NOT change*; verified by reading `why.parse`.

## R13. The denominators, counted and not yet countable

**Decision.** What is countable now, from `03-lullaby.yaml` r2 and marks §5, is written into the
plan: 12 people; Hugo Laurent (*ten days ago*) and Leo Martins (*hasn't happened*) answer **No** at
the 7-night gate (FR-011); Jonas Weber carries `chip: cant_recall` and builds no case (FR-017); so
`INTERPRET` builds **9** cases at N=1 and `anchoring_accuracy`'s denominator is 9 (8 `ANCHORED` /
1 `GUESSED` — Finn). At N=1 on Lullaby: 3 + 3 + 3 + 9 + 1 = **19** model cases plus the `COMPARE`
row (SC-003); at N=3: **57** (SC-010). The corpus-wide `INTERPRET` denominator (106 people less
every gate-No and every chipped story) **cannot be counted until the other six entries are
re-expressed** — it goes into the v9 header then (US4.2). The plan records that the spec's *≈ 420
cases at N=3* is an estimate: 7 × (3 + 3 + 3 + 1) × 3 = 210 non-read cases, plus roughly 80 gate-yes
un-chipped people × 3 ≈ 240 reads, lands nearer 450; the true figure is the r3 writer's to count
and the certificate's to state.

**Rationale.** SC-003/SC-008/SC-010/SC-012 need these numbers to be checkable; the ones that are
checkable today are checked today.

## R14. The red window, and the harness readers the spec did not name

**Decision.** Two things go red when keel-cloud's r3 commit lands, and the plan names both.

1. **This repository's tests that read the real seven files** (`tests/test_corpus_script.py`'s
   shape assertions, and the new r3 shape tests of US4) — the 025 precedent, kept: **`make unit` is
   red between keel-cloud's r3 landing and this branch's loader landing, and the tasks order the
   work so the window is one commit wide**, never closed by a fixture copy.
2. **The harness and scenario readers of the r2 shape** — 87 call sites in `harness/corpus_script.py`,
   `harness/browser.py`, `harness/stranger_stories.py`, `evals/corpus_scenario.py`,
   `evals/corpus_facts.py`, `evals/test_s001_smoke.py`, `evals/test_s002_agent_optional.py`,
   `evals/test_s004_stranger_who_gives_orders.py`, `evals/test_s005_countly.py`,
   `evals/test_s006_paidly.py`, `evals/test_s012_journey_through_a_host.py` and
   `evals/tools/curated_proof_run.py` — read `beliefs`, `questionnaire.anchors`, `expected.buckets`
   and `expected.stages` through `instructions/corpus.py`, and drive **today's** product (the
   three-stage framing, the review cards, the one questionnaire) which keel-cloud and keel-web
   still ship. r3 drops every one of those keys. **This spec does not rewrite those readers**: the
   product they drive is being replaced by tracks A–C and their rewrite is a sibling spec of the
   journey (proposed `030-journey-vectors`, after keel-web's corridor lands). What this spec does is
   keep `make unit` honest: the Foundational phase adds a **named skip** — `pytest.skip` with the
   reason and the sibling's name — to the tests that assert the r2 shape on the real files, taken
   only when `corpus.load` reports `revision == 3`, and `evals/corpus_scenario.py`'s three scenarios
   plus S-012's `ENTRY=` read refuse by name at their preludes rather than failing twenty steps in.
   **This is an open item for the founder** (plan §Open items O-1): the alternative — carrying an r2
   reader beside the r3 one so the old journey keeps its script source — is a second frozen corpus
   in all but name.

**Rationale.** AGENTS.md: *"a run can never be green against a script that drifted from a corpus
that moved"*; 025 plan §2 *"a test that passes against a corpus that has not been revised is a
test that would pass against the wrong corpus"*; and the spec's silence on the harness is a gap,
not a decision, so it is surfaced rather than papered over.

## R15. `text.py`, `compare.py`, `registry.py`: the module map

**Decision.** Three modules join `instructions/`; one leaves.

| Module | Fate | Holds |
|---|---|---|
| `instructions/text.py` | **new** | `normalise`, `normalise_phrase` (moved from `align.py` unchanged), `stems(text) -> set` (a small suffix stemmer: `-s`, `-es`, `-ed`, `-ing`, `-ion/-ification`), `STOPLIST`, `content_words`. The one place a word is turned into a stem, used by `Entry.vocabulary()` and `no_leak`. |
| `instructions/registry.py` | **new** | `Registry` (25 `Dimension`s, `slice(vector)`, `by_key`, `asked_in_v1`, `part_of`, `codes_of`, `fixed_respondent_codes`), `check_invariants(registry) -> list[str]` (the seven), `RegistryUnavailable`. |
| `instructions/compare.py` | **new** | `build_input(entry, registry)`, `run(keel_cloud, entry_input, in_path, out_path)`, `diff(expected, produced) -> CompareScore`, `EngineUnavailable`. |
| `instructions/align.py` | **retired** | deleted; its docstring's T001 finding is quoted once in `marks.py` call 29's own words and nowhere else. |

**Rationale.** The spec's file table names `text.py` and `compare.py`; `registry.py` is the
invariants' home because `contract.py` is a reader and `score.py` is arithmetic, and seven checks
with their own refusal messages belong to neither.

**Alternatives.** Putting the registry into `contract.py` as a dict (rejected: four scorers read
it and each would re-derive the slice).

## R16. The three interpretation screens' contexts, from the corpus

**Decision.** `build_context_interpret(entry, keys)` sends `context_fields` = the r3 `context`'s
four slots as the founder typed them (`actor`, `job`, `circumstance`, `segment` → `who`, `what`,
`when`, `which_people`), `market`, `project_name`; `build_problem_interpret(entry, keys)` sends
`input.content` = `statements.problem` (the seed, verbatim), `context`, `market`, an empty
`interaction_history`; `build_solution_mechanism(entry, keys)` sends `statements.solution`,
`context`, `problem.statement` = the corpus's own `context`-era problem sentence — **the r3 file
must carry one**: `interpretations.problem` (one sentence, hand-written, the `PROBLEM_INTERPRET`
golden that downstream screens read, marks §1 *"downstream screens get the corpus's own
context / solution_mechanism, never the live output"*). Requested of the r3 writer with R9's key
(plan §Open items O-2). `NEEDS_INPUT` twice is a rule refusal (`X3`/`P3`/`M3`) counted in the rate
and rendered as refused; the eval never answers a `NEEDS_INPUT` (no repair turn, as today).

**Rationale.** FR-021 and A-2; the context keys come from the export (`exported.keys_for(screen)`)
in the exporter's order, as every builder in `context.py` already does.

## R17. Effort, ceiling, and the one `high` measurement

**Decision.** The ceiling is `claude-sonnet-5-5` at `medium` on `standard`, Haiku 4.5 on `light`,
pinned **through the job's own `model`/`effort` keys** by `models.stamp`, never through
`CLAUDE_CODE_EFFORT_LEVEL` (which `judge.judge_env` strips). FR-028's single `high` measurement is
`make instruction-screen K=03-lullaby/CALIBRATION HOST=claude N=3
WHY=new-model:claude:claude-sonnet-5-5 MODELS=<file-with-high>` — reported in `runs/DRIFT.md`,
never routed, never the fix. The quickstart carries the command and the pin file's shape.

**Rationale.** A-4, HANDOFF §4's ceiling, the Makefile's own warning about the process-wide
variable.
