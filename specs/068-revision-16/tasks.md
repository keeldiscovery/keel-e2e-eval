# Tasks 068 -- Corpus revision 16 and the walks of keel-web 106's screens

Branch `068-revision-16` off master `876e95d` (worktree `wt/eval-068`). The cloud half is keel-cloud-docs master
`efdd37bf` (spec 129, corpus revision 16, `canon/designs/measured-beliefs/sim/check_corpus_r16.py`, the mirrors
`src/test/resources/keel/corpus-r15/`, `backtest-r15/`, `corpus-r16/`, contract 36 in `canon/openapi-v2.yaml`); the web
half is keel-web master (`3651081`, 106 built, contract 36 vendored: `OCCASION_ON_THE_WIRE = true` in
`src/lib/contextOccasion.ts`), its selectors in `specs/106-after-the-batch-web/tasks.md`. One commit per section below,
in this order, each gated on `.venv/bin/python -m pytest tests -q` and a case-insensitive grep of its output for
`failed` / `error`. No `make backtest`, no live model: the host-door re-runs are the parent's.

Unit suite with `REVISION = 16` alone, before any other change: **226 failed, 2,711 passed, 53 skipped, 191 errors**
(the fixtures at 15 -- 282 of the errors' lines are the fixture refusal --, `test_corpus_r15.py` diffing against r14,
the marks header's digests at r15, and the spoken record read with 128's Commitment options).

## FR-1 -- revision 16 (first: it unblocks every load)

- [x] T001 `instructions/corpus.py`: `REVISION = 16`; `_REVISION_OF[15]` names revision 15 as *before keel-cloud 129*
  (112 back-test Commitment picks `yes_after_trying` on a step-alone list); the module's account gains revision 16.
- [x] T002 fixtures (`tests/fixtures/corpus/09-fixture.yaml`, `10-fixture-b2b.yaml`, `tests/fixtures/backtest/99-broken.yaml`)
  at revision 16; the registry slice (`tests/fixtures/registry/slice.yaml`) unchanged -- 129 moved no registry json or
  yaml (`git diff 423f0983 efdd37bf` names none), named here so the next reader does not look for an edit.
- [x] T003 `instructions/marks.py`'s header: a *Corpus revision 16* paragraph naming the seven golden files by sha256
  (canon bytes at `efdd37bf`, equal to `corpus-r16/`); v20 stands; the two cut Commitment options named as served words.
- [x] T004 the golden mirrors: `spoken.served_labels` writes Commitment's options as 129 does (`ItemFrames.firstYes` /
  `secondYes` / `cutToFit`, FR-15: the step cut by its trailing phrase to its share of nine; FR-9: never *first first*),
  so the record is read back whole -- 03-lullaby's *Yes, I'd allow it to use the microphone* and 02-compliancelog's
  *Yes, after a look at it first* (word changes only).
- [x] T005 `tests/test_corpus_r15.py` becomes `tests/test_corpus_r16.py`: D16 mirrored -- every entry beside the cloud's
  r15 mirrors, every difference the revision line or a step-alone back-test entry's `yes_after_trying` -> `yes_start`,
  the moved picks per entry exactly 129 T028's listing (112, Issen's seven by name), nothing else; the cloud's
  `check_corpus_r16.py` prints OK on all 35; all 35 load at 16 (the 28 in back-test mode) and r15's 11-issen is refused
  by name; 067's rule-Q, answer-box, rung, follow-up, needs-input, spoken-guard, changed-screen and register tests kept.
- [x] T006 the tests that read fifteen read sixteen (`test_corpus_r11_shape`, `test_instruction_corpus_r11`'s refusal
  table gains revision 15, `test_instruction_marks`, `test_instruction_spoken`'s Lullaby Commitment).

Measured: **3,131 passed, 53 skipped, 0 failed, 0 errors**; the grep clean. (The rename of `test_corpus_r15.py` to
`test_corpus_r16.py` rode in the tasks.md commit, content unchanged there; its D16 content is this section's.)

## FR-5 -- contract 36

- [x] T010 wherever this repository reads `ContextFields`: the context Save's PUT (`Corridor._save_context`) records
  the fields the page sent (`sent`) and `occasion` apart (contract 36: present once the founder's field holds one; a
  422 `TEXT_REFUSED` past eight words keeps its body); the confirmed context's GET is read with `fields.occasion` (the
  founder's, else the noun the job derived, absent for none or *time*) into `j.screens["context_wire"]` with every PUT's
  occasion. Nothing in this repository names the contract version as a number to bump (no vendored openapi copy; the
  `contract 33` / `contract 35` comments name where a rule came from, not the wire today), so none moved.
  `tests/test_revision_16_walk.py` (stub page). Unit: 3,132 passed, 53 skipped, 0 failed.

## FR-2 -- the spoken mirror follows the served escapes

- [ ] T020 `instructions/spoken.py`: the escape an item names is the served one where the side is served apart --
  Ability to pay on a consumer link is the budget item, *I can't say* (the guard called Issen's clean run RED on the
  registry's *I can't recall one*); Commitment's is none (129 FR-9's escape open, T025 there), an escape served on it a
  fault.
- [ ] T021 S4 counts Commitment's options whole at nine (`STEP_OPTION_MAX_WORDS` 11 -> 9, 129 FR-15); `spoken_form`
  stays 109 of 109 on the golden corpus.

## FR-3 -- the moved people's lines

- [ ] T030 the reader keeps each revision-16 back-test entry's *Changed:* people (the entry's own header: the 112
  whose Commitment pick moved), refusing a named person who is not in the entry or whose pick is not `yes_start`.
- [ ] T031 a moved person's bare line written for the second yes -- the line the r15 walk owed on Commitment (their
  picks read with the r15 answer, which no served option carried) -- belongs to Commitment's rung: typed only where the
  served follow-up lands on Commitment (their *yes_start*), otherwise skipped with a finding (067 FR-3's machinery),
  never typed on another rung. A moved person whose line the r15 walk owed elsewhere keeps their line as before.

## FR-4 -- the walks of keel-web 106's screens

- [ ] T040 the reads (106's selectors): the occasion field (`context-occasion`) drawn from `occasion.noun` and sent on
  the PUT; the gate's No label (*I didn't* where served); the idea-name box empty with `idea-name-suggestion`; the
  needs-input screen (`context-needs-input`) answered once through the page; the *Another country* line
  (`market-other-line`) and the currency list opening on the country's own (`market-other-currency`); the Overview's
  row words (`a.rp-row[data-dim] .rp-rs`) and price tile, the Insights footers (`.rp-tookby`) and GUESSED words
  (`insights-guessed`); the friction row's status column at 390 (`.rp-rv` / `.rp-rs` never overlapping).
- [ ] T041 the holds: on the golden seven (strict) what 106 must draw is held; on the back-tests each read is a
  finding into `backtest.json` / `backtest.md` (`changed_screens`), never a stop.

## Acceptance

1. Unit suite green; the golden seven's numbers and marks unchanged on the 129 build (v20 stands); S-005, S-006, S-007
   green on the local stack with the fake interviewer.
2. Every revision-16 entry loads (a unit test loads all 35, the 28 in back-test mode).
3. No queued chain whose command line carries the words `pytest evals`.
