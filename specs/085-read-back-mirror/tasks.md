# Tasks 085 -- The harness reads the read-back as keel-cloud 149 writes it

Branch `085-read-back-mirror` (worktree `wt/eval-085`, `.git` a file), off master `c474dfe` (087 merged and the
decisions' merged marks of 2026-10-29/30). Read only: keel-cloud-docs (live `ad5f6441`, and an exported snapshot at
`73426a67`, 149's merge, for the gate, below). `REVISION` 17, `MARKS_VERSION` 21, `INTERVIEWER_MARKS_VERSION` 12,
`RUBRIC_VERSION` 2 unchanged. **No paid call**: no walk, no reader, no adviser call, no model, no `make eval`. Nothing
merged or deployed; every commit pushed to the branch.

| Commit | What |
|---|---|
| `7eeba20` | FR-1: `vectors_script.sentence` (149's two sentences), `qualifiers.they`, `qualifiers.segment` / `segment_line` (148 FR-2's own pronoun), `tests/test_read_back_mirror_085.py` (FR-1 part) |
| `fe5096a` | FR-2: `qualifiers.parts` / `bare` / `thing_of_theirs` / `organisation_frame` / `organisations_clause` (+ `present_verb`, `ORGANISATIONS`, `singular`, `article`), `same_qualifier` and `in_core` on them, `vectors_script.condition_from(part, before)` / `drawn_condition`, the FR-2 tests |
| `1ed3e39` | FR-3: 077's and the vectors journey's sentence pins re-pinned, `leg_context`'s step names 149 |
| `25f549b` | FR-4: D-2026-10-29-01's mark confirmed; 087's two "nothing merged yet" pins moved, one test added |
| this commit | this file, `AGENTS.md` (the 085 paragraph; 087's dry-advise sentence brought to the merged marks) |

## Unit

The live keel-cloud-docs checkout (`ad5f6441`) is at corpus revision 19 and the harness reads 17 until spec 089, so
master is not green on it. The gate was run on each tree against keel-cloud-docs `73426a67` (149's merge, the sha this
spec names) exported by `git archive` into a scratch folder and named in `stack.toml` for the run only (restored after;
never committed), and against the live checkout.

| | passed | failed | errors | skipped |
|---|---|---|---|---|
| master `c474dfe`, keel-cloud-docs `73426a67` snapshot | 3,692 | **2** | 0 | 61 |
| **branch, keel-cloud-docs `73426a67` snapshot** | **3,709** | **0** | **0** | **61** |
| master `c474dfe`, live keel-cloud-docs `ad5f6441` | 3,428 | 81 | 40 | 206 |
| branch, live keel-cloud-docs `ad5f6441` | 3,444 | 79 | 40 | 207 |

**Master is red on the snapshot by two**, `test_decided_before_087.py`'s
`test_the_file_of_record_parses_...` (*nothing it names had merged when it was written*) and the acceptance's dry advise
(62 snoozed rows; 15 since the marks), both broken by master's `c474dfe`, which wrote the eight `merged` marks without
moving 087's pins. They are FR-4's own consequence, so FR-4 moves them (below). +17 on the branch = the 14 tests of
`tests/test_read_back_mirror_085.py`, 087's new test, and the 2 that were red. On the live checkout the branch's 79 failed and 40 errors are the
same set as master's (diffed by node id; master's two more are 087's pins): every error and 72 of the failures are
`CorpusError: ... revision is 19; this eval reads revision 17 only`, and the other seven are assertions on what
revision 19 and keel-cloud 158-160 moved (`test_backtest.py:76`, `test_corpus_r17.py:112` and `:200`,
`test_follow_up_ladder.py` x3, `test_interviewer_marks.py`'s `ONE_MORE` line) -- none in this spec's area. One new test
skips there (03-lullaby reads the revision-17 corpus), hence 207 skipped.

## FR-1 -- the mirror

- [x] T001 `vectors_script.sentence(core, condition, circumstance, job, window)`: *{Segment}. When {when}, they want to
  {what}, counting the last {window}.* -- the segment whole as `qualifiers.segment` composes it, a capital and a full
  stop; `with_when(circumstance)` with its first letter raised (*While running payroll, ...*); a comma and
  `qualifiers.they(job)`; *, counting the last {window}.* or *.* where `read_back` hands no window (spec 135's scope rule
  as before). The docstring names 149.
- [x] T002 `qualifiers.they` mirrors `ReadBack.they` with its three patterns: *want to* / *need to* / *try to* / *have
  to* / *must* -> *they {job}*; the third-person *wants to* / *needs to* / *tries to* / *has to* (149's judgement call
  1) -> *they want to* ...; *trying to* / *are trying to* -> *they are trying to ...*; a job opening *they* kept; a bare
  *to ...* -> *they want to ...*; *mustard* is no *must*.
- [x] T003 `qualifiers.segment` gains 148 FR-2's own pronoun (*, whose ...*, *and whose ...*), and `segment_line` reads
  `segment` as `ContextSlots.segmentLine` has read `ReadBack.segment` since 148 (judgement call 1).
- [x] T004 `tests/test_read_back_mirror_085.py`: 149's `ReadBackReadsOnceTest` word for word (Lullaby, 13-aircaps, a
  want of its own and every opener, *trying to*, *they* / *to* / *mustard*, *while*, money alone), 08-fresco on 149's
  slots, 03-lullaby as the journeys script it, the own pronoun, and `ReadBack.java` / `ContextSlots.java` held to the
  mirror's patterns and joins.

The sentences the tests assert:

- 03-lullaby (the journeys' slots, `read_back`): *First-time parents in the US, who have a baby under six months. When
  the baby cries in the night, they want to work out what the baby needs and settle them, counting the last 7 nights.*
- Lullaby (149's slots): *First-time parents in the US, who have a baby under six months. When the baby cries during the
  night, they want to work out what the baby needs and settle the baby, counting the last 7 nights.*
- 08-fresco (149's slots, the condition the mirror draws from the back-test entry's WHICH PEOPLE): *Construction
  superintendents at US general contractors, who have jobs that run on Procore or ACC. When the day's site walks are
  done and the photos and notes still have to go into the daily log, they want to keep an accurate record of the day's
  work on site, counting the last 5 working days.*
- 10-palus (the core as typed, code's draw said once): *Finance leads at venture-backed startups in the US within two
  years of a raise, banking with Mercury, Brex or similar. When the company decides where cash from a raise sits until
  it is needed, they want to keep the money from a raise safe and earning until the company spends it, counting the last
  3 months.*

## FR-2 -- the drawn condition

- [x] T005 `qualifiers.parts` mirrors `Qualifiers.parts` (`ITEM_OPENS`, `ITEM`, `LIST`, the two placeholder
  characters, Java's `String.split` dropping trailing empty parts): *Mercury, Brex or similar*, *OPERA Cloud, Sihot and
  Apaleo*, *Germany, Italy or France* stay one part; *cooks, cleaning or driving* is still split (149's judgement call
  2). `in_core` reads it in place of its own split.
- [x] T006 `qualifiers.bare` (*banking* is *bank*), read by `same_qualifier` as 149 reads it (149's judgement call 4),
  so `in_core` sees that Palus's core as typed says *work at a startup that banks with Mercury, Brex or similar*.
- [x] T007 The draw: `vectors_script.condition_from(part, before=None)` now draws, in the cloud's order after the
  negative and before *with no*, the size and the tool branch: `qualifiers.thing_of_theirs` (*whose jobs run on Procore
  or ACC* -> *have jobs that run on Procore or ACC*; *whose team shares a cluster* -> *have a team that shares a
  cluster*; `StrangerGrammar.presentVerb` mirrored as `present_verb` for its verb test), 131 FR-6's *at X that run Y*
  frame (`organisation_frame`, judgement call 2), and `organisations_clause` (149's judgement call 3: the head is the
  last `ORGANISATIONS` noun said before the clause, in the part or the founder's words ahead of it). So the tool branch
  draws only where the people are the subject (*who run on Procore* -> *run on Procore*).
- [x] T008 `drawn_condition` reads `qualifiers.parts` and hands each part the words said before it in its own text
  (WHICH PEOPLE, then the segment), as `candidates` does: Palus draws *work at a startup that banks with Mercury, Brex
  or similar*, 08-fresco *have jobs that run on Procore or ACC*.
- [x] T009 Tests: 149's `Fresco.theToolBranchDrawsOnlyWhereThePeopleAreTheSubject` and
  `Palus.theOrganisationsQualifierDrawsOnItsHeadNoun` mirrored, 08-fresco's and 10-palus's WHICH PEOPLE read from the
  back-test entries, Palus said once and the dropped core taking the clause after *, who*, `aListIsOnePart`, and
  `Qualifiers.java` / `ScreenResultApplier.java` held to the patterns and to the branch order.

**149's judgement calls the harness does not need** (no `candidates`, `lostQualifiers`, X8 or `settled` in the harness:
the journeys' conditions are `SEGMENTS`' scripted ones, and `drawn_condition` only words a finding): 5, the market read
on the place's own name (`placeName`; the harness's draw has no place branch); 6, a drawn condition the core already
says never displaces the model's (`settled`); 7 and 8, X8's narrowing to names and numbers (`namesKept`) and where the
Palus breach is read. 9 and 10 are keel-cloud's files.

## FR-3 -- the pins

- [x] T010 `tests/test_drawn_screener_seams_077.py`: 07-mulchrun's card = confirmed sentence, 146's two `in_core`
  sentences and the Pakistan pair, 05-paidly's read-back, *when* once (three sentences), and every corpus entry's
  `. When {circumstance}, they ` -- the new words, the rule each pins unchanged, the docstrings say why.
  `tests/test_vectors_journey.py`'s 07-mulchrun and 01-countly sentences likewise. `test_after_130.py`'s draws, 072's and
  scope's money-alone endings (*... matching what is on the shelves.*) and *, counting the last 4 weeks.* hold unmoved.
- [x] T011 The strict compare (`evals/corpus_scenario.leg_context`, and `_drift_96_guard` on money alone) reads
  `vs.read_back`, so it moves with the mirror; its step names 149's shape. **The six journeys** (S-005/006/007/014/015/016)
  carry no recorded sentence of their own: each asserts the card through `leg_context`, so none needed a pin.
- [x] T012 **The gallery fixture** (`tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/export/{plan,standings}.json`,
  `contextUnderstands`) and `tests/fixtures/sample/s006-reads.json` are recorded runs (a keel-cloud of 2026-10-22 and
  before); no test reads their sentence against the mirror, so they are left as recorded (rewriting them would falsify
  the record).
- [x] T013 **17-expanse** draws *have 100 or more GPUs* in keel-cloud (145's amount branch, which 149 left; named in
  149's *What did not hold*). The harness's 130-era draw never mirrored that branch, so it draws none from 17-expanse's
  WHICH PEOPLE, before and after this spec; `test_expanses_amount_is_not_the_harness_to_draw` pins both that and the
  cloud's branch unchanged.

## FR-4 -- decided before

- [x] T014 `quality/decisions.toml` D-2026-10-29-01 carries `merged = "73426a67"` (master `c474dfe`): confirmed.
- [x] T015 087's pins moved (judgement call 3): `test_the_file_of_record_parses_...` holds the eight marks of master (D-01,
  -02, -03, -05, -13, -14, -15, -19), each on a taken, spec-merged entry; the acceptance's dry advise reads the file as
  written (the marks stripped into a temporary copy) and still lists all 62 rows; the new
  `test_a_merged_decision_ends_its_snooze_on_the_file_of_record` reads the file of record: 15 rows snoozed, each by an
  entry still active, 47 adviser prompts (none made), 149's `COMMERCIAL · founder · - · context` first.

## Acceptance

- [x] `make unit` on the snapshot: 0 failed (table above).
- [ ] `make eval K=s005` and `K=s007` on the local stack at cloud `c1da0d05` or later and web master: **left for the
  coordinator.** The local stack was not up at build time (nothing on `localhost:18080` or `:5173`), and starting it is
  the coordinator's. S-007's chip reads the settled condition as 084 pinned it (`card_condition`, untouched).

## Judgement calls

1. **148 FR-2 mirrored with 149.** The spec reads "the segment as `qualifiers.segment` says it (146 FR-2, 148 FR-2
   unchanged)"; the harness had never mirrored 148 FR-2's own pronoun, nor `segmentLine` reading `ReadBack.segment`.
   Both are in 149's sentence, so they were added (no corpus row's condition opens with *whose* / *that* / *which*, and
   no core with *who*, so no journey's line moved).
2. **131's organisation frame added to the harness's draw.** `organisations_clause` sits after it in the cloud; without
   it *agents at hotel groups in Germany that run ...* would have drawn *work at a group that runs ...*, not the
   cloud's *work at a hotel group in Germany that runs ...*.
3. **087's pins moved here.** Master `c474dfe` (the marks) left 087's two pins red; FR-4 is that mark, so its commit
   carries them: the acceptance as written (on the unmarked file) and the file of record as it now is, side by side.
4. **The helpers live in `qualifiers.py`** (FR-2 names it), and `condition_from` stays in `vectors_script.py` where its
   callers are; its 130-era scope is kept (145's amount, relative-clause and place branches are still not mirrored).
5. **`drawn_condition` keeps its own 130 `QUALIFIER`** (no 131 relative clause), as before: it only names, in a
   finding, what X12 would draw where the page served no chip.

## What did not hold

- `make eval K=s005` / `K=s007`: not run (the stack was down; the coordinator's).
- Master is red by two on the snapshot (087's pins after `c474dfe`), so "master's counts as the last spec's tasks.md
  records them" (087: 3,694 / 0 / 61 on `f48f256e`) is not today's master; both baselines are recorded above.
