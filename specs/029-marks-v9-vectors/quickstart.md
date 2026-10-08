# Quickstart: proving marks v9 end to end, cheapest first

**Branch**: `029-marks-v9-vectors` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

Every scenario below is runnable; the first four spend nothing. Expected outcomes are the spec's
success criteria, by number. Paths are from the repository root; the keel-cloud checkout is the
one `stack.toml` names (`../keel-cloud`).

## Prerequisites

| For | What must be true | Where it comes from |
|---|---|---|
| S0, S1 | `make venv` once; Python 3.12 (floor 3.11, `tomllib`) | this repo |
| S1–S4 | the keel-cloud checkout is on **058's branch** with: the exporter writing `dimension-registry.json`; `screenContracts compare`; `03-lullaby.yaml` at `revision: 3` | keel-cloud 058 (track A) and its corpus commit (research R2) — **the Waits** |
| S3 | the template under screen exists in `src/main/resources/keel/inference-instructions/` | keel-cloud 059–065, one each |
| S3, S4 | a logged-in `claude` CLI on `PATH`; `CLAUDE_CODE_EFFORT_LEVEL` **unset** | the founder's shell |
| S4 | all seven entries at r3; `check_corpus.py` green on each; every template screened green | the Waits, in full |

## S0 — the unit gate (free, always)

```sh
make unit
```

**Expect**: green at every commit on this branch (SC-002), with the r3 loader, the registry
invariants, the four scorers, the five-mark brief, the models classes and the rescore refusal each
held by a fixture. **Known red window** (research R14): between keel-cloud's r3 commit landing and
this branch's loader commit, the tests that read the real seven files are red, one commit wide and
named in tasks.md.

## S1 — the rubric, the loader, the engine: `DRY=1` (free; US1)

```sh
make instruction-eval DRY=1 K=03-lullaby
```

**Expect** (SC-003): the header prints the eight screens' context keys from the export and the
registry version; one prompt per kind is printed; the footer reads **19 cases** at N=1 — 3
interpretation, 3 calibration, 3 respondent, 9 `INTERPRET` (none for Hugo Laurent, Leo Martins or
Jonas Weber), 1 brief — plus the `COMPARE` row; *nothing was called and nothing was spent*; and
`runs/<stamp>-instructions/scorecard.json` carries `compare_correctness` **28 of 28** with every
model mark `unmeasured` and `verdict.passed: false` by name.

Three refusals to see on the way, each one line, each by name:

```sh
# a corpus entry still at revision 2 (point stack.toml, or a copy of it, at a master checkout)
.venv/bin/python -c "from instructions import corpus; from stack.config import load_config; corpus.load(load_config().keel_cloud)"
#   -> CorpusError: 03-lullaby: revision is 2; this eval reads revision 3 only (spec 029 FR-006) …

# an export without the registry
#   -> ContractUnavailable: <dir> carries no dimension-registry.json -- keel-cloud 058's exporter writes it beside model-routing.json …

# the v8 table through MODELS=exported
make instruction-eval DRY=1 K=03-lullaby MODELS=exported
#   -> ModelsUnavailable: classes says nothing about context, calibration, respondent (table version 8) …
```

## S2 — the rescore refusal (free; US1, SC-004)

```sh
.venv/bin/python -m instructions.rescore runs/20261001T043420Z-instructions
```

**Expect**: exit 2 and one line — *`runs/20261001T043420Z-instructions` was scored at
`marks_version` 8: answered on screens v9 does not have, against corpus r2. Not re-scored.* The
bundle is untouched. (Unit test: a two-file fixture bundle; the real one lives only on the
founder's disk.)

## S3 — one template, one screen (spends ~$0.30–$3; US2/US3/US4)

In the order FR-027 fixes — 062, then 063 and 064, then 065, then 059–061 — each on `03-lullaby`
at N=3. `MODELS=exported` once 058's table carries the three new classes; until then the pin file:

```sh
M=specs/029-marks-v9-vectors/contracts/models-screen.json
make instruction-screen K=03-lullaby/CALIBRATION HOST=claude N=3 WHY=instruction:calibration-questions.md MODELS=$M
make instruction-screen K=03-lullaby/RESPONDENT  HOST=claude N=3 WHY=instruction:respondent-questions.md  MODELS=$M
make instruction-screen K=03-lullaby/INTERPRET   HOST=claude N=3 WHY=instruction:interpret.md             MODELS=$M
make instruction-screen K=03-lullaby/BRIEF       HOST=claude N=3 WHY=instruction:brief.md                 MODELS=$M
make instruction-screen K=03-lullaby/CONTEXT_INTERPRET  HOST=claude N=3 WHY=instruction:context-interpret.md MODELS=$M
make instruction-screen K=03-lullaby/PROBLEM_INTERPRET  HOST=claude N=3 WHY=instruction:problem-interpret.md MODELS=$M
make instruction-screen K=03-lullaby/SOLUTION_MECHANISM HOST=claude N=3 WHY=instruction:solution-mechanism.md MODELS=$M
```

**Expect**, per screen (SC-006 to SC-009): calibration — 9 calls, `dimension_coverage` 1.00 (25 of
25, three times), `option_validity` 1.00 over 75, `no_leak` 1.00 over 27, `shape_refusals` 0,
`rule_refusal_rate` 0 of 9; respondent — 9 calls, coverage 1.00 over 69, validity 1.00 over 69,
`no_leak` 1.00 over 93 sweeps; `INTERPRET` — 27 calls, `anchoring_accuracy` ≥ 0.90 with
`guessed_precision`/`guessed_recall` beside it, `missing_ids`/`extra_ids` empty; brief — 3 calls,
`brief_paragraphs` 3 of 3 on five marks; each interpretation — 3 calls, `shape_refusals` 0, rate 0
of 3, rendered on `register.html`. **Every screen comes back `passed: false`** with the other six
entries and the unselected marks unmeasured (SC-010): a screen is never a run of record. A template
that misses is edited on **its screen's** evidence and screened again (FR-026).

The one permitted `high` measurement (FR-028), reported in `runs/DRIFT.md` and never routed:

```sh
# a copy of models-screen.json with "efforts": {"claude": {"standard": "high"}}
make instruction-screen K=03-lullaby/CALIBRATION HOST=claude N=3 WHY=new-model:claude:claude-sonnet-5-5 MODELS=<that-file>
```

A whole-entry screen (57 calls) is allowed for shopping and is also never a run of record:

```sh
make instruction-screen K=03-lullaby HOST=claude N=3 WHY=contract:dimension-registry.json MODELS=$M
```

## S4 — the run of record (spends ~$15–20 and ~3 h; US4, the founder's to type)

After **all seven** templates have passed their screens and **all seven** entries are at r3:

```sh
cd /Users/athulrajeev/Documents/projects/keel-e2e-eval
make instruction-eval HOST=claude WHY=marks:9 MODELS=exported
```

**Expect** (SC-011, SC-012): `WHY=marks:9` is accepted at the door (and refused on any `-k`
screen); `MODELS=exported` reads keel-cloud's own table (which by then names `context`,
`calibration`, `respondent` — otherwise the run refuses before spending); ≈ 420–480 cases at N=3
(research R13), `shape_refusals` 0, `rule_refusal_rate` ≤ 0.02 over ≈ 510 judged answers,
`compare_correctness` 196 of 196, `judged_fraction` reported; `verdict.passed: true` on all eight
marks at `MARKS_VERSION` 9. Then: the bundle, its time and price into `README.md` beside the v8
record (414 cases, 3 h 11 m, $15.41); anything that surprised into `runs/DRIFT.md`. **A red mark is
a finding, not a reason to run again.** Routing stays v8 until this bundle exists.

## What never happens here

No corpus file is written in this repository; no `model-routing.json` is edited; no run is taken on
a schedule or in CI; `rescore.py` is not an escape hatch across the bump; the three interpretation
screens are never scored; `CLAUDE_CODE_EFFORT_LEVEL` is never exported near any of the above.
