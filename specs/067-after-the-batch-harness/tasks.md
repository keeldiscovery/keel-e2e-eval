# Tasks 067 -- After the batch of 2026-10-23: the harness half of keel-cloud 128

Branch `067-after-the-batch-harness` off master `da61f6c`. The cloud half is keel-cloud-docs master `423f0983` (spec 128,
corpus revision 15, `canon/designs/measured-beliefs/sim/check_corpus_r15.py`); keel-web 106 is a spec only on keel-web
master `bec3836` (nothing built). One commit per section below, in this order, each gated on
`.venv/bin/python -m pytest tests -q` and a case-insensitive grep of its output for `failed` / `error`.

Unit suite on master `da61f6c` against keel-cloud-docs `423f0983`, before any change: **42 failed, 2,921 passed, 195
skipped** -- every failure the revision refusal (*"revision is 15; this eval reads revision 14 only"*), the same stop
`make backtest DOOR=host ENTRY=09-karsa` meets on the main checkout.

## FR-6 -- entries revision 15 and the new fields (first: it unblocks every load)

- [x] T001 `instructions/corpus.py`: `REVISION = 15`; `_REVISION_OF[14]` names revision 14 as *before keel-cloud 128*
  (Issen's cost inverted, the Importance rivals over the 25-word box, no per-person segment answer).
- [x] T002 the per-person `condition` (rule Q of `check_corpus_r15.py`, mirrored in the reader): `YES` or `NO`, on the
  primary link only, and only where `context.condition` is recorded; `Person.condition` kept; `NO` is a person outside
  the segment (`in_segment` False, thanked at the chip and recorded apart), `YES` inside. An entry carrying both
  `condition` and the older `in_segment` that disagree is refused by name.
- [x] T003 the pilot opt-ins read as before (`pilot_opt_in`), now true on 12-transload's Nadine Fournier and Oluwaseun
  Adebayo (decision-maker link); a person whose entry opts in and whose done screen serves no pilot is a finding, not
  a silent pass.
- [x] T004 fixtures (`tests/fixtures/corpus/09-fixture.yaml`, `10-fixture-b2b.yaml`, `tests/fixtures/backtest/99-broken.yaml`)
  at revision 15; the registry slice unchanged (128 moved no registry json or yaml -- the slice is named here so the
  next reader does not look for an edit).
- [x] T005 `instructions/marks.py`'s header: a *Corpus revision 15* paragraph naming the seven golden files by sha256
  (canon bytes at `423f0983`, equal to `src/test/resources/keel/corpus-r15/`); v20 stands; the test reads the seven.
- [x] T006 D15 and Q mirrored: `tests/test_corpus_r15.py` -- the reader's Q refusals; the eval's own diff of every entry
  against the cloud's revision-14 mirrors (`corpus-r14/`, `backtest-r14/`) equals 128 tasks.md's listing exactly
  (10-palus 3, 11-issen 64, 12-transload 4, 13-aircaps 45, 17-expanse 3, 18-careforce 14, 19-veles 2, 21-codyco 2,
  25-bidflow 2, every other entry 1); and the cloud's own `check_corpus_r15.py` prints OK on all 35 (skipped by name
  where keel-cloud's checkout lacks it).
- [x] T007 the tests that read fourteen read fifteen; 13-aircaps carries no *Nothing* any more (128 FR-21), so the
  value box's NOTHING chip is read on 11-issen's Patrick Sorensen.
- [x] T008 the zero-spend rows held on the 128 build, which the bump un-skipped (they skip while the reader refuses the
  canon): 128 moved words, not numbers, and the eval's reading follows -- `brief_facts.bar_words` (128 FR-8
  `BriefFacts.barWords`: a bar line's amber is *Did not hold*, Purchase friction's held fear *Holding up*), the seven
  golden decisions' change sentences in 128's *only k of n ..., and m did not* (`ChangeSentences.namedAgainst`),
  and `spoken.served_labels` knowing 128's label sets (a fact's *Yes · Mostly · Partly · No*, Purchase friction for
  this purchase, Buyer and payer's distinct four). `brief_facts` 101 of 101, `report_overview` 49 of 49,
  `spoken_form` 109 of 109 -- as on master; no number moved.
- [x] T009 a person the entry answers NO whose page serves no segment chip (the chip is the model's to write) is walked
  inside on their recorded answers (`vs.inside_inputs`) and named as a finding.
- [x] T010a 123 T019's bins-edge property: 18-careforce sits on the 0.8 edge at revision 15 (Olga and Miguel outside,
  8 of 10) -- a back-test entry, no golden standing to move; named in the test, never a golden entry.

Measured: **3,112 passed, 53 skipped, 0 failed** (was 42 failed, 2,921 passed, 195 skipped); the 142 un-skipped are
the canon-reading tests the revision refusal had skipped.

## FR-1 -- picks are sent as written

- [x] T010 at load, on a back-test entry: Importance's Answer (`vs.answer_text`) names every founder item within the
  25-word box, or `vs.founder_inputs` stops with the label(s) the box drops named; any single list label over 25 words
  stops likewise. All 28 revision-15 entries pass (128 shortened six entries' rivals).
- [x] T011 the walk never swaps a pick: on a non-strict walk an option the page does not offer is dropped from the
  answer (the item's other picks kept; an item left with none is answered by its escape, as the unanswered item
  already is), and each such pick is a finding naming the dimension, the entry's label and what was served.
  `_on_the_offered_options` (the swap onto the item's first options) is deleted.
- [x] T012 as built: `vs.check_answer_box` runs first in `vs.founder_inputs` on every entry (golden too: 01-countly's and
  05-paidly's named sublists fit), so `test_every_backtest_entry_loads_in_backtest_mode` holds it; revision 14's
  12-transload read at 15 stops naming *Finding freight sitting at the wrong door*. Judgement call 7: pick_two needs
  exactly two (keel-web `interviewAnswers.ts`), so an Importance answer left with one is the item's escape, named.
  Unit: 3,114 passed, 53 skipped, 0 failed.

## FR-2 -- every founder rung is typed

- [ ] T020 on a back-test, Current solution's Check screen: every entry rung the drawn list does not carry is typed
  into a new row (*+ add*), in the entry's order; where the screen cannot hold them (the registry's `max_items`, or
  the add control gone) the walk stops naming the rung. `vs.rungs_to_type(entry, drawn, max_items)` is the pure rule.

## FR-3 -- a follow-up line belongs to a rung

- [ ] T030 the reader takes `follow_up: {dimension, text}` (dimension a registry key a follow-up is asked on, text
  non-empty) and keeps `Person.follow_up_dimension`; the walk types the line only when the served rung is that
  dimension, else skips and records it. Judgement call 3: a bare string is still read on revision 15.

## FR-4 -- for/against from the served bar

- [ ] T040 `interviewer_fake.Founder.current_line` (keel-cloud `Ladder`, spec 117 FR-3: an outcome above the
  founder's list's `line` is against); on a back-test the walk reads the stored Current-solution list's `line` off
  `GET calibration/PROBLEM` and the owed follow-up is computed on it; golden walks keep the registry's
  `outcome_1, outcome_2` (D4's line, 2 on every golden entry).

## FR-5 -- a needs-input question is answered once

- [ ] T050 the context step: while the card is awaited, the CONTEXT_INTERPRET interaction is read; on `AWAITING_INPUT`
  a back-test answers once from the entry's own fields (`POST inference-interactions/{id}/answers`) and records a
  finding with the question asked; a second ask, or any ask on a golden walk, stops at once naming the question --
  never a 660 s wait.

## FR-8 -- the spoken guard on the served record

- [ ] T060 on a back-test every served item of every link watched is read back through `spoken.item_faults` (S1-S10)
  into `backtest.json` / `backtest.md` with each stem's word count; a stem over 20 words is a red line in the
  transcript, not a note. `instructions/spoken.py` untouched; its 109 of 109 guard still passes.

## FR-7 -- the walks of the changed screens

- [ ] T070 judgement call 6: keel-web 106 is a spec only (keel-web master `bec3836`), so the context occasion field,
  the seed-name suggestion, the needs-input screen, the market step's *Another country* line, the friction row at
  phone width and the Insights footers have no selectors yet. What the harness can read without them is read on
  every back-test and recorded as findings: the consumer vocabulary (*decision-makers*, *the payer*, *per person*,
  *per company*, *your team*, *new money*) on a consumer study's served items; a plan screen after a closed price (an
  escape or *I wouldn't pay*); *People disagree* at or past a founder's bar in the brief's cards. Holding these on the
  golden seven and on 13-aircaps, 16-pairio, 21-codyco waits for web 106's build (left open below).

## The register's Re-run column

- [ ] T080 `python -m evals.backtest summary <log> <id>` (and so `scripts/backtest-host.sh`) prints, after FR-6's
  line, the **re-run row** the register needs: `entry · judged (to fill) · run id · door · decision · score · was`,
  the score the run's `backtest.json` carries (none today: a score is a judge's, so it reads *to be judged*) and *was*
  the previous row's score for that entry read from keel-cloud-docs
  `canon/designs/measured-beliefs/backtest/judgements/README.md` (the last row whose Entry cell is the id). The
  register is the cloud repo's and is never written here.

  The column's shape (for the parent session, who adds the rows): the register keeps its columns and gains **Re-run**
  between *Score* and *Zeros*; a re-run is a new row (rows are never rewritten) whose *Re-run* cell reads
  `after 128 · was <old score>` (e.g. `after 128 · was 60% (94/156)`), and the original rows' *Re-run* cells are empty.

## Acceptance

1. Unit suite green; the golden seven's numbers and marks unchanged on the 128 build (the revision-15 digests in the
   marks header). -- this build
2. `make backtest DOOR=host ENTRY=...` for 09-karsa, 10-palus, 11-issen, 12-transload, 16-pairio, 21-codyco and
   13-aircaps with no harness stop, each judgement's re-run row written. -- **owed to the parent** (after the merge;
   no live model runs in this build)
3. No queued chain whose command line carries the words `pytest evals`. -- held throughout (no stack booted)

## Judgement calls

1. **`condition` is the segment's chip, YES or NO.** Spec 067's *From the cloud build* paragraph calls it the
   Compatibility fact's four answers; the entries and the cloud checker's rule Q say otherwise (`YES` / `NO`, primary
   link, only where `context.condition` is recorded -- 11-issen and 18-careforce). The Compatibility fact's four
   (*Yes · Mostly · Partly · No*) are the cloud's labels on the registry's four codes, so the walk keeps sending the
   pick's code and clicks the served label for it; no entry field is needed for them.
2. **`condition` and `in_segment` are one fact.** `NO` is outside; both present and disagreeing is refused.
3. **A bare `follow_up` string is still read at revision 15.** Every one of the 28 back-test entries carries bare
   strings and the canon is keel-cloud's (128 tasks.md: *the shape is 067's*, not added to the entries). Refusing them
   would stop every back-test at load, which is the opposite of this spec's purpose. The reader takes the new shape
   and enforces it where written; the refusal of a bare string is owed to the revision that rewrites the entries.
4. **The eval has no `sim` of its own.** FR-6's *sim's checker diff exactly 128 FR-11's* is held by T006: the eval's
   diff of every entry against the cloud's revision-14 mirrors equals 128's listing, the reader mirrors rule Q, and
   the cloud's checker runs over all 35.
5. **The Re-run column is printed, not written** (the register is the cloud repo's, the parent's instruction).
6. **FR-7 waits for keel-web 106's build** for every screen that build adds; this build reads what the wire and the
   existing screens already show.

7. **An item the control cannot carry after the drop goes to its escape.** The alternative -- a neighbour -- is the
   swap FR-1 forbids; stopping the run loses a paid walk for one pick. The escape is named beside the dropped pick.

## Left open

- FR-7's holds on the golden seven and on 13-aircaps, 16-pairio, 21-codyco for web 106's screens (no selectors).
- Acceptance 2 (the host-door re-runs and the register rows): the parent's.
- The refusal of a bare `follow_up` string (judgement call 3): the revision that writes `{dimension, text}`.
