# Tasks -- spec 164

Base: `origin/master` (161, 162, 163 specs; 161 merged at 9b01518). Built by a builder (Claude Opus 5.5) in the worktree
`/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-164`, branch `164-the-mirrors-of-258`. Nothing paid: no model,
no key, no pip install (the main checkout's `.venv`), no network but `git fetch` / `git push` of this branch; the local
stack allowed ONLY once the integrator's run has released it. Push after every commit.

- [x] T1 FR-1 the ten mirrors, their unit mirrors.
- [x] T2 FR-2 the card's walked record by passage kind.
- [x] T3 FR-3 `make unit`; the local run; this file.

## How each mirror is met

| # | keel-web 258's item | Where | What the harness holds |
|---|---|---|---|
| 1 | the `pending_258` film-first branch retired | `evals/three_views_strangers.py`: `pending_258`, `pending_check`, `SCREEN_CHECKS_258` gone; `film_first_checks` holds 258's order alone; the film's *Begin* compared with `gate_clip`; orb / face / card walk the problem link on screen always; `tests/test_orb_159.py`, `tests/test_both_speakers_160.py` moved to 258's order | the opening and the screener before the film, no film-first branch left to take |
| 2 | `.rp-tookby` -> `insights-capped` | `harness/vectors_screens.Answers.insights`: `capped` (`[data-testid=insights-capped]`), `count_line` (`insights-count-line`), both among the view's own lines | the drawn box's `capped` / `count_line` |
| 3 | `report_marks` `capped` in place of `took_by` | `evals/report_marks.expected_box` (`count_line`, `capped` via `capped_line`, `interviewer_fake.insights_capped`), `insight_faults`' parts, `consumer_report_words`; `tests/test_insights_also_group_120.py`, `tests/test_report_marks.py` | *{k} of the {n} were past the two-question cap* (*1 of the n was ...*) where `capped > 0` and the count line does not say it; no composed footer, ever |
| 4 | Frequency's chart: `data-chart="frequency"`, five bands, `data-for`, the caption | `evals/backtest.CARD_JS` (`frequency_caption`, each bar's `for` and `count`); `harness/three_surfaces.frequency_chart_faults`; `three_views_strangers.founder_page_on_screen` (the stage page's Frequency card) | the five bands with their served counts, Every time / Most times `data-for`, *{k} of {n} said most times or every time · you said {band}* |
| 5 | the breakdown's bands cell, no Current solution row | `vectors_screens.Answers.brief` (`breakdown`: `section.rp-bd tr[data-dim]`, `.rp-bd__facts`); `report_marks.breakdown_frequency` / `breakdown_faults` (in `binding_faults` too); `founder_page_on_screen` | *Every time 4 · Most times 5 · ...* (an older server's `middle` words), no `problem.current_solution_satisfaction` row |
| 6 | the card's Frequency bubbles as digits 1..5 | `copilot_walk` reads each strip's `.cpl-bubble__let`; `three_surfaces.badge_faults` / `FREQUENCY_DIGITS`; `card_machine_checks`; the note at `story_screens.StoryLinkText._card` | Frequency's five badged 1-5 on the card, every other question lettered |
| 7 | the card walk: two follow-ups a call, Frequency's `also` on Never, the gate's `followUp` on a No, Importance alone after | `three_surfaces.card_follow_ups` / `card_no_path` / `CARD_MAX_FOLLOW_UPS` (the machine's mirror); `copilot_walk` keeps the picks filed (`filed`); `card_machine_checks`; `evals/calls_leg.py`'s words | the follow-ups the card opens are its machine's for the picks filed, on both calls; after the gate's No: the gate's follow-up, then Importance alone |
| 8 | `interviewer_fake.owed` on `recency` | `owed(..., recency=)`, `first_stem` / `first_rung` pass it; `PREVALENCE_RUNG`, `AFTER_A_NO` | `recency=False`: Prevalence first (unless asked or not served), Importance's pick alone read |
| 9 | the ways panel's DOM | `three_views_strangers.WAYS_PANEL_JS`, `founder_page_on_screen`; `three_surfaces.ways_panel_faults` (`WAYS_HEADING`, `ways_read_from`, `WAYS_YOUR_WAY`, `WAYS_READING`, `ON_THEIR_OWN_LABEL`) | `[data-testid=rp-ways]` in `li.rp-ways-row` right after Prevalence's row in the problem's panel; the heading, the read line, a row a group (*On their own*, *your way* on the founder's); GROUPING *Reading …*; RAW the line alone |
| 10 | the nesting on `defined`, `calibrating`, `calibrated` | `story_screens.BEFORE_THE_LOCK` / `is_defined` / `parent_of`; `three_views.fr1_d` | the list nests the problem project under the solution whose lineage names it, and the wire's row says it nests (DRIFT #114 dropped from the check) |
| FR-2 | the card's walked record by passage kind | `three_surfaces.card_passages` (`withCondition`, `withCheck`), `passage_of`, `strip_step`, `strips_record`; `copilot_walk` (`passage_kind` / `passage_item` / `passage_dimension` / `options` / `badges`, a follow-up's `read`); the yes call answered on the orb's rows (`answered_rows`) | the intro, the reveal and the pilot ask are never a step; the screener, the gate (*Did this happen to you?*, Yes / No), each item by its dimension, each follow-up folded onto its question |

## Runs
All local (`make e2e-157 PROFILE=eval`, the main checkout's `.venv`), FakeSpeech / fake avatar / fake transcriber /
scripted readers only: no vendor host contacted (the log scan), every Keel AI clip FakeSpeech at 0 µUSD. Started only
after the integrator's run of record 3 logged `EXIT` (16:5x ET); keel-cloud served from the temporary worktree
`wt/keel-cloud-eval-164` (`8fc10e71`), keel-web from `wt/keel-web-eval-164`; `stack.toml` pointed at them in this
worktree's copy only (restored, never committed); both worktrees removed after; `make down` after each run (the last
run's Gradle daemon and JVM, started by this run, gone).

| run | stack | result |
|---|---|---|
| 1 (16:53 ET) | cloud `8fc10e71`, web `1fdea165`, eval `9f4518c` | stopped at the founder's sign-in (*.auth-title* never drawn): vite's first-load dependency re-optimisation in the new worktree's empty cache reloaded the page -- environment, not a red; no bundle |
| 2 (16:56 ET) | cloud `8fc10e71`, web `1fdea165` | stopped by the builder (its own make; `make down`) on the coordinator's word: keel-web for the run is `9ef65690` |
| 3 `runs/157/8fc10e71-9ef65690/20261124T220247Z` | cloud `8fc10e71` (contract 87), web `9ef65690`, eval `9f4518c`, 17:02-17:40 ET | **6 of 13 green** (FR-1a-d, problem avatar, solution avatar). The No-sayer's why, the No path, Frequency on bands, the ways, Insights, the brief, the founder's page on screen and the card's walked gate all held on the problem study. Red: problem orb and solution orb on the phone film (the walk did not answer the screener 258 puts before the film -- harness), money orb and avatar after *Begin* (the check, which has no clip, read as the gate -- harness), money copilot (a ladder's second step not filed; the orb's sheet rows' badge on *$...* rows; number items not in the walked record; the card's anchor -- harness), problem copilot (**DRIFT #116**), solution copilot (**DRIFT #117**, **#118**). All harness reds fixed in `eb5222d` |
| **4 (the run reported)** `runs/157/8fc10e71-eb4955fc/20261124T224322Z` | cloud `8fc10e71` (contract 87), web `eb4955fc` (= `9ef65690` + a test-only commit, the coordinator's word), eval `eb5222d`, 17:43-18:20 ET | **11 of 13 green**: FR-1a, FR-1b, FR-1c, FR-1d (the list's nesting held: DRIFT #114 resolved), problem orb, problem avatar, solution orb, solution avatar, money orb, money avatar, money copilot. Red, both the product's: **problem copilot** by one check, the walked one script at step 4 (`problem.importance`): the orb and the face ask Importance's why on a row that is not the founder's own, the card opens none (**DRIFT #116**; every other check of the leg green -- the card read by passage, its gate *Did this happen to you?* with Yes / No, the No path by passage, its machine's follow-ups on both calls, Frequency's digits); **solution copilot** by two: the card's No goes on with Prevalence's why on an anchor that ends the interview on the orb and the face (**DRIFT #117**), and the walked one script at `solution.compatibility`: the card opens *You said yes, with some steps ...* on *Yes, most of the time* (**DRIFT #118**) |


## Commits
| Commit | FR | What |
|---|---|---|
| `d976972` | FR-1, FR-2 | T1+T2: the ten mirrors (pending_258 retired, capped, the Frequency chart, the breakdown, the digits, the card's machine, owed on recency, the ways panel, the nesting), the founder's page on screen, the card's walked record by passage kind; tests |
| `9f4518c` | FR-1, FR-2 | the voice walk's yes-sayer by its `MadeLink` invitation id; the decision-maker's check strip read as the card's check passage; the mirror table |
| `eb5222d` | FR-2, FR-3 | run 3's reading (harness): the phone film answers the screener first; the money link after *Begin* is the check with no clip; a row's badge off by its place; number items in the walked record; a ladder's second step filed; the card's anchor before its stem; a walked why compared by where it is asked |
| (this commit) | FR-3 | DRIFT #116-#118 written, #114 / #115 resolved; this file's runs, unit counts, commits and judgement calls |

## make unit
- Before (`b4843ca`, the base, 16:31-16:38 ET, siblings keel-cloud-docs `8fc10e71` / keel-web `c7f5b97a`): **92 failed,
  6050 passed, 137 skipped**.
- After T1+T2 (`d976972`, siblings cloud `6a50f661` -- the integrator's checkout back on it -- / web `c7f5b97a`): 90
  failed, 6068 passed, 137 skipped; the one red not in the base's list (`test_three_views_157::
  test_the_idea_beats_answer_every_limit_of_the_story`) is the sibling keel-cloud's 271 fake readings (*idea beats are not
  1 and 2*), not this branch (green on `8fc10e71`).
- **After (the head, 18:22-18:29 ET, siblings keel-cloud-docs `b48e1f49` / keel-web `7c98d472` as the main checkouts
  stood): 97 failed, 6065 passed, 137 skipped -- no new red**: the base `b4843ca` run beside it on the same siblings, at
  the same time, has **100 failed, 6042 passed, 137 skipped**; the after's reds are a subset of the base's, three fixed
  (`test_orb_159::test_keel_web_plays_the_orb`, `test_both_speakers_160::test_the_web_side_walks_the_same_states` --
  258's order -- and `test_founder_walk_076::test_the_dry_runs_hello_on_the_gates_id_is_not_the_story`), 20 tests added
  (`tests/test_mirrors_of_258_164.py`'s 19, 120's capped line). Every remaining red is the base's own (the sibling checkouts'
  drift of earlier specs' mirrors).

## DRIFT written
- **#116** (keel-cloud, `CallScriptComposer`): Importance's `followUp.against` empty on the card's script -- the card never
  asks Importance's why where the orb and the face do. Met in runs 3 and 4.
- **#117** (keel-cloud, `CallScriptComposer`): on a solution study the card's gate carries Prevalence's follow-up, so the
  card's No goes on where the anchor ends the interview on the orb and the face. Met in runs 3 and 4.
- **#118** (keel-cloud, `CallScriptComposer`): Compatibility's second stem opened on *Yes, most of the time* (the card's
  `also.on` not held to `saysItsSteps`). Met in runs 3 and 4.
- **#114** status: resolved (keel-web `d4fb9318`, in `9ef65690`). **#115** status: resolved (keel-cloud-docs `8fc10e71`).

## Open
- The two copilot legs stay red until keel-cloud answers DRIFT #116-#118 (the card's script); nothing in the harness
  patches around them.
- keel-web `9ef65690` / `eb4955fc` vendor contract 89 / 90 (261, 259) while the stack's keel-cloud serves 87: the run
  read 87 and the four questions held; the next integrator run on merged masters names its own pair.
- The money's walked comparison now runs (161 compared it on the wire alone): green on run 4.


## Judgement calls
1. **keel-web for the local run is master `9ef65690`, not `1fdea165`** (the coordinator's word, 2026-11-24 ~17:00 ET, after
   the brief): `1fdea165` (the on-the-spot follow-up waits for the route) and `9ef65690` (the real cause of the No-sayer's
   missing why in the run of record: the cloud serves no `counts` on a counted gate, only `false` on an anchor, and
   `noGoesOn` required `true`, so every real link's No still ended the interview -- it now reads absent as counted).
   `9ef65690` also carries keel-web 261 and 259 (contract 89 vendored) -- the stack's keel-cloud stays `8fc10e71`
   (contract 87). A run already started on `1fdea165` (run 2) was stopped by the builder (its own make, then `make down`)
   and the temporary keel-web worktree detached at `9ef65690`.
2. **The stack served temporary worktrees**: keel-cloud-docs `8fc10e71` at `wt/keel-cloud-eval-164` and keel-web at
   `wt/keel-web-eval-164` (the main keel-web checkout had moved to `c7f5b97a` under the integrator's run), with
   `node_modules` cloned (`cp -c`, the lockfile unchanged between the shas); `stack.toml` pointed at them in the
   worktree's copy only, never committed. Run 1 lost the founder's sign-in to vite's first-load dependency
   re-optimisation (*new dependencies optimized ... reloading*, the empty cache of the new worktree) -- an environment
   miss, not a red; the cache warm, the run was made again.
3. **All of `pending_258` is retired**, not only the film-first branch keel-web 258's item 1 names: 258 is merged and
   every branch it guarded was dead (the wire-only roster walk, the pending checks, the order note). `roster_on_the_wire`
   stays as a function (its record shape is documented by it), uncalled.
4. **The card's walked record keeps the screener** where the card draws it (the condition passage): the wire's card
   record keeps it too, so the walked step 1 is the screener and the gate step 2 (FR-2's *step 1 is the gate* was read
   off the failing verdict, where the screener had been dropped as not on every surface).
5. **The yes call is answered on the orb's rows** (`answered_rows`: Frequency by its letter's row, Importance by its first
   row's words), so the card owes the whys the orb owed and the walked follow-ups can be compared at all; the No call
   picks as before.
6. **A two-step ladder's bands on the card's walked record are its passage's** (`_card_labels`): the card draws only the
   side the first answer opens, so the drawn bubbles cannot hold the whole ladder; compared as a set, as 161 does.
7. **The decision-maker's check** (the script serves none; the route words it from the story's people) is read as the
   card's `check` passage by the card's own press: on a script with no gate, the question strip that carries *Story
   again*.
8. **The founder's page counts every yes-sayer the study's links were walked with** (`other_yes_sayers`): on keel-web 258
   the problem link's walk by voice runs before the roster (its Frequency by letter, *Most times*, and its story), so the
   run of record's `n/share` [5, 0.4] against the roster's [4, 0.25] and the ways' `read` 5 were the harness's count, not
   the product's. Its invitation id is the `MadeLink` Send more posted.
9. **The founder's page is read on screen too** (`founder_page_on_screen`): mirrors 2, 4, 5 and 9 are DOM reads, so they
   are held on the founder's real page right after the wire reads -- the Overview's ways panel, the stage page's
   Frequency card, the Insights boxes, the binding's breakdown.
10. **Unit reds that are 258's moves were moved, the rest left**: the film-first mirrors of 159 / 160 and 076's
    formatter-wrapped `firstItemId` line; every other red is the base's own (the sibling checkouts' drift of earlier
    specs).
11. **Run 4 is on keel-web `eb4955fc`** (the coordinator's second word: `9ef65690` plus a test-only commit, two e2e walks
    answering Importance after the gate's No; *use it if the run has not started*): run 3 had run on `9ef65690`; run 4,
    started after, ran on `eb4955fc` -- the sha each report names.
12. **A walked why is compared by where it is asked, not by its words** (`three_surfaces.WALKED_WHY`, the walked records
    only): the orb and the face say the route's why, which says the person's pick back (*You picked ... over ...*, *You
    said under $10 a month ...*), the card reads the script's hint; the words are held on the served records (the cloud's
    one script, compared word for word as 161 did). A why asked on one surface and not another still parts the records.
13. **A sheet row's badge is taken off by its place** (`letterOf(i)` on a story link): 161's regex kept the letter on a row
    starting with *$* (*B$10 to under $20*); a number item (no rows) is a step of the walked record too, so the card's
    *Existing sacrifice* is matched on the orb and the face.
14. **The decision-maker's link after *Begin*** is the problem check, which keel-web 258 asks with no clip of its own
    (`stepsOf`: `clip: undefined`): the check holds that nothing plays and the window opens; a link with a gate keeps the
    gate's clip first.
