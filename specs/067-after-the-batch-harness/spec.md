# Spec 067 -- After the batch of 2026-10-23: the harness half of keel-cloud 128

keel-cloud 128 (and keel-web 106) fix what fourteen back-tests said about Keel's questions and brief. This spec is the
harness's share: the lags the judges found in how the back-test types a person's file, plus the walks of the changed
screens. Done on master during the batch and kept (not re-specified here): the escaped up-front-then price's plan
screen, the Another-country market path and its English, D19's own-currency allowance, the walk's wait for the
screen to move after Next, the server's follow-up rung accepted with a finding, the unanswered item's escape, the
named-idea tolerances, the price tile under the ladder.

## Rules

- **FR-1 Picks are sent as written.** The Importance box's 25-word cap dropped a founder item on Veles, Codyco and
  Transload, and the harness then swapped the person's pick for a neighbour: an entry label over 25 words stops the run
  at load with the label named, and a pick the page does not offer is a finding, never a swap (128 FR-17, FR-20).
- **FR-2 Every founder rung is typed.** The Current-solution Check screen types all of the entry's rungs on a
  back-test (Pairio typed two of five, Veles lost the terms rungs); a Check screen that cannot hold them stops with
  the rung named (128 FR-16).
- **FR-3 A follow-up line belongs to a rung.** The entry carries `follow_up: {dimension, text}` per person; the walk
  types the line only on that rung (master already skips on another rung) and the corpus reader refuses a bare
  string (128 FR-14, Careforce: Commitment answers filed under Purchase friction).
- **FR-4 For/against from the served bar.** Whether a pick counts against is read from the served item's bar, not
  the entry's code (128 FR-16, Pairio: *Found it, logged a line or two* counted for the founder on the served bar).
- **FR-5 A needs-input question is answered once.** On a back-test the context interpret's `NEEDS_INPUT` is
  answered from the entry's fields once, then recorded as a finding; the walk never waits 660 s on it (128 FR-15).
- **FR-6 Entries revision 15 and the register.** `instructions/corpus.py REVISION = 15`, fixtures and the slice to
  match, `sim`'s checker diff exactly keel-cloud 128 FR-11's; 18-careforce's Olga and Miguel chips follow their
  stories; the judgement register gains a *Re-run* column and `make backtest` writes the new score beside the old
  when an entry is re-run on the 128 build.
- **FR-7 The walks of the changed screens.** The context screen's occasion field, the consumer vocabulary, the verdict
  words, the Insights footers, the friction row at phone width, the seed-name suggestion, the needs-input screen, the
  market step's *Another country* line, the closed price item (no plan screen) -- each read back by the walk and held
  on the golden seven and on 13-aircaps, 16-pairio, 21-codyco.
- **FR-8 The spoken guard on the regenerated record.** `instructions/spoken.py` at 109 of 109, and on a back-test
  every served item's `spoken` read back with no S1–S8 fault; the record names the stem length so a 21-word stem is a
  red line, not a note.

## Acceptance

1. Unit suite green; the golden seven's numbers and marks unchanged on the 128 build (revision 15 digests in the
   marks header).
2. `make backtest DOOR=host ENTRY=…` for 09-karsa, 10-palus, 11-issen, 12-transload, 16-pairio, 21-codyco and
   13-aircaps completes with no harness stop; each judgement's re-run row written.
3. No queued chain whose command line carries the words `pytest evals` (the runner's own wait pattern self-matches).
