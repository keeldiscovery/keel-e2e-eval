# Corpus revision 3 — recorded here, to be moved verbatim into keel-cloud's canon

**These files are the golden corpus at revision 3** (keel-e2e-eval spec 029, marks v9, the vector
redesign), written on 2026-10-07. They are **not fixtures in the usual sense and not a copy**: they
are the revision itself, recorded under this repository only because the corpus lives in
keel-cloud's canon (`canon/designs/measured-beliefs/corpus/`), which spec 029's branch may not
touch (the orchestrator's cross-track arrangement of 2026-10-07).

**At integration they are moved, byte for byte, into keel-cloud's
`canon/designs/measured-beliefs/corpus/`** — replacing the revision-2 files of the same names —
with `check_corpus.py` and `GoldenCorpusTest` reading revision 3 in the same commit series (spec 029
research R2), and the corpus `README.md` gaining its second *Revised* paragraph. After that move
this directory is deleted.

## How the eval reads them

`instructions/corpus.load(keel_cloud)` reads keel-cloud's corpus directory **once it holds a
revision-3 entry**, and this directory **only while it holds none** (the loader's docstring). The
moment keel-cloud carries one r3 file, every revision-2 file left beside it is a refusal to start,
by entry and by key — never a silent mix of the two.

## What each file records

The schema is marks-v9 §4 (`specs/029-marks-v9-vectors/contracts/marks-v9.md`), plus what spec 029's
plan asks of the r3 writer:

- **`founder_calibration[<dimension>].belief_sentence`** on all 25 (plan O-2, research R9): the
  sentence the engine writes from the registry template, the chosen phrase and the context slots —
  `"Left out: you weren't sure."` on an unsure one. This repository composes none; the brief and
  the register read it here.
- **`interpretations.problem`** (plan O-3, research R16): the golden `PROBLEM_INTERPRET` sentence the
  downstream screens are handed instead of a live answer.
- **`respondent_questions` holds the gate itself** (`problem.prevalence`, `gate_yes_no`, codes
  `[yes, no]`) — the registry asks it in Part 1 and counts it in the 8 — and
  **`problem.importance.own_item`**, the code of the problem's own item: the engine needs it for the
  share-to-band rule (A-7) and `option_validity` for *never first* (spec 029 tasks.md D3).

## How the counts were worked

By hand, person by person, under the compare rules the founder signed on 2026-10-07 (marks-v9
§2.5, spec 029 FR-018): ⅔ / ⅓ thresholds; ordinal band = the founder's rung ± 1, tolerance
dimensions counting the whole more-forgiving side inside; `set_overlap` per code; Importance as the
share who picked the problem's own item mapped onto the rank band; a gate-No answers nothing more; a
chipped or vague story is `GUESSED` and counted nowhere; a `rough` number from an anchored person is
counted nowhere for that dimension. Each file was then re-tallied from its own picks by a scratch
script (not committed: this repository keeps no copy of the compare arithmetic, `runs/DRIFT.md`
#33/#36/#41/#44/#45) before being written. **`check_corpus.py` confirms the counts when the files
move**; a disagreement there is the checker's to report and the file's to fix, never the other way
round.

Two reading conventions the hand-working used and the engine must agree with (both are in each
file's own `expected` rows, so `compare_correctness` will say so if they differ):

- **Drift on an ordinal** reads the dimension's own quantity: `above` is *more* of it (later on
  Compatibility, a higher bar on the threshold), `below` is less (milder on Severity, less effort on
  Adoption friction). Current-solution satisfaction's codes run best → worst, so *works better than
  you think* is `above` (marks-v9 §5).
- **Escapes**: *it was free or a gift* counts nothing (Ability to pay's `n` drops by one);
  *I wouldn't have reached for the phone* is outside with no direction.

| File | Revision | Notes |
|---|---|---|
| `03-lullaby.yaml` | 3 | First and complete. The registry's `lullaby` objects (spec 029 A-6); Hugo Laurent and Leo Martins answer No at the gate; Jonas Weber chips; the six commercial examples re-worked at n = 8 with no status changed (decision 14). Status totals 12 / 6 / 3 / 1 / 1 / 2. |
