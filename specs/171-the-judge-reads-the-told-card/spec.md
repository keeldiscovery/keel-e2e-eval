# Spec 171 -- The judge reads the told card: the Insights tab's "On your problem" view graded against what the strangers told

The founder, 2026-11-25 ~12:55 ET: *"update the judge to evaluate for the problem, not only evaluate the insights -- in
the Insights, the new tab."* keel-cloud 281 reads every yes-sayer's story into the founder's three boxes (way,
limitations hit, pain) and serves `BriefFacts.problem.told` (the bands MOST / SOME / NONE over the anchored tellers,
theirs grouped, the verdict); keel-web 273 draws it as the Insights tab's *On your problem* view (the told card) and
the person's popup's Insights tab. Today §B reads the founder's page after the answers (the stage page, the cards, the
Insights cards of the whys) and the founder-reader grades the beats (R1-R5). Nothing reads the told card. Eval side;
built on 170; runs on a stack with keel-cloud 281 and keel-web 273; paid only on the founder's word.

## Rules
- **FR-1 The ground truth is the stub strangers' own stories.** The walk already holds every stub stranger's story
  (the experience after the yes) and the entry's board (the persona's way, limitations and pain). `harness/film_told.py`
  (new) writes `told_truth.json` beside `film.json`: for each stranger with a story, the judge-reader (one call a
  story, the film-reader's model) marks which of the entry's limitations the story describes happening, whether the
  way and the pain are the founder's, and whether the story is a real occasion or a guess -- independent of Keel's
  reading, from the story text alone.
- **FR-2 The told card captured and compared.** §B gains the told card: `GET` the brief facts (`told`) and the page
  as drawn (the switch, the card, the four numbers, the three blocks, the bands, the amber rows: screenshots as §B's
  screens), and the per-person popup's Insights tab for three strangers (the first with a hit, the first with a new
  row, the first guess, where they exist). Compared against `told_truth.json`: per person, the ticks, the way match
  and the pain match; per card, the counts and the bands recomputed from the truth; the verdict.
- **FR-3 Four criteria, scored as the R's.** `quality/FILM-RUBRIC.md` gains *The told card (the told-reader)*: **T1
  The ticks are right** -- across the three sampled people, every limitation ticked is in the truth and none missed
  (2 all right / 1 one off / 0 more); **T2 The counts add up** -- each of the founder's rows' counts and bands match
  the truth's within one person (2 / 1 one row off / 0); **T3 Theirs are real** -- every amber row is said by two or
  more stories in the truth and is not one of the founder's reworded (2 / 1 one row wrong / 0); **T4 Legible** -- the
  card reads in the founder's order and words, the bands say what they mean, nothing garbled, no trade word the
  entry does not use (2 / 1 / 0). One sentence of why each; `instead` as the R's. `told_pct` = the sum over 2 x 4 x
  100, recorded under `told` in the problem film's score file beside `founder_pct`, never folded into `film_pct`;
  the table (`quality/film_table.py`, `FILM-TABLE.md`) gains a `told` column after `founder_pct` and the weak rule
  covers T1-T4. A card absent on a problem project (older cloud) scores nothing and DRIFTs *(capture): no told card*.
- **FR-4 DRIFT on a mismatch.** A T1 or T2 at 0 writes a DRIFT finding naming the person or the row, with the truth
  and Keel's reading side by side (the product's reading is the fault, never patched around).
- **FR-5 Tests.** `tests/test_the_judge_reads_the_told_card_171.py`: the truth file from a fixture walk (payroll);
  T1-T4 on a fixture card that matches, one off, and wrong; `told_pct`; the table column; the DRIFT line; the absent
  card. `make unit` green on the base's known reds only. Nothing paid.
- **FR-6 The respondent-question rule.** The harness writes no respondent words.

## Acceptance
- On the next paid walk (the founder's word) the problem film's score file carries `told` with T1-T4 and `told_pct`;
  the table shows it; a wrong tick on one person is a DRIFT finding with both readings.
