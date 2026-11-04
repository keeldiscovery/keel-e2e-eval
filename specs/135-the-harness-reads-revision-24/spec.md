# Spec 135 -- The harness reads corpus revision 24

Owed by keel-cloud 215 (merged 2026-11-04, master `0464e20`): the fourteen gallery entries moved to revision 24 (every
row of spec 134's `corpus-rewording.md`, Table 1 and the shape changes); entries 22 to 35 stay at 23;
`canon/designs/measured-beliefs/backtest/CONSTITUTION.md` is the corpus writer's constitution.

## Rules

- **FR-1 The loader and the pins.** Everything that reads the gallery at revision 23 reads it at 24 (the other entries
  at 23, as keel-cloud's `VectorCorpusFixture` does): `instructions/corpus.py` / `screen_entries.py` loaders, the
  revision pins, and every fixture and test line in spec 134's Table 2 (79 lines: `tests/fixtures/gallery/*.json`,
  `test_reworded_row_108`, `test_seven_templates_115`, `test_cloud_205_208_mirror_132`, the harness code that quotes a
  row) moves to the revision-24 words. `make unit` green.
- **FR-2 The scripted walk.** `harness/vectors_script.py` (and whatever else types the entries' rows) knows the three
  new codes (`no_treasury_hire`, `no_tutor_to_book`, `phone_with_them`), Fresco's Purchase friction pick at index 0 of
  two items with the founder's 2 weeks, AirCaps' four Compatibility conditions, Issen's Compatibility pick on
  `speak_aloud`; the own-offer rows are gone, so `vectors_script.offer_rows` is empty on all fourteen and the walk's
  L32 expectation becomes "no own-offer row typed" (reported, not asserted).
- **FR-3 The constitution in the harness.** `quality/readers/dimensions.md` gains, under Prevalence, Frequency and
  Compatibility, the one-clause rule of keel-cloud 212 only when 212 merges (its own mirror spec); this spec adds a
  pointer at the head of the cards file to `CONSTITUTION.md` as the corpus writer's law, and the gallery README says
  an entry enters the gallery only through the constitution's gate (section 9).
- **FR-4 The gallery's recorded Fresco run** is re-recorded in the next quality cycle's walk, not here (paid); until
  then its fixture is marked `revision: 23` and the test that compares it is skipped with that reason, never
  hand-edited.
