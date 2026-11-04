# Tasks 135 -- The harness reads corpus revision 24

Branch `spec-135`, off `80771da` (the spec), in the worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-135`
(`.git` a file). Built 2026-11-04 (ET) against keel-cloud-docs master `0464e20f` (keel-cloud 215: the fourteen gallery
entries at revision 24, `CONSTITUTION.md`, the revision-23 records). Not merged; nothing paid (no walk, no reader, no
`claude -p`); no contract, rubric, card rule or `MARKS_VERSION` moved (v24 stands).

| Commit | What |
|---|---|
| `c7ae045` | plan.md; FR-1's loader (`GALLERY`, `GALLERY_REVISION`, `revision_of`); FR-3's pointers |
| `0b75179` | FR-1 / FR-2 / FR-4: the slice, Voltair's fact, `time_sourced`, `offer_expectation`, the pins, the six held at the Answer box, the Fresco run marked and its compare skipped, `tests/test_harness_reads_r24_135.py` |
| this commit | the last two pins (211's cards compare, r11's ten-word label), plan's judgement calls 3-7, these tasks |

## FR-1 The loader and the pins

- [x] T001 `instructions/corpus.py`: `GALLERY` (the fourteen, held equal to `gallery_names.toml`), `GALLERY_REVISION` 24,
  `revision_of(id)`; `_check_revision` reads 24 for a gallery entry and `REVISION` (23) for every other; a gallery file at
  23 is refused as *the gallery's rows before keel-cloud 215*, any other file at 24 as *the gallery's alone*. The module
  head says revision 24 and points to the constitution. `instructions/marks.py` gains the revision-24 paragraph (v24
  stands, the golden digests unchanged). `instructions/screen_entries.py`'s docstrings say 24 (Palus's two rows).
- [x] T002 `tests/fixtures/registry/slice.yaml`: Compatibility's `saves.max_words` 16 (keel-cloud 187's registry), which
  10-palus, 12-transload, 15-voltair and 19-veles need; `test_instruction_corpus_r11`'s refused label is 17 words.
- [x] T003 `corpus.R24_FACT_FOUR` / `r24_fact_read_as_three`: 15-voltair's fact on the four read as code's three, refused
  the moment a person picks `only_with_help` (judgement call 4).
- [x] T004 The Table 2 lines that read the corpus, moved to revision 24's words, each with why:
  `test_adoption_steps_112` (Codyco's first effort; the 171 run case reads the case's own typed rows),
  `test_advantage_belief_113` (Palus's two benefits, one row each: `PALUS_24`, `ROW_24`; a split is 3 rows for 2),
  `test_after_131` (Issen's first benefit *speaking practice any time*), `test_cloud_205_208_mirror_132` (no gallery
  entry types an offer, the five outside it do; Fresco's two rows, Expanse's budget line, Bidflow's trial left out; the
  22 -> 23 test on the r22 and r23 records), `test_money_cards_redrawn_118` (the gallery loads at 24; Voltair a fact;
  Fresco's belief and card on the Procore check), `test_instruction_brief_facts` (the card), `test_backtest`,
  `test_cycle_5_to_the_end_119` (21-codyco's refusal names the gallery's 24), `harness/vectors_script.py` docstrings
  (`offer_rows`, `kept_picked`, `current_solution_boxes`).
- [x] T005 The Table 2 lines left as they are (judgement call 5): the run records (`tests/fixtures/gallery/...`,
  `runs/08-fresco-choose-108`, `runs/13-aircaps-choose-108`, `runs/21-codyco-choose-104`, `typist/backtest-21-codyco-
  PROBLEM.json`, `cycle5/10-palus-solution.json`); the rule examples (`test_cloud_205_208_mirror_132`'s offer vocabulary
  and L32 note, `test_adoption_steps_112`'s 171 frame and clause cases, `test_after_130`, `test_after_131`'s `fact_said`,
  `test_cloud_200_mirror_129`'s K9, `test_seven_templates_115`'s condition kinds and its recorded Fresco beliefs,
  `test_reworded_row_108` and `test_choose_by_label_104`'s fold and drift cases from the walks of 2026-10-30,
  `test_phrase_is_the_peoples_093`, `test_reworded_founder_screens_116`, `test_web_164_mirror_129`,
  `test_cycle_5_to_the_end_119`'s Choose HTML, `test_dimension_cards_131`'s reader case, `test_reader_sees_screen_134`);
  `evals/corpus_scenario.py`'s notes on past walks; `quality/readers/dimensions.md`'s bad examples and AGENTS.md's
  history (Table 2's preface).

## FR-2 The scripted walk

- [x] T006 Nothing in the walk names a row or code by entry: the three new codes, Fresco's pick at index 0 of two with
  its 2 weeks (`kept_picked`, `saved_list.duration`), AirCaps' four conditions (pick 0), Issen's pick on `speak_aloud`
  (`pickedIndex` 1) arrive with the data -- held in `tests/test_harness_reads_r24_135.py`.
- [x] T007 `vs.offer_expectation` / `NO_OFFER_TYPED`: the L32 expectation *no own-offer row typed* on all fourteen,
  reported in the transcript (`own_offer`) and the bundle's markdown, never asserted; `offer_rows` empty on the gallery.
- [x] T008 `vs.time_sourced` stops at a sources file's `## Revision` heading (215's trace says *the founder's 2 weeks
  kept*; the 2 weeks stays the author's choice).

## FR-3 The constitution in the harness

- [x] T009 `quality/readers/dimensions.md`: *The corpus writer's law* above the first card (never handed to a reader;
  `test_cloud_211_mirror_133` compares the cloud's vendored copy without it -- the cloud's copy owes it).
  `instructions/gallery_names.toml` (the gallery's map) and `quality/CYCLE.md` (the gallery step): an entry enters only
  through the constitution's gate, section 9. 212's one-clause rule waits for 212's mirror spec.

## FR-4 The recorded Fresco run

- [x] T010 `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/backtest.json` `"revision": 23`;
  `test_gallery.test_the_interview_is_pinned_on_one_run` skipped with the reason; no recorded word edited.

## Left open

1. **Six gallery entries stop at load** (09-karsa, 12-transload, 13-aircaps, 14-code-four, 15-voltair, 20-lemma): their
   revision-24 Importance rivals outrun the 25-word Answer (26-30 words), so spec 067 FR-1's stop refuses the walk before
   any spend. Owed: shorter rivals in a keel-cloud corpus spec (and a constitution rule: the other difficulties fit the
   25-word Answer together), or a coordinator's call to let a back-test walk type the rest on the Check screen.
2. **15-voltair's respondent Compatibility row** records the four on what is now a fact; the corpus owes the three.
3. **The cloud's vendored cards** (`src/main/resources/keel/dimension-cards.md`) owe FR-3's pointer, with 211's example.
4. **The recorded Fresco run** is re-recorded in the next quality cycle's walk (paid, the founder's word).

## The gate

`set -o pipefail; make unit 2>&1 | tail -1`: **5352 passed, 85 skipped** (0 failed, 0 errors) against keel-cloud-docs
`0464e20f`. At the spec's base (`80771da`, the loader at 23 against canon at 24) the same suite read 145 failed /
5,178 passed / 85 skipped / 16 errors.
