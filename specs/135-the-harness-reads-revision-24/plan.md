# Plan 135 -- The harness reads corpus revision 24

Branch `spec-135` (worktree `wt/keel-e2e-eval-135`, `.git` a file), off `80771da` (the spec). Read only: keel-cloud-docs
master `0464e20f` (keel-cloud 215 merged: the fourteen gallery entries at revision 24 under
`canon/designs/measured-beliefs/backtest/`, `CONSTITUTION.md` beside them, the revision-23 records under
`src/test/resources/keel/backtest-r23/`). No stack, no model, no walk, no reader, no paid call, no key read; the unit
suite only.

## Where each FR lands

| FR | Where |
|---|---|
| FR-1 the loader and the pins | `instructions/corpus.py`: `GALLERY` (the fourteen, as keel-cloud's `VectorCorpusFixture.GALLERY`), `GALLERY_REVISION` 24, `revision_of(id)`; `_check_revision` reads 24 for a gallery entry and 23 for every other (22 to 35 and the golden seven), a gallery file at 23 and any other file at 24 refused by name. `instructions/screen_entries.py` reads through `corpus.load(..., backtest=True)` and moves by its docstring's quote alone. The pins and fixture lines of spec 134's Table 2 moved to the revision-24 words (tasks.md lists each), the run records kept as served (see the judgement calls). |
| FR-2 the scripted walk | `harness/vectors_script.py`: nothing in the walk names a row or a code by entry -- `founder_list`, `kept_items`, `kept_picked`, `offer_rows` read the entry -- so the new codes, Fresco's pick at index 0 of two with its 2 weeks, AirCaps' four conditions and Issen's pick on `speak_aloud` arrive with the data; the docstrings that quoted a revision-23 row move; `tests/test_harness_reads_r24_135.py` holds each of FR-2's facts on canon; the L32 expectation is reported, not asserted (`offer_rows` empty on all fourteen). |
| FR-3 the constitution | `quality/readers/dimensions.md` head: a pointer to `CONSTITUTION.md` (212's one-clause rule waits for 212's mirror spec); `instructions/gallery_names.toml` head (the gallery's map, the only place an entry is added) and `quality/CYCLE.md`'s gallery step: an entry enters only through the constitution's gate (section 9). |
| FR-4 the recorded Fresco run | `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/backtest.json` marked `"revision": 23`; the test that compares it to `expected-interview-fresco.json` skipped with that reason; neither file's words hand-edited. |

## Order

1. Plan; the loader (FR-1's code) and the suite read on canon at `0464e20f`.
2. The pins and fixtures that fail on revision 24, each moved to the revision-24 words with why; FR-4's mark and skip.
3. FR-2's tests; FR-3's pointers; tasks.md.

## Judgement calls

1. **A mixed folder, held by name** (keel-cloud 215's plan, call 4): `GALLERY` is a constant here as it is in keel-cloud,
   and a test holds it equal to `gallery_names.toml`'s entries, so a gallery that grows must move both.
2. **Run records are what was served on their day** (Table 2's own preface): a recorded run's `backtest.json`,
   `inputs.json`, `export/*.json`, the `runs/`, typist and cycle fixtures are not reworded; where a test reads a record
   against canon, the test is re-pinned (to the revision-23 record keel-cloud keeps, or skipped with its reason), never
   the record. The gallery's Fresco run and its pinned interview are FR-4's.
3. **The registry slice follows keel-cloud 187** (`tests/fixtures/registry/slice.yaml`): Compatibility's `saves.max_words`
   9 -> 16, the registry's own since 2026-11-01. Revision 24's conditions name the act and its object in 10 to 12 words
   (10-palus, 12-transload, 15-voltair, 19-veles), which the hand-sized slice, cut at keel-cloud 087, refused.
4. **Two things revision 24 does that the review did not foresee** (found by the suite on canon, not built around):
   - *Six gallery entries' Importance outruns the 25-word Answer* (09-karsa, 12-transload, 13-aircaps, 14-code-four,
     15-voltair, 20-lemma: 26 to 30 words where revision 23 held 18 to 25). keel-web refuses an over-long Answer (422
     `VALUE_OUT_OF_SHAPE`) and spec 067 FR-1's stop (`check_answer_box`) refuses such an entry at load, naming the row the
     Answer would drop, before any spend. The stop is kept -- a back-test walk types no Importance row on the Check
     screen (only the golden walk does, `IMPORTANCE_NAMED`), so loosening it would lose the row; the six are held by name
     (`R24_ANSWER_OVERFLOW`) and the corpus owes shorter rivals (or the walk a Check-screen path for them: the
     coordinator's call). Tests that walk every entry assert the stop for the six; tests about something else on AirCaps
     or Lemma set the box's check aside for themselves alone.
   - *15-voltair's tested Compatibility condition became a fact* (*had poles whose tops were clear of tree cover*;
     revision 23's *could be seen* was an ability) while its respondent row kept the registry's four. Code serves a fact
     three (`ItemFrames.conditionKind`, the eval's `spoken.condition_kind` its port) and nobody picked `only_with_help`,
     so the loader reads the row as served (`R24_FACT_FOUR`, `r24_fact_read_as_three`) -- spec 130's pattern, the record
     never rewritten -- and still refuses it the moment a person's pick is `only_with_help`.
5. **Table 2's lines that are not a corpus read stay.** Its own preface keeps the run records as served and the cards'
   bad examples and AGENTS.md's history as written; beside those, the lines that are a rule's worked example (the
   offer vocabulary's *A trial on one live job* -> *trial*, 171's ten-word clause, 131's `fact_said`, 115's condition
   kinds, 108's folding and drift cases from the walks of 2026-10-30) or a record of a past walk (`corpus_scenario`'s
   *150723Z* AirCaps and Pairio notes) quote a row to show a rule, not to read the corpus; rewording them would make
   them test nothing or say what never happened. Every line that reads the corpus moved (tasks.md lists both).
6. **The recorded Fresco run** (FR-4) is marked in its own `backtest.json` (`"revision": 23`); its pinned interview
   (`expected-interview-fresco.json`) is the run's export, kept with it, and `test_the_interview_is_pinned_on_one_run`
   is skipped with the reason. The tests that read the record as a record (115's beliefs, 112's frame) still read it.
7. **Fresco's Purchase friction time** (`time_sourced`): revision 24's sources file traces the rows it moved under
   `## Revision 24`, one of which says *the founder's 2 weeks kept*; that trace is no source, so the read stops at a
   `## Revision` heading (the 2 weeks stays the author's choice, as spec 130 read it).
