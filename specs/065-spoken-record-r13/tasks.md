# Tasks 065

Built on keel-e2e-eval master `4e2d622` (the spec), branch `065-spoken-record-r13`, against keel-cloud-docs master
`6d1deb71` (registry revision 13 of record, `src/main/resources/keel/dimension-registry.json`; corpus revision 13;
`build/spoken-corpus.txt` regenerated from that master just before the build). keel-cloud-docs was read, never written.
`MARKS_VERSION` 20, unchanged; no mark's rule changed. Built by Claude Opus 5.5.

Worktree note: `stack.toml`'s four sibling paths are relative and wrong from `wt/`; all four were pointed at the
absolute checkouts under `git update-index --skip-worktree stack.toml` (keel-cloud alone was not enough: `make unit`
collects `tests/test_journey_coverage.py`, which validates every sibling) and **restored** (master's bytes,
`--no-skip-worktree`) before handing back. `.venv` was a symlink to the main checkout's, never committed.

## The counts (acceptance 1)

| | units | clean | `spoken_form` |
|---|---|---|---|
| master `4e2d622`, the real record held to the fixture registry and the fixed §5 table | 109 | 75 | 0.688 (34 faults) |
| what master's test asserted | 109 | 109 | 1.0 |
| this branch, the real record held to the registry of record | **109** | **109** | **1.0** |

74 composed items and 35 faces, as before; `03-lullaby` alone 15 units, as before. The 34 faults on master were
7 Current solution escapes (S6), 7 Existing sacrifice escapes (S6), 7 Buyer and payer (S7 + S8: the revised labels
split at their comma), 6 Compatibility (S7 + S8: the ability four split at *Yes, mostly*; 05-paidly's is a permission
and kept the registry's four) and 7 Commitment (S7 + S8: *Yes, I'd {step}* split at its comma, three bands read as
four). The test's asserted numbers did not move; the record's real numbers moved from 75 to 109 clean.

`make unit`: master 4 failed, 3067 passed, 53 skipped -> 065 3 failed, 3076 passed, 53 skipped (+8 tests, 47 in
`test_instruction_spoken.py`). The three still red are not this spec's -- see *Not done*.

## FR-1 The record reads the registry

- [x] T001 `instructions/spoken.py`: the fixed `ESCAPES` table is deleted. `registry_escape(registry, key)` is the
  escape the registry's row names; `served_escape(registry, key, entry)` the one the item is served and said with,
  read by the side keel-cloud serves it by (`CommercialChain.side`): Existing sacrifice under a `value_box` row on a
  cost stated before the chain is spec 077's *I can't recall*; Ability to pay on a consumer link *I can't say*.
- [x] T002 `S6` holds the item's `escape:` to the registry's row, the escape line *Or say {escape}.* to the served
  escape, neither escape among the options, and no escape line where nothing is served. A key off the registry is an
  S6 fault (no escape of record).
- [x] T003 `served_labels(registry, key, entry)`: the fixed answers; Compatibility's ability four beside them
  (`ABILITY_ANSWERS`, 123 FR-8, keel-cloud `ItemFrames.ABILITY_LABELS` on the registry's four codes); Commitment's
  *Yes, I'd {step}* and, when the list carries a smaller step, *Yes, after {smaller step} first* (118 FR-1, the step
  lowered as `BeliefSentence.lower`). `cloud_corpus.known_labels_for` reads them, so an option list is split into the
  labels keel-cloud served and S7 / S8 hold the count and options lines to the served number and labels.
- [x] T004 `S4` holds Commitment's options to eleven words (`STEP_OPTION_MAX_WORDS`; keel-cloud 118, the guidelines'
  §10), every other option to nine. See judgement call 3.
- [x] T005 `item_faults(item, registry, entry=None)` takes the registry it is held to; `score(cloud, corpus, *,
  entry_ids=None, registry=None)` holds each item to the entry's bound registry by default (the export's on a run, as
  `run.py` binds it).
- [x] T006 `cloud_corpus.REGISTRY_FILE` and `registry_of_record(keel_cloud)`: keel-cloud's `dimension-registry.json`,
  loaded and checked; the `real` fixture binds the corpus to it instead of the fixture slice.

## FR-2 What was on purpose, named

- [x] T007 `instructions/spoken.py`'s header and `tests/test_instruction_spoken.py`'s docstring name the five changes
  with their specs: Current solution *Someone else did it* (123 FR-3); Existing sacrifice *I don't know* in the
  registry, *I can't recall* served on a cost before the chain (115 / 123's escapes, `CommercialChain.side`);
  Compatibility's four to the condition's verb (123 FR-8); Buyer and payer's revised four (123 FR-5); Commitment's
  options from the step, three bands on a free step (118 FR-1 / FR-2) and held to eleven words. `KNOWN` stays `()`.

## FR-3 The guideline of record (findings for keel-cloud, not edited)

`canon/designs/spoken-questions-guidelines.md` at keel-cloud-docs `6d1deb71` (last touched `90fd6dc4`, 123's docs).
The amendments §10 and §15 record most changes, but the body tables still say the old words:

1. **Line 61** (§5 table): *Frequency, Existing sacrifice, Purchase friction | I can't recall* -- Existing sacrifice's
   registry escape is *I don't know* (the value box, keel-cloud 115, registry decision 24), with *I can't recall* kept
   only for a cost stated before the chain. **No amendment mentions this one at all.**
2. **Line 63** (§5 table): *Current solution | Someone else does the checking* -- superseded by §15 (lines 222-224,
   *Someone else did it*), the table not updated.
3. **Line 23** (§2 Options): *3 to 9 words ... at most five* -- Commitment's options are held to eleven (§10, line
   107), not reflected in the table.
4. **Line 92** (§8 Marks): *options 3–9 words, ≤ 5 (Price 6)* -- the same: no Commitment eleven.
5. **Line 24** (§2 Escape): *The set is fixed per dimension (§5). "I'd rather not say" ... do not exist.* -- §15 (lines
   220-222) brings *I'd rather not say* back on the gate (`RATHER_NOT_SAY`), and keel-cloud 115's value box carries it
   as a chip on a consumer link.
6. **Line 201** (§14): *its fixed four are unchanged* -- 123 FR-8 (§15, lines 230-233) drafts Compatibility's four to
   the condition's verb.

Two findings about keel-cloud's record itself, met while building:

7. **`build/spoken-corpus.txt`'s `escape:` line prints the registry's row, not the side served**
   (`SpokenGuidelinesCorpusTest` writes `c.dimension().respondent().escape()`, while the spoken line reads
   `CommercialChain.side`): every golden entry's Existing sacrifice says `escape: I don't know` beside `escape=Or say
   you can't recall.`. The eval reads it as written (judgement call 1); a structured `spoken-corpus.json` carrying the
   served escape would end the ambiguity (the follow-up spec 040 already named).
8. **The record does not carry §15's occasion escape**: `InterviewComposer.ownEscape` serves *Someone else did it that
   night* where the occasion is a time (03-lullaby's *night*), but the corpus test's `spokenFormOf` path does not apply
   it, so the record says *Or say someone else did it.* for all seven entries. The eval holds the record to what the
   record's own path serves (judgement call 2), so this is not a fault here; it is a gap between the record and the
   interview.

## FR-4 Tests

- [x] T008 the real record: 109 of 109 against the registry of record (`test_the_corpus_record_keeps_every_rule_...`),
  and each of the five changes pinned as the record and the registry carry them (`test_the_record_follows_registry_
  revision_13s_five_changes`); `ABILITY_ANSWERS` pinned to the registry's guidance and worked example on its codes.
- [x] T009 fixtures (stackless): a count line disagreeing with the served options is still S7 (Commitment's three
  bands said *four*; Compatibility's ability four said *five*), a missing *or* still S8; the escape moves with the
  registry (the same item clean under a row saying *Someone else did it*, S6 under 087's slice); a cost before the
  chain says *I can't recall*, on the chain the row's *I don't know*; Commitment eleven words kept, twelve S4, any other
  option ten S4; `served_labels`; the served options read back whole from a revision-13-shaped text.
- [x] T010 `make unit` once at the end (counts above).

## Judgement calls

1. **Named versus said.** The record's `escape:` field is the registry row's label (that is what keel-cloud's corpus
   test prints), and the escape line is the served side's. S6 holds each to its own source rather than both to one,
   so the record keeps every rule while still faulting an item whose named escape is not the registry's.
2. **Served means `CommercialChain.side`, not `ownEscape`.** `served_escape` mirrors the side the record's own
   `spokenFormOf` path reads (cost before the chain, consumer budget), and not the interview's occasion escape (finding
   8). Mirroring `ownEscape` would make 03-lullaby a fault of the record that the record's code never claimed.
3. **Commitment's eleven words is a sixth change, not in the spec's five.** Reading *Yes, I'd allow it to use the
   microphone at night* whole (ten words) for the first time made it an S4 fault at nine. keel-cloud 118 and the
   guidelines' §10 hold these two options to eleven (`SpokenForm.STEP_OPTION_MAX_WORDS`) and keel-cloud's own corpus
   test does too, so S4 follows the guidelines of record. S4 still means "at most the guidelines' words".
4. **The ability four as a constant, pinned to the registry.** The registry carries them in Compatibility's guidance
   prose and its Lullaby worked example, not as data; `ABILITY_ANSWERS` mirrors `ItemFrames.ABILITY_LABELS` on the
   registry's codes, and a real-registry test fails if the guidance or the example stop naming them. Which four an
   item is served (the verb picker) is not copied; the reader accepts either set's labels.
5. **No new rule.** The options are not checked against the registry's sets (that would be a new meaning); they are
   read back with the registry's labels, and S3-S8 hold them as before.
6. **The spec's `instructions/cloud.py` is `instructions/cloud_corpus.py`**, the module the test reads the record
   through; the registry of record is read there (`registry_of_record`).
7. **The overview's text** (AGENTS.md's `spoken_form 109 of 109`) still holds and was not edited.

## Not done

- `make unit` is not green: three tests stay red on master and here, none of them spoken --
  `test_backtest.py::test_every_backtest_entry_loads_in_backtest_mode`, `test_corpus_r11_shape.py::
  test_a_chain_entry_is_accepted_with_the_engines_reading[08-fresco-budget-AMOUNT_PERIOD]` and
  `::test_no_golden_or_back_test_entry_sits_on_a_bins_edge`. keel-cloud-docs `6d1deb71` (126's back-test edit) set
  Fresco's `persona.decision_maker.role` to *operations lead*, which is not in its `roles` (*contractor,
  superintendent*), and the eval's loader refuses it (spec 042; calls 49, 78, 110). Outside this spec's scope; either
  keel-cloud adds the role (or moves *operations lead* to the decider's `title`, 123 FR-10) or an eval spec reads it.
