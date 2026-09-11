# Tasks: the short journey, a golden founder, and the cell sets that pay for themselves

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Branch**: `short-journey`

`make unit`: **821** before (820 passing and one stale assertion, T002), **911** after, green.
`actionlint` 1.7.12: clean.

## Phase 1 — read before writing anything

- [X] T001 keel-cloud `canon/designs/e2e-matrix-design.md` §5, §6.4 and §14 — what a cell is, what
      the three schedules were, where a verdict is recorded, and which decisions are marked
      **[overrulable]**. Answer: decision 4 is, in both directions, which is what makes the new
      sets an overrule rather than a contradiction.
- [X] T002 `specs/019-journey-through-a-host/` and `specs/020-matrix-workflow/` — the shape this
      repeats and the two runs of record it must not invalidate. **And one finding**: at `master`,
      `tests/test_stub_oidc.py::test_the_sign_in_step_clicks_a_link_and_then_the_founders_own_name`
      was failing, left behind by commit `87e968c` (which moved the chooser click from a visible
      name to `chooser_button_selector(founder.id)`). Fixed here rather than merged around, because
      `make unit` green is this specification's own gate.
- [X] T003 `evals/test_s012_journey_through_a_host.py` line by line: which assertions come before
      the first card (all of leg one, the executor, the pin) and which after.
- [X] T004 `harness/corpus_script.py` — `entry_for`, `founder_inputs`, `person_inputs`, `_pick`,
      `PersonInputs.written()`. The half a live run can use is exactly these four; `generate()` and
      everything under it is the *script's* half and a live run must never touch it.
- [X] T005 `evals/corpus_scenario.py` — how S-005/6/7 call the same three functions, so this one
      calls them the same way rather than a new way.
- [X] T006 `matrix/cells.toml`, `matrix/cells.py`, `tests/test_matrix_cells.py` — the three
      coverage rules as they were, and which of them survive (one: weekly is the product).
- [X] T007 `.github/workflows/matrix.yml` — the `select` gate, the cell's env, the summary job, and
      **the finding that the cell job checks out only the two public siblings**, so the nightly
      corpus cell of spec 020 could never have read the corpus. Fixed here (spec deviation 2).
- [X] T008 keel-cloud `canon/designs/measured-beliefs/corpus/03-lullaby.yaml` — the title, the
      market, the three statements, the one CONSUMER role, three anchors, and Amira Saleh, who
      wrote under all three.

## Phase 2 — the harness

- [X] T009 `harness/agent_host.py`: `LEGS`, `DEFAULT_LEGS`, `LEGS_ENV`, `UnknownLegs`,
      `journey_legs()`; `DEFAULT_ENTRY`, `ENTRY_ENV`, `journey_entry()`; `bundle_slug(host, legs)`
      suffixing only the short one.
- [X] T010 `harness/evidence.py`: `write_block`; `write_host` reseated on it.
- [X] T011 `Makefile`: `LEGS=` and `ENTRY=` on `eval-live`, with the commands written out above it.

## Phase 3 — the scenario

- [X] T012 `_land_the_card` split out of `_walk_stage_live`, called by both.
- [X] T013 The founder and the one person from the corpus; `_story_texts` and `_their_pick`;
      `payroll_exceptions` gone from the module.
- [X] T014 `if SHORT:` — the note, and the `else:` that is the whole of the rest of the journey,
      unmoved. The wire checks, the spend and the disconnect are outside the branch, so both
      lengths make them.
- [X] T015 The bundle: `versions.json`'s `journey` block, two more `facts.json` strings, the
      cell label, and the printed line.

## Phase 4 — the matrix

- [X] T016 `matrix/cells.py`: `Cell.legs`, the refusal, `as_dict`, `render`, and the six coverage
      rules with the reasoning in the docstring.
- [X] T017 `matrix/cells.toml`: four, six, eighteen — and a header that says who decided and when.
- [X] T018 `matrix/notify.py`.

## Phase 5 — the workflow

- [X] T019 `[skip e2e]` on the receiver's own push, read through the environment, `push` only,
      one line of summary.
- [X] T020 `KEEL_JOURNEY_LEGS: ${{ matrix.cell.legs }}` in the cell's env.
- [X] T021 The corpus sparse checkout, its token probe, its warning, and `stack.toml` pointed at it.
- [X] T022 The `summary` job: `permissions: {contents: read, issues: write}`, a checkout, a Python,
      the table written to a file, `red`/`ran_any` as outputs, and the four-verb `gh` case.
- [X] T023 `actionlint` clean.

## Phase 6 — the tests

- [X] T024 `tests/test_matrix_cells.py` rewritten to the six rules, plus the `legs` section — 66.
- [X] T025 `tests/test_journey_through_a_host.py` — the two axes, the shared card assertion, the
      corpus founder and the corpus person read through the real corpus — 74.
- [X] T026 `tests/test_matrix_notify.py` — 32.
- [X] T027 `tests/test_matrix_workflow.py` — 23, including the matcher run under bash.
- [X] T028 `tests/test_stub_oidc.py` — T002's stale assertion, corrected.

## Phase 7 — the documents

- [X] T029 `README.md`: the commands, the env vars, the new sets as a table, the issue.
- [X] T030 This specification, its plan and these tasks.

## Phase 8 — the runs, which are the founder's to spend

- [ ] T031 `make up`, `make eval-live K=s012 HOST=claude LEGS=short`, `make down` — the short
      journey, live, once. **Not run here.** It needs a credential in the caller's own shell
      (spec 019 T012) and it is about two premium requests or `$0.30`.
- [ ] T032 `make eval-live K=s012` at these commits — the full journey, to confirm the corpus
      founder walks it as the payroll one did. The founder's to spend.
- [ ] T033 The first cloud run of the new `per_change`, four cells, when the twin is on.
- [ ] T034 Whatever T031–T033 find → `runs/DRIFT.md`, `README.md`, and this file.
