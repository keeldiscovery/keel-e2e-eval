# Tasks 091 -- A drafted list is held to the draft's rule, not the save's (with FR-3 on IM2's credits line and FR-3a on the cloud's classes)

Branch `091-the-draft-list-minimum` (worktree `wt/eval-091`), off master `fb7a7f7` (090 and 093 in; `MARKS_VERSION` 22),
origin/master `dfb5df0` merged in mid-build for FR-3a. Built by Claude Opus 5.5 on 2026-10-30 (commits carry the
hand-off's `Claude Fable 5.1` trailer). Read only: keel-cloud-docs **`a41b6226`** (`dimension-registry.json`:
Importance `saves` `{min_items 2, max_items 5}`; `founder-lists.md`'s `rival_list` bullet; `ScreenResultApplier.draft`'s
097 F9 bounds; `model-routing.json` v13; `JobClass`), keel-web **`e4f204e`** (`beforeInterviewerSub`,
`recordAtLockSwitch`, specs 130 / 132). The spec of record (FR-1 to FR-4 and FR-3a, not edited). The two founder-lists
bundles (`runs/20261030T111940Z-instructions`, `runs/20261029T193750Z-instructions`) copied from the main checkout into
the worktree's ignored `runs/` and re-scored there. **No paid call**: re-scores `--no-judge`, the screen `DRY=1`. Nothing
merged into master or deployed; the branch pushed after every commit, never force-pushed.

| Commit | What |
|---|---|
| `e8041e1` | FR-1: Importance's draft count; `MARKS_VERSION` 22 -> 23 |
| `5a72715` | FR-3: IM2 reads L1's credits sentence; `INTERVIEWER_MARKS_VERSION` 14 -> 15 |
| `973bc91` | merge of origin/master (`dfb5df0` FR-3a's spec text, `c839572` 092 FR-4a's) -- merged, not rebased (judgement call 6) |
| `2b23e58` | FR-3a: `CLASSES` gains `example_match`; the live-table test |
| the docs commit | this file, `AGENTS.md`'s spec-091 paragraph |

## Unit (the gate)

`make unit` on the live checkouts (keel-cloud-docs `a41b6226`, keel-web `e4f204e`):

| | passed | failed | skipped |
|---|---|---|---|
| master `fb7a7f7` | 3,855 | 0 | 53 |
| branch at FR-1 (`e8041e1`) | 3,877 | 0 | 53 |
| branch at FR-3 (`5a72715`) | 3,886 | 0 | 53 |
| **branch, final tree (the docs commit; FR-3a `2b23e58` the last code)** | **3,888** | **0** | **53** |

`make instruction-screen K=03-lullaby/CALIBRATION DRY=1 WHY=instruction:founder-lists.md`, master (`git archive fb7a7f7`,
run in the scratchpad beside sibling links, then removed) and branch: the same **9 cases** (9 calibration, N=3; the one
listed case `03-lullaby/CALIBRATION_PROBLEM/run1 (CALIBRATION_QUESTIONS)`), the same `spoken 15 of 15`, `facts 14 of
14`, `overview 7 of 7`, the same denominators (calibration 11, validity 11, no_leak sweep A 3); the printed output is
byte-identical but for the prompt's random KEEL-DATA fence. The verdict's `marks_version` reads 22 -> 23. Nothing called,
nothing spent.

## The re-score (the acceptance)

`python -m instructions.rescore runs/<id> --no-judge`; `option_validity` faults by rule on the calibration screens:

| Bundle | Recorded (v21) | 093's v22 (its tasks.md) | **Re-scored at v23 (this branch)** |
|---|---|---|---|
| `20261030T111940Z` (after keel-cloud 161 / 163) | 25/33 (75.8 %): L1 x3 Importance, L5 x3 Compatibility, K3 x2 Adoption | 30/33: L1 x3 Importance | **33/33 (100 %): none** |
| `20261029T193750Z` (before 161) | 26/33 (78.8 %): L1 x3 Importance, L5 x3, K2 x2 + K3 x2 Compatibility, K2 x1 Adoption | 24/33 | **27/33 (81.8 %)**: L1 x3 Current solution (*your way of ...*, written before 161), K2 x2 + K3 x2 Compatibility |

- **`problem.importance` is valid on all six PROBLEM runs** (each the problem itself alone, `answers` `{}`: *Working out
  what the cry means*, *Guessing why the baby is crying*, *Guessing what the baby needs*, *Figuring out what the cry
  means*) -- the spec's acceptance (*valid on all three runs* of the 2026-10-29 bundle) met, and on the 2026-10-30 one.
- What remains on the 2026-10-29 bundle is 093's (Current solution's *your way of*, the pre-161 writer) and 161 FR-3's
  (Compatibility's K2 / K3, the instruction's subject) -- neither this spec's.

## FR-1 -- the draft's minimum -- `e8041e1`

- [x] T001 `instructions/score.py`: `_draft_count(dimension, answers)` -- on `rival_list` with no founder Answer for it
  (`answers` `{}` or the key absent or blank) exactly **1** item; with an Answer exactly **1 + N** (N =
  `named_difficulties(answer)`, capped at `saves.max_items`); every other list the registry's bounds less a fixed first
  item, as before. `list_faults` / `calibration_checks` take `answers`; `score_calibration` hands the case's sent context's
  `answers` through (else the seed-time job's `{}` from `context.build_calibration`).
- [x] T002 `named_difficulties(answer)`: a list Answer one difficulty an element; a text one split on lines, bullets,
  `;` and `,`, a serial list's last *and* / *or* split (*A, B and C* is three), a lone *and* kept as one, an Answer
  naming none (*Nothing else*, *None*) zero.
- [x] T003 **`MARKS_VERSION` 22 -> 23** (`instructions/marks.py`): the v23 paragraph; calls **127** (the draft's count)
  and **128** (`OLDEST` stays 20: a v20 / v21 / v22 bundle re-scores at v23); `instructions/marks.toml`'s v23 header. No
  number in `[marks]` moved.
- [x] T004 Pins and fixtures, and `tests/test_draft_list_minimum_091.py`.

| File | Old | New | Why |
|---|---|---|---|
| `instructions/score.py` `list_faults` L1 | `low = min_items - fixed`, `high = max_items - fixed` on every list | `_draft_count`: Importance 1 / 1 + N; the rest unchanged | FR-1 |
| L1's words | *takes 2 to 5 items, and 1 were written* | *takes exactly 1 item (the problem itself alone, with no founder Answer), and 2 were written*; *exactly 3 items (the problem itself and the 2 difficulties the founder's Answer names)* | the rule named |
| `tests/v9_fixtures.GOOD_LISTS["problem.importance"]` | five items | the own item alone | a seed-time draft meeting every rule |
| `tests/test_instruction_score.py` | *importance four* (pop -> `exactly 5`); *a long rival* (item 3); *a not-sure rival* (item 5); the corpus-as-a-draft test drafts Lullaby's five | *importance with a rival and no Answer* (`exactly 1 item ...`), *importance empty*; *a long own item* (item 1); *a not-sure own item*; the corpus-as-a-draft test drafts the own item | FR-1 |
| `tests/test_instruction_leak.py` `_with_label` | `index=1` (a rival) | `index=0` (the own item) | the seed-time draft has one item |
| every `MARKS_VERSION == 22` pin (`test_backtest`, `test_follow_ups_075`, `test_founder_walk_076`, `test_guide_marks`, `test_instruction_marks` -- the version, calls 110-128, the marks file's v23 header --, `test_instruction_rescore` -- *cannot be re-scored at v23*, a v20 bundle re-scored at v23 --, `test_phrase_is_the_peoples_093`, `test_quality_081`, `test_recorded_path_074`, `test_sample_export`, `test_study_scopes`) | 22 | 23 | T003 |

Tests (`test_draft_list_minimum_091.py`): the four recorded Lullaby own items valid with no Answer; the recorded PROBLEM
run 4 of 4; a rival with no Answer and an empty draft faulted; an Answer naming two is three items; **fewer than the
Answer names faulted** (*exactly 3 ... and 2 were written*); more faulted (*Add none*); *Nothing else* leaves the own
item; the cap at `max_items`; the Answer's parts; Compatibility still *2 to 4*; **a saved Importance of one item still
refused by `corpus._check_list` (`saves.min_items`)**; the version and its note.

## FR-2 -- decided before

No entry in `quality/decisions.toml` (a harness mark, not a founder's decision). No commit.

## FR-3 -- IM2 and the lock screen's credits line -- `5a72715`

- [x] T005 `evals/interviewer_marks.py`: `LOCK_CREDITS_SENTENCE` (keel-web `beforeInterviewerSub`: *Keel records {face}
  once for this project, which uses Keel's credits.* / *... which uses 400 credits.*), `CURRENCY`, `served_prices(r)`
  (the wire's `changePrice`), `price_words_on(name, text, served)`: on **L1** the one sentence is the screen's own words;
  a second such sentence, a number in it other than the served price (else `fake.CHANGE_PRICE`, 400), any currency
  anywhere on L1, or a price word outside the sentence is named. S2's one action stays its own; S1 and S3 read as before.
  `no_price_shown` (IM2) reads it and names the sentence it read (`L1 credits sentence`).
- [x] T006 **`INTERVIEWER_MARKS_VERSION` 14 -> 15** with its v15 note.
- [x] T007 `evals/interviewer_leg.py`: the journey's *L1 revisited ... and no price on it* reads `marks.price_words_on("L1",
  ...)` (two lines; it read the bare `PRICE_WORD`, which 090's builder showed would fault on the stack).

| File | Old | New | Why |
|---|---|---|---|
| `tests/test_interviewer_marks.py` `good()` L1 | *Who asks the questions. Keel records your interviewer once for this project. Lock and record the interviewer* | keel-web 132's screen: *Who should ask them your questions? Daphne is picked for you. ... Keel records Daphne once for this project, which uses 400 credits. ... Lock and record Daphne* | the screen as served |
| `SEEDED` IM2 | four L1/S1/S2/S3 faults | + *uses 900 credits*, the sentence twice, *About $2.* | each FR-3 clause made to fail |
| `test_interviewer_marks` (card), `test_controls_089`, `test_recorded_path_074`, `test_founder_walk_076` | `INTERVIEWER_MARKS_VERSION == 14` | 15 | T006 |

## FR-3a -- the model table's classes are the cloud's -- `2b23e58`

- [x] T008 `instructions/models.py`: `DORMANT_CLASSES` gains **`example_match`** last, so `CLASSES` ends on it -- the
  cloud's order (`JobClass`: ... `ASKED`, `EXAMPLE_MATCH`) -- tolerated, never measured or reported (it runs on no
  project); the validator's message follows (*... the classes are exactly context, frame, calibration, respondent,
  reading, asked, assumptions, reframe, questions, brief, example_match*).
- [x] T009 `tests/test_instruction_models.py`: `test_classes_carry_every_class_the_live_routing_table_names` reads the live
  keel-cloud `model-routing.json` (v13) -- every class it names in `CLASSES`, and the table parses -- so the next class
  the cloud adds fails `make unit`, not s012 (it ran, not skipped, on `a41b6226`); `test_the_validators_message_names_example_match`.

## FR-4 -- nothing else moves

The other L rules, the registry, the corpus (revision 19), the instructions, the screens' other marks, `SCREEN_TO_CLASS`.

## Judgement calls

1. **N is read off the Answer's parts, grammar only.** The cloud bounds a redraft 1 to `max_items` (097 F9) and counts no
   N; the spec asks 1 + N exactly, so the harness reads N off the Answer: lines, bullets, `;`, `,`, a serial list's last
   *and* / *or*. A lone *and* (*settling the baby and finding the bottle*) is one difficulty; an Answer naming two joined
   by a bare *and* reads as one and a draft of three would be faulted -- named, not guarded. No trade words. Every
   screen this eval runs sends `answers` `{}`, so today only the one-item reading is exercised on a bundle.
2. **The fault's words name the draft's rule** (*the problem itself alone, with no founder Answer* / *the problem itself
   and the N difficulties the founder's Answer names*), keeping the *L1: <key> takes ... , and n were written* shape every
   reader parses.
3. **`MARKS_VERSION` moved (22 -> 23)**: `option_validity`'s reading moved both ways (FR-4's own clause). `OLDEST` stays
   20: the rule reads the draft and the `answers` a bundle holds.
4. **`validate.py` was not touched**: it restates no count (the founder-lists rules are keel-cloud's validator's, read
   through it); `score.list_faults` is the one harness L1.
5. **IM2's L1 admits the sub's sentence alone, not 132 FR-2's switch** (*Record {face} at lock · 400 credits*): the spec
   names the one credits sentence; the switch is drawn only where the server serves `recordOnSend: true`
   (`KEEL_V2_INTERVIEWER_LOCK_RECORD_OPTIONAL`, staging's overlay alone), which the eval stack does not set. A stack that
   set it would fault IM2 on the switch -- named, not guarded. The face is read as one to three words (*Daphne*,
   *them*: the faceless fallback).
6. **origin/master was merged, not rebased.** The coordinator asked for a rebase; the branch was already pushed and the
   brief forbids a force-push, so `973bc91` merges `dfb5df0` (nothing of either side lost).
7. **`interviewer_leg.py` was touched** (two lines) though the journeys are 092's: the spec's FR-3 names the *L1
   revisited ... no price* reading; it now calls the same helper as IM2.
8. **`SCREEN_TO_CLASS` gained no `EXAMPLE_MATCH`**: FR-3a names `CLASSES`; s012 reads the map with `.get`.

## What did not hold

- **Nothing was walked on a stack**: IM2 v15 and the leg's L1 step are held by unit doubles built from keel-web's
  source words; `make eval K=s005` / `s006` (the lock walk) and s012 (the table) are the coordinator's after the merge.
- **No 1 + N case exists on a recorded bundle**: the founder-lists screen sends `answers` `{}`; the Answer reading is held
  by tests alone.
