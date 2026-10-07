# Implementation Plan: marks v9, corpus revision 3, and the run that certifies the vectors

**Branch**: `029-marks-v9-vectors` | **Date**: 2026-10-07 | **Spec**: [spec.md](spec.md) |
**Tasks**: [tasks.md](tasks.md)

**Input**: `specs/029-marks-v9-vectors/spec.md` (committed at `a673a67`, off `master` `0165017`);
the Phase 0 drafts copied into [contracts/](contracts/README.md) at their recorded digests;
[research.md](research.md) (R1–R17), [data-model.md](data-model.md), [quickstart.md](quickstart.md).

## Summary

`MARKS_VERSION` goes 8 → 9 with judgement calls 28–36 appended verbatim; the subjects become the
eight screens of the vector redesign (three rendered unscored, two question screens scored by code
against keel-cloud's exported dimension registry, `INTERPRET` narrowed to one gate story a person,
`COMPARE` shelled to keel-cloud's engine at zero spend, `BRIEF` with a fifth per-case mark);
`golden_belief_recall` and `align.py` retire; `instructions/corpus.py` becomes the revision-3 loader
that refuses anything else; and the work is ordered so that **the first green thing is free**
(`DRY=1 K=03-lullaby`, `compare_correctness` 28 of 28), each template is then proven on one entry at
N=3, and one full run, `WHY=marks:9`, is spent last and once as the certificate routing v9 lands
on. The approach is the repository's own: tests before code, fixtures for every scorer, nothing
copied from the cloud (the registry, the contract and the engine are all *read*), nothing committed
that was generated, and every prerequisite that is missing refused **by name** or reported
**unmeasured** — never warned past.

## Technical Context

**Language/Version**: Python 3.12 (`make venv` from the machine's `python3`); floor 3.11
(`tomllib` in `instructions/marks.py`). Type syntax `X | None`, dataclasses, `from __future__
import annotations` throughout `instructions/`.

**Primary Dependencies**: stdlib (`tomllib`, `json`, `hashlib`, `subprocess`, `re`); `pyyaml>=6.0`
(the corpus, read only); `pytest>=8.0`. Siblings read, never copied: keel-cloud through
`./gradlew -q screenContracts --args="export|validate|compare …"` (`instructions/contract.py`,
`validate.py`, new `compare.py`); keel-runtime through `prompts.load_runtime` (its own
`build_prompt` and executors); the host CLI `claude` (judge and subject), `copilot`/`codex`
(untouched, no v9 run on them).

**Storage**: files. The frozen corpus in keel-cloud's checkout (`canon/designs/measured-beliefs/corpus/*.yaml`,
hashed on the way in and out); the export under `runs/.contracts*`; bundles under `runs/<stamp>-instructions[-host]/`
(git-ignored); `instructions/marks.toml`.

**Testing**: `make unit` = `.venv/bin/python -m pytest tests -q`, stackless, no model, fixtures a
person can check by hand (the convention of `tests/test_instruction_score.py`,
`test_instruction_validate.py`, `test_instruction_marks.py`); shape tests against the **real**
corpus files (`tests/test_corpus_script.py`'s rule since spec 010: one reader, one hash). The eval
itself is collected by no pytest run (AGENTS.md).

**Target Platform**: the founder's macOS shell, `make` from the repository root; the keel-cloud
checkout at `../keel-cloud` with JDK + Gradle; Colima not needed for anything here (the engine is
a Gradle task, not a Testcontainers test).

**Project Type**: a CLI eval (`python -m instructions.run`) with a scoring library and two rendered
HTML pages; single project, no service.

**Performance Goals**: `DRY=1 K=03-lullaby` under the exporter's own time (~1 min of Gradle);
`compare.py` adds one Gradle invocation per entry (seven on the full run); the full run ≈ 3 h and
≈ $15–20 at N=3 (the v8 record: 414 cases, 3 h 11 m, $15.41).

**Constraints**: every model call needs a `WHY` event at the door; `marks:` is full-run only; the
ceiling is `claude-sonnet-5-5` at `medium` on `standard`, Haiku 4.5 on `light`, pinned through the
job's keys (`models.stamp`), never `CLAUDE_CODE_EFFORT_LEVEL`; routing stays v8 until the
certificate; `why.py`'s events do not change; no corpus file and no routing table edited here; no
repair turn, no retry, no second run to get a better number.

**Scale/Scope**: 8 screens; 8 marks; 36 judgement calls; 25 dimensions; 7 corpus entries (106
people); ≈ 19 cases per entry at N=1 plus one `COMPARE` row; ≈ 420–480 cases at N=3 on the full
run (research R13); 20 source files touched or created under `instructions/`, ~14 test files
rewritten or added under `tests/`, `Makefile` unchanged, `README.md`/`AGENTS.md` gate text.

**Unknowns**: none left as `NEEDS CLARIFICATION` — the spec closed its clarifications on
2026-10-07 and research.md resolves the seventeen technical ones. Two **requests to the r3 writer**
(the belief sentence and the golden problem interpretation keys, R9/R16) and one **decision for
the founder** (the harness readers of the r2 shape, R14) are carried under *Open items* below;
none blocks Phase 2 or US1.

## Constitution Check

*GATE: must pass before Phase 0 research. Re-checked after Phase 1 design (below).*

`.specify/memory/constitution.md` is still the **unfilled template** at `a673a67` (every principle
reads `[PRINCIPLE_N_NAME]`; 025's T008 recorded the same). There is therefore nothing to check
against in that file, and this repository's governing document is **`AGENTS.md`**, with
`README.md`'s standing gate, `instructions/marks.py`'s judgement calls and `runs/DRIFT.md`'s
recorded lessons as the rules the referee actually works to. The gates below are drawn from
those, stated as checks, and each is evaluated twice.

| # | Gate (source) | Pre-research | Post-design |
|---|---|---|---|
| G1 | **No LLM except in the three named places** (AGENTS.md). The instruction eval is one; this feature adds no fourth place. The judge narrows to one question. `compare.py` calls no model. | PASS — eight screens are still *the instruction eval*; the judge's question count goes 3 → 1. | PASS — research R8 (one question, cached, isolated); R3 (the engine is Gradle, not a model). |
| G2 | **It spends only for a named `WHY` event, never on a schedule or in CI; `DRY=1` needs none** (AGENTS.md, Makefile, `why.py`). | PASS — `WHY=marks:9` already parses; no new event; the Makefile is untouched. | PASS — R12 (`why.py` unchanged); R7 (DRY writes a scorecard and spends nothing); quickstart S1–S4 each name the event. |
| G3 | **No copy of the cloud's arithmetic; siblings are read at HEAD, never vendored** (DRIFT #33/#36/#41/#44/#45; `contract.py`, `models.py`, `prompts.py` docstrings). | PASS in intent — the spec shells the engine (FR-018) and reads the registry export (FR-021). | PASS — R3 (compare shelled; a Python port refused), R4 (registry from the export), R9 (the belief sentence is recorded in r3, never composed here), R10 (the aggregate is asked, not restated). |
| G4 | **This repository writes to no sibling and carries no corpus copy; its tests read the real files** (AGENTS.md; spec 021 deviation 3; spec 010 R6). | PASS — FR-012; the corpus lands in keel-cloud. | PASS with a note — `contracts/dimension-registry.yaml` and `contracts/marks-v9.md` are **design-time copies of drafts**, read by no code at run time (contracts/README.md); fixtures under `tests/` are hand-sized slices, never a corpus entry. R2 names the branch that writes r3. |
| G5 | **An unmeasured mark is not a met mark; a missing prerequisite is a refusal by name or an unmeasured mark, never a warning** (calls 13, 34; 025 FR-019). | PASS — FR-003, FR-021, FR-024, Edge Cases. | PASS — data-model §5/§6 (every row carries `measured`/`met`; the bundle's state table); R5 (the v8 table refuses by naming the three classes); R10/R11. |
| G6 | **Judgement calls are append-only, struck nowhere; the rubric's version moves with any mark, metric, rule or call** (`marks.py` docstring). | PASS — calls 28–36 appended, 1–27 byte-identical (SC-001). | PASS — tasks.md pins 1–27 against a frozen copy extracted at `0165017` and asserts the set 1–36 (D7's rule: the list is a set, not sorted). |
| G7 | **`make unit` green at every commit; tests first; no test deleted to make a phase pass** (025 tasks.md's standing rule, D11). | PASS as a plan — the known exception is the r3 red window. | PASS with the exception named — R14 and tasks.md order the loader so the window is one commit wide; the retired tests (`test_instruction_align.py`, `test_instruction_reads.py`, `test_instruction_questions.py`) are **replaced with the reason written where they stood**, not deleted to pass. |
| G8 | **The judge answers at the CLI's own default** (`judge.JUDGE_UNSET_ENV`, `tests/test_instruction_judge_isolation.py`). | PASS — FR-005 keeps it. | PASS — R8; the isolation test is unchanged and must stay green. |
| G9 | **The referee owns no product code; cross-repo defects go to `runs/DRIFT.md`; a red run is a finding, not a reason to run again** (AGENTS.md rules; 025 T031). | PASS — the seven templates are keel-cloud 059–065; routing v9 is keel-cloud's. | PASS — §*What is deliberately not built*; quickstart S4's last line. |
| G10 | **The run of record is spent once, after every Wait, by the founder** (HANDOFF §4; FR-029). | PASS — US4 is the founder's. | PASS — §*The Waits* below; tasks.md's last phase is unticked and its command is the only thing that spends. |

**Result, both passes: no violation.** Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/029-marks-v9-vectors/
├── spec.md              # committed a673a67
├── plan.md              # this file
├── research.md          # R1–R17: every unknown resolved
├── data-model.md        # Registry/Dimension, Entry/Person r3, Plan, Screen, Mark, Scorecard/Bundle, Certificate
├── quickstart.md        # S0 unit · S1 DRY · S2 rescore refusal · S3 screens · S4 the run of record
├── contracts/
│   ├── README.md                  # provenance and digests of every copy
│   ├── marks-v9.toml              # verbatim draft → instructions/marks.toml
│   ├── marks-v9.md                # verbatim draft: the rubric, calls 28–36, the r3 schema
│   ├── dimension-registry.yaml    # verbatim draft: the golden for option_validity (design-time)
│   ├── screen-shapes.md           # case ids, context keys, response shapes, rule ids, batch, compare files, register
│   └── models-screen.json         # the MODELS=<file> pin for a screen until 058's table exports
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source code (repository root) — what moves, what joins, what leaves

```text
instructions/
├── marks.py          MARKS_VERSION = 9; DEFAULTS = the eight keys; judge() eight rows; calls 28–36 appended
├── marks.toml        contracts/marks-v9.toml, byte for byte
├── corpus.py         the r3 loader: Entry/Person per data-model §2; plan(), vocabulary(), readable(); refusals
├── registry.py       NEW  Registry/Dimension from dimension-registry.json; the seven invariants; slices
├── text.py           NEW  normalise, normalise_phrase (from align.py), stems, STOPLIST, content_words
├── contract.py       eight screen constants; ExportedContract.registry; refusal when the file is absent
├── instruction.py    STEMS for context-interpret, problem-interpret, solution-mechanism, calibration-questions, respondent-questions
├── context.py        build_context_interpret, build_problem_interpret, build_solution_mechanism,
│                     build_calibration, build_respondent, build_interpret, build_brief; earlier_lines/build_questions/anchors_for deleted
├── prompts.py        build_cases in FR-016's order and ids; Case.kind ∈ {CONTEXT, FRAME, CALIBRATION, RESPONDENT, READING, COMPARE, BRIEF}
├── compare.py        NEW  build_input, run (shells `screenContracts compare`), diff → CompareScore; EngineUnavailable
├── score.py          score_calibration, score_respondent, score_interpret (by person), score_compare; totals/spread with v9 keys;
│                     score_assumptions, score_reading deleted
├── judge.py          reveals_solution only; cache, calls, judge_env, JUDGE_UNSET_ENV unchanged
├── brief.py          no_claim_words (fifth mark); deciding_line reads vector_verdicts; ENUM_NAMES/CONTEXT_FIELD_NAMES widened; VERDICT_MARKERS by Status
├── validate.py       batch kinds for the seven model screens; _SHAPE_MARKERS/_PREREQUISITE per screen; unknown kind → unmeasured by name
├── rescore.py        refuses marks_version < 9 by name; v9 path re-scores every kind and re-runs compare
├── report.py         the v9 mark table; register_blocks per contracts/screen-shapes.md §7; copy_contracts copies dimension-registry.json
├── models.py         CLASSES = six measured + three dormant tolerated; KIND_TO_CLASS, SCREEN_TO_CLASS, REPORTED_CLASSES per FR-023
├── run.py            SCREENS = the eight; -k kind words; the printed line per kind; DRY writes scorecard/verdict; COMPARE at build time
├── runner.py         unchanged
├── why.py            unchanged (FR-029)
└── align.py          RETIRED (deleted; call 29)

tests/
├── test_instruction_marks.py        rewritten: version 9; set 1–36; 1–27 byte-identical to tests/fixtures/marks/calls-1-27.at-0165017.txt; no number moved but one struck
├── test_instruction_corpus_r3.py    NEW  the loader on fixtures: plan(), vocabulary(), readable(), every refusal
├── test_instruction_registry.py     NEW  the seven invariants, each made to fail once; slices; plan_keys
├── test_instruction_text.py         NEW  normalise (moved tests from test_instruction_align.py), stems, stoplist
├── test_instruction_context.py      rewritten: the seven builders in the exporter's key order; what each must NOT carry
├── test_instruction_prompts.py      rewritten: build_cases order and ids; 19 + COMPARE on a 12-person fixture; needles
├── test_instruction_compare.py      NEW  build_input from r3; diff on fixture out.json; unmeasured on a non-zero exit
├── test_instruction_score.py        rewritten: score_calibration (US2), score_respondent, score_interpret (US3), score_compare, totals/spread
├── test_instruction_leak.py         NEW  vocabulary, sweeps A/B, the inflection tie to a fake judge, judged_fraction
├── test_instruction_brief.py        extended: no_claim_words; deciding_line off vector_verdicts; five-or-nothing
├── test_instruction_judge.py        NEW  reveals_solution wording, SAME = reveals, cache; isolation test untouched
├── test_instruction_validate.py     rewritten: the seven batch kinds; unknown kind → unmeasured by name
├── test_instruction_rescore.py      NEW  the refusal on a two-file v8 fixture bundle; scorecard-v9.json beside
├── test_instruction_models.py       extended: six classes; the v8 table refuses naming three classes and version 8; models-screen.json parses
├── test_instruction_report.py       NEW  register blocks per entry: 25 beside the registry, 23 beside the plan, the standings table; no score words
├── test_instruction_why.py          + marks:9
├── test_instruction_modules_import.py  MODULES: − align, + compare, registry, text; the v9 scorecard fixture
├── test_corpus_r3_shape.py          NEW  the real seven files: revision 3, 25 keys, plan ≤ 23, standings on 25, FR-009/FR-010/FR-011 facts (red until keel-cloud's r3 lands — named)
├── test_corpus_script.py            the r2 shape assertions skip by name once revision 3 is detected (Open item O-1)
├── test_instruction_align.py        REPLACED by test_instruction_text.py (reason written in its place)
├── test_instruction_reads.py        REPLACED (call 27's resolve_reads retires with align.py)
├── test_instruction_questions.py    REPLACED by test_instruction_prompts.py's QUESTIONS-less order
└── fixtures/
    ├── marks/calls-1-27.at-0165017.txt      the v8 judgement calls, extracted once, for SC-001
    ├── registry/slice.yaml                  a 25-key registry fixture (Lullaby values, hand-sized)
    ├── corpus/09-fixture-r3.yaml            one r3 entry: 12 people, 2 gate-No, 1 chipped, B2B off
    ├── corpus/10-fixture-r3-b2b.yaml        one r3 entry with persona.decision_maker: {role}
    ├── compare/09-fixture.out.json          an engine output that agrees; one that disagrees on two rows
    └── runs/v8-bundle/{manifest.json, scorecard.json}   marks_version 8, for the rescore refusal

runs/
└── DRIFT.md                         anything that surprised on a screen or the run

README.md, AGENTS.md                 the v9 gate: eight marks, the denominators, the three unscored screens, the rescore refusal; the run of record when spent
```

**Structure decision**: single project, the layout the repository already has. Three modules join
`instructions/` for the reasons research R15 gives (a stemmer, a registry with invariants, an
engine shim are each one thing); one leaves because the thing it aligned no longer exists.
`Makefile` is untouched: `instruction-screen` and `instruction-eval` already take every knob this
feature needs (`DRY`, `K`, `N`, `HOST`, `MODELS`, `WHY`, `MARKS`).

## Complexity Tracking

No Constitution Check violation to justify. (The three new modules are not a new layer; they are
the places three existing concerns were living inside the wrong file.)

## 1. The decisions worth writing down

### The nine v9 judgement calls are appended verbatim, and the first twenty-seven are pinned

`marks.py`'s docstring gains **28–36** in the words of `contracts/marks-v9.md` §3 — the table's
second column, one numbered paragraph each, prefixed `**v9**` and, where the founder decided it,
dated *2026-10-07* — and nothing above 27 is touched. SC-001's *byte for byte* is made testable the
only honest way: `tests/fixtures/marks/calls-1-27.at-0165017.txt` is extracted once from `master`
`0165017`'s `marks.py` and the test compares the live 1–27 against it. Call 22 stays between 16 and
17 (025 D7: the list is append-only and struck-nowhere, not sorted).

### `marks.toml` is the draft, byte for byte, and `DEFAULTS` follows it

FR-002. `golden_belief_recall` survives as a struck comment and no key; `DEFAULTS` in `marks.py` is
the eight keys with the draft's numbers; `tests/test_instruction_marks.py` asserts `load() ==
DEFAULTS` and that `golden_belief_recall` is **absent** — a v9 verdict cannot carry a value for it.
The draft's header already says `INTERPRET` and *there is no ANCHOR_READ constant* (A-1), so
"read as `INTERPRET`" costs no edit.

### The corpus revision is a keel-cloud commit, and this repository's tests read the real files

Research R2 and R14, and 025 plan §2 word for word: *the only thing that stops the two
repositories drifting is that this repository's tests read the real files.* `make unit` on this
branch is red from keel-cloud's r3 landing until the loader commit lands, and the tasks make that
window one commit wide. The hash mechanism (`sha256`, `verify_unchanged`) does not change; what
changes is what the digests are, and every v8 bundle on disk is a different measurement.

### `rescore.py` refuses, and this time the subjects moved as well as the corpus

v7 → v8 could not be re-scored because the corpus moved. v8 → v9 cannot be re-scored for two
reasons, and the refusal names both: *answered on screens v9 does not have, against corpus r2*.
The version is read **first**, before the corpus is loaded, so a v8 bundle is refused in one line
and never half-processed. For a v9 bundle `rescore` is the same free re-read it has always been,
with `compare.py` re-run (zero spend) and `scorecard-v9.json` written beside.

### The registry is read from the export, and the invariants are this repository's to check

FR-021. keel-cloud 058 exports `dimension-registry.json` beside `model-routing.json`;
`contract.read` loads it into `instructions/registry.py`'s `Registry`, which checks
`registry-schema.draft.md`'s seven invariants before a case is built. A registry that fails one is
a refusal naming the invariant and the key. `contracts/dimension-registry.yaml` is the design-time
golden every fixture copies a slice of, and no code reads it.

### `compare.py` is an engine shim, not an engine — and it runs on `DRY=1`

Research R3/R7. The eval builds `<in>` from r3, shells `screenContracts compare`, keeps both files
in the bundle, and diffs. Status and drift per dimension and verdict and deciding per vector are
**marked** (28 on one entry); counts, medians, proportions, `optionCounts`, bars and belief
sentences are **reported**. The `COMPARE` row is built at case-build time so the DRY path and the
real path are one code path — which is what makes `DRY=1 K=03-lullaby` the first thing that can
be green, before a template exists.

### `MODELS=exported` must refuse the v8 table for the right reason

Research R5. `models.CLASSES` tolerates the three dormant names (`assumptions`, `reframe`,
`questions`) so a v8 table still parses, and the *missing* check names `context`, `calibration`,
`respondent` and *table version 8*. Found by reading `models.parse` and keel-cloud's
`model-routing.json` (`version: 8`), not by a failed run — the inverse of 025 D13.

### `no_leak`'s list is the corpus's, its ties are the judge's, and the judge has one question

Research R8 and R15. `Entry.vocabulary()` stems the golden `solution_mechanism` and
`mechanism_terms`, subtracts the stoplist and every stem of the problem's own words (`context`,
`statements.problem`, `interpretations.problem`, every `story`), and keeps the **inflection
ledger** — the stems excluded only because their problem-world form differs by inflection. Sweep A
(mechanism stems in a PROBLEM calibration question or a Part-1 item) and sweep B (the founder's
label, phrase or number for dimension *d* in item *d*) are code; a ledger hit goes to
`judge.reveals_solution` once, cached, and counts in `judged_fraction`. Everything else in
`judge.py` is deleted with `align.py`.

### The chipped story builds no case, and that rule is the engine's too

FR-017 (decision 5). `Entry.readable()` = gate-yes ∧ `chip is None` ∧ story non-empty;
`build_cases` iterates it; `score_interpret` keys on the person and neither reads nor refuses a
`stage` or `anchorId`. Jonas Weber's golden `GUESSED` is a corpus fact `compare_correctness` checks
(the engine must count him nowhere), never a judgement the model makes. Lullaby's denominator is
9, not 10; the corpus-wide one is written into the v9 header when the other six entries exist.

### The three interpretation screens run everywhere and are scored nowhere

A-2, FR-021, decision 16. Built from the corpus's own `context`, `statements` and
`interpretations.problem`; sent, validated, rendered; feeding `rule_refusal_rate` and
`shape_refusals` only. Their product-word sweeps are the aggregate's rules (`X1`/`P1`/`M1`), not a
mark here — judgement call 10, three subjects wider, and the same shape `QUESTIONS` took at v8.

### Why the harness readers are an open item and not a task

Research R14. Eighty-seven call sites in `harness/` and `evals/` read the r2 shape and drive
**today's** product, which tracks A–C are replacing. Rewriting them here would be this spec
writing the journey's spec; carrying an r2 reader beside the r3 one would be a second frozen
corpus in all but name. So this plan keeps `make unit` honest with a **named skip** once revision 3
is detected, names the sibling (`030-journey-vectors`), and puts the choice in front of the
founder (O-1). It is the one place this plan asks rather than decides.

## 2. The Waits (HANDOFF §4), stated as this feature's prerequisites

| Wait | What this feature needs | Who provides it, where | What happens here until it lands |
|---|---|---|---|
| **W1 — the registry and the contract export** | `dimension-registry.json` beside the contracts; `InferenceScreen` += the five constants; `JobClass` += `CONTEXT`, `CALIBRATION`, `RESPONDENT`; contract export for the five new and two narrowed screens; `screenContracts validate` taking the new kinds | **keel-cloud 058** (track A), on its own branch | `contract.read` refuses by name; `validate` reports the kinds unmeasured by name; `make unit` is green on fixtures. **P2–P4 wait here; P1 does not.** |
| **W2 — the engine** | `screenContracts compare <in> <out>` | keel-cloud 058 | `compare_correctness` unmeasured by name → `DRY=1` writes `passed: false` and says why. **P1's independent test waits here.** |
| **W3 — corpus revision 3** | `03-lullaby.yaml` at `revision: 3` first, the other six after; `check_corpus.py` and `GoldenCorpusTest` reading r3 in the same commit series; headers recording the revision, the date and this spec | **keel-cloud, 058's branch** (research R2) — never this repository | the loader refuses `revision != 3` by entry; the real-file tests are red for one named commit (R14). **P1 waits on Lullaby; P4 waits on all seven.** |
| **W4 — the seven templates** | `context-interpret.md`, `problem-interpret.md`, `solution-mechanism.md`, `calibration-questions.md`, `respondent-questions.md` (new, byte-pinned in `GenerationPromptCutsTest`); `interpret.md`, `brief.md` (narrowed in place) | **keel-cloud 059–065**, one spec each, in the order 062 → 063 + 064 → 065 → 059–061 | `instruction.read` refuses by name per missing file; a screen cannot be built for a screen whose template is absent. **Each of P2–P4's screens waits on its own template.** |
| **W5 — the run of record** | every template green on its screen; all seven entries at r3; `MODELS=exported` carrying the three new classes | the founder, once, `make instruction-eval HOST=claude WHY=marks:9 MODELS=exported` | nothing is spent on the full run; **routing stays v8**; the ceiling is `claude-sonnet-5-5` at `medium` (A-4). |

The eval's loader refuses revision ≠ 3 by name; a run never silently measures the wrong corpus.

## 3. What is deliberately not built

- **No instruction file** — keel-cloud 059–065 (FR-025). This plan defines each file's screen,
  bars and order, and nothing else about it.
- **No corpus file in this repository**, and no fixture copy of one (FR-012; spec 021 deviation 3).
- **No Python port of the compare rules**, for `DRY=1` or anything (research R3).
- **No belief sentence composed here** (research R9): recorded in r3 by the checker.
- **No `make` target**, no new `WHY` event, no change to `why.py`, `runner.py` or the Makefile.
- **No rename of `INTERPRET`**, no `ANCHOR_READ` (A-1); no edit to `model-routing.json` (A-9).
- **No repair turn, no retry, no second run**; no re-score of a v8 bundle.
- **No rewrite of the journey's corpus readers** (Open item O-1).
- **No scoring of the three interpretation screens**, no golden question text, no mark on the
  register (calls 10, 28, 29).

## 4. Risks, and what each one costs

| Risk | Cost | What is done about it |
|---|---|---|
| 058 ships `compare` or the registry export in a shape this plan did not predict | `compare.py`/`registry.py` built against the wrong file | contracts/screen-shapes.md §5 is written as a **request**, the first task of US1 re-reads 058's actual CLI and export before a line of `compare.py` is written, and this plan is corrected (not the sibling). |
| r3 lands without `belief_sentence` or `interpretations.problem` (R9, R16) | `BRIEF` and `SOLUTION_MECHANISM` contexts cannot be built from the corpus alone | Open items O-2/O-3 are sent to the r3 writer before `03-lullaby` is written; the shape tests assert both keys on the real file, so the gap is red and named rather than silent. |
| The v8 table refuses `MODELS=exported` on every screen until 058's table | screens cannot be taken on the cloud's own table | By design (A-9); `contracts/models-screen.json` is the pin, and the certificate waits for the export (W5). |
| A screen of 9 or 27 cannot separate a fixed fault from a lucky sample (A-10) | a template passes its screen and fails the run | Named in the spec; the run is the certificate; a red mark on the run goes to `runs/DRIFT.md` and back to the template's own spec, never to the rubric. |
| `no_leak`'s stemmer is too eager or too lazy | a fault missed, or a tie that was a plain hit | The stemmer is five suffix rules in `text.py` with its own fixture test; the inflection ledger makes every judged tie visible in `judged_fraction`; a wrong list is a `DRIFT.md` finding about the ruler, fixed with a bump. |
| The harness readers go red on r3 (R14) | S-001/S-005/6/7/S-012 lose their script source | O-1: named skip with the reason; the founder decides the sibling's shape. |
| The run of record goes red on one mark | ~3 h and ~$15–20 | It is the measurement (G9); nothing is re-run to get a better number. |
| `make unit` red between keel-cloud's r3 commit and this branch's loader commit | a red window | One commit wide, named in tasks.md (G7). |

## 5. Open items (none blocks Phase 2 or US1)

- **O-1 — the harness readers of the r2 shape** (research R14). *Founder's decision.* This plan's
  position: a named skip once revision 3 is detected, and a sibling spec `030-journey-vectors`
  rewrites `harness/corpus_script.py`, `evals/corpus_scenario.py`, `evals/corpus_facts.py` and
  S-012's `ENTRY=` read against the vector product when keel-web's corridor lands. The alternative
  (an r2 reader kept beside the r3 one) is refused here for the reason stated.
- **O-2 — `founder_calibration[<key>].belief_sentence` in r3** (research R9). *Request to the r3
  writer (keel-cloud 058).* Recorded by `check_corpus.py`, never hand-written.
- **O-3 — `interpretations.problem` in r3** (research R16). *Request to the r3 writer.* The golden
  `PROBLEM_INTERPRET` sentence downstream screens read.
- **O-4 — the corpus-wide `INTERPRET` denominator and the ≈ 420 estimate** (research R13).
  *Counted when the six entries exist; written into the v9 header then* (US4.2).

## Post-design Constitution Check

Re-evaluated after Phase 1 (research.md, data-model.md, contracts/, quickstart.md): **G1–G10
PASS**, with the two notes recorded in the table (G4: design-time copies read by no code; G7: the
one-commit red window, named). No new gate was needed and none was loosened. Complexity Tracking
stays empty.
