# Tasks 096 -- Three stops of the quality walk that were the harness's: the idea-card edit in the money study, the cost step's rate read before it is typed, the decision-maker's line named

Branch `096-three-stops-of-the-walk` (worktree `wt/keel-e2e-eval-096`), off master `dafb23d` (097, 098 and 099 are
spec files only). Built by Claude Opus 5.5 on 2026-10-30 (commits carry the hand-off's `Claude Fable 5.1` trailer).
Read only: keel-web `IdeaCheck.tsx:167` (the idea's Save goes to `/define/solution/q/{n}` where the solution is in scope,
else `/define/persona`), keel-cloud `d3a37953` (165's wording for the decider's line), and the three bundles named in the
spec, from the main checkout's `runs/`. **No browser, no stack, no paid call**: `make quality-walk ENTRIES=10-palus,08-fresco
SCOPES=SOLUTION,COMMERCIAL ...` is the coordinator's, after the merge. Nothing merged into master; the branch pushed
after every commit, never force-pushed.

All three FRs were built together (cloud 165 had already merged at `d3a37953`), FR-1 and FR-2 first as the spec allows.

| Commit | What |
|---|---|
| `cea8c52` | FR-1: the idea card's edit lands on the solution's first question or on who decides |
| `acb4ca9` | FR-2: the cost step's rate box held to the view before the screen's own save; the entry's rate a second step |
| `2820f60` | FR-3: *the idea card's decision-maker's how line* read as `howDecider`, each line edited alone |
| the docs commit | this file, `AGENTS.md`'s spec-096 paragraph |

## Unit (the gate)

`make unit` on the live checkouts (keel-cloud-docs `d3a37953`, keel-web `f661542`):

| | passed | failed | skipped |
|---|---|---|---|
| 094's tasks.md record (master `6a2d4dd`-era) | 3,970 | 0 | 53 |
| **master `dafb23d`, re-measured** | **3,970** | **0** | **53** |
| branch at FR-1 (`cea8c52`) | 3,984 | 0 | 53 |
| branch at FR-2 (`acb4ca9`) | 3,996 | 0 | 53 |
| **branch at FR-3 (`2820f60`, the last code; the docs commit adds none)** | **4,003** | **0** | **53** |

The +33 are this spec's: `tests/test_three_stops_096.py` (32: FR-1 14, FR-2 12, FR-3 6) and one in
`tests/test_after_131.py` (`test_the_deciders_line_is_its_own_refusal_096`). A first master run overlapped the edits
being written into the same tree and read 4 failed (`inspect.getsource` against moved lines -- 094's judgement call 12
again); it was discarded and master re-measured clean with the edits stashed.

## FR-1 -- the edit lands on the scope's next screen -- `cea8c52`

Stop: `runs/20261030T144756Z-backtest-10-palus` (COMMERCIAL), seq 70 -- `waiting for navigation to
"re.compile('/define/solution/q/\\d+$')"`, 30 s; the money-only study's Save went on to `/define/persona` (seq 39's own
idea step already says *Save goes on to who decides*, `scope_journey.py:176`).

- [x] T001 `harness/vectors_screens.py:282-291`: `IDEA_SAVE_LANDINGS` (`solution`: `/define/solution/q/\d+$`, `persona`:
  `/define/persona$`), `IDEA_SAVE_LANDS` (the two as one alternation for the wait) and `idea_save_landing(url)`.
- [x] T002 `Corridor.edit_idea_lines` (`:2073`): waits for `IDEA_SAVE_LANDS` (`:2100`, was `/define/solution/q/\d+$` at
  master `:2082`) and returns `landed` (`:2102`); the step's name says *Save goes on to the solution's first question, or
  to who decides in the money study*; the docstring follows. `relock` untouched.
- [x] T003 Tests: both landings accepted by the one pattern (searched, as Playwright does) and read back; the Check
  screen, L1, Sent, `/define/persona/edit` and `/q/` without a number refused; the palus URL; `edit_idea_lines` on a page
  double (money-only -> `persona`, money + solution and solution-only -> `solution`, the wait's pattern, the step's name;
  Save going nowhere owed still times out; an undrawn decider's box named `absent`).

## FR-2 -- the cost step reads the rate as drawn -- `acb4ca9`

Stop: `runs/20261030T142020Z-backtest-08-fresco` (COMMERCIAL), seq 46 -- the box read before typing `rate: "80"` with
Keel's note; the view read after the screen's Save `hourlyRate {amount: 55, defaulted: false}`; `float("80") == 55`
failed. The screen already read the box before typing (master `vectors_screens.py:1684`) and typed the entry's rate at
`:1708`; nothing in the screen moved.

- [x] T004 `evals/corpus_scenario.py` `leg_calibrate` (`:1673`): passes `drawn_rate=view.get("hourlyRate")` -- `view` is
  the leg's own `_wait_calibration(j, vector)` read **before the screen walk**, so no new GET was needed -- to
  `_hold_the_chain_screen` (`:2017`, new keyword), which hands it to `_hold_the_cost_fill` (`:2032`).
- [x] T005 `cost_fill_rate_owed` (`:2074`): the box owes the before-view's amount and `HOURLY_RATE_DEFAULTED` iff
  `defaulted` (None where the view priced no hours). `cost_fill_rate_faults` (`:2084`): amount, note iff defaulted, and
  the two order checks (unchanged in substance; moved from master `:2103-2109`).
- [x] T006 `saved_rate_faults` (`:2114`): after the save the view's `hourlyRate.amount` is the entry's rate with
  `defaulted: false`. `_hold_the_cost_fill` (`:2133`) runs it as a **second, separate step** (`:2174`, *the cost step's
  save: the view's hourly rate is the entry's own, no longer Keel's default*, party stack) where the mode is HOURS, the
  entry states a rate and the box was drawn (the conditions under which the screen typed it).
- [x] T007 `tests/test_backtest_scope_082.py::test_the_step_and_the_docstring_say_when_the_box_is_read` re-pinned: the
  step's words and the `base_help` pin stay in `_hold_the_cost_fill`; the note and order pins now read
  `cost_fill_rate_owed` / `cost_fill_rate_faults` (the note's pin is *iff defaulted*).
- [x] T008 Tests: 08-fresco's box against the before-view (80, defaulted) holds; against the after-view (55, not
  defaulted) faults on the amount and on the note; note iff defaulted both ways; not drawn / another amount / `80.0`;
  the order checks; no rate owed; `saved_rate_faults` (met, a kept default, `defaulted` missing or true, no entry rate);
  `_hold_the_cost_fill` on a journey double -- both steps met on fresco's numbers, the old stop reproduced, a save that
  kept Keel's default faulting the second step, no second step without an entry rate; the leg passes the before-walk
  read.

## FR-3 -- the decision-maker's line is named -- `2820f60`

Stop: `runs/20261030T143848Z-backtest-10-palus` (SOLUTION), seq 63 -- the first refusal edited `how` and `howDecider`
(both lost *mortgage bonds*), then the cloud (`fcec4533`) refused *the how line* on *mortgage bonds* again.

- [x] T009 `evals/corpus_scenario.py:2348-2349`: `_LOCK_LINE` reads `(decision-maker's how|how|belief)` and
  `_LOCK_LINE_NAMES` maps the first to `howDecider`; `lock_refusal` (`:2353`, `:2365`) returns it; docstring follows.
- [x] T010 `LOCK_EDITS` (`:2371`): `{"how": ("how",), "howDecider": ("howDecider",), "belief": ("belief",)}`.
  `edit_idea_lines` already types `#idea-howDecider` where drawn (`IDEA_BOXES`); a refusal naming a line the card does
  not draw stops as today, now with *howDecider* named in the message.
- [x] T011 `tests/test_after_131.py`: `test_a_stubbed_422_then_a_second_pass_200` re-pinned (*how* edits `how` alone);
  `test_the_deciders_line_is_its_own_refusal_096` (how refused and edited, then the decider's line refused, read as
  `howDecider` and edited alone, then 200). `tests/test_three_stops_096.py`: the three wordings, the decider's name read
  whole, `LOCK_EDITS` one line each and every key a box `IDEA_BOXES` knows, the undrawn line's stop named.

## FR-4 -- nothing else moves

`plain_line`, the M5 word list mirror, `answer_refused_lock`'s loop, `relock`, the other journeys' lock paths, the
quality readers, the marks (`MARKS_VERSION` 23, `INTERVIEWER_MARKS_VERSION` 16), the corpus, the scenario set.

## What the spec got wrong (or left loose)

1. **FR-2's "the leg reads `GET calibration/COMMERCIAL` once before the screen walk"** -- it already did:
   `leg_calibrate`'s first line (`view = _wait_calibration(j, vector)`) is that read, and no screen before the cost
   step sends a rate (08-fresco's box drew Keel's 80 with its note). It is passed through; no second GET was added.
2. **FR-2's line numbers**: the typing is master `vectors_screens.py:1706-1708` (the spec's `:1706-1709` ends one line
   late); immaterial.
3. **FR-3's 10-palus SOLUTION stop is not cured by the harness alone.** In that bundle both lines were already edited
   (the `before` / `after` of the first finding: neither says *mortgage bonds* after), yet the cloud refused *the how
   line* again. The reading that fits: on a solution-only study the Check screen draws no decider's box, so the typed
   `howDecider` was skipped as `absent`, while cloud `fcec4533` still read the stored decider line and named it *how*.
   (Inferred: the edit step's `absent` was not recorded because the step failed before its record.) That stop goes with
   keel-cloud 165 FR-1 (the line read only where money is in scope); 096's part is the naming and the one-line edits, as
   FR-3 says. On a cloud before 165 the same walk would still stop there.
4. **The spec's acceptance counts (3,970 / 0 / 53) are master's own at `dafb23d` too** -- 097-099 added only spec files.

## Judgement calls

1. **The second FR-2 assertion is its own step, party stack**, so a fault in the save never hides the screen's reading
   and the bundle names which moment failed.
2. **`defaulted` must be exactly `false` after the save** (`is not False` faults a missing key too), the spec's words.
3. **The second assertion is owed only where the screen typed the rate** (HOURS, an entry rate, the box drawn) -- the
   conditions in `Corridor._chain_cost` -- so a B2C or a money cost owes none.
4. **FR-1's `landed` is read back off `page.url` after the wait**, not threaded through the scope: the screen says where
   it went; the caller (`_answer_the_refused_lock`) keeps the dict in its record unchanged.
