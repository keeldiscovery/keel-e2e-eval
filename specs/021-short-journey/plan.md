# Implementation Plan: the short journey, a golden founder, and the cell sets that pay for themselves

**Branch**: `short-journey` | **Spec**: [spec.md](spec.md) | **Tasks**: [tasks.md](tasks.md)

## 1. Where the code goes

| File | What it is |
|---|---|
| `harness/agent_host.py` | The journey's axes, all three in one module. `LEGS`/`DEFAULT_LEGS`/`LEGS_ENV`/`UnknownLegs`/`journey_legs()`; `DEFAULT_ENTRY`/`ENTRY_ENV`/`journey_entry()`; `bundle_slug(host, legs)`. Spec 019's plan already said this module is *the journey's*, not Copilot's; this widens it by two axes and no more. |
| `evals/test_s012_journey_through_a_host.py` | `LEGS`, `SHORT`, `ENTRY_ID` at import. `_land_the_card` split out of `_walk_stage_live`. `_story_texts` and `_their_pick` for the corpus person. `corpus_script.entry_for`/`founder_inputs`/`person_inputs` where `fx.founder()`/`fx.people()` were. One `if SHORT: … else: …` around everything after the first card. |
| `harness/evidence.py` | `write_block(run_dir, name, record)`. `write_host` becomes one call to it, and its own test still passes untouched. |
| `matrix/cells.py` | `Cell.legs` with a default; `LEGS`/`DEFAULT_LEGS` restated (not imported — see §2); the six coverage rules; `legs` in `as_dict` and in `render`. |
| `matrix/cells.toml` | The four/six/eighteen, and a header that says what the founder decided and when. |
| `matrix/notify.py` | `decide()`, `Plan`, `_issue_number`, `_truthy`, and a `main()` that prints JSON and writes the body to a file. |
| `.github/workflows/matrix.yml` | Four edits: the `gate` step's skip marker; `KEEL_JOURNEY_LEGS` in the cell's `env`; the corpus sparse checkout and its token probe; the `summary` job's checkout, Python, `permissions` and issue step. |
| `Makefile` | `LEGS=` and `ENTRY=` on `eval-live`, each with its default written out. |
| `tests/test_matrix_cells.py` | Rewritten coverage half; a `legs` section; `PER_CHANGE_FOUR`, a fixture file whose per-change set is right so that a nightly rule can be caught failing alone. |
| `tests/test_journey_through_a_host.py` | The two axes, the shared card assertion, and the corpus founder read **through the real corpus**. |
| `tests/test_matrix_notify.py` | 32 stackless tests: four branches, two edge cases, the body, and what `gh --jq` actually hands over. |
| `tests/test_matrix_workflow.py` | 22 stackless tests, and the one that matters **runs the workflow's own matcher under bash** against eight commit messages. |

## 2. The five decisions worth writing down

**The stopping point is a shared function, not a shared intention.** The founder's rule was
*"assertions in short mode are the same ones the full journey makes up to that point"*. The only
way to hold that is for there to be **one** assertion: `_land_the_card` is called by the short
branch and by `_walk_stage_live`, and a test asserts the file contains exactly one definition of it
and exactly one non-`_walk_stage_live` call. Two blocks that look alike would agree today and drift
the first time either is edited.

**`matrix/cells.py` restates `LEGS` rather than importing it.** That module is deliberately
stdlib-only — `select` runs it on a runner before the harness's requirements are installed, and
`make matrix-check` runs it on a Mac with no venv warmed. So the two values are written twice, and
one test imports both and asserts they agree, which is the cheapest form of the seam.

**`legs` is not part of a cell's id.** A cell's id is its job name, its artifact name, its
`KEEL_REMOTE_CELL` and the founder it registers with the twin's picker (design §4.3). The *same*
macOS Claude 3.13 cell appears short in `per_change` and full in `nightly`; making the length part
of the identity would make it two founders in the picker, and the founder reading the morning list
would see two rows for one machine.

**The issue's decision is a module and the issue's I/O is three `gh` calls.** Four branches and two
edge cases inside a `run:` block is four branches nothing checks — not `actionlint`, not `make
unit`, not a founder reading a diff. So `matrix/notify.py` decides and prints a plan, and the
workflow's `case` has one line per verb. The body goes through a **file**, never an argument: a
summary table is backticks, pipes and em dashes, and a shell is the wrong place to carry those.

**The corpus reaches a cell by sparse checkout, and a cell without it fails loudly.** The
alternative — a copy of the corpus in this repository — would be a second frozen set that could
drift from the one keel-cloud froze, which is the single thing freezing it exists to prevent. The
other alternative — falling back to the payroll fixture when the corpus is absent — would produce a
green bundle that names a founder it did not measure, which is worse than a red one.

## 3. What is deliberately not built

- **No `make` target of its own.** `K=` selects, `HOST=`, `LEGS=` and `ENTRY=` parameterise.
- **No edit to keel-cloud's design.** The amended sets are written down here and in the data file;
  keel-cloud's §5.2 is that repository's to amend.
- **No retry, anywhere.** Spec 016 FR-009 stands, in both lengths.
- **No new scored attribute.** S-012 is still unscored, for S-008's and S-009's reason.

## 4. Risks, and what each one costs

| Risk | Cost | What is done about it |
|---|---|---|
| The short journey misses a break the full one would catch | one night | Rule 4: `nightly` runs every per-change cell again at full length, so the exposure is bounded by a day and the rule is checked by `make unit` rather than remembered. |
| A cell cannot reach the corpus and every per-change cell goes red | a red matrix on a config fault | The workflow warns by name at the checkout step, the scenario fails with the directory it looked in, and the token is one the deploy job already needs. |
| The live model writes a questionnaire the corpus person's picks do not fit | nothing measured wrongly | The page's own first option is taken and the bundle says so, per selection. Nothing about a pick is asserted anywhere (FR-007). |
| The issue step opens an issue nobody wanted | noise in the founder's inbox | Every branch is a unit test, including the two silences; and `ran_any` makes a run that measured nothing say nothing at all. |
| `[skip e2e]` matches something it should not | a matrix that did not run when it should have | The real condition line is extracted from the YAML and run under bash against eight messages, including `[skip ci]` and `[SKIP E2E]`. |
| Neither the short journey nor the new sets have been run live | the first cell is the measurement | Deliberate, and the same position spec 020 shipped in. Everything provable for free is held by 911 stackless tests; the first paid run is the founder's. |
