# Spec 089 -- The harness reads corpus revision 19, the three moved controls, and the question frames in the people's words

Four keel-cloud merges of 2026-10-30 move what the harness pins:

- **158** (cloud master `e3d34831`, contract 46): frequency counts from 1 (`segmented_1_to_n`: `scale {min 1, max N}`,
  a longer window `number_with_unit` with `numeric.min 1`; a 0 is SHAPE_MISMATCH); importance asks one pick then one
  more (`pick_one_then_one`: the question *which one ...?*, `secondAsk {"And one more?", NOTHING_ELSE}`, the answer two
  `optionIds` or one with `chip: NOTHING_ELSE`; `ask: second` on the classify requests); the ITEM_MORE clip *And one
  more?* replaces *And which one more?*.
- **159** (cloud master `1cf2ebc3`, contract 47): relative advantage is `scale_four` (`a_lot_better`, `a_little_better`,
  `no_difference`, `worse`; `I can't tell` apart); `advantages`, `advantageIds`, `yes_no_per_benefit` and `benefit_first`
  are gone; the brief's line *N of M said it would have gone better, K of them a lot*; **corpus revision 19** cut with no
  golden row moved (every recorded `positive` had a ticked benefit, so every one is `a_lot_better`; the corpus holds no
  `a_little_better`); mirrors `corpus-r19/` and `backtest-r18/`; `check_corpus_r19.py` OK on 35.
- **160** (building): the question frames code writes, in the people's words (founder and respondent frequency open
  with the window, no *Think of one who*; current solution asks *How did {phrase} go?*; the prevalence example in
  founder-lists.md).
- **The five 0s.** `corpus-r19` records five people who answered 0 after a yes (04-linerly: Bruno Costa, Dmitri Volkov,
  Gwen Price, window 12 MONTHS; 05-paidly: Petra Novak, Talia Ben-David, window 3 MONTHS). The engine still reads them
  and the corpus is untouched; a journey replaying them on the wire is refused. The founder's call is open (drop them
  in a revision, or replay as *I can't recall*); until he decides, the harness replays those five as `CANT_RECALL`,
  named one by one in the scripted person's notes, and tasks.md says so.

## Rules

- **FR-1 `REVISION = 19`** in `instructions/corpus.py` (the 18 note kept, a 19 note: 159, the one mapping rule, no
  standing moved); a file at 18 refused by name. **Rule D19** (`tests/test_corpus_r19.py`): every entry read beside its
  revision-18 record (keel-cloud's `corpus-r18/` and `backtest-r18/`), every leaf difference one of 159's edits -- the
  revision line and header everywhere, the relative-advantage answers mapped by the one rule, `optionCounts` added on
  that row, two decision sentences reworded -- never a standing. The marks header's seven r19 digests (the sha256s
  159's tasks.md lists; `MARKS_VERSION` moves only if a mark reads a moved field). `instructions/registry.py`'s control
  and code tables (`benefit_with_advantages` gone, `scale_four` and its four codes; `segmented_1_to_n`;
  `pick_one_then_one` and `nothing_else`).
- **FR-2 Frequency from 1.** `harness/vectors_script.py` (`frequency_fits`, `Pick(scale=...)`, `as_wire`) sends 1..N;
  `harness/vectors_screens.py` taps the radio 1..N (the 0 is no longer drawn); the five 0s as above.
- **FR-3 One pick, then one more.** `harness/vectors_screens.py` and `evals/interviewer_leg.py` (`tap_pick_two`, the
  spoken pick) tap one, wait for *And one more?* (the clip on the AI link, the written prompt on text), tap the second
  or *Nothing else*; `evals/corpus_scenario.py`'s `PICKS_NEEDED` reads one pick plus NOTHING_ELSE as a whole answer;
  `harness/interviewer_fake.py` `MORE = "And one more?"`; `harness/classifier_guard.py` and `instructions/spoken.py`'s S7
  (*; pick two* is never said now; the transform stays `one_then_one_more`), with their tests.
- **FR-4 One scale.** Every journey that ticked a benefit answers the four-step scale instead (`vectors_script.py`'s
  question text and `advantageIds` gone; `vectors_screens.py`'s ticks; `interviewer_leg.py`'s six sites;
  `corpus_scenario.py`'s benefit block; `preludes.py`); `instructions/spoken.py`'s `yes_no_per_benefit` retired;
  `classifier_guard.py`'s two sites; the brief-facts mirror reads `{better, aLot, aLittle, noDifference, worse, n}` and
  the new line; the quality readers' anchors where a rubric anchor named the benefit tick.
- **FR-5 The frames.** Every pin on a served question that 160 moves (160's tasks.md names them: the six journeys'
  recorded questions, `interviewer_fake.py`'s lines, the gallery's expected interviews as data) re-pinned with why.
- **FR-6 Decided before.** `quality/decisions.toml`: D-2026-10-29-13, -14 and -15 gain `merged` with 158's and 159's
  shas; the five-0s question is added as a `held` entry (D-2026-10-30-01) for the founder.

## Acceptance

`make unit` green with ZERO failed (master's counts as the last spec's tasks.md records them); `tests/test_corpus_r19.py`
on the cloud checkout at 159's merge or later; then, on the local stack at the cloud sha that carries 160 and web at
135, `make eval K=s005`, `K=s006`, `K=s007` green with the three controls walked. Build after 086 and 088; FR-5 when 160
has merged (tasks.md says which parts went first). Build on the founder's word (the overnight run of 2026-10-29).
