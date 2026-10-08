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
- **A decision-maker answers on their own link.** On a B2B entry (`persona.decision_maker:
  {role}`), the decision-maker role's people carry **`link: COMMERCIAL_B2B`**: no gate answer
  (`recency: null`), their last-purchase story, a golden anchoring, and picks on `commercial.*` only.
  The commercial vector is counted over them; the primary respondents answer Parts 1 and 2. marks-v9
  §4 has no field for this, and FR-010 needs one (spec 029 tasks.md D15).

## What the registry fixes that only Lullaby fits (findings for keel-cloud 058)

The registry v1 is Lullaby's shape in three places, and the other six entries read them as follows
-- recorded here so 058 can make each a per-project value rather than discover it:

- **The gate's window** is fixed at *7 nights* (`problem.prevalence.founder.normalized.window`). Each
  of the other six reads the gate over its own circumstance's natural window, stated in its header
  (a mismatched delivery in the last month; a report in the last quarter; a puncture in the last
  year; an invoice paid in the last three months; the last shift; a yard run in the last two weeks).
- **Frequency's unit** is *nights out of 7*; the six count days, rides, invoices, shifts or working
  days out of 7 on the same 0-7 axis.
- **Duration's units** are minutes and hours; Paidly waits in *days*. And the threshold's bands
  (`0-5`, `5-10`, `10-20`, `20+`) are read in the founder's own unit (hours on ComplianceLog, days
  on Paidly).

## How the counts were worked

The picks by hand, person by person -- Lullaby's from the registry's own counts, the other six
chosen to exercise the statuses each entry's verdicts turn on -- under the compare rules the
founder signed on 2026-10-07 (marks-v9
§2.5, spec 029 FR-018): ⅔ / ⅓ thresholds; ordinal band = the founder's rung ± 1, tolerance
dimensions counting the whole more-forgiving side inside; `set_overlap` per code; Importance as the
share who picked the problem's own item mapped onto the rank band; a gate-No answers nothing more; a
chipped or vague story is `GUESSED` and counted nowhere; a `rough` number from an anchored person is
counted nowhere for that dimension. Every standing was then tallied from those picks by a scratch
script (Lullaby's and the three single-role entries by two independently written ones, which agree) (not committed: this repository keeps no copy of the compare arithmetic, `runs/DRIFT.md`
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

| File | People | Read (N=1) | Verdicts (PROBLEM · SOLUTION · COMMERCIAL) | Notes |
|---|---|---|---|---|
| `01-countly.yaml` | 12 | 10 | holding up · people disagree · holding up | **Leaves out an asked dimension** (`problem.severity`, FR-009): Part 1 is 7. Urgency carries a belief: `NOT_ASKED_YET`. |
| `02-compliancelog.yaml` | 12 | 9 | people disagree · people disagree · people disagree | One chip. Hours. |
| `03-lullaby.yaml` | 12 | 9 | not holding up · not holding up · not holding up | First and complete: the registry's `lullaby` objects (A-6); Hugo and Leo answer No; Jonas chips; the six commercial examples re-worked at n = 8, no status changed (decision 14). Totals 12 / 6 / 3 / 1 / 1 / 2. `mechanism_terms` is `[listen, phone, card, most likely, suggestion]` -- `cot` dropped 2026-10-08 (call 39): the cot is the problem's furniture, not the idea's. |
| `04-linerly.yaml` | 12 | 9 | not holding up · not holding up · people disagree | One chip. Urgency: `NOT_ASKED_YET`. |
| `05-paidly.yaml` | 20 | 10 | people disagree · bar set · not holding up | **The B2B entry** (A-5, FR-010): eight agency project managers on the `COMMERCIAL_B2B` link; the B2B ladder. |
| `06-repeatline.yaml` | 19 | 10 | holding up · not holding up · not holding up | B2B: seven practice managers on their own link. |
| `07-mulchrun.yaml` | 19 | 8 | not holding up · people disagree · people disagree | B2B: seven crew owners. Prevalence below the founder's bin: the PROBLEM verdict turns on the gate. USD. |

106 people; **65 readable** at N=1 (less 13 gate-No, 6 chips, 22 decision-makers); 138 model cases
at N=1 and seven `COMPARE` rows. Every one of the eight `Status` words appears somewhere but
`TOO_FEW_TO_CALL`.
